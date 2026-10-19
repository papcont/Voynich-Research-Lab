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
                    "E008_exploratory": "post-reveal exploratory backoff-coder analysis (exploratory.py) trained on dev {0,1,2} and scored on holdout {3,4}; its result motivated the E011 design => error analysis = SELECTION for ALL running-text folios (recorded 2026-10-19)",
                    "E001-E005": "historical exploratory analyses (not reproducible from this repo); conservatively assumed to have touched any running-text token"},
                "folios": {}, "selection_folios": [], "lockboxes": {}}
    sel = set()
    for f in folios:
        roles = {"E006": "SELECTION" if folio_fold(f) in (0, 1, 2) else "EVALUATION",
                 "E007": "SELECTION+EVALUATION" if efold(f) in (0, 1, 2) else "EVALUATION",
                 "E008": "SELECTION" if efold(f) in (0, 1, 2) else "EVALUATION",
                 "E008_exploratory": "SELECTION"}
        is_sel = any("SELECTION" in r for r in roles.values())
        if is_sel:
            sel.add(f)
        registry["folios"][f] = {"running_text_tokens": run_tokens[f], "non_running_tokens": other_tokens.get(f, 0),
                                 "roles": roles, "ever_selection": is_sel}
    registry["selection_folios"] = sorted(sel)
    never_sel = sorted(f for f in folios if f not in sel)

    # Running text: after the E008 exploratory analysis every running-text folio has a SELECTION
    # role, so NO running-text lockbox exists in ZL3b. The whole running text is a development pool.
    registry["lockboxes"]["DEVELOPMENT_POOL_RUNNING_V1"] = {
        "independence": "DEVELOPMENT_ONLY",
        "description": "All 206 running-text folios. Every one carries a SELECTION role (E006/E007/E008 development folds, "
                       "or the E008 post-reveal exploratory backoff analysis on the E007 holdout folds). Usable for development "
                       "and internally cross-fitted development-stage estimates; NEVER as a Gate v2 confirmation lockbox.",
        "folios": folios, "n_folios": len(folios), "n_tokens": sum(run_tokens[f] for f in folios), "sha256": sha_list(folios),
        "never_selection_before_E008_exploratory": never_sel}
    # Lockbox 2: non-running loci (labels, circular, radial) — never used by any committed experiment
    nr = sorted(f for f in other_tokens if other_tokens[f] > 0)
    registry["lockboxes"]["LOCKBOX_NONRUNNING_V1"] = {
        "independence": "SEMI_INDEPENDENT",
        "description": "Label/circular/radial loci (locus type not P*). No committed experiment coded these TOKENS, but they lie on "
                       "folios whose running text carries SELECTION roles, and the dependency unit is the physical folio. "
                       "Classified INDEPENDENT in the first registry versions; corrected 2026-10-20 after the E013 gate run "
                       "flagged the folio overlap. Usable for development-stage transfer tests only.",
        "folios": nr, "n_folios": len(nr), "n_tokens": sum(other_tokens[f] for f in nr), "sha256": sha_list(nr),
        "folios_with_selection_role": sorted(set(nr) & sel)}
    registry["statement"] = ("NO independent lockbox exists in ZL3b under the folio-as-dependency-unit rule: every running-text folio "
                             "carries a SELECTION role (E006/E007/E008 development folds or the E008 exploratory analysis), and the "
                             "label/circular/radial tokens lie on those same folios. All ZL3b claims are development-stage until a human "
                             "registers a confirmation surface from outside (new transliteration with independent readings, newly "
                             "transcribed material) or amends the protocol with an explicit semi-independent tier for candidates that "
                             "were not developed on these folios.")
    OUT.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "folios"} for k, v in registry["lockboxes"].items()}, indent=1))
    print("selection folios:", len(sel), "never-selection:", len(never_sel), "->", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
