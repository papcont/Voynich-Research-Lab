"""Independent validator for E020 results.json: re-scores the saved MIX(p*) prediction
text and the size-matched Voynich text with the E012 validator's independent Signature-G,
recomputes the selectivity share with its own decomposition, and re-derives H030a-c.
Calibration values are checked for internal consistency (p* = argmin on the recorded grid)."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V12 = _load("e012_validate", ROOT / "experiments" / "E012_reference_signature" / "validate.py")
V11 = V12.V11
EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E020"
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= 1e-6 * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def load(name):
    d = json.loads((RUNS / name).read_text(encoding="utf-8"))
    return {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}, d["order"]


def top1(lines, order):
    rr = V12.rows(lines, order)
    sigma = len({c for r in rr for c in r["v"]})
    p0 = V11.crossfit(rr, {}, sigma); pS = V11.crossfit(rr, {0: ("S",)}, sigma)
    by = defaultdict(float)
    for r, g in zip(rr, p0 - pS):
        by[r["S"]] += g
    tot = float((p0 - pS).sum())
    return max(by.values()) / tot


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    cal = res["calibration"]["grid_delta_S"]; t = res["calibration"]["target"]
    best = min(abs(v - t) for v in cal.values())
    p_star = max(float(p) for p, v in cal.items() if abs(v - t) == best)
    check(abs(p_star - res["calibration"]["p_star"]) < 1e-9, "p*")
    mt, mo = load("MIX_N_ITA.json")
    comp = V12.components(mt, mo)
    for X in V12.COMPS:
        close(comp[X], res["MIX_signature"][X], f"MIX {X}")
    V = res["voynich_reference"]
    dS = abs(comp["delta_S"] - V["delta_S"])
    check(res["hypothesis_outcomes"]["H030a"] == ("SUPPORTED" if dS <= 0.05 else "FALSIFIED" if dS > 0.10 else "PARTIAL"), "H030a")
    within = sum(abs(comp[X] - V[X]) <= (0.05 if X in ("delta_L", "delta_C") else 0.02) for X in ("delta_L", "delta_C", "TTR", "H1", "F_excess", "dJ_order"))
    check(res["hypothesis_outcomes"]["H030b"] == ("SUPPORTED" if within >= 4 else "FALSIFIED" if within <= 1 else "PARTIAL"), "H030b")
    vt, vo = load("V_matched.json")
    sv, sm = top1(vt, vo), top1(mt, mo)
    close(sv, res["selectivity"]["voynich"]["top1_share"], "top1 V"); close(sm, res["selectivity"]["mix"]["top1_share"], "top1 MIX")
    diff = sm - sv
    check(res["hypothesis_outcomes"]["H030c"] == ("SUPPORTED" if diff >= -0.10 else "FALSIFIED" if diff < -0.20 else "PARTIAL"), "H030c")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E020_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
