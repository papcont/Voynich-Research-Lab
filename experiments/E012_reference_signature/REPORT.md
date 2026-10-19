# E012 stage B-open — REPORT (interpretation, written after results.json)

**H027 FALSIFIED: no natural-language reference text matches the Voynich signature under
the script-agnostic Signature-G; every text is MISMATCH. H028 SUPPORTED: the signature is
exactly invariant under monoalphabetic substitution.** But the *reasons* for the mismatch
are not the ones predicted, and that is the result.

Plan `72f62d7`; one run; independent `validate.py` (own A3 coder path, copy model,
vocabulary statistics, permutations): `E012_VALIDATION_PASS`. Development stage; open-rights
texts only (Copiale German; Gutenberg Italian/English/German/French samples); Borg Latin
awaits approval. Primary surface: first 3,660 tokens of every text (size-matched).

## Signature-G, size-matched (A3 slots: first character · middle · last character)

| text | Δ_S′ first \| prev. last | Δ_L′ first+last \| line pos. | Δ_C copy W=5 | TTR | H1 | F excess | dJ order | verdict |
|---|---|---|---|---|---|---|---|---|
| **Voynich** | **+0.178** | **+0.061** | −0.283 | 0.393 | 0.703 | 0.019 | 0.015 | — |
| Copiale (de, real lines) | −0.052 | −0.038 | −0.303 | 0.355 | 0.663 | 0.043 | 0.014 | MISMATCH |
| Gutenberg it (re-segmented) | +0.010 | −0.045 | −0.211 | 0.451 | 0.745 | 0.028 | 0.013 | MISMATCH |
| Gutenberg en | −0.066 | −0.060 | −0.427 | 0.250 | 0.577 | 0.036 | 0.024 | MISMATCH |
| Gutenberg de | −0.056 | −0.052 | −0.377 | 0.327 | 0.656 | 0.033 | 0.013 | MISMATCH |
| Gutenberg fr | −0.048 | −0.044 | −0.499 | 0.359 | 0.685 | 0.056 | 0.015 | MISMATCH |
| substitution controls | identical to their plaintexts (max \|diff\| < 1e-9) | | | | | | | H028 ✔ |
| G4 edge-coupled generator | +0.022 | −0.020 | −0.475 | 0.366 | 0.633 | 0.005 | 0.007 | MISMATCH |

Nearest text to Voynich (tolerance-normalised L1): **Copiale**, not G4 as predicted.
Full-size values (secondary) are in `results.json`; Voynich full-size: Δ_S′ +0.168,
Δ_L′ +0.067, Δ_C −0.434.

## Predictions vs outcome — mostly wrong in detail, right in verdict

- Predicted: natural prose shows Δ_S′ > 0. **Observed: ≈ 0 or negative in every language.**
  Under a fair backoff coder, the last letter of a word carries no usable information about
  the first letter of the next word in German, English, French or Italian; the manuscript's
  coupling (+0.18 at matched size, +0.17 at full size) is an order of magnitude outside the
  natural range.
- Predicted: natural prose has Δ_C far above Voynich's (function-word repetition). **Observed:
  no natural text gains from the copy model either** (−0.21 to −0.50; Voynich −0.28). Local
  exact/one-edit copying is not a profitable description of any of these texts at W = 5.
- Predicted: TTR/H1 far below Voynich's. **Observed: comparable at matched size** (Voynich
  0.39/0.70 vs 0.25–0.45 / 0.58–0.75). At equal length the manuscript's vocabulary growth
  looks like prose; E014/E015's inventory contrast was against *generators*, not prose.
- H028 exact ✔. H027 FALSIFIED ✔ — on **Δ_S′** (all texts) and on **Δ_L′** (Copiale, the
  only reference with real manuscript lines, is negative; the manuscript is positive).

## Reading

1. **The edge coupling is the discriminator.** Across a word boundary, natural languages
   written one token per word decouple; the manuscript does not. Combined with E018 (the
   coupling is mostly `…y → qo…`, graded by section) this is the single structural fact
   that most separates the text from plain prose in four languages — consistent with
   upstream's exclusion of "natural language written one token per word" (their C132), now
   reproduced with an independent method.
2. **Line position is a second discriminator** where it can be tested: Copiale's real
   manuscript lines show no first/last-character line effect; the manuscript's do. For the
   re-segmented Gutenberg texts Δ_L′ is uninformative by construction (random lines), a
   design limitation recorded here.
3. **Vocabulary statistics do not separate the manuscript from prose at matched size.**
   The programme's inventory statements (E014/E015) must be read as "unlike simple
   generators", not "unlike language".
4. What this does *not* say: that the text is not language. A cipher or an encoding that
   couples adjacent words (e.g. a verbose cipher whose units straddle word boundaries, or a
   nomenclator with a carrier convention) could induce the coupling; family C with a real
   historical cipher (Borg, pending approval) and verbose designs remain to be scored.
5. Caveats: 3,660-token samples; modern literary prose in four samples (uppercase-
   normalised); only two language families; A3 slots are a coarse base; Copiale is a
   deciphered ritual text, not pharmaceutical prose.

## Consequences

- H027 FALSIFIED; H028 SUPPORTED. The structural inventory separates the manuscript from
  natural prose on edge coupling and line position, not on vocabulary.
- E012-B (Borg Latin recipes + its real simple-substitution ciphertext; verbose-cipher
  transforms of the open texts) is the obvious next registered extension; the Borg
  material waits for the human's approval of local analysis use.

Claim ceiling: signature similarity between texts; development stage; no decipherment, no
language identification, no Gate v2 level.
