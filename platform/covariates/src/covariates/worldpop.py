"""Tier B — WorldPop population as an LGA covariate (zonal statistics).

Needs the `raster` extra:  uv sync --extra raster   (pulls rasterio + exactextract)

    covariates worldpop fetch      # download the 1km rasters -> data/raw/worldpop/
    covariates worldpop zonal      # sum/mean per LGA, merge into covariates_lga.parquet

Adds: pop_2020, pop_density_km2, pop_u5_2020, pop_wra_2020, pct_u5, pct_wra
(WRA = women of reproductive age, 15–49). Age-structure files are optional;
if only the total raster is present just the first two columns are added.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

from .config import LGA_PARQUET, OCHA_SHP_ZIP, OUT, RAW

WP_DIR = RAW / "worldpop"
WP_DIR.mkdir(parents=True, exist_ok=True)

# WorldPop, unconstrained, UN-adjusted, 1 km. If a URL 404s, check
# https://hub.worldpop.org/ for the current path and update here.
BASE = "https://data.worldpop.org/GIS"
_AGESEX = f"{BASE}/AgeSex_structures/Global_2000_2020_Constrained/2020/NGA/nga_{{sex}}_{{band}}_2020_constrained.tif"
RASTERS = {
    "pop_2020": f"{BASE}/Population/Global_2000_2020_1km_UNadj/2020/NGA/nga_ppp_2020_1km_Aggregated_UNadj.tif",
    # age–sex, 100m constrained (verified live 2026-09-14 via hub.worldpop.org/rest/data/age_structures/ascic_2020).
    # bands 0 and 1 = ages 0 and 1-4 -> together, under-5.
    "f_0_2020": _AGESEX.format(sex="f", band=0), "m_0_2020": _AGESEX.format(sex="m", band=0),
    "f_1_2020": _AGESEX.format(sex="f", band=1), "m_1_2020": _AGESEX.format(sex="m", band=1),
}


def fetch(*, only_total: bool = False, force: bool = False) -> list[Path]:
    got = []
    items = {"pop_2020": RASTERS["pop_2020"]} if only_total else RASTERS
    with httpx.Client(timeout=120, follow_redirects=True) as c:
        for key, url in items.items():
            dst = WP_DIR / Path(url).name
            if dst.exists() and not force:
                got.append(dst)
                continue
            with c.stream("GET", url) as r:
                if r.status_code != 200:
                    print(f"  skip {key}: HTTP {r.status_code} ({url})")
                    continue
                with open(dst, "wb") as fh:
                    for chunk in r.iter_bytes(1 << 20):
                        fh.write(chunk)
            (WP_DIR / (dst.name + "._manifest.json")).write_text(json.dumps({
                "url": url, "bytes": dst.stat().st_size,
                "sha256": hashlib.sha256(dst.read_bytes()).hexdigest(),
                "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }, indent=2))
            got.append(dst)
            print(f"  {key}: {dst.stat().st_size/1e6:.1f} MB")
    return got


def _lga_polygons():
    import geopandas as gpd
    return gpd.read_file(f"/vsizip/{OCHA_SHP_ZIP}/nga_admin2.shp")[["adm2_pcode", "geometry"]]


def zonal() -> dict:
    try:
        from exactextract import exact_extract
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Tier B needs the raster extra:  uv sync --extra raster") from e

    pop_tif = WP_DIR / Path(RASTERS["pop_2020"]).name
    if not pop_tif.exists():
        raise SystemExit("run `covariates worldpop fetch` first")

    polys = _lga_polygons().rename(columns={"adm2_pcode": "lga_pcode"})
    res = exact_extract(str(pop_tif), polys, ["sum"], include_cols=["lga_pcode"],
                        output="pandas")
    out = res.rename(columns={"sum": "pop_2020"})[["lga_pcode", "pop_2020"]]

    u5_bands = ["f_0_2020", "m_0_2020", "f_1_2020", "m_1_2020"]
    have = [b for b in u5_bands if (WP_DIR / Path(RASTERS[b]).name).exists()]
    for b in have:
        t = WP_DIR / Path(RASTERS[b]).name
        r = exact_extract(str(t), polys, ["sum"], include_cols=["lga_pcode"],
                          output="pandas").rename(columns={"sum": b})
        out = out.merge(r[["lga_pcode", b]], on="lga_pcode", how="left")
    if set(u5_bands).issubset(out.columns):
        out["pop_u5_2020"] = out[u5_bands].sum(axis=1)
        out = out.drop(columns=u5_bands)

    lga = pd.read_parquet(LGA_PARQUET)
    lga = lga.drop(columns=[c for c in out.columns if c != "lga_pcode" and c in lga.columns])
    lga = lga.merge(out, on="lga_pcode", how="left")
    lga["pop_density_km2"] = lga.pop_2020 / lga.area_km2
    if "pop_u5_2020" in lga.columns:
        lga["pct_u5"] = (lga.pop_u5_2020 / lga.pop_2020).clip(0, 1)
    lga.to_parquet(LGA_PARQUET, index=False)
    return {"lgas": len(lga), "added": [c for c in out.columns if c != "lga_pcode"]}
