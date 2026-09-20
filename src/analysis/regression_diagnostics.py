from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats


INPUT_PATH = Path(
    "data/processed/college_town_analysis.gpkg"
)
OUTPUT_DIR = Path("docs/figures")


def load_data():
    return gpd.read_file(INPUT_PATH)


def prepare_model_data(dataset):
    columns = [
        "median_gross_rent",
        "median_transit_distance_m",
        "median_household_income",
        "vehicle_access_pct",
    ]

    data = dataset[columns].dropna().copy()

    data["transit_distance_km"] = (
        data["median_transit_distance_m"] / 1000
    )

    data["income_10k"] = (
        data["median_household_income"] / 10000
    )

    return data


def fit_full_model(data):
    predictors = [
        "transit_distance_km",
        "income_10k",
        "vehicle_access_pct",
    ]

    x = sm.add_constant(data[predictors])
    y = data["median_gross_rent"]

    model = sm.OLS(y, x).fit(cov_type="HC3")

    return model


def create_diagnostic_plots(model):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fitted_values = model.fittedvalues
    residuals = model.resid

    figure, axis = plt.subplots(figsize=(8, 6))
    axis.scatter(fitted_values, residuals)
    axis.axhline(0, linestyle="--")
    axis.set_xlabel("Fitted values")
    axis.set_ylabel("Residuals")
    axis.set_title("Residuals vs Fitted Values")
    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "residuals_vs_fitted.png",
        dpi=300,
    )
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 6))
    sm.qqplot(
        residuals,
        line="45",
        ax=axis,
    )
    axis.set_title("Q-Q Plot of Regression Residuals")
    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "regression_qq_plot.png",
        dpi=300,
    )
    plt.close(figure)


def run_diagnostics(model):
    residuals = model.resid

    shapiro_statistic, shapiro_pvalue = stats.shapiro(
        residuals
    )

    influence = model.get_influence()
    cooks_distance = influence.cooks_distance[0]

    print()
    print("CollegeTownIQ Regression Diagnostics")
    print("====================================")
    print(f"Observations: {int(model.nobs)}")
    print()

    print("Model fit")
    print("---------")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")
    print()

    print("Residual diagnostics")
    print("--------------------")
    print(f"Residual mean: {residuals.mean():.6f}")
    print(f"Residual std: {residuals.std():.4f}")
    print(
        f"Shapiro-Wilk statistic: "
        f"{shapiro_statistic:.4f}"
    )
    print(
        f"Shapiro-Wilk p-value: "
        f"{shapiro_pvalue:.6f}"
    )
    print()

    print("Influence diagnostics")
    print("---------------------")
    print(
        f"Maximum Cook's distance: "
        f"{cooks_distance.max():.4f}"
    )

    influential_count = (
        cooks_distance > 4 / model.nobs
    ).sum()

    print(
        f"Observations above 4/n threshold: "
        f"{influential_count}"
    )

    print()
    print("Largest Cook's distances:")

    largest_indices = (
        cooks_distance.argsort()[-5:][::-1]
    )

    for index in largest_indices:
        print(
            f"  Observation {index}: "
            f"{cooks_distance[index]:.4f}"
        )


def main():
    dataset = load_data()
    data = prepare_model_data(dataset)
    model = fit_full_model(data)

    create_diagnostic_plots(model)
    run_diagnostics(model)

    print()
    print("Saved diagnostic figures to docs/figures/")


if __name__ == "__main__":
    main()
