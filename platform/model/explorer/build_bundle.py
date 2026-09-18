"""Build the compact data bundle for the Àlááfìa estimates explorer.

    python explorer/build_bundle.py

Reads the committed model + survey + geo outputs, simplifies geometry
with mapshaper (via npx, same recipe as platform/geo/explorer), and
writes explorer/build/index.html — the page to publish.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import geopandas as gpd
import pandas as pd

MODEL = Path(__file__).resolve().parent.parent
GEO = MODEL.parent / "geo"
SHP_ZIP = GEO / "data" / "raw" / "ocha_cod" / "nga_admin_boundaries.shp.zip"
OUT = Path(__file__).resolve().parent / "build"
OUT.mkdir(exist_ok=True)

# "does high mean good or bad" is decided once, by the model package
# itself (sae/direction.py), and written to indicator_meta.parquet by
# `sae build` — read it from there rather than keeping a second,
# driftable copy of the classification here.
INDICATOR_META = MODEL / "data" / "model" / "indicator_meta.parquet"


def _mapshaper(args: list[str]) -> None:
    subprocess.run(["npx", "-y", "mapshaper@0.6.102", *args], check=True, cwd=OUT)


def build_geometry() -> None:
    gdf = gpd.read_file(f"/vsizip/{SHP_ZIP}/nga_admin2.shp")[
        ["adm1_pcode", "adm2_pcode", "adm2_name", "adm1_name", "geometry"]
    ].rename(columns={"adm1_pcode": "s", "adm2_pcode": "l", "adm2_name": "ln", "adm1_name": "sn"})
    raw = OUT / "lga_raw.geojson"
    gdf.to_file(raw, driver="GeoJSON")
    _mapshaper(["lga_raw.geojson", "-simplify", "6%", "keep-shapes", "planar",
               "-o", "lga.topo.json", "format=topojson", "drop-table", "id-field=l"])
    _mapshaper(["lga_raw.geojson", "-dissolve2", "fields=s", "copy-fields=sn",
               "-simplify", "4%", "keep-shapes", "planar",
               "-o", "state.topo.json", "format=topojson", "id-field=s"])
    raw.unlink()


def build() -> dict:
    if not INDICATOR_META.exists():
        raise SystemExit(f"missing {INDICATOR_META} — run `sae build --survey ...` first "
                         f"(platform/model), which now writes this alongside fh_state.parquet")
    ind = pd.read_parquet(INDICATOR_META)
    fh = pd.read_parquet(MODEL / "data" / "model" / "fh_state.parquet")
    lga_est = pd.read_parquet(MODEL / "data" / "model" / "sae_lga.parquet")
    unit = pd.read_parquet(GEO / "data" / "spine" / "geo_unit.parquet")

    built_slugs = set(fh.slug.unique())
    indicators = [
        {"slug": r.slug, "domain": r.domain, "unit": r.unit, "label": r.indicator_label,
         "worse_high": bool(r.worse_high), "n_surveys": int(r.n_surveys),
         "years": f"{int(r.first_year)}-{int(r.last_year)}"}
        for r in ind.sort_values(["domain", "slug"]).itertuples()
    ]

    states = unit[unit.level == 1][["pcode", "name", "center_lon", "center_lat"]]
    lgas_u = unit[unit.level == 2][["pcode", "name", "adm1_pcode", "center_lon", "center_lat"]]

    fh = fh[fh.slug.isin(built_slugs)]
    est_state = {
        "slug": fh.slug.tolist(), "p": fh.state_pcode.tolist(),
        "direct": [round(float(v), 2) for v in fh.direct],
        "fh": [round(float(v), 2) for v in fh.fh_estimate],
        "se": [round(float(v), 3) for v in fh.fh_se],
        "lo": [round(float(v), 2) for v in fh.fh_ci_low],
        "hi": [round(float(v), 2) for v in fh.fh_ci_high],
        "gamma": [round(float(v), 3) for v in fh.gamma],
        "psi": fh.psi_method.tolist(),
    }
    est_lga = {
        "slug": lga_est.slug.tolist(), "p": lga_est.lga_pcode.tolist(),
        "est": [round(float(v), 2) for v in lga_est.estimate],
        "se": [round(float(v), 3) for v in lga_est.se_floor],
        "lo": [round(float(v), 2) for v in lga_est.ci_low],
        "hi": [round(float(v), 2) for v in lga_est.ci_high],
    }

    bundle = {
        "built": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d"),
        "survey_id": sorted(fh.survey_id.unique().tolist()),
        "indicators": indicators,
        "states": [{"p": r.pcode, "n": r.name, "lon": round(float(r.center_lon), 4),
                   "lat": round(float(r.center_lat), 4)} for r in states.itertuples()],
        "lgas": [{"p": r.pcode, "n": r.name, "s": r.adm1_pcode,
                 "lon": round(float(r.center_lon), 4), "lat": round(float(r.center_lat), 4)}
                for r in lgas_u.itertuples()],
        "est_state": est_state,
        "est_lga": est_lga,
    }
    return bundle


def main() -> None:
    print("· geometry (mapshaper)…")
    build_geometry()
    print("· tables…")
    bundle = build()
    bundle["geometry"] = {
        "states": json.loads((OUT / "state.topo.json").read_text()),
        "lgas": json.loads((OUT / "lga.topo.json").read_text()),
    }
    payload = json.dumps(bundle, separators=(",", ":"))
    tpl = (Path(__file__).resolve().parent / "template.html").read_text()
    if "__BUNDLE__" not in tpl:
        raise SystemExit("template.html is missing the __BUNDLE__ marker")
    page = OUT / "index.html"
    page.write_text(tpl.replace("__BUNDLE__", payload))
    print(f"\n  {page}  {page.stat().st_size/1e6:.2f} MB  (publish this)")
    print(f"  {len(bundle['indicators'])} indicators · "
          f"{len(bundle['est_state']['p'])} state rows · {len(bundle['est_lga']['p'])} LGA rows")


if __name__ == "__main__":
    main()
