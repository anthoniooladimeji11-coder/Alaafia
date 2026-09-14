"""surveylayer CLI."""

from __future__ import annotations

import json

import duckdb
import typer

from . import dhs_api
from .build import build as _build
from .config import DUCKDB, INDICATOR_PARQUET
from .indicators import IDS

app = typer.Typer(add_completion=False, help="Àlááfìa survey layer")


@app.command()
def surveys():
    """List the Nigeria surveys the DHS API exposes."""
    for s in sorted(dhs_api.surveys(), key=lambda x: x["SurveyYear"]):
        typer.echo(f"  {s['SurveyId']:<12} {s['SurveyYear']}  {s['SurveyType']}")


@app.command()
def fetch(force: bool = typer.Option(False, help="re-hit the network")):
    """Download the raw DHS API pages into the cache."""
    p = dhs_api.fetch_data(IDS, force=force)
    man = json.loads(p.with_name(p.stem + "._manifest.json").read_text())
    typer.echo(f"cached {man['rows']} rows -> {p.name}  ({man['retrieved_at']})")


@app.command()
def build(force_fetch: bool = typer.Option(False, help="re-download first")):
    """Assemble survey_indicator.parquet + series dict + duckdb."""
    r = _build(force_fetch=force_fetch)
    typer.echo(f"rows={r['rows']}  indicators={r['indicators']}  "
               f"state_rows={r['state_rows']}")
    typer.echo("surveys: " + ", ".join(r["surveys"]))
    if r["unresolved"]:
        typer.secho(f"UNRESOLVED geography: {r['unresolved']}", fg="yellow")
    else:
        typer.secho("all geography resolved to the spine", fg="green")


@app.command()
def query(sql: str = typer.Argument(..., help="SQL over survey_indicator / survey_series")):
    """Run SQL against the built tables (read-only, in-memory)."""
    from .config import SERIES_PARQUET
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE VIEW survey_indicator AS SELECT * FROM read_parquet('{INDICATOR_PARQUET}')")
    con.execute(f"CREATE VIEW survey_series AS SELECT * FROM read_parquet('{SERIES_PARQUET}')")
    typer.echo(con.sql(sql))


@app.command()
def check():
    """Sanity checks on the built table."""
    import pandas as pd
    df = pd.read_parquet(INDICATOR_PARQUET)
    bad = []
    if df.duplicated(["indicator_id", "survey_id", "geo_pcode", "geo_name"]).any():
        bad.append("duplicate (indicator, survey, geo) keys")
    if (df["value"].dropna() < 0).any():
        bad.append("negative values")
    pct = df[df.unit.isin(["pct", "prev_pct"])]["value"].dropna()
    if (pct > 100).any():
        bad.append("percentages over 100")
    natl = df[df.geo_level == "national"]
    if natl.empty:
        bad.append("no national rows")
    for b in bad:
        typer.secho(f"  FAIL {b}", fg="red")
    if not bad:
        typer.secho(f"  ok — {len(df)} rows, {df.indicator_id.nunique()} indicators, "
                    f"{df.survey_id.nunique()} surveys", fg="green")

    # informational: where subnational coverage is thin
    st = df[df.geo_level == "state"]
    thin = (st.groupby("slug").geo_pcode.nunique()
              .pipe(lambda s: s[s < 37]).sort_values())
    if len(thin):
        typer.secho("  note — indicators with <37 states in some/all rounds:", fg="yellow")
        for slug, n in thin.items():
            yrs = sorted(int(y) for y in st[st.slug == slug].survey_year.unique())
            typer.echo(f"      {slug:<20} max {int(n)} states · rounds {yrs}")
    ci = df.ci_low.notna().mean()
    typer.echo(f"  CIs present on {ci:.0%} of rows; "
               f"{df.denom_unweighted.notna().mean():.0%} carry an unweighted N")


if __name__ == "__main__":
    app()
