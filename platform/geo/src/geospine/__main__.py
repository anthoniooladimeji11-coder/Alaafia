"""geospine CLI.

  geospine fetch [--force] [--big]     download raw sources
  geospine build                        build geo_unit / geo_alias / geo_source_meta
  geospine crosswalk dhs                build the DHS → canonical crosswalk
  geospine resolve NAME [--level L] [--parent PCODE]
  geospine locate LON LAT
  geospine check                        integrity report on the built spine
"""

from __future__ import annotations

import json

import typer

app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def fetch(
    keys: list[str] = typer.Argument(None, help="specific source keys; default = the standard set"),
    force: bool = False,
    big: bool = typer.Option(False, help="also fetch large sources a build step needs (settlement extents)"),
):
    from .fetch import fetch_all

    print("fetching sources …")
    fetch_all(force=force, big=big, only=list(keys) if keys else None)


@app.command()
def build():
    from .build import build as _b

    r = _b()
    print(json.dumps(r, indent=2, default=str))


@app.command()
def crosswalk(which: str):
    if which != "dhs":
        raise typer.BadParameter("only 'dhs' is implemented")
    from .crosswalks.dhs import build as _b

    print(json.dumps(_b(), indent=2, default=str))


@app.command()
def facilities():
    """Geocode the GRID3 health-facility layer onto the spine."""
    from .facilities import build as _b

    print(json.dumps(_b(), indent=2, default=str))


@app.command()
def settlements(refresh: bool = typer.Option(False, help="redo the ~7-min geocode instead of using the checkpoint")):
    """Build the level-4 settlement layer (needs `fetch --big`)."""
    from .settlements import build as _b

    print(json.dumps(_b(refresh=refresh), indent=2, default=str))


@app.command()
def resolve(name: str, level: int = 1, parent: str = typer.Option(None)):
    from .resolve import NameResolver

    m = NameResolver(level=level, parent_pcode=parent).resolve(name)
    print(json.dumps(m.__dict__, indent=2, default=str))


@app.command()
def locate(lon: float, lat: float):
    from .resolve import PointResolver

    print(json.dumps(PointResolver().locate(lon, lat), indent=2))


@app.command()
def check():
    import duckdb

    from . import config

    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    q = con.execute
    report = {
        "by_level": q(
            "SELECT level_name, source, count(*) n FROM geo_unit "
            "GROUP BY 1,2 ORDER BY 1,2"
        ).fetchall(),
        "dup_pcodes": q(
            "SELECT count(*) FROM (SELECT pcode FROM geo_unit GROUP BY 1 HAVING count(*)>1)"
        ).fetchone()[0],
        "orphans": q(
            "SELECT count(*) FROM geo_unit c LEFT JOIN geo_unit p "
            "ON c.parent_pcode = p.pcode WHERE c.level>0 AND p.pcode IS NULL"
        ).fetchone()[0],
        "centroid_out_of_bbox": q(
            "SELECT count(*) FROM geo_unit WHERE center_lon IS NOT NULL AND "
            f"NOT (center_lon BETWEEN {config.NG_BBOX[0]} AND {config.NG_BBOX[2]} "
            f"AND center_lat BETWEEN {config.NG_BBOX[1]} AND {config.NG_BBOX[3]})"
        ).fetchone()[0],
        "aliases": q("SELECT count(*) FROM geo_alias").fetchone()[0],
    }
    con.close()
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    app()
