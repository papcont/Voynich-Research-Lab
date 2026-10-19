"""Independent validator for E021 results.json: own S1 (joint-count mutual information and
binary-contrast search) on the saved texts, own delta_S' via the E012 validator path, own
decisions. Calibration checked for argmin consistency; the processes are not re-derived."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
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
EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= 1e-6 * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def load(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}, d["order"]


def mi_table(tab):
    n = sum(tab.values())
    ra, cb = Counter(), Counter()
    for (a, b), c in tab.items():
        ra[a] += c; cb[b] += c
    return sum(c / n * math.log2(c * n / (ra[a] * cb[b])) for (a, b), c in tab.items())


def s1(lines, order):
    tab = Counter()
    for u in order:
        for _l, _s, full in lines[u]:
            for i in range(1, len(full)):
                if not full[i][1] and not full[i - 1][1]:
                    tab[(full[i - 1][0][-1], full[i][0][0])] += 1
    I = mi_table(tab)
    best = -1
    for (a0, b0) in list(tab):
        bt = Counter()
        for (a, b), c in tab.items():
            bt[(a == a0, b == b0)] += c
        best = max(best, mi_table(bt))
    return best / I


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    paths = {"V": RUNS / "E021" / "V_matched.json", "C_STREAM(N_DEU)": RUNS / "E019" / "C_STREAM(N_DEU).json",
             "C_STREAM(N_ITA)": RUNS / "E019" / "C_STREAM(N_ITA).json", "MIX(0.8)(N_ITA)": RUNS / "E020" / "MIX_N_ITA.json",
             "N_DEU": RUNS / "E012" / "N_DEU_matched.json", "N_ITA": RUNS / "E012" / "N_ITA_matched.json"}
    mine = {}
    for k, p in paths.items():
        if not p.is_file():
            errors.append(f"missing {p}"); continue
        lines, order = load(p)
        mine[k] = s1(lines, order)
        close(mine[k], res["S1"][k]["S1"], f"S1 {k}")
    for proc in ("SEL_L", "SEL_M"):
        cal = res["calibration"]["grid"][proc]; t = res["calibration"]["target"]
        best = min(abs(v - t) for v in cal.values())
        star = max(float(g) for g, v in cal.items() if abs(v - t) == best)
        check(abs(star - res["calibration"]["star"][proc]) < 1e-9, f"{proc} star")
        lines, order = load(RUNS / "E021" / f"{proc}_N_ITA.json")
        comp = V12.components(lines, order)
        close(comp["delta_S"], res["predictions_N_ITA"][proc]["signature"]["delta_S"], f"{proc} delta_S")
        s = s1(lines, order)
        close(s, res["predictions_N_ITA"][proc]["S1"]["S1"], f"{proc} S1")
        dd, ds = abs(comp["delta_S"] - t), abs(s - mine["V"])
        v = "SUPPORTED" if (dd <= 0.05 and ds <= 0.10) else "FALSIFIED" if (dd > 0.10 or ds > 0.20) else "PARTIAL"
        check(res["predictions_N_ITA"][proc]["verdict"] == v, f"{proc} verdict")
    others = ["N_DEU", "N_ITA", "C_STREAM(N_DEU)", "C_STREAM(N_ITA)", "MIX(0.8)(N_ITA)"]
    if all(k in mine for k in others + ["V"]):
        sv = mine["V"]
        h31 = "SUPPORTED" if all(sv >= mine[x] + 0.10 for x in others) else "FALSIFIED" if any(mine[x] >= sv for x in others) else "PARTIAL"
        check(res["hypothesis_outcomes"]["H031"] == h31, "H031")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E021_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
