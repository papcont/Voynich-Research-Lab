# E022 — does the boundary coupling cross the line break? (PLAN — DRAFT UNDER REVIEW, not frozen)

Status: DRAFT (2026-10-20). **No E022 conditional statistic has been computed.** The only
pre-freeze numbers are marginals (pair counts, edge-glyph and line-initial prefix frequencies;
§2.4), recorded here so the power statement is auditable. Evidence class: DEVELOPMENT (ZL3b
running text; no lockbox; Gate v2 level claimable: none).

## 1. Question and why it discriminates

Within lines, the previous token's final glyph predicts the next token's P70 prefix, dominated
by one probabilistic transition `y → qo` (E011 Δ_S +0.088; E018 R = 6.07 in Biological B,
3.71 other B, 2.19 A; E021 S1 = 0.23). Every account so far treats the token sequence inside a
line. The two live mechanism families make opposite predictions about the **line break**:

- **Stream accounts** (verbose/syllabic/letter-chunk codes with a mostly aligned boundary
  process, E019–E021; natural language with a written previous-word → next-initial dependency):
  the underlying sequence continues across the line break, so the coupling between the last
  token of line *i* and the first token of line *i+1* persists at (close to) its within-line
  strength.
- **Line-as-unit accounts** (Currier's "line as a functional unit", grille-row/table generators,
  scribal conventions applied within a line, language with line-end conventions): the first
  token of a line is not conditioned on the previous line's last token; cross-break coupling is
  at the null.

Paragraph breaks (last line of paragraph *k* → first line of paragraph *k+1* on the same page)
are a third class, reported as a gradient check: a stream without paragraph semantics would
carry coupling there too; a text with paragraph units would not.

## 2. Population, definitions, statistics

### 2.1 Data and units
- `data/raw/ZL3b-n.txt` (git blob 2a4533ab…, sha256 bf5b6d4a…), running-text loci only
  (`loci.is_running_text`, E007 filter), tokens by `ivtff.tokenize_surface` (`<->` gaps become
  certain separators, as in E011/E018), strict tokens = not uncertain.
- Lines in file order per folio. **Line-break pair** = two consecutive running-text records of
  the same folio where the earlier record does not carry `<$>`; **paragraph-break pair** = the
  same with `<$>` on the earlier record. A pair enters only if the earlier line's last surface
  token and the later line's first surface token are both strict and both lines belong to the
  same population; others are excluded and counted. Records with `<%>`/`<$>` inconsistencies
  (3 in the corpus) are excluded and counted.
- Features exactly as E011/E018: previous final glyph `S` = last EVA character of the previous
  token; next prefix = `p70.parse_p70(token)[0]`; the within-line reference uses the same code
  path on consecutive strict token pairs inside a line.
- Populations: `bio_B` (Currier B, section `$I=B`), `other_B`, `A`, and `B_pooled`
  (= bio_B ∪ other_B, used only where stated). Dependency unit: folio.

### 2.2 Statistics
- **Enrichment, folio-stratified (Mantel–Haenszel risk ratio):**
  `R_MH = Σ_f a_f·n_o,f/N_f ÷ Σ_f c_f·n_y,f/N_f`, where in folio *f* among the pairs of the
  class, `a_f`/`n_y,f` = `qo`-prefixed next tokens / pairs after a `y`-final previous token,
  `c_f`/`n_o,f` the same after a non-`y` final, `N_f = n_y,f + n_o,f`. Folios with
  `n_y,f = 0` or `n_o,f = 0` contribute nothing. The plain pooled `R` of E018 is reported
  beside it; **decisions use R_MH** (pooling across folios with different line-initial `qo`
  rates would otherwise inflate R by composition).
- **Null:** within-folio *pairing* permutation — the next-prefix column of the pairs of that
  class is permuted among the pairs of the same folio (preserves both edge marginals per
  folio, line/paragraph positions and folio vocabulary; destroys only the pairing).
  1,000 permutations, seed 20261190; `p = (1 + #{R_MH,null ≥ R_MH}) / 1001`; null mean and
  97.5% quantile reported.
- **Persistence ratio:** `ρ = ln R_MH(line break) / ln R_MH(within line)` on the same
  population; folio bootstrap (10,000 resamples of folios with replacement, seed 20261019,
  both ratios recomputed per resample), percentile 95% CI; resamples with a non-positive
  logarithm are dropped and their fraction reported.
- **Whole-table check (reported, no decision):** mutual information `I(S; prefix)` over the
  line-break pairs vs. 200 random within-line subsamples of equal size (seed 20261191),
  each minus its own one-permutation pairing null; the ratio of the two excesses says whether
  the diffuse remainder of the coupling (E021) crosses the break as well as `y → qo` does.

### 2.3 Decisions (fixed before any conditional statistic)
Decision population for H034/H035: **bio_B** (largest within-line effect, 622 line-break
pairs, 324 after `y`, line-initial `qo` rate 0.25 = overall rate, so the comparison is not
starved). `other_B` and `A` are reported with the same statistics, no decision.

- **H034 — the dominant transition crosses the line break.** `SUPPORTED_DEV` iff
  `R_MH ≥ 1.5` and `p ≤ 0.01`; `FALSIFIED_DEV` iff `R_MH ≤ 1.1` or the null's 97.5% quantile
  `≥ R_MH`; else `INCONCLUSIVE_DEV`. (Thresholds as E018 H003a.)
- **H035 — it crosses undiminished.** `SUPPORTED_DEV` iff `ρ ≥ 0.75` and CI lower `≥ 0.5`;
  `FALSIFIED_DEV` iff CI upper `< 0.25` or H034 is `FALSIFIED_DEV`; else `PARTIAL`.
- **H036 — coupling across paragraph breaks** (population `B_pooled`, 357 pairs, 175 after
  `y`; R_MH is folio-stratified, so pooling is admissible): `SUPPORTED_DEV` iff `R_MH ≥ 1.5`
  and `p ≤ 0.01`; `FALSIFIED_DEV` iff the null's 97.5% quantile `≥ R_MH` **and** `n_after_y ≥
  100`; else `INCONCLUSIVE_DEV`.

### 2.4 Pre-freeze marginals (feasibility; no conditional quantity)
| population | lines | within-line pairs | line-break pairs (after y) | paragraph-break pairs (after y) | P(qo \| line-initial) vs P(qo) | P(y-final \| line-final) vs P(y-final) |
|---|---|---|---|---|---|---|
| bio_B | 745 | 5,324 | 622 (324) | 61 (42) | 0.252 vs 0.245 | 0.537 vs 0.534 |
| other_B | 1,678 | 14,143 | 1,180 (424) | 296 (133) | 0.068 vs 0.152 | 0.384 vs 0.419 |
| A | 1,557 | 8,976 | 1,180 (395) | 104 (41) | 0.132 vs 0.096 | 0.340 vs 0.316 |

`qo` is depleted at line starts in other_B and enriched in A; the pairing null and R_MH
condition on these marginals, so they cannot produce a spurious R_MH.

## 3. Pre-result predictions (recorded before the run)
- H034: `SUPPORTED_DEV`, R_MH ≈ 2–3 in bio_B (attenuated against the within-line 6.07).
- H035: `PARTIAL`, ρ ≈ 0.4–0.7. Reasoning: the coupling is one probabilistic transition plus
  a diffuse remainder (E021); a stream account predicts ρ ≈ 1, a within-line scribal
  convention ρ ≈ 0; the hedge is deliberate and will be scored as wrong if either extreme
  obtains.
- H036: `INCONCLUSIVE_DEV`, R_MH ≈ 1–1.5 (small n; paragraphs expected to be units).
- Whole-table excess ratio ≈ 0.3–0.6; other_B and A ordered as within lines (other_B > A).

## 4. Interpretation rules (fixed)
- H034 `SUPPORTED_DEV` **and** H035 `SUPPORTED_DEV`: the token sequence behaves as one stream
  across lines; line-as-unit accounts and within-line scribal-convention accounts are
  disfavoured as sufficient; stream accounts (E019–E021 family) gain.
- H034 `FALSIFIED_DEV`: the line is a conditioning unit; every stream account must add a
  line-reset, and generators with line structure (grille rows, line conventions) gain.
- H035 `PARTIAL`: both a cross-line dependency and a line-specific component exist; the
  mechanism target (E021 §5) gains a line-break attenuation factor ρ that any proposal must
  reproduce.
- H036 `SUPPORTED_DEV` would mean the stream ignores paragraph structure (unexpected).

## 5. Degrees of freedom, confounds, registration
- No free parameters: thresholds inherited from E018; populations and classes fixed above;
  seeds fixed. Line-initial/line-final marginal effects (Grove-word-type conventions, `m`/`g`
  finals) are absorbed by the pairing null and by R_MH. LFD hand is not separated (bio_B is
  essentially one hand); reported descriptively if feasible, no decision.
- Uncertain readings excluded at both edges; the exclusion count is reported.
- `experiment.json` records sha256 of input, of this plan and of the predictions. Independent
  `validate.py` recomputes pairs, R_MH, permutation p-values and decisions from the raw file.
- Claim ceiling: structural transition statistics across line and paragraph breaks; nothing
  about meaning, language, or what `y`/`qo` are. Negative results stay in the ledger.
