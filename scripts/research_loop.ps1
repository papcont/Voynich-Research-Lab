param(
    [int]$MaxCycles = 20,
    [int]$MaxTurns = 60,
    [string]$Model = ""
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Repo

function Get-State {
    Get-Content "RESEARCH_STATE.json" -Raw | ConvertFrom-Json
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    throw "Claude Code CLI ('claude') not found in PATH."
}

python scripts/validate_repo.py
if ($LASTEXITCODE -ne 0) { throw "Repository preflight failed." }

for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
    $state = Get-State
    Write-Host "=== Voynich research cycle $cycle / $MaxCycles ==="
    Write-Host "status=$($state.status) active=$($state.active_experiment)"

    if ($state.status -in @("BLOCKED", "DONE")) {
        Write-Host "Stopping: $($state.status) $($state.blocked_reason)"
        break
    }

    $prompt = @"
Read CLAUDE.md and follow its restart order.
Execute exactly ONE autonomous research cycle for the current RESEARCH_STATE.json action.
Do not ask me to type continue and do not run a later cycle in this invocation.
Respect preregistration: if this is a plan-freeze cycle, do not compute or inspect the designated target result.
At the end run pytest and python scripts/validate_repo.py, update state/ledger/status/resume as required, and make one local git commit.
If a genuine human decision is required, set status=BLOCKED with a precise blocked_reason.
"@

    $claudeArgs = @(
        "-p", $prompt,
        "--output-format", "json",
        "--max-turns", "$MaxTurns",
        "--permission-mode", "auto",
        "--tools", "Bash,Edit,Read,Write,Glob,Grep",
        "--allowedTools",
            "Read", "Edit", "Write", "Glob", "Grep",
            "Bash(python *)",
            "Bash(pytest *)",
            "Bash(git status *)",
            "Bash(git diff *)",
            "Bash(git log *)",
            "Bash(git add *)",
            "Bash(git commit *)"
    )
    if ($Model -ne "") { $claudeArgs += @("--model", $Model) }

    $runFile = "runs/claude-cycle-{0:D3}.json" -f $cycle
    & claude @claudeArgs | Tee-Object -FilePath $runFile
    $claudeExit = $LASTEXITCODE

    python scripts/validate_repo.py
    if ($LASTEXITCODE -ne 0) { throw "Post-cycle preflight failed." }

    if ($claudeExit -ne 0) {
        Write-Warning "Claude exited with code $claudeExit; inspect $runFile."
        break
    }

    if (git status --porcelain) {
        Write-Warning "Cycle left uncommitted changes; stopping rather than hiding them."
        break
    }

    if ($env:VOYNICH_AUTO_PUSH -eq "1") {
        git push
        if ($LASTEXITCODE -ne 0) { throw "git push failed" }
    }
}
