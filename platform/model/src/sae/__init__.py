"""Àlááfìa small-area estimation.

MODEL step: INGEST (survey) + covariates -> estimates with uncertainty,
calibrated to the official state figures. No microdata needed for this
first pass — that's the point: it proves the method on public API data,
and slots in a proper unit-level model later without changing the shape
of the output.

Two stages, one indicator/survey at a time:

  1. Area-level Fay–Herriot (`fayherriot.py`) on the 37 states. Shrinks
     each state's direct DHS estimate toward a regression on the
     covariate stack, weighted by how noisy that state's own estimate
     is. Output: a smoothed state estimate + an honest MSE for every
     state, including ones a given survey round didn't sample well.

  2. Synthetic regression to the 774 LGAs (`disaggregate.py`): the same
     fitted regression applied to LGA-level covariates, then calibrated
     so population-weighted LGA estimates reconcile to each state's FH
     number. This is explicitly a *synthetic* estimate — no LGA-local
     survey signal, just "what the covariates predict" — and is labelled
     that way in the output. Swapping in unit-level microdata later
     replaces this stage, not the interface.
"""

__version__ = "0.1.0"
