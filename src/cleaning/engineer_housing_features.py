from pathlib import Path

import geopandas as gpd

INPUT_PATH = Path("data/processed/college_town_tracts.gpkg")
OUTPUT_PATH = Path("data/processed/college_town_features.gpkg")


def load_dataset() -> gpd.GeoDataFrame:
    return gpd.read_file(INPUT_PATH)


def engineer_housing_features(
    dataset: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    features = dataset.copy()

    features["median_gross_rent"] = features["B25064_001E"]
    features["median_rent_burden_pct"] = features["B25071_001E"]
    features["median_household_income"] = features["B19013_001E"]

    features["households_without_vehicle"] = features["B08201_002E"]
    features["total_households_vehicle"] = features["B08201_001E"]

    features["vehicle_access_pct"] = (
        100
        * (
            features["total_households_vehicle"]
            - features["households_without_vehicle"]
        )
        / features["total_households_vehicle"]
    )

    return features


def save_features(dataset: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_file(
        OUTPUT_PATH,
        layer="college_town_features",
        driver="GPKG",
    )

    print(f"Saved engineered dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(dataset)}")


if __name__ == "__main__":
    dataset = load_dataset()
    engineered_dataset = engineer_housing_features(dataset)
    save_features(engineered_dataset)