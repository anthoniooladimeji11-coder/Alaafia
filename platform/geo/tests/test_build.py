"""Integrity of the built spine."""


def test_state_count(spine):
    assert spine.execute("SELECT count(*) FROM geo_unit WHERE level=1").fetchone()[0] == 37


def test_lga_count(spine):
    assert spine.execute("SELECT count(*) FROM geo_unit WHERE level=2").fetchone()[0] == 774


def test_pcodes_unique(spine):
    dups = spine.execute(
        "SELECT count(*) FROM (SELECT pcode FROM geo_unit GROUP BY 1 HAVING count(*)>1)"
    ).fetchone()[0]
    assert dups == 0


def test_no_orphans(spine):
    orphans = spine.execute(
        "SELECT count(*) FROM geo_unit c LEFT JOIN geo_unit p "
        "ON c.parent_pcode = p.pcode WHERE c.level>0 AND p.pcode IS NULL"
    ).fetchone()[0]
    assert orphans == 0


def test_pcode_hierarchy_prefix(spine):
    """Every LGA pcode starts with its parent state pcode (OCHA COD scheme)."""
    bad = spine.execute(
        "SELECT count(*) FROM geo_unit "
        "WHERE level=2 AND NOT starts_with(pcode, parent_pcode)"
    ).fetchone()[0]
    assert bad == 0


def test_centroids_in_nigeria(spine):
    from geospine import config

    lo, la, hi, ha = config.NG_BBOX
    out = spine.execute(
        "SELECT count(*) FROM geo_unit WHERE center_lon IS NOT NULL AND NOT "
        f"(center_lon BETWEEN {lo} AND {hi} AND center_lat BETWEEN {la} AND {ha})"
    ).fetchone()[0]
    assert out == 0


def test_every_state_has_lgas(spine):
    n = spine.execute(
        "SELECT count(*) FROM geo_unit s WHERE s.level=1 AND NOT EXISTS "
        "(SELECT 1 FROM geo_unit l WHERE l.level=2 AND l.parent_pcode = s.pcode)"
    ).fetchone()[0]
    assert n == 0


def test_fct_present(spine):
    row = spine.execute(
        "SELECT pcode FROM geo_unit WHERE level=1 AND name_key = "
        "(SELECT name_key FROM geo_unit WHERE level=1 AND lower(name) LIKE '%capital%')"
    ).fetchone()
    assert row is not None
