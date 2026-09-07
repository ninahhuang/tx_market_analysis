# North Dallas Housing Market Analysis

An interactive housing-market screening dashboard comparing long-term growth fundamentals, current market momentum, construction activity, and ranking robustness across nine North Dallas markets.

The project combines data from Zillow Research, the Redfin Data Center, and the U.S. Census Bureau to examine how market attractiveness changes with different investor priorities.

## Markets Analyzed

- Anna
- Celina
- Frisco
- McKinney
- Melissa
- Plano
- Princeton
- Prosper
- Richardson

## Project Overview

Rapid population growth or historical appreciation does not necessarily indicate strong current housing-market conditions. A fast-growing market may also experience rising inventory, increased construction, longer selling times, or weaker near-term price momentum.

This project separates market performance into two primary dimensions:

1. **Long-Term Fundamentals** — demographic growth, historical home-value appreciation, and population-growth trends.
2. **Current Market Momentum** — recent pricing, transaction activity, inventory, supply, and market-balance conditions.

The analysis then evaluates how rankings change under different investor strategies and tests whether the results remain stable across 10,000 alternative weighting scenarios.

## Key Questions

The project addresses the following questions:

- Which North Dallas markets have the strongest long-term growth fundamentals?
- Which markets currently demonstrate the strongest housing-market momentum?
- Where are population and residential construction expanding most rapidly?
- Which markets are experiencing supply pressure or price corrections?
- How do rankings change under different investor priorities?
- Which markets remain competitive when model assumptions change?
- Which markets offer the strongest balance between long-term growth and current conditions?

## Interactive Dashboard

The Streamlit application contains five tabs.

### Executive Overview

Provides a summary of the model’s primary findings through:

- Headline market KPI cards
- Top-3 ranking-probability chart
- Final market comparison table
- Model takeaway
- Market interpretation cards

### Market Explorer

Allows the user to select an individual city and explore:

- Five-year home-value CAGR
- Population CAGR
- Home-sales year-over-year change
- Months of supply
- Historical home-value trends
- Annual population growth
- Residential construction activity
- Market regime
- Ranking robustness
- Data-driven market interpretation

### Fundamentals vs. Momentum

Compares all nine cities on the model’s two primary dimensions through:

- Fundamentals and momentum leaders
- Quadrant scatterplot
- Market-profile explanations
- Construction activity comparison
- Market-positioning summary table
- Model interpretation

### Investor Scenarios

Shows how rankings change under three investor strategies:

- Growth-Oriented
- Balanced
- Momentum-Oriented

The tab also includes:

- Strategy definitions and weights
- Top-three markets for the selected strategy
- Scenario ranking chart
- Detailed score table
- Ranking-robustness chart
- Monte Carlo robustness results

### Methodology

Documents:

- Long-term fundamentals
- Current market momentum
- Score normalization
- Reverse-scoring
- Investor-scenario weights
- Ranking-robustness testing
- Data sources
- Model limitations

## Data Sources

### Zillow Research

The Zillow Home Value Index is used to analyze:

- Historical home values
- Five-year appreciation
- Three-year appreciation
- Year-over-year price changes
- Declines from previous market peaks

Source: **Zillow Research — Zillow Home Value Index**

### Redfin Data Center

Redfin housing-market data is used to measure:

- Homes sold
- Pending sales
- Inventory
- New listings
- Median days on market
- Months of supply
- Sale-to-list ratio

The Redfin dataset uses rolling three-month observations. Transaction measures are therefore used for market-momentum comparisons rather than summed into annual totals.

Source: **Redfin Data Center**

### U.S. Census Bureau Population Estimates Program

Annual city population estimates are used to measure:

- Total population growth
- Population CAGR
- Recent population growth
- Population-growth acceleration or deceleration

Source: **U.S. Census Bureau Population Estimates Program**

### U.S. Census Bureau Building Permits Survey

Residential building-permit data is used to evaluate:

- Total permitted housing units
- Permits per 1,000 residents
- Single-family and multifamily units
- Single-family share of permitted construction
- Construction intensity
- Changes from peak construction activity

Building permits represent housing units authorized, not necessarily completed housing units.

Source: **U.S. Census Bureau Building Permits Survey**

## Analysis Workflow

### 1. Data Cleaning

[`notebooks/01_data_cleaning.ipynb`](notebooks/01_data_cleaning.ipynb)

The first notebook prepares the source datasets by:

- Filtering for the nine target cities
- Restricting the analysis period
- Reshaping housing data into a city-month panel
- Standardizing dates and market names
- Checking missing values and duplicate observations
- Producing cleaned analytical datasets

### 2. Exploratory Data Analysis

[`notebooks/02_market_eda.ipynb`](notebooks/02_market_eda.ipynb)

The second notebook analyzes and combines:

- Historical home-value trends
- Five-year and three-year appreciation
- Current home-value changes
- Population growth
- Residential construction intensity
- Construction relative to population
- Inventory and months of supply
- Sales and pending-sales momentum
- Days on market
- Sale-to-list ratios

These measures are combined into a city-level master dataset.

### 3. Market Scoring and Robustness

[`notebooks/03_market_momentum_model.ipynb`](notebooks/03_market_momentum_model.ipynb)

The third notebook creates the market scores, investor scenarios, ranking-robustness simulation, and final decision table.

The Streamlit dashboard reads the processed outputs from this workflow and does not recalculate the underlying model.

## Scoring Framework

### Long-Term Fundamentals Score

The long-term fundamentals score combines:

- Population CAGR
- Five-year home-value CAGR
- Population-growth acceleration

### Current Market Momentum Score

The current market momentum score incorporates:

- ZHVI year-over-year growth
- Homes-sold year-over-year growth
- Sale-to-list ratio
- Inventory growth
- Months of supply

Indicators are normalized to a common 0–100 scale.

Variables where lower values indicate stronger market conditions, including inventory growth and months of supply, are reverse-scored before being included in the model.

## Investor Scenarios

Three scenarios show how the results change with different investment priorities.

| Scenario | Fundamentals Weight | Momentum Weight | Primary Emphasis |
|---|---:|---:|---|
| Growth-Oriented | 70% | 30% | Long-term demographic and appreciation potential |
| Balanced | 50% | 50% | Equal emphasis on long-term and current conditions |
| Momentum-Oriented | 30% | 70% | Current activity, pricing, and market resilience |

The scenario analysis avoids relying on one universal definition of the “best” housing market.

## Monte Carlo Ranking Robustness

The model evaluates **10,000 alternative weighting scenarios** to measure how sensitive each market’s position is to changes in investor priorities.

For each city, the simulation calculates:

- Probability of ranking first
- Probability of ranking in the Top 3
- Average rank
- Median rank
- Best observed rank
- Worst observed rank
- Composite-score distribution
- Composite-score dispersion
- Sensitivity to investor priorities

This distinguishes consistently competitive markets from markets whose rankings depend heavily on a particular weighting assumption.

## Current Market Regimes

The model also classifies each city according to its current supply-and-demand conditions.

The classifications include:

- **Relatively Stable**
- **Recovery / Repricing**
- **Demand Growth / Supply Pressure**
- **Mixed / Transitional**

These regimes provide context for the momentum scores by combining indicators such as:

- Home-value changes
- Homes sold
- Pending sales
- Inventory growth
- Months of supply
- Days on market
- Sale-to-list ratio

## Selected Results

| Market | Fundamentals | Fundamentals Rank | Momentum | Momentum Rank | Top-3 Probability | Average Rank | Robustness |
|---|---:|---:|---:|---:|---:|---:|---|
| Plano | 42.94 | 6 | 75.61 | 1 | 81.62% | 2.31 | Highly Robust |
| Melissa | 62.50 | 2 | 54.61 | 5 | 74.69% | 2.84 | Moderately Robust |
| Richardson | 47.27 | 5 | 64.32 | 2 | 58.72% | 3.44 | Moderately Robust |
| Celina | 91.02 | 1 | 21.50 | 9 | 42.94% | 4.25 | Moderately Robust |
| Princeton | 31.07 | 9 | 58.98 | 3 | 19.88% | 6.58 | Weight Sensitive |
| Frisco | 48.93 | 4 | 47.92 | 6 | 11.93% | 5.66 | Consistently Lower Ranked |
| McKinney | 41.72 | 8 | 57.07 | 4 | 8.52% | 5.16 | Consistently Lower Ranked |
| Prosper | 57.26 | 3 | 31.46 | 8 | 1.14% | 7.21 | Consistently Lower Ranked |
| Anna | 42.75 | 7 | 36.01 | 7 | 0.56% | 7.56 | Consistently Lower Ranked |

## Key Findings

### Plano — Current Resilience Leader

Plano has the strongest current market-momentum score and the highest Top-3 ranking probability.

Its long-term fundamentals are more moderate than those of rapidly expanding outer suburbs, but its current housing-market conditions are comparatively resilient.

### Melissa — Balanced Growth Candidate

Melissa combines relatively strong long-term fundamentals with solid current momentum.

Its performance across investor scenarios makes it one of the most balanced markets in the analysis.

### Richardson — Momentum-Oriented Contender

Richardson ranks second in current market momentum and has a 58.72% probability of ranking in the Top 3.

Its relatively stable current market regime makes it a credible alternative for investors prioritizing present-day resilience.

### Celina — Long-Term Growth Leader

Celina ranks first in long-term fundamentals, supported by exceptional population growth and historical home-value appreciation.

However, weaker current momentum and substantial construction activity create a more supply-sensitive near-term investment profile.

### Princeton — Recovery / Repricing Profile

Princeton combines comparatively strong transaction momentum with a weaker long-term fundamentals score and recent price correction.

Its ranking is more sensitive to investor assumptions, but its current profile may be relevant to recovery-oriented or contrarian analysis.

## Main Takeaway

Long-term growth and current housing-market strength are not the same.

Rapidly growing cities can have exceptional demographic fundamentals while simultaneously experiencing high construction activity, rising supply, and weaker current price momentum. More mature markets can have slower population growth but stronger present-day housing conditions.

The model therefore does not identify one universally superior market. Instead, it highlights several investment profiles:

- **Plano:** strongest current momentum and ranking robustness
- **Melissa:** strongest overall balance
- **Richardson:** strong momentum-oriented alternative
- **Celina:** strongest long-term growth thesis
- **Princeton:** recovery or repricing profile

The preferred market depends on the investor’s time horizon, risk tolerance, and emphasis on current conditions versus future growth.

## Project Structure

```text
tx_market_analysis/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
│       ├── dallas_building_permits_annual.csv
│       ├── dallas_construction_summary.csv
│       ├── dallas_final_decision_table.csv
│       ├── dallas_market_diagnostics.csv
│       ├── dallas_market_master.csv
│       ├── dallas_market_scores.csv
│       ├── dallas_market_snapshot.csv
│       ├── dallas_population_annual.csv
│       ├── dallas_population_summary.csv
│       ├── dallas_ranking_robustness.csv
│       ├── dallas_redfin_market_activity.csv
│       └── dallas_zhvi_monthly.csv
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_market_eda.ipynb
│   └── 03_market_momentum_model.ipynb
├── src/
├── .gitignore
├── README.md
└── requirements.txt
```

Raw source datasets are excluded from Git. Processed analytical outputs are included so the dashboard can run without rerunning the notebooks.

## Running the Dashboard Locally

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd tx_market_analysis
```

Replace `YOUR_REPOSITORY_URL` with the repository’s GitHub URL.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Streamlit application

```bash
streamlit run dashboard/app.py
```

Streamlit will display a local URL, typically:

```text
http://localhost:8501
```

Open that address in a browser if it does not open automatically.

## Technologies

- Python
- pandas
- NumPy
- Altair
- Matplotlib
- Streamlit
- Jupyter Notebook
- Git and GitHub

## Limitations

- Market-level analysis does not capture neighborhood-level differences.
- Building permits represent authorized construction, not completed units.
- Recent housing-market indicators can change quickly.
- Composite rankings depend on the selected investor priorities.
- Historical appreciation does not guarantee future returns.
- The model is intended as a market-screening framework rather than a forecast of investment returns.

## Disclaimer

This project is an analytical market-screening tool and is not financial, investment, legal, or real-estate advice. The results should be combined with current market research and property-level due diligence before making an investment decision.