"""E021 — selectivity of the boundary coupling; selective boundary processes (FIRST RUN).

Implements experiments/E021_selective_boundaries/PLAN.md. Reuses E012/E019 preparation and
E020's verbose+mix machinery via module loading. Calibration on N_DEU is recorded before
any N_ITA value. Prepared texts: runs/E021/. results.json first.

Run:  python experiments/E021_selective_boundaries/run.py
"""
from __future__ import annotations

import json
import math
import platform
import sys
from collections import Counter
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
OUT_DIR = ROOT / "runs" / "E021"
GRID = [round(0.1 * i, 1) for i in range(1, 11)]
TARGET = 0.178
SEED_L, SEED_M, SEED_PL, SEED_PM = 20261130, 20261150, 20261170, 20261171


# --------------------------------------------------------------------------- #
# S1 measure
# --------------------------------------------------------------------------- #
def _mi(joint: Counter) -> float:
    n = sum(joint.values())
    pa, pb = Counter(), Counter()
    for (a, b), c in joint.items():
        pa[a] += c; pb[b] += c
    return sum(c / n * math.log2((c / n) / ((pa[a] / n) * (pb[b] / n))) for (a, b), c in joint.items())


def s1(lines, order):
    joint = Counter()
    for u in order:
        for _l, _s, full in lines[u]:
            for i in range(1, len(full)):
                if full[i][1] or full[i - 1][1]:
                    continue
                joint[(full[i - 1][0][-1], full[i][0][0])] += 1
    I = _mi(joint)
    n = sum(joint.values())
    best, best_pair = -1.0, None
    pairs = {p for p in joint}
    for (a0, b0) in pairs:
        bj = Counter()
        for (a, b), c in joint.items():
            bj[(a == a0, b == b0)] += c
        ip = _mi(bj)
        if ip > best:
            best, best_pair = ip, (a0, b0)
    return {"I_bits": I, "S1": best / I if I > 0 else float("nan"), "pair": list(best_pair), "n_boundaries": n}


# --------------------------------------------------------------------------- #
# selective processes on a verbose stream
# --------------------------------------------------------------------------- #
def most_frequent_letter(plain_lines):
    c = Counter(ch for u in plain_lines for _l, _s, full in plain_lines[u] for v, _uu in full for ch in v)
    return max(c, key=lambda k: (c[k], k))


def sel_l(verb_lines, code, q, rng):
    """Keep word boundaries; also cut after every occurrence of `code` (a 2-symbol unit) with prob q."""
    out = {}
    for u in verb_lines:
        new = []
        for l, s, full in verb_lines[u]:
            toks = []
            for v, uu in full:
                if uu:
                    toks.append([v, uu]); continue
                pieces, start = [], 0
                i = 0
                while i + 2 <= len(v):
                    if v[i:i + 2] == code and i + 2 < len(v) and rng.random() < q:
                        pieces.append(v[start:i + 2]); start = i + 2
                    i += 2
                pieces.append(v[start:])
                toks.extend([pc, False] for pc in pieces if pc)
            new.append((l, s, toks))
        out[u] = new
    return out


def sel_m(verb_lines, r, rng):
    """At a fraction r of word boundaries append Y to the left word and prepend Q to the right word."""
    out = {}
    for u in verb_lines:
        new = []
        for l, s, full in verb_lines[u]:
            toks = [[v, uu] for v, uu in full]
            for i in range(1, len(toks)):
                if toks[i][1] or toks[i - 1][1]:
                    continue
                if rng.random() < r:
                    toks[i - 1][0] += "Y"; toks[i][0] = "Q" + toks[i][0]
            new.append((l, s, toks))
        out[u] = new
    return out


def load_prepared(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return {u: [(l, s, full) for l, s, full in d["lines"][u]] for u in d["lines"]}, d["order"]


def delta_S_matched(lines, order):
    mt, mo = E012.truncate(lines, order, E012.N_MATCH)
    return float(SG.signature(mt, components=("delta_S",), slot_fn=SG.a3_slots, folio_order=mo)["delta_S"]), mt, mo


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vlines, vorder = E012.voynich_lines()
    ll = E012.zl3b_line_lengths(vlines)
    e12 = json.loads((ROOT / "experiments" / "E012_reference_signature" / "results.json").read_text(encoding="utf-8"))
    V = e12["results"]["size_matched"]["V"]
    rng_reseg = np.random.default_rng(E012.SEED_RESEG)
    plain, orders = {}, {}
    for tid, (src, lang) in E012.TEXTS.items():
        lines, order, _ = E012.reference_lines(src, lang, ll, rng_reseg)
        if tid in ("N_DEU", "N_ITA"):
            plain[tid], orders[tid] = lines, order
    verb = {t: E019.verbose(plain[t]) for t in plain}
    # letter codes (E019 verbose table is deterministic per source alphabet)
    def code_of(t):
        letter = most_frequent_letter(plain[t])
        # find the code by encoding a one-letter token through the same table
        probe = {"x": [("", "", [[letter, False]])]}
        return E019.verbose(probe)["x"][0][2][0][0], letter

    # ---- S1 on existing texts ----
    s1_res = {}
    vt, vo = E012.truncate(vlines, vorder, E012.N_MATCH)
    s1_res["V"] = s1(vt, vo); s1_res["V_full"] = s1(vlines, vorder)
    for tid in ("N_DEU", "N_ITA"):
        mt, mo = E012.truncate(plain[tid], orders[tid], E012.N_MATCH); s1_res[tid] = s1(mt, mo)
    for name in ("C_STREAM(N_DEU)", "C_STREAM(N_ITA)"):
        lines, order = load_prepared(ROOT / "runs" / "E019" / f"{name}.json"); s1_res[name] = s1(lines, order)
    lines, order = load_prepared(ROOT / "runs" / "E020" / "MIX_N_ITA.json"); s1_res["MIX(0.8)(N_ITA)"] = s1(lines, order)
    print("S1:", {k: (round(v["S1"], 3), v["pair"]) for k, v in s1_res.items()})

    # ---- calibration on N_DEU ----
    code_deu, letter_deu = code_of("N_DEU")
    cal = {"SEL_L": {}, "SEL_M": {}}
    for gi, g in enumerate(GRID):
        cal["SEL_L"][str(g)] = delta_S_matched(sel_l(verb["N_DEU"], code_deu, g, np.random.default_rng(SEED_L + gi)), orders["N_DEU"])[0]
        cal["SEL_M"][str(g)] = delta_S_matched(sel_m(verb["N_DEU"], g, np.random.default_rng(SEED_M + gi)), orders["N_DEU"])[0]
    star = {}
    for proc in cal:
        best = min(abs(v - TARGET) for v in cal[proc].values())
        star[proc] = max(float(g) for g, v in cal[proc].items() if abs(v - TARGET) == best)
    print("calibration:", {p: {g: round(v, 3) for g, v in c.items()} for p, c in cal.items()}, "stars", star)

    # ---- predictions on N_ITA ----
    code_ita, letter_ita = code_of("N_ITA")
    pred = {}
    for proc, lines in (("SEL_L", sel_l(verb["N_ITA"], code_ita, star["SEL_L"], np.random.default_rng(SEED_PL))),
                        ("SEL_M", sel_m(verb["N_ITA"], star["SEL_M"], np.random.default_rng(SEED_PM)))):
        dS, mt, mo = delta_S_matched(lines, orders["N_ITA"])
        (OUT_DIR / f"{proc}_N_ITA.json").write_text(json.dumps({"order": mo, "lines": {u: [[l, s, full] for l, s, full in mt[u]] for u in mt}}), encoding="utf-8")
        sig = E012.score(mt, mo)
        s = s1(mt, mo)
        dd, ds1 = abs(sig["delta_S"] - TARGET), abs(s["S1"] - s1_res["V"]["S1"])
        verdict = "SUPPORTED" if (dd <= 0.05 and ds1 <= 0.10) else "FALSIFIED" if (dd > 0.10 or ds1 > 0.20) else "PARTIAL"
        pred[proc] = {"param": star[proc], "signature": sig, "S1": s, "abs_diff_delta_S": dd, "abs_diff_S1": ds1, "verdict": verdict}
        print(proc, star[proc], "delta_S", round(sig["delta_S"], 4), "S1", round(s["S1"], 3), s["pair"], verdict)
    (OUT_DIR / "V_matched.json").write_text(json.dumps({"order": vo, "lines": {u: [[l, s, full] for l, s, full in vt[u]] for u in vt}}), encoding="utf-8")
    others = ["N_DEU", "N_ITA", "C_STREAM(N_DEU)", "C_STREAM(N_ITA)", "MIX(0.8)(N_ITA)"]
    sv = s1_res["V"]["S1"]
    h31 = "SUPPORTED" if all(sv >= s1_res[x]["S1"] + 0.10 for x in others) else "FALSIFIED" if any(s1_res[x]["S1"] >= sv for x in others) else "PARTIAL"
    out = {"experiment": "E021", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "d399697", "run_head_commit": E012.head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__},
           "S1": s1_res, "calibration": {"text": "N_DEU", "target": TARGET, "grid": cal, "star": star,
                                          "SEL_L_letter": {"N_DEU": letter_deu, "N_ITA": letter_ita}, "SEL_L_code": {"N_DEU": code_deu, "N_ITA": code_ita}},
           "predictions_N_ITA": pred, "voynich_reference": V,
           "hypothesis_outcomes": {"H031": h31, "H032": pred["SEL_M"]["verdict"], "H033": pred["SEL_L"]["verdict"]},
           "claim_ceiling": "Which boundary processes reproduce which structural properties; Y/Q abstract; no decipherment; no Gate level."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out["hypothesis_outcomes"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
