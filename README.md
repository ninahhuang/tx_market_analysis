# Market Match: Housing Market Investment Screening

An interactive Streamlit dashboard for comparing housing markets based on long-term growth, current market conditions, and ranking stability.

The dashboard began as a comparison of nine North Dallas cities and now also allows users to upload data for other U.S. cities. It validates and standardizes the source files, calculates market scores, tests ranking stability, and presents the results through an investor-friendly dashboard and downloadable report.

## Live Dashboard

[Open the deployed Streamlit dashboard](https://tx-market-analysis.streamlit.app/)

> The complete national Redfin file can exceed the memory available on Streamlit Community Cloud. See [Deployment and large-file considerations](#deployment-and-large-file-considerations) before uploading very large files.

## Project Purpose

A market with rapid population growth or strong historical appreciation does not necessarily have strong current housing conditions. Fast-growing markets may also face:

- Rising housing inventory
- Elevated construction activity
- Longer selling times
- Slowing transaction activity
- Weaker near-term price momentum

At the same time, more mature markets may have slower demographic growth but stronger current demand, greater pricing stability, or more consistent rankings.

This project separates those considerations into three decision areas:

1. **Long-term fundamentals** — population growth, historical appreciation, and demographic trends.
2. **Current market momentum** — pricing, sales activity, inventory, supply, and market balance.
3. **Ranking robustness** — how consistently a market performs when investor priorities change.

The result is a flexible market-screening tool rather than a single universal definition of the “best” market.

## Key Features

- Included North Dallas demonstration dataset
- Upload support for completed market-scoring CSV files
- Raw-data processing for user-selected U.S. markets
- Animated dataset compatibility checks
- Automatic column and value standardization
- Cross-source city coverage validation
- Selection of all compatible cities or individual markets
- Three investor strategy presets
- Adjustable fundamentals, momentum, and robustness weights
- Custom-strategy detection when sliders are changed
- Personalized preference-match scores
- Market comparison cards
- Individual market exploration
- Historical home-value, population, and construction charts
- Market warning factors with recommended next steps
- Downloadable client comparison report

## How the Dashboard Works

### Step 1: Choose a dataset

The dashboard provides three ways to begin.

#### Option A: Use the included North Dallas data

Use the project’s prepared dataset covering:

- Anna
- Celina
- Frisco
- McKinney
- Melissa
- Plano
- Princeton
- Prosper
- Richardson

This option is ready for immediate analysis and is useful for demonstrations.

#### Option B: Upload a market-scoring file

Upload a completed CSV containing one row per market.

Required columns include:

- `City`
- `Long_Term_Fundamentals_Score`
- `Fundamentals_Rank`
- `Current_Market_Momentum_Score`
- `Momentum_Rank`
- `Pct_Top_3`
- `Average_Rank`
- `Robustness_Profile`
- `Current_Market_Regime`

The dashboard checks:

- Required columns
- Minimum market coverage
- Unique city names
- Numeric formatting
- Score ranges from 0 to 100

#### Option C: Build from original source files

Upload original city-level data from four sources:

1. Zillow home-value history
2. Redfin housing-market activity
3. U.S. Census population estimates
4. U.S. Census residential building permits

The dashboard then:

1. Reads each file.
2. Standardizes columns and market names.
3. Converts source values into consistent numeric formats.
4. Checks missing and duplicate records.
5. Finds markets represented across every source.
6. Allows the user to select all compatible markets or specific cities.
7. Calculates market features and scores.
8. Runs the ranking-robustness simulation.
9. Builds a model-ready decision table.

At least three compatible markets are required for comparative ranking.

### Step 2: Build an investment strategy

Users can begin with one of three presets:

| Strategy | Fundamentals | Momentum | Intended emphasis |
|---|---:|---:|---|
| Long-Term Growth | 70% | 30% | Demographic growth and historical appreciation |
| Balanced | 50% | 50% | Equal attention to long-term and current conditions |
| Current Resilience | 30% | 70% | Present-day pricing, demand, inventory, and supply |

Users can also adjust the sliders manually. When a preset’s values are changed, the strategy is identified as **Custom**.

A separate ranking-confidence adjustment controls how much ranking robustness influences the final preference-match score.

### Step 3: Review the results

The results workspace contains two primary views.

#### Results Summary

The summary identifies the strongest matches for the selected strategy and presents:

- Best overall match
- Alternative markets
- Preference-match score
- Fundamentals score
- Momentum score
- Top-three probability
- Primary market strength
- Main factor to monitor

#### Compare & Explore

Users can compare up to three markets and then explore any market included in the analysis.

The market explorer includes:

- Five-year home-value CAGR
- Population CAGR
- Home-sales year-over-year change
- Months of supply
- Historical Zillow Home Value Index
- Annual population trend
- Residential construction activity
- Fundamentals and momentum scores
- Average rank
- Top-three probability
- Market regime
- Robustness classification
- Factors to monitor
- Suggested investor next steps

Users can also download a client-facing market comparison report as a PDF.

## Data Sources

### Zillow Research

[Zillow Research Housing Data](https://www.zillow.com/research/data/)

The Zillow Home Value Index is used to evaluate:

- Historical home values
- Five-year appreciation
- Three-year appreciation
- Year-over-year value changes
- Distance from a previous market peak

The raw-data workflow expects city-level ZHVI history with at least five years of observations.

### Redfin Data Center

[Redfin Data Center Downloads](https://www.redfin.com/news/data-center/downloads/)

Redfin data is used to evaluate:

- Homes sold
- Pending sales
- Inventory
- Active listings
- New listings
- Median days on market
- Months of supply
- Sale-to-list ratio

The raw-data workflow uses monthly city-level observations. Missing Redfin values should remain missing rather than being replaced with zero.

### U.S. Census Bureau Population Estimates

[City and Town Population Estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html)

Population data is used to calculate:

- Total population change
- Population CAGR
- Recent annual population growth
- Population-growth acceleration or deceleration

Use one consistent Census vintage. Estimates from different vintages should not be combined because previously reported years may be revised.

### U.S. Census Bureau Building Permits Survey

[Building Permits Survey](https://www.census.gov/construction/bps/)

[Place-Level Building Permit Files](https://www2.census.gov/econ/bps/Place/)

Building-permit data is used to evaluate:

- Total permitted housing units
- Permits per 1,000 residents
- Construction intensity
- Changes from peak construction activity

The dashboard accepts multiple annual place-level permit files. For a current six-year comparison, users can upload one annual file for each year from 2020 through 2025.

Building permits measure units authorized, not necessarily units completed.

## Data Requirements

For the original-source workflow:

- Every source must use city- or place-level geography.
- The same cities should appear across the sources.
- The files should cover comparable periods.
- Zillow history must contain at least five years.
- Redfin data must contain monthly city-level market measurements.
- Population data must come from one Census vintage.
- Permit uploads must include one annual file for every selected year.
- Missing values must not be replaced with zero.
- Market names and state identifiers must be present or derivable.

The dashboard identifies the intersection of markets that can be matched across all four sources. Markets missing from one or more sources are excluded from the final selection.

## Methodology

### Long-Term Fundamentals Score

The long-term fundamentals score combines:

- Population CAGR
- Five-year home-value CAGR
- Population-growth acceleration

These measurements represent demographic expansion and longer-term market growth.

### Current Market Momentum Score

The current market momentum score incorporates:

- Home-value year-over-year change
- Homes-sold year-over-year change
- Sale-to-list ratio
- Inventory year-over-year change
- Months of supply

Indicators are normalized to a comparable 0–100 scale.

Variables where lower values indicate stronger market conditions—such as inventory growth and months of supply—are reverse-scored before inclusion.

### Preference-Match Score

The dashboard combines the user’s fundamentals and momentum weights into a base preference score:

```text
Base Preference Score
= Fundamentals Weight × Fundamentals Score
+ Momentum Weight × Momentum Score
```

Ranking robustness can then influence up to 30% of the final score:

```text
Preference Match Score
= (1 − Robustness Share) × Base Preference Score
+ Robustness Share × Top-3 Probability
```

The score is a comparison tool. It is not a predicted investment return.

### Ranking-Robustness Simulation

The model evaluates 10,000 alternative weighting scenarios.

For each market, the simulation calculates:

- Probability of ranking first
- Probability of ranking in the top three
- Average rank
- Median rank
- Best observed rank
- Worst observed rank
- Composite-score distribution
- Score dispersion
- Sensitivity to investor preferences

This distinguishes markets that remain competitive under many assumptions from those that rank highly only under a narrow strategy.

### Market Regimes

The model classifies current market conditions using pricing, demand, and supply indicators.

Possible classifications include:

- Relatively Stable
- Recovery / Repricing
- Demand Growth / Supply Pressure
- Mixed / Transitional

These classifications provide context for the numerical scores and are not forecasts.

## Warning Factors

The market explorer identifies conditions that may require additional investor attention, including:

- Elevated months of supply
- Rising inventory
- Weak home-sales activity
- A low sale-to-list ratio
- Moderate long-term fundamentals
- High construction intensity
- Price correction or repricing signals

Each warning includes a short recommended next step, such as reviewing neighborhood-level inventory, confirming demand conditions, comparing concessions, or adjusting acquisition assumptions.

Warnings should guide additional due diligence rather than automatically disqualifying a market.

## Project Structure

```text
tx_market_analysis/
├── .streamlit/
│   └── config.toml
├── dashboard/
│   ├── app.py
│   ├── client_app.py
│   ├── pdf_report.py
│   └── raw_data_pipeline.py
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
├── .gitignore
├── README.md
└── requirements.txt
```

### Main application files

- `dashboard/client_app.py` — investor-facing Streamlit interface and workflow
- `dashboard/raw_data_pipeline.py` — source ingestion, cleaning, validation, feature engineering, scoring, and robustness analysis
- `dashboard/pdf_report.py` — downloadable client comparison report
- `dashboard/app.py` — earlier dashboard implementation
- `data/processed/` — prepared North Dallas demonstration data
- `notebooks/` — original research, exploratory analysis, and model development

Raw source datasets are excluded from Git. Prepared North Dallas outputs are included so the demonstration can run without downloading the original national files.

## Running the Dashboard Locally

### 1. Clone the repository

```bash
git clone https://github.com/ninahhuang/tx_market_analysis.git
cd tx_market_analysis
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the current dashboard

Run Streamlit from the project root so it finds `.streamlit/config.toml`:

```bash
streamlit run dashboard/client_app.py
```

The dashboard will normally open at:

```text
http://localhost:8501
```

## Streamlit Configuration

The project uses `.streamlit/config.toml` for its theme and upload settings.

```toml
[server]
maxUploadSize = 500
maxMessageSize = 500

[theme]
base = "dark"
primaryColor = "#9BB6FF"
backgroundColor = "#111638"
secondaryBackgroundColor = "#171C4D"
textColor = "#FCFAFF"
```

The 500 MB setting changes Streamlit’s permitted upload size. It does not increase the memory available to the application.

Restart the Streamlit server after changing configuration values.

## Deployment and Large-File Considerations

The dashboard can be deployed through Streamlit Community Cloud using:

```text
dashboard/client_app.py
```

as the main application file.

The complete national Redfin CSV is significantly larger than the other source files. Although the dashboard reads it in chunks, Streamlit first holds the uploaded file in memory. Processing the national file can therefore exceed Community Cloud’s memory allocation.

For a scalable public deployment, the recommended approach is:

1. Process the national Redfin dataset outside the deployed application.
2. Keep only the model’s required columns.
3. Divide the data into state-level Parquet files.
4. Store those files in cloud storage or another server-side location.
5. Ask the user to select a state before selecting cities.
6. Load and cache only the selected state’s data.

This removes the need for every visitor to download and upload the complete national Redfin file.

The 500 MB upload setting permits larger uploads but does not guarantee that Community Cloud has enough memory to process them.

## Technologies

- Python
- Streamlit
- pandas
- NumPy
- Altair
- ReportLab
- OpenPyXL
- Jupyter Notebook
- Git and GitHub

## Limitations

- The model compares cities relative to the markets included in the current analysis.
- Scores can change when the selected market group changes.
- Results depend on source availability and consistent market naming.
- City-level analysis does not capture neighborhood or property-level differences.
- Recent housing indicators may change quickly or be revised.
- Building permits represent authorized construction rather than completed homes.
- Composite rankings depend on the selected investment priorities.
- Ranking robustness measures model stability, not investment certainty.
- Historical appreciation does not guarantee future performance.
- The dashboard does not model property prices, rents, financing, taxes, insurance, renovation costs, or investor-specific cash flows.
- Large national files may exceed the resources available on hosted Streamlit deployments.

## Intended Use

This dashboard is designed for:

- Initial market screening
- Comparing investment-market candidates
- Identifying market strengths and tradeoffs
- Exploring sensitivity to different investor priorities
- Preparing client-facing market discussions
- Directing deeper market and property-level due diligence

It should not be used as the sole basis for an investment decision.

## Disclaimer

This project is an analytical market-screening tool and does not provide financial, investment, legal, tax, lending, or real-estate advice.

Results should be combined with current local-market research, neighborhood-level analysis, property-level underwriting, professional guidance, and independent due diligence before making an investment decision.