from pathlib import Path

import geopandas as gpd


BASE_DATA_PATH = Path(
    "data/processed/college_town_dataset.gpkg"
)
ACCESSIBILITY_PATH = Path(
    "data/processed/transit_accessibility_250m.gpkg"
)
OUTPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)


def build_analysis_dataset() -> gpd.GeoDataFrame:
    base_data = gpd.read_file(BASE_DATA_PATH)

    accessibility = gpd.read_file(
        ACCESSIBILITY_PATH
    )[
        [
            "GEOID",
            "sample_point_count",
            "median_transit_distance_m",
            "p25_transit_distance_m",
            "p75_transit_distance_m",
            "max_sampled_transit_distance_m",
        ]
    ]

    dataset = base_data.drop(
        columns=["nearest_transit_stop_distance_m"],
        errors="ignore",
    )

    dataset = dataset.merge(
        accessibility,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    if len(dataset) != 28:
        raise ValueError(
            f"Expected 28 study-area tracts, "
            f"found {len(dataset)}."
        )

    if dataset["GEOID"].nunique() != 28:
        raise ValueError(
            "GEOID uniqueness check failed."
        )

    required_columns = [
        "median_gross_rent",
        "median_household_income",
        "annual_rent_to_income_ratio",
        "vehicle_access_pct",
        "transit_stop_count",
        "scheduled_trip_count",
        "scheduled_stop_events",
        "median_transit_distance_m",
        "sample_point_count",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return dataset


def save_dataset(
    dataset: gpd.GeoDataFrame,
) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_file(
        OUTPUT_PATH,
        layer="college_town_analysis",
        driver="GPKG",
    )

    print(
        f"Saved analysis dataset to {OUTPUT_PATH}"
    )
    print(f"Rows: {len(dataset)}")
    print(
        f"Unique GEOIDs: "
        f"{dataset['GEOID'].nunique()}"
    )
    print(
        "Median transit accessibility (m): "
        f"{dataset['median_transit_distance_m'].median():.2f}"
    )
    print(
        "Mean transit accessibility (m): "
        f"{dataset['median_transit_distance_m'].mean():.2f}"
    )
    print(
        "Missing median transit accessibility: "
        f"{dataset['median_transit_distance_m'].isna().sum()}"
    )


if __name__ == "__main__":
    analysis_dataset = build_analysis_dataset()
    save_dataset(analysis_dataset)