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

**E011 complete (development-stage).** Under a backoff universal coder, conditioning the
P70 prefix slot on the previous token's final glyph lowers out-of-fold description length by
**0.088 bits/token** (folio-mean, CI 0.073–0.102; Currier A +0.035, B +0.166; feature-permuted
null −0.004; token-permutation control removes the gain) → **H014 SUPPORTED_DEV**. Line
position (prefix+suffix) raises it (−0.026, CI −0.042..−0.011) → **H015 FALSIFIED_DEV**.
All-slot conditioning (E008 shape) loses 0.69 even with backoff: slot targeting matters.
New strongest structural null for the running-text development pool: **M_Sfam 13.813 /
M_S 13.829** bits/token vs plain P70 13.967 (`research/gate/registered_nulls.json`).
No Gate v2 level is claimable (every ZL3b running-text folio has a SELECTION role).

Earlier: E008 stage A ALL_COMPONENTS_NOT_INFORMATIVE (no-backoff scorecard; see REPORT);
E007 REPRODUCED_BUT_NOT_VALIDATED; E006 INCONCLUSIVE_UNDERPOWERED.

Next frontier: **E010** (PLAN_FROZEN) — epilectrik's Currier-B claims as external structural
competitor: reproduce their boundary coupling, then test glyph-unit edge features and their
49-class table under the E011 scorecard (development-stage). **E012** (reference-text
signature comparison, stage B) is drafted and waits for the human corpus/licence decision.

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
