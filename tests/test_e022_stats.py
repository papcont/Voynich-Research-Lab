"""Synthetic fixture tests for the E022 statistics (pair extraction, Mantel–Haenszel enrichment,
pairing-permutation null, persistence bootstrap). No corpus access."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e022_run", ROOT / "experiments" / "E022_line_break_coupling" / "run.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


def _line(tokens, pend=False, pstart=False, pop="bio_B"):
    return (pop, pend, pstart, [[t, False] for t in tokens])


def test_pair_extraction_classes_and_exclusions():
    recs = {"f1": [_line(["daiin", "chey"], pstart=True), _line(["qokedy", "ol"]), _line(["shedy", "oty"], pend=True),
                   _line(["qokeey", "dal"], pstart=True), (None, False, False, [["x", False]]), _line(["okal", "dy"], pend=True)],
            "f2": [_line(["chol", "dy"], pstart=True), ("bio_B", False, False, [["sho?", True], ["qol", False]]), _line(["ar", "qoky"], pend=True)]}
    pairs, excl = E.extract_pairs(recs)
    # f1: line pairs (chey->qokedy), (ol->shedy); para pair (oty->qokeey); next pair hits a None-population line
    line_b = [(f, S, p) for f, S, p in pairs["line"]["bio_B"]]
    assert ("f1", "y", "qo") in line_b and ("f1", "l", "sh") in line_b
    assert ("f1", "y", "qo") in pairs["para"]["bio_B"]
    # the population-less line is the "next" of one pair and the "previous" of the following one
    assert excl.get("line_no_population") == 2 and "para_no_population" not in excl
    # f2: first pair has an uncertain next-line-initial token -> excluded; second pair (qol -> ar)
    assert excl.get("line_uncertain_edge") == 1
    assert sum(1 for f, _, _ in pairs["line"]["bio_B"] if f == "f2") == 1   # qol -> ar
    # within-line pairs: one per two-token line whose tokens are both strict (f1: 5, f2: 2)
    assert len(pairs["within"]["bio_B"]) == 7


def test_mh_matches_hand_computation_and_is_composition_robust():
    # folio A: after y 10 pairs (6 qo), after other 10 pairs (2 qo)  -> within-folio RR 3
    # folio B: after y 20 pairs (3 qo), after other 5 pairs (0 qo) ... use a symmetric design: both folios RR 3, different base rates
    pl = []
    pl += [("A", "y", "qo")] * 6 + [("A", "y", "ch")] * 4 + [("A", "n", "qo")] * 2 + [("A", "n", "ch")] * 8
    pl += [("B", "y", "qo")] * 9 + [("B", "y", "ch")] * 1 + [("B", "n", "qo")] * 3 + [("B", "n", "ch")] * 7
    arrs = E.folio_arrays(pl)
    num = 6 * 10 / 20 + 9 * 10 / 20
    den = 2 * 10 / 20 + 3 * 10 / 20
    assert math.isclose(E.r_mh(arrs), num / den)
    assert math.isclose(E.r_mh(arrs), 3.0)
    # composition trap: folio C has only y-finals and a high qo rate; folio D only other-finals and a low qo rate
    trap = [("C", "y", "qo")] * 8 + [("C", "y", "ch")] * 2 + [("D", "n", "qo")] * 1 + [("D", "n", "ch")] * 9
    assert E.r_plain(E.folio_arrays(trap))[0] == 8.0          # pooled ratio is inflated by composition
    assert math.isnan(E.r_mh(E.folio_arrays(trap)))            # MH has no informative stratum


def test_permutation_null_centres_near_one_and_detects_coupling():
    rng = np.random.default_rng(1)
    folios = [f"f{i}" for i in range(20)]
    indep, coupled = [], []
    for f in folios:
        for _ in range(30):
            y = rng.random() < 0.5
            indep.append((f, "y" if y else "n", "qo" if rng.random() < 0.25 else "ch"))
            p_qo = 0.6 if y else 0.1
            coupled.append((f, "y" if y else "n", "qo" if rng.random() < p_qo else "ch"))
    b0 = E.enrichment_block(indep, np.random.default_rng(2))
    b1 = E.enrichment_block(coupled, np.random.default_rng(3))
    assert 0.8 < b0["null_mean"] < 1.25 and b0["p_perm"] > 0.05
    assert b1["R_MH"] > 3 and b1["p_perm"] <= 0.01 and b1["null_q975"] < b1["R_MH"]
    assert E.decide_h034(b1) == "SUPPORTED_DEV" and E.decide_h034(b0) in ("FALSIFIED_DEV", "INCONCLUSIVE_DEV")


def test_bootstrap_rho_recovers_ratio():
    rng = np.random.default_rng(4)
    brk, within = [], []
    for i in range(25):
        f = f"f{i}"
        for _ in range(40):
            y = rng.random() < 0.5
            brk.append((f, "y" if y else "n", "qo" if rng.random() < (0.45 if y else 0.15) else "ch"))
        for _ in range(300):
            y = rng.random() < 0.5
            within.append((f, "y" if y else "n", "qo" if rng.random() < (0.45 if y else 0.15) else "ch"))
    r = E.bootstrap_rho(E.folio_arrays(brk), E.folio_arrays(within), np.random.default_rng(5), n_boot=2000)
    assert r["dropped_fraction"] < 0.01
    assert r["ci_lower"] < 1.0 < r["ci_upper"]
    assert E.decide_h035(1.0, r["ci_lower"], r["ci_upper"], "SUPPORTED_DEV") in ("SUPPORTED_DEV", "PARTIAL")


def test_mi_excess_near_zero_under_independence():
    rng = np.random.default_rng(6)
    pl = [(f"f{i%10}", rng.choice(list("ynlrd")), rng.choice(["qo", "ch", "sh", "o", "d"])) for i in range(600)]
    m = E.mi_excess_break(pl, np.random.default_rng(7), n_perm=200)
    assert abs(m["excess"]) < 0.02
