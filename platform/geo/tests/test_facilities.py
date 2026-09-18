import duckdb
import pytest

from geospine import config


@pytest.fixture(scope="session")
def fac(spine):
    if not (config.SPINE / "geo_facility.parquet").exists():
        pytest.skip("run `uv run geospine facilities`")
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    df = con.execute("SELECT * FROM geo_facility").fetchdf()
    con.close()
    return df


def test_all_facilities_have_state_and_lga(fac):
    assert fac.state_pcode.notna().all()
    assert fac.lga_pcode.notna().all()


def test_most_facilities_geocode_to_ward(fac):
    # GRID3 v3.0 standardised ward names → our GRID3-minted wards should match well
    assert fac.ward_pcode.notna().mean() > 0.95


def test_lga_pcode_is_child_of_state(fac, spine):
    j = spine.execute(
        "SELECT f.lga_pcode, u.adm1_pcode FROM geo_facility f "
        "JOIN geo_unit u ON f.lga_pcode = u.pcode WHERE u.level=2"
    ).fetchdf()
    assert (j.lga_pcode.str[:5] == j.adm1_pcode).all()


def test_point_and_name_ward_mostly_agree(fac):
    both = fac[fac.ward_pcode.notna() & fac.ward_pcode_pt.notna()]
    assert (both.ward_pcode == both.ward_pcode_pt).mean() > 0.7
