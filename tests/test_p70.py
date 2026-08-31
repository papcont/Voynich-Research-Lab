from voynichlab.p70 import parse_p70, is_degenerate, SUFFIX_FAMILY


def test_demo_contract():
    from voynichlab.p70 import demo
    demo()


def test_precedence_and_chsh_are_prefixes():
    assert parse_p70("qokeedy") == ("qo", "k", "", "eedy")
    assert parse_p70("chol") == ("ch", "", "", "ol")
    assert parse_p70("shdy") == ("sh", "", "", "dy")
    assert parse_p70("chey")[0] == "ch"


def test_lossless_reconstruction():
    for t in ("qokeedy", "chol", "otaram", "daiin", "qokchey", "xyzzy", "ar", "a"):
        p, g, c, s = parse_p70(t)
        assert p + g + c + s == t


def test_suffix_only_on_remaining_never_overlaps_affix():
    # gallows 'k' consumed; suffix taken from remainder only
    p, g, c, s = parse_p70("okaiin")
    assert (p, g) == ("o", "k")
    assert p + g + c + s == "okaiin"


def test_degenerate_when_no_affix():
    assert is_degenerate(parse_p70("xqz")) is True
    assert is_degenerate(parse_p70("qokeedy")) is False


def test_suffix_family_lookup():
    assert SUFFIX_FAMILY["eedy"] == "Y"
    assert SUFFIX_FAMILY["aiin"] == "N"
    assert SUFFIX_FAMILY["ar"] == "R"
