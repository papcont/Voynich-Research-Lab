# E012 — mechanism-family signature comparison on reference texts (stage B of E008)
Status: DRAFT (nothing fetched, nothing computed)

## Question
Does the Voynich component signature measured in E008/E011 — a modest sequence-specific gain
from the previous token's final glyph on the next initial (≈ +0.09 to +0.11 bits/token, B > A),
no gain from local copy/modify at W ≤ 5 beyond folio vocabulary, and a loss from line-position
conditioning — look like (N) natural language, (C) a verbose cipher of natural language, or
(G) a non-semantic generator, when the **identical** scorecard is applied to reference texts?

## Design sketch (to be frozen)
- Scorecard: E011 backoff coder with slot-targeted conditioning; a text-agnostic 4-slot
  segmentation is needed for non-Voynich scripts → freeze a generic "P70-shaped" segmenter
  (longest-match prefix/suffix inventories learned on each reference text's development half
  by a fixed, hypothesis-neutral rule) so that each text gets its own slots; report also the
  whole-token base to avoid segmenter artefacts.
- Reference texts (provenance, hash and license fixed before freeze; fetched locally, never
  committed):
  - N1 medieval/classical Latin prose (e.g. PerseusDL canonical-latinLit, CC-BY-SA 4.0, via GitHub);
  - N2 a second language family text (e.g. Dante, Commedia; or Middle High German) — human to confirm;
  - C1 a verbose homophonic cipher of N1 (Naibbe-style reimplementation from the published
    description; the Cryptologia paper itself is not accessible from the research environment);
  - C2 a simple monoalphabetic substitution of N1 (control that preserves all sequence structure);
  - G1 a self-citation (copy/modify) generator seeded from a Voynich line (independent reimplementation);
  - G2 a slot-grammar random generator (P70 inventories, independent slots);
  - V the Voynich running text (E011 numbers, already known → EXPLORATORY for V).
- Line segmentation of reference texts to the Voynich line-length distribution (tokens per line
  sampled from ZL3b's empirical distribution, seed fixed) so S (BOL) and L are comparable.
- Signature per text: (Δ_S prefix-only, Δ_C at W=5, Δ_L, Currier-like split by halves).
- Pre-result predictions per family (ordinal): N and C2 show Δ_S > 0 with word-order dependence
  (control permutation kills it); C1 attenuates Δ_S by the homophone table; G1 shows large Δ_C;
  G2 shows Δ_S ≈ 0. The Voynich signature is then placed by nearest family under a frozen distance.

## Falsification
If every family reproduces the Voynich signature within the frozen tolerance, the signature is
non-diagnostic (negative result, recorded).

## Human decisions needed before freeze
Corpus choice and licenses; whether network access to GitHub-hosted corpora is acceptable; the
generator family set.

## Claim ceiling
Mechanism-family *signature similarity*; no decipherment, no language identification.
