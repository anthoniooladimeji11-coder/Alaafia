"""Unit-level small-area model: LGA direct estimates computed from actual
DHS cluster microdata, shrunk via the same Fay-Herriot EBLUP logic as
Stage 1 — just run one level finer, with a real local sample behind each
estimate instead of a national regression redistributed down.

    y_i = x_i'β + u_i + e_i      (identical model to fayherriot.py;
                                   i indexes LGAs here, not states)

Where an LGA has zero DHS clusters there is no direct estimate to shrink;
that LGA gets the pure regression (synthetic) prediction — the same honest
fallback Stage 2 already uses when it has nothing else, except this
regression is fit on 646 LGA-level observations instead of 37 state-level
ones, so even the no-data LGAs inherit a more local signal than before.

This deliberately duplicates fayherriot.py's REML/EBLUP core (reusing its
`sampling_variance` and `_neg_reml_loglik` directly, but re-deriving the fit
loop) rather than refactoring that module to be level-generic. fayherriot.py
is live, tested code behind the already-published state estimates;
reshaping its signature to serve two callers is a real, separate refactor
with its own review — not something to fold into proving this approach
works. If unit-level estimation proves out and expands past stunting, that
consolidation is the natural next cleanup.

Scoped to whatever surveylayer.microdata has extracted into
cluster_nutrition.parquet — currently child_stunting, child_wasting,
child_underweight, same 4 rounds each. `run_all()` discovers available
slugs from the data itself rather than keeping its own parallel list, so
there's nothing to forget to update when microdata.py grows another one.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from .config import CLUSTER_NUTRITION, COV_LGA, STATE_COVARIATES, UNIT_LGA_PARQUET
from .fayherriot import _neg_reml_loglik, sampling_variance

MIN_LGAS_TO_FIT = 50


def lga_direct_estimates(slug: str, survey_id: str = "NG2024DHS") -> pd.DataFrame:
    """One row per LGA with >=1 DHS cluster: the pooled weighted rate for
    `slug` across every child in every one of that LGA's clusters (pooled
    at the child level via each cluster's own weight_sum — a 12-child
    cluster and a 2-child cluster don't count equally), plus its sampling
    variance via the same DEFF approximation Stage 1 uses for any cell
    without a published CI (there is no published CI here at all; it's
    the only option, not a fallback among several)."""
    cs = pd.read_parquet(CLUSTER_NUTRITION)
    d = cs[(cs.slug == slug) & (cs.survey_round == survey_id) & cs.lga_pcode.notna()].copy()
    if d.empty:
        raise ValueError(f"{slug}/{survey_id}: no cluster data in {CLUSTER_NUTRITION}")
    # weight_sum * rate reconstructs each cluster's weighted-affected total
    # exactly (rate was defined as that total / weight_sum) — no need to
    # re-read the raw KR file to pool clusters correctly.
    d["w_affected"] = d.weight_sum * d.rate

    g = d.groupby("lga_pcode").agg(
        n_clusters=("cluster_id", "size"),
        n_children=("n_children", "sum"),
        weight_sum=("weight_sum", "sum"),
        w_affected_sum=("w_affected", "sum"),
    )
    g["direct"] = 100.0 * g.w_affected_sum / g.weight_sum   # pct, matching Stage 1's unit

    psi_method = g.apply(
        lambda r: sampling_variance(r.direct, None, None, r.n_children, "pct"), axis=1
    )
    g["psi"] = [p for p, _ in psi_method]
    g["psi_method"] = [m for _, m in psi_method]
    return g[["n_clusters", "n_children", "direct", "psi", "psi_method"]].reset_index()


def available_slugs() -> list[str]:
    """Indicators surveylayer.microdata has actually extracted — read from
    the data, not a parallel hardcoded list that could drift from it."""
    return pd.read_parquet(CLUSTER_NUTRITION, columns=["slug"]).slug.unique().tolist()


def _lga_covariates(cols: list[str]) -> pd.DataFrame:
    """All 774 LGAs, every covariate present — same imputation disaggregate.py
    already uses for the ~14 LGAs GRID3's settlement layer doesn't reach
    (same-state mean, then national mean as a last resort), so this output
    covers every LGA Stage 2 does, not a quietly smaller set."""
    lga = pd.read_parquet(COV_LGA, columns=["lga_pcode", "state_pcode"] + cols).copy()
    for c in cols:
        if lga[c].isna().any():
            lga[c] = lga[c].fillna(lga.groupby("state_pcode")[c].transform("mean"))
            lga[c] = lga[c].fillna(lga[c].mean())
    return lga


@dataclass
class UnitFit:
    slug: str
    survey_id: str
    cols: list[str]
    beta: np.ndarray
    sigma_u2: float
    col_mean: pd.Series
    col_std: pd.Series
    n_lgas: int
    var_sigma_u2: float
    weak_signal: bool                                 # see fit() — sigma_u2 negligible vs sampling noise
    lgas: pd.DataFrame = field(repr=False)          # the LGAs actually fit (have direct data)
    all_covariates: pd.DataFrame = field(repr=False)  # all 774, for out-of-sample prediction


def fit(slug: str, survey_id: str = "NG2024DHS", cols: list[str] = STATE_COVARIATES) -> UnitFit:
    direct = lga_direct_estimates(slug, survey_id)
    cov = _lga_covariates(cols)
    d = direct.merge(cov, on="lga_pcode", how="inner")
    if len(d) < MIN_LGAS_TO_FIT:
        raise ValueError(f"{slug}/{survey_id}: only {len(d)} LGAs with a direct "
                         f"estimate (need >= {MIN_LGAS_TO_FIT})")

    col_mean, col_std = d[cols].mean(), d[cols].std(ddof=0).replace(0, 1)
    Xz = ((d[cols] - col_mean) / col_std).to_numpy()
    X = np.column_stack([np.ones(len(d)), Xz])
    y, psi = d.direct.to_numpy(), d.psi.to_numpy()

    upper = 10 * np.var(y) + 1.0
    res = minimize_scalar(_neg_reml_loglik, bounds=(0.0, upper), method="bounded",
                          args=(y, X, psi), options={"xatol": 1e-6})
    sigma_u2 = float(res.x)

    V = sigma_u2 + psi
    Vinv = 1.0 / V
    XtVinvX = X.T @ (X * Vinv[:, None])
    beta = np.linalg.solve(XtVinvX, X.T @ (y * Vinv))
    var_sigma_u2 = 2.0 / float(np.sum(Vinv ** 2))

    # REML found essentially no between-LGA variance beyond sampling noise:
    # every LGA's gamma will be near 0 and the EBLUP collapses to the
    # (nearly flat) regression line regardless of each LGA's own direct
    # estimate — the honest outcome when raw variance across direct
    # estimates doesn't exceed the sampling noise itself (seen for real with
    # child_wasting: var(direct)=134 < mean(psi)=158), not a bug to chase
    # away by forcing sigma_u2 up. Surfaced rather than left for someone to
    # notice only by eyeballing a suspiciously narrow estimate range.
    weak_signal = sigma_u2 < 0.1 * float(np.median(psi))

    return UnitFit(slug=slug, survey_id=survey_id, cols=cols, beta=beta,
                   sigma_u2=sigma_u2, col_mean=col_mean, col_std=col_std, n_lgas=len(d),
                   var_sigma_u2=var_sigma_u2, weak_signal=weak_signal,
                   lgas=d.reset_index(drop=True), all_covariates=cov)


def estimate(fit_: UnitFit) -> pd.DataFrame:
    d = fit_.lgas
    Xz = ((d[fit_.cols] - fit_.col_mean) / fit_.col_std).to_numpy()
    X = np.column_stack([np.ones(len(d)), Xz])
    y, psi = d.direct.to_numpy(), d.psi.to_numpy()

    V = fit_.sigma_u2 + psi
    gamma = fit_.sigma_u2 / V
    synthetic = X @ fit_.beta
    eblup = gamma * y + (1 - gamma) * synthetic

    Vinv = 1.0 / V
    XtVinvX_inv = np.linalg.inv(X.T @ (X * Vinv[:, None]))
    g1 = gamma * psi
    g2 = np.einsum("ij,jk,ik->i", X, XtVinvX_inv, X) * (1 - gamma) ** 2
    g3 = (psi ** 2 / V ** 3) * fit_.var_sigma_u2
    mse = np.clip(g1 + g2 + g3, 1e-9, None)

    fitted = d[["lga_pcode", "n_clusters", "n_children", "direct", "psi"]].copy()
    fitted["gamma"] = gamma
    fitted["estimate"] = np.clip(eblup, 0, 100)
    fitted["se"] = np.sqrt(mse)
    fitted["method"] = "unit_level_eblup"

    # ── LGAs with zero DHS clusters: pure out-of-sample synthetic prediction ──
    missing = fit_.all_covariates[~fit_.all_covariates.lga_pcode.isin(d.lga_pcode)].copy()
    if len(missing):
        Xz_m = ((missing[fit_.cols] - fit_.col_mean) / fit_.col_std).to_numpy()
        X_m = np.column_stack([np.ones(len(missing)), Xz_m])
        synth_m = X_m @ fit_.beta
        # Out-of-sample MSE: sigma_u2 (we know nothing about THIS area's own
        # random effect — its full prior variance is the honest floor) plus
        # the same regression-parameter-uncertainty term as above (the
        # gamma->0 limit of g1+g2's g2 term). g3 (variance of the variance
        # component) is a second-order refinement, dropped here — not needed
        # for a defensible SE on a quantity this uncertain to begin with.
        g2_m = np.einsum("ij,jk,ik->i", X_m, XtVinvX_inv, X_m)
        mse_m = fit_.sigma_u2 + g2_m

        unfitted = missing[["lga_pcode"]].copy()
        unfitted["n_clusters"] = 0
        unfitted["n_children"] = 0
        unfitted["direct"] = np.nan
        unfitted["psi"] = np.nan
        unfitted["gamma"] = 0.0
        unfitted["estimate"] = np.clip(synth_m, 0, 100)
        unfitted["se"] = np.sqrt(np.clip(mse_m, 1e-9, None))
        unfitted["method"] = "unit_level_synthetic"
        out = pd.concat([fitted, unfitted], ignore_index=True)
    else:
        out = fitted

    out["ci_low"] = (out.estimate - 1.96 * out.se).clip(lower=0, upper=100)
    out["ci_high"] = (out.estimate + 1.96 * out.se).clip(lower=0, upper=100)
    out["slug"], out["survey_id"], out["unit"] = fit_.slug, fit_.survey_id, "pct"
    # carried through to the persisted table, not just the transient fit
    # object — a reader of unit_lga.parquet alone should be able to tell
    # this indicator's LGA variation is mostly noise, not go looking for it
    out["weak_signal"] = fit_.weak_signal
    return out


def run_all(survey_id: str = "NG2024DHS", *, slugs: list[str] | None = None) -> dict:
    """Fit + estimate every available slug, persist to UNIT_LGA_PARQUET.
    Same incremental-rebuild pattern as run.run_all(): drop any prior rows
    for (slug, survey_id) about to be rewritten, keep everything else."""
    todo = slugs if slugs is not None else available_slugs()
    frames, ok, failed, weak = [], [], [], []
    for slug in todo:
        try:
            fit_ = fit(slug, survey_id)
            frames.append(estimate(fit_))
            ok.append(slug)
            if fit_.weak_signal:
                weak.append(slug)
        except ValueError as e:
            failed.append((slug, str(e)))

    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if len(result):
        prior = pd.read_parquet(UNIT_LGA_PARQUET) if UNIT_LGA_PARQUET.exists() else pd.DataFrame()
        if len(prior):
            prior = prior[~((prior.survey_id == survey_id) & prior.slug.isin(ok))]
        pd.concat([prior, result], ignore_index=True).to_parquet(UNIT_LGA_PARQUET, index=False)

    return {"survey_id": survey_id, "fit": ok, "skipped": failed, "weak_signal": weak,
           "rows": len(result)}
