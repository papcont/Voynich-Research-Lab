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

**E007 complete — REPRODUCED_BUT_NOT_VALIDATED** (first reveal 2026-10-19;
`results.json` + independent `validate.py` pass; amendment 002 committed before
reveal). Independent P70 layer-A parser on ZL3b (33,611 running-text strict
tokens): R1 reproduces published values approximately (empty core 55.3% vs
52.7%; total chain-rule entropy 10.11 vs 10.311 bits). R2 prequential KT
bits/token: P70 15.03, best alternatives A7 (ch/sh not prefix) 15.21 and A5 (no
gallows) 15.25, matched random 4-slot A8 15.96, whole token A0 16.91; P70 wins
5/5 cross-fitted folds against every competitor and is lowest in Currier A and
B. The frozen gate fails only in major section P (A6 16.996 < P70 17.069), so
H009 is **not supported under the frozen gate**. Exploratory post-reveal check:
under natural folio order and order-free cross-fitted costs P70 is lowest in all
major sections — the miss looks like a prequential-order artefact, but cannot
relabel E007. Non-prospective (P70 built on the whole VMS). Structural only.

Previous: E006 INCONCLUSIVE_UNDERPOWERED (H008 unresolved; no tuning).

**E008 stage A complete — ALL_COMPONENTS_NOT_INFORMATIVE** (first reveal
2026-10-19; `validate.py` pass). On the frozen no-backoff KT scorecard, adding
edge state S, line position L or local copy/modify C to the P70 base *costs*
1.95 / 0.36 / 0.25 bits/token on the holdout (B1 = 14.42). S and L still beat
the within-folio shuffle by 0.89 / 0.33 (information exists, fragmentation
dominates); C equals the shuffle (no locality-specific copying at W ≤ 5).
H011–H013 falsified as predictive components under this scorecard; H003 (prefix
given previous final) is untested by E008. Lesson: codelength tests of
conditioning hypotheses need a backoff coder and slot-targeted conditioning
(E011 draft).

Next frontier: Gate v2 protocol amendment (human-approved 2026-10-19), then
freeze E011.

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
