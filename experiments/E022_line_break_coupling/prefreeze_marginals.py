"""E022 pre-freeze marginals (committed with the freeze). MARGINAL COUNTS ONLY: pair counts per
class/population, edge-glyph and line-initial/paragraph-initial prefix rates, record-set
diagnostics. No (previous-final × next-prefix) cell is ever formed, so no conditional/target
statistic (R, MI, p) can be read from this output. Output sha256 is recorded in experiment.json.

Run:  python experiments/E022_line_break_coupling/prefreeze_marginals.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text, locus_type  # noqa: E402
from voynichlab.p70 import parse_p70  # noqa: E402

DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
LOCUS_RE = re.compile(r"^<(f[^>,]+),([^>]*)>\s+(.*)$")
GALLOWS = "tkpfTKPF"


def population(lang, sec):
    return ("bio_B" if sec == "B" else "other_B") if lang == "B" else ("A" if lang == "A" else None)


def raw_running_loci():
    """All P-type loci in raw file order per folio (independent of parse_ivtff), with a flag for
    records whose text starts with an inline comment (dropped by parse_ivtff)."""
    out = defaultdict(list)
    for raw in DATA.read_text(encoding="utf-8").splitlines():
        m = LOCUS_RE.match(raw)
        if not m:
            continue
        locus, locator, text = m.groups()
        if "." not in locus or not is_running_text(locator):
            continue
        out[locus.split(".", 1)[0]].append((locus, locator, text.lstrip().startswith("<!")))
    return out


def main():
    rawloci = raw_running_loci()
    n_raw = sum(len(v) for v in rawloci.values())
    dropped = [l for v in rawloci.values() for l, _loc, d in v if d]
    recs = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        toks = [(t.value, t.uncertain) for t in tokenize_surface(rec.raw_text) if t.value]
        recs[rec.folio].append({"locus": rec.locus, "locator": rec.locator or "", "pop": population(rec.meta.language, rec.meta.illustration),
                                "hand": rec.meta.hand, "end": "<$>" in rec.raw_text, "start": "<%>" in rec.raw_text, "toks": toks})
    n_parsed = sum(len(v) for v in recs.values())
    C = defaultdict(Counter)
    per_stratum = {k: {"line": defaultdict(lambda: [0, 0, 0]), "para": defaultdict(lambda: [0, 0, 0])} for k in ("bio_B", "other_B", "A")}
    for folio, lines in recs.items():
        order = {l: i for i, (l, _loc, _d) in enumerate(rawloci.get(folio, []))}
        pid = 0
        for i, ln in enumerate(lines):
            if ln["start"]:
                pid += 1
            ln["pid"] = pid
            k = ln["pop"] or "none"
            strict = [v for v, u in ln["toks"] if not u]
            c = C[k]
            c["lines"] += 1; c["tokens_strict"] += len(strict)
            c[f"hand_{ln['hand']}"] += 1
            if locus_type(ln["locator"]) == "Pb":
                c["pb_records"] += 1
            if len(ln["toks"]) == 1:
                c["one_token_lines"] += 1
            if not strict:
                c["all_uncertain_lines"] += 1
            c["within_pairs"] += sum(1 for j in range(1, len(ln["toks"])) if not ln["toks"][j][1] and not ln["toks"][j - 1][1])
            if ln["toks"] and not ln["toks"][0][1]:
                v = ln["toks"][0][0]
                c["line_initial_strict"] += 1; c["line_initial_qo"] += parse_p70(v)[0] == "qo"
                if ln["start"]:
                    c["para_initial_strict"] += 1; c["para_initial_qo"] += parse_p70(v)[0] == "qo"; c["para_initial_gallows"] += v[0] in GALLOWS
            if ln["toks"] and not ln["toks"][-1][1]:
                v = ln["toks"][-1][0]
                c["line_final_strict"] += 1; c["line_final_y"] += v.endswith("y"); c["line_final_mg"] += v[-1] in "mg"
            for v in strict:
                c["all_qo"] += parse_p70(v)[0] == "qo"; c["all_y_final"] += v.endswith("y"); c["all_mg_final"] += v[-1] in "mg"
            if i + 1 < len(lines):
                nl = lines[i + 1]
                cls = "para" if ln["end"] else "line"
                if nl["start"] != ln["end"]:
                    c[f"{cls}_marker_mismatch"] += 1; continue
                if nl["pop"] != ln["pop"]:
                    c[f"{cls}_population_change"] += 1; continue
                if ln["pop"] is None:
                    continue
                if order.get(nl["locus"], -9) != order.get(ln["locus"], -99) + 1:
                    c[f"{cls}_bridges_dropped_record"] += 1; continue
                if nl["locator"].startswith("="):
                    c[f"{cls}_same_line_title"] += 1; continue
                if locus_type(ln["locator"]) == "Pb" or locus_type(nl["locator"]) == "Pb":
                    c[f"{cls}_pb_record"] += 1; continue
                if not ln["toks"] or not nl["toks"]:
                    c[f"{cls}_empty_line"] += 1; continue
                if ln["toks"][-1][1] or nl["toks"][0][1]:
                    c[f"{cls}_uncertain_edge"] += 1; continue
                c[f"{cls}_pairs"] += 1
                c[f"{cls}_prev_y"] += ln["toks"][-1][0].endswith("y")
                c[f"{cls}_next_qo"] += parse_p70(nl["toks"][0][0])[0] == "qo"
                st = per_stratum[k][cls][f"{folio}|{ln['pid']}" if cls == "line" else folio]
                st[0] += 1; st[1] += ln["toks"][-1][0].endswith("y"); st[2] += parse_p70(nl["toks"][0][0])[0] == "qo"
                c[f"{cls}_prev_mg"] += ln["toks"][-1][0][-1] in "mg"
                if len(ln["toks"]) == 1 or len(nl["toks"]) == 1:
                    c[f"{cls}_pairs_with_one_token_line"] += 1
    out = {"records": {"raw_P_type": n_raw, "parsed_running_text": n_parsed, "dropped_by_parser": dropped},
           "populations": {k: dict(sorted(C[k].items())) for k in ("bio_B", "other_B", "A", "none")},
           "per_stratum_marginals": {k: {cls: {s_: {"N": v[0], "n_y": v[1], "k_qo": v[2]} for s_, v in sorted(per_stratum[k][cls].items())}
                                         for cls in ("line", "para")} for k in per_stratum}}
    for k in ("bio_B", "other_B", "A"):
        c = C[k]
        out["populations"][k]["rates"] = {
            "P_qo_line_initial": c["line_initial_qo"] / c["line_initial_strict"], "P_qo_all": c["all_qo"] / c["tokens_strict"],
            "P_qo_pair_level_line": c["line_next_qo"] / c["line_pairs"], "P_y_pair_level_line": c["line_prev_y"] / c["line_pairs"],
            "P_qo_pair_level_para": c["para_next_qo"] / c["para_pairs"] if c["para_pairs"] else None,
            "P_y_final_line_final": c["line_final_y"] / c["line_final_strict"], "P_y_final_all": c["all_y_final"] / c["tokens_strict"],
            "P_mg_final_line_final": c["line_final_mg"] / c["line_final_strict"], "P_mg_final_all": c["all_mg_final"] / c["tokens_strict"],
            "P_qo_para_initial": c["para_initial_qo"] / c["para_initial_strict"] if c["para_initial_strict"] else None,
            "P_gallows_para_initial": c["para_initial_gallows"] / c["para_initial_strict"] if c["para_initial_strict"] else None}
    text = json.dumps(out, indent=2, sort_keys=True)
    print(text)
    print("sha256:", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main()
