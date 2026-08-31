from __future__ import annotations

import json
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

    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("REPOSITORY_PREFLIGHT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
