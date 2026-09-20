from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm


INPUT_PATH = Path("data/processed/college_town_analysis.gpkg")


def load_analysis_data() -> pd.DataFrame:
    dataset = gpd.read_file(INPUT_PATH)

    columns = [
        "median_gross_rent",
        "median_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
    ]

    analysis_data = dataset[columns].copy()
    analysis_data = analysis_data.dropna()

    analysis_data["transit_distance_km"] = (
        analysis_data["median_transit_distance_m"] / 1000
    )

    analysis_data["income_10k"] = (
        analysis_data["median_household_income"] / 10000
    )

    return analysis_data


def run_model(analysis_data: pd.DataFrame) -> None:
    predictors = analysis_data[
        [
            "transit_distance_km",
            "income_10k",
            "vehicle_access_pct",
        ]
    ]

    predictors = sm.add_constant(predictors)

    outcome = analysis_data["median_gross_rent"]

    model = sm.OLS(outcome, predictors).fit(cov_type="HC3")

    print("\nCollegeTownIQ Affordability–Accessibility Model")
    print("=" * 52)
    print(f"Observations: {len(analysis_data)}")
    print("\nOLS with HC3 robust standard errors:")
    print(model.summary())


def main() -> None:
    analysis_data = load_analysis_data()
    run_model(analysis_data)


if __name__ == "__main__":
    main()
