from pathlib import Path
import zipfile

import pandas as pd


ZIP_PATH = Path(
    "data/raw/2025-sram-fara-data.zip"
)

OUTPUT_PATH = Path(
    "data/processed/usda_food_access_2025.csv"
)

ENCODING = "latin-1"

TARGET_PREFIX = "42027"

STRAIGHT_LINE_COLUMN = (
    "SD_SRAM_lapophalfshare"
)

NETWORK_COLUMN = (
    "DD_SRAM_lapophalfshare"
)

def extract_food_access_data() -> pd.DataFrame:
    with zipfile.ZipFile(ZIP_PATH) as zip_file:

        with zip_file.open(
            "SRAM Straight Line Distance Data.csv"
        ) as file:
            straight_line = pd.read_csv(
                file,
                usecols=[
                    "CensusTract20",
                    STRAIGHT_LINE_COLUMN,
                ],
                encoding=ENCODING,
                dtype={
                    "CensusTract20": str,
                },
            )

        with zip_file.open(
            "SRAM Driving Distance Data.csv"
        ) as file:
            network = pd.read_csv(
                file,
                usecols=[
                    "CensusTract20",
                    NETWORK_COLUMN,
                ],
                encoding=ENCODING,
                dtype={
                    "CensusTract20": str,
                },
            )

    straight_line = straight_line[
        straight_line["CensusTract20"].str.startswith(
            TARGET_PREFIX
        )
    ].copy()

    network = network[
        network["CensusTract20"].str.startswith(
            TARGET_PREFIX
        )
    ].copy()

    data = straight_line.merge(
        network,
        on="CensusTract20",
        how="inner",
        validate="one_to_one",
    )

    data = data.rename(
        columns={
            "CensusTract20": "GEOID",
            STRAIGHT_LINE_COLUMN:
                "food_access_beyond_half_mile_straight_share",
            NETWORK_COLUMN:
                "food_access_beyond_half_mile_network_share",
        }
    )

    return data


def validate_data(data: pd.DataFrame) -> None:
    if len(data) != 41:
        raise ValueError(
            f"Expected 41 Centre County tracts, "
            f"found {len(data)}."
        )

    if data["GEOID"].nunique() != 41:
        raise ValueError(
            "GEOID values are not unique."
        )

    for column in [
        "food_access_beyond_half_mile_straight_share",
        "food_access_beyond_half_mile_network_share",
    ]:
        values = pd.to_numeric(
            data[column],
            errors="coerce",
        )

        invalid = values.dropna()[
            (values.dropna() < 0)
            | (values.dropna() > 100)
        ]

        if len(invalid) > 0:
            raise ValueError(
                f"Invalid share values found "
                f"in {column}."
            )


def save_data(data: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Saved USDA food-access data to "
        f"{OUTPUT_PATH}"
    )

    print(
        f"Rows: {len(data)}"
    )

    print(
        f"Unique GEOIDs: "
        f"{data['GEOID'].nunique()}"
    )

    print("\nColumns:")
    for column in data.columns:
        print(f"  - {column}")


def main() -> None:
    data = extract_food_access_data()

    validate_data(data)

    save_data(data)

    print("\nPreview:")
    print(data.head().to_string(index=False))


if __name__ == "__main__":
    main()