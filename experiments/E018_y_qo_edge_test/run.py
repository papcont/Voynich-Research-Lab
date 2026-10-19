"""E018 — y -> qo edge transition as a frozen test (FIRST RUN).

Implements experiments/E018_y_qo_edge_test/PLAN.md using the shared signature module's
feature extraction and backoff cross-fit (frozen definitions). results.json first.

Run:  python experiments/E018_y_qo_edge_test/run.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab import signature as SG  # noqa: E402
from voynichlab.gate import bootstrap_mean_ci  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
SEED_PERM, SEED_BOOT, NPERM = 20261070, 20261019, 1000


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def load_lines():
    lines = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            lines[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    return dict(lines)


def enrichment(toks):
    """R = P(qo | prev y) / P(qo | prev other final); None if undefined."""
    y = [t for t in toks if t.S == "y"]
    o = [t for t in toks if t.S not in ("y", "BOL", "UNC")]
    if not y or not o:
        return None
    py = np.mean([t.slots[0] == "qo" for t in y]); po = np.mean([t.slots[0] == "qo" for t in o])
    return float(py / po) if po > 0 else None, float(py), float(po), len(y), len(o)


def permute_within_folio(lines, rng):
    out = {}
    for folio in sorted(lines):
        new = [(l, s, [[v, u] for v, u in full]) for l, s, full in lines[folio]]
        pos = [(ln, i) for ln in new for i, (_, u) in enumerate(ln[2]) if not u]
        vals = [ln[2][i][0] for ln, i in pos]
        perm = rng.permutation(len(vals))
        for (ln, i), j in zip(pos, perm):
            ln[2][i][0] = vals[j]
        out[folio] = new
    return out


class SyTok:
    """Wrapper exposing the binary feature Sy for the backoff cross-fit."""
    __slots__ = ("value", "slots", "folio", "fold", "S", "L", "Sy")

    def __init__(self, t):
        self.value, self.slots, self.folio, self.fold, self.S, self.L = t.value, t.slots, t.folio, t.fold, t.S, t.L
        self.Sy = t.S if t.S in ("y", "BOL", "UNC") else "other"


def main() -> int:
    raw = DATA.read_bytes()
    if git_blob_sha1(raw) != "2a4533ab9bdfa85db9bad602d590978953055df1":
        raise SystemExit("source identity mismatch")
    lines = load_lines()
    toks = SG.tokens(lines)
    sub = {"bio_B": [t for t in toks if t.language == "B" and t.section == "B"],
           "other_B": [t for t in toks if t.language == "B" and t.section != "B"],
           "A": [t for t in toks if t.language == "A"]}
    R_obs = {k: enrichment(v) for k, v in sub.items()}
    rng = np.random.default_rng(SEED_PERM)
    null = {k: [] for k in sub}
    prefix_of = {t.value: t.slots[0] for t in toks}
    selectors = {"bio_B": lambda l, s: l == "B" and s == "B", "other_B": lambda l, s: l == "B" and s != "B", "A": lambda l, s: l == "A"}
    for _ in range(NPERM):
        pl = permute_within_folio(lines, rng)
        light = {k: [] for k in sub}  # (S, prefix) pairs per subset — the only features enrichment needs
        for folio in sorted(pl):
            for lang, sec, full in pl[folio]:
                for i, (v, u) in enumerate(full):
                    if u:
                        continue
                    S = "BOL" if i == 0 else "UNC" if full[i - 1][1] else full[i - 1][0][-1]
                    for k, f in selectors.items():
                        if f(lang, sec):
                            light[k].append((S, prefix_of[v]))
        for k in sub:
            y = [p for s_, p in light[k] if s_ == "y"]
            o = [p for s_, p in light[k] if s_ not in ("y", "BOL", "UNC")]
            po = np.mean([p == "qo" for p in o])
            null[k].append(float(np.mean([p == "qo" for p in y]) / po) if (y and o and po > 0) else np.nan)
    stats = {}
    for k in sub:
        R = R_obs[k][0]
        nk = np.array(null[k], dtype=float)
        stats[k] = {"R": R, "p_qo_after_y": R_obs[k][1], "p_qo_after_other": R_obs[k][2], "n_after_y": R_obs[k][3], "n_after_other": R_obs[k][4],
                    "null_mean": float(np.nanmean(nk)), "null_q975": float(np.nanquantile(nk, 0.975)),
                    "p_perm": float((1 + np.nansum(nk >= R)) / (NPERM + 1))}
    b = stats["bio_B"]
    dec_a = ("SUPPORTED_DEV" if (b["R"] >= 1.5 and b["p_perm"] <= 0.01) else "FALSIFIED_DEV" if (b["R"] <= 1.1 or b["null_q975"] >= b["R"])
             else "INCONCLUSIVE_DEV")

    # ---- codelength share on Currier B ----
    B = [SyTok(t) for t in toks if t.language == "B"]
    sigma = len({c for t in toks for c in t.value})
    p0 = SG._crossfit_backoff(B, {}, sigma)
    pS = SG._crossfit_backoff(B, {0: ("S",)}, sigma)
    pSy = SG._crossfit_backoff(B, {0: ("Sy",)}, sigma)
    def per_folio(pa, pb):
        ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
        for t, x, y in zip(B, pa, pb):
            ba[t.folio] += x; bb[t.folio] += y; n[t.folio] += 1
        return np.array([(ba[f] - bb[f]) / n[f] for f in sorted(n)])
    dS, dSy = per_folio(p0, pS), per_folio(p0, pSy)
    mS, loS, hiS = bootstrap_mean_ci(dS, 10000, SEED_BOOT, 0.025)
    mSy, loSy, hiSy = bootstrap_mean_ci(dSy, 10000, SEED_BOOT, 0.025)
    share = float(mSy / mS) if mS > 0 else float("nan")
    dec_b = ("SUPPORTED_DEV" if (mSy >= 0.05 and loSy > 0 and share >= 0.5) else "FALSIFIED_DEV" if (hiSy < 0.05 or share < 0.25)
             else "INCONCLUSIVE_DEV")
    result = {
        "experiment": "E018", "evidence_class": "DEVELOPMENT", "gate_level_claimable": "none",
        "frozen_plan_commit": "c980ba7", "run_head_commit": head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"perm": SEED_PERM, "bootstrap": SEED_BOOT}, "n_permutations": NPERM,
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()},
        "population": {"n_tokens": len(toks), "n_bio_B": len(sub["bio_B"]), "n_other_B": len(sub["other_B"]), "n_A": len(sub["A"]), "n_currier_B": len(B)},
        "H003a": {"enrichment": stats, "biological_minus_otherB": float(stats["bio_B"]["R"] - stats["other_B"]["R"]), "decision": dec_a},
        "H003b": {"delta_S_B": {"mean": mS, "ci_lower": loS, "ci_upper": hiS}, "delta_Sy_B": {"mean": mSy, "ci_lower": loSy, "ci_upper": hiSy},
                  "share": share, "bits_per_token": {"M0": float(p0.mean()), "M_S": float(pS.mean()), "M_Sy": float(pSy.mean())}, "decision": dec_b},
        "claim_ceiling": "Structural transition statistics; no meaning claims.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"H003a": {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in stats.items()}, "dec_a": dec_a,
                      "H003b": {"dS": round(mS, 4), "dSy": round(mSy, 4), "ci": [round(loSy, 4), round(hiSy, 4)], "share": round(share, 3)}, "dec_b": dec_b}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
