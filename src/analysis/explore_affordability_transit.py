from pathlib import Path

import geopandas as gpd
import pandas as pd


INPUT_PATH = Path("data/processed/college_town_dataset.gpkg")
OUTPUT_PATH = Path("docs/affordability_transit_summary.csv")

FEATURES = [
    "median_gross_rent",
    "median_household_income",
    "annual_rent_to_income_ratio",
    "vehicle_access_pct",
    "transit_stop_count",
    "nearest_transit_stop_distance_m",
    "scheduled_trip_count",
]


def load_data() -> gpd.GeoDataFrame:
    return gpd.read_file(INPUT_PATH)


def create_analysis_data(
    dataset: gpd.GeoDataFrame,
) -> pd.DataFrame:
    analysis_data = dataset[FEATURES].copy()

    analysis_data = analysis_data.dropna(
        subset=[
            "median_gross_rent",
            "median_household_income",
            "annual_rent_to_income_ratio",
            "nearest_transit_stop_distance_m",
        ]
    )

    return analysis_data


def create_summary(
    analysis_data: pd.DataFrame,
) -> pd.DataFrame:
    summary = analysis_data.describe().T

    summary = summary[
        [
            "count",
            "mean",
            "std",
            "min",
            "50%",
            "max",
        ]
    ]

    summary = summary.rename(
        columns={"50%": "median"}
    )

    return summary.reset_index().rename(
        columns={"index": "feature"}
    )


def calculate_correlations(
    analysis_data: pd.DataFrame,
) -> pd.DataFrame:
    correlation_columns = [
        "median_gross_rent",
        "annual_rent_to_income_ratio",
        "transit_stop_count",
        "nearest_transit_stop_distance_m",
        "scheduled_trip_count",
    ]

    return analysis_data[
        correlation_columns
    ].corr()


def main() -> None:
    dataset = load_data()
    analysis_data = create_analysis_data(dataset)

    summary = create_summary(analysis_data)
    correlations = calculate_correlations(analysis_data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    summary.to_csv(OUTPUT_PATH, index=False)

    print("Affordability/transit analysis dataset")
    print("---------------------------------------")
    print(f"Original tracts: {len(dataset)}")
    print(f"Analysis observations: {len(analysis_data)}")

    print("\nSummary statistics:")
    print(summary.to_string(index=False))

    print("\nCorrelation matrix:")
    print(correlations.to_string())


if __name__ == "__main__":
    main()