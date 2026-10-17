# CollegeTownIQ 🏡
### Exploring Housing Affordability and Accessibility in State College, Pennsylvania

[**🌐 View the Live Dashboard**](https://mannat-sadana.github.io/CollegeTownIQ/dashboard/) · [View Source Code](https://github.com/Mannat-Sadana/CollegeTownIQ)

---

## What is CollegeTownIQ?

CollegeTownIQ is a data science project I built to explore a question that I find interesting as a college student: **Does living in a cheaper area also mean having less convenient access to public transportation and other essential resources?**

I used State College, Pennsylvania, as my case study and combined housing, census, transit, food-access, and geographic data to investigate how these factors vary across the area.

I didn't want to create another project that just takes a dataset, makes a few charts, and stops there. I wanted to work through the different parts of a data science project, from collecting and cleaning data to analyzing it, checking the results, and building an interactive dashboard.

The goal isn't to identify one universally "best" neighborhood. Instead, I wanted to make it easier to explore the tradeoffs between housing costs and accessibility.

## Explore the dashboard

## Interactive Dashboard

[**Explore the live CollegeTownIQ dashboard →**](https://mannat-sadana.github.io/CollegeTownIQ/dashboard/)

CollegeTownIQ is an interactive geospatial dashboard for exploring how housing costs and access to transportation and essential resources vary across State College, Pennsylvania.

### Explore housing affordability geographically

![CollegeTownIQ housing affordability map](docs/figures/dashboard_preview.png)

### Compare census tracts

Compare two census tracts across median rent, rent burden, transit distance, food access, and vehicle access to explore how local conditions differ.

![CollegeTownIQ census tract comparison](docs/figures/tract_comparison.png)

## Key Research Findings

CollegeTownIQ examines the relationship between housing costs and public transit accessibility across 28 census tracts in the State College, Pennsylvania area. The primary regression uses 25 complete observations.

### Main finding

In the primary regression, greater straight-line distance to the nearest CATA transit stop was associated with lower median gross rent, after accounting for median household income and vehicle access.

- **Estimated association:** Approximately $35 lower median gross rent per additional kilometer of transit distance.
- **Robust p-value:** 0.0066.
- **Model R²:** 0.1902.
- **Sensitivity check:** The estimated association remained similar when transit distance was recalculated using a 500-meter sampling resolution.

These results suggest a relationship between housing costs and transit accessibility within the study area. They do not establish that distance from transit causes rents to decrease.

## Methodology and Robustness Checks

I built a geospatial workflow that combines public datasets, constructs tract-level accessibility measures, and evaluates the relationship between housing costs and transit access.

1. **Data integration:** Combined 2024 American Community Survey 5-Year Estimates, CATA transit data, food-access data, census boundaries, and geographic datasets.
2. **Geospatial processing:** Defined a study area covering State College Borough, College Township, Ferguson Township, Harris Township, and Patton Township.
3. **Feature engineering:** Calculated housing, socioeconomic, transit-accessibility, and food-access measures at the census-tract level.
4. **Statistical modeling:** Estimated a regression relating median gross rent to transit distance, median household income, and vehicle access.
5. **Robustness checks:** Evaluated alternative transit-distance sampling resolutions, influential observations, and spatial residual patterns.

### Diagnostic results

- The estimated transit-distance association remained similar using a 500-meter sampling resolution.
- The association persisted after excluding two potentially influential observations, with 23 observations remaining.
- The spatial residual diagnostic did not detect statistically significant spatial autocorrelation in the tested model.

These checks help assess the stability of the findings, but they do not eliminate every source of uncertainty or establish causation.

## A look at the study area

### 1. Housing costs

![Housing affordability dashboard](docs/figures/dashboard_preview_2.png)

*Median gross rent by census tract, based on the 2024 American Community Survey 5-Year Estimates.*

Housing costs vary across the study area, which is why I wanted to examine individual census tracts instead of relying on one average for the entire region.

### 2. Public transportation accessibility

![Transit accessibility dashboard](docs/figures/transit_dashboard.png)

*Transit accessibility across the study area. The project examines both straight-line distance and pedestrian-network distance, which represent different ways of measuring accessibility.*

A straight-line distance doesn't necessarily represent the route someone would actually walk. I explored pedestrian-network distances separately to better understand this difference.

### 3. Food accessibility

![Food accessibility dashboard](docs/figures/food_access_dashboard.png)

*Geographic variation in the food-access measure used in the project.*

I also included food accessibility because transportation and access to essential resources are part of the broader picture of how convenient a location may be.

## Research questions

I built the project around four main questions:

1. How does housing cost vary across the State College area?
2. How does access to public transportation and food resources vary by location?
3. Is housing cost associated with transit accessibility after accounting for other observed characteristics?
4. Do the results change when I use a different spatial sampling resolution?

These questions helped me connect data engineering, geospatial analysis, visualization, and statistical modeling in one project.

## What I found

Here are some of the main findings from my analysis.

| Finding | Result |
|---|---|
| Study area | 28 census tracts across five municipalities |
| Primary regression sample | 25 complete observations |
| Median gross rent across tracts | $1,214 per month |
| Median household income across tracts | $84,063 per year |
| Primary transit-distance measure | 250-meter sampled straight-line distance |

### Housing costs and transit distance

In my primary regression model, greater straight-line distance to the nearest CATA transit stop was associated with lower median gross rent, after accounting for the other variables included in the model.

- **Estimated coefficient:** approximately −$35.4 per additional kilometer.
- **HC3 robust p-value:** 0.0066.
- **R²:** approximately 0.19.

The result was similar when I tested a 500-meter sampling resolution. The estimated coefficient was approximately −$35.3 per kilometer, with a robust p-value of 0.0071.

I found this relationship interesting because it shows that the relationship between housing costs and accessibility may not be as straightforward as simply assuming that areas closer to transit always have higher rents.

However, the model explains only part of the variation in rent, and the sample is small. These results should be treated as a starting point for further investigation, not a complete explanation of the housing market.

**An important limitation:** This is an observational analysis. It does not show that distance from transit causes rent to decrease, and it cannot establish what an individual household would pay.

## How I approached the analysis

One of the main things I wanted to learn through this project was how the different stages of a data science workflow fit together.

### 1. Data collection and cleaning

I brought together multiple public datasets covering housing, socioeconomic characteristics, transportation, food access, and geographic boundaries.

I organized the processing scripts so that the source data could be transformed into datasets suitable for geospatial analysis and modeling.

### 2. Geospatial analysis

I used census tracts as the main geographic unit and focused on five municipalities in the State College region:

- State College Borough
- College Township
- Ferguson Township
- Harris Township
- Patton Township

The geospatial dataset contains 28 census tracts. The primary regression uses 25 because three tracts do not have complete values for all the required model variables.

For transit accessibility, I calculated straight-line distances using a 250-meter sampling grid and tested a 500-meter grid to see whether the results were sensitive to the sampling resolution.

I also worked with OpenStreetMap pedestrian-network data to calculate network distances. This gave me a second way to examine accessibility instead of assuming that straight-line distance represents the route someone would actually walk.

### 3. Statistical modeling

I used a multivariable regression model to explore the relationship between median gross rent and transit distance, controlling for median household income and vehicle access.

I also used HC3 heteroskedasticity-robust standard errors to make the statistical inference less dependent on the assumption of constant error variance.

### 4. Checking the results

I didn't want to stop once I had a statistically significant coefficient. I also looked at whether the model's results were sensitive to diagnostics and alternative specifications.

The project includes:

- Regression diagnostics and residual checks.
- Cook's distance to identify potentially influential observations.
- Spatial residual analysis using Moran's I.
- A sensitivity analysis using a 500-meter sampling resolution.
- An influence sensitivity check to see whether the transit-distance association persisted when influential observations were excluded.

The spatial residual analysis did not find statistically significant residual spatial autocorrelation in the tested specification. That does not prove that all spatial dependence is absent, but it provides another diagnostic to consider when interpreting the model.

These checks helped me think more carefully about the difference between obtaining a result and understanding how reliable that result might be.

## Data sources

The project uses several public data sources:

| Source | What I used it for |
|---|---|
| [U.S. Census Bureau — ACS](https://www.census.gov/programs-surveys/acs) | Median gross rent, household income, rent burden, and vehicle availability |
| Centre Area Transportation Authority (CATA) GTFS | Transit stops, trips, schedules, and stop events |
| [USDA Food Access Research Atlas](https://www.ers.usda.gov/data-products/food-access-research-atlas/) and related food-access data | Food-access measures |
| [Census TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) | Census tract boundaries |
| Centre County GIS | Geographic boundaries for defining the study area |
| [OpenStreetMap](https://www.openstreetmap.org/) | Street-network data for pedestrian accessibility analysis |

Housing and socioeconomic measures use the 2024 ACS 5-Year Estimates.

## Tools and technologies

These are the main tools I used throughout the project.

| Tool | How I used it |
|---|---|
| Python | Data processing, feature engineering, and analysis |
| pandas and NumPy | Cleaning, transforming, and analyzing tabular data |
| GeoPandas and Shapely | Working with geographic datasets |
| OSMnx and NetworkX | Pedestrian-network analysis |
| Statsmodels and SciPy | Regression and statistical diagnostics |
| Matplotlib | Maps and analytical visualizations |
| HTML, CSS, and JavaScript | Building the interactive dashboard |
| GeoJSON | Exporting geographic data for the dashboard |
| Git and GitHub | Version control and project documentation |

## Project structure

I organized the project into separate folders for data, processing scripts, analysis, and the dashboard.

```text
CollegeTownIQ/
├── dashboard/
│   ├── index.html
│   └── data/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── figures/
│   │   └── maps/
│   ├── analysis_report.md
│   ├── research_findings.md
│   └── missing_data_details.csv
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── geospatial/
│   └── analysis/
├── requirements.txt
└── README.md
```

This is a simplified overview of the main folders. The `src` directory contains scripts for the different processing and analysis stages, while `docs` contains reports and generated figures.

## Running the project locally

The live dashboard is available here:

**[CollegeTownIQ Dashboard](https://mannat-sadana.github.io/CollegeTownIQ/dashboard/)**

### Set up the environment

Clone the repository and install the Python dependencies in a virtual environment:

```bash
git clone https://github.com/Mannat-Sadana/CollegeTownIQ.git
cd CollegeTownIQ

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
```

### Data requirements

The dashboard can be explored independently using the exported GeoJSON file included in the repository. Reproducing the full analysis requires the source datasets and intermediate files expected by the scripts. Some raw data and processed outputs are not tracked in Git.

Before running the processing pipeline, make sure the required ACS data, Census TIGER/Line shapefiles, CATA GTFS files, and food-access data are available in the paths expected by the scripts.

### Reproducing the analysis

Run the processing scripts from the repository root, with the virtual environment activated. The general workflow is:

1. Clean the ACS data and construct the census-tract dataset.
2. Build the study area and process CATA transit stops and service data.
3. Calculate transit accessibility and assemble the analysis dataset.
4. Build the walking-network accessibility and food-access datasets.
5. Assemble the master dataset and run the statistical analyses.
6. Export the dashboard data and regenerate the figures as needed.

The 250 m and 500 m straight-line accessibility measures support a sensitivity analysis that checks whether the main regression results are consistent across grid resolutions. Run the relevant accessibility scripts before the analysis scripts that depend on their outputs.

For exact input paths and output filenames, refer to each script's constants and data-loading functions. Not every intermediate dataset is included in the repository, so the full workflow may require obtaining the original data and generating intermediate files first.

### Preview the dashboard locally

The dashboard uses the exported GeoJSON data in `dashboard/data/college_town_data.geojson`. To preview it locally, start a web server from the repository root rather than opening the HTML file directly:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/dashboard/` in your browser.

### Robustness Check: Housing Tenure

The initial regression showed a negative association between distance to public transit and median gross rent. However, after adding renter share as a control variable, the transit-distance coefficient decreased from approximately −$35.40 to −$18.93 per kilometer and became statistically insignificant (p = 0.4801).

When both renter share and the college-enrollment proxy were included, the coefficient decreased further to −$12.59 per kilometer (p = 0.6281).

These findings suggest that housing tenure may partly account for the original association. However, the analysis uses only 25 observations, and the observational design does not establish causality. The results should therefore be interpreted cautiously.

Detailed results are available in `docs/confounding_check.csv`.

## Limitations and Future Improvements

Several limitations matter when interpreting the results:

- **Small sample:** The primary regression uses 25 complete census-tract observations, so estimates may be sensitive to the areas included.
- **Observational design:** The analysis identifies associations, not causal effects.
- **Geographic aggregation:** Census-tract statistics do not describe every household or individual within an area.
- **Accessibility assumptions:** Straight-line distance and pedestrian-network distance represent different measures. Neither directly captures actual travel time, service quality, or every individual's access to transit.
- **Missing data:** Some housing and socioeconomic variables are unavailable for certain tracts, reducing the number of observations available for the regression.
- **Unobserved factors:** Housing characteristics, neighborhood amenities, land use, and other local conditions may also influence rent.

Future improvements could incorporate additional explanatory variables, refine accessibility measures, and expand the analysis to a larger geographic area.

## Why I built this project

I wanted to build something that connected data science to a real place and a practical problem rather than just complete an analysis and move on to the next assignment.

CollegeTownIQ gave me a chance to work through data collection, cleaning, feature engineering, geospatial processing, statistical modeling, diagnostics, and interactive visualization in one project.

It also made me think more carefully about how data should be interpreted. A coefficient or a map can tell part of a story, but understanding the limitations behind it matters just as much.

The project is still something I can improve, but I'm proud of how much I learned by building the different pieces and connecting them into one workflow.

---

*CollegeTownIQ is an independent student data science project exploring housing affordability and accessibility in the State College, Pennsylvania area.*