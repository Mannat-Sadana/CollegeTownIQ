from pathlib import Path

import geopandas as gpd
import osmnx as ox


STUDY_AREA_PATH = Path(
    "data/processed/study_area.gpkg"
)

OUTPUT_PATH = Path(
    "data/processed/walking_network.graphml"
)


def load_study_area() -> gpd.GeoDataFrame:
    return gpd.read_file(STUDY_AREA_PATH)


def build_walking_network(
    study_area: gpd.GeoDataFrame,
):
    study_area_wgs84 = study_area.to_crs("EPSG:4326")

    boundary = study_area_wgs84.union_all()

    print("Downloading pedestrian street network...")
    print("Study area: State College region")

    graph = ox.graph_from_polygon(
        boundary,
        network_type="walk",
        simplify=True,
    )

    return graph


def save_network(graph) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ox.save_graphml(
        graph,
        filepath=OUTPUT_PATH,
    )

    print(
        f"Saved walking network to {OUTPUT_PATH}"
    )
    print(
        f"Nodes: {len(graph.nodes):,}"
    )
    print(
        f"Edges: {len(graph.edges):,}"
    )


def main() -> None:
    study_area = load_study_area()

    walking_network = build_walking_network(
        study_area
    )

    save_network(walking_network)


if __name__ == "__main__":
    main()