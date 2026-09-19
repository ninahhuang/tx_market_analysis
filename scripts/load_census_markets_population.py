from datetime import datetime, timezone

import certifi
import pandas as pd
import requests
from google.cloud import bigquery

from io import BytesIO

PROJECT_ID = "tx-market-analysis"
DATASET_ID = "market_data"

STATE_FIPS_TO_CODE = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
    "72": "PR",
}

CENSUS_URL = (
    "https://www2.census.gov/programs-surveys/"
    "popest/datasets/2020-2025/cities/totals/"
    "sub-est2025.csv"
)

SOURCE_RELEASED_AT = datetime(
    2026,
    5,
    14,
    tzinfo=timezone.utc,
)


def clean_city_name(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(
            (
                r"\s+(city and borough|city|town|village|"
                r"borough|municipality)$"
            ),
            "",
            case=False,
            regex=True,
        )
        .str.strip()
    )


def build_frames():
    print("Downloading Census Vintage 2025 data...")

    response = requests.get(
        CENSUS_URL,
        timeout=120,
        verify=certifi.where(),
    )

    response.raise_for_status()

    print(
        f"Downloaded {len(response.content) / 1_000_000:.1f} MB."
    )

    raw = pd.read_csv(
        BytesIO(response.content),
        dtype={
            "SUMLEV": str,
            "STATE": str,
            "PLACE": str,
        },
        encoding="latin-1",
        low_memory=False,
    )

    raw.columns = (
        raw.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Summary level 162 represents incorporated places.
    places = raw.loc[
        raw["SUMLEV"].astype(str).str.zfill(3).eq("162")
    ].copy()

    # Keep active governmental entities when FUNCSTAT is supplied.
    if "FUNCSTAT" in places.columns:
        places = places.loc[
            places["FUNCSTAT"].astype(str).str.upper().eq("A")
        ].copy()

    places["state_fips"] = (
        places["STATE"].astype(str).str.zfill(2)
    )

    places["place_fips"] = (
        places["PLACE"].astype(str).str.zfill(5)
    )

    places["market_id"] = (
        "US-"
        + places["state_fips"]
        + places["place_fips"]
    )

    places["city"] = clean_city_name(places["NAME"])

    places["state_name"] = (
        places["STNAME"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    places["state_fips"] = (
        places["STATE"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(2)
    )

    places["state_code"] = places["state_fips"].map(
        STATE_FIPS_TO_CODE
    )

    missing_state_codes = places.loc[
        places["state_code"].isna(),
        ["STATE", "STNAME"],
    ].drop_duplicates()

    if not missing_state_codes.empty:
        raise ValueError(
            "State abbreviations are missing for:\n"
            + missing_state_codes.to_string(index=False)
        )

    loaded_at = datetime.now(timezone.utc)

    markets = pd.DataFrame(
        {
            "market_id": places["market_id"],
            "city": places["city"],
            "state_name": places["state_name"],
            "state_code": places["state_code"],
            "state_fips": places["state_fips"],
            "place_fips": places["place_fips"],
            "latitude": None,
            "longitude": None,

            # Markets remain inactive until all four sources match.
            "active": False,

            "source_updated_at": SOURCE_RELEASED_AT,
            "loaded_at": loaded_at,
        }
    )

    markets = (
        markets
        .drop_duplicates(subset=["market_id"])
        .sort_values(["state_code", "city"])
        .reset_index(drop=True)
    )

    population_columns = [
        column
        for column in places.columns
        if column.startswith("POPESTIMATE")
        and column.removeprefix("POPESTIMATE").isdigit()
    ]

    if not population_columns:
        raise ValueError(
            "No POPESTIMATE year columns were found."
        )

    population = places[
        ["market_id"] + population_columns
    ].melt(
        id_vars=["market_id"],
        value_vars=population_columns,
        var_name="estimate_column",
        value_name="population",
    )

    population["year"] = (
        population["estimate_column"]
        .str.extract(r"(\d{4})", expand=False)
        .astype(int)
    )

    population["population"] = pd.to_numeric(
        population["population"],
        errors="coerce",
    )

    population = (
        population
        .dropna(subset=["market_id", "year", "population"])
        .loc[lambda frame: frame["population"] >= 0]
        .copy()
    )

    population["population"] = (
        population["population"].astype("int64")
    )

    population["vintage"] = "2025"
    population["source"] = CENSUS_URL
    population["source_updated_at"] = SOURCE_RELEASED_AT
    population["loaded_at"] = loaded_at

    population = population[
        [
            "market_id",
            "year",
            "population",
            "vintage",
            "source",
            "source_updated_at",
            "loaded_at",
        ]
    ].sort_values(["market_id", "year"])

    return markets, population


def validate_frames(markets, population):
    if markets.empty:
        raise ValueError("No incorporated places were found.")

    if population.empty:
        raise ValueError("No population records were created.")

    if markets["market_id"].duplicated().any():
        raise ValueError("Duplicate market IDs were found.")

    duplicate_population = population.duplicated(
        subset=["market_id", "year"],
        keep=False,
    )

    if duplicate_population.any():
        raise ValueError(
            "Duplicate market-year population rows were found."
        )

    valid_year_counts = (
        population.groupby("market_id")["year"].nunique()
    )

    if valid_year_counts.min() < 3:
        raise ValueError(
            "One or more markets have fewer than three years."
        )

    missing_market_ids = (
        set(population["market_id"])
        - set(markets["market_id"])
    )

    if missing_market_ids:
        raise ValueError(
            "Population contains unknown market IDs."
        )

    print(f"Markets prepared: {len(markets):,}")
    print(f"States represented: {markets['state_code'].nunique():,}")
    print(f"Population rows prepared: {len(population):,}")
    print(
        "Population years: "
        f"{population['year'].min()}–"
        f"{population['year'].max()}"
    )


def load_staging_tables(client, markets, population):
    markets_stage = (
        f"{PROJECT_ID}.{DATASET_ID}.markets_census_stage"
    )

    population_stage = (
        f"{PROJECT_ID}.{DATASET_ID}.population_census_stage"
    )

    load_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print("Loading staging tables...")

    client.load_table_from_dataframe(
        markets,
        markets_stage,
        job_config=load_config,
    ).result()

    client.load_table_from_dataframe(
        population,
        population_stage,
        job_config=load_config,
    ).result()

    return markets_stage, population_stage


def publish_tables(
    client,
    markets_stage,
    population_stage,
):
    print("Publishing validated records...")

    query = f"""
        BEGIN TRANSACTION;

        DELETE FROM `{PROJECT_ID}.{DATASET_ID}.markets`
        WHERE TRUE;

        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.markets`
        (
            market_id,
            city,
            state_name,
            state_code,
            state_fips,
            place_fips,
            latitude,
            longitude,
            active,
            source_updated_at,
            loaded_at
        )
        SELECT
            market_id,
            city,
            state_name,
            state_code,
            state_fips,
            place_fips,
            CAST(latitude AS FLOAT64),
            CAST(longitude AS FLOAT64),
            active,
            source_updated_at,
            loaded_at
        FROM `{markets_stage}`;

        DELETE FROM `{PROJECT_ID}.{DATASET_ID}.population`
        WHERE year BETWEEN 1900 AND 2100;

        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.population`
        (
            market_id,
            year,
            population,
            vintage,
            source,
            source_updated_at,
            loaded_at
        )
        SELECT
            market_id,
            year,
            population,
            vintage,
            source,
            source_updated_at,
            loaded_at
        FROM `{population_stage}`;

        COMMIT TRANSACTION;
    """

    client.query(query).result()

    client.delete_table(
        markets_stage,
        not_found_ok=True,
    )

    client.delete_table(
        population_stage,
        not_found_ok=True,
    )


def main():
    markets, population = build_frames()

    validate_frames(
        markets,
        population,
    )

    client = bigquery.Client(project=PROJECT_ID)

    markets_stage, population_stage = (
        load_staging_tables(
            client,
            markets,
            population,
        )
    )

    publish_tables(
        client,
        markets_stage,
        population_stage,
    )

    print("Census markets and population loaded successfully.")


if __name__ == "__main__":
    main()