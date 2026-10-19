"""Independent validator for E007 results.json.

Re-derives the population, alphabet, all nine segmentations (own parser, not
voynichlab.p70 / run.py), an own KT prequential coder, cross-fitted folds,
dev->holdout arm, subset scores, R1 entropies, model bits, gate arithmetic and
the decision label. Exit non-zero on any mismatch.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
TOL = 1e-6

PFX = ["o", "y", "d", "s", "ch", "sh", "qo"]
GAL = ["k", "t", "p", "f", "ckh", "cth", "cph", "cfh"]
SUF = ["y", "edy", "ey", "eey", "eedy", "dy", "ody", "chy", "shy",
       "aiin", "ain", "iin", "n", "aiiin", "iiin", "oiin", "oiiin",
       "ol", "al", "l", "ar", "or", "r", "ir", "am", "m",
       "g", "he", "ee", "b", "ai", "a", "e", "s"]
MODELS = ["P70", "A0", "A1", "A2", "A3", "A5", "A6", "A7", "A8"]

errors: list[str] = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def close(a, b, msg):
    check(a is not None and b is not None and abs(a - b) <= TOL * max(1.0, abs(b)), f"{msg}: {a} vs {b}")


def fold_of(folio):
    return int(hashlib.sha256(("E007:" + folio.lower()).encode()).hexdigest(), 16) % 5


def running(locator):
    s = (locator or "").lstrip("@+*=&~/!")
    return s[:1] == "P"


def head(s, inv):
    m = [v for v in inv if s.startswith(v)]
    return max(m, key=len) if m else ""


def tail(s, inv):
    m = [v for v in inv if s.endswith(v)]
    return max(m, key=len) if m else ""


def p4(t, pfx=PFX, block=()):
    p = "" if any(t.startswith(b) for b in block) else head(t, pfx)
    r = t[len(p):]
    g = head(r, GAL)
    r = r[len(g):]
    s = tail(r, SUF)
    return p, g, r[:len(r) - len(s)], s


def segmenters(dev):
    pool = defaultdict(list)
    sums, total_len = [0, 0, 0, 0], 0
    for t in dev:
        lens = [len(x) for x in p4(t)]
        pool[len(t)].append(tuple(lens))
        sums = [a + b for a, b in zip(sums, lens)]
        total_len += len(t)
    for k in pool:
        pool[k].sort()
    fr = [x / total_len for x in sums]

    def a8(t):
        h = int(hashlib.sha256(("E007-A8|20260907|" + t).encode()).hexdigest(), 16)
        if len(t) in pool:
            lens = pool[len(t)][h % len(pool[len(t)])]
        else:
            L, c, b = len(t), 0.0, []
            for f in fr[:3]:
                c += f
                b.append(min(max(int(math.floor(L * c + 0.5)), b[-1] if b else 0), L))
            lens = (b[0], b[1] - b[0], b[2] - b[1], L - b[2])
        out, i = [], 0
        for n in lens:
            out.append(t[i:i + n])
            i += n
        return tuple(out)

    def a1(t):
        p = head(t, PFX)
        return (p, t[len(p):])

    def a2(t):
        s = tail(t, SUF)
        return (t[:len(t) - len(s)], s)

    def a5(t):
        p, g, c, s = p4(t)
        return (p, g + c, s)

    def a6(t):
        p, g, c, s = p4(t)
        return (p, g, c + s)

    return {
        "P70": p4, "A0": lambda t: (t,), "A1": a1, "A2": a2,
        "A3": lambda t: (t[0], t[1:-1], t[-1]) if len(t) >= 3 else ("", t, ""),
        "A5": a5, "A6": a6,
        "A7": lambda t: p4(t, ["o", "y", "d", "s", "qo"], ("ch", "sh")),
        "A8": a8,
    }


class Coder:
    def __init__(self, sigma):
        self.esc = math.log2(sigma + 1)
        self.n = defaultdict(int)
        self.c = defaultdict(Counter)

    def cost(self, ctx, v):
        n, cnt = self.n[ctx], self.c[ctx]
        d = n + 0.5 * (len(cnt) + 1)
        if v in cnt:
            return -math.log2((cnt[v] + 0.5) / d)
        return -math.log2(0.5 / d) + (len(v) + 1) * self.esc

    def add(self, ctx, v):
        self.n[ctx] += 1
        self.c[ctx][v] += 1


def code(seg, toks, sigma, train=None):
    c = Coder(sigma)
    if train is not None:
        for t in train:
            sl = seg(t)
            for i, v in enumerate(sl):
                c.add((i, sl[:i]), v)
    out = []
    for t in toks:
        sl = seg(t)
        b = 0.0
        for i, v in enumerate(sl):
            b += c.cost((i, sl[:i]), v)
            if train is None:
                c.add((i, sl[:i]), v)
        out.append(b)
    return out


def H(counter):
    n = sum(counter.values())
    return -sum(x / n * math.log2(x / n) for x in counter.values())


def main() -> int:
    check(DATA.is_file(), "source data missing")
    check((EXP / "results.json").is_file(), "results.json missing")
    if errors:
        return report()
    raw = DATA.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    check(blob == EXPECTED_BLOB, "source blob mismatch")
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    check(res["source_identity"]["git_blob_sha1"] == EXPECTED_BLOB, "results source blob")

    by_folio = defaultdict(list)
    for rec, _i, tok in iter_strict_tokens(parse_ivtff(DATA)):
        if running(rec.locator):
            by_folio[rec.folio].append((tok.value, rec.meta.language, rec.meta.illustration))
    rows = [(f,) + x for f in sorted(by_folio) for x in by_folio[f]]
    toks = [r[1] for r in rows]
    N = len(toks)
    sigma = len({ch for t in toks for ch in t})
    check(res["population"]["n_tokens"] == N, "n_tokens")
    check(res["population"]["sigma_size"] == sigma, "sigma")
    folds = [fold_of(r[0]) for r in rows]
    dev = [t for t, k in zip(toks, folds) if k in (0, 1, 2)]
    hold = [t for t, k in zip(toks, folds) if k in (3, 4)]
    segs = segmenters(dev)
    check(res["deferred_models"].get("A4", "").startswith("DEFERRED"), "A4 must be deferred")
    check(res["models"] == MODELS, "model set")

    # lossless + primary
    per = {}
    prim = res["R2"]["primary_global_prequential"]
    for m in MODELS:
        check(all("".join(segs[m](t)) == t for t in toks), f"{m} not lossless")
        per[m] = code(segs[m], toks, sigma)
        close(sum(per[m]) / N, prim[m]["data_bits_per_token"], f"{m} primary bits/token")

    # model bits
    inv = {"P70": PFX + GAL + SUF, "A0": [], "A1": PFX, "A2": SUF, "A3": [],
           "A5": PFX + GAL + SUF, "A6": PFX + GAL,
           "A7": ["o", "y", "d", "s", "qo", "ch", "sh"] + GAL + SUF, "A8": []}
    ns = {"P70": 4, "A0": 1, "A1": 2, "A2": 2, "A3": 3, "A5": 3, "A6": 3, "A7": 4, "A8": 4}
    eg = lambda k: 2 * int(math.floor(math.log2(k))) + 1  # noqa: E731
    for m in MODELS:
        mb = sum((len(s) + 1) * math.log2(sigma + 1) for s in inv[m]) + eg(ns[m]) + (eg(20260908) if m == "A8" else 0)
        close(mb, prim[m]["model_bits"], f"{m} model_bits")
        close((sum(per[m]) + mb) / N, prim[m]["total_bits_per_token"], f"{m} total bits/token")

    # cross-fitted folds + holdout arm
    cf = res["R2"]["cross_fitted_fold_bits_per_token"]
    for m in MODELS:
        for j in range(5):
            test = [t for t, k in zip(toks, folds) if k == j]
            train = [t for t, k in zip(toks, folds) if k != j]
            close(sum(code(segs[m], test, sigma, train)) / len(test), cf[m][j], f"{m} fold {j}")
        close(sum(code(segs[m], hold, sigma, dev)) / len(hold),
              res["R2"]["development_to_holdout_bits_per_token"][m], f"{m} holdout arm")

    # subsets
    def sub(pred):
        ix = [i for i, r in enumerate(rows) if pred(r)]
        return {m: sum(per[m][i] for i in ix) / len(ix) for m in MODELS}

    lowest = lambda sc: sc["P70"] < min(v for k, v in sc.items() if k != "P70")  # noqa: E731
    cur_ok = True
    for L in ("A", "B"):
        sc = sub(lambda r, L=L: r[2] == L)
        for m in MODELS:
            close(sc[m], res["R2"]["currier"][L]["bits_per_token"][m], f"currier {L} {m}")
        cur_ok &= lowest(sc)
    sec_tok = Counter(r[3] for r in rows)
    sec_fol = defaultdict(set)
    for r in rows:
        sec_fol[r[3]].add(r[0])
    major = sorted(s for s in sec_tok if s and sec_tok[s] >= 2000 and len(sec_fol[s]) >= 8)
    check(major == res["R2"]["major_sections_by_rule"], f"major sections {major}")
    sec_ok = True
    for s in major:
        sc = sub(lambda r, s=s: r[3] == s)
        for m in MODELS:
            close(sc[m], res["R2"]["sections"][s]["bits_per_token"][m], f"section {s} {m}")
        sec_ok &= lowest(sc)

    # R1
    ps = [p4(t) for t in toks]
    nondeg = sum(1 for p in ps if p[0] or p[1] or p[3]) / N
    ecore = sum(1 for p in ps if not p[2]) / N
    hP = H(Counter(p[0] for p in ps))
    hPG = H(Counter(p[:2] for p in ps))
    hPGC = H(Counter(p[:3] for p in ps))
    hW = H(Counter(ps))
    r1 = res["R1"]
    close(nondeg, r1["non_degenerate_parse_rate"], "non-degenerate rate")
    close(ecore, r1["empty_core_rate"], "empty-core rate")
    close(hP, r1["chain_rule_entropies_bits"]["H_P"], "H_P")
    close(hPG - hP, r1["chain_rule_entropies_bits"]["H_G_given_P"], "H_G|P")
    close(hPGC - hPG, r1["chain_rule_entropies_bits"]["H_C_given_PG"], "H_C|PG")
    close(hW - hPGC, r1["chain_rule_entropies_bits"]["H_S_given_PGC"], "H_S|PGC")
    r1_fail = nondeg < 0.85 or (not (0.427 <= ecore <= 0.627) and abs(hW - 10.311) > 1.0)
    check(r1["decision"] == ("REPRODUCTION_FAILURE" if r1_fail else "REPRODUCED"), "R1 decision")

    # gates + decision
    bpt = {m: sum(per[m]) / N for m in MODELS}
    g2 = bpt["A0"] - bpt["P70"] >= 0.05
    g3 = True
    for c in ["A1", "A2", "A3", "A5", "A6", "A7", "A8"]:
        wins = sum(1 for j in range(5) if cf["P70"][j] < cf[c][j])
        g3 &= (bpt[c] - bpt["P70"] >= 0.05) or wins >= 4
    g4 = prim["P70"]["total_bits_per_token"] < prim["A0"]["total_bits_per_token"]
    g = res["gates"]
    check(g["G2_beats_A0_by_0.05"] == g2, "G2")
    check(g["G3_beats_each_competitor"] == g3, "G3")
    check(g["G4_total_bits_beats_A0"] == g4, "G4")
    check(g["G5_currier_A_and_B"] == cur_ok, "G5 currier")
    check(g["G5_major_sections"] == sec_ok, "G5 sections")
    exp = ("REPRODUCTION_FAILURE" if r1_fail else
           "STRUCTURAL_SUPPORT" if (g["G1_lossless_coverage_ge_0.99"] and g2 and g3 and g4 and cur_ok and sec_ok)
           else "REPRODUCED_BUT_NOT_VALIDATED")
    check(res["decision"] == exp, f"decision {res['decision']} != {exp}")
    return report()


def report() -> int:
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E007_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
