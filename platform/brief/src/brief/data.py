"""Assemble one state's profile: every modelled indicator against its
national figure, ranked among the other 36 states, grouped by domain.

Every number here traces to a specific source row — nothing here is
invented or smoothed beyond what platform/model already computed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .config import COV_LGA, FH_STATE, GEO_UNIT, INDICATOR_META, N_HEADLINE, SURVEY_INDICATOR

DOMAIN_LABEL = {
    "nutrition": "Nutrition", "anaemia": "Anaemia", "immunisation": "Immunisation",
    "child_health": "Child health", "mortality": "Child mortality", "maternal": "Maternal health",
    "family_plan": "Family planning", "malaria": "Malaria", "wash": "Water & sanitation",
    "education": "Education", "living_std": "Living standards",
}


@dataclass
class Row:
    slug: str
    label: str
    domain: str
    unit: str
    worse_high: bool
    value: float
    ci_low: float
    ci_high: float
    se: float
    gamma: float
    psi_method: str
    national: float | None
    delta: float | None          # value - national, signed
    rank: int | None             # 1 = best of the 37 (direction-aware)
    n_ranked: int


@dataclass
class Profile:
    state_pcode: str
    state_name: str
    area_km2: float
    population: float
    survey_id: str
    built: str
    rows: list[Row]
    by_domain: dict[str, list[Row]] = field(default_factory=dict)
    concerns: list[Row] = field(default_factory=list)     # furthest-worse-than-national
    strengths: list[Row] = field(default_factory=list)    # furthest-better-than-national
    sources: list[dict] = field(default_factory=list)


def _fmt_unit(unit: str) -> str:
    return "per 1,000" if unit == "rate_1000" else "%"


def list_states() -> pd.DataFrame:
    unit = pd.read_parquet(GEO_UNIT, columns=["pcode", "name", "level"])
    return unit[unit.level == 1][["pcode", "name"]].sort_values("name").reset_index(drop=True)


def build_profile(state_pcode: str, survey_id: str | None = None) -> Profile:
    st = pd.read_parquet(FH_STATE)
    if survey_id is None:
        survey_id = st.survey_id.value_counts().idxmax()
    st = st[st.survey_id == survey_id]

    meta = pd.read_parquet(INDICATOR_META).set_index("slug")
    natl = (pd.read_parquet(SURVEY_INDICATOR,
                            columns=["slug", "survey_id", "geo_level", "value"])
           .pipe(lambda d: d[(d.survey_id == survey_id) & (d.geo_level == "national")])
           .set_index("slug").value)

    unit_t = pd.read_parquet(GEO_UNIT, columns=["pcode", "name", "level", "area_sqkm"])
    srow = unit_t[(unit_t.level == 1) & (unit_t.pcode == state_pcode)]
    if srow.empty:
        raise ValueError(f"unknown state pcode {state_pcode!r}")
    state_name, area_km2 = srow.iloc[0]["name"], float(srow.iloc[0].area_sqkm)

    cov = pd.read_parquet(COV_LGA, columns=["state_pcode", "pop_2020"])
    population = float(cov[cov.state_pcode == state_pcode].pop_2020.sum())

    rows: list[Row] = []
    for slug, g in st.groupby("slug"):
        if slug not in meta.index:
            continue
        m = meta.loc[slug]
        worse_high = bool(m.worse_high)
        # rank every state that has a fitted value for this indicator/round;
        # 1 = best (lowest for worse_high, highest for better_high)
        ranked = g.sort_values("fh_estimate", ascending=worse_high).reset_index(drop=True)
        mine = g[g.state_pcode == state_pcode]
        if mine.empty:
            continue
        r = mine.iloc[0]
        rank = int(ranked.index[ranked.state_pcode == state_pcode][0]) + 1
        nat = float(natl.get(slug)) if slug in natl.index else None
        delta = (float(r.fh_estimate) - nat) if nat is not None else None
        rows.append(Row(
            slug=slug, label=m.indicator_label, domain=m.domain, unit=m.unit,
            worse_high=worse_high, value=float(r.fh_estimate), ci_low=float(r.fh_ci_low),
            ci_high=float(r.fh_ci_high), se=float(r.fh_se), gamma=float(r.gamma),
            psi_method=r.psi_method, national=nat, delta=delta, rank=rank, n_ranked=len(ranked),
        ))

    rows.sort(key=lambda r: (r.domain, r.slug))
    by_domain: dict[str, list[Row]] = {}
    for r in rows:
        by_domain.setdefault(r.domain, []).append(r)

    # "concern" = delta signed so a bigger number is always worse, regardless
    # of the indicator's own direction; same trick in reverse for "strength".
    scored = [(r, r.delta if r.worse_high else -r.delta) for r in rows if r.delta is not None]
    concerns = [r for r, s in sorted(scored, key=lambda t: -t[1])[:N_HEADLINE] if s > 0]
    strengths = [r for r, s in sorted(scored, key=lambda t: t[1])[:N_HEADLINE] if s < 0]

    sources = _sources()

    return Profile(state_pcode=state_pcode, state_name=state_name, area_km2=area_km2,
                   population=population, survey_id=survey_id,
                   built=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d"),
                   rows=rows, by_domain=by_domain, concerns=concerns, strengths=strengths,
                   sources=sources)


def _sources() -> list[dict]:
    from .config import SURVEY_SOURCE_META
    out = []
    try:
        d = pd.read_parquet(SURVEY_SOURCE_META)
        out += d.to_dict("records")
    except FileNotFoundError:
        pass
    out.append({
        "title": "Fay–Herriot small-area estimation, state -> LGA",
        "provider": "Àlááfìa", "licence": "internal method — see platform/model/README.md",
    })
    return out
