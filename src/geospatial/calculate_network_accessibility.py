from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point
from src.geospatial.select_study_area_tracts import (
    select_majority_overlap_tracts,
)

TRACTS_PATH = Path(
    "data/raw/tiger_2024_pa_tracts/tl_2024_42_tract.shp"
)

STUDY_AREA_PATH = Path(
    "data/processed/study_area.gpkg"
)

STOPS_PATH = Path(
    "data/processed/cata_stops.gpkg"
)

NETWORK_PATH = Path(
    "data/processed/walking_network.graphml"
)

OUTPUT_PATH = Path(
    "data/processed/network_transit_accessibility.gpkg"
)

METRIC_CRS = "EPSG:26918"

GRID_SPACING_METERS = 250


def load_data():
    study_area = gpd.read_file(
        STUDY_AREA_PATH
    )

    tracts = gpd.read_file(
        TRACTS_PATH
    )

    stops = gpd.read_file(
        STOPS_PATH
    )

    walking_network = ox.load_graphml(
        NETWORK_PATH
    )

    return (
        study_area,
        tracts,
        stops,
        walking_network,
    )


def select_study_area_tracts(
    study_area: gpd.GeoDataFrame,
    tracts: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    tracts = tracts[
        tracts["COUNTYFP"] == "027"
    ].copy()

    tracts = select_majority_overlap_tracts(
        tracts,
        study_area,
    )

    # Project tract geometries into meters before
    # generating the 250 m sample grid.
    return tracts.to_crs(METRIC_CRS)


def create_sample_points(
    geometry,
    spacing,
):
    min_x, min_y, max_x, max_y = (
        geometry.bounds
    )

    x_values = range(
        int(min_x),
        int(max_x) + spacing,
        spacing,
    )

    y_values = range(
        int(min_y),
        int(max_y) + spacing,
        spacing,
    )

    points = []

    for x in x_values:
        for y in y_values:
            point = Point(x, y)

            if geometry.contains(point):
                points.append(point)

    representative_point = (
        geometry.representative_point()
    )

    if (
        not points
        or representative_point not in points
    ):
        points.append(
            representative_point
        )

    return points


def prepare_network(
    walking_network,
    stops,
):
    walking_network = ox.project_graph(
        walking_network,
        to_crs=METRIC_CRS,
    )

    stops_projected = stops.to_crs(
        METRIC_CRS
    )

    stop_nodes = ox.distance.nearest_nodes(
        walking_network,
        X=stops_projected.geometry.x,
        Y=stops_projected.geometry.y,
    )

    stop_node_set = set(stop_nodes)

    print(
        f"CATA stops mapped to "
        f"{len(stop_node_set)} unique network nodes."
    )

    # Convert the directed walking network to
    # an undirected graph so walking distance
    # is not dependent on street direction.
    undirected_network = (
        walking_network.to_undirected()
    )

    return (
        undirected_network,
        stop_node_set,
    )


def calculate_nearest_stop_distances(
    walking_network,
    stop_node_set,
):
    print(
        "Calculating network distance to "
        "nearest CATA stop..."
    )

    distances = nx.multi_source_dijkstra_path_length(
        walking_network,
        sources=stop_node_set,
        weight="length",
    )

    print(
        f"Calculated distances for "
        f"{len(distances):,} network nodes."
    )

    return distances



def calculate_accessibility(
    tracts,
    walking_network,
    network_distances,
):
    results = []

    # Provisional quality-control threshold.
    MAX_SNAP_DISTANCE_M = 250

    nodes = ox.graph_to_gdfs(
        walking_network,
        edges=False,
    )

    for _, tract in tracts.iterrows():
        points = create_sample_points(
            tract.geometry,
            GRID_SPACING_METERS,
        )

        sample_nodes = ox.distance.nearest_nodes(
            walking_network,
            X=[point.x for point in points],
            Y=[point.y for point in points],
        )

        point_records = []

        for point, node in zip(points, sample_nodes):
            snap_distance = point.distance(
                nodes.loc[node].geometry
            )

            network_distance = network_distances.get(
                node
            )

            point_records.append({
                "snap_distance_m": snap_distance,
                "network_distance_m": network_distance,
            })

        point_df = pd.DataFrame(point_records)

        # Only points with a network distance and a
        # sufficiently close network node are retained.
        valid = point_df[
            point_df["network_distance_m"].notna()
            & (
                point_df["snap_distance_m"]
                <= MAX_SNAP_DISTANCE_M
            )
        ]

        # Original baseline: network distance from the
        # snapped sample-point node to the nearest stop.
        # Sensitivity estimate adds straight-line snap distance.
        # This is not a true routed walking distance.
        if valid.empty:
            median_distance = float("nan")
            p25_distance = float("nan")
            p75_distance = float("nan")
            max_distance = float("nan")

            median_corrected_distance = float("nan")
            p25_corrected_distance = float("nan")
            p75_corrected_distance = float("nan")
            max_corrected_distance = float("nan")
        else:
            baseline_distances = valid["network_distance_m"]

            corrected_distances = (
                valid["network_distance_m"]
                + valid["snap_distance_m"]
            )

            median_distance = baseline_distances.median()
            p25_distance = baseline_distances.quantile(0.25)
            p75_distance = baseline_distances.quantile(0.75)
            max_distance = baseline_distances.max()

            median_corrected_distance = corrected_distances.median()
            p25_corrected_distance = corrected_distances.quantile(0.25)
            p75_corrected_distance = corrected_distances.quantile(0.75)
            max_corrected_distance = corrected_distances.max()

        results.append({
            "GEOID": str(tract["GEOID"]),
            "sample_point_count": len(point_df),
            "valid_sample_point_count": len(valid),
            "pct_points_within_250m": (
                len(valid) / len(point_df) * 100
                if len(point_df) else float("nan")
            ),
            "median_snap_distance_m": (
                point_df["snap_distance_m"].median()
            ),
            "median_network_transit_distance_m": (
                median_distance
            ),
            "p25_network_transit_distance_m": (
                p25_distance
            ),
            "p75_network_transit_distance_m": (
                p75_distance
            ),
            "max_network_transit_distance_m": (
                max_distance
            ),
            "median_snap_adjusted_transit_distance_m": (
                median_corrected_distance
            ),
            "p25_snap_adjusted_transit_distance_m": (
                p25_corrected_distance
            ),
            "p75_snap_adjusted_transit_distance_m": (
                p75_corrected_distance
            ),
            "max_snap_adjusted_transit_distance_m": (
                max_corrected_distance
            ),
        })

    return pd.DataFrame(results)



def save_results(
    accessibility,
    tracts,
):
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

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_file(
        OUTPUT_PATH,
        layer="network_transit_accessibility",
        driver="GPKG",
    )

    distances = output[
        "median_network_transit_distance_m"
    ]

    print(
        f"Saved network accessibility dataset "
        f"to {OUTPUT_PATH}"
    )

    print(
        f"Rows: {len(output)}"
    )

    print(
        f"Unique GEOIDs: "
        f"{output['GEOID'].nunique()}"
    )

    print(
        "Median tract network distance (m): "
        f"{distances.median():.2f}"
    )

    print(
        "Maximum tract network distance (m): "
        f"{distances.max():.2f}"
    )

    print(
        "Missing network distances: "
        f"{distances.isna().sum()}"
    )


def main():
    (
        study_area,
        tracts,
        stops,
        walking_network,
    ) = load_data()

    tracts = select_study_area_tracts(
        study_area,
        tracts,
    )

    (
        walking_network,
        stop_node_set,
    ) = prepare_network(
        walking_network,
        stops,
    )

    network_distances = (
        calculate_nearest_stop_distances(
            walking_network,
            stop_node_set,
        )
    )

    accessibility = calculate_accessibility(
        tracts,
        walking_network,
        network_distances,
    )

    save_results(
        accessibility,
        tracts,
    )


if __name__ == "__main__":
    main()