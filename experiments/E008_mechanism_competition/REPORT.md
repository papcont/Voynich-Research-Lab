# E008 stage A — REPORT (interpretation, written after results.json)

**Decision: all three components NOT_INFORMATIVE under the frozen scorecard.**
H011 (edge state S), H012 (local copy/modify C) and H013 (line position L) are
**falsified as predictive components on this corpus and this scorecard**. No
family signature (copy/modify, sequential, line-as-unit) is present under the
frozen readout. The best model remains the bare P70 slot base (B1).

Evidence class: `FROZEN_HOLDOUT` for the component contrasts (their holdout
values had never been computed); the two bases were known from E007; the P70
base is non-prospective. Source ZL3b-n.txt, blob `2a4533ab…`. Plan `9563bc4`,
amendment 001 `f71a588`, first reveal 2026-10-19. Independent `validate.py`
(own features, own copy/edit search, own KT coder, own shuffles) re-derives
every number: `E008_VALIDATION_PASS`.

Population: 33,611 running-text strict tokens, 206 folios, 4,075 lines;
development 19,483 tokens, holdout 14,128 tokens on 85 folios. W selected on
development only: W = 5 (development bits rise monotonically with W; 5 is the
grid boundary).

## Holdout bits/token (counts trained on development, then frozen)

| model | B0 base | B1 base |
|---|---|---|
| base | 16.111 | **14.422** |
| +S | 19.181 | 16.738 |
| +L | 16.878 | 15.003 |
| +C | 16.532 | 14.908 |
| +S+L | 19.636 | 17.158 |
| +S+C | 19.348 | 17.051 |
| +L+C | 17.247 | 15.457 |
| +S+L+C | 19.731 | 17.411 |

Model-description cost changes nothing (≤ 0.05 bits/token).

## Contrasts on B1 (negative = the component costs bits)

| X | marginal Δ | unique Δ | folio wins | Currier A / B | unique Δ under N1 | criterion 5 |
|---|---|---|---|---|---|---|
| S | −2.316 | −1.954 | 0 / 85 | −2.21 / −1.85 | −2.846 | ✔ (+0.89) |
| L | −0.581 | −0.360 | 13 / 85 | −0.46 / −0.32 | −0.693 | ✔ (+0.33) |
| C | −0.486 | −0.253 | 20 / 85 | −0.22 / −0.27 | −0.180 | ✘ (−0.07) |

B0 reproduces every direction (`base_dependent = false`). Criteria 1–4 fail for
all three components; verdict `NOT_INFORMATIVE` for all three.

## What the numbers say

1. **Context fragmentation dominates.** The frozen KT scorecard has no backoff:
   a slot value that is new *in its conditioned context* pays the full
   char-escape even if it is common elsewhere. Conditioning every slot on S
   (27 values) or L (4 values) multiplies contexts faster than the holdout can
   fill them. This cost was accepted at freeze (PLAN §4 inherits E007 §4.4
   "saturation is measured, not assumed"); the result is therefore valid for
   the scorecard as frozen, and it tells us the scorecard is a blunt
   instrument for conditioning hypotheses.
2. **S and L do carry information.** Criterion 5 passes for both: on real
   text the penalty is 0.89 (S) and 0.33 (L) bits/token *smaller* than on the
   within-folio shuffle, where the same contexts exist but the pairing is
   destroyed. The information is real but smaller than the fragmentation cost
   under this coder.
3. **C shows no locality-specific gain.** Real and shuffled penalties are
   equal within 0.07 bits/token; `B1+C` scores 14.908 on real and 14.915 on
   shuffled text. Exact/one-edit copies within five tokens occur in 16.8% of
   holdout tokens on real text vs 14.1% after within-folio shuffling
   (exploratory). At W ≤ 5 and with a frequency-aware base, "copy a recent
   token" adds almost nothing beyond folio vocabulary.

## Implementation erratum (recorded, verdict unchanged)

The first run used the first differing position as the insertion/deletion
index in the canonical edit string; PLAN §6.3 specifies the *smallest* valid
position. The independent validator caught the deviation (C-models only,
≤ 0.008 bits/token). `run.py` was corrected to the frozen definition and
re-run; no verdict, criterion or ordering changed. The deviating output was not
kept in the repository.

## Exploratory, post-reveal (not gated; `exploratory_post_reveal.json`)

A PPM-style backoff variant of the same coder (escape mass routed to the
unconditioned context) changes the picture only partly: on B1, +L gains
0.10 bits/token, but +S still loses 0.13. Conditioning *all* slots on the
previous final glyph is the wrong shape for the E002 claim (previous final →
next *initial* class); a targeted test should condition only the prefix slot.
These observations are hypotheses for a new preregistration, not results.

## Consequences

- H011, H012, H013 → `FALSIFIED_AS_PREDICTIVE_COMPONENT` (scorecard-specific).
  H003 (y → qo) is **not** touched: E008 did not test a prefix-only conditioning.
- Design lesson for the programme: codelength scorecards must use a backoff /
  mixture coder and hypothesis-shaped conditioning; this belongs in the next
  preregistration (E011 draft) and in the Gate v2 compression test.
- Stage B (reference corpora) remains deferred; it needs the improved
  scorecard first, otherwise every reference text would show the same
  fragmentation artefact.

Claim ceiling unchanged: structural statements only; no morphemes, language,
cipher, hoax or meaning.
