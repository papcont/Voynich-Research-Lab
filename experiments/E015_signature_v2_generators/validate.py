"""Independent validator for E015 results.json.

Re-scores the saved generated texts (runs/E015/, git-ignored) and the real skeleton with
the E014 validator's independent sequence components plus own inventory/sharing
statistics; re-derives decisions and hypothesis outcomes. The seeded generation step is
not re-derived.
"""
from __future__ import annotations

import json
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


V14 = _load("e014_validate", ROOT / "experiments" / "E014_generator_signatures" / "validate.py")
EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E015"
TOL = 1e-6
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def inventory(lines):
    per = {f: [v for _l, _s, full in lines[f] for v, u in full if not u] for f in lines}
    toks = [v for f in sorted(per) for v in per[f]]
    c = Counter(toks)
    types_per = {f: set(t) for f, t in per.items() if t}
    occ = Counter(ty for s in types_per.values() for ty in s)
    return {"TTR": len(c) / len(toks), "H1": sum(1 for k in c if c[k] == 1) / len(c),
            "F": float(np.mean([1 - len(set(t)) / len(t) for t in per.values() if t])),
            "X": float(np.mean([np.mean([occ[ty] > 1 for ty in s]) for s in types_per.values()]))}


def flat(lines):
    comp = V14.components(lines)
    out = {X: comp[X][0] for X in ("delta_S", "delta_L", "delta_C")}
    out.update(inventory(lines))
    return out


def decide(means, voy):
    bits, fr = ("delta_S", "delta_L", "delta_C"), ("TTR", "H1", "F", "X")
    d = {X: abs(means[X] - voy[X]) for X in bits + fr}
    if all(d[X] <= 0.05 for X in bits) and all(d[X] <= 0.02 for X in fr):
        return "MATCH"
    if any(d[X] > 0.10 for X in bits) or any(d[X] > 0.05 for X in fr):
        return "MISMATCH"
    return "PARTIAL"


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    voy = flat(V14.real_lines())
    for X, v in voy.items():
        close(v, res["voynich_reference_EXPLORATORY"]["flat"][X], f"voynich {X}")
    for name, r in res["generators"].items():
        acc = []
        for seed, per in zip(res["seeds"], r["per_seed"]):
            f = RUNS / f"{name}_{seed}.json"
            if not f.is_file():
                errors.append(f"missing generated text {f.name}")
                continue
            fl = flat(json.loads(f.read_text(encoding="utf-8")))
            for X in ("delta_S", "delta_L", "delta_C"):
                close(fl[X], per["sequence"][X]["mean"], f"{name} {seed} {X}")
            for X in ("TTR", "H1", "F", "X"):
                close(fl[X], per["inventory"][X], f"{name} {seed} {X}")
            acc.append(fl)
        if acc:
            means = {X: float(np.mean([a[X] for a in acc])) for X in acc[0]}
            check(decide(means, voy) == r["decision"], f"{name} decision")
    hyp = lambda s: "FALSIFIED" if s == "MISMATCH" else "SUPPORTED" if s == "MATCH" else "PARTIAL"  # noqa: E731
    check(res["hypothesis_outcomes"] == {"H022": hyp(res["generators"]["G5_EDGE_PY"]["decision"]), "H023": hyp(res["generators"]["G6_FOLIO_SC"]["decision"])}, "hypotheses")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E015_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
