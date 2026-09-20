from pathlib import Path

import geopandas as gpd
import pandas as pd


STRAIGHT_LINE_PATH = Path(
    "data/processed/transit_accessibility_250m.gpkg"
)

NETWORK_PATH = Path(
    "data/processed/network_transit_accessibility.gpkg"
)


def main() -> None:
    straight_line = gpd.read_file(
        STRAIGHT_LINE_PATH
    )[
        [
            "GEOID",
            "median_transit_distance_m",
        ]
    ]

    network = gpd.read_file(
        NETWORK_PATH
    )[
        [
            "GEOID",
            "median_network_transit_distance_m",
        ]
    ]

    comparison = straight_line.merge(
        network,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    comparison["absolute_difference_m"] = (
        comparison[
            "median_network_transit_distance_m"
        ]
        - comparison["median_transit_distance_m"]
    ).abs()

    comparison["network_to_straight_ratio"] = (
        comparison[
            "median_network_transit_distance_m"
        ]
        / comparison[
            "median_transit_distance_m"
        ]
    )

    print(
        "CollegeTownIQ Accessibility Method Comparison"
    )
    print(
        "----------------------------------------------"
    )

    print(
        f"Tracts compared: {len(comparison)}"
    )

    print("\nStraight-line accessibility:")
    print(
        comparison[
            "median_transit_distance_m"
        ].describe()
    )

    print("\nNetwork accessibility:")
    print(
        comparison[
            "median_network_transit_distance_m"
        ].describe()
    )

    print("\nMethod differences:")
    print(
        "Mean absolute difference (m): "
        f"{comparison['absolute_difference_m'].mean():.2f}"
    )

    print(
        "Median absolute difference (m): "
        f"{comparison['absolute_difference_m'].median():.2f}"
    )

    print(
        "Maximum absolute difference (m): "
        f"{comparison['absolute_difference_m'].max():.2f}"
    )

    print(
        "Mean network / straight-line ratio: "
        f"{comparison['network_to_straight_ratio'].mean():.2f}"
    )

    print(
        "Median network / straight-line ratio: "
        f"{comparison['network_to_straight_ratio'].median():.2f}"
    )

    correlation = comparison[
        [
            "median_transit_distance_m",
            "median_network_transit_distance_m",
        ]
    ].corr().iloc[0, 1]

    print(
        "Correlation between methods: "
        f"{correlation:.4f}"
    )


if __name__ == "__main__":
    main()