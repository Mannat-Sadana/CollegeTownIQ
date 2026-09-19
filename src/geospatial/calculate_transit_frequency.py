from pathlib import Path

import geopandas as gpd
import pandas as pd


TRACTS_PATH = Path(
    "data/raw/tiger_2024_pa_tracts/tl_2024_42_tract.shp"
)
STOPS_PATH = Path("data/processed/cata_stops.gpkg")
STOP_TIMES_PATH = Path("data/raw/cata_gtfs/stop_times.txt")
TRIPS_PATH = Path("data/raw/cata_gtfs/trips.txt")
OUTPUT_PATH = Path("data/processed/transit_frequency.gpkg")


def calculate_transit_frequency() -> None:
    # Load actual Census tract polygons
    tracts = gpd.read_file(TRACTS_PATH)

    tracts = tracts[tracts["COUNTYFP"] == "027"].copy()

    # Load CATA stop locations
    stops = gpd.read_file(STOPS_PATH)
    stops["stop_id"] = stops["stop_id"].astype(str)

    # Match coordinate systems
    stops = stops.to_crs(tracts.crs)

    # Assign each CATA stop to its Census tract
    stop_tracts = gpd.sjoin(
        stops[["stop_id", "geometry"]],
        tracts[["GEOID", "geometry"]],
        how="left",
        predicate="within",
    )

    # Remove duplicate spatial matches if any
    stop_tracts = stop_tracts.drop_duplicates(
        subset=["stop_id"]
    )

    # Load scheduled stop times
    stop_times = pd.read_csv(
        STOP_TIMES_PATH,
        usecols=["trip_id", "stop_id"],
        dtype={"trip_id": str, "stop_id": str},
    )

    # Keep only valid scheduled trips
    trips = pd.read_csv(
        TRIPS_PATH,
        usecols=["trip_id"],
        dtype={"trip_id": str},
    )

    stop_times = stop_times[
        stop_times["trip_id"].isin(trips["trip_id"])
    ].copy()

    # Attach tract to every scheduled stop event
    stop_events = stop_times.merge(
        stop_tracts[["stop_id", "GEOID"]],
        on="stop_id",
        how="left",
    )

    # Calculate tract-level transit metrics
    tract_frequency = (
        stop_events.dropna(subset=["GEOID"])
        .groupby("GEOID")
        .agg(
            scheduled_trip_count=("trip_id", "nunique"),
            scheduled_stop_events=("trip_id", "size"),
        )
        .reset_index()
    )

    # Count physical transit stops in each tract
    stop_counts = (
        stop_tracts.dropna(subset=["GEOID"])
        .groupby("GEOID")["stop_id"]
        .nunique()
        .reset_index(name="transit_stop_count")
    )

    # Combine metrics
    result = tracts.merge(
        stop_counts,
        on="GEOID",
        how="left",
    )

    result = result.merge(
        tract_frequency,
        on="GEOID",
        how="left",
    )

    # Fill tracts without service with zero
    for column in [
        "transit_stop_count",
        "scheduled_trip_count",
        "scheduled_stop_events",
    ]:
        result[column] = (
            result[column]
            .fillna(0)
            .astype(int)
        )

    # Save
    result.to_file(
        OUTPUT_PATH,
        layer="transit_frequency",
        driver="GPKG",
    )

    print(f"Saved transit frequency dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(result)}")
    print(
        "Tracts with scheduled service:",
        (result["scheduled_trip_count"] > 0).sum(),
    )
    print(
        "Total unique transit stops:",
        result["transit_stop_count"].sum(),
    )
    print(
        "Total scheduled trip events:",
        result["scheduled_stop_events"].sum(),
    )
    print(
        "Unassigned stops:",
        stop_tracts["GEOID"].isna().sum(),
    )


if __name__ == "__main__":
    calculate_transit_frequency()