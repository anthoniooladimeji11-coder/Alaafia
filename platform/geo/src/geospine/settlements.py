"""Level-4 settlement layer from GRID3 NGA Settlement Extents v3.1.

The extents GPKG is ~700k+ polygons (Built-up Areas, Small Settlement Areas,
Hamlets). We reduce it to a points table keyed to the spine:

  geo_settlement.parquet   pcode, ward_pcode, lga_pcode, state_pcode, name,
                           type, bldg_count, bldg_area_m2, area_km2,
                           center_lon, center_lat, source_id
  geo_settlement_geom.parquet   pcode + polygon   (git-ignored, large)

Both are BUILD PRODUCTS — git-ignored, regenerated from the raw GPKG. Only the
levels 0–3 spine and the facility registry are committed.

Settlement P-codes are minted:  <ward_pcode> "S" <5-digit sequence within ward,
ordered by descending building count>.  Bound to grid3_settlements v3.1.
"""

from __future__ import annotations

import zipfile

import duckdb
import geopandas as gpd
import pandas as pd

from . import config
from .normalize import name_key, norm_name
from .resolve import NameResolver, PointResolver

_ZIP = "grid3/GRID3_NGA_settlement_extents_v3_1_gpkg.zip"

# GRID3 extents column names vary by release — resolve against these candidates.
_FIELDS = {
    "sid": ["mgrs_code", "settlement_id", "sid", "id", "dou_id"],
    "name": ["settlement_name", "name", "sett_name", "primary_name"],
    "type": ["type", "settlement_type", "sett_type", "class"],
    "bldg_count": ["building_count", "bldg_count", "count", "imputed_building_count"],
    "bldg_area": ["building_area", "bldg_area", "sum_building_area", "imputed_building_area"],
    "area_km2": ["area_km2", "area_sqkm", "sqkm", "shape_area"],
    "state": ["statename", "admin1name", "state", "adm1_name"],
    "lga": ["lganame", "admin2name", "lga", "adm2_name"],
    "ward": ["wardname", "admin3name", "ward", "adm3_name"],
}


def _pick(cols_lower, opts):
    for o in opts:
        if o in cols_lower:
            return cols_lower[o]
    return None


def _read_gpkg() -> gpd.GeoDataFrame:
    src = config.PKG_ROOT / "data/raw" / _ZIP
    if not src.exists():
        raise FileNotFoundError(
            f"{src} — run `geospine fetch --big` (settlement extents is ~736 MB)."
        )
    with zipfile.ZipFile(src) as z:
        gpkg = next(n for n in z.namelist() if n.lower().endswith(".gpkg"))
    return gpd.read_file(f"zip://{src}!{gpkg}").to_crs(4326)


# The expensive step (read 745k polygons + representative points + one big
# point-in-polygon sjoin, ~7 min) is checkpointed here so re-runs that only
# change the P-code scheme or the output columns are instant.
_CKPT = "grid3/_settlement_geocoded.parquet"


def _geocode(g_getter):
    """Returns (df, geometry_ndarray, detected_fields). The ~7-min step."""
    g = g_getter()
    cl = {c.lower(): c for c in g.columns}
    f = {k: _pick(cl, opts) for k, opts in _FIELDS.items()}
    if f["type"] is None and f["bldg_count"] is None:
        raise RuntimeError(f"Unrecognised GRID3 extents schema: {list(g.columns)}")

    n = len(g)
    df = pd.DataFrame({
        "_orig": range(n),
        "source_id": g[f["sid"]].astype(str) if f["sid"] else [f"row{i}" for i in range(n)],
        "name": g[f["name"]].astype("string") if f["name"] else pd.Series([pd.NA] * n, dtype="string"),
        "type": g[f["type"]].astype("string") if f["type"] else pd.Series([pd.NA] * n, dtype="string"),
        "bldg_count": pd.to_numeric(g[f["bldg_count"]], errors="coerce") if f["bldg_count"] else pd.Series([pd.NA] * n),
        "bldg_area_m2": pd.to_numeric(g[f["bldg_area"]], errors="coerce") if f["bldg_area"] else pd.Series([pd.NA] * n),
        "area_km2": pd.to_numeric(g[f["area_km2"]], errors="coerce") if f["area_km2"] else pd.Series([pd.NA] * n),
    })
    reps = g.geometry.representative_point()
    df["center_lon"] = reps.x.values
    df["center_lat"] = reps.y.values

    # v3.1 extents carry no admin names → pure point-in-polygon. Keep all three
    # levels: a settlement whose centroid misses a ward polygon (ward tiling has
    # gaps) usually still lands in an LGA.
    pt = PointResolver().locate_frame(
        df[["center_lon", "center_lat"]].rename(
            columns={"center_lon": "lon", "center_lat": "lat"})
    )
    df["ward_pcode_pt"] = pt["ward_pcode_pt"].values
    df["lga_pcode_pt"] = pt["lga_pcode_pt"].values
    df["state_pcode_pt"] = pt["state_pcode_pt"].values

    if f["state"] and f["lga"] and f["ward"]:
        by_name = _by_name(g, f)
        df["ward_pcode_pt"] = df["ward_pcode_pt"].where(by_name.isna(), by_name.values)
    return df, g.geometry.values, f


def build(*, refresh: bool = False) -> dict:
    if not config.DUCKDB_PATH.exists():
        raise FileNotFoundError("spine not built — run `geospine build` first.")

    ckpt = config.PKG_ROOT / "data/raw" / _CKPT
    src_zip = config.PKG_ROOT / "data/raw" / _ZIP
    geom_src = None
    fields: dict = {}
    if ckpt.exists() and not refresh and ckpt.stat().st_mtime >= src_zip.stat().st_mtime:
        df = pd.read_parquet(ckpt)
        print(f"  (using geocode checkpoint — {len(df):,} rows; --refresh to rebuild)")
    else:
        df, geom_src, fields = _geocode(_read_gpkg)
        df.to_parquet(ckpt, index=False)  # plain df, no geometry, safe to serialise

    # ── resolve final parent: ward if we have one, else LGA, else state ──
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    ward_anc = con.execute(
        "SELECT pcode w, adm2_pcode l, adm1_pcode s FROM geo_unit WHERE level=3"
    ).fetchdf().set_index("w")
    lga_state = con.execute(
        "SELECT pcode l, adm1_pcode s FROM geo_unit WHERE level=2"
    ).fetchdf().set_index("l")["s"].to_dict()
    con.close()

    w2l = ward_anc["l"].to_dict()
    w2s = ward_anc["s"].to_dict()
    df["ward_pcode"] = df["ward_pcode_pt"].where(df["ward_pcode_pt"].isin(w2l))
    df["lga_pcode"] = df["ward_pcode"].map(w2l)
    df["lga_pcode"] = df["lga_pcode"].fillna(
        df["lga_pcode_pt"].where(df["lga_pcode_pt"].isin(lga_state)))
    df["state_pcode"] = df["ward_pcode"].map(w2s)
    df["state_pcode"] = df["state_pcode"].fillna(df["lga_pcode"].map(lga_state))
    df["state_pcode"] = df["state_pcode"].fillna(df["state_pcode_pt"])
    df["parent_pcode"] = df["ward_pcode"].fillna(df["lga_pcode"]).fillna(df["state_pcode"])
    df["parent_level"] = (
        df["ward_pcode"].notna().map({True: 3}).fillna(
            df["lga_pcode"].notna().map({True: 2})).fillna(
            df["state_pcode"].notna().map({True: 1})).fillna(0).astype(int)
    )

    # ── mint pcodes: within parent, ordered by descending building count ──
    df["_bc"] = pd.to_numeric(df["bldg_count"], errors="coerce").fillna(0)
    df = df.sort_values(["parent_pcode", "_bc"], ascending=[True, False]).reset_index(drop=True)
    df["_seq"] = df.groupby("parent_pcode", dropna=False).cumcount() + 1
    df["pcode"] = [
        f"{p}S{int(s):05d}" if isinstance(p, str) and p else f"NGxxxxS{i:06d}"
        for i, (p, s) in enumerate(zip(df["parent_pcode"], df["_seq"]))
    ]
    df["name_norm"] = df["name"].map(lambda x: norm_name(x) if pd.notna(x) else None)

    out = df[[
        "pcode", "parent_pcode", "parent_level", "ward_pcode", "lga_pcode",
        "state_pcode", "name", "name_norm", "type", "bldg_count", "bldg_area_m2",
        "area_km2", "center_lon", "center_lat", "source_id",
    ]]
    out.to_parquet(config.SPINE / "geo_settlement.parquet", index=False)

    # geometry aligned to the (sorted) output order via the preserved original
    # index. Only re-exported on a full run; the checkpoint path leaves the
    # existing geo_settlement_geom.parquet in place.
    if geom_src is not None:
        gpd.GeoDataFrame(
            {"pcode": df["pcode"].values},
            geometry=geom_src[df["_orig"].values],
            crs=4326,
        ).to_parquet(config.SPINE / "geo_settlement_geom.parquet")

    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS geo_settlement")
    con.register("s", out)
    con.execute("CREATE TABLE geo_settlement AS SELECT * FROM s")
    con.close()

    return {
        "settlements": int(len(out)),
        "to_ward": int((out.parent_level == 3).sum()),
        "to_lga_only": int((out.parent_level == 2).sum()),
        "to_state_only": int((out.parent_level == 1).sum()),
        "unplaced": int((out.parent_level == 0).sum()),
        "named": int(out.name.notna().sum()),
        "by_type": {str(k): int(v) for k, v in out["type"].value_counts().to_dict().items()},
        "total_buildings": int(pd.to_numeric(out.bldg_count, errors="coerce").sum()),
        "columns_detected": fields or "(from checkpoint)",
        "parquet": str(config.SPINE / "geo_settlement.parquet"),
    }


def _by_name(g: gpd.GeoDataFrame, f: dict) -> pd.Series:
    r_state = NameResolver(level=1)
    state_cache, lga_res, ward_res = {}, {}, {}
    lga_cache, ward_cache = {}, {}

    def sp(v):
        v = str(v)
        if v not in state_cache:
            state_cache[v] = r_state.resolve(v).pcode
        return state_cache[v]

    def lp(spc, v):
        if spc is None:
            return None
        k = (spc, str(v))
        if k not in lga_cache:
            r = lga_res.get(spc) or lga_res.setdefault(spc, NameResolver(level=2, parent_pcode=spc))
            lga_cache[k] = r.resolve(str(v)).pcode
        return lga_cache[k]

    def wp(lpc, v):
        if lpc is None:
            return None
        k = (lpc, str(v))
        if k not in ward_cache:
            r = ward_res.get(lpc) or ward_res.setdefault(lpc, NameResolver(level=3, parent_pcode=lpc))
            ward_cache[k] = r.resolve(str(v)).pcode
        return ward_cache[k]

    out = []
    for st, lg, wd in zip(g[f["state"]], g[f["lga"]], g[f["ward"]]):
        out.append(wp(lp(sp(st), lg), wd))
    return pd.Series(out, dtype="object")
