# E021 — selectivity of the boundary coupling and selective boundary processes (FROZEN PLAN)

Status: **PLAN_FROZEN** (2026-10-20). **No E021 metric has been computed.** Evidence class:
MECHANISM_DEMONSTRATION / DEVELOPMENT; no lockbox; no Gate level. Known: all E012/E019/E020
Signature-G values; E018's prefix-level finding that `y`/not-`y` carries 72% of the edge
gain and `y → qo` is 6× enriched in Biological B.

## 1. Question

E020 showed that randomly placed boundaries reproduce the *level* of the manuscript's
cross-boundary coupling but its selectivity rule was confounded. Two questions, with a
measure that does not depend on alphabet size:

(a) How concentrated is the manuscript's boundary coupling in a single transition, compared
with prose, stream cuts and the E020 mixture? (b) Can a *selective* boundary process —
boundaries conditioned on a letter class, or explicit marker pairs at boundaries — reproduce
both the coupling level and its concentration on a held text?

## 2. Selectivity measure S1 (frozen)

Over all within-line boundaries (previous token certain, next token certain; BOL excluded),
let `a` = previous token's last character, `b` = next token's first character.
`I = I(a; b)` (plug-in mutual information, bits). For each pair (a\*, b\*):
`I_pair = I(1[a = a*]; 1[b = b*])`. **S1 = max over pairs of I_pair / I**; the maximising
pair is reported. S1 is the share of the boundary information captured by one binary
contrast; it is invariant to relabelling and insensitive to alphabet size. Computed on the
size-matched (3,660-token) texts; full-size reported for Voynich.

## 3. Texts

Voynich (E012 size-matched); plaintexts N_DEU, N_ITA; C_STREAM(N_DEU), C_STREAM(N_ITA)
(E019, from `runs/E019/`); MIX(0.8)(N_ITA) (E020, `runs/E020/`); and two new selective
processes on the verbose streams (E019 C_VERB), calibrated on N_DEU and predicted on N_ITA:

- **SEL_L(q)** — letter-conditioned cuts: keep all word boundaries; additionally insert a
  boundary *after every occurrence of the code of the most frequent letter* of the source
  (determined on the source plaintext) with probability q. Grid q ∈ {0.1, …, 1.0}.
- **SEL_M(r)** — marker pairs: at a fraction r of word boundaries, append the marker symbol
  `Y` to the end of the word and prepend `Q` to the next word (two new symbols; token
  count unchanged, two tokens lengthened). Grid r ∈ {0.1, …, 1.0}.

Calibration (N_DEU, size-matched): for each process choose the grid value minimising
|Δ_S′ − 0.178| (ties → larger value); recorded before any N_ITA value. Seeds 20261130 +
grid index (SEL_L), 20261150 + grid index (SEL_M); prediction seeds 20261170 / 20261171.

## 4. Decisions (frozen)

- **H031** (the manuscript is selective where boundary noise is not): `SUPPORTED` iff
  S1(Voynich) ≥ S1(x) + 0.10 for every x in {N_DEU, N_ITA, C_STREAM(N_DEU), C_STREAM(N_ITA),
  MIX(0.8)(N_ITA)}; `FALSIFIED` iff any x has S1(x) ≥ S1(Voynich); else `PARTIAL`.
- **H032** (a marker-pair process reproduces level and concentration): on N_ITA at r\*:
  `SUPPORTED` iff |Δ_S′ − 0.178| ≤ 0.05 **and** |S1 − S1(Voynich)| ≤ 0.10; `FALSIFIED` iff
  either deviates by more than twice its tolerance; else `PARTIAL`.
- **H033** (a letter-conditioned cut process reproduces level and concentration): same
  rule for SEL_L at q\*.

Pre-result predictions: S1(Voynich) ≈ 0.3–0.5 with pair (y, q) at letter level; prose,
stream cuts and MIX ≤ 0.15 → **H031 SUPPORTED**. SEL_M: level calibrates (r\* ≈ 0.3–0.5) and
S1 lands high (the marker pair *is* one contrast) → **H032 SUPPORTED** — showing that an
explicit boundary-marker convention is a sufficient mechanism for both edge properties.
SEL_L: level calibrates but S1 stays moderate (cuts after one letter still face many
following letters) → **H033 PARTIAL or FALSIFIED**. None of this touches vocabulary or
line position, which remain the open components.

## 5. Degrees of freedom, retraction

One calibrated parameter per process (grid, one component, one text). H032 FALSIFIED
retires explicit marker pairs as a sufficient mechanism for the edge properties; H031
FALSIFIED means the manuscript's selectivity is not special.

## 6. Registration and claim ceiling

`experiment.json` records sha256 of inputs (E012 corpus hashes), config, predictions.
Claim ceiling: which boundary processes reproduce which structural properties; no
decipherment, no language identification, no Gate level; `Y`/`Q` are abstract symbols,
not readings of `y`/`qo`.
