"""Independent validator for E016 results.json (own strata, permutation, statistics)."""
from __future__ import annotations

import json
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
    check({str(k): len(v) for k, v in groups.items()} == res["population"]["strata"], "strata")

    def F(tk):
        return np.array([1 - len(set(tk[f])) / len(tk[f]) for f in folios])

    def jac(a, b):
        a, b = set(a), set(b)
        return len(a & b) / len(a | b)

    def J(tk):
        vals = [jac(tk[folios[i]], tk[folios[i + 1]]) for i in range(len(folios) - 1)
                if len(tk[folios[i]]) >= 20 and len(tk[folios[i + 1]]) >= 20]
        return float(np.mean(vals))

    def perm(tk, gr, rng):
        out = {}
        for members in gr.values():
            pool = [v for f in members for v in tk[f]]
            p = rng.permutation(len(pool))
            k = 0
            for f in members:
                n = len(tk[f])
                out[f] = [pool[p[j]] for j in range(k, k + n)]
                k += n
        return out

    Fo, Jo = F(toks), J(toks)
    rng = np.random.default_rng(20261050)
    Fn, Jn = [], []
    for _ in range(1000):
        p = perm(toks, groups, rng)
        Fn.append(F(p)); Jn.append(J(p))
    Fn = np.array(Fn); Jn = np.array(Jn)
    ex = Fo - Fn.mean(axis=0)
    close(float(Fo.mean()), res["H024"]["F_obs"], "F_obs")
    close(float(Fn.mean()), res["H024"]["F_null_N1_mean"], "F null mean")
    close(float(ex.mean()), res["H024"]["excess_dF"], "dF")
    b = np.random.default_rng(20261019)
    means = ex[b.integers(0, len(ex), size=(10000, len(ex)))].mean(axis=1)
    close(float(np.quantile(means, 0.025)), res["H024"]["ci_lower"], "ci lower")
    close(float(np.quantile(means, 0.975)), res["H024"]["ci_upper"], "ci upper")
    pF = (1 + np.sum(Fn.mean(axis=1) >= Fo.mean())) / 1001
    close(pF, res["H024"]["p_perm"], "pF")
    decF = "SUPPORTED_DEV" if (ex.mean() >= 0.02 and np.quantile(means, 0.025) > 0 and pF <= 0.01) else "FALSIFIED_DEV" if np.quantile(means, 0.975) < 0.02 else "INCONCLUSIVE_DEV"
    check(res["H024"]["decision"] == decF, f"H024 decision {res['H024']['decision']} != {decF}")
    close(Jo, res["H025"]["J_adj_obs"], "J obs"); close(float(Jn.mean()), res["H025"]["J_adj_null_mean"], "J null")
    pJ = (1 + np.sum(Jn >= Jo)) / 1001
    close(pJ, res["H025"]["p_perm"], "pJ")
    adj = [jac(toks[folios[i]], toks[folios[i + 1]]) for i in range(len(folios) - 1)
           if key[folios[i]] == key[folios[i + 1]] and len(toks[folios[i]]) >= 20 and len(toks[folios[i + 1]]) >= 20]
    non = []
    for members in groups.values():
        big = [f for f in members if len(toks[f]) >= 20]
        for i in range(len(big)):
            for j in range(i + 1, len(big)):
                if abs(folios.index(big[i]) - folios.index(big[j])) > 1:
                    non.append(jac(toks[big[i]], toks[big[j]]))
    avn = float(np.mean(adj) - np.mean(non))
    close(avn, res["H025"]["adjacent_minus_nonadjacent"], "adj-non")
    dJ = Jo - Jn.mean()
    decJ = "SUPPORTED_DEV" if (dJ >= 0.01 and pJ <= 0.01 and avn > 0) else "FALSIFIED_DEV" if np.quantile(Jn, 0.975) >= Jo else "INCONCLUSIVE_DEV"
    check(res["H025"]["decision"] == decJ, f"H025 decision {res['H025']['decision']} != {decJ}")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E016_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
