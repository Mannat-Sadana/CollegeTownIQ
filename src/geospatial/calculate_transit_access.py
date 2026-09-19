import geopandas as gpd

TRACTS_PATH = "data/processed/college_town_features.gpkg"
TRANSIT_DISTANCE_PATH = "data/processed/transit_distance.gpkg"
OUTPUT_PATH = "data/processed/transit_access.gpkg"

PROJECTED_CRS = "EPSG:26918"


def calculate_transit_access() -> None:
    tracts = gpd.read_file(TRACTS_PATH)
    transit_distances = gpd.read_file(TRANSIT_DISTANCE_PATH)

    tracts = tracts.to_crs(PROJECTED_CRS)
    transit_distances = transit_distances.to_crs(PROJECTED_CRS)

    stop_counts = (
        transit_distances.groupby("GEOID")
        .size()
        .rename("transit_stop_count")
        .reset_index()
    )

    nearest_distances = (
        transit_distances.groupby("GEOID")["nearest_transit_stop_distance_m"]
        .min()
        .rename("nearest_transit_stop_distance_m")
        .reset_index()
    )

    transit_access = tracts.merge(
        stop_counts,
        on="GEOID",
        how="left",
    )

    transit_access = transit_access.merge(
        nearest_distances,
        on="GEOID",
        how="left",
    )

    transit_access["transit_stop_count"] = (
        transit_access["transit_stop_count"]
        .fillna(0)
        .astype(int)
    )

    transit_access.to_file(
        OUTPUT_PATH,
        driver="GPKG",
    )

    print(f"Saved transit access dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(transit_access)}")
    print(
        "Tracts with transit stops:",
        (transit_access["transit_stop_count"] > 0).sum(),
    )
    print(
        "Total assigned stops:",
        transit_access["transit_stop_count"].sum(),
    )
    print(
        "Nearest-stop distance available for:",
        transit_access["nearest_transit_stop_distance_m"].notna().sum(),
        "tracts",
    )


if __name__ == "__main__":
    calculate_transit_access()