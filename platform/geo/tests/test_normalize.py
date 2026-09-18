from geospine.normalize import name_key, norm_name


def test_separators_and_case():
    assert norm_name("  ABA  NORTH ") == "Aba North"
    assert norm_name("Cross/River") == "Cross River"
    assert norm_name("Dan'Gora") == "Dangora"


def test_fct_equivalence():
    for v in ("FCT", "Abuja", "FCT Abuja", "Federal Capital Territory"):
        assert name_key(v) == name_key("Federal Capital Territory")


def test_nasarawa_spelling():
    assert name_key("Nassarawa") == name_key("Nasarawa")


def test_key_drops_noise_words():
    assert name_key("Bwari Area Council") == name_key("Bwari")
    assert name_key("Oyo State") == name_key("Oyo")
    assert name_key("Ikeja Local Government Area") == name_key("Ikeja")


def test_key_roman_numerals():
    assert name_key("Bassa II") == name_key("Bassa 2")


def test_direction_words_are_kept():
    assert name_key("Aba North") != name_key("Aba South")
