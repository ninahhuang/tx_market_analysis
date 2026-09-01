# Texas Housing Market Analysis

A data-driven analysis of housing market conditions across eight North Dallas, TX cities, combining home values, demographic growth, residential construction, and current market activity to evaluate long-term fundamentals and near-term market momentum.

## Project Overview

North Dallas has experienced significant population growth, housing development, and home-price appreciation over the past several years. However, rapidly growing cities do not necessarily have the strongest current housing-market conditions.

This project evaluates eight North Dallas markets:

- Anna
- Celina
- Frisco
- McKinney
- Melissa
- Plano
- Princeton
- Prosper

The analysis separates each market into two dimensions:

1. **Long-Term Growth Fundamentals** — demographic growth, historical appreciation, and population-growth trends.
2. **Current Market Momentum** — recent price performance, transaction activity, inventory conditions, and market balance.

The goal is not simply to identify the fastest-growing city, but to understand the tradeoff between **long-term growth potential and current market conditions**.

---

## Key Questions

The analysis addresses several investment-oriented questions:

- Which North Dallas markets have the strongest long-term growth fundamentals?
- Which markets currently show the strongest housing-market momentum?
- Where are population growth and residential construction expanding most rapidly?
- Which markets are experiencing price corrections despite strong demographic growth?
- How sensitive are market rankings to different investor priorities?
- Which markets remain attractive across a wide range of weighting assumptions?

---

## Data Sources

The project combines data from several housing and demographic sources.

### Zillow Home Value Index (ZHVI)

Used to analyze:

- Historical home values
- Five-year appreciation
- Three-year appreciation
- Year-over-year price changes
- Declines from previous market peaks

Source: Zillow Research

### Redfin Housing Market Data

Used to measure current housing-market activity, including:

- Homes sold
- Pending sales
- Inventory
- New listings
- Months of supply
- Median days on market
- Sale-to-list price ratio

The Redfin dataset uses rolling three-month observations, so transaction counts are used for momentum comparisons rather than summed into annual totals.

Source: Redfin Data Center

### U.S. Census Population Estimates Program

Annual city population estimates are used to measure:

- Population growth
- Population CAGR
- Recent population growth
- Growth acceleration/deceleration

Source: U.S. Census Bureau Population Estimates Program, Vintage 2025

### U.S. Census Building Permits Survey

Residential building permit data is used to evaluate:

- Total permitted housing units
- Construction intensity
- Permits per 1,000 residents
- Single-family share of new construction
- Changes from peak construction activity

Source: U.S. Census Bureau Building Permits Survey

---

## Project Structure

```text
tx_market_analysis/
│
├── data/
│   ├── raw/                  # Original source datasets (excluded from Git)
│   └── processed/            # Cleaned and model-ready datasets
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_market_eda.ipynb
│   └── 03_market_momentum_model.ipynb
│
├── dashboard/                # Dashboard development
├── src/                      # Reusable project code
├── requirements.txt
├── .gitignore
└── README.md
```

Raw source datasets are excluded from the repository. Processed analytical datasets are included to make the results easier to reproduce.

---

## Analysis Workflow

### 1. Data Collection and Cleaning

`01_data_collection.ipynb`

The first notebook prepares the Zillow housing-price dataset by:

- Filtering for the eight target cities
- Restricting the analysis period
- Converting Zillow's wide-format data into a city-month panel
- Creating standardized date variables
- Validating missing values and duplicate observations

The resulting dataset contains monthly ZHVI observations for all eight markets.

### 2. Exploratory Data Analysis

`02_market_eda.ipynb`

The second notebook combines housing, demographic, construction, and market-activity data.

Major analyses include:

- Historical home-price trends
- Five-year and three-year appreciation
- Current price corrections
- Population growth
- Residential construction intensity
- Construction relative to population growth
- Inventory and months of supply
- Transaction and pending-sales momentum
- Days on market
- Sale-to-list ratios

These datasets are combined into a city-level master dataset used by the scoring model.

### 3. Market Scoring and Robustness Analysis

`03_market_momentum_model.ipynb`

The final notebook develops two separate market scores.

#### Long-Term Fundamentals Score

Built from:

- Population CAGR
- Five-year home-price CAGR
- Population growth acceleration

#### Current Market Momentum Score

Built from:

- ZHVI year-over-year growth
- Homes-sold year-over-year growth
- Sale-to-list ratio
- Inventory growth
- Months of supply

Metrics are normalized to a 0–100 scale. Variables where lower values represent stronger conditions, such as months of supply, are reverse-scored.

---

## Scenario Analysis

Because different investors may prioritize different characteristics, the project evaluates multiple weighting strategies:

- **Growth-Oriented** — greater emphasis on long-term fundamentals
- **Balanced** — similar emphasis on fundamentals and current momentum
- **Momentum-Oriented** — greater emphasis on current market conditions

This prevents the analysis from relying on a single arbitrary definition of the "best" housing market.

---

## Monte Carlo Ranking Robustness

To test how dependent the rankings are on subjective weighting choices, the model runs **10,000 alternative weighting scenarios**.

For each city, the simulation evaluates:

- Probability of ranking #1
- Probability of ranking in the Top 3
- Average rank
- Median rank
- Best and worst observed rank
- Distribution of composite scores

This distinguishes markets that perform consistently across different investor preferences from markets whose attractiveness depends heavily on the chosen assumptions.

---

## Current Market Regimes

The analysis also classifies each city according to current supply-and-demand conditions.

Examples include:

- **Relatively Stable**
- **Recovery / Repricing**
- **Demand Growth + Supply Pressure**
- **Mixed / Transitional**

These classifications combine indicators such as:

- Price changes
- Homes sold
- Pending sales
- Inventory growth
- Months of supply
- Days on market

This helps explain *why* a city receives its current momentum score.

---

## Key Findings

### Plano — Strongest Current Position

Plano ranks first in current market momentum and performs extremely well across alternative weighting assumptions.

Despite slower demographic growth than the outer North Dallas suburbs, its relatively stable housing conditions make it one of the most robust markets in the analysis.

### Melissa — Strongest Balance

Melissa combines strong long-term fundamentals with comparatively strong current momentum.

It performs consistently across growth-oriented, balanced, and momentum-oriented scenarios, making it one of the most robust markets in the model.

### Celina — Strongest Long-Term Growth Thesis

Celina has the strongest long-term fundamentals in the analysis, driven by exceptional population growth.

However, rapid residential construction and rising supply coincide with weaker current price momentum. Celina therefore represents a strong long-term growth market with a meaningful short-term supply-demand imbalance.

### Princeton — Recovery / Repricing Opportunity

Princeton has experienced one of the largest price corrections in the group while simultaneously showing strong transaction and pending-sales growth.

This combination makes Princeton an interesting recovery or contrarian market, although its overall ranking remains more sensitive to investor assumptions.

---

## Selected Results

| City | Fundamentals Rank | Momentum Rank | Top-3 Probability | Robustness |
|---|---:|---:|---:|---|
| Plano | 6 | 1 | 89.0% | Highly Robust |
| Melissa | 2 | 3 | 81.1% | Highly Robust |
| Celina | 1 | 8 | 48.7% | Moderately Robust |
| McKinney | 7 | 2 | 30.4% | Weight Sensitive |
| Frisco | 4 | 5 | 25.3% | Weight Sensitive |
| Princeton | 8 | 4 | 19.9% | Weight Sensitive |
| Prosper | 3 | 7 | 4.9% | Consistently Lower Ranked |
| Anna | 5 | 6 | 0.9% | Consistently Lower Ranked |

---

## Main Takeaway

The analysis shows that **long-term growth and current housing-market strength are not the same thing**.

Fast-growing markets such as Celina can have exceptional demographic fundamentals while simultaneously experiencing supply pressure and falling home prices. More mature markets such as Plano can have slower population growth while maintaining stronger current market conditions.

Rather than identifying one universally "best" market, the model highlights different investment profiles:

- **Plano:** strongest current and most robust opportunity
- **Melissa:** strongest overall balance
- **Celina:** strongest long-term growth thesis
- **Princeton:** potential recovery/repricing opportunity

The preferred market therefore depends on an investor's time horizon, risk tolerance, and emphasis on current conditions versus future growth.

---

## Technologies

- Python
- pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- Git / GitHub

---

## Repository Outputs

Processed datasets include:

- Housing price history
- Population estimates
- Building permit activity
- Redfin market activity
- Market-level master dataset
- Market diagnostics
- Composite market scores
- Monte Carlo ranking robustness
- Final investment decision table

These files are stored in:

```text
data/processed/
```

---

## Limitations

This analysis should be interpreted as a market-screening framework rather than a prediction of future investment returns.

Important limitations include:

- Only eight cities are included in the comparison.
- Market indicators can be highly correlated.
- Recent housing conditions can change quickly.
- Building permits represent authorized construction rather than guaranteed completions.
- City-level trends may not reflect individual neighborhoods or properties.
- The scoring system necessarily depends on assumptions about investor priorities.
- Historical appreciation does not guarantee future appreciation.

The Monte Carlo sensitivity analysis helps reduce dependence on any single weighting scheme but does not eliminate these limitations.

---

## Future Development

Potential extensions include:

- Interactive Streamlit dashboard
- Neighborhood or ZIP-code-level analysis
- Rental yield and cash-flow modeling
- Mortgage-rate sensitivity
- Property-tax and insurance modeling
- Employment and income growth
- School-district indicators
- New-home inventory
- Housing affordability metrics
- Forward-looking investment scenarios

---

## Author

**Nina Huang**

North Dallas Housing Market Analysis  
2026