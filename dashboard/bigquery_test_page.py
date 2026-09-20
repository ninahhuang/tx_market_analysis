import streamlit as st
import altair as alt

from bigquery_data import (
    load_building_permits,
    load_home_values,
    load_markets,
    load_population,
)

st.set_page_config(
    page_title="BigQuery Connection Test",
    layout="wide",
)

st.title("BigQuery Market Data Test")

markets = load_markets().copy()
markets["label"] = markets["city"] + ", " + markets["state_code"]

label_to_id = dict(zip(markets["label"], markets["market_id"]))

selection_mode = st.radio(
    "Choose how to view markets",
    [
        "One market",
        "Compare selected markets",
        "All available markets",
    ],
    horizontal=True,
)

if selection_mode == "One market":
    selected_labels = [
        st.selectbox(
            "Select a market",
            options=markets["label"].tolist(),
        )
    ]

elif selection_mode == "Compare selected markets":
    selected_labels = st.multiselect(
        "Select up to 10 markets",
        options=markets["label"].tolist(),
        default=markets["label"].tolist()[:2],
        max_selections=10,
    )

else:
    if len(markets) > 10:
        st.error(
            "More than 10 markets are available. "
            "Use Compare selected markets and choose up to 10."
        )
        st.stop()

    selected_labels = markets["label"].tolist()

if not selected_labels:
    st.info("Select at least one market.")
    st.stop()

selected_market_ids = [
    label_to_id[label]
    for label in selected_labels
]

st.success(
    f"{len(selected_market_ids)} market(s) selected: "
    + ", ".join(selected_labels)
)

home_values = load_home_values(selected_market_ids)
population = load_population(selected_market_ids)
building_permits = load_building_permits(selected_market_ids)

LIGHT_COLORS = [
    "#9CC2FF",
    "#FFB38A",
    "#FF8F91",
    "#8ED8CF",
    "#A8D97B",
    "#FFE07A",
    "#D8A7CE",
    "#FFB3C7",
    "#C6A57A",
    "#B9AEFF",
]

color_encoding = alt.Color(
    "market:N",
    title="Market",
    scale=alt.Scale(range=LIGHT_COLORS),
)


st.subheader("Home Value Trends")

if home_values.empty:
    st.info("No home-value records are available for this selection.")
else:
    home_value_chart = (
        alt.Chart(home_values)
        .mark_line(
            point=True,
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "observation_date:T",
                title="Date",
            ),
            y=alt.Y(
                "home_value:Q",
                title="Typical home value",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(format="$,.0f"),
            ),
            color=color_encoding,
            tooltip=[
                alt.Tooltip("market:N", title="Market"),
                alt.Tooltip(
                    "observation_date:T",
                    title="Date",
                    format="%B %Y",
                ),
                alt.Tooltip(
                    "home_value:Q",
                    title="Home value",
                    format="$,.0f",
                ),
            ],
        )
        .properties(height=420)
        .interactive()
    )

    st.altair_chart(
        home_value_chart,
        use_container_width=True,
    )


st.subheader("Population Growth")

if population.empty:
    st.info("No population records are available for this selection.")
else:
    population_chart = (
        alt.Chart(population)
        .mark_line(
            point=True,
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "year:O",
                title="Year",
            ),
            y=alt.Y(
                "population:Q",
                title="Population",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(format=","),
            ),
            color=color_encoding,
            tooltip=[
                alt.Tooltip("market:N", title="Market"),
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip(
                    "population:Q",
                    title="Population",
                    format=",",
                ),
            ],
        )
        .properties(height=420)
        .interactive()
    )

    st.altair_chart(
        population_chart,
        use_container_width=True,
    )


st.subheader("Residential Construction")

if building_permits.empty:
    st.info("No building-permit records are available for this selection.")
else:
    permit_chart = (
        alt.Chart(building_permits)
        .mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        )
        .encode(
            x=alt.X(
                "year:O",
                title="Year",
            ),
            xOffset=alt.XOffset(
                "market:N",
                title="Market",
            ),
            y=alt.Y(
                "units_per_1000_residents:Q",
                title="Permitted units per 1,000 residents",
                scale=alt.Scale(zero=True),
                axis=alt.Axis(format=".1f"),
            ),
            color=color_encoding,
            tooltip=[
                alt.Tooltip("market:N", title="Market"),
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip(
                    "total_units:Q",
                    title="Total permitted units",
                    format=",",
                ),
                alt.Tooltip(
                    "population:Q",
                    title="Population",
                    format=",",
                ),
                alt.Tooltip(
                    "units_per_1000_residents:Q",
                    title="Units per 1,000",
                    format=".2f",
                ),
            ],
        )
        .properties(height=420)
    )

    st.altair_chart(
        permit_chart,
        use_container_width=True,
    )


with st.expander("View underlying BigQuery records"):
    st.markdown("#### Home values")
    st.dataframe(home_values, use_container_width=True)

    st.markdown("#### Population")
    st.dataframe(population, use_container_width=True)

    st.markdown("#### Residential construction")
    st.dataframe(building_permits, use_container_width=True)