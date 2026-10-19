# E020 — REPORT (interpretation, written after results.json)

**H030a SUPPORTED: the word-alignment fraction calibrated on Copiale (p\* = 0.8) transfers
to Italian — a verbose stream with 80% of word boundaries kept and 20% placed at random
gives the manuscript's cross-boundary coupling in both languages (0.200 / 0.162 vs 0.178).
H030b PARTIAL: only 2 of the other 6 components follow (F, dJ); line position, copying and
vocabulary do not. H030c SUPPORTED by the frozen rule — but the rule is confounded (see §3)
and the question it was meant to answer stays open.**

Plan `ed983a0`; one run; independent `validate.py`: `E020_VALIDATION_PASS`. Development
stage; open-rights sources; size-matched at 3,660 tokens.

## 1. Calibration (Copiale, verbose stream, MIX(p))

| p (word boundaries kept) | 0.0 | 0.2 | 0.4 | 0.6 | 0.7 | **0.8** | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|---|
| Δ_S′ | 0.488 | 0.454 | 0.377 | 0.326 | 0.277 | **0.200** | 0.129 | 0.008 |

Monotone, as expected; p\* = 0.8 (target 0.178).

## 2. Prediction on Italian at p\* = 0.8

| component | MIX(0.8) Italian | Voynich | within tol. |
|---|---|---|---|
| Δ_S′ | **0.162** | 0.178 | ✔ (H030a) |
| Δ_L′ | −0.014 | +0.061 | ✘ |
| Δ_C | −0.112 | −0.283 | ✘ |
| TTR | 0.601 | 0.393 | ✘ |
| H1 | 0.834 | 0.703 | ✘ |
| F excess | 0.012 | 0.019 | ✔ |
| dJ order | 0.005 | 0.015 | ✔ |

Predictions: p\* was predicted 0.5–0.7, observed 0.8; H030a SUPPORTED (predicted
SUPPORTED/PARTIAL ✔); H030b PARTIAL ✔; H030c predicted FALSIFIED, observed SUPPORTED by
rule — see §3.

## 3. Selectivity: the frozen rule measured the wrong thing

Top-1 previous-character share of the edge gain: Voynich 0.38 (class BOL), MIX 0.60 (class
"B"). The verbose table makes one symbol the dominant word-final symbol *by construction*
(word-aligned boundaries always end on the second symbol of a letter code), so MIX is
"more selective" than the manuscript by this measure; normalising for alphabet size
(`exploratory_post_run.json`: concentration 0.35 vs 0.17 with 9 positive classes each)
says the same. The rule therefore cannot test what E018 established — that the
manuscript's coupling is dominated by one *transition* (`…y → qo…`) — and H030c's
SUPPORTED is recorded as a measurement of the wrong quantity. A transition-level measure
(share of the coupling's mutual information carried by the top (previous-last, first)
pair, compared at equal alphabet size) is the corrected rule for a successor
preregistration; it is not applied here.

## 4. Reading

1. **A boundary process is sufficient for the coupling's *level*.** Keeping 80% of word
   boundaries and randomising 20% reproduces the manuscript's cross-boundary coupling
   across two languages at matched size — one calibrated parameter, out-of-sample
   transfer. This makes "token boundaries are mostly, not entirely, word boundaries" a
   quantitatively adequate account of *one* component.
2. **It is not sufficient for the rest.** Line position is absent (the manuscript's line
   edges behave differently from both word edges and random cuts), the local-copy cost is
   too small (fewer near-repeats than the manuscript), and vocabulary is far too rich
   (random cuts manufacture types). A verbose stream with random cuts cannot be the whole
   mechanism; neither can any transform tested in E019.
3. The manuscript's *selectivity* — one transition type carrying most of the coupling —
   remains the component no boundary process has reproduced, and it is the one most
   likely to encode the mechanism (a rule, not noise, decides where boundaries fall or
   what follows `y`).

## 5. Consequences

- H030a SUPPORTED; H030b PARTIAL; H030c SUPPORTED-by-rule with the rule retired
  (design limitation recorded). No family verdict changes.
- Successor: a boundary rule that is *selective* (e.g. boundaries conditioned on specific
  letter classes) on a verbose stream, tested against the transition-level selectivity
  measure; and the Borg real cipher when approved.

Claim ceiling: which boundary processes reproduce which structural components; development
stage; no decipherment, no language identification, no Gate v2 level.
