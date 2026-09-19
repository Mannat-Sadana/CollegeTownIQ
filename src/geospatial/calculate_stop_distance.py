from pathlib import Path

import geopandas as gpd

TRACTS_PATH = Path("data/processed/transit_access.gpkg")
STOPS_PATH = Path("data/processed/cata_stops.gpkg")
OUTPUT_PATH = Path("data/processed/transit_distance.gpkg")

METRIC_CRS = "EPSG:26918"


def load_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    tracts = gpd.read_file(TRACTS_PATH)
    stops = gpd.read_file(STOPS_PATH)

    return tracts, stops


def calculate_nearest_stop_distance(
    tracts: gpd.GeoDataFrame,
    stops: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tracts_projected = tracts.to_crs(METRIC_CRS)
    stops_projected = stops.to_crs(METRIC_CRS)

    tract_points = tracts_projected.copy()
    tract_points["geometry"] = tract_points.geometry.representative_point()

    nearest = gpd.sjoin_nearest(
        tract_points,
        stops_projected[["stop_id", "geometry"]],
        how="left",
        distance_col="nearest_transit_stop_distance_m",
    )

    return nearest


def save_dataset(dataset: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_file(
        OUTPUT_PATH,
        layer="transit_distance",
        driver="GPKG",
    )

    print(f"Saved transit distance dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(dataset)}")
    print(
        "Mean nearest-stop distance (m): "
        f"{dataset['nearest_transit_stop_distance_m'].mean():.2f}"
    )


if __name__ == "__main__":
    tracts, stops = load_data()
    transit_distance = calculate_nearest_stop_distance(tracts, stops)
    save_dataset(transit_distance)