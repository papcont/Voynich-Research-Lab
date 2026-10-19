"""E007 — independent P70 four-slot grammar replication (FIRST REVEAL runner).

Implements experiments/E007_p70_replication/PLAN.md as clarified by
PREFLIGHT_AMENDMENT_001.md and PREFLIGHT_AMENDMENT_002.md. Computes every target
metric once and writes results.json BEFORE any interpretation. No scientific
parameter here may be changed; all are frozen upstream.

Run:  python experiments/E007_p70_replication/run.py
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

from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.mdl import KTCoder, charcost  # noqa: E402
from voynichlab.p70 import parse_p70, is_degenerate, PREFIXES, GALLOWS, SUFFIXES  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"

# ---- frozen constants (mirrors PLAN.md / amendments / experiment.json) ----
A8_SEED = 20260907
MARGIN = 0.05                 # bits/token (Gates 2, 3)
FOLD_WINS = 4                 # of 5 (Gate 3)
N_FOLDS = 5
DEV_FOLDS = (0, 1, 2)
HOLD_FOLDS = (3, 4)
MAJOR_MIN_TOKENS = 2000
MAJOR_MIN_FOLIOS = 8
R1_NONDEG_MIN = 0.85
R1_EMPTY_CORE_BAND = (0.427, 0.627)
R1_TOTAL_H = 10.311
R1_TOTAL_H_TOL = 1.0
COVERAGE_MIN = 0.99
MODELS = ("P70", "A0", "A1", "A2", "A3", "A5", "A6", "A7", "A8")
GATE3_COMPETITORS = ("A1", "A2", "A3", "A5", "A6", "A7", "A8")
CORE_SLOT = {"P70": 2}
A7_PREFIXES = ("o", "y", "d", "s", "qo")
A7_BLOCKERS = ("ch", "sh")


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def efold(folio: str) -> int:
    return int(hashlib.sha256(("E007:" + folio.lower()).encode("utf-8")).hexdigest(), 16) % N_FOLDS


def elias_gamma(k: int) -> int:
    return 2 * int(math.floor(math.log2(k))) + 1


def natural_folio_key(folio: str):
    m = re.match(r"f(\d+)(.*)$", folio)
    return (int(m.group(1)), m.group(2)) if m else (10**9, folio)


# --------------------------------------------------------------------------- #
# population
# --------------------------------------------------------------------------- #
class Tok:
    __slots__ = ("value", "folio", "language", "section", "fold")

    def __init__(self, value, folio, language, section):
        self.value = value
        self.folio = folio
        self.language = language
        self.section = section
        self.fold = efold(folio)


def load_population():
    lines = list(parse_ivtff(DATA))
    by_folio = defaultdict(list)
    for rec, _i, t in iter_strict_tokens(lines):
        if is_running_text(rec.locator):
            by_folio[rec.folio].append(Tok(t.value, rec.folio, rec.meta.language, rec.meta.illustration))
    return by_folio


def ordered(by_folio, key=None):
    return [t for f in sorted(by_folio, key=key) for t in by_folio[f]]


# --------------------------------------------------------------------------- #
# segmentation models (Amendment 002 §3)
# --------------------------------------------------------------------------- #
def _longest_start(s, inv):
    best = ""
    for v in inv:
        if s.startswith(v) and len(v) > len(best):
            best = v
    return best


def _longest_end(s, inv):
    best = ""
    for v in inv:
        if s.endswith(v) and len(v) > len(best):
            best = v
    return best


def seg_a1(t):
    p = _longest_start(t, PREFIXES)
    return (p, t[len(p):])


def seg_a2(t):
    s = _longest_end(t, SUFFIXES)
    return (t[: len(t) - len(s)], s)


def seg_a3(t):
    if len(t) < 3:
        return ("", t, "")
    return (t[0], t[1:-1], t[-1])


def seg_a5(t):
    p, g, c, s = parse_p70(t)
    return (p, g + c, s)


def seg_a6(t):
    p, g, c, s = parse_p70(t)
    return (p, g, c + s)


def _parse_with_prefixes(t, prefixes, blockers):
    if blockers and any(t.startswith(b) for b in blockers):
        p = ""
    else:
        p = _longest_start(t, prefixes)
    rem = t[len(p):]
    g = _longest_start(rem, GALLOWS)
    rem = rem[len(g):]
    s = _longest_end(rem, SUFFIXES)
    c = rem[: len(rem) - len(s)]
    return (p, g, c, s)


def seg_a7(t):
    return _parse_with_prefixes(t, A7_PREFIXES, A7_BLOCKERS)


def seg_a7_literal(t):
    return _parse_with_prefixes(t, A7_PREFIXES, ())


def build_a8(dev_tokens):
    pool = defaultdict(list)
    tot = [0, 0, 0, 0]
    tot_len = 0
    for t in dev_tokens:
        lens = tuple(len(x) for x in parse_p70(t.value))
        pool[len(t.value)].append(lens)
        for i in range(4):
            tot[i] += lens[i]
        tot_len += len(t.value)
    for L in pool:
        pool[L].sort()
    fracs = [x / tot_len for x in tot]

    def cut_by_lens(t, lens):
        out, pos = [], 0
        for n in lens:
            out.append(t[pos:pos + n])
            pos += n
        return tuple(out)

    def seg(t):
        L = len(t)
        digest = hashlib.sha256(("E007-A8|%d|" % A8_SEED + t).encode("utf-8")).hexdigest()
        if L in pool:
            lens = pool[L][int(digest, 16) % len(pool[L])]
            return cut_by_lens(t, lens)
        cum, bounds = 0.0, []
        for f in fracs[:3]:
            cum += f
            bounds.append(int(math.floor(L * cum + 0.5)))
        b, prev = [], 0
        for x in bounds:
            x = min(max(x, prev), L)
            b.append(x)
            prev = x
        return (t[:b[0]], t[b[0]:b[1]], t[b[1]:b[2]], t[b[2]:])

    profile = {"lengths_in_pool": len(pool), "global_fractions": fracs,
               "dev_tokens": len(dev_tokens)}
    return seg, profile


def model_bits_table(sigma):
    inv = {
        "P70": list(PREFIXES) + list(GALLOWS) + list(SUFFIXES),
        "A0": [],
        "A1": list(PREFIXES),
        "A2": list(SUFFIXES),
        "A3": [],
        "A5": list(PREFIXES) + list(GALLOWS) + list(SUFFIXES),
        "A6": list(PREFIXES) + list(GALLOWS),
        "A7": list(A7_PREFIXES) + list(A7_BLOCKERS) + list(GALLOWS) + list(SUFFIXES),
        "A8": [],
    }
    slots = {"P70": 4, "A0": 1, "A1": 2, "A2": 2, "A3": 3, "A5": 3, "A6": 3, "A7": 4, "A8": 4}
    out = {}
    for m in MODELS:
        bits = sum(charcost(s, sigma) for s in inv[m]) + elias_gamma(slots[m])
        if m == "A8":
            bits += elias_gamma(A8_SEED + 1)
        out[m] = {"model_bits": bits, "n_inventory_strings": len(inv[m]), "n_slots": slots[m]}
    return out


# --------------------------------------------------------------------------- #
# coding
# --------------------------------------------------------------------------- #
def prequential(seg, tokens, sigma, core_slot=None):
    """Global prequential KT codelength. Returns per-token bits array and core-escape bits."""
    coder = KTCoder(sigma)
    per = np.empty(len(tokens))
    core_escape = 0.0
    cache = {}
    for k, t in enumerate(tokens):
        slots = cache.get(t.value)
        if slots is None:
            slots = seg(t.value)
            assert "".join(slots) == t.value, (t.value, slots)
            cache[t.value] = slots
        bits = 0.0
        for i, v in enumerate(slots):
            ctx = (i, slots[:i])
            _p, seen = coder.prob(ctx, v)
            b = coder.encode(ctx, v)
            if core_slot is not None and i == core_slot and not seen:
                core_escape += b
            bits += b
        per[k] = bits
    return per, core_escape


def train_then_code(seg, train, test, sigma):
    coder = KTCoder(sigma)
    for t in train:
        slots = seg(t.value)
        for i, v in enumerate(slots):
            coder.update((i, slots[:i]), v)
    total = 0.0
    for t in test:
        slots = seg(t.value)
        for i, v in enumerate(slots):
            total += coder.cost((i, slots[:i]), v)
    return total / len(test)


# --------------------------------------------------------------------------- #
# R1 diagnostics
# --------------------------------------------------------------------------- #
def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c)


def cond_entropy(pairs):
    """H(Y|X) for list of (x, y)."""
    return entropy(Counter(pairs)) - entropy(Counter(x for x, _ in pairs))


def mi_and_v(pairs):
    n = len(pairs)
    hx = entropy(Counter(x for x, _ in pairs))
    hy = entropy(Counter(y for _, y in pairs))
    hxy = entropy(Counter(pairs))
    mi = hx + hy - hxy
    xs = sorted({x for x, _ in pairs})
    ys = sorted({y for _, y in pairs})
    xi = {x: i for i, x in enumerate(xs)}
    yi = {y: i for i, y in enumerate(ys)}
    tab = np.zeros((len(xs), len(ys)))
    for x, y in pairs:
        tab[xi[x], yi[y]] += 1
    exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / n
    chi2 = float(((tab - exp) ** 2 / exp).sum())
    k = min(len(xs), len(ys)) - 1
    v = math.sqrt(chi2 / (n * k)) if k > 0 else float("nan")
    return {"mi_bits": mi, "cramers_v": v, "rows": len(xs), "cols": len(ys)}


def r1_diagnostics(tokens):
    parses = [parse_p70(t.value) for t in tokens]
    n = len(parses)
    recon = sum(1 for t, p in zip(tokens, parses) if "".join(p) == t.value) / n
    nondeg = sum(1 for p in parses if not is_degenerate(p)) / n
    empty_core = sum(1 for p in parses if p[2] == "") / n
    hP = entropy(Counter(p[0] for p in parses))
    hG = cond_entropy([((p[0],), p[1]) for p in parses])
    hC = cond_entropy([((p[0], p[1]), p[2]) for p in parses])
    hS = cond_entropy([((p[0], p[1], p[2]), p[3]) for p in parses])
    hW = entropy(Counter(t.value for t in tokens))
    total = hP + hG + hC + hS
    used = {name: len({p[i] for p in parses if p[i]}) for i, name in enumerate(("prefix", "gallows", "core", "suffix"))}
    sec = defaultdict(lambda: [0, 0, 0])
    for t, p in zip(tokens, parses):
        s = sec[t.section]
        s[0] += 1
        s[1] += not is_degenerate(p)
        s[2] += p[2] == ""
    section_rates = {str(k): {"tokens": v[0], "non_degenerate": v[1] / v[0], "empty_core": v[2] / v[0]}
                     for k, v in sorted(sec.items(), key=lambda kv: str(kv[0]))}
    fail = (nondeg < R1_NONDEG_MIN) or (
        not (R1_EMPTY_CORE_BAND[0] <= empty_core <= R1_EMPTY_CORE_BAND[1])
        and not (abs(total - R1_TOTAL_H) <= R1_TOTAL_H_TOL))
    return {
        "evidence_class": "EXTERNAL_REPLICATION/REPRODUCTION (approximate, ZL3b vs published ZL_2b)",
        "n_tokens": n,
        "reconstruction_exact_rate": recon,
        "non_degenerate_parse_rate": nondeg,
        "empty_core_rate": empty_core,
        "published_empty_core_rate": 0.527,
        "chain_rule_entropies_bits": {"H_P": hP, "H_G_given_P": hG, "H_C_given_PG": hC,
                                       "H_S_given_PGC": hS, "total": total},
        "published_entropies_bits": {"H_P": 2.788, "H_G_given_P": 1.374, "H_C_given_PG": 3.622,
                                     "H_S_given_PGC": 2.527, "total": 10.311},
        "H_W_bits": hW,
        "chain_rule_residual_bits": hW - total,
        "inventory_used_nonempty": used,
        "MI_section_prefix": mi_and_v([(t.section, p[0]) for t, p in zip(tokens, parses)]),
        "MI_core_suffix": mi_and_v([(p[2], p[3]) for p in parses]),
        "section_rates": section_rates,
        "tolerance_checks": {
            "non_degenerate_ge_0.85": nondeg >= R1_NONDEG_MIN,
            "empty_core_in_band": R1_EMPTY_CORE_BAND[0] <= empty_core <= R1_EMPTY_CORE_BAND[1],
            "total_entropy_within_1bit": abs(total - R1_TOTAL_H) <= R1_TOTAL_H_TOL,
        },
        "decision": "REPRODUCTION_FAILURE" if fail else "REPRODUCED",
        "note": "Reconstruction exactness and zero residual are constructive sanity checks, not evidence.",
    }


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    if not DATA.is_file():
        raise SystemExit("data/raw/ZL3b-n.txt missing; run scripts/fetch_zl3b.py")
    raw = DATA.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"source identity mismatch: {blob} != {EXPECTED_BLOB}")

    by_folio = load_population()
    tokens = ordered(by_folio)
    N = len(tokens)
    sigma_chars = sorted({c for t in tokens for c in t.value})
    sigma = len(sigma_chars)

    dev = [t for t in tokens if t.fold in DEV_FOLDS]
    hold = [t for t in tokens if t.fold in HOLD_FOLDS]
    seg_a8, a8_profile = build_a8(dev)
    segs = {
        "P70": parse_p70, "A0": lambda t: (t,), "A1": seg_a1, "A2": seg_a2, "A3": seg_a3,
        "A5": seg_a5, "A6": seg_a6, "A7": seg_a7, "A8": seg_a8,
    }

    # ---- lossless check (Gate 1) ----
    lossless = {m: sum(1 for t in tokens if "".join(segs[m](t.value)) == t.value) / N for m in MODELS}

    # ---- primary: global prequential ----
    per_token, core_escape = {}, {}
    for m in MODELS:
        per_token[m], core_escape[m] = prequential(segs[m], tokens, sigma, CORE_SLOT.get(m))
    data_bits = {m: float(per_token[m].sum()) for m in MODELS}
    bpt = {m: data_bits[m] / N for m in MODELS}
    mb = model_bits_table(sigma)
    primary = {m: {"data_bits": data_bits[m], "data_bits_per_token": bpt[m],
                   "model_bits": mb[m]["model_bits"],
                   "total_bits_per_token": (data_bits[m] + mb[m]["model_bits"]) / N,
                   "n_slots": mb[m]["n_slots"], "n_inventory_strings": mb[m]["n_inventory_strings"]}
               for m in MODELS}

    # ---- cross-fitted folds ----
    fold_scores = {m: [] for m in MODELS}
    fold_n = []
    for j in range(N_FOLDS):
        test = [t for t in tokens if t.fold == j]
        train = [t for t in tokens if t.fold != j]
        fold_n.append(len(test))
        for m in MODELS:
            fold_scores[m].append(train_then_code(segs[m], train, test, sigma))

    # ---- development -> holdout arm (reported, not gated) ----
    holdout_arm = {m: train_then_code(segs[m], dev, hold, sigma) for m in MODELS}

    # ---- subsets (Gate 5) ----
    idx_by_lang = defaultdict(list)
    idx_by_sec = defaultdict(list)
    for k, t in enumerate(tokens):
        idx_by_lang[t.language].append(k)
        idx_by_sec[t.section].append(k)
    sec_folios = defaultdict(set)
    for t in tokens:
        sec_folios[t.section].add(t.folio)
    major = sorted(s for s in idx_by_sec if s is not None
                   and len(idx_by_sec[s]) >= MAJOR_MIN_TOKENS and len(sec_folios[s]) >= MAJOR_MIN_FOLIOS)

    def subset_scores(idx):
        ix = np.array(idx)
        return {m: float(per_token[m][ix].sum() / len(ix)) for m in MODELS}

    def strictly_lowest_is_p70(scores):
        others = [scores[m] for m in MODELS if m != "P70"]
        return scores["P70"] < min(others)

    currier = {}
    for L in ("A", "B"):
        sc = subset_scores(idx_by_lang[L])
        currier[L] = {"n_tokens": len(idx_by_lang[L]), "bits_per_token": sc,
                      "lowest_model": min(sc, key=sc.get), "p70_lowest": strictly_lowest_is_p70(sc)}
    sections = {}
    for s in sorted(idx_by_sec, key=str):
        sc = subset_scores(idx_by_sec[s])
        sections[str(s)] = {"n_tokens": len(idx_by_sec[s]), "n_folios": len(sec_folios[s]),
                            "major": s in major, "bits_per_token": sc,
                            "lowest_model": min(sc, key=sc.get), "p70_lowest": strictly_lowest_is_p70(sc)}

    # ---- gates ----
    g1 = lossless["P70"] >= COVERAGE_MIN
    g2 = (bpt["A0"] - bpt["P70"]) >= MARGIN
    g3_detail = {}
    for c in GATE3_COMPETITORS:
        delta = bpt[c] - bpt["P70"]
        wins = sum(1 for j in range(N_FOLDS) if fold_scores["P70"][j] < fold_scores[c][j])
        g3_detail[c] = {"delta_bits_per_token": delta, "fold_wins": wins,
                        "pass": delta >= MARGIN or wins >= FOLD_WINS}
    g3 = all(v["pass"] for v in g3_detail.values())
    g4 = primary["P70"]["total_bits_per_token"] < primary["A0"]["total_bits_per_token"]
    g5_currier = all(currier[L]["p70_lowest"] for L in ("A", "B"))
    g5_sections = all(sections[str(s)]["p70_lowest"] for s in major)
    g5 = g5_currier and g5_sections

    r1 = r1_diagnostics(tokens)
    if r1["decision"] == "REPRODUCTION_FAILURE":
        decision = "REPRODUCTION_FAILURE"
    elif g1 and g2 and g3 and g4 and g5:
        decision = "STRUCTURAL_SUPPORT"
    else:
        decision = "REPRODUCED_BUT_NOT_VALIDATED"

    # ---- descriptive sensitivities (Amendment 002 §1, §3) ----
    nat_tokens = ordered(by_folio, key=natural_folio_key)
    nat = {m: float(prequential(segs[m], nat_tokens, sigma)[0].sum() / N) for m in MODELS}
    a7lit = float(prequential(seg_a7_literal, tokens, sigma)[0].sum() / N)

    result = {
        "experiment": "E007",
        "hypothesis": "H009",
        "evidence_class": {"R1": "EXTERNAL_REPLICATION/REPRODUCTION", "R2": "EXTERNAL_MODEL_EVALUATION",
                           "R3": "DEFERRED"},
        "prospectivity": "NON-PROSPECTIVE (P70 built on whole VMS; split is a comparison surface only)",
        "source_identity": {"path": "data/raw/ZL3b-n.txt", "git_blob_sha1": blob,
                            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)},
        "upstream": {"repo": "digitalgoldfisj79/Voynichdecomp",
                     "pin": "4f8a11174189148f312205d088910361ee67bde6"},
        "frozen_plan_commit": "2f77096",
        "amendment_commits": {"001": "d42d9f0", "002": "db81687"},
        "run_head_commit": head_commit(),
        "first_reveal_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"A8": A8_SEED},
        "population": {
            "n_tokens": N, "n_folios": len(by_folio), "sigma_size": sigma, "sigma": "".join(sigma_chars),
            "n_development_tokens": len(dev), "n_holdout_tokens": len(hold),
            "currier_counts": {str(k): len(v) for k, v in sorted(idx_by_lang.items(), key=lambda kv: str(kv[0]))},
            "fold_token_counts": fold_n,
            "order": "folios sorted lexicographically by id; file order within folio",
        },
        "models": list(MODELS),
        "deferred_models": {"A4": "DEFERRED_PRE_REVEAL (Amendment 001 §2)"},
        "a8_profile": a8_profile,
        "lossless_rate": lossless,
        "R1": r1,
        "R2": {
            "primary_global_prequential": primary,
            "p70_core_escape_bits": core_escape["P70"],
            "p70_core_escape_share_of_data_bits": core_escape["P70"] / data_bits["P70"],
            "cross_fitted_fold_bits_per_token": fold_scores,
            "development_to_holdout_bits_per_token": holdout_arm,
            "development_to_holdout_lowest_model": min(holdout_arm, key=holdout_arm.get),
            "currier": currier,
            "sections": sections,
            "major_sections_by_rule": [str(s) for s in major],
            "major_sections_expected": ["B", "H", "P", "S"],
        },
        "gates": {
            "G1_lossless_coverage_ge_0.99": g1,
            "G2_beats_A0_by_0.05": g2,
            "G2_delta_A0_minus_P70": bpt["A0"] - bpt["P70"],
            "G3_beats_each_competitor": g3,
            "G3_detail": g3_detail,
            "G4_total_bits_beats_A0": g4,
            "G5_currier_A_and_B": g5_currier,
            "G5_major_sections": g5_sections,
            "G5": g5,
        },
        "decision": decision,
        "descriptive_sensitivity": {
            "natural_folio_order_bits_per_token": nat,
            "A7_literal_bits_per_token": a7lit,
            "note": "Not gated (Amendment 002).",
        },
        "claim_ceiling": "Structural factorization only; NOT morphemes/language/decipherment.",
    }
    out = EXP_DIR / "results.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(json.dumps({"decision": decision, "R1": r1["decision"],
                      "bits_per_token": {m: round(bpt[m], 4) for m in MODELS}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
