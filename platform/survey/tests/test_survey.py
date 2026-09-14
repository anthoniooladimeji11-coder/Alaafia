"""Shape + integrity checks on the built survey layer."""

import pandas as pd

from surveylayer.config import GEO_UNIT_PARQUET
from surveylayer.indicators import IDS, META


def test_all_indicators_present(series):
    got = set(series.indicator_id)
    assert got.issubset(set(IDS))                     # no stray IDs
    assert len(got) >= 0.9 * len(IDS)                 # ≥90% of the curated set landed
    assert (series.n_rows > 0).all()


def test_unique_keys(indicators):
    dup = indicators.duplicated(["indicator_id", "survey_id", "geo_pcode", "geo_name"])
    assert not dup.any()


def test_national_rows_exist(indicators):
    natl = indicators[indicators.geo_level == "national"]
    assert natl.geo_pcode.eq("NG").all()
    assert natl.indicator_id.nunique() >= 20


def test_percentages_in_range(indicators):
    pct = indicators[indicators.unit.isin(["pct", "prev_pct"])]["value"].dropna()
    assert pct.between(0, 100).all()


def test_mortality_rates_plausible(indicators):
    mort = indicators[indicators.unit == "rate_1000"]["value"].dropna()
    assert mort.between(0, 400).all()


def test_state_geography_resolves_to_spine(indicators):
    units = pd.read_parquet(GEO_UNIT_PARQUET, columns=["pcode", "level"])
    state_pcodes = set(units[units.level == 1].pcode)
    got = indicators[indicators.geo_level == "state"]
    resolved = got[got.geo_pcode.notna()]
    # at least the 2013+ surveys give 37 states; expect near-total resolution
    assert resolved.geo_pcode.isin(state_pcodes).all()
    assert len(resolved) / len(got) > 0.98


def test_state_level_series_since_2013(indicators):
    st = indicators[(indicators.geo_level == "state") & indicators.geo_pcode.notna()]
    yrs = set(st.survey_year.unique())
    assert {2013, 2018}.issubset(yrs)
    # every state present in a recent round
    recent = st[st.survey_year >= 2018]
    assert recent.geo_pcode.nunique() >= 36


def test_domains_tagged(series):
    assert set(series.domain) == {META[i]["domain"] for i in IDS}
    assert series.domain.nunique() >= 8
