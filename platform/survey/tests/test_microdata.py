import pandas as pd
import pytest

from surveylayer.config import OUT
from surveylayer.microdata import UNIFORM_ROUNDS

CLUSTER_STUNTING = OUT / "cluster_stunting.parquet"


@pytest.fixture(scope="session")
def cluster_stunting():
    if not CLUSTER_STUNTING.exists():
        pytest.skip("run `uv run surveylayer clusters`")
    return pd.read_parquet(CLUSTER_STUNTING)


def test_every_uniform_round_present(cluster_stunting):
    assert set(cluster_stunting.survey_round.unique()) == set(UNIFORM_ROUNDS)


def test_cluster_key_unique(cluster_stunting):
    dup = cluster_stunting.duplicated(["survey_round", "cluster_id"])
    assert not dup.any()


def test_stunting_rate_in_unit_interval(cluster_stunting):
    assert cluster_stunting.stunting_rate.between(0, 1).all()


def test_n_stunted_never_exceeds_n_children(cluster_stunting):
    assert (cluster_stunting.n_stunted <= cluster_stunting.n_children).all()


def test_national_rate_near_published_ndhs_range(cluster_stunting):
    # loose bounds, not a precision check — NDHS stunting has run ~35-45%
    # nationally across these rounds; this catches a sign-flip or a
    # threshold/weight bug, not meant to pin an exact figure
    for r, g in cluster_stunting.groupby("survey_round"):
        nat = (g.stunting_rate * g.n_children).sum() / g.n_children.sum()
        assert 0.25 < nat < 0.55, f"{r}: {nat:.1%} is outside a plausible NDHS range"


def test_most_clusters_join_to_lga_and_covariates(cluster_stunting):
    assert cluster_stunting.lga_pcode.notna().mean() > 0.95
    assert cluster_stunting.pop_density_km2.notna().mean() > 0.95
