# E017 — REPORT (interpretation, written after results.json)

**H025b SUPPORTED_DEV: consecutive folios in the current order share vocabulary beyond an
order-permutation null that keeps every folio's vocabulary intact (ΔJ = +0.013, p < 0.001,
positive in Currier A +0.016 and B +0.011). H026 FALSIFIED_DEV: the two sides of one leaf
do not share more than facing pages (D = +0.004, p = 0.33).**

Plan `54ab005`; one run; independent `validate.py`: `E017_VALIDATION_PASS`. Development
stage; the overall adjacency excess was EXPLORATORY-known from E016's post-run check, the
Currier split and the leaf split are new.

## Numbers

| quantity | value |
|---|---|
| adjacent same-stratum pairs (both folios ≥ 20 tokens) | 151 (same-leaf 100, facing 44, other 7) |
| J_adj observed | 0.1229 |
| order-permutation null (within strata, 1,000) | 0.1095 (97.5% 0.1128) |
| **excess ΔJ** | **+0.0133**, p < 0.001 |
| by Currier: A / B | +0.0156 / +0.0106 |
| J same-leaf / facing / other | 0.1256 / 0.1214 / 0.0925 |
| D = same-leaf − facing | +0.0042 (label-permutation null 0.000, 97.5% 0.018), p = 0.33 |

## Reading

1. **Vocabulary is local along the present folio order**, modestly: neighbouring folios
   share about 12% of their types against 11% for order-permuted neighbours of the same
   language and section. The effect holds in both Currier languages. It is small next to
   folio-local reuse (E016) but consistent and well-powered.
2. **Leaf structure adds nothing.** Recto → verso of one leaf (0.126) and verso → next recto
   (0.121) are indistinguishable; both are well above non-consecutive pairs ("other",
   0.093, mostly across numbering gaps). The text does not treat the physical leaf as a unit
   of vocabulary any more than the page turn. Upstream's bifolium claim (partners on the
   same sheet share, facing pages do not) cannot be tested without collation data; what we
   can say is that *facing pages do share* beyond order-permuted neighbours here, which
   does not match the "facing pages do not share" part of that claim at face value, though
   the statistics differ (they control distance and length explicitly).
3. The two prior misreadings are both resolved: E016's H025 null was wrong (recorded), and
   with the right null the effect is real but small.

## Consequences

- H025b SUPPORTED_DEV; H026 FALSIFIED_DEV (leaf is not a vocabulary unit beyond adjacency).
- Structural inventory now: four-slot token form; edge state → next prefix; no local
  copying; line homogeneity; folio-local vocabulary; weak codex-order locality. Any
  mechanism proposal — language, cipher, or generator — must produce all six.
- A bifolium/quire test requires registered collation data (human decision; none here).

Claim ceiling: structural statement about the current order; no quire, binding, or meaning
claims; no Gate v2 level.
