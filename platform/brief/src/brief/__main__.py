"""brief CLI."""

from __future__ import annotations

import typer

from .config import OUT
from .data import build_profile, list_states
from .render import render

app = typer.Typer(add_completion=False, help="Àlááfìa brief generator")


@app.command()
def states():
    """List state pcodes to generate a brief for."""
    for _, r in list_states().iterrows():
        typer.echo(f"  {r.pcode}  {r['name']}")


@app.command()
def generate(pcode: str, survey: str = typer.Option(None, "--survey")):
    """Build one state's brief -> build/<pcode>.html."""
    p = build_profile(pcode, survey_id=survey)
    html = render(p)
    out = OUT / f"{pcode}.html"
    out.write_text(html)
    typer.secho(f"  {out}  ({len(html)/1024:.0f} KB) — {p.state_name}, "
               f"{len(p.rows)} indicators, {len(p.concerns)} concerns, "
               f"{len(p.strengths)} strengths", fg="green")


@app.command()
def generate_all(survey: str = typer.Option(None, "--survey")):
    """Build every state's brief."""
    for _, r in list_states().iterrows():
        p = build_profile(r.pcode, survey_id=survey)
        (OUT / f"{r.pcode}.html").write_text(render(p))
    typer.secho(f"  wrote {len(list_states())} briefs to {OUT}/", fg="green")


if __name__ == "__main__":
    app()
