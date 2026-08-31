"""IVTFF locus-type classification for the E007 running-text vs label filter.

Frozen by PREFLIGHT_AMENDMENT_001: a locus is RUNNING_TEXT iff its locus-type
letters (the locator with leading position characters and trailing digits
removed) begin with 'P' (paragraph). Everything else — labels (L*), circular
(C*), radial (R*), etc. — is excluded. Pure/deterministic; no corpus access.
"""
from __future__ import annotations

import re

# IVTFF position/annotation characters that may prefix a locus type code.
POSITION_CHARS = "@+*=&~/!"
_TRAILING_DIGITS = re.compile(r"[0-9]+$")


def locus_type(locator: str | None) -> str:
    """'@P0' -> 'P', '&Lz' -> 'Lz', '/L' -> 'L', '@Ri' -> 'Ri', None -> ''."""
    if not locator:
        return ""
    s = locator.lstrip(POSITION_CHARS)
    return _TRAILING_DIGITS.sub("", s)


def is_running_text(locator: str | None) -> bool:
    """Frozen E007 filter: running text = paragraph loci (type letter starts with 'P')."""
    return locus_type(locator).startswith("P")
