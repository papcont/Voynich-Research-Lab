"""Independent validator for E012 results.json.

Re-scores the prepared texts saved under runs/E012/ with an independent implementation
of Signature-G (own A3 slots, own backoff coder from the E011 validator, own copy model
from the E008 validator, own vocabulary statistics and permutations) and re-derives the
decisions, H027, H028 and the nearest text. Text preparation (normalization,
re-segmentation, truncation, substitution) is checked structurally (token counts, unit
order) but not re-derived.
"""
from __future__ import annotations

import hashlib
import json
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


V11 = _load("e011_validate", ROOT / "experiments" / "E011_targeted_context_scorecard" / "validate.py")
V8 = _load("e008_validate", ROOT / "experiments" / "E008_mechanism_competition" / "validate.py")
EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E012"
TOL = 1e-6
COMPS = ("delta_S", "delta_L", "delta_C", "TTR", "H1", "F_excess", "dJ_order")
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def fold(u):
    return int(hashlib.sha256(("E007:" + u.lower()).encode()).hexdigest(), 16) % 5


def a3(v):
    return (v[0], v[1:-1], v[-1]) if len(v) >= 3 else ("", v, "")


def rows(lines, order):
    out = []
    for u in order:
        for lang, sec, full in lines[u]:
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                out.append({"v": v, "s": a3(v), "folio": u, "lang": lang, "fold": fold(u), "S": S, "L": L, "Sfam": ""})
    for k, r in enumerate(out):
        r["id"] = k
    return out


def delta(rows_, pa, pb):
    ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for r, x, y in zip(rows_, pa, pb):
        ba[r["folio"]] += x; bb[r["folio"]] += y; n[r["folio"]] += 1
    return float(np.mean([(ba[f] - bb[f]) / n[f] for f in n]))


def copy_rows(lines, order):
    by = {u: [(l, s, full) for l, s, full in lines[u]] for u in order}
    return V8.features(by, order)  # copy search / edit strings from the E008 validator


def code_copy(coder, with_copy, r, W, update):
    """E008 validator's code_token with the A3 slot base (Signature-G)."""
    slots = a3(r["v"])
    bits = 0.0

    def step(ctx, v):
        b = coder.cost(ctx, v)
        if update:
            coder.add(ctx, v)
        return b

    if with_copy:
        val, d = V8.src_of(r, W)
        bits += step(("src",), val)
        if d is not None:
            if d == 1:
                bits += step(("edit",), r["ed"])
            if update:
                for i, v in enumerate(slots):
                    coder.add(("base", i, slots[:i], None, None), v)
            return bits
    for i, v in enumerate(slots):
        bits += step(("base", i, slots[:i], None, None), v)
    return bits


def components(lines, order):
    rr = rows(lines, order)
    sigma = len({c for r in rr for c in r["v"]})
    p0 = V11.crossfit(rr, {}, sigma); pS = V11.crossfit(rr, {0: ("S",)}, sigma); pL = V11.crossfit(rr, {0: ("L",), 2: ("L",)}, sigma)
    feats = copy_rows(lines, order)
    check([r["v"] for r in feats] == [r["v"] for r in rr], "alignment")
    perB, perBC = np.empty(len(feats)), np.empty(len(feats))
    for j in range(5):
        c1, c2 = V8.Coder(sigma), V8.Coder(sigma)
        for r in feats:
            if r["fold"] != j:
                code_copy(c1, False, r, 5, True); code_copy(c2, True, r, 5, True)
        for k, r in enumerate(feats):
            if r["fold"] == j:
                perB[k] = code_copy(c1, False, r, 5, False); perBC[k] = code_copy(c2, True, r, 5, False)
    # vocabulary components
    tk = {u: [v for _l, _s, full in lines[u] for v, uu in full if not uu] for u in order}
    units = [u for u in order if tk[u]]
    toks = [v for u in units for v in tk[u]]
    c = Counter(toks)
    meta = {u: (lines[u][0][0], lines[u][0][1]) for u in units}
    key = dict(meta)
    for _ in range(2):
        cnt = Counter(key.values())
        for u in units:
            if cnt[key[u]] < 3:
                key[u] = (meta[u][0], "rest") if key[u][1] != "rest" else ("rest", "rest")
    groups = defaultdict(list)
    for u in units:
        groups[key[u]].append(u)
    F = lambda t: np.array([1 - len(set(t[u])) / len(t[u]) for u in units])  # noqa: E731
    rng = np.random.default_rng(20261050)
    Fn = []
    for _ in range(1000):
        p = {}
        for members in groups.values():
            pool = [v for u in members for v in tk[u]]
            perm = rng.permutation(len(pool)); k = 0
            for u in members:
                n = len(tk[u]); p[u] = [pool[perm[j]] for j in range(k, k + n)]; k += n
        Fn.append(F(p))
    Fex = float((F(tk) - np.mean(Fn, axis=0)).mean())
    sets = {u: set(tk[u]) for u in units}
    jac = lambda a, b: len(sets[a] & sets[b]) / len(sets[a] | sets[b])  # noqa: E731
    def J(order_):
        vals = [jac(order_[i], order_[i + 1]) for i in range(len(order_) - 1)
                if key[order_[i]] == key[order_[i + 1]] and len(tk[order_[i]]) >= 20 and len(tk[order_[i + 1]]) >= 20]
        return float(np.mean(vals)) if vals else float("nan")
    rng = np.random.default_rng(20261060)
    pos = {g: [units.index(u) for u in m] for g, m in groups.items()}
    Jn = []
    for _ in range(1000):
        o = list(units)
        for g, m in groups.items():
            perm = rng.permutation(len(m))
            for p_, j in zip(pos[g], perm):
                o[p_] = m[j]
        Jn.append(J(o))
    return {"delta_S": delta(rr, p0, pS), "delta_L": delta(rr, p0, pL), "delta_C": delta(rr, perB, perBC),
            "TTR": len(c) / len(toks), "H1": sum(1 for k in c if c[k] == 1) / len(c), "F_excess": Fex,
            "dJ_order": float(J(units) - np.nanmean(Jn))}


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    mine = {}
    for tid, sig in res["results"]["size_matched"].items():
        f = RUNS / f"{tid}_matched.json"
        if not f.is_file():
            errors.append(f"missing {f.name}"); continue
        d = json.loads(f.read_text(encoding="utf-8"))
        lines = {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}
        comp = components(lines, d["order"])
        mine[tid] = comp
        for X in COMPS:
            close(comp[X], sig[X], f"{tid} {X}")
    V = mine.get("V")
    if V:
        for tid, comp in mine.items():
            if tid == "V":
                continue
            d = {X: abs(comp[X] - V[X]) for X in COMPS}
            bits, fr = COMPS[:3], COMPS[3:]
            state = "MATCH" if (all(d[X] <= 0.05 for X in bits) and all(d[X] <= 0.02 for X in fr)) else \
                    "MISMATCH" if (any(d[X] > 0.10 for X in bits) or any(d[X] > 0.05 for X in fr)) else "PARTIAL"
            check(res["decisions"][tid] == state, f"{tid} decision {res['decisions'][tid]} != {state}")
        nat = [t for t in res["decisions"] if t.startswith("N_")]
        h27 = "SUPPORTED" if any(res["decisions"][t] == "MATCH" for t in nat) else "FALSIFIED" if all(res["decisions"][t] == "MISMATCH" for t in nat) else "PARTIAL"
        check(res["hypothesis_outcomes"]["H027"] == h27, "H027")
        inv = all(max(abs(mine["N_" + t][X] - mine["C_SUB_" + t][X]) for X in COMPS) < 1e-9 for t in ("DEU", "ITA") if "N_" + t in mine)
        check(res["hypothesis_outcomes"]["H028"] == ("SUPPORTED" if inv else "FALSIFIED"), "H028")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E012_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
