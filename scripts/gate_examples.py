"""Write two reproducible Gate v2 example reports (synthetic, no corpus access).

Usage: python scripts/gate_examples.py  -> research/gate/examples/*.json|*.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from voynichlab.gate import evaluate, load_spec, render_report  # noqa: E402
import test_gate as tg  # noqa: E402  (synthetic world + claim builders)

OUT = ROOT / "research" / "gate" / "examples"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    T, folios = tg.synthetic_world()
    _, shuffled = tg.synthetic_world(shuffle=True)
    pos = tg.base_claim()
    pos["claim_id"] = "example_genuine_mechanism"
    pos["compression"] = tg.compression_block(tg.code_world(T, folios, True), tg.code_world(T, shuffled, True))
    pos["mechanism"] = tg.mechanism_block()
    sham = tg.base_claim()
    sham["claim_id"] = "example_sham_readable_plaintext"
    sham["compression"] = tg.compression_block(tg.code_world(T, folios, False))
    sham["mechanism"] = tg.mechanism_block()
    for claim in (pos, sham):
        res = evaluate(claim, load_spec(), tg.REGISTRY)
        (OUT / f"{claim['claim_id']}.json").write_text(json.dumps(claim, indent=1, default=float) + "\n", encoding="utf-8")
        (OUT / f"{claim['claim_id']}.md").write_text(render_report(res), encoding="utf-8")
        print(claim["claim_id"], "->", res.highest_pass, {k: v.state for k, v in res.levels.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
