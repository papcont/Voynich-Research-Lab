# E021 — REPORT (interpretation, written after results.json)

**The manuscript's boundary coupling is neither diffuse nor a marker: one binary contrast
(`y` → `q…`) carries 23% of the boundary information (28% at full size), against 6–14% for
prose, stream cuts and the E020 mixture (H031 PARTIAL: above every reference, one by less
than the 0.10 margin). An explicit marker-pair convention overshoots on both axes even at
the lowest grid value (coupling 0.44 vs 0.18; S1 0.98 vs 0.23) → H032 FALSIFIED. Letter-
conditioned cuts cannot even reach the coupling level (max 0.036) → H033 FALSIFIED.**

Plan `d399697`; one run; independent `validate.py` (own MI tables and contrast search):
`E021_VALIDATION_PASS`. Development stage; open-rights sources; size-matched at 3,660
tokens where applicable.

## 1. Selectivity S1 (share of the boundary mutual information captured by one binary contrast)

| text | S1 | top contrast (prev. last → first) |
|---|---|---|
| **Voynich** (size-matched / full) | **0.233 / 0.284** | **y → q** |
| Copiale plaintext | 0.059 | t → i |
| Italian plaintext | 0.103 | d → e |
| stream re-cut (Copiale / Italian) | 0.143 / 0.058 | c → h |
| MIX(0.8) Italian (E020) | 0.127 | B → B (verbose code artefact) |
| SEL_L(0.9) Italian | 0.790 | A → A (code artefact; no coupling to speak of) |
| SEL_M(0.1) Italian | 0.982 | Y → Q |

Predicted S1(Voynich) 0.3–0.5 with pair (y, q): pair ✔, level somewhat lower (0.23).
Predicted references ≤ 0.15 ✔.

## 2. Calibration on Copiale and predictions on Italian

| process | grid Δ_S′ (Copiale) | chosen | Italian Δ_S′ | Italian S1 | verdict |
|---|---|---|---|---|---|
| SEL_L(q): extra cut after the most frequent letter's code with prob q | 0.010 … 0.036 (never near 0.178) | q = 0.9 | 0.013 | 0.79 (artefact) | FALSIFIED |
| SEL_M(r): `Y`/`Q` marker pair at a fraction r of word boundaries | 0.419 (r = 0.1) … 0.984 (r = 0.6) | r = 0.1 | 0.437 | 0.982 | FALSIFIED |

The SEL_M grid's lowest value is already 2.4× the target; a marker pair at ≈ 2–4% of
boundaries might calibrate the level, but its S1 would stay ≈ 1 (a deterministic pair
concentrates everything), which is the opposite of the manuscript's 0.23.

## 3. Reading

1. **The manuscript sits between two extremes it is not.** Random boundary processes give a
   coupling spread over the whole table (S1 ≤ 0.14); an explicit boundary marker gives a
   coupling concentrated in one deterministic pair (S1 ≈ 1). The manuscript has one
   *probabilistic* dominant transition (`y` → `q…`: after `y`, `qo` 40% in Biological B,
   E018) and a diffuse remainder — a quarter of the boundary information in one contrast.
2. Together with E019/E020: the boundary process must be **mostly aligned with some unit,
   partly not, and biased toward one transition without being deterministic**. Neither
   "spaces are random nulls" nor "`y`/`qo` are a marker pair" survives as a sufficient
   account; a rule with a strong but incomplete preference (e.g. a convention applied by a
   scribe inconsistently, a state-dependent encoding, or phonotactics of an underlying
   system in which `y`-final units attract `qo`-initial ones) is what the numbers describe.
3. Letter-conditioned cuts are not a route to the coupling at all in a verbose stream:
   where the cut falls is then predictable, but what follows is not.

## 4. Predictions vs outcome

H031 predicted SUPPORTED, got PARTIAL (Copiale stream cut 0.143 is within 0.10 of 0.233).
H032 predicted SUPPORTED — **wrong**: a marker pair is far too strong and too concentrated.
H033 predicted PARTIAL/FALSIFIED ✔.

## 5. Consequences

- H031 PARTIAL, H032 FALSIFIED, H033 FALSIFIED. The marker-pair reading of `y`/`qo` is
  excluded as a sufficient mechanism in its simple form.
- Quantitative target registered for any mechanism: at matched size, Δ_S′ ≈ 0.18, S1 ≈
  0.23 with a single dominant probabilistic transition, TTR ≈ 0.39, H1 ≈ 0.70, a positive
  line effect, and no local-copy gain.

Claim ceiling: which boundary processes reproduce which structural properties; `Y`/`Q` are
abstract symbols; development stage; no decipherment, no language identification, no Gate
v2 level.
