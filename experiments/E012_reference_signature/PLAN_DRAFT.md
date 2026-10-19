# E012 — mechanism-family signature comparison on reference texts (stage B)
Status: **DRAFT v2 — concrete corpus proposal; nothing computed; awaiting the human corpus decision**

## What changed since v1
E014–E018 established signature v3 (`voynichlab.signature`, seven components, regression-
tested) and excluded the simple family-G generators. The missing piece is family N and C
reference material. **It is already in hand, with documented provenance, no network needed:**
the ZL3b source repository `matthewdgreen/cipher_benchmark` (read-only clone, pinned in
`external/repos.yml`) carries natural-language plaintexts *and real historical ciphertexts
with known plaintext*, each with a `rights_class` in its manifest.

## Proposed reference texts (local files; never committed; hashes of the concatenated files)

| id | family | text | tokens | lines | rights_class (benchmark manifest) | sha256 (prefix) |
|---|---|---|---|---|---|---|
| **N_LAT** | N | Borg plaintext — 17th-c. Latin pharmaceutical recipes (MSS Borg.lat.898; plaintext from Aldarrab–Knight–Megyesi, Stockholm Univ.) | 27,032 | 399 (page/paragraph-level, not manuscript lines) | `linked_only` (plaintext = research data; images Vatican) | `a1057341920dadb5` |
| **N_DEU** | N | Copiale plaintext — 18th-c. German ritual text | 13,712 | 1,823 (manuscript lines, ≈ 7.5 tokens) | `open` | `1f93e9902ac068f2` |
| N_ITA / N_ENG / N_DE2 / N_FRA | N | Gutenberg prose samples (Manzoni/Collodi; Austen/Dickens/Doyle; Kafka/Mann; Hugo/Flaubert) | 3,660 each | 30 | `open` | `1cc3c7d4…`, `fad46190…`, `0b1a0600…`, `9b119dc6…` |
| **C_BORG** | C | Borg **real ciphertext**, canonical S-token transcription, letter-level simple substitution (34 symbols), word boundaries preserved | ≈ 27k words | as plaintext | `linked_only` | to be hashed |
| C_COP | C | Copiale real homophonic ciphertext — **no word boundaries** in the cipher stream | — | — | `open` | token-level signature not defined; letter-level only, reported |
| C_SUB(N_DEU) | C | our own monoalphabetic substitution of N_DEU (control preserving all sequence structure) | 13,712 | as N_DEU | derived | — |
| G_* | G | E014/E015 generators on the ZL3b skeleton (already computed) | 33,611 | ZL3b | — | — |
| V | — | ZL3b running text (EXPLORATORY for the components already measured; new for the generic variant) | 33,611 | 4,075 | — | — |

**The one question for the human:** may the `linked_only` Borg plaintext and ciphertext be
used *locally, for analysis only, never committed or redistributed* (CLAUDE.md rule 12
concerns redistribution; the benchmark's class reflects image/transcription rights held by
third parties)? If not, E012 runs on Copiale + Gutenberg + our substitution control only.

## Script-agnostic signature (to be frozen)
P70 slots exist only for Voynichese. For cross-script comparability the generic variant
**Signature-G** uses E007's fixed cuts **A3** (first character, middle, last character) as the
slot base for *every* text including Voynich, and otherwise the frozen component definitions:
Δ_S′ (first-character slot | previous token's last character, BOL/UNC; backoff coder),
Δ_L′ (first and last slots | line position), Δ_C (copy model, W = 5), TTR, H1, F excess
(stratified by the text's own "folio" units: Borg pages, Copiale pages, Gutenberg test
chunks, ZL3b folios), dJ_order. For N_LAT the page-level lines are re-segmented to ZL3b's
line-length distribution (seeded) so BOL/L are comparable; this is declared and the
unsegmented version reported.

## Decisions (to be frozen)
Per reference text: distance to Voynich on Signature-G with the E015 tolerances
(bits 0.05/0.10, fractions 0.02/0.05) → MATCH / PARTIAL / MISMATCH; family readout by the
nearest text, **only ordinal**, with the explicit caveat that two reference languages and one
real cipher system do not span the families. Pre-result predictions (to be written at
freeze): natural prose shows Δ_S′ > 0 (letter phonotactics across word boundaries) and
*high* local repetition (function words) → Δ_C above Voynich's; the real substitution
cipher preserves all of that exactly (C_BORG ≈ N_LAT on every component); Voynich's
combination (edge gain, *no* local copying, high hapax, folio-local vocabulary) is predicted
to MISMATCH every natural text on Δ_C and TTR/H1.

## Falsification
If a natural-language text MATCHes Voynich on Signature-G, the signature cannot separate
family N from the manuscript and the programme's structural inventory is non-diagnostic
for N (negative result, recorded).

## Claim ceiling
Signature similarity between texts; no decipherment, no language identification, no Gate level.
