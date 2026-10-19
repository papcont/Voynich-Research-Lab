"""Independent validator for E018 results.json (own features, permutation, coder)."""
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


V11 = _load("e011_validate", ROOT / "experiments" / "E011_targeted_context_scorecard" / "validate.py")
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
TOL = 1e-6
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def lines_real():
    out = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            out[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    return dict(out)


_PARSE = {}


def _p70(v):
    s = _PARSE.get(v)
    if s is None:
        s = _PARSE[v] = parse_p70(v)
    return s


def rows(lines):
    r = []
    for folio in sorted(lines):
        for lang, sec, full in lines[folio]:
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                r.append({"v": v, "s": _p70(v), "folio": folio, "lang": lang, "sec": sec, "fold": V11.fold(folio), "S": S,
                          "Sy": S if S in ("y", "BOL", "UNC") else "other", "L": "", "Sfam": ""})
    return r


def R(sel):
    y = [r for r in sel if r["S"] == "y"]; o = [r for r in sel if r["S"] not in ("y", "BOL", "UNC")]
    py = np.mean([r["s"][0] == "qo" for r in y]); po = np.mean([r["s"][0] == "qo" for r in o])
    return py / po


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    lines = lines_real()
    rr = rows(lines)
    selectors = {"bio_B": lambda r: r["lang"] == "B" and r["sec"] == "B", "other_B": lambda r: r["lang"] == "B" and r["sec"] != "B", "A": lambda r: r["lang"] == "A"}
    for k, f in selectors.items():
        close(R([r for r in rr if f(r)]), res["H003a"]["enrichment"][k]["R"], f"R {k}")
    rng = np.random.default_rng(20261070)
    null = {k: [] for k in selectors}
    for _ in range(1000):
        pl = {}
        for folio in sorted(lines):
            new = [(l, s, [[v, u] for v, u in full]) for l, s, full in lines[folio]]
            pos = [(ln, i) for ln in new for i, (_, u) in enumerate(ln[2]) if not u]
            vals = [ln[2][i][0] for ln, i in pos]
            perm = rng.permutation(len(vals))
            for (ln, i), j in zip(pos, perm):
                ln[2][i][0] = vals[j]
            pl[folio] = new
        pr = rows(pl)
        for k, f in selectors.items():
            null[k].append(R([r for r in pr if f(r)]))
    for k in selectors:
        close(float(np.mean(null[k])), res["H003a"]["enrichment"][k]["null_mean"], f"null mean {k}")
        p = (1 + np.sum(np.array(null[k]) >= res["H003a"]["enrichment"][k]["R"])) / 1001
        close(p, res["H003a"]["enrichment"][k]["p_perm"], f"p {k}")
    b = res["H003a"]["enrichment"]["bio_B"]
    dec_a = "SUPPORTED_DEV" if (b["R"] >= 1.5 and b["p_perm"] <= 0.01) else "FALSIFIED_DEV" if (b["R"] <= 1.1 or b["null_q975"] >= b["R"]) else "INCONCLUSIVE_DEV"
    check(res["H003a"]["decision"] == dec_a, "H003a decision")
    B = [r for r in rr if r["lang"] == "B"]
    for k, r in enumerate(B):
        r["id"] = k
    sigma = len({c for r in rr for c in r["v"]})
    p0 = V11.crossfit(B, {}, sigma); pS = V11.crossfit(B, {0: ("S",)}, sigma); pSy = V11.crossfit(B, {0: ("Sy",)}, sigma)
    def pf(pa, pb):
        ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
        for r, x, y in zip(B, pa, pb):
            ba[r["folio"]] += x; bb[r["folio"]] += y; n[r["folio"]] += 1
        return np.array([(ba[f] - bb[f]) / n[f] for f in sorted(n)])
    dS, dSy = pf(p0, pS), pf(p0, pSy)
    close(float(dS.mean()), res["H003b"]["delta_S_B"]["mean"], "dS"); close(float(dSy.mean()), res["H003b"]["delta_Sy_B"]["mean"], "dSy")
    rb = np.random.default_rng(20261019); means = dSy[rb.integers(0, len(dSy), size=(10000, len(dSy)))].mean(axis=1)
    lo, hi = float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))
    close(lo, res["H003b"]["delta_Sy_B"]["ci_lower"], "ci lo")
    share = dSy.mean() / dS.mean()
    dec_b = "SUPPORTED_DEV" if (dSy.mean() >= 0.05 and lo > 0 and share >= 0.5) else "FALSIFIED_DEV" if (hi < 0.05 or share < 0.25) else "INCONCLUSIVE_DEV"
    check(res["H003b"]["decision"] == dec_b, f"H003b decision {res['H003b']['decision']} != {dec_b}")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E018_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
