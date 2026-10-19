"""E007 post-reveal EXPLORATORY diagnostic (NOT part of the frozen gate).

Written after the first reveal showed Gate 5 failing only in section P. Asks
whether that failure depends on the prequential coding order (section P folios
f99-f102 sort first lexicographically, so they are coded with few counts).
Reports per-section bits/token under (a) natural folio order prequential and
(b) cross-fitted per-token costs (each token coded by the predictor trained on
the other four folds; order-free). The frozen decision in results.json is not
changed by anything here.

Run:  python experiments/E007_p70_replication/exploratory.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR))

import run  # noqa: E402
from voynichlab.mdl import KTCoder  # noqa: E402


def cross_fitted_per_token(seg, tokens, sigma):
    per = np.empty(len(tokens))
    for j in range(run.N_FOLDS):
        coder = KTCoder(sigma)
        for t in tokens:
            if t.fold != j:
                slots = seg(t.value)
                for i, v in enumerate(slots):
                    coder.update((i, slots[:i]), v)
        for k, t in enumerate(tokens):
            if t.fold == j:
                slots = seg(t.value)
                per[k] = sum(coder.cost((i, slots[:i]), v) for i, v in enumerate(slots))
    return per


def main() -> int:
    by_folio = run.load_population()
    lex = run.ordered(by_folio)
    nat = run.ordered(by_folio, key=run.natural_folio_key)
    sigma = len({c for t in lex for c in t.value})
    dev = [t for t in lex if t.fold in run.DEV_FOLDS]
    seg_a8, _ = run.build_a8(dev)
    segs = {"P70": run.parse_p70, "A0": lambda t: (t,), "A1": run.seg_a1, "A2": run.seg_a2,
            "A3": run.seg_a3, "A5": run.seg_a5, "A6": run.seg_a6, "A7": run.seg_a7, "A8": seg_a8}

    out = {"evidence_class": "EXPLORATORY_POST_REVEAL", "gated": False,
           "natural_order_prequential": {}, "cross_fitted": {}}
    for label, tokens, fn in (
        ("natural_order_prequential", nat, lambda s: run.prequential(s, nat, sigma)[0]),
        ("cross_fitted", lex, lambda s: cross_fitted_per_token(s, lex, sigma)),
    ):
        per = {m: fn(segs[m]) for m in run.MODELS}
        idx = defaultdict(list)
        for k, t in enumerate(tokens):
            idx[t.section].append(k)
        for sec in ("B", "H", "P", "S"):
            ix = np.array(idx[sec])
            sc = {m: float(per[m][ix].mean()) for m in run.MODELS}
            out[label][sec] = {"bits_per_token": sc, "lowest_model": min(sc, key=sc.get),
                               "p70_minus_best_other": sc["P70"] - min(v for m, v in sc.items() if m != "P70")}
    path = EXP_DIR / "exploratory_post_reveal.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {s: (v["lowest_model"], round(v["p70_minus_best_other"], 4)) for s, v in d.items()}
                      for k, d in out.items() if isinstance(d, dict)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
