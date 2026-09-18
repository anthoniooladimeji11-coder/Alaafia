"""Paths and constants."""

from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent                        # platform/covariates
DATA = ROOT / "data"
RAW = DATA / "raw"
OUT = DATA / "covariates"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# geography spine (committed sibling package)
GEO_SPINE = ROOT.parent / "geo" / "data" / "spine"
GEO_UNIT = GEO_SPINE / "geo_unit.parquet"
GEO_SETTLEMENT = GEO_SPINE / "geo_settlement.parquet"
GEO_FACILITY = GEO_SPINE / "geo_facility.parquet"
# LGA polygons for Tier B zonal stats
OCHA_SHP_ZIP = ROOT.parent / "geo" / "data" / "raw" / "ocha_cod" / "nga_admin_boundaries.shp.zip"

# outputs
LGA_PARQUET = OUT / "covariates_lga.parquet"
DICT_PARQUET = OUT / "covariates_dict.parquet"
DUCKDB = OUT / "covariates.duckdb"

# major urban centres — crude accessibility proxy (lon, lat)
BIG_CITIES = {
    "Lagos": (3.379, 6.524), "Kano": (8.520, 12.000), "Ibadan": (3.900, 7.378),
    "Abuja": (7.398, 9.076), "Port Harcourt": (7.010, 4.824), "Kaduna": (7.438, 10.523),
    "Benin City": (5.626, 6.339), "Maiduguri": (13.151, 11.833), "Enugu": (7.510, 6.459),
    "Jos": (8.892, 9.897), "Ilorin": (4.550, 8.500), "Sokoto": (5.243, 13.061),
}
