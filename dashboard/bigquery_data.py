from datetime import date

import streamlit as st
from google.cloud import bigquery

PROJECT_ID = "tx-market-analysis"
DATASET_ID = "market_data"

MIN_ANALYSIS_MARKETS = 3
MAX_ANALYSIS_MARKETS = 50

@st.cache_resource
def get_bigquery_client():
    return bigquery.Client(project=PROJECT_ID)

@st.cache_data(ttl=3600, show_spinner=False)
def load_markets():
    client = get_bigquery_client()

    query = f"""
        SELECT
            market_id,
            city,
            state_name,
            state_code
        FROM `{PROJECT_ID}.{DATASET_ID}.markets`
        ORDER BY state_code, city
    """

    return client.query(query).to_dataframe()

def _validate_market_ids(market_ids):
    market_ids = list(dict.fromkeys(market_ids))

    if not market_ids:
        raise ValueError("Select at least one market.")

    if len(market_ids) > MAX_ANALYSIS_MARKETS:
        raise ValueError(
            f"You may analyze a maximum of "
            f"{MAX_ANALYSIS_MARKETS} markets at once."
        )

    return market_ids

@st.cache_data(ttl=3600, show_spinner=False)
def load_home_values(
    market_ids,
    start_date=date(2000, 1, 1),
    end_date=None,
):
    market_ids = _validate_market_ids(market_ids)
    end_date = end_date or date.today()

    query = f"""
        SELECT
            h.market_id,
            m.city,
            m.state_code,
            CONCAT(m.city, ', ', m.state_code) AS market,
            h.observation_date,
            h.home_value
        FROM `{PROJECT_ID}.{DATASET_ID}.home_values` AS h
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.markets` AS m
            USING (market_id)
        WHERE h.observation_date BETWEEN @start_date AND @end_date
          AND h.market_id IN UNNEST(@market_ids)
        ORDER BY h.observation_date, market
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "market_ids",
                "STRING",
                market_ids,
            ),
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date,
            ),
            bigquery.ScalarQueryParameter(
                "end_date",
                "DATE",
                end_date,
            ),
        ]
    )

    client = get_bigquery_client()

    return client.query(
        query,
        job_config=job_config,
    ).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_population(
    market_ids,
    start_year=2000,
    end_year=None,
):
    market_ids = _validate_market_ids(market_ids)
    end_year = end_year or date.today().year

    query = f"""
        SELECT
            p.market_id,
            m.city,
            m.state_code,
            CONCAT(m.city, ', ', m.state_code) AS market,
            p.year,
            p.population,
            p.vintage
        FROM `{PROJECT_ID}.{DATASET_ID}.population` AS p
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.markets` AS m
            USING (market_id)
        WHERE p.year BETWEEN @start_year AND @end_year
          AND p.market_id IN UNNEST(@market_ids)
        ORDER BY p.year, market
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "market_ids",
                "STRING",
                market_ids,
            ),
            bigquery.ScalarQueryParameter(
                "start_year",
                "INT64",
                start_year,
            ),
            bigquery.ScalarQueryParameter(
                "end_year",
                "INT64",
                end_year,
            ),
        ]
    )

    client = get_bigquery_client()

    return client.query(
        query,
        job_config=job_config,
    ).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_building_permits(
    market_ids,
    start_year=2000,
    end_year=None,
):
    market_ids = _validate_market_ids(market_ids)
    end_year = end_year or date.today().year

    query = f"""
        WITH latest_population AS (
            SELECT
                market_id,
                year,
                population
            FROM `{PROJECT_ID}.{DATASET_ID}.population`
            WHERE year BETWEEN @start_year AND @end_year
              AND market_id IN UNNEST(@market_ids)
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY market_id, year
                ORDER BY source_updated_at DESC, loaded_at DESC
            ) = 1
        )

        SELECT
            b.market_id,
            m.city,
            m.state_code,
            CONCAT(m.city, ', ', m.state_code) AS market,
            b.year,
            b.total_units,
            p.population,
            SAFE_DIVIDE(
                b.total_units * 1000.0,
                p.population
            ) AS units_per_1000_residents
        FROM `{PROJECT_ID}.{DATASET_ID}.building_permits` AS b
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.markets` AS m
            USING (market_id)
        LEFT JOIN latest_population AS p
            ON b.market_id = p.market_id
           AND b.year = p.year
        WHERE b.year BETWEEN @start_year AND @end_year
          AND b.market_id IN UNNEST(@market_ids)
        ORDER BY b.year, market
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "market_ids",
                "STRING",
                market_ids,
            ),
            bigquery.ScalarQueryParameter(
                "start_year",
                "INT64",
                start_year,
            ),
            bigquery.ScalarQueryParameter(
                "end_year",
                "INT64",
                end_year,
            ),
        ]
    )

    client = get_bigquery_client()

    return client.query(
        query,
        job_config=job_config,
    ).to_dataframe(create_bqstorage_client=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_market_activity(
    market_ids,
    start_date=date(2000, 1, 1),
    end_date=None,
):
    market_ids = _validate_market_ids(market_ids)
    end_date = end_date or date.today()

    query = f"""
        SELECT
            a.market_id,
            m.city,
            m.state_code,
            CONCAT(m.city, ', ', m.state_code) AS market,
            a.observation_date,
            a.homes_sold,
            a.inventory,
            a.months_of_supply,
            a.sale_to_list_pct
        FROM `{PROJECT_ID}.{DATASET_ID}.market_activity` AS a
        INNER JOIN `{PROJECT_ID}.{DATASET_ID}.markets` AS m
            USING (market_id)
        WHERE a.observation_date BETWEEN @start_date AND @end_date
          AND a.market_id IN UNNEST(@market_ids)
        ORDER BY a.observation_date, market
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "market_ids",
                "STRING",
                market_ids,
            ),
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date,
            ),
            bigquery.ScalarQueryParameter(
                "end_date",
                "DATE",
                end_date,
            ),
        ]
    )

    client = get_bigquery_client()

    return client.query(
        query,
        job_config=job_config,
    ).to_dataframe(create_bqstorage_client=False)

def load_analysis_sources(market_ids):
    """
    Load and standardize all four BigQuery sources for the existing
    raw-data scoring pipeline.
    """
    market_ids = _validate_market_ids(market_ids)

    home_values = (
        load_home_values(market_ids)
        .rename(
            columns={
                "city": "City",
                "state_code": "State",
                "observation_date": "Date",
                "home_value": "Home_Value",
            }
        )
        [
            [
                "City",
                "State",
                "Date",
                "Home_Value",
            ]
        ]
        .copy()
    )

    market_activity = (
        load_market_activity(market_ids)
        .rename(
            columns={
                "city": "City",
                "state_code": "State",
                "observation_date": "Date",
                "homes_sold": "Homes_Sold",
                "inventory": "Inventory",
                "months_of_supply": "Months_of_Supply",
                "sale_to_list_pct": "Sale_to_List_Pct",
            }
        )
        [
            [
                "City",
                "State",
                "Date",
                "Homes_Sold",
                "Inventory",
                "Months_of_Supply",
                "Sale_to_List_Pct",
            ]
        ]
        .copy()
    )

    population = (
        load_population(market_ids)
        .rename(
            columns={
                "city": "City",
                "state_code": "State",
                "year": "Year",
                "population": "Population",
            }
        )
        [
            [
                "City",
                "State",
                "Year",
                "Population",
            ]
        ]
        .copy()
    )

    permits = (
        load_building_permits(market_ids)
        .rename(
            columns={
                "city": "City",
                "state_code": "State",
                "year": "Year",
                "total_units": "Total_Units",
            }
        )
        [
            [
                "City",
                "State",
                "Year",
                "Total_Units",
            ]
        ]
        .copy()
    )

    return {
        "home_values": home_values,
        "market_activity": market_activity,
        "population": population,
        "permits": permits,
    }

@st.cache_data(ttl=3600, show_spinner=False)
def load_final_decision_table():
    client = get_bigquery_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.final_decision_table`
        ORDER BY national_robust_rank
    """

    return client.query(
        query
    ).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600, show_spinner=False)
def load_texas_decision_table():
    client = get_bigquery_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.final_decision_table`
        WHERE state_code = 'TX'
        ORDER BY state_robust_rank
    """

    return client.query(
        query
    ).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600, show_spinner=False)
def load_ranking_robustness():
    client = get_bigquery_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.market_ranking_robustness`
        ORDER BY avg_rank
    """

    return client.query(
        query
    ).to_dataframe(create_bqstorage_client=False)