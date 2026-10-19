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


class BackoffKTCoder:
    """KT coder with one level of PPM-style backoff and exclusion (E011 §2, frozen).

    A slot value is coded in a *child* context (conditioned on a feature); if it is
    unseen there, the child's escape mass is spent and the value is coded in the
    *parent* context (unconditioned) with the child's seen values excluded; if it
    is unseen in the parent too, the parent's escape mass plus the char code pay
    for it. With child_key=None the coder is the plain KT + char escape of KTCoder.
    Seen mass + escape mass sum to one at every level, so the code is prefix-free.
    """

    def __init__(self, sigma_size: int):
        if sigma_size < 1:
            raise ValueError("sigma_size must be >= 1")
        self.sigma_size = sigma_size
        self._ctx: dict[object, dict] = {}

    def _get(self, key):
        st = self._ctx.get(key)
        return (st["n"], st["counts"]) if st else (0, {})

    def _state(self, key) -> dict:
        st = self._ctx.get(key)
        if st is None:
            st = {"n": 0, "counts": {}}
            self._ctx[key] = st
        return st

    def _parent_cost(self, parent_key, value, excluded) -> float:
        n0, cnt0 = self._get(parent_key)
        if excluded:
            n0 = sum(c for k, c in cnt0.items() if k not in excluded)
            m0 = sum(1 for k in cnt0 if k not in excluded)
        else:
            m0 = len(cnt0)
        denom = n0 + 0.5 * (m0 + 1)
        if value in cnt0 and value not in excluded:
            return -math.log2((cnt0[value] + 0.5) / denom)
        return -math.log2(0.5 / denom) + charcost(value, self.sigma_size)

    def cost(self, child_key, parent_key, value) -> float:
        """Codelength in bits WITHOUT updating state."""
        if child_key is None:
            return self._parent_cost(parent_key, value, ())
        n1, cnt1 = self._get(child_key)
        denom = n1 + 0.5 * (len(cnt1) + 1)
        if value in cnt1:
            return -math.log2((cnt1[value] + 0.5) / denom)
        return -math.log2(0.5 / denom) + self._parent_cost(parent_key, value, cnt1)

    def prob_mass(self, child_key, parent_key, candidates) -> float:
        """Total probability of `candidates` plus the residual escape (for tests)."""
        total = 0.0
        for v in candidates:
            total += 2.0 ** (-self.cost(child_key, parent_key, v))
        return total

    def update(self, child_key, parent_key, value) -> None:
        if child_key is not None:
            st = self._state(child_key)
            st["counts"][value] = st["counts"].get(value, 0) + 1
            st["n"] += 1
        st = self._state(parent_key)
        st["counts"][value] = st["counts"].get(value, 0) + 1
        st["n"] += 1

    def encode(self, child_key, parent_key, value) -> float:
        bits = self.cost(child_key, parent_key, value)
        self.update(child_key, parent_key, value)
        return bits
