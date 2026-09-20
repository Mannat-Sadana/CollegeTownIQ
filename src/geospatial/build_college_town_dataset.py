import geopandas as gpd

INPUT_PATH = "data/processed/transit_access.gpkg"
OUTPUT_PATH = "data/processed/college_town_dataset.gpkg"

REQUIRED_COLUMNS = [
    "GEOID",
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "households_without_vehicle",
    "total_households_vehicle",
    "vehicle_access_pct",
    "transit_stop_count",
    "nearest_transit_stop_distance_m",
    "scheduled_trip_count",
    "scheduled_stop_events",
    "geometry",
]


def build_college_town_dataset() -> None:
    data = gpd.read_file(INPUT_PATH)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    dataset = data[REQUIRED_COLUMNS].copy()

    dataset["annual_rent_to_income_ratio"] = (
        dataset["median_gross_rent"] * 12
        / dataset["median_household_income"]
    )

    dataset = gpd.GeoDataFrame(
        dataset,
        geometry="geometry",
        crs=data.crs,
    )

    dataset.to_file(
        OUTPUT_PATH,
        layer="college_town_dataset",
        driver="GPKG",
    )

    print(f"Saved college-town dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print(f"Unique GEOIDs: {dataset['GEOID'].nunique()}")
    print(
        f"Transit stops: "
        f"{dataset['transit_stop_count'].sum()}"
    )
    print(
        f"Scheduled stop events: "
        f"{dataset['scheduled_stop_events'].sum()}"
    )


if __name__ == "__main__":
    build_college_town_dataset()