"""Fay–Herriot math, checked against a simulated ground truth (no I/O)."""

import numpy as np
import pandas as pd
import pytest

from sae.fayherriot import FHFit, _neg_reml_loglik, estimate


def _simulate(m=50, true_beta=(50.0, 6.0), true_sigma_u2=4.0, seed=7):
    # beta[0]=50 keeps y well inside the [0,100] percentage range this
    # module clips to, so the shrinkage-bounds test isn't confounded by
    # clipping — this is simulated math, not a real indicator.
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=m)
    X = np.column_stack([np.ones(m), x1])
    psi = rng.uniform(1.0, 9.0, size=m)                # known, heterogeneous
    u = rng.normal(0, np.sqrt(true_sigma_u2), size=m)
    e = rng.normal(0, np.sqrt(psi))
    y = X @ np.array(true_beta) + u + e
    return X, y, psi, u


def test_reml_recovers_beta_and_variance_in_the_right_ballpark():
    X, y, psi, _ = _simulate()
    from scipy.optimize import minimize_scalar
    res = minimize_scalar(_neg_reml_loglik, bounds=(0, 50), method="bounded", args=(y, X, psi))
    sigma_u2 = res.x
    Vinv = 1.0 / (sigma_u2 + psi)
    beta = np.linalg.solve(X.T @ (X * Vinv[:, None]), X.T @ (y * Vinv))
    assert sigma_u2 == pytest.approx(4.0, abs=3.5)         # noisy with m=50, but same order
    assert beta[0] == pytest.approx(50.0, abs=1.5)
    assert beta[1] == pytest.approx(6.0, abs=1.0)


def _fit_result(X, y, psi, sigma_u2, beta) -> FHFit:
    cols = ["x1"]
    d = pd.DataFrame({
        "state_pcode": [f"S{i}" for i in range(len(y))],
        "state_name": [f"S{i}" for i in range(len(y))],
        "y": y, "psi": psi, "psi_method": "sim", "denom_unweighted": 500,
        "x1": X[:, 1],
    })
    return FHFit(slug="sim", survey_id="SIM", cols=cols, beta=beta, sigma_u2=sigma_u2,
                col_mean=d[cols].mean(), col_std=pd.Series([1.0], index=cols),
                n_states=len(d), var_sigma_u2=0.5, states=d)


def test_shrinkage_direction_and_bounds():
    """gamma in (0,1), fh between direct and synthetic, tighter psi -> more direct weight."""
    X, y, psi, _ = _simulate()
    beta = np.array([10.0, 6.0])
    fit_ = _fit_result(X, y, psi, sigma_u2=4.0, beta=beta)
    out = estimate(fit_)

    assert out.gamma.between(0, 1, inclusive="neither").all()
    lo = np.minimum(out.direct, out.synthetic)
    hi = np.maximum(out.direct, out.synthetic)
    assert ((out.fh_estimate >= lo - 1e-6) & (out.fh_estimate <= hi + 1e-6)).all()
    # low psi (precise survey) -> gamma close to 1 (trust the direct estimate)
    assert out.loc[out.psi.idxmin(), "gamma"] > out.loc[out.psi.idxmax(), "gamma"]
    assert (out.fh_se > 0).all()


def test_extreme_psi_limits():
    """psi -> 0 collapses to the direct estimate; psi -> inf collapses to the synthetic one."""
    X = np.column_stack([np.ones(3), [0.0, 1.0, -1.0]])
    y = np.array([50.0, 60.0, 40.0])
    beta = np.array([50.0, 5.0])
    tiny = _fit_result(X, y, np.array([1e-8, 1e-8, 1e-8]), sigma_u2=4.0, beta=beta)
    huge = _fit_result(X, y, np.array([1e8, 1e8, 1e8]), sigma_u2=4.0, beta=beta)
    assert estimate(tiny).fh_estimate.to_numpy() == pytest.approx(y, abs=1e-3)
    assert estimate(huge).fh_estimate.to_numpy() == pytest.approx(X @ beta, abs=1e-3)
