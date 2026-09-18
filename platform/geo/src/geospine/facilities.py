"""Geocode the GRID3 Health Facilities layer onto the spine.

Output: data/spine/geo_facility.parquet — the Nigeria health-facility registry
keyed to canonical state / LGA / ward P-codes, carrying the NHFR facility code
(the bridge to NHMIS/DHIS2). 41,778 facilities.

Two independent locators, kept side by side so disagreements are visible:
  * by name  — GRID3's own standardised state/LGA/ward name strings resolved
               through NameResolver
  * by point — (lon, lat) through PointResolver (point-in-polygon)
`ward_pcode` is the name-based result; `ward_pcode_pt` the spatial one;
`ward_agree` flags whether they match.
"""

from __future__ import annotations

import duckdb
import geopandas as gpd
import pandas as pd

from . import config
from .resolve import NameResolver, PointResolver

_SRC = "data/raw/grid3/GRID3_NGA_health_facilities_v3_0.gpkg"

_KEEP = {
    "unique_id": "facility_id",
    "nhfr_facility_code": "nhfr_code",
    "facility_name": "name",
    "alt_name": "alt_name",
    "settlement_name": "settlement_name",
    "facility_level": "level",
    "facility_type": "type",
    "facility_ownership": "ownership",
    "facility_ownership_type": "ownership_type",
    "functional": "functional",
    "sett_ext_type": "settlement_ext_type",
    "longitude": "lon",
    "latitude": "lat",
}


def build() -> dict:
    src = config.PKG_ROOT / _SRC
    if not src.exists():
        raise FileNotFoundError(f"{src} — run `geospine fetch` first.")
    if not config.DUCKDB_PATH.exists():
        raise FileNotFoundError("spine not built — run `geospine build` first.")

    g = gpd.read_file(src).to_crs(4326)
    df = g[list(_KEEP)].rename(columns=_KEEP).copy()
    df["lon"] = df["lon"].fillna(g.geometry.x)
    df["lat"] = df["lat"].fillna(g.geometry.y)

    # ── name-based resolution ──────────────────────────────────────────
    r_state = NameResolver(level=1)
    state_pc, state_score = _resolve_col(r_state, g["state_standard"])

    lga_pc, lga_score = [], []
    lga_resolvers: dict[str, NameResolver] = {}
    for spc, name in zip(state_pc, g["lga_standard"]):
        if spc is None:
            lga_pc.append(None); lga_score.append(0.0); continue
        r = lga_resolvers.get(spc) or lga_resolvers.setdefault(
            spc, NameResolver(level=2, parent_pcode=spc))
        m = r.resolve(str(name))
        lga_pc.append(m.pcode); lga_score.append(m.score)

    ward_pc, ward_score = [], []
    ward_resolvers: dict[str, NameResolver] = {}
    for lpc, name in zip(lga_pc, g["ward_standard"]):
        if lpc is None:
            ward_pc.append(None); ward_score.append(0.0); continue
        r = ward_resolvers.get(lpc) or ward_resolvers.setdefault(
            lpc, NameResolver(level=3, parent_pcode=lpc))
        m = r.resolve(str(name))
        ward_pc.append(m.pcode); ward_score.append(m.score)

    df["state_pcode"] = state_pc
    df["lga_pcode"] = lga_pc
    df["ward_pcode"] = ward_pc
    df["name_match_min_score"] = [
        min(s, l, w) for s, l, w in zip(state_score, lga_score, ward_score)
    ]

    # ── point-based cross-check (vectorised: one sjoin per layer) ──────
    pr = PointResolver()
    pt = pr.locate_frame(df[["lon", "lat"]])
    df["state_pcode_pt"] = pt["state_pcode_pt"].values
    df["lga_pcode_pt"] = pt["lga_pcode_pt"].values
    df["ward_pcode_pt"] = pt["ward_pcode_pt"].values
    df["ward_agree"] = df["ward_pcode"].eq(df["ward_pcode_pt"]) & df["ward_pcode"].notna()

    df.to_parquet(config.SPINE / "geo_facility.parquet", index=False)

    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS geo_facility")
    con.register("f", df)
    con.execute("CREATE TABLE geo_facility AS SELECT * FROM f")
    con.close()

    n = len(df)
    return {
        "facilities": n,
        "with_state": int(df.state_pcode.notna().sum()),
        "with_lga": int(df.lga_pcode.notna().sum()),
        "with_ward_by_name": int(df.ward_pcode.notna().sum()),
        "with_ward_by_point": int(df.ward_pcode_pt.notna().sum()),
        "ward_name_point_agree": int(df.ward_agree.sum()),
        "with_nhfr_code": int(df.nhfr_code.notna().sum()),
        "parquet": str(config.SPINE / "geo_facility.parquet"),
    }


def _resolve_col(resolver: NameResolver, col) -> tuple[list, list]:
    cache: dict[str, tuple] = {}
    pcs, scs = [], []
    for v in col:
        key = str(v)
        if key not in cache:
            m = resolver.resolve(key)
            cache[key] = (m.pcode, m.score)
        pc, sc = cache[key]
        pcs.append(pc); scs.append(sc)
    return pcs, scs
