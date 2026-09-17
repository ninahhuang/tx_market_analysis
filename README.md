# Market Match: Housing Market Investment Screening

Market Match is an interactive Streamlit dashboard for comparing housing markets based on long-term growth, current market conditions, and ranking stability.

The project began as an analysis of nine North Dallas cities and now supports user-provided data for additional U.S. markets. The dashboard can validate original source files, standardize city-level data, calculate comparative scores, test ranking robustness, identify warning factors, and generate a client-ready comparison report.

## Live Dashboard

[Open the deployed Streamlit dashboard](https://tx-market-analysis.streamlit.app/)

> Large national source files—particularly the complete Redfin download—may exceed the memory available on Streamlit Community Cloud. See [Deployment and Large-File Considerations](#deployment-and-large-file-considerations) before uploading very large files.

## Project Purpose

A housing market with rapid population growth or strong historical appreciation does not necessarily have favorable current conditions. Fast-growing markets may also experience:

- Rising inventory
- Elevated housing supply
- Slowing transaction activity
- Increased residential construction
- Weaker short-term price momentum

More mature markets may have slower demographic growth but stronger current demand, greater pricing stability, or more consistent rankings.

Market Match separates these considerations into three decision areas:

1. **Long-term fundamentals** — population growth, historical home-value appreciation, and demographic momentum.
2. **Current market momentum** — pricing, sales activity, inventory, supply, and sale-to-list conditions.
3. **Ranking robustness** — how consistently a market performs when the model’s assumptions and weights change.

The result is a flexible market-screening tool rather than a single universal definition of the “best” market.

## Key Features

- Included nine-market North Dallas demonstration dataset
- Upload support for completed market-scoring CSV files
- Original-source processing for user-selected U.S. cities
- Zillow, Redfin, and U.S. Census source integration
- CSV and Excel support for Census population estimates
- Multiple-file support for annual building-permit data
- Chunked processing for large Redfin CSV files
- Animated dataset compatibility checks
- Automatic column and value standardization
- Missing-value, duplicate-record, and numeric-format validation
- Cross-source city-coverage validation
- Selection of all compatible markets or specific cities
- Three investor strategy presets
- Adjustable fundamentals, momentum, and robustness weights
- Personalized preference-match scores
- 10,000-run ranking-robustness simulation
- Investor-friendly market comparison cards
- Individual market deep dives
- Historical home-value, population, and construction charts
- Warning factors with recommended next steps
- Downloadable client comparison report
- Demonstration files for successful and unsuccessful upload testing
- Detailed data dictionary, methodology, and testing documentation

## How the Dashboard Works

### Step 1: Choose a Dataset

The dashboard provides three ways to begin.

#### Option A: Use the Included North Dallas Data

The included demonstration dataset covers:

- Anna
- Celina
- Frisco
- McKinney
- Melissa
- Plano
- Princeton
- Prosper
- Richardson

This option is ready for immediate analysis and does not require any file uploads.

#### Option B: Upload a Market-Scoring File

Users can upload a completed CSV containing one row per housing market.

Required columns are:

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
- A minimum of three market rows
- Unique and nonblank city names
- Numeric score and ranking values
- Score ranges from 0 to 100

Demonstration files are available in the [`demo/`](demo/) folder:

- [`valid_market_scoring_sample.csv`](demo/valid_market_scoring_sample.csv) — passes all compatibility checks
- [`invalid_market_scoring_sample.csv`](demo/invalid_market_scoring_sample.csv) — demonstrates duplicate, nonnumeric, and out-of-range validation errors

#### Option C: Build from Original Source Files

Users can upload original city-level files from four sources:

1. Zillow home-value history
2. Redfin housing-market activity
3. U.S. Census population estimates
4. U.S. Census residential building permits

The dashboard then:

1. Reads the source files.
2. Standardizes market names and state identifiers.
3. Converts source measurements into consistent numeric formats.
4. Checks required columns, missing values, and duplicate records.
5. Identifies cities represented across every source.
6. Excludes markets that cannot be matched across all four sources.
7. Allows the user to analyze all compatible markets or select specific cities.
8. Calculates market-level features.
9. Calculates fundamentals and momentum scores.
10. Runs the ranking-robustness simulation.
11. Builds a model-ready decision table.

At least three fully matched markets are required for comparative scoring and ranking.

### Step 2: Select Markets

When original source files are approved, users can choose:

- **All markets** — analyzes every city represented across all four sources.
- **Select specific cities** — allows users to search for and select individual city-state combinations.

At least three markets must be selected. Scores and ranks are recalculated for the selected comparison group.

### Step 3: Build an Investment Strategy

Users can begin with one of three presets:

| Strategy | Fundamentals | Momentum | Intended emphasis |
|---|---:|---:|---|
| Long-Term Growth | 70% | 30% | Demographic growth and historical appreciation |
| Balanced | 50% | 50% | Equal attention to long-term and current conditions |
| Current Resilience | 30% | 70% | Current pricing, demand, inventory, and supply |

Users can also adjust the sliders manually. When the values no longer match a preset, the strategy is identified as **Custom**.

Fundamentals and momentum weights must total 100%.

A separate robustness control determines how much ranking stability influences the final preference-match score. Robustness can contribute up to 30% of the final score.

### Step 4: Review the Results

The results workspace contains two primary views.

#### Results Summary

The summary presents:

- Best overall match
- Alternative markets
- Preference-match score
- Fundamentals score
- Momentum score
- Top-three probability
- Primary market strength
- Main factor to monitor

#### Compare & Explore

Users can compare up to three markets and explore any market included in the current analysis.

The market explorer includes:

- Five-year home-value CAGR
- Population CAGR
- Homes-sold year-over-year change
- Months of supply
- Historical Zillow Home Value Index
- Annual population trend
- Residential construction activity
- Fundamentals and momentum scores
- Average simulated rank
- Top-three probability
- Market regime
- Robustness classification
- Factors to monitor
- Recommended investor next steps

Users can also download a client-facing market comparison report as a PDF.

## Data Sources

### Zillow Research

[Zillow Research Housing Data](https://www.zillow.com/research/data/)

The raw-data workflow uses city-level Zillow Home Value Index history to calculate:

- Latest typical home value
- Five-year home-value CAGR
- Year-over-year home-value change

The file should contain at least five years of monthly history.

### Redfin Data Center

[Redfin Data Center Downloads](https://www.redfin.com/news/data-center/downloads/)

The dashboard uses monthly city-level Redfin data for:

- Homes sold
- Inventory or active listings
- Months of supply
- Average sale-to-list ratio

The national Redfin file is read in chunks to reduce processing memory. Missing values should remain missing rather than being replaced with zero.

### U.S. Census Bureau Population Estimates

[City and Town Population Estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html)

The dashboard accepts population files in:

- CSV format
- Excel `.xlsx` format

Population data is used to calculate:

- Latest population
- Population CAGR
- Recent annual population growth
- Population-growth acceleration or deceleration

Use one consistent Census vintage. Previously reported estimates may be revised between vintages, so separate vintages should not be combined.

The current automatic full-state-name mapping includes:

- Arizona
- California
- Colorado
- Florida
- Georgia
- North Carolina
- South Carolina
- Tennessee
- Texas

Supporting another state may require adding its full name and two-letter abbreviation to the `STATE_ABBREVIATIONS` mapping in `dashboard/raw_data_pipeline.py`.

### U.S. Census Bureau Building Permits Survey

[Building Permits Survey](https://www.census.gov/construction/bps/)

[Place-Level Building Permit Files](https://www2.census.gov/econ/bps/Place/)

Building-permit data is used to calculate:

- Latest annual permitted housing units
- Average annual permitted housing units
- Latest permits per 1,000 residents
- Average permits per 1,000 residents

The dashboard accepts multiple annual place-level files in CSV or TXT format.

For a recent six-year comparison, users can upload one annual file for each year from 2020 through 2025.

Building permits measure units authorized, not necessarily units completed.

## Data Requirements

For the original-source workflow:

- Every file must contain city- or place-level data.
- City data should not be combined with county, ZIP-code, neighborhood, or metropolitan-area data.
- The same cities should appear across all four sources.
- At least three cities must appear in every source.
- Source files should cover comparable periods.
- Zillow history must contain at least five years of observations.
- Redfin data must contain current and prior-year monthly observations.
- Population data must include at least three annual observations.
- Population estimates must come from one Census vintage.
- Permit uploads should include one annual file for each selected year.
- City and state information must be present or derivable.
- Required numeric measurements must not be blank.
- Missing values must not be replaced with zero.
- Duplicate market-period records must be resolved.

The model uses the intersection of markets available across all four sources. A market missing from any source is excluded.

For exact columns, units, date formats, and accepted file structures, see the [Data Dictionary](docs/data_dictionary.md).

## Methodology

### Feature Standardization

Market measurements are converted to comparable scores from 0 to 100 using min-max scaling.

Higher values are treated as favorable for:

- Population CAGR
- Five-year home-value CAGR
- Population-growth acceleration
- Year-over-year home-value change
- Year-over-year homes-sold change
- Sale-to-list percentage

Lower values are treated as favorable for:

- Inventory growth
- Months of supply

Inventory growth and months of supply are therefore reverse-scored.

If every market has the same value for a measurement, each market receives a neutral score of 50 for that measurement.

Because the model uses relative scaling, scores depend on the markets included in the analysis.

### Long-Term Fundamentals Score

```text
Long-Term Fundamentals Score
= 45% × Population CAGR Score
+ 35% × Five-Year Home-Value CAGR Score
+ 20% × Population-Growth Acceleration Score
```

A higher score indicates stronger longer-term demographic and home-value growth relative to the other selected markets.

### Current Market Momentum Score

```text
Current Market Momentum Score
= 25% × Home-Value YoY Score
+ 20% × Homes-Sold YoY Score
+ 20% × Reverse Inventory YoY Score
+ 20% × Reverse Months-of-Supply Score
+ 15% × Sale-to-List Score
```

A higher score indicates stronger current market conditions relative to the other selected markets.

### Preference-Match Score

The user-selected fundamentals and momentum weights create a base score:

```text
Base Preference Score
= Fundamentals Weight × Fundamentals Score
+ Momentum Weight × Momentum Score
```

Ranking robustness can then influence up to 30% of the result:

```text
Preference-Match Score
= (1 − Robustness Share) × Base Preference Score
+ Robustness Share × Top-Three Probability
```

The preference-match score measures alignment with the selected strategy. It is not a predicted return.

### Ranking-Robustness Simulation

The model runs 10,000 alternative weighting scenarios.

During each simulation:

1. The fundamentals measurements receive randomized weights.
2. The momentum measurements receive randomized weights.
3. The total fundamentals share is randomly selected between 30% and 70%.
4. The remaining share is assigned to momentum.
5. Every market receives a simulated composite score.
6. Markets are ranked for that simulation.

The model records:

- Percentage of simulations in which each market ranks in the top three
- Average simulated rank
- Robustness classification

Robustness profiles are assigned as follows:

| Top-three probability | Classification |
|---:|---|
| 75% or higher | Highly Robust |
| 40% to less than 75% | Moderately Robust |
| 15% to less than 40% | Weight Sensitive |
| Less than 15% | Consistently Lower Ranked |

Robustness measures ranking consistency under changing assumptions. It does not represent investment certainty.

### Market Regimes

Markets are classified using their fundamentals and momentum scores:

| Fundamentals | Momentum | Market regime |
|---:|---:|---|
| 50 or higher | 50 or higher | Strong / Expanding |
| 50 or higher | Below 50 | Long-Term Strength / Near-Term Pressure |
| Below 50 | 50 or higher | Momentum-Led / Developing Fundamentals |
| Below 50 | Below 50 | Weak / Transitional |

These classifications summarize the current model results and are not forecasts.

For complete formulas and interpretation guidance, see [Methodology](docs/methodology.md).

## Warning Factors

The market explorer identifies four threshold-based conditions.

### Inventory Growth

Triggered when:

```text
Inventory YoY > 10%
```

Recommended response:

Review competing listings, expected time on market, and rent assumptions before making an offer.

### Months of Supply

Triggered when:

```text
Months of Supply > 5
```

Recommended response:

Use conservative appreciation assumptions and investigate price reductions, closing credits, or other seller concessions.

### Home-Sales Activity

Triggered when:

```text
Homes Sold YoY < 0%
```

Recommended response:

Confirm recent comparable sales and allow for a longer holding or resale period.

### Sale-to-List Ratio

Triggered when:

```text
Sale-to-List Percentage < 98%
```

Recommended response:

Compare recent asking and closing prices and consider negotiating below list price.

When no threshold is triggered, the dashboard recommends routine monitoring.

Warning factors are due-diligence signals. They do not automatically disqualify a market.

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
├── demo/
│   ├── invalid_market_scoring_sample.csv
│   └── valid_market_scoring_sample.csv
├── docs/
│   ├── data_dictionary.md
│   ├── methodology.md
│   └── testing_checklist.md
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_market_eda.ipynb
│   └── 03_market_momentum_model.ipynb
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### Main Application Files

- `dashboard/client_app.py` — current investor-facing Streamlit application
- `dashboard/raw_data_pipeline.py` — source ingestion, cleaning, validation, feature engineering, scoring, and robustness analysis
- `dashboard/pdf_report.py` — client comparison PDF generation
- `dashboard/app.py` — earlier dashboard implementation retained for reference
- `data/processed/` — prepared North Dallas demonstration data
- `notebooks/` — original data preparation, exploratory analysis, and model-development work

### Documentation

- [`docs/data_dictionary.md`](docs/data_dictionary.md) — accepted files, required columns, units, date formats, and geographic requirements
- [`docs/methodology.md`](docs/methodology.md) — feature calculations, score formulas, robustness analysis, market regimes, and warning thresholds
- [`docs/testing_checklist.md`](docs/testing_checklist.md) — application, upload, selector, visualization, PDF, and deployment testing procedures

### Demonstration Files

- [`demo/valid_market_scoring_sample.csv`](demo/valid_market_scoring_sample.csv) — sample file designed to pass validation
- [`demo/invalid_market_scoring_sample.csv`](demo/invalid_market_scoring_sample.csv) — sample file designed to demonstrate validation failures

Raw national source datasets are excluded from Git. Prepared North Dallas outputs are included so the demonstration can run without downloading the original files.

## Running the Dashboard Locally

### 1. Clone the Repository

```bash
git clone https://github.com/ninahhuang/tx_market_analysis.git
cd tx_market_analysis
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate the Environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Installing the requirements is necessary for PDF generation because `dashboard/pdf_report.py` depends on ReportLab.

If ReportLab is unavailable after installation:

```bash
python -m pip install "reportlab>=4.2,<5"
```

### 5. Start the Dashboard

Run Streamlit from the repository root so it detects `.streamlit/config.toml`:

```bash
streamlit run dashboard/client_app.py
```

The dashboard normally opens at:

```text
http://localhost:8501
```

## Testing the Dashboard

The repository contains two demonstration scoring files.

### Test a Successful Upload

Upload:

```text
demo/valid_market_scoring_sample.csv
```

Expected result:

- All five compatibility checks pass.
- The dataset is approved.
- The user can continue to strategy selection.
- All three sample markets appear in the analysis.

### Test an Unsuccessful Upload

Upload:

```text
demo/invalid_market_scoring_sample.csv
```

Expected result:

- The duplicate city is identified.
- The nonnumeric fundamentals rank is identified.
- The momentum score above 100 is identified.
- The top-three probability below zero is identified.
- The application remains running, but the dataset is not approved.

For the complete manual testing process, see the [Dashboard Testing Checklist](docs/testing_checklist.md).

## Streamlit Configuration

The project uses `.streamlit/config.toml` for theme and upload settings:

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

The 500 MB configuration changes Streamlit’s permitted upload size. It does not increase the memory available to the local computer or deployed application.

Restart the Streamlit server after changing configuration values.

## Deployment and Large-File Considerations

The dashboard can be deployed through Streamlit Community Cloud using:

```text
dashboard/client_app.py
```

as the main application file.

The complete national Redfin CSV is considerably larger than the other sources. Although the dashboard processes it in chunks, Streamlit first receives the uploaded file. Processing the national dataset may exceed the memory available on Community Cloud.

For a more scalable public deployment:

1. Process the national Redfin dataset outside the deployed application.
2. Retain only the columns required by the model.
3. Divide the data into smaller state-level files.
4. Store the prepared files in cloud storage or another server-side location.
5. Ask the user to select a state before selecting cities.
6. Load and cache only the selected state’s data.

The 500 MB upload configuration permits larger uploads but does not guarantee sufficient processing memory.

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

- The model compares cities relative to the markets in the current analysis.
- Scores and ranks may change when cities are added or removed.
- Min-max scaling can be affected by extreme values.
- Results depend on source availability and consistent market naming.
- City-level analysis does not capture neighborhood or property-level differences.
- Recent housing indicators may change quickly or be revised.
- Building permits represent authorized construction rather than completed housing.
- Construction measurements currently provide context but do not directly affect the fundamentals or momentum scores.
- Ranking robustness measures model stability, not investment certainty.
- Historical appreciation does not guarantee future performance.
- The current Census full-state-name mapping does not yet include every U.S. state.
- Large national source files may exceed hosted Streamlit resources.
- The dashboard does not model individual-property prices, rents, operating expenses, financing, taxes, insurance, renovation costs, or investor cash flows.

## Intended Use

Market Match is designed for:

- Initial market screening
- Comparing housing-market candidates
- Identifying market strengths and tradeoffs
- Testing sensitivity to different investor priorities
- Preparing client-facing market discussions
- Directing deeper market, neighborhood, and property-level research

It should not be used as the sole basis for an investment decision.

## License

This project is licensed under the [MIT License](LICENSE).

The license applies to the project’s original code and documentation. Third-party data remains subject to the terms and policies of its original providers.

## Disclaimer

This project is an analytical market-screening tool. It does not provide financial, investment, legal, tax, lending, or real-estate advice.

Results should be combined with current local-market research, neighborhood-level analysis, property-level underwriting, professional guidance, and independent due diligence before making an investment decision.