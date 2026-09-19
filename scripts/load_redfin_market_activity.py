from datetime import datetime, timezone
import re
import unicodedata
from pathlib import Path

import pandas as pd
from google.cloud import bigquery


PROJECT_ID = "tx-market-analysis"
DATASET_ID = "market_data"

MARKETS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.markets"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.market_activity"
STAGE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.market_activity_redfin_stage"

CSV_PATH = Path("data/raw/redfin_monthly_city.csv")
CSV_GZ_PATH = Path("data/raw/redfin_monthly_city.csv.gz")

SOURCE_NAME = "Redfin Housing Market Tracker"
BATCH_SIZE = 250_000


REQUIRED_COLUMNS = {
    "LAST UPDATED",
    "FREQUENCY",
    "PERIOD END",
    "REGION ID",
    "REGION TYPE",
    "REGION NAME",
    "HOMES SOLD",
    "INVENTORY",
    "MONTHS OF SUPPLY",
    "AVERAGE SALE TO LIST RATIO (%)",
}


def normalize_city(value):
    if pd.isna(value):
        return ""

    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.casefold().strip()

    text = re.sub(
        r"\s+(city and borough|city|town|village|borough|municipality)$",
        "",
        text,
    )

    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_source_file():
    if CSV_PATH.exists():
        return CSV_PATH

    if CSV_GZ_PATH.exists():
        return CSV_GZ_PATH

    raise FileNotFoundError(
        "The Redfin file was not found. Expected either:\n"
        f"  {CSV_PATH}\n"
        f"  {CSV_GZ_PATH}"
    )


def load_redfin_file():
    path = find_source_file()
    print(f"Reading Redfin data from {path}...")

    data = pd.read_csv(path, low_memory=False)
    data.columns = data.columns.astype(str).str.strip().str.upper()

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(
            "The Redfin file is missing required columns:\n"
            + "\n".join(f"  - {name}" for name in sorted(missing))
        )

    print(f"Downloaded file contains {len(data):,} rows.")
    return data


def load_markets(client):
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

    markets["state_code"] = (
        markets["state_code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    markets["_city_key"] = markets["city"].map(normalize_city)
    markets["_join_key"] = (
        markets["state_code"] + "|" + markets["_city_key"]
    )

    # Do not guess when Census has multiple places with the same city/state.
    key_counts = markets["_join_key"].value_counts()
    unique_keys = key_counts[key_counts == 1].index

    return markets[
        markets["_join_key"].isin(unique_keys)
    ].copy()


def prepare_redfin(data):
    redfin = data.copy()

    redfin = redfin[
        redfin["REGION TYPE"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("city")
    ].copy()

    redfin = redfin[
        redfin["FREQUENCY"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("rolling 3 months")
    ].copy()

    region_parts = redfin["REGION NAME"].astype(str).str.rsplit(
        ",",
        n=1,
        expand=True,
    )

    if region_parts.shape[1] != 2:
        raise ValueError(
            "Could not split REGION NAME into city and state."
        )

    redfin["_city"] = region_parts[0].str.strip()
    redfin["state_code"] = (
        region_parts[1]
        .str.strip()
        .str.upper()
    )

    redfin["_city_key"] = redfin["_city"].map(normalize_city)
    redfin["_join_key"] = (
        redfin["state_code"] + "|" + redfin["_city_key"]
    )

    redfin["observation_date"] = pd.to_datetime(
        redfin["PERIOD END"],
        errors="coerce",
    ).dt.date

    redfin["source_updated_at"] = pd.to_datetime(
        redfin["LAST UPDATED"],
        errors="coerce",
        utc=True,
    )

    metric_mapping = {
        "HOMES SOLD": "homes_sold",
        "INVENTORY": "inventory",
        "MONTHS OF SUPPLY": "months_of_supply",
        "AVERAGE SALE TO LIST RATIO (%)": "sale_to_list_pct",
    }

    for source_column, target_column in metric_mapping.items():
        redfin[target_column] = pd.to_numeric(
            redfin[source_column],
            errors="coerce",
        )

    redfin["REGION ID"] = redfin["REGION ID"].astype(str).str.strip()

    redfin = redfin[
        redfin["observation_date"].notna()
        & redfin["state_code"].str.fullmatch(r"[A-Z]{2}", na=False)
        & redfin["_city_key"].ne("")
    ].copy()

    # A city/state key is reliable only when Redfin associates it with one
    # Region ID. Repeated months for the same Region ID are expected.
    region_counts = (
        redfin.groupby("_join_key")["REGION ID"]
        .nunique()
    )

    unique_redfin_keys = region_counts[region_counts == 1].index

    ambiguous_count = int((region_counts > 1).sum())

    print(
        f"Excluded {ambiguous_count:,} ambiguous Redfin "
        "city/state names."
    )

    redfin = redfin[
        redfin["_join_key"].isin(unique_redfin_keys)
    ].copy()

    return redfin


def match_markets(markets, redfin):
    matched = redfin.merge(
        markets[["market_id", "_join_key"]],
        on="_join_key",
        how="inner",
        validate="many_to_one",
    )

    metrics = [
        "homes_sold",
        "inventory",
        "months_of_supply",
        "sale_to_list_pct",
    ]

    matched["_metric_count"] = matched[metrics].notna().sum(axis=1)

    # If Redfin includes a repeated city-period row, retain the row with the
    # most populated required metrics.
    matched = matched.sort_values(
        ["market_id", "observation_date", "_metric_count"],
        ascending=[True, True, False],
    )

    matched = matched.drop_duplicates(
        subset=["market_id", "observation_date"],
        keep="first",
    )

    matched = matched[
        matched[metrics].notna().any(axis=1)
    ].copy()

    loaded_at = datetime.now(timezone.utc)

    matched["source"] = SOURCE_NAME
    matched["loaded_at"] = loaded_at
    matched["source_updated_at"] = (
        matched["source_updated_at"].fillna(loaded_at)
    )

    output_columns = [
        "market_id",
        "observation_date",
        "homes_sold",
        "inventory",
        "months_of_supply",
        "sale_to_list_pct",
        "source",
        "source_updated_at",
        "loaded_at",
    ]

    return matched[output_columns]


def upload_stage(client, data):
    client.delete_table(STAGE_TABLE, not_found_ok=True)

    schema = [
        bigquery.SchemaField("market_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("observation_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("homes_sold", "FLOAT64"),
        bigquery.SchemaField("inventory", "FLOAT64"),
        bigquery.SchemaField("months_of_supply", "FLOAT64"),
        bigquery.SchemaField("sale_to_list_pct", "FLOAT64"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_updated_at", "TIMESTAMP"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    first_batch = True
    uploaded = 0

    for start in range(0, len(data), BATCH_SIZE):
        batch = data.iloc[start:start + BATCH_SIZE].copy()

        config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=(
                bigquery.WriteDisposition.WRITE_TRUNCATE
                if first_batch
                else bigquery.WriteDisposition.WRITE_APPEND
            ),
        )

        client.load_table_from_dataframe(
            batch,
            STAGE_TABLE,
            job_config=config,
        ).result()

        first_batch = False
        uploaded += len(batch)

        print(f"Uploaded {uploaded:,} staged Redfin rows...")

    if first_batch:
        raise RuntimeError(
            "No Redfin records matched the Census market directory."
        )


def validate_stage(client):
    query = f"""
        SELECT
            COUNT(*) AS row_count,
            COUNT(DISTINCT market_id) AS market_count,
            MIN(observation_date) AS first_date,
            MAX(observation_date) AS latest_date,
            COUNTIF(homes_sold IS NULL) AS missing_homes_sold,
            COUNTIF(inventory IS NULL) AS missing_inventory,
            COUNTIF(months_of_supply IS NULL)
                AS missing_months_of_supply,
            COUNTIF(sale_to_list_pct IS NULL)
                AS missing_sale_to_list
        FROM `{STAGE_TABLE}`
    """

    summary = client.query(query).to_dataframe().iloc[0]

    duplicate_query = f"""
        SELECT COUNT(*) AS duplicate_groups
        FROM (
            SELECT
                market_id,
                observation_date,
                COUNT(*) AS records
            FROM `{STAGE_TABLE}`
            GROUP BY market_id, observation_date
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
            f"Redfin staging contains {duplicates:,} duplicate "
            "market-period groups."
        )

    print("\nStaging validation")
    print("------------------")
    print(summary.to_string())
    print("Duplicate market-period groups: 0")


def publish_stage(client):
    query = f"""
        BEGIN TRANSACTION;

        DELETE FROM `{TARGET_TABLE}`
        WHERE observation_date
            BETWEEN DATE '1900-01-01' AND DATE '2100-12-31';

        INSERT INTO `{TARGET_TABLE}` (
            market_id,
            observation_date,
            homes_sold,
            inventory,
            months_of_supply,
            sale_to_list_pct,
            source,
            source_updated_at,
            loaded_at
        )
        SELECT
            market_id,
            observation_date,
            homes_sold,
            inventory,
            months_of_supply,
            sale_to_list_pct,
            source,
            source_updated_at,
            loaded_at
        FROM `{STAGE_TABLE}`;

        COMMIT TRANSACTION;
    """

    client.query(query).result()
    print("\nPublished Redfin data to market_activity.")


def print_coverage(client):
    query = f"""
        SELECT
            m.state_code,
            COUNT(DISTINCT a.market_id) AS matched_markets,
            COUNT(*) AS observations,
            MIN(a.observation_date) AS first_date,
            MAX(a.observation_date) AS latest_date
        FROM `{TARGET_TABLE}` AS a
        JOIN `{MARKETS_TABLE}` AS m
          USING (market_id)
        WHERE a.observation_date
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

    raw_redfin = load_redfin_file()
    markets = load_markets(client)
    redfin = prepare_redfin(raw_redfin)
    matched = match_markets(markets, redfin)

    print("\nMatching summary")
    print("----------------")
    print(f"Unambiguous Census markets: {len(markets):,}")
    print(
        "Distinct Redfin city/state keys: "
        f"{redfin['_join_key'].nunique():,}"
    )
    print(
        "Matched Census markets: "
        f"{matched['market_id'].nunique():,}"
    )
    print(f"Prepared observations: {len(matched):,}")

    if matched.empty:
        raise RuntimeError(
            "No Redfin records matched the Census market directory."
        )

    upload_stage(client, matched)
    validate_stage(client)
    publish_stage(client)
    print_coverage(client)

    client.delete_table(STAGE_TABLE, not_found_ok=True)
    print("\nTemporary staging table removed.")
    print("Redfin market-activity load completed successfully.")


if __name__ == "__main__":
    main()