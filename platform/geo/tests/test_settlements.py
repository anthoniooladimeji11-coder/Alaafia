import duckdb
import pytest

from geospine import config


@pytest.fixture(scope="session")
def sett(spine):
    if not (config.SPINE / "geo_settlement.parquet").exists():
        pytest.skip("run `uv run geospine fetch --big && uv run geospine settlements`")
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    df = con.execute("SELECT * FROM geo_settlement").fetchdf()
    con.close()
    return df


def test_row_count_matches_grid3(sett):
    assert len(sett) == 745191  # GRID3 NGA Settlement Extents v3.1 feature count


def test_almost_all_placed_to_lga_or_better(sett):
    assert (sett.parent_level >= 2).mean() > 0.99


def test_pcodes_unique(sett):
    assert sett.pcode.nunique() == len(sett)


def test_pcode_encodes_parent(sett):
    placed = sett[sett.parent_pcode.notna()]
    assert placed.pcode.str.startswith(tuple(placed.parent_pcode.unique()[:1])).any()
    # every placed pcode is <parent_pcode> + 'S' + 5 digits
    bad = placed[~placed.apply(lambda r: r.pcode == f"{r.parent_pcode}S{r.pcode[-5:]}", axis=1)]
    assert bad.empty


def test_ward_children_have_matching_lga_and_state(sett, spine):
    w = sett[sett.parent_level == 3][["ward_pcode", "lga_pcode", "state_pcode"]].drop_duplicates()
    j = spine.execute(
        "SELECT u.pcode, u.adm2_pcode, u.adm1_pcode FROM geo_unit u WHERE u.level=3"
    ).fetchdf().set_index("pcode")
    m = w.join(j, on="ward_pcode")
    assert (m.lga_pcode == m.adm2_pcode).all()
    assert (m.state_pcode == m.adm1_pcode).all()


def test_types_are_grid3_settlement_classes(sett):
    assert set(sett["type"].dropna().unique()) <= {
        "Hamlet", "Small Settlement Area", "Built-up Area"
    }


def test_centroids_in_country(sett):
    lo, la, hi, ha = config.NG_BBOX
    inb = sett[(sett.center_lon.between(lo, hi)) & (sett.center_lat.between(la, ha))]
    assert len(inb) / len(sett) > 0.999
