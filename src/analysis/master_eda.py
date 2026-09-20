from pathlib import Path

import geopandas as gpd
import pandas as pd


INPUT_PATH = Path(
    "data/processed/college_town_master.gpkg"
)

OUTPUT_PATH = Path(
    "docs/master_eda_correlations.csv"
)


FEATURES = [
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "vehicle_access_pct",
    "transit_stop_count",
    "scheduled_trip_count",
    "median_transit_distance_m",
    "median_network_transit_distance_m",
    "food_access_beyond_half_mile_straight_share",
    "food_access_beyond_half_mile_network_share",
]


def load_data() -> gpd.GeoDataFrame:
    return gpd.read_file(INPUT_PATH)


def create_analysis_data(
    dataset: gpd.GeoDataFrame,
) -> pd.DataFrame:

    analysis_data = dataset[FEATURES].copy()

    return analysis_data.dropna()


def create_summary(
    analysis_data: pd.DataFrame,
) -> pd.DataFrame:

    summary = analysis_data.describe().T

    summary = summary[
        [
            "count",
            "mean",
            "std",
            "min",
            "50%",
            "max",
        ]
    ]

    summary = summary.rename(
        columns={"50%": "median"}
    )

    return summary.reset_index().rename(
        columns={"index": "feature"}
    )


def create_correlations(
    analysis_data: pd.DataFrame,
) -> pd.DataFrame:

    return analysis_data.corr()


def main() -> None:

    dataset = load_data()

    analysis_data = create_analysis_data(
        dataset
    )

    summary = create_summary(
        analysis_data
    )

    correlations = create_correlations(
        analysis_data
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary.to_csv(
        "docs/master_eda_summary.csv",
        index=False,
    )

    correlations.to_csv(
        OUTPUT_PATH
    )

    print(
        "CollegeTownIQ Master EDA"
    )
    print(
        "------------------------"
    )
    print(
        f"Master observations: {len(dataset)}"
    )
    print(
        f"Complete observations: "
        f"{len(analysis_data)}"
    )

    print("\nSummary statistics:")
    print(
        summary.to_string(index=False)
    )

    print("\nCorrelation matrix:")
    print(
        correlations.round(3).to_string()
    )

    print(
        "\nSaved EDA outputs to docs/"
    )


if __name__ == "__main__":
    main()