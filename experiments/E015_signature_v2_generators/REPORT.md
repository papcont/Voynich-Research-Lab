# E015 — REPORT (interpretation, written after results.json)

**All three generators MISMATCH signature v2. H022 (edge-coupled + Pitman–Yor vocabulary)
FALSIFIED; H023 (folio-horizon self-citation) FALSIFIED.** Adding inventory and sharing
components makes the signature discriminate every generator tested so far, and the
pattern of misses says what a generator would still need.

Plan `3bc52d2`; one run (5 seeds per generator); independent `validate.py` re-scores all 15
generated texts and the real skeleton: `E015_VALIDATION_PASS`. Development stage; no Gate
level; Voynich values EXPLORATORY.

## Signature v2 (generators: mean over 5 seeds; SD ≤ 0.02 on every component)

| component | Voynich | G4 edge | G5 edge + PY (d 0.7, θ 10) | G6 folio self-citation (0.5, 0.6) |
|---|---|---|---|---|
| Δ_S prefix \| prev. final | **+0.088** | 0.147 ✘ | 0.139 ✘ | −0.005 ✘ |
| Δ_L line position | **−0.026** | −0.041 ✔ | −0.166 ✘ | −0.159 ✘ |
| Δ_C copy W=5 | **−0.463** | −0.447 ✔ | −0.188 ✘ | **+1.604** ✘ |
| TTR | **0.193** | 0.141 ✘ | 0.220 (by construction) | 0.298 ✘ |
| H1 hapax share | **0.669** | 0.386 ✘ | 0.702 (by construction) | 0.630 (constr.) |
| F within-folio repetition | **0.242** | 0.166 ✘ | 0.168 ✘ | 0.272 (0.03) |
| X cross-folio sharing | **0.818** | 0.934 ✘ | 0.811 ✔ | 0.691 ✘ |
| verdict | — | MISMATCH | MISMATCH | MISMATCH |

Predictions: G4 MISMATCH on TTR/H1 ✔; G5 predicted PARTIAL with Δ_S overshoot — the
overshoot came (0.139) but Δ_L and Δ_C also missed, so MISMATCH; G6 MISMATCH ✔ (Δ_S ≈ 0,
Δ_C +1.6, F high).

## Reading

1. **Edge coupling overshoots in every edge-coupled generator** (0.139–0.147 vs 0.088,
   E014 and E015, ten seeds). Sampling the next prefix from the empirical
   `P(prefix | previous final)` yields a *cleaner* coupling than the manuscript has. The
   real dependency is weaker or shared with other constraints; a generator must dilute it.
2. **Self-citation fails even with a folio-wide horizon.** With copies drawn uniformly
   from the whole folio history, near-duplicates still saturate the five-token window
   (+1.6 bits/token) because copies of copies cluster. The manuscript shows the opposite:
   its local copying is *below* what a frequency-driven vocabulary process (G5, −0.19)
   produces, and far below any self-citation process. Together with E014, simple
   copy/modify generation is excluded at every horizon tested.
3. **Within-folio vocabulary reuse is the discriminator the vocabulary process cannot
   fake.** G5 reproduces cross-folio sharing exactly (X 0.811 vs 0.818) with no folio
   structure at all, so X is weak; but the manuscript's folios reuse their own words more
   (F 0.242 vs 0.168). That matches upstream's "folio units carrying their own vocabulary"
   and is worth its own preregistered test with folio-shuffle nulls (candidate E016).
4. Line-position conditioning hurts much more in G5/G6 (−0.16) than in the manuscript
   (−0.026): the real text's suffix distribution is comparatively stable across line
   positions, i.e. the manuscript is *more* line-homogeneous than generators whose
   vocabulary grows.

## Consequences

- H022, H023 → FALSIFIED. The family-G candidates tested in E014/E015 (independent slots,
  unigram, local and folio-wide self-citation, edge-coupled with and without a growth
  process) are all excluded as full generators of the running text under signature v2.
- Signature v2 is now diagnostic against all tested generators; the E012 corpus stage can
  use it, with F as the component most likely to separate real texts from processes.
- Nothing here bears on meaning; the result constrains mechanisms, not content.

Claim ceiling: development-stage structural statements about generators; no Gate level.
