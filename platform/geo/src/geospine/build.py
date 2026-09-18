"""Build the canonical spine tables from the raw sources.

Outputs (in data/spine/):
  geo.duckdb            — geo_unit, geo_alias, geo_source_meta  (+ crosswalk_dhs
                          once crosswalks.dhs has run)
  geo_unit.parquet
  geo_alias.parquet
  geo_source_meta.parquet

geo_unit schema:
  pcode            TEXT  PK   canonical P-code
  level            INT        0 national · 1 state · 2 lga · 3 ward · 4 settlement
  level_name       TEXT
  name             TEXT       normalised display name  ("Aba North")
  name_official    TEXT       exact source spelling
  name_key         TEXT       aggressive lookup key
  parent_pcode     TEXT
  adm1_pcode       TEXT       denormalised ancestors, for fast filtering
  adm2_pcode       TEXT
  senatorial_pcode TEXT       alternate political hierarchy (state → sen. district → LGA)
  senatorial_name  TEXT
  area_sqkm        DOUBLE
  center_lon       DOUBLE
  center_lat       DOUBLE
  valid_from       DATE
  valid_to         DATE       NULL = current
  source           TEXT       sources.py key
  source_version   TEXT
"""

from __future__ import annotations

import json

import duckdb
import pandas as pd

from . import config
from .normalize import name_key, norm_name

_UNIT_COLS = [
    "pcode", "level", "level_name", "name", "name_official", "name_key",
    "parent_pcode", "adm1_pcode", "adm2_pcode", "senatorial_pcode",
    "senatorial_name", "area_sqkm", "center_lon", "center_lat",
    "valid_from", "valid_to", "source", "source_version",
]


# ─────────────────────────── OCHA COD ────────────────────────────────────
def _ocha_xlsx() -> pd.ExcelFile:
    p = config.RAW_OCHA / "nga_admin_boundaries.xlsx"
    if not p.exists():
        raise FileNotFoundError(
            f"{p} missing — run `geospine fetch` first (needs the OCHA COD)."
        )
    return pd.ExcelFile(p)


def _row(level, pcode, name_official, parent, adm1, adm2, sd_pc, sd_name,
         area, lon, lat, valid_on, valid_to, version):
    return {
        "pcode": pcode,
        "level": level,
        "level_name": config.LEVELS[level],
        "name": norm_name(name_official),
        "name_official": str(name_official).strip(),
        "name_key": name_key(name_official),
        "parent_pcode": parent,
        "adm1_pcode": adm1,
        "adm2_pcode": adm2,
        "senatorial_pcode": sd_pc,
        "senatorial_name": sd_name,
        "area_sqkm": area,
        "center_lon": lon,
        "center_lat": lat,
        "valid_from": pd.to_datetime(valid_on).date() if pd.notna(valid_on) else None,
        "valid_to": pd.to_datetime(valid_to).date() if pd.notna(valid_to) else None,
        "source": "ocha_cod",
        "source_version": version,
    }


def _build_ocha() -> tuple[pd.DataFrame, pd.DataFrame]:
    xl = _ocha_xlsx()
    a0 = xl.parse("nga_admin0")
    a1 = xl.parse("nga_admin1")
    a2 = xl.parse("nga_admin2")
    try:
        a3 = xl.parse("nga_admin3")
    except ValueError:
        a3 = None

    units: list[dict] = []
    aliases: list[dict] = []

    # level 0
    r = a0.iloc[0]
    units.append(_row(0, r["adm0_pcode"], r["adm0_name"], None, None, None, None,
                      None, r.get("area_sqkm"), r.get("center_lon"),
                      r.get("center_lat"), r.get("valid_on"), r.get("valid_to"),
                      r.get("version")))

    # level 1 — states
    for _, r in a1.iterrows():
        pc = r["adm1_pcode"]
        units.append(_row(1, pc, r["adm1_name"], r["adm0_pcode"], pc, None, None,
                          None, r.get("area_sqkm"), r.get("center_lon"),
                          r.get("center_lat"), r.get("valid_on"), r.get("valid_to"),
                          r.get("version")))
        _add_aliases(aliases, pc, r, "adm1")

    # level 2 — LGAs
    for _, r in a2.iterrows():
        pc = r["adm2_pcode"]
        units.append(_row(2, pc, r["adm2_name"], r["adm1_pcode"], r["adm1_pcode"],
                          pc, r.get("sendistpcode"), r.get("sendist_en"),
                          r.get("area_sqkm"), r.get("center_lon"),
                          r.get("center_lat"), r.get("valid_on"), r.get("valid_to"),
                          r.get("version")))
        _add_aliases(aliases, pc, r, "adm2")

    # level 3 — OCHA partial wards (only if GRID3 not available; see _merge_wards)
    if a3 is not None:
        for _, r in a3.iterrows():
            pc = r["adm3_pcode"]
            units.append(_row(3, pc, r["adm3_name"], r["adm2_pcode"],
                              r["adm1_pcode"], r["adm2_pcode"],
                              r.get("sendistpcode"), r.get("sendist_en"),
                              r.get("area_sqkm"), r.get("center_lon"),
                              r.get("center_lat"), r.get("valid_on"),
                              r.get("valid_to"), r.get("version")))
            _add_aliases(aliases, pc, r, "adm3")

    return pd.DataFrame(units, columns=_UNIT_COLS), pd.DataFrame(aliases)


def _apply_manual_aliases(units: pd.DataFrame, aliases: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Fold reference/manual_aliases.csv into geo_alias (renames, known typos)."""
    p = config.REFERENCE / "manual_aliases.csv"
    if not p.exists():
        return aliases, 0
    man = pd.read_csv(p)
    state_pc = dict(zip(units.loc[units.level == 1, "name_key"],
                        units.loc[units.level == 1, "pcode"]))
    rows, applied = [], 0
    for _, x in man.iterrows():
        lvl = int(x["level"])
        spc = state_pc.get(name_key(str(x["state_name"])))
        if spc is None:
            continue
        cand = units[(units.level == lvl) & (units.adm1_pcode == spc)
                     & (units.name_key == name_key(str(x["canonical_name"])))]
        if cand.empty:
            print(f"  manual_aliases: canonical '{x['canonical_name']}' not found in {x['state_name']}")
            continue
        rows.append({
            "pcode": cand.iloc[0]["pcode"], "alias": str(x["alias"]).strip(),
            "alias_key": name_key(str(x["alias"])), "alias_type": "manual",
            "source": "reference/manual_aliases.csv",
        })
        applied += 1
    if rows:
        aliases = pd.concat([aliases, pd.DataFrame(rows)], ignore_index=True)
    return aliases, applied


def _add_aliases(bucket: list[dict], pcode: str, r: pd.Series, prefix: str) -> None:
    seen = set()

    def push(val, atype):
        if pd.isna(val):
            return
        val = str(val).strip()
        k = name_key(val)
        if not k or k in seen:
            return
        seen.add(k)
        bucket.append({
            "pcode": pcode, "alias": val, "alias_key": k,
            "alias_type": atype, "source": "ocha_cod",
        })

    push(r.get(f"{prefix}_name"), "official")
    push(r.get(f"{prefix}_ref_name"), "ref_name")
    for i in (1, 2, 3):
        push(r.get(f"{prefix}_name{i}"), "altname")


# ─────────────────────────── GRID3 wards ────────────────────────────────
# GRID3 Operational Wards v3.0 carries NO ward P-code and no LGA code — only
# name columns (`state`, `lga`, `ward`) + alt-name lists. We resolve the ward's
# LGA by name (scoped to its state) against the OCHA layer already built, then
# MINT a ward pcode by extending the OCHA hierarchy:  <lga_pcode><NNN>,
# NNN = 3-digit sequence over wards in that LGA ordered by normalised name.
_GRID3_GPKG = "GRID3_NGA_operational_wards_v3_0.gpkg"


def _merge_wards(units: pd.DataFrame, aliases: pd.DataFrame):
    gpkg = config.RAW_GRID3 / _GRID3_GPKG
    if not gpkg.exists():
        n = int((units["level"] == 3).sum())
        return units, aliases, (
            f"wards: {n} from ocha_cod (PARTIAL — humanitarian coverage only). "
            f"Run `geospine fetch` to pull GRID3 Operational Wards v3.0."
        )

    import geopandas as gpd
    from rapidfuzz import fuzz, process

    g = gpd.read_file(gpkg).to_crs(4326)
    g["_rep"] = g.geometry.representative_point()

    # in-memory resolution against the OCHA units already built (DuckDB isn't
    # written until the end of build()).
    states = units[units["level"] == 1]
    lgas = units[units["level"] == 2]
    state_key = dict(zip(states["name_key"], states["pcode"]))
    state_names = dict(zip(states["pcode"], states["name"]))
    lga_key_by_state: dict[str, dict[str, str]] = {}
    lga_names_by_state: dict[str, dict[str, str]] = {}
    lga_pcodes = set(lgas["pcode"])
    alias_key_to_pc = dict(zip(aliases["alias_key"], aliases["pcode"]))
    for spc in states["pcode"]:
        sub = lgas[lgas["adm1_pcode"] == spc]
        km = dict(zip(sub["name_key"], sub["pcode"]))
        # fold in every alias whose pcode is an LGA in this state
        for ak, pc in alias_key_to_pc.items():
            if pc in set(sub["pcode"]):
                km.setdefault(ak, pc)
        lga_key_by_state[spc] = km
        lga_names_by_state[spc] = dict(zip(sub["pcode"], sub["name"]))

    state_cache: dict[str, str | None] = {}
    lga_cache: dict[tuple[str, str], str | None] = {}

    def state_pc(name: str) -> str | None:
        if name not in state_cache:
            k = name_key(name)
            pc = state_key.get(k)
            if pc is None and state_names:
                hit = process.extractOne(norm_name(name), state_names,
                                         scorer=fuzz.token_set_ratio)
                pc = hit[2] if hit and hit[1] >= 90 else None
            state_cache[name] = pc
        return state_cache[name]

    def lga_pc(state_pcode: str | None, name: str) -> str | None:
        if state_pcode is None:
            return None
        ck = (state_pcode, name)
        if ck not in lga_cache:
            k = name_key(name)
            pc = lga_key_by_state.get(state_pcode, {}).get(k)
            if pc is None:
                choices = lga_names_by_state.get(state_pcode, {})
                hit = process.extractOne(norm_name(name), choices,
                                         scorer=fuzz.token_set_ratio) if choices else None
                pc = hit[2] if hit and hit[1] >= 88 else None
            lga_cache[ck] = pc
        return lga_cache[ck]

    # first pass — attach lga_pcode to every ward row
    recs = []
    unmatched_lga: set[tuple[str, str]] = set()
    for _, gr in g.iterrows():
        spc = state_pc(str(gr["state"]))
        lpc = lga_pc(spc, str(gr["lga"])) if spc else None
        if lpc is None:
            unmatched_lga.add((str(gr["state"]), str(gr["lga"])))
        recs.append((lpc, spc, str(gr["ward"]).strip(),
                     str(gr.get("ward_alt_names") or ""), gr.get("area_sqkm"),
                     gr["_rep"], gr["geometry"]))

    # second pass — mint pcodes, sequence within LGA by normalised ward name
    from collections import defaultdict

    by_lga: dict[str | None, list] = defaultdict(list)
    for rec in recs:
        by_lga[rec[0]].append(rec)

    drop = units["level"] == 3
    kept = units[~drop].to_dict("records")
    alias_rows = aliases[aliases["pcode"].isin(units.loc[~drop, "pcode"])].to_dict("records")
    n_wards = 0
    ward_geoms: list[tuple[str, object]] = []

    for lpc, group in by_lga.items():
        group.sort(key=lambda r: norm_name(r[2]))
        for i, (_, spc, wname, alt, area, rep, geom) in enumerate(group, start=1):
            wpc = f"{lpc}{i:03d}" if lpc else f"NGxxx_{n_wards:05d}"
            n_wards += 1
            ward_geoms.append((wpc, geom))
            kept.append({
                "pcode": wpc, "level": 3, "level_name": "ward",
                "name": norm_name(wname), "name_official": wname,
                "name_key": name_key(wname), "parent_pcode": lpc,
                "adm1_pcode": spc, "adm2_pcode": lpc,
                "senatorial_pcode": None, "senatorial_name": None,
                "area_sqkm": float(area) if pd.notna(area) else None,
                "center_lon": rep.x, "center_lat": rep.y,
                "valid_from": None, "valid_to": None,
                "source": "grid3_wards", "source_version": "v3.0",
            })
            for a in [wname] + [x.strip() for x in alt.split(",") if x.strip()]:
                k = name_key(a)
                if k:
                    alias_rows.append({
                        "pcode": wpc, "alias": a, "alias_key": k,
                        "alias_type": "official" if a == wname else "altname",
                        "source": "grid3_wards",
                    })

    # canonical ward geometry, keyed to the minted pcode (GeoParquet)
    gpc = gpd.GeoDataFrame(
        {"pcode": [p for p, _ in ward_geoms]},
        geometry=[geom for _, geom in ward_geoms],
        crs=4326,
    )
    gpc.to_parquet(config.WARD_GEOM_PARQUET)

    note = f"wards: {n_wards} from grid3 v3.0"
    if unmatched_lga:
        note += f"  ({len(unmatched_lga)} distinct LGA names did not resolve — see build report)"
    return (
        pd.DataFrame(kept, columns=_UNIT_COLS),
        pd.DataFrame(alias_rows),
        note,
        sorted(f"{s} / {l}" for s, l in unmatched_lga),
    )


# ─────────────────────────── assemble + write ───────────────────────────
def _source_meta() -> pd.DataFrame:
    rows = []
    for mf in config.RAW.rglob("*._manifest.json"):
        rows.append(json.loads(mf.read_text()))
    if not rows:
        return pd.DataFrame(columns=["key", "title", "url", "licence", "provider",
                                     "bytes", "sha256", "retrieved_at"])
    df = pd.DataFrame(rows)
    return df[["key", "title", "url", "licence", "provider", "bytes", "sha256",
               "retrieved_at"]]


def build() -> dict:
    units, aliases = _build_ocha()
    aliases, n_manual = _apply_manual_aliases(units, aliases)
    units, aliases, ward_note, unmatched_lga = _merge_wards(units, aliases)

    # dedupe aliases, drop rows whose key equals the unit's own name_key already
    aliases = aliases.drop_duplicates(subset=["pcode", "alias_key"]).reset_index(drop=True)

    meta = _source_meta()

    config.SPINE.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(config.DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS geo_unit")
    con.execute("DROP TABLE IF EXISTS geo_alias")
    con.execute("DROP TABLE IF EXISTS geo_source_meta")
    con.register("u_df", units)
    con.register("a_df", aliases)
    con.register("m_df", meta)
    con.execute("CREATE TABLE geo_unit AS SELECT * FROM u_df")
    con.execute("CREATE TABLE geo_alias AS SELECT * FROM a_df")
    con.execute("CREATE TABLE geo_source_meta AS SELECT * FROM m_df")
    con.execute("CREATE UNIQUE INDEX ux_unit_pcode ON geo_unit(pcode)")
    con.execute("CREATE INDEX ix_unit_key ON geo_unit(level, name_key)")
    con.execute("CREATE INDEX ix_alias_key ON geo_alias(alias_key)")
    con.close()

    units.to_parquet(config.UNIT_PARQUET, index=False)
    aliases.to_parquet(config.ALIAS_PARQUET, index=False)
    meta.to_parquet(config.SOURCE_META_PARQUET, index=False)

    counts = units["level_name"].value_counts().to_dict()
    return {
        "counts": {k: int(counts.get(k, 0)) for k in config.LEVELS.values()},
        "aliases": int(len(aliases)),
        "manual_aliases_applied": n_manual,
        "ward_note": ward_note,
        "unmatched_lga_names": unmatched_lga,
        "sources": meta["key"].tolist() if len(meta) else [],
        "duckdb": str(config.DUCKDB_PATH),
    }
