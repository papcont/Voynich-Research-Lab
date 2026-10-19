# E010 — external structural competitor stress test: epilectrik Currier-B claims (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20)
Freeze rule: every scientific choice is fixed here before any E010 metric is computed.
**No E010 metric has been computed at freeze time.** Inspected before freeze: the upstream
repository's documentation and the structure of one data file (counts of classes/types only).

Upstream: `epilectrik/voynich` @ `ff399c44c71bc38364361e51df2afbcb6b665406` (pinned in
`external/repos.yml`; local read-only clone in git-ignored `.external/epilectrik_voynich`;
"provided for research purposes", no code licence stated — nothing is copied or
redistributed; the class table is used as a **fixed external model input** and only its hash
is recorded). Evidence class: R1 `EXTERNAL_REPLICATION/REPRODUCTION`; R2
`DEVELOPMENT_CROSSFIT` (no Gate v2 level claimable: ZL3b running text has no lockbox).

Scope restriction: all of E010 is on **Currier B running text** (`$L = B`, paragraph loci),
the upstream claim's domain. Currier A is reported descriptively only.

## 0. What upstream claims (data, not accepted)

Tier-0 sentence (2026-09-28): "Currier B is written in a single, compact token grammar: 49
classes covering 69.5% of its tokens, organised by line with positional zones and
word-boundary glyph coupling …". Measurements relevant here:

- **Boundary glyph coupling** (C1212/C1563, PHASE_761 on ZL3b): shuffle-corrected MI between
  the last *glyph unit* of a token and the first glyph unit of the next token within a line;
  glyph units by the regex `c[tkpf]h|[cs]h|i+[nrlm]|.`; published ZL3b values **0.256 bits
  (all spaces)**, **0.215 (definite `.` spaces only)**; permutation baseline = mean MI over
  1,000 permutations of the right-hand units across the boundary set.
- **49 token classes** (C121/C124): `results/phase20a_operator_equivalence.json`, 49 classes
  × 480 member types (Ward hierarchical clustering on "behavioural signatures"), covering
  69.5% of B tokens on their H track; the remainder is "unclassified by exclusion". The
  merge procedure is data-derived and **not reconstructible from prose**; we replicate the
  fixed published table, we do not rediscover it.
- **Word-ending routing** (C2082): a token's last two glyphs predict the next token's class
  beyond last-glyph → first-glyph coupling.

## 1. R1 — reproduction of boundary coupling on our pipeline

Population: our strict-token pipeline (uncertain tokens excluded, both `.` and `,`
separators split), ZL3b, Currier B running text. Boundary set = consecutive strict tokens
within a line where neither is uncertain. Two sets: **all** boundaries, and **definite**
boundaries (`separator == '.'`). Statistic exactly as upstream: glyph units by the regex
above (applied to the EVA surface string), `C = MI(last_unit_left; first_unit_right) −
mean MI under 1,000 permutations of the right units` (seed **20261020**; permutation over the
whole boundary set, as in upstream's `coupling()`), with the permutation p-value.

Tolerance (approximate reproduction: our strict-token exclusion differs from upstream's
`readable()` filter): **REPRODUCED** iff `|C_def − 0.215| ≤ 0.03` **and** `|C_all − 0.256|
≤ 0.03`; **REPRODUCTION_FAILURE** iff either deviates by more than 0.06; otherwise
**APPROXIMATE**. Descriptive only; this is reproduction, not validation of any
interpretation.

## 2. R2 — their representational claims under our scorecard (development-stage)

Scorecard, population order, 5-fold cross-fit, folio bootstrap CI, margin rule and
decision labels exactly as **E011** (`BackoffKTCoder`, P70 slots, feature-permuted null,
`margin = max(0.05, q97.5 of null mean)`, SUPPORTED_DEV / FALSIFIED_DEV /
INCONCLUSIVE_DEV), restricted to Currier B folios (training and coding within B).

| model | prefix-slot feature |
|---|---|
| M_S (E011, reference) | previous token's last EVA character; BOL; UNC |
| **M_Sunit** | previous token's last **glyph unit** (upstream regex); BOL; UNC |
| **M_S2unit** | previous token's last **two** glyph units (the whole token if shorter); BOL; UNC |
| M_Sfam (E011, reference) | previous token's P70 suffix string |

Class-grammar models (fixed external table; type → class, else `UN`):

| model | coding |
|---|---|
| **M_class** | slot 0′ = class label (49 classes + `UN`) coded by plain KT; then P70 slots with the prefix slot conditioned on the class label (backoff). Lossless: the class is a function of the token, so it is redundant information that must pay for itself. |
| **M_classprev** | as M_class, but the class slot is conditioned on the **previous token's class** (BOL/UNC at line start/after uncertain) with backoff — the "grammar transition" reading. |

Primary hypotheses and contrasts (all vs the E011 reference models recomputed on B):

- **H016** (glyph units are the right boundary alphabet): `M_Sunit − M_S`.
- **H017** (word-ending routing beyond last glyph): `M_S2unit − M_Sunit`.
- **H018** (the 49-class grammar carries predictive information beyond edge state):
  `M_classprev − M_Sfam`. Secondary: `M_class − M_Sfam`, `M_classprev − M_class`.

Margins per contrast from the corresponding feature-permuted null (for H018: the class
labels permuted within folio among tokens). Model-description cost: for class models the
table is an external input; its cost is charged as `480 × charcost(mean type length) +
480 × log2(49)` bits in the Gate-style accounting (reported; the development-stage decision
uses data bits as in E011, with the cost shown alongside).

Pre-result predictions: H016 small positive or INCONCLUSIVE (the last EVA character already
separates most units; `iin`/`in` vs `n` and `ch`/`sh` vs `h` are the cases that can differ);
H017 positive if upstream's C2082 is real at the codelength level; H018: **FALSIFIED_DEV or
INCONCLUSIVE_DEV** — the class slot is redundant with the token and the clustering was not
built for prediction; a positive result would be informative.

## 3. Nulls, confounds, degrees of freedom

Feature-permuted nulls as E011 (seed 20261020). Descriptive: Currier A transfer of
M_Sunit/M_S2unit; per-section Δ within B; class coverage of B tokens on our pipeline
(compare 69.5%); share of `UN` tokens. No free parameter.

## 4. Falsification / retraction

- H016 FALSIFIED_DEV ⇒ the EVA-character edge feature stays the programme's boundary alphabet.
- H017 FALSIFIED_DEV ⇒ "word-ending routing" is not supported at codelength level here.
- H018 FALSIFIED_DEV ⇒ the 49-class table is recorded as a non-predictive description on
  ZL3b; it stays a competitor only in its coupling/zone measurements.
- No post-hoc regex changes, class-table edits, slot re-targeting or margin changes.

## 5. Registration and claim ceiling

`experiment.json` records sha256 of inputs (ZL3b; the upstream table file and the sorted
(class, type) pair list), split (E011 split restricted to B), config (this file) and
predictions (§2 last paragraph). Claim ceiling: structural, development-stage statements
about predictive information on ZL3b Currier B; nothing about operations, programs,
meaning or language. Upstream's interpretations (procedural notation, "operators") are not
evaluated and not adopted.

## 6. Deliverables

`run.py` (R1 then R2; `results.json` first), `validate.py` (independent regex/MI/coder),
`REPORT.md`. **No E010 number has been computed.**
