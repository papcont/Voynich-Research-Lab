"""Prequential KT description-length coder for the E007 benchmark (frozen §4.3).

Context-conditional Krichevsky-Trofimov predictor with an explicit escape for
novel values coded by a fixed char-level universal code. Identical estimator for
every segmentation model. No corpus access here; run.py drives it next cycle.

Per context c seen n times with m distinct values (counts n_v):
    denom      = n + 0.5 * (m + 1)
    P(seen v)  = (n_v + 0.5) / denom
    P(unseen)  = 0.5 / denom
    bits(v)    = -log2 P(seen v)                 if v already seen in c
               = -log2 P(unseen) + charcost(v)   if v is novel in c
The seen-values mass plus the single escape mass sum to 1 exactly.
The empty slot value is the empty string "" (logical ∅); real slot values are
non-empty, so there is no collision.
"""
from __future__ import annotations

import math


def charcost(value: str, sigma_size: int) -> float:
    """Fixed universal code length (bits) of a novel string over Σ plus an EOS symbol."""
    return (len(value) + 1) * math.log2(sigma_size + 1)


class KTCoder:
    """Prequential KT coder with char-escape. encode() returns bits and updates state."""

    def __init__(self, sigma_size: int):
        if sigma_size < 1:
            raise ValueError("sigma_size must be >= 1")
        self.sigma_size = sigma_size
        self.charbits = math.log2(sigma_size + 1)
        # context_key -> {"n": int, "counts": {value: int}}
        self._ctx: dict[object, dict] = {}

    def _state(self, context_key) -> dict:
        st = self._ctx.get(context_key)
        if st is None:
            st = {"n": 0, "counts": {}}
            self._ctx[context_key] = st
        return st

    def prob(self, context_key, value) -> tuple[float, bool]:
        """Return (probability, seen) for value in context under current state."""
        st = self._ctx.get(context_key)
        if st is None or st["n"] == 0:
            n, counts = 0, {}
        else:
            n, counts = st["n"], st["counts"]
        m = len(counts)
        denom = n + 0.5 * (m + 1)
        if value in counts:
            return (counts[value] + 0.5) / denom, True
        return 0.5 / denom, False

    def cost(self, context_key, value) -> float:
        """Codelength in bits for value in context WITHOUT updating state."""
        p, seen = self.prob(context_key, value)
        bits = -math.log2(p)
        if not seen:
            bits += charcost(value, self.sigma_size)
        return bits

    def update(self, context_key, value) -> None:
        st = self._state(context_key)
        st["counts"][value] = st["counts"].get(value, 0) + 1
        st["n"] += 1

    def encode(self, context_key, value) -> float:
        """Prequential step: cost under current state, then update. Returns bits."""
        bits = self.cost(context_key, value)
        self.update(context_key, value)
        return bits


def demo() -> None:
    """Runnable self-check of the frozen contract (no corpus)."""
    import itertools

    c = KTCoder(sigma_size=20)
    # probabilities (seen values + escape) sum to 1 in any context
    c.update("ctx", "a")
    c.update("ctx", "a")
    c.update("ctx", "b")
    seen_mass = sum(c.prob("ctx", v)[0] for v in ("a", "b"))
    escape_mass = c.prob("ctx", "zzz")[0]
    assert abs(seen_mass + escape_mass - 1.0) < 1e-12, (seen_mass, escape_mass)
    # first value in a fresh context costs exactly its char code
    c2 = KTCoder(sigma_size=20)
    assert abs(c2.cost("fresh", "ab") - charcost("ab", 20)) < 1e-12
    # repeated seen value is cheap and monotonically not more than char cost
    c3 = KTCoder(sigma_size=20)
    b1 = c3.encode("k", "x")
    b2 = c3.encode("k", "x")
    assert b2 < b1
    # empty slot (∅ == "") is a normal value
    c4 = KTCoder(sigma_size=20)
    _ = c4.encode("k", "")
    assert c4.prob("k", "")[1] is True
    # determinism: same inputs -> same bits
    def run():
        cc = KTCoder(sigma_size=20)
        return [round(cc.encode(ctx, v), 9)
                for ctx, v in itertools.product(("p", "q"), ("a", "b", "a"))]
    assert run() == run()
    print("mdl.demo OK")


if __name__ == "__main__":
    demo()
