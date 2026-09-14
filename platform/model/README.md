# model/ — small-area estimation

`MODEL` step of the pipeline. Turns the survey layer's state-level DHS
numbers + the covariate stack into estimates for all 774 LGAs, with
uncertainty, calibrated so they reconcile to the official state figures.
No microdata needed for this — that's the point of building it first.

## The method

**Stage 1 — area-level Fay–Herriot**, on the 37 states:

```
y_i = x_i'β + u_i + e_i        u_i ~ N(0, σ²_u)     e_i ~ N(0, ψ_i known)
```

β and σ²_u fit by REML. Each state's *direct* DHS estimate is shrunk
toward a regression on the covariate stack (`config.STATE_COVARIATES`),
weighted by `γ_i = σ²_u/(σ²_u+ψ_i)` — a noisy state (small survey
sample) leans on the regression; a well-sampled state stays close to
its own number. MSE via the standard Prasad-Rao / Datta-Lahiri (REML)
three-term approximation (Rao & Molina, *Small Area Estimation*, 2nd ed.
2015, §6.2/§7.1).

**Stage 2 — synthetic regression to LGA**: the same β applied to each
LGA's own covariates, then benchmarked (additive shift) so the
population-weighted mean of a state's LGAs equals that state's Stage-1
number. The state figure stays authoritative; covariates only
redistribute it within the state.

## What this is not

- **Not unit-level SAE.** There is no LGA-local survey signal in Stage
  2 — only what the covariate surface predicts. `sae_lga.se_floor` is
  the *parent state's* Stage-1 standard error, a documented **lower
  bound**: true LGA uncertainty is higher by an amount the covariates
  can't capture. Swapping in DHS/MICS microdata + GPS replaces Stage 2
  with a real unit-level model (area random effects at ward/LGA,
  fit on the actual clusters) — same output shape, better numbers.
- **Not a design-based sampling error**, where the DHS API doesn't
  publish a CI (~87% of cells). `ψ_i` falls back to
  `DEFF · p(1-p)/n` with a fixed `DEFAULT_DEFF = 2.0` — a documented,
  literature-typical approximation (see `config.py`), not the survey's
  actual Taylor-linearised SE. Replace once microdata gives real SEs.
- **Percentage/prevalence indicators only.** Mortality rates
  (`unit == "rate_1000"`) need a Poisson/person-years variance model,
  not the binomial one used here — `run.eligible_indicators()` excludes
  them on purpose rather than silently misapplying this model.

## Run it

```bash
cd platform/model
uv sync
uv run sae ready                          # which indicators are fittable
uv run sae fit child_stunting --survey NG2024DHS      # one, printed
uv run sae build --survey NG2024DHS       # every eligible indicator -> parquet
uv run sae check
uv run pytest                             # synthetic-data math tests always run;
                                           # real-data integration tests skip
                                           # cleanly if survey/covariates aren't built
```

Outputs: `data/model/fh_state.parquet` (state, direct vs. FH, γ, SE, CI)
and `data/model/sae_lga.parquet` (all 774 LGAs, estimate + CI floor),
long over every built (indicator, survey) pair — `build` replaces only
the pairs it just ran, keeping everything else.

## Verifying it (don't skip this)

`sae check` recomputes the population-weighted mean of every state's
LGAs from the persisted output and compares it to that state's Stage-1
figure — reconciliation isn't assumed, it's checked on every build. Two
real bugs only showed up this way and are worth knowing about:

- **Clipping broke calibration at the boundary.** An early version
  added the benchmarking shift on the raw percentage scale, then
  clipped to [0,100] — for a state with an already-high or -low figure,
  clipping the LGAs that got pushed past the edge silently changed the
  weighted mean without changing the target. Fixed by calibrating on
  the logit scale instead (`disaggregate.py`), which can't leave
  (0,100) by construction, so nothing is ever clipped.
- **A merge-then-index misalignment.** Population weights were computed
  before a `pandas.merge` that resets row order, then indexed into with
  positions computed *after* it — correct for any state the merge
  happened not to reorder, silently wrong for the rest. Fixed by
  computing weights after the merge, and is exactly why `sae check`
  verifies every state's reconciliation rather than spot-checking one.
- **A joint-extreme extrapolation.** Winsorizing each covariate bounds
  any *one* input, but a few moderately-extreme covariates can still
  sum to a linear predictor no real place would produce — an urban LGA
  came out predicted at exactly 0.0% stunting. Fixed by also bounding
  the predicted logit to Nigeria's own most extreme *state* direct
  estimate, plus a margin — an LGA can plausibly beat every state's
  number a little, not be pinned at a probability of literally zero.

## Reading `psi_method`

`api_ci` — DHS published a CI for this cell, used directly.
`deff_approx` — no CI; approximated from the unweighted N. `unavailable`
— no N either; that state/indicator/round is dropped from the fit
(rare — see `sae check`'s "<700 LGAs" warning if it happens a lot).
