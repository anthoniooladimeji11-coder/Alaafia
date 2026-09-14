"""Thin client for the DHS program API (StatCompiler).

Docs: https://api.dhsprogram.com/  — public, no key. We only touch three
endpoints: /surveys, /indicators, /data. Raw JSON pages are cached under
data/raw/dhs_api/ with a manifest so a rebuild never re-hits the network.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .config import DHS_API, DHS_COUNTRY, DHS_PAUSE_S, DHS_PERPAGE, RAW

CACHE = RAW / "dhs_api"
CACHE.mkdir(parents=True, exist_ok=True)

_client = httpx.Client(timeout=60, headers={"User-Agent": "alaafia-surveylayer/0.1"})


def _get(path: str, params: dict) -> dict:
    for attempt in range(4):
        r = _client.get(f"{DHS_API}/{path}", params=params)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(1.5 * (attempt + 1))
            continue
        r.raise_for_status()
    raise RuntimeError(f"DHS API {path} failed after retries: {r.status_code}")


def _paged(path: str, params: dict) -> list[dict]:
    params = {**params, "f": "json", "perpage": DHS_PERPAGE, "page": 1}
    first = _get(path, params)
    rows = list(first.get("Data", []))
    total = int(first.get("TotalPages", 1) or 1)
    for page in range(2, total + 1):
        time.sleep(DHS_PAUSE_S)
        rows += _get(path, {**params, "page": page}).get("Data", [])
    return rows


# ---------------------------------------------------------------- public --
def surveys(country: str = DHS_COUNTRY) -> list[dict]:
    return _paged("surveys", {"countryIds": country})


def indicators(ids: list[str]) -> list[dict]:
    return _paged("indicators", {"indicatorIds": ",".join(ids)})


def fetch_data(indicator_ids: list[str], country: str = DHS_COUNTRY,
               *, force: bool = False) -> Path:
    """Pull /data for the indicator set at national + subnational breakdown.

    One cache file per (country, indicator-set hash). Returns its path.
    """
    key = hashlib.sha1((country + "|" + ",".join(sorted(indicator_ids))).encode()).hexdigest()[:12]
    out = CACHE / f"data_{country}_{key}.json"
    man = CACHE / f"data_{country}_{key}._manifest.json"
    if out.exists() and not force:
        return out

    rows: list[dict] = []
    # the API caps indicatorIds per call; chunk to be safe
    for i in range(0, len(indicator_ids), 12):
        chunk = indicator_ids[i:i + 12]
        for breakdown in ("national", "subnational"):
            time.sleep(DHS_PAUSE_S)
            rows += _paged("data", {
                "countryIds": country,
                "indicatorIds": ",".join(chunk),
                "breakdown": breakdown,
            })

    out.write_text(json.dumps(rows))
    man.write_text(json.dumps({
        "endpoint": "data",
        "country": country,
        "indicator_ids": indicator_ids,
        "rows": len(rows),
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    }, indent=2))
    return out
