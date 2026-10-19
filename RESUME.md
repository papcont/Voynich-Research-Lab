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

`E008_mechanism_competition` stage A — **COMPLETED, ALL_COMPONENTS_NOT_INFORMATIVE** (first reveal 2026-10-19; plan `9563bc4`, amendment `f71a588`). Edge state S, line position L and local copy/modify C each *increase* holdout bits/token over the bare P70 base under the frozen no-backoff KT scorecard (unique Δ −1.95 / −0.36 / −0.25). S and L beat the within-folio shuffle null by 0.89 / 0.33 (information present, context fragmentation dominates); C equals the null. H011–H013 falsified as predictive components (scorecard-specific). An implementation deviation in the canonical edit string was caught by `validate.py`, corrected and re-run before interpretation (verdicts unchanged). Exploratory backoff coder: +L gains 0.10, +S still −0.13 → test S on the prefix slot only (E011 draft). See `REPORT.md`.

## Active frontier

`E011_targeted_context_scorecard` — **PLAN_FROZEN** (development-stage, `DEVELOPMENT_CROSSFIT`). Backoff KT scorecard (escape to parent context with exclusion), slot-targeted conditioning: M_S (prefix | previous final glyph, H014), M_L (prefix+suffix | line position, H015) vs M0 = P70 plain KT; 5-fold cross-fit over all 206 running-text folios; folio bootstrap CI; margin = max(0.05, q97.5 of a feature-permuted null) computed before the real contrasts; labels SUPPORTED_DEV / FALSIFIED_DEV / INCONCLUSIVE_DEV; sha256 registration in `experiment.json`. **No Gate v2 level is claimable**: the holdout registry (A001 §4 erratum) shows every ZL3b running-text folio carries a SELECTION role, so `DEVELOPMENT_POOL_RUNNING_V1` is development-only. Next action: implement `BackoffKTCoder` (+fixtures), `run.py`, `validate.py`; results before report.

Gate v2 is in force (`research/protocol_amendments/A001_GATE_V2.md`, `research/gate/gate_v2.json`, `src/voynichlab/gate.py`, `tests/test_gate.py`, `scripts/gate_report.py`, `research/holdout_registry.json`). Confirmation surfaces: `LOCKBOX_NONRUNNING_V1` (710 label/circular/radial tokens, INDEPENDENT) only; running-text confirmation needs data registered from outside ZL3b. IT2a/GC hashes unregistered (voynich.nu unreachable 2026-10-19).

## External check (2026-10-19)

See `research/STATUS.md` § External landscape check and `external/repos.yml`.
Does not change E007 (frozen on its pin). **E009 provenance blocker:** the
Deshuffling-Matrix upstream is unreachable and no spec copy exists here; E009
must not be frozen without a human decision. New E008 candidates:
`epilectrik/voynich` Currier-B grammar, Naibbe cipher, arXiv:2609.20835.

## Previously completed

- `E008_mechanism_competition` stage A — ALL_COMPONENTS_NOT_INFORMATIVE (scorecard-specific; see REPORT).
- `E007_p70_replication` — REPRODUCED_BUT_NOT_VALIDATED (Gate 5 section P miss; exploratory order artefact; non-prospective).
- `E006_canonical_sequence_holdout` — INCONCLUSIVE_UNDERPOWERED (1 qualifying holdout chain < floor 3; H008 unresolved; no tuning of the revealed holdout).

## Queue

- E008 — common-scorecard competition between language/cipher/generator/state-module models.
- E009 — independent blind implementation/test of the Deshuffling Matrix.
- E010 — stress-test external full-decode claims without treating their glosses as truth.
