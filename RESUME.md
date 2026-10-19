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

`E013_nonrunning_lockbox_claim` — **COMPLETED; Gate v2 registration FAIL; H019 SUPPORTED_DEV.** P70 vs whole-token on the never-coded label/circular/radial tokens: +2.20 bits/token (CI 0.99–3.50) from scratch with model bits charged — but the gate correctly refused registration because every lockbox folio carries a SELECTION role via its running text (folio = dependency unit). Registry corrected (`LOCKBOX_NONRUNNING_V1` → SEMI_INDEPENDENT; A001 erratum 2). On labels A6 (no suffix) and A1 beat P70 from scratch; with running-text counts P70 is best. Validator pass. See `REPORT.md`, `GATE_REPORT_P70.md`.

Before: `E010` (coupling REPRODUCED; H016–H018 FALSIFIED_DEV), `E011` (H014 SUPPORTED_DEV, H015 FALSIFIED_DEV), `E008`, `E007`, `E006`.

## Active frontier — BLOCKED on two human decisions

1. **Confirmation surface.** Under the folio rule ZL3b has no independent lockbox for any claim. Options: (a) register data from outside ZL3b (a transliteration with independent readings — IT2a/GC if reachable — or newly transcribed material); (b) amend A001 with an explicit SEMI_INDEPENDENT tier (registration flag, not FAIL) for candidates demonstrably not developed on the overlapping folios; (c) accept that all ZL3b results stay development-stage.
2. **E012 corpora/licences** (reference-text signature comparison): PerseusDL canonical-latinLit (CC-BY-SA 4.0), Dante; network use; generator/cipher set.

Development-stage work that needs no decision: a y→qo-specific prefix test (H003) under the backoff scorecard; an A6-vs-P70 label-text follow-up; stage-A of E012 generators that need no corpus (slot-grammar and self-citation generators seeded from ZL3b).

Gate v2 is in force (`research/protocol_amendments/A001_GATE_V2.md`, `research/gate/gate_v2.json`, `src/voynichlab/gate.py`, `tests/test_gate.py`, `scripts/gate_report.py`, `research/holdout_registry.json`). Confirmation surfaces: none inside ZL3b under the folio rule (A001 errata 1–2). IT2a/GC hashes unregistered (voynich.nu unreachable 2026-10-19).

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
