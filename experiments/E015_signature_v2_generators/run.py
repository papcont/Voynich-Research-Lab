"""E015 — signature v2 and stronger generators (FIRST RUN).

Implements experiments/E015_signature_v2_generators/PLAN.md. Sequence components and
the E014 generators/stats are imported from the frozen E014 runner; inventory and sharing
components are defined here. Calibrations are recorded before any signature is read.
Generated texts go to runs/E015/ (git-ignored). results.json first.

Run:  python experiments/E015_signature_v2_generators/run.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import platform
import sys
from collections import Counter, defaultdict
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


E014 = _load("e014_run", ROOT / "experiments" / "E014_generator_signatures" / "run.py")
from voynichlab.p70 import parse_p70  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runs" / "E015"
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
SEEDS = [20261040 + i for i in range(5)]
GRID_PY = list(itertools.product((0.5, 0.7, 0.9), (10, 100, 1000)))
GRID_SC = list(itertools.product((0.5, 0.7, 0.9), (0.3, 0.6, 0.9)))
BITS = ("delta_S", "delta_L", "delta_C")
FRACS = ("TTR", "H1", "F", "X")
TOL = {"bits": (0.05, 0.10), "fractions": (0.02, 0.05)}


# --------------------------------------------------------------------------- #
# inventory / sharing components
# --------------------------------------------------------------------------- #
def inventory(lines):
    per_folio = {f: [v for _l, _s, full in lines[f] for v, u in full if not u] for f in lines}
    all_tokens = [v for f in sorted(per_folio) for v in per_folio[f]]
    c = Counter(all_tokens)
    ttr = len(c) / len(all_tokens)
    h1 = sum(1 for k in c if c[k] == 1) / len(c)
    F = float(np.mean([1 - len(set(t)) / len(t) for t in per_folio.values() if t]))
    folio_types = {f: set(t) for f, t in per_folio.items() if t}
    count_in_folios = Counter(ty for s in folio_types.values() for ty in s)
    X = float(np.mean([np.mean([count_in_folios[ty] > 1 for ty in s]) for s in folio_types.values()]))
    return {"TTR": ttr, "H1": h1, "F": F, "X": X}


# --------------------------------------------------------------------------- #
# generators
# --------------------------------------------------------------------------- #
def prefix_conditionals(st):
    """Empirical marginals of (gallows, core, suffix) given prefix, for new-type creation."""
    out = defaultdict(lambda: [Counter(), Counter(), Counter()])
    for v, n in st["uni"].items():
        p, g, c, s = parse_p70(v)
        out[p][0][g] += n; out[p][1][c] += n; out[p][2][s] += n
    return out


def generate_g5(lines, st, seed, d, theta, cond):
    rng = np.random.default_rng(seed)
    rest = defaultdict(lambda: {"n": 0, "counts": Counter()})  # per prefix
    out = {}
    for folio in sorted(lines):
        new_lines = []
        for lang, sec, full in lines[folio]:
            nf = [[v, u] for v, u in full]
            for i, (v, u) in enumerate(nf):
                if u:
                    continue
                S = "BOL" if i == 0 else "UNC" if nf[i - 1][1] else nf[i - 1][0][-1]
                pfx = E014.draw(rng, st["pS"][S]) if st["pS"].get(S) else E014.draw(rng, st["marg"][0])
                r = rest[pfx]
                K = len(r["counts"])
                p_new = (theta + d * K) / (r["n"] + theta)
                if r["n"] == 0 or rng.random() < p_new:
                    tok = None
                    for _ in range(50):
                        cand = pfx + "".join(E014.draw(rng, cond[pfx][k]) for k in range(3))
                        if cand and cand not in r["counts"]:
                            tok = cand
                            break
                    if tok is None:
                        tok = pfx + "".join(E014.draw(rng, cond[pfx][k]) for k in range(3)) or E014.draw(rng, st["uni"])
                else:
                    keys = list(r["counts"].keys())
                    w = np.array([r["counts"][k] - d for k in keys], dtype=float)
                    tok = keys[rng.choice(len(keys), p=w / w.sum())]
                r["counts"][tok] += 1
                r["n"] += 1
                nf[i][0] = tok
            new_lines.append((lang, sec, nf))
        out[folio] = new_lines
    return out


def generate_g6(lines, st, seed, p_copy, p_edit):
    rng = np.random.default_rng(seed)
    out = {}
    for folio in sorted(lines):
        hist = []
        new_lines = []
        for lang, sec, full in lines[folio]:
            nf = [[v, u] for v, u in full]
            for i, (v, u) in enumerate(nf):
                if u:
                    continue
                if hist and rng.random() < p_copy:
                    src = hist[int(rng.integers(len(hist)))]
                    tok = src
                    if rng.random() < p_edit:
                        op = rng.integers(3)
                        if op == 0 or (len(src) == 1 and op == 2):
                            pos = int(rng.integers(len(src)))
                            tok = src[:pos] + E014.draw(rng, st["glyph"]) + src[pos + 1:]
                        elif op == 1:
                            pos = int(rng.integers(len(src) + 1))
                            tok = src[:pos] + E014.draw(rng, st["glyph"]) + src[pos:]
                        else:
                            pos = int(rng.integers(len(src)))
                            tok = src[:pos] + src[pos + 1:]
                else:
                    tok = E014.draw(rng, st["uni"])
                nf[i][0] = tok
                hist.append(tok)
            new_lines.append((lang, sec, nf))
        out[folio] = new_lines
    return out


# --------------------------------------------------------------------------- #
# decision
# --------------------------------------------------------------------------- #
def decide(means, voy):
    diffs, state_flags = {}, []
    for X in BITS + FRACS:
        diffs[X] = abs(means[X] - voy[X])
    m_tol, mm_tol = TOL["bits"], TOL["fractions"]
    match = all(diffs[X] <= m_tol[0] for X in BITS) and all(diffs[X] <= mm_tol[0] for X in FRACS)
    mismatch = [X for X in BITS if diffs[X] > m_tol[1]] + [X for X in FRACS if diffs[X] > mm_tol[1]]
    state = "MATCH" if match else "MISMATCH" if mismatch else "PARTIAL"
    off = [X for X in BITS if diffs[X] > m_tol[0]] + [X for X in FRACS if diffs[X] > mm_tol[0]]
    return state, diffs, off


def full_signature(lines):
    sig = E014.signature(lines)
    inv = inventory(lines)
    flat = {X: sig[X]["mean"] for X in BITS}
    flat.update(inv)
    return sig, inv, flat


def main() -> int:
    raw = DATA.read_bytes()
    if E014.E008.git_blob_sha1(raw) != "2a4533ab9bdfa85db9bad602d590978953055df1":
        raise SystemExit("source identity mismatch")
    lines = E014.skeleton()
    st = E014.stats(lines)
    cond = prefix_conditionals(st)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    voy_inv = inventory(lines)

    # ---- calibrations first (TTR + H1 on seed 0) ----
    cal5 = {}
    for d, th in GRID_PY:
        inv = inventory(generate_g5(lines, st, SEEDS[0], d, th, cond))
        cal5[f"{d},{th}"] = {**inv, "loss": abs(inv["TTR"] - voy_inv["TTR"]) + abs(inv["H1"] - voy_inv["H1"])}
    best5 = min(cal5, key=lambda k: (cal5[k]["loss"], k))
    d5, th5 = float(best5.split(",")[0]), float(best5.split(",")[1])
    cal6 = {}
    for pc, pe in GRID_SC:
        inv = inventory(generate_g6(lines, st, SEEDS[0], pc, pe))
        cal6[f"{pc},{pe}"] = {**inv, "loss": abs(inv["TTR"] - voy_inv["TTR"]) + abs(inv["H1"] - voy_inv["H1"])}
    best6 = min(cal6, key=lambda k: (cal6[k]["loss"], k))
    pc6, pe6 = (float(x) for x in best6.split(","))
    print("calibration G5", best5, {k: round(v, 3) for k, v in cal5[best5].items()}, "| G6", best6,
          {k: round(v, 3) for k, v in cal6[best6].items()}, "| voynich", {k: round(v, 3) for k, v in voy_inv.items()})

    # ---- signatures ----
    voy_sig, _, voy_flat = full_signature(lines)
    print("Voynich (exploratory):", {k: round(v, 4) for k, v in voy_flat.items()})
    gens = {"G4_EDGE": lambda s: E014.generate("G4_EDGE", lines, st, s),
            "G5_EDGE_PY": lambda s: generate_g5(lines, st, s, d5, th5, cond),
            "G6_FOLIO_SC": lambda s: generate_g6(lines, st, s, pc6, pe6)}
    results = {}
    for name, fn in gens.items():
        per_seed, flats = [], []
        for s in SEEDS:
            g = fn(s)
            (OUT_DIR / f"{name}_{s}.json").write_text(json.dumps({f: [[l, se, full] for l, se, full in g[f]] for f in g}), encoding="utf-8")
            sig, inv, flat = full_signature(g)
            per_seed.append({"sequence": sig, "inventory": inv}); flats.append(flat)
            print(name, s, {k: round(v, 4) for k, v in flat.items()})
        means = {X: float(np.mean([f[X] for f in flats])) for X in BITS + FRACS}
        sds = {X: float(np.std([f[X] for f in flats], ddof=1)) for X in BITS + FRACS}
        state, diffs, off = decide(means, voy_flat)
        results[name] = {"per_seed": per_seed, "mean_over_seeds": means, "sd_over_seeds": sds, "abs_diff_to_voynich": diffs,
                         "components_outside_match_tolerance": off, "decision": state,
                         "params": {"G5_EDGE_PY": [d5, th5], "G6_FOLIO_SC": [pc6, pe6]}.get(name)}
    hyp = lambda s: "FALSIFIED" if s == "MISMATCH" else "SUPPORTED" if s == "MATCH" else "PARTIAL"  # noqa: E731
    out = {"experiment": "E015", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "3bc52d2", "run_head_commit": E014.E008.head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__}, "seeds": SEEDS,
           "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()},
           "voynich_reference_EXPLORATORY": {"sequence": voy_sig, "inventory": voy_inv, "flat": voy_flat},
           "calibration": {"G5": {"grid": cal5, "chosen": best5}, "G6": {"grid": cal6, "chosen": best6},
                           "rule": "min |TTR diff| + |H1 diff| on seed 0; TTR/H1 matches are by construction"},
           "tolerances": TOL, "generators": results,
           "hypothesis_outcomes": {"H022": hyp(results["G5_EDGE_PY"]["decision"]), "H023": hyp(results["G6_FOLIO_SC"]["decision"])},
           "claim_ceiling": "Which generators reproduce which structural components; no meaning/language; no Gate level."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({n: (r["decision"], r["components_outside_match_tolerance"], {k: round(v, 4) for k, v in r["mean_over_seeds"].items()}) for n, r in results.items()}, indent=1))
    print(out["hypothesis_outcomes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
