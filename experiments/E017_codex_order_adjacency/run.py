"""E017 — codex-order vocabulary adjacency with an order-permutation null (FIRST RUN).

Implements experiments/E017_codex_order_adjacency/PLAN.md. Strata and loading are
imported from the frozen E016 runner. Writes results.json BEFORE any interpretation.

Run:  python experiments/E017_codex_order_adjacency/run.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
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


E016 = _load("e016_run", ROOT / "experiments" / "E016_folio_vocabulary_locality" / "run.py")
EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
SEED_ORDER, SEED_TYPE, NPERM, MIN_TOK, MARGIN = 20261060, 20261061, 1000, 20, 0.01
FOLIO_RE = re.compile(r"^f(\d+)([rv])(\d*)$")


def pair_type(a, b):
    ma, mb = FOLIO_RE.match(a), FOLIO_RE.match(b)
    if not ma or not mb:
        return "other"
    na, sa, nb, sb = int(ma.group(1)), ma.group(2), int(mb.group(1)), mb.group(2)
    if na == nb:
        return "same-leaf"
    if nb == na + 1 and sa == "v" and sb == "r":
        return "facing"
    return "other"


def adjacent_pairs(order, skey, toks):
    return [(order[i], order[i + 1]) for i in range(len(order) - 1)
            if skey[order[i]] == skey[order[i + 1]] and len(toks[order[i]]) >= MIN_TOK and len(toks[order[i + 1]]) >= MIN_TOK]


def J(pairs, toks):
    return float(np.mean([E016.jaccard(toks[a], toks[b]) for a, b in pairs])) if pairs else float("nan")


def main() -> int:
    raw = DATA.read_bytes()
    if E016.git_blob_sha1(raw) != E016.EXPECTED_BLOB:
        raise SystemExit("source identity mismatch")
    toks, meta = E016.load()
    folios = sorted(toks)
    skey = E016.strata(folios, meta)
    groups = defaultdict(list)
    for f in folios:
        groups[skey[f]].append(f)

    pairs = adjacent_pairs(folios, skey, toks)
    types = [pair_type(a, b) for a, b in pairs]
    J_obs = J(pairs, toks)
    by_lang_obs = {L: J([p for p in pairs if meta[p[0]][0] == L], toks) for L in ("A", "B")}

    # ---- order-permutation null within strata ----
    rng = np.random.default_rng(SEED_ORDER)
    null, null_lang = [], {"A": [], "B": []}
    positions = {g: [folios.index(f) for f in members] for g, members in groups.items()}
    for _ in range(NPERM):
        order = list(folios)
        for g, members in groups.items():
            perm = rng.permutation(len(members))
            for pos, j in zip(positions[g], perm):
                order[pos] = members[j]
        pp = adjacent_pairs(order, skey, toks)
        null.append(J(pp, toks))
        for L in ("A", "B"):
            null_lang[L].append(J([p for p in pp if meta[p[0]][0] == L], toks))
    null = np.array(null)
    dJ = float(J_obs - null.mean())
    pJ = float((1 + np.sum(null >= J_obs)) / (NPERM + 1))
    dJ_lang = {L: float(by_lang_obs[L] - np.nanmean(null_lang[L])) for L in ("A", "B")}
    dec_25b = ("SUPPORTED_DEV" if (dJ >= MARGIN and pJ <= 0.01 and dJ_lang["A"] > 0 and dJ_lang["B"] > 0)
               else "FALSIFIED_DEV" if np.quantile(null, 0.975) >= J_obs else "INCONCLUSIVE_DEV")

    # ---- pair-type label permutation ----
    jac = np.array([E016.jaccard(toks[a], toks[b]) for a, b in pairs])
    t = np.array(types)
    counts = dict(Counter(types))
    J_type = {k: float(jac[t == k].mean()) for k in ("same-leaf", "facing", "other") if (t == k).any()}
    D_obs = J_type.get("same-leaf", float("nan")) - J_type.get("facing", float("nan"))
    rng2 = np.random.default_rng(SEED_TYPE)
    Dn = []
    for _ in range(NPERM):
        tp = t[rng2.permutation(len(t))]
        Dn.append(jac[tp == "same-leaf"].mean() - jac[tp == "facing"].mean())
    Dn = np.array(Dn)
    pD = float((1 + np.sum(Dn >= D_obs)) / (NPERM + 1))
    dec_26 = ("SUPPORTED_DEV" if (D_obs >= MARGIN and pD <= 0.01) else "FALSIFIED_DEV" if (np.quantile(Dn, 0.975) >= D_obs or D_obs < 0)
              else "INCONCLUSIVE_DEV")

    result = {
        "experiment": "E017", "evidence_class": "DEVELOPMENT", "gate_level_claimable": "none",
        "frozen_plan_commit": "54ab005", "run_head_commit": E016.head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"order": SEED_ORDER, "type": SEED_TYPE}, "n_permutations": NPERM,
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()},
        "population": {"n_folios": len(folios), "n_adjacent_same_stratum_pairs": len(pairs), "pair_type_counts": counts,
                       "strata": {str(k): len(v) for k, v in groups.items()}},
        "H025b": {"J_adj_obs": J_obs, "null_mean": float(null.mean()), "null_q975": float(np.quantile(null, 0.975)),
                  "excess_dJ": dJ, "p_perm": pJ, "by_currier": {L: {"J_obs": by_lang_obs[L], "excess": dJ_lang[L]} for L in ("A", "B")},
                  "margin": MARGIN, "decision": dec_25b, "note": "overall excess EXPLORATORY-known from E016 check; Currier split new"},
        "H026": {"J_by_type": J_type, "D_same_leaf_minus_facing": float(D_obs), "null_mean": float(Dn.mean()), "null_q975": float(np.quantile(Dn, 0.975)),
                 "p_perm": pD, "margin": MARGIN, "decision": dec_26},
        "claim_ceiling": "Vocabulary distribution along the current folio order; no quire/binding/meaning claims.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"H025b": result["H025b"], "H026": result["H026"], "types": counts}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
