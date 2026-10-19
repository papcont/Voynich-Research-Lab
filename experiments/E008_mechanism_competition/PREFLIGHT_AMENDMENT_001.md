# E008 — Preflight Amendment 001 (pre-reveal implementation details)

- Date (UTC): **2026-10-19**
- Pre-reveal HEAD at authoring: **9563bc4**
- **No E008 holdout, null, subset or contrast value has been computed.** The
  only computations permitted before this amendment were population facts and
  development-only quantities (W selection, PLAN §6.4), none of which is a
  target.

Resolutions of details PLAN.md leaves open; none changes a frozen choice.

1. **Previous-token surface.** `S(t)` uses the previous element of the line's
   `tokenize_surface` list; if that element is uncertain → `UNC`; if the token
   is index 0 → `BOL`; else the last character of that element's `.value`.
2. **Context keys.** Base slot *i* of a token with slots `v` is coded in context
   `("base", i, v[:i], S or None, L or None)`; `src` in `("src",)`; `edit` in
   `("edit",)`. One `KTCoder` per (model, dataset, arm).
3. **Copy search.** For each token, `k_exact` = smallest `k ≤ 40` with an exact
   match in the same-folio window, `k_edit` = smallest `k ≤ 40` with Levenshtein
   distance exactly 1. For window `W`: `(k_exact, 0)` if `k_exact ≤ W`, else
   `(k_edit, 1)` if `k_edit ≤ W`, else `NONE`. Decodability is asserted at run
   time by reconstructing the token from `(window, src, edit)`.
4. **Model bits.** `base_bits(B1)` = Σ charcost over P70 prefixes, gallows,
   suffixes (as E007: 728.9 bits at |Σ| = 25); `base_bits(B0) = 0`;
   `+ elias_gamma(1 + n_components)`; `+ elias_gamma(W_index + 1) + 2` when C is
   on, `W_index` ∈ {0,1,2,3} for {5,10,20,40}.
5. **Development prequential order** = E007 lexicographic folio order.
   Declared sensitivity (reported only): natural folio order for the development
   pass, B1-family models only.
6. **Holdout folio scores.** `bpt_folio` over holdout folios with ≥ 1 population
   token; stability `f(X)` counts strict wins of the full model.
7. **Descriptive bins.** Line-length terciles: token-weighted terciles of the
   line's full token count over the population; token length bins ≤4 / 5–6 / ≥7;
   hand from folio header `$H` (reported if ≥ 2 values among holdout tokens);
   major sections = E007 rule result {B,H,P,S}.
8. **Nulls.** N1: for each folio, `rng.permutation` of its population tokens
   placed back into the population positions (uncertain tokens fixed); seed
   `20261019`. N0: the same per line; seed `20261020`. Features S, L and copy
   windows are recomputed on the shuffled lines; folio, fold, language, section
   unchanged. W is **not** re-selected on nulls.
9. **De-risking rule.** `run.py --dev-only` may be executed before the reveal:
   it codes development tokens only (prequential), checks losslessness and
   selects W. It writes no holdout number and no `results.json`.
10. **Software.** Python 3.13, numpy only.
