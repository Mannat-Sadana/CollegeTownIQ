from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler


BASE_PATH = Path(
    "data/processed/college_town_dataset.gpkg"
)

NETWORK_PATH = Path(
    "data/processed/network_transit_accessibility.gpkg"
)

PREDICTORS = [
    "median_network_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]

TARGET = "median_gross_rent"


def load_data() -> gpd.GeoDataFrame:
    base_data = gpd.read_file(BASE_PATH)

    network_accessibility = gpd.read_file(
        NETWORK_PATH
    )[
        [
            "GEOID",
            "median_network_transit_distance_m",
        ]
    ]

    dataset = base_data.drop(
        columns=["nearest_transit_stop_distance_m"],
        errors="ignore",
    )

    dataset = dataset.merge(
        network_accessibility,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    return dataset


def main() -> None:
    dataset = load_data()

    analysis_data = dataset[
        PREDICTORS + [TARGET]
    ].dropna()

    x_data = analysis_data[PREDICTORS]
    y_data = analysis_data[TARGET]

    scaler = StandardScaler()

    x_scaled = scaler.fit_transform(x_data)

    x_scaled = pd.DataFrame(
        x_scaled,
        columns=PREDICTORS,
        index=analysis_data.index,
    )

    x_scaled = sm.add_constant(x_scaled)

    model = sm.OLS(
        y_data,
        x_scaled,
    ).fit(
        cov_type="HC3"
    )

    print(
        "CollegeTownIQ Network Accessibility "
        "Housing Regression"
    )
    print(
        "---------------------------------------"
    )

    print(
        f"Observations: {len(analysis_data)}"
    )

    print("\nRegression results:")
    print(model.summary())

    print(
        "\nRobust 95% Confidence Intervals:"
    )

    print(model.conf_int())

    print(
        "\nStandardized predictor coefficients:"
    )

    for variable in PREDICTORS:
        print(
            f"{variable}: "
            f"coefficient = "
            f"{model.params[variable]:.4f}, "
            f"p-value = "
            f"{model.pvalues[variable]:.4f}"
        )


if __name__ == "__main__":
    main()