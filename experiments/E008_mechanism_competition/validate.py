"""Independent validator for E008 stage A results.json.

Re-derives population, features (S, L), copy search, W selection, all sixteen
models on real data and on nulls N1/N0 (own shuffle, own KT coder, own copy /
edit search — not imported from run.py), contrasts, criteria and verdicts.
Exit non-zero on any mismatch.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.p70 import parse_p70, PREFIXES, GALLOWS, SUFFIXES  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
TOL = 1e-6
COMPS = ("S", "L", "C")
SPECS = [(b, frozenset(c)) for b in ("B0", "B1") for r in range(4) for c in itertools.combinations(COMPS, r)]
errors: list[str] = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def close(a, b, msg):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{msg}: {a} vs {b}")


def name(spec):
    return spec[0] + "".join("+" + c for c in COMPS if c in spec[1])


def fold(folio):
    return int(hashlib.sha256(("E007:" + folio.lower()).encode()).hexdigest(), 16) % 5


def lev(a, b):
    """Plain DP Levenshtein (independent of run.py's lev1 shortcut)."""
    if abs(len(a) - len(b)) > 1:
        return 2
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def edit_string(src, t):
    """Enumerate all single edits of src; the canonical one per PLAN §6.3."""
    if len(src) == len(t):
        for p in range(len(t)):
            if src[:p] + t[p] + src[p + 1:] == t and src[p] != t[p]:
                return f"s{p}{t[p]}"
    elif len(t) == len(src) + 1:
        for p in range(len(t)):
            if src[:p] + t[p] + src[p:] == t:
                return f"i{p}{t[p]}"
    else:
        for p in range(len(src)):
            if src[:p] + src[p + 1:] == t:
                return f"d{p}"
    raise AssertionError((src, t))


def load():
    by_folio = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            by_folio[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    return by_folio


def features(by_folio, order):
    rows = []  # dict per token
    for folio in order:
        win = []
        for lang, sec, full in by_folio[folio]:
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                ke = kd = None
                ed = None
                for k in range(1, min(40, len(win)) + 1):
                    w = win[-k]
                    if w == v:
                        ke = k
                        break
                    if kd is None and lev(w, v) == 1:
                        kd, ed = k, edit_string(w, v)
                rows.append({"v": v, "folio": folio, "lang": lang, "sec": sec, "fold": fold(folio),
                             "S": S, "L": L, "ke": ke, "kd": kd, "ed": ed, "ll": n})
                win.append(v)
    return rows


def shuffle(by_folio, order, seed, per_line):
    rng = np.random.default_rng(seed)
    out = {}
    for folio in order:
        lines = [(lang, sec, [[v, u] for v, u in full]) for lang, sec, full in by_folio[folio]]
        groups = [[ln] for ln in lines] if per_line else [lines]
        for grp in groups:
            pos = [(ln, i) for ln in grp for i, (_, u) in enumerate(ln[2]) if not u]
            vals = [ln[2][i][0] for ln, i in pos]
            perm = rng.permutation(len(vals))
            for (ln, i), j in zip(pos, perm):
                ln[2][i][0] = vals[j]
        out[folio] = lines
    return out


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


def src_of(r, W):
    if r["ke"] is not None and r["ke"] <= W:
        return f"{r['ke']}:0", 0
    if r["kd"] is not None and r["kd"] <= W:
        return f"{r['kd']}:1", 1
    return "NONE", None


def code_token(coder, spec, r, W, update):
    base, comps = spec
    slots = (r["v"],) if base == "B0" else parse_p70(r["v"])
    S = r["S"] if "S" in comps else None
    L = r["L"] if "L" in comps else None
    bits = 0.0

    def step(ctx, v):
        b = coder.cost(ctx, v)
        if update:
            coder.add(ctx, v)
        return b

    if "C" in comps:
        val, d = src_of(r, W)
        bits += step(("src",), val)
        if d is not None:
            if d == 1:
                bits += step(("edit",), r["ed"])
            if update:
                for i, v in enumerate(slots):
                    coder.add(("base", i, slots[:i], S, L), v)
            return bits
    for i, v in enumerate(slots):
        bits += step(("base", i, slots[:i], S, L), v)
    return bits


def run_models(rows, W, sigma):
    dev = [r for r in rows if r["fold"] in (0, 1, 2)]
    hold = [r for r in rows if r["fold"] in (3, 4)]
    out = {}
    for spec in SPECS:
        c = Coder(sigma)
        for r in dev:
            code_token(c, spec, r, W, True)
        out[spec] = np.array([code_token(c, spec, r, W, False) for r in hold])
    return hold, out


def contrasts(hold, hb, base):
    folios = sorted({r["folio"] for r in hold})
    fidx = {f: np.array([i for i, r in enumerate(hold) if r["folio"] == f]) for f in folios}
    A = np.array([i for i, r in enumerate(hold) if r["lang"] == "A"])
    B = np.array([i for i, r in enumerate(hold) if r["lang"] == "B"])
    full = (base, frozenset(COMPS))
    out = {}
    for X in COMPS:
        red = (base, frozenset(c for c in COMPS if c != X))
        dm = hb[(base, frozenset())].mean() - hb[(base, frozenset([X]))].mean()
        du = hb[red].mean() - hb[full].mean()
        wins = sum(1 for f in folios if hb[full][fidx[f]].mean() < hb[red][fidx[f]].mean())
        out[X] = {"dm": float(dm), "du": float(du), "stab": wins / len(folios),
                  "A": float(hb[red][A].mean() - hb[full][A].mean()),
                  "B": float(hb[red][B].mean() - hb[full][B].mean())}
    return out


def main() -> int:
    check(DATA.is_file(), "source missing")
    check((EXP / "results.json").is_file(), "results.json missing")
    if errors:
        return report()
    raw = DATA.read_bytes()
    check(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == EXPECTED_BLOB, "blob")
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))

    by_folio = load()
    order = sorted(by_folio)
    rows = features(by_folio, order)
    sigma = len({ch for r in rows for ch in r["v"]})
    check(res["population"]["n_tokens"] == len(rows), "n_tokens")
    check(res["population"]["sigma_size"] == sigma, "sigma")

    # W selection on development only
    dev = [r for r in rows if r["fold"] in (0, 1, 2)]
    wbits = {}
    for W in (5, 10, 20, 40):
        c = Coder(sigma)
        wbits[W] = sum(code_token(c, ("B1", frozenset("C")), r, W, True) for r in dev)
        close(wbits[W], res["W_selection"]["development_data_bits_B1+C"][str(W)], f"W dev bits {W}")
    W = min((5, 10, 20, 40), key=lambda w: (wbits[w], w))
    check(W == res["W_selection"]["chosen_W"], "chosen W")
    widx = (5, 10, 20, 40).index(W)
    eg = lambda k: 2 * int(math.floor(math.log2(k))) + 1  # noqa: E731

    # real + nulls
    datasets = {
        "models_real": rows,
        "N1": features(shuffle(by_folio, order, 20261019, False), order),
        "N0": features(shuffle(by_folio, order, 20261020, True), order),
    }
    tables = {"models_real": res["models_real"], "N1": res["null_N1_within_folio"]["models"],
              "N0": res["null_N0_within_line"]["models"]}
    ctabs = {"models_real": res["contrasts_real"], "N1": res["null_N1_within_folio"]["contrasts"],
             "N0": res["null_N0_within_line"]["contrasts"]}
    my = {}
    for key, data in datasets.items():
        hold, hb = run_models(data, W, sigma)
        n_hold = len(hold)
        for spec in SPECS:
            nm = name(spec)
            close(float(hb[spec].mean()), tables[key][nm]["holdout_bits_per_token"], f"{key} {nm} holdout")
            mb = (sum((len(s) + 1) * math.log2(sigma + 1) for s in list(PREFIXES) + list(GALLOWS) + list(SUFFIXES))
                  if spec[0] == "B1" else 0.0) + eg(1 + len(spec[1])) + ((eg(widx + 1) + 2) if "C" in spec[1] else 0)
            close(mb, tables[key][nm]["model_bits"], f"{key} {nm} model bits")
            close(float(hb[spec].mean()) + mb / n_hold, tables[key][nm]["holdout_total_bits_per_token"], f"{key} {nm} total")
        my[key] = {b: contrasts(hold, hb, b) for b in ("B0", "B1")}
        for b in ("B0", "B1"):
            for X in COMPS:
                mine, theirs = my[key][b][X], ctabs[key][b][X]
                close(mine["dm"], theirs["marginal_gain"], f"{key} {b} {X} marginal")
                close(mine["du"], theirs["unique_gain"], f"{key} {b} {X} unique")
                close(mine["stab"], theirs["folio_stability"], f"{key} {b} {X} stability")
                close(mine["A"], theirs["unique_gain_subsets"]["currier:A"], f"{key} {b} {X} A")
                close(mine["B"], theirs["unique_gain_subsets"]["currier:B"], f"{key} {b} {X} B")

    # verdicts
    for b in ("B0", "B1"):
        for X in COMPS:
            r, n = my["models_real"][b][X], my["N1"][b][X]
            ok = (r["dm"] >= 0.05 and r["du"] >= 0.05 and r["stab"] >= 2 / 3 and r["A"] > 0 and r["B"] > 0
                  and r["du"] - n["du"] >= 0.05)
            v = "INFORMATIVE" if ok else "NOT_INFORMATIVE" if (r["dm"] < 0.05 and r["du"] < 0.05) else "MIXED"
            check(res["verdicts"][b][X]["verdict"] == v, f"verdict {b} {X}: {res['verdicts'][b][X]['verdict']} != {v}")
    vb = res["verdicts"]["B1"]
    check(res["hypothesis_outcomes"] == {"H011": vb["S"]["verdict"], "H012": vb["C"]["verdict"], "H013": vb["L"]["verdict"]},
          "hypothesis outcomes")
    fam = res["family_readout"]
    rc = my["models_real"]["B1"]
    check(fam["copy_modify_generator_signature"] == (vb["C"]["verdict"] == "INFORMATIVE" and rc["C"]["du"] >= rc["S"]["du"]), "family C")
    check(fam["sequential_dependency_signature"] == (vb["S"]["verdict"] == "INFORMATIVE"), "family S")
    check(fam["line_as_unit_signature"] == (vb["L"]["verdict"] == "INFORMATIVE"), "family L")
    return report()


def report() -> int:
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E008_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
