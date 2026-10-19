"""E011 — slot-targeted conditioning under a backoff scorecard (FIRST RUN, development-stage).

Implements experiments/E011_targeted_context_scorecard/PLAN.md. Computes the
feature-permuted null models and the margins FIRST, then the primary contrasts,
and writes results.json BEFORE any interpretation. No scientific parameter here
may be changed.

Run:  python experiments/E011_targeted_context_scorecard/run.py
"""
from __future__ import annotations

import hashlib
import json
import math
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
from voynichlab.mdl import BackoffKTCoder, charcost  # noqa: E402
from voynichlab.p70 import parse_p70, PREFIXES, GALLOWS, SUFFIXES  # noqa: E402
from voynichlab.gate import bootstrap_mean_ci  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"

# ---- frozen constants (PLAN.md) ----
SEED = 20261019
N_FOLDS = 5
FLOOR = 0.05
BOOT = 10000
MODELS = {  # slot index -> tuple of feature names
    "M0": {},
    "M_S": {0: ("S",)},
    "M_L": {0: ("L",), 3: ("L",)},
    "M_SL": {0: ("S", "L"), 3: ("L",)},
    "M_Sfam": {0: ("Sfam",)},
    "M_Sall": {0: ("S",), 1: ("S",), 2: ("S",), 3: ("S",)},
}
PRIMARY = {"H014": ("M_S", "S"), "H015": ("M_L", "L")}
SECONDARY = [("M_SL", "M0"), ("M_Sfam", "M0"), ("M_SL", "M_S"), ("M_SL", "M_L"), ("M_Sall", "M0")]
MAJOR_SECTIONS = ("B", "H", "P", "S")
TOKLEN_BINS = (("<=4", 0, 4), ("5-6", 5, 6), (">=7", 7, 10**9))


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def efold(folio: str) -> int:
    return int(hashlib.sha256(("E007:" + folio.lower()).encode("utf-8")).hexdigest(), 16) % N_FOLDS


def elias_gamma(k: int) -> int:
    return 2 * int(math.floor(math.log2(k))) + 1


# --------------------------------------------------------------------------- #
# population with features
# --------------------------------------------------------------------------- #
class Tok:
    __slots__ = ("value", "slots", "folio", "language", "section", "fold", "feat")

    def __init__(self, value, folio, language, section, feat):
        self.value = value
        self.slots = parse_p70(value)
        self.folio = folio
        self.language = language
        self.section = section
        self.fold = efold(folio)
        self.feat = feat  # dict feature name -> value


def load_population(by_folio_lines=None):
    """Returns (tokens in frozen order, lines_by_folio) — lines are [[value, uncertain], ...]."""
    if by_folio_lines is None:
        by_folio_lines = defaultdict(list)
        for rec in parse_ivtff(DATA):
            if not is_running_text(rec.locator):
                continue
            full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
            if any(not u for _, u in full):
                by_folio_lines[rec.folio].append((rec.meta.language, rec.meta.illustration, full))
    toks = []
    for folio in sorted(by_folio_lines):
        for lang, sec, full in by_folio_lines[folio]:
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                if i == 0:
                    S = Sfam = "BOL"
                elif full[i - 1][1]:
                    S = Sfam = "UNC"
                else:
                    S = full[i - 1][0][-1]
                    Sfam = parse_p70(full[i - 1][0])[3] or "∅"
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                toks.append(Tok(v, folio, lang, sec, {"S": S, "L": L, "Sfam": Sfam}))
    return toks, by_folio_lines


def permute_features(toks, names, seed):
    """Within-folio permutation of the named features among the population tokens (PLAN §4)."""
    rng = np.random.default_rng(seed)
    by_folio = defaultdict(list)
    for t in toks:
        by_folio[t.folio].append(t)
    out = {}
    for folio in sorted(by_folio):
        group = by_folio[folio]
        for name in names:
            perm = rng.permutation(len(group))
            vals = [group[j].feat[name] for j in perm]
            for t, v in zip(group, vals):
                out.setdefault(id(t), {})[name] = v
    return out  # id(tok) -> {name: permuted value}


def shuffled_text(by_folio_lines, seed):
    """Within-folio permutation of the population TOKENS (control text for the claim record)."""
    rng = np.random.default_rng(seed)
    out = {}
    for folio in sorted(by_folio_lines):
        lines = [(lang, sec, [[v, u] for v, u in full]) for lang, sec, full in by_folio_lines[folio]]
        pos = [(ln, i) for ln in lines for i, (_, u) in enumerate(ln[2]) if not u]
        vals = [ln[2][i][0] for ln, i in pos]
        perm = rng.permutation(len(vals))
        for (ln, i), j in zip(pos, perm):
            ln[2][i][0] = vals[j]
        out[folio] = lines
    return out


# --------------------------------------------------------------------------- #
# coding
# --------------------------------------------------------------------------- #
def keys(tok, i, spec, override=None):
    parent = ("b", i, tok.slots[:i])
    feats = spec.get(i)
    if not feats:
        return None, parent
    fv = tuple((override or {}).get(name, tok.feat[name]) if override else tok.feat[name] for name in feats)
    return ("c", i, tok.slots[:i], fv), parent


def crossfit(toks, spec, sigma, overrides=None):
    """Out-of-fold bits per token (5-fold by efold)."""
    per = np.empty(len(toks))
    for j in range(N_FOLDS):
        coder = BackoffKTCoder(sigma)
        for t in toks:
            if t.fold != j:
                ov = overrides.get(id(t)) if overrides else None
                for i, v in enumerate(t.slots):
                    ck, pk = keys(t, i, spec, ov)
                    coder.update(ck, pk, v)
        for k, t in enumerate(toks):
            if t.fold == j:
                ov = overrides.get(id(t)) if overrides else None
                per[k] = sum(coder.cost(*keys(t, i, spec, ov), v) for i, v in enumerate(t.slots))
    return per


def model_bits(spec, sigma):
    inv = sum(charcost(s, sigma) for s in list(PREFIXES) + list(GALLOWS) + list(SUFFIXES))
    return {"mechanism_code_bits": inv + elias_gamma(1 + len(spec)), "dictionary_bits": 0, "key_bits": 0,
            "exception_bits": 0, "residual_bits": 0, "transmission_bits": 0}


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def folio_table(toks, per):
    bits, n = defaultdict(float), defaultdict(int)
    for t, b in zip(toks, per):
        bits[t.folio] += b
        n[t.folio] += 1
    return bits, n


def contrast(toks, per_a, per_b, lang_of):
    """A − B in bits/token per folio (positive = A better). Returns dict."""
    ba, n = folio_table(toks, per_a)
    bb, _ = folio_table(toks, per_b)
    folios = sorted(n)
    d = np.array([(bb[f] - ba[f]) / n[f] for f in folios])
    mean, lo, hi = bootstrap_mean_ci(d, BOOT, SEED, 0.025)
    sub = {}
    for L in ("A", "B"):
        ix = [i for i, f in enumerate(folios) if lang_of[f] == L]
        sub[L] = float(d[ix].mean()) if ix else None
    wins = int((d > 0).sum())
    return {"mean": mean, "ci_lower": lo, "ci_upper": hi, "n_folios": len(folios), "folio_wins": wins,
            "currier": sub, "per_folio": {f: float(x) for f, x in zip(folios, d)}}


def decide(real, null, margin):
    if real["mean"] >= margin and real["ci_lower"] > 0 and (real["mean"] - null["mean"]) >= margin \
            and real["currier"]["A"] > 0 and real["currier"]["B"] > 0:
        return "SUPPORTED_DEV"
    if real["ci_upper"] < margin:
        return "FALSIFIED_DEV"
    return "INCONCLUSIVE_DEV"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    raw = DATA.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"source identity mismatch: {blob}")
    toks, lines = load_population()
    N = len(toks)
    sigma = len({c for t in toks for c in t.value})
    lang_of = {t.folio: t.language for t in toks}
    for t in toks:
        assert "".join(t.slots) == t.value
    text_sha = hashlib.sha256("\n".join(t.value for t in toks).encode()).hexdigest()

    per = {m: crossfit(toks, spec, sigma) for m, spec in MODELS.items()}

    # ---- margins FIRST: feature-permuted null models vs M0 ----
    overrides = permute_features(toks, ("S", "L"), SEED)
    null_contr, margins = {}, {}
    for h, (m, feat) in PRIMARY.items():
        per_null = crossfit(toks, MODELS[m], sigma, overrides)
        null_contr[h] = contrast(toks, per_null, per["M0"], lang_of)
        # q97.5 of the bootstrap distribution of the null mean (same resampling as the CI)
        margins[h] = max(FLOOR, null_contr[h]["ci_upper"])
    print("margins (computed before real contrasts):", margins)

    # ---- primary contrasts ----
    real_contr, decisions = {}, {}
    for h, (m, feat) in PRIMARY.items():
        real_contr[h] = contrast(toks, per[m], per["M0"], lang_of)
        decisions[h] = decide(real_contr[h], null_contr[h], margins[h])

    secondary = {f"{a}-{b}": contrast(toks, per[a], per[b], lang_of) for a, b in SECONDARY}

    # ---- descriptive ----
    bpt = {m: float(per[m].mean()) for m in MODELS}
    idx_sec = defaultdict(list)
    idx_len = defaultdict(list)
    for k, t in enumerate(toks):
        idx_sec[t.section].append(k)
        for name, lo, hi in TOKLEN_BINS:
            if lo <= len(t.value) <= hi:
                idx_len[name].append(k)
    desc = {"bits_per_token_out_of_fold": bpt,
            "per_fold_bits_per_token": {m: [float(per[m][[t.fold == j for t in toks]].mean()) for j in range(N_FOLDS)] for m in MODELS},
            "section_delta_M_S": {s: float((per["M0"][idx_sec[s]] - per["M_S"][idx_sec[s]]).mean()) for s in MAJOR_SECTIONS},
            "section_delta_M_L": {s: float((per["M0"][idx_sec[s]] - per["M_L"][idx_sec[s]]).mean()) for s in MAJOR_SECTIONS},
            "toklen_delta_M_S": {b: float((per["M0"][idx_len[b]] - per["M_S"][idx_len[b]]).mean()) for b in idx_len},
            "toklen_delta_M_L": {b: float((per["M0"][idx_len[b]] - per["M_L"][idx_len[b]]).mean()) for b in idx_len},
            "feature_shares": {"S": dict(Counter("BOL" if t.feat["S"] == "BOL" else "UNC" if t.feat["S"] == "UNC" else "glyph" for t in toks)),
                               "L": dict(Counter(t.feat["L"] for t in toks))}}

    # ---- control text for the claim record: within-folio token permutation ----
    ctoks, _ = load_population(shuffled_text(lines, SEED))
    assert [t.folio for t in ctoks] == [t.folio for t in toks]
    ctrl = {m: float(crossfit(ctoks, MODELS[m], sigma).mean()) for m in ("M0", "M_S", "M_L")}

    mb = {m: model_bits(spec, sigma) for m, spec in MODELS.items()}
    result = {
        "experiment": "E011", "evidence_class": "DEVELOPMENT_CROSSFIT", "gate_level_claimable": "none",
        "source_identity": {"path": "data/raw/ZL3b-n.txt", "git_blob_sha1": blob, "sha256": hashlib.sha256(raw).hexdigest()},
        "frozen_plan_commit": "24dc8c7", "run_head_commit": head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__}, "seed": SEED,
        "population": {"n_tokens": N, "n_folios": len(lang_of), "sigma_size": sigma, "text_sha256": text_sha},
        "models": {m: {"conditioned_slots": {str(k): list(v) for k, v in spec.items()}, "model_bits": mb[m]} for m, spec in MODELS.items()},
        "margins": {h: {"margin": margins[h], "floor": FLOOR, "null_mean": null_contr[h]["mean"],
                        "null_ci_upper": null_contr[h]["ci_upper"], "rule": "max(floor, q97.5 of feature-permuted null mean)"} for h in PRIMARY},
        "null_contrasts": {h: {k: v for k, v in null_contr[h].items() if k != "per_folio"} for h in PRIMARY},
        "primary_contrasts": {h: {k: v for k, v in real_contr[h].items() if k != "per_folio"} for h in PRIMARY},
        "per_folio_delta": {h: real_contr[h]["per_folio"] for h in PRIMARY},
        "decisions": decisions,
        "secondary_contrasts": {k: {kk: vv for kk, vv in v.items() if kk != "per_folio"} for k, v in secondary.items()},
        "descriptive": desc,
        "control_within_folio_token_permutation_bits_per_token": ctrl,
        "claim_ceiling": "Development-stage structural statement; no Gate v2 level; registers the strongest structural null.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    # ---- Gate v2 claim record for M_S (pipeline exercise; expected: no gate level) ----
    bits_s, n_f = folio_table(toks, per["M_S"])
    bits_0, _ = folio_table(toks, per["M0"])
    mb0 = sum(mb["M0"].values())
    exp_json = json.loads((EXP_DIR / "experiment.json").read_text(encoding="utf-8"))
    claim = {
        "claim_id": "E011_M_S_development_stage", "registered_utc": exp_json.get("registered_utc", "2026-10-19T23:50:00Z"),
        "freeze_commit": "24dc8c7", "lockbox_id": "DEVELOPMENT_POOL_RUNNING_V1",
        "retraction_condition": exp_json["retraction_conditions"]["H014"], "post_reveal_changes": False,
        "sha256": exp_json["sha256"],
        "compression": {
            "folios": [{"folio": f, "n_tokens": n_f[f], "candidate_data_bits": bits_s[f], "null_total_bits": bits_0[f] + mb0 * n_f[f] / N} for f in sorted(n_f)],
            "candidate_model_bits": mb["M_S"], "reconstruction_sha256": text_sha, "lockbox_text_sha256": text_sha,
            "margin": {"bits_per_token": margins["H014"], "calibration_source": "development",
                       "justification": "max(0.05, q97.5 of the within-folio feature-permuted null model's gain over M0) on the development pool"},
            "controls": {"folio_internal_permutation": {"candidate_total_bits_per_token": ctrl["M_S"] + sum(mb["M_S"].values()) / N,
                                                        "null_total_bits_per_token": ctrl["M0"] + mb0 / N}},
        },
    }
    (EXP_DIR / "claim_E011_M_S.json").write_text(json.dumps(claim, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"decisions": decisions, "primary": {h: {k: round(v, 4) for k, v in real_contr[h].items() if k in ("mean", "ci_lower", "ci_upper")} for h in PRIMARY},
                      "bpt": {m: round(v, 3) for m, v in bpt.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
