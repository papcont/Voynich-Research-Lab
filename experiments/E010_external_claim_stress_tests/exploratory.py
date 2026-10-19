"""E010 post-run EXPLORATORY (not gated; written after results.json).

The frozen M_class/M_classprev code the class and then condition only the P70
prefix slot on it, so the class information is mostly not recouped. A fairer
descriptive-power test of the 49-class table codes the WHOLE TOKEN given its
class (type | class, backoff to the unconditioned token distribution) after the
class slot. This is a different model shape and only motivates a new
preregistration; it changes no E010 decision.

Models (Currier B, 5-fold cross-fit, same coder):
  W0        whole token, plain KT (E007 A0 shape)
  W_class   class slot (plain KT) + token | class (backoff)
  W_classprev class | previous class (backoff) + token | class (backoff)
Reference: M_Sfam from results.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR))

import run  # noqa: E402
from voynichlab.mdl import BackoffKTCoder  # noqa: E402


def code_w(coder, model, t, update):
    bits = 0.0
    if model != "W0":
        child = ("clsc", t.feat["prevcls"]) if model == "W_classprev" else None
        bits += coder.update(child, ("cls",), t.feat["cls"]) or 0.0 if update else coder.cost(child, ("cls",), t.feat["cls"])
        child_t = ("tc", t.feat["cls"])
    else:
        child_t = None
    if update:
        coder.update(child_t, ("t",), t.value)
    else:
        bits += coder.cost(child_t, ("t",), t.value)
    return bits


def crossfit(toks, model, sigma):
    per = np.empty(len(toks))
    for j in range(run.N_FOLDS):
        c = BackoffKTCoder(sigma)
        for t in toks:
            if t.fold != j:
                code_w(c, model, t, True)
        for k, t in enumerate(toks):
            if t.fold == j:
                per[k] = code_w(c, model, t, False)
    return per


def main() -> int:
    table, _ = run.load_table()
    toks, _ = run.load(table)
    sigma = len({c for t in toks for c in t.value})
    B = [t for t in toks if t.language == "B"]
    res = json.loads((EXP_DIR / "results.json").read_text(encoding="utf-8"))
    out = {"evidence_class": "EXPLORATORY_POST_RUN", "gated": False,
           "bits_per_token_out_of_fold_B": {m: float(crossfit(B, m, sigma).mean()) for m in ("W0", "W_class", "W_classprev")},
           "reference_M_Sfam": res["R2"]["bits_per_token_out_of_fold_B"]["M_Sfam"],
           "reference_M_class_frozen_shape": res["R2"]["bits_per_token_out_of_fold_B"]["M_class"]}
    (EXP_DIR / "exploratory_post_run.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
