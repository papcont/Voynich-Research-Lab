from voynichlab.ivtff import tokenize_surface

def test_surface_separators():
    toks = tokenize_surface("otar.ar.okol")
    assert [t.value for t in toks] == ["otar", "ar", "okol"]
    assert toks[0].separator_after == "."
    assert toks[1].separator_before == "."
    assert toks[1].separator_after == "."

def test_uncertain_token_flag():
    toks = tokenize_surface("qokar.[a:o]l")
    assert toks[1].uncertain
