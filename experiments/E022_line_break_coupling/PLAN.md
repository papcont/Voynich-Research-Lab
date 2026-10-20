# E022 — does the boundary coupling cross the line break? (PLAN v2 — review folded in; FREEZE PENDING)

Status: **DRAFT v2, not yet frozen** (2026-10-20; the freeze commit flips this line and RESEARCH_STATE.json). **No E022 conditional statistic has been computed.** The
only pre-freeze numbers are marginals (§2.5; `prefreeze_marginals.py`, output sha256 in
`experiment.json`) and a power simulation driven by those marginals (`prefreeze_power.py`).
Draft v1 (commit 8806e69) was reviewed adversarially (three lenses, each verified); the changes
are listed in §7. Evidence class: DEVELOPMENT (ZL3b running text; development pool; no lockbox;
Gate v2 level claimable: none).

## 1. Question and why it discriminates

Within lines, the previous token's final glyph predicts the next token's P70 prefix, dominated
by one probabilistic transition `y → qo` (E011 Δ_S +0.088; E018 R = 6.07 in Biological B,
3.71 other B, 2.19 A; E021 S1 = 0.23). Every account so far treats the token sequence inside a
line. Three account families make different predictions about the **line break** (last token of
line *i* → first token of line *i+1* inside a paragraph):

- **(a) State-carrying streams** (a Markov glyph/syllable process, phonotactics or morphology of
  an underlying unit sequence with a previous-unit → next-initial dependency, a cipher whose
  output depends on the previous output): the dependency persists at the break at (close to)
  its within-line strength, and across drawing gaps.
- **(b) Boundary-placement streams** (E019–E021 family: the coupling arises from where token
  cuts fall in a verbose stream): persistence only if line breaks are placed like other cuts; if
  the scribe ends lines at unit boundaries, cross-line coupling falls to the aligned-boundary
  level (≈ 0, E019) without any "line reset".
- **(c) Line-as-unit and visual-adjacency accounts** (Currier's "line as a functional unit",
  grille-row/table generators with one line per placement, scribal conventions applied to
  adjacent tokens on the same physical line): null at the break; visual adjacency also null
  across drawing gaps (`<->`), line-as-unit keeps coupling across gaps.

Paragraph breaks (last line of paragraph *k* → first line of paragraph *k+1* on the same page)
are a third class, reported as a gradient check; its power is low (§2.5), so it carries no
falsification in this run.

Prior observations (none reimplemented, none a verified prior result for the cross-line
transition; CLAUDE.md rule 10 → `EXTERNAL_UNVERIFIED`): Currier (1976) line-edge frequency
anomalies; the LAAFU line-initial/line-final and paragraph-initial conventions (Vogt, Smith,
Ponzi, Feaster); Smith & Ponzi (2019) within-line word-break combinations; voynich.ninja
discussions reporting a negative cross-line word-join test and a 2026 report of no glyph-level
cross-line coupling; the line-breaking-bias critique. Sources were unreachable from the
2026-10-20 environment. H034's prediction below is the programme's own; taken at face value the
2026 report predicts H034 `FALSIFIED_DEV`, so either outcome discriminates.

## 2. Population, definitions, statistics

### 2.1 Records
- `data/raw/ZL3b-n.txt` (git blob 2a4533ab…, sha256 bf5b6d4a…). Records = the running-text
  records returned by `voynichlab.ivtff.parse_ivtff` (E007 filter `loci.is_running_text`) in
  file order per folio. Known parser limitation, kept for comparability with E007–E021: a record
  whose text begins with an inline comment matches the folio-header pattern and is dropped —
  55 P-type records (f85r2.2–23, f86v3.1–14 and 23–36, fRos.39–40, 137, 139, 142), all locus
  type `Pb`, all Currier B non-biological; 4,075 of 4,130 P-type records remain. `run.py` and
  `validate.py` assert both counts and list the dropped loci in `results.json`.
- Tokens: `ivtff.tokenize_surface` (E011/E018). Strict = `Token.uncertain` is False. Drawing
  gaps `<->`/`<~>` become certain separators; a token whose separator derives from a gap is
  flagged `gap_before` (segment-wise tokenisation, asserted identical to the frozen tokenizer).
- Population ($L × $I) is a folio attribute: `bio_B` (B, section B), `other_B`, `A`;
  `B_pooled` = bio_B ∪ other_B where stated. The 95 running-text lines on the 10 folios without
  $L belong to no population; all their pairs are excluded and counted (`no_population`).
- Paragraph id: increments at every record carrying `<%>`; records before a folio's first
  `<%>` form paragraph 0.
- Records of locus type `Pb` (word columns beside figures) are excluded from every class and
  counted (bio_B 27 records). Every other record stays in the sequence, including lines whose
  tokens are all uncertain; nothing is bridged.

### 2.2 Pair classes (a pair is (previous final glyph `S`, next P70 prefix))
Features exactly as E011/E018: `S` = last EVA character of the previous token; prefix =
`p70.parse_p70(token)[0]`. Both edge tokens must be strict.
- **within** — consecutive strict tokens of one record, separator not a gap. Stratum
  (folio, paragraph).
- **gap** — consecutive strict tokens of one record across a drawing gap. Stratum (folio,
  paragraph). Reported only.
- **line** (line-break) — consecutive records *i*, *i+1* of a folio, earlier without `<$>`,
  later without `<%>`. Stratum (folio, paragraph) of the earlier record (same paragraph by
  construction).
- **para** (paragraph-break) — earlier with `<$>` and later with `<%>`. Stratum folio.
- **lag2** — records *i*, *i+2* with *i*, *i+1*, *i+2* consecutive, no `<$>` on *i* or *i+1*,
  no `<%>` on *i+1* or *i+2*. Stratum (folio, paragraph). Composition control, reported only.
- Exclusions for line/para/lag2, applied in this order and counted per class:
  `no_population`; `bridges_dropped_record` (the two records are not adjacent in the raw-file
  order of P-type loci); `marker_mismatch` (later `<%>` ≠ earlier `<$>`); `same_line_title`
  (later record's IVTFF position mark is `=`: same physical line, the paragraph's title); 
  `pb_record`; `population_change` (zero-count assertion); `empty_line`; `uncertain_edge`.
  Label/circular loci between two running-text records do not break a pair. One-token lines are
  admitted (the token is both line-final and line-initial); pairs touching them are counted
  and a bio_B sensitivity without them is reported.

### 2.3 Statistics
- **Enrichment, stratified (Mantel–Haenszel risk ratio):** over the strata *s* of a class,
  `R_MH = Σ_s a_s·n_o,s/N_s ÷ Σ_s c_s·n_y,s/N_s` with `a_s`/`n_y,s` = `qo`-prefixed next tokens /
  pairs after a `y`-final previous token, `c_s`/`n_o,s` the same after a non-`y` final,
  `N_s = n_y,s + n_o,s`; strata with `n_y,s = 0` or `n_o,s = 0` contribute nothing and are
  counted. **Decisions use the paragraph-stratified R_MH** (line, lag2, within) and the
  folio-stratified R_MH (para). Reported beside it: the plain pooled `R` of E018, the
  folio-stratified R_MH (sensitivity), and the Mantel–Haenszel odds ratio (risk ratios are not
  comparable across populations whose line-initial `qo` base rates differ).
- **Null:** pairing permutation within stratum — the next-prefix column is permuted among the
  pairs of the same stratum (preserves both edge marginals per stratum and therefore
  line-position, between-folio and between-paragraph composition; destroys only the pairing).
  1,000 permutations; `p = (1 + #{R_MH,null ≥ R_MH} + #{undefined}) / 1001`; a permutation with
  zero MH denominator counts as `+∞`; the undefined fraction is reported and if it exceeds 5%
  the block's null is `NOT_DEFINED` (no decision, no prediction score). Null mean, median and
  97.5% quantile reported. R_MH is reported raw; the null median is 1.00 by construction.
- **Folio bootstrap (bio_B, other_B, A):** 10,000 paired resamples (with replacement) of the
  population's folios holding at least one line or within pair; per resample the per-folio MH
  terms are summed and `R_MH,b(line)`, `R_MH,b(within)` recomputed. Percentile 95% CI of
  `R_MH(line)` (resamples with zero denominator dropped and counted). **Persistence ratio**
  `ρ_b = ln R_MH,b(line) / ln R_MH,b(within)`; a resample is dropped only if its denominator is
  undefined or non-positive (`R_MH,b(within) ≤ 1`, or a zero MH denominator in either class);
  `ρ_b ≤ 0` is kept, `R_MH,b(line) = 0` gives `ρ_b = −∞` and is kept; rank-based (non-
  interpolating) 95% percentile interval; dropped fraction reported; if it exceeds 5% the CI is
  flagged `CI_UNRELIABLE`. Point estimate `ρ = ln R_MH(line)/ln R_MH(within)`. ρ for other_B and
  A is descriptive (their line-initial `qo` baselines differ from the within-line baseline).
- **Sensitivities (bio_B, reported, no decision):** `R_MH^−mg`, `ρ^−mg` with previous tokens
  ending in `m` or `g` removed from both classes; `ρ_len` with the within-line reference
  post-stratified (weighted MH) to the line-final previous-token length distribution (classes
  ≤ 2, 3–4, 5–6, ≥ 7 characters); the within reference including gap pairs (E018-comparable);
  bio_B without one-token lines. other_B additionally by LFD hand ($H), same statistics.
- **Whole-table check (bio_B, reported):** plug-in MI `I(S; prefix)` in bits over the full
  previous-final alphabet × P70 prefix (∅ included). Line class: `I` minus the mean of the 1,000
  pairing permutations. Within reference: 200 subsamples of the line-class size (seed 20261191),
  each `I` minus the mean of 20 pairing permutations; mean and SD over subsamples. Selectivity
  `S1` (E021: share of `I` in the binary contrast 1[S = y] × 1[prefix = qo]) on the line class and
  on each subsample; remainder excess = excess × (1 − S1). Ratios reported: total and remainder.
- **RNG:** one generator per seed. Seed 20261190 (permutations) consumed in the order class
  within, gap, line, para, lag2 × population bio_B, other_B, A (+ B_pooled for line, para,
  lag2), then other_B hands, then the m/g sensitivity blocks. Seed 20261019 (bootstrap)
  consumed bio_B, other_B, A. Seed 20261191: line-class MI permutations, then the within
  subsamples.

### 2.4 Decisions (fixed before any conditional statistic)
Decision population for H034/H035: **bio_B** (one hand, one section; largest within-line
effect; 602 line pairs, 313 after `y`, 172 `qo`-initial; line-start `qo` rate equals the overall
rate, so the comparison is not starved). other_B and A are reported with the same statistics,
no decision. Evaluation order within each rule: FALSIFIED, then SUPPORTED, else the residual
state.

- **H034 — the dominant transition crosses the line break** (line class, bio_B, paragraph
  strata). `FALSIFIED_DEV` iff `R_MH ≤ 1.1` or the folio-bootstrap 95% CI upper bound of
  `R_MH(line)` `< 1.5`; `SUPPORTED_DEV` iff `R_MH ≥ 1.5` and `p ≤ 0.01`; else `INCONCLUSIVE_DEV`
  (includes "not beyond the null but CI upper ≥ 1.5": attenuated to the detection floor, no
  mechanism conclusion). Null `NOT_DEFINED` → `INCONCLUSIVE_DEV`.
  *Composition guard (interpretation, not decision):* a `SUPPORTED_DEV` H034 is read as
  adjacency coupling only if the lag2 block does **not** itself meet the SUPPORTED rule and
  `R_MH(lag2) < R_MH(line)`; otherwise the result is labelled `COMPOSITION_CONFOUNDED` and the
  stream reading is withheld.
- **H035 — it crosses undiminished** (ρ, bio_B). `FALSIFIED_DEV` iff H034 is `FALSIFIED_DEV` or
  the ρ CI upper bound `< 0.25`; `SUPPORTED_DEV` iff `ρ ≥ 0.75` and CI lower `≥ 0.5`; else
  `PARTIAL`. With `CI_UNRELIABLE` the CI clauses are void (only the H034 route to FALSIFIED
  remains) and the state is `PARTIAL` with the flag. The numeric prediction (§3) is scored
  against the point estimate independently of the label.
- **H036 — coupling across paragraph breaks** (para class, B_pooled, folio strata).
  `FALSIFIED_DEV` iff the null's 97.5% quantile `≥ R_MH` **and** the number of `qo`-prefixed next
  tokens in informative strata `≥ 100`; `SUPPORTED_DEV` iff `R_MH ≥ 1.5` and `p ≤ 0.01`; else
  `INCONCLUSIVE_DEV`. At the pre-freeze marginals (10 such events) the FALSIFIED state is
  unreachable: H036 can only be SUPPORTED or INCONCLUSIVE in this run and stays a reported
  gradient check (R_MH, p, event count, paragraph-start vs line-start `qo` rate; the line class
  on B_pooled is the gradient reference). bio_B-only and A-only paragraph blocks are reported
  with their `NOT_DEFINED`/event counts; no decision.

### 2.5 Pre-freeze marginals and power (no conditional quantity)
`prefreeze_marginals.py` (counts and rates only; no (S × prefix) cell is formed):

| population | lines | within pairs | line pairs (after y; qo-initial) | para pairs (after y; qo) | P(qo \| line-initial) · pair-level · overall | P(y-final \| line-final) · pair-level · overall | P(qo \| para-initial), P(gallows \| para-initial) | P(m/g-final \| line-final) vs overall |
|---|---|---|---|---|---|---|---|---|
| bio_B | 745 | 5,324 | 602 (313; 172) | 56 (38; 6) | 0.252 · 0.286 · 0.245 | 0.537 · 0.520 · 0.534 | 0.086, 0.79 | 0.084 vs 0.010 |
| other_B | 1,678 | 14,143 | 1,169 (418; 92) | 295 (132; 7) | 0.068 · 0.079 · 0.152 | 0.384 · 0.358 · 0.419 | 0.019, 0.91 | 0.239 vs 0.030 |
| A | 1,557 | 8,976 | 1,152 (383; 172) | 102 (40; 6) | 0.132 · 0.149 · 0.096 | 0.340 · 0.332 · 0.316 | 0.043, 0.87 | 0.139 vs 0.034 |

Exclusions already visible at the marginal level: Pb records 27/6/0; same-line titles 0/10/35;
uncertain edges 34/112/138 (line); marker mismatches 1 (bio_B para), 2 (other_B para); one-token
lines 13/1/6. Known before freeze and recorded as such: `qo` is depleted at line starts in
other_B (0.08 vs 0.15) and enriched in A (0.15 vs 0.10) — a line-position effect of the E011 Δ_L
kind; paragraph-initial tokens are 79–91% gallows-initial and almost never `qo` (no token of
shape gallows+`qo` exists). These quantities constrain neither R_MH nor ρ.

Power (`prefreeze_power.py`, synthetic tables from the per-stratum marginals, exact
hypergeometric pairing null, 400 tables × 1,000 permutations, seed 12345): null 97.5% quantile
of R_MH 1.30 (bio_B), 1.51 (other_B), 1.35 (A); P(SUPPORTED_DEV) at true R = 1.5 / 1.7 / 2.0:
bio_B 0.52 / 0.81 / 0.98, other_B 0.34 / 0.57 / 0.82, A 0.46 / 0.78 / 0.97. Paragraph class
(B_pooled, 10 events): null q97.5 ≈ 3.8, P(SUPPORTED | R = 6) = 0.38.

## 3. Pre-result predictions (recorded before the run)
- H034: `SUPPORTED_DEV`, R_MH ≈ 2–3 in bio_B (attenuated against the within-line ≈ 6).
- H035: `PARTIAL`, ρ ≈ 0.4–0.7 (scored on the point estimate). Family (a) predicts ρ ≈ 1,
  families (b)-with-aligned-line-ends and (c) predict ≈ 0; the hedge is deliberate and is scored
  as wrong if either extreme obtains.
- Lag2 (bio_B): R_MH < 1.3 and not meeting the SUPPORTED rule (no composition confound).
- H036: `INCONCLUSIVE_DEV` (≈ 10 events).
- Gap class: in A (the informative population, n ≈ 1,000+) R_MH at the within-line level
  (coupling survives drawing gaps → against visual adjacency); bio_B gap n too small.
- Whole-table: total excess ratio ≈ 0.3–0.6; remainder ratio ≤ total ratio (directional).
- other_B > A on the line-class point estimates; labels not predicted (A is at the detection
  floor for ρ = 0.5).

## 4. Interpretation rules (fixed)
- H034 `SUPPORTED_DEV` (adjacency reading) **and** H035 `SUPPORTED_DEV`: the token sequence
  behaves as one stream across lines for the dominant transition; whether the diffuse remainder
  does is the reported MI ratio. Family (c) and within-line scribal conventions are disfavoured
  as sufficient; family (a) gains; family (b) survives only with line breaks placed like other
  cuts.
- H034 `FALSIFIED_DEV`: the first token's prefix does not depend on the previous line's final
  glyph. Family (a) must add a line-initial process that removes the dependence (a reset or a
  line-initial rewrite); family (b) must place line breaks at unit boundaries; family (c) and
  generators with line structure gain.
- H034 `INCONCLUSIVE_DEV` with R_MH in (1.1, 1.5): attenuated to the detection floor; no
  mechanism conclusion.
- H035 `PARTIAL`: both a cross-line dependency and a line-specific component exist; the
  mechanism target (E021 §5) gains one reported component — the line-break persistence ρ with
  its folio-bootstrap 95% CI at the stated pair counts — that proposals are scored against, not
  a gate.
- `COMPOSITION_CONFOUNDED`: the stream reading is withheld; the result is recorded as
  "coupling present at lag 1 and lag 2, consistent with paragraph-level vocabulary drift".
- H036: only `SUPPORTED_DEV` is informative (the stream ignores paragraph structure,
  unexpected); a null or inconclusive H036 cannot separate paragraph-as-unit from the
  paragraph-initial gallows convention.
- Gap class: R_MH at the within-line level together with a null at the line break favours
  line-as-unit over visual adjacency; a null across gaps favours visual adjacency.

## 5. Degrees of freedom, confounds, registration
- **Selection rule:** the tested transition (`y`-final → `qo`-prefix), the three populations
  and the decision population were fixed by E018 before any E022 pair was formed; no other
  final glyph, prefix, population, lag or threshold is searched for a decision; the MI check,
  the gap/lag2 classes, the sensitivities and the other_B/A values are reported only.
- **Free parameters:** none. H034 gates 1.1/1.5 and p ≤ 0.01 are inherited from E018 H003a; the
  CI-based FALSIFIED clause, the H035 thresholds (0.75 / CI lower 0.5 / CI upper 0.25), the 5%
  undefined/dropped floors and the H036 event floor (100) are new, set here a priori and
  untuned. Seeds fixed.
- **Confounds:** line-initial/line-final marginal conventions and between-folio and
  between-paragraph composition are absorbed by the paragraph-stratified R_MH and the pairing
  null; paragraph-level drift is additionally guarded by lag2. Line-final `m`/`g` tokens and the
  different lexical/length mix of line-final tokens act on the conditioning variable and can
  only attenuate the break statistics; covered by the `−mg` and length sensitivities. Word
  splitting at the right margin cannot produce a false-positive `y → qo` (`q` is token-initial;
  no token contains `y` followed by `q`; no gallows+`qo` token exists) and is not a control
  target; it can only attenuate, and an attenuated ρ is **not** to be reinterpreted post hoc as
  splitting. LFD hand: bio_B is one hand (2); other_B by hand reported, no decision.
- **Dependency unit:** folio (strata nested in folios; bootstrap over folios).
- **Evidence surface:** development pool (all ZL3b running-text folios, DEVELOPMENT_ONLY per
  `research/holdout_registry.json`); no lockbox; no Gate v2 level.
- **Validation:** decision inputs are `run.py`'s statistics under the registered seeds.
  Independent `validate.py` re-derives from the raw file with its own extraction and
  arithmetic: the record set and dropped loci, pairs and every exclusion count (exact), R_MH,
  R_plain, OR_MH, counts and the MI/S1 point values (tolerance 1e-9), the bootstrap by exact
  reproduction (same seed and draw order), and the §2.4 decisions from the recorded numbers
  (exact). Its own permutation null (own scheme, seed 20269999) must agree within
  `|p_val − p_run| ≤ 0.02` (or both ≤ 0.01) and 5% on the 97.5% quantile. **Pre-registered
  resolution:** if a §2.4 decision under the validator's own null differs from `run.py`'s, the
  recorded outcome is `INCONCLUSIVE_DEV` (near-threshold) and both p-values are reported.
- **Retraction condition** per hypothesis = its FALSIFIED_DEV rule; any post-reveal change to §2
  or §2.4 relabels the affected hypothesis `EXPLORATORY`. Parser/tooling version = `src/voynichlab`
  at the freeze commit. `experiment.json` records sha256 of the input, of this plan, of the
  predictions and of the pre-freeze marginals output.
- **Claim ceiling:** structural transition statistics across line, gap and paragraph breaks;
  nothing about meaning, language, or what `y`/`qo` are. Negative results stay in the ledger.

## 6. Prior observations referenced (unverified)
Currier, P. (1976) "Some important new statistical findings" (New Research on the Voynich
Manuscript); Smith, E. M. & Ponzi, M. (2019) "The word-break combinations" (voynich.ninja /
agnosticvoynich); LAAFU discussions (Vogt, Feaster); voynich.ninja threads on cross-line word
joins (2017–2026). Listed in `experiment.json` as `EXTERNAL_UNVERIFIED`.

## 7. Changes from draft v1 (review 2026-10-20)
Paragraph strata for line/lag2/within (sub-folio composition), lag2 composition guard, gap
class, same-line-title and Pb exclusions, parser-limitation record set, bootstrap drop rule
(ρ ≤ 0 kept), CI-based H034 falsification, H036 falsification made power-honest, undefined-
permutation rule, MI check with 20-permutation subsample nulls and S1 remainder, pair-level
marginals and committed power simulation, odds ratios and hand breakdown, three-family framing,
selection-rule and validator-resolution text, word-splitting statement.
