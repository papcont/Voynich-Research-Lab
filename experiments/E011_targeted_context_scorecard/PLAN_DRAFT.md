# E011 — hypothesis-shaped conditioning with a backoff scorecard
Status: DRAFT (from the E008 design lesson; nothing computed)

## Question
Does the previous token's final glyph predict the next token's *prefix slot* (H003 shape), and does line
position predict the prefix/suffix slots, when the coder can back off to the unconditioned context?

## Design sketch (to be frozen)
- Scorecard: KT coder with PPM-style backoff (escape mass -> parent context; exclusion handled), fixed before reveal;
  calibrate nothing on holdout.
- Conditioning is slot-targeted: S -> prefix slot only; L -> prefix and suffix slots; never all slots.
- Bases, population, split and nulls as E008; Gate v2 compression protocol applies (folio-level CI, 0.5 bits/token
  provisional margin calibrated on development data; INCONCLUSIVE when underpowered).
- Pre-result predictions: positive prefix-slot gain for S in Currier B (y -> qo history), smaller in A.

## Falsification
No prefix-slot gain for S beyond the within-folio shuffle null, on the lockbox defined by Gate v2.

## Claim ceiling
Structural only; no semantic decipherment.
