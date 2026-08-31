# E007 — independent P70 four-slot grammar replication (FROZEN PLAN)

Status: **PLAN_FROZEN**
Freeze rule: this file fixes every scientific choice before any E007 target
metric is computed. **No E007 metric has been computed at freeze time.** Only
the upstream specification was read. Implementation (`src/voynichlab/p70.py`,
`run.py`, `validate.py`) and all metrics belong to the next cycle.

Hypothesis under test: **H009** (the P70 four-slot factorization is a uniquely
/ better explanatory description of the Voynich surface-token inventory).

---

## 0. Upstream audit (pinned commit)

Repo `digitalgoldfisj79/Voynichdecomp` @ `4f8a11174189148f312205d088910361ee67bde6`.
License: MIT for code+data (VMS public domain) — reimplementation from the
published spec facts is permitted; we reimplement, we do not copy code.

Files inspected: `README.md`, `p70_grammar_validation.py`,
`p70_rules_canonical.json`, `voynich_section_map.json`, tree schema of
`enriched_records.json/.pkl`, `voynich_transcriptions_slim.json`.

**Specification-sufficiency finding — the spec is dual-layer:**

- **(A) Independently reconstructible layer.** A compact closed-inventory
  longest-match parser (inventories in §5) with core = residual. The README and
  `p70_grammar_validation.py` both describe this greedy parser; it is fully
  reconstructible without upstream data. **E007 R1/R2 implement layer (A).**
- **(B) Canonical-rules layer.** `p70_rules_canonical.json` is a
  section-conditioned **weighted rule system** (schema `P70-canonical-sections`,
  210 rules = 109 p69 + 71 p70, `allow`/`deny` per section, `base_weight`,
  `boundary_weight`, `coverage_weight`, `boundary_role`). It is **not** a closed
  inventory and **not** a per-token lookup; it resolves ambiguous parses via
  section-weighted scoring and produced `enriched_records`. Layer (B) is **not**
  reconstructible from prose. If exact reproduction of `enriched_records` is
  required, `p70_rules_canonical.json` would be used as a **FIXED EXTERNAL MODEL
  INPUT** and the result labelled "we replicate the fixed published model, we do
  not rediscover it." **E007 does not implement layer (B) this program**; it is
  named as an optional fixed-input reproduction cross-check only.

Their published validator uses the grammar's **own** entropy profile
(`H(p)=2.788 H(g|p)=1.374 H(c|p,g)=3.622 H(s|p,g,c)=2.527 Total=10.311`) as the
success target and loads `enriched_records.pkl` (hardcoded
`/home/claude/Voynichdecomp/...`). We do **not** adopt that target; see §4.

**Transcription-version mismatch:** P70 was built on ZL_ivtff_**2b** (voynich.science,
37,465 tokens / 7,598 types). Our corpus is ZL3b-n (**3b**, blob
`2a4533ab…`). Exact count reproduction is therefore **not expected**; R1 tests
approximate/directional reproduction of structural values on our ZL3b.

---

## 1. Three separated arms (do not mix evidence classes)

| Arm | Question | Evidence class |
|-----|----------|----------------|
| **R1** | Can an independent implementation of the published closed-inventory parser reproduce P70's key structural values (approximately, on ZL3b)? | `EXTERNAL_REPLICATION / REPRODUCTION` |
| **R2** | Under a fair, externally-defined predictive-codelength benchmark, does P70 generalize better than predeclared alternative segmentations? | `EXTERNAL_MODEL_EVALUATION` (adversarial retrospective benchmark) |
| **R3** | Does the structure hold on an independently-maintained transcription / real representation transfer? | `EXTERNAL_REPLICATION / TRANSFER` — **DEFERRED** (see §11) |

**Non-prospectivity statement (mandatory honesty):** P70's inventories and
rules were derived on the *whole* VMS. A folio split *inside* ZL3b does **not**
make P70 a previously-unseen hypothesis. The E007 held-out split provides only a
**common predictive comparison surface** for all models; it is **not** evidence
that P70's architecture was unseen. No confirmatory/"validated holdout" language
will be attached to P70's architecture. No genuine prospective validation exists
here, and this plan says so explicitly.

---

## 2. Zero-entropy-residual note (frozen)

For any lossless deterministic factorization `W ↔ (P,G,C,S)`, the Shannon chain
rule gives `H(W) = H(P) + H(G|P) + H(C|P,G) + H(S|P,G,C)` exactly. A "zero
residual" is therefore a **mathematical identity**, not evidence, not an
independent P70 success, and **not a pass gate**. Likewise, "alternative X is N
bits from P70's entropy profile" is **rejected as a primary quality measure**,
because it makes P70's own profile the target and rewards mere similarity to
P70. The primary objective (§4) is external to P70's profile.

---

## 3. Data-leakage ledger (frozen)

| Source of knowledge | Used by original P70? | Used by our impl? | For training? | For evaluation? | Evidence class |
|---|---|---|---|---|---|
| ZL3b-n.txt corpus (blob `2a4533ab…`) | no (they used 2b) | yes | prequential/dev only | yes (held-out) | our corpus |
| P70 README/spec inventories (§5) | yes (defined there) | yes (reimplemented) | model definition (fixed, not fit) | model definition | external spec |
| `p70_rules_canonical.json` (layer B) | yes | **no** (not implemented; optional fixed input only) | no | no | external model artefact |
| `enriched_records.*` | produced by them | **no as labels**; optional final reproduction cross-check only | **never** | reference-output compare only | external reference output |
| `voynich_section_map.json` | yes | maybe (section labels for A/B & section diagnostics) | no | stratification only | external metadata |
| our E007 held-out folds | n/a | yes | freeze-after-dev arm | yes | our split |
| `voynich_transcriptions_slim.json` (2b) | yes (source) | **R3 only, DEFERRED** | no | deferred | external transcription (same author family) |

Rule: `enriched_records` and layer-(B) outputs are **never** training labels and
**never** define the gold segmentation. They may only be a *published reference
output* compared against our frozen parser after implementation.

---

## 4. Primary objective (frozen): prequential (online) description length

**Primary metric = prequential predictive description length in bits per surface
token, identical estimator and escape for every segmentation model.** Lower =
better generalization/compression. This is external to P70's entropy profile and
automatically charges model complexity (a richer model pays more early
codelength).

### 4.1 Token population (frozen)
Strict tokens only — the non-uncertain tokens from
`voynichlab.ivtff.iter_strict_tokens` over ZL3b-n.txt (EVA uncertainty excluded,
consistent with E006). Running-text loci only; label loci excluded. This same
population is used for **all** models.

### 4.2 Segmentation model = deterministic function token → slot tuple
Each competing model (§6) maps a surface token to an ordered tuple of slot
values whose non-empty concatenation **exactly** reconstructs the token
(lossless). Empty slots take the literal value `∅`. Any token a model cannot
segment under its rules receives the **degenerate lossless fallback**: the whole
token in the residual/core slot, all other slots `∅`. The fallback is applied
identically to every model, so coverage never filters tokens and no model gains
by dropping hard tokens. (Coverage is an R1 metric, §10, not a filter.)

### 4.3 Prequential per-slot code (frozen, KT + char escape)
Tokens are processed in a fixed order: folios sorted ascending by folio id,
tokens in file order within a folio. Every model sees the same order.

For each token, its slots are coded left-to-right. Slot *i* is coded by a
context-conditional Krichevsky–Trofimov (KT) predictor whose **context is the
tuple of all preceding slot values of that token** (fixed slot order). For a
context `c` that has previously been seen `n` times with `m` distinct values
(counts `n_v`):

```
denom   = n + 0.5 * (m + 1)
P(seen v)  = (n_v + 0.5) / denom
P(unseen)  = 0.5 / denom
codelen(v) = -log2 P(seen v)                    if v already seen in c
           = -log2 P(unseen) + charcost(v)      if v is novel in c
```

`charcost(v) = (len(v) + 1) * log2(|Σ| + 1)`, where **Σ is the frozen EVA
character set of the ZL3b strict-token population** (computed once; recorded in
results) and the `+1` is an end-of-string symbol. After coding, counts for `c`
are updated (increment `n_v` or admit the new value). KT is a standard universal
predictor; the char escape is the same fixed universal code of a novel string
for **every** model. No tunable smoothing constant beyond KT's 1/2 is
introduced.

The whole-token baseline A0 has one slot with empty global context, i.e. a KT
code over the token stream with char escape for novel tokens — the canonical
universal code for the token sequence.

Total codelength(model) = Σ over tokens Σ over slots codelen; **primary score =
total / N_tokens (bits per surface token).** The code is prefix-free and
decodable (fixed slot order; each slot code self-delimiting), hence a genuine
lossless description length.

### 4.4 Saturation is measured, not assumed
Conditioning `S` on `(P,G,C)` etc. may make late slots fall into rare/unique
contexts → escape cost. This is exactly what the benchmark measures: if
factorization saturates to a whole-token-equivalent, P70's bits/token approach
A0's and P70 does **not** win. If factorization genuinely compresses (small
closed slots reused, only the smaller core paying char cost), P70 wins. No
post-hoc conditioning change is permitted.

### 4.5 Complexity accounting
Prequential coding charges complexity implicitly (each new symbol/context costs).
Additionally, for transparency, we report each model's fixed inventory
description cost (bits to specify its closed inventories) and the **data+model
total**; the primary comparison is the data prequential codelength, with the
data+model total reported alongside so no model hides complexity.

---

## 5. Frozen P70 spec to reimplement (layer A)

Reimplement as `src/voynichlab/p70.py` next cycle. Inventories verbatim from the
README:

- **Prefix (8):** `∅, o, y, d, s, ch, sh, qo`
- **Gallows (9):** `∅, k, t, p, f, ckh, cth, cph, cfh`
- **Suffix (33 in 7 families):**
  - Y: `y, edy, ey, eey, eedy, dy, ody, chy, shy`
  - N: `aiin, ain, iin, n, aiiin, iiin, oiin, oiiin`
  - L: `ol, al, l`
  - R: `ar, or, r, ir`
  - BARE: `∅`
  - M: `am, m`
  - OTHER: `g, he, ee, b, ai, a, e, s`
- **Core:** open residual (may be `∅`).

**Parser (frozen, deterministic longest-match):** on the surface token string,
(1) match the **longest** prefix from the prefix inventory at the start (`ch`,
`sh` are **prefixes**, not gallows — P70's key decision); (2) match the longest
gallows from the gallows inventory at the new start; (3) match the longest suffix
from the suffix inventory at the **end**; (4) the remainder is the core (`∅` if
empty). Empty slot = `∅`. A token whose non-`∅` slots do not exactly reconstruct
it, or that leaves an inconsistent parse, takes the degenerate fallback (§4.2).
EVA uncertainty: excluded upstream via strict tokens (§4.1); the parser never
resolves ambiguity silently.

Population note: P70's own counts (37,465 tokens, 52.7% empty core, total
entropy 10.311) were on ZL_2b; on ZL3b we expect *approximate* values (R1).

---

## 6. Predeclared competitors (frozen, all same estimator §4.3)

- **A0** whole token (1 slot; baseline).
- **A1** prefix + rest (P70 prefix inventory longest-match; rest = core).
- **A2** rest + suffix (P70 suffix families from end; rest = core).
- **A3** fixed-position cuts: slot1 = first char, slot3 = last char, slot2 =
  middle remainder (tokens of length < 3 → whole token in slot2, others `∅`).
- **A4** Stolfi-inspired prefix·midfix·suffix — **our fixed reimplementation**
  (documented small inventory), explicitly *not* Stolfi's exact grammar; if it
  cannot be pinned to a deterministic rule this cycle it is marked **DEFERRED**
  and excluded from the gate rather than approximated loosely.
- **A5** P70 without gallows (3 slots P·C·S; gallows folded into core).
- **A6** P70 without suffix (3 slots P·G·C; suffix folded into core).
- **A7** ch/sh **not** prefixes (P70 inventories minus `ch,sh` from prefix; such
  leading sequences fall into core) — the direct alternative to P70's key call.
- **A8** matched random-but-lossless segmentation: deterministic (seed
  `20260907`) cut of each token into 4 slots with cut positions drawn from a
  fixed distribution matched to P70's mean slot-length profile; comparable slot
  complexity, no linguistic content.

---

## 7. Physical-folio split (frozen, secondary held-out arm)

Primary (§4) is prequential and needs no split. A **secondary confirmatory
held-out arm** freezes the KT counts after development folios, then codes holdout
folios without further updates, to satisfy the explicit train/holdout
requirement and check directional stability.

Split (domain-separated from E006 so E006's holdout is not systematically E007's
development):

```
efold(folio) = int(sha256(("E007:" + folio.lower()).encode()).hexdigest(),16) % 5
DEVELOPMENT = {0,1,2}   HOLDOUT = {3,4}
```

Dependency unit = physical folio (uncertainty and fold-consistency are
folio-level, not token-level). Per-fold (5 folds) bits/token are also reported
for stability.

---

## 8. R2 decision gate (frozen; no "p<.05 ⇒ proven")

P70 earns **STRUCTURAL_SUPPORT** only if **all** hold:

1. **Reconstruction/coverage** (R1) succeeds: the parser is deterministic and
   reconstructs ≥ 99% of strict tokens losslessly (degenerate fallback counts as
   covered but is reported separately; non-degenerate parse rate reported).
2. **Beats whole-token:** primary prequential bits/token(P70) < bits/token(A0)
   by ≥ **0.05 bits/token**.
3. **Beats every predeclared nontrivial competitor** (A1–A8, excluding any
   DEFERRED) by ≥ **0.05 bits/token** in the primary metric, **or** P70 is
   strictly lowest in ≥ **4 of 5** folio folds against each competitor.
4. **Not a complexity/fallback artefact:** P70 still wins after reporting the
   data+model total (§4.5), and P70's advantage over A0 is not wholly attributable
   to core-escape bookkeeping (report core-escape bit share; P70 must still beat
   A0 on total bits).
5. **Directional stability:** P70 is lowest within **both** Currier A and Currier
   B subsets and across the major sections in `voynich_section_map`.

Outcome labels (mutually exclusive):

- **STRUCTURAL_SUPPORT** — all five hold. Max claim = §12.
- **REPRODUCED_BUT_NOT_VALIDATED** — R1 reproduces P70's own structural values
  but the predictive gate (2–5) fails (P70 does not generalize better).
- **REPRODUCTION_FAILURE** — parser cannot reproduce P70's key structural values
  even approximately.
- **SPECIFICATION_AMBIGUITY** — the published layer-(A) spec is insufficient to
  reconstruct the parser deterministically (documented as an auditable result).

Report **practical effect sizes** (Δ bits/token) and per-fold consistency, never
significance stars.

---

## 9. Nulls / baselines

A0 (whole token) is the primary baseline; A8 (matched random lossless
segmentation) is the complexity-matched null. A model must beat A8 to show its
advantage is not merely "any 4-slot lossless cut."

---

## 10. R1 reproduction metrics (reported, not validation proofs)

Token coverage; non-degenerate parse rate; reconstruction exactness; slot
inventory sizes actually used; empty-core rate (compare to published 52.7%);
chain-rule slot entropies `H(P),H(G|P),H(C|P,G),H(S|P,G,C)` and total (compare to
published 10.311, expecting only approximate agreement on ZL3b); cross-slot MI
and Cramér's V; section-wise rates. These are **reproduction diagnostics**, not
evidence that the grammar is correct.

---

## 11. R3 transfer (DEFERRED secondary arm)

Candidate independent transcription: `voynich_transcriptions_slim.json` (ZL_2b)
from the upstream repo — but it is the **same author family** (Zandbergen–Landini),
so it is a different *version*, not a fully independent *reading*. A genuinely
independent reading (e.g. a distinct interlinear/GC/Takahashi transcription) is
preferable. R3 is **DEFERRED**: this cycle does not fetch or hash an R3 source or
compute transfer metrics. A later cycle must fix source provenance + exact hash
and distinguish "independent alphabet" from "independent reading in EVA-like
units" before any R3 metric. E007 is not blocked on R3; R1/R2 are executable.

---

## 12. Claim ceiling

Even with a strong P70 result, the maximum claim is:

> "The Voynich surface-token inventory is well described by a reproducible
> four-slot structural factorization that generalizes better than the tested
> alternative segmentations under the frozen benchmark."

**Not** morphemes proven, natural language proven, notation system proven,
meaningless generator proven, language identified, or deciphered.

---

## 13. Frozen constants & non-computation statement

Inventories (§5), competitors (§6), primary KT prequential code + char escape
(§4.3), token population (§4.1), degenerate fallback (§4.2), split function/seed
(§7), decision margins 0.05 bits/token and 4-of-5 folds (§8), A8 seed
`20260907`, and outcome labels are all fixed here. **No E007 target metric,
codelength, entropy value, or reproduction number has been computed.** Results
(`results.json`) will be written before any `REPORT.md` next cycle.
