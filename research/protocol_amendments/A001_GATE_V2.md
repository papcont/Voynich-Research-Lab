# Protocol Amendment A001 — Decipherment promotion gate v2.0.0

- Amendment to: `RESEARCH_PROTOCOL.md` § "Decipherment promotion gate"
- Version: **gate_v2.0.0** (machine-readable: `research/gate/gate_v2.json`)
- Approved by: human operator, 2026-10-19 (with the methodological tightenings listed below)
- Effective: for claims registered after 2026-10-19T22:30Z
- **Non-retroactive.** E006, E007 (commits up to `1a00f03`), E008 (plan `9563bc4`, result
  `d12af64`) keep their original labels and evidence classes. Nothing in this amendment
  reinterprets a revealed result. Any re-evaluation of old material under v2 is a new,
  separately registered claim.

The original seven-point gate was qualitative ("substantial", "strong", "constrained").
v2 replaces it with independent, machine-checkable evidence levels, a fair compression test
against the strongest frozen null, mandatory negative controls, holdout protection,
transliteration robustness, independently checkable semantics and mandatory falsification.
Implementation: `src/voynichlab/gate.py`; tests: `tests/test_gate.py`; report:
`scripts/gate_report.py`; holdout audit: `scripts/holdout_audit.py` →
`research/holdout_registry.json`.

## 1. Evidence levels (independent states)

| level | meaning | own evidence |
|---|---|---|
| `STRUCTURAL_MODEL_VALIDATED` | a fixed, lossless model of the observed text beats the strongest frozen null on a lockbox | compression test (§2) |
| `DECODING_MECHANISM_SUPPORTED` | a deterministic, executable mechanism producing a fixed plaintext passes the compression test **and** the specificity controls (§3) | + mechanism block, controls |
| `LANGUAGE_IDENTIFICATION_SUPPORTED` | the mechanism's plaintext is better predicted by one language's fixed, independently trained model than by ≥ 3 alternatives, with CI, and not on generator controls | + language block |
| `SEMANTIC_DECODING_SUPPORTED` | pre-registered, text-derived statements survive matched wrong-page controls at Holm-corrected p ≤ 0.01 with a pre-registered minimum effect | + semantic block |
| `DECIPHERMENT_CONFIRMED` | all of the above, plus independent replication, transliteration robustness and an un-triggered retraction condition | + confirmation block |

States per level: `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_TESTED`. A level can be `PASS` only
if every lower level is `PASS`. **A compression pass never promotes a language or semantic
level**; those stay `NOT_TESTED` until their own evidence exists.

## 2. Fair compression test (MDL on the observed text)

- What is scored is the **description length of the observed Voynich lockbox text** under the
  candidate, in bits per token, against the strongest frozen null registered for that
  lockbox (currently P70 layer A, E007). The historical P70 values 15.03 (global) and
  14.42 (dev→holdout) are references, **not** pass thresholds. Perplexity of a produced
  plaintext is not evidence.
- The candidate must reconstruct the observed text exactly (sha256 of reconstruction =
  sha256 of lockbox text); otherwise the level is `NOT_TESTED`.
- `total_candidate_bits = data_bits + mechanism_code_bits + dictionary_bits + key_bits +
  exception_bits + residual_bits + transmission_bits`. All six components must be declared
  (≥ 0); a missing component is a `FAIL`.
- Dependency unit = folio. Statistic = mean over lockbox folios of the per-folio paired
  difference (null − candidate, bits/token); percentile bootstrap (10,000 resamples, seed
  20261019) gives the two-sided 95% interval.
- Provisional margin **0.5 bits/token**. The margin must be calibrated and justified on
  development data only and stated in the claim record; a margin calibrated on lockbox
  data is a `FAIL`.
- Decision: `PASS` iff n_folios ≥ 20 **and** mean ≥ margin **and** CI lower bound > 0;
  `FAIL` iff n_folios ≥ 20 and CI upper bound < margin; otherwise `INCONCLUSIVE`.
  **Lack of power is `INCONCLUSIVE`, never `PASS`.**

## 3. Negative controls (specificity)

The *unchanged* candidate is evaluated, against the same null, on three control texts:
folio-internal permutation of the real tokens, statistically matched synthetic text, and an
established non-semantic generator. If its gain on any control is ≥ (real gain − margin),
specificity fails: the candidate gains for reasons unrelated to content (it is at most a
structural model, level 1). For semantic claims, each prediction family needs a
pre-registered minimum effect over matched wrong pages **and** a permutation p-value
(≥ 99 permutations, +1 correction) with Holm correction across families, target α = 0.01.

## 4. Holdout protection and lockboxes

`scripts/holdout_audit.py` records for every running-text folio which experiment used it
and in what role (`SELECTION` = model/parameter/threshold selection or error analysis;
`EVALUATION` = a revealed target metric). Result (2026-10-19, `research/holdout_registry.json`):

- 168 of 206 running-text folios were development (`SELECTION`) folios in E006 and/or
  E007/E008 (two different hash splits, each 60% development).
- **Erratum (same day, before any use):** the E008 post-reveal *exploratory* backoff-coder
  analysis (`experiments/E008_mechanism_competition/exploratory.py`) was trained on the
  E007 development folds and scored on the E007 holdout folds — which contain all 38
  remaining folios — and its result motivated the E011 design. Under §4's strict rule that
  is error analysis = `SELECTION`. Consequently **no running-text lockbox exists in ZL3b.**
  The first registry version (commit `ac3ebc7`) listed a 38-folio `LOCKBOX_RUNNING_SEMI_V1`;
  it is withdrawn and replaced by `DEVELOPMENT_POOL_RUNNING_V1` (all 206 folios,
  `DEVELOPMENT_ONLY`). Running-text hypotheses can be *developed* here with internally
  cross-fitted, folio-level estimates and development-stage labels; they cannot reach any
  Gate v2 level without new data.
- `LOCKBOX_NONRUNNING_V1` — label/circular/radial loci (39 folios, 710 tokens), sha256
  `6c7ae533…`. **Erratum 2 (2026-10-20, E013):** first listed `INDEPENDENT`; the gate's
  registration check correctly flagged that these tokens lie on folios whose running text
  carries `SELECTION` roles, and the dependency unit is the folio. Reclassified
  `SEMI_INDEPENDENT`; the E013 claim therefore fails registration and is development-stage.
- **Consequence:** under the folio rule ZL3b offers *no* independent confirmation lockbox for
  any claim. Confirmation surfaces must be registered by a human from outside (a future
  transliteration release with independent readings, newly transcribed material), or the
  protocol must be amended with an explicit semi-independent tier for candidates that were
  not developed on these folios (a human decision; not taken here).

A claim names its `lockbox_id`; overlap with any `SELECTION` folio is a registration
`FAIL`; a `SEMI_INDEPENDENT` lockbox is flagged in every report. Splits, inputs,
configuration and predictions are registered by sha256 in a commit that precedes the
first final evaluation.

## 5. Transliteration robustness

Confirmation requires ZL3b **plus IT2a** (Takahashi, IVTFF 2a) and, where available,
GC/v101, on aligned loci only, with glyph-interpretation differences documented and
results reported separately for clear and uncertain passages. Sources are declared in
`data/sources.yml` (`scripts/fetch_transliteration.py`); the IT2a/GC hashes are **not yet
registered** because `voynich.nu` was unreachable from the 2026-10-19 environment and the
files are not in `matthewdgreen/cipher_benchmark`. Until a verified hash exists, the
confirmation level cannot be reached by anyone.

## 6. Independently checkable semantics

Text-derived statements are hash-registered **before** the illustrations of the tested pages
are inspected. Each statement family is tested against matched wrong pages, including
controlled permutations within similar sections. Reports separate (a) semantic
plausibility, (b) independent-rater agreement, (c) verifiable text statements. No true word
error rate may be claimed (no known plaintext exists); error rates are measured on synthetic
positive controls and labelled as such. Every decode claim reports coverage %, undetermined-
word % and an evidence-quality tier.

## 7. Mandatory falsification

Every registered claim carries a `retraction_condition`. No post-hoc exceptions, no change
of scoring method, no retuning after the final lockbox is opened (`post_reveal_changes =
true` ⇒ `FAIL`).

## 8. Machine-checkable implementation and tests

`tests/test_gate.py` contains synthetic positive and negative cases: a genuine mechanism
(a coder that knows how a synthetic Markov ciphertext was generated) passes levels 1–2 and
leaves 3–5 `NOT_TESTED`; a full planted chain passes all five; a readable-output decode with
no compression gain fails; a gain that survives permutation is a structural model but not a
mechanism; under-powered or imprecise claims are `INCONCLUSIVE`; lockbox-calibrated margins,
missing model-bit components, missing reconstruction, missing retraction conditions,
post-reveal changes, lockbox overlap with selection folios, unregistered predictions,
claimed word error rates, Holm-failing families and missing replication/transliteration all
fail at the right level.

## Known limitations and open methodological risks

1. There is no running-text lockbox in ZL3b at all (see §4 erratum). A genuinely blind
   confirmation of any running-text claim needs data outside ZL3b running text or a newly
   released transliteration with independent readings; until then every running-text
   result is development-stage.
2. The 0.5 bits/token margin is provisional and must be re-justified per claim on
   development data; the gate checks the provenance of the justification, not its quality.
3. Specificity controls can be gamed by weak controls; the registry of accepted generator
   nulls is a human responsibility (see `external/repos.yml`).
4. Language identification depends on the quality and independence of the reference
   corpora; provenance and licensing of those corpora are open (no corpus fetched yet).
5. Semantic permutation tests are only as good as the "matched wrong pages" construction;
   section/illustration confounds must be controlled in the registration.
6. The gate validates claim *records*; it cannot verify that the numbers in a record were
   produced honestly. Reproduction scripts and hashes are required for that, as before.
