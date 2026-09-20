from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt


INPUT_PATH = Path("data/processed/college_town_master.gpkg")
OUTPUT_DIR = Path("docs/figures/maps")


def load_data() -> gpd.GeoDataFrame:
    return gpd.read_file(INPUT_PATH)


def create_map(
    dataset: gpd.GeoDataFrame,
    column: str,
    title: str,
    legend_label: str,
    filename: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 8))

    dataset.plot(
        column=column,
        ax=axis,
        legend=True,
        scheme="quantiles",
        k=5,
        edgecolor="black",
        linewidth=0.4,
        legend_kwds={
            "title": legend_label,
            "loc": "lower left",
        },
    )

    axis.set_title(
        title,
        fontsize=15,
        fontweight="bold",
        pad=12,
    )

    axis.set_axis_off()

    figure.tight_layout()

    output_path = OUTPUT_DIR / filename
    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    print(f"Saved: {output_path}")


def main() -> None:
    dataset = load_data()

    print("CollegeTownIQ Geospatial Maps")
    print("============================")
    print(f"Tracts: {len(dataset)}")
    print(f"Unique GEOIDs: {dataset['GEOID'].nunique()}")

    create_map(
        dataset,
        column="median_gross_rent",
        title="Median Gross Rent Across the CollegeTownIQ Study Area",
        legend_label="Median gross rent ($)",
        filename="median_gross_rent_map.png",
    )

    create_map(
        dataset,
        column="median_transit_distance_m",
        title="Network Transit Accessibility Across the CollegeTownIQ Study Area",
        legend_label="Median pedestrian-network distance to transit stop (m)",
        filename="transit_accessibility_map.png",
    )

    create_map(
        dataset,
        column="food_access_beyond_half_mile_network_share",
        title="Food Access Across the CollegeTownIQ Study Area",
        legend_label="Share beyond 1/2 mile (%)",
        filename="food_access_map.png",
    )

    print()
    print("All maps created successfully.")


if __name__ == "__main__":
    main()