"""Paths, constants, the state-level covariate set."""

from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent                     # platform/model
DATA = ROOT / "data"
OUT = DATA / "model"
OUT.mkdir(parents=True, exist_ok=True)

# sibling packages' committed outputs
SURVEY = ROOT.parent / "survey" / "data" / "survey" / "survey_indicator.parquet"
SURVEY_SERIES = ROOT.parent / "survey" / "data" / "survey" / "survey_series.parquet"
COV_LGA = ROOT.parent / "covariates" / "data" / "covariates" / "covariates_lga.parquet"
GEO_UNIT = ROOT.parent / "geo" / "data" / "spine" / "geo_unit.parquet"

FH_STATE_PARQUET = OUT / "fh_state.parquet"          # all fitted indicators, long
SAE_LGA_PARQUET = OUT / "sae_lga.parquet"
INDICATOR_META_PARQUET = OUT / "indicator_meta.parquet"   # slug, domain, unit, label, worse_high
DUCKDB = OUT / "model.duckdb"

# Covariates carried into the state-level regression, and later applied
# per-LGA in Stage 2. Kept short and generic on purpose (m=37 areas; a
# Fay-Herriot regression with many predictors overfits fast) — and,
# deliberately, NOT the facility-derived covariates: those are NaN for
# the 261 LGAs in the 13 states GRID3's facility layer doesn't cover
# yet, which would either drop a third of the country from Stage 2 or
# force a heavy imputation nobody should trust. `pop_density_km2` and
# `dist_nearest_city_km` are complete for all 774 LGAs; the settlement
# pair is missing for only the ~14 LGAs `disaggregate.py` imputes.
STATE_COVARIATES = [
    "pop_density_km2", "builtup_fraction", "settlement_density_km2",
    "dist_nearest_city_km",
]

# DHS-typical design effect used to approximate sampling variance when
# the API doesn't publish a CI for a cell (~87% of rows). This is a
# documented approximation, not a design-based SE — see model/README.md.
DEFAULT_DEFF = 2.0

MIN_STATES_TO_FIT = 20                          # below this, don't trust FH
