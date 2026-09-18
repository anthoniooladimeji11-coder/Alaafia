"""The area-level Fay–Herriot model.

    y_i = x_i'β + u_i + e_i,   u_i ~ N(0, σ²_u),   e_i ~ N(0, ψ_i known)

β and σ²_u fit by REML; the EBLUP shrinks each state's direct estimate
toward the regression line in proportion to how noisy that state's own
number is (γ_i = σ²_u/(σ²_u+ψ_i)). MSE via the standard Prasad-Rao /
Datta-Lahiri (REML) second-order approximation: g1 + g2 + g3 — see
Rao & Molina, *Small Area Estimation* 2nd ed. (2015), §6.2, §7.1.

ψ_i (sampling variance) comes from the DHS API's CI when published;
otherwise from an indicator-typical design effect on the binomial
variance — a documented approximation, not a design-based SE (see
model/README.md "What this is not").
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from .config import COV_LGA, DEFAULT_DEFF, MIN_STATES_TO_FIT, STATE_COVARIATES, SURVEY


# ------------------------------------------------------------ direct estimates --
def sampling_variance(value: float, ci_low: float | None, ci_high: float | None,
                      denom: float | None, unit: str = "pct",
                      *, deff: float = DEFAULT_DEFF) -> tuple[float, str]:
    """psi for one cell, in the same natural units as `value`
    (0-100 for pct/prev_pct, deaths-per-1,000 for rate_1000).
    Returns (psi, method).

    The API's own CI is unit-agnostic (just a width -> variance
    conversion) and is used whenever published. The denominator
    fallback is not: it approximates a *binomial* proportion's
    variance, which only makes sense for pct/prev_pct — applying it to
    a mortality rate would silently treat "132 deaths per 1,000" as a
    132% probability. An unrecognised unit returns "unavailable"
    rather than guess.
    """
    if ci_low is not None and ci_high is not None and not (pd.isna(ci_low) or pd.isna(ci_high)):
        se = (ci_high - ci_low) / (2 * 1.96)
        return max(se, 1e-6) ** 2, "api_ci"
    if denom is not None and not pd.isna(denom) and denom > 0:
        if unit in ("pct", "prev_pct"):
            p = np.clip(value / 100.0, 0.01, 0.99)
            var_p = deff * p * (1 - p) / denom
            return max(var_p * 100.0 ** 2, 1e-6), "deff_approx"
        if unit == "rate_1000":
            # Poisson approximation: Var(deaths) ~ deaths, propagated to the
            # per-1,000 rate, with the same DEFF used for proportions as a
            # documented stand-in for the real design effect on a rate.
            deaths = max(value, 0.0) * denom / 1000.0
            var_rate = deff * deaths * (1000.0 / denom) ** 2
            return max(var_rate, 1e-6), "deff_approx"
        return np.nan, "unavailable"
    return np.nan, "unavailable"


def direct_estimates(slug: str, survey_id: str) -> pd.DataFrame:
    """One row per state with a direct estimate for this indicator/survey."""
    df = pd.read_parquet(SURVEY)
    d = df[(df.slug == slug) & (df.survey_id == survey_id) & (df.geo_level == "state")
          & df.geo_pcode.notna()].copy()
    psi_method = d.apply(lambda r: sampling_variance(r.value, r.ci_low, r.ci_high,
                                                      r.denom_unweighted, r.unit), axis=1)
    d["psi"] = [p for p, _ in psi_method]
    d["psi_method"] = [m for _, m in psi_method]
    return d[["geo_pcode", "geo_name", "value", "psi", "psi_method",
              "denom_unweighted", "unit"]].rename(
        columns={"geo_pcode": "state_pcode", "geo_name": "state_name", "value": "y"}
    ).dropna(subset=["y", "psi"]).reset_index(drop=True)


# ---------------------------------------------------------- covariate matrix --
def state_covariate_matrix(cols: list[str] = STATE_COVARIATES) -> pd.DataFrame:
    """Population-weighted LGA covariates rolled up to state level."""
    lga = pd.read_parquet(COV_LGA, columns=["state_pcode", "pop_2020"] + cols)
    w = lga.pop_2020.fillna(lga.groupby(lga.state_pcode).pop_2020.transform("mean"))
    out = {}
    for c in cols:
        v = lga[c]
        num = (v * w).groupby(lga.state_pcode).sum()
        den = w.where(v.notna()).groupby(lga.state_pcode).sum()
        out[c] = num / den
    return pd.DataFrame(out).reset_index().rename(columns={"index": "state_pcode"})


@dataclass
class FHFit:
    slug: str
    survey_id: str
    unit: str
    cols: list[str]
    beta: np.ndarray
    sigma_u2: float
    col_mean: pd.Series
    col_std: pd.Series
    n_states: int
    var_sigma_u2: float
    states: pd.DataFrame = field(repr=False)          # the fitted state table


# --------------------------------------------------------------------- REML --
def _neg_reml_loglik(sigma_u2: float, y: np.ndarray, X: np.ndarray, psi: np.ndarray) -> float:
    V = sigma_u2 + psi
    Vinv = 1.0 / V
    XtVinvX = X.T @ (X * Vinv[:, None])
    XtVinvy = X.T @ (y * Vinv)
    beta = np.linalg.solve(XtVinvX, XtVinvy)
    resid = y - X @ beta
    quad = float(np.sum(resid ** 2 * Vinv))
    _, logdet = np.linalg.slogdet(XtVinvX)
    ll = -0.5 * (np.sum(np.log(V)) + logdet + quad)
    return -ll


def fit(slug: str, survey_id: str, cols: list[str] = STATE_COVARIATES) -> FHFit:
    direct = direct_estimates(slug, survey_id)
    if len(direct) < MIN_STATES_TO_FIT:
        raise ValueError(f"{slug}/{survey_id}: only {len(direct)} states with a direct "
                         f"estimate (need >= {MIN_STATES_TO_FIT})")

    cov = state_covariate_matrix(cols)
    d = direct.merge(cov, on="state_pcode", how="inner")
    if len(d) < len(direct):
        missing = set(direct.state_pcode) - set(d.state_pcode)
        raise ValueError(f"{slug}/{survey_id}: no covariates for states {missing}")

    col_mean, col_std = d[cols].mean(), d[cols].std(ddof=0).replace(0, 1)
    Xz = ((d[cols] - col_mean) / col_std).to_numpy()
    X = np.column_stack([np.ones(len(d)), Xz])
    y, psi = d.y.to_numpy(), d.psi.to_numpy()

    upper = 10 * np.var(y) + 1.0
    res = minimize_scalar(_neg_reml_loglik, bounds=(0.0, upper), method="bounded",
                          args=(y, X, psi), options={"xatol": 1e-6})
    sigma_u2 = float(res.x)

    V = sigma_u2 + psi
    Vinv = 1.0 / V
    XtVinvX = X.T @ (X * Vinv[:, None])
    beta = np.linalg.solve(XtVinvX, X.T @ (y * Vinv))
    var_sigma_u2 = 2.0 / float(np.sum(Vinv ** 2))          # REML asymptotic variance

    d = d.assign(_row=range(len(d)))
    return FHFit(slug=slug, survey_id=survey_id, unit=d.unit.iloc[0], cols=cols, beta=beta,
                sigma_u2=sigma_u2, col_mean=col_mean, col_std=col_std, n_states=len(d),
                var_sigma_u2=var_sigma_u2, states=d)


# ------------------------------------------------------------------ estimate --
def estimate(fit_: FHFit) -> pd.DataFrame:
    d = fit_.states
    Xz = ((d[fit_.cols] - fit_.col_mean) / fit_.col_std).to_numpy()
    X = np.column_stack([np.ones(len(d)), Xz])
    y, psi = d.y.to_numpy(), d.psi.to_numpy()

    V = fit_.sigma_u2 + psi
    gamma = fit_.sigma_u2 / V
    synthetic = X @ fit_.beta
    fh = gamma * y + (1 - gamma) * synthetic

    Vinv = 1.0 / V
    XtVinvX_inv = np.linalg.inv(X.T @ (X * Vinv[:, None]))
    g1 = gamma * psi
    g2 = np.array([(1 - gamma[i]) ** 2 * X[i] @ XtVinvX_inv @ X[i] for i in range(len(d))])
    g3 = (psi ** 2 / V ** 3) * fit_.var_sigma_u2
    mse = np.clip(g1 + g2 + g3, 1e-9, None)
    se = np.sqrt(mse)

    # A percentage/prevalence is bounded on both sides; a per-1,000 rate
    # only below, at 0 — deaths can't be negative, but a rate in the
    # hundreds is a real (if grim) possibility, not a bug to clip away.
    # np.clip (not pandas .clip) on purpose: these are plain ndarrays and
    # assigning a bare array avoids any index-alignment surprise against
    # `out`'s own index.
    hi_bound = 100.0 if fit_.unit in ("pct", "prev_pct") else None
    out = d[["state_pcode", "state_name", "y", "psi", "psi_method", "denom_unweighted"]].copy()
    out["synthetic"] = synthetic
    out["gamma"] = gamma
    out["fh_estimate"] = np.clip(fh, 0, hi_bound)
    out["fh_se"] = se
    out["fh_ci_low"] = np.clip(fh - 1.96 * se, 0, hi_bound)
    out["fh_ci_high"] = np.clip(fh + 1.96 * se, 0, hi_bound)
    out["slug"], out["survey_id"], out["unit"] = fit_.slug, fit_.survey_id, fit_.unit
    return out.rename(columns={"y": "direct"})
