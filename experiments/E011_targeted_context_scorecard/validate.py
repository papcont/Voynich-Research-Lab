"""Independent validator for E011 results.json.

Own feature extraction, own backoff coder (written from PLAN §2, not imported),
own cross-fit, own feature permutation, own bootstrap; re-derives model
bits/token, null and primary contrasts, margins and decisions. Exit non-zero on
mismatch.
"""
from __future__ import annotations

import hashlib
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


def fold(f):
    return int(hashlib.sha256(("E007:" + f.lower()).encode()).hexdigest(), 16) % 5


def rows():
    out = []
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [(t.value, t.uncertain) for t in tokenize_surface(rec.raw_text) if t.value]
        if not any(not u for _, u in full):
            continue
        n = len(full)
        for i, (v, unc) in enumerate(full):
            if unc:
                continue
            if i == 0:
                S = Sf = "BOL"
            elif full[i - 1][1]:
                S = Sf = "UNC"
            else:
                S, Sf = full[i - 1][0][-1], (parse_p70(full[i - 1][0])[3] or "∅")
            L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
            out.append({"v": v, "s": parse_p70(v), "folio": rec.folio, "lang": rec.meta.language, "fold": fold(rec.folio),
                        "S": S, "L": L, "Sfam": Sf})
    out.sort(key=lambda r: r["folio"])  # stable sort keeps file order within folio
    return out


class Coder:
    """Backoff KT written from PLAN §2."""

    def __init__(self, sigma):
        self.esc = math.log2(sigma + 1)
        self.tab = defaultdict(Counter)

    def kt(self, cnt, value, excl=()):
        n = sum(c for k, c in cnt.items() if k not in excl)
        m = sum(1 for k in cnt if k not in excl)
        d = n + 0.5 * (m + 1)
        if value in cnt and value not in excl:
            return -math.log2((cnt[value] + 0.5) / d), True
        return -math.log2(0.5 / d), False

    def cost(self, child, parent, v):
        if child is None:
            b, seen = self.kt(self.tab[parent], v)
            return b if seen else b + (len(v) + 1) * self.esc
        b1, seen1 = self.kt(self.tab[child], v)
        if seen1:
            return b1
        b0, seen0 = self.kt(self.tab[parent], v, self.tab[child])
        return b1 + b0 + (0 if seen0 else (len(v) + 1) * self.esc)

    def add(self, child, parent, v):
        if child is not None:
            self.tab[child][v] += 1
        self.tab[parent][v] += 1


def ks(r, i, spec, ov):
    parent = ("p", i, r["s"][:i])
    feats = spec.get(i)
    if not feats:
        return None, parent
    return ("c", i, r["s"][:i], tuple((ov or {}).get(f, r[f]) for f in feats)), parent


def crossfit(data, spec, sigma, ov=None):
    per = np.empty(len(data))
    for j in range(5):
        c = Coder(sigma)
        for r in data:
            if r["fold"] != j:
                for i, v in enumerate(r["s"]):
                    c.add(*ks(r, i, spec, ov.get(r["id"]) if ov else None), v)
        for k, r in enumerate(data):
            if r["fold"] == j:
                per[k] = sum(c.cost(*ks(r, i, spec, ov.get(r["id"]) if ov else None), v) for i, v in enumerate(r["s"]))
    return per


def boot(d, seed=20261019, B=10000):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(B, len(d)))
    means = d[idx].mean(axis=1)
    return float(d.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def contrast(data, pa, pb, lang):
    ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for r, x, y in zip(data, pa, pb):
        ba[r["folio"]] += x
        bb[r["folio"]] += y
        n[r["folio"]] += 1
    fol = sorted(n)
    d = np.array([(bb[f] - ba[f]) / n[f] for f in fol])
    mean, lo, hi = boot(d)
    sub = {L: float(d[[i for i, f in enumerate(fol) if lang[f] == L]].mean()) for L in ("A", "B")}
    return {"mean": mean, "lo": lo, "hi": hi, "A": sub["A"], "B": sub["B"]}


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    data = rows()
    for k, r in enumerate(data):
        r["id"] = k
    sigma = len({ch for r in data for ch in r["v"]})
    check(res["population"]["n_tokens"] == len(data), "n_tokens")
    check(res["population"]["sigma_size"] == sigma, "sigma")
    lang = {r["folio"]: r["lang"] for r in data}
    specs = {"M0": {}, "M_S": {0: ("S",)}, "M_L": {0: ("L",), 3: ("L",)}, "M_SL": {0: ("S", "L"), 3: ("L",)},
             "M_Sfam": {0: ("Sfam",)}, "M_Sall": {0: ("S",), 1: ("S",), 2: ("S",), 3: ("S",)}}
    per = {m: crossfit(data, s, sigma) for m, s in specs.items()}
    for m in specs:
        close(float(per[m].mean()), res["descriptive"]["bits_per_token_out_of_fold"][m], f"{m} bits/token")

    # feature permutation: same procedure (folio order, S then L, one rng)
    rng = np.random.default_rng(20261019)
    byf = defaultdict(list)
    for r in data:
        byf[r["folio"]].append(r)
    ov = {}
    for f in sorted(byf):
        g = byf[f]
        for name in ("S", "L"):
            perm = rng.permutation(len(g))
            vals = [g[j][name] for j in perm]
            for r, v in zip(g, vals):
                ov.setdefault(r["id"], {})[name] = v
    for h, (m, name) in {"H014": ("M_S", "S"), "H015": ("M_L", "L")}.items():
        nc = contrast(data, crossfit(data, specs[m], sigma, ov), per["M0"], lang)
        close(nc["mean"], res["null_contrasts"][h]["mean"], f"{h} null mean")
        margin = max(0.05, nc["hi"])
        close(margin, res["margins"][h]["margin"], f"{h} margin")
        rc = contrast(data, per[m], per["M0"], lang)
        for k, kk in (("mean", "mean"), ("lo", "ci_lower"), ("hi", "ci_upper")):
            close(rc[k], res["primary_contrasts"][h][kk], f"{h} {kk}")
        close(rc["A"], res["primary_contrasts"][h]["currier"]["A"], f"{h} currier A")
        close(rc["B"], res["primary_contrasts"][h]["currier"]["B"], f"{h} currier B")
        if rc["mean"] >= margin and rc["lo"] > 0 and rc["mean"] - nc["mean"] >= margin and rc["A"] > 0 and rc["B"] > 0:
            dec = "SUPPORTED_DEV"
        elif rc["hi"] < margin:
            dec = "FALSIFIED_DEV"
        else:
            dec = "INCONCLUSIVE_DEV"
        check(res["decisions"][h] == dec, f"{h} decision {res['decisions'][h]} != {dec}")
    for key, (a, b) in {"M_SL-M0": ("M_SL", "M0"), "M_Sfam-M0": ("M_Sfam", "M0"), "M_Sall-M0": ("M_Sall", "M0")}.items():
        close(contrast(data, per[a], per[b], lang)["mean"], res["secondary_contrasts"][key]["mean"], key)
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E011_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
