# CollegeTownIQ Analysis Report

## 1. Research Question

CollegeTownIQ investigates how housing affordability and accessibility interact across the State College, Pennsylvania study area.

The primary analytical question is:

> Is housing cost associated with access to public transportation after accounting for observable area-level differences in household income and vehicle access?

The project focuses on tradeoffs between affordability and accessibility rather than identifying a universally "best" neighborhood.

---

## 2. Study Area

The study area consists of five municipalities in the State College region:

- State College Borough
- College Township
- Ferguson Township
- Harris Township
- Patton Township

Census tracts were included when their geographic boundaries intersected the study-area boundary.

The final study area contains:

- 28 census tracts
- 25 complete observations for the regression analysis

Three tracts were excluded from the regression because one or more required analytical variables were unavailable.

---

## 3. Data Sources

### Housing and socioeconomic data

2024 American Community Survey 5-Year data from the U.S. Census Bureau were used for:

- Median gross rent
- Median household income
- Median rent burden
- Household vehicle availability

### Transit data

The Centre Area Transportation Authority (CATA) GTFS feed was used for:

- Transit stops
- Scheduled trips
- Scheduled stop events
- Transit network accessibility

### Food accessibility

The USDA Food Access Research Atlas SNAP-authorized Retailer Access Map was used for area-level food-access measures.

### Geographic data

2024 Census TIGER/Line census tract boundaries and Centre County GIS municipal boundaries were used to establish the study geography.

---

## 4. Transit Accessibility Methodology

Two approaches were evaluated.

### Straight-line accessibility

A regular sampling grid was generated within each census tract. For each sampled point, the straight-line distance to the nearest CATA transit stop was calculated.

The primary straight-line analysis used 250-meter sampling.

A 500-meter sampling grid was evaluated as a sensitivity test.

The two sampling resolutions produced highly similar results, with a correlation of approximately 0.9999 between tract-level accessibility measures.

### Network accessibility

A pedestrian street network was constructed using OpenStreetMap data and OSMnx.

The network contained approximately:

- 25,888 nodes
- 72,952 edges

CATA stops were mapped to the pedestrian network and shortest-path distances were calculated.

The 250-meter sampled straight-line measure was used for the primary housing-accessibility regression.

---

## 5. Accessibility Method Comparison

The network and straight-line measures were strongly related but not identical.

### Straight-line accessibility

Median tract-level distance:

- Mean: approximately 2,320 m
- Median: approximately 378 m
- Maximum: approximately 12,406 m

### Network accessibility

Median tract-level distance:

- Mean: approximately 2,651 m
- Median: approximately 638 m
- Maximum: approximately 13,425 m

Comparison:

- Mean absolute difference: approximately 863 m
- Median absolute difference: approximately 176 m
- Mean network/straight-line ratio: approximately 1.38
- Median network/straight-line ratio: approximately 1.45
- Correlation: approximately 0.90

This demonstrates why network distance provides additional information beyond simple Euclidean distance.

---

## 6. Housing Cost Model

The primary regression modeled tract-level median gross rent as a function of:

- 250-meter sampled straight-line transit distance
- Median household income
- Vehicle access

The regression used 25 complete observations.

Predictors were rescaled for interpretability:

- Transit distance was measured in kilometers.
- Household income was measured in $10,000 units.

Heteroskedasticity-consistent HC3 standard errors were used.

---

## 7. Primary Regression Results

The model produced:

- R²: 0.190
- Adjusted R²: 0.075
- Observations: 25

The estimated transit coefficient was:

**−$35.40 per additional kilometer**

with:

- Robust p-value: 0.0066
- 95% confidence interval: [−$60.97, −$9.84]

The income coefficient was:

**−$2.56 per additional $10,000 of median household income**

with:

- Robust p-value: 0.953
- 95% confidence interval: [−$88.52, $83.39]

The vehicle-access coefficient was:

**+$5.26 per percentage-point increase in vehicle access**

with:

- Robust p-value: 0.575
- 95% confidence interval: [−$13.13, $23.65]

---

## 8. Multicollinearity Diagnostics

Variance Inflation Factors were calculated for the three predictors.

| Predictor | VIF |
|---|---:|
| Transit distance | 1.47 |
| Median household income | 3.80 |
| Vehicle access | 4.56 |

Transit distance showed relatively little overlap with the other predictors.

Income and vehicle access showed greater overlap, consistent with their observed correlation of approximately 0.83.

The model therefore requires caution when interpreting the individual coefficients for income and vehicle access.

---

## 9. Spatial Residual Diagnostics

Spatial autocorrelation of the regression residuals was evaluated using Moran's I with a queen-neighbor spatial structure.

Results:

- Moran's I: −0.1142
- Expected Moran's I: −0.0417
- Permutation p-value: 0.2830

No statistically significant spatial autocorrelation was detected in the regression residuals under this specification.

This reduces concern that the regression residuals exhibit strong remaining spatial clustering under the tested specification.

---

## 10. Influence Diagnostics

Cook's distance identified two observations with substantially greater influence on the fitted model:

- GEOID 42027011903: Cook's distance ≈ 0.709
- GEOID 42027012300: Cook's distance ≈ 0.424

These observations were not automatically removed.

Instead, a leave-one-out sensitivity analysis was performed.

---

## 11. Leave-One-Out Sensitivity Analysis

| Specification | N | Transit coefficient | p-value | 95% CI |
|---|---:|---:|---:|---|
| All observations | 25 | −35.40 | 0.0066 | [−60.97, −9.84] |
| Remove 42027011903 | 24 | −36.05 | 0.0153 | [−65.18, −6.92] |
| Remove 42027012300 | 24 | −32.70 | 0.0157 | [−59.22, −6.17] |
| Remove both | 23 | −33.96 | 0.0105 | [−59.98, −7.95] |

The estimated transit coefficient remained within a relatively narrow range across all four specifications.

Removing both highly influential observations did not eliminate the observed association.

This indicates that the direction and approximate magnitude of the estimated transit relationship are not dependent solely on those two observations.

---

## 12. Accessibility Sensitivity Analysis

The housing regression was also evaluated using the 250-meter and 500-meter straight-line accessibility calculations.

### 250-meter sampling

- Transit coefficient: −0.0354
- Robust p-value: 0.0066
- R²: 0.1902

### 500-meter sampling

- Transit coefficient: −0.0353
- Robust p-value: 0.0071
- R²: 0.1885

The estimated coefficient and model fit were nearly unchanged.

This provides evidence that the straight-line accessibility results are not highly sensitive to the selected sampling resolution.

---

## 13. Main Research Finding

Within the 25 complete census-tract observations analyzed, greater 250-meter sampled straight-line distance to public transit was associated with lower tract-level median gross rent after accounting for median household income and vehicle access.

The estimated association was approximately:

> **$35 lower median gross rent per additional kilometer of 250-meter sampled straight-line transit distance.**

The estimated relationship remained similar when the two most influential observations were excluded.

---

## 14. Interpretation

The results are consistent with an affordability-accessibility tradeoff within the study area: areas with greater distance from public transit tended to have lower median gross rents in the analyzed data.

However, this analysis does not establish that transit accessibility causes housing prices to change.

Other factors may influence both housing costs and transit accessibility, including:

- Housing characteristics
- Neighborhood characteristics
- Location
- Land use
- Student concentration
- Development patterns
- Unobserved socioeconomic factors

The analysis should therefore be interpreted as an observational association rather than a causal estimate.

---

## 15. What the Analysis Does Not Claim

CollegeTownIQ does not claim that:

- Moving farther from transit will necessarily reduce an individual's rent.
- Transit accessibility causes housing prices to increase or decrease.
- One census tract is universally better than another.
- Census-tract averages represent individual households.
- The regression provides a prediction of an individual's rent.
- The study identifies the objectively best place for students to live.

The project instead presents measurable differences and tradeoffs across locations.

---

## 16. Key Limitations

### Sample size

The regression contains only 25 complete observations. Statistical estimates should therefore be interpreted cautiously.

### Geographic aggregation

The analysis uses census-tract-level data. Relationships observed across tracts may not apply directly to individual households.

### Transit accessibility

The network measure represents modeled pedestrian network distance to transit stops. It is not equivalent to actual travel time, service quality, frequency experienced by an individual, or door-to-door accessibility.

### Study-area boundaries

Some census tracts intersect the study-area boundary rather than falling completely inside it.

### Housing data

ACS median rent represents an area-level statistical measure rather than individual rental listings.

### Observational design

The analysis identifies associations and does not establish causal relationships.

---

## 17. Project Philosophy

CollegeTownIQ intentionally avoids collapsing all dimensions into a single arbitrary "best neighborhood" score.

Instead, the project separates:

- Housing affordability
- Transit accessibility
- Food accessibility
- Vehicle access
- Household economic characteristics

This allows users to examine tradeoffs directly and apply their own priorities.

---

## 18. Reproducibility

The project uses reproducible Python scripts for:

- Data ingestion
- Data cleaning
- Geographic processing
- Transit-network construction
- Accessibility calculation
- Statistical analysis
- Diagnostics
- Sensitivity analysis
- Dashboard data export

Raw and processed datasets are separated from source code through the project directory structure and Git configuration.

---

## 19. Current Analytical Conclusion

The evidence supports a consistent descriptive and multivariable association between transit accessibility and housing cost across the analyzed State College-area census tracts.

The relationship survives:

1. Robust standard errors
2. Multicollinearity diagnostics
3. Spatial residual diagnostics
4. Influence diagnostics
5. Leave-one-out sensitivity analysis
6. Accessibility-resolution sensitivity analysis

The result should nevertheless remain framed as an **area-level observational association**, not a causal effect or individual-level prediction.