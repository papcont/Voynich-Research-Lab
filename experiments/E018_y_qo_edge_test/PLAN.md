# E018 — the y → qo edge transition as a frozen test (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E018 metric has been computed.** Evidence class:
DEVELOPMENT (ZL3b running text; no lockbox). The full edge-state gain Δ_S (+0.088, B +0.166)
and the exploratory observation that y-final previous tokens contribute ≈ 22% of it with
`qo` as the top following prefix (E011 exploratory) are known; the quantities below are new.

## 1. Question

H003 (ledger, EXTERNAL_SUPPORT since the scaffold): "previous final *y* increases next *qo*
in Biological B". Two registered forms:

- **H003a (transition):** after a token ending in `y`, the next token's P70 prefix is `qo`
  more often than after other finals, in Biological-section Currier B, beyond a
  within-folio token-permutation null.
- **H003b (information share):** the binary feature "previous final is y / is not y"
  (BOL, UNC kept separate) captures at least half of the full edge-state codelength gain in
  Currier B.

## 2. Population and statistics

E007 population and order; features as E011. Sections from `$I`; Biological = `B`.

- **Enrichment:** `R = P(prefix = qo | prev final = y) / P(prefix = qo | prev final ∉ {y, BOL, UNC})`
  computed on Biological-B tokens; null = within-folio permutation of the population tokens
  (features recomputed), 1,000 permutations, seed 20261070; `p = (1 + #{R_null ≥ R}) / 1001`.
  Also R on the other Currier-B sections pooled, and on Currier A (reported).
- **Codelength share:** Currier-B folios, 5-fold cross-fit, `BackoffKTCoder`:
  `Δ_Sy = folio-mean(M0 − M_Sy)` with `M_Sy` = prefix slot | `Sy ∈ {y, other, BOL, UNC}`;
  `Δ_S` = the E011 M_S recomputed on B; `share = Δ_Sy / Δ_S`; folio bootstrap CIs (10,000,
  seed 20261019) for Δ_Sy and for the per-folio ratio's numerator/denominator means.

## 3. Decisions (frozen)

- H003a `SUPPORTED_DEV` iff R ≥ 1.5 and p ≤ 0.01 in Biological B; `FALSIFIED_DEV` iff
  R ≤ 1.1 or the null's 97.5% quantile ≥ R; else `INCONCLUSIVE_DEV`. "Biological-specific"
  is reported descriptively as R(Bio-B) − R(other B sections), no decision.
- H003b `SUPPORTED_DEV` iff Δ_Sy ≥ 0.05 bits/token with CI lower > 0 **and** share ≥ 0.5;
  `FALSIFIED_DEV` iff Δ_Sy CI upper < 0.05 or share < 0.25; else `INCONCLUSIVE_DEV`.

Pre-result predictions: H003a SUPPORTED_DEV with R ≈ 2–4 (historical support). H003b
`INCONCLUSIVE_DEV` or weak: share predicted 0.3–0.6 (y is the largest single contributor but
BOL, n and r carry most of the rest, E011 exploratory).

## 4. Degrees of freedom, confounds, retraction

None free. Section and language are explicit strata of the report; folio permutation
preserves folio vocabulary and line structure. H003a FALSIFIED_DEV retires H003 in this
programme; H003b only quantifies how much of the edge effect the historical y → qo
observation explains.

## 5. Registration and claim ceiling

`experiment.json` records sha256 of inputs, config, predictions. Claim ceiling: structural
transition statistics; no claim about what `y`, `qo` or the transition mean.
