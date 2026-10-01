import duckdb
import pytest

from geospine import config
from geospine.dhs_clusters import ROUNDS


@pytest.fixture(scope="session")
def clusters(spine):
    if not (config.SPINE / "geo_dhs_cluster.parquet").exists():
        pytest.skip("run `uv run geospine dhs-clusters`")
    con = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    df = con.execute("SELECT * FROM geo_dhs_cluster").fetchdf()
    con.close()
    return df


def test_every_round_present(clusters):
    assert set(clusters.survey_round.unique()) == set(ROUNDS)


def test_cluster_id_unique_within_round(clusters):
    dup = clusters.duplicated(["survey_round", "cluster_id"])
    assert not dup.any()


def test_almost_all_clusters_geocode_to_lga(clusters):
    assert clusters.lga_pcode.notna().mean() > 0.99


def test_lga_pcode_is_child_of_point_state(clusters, spine):
    j = spine.execute(
        "SELECT c.lga_pcode, u.adm1_pcode FROM geo_dhs_cluster c "
        "JOIN geo_unit u ON c.lga_pcode = u.pcode WHERE u.level=2"
    ).fetchdf()
    assert (j.lga_pcode.str[:5] == j.adm1_pcode).all()


def test_name_and_point_state_mostly_agree_where_resolvable(clusters):
    # only meaningful where DHS published a usable label AND it resolved to
    # a real state (1990/2003 publish no label at all — excluded entirely;
    # see dhs_clusters.py's docstring on name_label_available vs name_unresolved)
    resolvable = clusters[clusters.name_label_available & ~clusters.name_unresolved]
    assert len(resolvable) > 0
    assert resolvable.state_agree.mean() > 0.95


def test_zero_coordinates_are_dropped_not_geocoded(clusters):
    zero = clusters[(clusters.lat == 0) & (clusters.lon == 0)]
    assert (zero.coord_missing & zero.lga_pcode.isna()).all()
