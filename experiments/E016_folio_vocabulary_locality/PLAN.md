# E016 — within-folio vocabulary locality (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E016 metric has been computed.** Evidence class:
DEVELOPMENT (population = all ZL3b running text; no lockbox exists; the raw F value 0.242
was seen in E015 as a descriptive statistic, so the *observed* F is EXPLORATORY-known; the
null-corrected excess, permutation p and CIs have never been computed).

## 1. Question

E015 found that a vocabulary-growth process with no folio structure reproduces the
manuscript's cross-folio sharing but not its within-folio repetition (F 0.168 vs 0.242).
Upstream (epilectrik) phrases the same thing as "folio units carrying their own vocabulary".
Is the excess real after controlling token frequencies, Currier language, section and folio
size? And is vocabulary local in codex order (adjacent folios more alike than same-stratum
folios)?

## 2. Population

ZL3b running text (blob `2a4533ab…`), strict tokens, E007 population and order; folio
metadata `$L` (A/B/None) and `$I` (section). Dependency unit = folio.

## 3. Statistics (frozen)

- **F_f** = `1 − types_f / tokens_f` per folio; **F** = mean over folios.
- **J_adj** = mean over consecutive folio pairs in frozen order (both with ≥ 20 tokens) of
  the Jaccard similarity of their type sets.
- **Strata** = (`$L`, `$I`); a stratum with < 3 folios is merged into (`$L`, "rest"); if that
  still has < 3 folios, into ("rest", "rest").
- **Null N1 (stratified folio permutation):** the population tokens of each stratum are
  pooled and dealt back to the stratum's folios preserving every folio's token count (folio
  order within a folio = dealt order). Preserves stratum vocabulary, token frequencies and
  folio sizes; destroys folio-specific vocabulary. 1,000 permutations, seed 20261050.
- **Null N2 (unstratified permutation):** the same across all folios (reported).
- **Excess:** `ΔF = F_obs − mean_N1(F)`; per-folio excess `ΔF_f = F_f − mean_N1(F_f)`, folio
  bootstrap CI (10,000, seed 20261019). Permutation p = `(1 + #{F_null ≥ F_obs}) / 1001`.
- **Adjacency:** `ΔJ = J_adj − mean over the N1 permutations of J_adj computed on the permuted
  texts` (same permutations), with permutation p, plus a second comparison against
  non-adjacent same-stratum pairs on the real text (reported).

## 4. Decisions (frozen)

- **H024** (folio-specific vocabulary): `SUPPORTED_DEV` iff ΔF ≥ **0.02** and folio-bootstrap
  CI lower > 0 and p ≤ 0.01; `FALSIFIED_DEV` iff CI upper < 0.02; else `INCONCLUSIVE_DEV`.
  Margin justification: a quarter of the generator gap seen in E015 (0.074); a smaller
  excess would be real but not useful as a discriminator.
- **H025** (codex-order locality): `SUPPORTED_DEV` iff ΔJ ≥ **0.01** and p ≤ 0.01 and the
  adjacent-vs-non-adjacent same-stratum comparison is positive; `FALSIFIED_DEV` iff the
  permutation 97.5% quantile of J_adj exceeds J_obs (no excess); else `INCONCLUSIVE_DEV`.

Pre-result predictions: H024 SUPPORTED_DEV with ΔF ≈ 0.03–0.07, present in both Currier A
and B (reported by language). H025 small or INCONCLUSIVE_DEV (upstream reports that facing
pages do *not* share vocabulary while bifolium partners do; consecutive folios in file order
mix both relations).

## 5. Confounds, degrees of freedom, retraction

Folio size and stratum are held fixed by N1; hand (`$H`) reported descriptively; token
length and line count per folio reported. No free parameter. H024 FALSIFIED_DEV retires
"folio-specific vocabulary" as a structural component in this programme; H025 is purely
descriptive of order and carries no mechanism claim.

## 6. Registration and claim ceiling

`experiment.json` records sha256 of inputs, config, predictions. Claim ceiling: a structural
statement about vocabulary distribution across folios; nothing about meaning, authorship,
or quire structure (no physical collation data used).
