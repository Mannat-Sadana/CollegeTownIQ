
from pathlib import Path

import geopandas as gpd

from src.geospatial.select_study_area_tracts import (
    select_majority_overlap_tracts,
)

TRACTS_PATH = Path(
    "data/raw/tiger_2024_pa_tracts/tl_2024_42_tract.shp"
)
STUDY_AREA_PATH = Path("data/processed/study_area.gpkg")
STOPS_PATH = Path("data/processed/cata_stops.gpkg")
OUTPUT_PATH = Path("data/processed/transit_distance.gpkg")

METRIC_CRS = "EPSG:26918"


def load_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    tracts = gpd.read_file(TRACTS_PATH)
    study_area = gpd.read_file(STUDY_AREA_PATH)
    stops = gpd.read_file(STOPS_PATH)

    tracts = tracts[
        tracts["COUNTYFP"] == "027"
    ].copy()

    tracts = select_majority_overlap_tracts(
        tracts,
        study_area,
    )

    return tracts, stops


def calculate_nearest_stop_distance(
    tracts: gpd.GeoDataFrame,
    stops: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tracts_projected = tracts.to_crs(METRIC_CRS)
    stops_projected = stops.to_crs(METRIC_CRS)

    tract_points = tracts_projected[
        ["GEOID", "geometry"]
    ].copy()

    tract_points["geometry"] = (
        tract_points.geometry.representative_point()
    )

    nearest = gpd.sjoin_nearest(
        tract_points,
        stops_projected[["stop_id", "geometry"]],
        how="left",
        distance_col="nearest_transit_stop_distance_m",
    )

    # A tract may match multiple stops if distances tie.
    # Keep one result per GEOID for downstream one-to-one merges.
    nearest = (
        nearest.sort_values(
            "nearest_transit_stop_distance_m"
        )
        .drop_duplicates("GEOID")
        .reset_index(drop=True)
    )

    return nearest


def save_dataset(dataset: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset.to_file(
        OUTPUT_PATH,
        layer="transit_distance",
        driver="GPKG",
    )

    distances = dataset[
        "nearest_transit_stop_distance_m"
    ]

    print(f"Saved transit distance dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(dataset)}")
    print(f"Unique GEOIDs: {dataset['GEOID'].nunique()}")
    print(f"Mean nearest-stop distance (m): {distances.mean():.2f}")
    print(f"Median nearest-stop distance (m): {distances.median():.2f}")
    print(f"Maximum nearest-stop distance (m): {distances.max():.2f}")


if __name__ == "__main__":
    tracts, stops = load_data()
    transit_distance = calculate_nearest_stop_distance(
        tracts,
        stops,
    )
    save_dataset(transit_distance)
