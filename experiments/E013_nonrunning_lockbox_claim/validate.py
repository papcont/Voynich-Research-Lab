"""Independent validator for E013 results.json / claim record.

Own lockbox extraction, own P70/A0 segmentation (and the E007 competitors written
independently as in E007's validate.py), own KT coder, own per-folio differences and
bootstrap; checks the gate statistics, the state, STRICT_PASS and the claim record's
rows. Exit non-zero on mismatch.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "E007_p70_replication"))
from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
import validate as V7  # noqa: E402  (E007 validator: independent segmenters + coder)

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
TOL = 1e-6
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    claim = json.loads((EXP / "claim_E013_P70.json").read_text(encoding="utf-8"))
    lock, dev = defaultdict(list), []
    for rec, _i, t in iter_strict_tokens(parse_ivtff(DATA)):
        if is_running_text(rec.locator):
            dev.append(t.value)
        else:
            lock[rec.folio].append(t.value)
    folios = sorted(lock)
    toks = [v for f in folios for v in lock[f]]
    N = len(toks)
    sigma = len({c for v in toks for c in v})
    check(N == res["population"]["n_tokens"] and len(folios) == res["population"]["n_folios"], "population")
    check(hashlib.sha256("\n".join(toks).encode()).hexdigest() == res["source_identity"]["lockbox_text_sha256"], "text hash")
    check(claim["compression"]["reconstruction_sha256"] == claim["compression"]["lockbox_text_sha256"], "claim reconstruction hash")
    segs = V7.segmenters(dev)  # A8 profile from the running-text pool, as frozen
    eg = lambda k: 2 * int(math.floor(math.log2(k))) + 1  # noqa: E731
    inv = {"P70": V7.PFX + V7.GAL + V7.SUF, "A0": [], "A1": V7.PFX, "A2": V7.SUF, "A3": [], "A5": V7.PFX + V7.GAL + V7.SUF,
           "A6": V7.PFX + V7.GAL, "A7": ["o", "y", "d", "s", "qo", "ch", "sh"] + V7.GAL + V7.SUF, "A8": []}
    ns = {"P70": 4, "A0": 1, "A1": 2, "A2": 2, "A3": 3, "A5": 3, "A6": 3, "A7": 4, "A8": 4}
    mb = {m: sum((len(s) + 1) * math.log2(sigma + 1) for s in inv[m]) + eg(ns[m]) + (eg(20260908) if m == "A8" else 0) for m in V7.MODELS}
    per = {}
    for m in V7.MODELS:
        per[m] = V7.code(segs[m], toks, sigma)
        close(sum(per[m]) / N, res["primary_arm_pure_prequential"][m]["data_bits_per_token"], f"{m} data bpt")
        close(sum(per[m]) / N + mb[m] / N, res["primary_arm_pure_prequential"][m]["total_bits_per_token"], f"{m} total bpt")
    # folio differences, bootstrap, state
    k = 0
    diffs, rows = [], {r["folio"]: r for r in claim["compression"]["folios"]}
    for f in folios:
        n = len(lock[f])
        c = sum(per["P70"][k:k + n]); u = sum(per["A0"][k:k + n]); k += n
        close(rows[f]["candidate_data_bits"], c, f"claim row {f} candidate")
        close(rows[f]["null_total_bits"], u + mb["A0"] * n / N, f"claim row {f} null")
        diffs.append(((u + mb["A0"] * n / N) - (c + mb["P70"] * n / N)) / n)
    d = np.array(diffs)
    rng = np.random.default_rng(20261019)
    means = d[rng.integers(0, len(d), size=(10000, len(d)))].mean(axis=1)
    mean, lo, hi = float(d.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))
    g = res["gate_statistics"]
    close(mean, g["mean_delta_bits_per_token"], "mean delta"); close(lo, g["ci_lower"], "ci lower"); close(hi, g["ci_upper"], "ci upper")
    state = "PASS" if (mean >= 0.5 and lo > 0) else "FAIL" if hi < 0.5 else "INCONCLUSIVE"
    check(g["state"] == state, f"state {g['state']} != {state}")
    lowest = min(V7.MODELS, key=lambda m: sum(per[m]) / N + mb[m] / N)
    check(g["lowest_total_model"] == lowest, "lowest model")
    check(g["STRICT_PASS"] == (state == "PASS" and lowest == "P70"), "STRICT_PASS")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E013_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
