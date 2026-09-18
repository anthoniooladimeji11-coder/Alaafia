"""Stage 2 — spread the state-level Fay–Herriot fit down to 774 LGAs.

A *synthetic* regression estimate: the same fitted β applied to each
LGA's own covariates, using the exact standardisation the state fit
used. Then benchmarked so the population-weighted mean of a state's
LGAs reconciles to that state's FH number — the state figure stays
authoritative; covariates only redistribute it within the state.

The benchmarking shift is solved on a **link scale**, not added to the
raw value — which link depends on the indicator's unit (`_link_pair`):
logit for a percentage/prevalence (bounded to (0,100)), log for a
per-1,000 rate (bounded only below, at 0). An additive shift on the
raw scale can push an already-high (or low) LGA past its natural
bound; clipping it back then silently breaks the very reconciliation
the shift was for — an LGA near the boundary "absorbs" less of the
shift than its covariates said it should, once cut. Working in link
space and solving for the shift with a root-finder keeps every LGA
estimate within its natural range by construction, so no clipping is
ever needed and the population-weighted mean of the LGAs hits the
state figure to numerical precision.

This is not a substitute for unit-level small-area estimation: there is
no LGA-local survey signal here, only "what the covariate surface
predicts." `se_floor` is the parent state's own FH standard error — a
documented lower bound, not the true LGA uncertainty (which is higher
than this by an amount the covariates can't measure). See
model/README.md "What this is not."
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from .config import COV_LGA
from .fayherriot import FHFit

_EPS = 1e-6           # keeps a logit input off the exact 0/1 boundary
_RATE_FLOOR = 0.01    # deaths per 1,000 — keeps log(rate) finite for a ~0 rate


def _logit(p: np.ndarray) -> np.ndarray:
    return np.log(p / (1 - p))


def _inv_logit(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def _link_pair(unit: str) -> tuple[Callable, Callable]:
    """(to_link, from_link) for an indicator's natural-scale value.

    pct / prev_pct — bounded (0,100): logit.
    rate_1000      — bounded (0,∞): log. `from_link` clips its input before
                     `exp` purely for numerical safety (overflow at the
                     brentq bracket's edges, ±40) — it does not bound the
                     *result*, unlike the logit case where the bound is
                     the entire point.
    """
    if unit in ("pct", "prev_pct"):
        return (lambda v: _logit(np.clip(v / 100.0, _EPS, 1 - _EPS)),
                lambda z: 100.0 * _inv_logit(z))
    if unit == "rate_1000":
        return (lambda v: np.log(np.maximum(v, _RATE_FLOOR)),
                lambda z: np.exp(np.clip(z, -30, 30)))
    raise ValueError(f"disaggregate: no link function defined for unit={unit!r}")


def _benchmark_state(link_raw: np.ndarray, w: np.ndarray, target: float,
                     from_link: Callable) -> np.ndarray:
    """Find delta so the pop-weighted mean of from_link(link_raw + delta) hits
    target. from_link is strictly increasing in its input, so is the
    resulting weighted mean -> a bracketed root always exists."""
    def f(delta: float) -> float:
        return float(np.average(from_link(link_raw + delta), weights=w)) - target

    lo, hi = -40.0, 40.0
    if f(lo) > 0 or f(hi) < 0:              # degenerate (single LGA etc.) — clamp
        delta = lo if f(lo) > 0 else hi
    else:
        delta = brentq(f, lo, hi, xtol=1e-10)
    return link_raw + delta


def disaggregate(fit_: FHFit, fh_state: pd.DataFrame) -> pd.DataFrame:
    to_link, from_link = _link_pair(fit_.unit)
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
    # predicted link value and can saturate an LGA's estimate at an
    # implausible extreme regardless of the indicator. Winsorizing the
    # standardized covariates keeps every LGA within the range the
    # model was actually trained on — a standard safeguard against
    # exactly this, not specific to the metro-merge issue.
    Xz = (((lga[fit_.cols] - fit_.col_mean) / fit_.col_std)
         .clip(-4, 4).to_numpy())
    X = np.column_stack([np.ones(len(lga)), Xz])
    # the regression is fit on the indicator's natural scale (Stage 1);
    # read its linear predictor through the link function so Stage 2's
    # calibration can't leave the indicator's natural range.
    link_raw = to_link(X @ fit_.beta)

    # Winsorizing each covariate bounds any *one* input's contribution,
    # but several moderately-extreme covariates can still sum to a
    # linear predictor no real place would produce — which is exactly
    # how an urban LGA ended up predicted at *exactly* 0.0% stunting.
    # Bound the joint prediction too: no LGA is allowed to be more
    # extreme, on the link scale, than Nigeria's own most extreme
    # *state* direct estimate plus a margin — an LGA can plausibly
    # exceed every state's number a little, not implausibly (a
    # probability pinned at literally zero, or a mortality rate an
    # order of magnitude past the worst state on record).
    obs_link = to_link(fh_state["direct"].to_numpy())
    span = float(obs_link.max() - obs_link.min())
    pad = max(1.0, 0.75 * span)
    lo, hi = obs_link.min() - pad, obs_link.max() + pad
    lga["link_raw"] = np.clip(link_raw, lo, hi)

    # merge FIRST, weights SECOND: a merge resets the row order/index, so
    # computing `w` before it and then indexing into it with positions
    # from a groupby run *after* it is a silent misalignment — weights
    # end up attached to the wrong LGAs for any state pandas happened to
    # reorder during the join. (This produced a real, hard-to-spot
    # reconciliation gap in a handful of states before it was caught by
    # `sae check`'s reconciliation test — see model/README.md changelog.)
    lga = lga.merge(fh_state[["state_pcode", "fh_estimate", "fh_se"]], on="state_pcode", how="inner")
    w = lga.pop_2020.fillna(lga.groupby("state_pcode").pop_2020.transform("mean")).fillna(1.0)

    link_adj = np.empty(len(lga))
    for state, idx in lga.groupby("state_pcode").indices.items():
        idx = np.asarray(idx)
        target = lga.iloc[idx[0]].fh_estimate
        link_adj[idx] = _benchmark_state(lga.link_raw.to_numpy()[idx],
                                         w.to_numpy()[idx], target, from_link)

    lga["estimate"] = from_link(link_adj)
    lga["se_floor"] = lga.fh_se
    lo_bound = 0.0
    hi_bound = 100.0 if fit_.unit in ("pct", "prev_pct") else None
    lga["ci_low"] = (lga.estimate - 1.96 * lga.se_floor).clip(lower=lo_bound, upper=hi_bound)
    lga["ci_high"] = (lga.estimate + 1.96 * lga.se_floor).clip(lower=lo_bound, upper=hi_bound)
    lga["slug"], lga["survey_id"], lga["unit"] = fit_.slug, fit_.survey_id, fit_.unit
    lga["method"] = "synthetic_regression_link_benchmarked"

    return lga[["lga_pcode", "lga_name", "state_pcode", "slug", "survey_id", "unit",
               "estimate", "se_floor", "ci_low", "ci_high", "method"]]
