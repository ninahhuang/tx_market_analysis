from pathlib import Path

import pandas as pd
import streamlit as st


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="North Dallas Housing Market Analysis",
    page_icon="🏠",
    layout="wide"
)


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

@st.cache_data
def load_data():

    market = pd.read_csv(
        DATA_DIR / "dallas_market_master.csv"
    )

    scores = pd.read_csv(
        DATA_DIR / "dallas_market_scores.csv"
    )

    robustness = pd.read_csv(
        DATA_DIR / "dallas_ranking_robustness.csv"
    )

    diagnostics = pd.read_csv(
        DATA_DIR / "dallas_market_diagnostics.csv"
    )

    decision = pd.read_csv(
        DATA_DIR / "dallas_final_decision_table.csv"
    )

    zhvi = pd.read_csv(
        DATA_DIR / "dallas_zhvi_monthly.csv"
    )

    population = pd.read_csv(
        DATA_DIR / "dallas_population_annual.csv"
    )

    permits = pd.read_csv(
        DATA_DIR / "dallas_building_permits_annual.csv"
    )

    return {
        "market": market,
        "scores": scores,
        "robustness": robustness,
        "diagnostics": diagnostics,
        "decision": decision,
        "zhvi": zhvi,
        "population": population,
        "permits": permits,
    }


data = load_data()

market = data["market"]
scores = data["scores"]
robustness = data["robustness"]
diagnostics = data["diagnostics"]
decision = data["decision"]
zhvi = data["zhvi"]
population = data["population"]
permits = data["permits"]

# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

st.title("North Dallas Housing Market Analysis")

st.markdown(
    """
    A data-driven comparison of nine North Dallas housing markets
    using home values, population growth, residential construction,
    current market activity, and investment-ranking robustness.
    """
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Executive Overview",
        "Market Explorer",
        "Fundamentals vs Momentum",
        "Investor Scenarios",
        "Methodology",
    ]
)

# EXECUTIVE OVERVIEW
with tab1:

    st.header("Executive Overview")

    st.markdown(
        """
        This dashboard compares nine North Dallas housing markets
        across long-term growth fundamentals, current market momentum,
        residential construction, and ranking robustness.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Strongest Fundamentals",
        "Celina"
    )

    col2.metric(
        "Strongest Momentum",
        "Plano"
    )

    col3.metric(
        "Most Robust",
        "Plano"
    )

    col4.metric(
        "Strong Momentum Contender",
        "Richardson"
    )

    st.subheader("Final Market Ranking Summary")

    display_columns = [
        "City",
        "Long_Term_Fundamentals_Score",
        "Fundamentals_Rank",
        "Current_Market_Momentum_Score",
        "Momentum_Rank",
        "Pct_Top_3",
        "Average_Rank",
        "Robustness_Profile",
        "Current_Market_Regime"
    ]

    available_columns = [
        col for col in display_columns
        if col in decision.columns
    ]

    st.dataframe(
        decision[available_columns],
        use_container_width=True,
        hide_index=True
    )

# MARKET EXPLORER

with tab2:

    st.header("Market Explorer")

    cities = sorted(market["City"].unique())

    selected_city = st.selectbox(
        "Select a market",
        cities
    )

    city_data = market[
        market["City"] == selected_city
    ].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "5-Year Home Value CAGR",
        f"{city_data['Five_Yr_CAGR_Pct']:.2f}%"
    )

    col2.metric(
        "Population CAGR",
        f"{city_data['Population_CAGR_Pct']:.2f}%"
    )

    col3.metric(
        "Home Sales YoY",
        f"{city_data['Homes_Sold_YoY_Pct']:.2f}%"
    )

    col4.metric(
        "Months of Supply",
        f"{city_data['Months_of_Supply']:.2f}"
    )

    st.subheader("Home Value Trend")

    city_zhvi = (
        zhvi[
            zhvi["City"] == selected_city
        ]
        .sort_values("Date")
    )

    st.line_chart(
        city_zhvi,
        x="Date",
        y="ZHVI"
    )

    st.subheader("Population Growth")

    city_population = (
        population[
            population["City"] == selected_city
        ]
        .sort_values("Year")
    )

    st.line_chart(
        city_population,
        x="Year",
        y="Population"
    )

    st.subheader("Residential Construction")

    city_permits = (
        permits[
            permits["City"] == selected_city
        ]
        .sort_values("Year")
    )

    st.line_chart(
        city_permits,
        x="Year",
        y="Total_Units_Permitted"
    )

# FUNDAMENTALS VS. MOMENTUM

with tab3:

    st.header("Long-Term Fundamentals vs Current Momentum")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(
        scores["Long_Term_Fundamentals_Score"],
        scores["Current_Market_Momentum_Score"]
    )

    for _, row in scores.iterrows():
        ax.annotate(
            row["City"],
            (
                row["Long_Term_Fundamentals_Score"],
                row["Current_Market_Momentum_Score"]
            ),
            xytext=(5, 5),
            textcoords="offset points"
        )

    ax.axvline(
        50,
        linestyle="--",
        alpha=0.5
    )

    ax.axhline(
        50,
        linestyle="--",
        alpha=0.5
    )

    ax.set_xlabel(
        "Long-Term Fundamentals Score"
    )

    ax.set_ylabel(
        "Current Market Momentum Score"
    )

    ax.set_title(
        "Market Positioning: Fundamentals vs Momentum"
    )

    ax.grid(alpha=0.2)

    st.pyplot(fig)

    st.markdown(
        """
        **Interpretation**

        - Upper-right: strong fundamentals + strong momentum
        - Upper-left: weaker fundamentals + strong momentum
        - Lower-right: strong fundamentals + weak momentum
        - Lower-left: weaker fundamentals + weak momentum
        """
    )

# INVESTOR SCENARIOS TAB

with tab4:

    st.header("Investor Scenarios & Ranking Robustness")

    scenario = st.radio(
        "Investor Priority",
        [
            "Growth-Oriented",
            "Balanced",
            "Momentum-Oriented"
        ],
        horizontal=True
    )

    score_map = {
        "Growth-Oriented": "Growth_Oriented_Score",
        "Balanced": "Balanced_Score",
        "Momentum-Oriented": "Momentum_Oriented_Score"
    }

    selected_score = score_map[scenario]

    scenario_table = (
        scores[
            [
                "City",
                selected_score
            ]
        ]
        .sort_values(
            selected_score,
            ascending=False
        )
    )

    st.dataframe(
        scenario_table,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Top-3 Probability Across 10,000 Weighting Scenarios"
    )

    robustness_plot = (
        robustness[
            [
                "City",
                "Pct_Top_3"
            ]
        ]
        .sort_values(
            "Pct_Top_3",
            ascending=False
        )
    )

    st.bar_chart(
        robustness_plot,
        x="City",
        y="Pct_Top_3"
    )

    st.subheader("Ranking Robustness")

    st.dataframe(
        robustness[
            [
                "City",
                "Pct_Rank_1",
                "Pct_Top_3",
                "Average_Rank",
                "Robustness_Profile"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# METHODOLOGY TAB

with tab5:

    st.header("Methodology")

    st.markdown(
        """
        ### Long-Term Fundamentals

        The long-term fundamentals score combines:

        - Population CAGR
        - Five-year home-value CAGR
        - Population growth acceleration

        ### Current Market Momentum

        The current momentum score incorporates:

        - ZHVI year-over-year growth
        - Home sales year-over-year growth
        - Sale-to-list ratio
        - Inventory growth
        - Months of supply

        Indicators are normalized to a 0–100 scale.

        Variables where lower values indicate stronger market
        conditions are reverse-scored.

        ### Ranking Robustness

        The model evaluates 10,000 alternative weighting scenarios
        to measure:

        - Probability of ranking #1
        - Probability of ranking in the Top 3
        - Average market rank
        - Composite-score dispersion
        - Sensitivity to investor priorities
        """
    )

    st.markdown(
        """
        ### Data Sources

        **Zillow Research**
        - Zillow Home Value Index (ZHVI)

        **Redfin Data Center**
        - Sales activity
        - Pending sales
        - Inventory
        - New listings
        - Days on market
        - Months of supply
        - Sale-to-list ratio

        **U.S. Census Bureau**
        - Population Estimates Program
        - Building Permits Survey
        """
    )

    st.markdown(
        """
        ### Limitations

        - Market-level analysis does not capture neighborhood-level differences.
        - Building permits represent authorized construction, not completed units.
        - Recent housing-market indicators can change quickly.
        - Composite rankings depend on the selected investor priorities.
        - Historical appreciation does not guarantee future returns.
        - The model is intended as a market-screening framework rather than a forecast of investment returns.
        """
    )