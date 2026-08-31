# E006 — canonical final-chain holdout test (FROZEN PLAN)

Status: **PLAN_FROZEN**
Freeze rule: this file fixes every scientific choice **before** the confirmatory
holdout metric is computed. No target result on the holdout set has been
computed at freeze time. Occurrence *counts* of already-known development
tokens (frequency is a declared nuisance, not the target) were the only corpus
statistic inspected while writing this plan; the target statistic is context
similarity on the holdout set and remains uncomputed.

Hypotheses under test: **H007** (specific final chains have variable
attachment) and **H008** (canonicalizing that attachment improves *held-out
distant context similarity* beyond matched nulls).

---

## 1. Claim and scope

**Claim (H008):** For a narrow, predeclared grammar, the *fused* and *spaced*
surface realizations of the same canonical unit sequence occur in more similar
external contexts, on held-out folios, than matched null pairings predict.

**Scope:** ZL3b-n.txt only (upstream git-blob
`2a4533ab9bdfa85db9bad602d590978953055df1`). Parser
`src/voynichlab/canonical.py` @ this commit. No other transcription, no glyph
re-reading, no phonetic mapping.

**Claim ceiling (pass):** "some visible token boundaries are compatible with
variable attachment of a shared structural unit sequence." Explicitly **not**
morphology, phonetics, semantics, language identification, or plaintext.

---

## 2. Canonical grammar (frozen)

- STEMS = `ot`, `ok`, `qot`, `qok`
- FINALS = `ar`, `al`, `aiin`, `am`, `or`, `ol`
- A **canonical chain** C = (stem, f1, …, fk), k ≥ 1, parsed by
  `parse_fused_token` (greedy longest-match, whole-token exact).
- `edy`/`eedy` and any other unit are **not** added, before or after any
  target inspection.

**Primary test restricts to k = 2** (stem + exactly two finals), e.g.
`ot|ar|ar`, `ot|ar|al`, `ok|ar|ar`. This is where the discovery pairs live and
keeps the attachment boundary unambiguous. k ≥ 3 chains are **secondary /
exploratory** only.

---

## 3. Realizations (frozen)

For a k = 2 chain C = (stem, f1, f2):

- **FUSED**: one strict token whose whole surface parses exactly as C.
- **SPACED**: two consecutive strict tokens on the same line,
  token A parsing exactly as (stem, f1) and token B exactly equal to `f2`,
  with the separator between them being a **certain `.`** (uncertain `,` is
  excluded), and both tokens flagged non-uncertain by
  `iter_strict_tokens`.

"Strict token" = the non-uncertain tokens yielded by
`voynichlab.ivtff.iter_strict_tokens`.

---

## 4. Dependency unit and holdout split (frozen)

**Dependency unit:** physical folio (the IVTFF `folio` field, lowercased,
e.g. `f78r`). All resampling and uncertainty are folio-clustered. Tokens are
**not** treated as independent.

**Deterministic split** (stable, transcription-agnostic, computed without
looking at the target):

```
fold(folio) = int(sha256(folio.encode("utf-8")).hexdigest(), 16) % 5
DEVELOPMENT = folios with fold in {0, 1, 2}   # ~60%
HOLDOUT     = folios with fold in {3, 4}       # ~40%, confirmatory
```

Holdout is enlarged to two folds **because the fused chains are rare**
(`otarar` = 5 corpus-wide); this sizing decision is made now, from frequency
alone, never from the target metric. The holdout metric is computed **exactly
once**, after development is finalized. No tuning on the holdout after reveal.

---

## 5. Context definition (frozen)

For each realization occurrence, context is drawn from the folio's ordered
**strict-token stream** (all lines of that folio concatenated in file order),
**after removing the tokens that constitute the chain itself** (so fused vs
spaced cannot differ merely by their own consumed tokens). Context never
crosses folio boundaries (consistent with the dependency unit). This
cross-line-within-folio window is a deliberate simplification chosen for
reproducibility over fragile IVTFF paragraph reconstruction.

Two bands, by surface distance d (in strict-token steps) from the realization
span:

- **Band A (immediate):** d = 1 (left and right neighbor), weight **1.0**.
- **Band B (distant local):** 2 ≤ d ≤ 10, weight **0.5** (uniform within band).

Context features are neighboring strict-token **surface types** (no EVA
re-reading). Per (chain C, realization ∈ {fused, spaced}) a weighted context
distribution is built by pooling weighted context-type counts over all
occurrences in the fold under analysis, then normalizing.

---

## 6. Primary statistic (frozen)

Rarity forces **pooling across chains with equal per-chain weight** (a
single-chain per-fold test is unpowered):

1. Include a chain C in the holdout analysis iff it has ≥ **2** fused and ≥ **2**
   spaced occurrences within the holdout set (`n_min = 2`, frozen).
2. For each included C compute `JSD_fused_spaced(C)` =
   `voynichlab.metrics.jensen_shannon` between its fused and spaced weighted
   context distributions.
3. Primary observed statistic **D_obs = mean over included chains of
   JSD_fused_spaced(C)** (equal weight per chain, so a frequent chain cannot
   dominate).

Lower JSD = more similar context = support for shared-unit attachment.

If fewer than **3** chains qualify in the holdout, the result is declared
**INCONCLUSIVE (underpowered)** and H008 is neither supported nor falsified;
this branch is a legitimate preregistered outcome, not a failure to hide.

---

## 7. Null models (frozen)

Each null is folio-clustered and yields a distribution of D under the null via
≥ **1000** resamples (seed `20260831`):

- **N1 — frequency/section-matched random pairing.** Replace each spaced
  context distribution with that of a random *other* strict token matched on
  (frequency decile, Currier language of the occurrence), sampled within the
  holdout. Tests whether fused↔spaced similarity beats fused↔matched-random.
- **N2 — boundary-label permutation.** Within each folio, permute fused/spaced
  labels across occurrences of the same chain, preserving per-folio per-chain
  counts; recompute D. Tests whether the fused/spaced distinction carries
  context information beyond folio identity.
- **N3 — length-matched pseudo-canonicalization.** Pair each fused chain with a
  random non-canonical strict token of equal surface length and equal frequency
  decile; compute the same D. Tests whether the effect is specific to the
  canonical grammar.

Nulls preserve folio/section structure; they never shuffle the whole corpus
flat.

---

## 8. Decision rule (frozen, one-sided)

H008 is **supported on the holdout** iff **all** hold:

1. **Primary:** D_obs < 5th percentile of the N1 null distribution
   (one-sided empirical p < 0.05, folio-clustered).
2. **N2:** D_obs < 5th percentile of the N2 null (p < 0.05).
3. **Robustness:** leave-one-chain-out — removing any single qualifying chain
   still gives N1 p < 0.10 (effect not driven by one family).

H008 is **weakened/falsified** if the primary p ≥ 0.05, or the effect is
present only in Band A but absent in Band B (no distant transfer), or it
vanishes under N2, or a single leave-one-chain-out removal destroys it, or the
holdout is underpowered (§6 INCONCLUSIVE branch).

N3 is reported as specificity context (a canonical-vs-noncanonical contrast),
not part of the pass gate.

All p-values are reported exactly; no post-hoc metric substitution.

---

## 9. Degrees of freedom already fixed here

grammar, k = 2 restriction, realization rules, `.`-only separators, split
function, holdout = folds {3,4}, context bands and weights, feature =
surface-type bag, `n_min = 2`, ≥ 3-chain power floor, aggregation =
equal-weight-per-chain mean JSD, three nulls, ≥ 1000 resamples, seed
`20260831`, and the three-part decision gate. Development folds {0,1,2} may be
used only to confirm the pipeline runs and to sanity-check power — never to
choose any threshold above.

---

## 10. Confounds controlled

folio (dependency unit + split), Currier A/B (null matching), token frequency
(null matching + equal-weight aggregation), token length (N3), uncertain EVA
readings (excluded via strict tokens), certain vs uncertain separators
(`.`-only). Hand/section remain partially confounded with folio and are
absorbed by folio clustering; a hand-stratified re-analysis is deferred to a
secondary diagnostic.

---

## 11. Outputs (written next cycle, results before interpretation)

`results.json` (machine-readable: D_obs, per-null p-values, qualifying chains,
per-chain JSD, power branch) is written **before** any prose in `REPORT.md`.
