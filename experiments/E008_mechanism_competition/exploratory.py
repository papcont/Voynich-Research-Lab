"""E008 post-reveal EXPLORATORY diagnostics (NOT part of the frozen gate).

Written after the first reveal showed every component NOT_INFORMATIVE under
the frozen scorecard, while criterion 5 (real penalty smaller than the
within-folio-shuffle penalty) held for S and L. Two questions:

1. Does the S / L penalty come from context fragmentation (novel contexts on
   holdout paying the char escape) rather than from absent information?
   Diagnostic: a PPM-style *backoff* variant of the same KT coder — a value
   unseen in the conditioned context is coded by the escape probability times
   the unconditioned base-context predictor (itself KT + char escape). This is
   a different coder, so it is EXPLORATORY and only motivates a new
   preregistration.
2. How often do exact / one-edit copies occur within W=5 on real holdout vs the
   N1 shuffle? (Interprets the C result.)

Run:  python experiments/E008_mechanism_competition/exploratory.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR))

import run  # noqa: E402
from voynichlab.mdl import KTCoder, charcost  # noqa: E402


class BackoffModel:
    """B-slots coded with (S,L) context; escape mass routed to the unconditioned context."""

    def __init__(self, base, comps, sigma, cache):
        self.base, self.comps = base, comps
        self.cond = KTCoder(sigma)
        self.plain = KTCoder(sigma)
        self.sigma = sigma
        self.cache = cache

    def slots(self, v):
        if self.base == "B0":
            return (v,)
        s = self.cache.get(v)
        if s is None:
            s = self.cache[v] = run.parse_p70(v)
        return s

    def code(self, tok, update):
        slots = self.slots(tok.value)
        S = tok.S if "S" in self.comps else None
        L = tok.L if "L" in self.comps else None
        bits = 0.0
        for i, v in enumerate(slots):
            cctx = ("base", i, slots[:i], S, L)
            pctx = ("base", i, slots[:i])
            p_c, seen = self.cond.prob(cctx, v)
            if seen:
                bits += -math.log2(p_c)
            else:
                p_esc = p_c  # escape mass of the conditioned context
                p_b, seen_b = self.plain.prob(pctx, v)
                b = -math.log2(p_esc) - math.log2(p_b)
                if not seen_b:
                    b += charcost(v, self.sigma)
                bits += b
            if update:
                self.cond.update(cctx, v)
                self.plain.update(pctx, v)
        return bits


def main() -> int:
    by_folio = run.load_lines()
    order = sorted(by_folio)
    toks = run.materialize(by_folio, order)
    sigma = len({c for t in toks for c in t.value})
    dev = [t for t in toks if t.fold in run.DEV_FOLDS]
    hold = [t for t in toks if t.fold in run.HOLD_FOLDS]
    cache = {}

    out = {"evidence_class": "EXPLORATORY_POST_REVEAL", "gated": False,
           "backoff_coder_holdout_bits_per_token": {}, "copy_path_shares_W5": {}}
    for base in ("B1", "B0"):
        for comps in (frozenset(), frozenset("S"), frozenset("L"), frozenset("SL")):
            m = BackoffModel(base, comps, sigma, cache)
            for t in dev:
                m.code(t, True)
            hb = sum(m.code(t, False) for t in hold) / len(hold)
            out["backoff_coder_holdout_bits_per_token"][base + "".join("+" + c for c in "SL" if c in comps)] = hb

    def shares(tt):
        c = Counter(run.src_slot(t, 5)[1] for t in tt if t.fold in run.HOLD_FOLDS)
        n = sum(c.values())
        return {"exact": c[0] / n, "edit": c[1] / n, "none": c[None] / n}

    out["copy_path_shares_W5"]["real"] = shares(toks)
    n1 = run.materialize(run.shuffled_copy(by_folio, order, run.SEED_N1, False), order)
    out["copy_path_shares_W5"]["N1_within_folio_shuffle"] = shares(n1)
    n0 = run.materialize(run.shuffled_copy(by_folio, order, run.SEED_N0, True), order)
    out["copy_path_shares_W5"]["N0_within_line_shuffle"] = shares(n0)

    path = EXP_DIR / "exploratory_post_reveal.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
