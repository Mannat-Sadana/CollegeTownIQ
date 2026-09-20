from pathlib import Path

import geopandas as gpd
import statsmodels.api as sm


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

    x_data = sm.add_constant(x_data)

    model = sm.OLS(y_data, x_data).fit()

    print("CollegeTownIQ Housing Cost Regression")
    print("--------------------------------------")
    print(
        f"Observations: {len(analysis_data)}"
    )

    print("\nRegression results:")
    print(model.summary())

    print("\n95% Confidence Intervals:")
    print(model.conf_int())

    print("\nKey coefficients:")
    for variable in model.params.index:
        print(
            f"{variable}: "
            f"coefficient = {model.params[variable]:.4f}, "
            f"p-value = {model.pvalues[variable]:.4f}"
        )


if __name__ == "__main__":
    main()