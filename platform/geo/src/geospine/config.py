"""Paths and constants for the geography spine."""

from __future__ import annotations

from pathlib import Path

# platform/geo/
PKG_ROOT = Path(__file__).resolve().parents[2]

DATA = PKG_ROOT / "data"
RAW = DATA / "raw"
SPINE = DATA / "spine"
REFERENCE = PKG_ROOT / "reference"

RAW_OCHA = RAW / "ocha_cod"
RAW_GRID3 = RAW / "grid3"

DUCKDB_PATH = SPINE / "geo.duckdb"

# Canonical output tables (also exported as parquet next to the duckdb file)
UNIT_PARQUET = SPINE / "geo_unit.parquet"
ALIAS_PARQUET = SPINE / "geo_alias.parquet"
SOURCE_META_PARQUET = SPINE / "geo_source_meta.parquet"
CROSSWALK_DHS_PARQUET = SPINE / "crosswalk_dhs.parquet"
# Ward polygons keyed to the minted canonical pcode (GeoParquet). Written by
# build() when the GRID3 ward layer is present; used by PointResolver.
WARD_GEOM_PARQUET = SPINE / "geo_ward_geom.parquet"

# Admin levels. `level` is the integer used everywhere; `name` is for humans.
LEVELS = {
    0: "national",
    1: "state",
    2: "lga",
    3: "ward",
    4: "settlement",
}
LEVEL_BY_NAME = {v: k for k, v in LEVELS.items()}

# Nigeria bounding box (lon/lat) — sanity check for centroids and points.
NG_BBOX = (2.6, 3.9, 14.7, 13.9)  # (min_lon, min_lat, max_lon, max_lat)

for _d in (RAW_OCHA, RAW_GRID3, SPINE):
    _d.mkdir(parents=True, exist_ok=True)
