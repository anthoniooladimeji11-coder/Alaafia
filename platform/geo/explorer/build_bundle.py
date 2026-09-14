"""Build the compact data bundle for the Àlááfìa geography-spine explorer.

Reads the committed spine outputs (data/spine/*.parquet) plus the raw OCHA
admin-boundary shapefile, and emits one JSON file the static explorer page
inlines. Geometry is simplified + quantised with mapshaper (via npx).

    python explorer/build_bundle.py

Outputs:
    explorer/build/spine_bundle.json   -- everything the page needs
    explorer/build/state.topo.json     -- intermediate (dissolved states)
    explorer/build/lga.topo.json       -- intermediate (LGAs)
"""

from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

GEO = Path(__file__).resolve().parent.parent
SPINE = GEO / "data" / "spine"
RAW = GEO / "data" / "raw"
OUT = Path(__file__).resolve().parent / "build"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- geometry ----
SHP_ZIP = RAW / "ocha_cod" / "nga_admin_boundaries.shp.zip"


def _mapshaper(args: list[str]) -> None:
    subprocess.run(["npx", "-y", "mapshaper@0.6.102", *args], check=True, cwd=OUT)


def build_geometry() -> None:
    """LGA polygons -> simplified TopoJSON; dissolve -> state TopoJSON."""
    gdf = gpd.read_file(f"/vsizip/{SHP_ZIP}/nga_admin2.shp")[
        ["adm1_pcode", "adm2_pcode", "adm2_name", "adm1_name", "geometry"]
    ].rename(columns={"adm1_pcode": "s", "adm2_pcode": "l", "adm2_name": "ln", "adm1_name": "sn"})
    raw = OUT / "lga_raw.geojson"
    gdf.to_file(raw, driver="GeoJSON")

    # LGAs: keep-shapes stops small islands collapsing; 6% visvalingam is plenty
    # at the zoom levels the page allows.
    _mapshaper([
        "lga_raw.geojson", "-simplify", "6%", "keep-shapes", "planar",
        "-o", "lga.topo.json", "format=topojson", "drop-table", "id-field=l",
    ])
    # States: dissolve LGA arcs so borders stay perfectly coincident, then a
    # gentler simplify for the outer coastline.
    _mapshaper([
        "lga_raw.geojson", "-dissolve2", "fields=s", "copy-fields=sn",
        "-simplify", "4%", "keep-shapes", "planar",
        "-o", "state.topo.json", "format=topojson", "id-field=s",
    ])
    raw.unlink()


# ------------------------------------------------------------------ tables ----
FAC_TYPE_GROUPS = {
    "Primary Health Center": "phc", "Primary Health Clinic": "phc",
    "Health Post": "post", "Health Center": "phc", "Clinic": "clinic",
    "Maternity Home": "maternity", "Hospital": "hospital",
    "General Hospital": "hospital", "Cottage Hospital": "hospital",
    "Specialist Hospital": "hospital", "Teaching/Tertiary Hospital": "hospital",
    "Federal Medical Center": "hospital", "Medical Center": "clinic",
}


def _grp(t: str) -> str:
    return FAC_TYPE_GROUPS.get(str(t).strip(), "other")


def build_tables() -> dict:
    unit = pd.read_parquet(SPINE / "geo_unit.parquet")
    fac = pd.read_parquet(SPINE / "geo_facility.parquet")
    meta = pd.read_parquet(SPINE / "geo_source_meta.parquet")
    settl = pd.read_parquet(SPINE / "geo_settlement.parquet", columns=["state_pcode", "lga_pcode"])

    states = unit[unit.level == 1]
    lgas = unit[unit.level == 2]
    wards = unit[unit.level == 3]

    # A settlement resolved to a ward implicitly has that ward's LGA/state;
    # the flat lga_pcode/state_pcode columns only hold the *shallowest* hit,
    # so backfill from ward_pcode (<lga(8)><ward(3)>) before counting.
    settl_full = pd.read_parquet(
        SPINE / "geo_settlement.parquet", columns=["state_pcode", "lga_pcode", "ward_pcode"]
    )
    s_lga = settl_full.lga_pcode.fillna(settl_full.ward_pcode.str[:8])
    s_state = settl_full.state_pcode.fillna(s_lga.str[:5])

    w_by_state = wards.groupby("adm1_pcode").size()
    w_by_lga = wards.groupby("parent_pcode").size()
    f_by_state = fac.groupby("state_pcode").size()
    f_by_lga = fac.groupby("lga_pcode").size()
    fm_by_state = fac[fac.lon.notna()].groupby("state_pcode").size()
    s_by_state = s_state.value_counts()
    s_by_lga = s_lga.value_counts()

    state_rows = []
    for _, r in states.sort_values("name").iterrows():
        p = r.pcode
        state_rows.append({
            "p": p, "n": r["name"],
            "lon": round(float(r.center_lon), 4), "lat": round(float(r.center_lat), 4),
            "km2": round(float(r.area_sqkm)),
            "lga": int((lgas.adm1_pcode == p).sum()),
            "ward": int(w_by_state.get(p, 0)),
            "fac": int(f_by_state.get(p, 0)),
            "facm": int(fm_by_state.get(p, 0)),
            "set": int(s_by_state.get(p, 0)),
        })

    lga_rows = []
    for _, r in lgas.sort_values(["adm1_pcode", "name"]).iterrows():
        p = r.pcode
        lga_rows.append({
            "p": p, "n": r["name"], "s": r.adm1_pcode,
            "lon": round(float(r.center_lon), 4), "lat": round(float(r.center_lat), 4),
            "km2": round(float(r.area_sqkm)),
            "ward": int(w_by_lga.get(p, 0)),
            "fac": int(f_by_lga.get(p, 0)),
            "set": int(s_by_lga.get(p, 0)),
        })

    # wards: centroid + parent only (no polygons in the bundle)
    ward_rows = []
    for _, r in wards.sort_values("parent_pcode").iterrows():
        ward_rows.append([
            r.pcode, r["name"], r.parent_pcode,
            round(float(r.center_lon), 4), round(float(r.center_lat), 4),
        ])

    # facilities: mapped points only, packed as parallel arrays
    fm = fac[fac.lon.notna() & fac.lat.notna()].copy()
    fm["g"] = fm["type"].map(_grp)
    gcodes = ["phc", "clinic", "post", "maternity", "hospital", "other"]
    lvl = {"Primary": 0, "Secondary": 1, "Tertiary": 2}
    facilities = {
        "codes": gcodes,
        "lon": [round(float(x), 4) for x in fm.lon],
        "lat": [round(float(x), 4) for x in fm.lat],
        "g": [gcodes.index(x) for x in fm.g],
        "lv": [int(lvl.get(str(x), 3)) for x in fm.level],
        "pub": [1 if str(x) == "Public" else 0 for x in fm.ownership],
        "fn": [1 if str(x) == "Functional" else 0 for x in fm.functional],
        "lga": list(fm.lga_pcode),
    }

    src = [
        {"title": r.title, "url": r.url, "licence": r.licence,
         "provider": r.provider, "retrieved": str(r.retrieved_at)}
        for _, r in meta.iterrows()
    ]

    no_ward = [row["n"] for row in state_rows if row["ward"] == 0]
    return {
        "built": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d"),
        "totals": {
            "states": len(state_rows), "lgas": len(lga_rows),
            "wards": len(ward_rows), "settlements": int(len(settl)),
            "facilities": int(len(fac)), "facilities_mapped": int(len(fm)),
            "ward_states": int((w_by_state > 0).sum()),
            "ward_lgas": int(w_by_lga.shape[0]),
            "fac_states": int((f_by_state > 0).sum()),
        },
        "no_ward_states": no_ward,
        "sources": src,
        "states": state_rows,
        "lgas": lga_rows,
        "wards": ward_rows,
        "facilities": facilities,
    }


def main() -> None:
    print("· geometry (mapshaper)…")
    build_geometry()
    print("· tables…")
    bundle = build_tables()
    bundle["geometry"] = {
        "states": json.loads((OUT / "state.topo.json").read_text()),
        "lgas": json.loads((OUT / "lga.topo.json").read_text()),
    }
    out = OUT / "spine_bundle.json"
    payload = json.dumps(bundle, separators=(",", ":"))
    out.write_text(payload)
    mb = out.stat().st_size / 1e6

    # assemble the publishable page: template + inlined bundle
    tpl = (Path(__file__).resolve().parent / "template.html").read_text()
    if "__BUNDLE__" not in tpl:
        raise SystemExit("template.html is missing the __BUNDLE__ marker")
    page = OUT / "index.html"
    page.write_text(tpl.replace("__BUNDLE__", payload))
    print(f"  {page}  {page.stat().st_size/1e6:.2f} MB  (publish this)")
    t = bundle["totals"]
    print(f"\n  {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}  {mb:.2f} MB")
    print(f"  states={t['states']} lgas={t['lgas']} wards={t['wards']} "
          f"({t['ward_states']} states) facilities={t['facilities']} "
          f"({t['facilities_mapped']} mapped, {t['fac_states']} states) "
          f"settlements={t['settlements']:,}")
    print(f"  no ward layer: {', '.join(bundle['no_ward_states'])}")


if __name__ == "__main__":
    main()
