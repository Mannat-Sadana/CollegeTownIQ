from pathlib import Path

import geopandas as gpd


TRACTS_PATH = Path("data/processed/college_town_features.gpkg")
DISTANCE_PATH = Path("data/processed/transit_distance.gpkg")
FREQUENCY_PATH = Path("data/processed/transit_frequency.gpkg")
OUTPUT_PATH = Path("data/processed/transit_access.gpkg")


def calculate_transit_access() -> None:
    tracts = gpd.read_file(TRACTS_PATH)
    distances = gpd.read_file(DISTANCE_PATH)
    frequency = gpd.read_file(FREQUENCY_PATH)

    study_geoids = distances[["GEOID"]].drop_duplicates()

    tracts = tracts.merge(
        study_geoids,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    frequency = frequency[
        [
            "GEOID",
            "transit_stop_count",
            "scheduled_trip_count",
            "scheduled_stop_events",
        ]
    ].copy()

    distances = distances[
        [
            "GEOID",
            "nearest_transit_stop_distance_m",
        ]
    ].copy()

    transit_access = tracts.merge(
        frequency,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    transit_access = transit_access.merge(
        distances,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    required_columns = [
        "transit_stop_count",
        "scheduled_trip_count",
        "scheduled_stop_events",
        "nearest_transit_stop_distance_m",
    ]

    if transit_access[required_columns].isna().any().any():
        raise ValueError(
            "Some study-area tracts are missing transit data."
        )

    transit_access.to_file(
        OUTPUT_PATH,
        layer="transit_access",
        driver="GPKG",
    )

    print(f"Saved transit access dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(transit_access)}")
    print(
        "Unique GEOIDs:",
        transit_access["GEOID"].nunique(),
    )
    print(
        "Total transit stops:",
        transit_access["transit_stop_count"].sum(),
    )
    print(
        "Tracts with transit service:",
        (
            transit_access["scheduled_trip_count"] > 0
        ).sum(),
    )
    print(
        "Scheduled stop events:",
        transit_access["scheduled_stop_events"].sum(),
    )
    print(
        "Median nearest-stop distance (m):",
        f"{transit_access['nearest_transit_stop_distance_m'].median():.2f}",
    )


if __name__ == "__main__":
    calculate_transit_access()