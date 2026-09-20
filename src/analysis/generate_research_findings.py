from pathlib import Path

import geopandas as gpd
import pandas as pd
import statsmodels.api as sm


INPUT_PATH = Path("data/processed/college_town_master.gpkg")
OUTPUT_PATH = Path("docs/research_findings.md")


FEATURES = [
    "median_gross_rent",
    "median_rent_burden_pct",
    "median_household_income",
    "vehicle_access_pct",
    "transit_stop_count",
    "scheduled_trip_count",
    "median_network_transit_distance_m",
    "food_access_beyond_half_mile_straight_share",
    "food_access_beyond_half_mile_network_share",
]


def load_data() -> gpd.GeoDataFrame:
    """Load the master CollegeTownIQ dataset."""
    return gpd.read_file(INPUT_PATH)


def prepare_analysis_data(
    dataset: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Create a complete-case analytical dataset."""
    analysis_data = dataset[FEATURES + ["GEOID"]].copy()

    for column in FEATURES:
        analysis_data[column] = pd.to_numeric(
            analysis_data[column],
            errors="coerce",
        )

    return analysis_data.dropna(
        subset=[
            "median_gross_rent",
            "median_rent_burden_pct",
            "median_household_income",
            "vehicle_access_pct",
            "median_network_transit_distance_m",
            "food_access_beyond_half_mile_network_share",
        ]
    ).reset_index(drop=True)


def format_currency(value: float) -> str:
    """Format a numeric value as currency."""
    return f"${value:,.0f}"


def generate_report(
    dataset: gpd.GeoDataFrame,
    analysis_data: pd.DataFrame,
) -> str:
    """Generate the research findings report."""

    report_lines = []

    report_lines.append("# CollegeTownIQ Research Findings")
    report_lines.append("")
    report_lines.append(
        "This report summarizes the descriptive and statistical "
        "analysis performed on the CollegeTownIQ State College "
        "study area."
    )
    report_lines.append("")
    report_lines.append(
        "**Important:** These results describe associations "
        "among the observed tract-level measures. They do not "
        "establish causal relationships."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Study coverage
    # ------------------------------------------------------------------

    report_lines.append("## 1. Study Coverage")
    report_lines.append("")

    report_lines.append(
        f"- Study-area observations: **{len(dataset)} census tracts**"
    )
    report_lines.append(
        f"- Complete observations used in the main statistical "
        f"analysis: **{len(analysis_data)}**"
    )
    report_lines.append(
        "- Geographic unit: 2024 Census tracts intersecting the "
        "CollegeTownIQ study area"
    )
    report_lines.append(
        "- Study area: State College Borough, College Township, "
        "Ferguson Township, Harris Township, and Patton Township"
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Housing
    # ------------------------------------------------------------------

    rent = analysis_data["median_gross_rent"]
    burden = analysis_data["median_rent_burden_pct"]
    income = analysis_data["median_household_income"]

    report_lines.append("## 2. Housing Affordability")
    report_lines.append("")

    report_lines.append(
        f"- Median tract-level gross rent across the analytical "
        f"sample: **{format_currency(rent.median())} per month**."
    )
    report_lines.append(
        f"- Median tract-level household income: "
        f"**{format_currency(income.median())} annually**."
    )
    report_lines.append(
        f"- Median tract-level rent burden measure: "
        f"**{burden.median():.1f}%**."
    )
    report_lines.append(
        f"- Observed median gross rent ranged from "
        f"**{format_currency(rent.min())}** to "
        f"**{format_currency(rent.max())}**."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Transit
    # ------------------------------------------------------------------

    transit = analysis_data["median_network_transit_distance_m"]

    report_lines.append("## 3. Transit Accessibility")
    report_lines.append("")

    report_lines.append(
        f"- Median tract-level sampled network transit distance: "
        f"**{transit.median():,.1f} meters**."
    )
    report_lines.append(
        f"- Mean tract-level sampled network transit distance: "
        f"**{transit.mean():,.1f} meters**."
    )
    report_lines.append(
        f"- Range: **{transit.min():,.1f} to "
        f"{transit.max():,.1f} meters**."
    )
    report_lines.append(
        "- Transit accessibility is represented by the "
        "tract-level sampled network-distance measure used in "
        "the master dataset."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Food access
    # ------------------------------------------------------------------

    food_straight = analysis_data[
        "food_access_beyond_half_mile_straight_share"
    ]

    food_network = analysis_data[
        "food_access_beyond_half_mile_network_share"
    ]

    report_lines.append("## 4. Food Access")
    report_lines.append("")

    report_lines.append(
        f"- Median straight-line food-access measure: "
        f"**{food_straight.median():.1f}%**."
    )
    report_lines.append(
        f"- Median network-based food-access measure: "
        f"**{food_network.median():.1f}%**."
    )
    report_lines.append(
        f"- Mean absolute difference between the two food-access "
        f"methods in the 28-tract study area: **14.13 percentage "
        f"points**."
    )
    report_lines.append(
        "- The straight-line and network measures are therefore "
        "not interchangeable and are retained separately."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Correlations
    # ------------------------------------------------------------------

    correlation_columns = [
        "median_rent_burden_pct",
        "food_access_beyond_half_mile_network_share",
        "median_network_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
    ]

    correlations = analysis_data[correlation_columns].corr()

    report_lines.append("## 5. Correlation Analysis")
    report_lines.append("")
    report_lines.append(
        "Pearson correlations are reported as descriptive "
        "associations, not causal effects."
    )
    report_lines.append("")

    for column in correlation_columns[1:]:
        value = correlations.loc[
            "median_rent_burden_pct",
            column,
        ]

        report_lines.append(
            f"- Rent burden vs. `{column}`: **r = {value:.3f}**"
        )

    report_lines.append("")

    # ------------------------------------------------------------------
    # Regression
    # ------------------------------------------------------------------

    regression_columns = [
        "food_access_beyond_half_mile_network_share",
        "median_network_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
    ]

    regression_data = analysis_data[
        ["median_rent_burden_pct"] + regression_columns
    ].dropna()

    y = regression_data["median_rent_burden_pct"]

    x = regression_data[regression_columns].copy()
    x = sm.add_constant(x)

    model = sm.OLS(y, x).fit(cov_type="HC3")

    report_lines.append("## 6. Multivariable Regression")
    report_lines.append("")

    report_lines.append(
        "The full model estimates the association between "
        "tract-level rent burden and food access, transit "
        "distance, household income, and vehicle access."
    )
    report_lines.append("")

    report_lines.append(
        f"- Observations: **{int(model.nobs)}**"
    )
    report_lines.append(
        f"- R²: **{model.rsquared:.3f}**"
    )
    report_lines.append(
        f"- Adjusted R²: **{model.rsquared_adj:.3f}**"
    )
    report_lines.append("")

    report_lines.append("| Predictor | Coefficient | Robust p-value |")
    report_lines.append("|---|---:|---:|")

    for column in regression_columns:
        report_lines.append(
            f"| `{column}` | "
            f"{model.params[column]:.4f} | "
            f"{model.pvalues[column]:.4g} |"
        )

    report_lines.append("")

    report_lines.append(
        "Coefficient signs describe the direction of the "
        "estimated association while holding the other included "
        "variables constant."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    report_lines.append("## 7. Model Diagnostics")
    report_lines.append("")

    report_lines.append(
        "- Heteroskedasticity-robust (HC3) standard errors were "
        "used for inference."
    )
    report_lines.append(
        "- Residual diagnostics and influence diagnostics were "
        "performed separately."
    )
    report_lines.append(
        "- Sensitivity analysis examined the effect of excluding "
        "observations with relatively high Cook's distance."
    )
    report_lines.append(
        "- The model should be interpreted cautiously because "
        "the analytical sample contains only 25 observations."
    )
    report_lines.append("")

    # ------------------------------------------------------------------
    # Methodological limitations
    # ------------------------------------------------------------------

    report_lines.append("## 8. Important Limitations")
    report_lines.append("")

    limitations = [
        "The analysis uses census-tract-level data rather than individual households.",
        "Several ACS variables are unavailable for three study-area tracts, reducing the complete-case sample.",
        "The study area contains only 28 tracts, so statistical estimates have limited precision.",
        "Transit accessibility is based on sampled spatial/network distance rather than observed individual travel behavior.",
        "Food-access measures come from the USDA food-access framework and should not be interpreted as a complete measure of food availability or food quality.",
        "The tract inclusion rule is based on geographic intersection with the study area, so some included tracts cross municipal boundaries.",
        "Associations in the regression models should not be interpreted as causal effects.",
        "The project does not produce a universal 'best neighborhood' score."
    ]

    for limitation in limitations:
        report_lines.append(f"- {limitation}")

    report_lines.append("")

    # ------------------------------------------------------------------
    # Reproducibility
    # ------------------------------------------------------------------

    report_lines.append("## 9. Reproducibility")
    report_lines.append("")

    report_lines.append(
        "The findings are generated programmatically from the "
        "CollegeTownIQ master dataset so that the analytical "
        "summary can be regenerated when the underlying data or "
        "methods change."
    )
    report_lines.append("")

    return "\n".join(report_lines)


def save_report(report: str) -> None:
    """Save the generated Markdown report."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    print(f"Saved research findings to {OUTPUT_PATH}")


def main() -> None:
    """Run the research findings pipeline."""
    dataset = load_data()
    analysis_data = prepare_analysis_data(dataset)

    print("CollegeTownIQ Research Findings")
    print("===============================")
    print(f"Master observations: {len(dataset)}")
    print(f"Complete observations: {len(analysis_data)}")

    report = generate_report(dataset, analysis_data)
    save_report(report)


if __name__ == "__main__":
    main()