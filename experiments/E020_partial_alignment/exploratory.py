"""E020 post-run EXPLORATORY (not gated): per-class edge-gain shares under A3 for Voynich and
MIX(p*), plus an alphabet-size-normalised concentration 1 - H(shares)/log2(n_classes).
The frozen H030c top-1 rule is confounded by the number of previous-character classes
(verbose stream: 11; Voynich: 21); this diagnostic informs a corrected rule only."""
from __future__ import annotations
import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab import signature as SG
EXP = Path(__file__).resolve().parent
RUNS = ROOT / "runs" / "E020"

def shares(name):
    d = json.loads((RUNS / name).read_text(encoding="utf-8"))
    lines = {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}
    toks = SG.tokens(lines, SG.a3_slots, d["order"])
    sigma = len({c for t in toks for c in t.value})
    g = SG._crossfit_backoff(toks, {}, sigma) - SG._crossfit_backoff(toks, {0: ("S",)}, sigma)
    by = defaultdict(float)
    for t, x in zip(toks, g):
        by[t.S] += x
    tot = sum(v for v in by.values() if v > 0)
    pos = {k: v / tot for k, v in by.items() if v > 0}
    H = -sum(p * math.log2(p) for p in pos.values())
    n = len(pos)
    return {"n_classes_positive": n, "top5": sorted(pos.items(), key=lambda kv: -kv[1])[:5], "entropy_bits": H,
            "concentration_1_minus_H_over_log2n": 1 - H / math.log2(n) if n > 1 else float("nan")}

out = {"evidence_class": "EXPLORATORY_POST_RUN", "gated": False, "voynich": shares("V_matched.json"), "mix": shares("MIX_N_ITA.json")}
(EXP / "exploratory_post_run.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
