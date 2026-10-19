# Protocol Amendment A002 — PROPOSAL: candidate-specific contamination and a semi-independent confirmation tier

- Status: **PROPOSAL — not in force.** Nothing in the gate, registry or any result changes until
  a human approves this text (possibly modified). Drafted 2026-10-20 to make decision 1
  concrete.
- Would amend: A001 §4 (holdout protection) and `research/gate/gate_v2.json`
  (`holdout_protection`, `registration`).

## Problem

A001 §4 treats a folio as burned for *every* future claim once *any* experiment used it for
selection or error analysis. After E006–E008 and the E008 exploratory analysis, every ZL3b
running-text folio carries such a role, and label text lies on the same folios. All
Voynich text is in ZL3b. Consequence: **no claim of any kind can ever reach a Gate v2 level
in this programme**, including claims by external parties whose development never touched
our folds. The rule protects against our own leakage but also forecloses confirmation of
anything, which was not its purpose.

## Proposal

1. **Contamination is candidate-specific.** The registry records, per *candidate* (a
   registered model/mechanism with a sha256 specification), the set of folios used in that
   candidate's development: selection, threshold setting, error analysis, or any
   evaluation whose result was visible to the candidate's authors before the candidate's
   specification was hash-registered. A folio is contaminated *for that candidate* only.

2. **Three independence classes for a lockbox, per candidate:**
   - `INDEPENDENT` — data outside any material the candidate's authors could have seen
     (new transcriptions, new sources). Required for `LANGUAGE_IDENTIFICATION_SUPPORTED`
     and above (levels 3–5) and for `DECIPHERMENT_CONFIRMED`.
   - `SEMI_INDEPENDENT` — folios not in the candidate's own development set, but used by
     *other* candidates or by this programme's earlier experiments. Admissible for levels
     1–2 (`STRUCTURAL_MODEL_VALIDATED`, `DECODING_MECHANISM_SUPPORTED`) only, with the
     conditions in 3.
   - `DEVELOPMENT_ONLY` — folios in the candidate's own development set. Never a lockbox.

3. **Conditions for a SEMI_INDEPENDENT level-1/2 claim:**
   a. The candidate's full specification (mechanism, dictionaries, keys, exceptions) was
      hash-registered in a commit that precedes any evaluation of that candidate on the
      lockbox folios, and the commit is in this repository or a public, timestamped one.
   b. A written development log states which data the candidate was built on; the gate
      report prints the overlap between that set and the lockbox (must be empty).
   c. The strongest frozen null for the pool is itself re-fitted only on folios outside
      the candidate's development set, or the claim uses a null registered before the
      candidate (the null may be contaminated for the *programme* — that penalises the
      candidate, never helps it).
   d. Every report, ledger row and status line carries the flag
      `SEMI_INDEPENDENT (levels ≤ 2)`; the claim ceiling says so verbatim.
   e. A SEMI_INDEPENDENT level can be withdrawn if a later audit finds the development
      log incomplete; the registry keeps the withdrawal.

4. **This programme's own candidates.** P70 layer A (E007) was scored on every folio
   (global and cross-fitted) with its specification registered beforehand but its
   *competitor set, margins and gate design* chosen on all folios: for P70 the whole ZL3b
   stays `DEVELOPMENT_ONLY`. M_S/M_Sfam (E011) likewise. New structural candidates from
   this programme may use SEMI_INDEPENDENT lockboxes only if their specification is
   registered before any run and their development uses a *declared* folio subset,
   recorded in the registry at freeze time.

5. **What stays unchanged.** Levels 3–5 still need INDEPENDENT data; specificity controls,
   model-bit accounting, margins, bootstrap CIs, retraction conditions and the no-retuning
   rule are untouched. A001 errata 1–2 remain correct statements about *programme-level*
   contamination.

## Implementation if approved

- `research/holdout_registry.json`: add `candidates: {id: {spec_sha256, development_folios,
  registered_commit}}`; lockbox independence becomes a function `independence(lockbox,
  candidate)`.
- `voynichlab.gate.check_registration`: take `candidate_id`; overlap check against that
  candidate's development set; emit the flag and cap the achievable level at 2 for
  SEMI_INDEPENDENT.
- Tests: a candidate with an empty development overlap passes level 1 on a
  SEMI_INDEPENDENT lockbox with the flag; the same candidate with one overlapping folio
  fails registration; level 3 on a SEMI_INDEPENDENT lockbox is capped to NOT_TESTED.
- E013's P70 claim would **still fail** under A002 (P70 is DEVELOPMENT_ONLY on all folios);
  a freshly specified structural candidate with a declared development subset would be the
  first eligible claim.

## What the human decides

Approve as written, approve with changes (e.g. cap at level 1 only, or require a public
timestamp), or reject and keep A001 §4 strict (all ZL3b results remain development-stage;
confirmation only on new data).
