# E013 — first Gate v2 lockbox claim: P70 four-slot model on the independent non-running text (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20)
Freeze rule: every scientific choice is fixed here before any lockbox number is computed.
**No E013 metric has been computed.** Inspected before freeze: lockbox population facts only
(710 strict tokens on 39 folios, 529 types, locus types L 493 / R 217, Currier A 126 / B 167 /
none 417, token-length distribution, per-folio token counts from 1 to 71).

Hypothesis **H019**: the P70 layer-A four-slot factorization, frozen in E007 on running text,
transfers to ZL3b's label/circular/radial text: it describes that text in fewer bits than
whole-token coding by at least the registered margin.

Gate v2 target: **`STRUCTURAL_MODEL_VALIDATED`** (level 1) on `LOCKBOX_NONRUNNING_V1`
(`research/holdout_registry.json`, sha256 `6c7ae53325d917a2982d504d5ea47c55ff485ed130a6d8f1a27173eb590aa2a6`,
`INDEPENDENT`: no committed experiment has ever coded these tokens). No higher level is
claimed or claimable (no mechanism, no plaintext).

## 1. Lockbox, order, population

- Source `data/raw/ZL3b-n.txt` (blob `2a4533ab…`). Lockbox tokens = strict tokens
  (`iter_strict_tokens`) on loci that are **not** running text (`loci.is_running_text` false:
  labels `L*`, circular `C*`, radial `R*`). All 39 folios, all 710 tokens; no exclusion by folio
  size (the registry defines the lockbox; the gate's folio-level CI is run on all folios and
  the resulting power is whatever it is).
- Frozen order: folios lexicographic, file order within folio (sensitivity: natural order,
  reported). Σ = character set of the lockbox tokens (recorded).
- Lockbox text hash = sha256 of `"\n".join(tokens)` in frozen order; every model must
  reconstruct it exactly.

## 2. Models (all frozen in E007 — no change)

Candidate **P70**: `(p, g, c, s)` via `voynichlab.p70.parse_p70`, plain KT with char escape
(`mdl.KTCoder`), slot context = `(i, preceding slots)`. Null **A0**: whole token, one KT
context. Competitors (reported; stricter preregistered rule below): **A1, A2, A3, A5, A6,
A7, A8** exactly as E007 `run.py` (A8: deterministic sha256 cut with the slot-length profile
estimated on the **running-text development pool** — all 206 running-text folios — never
on the lockbox). Model bits per E007 Amendment 001 §4 (P70 inventories 728.9 bits at
|Σ| = 25; recomputed for the lockbox Σ), split into Gate v2 components: `mechanism_code_bits`
= inventory + slot-count cost; `dictionary/key/exception/residual/transmission_bits` = 0,
declared.

## 3. Arms

- **Primary (pure MDL on the lockbox):** every model starts with empty counts and codes the
  710 tokens prequentially in the frozen order. This is the description length of the
  observed lockbox text, with model bits added for the candidate (and competitors).
  No side information.
- **Secondary (transfer with side information, reported):** counts trained prequentially on
  the running-text development pool, frozen, then the lockbox coded without updates.

## 4. Statistics and decision (Gate v2 compression semantics)

Per folio f: `Δ_f = (A0_total_bits_f − P70_total_bits_f) / n_f` with model bits allocated
per token (`model_bits × n_f / N`), from the primary arm. Folio-mean, percentile bootstrap
(10,000, seed 20261019, 2.5/97.5%). `n_folios = 39 ≥ 20`.

**Margin: 0.5 bits/token** (Gate v2 provisional default). Calibration and justification,
development data only: on the running-text pool P70 beat A0 by 1.87 bits/token (E007 global
prequential) and by 1.69 in the E007 dev→holdout arm; A8 (complexity-matched random cut)
retained 0.95 of that. A transfer that retains at least about a quarter of the development
effect (0.5) is claimed; smaller retained effects are reported, not claimed.

Gate decision (as `voynichlab.gate.compression_test`): PASS iff mean ≥ 0.5 and CI lower > 0;
FAIL iff CI upper < 0.5; else INCONCLUSIVE. **Stricter preregistered rule for our own
label:** `STRICT_PASS` additionally requires P70's primary-arm total bits/token to be strictly
lowest among {A0, A1, A2, A3, A5, A6, A7, A8} on the lockbox; otherwise the gate result is
reported with `COMPETITOR_BEATS_P70: <name>`.

Specificity controls are **not** required at level 1 (a structural model is expected to
gain on permuted text too); the within-folio token-permutation control is computed and
reported for the record, and the claim record carries it so the gate shows level 2 as
`NOT_TESTED`/`FAIL` correctly (no mechanism block is supplied).

## 5. Pre-result predictions

- P70 − A0 ≥ 0.5 with CI lower > 0 (**PASS predicted**): 74% of lockbox tokens are unique,
  so whole-token coding pays the char code for most tokens, while P70 re-uses closed
  prefix/gallows/suffix inventories; predicted Δ in the range 1–4 bits/token.
- Competitors: predicted ordering as on running text (A7, A5 closest; A8 and A1–A3 further);
  `STRICT_PASS` predicted but not certain (A7 was only 0.18 below P70 on running text).
- Secondary arm: larger Δ than primary (running-text counts transfer).

## 6. Retraction condition

If the gate result is FAIL, H019 is retracted: the P70 factorization is recorded as **not
transferring** to label/circular/radial text, and E007's running-text result is unchanged.
INCONCLUSIVE leaves H019 open; no second attempt on this lockbox without a new
preregistration and a new lockbox.

## 7. Registration

`experiment.json` records sha256 of inputs (ZL3b), split (registry lockbox hash), config (this
file), predictions (§5). The null for the pool is registered in
`research/gate/registered_nulls.json` **in the freeze commit**. Claim record
`claim_E013_P70.json` → `scripts/gate_report.py` → `GATE_REPORT_P70.md`.

## 8. Claim ceiling

> "On ZL3b label/circular/radial text, never used in any prior analysis, the P70 four-slot
> factorization describes the text in Δ fewer bits per token than whole-token coding (CI)."

Structural model only: not morphemes, not language, not cipher, not meaning; a level-1
state in Gate v2 terms, nothing above it. Degrees of freedom: none (every choice inherited
from E007 or fixed here).
