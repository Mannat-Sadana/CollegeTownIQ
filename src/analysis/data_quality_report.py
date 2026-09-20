from pathlib import Path

import geopandas as gpd
import pandas as pd


INPUT_PATH = Path("data/processed/college_town_dataset.gpkg")
OUTPUT_PATH = Path("docs/data_quality_report.csv")


NUMERIC_FEATURES = [
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "households_without_vehicle",
    "total_households_vehicle",
    "vehicle_access_pct",
    "transit_stop_count",
    "nearest_transit_stop_distance_m",
    "scheduled_trip_count",
    "scheduled_stop_events",
    "annual_rent_to_income_ratio",
]


def create_quality_report() -> pd.DataFrame:
    dataset = gpd.read_file(INPUT_PATH)

    report = []

    for column in NUMERIC_FEATURES:
        values = pd.to_numeric(
            dataset[column],
            errors="coerce",
        )

        report.append(
            {
                "feature": column,
                "rows": len(values),
                "missing_values": int(values.isna().sum()),
                "non_missing_values": int(values.notna().sum()),
                "minimum": values.min(),
                "median": values.median(),
                "maximum": values.max(),
            }
        )

    return pd.DataFrame(report)


def save_report(report: pd.DataFrame) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Saved data-quality report to {OUTPUT_PATH}")
    print(f"Features checked: {len(report)}")
    print(f"Rows checked: {report['rows'].iloc[0]}")


if __name__ == "__main__":
    quality_report = create_quality_report()
    save_report(quality_report)
    print(quality_report.to_string(index=False))