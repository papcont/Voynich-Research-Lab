"""E016 — within-folio vocabulary locality (FIRST RUN).

Implements experiments/E016_folio_vocabulary_locality/PLAN.md. Writes results.json BEFORE
any interpretation. No scientific parameter here may be changed.

Run:  python experiments/E016_folio_vocabulary_locality/run.py
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
from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.gate import bootstrap_mean_ci  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
SEED_PERM, SEED_BOOT, NPERM = 20261050, 20261019, 1000
MARGIN_F, MARGIN_J, MIN_TOK_J = 0.02, 0.01, 20


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def load():
    toks, meta = defaultdict(list), {}
    for rec, _i, t in iter_strict_tokens(parse_ivtff(DATA)):
        if is_running_text(rec.locator):
            toks[rec.folio].append(t.value)
            meta[rec.folio] = (rec.meta.language, rec.meta.illustration, rec.meta.hand)
    return toks, meta


def strata(folios, meta):
    key = {f: (meta[f][0], meta[f][1]) for f in folios}
    cnt = Counter(key.values())
    for f in folios:
        if cnt[key[f]] < 3:
            key[f] = (meta[f][0], "rest")
    cnt = Counter(key.values())
    for f in folios:
        if cnt[key[f]] < 3:
            key[f] = ("rest", "rest")
    return key


def F_per_folio(toks, folios):
    return np.array([1 - len(set(toks[f])) / len(toks[f]) for f in folios])


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def J_adjacent(toks, folios):
    pairs = [(folios[i], folios[i + 1]) for i in range(len(folios) - 1)
             if len(toks[folios[i]]) >= MIN_TOK_J and len(toks[folios[i + 1]]) >= MIN_TOK_J]
    return float(np.mean([jaccard(toks[a], toks[b]) for a, b in pairs])), len(pairs)


def permute(toks, folios, groups, rng):
    """Deal each group's pooled tokens back to its folios, preserving folio sizes."""
    out = {}
    for members in groups.values():
        pool = [v for f in members for v in toks[f]]
        perm = rng.permutation(len(pool))
        k = 0
        for f in members:
            n = len(toks[f])
            out[f] = [pool[perm[j]] for j in range(k, k + n)]
            k += n
    return out


def main() -> int:
    raw = DATA.read_bytes()
    if git_blob_sha1(raw) != EXPECTED_BLOB:
        raise SystemExit("source identity mismatch")
    toks, meta = load()
    folios = sorted(toks)
    skey = strata(folios, meta)
    groups_n1 = defaultdict(list)
    for f in folios:
        groups_n1[skey[f]].append(f)
    groups_n2 = {"all": list(folios)}

    F_obs = F_per_folio(toks, folios)
    J_obs, n_pairs = J_adjacent(toks, folios)
    rng = np.random.default_rng(SEED_PERM)
    F_null = np.empty((NPERM, len(folios)))
    J_null = np.empty(NPERM)
    for r in range(NPERM):
        p = permute(toks, folios, groups_n1, rng)
        F_null[r] = F_per_folio(p, folios)
        J_null[r], _ = J_adjacent(p, folios)
    rng2 = np.random.default_rng(SEED_PERM + 1)
    F_null2 = np.array([F_per_folio(permute(toks, folios, groups_n2, rng2), folios).mean() for _ in range(NPERM)])

    excess_f = F_obs - F_null.mean(axis=0)
    dF = float(excess_f.mean())
    mean, lo, hi = bootstrap_mean_ci(excess_f, 10000, SEED_BOOT, 0.025)
    pF = float((1 + np.sum(F_null.mean(axis=1) >= F_obs.mean())) / (NPERM + 1))
    dec_F = "SUPPORTED_DEV" if (dF >= MARGIN_F and lo > 0 and pF <= 0.01) else "FALSIFIED_DEV" if hi < MARGIN_F else "INCONCLUSIVE_DEV"

    dJ = float(J_obs - J_null.mean())
    pJ = float((1 + np.sum(J_null >= J_obs)) / (NPERM + 1))
    # adjacent vs non-adjacent same-stratum pairs on the real text
    same = defaultdict(list)
    for i in range(len(folios) - 1):
        a, b = folios[i], folios[i + 1]
        if skey[a] == skey[b] and len(toks[a]) >= MIN_TOK_J and len(toks[b]) >= MIN_TOK_J:
            same["adjacent"].append(jaccard(toks[a], toks[b]))
    for g, members in groups_n1.items():
        big = [f for f in members if len(toks[f]) >= MIN_TOK_J]
        for i in range(len(big)):
            for j in range(i + 1, len(big)):
                if abs(folios.index(big[i]) - folios.index(big[j])) > 1:
                    same["nonadjacent"].append(jaccard(toks[big[i]], toks[big[j]]))
    adj_vs_non = float(np.mean(same["adjacent"]) - np.mean(same["nonadjacent"]))
    dec_J = ("SUPPORTED_DEV" if (dJ >= MARGIN_J and pJ <= 0.01 and adj_vs_non > 0)
             else "FALSIFIED_DEV" if np.quantile(J_null, 0.975) >= J_obs else "INCONCLUSIVE_DEV")

    by_lang = {}
    for L in ("A", "B"):
        ix = [i for i, f in enumerate(folios) if meta[f][0] == L]
        by_lang[L] = {"n_folios": len(ix), "F_obs": float(F_obs[ix].mean()), "excess": float(excess_f[ix].mean())}
    by_hand = defaultdict(list)
    for i, f in enumerate(folios):
        by_hand[str(meta[f][2])].append(excess_f[i])
    result = {
        "experiment": "E016", "evidence_class": "DEVELOPMENT", "gate_level_claimable": "none",
        "frozen_plan_commit": "f7f1fc7", "run_head_commit": head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"perm": SEED_PERM, "bootstrap": SEED_BOOT}, "n_permutations": NPERM,
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()},
        "population": {"n_folios": len(folios), "n_tokens": sum(len(v) for v in toks.values()),
                       "strata": {str(k): len(v) for k, v in groups_n1.items()}, "n_adjacent_pairs": n_pairs},
        "H024": {"F_obs": float(F_obs.mean()), "F_null_N1_mean": float(F_null.mean()), "F_null_N1_sd": float(F_null.mean(axis=1).std(ddof=1)),
                 "F_null_N2_mean": float(F_null2.mean()), "excess_dF": dF, "ci_lower": lo, "ci_upper": hi, "p_perm": pF,
                 "folios_with_positive_excess": int((excess_f > 0).sum()), "margin": MARGIN_F, "decision": dec_F,
                 "by_currier": by_lang, "by_hand_mean_excess": {h: float(np.mean(v)) for h, v in sorted(by_hand.items())}},
        "H025": {"J_adj_obs": J_obs, "J_adj_null_mean": float(J_null.mean()), "J_adj_null_q975": float(np.quantile(J_null, 0.975)),
                 "excess_dJ": dJ, "p_perm": pJ, "adjacent_same_stratum_mean": float(np.mean(same["adjacent"])),
                 "nonadjacent_same_stratum_mean": float(np.mean(same["nonadjacent"])), "adjacent_minus_nonadjacent": adj_vs_non,
                 "n_adjacent_same_stratum": len(same["adjacent"]), "n_nonadjacent_same_stratum": len(same["nonadjacent"]),
                 "margin": MARGIN_J, "decision": dec_J},
        "per_folio_excess": {f: float(x) for f, x in zip(folios, excess_f)},
        "claim_ceiling": "Structural statement about vocabulary distribution across folios; no meaning/authorship/quire claims.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in result[k].items() if kk not in ("by_currier", "by_hand_mean_excess")} for k in ("H024", "H025")}, indent=1))
    print(result["H024"]["by_currier"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
