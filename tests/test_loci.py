from voynichlab.loci import locus_type, is_running_text


def test_locus_type_strips_position_and_digits():
    assert locus_type("@P0") == "P"
    assert locus_type("+P0") == "P"
    assert locus_type("&Lz") == "Lz"
    assert locus_type("/L") == "L"
    assert locus_type("@Ri") == "Ri"
    assert locus_type("=Pt") == "Pt"
    assert locus_type(None) == ""
    assert locus_type("") == ""


def test_running_text_is_paragraph_only():
    assert is_running_text("@P0") is True
    assert is_running_text("+Pb") is True
    assert is_running_text("=Pt") is True
    # labels / circular / radial are NOT running text
    assert is_running_text("&Lz") is False
    assert is_running_text("@Lf") is False
    assert is_running_text("@Cc") is False
    assert is_running_text("@Ri") is False
    assert is_running_text(None) is False
