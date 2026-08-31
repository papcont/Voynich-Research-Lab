# Research protocol

## Evidence classes

Every result must be labeled:

- `EXPLORATORY`
- `FROZEN_HOLDOUT`
- `PROSPECTIVE`
- `EXTERNAL_REPLICATION`
- `MECHANISM_DEMONSTRATION`

## Experiment contract

Each experiment specifies:

- question and scope;
- sources and hashes;
- parser/normalization version;
- development and holdout units;
- dependency unit for uncertainty;
- exact metrics;
- null/baseline;
- random seeds;
- decision rule;
- claim ceiling;
- confounds;
- falsification condition.

## Anti-overfitting rules

- Do not select a promising token after seeing its distribution and report an uncorrected confirmatory p-value.
- Do not compare many candidates and report only the best.
- Do not use token independence where page/folio clustering matters.
- Preserve nuisance structure in nulls.
- Keep discovery and confirmation separate.
- Record amendments before target reveal.

## Decipherment promotion gate

Do not accept "decoded/translated/deciphered" until there is:

1. a fixed executable mapping/mechanism;
2. substantial unseen prediction;
3. constrained output freedom;
4. strong competitors/nulls;
5. independent replication;
6. independently grounded content relation;
7. explicit complexity and failure accounting.

## External repositories

Classify external repos as workflow references, structural/cipher competitors, semantic claims, methodology references, or unrelated. Their own conclusions are never accepted automatically.
