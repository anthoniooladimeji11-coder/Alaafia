"""Shared fixtures. The build/resolve/crosswalk tests need a built spine; they
skip (rather than fail) if `geospine build` hasn't been run yet."""

import duckdb
import pytest

from geospine import config


def _has_spine() -> bool:
    if not config.DUCKDB_PATH.exists():
        return False
    try:
        con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
        n = con.execute("SELECT count(*) FROM geo_unit").fetchone()[0]
        con.close()
        return n > 0
    except Exception:
        return False


@pytest.fixture(scope="session")
def spine():
    if not _has_spine():
        pytest.skip("spine not built — run `uv run geospine fetch && uv run geospine build`")
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    yield con
    con.close()
