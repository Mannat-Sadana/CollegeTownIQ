from pathlib import Path

import geopandas as gpd
import pandas as pd

INPUT_PATH = Path("data/raw/cata_gtfs/stops.txt")
OUTPUT_PATH = Path("data/processed/cata_stops.gpkg")

WGS84_CRS = "EPSG:4326"


def load_stops() -> pd.DataFrame:
    return pd.read_csv(INPUT_PATH)


def build_stop_geodataframe(stops: pd.DataFrame) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(
            stops["stop_lon"],
            stops["stop_lat"],
        ),
        crs=WGS84_CRS,
    )


def save_stops(stops: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    stops.to_file(
        OUTPUT_PATH,
        layer="cata_stops",
        driver="GPKG",
    )

    print(f"Saved CATA stops to {OUTPUT_PATH}")
    print(f"Rows: {len(stops)}")
    print(f"CRS: {stops.crs}")


if __name__ == "__main__":
    stops = load_stops()
    stop_geodata = build_stop_geodataframe(stops)
    save_stops(stop_geodata)