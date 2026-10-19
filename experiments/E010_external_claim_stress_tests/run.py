"""E010 — epilectrik Currier-B claims as external structural competitor (FIRST RUN).

Implements PLAN.md + PREFLIGHT_AMENDMENT_001.md: R1 reproduction of upstream's
boundary glyph coupling; R2 development-stage contrasts under the E011 backoff
scorecard on Currier B. Null margins are computed before the real contrasts.
Writes results.json BEFORE any interpretation.

Run:  python experiments/E010_external_claim_stress_tests/run.py
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import re
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
TABLE = ROOT / ".external" / "epilectrik_voynich" / "results" / "phase20a_operator_equivalence.json"
TABLE_SHA = "ccc0ea339badc1dfdb3caa3b5962421dbb84be22ccec07e2bc7f701fdb5395fe"
PAIRS_SHA = "338892c0068ed28fdf41d7c105da7b617e85672ec5522fc5a9416f528123b1b1"

SEED_R1_ALL, SEED_R1_DEF, SEED_NULL, SEED_BOOT = 20261020, 20261021, 20261020, 20261019
NPERM, N_FOLDS, FLOOR, BOOT = 1000, 5, 0.05, 10000
UNIT_RE = re.compile(r"c[tkpf]h|[cs]h|i+[nrlm]|.")
PUBLISHED = {"C_all": 0.256, "C_def": 0.215, "coverage": 0.695}
MODELS = {  # (class_stage, prefix features)
    "M_S": (None, ("S",)), "M_Sfam": (None, ("Sfam",)), "M_Sunit": (None, ("Sunit",)), "M_S2unit": (None, ("S2unit",)),
    "M_class": ("plain", ("cls",)), "M_classprev": ("prev", ("cls",)),
}
CONTRASTS = {"H016": ("M_Sunit", "M_S", "Sunit"), "H017": ("M_S2unit", "M_Sunit", "S2unit"), "H018": ("M_classprev", "M_Sfam", "cls")}
SECONDARY = [("M_class", "M_Sfam"), ("M_classprev", "M_class")]


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def head_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT)).decode().strip()
    except Exception:
        return "unknown"


def efold(folio):
    return int(hashlib.sha256(("E007:" + folio.lower()).encode()).hexdigest(), 16) % N_FOLDS


def elias_gamma(k):
    return 2 * int(math.floor(math.log2(k))) + 1


def units(tok):
    return UNIT_RE.findall(tok)


# --------------------------------------------------------------------------- #
# class table (fixed external input)
# --------------------------------------------------------------------------- #
def load_table():
    raw = TABLE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != TABLE_SHA:
        raise SystemExit("class table hash mismatch")
    d = json.loads(raw)
    pairs = sorted((c["class_id"], t) for c in d["classes"] for t in c["members"])
    if hashlib.sha256(json.dumps(pairs).encode()).hexdigest() != PAIRS_SHA:
        raise SystemExit("class pair-list hash mismatch")
    table = {t: str(c) for c, t in pairs}
    mean_len = sum(len(t) for t in table) / len(table)
    return table, mean_len


# --------------------------------------------------------------------------- #
# population
# --------------------------------------------------------------------------- #
class Tok:
    __slots__ = ("value", "slots", "folio", "language", "section", "fold", "feat")

    def __init__(self, value, folio, language, section, feat):
        self.value, self.slots, self.folio, self.language, self.section = value, parse_p70(value), folio, language, section
        self.fold, self.feat = efold(folio), feat


def load(table):
    toks, boundaries = [], []  # boundaries: (language, last_unit_left, first_unit_right, sep)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [t for t in tokenize_surface(rec.raw_text) if t.value]
        n = len(full)
        for i, t in enumerate(full):
            if t.uncertain:
                continue
            if i == 0:
                S = Sf = Su = S2 = pc = "BOL"
            elif full[i - 1].uncertain:
                S = Sf = Su = S2 = pc = "UNC"
            else:
                pv = full[i - 1].value
                pu = units(pv)
                S, Sf, Su, S2 = pv[-1], (parse_p70(pv)[3] or "∅"), pu[-1], "".join(pu[-2:])
                pc = table.get(pv, "UN")
                boundaries.append((rec.meta.language, pu[-1], units(t.value)[0], t.separator_before))
            toks.append(Tok(t.value, rec.folio, rec.meta.language, rec.meta.illustration,
                            {"S": S, "Sfam": Sf, "Sunit": Su, "S2unit": S2, "cls": table.get(t.value, "UN"), "prevcls": pc}))
    toks.sort(key=lambda t: t.folio)  # stable: file order within folio
    return toks, boundaries


# --------------------------------------------------------------------------- #
# R1: boundary coupling (upstream definition)
# --------------------------------------------------------------------------- #
def mi(x, y, nx, ny):
    j = np.bincount(x * ny + y, minlength=nx * ny).astype(float).reshape(nx, ny)
    p = j / j.sum()
    px, py = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (px @ py)[nz])).sum())


def coupling(x, y, nx, ny, seed):
    rng = np.random.default_rng(seed)
    obs = mi(x, y, nx, ny)
    perm = np.array([mi(x, rng.permutation(y), nx, ny) for _ in range(NPERM)])
    return {"n": int(len(x)), "mi": obs, "perm_mean": float(perm.mean()), "C": obs - float(perm.mean()),
            "p": float((1 + (perm >= obs).sum()) / (1 + NPERM))}


def r1(boundaries):
    B = [b for b in boundaries if b[0] == "B"]
    lefts, rights = sorted({b[1] for b in B}), sorted({b[2] for b in B})
    li, ri = {u: i for i, u in enumerate(lefts)}, {u: i for i, u in enumerate(rights)}
    x = np.array([li[b[1]] for b in B]); y = np.array([ri[b[2]] for b in B])
    d = np.array([b[3] == "." for b in B])
    out = {"n_boundaries": len(B), "n_definite": int(d.sum()), "n_uncertain": int((~d).sum()),
           "C_all": coupling(x, y, len(lefts), len(rights), SEED_R1_ALL),
           "C_def": coupling(x[d], y[d], len(lefts), len(rights), SEED_R1_DEF), "published": PUBLISHED}
    da, dd = abs(out["C_all"]["C"] - PUBLISHED["C_all"]), abs(out["C_def"]["C"] - PUBLISHED["C_def"])
    out["decision"] = "REPRODUCED" if (da <= 0.03 and dd <= 0.03) else "REPRODUCTION_FAILURE" if (da > 0.06 or dd > 0.06) else "APPROXIMATE"
    return out


# --------------------------------------------------------------------------- #
# R2: coding
# --------------------------------------------------------------------------- #
def code_token(coder, model, t, ov, update):
    stage, pf = MODELS[model]
    f = lambda name: (ov or {}).get(name, t.feat[name])  # noqa: E731
    bits = 0.0
    if stage is not None:
        child = ("clsc", f("prevcls")) if stage == "prev" else None
        if update:
            coder.update(child, ("cls",), f("cls"))
        else:
            bits += coder.cost(child, ("cls",), f("cls"))
    for i, v in enumerate(t.slots):
        parent = ("b", i, t.slots[:i])
        child = ("c", i, t.slots[:i], tuple(f(n) for n in pf)) if i == 0 else None
        if update:
            coder.update(child, parent, v)
        else:
            bits += coder.cost(child, parent, v)
    return bits


def crossfit(toks, model, sigma, overrides=None):
    per = np.empty(len(toks))
    for j in range(N_FOLDS):
        coder = BackoffKTCoder(sigma)
        for t in toks:
            if t.fold != j:
                code_token(coder, model, t, overrides.get(id(t)) if overrides else None, True)
        for k, t in enumerate(toks):
            if t.fold == j:
                per[k] = code_token(coder, model, t, overrides.get(id(t)) if overrides else None, False)
    return per


def permute_features(toks, names, seed):
    rng = np.random.default_rng(seed)
    byf = defaultdict(list)
    for t in toks:
        byf[t.folio].append(t)
    out = {}
    for folio in sorted(byf):
        g = byf[folio]
        for name in names:
            perm = rng.permutation(len(g))
            vals = [g[j].feat[name] for j in perm]
            for t, v in zip(g, vals):
                out.setdefault(id(t), {})[name] = v
    return out


def derive_null_prevcls(toks, overrides):
    """prevcls° = permuted class of the previous same-line token (BOL/UNC preserved)."""
    prev_tok = None
    for t in toks:
        if t.feat["prevcls"] in ("BOL", "UNC") or prev_tok is None or prev_tok.folio != t.folio:
            overrides.setdefault(id(t), {})["prevcls"] = t.feat["prevcls"]
        else:
            overrides.setdefault(id(t), {})["prevcls"] = overrides.get(id(prev_tok), {}).get("cls", prev_tok.feat["cls"])
        prev_tok = t
    return overrides


def contrast(toks, pa, pb, sections):
    ba, bb, n = defaultdict(float), defaultdict(float), defaultdict(int)
    sec_of = {}
    for t, x, y in zip(toks, pa, pb):
        ba[t.folio] += x; bb[t.folio] += y; n[t.folio] += 1; sec_of[t.folio] = t.section
    fol = sorted(n)
    d = np.array([(bb[f] - ba[f]) / n[f] for f in fol])
    mean, lo, hi = bootstrap_mean_ci(d, BOOT, SEED_BOOT, 0.025)
    sub = {s: float(d[[i for i, f in enumerate(fol) if sec_of[f] == s]].mean()) for s in sections}
    return {"mean": mean, "ci_lower": lo, "ci_upper": hi, "n_folios": len(fol), "folio_wins": int((d > 0).sum()), "sections": sub}


def decide(real, null, margin, sections):
    if real["mean"] >= margin and real["ci_lower"] > 0 and real["mean"] - null["mean"] >= margin \
            and all(real["sections"][s] > 0 for s in sections):
        return "SUPPORTED_DEV"
    if real["ci_upper"] < margin:
        return "FALSIFIED_DEV"
    return "INCONCLUSIVE_DEV"


def main():
    raw = DATA.read_bytes()
    if git_blob_sha1(raw) != EXPECTED_BLOB:
        raise SystemExit("source identity mismatch")
    table, mean_len = load_table()
    toks_all, boundaries = load(table)
    sigma = len({c for t in toks_all for c in t.value})
    B = [t for t in toks_all if t.language == "B"]
    A = [t for t in toks_all if t.language == "A"]
    sec_counts = Counter(t.section for t in B)
    sections = [s for s, _ in sec_counts.most_common(2)]
    print("B tokens", len(B), "largest sections", sections, dict(sec_counts))

    res_r1 = r1(boundaries)
    print("R1", {k: round(res_r1[k]["C"], 4) for k in ("C_all", "C_def")}, res_r1["decision"])

    per = {m: crossfit(B, m, sigma) for m in MODELS}

    # ---- null margins FIRST ----
    ov = permute_features(B, ("S", "Sunit", "S2unit", "Sfam", "cls"), SEED_NULL)
    ov = derive_null_prevcls(B, ov)
    null, margins = {}, {}
    for h, (a, b, feat) in CONTRASTS.items():
        pa = crossfit(B, a, sigma, ov)
        null[h] = contrast(B, pa, per[b], sections)
        margins[h] = max(FLOOR, null[h]["ci_upper"])
    print("margins (before real contrasts):", margins)

    real, decisions = {}, {}
    for h, (a, b, feat) in CONTRASTS.items():
        real[h] = contrast(B, per[a], per[b], sections)
        decisions[h] = decide(real[h], null[h], margins[h], sections)
    secondary = {f"{a}-{b}": contrast(B, per[a], per[b], sections) for a, b in SECONDARY}

    # descriptive
    coverage = sum(1 for t in B if t.feat["cls"] != "UN") / len(B)
    perA = {m: float(crossfit(A, m, sigma).mean()) for m in ("M_S", "M_Sunit", "M_S2unit")}
    inv = sum(charcost(s, sigma) for s in list(PREFIXES) + list(GALLOWS) + list(SUFFIXES))
    table_bits = 480 * charcost("x" * int(round(mean_len)), sigma) + 480 * math.log2(49)

    result = {
        "experiment": "E010", "evidence_class": {"R1": "EXTERNAL_REPLICATION/REPRODUCTION", "R2": "DEVELOPMENT_CROSSFIT"},
        "gate_level_claimable": "none", "frozen_plan_commit": "7cf5430", "run_head_commit": head_commit(),
        "first_run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"R1_all": SEED_R1_ALL, "R1_def": SEED_R1_DEF, "null": SEED_NULL, "bootstrap": SEED_BOOT},
        "source_identity": {"zl3b_sha256": hashlib.sha256(raw).hexdigest(), "class_table_sha256": TABLE_SHA, "class_pairs_sha256": PAIRS_SHA},
        "population": {"n_B_tokens": len(B), "n_B_folios": len({t.folio for t in B}), "n_A_tokens": len(A), "sigma_size": sigma,
                       "B_sections": dict(sec_counts), "gate_sections": sections,
                       "class_coverage_B": coverage, "published_coverage_B_H_track": PUBLISHED["coverage"]},
        "R1_boundary_coupling": res_r1,
        "R2": {"bits_per_token_out_of_fold_B": {m: float(per[m].mean()) for m in MODELS},
               "model_bits": {m: inv + elias_gamma(2 if MODELS[m][0] else 1) + (table_bits if MODELS[m][0] else 0) for m in MODELS},
               "margins": {h: {"margin": margins[h], "null_mean": null[h]["mean"], "null_ci_upper": null[h]["ci_upper"]} for h in CONTRASTS},
               "null_contrasts": null, "primary_contrasts": real, "decisions": decisions, "secondary_contrasts": secondary,
               "currier_A_transfer_bits_per_token": perA},
        "claim_ceiling": "Structural, development-stage, Currier B; upstream interpretations not evaluated or adopted.",
    }
    (EXP_DIR / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"R1": res_r1["decision"], "decisions": decisions,
                      "primary": {h: {k: round(v, 4) for k, v in real[h].items() if k in ("mean", "ci_lower", "ci_upper")} for h in CONTRASTS},
                      "bpt": {m: round(float(per[m].mean()), 3) for m in MODELS}, "coverage_B": round(coverage, 4)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
