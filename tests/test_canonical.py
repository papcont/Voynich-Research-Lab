from voynichlab.canonical import parse_fused_token

def test_known_candidate_chains():
    assert parse_fused_token("otarar") == ("ot", "ar", "ar")
    assert parse_fused_token("otaral") == ("ot", "ar", "al")
    assert parse_fused_token("otaraiin") == ("ot", "ar", "aiin")
    assert parse_fused_token("otaram") == ("ot", "ar", "am")
    assert parse_fused_token("okarar") == ("ok", "ar", "ar")
    assert parse_fused_token("okaral") == ("ok", "ar", "al")

def test_parser_is_conservative():
    assert parse_fused_token("qokedy") is None
    assert parse_fused_token("shedy") is None
