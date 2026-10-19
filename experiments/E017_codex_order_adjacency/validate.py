"""Independent validator for E017 results.json (own strata, pairs, permutations)."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
TOL = 1e-6
errors = []
FR = re.compile(r"^f(\d+)([rv])(\d*)$")


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    toks, meta = defaultdict(list), {}
    for rec, _i, t in iter_strict_tokens(parse_ivtff(DATA)):
        if is_running_text(rec.locator):
            toks[rec.folio].append(t.value)
            meta[rec.folio] = (rec.meta.language, rec.meta.illustration)
    folios = sorted(toks)
    key = {f: meta[f] for f in folios}
    for _ in range(2):
        cnt = Counter(key.values())
        for f in folios:
            if cnt[key[f]] < 3:
                key[f] = (meta[f][0], "rest") if key[f][1] != "rest" else ("rest", "rest")
    groups = defaultdict(list)
    for f in folios:
        groups[key[f]].append(f)
    sets = {f: set(toks[f]) for f in folios}

    def jac(a, b):
        return len(sets[a] & sets[b]) / len(sets[a] | sets[b])

    def pairs(order):
        return [(order[i], order[i + 1]) for i in range(len(order) - 1)
                if key[order[i]] == key[order[i + 1]] and len(toks[order[i]]) >= 20 and len(toks[order[i + 1]]) >= 20]

    def J(pp):
        return float(np.mean([jac(a, b) for a, b in pp])) if pp else float("nan")

    def ptype(a, b):
        ma, mb = FR.match(a), FR.match(b)
        if not ma or not mb:
            return "other"
        if ma.group(1) == mb.group(1):
            return "same-leaf"
        if int(mb.group(1)) == int(ma.group(1)) + 1 and ma.group(2) == "v" and mb.group(2) == "r":
            return "facing"
        return "other"

    pp = pairs(folios)
    check(len(pp) == res["population"]["n_adjacent_same_stratum_pairs"], "n pairs")
    Jo = J(pp)
    close(Jo, res["H025b"]["J_adj_obs"], "J obs")
    rng = np.random.default_rng(20261060)
    pos = {g: [folios.index(f) for f in m] for g, m in groups.items()}
    null, nl = [], {"A": [], "B": []}
    for _ in range(1000):
        order = list(folios)
        for g, m in groups.items():
            perm = rng.permutation(len(m))
            for p_, j in zip(pos[g], perm):
                order[p_] = m[j]
        q = pairs(order)
        null.append(J(q))
        for L in ("A", "B"):
            nl[L].append(J([x for x in q if meta[x[0]][0] == L]))
    null = np.array(null)
    close(float(null.mean()), res["H025b"]["null_mean"], "null mean")
    dJ = Jo - null.mean()
    pJ = (1 + np.sum(null >= Jo)) / 1001
    close(pJ, res["H025b"]["p_perm"], "pJ")
    dl = {L: J([x for x in pp if meta[x[0]][0] == L]) - np.nanmean(nl[L]) for L in ("A", "B")}
    for L in ("A", "B"):
        close(dl[L], res["H025b"]["by_currier"][L]["excess"], f"excess {L}")
    dec = "SUPPORTED_DEV" if (dJ >= 0.01 and pJ <= 0.01 and dl["A"] > 0 and dl["B"] > 0) else "FALSIFIED_DEV" if np.quantile(null, 0.975) >= Jo else "INCONCLUSIVE_DEV"
    check(res["H025b"]["decision"] == dec, f"H025b decision {res['H025b']['decision']} != {dec}")
    jv = np.array([jac(a, b) for a, b in pp]); t = np.array([ptype(a, b) for a, b in pp])
    D = jv[t == "same-leaf"].mean() - jv[t == "facing"].mean()
    close(D, res["H026"]["D_same_leaf_minus_facing"], "D")
    rng2 = np.random.default_rng(20261061)
    Dn = np.array([(lambda tp: jv[tp == "same-leaf"].mean() - jv[tp == "facing"].mean())(t[rng2.permutation(len(t))]) for _ in range(1000)])
    pD = (1 + np.sum(Dn >= D)) / 1001
    close(pD, res["H026"]["p_perm"], "pD")
    dec26 = "SUPPORTED_DEV" if (D >= 0.01 and pD <= 0.01) else "FALSIFIED_DEV" if (np.quantile(Dn, 0.975) >= D or D < 0) else "INCONCLUSIVE_DEV"
    check(res["H026"]["decision"] == dec26, f"H026 decision {res['H026']['decision']} != {dec26}")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E017_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
