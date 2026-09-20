from pathlib import Path

import geopandas as gpd


INPUT_PATH = Path("data/processed/college_town_master.gpkg")
OUTPUT_DIR = Path("dashboard/data")

REQUIRED_COLUMNS = [
    "GEOID",
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "vehicle_access_pct",
    "transit_stop_count",
    "scheduled_trip_count",
    "median_network_transit_distance_m",
    "food_access_beyond_half_mile_straight_share",
    "food_access_beyond_half_mile_network_share",
    "geometry",
]


def load_master_dataset() -> gpd.GeoDataFrame:
    """Load the CollegeTownIQ master dataset."""
    return gpd.read_file(INPUT_PATH)


def prepare_dashboard_data(
    dataset: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Select and validate fields required by the dashboard."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dashboard columns: {missing_columns}"
        )

    dashboard_data = dataset[REQUIRED_COLUMNS].copy()
    dashboard_data = dashboard_data.rename(columns={"median_network_transit_distance_m": "median_transit_distance_m"})

    if dashboard_data["GEOID"].duplicated().any():
        raise ValueError("Duplicate GEOIDs found.")

    if dashboard_data["geometry"].isna().any():
        raise ValueError("Missing geometries found.")

    return dashboard_data


def save_geojson(
    dashboard_data: gpd.GeoDataFrame,
) -> None:
    """Export dashboard-ready geographic data."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "college_town_data.geojson"

    dashboard_data.to_file(
        output_path,
        driver="GeoJSON",
    )

    print(f"Saved dashboard data to {output_path}")
    print(f"Rows: {len(dashboard_data)}")
    print(
        f"Unique GEOIDs: "
        f"{dashboard_data['GEOID'].nunique()}"
    )


def main() -> None:
    """Build the dashboard data layer."""

    dataset = load_master_dataset()
    dashboard_data = prepare_dashboard_data(dataset)
    save_geojson(dashboard_data)


if __name__ == "__main__":
    main()