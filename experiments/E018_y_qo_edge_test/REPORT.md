# E018 — REPORT (interpretation, written after results.json)

**H003a SUPPORTED_DEV: after a token ending in `y`, the next token's P70 prefix is `qo`
6.1 times as often as after other finals in Biological-section Currier B (40.1% vs 6.6%;
within-folio permutation null 0.99, 97.5% quantile 1.09, p < 0.001). H003b SUPPORTED_DEV:
the binary feature "previous final is y / is not" captures 72% of the full edge-state
codelength gain in Currier B (Δ_Sy = 0.124 bits/token, CI 0.106–0.142, vs Δ_S = 0.171).**

Plan `c980ba7`; one run; independent `validate.py`: `E018_VALIDATION_PASS`. Development
stage (no lockbox). The historical H003 (ledger, EXTERNAL_SUPPORT since the scaffold) is
now independently quantified in this programme.

## Enrichment R = P(qo | prev y) / P(qo | prev other final)

| population | n after y / after other | P(qo \| y) | P(qo \| other) | R | null mean (97.5%) | p |
|---|---|---|---|---|---|---|
| **Biological B** | 2,841 / 2,483 | **0.401** | 0.066 | **6.07** | 0.99 (1.09) | < 0.001 |
| other B sections | 5,993 / 8,150 | 0.282 | 0.076 | 3.71 | 1.02 (1.09) | < 0.001 |
| Currier A | 2,803 / 6,173 | 0.145 | 0.066 | 2.19 | 1.02 (1.15) | < 0.001 |

Prediction (R 2–4) was *exceeded* in Biological B (6.1) and met elsewhere; the effect is
present in every population and graded: Biological B > other B > A (R difference
Biological − other B = +2.36, descriptive).

## Codelength share (Currier B, 5-fold cross-fit, backoff coder)

| model | bits/token | folio-mean gain vs M0 |
|---|---|---|
| M0 | 13.769 | — |
| M_Sy prefix \| {y, other, BOL, UNC} | 13.625 | **0.124** [0.106, 0.142] |
| M_S prefix \| full previous final | 13.577 | 0.171 [0.151, 0.191] |

share = 0.72 (prediction 0.3–0.6: exceeded). A four-valued feature carries nearly three
quarters of what the 27-valued one carries.

## Reading

1. The y → qo transition is the single dominant component of the edge-state effect, not one
   contributor among many. Combined with E011's exploratory decomposition (line start 28%,
   y 22% of the gain *across all contexts*), in Currier B the y/not-y distinction alone
   explains most of the between-token dependency the programme has found.
2. It is strongest where the lore said (Biological B), but it is not a Biological-only
   phenomenon: even Currier A shows a doubling. Any mechanism proposal must produce a
   graded, population-wide `…y → qo…` coupling with the Biological section as its extreme.
3. Nothing here says what `y`, `qo` or the coupling *are*. Candidate readings (a boundary
   marker pair, a cipher state, a scribal habit, a phonotactic constraint) are not
   separated by this test; E012's reference corpora are the place to compare.

## Consequences

- H003 → the parent row is updated to `QUANTIFIED_HERE` with E018 as the registered
  form; H003a and H003b SUPPORTED_DEV.
- The structural inventory's "edge state" component gets a concrete shape: mostly y → qo.

Claim ceiling: structural transition statistics; no meaning claims; no Gate v2 level.
