from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)

PREDICTORS = [
    "median_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]

TARGET = "median_gross_rent"


def main() -> None:
    dataset = gpd.read_file(INPUT_PATH)

    analysis_data = dataset[
        PREDICTORS + [TARGET]
    ].dropna()

    x_data = analysis_data[PREDICTORS]
    y_data = analysis_data[TARGET]

    # Standardize predictors so coefficients are comparable
    # and numerical conditioning is improved.
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_data)

    x_scaled = pd.DataFrame(
        x_scaled,
        columns=PREDICTORS,
        index=analysis_data.index,
    )

    x_scaled = sm.add_constant(x_scaled)

    # HC3 robust standard errors are appropriate for a
    # small cross-sectional dataset where unequal variance
    # across observations is possible.
    model = sm.OLS(y_data, x_scaled).fit(
        cov_type="HC3"
    )

    print("CollegeTownIQ Robust Housing Cost Regression")
    print("---------------------------------------------")
    print(f"Observations: {len(analysis_data)}")

    print("\nRegression results:")
    print(model.summary())

    print("\nRobust 95% Confidence Intervals:")
    print(model.conf_int())

    print("\nStandardized predictor coefficients:")

    for variable in PREDICTORS:
        print(
            f"{variable}: "
            f"coefficient = {model.params[variable]:.4f}, "
            f"p-value = {model.pvalues[variable]:.4f}"
        )


if __name__ == "__main__":
    main()