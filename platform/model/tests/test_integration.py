"""End-to-end on real data: survey layer + covariates -> one fitted indicator.

Skips cleanly if the sibling packages haven't been built yet.
"""

import numpy as np
import pandas as pd
import pytest

from sae.config import COV_LGA, SURVEY
from sae.disaggregate import disaggregate
from sae.fayherriot import fit, sampling_variance
from sae.run import eligible_indicators

pytestmark = pytest.mark.skipif(
    not (SURVEY.exists() and COV_LGA.exists()),
    reason="survey layer / covariates not built — see their READMEs",
)


def _first_fittable():
    elig = eligible_indicators()
    df = pd.read_parquet(SURVEY)
    for _, row in elig.sort_values("n_state_obs", ascending=False).iterrows():
        rounds = sorted(df[(df.slug == row.slug) & (df.geo_level == "state")]
                        .survey_id.unique(), reverse=True)
        for sid in rounds:
            try:
                return fit(row.slug, sid)
            except ValueError:
                continue
    pytest.skip("no indicator/survey had enough state coverage to fit")


def test_sampling_variance_behaviour():
    psi_ci, m = sampling_variance(30.0, 25.0, 35.0, denom=None)
    assert m == "api_ci" and psi_ci > 0
    psi_deff, m2 = sampling_variance(30.0, None, None, denom=400)
    assert m2 == "deff_approx" and psi_deff > 0
    # smaller sample -> more sampling variance
    psi_small, _ = sampling_variance(30.0, None, None, denom=50)
    assert psi_small > psi_deff
    psi_none, m3 = sampling_variance(30.0, None, None, denom=None)
    assert m3 == "unavailable" and np.isnan(psi_none)


def test_fit_and_estimate_real_indicator():
    from sae.fayherriot import estimate
    fit_ = _first_fittable()
    out = estimate(fit_)
    assert fit_.n_states >= 20
    assert out.fh_estimate.between(0, 100).all()
    assert out.fh_se.gt(0).all()
    assert set(out.state_pcode) == set(fit_.states.state_pcode)


def test_disaggregate_reconciles_to_state():
    from sae.fayherriot import estimate
    fit_ = _first_fittable()
    state_df = estimate(fit_)
    lga_df = disaggregate(fit_, state_df)

    assert lga_df.estimate.between(0, 100).all()
    assert lga_df.lga_pcode.nunique() >= 700            # covariate coverage gaps aside

    cov = pd.read_parquet(COV_LGA, columns=["lga_pcode", "pop_2020"])
    m = lga_df.merge(cov, on="lga_pcode")
    recon = (m.assign(w=m.pop_2020.fillna(1.0))
              .groupby("state_pcode")
              .apply(lambda g: np.average(g.estimate, weights=g.w), include_groups=False))
    check = state_df.set_index("state_pcode").fh_estimate.reindex(recon.index)
    # logit-scale benchmarking (disaggregate.py) makes this exact, not just close —
    # if this drifts, clipping likely crept back into the calibration path.
    assert (recon - check).abs().max() < 0.01
