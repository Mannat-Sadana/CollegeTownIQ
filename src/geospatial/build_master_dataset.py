from pathlib import Path

import geopandas as gpd


BASE_DATA_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)

NETWORK_ACCESS_PATH = Path(
    "data/processed/network_transit_accessibility.gpkg"
)

FOOD_ACCESS_PATH = Path(
    "data/processed/college_town_food_access.gpkg"
)

OUTPUT_PATH = Path(
    "data/processed/college_town_master.gpkg"
)


def load_base_data() -> gpd.GeoDataFrame:
    return gpd.read_file(BASE_DATA_PATH)


def load_network_access() -> gpd.GeoDataFrame:
    return gpd.read_file(NETWORK_ACCESS_PATH)


def load_food_access() -> gpd.GeoDataFrame:
    return gpd.read_file(FOOD_ACCESS_PATH)


def build_master_dataset(
    base_data: gpd.GeoDataFrame,
    network_access: gpd.GeoDataFrame,
    food_access: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:

    network_access = network_access[
        [
            "GEOID",
            "median_network_transit_distance_m",
            "p25_network_transit_distance_m",
            "p75_network_transit_distance_m",
            "max_network_transit_distance_m",
        ]
    ].copy()

    food_access = food_access[
        [
            "GEOID",
            "food_access_beyond_half_mile_straight_share",
            "food_access_beyond_half_mile_network_share",
        ]
    ].copy()

    dataset = base_data.merge(
        network_access,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    dataset = dataset.merge(
        food_access,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    if len(dataset) != 28:
        raise ValueError(
            f"Expected 28 tracts, found {len(dataset)}."
        )

    if dataset["GEOID"].nunique() != 28:
        raise ValueError(
            "GEOID uniqueness check failed."
        )

    required_columns = [
        "GEOID",
        "median_gross_rent",
        "median_rent_burden_pct",
        "median_household_income",
        "vehicle_access_pct",
        "transit_stop_count",
        "scheduled_trip_count",
        "scheduled_stop_events",
        "median_transit_distance_m",
        "median_network_transit_distance_m",
        "food_access_beyond_half_mile_straight_share",
        "food_access_beyond_half_mile_network_share",
        "geometry",
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

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset.to_file(
        OUTPUT_PATH,
        layer="college_town_master",
        driver="GPKG",
    )

    print(
        f"Saved master dataset to {OUTPUT_PATH}"
    )

    print(f"Rows: {len(dataset)}")
    print(
        f"Unique GEOIDs: "
        f"{dataset['GEOID'].nunique()}"
    )

    print(
        "Missing network transit accessibility:",
        dataset[
            "median_network_transit_distance_m"
        ].isna().sum(),
    )

    print(
        "Missing food accessibility:",
        dataset[
            "food_access_beyond_half_mile_network_share"
        ].isna().sum(),
    )

    print(
        "Columns:",
        len(dataset.columns),
    )


def main() -> None:

    base_data = load_base_data()
    network_access = load_network_access()
    food_access = load_food_access()

    master_dataset = build_master_dataset(
        base_data,
        network_access,
        food_access,
    )

    save_dataset(master_dataset)


if __name__ == "__main__":
    main()