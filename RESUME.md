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

`E010_external_claim_stress_tests` — **COMPLETED**: R1 REPRODUCED (epilectrik boundary coupling 0.2548/0.2134 vs published 0.256/0.215; class coverage 71.3% vs 69.5%); H016 (glyph units) −0.0007, H017 (two units) +0.0012, H018 (49-class table) −3.085 bits/token → all FALSIFIED_DEV on Currier B under the E011 scorecard. Validator pass. See `REPORT.md`.

Before that: `E011` (H014 SUPPORTED_DEV +0.088; H015 FALSIFIED_DEV; null M_Sfam registered), `E008` (all components NOT_INFORMATIVE under the no-backoff scorecard), `E007` (REPRODUCED_BUT_NOT_VALIDATED), `E006` (INCONCLUSIVE_UNDERPOWERED).

## Active frontier

`E013` — **READY_TO_FREEZE_PLAN**: first Gate v2 lockbox claim. Candidate = P70 layer-A four-slot model (plain KT, frozen since E007); null = whole-token KT (to be registered for the non-running pool); lockbox = `LOCKBOX_NONRUNNING_V1` (710 label/circular/radial tokens on 39 folios, INDEPENDENT — never coded by any experiment); development = running-text pool for margin calibration (P70 beat whole-token by 1.87 bits/token prequentially in E007; provisional margin 0.5); E007 competitors A5/A6/A7/A8 reported, with a preregistered stricter rule that P70 must also beat each of them. Claim record + `scripts/gate_report.py`; expected level if it passes: `STRUCTURAL_MODEL_VALIDATED` (level 1 only). Freeze PLAN.md, register sha256, then run once.

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
