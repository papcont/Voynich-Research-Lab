# Voynich Research Lab

A reproducible, falsification-first workspace for structural analysis of the Voynich Manuscript.

**This repository does not claim that the manuscript has been deciphered.** Its purpose is to let a human or coding agent (Claude Code, Codex, etc.) continue a long research program without relying on chat memory.

## Why this repo exists

The active research direction is no longer "guess a translation". It is to separate and test:

1. token-edge state effects, especially previous-final -> next-initial behavior such as `y -> qo`;
2. token-internal module structure such as `qok/ok`, `qot/ot`, `ch/sh` and right-side families `ar/al/aiin/edy/eedy/...`;
3. Currier A/B, scribal hand, section, locus, line and paragraph effects;
4. variable attachment of short finals, e.g. candidate equivalences such as `otar.ar` vs `otarar`;
5. natural-language, cipher/shorthand, formal-generator and mixed explanations on common held-out scorecards.

The key rule is: **a readable output is not evidence by itself**. Every hypothesis must state what would falsify it.

## Start here

Human or agent:

1. `CLAUDE.md`
2. `RESUME.md`
3. `RESEARCH_STATE.json`
4. `RESEARCH_PROTOCOL.md`
5. `research/STATUS.md`
6. `research/hypothesis-ledger.tsv`
7. the active experiment's plan

`RESEARCH_STATE.json` is the machine-readable continuation pointer.

## Quick setup

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e ".[dev]"
python scripts/fetch_zl3b.py
pytest
python scripts/validate_repo.py
```

## Autonomous Claude Code loop

One cycle:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\research_loop.ps1 -MaxCycles 1
```

Repeated cycles:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\research_loop.ps1 -MaxCycles 20
```

The loop asks Claude Code to execute exactly the next READY research step, update the ledger/state, validate, and commit. It stops automatically on `BLOCKED` or `DONE`.

**Push is off by default.** Set `VOYNICH_AUTO_PUSH=1` only after the local loop has been reviewed.

## External research

Third-party repositories are **pinned references, not truth sources**. See `external/repos.yml`.

The most useful current upstreams are:

- `daito-dot/LETSGO-Voynich` — falsification/prospective-research workflow and deterministic handoff.
- `yodakohl/VManus` — experiment manifests, preflight validation, provenance and guarded/sealed-data workflow.
- `digitalgoldfisj79/Voynichdecomp` — directly relevant 4-slot decomposition hypothesis; independently reproduce and test it.
- `Halkosuoja/Voynich-Deshuffling-Matrix` — concrete Latin/deshuffling claim; use as a falsifiable competitor, not an accepted decode.

## Data policy

Do not commit third-party manuscript images or transcriptions unless redistribution terms have been explicitly verified. Fetch them locally and record source URL, upstream identity and local cryptographic hash.

The primary transcription target is ZL3b / EVA v3b dated 2025-05-13. EVA labels glyph shapes; it is not a known phonetic alphabet.

## Current frontier

**E006 — canonical final-chain / attachment holdout test**.
