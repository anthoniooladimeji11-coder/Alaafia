"""covariates CLI."""

from __future__ import annotations

import duckdb
import typer

from .build_lga import build as _build
from .config import DICT_PARQUET, LGA_PARQUET

app = typer.Typer(add_completion=False, help="Àlááfìa covariate stack")
worldpop_app = typer.Typer(add_completion=False, help="Tier B — WorldPop population")
app.add_typer(worldpop_app, name="worldpop")


@app.command()
def build():
    """Tier A — build covariates_lga.parquet from repo data (no downloads)."""
    r = _build()
    typer.echo(f"lgas={r['lgas']}  covariates={r['covariates']}  "
               f"facility_states={r['facility_states']}  ward_states={r['ward_states']}")
    if r["null_counts"]:
        typer.secho("  nulls (expected in non-covered states): "
                    + ", ".join(f"{k}={v}" for k, v in r["null_counts"].items()), fg="yellow")
    else:
        typer.secho("  no nulls", fg="green")


@app.command()
def check():
    """Integrity checks."""
    import pandas as pd
    lga = pd.read_parquet(LGA_PARQUET)
    d = pd.read_parquet(DICT_PARQUET)
    bad = []
    if len(lga) != 774:
        bad.append(f"expected 774 LGAs, got {len(lga)}")
    if lga.lga_pcode.duplicated().any():
        bad.append("duplicate lga_pcode")
    always = d[d.coverage == "all"].name.tolist()
    miss = [c for c in always if lga[c].isna().any()]
    if miss:
        bad.append(f"nulls in always-on covariates: {miss}")
    for c in ("builtup_fraction", "builtup_core_share", "nonhamlet_area_share",
              "pct_fac_functional", "pct_fac_public", "pct_fac_referral"):
        v = lga[c].dropna()
        if len(v) and (v.lt(-1e-6).any() or v.gt(1 + 1e-6).any()):
            bad.append(f"{c} outside [0,1]")
    for c in bad:
        typer.secho(f"  FAIL {c}", fg="red")
    if not bad:
        fac = lga.facility_data.sum()
        typer.secho(f"  ok — {len(lga)} LGAs, {len(d)} covariates; "
                    f"facility cols populated for {fac} LGAs, NaN for {len(lga)-fac}", fg="green")


@app.command()
def query(sql: str = typer.Argument(...)):
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE VIEW covariates_lga AS SELECT * FROM read_parquet('{LGA_PARQUET}')")
    con.execute(f"CREATE VIEW covariates_dict AS SELECT * FROM read_parquet('{DICT_PARQUET}')")
    typer.echo(con.sql(sql))


@worldpop_app.command("fetch")
def wp_fetch(only_total: bool = typer.Option(False, "--only-total"),
            force: bool = typer.Option(False)):
    from .worldpop import fetch
    fetch(only_total=only_total, force=force)


@worldpop_app.command("zonal")
def wp_zonal():
    from .worldpop import zonal
    r = zonal()
    typer.secho(f"  merged WorldPop -> {r['lgas']} LGAs; added {r['added']}", fg="green")


if __name__ == "__main__":
    app()
