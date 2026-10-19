# E019 — cipher/encoding transforms of open-rights prose under Signature-G (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E019 metric has been computed.** Evidence class:
MECHANISM_DEMONSTRATION / DEVELOPMENT; no lockbox; no Gate level. The Voynich and
plaintext Signature-G values are known from E012 (EXPLORATORY here).

## 1. Question

E012 found that the manuscript differs from natural prose on **edge coupling** (first
character | previous token's last character: +0.178 vs ≈ 0) and **line position**, not on
vocabulary. Which simple encodings of prose, applied to the same open-rights texts, move
these components toward the manuscript? In particular: does **re-cutting a continuous
letter stream into tokens** (token boundaries that are not word boundaries) produce the
coupling?

## 2. Source texts and transforms (frozen; seeds 20261090 + index)

Sources: **N_DEU** (Copiale, real manuscript lines) and **N_ITA** (Gutenberg Italian,
re-segmented as in E012), each prepared exactly as in E012 (normalization, units, lines,
size matching at 3,660 tokens *after* transformation where token counts change).

| id | transform | what it preserves / breaks |
|---|---|---|
| C_HOMO | homophonic substitution: each letter gets ⌈3·freq/maxfreq⌉ homophones (1–3), one drawn uniformly per occurrence; homophones are new symbols | word boundaries, lengths; breaks character identity across occurrences |
| C_VERB | verbose substitution: each letter → a fixed two-symbol unit from a deterministic table (26×2 symbols over a 10-symbol alphabet, injective) | word boundaries; doubles token length; keeps all sequence structure |
| C_STREAM | **stream re-cut**: within each line, remove word boundaries, then cut the letter stream into tokens whose lengths are drawn from ZL3b's empirical running-text token-length distribution (seed) | letters and lines; breaks word boundaries — token boundaries become arbitrary |
| C_STREAM_VERB | C_VERB followed by C_STREAM | as above, on the verbose stream |

Plaintext references (from E012, re-used): N_DEU, N_ITA. Voynich reference: E012's
size-matched V.

## 3. Signature and decisions (frozen)

Signature-G exactly as E012 (A3 slots; `voynichlab.signature`, `slot_fn=a3_slots`), on
the first 3,660 tokens of each transformed text; E015 tolerances; MATCH / PARTIAL /
MISMATCH per transformed text against V.

- **H029a** (stream re-cut reproduces the edge coupling): `SUPPORTED` iff Δ_S′ of
  C_STREAM is ≥ 0.05 for **both** sources and within 0.10 of Voynich's for at least one;
  `FALSIFIED` iff Δ_S′ of C_STREAM < 0.05 for both; else `PARTIAL`.
- **H029b** (some cipher transform MATCHes the manuscript on all components): `SUPPORTED`
  iff any transformed text is MATCH; `FALSIFIED` iff all are MISMATCH; else `PARTIAL`.

Pre-result predictions: C_HOMO and C_VERB: Δ_S′ stays ≈ 0 (MISMATCH on edge coupling; C_HOMO
raises TTR/H1). C_STREAM: Δ_S′ clearly positive (letter-bigram information crosses the
arbitrary boundary) — predicted 0.1–0.4, i.e. H029a SUPPORTED or PARTIAL; its TTR/H1 rise
well above Voynich's (random cuts multiply types) and its line effect stays ≈ 0, so
H029b FALSIFIED: no single transform matches everything. If C_STREAM's coupling lands
near the manuscript's, "token boundaries are not word boundaries" becomes a registered
candidate component of any family-C/M proposal, to be tested against the y → qo
specificity (E018) next.

## 4. Degrees of freedom, retraction

None free (tables, homophone rule, length distribution and seeds fixed). H029a FALSIFIED
retires the stream-cut idea as a source of the coupling.

## 5. Registration and claim ceiling

`experiment.json` records sha256 of inputs (E012 corpus hashes), config and predictions.
Claim ceiling: which encodings of prose reproduce which structural components; no
decipherment, no language identification, no Gate level.
