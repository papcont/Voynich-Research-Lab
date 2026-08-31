import math

from voynichlab.mdl import KTCoder, charcost


def test_demo_contract():
    from voynichlab.mdl import demo
    demo()  # asserts internally


def test_probabilities_sum_to_one():
    c = KTCoder(sigma_size=15)
    for v in ("a", "a", "b", "c", "a"):
        c.update("ctx", v)
    seen = sum(c.prob("ctx", v)[0] for v in ("a", "b", "c"))
    escape = c.prob("ctx", "novel")[0]
    assert abs(seen + escape - 1.0) < 1e-12


def test_first_unseen_costs_charcost():
    c = KTCoder(sigma_size=15)
    assert abs(c.cost("k", "abc") - charcost("abc", 15)) < 1e-12
    assert not c.prob("k", "abc")[1]  # unseen before update


def test_repeated_seen_is_cheaper():
    c = KTCoder(sigma_size=15)
    b1 = c.encode("k", "x")
    b2 = c.encode("k", "x")
    assert b2 < b1
    assert c.prob("k", "x")[1]  # now seen


def test_empty_slot_value_and_eos():
    c = KTCoder(sigma_size=15)
    # empty slot "" costs one EOS unit on first sight
    assert abs(c.cost("k", "") - math.log2(16)) < 1e-12
    c.update("k", "")
    assert c.prob("k", "")[1]


def test_determinism_same_input_same_bits():
    def run():
        cc = KTCoder(sigma_size=15)
        return [round(cc.encode(ctx, v), 9)
                for ctx in ("p", "q") for v in ("a", "b", "a", "")]
    assert run() == run()


def test_context_separation():
    c = KTCoder(sigma_size=15)
    c.encode("ctx1", "a")
    # "a" is novel in ctx2 even though seen in ctx1
    assert not c.prob("ctx2", "a")[1]
