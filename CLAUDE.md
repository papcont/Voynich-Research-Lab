# CLAUDE.md — autonomous research contract

You are operating a scientific code repository, not an open-ended chat.

## Authority and restart order

At the beginning of every new session, read:

1. `RESUME.md`
2. `RESEARCH_STATE.json`
3. `RESEARCH_PROTOCOL.md`
4. `research/STATUS.md`
5. `research/hypothesis-ledger.tsv`
6. the active experiment directory named in `RESEARCH_STATE.json`

Repository evidence overrides old chat memory.

## Mission

Advance the Voynich research program **one auditable decision at a time**. The goal is not to produce a plausible translation. The goal is to discriminate among explanations with reproducible tests.

Open mechanism families:

- N — meaningful natural/technical language
- C — meaningful text plus cipher/shorthand/obscuration
- G — constrained formal/generative text
- M — mixed mechanisms

## Non-negotiable scientific rules

1. EVA is a glyph transliteration. Never silently interpret EVA symbols as sounds or letters.
2. Readable plaintext is not validation.
3. Every new hypothesis records: claim, scope, pre-result prediction, falsification condition, baseline/null, degrees of freedom, selection rule, dependency unit, and claim ceiling.
4. Freeze a test plan **before** opening a designated holdout or computing its target metric.
5. If a target has already been inspected, label it `EXPLORATORY`; never relabel it prospective.
6. Negative results remain in git and in the hypothesis ledger.
7. Never tune on a held-out result after reveal and still call it held-out.
8. Prefer page/physical-leaf or other dependency-aware uncertainty over treating every token as independent.
9. Control relevant confounds: Currier A/B, LFD hand, section/locus, line/paragraph position, uncertain EVA reading, token/line length, labels vs running text.
10. Any external "decode" is a competitor until independently reimplemented and prospectively tested.
11. Never import an external repo's semantic assignments as gold labels merely because they are internally consistent.
12. Do not redistribute third-party source data unless its license is explicitly verified.
13. Record random seeds and software versions.
14. Keep raw results separate from narrative interpretation.
15. If a null explains the result, record that.

## Coding rules

- Python 3.11+.
- New analysis belongs in an experiment directory with `PLAN.md`, `experiment.json`, `run.py`, `validate.py`, `results.json`, `REPORT.md`.
- Shared hypothesis-neutral utilities go under `src/voynichlab/`.
- Do not hardcode machine-specific absolute paths.
- Do not edit external repositories in place.
- `python scripts/validate_repo.py` and `pytest` must pass before commit.

## Autonomous-cycle behavior

When invoked by the research loop:

1. Read state and execute the **single next action**.
2. If `READY_TO_FREEZE_PLAN`, audit the draft, make it executable/falsifiable, create `PLAN.md`, update state to `PLAN_FROZEN`, and commit that freeze **without computing target results**.
3. If `PLAN_FROZEN`, implement without changing frozen scientific choices. If implementation forces a scientific change, write an amendment before target reveal.
4. Run the experiment and validator.
5. Write machine-readable results first, then interpretation.
6. Update `research/STATUS.md`, `research/hypothesis-ledger.tsv`, `RESUME.md`, and `RESEARCH_STATE.json`.
7. Commit the completed cycle.
8. Do not depend on conversational memory; the wrapper may start a fresh session for the next cycle.
9. If a real human decision is required, set `"status": "BLOCKED"` and a precise `"blocked_reason"`, then stop.
10. Never ask the human to type "continue" for routine work.

## Stop conditions requiring a human

Stop rather than guess if:

- source licensing is ambiguous and data would be copied;
- a preregistered holdout was accidentally exposed before freeze;
- two materially different scientific designs are equally defensible and choosing changes the claim;
- credentials/payment are required;
- provenance is inconsistent;
- destructive git operations would be required.

## Git policy

Allowed autonomously: inspect status/diff/log, edit experiment files, add files, make local commits after validation.

Not allowed autonomously: force push, rewrite history, delete historical negative results, or turn an external claim into accepted truth.

## Current frontier

Use `RESEARCH_STATE.json`. Initial frontier: E006 canonical final-chain holdout test.
