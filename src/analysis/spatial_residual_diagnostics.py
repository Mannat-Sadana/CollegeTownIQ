from pathlib import Path

import geopandas as gpd
import statsmodels.api as sm
from libpysal.weights import Queen
from esda.moran import Moran


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)

PREDICTORS = [
    "median_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]

TARGET = "median_gross_rent"


def main() -> None:
    dataset = gpd.read_file(INPUT_PATH)

    analysis_data = dataset[
        ["GEOID", "geometry"] + PREDICTORS + [TARGET]
    ].dropna().copy()

    x_data = analysis_data[PREDICTORS]
    y_data = analysis_data[TARGET]

    x_data = sm.add_constant(x_data)

    model = sm.OLS(y_data, x_data).fit(
        cov_type="HC3"
    )

    analysis_data["residual"] = model.resid

    # Queen contiguity defines neighboring tracts
    # based on shared boundaries.
    weights = Queen.from_dataframe(
        analysis_data,
        use_index=False,
    )

    weights.transform = "r"

    moran = Moran(
        analysis_data["residual"],
        weights,
        permutations=999,
    )

    print("CollegeTownIQ Spatial Residual Diagnostics")
    print("------------------------------------------")
    print(
        f"Observations: {len(analysis_data)}"
    )

    print("\nQueen-neighbor structure:")
    print(
        f"Tracts: {weights.n}"
    )
    print(
        f"Average neighbors: "
        f"{sum(len(neighbors) for neighbors in weights.neighbors.values()) / weights.n:.2f}"
    )

    print("\nMoran's I:")
    print(
        f"I statistic: {moran.I:.4f}"
    )
    print(
        f"Expected I: {moran.EI:.4f}"
    )
    print(
        f"Permutation p-value: "
        f"{moran.p_sim:.4f}"
    )

    if moran.p_sim < 0.05:
        print(
            "\nResult: Evidence of spatial autocorrelation "
            "in the regression residuals."
        )
    else:
        print(
            "\nResult: No statistically significant spatial "
            "autocorrelation detected in the regression residuals."
        )


if __name__ == "__main__":
    main()