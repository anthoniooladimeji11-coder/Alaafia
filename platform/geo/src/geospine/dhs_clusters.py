"""Geocode every DHS round's GPS cluster layer onto the spine.

Output: data/spine/geo_dhs_cluster.parquet — one row per (survey_round,
cluster_id), carrying the canonical state/LGA P-code for that cluster's
GPS coordinate. This is the join key the unit-level model snaps KR/IR/HR/BR
respondent rows onto (they carry v001 = cluster_id, no lon/lat of their own).

DHS displaces every published cluster coordinate for respondent privacy —
up to ~2km urban / ~5km rural, 10km for a random 1% of rural clusters — so
a point can land across an LGA line, occasionally a state line, from where
the household actually was. We can't undo that, but we don't have to hide
it: same two-locator pattern as facilities.py — DHS's own ADM1NAME (their
survey-design state label, independent of GPS) checked against the
point-in-polygon state. Where they disagree, the LGA drawn from the point
is suspect too; `low_confidence` flags it rather than silently shipping it.
Ward-level snapping isn't attempted at all: displacement is routinely
larger than a ward, so a ward-level point-in-polygon result would be noise
dressed up as precision.
"""

from __future__ import annotations

import duckdb
import geopandas as gpd
import pandas as pd

from . import config
from .resolve import NameResolver, PointResolver

# round_label -> GE shapefile, under the sibling survey package's raw microdata.
# Cross-package read of a raw/ folder — same precedent as the model package's
# explorer reaching into this package's raw OCHA shapefile directly.
_SURVEY_RAW = config.PKG_ROOT.parent / "survey" / "data" / "raw" / "microdata"
ROUNDS: dict[str, str] = {
    "NG1990DHS": "NGGE23FL.shp",
    "NG2003DHS": "NGGE4BFL.shp",
    "NG2008DHS": "NGGE52FL.shp",
    "NG2013DHS": "NGGE6AFL.shp",
    "NG2018DHS": "NGGE7BFL.shp",
    "NG2024DHS": "NGGE8AFL.shp",
}

_KEEP = {
    "DHSCLUST": "cluster_id", "DHSYEAR": "dhs_year", "ADM1NAME": "adm1name_dhs",
    "URBAN_RURA": "urban_rural", "LATNUM": "lat", "LONGNUM": "lon", "ALT_GPS": "alt_gps",
}


def _round_frame(round_label: str, shp_path) -> pd.DataFrame:
    g = gpd.read_file(shp_path)
    df = g[list(_KEEP)].rename(columns=_KEEP).copy()
    df["cluster_id"] = df["cluster_id"].astype(int)
    df.insert(0, "survey_round", round_label)
    return df


def build() -> dict:
    if not config.DUCKDB_PATH.exists():
        raise FileNotFoundError("spine not built — run `geospine build` first.")

    frames, missing = [], []
    for round_label, fname in ROUNDS.items():
        shp = _SURVEY_RAW / round_label / "GE" / fname
        if not shp.exists():
            missing.append(round_label)
            continue
        frames.append(_round_frame(round_label, shp))
    if not frames:
        raise FileNotFoundError(
            f"no GE shapefiles found under {_SURVEY_RAW}/<ROUND>/GE/ — "
            "copy the DHS GE recode in first."
        )
    df = pd.concat(frames, ignore_index=True)

    # zero/implausible coordinates happen occasionally in older rounds — drop
    # them, don't silently geocode (0,0) into the Gulf of Guinea as if real.
    bad_coord = (df.lat == 0) & (df.lon == 0)
    df["coord_missing"] = bad_coord

    # ── name-based: DHS's own survey-design state label, GPS-independent ──
    # Some older rounds (1990, 2003) ship the literal string "NULL" for every
    # row instead of leaving the field blank — DHS didn't publish this label
    # for those rounds, full stop. That's "no cross-check available", not
    # "the label disagreed" — the two must not be conflated below, or every
    # cluster in those rounds would read as suspect when the GPS point itself
    # was never in question.
    name_available = (
        df.adm1name_dhs.notna()
        & df.adm1name_dhs.astype(str).str.strip().ne("")
        & ~df.adm1name_dhs.astype(str).str.upper().eq("NULL")
    )
    r_state = NameResolver(level=1)
    cache: dict[str, tuple] = {}
    name_pc, name_sc = [], []
    for v, avail in zip(df.adm1name_dhs, name_available):
        if not avail:
            name_pc.append(None); name_sc.append(0.0)
            continue
        key = str(v)
        if key not in cache:
            m = r_state.resolve(key)
            cache[key] = (m.pcode, m.score)
        pc, sc = cache[key]
        name_pc.append(pc); name_sc.append(sc)
    df["state_pcode_name"] = name_pc
    df["state_name_match_score"] = name_sc
    df["name_label_available"] = name_available

    # ── point-based: point-in-polygon on the (displaced) GPS coordinate ───
    # Join back by an explicit key, not row position — locate_frame resets
    # its internal index, and silently trusting position-after-filter is
    # exactly the bug class disaggregate.py already paid for once.
    valid = df.loc[~bad_coord, ["lon", "lat"]].copy()
    valid["_row_key"] = valid.index.values
    pt = PointResolver().locate_frame(valid, lon="lon", lat="lat")
    lookup = pt.set_index("_row_key")[["state_pcode_pt", "lga_pcode_pt"]]
    df["state_pcode_pt"] = df.index.map(lookup["state_pcode_pt"])
    df["lga_pcode_pt"] = df.index.map(lookup["lga_pcode_pt"])

    df["state_agree"] = df.state_pcode_name.eq(df.state_pcode_pt) & df.state_pcode_name.notna()
    df["lga_pcode"] = df["lga_pcode_pt"]

    # Two different reasons a row can fail the cross-check, worth telling
    # apart: a label that didn't resolve to ANY state is most likely a
    # spelling/formatting gap in NameResolver against this round's label
    # (seen once: 2013's "FCT-Abuja" hyphenation — other rounds' "Abuja" /
    # "FCT ABUJA" / "Fct" all resolve fine) and says little about the GPS
    # point. A label that resolved cleanly to a DIFFERENT state than the
    # point landed in is the real signal — genuine border-adjacent
    # displacement (observed: Zamfara/Kebbi, Ebonyi/Enugu — all adjacent
    # states, consistent with DHS's documented displacement radius).
    df["name_unresolved"] = df["name_label_available"] & df["state_pcode_name"].isna()
    df["state_conflict"] = (
        df["name_label_available"] & df["state_pcode_name"].notna() & ~df["state_agree"]
    )
    # low_confidence stays the broad "treat with care" flag — union of both
    # plus missing coordinates — but the two columns above let a downstream
    # reader tell a likely-fine spelling gap from a real place conflict.
    df["low_confidence"] = df["name_unresolved"] | df["state_conflict"] | df["coord_missing"]

    df.to_parquet(config.SPINE / "geo_dhs_cluster.parquet", index=False)

    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS geo_dhs_cluster")
    con.register("c", df)
    con.execute("CREATE TABLE geo_dhs_cluster AS SELECT * FROM c")
    con.close()

    by_round = (
        df.groupby("survey_round", sort=False)
        .agg(clusters=("cluster_id", "size"),
             with_lga=("lga_pcode", lambda s: int(s.notna().sum())),
             name_label_available=("name_label_available", "sum"),
             state_agree=("state_agree", "sum"),
             name_unresolved=("name_unresolved", "sum"),
             state_conflict=("state_conflict", "sum"))
        .to_dict("index")
    )
    return {
        "clusters": len(df),
        "rounds_found": [r for r in ROUNDS if r not in missing],
        "rounds_missing": missing,
        "with_lga": int(df.lga_pcode.notna().sum()),
        "name_label_available": int(df.name_label_available.sum()),
        "state_name_point_agree": int(df.state_agree.sum()),
        "name_unresolved": int(df.name_unresolved.sum()),
        "state_conflict": int(df.state_conflict.sum()),
        "low_confidence": int(df.low_confidence.sum()),
        "coord_missing": int(df.coord_missing.sum()),
        "by_round": by_round,
        "parquet": str(config.SPINE / "geo_dhs_cluster.parquet"),
    }
