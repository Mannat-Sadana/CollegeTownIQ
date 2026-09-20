from pathlib import Path

import geopandas as gpd
import statsmodels.api as sm
import pandas as pd


INPUT_PATH = Path("data/processed/college_town_master.gpkg")
OUTPUT_PATH = Path("docs/regression_sensitivity.csv")


TARGET = "median_rent_burden_pct"

PREDICTORS = [
    "food_access_beyond_half_mile_network_share",
    "median_network_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]


def load_model_data():
    dataset = gpd.read_file(INPUT_PATH)

    columns = ["GEOID", TARGET] + PREDICTORS

    data = dataset[columns].dropna().reset_index(drop=True)

    return data


def fit_model(data):
    x = sm.add_constant(data[PREDICTORS])
    y = data[TARGET]

    return sm.OLS(y, x).fit(cov_type="HC3")


def calculate_results(data, excluded_indices, scenario):
    analysis_data = data.drop(
        index=excluded_indices
    ).reset_index(drop=True)

    model = fit_model(analysis_data)

    results = {
        "scenario": scenario,
        "observations": len(analysis_data),
        "r_squared": model.rsquared,
        "adjusted_r_squared": model.rsquared_adj,
    }

    for predictor in PREDICTORS:
        results[f"{predictor}_coefficient"] = model.params[
            predictor
        ]
        results[f"{predictor}_p_value"] = model.pvalues[
            predictor
        ]

    return results


def main():
    data = load_model_data()

    scenarios = [
        ([], "All observations"),
        ([12], "Exclude observation 12"),
        ([17], "Exclude observation 17"),
        ([12, 17], "Exclude observations 12 and 17"),
    ]

    results = []

    for excluded_indices, scenario in scenarios:
        results.append(
            calculate_results(
                data,
                excluded_indices,
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