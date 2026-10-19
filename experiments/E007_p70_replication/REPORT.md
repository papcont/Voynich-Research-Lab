# E007 — REPORT (interpretation, written after results.json)

**Decision: REPRODUCED_BUT_NOT_VALIDATED.** R1 reproduces P70's published
structural values approximately; the R2 predictive gate passes Gates 1–4 and the
Currier part of Gate 5, but **fails Gate 5 in one major section (P)**, so
`STRUCTURAL_SUPPORT` is not reached. H009 is **not supported** under the frozen
rule.

Evidence classes: R1 `EXTERNAL_REPLICATION/REPRODUCTION`, R2
`EXTERNAL_MODEL_EVALUATION`, R3 `DEFERRED`. **Non-prospective:** P70 was built
on the whole manuscript; the folio split is only a common comparison surface.
Source ZL3b-n.txt, git-blob `2a4533ab…`. Plan `2f77096`, amendments `d42d9f0`
(001) and `db81687` (002, written before reveal). First reveal 2026-10-19,
A8 seed `20260907`, Python 3.13, numpy. Independent `validate.py` re-derives
every number with its own parser and coder: `E007_VALIDATION_PASS`.

Population: 33,611 running-text strict tokens, 206 folios, |Σ| = 25.

## R1 — reproduction (approximate, ZL3b vs published ZL_2b)

| quantity | ours | published | rule |
|---|---|---|---|
| non-degenerate parse rate | 99.6% | — | ≥ 85% ✔ |
| empty-core rate | 55.3% | 52.7% | [42.7, 62.7] ✔ |
| total chain-rule entropy | 10.11 bits | 10.311 | ±1.0 ✔ |
| H(P) / H(G\|P) / H(C\|P,G) / H(S\|P,G,C) | 2.79 / 1.37 / 3.29 / 2.66 | 2.788 / 1.374 / 3.622 / 2.527 | descriptive |

Lossless reconstruction is 100% and the chain-rule residual is 0 — both are
constructive and **not evidence**. Suffix inventory note: the verbatim
published family lists contain 34 non-empty suffixes (+∅), not the "33" in the
upstream prose; we used the lists as written.

## R2 — prequential description length (bits/token, lower is better)

| model | data bits/token | Δ vs P70 | total (+model) | cross-fitted fold wins of P70 |
|---|---|---|---|---|
| **P70** | **15.033** | — | 15.055 | — |
| A7 ch/sh not prefix | 15.214 | +0.181 | 15.236 | 5/5 |
| A5 no gallows | 15.245 | +0.212 | 15.267 | 5/5 |
| A6 no suffix | 15.520 | +0.487 | 15.526 | 5/5 |
| A2 rest+suffix | 15.664 | +0.630 | 15.680 | 5/5 |
| A8 matched random 4-slot | 15.956 | +0.922 | 15.957 | 5/5 |
| A1 prefix+rest | 15.997 | +0.963 | 15.999 | 5/5 |
| A3 fixed cuts | 16.065 | +1.031 | 16.065 | 5/5 |
| A0 whole token | 16.906 | +1.872 | 16.906 | (Gate 2) |

- Gate 1 (lossless ≥ 99%): pass. Gate 2 (beats A0 by ≥ 0.05): pass (1.87).
- Gate 3 (each competitor by ≥ 0.05 or ≥ 4/5 folds): pass for all seven.
- Gate 4 (total bits incl. inventory cost beats A0): pass. P70 core-escape
  share of data bits: 19.6%.
- Gate 5 Currier: P70 lowest in A (15.83) and B (14.61): pass.
- Gate 5 major sections {B,H,P,S} (recomputed by rule = expected set):
  P70 lowest in B, H, S; **in P (2,240 tokens, 16 folios) A6 = 16.996 < P70 =
  17.069** → fail.
- Development→holdout arm (reported, not gated): P70 lowest (14.42 vs next A7
  14.55, A0 16.11).
- Declared sensitivities (not gated): natural folio order leaves the ranking
  unchanged (P70 15.032); A7-literal 15.184, still 0.15 above P70.

## Exploratory, post-reveal (does NOT change the decision)

`exploratory.py` → `exploratory_post_reveal.json`, written **after** seeing the
section-P failure. Lexicographic order codes f99–f102 (section P) first, when
few counts exist and richer factorizations pay more for novelty. Under natural
folio order and under order-free cross-fitted per-token costs, P70 is lowest in
**all four** major sections, including P (P70 − best other = −0.13 and −0.10
bits/token). This suggests the frozen Gate-5 failure is an artefact of the
prequential order interacting with a small section, not a section where P70
is genuinely worse. Because it was found after the reveal on already-seen data,
it is `EXPLORATORY` and cannot be used to relabel E007.

## Interpretation (bounded)

- On ZL3b, an independent implementation of P70's published closed-inventory
  parser reproduces its headline structural values approximately.
- Under a codelength benchmark that is external to P70's own entropy profile and
  charges model cost, the P70 factorization compresses the running-text token
  stream better than every tested alternative segmentation, by 0.18–1.87
  bits/token, consistently across all five cross-fitted folds and both Currier
  languages. It beats a 4-slot random cut with P70's own slot-length profile by
  0.92 bits/token, so *which* characters go into which slot matters, not merely
  having four slots.
- Its two most debatable design choices both pay off in this benchmark:
  separating gallows (vs A5, +0.21) and treating `ch/sh` as prefixes (vs A7,
  +0.18).
- The frozen gate nevertheless fails on one section, so the preregistered
  outcome is **REPRODUCED_BUT_NOT_VALIDATED**, not `STRUCTURAL_SUPPORT`.

Not claimed: that the slots are morphemes, that P70 is the unique or best
possible factorization (only eight alternatives were tested; A4 deferred), any
language, notation or meaning. P70's advantage is partly fit: its inventories
were derived from this manuscript.

## Consequences for the programme

- H009 → `NOT_SUPPORTED_UNDER_FROZEN_GATE` (narrow miss; see exploratory note).
  H005 (compositional modules) gains a structural datapoint: a fixed four-slot
  factorization is a strong compression baseline.
- Any retest of the section criterion needs a new preregistration with an
  order-free subset metric; it would still be non-prospective on ZL3b.
  A genuinely new test needs an independent transcription (R3) or new data.
- E008 (mechanism tournament) should include P70 layer A as a structural
  baseline with this exact scorecard.
