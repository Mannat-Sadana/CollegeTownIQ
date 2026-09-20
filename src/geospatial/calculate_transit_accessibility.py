from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point


TRACTS_PATH = Path(
    "data/raw/tiger_2024_pa_tracts/tl_2024_42_tract.shp"
)
STUDY_AREA_PATH = Path("data/processed/study_area.gpkg")
STOPS_PATH = Path("data/processed/cata_stops.gpkg")
OUTPUT_PATH = Path(
    "data/processed/transit_accessibility.gpkg"
)

METRIC_CRS = "EPSG:26918"
GRID_SPACING_METERS = 500


def load_study_area() -> gpd.GeoDataFrame:
    return gpd.read_file(STUDY_AREA_PATH)


def load_tracts(
    study_area: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tracts = gpd.read_file(TRACTS_PATH)

    tracts = tracts[tracts["COUNTYFP"] == "027"].copy()
    tracts = tracts.to_crs(study_area.crs)

    study_area_geometry = study_area.union_all()

    tracts = tracts[
        tracts.geometry.intersects(study_area_geometry)
    ].copy()

    return tracts


def load_stops() -> gpd.GeoDataFrame:
    return gpd.read_file(STOPS_PATH)


def create_sample_points(
    geometry,
    spacing: float,
) -> list[Point]:
    min_x, min_y, max_x, max_y = geometry.bounds

    x_values = np.arange(
        min_x,
        max_x + spacing,
        spacing,
    )
    y_values = np.arange(
        min_y,
        max_y + spacing,
        spacing,
    )

    points = []

    for x in x_values:
        for y in y_values:
            point = Point(x, y)

            if geometry.contains(point):
                points.append(point)

    representative_point = geometry.representative_point()

    if not points:
        points.append(representative_point)
    elif representative_point not in points:
        points.append(representative_point)

    return points


def calculate_accessibility(
    tracts: gpd.GeoDataFrame,
    stops: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tracts_projected = tracts.to_crs(METRIC_CRS)
    stops_projected = stops.to_crs(METRIC_CRS)

    results = []

    for _, tract in tracts_projected.iterrows():
        points = create_sample_points(
            tract.geometry,
            GRID_SPACING_METERS,
        )

        point_geometries = gpd.GeoDataFrame(
            geometry=points,
            crs=METRIC_CRS,
        )

        nearest = gpd.sjoin_nearest(
            point_geometries,
            stops_projected[["stop_id", "geometry"]],
            how="left",
            distance_col="distance_m",
        )

        distances = nearest["distance_m"].dropna()

        results.append(
            {
                "GEOID": tract["GEOID"],
                "sample_point_count": len(distances),
                "median_transit_distance_m": distances.median(),
                "p25_transit_distance_m": distances.quantile(0.25),
                "p75_transit_distance_m": distances.quantile(0.75),
                "max_sampled_transit_distance_m": distances.max(),
            }
        )

    accessibility = pd.DataFrame(results)

    return accessibility


def save_results(
    accessibility: pd.DataFrame,
    tracts: gpd.GeoDataFrame,
) -> None:
    output = tracts[
        ["GEOID", "geometry"]
    ].merge(
        accessibility,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    output = gpd.GeoDataFrame(
        output,
        geometry="geometry",
        crs=tracts.crs,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output.to_file(
        OUTPUT_PATH,
        layer="transit_accessibility",
        driver="GPKG",
    )

    print(
        f"Saved transit accessibility dataset to "
        f"{OUTPUT_PATH}"
    )
    print(f"Rows: {len(output)}")
    print(
        f"Unique GEOIDs: "
        f"{output['GEOID'].nunique()}"
    )
    print(
        "Median of tract median distances (m): "
        f"{output['median_transit_distance_m'].median():.2f}"
    )
    print(
        "Maximum tract median distance (m): "
        f"{output['median_transit_distance_m'].max():.2f}"
    )


def main() -> None:
    study_area = load_study_area()
    tracts = load_tracts(study_area)
    stops = load_stops()

    accessibility = calculate_accessibility(
        tracts,
        stops,
    )

    save_results(
        accessibility,
        tracts,
    )


if __name__ == "__main__":
    main()