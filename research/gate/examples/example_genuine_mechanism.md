# Gate v2.0.0 report — claim `example_genuine_mechanism`

Registration: **PASS**

| level | state | reasons |
|---|---|---|
| STRUCTURAL_MODEL_VALIDATED | **PASS** | — |
| DECODING_MECHANISM_SUPPORTED | **PASS** | — |
| LANGUAGE_IDENTIFICATION_SUPPORTED | **NOT_TESTED** | no language block |
| SEMANTIC_DECODING_SUPPORTED | **NOT_TESTED** | no semantic block |
| DECIPHERMENT_CONFIRMED | **NOT_TESTED** | no confirmation block |

Highest PASS level: **DECODING_MECHANISM_SUPPORTED**

Numbers:
```json
{
 "STRUCTURAL_MODEL_VALIDATED": {
  "n_folios": 40,
  "n_tokens": 4800,
  "model_bits": 796.0,
  "mean_delta_bits_per_token": 1.1288498845572974,
  "ci_lower": 1.081665498698551,
  "ci_upper": 1.1852064753144358,
  "margin": 0.5,
  "control_gains": {
   "folio_internal_permutation": -5.0869183928955355,
   "matched_synthetic": -5.0869183928955355,
   "nonsemantic_generator": -5.0869183928955355
  }
 },
 "DECODING_MECHANISM_SUPPORTED": {
  "specificity": {
   "control_gains": {
    "folio_internal_permutation": -5.0869183928955355,
    "matched_synthetic": -5.0869183928955355,
    "nonsemantic_generator": -5.0869183928955355
   }
  }
 },
 "LANGUAGE_IDENTIFICATION_SUPPORTED": {},
 "SEMANTIC_DECODING_SUPPORTED": {},
 "DECIPHERMENT_CONFIRMED": {}
}
```
