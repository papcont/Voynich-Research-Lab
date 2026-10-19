"""Holdout audit for Gate v2 — which folios were used, in what role, by which experiment.

Writes research/holdout_registry.json with, per running-text folio, the roles
it played in E006, E007 and E008 (SELECTION = used for model/parameter/threshold
selection or error analysis; EVALUATION = target metrics computed on it), and
the lockboxes available to future claims, each with a SHA-256 over its sorted
folio list. Purely a bookkeeping script: no model metric is computed.

Run:  python scripts/holdout_audit.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from voynichlab.ivtff import parse_ivtff, iter_strict_tokens  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab.folds import folio_fold  # noqa: E402  (E006 split)

DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
OUT = ROOT / "research" / "holdout_registry.json"


def efold(folio: str) -> int:
    return int(hashlib.sha256(("E007:" + folio.lower()).encode()).hexdigest(), 16) % 5


def sha_list(items) -> str:
    return hashlib.sha256("\n".join(sorted(items)).encode()).hexdigest()


def main() -> int:
    if not DATA.is_file():
        raise SystemExit("data/raw/ZL3b-n.txt missing; run scripts/fetch_zl3b.py")
    run_tokens, other_tokens = defaultdict(int), defaultdict(int)
    for rec, _i, _t in iter_strict_tokens(parse_ivtff(DATA)):
        (run_tokens if is_running_text(rec.locator) else other_tokens)[rec.folio] += 1
    folios = sorted(run_tokens)

    registry = {"schema": 1, "generated_by": "scripts/holdout_audit.py", "source_blob": "2a4533ab9bdfa85db9bad602d590978953055df1",
                "roles": {"SELECTION": "used for model/parameter/threshold selection or error analysis",
                          "EVALUATION": "target metric computed and revealed on it",
                          "UNTOUCHED": "no committed experiment used it"},
                "experiments": {
                    "E006": "split folds.folio_fold (sha256(folio) % 5); dev {0,1,2} = SELECTION (grammar/threshold development), holdout {3,4} = EVALUATION (revealed)",
                    "E007": "split efold (sha256('E007:'+folio) % 5); global prequential + 5-fold cross-fitted scores on ALL folios = EVALUATION; dev {0,1,2} also SELECTION (A8 slot-length profile); dev->holdout arm revealed",
                    "E008": "same split; dev {0,1,2} = SELECTION (W chosen on development); holdout {3,4} = EVALUATION",
                    "E001-E005": "historical exploratory analyses (not reproducible from this repo); conservatively assumed to have touched any running-text token"},
                "folios": {}, "selection_folios": [], "lockboxes": {}}
    sel = set()
    for f in folios:
        roles = {"E006": "SELECTION" if folio_fold(f) in (0, 1, 2) else "EVALUATION",
                 "E007": "SELECTION+EVALUATION" if efold(f) in (0, 1, 2) else "EVALUATION",
                 "E008": "SELECTION" if efold(f) in (0, 1, 2) else "EVALUATION"}
        is_sel = any("SELECTION" in r for r in roles.values())
        if is_sel:
            sel.add(f)
        registry["folios"][f] = {"running_text_tokens": run_tokens[f], "non_running_tokens": other_tokens.get(f, 0),
                                 "roles": roles, "ever_selection": is_sel}
    registry["selection_folios"] = sorted(sel)
    never_sel = sorted(f for f in folios if f not in sel)

    # Lockbox 1: SEMI_INDEPENDENT running-text folios = ALL folios never used for selection.
    # (Only 38 of 206 escape both the E006 and the E007/E008 development folds; splitting
    # them further would push any claim below the Gate v2 power floor of 20 folios.)
    registry["lockboxes"]["LOCKBOX_RUNNING_SEMI_V1"] = {
        "independence": "SEMI_INDEPENDENT",
        "description": "All running-text folios never used for selection by any committed experiment (E006 dev folds, "
                       "E007/E008 dev folds excluded). Their P70/A0/S/L/C scores were revealed in E006-E008, so they are "
                       "not fully independent. From 2026-10-19 excluded from all development.",
        "folios": never_sel, "n_folios": len(never_sel), "n_tokens": sum(run_tokens[f] for f in never_sel),
        "sha256": sha_list(never_sel)}
    # Lockbox 2: non-running loci (labels, circular, radial) — never used by any committed experiment
    nr = sorted(f for f in other_tokens if other_tokens[f] > 0)
    registry["lockboxes"]["LOCKBOX_NONRUNNING_V1"] = {
        "independence": "INDEPENDENT",
        "description": "Label/circular/radial loci (locus type not P*). No committed experiment coded them. Small, structurally different from running text; suitable for transfer-style confirmation only.",
        "folios": nr, "n_folios": len(nr), "n_tokens": sum(other_tokens[f] for f in nr), "sha256": sha_list(nr)}
    registry["statement"] = ("No fully independent RUNNING-TEXT data remain in ZL3b: every running-text folio has had a revealed "
                             "target metric in E007 (global and cross-fitted scores). Confirmation of a running-text claim can only use "
                             "LOCKBOX_RUNNING_SEMI_V1 (flagged SEMI_INDEPENDENT) or data outside ZL3b running text "
                             "(LOCKBOX_NONRUNNING_V1, other transliterations' uncertain-reading sets, future sources).")
    OUT.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "folios"} for k, v in registry["lockboxes"].items()}, indent=1))
    print("selection folios:", len(sel), "never-selection:", len(never_sel), "->", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
