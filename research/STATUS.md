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

**E010 complete.** epilectrik's boundary glyph coupling reproduces on our pipeline to within
0.002 bits (0.2548 all / 0.2134 definite vs 0.256 / 0.215) and their class table covers
71.3% of B tokens (published 69.5%). Under the E011 scorecard on Currier B their refinements
add nothing: glyph units vs EVA characters −0.0007, last two units +0.0012, and the 49-class
table costs 3.08 bits/token (class → class transitions add nothing). H016–H018 falsified
(development-stage). Upstream's measurement is solid; its grammar is not predictive.

**E011 complete (development-stage).** Prefix slot | previous final glyph: +0.088 bits/token
(CI 0.073–0.102; B +0.166 > A +0.035; permutation control removes it) → H014 SUPPORTED_DEV;
line position −0.026 → H015 FALSIFIED_DEV. Registered strongest structural null for the
running-text development pool: M_Sfam 13.813 / M_S 13.829 vs P70 13.967.

Earlier: E008 stage A ALL_COMPONENTS_NOT_INFORMATIVE (no-backoff scorecard; see REPORT);
E007 REPRODUCED_BUT_NOT_VALIDATED; E006 INCONCLUSIVE_UNDERPOWERED.

Next frontier: **E013** — the first Gate v2 lockbox claim: P70 four-slot structural model vs
the whole-token null on `LOCKBOX_NONRUNNING_V1` (labels/circular/radial, 710 tokens, 39
folios, INDEPENDENT; never coded by any experiment), margin calibrated on running text.
**E012** (reference-text signature comparison) still waits for the human corpus decision.

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
