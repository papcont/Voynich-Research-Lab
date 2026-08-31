from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

STEMS = ("qok", "qot", "ok", "ot")
FINALS = ("aiin", "ar", "al", "am", "or", "ol")


@dataclass(frozen=True)
class UnitChain:
    surface: tuple[str, ...]
    units: tuple[str, ...]
    boundary_pattern: tuple[str, ...]

    @property
    def canonical(self) -> str:
        return "|".join(self.units)


def parse_fused_token(token: str, stems: Sequence[str] = STEMS, finals: Sequence[str] = FINALS):
    """Conservative E006 parser: complete token must be STEM + one-or-more FINALS."""
    stem = next((s for s in sorted(stems, key=len, reverse=True) if token.startswith(s)), None)
    if stem is None:
        return None
    rem = token[len(stem):]
    if not rem:
        return None

    units = [stem]
    finals_sorted = sorted(finals, key=len, reverse=True)
    while rem:
        f = next((x for x in finals_sorted if rem.startswith(x)), None)
        if f is None:
            return None
        units.append(f)
        rem = rem[len(f):]
    return tuple(units) if len(units) >= 2 else None


def candidate_spaced_chain(tokens: Sequence[str], start: int):
    first = parse_fused_token(tokens[start])
    if first is None:
        return None
    units = list(first)
    surface = [tokens[start]]
    i = start + 1
    while i < len(tokens) and tokens[i] in FINALS:
        units.append(tokens[i])
        surface.append(tokens[i])
        i += 1
    return UnitChain(
        surface=tuple(surface),
        units=tuple(units),
        boundary_pattern=tuple(["FUSED"] * (len(first) - 1) + ["SPACE"] * (len(surface) - 1)),
    )
