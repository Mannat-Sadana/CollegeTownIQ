from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)

OUTPUT_DIR = Path("docs/figures")


def load_data() -> gpd.GeoDataFrame:
    return gpd.read_file(INPUT_PATH)


def create_scatterplots(
    dataset: gpd.GeoDataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    analysis_data = dataset.dropna(
        subset=[
            "median_gross_rent",
            "median_transit_distance_m",
            "annual_rent_to_income_ratio",
        ]
    ).copy()

    figure, axis = plt.subplots(figsize=(8, 6))

    axis.scatter(
        analysis_data["median_transit_distance_m"],
        analysis_data["median_gross_rent"],
    )

    axis.set_xlabel(
        "Median distance to nearest transit stop (m)"
    )
    axis.set_ylabel("Median gross rent ($)")
    axis.set_title(
        "Housing Cost and Transit Accessibility"
    )

    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "rent_vs_transit_accessibility.png",
        dpi=300,
    )
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 6))

    axis.scatter(
        analysis_data["median_transit_distance_m"],
        analysis_data["annual_rent_to_income_ratio"],
    )

    axis.set_xlabel(
        "Median distance to nearest transit stop (m)"
    )
    axis.set_ylabel(
        "Annual rent-to-income ratio"
    )
    axis.set_title(
        "Rent Burden and Transit Accessibility"
    )

    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "rent_burden_vs_transit_accessibility.png",
        dpi=300,
    )
    plt.close(figure)

    print(
        "Saved figures to "
        f"{OUTPUT_DIR}"
    )
    print(
        f"Observations plotted: "
        f"{len(analysis_data)}"
    )


if __name__ == "__main__":
    dataset = load_data()
    create_scatterplots(dataset)