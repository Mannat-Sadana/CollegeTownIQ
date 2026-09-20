from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point


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
    study_area,
    tracts,
):
    tracts = tracts[
        tracts["COUNTYFP"] == "027"
    ].copy()

    study_area = study_area.to_crs(
        tracts.crs
    )

    study_area_geometry = (
        study_area.union_all()
    )

    tracts = tracts[
        tracts.geometry.intersects(
            study_area_geometry
        )
    ].copy()

    # Project tract geometries into meters before
    # generating the 250 m sample grid.
    tracts = tracts.to_crs(
        METRIC_CRS
    )

    return tracts


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

        point_distances = []

        for node in sample_nodes:
            if node in network_distances:
                point_distances.append(
                    network_distances[node]
                )

        if not point_distances:
            raise ValueError(
                f"No network distance found "
                f"for tract {tract['GEOID']}"
            )

        distances = pd.Series(
            point_distances
        )

        results.append(
            {
                "GEOID": tract["GEOID"],
                "sample_point_count": len(
                    distances
                ),
                "median_network_transit_distance_m":
                    distances.median(),
                "p25_network_transit_distance_m":
                    distances.quantile(0.25),
                "p75_network_transit_distance_m":
                    distances.quantile(0.75),
                "max_network_transit_distance_m":
                    distances.max(),
            }
        )

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