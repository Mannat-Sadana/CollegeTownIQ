from pathlib import Path

import geopandas as gpd
import pandas as pd


BASE_DATA_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)

FOOD_ACCESS_PATH = Path(
    "data/processed/usda_food_access_2025.csv"
)

OUTPUT_PATH = Path(
    "data/processed/college_town_food_access.gpkg"
)


def load_base_data() -> gpd.GeoDataFrame:
    return gpd.read_file(BASE_DATA_PATH)


def load_food_access_data() -> pd.DataFrame:
    food_access = pd.read_csv(
        FOOD_ACCESS_PATH,
        dtype={"GEOID": str},
    )

    food_access["GEOID"] = (
        food_access["GEOID"]
        .str.strip()
        .str.zfill(11)
    )

    return food_access


def build_dataset(
    base_data: gpd.GeoDataFrame,
    food_access: pd.DataFrame,
) -> gpd.GeoDataFrame:

    food_access = food_access[
        [
            "GEOID",
            "food_access_beyond_half_mile_straight_share",
            "food_access_beyond_half_mile_network_share",
        ]
    ].copy()

    dataset = base_data.merge(
        food_access,
        on="GEOID",
        how="left",
        validate="one_to_one",
    )

    if len(dataset) != 28:
        raise ValueError(
            f"Expected 28 study-area tracts, found {len(dataset)}."
        )

    if dataset["GEOID"].nunique() != 28:
        raise ValueError(
            "GEOID uniqueness check failed."
        )

    return dataset


def save_dataset(
    dataset: gpd.GeoDataFrame,
) -> None:

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset.to_file(
        OUTPUT_PATH,
        layer="college_town_food_access",
        driver="GPKG",
    )

    print(
        f"Saved food-access dataset to {OUTPUT_PATH}"
    )

    print(f"Rows: {len(dataset)}")
    print(
        f"Unique GEOIDs: "
        f"{dataset['GEOID'].nunique()}"
    )

    print(
        "Missing straight-line food access:",
        dataset[
            "food_access_beyond_half_mile_straight_share"
        ].isna().sum(),
    )

    print(
        "Missing network food access:",
        dataset[
            "food_access_beyond_half_mile_network_share"
        ].isna().sum(),
    )


def main() -> None:

    base_data = load_base_data()
    food_access = load_food_access_data()

    dataset = build_dataset(
        base_data,
        food_access,
    )

    save_dataset(dataset)


if __name__ == "__main__":
    main()