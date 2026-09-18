"""Paths, endpoints, constants."""

from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent                      # platform/survey
DATA = ROOT / "data"
RAW = DATA / "raw"
OUT = DATA / "survey"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# geography spine outputs (committed in the sibling package)
GEO_SPINE = ROOT.parent / "geo" / "data" / "spine"
GEO_UNIT_PARQUET = GEO_SPINE / "geo_unit.parquet"
CROSSWALK_DHS_PARQUET = GEO_SPINE / "crosswalk_dhs.parquet"

# outputs
INDICATOR_PARQUET = OUT / "survey_indicator.parquet"     # long fact table
SERIES_PARQUET = OUT / "survey_series.parquet"           # indicator dictionary
SOURCE_META_PARQUET = OUT / "survey_source_meta.parquet"
DUCKDB = OUT / "survey.duckdb"

# ---- DHS program API ----------------------------------------------------
DHS_API = "https://api.dhsprogram.com/rest/dhs"
DHS_COUNTRY = "NG"
DHS_PERPAGE = 1000
DHS_PAUSE_S = 0.35                                       # be polite

# The six geopolitical zones as DHS labels them (v024 scheme).
DHS_ZONES = {
    "North Central", "North East", "North West",
    "South East", "South South", "South West",
}
