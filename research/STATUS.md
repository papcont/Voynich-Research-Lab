# Current research status

## Claim ceiling

**Structural analysis only. No accepted plaintext, language identification, phonetic key or semantic lexicon.**

## Token-edge state

The most important edge phenomenon is a short-memory relationship between the end of one visible token and the beginning of the next. `y -> qo` is a major candidate. This does not imply that `q` means a specific article, preposition or sound.

## Compositional/token grammar

Repeated families support structural decomposition tests:

- `qokal / okal`
- `qokar / okar`
- `qokey / okey`
- `qokedy / okedy`
- `qokeedy / okeedy`

Right-side families include `ar/al/aiin/or/ol/am` and B-heavy `dy/edy/eedy`. These are structural candidates, not translated morphemes.

## Regime, hand and section

Currier A/B differences are not reducible to different people writing differently, but hand/section/regime remain confounded enough to require joint controls.

## Variable attachment

Candidate pairs already discovered in ZL3b:

- `otar.ar` and `otarar`
- `otar.al` and `otaral`
- `otar.aiin` and `otaraiin`
- `otar.am` and `otaram`
- `okar.ar` and `okarar`
- `okar.al` and `okaral`

The stronger claim — same underlying unit sequence — has **not passed a context-based holdout test**.

## Weak/rejected simple models

- deterministic A `y` <-> B `dy`: rejected;
- q as universal prose-only marker: rejected;
- q as mandatory line-start marker: rejected;
- delete q and reveal ordinary phrases: not supported;
- merge all predictable token boundaries into larger words: not supported.

## Current frontier

**E020 complete.** A verbose stream in which **80% of word boundaries are kept and 20%
are placed at random** reproduces the manuscript's cross-boundary coupling level in both
Copiale (0.200, calibration) and Italian (0.162, out-of-sample; target 0.178) → **H030a
SUPPORTED** with one calibrated parameter. It does *not* reproduce line position, local
copying or vocabulary (2 of 6 components; **H030b PARTIAL**), and the frozen selectivity
rule turned out to measure alphabet structure rather than transition selectivity
(**H030c retired**). So "mostly-but-not-entirely word-aligned boundaries" is an adequate
account of one component only; the manuscript's one-transition selectivity (E018) remains
unreproduced by any process tested.

**E019 complete — boundary placement is the lever.** Encodings of open-rights prose that
keep word boundaries (homophonic, verbose, monoalphabetic) never produce the manuscript's
cross-boundary coupling (≤ +0.01; homophony −0.16/−0.20); cutting a continuous letter
stream into Voynich-length tokens produces 2.5× too much (+0.43/+0.46 vs +0.178) and, as a
side effect, a line-position effect of the manuscript's size (+0.05 vs +0.06). Vocabulary
explodes under stream cuts unless the stream is verbose (TTR 0.58, H1 0.73 vs 0.39/0.70).
H029a PARTIAL, H029b FALSIFIED. Registered follow-up (E019-B): partly word-aligned
boundaries on a verbose stream, alignment fraction calibrated on Δ_S′, the other six
components tested as predictions; Borg's real cipher when approved. Not reproduced by any
transform: the manuscript's selectivity (one dominant `…y → qo…` transition, E018).

**E012 stage B-open complete — first comparison with natural language.** Under a
script-agnostic signature (first/middle/last-character slots) at matched size (3,660
tokens), **no natural text matches the manuscript** (H027 FALSIFIED): the manuscript's
cross-boundary coupling (first character | previous last character, **+0.178** bits/token)
is an order of magnitude outside German, English, French and Italian prose (−0.07 to
+0.01), and its line-position effect (+0.061) is absent in Copiale's real manuscript lines
(−0.038). **Vocabulary statistics do not separate it from prose** at matched size (TTR
0.39 vs 0.25–0.45; hapax 0.70 vs 0.58–0.75) — the earlier inventory contrasts were against
generators, not language. Natural prose also gains nothing from the local-copy model, so
Δ_C is not a language/manuscript discriminator either. Substitution invariance exact
(H028). Nearest text: Copiale. Two of four predictions were wrong in detail (recorded).

**E018 complete.** The historical y → qo observation is quantified: after a `y`-final
token the next prefix is `qo` **6.1×** as often in Biological-section B (40.1% vs 6.6%,
permutation p < 0.001), 3.7× in other B sections, 2.2× in Currier A → **H003a
SUPPORTED_DEV**; the binary y/not-y feature carries **72%** of the Currier-B edge-state
codelength gain (0.124 of 0.171 bits/token) → **H003b SUPPORTED_DEV**. The "edge state"
component of the structural inventory is therefore mostly one graded, population-wide
transition with the Biological section as its extreme.

Retained structural components after E006–E016 (all development-stage, all validated):
four-slot token form (E007/E013); edge state → next prefix, mostly y → qo, graded Bio-B > B > A, absent in natural prose at letter level (E011/E010/E018/E012);
no local copying, self-citation excluded at every horizon (E008/E014/E015); line-position
not predictive, text line-homogeneous (E011/E015); folio-local vocabulary (E016); weak
codex-order locality, leaf not a unit (E017);
epilectrik's boundary coupling reproduced, its class grammar not predictive (E010).

**E015 complete.** Signature v2 (Δ_S, Δ_L, Δ_C + TTR, hapax share H1, within-folio
repetition F, cross-folio sharing X) vs three generators on the ZL3b skeleton: G4
edge-coupled, G5 edge-coupled + Pitman–Yor vocabulary, G6 folio-horizon self-citation —
**all MISMATCH**; H022/H023 falsified. Robust pattern: every edge-coupled generator
*overshoots* the edge gain (0.14–0.15 vs 0.088); every self-citation generator leaves a
large local-copy signal the manuscript lacks (+1.6 to +2.9 vs −0.46); a vocabulary-growth
process reproduces cross-folio sharing (X) but not within-folio reuse (F 0.17 vs 0.24).
Simple family-G generators are excluded; F is the discriminator to carry into E012.

**E014 complete.** Four non-semantic generators on the ZL3b folio/line skeleton vs the
Voynich component signature (Δ_S +0.088, Δ_L −0.026, Δ_C −0.463): independent slots
MISMATCH; token unigram PARTIAL; **self-citation MISMATCH** (Δ_C +2.93 bits/token — the
real text has no local-copy gain at all) → H020 FALSIFIED; **edge-coupled slot generator
PARTIAL** (matches L and C, overshoots S: 0.144 vs 0.088) → H021 PARTIAL. The three
components separate Voynich from a shallow edge-coupled generator by only 0.056 on one
component; type-inventory growth (TTR 0.193 / hapax 0.669 vs ≈ 0.14 / 0.40 for token-
sampling generators) is the stronger discriminator and must join the E012 signature.

**E013 complete — the first Gate v2 claim was stopped at registration, correctly.** P70 vs
whole-token on the 710 label/circular/radial tokens (never coded before): +2.20 bits/token
from scratch with model bits charged (CI 0.99–3.50, 30/39 folios), but the gate found that
every lockbox folio carries a SELECTION role through its running text; the registry had
mislabelled the pool INDEPENDENT (corrected: SEMI_INDEPENDENT, A001 erratum 2). H019 is
SUPPORTED_DEV only. Also: on labels the suffix slot is dead weight — A6 (no suffix) 26.39
and A1 27.48 beat P70 28.40 total bits/token from scratch; with running-text counts P70 is
best (21.35). **Under the folio rule, ZL3b offers no independent lockbox for any claim.**

**E010 complete.** epilectrik's boundary glyph coupling reproduces on our pipeline to within
0.002 bits (0.2548 all / 0.2134 definite vs 0.256 / 0.215) and their class table covers
71.3% of B tokens (published 69.5%). Under the E011 scorecard on Currier B their refinements
add nothing: glyph units vs EVA characters −0.0007, last two units +0.0012, and the 49-class
table costs 3.08 bits/token (class → class transitions add nothing). H016–H018 falsified
(development-stage). Upstream's measurement is solid; its grammar is not predictive.

**E011 complete (development-stage).** Prefix slot | previous final glyph: +0.088 bits/token
(CI 0.073–0.102; B +0.166 > A +0.035; permutation control removes it) → H014 SUPPORTED_DEV;
line position −0.026 → H015 FALSIFIED_DEV. Registered strongest structural null for the
running-text development pool: M_Sfam 13.813 / M_S 13.829 vs P70 13.967.

Earlier: E008 stage A ALL_COMPONENTS_NOT_INFORMATIVE (no-backoff scorecard; see REPORT);
E007 REPRODUCED_BUT_NOT_VALIDATED; E006 INCONCLUSIVE_UNDERPOWERED.

Two human decisions are pending: (1) a confirmation surface or a protocol tier for
semi-independent lockboxes (A001 erratum 2); (2) E012 corpora/licences. Development-stage
work can continue meanwhile (see RESEARCH_STATE.json).

## Tooling

`voynichlab.signature` (2026-10-20): one hypothesis-neutral module for the seven-component
structural signature, fixture-tested and regression-tested against E011/E014/E016/E017.

## External landscape check (2026-10-19)

Landing pages and commit lists only; nothing audited or accepted. Details and
observed upstream heads in `external/repos.yml`.

- **Voynichdecomp** (E007 upstream) moved past our pin to `b4f4995` (Super
  Grammar v03, bifolium/ordering tests, PREREG 1–38, retractions R1–R6). E007
  stays frozen on `4f8a1117…`; testing Super Grammar would need a separate
  preregistration.
- **Voynich-Deshuffling-Matrix** (E009 upstream) is **unreachable** (404 /
  auth). No local spec copy → E009 needs a human provenance decision before
  freeze.
- **New structural competitor:** `epilectrik/voynich` reports a single Currier-B
  token grammar (49 classes, 69.5% coverage, line-position zones, boundary
  coupling) after a 2026-09-27 self-review that retracted several earlier
  claims. Overlaps H002/H003/H005; candidate for E008 after independent
  reimplementation.
- **New generator/cipher baselines for E008:** Naibbe cipher (Greshko,
  Cryptologia 2025; no code located) and arXiv:2609.20835 (pastiche /
  generative-grammar hypothesis; not inspected).
- No external work reports an accepted decipherment.
