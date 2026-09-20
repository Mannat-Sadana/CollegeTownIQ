from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)
OUTPUT_PATH = Path(
    "docs/regression_sensitivity.csv"
)

TARGET = "median_gross_rent"

PREDICTORS = [
    "median_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]


def load_model_data():
    dataset = gpd.read_file(INPUT_PATH)

    columns = ["GEOID", TARGET] + PREDICTORS

    data = dataset[columns].dropna().copy()

    data["transit_distance_km"] = (
        data["median_transit_distance_m"] / 1000
    )

    data["income_10k"] = (
        data["median_household_income"] / 10000
    )

    return data.reset_index(drop=True)


def fit_model(data):
    predictors = [
        "transit_distance_km",
        "income_10k",
        "vehicle_access_pct",
    ]

    x = sm.add_constant(data[predictors])
    y = data[TARGET]

    return sm.OLS(y, x).fit(cov_type="HC3")


def calculate_results(
    data,
    excluded_geoids,
    scenario,
):
    analysis_data = data[
        ~data["GEOID"].isin(excluded_geoids)
    ].copy()

    model = fit_model(analysis_data)

    transit_coefficient = model.params[
        "transit_distance_km"
    ]

    transit_p_value = model.pvalues[
        "transit_distance_km"
    ]

    confidence_interval = model.conf_int().loc[
        "transit_distance_km"
    ]

    return {
        "scenario": scenario,
        "observations": len(analysis_data),
        "r_squared": model.rsquared,
        "adjusted_r_squared": model.rsquared_adj,
        "transit_distance_coefficient": transit_coefficient,
        "transit_distance_p_value": transit_p_value,
        "transit_distance_ci_lower": confidence_interval[0],
        "transit_distance_ci_upper": confidence_interval[1],
    }


def main():
    data = load_model_data()

    scenarios = [
        (
            [],
            "All observations",
        ),
        (
            ["42027011903"],
            "Exclude 42027011903",
        ),
        (
            ["42027012300"],
            "Exclude 42027012300",
        ),
        (
            [
                "42027011903",
                "42027012300",
            ],
            "Exclude both influential observations",
        ),
    ]

    results = []

    for excluded_geoids, scenario in scenarios:
        results.append(
            calculate_results(
                data,
                excluded_geoids,
                scenario,
            )
        )

    results_dataframe = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("CollegeTownIQ Regression Sensitivity Analysis")
    print("==============================================")
    print()
    print(results_dataframe.to_string(index=False))
    print()
    print(
        f"Saved sensitivity results to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
