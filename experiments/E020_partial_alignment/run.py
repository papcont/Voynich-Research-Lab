"""E020 — partly word-aligned boundaries on a verbose stream (FIRST RUN).

Implements experiments/E020_partial_alignment/PLAN.md. Preparation, verbose encoding,
truncation and scoring come from the frozen E012/E019 runners. Calibration on N_DEU is
recorded before any prediction-text value is computed. Prepared texts: runs/E020/.

Run:  python experiments/E020_partial_alignment/run.py
"""
from __future__ import annotations

import json
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E012 = _load("e012_run", ROOT / "experiments" / "E012_reference_signature" / "run.py")
E019 = _load("e019_run", ROOT / "experiments" / "E019_cipher_transforms" / "run.py")
from voynichlab import signature as SG  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runs" / "E020"
GRID = [round(0.1 * i, 1) for i in range(11)]
TARGET = 0.178
SEED_CAL, SEED_PRED = 20261100, 20261120


def mix(lines, p, rng):
    """Keep each word boundary with prob p; re-add random boundaries to restore the token count."""
    out = {}
    for u in lines:
        new = []
        for l, s, full in lines[u]:
            words = [v for v, uu in full if not uu]
            if not words:
                continue
            stream = "".join(words)
            w = len(words)
            cuts, pos = set(), 0
            for v in words[:-1]:
                pos += len(v)
                if rng.random() < p:
                    cuts.add(pos)
            candidates = [i for i in range(1, len(stream)) if i not in cuts]
            need = (w - 1) - len(cuts)
            if need > 0 and candidates:
                for i in rng.choice(len(candidates), size=min(need, len(candidates)), replace=False):
                    cuts.add(candidates[i])
            bounds = sorted(cuts)
            toks, prev = [], 0
            for b in bounds + [len(stream)]:
                toks.append([stream[prev:b], False]); prev = b
            new.append((l, s, toks))
        out[u] = new
    return out


def top1_share(lines, order):
    """Share of the total out-of-fold edge gain carried by the top previous-last-character class."""
    toks = SG.tokens(lines, SG.a3_slots, order)
    sigma = len({c for t in toks for c in t.value})
    p0 = SG._crossfit_backoff(toks, {}, sigma)
    pS = SG._crossfit_backoff(toks, {0: ("S",)}, sigma)
    gain = p0 - pS
    by = defaultdict(float)
    for t, g in zip(toks, gain):
        by[t.S] += g
    total = float(gain.sum())
    top = max(by.items(), key=lambda kv: kv[1])
    return {"top_class": top[0], "top1_share": float(top[1] / total) if total > 0 else float("nan"),
            "total_gain_bits": total, "n_classes": len(by)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vlines, vorder = E012.voynich_lines()
    ll = E012.zl3b_line_lengths(vlines)
    e12 = json.loads((ROOT / "experiments" / "E012_reference_signature" / "results.json").read_text(encoding="utf-8"))
    V = e12["results"]["size_matched"]["V"]
    rng_reseg = np.random.default_rng(E012.SEED_RESEG)
    texts, orders = {}, {}
    for tid, (src, lang) in E012.TEXTS.items():
        lines, order, _ = E012.reference_lines(src, lang, ll, rng_reseg)
        if tid in ("N_DEU", "N_ITA"):
            texts[tid], orders[tid] = E019.verbose(lines), order
    # ---- calibration on N_DEU, recorded first ----
    cal = {}
    for gi, p in enumerate(GRID):
        m = mix(texts["N_DEU"], p, np.random.default_rng(SEED_CAL + gi))
        mt, mo = E012.truncate(m, orders["N_DEU"], E012.N_MATCH)
        sig = SG.signature(mt, components=("delta_S",), slot_fn=SG.a3_slots, folio_order=mo)
        cal[str(p)] = float(sig["delta_S"])
        print("calibration p", p, "delta_S", round(cal[str(p)], 4))
    p_star = max((p for p in GRID if abs(cal[str(p)] - TARGET) == min(abs(cal[str(q)] - TARGET) for q in GRID)))
    print("p* =", p_star)
    # ---- prediction on N_ITA ----
    m = mix(texts["N_ITA"], p_star, np.random.default_rng(SEED_PRED))
    mt, mo = E012.truncate(m, orders["N_ITA"], E012.N_MATCH)
    (OUT_DIR / "MIX_N_ITA.json").write_text(json.dumps({"order": mo, "lines": {u: [[l, s, full] for l, s, full in mt[u]] for u in mt}}), encoding="utf-8")
    sig = E012.score(mt, mo)
    state, d, norm = E012.distance(sig, V)
    dS = abs(sig["delta_S"] - V["delta_S"])
    h30a = "SUPPORTED" if dS <= 0.05 else "FALSIFIED" if dS > 0.10 else "PARTIAL"
    rest = ("delta_L", "delta_C", "TTR", "H1", "F_excess", "dJ_order")
    within = {X: (d[X] <= (0.05 if X in ("delta_L", "delta_C") else 0.02)) for X in rest}
    n_within = sum(within.values())
    h30b = "SUPPORTED" if n_within >= 4 else "FALSIFIED" if n_within <= 1 else "PARTIAL"
    vt, vo = E012.truncate(vlines, vorder, E012.N_MATCH)
    (OUT_DIR / "V_matched.json").write_text(json.dumps({"order": vo, "lines": {u: [[l, s, full] for l, s, full in vt[u]] for u in vt}}), encoding="utf-8")
    sel_V, sel_M = top1_share(vt, vo), top1_share(mt, mo)
    diff = sel_M["top1_share"] - sel_V["top1_share"]
    h30c = "SUPPORTED" if diff >= -0.10 else "FALSIFIED" if diff < -0.20 else "PARTIAL"
    out = {"experiment": "E020", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "ed983a0", "run_head_commit": E012.head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__},
           "calibration": {"text": "N_DEU", "target": TARGET, "grid_delta_S": cal, "p_star": p_star},
           "voynich_reference": V, "prediction_text": "N_ITA", "MIX_signature": sig, "distance": {"abs_diff": d, "normalised_L1": norm, "state": state},
           "components_within_tolerance": within, "n_within": n_within,
           "selectivity": {"voynich": sel_V, "mix": sel_M, "difference": diff},
           "hypothesis_outcomes": {"H030a": h30a, "H030b": h30b, "H030c": h30c},
           "claim_ceiling": "Which boundary processes reproduce which structural components; no decipherment; no Gate level."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"p_star": p_star, "MIX": {k: round(v, 4) for k, v in sig.items() if k in E012.COMPS}, "V": {k: round(V[k], 4) for k in E012.COMPS},
                      "within": within, "selectivity": {"V": sel_V, "MIX": sel_M}, "H": out["hypothesis_outcomes"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
