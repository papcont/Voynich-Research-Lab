# E012 (stage B-open) — reference-text signature comparison on open-rights corpora (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E012 metric has been computed.** Evidence class:
MECHANISM_DEMONSTRATION / DEVELOPMENT; no lockbox; no Gate level. Scope restriction: only
texts whose benchmark `rights_class` is `open` are used. The `linked_only` Borg material
(Latin recipes + real ciphertext) is **excluded until the human approves local analysis
use**; adding it later is a registered extension (E012-B), not a change to this plan.

## 1. Question

Does any natural-language text, scored with the **same code** as the manuscript, reproduce the
Voynich structural signature? And is the signature invariant under a monoalphabetic
substitution (the script-agnosticism sanity check that any cross-script comparison needs)?

## 2. Texts (local read-only clone of `matthewdgreen/cipher_benchmark`, pinned in
`external/repos.yml`; nothing copied into this repository; sha256 of concatenated files
recorded in `experiment.json`)

| id | text | tokens (raw) | units | lines |
|---|---|---|---|---|
| V | ZL3b running text | 33,611 | 206 folios | 4,075 manuscript lines |
| N_DEU | Copiale plaintext (18th-c. German), `open` | 13,712 | 101 pages | 1,823 manuscript lines |
| N_ITA | Gutenberg Italian sample (Manzoni, Collodi), `open` | 3,660 | 30 chunks | none (re-segmented, §3) |
| N_ENG | Gutenberg English sample (Austen, Dickens, Doyle), `open` | 3,660 | 30 | re-segmented |
| N_DE2 | Gutenberg German sample (Kafka, Mann), `open` | 3,660 | 30 | re-segmented |
| N_FRA | Gutenberg French sample (Hugo, Flaubert), `open` | 3,660 | 30 | re-segmented |
| C_SUB_DEU, C_SUB_ITA | monoalphabetic substitution of N_DEU / N_ITA (letter permutation, seed 20261081) | as source | as source | as source |
| G4 | E014 edge-coupled generator, seed 20261030 (from `runs/E014/`, regenerated if absent) | 33,611 | ZL3b | ZL3b |

## 3. Normalization, units, lines, size matching (frozen)

- **Normalization:** lowercase; within a token keep Unicode letters only (`str.isalpha`);
  drop empty tokens; all tokens certain (no uncertain placeholders exist in these texts).
  Copiale markers such as `*lip*` thus become `lip`; `eN` → `en`.
- **Units** ("folios"): Copiale page files; Gutenberg test files; ZL3b folios. Strata for the
  F-excess null = one stratum per text (language, "all"); ZL3b keeps its Currier × section
  strata as in E016.
- **Lines:** texts whose median tokens per line exceeds 20 are re-segmented: within each
  unit the token stream is cut into lines whose lengths are drawn from ZL3b's empirical
  running-text line-length distribution (population tokens per line), seed 20261080,
  last line shorter. Copiale and ZL3b keep their manuscript lines.
- **Size matching (primary comparison surface):** every text is truncated to its **first
  3,660 population tokens** in reading order (whole units kept up to the cut; the cut unit
  truncated); all components are computed on that prefix. The full-size values are the
  secondary surface (reported). Reason: TTR/H1 and cross-fit learning depend on N.

## 4. Signature-G (script-agnostic; frozen)

Slot base for **every** text, including Voynich: E007's fixed cuts **A3** — (first
character, middle, last character); tokens shorter than 3 → ("", token, ""). Components with
the frozen definitions of `voynichlab.signature` under this slot base:
Δ_S′ (first slot | previous token's last character / BOL / UNC; backoff coder; 5-fold
cross-fit by unit hash), Δ_L′ (first and last slots | line position), Δ_C (copy model,
W = 5), TTR, H1, F_excess (unit-stratified size-preserving permutation, 1,000, seed
20261050), dJ_order (unit-order permutation, 1,000, seed 20261060). Voynich's Signature-G
values are new (its P70-slot values are the known signature v3).

## 5. Decisions (frozen)

Distances to V per component with the E015 tolerances (bits 0.05 match / 0.10 mismatch;
fractions 0.02 / 0.05) → MATCH / PARTIAL / MISMATCH per text, on the size-matched surface.

- **H027** — "at least one natural-language text MATCHes Voynich on Signature-G":
  `SUPPORTED` iff any N_* text is MATCH; `FALSIFIED` iff every N_* text is MISMATCH; else
  `PARTIAL`.
- **H028** — "Signature-G is invariant under monoalphabetic substitution": `SUPPORTED` iff
  every component of C_SUB_X equals that of N_X to within 1e-9; else `FALSIFIED` (a pipeline
  defect, to be fixed before any reading).
- Family readout (ordinal, no decision): nearest text to V by the tolerance-normalised L1
  distance, with the caveat that two language families and no real cipher are covered.

Pre-result predictions: H027 FALSIFIED — natural prose is predicted to show Δ_S′ > 0
(cross-boundary letter phonotactics) but **Δ_C far above** Voynich's (function-word
repetition within five tokens) and TTR/H1 far below Voynich's at matched size; H028
SUPPORTED. G4 predicted PARTIAL on Signature-G as on signature v3. Voynich predicted to be
nearest to G4, not to any natural text.

## 6. Falsification, degrees of freedom, retraction

No free parameter (all seeds, rules and tolerances fixed; normalization fixed). H027
SUPPORTED would record that the structural inventory does not separate the manuscript
from natural prose (negative result for the discriminator). H028 FALSIFIED halts the
reading until the defect is fixed and the run repeated with an amendment.

## 7. Registration and claim ceiling

`experiment.json` records sha256 of the ZL3b file, each reference text's concatenated
plaintext, this file and the predictions. Claim ceiling: signature similarity between
texts; no decipherment, no language identification, no Gate level.
