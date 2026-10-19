"""Fixture tests for mdl.BackoffKTCoder (E011 §2). No corpus access."""
import math

from voynichlab.mdl import BackoffKTCoder, KTCoder, charcost


def _seen_plus_escape_mass(c, child, parent, values):
    """Mass of all values seen anywhere plus the mass of one novel string, excluding its char code."""
    mass = 0.0
    for v in values:
        mass += 2.0 ** (-c.cost(child, parent, v))
    # escape to a novel string: strip the char code to get the escape mass alone
    novel_bits = c.cost(child, parent, "zzz") - charcost("zzz", c.sigma_size)
    return mass + 2.0 ** (-novel_bits)


def test_plain_mode_equals_ktcoder():
    a, b = BackoffKTCoder(20), KTCoder(20)
    seq = ["x", "y", "x", "x", "z", "y"]
    ba = [a.encode(None, "p", v) for v in seq]
    bb = [b.encode("p", v) for v in seq]
    assert all(abs(u - w) < 1e-12 for u, w in zip(ba, bb))


def test_masses_sum_to_one_with_exclusion():
    c = BackoffKTCoder(20)
    for v in ("a", "a", "b", "c", "d", "d"):
        c.update(None, "p", v)          # parent only
    for v in ("a", "b", "b"):
        c.update("k", "p", v)           # child (and parent)
    mass = _seen_plus_escape_mass(c, "k", "p", ["a", "b", "c", "d"])
    assert abs(mass - 1.0) < 1e-12, mass


def test_unseen_child_context_costs_exactly_parent():
    c = BackoffKTCoder(20)
    for v in ("a", "b", "a"):
        c.update(None, "p", v)
    assert abs(c.cost("fresh", "p", "a") - c.cost(None, "p", "a")) < 1e-12
    assert abs(c.cost("fresh", "p", "q") - c.cost(None, "p", "q")) < 1e-12


def test_exclusion_makes_backoff_cheaper_than_naive_parent():
    c = BackoffKTCoder(20)
    for v in ("a", "a", "a", "b"):
        c.update(None, "p", v)
    c.update("k", "p", "a")
    # 'b' unseen in child: escape then parent with 'a' excluded -> cheaper than parent without exclusion
    assert c.cost("k", "p", "b") < -math.log2(0.5 / (1 + 0.5 * 2)) + c.cost(None, "p", "b")


def test_conditioning_helps_when_feature_is_informative():
    rng_seq = [("f0", "a")] * 30 + [("f1", "b")] * 30
    cond, plain = BackoffKTCoder(20), BackoffKTCoder(20)
    bc = sum(cond.encode(("c", f), "p", v) for f, v in rng_seq)
    bp = sum(plain.encode(None, "p", v) for f, v in rng_seq)
    assert bc < bp


def test_determinism_and_empty_value():
    def run():
        c = BackoffKTCoder(20)
        return [round(c.encode(k, "p", v), 10) for k, v in (("k", ""), (None, "a"), ("k", ""), ("j", "a"))]
    assert run() == run()
