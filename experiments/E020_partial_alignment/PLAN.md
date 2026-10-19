# E020 — partly word-aligned token boundaries on a verbose stream: calibration-then-prediction (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E020 metric has been computed.** Evidence class:
MECHANISM_DEMONSTRATION / DEVELOPMENT; no lockbox; no Gate level. Known inputs: E012's
Voynich Signature-G (Δ_S′ +0.178, Δ_L′ +0.061, Δ_C −0.283, TTR 0.393, H1 0.703, F 0.019,
dJ 0.015) and E019's transform values.

## 1. Question

E019 bracketed the manuscript's cross-boundary coupling between word-aligned boundaries
(≈ 0) and arbitrary cuts (+0.43–0.55). If a fraction *p* of token boundaries is word-aligned
and the rest arbitrary, on a verbose (two-symbols-per-letter) stream, does the *p* that
reproduces the coupling on one text also reproduce the other six components — and the
manuscript's **selectivity** (most of the coupling carried by one previous-character
class, E018) — on a second text?

## 2. Transform MIX(p) (frozen)

Source prepared as in E012 (normalization, units, lines). Verbose encoding as E019 C_VERB.
Within each line with *w* original words: keep each original word boundary with
probability *p*; then add boundaries at uniformly random symbol positions (not already
boundaries, not line edges) until the line has exactly *w* tokens again. Token count,
lines and units are therefore preserved; only boundary placement changes. Seeds:
calibration texts 20261100 + grid index; prediction text 20261120.

## 3. Calibration (development text = N_DEU / Copiale)

Grid *p* ∈ {0.0, 0.1, …, 1.0}; for each, MIX(p) on N_DEU, size-matched (first 3,660
tokens), Δ_S′ computed with Signature-G; **p\*** = the grid value minimising
|Δ_S′ − 0.178| (ties → larger p). Recorded before any prediction-text value is computed.

## 4. Predictions on the held text (N_ITA / Gutenberg Italian), frozen

With p\* fixed, MIX(p\*) on N_ITA, size-matched:

- **H030a** (transfer of the coupling): `SUPPORTED` iff |Δ_S′ − 0.178| ≤ 0.05;
  `FALSIFIED` iff > 0.10; else `PARTIAL`.
- **H030b** (the rest of the signature follows): count the components among {Δ_L′, Δ_C,
  TTR, H1, F_excess, dJ_order} within match tolerance of Voynich (bits 0.05; fractions
  0.02): `SUPPORTED` iff ≥ 4 of 6; `FALSIFIED` iff ≤ 1; else `PARTIAL`.
- **H030c** (selectivity): define `top1` = the share of the total out-of-fold edge gain
  (Σ over tokens of bits(M0) − bits(M_S′)) carried by the single most contributing
  previous-last-character class (BOL/UNC included). Compute for Voynich (size-matched) and
  for MIX(p\*)(N_ITA). `SUPPORTED` (selectivity reproduced) iff top1(MIX) ≥ top1(V) − 0.10;
  `FALSIFIED` iff top1(MIX) < top1(V) − 0.20; else `PARTIAL`.

Pre-result predictions: p\* ≈ 0.5–0.7. H030a SUPPORTED or PARTIAL (the coupling should
transfer across languages at matched size). H030b PARTIAL: Δ_L′ should transfer (edge
tokens stay word-aligned at line edges), TTR/H1 stay above Voynich (E019: 0.58/0.73),
Δ_C and F uncertain. **H030c FALSIFIED**: random partial cuts spread the coupling across the
bigram table; the manuscript concentrates it (E018: y/not-y = 72% of the P70-prefix gain).

## 5. Degrees of freedom, retraction

One calibrated parameter (p\*, 11-point grid, fitted on one component of one text). H030c
FALSIFIED means boundary randomisation alone cannot be the mechanism; a selective boundary
rule would be required. H030a FALSIFIED means the coupling level is language-specific.

## 6. Registration and claim ceiling

`experiment.json` records sha256 of inputs (E012 corpus hashes), config, predictions.
Claim ceiling: which boundary processes reproduce which structural components; no
decipherment, no language identification, no Gate level.
