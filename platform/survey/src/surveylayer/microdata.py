"""Cluster-level indicator rates computed from raw DHS recode microdata.

Different animal from dhs_api.py/build.py: those pull ALREADY-PUBLISHED
state-level estimates from the DHS API. This reads the RAW respondent-level
recode files (data/raw/microdata/, gitignored, analyse-only — see the
package README) and computes weighted cluster-level rates: the unit-level
input the real small-area model fits on, joined to geo_dhs_cluster
(platform/geo — place) and covariates_lga (platform/covariates — context).

Scoped to the 4 rounds where child anthropometry lives directly in KR with a
uniform schema (hw70/71/72 + v001 + v005 + b5 + hw1 all present): 2008,
2013, 2018, 2024. 1990 and 2003 keep it in a separate HW file linked by
hwcaseid/hwline rather than v001/v005 — a different, unverified join,
deliberately left out here rather than guessed at.

Output is long, like every other indicator table in this project
(survey_indicator.parquet, fh_state.parquet): one row per
(slug, survey_round, cluster_id), not one file per indicator — adding the
next indicator means adding a dict entry, not a new near-duplicate function.
Carries both the weighted rate and the raw unweighted n — same "don't hide
the sample size" standard the API-sourced series already holds itself to
(see __main__.py's `check`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

UNIFORM_ROUNDS = ["NG2008DHS", "NG2013DHS", "NG2018DHS", "NG2024DHS"]

# slug -> KR z-score column. All three are WHO Child Growth Standards
# z-scores, "< -2.00 SD" by the same universal convention, differing only
# in which measurement the z-score is computed against. Flag/plausible-range
# convention verified empirically to be identical across all three (9996/9998
# sentinels; real values always within +/-600) — not assumed from memory.
#
# hw71/hw72 are deliberately NOT in DHS's usual "71=WHZ, 72=WAZ" ordering —
# checked directly against the variable labels DHS shipped in each round's
# own .DO file (consistent across 2008/2013/2018/2024): hw71 is Weight/Age,
# hw72 is Weight/Height. Getting this backwards doesn't error, it just
# quietly swaps two indicators' numbers — caught here by the national
# aggregate landing nowhere near Nigeria's actual published rates (wasting
# at ~25% instead of ~7%) before this was trusted.
NUTRITION_INDICATORS: dict[str, str] = {
    "child_stunting": "hw70",       # Height/Age (HAZ)
    "child_wasting": "hw72",        # Weight/Height (WHZ)
    "child_underweight": "hw71",    # Weight/Age (WAZ)
}


def _kr_path(round_label: str) -> Path:
    d = config.MICRODATA / round_label / "KR"
    return next(p for p in d.iterdir() if p.suffix.lower() == ".dta")


def cluster_zscore_rate(round_label: str, hw_col: str) -> pd.DataFrame:
    """Weighted rate of `hw_col` < -2.00 SD per cluster, among children
    0-59 months with a plausible measurement (DHS standard: within
    +/-6.00 SD — outside that range, or the 9996-9999 sentinel codes,
    means flagged/not-measured, excluded by the same bound, not a
    separate rule)."""
    df = pd.read_stata(
        _kr_path(round_label), convert_categoricals=False,
        columns=["v001", "v005", "b5", "hw1", hw_col],
    )
    valid = (df.b5 == 1) & df.hw1.between(0, 59) & df[hw_col].between(-600, 600)
    d = df.loc[valid, ["v001", "v005", hw_col]].copy()
    d["weight"] = d.v005 / 1_000_000
    d["affected"] = (d[hw_col] < -200).astype(float)
    d["w_affected"] = d.weight * d.affected

    g = d.groupby("v001").agg(
        n_children=("affected", "size"),
        n_affected=("affected", "sum"),
        weight_sum=("weight", "sum"),
        w_affected_sum=("w_affected", "sum"),
    )
    g["rate"] = g.w_affected_sum / g.weight_sum
    # weight_sum carried through (not just n_children): pooling clusters up to
    # LGA level needs each cluster's total survey weight, not its raw count —
    # the two track closely but aren't identical, and the whole point of
    # using v005 at all is to not approximate where the real number is sitting
    # right there.
    out = g[["n_children", "n_affected", "weight_sum", "rate"]].reset_index()
    out = out.rename(columns={"v001": "cluster_id"})
    out["n_affected"] = out["n_affected"].astype(int)
    out.insert(0, "survey_round", round_label)
    return out


def build() -> dict:
    frames = []
    for slug, hw_col in NUTRITION_INDICATORS.items():
        for r in UNIFORM_ROUNDS:
            f = cluster_zscore_rate(r, hw_col)
            f.insert(1, "slug", slug)
            frames.append(f)
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

    out_path = config.OUT / "cluster_nutrition.parquet"
    df.to_parquet(out_path, index=False)

    by_slug = (
        df.groupby("slug", sort=False)
        .agg(clusters=("cluster_id", "size"),
             children=("n_children", "sum"),
             with_lga=("lga_pcode", lambda s: int(s.notna().sum())),
             low_confidence=("low_confidence", "sum"))
        .to_dict("index")
    )
    return {
        "rows": len(df),
        "slugs": list(NUTRITION_INDICATORS),
        "with_lga": int(df.lga_pcode.notna().sum()),
        "with_covariates": int(df["pop_density_km2"].notna().sum()),
        "by_slug": by_slug,
        "parquet": str(out_path),
    }
