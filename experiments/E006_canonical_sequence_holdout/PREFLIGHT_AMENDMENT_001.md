# E006 — Preflight Amendment 001 (pre-reveal)

- Amendment timestamp (UTC): **2026-08-31T13:44:26Z**
- Pre-reveal HEAD at authoring: **4c80f70** ("Freeze E006 canonical final-chain holdout plan (pre-result)")
- **No holdout target metric had been computed before this amendment.** Only
  corpus-wide occurrence *counts* of already-known development tokens
  (frequency is a declared nuisance) had been inspected. The confirmatory
  statistic — context similarity on holdout folds {3,4} — is uncomputed.

This amendment only resolves internal contradictions and implementation
ambiguities in the frozen `PLAN.md`. It does **not** change the grammar,
stems/finals lists, k=2 restriction, holdout split, seed, resample count,
metric, `n_min`, power floor, or decision thresholds. It does not optimize any
choice toward a result, because no result exists yet. Where `PLAN.md` prose and
`experiment.json` disagree, the resolutions below adopt the reading **already
recorded in `experiment.json`**.

---

## Resolution A — Underpowered ⇒ INCONCLUSIVE (not falsified)

`PLAN.md` §6 (authoritative, preregistered):
> "If fewer than **3** chains qualify in the holdout, the result is declared
> INCONCLUSIVE (underpowered) and H008 is neither supported nor falsified;
> this branch is a legitimate preregistered outcome, not a failure to hide."

`PLAN.md` §8 contains a contradictory trailing clause:
> "… or a single leave-one-chain-out removal destroys it, **or the holdout is
> underpowered (§6 INCONCLUSIVE branch)**."

**Resolution:** §6 governs. The trailing "or the holdout is underpowered"
clause in §8 is **void**. Underpowered (< 3 qualifying chains) ⇒
`power_branch = "INCONCLUSIVE_UNDERPOWERED"` ⇒ H008 remains **unresolved**
(neither SUPPORTED nor WEAKENED/NOT_SUPPORTED). This matches
`experiment.json.decision_rule` ("underpowered (<3 chains) => INCONCLUSIVE").

The falsification/weakening conditions in §8 that remain in force are:
primary N1 p ≥ 0.05; a Band-A-only effect with no Band-B transfer; effect
vanishing under N2; a single leave-one-chain-out removal destroying the effect.
These apply **only when the holdout is adequately powered** (≥ 3 qualifying
chains).

## Resolution B — N1 matching = frequency-decile + Currier-language

`PLAN.md` §7 header uses the misleading shorthand
"N1 — frequency/**section**-matched random pairing", while its own body and
`experiment.json` operationalize it as **frequency decile + Currier language**.

**Resolution:** N1 matches replacement tokens on **(frequency decile, Currier
language)**, holdout-preserving, exactly as the §7 body and
`experiment.json.nulls[0]` already state. The word "section" in the §7 header
is a labeling error and is corrected to "Currier-language". **No additional
section/locus stratification is introduced.** Hand/section remain partially
folio-confounded and are absorbed by folio-clustered resampling, as
`PLAN.md` §10 already states.

---

## Operational clarifications (implementation determinism, not new science)

These pin down under-specified mechanics so the run is deterministic and
replayable. None changes a frozen scientific parameter; all are fixed here
before any target computation.

1. **Strict tokens** are exactly the non-uncertain tokens yielded by
   `voynichlab.ivtff.iter_strict_tokens` over `data/raw/ZL3b-n.txt`.

2. **Realization / chain identity.** A chain C is the unit tuple `(stem,f1,f2)`
   with `f1,f2 ∈ FINALS`. FUSED = one strict token whose whole surface parses
   via `parse_fused_token` to exactly `(stem,f1,f2)`. SPACED = strict token A
   with `parse_fused_token(A) == (stem,f1)` immediately followed **on the same
   source line** by strict token B with surface `== f2`, the separator between
   them being a certain `.` (uncertain `,` excluded).

3. **Per-folio context stream.** For a folio, concatenate its lines' strict
   tokens in file order into one stream. Context never crosses folios.

4. **Distance and consumed-span exclusion.** For one realization occurrence,
   let its consumed positions be the stream index of the fused token, or the
   two indices of spaced tokens A,B. Candidate context tokens are all other
   stream positions; the distance of a candidate at index `j` is the number of
   positions to the nearest edge of the consumed span
   (`min(|j - first|, |j - last|)`), the consumed positions themselves being
   excluded from candidacy. Band A = distance exactly 1 (weight 1.0);
   Band B = distance 2..10 inclusive (weight 0.5).

5. **Context distribution.** A realization-type's context distribution for a
   chain pools, over all that chain's occurrences of that type in the fold
   under analysis, the weighted counts of neighboring strict-token **surface
   types**, normalized to sum 1. JSD via `voynichlab.metrics.jensen_shannon`
   (base-2, range [0,1]).

6. **Frequency deciles** are computed over strict-token **type** frequencies in
   the **holdout** stream (folds {3,4}): rank types by holdout count, split into
   10 approximately equal-count bins; a token's decile is its bin.

7. **N1 (null).** Replace each qualifying chain's *spaced* context distribution
   with the folio-context distribution of a random replacement strict-token
   **type** drawn from the holdout, matched to the chain's **fused** token
   frequency decile and drawn with Currier-language composition matching that
   chain's spaced occurrences; recompute mean JSD over qualifying chains to get
   one null `D`. ≥ 1000 resamples. `p = (#{null D ≤ D_obs}) / R` (one-sided;
   lower JSD = more similar).

8. **N2 (null).** Within each folio, permute fused/spaced labels across that
   folio's occurrences of the same chain, preserving per-folio per-chain fused
   and spaced counts; recompute mean JSD. ≥ 1000 resamples; same one-sided p.
   **N2 degeneracy check (Task §8):** a (folio, chain) stratum with all-fused or
   all-spaced occurrences yields zero permutable pairs. Count contributing
   strata; if **no** stratum admits a non-trivial permutation, N2 is reported as
   **DEGENERATE**, the N2 gate cannot be passed, and the frozen gate cannot be
   fully cleared — this is recorded, **not silently replaced**.

9. **N3 (specificity, not a gate).** Pair each fused chain with a random
   **non-canonical** strict token (`parse_fused_token(token) is None`) of equal
   surface length and equal frequency decile (of the fused token), drawn from
   the holdout; compute JSD(fused_ctx, distractor_ctx); aggregate as D. ≥ 1000
   resamples; report the one-sided p as specificity context only.

10. **Determinism.** A single `numpy.random.default_rng(20260831)` (or a fixed
    `random.Random(20260831)`) drives all resampling; chains are processed in
    sorted order and resample draws occur in a fixed loop order, so the run is
    exactly replayable. Seed, resample count, and software versions are recorded
    in `results.json`.

11. **Reporting bands.** Band A and Band B mean-JSD are computed and reported
    **separately** in addition to the combined primary metric, so the frozen
    §8 "Band-A-only ⇒ no distant transfer" condition can be evaluated. The
    primary metric is **not** redefined; the combined weighted distribution
    (bands A+B together) remains the primary D_obs.

---

## Residual-ambiguity check

No remaining ambiguity is a materially-different, equally-defensible scientific
design that would change the claim. Therefore the run proceeds; `RESEARCH_STATE`
is **not** set to BLOCKED. If, during implementation, any choice above proves
to have a genuinely defensible alternative that could move the target, the run
must stop and record a BLOCKED state before reveal rather than pick silently.
