"""Profile assembly, checked against the model's own output — no invented
expectations, just internal consistency of what data.py derives from it."""

import pandas as pd
import pytest

from brief.config import FH_STATE
from brief.data import build_profile, list_states


def test_list_states_is_the_full_37():
    s = list_states()
    assert len(s) == 37
    assert s.pcode.is_unique
    assert "NG021" in s.pcode.values


def test_profile_basics(katsina):
    assert katsina.state_pcode == "NG021"
    assert katsina.state_name == "Katsina"
    assert katsina.population > 1_000_000          # Katsina is one of the larger states
    assert katsina.area_km2 > 0
    assert len(katsina.rows) == 25                  # every indicator the model fit


def test_rank_is_within_its_own_comparison_set(katsina):
    for r in katsina.rows:
        assert r.rank is not None
        assert 1 <= r.rank <= r.n_ranked <= 37


def test_delta_sign_matches_direct_subtraction(katsina):
    for r in katsina.rows:
        if r.national is None:
            continue
        assert r.delta == pytest.approx(r.value - r.national, abs=1e-6)


def test_concerns_are_all_actually_worse_than_national(katsina):
    for r in katsina.concerns:
        bad = (r.delta > 0) == r.worse_high
        assert bad, f"{r.slug} is in `concerns` but isn't worse than national"


def test_strengths_are_all_actually_better_than_national(katsina):
    for r in katsina.strengths:
        good = (r.delta > 0) != r.worse_high
        assert good, f"{r.slug} is in `strengths` but isn't better than national"


def test_missing_national_is_dropped_not_faked(katsina):
    # women_literate has no national row in the NG2024DHS pull (a real API gap,
    # not a bug) -- confirm it surfaces as "no comparison", not a fabricated 0.
    lit = [r for r in katsina.rows if r.slug == "women_literate"]
    if lit:
        assert lit[0].national is None
        assert lit[0].delta is None
        assert lit[0].rank is not None              # rank alone doesn't need `national`


def test_by_domain_partitions_all_rows(katsina):
    total = sum(len(v) for v in katsina.by_domain.values())
    assert total == len(katsina.rows)


def test_thin_coverage_indicator_has_smaller_denominator(katsina):
    # diarrhoea_ors_rhf only fit ~28 states (see platform/model's `sae check`
    # note) -- the rank denominator should reflect that, not silently say /37.
    d = [r for r in katsina.rows if r.slug == "diarrhoea_ors_rhf"]
    if d:
        assert d[0].n_ranked < 37


def test_every_row_traces_to_a_real_fh_state_cell(katsina):
    st = pd.read_parquet(FH_STATE)
    st = st[(st.state_pcode == "NG021") & (st.survey_id == katsina.survey_id)]
    have = set(st.slug)
    assert {r.slug for r in katsina.rows} <= have
