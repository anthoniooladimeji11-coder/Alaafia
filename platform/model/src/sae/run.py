"""Orchestration: fit + disaggregate one or every eligible indicator."""

from __future__ import annotations

import duckdb
import pandas as pd

from . import fayherriot as fh
from .config import (
    DUCKDB, FH_STATE_PARQUET, INDICATOR_META_PARQUET, SAE_LGA_PARQUET, SURVEY_SERIES,
)
from .direction import classify
from .disaggregate import disaggregate


def run_one(slug: str, survey_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    fit_ = fh.fit(slug, survey_id)
    state_df = fh.estimate(fit_)
    lga_df = disaggregate(fit_, state_df)
    return state_df, lga_df


def eligible_indicators() -> pd.DataFrame:
    """Indicators this model can honestly touch: percentages, prevalences,
    and per-1,000 rates (mortality) — every unit `fayherriot.sampling_variance`
    and `disaggregate._link_pair` know how to handle. Anything else is left
    out on purpose rather than silently misapplied."""
    series = pd.read_parquet(SURVEY_SERIES)
    return series[series.unit.isin(["pct", "prev_pct", "rate_1000"])]


def run_all(survey_id: str, *, slugs: list[str] | None = None) -> dict:
    todo = eligible_indicators().slug.tolist() if slugs is None else slugs
    states, lgas, ok, failed = [], [], [], []
    for slug in todo:
        try:
            s, l = run_one(slug, survey_id)
            states.append(s); lgas.append(l); ok.append(slug)
        except ValueError as e:
            failed.append((slug, str(e)))

    fh_state = pd.concat(states, ignore_index=True) if states else pd.DataFrame()
    sae_lga = pd.concat(lgas, ignore_index=True) if lgas else pd.DataFrame()
    if len(fh_state):
        prior = pd.read_parquet(FH_STATE_PARQUET) if FH_STATE_PARQUET.exists() else pd.DataFrame()
        if len(prior):
            prior = prior[~((prior.survey_id == survey_id) & prior.slug.isin(ok))]
        pd.concat([prior, fh_state], ignore_index=True).to_parquet(FH_STATE_PARQUET, index=False)

        prior_l = pd.read_parquet(SAE_LGA_PARQUET) if SAE_LGA_PARQUET.exists() else pd.DataFrame()
        if len(prior_l):
            prior_l = prior_l[~((prior_l.survey_id == survey_id) & prior_l.slug.isin(ok))]
        pd.concat([prior_l, sae_lga], ignore_index=True).to_parquet(SAE_LGA_PARQUET, index=False)

        con = duckdb.connect(str(DUCKDB))
        con.execute(f"CREATE OR REPLACE VIEW fh_state AS SELECT * FROM read_parquet('{FH_STATE_PARQUET}')")
        con.execute(f"CREATE OR REPLACE VIEW sae_lga AS SELECT * FROM read_parquet('{SAE_LGA_PARQUET}')")
        con.close()

        # one row per indicator ever built (across all persisted survey rounds),
        # the shared "does high mean good or bad" answer for every downstream
        # consumer (the explorer, the brief generator) to read rather than guess.
        built = pd.read_parquet(FH_STATE_PARQUET, columns=["slug"]).slug.unique()
        series = pd.read_parquet(SURVEY_SERIES)
        meta = series[series.slug.isin(built)].copy()
        worse_high = classify(set(meta.slug))
        meta["worse_high"] = meta.slug.map(worse_high)
        meta[["slug", "domain", "unit", "indicator_label", "worse_high",
             "n_surveys", "first_year", "last_year"]].to_parquet(
            INDICATOR_META_PARQUET, index=False)

    return {"survey_id": survey_id, "fit": ok, "skipped": failed,
            "state_rows": len(fh_state), "lga_rows": len(sae_lga)}
