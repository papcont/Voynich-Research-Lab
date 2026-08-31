# E006 — canonical final-chain holdout test

Status: DRAFT — AUDIT/FREEZE BEFORE TARGET REVEAL

## Question

Do a narrow set of attached/spaced final-chain variants behave like two surface realizations of the same structural unit sequence **in held-out context**, rather than merely looking similar?

## Candidate canonical grammar

Use only `src/voynichlab/canonical.py`.

Stems:
`ot`, `ok`, `qot`, `qok`

Finals:
`ar`, `al`, `aiin`, `am`, `or`, `ol`

A fused token is eligible only when the entire token parses exactly as STEM + one-or-more FINALS.
A spaced continuation is eligible only if the next token is exactly one listed FINAL and the separator is a certain `.` rather than uncertain `,`.

Do not add `edy/eedy` after viewing E006 targets.

## Development-known examples

These motivate the grammar but cannot validate it:
`otarar/otar.ar`, `otaral/otar.al`, `otaraiin/otar.aiin`, `otaram/otar.am`,
`okarar/okar.ar`, `okaral/okar.al`.

q-bearing forms are evaluated under the same grammar even where only one realization is seen.

## Required design decision before freeze

Choose a physical-folio holdout scheme without inspecting the primary metric.

Recommended option:
- deterministic 5-fold folio assignment from a stable hash;
- folds 0-3 for implementation/nuisance estimation;
- fold 4 as first primary confirmatory reveal.

A stricter preselected folio range is also defensible. Choose ONE before `PLAN.md` is committed.

## Primary metric concept

For each canonical chain, compare external context distributions for fused vs spaced realizations.
Consumed chain units are excluded from context.

Predeclare:
- immediate external neighbor;
- distant local context 2-10 tokens away, with exact line/paragraph boundary policy.

Primary statistic candidate:
weighted Jensen-Shannon divergence between fused/spaced context distributions, compared to matched random pseudo-pairings.

## Nulls

At minimum:
1. frequency + section/hand-stratified random surface pairing;
2. boundary-label permutation preserving folio/line and fused/spaced counts;
3. token-length-matched pseudo-canonicalization.

## Secondary diagnostics

- repeated canonical bigram/trigram types before/after;
- cross-folio recurrence;
- neighbor entropy;
- q vs non-q attachment rate (descriptive unless separately powered).

## Falsification

Weaken H007/H008 if:
- fused/spaced contexts are not closer than matched nulls;
- gain is only immediate/local and does not transfer across folios;
- effect vanishes under page/hand/section-aware uncertainty;
- one development-known family drives the result.

## Claim ceiling

A strong pass supports only:
"some visible token boundaries are compatible with variable attachment of a shared structural unit sequence."

It does not establish natural-language morphology, phonetics, semantics or plaintext.
