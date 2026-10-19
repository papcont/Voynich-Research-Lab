# E014 — REPORT (interpretation, written after results.json)

**No tested generator reproduces the Voynich component signature. H020 (self-citation)
FALSIFIED; H021 (edge-coupled slot generator) PARTIAL.** The signature is diagnostic
against the four generators tested, but only narrowly against the edge-coupled one.

Plan `9ce3637`; one run (5 seeds per generator); independent `validate.py` re-scores every
generated text with its own coders: `E014_VALIDATION_PASS`. Evidence class
MECHANISM_DEMONSTRATION / DEVELOPMENT; no Gate level. The Voynich reference values are
EXPLORATORY (their components were measured before in other protocols).

## Signature (folio-mean bits/token; generators: mean over 5 seeds, SD in brackets)

| text | Δ_S prefix \| prev. final | Δ_L line position | Δ_C copy W=5 | TTR / hapax | verdict |
|---|---|---|---|---|---|
| **Voynich** (ZL3b running text) | **+0.088** [CI 0.073, 0.102] | **−0.026** [−0.042, −0.011] | **−0.463** [−0.49, −0.43] | 0.193 / 0.669 | — |
| G1 independent P70 slots | −0.004 (0.0005) | −0.297 (0.010) | −0.290 (0.010) | 0.321 / 0.737 | MISMATCH |
| G2 token unigram | −0.004 (0.001) | −0.100 (0.003) | −0.447 (0.011) | 0.142 / 0.392 | PARTIAL (S 0.091, L 0.074) |
| G3 self-citation (p_copy 0.5, p_edit 0.6) | −0.005 (0.001) | −0.158 (0.002) | **+2.93** (0.13) | 0.298 / 0.622 | MISMATCH |
| G4 edge-coupled slots | **+0.144** (0.002) | −0.041 (0.008) | −0.444 (0.008) | 0.140 / 0.399 | PARTIAL (S 0.056) |

Predictions: G1 MISMATCH ✔; G2 predicted MISMATCH, got PARTIAL (its Δ_S gap 0.091 falls
just under the 0.10 mismatch threshold); G3 MISMATCH ✔ (on C and S, as predicted); G4
"MATCH or PARTIAL" ✔ (PARTIAL).

## Reading

1. **Simple self-citation is excluded as the whole story.** Calibrated to come as close as
   the grid allows to Voynich's type/token and hapax statistics, a copy-with-one-edit
   generator leaves a local-copy signal of ≈ 3 bits/token at W = 5; the real text has
   none (−0.46, the pure cost of the copy slot). This agrees with E008 (no locality-specific
   gain), with the real text's chance-level adjacent repetition reported by epilectrik,
   and it falsifies H020. A self-citation mechanism would need a much longer or
   non-local copying horizon and some other source of the edge coupling to survive.
2. **Edge coupling is cheap to fake, but the fake overshoots.** G4 reproduces the line-
   position loss and the absent copy gain exactly and *over*-produces the edge-state gain
   (0.144 vs 0.088): the real text's coupling is noisier than the empirical
   `P(prefix | previous final)` applied deterministically. The three-component signature
   therefore separates Voynich from G4 by only 0.056 bits/token on one component — weak.
3. **Inventory statistics discriminate far more strongly.** Every generator that samples
   real tokens with replacement (G2, G4) has TTR ≈ 0.14 and hapax ≈ 0.40 against Voynich's
   0.193 / 0.669; the slot generator (G1) overshoots the other way (0.32 / 0.74). Type-
   inventory growth is the obvious fourth component for E012, together with the
   folio-level vocabulary sharing and the order-information-beyond-edge measurements that
   upstream work already uses.
4. The whole-token coder's bits/token differ across texts (Voynich 13.97; G2/G4 ≈ 12;
   G1 17.9; G3 19.7), so absolute compressibility is not comparable and was not used.

## Consequences

- H020 → FALSIFIED (simple self-citation generator). H021 → PARTIAL: an edge-coupled slot
  generator matches L and C and overshoots S; recorded as a near-miss, not a match.
- E012 (reference corpora) should add inventory-growth and vocabulary-sharing components
  before any family readout; otherwise shallow generators sit too close to the real text
  on the three components alone.
- No generator tested here reproduces the manuscript; nothing here concerns meaning.

Claim ceiling: which simple generators reproduce which structural components; development
stage; no Gate v2 level.
