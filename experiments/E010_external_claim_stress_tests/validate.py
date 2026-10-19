"""Independent validator for E010 results.json (own units/MI/coder/permutation/bootstrap)."""
from __future__ import annotations

import hashlib
import json
import math
import re
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
TABLE = ROOT / ".external" / "epilectrik_voynich" / "results" / "phase20a_operator_equivalence.json"
TOL = 1e-6
U = re.compile(r"c[tkpf]h|[cs]h|i+[nrlm]|.")
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m):
    check(abs(a - b) <= TOL * max(1.0, abs(b)), f"{m}: {a} vs {b}")


def fold(f):
    return int(hashlib.sha256(("E007:" + f.lower()).encode()).hexdigest(), 16) % 5


def load():
    d = json.loads(TABLE.read_text(encoding="utf-8"))
    table = {t: str(c["class_id"]) for c in d["classes"] for t in c["members"]}
    rows, bnd = [], []
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [t for t in tokenize_surface(rec.raw_text) if t.value]
        for i, t in enumerate(full):
            if t.uncertain:
                continue
            if i == 0:
                S = Sf = Su = S2 = pc = "BOL"
            elif full[i - 1].uncertain:
                S = Sf = Su = S2 = pc = "UNC"
            else:
                pv = full[i - 1].value
                pu = U.findall(pv)
                S, Sf, Su, S2, pc = pv[-1], parse_p70(pv)[3] or "∅", pu[-1], "".join(pu[-2:]), table.get(pv, "UN")
                bnd.append((rec.meta.language, pu[-1], U.findall(t.value)[0], t.separator_before))
            rows.append({"v": t.value, "s": parse_p70(t.value), "folio": rec.folio, "lang": rec.meta.language, "sec": rec.meta.illustration,
                         "fold": fold(rec.folio), "S": S, "Sfam": Sf, "Sunit": Su, "S2unit": S2, "cls": table.get(t.value, "UN"), "prevcls": pc})
    rows.sort(key=lambda r: r["folio"])
    return rows, bnd


def mi(x, y, nx, ny):
    j = np.zeros((nx, ny))
    np.add.at(j, (x, y), 1)
    p = j / j.sum()
    px, py = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (px @ py)[nz])).sum())


def coupling(x, y, nx, ny, seed):
    rng = np.random.default_rng(seed)
    obs = mi(x, y, nx, ny)
    perm = [mi(x, rng.permutation(y), nx, ny) for _ in range(1000)]
    return obs - float(np.mean(perm))


class Coder:
    def __init__(self, sigma):
        self.esc = math.log2(sigma + 1)
        self.tab = defaultdict(Counter)

    def kt(self, cnt, v, excl=()):
        n = sum(c for k, c in cnt.items() if k not in excl)
        m = sum(1 for k in cnt if k not in excl)
        d = n + 0.5 * (m + 1)
        if v in cnt and v not in excl:
            return -math.log2((cnt[v] + 0.5) / d), True
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


MODELS = {"M_S": (None, ("S",)), "M_Sfam": (None, ("Sfam",)), "M_Sunit": (None, ("Sunit",)), "M_S2unit": (None, ("S2unit",)),
          "M_class": ("plain", ("cls",)), "M_classprev": ("prev", ("cls",))}


def code(c, model, r, ov, update):
    stage, pf = MODELS[model]
    f = lambda n: (ov or {}).get(n, r[n])  # noqa: E731
    bits = 0.0
    if stage:
        child = ("clsc", f("prevcls")) if stage == "prev" else None
        if update:
            c.add(child, ("cls",), f("cls"))
        else:
            bits += c.cost(child, ("cls",), f("cls"))
    for i, v in enumerate(r["s"]):
        parent = ("b", i, r["s"][:i])
        child = ("c", i, r["s"][:i], tuple(f(n) for n in pf)) if i == 0 else None
        if update:
            c.add(child, parent, v)
        else:
            bits += c.cost(child, parent, v)
    return bits


def crossfit(data, model, sigma, ov=None):
    per = np.empty(len(data))
    for j in range(5):
        c = Coder(sigma)
        for r in data:
            if r["fold"] != j:
                code(c, model, r, ov.get(r["id"]) if ov else None, True)
        for k, r in enumerate(data):
            if r["fold"] == j:
                per[k] = code(c, model, r, ov.get(r["id"]) if ov else None, False)
    return per


def contrast(data, pa, pb, sections):
    ba, bb, n, sec = defaultdict(float), defaultdict(float), defaultdict(int), {}
    for r, x, y in zip(data, pa, pb):
        ba[r["folio"]] += x; bb[r["folio"]] += y; n[r["folio"]] += 1; sec[r["folio"]] = r["sec"]
    fol = sorted(n)
    d = np.array([(bb[f] - ba[f]) / n[f] for f in fol])
    rng = np.random.default_rng(20261019)
    means = d[rng.integers(0, len(d), size=(10000, len(d)))].mean(axis=1)
    return {"mean": float(d.mean()), "lo": float(np.quantile(means, 0.025)), "hi": float(np.quantile(means, 0.975)),
            "sections": {s: float(d[[i for i, f in enumerate(fol) if sec[f] == s]].mean()) for s in sections}}


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    rows, bnd = load()
    for k, r in enumerate(rows):
        r["id"] = k
    sigma = len({ch for r in rows for ch in r["v"]})
    B = [r for r in rows if r["lang"] == "B"]
    check(len(B) == res["population"]["n_B_tokens"], "n_B_tokens")
    sections = res["population"]["gate_sections"]
    check(sections == [s for s, _ in Counter(r["sec"] for r in B).most_common(2)], "gate sections")
    # R1
    Bb = [b for b in bnd if b[0] == "B"]
    L, R = sorted({b[1] for b in Bb}), sorted({b[2] for b in Bb})
    li, ri = {u: i for i, u in enumerate(L)}, {u: i for i, u in enumerate(R)}
    x = np.array([li[b[1]] for b in Bb]); y = np.array([ri[b[2]] for b in Bb]); d = np.array([b[3] == "." for b in Bb])
    close(coupling(x, y, len(L), len(R), 20261020), res["R1_boundary_coupling"]["C_all"]["C"], "C_all")
    close(coupling(x[d], y[d], len(L), len(R), 20261021), res["R1_boundary_coupling"]["C_def"]["C"], "C_def")
    # R2
    per = {m: crossfit(B, m, sigma) for m in MODELS}
    for m in MODELS:
        close(float(per[m].mean()), res["R2"]["bits_per_token_out_of_fold_B"][m], f"{m} bpt")
    rng = np.random.default_rng(20261020)
    byf = defaultdict(list)
    for r in B:
        byf[r["folio"]].append(r)
    ov = {}
    for f in sorted(byf):
        g = byf[f]
        for name in ("S", "Sunit", "S2unit", "Sfam", "cls"):
            perm = rng.permutation(len(g))
            vals = [g[j][name] for j in perm]
            for r, v in zip(g, vals):
                ov.setdefault(r["id"], {})[name] = v
    prev = None
    for r in B:
        if r["prevcls"] in ("BOL", "UNC") or prev is None or prev["folio"] != r["folio"]:
            ov.setdefault(r["id"], {})["prevcls"] = r["prevcls"]
        else:
            ov.setdefault(r["id"], {})["prevcls"] = ov.get(prev["id"], {}).get("cls", prev["cls"])
        prev = r
    for h, (a, b, _f) in {"H016": ("M_Sunit", "M_S", 0), "H017": ("M_S2unit", "M_Sunit", 0), "H018": ("M_classprev", "M_Sfam", 0)}.items():
        nc = contrast(B, crossfit(B, a, sigma, ov), per[b], sections)
        close(nc["mean"], res["R2"]["null_contrasts"][h]["mean"], f"{h} null")
        margin = max(0.05, nc["hi"])
        close(margin, res["R2"]["margins"][h]["margin"], f"{h} margin")
        rc = contrast(B, per[a], per[b], sections)
        close(rc["mean"], res["R2"]["primary_contrasts"][h]["mean"], f"{h} mean")
        close(rc["lo"], res["R2"]["primary_contrasts"][h]["ci_lower"], f"{h} lo")
        close(rc["hi"], res["R2"]["primary_contrasts"][h]["ci_upper"], f"{h} hi")
        dec = ("SUPPORTED_DEV" if rc["mean"] >= margin and rc["lo"] > 0 and rc["mean"] - nc["mean"] >= margin and all(v > 0 for v in rc["sections"].values())
               else "FALSIFIED_DEV" if rc["hi"] < margin else "INCONCLUSIVE_DEV")
        check(res["R2"]["decisions"][h] == dec, f"{h} decision {res['R2']['decisions'][h]} != {dec}")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("E010_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
