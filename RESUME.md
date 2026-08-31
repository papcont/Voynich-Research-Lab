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

`E007_p70_replication` — **status PLAN_FROZEN** (see `experiments/E007_p70_replication/PLAN.md` + `experiment.json`).

Upstream `Voynichdecomp` audited @ `4f8a1117…`. Frozen design, three separated arms:
- **R1** (`EXTERNAL_REPLICATION`): reimplement the published closed-inventory longest-match parser (layer A: 8 prefixes, 9 gallows, 33 suffixes/7 families, core=residual, ch/sh as prefixes) and check approximate reproduction of P70 structural values on ZL3b. The 210-rule `p70_rules_canonical.json` (layer B) is **not** implemented; `enriched_records` is **never** gold/training.
- **R2** (`EXTERNAL_MODEL_EVALUATION`): primary = prequential KT description-length (bits/surface-token), identical estimator + char-escape for P70 and competitors A0–A8; gate = beat A0 and every non-deferred competitor by ≥0.05 bits/token (or lowest in ≥4/5 folds), not a complexity/fallback artefact, stable across Currier A/B. Outcomes: STRUCTURAL_SUPPORT / REPRODUCED_BUT_NOT_VALIDATED / REPRODUCTION_FAILURE / SPECIFICATION_AMBIGUITY.
- **R3** (`TRANSFER`): DEFERRED (needs a genuinely independent transcription with provenance/hash).

Honesty anchors: zero chain-rule residual is a mathematical identity, not evidence; P70 is **non-prospective** (built on the whole VMS), so the folio split is only a common comparison surface, never "validated holdout". No E007 target computed. Next action: implement `p70.py`/`run.py`/`validate.py`, write `results.json` before `REPORT.md`.

## Previously completed

- `E006_canonical_sequence_holdout` — INCONCLUSIVE_UNDERPOWERED (1 qualifying holdout chain < floor 3; H008 unresolved; no tuning of the revealed holdout).

## After E006

- E007 — independently reimplement and stress-test the P70 4-slot grammar.
- E008 — common-scorecard competition between language/cipher/generator/state-module models.
- E009 — independent blind implementation/test of the Deshuffling Matrix.
- E010 — stress-test external full-decode claims without treating their glosses as truth.
