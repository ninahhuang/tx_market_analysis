# Data Dictionary

## Purpose

This document describes the data accepted by the Market Match housing-market investment screening dashboard.

The dashboard supports three data paths:

1. Use the included North Dallas dataset.
2. Upload a completed market-scoring CSV.
3. Build a new analysis from original Zillow, Redfin, and U.S. Census source files.

All uploaded data should represent city-level housing markets. County, metropolitan-area, ZIP-code, neighborhood, and city data should not be combined in the same analysis.

---

## General Data Requirements

For an uploaded dataset to be analyzed successfully:

- At least three cities must be available.
- Each city must have a city name and state.
- The same cities should appear across all four original data sources.
- City and state names should be consistent across sources.
- Numeric fields must not contain text.
- Required values must not be blank.
- Each city and reporting period should appear only once.
- Scores and probabilities must be between 0 and 100.
- Dates must be recognizable calendar dates.
- Years must be four-digit calendar years.
- All source files should describe the same geographic level.

The dashboard creates a market identifier in this format:

```text
City, State
```

Example:

```text
Plano, TX
```

---

# Market-Scoring File

## Accepted File Type

```text
.csv
```

The market-scoring upload must contain one row per city. Column names are case-sensitive and should match the names below exactly.

## Required Columns

| Column | Type | Unit or format | Description |
|---|---|---|---|
| `City` | Text | City or market name | Unique name used to identify the market. It cannot be blank or duplicated. |
| `Long_Term_Fundamentals_Score` | Number | 0–100 | Relative score for population growth, long-term home-value growth, and population-growth acceleration. |
| `Fundamentals_Rank` | Integer | 1 = strongest | Rank based on the long-term fundamentals score. |
| `Current_Market_Momentum_Score` | Number | 0–100 | Relative score for current home values, sales, inventory, supply, and pricing conditions. |
| `Momentum_Rank` | Integer | 1 = strongest | Rank based on the current market momentum score. |
| `Pct_Top_3` | Number | Percentage, 0–100 | Percentage of robustness simulations in which the market ranked in the top three. |
| `Average_Rank` | Number | Rank | Average position across all robustness simulations. Lower values indicate stronger average placement. |
| `Robustness_Profile` | Text | Classification | Description of how consistently the market ranks under changing assumptions. |
| `Current_Market_Regime` | Text | Classification | Combined interpretation of long-term fundamentals and current momentum. |

## Accepted Robustness Classifications

The model-generated classifications are:

- `Highly Robust`
- `Moderately Robust`
- `Weight Sensitive`
- `Consistently Lower Ranked`

## Accepted Market-Regime Classifications

The model-generated classifications are:

- `Strong / Expanding`
- `Long-Term Strength / Near-Term Pressure`
- `Momentum-Led / Developing Fundamentals`
- `Weak / Transitional`

## Market-Scoring Validation Rules

The dashboard checks that:

- All nine required columns are present.
- At least three market rows are present.
- Every city name is populated.
- City names are unique.
- All score and ranking fields are numeric.
- Fundamentals, momentum, and top-three probability are between 0 and 100.

The dashboard does not recalculate the underlying scores when this upload option is used. It assumes the uploaded values have already been calculated correctly.

---

# Original Source Files

The original-source workflow processes four categories of data:

1. Zillow home-value history
2. Redfin market activity
3. U.S. Census population estimates
4. U.S. Census residential building permits

The dashboard standardizes these sources before scoring the markets.

---

## 1. Home-Value History

### Accepted File Type

```text
.csv
```

### Recommended Source

Zillow Home Value Index, or ZHVI, using:

- Geography: City
- Home type: All Homes
- Frequency: Monthly
- Adjustment: Smoothed and seasonally adjusted

### Accepted Raw Zillow Structure

The dashboard recognizes:

- `RegionName` or `City` as the city field
- `StateName` or `State` as the state field
- Monthly columns with date-formatted column names
- Numeric home values in the monthly columns

Example:

| RegionName | StateName | 2020-01-31 | 2020-02-29 |
|---|---|---:|---:|
| Plano | TX | 345000 | 346500 |

### Standardized Internal Structure

| Column | Type | Unit or format | Description |
|---|---|---|---|
| `City` | Text | City name | City associated with the observation. |
| `State` | Text | Two-letter abbreviation | State associated with the city. |
| `Date` | Date | Recommended `YYYY-MM-DD` | Monthly observation date. |
| `Home_Value` | Number | U.S. dollars | Typical home value represented by ZHVI. |

### History Requirement

At least five years of home-value observations are required to calculate five-year compound annual growth.

The model also needs an observation approximately one year before the latest observation to calculate year-over-year home-value growth.

---

## 2. Market Activity

### Accepted File Type

```text
.csv
```

### Recommended Source

Redfin Data Center city-level monthly market data.

### Required Raw Redfin Columns

| Source column | Type | Unit or format | Description |
|---|---|---|---|
| `REGION TYPE` | Text | `City` | Used to retain city-level records. |
| `REGION NAME` | Text | `City, State` | Identifies the city and state. |
| `PERIOD END` | Date | Date | End date of the reporting period. |
| `HOMES SOLD` | Number | Number of homes | Homes sold during the reporting period. |
| `INVENTORY` or `ACTIVE LISTINGS` | Number | Number of listings | Available housing inventory. |
| `MONTHS OF SUPPLY` | Number | Months | Estimated months needed to sell available inventory. |
| `AVERAGE SALE TO LIST RATIO (%)` | Number | Percentage | Average sale price divided by original or final list price, depending on Redfin’s definition. |

### Standardized Internal Structure

| Column | Type | Unit or format | Description |
|---|---|---|---|
| `City` | Text | City name | City associated with the activity record. |
| `State` | Text | Two-letter abbreviation | State associated with the city. |
| `Date` | Date | Recommended `YYYY-MM-DD` | Reporting-period end date. |
| `Homes_Sold` | Number | Number of homes | Transaction activity during the period. |
| `Inventory` | Number | Number of listings | Available inventory during the period. |
| `Months_of_Supply` | Number | Months | Current inventory relative to sales activity. |
| `Sale_to_List_Pct` | Number | Percentage | Average sale-to-list ratio. |

The model needs a current observation and a comparable observation approximately one year earlier.

---

## 3. Population Estimates

### Accepted File Types

```text
.csv
.xlsx
```

### Recommended Source

U.S. Census Bureau City and Town Population Estimates.

The dashboard is designed to read the original Census table with approximately three title or metadata rows above the column headers.

### Expected Raw Structure

The first substantive column should identify the geographic area. Annual population columns should use four-digit year headings.

Example:

| Geographic area | 2020 | 2021 | 2022 |
|---|---:|---:|---:|
| Plano city, Texas | 285494 | 287677 | 289547 |

### Standardized Internal Structure

| Column | Type | Unit or format | Description |
|---|---|---|---|
| `City` | Text | City name | City or town associated with the estimate. |
| `State` | Text | Two-letter abbreviation | State associated with the city. |
| `Year` | Integer | `YYYY` | Population-estimate year. |
| `Population` | Number | People | Estimated city population. |

### History Requirement

At least three annual observations are required to calculate:

- Population compound annual growth
- Most recent annual growth
- Previous annual growth
- Population-growth acceleration

Use one Census vintage consistently. Do not combine annual estimates from different vintages.

### Current State-Name Support

The current population import code directly maps these full state names:

- Arizona
- California
- Colorado
- Florida
- Georgia
- North Carolina
- South Carolina
- Tennessee
- Texas

Using another state may require adding its full name and abbreviation to the `STATE_ABBREVIATIONS` mapping in `raw_data_pipeline.py`.

---

## 4. Residential Building Permits

### Accepted File Types

```text
.csv
.txt
```

Multiple files may be uploaded. One annual file should be uploaded for each year included in the analysis.

### Recommended Source

U.S. Census Bureau Building Permits Survey place-level annual data.

For a recent multiyear analysis, use the annual place files for 2020 through 2025.

Example file naming pattern:

```text
we2025a.txt
```

In this example:

- `we` identifies the Census region.
- `2025` identifies the year.
- `a` indicates annual totals.

### Standardized Internal Structure

| Column | Type | Unit or format | Description |
|---|---|---|---|
| `City` | Text | City name | City associated with the permit record. |
| `State` | Text | Two-letter abbreviation | State associated with the city. |
| `Year` | Integer | `YYYY` | Permit year. |
| `Total_Units` | Number | Residential units | Total residential housing units authorized by permits. |

Permit activity is converted into permitted units per 1,000 residents so differently sized cities can be compared more fairly.

---

# Calculated Market Features

The original source files are converted into the following market-level measurements.

| Feature | Unit | Description |
|---|---|---|
| `Latest_ZHVI` | U.S. dollars | Most recent Zillow home-value estimate. |
| `Five_Yr_CAGR_Pct` | Percentage | Annualized home-value growth over approximately five years. |
| `ZHVI_YoY_Pct` | Percentage | Home-value change from approximately one year earlier. |
| `Latest_Population` | People | Most recent available population estimate. |
| `Population_CAGR_Pct` | Percentage | Annualized population growth across the uploaded period. |
| `Population_Growth_Acceleration` | Percentage points | Most recent annual population growth minus the prior annual growth rate. |
| `Homes_Sold_YoY_Pct` | Percentage | Change in homes sold from approximately one year earlier. |
| `Inventory_YoY_Pct` | Percentage | Change in inventory from approximately one year earlier. |
| `Months_of_Supply` | Months | Most recent months-of-supply measurement. |
| `Sale_to_List_Pct` | Percentage | Most recent sale-to-list ratio. |
| `Latest_Permits_Per_1000` | Units per 1,000 residents | Latest annual permitted units normalized by population. |
| `Avg_Permits_Per_1000` | Units per 1,000 residents | Average annual permitted units normalized by the latest population. |

Building-permit measurements provide contextual construction information. They are displayed in the market analysis but are not currently included directly in the fundamentals or momentum score formulas.

---

# Date and Number Formatting

## Recommended Date Format

Use ISO dates whenever a manually prepared file is uploaded:

```text
YYYY-MM-DD
```

Example:

```text
2025-06-30
```

The dashboard uses automatic date parsing, but ISO formatting is the least ambiguous.

## Year Format

Use four-digit whole years:

```text
2020
2021
2022
```

## Percentages

Store percentage values as the displayed percentage rather than a decimal fraction.

Correct:

```text
98.5
```

Not recommended:

```text
0.985
```

## Numeric Values

Numeric measurements may contain commas, currency symbols, or percentage symbols because the standardization process attempts to remove common formatting characters. Plain numeric values remain the safest format.

---

# Geographic Compatibility

All original source files must use city-level observations.

A market is eligible for analysis only when it appears in:

- Home-value history
- Market activity
- Population estimates
- Building permits

The dashboard uses the intersection of the four sources. A city missing from any source is excluded.

At least three fully matched cities are required because the model performs comparative scoring and ranking.

Scores are relative to the cities selected for the current analysis. Changing the cities in the comparison group may change every market’s score and rank.