# Current research status

## Claim ceiling

**Structural analysis only. No accepted plaintext, language identification, phonetic key or semantic lexicon.**

## Token-edge state

The most important edge phenomenon is a short-memory relationship between the end of one visible token and the beginning of the next. `y -> qo` is a major candidate. This does not imply that `q` means a specific article, preposition or sound.

## Compositional/token grammar

Repeated families support structural decomposition tests:

- `qokal / okal`
- `qokar / okar`
- `qokey / okey`
- `qokedy / okedy`
- `qokeedy / okeedy`

Right-side families include `ar/al/aiin/or/ol/am` and B-heavy `dy/edy/eedy`. These are structural candidates, not translated morphemes.

## Regime, hand and section

Currier A/B differences are not reducible to different people writing differently, but hand/section/regime remain confounded enough to require joint controls.

## Variable attachment

Candidate pairs already discovered in ZL3b:

- `otar.ar` and `otarar`
- `otar.al` and `otaral`
- `otar.aiin` and `otaraiin`
- `otar.am` and `otaram`
- `okar.ar` and `okarar`
- `okar.al` and `okaral`

The stronger claim — same underlying unit sequence — has **not passed a context-based holdout test**.

## Weak/rejected simple models

- deterministic A `y` <-> B `dy`: rejected;
- q as universal prose-only marker: rejected;
- q as mandatory line-start marker: rejected;
- delete q and reveal ordinary phrases: not supported;
- merge all predictable token boundaries into larger words: not supported.

## Current frontier

E006 is **complete with an INCONCLUSIVE_UNDERPOWERED result** (first reveal
2026-08-31, seed 20260831, `results.json` + independent `validate.py`). On the
frozen hash holdout (folds 3–4, 88 folios) only **1** k=2 canonical chain
(`ok|al|or`) had ≥2 fused AND ≥2 spaced occurrences, below the preregistered
power floor of 3; the frozen design therefore computes no target JSD and H008
stays **unresolved** (neither supported nor falsified). N2 would also have been
degenerate (fused/spaced of the same chain never share a folio). The narrow k=2
same-chain co-occurrence is simply too rare in ZL3b to power this test. No
grammar/threshold tuning is permitted on this revealed holdout; a powered
retest would require a separate preregistration.

Next frontier: **E007** — independent P70 4-slot grammar replication
(**PLAN_FROZEN**). Upstream `Voynichdecomp` audited at the pinned commit: the
published spec is dual-layer — a compact closed-inventory longest-match parser
(reconstructible; we reimplement it) plus a 210-rule section-weighted
`p70_rules_canonical.json` (not reconstructible; not implemented, optional fixed
input only). Their validator targets P70's own entropy profile (10.311 bits) and
zero residual is a chain-rule identity — both rejected as evidence. P70 used
ZL_ivtff_2b, we use ZL3b, so reproduction is approximate. Primary benchmark is a
prequential KT description-length (bits/surface-token) with an identical
estimator + char-escape for P70 and competitors A0–A8; the folio split is only a
common comparison surface (P70 is **non-prospective** — built on the whole VMS).
No E007 metric is computed yet. R3 (independent transcription) is DEFERRED.

## External landscape check (2026-10-19)

Landing pages and commit lists only; nothing audited or accepted. Details and
observed upstream heads in `external/repos.yml`.

- **Voynichdecomp** (E007 upstream) moved past our pin to `b4f4995` (Super
  Grammar v03, bifolium/ordering tests, PREREG 1–38, retractions R1–R6). E007
  stays frozen on `4f8a1117…`; testing Super Grammar would need a separate
  preregistration.
- **Voynich-Deshuffling-Matrix** (E009 upstream) is **unreachable** (404 /
  auth). No local spec copy → E009 needs a human provenance decision before
  freeze.
- **New structural competitor:** `epilectrik/voynich` reports a single Currier-B
  token grammar (49 classes, 69.5% coverage, line-position zones, boundary
  coupling) after a 2026-09-27 self-review that retracted several earlier
  claims. Overlaps H002/H003/H005; candidate for E008 after independent
  reimplementation.
- **New generator/cipher baselines for E008:** Naibbe cipher (Greshko,
  Cryptologia 2025; no code located) and arXiv:2609.20835 (pastiche /
  generative-grammar hypothesis; not inspected).
- No external work reports an accepted decipherment.
