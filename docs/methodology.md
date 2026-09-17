# Methodology

## Overview

Market Match is a comparative housing-market screening model. It evaluates cities across three dimensions:

1. Long-term market fundamentals
2. Current market momentum
3. Ranking robustness

The dashboard then combines these dimensions according to the investor’s selected priorities.

The output is intended to support market screening and due diligence. It is not a forecast of investment returns, property-level performance, rent growth, or resale profit.

---

# 1. Data Preparation

The model combines four city-level sources:

- Zillow home-value history
- Redfin market activity
- U.S. Census population estimates
- U.S. Census residential building permits

City and state names are standardized, and a market identifier is created:

```text
Market_ID = City + ", " + State
```

Example:

```text
Plano, TX
```

A market is retained only when it appears in all four sources. At least three fully matched markets are required.

Duplicate city-period records, blank identities, nonnumeric measurements, and incompatible geographic levels may prevent a source file from passing validation.

---

# 2. Feature Calculation

## Home-Value Measurements

### Five-Year Home-Value CAGR

The five-year compound annual growth rate estimates annualized home-value growth:

```text
Five-Year CAGR
= ((Latest Home Value / Starting Home Value)^(1 / 5) − 1) × 100
```

### Home-Value Year-over-Year Change

```text
ZHVI YoY %
= ((Latest Home Value / Prior-Year Home Value) − 1) × 100
```

---

## Population Measurements

### Population CAGR

```text
Population CAGR
= ((Latest Population / Starting Population)^(1 / Number of Years) − 1) × 100
```

### Population-Growth Acceleration

```text
Population-Growth Acceleration
= Latest Annual Population Growth
− Previous Annual Population Growth
```

A positive result indicates that population growth accelerated. A negative result indicates deceleration.

---

## Market-Activity Measurements

### Homes-Sold Year-over-Year Change

```text
Homes Sold YoY %
= ((Latest Homes Sold / Prior-Year Homes Sold) − 1) × 100
```

### Inventory Year-over-Year Change

```text
Inventory YoY %
= ((Latest Inventory / Prior-Year Inventory) − 1) × 100
```

The model also uses the latest:

- Months of supply
- Sale-to-list percentage

---

## Residential Construction Measurements

### Latest Permits per 1,000 Residents

```text
Latest Permits per 1,000
= Latest Permitted Units / Latest Population × 1,000
```

### Average Permits per 1,000 Residents

```text
Average Permits per 1,000
= Average Annual Permitted Units / Latest Population × 1,000
```

Construction measurements are displayed as market context. They do not currently contribute directly to the fundamentals or momentum scores.

---

# 3. Score Standardization

The model converts market measurements into comparable scores from 0 to 100 using min-max scaling.

For a variable where a higher value is preferred:

```text
Score
= (Market Value − Minimum Value)
  / (Maximum Value − Minimum Value)
  × 100
```

For a variable where a lower value is preferred:

```text
Reverse Score
= (Maximum Value − Market Value)
  / (Maximum Value − Minimum Value)
  × 100
```

If every market has the same value for a measurement, each market receives a neutral score of 50 for that measurement.

Because the scores use min-max scaling, they are relative to the markets included in the current analysis. They are not fixed national benchmarks.

---

# 4. Long-Term Fundamentals Score

The fundamentals score evaluates longer-term demographic and home-value growth.

```text
Long-Term Fundamentals Score
= 45% × Population CAGR Score
+ 35% × Five-Year Home-Value CAGR Score
+ 20% × Population-Growth Acceleration Score
```

## Interpretation

A higher score indicates stronger long-term performance relative to the other selected markets.

The score emphasizes:

- Sustained population growth
- Sustained home-value appreciation
- Improving demographic growth

## Fundamentals Rank

Markets are ranked from highest to lowest fundamentals score:

```text
1 = strongest fundamentals score
```

Tied values receive the same minimum rank.

---

# 5. Current Market Momentum Score

The momentum score evaluates more recent housing-market conditions.

```text
Current Market Momentum Score
= 25% × ZHVI YoY Score
+ 20% × Homes-Sold YoY Score
+ 20% × Reverse Inventory YoY Score
+ 20% × Reverse Months-of-Supply Score
+ 15% × Sale-to-List Score
```

Higher values are treated as favorable for:

- Home-value growth
- Homes-sold growth
- Sale-to-list ratio

Lower values are treated as favorable for:

- Inventory growth
- Months of supply

The inventory and supply variables are therefore reverse-scored.

## Momentum Rank

Markets are ranked from highest to lowest momentum score:

```text
1 = strongest momentum score
```

---

# 6. Ranking-Robustness Analysis

A market may rank highly under one set of weights but fall substantially when investor assumptions change. The robustness simulation tests this sensitivity.

The model performs:

```text
10,000 simulations
```

A fixed random seed of `42` is used so the same input data produces reproducible results.

During each simulation:

1. The three fundamentals variables receive randomly generated weights that sum to 100%.
2. The five momentum variables receive randomly generated weights that sum to 100%.
3. The total fundamentals share is randomly selected between 30% and 70%.
4. The momentum share equals the remaining percentage.
5. Every market receives a simulated composite score.
6. Markets are ranked for that simulation.

## Top-Three Probability

```text
Pct_Top_3
= Simulations Ranked in Top Three
  / Total Simulations
  × 100
```

A higher result indicates that the market remains competitive under a wider range of assumptions.

## Average Rank

```text
Average_Rank
= Mean Rank Across All Simulations
```

A lower average rank is stronger.

## Robustness Profiles

| Top-three probability | Classification |
|---:|---|
| 75% or higher | `Highly Robust` |
| 40% to less than 75% | `Moderately Robust` |
| 15% to less than 40% | `Weight Sensitive` |
| Less than 15% | `Consistently Lower Ranked` |

Robustness measures ranking consistency. It does not measure forecast certainty or the probability of earning a return.

---

# 7. Market Regime

The market regime combines fundamentals and momentum scores.

| Fundamentals | Momentum | Classification |
|---:|---:|---|
| 50 or higher | 50 or higher | `Strong / Expanding` |
| 50 or higher | Below 50 | `Long-Term Strength / Near-Term Pressure` |
| Below 50 | 50 or higher | `Momentum-Led / Developing Fundamentals` |
| Below 50 | Below 50 | `Weak / Transitional` |

The classifications summarize current model conditions and are not economic forecasts.

---

# 8. Investor Preference-Match Score

Users select:

- Fundamentals weight
- Momentum weight
- Robustness emphasis

The fundamentals and momentum weights must total 100%.

## Base Preference Score

```text
Base Preference Score
= Fundamentals Weight × Long-Term Fundamentals Score
+ Momentum Weight × Current Market Momentum Score
```

The percentage weights are converted to decimal shares before the calculation.

## Final Preference-Match Score

```text
Preference-Match Score
= (1 − Robustness Share) × Base Preference Score
+ Robustness Share × Top-Three Probability
```

The dashboard allows robustness to influence up to 30% of the final score.

## Preference Rank

Markets are ranked from highest to lowest preference-match score.

The preference-match score reflects alignment with the selected strategy. It is not a predicted return, appreciation rate, or probability of investment success.

---

# 9. Warning Factors

The dashboard identifies conditions that may deserve additional due diligence.

## Inventory Growth

Trigger:

```text
Inventory YoY > 10%
```

Priority:

```text
High priority
```

Interpretation:

Inventory is expanding relatively quickly.

Suggested next step:

Review competing listings, expected time on market, and rent assumptions before making an offer.

---

## Months of Supply

Trigger:

```text
Months of Supply > 5
```

Priority:

```text
High priority
```

Interpretation:

Available housing supply may be placing pressure on sellers.

Suggested next step:

Use conservative appreciation assumptions and investigate price reductions, closing credits, or other seller concessions.

---

## Home-Sales Activity

Trigger:

```text
Homes Sold YoY < 0%
```

Priority:

```text
Monitor
```

Interpretation:

Transaction activity is below the prior-year level.

Suggested next step:

Confirm recent comparable sales and allow for a longer holding or resale period in the investment plan.

---

## Sale-to-List Ratio

Trigger:

```text
Sale-to-List Percentage < 98%
```

Priority:

```text
Monitor
```

Interpretation:

Sellers may be accepting larger discounts.

Suggested next step:

Compare recent asking and closing prices and consider negotiating below list price.

---

## No Threshold-Based Warning

When none of the thresholds are triggered, the dashboard displays a routine-monitoring message.

Suggested next step:

Continue normal due diligence and monitor inventory, sales activity, and pricing before acquisition.

Warnings are screening signals. They should not automatically disqualify a market.

---

# 10. Important Limitations

- Scores are relative to the selected comparison group.
- Adding or removing cities may change all scores and rankings.
- Min-max scaling can be sensitive to outliers.
- Source publication schedules may differ.
- Recent values may be revised by the source provider.
- City-wide results do not capture neighborhood-level differences.
- Building permits indicate authorized construction, not necessarily completed units.
- The model does not include property prices, rents, operating expenses, financing, taxes, insurance, or renovation costs at the individual-property level.
- The model does not produce forecasts of returns or appreciation.
- Warning thresholds are screening rules rather than universal investment standards.
- Results should be combined with property-level underwriting and local due diligence.