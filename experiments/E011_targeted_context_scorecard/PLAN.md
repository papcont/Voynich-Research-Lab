# E011 — hypothesis-shaped conditioning under a backoff scorecard (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-19)
Freeze rule: every scientific choice is fixed here before any E011 metric is computed.
**No E011 metric has been computed at freeze time.** Inspected before freeze: population
facts only (running text 33,611 strict tokens / 206 folios; Currier A 10,833, B 22,255;
E008 feature counts BOL 3,900 / UNC 858 / glyph 28,853). The E008 post-reveal exploratory
numbers (all-slot backoff: B1 15.57, +L 15.47, +S 15.70 on the E007 holdout) are known and
are the reason this experiment exists; they are **not** E011 targets and E011 does not
reuse that coder variant.

Evidence class: **DEVELOPMENT_CROSSFIT** (development-stage). Per the holdout registry
(`research/holdout_registry.json`, A001 §4 erratum) no running-text lockbox exists in ZL3b,
so E011 cannot reach any Gate v2 level. It (1) tests H014/H015 at development stage with
Gate-v2 statistics, and (2) registers the strongest frozen structural null for future
claims.

Hypotheses: **H014** — the previous token's final glyph carries predictive information
about the next token's **prefix slot** (the E002/H003 "y → qo" shape). **H015** — line
position carries predictive information about the prefix and suffix slots.

---

## 1. Population, order, split

- Source `data/raw/ZL3b-n.txt`, blob `2a4533ab…`, sha256 `bf5b6d4a…` (checked at run time).
- Population and order identical to E007/E008 (running-text strict tokens, lexicographic
  folio order, file order within folio). Line features as E008 §6.1–6.2: `S(t)` = last EVA
  character of the previous token in the same line, `BOL`, or `UNC`; `L(t)` ∈
  {FIRST, MID, LAST, ONLY}.
- Development pool = all 206 folios (`DEVELOPMENT_POOL_RUNNING_V1`, sha256 `…` recorded in
  `experiment.json`). Estimates are **5-fold cross-fitted** by `efold` (E007 split): for
  each fold j, counts are accumulated on the other four folds, frozen, and fold j is coded
  without updates. Every token therefore receives exactly one out-of-fold codelength.
- Dependency unit = folio (206 paired folio differences).

## 2. Scorecard (frozen): KT with PPM-style backoff and exclusion

Base slots = P70 layer A `(p, g, c, s)` via `voynichlab.p70.parse_p70` (lossless). The
null model **M0** codes slot *i* in context `c0 = ("base", i, v[:i])` with the plain KT +
char-escape coder of E007 §4.3 (`mdl.KTCoder`) — identical to E007/E008 "B1".

A *conditioned* slot has context `c1 = ("base", i, v[:i], F)` where `F` is the model's
feature for that slot. Coding value `x` in `c1` (counts `n1`, distinct `m1`, `n1_x`):

```
P1(x)      = (n1_x + 0.5) / (n1 + 0.5 (m1 + 1))              if x seen in c1
escape1    =  0.5         / (n1 + 0.5 (m1 + 1))
otherwise  cost = -log2(escape1) + cost0_excl(x)
cost0_excl: KT in c0 restricted to values NOT seen in c1 (exclusion):
            P0(x) = (n0_x + 0.5) / (n0' + 0.5 (m0' + 1)),  n0', m0' over non-excluded values
            if x unseen in c0 too:  -log2(0.5 / (n0' + 0.5 (m0' + 1))) + charcost(x)
```

Seen mass + escape mass sum to 1 in `c1`; the escape mass is spread over `c0`'s
distribution restricted to non-excluded values (which sums to 1 with its own escape), so
the code is a proper prefix code. After coding, **both** `c1` and `c0` counts are updated
with `x` (training passes only). Implementation: `mdl.BackoffKTCoder`, fixture-tested
before the run (sum-to-one, exclusion, determinism); no corpus metric in the tests.
`charcost` and Σ as in E007 (|Σ| recorded).

## 3. Models (frozen)

| model | conditioned slots | feature |
|---|---|---|
| **M0** | none | — (null; = E007/E008 B1) |
| **M_S** | prefix (slot 0) | `S(t)` |
| **M_L** | prefix (0) and suffix (3) | `L(t)` |
| M_SL | prefix by `(S, L)`, suffix by `L` | both (secondary) |
| M_Sfam | prefix | previous token's P70 suffix string or `BOL`/`UNC` (secondary) |
| M_Sall | all four slots | `S(t)` (E008 shape under backoff; descriptive continuity) |

Primary contrasts: **M_S − M0** (H014) and **M_L − M0** (H015). Secondary (reported, not
gated): M_SL − M0, M_Sfam − M0, M_SL − M_S, M_SL − M_L, M_Sall − M0. Model-description cost
per Gate v2 components: `mechanism_code_bits` = P70 inventory cost (E007 Amendment 001 §4)
+ `elias_gamma(1 + #conditioned slots)`; the other five components are 0 and declared.

## 4. Statistics (Gate v2 compression semantics, development stage)

For a contrast `A − B`: per-folio paired difference `Δ_f = (bits_B(f) − bits_A(f)) / n_f`
in bits/token (positive = A better), computed from out-of-fold codelengths; mean over
folios; percentile bootstrap of the mean (10,000 resamples, seed 20261019, 2.5/97.5%).
Currier subsets: the same with folios of `$L = A` and `$L = B` (folios with `$L` None
excluded from the subset check).

**Margin calibration (frozen rule, development data only).** For each primary model X,
build the *null-feature* model X° in which the feature values are permuted among the
population tokens **within each folio** (seed 20261019; feature marginals preserved,
pairing destroyed) and compute its cross-fitted Δ°_f against M0. `margin_X =
max(0.05, q97.5 of the bootstrap distribution of mean Δ°)`. Justification: a component must
beat what a meaningless feature of the same cardinality obtains from coder bookkeeping,
with the programme's 0.05 bits/token floor. Margins are recorded in `results.json` before
the real contrasts are read.

**Decision per primary hypothesis (development-stage labels):**
- `SUPPORTED_DEV` iff mean Δ ≥ margin_X **and** CI lower > 0 **and** mean Δ − mean Δ° ≥
  margin_X **and** Δ > 0 in both Currier A and B.
- `FALSIFIED_DEV` iff CI upper < margin_X.
- otherwise `INCONCLUSIVE_DEV`.

No Gate v2 level is claimable (no lockbox). The claim record is still written
(`claim_E011_M_S.json`) and run through `scripts/gate_report.py` to exercise the pipeline;
the expected gate outcome is registration FAIL / NOT_TESTED because `lockbox_id` names a
`DEVELOPMENT_ONLY` pool — that is the correct behaviour, not a defect.

## 5. Pre-result predictions

- H014: `SUPPORTED_DEV`; Δ larger in Currier B than in A (y → qo is a Biological-B
  phenomenon in E002); predicted size 0.05–0.3 bits/token.
- H015: small; `INCONCLUSIVE_DEV` or weak `SUPPORTED_DEV`; `FALSIFIED_DEV` is live.
- Secondary: M_Sall − M0 < M_S − M0 (slot targeting matters); M_Sfam ≈ M_S.

## 6. Falsification / retraction conditions

- H014 `FALSIFIED_DEV` ⇒ the programme retires "previous final glyph predicts the next
  initial" as a *predictive* mechanism component on ZL3b (H003 keeps its literature status
  but is marked not reproduced here).
- H015 `FALSIFIED_DEV` ⇒ line position is dropped from the mechanism inventory.
- No post-hoc feature redefinition, slot re-targeting, coder change or margin change after
  the run. Any implementation detail not fixed here is settled by a committed amendment
  **before** `run.py` computes a contrast.

## 7. Registration (Gate v2 §registration)

`experiment.json` records sha256 of: inputs (ZL3b file), split (the efold definition
string and the development-pool folio list), config (this PLAN.md at freeze), predictions
(§5 text). Freeze commit = the commit introducing this file.

## 8. Confounds and descriptive reports

Per major section {S, H, B, P} Δ; token-length bins; share of `BOL`/`UNC` contexts; per-fold
means; all-slot variant (M_Sall) for continuity with E008. None gate anything.

## 9. Degrees of freedom

None free: coder, slots, features, split, seeds, margin rule and labels are fixed above.
Two primary contrasts; secondary contrasts are descriptive.

## 10. Claim ceiling

> "On ZL3b running text, under a backoff universal coder, conditioning the P70 prefix slot
> on the previous token's final glyph (and/or the prefix and suffix slots on line position)
> changes out-of-fold description length by Δ bits/token (CI)."

Development-stage, structural only; not morphemes, language, cipher, hoax or meaning; not a
Gate v2 level. The best model becomes the registered strongest structural null for future
lockbox claims.

## 11. Deliverables

`src/voynichlab/mdl.py::BackoffKTCoder` + `tests/test_mdl.py` fixtures; `run.py`
(`results.json` first), `validate.py` (independent coder + features), `REPORT.md`,
`claim_E011_M_S.json` + gate report. **No E011 contrast, margin or codelength has been
computed.**
