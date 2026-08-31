from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Iterator

HEADER_RE = re.compile(r"^<(?P<folio>f[^>]+)>\s+<!\s*(?P<meta>.*?)>")
TEXT_RE = re.compile(r"^<(?P<locus>f[^>,]+)(?P<rest>[^>]*)>\s+(?P<text>.*)$")
KV_RE = re.compile(r"\$(?P<key>[A-Z])=(?P<value>[^\s>]+)")
INLINE_COMMENT_RE = re.compile(r"<!.*?>")
ANGLE_GAP_RE = re.compile(r"<->|<~>")
PARA_MARK_RE = re.compile(r"<%>|<\$>")


@dataclass(frozen=True)
class FolioMeta:
    folio: str
    language: str | None = None
    hand: str | None = None
    currier_hand: str | None = None
    illustration: str | None = None


@dataclass(frozen=True)
class LineRecord:
    locus: str
    folio: str
    line_number: str | None
    raw_text: str
    meta: FolioMeta
    locator: str | None = None  # IVTFF locus locator after the comma, e.g. "@P0" (E007 running-text filter)


@dataclass(frozen=True)
class Token:
    value: str
    separator_before: str | None
    separator_after: str | None
    uncertain: bool


def _folio_from_locus(locus: str) -> str:
    return locus.split(".", 1)[0]


def parse_ivtff(path: str | Path) -> Iterator[LineRecord]:
    current: dict[str, FolioMeta] = {}
    active: FolioMeta | None = None
    with Path(path).open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            hm = HEADER_RE.match(line)
            if hm:
                kv = {m.group("key"): m.group("value") for m in KV_RE.finditer(hm.group("meta"))}
                active = FolioMeta(
                    folio=hm.group("folio"),
                    language=kv.get("L"),
                    hand=kv.get("H"),
                    currier_hand=kv.get("C"),
                    illustration=kv.get("I"),
                )
                current[active.folio] = active
                continue

            tm = TEXT_RE.match(line)
            if not tm:
                continue
            locus = tm.group("locus")
            folio = _folio_from_locus(locus)
            meta = current.get(folio, active or FolioMeta(folio=folio))
            line_number = locus.split(".", 1)[1] if "." in locus else None
            locator = tm.group("rest").lstrip(",") or None
            yield LineRecord(
                locus=locus,
                folio=folio,
                line_number=line_number,
                raw_text=tm.group("text"),
                meta=meta,
                locator=locator,
            )


def clean_text(text: str) -> str:
    text = INLINE_COMMENT_RE.sub("", text)
    text = ANGLE_GAP_RE.sub(".", text)
    text = PARA_MARK_RE.sub("", text)
    return text.strip()


def tokenize_surface(text: str) -> list[Token]:
    """Split on certain '.' and uncertain ',' separators without resolving EVA ambiguity."""
    text = clean_text(text)
    parts = re.split(r"([.,])", text)
    pending_sep: str | None = None
    out: list[Token] = []

    for part in parts:
        if part == "":
            continue
        if part in {".", ","}:
            pending_sep = part
            continue
        value = part.strip()
        if not value:
            continue
        sep_before = pending_sep if out else None
        if out:
            prev = out[-1]
            out[-1] = Token(prev.value, prev.separator_before, sep_before, prev.uncertain)
        uncertain = any(ch in value for ch in "[]{}?@'") or ":" in value
        out.append(Token(value, sep_before, None, uncertain))
        pending_sep = None
    return out


def iter_strict_tokens(lines: Iterable[LineRecord]) -> Iterator[tuple[LineRecord, int, Token]]:
    for line in lines:
        for i, token in enumerate(tokenize_surface(line.raw_text)):
            if not token.uncertain and token.value:
                yield line, i, token
