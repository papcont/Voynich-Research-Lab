"""E022 — does the boundary coupling cross the line break? (FIRST RUN after plan freeze)

Implements experiments/E022_line_break_coupling/PLAN.md. Folio-stratified (Mantel–Haenszel)
qo-after-y enrichment on line-break, paragraph-break and within-line pairs; within-folio
pairing-permutation null; persistence ratio with folio bootstrap; matched-n MI check.
results.json first; interpretation only in REPORT.md.

Run:  python experiments/E022_line_break_coupling/run.py
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
BLOB_SHA1 = "2a4533ab9bdfa85db9bad602d590978953055df1"
SEED_PERM, SEED_BOOT, SEED_MI = 20261190, 20261019, 20261191
N_PERM, N_BOOT, N_SUB = 1000, 10000, 200
POPS = ("bio_B", "other_B", "A")


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


# --------------------------------------------------------------------------- #
# records and pairs
# --------------------------------------------------------------------------- #
def load_records(path=DATA):
    """Running-text records in file order per folio: (pop, para_end, para_start, [[value, uncertain], ...])."""
    recs = defaultdict(list)
    for rec in parse_ivtff(path):
        if not is_running_text(rec.locator):
            continue
        toks = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        recs[rec.folio].append((population(rec.meta.language, rec.meta.illustration),
                                "<$>" in rec.raw_text, "<%>" in rec.raw_text, toks))
    return dict(recs)


def prefix_of(value: str) -> str:
    return parse_p70(value)[0]


def extract_pairs(recs):
    """Return pairs[cls][pop] = list of (folio, S, prefix) for cls in line/para/within, plus exclusion counts."""
    pairs = {c: {p: [] for p in POPS} for c in ("line", "para", "within")}
    excl = Counter()
    for folio in sorted(recs):
        lines = recs[folio]
        for pop, _pe, _ps, toks in lines:
            if pop is None:
                continue
            for j in range(1, len(toks)):
                if toks[j][1] or toks[j - 1][1]:
                    continue
                pairs["within"][pop].append((folio, toks[j - 1][0][-1], prefix_of(toks[j][0])))
        for i in range(len(lines) - 1):
            pa, pe, _ps, ta = lines[i]
            pb, _pe2, ps2, tb = lines[i + 1]
            cls = "para" if pe else "line"
            if ps2 != pe:
                excl[f"{cls}_marker_mismatch"] += 1
                continue
            if pa is None or pb is None:
                excl[f"{cls}_no_population"] += 1
                continue
            if pa != pb:
                excl[f"{cls}_population_change"] += 1
                continue
            if not ta or not tb:
                excl[f"{cls}_empty_line"] += 1
                continue
            if ta[-1][1] or tb[0][1]:
                excl[f"{cls}_uncertain_edge"] += 1
                continue
            pairs[cls][pa].append((folio, ta[-1][0][-1], prefix_of(tb[0][0])))
    return pairs, dict(excl)


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def folio_arrays(plist):
    """{folio: (is_y bool array, is_qo bool array)}"""
    by = defaultdict(lambda: ([], []))
    for folio, S, pre in plist:
        by[folio][0].append(S == "y"); by[folio][1].append(pre == "qo")
    return {f: (np.array(a, dtype=bool), np.array(b, dtype=bool)) for f, (a, b) in by.items()}


def mh_terms(is_y, is_qo):
    """Per-folio Mantel–Haenszel numerator/denominator terms (0, 0 if a stratum is empty)."""
    n_y = int(is_y.sum()); n_o = int(len(is_y) - n_y)
    if n_y == 0 or n_o == 0:
        return 0.0, 0.0
    a = int((is_y & is_qo).sum()); c = int((~is_y & is_qo).sum())
    N = n_y + n_o
    return a * n_o / N, c * n_y / N


def r_mh(arrs):
    num = den = 0.0
    for is_y, is_qo in arrs.values():
        t = mh_terms(is_y, is_qo); num += t[0]; den += t[1]
    return float(num / den) if den > 0 else float("nan")


def r_plain(arrs):
    y_qo = y_n = o_qo = o_n = 0
    for is_y, is_qo in arrs.values():
        y_qo += int((is_y & is_qo).sum()); y_n += int(is_y.sum())
        o_qo += int((~is_y & is_qo).sum()); o_n += int((~is_y).sum())
    if y_n == 0 or o_n == 0 or o_qo == 0:
        return float("nan"), y_qo, y_n, o_qo, o_n
    return float((y_qo / y_n) / (o_qo / o_n)), y_qo, y_n, o_qo, o_n


def permute_pairing(arrs, rng):
    return {f: (is_y, is_qo[rng.permutation(len(is_qo))]) for f, (is_y, is_qo) in arrs.items()}


def perm_null(arrs, rng, n_perm=N_PERM):
    return np.array([r_mh(permute_pairing(arrs, rng)) for _ in range(n_perm)], dtype=float)


def enrichment_block(plist, rng):
    arrs = folio_arrays(plist)
    R = r_mh(arrs)
    null = perm_null(arrs, rng)
    Rp, y_qo, y_n, o_qo, o_n = r_plain(arrs)
    return {"R_MH": R, "R_plain": Rp, "n_pairs": len(plist), "n_after_y": y_n, "n_after_other": o_n,
            "p_qo_after_y": (y_qo / y_n if y_n else None), "p_qo_after_other": (o_qo / o_n if o_n else None),
            "n_folios": len(arrs), "n_folios_informative": sum(1 for a in arrs.values() if 0 < a[0].sum() < len(a[0])),
            "null_mean": float(np.nanmean(null)), "null_q975": float(np.nanquantile(null, 0.975)),
            "p_perm": float((1 + np.nansum(null >= R)) / (len(null) + 1))}


def bootstrap_rho(break_arrs, within_arrs, rng, n_boot=N_BOOT):
    """Folio bootstrap of rho = ln R_MH(break) / ln R_MH(within) over folios with pairs in either class."""
    folios = sorted(set(break_arrs) | set(within_arrs))
    zero = (0.0, 0.0)
    tb = np.array([mh_terms(*break_arrs[f]) if f in break_arrs else zero for f in folios])
    tw = np.array([mh_terms(*within_arrs[f]) if f in within_arrs else zero for f in folios])
    n = len(folios)
    rhos = []
    dropped = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        sb, sw = tb[idx].sum(axis=0), tw[idx].sum(axis=0)
        if sb[1] <= 0 or sw[1] <= 0:
            dropped += 1; continue
        lb, lw = math.log(sb[0] / sb[1]) if sb[0] > 0 else -math.inf, math.log(sw[0] / sw[1]) if sw[0] > 0 else -math.inf
        if lb <= 0 or lw <= 0:
            dropped += 1; continue
        rhos.append(lb / lw)
    rhos = np.array(rhos)
    return {"n_folios": n, "n_boot": n_boot, "dropped": dropped, "dropped_fraction": dropped / n_boot,
            "ci_lower": float(np.quantile(rhos, 0.025)) if len(rhos) else None,
            "ci_upper": float(np.quantile(rhos, 0.975)) if len(rhos) else None,
            "median": float(np.median(rhos)) if len(rhos) else None}


def mi_bits(pairs_sp):
    joint = Counter(pairs_sp); n = len(pairs_sp)
    pa, pb = Counter(), Counter()
    for (a, b), c in joint.items():
        pa[a] += c; pb[b] += c
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in joint.items())


def mi_excess_break(plist, rng, n_perm=N_PERM):
    by = defaultdict(list)
    for folio, S, pre in plist:
        by[folio].append((S, pre))
    I = mi_bits([sp for v in by.values() for sp in v])
    null = []
    for _ in range(n_perm):
        perm = []
        for v in by.values():
            pres = [p for _, p in v]
            order = rng.permutation(len(v))
            perm.extend((v[i][0], pres[order[i]]) for i in range(len(v)))
        null.append(mi_bits(perm))
    null = np.array(null)
    return {"I_bits": I, "null_mean": float(null.mean()), "null_q975": float(np.quantile(null, 0.975)), "excess": float(I - null.mean())}


def mi_excess_within_matched(plist, n_match, rng, n_sub=N_SUB):
    arr = np.array(plist, dtype=object)
    ex, raw = [], []
    for _ in range(n_sub):
        idx = rng.choice(len(arr), size=n_match, replace=False)
        sub = [tuple(x) for x in arr[idx]]
        I = mi_bits([(S, p) for _f, S, p in sub])
        by = defaultdict(list)
        for f, S, p in sub:
            by[f].append((S, p))
        perm = []
        for v in by.values():
            pres = [p for _, p in v]; order = rng.permutation(len(v))
            perm.extend((v[i][0], pres[order[i]]) for i in range(len(v)))
        ex.append(I - mi_bits(perm)); raw.append(I)
    return {"n_match": n_match, "n_subsamples": n_sub, "I_mean": float(np.mean(raw)), "excess_mean": float(np.mean(ex)), "excess_sd": float(np.std(ex, ddof=1))}


# --------------------------------------------------------------------------- #
# decisions (PLAN §2.3)
# --------------------------------------------------------------------------- #
def decide_h034(b):
    if b["R_MH"] >= 1.5 and b["p_perm"] <= 0.01:
        return "SUPPORTED_DEV"
    if b["R_MH"] <= 1.1 or b["null_q975"] >= b["R_MH"]:
        return "FALSIFIED_DEV"
    return "INCONCLUSIVE_DEV"


def decide_h035(rho, ci_lo, ci_hi, h034):
    if h034 == "FALSIFIED_DEV" or (ci_hi is not None and ci_hi < 0.25):
        return "FALSIFIED_DEV"
    if rho is not None and ci_lo is not None and rho >= 0.75 and ci_lo >= 0.5:
        return "SUPPORTED_DEV"
    return "PARTIAL"


def decide_h036(b):
    if b["R_MH"] >= 1.5 and b["p_perm"] <= 0.01:
        return "SUPPORTED_DEV"
    if b["null_q975"] >= b["R_MH"] and b["n_after_y"] >= 100:
        return "FALSIFIED_DEV"
    return "INCONCLUSIVE_DEV"


def main() -> int:
    raw = DATA.read_bytes()
    if git_blob_sha1(raw) != BLOB_SHA1:
        raise SystemExit("source identity mismatch")
    recs = load_records()
    pairs, excl = extract_pairs(recs)
    rng = np.random.default_rng(SEED_PERM)
    enrich = {cls: {p: enrichment_block(pairs[cls][p], rng) for p in POPS} for cls in ("line", "para", "within")}
    pooled_B_para = pairs["para"]["bio_B"] + pairs["para"]["other_B"]
    enrich["para"]["B_pooled"] = enrichment_block(pooled_B_para, rng)
    # persistence ratio per population
    rng_b = np.random.default_rng(SEED_BOOT)
    rho = {}
    for p in POPS:
        Rb, Rw = enrich["line"][p]["R_MH"], enrich["within"][p]["R_MH"]
        point = (math.log(Rb) / math.log(Rw)) if (Rb > 0 and Rw > 1) else None
        rho[p] = {"point": point, **bootstrap_rho(folio_arrays(pairs["line"][p]), folio_arrays(pairs["within"][p]), rng_b)}
    # whole-table MI check (bio_B)
    rng_m = np.random.default_rng(SEED_MI)
    mi = {"line_break_bio_B": mi_excess_break(pairs["line"]["bio_B"], rng_m),
          "within_matched_bio_B": mi_excess_within_matched(pairs["within"]["bio_B"], len(pairs["line"]["bio_B"]), rng_m)}
    mi["excess_ratio"] = (mi["line_break_bio_B"]["excess"] / mi["within_matched_bio_B"]["excess_mean"]
                          if mi["within_matched_bio_B"]["excess_mean"] > 0 else None)
    h034 = decide_h034(enrich["line"]["bio_B"])
    h035 = decide_h035(rho["bio_B"]["point"], rho["bio_B"]["ci_lower"], rho["bio_B"]["ci_upper"], h034)
    h036 = decide_h036(enrich["para"]["B_pooled"])
    out = {"experiment": "E022", "evidence_class": "DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "FROZEN_PLAN_COMMIT_PLACEHOLDER", "run_head_commit": head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__},
           "seeds": {"perm": SEED_PERM, "bootstrap": SEED_BOOT, "mi": SEED_MI}, "n_permutations": N_PERM, "n_bootstrap": N_BOOT,
           "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_sha1": BLOB_SHA1},
           "pair_counts": {cls: {p: len(pairs[cls][p]) for p in POPS} for cls in pairs}, "exclusions": excl,
           "enrichment": enrich, "persistence_rho": rho, "mi_check": mi,
           "hypothesis_outcomes": {"H034": h034, "H035": h035, "H036": h036},
           "claim_ceiling": "Structural transition statistics across line and paragraph breaks; no meaning, language or glyph-identity claims."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for cls in ("within", "line", "para"):
        for p, b in enrich[cls].items():
            print(f"{cls:7s} {p:9s} R_MH {b['R_MH']:.3f} (plain {b['R_plain']:.3f}) n {b['n_pairs']} after_y {b['n_after_y']} p {b['p_perm']:.4f} q975 {b['null_q975']:.3f}")
    print("rho:", {p: (None if rho[p]["point"] is None else round(rho[p]["point"], 3), rho[p]["ci_lower"], rho[p]["ci_upper"]) for p in POPS})
    print("MI:", json.dumps(mi, indent=1))
    print(json.dumps(out["hypothesis_outcomes"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
