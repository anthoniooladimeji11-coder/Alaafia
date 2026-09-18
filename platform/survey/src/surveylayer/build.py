"""Assemble the raw DHS API pull into the canonical survey table.

    raw JSON  ->  tidy long rows  ->  resolve geography to spine pcodes
              ->  survey_indicator.parquet  (+ series dict, source meta, duckdb)

Every row keeps its source and retrieval date. Geography that doesn't
resolve is kept with a null pcode and flagged, never dropped.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb
import pandas as pd
from rapidfuzz import fuzz, process

from . import dhs_api
from .config import (
    CROSSWALK_DHS_PARQUET, DHS_ZONES, DUCKDB, GEO_UNIT_PARQUET,
    INDICATOR_PARQUET, SERIES_PARQUET, SOURCE_META_PARQUET,
)
from .indicators import IDS, META


def _num(x):
    if x is None or x == "" or (isinstance(x, str) and not x.strip()):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


_ZONE_FIX = {
    "northeast": "North East", "northwest": "North West",
    "southeast": "South East", "southwest": "South West",
    "northcentral": "North Central", "north-central": "North Central",
    "south-south": "South South",
}


def _clean_label(s: str) -> str:
    s = str(s).lstrip(". ").strip()
    s = s.split(" - ")[0].strip()                     # "Northeast - 1990" -> "Northeast"
    key = s.lower().replace(" ", "")
    return _ZONE_FIX.get(key, s)


# ---------------------------------------------------------- geo resolver --
class _GeoResolver:
    """DHS subnational label -> spine pcode, via the committed crosswalk."""

    def __init__(self) -> None:
        cw = pd.read_parquet(CROSSWALK_DHS_PARQUET)
        self.state = {r.dhs_label.lower(): r.pcode
                      for r in cw[cw.dhs_scheme == "sstate"].itertuples()}
        self.zone = {r.dhs_label.lower(): r.pcode
                     for r in cw[cw.dhs_scheme == "v024"].itertuples()}
        units = pd.read_parquet(GEO_UNIT_PARQUET, columns=["pcode", "name", "level"])
        self._state_names = {r["name"].lower(): r.pcode
                             for _, r in units[units.level == 1].iterrows()}
        self.misses: dict[str, int] = {}

    def resolve(self, raw_label: str, category: str) -> tuple[str | None, str, str]:
        label = _clean_label(raw_label)
        low = label.lower()
        if category == "Total" or low in ("nigeria", "total", ""):
            return "NG", "national", "Nigeria"
        if label in DHS_ZONES or low in self.zone:
            return self.zone.get(low), "zone", label
        if low in self.state:
            return self.state[low], "state", label
        if low in self._state_names:
            return self._state_names[low], "state", label
        # fuzzy last resort against canonical state names
        hit = process.extractOne(low, self._state_names.keys(),
                                 scorer=fuzz.token_set_ratio)
        if hit and hit[1] >= 90:
            return self._state_names[hit[0]], "state", label
        self.misses[label] = self.misses.get(label, 0) + 1
        return None, "state", label


# ------------------------------------------------------------------ build --
def build(*, force_fetch: bool = False) -> dict:
    raw_path = dhs_api.fetch_data(IDS, force=force_fetch)
    rows = json.loads(raw_path.read_text())
    man = json.loads((raw_path.with_name(raw_path.stem + "._manifest.json")).read_text())

    geo = _GeoResolver()
    ind_labels = {i["IndicatorId"]: i["Label"] for i in dhs_api.indicators(IDS)}

    recs = []
    for r in rows:
        # geography rows only ("Region" = subnational, "Total" = national);
        # drop Age / vaccination-source / wealth splits.
        if r.get("CharacteristicCategory") not in ("Region", "Total"):
            continue
        # DHS flags the canonical reference period / definition per cell.
        if int(r.get("IsPreferred", 0) or 0) != 1:
            continue
        iid = r["IndicatorId"]
        if iid not in META:
            continue
        pcode, level, gname = geo.resolve(r.get("CharacteristicLabel", ""),
                                          r.get("CharacteristicCategory", ""))
        m = META[iid]
        recs.append({
            "indicator_id": iid,
            "slug": m["slug"],
            "domain": m["domain"],
            "unit": m["unit"],
            "populace": m["populace"],
            "indicator_label": ind_labels.get(iid, r.get("Indicator", "")),
            "survey_id": r["SurveyId"],
            "survey_type": r.get("SurveyType", ""),
            "survey_year": int(r["SurveyYear"]),
            "geo_level": level,
            "geo_pcode": pcode,
            "geo_name": gname,
            "geo_unresolved": pcode is None,
            "value": _num(r.get("Value")),
            "ci_low": _num(r.get("CILow")),
            "ci_high": _num(r.get("CIHigh")),
            "denom_unweighted": _num(r.get("DenominatorUnweighted")),
            "denom_weighted": _num(r.get("DenominatorWeighted")),
            "is_preferred": int(r.get("IsPreferred", 0) or 0),
            "source": "DHS API",
            "retrieved_at": man["retrieved_at"],
        })

    df = pd.DataFrame.from_records(recs)
    # one row per (indicator, survey, geography): prefer IsPreferred, then first
    df = (df.sort_values("is_preferred", ascending=False)
            .drop_duplicates(["indicator_id", "survey_id", "geo_pcode", "geo_name"])
            .sort_values(["domain", "slug", "survey_year", "geo_level", "geo_name"])
            .reset_index(drop=True))
    df.to_parquet(INDICATOR_PARQUET, index=False)

    # indicator dictionary
    g = df.groupby(["indicator_id", "slug", "domain", "unit", "populace",
                    "indicator_label"], as_index=False)
    series = g.agg(
        n_rows=("value", "size"),
        n_surveys=("survey_id", "nunique"),
        first_year=("survey_year", "min"),
        last_year=("survey_year", "max"),
        n_state_obs=("geo_level", lambda s: int((s == "state").sum())),
    )
    series.to_parquet(SERIES_PARQUET, index=False)

    pd.DataFrame([{
        "key": "dhs_api",
        "title": "DHS Program API (StatCompiler) — Nigeria",
        "url": "https://api.dhsprogram.com/rest/dhs/data",
        "licence": "DHS Program Terms of Use — https://dhsprogram.com/Data/terms-of-use.cfm",
        "provider": "The DHS Program, ICF",
        "rows": man["rows"],
        "sha256": man["sha256"],
        "retrieved_at": man["retrieved_at"],
    }]).to_parquet(SOURCE_META_PARQUET, index=False)

    con = duckdb.connect(str(DUCKDB))
    con.execute("CREATE OR REPLACE VIEW survey_indicator AS "
                f"SELECT * FROM read_parquet('{INDICATOR_PARQUET}')")
    con.execute("CREATE OR REPLACE VIEW survey_series AS "
                f"SELECT * FROM read_parquet('{SERIES_PARQUET}')")
    con.close()

    return {
        "rows": len(df),
        "indicators": df["indicator_id"].nunique(),
        "surveys": sorted(df["survey_id"].unique().tolist()),
        "state_rows": int((df["geo_level"] == "state").sum()),
        "unresolved": geo.misses,
    }
