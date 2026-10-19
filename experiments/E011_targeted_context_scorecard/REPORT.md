# E011 — REPORT (interpretation, written after results.json)

**H014 SUPPORTED_DEV; H015 FALSIFIED_DEV.** Under a backoff universal coder, conditioning
the P70 **prefix slot** on the previous token's final glyph lowers out-of-fold description
length by **0.088 bits/token** (folio-mean; 95% bootstrap CI 0.073–0.102; 162/206 folios;
Currier A +0.035, B +0.166), against a feature-permuted null of −0.004. Conditioning the
prefix and suffix slots on line position **raises** description length (−0.026,
CI −0.042 to −0.011; CI upper < margin ⇒ falsified as a predictive component in this
shape).

Evidence class **DEVELOPMENT_CROSSFIT**: 5-fold cross-fit over all 206 running-text
folios, which all carry a SELECTION role in the holdout registry; **no Gate v2 level is
claimable**. `claim_E011_M_S.json` was run through `scripts/gate_report.py` and, as
expected, fails registration ("lockbox overlaps SELECTION folios", `GATE_REPORT_M_S.md`) —
the gate behaves correctly. Plan `24dc8c7`; margins (both 0.05, the floor, since the null
upper CI was below it) were computed and printed before the real contrasts; independent
`validate.py` (own coder, features, permutation, bootstrap): `E011_VALIDATION_PASS`.

## Numbers (out-of-fold bits/token, token-weighted; contrasts are folio-mean)

| model | bits/token | vs M0 (folio-mean Δ, CI) |
|---|---|---|
| M0 P70 plain KT (null) | 13.967 | — |
| **M_S** prefix \| previous final glyph | 13.829 | **+0.088** [0.073, 0.102] |
| M_Sfam prefix \| previous P70 suffix string | 13.813 | +0.106 [0.092, 0.120] (secondary) |
| M_L prefix+suffix \| line position | 13.961 | −0.026 [−0.042, −0.011] |
| M_SL | 13.868 | +0.030; vs M_S −0.057 (adding L hurts) |
| M_Sall all slots \| S (E008 shape) | 14.522 | −0.686 (slot targeting matters, as predicted) |

Control (within-folio token permutation, features recomputed): M_S 13.970 vs M0 13.967 —
the gain disappears when the sequence is destroyed, so it is sequence-specific.

Predictions vs outcome: H014 predicted SUPPORTED_DEV, larger in B, 0.05–0.3 — all three
met. H015 predicted small/INCONCLUSIVE — outcome was a clear negative. Secondary
predictions met (M_Sall < M_S; M_Sfam ≈ M_S, in fact slightly better).

## Exploratory decomposition (post-run, not gated; `exploratory_post_run.json`)

Share of the M_S gain by previous-final context: **line start (BOL) 28%** (0.34 bits/token
within that group), **y 22%** (top following prefix `qo`), **n 16%**, **r 13%**. So roughly
a quarter of the "edge state" gain is a line-initial effect that the L feature failed to
capture because H015 also conditioned the *suffix* slot, which costs more than it gains.
The y → qo shape of E002/H003 is visible but is not the whole story.

## What this means for the programme

- The previous token's final glyph is a real, modest predictor of the next token's
  *initial* class in ZL3b running text, strongest in Currier B. This is consistent with
  the E002 history and is now a development-stage, cross-fitted, coder-fair result.
  It says nothing about *why* (language, cipher state, or generator rule).
- Line position does not help once the prefix slot already sees `BOL` via S; conditioning
  the suffix slot on position is harmful under this coder.
- **New strongest structural null (development pool):** M_Sfam (13.813) / M_S (13.829)
  replace plain P70 (13.967) as the frozen null that any future running-text claim must
  beat (registered in `research/gate/registered_nulls.json`). For lockboxes outside running
  text the null must be re-fitted there.
- E008 (all-slot conditioning, no backoff) and E011 (slot-targeted, backoff) agree once
  the coder artefact is removed: information exists in S, not in C at W ≤ 5, and L is
  marginal to negative.

## Retraction conditions

H014's retraction condition (FALSIFIED_DEV) was not triggered. H015's was: line position
is dropped from the mechanism inventory in this shape; a prefix-only L test (without suffix
conditioning) would be a new hypothesis, not a rescue of H015.

Claim ceiling unchanged: structural, development-stage; no morphemes, language, cipher,
hoax or meaning; no Gate v2 level.
