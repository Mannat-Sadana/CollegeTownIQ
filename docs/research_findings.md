# CollegeTownIQ Research Findings

This report summarizes the descriptive, geospatial, and statistical analysis performed on the CollegeTownIQ State College study area.

**Important:** These results describe associations among observed tract-level measures. They do not establish causal relationships.

## 1. Study Coverage

- Study-area observations: **28 census tracts**
- Complete observations used in the primary statistical model: **25**
- Geographic unit: 2024 Census tracts intersecting the CollegeTownIQ study area
- Study area: State College Borough, College Township, Ferguson Township, Harris Township, and Patton Township

## 2. Housing Affordability

- Median tract-level gross rent: **$1,214 per month**
- Median tract-level household income: **$84,063 annually**
- Rent burden is retained as a secondary housing measure.
- Observed median gross rent ranged from **$674** to **$1,924**

The tract-level gross-rent measure is an area-level statistic and should not be interpreted as the rent paid by every household in a tract.

## 3. Transit Accessibility

The primary accessibility measure is a **250-meter sampled straight-line distance** to the nearest CATA transit stop.

A 500-meter sampling resolution was evaluated as a sensitivity check.

- The primary model uses the 250m sampled straight-line measure.
- A separate pedestrian-network analysis provides a different accessibility perspective.
- Straight-line and network measures are kept conceptually separate because they represent different accessibility assumptions.

- Median primary transit-distance measure: **423.3 meters**

## 4. Food Access

USDA Food Access Research Atlas / SRAM measures were integrated as a separate essential-service accessibility dimension.

The project retains both straight-line and network-based food-access measures rather than treating them as interchangeable.

Food access is used as a complementary analysis rather than as a predictor in the primary gross-rent regression.

## 5. Descriptive Relationships

Pearson correlations are used to describe relationships among tract-level variables.

- Median gross rent vs. 250m sampled straight-line transit distance: **r = -0.391**
- Median gross rent vs. median household income: **r = 0.092**
- Median rent burden vs. median household income: **r = -0.728**
- Median rent burden vs. 250m sampled straight-line transit distance: **r = -0.410**

These are descriptive associations and should not be interpreted as causal effects.

## 6. Primary Multivariable Regression

The primary model estimates the association between tract-level median gross rent and transit accessibility while controlling for median household income and vehicle access.

- Observations: **25**
- R²: **0.190**
- Adjusted R²: **0.075**
- Overall F-test p-value: **0.0671**

| Predictor | Coefficient | Robust p-value |
|---|---:|---:|
| Transit distance (km) | **-35.404** | **0.0066** |
| Household income ($10,000s) | -2.562 | 0.953 |
| Vehicle access (%) | 5.260 | 0.575 |

The estimated coefficient for transit distance corresponds to approximately **$35 lower tract-level median gross rent per additional kilometer of the 250-meter sampled straight-line transit-distance measure**, conditional on the other included variables.

This is an association at the census-tract level, not evidence that increasing or decreasing transit access causes rents to change.

## 7. Influence and Sensitivity Analysis

- GEOID `42027011903`: Cook's distance ≈ **0.709**
- GEOID `42027012300`: Cook's distance ≈ **0.424**

The transit-distance association remained similar when these observations were removed individually or together.

| Scenario | Observations | Transit coefficient | p-value |
|---|---:|---:|---:|
| All observations | 25 | -35.40 | 0.0066 |
| Remove 42027011903 | 24 | -36.05 | 0.0153 |
| Remove 42027012300 | 24 | -32.70 | 0.0157 |
| Remove both | 23 | -33.96 | 0.0105 |

## 8. Spatial Residual Diagnostics

- Observations: **25**
- Neighborhood definition: **Queen contiguity**
- Average neighbors: **5.04**
- Moran's I: **-0.1142**
- Permutation p-value: **0.2700**

The selected test did not detect statistically significant spatial autocorrelation in the primary regression residuals.

## 9. Secondary Accessibility Analysis

- Pedestrian-network transit accessibility
- Food-access measures
- Alternative spatial sampling resolutions
- Transit accessibility method differences

These analyses provide methodological context and sensitivity checks but are not substituted for the primary gross-rent model.

## 10. Interpretation

Within the analyzed State College study area, tracts with greater sampled straight-line distance to CATA transit stops tended to have lower median gross rents after accounting for median household income and vehicle access.

The result should be interpreted as an **observed tract-level association**. It does not establish that transit accessibility causes housing costs to increase or decrease.

The project therefore focuses on identifying **tradeoffs and spatial patterns** rather than producing a universal ranking of neighborhoods.

## 11. Important Limitations

- The analysis uses census-tract-level data rather than individual households.
- Only 25 complete observations are available for the primary regression.
- Several ACS variables are unavailable for three study-area tracts.
- The study area contains only 28 tracts, limiting statistical precision.
- Straight-line transit distance is not equivalent to walking distance or travel time.
- The pedestrian-network analysis provides a separate accessibility perspective but does not model individual travel behavior.
- Food-access measures come from the USDA food-access framework and do not represent every dimension of food availability, quality, or affordability.
- Some census tracts cross municipal boundaries because the study-area inclusion rule is based on geographic intersection.
- Associations should not be interpreted as causal effects.
- The project does not produce a universal "best neighborhood" score.

## 12. Reproducibility

The primary findings are generated from the CollegeTownIQ processed analysis dataset and can be reproduced using the analysis scripts in `src/analysis/`.

Key reproducible components include:

- Primary affordability-accessibility regression
- Regression diagnostics
- Cook's-distance influence analysis
- Leave-out sensitivity analysis
- Spatial residual diagnostics
- Transit accessibility sensitivity analysis

The repository keeps analytical methods separate from generated outputs so that results can be regenerated when underlying data or methodology changes.
