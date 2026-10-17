import json
from pathlib import Path

import pandas as pd

INPUT_PATH = Path("data/raw/acs_2024_centre_county_tracts.json")
OUTPUT_PATH = Path("data/processed/acs_2024_centre_county_tracts.csv")

CENSUS_MISSING_VALUE = -666666666

NUMERIC_COLUMNS = [
    "B25064_001E",
    "B25031_001E",
    "B25031_002E",
    "B25031_003E",
    "B25031_004E",
    "B25031_005E",
    "B25031_006E",
    "B25031_007E",
    "B25071_001E",
    "B19013_001E",
    "B08201_001E",
    "B08201_002E",
    "B25003_001E",
    "B25003_003E",
    "B14007_001E",
    "B14007_008E",
    "B14007_009E",
    "B01003_001E",
]


def load_raw_data() -> pd.DataFrame:
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return pd.DataFrame(data[1:], columns=data[0])


def clean_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = cleaned[column].replace(
            CENSUS_MISSING_VALUE, float("nan")
        )

    return cleaned


def save_clean_data(dataframe: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved cleaned Census data to {OUTPUT_PATH}")
    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")


if __name__ == "__main__":
    save_clean_data(clean_data(load_raw_data()))
