from pathlib import Path

import altair as alt
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

#
# FIGMA CONFIGURATION
#

st.markdown(
    """
    <style>
        /* Overall page */
        .stApp {
            background: #F6F7F9;
            color: #172B3A;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* Main page header */
        .dashboard-title {
            margin: 0;
            color: #172B3A;
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .dashboard-subtitle {
            max-width: 900px;
            margin: 0.45rem 0 0;
            color: #5E6C76;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .dashboard-source {
            margin-top: 0.35rem;
            color: #89949D;
            font-size: 0.75rem;
        }

        .dashboard-divider {
            height: 1px;
            margin: 1.5rem 0 1.8rem;
            background: #CDD5DB;
        }

        /* Section headings */
        .section-heading {
            margin: 0;
            color: #172B3A;
            font-size: 1.45rem;
            font-weight: 700;
        }

        .section-subtitle {
            margin: 0.25rem 0 1rem;
            color: #66737D;
            font-size: 0.86rem;
        }

        .section-spacer {
            height: 1.6rem;
        }

        /* KPI cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin: 0.9rem 0 2.2rem;
        }

        .kpi-card {
            min-height: 132px;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #DDE4E9;
            border-radius: 12px;
            box-sizing: border-box;
        }

        .kpi-label {
            color: #66737D;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.045em;
            text-transform: uppercase;
        }

        .kpi-city {
            margin-top: 0.75rem;
            color: #172B3A;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .kpi-detail {
            margin-top: 0.3rem;
            color: #66737D;
            font-size: 0.8rem;
        }

        /* Comparison table */
        .comparison-card {
            overflow-x: auto;
            padding: 0.35rem 1rem 0.6rem;
            background: #FFFFFF;
            border: 1px solid #B7CAD8;
            border-radius: 10px;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            color: #293B48;
            font-size: 0.79rem;
        }

        .comparison-table th {
            padding: 0.8rem 0.65rem;
            border-bottom: 1px solid #AEBCC6;
            color: #53636E;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.025em;
            text-align: left;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .comparison-table td {
            padding: 0.72rem 0.65rem;
            border-bottom: 1px solid #E1E7EB;
        }

        .comparison-table tr:last-child td {
            border-bottom: none;
        }

        .comparison-table td:first-child {
            color: #172B3A;
            font-weight: 700;
        }

        /* Model takeaway */
        .takeaway-card {
            margin: 1rem 0 2rem;
            padding: 1rem 1.1rem;
            background: #DDEBFF;
            border-left: 4px solid #5077A3;
            border-radius: 8px;
        }

        .takeaway-title {
            margin-bottom: 0.35rem;
            color: #1C3852;
            font-size: 0.88rem;
            font-weight: 700;
        }

        .takeaway-text {
            color: #405565;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        /* Interpretation cards */
        .interpretation-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .interpretation-card {
            min-height: 245px;
            padding: 1.35rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
            box-sizing: border-box;
        }

        .interpretation-city {
            color: #172B3A;
            font-size: 1.4rem;
            font-weight: 700;
        }

        .interpretation-profile {
            display: inline-block;
            margin-top: 0.35rem;
            padding: 0.25rem 0.55rem;
            background: #E7EEF3;
            border-radius: 999px;
            color: #3D586B;
            font-size: 0.72rem;
            font-weight: 600;
        }

        .score-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.7rem;
            margin: 1rem 0;
        }

        .score-label {
            color: #7B8790;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .score-value {
            margin-top: 0.2rem;
            color: #223947;
            font-size: 0.96rem;
            font-weight: 700;
        }

        .interpretation-text {
            color: #53636E;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .best-fit {
            margin-top: 1rem;
            color: #435762;
            font-size: 0.77rem;
        }

        /* Market Explorer */
        .explorer-selection {
            margin: 0.4rem 0 1rem;
            color: #66737D;
            font-size: 0.8rem;
        }

        .explorer-regime-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
            margin: 0.35rem 0 1.25rem;
        }

        .explorer-badge {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            background: #E7EEF3;
            border-radius: 999px;
            color: #3D586B;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .explorer-profile-badge {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            background: #EEF2F5;
            border-radius: 999px;
            color: #53636E;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .market-summary-card {
            margin-top: 1.25rem;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .market-summary-title {
            margin-bottom: 0.75rem;
            color: #172B3A;
            font-size: 1.05rem;
            font-weight: 700;
        }

        .market-summary-text {
            color: #53636E;
            font-size: 0.85rem;
            line-height: 1.6;
        }

        .market-summary-metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .market-summary-metric {
            padding: 0.8rem;
            background: #F6F8FA;
            border-radius: 8px;
        }

        .market-summary-label {
            color: #7B8790;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .market-summary-value {
            margin-top: 0.2rem;
            color: #223947;
            font-size: 1rem;
            font-weight: 700;
        }
        
        /* Fundamentals vs. Momentum */
        .quadrant-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.5rem;
        }

        .quadrant-card {
            min-height: 145px;
            padding: 1.15rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .quadrant-card-title {
            color: #172B3A;
            font-size: 0.93rem;
            font-weight: 700;
        }

        .quadrant-card-location {
            margin-top: 0.2rem;
            color: #78909F;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .quadrant-card-text {
            margin-top: 0.65rem;
            color: #53636E;
            font-size: 0.8rem;
            line-height: 1.55;
        }

        /* Investor Scenarios */
        .scenario-leader-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.75rem;
        }

        .scenario-definition {
            margin: 0.5rem 0 1.25rem;
            padding: 1rem 1.15rem;
            background: #EAF0F5;
            border-left: 4px solid #5077A3;
            border-radius: 8px;
        }

        .scenario-definition-title {
            color: #24445C;
            font-size: 0.9rem;
            font-weight: 700;
        }

        .scenario-definition-text {
            margin-top: 0.35rem;
            color: #536978;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .scenario-weight-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.7rem;
        }

        .scenario-weight {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            background: #FFFFFF;
            border: 1px solid #CFD9E0;
            border-radius: 999px;
            color: #435C6D;
            font-size: 0.72rem;
            font-weight: 700;
        }

        /* Methodology */
        .methodology-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.75rem;
        }

        .methodology-card {
            min-height: 245px;
            padding: 1.3rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .methodology-card-number {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            margin-bottom: 0.9rem;
            background: #E7EEF3;
            border-radius: 50%;
            color: #3D586B;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .methodology-card-title {
            color: #172B3A;
            font-size: 1.05rem;
            font-weight: 700;
        }

        .methodology-card-subtitle {
            margin-top: 0.35rem;
            color: #66737D;
            font-size: 0.78rem;
            line-height: 1.5;
        }

        .methodology-list {
            margin: 0.9rem 0 0;
            padding-left: 1.2rem;
            color: #53636E;
            font-size: 0.82rem;
            line-height: 1.65;
        }

        .methodology-note {
            margin-top: 1rem;
            padding: 0.8rem;
            background: #F5F7F9;
            border-radius: 8px;
            color: #53636E;
            font-size: 0.78rem;
            line-height: 1.5;
        }

        .source-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.75rem;
        }

        .source-card {
            min-height: 190px;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .source-name {
            color: #172B3A;
            font-size: 1rem;
            font-weight: 700;
        }

        .source-type {
            margin-top: 0.25rem;
            color: #78909F;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .source-list {
            margin: 0.9rem 0 0;
            padding-left: 1.15rem;
            color: #53636E;
            font-size: 0.8rem;
            line-height: 1.65;
        }

        .limitations-card {
            padding: 1.3rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .limitations-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem 1.5rem;
            margin: 0;
            padding-left: 1.2rem;
            color: #53636E;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .methodology-disclaimer {
            margin-top: 1rem;
            padding: 1rem 1.15rem;
            background: #F7EDDD;
            border-left: 4px solid #B88746;
            border-radius: 8px;
        }

        .methodology-disclaimer-title {
            color: #674E2E;
            font-size: 0.86rem;
            font-weight: 700;
        }

        .methodology-disclaimer-text {
            margin-top: 0.3rem;
            color: #695A47;
            font-size: 0.8rem;
            line-height: 1.55;
        }

        /* Responsive behavior */
        
        @media (max-width: 950px) {
            .kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .kpi-grid,
            .interpretation-grid {
                grid-template-columns: 1fr;
            }

            .market-summary-metrics {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .quadrant-grid {
                grid-template-columns: 1fr;
            }

            .scenario-leader-grid {
                grid-template-columns: 1fr;
            }

            .methodology-grid,
            .source-grid,
            .limitations-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
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

def get_market_result(city):
    """Return one city's final model result."""
    matches = decision.loc[decision["City"] == city]

    if matches.empty:
        raise ValueError(f"{city} is missing from the final decision table.")

    return matches.iloc[0]

def compact_html(markup):
    """
    Remove indentation while preserving spaces between
    text that is split across multiple source-code lines.
    """
    return " ".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )

def kpi_card(label, city, detail):
    """Return the HTML for one KPI card."""
    return compact_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-city">{city}</div>
            <div class="kpi-detail">{detail}</div>
        </div>
        """
    )


def interpretation_card(
    city,
    profile,
    description,
    best_fit,
):
    """Build an interpretation card using live CSV values."""
    row = get_market_result(city)

    fundamentals = row[
        "Long_Term_Fundamentals_Score"
    ]
    momentum = row[
        "Current_Market_Momentum_Score"
    ]
    top_three = row["Pct_Top_3"]

    return compact_html(
        f"""
        <div class="interpretation-card">
            <div class="interpretation-city">
                {city}
            </div>

            <div class="interpretation-profile">
                {profile}
            </div>

            <div class="score-row">
                <div>
                    <div class="score-label">
                        Fundamentals
                    </div>
                    <div class="score-value">
                        {fundamentals:.2f}
                    </div>
                </div>

                <div>
                    <div class="score-label">
                        Momentum
                    </div>
                    <div class="score-value">
                        {momentum:.2f}
                    </div>
                </div>

                <div>
                    <div class="score-label">
                        Top-3 Prob.
                    </div>
                    <div class="score-value">
                        {top_three:.2f}%
                    </div>
                </div>
            </div>

            <div class="interpretation-text">
                {description}
            </div>

            <div class="best-fit">
                <strong>Best fit:</strong> {best_fit}
            </div>
        </div>
        """
    )

# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

st.markdown(
    """
    <h1 class="dashboard-title">
        North Dallas Housing Market Analysis
    </h1>

    <div class="dashboard-subtitle">
        Comparing long-term fundamentals, current market momentum,
        and ranking robustness across nine North Dallas markets.
    </div>

    <div class="dashboard-source">
        Zillow Research · Redfin Data Center · U.S. Census Bureau
    </div>

    <div class="dashboard-divider"></div>
    """,
    unsafe_allow_html=True,
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

    st.markdown(
        """
        <h2 class="section-heading">Market Overview</h2>
        <div class="section-subtitle">
            Key findings from the current market screening model
        </div>
        """,
        unsafe_allow_html=True,
    )

    celina = get_market_result("Celina")
    plano = get_market_result("Plano")
    richardson = get_market_result("Richardson")

    kpi_cards = [
        kpi_card(
            "Strongest Fundamentals",
            "Celina",
            (
                f"Score {celina['Long_Term_Fundamentals_Score']:.2f}"
                f" · Rank #{int(celina['Fundamentals_Rank'])}"
            ),
        ),
        kpi_card(
            "Strongest Momentum",
            "Plano",
            (
                f"Score {plano['Current_Market_Momentum_Score']:.2f}"
                f" · Rank #{int(plano['Momentum_Rank'])}"
            ),
        ),
        kpi_card(
            "Most Robust",
            "Plano",
            f"{plano['Pct_Top_3']:.2f}% Top-3 Probability",
        ),
        kpi_card(
            "Strong Momentum Contender",
            "Richardson",
            (
                f"Momentum {richardson['Current_Market_Momentum_Score']:.2f}"
                f" · Rank #{int(richardson['Momentum_Rank'])}"
            ),
        ),
    ]

    kpi_grid_html = compact_html(
        '<div class="kpi-grid">'
        + "".join(kpi_cards)
        + "</div>"
    )

    st.markdown(
        kpi_grid_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h2 class="section-heading">Final Market Ranking</h2>
        <div class="section-subtitle">
            Integrated comparison of fundamentals, momentum,
            ranking robustness, and current market conditions
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h3 style="margin: 0; font-size: 1.05rem;">
            Market Ranking Robustness
        </h3>
        <div class="section-subtitle">
            Probability of ranking in the Top 3 across
            10,000 weighting scenarios
        </div>
        """,
        unsafe_allow_html=True,
    )

    robustness_plot = (
        robustness[["City", "Pct_Top_3"]]
        .copy()
        .sort_values("Pct_Top_3", ascending=False)
    )

    robustness_plot["Full_Scale"] = 100
    robustness_plot["Probability_Label"] = (
        robustness_plot["Pct_Top_3"]
        .map(lambda value: f"{value:.2f}%")
    )

    city_order = robustness_plot["City"].tolist()

    chart_base = alt.Chart(robustness_plot).encode(
        y=alt.Y(
            "City:N",
            sort=city_order,
            title=None,
            axis=alt.Axis(
                labelColor="#293B48",
                labelFontSize=13,
                labelFontWeight=600,
                labelPadding=10,
                ticks=False,
                domain=False,
            ),
        )
    )

    background_bars = chart_base.mark_bar(
        color="#E6EDF2",
        cornerRadiusEnd=7,
        size=17,
    ).encode(
        x=alt.X(
            "Full_Scale:Q",
            scale=alt.Scale(domain=[0, 100]),
            title="Top-3 probability",
            axis=alt.Axis(
                values=[0, 25, 50, 75, 100],
                labelExpr="datum.value + '%'",
                grid=True,
                gridColor="#E5EAEE",
                tickColor="#C7D0D7",
                domain=False,
                titleColor="#66737D",
                labelColor="#66737D",
            ),
        )
    )

    probability_bars = chart_base.mark_bar(
        color="#334E68",
        cornerRadiusEnd=7,
        size=17,
    ).encode(
        x=alt.X(
            "Pct_Top_3:Q",
            scale=alt.Scale(domain=[0, 100]),
            title="Top-3 probability",
        ),
        tooltip=[
            alt.Tooltip("City:N", title="Market"),
            alt.Tooltip(
                "Pct_Top_3:Q",
                title="Top-3 probability",
                format=".2f",
            ),
        ],
    )

    probability_labels = chart_base.mark_text(
        align="left",
        baseline="middle",
        dx=7,
        color="#33404A",
        fontSize=12,
        fontWeight=600,
    ).encode(
        x=alt.X("Pct_Top_3:Q"),
        text=alt.Text("Probability_Label:N"),
    )

    robustness_chart = (
        background_bars
        + probability_bars
        + probability_labels
    ).properties(
        height=340
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):
        st.altair_chart(
            robustness_chart,
            use_container_width=True,
        )

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            Final Market Comparison
        </h3>
        <div class="section-subtitle">
            Integrated view of fundamentals, momentum,
            ranking robustness, and current market conditions
        </div>
        """,
        unsafe_allow_html=True,
    )

    comparison_table = decision[
        [
            "City",
            "Long_Term_Fundamentals_Score",
            "Current_Market_Momentum_Score",
            "Pct_Top_3",
            "Average_Rank",
            "Current_Market_Regime",
        ]
    ].copy()

    comparison_table = comparison_table.rename(
        columns={
            "City": "Market",
            "Long_Term_Fundamentals_Score": "Fundamentals",
            "Current_Market_Momentum_Score": "Momentum",
            "Pct_Top_3": "Top-3 Prob.",
            "Average_Rank": "Avg. Rank",
            "Current_Market_Regime": "Market Regime",
        }
    )

    comparison_table["Fundamentals"] = comparison_table[
        "Fundamentals"
    ].map(lambda value: f"{value:.2f}")

    comparison_table["Momentum"] = comparison_table[
        "Momentum"
    ].map(lambda value: f"{value:.2f}")

    comparison_table["Top-3 Prob."] = comparison_table[
        "Top-3 Prob."
    ].map(lambda value: f"{value:.2f}%")

    comparison_table["Avg. Rank"] = comparison_table[
        "Avg. Rank"
    ].map(lambda value: f"{value:.2f}")

    comparison_html = comparison_table.to_html(
        index=False,
        border=0,
        classes="comparison-table",
        escape=True,
    )

    comparison_card_html = compact_html(
        f"""
        <div class="comparison-card">
            {comparison_html}
        </div>
        """
    )

    st.markdown(
        comparison_card_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="takeaway-card">
            <div class="takeaway-title">Model Takeaway</div>
            <div class="takeaway-text">
                Plano offers the strongest combination of current
                momentum and ranking robustness, while Melissa provides
                a stronger balance of long-term fundamentals and present
                conditions. Richardson emerges as another relatively
                stable, momentum-oriented contender, while Celina
                represents the strongest long-term growth thesis but
                faces substantial current supply pressure.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h2 class="section-heading">Market Interpretation</h2>
        <div class="section-subtitle">
            What the model suggests about the strongest
            investment candidates
        </div>
        """,
        unsafe_allow_html=True,
    )

    interpretation_cards = [
        interpretation_card(
            city="Plano",
            profile="Current Resilience Leader",
            description=(
                "Plano combines the strongest current market momentum "
                "with the highest ranking robustness. Its lower "
                "fundamentals score reflects a more mature growth "
                "profile, while current conditions remain comparatively "
                "resilient."
            ),
            best_fit="stability and near-term market strength",
        ),
        interpretation_card(
            city="Melissa",
            profile="Balanced Growth Candidate",
            description=(
                "Melissa combines relatively strong long-term "
                "fundamentals with solid current momentum and strong "
                "ranking robustness. It offers one of the most balanced "
                "profiles in the analysis."
            ),
            best_fit="balance between growth and current conditions",
        ),
        interpretation_card(
            city="Richardson",
            profile="Momentum-Oriented Contender",
            description=(
                "Richardson shows strong current momentum with moderate "
                "long-term fundamentals. Its relatively stable market "
                "regime and Top-3 probability make it a credible "
                "alternative to the leading markets."
            ),
            best_fit="present-day resilience over rapid expansion",
        ),
        interpretation_card(
            city="Celina",
            profile="Long-Term Growth Leader",
            description=(
                "Celina ranks first in long-term fundamentals, supported "
                "by strong population and historical home-value growth. "
                "Weak current momentum and supply pressure make the "
                "investment thesis more dependent on a longer horizon."
            ),
            best_fit="long-term appreciation potential",
        ),
    ]

    interpretation_grid_html = compact_html(
        '<div class="interpretation-grid">'
        + "".join(interpretation_cards)
        + "</div>"
    )

    st.markdown(
        interpretation_grid_html,
        unsafe_allow_html=True,
    )

# MARKET EXPLORER

with tab2:

    # --------------------------------------------------------
    # SECTION HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <h2 class="section-heading">Market Explorer</h2>
        <div class="section-subtitle">
            Explore long-term growth, current housing-market
            conditions, and model results for an individual
            North Dallas market
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CITY SELECTOR
    # --------------------------------------------------------

    cities = sorted(market["City"].dropna().unique())

    selected_city = st.selectbox(
        "Select a market",
        cities,
        key="market_explorer_city",
    )

    # Pull the selected city's master-market metrics.
    city_data = (
        market.loc[market["City"] == selected_city]
        .iloc[0]
    )

    # Pull the selected city's final model results.
    city_result = get_market_result(selected_city)

    # --------------------------------------------------------
    # MARKET CLASSIFICATION BADGES
    # --------------------------------------------------------

    st.markdown(
        compact_html(
            f"""
            <div class="explorer-regime-row">
                <div class="explorer-badge">
                    {city_result['Current_Market_Regime']}
                </div>
                <div class="explorer-profile-badge">
                    {city_result['Robustness_Profile']}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    explorer_kpis = [
        kpi_card(
            "5-Year Home Value CAGR",
            f"{city_data['Five_Yr_CAGR_Pct']:.2f}%",
            "Annualized five-year home-value growth",
        ),
        kpi_card(
            "Population CAGR",
            f"{city_data['Population_CAGR_Pct']:.2f}%",
            "Annualized population growth",
        ),
        kpi_card(
            "Home Sales YoY",
            f"{city_data['Homes_Sold_YoY_Pct']:.2f}%",
            "Current transaction activity",
        ),
        kpi_card(
            "Months of Supply",
            f"{city_data['Months_of_Supply']:.2f}",
            "Current inventory conditions",
        ),
    ]

    explorer_kpi_html = compact_html(
        '<div class="kpi-grid">'
        + "".join(explorer_kpis)
        + "</div>"
    )

    st.markdown(
        explorer_kpi_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # HOME VALUE TREND
    # --------------------------------------------------------

    city_zhvi = (
        zhvi.loc[zhvi["City"] == selected_city]
        .copy()
    )

    city_zhvi["Date"] = pd.to_datetime(
        city_zhvi["Date"]
    )

    city_zhvi = city_zhvi.sort_values("Date")

    home_value_line = (
        alt.Chart(city_zhvi)
        .mark_line(
            color="#334E68",
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                axis=alt.Axis(
                    format="%Y",
                    labelColor="#66737D",
                    titleColor="#66737D",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "ZHVI:Q",
                title="Typical home value",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format="$,.0f",
                    labelColor="#66737D",
                    titleColor="#66737D",
                    gridColor="#E5EAEE",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%B %Y",
                ),
                alt.Tooltip(
                    "ZHVI:Q",
                    title="Typical home value",
                    format="$,.0f",
                ),
            ],
        )
    )

    home_value_points = (
        alt.Chart(city_zhvi)
        .mark_circle(
            color="#334E68",
            size=30,
            opacity=0,
        )
        .encode(
            x="Date:T",
            y=alt.Y(
                "ZHVI:Q",
                scale=alt.Scale(zero=False),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%B %Y",
                ),
                alt.Tooltip(
                    "ZHVI:Q",
                    title="Typical home value",
                    format="$,.0f",
                ),
            ],
        )
    )

    home_value_chart = (
        home_value_line + home_value_points
    ).properties(
        height=340
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):

        st.markdown(
            f"""
            ### Home Value Trend

            Historical Zillow Home Value Index for {selected_city}
            """
        )

        st.altair_chart(
            home_value_chart,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # POPULATION AND CONSTRUCTION CHARTS
    # --------------------------------------------------------

    chart_col1, chart_col2 = st.columns(
        2,
        gap="large",
    )

    # Population data for the selected city.
    city_population = (
        population.loc[
            population["City"] == selected_city
        ]
        .copy()
        .sort_values("Year")
    )

    population_chart = (
        alt.Chart(city_population)
        .mark_line(
            color="#5077A3",
            strokeWidth=3,
            point=alt.OverlayMarkDef(
                filled=True,
                fill="#5077A3",
                size=65,
            ),
        )
        .encode(
            x=alt.X(
                "Year:O",
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelColor="#66737D",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "Population:Q",
                title="Population",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format=",.0f",
                    labelColor="#66737D",
                    titleColor="#66737D",
                    gridColor="#E5EAEE",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Year:O",
                    title="Year",
                ),
                alt.Tooltip(
                    "Population:Q",
                    title="Population",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Population_YoY_Pct:Q",
                    title="Annual growth",
                    format=".2f",
                ),
            ],
        )
        .properties(height=280)
        .configure_view(stroke=None)
    )

    with chart_col1:

        with st.container(border=True):

            st.markdown(
                """
                ### Population Growth

                Annual Census population estimates
                """
            )

            st.altair_chart(
                population_chart,
                use_container_width=True,
            )

    # Construction data for the selected city.
    city_permits = (
        permits.loc[
            permits["City"] == selected_city
        ]
        .copy()
        .sort_values("Year")
    )

    permits_chart = (
        alt.Chart(city_permits)
        .mark_bar(
            color="#7392AA",
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        )
        .encode(
            x=alt.X(
                "Year:O",
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelColor="#66737D",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "Permits_Per_1000_Residents:Q",
                title="Permitted units per 1,000 residents",
                axis=alt.Axis(
                    format=",.0f",
                    labelColor="#66737D",
                    titleColor="#66737D",
                    gridColor="#E5EAEE",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Year:O",
                    title="Year",
                ),
                alt.Tooltip(
                    "Permits_Per_1000_Residents:Q",
                    title="Permits per 1,000",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Total_Units_Permitted:Q",
                    title="Total units",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Single_Family_Units:Q",
                    title="Single-family units",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Multifamily_Units:Q",
                    title="Multifamily units",
                    format=",.0f",
                ),
            ],
        )
        .properties(height=280)
        .configure_view(stroke=None)
    )

    with chart_col2:

        with st.container(border=True):

            st.markdown(
                """
                ### Residential Construction

                Annual housing units permitted per 1,000 residents
                """
            )

            st.altair_chart(
                permits_chart,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # MARKET INTERPRETATION
    # --------------------------------------------------------

    fundamentals_score = city_result[
        "Long_Term_Fundamentals_Score"
    ]

    momentum_score = city_result[
        "Current_Market_Momentum_Score"
    ]

    fundamentals_rank = int(
        city_result["Fundamentals_Rank"]
    )

    momentum_rank = int(
        city_result["Momentum_Rank"]
    )

    top_three_probability = city_result["Pct_Top_3"]

    average_rank = city_result["Average_Rank"]

    # Create a data-driven interpretation sentence.
    if fundamentals_score >= 50:
        fundamentals_description = (
            "relatively strong long-term fundamentals"
        )
    else:
        fundamentals_description = (
            "more moderate long-term fundamentals"
        )

    if momentum_score >= 50:
        momentum_description = (
            "positive current-market momentum"
        )
    else:
        momentum_description = (
            "weaker current-market momentum"
        )

    market_summary = (
        f"{selected_city} combines "
        f"{fundamentals_description} with "
        f"{momentum_description}. "
        f"The market is classified as "
        f"{city_result['Current_Market_Regime'].lower()} "
        f"and has a {top_three_probability:.2f}% probability "
        f"of ranking in the Top 3 across alternative "
        f"investor-weighting scenarios."
    )

    summary_html = compact_html(
        f"""
        <div class="market-summary-card">
            <div class="market-summary-title">
                {selected_city} Market Interpretation
            </div>

            <div class="market-summary-text">
                {market_summary}
            </div>

            <div class="market-summary-metrics">
                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Fundamentals
                    </div>
                    <div class="market-summary-value">
                        {fundamentals_score:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Fundamentals Rank
                    </div>
                    <div class="market-summary-value">
                        #{fundamentals_rank}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Momentum
                    </div>
                    <div class="market-summary-value">
                        {momentum_score:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Momentum Rank
                    </div>
                    <div class="market-summary-value">
                        #{momentum_rank}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Top-3 Probability
                    </div>
                    <div class="market-summary-value">
                        {top_three_probability:.2f}%
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Average Rank
                    </div>
                    <div class="market-summary-value">
                        {average_rank:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Market Regime
                    </div>
                    <div class="market-summary-value"
                         style="font-size: 0.78rem;">
                        {city_result['Current_Market_Regime']}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Robustness
                    </div>
                    <div class="market-summary-value"
                         style="font-size: 0.78rem;">
                        {city_result['Robustness_Profile']}
                    </div>
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        summary_html,
        unsafe_allow_html=True,
    )

# FUNDAMENTALS VS. MOMENTUM

with tab3:

    # --------------------------------------------------------
    # SECTION HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <h2 class="section-heading">
            Fundamentals vs. Momentum
        </h2>
        <div class="section-subtitle">
            Comparing long-term market growth with current
            housing-market conditions across nine North Dallas markets
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SUMMARY RESULTS
    # --------------------------------------------------------

    fundamentals_leader = (
        scores.loc[
            scores[
                "Long_Term_Fundamentals_Score"
            ].idxmax()
        ]
    )

    momentum_leader = (
        scores.loc[
            scores[
                "Current_Market_Momentum_Score"
            ].idxmax()
        ]
    )

    balanced_leader = (
        scores.loc[
            scores["Balanced_Score"].idxmax()
        ]
    )

    robust_leader = (
        decision.loc[
            decision["Pct_Top_3"].idxmax()
        ]
    )

    positioning_kpis = [
        kpi_card(
            "Fundamentals Leader",
            fundamentals_leader["City"],
            (
                "Score "
                f"{fundamentals_leader['Long_Term_Fundamentals_Score']:.2f}"
                " · Rank #"
                f"{int(fundamentals_leader['Fundamentals_Rank'])}"
            ),
        ),
        kpi_card(
            "Momentum Leader",
            momentum_leader["City"],
            (
                "Score "
                f"{momentum_leader['Current_Market_Momentum_Score']:.2f}"
                " · Rank #"
                f"{int(momentum_leader['Momentum_Rank'])}"
            ),
        ),
        kpi_card(
            "Balanced Leader",
            balanced_leader["City"],
            (
                "Balanced Score "
                f"{balanced_leader['Balanced_Score']:.2f}"
            ),
        ),
        kpi_card(
            "Most Robust",
            robust_leader["City"],
            (
                f"{robust_leader['Pct_Top_3']:.2f}% "
                "Top-3 Probability"
            ),
        ),
    ]

    positioning_kpi_html = compact_html(
        '<div class="kpi-grid">'
        + "".join(positioning_kpis)
        + "</div>"
    )

    st.markdown(
        positioning_kpi_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # QUADRANT SCATTERPLOT
    # --------------------------------------------------------

    quadrant_definitions = [
        {
            "x": 0,
            "x2": 50,
            "y": 50,
            "y2": 100,
            "color": "#E8F0F5",
        },
        {
            "x": 50,
            "x2": 100,
            "y": 50,
            "y2": 100,
            "color": "#E1F0E8",
        },
        {
            "x": 0,
            "x2": 50,
            "y": 0,
            "y2": 50,
            "color": "#F1F3F5",
        },
        {
            "x": 50,
            "x2": 100,
            "y": 0,
            "y2": 50,
            "color": "#F7EDDD",
        },
    ]

    quadrant_layers = []

    for quadrant in quadrant_definitions:

        quadrant_data = pd.DataFrame(
            [
                {
                    "x": quadrant["x"],
                    "x2": quadrant["x2"],
                    "y": quadrant["y"],
                    "y2": quadrant["y2"],
                }
            ]
        )

        quadrant_layer = (
            alt.Chart(quadrant_data)
            .mark_rect(
                color=quadrant["color"],
                opacity=0.65,
            )
            .encode(
                x=alt.X(
                    "x:Q",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                x2="x2:Q",
                y=alt.Y(
                    "y:Q",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                y2="y2:Q",
            )
        )

        quadrant_layers.append(quadrant_layer)

    market_points = (
        alt.Chart(scores)
        .mark_circle(
            size=180,
            opacity=0.9,
            stroke="#FFFFFF",
            strokeWidth=2,
        )
        .encode(
            x=alt.X(
                "Long_Term_Fundamentals_Score:Q",
                title="Long-Term Fundamentals Score",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    gridColor="#DDE4E9",
                    labelColor="#66737D",
                    titleColor="#53636E",
                ),
            ),
            y=alt.Y(
                "Current_Market_Momentum_Score:Q",
                title="Current Market Momentum Score",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    gridColor="#DDE4E9",
                    labelColor="#66737D",
                    titleColor="#53636E",
                ),
            ),
            color=alt.Color(
                "Market_Profile:N",
                title="Market profile",
                scale=alt.Scale(
                    domain=[
                        "Strong Fundamentals + Strong Momentum",
                        "Strong Fundamentals + Weak Momentum",
                        "Weaker Fundamentals + Strong Momentum",
                        "Weaker Fundamentals + Weak Momentum",
                    ],
                    range=[
                        "#3F7D68",
                        "#B88746",
                        "#5077A3",
                        "#84929C",
                    ],
                ),
                legend=alt.Legend(
                    orient="bottom",
                    direction="vertical",
                    labelLimit=400,
                    titleColor="#53636E",
                    labelColor="#66737D",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "City:N",
                    title="Market",
                ),
                alt.Tooltip(
                    "Long_Term_Fundamentals_Score:Q",
                    title="Fundamentals",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Fundamentals_Rank:Q",
                    title="Fundamentals rank",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Current_Market_Momentum_Score:Q",
                    title="Momentum",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Momentum_Rank:Q",
                    title="Momentum rank",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Market_Profile:N",
                    title="Profile",
                ),
            ],
        )
    )

    market_labels = (
        alt.Chart(scores)
        .mark_text(
            align="left",
            baseline="middle",
            dx=9,
            dy=-9,
            color="#293B48",
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            x=alt.X(
                "Long_Term_Fundamentals_Score:Q",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "Current_Market_Momentum_Score:Q",
                scale=alt.Scale(domain=[0, 100]),
            ),
            text="City:N",
        )
    )

    vertical_midpoint = (
        alt.Chart(
            pd.DataFrame({"midpoint": [50]})
        )
        .mark_rule(
            color="#8D9AA3",
            strokeDash=[6, 5],
            strokeWidth=1.2,
        )
        .encode(
            x="midpoint:Q",
        )
    )

    horizontal_midpoint = (
        alt.Chart(
            pd.DataFrame({"midpoint": [50]})
        )
        .mark_rule(
            color="#8D9AA3",
            strokeDash=[6, 5],
            strokeWidth=1.2,
        )
        .encode(
            y="midpoint:Q",
        )
    )

    positioning_chart = alt.layer(
        *quadrant_layers,
        vertical_midpoint,
        horizontal_midpoint,
        market_points,
        market_labels,
    ).properties(
        height=500
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):

        st.markdown(
            """
            ### Market Positioning

            Long-term fundamentals compared with current
            market momentum
            """
        )

        st.altair_chart(
            positioning_chart,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # QUADRANT GUIDE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            How to Read the Quadrants
        </h3>
        <div class="section-subtitle">
            What each combination suggests about a market
        </div>
        """,
        unsafe_allow_html=True,
    )

    quadrant_guide_html = compact_html(
        """
        <div class="quadrant-grid">
            <div class="quadrant-card">
                <div class="quadrant-card-title">
                    Strong Fundamentals + Strong Momentum
                </div>
                <div class="quadrant-card-location">
                    Upper right
                </div>
                <div class="quadrant-card-text">
                    Markets combining favorable long-term growth
                    characteristics with comparatively strong current 
                    housing-market conditions.
                </div>
            </div>

            <div class="quadrant-card">
                <div class="quadrant-card-title">
                    Weaker Fundamentals + Strong Momentum
                </div>
                <div class="quadrant-card-location">
                    Upper left
                </div>
                <div class="quadrant-card-text">
                    Markets showing present-day resilience or activity
                    despite more moderate long-term growth fundamentals.
                </div>
            </div>

            <div class="quadrant-card">
                <div class="quadrant-card-title">
                    Strong Fundamentals + Weak Momentum
                </div>
                <div class="quadrant-card-location">
                    Lower right
                </div>
                <div class="quadrant-card-text">
                    Markets with attractive long-term growth potential
                    but weaker current conditions or greater near-term
                    supply pressure.
                </div>
            </div>

            <div class="quadrant-card">
                <div class="quadrant-card-title">
                    Weaker Fundamentals + Weak Momentum
                </div>
                <div class="quadrant-card-location">
                    Lower left
                </div>
                <div class="quadrant-card-text">
                    Markets scoring below the model midpoint in both
                    long-term growth and current market conditions.
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        quadrant_guide_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="takeaway-card">
            <div class="takeaway-title">
                Model Takeaway
            </div>
            <div class="takeaway-text">
                No market leads across every dimension. Celina has
                the strongest long-term fundamentals but weak current
                momentum. Plano has the strongest current momentum,
                while Melissa provides the clearest balance between
                long-term growth and present market conditions.
                Richardson also remains a notable momentum-oriented
                contender.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CONSTRUCTION COMPARISON
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="margin: 0; font-size: 1.05rem;">
            Construction Activity Comparison
        </h3>
        <div class="section-subtitle">
            Latest housing units permitted per 1,000 residents
            across the nine markets
        </div>
        """,
        unsafe_allow_html=True,
    )

    construction_comparison = (
        market[
            [
                "City",
                "Latest_Permits_Per_1000",
                "Latest_Permits",
                "Latest_SF_Share_Pct",
            ]
        ]
        .copy()
        .sort_values(
            "Latest_Permits_Per_1000",
            ascending=False,
        )
    )

    construction_comparison["Permits_Label"] = (
        construction_comparison[
            "Latest_Permits_Per_1000"
        ].map(lambda value: f"{value:.1f}")
    )

    construction_order = construction_comparison[
        "City"
    ].tolist()

    construction_bars = (
        alt.Chart(construction_comparison)
        .mark_bar(
            color="#7392AA",
            cornerRadiusEnd=6,
            size=23,
        )
        .encode(
            y=alt.Y(
                "City:N",
                sort=construction_order,
                title=None,
                axis=alt.Axis(
                    labelColor="#53636E",
                    labelFontSize=12,
                    labelFontWeight=600,
                    ticks=False,
                    domain=False,
                ),
            ),
            x=alt.X(
                "Latest_Permits_Per_1000:Q",
                title="Permitted units per 1,000 residents",
                axis=alt.Axis(
                    gridColor="#E5EAEE",
                    labelColor="#66737D",
                    titleColor="#53636E",
                    domain=False,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "City:N",
                    title="Market",
                ),
                alt.Tooltip(
                    "Latest_Permits_Per_1000:Q",
                    title="Permits per 1,000",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Latest_Permits:Q",
                    title="Total units permitted",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Latest_SF_Share_Pct:Q",
                    title="Single-family share",
                    format=".2f",
                ),
            ],
        )
    )

    construction_labels = (
        alt.Chart(construction_comparison)
        .mark_text(
            align="left",
            baseline="middle",
            dx=6,
            color="#33404A",
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            y=alt.Y(
                "City:N",
                sort=construction_order,
            ),
            x="Latest_Permits_Per_1000:Q",
            text="Permits_Label:N",
        )
    )

    construction_chart = (
        construction_bars
        + construction_labels
    ).properties(
        height=340
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):

        st.altair_chart(
            construction_chart,
            use_container_width=True,
        )

        st.caption(
            "Building permits represent housing units authorized, "
            "not necessarily completed housing units."
        )

    # --------------------------------------------------------
    # MARKET POSITIONING TABLE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            Market Positioning Summary
        </h3>
        <div class="section-subtitle">
            Scores, ranks, and model-defined market profiles
        </div>
        """,
        unsafe_allow_html=True,
    )

    positioning_table = (
        scores[
            [
                "City",
                "Long_Term_Fundamentals_Score",
                "Fundamentals_Rank",
                "Current_Market_Momentum_Score",
                "Momentum_Rank",
                "Market_Profile",
            ]
        ]
        .copy()
        .sort_values(
            [
                "Fundamentals_Rank",
                "Momentum_Rank",
            ]
        )
    )

    positioning_table = positioning_table.rename(
        columns={
            "City": "Market",
            "Long_Term_Fundamentals_Score": "Fundamentals",
            "Fundamentals_Rank": "Fund. Rank",
            "Current_Market_Momentum_Score": "Momentum",
            "Momentum_Rank": "Mom. Rank",
            "Market_Profile": "Market Profile",
        }
    )

    positioning_table["Fundamentals"] = (
        positioning_table["Fundamentals"]
        .map(lambda value: f"{value:.2f}")
    )

    positioning_table["Momentum"] = (
        positioning_table["Momentum"]
        .map(lambda value: f"{value:.2f}")
    )

    positioning_table["Fund. Rank"] = (
        positioning_table["Fund. Rank"]
        .map(lambda value: f"#{int(value)}")
    )

    positioning_table["Mom. Rank"] = (
        positioning_table["Mom. Rank"]
        .map(lambda value: f"#{int(value)}")
    )

    positioning_table_html = positioning_table.to_html(
        index=False,
        border=0,
        classes="comparison-table",
        escape=True,
    )

    st.markdown(
        compact_html(
            f"""
            <div class="comparison-card">
                {positioning_table_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

# INVESTOR SCENARIOS TAB

with tab4:

    # --------------------------------------------------------
    # SECTION HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <h2 class="section-heading">
            Investor Scenarios
        </h2>
        <div class="section-subtitle">
            Compare how market rankings change when investors
            place different emphasis on long-term growth and
            current market momentum
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SCENARIO SELECTOR
    # --------------------------------------------------------

    scenario = st.radio(
        "Investor Priority",
        [
            "Growth-Oriented",
            "Balanced",
            "Momentum-Oriented",
        ],
        horizontal=True,
        key="investor_scenario",
    )

    score_map = {
        "Growth-Oriented": "Growth_Oriented_Score",
        "Balanced": "Balanced_Score",
        "Momentum-Oriented": "Momentum_Oriented_Score",
    }

    rank_map = {
        "Growth-Oriented": "Growth_Oriented_Rank",
        "Balanced": "Balanced_Rank",
        "Momentum-Oriented": "Momentum_Oriented_Rank",
    }

    scenario_settings = {
        "Growth-Oriented": {
            "fundamentals_weight": 70,
            "momentum_weight": 30,
            "description": (
                "Prioritizes long-term population and home-value "
                "growth while still considering current market "
                "conditions."
            ),
        },
        "Balanced": {
            "fundamentals_weight": 50,
            "momentum_weight": 50,
            "description": (
                "Gives equal importance to long-term market "
                "fundamentals and present-day housing-market momentum."
            ),
        },
        "Momentum-Oriented": {
            "fundamentals_weight": 30,
            "momentum_weight": 70,
            "description": (
                "Prioritizes current market resilience and activity "
                "while placing less emphasis on long-term expansion."
            ),
        },
    }

    selected_score = score_map[scenario]
    selected_rank = rank_map[scenario]
    selected_settings = scenario_settings[scenario]

    scenario_definition_html = compact_html(
        f"""
        <div class="scenario-definition">
            <div class="scenario-definition-title">
                {scenario} Strategy
            </div>

            <div class="scenario-definition-text">
                {selected_settings['description']}
            </div>

            <div class="scenario-weight-row">
                <div class="scenario-weight">
                    Fundamentals:
                    {selected_settings['fundamentals_weight']}%
                </div>

                <div class="scenario-weight">
                    Momentum:
                    {selected_settings['momentum_weight']}%
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        scenario_definition_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SCENARIO RESULTS
    # --------------------------------------------------------

    scenario_table = (
        scores[
            [
                "City",
                "Long_Term_Fundamentals_Score",
                "Current_Market_Momentum_Score",
                selected_score,
                selected_rank,
            ]
        ]
        .copy()
        .sort_values(
            selected_score,
            ascending=False,
        )
        .reset_index(drop=True)
    )

    scenario_table["Score_Label"] = (
        scenario_table[selected_score]
        .map(lambda value: f"{value:.2f}")
    )

    scenario_order = scenario_table["City"].tolist()

    top_three_markets = scenario_table.head(3)

    leader_cards = []

    for position, (_, row) in enumerate(
        top_three_markets.iterrows(),
        start=1,
    ):
        leader_cards.append(
            kpi_card(
                f"Scenario Rank #{position}",
                row["City"],
                f"{scenario} Score {row[selected_score]:.2f}",
            )
        )

    leader_grid_html = compact_html(
        '<div class="scenario-leader-grid">'
        + "".join(leader_cards)
        + "</div>"
    )

    st.markdown(
        leader_grid_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SCENARIO RANKING CHART
    # --------------------------------------------------------

    scenario_bars = (
        alt.Chart(scenario_table)
        .mark_bar(
            color="#5077A3",
            cornerRadiusEnd=7,
            size=24,
        )
        .encode(
            y=alt.Y(
                "City:N",
                sort=scenario_order,
                title=None,
                axis=alt.Axis(
                    labelColor="#53636E",
                    labelFontSize=12,
                    labelFontWeight=600,
                    ticks=False,
                    domain=False,
                ),
            ),
            x=alt.X(
                f"{selected_score}:Q",
                title=f"{scenario} score",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    gridColor="#E5EAEE",
                    labelColor="#66737D",
                    titleColor="#53636E",
                    domain=False,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "City:N",
                    title="Market",
                ),
                alt.Tooltip(
                    f"{selected_score}:Q",
                    title=f"{scenario} score",
                    format=".2f",
                ),
                alt.Tooltip(
                    f"{selected_rank}:Q",
                    title="Scenario rank",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Long_Term_Fundamentals_Score:Q",
                    title="Fundamentals",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Current_Market_Momentum_Score:Q",
                    title="Momentum",
                    format=".2f",
                ),
            ],
        )
    )

    scenario_labels = (
        alt.Chart(scenario_table)
        .mark_text(
            align="left",
            baseline="middle",
            dx=7,
            color="#33404A",
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            y=alt.Y(
                "City:N",
                sort=scenario_order,
            ),
            x=alt.X(
                f"{selected_score}:Q",
                scale=alt.Scale(domain=[0, 100]),
            ),
            text="Score_Label:N",
        )
    )

    scenario_chart = (
        scenario_bars
        + scenario_labels
    ).properties(
        height=350
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):

        st.markdown(
            f"""
            ### {scenario} Market Ranking

            Composite score based on the selected investor priorities
            """
        )

        st.altair_chart(
            scenario_chart,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # SCENARIO RANKING TABLE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            Scenario Ranking Details
        </h3>
        <div class="section-subtitle">
            Comparison of the component scores behind the
            selected scenario ranking
        </div>
        """,
        unsafe_allow_html=True,
    )

    scenario_display = scenario_table[
        [
            "City",
            "Long_Term_Fundamentals_Score",
            "Current_Market_Momentum_Score",
            selected_score,
            selected_rank,
        ]
    ].copy()

    scenario_display = scenario_display.rename(
        columns={
            "City": "Market",
            "Long_Term_Fundamentals_Score": "Fundamentals",
            "Current_Market_Momentum_Score": "Momentum",
            selected_score: "Scenario Score",
            selected_rank: "Scenario Rank",
        }
    )

    scenario_display["Fundamentals"] = (
        scenario_display["Fundamentals"]
        .map(lambda value: f"{value:.2f}")
    )

    scenario_display["Momentum"] = (
        scenario_display["Momentum"]
        .map(lambda value: f"{value:.2f}")
    )

    scenario_display["Scenario Score"] = (
        scenario_display["Scenario Score"]
        .map(lambda value: f"{value:.2f}")
    )

    scenario_display["Scenario Rank"] = (
        scenario_display["Scenario Rank"]
        .map(lambda value: f"#{int(value)}")
    )

    scenario_table_html = scenario_display.to_html(
        index=False,
        border=0,
        classes="comparison-table",
        escape=True,
    )

    st.markdown(
        compact_html(
            f"""
            <div class="comparison-card">
                {scenario_table_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # RANKING ROBUSTNESS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            Ranking Robustness
        </h3>
        <div class="section-subtitle">
            Probability of ranking in the Top 3 across
            10,000 alternative weighting scenarios
        </div>
        """,
        unsafe_allow_html=True,
    )

    robustness_plot = (
        robustness[
            [
                "City",
                "Pct_Rank_1",
                "Pct_Top_3",
                "Average_Rank",
                "Robustness_Profile",
            ]
        ]
        .copy()
        .sort_values(
            "Pct_Top_3",
            ascending=False,
        )
    )

    robustness_plot["Full_Scale"] = 100

    robustness_plot["Top_3_Label"] = (
        robustness_plot["Pct_Top_3"]
        .map(lambda value: f"{value:.2f}%")
    )

    robustness_order = robustness_plot["City"].tolist()

    robustness_base = (
        alt.Chart(robustness_plot)
        .encode(
            y=alt.Y(
                "City:N",
                sort=robustness_order,
                title=None,
                axis=alt.Axis(
                    labelColor="#53636E",
                    labelFontSize=12,
                    labelFontWeight=600,
                    ticks=False,
                    domain=False,
                ),
            )
        )
    )

    robustness_tracks = (
        robustness_base
        .mark_bar(
            color="#E6EDF2",
            cornerRadiusEnd=7,
            size=20,
        )
        .encode(
            x=alt.X(
                "Full_Scale:Q",
                title="Top-3 probability",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    values=[0, 25, 50, 75, 100],
                    labelExpr="datum.value + '%'",
                    gridColor="#E5EAEE",
                    labelColor="#66737D",
                    titleColor="#53636E",
                    domain=False,
                ),
            )
        )
    )

    robustness_bars = (
        robustness_base
        .mark_bar(
            color="#334E68",
            cornerRadiusEnd=7,
            size=20,
        )
        .encode(
            x=alt.X(
                "Pct_Top_3:Q",
                scale=alt.Scale(domain=[0, 100]),
            ),
            tooltip=[
                alt.Tooltip(
                    "City:N",
                    title="Market",
                ),
                alt.Tooltip(
                    "Pct_Rank_1:Q",
                    title="Rank #1 probability",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Pct_Top_3:Q",
                    title="Top-3 probability",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Average_Rank:Q",
                    title="Average rank",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Robustness_Profile:N",
                    title="Robustness profile",
                ),
            ],
        )
    )

    robustness_labels = (
        robustness_base
        .mark_text(
            align="left",
            baseline="middle",
            dx=7,
            color="#33404A",
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            x=alt.X(
                "Pct_Top_3:Q",
                scale=alt.Scale(domain=[0, 100]),
            ),
            text="Top_3_Label:N",
        )
    )

    robustness_chart = (
        robustness_tracks
        + robustness_bars
        + robustness_labels
    ).properties(
        height=350
    ).configure_view(
        stroke=None
    )

    with st.container(border=True):

        st.altair_chart(
            robustness_chart,
            use_container_width=True,
        )

    robustness_display = robustness_plot[
        [
            "City",
            "Pct_Rank_1",
            "Pct_Top_3",
            "Average_Rank",
            "Robustness_Profile",
        ]
    ].copy()

    robustness_display = robustness_display.rename(
        columns={
            "City": "Market",
            "Pct_Rank_1": "Rank #1 Prob.",
            "Pct_Top_3": "Top-3 Prob.",
            "Average_Rank": "Avg. Rank",
            "Robustness_Profile": "Robustness Profile",
        }
    )

    robustness_display["Rank #1 Prob."] = (
        robustness_display["Rank #1 Prob."]
        .map(lambda value: f"{value:.2f}%")
    )

    robustness_display["Top-3 Prob."] = (
        robustness_display["Top-3 Prob."]
        .map(lambda value: f"{value:.2f}%")
    )

    robustness_display["Avg. Rank"] = (
        robustness_display["Avg. Rank"]
        .map(lambda value: f"{value:.2f}")
    )

    robustness_table_html = robustness_display.to_html(
        index=False,
        border=0,
        classes="comparison-table",
        escape=True,
    )

    st.markdown(
        compact_html(
            f"""
            <div class="comparison-card">
                {robustness_table_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SCENARIO INTERPRETATION
    # --------------------------------------------------------

    first_market = top_three_markets.iloc[0]["City"]
    second_market = top_three_markets.iloc[1]["City"]
    third_market = top_three_markets.iloc[2]["City"]

    scenario_takeaway = (
        f"Under the {scenario.lower()} strategy, "
        f"{first_market} ranks first, followed by "
        f"{second_market} and {third_market}. "
        f"This ranking reflects a "
        f"{selected_settings['fundamentals_weight']}% weight on "
        f"long-term fundamentals and a "
        f"{selected_settings['momentum_weight']}% weight on "
        f"current market momentum. The robustness analysis should "
        f"be considered alongside this scenario because it shows "
        f"whether these results remain competitive when the model's "
        f"weights change."
    )

    st.markdown(
        compact_html(
            f"""
            <div class="takeaway-card">
                <div class="takeaway-title">
                    Scenario Interpretation
                </div>
                <div class="takeaway-text">
                    {scenario_takeaway}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

# METHODOLOGY TAB

with tab5:

    # --------------------------------------------------------
    # SECTION HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <h2 class="section-heading">
            Methodology
        </h2>
        <div class="section-subtitle">
            How the market-screening model combines long-term
            fundamentals, current momentum, and ranking robustness
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # FRAMEWORK OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        compact_html(
            """
            <div class="takeaway-card">
                <div class="takeaway-title">
                    Market-Screening Framework
                </div>
                <div class="takeaway-text">
                    The model evaluates each North Dallas market
                    using two primary dimensions: long-term
                    fundamentals and current market momentum.
                    Indicators are normalized to a common 0–100
                    scale, combined into investor scenarios, and
                    tested across 10,000 alternative weighting
                    scenarios.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # METHODOLOGY COMPONENTS
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="margin: 0; font-size: 1.05rem;">
            Scoring Framework
        </h3>
        <div class="section-subtitle">
            The inputs and processing steps used to compare markets
        </div>
        """,
        unsafe_allow_html=True,
    )

    methodology_cards_html = compact_html(
        """
        <div class="methodology-grid">

            <div class="methodology-card">
                <div class="methodology-card-number">1</div>

                <div class="methodology-card-title">
                    Long-Term Fundamentals
                </div>

                <div class="methodology-card-subtitle">
                    Measures the structural growth characteristics
                    of each housing market.
                </div>

                <ul class="methodology-list">
                    <li>Population CAGR</li>
                    <li>Five-year home-value CAGR</li>
                    <li>Population growth acceleration</li>
                </ul>
            </div>

            <div class="methodology-card">
                <div class="methodology-card-number">2</div>

                <div class="methodology-card-title">
                    Current Market Momentum
                </div>

                <div class="methodology-card-subtitle">
                    Measures current housing-market activity,
                    pricing, and supply conditions.
                </div>

                <ul class="methodology-list">
                    <li>ZHVI year-over-year growth</li>
                    <li>Home sales year-over-year growth</li>
                    <li>Sale-to-list ratio</li>
                    <li>Inventory growth</li>
                    <li>Months of supply</li>
                </ul>
            </div>

            <div class="methodology-card">
                <div class="methodology-card-number">3</div>

                <div class="methodology-card-title">
                    Score Normalization
                </div>

                <div class="methodology-card-subtitle">
                    Converts indicators measured in different units
                    into comparable model inputs.
                </div>

                <div class="methodology-note">
                    Indicators are normalized to a 0–100 scale.
                </div>

                <div class="methodology-note">
                    Variables where lower values indicate stronger
                    market conditions are reverse-scored.
                </div>
            </div>

            <div class="methodology-card">
                <div class="methodology-card-number">4</div>

                <div class="methodology-card-title">
                    Ranking Robustness
                </div>

                <div class="methodology-card-subtitle">
                    Evaluates how sensitive the market rankings are
                    to alternative investor priorities.
                </div>

                <div class="methodology-note">
                    The model evaluates 10,000 alternative weighting
                    scenarios.
                </div>

                <ul class="methodology-list">
                    <li>Probability of ranking #1</li>
                    <li>Probability of ranking in the Top 3</li>
                    <li>Average market rank</li>
                    <li>Composite-score dispersion</li>
                    <li>Sensitivity to investor priorities</li>
                </ul>
            </div>

        </div>
        """
    )

    st.markdown(
        methodology_cards_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # DATA SOURCES
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="margin: 0; font-size: 1.05rem;">
            Data Sources
        </h3>
        <div class="section-subtitle">
            Public housing-market, population, and construction
            datasets used in the analysis
        </div>
        """,
        unsafe_allow_html=True,
    )

    source_cards_html = compact_html(
        """
        <div class="source-grid">

            <div class="source-card">
                <div class="source-name">
                    Zillow Research
                </div>

                <div class="source-type">
                    Home Values
                </div>

                <ul class="source-list">
                    <li>
                        Zillow Home Value Index (ZHVI)
                    </li>
                </ul>
            </div>

            <div class="source-card">
                <div class="source-name">
                    Redfin Data Center
                </div>

                <div class="source-type">
                    Current Market Activity
                </div>

                <ul class="source-list">
                    <li>Sales activity</li>
                    <li>Pending sales</li>
                    <li>Inventory</li>
                    <li>New listings</li>
                    <li>Days on market</li>
                    <li>Months of supply</li>
                    <li>Sale-to-list ratio</li>
                </ul>
            </div>

            <div class="source-card">
                <div class="source-name">
                    U.S. Census Bureau
                </div>

                <div class="source-type">
                    Demographics and Construction
                </div>

                <ul class="source-list">
                    <li>
                        Population Estimates Program
                    </li>
                    <li>
                        Building Permits Survey
                    </li>
                </ul>
            </div>

        </div>
        """
    )

    st.markdown(
        source_cards_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="margin: 0; font-size: 1.05rem;">
            Limitations
        </h3>
        <div class="section-subtitle">
            Important considerations when interpreting the results
        </div>
        """,
        unsafe_allow_html=True,
    )

    limitations_html = compact_html(
        """
        <div class="limitations-card">
            <ul class="limitations-list">
                <li>
                    Market-level analysis does not capture
                    neighborhood-level differences.
                </li>

                <li>
                    Building permits represent authorized
                    construction, not completed units.
                </li>

                <li>
                    Recent housing-market indicators can
                    change quickly.
                </li>

                <li>
                    Composite rankings depend on the selected
                    investor priorities.
                </li>

                <li>
                    Historical appreciation does not guarantee
                    future returns.
                </li>

                <li>
                    The model is intended as a market-screening
                    framework rather than a forecast of
                    investment returns.
                </li>
            </ul>
        </div>
        """
    )

    st.markdown(
        limitations_html,
        unsafe_allow_html=True,
    )

    disclaimer_html = compact_html(
        """
        <div class="methodology-disclaimer">
            <div class="methodology-disclaimer-title">
                Interpretation Notice
            </div>

            <div class="methodology-disclaimer-text">
                The model is intended as a market-screening
                framework rather than a forecast of investment
                returns. Historical appreciation does not
                guarantee future returns.
            </div>
        </div>
        """
    )

    st.markdown(
        disclaimer_html,
        unsafe_allow_html=True,
    )