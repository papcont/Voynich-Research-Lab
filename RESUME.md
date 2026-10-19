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

`E007_p70_replication` — **COMPLETED, REPRODUCED_BUT_NOT_VALIDATED** (first reveal 2026-10-19; plan `2f77096`, amendments `d42d9f0`, `db81687`).

R1: our independent P70 layer-A parser reproduces the published structural values approximately on ZL3b. R2: P70 has the lowest prequential KT bits/token (15.03) against A0, A1, A2, A3, A5, A6, A7, A8 (+0.18 to +1.87), wins 5/5 cross-fitted folds and both Currier languages, but the frozen Gate 5 fails in major section P (A6 lower), so H009 is not supported under the frozen gate. An exploratory post-reveal check (`exploratory_post_reveal.json`) indicates an order artefact; it must not be used to relabel E007. See `experiments/E007_p70_replication/REPORT.md`.

## Active frontier

`E008_mechanism_competition` — **status PLAN_FROZEN (stage A)**, see `experiments/E008_mechanism_competition/PLAN.md` + `experiment.json`. Question: do S (previous token's final glyph), L (line position) and C (exact/one-edit copy of a recent same-folio token, window W ∈ {5,10,20,40} chosen on development only) carry independent held-out predictive information beyond P70 slots? 16 models, KT scorecard inherited from E007, dev→holdout frozen counts on the E007 split, folio-level stability, Currier A/B, within-folio shuffle null N1 (seed 20261019). Hypotheses H011/H012/H013 with pre-result predictions in PLAN §8. Family readout (copy/modify vs sequential vs line-unit signature) is ordinal only. Stage B with reference corpora is deferred. Next action: implement `run.py`/`validate.py`, amend before first holdout coding if needed, write `results.json` before `REPORT.md`.

## External check (2026-10-19)

See `research/STATUS.md` § External landscape check and `external/repos.yml`.
Does not change E007 (frozen on its pin). **E009 provenance blocker:** the
Deshuffling-Matrix upstream is unreachable and no spec copy exists here; E009
must not be frozen without a human decision. New E008 candidates:
`epilectrik/voynich` Currier-B grammar, Naibbe cipher, arXiv:2609.20835.

## Previously completed

- `E007_p70_replication` — REPRODUCED_BUT_NOT_VALIDATED (Gate 5 section P miss; exploratory order artefact; non-prospective).
- `E006_canonical_sequence_holdout` — INCONCLUSIVE_UNDERPOWERED (1 qualifying holdout chain < floor 3; H008 unresolved; no tuning of the revealed holdout).

## Queue

- E008 — common-scorecard competition between language/cipher/generator/state-module models.
- E009 — independent blind implementation/test of the Deshuffling Matrix.
- E010 — stress-test external full-decode claims without treating their glosses as truth.
