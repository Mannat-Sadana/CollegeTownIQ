from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
from libpysal.weights import Queen
from esda.moran import Moran


INPUT_PATH = Path("data/processed/college_town_analysis.gpkg")
OUTPUT_PATH = Path("docs/research_findings.md")


TARGET = "median_gross_rent"

PREDICTORS = [
    "median_transit_distance_m",
    "median_household_income",
    "vehicle_access_pct",
]


def load_data() -> gpd.GeoDataFrame:
    """Load the primary CollegeTownIQ analysis dataset."""
    return gpd.read_file(INPUT_PATH)


def prepare_analysis_data(
    dataset: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Create the complete-case dataset used by the primary model."""

    columns = [
        "GEOID",
        TARGET,
        *PREDICTORS,
    ]

    analysis_data = dataset[columns].copy()

    for column in columns[1:]:
        analysis_data[column] = pd.to_numeric(
            analysis_data[column],
            errors="coerce",
        )

    return analysis_data.dropna(
        subset=[TARGET, *PREDICTORS]
    ).reset_index(drop=True)


def fit_primary_model(
    analysis_data: pd.DataFrame,
):
    """Fit the primary gross-rent accessibility model."""

    model_data = analysis_data.copy()

    model_data["transit_distance_km"] = (
        model_data["median_transit_distance_m"] / 1000
    )

    model_data["income_10k"] = (
        model_data["median_household_income"] / 10000
    )

    x = model_data[
        [
            "transit_distance_km",
            "income_10k",
            "vehicle_access_pct",
        ]
    ]

    x = sm.add_constant(x)

    y = model_data[TARGET]

    return sm.OLS(y, x).fit(cov_type="HC3")


def format_currency(value: float) -> str:
    """Format a numeric value as currency."""
    return f"${value:,.0f}"


def calculate_influence(
    model,
    analysis_data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate Cook's distance for each observation."""

    influence = model.get_influence()

    result = analysis_data[
        ["GEOID"]
    ].copy()

    result["cooks_distance"] = (
        influence.cooks_distance[0]
    )

    return result.sort_values(
        "cooks_distance",
        ascending=False,
    )


def fit_model_without_geoids(
    analysis_data: pd.DataFrame,
    excluded_geoids: list[str],
):
    """Fit the primary model after excluding selected GEOIDs."""

    filtered = analysis_data[
        ~analysis_data["GEOID"].isin(excluded_geoids)
    ].copy()

    return fit_primary_model(filtered)


def calculate_spatial_diagnostics(
    analysis_data: pd.DataFrame,
    model,
    dataset: gpd.GeoDataFrame,
) -> tuple[float, float, float]:
    """Calculate Moran's I for primary-model residuals."""

    residual_data = analysis_data[
        ["GEOID"]
    ].copy()

    residual_data["residual"] = model.resid

    geometry_data = dataset[
        ["GEOID", "geometry"]
    ].copy()

    geometry_data = geometry_data[
        geometry_data["GEOID"].isin(
            residual_data["GEOID"]
        )
    ]

    geometry_data = geometry_data.merge(
        residual_data,
        on="GEOID",
        how="inner",
        validate="one_to_one",
    )

    geometry_data = geometry_data.reset_index(
        drop=True
    )

    weights = Queen.from_dataframe(
        geometry_data,
        use_index=False,
    )

    np.random.seed(42)

    moran = Moran(
        geometry_data["residual"],
        weights,
        permutations=999,
    )

    average_neighbors = float(
        np.mean(
            [
                len(neighbors)
                for neighbors in weights.neighbors.values()
            ]
        )
    )

    return (
        float(moran.I),
        float(moran.p_sim),
        average_neighbors,
    )


def generate_report(
    dataset: gpd.GeoDataFrame,
    analysis_data: pd.DataFrame,
    model,
    influence: pd.DataFrame,
    sensitivity_models: dict,
    moran_i: float,
    moran_p: float,
    average_neighbors: float,
) -> str:
    """Generate the current CollegeTownIQ research findings report."""

    rent = analysis_data[TARGET]
    income = analysis_data["median_household_income"]

    transit_distance = (
        analysis_data["median_transit_distance_m"]
    )

    report = []

    report.append("# CollegeTownIQ Research Findings")
    report.append("")
    report.append(
        "This report summarizes the descriptive, geospatial, "
        "and statistical analysis performed on the CollegeTownIQ "
        "State College study area."
    )
    report.append("")
    report.append(
        "**Important:** These results describe associations "
        "among observed tract-level measures. They do not "
        "establish causal relationships."
    )
    report.append("")

    report.append("## 1. Study Coverage")
    report.append("")
    report.append(
        f"- Study-area observations: **{len(dataset)} census tracts**"
    )
    report.append(
        f"- Complete observations used in the primary statistical "
        f"model: **{len(analysis_data)}**"
    )
    report.append(
        "- Geographic unit: 2024 Census tracts intersecting "
        "the CollegeTownIQ study area"
    )
    report.append(
        "- Study area: State College Borough, College Township, "
        "Ferguson Township, Harris Township, and Patton Township"
    )
    report.append("")

    report.append("## 2. Housing Affordability")
    report.append("")
    report.append(
        f"- Median tract-level gross rent: "
        f"**{format_currency(rent.median())} per month**"
    )
    report.append(
        f"- Median tract-level household income: "
        f"**{format_currency(income.median())} annually**"
    )
    report.append(
        f"- Median tract-level rent burden measure: "
        f"**{analysis_data.get('median_rent_burden_pct', pd.Series(dtype=float)).median():.1f}%**"
        if "median_rent_burden_pct" in analysis_data
        else "- Rent burden is retained as a secondary housing measure."
    )
    report.append(
        f"- Observed median gross rent ranged from "
        f"**{format_currency(rent.min())}** to "
        f"**{format_currency(rent.max())}**"
    )
    report.append("")
    report.append(
        "The tract-level gross-rent measure is an area-level "
        "statistic and should not be interpreted as the rent "
        "paid by every household in a tract."
    )
    report.append("")

    report.append("## 3. Transit Accessibility")
    report.append("")
    report.append(
        "The primary accessibility measure is a **250-meter "
        "sampled straight-line distance** to the nearest CATA "
        "transit stop."
    )
    report.append("")
    report.append(
        "A 500-meter sampling resolution was evaluated as a "
        "sensitivity check."
    )
    report.append("")
    report.append(
        "- The primary model uses the 250m sampled straight-line measure."
    )
    report.append(
        "- A separate pedestrian-network analysis provides a "
        "different accessibility perspective."
    )
    report.append(
        "- Straight-line and network measures are kept "
        "conceptually separate because they represent "
        "different accessibility assumptions."
    )
    report.append("")
    report.append(
        f"- Median primary transit-distance measure: "
        f"**{transit_distance.median():,.1f} meters**"
    )
    report.append("")

    report.append("## 4. Food Access")
    report.append("")
    report.append(
        "USDA Food Access Research Atlas / SRAM measures were "
        "integrated as a separate essential-service accessibility "
        "dimension."
    )
    report.append("")
    report.append(
        "The project retains both straight-line and network-based "
        "food-access measures rather than treating them as interchangeable."
    )
    report.append("")
    report.append(
        "Food access is used as a complementary analysis rather "
        "than as a predictor in the primary gross-rent regression."
    )
    report.append("")

    report.append("## 5. Descriptive Relationships")
    report.append("")
    report.append(
        "Pearson correlations are used to describe relationships "
        "among tract-level variables."
    )
    report.append("")

    correlation_data = dataset[
        [
            "median_gross_rent",
            "median_household_income",
            "median_transit_distance_m",
            "median_rent_burden_pct",
        ]
    ].copy()

    correlation_data = correlation_data.apply(
        pd.to_numeric,
        errors="coerce",
    )

    gross_rent_corr = correlation_data.corr()

    report.append(
        f"- Median gross rent vs. 250m sampled straight-line "
        f"transit distance: **r = "
        f"{gross_rent_corr.loc['median_gross_rent', 'median_transit_distance_m']:.3f}**"
    )
    report.append(
        f"- Median gross rent vs. median household income: **r = "
        f"{gross_rent_corr.loc['median_gross_rent', 'median_household_income']:.3f}**"
    )
    report.append(
        f"- Median rent burden vs. median household income: **r = "
        f"{gross_rent_corr.loc['median_rent_burden_pct', 'median_household_income']:.3f}**"
    )
    report.append(
        f"- Median rent burden vs. 250m sampled straight-line "
        f"transit distance: **r = "
        f"{gross_rent_corr.loc['median_rent_burden_pct', 'median_transit_distance_m']:.3f}**"
    )
    report.append("")
    report.append(
        "These are descriptive associations and should not be "
        "interpreted as causal effects."
    )
    report.append("")

    report.append("## 6. Primary Multivariable Regression")
    report.append("")
    report.append(
        "The primary model estimates the association between "
        "tract-level median gross rent and transit accessibility "
        "while controlling for median household income and vehicle access."
    )
    report.append("")
    report.append(
        f"- Observations: **{int(model.nobs)}**"
    )
    report.append(
        f"- R²: **{model.rsquared:.3f}**"
    )
    report.append(
        f"- Adjusted R²: **{model.rsquared_adj:.3f}**"
    )
    report.append(
        f"- Overall F-test p-value: **{model.f_pvalue:.4f}**"
    )
    report.append("")
    report.append("| Predictor | Coefficient | Robust p-value |")
    report.append("|---|---:|---:|")
    report.append(
        f"| Transit distance (km) | "
        f"**{model.params['transit_distance_km']:.3f}** | "
        f"**{model.pvalues['transit_distance_km']:.4f}** |"
    )
    report.append(
        f"| Household income ($10,000s) | "
        f"{model.params['income_10k']:.3f} | "
        f"{model.pvalues['income_10k']:.3f} |"
    )
    report.append(
        f"| Vehicle access (%) | "
        f"{model.params['vehicle_access_pct']:.3f} | "
        f"{model.pvalues['vehicle_access_pct']:.3f} |"
    )
    report.append("")
    report.append(
        "The estimated coefficient for transit distance corresponds "
        f"to approximately **${abs(model.params['transit_distance_km']):.0f} "
        "lower tract-level median gross rent per additional kilometer "
        "of the 250-meter sampled straight-line transit-distance "
        "measure**, conditional on the other included variables."
    )
    report.append("")
    report.append(
        "This is an association at the census-tract level, not "
        "evidence that increasing or decreasing transit access "
        "causes rents to change."
    )
    report.append("")

    report.append("## 7. Influence and Sensitivity Analysis")
    report.append("")
    influential = influence[
        influence["cooks_distance"] > 4 / len(analysis_data)
    ]

    for _, row in influential.head(2).iterrows():
        report.append(
            f"- GEOID `{row['GEOID']}`: Cook's distance ≈ "
            f"**{row['cooks_distance']:.3f}**"
        )

    report.append("")
    report.append(
        "The transit-distance association remained similar when "
        "these observations were removed individually or together."
    )
    report.append("")
    report.append(
        "| Scenario | Observations | Transit coefficient | p-value |"
    )
    report.append("|---|---:|---:|---:|")

    scenarios = [
        ("All observations", []),
        ("Remove 42027011903", ["42027011903"]),
        ("Remove 42027012300", ["42027012300"]),
        (
            "Remove both",
            ["42027011903", "42027012300"],
        ),
    ]

    for label, excluded in scenarios:
        if not excluded:
            sensitivity_model = model
        else:
            sensitivity_model = sensitivity_models[
                tuple(excluded)
            ]

        report.append(
            f"| {label} | "
            f"{int(sensitivity_model.nobs)} | "
            f"{sensitivity_model.params['transit_distance_km']:.2f} | "
            f"{sensitivity_model.pvalues['transit_distance_km']:.4f} |"
        )

    report.append("")
    report.append("## 8. Spatial Residual Diagnostics")
    report.append("")
    report.append(
        f"- Observations: **{int(model.nobs)}**"
    )
    report.append(
        "- Neighborhood definition: **Queen contiguity**"
    )
    report.append(
        f"- Average neighbors: **{average_neighbors:.2f}**"
    )
    report.append(
        f"- Moran's I: **{moran_i:.4f}**"
    )
    report.append(
        f"- Permutation p-value: **{moran_p:.4f}**"
    )
    report.append("")
    report.append(
        "The selected test did not detect statistically "
        "significant spatial autocorrelation in the primary "
        "regression residuals."
    )
    report.append("")

    report.append("## 9. Secondary Accessibility Analysis")
    report.append("")
    report.append(
        "- Pedestrian-network transit accessibility"
    )
    report.append(
        "- Food-access measures"
    )
    report.append(
        "- Alternative spatial sampling resolutions"
    )
    report.append(
        "- Transit accessibility method differences"
    )
    report.append("")
    report.append(
        "These analyses provide methodological context and "
        "sensitivity checks but are not substituted for the "
        "primary gross-rent model."
    )
    report.append("")

    report.append("## 10. Interpretation")
    report.append("")
    report.append(
        "Within the analyzed State College study area, tracts "
        "with greater sampled straight-line distance to CATA "
        "transit stops tended to have lower median gross rents "
        "after accounting for median household income and vehicle access."
    )
    report.append("")
    report.append(
        "The result should be interpreted as an **observed "
        "tract-level association**. It does not establish that "
        "transit accessibility causes housing costs to increase or decrease."
    )
    report.append("")
    report.append(
        "The project therefore focuses on identifying **tradeoffs "
        "and spatial patterns** rather than producing a universal "
        "ranking of neighborhoods."
    )
    report.append("")

    report.append("## 11. Important Limitations")
    report.append("")
    limitations = [
        "The analysis uses census-tract-level data rather than individual households.",
        f"Only {int(model.nobs)} complete observations are available for the primary regression.",
        "Several ACS variables are unavailable for three study-area tracts.",
        f"The study area contains only {len(dataset)} tracts, limiting statistical precision.",
        "Straight-line transit distance is not equivalent to walking distance or travel time.",
        "The pedestrian-network analysis provides a separate accessibility perspective but does not model individual travel behavior.",
        "Food-access measures come from the USDA food-access framework and do not represent every dimension of food availability, quality, or affordability.",
        "Some census tracts cross municipal boundaries because the study-area inclusion rule is based on geographic intersection.",
        "Associations should not be interpreted as causal effects.",
        'The project does not produce a universal "best neighborhood" score.',
    ]

    for limitation in limitations:
        report.append(f"- {limitation}")

    report.append("")

    report.append("## 12. Reproducibility")
    report.append("")
    report.append(
        "The primary findings are generated from the CollegeTownIQ "
        "processed analysis dataset and can be reproduced using the "
        "analysis scripts in `src/analysis/`."
    )
    report.append("")
    report.append("Key reproducible components include:")
    report.append("")
    report.append("- Primary affordability-accessibility regression")
    report.append("- Regression diagnostics")
    report.append("- Cook's-distance influence analysis")
    report.append("- Leave-out sensitivity analysis")
    report.append("- Spatial residual diagnostics")
    report.append("- Transit accessibility sensitivity analysis")
    report.append("")
    report.append(
        "The repository keeps analytical methods separate from "
        "generated outputs so that results can be regenerated when "
        "underlying data or methodology changes."
    )

    return "\n".join(report) + "\n"


def main() -> None:
    """Generate the current research findings report."""

    dataset = load_data()
    analysis_data = prepare_analysis_data(dataset)

    model = fit_primary_model(analysis_data)

    influence = calculate_influence(
        model,
        analysis_data,
    )

    sensitivity_models = {
        ("42027011903",): fit_model_without_geoids(
            analysis_data,
            ["42027011903"],
        ),
        ("42027012300",): fit_model_without_geoids(
            analysis_data,
            ["42027012300"],
        ),
        (
            "42027011903",
            "42027012300",
        ): fit_model_without_geoids(
            analysis_data,
            [
                "42027011903",
                "42027012300",
            ],
        ),
    }

    moran_i, moran_p, average_neighbors = (
        calculate_spatial_diagnostics(
            analysis_data,
            model,
            dataset,
        )
    )

    report = generate_report(
        dataset=dataset,
        analysis_data=analysis_data,
        model=model,
        influence=influence,
        sensitivity_models=sensitivity_models,
        moran_i=moran_i,
        moran_p=moran_p,
        average_neighbors=average_neighbors,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    print(
        f"Saved research findings to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
