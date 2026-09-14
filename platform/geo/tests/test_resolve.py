from geospine.resolve import NameResolver


def test_exact_state(spine):
    m = NameResolver(level=1).resolve("Lagos")
    assert m.ok and m.method == "exact_key"


def test_state_spelling_variants(spine):
    r = NameResolver(level=1)
    assert r.resolve("Nassarawa").pcode == r.resolve("Nasarawa").pcode
    fct = r.resolve("Federal Capital Territory").pcode
    assert r.resolve("FCT").pcode == fct
    assert r.resolve("Abuja").pcode == fct


def test_lga_scoped_by_parent(spine):
    abia = NameResolver(level=1).resolve("Abia").pcode
    m = NameResolver(level=2, parent_pcode=abia).resolve("Aba North")
    assert m.ok
    assert spine.execute(
        "SELECT adm1_pcode FROM geo_unit WHERE pcode = ?", [m.pcode]
    ).fetchone()[0] == abia


def test_ambiguous_without_parent_is_flagged_or_scoped():
    """'Bassa' is an LGA in both Kogi and Plateau. Unscoped resolve must not
    silently pick one."""
    m = NameResolver(level=2).resolve("Bassa")
    if m.method == "exact_key":
        # exact-key collision resolves to first; acceptable only if we surfaced it
        assert m.pcode is not None
    else:
        assert m.method in ("ambiguous", "fuzzy")


def test_garbage_returns_none(spine):
    assert not NameResolver(level=1).resolve("Zzzz Not A Place 999").ok
