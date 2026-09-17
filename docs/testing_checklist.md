# Dashboard Testing Checklist

## Purpose

Use this checklist after changing the dashboard, scoring model, upload pipeline, dependencies, or deployment configuration.

Record the test date, environment, result, and any unresolved issue.

---

## Test Information

- Tester:
- Test date:
- Branch or commit:
- Python version:
- Streamlit version:
- Environment:
  - [ ] Local
  - [ ] Streamlit Community Cloud
- Browser:
- Dashboard URL:

---

# 1. Application Startup

- [ ] The application starts without a Python traceback.
- [ ] The application loads without a blank page.
- [ ] `dashboard/client_app.py` is the active Streamlit entry point.
- [ ] All required packages install successfully.
- [ ] PDF dependencies load without a `reportlab` error.
- [ ] The Streamlit theme and custom formatting load correctly.
- [ ] No text is unreadable against the background.
- [ ] Navigation controls are visible.
- [ ] The application works after a full browser refresh.

Expected result:

The landing page loads and allows the user to select a dataset path.

---

# 2. Included North Dallas Data

- [ ] Select `Use included North Dallas data`.
- [ ] The dashboard confirms that the included dataset is ready.
- [ ] The number of available markets is displayed.
- [ ] No upload controls are required.
- [ ] Select `Generate Investment Strategy`.
- [ ] The strategy page opens successfully.
- [ ] Fundamentals and momentum weights can be changed.
- [ ] The dashboard requires the two primary weights to total 100%.
- [ ] Robustness emphasis can be adjusted.
- [ ] The analysis can be generated without an error.
- [ ] At least three results are displayed.
- [ ] Preference-match scores are numeric.
- [ ] Results are sorted from highest to lowest match score.
- [ ] Market names and scores match the included dataset.

Expected result:

The original North Dallas analysis remains fully usable without uploading files.

---

# 3. Valid Market-Scoring Upload

Use:

```text
demo/valid_market_scoring_sample.csv
```

- [ ] Select `Upload a market scoring file`.
- [ ] Upload the valid demonstration CSV.
- [ ] The file preview appears.
- [ ] The displayed row count is correct.
- [ ] The displayed column count is correct.
- [ ] Select `Check Dataset`.
- [ ] Required-columns validation passes.
- [ ] Market-coverage validation passes.
- [ ] City-record validation passes.
- [ ] Numeric-formatting validation passes.
- [ ] Score-range validation passes.
- [ ] The dashboard displays the approved-dataset message.
- [ ] The user can continue to strategy selection.
- [ ] Match scores can be generated.
- [ ] The three sample markets appear in the results.

Expected result:

The valid file passes all checks and proceeds to analysis.

---

# 4. Invalid Market-Scoring Upload

Use:

```text
demo/invalid_market_scoring_sample.csv
```

- [ ] Upload the invalid demonstration CSV.
- [ ] Select `Check Dataset`.
- [ ] The dashboard detects the duplicate city.
- [ ] The dashboard detects the nonnumeric ranking value.
- [ ] The dashboard detects the score outside the 0–100 range.
- [ ] The dataset is not approved.
- [ ] The user cannot continue to strategy selection.
- [ ] The error messages identify the relevant problem.
- [ ] The application remains running after validation fails.

Expected result:

The invalid file fails validation without crashing the application.

---

# 5. Original Source-File Upload

Select:

```text
Build from original source files
```

## Home-Value File

- [ ] The upload accepts a `.csv` file.
- [ ] A city-level Zillow ZHVI file can be uploaded.
- [ ] Monthly date columns are recognized.
- [ ] City and state columns are recognized.
- [ ] At least five years of history are present.
- [ ] Home values are converted to numeric values.
- [ ] Duplicate city-date records are handled.
- [ ] Invalid or ambiguous markets are excluded appropriately.

## Market-Activity File

- [ ] The upload accepts a `.csv` file.
- [ ] A city-level Redfin file can be uploaded.
- [ ] A large Redfin file is read in chunks without crashing the application.
- [ ] `REGION TYPE` correctly filters to city records.
- [ ] `REGION NAME` is separated into city and state.
- [ ] `PERIOD END` is parsed as a date.
- [ ] `HOMES SOLD` is recognized.
- [ ] `INVENTORY` or `ACTIVE LISTINGS` is recognized.
- [ ] `MONTHS OF SUPPLY` is recognized.
- [ ] `AVERAGE SALE TO LIST RATIO (%)` is recognized.

## Population File

- [ ] The upload accepts `.csv`.
- [ ] The upload accepts `.xlsx`.
- [ ] The original Census title rows are skipped correctly.
- [ ] Four-digit annual columns are recognized.
- [ ] Geographic-area names are separated into city and state.
- [ ] Population values are converted to numeric values.
- [ ] The newest available Census vintage works.
- [ ] Files from different Census vintages are not combined.

## Building-Permit Files

- [ ] The upload accepts `.txt`.
- [ ] The upload accepts `.csv`.
- [ ] Multiple annual files can be selected.
- [ ] The year is identified correctly for each file.
- [ ] City and state values are extracted correctly.
- [ ] Total permitted units are numeric.
- [ ] Duplicate market-year records are removed.
- [ ] The selected files cover the intended date range.

## Cross-Source Validation

- [ ] Required-column checks pass for all four sources.
- [ ] City and state identity checks pass.
- [ ] Duplicate-record checks pass.
- [ ] Numeric-value checks pass.
- [ ] Cross-source coverage is calculated.
- [ ] Excluded cities are identified.
- [ ] At least three cities appear in every source.
- [ ] The model creates the market feature table.
- [ ] Fundamentals scores are calculated.
- [ ] Momentum scores are calculated.
- [ ] The 10,000-run robustness analysis completes.
- [ ] The approved market count is displayed.

Expected result:

The four source categories are standardized, validated, joined, scored, and made available for city selection.

---

# 6. City Selector

- [ ] The city selector appears after original source files are approved.
- [ ] `All markets` is selected by default.
- [ ] The correct total number of compatible markets is displayed.
- [ ] Select `Select specific cities`.
- [ ] The city-search field appears.
- [ ] The list contains only compatible city-state combinations.
- [ ] Search returns the expected city.
- [ ] Multiple cities can be selected.
- [ ] Selected cities remain visible.
- [ ] Fewer than three selected cities produces a warning.
- [ ] The continue button is disabled when fewer than three cities are selected.
- [ ] Three or more selected cities enables the continue button.
- [ ] Only selected cities appear in the analysis.
- [ ] Scores and ranks are recalculated for the selected comparison group.
- [ ] Switching back to `All markets` restores all compatible markets.

Expected result:

The user can analyze all compatible cities or a selected group of at least three.

---

# 7. Investment Strategy Controls

- [ ] Fundamentals and momentum weights are visible.
- [ ] The weights must total 100%.
- [ ] Invalid totals generate a clear warning.
- [ ] The analysis button is unavailable or ineffective until the total is valid.
- [ ] Robustness emphasis is visible.
- [ ] Robustness does not exceed the intended maximum of 30%.
- [ ] Conservative Growth selection works.
- [ ] Balanced selection works.
- [ ] Momentum selection works.
- [ ] Custom weights work.
- [ ] Strategy changes produce understandable ranking changes.

Expected result:

The selected priorities alter the preference-match score without altering the underlying source data.

---

# 8. Results and Comparison

- [ ] The best overall match appears first.
- [ ] At least two alternatives are displayed when available.
- [ ] Each result displays the city.
- [ ] Each result displays the preference-match score.
- [ ] Each result displays the fundamentals score.
- [ ] Each result displays the momentum score.
- [ ] Each result displays top-three probability.
- [ ] Primary strengths are displayed.
- [ ] Main considerations are displayed.
- [ ] Comparison cards align correctly.
- [ ] Long city names do not overlap.
- [ ] Scores use consistent decimal formatting.
- [ ] No duplicate result cards appear.
- [ ] No duplicate Streamlit element-key error appears.

Expected result:

The results are readable, correctly ordered, and suitable for presentation to a client or investor.

---

# 9. Market Deep Dive and Charts

- [ ] The `Explore One Market` selector loads.
- [ ] Every analyzed market is available.
- [ ] Selecting a different market updates the page.
- [ ] Five-year home-value CAGR displays.
- [ ] Population CAGR displays.
- [ ] Homes-sold year-over-year change displays.
- [ ] Months of supply displays.
- [ ] The home-value chart contains visible data.
- [ ] The home-value chart uses the selected city.
- [ ] The population chart contains visible data.
- [ ] The construction chart contains visible data.
- [ ] Date and year axes display correctly.
- [ ] Dollar, percentage, population, and permit units are labeled correctly.
- [ ] Tooltips display understandable values.
- [ ] Charts remain visible on the dark background.
- [ ] Empty charts display an explanatory message instead of silently failing.
- [ ] Uploaded source data is used for uploaded-market charts.
- [ ] Included North Dallas data is used for included-market charts.

Expected result:

Every deep-dive chart uses the selected market’s relevant time-series data.

---

# 10. Warning Factors

- [ ] Inventory growth above 10% produces a high-priority warning.
- [ ] Months of supply above 5 produces a high-priority warning.
- [ ] Negative homes-sold growth produces a monitoring warning.
- [ ] Sale-to-list percentage below 98% produces a monitoring warning.
- [ ] Each warning includes an interpretation.
- [ ] Each warning includes a recommended next step.
- [ ] A market with no triggered threshold receives routine-monitoring guidance.
- [ ] Warning text remains readable.
- [ ] Warning cards do not overlap or repeat unexpectedly.

Expected result:

Warnings clearly identify both the condition and an appropriate due-diligence response.

---

# 11. PDF Download

- [ ] `reportlab` imports without an error.
- [ ] The client-comparison download button is visible.
- [ ] The button has a unique Streamlit key.
- [ ] Selecting the button generates a PDF.
- [ ] The downloaded file opens successfully.
- [ ] The PDF includes the selected strategy.
- [ ] The PDF includes the compared markets.
- [ ] Market names are correct.
- [ ] Preference-match scores are correct.
- [ ] Fundamentals scores are correct.
- [ ] Momentum scores are correct.
- [ ] Top-three probabilities are correct.
- [ ] Warnings or considerations are included where intended.
- [ ] Text does not extend outside the page.
- [ ] Tables do not overlap.
- [ ] Page breaks occur in sensible locations.
- [ ] The PDF filename is clear and descriptive.
- [ ] Repeated downloads do not produce a duplicate-element error.

Expected result:

A readable, client-ready PDF is downloaded without interrupting the dashboard.

---

# 12. Responsive and Visual Testing

Test at desktop and narrow browser widths.

- [ ] Page content remains centered.
- [ ] Cards stack correctly on smaller screens.
- [ ] Upload controls remain usable.
- [ ] Tables remain readable or horizontally scrollable.
- [ ] Charts resize correctly.
- [ ] Buttons remain visible.
- [ ] No content is cut off.
- [ ] Navigation remains usable.
- [ ] Text has sufficient color contrast.
- [ ] Hover and focus states are visible.

---

# 13. Streamlit Community Cloud

- [ ] The latest GitHub commit is deployed.
- [ ] The correct repository and branch are selected.
- [ ] The entry point is `dashboard/client_app.py`.
- [ ] `requirements.txt` is located at the repository root.
- [ ] `reportlab` is included in `requirements.txt`.
- [ ] `openpyxl` is included in `requirements.txt`.
- [ ] The app starts after rebooting.
- [ ] The included dataset works online.
- [ ] A valid scoring CSV works online.
- [ ] Raw uploads remain within the hosting limits.
- [ ] Large uploads do not exceed available memory.
- [ ] PDF generation works online.
- [ ] No secrets or local file paths are exposed.

---

# Test Summary

## Passed

-

## Failed

-

## Known Limitations

-

## Required Follow-Up

-

## Final Decision

- [ ] Ready to deploy
- [ ] Ready with documented limitations
- [ ] Not ready to deploy
