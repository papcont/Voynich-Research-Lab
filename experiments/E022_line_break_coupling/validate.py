"""Independent validator for E022 results.json (PLAN §5).

Own derivations from the raw ZL3b file: record set and parser-dropped loci (own regex scan), gap
flags (marker-token method), pairs of every class with every exclusion (own loop), stratified
Mantel–Haenszel risk/odds ratios and pooled ratios in exact rational arithmetic, counts, the
permutation null with its own scheme and seed (Monte-Carlo tolerance), the folio bootstrap by exact
reproduction (same seed and draw order), the MI/S1 point values, and the §2.4 decisions from the
recorded numbers and from the validator's own null (pre-registered resolution: a differing decision
must be recorded as INCONCLUSIVE_DEV). Prints E022_VALIDATION_PASS or the failures."""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import INLINE_COMMENT_RE, PARA_MARK_RE, parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text, locus_type  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
POPS = ("bio_B", "other_B", "A")
OWN_SEED = 20269999
errors = []


def check(c, m):
    if not c:
        errors.append(m)


def isnan(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def close(a, b, m, tol=1e-9):
    if isnan(a) or isnan(b):
        check(isnan(a) and isnan(b), f"{m}: {a} vs {b}")
        return
    check(abs(a - b) <= tol * max(1.0, abs(b)), f"{m}: {a} vs {b}")


# ---------------------------------------------------------------- records ---- #
def pop_of(lang, sec):
    return ("bio_B" if sec == "B" else "other_B") if lang == "B" else ("A" if lang == "A" else None)


def raw_scan():
    """folio -> ordered list of (locus, dropped_by_parser) for P-type loci (own regex)."""
    out = defaultdict(list)
    pat = re.compile(r"^<(f[^>,]+),([^>]*)>\s+(.*)$")
    for line in DATA.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if m and "." in m.group(1) and is_running_text(m.group(2)):
            out[m.group(1).split(".", 1)[0]].append((m.group(1), m.group(3).lstrip().startswith("<!")))
    return dict(out)


def tokens_with_gaps(raw_text):
    """Marker-token method: gaps become a sentinel token; the token after it is flagged."""
    text = PARA_MARK_RE.sub("", INLINE_COMMENT_RE.sub("", raw_text))
    text = re.sub(r"<->|<~>", ".GAPSENTINEL.", text)
    out, flag = [], False
    for t in tokenize_surface(text):
        if not t.value:
            continue
        if t.value == "GAPSENTINEL":
            flag = True; continue
        out.append((t.value, t.uncertain, flag and bool(out))); flag = False
    ref = [(t.value, t.uncertain) for t in tokenize_surface(raw_text) if t.value]
    if [(v, u) for v, u, _ in out] != ref:
        return [(v, u, False) for v, u in ref]
    return out


def load():
    seq = defaultdict(list)
    for r in parse_ivtff(DATA):
        if not is_running_text(r.locator):
            continue
        seq[r.folio].append({"locus": r.locus, "loc": r.locator or "", "pb": locus_type(r.locator) == "Pb", "pop": pop_of(r.meta.language, r.meta.illustration),
                             "hand": r.meta.hand, "end": "<$>" in r.raw_text, "start": "<%>" in r.raw_text, "toks": tokens_with_gaps(r.raw_text)})
    for f in seq:
        pid = 0
        for r in seq[f]:
            pid += r["start"]; r["pid"] = pid
    return dict(seq)


# ------------------------------------------------------------------ pairs ---- #
def own_pairs(seq, rawidx):
    P = {c: [] for c in ("within", "gap", "line", "para", "lag2")}
    X = Counter()

    def mk(cls, a, b, folio, st):
        return {"cls": cls, "pop": a["pop"], "folio": folio, "stratum": st, "S": a["toks"][-1][0][-1], "pre": parse_p70(b["toks"][0][0])[0],
                "prev_len": len(a["toks"][-1][0]), "one_token": len(a["toks"]) == 1 or len(b["toks"]) == 1, "hand": a["hand"]}

    for folio, lines in seq.items():
        idx = {l: i for i, (l, _d) in enumerate(rawidx.get(folio, []))}
        for r in lines:
            if r["pop"] is None:
                continue
            if r["pb"]:
                X["within_pb_record"] += 1; continue
            tk = r["toks"]
            for (va, ua, _ga), (vb, ub, gb) in zip(tk, tk[1:]):
                if ua or ub:
                    continue
                c = "gap" if gb else "within"
                P[c].append({"cls": c, "pop": r["pop"], "folio": folio, "stratum": (folio, r["pid"]), "S": va[-1], "pre": parse_p70(vb)[0],
                             "prev_len": len(va), "one_token": False, "hand": r["hand"]})
        n = len(lines)
        for i in range(n - 1):
            a, b = lines[i], lines[i + 1]
            cls = "para" if a["end"] else "line"
            why = None
            if a["pop"] is None or b["pop"] is None: why = "no_population"
            elif idx.get(b["locus"]) != idx.get(a["locus"], -5) + 1: why = "bridges_dropped_record"
            elif b["start"] != a["end"]: why = "marker_mismatch"
            elif b["loc"].startswith("="): why = "same_line_title"
            elif a["pb"] or b["pb"]: why = "pb_record"
            elif a["pop"] != b["pop"]: why = "population_change"
            elif not a["toks"] or not b["toks"]: why = "empty_line"
            elif a["toks"][-1][1] or b["toks"][0][1]: why = "uncertain_edge"
            if why:
                X[f"{cls}_{why}"] += 1
            else:
                P[cls].append(mk(cls, a, b, folio, folio if cls == "para" else (folio, a["pid"])))
        for i in range(n - 2):
            a, m, b = lines[i], lines[i + 1], lines[i + 2]
            if a["end"]:
                continue
            why = None
            if a["pop"] is None or m["pop"] is None or b["pop"] is None: why = "no_population"
            elif idx.get(m["locus"]) != idx.get(a["locus"], -5) + 1 or idx.get(b["locus"]) != idx.get(m["locus"], -5) + 1: why = "bridges_dropped_record"
            elif m["end"] or m["start"] or b["start"]: why = "marker_mismatch"
            elif m["loc"].startswith("=") or b["loc"].startswith("="): why = "same_line_title"
            elif a["pb"] or m["pb"] or b["pb"]: why = "pb_record"
            elif a["pop"] != b["pop"]: why = "population_change"
            elif not a["toks"] or not b["toks"]: why = "empty_line"
            elif a["toks"][-1][1] or b["toks"][0][1]: why = "uncertain_edge"
            if why:
                X[f"lag2_{why}"] += 1
            else:
                P["lag2"].append(mk("lag2", a, b, folio, (folio, a["pid"])))
    return P, dict(X)


# ------------------------------------------------------------- statistics ---- #
def table(plist, key=lambda p: p["stratum"]):
    st = defaultdict(lambda: [0, 0, 0, 0])  # a (y,qo) b (y,other) c (n,qo) d (n,other)
    for p in plist:
        t = st[key(p)]
        if p["S"] == "y":
            t[0 if p["pre"] == "qo" else 1] += 1
        else:
            t[2 if p["pre"] == "qo" else 3] += 1
    return st


def rr(st):
    num = den = Fraction(0)
    for a, b, c, d in st.values():
        ny, no = a + b, c + d
        if ny == 0 or no == 0:
            continue
        num += Fraction(a * no, ny + no); den += Fraction(c * ny, ny + no)
    return float(num / den) if den else float("nan")


def odds(st):
    num = den = Fraction(0)
    for a, b, c, d in st.values():
        if a + b == 0 or c + d == 0:
            continue
        num += Fraction(a * d, a + b + c + d); den += Fraction(b * c, a + b + c + d)
    return float(num / den) if den else float("nan")


def cnts(st):
    a = sum(t[0] for t in st.values()); b = sum(t[1] for t in st.values()); c = sum(t[2] for t in st.values()); d = sum(t[3] for t in st.values())
    inf = [t for t in st.values() if (t[0] + t[1]) > 0 and (t[2] + t[3]) > 0]
    return {"n_pairs": a + b + c + d, "n_after_y": a + b, "n_after_other": c + d, "n_qo": a + c, "n_strata": len(st), "n_strata_informative": len(inf),
            "n_qo_informative": sum(t[0] + t[2] for t in inf), "R_plain": float(Fraction(a, a + b) / Fraction(c, c + d)) if (a + b and c + d and c) else float("nan")}


def own_null(plist, R, rng, n=1000):
    by = defaultdict(list)
    for p in plist:
        by[p["stratum"]].append(p)
    vals = []
    for _ in range(n):
        st = {}
        for k, v in by.items():
            pres = [p["pre"] for p in v]; order = rng.permutation(len(v))
            t = [0, 0, 0, 0]
            for i, p in enumerate(v):
                q = pres[order[i]] == "qo"
                t[(0 if q else 1) if p["S"] == "y" else (2 if q else 3)] += 1
            st[k] = t
        vals.append(rr(st))
    vals = np.array(vals, dtype=float)
    und = int(np.isnan(vals).sum()); fin = vals[~np.isnan(vals)]
    p = (1 + np.sum(fin >= R) + und) / (n + 1) if not isnan(R) else None
    return p, float(np.quantile(np.where(np.isnan(vals), np.inf, vals), 0.975, method="higher")), und / n


def folio_terms(plist, weight=None):
    out = defaultdict(lambda: [0.0, 0.0])
    st = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for p in plist:
        w = 1.0 if weight is None else weight(p); t = st[p["stratum"]]
        if p["S"] == "y":
            t[0 if p["pre"] == "qo" else 1] += w
        else:
            t[2 if p["pre"] == "qo" else 3] += w
    for k, (a, b, c, d) in st.items():
        ny, no = a + b, c + d
        if ny == 0 or no == 0:
            continue
        f = k[0] if isinstance(k, tuple) else k
        out[f][0] += a * no / (ny + no); out[f][1] += c * ny / (ny + no)
    return out


def own_boot(line, within, rng, n_boot):
    tl, tw = folio_terms(line), folio_terms(within)
    folios = sorted(set(tl) | set(tw)); n = len(folios)
    TL = np.array([tl.get(f, [0.0, 0.0]) for f in folios]); TW = np.array([tw.get(f, [0.0, 0.0]) for f in folios])
    R, rho, dR, drho = [], [], 0, 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        l, w = TL[idx].sum(axis=0), TW[idx].sum(axis=0)
        if l[1] <= 0: dR += 1
        else: R.append(l[0] / l[1])
        if l[1] <= 0 or w[1] <= 0 or w[0] <= 0 or w[0] / w[1] <= 1.0:
            drho += 1; continue
        rho.append((math.log(l[0] / l[1]) if l[0] > 0 else -math.inf) / math.log(w[0] / w[1]))
    R, rho = np.array(R), np.array(rho)
    return {"R_line_ci_lower": float(np.quantile(R, 0.025)), "R_line_ci_upper": float(np.quantile(R, 0.975)), "R_line_dropped": dR,
            "rho_ci_lower": float(np.quantile(rho, 0.025, method="inverted_cdf")), "rho_ci_upper": float(np.quantile(rho, 0.975, method="inverted_cdf")),
            "rho_dropped": drho}


def mi(sp):
    j = Counter(sp); n = len(sp); pa, pb = Counter(), Counter()
    for (a, b), c in j.items():
        pa[a] += c; pb[b] += c
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in j.items())


def h034(R, p, q975, status, ci_up):
    if status != "OK":
        return "INCONCLUSIVE_DEV"
    if R <= 1.1 or (ci_up is not None and ci_up < 1.5):
        return "FALSIFIED_DEV"
    return "SUPPORTED_DEV" if (R >= 1.5 and p <= 0.01) else "INCONCLUSIVE_DEV"


def h035(rho, lo, hi, flag, d34):
    ok = flag == "OK"
    if d34 == "FALSIFIED_DEV" or (ok and hi is not None and hi < 0.25):
        return "FALSIFIED_DEV"
    return "SUPPORTED_DEV" if (ok and rho is not None and lo is not None and rho >= 0.75 and lo >= 0.5) else "PARTIAL"


def h036(R, p, q975, status, n_qo_inf):
    if status != "OK":
        return "INCONCLUSIVE_DEV"
    if q975 >= R and n_qo_inf >= 100:
        return "FALSIFIED_DEV"
    return "SUPPORTED_DEV" if (R >= 1.5 and p <= 0.01) else "INCONCLUSIVE_DEV"


def main():
    res = json.loads((EXP / "results.json").read_text(encoding="utf-8"))
    rawidx = raw_scan(); seq = load()
    n_raw = sum(len(v) for v in rawidx.values()); n_parsed = sum(len(v) for v in seq.values())
    dropped = sorted(l for v in rawidx.values() for l, d in v if d)
    check(n_raw == res["records"]["raw_P_type"] == 4130 and n_parsed == res["records"]["parsed_running_text"] == 4075, f"record counts {n_raw}/{n_parsed}")
    check(dropped == sorted(res["records"]["dropped_by_parser"]) and len(dropped) == 55, "dropped loci")
    P, X = own_pairs(seq, rawidx)
    check(X == res["exclusions"], f"exclusions differ: {X} vs {res['exclusions']}")
    byp = {c: {p: [x for x in P[c] if x["pop"] == p] for p in POPS} for c in P}
    for c in ("line", "para", "lag2"):
        byp[c]["B_pooled"] = byp[c]["bio_B"] + byp[c]["other_B"]
    rng = np.random.default_rng(OWN_SEED)
    own_dec = {}
    for c in P:
        for p, pl in byp[c].items():
            r = res["enrichment"][c][p]
            st = table(pl); k = cnts(st)
            check(k["n_pairs"] == r["n_pairs"] == res["pair_counts"][c][p], f"n_pairs {c}/{p}: {k['n_pairs']} vs {r['n_pairs']}")
            R = rr(st)
            close(R, r["R_MH"], f"R_MH {c}/{p}"); close(odds(st), r["OR_MH"], f"OR_MH {c}/{p}"); close(k["R_plain"], r["R_plain"], f"R_plain {c}/{p}")
            for f in ("n_after_y", "n_after_other", "n_qo", "n_strata", "n_strata_informative", "n_qo_informative"):
                check(k[f] == r[f], f"{f} {c}/{p}: {k[f]} vs {r[f]}")
            if "R_MH_folio_strata" in r:
                close(rr(table(pl, key=lambda q: q["folio"])), r["R_MH_folio_strata"], f"R_MH folio strata {c}/{p}")
            if c in ("line", "para", "lag2"):
                p_own, q_own, und = own_null(pl, R, rng)
                if r["null_status"] == "OK":
                    check(abs(p_own - r["p_perm"]) <= 0.02 or (p_own <= 0.01 and r["p_perm"] <= 0.01), f"p_perm {c}/{p}: own {p_own} vs {r['p_perm']}")
                    check(abs(q_own - r["null_q975"]) <= 0.05 * max(1.0, abs(r["null_q975"])), f"q975 {c}/{p}: own {q_own} vs {r['null_q975']}")
                own_dec[(c, p)] = (R, p_own, q_own, "OK" if (und <= 0.05 and not isnan(R)) else "NOT_DEFINED", k["n_qo_informative"])
    # bootstrap: exact reproduction (one generator, POPS order)
    rb = np.random.default_rng(res["seeds"]["bootstrap"])
    for p in POPS:
        b = own_boot(byp["line"][p], byp["within"][p], rb, res["n_bootstrap"]); r = res["bootstrap"][p]
        for f in ("R_line_ci_lower", "R_line_ci_upper", "rho_ci_lower", "rho_ci_upper"):
            close(b[f], r[f], f"bootstrap {f} {p}")
        check(b["rho_dropped"] == r["rho_dropped"] and b["R_line_dropped"] == r["R_line_dropped"], f"bootstrap dropped {p}")
        Rl, Rw = res["enrichment"]["line"][p]["R_MH"], res["enrichment"]["within"][p]["R_MH"]
        pt = None if (isnan(Rl) or isnan(Rw) or Rw <= 1.0) else (math.log(Rl) / math.log(Rw) if Rl > 0 else float("-inf"))
        close(pt, res["persistence_rho"][p], f"rho point {p}")
    # MI / S1 point values on the line class
    sp = [(x["S"], x["pre"]) for x in byp["line"]["bio_B"]]
    I = mi(sp); close(I, res["mi_check"]["line_break_bio_B"]["I_bits"], "MI line bio_B")
    close(mi([(a == "y", b == "qo") for a, b in sp]) / I, res["mi_check"]["line_break_bio_B"]["S1"], "S1 line bio_B")
    # decisions from recorded numbers
    e, bb = res["enrichment"], res["bootstrap"]["bio_B"]
    d34 = h034(e["line"]["bio_B"]["R_MH"], e["line"]["bio_B"]["p_perm"], e["line"]["bio_B"]["null_q975"], e["line"]["bio_B"]["null_status"], bb["R_line_ci_upper"])
    d35 = h035(res["persistence_rho"]["bio_B"], bb["rho_ci_lower"], bb["rho_ci_upper"], bb["rho_ci_flag"], d34)
    pb = e["para"]["B_pooled"]
    d36 = h036(pb["R_MH"], pb["p_perm"], pb["null_q975"], pb["null_status"], pb["n_qo_informative"])
    ho = res["hypothesis_outcomes"]
    check((ho["H034"], ho["H035"], ho["H036"]) == (d34, d35, d36), f"decisions {ho} vs {(d34, d35, d36)}")
    lag = e["lag2"]["bio_B"]
    lag_sup = lag["null_status"] == "OK" and lag["R_MH"] >= 1.5 and lag["p_perm"] <= 0.01
    guard = "NOT_APPLICABLE" if d34 != "SUPPORTED_DEV" else ("ADJACENCY" if (not lag_sup and lag["R_MH"] < e["line"]["bio_B"]["R_MH"]) else "COMPOSITION_CONFOUNDED")
    check(res["composition_guard"] == guard, f"composition guard {res['composition_guard']} vs {guard}")
    # decisions under the validator's own null (pre-registered resolution)
    R, p_own, q_own, st_own, _ = own_dec[("line", "bio_B")]
    o34 = h034(R, p_own, q_own, st_own, bb["R_line_ci_upper"])
    if o34 != d34:
        check(ho["H034"] == "INCONCLUSIVE_DEV", f"H034 near threshold (own null {o34} vs run {d34}): recorded outcome must be INCONCLUSIVE_DEV")
    R, p_own, q_own, st_own, nq = own_dec[("para", "B_pooled")]
    o36 = h036(R, p_own, q_own, st_own, nq)
    if o36 != d36:
        check(ho["H036"] == "INCONCLUSIVE_DEV", f"H036 near threshold (own null {o36} vs run {d36}): recorded outcome must be INCONCLUSIVE_DEV")
    print("own-null decisions:", {"H034": o34, "H036": o36, "p_own_line_bio_B": own_dec[("line", "bio_B")][1], "p_own_para_B_pooled": own_dec[("para", "B_pooled")][1]})
    if errors:
        for x in errors:
            print("FAIL", x)
        return 1
    print("E022_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
