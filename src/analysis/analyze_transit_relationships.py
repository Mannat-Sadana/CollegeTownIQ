from pathlib import Path

import geopandas as gpd
import pandas as pd


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)


def main() -> None:
    dataset = gpd.read_file(INPUT_PATH)

    variables = [
        "median_gross_rent",
        "annual_rent_to_income_ratio",
        "median_household_income",
        "vehicle_access_pct",
        "transit_stop_count",
        "median_transit_distance_m",
        "scheduled_trip_count",
    ]

    analysis_data = dataset[variables].dropna()

    correlations = analysis_data.corr()

    print("CollegeTownIQ Transit Relationship Analysis")
    print("--------------------------------------------")
    print(
        f"Study-area tracts: {len(dataset)}"
    )
    print(
        f"Complete observations: "
        f"{len(analysis_data)}"
    )

    print("\nCorrelation matrix:")
    print(
        correlations.to_string(
            float_format=lambda value: f"{value:.4f}"
        )
    )

    print("\nKey relationships:")

    relationships = [
        (
            "Median rent",
            "Median transit distance",
        ),
        (
            "Rent-to-income ratio",
            "Median transit distance",
        ),
        (
            "Median rent",
            "Transit stop count",
        ),
        (
            "Median rent",
            "Scheduled trip count",
        ),
    ]

    for first, second in relationships:
        correlation = correlations.loc[
            first.lower().replace(" ", "_")
            if False
            else {
                "Median rent": "median_gross_rent",
                "Rent-to-income ratio":
                    "annual_rent_to_income_ratio",
                "Median transit distance":
                    "median_transit_distance_m",
                "Transit stop count":
                    "transit_stop_count",
                "Scheduled trip count":
                    "scheduled_trip_count",
            }[first],
            {
                "Median rent": "median_gross_rent",
                "Rent-to-income ratio":
                    "annual_rent_to_income_ratio",
                "Median transit distance":
                    "median_transit_distance_m",
                "Transit stop count":
                    "transit_stop_count",
                "Scheduled trip count":
                    "scheduled_trip_count",
            }[second],
        ]

        print(
            f"{first} vs {second}: "
            f"r = {correlation:.4f}"
        )


if __name__ == "__main__":
    main()