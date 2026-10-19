"""Signature v3 — hypothesis-neutral structural signature of a line-structured token text.

Consolidates the components frozen in E008 (Δ_C), E011 (Δ_S, Δ_L), E014/E015 (TTR, H1),
E016 (folio-local reuse excess) and E017 (codex-order locality) into one module with
identical definitions, so that reference corpora and generators (E012) are scored by the
same code as the manuscript. Nothing here reads the corpus or decides anything.

Input format ("lines"): {folio: [(language, section, [[token, uncertain], ...]), ...]}
in the order the text is to be read; uncertain tokens are never coded (they only define
BOL/UNC features). Folds: sha256("E007:" + folio) % 5 (the E007 split).

Components (all frozen definitions, see the experiments' PLAN.md files):
  delta_S  folio-mean of (M0 − M_S) bits/token: P70 prefix slot | previous token's final
           EVA character (BOL/UNC), BackoffKTCoder, 5-fold cross-fit.
  delta_L  folio-mean of (M0 − M_L): prefix and suffix slots | line position.
  delta_C  folio-mean of (B1 − B1+C): plain-KT copy model, W = 5, src slot 'k:d' / NONE,
           canonical single edit (smallest position), base counts updated on every token.
  TTR, H1  types/tokens, single-occurrence types/types.
  F_excess mean over folios of (1 − types_f/tokens_f) minus its mean under a stratified
           (language × section, ≥3 folios, size-preserving) token permutation.
  dJ_order mean Jaccard of consecutive same-stratum folios (≥20 tokens) minus its mean under
           an order permutation within strata (vocabularies intact).
"""
from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict

import numpy as np

from .mdl import BackoffKTCoder, KTCoder
from .p70 import parse_p70

N_FOLDS = 5
W_COPY = 5
W_MAX = 40
MIN_TOK_J = 20


def efold(folio: str) -> int:
    return int(hashlib.sha256(("E007:" + folio.lower()).encode("utf-8")).hexdigest(), 16) % N_FOLDS


# --------------------------------------------------------------------------- #
# tokens with features
# --------------------------------------------------------------------------- #
def a3_slots(value: str) -> tuple:
    """E007 competitor A3: fixed cuts (first character, middle, last character); script-agnostic."""
    return (value[0], value[1:-1], value[-1]) if len(value) >= 3 else ("", value, "")


class Tok:
    __slots__ = ("value", "slots", "folio", "language", "section", "fold", "S", "L", "k_exact", "k_edit", "edit")

    def __init__(self, value, folio, language, section, S, L, slot_fn=parse_p70):
        self.value, self.slots, self.folio = value, slot_fn(value), folio
        self.language, self.section, self.fold = language, section, efold(folio)
        self.S, self.L = S, L
        self.k_exact = self.k_edit = self.edit = None


def _lev1(a: str, b: str) -> bool:
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    i, n = 0, min(len(a), len(b))
    while i < n and a[i] == b[i]:
        i += 1
    if len(a) == len(b):
        return a[i + 1:] == b[i + 1:]
    if len(a) + 1 == len(b):
        return a[i:] == b[i + 1:]
    return a[i + 1:] == b[i:]


def canonical_edit(src: str, t: str) -> str:
    if len(src) == len(t):
        i = next(i for i in range(len(t)) if src[i] != t[i])
        return f"s{i}{t[i]}"
    if len(t) == len(src) + 1:
        p = next(p for p in range(len(t)) if src[:p] + t[p] + src[p:] == t)
        return f"i{p}{t[p]}"
    p = next(p for p in range(len(src)) if src[:p] + src[p + 1:] == t)
    return f"d{p}"


def tokens(lines: dict, slot_fn=parse_p70, folio_order=None) -> list[Tok]:
    """Feature tokens in reading order (folios sorted lexicographically unless folio_order given)."""
    out = []
    for folio in (folio_order if folio_order is not None else sorted(lines)):
        window = []
        for lang, sec, full in lines[folio]:
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                t = Tok(v, folio, lang, sec, S, L, slot_fn)
                for k in range(1, min(W_MAX, len(window)) + 1):
                    w = window[-k]
                    if w == v:
                        t.k_exact = k
                        break
                    if t.k_edit is None and _lev1(w, v):
                        t.k_edit, t.edit = k, canonical_edit(w, v)
                out.append(t)
                window.append(v)
    return out


# --------------------------------------------------------------------------- #
# coders
# --------------------------------------------------------------------------- #
def _crossfit_backoff(toks, spec, sigma):
    """spec: {slot index: tuple of feature names in ('S','L')}. Out-of-fold bits per token."""
    def keys(t, i):
        parent = ("b", i, t.slots[:i])
        feats = spec.get(i)
        if not feats:
            return None, parent
        return ("c", i, t.slots[:i], tuple(getattr(t, f) for f in feats)), parent

    per = np.empty(len(toks))
    for j in range(N_FOLDS):
        coder = BackoffKTCoder(sigma)
        for t in toks:
            if t.fold != j:
                for i, v in enumerate(t.slots):
                    coder.update(*keys(t, i), v)
        for k, t in enumerate(toks):
            if t.fold == j:
                per[k] = sum(coder.cost(*keys(t, i), v) for i, v in enumerate(t.slots))
    return per


def _src(t):
    if t.k_exact is not None and t.k_exact <= W_COPY:
        return f"{t.k_exact}:0", 0
    if t.k_edit is not None and t.k_edit <= W_COPY:
        return f"{t.k_edit}:1", 1
    return "NONE", None


def _crossfit_copy(toks, sigma, with_copy):
    def code(coder, t, update):
        step = coder.encode if update else coder.cost
        bits = 0.0
        if with_copy:
            val, d = _src(t)
            bits += step(("src",), val)
            if d is not None:
                if d == 1:
                    bits += step(("edit",), t.edit)
                if update:
                    for i, v in enumerate(t.slots):
                        coder.update(("base", i, t.slots[:i], None, None), v)
                return bits
        for i, v in enumerate(t.slots):
            bits += step(("base", i, t.slots[:i], None, None), v)
        return bits

    per = np.empty(len(toks))
    for j in range(N_FOLDS):
        coder = KTCoder(sigma)
        for t in toks:
            if t.fold != j:
                code(coder, t, True)
        for k, t in enumerate(toks):
            if t.fold == j:
                per[k] = code(coder, t, False)
    return per


def folio_mean_delta(toks, per_base, per_model):
    bb, bm, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for t, x, y in zip(toks, per_base, per_model):
        bb[t.folio] += x; bm[t.folio] += y; n[t.folio] += 1
    return float(np.mean([(bb[f] - bm[f]) / n[f] for f in sorted(n)]))


# --------------------------------------------------------------------------- #
# vocabulary components
# --------------------------------------------------------------------------- #
def strata(lines: dict) -> dict:
    meta = {f: (lines[f][0][0], lines[f][0][1]) for f in lines if lines[f]}
    key = dict(meta)
    for _ in range(2):
        cnt = Counter(key.values())
        for f in key:
            if cnt[key[f]] < 3:
                key[f] = (meta[f][0], "rest") if key[f][1] != "rest" else ("rest", "rest")
    return key


def _per_folio_tokens(lines):
    return {f: [v for _l, _s, full in lines[f] for v, u in full if not u] for f in lines}


def _F(tk, folios):
    return np.array([1 - len(set(tk[f])) / len(tk[f]) for f in folios])


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def _permute_tokens(tk, groups, rng):
    out = {}
    for members in groups.values():
        pool = [v for f in members for v in tk[f]]
        perm = rng.permutation(len(pool))
        k = 0
        for f in members:
            n = len(tk[f])
            out[f] = [pool[perm[j]] for j in range(k, k + n)]
            k += n
    return out


def _J_adjacent(tk, order, skey):
    vals = [_jaccard(tk[order[i]], tk[order[i + 1]]) for i in range(len(order) - 1)
            if skey[order[i]] == skey[order[i + 1]] and len(tk[order[i]]) >= MIN_TOK_J and len(tk[order[i + 1]]) >= MIN_TOK_J]
    return float(np.mean(vals)) if vals else float("nan")


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def signature(lines: dict, n_perm: int = 1000, seed_F: int = 20261050, seed_J: int = 20261060,
              components=("delta_S", "delta_L", "delta_C", "TTR", "H1", "F_excess", "dJ_order"),
              slot_fn=parse_p70, folio_order=None) -> dict:
    """Compute the requested signature components for a line-structured text.

    slot_fn: token -> slot tuple (parse_p70 = signature v3; a3_slots = script-agnostic Signature-G).
    folio_order: explicit unit order (default: lexicographic) — used by texts whose units are not
    folio ids; the order also defines dJ_order adjacency and the cross-fit fold hash input.
    """
    out = {}
    toks = tokens(lines, slot_fn, folio_order)
    sigma = len({c for t in toks for c in t.value})
    out["n_tokens"], out["n_folios"], out["sigma_size"] = len(toks), len({t.folio for t in toks}), sigma
    if {"delta_S", "delta_L"} & set(components):
        p0 = _crossfit_backoff(toks, {}, sigma)
        if "delta_S" in components:
            out["delta_S"] = folio_mean_delta(toks, p0, _crossfit_backoff(toks, {0: ("S",)}, sigma))
        if "delta_L" in components:
            last = len(slot_fn("abcd")) - 1  # P70 -> suffix slot 3; A3 -> last-character slot 2
            out["delta_L"] = folio_mean_delta(toks, p0, _crossfit_backoff(toks, {0: ("L",), last: ("L",)}, sigma))
    if "delta_C" in components:
        out["delta_C"] = folio_mean_delta(toks, _crossfit_copy(toks, sigma, False), _crossfit_copy(toks, sigma, True))
    tk = _per_folio_tokens(lines)
    folios = [f for f in (folio_order if folio_order is not None else sorted(tk)) if tk.get(f)]
    all_tokens = [v for f in folios for v in tk[f]]
    c = Counter(all_tokens)
    if "TTR" in components:
        out["TTR"] = len(c) / len(all_tokens)
    if "H1" in components:
        out["H1"] = sum(1 for k in c if c[k] == 1) / len(c)
    skey = strata(lines)
    groups = defaultdict(list)
    for f in folios:
        groups[skey[f]].append(f)
    if "F_excess" in components:
        rng = np.random.default_rng(seed_F)
        F_obs = _F(tk, folios)
        F_null = np.mean([_F(_permute_tokens(tk, groups, rng), folios) for _ in range(n_perm)], axis=0)
        out["F"], out["F_excess"] = float(F_obs.mean()), float((F_obs - F_null).mean())
    if "dJ_order" in components:
        rng = np.random.default_rng(seed_J)
        J_obs = _J_adjacent(tk, folios, skey)
        pos = {g: [folios.index(f) for f in m] for g, m in groups.items()}
        null = []
        for _ in range(n_perm):
            order = list(folios)
            for g, m in groups.items():
                perm = rng.permutation(len(m))
                for p_, j in zip(pos[g], perm):
                    order[p_] = m[j]
            null.append(_J_adjacent(tk, order, skey))
        out["J_adj"], out["dJ_order"] = J_obs, float(J_obs - np.nanmean(null))
    return out
