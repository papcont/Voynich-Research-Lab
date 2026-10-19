"""E014 — generator-family component signatures on the ZL3b skeleton (FIRST RUN).

Implements experiments/E014_generator_signatures/PLAN.md. Signature code is imported
from the frozen E011 (Δ_S, Δ_L; backoff coder) and E008 (Δ_C; plain KT copy model)
runners so nothing is redefined. Generated texts are written to runs/E014/ (git-ignored).
results.json is written BEFORE any interpretation.

Run:  python experiments/E014_generator_signatures/run.py
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


E011 = _load("e011_run", ROOT / "experiments" / "E011_targeted_context_scorecard" / "run.py")
E008 = _load("e008_run", ROOT / "experiments" / "E008_mechanism_competition" / "run.py")
from voynichlab.p70 import parse_p70  # noqa: E402
from voynichlab.gate import bootstrap_mean_ci  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runs" / "E014"
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
SEEDS = [20261030 + i for i in range(5)]
GRID = list(itertools.product((0.5, 0.7, 0.9), (0.3, 0.6, 0.9)))
WINDOW = 20
W_C = 5
BOOT_SEED = 20261019
MATCH, MISMATCH = 0.05, 0.10
GENERATORS = ("G1_IND", "G2_UNI", "G3_SC", "G4_EDGE")


# --------------------------------------------------------------------------- #
# skeleton and statistics
# --------------------------------------------------------------------------- #
def skeleton():
    """ZL3b running-text lines: folio -> [(lang, sec, [[value, uncertain], ...]), ...]."""
    _toks, lines = E011.load_population()
    return lines


def stats(lines):
    toks = [v for folio in sorted(lines) for _l, _s, full in lines[folio] for v, u in full if not u]
    uni = Counter(toks)
    slots = [parse_p70(v) for v in toks]
    marg = [Counter(s[i] for s in slots) for i in range(4)]
    glyph = Counter(c for v in toks for c in v)
    by_prefix = defaultdict(Counter)
    for v, s in zip(toks, slots):
        by_prefix[s[0]][v] += 1
    # P(prefix | S) with S = previous final char / BOL / UNC, from the real lines
    pS = defaultdict(Counter)
    for folio in sorted(lines):
        for _l, _s, full in lines[folio]:
            for i, (v, u) in enumerate(full):
                if u:
                    continue
                S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                pS[S][parse_p70(v)[0]] += 1
    return {"tokens": toks, "uni": uni, "marg": marg, "glyph": glyph, "by_prefix": by_prefix, "pS": pS}


def draw(rng, counter):
    keys = list(counter.keys())
    p = np.fromiter(counter.values(), dtype=float)
    return keys[rng.choice(len(keys), p=p / p.sum())]


def ttr_hapax(lines):
    c = Counter(v for folio in lines for _l, _s, full in lines[folio] for v, u in full if not u)
    n = sum(c.values())
    return len(c) / n, sum(1 for k in c if c[k] == 1) / len(c)


# --------------------------------------------------------------------------- #
# generators (replace certain tokens in place; uncertain placeholders untouched)
# --------------------------------------------------------------------------- #
def generate(name, lines, st, seed, params=None):
    rng = np.random.default_rng(seed)
    out = {}
    for folio in sorted(lines):
        window = []
        new_lines = []
        for lang, sec, full in lines[folio]:
            nf = [[v, u] for v, u in full]
            for i, (v, u) in enumerate(nf):
                if u:
                    continue
                if name == "G1_IND":
                    tok = "".join(draw(rng, st["marg"][k]) for k in range(4)) or draw(rng, st["uni"])
                elif name == "G2_UNI":
                    tok = draw(rng, st["uni"])
                elif name == "G3_SC":
                    p_copy, p_edit = params
                    if window and rng.random() < p_copy:
                        src = window[-1 - int(rng.integers(min(WINDOW, len(window))))]
                        tok = src
                        if rng.random() < p_edit:
                            op = rng.integers(3)
                            if op == 0 or len(src) == 1 and op == 2:  # substitute
                                pos = int(rng.integers(len(src)))
                                tok = src[:pos] + draw(rng, st["glyph"]) + src[pos + 1:]
                            elif op == 1:  # insert
                                pos = int(rng.integers(len(src) + 1))
                                tok = src[:pos] + draw(rng, st["glyph"]) + src[pos:]
                            else:  # delete (len >= 2)
                                pos = int(rng.integers(len(src)))
                                tok = src[:pos] + src[pos + 1:]
                    else:
                        tok = draw(rng, st["uni"])
                elif name == "G4_EDGE":
                    S = "BOL" if i == 0 else "UNC" if nf[i - 1][1] else nf[i - 1][0][-1]
                    pfx = draw(rng, st["pS"][S]) if st["pS"].get(S) else draw(rng, st["marg"][0])
                    tok = draw(rng, st["by_prefix"][pfx])
                else:
                    raise ValueError(name)
                nf[i][0] = tok
                window.append(tok)
            new_lines.append((lang, sec, nf))
        out[folio] = new_lines
    return out


# --------------------------------------------------------------------------- #
# signature components
# --------------------------------------------------------------------------- #
def folio_mean_delta(toks_folio, per_a, per_b):
    ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for f, x, y in zip(toks_folio, per_a, per_b):
        ba[f] += x; bb[f] += y; n[f] += 1
    fol = sorted(n)
    d = np.array([(ba[f] - bb[f]) / n[f] for f in fol])  # a = base (worse) minus b = conditioned
    mean, lo, hi = bootstrap_mean_ci(d, 10000, BOOT_SEED, 0.025)
    return {"mean": mean, "ci_lower": lo, "ci_upper": hi, "n_folios": len(fol)}


def signature(lines):
    toks, _ = E011.load_population(lines)
    sigma = len({c for t in toks for c in t.value})
    folios = [t.folio for t in toks]
    p0 = E011.crossfit(toks, E011.MODELS["M0"], sigma)
    pS = E011.crossfit(toks, E011.MODELS["M_S"], sigma)
    pL = E011.crossfit(toks, E011.MODELS["M_L"], sigma)
    # Δ_C with the E008 machinery (plain KT, copy model, W=5), 5-fold cross-fit
    by_folio = {f: [E008.Line(f, lang, sec, None, [[v, u] for v, u in full]) for lang, sec, full in lines[f]] for f in lines}
    etoks = E008.materialize(by_folio, sorted(by_folio))
    assert [t.value for t in etoks] == [t.value for t in toks]
    cache = {}
    perB1, perB1C = np.empty(len(etoks)), np.empty(len(etoks))
    for j in range(E008.N_FOLDS):
        m1 = E008.Model(("B1", frozenset()), W_C, sigma, cache)
        m2 = E008.Model(("B1", frozenset("C")), W_C, sigma, cache)
        for t in etoks:
            if t.fold != j:
                m1.code(t, True); m2.code(t, True)
        for k, t in enumerate(etoks):
            if t.fold == j:
                perB1[k] = m1.code(t, False); perB1C[k] = m2.code(t, False)
    return {"delta_S": folio_mean_delta(folios, p0, pS), "delta_L": folio_mean_delta(folios, p0, pL),
            "delta_C": folio_mean_delta(folios, perB1, perB1C),
            "bits_per_token": {"M0": float(p0.mean()), "M_S": float(pS.mean()), "M_L": float(pL.mean()),
                               "B1_plainKT": float(perB1.mean()), "B1+C": float(perB1C.mean())}, "n_tokens": len(toks)}


def decide(gen_means, voy):
    d = {X: abs(gen_means[X] - voy[X]["mean"]) for X in ("delta_S", "delta_L", "delta_C")}
    if all(v <= MATCH for v in d.values()):
        state = "SIGNATURE_MATCH"
    elif any(v > MISMATCH for v in d.values()):
        state = "SIGNATURE_MISMATCH"
    else:
        state = "PARTIAL"
    return state, d


def main() -> int:
    raw = DATA.read_bytes()
    if E008.git_blob_sha1(raw) != "2a4533ab9bdfa85db9bad602d590978953055df1":
        raise SystemExit("source identity mismatch")
    lines = skeleton()
    st = stats(lines)
    voy_ttr, voy_hapax = ttr_hapax(lines)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- G3 calibration (recorded before any signature) ----
    calib = {}
    for pc, pe in GRID:
        g = generate("G3_SC", lines, st, SEEDS[0], (pc, pe))
        t, h = ttr_hapax(g)
        calib[f"{pc},{pe}"] = {"ttr": t, "hapax": h, "loss": abs(t - voy_ttr) + abs(h - voy_hapax)}
    best = min(calib, key=lambda k: (calib[k]["loss"], k))
    g3_params = tuple(float(x) for x in best.split(","))
    print("G3 calibration:", best, calib[best], "voynich ttr/hapax", round(voy_ttr, 4), round(voy_hapax, 4))

    # ---- signatures ----
    voy = signature(lines)
    print("Voynich (exploratory):", {k: round(v["mean"], 4) for k, v in voy.items() if k.startswith("delta")})
    results = {}
    for name in GENERATORS:
        per_seed = []
        for s in SEEDS:
            g = generate(name, lines, st, s, g3_params if name == "G3_SC" else None)
            (OUT_DIR / f"{name}_{s}.json").write_text(json.dumps({f: [[lang, sec, full] for lang, sec, full in g[f]] for f in g}), encoding="utf-8")
            sig = signature(g)
            t, h = ttr_hapax(g)
            sig["ttr"], sig["hapax"] = t, h
            per_seed.append(sig)
            print(name, s, {k: round(v["mean"], 4) for k, v in sig.items() if k.startswith("delta")}, "ttr", round(t, 3))
        means = {X: float(np.mean([p[X]["mean"] for p in per_seed])) for X in ("delta_S", "delta_L", "delta_C")}
        sds = {X: float(np.std([p[X]["mean"] for p in per_seed], ddof=1)) for X in ("delta_S", "delta_L", "delta_C")}
        state, d = decide(means, voy)
        results[name] = {"per_seed": per_seed, "mean_over_seeds": means, "sd_over_seeds": sds, "abs_diff_to_voynich": d, "decision": state,
                         "params": list(g3_params) if name == "G3_SC" else None}
    out = {
        "experiment": "E014", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
        "frozen_plan_commit": "9ce3637", "run_head_commit": E008.head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__}, "seeds": SEEDS,
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()},
        "voynich_reference_EXPLORATORY": {**voy, "ttr": voy_ttr, "hapax": voy_hapax},
        "G3_calibration": {"grid": calib, "chosen": best, "rule": "min |TTR diff| + |hapax diff| on seed 0"},
        "generators": results,
        "hypothesis_outcomes": {"H020": "FALSIFIED" if results["G3_SC"]["decision"] == "SIGNATURE_MISMATCH" else "SUPPORTED" if results["G3_SC"]["decision"] == "SIGNATURE_MATCH" else "PARTIAL",
                                "H021": "FALSIFIED" if results["G4_EDGE"]["decision"] == "SIGNATURE_MISMATCH" else "SUPPORTED" if results["G4_EDGE"]["decision"] == "SIGNATURE_MATCH" else "PARTIAL"},
        "signature_diagnostic": "NON_DIAGNOSTIC" if results["G4_EDGE"]["decision"] == "SIGNATURE_MATCH" else "DIAGNOSTIC_AGAINST_TESTED_GENERATORS",
        "claim_ceiling": "Which simple generators reproduce which structural components; no meaning/language; no Gate level.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({n: (r["decision"], {k: round(v, 4) for k, v in r["mean_over_seeds"].items()}) for n, r in results.items()}, indent=1))
    print("H020", out["hypothesis_outcomes"]["H020"], "H021", out["hypothesis_outcomes"]["H021"], out["signature_diagnostic"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
