"""Paths — reads sibling packages' committed outputs directly (parquet
files), the same loose-coupling pattern every platform/ package uses;
no cross-package Python imports."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent    # platform/brief
PLATFORM = ROOT.parent

MODEL_DIR = PLATFORM / "model" / "data" / "model"
FH_STATE = MODEL_DIR / "fh_state.parquet"
INDICATOR_META = MODEL_DIR / "indicator_meta.parquet"

SURVEY_INDICATOR = PLATFORM / "survey" / "data" / "survey" / "survey_indicator.parquet"
SURVEY_SOURCE_META = PLATFORM / "survey" / "data" / "survey" / "survey_source_meta.parquet"

GEO_UNIT = PLATFORM / "geo" / "data" / "spine" / "geo_unit.parquet"
COV_LGA = PLATFORM / "covariates" / "data" / "covariates" / "covariates_lga.parquet"

OUT = Path(__file__).resolve().parent.parent.parent / "build"
OUT.mkdir(exist_ok=True)

# how many indicators to headline as "notable" on each side (concerns / strengths)
N_HEADLINE = 3
