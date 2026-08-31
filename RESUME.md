# RESUME — deterministic restart point

## Read order

1. `CLAUDE.md`
2. `RESEARCH_STATE.json`
3. `RESEARCH_PROTOCOL.md`
4. `research/STATUS.md`
5. `research/hypothesis-ledger.tsv`
6. active experiment plan

## Current accepted state

No plaintext decipherment is accepted.

Retained structural observations:

- Voynich tokens have highly constrained internal form.
- Currier A/B is statistically real but not identical to scribal hand.
- The same LFD hand can produce different Currier regimes.
- Previous token-final glyphs strongly predict next token-initial classes in some regimes, especially Biological-B `y -> qo`.
- Complete previous-token identity appears much less informative for the next initial than the edge class, so a short-memory boundary/state layer is plausible.
- Families such as `qokal/okal`, `qokar/okar`, `qokedy/okedy`, `qokeedy/okeedy` support compositional testing; semantics remain unknown.
- Short finals such as `ar`, `al`, `aiin`, `or`, `ol`, `am` occur both free and inside longer forms.
- Candidate attachment pairs include `otar.ar <-> otarar`, `otar.al <-> otaral`, `otar.aiin <-> otaraiin`, `otar.am <-> otaram`, `okar.ar <-> okarar`, `okar.al <-> okaral`.
- q-bearing families do not show identical attachment behavior; e.g. `qokar.ar` is observed while exact `qokarar` has not been located in the current ZL3b search. This is exploratory.
- Simple "remove q" normalization did not reveal normal repeated phrase structure.
- Simply merging highly predictable token boundaries did not create compelling repeated multi-token units.
- Section, hand, regime, locus and line effects must be separated before semantic claims.

## Last completed experiment

`E006_canonical_sequence_holdout` — **COMPLETED, INCONCLUSIVE_UNDERPOWERED** (first reveal 2026-08-31, seed 20260831).

On the frozen hash holdout (folds 3–4, 88 folios) only 1 k=2 canonical chain (`ok|al|or`) met the ≥2-fused-and-≥2-spaced threshold, below the preregistered power floor of 3. The frozen design computes no target JSD below that floor, so **H008 is unresolved** (neither supported nor falsified); N2 would also have been degenerate. See `experiments/E006_canonical_sequence_holdout/results.json` and `REPORT.md`. The revealed holdout must not be tuned (no widening grammar, no lowering thresholds); a powered retest needs a fresh preregistration.

## Active frontier

`E007_p70_replication` — **status READY_TO_FREEZE_PLAN**. Independently reimplement and stress-test the P70 4-slot grammar (`prefix·gallows·core·suffix`) against independent/held-out objectives; the upstream "zero entropy residual" is mathematically trivial for any lossless chain-rule decomposition and is not evidence. Audit its `PLAN_DRAFT.md` and freeze an executable plan before any target reveal — a new cycle, not an E006 reanalysis.

## After E006

- E007 — independently reimplement and stress-test the P70 4-slot grammar.
- E008 — common-scorecard competition between language/cipher/generator/state-module models.
- E009 — independent blind implementation/test of the Deshuffling Matrix.
- E010 — stress-test external full-decode claims without treating their glosses as truth.
