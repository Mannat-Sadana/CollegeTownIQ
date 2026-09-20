from pathlib import Path

import geopandas as gpd

OUTPUT_PATH = Path("data/processed/study_area.gpkg")

MUNICIPALITY_URL = (
    "https://gissites4.centrecountypa.gov/arcgis/rest/services/"
    "Basic2/MapServer/9/query"
)

TARGET_MUNICIPALITIES = [
    "STATE COLLEGE BORO",
    "COLLEGE TWP",
    "FERGUSON TWP",
    "HARRIS TWP",
    "PATTON TWP",
]


def load_municipalities() -> gpd.GeoDataFrame:
    url = (
        f"{MUNICIPALITY_URL}"
        "?where=1%3D1"
        "&outFields=*"
        "&f=geojson"
    )

    municipalities = gpd.read_file(url)

    return municipalities


def build_study_area(
    municipalities: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    study_area = municipalities[
        municipalities["NAME"].isin(TARGET_MUNICIPALITIES)
    ].copy()

    if len(study_area) != len(TARGET_MUNICIPALITIES):
        found = set(study_area["NAME"])
        missing = set(TARGET_MUNICIPALITIES) - found
        raise ValueError(f"Missing municipalities: {sorted(missing)}")

    study_area = study_area[
        ["NAME", "geometry"]
    ].copy()

    return study_area


def save_study_area(study_area: gpd.GeoDataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    study_area.to_file(
        OUTPUT_PATH,
        layer="study_area_municipalities",
        driver="GPKG",
    )

    print(f"Saved study area to {OUTPUT_PATH}")
    print(f"Municipalities: {len(study_area)}")
    print("Included municipalities:")
    for name in study_area["NAME"]:
        print(f"  - {name}")


if __name__ == "__main__":
    municipalities = load_municipalities()
    study_area = build_study_area(municipalities)
    save_study_area(study_area)