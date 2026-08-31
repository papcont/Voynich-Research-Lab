"""P70 four-slot grammar — layer-A closed-inventory parser (E007, frozen).

Independent reimplementation of the published closed-inventory longest-match
parser (Voynichdecomp README). NOT the 210-rule section-weighted layer B, and
no use of enriched_records. Inventories verbatim from the published spec; ch/sh
are prefixes (P70's key decision). Empty slot = "" (logical ∅).

Precedence (frozen, PREFLIGHT_AMENDMENT_001 §9):
  surface -> longest PREFIX at start -> remove
          -> longest GALLOWS at new start -> remove
          -> longest SUFFIX at end of the remaining string -> remove
          -> remaining = CORE
Suffix matches only the remaining string, so it can never overlap prefix/gallows.
Tie-break: longest length, then frozen inventory declaration order.

This module is a pure parser (no scoring, no corpus). The benchmark lives in
the E007 run.py next cycle.
"""
from __future__ import annotations

# Non-empty inventory members (∅ = no-match). Declaration order is the frozen
# tie-break order; matching sorts by length desc then this order.
PREFIXES = ("o", "y", "d", "s", "ch", "sh", "qo")
GALLOWS = ("k", "t", "p", "f", "ckh", "cth", "cph", "cfh")
SUFFIXES = (
    # Y
    "y", "edy", "ey", "eey", "eedy", "dy", "ody", "chy", "shy",
    # N
    "aiin", "ain", "iin", "n", "aiiin", "iiin", "oiin", "oiiin",
    # L
    "ol", "al", "l",
    # R
    "ar", "or", "r", "ir",
    # M
    "am", "m",
    # OTHER
    "g", "he", "ee", "b", "ai", "a", "e", "s",
)

SUFFIX_FAMILY = {}
for _fam, _members in (
    ("Y", ("y", "edy", "ey", "eey", "eedy", "dy", "ody", "chy", "shy")),
    ("N", ("aiin", "ain", "iin", "n", "aiiin", "iiin", "oiin", "oiiin")),
    ("L", ("ol", "al", "l")),
    ("R", ("ar", "or", "r", "ir")),
    ("M", ("am", "m")),
    ("OTHER", ("g", "he", "ee", "b", "ai", "a", "e", "s")),
):
    for _s in _members:
        SUFFIX_FAMILY.setdefault(_s, _fam)


def _order_by_len_then_decl(inv):
    return sorted(enumerate(inv), key=lambda ix: (-len(ix[1]), ix[0]))


_PFX = [v for _, v in _order_by_len_then_decl(PREFIXES)]
_GAL = [v for _, v in _order_by_len_then_decl(GALLOWS)]
_SUF = [v for _, v in _order_by_len_then_decl(SUFFIXES)]


def _match_start(s, inventory):
    for v in inventory:
        if s.startswith(v):
            return v
    return ""


def _match_end(s, inventory):
    for v in inventory:
        if v and s.endswith(v) and len(v) <= len(s):
            return v
    return ""


def parse_p70(token: str) -> tuple[str, str, str, str]:
    """Return (prefix, gallows, core, suffix); "" is the empty (∅) slot.

    Lossless by construction: prefix + gallows + core + suffix == token.
    """
    rem = token
    pfx = _match_start(rem, _PFX)
    rem = rem[len(pfx):]
    gal = _match_start(rem, _GAL)
    rem = rem[len(gal):]
    suf = _match_end(rem, _SUF)
    core = rem[: len(rem) - len(suf)] if suf else rem
    return (pfx, gal, core, suf)


def is_degenerate(slots: tuple[str, str, str, str]) -> bool:
    """True when no affix matched (everything fell into core)."""
    p, g, c, s = slots
    return p == "" and g == "" and s == ""


def demo() -> None:
    """Runnable self-check of the frozen parse precedence (no corpus)."""
    assert parse_p70("qokeedy") == ("qo", "k", "", "eedy"), parse_p70("qokeedy")
    assert parse_p70("chol") == ("ch", "", "", "ol"), parse_p70("chol")
    assert parse_p70("shdy") == ("sh", "", "", "dy"), parse_p70("shdy")
    assert parse_p70("otaram") == ("o", "t", "ar", "am"), parse_p70("otaram")
    assert parse_p70("daiin") == ("d", "", "", "aiin"), parse_p70("daiin")
    # lossless reconstruction
    for t in ("qokeedy", "chol", "otaram", "daiin", "qokchey", "xyzzy", "ar"):
        p, g, c, s = parse_p70(t)
        assert p + g + c + s == t, (t, (p, g, c, s))
    # a token with no affix match is degenerate (whole token -> core)
    assert is_degenerate(parse_p70("xqz")) is True, parse_p70("xqz")
    # ch/sh are prefixes, not gallows
    assert parse_p70("chey")[0] == "ch"
    print("p70.demo OK")


if __name__ == "__main__":
    demo()
