
from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm

INPUT_PATH = Path("data/processed/college_town_analysis.gpkg")
OUTPUT_PATH = Path("docs/confounding_check.csv")

TARGET = "median_gross_rent"

# Approximate Old Main reference point, Penn State University Park.
# Coordinates are longitude, latitude in EPSG:4326.
OLD_MAIN_LON = -77.8651
OLD_MAIN_LAT = 40.7982


def main():
    gdf = gpd.read_file(INPUT_PATH)

    required = [
        "GEOID",
        TARGET,
        "median_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
        "renter_share_pct",
        "college_enrollment_share_pct",
        "geometry",
    ]

    missing = [c for c in required if c not in gdf.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Project to Pennsylvania South State Plane, in meters.
    projected = gdf.to_crs("EPSG:2272").copy()

    # Use one representative point per tract.
    # Unlike a centroid, this point is guaranteed to lie within the tract.
    tract_points = projected.geometry.representative_point()

    campus = gpd.GeoSeries(
        gpd.points_from_xy([OLD_MAIN_LON], [OLD_MAIN_LAT]),
        crs="EPSG:4326",
    ).to_crs(projected.crs).iloc[0]

    projected["distance_to_old_main_km"] = (
        tract_points.distance(campus) / 1000
    )

    data = pd.DataFrame(projected.drop(columns="geometry"))
    data["transit_distance_km"] = (
        data["median_transit_distance_m"] / 1000
    )
    data["income_10k"] = (
        data["median_household_income"] / 10000
    )

    base = [
        "transit_distance_km",
        "income_10k",
        "vehicle_access_pct",
    ]

    models = {
        "Original controls": base,
        "Plus renter share": base + ["renter_share_pct"],
        "Plus enrollment proxy": base + [
            "college_enrollment_share_pct"
        ],
        "Both new controls": base + [
            "renter_share_pct",
            "college_enrollment_share_pct",
        ],
        "Original + distance to Old Main": base + [
            "distance_to_old_main_km"
        ],
        "All controls + distance to Old Main": base + [
            "renter_share_pct",
            "college_enrollment_share_pct",
            "distance_to_old_main_km",
        ],
    }

    results = []

    for name, predictors in models.items():
        subset = data[["GEOID", TARGET] + predictors].dropna()

        x = sm.add_constant(subset[predictors])
        fit = sm.OLS(subset[TARGET], x).fit(cov_type="HC3")
        ci = fit.conf_int().loc["transit_distance_km"]

        results.append({
            "model": name,
            "observations": len(subset),
            "r_squared": fit.rsquared,
            "transit_coefficient_per_km": (
                fit.params["transit_distance_km"]
            ),
            "transit_p_value": (
                fit.pvalues["transit_distance_km"]
            ),
            "transit_ci_lower": ci.iloc[0],
            "transit_ci_upper": ci.iloc[1],
        })

    result_df = pd.DataFrame(results)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False)

    print("\nConfounding check — exploratory, observational")
    print("Geographic control: distance from tract representative point to Old Main")
    print(result_df.round(4).to_string(index=False))
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
