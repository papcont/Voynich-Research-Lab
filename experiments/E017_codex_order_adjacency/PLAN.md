# E017 — codex-order vocabulary adjacency with an order-permutation null (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E017 metric has been computed.** Evidence class:
DEVELOPMENT. The overall adjacency excess is **EXPLORATORY-known** from E016's post-run check
(J_adj 0.1066 vs order-null 0.0964); the leaf-type split (§3, H026) and all Currier-split
results have never been computed. No physical collation data are used (none registered).

## 1. Question

E016 showed folio-local vocabulary (H024) and, in an unregistered check, that consecutive
folios in ZL3b file order are more alike than order-permuted folios. Registered here: (a) is
that adjacency excess real under a null that keeps every folio's vocabulary intact and
permutes only the order within Currier × section strata; (b) do the two sides of the same
physical leaf (recto → verso) share more vocabulary than facing pages (verso → next recto)?

## 2. Population and statistics

ZL3b running text, strict tokens, E007 population; folios with ≥ 20 tokens enter pairs.
Strata as E016 (Currier × section; < 3 folios merged). Jaccard of folio type sets.

- **Adjacent pairs** = consecutive folios in frozen (lexicographic) order — the same order
  used in E016 — restricted to pairs in the **same stratum** (so language/section changes
  do not enter).
- **Pair types** from folio names `f<number><side><panel?>`: **same-leaf** = same number
  (r → v, or panels of one side); **facing** = number differs by exactly 1 and the first is
  verso, the second recto; **other** = remaining adjacent pairs (gaps, non-consecutive
  numbering). Reported counts.
- **J_adj** = mean Jaccard over adjacent same-stratum pairs; **J_leaf**, **J_facing**.

## 3. Nulls and decisions (frozen)

- **Order-permutation null:** within each stratum, permute the folio order (vocabularies
  intact), recompute J_adj over the pairs that are adjacent *and same-stratum in the
  permuted order*. 1,000 permutations, seed 20261060. `ΔJ = J_adj − mean_null`,
  `p = (1 + #{null ≥ obs}) / 1001`.
- **H025b** (codex-order locality): `SUPPORTED_DEV` iff ΔJ ≥ 0.01 **and** p ≤ 0.01 **and**
  ΔJ > 0 within Currier A pairs and within Currier B pairs separately; `FALSIFIED_DEV` iff
  the null's 97.5% quantile ≥ J_adj; else `INCONCLUSIVE_DEV`.
- **Pair-type null:** among the real adjacent same-stratum pairs, permute the type labels
  (same-leaf / facing / other), 1,000 times (seed 20261061); statistic `D = J_leaf − J_facing`.
- **H026** (same leaf > facing pages): `SUPPORTED_DEV` iff D ≥ 0.01 and p ≤ 0.01;
  `FALSIFIED_DEV` iff the null's 97.5% quantile ≥ D (no excess) **or** D < 0; else
  `INCONCLUSIVE_DEV`.

Pre-result predictions: H025b SUPPORTED_DEV (ΔJ ≈ 0.01, both languages). H026 SUPPORTED_DEV
with moderate confidence (text continuing over a leaf should share more than facing pages
of different leaves; upstream reports facing pages share little).

## 4. Confounds, degrees of freedom, retraction

Dependency across pairs (a folio appears in two pairs) is handled by permutation, not by
pair-level CIs; folio sizes are unchanged by order permutation. No free parameter. Section
boundaries never cross a pair. H025b FALSIFIED_DEV retires codex-order locality; H026
FALSIFIED_DEV means leaf structure does not organise vocabulary beyond adjacency.

## 5. Registration and claim ceiling

`experiment.json` records sha256 of inputs, config, predictions. Claim ceiling: structural
statement about the distribution of vocabulary along the current folio order; no claim about
original quire order, binding, or meaning.
