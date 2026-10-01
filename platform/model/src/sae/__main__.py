"""sae CLI."""

from __future__ import annotations

import duckdb
import numpy as np
import typer

from .config import COV_LGA, FH_STATE_PARQUET, SAE_LGA_PARQUET
from .run import eligible_indicators, run_all, run_one

app = typer.Typer(add_completion=False, help="Àlááfìa small-area estimation")


@app.command()
def ready():
    """Indicators this model can fit (percentage, prevalence, or per-1,000 rate)."""
    for _, r in eligible_indicators().iterrows():
        typer.echo(f"  {r.slug:<22} {r.domain:<14} rounds {r.first_year}-{r.last_year}"
                   f"  n_state_obs(any round)={r.n_state_obs}")


@app.command()
def fit(slug: str, survey: str = typer.Option(..., "--survey", help="e.g. NG2024DHS")):
    """Fit + disaggregate one indicator; print the state table."""
    state_df, lga_df = run_one(slug, survey)
    import pandas as pd
    pd.set_option("display.width", 140)
    typer.echo(state_df[["state_name", "direct", "fh_estimate", "fh_se", "gamma",
                         "psi_method"]].sort_values("fh_estimate").to_string(index=False))
    typer.secho(f"\nsigma_u2 shrinkage fitted; {len(lga_df)} LGA rows produced "
               f"(not saved — run `sae build` to persist).", fg="cyan")


@app.command()
def build(survey: str = typer.Option(..., "--survey"),
          slug: list[str] = typer.Option(None, "--slug", help="repeatable; default = all eligible")):
    """Fit + disaggregate every eligible indicator (or a chosen subset), persist parquet."""
    r = run_all(survey, slugs=slug or None)
    typer.secho(f"fit {len(r['fit'])}: {', '.join(r['fit'])}", fg="green")
    if r["skipped"]:
        typer.secho(f"skipped {len(r['skipped'])}:", fg="yellow")
        for slug_, why in r["skipped"]:
            typer.echo(f"    {slug_}: {why}")
    typer.echo(f"state_rows={r['state_rows']}  lga_rows={r['lga_rows']}")


@app.command()
def check():
    """Sanity checks on the persisted model output."""
    import pandas as pd
    if not FH_STATE_PARQUET.exists():
        typer.secho("nothing built yet — run `sae build --survey NG2024DHS`", fg="yellow")
        raise typer.Exit(1)
    st, lga = pd.read_parquet(FH_STATE_PARQUET), pd.read_parquet(SAE_LGA_PARQUET)
    bad, notes = [], []
    # pct/prev_pct are bounded both sides; rate_1000 only below, at 0 — a
    # mortality rate legitimately running into the hundreds isn't a bug.
    pct = st.unit.isin(["pct", "prev_pct"])
    if not st.fh_estimate.ge(0).all() or not st.loc[pct, "fh_estimate"].le(100).all():
        bad.append("fh_estimate outside its natural range")
    pct_l = lga.unit.isin(["pct", "prev_pct"])
    if not lga.estimate.ge(0).all() or not lga.loc[pct_l, "estimate"].le(100).all():
        bad.append("lga estimate outside its natural range")
    if not st.loc[~pct, "fh_estimate"].le(500).all():
        bad.append("a rate_1000 estimate exceeds 500/1,000 — check for a fit blow-up")
    if (st.fh_se <= 0).any():
        bad.append("non-positive fh_se")

    # LGA count should track the state count that indicator/round actually
    # fit with (fewer states -> fewer LGAs, by design, via the inner join
    # in disaggregate()) — flag only a *disproportionate* LGA loss, which
    # would point at a real covariate-join bug rather than known-thin
    # survey coverage.
    n_state = st.groupby(["slug", "survey_id"]).state_pcode.nunique()
    n_lga = lga.groupby(["slug", "survey_id"]).lga_pcode.nunique()
    expect = (n_state / 37 * 774)
    for key, got in n_lga.items():
        if got < 0.9 * expect[key]:
            bad.append(f"{key}: {got} LGAs, expected ~{expect[key]:.0f} for "
                      f"{n_state[key]}/37 states fit")
        elif n_state[key] < 37:
            notes.append(f"{key}: {n_state[key]}/37 states (survey coverage, not a bug) "
                        f"-> {got} LGAs")

    # reconciliation: population-weighted LGA mean should equal the state FH figure
    cov = pd.read_parquet(COV_LGA, columns=["lga_pcode", "pop_2020"])
    m = lga.merge(cov, on="lga_pcode")
    recon = (m.assign(w=m.pop_2020.fillna(1.0))
              .groupby(["slug", "survey_id", "state_pcode"])
              .apply(lambda g: np.average(g.estimate, weights=g.w), include_groups=False))
    target = st.set_index(["slug", "survey_id", "state_pcode"]).fh_estimate
    gap = (recon - target.reindex(recon.index)).abs()
    if gap.max() > 0.5:
        bad.append(f"disaggregation doesn't reconcile to the state figure "
                  f"(max gap {gap.max():.2f} pts)")

    for b in bad:
        typer.secho(f"  FAIL {b}", fg="red")
    if not bad:
        typer.secho(f"  ok — {st.slug.nunique()} indicators, {len(st)} state rows, "
                    f"{len(lga)} LGA rows; median gamma={st.gamma.median():.2f}; "
                    f"max reconciliation gap {gap.max():.4f} pts", fg="green")
    for n in notes:
        typer.secho(f"  note {n}", fg="yellow")


@app.command(name="unit-fit")
def unit_fit(slug: str, survey: str = typer.Option("NG2024DHS", "--survey")):
    """Unit-level model for one indicator, from real DHS cluster microdata —
    separate from `build`/`fit`, which still only know the state-level,
    API-sourced pipeline. Prints a comparison against the existing synthetic
    Stage-2 output for the same indicator/survey, where both exist. Does not
    persist — use `unit-build` for that."""
    import pandas as pd

    from . import unit_level as ul
    from .config import SAE_LGA_PARQUET

    fit_ = ul.fit(slug, survey)
    out = ul.estimate(fit_)

    typer.secho(f"{fit_.n_lgas} LGAs with direct cluster data (of 774); "
               f"sigma_u2={fit_.sigma_u2:.1f}", fg="cyan")
    typer.echo(out.method.value_counts().to_string())
    if fit_.weak_signal:
        typer.secho(f"  WEAK SIGNAL: between-LGA variance is negligible next to sampling "
                   f"noise for {slug} — estimates will barely vary by LGA regardless of "
                   f"each one's own direct data. Not a bug; this indicator doesn't yet "
                   f"support real LGA differentiation at this sample size.", fg="yellow")

    if SAE_LGA_PARQUET.exists():
        old = pd.read_parquet(SAE_LGA_PARQUET)
        old = old[(old.slug == slug) & (old.survey_id == survey)][
            ["lga_pcode", "estimate", "se_floor"]
        ].rename(columns={"estimate": "old_estimate", "se_floor": "old_se"})
        if len(old):
            cmp = out.merge(old, on="lga_pcode")
            typer.echo(f"\nvs existing Stage-2 synthetic ({len(cmp)} LGAs matched):")
            typer.echo(f"  corr={cmp.estimate.corr(cmp.old_estimate):.3f}  "
                       f"mean|diff|={abs(cmp.estimate - cmp.old_estimate).mean():.1f}pp")
            typer.echo(cmp.groupby("method")[["se", "old_se"]].mean().to_string())


@app.command(name="unit-build")
def unit_build(survey: str = typer.Option("NG2024DHS", "--survey"),
              slug: list[str] = typer.Option(None, "--slug", help="repeatable; default = all available")):
    """Fit + estimate every unit-level indicator available in
    cluster_nutrition.parquet (or a chosen subset), persist to
    unit_lga.parquet."""
    from . import unit_level as ul

    r = ul.run_all(survey, slugs=slug or None)
    typer.secho(f"fit {len(r['fit'])}: {', '.join(r['fit'])}", fg="green")
    if r["weak_signal"]:
        typer.secho(f"  weak signal (negligible between-LGA variance vs sampling noise): "
                   f"{', '.join(r['weak_signal'])}", fg="yellow")
    if r["skipped"]:
        typer.secho(f"skipped {len(r['skipped'])}:", fg="yellow")
        for slug_, why in r["skipped"]:
            typer.echo(f"    {slug_}: {why}")
    typer.echo(f"rows={r['rows']}")


@app.command()
def query(sql: str = typer.Argument(...)):
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE VIEW fh_state AS SELECT * FROM read_parquet('{FH_STATE_PARQUET}')")
    con.execute(f"CREATE VIEW sae_lga AS SELECT * FROM read_parquet('{SAE_LGA_PARQUET}')")
    typer.echo(con.sql(sql))


if __name__ == "__main__":
    app()
