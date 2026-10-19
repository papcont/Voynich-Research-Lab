# E019 — REPORT (interpretation, written after results.json)

**H029a PARTIAL: re-cutting a continuous letter stream of prose into Voynich-length tokens
produces a cross-boundary coupling of the right sign but far too strong (Δ_S′ 0.43–0.46
vs the manuscript's 0.18). H029b FALSIFIED: no transform matches the manuscript on all
components.** The manuscript's coupling sits *between* word-aligned boundaries (≈ 0 in
all prose, E012) and arbitrary cuts in a natural letter stream.

Plan `290ecdc`; one run; independent `validate.py` (E012's independent Signature-G path):
`E019_VALIDATION_PASS`. Development stage; open-rights sources only (Copiale German with
real lines; Gutenberg Italian re-segmented); size-matched at 3,660 tokens.

## Signature-G, size-matched

| text | Δ_S′ | Δ_L′ | Δ_C | TTR | H1 | F excess | dJ | verdict |
|---|---|---|---|---|---|---|---|---|
| **Voynich** (E012) | **+0.178** | **+0.061** | −0.283 | 0.393 | 0.703 | 0.019 | 0.015 | — |
| Copiale plaintext (E012) | −0.052 | −0.038 | −0.303 | 0.355 | 0.663 | 0.043 | 0.014 | MISMATCH |
| C_HOMO (de) homophonic 1–3 | −0.163 | −0.054 | −0.247 | 0.572 | 0.833 | 0.017 | 0.007 | MISMATCH |
| C_VERB (de) verbose 2-symbol | +0.008 | −0.026 | −0.143 | 0.355 | 0.663 | 0.043 | 0.014 | MISMATCH |
| **C_STREAM (de)** stream re-cut | **+0.433** | **+0.048** | −0.344 | 0.806 | 0.900 | −0.003 | 0.000 | MISMATCH |
| C_STREAM_VERB (de) | +0.553 | +0.043 | −0.286 | 0.575 | 0.733 | 0.001 | 0.002 | MISMATCH |
| Italian plaintext (E012) | +0.010 | −0.045 | −0.211 | 0.451 | 0.745 | 0.028 | 0.013 | MISMATCH |
| C_HOMO (it) | −0.202 | −0.060 | −0.250 | 0.737 | 0.902 | 0.005 | 0.002 | MISMATCH |
| C_VERB (it) | −0.002 | −0.028 | −0.042 | 0.451 | 0.745 | 0.028 | 0.013 | MISMATCH |
| **C_STREAM (it)** | **+0.460** | **+0.049** | −0.179 | 0.843 | 0.917 | 0.003 | 0.002 | MISMATCH |
| C_STREAM_VERB (it) | +0.421 | +0.038 | −0.237 | 0.586 | 0.745 | 0.006 | 0.000 | MISMATCH |

Predictions: C_HOMO/C_VERB ≈ 0 coupling ✔ (C_HOMO in fact strongly negative: homophones
fragment the boundary alphabet); C_STREAM strongly positive ✔ but above the predicted
0.1–0.4 range; vocabulary explodes ✔; H029b FALSIFIED ✔. Not predicted: the stream re-cut
also produces a **line-position effect of the manuscript's size** (+0.04–0.05 vs +0.061),
because line-initial and line-final "tokens" keep real word edges while mid-line cuts are
arbitrary — the manuscript's line effect is thus reproducible by boundaries that are
word-aligned at line edges and arbitrary inside.

## Reading

1. **Boundary placement is the lever.** Nothing that keeps word boundaries (homophonic,
   verbose, monoalphabetic) produces the manuscript's coupling; cutting through words
   produces too much of it. A text whose token boundaries are *partly* word-aligned (or
   whose underlying stream has weaker adjacent-unit dependence than natural letters) would
   land in between. This is a quantitative, testable constraint for any family-C or
   family-M proposal: the boundary process must deliver Δ_S′ ≈ 0.18 at matched size while
   keeping TTR ≈ 0.39 and H1 ≈ 0.70 — and, per E018, concentrate the coupling in one
   transition type (`…y → qo…`), which random cuts in a letter stream would not.
2. **Verbose encoding brings vocabulary back toward the manuscript** (C_STREAM_VERB: TTR
   0.58–0.59, H1 0.73–0.75 vs 0.39/0.70) while keeping the coupling too high; homophony
   pushes vocabulary the wrong way. The combination "verbose + partly-aligned cuts" is the
   obvious next transform family, with the alignment fraction calibrated on Δ_S′ and the
   other six components then tested as predictions (E019-B).
3. The manuscript's *selectivity* (one dominant transition, graded by section) remains
   unexplained by any transform here; all stream cuts spread the coupling over the whole
   bigram table.

## Consequences

- H029a PARTIAL, H029b FALSIFIED. "Token boundaries are not (all) word boundaries" is
  registered as a candidate component with a quantitative target, not as a finding.
- E019-B: mixture transforms (fraction of word-aligned boundaries; verbose + mixture) with
  calibration-then-prediction design; Borg's real ciphertext when approved.

Claim ceiling: which encodings of prose reproduce which structural components; development
stage; no decipherment, no language identification, no Gate v2 level.
