# CollegeTownIQ Research Findings

This report summarizes the descriptive, geospatial, and statistical analysis performed on the CollegeTownIQ State College study area.

**Important:** These results describe associations among observed tract-level measures. They do not establish causal relationships.

## 1. Study Coverage

- Study-area observations: **23 census tracts**
- Complete observations used in the primary statistical model: **21**
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

- Median primary transit-distance measure: **311.2 meters**

## 4. Food Access

USDA Food Access Research Atlas / SRAM measures were integrated as a separate essential-service accessibility dimension.

The project retains both straight-line and network-based food-access measures rather than treating them as interchangeable.

Food access is used as a complementary analysis rather than as a predictor in the primary gross-rent regression.

## 5. Descriptive Relationships

Pearson correlations are used to describe relationships among tract-level variables.

- Median gross rent vs. 250m sampled straight-line transit distance: **r = 0.076**
- Median gross rent vs. median household income: **r = 0.140**
- Median rent burden vs. median household income: **r = -0.792**
- Median rent burden vs. 250m sampled straight-line transit distance: **r = -0.337**

These are descriptive associations and should not be interpreted as causal effects.

## 6. Primary Multivariable Regression

The primary model estimates the association between tract-level median gross rent and transit accessibility while controlling for median household income and vehicle access.

- Observations: **21**
- R²: **0.029**
- Adjusted R²: **-0.143**
- Overall F-test p-value: **0.6699**

| Predictor | Coefficient | Robust p-value |
|---|---:|---:|
| Transit distance (km) | **0.518** | **0.9884** |
| Household income ($10,000s) | -1.696 | 0.975 |
| Vehicle access (%) | 3.688 | 0.736 |

The estimated coefficient for transit distance corresponds to approximately **$1 lower tract-level median gross rent per additional kilometer of the 250-meter sampled straight-line transit-distance measure**, conditional on the other included variables.

This is an association at the census-tract level, not evidence that increasing or decreasing transit access causes rents to change.

## 7. Influence and Sensitivity Analysis

- GEOID `42027011903`: Cook's distance ≈ **0.831**
- GEOID `42027012300`: Cook's distance ≈ **0.641**

The transit-distance association remained similar when these observations were removed individually or together.

| Scenario | Observations | Transit coefficient | p-value |
|---|---:|---:|---:|
| All observations | 21 | 0.52 | 0.9884 |
| Remove 42027011903 | 20 | -16.57 | 0.5807 |
| Remove 42027012300 | 20 | 24.58 | 0.4928 |
| Remove both | 19 | 4.56 | 0.8697 |

## 8. Spatial Residual Diagnostics

- Observations: **21**
- Neighborhood definition: **Queen contiguity**
- Average neighbors: **4.86**
- Moran's I: **-0.0419**
- Permutation p-value: **0.4770**

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
- Only 21 complete observations are available for the primary regression.
- Several ACS variables are unavailable for three study-area tracts.
- The study area contains only 23 tracts, limiting statistical precision.
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
