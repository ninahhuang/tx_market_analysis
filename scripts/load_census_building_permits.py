from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import io
from io import BytesIO
import re

import certifi
import pandas as pd
import requests
from google.cloud import bigquery

PROJECT_ID = "tx-market-analysis"
DATASET_ID = "market_data"

CENSUS_COLUMNS = [
    "SURVEY",
    "STATE",
    "6_DIGIT",
    "COUNTY",
    "CENSUS_PLACE",
    "FIPS_PLACE",
    "FIPS_MCD",
    "POP",
    "CSA",
    "CBSA",
    "FOOTNOTE",
    "CENTRAL",
    "ZIP",
    "REGION",
    "DIVISION",
    "NUMBER_OF",
    "PLACE",

    "1_UNIT_BLDGS",
    "1_UNIT",
    "1_UNIT_VALUE",

    "2_UNITS_BLDGS",
    "2_UNITS",
    "2_UNITS_VALUE",

    "3_4_UNITS_BLDGS",
    "3_4_UNITS",
    "3_4_UNITS_VALUE",

    "5_UNITS_BLDGS",
    "5_UNITS",
    "5_UNITS_VALUE",

    "1_UNIT_REP_BLDGS",
    "1_UNIT_REP",
    "1_UNIT_REP_VALUE",

    "2_UNITS_REP_BLDGS",
    "2_UNITS_REP",
    "2_UNITS_REP_VALUE",

    "3_4_UNITS_REP_BLDGS",
    "3_4_UNITS_REP",
    "3_4_UNITS_REP_VALUE",

    "5_UNITS_REP_BLDGS",
    "5_UNITS_REP",
    "5_UNITS_REP_VALUE",
]

MARKETS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.markets"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.building_permits"
STAGE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.building_permits_census_stage"

FIRST_YEAR = 2020
LAST_YEAR = 2025

REGIONS = {
    "Northeast Region": "ne",
    "Midwest Region": "mw",
    "South Region": "so",
    "West Region": "we",
}

BASE_URL = "https://www2.census.gov/econ/bps/Place"


def normalize_column(value):
    value = str(value).strip().upper()
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    return value.strip("_")


def select_column(columns, candidates, description):
    for candidate in candidates:
        if candidate in columns:
            return candidate

    raise ValueError(
        f"Could not identify {description}.\n"
        f"Tried: {candidates}\n"
        f"Available columns: {sorted(columns)}"
    )


def normalize_fips(series, width):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
        .replace("", pd.NA)
        .str.zfill(width)
    )


def download_file(region_name, prefix, year):
    filename = f"{prefix}{year}a.txt"
    encoded_region = region_name.replace(" ", "%20")
    url = f"{BASE_URL}/{encoded_region}/{filename}"

    print(f"Downloading {filename}...")

    response = requests.get(
        url,
        timeout=180,
        verify=certifi.where(),
    )
    response.raise_for_status()

    last_modified = response.headers.get("Last-Modified")

    if last_modified:
        source_updated_at = parsedate_to_datetime(last_modified)
    else:
        source_updated_at = datetime.now(timezone.utc)

    data = pd.read_csv(
        io.StringIO(response.text),
        skiprows=2,
        header=None,
        names=CENSUS_COLUMNS,
        dtype=str,
    )

    data.columns = [normalize_column(column) for column in data.columns]

    return data, url, source_updated_at


def transform_file(data, year, url, source_updated_at):
    columns = set(data.columns)

    state_column = select_column(
        columns,
        [
            "STATE_FIPS",
            "STATE_FIPS_CODE",
            "STATE_CODE",
            "STATE",
        ],
        "state FIPS column",
    )

    place_column = select_column(
        columns,
        [
            "PLACE_FIPS",
            "PLACE_FIPS_CODE",
            "PLACE_CODE",
            "FIPS_PLACE",
        ],
        "place FIPS column",
    )

    required_unit_columns = [
        "1_UNIT",
        "2_UNITS",
        "3_4_UNITS",
        "5_UNITS",
    ]

    missing_unit_columns = [
        col for col in required_unit_columns if col not in columns
    ]

    if missing_unit_columns:
        raise ValueError(
            "Could not identify all permitted-unit columns. "
            f"Missing: {missing_unit_columns}. "
            f"Available columns: {sorted(columns)}"
        )

    result = pd.DataFrame()

    result["state_fips"] = normalize_fips(
        data[state_column],
        2,
    )

    result["place_fips"] = normalize_fips(
        data[place_column],
        5,
    )

    result["total_units"] = (
        pd.to_numeric(data["1_UNIT"], errors="coerce").fillna(0)
        + pd.to_numeric(data["2_UNITS"], errors="coerce").fillna(0)
        + pd.to_numeric(data["3_4_UNITS"], errors="coerce").fillna(0)
        + pd.to_numeric(data["5_UNITS"], errors="coerce").fillna(0)
    )

    result["year"] = int(year)
    result["source"] = url
    result["source_updated_at"] = source_updated_at

    print("----------------------")
    print("Raw rows:", len(result))

    print("\nSample transformed rows:")
    print(
        result[
            ["state_fips", "place_fips", "total_units"]
        ].head(10).to_string(index=False)
    )

    print("\nNon-null counts:")
    print(
        result[
            ["state_fips", "place_fips", "total_units"]
        ].notna().sum()
    )

    print("\nSample raw Census identifiers:")
    print(
        data[
            ["STATE", "FIPS_PLACE", "PLACE"]
        ].head(10).to_string(index=False)
    )

    result = result.dropna(
        subset=["state_fips", "place_fips", "total_units"]
    )

    result = result[
        result["state_fips"].str.fullmatch(r"\d{2}", na=False)
        & result["place_fips"].str.fullmatch(r"\d{5}", na=False)
        & result["total_units"].ge(0)
    ].copy()

    result["_geo_key"] = (
        result["state_fips"] + result["place_fips"]
    )

    return result


def download_all_files():
    frames = []

    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for region_name, prefix in REGIONS.items():
            data, url, updated_at = download_file(
                region_name,
                prefix,
                year,
            )

            if not frames:
                print("\nDetected Census columns")
                print("-----------------------")
                print(data.columns.tolist())

            transformed = transform_file(
                data,
                year,
                url,
                updated_at,
            )

            frames.append(transformed)

            print(
                f"Prepared {len(transformed):,} place records "
                f"for {region_name}, {year}."
            )

    permits = pd.concat(frames, ignore_index=True)

    # Multiple permit offices can occasionally map to one incorporated
    # place. Aggregate their authorized housing units.
    permits = (
        permits.groupby(
            ["_geo_key", "year"],
            as_index=False,
        )
        .agg(
            total_units=("total_units", "sum"),
            source=("source", lambda values: "; ".join(sorted(set(values)))),
            source_updated_at=("source_updated_at", "max"),
        )
    )

    return permits


def load_markets(client):
    query = f"""
        SELECT
            market_id,
            state_fips,
            place_fips
        FROM `{MARKETS_TABLE}`
        WHERE market_id IS NOT NULL
          AND state_fips IS NOT NULL
          AND place_fips IS NOT NULL
    """

    markets = client.query(query).to_dataframe()

    markets["state_fips"] = normalize_fips(
        markets["state_fips"],
        2,
    )
    markets["place_fips"] = normalize_fips(
        markets["place_fips"],
        5,
    )

    markets["_geo_key"] = (
        markets["state_fips"] + markets["place_fips"]
    )

    counts = markets["_geo_key"].value_counts()
    unique_keys = counts[counts == 1].index

    return markets[
        markets["_geo_key"].isin(unique_keys)
    ][["market_id", "_geo_key"]].copy()


def match_markets(markets, permits):
    matched = permits.merge(
        markets,
        on="_geo_key",
        how="inner",
        validate="many_to_one",
    )

    matched["total_units"] = (
        pd.to_numeric(matched["total_units"], errors="coerce")
        .round()
        .astype("Int64")
    )

    matched["loaded_at"] = datetime.now(timezone.utc)

    matched = matched.dropna(
        subset=["market_id", "year", "total_units"]
    )

    matched = matched.drop_duplicates(
        subset=["market_id", "year"],
        keep="last",
    )

    return matched[
        [
            "market_id",
            "year",
            "total_units",
            "source",
            "source_updated_at",
            "loaded_at",
        ]
    ].copy()


def upload_stage(client, data):
    client.delete_table(STAGE_TABLE, not_found_ok=True)

    schema = [
        bigquery.SchemaField("market_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("year", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("total_units", "INT64"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_updated_at", "TIMESTAMP"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    client.load_table_from_dataframe(
        data,
        STAGE_TABLE,
        job_config=config,
    ).result()

    print(f"\nUploaded {len(data):,} staged permit records.")


def validate_stage(client):
    query = f"""
        SELECT
            COUNT(*) AS row_count,
            COUNT(DISTINCT market_id) AS market_count,
            MIN(year) AS first_year,
            MAX(year) AS latest_year,
            COUNTIF(total_units IS NULL) AS missing_units,
            COUNTIF(total_units < 0) AS negative_units
        FROM `{STAGE_TABLE}`
    """

    summary = client.query(query).to_dataframe().iloc[0]

    duplicate_query = f"""
        SELECT COUNT(*) AS duplicate_groups
        FROM (
            SELECT
                market_id,
                year,
                COUNT(*) AS records
            FROM `{STAGE_TABLE}`
            GROUP BY market_id, year
            HAVING COUNT(*) > 1
        )
    """

    duplicates = int(
        client.query(duplicate_query)
        .to_dataframe()
        .iloc[0]["duplicate_groups"]
    )

    if duplicates:
        raise ValueError(
            f"Staging contains {duplicates:,} duplicate market-year groups."
        )

    if int(summary["negative_units"]) > 0:
        raise ValueError("Negative building-permit totals were found.")

    print("\nStaging validation")
    print("------------------")
    print(summary.to_string())
    print("Duplicate market-year groups: 0")


def publish_stage(client):
    query = f"""
        BEGIN TRANSACTION;

        DELETE FROM `{TARGET_TABLE}`
        WHERE year BETWEEN {FIRST_YEAR} AND {LAST_YEAR};

        INSERT INTO `{TARGET_TABLE}` (
            market_id,
            year,
            total_units,
            source,
            source_updated_at,
            loaded_at
        )
        SELECT
            market_id,
            year,
            total_units,
            source,
            source_updated_at,
            loaded_at
        FROM `{STAGE_TABLE}`;

        COMMIT TRANSACTION;
    """

    client.query(query).result()
    print("\nPublished Census permits to building_permits.")


def print_coverage(client):
    query = f"""
        SELECT
            m.state_code,
            COUNT(DISTINCT p.market_id) AS matched_markets,
            COUNT(*) AS observations,
            MIN(p.year) AS first_year,
            MAX(p.year) AS latest_year,
            SUM(p.total_units) AS permitted_units
        FROM `{TARGET_TABLE}` AS p
        JOIN `{MARKETS_TABLE}` AS m
          USING (market_id)
        WHERE p.year BETWEEN {FIRST_YEAR} AND {LAST_YEAR}
        GROUP BY m.state_code
        ORDER BY matched_markets DESC, m.state_code
    """

    coverage = client.query(query).to_dataframe()

    print("\nCoverage by state")
    print("-----------------")
    print(coverage.to_string(index=False))


def main():
    client = bigquery.Client(project=PROJECT_ID)

    permits = download_all_files()
    markets = load_markets(client)
    matched = match_markets(markets, permits)

    print("\nMatching summary")
    print("----------------")
    print(f"Permit market-year records: {len(permits):,}")
    print(f"Available Census markets: {len(markets):,}")
    print(
        "Matched permit markets: "
        f"{matched['market_id'].nunique():,}"
    )
    print(f"Matched observations: {len(matched):,}")

    if matched.empty:
        raise RuntimeError(
            "No building-permit records matched the market directory."
        )

    upload_stage(client, matched)
    validate_stage(client)
    publish_stage(client)
    print_coverage(client)

    client.delete_table(STAGE_TABLE, not_found_ok=True)
    print("\nTemporary staging table removed.")
    print("Census building-permit load completed successfully.")


if __name__ == "__main__":
    main()