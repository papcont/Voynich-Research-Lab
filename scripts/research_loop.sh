#!/usr/bin/env bash
set -euo pipefail
MAX_CYCLES="${MAX_CYCLES:-20}"
MAX_TURNS="${MAX_TURNS:-60}"
MODEL="${CLAUDE_MODEL:-}"
cd "$(dirname "$0")/.."

command -v claude >/dev/null || { echo "claude CLI not found"; exit 1; }
python scripts/validate_repo.py

for ((cycle=1; cycle<=MAX_CYCLES; cycle++)); do
  status="$(python -c 'import json;print(json.load(open("RESEARCH_STATE.json"))["status"])')"
  [[ "$status" == "BLOCKED" || "$status" == "DONE" ]] && break

  prompt='Read CLAUDE.md and follow its restart order.
Execute exactly ONE autonomous research cycle for RESEARCH_STATE.json.
Do not ask for continue. Respect preregistration. End by validating, updating state and making one local git commit.'

  args=(-p "$prompt" --output-format json --max-turns "$MAX_TURNS"
        --permission-mode auto --tools "Bash,Edit,Read,Write,Glob,Grep"
        --allowedTools "Read" "Edit" "Write" "Glob" "Grep"
        "Bash(python *)" "Bash(pytest *)"
        "Bash(git status *)" "Bash(git diff *)" "Bash(git log *)"
        "Bash(git add *)" "Bash(git commit *)")
  [[ -n "$MODEL" ]] && args+=(--model "$MODEL")

  set +e
  claude "${args[@]}" | tee "runs/claude-cycle-$(printf '%03d' "$cycle").json"
  rc=${PIPESTATUS[0]}
  set -e

  python scripts/validate_repo.py
  [[ $rc -ne 0 ]] && break
  [[ -n "$(git status --porcelain)" ]] && { echo "Uncommitted changes; stopping"; break; }
  [[ "${VOYNICH_AUTO_PUSH:-0}" == "1" ]] && git push
done
