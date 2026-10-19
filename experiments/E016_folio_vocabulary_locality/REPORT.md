# E016 — REPORT (interpretation, written after results.json)

**H024 SUPPORTED_DEV: folios reuse their own vocabulary beyond a stratified, size-preserving
permutation null (ΔF = +0.035, CI 0.027–0.044, p < 0.001, 142/196 folios, present in
Currier A and B). H025 FALSIFIED_DEV under the frozen rule — but the frozen null answers
a different question than adjacency; see §3.**

Plan `f7f1fc7`; one run; independent `validate.py` (own strata, permutations, statistics):
`E016_VALIDATION_PASS`. Development stage (all ZL3b running text; no lockbox); the raw
F = 0.242 was known from E015, the null-corrected excess was not.

## 1. Within-folio vocabulary reuse (H024)

| quantity | value |
|---|---|
| F observed (mean over 196 folios of 1 − types/tokens) | 0.2423 |
| F under N1 (tokens permuted within Currier × section strata, folio sizes kept) | 0.2071 (SD 0.0015) |
| F under N2 (unstratified permutation) | 0.1627 |
| **excess ΔF** (folio-mean, bootstrap CI) | **+0.0352 [0.0266, 0.0440]**, p < 0.001 |
| folios with positive excess | 142 / 196 |
| by Currier | A: F 0.204, excess +0.039 (114 folios); B: F 0.313, excess +0.031 (82) |

Reading: about 3.5 percentage points of each folio's repeated tokens are repeats of words
that are *specific to that folio* rather than to its section and language. Half of the raw
within-folio repetition (0.242) is explained by token frequencies and stratum vocabulary
(0.207 under N1; 0.163 without stratification), the rest is folio-local. The effect is not
a Currier-B artefact (A shows it slightly more strongly). Prediction (0.03–0.07, both
languages) met.

## 2. Codex-order adjacency (H025)

Frozen statistic: J_adj (mean Jaccard of consecutive folios, 204 pairs) = 0.1066; under the
N1 token-permutation null 0.1122 (97.5% quantile 0.1147) → no excess, p = 1.0 →
**FALSIFIED_DEV** by the preregistered rule. On the real text, however, adjacent
same-stratum pairs are more similar than non-adjacent same-stratum pairs (0.123 vs 0.091,
+0.032).

## 3. Design flaw, recorded

The N1 null permutes *tokens*, which also destroys the folio-specific vocabulary just
demonstrated in §1; under N1 every folio draws from the pooled stratum vocabulary and all
pairwise similarities rise. It therefore tests "is adjacent sharing above pooled-stratum
sharing", not "is adjacent sharing above non-adjacent sharing". The right null for codex
order permutes folio *order* with vocabularies intact. `exploratory.py` (post-run, not
gated) does that: J_adj 0.1066 vs order-permutation null 0.0964 within strata (97.5%
quantile 0.0991; p < 0.001) and 0.0702 globally. Codex-order locality is very likely real;
H025 nevertheless stays FALSIFIED_DEV as frozen, and a corrected test (H025b, order-
permutation null, bifolium partners vs facing pages when collation data are registered)
needs its own preregistration.

## 4. Consequences

- A fourth robust structural component: **folio-local vocabulary**. Together with the edge
  state (E011), the four-slot token form (E007), the absence of local copying (E008/E014)
  and the line-homogeneity (E011/E015), it is a constraint every mechanism proposal must
  meet, and the one that separated the manuscript from the vocabulary-growth generator in
  E015. It joins signature v2 with a proper null.
- For family readings: folio-local vocabulary is natural for texts whose pages are about
  different things (N, C) and for generators that re-use page-local material; it is not by
  itself diagnostic, but combined with *no local copying* it rules out the obvious page-
  local copy mechanism.
- Nothing here concerns meaning; nothing uses physical collation data.

Claim ceiling: development-stage structural statement; no Gate v2 level.
