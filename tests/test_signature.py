"""Fixture tests for voynichlab.signature (no corpus) plus a regression test against the
recorded E011/E014/E016/E017 values that runs only when data/raw/ZL3b-n.txt is present."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from voynichlab import signature as S

ROOT = Path(__file__).resolve().parents[1]


def _lines_from_folios(folios, lang="B", sec="S"):
    return {f: [(lang, sec, [[v, False] for v in line]) for line in lines] for f, lines in folios.items()}


def _synthetic(seed, coupled, n_folios=12, lines_per=8, per_line=9):
    """Edge-coupled (prefix depends on previous final char) vs independent token streams."""
    rng = np.random.default_rng(seed)
    prefixes = ["qo", "o", "ch", "sh", "d", ""]
    cores = ["k", "t", "ke", "te", "l", "r"]
    suffixes = ["y", "dy", "aiin", "ol", "ar"]
    folios = {}
    for i in range(n_folios):
        lines = []
        prev_final = None
        for _ in range(lines_per):
            line = []
            for _ in range(per_line):
                if coupled and prev_final == "y":
                    p = "qo" if rng.random() < 0.8 else prefixes[rng.integers(6)]
                elif coupled and prev_final == "n":
                    p = "ch" if rng.random() < 0.8 else prefixes[rng.integers(6)]
                else:
                    p = prefixes[rng.integers(6)]
                tok = p + cores[rng.integers(6)] + suffixes[rng.integers(5)]
                line.append(tok)
                prev_final = tok[-1]
            lines.append(line)
        folios[f"f{i + 1}r"] = lines
    return _lines_from_folios(folios)


def test_canonical_edit_and_lev1():
    assert S.canonical_edit("aab", "aaab") == "i0a"
    assert S.canonical_edit("aaab", "aab") == "d0"
    assert S.canonical_edit("okal", "okar") == "s3r"
    assert S._lev1("okal", "oka") and S._lev1("oka", "okal") and not S._lev1("okal", "okal")


def test_tokens_features_and_lossless():
    lines = {"f1r": [("A", "H", [["qokeedy", False], ["x", True], ["chol", False], ["chol", False]])]}
    toks = S.tokens(lines)
    assert [t.S for t in toks] == ["BOL", "UNC", "l"]
    assert [t.L for t in toks] == ["FIRST", "MID", "LAST"]
    assert toks[2].k_exact == 1 and all("".join(t.slots) == t.value for t in toks)


def test_edge_coupled_text_has_positive_delta_S_and_independent_does_not():
    coupled = S.signature(_synthetic(1, True), components=("delta_S",))
    indep = S.signature(_synthetic(1, False), components=("delta_S",))
    assert coupled["delta_S"] > 0.2
    assert abs(indep["delta_S"]) < 0.05


def test_determinism_and_vocabulary_components():
    lines = _synthetic(3, True)
    a = S.signature(lines, n_perm=50, components=("TTR", "H1", "F_excess", "dJ_order"))
    b = S.signature(lines, n_perm=50, components=("TTR", "H1", "F_excess", "dJ_order"))
    assert a == b
    assert 0 < a["TTR"] < 1 and 0 <= a["H1"] <= 1


@pytest.mark.skipif(not (ROOT / "data" / "raw" / "ZL3b-n.txt").is_file(), reason="corpus not fetched")
def test_regression_against_recorded_experiment_values():
    """The module must reproduce the frozen experiments' numbers exactly."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from voynichlab.ivtff import parse_ivtff, tokenize_surface
    from voynichlab.loci import is_running_text
    from collections import defaultdict
    lines = defaultdict(list)
    for rec in parse_ivtff(ROOT / "data" / "raw" / "ZL3b-n.txt"):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            lines[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    sig = S.signature(dict(lines))
    e014 = json.loads((ROOT / "experiments/E014_generator_signatures/results.json").read_text())["voynich_reference_EXPLORATORY"]
    e016 = json.loads((ROOT / "experiments/E016_folio_vocabulary_locality/results.json").read_text())["H024"]
    e017 = json.loads((ROOT / "experiments/E017_codex_order_adjacency/results.json").read_text())["H025b"]
    for k in ("delta_S", "delta_L", "delta_C"):
        assert abs(sig[k] - e014[k]["mean"]) < 1e-9
    assert abs(sig["TTR"] - e014["ttr"]) < 1e-12 and abs(sig["H1"] - e014["hapax"]) < 1e-12
    assert abs(sig["F_excess"] - e016["excess_dF"]) < 1e-9
    assert abs(sig["dJ_order"] - e017["excess_dJ"]) < 1e-9


def test_a3_slots_and_substitution_invariance():
    """Signature-G must be invariant under a bijective relabelling of characters."""
    lines = _synthetic(5, True)
    alphabet = sorted({c for f in lines for _l, _s, full in lines[f] for v, _u in full for c in v})
    perm = dict(zip(alphabet, reversed(alphabet)))
    sub = {f: [(l, s, [["".join(perm[c] for c in v), u] for v, u in full]) for l, s, full in lines[f]] for f in lines}
    comps = ("delta_S", "delta_L", "delta_C", "TTR", "H1")
    a = S.signature(lines, components=comps, slot_fn=S.a3_slots)
    b = S.signature(sub, components=comps, slot_fn=S.a3_slots)
    for k in comps:
        assert abs(a[k] - b[k]) < 1e-9
    assert S.a3_slots("ab") == ("", "ab", "") and S.a3_slots("qokeedy") == ("q", "okeed", "y")
