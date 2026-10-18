
import geopandas as gpd

METRIC_CRS = "EPSG:2272"
MINIMUM_OVERLAP = 0.50


def select_majority_overlap_tracts(
    tracts: gpd.GeoDataFrame,
    study_area: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Keep whole tracts with at least 50% of area in the study area."""
    if tracts.crs is None or study_area.crs is None:
        raise ValueError("Both inputs must have a defined CRS.")

    tracts_projected = tracts.to_crs(METRIC_CRS)
    area_projected = study_area.to_crs(METRIC_CRS)

    study_geometry = area_projected.geometry.union_all()

    tract_areas = tracts_projected.geometry.area
    if (tract_areas <= 0).any():
        raise ValueError("Found tracts with zero or negative area.")

    intersection_areas = (
        tracts_projected.geometry
        .intersection(study_geometry)
        .area
    )

    overlap_share = intersection_areas / tract_areas

    selected = tracts_projected.loc[
        overlap_share >= MINIMUM_OVERLAP
    ].copy()

    selected["study_area_overlap_pct"] = (
        overlap_share.loc[selected.index] * 100
    )

    return selected.to_crs(tracts.crs)
