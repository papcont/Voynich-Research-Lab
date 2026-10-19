# RESUME — deterministic restart point

## Read order

(Programme synthesis as of 2026-10-20: `research/SYNTHESIS_2026-10-20.md`.)

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

`E021_selective_boundaries` — **COMPLETED (development-stage).** Selectivity S1 (single-contrast share of boundary MI): Voynich 0.233 on `y → q` (full 0.284) vs 0.06–0.14 for prose, stream cuts, E020 mixture → H031 PARTIAL. Marker-pair process: coupling 0.44 and S1 0.98 at the lowest grid value → H032 FALSIFIED (too strong, too deterministic). Letter-conditioned cuts never reach the level → H033 FALSIFIED. The manuscript's coupling is one probabilistic dominant transition plus a diffuse remainder. Validator pass. See `REPORT.md`.

Before: `E020`, `E019`, `E012`, `E018`, `E017`, `E016`, `E015`, `E014`, `E013`, `E010`, `E011`, `E008`, `E007`, `E006`; synthesis `research/SYNTHESIS_2026-10-20.md` (E021 not yet folded in).

## Active frontier — BLOCKED on two human decisions

1. **Confirmation surface.** Under the folio rule ZL3b has no independent lockbox for any claim. Options: (a) register data from outside ZL3b (a transliteration with independent readings — IT2a/GC if reachable — or newly transcribed material); (b) amend A001 with an explicit SEMI_INDEPENDENT tier (registration flag, not FAIL) for candidates demonstrably not developed on the overlapping folios; (c) accept that all ZL3b results stay development-stage.
2. **E012-B (Borg)** — the open-rights texts are done; only the `linked_only` Borg material (17th-c. Latin pharmaceutical recipes + its real simple-substitution ciphertext, in the pinned `cipher_benchmark` clone) awaits your approval for local analysis use. It is the closest available analogue to the manuscript's subject matter and the only real historical cipher with known plaintext in hand.

Development-stage work that needs no decision: an A6-vs-P70 label-text follow-up (small). Everything else of value now needs one of the two decisions (corpora for E012; a confirmation surface or collation data).

**Signature v3 module:** `src/voynichlab/signature.py` (+ `tests/test_signature.py`) computes Δ_S, Δ_L, Δ_C, TTR, H1, folio-local reuse excess and codex-order locality for any line-structured text with the frozen definitions; the regression test reproduces the recorded E011/E014/E016/E017 values exactly. E012 scores reference texts and generators with this module.

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
