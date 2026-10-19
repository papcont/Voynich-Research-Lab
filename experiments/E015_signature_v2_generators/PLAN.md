# E015 — signature v2 (inventory growth, vocabulary sharing) and stronger generators (E012 stage A2) — FROZEN PLAN

Status: **PLAN_FROZEN** (2026-10-20). **No E015 metric has been computed.** Evidence class:
MECHANISM_DEMONSTRATION / DEVELOPMENT; no lockbox; Voynich reference values EXPLORATORY
(components seen in E008/E011/E014, inventory statistics seen in E014).

## 1. Question

E014 showed that a shallow edge-coupled slot generator (G4) reproduces two of three
sequence components and overshoots the third, while its vocabulary statistics are far from
the manuscript's. Does a generator that adds a realistic **vocabulary-growth process** to
edge coupling (G5), or a **non-local self-citation** process (G6), reproduce an extended
signature that includes inventory growth and folio-level vocabulary sharing?

## 2. Skeleton, population, order

As E014 (ZL3b running-text skeleton; uncertain placeholders preserved; efold folds; E007
order). Five seeds per generator: `20261040 + i`.

## 3. Signature v2 (frozen definitions)

Sequence components exactly as E014: **Δ_S, Δ_L** (E011 backoff coder, 5-fold cross-fit,
folio-mean) and **Δ_C** (E008 plain-KT copy model, W = 5). New components, computed on the
population tokens of the whole text (identical N for every text):

- **TTR** = types / tokens.
- **H1** = single-occurrence types / types (hapax share).
- **F** (within-folio repetition) = mean over folios of `1 − types_f / tokens_f`.
- **X** (cross-folio sharing) = mean over folios of the share of the folio's types that
  occur in at least one other folio.

Tolerances: bit components 0.05 (match) / 0.10 (mismatch); fraction components 0.02 (match)
/ 0.05 (mismatch). Per generator: **MATCH** iff every component is within its match
tolerance of the Voynich value (mean over seeds); **MISMATCH** iff any component exceeds
its mismatch tolerance; else **PARTIAL**. The mismatching components are listed.

## 4. Generators (independent implementations; frozen before any signature is read)

- **G4 EDGE** — E014 definition, re-run as the reference (prediction: MISMATCH on TTR/H1).
- **G5 EDGE+PY** — edge-coupled prefix (`P(prefix | previous final / BOL / UNC)` from ZL3b)
  and, per prefix, a **Pitman–Yor** token process with discount `d` and concentration `θ`:
  with probability `(θ + d·K_p) / (n_p + θ)` a *new* type is created (drawn from the
  empirical P70 slot marginals of gallows/core/suffix given that prefix, rejection-sampled
  until unseen in that prefix's restaurant, at most 50 tries then any draw), otherwise an
  existing type is chosen with probability ∝ `(count − d)`. `K_p`, `n_p` = types/tokens so
  far under prefix p (whole text, folios in frozen order). **Calibration (frozen rule):**
  grid `d ∈ {0.5, 0.7, 0.9} × θ ∈ {10, 100, 1000}`; choose the pair minimising
  `|TTR − TTR_voy| + |H1 − H1_voy|` on the seed-0 text (these two are signature components,
  so G5's TTR/H1 match is *by construction* and is reported as such; the test is whether
  the other five components follow).
- **G6 FOLIO-SC** — self-citation with a **folio-wide horizon**: with probability `p_copy`
  the source is drawn uniformly from *all* previous population tokens of the same folio;
  edit step and fresh draws as E014 G3; grid `p_copy ∈ {0.5, 0.7, 0.9} × p_edit ∈ {0.3,
  0.6, 0.9}` calibrated on `|TTR diff| + |H1 diff|` (seed 0) — same rule as E014, so
  TTR/H1 are again partly by construction.

Hypotheses: **H022** — G5 reproduces signature v2. **H023** — G6 reproduces signature v2.

Pre-result predictions: G4 MISMATCH (TTR/H1 gaps > 0.05). G5 PARTIAL: TTR/H1 by
construction, Δ_L and Δ_C match, **Δ_S overshoots** as in G4 (≈ 0.14 vs 0.088), F/X
uncertain. G6 MISMATCH: Δ_S ≈ 0 (no edge coupling) and Δ_C > 0 (copies still land within
5 tokens often enough), F too high.

## 5. Falsification / retraction

H022 FALSIFIED iff G5 MISMATCH; H023 FALSIFIED iff G6 MISMATCH. No post-hoc grid,
tolerance, horizon or component changes. Open details are settled by a committed amendment
before `run.py` computes a signature.

## 6. Degrees of freedom, confounds

Free: G5's (d, θ) and G6's (p_copy, p_edit), each a 9-point grid with a frozen matching rule
on TTR/H1 (reported as by-construction matches). Currier split reported descriptively.

## 7. Registration and claim ceiling

`experiment.json` records sha256 of inputs, skeleton definition, config, predictions.
Claim ceiling: which generators reproduce which structural components; nothing about
meaning, language or authorship; no Gate v2 level.
