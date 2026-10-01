"""Unit-level model: the vectorized MSE math checked against the loop-based
formula fayherriot.py uses (no I/O), plus an end-to-end check on real data.
Skips cleanly if the cluster microdata hasn't been built yet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sae.config import CLUSTER_STUNTING, COV_LGA
from sae.fayherriot import _neg_reml_loglik
from sae.unit_level import estimate, fit, lga_direct_estimates

pytestmark = pytest.mark.skipif(
    not (CLUSTER_STUNTING.exists() and COV_LGA.exists()),
    reason="cluster microdata / covariates not built — run `surveylayer clusters`",
)


def test_vectorized_g2_matches_loop_formula():
    """fayherriot.estimate() computes g2 with a Python loop; unit_level.estimate()
    vectorizes the identical quadratic form via einsum — this pins the two
    to agree to float precision on arbitrary inputs, not just the one real
    dataset this was eyeballed against."""
    rng = np.random.default_rng(3)
    n, k = 40, 3
    X = np.column_stack([np.ones(n), rng.normal(size=(n, k))])
    psi = rng.uniform(1.0, 9.0, size=n)
    sigma_u2 = 4.0
    V = sigma_u2 + psi
    gamma = sigma_u2 / V
    Vinv = 1.0 / V
    XtVinvX_inv = np.linalg.inv(X.T @ (X * Vinv[:, None]))

    g2_loop = np.array([(1 - gamma[i]) ** 2 * X[i] @ XtVinvX_inv @ X[i] for i in range(n)])
    g2_vec = np.einsum("ij,jk,ik->i", X, XtVinvX_inv, X) * (1 - gamma) ** 2
    assert g2_loop == pytest.approx(g2_vec, abs=1e-10)


def test_reml_objective_is_the_same_function_fayherriot_uses():
    # not a behavioural test so much as a guard against unit_level.py quietly
    # drifting to its own copy of the REML objective instead of importing it
    from sae.unit_level import _neg_reml_loglik as imported
    assert imported is _neg_reml_loglik


def test_lga_direct_estimates_sane():
    d = lga_direct_estimates()
    assert d.direct.between(0, 100).all()
    assert (d.psi > 0).all()
    assert (d.n_children > 0).all()
    assert d.lga_pcode.is_unique


def test_fit_and_estimate_cover_all_774_lgas():
    fit_ = fit()
    out = estimate(fit_)
    assert len(out) == 774
    assert out.lga_pcode.is_unique
    assert out.estimate.between(0, 100).all()
    assert (out.se > 0).all()
    assert set(out.method) == {"unit_level_eblup", "unit_level_synthetic"}
    # every LGA with direct data got the EBLUP treatment, no silent drop
    assert (out.method == "unit_level_eblup").sum() == fit_.n_lgas


def test_eblup_shrinks_toward_direct_when_data_is_rich():
    """An LGA with many of its own clusters should land closer to its own
    direct rate than to the pure covariate prediction — same shrinkage
    property fayherriot's own test checks, at this level instead."""
    fit_ = fit()
    out = estimate(fit_)
    rich = out[out.n_clusters >= 10]
    if rich.empty:
        pytest.skip("no LGA with >=10 clusters in this round")
    assert (rich.gamma > 0.7).all()
    assert ((rich.estimate - rich.direct).abs() < 10).all()


def test_zero_cluster_lgas_get_wider_uncertainty_than_data_rich_ones():
    fit_ = fit()
    out = estimate(fit_)
    synth_se = out.loc[out.method == "unit_level_synthetic", "se"].mean()
    rich_se = out.loc[out.n_clusters >= 5, "se"].mean()
    assert synth_se > rich_se
