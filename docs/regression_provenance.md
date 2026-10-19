# Regression Provenance — Issue A

## Decision
The current 250 m transit-accessibility analysis is the primary model.
Do not mix historical regression figures with current results.

## Current primary result
- Dataset: data/processed/transit_accessibility_250m.gpkg
- Tract selection: at least 50% overlap with the study area
- Selected tracts: 23
- Complete regression observations: 21
- R-squared: 0.028699
- Transit-distance coefficient: approximately +$0.5175 per km
- HC3 p-value: 0.98838481
- 95% confidence interval: approximately [-$69.1544, +$70.1894] per km

## Historical comparison
The historical 500 m dataset, merged with the raw ACS source, produced:
- 28 tracts before complete-case exclusion
- 25 complete observations
- R-squared: 0.188519
- Transit-distance coefficient: approximately -$35.3004 per km
- HC3 p-value: 0.00714785
- 95% confidence interval: approximately [-$61.0219, -$9.5790] per km

The historical headline also reported R-squared approximately 0.19 and
p = 0.0066. That exact result has not been independently reproduced from
a fully verified historical 250 m dataset.

## Likely source of the discrepancy
The current selection function applies a 50% tract-area overlap threshold.
The earlier workflow used a broader set of Centre County tracts. This changes
the analysis sample and can materially change the regression estimates.

The historical 500 m file's generation provenance remains uncertain because
the current source tree does not contain a dedicated builder that writes
data/processed/transit_accessibility_500m.gpkg.

## Reporting rule
Use the current 250 m result in the main README and current analysis.
Label historical estimates as historical and not directly comparable.
Do not change the overlap threshold merely to recover statistical significance.
