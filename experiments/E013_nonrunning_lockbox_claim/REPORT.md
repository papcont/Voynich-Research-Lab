# E013 — REPORT (interpretation, written after results.json)

**Gate v2 verdict: registration FAIL — no level earned.** The gate's holdout check found that
the 39 lockbox folios all carry `SELECTION` roles through their running text (E006/E007/E008
development folds), and the dependency unit is the physical folio. The registry had
classified the label/circular/radial tokens `INDEPENDENT` because no experiment had ever
coded them; that was too generous and is corrected (A001 erratum 2, registry regenerated).
E013 is therefore a **development-stage transfer result**, not a confirmation.

**Compression statistics (as frozen, now development-stage):** P70 four-slot model vs the
registered whole-token null on the 710 label/circular/radial tokens, pure prequential from
empty counts with model bits charged: **Δ = 2.20 bits/token** (folio-mean, 95% bootstrap
CI 0.99–3.50; 30/39 folios), above the 0.5 margin with CI > 0 — the compression test itself
would read PASS. Pre-result prediction (PASS, 1–4 bits/token) met. **STRICT_PASS false:**
two simpler factorizations describe labels better from scratch — **A6** (P70 without the
suffix slot) 26.39 total bits/token and **A1** (prefix + rest) 27.48 vs P70 28.40.

Plan `15f72da`; one run; independent `validate.py` (own segmenters, coder, bootstrap):
`E013_VALIDATION_PASS`. Gate report: `GATE_REPORT_P70.md`.

## Numbers (primary arm, total bits/token = data + model bits / 710)

| model | data | model bits | total |
|---|---|---|---|
| A6 no suffix | 26.13 | 183 | **26.39** |
| A1 prefix + rest | 27.37 | 78 | 27.48 |
| **P70** | 27.44 | 681 | 28.40 |
| A7 ch/sh not prefix | 27.98 | 681 | 28.94 |
| A5 no gallows | 28.18 | 679 | 29.14 |
| A3 fixed cuts | 29.76 | 3 | 29.77 |
| A8 random 4-slot | 30.33 | 54 | 30.41 |
| **A0 whole token (null)** | 30.56 | 1 | **30.56** |
| A2 rest + suffix | 30.34 | 499 | 31.04 |

Secondary arm (counts trained on running text, then frozen): P70 21.35 < A7 21.52 < A5
21.86 < A6 21.91 < A8 22.00 < … < A0 24.16 — with running-text statistics available, P70 is
best; from scratch on 710 short, mostly unique tokens (529 types, |Σ| = 20), the suffix
inventory (34 strings, ≈ 500 bits) and the extra slot cost more than they save.
Within-folio permutation control: identical totals (a token-internal model is order-free, as
expected). Natural-order sensitivity: P70 27.43, A0 30.55 (unchanged ranking).

## What this means

1. **Structure transfers, the exact shape does not.** Label text is also better described by
   a prefix-based factorization than by whole tokens, by about 2 bits/token; but on labels the
   suffix slot is dead weight. Labels are short (median length 5, 78 one-character tokens),
   rarely repeat, and largely lack the `-y/-dy/-aiin` endings of running text. This is a
   structural difference between labels and running text, consistent with E007's note that
   the two populations should not be pooled.
2. **The gate worked as intended — against us.** A claim we expected to pass was stopped at
   registration because the folio rule is stricter than our registry labelling. That is the
   right outcome: the label tokens are not independent of the running text on the same pages
   (shared scribe, section, vocabulary).
3. **Under the folio rule, ZL3b has no independent lockbox at all.** Every Voynich folio with
   text appears in ZL3b and every running-text folio was used for selection. Gate v2
   confirmation of anything developed here now needs either data from outside ZL3b
   (independent readings in a new transliteration, newly transcribed material) or a human
   protocol decision creating a semi-independent tier for candidates not developed on these
   folios. Neither is taken here.

## Hypothesis status

H019 → **SUPPORTED_DEV** (development-stage; registration failed, so no Gate level). The
retraction condition (gate FAIL on the compression test) was not triggered; the registration
failure is a classification error on our side, recorded as such. Registered null for the
pool stays A0 (nothing passed registration); A6's superiority is recorded for a future
preregistration if a suitable surface appears.

Claim ceiling: structural, development-stage; no Gate v2 level; nothing about meaning.
