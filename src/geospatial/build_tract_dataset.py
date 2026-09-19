from pathlib import Path

import geopandas as gpd
import pandas as pd

ACS_PATH = Path("data/processed/acs_2024_centre_county_tracts.csv")
TRACTS_PATH = Path(
    "data/raw/tiger_2024_pa_tracts/tl_2024_42_tract.shp"
)
OUTPUT_PATH = Path(
    "data/processed/college_town_tracts.gpkg"
)


def load_acs_data() -> pd.DataFrame:
    return pd.read_csv(
        ACS_PATH,
        dtype={
            "state": str,
            "county": str,
            "tract": str,
        },
    )


def load_centre_county_tracts() -> gpd.GeoDataFrame:
    tracts = gpd.read_file(TRACTS_PATH)
    return tracts[tracts["COUNTYFP"] == "027"].copy()


def build_geoid(acs_data: pd.DataFrame) -> pd.DataFrame:
    acs_data = acs_data.copy()

    acs_data["GEOID"] = (
        acs_data["state"].str.zfill(2)
        + acs_data["county"].str.zfill(3)
        + acs_data["tract"].str.zfill(6)
    )

    return acs_data


def build_geospatial_dataset() -> gpd.GeoDataFrame:
    acs_data = build_geoid(load_acs_data())
    tract_geometries = load_centre_county_tracts()

    dataset = tract_geometries.merge(
        acs_data,
        on="GEOID",
        how="inner",
    )

    return dataset


def save_dataset(dataset: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_file(
        OUTPUT_PATH,
        layer="centre_county_tracts",
        driver="GPKG",
    )

    print(f"Saved geospatial dataset to {OUTPUT_PATH}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")


if __name__ == "__main__":
    tract_dataset = build_geospatial_dataset()
    save_dataset(tract_dataset)