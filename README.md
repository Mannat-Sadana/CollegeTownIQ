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

## A look at the study area

### 1. Housing costs

![Median gross rent by census tract](docs/figures/maps/median_gross_rent_map.png)

*Median gross rent by census tract, based on the 2024 American Community Survey 5-Year Estimates.*

Housing costs vary across the study area, which is why I wanted to examine individual census tracts instead of relying on one average for the entire region.

### 2. Public transportation accessibility

![Transit accessibility by census tract](docs/figures/maps/transit_accessibility_map.png)

*Transit accessibility across the study area. The project examines both straight-line distance and pedestrian-network distance, which represent different ways of measuring accessibility.*

A straight-line distance doesn't necessarily represent the route someone would actually walk. I explored pedestrian-network distances separately to better understand this difference.

### 3. Food accessibility

![Food access by census tract](docs/figures/maps/food_access_map.png)

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

If you want to explore the code locally, start by cloning the repository and installing the Python dependencies.

```bash
git clone https://github.com/Mannat-Sadana/CollegeTownIQ.git
cd CollegeTownIQ

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

The commands above set up the Python environment. Reproducing the full analysis also requires the source datasets and intermediate files expected by the processing scripts.

The repository includes the dashboard's exported GeoJSON data, so the dashboard can be explored separately from the full geospatial processing workflow. For local browser testing, serve the project through a local web server rather than relying on a direct file URL.

## Limitations and things I'd improve next

This project has taught me a lot, but there are still limitations I'd like to address.

- **Small regression sample:** The primary model uses only 25 complete census-tract observations, so estimates may be sensitive to the particular areas included.
- **Missing data:** Some housing and socioeconomic variables are unavailable for certain tracts. I document missingness rather than treating every missing value as zero.
- **Geographic aggregation:** Census-tract averages do not describe every household or individual living in an area.
- **Distance measures:** Straight-line distance and pedestrian-network distance measure different things. Neither automatically represents actual travel time or the quality of transit service.
- **Observational analysis:** The model identifies an association and does not establish causation.
- **Additional explanatory factors:** The current model does not capture every factor that could influence rent, such as housing characteristics, neighborhood amenities, or local market conditions.

If I continue developing CollegeTownIQ, I'd like to investigate additional explanatory variables, improve the treatment of missing data, and explore ways to make the accessibility measures more representative of actual travel conditions.

## Why I built this project

I wanted to build something that connected data science to a real place and a practical problem rather than just complete an analysis and move on to the next assignment.

CollegeTownIQ gave me a chance to work through data collection, cleaning, feature engineering, geospatial processing, statistical modeling, diagnostics, and interactive visualization in one project.

It also made me think more carefully about how data should be interpreted. A coefficient or a map can tell part of a story, but understanding the limitations behind it matters just as much.

The project is still something I can improve, but I'm proud of how much I learned by building the different pieces and connecting them into one workflow.

---

*CollegeTownIQ is an independent student data science project exploring housing affordability and accessibility in the State College, Pennsylvania area.*