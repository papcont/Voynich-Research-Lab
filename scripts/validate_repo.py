from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "CLAUDE.md", "RESUME.md", "RESEARCH_PROTOCOL.md", "RESEARCH_STATE.json",
    "research/STATUS.md", "research/hypothesis-ledger.tsv",
]


def main() -> int:
    errors = [f"missing required file: {x}" for x in REQUIRED if not (ROOT / x).is_file()]
    try:
        state = json.loads((ROOT / "RESEARCH_STATE.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid RESEARCH_STATE.json: {exc}")
        state = {}

    active = state.get("active_experiment")
    if active and not (ROOT / "experiments" / active).is_dir():
        errors.append(f"missing active experiment: experiments/{active}")
    if state.get("status") == "PLAN_FROZEN":
        if not (ROOT / "experiments" / str(active) / "PLAN.md").is_file():
            errors.append("state says PLAN_FROZEN but PLAN.md is missing")


    # Prepared texts (reference corpora, ZL3b-derived streams, generator output) live in
    # runs/ and must never be tracked (CLAUDE.md rule 12). Incident 2026-10-20: the old
    # pattern runs/*.json missed nested paths and 66 files reached the public branch.
    try:
        tracked = subprocess.run(["git", "ls-files", "--", "runs/"], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.split()
        for t in tracked:
            if t != "runs/.gitkeep":
                errors.append(f"tracked file under runs/ (must stay untracked): {t}")
    except (OSError, subprocess.CalledProcessError):
        pass

    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("REPOSITORY_PREFLIGHT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
