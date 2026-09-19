from datetime import datetime, timezone
from io import BytesIO
import re
import unicodedata

import certifi
import pandas as pd
import requests
from google.cloud import bigquery


PROJECT_ID = "tx-market-analysis"
DATASET_ID = "market_data"

MARKETS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.markets"
HOME_VALUES_TABLE = f"{PROJECT_ID}.{DATASET_ID}.home_values"
STAGE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.home_values_zillow_stage"

ZILLOW_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)

# Keeps enough history for five-year growth calculations and historical charts.
MIN_OBSERVATION_DATE = pd.Timestamp("2000-01-01")

# Smaller batches avoid creating one extremely large DataFrame in memory.
DATE_COLUMNS_PER_BATCH = 24


STATE_ABBREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District Of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def normalize_city(value):
    """Create a conservative city-name key for matching sources."""

    if pd.isna(value):
        return ""

    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()

    # Remove legal place labels only when they appear at the end.
    text = re.sub(
        r"\s+(city and borough|city|town|village|borough|municipality)$",
        "",
        text,
    )

    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


STATE_NAME_TO_CODE = {
    name.casefold(): code
    for name, code in STATE_ABBREVIATIONS.items()
}

VALID_STATE_CODES = set(STATE_ABBREVIATIONS.values())


def normalize_state(value):
    """Convert either a full state name or abbreviation to a postal code."""

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    upper_text = text.upper()

    if upper_text in VALID_STATE_CODES:
        return upper_text

    return STATE_NAME_TO_CODE.get(text.casefold())


def download_zillow_data():
    print("Downloading Zillow city-level ZHVI history...")

    response = requests.get(
        ZILLOW_URL,
        timeout=180,
        verify=certifi.where(),
    )
    response.raise_for_status()

    data = pd.read_csv(BytesIO(response.content), low_memory=False)

    print(f"Downloaded {len(data):,} Zillow city records.")
    return data


def load_market_directory(client):
    query = f"""
        SELECT
            market_id,
            city,
            state_code
        FROM `{MARKETS_TABLE}`
        WHERE market_id IS NOT NULL
          AND city IS NOT NULL
          AND state_code IS NOT NULL
    """

    markets = client.query(query).to_dataframe()

    markets["_city_key"] = markets["city"].map(normalize_city)
    markets["state_code"] = markets["state_code"].map(normalize_state)
    markets = markets[
        markets["state_code"].notna()
        & markets["_city_key"].ne("")
    ].copy()

    print("\nCensus matching fields")
    print("----------------------")
    print(
        markets[
            ["market_id", "city", "state_code", "_city_key"]
        ].head(10).to_string(index=False)
    )

    markets["_join_key"] = (
        markets["state_code"] + "|" + markets["_city_key"]
    )

    return markets


def prepare_zillow_markets(zillow):
    required_columns = {"RegionName"}

    missing = required_columns - set(zillow.columns)
    if missing:
        raise ValueError(
            "The Zillow file is missing required columns: "
            + ", ".join(sorted(missing))
        )

    data = zillow.copy()

    # Retain city records, but do not discard the entire dataset if Zillow
    # changes the capitalization or formatting of RegionType.
    if "RegionType" in data.columns:
        region_type = (
            data["RegionType"]
            .astype(str)
            .str.strip()
            .str.casefold()
        )

        city_mask = region_type.str.contains(
            r"city|town|village|borough",
            regex=True,
            na=False,
        )

        if city_mask.any():
            data = data[city_mask].copy()

    state_code = pd.Series(
        pd.NA,
        index=data.index,
        dtype="object",
    )

    # Zillow has used both of these column names for state information.
    for column in ["StateName", "State"]:
        if column not in data.columns:
            continue

        candidate = data[column].map(normalize_state)
        state_code = state_code.fillna(candidate)

    data["state_code"] = state_code
    data["_city_key"] = data["RegionName"].map(normalize_city)

    data = data[
        data["state_code"].notna()
        & data["_city_key"].ne("")
    ].copy()

    data["_join_key"] = (
        data["state_code"].astype(str)
        + "|"
        + data["_city_key"]
    )

    print("\nZillow matching fields")
    print("----------------------")
    print(
        data[
            ["RegionName", "state_code", "_city_key", "_join_key"]
        ].head(10).to_string(index=False)
    )

    return data


def retain_unambiguous_matches(markets, zillow):
    """
    Match only city/state combinations that occur once in both sources.

    This deliberately avoids guessing when city names are ambiguous.
    """

    market_counts = markets["_join_key"].value_counts()
    zillow_counts = zillow["_join_key"].value_counts()

    unique_market_keys = set(
        market_counts[market_counts == 1].index
    )
    unique_zillow_keys = set(
        zillow_counts[zillow_counts == 1].index
    )

    valid_keys = unique_market_keys & unique_zillow_keys

    market_matches = markets[
        markets["_join_key"].isin(valid_keys)
    ][["market_id", "_join_key"]]

    zillow_matches = zillow[
        zillow["_join_key"].isin(valid_keys)
    ].copy()

    matched = zillow_matches.merge(
        market_matches,
        on="_join_key",
        how="inner",
        validate="one_to_one",
    )

    return matched


def get_date_columns(data):
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    columns = [
        column
        for column in data.columns
        if date_pattern.match(str(column))
    ]

    columns = [
        column
        for column in columns
        if pd.Timestamp(column) >= MIN_OBSERVATION_DATE
    ]

    return sorted(columns)


def upload_batches(client, matched, date_columns, downloaded_at):
    client.delete_table(STAGE_TABLE, not_found_ok=True)

    schema = [
        bigquery.SchemaField("market_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("observation_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("home_value", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_updated_at", "TIMESTAMP"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    first_write = True
    total_rows = 0

    for start in range(0, len(date_columns), DATE_COLUMNS_PER_BATCH):
        batch_columns = date_columns[
            start:start + DATE_COLUMNS_PER_BATCH
        ]

        batch = matched[
            ["market_id"] + batch_columns
        ].melt(
            id_vars=["market_id"],
            value_vars=batch_columns,
            var_name="observation_date",
            value_name="home_value",
        )

        batch["observation_date"] = pd.to_datetime(
            batch["observation_date"],
            errors="coerce",
        ).dt.date

        batch["home_value"] = pd.to_numeric(
            batch["home_value"],
            errors="coerce",
        )

        batch = batch.dropna(
            subset=["market_id", "observation_date", "home_value"]
        )

        if batch.empty:
            continue

        batch["source"] = "Zillow ZHVI"
        batch["source_updated_at"] = downloaded_at
        batch["loaded_at"] = downloaded_at

        write_disposition = (
            bigquery.WriteDisposition.WRITE_TRUNCATE
            if first_write
            else bigquery.WriteDisposition.WRITE_APPEND
        )

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=write_disposition,
        )

        client.load_table_from_dataframe(
            batch,
            STAGE_TABLE,
            job_config=job_config,
        ).result()

        first_write = False
        total_rows += len(batch)

        print(
            f"Uploaded {total_rows:,} staged home-value observations..."
        )

    if first_write:
        raise RuntimeError(
            "No valid Zillow observations were available to upload."
        )

    return total_rows


def validate_stage(client):
    summary_query = f"""
        SELECT
            COUNT(*) AS row_count,
            COUNT(DISTINCT market_id) AS market_count,
            MIN(observation_date) AS first_date,
            MAX(observation_date) AS last_date
        FROM `{STAGE_TABLE}`
    """

    summary = client.query(summary_query).to_dataframe().iloc[0]

    duplicate_query = f"""
        SELECT COUNT(*) AS duplicate_groups
        FROM (
            SELECT
                market_id,
                observation_date,
                COUNT(*) AS row_count
            FROM `{STAGE_TABLE}`
            GROUP BY market_id, observation_date
            HAVING COUNT(*) > 1
        )
    """

    duplicate_groups = int(
        client.query(duplicate_query).to_dataframe().iloc[0][
            "duplicate_groups"
        ]
    )

    if duplicate_groups:
        raise ValueError(
            f"Staging contains {duplicate_groups:,} duplicate "
            "market/date combinations."
        )

    print("\nStaging validation")
    print("------------------")
    print(f"Rows: {int(summary['row_count']):,}")
    print(f"Markets: {int(summary['market_count']):,}")
    print(f"First observation: {summary['first_date']}")
    print(f"Latest observation: {summary['last_date']}")
    print("Duplicate market/date groups: 0")


def publish_stage(client):
    publish_query = f"""
        BEGIN TRANSACTION;

        DELETE FROM `{HOME_VALUES_TABLE}`
        WHERE observation_date
            BETWEEN DATE '1900-01-01' AND DATE '2100-12-31';

        INSERT INTO `{HOME_VALUES_TABLE}` (
            market_id,
            observation_date,
            home_value,
            source,
            source_updated_at,
            loaded_at
        )
        SELECT
            market_id,
            observation_date,
            home_value,
            source,
            source_updated_at,
            loaded_at
        FROM `{STAGE_TABLE}`;

        COMMIT TRANSACTION;
    """

    client.query(publish_query).result()
    print("\nPublished Zillow history to the home_values table.")


def print_coverage(client):
    query = f"""
        SELECT
            m.state_code,
            COUNT(DISTINCT h.market_id) AS matched_markets,
            COUNT(*) AS observations,
            MIN(h.observation_date) AS first_date,
            MAX(h.observation_date) AS last_date
        FROM `{HOME_VALUES_TABLE}` AS h
        JOIN `{MARKETS_TABLE}` AS m
          USING (market_id)
        WHERE h.observation_date
            BETWEEN DATE '1900-01-01' AND DATE '2100-12-31'
        GROUP BY m.state_code
        ORDER BY matched_markets DESC, m.state_code
    """

    coverage = client.query(query).to_dataframe()

    print("\nCoverage by state")
    print("-----------------")
    print(coverage.to_string(index=False))


def main():
    client = bigquery.Client(project=PROJECT_ID)
    downloaded_at = datetime.now(timezone.utc)

    markets = load_market_directory(client)
    zillow = download_zillow_data()
    zillow = prepare_zillow_markets(zillow)

    matched = retain_unambiguous_matches(markets, zillow)

    census_keys = set(markets["_join_key"].dropna())
    zillow_keys = set(zillow["_join_key"].dropna())
    common_keys = census_keys & zillow_keys

    print("\nMatching summary")
    print("----------------")
    print(f"Census market keys: {len(census_keys):,}")
    print(f"Zillow market keys: {len(zillow_keys):,}")
    print(f"Common city/state keys: {len(common_keys):,}")
    print(f"Unambiguous matches retained: {len(matched):,}")

    if common_keys:
        print("\nExample common keys:")
        for key in sorted(common_keys)[:10]:
            print(f"  {key}")

    date_columns = get_date_columns(matched)

    if matched.empty:
        raise RuntimeError(
            "No Zillow cities matched the Census market directory."
        )

    if not date_columns:
        raise RuntimeError(
            "No Zillow monthly date columns were recognized."
        )

    print(f"Census markets available: {len(markets):,}")
    print(f"Unambiguous Zillow matches: {len(matched):,}")
    print(
        f"Monthly columns: {date_columns[0]} through "
        f"{date_columns[-1]}"
    )

    upload_batches(
        client,
        matched,
        date_columns,
        downloaded_at,
    )

    validate_stage(client)
    publish_stage(client)
    print_coverage(client)

    client.delete_table(STAGE_TABLE, not_found_ok=True)
    print("\nTemporary staging table removed.")
    print("Zillow home-value load completed successfully.")


if __name__ == "__main__":
    main()