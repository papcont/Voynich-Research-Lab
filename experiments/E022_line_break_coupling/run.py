"""E022 — does the boundary coupling cross the line break? (FIRST RUN after plan freeze)

Implements experiments/E022_line_break_coupling/PLAN.md: pair classes within/gap/line/para/lag2,
paragraph-stratified Mantel–Haenszel enrichment, within-stratum pairing-permutation null, folio
bootstrap (R_MH(line) CI, persistence ratio rho), sensitivities, whole-table MI/S1 check,
decisions H034–H036. results.json first; interpretation only in REPORT.md.

Run:  python experiments/E022_line_break_coupling/run.py
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import INLINE_COMMENT_RE, PARA_MARK_RE, parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text, locus_type  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
BLOB_SHA1 = "2a4533ab9bdfa85db9bad602d590978953055df1"
SEED_PERM, SEED_BOOT, SEED_MI = 20261190, 20261019, 20261191
N_PERM, N_BOOT, N_SUB, N_SUB_PERM = 1000, 10000, 200, 20
POPS = ("bio_B", "other_B", "A")
CLASSES = ("within", "gap", "line", "para", "lag2")
POOLED_CLASSES = ("line", "para", "lag2")
EXPECTED_RECORDS = {"raw_P_type": 4130, "parsed_running_text": 4075}
LOCUS_RE = re.compile(r"^<(f[^>,]+),([^>]*)>\s+(.*)$")
GAP_RE = re.compile(r"<->|<~>")


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def population(lang, sec):
    if lang == "B":
        return "bio_B" if sec == "B" else "other_B"
    return "A" if lang == "A" else None


def len_class(n: int) -> str:
    return "<=2" if n <= 2 else "3-4" if n <= 4 else "5-6" if n <= 6 else ">=7"


# --------------------------------------------------------------------------- #
# records
# --------------------------------------------------------------------------- #
def raw_running_loci(path=DATA):
    """All P-type loci in raw-file order per folio, independent of parse_ivtff; flags records whose
    text starts with an inline comment (dropped by the parser)."""
    out = defaultdict(list)
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        m = LOCUS_RE.match(raw)
        if not m:
            continue
        locus, locator, text = m.groups()
        if "." not in locus or not is_running_text(locator):
            continue
        out[locus.split(".", 1)[0]].append((locus, text.lstrip().startswith("<!")))
    return dict(out)


def gap_tokens(raw_text):
    """[[value, uncertain, gap_before], ...]; gap_before = separator derives from <-> / <~>.
    Falls back to all-False flags (and reports it) if the segment-wise tokenisation differs."""
    ref = [[t.value, t.uncertain] for t in tokenize_surface(raw_text) if t.value]
    text = PARA_MARK_RE.sub("", INLINE_COMMENT_RE.sub("", raw_text))
    toks = []
    for si, seg in enumerate(GAP_RE.split(text)):
        st = [[t.value, t.uncertain, False] for t in tokenize_surface(seg) if t.value]
        if st and si > 0 and toks:
            st[0][2] = True
        toks.extend(st)
    if [[v, u] for v, u, _ in toks] != ref:
        return [[v, u, False] for v, u in ref], False
    return toks, True


def load_records(path=DATA):
    recs = defaultdict(list)
    n_gap_unresolved = 0
    for rec in parse_ivtff(path):
        if not is_running_text(rec.locator):
            continue
        toks, ok = gap_tokens(rec.raw_text)
        n_gap_unresolved += not ok
        recs[rec.folio].append({"locus": rec.locus, "locator": rec.locator or "", "ltype": locus_type(rec.locator),
                                "pop": population(rec.meta.language, rec.meta.illustration), "hand": rec.meta.hand,
                                "end": "<$>" in rec.raw_text, "start": "<%>" in rec.raw_text, "toks": toks})
    for folio in recs:
        pid = 0
        for r in recs[folio]:
            if r["start"]:
                pid += 1
            r["pid"] = pid
    return dict(recs), n_gap_unresolved


# --------------------------------------------------------------------------- #
# pairs
# --------------------------------------------------------------------------- #
def _pair(cls, a, b, folio, stratum):
    pv, nv = a["toks"][-1][0], b["toks"][0][0]
    return {"cls": cls, "pop": a["pop"], "folio": folio, "stratum": stratum, "S": pv[-1], "pre": parse_p70(nv)[0],
            "prev_len": len(pv), "one_token": (len(a["toks"]) == 1 or len(b["toks"]) == 1), "hand": a["hand"]}


def extract_pairs(recs, rawidx):
    """pairs[cls] = list of pair dicts; excl = Counter of exclusions per class."""
    pairs = {c: [] for c in CLASSES}
    excl = Counter()
    for folio in sorted(recs):
        lines = recs[folio]
        order = {l: i for i, (l, _d) in enumerate(rawidx.get(folio, []))}
        for r in lines:
            if r["pop"] is None:
                continue
            if r["ltype"] == "Pb":
                excl["within_pb_record"] += 1; continue
            t = r["toks"]
            for j in range(1, len(t)):
                if t[j][1] or t[j - 1][1]:
                    continue
                c = "gap" if t[j][2] else "within"
                pairs[c].append({"cls": c, "pop": r["pop"], "folio": folio, "stratum": (folio, r["pid"]), "S": t[j - 1][0][-1],
                                 "pre": parse_p70(t[j][0])[0], "prev_len": len(t[j - 1][0]), "one_token": False, "hand": r["hand"]})

        def check(cls, a, b, middle=None):
            if a["pop"] is None or b["pop"] is None or (middle is not None and middle["pop"] is None):
                return "no_population"
            if middle is None:
                if order.get(b["locus"], -9) != order.get(a["locus"], -99) + 1:
                    return "bridges_dropped_record"
                if b["start"] != a["end"]:
                    return "marker_mismatch"
                if b["locator"].startswith("="):
                    return "same_line_title"
                if a["ltype"] == "Pb" or b["ltype"] == "Pb":
                    return "pb_record"
            else:
                if order.get(middle["locus"], -9) != order.get(a["locus"], -99) + 1 or order.get(b["locus"], -9) != order.get(middle["locus"], -99) + 1:
                    return "bridges_dropped_record"
                if a["end"] or middle["end"] or middle["start"] or b["start"]:
                    return "marker_mismatch"
                if middle["locator"].startswith("=") or b["locator"].startswith("="):
                    return "same_line_title"
                if a["ltype"] == "Pb" or middle["ltype"] == "Pb" or b["ltype"] == "Pb":
                    return "pb_record"
            if a["pop"] != b["pop"]:
                return "population_change"
            if not a["toks"] or not b["toks"]:
                return "empty_line"
            if a["toks"][-1][1] or b["toks"][0][1]:
                return "uncertain_edge"
            return None

        for i in range(len(lines) - 1):
            a, b = lines[i], lines[i + 1]
            cls = "para" if a["end"] else "line"
            why = check(cls, a, b)
            if why:
                excl[f"{cls}_{why}"] += 1; continue
            pairs[cls].append(_pair(cls, a, b, folio, folio if cls == "para" else (folio, a["pid"])))
        for i in range(len(lines) - 2):
            a, m, b = lines[i], lines[i + 1], lines[i + 2]
            if a["end"]:
                continue  # lag2 is defined inside a paragraph only
            why = check("lag2", a, b, middle=m)
            if why:
                excl[f"lag2_{why}"] += 1; continue
            pairs["lag2"].append(_pair("lag2", a, b, folio, (folio, a["pid"])))
    return pairs, dict(excl)


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def strata_arrays(plist, weights=None):
    """{stratum: (is_y, is_qo, w)} with w = per-pair weights (1.0 unless post-stratified)."""
    by = defaultdict(lambda: ([], [], []))
    for p in plist:
        s = by[p["stratum"]]
        s[0].append(p["S"] == "y"); s[1].append(p["pre"] == "qo"); s[2].append(1.0 if weights is None else weights(p))
    return {k: (np.array(a, bool), np.array(b, bool), np.array(w, float)) for k, (a, b, w) in by.items()}


def mh_terms(is_y, is_qo, w):
    """(RR numerator, RR denominator, OR numerator, OR denominator) for one stratum; zeros if uninformative."""
    n_y = float(w[is_y].sum()); n_o = float(w[~is_y].sum())
    if n_y == 0 or n_o == 0:
        return 0.0, 0.0, 0.0, 0.0
    a = float(w[is_y & is_qo].sum()); c = float(w[~is_y & is_qo].sum())
    b, d = n_y - a, n_o - c
    N = n_y + n_o
    return a * n_o / N, c * n_y / N, a * d / N, b * c / N


def r_mh(arrs):
    num = den = 0.0
    for is_y, is_qo, w in arrs.values():
        t = mh_terms(is_y, is_qo, w); num += t[0]; den += t[1]
    return float(num / den) if den > 0 else float("nan")


def or_mh(arrs):
    num = den = 0.0
    for is_y, is_qo, w in arrs.values():
        t = mh_terms(is_y, is_qo, w); num += t[2]; den += t[3]
    return float(num / den) if den > 0 else float("nan")


def counts(arrs):
    y_qo = y_n = o_qo = o_n = 0
    n_inf = qo_inf = 0
    for is_y, is_qo, _w in arrs.values():
        y_qo += int((is_y & is_qo).sum()); y_n += int(is_y.sum()); o_qo += int((~is_y & is_qo).sum()); o_n += int((~is_y).sum())
        if 0 < is_y.sum() < len(is_y):
            n_inf += 1; qo_inf += int(is_qo.sum())
    return {"n_pairs": y_n + o_n, "n_after_y": y_n, "n_after_other": o_n, "n_qo": y_qo + o_qo, "n_strata": len(arrs),
            "n_strata_informative": n_inf, "n_qo_informative": qo_inf, "p_qo_after_y": (y_qo / y_n if y_n else None),
            "p_qo_after_other": (o_qo / o_n if o_n else None),
            "R_plain": float((y_qo / y_n) / (o_qo / o_n)) if (y_n and o_n and o_qo) else float("nan")}


def permute_pairing(arrs, rng):
    return {k: (is_y, is_qo[rng.permutation(len(is_qo))], w) for k, (is_y, is_qo, w) in arrs.items()}


def perm_null(arrs, rng, n_perm=N_PERM):
    return np.array([r_mh(permute_pairing(arrs, rng)) for _ in range(n_perm)], dtype=float)


def null_summary(null, R):
    undefined = int(np.isnan(null).sum())
    finite = null[~np.isnan(null)]
    inf_null = np.where(np.isnan(null), np.inf, null)
    return {"null_mean": float(finite.mean()) if len(finite) else None, "null_median": float(np.median(finite)) if len(finite) else None,
            "null_q975": float(np.quantile(inf_null, 0.975)), "null_undefined": undefined, "null_undefined_fraction": undefined / len(null),
            "p_perm": float((1 + np.sum(finite >= R) + undefined) / (len(null) + 1)) if not math.isnan(R) else None,
            "null_status": "OK" if undefined / len(null) <= 0.05 and not math.isnan(R) else "NOT_DEFINED"}


def enrichment_block(plist, rng, folio_sensitivity=False):
    arrs = strata_arrays(plist)
    R = r_mh(arrs)
    out = {"R_MH": R, "OR_MH": or_mh(arrs), **counts(arrs), **null_summary(perm_null(arrs, rng), R)}
    if folio_sensitivity:
        fol = strata_arrays([{**p, "stratum": p["folio"]} for p in plist])
        out["R_MH_folio_strata"] = r_mh(fol)
    return out


def folio_terms(plist, weights=None):
    """{folio: (RRnum, RRden)} summed over the folio's strata."""
    out = defaultdict(lambda: [0.0, 0.0])
    for stratum, (is_y, is_qo, w) in strata_arrays(plist, weights).items():
        folio = stratum[0] if isinstance(stratum, tuple) else stratum
        t = mh_terms(is_y, is_qo, w)
        out[folio][0] += t[0]; out[folio][1] += t[1]
    return out


def bootstrap(line_pairs, within_pairs, rng, n_boot=N_BOOT):
    """Paired folio bootstrap: R_MH(line) CI and persistence ratio rho (PLAN §2.3)."""
    tl, tw = folio_terms(line_pairs), folio_terms(within_pairs)
    folios = sorted(set(tl) | set(tw))
    TL = np.array([tl.get(f, [0.0, 0.0]) for f in folios]); TW = np.array([tw.get(f, [0.0, 0.0]) for f in folios])
    n = len(folios)
    R_line, rhos = [], []
    dropped_R = dropped_rho = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        l, w = TL[idx].sum(axis=0), TW[idx].sum(axis=0)
        if l[1] <= 0:
            dropped_R += 1
        else:
            R_line.append(l[0] / l[1])
        if l[1] <= 0 or w[1] <= 0 or w[0] <= 0 or w[0] / w[1] <= 1.0:
            dropped_rho += 1; continue
        lw = math.log(w[0] / w[1])
        lb = math.log(l[0] / l[1]) if l[0] > 0 else -math.inf
        rhos.append(lb / lw)
    R_line = np.array(R_line); rhos = np.array(rhos)
    out = {"n_folios": n, "n_boot": n_boot,
           "R_line_ci_lower": float(np.quantile(R_line, 0.025)) if len(R_line) else None,
           "R_line_ci_upper": float(np.quantile(R_line, 0.975)) if len(R_line) else None, "R_line_dropped": dropped_R,
           "rho_ci_lower": float(np.quantile(rhos, 0.025, method="inverted_cdf")) if len(rhos) else None,
           "rho_ci_upper": float(np.quantile(rhos, 0.975, method="inverted_cdf")) if len(rhos) else None,
           "rho_median": float(np.median(rhos)) if len(rhos) else None, "rho_dropped": dropped_rho,
           "rho_dropped_fraction": dropped_rho / n_boot, "rho_n_neg_inf": int(np.isneginf(rhos).sum()) if len(rhos) else 0}
    out["rho_ci_flag"] = "CI_UNRELIABLE" if out["rho_dropped_fraction"] > 0.05 else "OK"
    return out


def rho_point(R_line, R_within):
    if math.isnan(R_line) or math.isnan(R_within) or R_within <= 1.0:
        return None
    return float(math.log(R_line) / math.log(R_within)) if R_line > 0 else float("-inf")


def length_weights(line_pairs, within_pairs):
    pl = Counter(len_class(p["prev_len"]) for p in line_pairs); pw = Counter(len_class(p["prev_len"]) for p in within_pairs)
    nl, nw = sum(pl.values()), sum(pw.values())
    w = {c: (pl[c] / nl) / (pw[c] / nw) if pw[c] else 0.0 for c in set(pl) | set(pw)}
    return (lambda p: w.get(len_class(p["prev_len"]), 0.0)), {c: w[c] for c in sorted(w)}


def mi_bits(sp):
    joint = Counter(sp); n = len(sp); pa, pb = Counter(), Counter()
    for (a, b), c in joint.items():
        pa[a] += c; pb[b] += c
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in joint.items())


def s1_share(sp):
    I = mi_bits(sp)
    return (mi_bits([(a == "y", b == "qo") for a, b in sp]) / I) if I > 0 else float("nan")


def permuted_sp(plist, rng):
    by = defaultdict(list)
    for p in plist:
        by[p["stratum"]].append(p)
    out = []
    for v in by.values():
        pres = [p["pre"] for p in v]; order = rng.permutation(len(v))
        out.extend((v[i]["S"], pres[order[i]]) for i in range(len(v)))
    return out


def mi_check(line_pairs, within_pairs, rng):
    sp = [(p["S"], p["pre"]) for p in line_pairs]
    I = mi_bits(sp); S1 = s1_share(sp)
    null = np.array([mi_bits(permuted_sp(line_pairs, rng)) for _ in range(N_PERM)])
    brk = {"n_pairs": len(sp), "I_bits": I, "S1": S1, "null_mean": float(null.mean()), "null_q975": float(np.quantile(null, 0.975)),
           "excess": float(I - null.mean())}
    brk["remainder_excess"] = brk["excess"] * (1 - S1)
    arr = np.array(within_pairs, dtype=object); ex, s1s, rem = [], [], []
    for _ in range(N_SUB):
        sub = list(arr[rng.choice(len(arr), size=len(sp), replace=False)])
        ssp = [(p["S"], p["pre"]) for p in sub]
        Is = mi_bits(ssp); s1 = s1_share(ssp)
        nm = np.mean([mi_bits(permuted_sp(sub, rng)) for _ in range(N_SUB_PERM)])
        ex.append(Is - nm); s1s.append(s1); rem.append((Is - nm) * (1 - s1))
    within = {"n_subsamples": N_SUB, "n_perm_per_subsample": N_SUB_PERM, "excess_mean": float(np.mean(ex)), "excess_sd": float(np.std(ex, ddof=1)),
              "S1_mean": float(np.mean(s1s)), "remainder_excess_mean": float(np.mean(rem)), "remainder_excess_sd": float(np.std(rem, ddof=1))}
    return {"line_break_bio_B": brk, "within_matched_bio_B": within,
            "excess_ratio_total": brk["excess"] / within["excess_mean"] if within["excess_mean"] > 0 else None,
            "excess_ratio_remainder": brk["remainder_excess"] / within["remainder_excess_mean"] if within["remainder_excess_mean"] > 0 else None}


# --------------------------------------------------------------------------- #
# decisions (PLAN §2.4)
# --------------------------------------------------------------------------- #
def decide_h034(b, ci_upper):
    if b["null_status"] != "OK":
        return "INCONCLUSIVE_DEV"
    if b["R_MH"] <= 1.1 or (ci_upper is not None and ci_upper < 1.5):
        return "FALSIFIED_DEV"
    if b["R_MH"] >= 1.5 and b["p_perm"] <= 0.01:
        return "SUPPORTED_DEV"
    return "INCONCLUSIVE_DEV"


def composition_guard(h034, line_b, lag2_b):
    if h034 != "SUPPORTED_DEV":
        return "NOT_APPLICABLE"
    lag_sup = lag2_b["null_status"] == "OK" and lag2_b["R_MH"] >= 1.5 and lag2_b["p_perm"] <= 0.01
    return "ADJACENCY" if (not lag_sup and lag2_b["R_MH"] < line_b["R_MH"]) else "COMPOSITION_CONFOUNDED"


def decide_h035(rho, boot, h034):
    reliable = boot["rho_ci_flag"] == "OK"
    if h034 == "FALSIFIED_DEV" or (reliable and boot["rho_ci_upper"] is not None and boot["rho_ci_upper"] < 0.25):
        return "FALSIFIED_DEV"
    if reliable and rho is not None and boot["rho_ci_lower"] is not None and rho >= 0.75 and boot["rho_ci_lower"] >= 0.5:
        return "SUPPORTED_DEV"
    return "PARTIAL"


def decide_h036(b):
    if b["null_status"] != "OK":
        return "INCONCLUSIVE_DEV"
    if b["null_q975"] >= b["R_MH"] and b["n_qo_informative"] >= 100:
        return "FALSIFIED_DEV"
    if b["R_MH"] >= 1.5 and b["p_perm"] <= 0.01:
        return "SUPPORTED_DEV"
    return "INCONCLUSIVE_DEV"


# --------------------------------------------------------------------------- #
def main() -> int:
    raw = DATA.read_bytes()
    if git_blob_sha1(raw) != BLOB_SHA1:
        raise SystemExit("source identity mismatch")
    rawidx = raw_running_loci()
    recs, n_gap_unresolved = load_records()
    n_raw = sum(len(v) for v in rawidx.values()); n_parsed = sum(len(v) for v in recs.values())
    dropped = [l for v in rawidx.values() for l, d in v if d]
    if (n_raw, n_parsed) != (EXPECTED_RECORDS["raw_P_type"], EXPECTED_RECORDS["parsed_running_text"]):
        raise SystemExit(f"record set differs from the frozen plan: raw {n_raw}, parsed {n_parsed}")
    pairs, excl = extract_pairs(recs, rawidx)
    byp = {c: {p: [x for x in pairs[c] if x["pop"] == p] for p in POPS} for c in CLASSES}
    for c in POOLED_CLASSES:
        byp[c]["B_pooled"] = byp[c]["bio_B"] + byp[c]["other_B"]

    rng = np.random.default_rng(SEED_PERM)
    enrich = {c: {} for c in CLASSES}
    for c in CLASSES:
        for p in POPS + (("B_pooled",) if c in POOLED_CLASSES else ()):
            enrich[c][p] = enrichment_block(byp[c][p], rng, folio_sensitivity=(c in ("line", "lag2", "within")))
            print(f"{c:6s} {p:9s} R_MH {enrich[c][p]['R_MH']:.3f} plain {enrich[c][p]['R_plain']:.3f} n {enrich[c][p]['n_pairs']:5d} "
                  f"after_y {enrich[c][p]['n_after_y']:4d} qo {enrich[c][p]['n_qo']:4d} p {enrich[c][p]['p_perm']} q975 {enrich[c][p]['null_q975']:.3f} {enrich[c][p]['null_status']}")
    hands = {}
    for h in sorted({x["hand"] for x in byp["line"]["other_B"]}, key=str):
        hands[str(h)] = {"line": enrichment_block([x for x in byp["line"]["other_B"] if x["hand"] == h], rng),
                         "within": enrichment_block([x for x in byp["within"]["other_B"] if x["hand"] == h], rng)}
    # sensitivities (bio_B)
    no_mg = {c: [x for x in byp[c]["bio_B"] if x["S"] not in ("m", "g")] for c in ("line", "within")}
    sens = {"minus_mg": {c: enrichment_block(no_mg[c], rng) for c in ("line", "within")}}
    sens["minus_mg"]["rho"] = rho_point(sens["minus_mg"]["line"]["R_MH"], sens["minus_mg"]["within"]["R_MH"])
    wfun, wtab = length_weights(byp["line"]["bio_B"], byp["within"]["bio_B"])
    R_len = r_mh(strata_arrays(byp["within"]["bio_B"], wfun))
    sens["length_poststratified"] = {"weights": wtab, "R_MH_within_weighted": R_len, "rho_len": rho_point(enrich["line"]["bio_B"]["R_MH"], R_len)}
    R_wg = r_mh(strata_arrays(byp["within"]["bio_B"] + byp["gap"]["bio_B"]))
    sens["within_including_gaps"] = {"R_MH": R_wg, "rho": rho_point(enrich["line"]["bio_B"]["R_MH"], R_wg)}
    sens["without_one_token_lines"] = enrichment_block([x for x in byp["line"]["bio_B"] if not x["one_token"]], rng)

    rng_b = np.random.default_rng(SEED_BOOT)
    boot = {p: bootstrap(byp["line"][p], byp["within"][p], rng_b) for p in POPS}
    rho = {p: rho_point(enrich["line"][p]["R_MH"], enrich["within"][p]["R_MH"]) for p in POPS}

    rng_m = np.random.default_rng(SEED_MI)
    mi = mi_check(byp["line"]["bio_B"], byp["within"]["bio_B"], rng_m)

    h034 = decide_h034(enrich["line"]["bio_B"], boot["bio_B"]["R_line_ci_upper"])
    guard = composition_guard(h034, enrich["line"]["bio_B"], enrich["lag2"]["bio_B"])
    h035 = decide_h035(rho["bio_B"], boot["bio_B"], h034)
    h036 = decide_h036(enrich["para"]["B_pooled"])

    out = {"experiment": "E022", "evidence_class": "DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "FROZEN_PLAN_COMMIT_PLACEHOLDER", "run_head_commit": head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__},
           "seeds": {"perm": SEED_PERM, "bootstrap": SEED_BOOT, "mi": SEED_MI}, "n_permutations": N_PERM, "n_bootstrap": N_BOOT,
           "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_sha1": BLOB_SHA1},
           "records": {"raw_P_type": n_raw, "parsed_running_text": n_parsed, "dropped_by_parser": dropped, "gap_flag_unresolved_records": n_gap_unresolved},
           "pair_counts": {c: {p: len(byp[c][p]) for p in byp[c]} for c in CLASSES}, "exclusions": excl,
           "enrichment": enrich, "other_B_by_hand": hands, "sensitivities_bio_B": sens,
           "bootstrap": boot, "persistence_rho": rho, "mi_check": mi,
           "hypothesis_outcomes": {"H034": h034, "H035": h035, "H036": h036}, "composition_guard": guard,
           "claim_ceiling": "Structural transition statistics across line, gap and paragraph breaks; no meaning, language or glyph-identity claims."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("bootstrap bio_B:", {k: v for k, v in boot["bio_B"].items()})
    print("rho:", rho, "guard:", guard)
    print("MI:", json.dumps(mi, indent=1))
    print(json.dumps(out["hypothesis_outcomes"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
