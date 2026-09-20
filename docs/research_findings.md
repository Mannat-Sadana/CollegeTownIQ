# CollegeTownIQ Research Findings

This report summarizes the descriptive and statistical analysis performed on the CollegeTownIQ State College study area.

**Important:** These results describe associations among the observed tract-level measures. They do not establish causal relationships.

## 1. Study Coverage

- Study-area observations: **28 census tracts**
- Complete observations used in the main statistical analysis: **25**
- Geographic unit: 2024 Census tracts intersecting the CollegeTownIQ study area
- Study area: State College Borough, College Township, Ferguson Township, Harris Township, and Patton Township

## 2. Housing Affordability

- Median tract-level gross rent across the analytical sample: **$1,214 per month**.
- Median tract-level household income: **$84,063 annually**.
- Median tract-level rent burden measure: **35.8%**.
- Observed median gross rent ranged from **$674** to **$1,924**.

## 3. Transit Accessibility

- Median tract-level sampled network transit distance: **639.4 meters**.
- Mean tract-level sampled network transit distance: **2,826.9 meters**.
- Range: **164.9 to 13,425.3 meters**.
- Transit accessibility is represented by the tract-level sampled network-distance measure used in the master dataset.

## 4. Food Access

- Median straight-line food-access measure: **61.0%**.
- Median network-based food-access measure: **87.7%**.
- Mean absolute difference between the two food-access methods in the 28-tract study area: **14.13 percentage points**.
- The straight-line and network measures are therefore not interchangeable and are retained separately.

## 5. Correlation Analysis

Pearson correlations are reported as descriptive associations, not causal effects.

- Rent burden vs. `food_access_beyond_half_mile_network_share`: **r = -0.711**
- Rent burden vs. `median_network_transit_distance_m`: **r = -0.453**
- Rent burden vs. `median_household_income`: **r = -0.728**
- Rent burden vs. `vehicle_access_pct`: **r = -0.697**

## 6. Multivariable Regression

The full model estimates the association between tract-level rent burden and food access, transit distance, household income, and vehicle access.

- Observations: **25**
- R²: **0.643**
- Adjusted R²: **0.572**

| Predictor | Coefficient | Robust p-value |
|---|---:|---:|
| `food_access_beyond_half_mile_network_share` | -0.1143 | 0.2135 |
| `median_network_transit_distance_m` | -0.0005 | 0.19 |
| `median_household_income` | -0.0001 | 0.2367 |
| `vehicle_access_pct` | -0.0338 | 0.8563 |

Coefficient signs describe the direction of the estimated association while holding the other included variables constant.

## 7. Model Diagnostics

- Heteroskedasticity-robust (HC3) standard errors were used for inference.
- Residual diagnostics and influence diagnostics were performed separately.
- Sensitivity analysis examined the effect of excluding observations with relatively high Cook's distance.
- The model should be interpreted cautiously because the analytical sample contains only 25 observations.

## 8. Important Limitations

- The analysis uses census-tract-level data rather than individual households.
- Several ACS variables are unavailable for three study-area tracts, reducing the complete-case sample.
- The study area contains only 28 tracts, so statistical estimates have limited precision.
- Transit accessibility is based on sampled spatial/network distance rather than observed individual travel behavior.
- Food-access measures come from the USDA food-access framework and should not be interpreted as a complete measure of food availability or food quality.
- The tract inclusion rule is based on geographic intersection with the study area, so some included tracts cross municipal boundaries.
- Associations in the regression models should not be interpreted as causal effects.
- The project does not produce a universal 'best neighborhood' score.

## 9. Reproducibility

The findings are generated programmatically from the CollegeTownIQ master dataset so that the analytical summary can be regenerated when the underlying data or methods change.
