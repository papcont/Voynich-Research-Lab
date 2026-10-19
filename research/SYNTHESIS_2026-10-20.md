# Synthesis — state of the programme after E006–E020 (2026-10-20)

Narrative layer only. Every number below is in an experiment's `results.json` with an
independent `validate.py`; hypotheses and their status are in `hypothesis-ledger.tsv`.
Evidence class of everything here: **development-stage structural findings** on ZL3b.
No Gate v2 level has been reached; no plaintext, language or meaning is claimed.

## 1. What the running text has been shown to be (structural inventory)

| # | component | key numbers | experiments |
|---|---|---|---|
| 1 | **Four-slot token form.** A fixed prefix · gallows · core · suffix factorisation (P70 layer A, reimplemented) describes tokens better than whole-token coding by 1.87 bits/token prequentially and beats every tested alternative segmentation (incl. a complexity-matched random cut, +0.92). On label text the suffix slot is dead weight (A6 better from scratch). | 15.03 vs 16.91 bits/token; 5/5 folds | E007, E013 |
| 2 | **Cross-boundary coupling, mostly one transition.** The previous token's final glyph predicts the next token's prefix (+0.088 bits/token folio-mean under a backoff coder; B +0.166, A +0.035). The binary feature "previous final is `y`" carries 72% of it; after a `y`-final token the next prefix is `qo` 6.1× as often in Biological B (40% vs 6.6%), 3.7× in other B, 2.2× in A. Epilectrik's independent measurement of the same coupling (0.215/0.256 bits) reproduces on our pipeline to 0.002. | E011, E018, E010 |
| 3 | **No local copying.** An exact/one-edit copy model of the previous five tokens adds nothing beyond folio vocabulary (real ≈ within-folio shuffle). Every self-citation generator tested — local, folio-wide, calibrated — leaves +1.6 to +2.9 bits/token of copy signal the manuscript lacks. | E008, E014, E015 |
| 4 | **Line homogeneity.** Conditioning the P70 prefix and suffix slots on line position costs bits (−0.026); the text is more line-homogeneous than any generator with a vocabulary-growth process (−0.16). Under character slots a positive line effect exists (+0.061) that natural manuscript lines (Copiale) lack. | E011, E015, E012 |
| 5 | **Folio-local vocabulary.** Folios reuse their own words beyond a Currier × section, size-preserving permutation: excess +0.035 (CI 0.027–0.044), in A and B. | E016 |
| 6 | **Weak codex-order locality.** Consecutive folios share vocabulary beyond order-permuted neighbours (+0.013, p < 0.001); the physical leaf adds nothing beyond adjacency. | E017 |

## 2. What has been excluded (as full accounts of the running text)

- **Simple non-semantic generators** (independent slots, token unigram, local and folio-wide
  self-citation, edge-coupled slot generators with and without a Pitman–Yor vocabulary
  process): every one mismatches the seven-component signature; edge-coupled generators
  overshoot the coupling (0.14–0.15 vs 0.088) and vocabulary processes fail folio-local
  reuse. (E014, E015)
- **Epilectrik's 49-class token grammar** as a predictive description: costs 3 bits/token;
  class → class transitions add nothing. Their *measurements* (coupling, coverage) stand.
  (E010)
- **Natural prose written one token per word**, at letter level: in German, English,
  French and Italian the last letter of a word and the first of the next are
  informationally decoupled (≈ 0); the manuscript's coupling is an order of magnitude
  larger. Vocabulary statistics do **not** separate the manuscript from prose at matched
  size. (E012)
- **Boundary-preserving encodings** (monoalphabetic, homophonic, verbose) never produce the
  coupling; **arbitrary cuts** through a letter stream produce 2.5× too much. (E019)

## 3. What partially works, and what it implies

A verbose letter stream in which **80% of word boundaries are kept and 20% are random**
reproduces the manuscript's coupling *level* in two languages with one calibrated
parameter (0.200 / 0.162 vs 0.178; E020). It does not reproduce line position, the low
copy signal or the vocabulary, and no boundary process yet reproduces the manuscript's
**selectivity** (one transition type dominating). The honest reading: the manuscript's
token boundaries behave like boundaries that are *mostly* but not entirely aligned with
some underlying unit, and the deviation is governed by a rule, not by chance. That rule —
whatever produces `…y → qo…` — is the most mechanism-laden unexplained fact in the
inventory.

## 4. Why no Gate v2 level has been reached (and cannot be, on ZL3b)

Gate v2 (A001) requires a confirmation lockbox the candidate's development never touched.
The holdout audit (errata 1–2) found that every ZL3b running-text folio carries a selection
role (E006/E007/E008 development folds, the E008 exploratory analysis), and label text sits
on the same folios. **ZL3b therefore contains no independent lockbox for any claim.** Our
own E013 claim (P70 on label text, +2.20 bits/token) was correctly refused at
registration. Everything above is development-stage by construction, not by weakness of
evidence.

## 5. The two decisions that unlock the next stage

1. **Confirmation surface.** Either (a) register data from outside ZL3b (a transliteration
   with independent readings — IT2a/GC were unreachable from this environment; or newly
   transcribed material), (b) amend A001 with an explicit `SEMI_INDEPENDENT` tier for
   candidates demonstrably not developed on the overlapping folios, or (c) accept that
   all ZL3b results remain development-stage. Without one of these, the programme can
   discriminate mechanisms but never *confirm* anything in Gate terms.
2. **Borg material (E012-B).** The pinned `cipher_benchmark` clone holds a 17th-century Latin
   pharmaceutical recipe text (27k tokens) and its real simple-substitution ciphertext with
   word boundaries — the closest subject-matter analogue available and the only real
   historical cipher with known plaintext in hand. Its `rights_class` is `linked_only`
   (third-party image rights; research plaintext). Approval is needed for *local analysis
   only*, never committed.

## 6. Recommended next steps (in order)

1. Decide 1 and 2.
2. E012-B: Borg plaintext and ciphertext under Signature-G; verbose/mixture transforms of
   Latin recipe prose (the text type matters: recipes are formulaic and repetitive).
3. E021: *selective* boundary rules on a verbose stream, scored with a transition-level
   selectivity measure at equal alphabet size (the E020 rule was confounded).
4. A corrected line-position component for re-segmented texts, so Δ_L′ can be compared
   fairly (today it is informative only where real lines exist).
5. If a confirmation surface is registered: re-run the strongest structural null
   (M_Sfam) and the E013-type transfer claim through the gate.

## 7. Methodological record

Three implementation or design errors were caught and recorded before interpretation (E008
canonical edit, E016 adjacency null, E020 selectivity rule); two registry errata reduced the
programme's own confirmation surface to zero; two sets of pre-result predictions were wrong
in detail (E012 Δ_C/TTR, E020 p\*/H030c) and are recorded as such. Nothing was retuned after
a reveal; every reveal has an independent validator that re-derives the numbers.
