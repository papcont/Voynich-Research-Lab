"""E012 stage B-open — reference-text signature comparison (FIRST RUN).

Implements experiments/E012_reference_signature/PLAN.md: open-rights texts from the pinned
cipher_benchmark clone, frozen normalization / units / line re-segmentation / size matching,
substitution controls, Voynich and G4, all scored with voynichlab.signature under the A3
slot base (Signature-G). Prepared texts are saved to runs/E012/ (git-ignored) for the
validator. results.json first.

Run:  python experiments/E012_reference_signature/run.py
"""
from __future__ import annotations

import glob
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from voynichlab.ivtff import parse_ivtff, tokenize_surface  # noqa: E402
from voynichlab.loci import is_running_text  # noqa: E402
from voynichlab import signature as SG  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runs" / "E012"
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
CB = Path("/home/user/matthewdgreen/cipher_benchmark/benchmark/sources")
TEXTS = {"N_DEU": ("copiale", "de"), "N_ITA": ("it_ss_synth", "it"), "N_ENG": ("en_ss_synth", "en"),
         "N_DE2": ("de_ss_synth", "de"), "N_FRA": ("fr_ss_synth", "fr")}
N_MATCH = 3660
SEED_RESEG, SEED_SUB = 20261080, 20261081
BITS, FRACS = ("delta_S", "delta_L", "delta_C"), ("TTR", "H1", "F_excess", "dJ_order")
TOL = {"bits": (0.05, 0.10), "fractions": (0.02, 0.05)}
COMPS = BITS + FRACS


def head_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# texts
# --------------------------------------------------------------------------- #
def norm_token(t: str) -> str:
    return "".join(c for c in t.lower() if c.isalpha())


def voynich_lines():
    lines, order = defaultdict(list), []
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if any(not u for _, u in full):
            if rec.folio not in lines:
                order.append(rec.folio)
            lines[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    return dict(lines), sorted(lines)


def zl3b_line_lengths(lines):
    return [sum(1 for _v, u in full if not u) for f in lines for _l, _s, full in lines[f] if any(not u for _v, u in full)]


def reference_lines(src, lang, line_lengths, rng):
    """Units = files in name order; lines = file lines if median tokens/line <= 20 else re-segmented."""
    files = sorted(glob.glob(str(CB / src / "plaintext" / "*.txt")))
    raw = {Path(f).stem: [[norm_token(t) for t in ln.split()] for ln in open(f, encoding="utf-8", errors="replace").read().split("\n")] for f in files}
    raw = {u: [[t for t in ln if t] for ln in lns] for u, lns in raw.items()}
    raw = {u: [ln for ln in lns if ln] for u, lns in raw.items()}
    tpl = [len(ln) for lns in raw.values() for ln in lns]
    reseg = bool(np.median(tpl) > 20)
    out, order = {}, []
    for u in sorted(raw):
        toks = [t for ln in raw[u] for t in ln]
        if not toks:
            continue
        if reseg:
            new, i = [], 0
            while i < len(toks):
                n = int(line_lengths[rng.integers(len(line_lengths))])
                new.append(toks[i:i + n]); i += n
            lns = new
        else:
            lns = raw[u]
        out[u] = [(lang, "all", [[t, False] for t in ln]) for ln in lns]
        order.append(u)
    return out, order, reseg


def truncate(lines, order, n):
    out, new_order, k = {}, [], 0
    for u in order:
        if k >= n:
            break
        kept = []
        for lang, sec, full in lines[u]:
            if k >= n:
                break
            room = n - k
            cert = [v for v, uu in full if not uu]
            if len(cert) <= room:
                kept.append((lang, sec, full)); k += len(cert)
            else:
                part, c = [], 0
                for v, uu in full:
                    if not uu:
                        if c >= room:
                            break
                        c += 1
                    part.append([v, uu])
                kept.append((lang, sec, part)); k += c
        if kept:
            out[u] = kept; new_order.append(u)
    return out, new_order


def substitute(lines, rng):
    alphabet = sorted({c for u in lines for _l, _s, full in lines[u] for v, _uu in full for c in v})
    perm = dict(zip(alphabet, [alphabet[i] for i in rng.permutation(len(alphabet))]))
    return {u: [(l, s, [["".join(perm[c] for c in v), uu] for v, uu in full]) for l, s, full in lines[u]] for u in lines}


def score(lines, order):
    sig = SG.signature(lines, slot_fn=SG.a3_slots, folio_order=order)
    return {k: float(sig[k]) for k in COMPS} | {"n_tokens": sig["n_tokens"], "n_units": sig["n_folios"]}


def distance(a, v):
    d = {X: abs(a[X] - v[X]) for X in COMPS}
    if all(d[X] <= TOL["bits"][0] for X in BITS) and all(d[X] <= TOL["fractions"][0] for X in FRACS):
        state = "MATCH"
    elif any(d[X] > TOL["bits"][1] for X in BITS) or any(d[X] > TOL["fractions"][1] for X in FRACS):
        state = "MISMATCH"
    else:
        state = "PARTIAL"
    norm = sum(d[X] / TOL["bits"][0] for X in BITS) + sum(d[X] / TOL["fractions"][0] for X in FRACS)
    return state, d, norm


def main() -> int:
    raw = DATA.read_bytes()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vlines, vorder = voynich_lines()
    ll = zl3b_line_lengths(vlines)
    rng = np.random.default_rng(SEED_RESEG)
    texts, orders, meta = {"V": vlines}, {"V": vorder}, {"V": {"resegmented": False}}
    for tid, (src, lang) in TEXTS.items():
        texts[tid], orders[tid], reseg = reference_lines(src, lang, ll, rng)
        meta[tid] = {"source": src, "resegmented": reseg, "n_units": len(orders[tid])}
    rs = np.random.default_rng(SEED_SUB)
    for tid in ("N_DEU", "N_ITA"):
        texts["C_SUB_" + tid[2:]] = substitute(texts[tid], rs); orders["C_SUB_" + tid[2:]] = orders[tid]
        meta["C_SUB_" + tid[2:]] = {"source": tid, "substitution": "letter permutation"}
    g4 = ROOT / "runs" / "E014" / "G4_EDGE_20261030.json"
    if g4.is_file():
        g = json.loads(g4.read_text(encoding="utf-8"))
        texts["G4"] = {f: [(l, s, full) for l, s, full in g[f]] for f in g}; orders["G4"] = sorted(texts["G4"])
        meta["G4"] = {"source": "runs/E014/G4_EDGE_20261030.json"}
    else:
        meta["G4"] = {"missing": True}

    results = {"size_matched": {}, "full": {}}
    for tid in texts:
        tl, to = truncate(texts[tid], orders[tid], N_MATCH)
        (OUT_DIR / f"{tid}_matched.json").write_text(json.dumps({"order": to, "lines": {u: [[l, s, full] for l, s, full in tl[u]] for u in tl}}), encoding="utf-8")
        results["size_matched"][tid] = score(tl, to)
        print("matched", tid, {k: round(v, 4) for k, v in results["size_matched"][tid].items() if k in COMPS})
    for tid in texts:
        (OUT_DIR / f"{tid}_full.json").write_text(json.dumps({"order": orders[tid], "lines": {u: [[l, s, full] for l, s, full in texts[tid][u]] for u in texts[tid]}}), encoding="utf-8")
        results["full"][tid] = score(texts[tid], orders[tid])
        print("full", tid, {k: round(v, 4) for k, v in results["full"][tid].items() if k in COMPS})

    decisions, dists = {}, {}
    V = results["size_matched"]["V"]
    for tid, sig in results["size_matched"].items():
        if tid == "V":
            continue
        state, d, norm = distance(sig, V)
        decisions[tid] = state; dists[tid] = {"abs_diff": d, "normalised_L1": norm}
    nat = [t for t in decisions if t.startswith("N_")]
    h27 = "SUPPORTED" if any(decisions[t] == "MATCH" for t in nat) else "FALSIFIED" if all(decisions[t] == "MISMATCH" for t in nat) else "PARTIAL"
    inv = {}
    for tid in ("DEU", "ITA"):
        a, b = results["size_matched"]["N_" + tid], results["size_matched"]["C_SUB_" + tid]
        inv[tid] = max(abs(a[X] - b[X]) for X in COMPS)
    h28 = "SUPPORTED" if all(v < 1e-9 for v in inv.values()) else "FALSIFIED"
    nearest = min(dists, key=lambda t: dists[t]["normalised_L1"])
    out = {"experiment": "E012", "stage": "B-open", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "72f62d7", "run_head_commit": head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__},
           "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest()}, "text_meta": meta, "size_match_tokens": N_MATCH,
           "signature": "Signature-G (A3 slots) via voynichlab.signature", "results": results, "distances_to_V_size_matched": dists,
           "decisions": decisions, "substitution_invariance_max_abs_diff": inv,
           "hypothesis_outcomes": {"H027": h27, "H028": h28}, "nearest_text_to_V": nearest,
           "claim_ceiling": "Signature similarity between texts; no decipherment, no language identification, no Gate level."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decisions": decisions, "H027": h27, "H028": h28, "nearest": nearest,
                      "V_matched": {k: round(V[k], 4) for k in COMPS}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
