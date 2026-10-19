# Gate v2.0.0 report — claim `example_sham_readable_plaintext`

Registration: **PASS**

| level | state | reasons |
|---|---|---|
| STRUCTURAL_MODEL_VALIDATED | **FAIL** | ci_upper -0.368 < margin 0.5 |
| DECODING_MECHANISM_SUPPORTED | **FAIL** | requires compression PASS; ci_upper -0.368 < margin 0.5 |
| LANGUAGE_IDENTIFICATION_SUPPORTED | **NOT_TESTED** | no language block |
| SEMANTIC_DECODING_SUPPORTED | **NOT_TESTED** | no semantic block |
| DECIPHERMENT_CONFIRMED | **NOT_TESTED** | no confirmation block |

Highest PASS level: **none**

Numbers:
```json
{
 "STRUCTURAL_MODEL_VALIDATED": {
  "n_folios": 40,
  "n_tokens": 4800,
  "model_bits": 796.0,
  "mean_delta_bits_per_token": -0.4237824374682875,
  "ci_lower": -0.4669871443931608,
  "ci_upper": -0.36849980463933807,
  "margin": 0.5,
  "control_gains": {}
 },
 "DECODING_MECHANISM_SUPPORTED": {},
 "LANGUAGE_IDENTIFICATION_SUPPORTED": {},
 "SEMANTIC_DECODING_SUPPORTED": {},
 "DECIPHERMENT_CONFIRMED": {}
}
```
