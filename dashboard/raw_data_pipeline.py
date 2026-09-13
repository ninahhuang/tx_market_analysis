from __future__ import annotations

import csv
import io

import numpy as np
import pandas as pd

HOME_VALUE_COLUMNS = [
    "City",
    "State",
    "Date",
    "Home_Value",
]

MARKET_ACTIVITY_COLUMNS = [
    "City",
    "State",
    "Date",
    "Homes_Sold",
    "Inventory",
    "Months_of_Supply",
    "Sale_to_List_Pct",
]

POPULATION_COLUMNS = [
    "City",
    "State",
    "Year",
    "Population",
]

PERMIT_COLUMNS = [
    "City",
    "State",
    "Year",
    "Total_Units",
]

def read_csv_upload(uploaded_file):
    if uploaded_file is None:
        return None

    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file)

def read_large_redfin_upload(
    uploaded_file,
    selected_markets=None,
):
    required_source_columns = [
        "REGION TYPE",
        "REGION NAME",
        "PERIOD END",
        "HOMES SOLD",
        "INVENTORY",
        "ACTIVE LISTINGS",
        "MONTHS OF SUPPLY",
        "AVERAGE SALE TO LIST RATIO (%)",
    ]

    uploaded_file.seek(0)
    retained_chunks = []

    for chunk in pd.read_csv(
        uploaded_file,
        usecols=lambda column: (
            column.strip().upper()
            in required_source_columns
        ),
        chunksize=100_000,
        low_memory=False,
    ):
        chunk.columns = (
            chunk.columns
            .astype(str)
            .str.strip()
            .str.upper()
        )

        if "REGION TYPE" in chunk.columns:
            chunk = chunk[
                chunk["REGION TYPE"]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("city")
            ]

        if selected_markets:
            chunk = chunk[
                chunk["REGION NAME"].isin(selected_markets)
            ]

        if not chunk.empty:
            retained_chunks.append(chunk)

    if not retained_chunks:
        raise ValueError(
            "No matching city-level Redfin records were found."
        )

    return pd.concat(
        retained_chunks,
        ignore_index=True,
    )

STATE_FIPS_TO_ABBR = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR",
    "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX",
    "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}


def read_bps_permit_upload(uploaded_file):
    """
    Convert an original Census BPS annual place file into:
    City, State, Year, Total_Units
    """
    if uploaded_file is None:
        return None

    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()
    text = raw_bytes.decode("utf-8-sig", errors="replace")

    # Permit files already manually cleaned for the model.
    try:
        cleaned = pd.read_csv(io.StringIO(text))

        if set(PERMIT_COLUMNS).issubset(cleaned.columns):
            return cleaned[PERMIT_COLUMNS].copy()
    except Exception:
        pass

    # Original Census BPS annual place files contain three
    # introductory/header rows. Ignoring quote handling is necessary
    # for the formatting used by these files.
    raw = pd.read_csv(
        io.StringIO(text),
        skiprows=3,
        header=None,
        dtype=str,
        quoting=csv.QUOTE_NONE,
        on_bad_lines="skip",
    )

    if raw.shape[1] < 20:
        raise ValueError(
            f"{uploaded_file.name} does not appear to be an original "
            "Census annual place-level permit file."
        )

    # Some annual BPS downloads have ordinary comma-separated rows,
    # while later downloaded files may contain additional quote fields.
    if raw.shape[1] >= 50:
        city_position = 17
        total_units_position = 19
    else:
        city_position = 16
        total_units_position = 18

    result = pd.DataFrame({
        "Year": (
            raw.iloc[:, 0]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.strip()
        ),
        "State_FIPS": (
            raw.iloc[:, 1]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.strip()
            .str.zfill(2)
        ),
        "City": (
            raw.iloc[:, city_position]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.strip()
        ),
        "Total_Units": raw.iloc[:, total_units_position],
    })

    result = pd.DataFrame({
        "Year": (
            raw.iloc[:, 0]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.strip()
        ),
        "State_FIPS": (
            raw.iloc[:, 1]
            .astype(str)
            .str.strip()
            .str.zfill(2)
        ),
        "City": (
            raw.iloc[:, 17]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.strip()
        ),
        # Column 19 is total permitted housing units.
        "Total_Units": raw.iloc[:, 19],
    })

    result["State"] = result["State_FIPS"].map(
        STATE_FIPS_TO_ABBR
    )

    result = result[
        result["State"].notna()
        & result["City"].notna()
        & result["City"].ne("")
    ].copy()

    return result[
        ["City", "State", "Year", "Total_Units"]
    ]


def clean_number(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce",
    )

STATE_ABBREVIATIONS = {
    "TEXAS": "TX",
    "CALIFORNIA": "CA",
    "FLORIDA": "FL",
    "ARIZONA": "AZ",
    "GEORGIA": "GA",
    "NORTH CAROLINA": "NC",
    "SOUTH CAROLINA": "SC",
    "TENNESSEE": "TN",
    "COLORADO": "CO",
}


def normalize_market_identity(df):
    result = df.copy()

    result["City"] = (
        result["City"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    result["State"] = (
        result["State"]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace(STATE_ABBREVIATIONS)
    )

    result["Market_ID"] = (
        result["City"] + ", " + result["State"]
    )

    return result

def process_home_values(df):
    required = set(HOME_VALUE_COLUMNS)
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Home-value file is missing: "
            + ", ".join(sorted(missing))
        )

    result = df[HOME_VALUE_COLUMNS].copy()
    result = normalize_market_identity(result)

    result["Date"] = pd.to_datetime(
        result["Date"],
        errors="coerce",
    )

    result["Home_Value"] = clean_number(
        result["Home_Value"]
    )

    result = result.dropna(
        subset=[
            "City",
            "State",
            "Date",
            "Home_Value",
            "Market_ID",
        ]
    ).copy()

    # A duplicated city-state-date usually means two distinct places
    # share the same name. Market_ID cannot distinguish them safely.
    ambiguous_markets = result.loc[
        result.duplicated(
            subset=["Market_ID", "Date"],
            keep=False,
        ),
        "Market_ID",
    ].unique()

    result = result[
        ~result["Market_ID"].isin(ambiguous_markets)
    ].copy()

    return (
        result
        .drop_duplicates(
            subset=["Market_ID", "Date"],
            keep="last",
        )
        .sort_values(["Market_ID", "Date"])
        .reset_index(drop=True)
    )

def process_market_activity(df):
    required = set(MARKET_ACTIVITY_COLUMNS)
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Market-activity file is missing: "
            + ", ".join(sorted(missing))
        )

    result = df[MARKET_ACTIVITY_COLUMNS].copy()
    result = normalize_market_identity(result)

    result["Date"] = pd.to_datetime(
        result["Date"],
        errors="coerce",
    )

    numeric_columns = [
        "Homes_Sold",
        "Inventory",
        "Months_of_Supply",
        "Sale_to_List_Pct",
    ]

    for column in numeric_columns:
        result[column] = clean_number(result[column])

    return result.sort_values(["Market_ID", "Date"])

def process_population(df):
    required = set(POPULATION_COLUMNS)
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Population file is missing: "
            + ", ".join(sorted(missing))
        )

    result = df[POPULATION_COLUMNS].copy()
    result = normalize_market_identity(result)

    result["Year"] = pd.to_numeric(
        result["Year"],
        errors="coerce",
    )

    result["Population"] = clean_number(
        result["Population"]
    )

    return result.sort_values(["Market_ID", "Year"])

def process_permits(df):
    required = set(PERMIT_COLUMNS)
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Permit file is missing: "
            + ", ".join(sorted(missing))
        )

    result = df[PERMIT_COLUMNS].copy()
    result = normalize_market_identity(result)

    result["Year"] = pd.to_numeric(
        result["Year"],
        errors="coerce",
    )

    result["Total_Units"] = clean_number(
        result["Total_Units"]
    )

    return result.sort_values(["Market_ID", "Year"])

def process_wide_home_values(df):
    possible_city_columns = [
        "City",
        "RegionName",
    ]

    possible_state_columns = [
        "State",
        "StateName",
    ]

    city_column = next(
        (
            column
            for column in possible_city_columns
            if column in df.columns
        ),
        None,
    )

    state_column = next(
        (
            column
            for column in possible_state_columns
            if column in df.columns
        ),
        None,
    )

    if city_column is None or state_column is None:
        raise ValueError(
            "The Zillow file must contain a city and state field."
        )

    date_columns = []

    for column in df.columns:
        parsed = pd.to_datetime(
            str(column),
            errors="coerce",
        )

        if pd.notna(parsed):
            date_columns.append(column)

    if not date_columns:
        raise ValueError(
            "No monthly date columns were found in the Zillow file."
        )

    result = df.melt(
        id_vars=[city_column, state_column],
        value_vars=date_columns,
        var_name="Date",
        value_name="Home_Value",
    ).rename(
        columns={
            city_column: "City",
            state_column: "State",
        }
    )

    return process_home_values(result)

def validate_table(
    df,
    name,
    required_columns,
    key_columns,
    numeric_columns,
):
    checks = []

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    checks.append({
        "name": f"{name}: required columns",
        "passed": not missing_columns,
        "detail": (
            "All required columns were found."
            if not missing_columns
            else "Missing: " + ", ".join(missing_columns)
        ),
    })

    if missing_columns:
        return checks

    blank_identity = (
        df["City"].isna().any()
        or df["State"].isna().any()
        or df["City"].astype(str).str.strip().eq("").any()
        or df["State"].astype(str).str.strip().eq("").any()
    )

    checks.append({
        "name": f"{name}: market identity",
        "passed": not blank_identity,
        "detail": (
            "Every record has a city and state."
            if not blank_identity
            else "One or more records have a blank city or state."
        ),
    })

    duplicates = df.duplicated(
        subset=key_columns,
        keep=False,
    )

    checks.append({
        "name": f"{name}: unique records",
        "passed": not duplicates.any(),
        "detail": (
            "No duplicate market-period records were found."
            if not duplicates.any()
            else f"{int(duplicates.sum())} duplicate records were found."
        ),
    })

    numeric_valid = all(
        pd.to_numeric(
            df[column],
            errors="coerce",
        ).notna().all()
        for column in numeric_columns
    )

    checks.append({
        "name": f"{name}: numeric values",
        "passed": numeric_valid,
        "detail": (
            "All required measurements are numeric."
            if numeric_valid
            else "One or more measurements are blank or non-numeric."
        ),
    })

    return checks

def validate_sources(
    home_values,
    market_activity,
    population,
    permits,
):
    checks = []

    checks += validate_table(
        home_values,
        "Home values",
        HOME_VALUE_COLUMNS,
        ["Market_ID", "Date"],
        ["Home_Value"],
    )

    checks += validate_table(
        market_activity,
        "Market activity",
        MARKET_ACTIVITY_COLUMNS,
        ["Market_ID", "Date"],
        [
            "Homes_Sold",
            "Inventory",
            "Months_of_Supply",
            "Sale_to_List_Pct",
        ],
    )

    checks += validate_table(
        population,
        "Population",
        POPULATION_COLUMNS,
        ["Market_ID", "Year"],
        ["Population"],
    )

    checks += validate_table(
        permits,
        "Building permits",
        PERMIT_COLUMNS,
        ["Market_ID", "Year"],
        ["Total_Units"],
    )

    return checks

def check_market_coverage(
    home_values,
    market_activity,
    population,
    permits,
):
    def valid_market_ids(df):
        return set(
            df["Market_ID"]
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda values: values.ne("")]
        )


    market_sets = {
        "Home values": valid_market_ids(home_values),
        "Market activity": valid_market_ids(market_activity),
        "Population": valid_market_ids(population),
        "Building permits": valid_market_ids(permits),
    }

    common_markets = set.intersection(
        *market_sets.values()
    )

    all_markets = set.union(
        *market_sets.values()
    )

    excluded_markets = sorted(
        all_markets - common_markets
    )

    check = {
        "name": "Cross-source market coverage",
        "passed": len(common_markets) >= 3,
        "detail": (
            f"{len(common_markets)} markets appear in every source."
        ),
    }

    return check, sorted(common_markets), excluded_markets

def calculate_cagr(
    starting_value,
    ending_value,
    periods,
):
    if (
        pd.isna(starting_value)
        or pd.isna(ending_value)
        or starting_value <= 0
        or periods <= 0
    ):
        return np.nan

    return (
        (ending_value / starting_value)
        ** (1 / periods)
        - 1
    ) * 100

def build_home_value_features(home_values):
    rows = []

    for market_id, group in home_values.groupby("Market_ID"):
        group = group.dropna(
            subset=["Date", "Home_Value"]
        ).sort_values("Date")

        latest = group.iloc[-1]
        latest_date = latest["Date"]

        five_year_cutoff = (
            latest_date - pd.DateOffset(years=5)
        )

        historical = group.loc[
            group["Date"] <= five_year_cutoff
        ]

        prior_year = group.loc[
            group["Date"]
            <= latest_date - pd.DateOffset(years=1)
        ]

        if historical.empty or prior_year.empty:
            continue

        five_year_row = historical.iloc[-1]
        prior_year_row = prior_year.iloc[-1]

        rows.append({
            "Market_ID": market_id,
            "City": latest["City"],
            "State": latest["State"],
            "Latest_ZHVI": latest["Home_Value"],
            "Five_Yr_CAGR_Pct": calculate_cagr(
                five_year_row["Home_Value"],
                latest["Home_Value"],
                5,
            ),
            "ZHVI_YoY_Pct": (
                latest["Home_Value"]
                / prior_year_row["Home_Value"]
                - 1
            ) * 100,
        })

    return pd.DataFrame(rows)

def build_population_features(population):
    rows = []

    for market_id, group in population.groupby("Market_ID"):
        group = group.dropna(
            subset=["Year", "Population"]
        ).sort_values("Year")

        if len(group) < 3:
            continue

        latest = group.iloc[-1]
        starting = group.iloc[0]
        previous = group.iloc[-2]

        years = latest["Year"] - starting["Year"]

        previous_growth = (
            previous["Population"]
            / group.iloc[-3]["Population"]
            - 1
        ) * 100

        latest_growth = (
            latest["Population"]
            / previous["Population"]
            - 1
        ) * 100

        rows.append({
            "Market_ID": market_id,
            "Latest_Population": latest["Population"],
            "Population_CAGR_Pct": calculate_cagr(
                starting["Population"],
                latest["Population"],
                years,
            ),
            "Population_Growth_Acceleration": (
                latest_growth - previous_growth
            ),
        })

    return pd.DataFrame(rows)

def build_activity_features(market_activity):
    rows = []

    for market_id, group in market_activity.groupby("Market_ID"):
        group = group.dropna(
            subset=["Date"]
        ).sort_values("Date")

        if group.empty:
            continue

        latest = group.iloc[-1]
        prior_year_rows = group.loc[
            group["Date"]
            <= latest["Date"] - pd.DateOffset(years=1)
        ]

        if prior_year_rows.empty:
            continue

        prior = prior_year_rows.iloc[-1]

        rows.append({
            "Market_ID": market_id,
            "Homes_Sold_YoY_Pct": (
                latest["Homes_Sold"]
                / prior["Homes_Sold"]
                - 1
            ) * 100,
            "Inventory_YoY_Pct": (
                latest["Inventory"]
                / prior["Inventory"]
                - 1
            ) * 100,
            "Months_of_Supply": latest["Months_of_Supply"],
            "Sale_to_List_Pct": latest["Sale_to_List_Pct"],
        })

    return pd.DataFrame(rows)

def build_permit_features(permits, population_features):
    latest_permits = (
        permits
        .sort_values("Year")
        .groupby("Market_ID", as_index=False)
        .tail(1)
    )

    result = latest_permits.merge(
        population_features[
            ["Market_ID", "Latest_Population"]
        ],
        on="Market_ID",
        how="inner",
        validate="one_to_one",
    )

    result["Latest_Permits_Per_1000"] = (
        result["Total_Units"]
        / result["Latest_Population"]
        * 1000
    )

    average_permits = (
        permits.groupby(
            "Market_ID",
            as_index=False,
        )["Total_Units"]
        .mean()
        .rename(
            columns={
                "Total_Units": "Average_Total_Units"
            }
        )
    )

    result = result.merge(
        average_permits,
        on="Market_ID",
        how="left",
        validate="one_to_one",
    )

    result["Avg_Permits_Per_1000"] = (
        result["Average_Total_Units"]
        / result["Latest_Population"]
        * 1000
    )

    return result[
        [
            "Market_ID",
            "Latest_Permits_Per_1000",
            "Avg_Permits_Per_1000",
        ]
    ]

def build_market_feature_table(
    home_values,
    market_activity,
    population,
    permits,
):
    home_features = build_home_value_features(
        home_values
    )

    population_features = build_population_features(
        population
    )

    activity_features = build_activity_features(
        market_activity
    )

    permit_features = build_permit_features(
        permits,
        population_features,
    )

    features = (
        home_features
        .merge(
            population_features,
            on="Market_ID",
            how="inner",
            validate="one_to_one",
        )
        .merge(
            activity_features,
            on="Market_ID",
            how="inner",
            validate="one_to_one",
        )
        .merge(
            permit_features,
            on="Market_ID",
            how="left",
            validate="one_to_one",
        )
    )

    return features

def minmax_score(series):
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(np.nan, index=series.index)

    if maximum == minimum:
        return pd.Series(50.0, index=series.index)

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    )


def reverse_minmax_score(series):
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(np.nan, index=series.index)

    if maximum == minimum:
        return pd.Series(50.0, index=series.index)

    return (
        (maximum - series)
        / (maximum - minimum)
        * 100
    )

def calculate_market_scores(features):
    scores = features.copy()

    positive_variables = [
        "Population_CAGR_Pct",
        "Five_Yr_CAGR_Pct",
        "Population_Growth_Acceleration",
        "ZHVI_YoY_Pct",
        "Homes_Sold_YoY_Pct",
        "Sale_to_List_Pct",
    ]

    negative_variables = [
        "Inventory_YoY_Pct",
        "Months_of_Supply",
    ]

    for column in positive_variables:
        scores[f"{column}_Score"] = minmax_score(
            scores[column]
        )

    for column in negative_variables:
        scores[f"{column}_Score"] = reverse_minmax_score(
            scores[column]
        )

    scores["Long_Term_Fundamentals_Score"] = (
        0.45 * scores["Population_CAGR_Pct_Score"]
        + 0.35 * scores["Five_Yr_CAGR_Pct_Score"]
        + 0.20
        * scores["Population_Growth_Acceleration_Score"]
    )

    scores["Current_Market_Momentum_Score"] = (
        0.25 * scores["ZHVI_YoY_Pct_Score"]
        + 0.20 * scores["Homes_Sold_YoY_Pct_Score"]
        + 0.20 * scores["Inventory_YoY_Pct_Score"]
        + 0.20 * scores["Months_of_Supply_Score"]
        + 0.15 * scores["Sale_to_List_Pct_Score"]
    )

    scores["Fundamentals_Rank"] = (
        scores["Long_Term_Fundamentals_Score"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    scores["Momentum_Rank"] = (
        scores["Current_Market_Momentum_Score"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    return scores

def classify_robustness(probability):
    if probability >= 75:
        return "Highly Robust"

    if probability >= 40:
        return "Moderately Robust"

    if probability >= 15:
        return "Weight Sensitive"

    return "Consistently Lower Ranked"

def run_robustness_simulation(
    scores,
    simulations=10_000,
    random_seed=42,
):
    rng = np.random.default_rng(random_seed)

    fundamental_columns = [
        "Population_CAGR_Pct_Score",
        "Five_Yr_CAGR_Pct_Score",
        "Population_Growth_Acceleration_Score",
    ]

    momentum_columns = [
        "ZHVI_YoY_Pct_Score",
        "Homes_Sold_YoY_Pct_Score",
        "Inventory_YoY_Pct_Score",
        "Months_of_Supply_Score",
        "Sale_to_List_Pct_Score",
    ]

    fundamental_values = scores[
        fundamental_columns
    ].to_numpy()

    momentum_values = scores[
        momentum_columns
    ].to_numpy()

    fundamental_weight_draws = rng.dirichlet(
        np.ones(len(fundamental_columns)),
        size=simulations,
    )

    momentum_weight_draws = rng.dirichlet(
        np.ones(len(momentum_columns)),
        size=simulations,
    )

    fundamentals_share = rng.uniform(
        0.30,
        0.70,
        size=simulations,
    )

    momentum_share = 1 - fundamentals_share

    simulated_fundamentals = (
        fundamental_values
        @ fundamental_weight_draws.T
    )

    simulated_momentum = (
        momentum_values
        @ momentum_weight_draws.T
    )

    simulated_overall = (
        simulated_fundamentals
        * fundamentals_share
        + simulated_momentum
        * momentum_share
    )

    order = np.argsort(-simulated_overall, axis=0)
    ranks = np.empty_like(order, dtype=int)

    simulation_numbers = np.arange(simulations)

    for rank_position in range(len(scores)):
        ranks[
            order[rank_position, :],
            simulation_numbers,
        ] = rank_position + 1

    top_n = min(3, len(scores))

    summary = pd.DataFrame({
        "Market_ID": scores["Market_ID"],
        "Pct_Top_3": (
            (ranks <= top_n).mean(axis=1) * 100
        ),
        "Average_Rank": ranks.mean(axis=1),
    })

    summary["Robustness_Profile"] = (
        summary["Pct_Top_3"].apply(
            classify_robustness
        )
    )

    return summary

def classify_regime(row):
    fundamentals = row[
        "Long_Term_Fundamentals_Score"
    ]

    momentum = row[
        "Current_Market_Momentum_Score"
    ]

    if fundamentals >= 50 and momentum >= 50:
        return "Strong / Expanding"

    if fundamentals >= 50 and momentum < 50:
        return "Long-Term Strength / Near-Term Pressure"

    if fundamentals < 50 and momentum >= 50:
        return "Momentum-Led / Developing Fundamentals"

    return "Weak / Transitional"

def build_model_outputs(
    home_values,
    market_activity,
    population,
    permits,
):
    features = build_market_feature_table(
        home_values,
        market_activity,
        population,
        permits,
    )

    if len(features) < 3:
        raise ValueError(
            "At least three fully matched markets are required."
        )

    scores = calculate_market_scores(features)

    robustness = run_robustness_simulation(scores)

    decision = scores.merge(
        robustness,
        on="Market_ID",
        how="left",
        validate="one_to_one",
    )

    decision["Current_Market_Regime"] = (
        decision.apply(classify_regime, axis=1)
    )

    required_output_columns = [
        "City",
        "State",
        "Market_ID",
        "Long_Term_Fundamentals_Score",
        "Fundamentals_Rank",
        "Current_Market_Momentum_Score",
        "Momentum_Rank",
        "Pct_Top_3",
        "Average_Rank",
        "Robustness_Profile",
        "Current_Market_Regime",
    ]

    decision_table = decision[
        required_output_columns
    ].copy()

    return {
        "decision": decision_table,
        "features": features,
        "scores": scores,
        "home_values": home_values,
        "market_activity": market_activity,
        "population": population,
        "permits": permits,
    }

def read_census_population_upload(uploaded_file):
    """
    Convert a Census state place-estimates download into:
    City, State, Year, Population
    """
    uploaded_file.seek(0)

    raw = pd.read_csv(
        uploaded_file,
        header=3,
        dtype=str,
    )

    raw = raw.rename(
        columns={raw.columns[0]: "Geographic_Area"}
    )

    year_columns = [
        column
        for column in raw.columns
        if str(column).strip().isdigit()
    ]

    if not year_columns:
        raise ValueError(
            "No annual population columns were found in the "
            "Census population file."
        )

    result = raw.melt(
        id_vars=["Geographic_Area"],
        value_vars=year_columns,
        var_name="Year",
        value_name="Population",
    )

    result["State_Name"] = (
        result["Geographic_Area"]
        .str.extract(r",\s*([^,]+)$", expand=False)
        .str.strip()
        .str.upper()
    )

    result["State"] = result["State_Name"].map(
        STATE_ABBREVIATIONS
    )

    result["City"] = (
        result["Geographic_Area"]
        .str.replace(r",\s*[^,]+$", "", regex=True)
        .str.replace(
            r"\s+(city|town|village|borough|municipality)$",
            "",
            regex=True,
        )
        .str.strip()
    )

    result = result[
        result["City"].notna()
        & result["State"].notna()
        & result["Year"].notna()
        & result["Population"].notna()
    ].copy()

    result = result[
        result["City"].astype(str).str.strip().ne("")
        & result["State"].astype(str).str.strip().ne("")
    ]

    return result[
        ["City", "State", "Year", "Population"]
    ]

def process_raw_market_activity(df):
    raw = df.copy()

    raw.columns = (
        raw.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    if "REGION TYPE" in raw.columns:
        raw = raw[
            raw["REGION TYPE"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("city")
        ].copy()

    required_source_columns = {
        "REGION NAME",
        "PERIOD END",
        "HOMES SOLD",
        "MONTHS OF SUPPLY",
        "AVERAGE SALE TO LIST RATIO (%)",
    }

    inventory_column = next(
        (
            column
            for column in [
                "INVENTORY",
                "ACTIVE LISTINGS",
            ]
            if column in raw.columns
        ),
        None,
    )

    if inventory_column is None:
        raise ValueError(
            "The Redfin file must contain INVENTORY "
            "or ACTIVE LISTINGS."
        )

    missing = required_source_columns - set(raw.columns)

    if missing:
        raise ValueError(
            "The selected Redfin download does not contain: "
            + ", ".join(sorted(missing))
            + ". Download a city-level file containing all required "
              "market-activity measurements."
        )

    identity = raw["REGION NAME"].str.rsplit(
        ",",
        n=1,
        expand=True,
    )

    result = pd.DataFrame({
        "City": identity[0].str.strip(),
        "State": identity[1].str.strip(),
        "Date": raw["PERIOD END"],
        "Homes_Sold": raw["HOMES SOLD"],
        "Inventory": raw[inventory_column],
        "Months_of_Supply": raw["MONTHS OF SUPPLY"],
        "Sale_to_List_Pct": (
            raw["AVERAGE SALE TO LIST RATIO (%)"]
        ),
    })

    result = process_market_activity(result)

    result = result.dropna(
        subset=[
            "City",
            "State",
            "Date",
            "Homes_Sold",
            "Inventory",
            "Months_of_Supply",
            "Sale_to_List_Pct",
            "Market_ID",
        ]
    ).copy()

    ambiguous_markets = result.loc[
        result.duplicated(
            subset=["Market_ID", "Date"],
            keep=False,
        ),
        "Market_ID",
    ].unique()

    result = result[
        ~result["Market_ID"].isin(ambiguous_markets)
    ].copy()

    return (
        result
        .drop_duplicates(
            subset=["Market_ID", "Date"],
            keep="last",
        )
        .sort_values(["Market_ID", "Date"])
        .reset_index(drop=True)
    )