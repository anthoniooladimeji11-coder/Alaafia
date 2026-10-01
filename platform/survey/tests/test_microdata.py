import pandas as pd
import pytest

from surveylayer.config import OUT
from surveylayer.microdata import NUTRITION_INDICATORS, UNIFORM_ROUNDS

CLUSTER_NUTRITION = OUT / "cluster_nutrition.parquet"

# Loose bounds, not a precision check — but deliberately tight enough to
# have actually caught the bug that motivated this test: hw71/hw72 swapped
# (wasting <-> underweight) during development, which produced wasting
# ~22-27% and underweight ~7-17% — each comfortably on the WRONG side of
# the other indicator's real range below. Nigeria's NDHS history across
# 2008-2024: stunting ~35-45%, underweight ~20-28% real / ~7-17% if swapped,
# wasting ~5-18% real / ~22-27% if swapped (wasting also ran genuinely
# higher in 2008/2013 than 2018/2024 — a real documented trend, not a bug).
PLAUSIBLE_NATIONAL_RANGE = {
    "child_stunting": (0.25, 0.55),
    "child_underweight": (0.18, 0.32),
    "child_wasting": (0.02, 0.20),
}


@pytest.fixture(scope="session")
def cluster_nutrition():
    if not CLUSTER_NUTRITION.exists():
        pytest.skip("run `uv run surveylayer clusters`")
    return pd.read_parquet(CLUSTER_NUTRITION)


def test_every_slug_and_round_present(cluster_nutrition):
    assert set(cluster_nutrition.slug.unique()) == set(NUTRITION_INDICATORS)
    assert set(cluster_nutrition.survey_round.unique()) == set(UNIFORM_ROUNDS)


def test_cluster_key_unique_per_slug(cluster_nutrition):
    dup = cluster_nutrition.duplicated(["slug", "survey_round", "cluster_id"])
    assert not dup.any()


def test_rate_in_unit_interval(cluster_nutrition):
    assert cluster_nutrition.rate.between(0, 1).all()


def test_n_affected_never_exceeds_n_children(cluster_nutrition):
    assert (cluster_nutrition.n_affected <= cluster_nutrition.n_children).all()


def test_national_rate_near_published_ndhs_range(cluster_nutrition):
    for (slug, r), g in cluster_nutrition.groupby(["slug", "survey_round"]):
        nat = (g.rate * g.n_children).sum() / g.n_children.sum()
        lo, hi = PLAUSIBLE_NATIONAL_RANGE[slug]
        assert lo < nat < hi, f"{slug}/{r}: {nat:.1%} is outside a plausible NDHS range"


def test_most_clusters_join_to_lga_and_covariates(cluster_nutrition):
    assert cluster_nutrition.lga_pcode.notna().mean() > 0.95
    assert cluster_nutrition.pop_density_km2.notna().mean() > 0.95
