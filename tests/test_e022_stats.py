"""Synthetic fixture tests for the E022 statistics (pair extraction, stratified Mantel–Haenszel
enrichment, pairing-permutation null, bootstrap persistence ratio, decisions). No corpus access."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e022_run", ROOT / "experiments" / "E022_line_break_coupling" / "run.py")
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


def _rec(locus, tokens, pend=False, pstart=False, pop="bio_B", locator="+P0", gaps=()):
    return {"locus": locus, "locator": locator, "ltype": E.locus_type(locator), "pop": pop, "hand": "2", "end": pend, "start": pstart,
            "toks": [[t, False, i in gaps] for i, t in enumerate(tokens)]}


def _fin(recs):
    for folio in recs:
        pid = 0
        for r in recs[folio]:
            if r["start"]:
                pid += 1
            r["pid"] = pid
    rawidx = {f: [(r["locus"], False) for r in recs[f]] for f in recs}
    return recs, rawidx


def test_pair_extraction_classes_and_exclusions():
    recs, rawidx = _fin({"f1": [_rec("f1.1", ["daiin", "chey"], pstart=True, locator="@P0"), _rec("f1.2", ["qokedy", "ol"]),
                                _rec("f1.3", ["shedy", "oty"], pend=True, locator="=Pt"), _rec("f1.4", ["qokeey", "dal"], pstart=True, locator="@P0"),
                                _rec("f1.5", ["x"], pop=None), _rec("f1.6", ["okal", "dy"], pend=True)],
                         "f2": [_rec("f2.1", ["chol", "dy", "shey"], pstart=True, locator="@P0", gaps=(2,)),
                                {"locus": "f2.2", "locator": "+P0", "ltype": "P", "pop": "bio_B", "hand": "2", "end": False, "start": False,
                                 "toks": [["sho?", True, False], ["qol", False, False]]},
                                _rec("f2.3", ["ar", "qoky"], pend=True), _rec("f2.4", ["otol"], pstart=True, locator="@Pb")]})
    pairs, excl = E.extract_pairs(recs, rawidx)
    line = {(p["folio"], p["S"], p["pre"]) for p in pairs["line"]}
    assert ("f1", "y", "qo") in line and ("f1", "l", "sh") not in line      # chey->qokedy kept; ol->shedy excluded: f1.3 carries '='
    assert excl.get("line_same_line_title") == 1                             # f1.2 -> f1.3 (later record '=', same physical line)
    assert ("f1", "y", "qo") in {(p["folio"], p["S"], p["pre"]) for p in pairs["para"]}   # oty -> qokeey
    assert excl.get("line_no_population") == 2 and "para_no_population" not in excl
    assert excl.get("line_uncertain_edge") == 1 and excl.get("para_pb_record") == 1
    assert sum(1 for p in pairs["line"] if p["folio"] == "f2") == 1          # qol -> ar
    assert len(pairs["gap"]) == 1 and pairs["gap"][0]["S"] == "y"            # dy -> shey across <->
    assert len(pairs["within"]) == 7                                          # f1: 5 ; f2: 1 (chol dy) + 1 (ar qoky); f2.2 none; f2.4 Pb excluded
    assert excl.get("within_pb_record") == 1
    assert all(p["stratum"] == (p["folio"], 1) or p["stratum"] == (p["folio"], 2) for p in pairs["line"])
    # lag2: f1.1 -> f1.3 blocked (f1.3 is '='), f2.1 -> f2.3 valid (middle line edges may be uncertain)
    assert {(p["folio"], p["S"], p["pre"]) for p in pairs["lag2"]} == {("f2", "y", "a" if E.parse_p70("ar")[0] == "a" else E.parse_p70("ar")[0])}


def _pl(items):
    return [{"stratum": s, "folio": s if isinstance(s, str) else s[0], "S": S, "pre": p, "prev_len": 5, "one_token": False, "hand": "2"} for s, S, p in items]


def test_mh_matches_hand_computation_and_is_composition_robust():
    pl = _pl([("A", "y", "qo")] * 6 + [("A", "y", "ch")] * 4 + [("A", "n", "qo")] * 2 + [("A", "n", "ch")] * 8
             + [("B", "y", "qo")] * 9 + [("B", "y", "ch")] * 1 + [("B", "n", "qo")] * 3 + [("B", "n", "ch")] * 7)
    arrs = E.strata_arrays(pl)
    assert math.isclose(E.r_mh(arrs), (6 * 10 / 20 + 9 * 10 / 20) / (2 * 10 / 20 + 3 * 10 / 20)) and math.isclose(E.r_mh(arrs), 3.0)
    assert math.isclose(E.or_mh(arrs), (6 * 8 / 20 + 9 * 7 / 20) / (4 * 2 / 20 + 1 * 3 / 20))
    trap = _pl([("C", "y", "qo")] * 8 + [("C", "y", "ch")] * 2 + [("D", "n", "qo")] * 1 + [("D", "n", "ch")] * 9)
    assert E.counts(E.strata_arrays(trap))["R_plain"] == 8.0      # pooled ratio inflated by composition
    assert math.isnan(E.r_mh(E.strata_arrays(trap)))              # no informative stratum


def test_permutation_null_and_undefined_handling():
    rng = np.random.default_rng(1)
    indep, coupled = [], []
    for i in range(20):
        for _ in range(30):
            y = rng.random() < 0.5
            indep.append((f"f{i}", "y" if y else "n", "qo" if rng.random() < 0.25 else "ch"))
            coupled.append((f"f{i}", "y" if y else "n", "qo" if rng.random() < (0.6 if y else 0.1) else "ch"))
    b0 = E.enrichment_block(_pl(indep), np.random.default_rng(2)); b1 = E.enrichment_block(_pl(coupled), np.random.default_rng(3))
    assert 0.85 < b0["null_median"] < 1.15 and b0["p_perm"] > 0.05 and b0["null_status"] == "OK"
    assert b1["R_MH"] > 3 and b1["p_perm"] <= 0.01 and b1["null_q975"] < b1["R_MH"]
    assert E.decide_h034(b1, ci_upper=5.0) == "SUPPORTED_DEV"
    assert E.decide_h034(b0, ci_upper=1.3) == "FALSIFIED_DEV"                          # R_MH <= 1.1 under independence
    mid = {**b0, "R_MH": 1.3, "p_perm": 0.2}                                           # attenuated to the detection floor
    assert E.decide_h034(mid, ci_upper=1.8) == "INCONCLUSIVE_DEV" and E.decide_h034(mid, ci_upper=1.45) == "FALSIFIED_DEV"
    # undefined permutations: a single stratum with one qo event after y -> permutations put it after 'other' or not
    tiny = _pl([("A", "y", "qo")] + [("A", "y", "ch")] * 3 + [("A", "n", "ch")] * 4)
    bt = E.enrichment_block(tiny, np.random.default_rng(4))
    assert bt["null_undefined"] > 0 and bt["null_status"] == "NOT_DEFINED" and bt["p_perm"] is not None
    assert E.decide_h034(bt, ci_upper=None) == "INCONCLUSIVE_DEV"


def test_bootstrap_rho_keeps_nonpositive_and_recovers_ratio():
    rng = np.random.default_rng(4)
    brk, within = [], []
    for i in range(25):
        f = f"f{i}"
        for _ in range(40):
            y = rng.random() < 0.5
            brk.append(((f, 1), "y" if y else "n", "qo" if rng.random() < (0.45 if y else 0.15) else "ch"))
        for _ in range(300):
            y = rng.random() < 0.5
            within.append(((f, 1), "y" if y else "n", "qo" if rng.random() < (0.45 if y else 0.15) else "ch"))
    r = E.bootstrap(_pl(brk), _pl(within), np.random.default_rng(5), n_boot=2000)
    assert r["rho_dropped_fraction"] < 0.01 and r["rho_ci_flag"] == "OK"
    assert r["rho_ci_lower"] < 1.0 < r["rho_ci_upper"] and r["R_line_ci_lower"] < 3.0 < r["R_line_ci_upper"]
    # no coupling at the break: rho <= 0 values must be retained (CI upper near 0, not truncated)
    flat = [(s, S, ("qo" if rng.random() < 0.25 else "ch")) for s, S, _ in brk]
    r0 = E.bootstrap(_pl(flat), _pl(within), np.random.default_rng(6), n_boot=2000)
    assert r0["rho_dropped_fraction"] < 0.01 and r0["rho_ci_lower"] < 0 < r0["rho_ci_upper"] and r0["rho_ci_upper"] < 0.25
    assert E.decide_h035(E.rho_point(1.0, 3.0), r0, "SUPPORTED_DEV") == "FALSIFIED_DEV"
    assert E.decide_h035(1.0, r, "SUPPORTED_DEV") in ("SUPPORTED_DEV", "PARTIAL")
    assert E.decide_h035(0.9, {**r, "rho_ci_flag": "CI_UNRELIABLE"}, "SUPPORTED_DEV") == "PARTIAL"


def test_h036_rule_and_composition_guard():
    base = {"null_status": "OK", "R_MH": 2.0, "p_perm": 0.004, "null_q975": 1.4, "n_qo_informative": 12}
    assert E.decide_h036(base) == "SUPPORTED_DEV"
    assert E.decide_h036({**base, "R_MH": 1.2, "p_perm": 0.3}) == "INCONCLUSIVE_DEV"                 # underpowered: never FALSIFIED
    assert E.decide_h036({**base, "R_MH": 1.2, "p_perm": 0.3, "n_qo_informative": 150}) == "FALSIFIED_DEV"
    line = {"R_MH": 2.5, "p_perm": 0.001, "null_status": "OK"}
    assert E.composition_guard("SUPPORTED_DEV", line, {"R_MH": 1.1, "p_perm": 0.4, "null_status": "OK"}) == "ADJACENCY"
    assert E.composition_guard("SUPPORTED_DEV", line, {"R_MH": 2.0, "p_perm": 0.001, "null_status": "OK"}) == "COMPOSITION_CONFOUNDED"
    assert E.composition_guard("INCONCLUSIVE_DEV", line, {"R_MH": 1.0, "p_perm": 0.5, "null_status": "OK"}) == "NOT_APPLICABLE"


def test_gap_tokens_matches_frozen_tokenizer():
    toks, ok = E.gap_tokens("<%>daiin.chey<->qokedy,ol<!comment>.shedy<$>")
    assert ok and [t[0] for t in toks] == ["daiin", "chey", "qokedy", "ol", "shedy"]
    assert [t[2] for t in toks] == [False, False, True, False, False]


def test_mi_excess_near_zero_under_independence():
    rng = np.random.default_rng(6)
    pl = _pl([((f"f{i % 10}", 1), rng.choice(list("ynlrd")), rng.choice(["qo", "ch", "sh", "o", "d"])) for i in range(600)])
    sp = [(p["S"], p["pre"]) for p in pl]
    null = np.mean([E.mi_bits(E.permuted_sp(pl, rng)) for _ in range(200)])
    assert abs(E.mi_bits(sp) - null) < 0.02
