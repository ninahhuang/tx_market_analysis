# Market Match: U.S. Housing Market Investment Screening

Market Match is a Streamlit dashboard for screening and comparing U.S. housing markets using housing values, population growth, market activity, and residential construction data.

The application began as a North Dallas market analysis and has expanded into a national, BigQuery-backed dashboard. Users can compare cities across different states, inspect historical trends, adjust investment preferences, and generate ranked market results.

> Market Match is a screening and research tool. It is not an investment forecast, appraisal, or substitute for property-level due diligence.

## Live dashboard

[Open the Streamlit dashboard](https://tx-market-analysis.streamlit.app/)

## Repository

[View the project on GitHub](https://github.com/ninahhuang/tx_market_analysis)

## Key features

- Compare cities across multiple U.S. states
- Select between 3 and 50 markets for an analysis
- Compare up to 10 markets simultaneously in detailed charts
- View home-value, population, residential-construction, and market-activity trends
- Rank markets using adjustable investment preferences
- Explore both long-term fundamentals and recent market momentum
- Identify warning signals such as rising inventory or weakening sales
- Generate downloadable PDF reports
- Query centralized cloud data instead of requiring every user to upload source files
- Retain local, uploaded-file, and raw-source workflows while the cloud migration is tested

## Current data options

The dashboard currently supports four workflows:

1. **Included North Dallas data**  
   Uses the processed demonstration dataset included with the repository.

2. **Cloud market database**  
   Retrieves national city-level data from Google BigQuery. This is the intended production workflow.

3. **Market-scoring file upload**  
   Accepts a prepared CSV or Excel file containing market metrics.

4. **Original source-file workflow**  
   Accepts Zillow, Census, Redfin, and building-permit source files and processes them locally.

The legacy options will remain available until the national cloud dataset passes final validation. The public dashboard can then be simplified to use only the cloud database.

## Dashboard workflow

### 1. Choose a data source

Select the included demonstration data, the BigQuery cloud database, a prepared scoring file, or original source files.

### 2. Select markets

When using BigQuery, select cities from the national market directory. Market labels include the state abbreviation—for example:

- Knoxville, TN
- Frisco, TX
- Huntsville, AL
- Raleigh, NC

The dashboard uses a stable `market_id` internally, so cities with identical names in different states remain separate.

### 3. Set investment preferences

Adjust the relative importance of market fundamentals and recent momentum. An optional robustness component can be included when simulation results are available.

### 4. Review the rankings

The dashboard produces:

- Composite preference scores
- Fundamentals and momentum scores
- Market tier classifications
- Warning indicators
- Supporting market measurements

### 5. Compare trends

View charts for:

- One city at a time
- A selected comparison group
- All selected cities

Large analysis groups are supported, but detailed overlaid charts are intentionally limited to a smaller number of markets to preserve readability.

## Data architecture

Market Match uses Google BigQuery as its central analytical database.

```text
Public data sources
        │
        ▼
Python ingestion and validation scripts
        │
        ▼
Google BigQuery: market_data
        │
        ▼
Parameterized dashboard queries
        │
        ▼
Streamlit analysis and visualizations
```

The dashboard queries only the selected market IDs and relevant date ranges. Query results are cached for one hour to reduce repeated BigQuery usage.

## BigQuery tables

The `market_data` dataset contains the following primary tables:

| Table | Purpose | Typical grain |
|---|---|---|
| `markets` | Canonical city and state directory | One row per market |
| `home_values` | Zillow Home Value Index history | Market and month |
| `population` | Census annual population estimates | Market and year |
| `market_activity` | Redfin housing-market measurements | Market and month |
| `building_permits` | Census permitted housing units | Market and year |

The application may also use derived tables such as:

- `final_decision_table`
- `market_ranking_robustness`

### Market identity

Each market has a stable identifier and supporting geographic fields:

- `market_id`
- `city`
- `state_name`
- `state_code`
- `state_fips`
- `place_fips`

The combination of state and city prevents records such as Springfield, Missouri and Springfield, Illinois from being merged accidentally.

## Data sources

### Zillow Home Value Index

Monthly city-level home-value history is sourced from the [Zillow Research Data](https://www.zillow.com/research/data/) library.

The production loader downloads Zillow’s city-level ZHVI data, standardizes city and state names, matches observations to the Census market directory, and loads the resulting records into BigQuery.

### U.S. Census population estimates

Annual city and town population estimates come from the Census Bureau’s [Population Estimates Program](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html).

The current loader uses the newest configured Census vintage and preserves the vintage value so later revisions can be identified.

### Redfin market activity

City-level market measurements come from the [Redfin Data Center](https://www.redfin.com/news/data-center/downloads/).

The project uses measurements such as:

- Homes sold
- Inventory
- Months of supply
- Sale-to-list ratio

Redfin’s city-level monthly data may represent rolling three-month periods. See the [Redfin methodology](https://www.redfin.com/news/data-center/methodology/) before interpreting short-term movements.

### Census Building Permits Survey

Residential construction data comes from the Census Bureau’s [Building Permits Survey](https://www.census.gov/construction/bps/) place-level files.

The loader is designed to combine the Census region files for multiple years, map each record to a state and place, and load annual authorized-unit totals into BigQuery.

The underlying files are available from the [Census place-level BPS directory](https://www2.census.gov/econ/bps/Place/).

## Scoring methodology

The dashboard separates structural market fundamentals from recent housing-market momentum.

### Fundamentals score

The default fundamentals score is based on:

- 45% population compound annual growth
- 35% five-year home-value compound annual growth
- 20% population-growth acceleration

### Momentum score

The default momentum score is based on:

- 25% home-value year-over-year change
- 20% homes-sold year-over-year change
- 20% inverse inventory growth
- 20% inverse months of supply
- 15% sale-to-list percentage

Metrics are normalized to a relative 0–100 scale within the comparison group.

### Preference score

Users can adjust the balance between fundamentals and momentum. When robustness results are available, robustness can contribute up to 30% of the final score.

Because the scores are relative, a city’s result can change when the comparison group changes.

### Warning indicators

The dashboard can flag conditions such as:

- Inventory growth greater than 10%
- More than five months of supply
- Negative year-over-year homes-sold growth
- Sale-to-list percentage below 98%

Warnings are screening signals, not automatic investment decisions.

## Robustness analysis

The modeling workflow can test ranking stability across 10,000 simulated weighting scenarios.

This helps distinguish:

- Markets that remain highly ranked across many reasonable assumptions
- Markets whose rankings are highly dependent on one particular weighting choice
- Markets that appear attractive but have unstable results

## Project structure

```text
tx_market_analysis/
├── .streamlit/
│   └── config.toml
├── dashboard/
│   ├── app.py
│   ├── bigquery_data.py
│   ├── bigquery_test_page.py
│   ├── client_app.py
│   ├── pdf_report.py
│   └── raw_data_pipeline.py
├── scripts/
│   ├── load_census_building_permits.py
│   ├── load_census_markets_population.py
│   ├── load_redfin_market_activity.py
│   └── load_zillow_home_values.py
├── data/
│   └── processed/
├── demo/
│   ├── valid_market_scoring_sample.csv
│   └── invalid_market_scoring_sample.csv
├── docs/
│   ├── data_dictionary.md
│   ├── methodology.md
│   └── testing_checklist.md
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_market_eda.ipynb
│   ├── 03_market_momentum_model.ipynb
│   └── 04_national_screening_validation.ipynb
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── README.md
```

## Local installation

### Requirements

- Python 3.11 or newer
- Git
- Google Cloud CLI for BigQuery authentication
- Access to the `tx-market-analysis` Google Cloud project, or a replacement project with the required tables

### 1. Clone the repository

```bash
git clone https://github.com/ninahhuang/tx_market_analysis.git
cd tx_market_analysis
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Authenticate with Google Cloud

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project tx-market-analysis
gcloud config set project tx-market-analysis
```

Confirm that the application can see the dataset:

```bash
python -c 'from google.cloud import bigquery; client = bigquery.Client(project="tx-market-analysis"); print([dataset.dataset_id for dataset in client.list_datasets()])'
```

The output should include:

```text
market_data
```

### 5. Start the dashboard

```bash
streamlit run dashboard/client_app.py
```

Open the local address shown in the terminal, normally:

```text
http://localhost:8501
```

## Loading production data

Run loader scripts from the repository’s top-level directory with the virtual environment activated.

### Census market directory and population

```bash
python -m scripts.load_census_markets_population
```

### Zillow home values

```bash
python -m scripts.load_zillow_home_values
```

### Redfin market activity

Place the Redfin city-level source file at one of the expected local paths, such as:

```text
data/raw/redfin_monthly_city.csv
```

Then run:

```bash
python -m scripts.load_redfin_market_activity
```

### Census building permits

```bash
python -m scripts.load_census_building_permits
```

The raw source files should not be committed to Git. Only code, documentation, small demonstration files, and appropriate processed outputs should be version controlled.

## Streamlit deployment

The deployed application should authenticate with a dedicated Google Cloud service account rather than a developer’s personal credentials.

Add the service-account fields to Streamlit’s secrets manager under:

```toml
[gcp_service_account]
```

The expected fields include:

- `type`
- `project_id`
- `private_key_id`
- `private_key`
- `client_email`
- `client_id`
- `auth_uri`
- `token_uri`
- `auth_provider_x509_cert_url`
- `client_x509_cert_url`

Never commit a service-account key, `.streamlit/secrets.toml`, or Application Default Credentials file to the repository.

The dashboard service account should receive only the permissions it needs, normally:

- BigQuery Data Viewer
- BigQuery Job User

## Testing

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the automated test suite:

```bash
python -m pytest
```

Compile the main application files:

```bash
python -m compileall dashboard scripts
```

A BigQuery connection test page is also available:

```bash
streamlit run dashboard/bigquery_test_page.py
```

Before deploying a new data load, validate:

- Row counts
- Market counts
- Minimum and maximum dates
- Missing values
- Duplicate market-period records
- Negative or impossible measurements
- Unmatched city and state keys
- Coverage across all required sources
- Dashboard behavior for one, several, and large groups of cities

See [docs/testing_checklist.md](docs/testing_checklist.md) for the project checklist.

## Current migration status

| Component | Status |
|---|---|
| BigQuery connection | Implemented |
| Cross-state market directory | Implemented |
| Cloud market selector | Implemented |
| Census population loader | Implemented and tested |
| Zillow home-value loader | Implemented and tested |
| Redfin market-activity loader | Implemented and tested |
| Census building-permit loader | Implemented; final production validation required |
| Local and uploaded-data workflows | Retained during testing |
| Cloud-only public landing screen | Planned after final validation |

## Data limitations

- Market Match compares cities, not individual properties or neighborhoods.
- Source providers may revise historical records.
- Missing observations are not interpreted as zero.
- Building permits measure authorized construction, not completed housing units.
- Redfin rolling periods should not be interpreted as isolated single-month totals.
- Scores are relative to the selected comparison group.
- Cities without sufficient cross-source coverage may be excluded during analysis.
- The Census incorporated-place source does not represent every possible community type. Hawaii may require a separate Census-designated-place workflow.
- City boundaries and housing-market definitions vary between data providers.
- Recent data may be preliminary.

## Cost controls

BigQuery costs depend on stored data and the amount of data scanned by queries. This project reduces unnecessary usage by:

- Partitioning time-series tables
- Clustering data by `market_id`
- Querying only selected markets
- Selecting only required columns
- Applying date filters
- Caching dashboard query results
- Setting Google Cloud budgets and alerts

A budget alert does not automatically prevent spending. Billing reports and query usage should still be reviewed regularly.

## Documentation

Additional documentation is available in:

- [Data dictionary](docs/data_dictionary.md)
- [Methodology](docs/methodology.md)
- [Testing checklist](docs/testing_checklist.md)

## Roadmap

Planned improvements include:

- Finish production validation of the building-permit pipeline
- Restrict the public selector to markets with complete source coverage
- Replace the landing screen with a cloud-only workflow
- Automate scheduled source refreshes
- Add freshness indicators for every source
- Improve geographic matching for Census-designated places
- Add additional market-level economic and rental indicators
- Expand automated data-quality monitoring
- Add user-friendly explanations of scoring sensitivity

## License

This project is licensed under the terms provided in [LICENSE](LICENSE).

## Disclaimer

This software and its outputs are provided for educational and analytical purposes only. Nothing in the dashboard constitutes financial, legal, tax, real-estate, or investment advice. Users should independently verify the source data and conduct property-level, legal, financial, and market due diligence before making an investment decision.