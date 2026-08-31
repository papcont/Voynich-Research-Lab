"""Independent validator for E006 results.json.

Re-derives the qualifying-chain set from the source with its own detection loop
(not by importing run.py), checks source identity, frozen constants, holdout
membership, decision-rule arithmetic, and numeric sanity. Exit non-zero on any
failure.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.canonical import parse_fused_token, STEMS, FINALS  # noqa: E402
from voynichlab.folds import folio_fold, HOLDOUT_FOLDS, DEVELOPMENT_FOLDS  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
FINALS_SET = set(FINALS)
STEMS_SET = set(STEMS)

errors: list[str] = []


def check(cond: bool, msg: str):
    if not cond:
        errors.append(msg)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def independent_qualifying():
    """Own detection of holdout qualifying k=2 chains and occurrence counts."""
    by_chain = defaultdict(lambda: {"fused": 0, "spaced": 0})
    tot = {"fused": 0, "spaced": 0}
    for rec in parse_ivtff(DATA):
        if folio_fold(rec.folio) not in HOLDOUT_FOLDS:
            continue
        toks = tokenize_surface(rec.raw_text)
        for i, A in enumerate(toks):
            if A.uncertain or not A.value:
                continue
            p = parse_fused_token(A.value)
            if p is None:
                continue
            if len(p) == 3 and p[0] in STEMS_SET and p[1] in FINALS_SET and p[2] in FINALS_SET:
                by_chain[p]["fused"] += 1
                tot["fused"] += 1
            elif len(p) == 2 and p[0] in STEMS_SET and p[1] in FINALS_SET and i + 1 < len(toks):
                B = toks[i + 1]
                if (not B.uncertain) and B.value in FINALS_SET and A.separator_after == ".":
                    by_chain[(p[0], p[1], B.value)]["spaced"] += 1
                    tot["spaced"] += 1
    qual = sorted("|".join(c) for c, d in by_chain.items()
                  if d["fused"] >= 2 and d["spaced"] >= 2)
    return qual, tot, len(by_chain)


def finite(x) -> bool:
    return x is None or (isinstance(x, (int, float)) and math.isfinite(x))


def main() -> int:
    check(DATA.is_file(), "source data missing")
    check((EXP / "results.json").is_file(), "results.json missing")
    if errors:
        return _report()

    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))

    # required top-level fields
    required = [
        "experiment", "evidence_class", "source_identity", "frozen_plan_commit",
        "amendment_commit", "first_reveal_timestamp", "seed", "holdout_folios",
        "qualifying_chains", "power_branch", "decision",
    ]
    for k in required:
        check(k in res, f"missing field: {k}")
    check(res.get("experiment") == "E006", "experiment != E006")
    check(res.get("evidence_class") == "FROZEN_HOLDOUT", "evidence_class != FROZEN_HOLDOUT")

    # source identity: recompute from disk
    raw = DATA.read_bytes()
    check(git_blob_sha1(raw) == EXPECTED_BLOB, "git blob sha1 mismatch vs upstream")
    check(res["source_identity"]["git_blob_sha1"] == EXPECTED_BLOB, "results blob sha1 wrong")
    check(res["source_identity"]["sha256"] == hashlib.sha256(raw).hexdigest(),
          "results sha256 does not match data on disk")

    # frozen constants
    fc = res.get("frozen_constants", {})
    check(res.get("seed") == 20260831, "seed changed")
    check(res.get("resamples", 0) >= 1000, "resamples < 1000")
    check(set(fc.get("stems", [])) == STEMS_SET, "stems changed")
    check(set(fc.get("finals", [])) == FINALS_SET, "finals changed")
    check(fc.get("n_min") == 2 and fc.get("power_floor") == 3, "n_min/power_floor changed")
    check(fc.get("holdout_folds") == list(HOLDOUT_FOLDS), "holdout folds changed")
    check(fc.get("development_folds") == list(DEVELOPMENT_FOLDS), "development folds changed")

    # holdout membership: every listed folio hashes into {3,4}; none into dev
    for f in res["holdout_folios"]:
        check(folio_fold(f) in HOLDOUT_FOLDS, f"folio {f} not in holdout folds")
        check(folio_fold(f) not in DEVELOPMENT_FOLDS, f"folio {f} leaks into dev folds")

    # independent re-derivation of qualifying chains + counts
    qual, tot, distinct = independent_qualifying()
    check(sorted(res["qualifying_chains"]) == qual,
          f"qualifying chains mismatch: results={sorted(res['qualifying_chains'])} indep={qual}")
    check(res["counts"]["holdout_occurrences_fused"] == tot["fused"],
          "fused occurrence count mismatch")
    check(res["counts"]["holdout_occurrences_spaced"] == tot["spaced"],
          "spaced occurrence count mismatch")
    check(res["counts"]["distinct_holdout_chains"] == distinct,
          "distinct chain count mismatch")

    # decision-rule arithmetic from raw numbers
    n_qual = len(qual)
    if n_qual < 3:
        check(res["power_branch"] == "INCONCLUSIVE_UNDERPOWERED",
              "power_branch should be INCONCLUSIVE_UNDERPOWERED")
        check(res["decision"] == "INCONCLUSIVE_UNDERPOWERED",
              "decision should be INCONCLUSIVE_UNDERPOWERED")
        for k in ("D_obs", "N1", "N2", "N3", "leave_one_chain_out"):
            check(res.get(k) is None, f"{k} must be null in underpowered branch")
    else:
        check(res["power_branch"] == "POWERED", "power_branch should be POWERED")
        p1 = res["N1"]["p_value"]
        n2 = res["N2"]
        loo = res["leave_one_chain_out"]
        check(finite(p1) and 0.0 <= p1 <= 1.0, "N1 p out of range")
        primary_ok = p1 < 0.05
        if n2.get("status") == "DEGENERATE":
            check(res["decision"] == "INVALID_N2_DEGENERATE_GATE_NOT_CLEARABLE",
                  "degenerate N2 must block full gate")
        else:
            p2 = n2["p_value"]
            check(finite(p2) and 0.0 <= p2 <= 1.0, "N2 p out of range")
            loo_ok = all(v["N1_p_without"] < 0.10 for v in loo.values()) if loo else False
            expect = "SUPPORTED" if (primary_ok and p2 < 0.05 and loo_ok) else "WEAKENED_NOT_SUPPORTED"
            check(res["decision"] == expect,
                  f"decision {res['decision']} inconsistent with gate (expected {expect})")

    # numeric sanity: no NaN/Inf anywhere numeric
    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for idx, v in enumerate(o):
                walk(v, f"{path}[{idx}]")
        else:
            check(finite(o) if isinstance(o, float) else True, f"non-finite at {path}: {o}")
    walk(res)

    return _report()


def _report() -> int:
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E006_RESULTS_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
