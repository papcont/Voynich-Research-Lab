# E007 — Preflight Amendment 001 (pre-reveal)

- Amendment timestamp (UTC): **2026-08-31T14:41:41Z**
- Pre-reveal HEAD at authoring: **2f77096** ("Freeze E007 independent P70 replication plan (pre-result)")
- **No E007 target metric had been computed before this amendment.** Only
  metadata population sizes (folio/token counts, Currier/section coverage,
  locus-type inventory) were inspected — declared nuisance/population facts, not
  prequential bits, entropies, competitor/fold scores, or Currier/section
  performance. No `results.json` exists.

This amendment resolves under-specified operationalizations in the frozen
`PLAN.md` so two independent implementers get identical results. It changes no
frozen scientific choice (grammar, competitors set intent, primary metric
family, split function/seed, decision margins, claim ceiling). Where the plan
left a mechanism open, the resolution below is fixed **before** any reveal and
is not result-driven.

Helper code frozen alongside this amendment (fixture-tested, no corpus metrics):
`src/voynichlab/loci.py`, `src/voynichlab/mdl.py`, `src/voynichlab/p70.py`, and a
`locator` field added to `LineRecord`. Tests: `test_loci.py`, `test_mdl.py`,
`test_p70.py`.

---

## 1. A8 determinism + no leakage (frozen)

**A8 is a deterministic function of the surface token TYPE.** The same EVA token
receives the same 4-slot cut at every occurrence. Pseudorandomness comes from a
stable hash, never a stateful stream RNG:

```
digest = SHA256("E007-A8|20260907|" + token).hexdigest()
```

**Matched slot-length profile is development-only nuisance estimation.** The
profile is the empirical distribution, computed on **DEVELOPMENT folios {0,1,2}**
under the frozen E007 split (`efold`), of the P70 layer-A slot-length 4-tuple
`(len(prefix), len(gallows), len(core), len(suffix))` **conditioned on token
length L**. It is frozen after development and then applied to all tokens
(including holdout) unchanged. It is never derived from holdout or from any
evaluation score.

**A8 cut rule (frozen):** for a token of length L, let `pool[L]` be the frozen
development list (in a deterministic order) of observed slot-length 4-tuples for
that L. Pick index `i = int(digest, 16) % len(pool[L])` and cut the surface
string into the four contiguous pieces of those lengths (a length-0 piece is the
empty slot `""`). Concatenation reconstructs the token (lossless). If `L` is
absent from `pool` (unseen length), fall back to cutting by the frozen global
development mean slot-length fractions `(f_p,f_g,f_c,f_s)`: boundaries at
`round(L·f_p)`, `round(L·(f_p+f_g))`, `round(L·(f_p+f_g+f_c))`, clamped
monotonically to `[0,L]`. Because A8 inherits P70's exact per-length slot-length
statistics, it is a **conservative** complexity-matched null (it is handed
P70's structural complexity for free and differs only by destroying which
characters occupy which slot).

This is consistent with the frozen §4.2 ("deterministic function token → slot
tuple") and §6 (seed 20260907, matched profile). It is not a silent change.

## 2. A4 — DEFERRED_PRE_REVEAL (frozen now)

No single canonical, deterministic, closed-inventory Stolfi-style rule can be
pinned this cycle without importing Stolfi's full external word-grammar (whose
own parsing ambiguities would need their own freeze). Any loose approximation
would be unfair and could be tuned after seeing scores. Therefore **A4 is
`DEFERRED_PRE_REVEAL`** and is **excluded from the E007 gate**; it may not be
reactivated in this E007 run. The competitor set for the reveal is
**A0, A1, A2, A3, A5, A6, A7, A8** (eight models).

## 3. R1 reproduction tolerances (frozen)

Each R1 quantity is classified now, from upstream published numbers, the known
ZL_2b↔ZL3b version difference, and methodological plausibility. Reconstruction
exactness and zero chain-rule residual are **near-constructive for a lossless
residual-core grammar and are NOT evidence.**

| R1 quantity | class | rule |
|---|---|---|
| Lossless reconstruction (prefix+gallows+core+suffix == token) | **DESCRIPTIVE / sanity** | must be 100% by construction; <100% ⇒ implementation bug, not evidence |
| Chain-rule residual | **DESCRIPTIVE / sanity** | identity (≈0); not evidence |
| Non-degenerate parse rate (≥1 non-empty affix) | **TOLERANCE** | REPRODUCTION_FAILURE if < **85%** |
| Empty-core rate (published 52.7%) | **TOLERANCE** | REPRODUCED band **[42.7%, 62.7%]** (±10 pp for version diff) |
| Total chain-rule entropy (published 10.311 bits) | **TOLERANCE** | REPRODUCED band **10.311 ± 1.0 bit** |
| Per-slot entropies H(P),H(G\|P),H(C\|P,G),H(S\|P,G,C) | **DESCRIPTIVE ONLY** | report; no pass/fail (tokenization/version dependent) |
| Inventory sizes actually used; MI(section,prefix); MI(core,suffix); Cramér's V | **DESCRIPTIVE ONLY** | no principled tolerance |
| Section-wise rates | **DESCRIPTIVE ONLY** | report |

**R1 decision (machine-decidable):** `REPRODUCTION_FAILURE` iff non-degenerate
parse rate < 85% **OR** (empty-core outside [42.7,62.7] **AND** total entropy
outside 10.311±1.0). Otherwise `REPRODUCED` (for R1 labelling only; R1 is never
by itself validation of the grammar).

## 4. Model description cost (frozen)

`total_bits(M) = model_bits(M) + data_bits(M)`, `total_bits_per_token =
total_bits(M) / N_tokens`.

- `data_bits(M)` = the prequential KT description length (§4.3 / `mdl.KTCoder`).
- `model_bits(M)` = Σ over M's **model-specific literal closed-inventory
  strings** of `charcost(string, |Σ|)` using the same frozen char code as §4.3,
  **plus** `elias_gamma(seed+1)` for a model that carries a seed (only A8),
  **plus** `elias_gamma(n_slots)` for its slot count. Σ is the frozen EVA
  character set of the ZL3b running-text strict-token population (recorded in
  results).
- Excluded explicitly: Python source byte length, JSON formatting length,
  README length — never used as complexity.
- A0 (whole token) has **no** closed inventory ⇒ `model_bits(A0)` = only its
  `elias_gamma(1)` slot-count term. This makes A0 the cheapest model and P70's
  inventory cost fully counts against P70 — a conservative setup.

**Gate 4 becomes machine-decidable:** P70 must beat A0 on `total_bits` (not only
`data_bits`), and P70's advantage over A0 must not be wholly attributable to
core-escape bookkeeping (report core-escape bit share; P70 must still beat A0 on
`total_bits`).

`elias_gamma(k)` for integer k≥1 = `2*floor(log2(k)) + 1` bits (the standard
Elias gamma length); it is the frozen universal integer code for all model
integer parameters.

## 5. Fold-score semantics (frozen — cross-fitted)

The 5-fold stability diagnostic used in Gate 3 is **cross-fitted**:

```
for j in folds 0..4 (E007 efold):
    train a fresh predictor on the tokens of the other four folds (prequential
    accumulation), then FREEZE counts;
    code fold j's tokens with NO further updates;
    fold_score(M, j) = coded bits(fold j) / N_tokens(fold j)   # bits/token
```

"P70 strictly lowest in ≥4 of 5 folds" (Gate 3) means: for each competitor C,
`fold_score(P70,j) < fold_score(C,j)` for ≥4 of the 5 folds. This is a genuine
cross-fitted predictive diagnostic. It is **separate** from and does not alter
the frozen §7 development/holdout arm or the primary global prequential metric
(§4). This resolves the previously-undefined Gate-3 fold semantics; it does not
contradict the frozen text.

## 6. Currier categories (frozen — ZL3b-native)

Currier language is taken from the **ZL3b folio header `$L`** (our own corpus,
maximally version-robust), not from any upstream JSON.

- Categories: **A** (`$L=A`) and **B** (`$L=B`).
- Folios with `$L` absent/unknown (`None`) are **excluded from the A/B gate**
  (reported descriptively). Population (running-text strict tokens): A ≈ 10,833,
  B ≈ 22,255, unclassified ≈ 523 — both A and B are amply powered.
- Gate 5 (Currier part): P70 lowest global-prequential `data_bits/token` within
  **both** A and B subsets. No category is dropped after seeing scores.

## 7. Section categories (frozen — ZL3b-native `$I`)

Section is taken from the **ZL3b folio header `$I`** illustration code, not from
the upstream `voynich_section_map.json` (which is 2b). The upstream map may only
be used to **descriptively** cross-check folio coverage, never to define scores.

- Section buckets = distinct `$I` codes on running-text folios: H, S, B, P, T,
  C, A.
- **Major-section rule (a-priori, population-based):** a section is
  gate-eligible iff its running-text strict-token count ≥ **2000** AND its folio
  count ≥ **8**. By current population that makes the **major sections =
  {S, H, B, P}**; **{T, C, A}** are DESCRIPTIVE ONLY (T has 6 folios < 8; C, A
  have <2000 tokens). Thresholds were set from population sizes (allowed
  nuisance), with no P70/competitor score consulted.
- Folios with `$I` absent → excluded from the section gate (none occur in
  running text currently; the rule stands for robustness).
- Gate 5 (section part): P70 lowest global-prequential `data_bits/token` within
  each **major** section {S,H,B,P}.

The section metadata is ZL3b-native, so Gate 5 is well-defined on our corpus and
is **not** UNRESOLVABLE_PRE_REVEAL; no BLOCKED is required on this point.

## 8. Running-text vs label filter (frozen + implemented)

`voynichlab.loci.is_running_text(locator)`: a locus is **RUNNING_TEXT** iff its
locus-type letters (locator with leading position chars `@+*=&~/!` and trailing
digits removed) **begin with `P`** (paragraph). Labels `L*`, circular `C*`,
radial `R*`, and anything else are **excluded**. This is the faithful reading of
the frozen §4.1 "running-text loci only"; it excludes circular/radial as well as
labels, applied identically to all models. The `LineRecord.locator` field now
carries the locator. Tested on hand fixtures (`test_loci.py`); no corpus metric
computed. Population: running-text strict tokens ≈ 33,611 of 34,321.

## 9. P70 parse precedence (frozen + implemented)

`voynichlab.p70.parse_p70` implements exactly:
surface → longest **prefix** at start → remove → longest **gallows** at new
start → remove → longest **suffix** at the **end of the remaining string** →
remove → remainder = **core**. The suffix matches only the remaining string, so
it can never overlap consumed prefix/gallows characters. Tie-break: longest
length, then frozen inventory declaration order (`PREFIXES`, `GALLOWS`,
`SUFFIXES`). Empty slot is the logical `""` (∅), not an EVA glyph. `ch`/`sh` are
prefixes. Semantics frozen in `test_p70.py`. No corpus metric computed.

## 10. KT / escape replay contract (frozen + implemented)

`voynichlab.mdl.KTCoder` implements the frozen §4.3 code. `test_mdl.py` fixes:
probabilities (seen values + single escape) sum to 1; first-unseen costs exactly
the char code; repeated-seen is cheaper; new context isolates counts; `∅` (empty
string) handled; char escape includes an EOS unit; identical input → identical
bits (determinism). The coder never iterates unordered containers to produce a
cost, so there is no float-order nondeterminism; run.py (next cycle) must sort
inventories/contexts where iteration order could otherwise matter.

---

## Residual-ambiguity check

Every open operationalization named in the amendment task is now fixed with a
machine-decidable rule (A8, A4, R1 tolerances, model cost, fold semantics,
Currier, sections, running-text filter, parse precedence, KT contract). A fair,
cross-model-identical primary metric and a machine-decidable gate exist.
Therefore E007 is **not** BLOCKED. If implementation reveals a genuinely
defensible alternative that could move the target, the run must stop and record
BLOCKED before reveal rather than choose silently.

**No E007 target metric is computed in this cycle.**
