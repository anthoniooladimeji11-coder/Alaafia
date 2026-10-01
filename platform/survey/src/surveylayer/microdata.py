"""Cluster-level indicator rates computed from raw DHS recode microdata.

Different animal from dhs_api.py/build.py: those pull ALREADY-PUBLISHED
state-level estimates from the DHS API. This reads the RAW respondent-level
recode files (data/raw/microdata/, gitignored, analyse-only — see the
package README) and computes weighted cluster-level rates: the unit-level
input the real small-area model fits on, joined to geo_dhs_cluster
(platform/geo — place) and covariates_lga (platform/covariates — context).

Scoped to the 4 rounds where child anthropometry lives directly in KR with a
uniform schema (hw70 + v001 + v005 + b5 + hw1 all present): 2008, 2013,
2018, 2024. 1990 and 2003 keep it in a separate HW file linked by
hwcaseid/hwline rather than v001/v005 — a different, unverified join,
deliberately left out here rather than guessed at.

Each extractor returns one row per cluster, carrying both the weighted rate
and the raw unweighted n — same "don't hide the sample size" standard the
API-sourced series already holds itself to (see __main__.py's `check`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

UNIFORM_ROUNDS = ["NG2008DHS", "NG2013DHS", "NG2018DHS", "NG2024DHS"]


def _kr_path(round_label: str) -> Path:
    d = config.MICRODATA / round_label / "KR"
    return next(p for p in d.iterdir() if p.suffix.lower() == ".dta")


def cluster_stunting(round_label: str) -> pd.DataFrame:
    """Weighted child-stunting rate per cluster: HAZ < -2.00 SD among
    children 0-59 months with a plausible z-score. DHS standard plausible
    range is -600..600 (i.e. +/-6.00 SD); the 9996-9999 sentinel codes for
    flagged/not-measured fall well outside it and are excluded by the same
    bound, not a separate rule."""
    df = pd.read_stata(
        _kr_path(round_label), convert_categoricals=False,
        columns=["v001", "v005", "b5", "hw1", "hw70"],
    )
    valid = (df.b5 == 1) & df.hw1.between(0, 59) & df.hw70.between(-600, 600)
    d = df.loc[valid, ["v001", "v005", "hw70"]].copy()
    d["weight"] = d.v005 / 1_000_000
    d["stunted"] = (d.hw70 < -200).astype(float)
    d["w_stunted"] = d.weight * d.stunted

    g = d.groupby("v001").agg(
        n_children=("stunted", "size"),
        n_stunted=("stunted", "sum"),
        weight_sum=("weight", "sum"),
        w_stunted_sum=("w_stunted", "sum"),
    )
    g["stunting_rate"] = g.w_stunted_sum / g.weight_sum
    # weight_sum carried through (not just n_children): pooling clusters up to
    # LGA level needs each cluster's total survey weight, not its raw count —
    # the two track closely but aren't identical, and the whole point of
    # using v005 at all is to not approximate where the real number is sitting
    # right there.
    out = g[["n_children", "n_stunted", "weight_sum", "stunting_rate"]].reset_index()
    out = out.rename(columns={"v001": "cluster_id"})
    out["n_stunted"] = out["n_stunted"].astype(int)
    out.insert(0, "survey_round", round_label)
    return out


def build() -> dict:
    frames = [cluster_stunting(r) for r in UNIFORM_ROUNDS]
    df = pd.concat(frames, ignore_index=True)

    if not config.GEO_DHS_CLUSTER_PARQUET.exists():
        raise FileNotFoundError(
            f"{config.GEO_DHS_CLUSTER_PARQUET} missing — "
            "run `uv run geospine dhs-clusters` in platform/geo first."
        )
    geo = pd.read_parquet(
        config.GEO_DHS_CLUSTER_PARQUET,
        columns=["survey_round", "cluster_id", "state_pcode_pt", "lga_pcode",
                  "urban_rural", "low_confidence"],
    )
    before = len(df)
    df = df.merge(geo, on=["survey_round", "cluster_id"], how="left")
    assert len(df) == before, "geo join changed row count — duplicate cluster keys in geo_dhs_cluster"

    cov = pd.read_parquet(config.COV_LGA_PARQUET)
    df = df.merge(cov, on="lga_pcode", how="left")
    assert len(df) == before, "covariate join changed row count — duplicate lga_pcode in covariates_lga"

    out_path = config.OUT / "cluster_stunting.parquet"
    df.to_parquet(out_path, index=False)

    by_round = (
        df.groupby("survey_round", sort=False)
        .agg(clusters=("cluster_id", "size"),
             children=("n_children", "sum"),
             with_lga=("lga_pcode", lambda s: int(s.notna().sum())),
             low_confidence=("low_confidence", "sum"))
        .to_dict("index")
    )
    return {
        "clusters": len(df),
        "children": int(df.n_children.sum()),
        "with_lga": int(df.lga_pcode.notna().sum()),
        "with_covariates": int(df["pop_density_km2"].notna().sum()),
        "low_confidence": int(df.low_confidence.sum()),
        "by_round": by_round,
        "parquet": str(out_path),
    }
