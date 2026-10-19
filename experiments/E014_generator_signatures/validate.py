"""Independent validator for E014 results.json.

Recomputes the three signature components with its own coders (backoff coder from the
E011 validator's definition; plain-KT copy model from the E008 validator's definition)
on the generated texts saved under runs/E014/ (git-ignored) and on the real skeleton,
and re-derives the decisions and hypothesis outcomes. The generation step itself is
not re-derived (it is a seeded sampling procedure); only its outputs are re-scored.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
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


V11 = _load("e011_validate", ROOT / "experiments" / "E011_targeted_context_scorecard" / "validate.py")  # backoff coder
V8 = _load("e008_validate", ROOT / "experiments" / "E008_mechanism_competition" / "validate.py")  # copy model
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E014"
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
TOL = 1e-6
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def fold(f):
    import hashlib
    return int(hashlib.sha256(("E007:" + f.lower()).encode()).hexdigest(), 16) % 5


def real_lines():
    out = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            out[rec.folio].append([rec.meta.language, rec.meta.illustration, full])
    return out


def rows_from_lines(lines):
    rows = []
    for folio in sorted(lines):
        for lang, sec, full in lines[folio]:
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                rows.append({"v": v, "s": parse_p70(v), "folio": folio, "lang": lang, "fold": fold(folio), "S": S, "L": L, "Sfam": ""})
    return rows


def delta(rows, pa, pb):
    ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for r, x, y in zip(rows, pa, pb):
        ba[r["folio"]] += x; bb[r["folio"]] += y; n[r["folio"]] += 1
    fol = sorted(n)
    d = np.array([(ba[f] - bb[f]) / n[f] for f in fol])
    rng = np.random.default_rng(20261019)
    means = d[rng.integers(0, len(d), size=(10000, len(d)))].mean(axis=1)
    return float(d.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def components(lines):
    rows = rows_from_lines(lines)
    sigma = len({c for r in rows for c in r["v"]})
    p0 = V11.crossfit(rows, {}, sigma)
    pS = V11.crossfit(rows, {0: ("S",)}, sigma)
    pL = V11.crossfit(rows, {0: ("L",), 3: ("L",)}, sigma)
    # Δ_C with the E008 validator's features/coder (W=5), 5-fold cross-fit
    by_folio = {f: [(lang, sec, full) for lang, sec, full in lines[f]] for f in lines}
    feats = V8.features(by_folio, sorted(by_folio))
    check([r["v"] for r in feats] == [r["v"] for r in rows], "token alignment")
    perB1, perB1C = np.empty(len(feats)), np.empty(len(feats))
    for j in range(5):
        c1, c2 = V8.Coder(sigma), V8.Coder(sigma)
        for r in feats:
            if r["fold"] != j:
                V8.code_token(c1, ("B1", frozenset()), r, 5, True)
                V8.code_token(c2, ("B1", frozenset("C")), r, 5, True)
        for k, r in enumerate(feats):
            if r["fold"] == j:
                perB1[k] = V8.code_token(c1, ("B1", frozenset()), r, 5, False)
                perB1C[k] = V8.code_token(c2, ("B1", frozenset("C")), r, 5, False)
    return {"delta_S": delta(rows, p0, pS), "delta_L": delta(rows, p0, pL), "delta_C": delta(rows, perB1, perB1C)}


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    voy = components(real_lines())
    for X in ("delta_S", "delta_L", "delta_C"):
        close(voy[X][0], res["voynich_reference_EXPLORATORY"][X]["mean"], f"voynich {X}")
    for name, r in res["generators"].items():
        means = {X: [] for X in ("delta_S", "delta_L", "delta_C")}
        for seed, per in zip(res["seeds"], r["per_seed"]):
            f = RUNS / f"{name}_{seed}.json"
            if not f.is_file():
                errors.append(f"missing generated text {f.name} (runs/ is git-ignored; re-run run.py)")
                continue
            lines = json.loads(f.read_text(encoding="utf-8"))
            comp = components(lines)
            for X in means:
                close(comp[X][0], per[X]["mean"], f"{name} {seed} {X}")
                means[X].append(comp[X][0])
        if all(means.values()):
            d = {X: abs(float(np.mean(means[X])) - voy[X][0]) for X in means}
            state = "SIGNATURE_MATCH" if all(v <= 0.05 for v in d.values()) else "SIGNATURE_MISMATCH" if any(v > 0.10 for v in d.values()) else "PARTIAL"
            check(r["decision"] == state, f"{name} decision {r['decision']} != {state}")
    h20 = res["generators"]["G3_SC"]["decision"]; h21 = res["generators"]["G4_EDGE"]["decision"]
    exp = lambda s: "FALSIFIED" if s == "SIGNATURE_MISMATCH" else "SUPPORTED" if s == "SIGNATURE_MATCH" else "PARTIAL"  # noqa: E731
    check(res["hypothesis_outcomes"] == {"H020": exp(h20), "H021": exp(h21)}, "hypothesis outcomes")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E014_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
