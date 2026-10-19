"""E019 — cipher/encoding transforms of open-rights prose under Signature-G (FIRST RUN).

Implements experiments/E019_cipher_transforms/PLAN.md. Text preparation and scoring are
imported from the frozen E012 runner; the transforms are defined here. Prepared texts go
to runs/E019/ (git-ignored). results.json first.

Run:  python experiments/E019_cipher_transforms/run.py
"""
from __future__ import annotations

import hashlib
import json
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
EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT / "runs" / "E019"
SEED = 20261090
SOURCES = {"N_DEU": ("copiale", "de"), "N_ITA": ("it_ss_synth", "it")}
TRANSFORMS = ("C_HOMO", "C_VERB", "C_STREAM", "C_STREAM_VERB")
VERB_ALPHABET = "0123456789"


def voynich_token_lengths(vlines):
    return [len(v) for f in vlines for _l, _s, full in vlines[f] for v, u in full if not u]


def letters(lines):
    return Counter(c for u in lines for _l, _s, full in lines[u] for v, _uu in full for c in v)


def homophonic(lines, rng):
    freq = letters(lines)
    mx = max(freq.values())
    table, symbol = {}, 0
    for c in sorted(freq):
        k = int(np.ceil(3 * freq[c] / mx))
        table[c] = [chr(0x3400 + symbol + i) for i in range(k)]  # fresh symbols (CJK ext-A block, letters for isalpha)
        symbol += k
    out = {}
    for u in lines:
        out[u] = [(l, s, [["".join(table[c][int(rng.integers(len(table[c])))] for c in v), uu] for v, uu in full]) for l, s, full in lines[u]]
    return out


def verbose(lines):
    freq = letters(lines)
    table = {}
    for i, c in enumerate(sorted(freq)):
        table[c] = VERB_ALPHABET[i // 10 % 10] + VERB_ALPHABET[i % 10]  # injective for <= 100 letters
    # the verbose symbols must count as "letters" for later normalization-free scoring: map digits to letters
    dmap = {d: chr(ord("A") + i) for i, d in enumerate(VERB_ALPHABET)}
    table = {c: "".join(dmap[d] for d in code) for c, code in table.items()}
    return {u: [(l, s, [["".join(table[c] for c in v), uu] for v, uu in full]) for l, s, full in lines[u]] for u in lines}


def stream_recut(lines, tok_lengths, rng):
    out = {}
    for u in lines:
        new = []
        for l, s, full in lines[u]:
            stream = "".join(v for v, uu in full if not uu)
            toks, i = [], 0
            while i < len(stream):
                n = int(tok_lengths[rng.integers(len(tok_lengths))])
                toks.append([stream[i:i + n], False]); i += n
            if toks:
                new.append((l, s, toks))
        out[u] = new
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vlines, vorder = E012.voynich_lines()
    ll = E012.zl3b_line_lengths(vlines)
    tl = voynich_token_lengths(vlines)
    e12 = json.loads((ROOT / "experiments" / "E012_reference_signature" / "results.json").read_text(encoding="utf-8"))
    V = e12["results"]["size_matched"]["V"]
    rng_reseg = np.random.default_rng(E012.SEED_RESEG)
    texts, orders = {}, {}
    for tid, (src, lang) in E012.TEXTS.items():  # same preparation sequence as E012 (rng state identical)
        lines, order, _ = E012.reference_lines(src, lang, ll, rng_reseg)
        if tid in SOURCES:
            texts[tid], orders[tid] = lines, order
    results, decisions, dists, meta = {}, {}, {}, {}
    k = 0
    for sid in SOURCES:
        base, order = texts[sid], orders[sid]
        made = {"C_HOMO": homophonic(base, np.random.default_rng(SEED + k)),
                "C_VERB": verbose(base),
                "C_STREAM": stream_recut(base, tl, np.random.default_rng(SEED + k + 1)),
                "C_STREAM_VERB": stream_recut(verbose(base), tl, np.random.default_rng(SEED + k + 2))}
        k += 3
        for tr, lines in made.items():
            tid = f"{tr}({sid})"
            m, mo = E012.truncate(lines, order, E012.N_MATCH)
            (OUT_DIR / f"{tid}.json").write_text(json.dumps({"order": mo, "lines": {u: [[l, s, full] for l, s, full in m[u]] for u in m}}), encoding="utf-8")
            sig = E012.score(m, mo)
            results[tid] = sig
            state, d, norm = E012.distance(sig, V)
            decisions[tid], dists[tid] = state, {"abs_diff": d, "normalised_L1": norm}
            meta[tid] = {"n_tokens_full": sum(1 for u in lines for _l, _s, full in lines[u] for _v, uu in full if not uu)}
            print(tid, state, {x: round(sig[x], 4) for x in E012.COMPS})
    s_vals = {sid: results[f"C_STREAM({sid})"]["delta_S"] for sid in SOURCES}
    near = any(abs(v - V["delta_S"]) <= 0.10 for v in s_vals.values())
    h29a = "SUPPORTED" if (all(v >= 0.05 for v in s_vals.values()) and near) else "FALSIFIED" if all(v < 0.05 for v in s_vals.values()) else "PARTIAL"
    h29b = "SUPPORTED" if any(v == "MATCH" for v in decisions.values()) else "FALSIFIED" if all(v == "MISMATCH" for v in decisions.values()) else "PARTIAL"
    out = {"experiment": "E019", "evidence_class": "MECHANISM_DEMONSTRATION/DEVELOPMENT", "gate_level_claimable": "none",
           "frozen_plan_commit": "290ecdc", "run_head_commit": E012.head_commit(),
           "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "software": {"python": platform.python_version(), "numpy": np.__version__}, "seed_base": SEED,
           "voynich_reference_E012_size_matched": V, "plaintext_reference_E012": {sid: e12["results"]["size_matched"][sid] for sid in SOURCES},
           "results_size_matched": results, "text_meta": meta, "distances_to_V": dists, "decisions": decisions,
           "C_STREAM_delta_S": s_vals, "hypothesis_outcomes": {"H029a": h29a, "H029b": h29b},
           "nearest_to_V": min(dists, key=lambda t: dists[t]["normalised_L1"]),
           "claim_ceiling": "Which encodings of prose reproduce which structural components; no decipherment; no Gate level."}
    (EXP_DIR / "results.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decisions": decisions, "H029a": h29a, "H029b": h29b, "C_STREAM_delta_S": {k: round(v, 4) for k, v in s_vals.items()},
                      "V_delta_S": round(V["delta_S"], 4), "nearest": out["nearest_to_V"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
