"""Secondary analysis of rent burden, food access, and network transit accessibility.

This analysis is retained as a methodological extension and is separate from
the project's primary gross-rent accessibility model.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


INPUT_PATH = Path(
    "data/processed/college_town_master.gpkg"
)


def load_data() -> pd.DataFrame:
    data = gpd.read_file(INPUT_PATH)

    columns = [
        "median_rent_burden_pct",
        "median_network_transit_distance_m",
        "food_access_beyond_half_mile_network_share",
        "median_household_income",
        "vehicle_access_pct",
    ]

    return data[columns].dropna()


def standardize(
    data: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

    standardized = data.copy()

    for column in columns:
        standardized[column] = (
            standardized[column]
            - standardized[column].mean()
        ) / standardized[column].std()

    return standardized


def run_model(
    data: pd.DataFrame,
    predictors: list[str],
):
    x = data[predictors].copy()
    y = data["median_rent_burden_pct"]

    x = sm.add_constant(x)

    model = sm.OLS(y, x).fit(
        cov_type="HC3"
    )

    return model


def calculate_vif(
    data: pd.DataFrame,
    predictors: list[str],
) -> pd.DataFrame:

    x = data[predictors].copy()

    vif_rows = []

    for index, column in enumerate(x.columns):
        vif_rows.append(
            {
                "feature": column,
                "VIF": variance_inflation_factor(
                    x.values,
                    index,
                ),
            }
        )

    return pd.DataFrame(vif_rows)


def print_model(
    name: str,
    model,
) -> None:

    print()
    print(name)
    print("-" * len(name))

    print(
        f"R-squared: {model.rsquared:.4f}"
    )

    print(
        f"Adjusted R-squared: "
        f"{model.rsquared_adj:.4f}"
    )

    print("\nCoefficients:")

    print(
        model.params.to_string()
    )

    print("\nRobust p-values:")

    print(
        model.pvalues.to_string()
    )

    print("\nRobust 95% confidence intervals:")

    print(
        model.conf_int().to_string()
    )


def main() -> None:

    data = load_data()

    print(
        "CollegeTownIQ Accessibility-Burden Regression"
    )
    print(
        "---------------------------------------------"
    )
    print(
        f"Complete observations: {len(data)}"
    )

    predictors = [
        "food_access_beyond_half_mile_network_share",
        "median_network_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
    ]

    standardized_data = standardize(
        data,
        predictors,
    )

    model_1 = run_model(
        standardized_data,
        [
            "food_access_beyond_half_mile_network_share",
        ],
    )

    model_2 = run_model(
        standardized_data,
        [
            "food_access_beyond_half_mile_network_share",
            "median_network_transit_distance_m",
        ],
    )

    model_3 = run_model(
        standardized_data,
        predictors,
    )

    print_model(
        "Model 1: Food accessibility only",
        model_1,
    )

    print_model(
        "Model 2: Food + transit accessibility",
        model_2,
    )

    print_model(
        "Model 3: Full model",
        model_3,
    )

    print()
    print("Multicollinearity diagnostics")
    print("------------------------------")

    vif = calculate_vif(
        standardized_data,
        predictors,
    )

    print(
        vif.to_string(index=False)
    )


if __name__ == "__main__":
    main()