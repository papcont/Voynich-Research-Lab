# E010 — Preflight Amendment 001 (pre-computation details)

- Date (UTC): 2026-10-20; pre-computation HEAD: **7cf5430**
- **No E010 metric has been computed.**

1. **Currier-subset criterion (E011 criterion 4) inside a B-only experiment.** Replaced by:
   folio-mean Δ > 0 within each of the two largest `$I` sections of the Currier-B population
   by token count (determined from population counts at run time and recorded).
2. **R1 permutation streams.** `C_all` uses `numpy.random.default_rng(20261020)`, `C_def`
   uses `default_rng(20261021)`; 1,000 permutations each of the right-hand unit array
   within the evaluated set; MI on the joint index table over the union alphabet of both
   sets (as upstream).
3. **R1 boundary definition on our pipeline.** Left and right are consecutive elements of
   the line's `tokenize_surface` list, both non-uncertain; `sep` = the right token's
   `separator_before` (`'.'` definite, `','` uncertain). Boundaries across `<->` gaps are
   already separate lines in our parser? No — `clean_text` maps `<->` to `.`; such
   boundaries count as definite, a known small deviation from upstream (recorded).
4. **Glyph units.** `re.findall(r'c[tkpf]h|[cs]h|i+[nrlm]|.', token)`; `Sunit` = last unit of
   the previous token; `S2unit` = `''.join(units[-2:])` (the whole token if it has one unit);
   `BOL`/`UNC` as in E011.
5. **Class features.** `cls(t)` = class id string from the fixed table if the surface token is
   a member, else `"UN"`; `prevcls` = `BOL` / `UNC` / `cls(previous token)`.
   Class models code an extra first slot: M_class: value `cls(t)` in parent context
   `("cls",)` (plain KT); M_classprev: child context `("clsc", prevcls)`, parent `("cls",)`
   (backoff). Then the P70 slots, with the prefix slot's child context carrying `cls(t)`.
   Lossless: the class slot adds information that is a function of the token.
6. **Null features.** Within-folio permutation (seed 20261020, folios in order, features
   S, Sunit, S2unit, Sfam, cls in that order, one `rng.permutation` per feature per folio);
   `prevcls` for the null is derived from the permuted `cls` labels. Null contrasts:
   H016 `M_Sunit° − M_S`, H017 `M_S2unit° − M_Sunit`, H018 `M_classprev° − M_Sfam`.
7. **Model bits (reported).** Class models: `480 × charcost(mean member length) +
   480 × log2(49)` added to the P70 inventory cost; other models as E011.
8. **Currier A transfer (descriptive).** M_S, M_Sunit, M_S2unit cross-fitted within A folios.
