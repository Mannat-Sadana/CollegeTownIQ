
from pathlib import Path

import geopandas as gpd
import pandas as pd


INPUT_PATH = Path("data/processed/college_town_dataset.gpkg")
OUTPUT_PATH = Path("docs/missing_data_details.csv")

CHECK_COLUMNS = [
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "vehicle_access_pct",
    "annual_rent_to_income_ratio",
]


def main():
    dataset = gpd.read_file(INPUT_PATH)

    # Identify a tract identifier column if one is available.
    possible_ids = ["GEOID", "geoid", "GEOID20", "tract_id", "NAME"]
    id_column = next(
        (column for column in possible_ids if column in dataset.columns),
        None,
    )

    print(f"Total census tracts: {len(dataset)}")
    print(f"Tract identifier: {id_column or 'Not found'}")
    print("\nMissing-value counts:")

    for column in CHECK_COLUMNS:
        if column not in dataset.columns:
            print(f"{column}: COLUMN NOT FOUND")
            continue

        values = pd.to_numeric(dataset[column], errors="coerce")
        print(f"{column}: {values.isna().sum()}")

    # Show the specific tracts with missing values.
    available_columns = [
        column for column in CHECK_COLUMNS
        if column in dataset.columns
    ]

    missing_mask = dataset[available_columns].isna().any(axis=1)
    details = dataset.loc[missing_mask].copy()

    display_columns = (
        ([id_column] if id_column else [])
        + available_columns
    )

    print("\nTracts with at least one missing value:")
    if details.empty:
        print("None")
    else:
        print(details[display_columns].to_string(index=False))

    # Save a separate diagnostic file, leaving the original data unchanged.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    details[display_columns].to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved details to {OUTPUT_PATH}")

    # Check unusually high rent-to-income ratios.
    if "annual_rent_to_income_ratio" in dataset.columns:
        ratio = pd.to_numeric(
            dataset["annual_rent_to_income_ratio"],
            errors="coerce",
        )
        print("\nHighest annual rent-to-income ratios:")
        top = dataset.loc[ratio.nlargest(5).index, display_columns]
        print(top.to_string(index=False))


if __name__ == "__main__":
    main()
