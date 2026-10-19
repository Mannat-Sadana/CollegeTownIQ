import geopandas as gpd
import pandas as pd

original_path = (
    "data/processed/"
    "network_transit_accessibility_before_qc.gpkg"
)

filtered_path = (
    "data/processed/"
    "network_transit_accessibility.gpkg"
)

original = gpd.read_file(original_path)
filtered = gpd.read_file(filtered_path)

original["GEOID"] = original["GEOID"].astype(str)
filtered["GEOID"] = filtered["GEOID"].astype(str)

original = original[
    ["GEOID", "median_network_transit_distance_m"]
].rename(columns={
    "median_network_transit_distance_m":
        "original_median_m"
})

filtered = filtered[
    [
        "GEOID",
        "median_network_transit_distance_m",
        "pct_points_within_250m",
    ]
].rename(columns={
    "median_network_transit_distance_m":
        "filtered_median_m"
})

comparison = original.merge(
    filtered,
    on="GEOID",
    validate="one_to_one",
)

comparison["coverage_class"] = pd.cut(
    comparison["pct_points_within_250m"],
    bins=[-0.01, 70, 90, 100.01],
    labels=[
        "Low coverage",
        "Moderate coverage",
        "High coverage",
    ],
)

comparison["change_m"] = (
    comparison["filtered_median_m"]
    - comparison["original_median_m"]
)

print("\n=== ORIGINAL VS FILTERED DISTANCE ===")
print(
    comparison.sort_values("pct_points_within_250m")[
        [
            "GEOID",
            "original_median_m",
            "filtered_median_m",
            "change_m",
            "pct_points_within_250m",
            "coverage_class",
        ]
    ].round(1).to_string(index=False)
)

print("\n=== MEDIAN DISTANCES ===")
print(
    comparison[
        ["original_median_m", "filtered_median_m"]
    ].describe().round(1).to_string()
)

comparison.to_csv(
    "data/processed/network_accessibility_comparison.csv",
    index=False,
)

print(
    "\nSaved comparison to "
    "data/processed/network_accessibility_comparison.csv"
)
