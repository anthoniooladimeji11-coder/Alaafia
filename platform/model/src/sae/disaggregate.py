"""Stage 2 — spread the state-level Fay–Herriot fit down to 774 LGAs.

A *synthetic* regression estimate: the same fitted β applied to each
LGA's own covariates, using the exact standardisation the state fit
used. Then benchmarked so the population-weighted mean of a state's
LGAs reconciles to that state's FH number — the state figure stays
authoritative; covariates only redistribute it within the state.

The benchmarking shift is solved on the **logit scale**, not added to
the raw percentage. An additive shift on the percentage scale can push
an already-high (or low) LGA past 100 (or below 0); clipping it back
into range then silently breaks the very reconciliation the shift was
for — an LGA near the boundary "absorbs" less of the shift than its
covariates said it should, once cut. Working in logit space and solving
for the shift with a root-finder keeps every LGA estimate in (0,100) by
construction, so no clipping is ever needed and the population-weighted
mean of the LGAs hits the state figure to numerical precision.

This is not a substitute for unit-level small-area estimation: there is
no LGA-local survey signal here, only "what the covariate surface
predicts." `se_floor` is the parent state's own FH standard error — a
documented lower bound, not the true LGA uncertainty (which is higher
than this by an amount the covariates can't measure). See
model/README.md "What this is not."
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from .config import COV_LGA
from .fayherriot import FHFit

_EPS = 1e-6


def _logit(p: np.ndarray) -> np.ndarray:
    return np.log(p / (1 - p))


def _inv_logit(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def _benchmark_state(logit_raw: np.ndarray, w: np.ndarray, target_pct: float) -> np.ndarray:
    """Find delta so the pop-weighted mean of inv_logit(logit_raw + delta) hits
    target_pct/100. inv_logit is strictly increasing in delta, so is its
    weighted mean -> a bracketed root always exists for target in (0,100)."""
    target = np.clip(target_pct / 100.0, _EPS, 1 - _EPS)

    def f(delta: float) -> float:
        return float(np.average(_inv_logit(logit_raw + delta), weights=w)) - target

    lo, hi = -40.0, 40.0                    # inv_logit(±40) is already ~0/1
    if f(lo) > 0 or f(hi) < 0:              # degenerate (single LGA etc.) — clamp
        delta = lo if f(lo) > 0 else hi
    else:
        delta = brentq(f, lo, hi, xtol=1e-10)
    return logit_raw + delta


def disaggregate(fit_: FHFit, fh_state: pd.DataFrame) -> pd.DataFrame:
    lga = pd.read_parquet(
        COV_LGA, columns=["lga_pcode", "lga_name", "state_pcode", "pop_2020"] + fit_.cols
    ).copy()

    # A handful of LGAs (~14, dense-urban — no discrete GRID3 settlement
    # extent) are missing a settlement-derived covariate. Impute with
    # their own state's mean rather than drop them from the output: losing
    # an LGA's estimate entirely is worse than a same-state approximation
    # for one predictor out of several.
    for c in fit_.cols:
        if lga[c].isna().any():
            lga[c] = lga[c].fillna(lga.groupby("state_pcode")[c].transform("mean"))
            lga[c] = lga[c].fillna(lga[c].mean())          # national fallback, last resort

    # The state fit trained on state-*aggregated* covariates, which
    # average out any one bad LGA. Applied raw to individual LGAs, the
    # ~65 `metro_merge_suspect` ones (GRID3's settlement blobs merged
    # across LGA lines — see covariates/README.md) are wild covariate
    # outliers: e.g. a `builtup_fraction` of ~0 next door to one pushed
    # to 1.0 that absorbed the whole conurbation. Fed through a
    # regression fit at state scale, that extrapolates to an absurd
    # predicted logit and can saturate an LGA's estimate at ~0% or
    # ~100% regardless of the indicator. Winsorizing the standardized
    # covariates keeps every LGA within the range the model was
    # actually trained on — a standard safeguard against exactly this,
    # not specific to the metro-merge issue.
    Xz = (((lga[fit_.cols] - fit_.col_mean) / fit_.col_std)
         .clip(-4, 4).to_numpy())
    X = np.column_stack([np.ones(len(lga)), Xz])
    # the regression is fit on the percentage scale (Stage 1); read its
    # linear predictor as a logit so Stage 2's calibration can't leave
    # (0,100) — clip away from the exact boundary first (only matters for
    # extreme covariate outliers).
    logit_raw = _logit(np.clip((X @ fit_.beta) / 100.0, _EPS, 1 - _EPS))

    # Winsorizing each covariate bounds any *one* input's contribution,
    # but several moderately-extreme covariates can still sum to a
    # linear predictor no real place would produce — which is exactly
    # how an urban LGA ended up predicted at *exactly* 0.0% stunting.
    # Bound the joint prediction too: no LGA is allowed to be more
    # extreme, in logit space, than Nigeria's own most extreme *state*
    # direct estimate plus a margin — an LGA can plausibly exceed every
    # state's number a little, not implausibly (a real value pinned at
    # a probability of literally zero).
    obs_logit = _logit(np.clip(fh_state["direct"].to_numpy() / 100.0, _EPS, 1 - _EPS))
    span = float(obs_logit.max() - obs_logit.min())
    pad = max(1.0, 0.75 * span)
    lo, hi = obs_logit.min() - pad, obs_logit.max() + pad
    lga["logit_raw"] = np.clip(logit_raw, lo, hi)

    # merge FIRST, weights SECOND: a merge resets the row order/index, so
    # computing `w` before it and then indexing into it with positions
    # from a groupby run *after* it is a silent misalignment — weights
    # end up attached to the wrong LGAs for any state pandas happened to
    # reorder during the join. (This produced a real, hard-to-spot
    # reconciliation gap in a handful of states before it was caught by
    # `sae check`'s reconciliation test — see model/README.md changelog.)
    lga = lga.merge(fh_state[["state_pcode", "fh_estimate", "fh_se"]], on="state_pcode", how="inner")
    w = lga.pop_2020.fillna(lga.groupby("state_pcode").pop_2020.transform("mean")).fillna(1.0)

    logit_adj = np.empty(len(lga))
    for state, idx in lga.groupby("state_pcode").indices.items():
        idx = np.asarray(idx)
        target = lga.iloc[idx[0]].fh_estimate
        logit_adj[idx] = _benchmark_state(lga.logit_raw.to_numpy()[idx],
                                          w.to_numpy()[idx], target)

    lga["estimate"] = 100.0 * _inv_logit(logit_adj)
    lga["se_floor"] = lga.fh_se
    lga["ci_low"] = np.clip(lga.estimate - 1.96 * lga.se_floor, 0, 100)
    lga["ci_high"] = np.clip(lga.estimate + 1.96 * lga.se_floor, 0, 100)
    lga["slug"], lga["survey_id"] = fit_.slug, fit_.survey_id
    lga["method"] = "synthetic_regression_logit_benchmarked"

    return lga[["lga_pcode", "lga_name", "state_pcode", "slug", "survey_id",
               "estimate", "se_floor", "ci_low", "ci_high", "method"]]
