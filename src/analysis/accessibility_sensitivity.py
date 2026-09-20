from pathlib import Path

import geopandas as gpd
import statsmodels.api as sm


BASE_PATH = Path(
    "data/processed/college_town_dataset.gpkg"
)

ACCESSIBILITY_FILES = {
    "250m": Path(
        "data/processed/transit_accessibility_250m.gpkg"
    ),
    "500m": Path(
        "data/processed/transit_accessibility_500m.gpkg"
    ),
}

PREDICTORS = [
    "median_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]

TARGET = "median_gross_rent"


def load_model_data(accessibility_path: Path) -> gpd.GeoDataFrame:
    base_data = gpd.read_file(BASE_PATH)

    accessibility = gpd.read_file(accessibility_path)[
        [
            "GEOID",
            "median_transit_distance_m",
        ]
    ]

    dataset = base_data.drop(
        columns=["nearest_transit_stop_distance_m"],
        errors="ignore",
    )

    dataset = dataset.merge(
        accessibility,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    return dataset


def run_regression(dataset: gpd.GeoDataFrame):
    analysis_data = dataset[
        PREDICTORS + [TARGET]
    ].dropna()

    x_data = analysis_data[PREDICTORS]
    y_data = analysis_data[TARGET]

    x_data = sm.add_constant(x_data)

    model = sm.OLS(y_data, x_data).fit(
        cov_type="HC3"
    )

    return model, len(analysis_data)


def main() -> None:
    print("CollegeTownIQ Accessibility Sensitivity Analysis")
    print("------------------------------------------------")

    for resolution, path in ACCESSIBILITY_FILES.items():
        dataset = load_model_data(path)

        model, observations = run_regression(dataset)

        coefficient = model.params[
            "median_transit_distance_m"
        ]

        p_value = model.pvalues[
            "median_transit_distance_m"
        ]

        confidence_interval = model.conf_int().loc[
            "median_transit_distance_m"
        ]

        print(f"\n{resolution} accessibility:")
        print(f"Observations: {observations}")
        print(
            f"Transit-distance coefficient: "
            f"{coefficient:.4f}"
        )
        print(
            f"Robust p-value: "
            f"{p_value:.4f}"
        )
        print(
            "95% CI: "
            f"[{confidence_interval.iloc[0]:.4f}, "
            f"{confidence_interval.iloc[1]:.4f}]"
        )
        print(
            f"R-squared: "
            f"{model.rsquared:.4f}"
        )


if __name__ == "__main__":
    main()