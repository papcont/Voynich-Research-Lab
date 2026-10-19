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

`E011_targeted_context_scorecard` — **COMPLETED (development-stage): H014 SUPPORTED_DEV, H015 FALSIFIED_DEV** (plan `24dc8c7`; validator pass; Gate v2 claim record correctly refused — development pool). Prefix slot | previous final glyph: +0.088 bits/token folio-mean (CI 0.073–0.102; B +0.166 > A +0.035; null −0.004; permutation control kills it). Line position (prefix+suffix): −0.026 (CI upper < margin). M_Sall (all slots) −0.69. New strongest structural null M_Sfam (13.813) / M_S (13.829) vs P70 plain 13.967, registered in `research/gate/registered_nulls.json`. Exploratory: 28% of the S gain is line-initial, 22% y → (qo). See `REPORT.md`.

## Active frontier

`E010_external_claim_stress_tests` — **PLAN_FROZEN** (`experiments/E010_external_claim_stress_tests/PLAN.md`). Upstream `epilectrik/voynich` @ `ff399c44` (read-only clone in git-ignored `.external/`, nothing copied). R1: reproduce their ZL3b boundary glyph coupling (0.215 definite / 0.256 all; their regex and shuffle-corrected MI) on our pipeline, ±0.03. R2 (Currier B, E011 scorecard, development-stage): H016 glyph-unit vs EVA-character edge feature; H017 last two units ("word-ending routing"); H018 their 49-class table (fixed external input, sha256 `338892c0…`) as class | previous class vs M_Sfam. Pre-result predictions and retraction conditions in PLAN §2/§4. Next action: implement run.py/validate.py; results before report.

`E012_reference_signature` (stage B) remains a DRAFT **pending your decision** on corpora/licences, network use and the generator/cipher set.

Gate v2 is in force (`research/protocol_amendments/A001_GATE_V2.md`, `research/gate/gate_v2.json`, `src/voynichlab/gate.py`, `tests/test_gate.py`, `scripts/gate_report.py`, `research/holdout_registry.json`). Confirmation surfaces: `LOCKBOX_NONRUNNING_V1` (710 label/circular/radial tokens, INDEPENDENT) only; running-text confirmation needs data registered from outside ZL3b. IT2a/GC hashes unregistered (voynich.nu unreachable 2026-10-19).

## External check (2026-10-19)

See `research/STATUS.md` § External landscape check and `external/repos.yml`.
Does not change E007 (frozen on its pin). **E009 provenance blocker:** the
Deshuffling-Matrix upstream is unreachable and no spec copy exists here; E009
must not be frozen without a human decision. New E008 candidates:
`epilectrik/voynich` Currier-B grammar, Naibbe cipher, arXiv:2609.20835.

## Previously completed

- `E011_targeted_context_scorecard` — H014 SUPPORTED_DEV / H015 FALSIFIED_DEV (development-stage).
- `E008_mechanism_competition` stage A — ALL_COMPONENTS_NOT_INFORMATIVE (scorecard-specific; see REPORT).
- `E007_p70_replication` — REPRODUCED_BUT_NOT_VALIDATED (Gate 5 section P miss; exploratory order artefact; non-prospective).
- `E006_canonical_sequence_holdout` — INCONCLUSIVE_UNDERPOWERED (1 qualifying holdout chain < floor 3; H008 unresolved; no tuning of the revealed holdout).

## Queue

- E008 — common-scorecard competition between language/cipher/generator/state-module models.
- E009 — independent blind implementation/test of the Deshuffling Matrix.
- E010 — stress-test external full-decode claims without treating their glosses as truth.
