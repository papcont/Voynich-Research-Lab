# E008 — common-scorecard mechanism tournament, stage A (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-19, after E007 completed)
Freeze rule: this file fixes every scientific choice before any E008 target
metric is computed. **No E008 target metric has been computed at freeze time.**
Only population facts were inspected (running-text strict tokens 33,611 on 206
folios and 4,075 lines; line positions FIRST 3,878 / MID 25,869 / LAST 3,842 /
ONLY 22; previous-token availability BOL 3,900 / TOK 28,853 / UNC 858; |Σ| = 25).
The E007 base scores (P70 and whole-token, including their dev→holdout values
14.42 / 16.11 bits/token) are already known and are **not** E008 targets.

Hypotheses under test: **H011** (inter-token edge state), **H012** (local
copy/modify), **H013** (line position) — all as *predictive-information*
claims, see §8. Mechanism families N/C/G/M are read out ordinally only (§9).

---

## 1. Question and scope

One scorecard, several mechanism *components*, one corpus. Which of the
following carry **independent held-out predictive information** about the next
running-text token in ZL3b, on top of each other and on top of within-token slot
structure?

- **S** — inter-token edge state (the previous token's final glyph);
- **L** — line position (first / middle / last token of a line);
- **C** — local copy/modify (the token is an exact or one-edit copy of a recent
  token in the same folio, the "self-citation" generator mechanism).

Scope: Zandbergen–Landini ZL3b (blob `2a4533ab…`), running-text strict tokens
(identical population and order to E007). No external corpora this stage.
Stage B (reference corpora: natural language, verbose cipher, generators) is
**DEFERRED** to its own preregistration (§12).

What this stage cannot do: decide N vs C vs G. A natural language, an
enciphered language and a generator can each produce sequential dependence and
local repetition. Stage A measures the *signature*; stage B compares signatures.

---

## 2. Data and population (frozen)

- Source `data/raw/ZL3b-n.txt`, git-blob `2a4533ab9bdfa85db9bad602d590978953055df1`
  (checked at run time).
- Population = running-text (`loci.is_running_text`) strict tokens
  (`ivtff.iter_strict_tokens`), exactly E007's 33,611 tokens, same order
  (folios sorted lexicographically, file order within folio).
- Line structure from `ivtff.tokenize_surface(line.raw_text)`; a line's full
  token list (including uncertain tokens) is used **only** to compute position
  and previous-token *availability* features. Uncertain tokens are never coded
  and their content is never read: the previous-token feature for a token whose
  predecessor is uncertain is the literal `UNC`.

## 3. Split, dependency unit, evidence class (frozen)

- Split = E007 `efold(folio) = int(sha256("E007:" + folio.lower()).hexdigest(), 16) % 5`;
  DEVELOPMENT = {0,1,2} (19,483 tokens), HOLDOUT = {3,4}.
- **Primary score of a model = holdout bits/token with counts trained on the
  development folios and then frozen** (no updates while coding holdout; the
  E007 dev→holdout arm). Development tokens are consumed prequentially in the
  frozen order.
- Dependency unit = physical folio. Folio-level stability is counted over
  holdout folios; no token-level p-values.
- Evidence class: **FROZEN_HOLDOUT** for every component contrast (their holdout
  numbers have never been computed). The two bases are known from E007 and
  carry no new evidence. The P70 base remains **NON-PROSPECTIVE** (built on the
  whole manuscript).

## 4. Scorecard (frozen, inherited from E007)

`voynichlab.mdl.KTCoder` with the frozen char escape over Σ (|Σ| = 25 recorded
at run time). Each model codes a token as an ordered list of slots; slot *i* is
coded in context `(i, preceding slot values of this token, conditioning
features)`. One coder per model. Totals:

- `data_bits` = Σ codelengths; `bits/token = data_bits / N`.
- `model_bits` = E007 Amendment 001 §4 inventory cost of the base
  (P70 inventories 728.9 bits; whole token 0) + `elias_gamma(1 + #components)`
  + for models with C: `elias_gamma(index_of_W + 1)` + 2 bits (selection, §6.4).
- `total_bits_per_token = (data_bits + model_bits) / N`.

Lossless check: every model must reconstruct 100% of tokens (constructive).

## 5. Bases (frozen)

- **B0** whole token: one slot `(t,)` (E007 A0).
- **B1** P70 layer A: `(p, g, c, s)` via `voynichlab.p70.parse_p70` (E007 P70).
  Chosen as primary base because it was the best segmentation in E007; this is
  not a claim that its slots are morphemes.

## 6. Components (frozen definitions)

### 6.1 S — edge state
Feature `S(t)` = last EVA character of the previous token **in the same line**
(previous element of the line's full token list): `BOL` if the token is
line-initial, `UNC` if the previous token is uncertain, otherwise the single
last character of the previous token's surface string. When S is on, `S(t)` is
appended to the context of **every** base slot of the token.

### 6.2 L — line position
`L(t)` ∈ {`FIRST`, `MID`, `LAST`, `ONLY`} by index in the line's full token
list. When L is on, `L(t)` is appended to the context of every base slot.

### 6.3 C — local copy/modify
Window `win(t)` = the previous `W` population tokens of the **same folio** in
the frozen order (across lines, not across folios; shorter at folio start).
Let `k` run from 1 (most recent) to `len(win)`.

- `d = 0` match: smallest `k` with `win[k] == t`.
- else `d = 1` match: smallest `k` with Levenshtein distance `lev(win[k], t) == 1`.
- else `NONE`.

Coding: slot `src` with value `"k:d"` or `"NONE"`, context `("src",)` (no other
conditioning). If `d = 0`, nothing more is coded. If `d = 1`, one slot `edit`
with context `("edit",)` and the canonical edit string: equal lengths →
`s{p}{c}` (substitution at the first differing position `p` with target char
`c`); `len(t) = len(src)+1` → `i{p}{c}` with the smallest `p` such that
`src[:p] + c + src[p:] == t`; `len(t) = len(src)−1` → `d{p}` with the smallest
`p` such that `src[:p] + src[p+1:] == t`. If `NONE`, the base slots are coded
as usual (with S/L contexts if on). **Base-slot counts are updated on every
token** regardless of path (the decoder knows the token either way). The code
is prefix-free and decodable given the window.

### 6.4 W selection (the only free parameter; development only)
`W ∈ {5, 10, 20, 40}`. Choose the `W` with the lowest **development-only
prequential** `data_bits` of model B1+C (ties → smaller W). The choice is made
once, before any holdout coding, recorded with all four development values, and
applied to every C-model and to the holdout unchanged. Cost: 2 bits + Elias
gamma of the index, charged to every C-model.

### 6.5 Model set
Full factorial over {S, L, C} on both bases: 16 models
(`B0`, `B0+S`, …, `B0+S+L+C`, `B1`, …, `B1+S+L+C`). Slot order inside a token:
`src` (if C on), `edit` (if d = 1), then base slots.

## 7. Nulls (frozen)

- **N1 — within-folio order shuffle (primary null).** Seed `20261019`,
  `numpy.random.default_rng`; permute the *population* tokens among the
  population positions of each folio (folios processed in frozen order,
  positions in file order); uncertain tokens keep their positions, so `UNC`,
  `BOL` and `L` are recomputed from the shuffled lines. Preserves folio
  vocabulary and token-length marginals; destroys sequential adjacency, line
  position and local (line-above) copying. All 16 models and all contrasts are
  recomputed on N1 with the same dev→holdout protocol and the same W.
- **N0 — within-line shuffle (secondary, reported only).** Same seed family
  (`20261019 + 1`); destroys S and L, leaves cross-line copying intact.

## 8. Decision rules (frozen; effect sizes, no significance stars)

For component X ∈ {S, L, C} on base B1 (primary) and B0 (robustness):

- marginal gain `Δm(X) = bpt(B1) − bpt(B1+X)`;
- unique gain `Δu(X) = bpt(B1 + all − X) − bpt(B1 + S + L + C)`;
- folio stability `f(X)` = fraction of holdout folios where
  `bpt_folio(B1+S+L+C) < bpt_folio(B1 + all − X)`;
- Currier `Δu_A(X)`, `Δu_B(X)` on holdout tokens with `$L` = A / B;
- null gain `Δu_N1(X)` from the N1 run.

**X is INFORMATIVE** iff all hold on B1:
1. `Δm(X) ≥ 0.05` bits/token;
2. `Δu(X) ≥ 0.05` bits/token;
3. `f(X) ≥ 2/3`;
4. `Δu_A(X) > 0` and `Δu_B(X) > 0`;
5. `Δu(X) − Δu_N1(X) ≥ 0.05` (the gain is not reproduced by folio vocabulary +
   coder bookkeeping alone).

**X is NOT_INFORMATIVE** iff `Δm(X) < 0.05` and `Δu(X) < 0.05`. Otherwise
**MIXED** (reported with all five criteria). B0 results are reported; if a
B1 verdict is not reproduced in direction on B0 this is stated as
`BASE_DEPENDENT`.

Hypothesis mapping: H011 ↔ S, H012 ↔ C, H013 ↔ L. INFORMATIVE → `SUPPORTED
(structural)`; NOT_INFORMATIVE → `FALSIFIED_AS_PREDICTIVE_COMPONENT` on this
corpus/scorecard; MIXED → `WEAK`.

Pre-result predictions (recorded now, before any computation):
- H011 (S): from E002/H003 history, a positive gain is expected; the open
  question is whether it survives conditioning on P70 slots and on C.
  Prediction: `Δm(S) ≥ 0.05`; `Δu(S)` uncertain.
- H012 (C): Voynichese is known to repeat locally; prediction `Δm(C) ≥ 0.05`.
  Whether `Δu(C) ≥ Δu(S)` is the actual contest (§9); no prediction.
- H013 (L): known line-initial/final glyph preferences; prediction
  `Δm(L) ≥ 0.05` is **uncertain** (small effect expected); falsification of
  H013 as a predictive component is a live outcome.

## 9. Mechanism-family readout (ordinal, non-decisive, frozen wording)

Reported after the component verdicts, in this exact form:

- *copy/modify-generator signature*: C INFORMATIVE **and** `Δu(C) ≥ Δu(S)`;
- *sequential-dependency signature*: S INFORMATIVE;
- *line-as-unit signature*: L INFORMATIVE.

None of these is evidence for or against language, cipher or hoax by itself;
all three can coexist (family M). Stage B is required for any family claim.

Best overall model by `total_bits_per_token` and the full 16-model table are
reported descriptively.

## 10. Degrees of freedom, confounds, selection

- Free parameter: W (4 values, development-only, charged). Everything else
  fixed here. Three gated components × five criteria; no p-values.
- Confounds reported descriptively (never gating): per major section {S,H,B,P}
  Δu; Δu by line-length tercile (short/medium/long lines, terciles from the
  population); Δu by token-length (≤4 / 5–6 / ≥7); hand `$H` if present on
  ≥ 2 values; share of `UNC` and `BOL` contexts.
- Order sensitivity (E007 lesson): the primary is order-free in the holdout
  (frozen counts); development order is the frozen lexicographic order. One
  declared sensitivity: natural folio order for development, reported only.

## 11. Claim ceiling

Maximum claim if everything passes:

> "In ZL3b running text, the previous token's final glyph / line position /
> local copy-with-one-edit each carry independent predictive information about
> the next token beyond a four-slot token grammar, under a fixed universal
> coding benchmark."

Not claimed: morphemes, words, language, cipher, hoax, meaning, authorship.
The P70 base is non-prospective; stage A is a within-corpus signature.

## 12. Stage B (DEFERRED, requires its own preregistration)

Apply the identical 16-model scorecard to reference texts and compare the
component-gain *signatures* `(Δu(S), Δu(L), Δu(C))` with Voynich's:
(i) natural-language controls (e.g. medieval Latin / Italian; provenance,
hash and license fixed first), (ii) a verbose homophonic cipher of (i)
(independent Naibbe reimplementation from the paper — no code located
2026-10-19), (iii) a self-citation generator (independent reimplementation),
(iv) the `epilectrik/voynich` Currier-B grammar as a structural competitor,
(v) P70 layer A. Reference texts must be line-segmented to Voynich's line-length
distribution so L and C are comparable. Not fetched, not hashed, not computed
in stage A.

## 13. Deliverables and non-computation statement

Next cycle: `run.py` (writes `results.json` first), `validate.py` (independent
re-derivation with its own coder and copy/edit search), `REPORT.md` after.
Any implementation choice not fixed above is resolved by a committed
`PREFLIGHT_AMENDMENT_00x.md` **before** the first holdout coding. **No E008
data bits, gain, fold, folio, subset or null value has been computed.**
