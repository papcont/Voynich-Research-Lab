"""E006 — frozen canonical final-chain holdout test (FIRST REVEAL runner).

Implements experiments/E006_canonical_sequence_holdout/PLAN.md as clarified by
PREFLIGHT_AMENDMENT_001.md. Computes the holdout target metric exactly once and
writes results.json BEFORE any interpretation. No scientific parameter here may
be changed; all are frozen upstream.

Run:  python experiments/E006_canonical_sequence_holdout/run.py
"""
from __future__ import annotations

import hashlib
import json
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
from voynichlab.canonical import parse_fused_token, STEMS, FINALS  # noqa: E402
from voynichlab.metrics import jensen_shannon  # noqa: E402
from voynichlab.folds import folio_fold, HOLDOUT_FOLDS, DEVELOPMENT_FOLDS  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"

# ---- frozen constants (mirrors PLAN.md / experiment.json) ----
SEED = 20260831
RESAMPLES = 1000
N_MIN = 2                 # >=2 fused AND >=2 spaced occurrences per chain in holdout
POWER_FLOOR = 3           # <3 qualifying chains => INCONCLUSIVE_UNDERPOWERED
BAND_A_W = 1.0
BAND_B_W = 0.5
BAND_B_MAX = 10
N_DECILES = 10
FINALS_SET = set(FINALS)


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT)
        ).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# corpus -> per-folio strict-token streams + realization occurrences
# --------------------------------------------------------------------------- #
class Occurrence:
    __slots__ = ("chain", "folio", "language", "realization", "ctxA", "ctxB")

    def __init__(self, chain, folio, language, realization, ctxA, ctxB):
        self.chain = chain
        self.folio = folio
        self.language = language
        self.realization = realization
        self.ctxA = ctxA  # Counter surface -> weight (band A)
        self.ctxB = ctxB  # Counter surface -> weight (band B)


def build_folio_streams(lines):
    """folio -> (stream[list surface], per-line full token lists in file order)."""
    streams = defaultdict(list)          # folio -> list[surface]  (strict only)
    stream_pos = defaultdict(dict)       # folio -> {(line_ord, full_idx): stream_idx}
    lang = {}                            # folio -> language
    lines_by_folio = defaultdict(list)   # folio -> list[(line_ord, tokens)]
    line_ord = defaultdict(int)
    for rec in lines:
        f = rec.folio
        lang.setdefault(f, rec.meta.language)
        toks = tokenize_surface(rec.raw_text)
        lo = line_ord[f]
        line_ord[f] += 1
        lines_by_folio[f].append((lo, toks))
        for full_idx, t in enumerate(toks):
            if not t.uncertain and t.value:
                stream_pos[f][(lo, full_idx)] = len(streams[f])
                streams[f].append(t.value)
    return streams, stream_pos, lang, lines_by_folio


def context_counters(stream, consumed):
    """Weighted band-A / band-B context surface counters for a consumed span."""
    first, last = min(consumed), max(consumed)
    ctxA, ctxB = Counter(), Counter()
    lo = max(0, first - BAND_B_MAX)
    hi = min(len(stream), last + BAND_B_MAX + 1)
    for j in range(lo, hi):
        if j in consumed:
            continue
        d = min(abs(j - first), abs(j - last))
        if d == 1:
            ctxA[stream[j]] += BAND_A_W
        elif 2 <= d <= BAND_B_MAX:
            ctxB[stream[j]] += BAND_B_W
    return ctxA, ctxB


def detect_occurrences(streams, stream_pos, lang, lines_by_folio):
    occ = []
    for folio, per_lines in lines_by_folio.items():
        stream = streams[folio]
        for lo, toks in per_lines:
            for i, A in enumerate(toks):
                if A.uncertain or not A.value:
                    continue
                pA = parse_fused_token(A.value)
                if pA is None:
                    continue
                # FUSED: exact stem + two finals
                if len(pA) == 3 and pA[0] in STEMS and pA[1] in FINALS_SET and pA[2] in FINALS_SET:
                    idx = stream_pos[folio].get((lo, i))
                    if idx is not None:
                        cA, cB = context_counters(stream, {idx})
                        occ.append(Occurrence(pA, folio, lang.get(folio), "fused", cA, cB))
                    continue
                # SPACED: A = stem+f1 (len2), next token B strict == final, certain '.' between
                if len(pA) == 2 and pA[0] in STEMS and pA[1] in FINALS_SET and i + 1 < len(toks):
                    B = toks[i + 1]
                    if (not B.uncertain) and B.value in FINALS_SET and A.separator_after == ".":
                        iA = stream_pos[folio].get((lo, i))
                        iB = stream_pos[folio].get((lo, i + 1))
                        if iA is not None and iB is not None:
                            chain = (pA[0], pA[1], B.value)
                            cA, cB = context_counters(stream, {iA, iB})
                            occ.append(Occurrence(chain, folio, lang.get(folio), "spaced", cA, cB))
    return occ


# --------------------------------------------------------------------------- #
# distributions / JSD
# --------------------------------------------------------------------------- #
def normalize(counter):
    tot = sum(counter.values())
    if tot <= 0:
        return {}
    return {k: v / tot for k, v in counter.items()}


def pooled(occs, band):
    c = Counter()
    for o in occs:
        if band == "A":
            c.update(o.ctxA)
        elif band == "B":
            c.update(o.ctxB)
        else:
            c.update(o.ctxA)
            c.update(o.ctxB)
    return c


def mean_jsd(chain_pairs):
    """chain_pairs: list of (fused_dist, spaced_dist); skip empties. -> (mean, used_flags)."""
    vals = []
    for fd, sd in chain_pairs:
        if fd and sd:
            vals.append(jensen_shannon(fd, sd))
    return (float(np.mean(vals)) if vals else float("nan")), len(vals)


# --------------------------------------------------------------------------- #
# token-type context cache (for N1/N3 distractors) over holdout
# --------------------------------------------------------------------------- #
def token_type_index(streams, holdout_folios, lang):
    """Per holdout token type: combined context dist, count, majority language, length."""
    ctx = defaultdict(Counter)   # type -> combined context counter
    count = Counter()            # type -> occurrence count
    lang_count = defaultdict(Counter)  # type -> Counter(language)
    for folio in holdout_folios:
        stream = streams[folio]
        L = lang.get(folio)
        for idx, surf in enumerate(stream):
            count[surf] += 1
            lang_count[surf][L] += 1
            cA, cB = context_counters(stream, {idx})
            ctx[surf].update(cA)
            ctx[surf].update(cB)
    dist = {t: normalize(c) for t, c in ctx.items()}
    maj_lang = {t: lang_count[t].most_common(1)[0][0] for t in count}
    return dist, count, maj_lang


def decile_map(count):
    """token type -> decile 0..9 by holdout frequency (rank-based, ~equal-count bins)."""
    types = sorted(count, key=lambda t: (count[t], t))
    n = len(types)
    dm = {}
    for rank, t in enumerate(types):
        dm[t] = min(N_DECILES - 1, rank * N_DECILES // n) if n else 0
    return dm


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    if not DATA.is_file():
        raise SystemExit("data/raw/ZL3b-n.txt missing; run scripts/fetch_zl3b.py")
    raw = DATA.read_bytes()
    blob = git_blob_sha1(raw)
    sha256 = hashlib.sha256(raw).hexdigest()
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"source identity mismatch: {blob} != {EXPECTED_BLOB}")

    lines = list(parse_ivtff(DATA))
    streams, stream_pos, lang, lines_by_folio = build_folio_streams(lines)
    all_occ = detect_occurrences(streams, stream_pos, lang, lines_by_folio)

    holdout_folios = sorted(f for f in streams if folio_fold(f) in HOLDOUT_FOLDS)
    dev_folios = sorted(f for f in streams if folio_fold(f) in DEVELOPMENT_FOLDS)
    holdout_set = set(holdout_folios)

    hold_occ = [o for o in all_occ if o.folio in holdout_set]

    # group holdout occurrences by chain / realization
    by_chain = defaultdict(lambda: {"fused": [], "spaced": []})
    for o in hold_occ:
        by_chain[o.chain][o.realization].append(o)

    qualifying = sorted(
        c for c, d in by_chain.items()
        if len(d["fused"]) >= N_MIN and len(d["spaced"]) >= N_MIN
    )

    # development qualifying count (a count only; NOT the target metric) for transparency
    dev_by_chain = defaultdict(lambda: {"fused": 0, "spaced": 0})
    for o in all_occ:
        if o.folio in set(dev_folios):
            dev_by_chain[o.chain][o.realization] += 1
    dev_qual = sum(1 for d in dev_by_chain.values() if d["fused"] >= N_MIN and d["spaced"] >= N_MIN)

    rng = np.random.default_rng(SEED)

    result = {
        "experiment": "E006",
        "evidence_class": "FROZEN_HOLDOUT",
        "source_identity": {
            "path": "data/raw/ZL3b-n.txt",
            "git_blob_sha1": blob,
            "sha256": sha256,
            "bytes": len(raw),
        },
        "frozen_plan_commit": "4c80f70",
        "amendment_commit": "4323969",
        "run_head_commit": head_commit(),
        "first_reveal_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": SEED,
        "resamples": RESAMPLES,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "frozen_constants": {
            "stems": list(STEMS), "finals": list(FINALS),
            "primary_units": 3, "n_min": N_MIN, "power_floor": POWER_FLOOR,
            "band_A_weight": BAND_A_W, "band_B_weight": BAND_B_W, "band_B_max": BAND_B_MAX,
            "development_folds": list(DEVELOPMENT_FOLDS), "holdout_folds": list(HOLDOUT_FOLDS),
        },
        "holdout_folios": holdout_folios,
        "n_holdout_folios": len(holdout_folios),
        "n_development_folios": len(dev_folios),
        "development_qualifying_chains": dev_qual,
        "counts": {
            "holdout_occurrences_fused": sum(len(d["fused"]) for d in by_chain.values()),
            "holdout_occurrences_spaced": sum(len(d["spaced"]) for d in by_chain.values()),
            "distinct_holdout_chains": len(by_chain),
        },
        "qualifying_chains": ["|".join(c) for c in qualifying],
    }

    # per-chain occurrence detail
    chain_detail = []
    for c in qualifying:
        d = by_chain[c]
        chain_detail.append({
            "chain": "|".join(c),
            "fused_occ": len(d["fused"]),
            "spaced_occ": len(d["spaced"]),
            "folios_fused": sorted({o.folio for o in d["fused"]}),
            "folios_spaced": sorted({o.folio for o in d["spaced"]}),
            "languages_spaced": dict(Counter(o.language for o in d["spaced"])),
        })
    result["chain_detail"] = chain_detail

    # ---------------- underpowered branch ----------------
    if len(qualifying) < POWER_FLOOR:
        result["power_branch"] = "INCONCLUSIVE_UNDERPOWERED"
        result["D_obs"] = None
        result["band_A"] = None
        result["band_B"] = None
        result["N1"] = None
        result["N2"] = None
        result["N3"] = None
        result["leave_one_chain_out"] = None
        result["decision"] = "INCONCLUSIVE_UNDERPOWERED"
        result["decision_note"] = (
            f"{len(qualifying)} qualifying chains (< {POWER_FLOOR}); per PLAN §6 and "
            "PREFLIGHT_AMENDMENT_001 Resolution A this is INCONCLUSIVE, not falsification. "
            "H008 remains unresolved. No thresholds/grammar altered."
        )
        _write(result)
        return 0

    result["power_branch"] = "POWERED"

    # ---------------- observed metric ----------------
    # per-chain distributions (combined + per band)
    dist_combined = {}   # chain -> (fused_dist, spaced_dist)
    dist_A = {}
    dist_B = {}
    per_chain_jsd = {}
    for c in qualifying:
        d = by_chain[c]
        fc = normalize(pooled(d["fused"], "all"))
        sc = normalize(pooled(d["spaced"], "all"))
        dist_combined[c] = (fc, sc)
        dist_A[c] = (normalize(pooled(d["fused"], "A")), normalize(pooled(d["spaced"], "A")))
        dist_B[c] = (normalize(pooled(d["fused"], "B")), normalize(pooled(d["spaced"], "B")))
        per_chain_jsd["|".join(c)] = jensen_shannon(fc, sc) if (fc and sc) else None

    D_obs, used = mean_jsd([dist_combined[c] for c in qualifying])
    A_obs, _ = mean_jsd([dist_A[c] for c in qualifying])
    B_obs, _ = mean_jsd([dist_B[c] for c in qualifying])
    result["D_obs"] = D_obs
    result["per_chain_jsd"] = per_chain_jsd
    result["chains_used_in_D_obs"] = used
    result["band_A"] = {"mean_jsd": A_obs}
    result["band_B"] = {"mean_jsd": B_obs}

    # distractor caches over holdout
    tdist, tcount, tmaj = token_type_index(streams, holdout_folios, lang)
    dmap = decile_map(tcount)
    fused_decile = {c: dmap.get("".join(c), 0) for c in qualifying}

    # pools for N1: (decile, majority_language) -> list of types
    pool_n1 = defaultdict(list)
    for t in tcount:
        pool_n1[(dmap[t], tmaj[t])].append(t)
    for k in pool_n1:
        pool_n1[k].sort()
    pool_n1_bydec = defaultdict(list)
    for t in tcount:
        pool_n1_bydec[dmap[t]].append(t)
    for k in pool_n1_bydec:
        pool_n1_bydec[k].sort()

    # pools for N3: (decile, length, non-canonical) -> list of types
    pool_n3 = defaultdict(list)
    for t in tcount:
        if parse_fused_token(t) is None:
            pool_n3[(dmap[t], len(t))].append(t)
    for k in pool_n3:
        pool_n3[k].sort()

    # empirical spaced-language composition per chain
    spaced_lang = {c: [o.language for o in by_chain[c]["spaced"]] for c in qualifying}

    # ---------------- N1 ----------------
    n1_fallbacks = 0
    n1_null = np.empty(RESAMPLES)
    for r in range(RESAMPLES):
        pairs = []
        for c in qualifying:
            fd = dist_combined[c][0]
            langs = spaced_lang[c]
            tgt = langs[rng.integers(len(langs))]
            pool = pool_n1[(fused_decile[c], tgt)]
            if not pool:
                pool = pool_n1_bydec[fused_decile[c]]
                n1_fallbacks += 1
            t = pool[int(rng.integers(len(pool)))] if pool else None
            sd = tdist.get(t, {}) if t is not None else {}
            pairs.append((fd, sd))
        n1_null[r], _ = mean_jsd(pairs)
    p1 = float(np.mean(n1_null <= D_obs))
    result["N1"] = {
        "definition": "frequency-decile + Currier-language matched random pairing (holdout)",
        "p_value": p1,
        "null_mean": float(np.nanmean(n1_null)),
        "null_p05": float(np.nanpercentile(n1_null, 5)),
        "fallback_draws": int(n1_fallbacks),
        "one_sided": "P(null_D <= D_obs)",
    }

    # ---------------- N2 (within-folio label permutation) ----------------
    # strata: (chain, folio) -> list of occurrences (fused+spaced)
    strata = defaultdict(list)
    for c in qualifying:
        for rlz in ("fused", "spaced"):
            for o in by_chain[c][rlz]:
                strata[(c, o.folio)].append(o)
    mixed = [k for k, v in strata.items()
             if any(o.realization == "fused" for o in v) and any(o.realization == "spaced" for o in v)]
    if not mixed:
        result["N2"] = {
            "status": "DEGENERATE",
            "reason": "no (chain, folio) stratum contains both fused and spaced occurrences; "
                      "within-folio label permutation is the identity. Gate cannot be fully cleared.",
            "mixed_strata": 0,
            "p_value": None,
        }
        n2_ok = False
        p2 = None
    else:
        n2_null = np.empty(RESAMPLES)
        # fixed per-stratum label counts
        stratum_items = sorted(strata.items(), key=lambda kv: (kv[0][0], kv[0][1]))
        for r in range(RESAMPLES):
            fused_by_chain = defaultdict(list)
            spaced_by_chain = defaultdict(list)
            for (c, _folio), occs in stratum_items:
                labels = [o.realization for o in occs]
                perm = rng.permutation(len(labels))
                for o, pi in zip(occs, perm):
                    lab = labels[pi]
                    (fused_by_chain if lab == "fused" else spaced_by_chain)[c].append(o)
            pairs = []
            for c in qualifying:
                fd = normalize(pooled(fused_by_chain[c], "all"))
                sd = normalize(pooled(spaced_by_chain[c], "all"))
                pairs.append((fd, sd))
            n2_null[r], _ = mean_jsd(pairs)
        p2 = float(np.mean(n2_null <= D_obs))
        n2_ok = p2 < 0.05
        result["N2"] = {
            "status": "OK",
            "definition": "within-folio fused/spaced label permutation (counts preserved)",
            "mixed_strata": len(mixed),
            "p_value": p2,
            "null_mean": float(np.nanmean(n2_null)),
            "one_sided": "P(null_D <= D_obs)",
        }

    # ---------------- N3 (specificity, not a gate) ----------------
    n3_fallbacks = 0
    n3_null = np.empty(RESAMPLES)
    for r in range(RESAMPLES):
        pairs = []
        for c in qualifying:
            fd = dist_combined[c][0]
            fused_surface = "".join(c)
            pool = pool_n3[(fused_decile[c], len(fused_surface))]
            if not pool:
                n3_fallbacks += 1
                pairs.append((fd, {}))
                continue
            t = pool[int(rng.integers(len(pool)))]
            pairs.append((fd, tdist.get(t, {})))
        n3_null[r], _ = mean_jsd(pairs)
    p3 = float(np.mean(n3_null <= D_obs))
    result["N3"] = {
        "definition": "length + frequency-decile matched non-canonical token (specificity, not gate)",
        "p_value": p3,
        "null_mean": float(np.nanmean(n3_null)),
        "fallback_draws": int(n3_fallbacks),
        "one_sided": "P(null_D <= D_obs)",
    }

    # ---------------- leave-one-chain-out (N1 on reduced set) ----------------
    loo = {}
    if len(qualifying) >= 2:
        for rem in qualifying:
            sub = [c for c in qualifying if c != rem]
            sub_D, _ = mean_jsd([dist_combined[c] for c in sub])
            null = np.empty(RESAMPLES)
            for r in range(RESAMPLES):
                pairs = []
                for c in sub:
                    langs = spaced_lang[c]
                    tgt = langs[rng.integers(len(langs))]
                    pool = pool_n1[(fused_decile[c], tgt)] or pool_n1_bydec[fused_decile[c]]
                    t = pool[int(rng.integers(len(pool)))] if pool else None
                    pairs.append((dist_combined[c][0], tdist.get(t, {}) if t is not None else {}))
                null[r], _ = mean_jsd(pairs)
            loo["|".join(rem)] = {"D_without": sub_D, "N1_p_without": float(np.mean(null <= sub_D))}
    result["leave_one_chain_out"] = loo
    loo_ok = all(v["N1_p_without"] < 0.10 for v in loo.values()) if loo else False

    # ---------------- frozen decision gate ----------------
    primary_ok = p1 < 0.05
    if not mixed:
        decision = "INVALID_N2_DEGENERATE_GATE_NOT_CLEARABLE"
        note = ("Primary/N1 evaluated but N2 is degenerate (no within-folio mixed strata); "
                "per amendment the frozen three-part gate cannot be fully cleared.")
    elif primary_ok and n2_ok and loo_ok:
        decision = "SUPPORTED"
        note = "N1 p<0.05 AND N2 p<0.05 AND all leave-one-chain-out N1 p<0.10."
    else:
        decision = "WEAKENED_NOT_SUPPORTED"
        note = (f"gate not met: primary(N1 p<0.05)={primary_ok}, N2(p<0.05)={n2_ok}, "
                f"leave_one_chain_out(all p<0.10)={loo_ok}.")
    result["decision"] = decision
    result["decision_note"] = note
    result["gate"] = {
        "primary_N1_p_lt_0.05": primary_ok,
        "N2_p_lt_0.05": n2_ok,
        "leave_one_chain_out_all_p_lt_0.10": loo_ok,
        "band_B_present": (B_obs == B_obs),  # not NaN
    }
    _write(result)
    return 0


def _write(result):
    out = EXP_DIR / "results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(json.dumps({k: result[k] for k in ("power_branch", "decision")
                      if k in result}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
