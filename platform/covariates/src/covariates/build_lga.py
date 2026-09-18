"""Tier A — LGA covariates derived from data already in the repo.

    geo_unit (geometry)  +  geo_settlement (GRID3 buildings)  +
    geo_facility (GRID3 health facilities)   ->   covariates_lga.parquet

774 rows, keyed to the spine LGA pcode. Facility- and ward-derived
columns are NaN (not 0) for the 13 states GRID3 v3.0 doesn't cover yet,
and carry a `*_data` flag so a model treats them as missing, not zero.
"""

from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from .config import (
    BIG_CITIES, DICT_PARQUET, DUCKDB, GEO_FACILITY, GEO_SETTLEMENT,
    GEO_UNIT, LGA_PARQUET,
)

R_EARTH_KM = 6371.0088


def _haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    d = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * R_EARTH_KM * np.arcsin(np.sqrt(d))


def _nearest_city_km(lon, lat):
    d = [_haversine_km(lon, lat, clon, clat) for clon, clat in BIG_CITIES.values()]
    return np.min(d, axis=0)


# ---------------------------------------------------------------- build --
def build() -> dict:
    u = pd.read_parquet(GEO_UNIT)
    lga = (u[u.level == 2][["pcode", "name", "adm1_pcode", "area_sqkm",
                            "center_lon", "center_lat"]]
           .rename(columns={"pcode": "lga_pcode", "name": "lga_name",
                            "adm1_pcode": "state_pcode", "area_sqkm": "area_km2",
                            "center_lon": "centroid_lon", "center_lat": "centroid_lat"})
           .reset_index(drop=True))

    wards = u[u.level == 3]
    ward_states = set(wards.adm1_pcode.unique())
    n_wards = wards.groupby("adm2_pcode").size().rename("n_wards")
    lga = lga.merge(n_wards, left_on="lga_pcode", right_index=True, how="left")
    lga["ward_data"] = lga.state_pcode.isin(ward_states)
    lga.loc[lga.ward_data, "n_wards"] = lga.loc[lga.ward_data, "n_wards"].fillna(0)

    # --- settlements / buildings (national) ----------------------------
    s = pd.read_parquet(GEO_SETTLEMENT,
                        columns=["lga_pcode", "type", "bldg_count", "bldg_area_m2"])
    s["is_builtup"] = s.type.eq("Built-up Area")
    s["nonhamlet_area"] = np.where(s.type.ne("Hamlet"), s.bldg_area_m2, 0.0)
    s["builtup_area"] = np.where(s.is_builtup, s.bldg_area_m2, 0.0)
    s = s[s.lga_pcode.isin(set(lga.lga_pcode))]        # drop state-only / unplaced
    g = s.groupby("lga_pcode")
    sett = pd.DataFrame({
        "n_settlements": g.size(),
        "bldg_count_total": g.bldg_count.sum(),
        "bldg_area_m2_total": g.bldg_area_m2.sum(),
        "n_builtup_settlements": g.is_builtup.sum(),
        "_builtup_area": g.builtup_area.sum(),
        "_nonhamlet_area": g.nonhamlet_area.sum(),
    })
    lga = lga.merge(sett, left_on="lga_pcode", right_index=True, how="left")
    # ~14 dense-urban LGAs get no discrete GRID3 settlement extent (the metro
    # is one merged polygon assigned to a neighbour). Flag, keep NaN — a "0"
    # here would be a lie the model shouldn't learn.
    lga["settlement_data"] = lga.n_settlements.notna()

    # --- facilities (24 states) -------------------------------------
    f = pd.read_parquet(GEO_FACILITY,
                        columns=["lga_pcode", "state_pcode", "level", "type",
                                 "functional", "ownership"])
    fac_states = set(f.state_pcode.unique())
    known = {"Functional", "Not-Functional", "Closed", "Partially Functional"}
    f["is_phc"] = f.type.str.contains("Primary Health", case=False, na=False)
    f["is_referral"] = f.level.isin(["Secondary", "Tertiary"])
    f["is_functional"] = f.functional.eq("Functional")
    f["known_status"] = f.functional.isin(known)
    f["is_public"] = f.ownership.eq("Public")
    gf = f.groupby("lga_pcode")
    fac = pd.DataFrame({
        "n_facilities": gf.size(),
        "n_phc": gf.is_phc.sum(),
        "n_referral": gf.is_referral.sum(),
        "_n_functional": gf.is_functional.sum(),
        "_n_known": gf.known_status.sum(),
        "_n_public": gf.is_public.sum(),
    })
    lga = lga.merge(fac, left_on="lga_pcode", right_index=True, how="left")
    lga["facility_data"] = lga.state_pcode.isin(fac_states)
    fac_cols = ["n_facilities", "n_phc", "n_referral", "_n_functional", "_n_known", "_n_public"]
    lga.loc[lga.facility_data, fac_cols] = lga.loc[lga.facility_data, fac_cols].fillna(0)

    # --- derived ratios ------------------------------------------
    a = lga.area_km2
    lga["bldg_density_km2"] = lga.bldg_count_total / a
    lga["settlement_density_km2"] = lga.n_settlements / a
    lga["builtup_fraction"] = ((lga.bldg_area_m2_total / 1e6) / a).clip(0, 1)
    lga["builtup_core_share"] = (lga._builtup_area / lga.bldg_area_m2_total).clip(0, 1)
    lga["nonhamlet_area_share"] = (lga._nonhamlet_area / lga.bldg_area_m2_total).clip(0, 1)
    lga["mean_settlement_bldg"] = lga.bldg_count_total / lga.n_settlements
    lga["log_bldg_count"] = np.log1p(lga.bldg_count_total)

    lga["fac_per_100k_bldg"] = lga.n_facilities / lga.bldg_count_total * 1e5
    lga["phc_per_100k_bldg"] = lga.n_phc / lga.bldg_count_total * 1e5
    lga["fac_per_1000km2"] = lga.n_facilities / a * 1e3
    lga["pct_fac_functional"] = (lga._n_functional / lga._n_known).where(lga._n_known > 0)
    lga["pct_fac_public"] = (lga._n_public / lga.n_facilities).where(lga.n_facilities > 0)
    lga["pct_fac_referral"] = (lga.n_referral / lga.n_facilities).where(lga.n_facilities > 0)

    # --- accessibility ----------------------------------------
    lga["dist_nearest_city_km"] = _nearest_city_km(lga.centroid_lon.values,
                                                   lga.centroid_lat.values)
    # GRID3 settlement extents merge across LGA lines in big metros, dumping a
    # whole conurbation's buildings into one neighbour and starving the rest.
    # Flag LGAs that sit on a major city yet read near-rural — their building
    # covariates are unreliable; WorldPop pop_density (Tier B) is the fix.
    lga["metro_merge_suspect"] = (
        (lga.dist_nearest_city_km < 25)
        & (lga.bldg_density_km2.fillna(0) < 800)
    )
    lc, la = BIG_CITIES["Lagos"]
    ac, at = BIG_CITIES["Abuja"]
    lga["dist_lagos_km"] = _haversine_km(lga.centroid_lon, lga.centroid_lat, lc, la)
    lga["dist_abuja_km"] = _haversine_km(lga.centroid_lon, lga.centroid_lat, ac, at)

    lga = lga.drop(columns=[c for c in lga.columns if c.startswith("_")])
    keys = ["lga_pcode", "lga_name", "state_pcode", "area_km2",
            "centroid_lon", "centroid_lat",
            "settlement_data", "ward_data", "facility_data", "metro_merge_suspect"]
    lga = (lga[keys + [c for c in lga.columns if c not in keys]]
           .sort_values("lga_pcode").reset_index(drop=True))
    lga.to_parquet(LGA_PARQUET, index=False)

    _write_dict()
    con = duckdb.connect(str(DUCKDB))
    con.execute("CREATE OR REPLACE VIEW covariates_lga AS "
                f"SELECT * FROM read_parquet('{LGA_PARQUET}')")
    con.close()

    covs = [c for c in lga.columns if c not in
            {"lga_pcode", "lga_name", "state_pcode", "settlement_data",
             "ward_data", "facility_data", "metro_merge_suspect"}]
    return {
        "lgas": len(lga),
        "covariates": len(covs),
        "facility_states": len(fac_states),
        "ward_states": len(ward_states),
        "null_counts": {c: int(lga[c].isna().sum()) for c in covs if lga[c].isna().any()},
    }


_DICT = [
    ("area_km2", "geometry", "LGA area", "km2", "spine (OCHA COD)", "all"),
    ("centroid_lon", "geometry", "LGA centroid longitude", "deg", "spine", "all"),
    ("centroid_lat", "geometry", "LGA centroid latitude", "deg", "spine", "all"),
    ("n_wards", "geometry", "Wards in the LGA", "count", "GRID3 wards v3.0", "ward_states"),
    ("n_settlements", "settlement", "Distinct GRID3 settlement extents", "count", "GRID3 settlements v3.1", "settlement_mapped"),
    ("bldg_count_total", "building", "Total building footprints", "count", "GRID3 settlements v3.1", "settlement_mapped"),
    ("bldg_area_m2_total", "building", "Total building footprint area", "m2", "GRID3 settlements v3.1", "settlement_mapped"),
    ("n_builtup_settlements", "settlement", "Settlements typed 'Built-up Area'", "count", "GRID3", "settlement_mapped"),
    ("bldg_density_km2", "building", "Buildings per km2", "per_km2", "derived", "settlement_mapped"),
    ("settlement_density_km2", "settlement", "Settlements per km2", "per_km2", "derived", "settlement_mapped"),
    ("builtup_fraction", "building", "Building area / LGA area (capped at 1)", "ratio", "derived", "settlement_mapped"),
    ("builtup_core_share", "building", "Share of building area in dense urban cores", "ratio", "derived", "settlement_mapped"),
    ("nonhamlet_area_share", "building", "Share of building area outside hamlets", "ratio", "derived", "settlement_mapped"),
    ("mean_settlement_bldg", "settlement", "Mean buildings per settlement", "count", "derived", "settlement_mapped"),
    ("log_bldg_count", "building", "log(1 + total buildings)", "log", "derived", "settlement_mapped"),
    ("n_facilities", "facility", "Health facilities", "count", "GRID3 HF v3.0", "facility_states"),
    ("n_phc", "facility", "Primary health centres/clinics", "count", "GRID3 HF v3.0", "facility_states"),
    ("n_referral", "facility", "Secondary/tertiary facilities", "count", "GRID3 HF v3.0", "facility_states"),
    ("fac_per_100k_bldg", "facility", "Facilities per 100k buildings (access proxy)", "rate", "derived", "facility_states"),
    ("phc_per_100k_bldg", "facility", "PHCs per 100k buildings", "rate", "derived", "facility_states"),
    ("fac_per_1000km2", "facility", "Facilities per 1,000 km2", "rate", "derived", "facility_states"),
    ("pct_fac_functional", "facility", "Share functional (of known status)", "ratio", "derived", "facility_states"),
    ("pct_fac_public", "facility", "Share publicly owned", "ratio", "derived", "facility_states"),
    ("pct_fac_referral", "facility", "Share secondary/tertiary", "ratio", "derived", "facility_states"),
    ("dist_nearest_city_km", "accessibility", "Great-circle distance to nearest of 12 major cities", "km", "derived", "all"),
    ("dist_lagos_km", "accessibility", "Great-circle distance to Lagos", "km", "derived", "all"),
    ("dist_abuja_km", "accessibility", "Great-circle distance to Abuja", "km", "derived", "all"),
    # Tier B — populated only after `covariates worldpop zonal`
    ("pop_2020", "population", "WorldPop UN-adjusted population, 2020", "count", "WorldPop 1km", "worldpop"),
    ("pop_density_km2", "population", "Persons per km2 (WorldPop / area)", "per_km2", "derived", "worldpop"),
    ("pop_u5_2020", "population", "Population under age 5, 2020", "count", "WorldPop AgeSex 1km", "worldpop_agesex"),
    ("pct_u5", "population", "Share of population under age 5", "ratio", "derived", "worldpop_agesex"),
]


def _write_dict() -> None:
    pd.DataFrame(_DICT, columns=["name", "group", "description", "unit",
                                 "source", "coverage"]).to_parquet(DICT_PARQUET, index=False)
