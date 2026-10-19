import geopandas as gpd
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt

from shapely.geometry import Point

from src.geospatial.calculate_network_accessibility import (
    TRACTS_PATH,
    STUDY_AREA_PATH,
    NETWORK_PATH,
    METRIC_CRS,
    GRID_SPACING_METERS,
    select_study_area_tracts,
    create_sample_points,
)

OUTPUT_DIR = "data/processed"
MAP_PATH = f"{OUTPUT_DIR}/network_coverage_diagnostic.png"
CSV_PATH = f"{OUTPUT_DIR}/network_snap_diagnostic.csv"

# Load and project the study area and census tracts.
study_area = gpd.read_file(STUDY_AREA_PATH)
tracts = select_study_area_tracts(
    study_area,
    gpd.read_file(TRACTS_PATH),
)

# Load the existing walking network.
graph = ox.load_graphml(NETWORK_PATH)
graph = ox.project_graph(graph, to_crs=METRIC_CRS)

nodes, edges = ox.graph_to_gdfs(graph)

# Build a point-level diagnostic dataset.
rows = []

for _, tract in tracts.iterrows():
    points = create_sample_points(
        tract.geometry,
        GRID_SPACING_METERS,
    )

    nearest_nodes = ox.distance.nearest_nodes(
        graph,
        X=[point.x for point in points],
        Y=[point.y for point in points],
    )

    for point, node in zip(points, nearest_nodes):
        snap_distance = point.distance(nodes.loc[node].geometry)

        rows.append({
            "GEOID": str(tract["GEOID"]),
            "snap_distance_m": snap_distance,
            "geometry": point,
        })

samples = gpd.GeoDataFrame(
    rows,
    geometry="geometry",
    crs=METRIC_CRS,
)

samples["snap_category"] = pd.cut(
    samples["snap_distance_m"],
    bins=[-1, 50, 100, 250, 500, float("inf")],
    labels=[
        "0–50 m",
        "50–100 m",
        "100–250 m",
        "250–500 m",
        ">500 m",
    ],
)

# Save exact point-level distances for further investigation.
samples.drop(columns="geometry").to_csv(CSV_PATH, index=False)

# Plot the network and sample points.
fig, ax = plt.subplots(figsize=(13, 11))

tracts.boundary.plot(
    ax=ax,
    color="black",
    linewidth=0.8,
)

edges.plot(
    ax=ax,
    color="gray",
    linewidth=0.35,
    alpha=0.65,
)

colors = {
    "0–50 m": "#2c7bb6",
    "50–100 m": "#abd9e9",
    "100–250 m": "#ffffbf",
    "250–500 m": "#fdae61",
    ">500 m": "#d7191c",
}

for category, color in colors.items():
    subset = samples[samples["snap_category"] == category]

    if not subset.empty:
        subset.plot(
            ax=ax,
            color=color,
            markersize=5,
            alpha=0.8,
            label=category,
        )

stops = gpd.read_file("data/processed/cata_stops.gpkg")

if stops.crs is None:
    print("WARNING: CATA stops have no CRS; not plotting them.")
else:
    stops = stops.to_crs(METRIC_CRS)
    stops.plot(
        ax=ax,
        color="purple",
        marker="^",
        markersize=18,
        label="Transit stops",
    )

ax.set_title(
    "Walking Network Coverage Diagnostic\n"
    "Sample-point distance to nearest network node"
)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.legend(title="Snap distance", loc="best")
ax.set_aspect("equal")
plt.tight_layout()
plt.savefig(MAP_PATH, dpi=220, bbox_inches="tight")
plt.close()

print(f"Saved map: {MAP_PATH}")
print(f"Saved point-level data: {CSV_PATH}")

print("\n=== SNAP DISTANCE BY TRACT ===")
summary = samples.groupby("GEOID", observed=True).agg(
    sample_count=("snap_distance_m", "size"),
    median_snap_m=("snap_distance_m", "median"),
    p95_snap_m=("snap_distance_m", lambda x: x.quantile(0.95)),
    pct_over_250m=("snap_distance_m", lambda x: (x > 250).mean() * 100),
    pct_over_500m=("snap_distance_m", lambda x: (x > 500).mean() * 100),
).sort_values("p95_snap_m", ascending=False)

print(summary.round(1).to_string())
