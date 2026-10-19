"""Independent validator for E022 results.json.

Re-derives from the raw ZL3b file: pairs per class and population (own extraction), the
Mantel–Haenszel and pooled enrichments (own arithmetic), the permutation p-values (own
permutation scheme and seed; Monte-Carlo tolerance), the persistence bootstrap (own term
computation, same seed and draw sequence → exact), the MI point values, and every decision from
the PLAN §2.3 rules. Prints E022_VALIDATION_PASS or the failures."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
POPS = ("bio_B", "other_B", "A")
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def close(a, b, m, tol=1e-9):
    if a is None or b is None or (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
        check((a is None or (isinstance(a, float) and math.isnan(a))) and (b is None or (isinstance(b, float) and math.isnan(b))), f"{m}: {a} vs {b}")
        return
    check(abs(a - b) <= tol * max(1.0, abs(b)), f"{m}: {a} vs {b}")


# ---- own extraction -------------------------------------------------------- #
def pop_of(lang, sec):
    return ("bio_B" if sec == "B" else "other_B") if lang == "B" else ("A" if lang == "A" else None)


def load():
    seq = defaultdict(list)
    for r in parse_ivtff(DATA):
        if not is_running_text(r.locator):
            continue
        seq[r.folio].append({"pop": pop_of(r.meta.language, r.meta.illustration), "end": "<$>" in r.raw_text,
                             "start": "<%>" in r.raw_text, "toks": [(t.value, t.uncertain) for t in tokenize_surface(r.raw_text) if t.value]})
    return seq


def own_pairs(seq):
    out = {c: {p: [] for p in POPS} for c in ("line", "para", "within")}
    excl = Counter()
    for folio, lines in seq.items():
        for ln in lines:
            if ln["pop"] is None:
                continue
            tk = ln["toks"]
            for a, b in zip(tk, tk[1:]):
                if not a[1] and not b[1]:
                    out["within"][ln["pop"]].append((folio, a[0][-1], parse_p70(b[0])[0]))
        for prev, nxt in zip(lines, lines[1:]):
            c = "para" if prev["end"] else "line"
            if nxt["start"] != prev["end"]:
                excl[c + "_marker_mismatch"] += 1; continue
            if prev["pop"] is None or nxt["pop"] is None:
                excl[c + "_no_population"] += 1; continue
            if prev["pop"] != nxt["pop"]:
                excl[c + "_population_change"] += 1; continue
            if not prev["toks"] or not nxt["toks"]:
                excl[c + "_empty_line"] += 1; continue
            last, first = prev["toks"][-1], nxt["toks"][0]
            if last[1] or first[1]:
                excl[c + "_uncertain_edge"] += 1; continue
            out[c][prev["pop"]].append((folio, last[0][-1], parse_p70(first[0])[0]))
    return out, dict(excl)


# ---- own statistics ---------------------------------------------------------- #
def strata(plist):
    st = defaultdict(lambda: {"a": 0, "ny": 0, "c": 0, "no": 0})
    for folio, S, pre in plist:
        d = st[folio]
        if S == "y":
            d["ny"] += 1; d["a"] += pre == "qo"
        else:
            d["no"] += 1; d["c"] += pre == "qo"
    return st


def mh_from_strata(st):
    num = den = Fraction(0)
    for d in st.values():
        if d["ny"] == 0 or d["no"] == 0:
            continue
        N = d["ny"] + d["no"]
        num += Fraction(d["a"] * d["no"], N); den += Fraction(d["c"] * d["ny"], N)
    return float(num / den) if den else float("nan")


def plain_from_strata(st):
    a = sum(d["a"] for d in st.values()); ny = sum(d["ny"] for d in st.values())
    c = sum(d["c"] for d in st.values()); no = sum(d["no"] for d in st.values())
    return (float((a / ny) / (c / no)) if (ny and no and c) else float("nan")), a, ny, c, no


def own_perm_p(plist, R, rng, n=1000):
    by = defaultdict(list)
    for folio, S, pre in plist:
        by[folio].append((S, pre))
    nulls = []
    for _ in range(n):
        st = defaultdict(lambda: {"a": 0, "ny": 0, "c": 0, "no": 0})
        for folio, v in by.items():
            pres = [p for _, p in v]
            order = rng.permutation(len(v))
            d = st[folio]
            for i, (S, _) in enumerate(v):
                q = pres[order[i]] == "qo"
                if S == "y":
                    d["ny"] += 1; d["a"] += q
                else:
                    d["no"] += 1; d["c"] += q
        nulls.append(mh_from_strata(st))
    nulls = np.array(nulls, dtype=float)
    return float((1 + np.nansum(nulls >= R)) / (n + 1)), float(np.nanquantile(nulls, 0.975)), float(np.nanmean(nulls))


def mi(pairs_sp):
    j = Counter(pairs_sp); n = len(pairs_sp); pa, pb = Counter(), Counter()
    for (a, b), c in j.items():
        pa[a] += c; pb[b] += c
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in j.items())


def h034(R, p, q975):
    return "SUPPORTED_DEV" if (R >= 1.5 and p <= 0.01) else "FALSIFIED_DEV" if (R <= 1.1 or q975 >= R) else "INCONCLUSIVE_DEV"


def h035(rho, lo, hi, d34):
    if d34 == "FALSIFIED_DEV" or (hi is not None and hi < 0.25):
        return "FALSIFIED_DEV"
    return "SUPPORTED_DEV" if (rho is not None and lo is not None and rho >= 0.75 and lo >= 0.5) else "PARTIAL"


def h036(R, p, q975, n_y):
    return "SUPPORTED_DEV" if (R >= 1.5 and p <= 0.01) else "FALSIFIED_DEV" if (q975 >= R and n_y >= 100) else "INCONCLUSIVE_DEV"


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    seq = load()
    pairs, excl = own_pairs(seq)
    check(excl == res["exclusions"], f"exclusions {excl} vs {res['exclusions']}")
    rng = np.random.default_rng(20269999)
    blocks = {(c, p): pairs[c][p] for c in ("line", "para", "within") for p in POPS}
    blocks[("para", "B_pooled")] = pairs["para"]["bio_B"] + pairs["para"]["other_B"]
    own_dec_inputs = {}
    for (c, p), pl in blocks.items():
        r = res["enrichment"][c][p]
        check(len(pl) == r["n_pairs"], f"n_pairs {c}/{p}: {len(pl)} vs {r['n_pairs']}")
        st = strata(pl)
        R = mh_from_strata(st); Rp, a, ny, cc, no = plain_from_strata(st)
        close(R, r["R_MH"], f"R_MH {c}/{p}"); close(Rp, r["R_plain"], f"R_plain {c}/{p}")
        check(ny == r["n_after_y"] and no == r["n_after_other"], f"counts {c}/{p}")
        if c != "within":  # own permutation null (different seed): Monte-Carlo agreement
            p_own, q_own, m_own = own_perm_p(pl, R, rng)
            check(abs(p_own - r["p_perm"]) <= 0.02 or (p_own <= 0.01 and r["p_perm"] <= 0.01), f"p_perm {c}/{p}: own {p_own} vs {r['p_perm']}")
            check(abs(q_own - r["null_q975"]) <= 0.05 * max(1.0, abs(r["null_q975"])), f"null q975 {c}/{p}: own {q_own} vs {r['null_q975']}")
            own_dec_inputs[(c, p)] = (R, p_own, q_own, ny)
    # bootstrap: own per-folio terms, same seed and draw sequence as run.py (one RNG, POPS order) -> exact
    rng_b = np.random.default_rng(res["seeds"]["bootstrap"])
    for q in POPS:
        d2, l2, h2 = own_rho_boot_rng(pairs["line"][q], pairs["within"][q], rng_b, res["n_bootstrap"])
        r2 = res["persistence_rho"][q]
        check(d2 == r2["dropped"], f"rho dropped {q}: {d2} vs {r2['dropped']}")
        close(l2, r2["ci_lower"], f"rho ci_lower {q}"); close(h2, r2["ci_upper"], f"rho ci_upper {q}")
        Rb, Rw = res["enrichment"]["line"][q]["R_MH"], res["enrichment"]["within"][q]["R_MH"]
        pt = math.log(Rb) / math.log(Rw) if (Rb > 0 and Rw > 1) else None
        close(pt, r2["point"], f"rho point {q}")
    # MI point values
    close(mi([(S, pr) for _f, S, pr in pairs["line"]["bio_B"]]), res["mi_check"]["line_break_bio_B"]["I_bits"], "MI line-break bio_B")
    # decisions: from the results' own numbers and from the validator's own null
    e = res["enrichment"]
    d34 = h034(e["line"]["bio_B"]["R_MH"], e["line"]["bio_B"]["p_perm"], e["line"]["bio_B"]["null_q975"])
    rb = res["persistence_rho"]["bio_B"]
    d35 = h035(rb["point"], rb["ci_lower"], rb["ci_upper"], d34)
    d36 = h036(e["para"]["B_pooled"]["R_MH"], e["para"]["B_pooled"]["p_perm"], e["para"]["B_pooled"]["null_q975"], e["para"]["B_pooled"]["n_after_y"])
    ho = res["hypothesis_outcomes"]
    check(ho["H034"] == d34 and ho["H035"] == d35 and ho["H036"] == d36, f"decisions {ho} vs {(d34, d35, d36)}")
    R, p_own, q_own, ny = own_dec_inputs[("line", "bio_B")]
    check(h034(R, p_own, q_own) == ho["H034"], f"H034 under own null: {h034(R, p_own, q_own)}")
    R, p_own, q_own, ny = own_dec_inputs[("para", "B_pooled")]
    check(h036(R, p_own, q_own, ny) == ho["H036"], f"H036 under own null: {h036(R, p_own, q_own, ny)}")
    if errors:
        for x in errors:
            print("FAIL", x)
        return 1
    print("E022_VALIDATION_PASS")
    return 0


def own_rho_boot_rng(brk, within, rng, n_boot):
    sb, sw = strata(brk), strata(within)
    folios = sorted(set(sb) | set(sw))
    def terms(st, f):
        d = st.get(f)
        if not d or d["ny"] == 0 or d["no"] == 0:
            return (0.0, 0.0)
        N = d["ny"] + d["no"]
        return (d["a"] * d["no"] / N, d["c"] * d["ny"] / N)
    tb = np.array([terms(sb, f) for f in folios]); tw = np.array([terms(sw, f) for f in folios])
    n = len(folios); rhos = []; dropped = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        b, w = tb[idx].sum(axis=0), tw[idx].sum(axis=0)
        if b[1] <= 0 or w[1] <= 0:
            dropped += 1; continue
        lb = math.log(b[0] / b[1]) if b[0] > 0 else -math.inf
        lw = math.log(w[0] / w[1]) if w[0] > 0 else -math.inf
        if lb <= 0 or lw <= 0:
            dropped += 1; continue
        rhos.append(lb / lw)
    rhos = np.array(rhos)
    return dropped, float(np.quantile(rhos, 0.025)), float(np.quantile(rhos, 0.975))


if __name__ == "__main__":
    raise SystemExit(main())
