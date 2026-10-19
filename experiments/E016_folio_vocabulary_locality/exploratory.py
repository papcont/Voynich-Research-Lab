"""E016 post-run EXPLORATORY (not gated): adjacency with an ORDER-permutation null.

The frozen H025 null permuted tokens within strata, which also destroys folio-specific
vocabulary and therefore raises every pairwise Jaccard; it answers "is adjacent sharing
above pooled-stratum sharing", not "is adjacent sharing above non-adjacent sharing".
Here folio ORDER is permuted (globally, and within strata) with vocabularies intact, and
J_adj is recomputed: a correct null for codex-order locality. Motivates a new
preregistration only; the frozen H025 decision stands.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
EXP = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))
import run as R

toks, meta = R.load()
folios = sorted(toks)
skey = R.strata(folios, meta)
J_obs, n = R.J_adjacent(toks, folios)
rng = np.random.default_rng(20261051)
glob = []
for _ in range(1000):
    order = [folios[i] for i in rng.permutation(len(folios))]
    glob.append(R.J_adjacent(toks, order)[0])
within = []
groups = {}
for f in folios:
    groups.setdefault(skey[f], []).append(f)
for _ in range(1000):
    order = list(folios)
    for members in groups.values():
        idx = [folios.index(f) for f in members]
        perm = rng.permutation(len(members))
        for i, j in zip(idx, perm):
            order[i] = members[j]
    within.append(R.J_adjacent(toks, order)[0])
glob, within = np.array(glob), np.array(within)
out = {"evidence_class": "EXPLORATORY_POST_RUN", "gated": False, "J_adj_obs": J_obs, "n_pairs": n,
       "order_null_global": {"mean": float(glob.mean()), "q975": float(np.quantile(glob, 0.975)), "p": float((1 + (glob >= J_obs).sum()) / 1001)},
       "order_null_within_strata": {"mean": float(within.mean()), "q975": float(np.quantile(within, 0.975)), "p": float((1 + (within >= J_obs).sum()) / 1001)}}
(EXP / "exploratory_post_run.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
