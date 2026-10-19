"""E013 — first Gate v2 lockbox claim: P70 four-slot model on the independent non-running
text (ONE RUN).

Implements experiments/E013_nonrunning_lockbox_claim/PLAN.md. Model definitions are
imported from the frozen E007 runner (segmenters, A8 builder, model-bit table, KT
prequential coder) so that nothing is redefined. Writes results.json and the Gate v2 claim
record BEFORE any interpretation.

Run:  python experiments/E013_nonrunning_lockbox_claim/run.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "E007_p70_replication"))

import run as E007  # noqa: E402  (frozen E007 definitions)
from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.mdl import KTCoder  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402
from voynichlab.gate import bootstrap_mean_ci  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
LOCKBOX_ID = "LOCKBOX_NONRUNNING_V1"
MARGIN = 0.5
SEED_PERM = 20261019
MODELS = E007.MODELS  # ("P70","A0","A1","A2","A3","A5","A6","A7","A8")


class Tok:
    __slots__ = ("value", "folio", "language")

    def __init__(self, value, folio, language):
        self.value, self.folio, self.language = value, folio, language


def load():
    lock, dev = defaultdict(list), defaultdict(list)
    for rec, _i, t in iter_strict_tokens(parse_ivtff(DATA)):
        (dev if is_running_text(rec.locator) else lock)[rec.folio].append(Tok(t.value, rec.folio, rec.meta.language))
    order = lambda d, key=None: [t for f in sorted(d, key=key) for t in d[f]]  # noqa: E731
    return order(lock), order(lock, E007.natural_folio_key), order(dev), lock


def folio_rows(tokens, per_cand, per_null, model_bits_cand, model_bits_null):
    bits_c, bits_n, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for t, c, u in zip(tokens, per_cand, per_null):
        bits_c[t.folio] += c; bits_n[t.folio] += u; n[t.folio] += 1
    N = len(tokens)
    rows, diffs = [], []
    for f in sorted(n):
        rows.append({"folio": f, "n_tokens": n[f], "candidate_data_bits": bits_c[f],
                     "null_total_bits": bits_n[f] + model_bits_null * n[f] / N})
        diffs.append(((bits_n[f] + model_bits_null * n[f] / N) - (bits_c[f] + model_bits_cand * n[f] / N)) / n[f])
    return rows, np.array(diffs)


def main() -> int:
    raw = DATA.read_bytes()
    if E007.git_blob_sha1(raw) != EXPECTED_BLOB:
        raise SystemExit("source identity mismatch")
    registry = json.loads((ROOT / "research" / "holdout_registry.json").read_text(encoding="utf-8"))
    lb = registry["lockboxes"][LOCKBOX_ID]
    lock, lock_nat, dev, lock_by_folio = load()
    folios = sorted(lock_by_folio)
    if folios != sorted(lb["folios"]) or len(lock) != lb["n_tokens"]:
        raise SystemExit("lockbox mismatch with registry")
    N = len(lock)
    sigma_chars = sorted({c for t in lock for c in t.value})
    sigma = len(sigma_chars)
    text_sha = hashlib.sha256("\n".join(t.value for t in lock).encode()).hexdigest()

    seg_a8, a8_profile = E007.build_a8(dev)  # profile from the running-text pool, never the lockbox
    segs = {"P70": parse_p70, "A0": lambda t: (t,), "A1": E007.seg_a1, "A2": E007.seg_a2, "A3": E007.seg_a3,
            "A5": E007.seg_a5, "A6": E007.seg_a6, "A7": E007.seg_a7, "A8": seg_a8}
    for m in MODELS:
        assert all("".join(segs[m](t.value)) == t.value for t in lock), m
    mb = {m: v["model_bits"] for m, v in E007.model_bits_table(sigma).items()}

    # ---- primary arm: pure prequential on the lockbox ----
    per = {m: E007.prequential(segs[m], lock, sigma)[0] for m in MODELS}
    primary = {m: {"data_bits_per_token": float(per[m].mean()), "model_bits": mb[m],
                   "total_bits_per_token": float(per[m].mean()) + mb[m] / N} for m in MODELS}
    rows, diffs = folio_rows(lock, per["P70"], per["A0"], mb["P70"], mb["A0"])
    mean, lo, hi = bootstrap_mean_ci(diffs, 10000, 20261019, 0.025)
    gate_state = "PASS" if (mean >= MARGIN and lo > 0) else "FAIL" if hi < MARGIN else "INCONCLUSIVE"
    lowest = min(MODELS, key=lambda m: primary[m]["total_bits_per_token"])
    strict = gate_state == "PASS" and lowest == "P70"

    # ---- secondary arm: transfer with running-text-trained counts ----
    secondary = {}
    for m in MODELS:
        coder = KTCoder(sigma_dev := len({c for t in dev for c in t.value}))
        cache = {}
        for t in dev:
            sl = cache.get(t.value) or cache.setdefault(t.value, segs[m](t.value))
            for i, v in enumerate(sl):
                coder.update((i, sl[:i]), v)
        tot = 0.0
        for t in lock:
            sl = segs[m](t.value)
            tot += sum(coder.cost((i, sl[:i]), v) for i, v in enumerate(sl))
        secondary[m] = tot / N
    # ---- controls / sensitivities (reported) ----
    rng = np.random.default_rng(SEED_PERM)
    perm_lock = []
    for f in sorted(lock_by_folio):
        g = lock_by_folio[f]
        for j in rng.permutation(len(g)):
            perm_lock.append(g[j])
    ctrl = {m: float(E007.prequential(segs[m], perm_lock, sigma)[0].mean()) + mb[m] / N for m in ("P70", "A0")}
    nat = {m: float(E007.prequential(segs[m], lock_nat, sigma)[0].mean()) for m in ("P70", "A0")}
    diffs_all_wins = int((diffs > 0).sum())

    result = {
        "experiment": "E013", "hypothesis": "H019", "evidence_class": "FROZEN_HOLDOUT (Gate v2 lockbox, INDEPENDENT)",
        "gate_level_target": "STRUCTURAL_MODEL_VALIDATED", "lockbox_id": LOCKBOX_ID, "lockbox_sha256": lb["sha256"],
        "frozen_plan_commit": "15f72da", "run_head_commit": E007.head_commit(),
        "first_reveal_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest(), "lockbox_text_sha256": text_sha},
        "population": {"n_tokens": N, "n_folios": len(folios), "sigma_size": sigma, "sigma": "".join(sigma_chars),
                       "n_types": len({t.value for t in lock}), "a8_profile": a8_profile},
        "primary_arm_pure_prequential": primary,
        "gate_statistics": {"margin": MARGIN, "mean_delta_bits_per_token": mean, "ci_lower": lo, "ci_upper": hi,
                            "n_folios": len(rows), "folio_wins": diffs_all_wins, "state": gate_state,
                            "lowest_total_model": lowest, "STRICT_PASS": strict},
        "secondary_arm_transfer_bits_per_token": secondary,
        "control_within_folio_permutation_total_bits_per_token": ctrl,
        "sensitivity_natural_order_data_bits_per_token": nat,
        "claim_ceiling": "Structural model on non-running text; Gate v2 level 1 only.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    exp = json.loads((EXP_DIR / "experiment.json").read_text(encoding="utf-8"))
    claim = {
        "claim_id": "E013_P70_nonrunning_transfer", "registered_utc": exp["registered_utc"], "freeze_commit": "15f72da",
        "lockbox_id": LOCKBOX_ID, "lockbox_folios": folios, "retraction_condition": exp["retraction_condition"],
        "post_reveal_changes": False, "sha256": exp["sha256"],
        "compression": {
            "folios": rows,
            "candidate_model_bits": {"mechanism_code_bits": mb["P70"], "dictionary_bits": 0, "key_bits": 0,
                                     "exception_bits": 0, "residual_bits": 0, "transmission_bits": 0},
            "reconstruction_sha256": text_sha, "lockbox_text_sha256": text_sha,
            "margin": exp["margin"],
            "controls": {"folio_internal_permutation": {"candidate_total_bits_per_token": ctrl["P70"],
                                                        "null_total_bits_per_token": ctrl["A0"]}},
        },
    }
    (EXP_DIR / "claim_E013_P70.json").write_text(json.dumps(claim, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"gate": result["gate_statistics"],
                      "primary_total_bpt": {m: round(v["total_bits_per_token"], 3) for m, v in primary.items()},
                      "secondary": {m: round(v, 3) for m, v in secondary.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
