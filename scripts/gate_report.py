"""Reproducible Gate v2 report for a claim record.

Usage:  python scripts/gate_report.py path/to/claim.json [--out REPORT.md] [--json RESULT.json]

Reads research/gate/gate_v2.json and research/holdout_registry.json, evaluates
the claim with voynichlab.gate.evaluate and writes a Markdown report (and
optionally the machine-readable result). Exit code 0 always; the states are the
result, not the exit code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from voynichlab.gate import evaluate, load_spec, render_report  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("claim")
    ap.add_argument("--out")
    ap.add_argument("--json")
    a = ap.parse_args()
    claim_bytes = Path(a.claim).read_bytes()
    claim = json.loads(claim_bytes)
    spec = load_spec()
    reg_path = ROOT / "research" / "holdout_registry.json"
    registry = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.is_file() else None
    res = evaluate(claim, spec, registry)
    report = render_report(res)
    report += (f"\nProvenance: claim sha256 `{hashlib.sha256(claim_bytes).hexdigest()}`, "
               f"spec `{hashlib.sha256((ROOT / 'research' / 'gate' / 'gate_v2.json').read_bytes()).hexdigest()}`, "
               f"registry `{hashlib.sha256(reg_path.read_bytes()).hexdigest() if registry else 'none'}`\n")
    if a.out:
        Path(a.out).write_text(report, encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps(res.to_dict(), indent=2, default=str) + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
