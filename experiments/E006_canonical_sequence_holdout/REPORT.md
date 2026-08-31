# E006 — REPORT (interpretation, written after results.json)

**Decision: INCONCLUSIVE_UNDERPOWERED. H008 remains unresolved.**

Evidence class: `FROZEN_HOLDOUT`. Source ZL3b-n.txt, git-blob
`2a4533ab…`, sha256 `bf5b6d4a…`. Plan commit `4c80f70`, amendment `4323969`,
run at HEAD `4323969`, first reveal `2026-08-31T13:50:51Z`, seed `20260831`.

## What was tested

Whether, on held-out folios (hash folds {3,4}, 88 folios), the *fused* and
*spaced* realizations of the **same** k=2 canonical chain (stem + two finals;
stems `ot/ok/qot/qok`, finals `ar/al/aiin/am/or/ol`) share external context
more than matched nulls predict — using an equal-weight-per-chain mean
Jensen-Shannon divergence with a preregistered p<0.05 gate (N1 + N2 +
leave-one-chain-out). All choices were frozen before this computation.

## What the holdout actually contains

- Holdout k=2 canonical occurrences: **25 fused, 53 spaced**, across **45**
  distinct chains.
- Chains with **≥2 fused AND ≥2 spaced** occurrences in the holdout: **1**
  (`ok|al|or`, 2 fused / 2 spaced).
- Preregistered power floor: **3** qualifying chains.

1 < 3 ⇒ `INCONCLUSIVE_UNDERPOWERED` per PLAN §6 and
PREFLIGHT_AMENDMENT_001 Resolution A. No target JSD, null p-values, or
leave-one-chain-out diagnostics were computed, because the frozen design does
not compute them below the power floor.

Additionally, the single qualifying chain has its fused occurrences (f103r,
f78v) and spaced occurrences (f105r, f86v6) in **disjoint folios**. Even with
more chains, the within-folio N2 label permutation would have been
**DEGENERATE** (no (chain, folio) stratum holds both realizations), so the
frozen three-part gate could not have been fully cleared as designed. This was
already observed in the development folds (0 mixed strata) and is recorded, not
worked around.

## Interpretation (bounded)

The same-chain fused/spaced co-occurrence that the k=2 grammar targets is **too
rare in the ZL3b holdout** to support the frozen context-similarity test with
power. This is a property of the data + the deliberately narrow grammar, not
evidence for or against variable attachment.

- H007 (specific final chains have variable attachment): **still OPEN**. The
  surface pairs exist (E005), but E006 did not adjudicate them.
- H008 (canonicalizing attachment improves held-out distant context):
  **UNRESOLVED**. Neither supported nor falsified.

## What must NOT be done (anti-tuning)

Per protocol and the frozen plan, the underpowered result is **not** a licence
to: add `edy/eedy` or other finals/stems; widen to k≥3; shrink the holdout;
lower `n_min`/the power floor; or relabel this run prospective after seeing it.
Any of those would be post-hoc tuning of a revealed holdout.

A future, **separately preregistered** experiment could test the same idea with
a design that is powered for rare same-chain co-occurrence (e.g. pooling
context at the stem×final-pair family level with an explicit dependency-aware
null, or a within-folio-mixing requirement built into eligibility). That is new
science with its own frozen plan — not a repair of E006.

## Claim ceiling

Unchanged and not reached: no morphology, phonetics, semantics, language
identification, or plaintext. E006 yields only a documented negative-space
result: **the frozen test is underpowered on this holdout.**
