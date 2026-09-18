import duckdb
import pytest

from geospine import config


@pytest.fixture(scope="session")
def dhs_cw(spine):
    if not config.CROSSWALK_DHS_PARQUET.exists():
        pytest.skip("run `uv run geospine crosswalk dhs`")
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    rows = con.execute("SELECT * FROM crosswalk_dhs").fetchdf()
    con.close()
    return rows


def test_all_37_states_resolved(dhs_cw):
    s = dhs_cw[dhs_cw.dhs_scheme == "sstate"]
    assert len(s) == 37
    assert s.pcode.notna().all(), list(s[s.pcode.isna()].dhs_label)


def test_state_codes_are_1_to_37(dhs_cw):
    s = dhs_cw[dhs_cw.dhs_scheme == "sstate"]
    assert sorted(s.dhs_code) == list(range(1, 38))


def test_pcodes_are_distinct(dhs_cw):
    s = dhs_cw[dhs_cw.dhs_scheme == "sstate"]
    assert s.pcode.nunique() == 37


def test_six_zones(dhs_cw):
    z = dhs_cw[dhs_cw.dhs_scheme == "v024"]
    assert len(z) == 6


def test_fct_maps(dhs_cw):
    row = dhs_cw[(dhs_cw.dhs_scheme == "sstate") & (dhs_cw.dhs_code == 14)].iloc[0]
    assert "capital" in row.canonical_name.lower()
