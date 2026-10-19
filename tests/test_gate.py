"""Gate v2 synthetic positive and negative test cases.

The gate must accept a genuine mechanism (a real coder that knows how a
synthetic ciphertext was generated) and reject sham decipherments (free
readable output, gains that survive permutation, under-powered or post-hoc
claims). Nothing here touches the Voynich corpus.
"""
from __future__ import annotations

import copy
import hashlib
import math

import numpy as np
import pytest

from voynichlab.gate import (FAIL, INCONCLUSIVE, LEVELS, NOT_TESTED, PASS, bootstrap_mean_ci, evaluate,
                             holm_adjust, load_spec, permutation_p, render_report)
from voynichlab.mdl import KTCoder

SPEC = load_spec()
H = lambda s: hashlib.sha256(s.encode()).hexdigest()  # noqa: E731
REGISTRY = {
    "selection_folios": ["s1", "s2"],
    "lockboxes": {
        "LB_OK": {"independence": "INDEPENDENT", "folios": [f"f{i}" for i in range(40)]},
        "LB_SEMI": {"independence": "SEMI_INDEPENDENT", "folios": [f"f{i}" for i in range(40)]},
        "LB_BAD": {"independence": "INDEPENDENT", "folios": ["s1", "f3"]},
    },
}


# --------------------------------------------------------------------------- #
# synthetic world: a 2-state Markov "cipher" over 12 symbols; the genuine
# mechanism knows the transition table, the null is a KT unigram coder.
# --------------------------------------------------------------------------- #
def synthetic_world(n_folios=40, tokens_per_folio=120, seed=7, shuffle=False):
    rng = np.random.default_rng(seed)
    K = 12
    T = rng.dirichlet(np.full(K, 0.15), size=K)  # peaked transitions = real structure
    folios = []
    for f in range(n_folios):
        s = rng.integers(K)
        seq = [s]
        for _ in range(tokens_per_folio - 1):
            s = rng.choice(K, p=T[s])
            seq.append(s)
        if shuffle:
            rng.shuffle(seq)
        folios.append([f"w{x}" for x in seq])
    return T, folios


def code_world(T, folios, genuine=True):
    """Per-folio bits: genuine mechanism (true conditional model) vs KT unigram null."""
    rows, null_rows = [], []
    null = KTCoder(sigma_size=3)
    inv = {f"w{i}": i for i in range(len(T))}
    for fi, seq in enumerate(folios):
        cand = 0.0
        nb = 0.0
        prev = None
        for v in seq:
            nb += null.encode((), v)
            if genuine and prev is not None:
                cand += -math.log2(T[inv[prev]][inv[v]])
            else:
                cand += math.log2(len(T))  # uniform: no knowledge
            prev = v
        rows.append({"folio": f"f{fi}", "n_tokens": len(seq), "candidate_data_bits": cand, "null_total_bits": nb})
    return rows


def base_claim(lockbox="LB_OK"):
    return {
        "claim_id": "synthetic", "registered_utc": "2026-10-19T00:00:00Z", "freeze_commit": "deadbeef",
        "lockbox_id": lockbox, "retraction_condition": "ci_lower <= 0 on the lockbox",
        "post_reveal_changes": False,
        "sha256": {k: H(k) for k in ("split", "inputs", "config", "predictions")},
    }


def compression_block(rows, control_rows=None, margin=0.5):
    text_hash = H("lockbox-text")
    blk = {
        "folios": rows,
        "candidate_model_bits": {"mechanism_code_bits": 200, "dictionary_bits": 500, "key_bits": 64,
                                 "exception_bits": 0, "residual_bits": 0, "transmission_bits": 32},
        "reconstruction_sha256": text_hash, "lockbox_text_sha256": text_hash,
        "margin": {"bits_per_token": margin, "calibration_source": "development",
                   "justification": "half the development-fold gain of the strongest null over whole-token coding"},
    }
    if control_rows is not None:
        def bpt(rs, key):
            return sum(r[key] for r in rs) / sum(r["n_tokens"] for r in rs)
        blk["controls"] = {
            c: {"candidate_total_bits_per_token": bpt(control_rows, "candidate_data_bits"),
                "null_total_bits_per_token": bpt(control_rows, "null_total_bits")}
            for c in ("folio_internal_permutation", "matched_synthetic", "nonsemantic_generator")}
    return blk


def mechanism_block():
    return {"produces_plaintext": True, "deterministic": True, "plaintext_sha256": H("plain"),
            "output_freedom_bits_per_token": 0.0}


# --------------------------------------------------------------------------- #
# statistics helpers
# --------------------------------------------------------------------------- #
def test_bootstrap_ci_brackets_mean():
    d = np.random.default_rng(1).normal(1.0, 0.5, 50)
    m, lo, hi = bootstrap_mean_ci(d, resamples=2000)
    assert lo < m < hi and lo > 0.6


def test_permutation_p_never_zero_and_holm():
    assert permutation_p(10.0, [0.0] * 99) == pytest.approx(1 / 100)
    assert permutation_p(0.0, [1.0] * 9) == 1.0
    adj = holm_adjust({"a": 0.001, "b": 0.02, "c": 0.5})
    assert adj["a"] == pytest.approx(0.003) and adj["b"] == pytest.approx(0.04) and adj["c"] == 0.5


# --------------------------------------------------------------------------- #
# positive cases
# --------------------------------------------------------------------------- #
def test_genuine_mechanism_passes_structural_and_mechanism_levels():
    T, folios = synthetic_world()
    rows = code_world(T, folios, genuine=True)
    _, shuffled = synthetic_world(shuffle=True)
    ctrl = code_world(T, shuffled, genuine=True)  # the same mechanism on permuted text gains far less
    claim = base_claim()
    claim["compression"] = compression_block(rows, ctrl)
    claim["mechanism"] = mechanism_block()
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.registration.state == PASS
    assert res.levels[LEVELS[0]].state == PASS
    assert res.levels[LEVELS[1]].state == PASS
    # a compression pass never promotes language/semantic levels
    assert res.levels[LEVELS[2]].state == NOT_TESTED
    assert res.levels[LEVELS[3]].state == NOT_TESTED
    assert res.levels[LEVELS[4]].state == NOT_TESTED
    assert res.highest_pass == LEVELS[1]
    assert "Gate v2.0.0 report" in render_report(res)


def test_structural_model_without_mechanism_block_stops_at_level_one():
    T, folios = synthetic_world()
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[0]].state == PASS
    assert res.levels[LEVELS[1]].state == NOT_TESTED


def test_full_chain_with_planted_semantics_and_confirmation():
    T, folios = synthetic_world()
    _, shuffled = synthetic_world(shuffle=True)
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True), code_world(T, shuffled, True))
    claim["mechanism"] = mechanism_block()
    rng = np.random.default_rng(3)
    lang_rows = []
    for r in claim["compression"]["folios"]:
        n = r["n_tokens"]
        lang_rows.append({"folio": r["folio"], "n_tokens": n, "target_bits": 5.0 * n,
                          "alt_bits": {"L1": 6.2 * n + rng.normal(0, 5), "L2": 6.0 * n + rng.normal(0, 5), "L3": 7.0 * n}})
    claim["language"] = {"target": "T", "alternatives": ["L1", "L2", "L3"], "folios": lang_rows,
                         "control_prefers_target": False, "corpora_sha256": {"T": H("t"), "L1": H("1"), "L2": H("2"), "L3": H("3")}}
    claim["semantic"] = {
        "predictions_registered_before_inspection": True, "claims_true_word_error_rate": False,
        "coverage_percent": 42.0, "undetermined_word_percent": 31.0, "evidence_quality_tier": "B",
        "synthetic_positive_control_error_rate": 0.12,
        "reports": {"semantic_plausibility": "...", "independent_rater_agreement": "kappa 0.71", "verifiable_text_statements": "..."},
        "families": [{"name": "plant_part", "primary": True, "observed_effect": 0.8, "min_effect": 0.3,
                      "null_effects": list(rng.normal(0, 0.1, 999))},
                     {"name": "star_names", "primary": True, "observed_effect": 0.6, "min_effect": 0.3,
                      "null_effects": list(rng.normal(0, 0.1, 999))}],
    }
    claim["confirmation"] = {
        "independent_replication": {"implementer": "other-team", "sha256": H("rep"), "result_direction_same": True},
        "transliterations": {"IT2a": {"clear": {"mean_delta": 0.9, "ci_lower": 0.4}, "uncertain": {"mean_delta": 0.2, "ci_lower": -0.3}}},
        "retraction_condition_triggered": False,
    }
    res = evaluate(claim, SPEC, REGISTRY)
    assert [res.levels[lv].state for lv in LEVELS] == [PASS] * 5
    assert res.highest_pass == LEVELS[4]


# --------------------------------------------------------------------------- #
# negative cases: sham decipherments must be rejected
# --------------------------------------------------------------------------- #
def test_readable_output_without_compression_gain_fails():
    T, folios = synthetic_world()
    rows = code_world(T, folios, genuine=False)  # "decode" knows nothing: uniform cost
    claim = base_claim()
    claim["compression"] = compression_block(rows)
    claim["mechanism"] = mechanism_block()
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[0]].state == FAIL
    assert res.levels[LEVELS[1]].state == FAIL
    assert res.highest_pass is None


def test_gain_that_survives_permutation_is_not_a_decoding_mechanism():
    T, folios = synthetic_world()
    rows = code_world(T, folios, True)
    claim = base_claim()
    claim["compression"] = compression_block(rows, rows)  # same gain on "controls" as on real text
    claim["mechanism"] = mechanism_block()
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[0]].state == PASS        # it is a valid structural model...
    assert res.levels[LEVELS[1]].state == FAIL        # ...but not a content-specific decoding
    assert any("specificity" in r for r in res.levels[LEVELS[1]].reasons)


def test_underpowered_is_inconclusive_not_pass():
    T, folios = synthetic_world(n_folios=8)
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[0]].state == INCONCLUSIVE


def test_small_noisy_gain_is_inconclusive_and_clear_shortfall_fails():
    z = np.random.default_rng(5).normal(0, 1, 40)
    z = (z - z.mean()) / z.std()
    diffs = 0.3 + 1.5 * z  # mean 0.3 bits/token (below the 0.5 margin) with a CI reaching past the margin
    rows = [{"folio": f"f{i}", "n_tokens": 100, "candidate_data_bits": 1000 - 100 * d, "null_total_bits": 1000}
            for i, d in enumerate(diffs)]
    claim = base_claim()
    claim["compression"] = compression_block(rows)
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[0]].state == INCONCLUSIVE
    rows = [{"folio": f"f{i}", "n_tokens": 100, "candidate_data_bits": 990, "null_total_bits": 1000} for i in range(40)]
    claim["compression"] = compression_block(rows)  # 0.1 bits/token: clearly below the 0.5 margin
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[0]].state == FAIL


def test_margin_calibrated_on_lockbox_or_missing_model_bits_fails():
    T, folios = synthetic_world()
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    claim["compression"]["margin"]["calibration_source"] = "lockbox"
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[0]].state == FAIL
    claim["compression"]["margin"]["calibration_source"] = "development"
    del claim["compression"]["candidate_model_bits"]["key_bits"]
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[0]].state == FAIL


def test_no_reconstruction_means_not_tested():
    T, folios = synthetic_world()
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    claim["compression"]["reconstruction_sha256"] = H("something else")
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[0]].state == NOT_TESTED


def test_registration_defects_fail_everything():
    T, folios = synthetic_world()
    good = base_claim()
    good["compression"] = compression_block(code_world(T, folios, True))
    for mutate in (
        lambda c: c.pop("retraction_condition"),
        lambda c: c["sha256"].pop("predictions"),
        lambda c: c.update(post_reveal_changes=True),
        lambda c: c.update(lockbox_id="LB_BAD"),      # overlaps SELECTION folios
        lambda c: c.update(lockbox_id="LB_UNKNOWN"),
    ):
        c = copy.deepcopy(good)
        mutate(c)
        res = evaluate(c, SPEC, REGISTRY)
        assert res.registration.state == FAIL
        assert all(res.levels[lv].state == FAIL for lv in LEVELS)


def test_semi_independent_lockbox_is_flagged_not_failed():
    T, folios = synthetic_world()
    claim = base_claim("LB_SEMI")
    claim["compression"] = compression_block(code_world(T, folios, True))
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.registration.state == PASS
    assert any("SEMI_INDEPENDENT" in f for f in res.flags)


def test_semantics_require_preregistration_effect_and_holm():
    rng = np.random.default_rng(11)
    sem = {
        "predictions_registered_before_inspection": True, "claims_true_word_error_rate": False,
        "coverage_percent": 10.0, "undetermined_word_percent": 60.0, "evidence_quality_tier": "C",
        "reports": {"semantic_plausibility": "", "independent_rater_agreement": "", "verifiable_text_statements": ""},
        "families": [{"name": "k", "primary": True, "observed_effect": 0.25, "min_effect": 0.2,
                      "null_effects": list(rng.normal(0, 0.1, 999))}],
    }
    T, folios = synthetic_world()
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    claim["semantic"] = copy.deepcopy(sem)
    # own evidence passes but lower levels (mechanism) are not PASS -> cannot be PASS
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[3]].state == INCONCLUSIVE
    # a null-like effect fails
    claim["semantic"]["families"][0]["observed_effect"] = 0.05
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[3]].state == FAIL
    # predictions not registered before inspection fails regardless of effect
    claim["semantic"]["families"][0]["observed_effect"] = 0.9
    claim["semantic"]["predictions_registered_before_inspection"] = False
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[3]].state == FAIL
    # claiming a true word error rate fails
    claim["semantic"]["predictions_registered_before_inspection"] = True
    claim["semantic"]["claims_true_word_error_rate"] = True
    assert evaluate(claim, SPEC, REGISTRY).levels[LEVELS[3]].state == FAIL
    # multiple testing: one strong and many weak families -> the weak primaries fail after Holm
    claim["semantic"]["claims_true_word_error_rate"] = False
    fams = [{"name": f"f{i}", "primary": True, "observed_effect": 0.22, "min_effect": 0.2,
             "null_effects": list(rng.normal(0, 0.1, 999))} for i in range(8)]
    claim["semantic"]["families"] = fams
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[3]].state == FAIL
    assert any("Holm" in r for r in res.levels[LEVELS[3]].reasons)


def test_confirmation_requires_replication_and_transliteration():
    T, folios = synthetic_world()
    claim = base_claim()
    claim["compression"] = compression_block(code_world(T, folios, True))
    claim["confirmation"] = {"independent_replication": {"implementer": "x", "sha256": H("r"), "result_direction_same": False},
                             "transliterations": {}, "retraction_condition_triggered": False}
    res = evaluate(claim, SPEC, REGISTRY)
    assert res.levels[LEVELS[4]].state == FAIL
    assert any("IT2a" in r for r in res.levels[LEVELS[4]].reasons)
