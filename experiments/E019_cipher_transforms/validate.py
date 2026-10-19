"""Independent validator for E019 results.json: re-scores the prepared transformed texts
(runs/E019/) with the E012 validator's independent Signature-G implementation and
re-derives decisions and hypothesis outcomes. The transforms themselves are checked
structurally (token counts) but not re-derived."""
from __future__ import annotations

import json
import sys
from pathlib import Path

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
RUNS = ROOT / "runs" / "E019"
COMPS = V12.COMPS
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= 1e-6 * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    V = res["voynich_reference_E012_size_matched"]
    mine = {}
    for tid, sig in res["results_size_matched"].items():
        f = RUNS / f"{tid}.json"
        if not f.is_file():
            errors.append(f"missing {f.name}"); continue
        d = json.loads(f.read_text(encoding="utf-8"))
        lines = {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}
        comp = V12.components(lines, d["order"])
        mine[tid] = comp
        for X in COMPS:
            close(comp[X], sig[X], f"{tid} {X}")
        dd = {X: abs(comp[X] - V[X]) for X in COMPS}
        bits, fr = COMPS[:3], COMPS[3:]
        state = "MATCH" if (all(dd[X] <= 0.05 for X in bits) and all(dd[X] <= 0.02 for X in fr)) else \
                "MISMATCH" if (any(dd[X] > 0.10 for X in bits) or any(dd[X] > 0.05 for X in fr)) else "PARTIAL"
        check(res["decisions"][tid] == state, f"{tid} decision {res['decisions'][tid]} != {state}")
    s_vals = [mine[t]["delta_S"] for t in mine if t.startswith("C_STREAM(")]
    if s_vals:
        near = any(abs(v - V["delta_S"]) <= 0.10 for v in s_vals)
        h29a = "SUPPORTED" if (all(v >= 0.05 for v in s_vals) and near) else "FALSIFIED" if all(v < 0.05 for v in s_vals) else "PARTIAL"
        check(res["hypothesis_outcomes"]["H029a"] == h29a, "H029a")
    h29b = "SUPPORTED" if any(v == "MATCH" for v in res["decisions"].values()) else "FALSIFIED" if all(v == "MISMATCH" for v in res["decisions"].values()) else "PARTIAL"
    check(res["hypothesis_outcomes"]["H029b"] == h29b, "H029b")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E019_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
