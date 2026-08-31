from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("slug")
    a = ap.parse_args()
    target = ROOT / "experiments" / f"{a.id}_{a.slug}"
    if target.exists():
        raise SystemExit(f"exists: {target}")
    target.mkdir(parents=True)
    (target / "PLAN_DRAFT.md").write_text(
        f"# {a.id} — {a.slug.replace('_',' ')}\n\nStatus: DRAFT\n\n"
        "## Question\nTODO\n\n## Prediction\nTODO\n\n## Falsification\nTODO\n\n"
        "## Data selection\nTODO\n\n## Metrics\nTODO\n\n## Null\nTODO\n\n"
        "## Claim ceiling\nStructural only; no semantic decipherment.\n",
        encoding="utf-8",
    )
    manifest = {
        "experiment_id": a.id, "status": "DRAFT", "question": "", "inputs": [],
        "holdout": None, "metrics": [], "nulls": [], "seed": 20260831,
        "claim_ceiling": "Structural only; no semantic decipherment."
    }
    (target / "experiment.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(target.relative_to(ROOT))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
