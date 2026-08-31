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
(`READY_TO_FREEZE_PLAN`).
