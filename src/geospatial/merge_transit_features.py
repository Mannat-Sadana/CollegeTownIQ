import geopandas as gpd

ACCESS_PATH = "data/processed/transit_access.gpkg"
FREQUENCY_PATH = "data/processed/transit_frequency.gpkg"
OUTPUT_PATH = "data/processed/transit_features.gpkg"


def merge_transit_features() -> None:
    access = gpd.read_file(ACCESS_PATH)
    frequency = gpd.read_file(FREQUENCY_PATH)

    frequency_columns = [
        "GEOID",
        "transit_stop_count",
        "scheduled_trip_count",
        "scheduled_stop_events",
    ]

    frequency = frequency[frequency_columns].copy()

    # Remove the older stop-count field from the access dataset.
    # The frequency dataset contains the authoritative tract-level count.
    access = access.drop(
        columns=[
            "transit_stop_count",
            "scheduled_trip_count",
            "scheduled_stop_events",
        ],
        errors="ignore",
    )

    merged = access.merge(
        frequency,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    if merged["transit_stop_count"].isna().any():
        raise ValueError("Some tracts are missing transit frequency data.")

    if merged["scheduled_trip_count"].isna().any():
        raise ValueError("Some tracts are missing scheduled trip data.")

    if merged["scheduled_stop_events"].isna().any():
        raise ValueError("Some tracts are missing scheduled stop-event data.")

    merged = gpd.GeoDataFrame(
        merged,
        geometry="geometry",
        crs=access.crs,
    )

    merged.to_file(OUTPUT_PATH, driver="GPKG")

    print(f"Saved merged transit dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(merged)}")
    print(f"Columns: {len(merged.columns)}")
    print(f"Transit stops: {merged['transit_stop_count'].sum()}")
    print(f"Scheduled trip count across tracts: {merged['scheduled_trip_count'].sum()}")
    print(f"Scheduled stop events: {merged['scheduled_stop_events'].sum()}")


if __name__ == "__main__":
    merge_transit_features()