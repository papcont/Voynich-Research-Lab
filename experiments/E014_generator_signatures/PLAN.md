# E014 — generator-family component signatures, corpus-free (E012 stage A) — FROZEN PLAN

Status: **PLAN_FROZEN** (2026-10-20). **No E014 metric has been computed.** Evidence class:
**MECHANISM_DEMONSTRATION / DEVELOPMENT** (no lockbox; the Voynich reference values are
re-measured here and are EXPLORATORY because their components were seen in E008/E011).

## 1. Question

Do simple non-semantic generators, built only from ZL3b running-text statistics and the
manuscript's own folio/line skeleton, reproduce the **component signature** measured for
Voynich: a positive prefix-slot gain from the previous token's final glyph (Δ_S), no gain
from local copy/modify at W = 5 (Δ_C), and a loss from line-position conditioning (Δ_L)?
If a shallow generator reproduces all three, the signature does not discriminate family G
from N/C and richer discriminators are needed; if none does, each mismatch names what a
generator must add.

## 2. Skeleton and population

ZL3b running text (blob `2a4533ab…`), the E007/E008 population and order. Every generated
text keeps the **same folios, lines, line lengths and positions of uncertain tokens**
(uncertain placeholders are never coded, exactly as in the real data); only the certain
tokens are replaced. Folds = `efold` of the folio (unchanged), so cross-fitting is identical.

## 3. Signature components (frozen definitions, computed by the same code for every text)

- **Δ_S** = folio-mean of `(bits(M0) − bits(M_S)) / n_f` — E011 models and `BackoffKTCoder`,
  5-fold cross-fit (prefix slot | previous token's final EVA character / BOL / UNC).
- **Δ_L** = folio-mean of `(bits(M0) − bits(M_L)) / n_f` — E011 M_L (prefix and suffix | line position).
- **Δ_C** = folio-mean of `(bits(B1) − bits(B1+C)) / n_f` — E008 definitions with plain KT
  (`src` slot `k:d` / `NONE`, W = 5 as selected in E008, canonical edit strings), 5-fold cross-fit.
Each with a folio-level percentile bootstrap CI (10,000, seed 20261019).

## 4. Generators (independent implementations; fixed before any signature is read)

All draw their statistics from the whole ZL3b running text (development data; there is no
lockbox). Seeds `20261030 + i`, i = 0..4 (five texts per generator).

- **G1 IND** — independent P70 slots: prefix, gallows, core, suffix each drawn from its
  empirical marginal; token = concatenation. No sequence structure at all.
- **G2 UNI** — tokens drawn independently from the empirical token unigram. No sequence
  structure; real tokens.
- **G3 SC** — self-citation (copy/modify, Timm–Schinner shape, independently written): at
  each position, with probability `p_copy` pick a source uniformly among the previous 20
  population tokens of the same folio (fresh draw if the window is empty); with probability
  `p_edit` apply one random edit (substitute / insert / delete, position uniform, inserted or
  substituted glyph drawn from the empirical glyph unigram), else copy exactly; with
  probability `1 − p_copy` draw a fresh token from the unigram. **Calibration (frozen rule):**
  grid `p_copy ∈ {0.5, 0.7, 0.9} × p_edit ∈ {0.3, 0.6, 0.9}`; choose the pair minimising
  `|TTR_gen − TTR_voy| + |hapax_gen − hapax_voy|` on the seed-0 text (type/token ratio and
  single-occurrence type share are not signature components). Recorded before the signature.
- **G4 EDGE** — edge-coupled slot generator: prefix drawn from the empirical
  `P(prefix | previous token's final character / BOL / UNC)`, then the token drawn from the
  empirical distribution of real tokens with that prefix. Builds in boundary coupling and
  line-initial structure, nothing else.

## 5. Decision per generator (frozen)

Let `d_X = |mean over seeds of Δ_X(gen) − Δ_X(Voynich)|` for X ∈ {S, L, C}.
- **SIGNATURE_MATCH** iff `d_S, d_L, d_C ≤ 0.05` bits/token;
- **SIGNATURE_MISMATCH** iff any `d_X > 0.10`;
- otherwise **PARTIAL**. Which components mismatch is reported.

Hypotheses: **H020** — the calibrated self-citation generator (G3) reproduces the signature.
**H021** — the edge-coupled slot generator (G4) reproduces the signature.

Pre-result predictions: G1, G2 MISMATCH (Δ_S ≈ 0 while Voynich ≈ +0.09). G3 MISMATCH on C
(copies within 5 tokens give Δ_C > 0 while Voynich has none) and on S. G4 MATCH or PARTIAL
(S built in; L likely similar because BOL conditioning carries line-initial structure; C ≈ 0).
If G4 MATCHes, the three-component signature is declared **non-diagnostic** between a
shallow edge-coupled generator and the real text (negative result for the discriminator,
recorded), and the E012 corpus stage must add discriminators (e.g. type inventory growth,
folio-level vocabulary sharing, order information beyond the edge).

## 6. Retraction / falsification

H020 FALSIFIED if G3 is MISMATCH; H021 FALSIFIED if G4 is MISMATCH. No post-hoc generator
tuning, grid change, window change or tolerance change. Any detail left open is settled by a
committed amendment before `run.py` computes a signature.

## 7. Degrees of freedom, confounds

Free: G3's two parameters (9-point grid, frozen matching rule, charged nothing because no
claim is made for G3). Confounds: generator texts inherit Currier/section labels from the
skeleton; Δ by Currier reported descriptively.

## 8. Registration and claim ceiling

`experiment.json` records sha256 of inputs, skeleton definition, config (this file) and
predictions (§5). Claim ceiling: statements about *which simple generators reproduce which
structural components*; nothing about meaning, language or authorship; no Gate level.
