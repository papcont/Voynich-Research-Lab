from __future__ import annotations
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
s = json.loads((root / "RESEARCH_STATE.json").read_text(encoding="utf-8"))
print(json.dumps({k: s.get(k) for k in ("status","active_experiment","next_action","blocked_reason")}, indent=2))
