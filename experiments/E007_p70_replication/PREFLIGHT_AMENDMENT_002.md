# E007 — Preflight Amendment 002 (pre-reveal implementation clarifications)

- Amendment date (UTC): **2026-10-19**
- Pre-reveal HEAD at authoring: **269cc77**
- **No E007 target metric had been computed before this amendment.** Only the
  population facts already declared in Amendment 001 were re-checked (running-text
  strict tokens = 33,611 on 206 folios; Currier A 10,833 / B 22,255 / unknown 523;
  |Σ| = 25, Σ = `abcdefghijklmnopqrstuvxyz`). No codelength, entropy, parse rate,
  competitor score, fold score or subset score was computed.

Writing `run.py` exposed points where PLAN.md + Amendment 001 leave an
implementation detail open. Each is fixed here **before** reveal, by the most
literal reading of the frozen text; none changes a frozen scientific choice
(grammar, competitor set, metric, split, margins, labels, claim ceiling). Where a
second reading is defensible, it is computed as a **DESCRIPTIVE_SENSITIVITY**
only and never enters the gate.

## 1. Token order (PLAN §4.3)

"Folios sorted ascending by folio id" = Python `sorted()` on the folio id string
(lexicographic: `f100r < f100v < … < f1r …`), the same convention as E006.
Within a folio, tokens in file order (folios are contiguous in ZL3b).
Sensitivity (descriptive): primary bits/token under natural numeric folio order
(`f1r, f1v, f2r, …`, key = (leaf number, remaining suffix)).

## 2. KT context key (PLAN §4.3)

Context of slot *i* = `(i, (v_0, …, v_{i-1}))` — slot index plus the tuple of
preceding slot values of the same token. One `KTCoder` per model per run.

## 3. Competitor functions (PLAN §6), exact slot tuples

`parse_p70(t) = (p, g, c, s)` is the frozen layer-A parser.

| model | slots (coding order) | inventories it uses (for model_bits) |
|---|---|---|
| P70 | `(p, g, c, s)` | prefixes, gallows, suffixes |
| A0 | `(t,)` | none |
| A1 | `(p1, t[len(p1):])`, p1 = longest P70 prefix | prefixes |
| A2 | `(t[:len(t)-len(s2)], s2)`, s2 = longest P70 suffix at end of whole token | suffixes |
| A3 | `(t[0], t[1:-1], t[-1])`; len < 3 → `("", t, "")` (characters = EVA string characters) | none |
| A5 | `(p, g+c, s)` — P70 parse, then gallows folded into core | prefixes, gallows, suffixes |
| A6 | `(p, g, c+s)` — P70 parse, then suffix folded into core | prefixes, gallows |
| A7 | as P70, but a token beginning with `ch` or `sh` takes **no prefix** (so the leading `ch`/`sh` falls into core, as PLAN §6 states); otherwise prefixes `o, y, d, s, qo` | `o,y,d,s,qo` + blockers `ch,sh`, gallows, suffixes |
| A8 | four contiguous pieces per Amendment 001 §1 | none (seed + slot count only) |

"Folded into core" (A5/A6) means merging the P70 slot into the core *after* the
P70 parse, not re-parsing with a smaller inventory (that would also change which
suffix is found and so is not "P70 without gallows").

A7 reading: removing `ch,sh` from the prefix list alone would let `s` peel off
`sh…` (prefix `s`, core `h…`), contradicting PLAN §6 "such leading sequences fall
into core". The table follows the explicit PLAN text. Sensitivity (descriptive):
A7-literal (prefix list `o,y,d,s,qo`, no blocking).

## 4. A8 profile details (Amendment 001 §1)

`pool[L]` = list of P70 slot-length 4-tuples of **every development token
occurrence** of length L (empirical distribution, multiplicity kept), sorted
ascending. Global fallback fractions `f_x = Σ len(slot_x) / Σ L` over development
tokens; `round` = round-half-up (`floor(x + 0.5)`).

## 5. Subset and fold scores

- Currier / section scores (Gate 5) = the **global prequential** per-token costs
  (one run over all tokens) summed over the subset's tokens / subset N. "Lowest"
  = strictly lowest among P70 and the eight non-deferred competitors.
- Major sections are recomputed from the population by the frozen rule
  (tokens ≥ 2000 AND folios ≥ 8). If the result differs from {S,H,B,P}, the rule
  (not the listed set) governs and the discrepancy is reported.
- Cross-fitted folds (Amendment 001 §5): training counts are order-independent
  after all updates, so "prequential accumulation" = updating on every training
  token; held fold coded with frozen counts. Gate 3 compares P70 with A1–A8 only;
  A0 is Gate 2.
- Development/holdout arm (PLAN §7): prequential over development folios in the
  §1 order, freeze, code holdout without updates. **Reported, not gated.**

## 6. Gate 4 and label precedence

- Gate 4 = `total_bits_per_token(P70) < total_bits_per_token(A0)` (strict).
  Core-escape share = P70 data bits spent on escape events in the core slot
  (KT escape term + char code) / P70 total data bits; reported.
- Label precedence: R1 `REPRODUCTION_FAILURE` (Amendment 001 §3 rule) overrides
  the R2 labels, because R2 would then not be testing P70 as published; R2
  numbers are still reported. Otherwise `STRUCTURAL_SUPPORT` iff Gates 1–5 all
  hold, else `REPRODUCED_BUT_NOT_VALIDATED`. `SPECIFICATION_AMBIGUITY` applies
  only if the layer-A parser cannot be built deterministically (it can).

## 7. R1 diagnostics definitions

Plug-in (empirical) entropies in bits over the population: `H(P)`, `H(G|P)`,
`H(C|P,G)`, `H(S|P,G,C)`, their sum, and `H(W)` (residual = `H(W)` − sum, sanity).
Non-degenerate = at least one of p, g, s non-empty. Empty core = `c == ""`.
`MI(section, prefix)` and `MI(core, suffix)` plug-in, with Cramér's V
`sqrt(χ² / (n · (min(r, k) − 1)))`.

## 8. Software

Python 3.13, numpy only (no scipy). No randomness beyond the frozen A8 hash.
