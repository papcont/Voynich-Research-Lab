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

`E016_folio_vocabulary_locality` — **COMPLETED (development-stage).** H024 SUPPORTED_DEV: folio-local vocabulary reuse +0.035 (CI 0.027–0.044, p < 0.001) beyond a Currier × section, size-preserving permutation; both languages. H025 FALSIFIED_DEV under the frozen rule, whose token-permutation null was unsuitable for an adjacency question (recorded as a design flaw); the exploratory order-permutation null is strongly positive (0.107 vs 0.096) → H025b to be preregistered. Validator pass. See `REPORT.md`.

Before: `E015`, `E014`, `E013`, `E010`, `E011`, `E008`, `E007`, `E006`.

## Active frontier — BLOCKED on two human decisions

1. **Confirmation surface.** Under the folio rule ZL3b has no independent lockbox for any claim. Options: (a) register data from outside ZL3b (a transliteration with independent readings — IT2a/GC if reachable — or newly transcribed material); (b) amend A001 with an explicit SEMI_INDEPENDENT tier (registration flag, not FAIL) for candidates demonstrably not developed on the overlapping folios; (c) accept that all ZL3b results stay development-stage.
2. **E012 corpora/licences** (reference-text signature comparison): PerseusDL canonical-latinLit (CC-BY-SA 4.0), Dante; network use; generator/cipher set.

Development-stage work that needs no decision: H025b codex-order adjacency with an order-permutation null (and collation data if registered); a y→qo-specific prefix test (H003); an A6-vs-P70 label-text follow-up; signature v2 + F with a proper null as the E012 scorecard.

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
