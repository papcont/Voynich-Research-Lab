# E010 — REPORT (interpretation, written after results.json)

**R1 REPRODUCED. H016, H017, H018 all FALSIFIED_DEV.** Upstream's boundary glyph coupling
reproduces on our pipeline to within 0.002 bits; their representational refinements (glyph
units, last two units) add nothing at codelength level; their 49-class table, used as a
fixed external input in the frozen model shape, costs ≈ 3 bits/token.

Plan `7cf5430`, amendment `4e79072`, first run 2026-10-20; independent `validate.py` (own
regex, MI, permutations, coder, bootstrap): `E010_VALIDATION_PASS`. Upstream
`epilectrik/voynich` @ `ff399c44` (read-only; nothing copied). Scope: Currier B running
text, 22,255 tokens, 82 folios; sections used for the subset criterion: S (10,627 tokens)
and B (6,140).

## R1 — boundary glyph coupling (upstream definition, our pipeline)

| set | n | C (bits) | published (ZL3b) | p |
|---|---|---|---|---|
| all boundaries | 19,467 | **0.2548** | 0.256 | < 0.001 |
| definite `.` only | 17,929 | **0.2134** | 0.215 | < 0.001 |

Decision **REPRODUCED** (both within 0.03; in fact within 0.002). The measurement is
robust to the pipeline differences (our strict-token exclusion vs their `readable()`
filter). Class-table coverage of B tokens on ZL3b: **71.3%** (published 69.5% on the H
track) — consistent.

## R2 — contrasts under the E011 scorecard (out-of-fold bits/token, Currier B)

| model | bits/token |
|---|---|
| M_S prefix \| last EVA char (E011 reference) | 13.577 |
| M_Sfam prefix \| previous P70 suffix (registered null shape) | **13.566** |
| M_Sunit prefix \| last glyph unit | 13.579 |
| M_S2unit prefix \| last two glyph units | 13.576 |
| M_class class slot + prefix \| class | 16.628 |
| M_classprev class \| previous class + prefix \| class | 16.629 |

| hypothesis | contrast | folio-mean Δ (95% CI) | verdict |
|---|---|---|---|
| H016 glyph units beat EVA characters | M_Sunit − M_S | −0.0007 (−0.003, 0.001) | FALSIFIED_DEV |
| H017 last two units beat last unit | M_S2unit − M_Sunit | +0.0012 (−0.005, 0.007) | FALSIFIED_DEV |
| H018 49-class grammar beats edge state | M_classprev − M_Sfam | −3.085 (−3.136, −3.035) | FALSIFIED_DEV |

Secondary: M_class − M_Sfam −3.075; M_classprev − M_class −0.010 (class → class transitions
carry nothing beyond the class marginal). Currier A transfer (descriptive): M_S 15.085,
M_Sunit 15.090, M_S2unit 15.100 — same ordering. All predictions were met (H016 small or
null; H018 falsified); H017 was predicted "positive if C2082 is real at codelength level" —
it is not, at the prefix-slot level.

## Reading

1. **Upstream's core measurement is solid.** The last glyph → first glyph coupling is real
   and reproduces exactly; it is the same phenomenon our E011 H014 result captures as a
   codelength gain on the prefix slot. Two independent pipelines and two metrics agree.
2. **Representation does not matter here.** Treating `ch`, `sh`, `cth`, `iin`… as single
   units changes nothing: the last EVA character already carries the information (the
   unit-final character determines the unit in nearly all cases). The "word-ending
   routing" (last two glyphs) adds nothing at the prefix slot.
3. **The 49-class table is not a predictive description of B.** In the frozen shape
   (class slot, prefix conditioned on class) it costs 3 bits/token; the class transition
   adds nothing. An exploratory, fairer shape (`exploratory_post_run.json`: class slot +
   whole token | class) is also worse than plain whole-token coding (17.44 vs 15.29), but
   that comparison is confounded by the backoff coder's double escape on hapax tokens (B
   has a high single-occurrence rate), so it neither rescues nor further condemns the
   table. Upstream itself calls the classes a measurement "defined by exclusion"; at
   codelength level they are a cost, not a gain. H018 stands as frozen.

## Consequences

- H016/H017 → the programme keeps the EVA-character edge feature (M_S/M_Sfam).
- H018 → the 49-class table is recorded as a non-predictive description on ZL3b; upstream
  remains a competitor only through its coupling/zone/bifolium measurements, which our
  pipeline can reproduce (coupling done; zones and bifolium not tested here).
- Upstream interpretations (procedural notation, operators, control programs) were not
  evaluated and are not adopted.

Claim ceiling: structural, development-stage, Currier B; no Gate v2 level.
