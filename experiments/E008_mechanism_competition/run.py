"""E008 stage A — common-scorecard mechanism tournament (FIRST REVEAL runner).

Implements experiments/E008_mechanism_competition/PLAN.md as clarified by
PREFLIGHT_AMENDMENT_001.md. Sixteen models = {B0 whole token, B1 P70 slots} x
subsets of {S edge state, L line position, C local copy/modify}; one KT
scorecard; development-trained frozen counts -> holdout bits/token; nulls N1
(within-folio shuffle) and N0 (within-line shuffle). Writes results.json BEFORE
any interpretation. No scientific parameter here may be changed.

Run:  python experiments/E008_mechanism_competition/run.py [--dev-only]
      --dev-only: losslessness checks + W selection on development folios only;
                  codes no holdout token and writes no results.json.
"""
from __future__ import annotations

import hashlib
import itertools
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
from voynichlab.mdl import KTCoder, charcost  # noqa: E402
from voynichlab.p70 import parse_p70, PREFIXES, GALLOWS, SUFFIXES  # noqa: E402

EXP_DIR = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw" / "ZL3b-n.txt"
EXPECTED_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"

# ---- frozen constants (PLAN.md / PREFLIGHT_AMENDMENT_001.md / experiment.json) ----
W_GRID = (5, 10, 20, 40)
W_MAX = 40
SEED_N1 = 20261019
SEED_N0 = 20261020
MARGIN = 0.05
STABILITY = 2 / 3
N_FOLDS = 5
DEV_FOLDS = (0, 1, 2)
HOLD_FOLDS = (3, 4)
COMPONENTS = ("S", "L", "C")
BASES = ("B0", "B1")
MAJOR_SECTIONS = ("B", "H", "P", "S")
TOKLEN_BINS = (("<=4", 0, 4), ("5-6", 5, 6), (">=7", 7, 10**9))
SPECS = [(b, frozenset(c)) for b in BASES
         for r in range(4) for c in itertools.combinations(COMPONENTS, r)]


def spec_name(spec):
    b, comps = spec
    return b + "".join("+" + c for c in COMPONENTS if c in comps)


# --------------------------------------------------------------------------- #
# provenance / helpers
# --------------------------------------------------------------------------- #
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


def natural_folio_key(folio: str):
    m = re.match(r"f(\d+)(.*)$", folio)
    return (int(m.group(1)), m.group(2)) if m else (10**9, folio)


def lev1(a: str, b: str) -> bool:
    """True iff Levenshtein distance is exactly 1."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    i = 0
    n = min(la, lb)
    while i < n and a[i] == b[i]:
        i += 1
    if la == lb:
        return a[i + 1:] == b[i + 1:]
    if la + 1 == lb:
        return a[i:] == b[i + 1:]
    return a[i + 1:] == b[i:]


def canonical_edit(src: str, t: str) -> str:
    """PLAN §6.3: substitution at the (unique) differing position; insertion /
    deletion at the SMALLEST position p that maps src onto t."""
    if len(src) == len(t):
        i = next(i for i in range(len(t)) if src[i] != t[i])
        return f"s{i}{t[i]}"
    if len(t) == len(src) + 1:
        p = next(p for p in range(len(t)) if src[:p] + t[p] + src[p:] == t)
        return f"i{p}{t[p]}"
    p = next(p for p in range(len(src)) if src[:p] + src[p + 1:] == t)
    return f"d{p}"


def apply_edit(src: str, e: str) -> str:
    op, rest = e[0], e[1:]
    if op == "d":
        p = int(rest)
        return src[:p] + src[p + 1:]
    p, c = int(rest[:-1]), rest[-1]
    if op == "s":
        return src[:p] + c + src[p + 1:]
    return src[:p] + c + src[p:]


# --------------------------------------------------------------------------- #
# corpus -> lines -> feature tokens
# --------------------------------------------------------------------------- #
class Line:
    __slots__ = ("folio", "language", "section", "hand", "fold", "full")

    def __init__(self, folio, language, section, hand, full):
        self.folio = folio
        self.language = language
        self.section = section
        self.hand = hand
        self.fold = efold(folio)
        self.full = full  # list of [value, uncertain]


class Tok:
    __slots__ = ("value", "folio", "language", "section", "hand", "fold", "S", "L",
                 "k_exact", "k_edit", "edit", "line_len")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def load_lines():
    by_folio = defaultdict(list)
    for rec in parse_ivtff(DATA):
        if not is_running_text(rec.locator):
            continue
        full = [[t.value, t.uncertain] for t in tokenize_surface(rec.raw_text) if t.value]
        if not any(not u for _, u in full):
            continue
        by_folio[rec.folio].append(Line(rec.folio, rec.meta.language, rec.meta.illustration,
                                        rec.meta.hand, full))
    return by_folio


def materialize(by_folio, folio_order):
    """Feature tokens in frozen order with S, L and copy-search results."""
    toks = []
    for folio in folio_order:
        window = []  # population tokens of this folio, oldest first
        for line in by_folio[folio]:
            full = line.full
            n = len(full)
            for i, (v, unc) in enumerate(full):
                if unc:
                    continue
                S = "BOL" if i == 0 else ("UNC" if full[i - 1][1] else full[i - 1][0][-1])
                L = "ONLY" if n == 1 else "FIRST" if i == 0 else "LAST" if i == n - 1 else "MID"
                k_exact = k_edit = None
                edit = None
                for k in range(1, min(W_MAX, len(window)) + 1):
                    w = window[-k]
                    if k_exact is None and w == v:
                        k_exact = k
                        break
                    if k_edit is None and lev1(w, v):
                        k_edit = k
                        edit = canonical_edit(w, v)
                if k_exact is not None and k_edit is not None and k_edit > k_exact:
                    k_edit, edit = None, None
                toks.append(Tok(value=v, folio=folio, language=line.language, section=line.section,
                                hand=line.hand, fold=line.fold, S=S, L=L, k_exact=k_exact,
                                k_edit=k_edit, edit=edit, line_len=n))
                window.append(v)
    return toks


def shuffled_copy(by_folio, folio_order, seed, per_line):
    rng = np.random.default_rng(seed)
    out = {}
    for folio in folio_order:
        new_lines = []
        for line in by_folio[folio]:
            new_lines.append(Line(line.folio, line.language, line.section, line.hand,
                                  [[v, u] for v, u in line.full]))
        groups = [[ln] for ln in new_lines] if per_line else [new_lines]
        for grp in groups:
            pos = [(ln, i) for ln in grp for i, (_, u) in enumerate(ln.full) if not u]
            vals = [ln.full[i][0] for ln, i in pos]
            perm = rng.permutation(len(vals))
            for (ln, i), j in zip(pos, perm):
                ln.full[i][0] = vals[j]
        out[folio] = new_lines
    return out


# --------------------------------------------------------------------------- #
# models and coding
# --------------------------------------------------------------------------- #
def src_slot(tok, W):
    if tok.k_exact is not None and tok.k_exact <= W:
        return f"{tok.k_exact}:0", 0
    if tok.k_edit is not None and tok.k_edit <= W:
        return f"{tok.k_edit}:1", 1
    return "NONE", None


class Model:
    def __init__(self, spec, W, sigma, parse_cache):
        self.base, self.comps = spec
        self.W = W
        self.coder = KTCoder(sigma)
        self.cache = parse_cache

    def base_slots(self, v):
        if self.base == "B0":
            return (v,)
        s = self.cache.get(v)
        if s is None:
            s = self.cache[v] = parse_p70(v)
        return s

    def code(self, tok, update):
        c = self.coder
        step = c.encode if update else c.cost
        bits = 0.0
        slots = self.base_slots(tok.value)
        S = tok.S if "S" in self.comps else None
        L = tok.L if "L" in self.comps else None
        if "C" in self.comps:
            val, d = src_slot(tok, self.W)
            bits += step(("src",), val)
            if d is not None:
                if d == 1:
                    bits += step(("edit",), tok.edit)
                if update:  # base counts are updated on every token (PLAN §6.3)
                    for i, v in enumerate(slots):
                        c.update(("base", i, slots[:i], S, L), v)
                return bits
        for i, v in enumerate(slots):
            bits += step(("base", i, slots[:i], S, L), v)
        return bits


def model_bits(spec, W_index, sigma):
    base, comps = spec
    bits = 0.0
    if base == "B1":
        bits += sum(charcost(s, sigma) for s in list(PREFIXES) + list(GALLOWS) + list(SUFFIXES))
    bits += elias_gamma(1 + len(comps))
    if "C" in comps:
        bits += elias_gamma(W_index + 1) + 2
    return bits


def dev_holdout(spec, W, sigma, cache, dev, hold):
    """Prequential over development (counts updated), then frozen coding of holdout."""
    m = Model(spec, W, sigma, cache)
    dev_bits = 0.0
    for t in dev:
        dev_bits += m.code(t, True)
    hold_bits = np.fromiter((m.code(t, False) for t in hold), dtype=float, count=len(hold))
    return dev_bits, hold_bits


def check_lossless(toks, W):
    """Every model path must reconstruct the token (constructive sanity)."""
    windows = defaultdict(list)
    for t in toks:
        win = windows[t.folio]
        assert "".join(parse_p70(t.value)) == t.value
        val, d = src_slot(t, W)
        if d == 0:
            assert win[-int(val.split(":")[0])] == t.value
        elif d == 1:
            assert apply_edit(win[-int(val.split(":")[0])], t.edit) == t.value, (t.value, t.edit)
        win.append(t.value)
    return True


# --------------------------------------------------------------------------- #
# scoring helpers
# --------------------------------------------------------------------------- #
def contrasts(hold_bits, hold, base, idx_sets):
    """Per-component gains on one base; idx_sets: name -> index array for subsets."""
    def bpt(spec, ix=None):
        arr = hold_bits[spec]
        return float(arr.mean() if ix is None else arr[ix].mean())
    full = (base, frozenset(COMPONENTS))
    out = {}
    for X in COMPONENTS:
        alone = (base, frozenset([X]))
        reduced = (base, frozenset(c for c in COMPONENTS if c != X))
        dm = bpt((base, frozenset())) - bpt(alone)
        du = bpt(reduced) - bpt(full)
        # folio stability
        folios = sorted({t.folio for t in hold})
        wins = 0
        for f in folios:
            ix = idx_sets["folio:" + f]
            if hold_bits[full][ix].mean() < hold_bits[reduced][ix].mean():
                wins += 1
        sub = {name: bpt(reduced, ix) - bpt(full, ix) for name, ix in idx_sets.items()
               if not name.startswith("folio:")}
        out[X] = {"marginal_gain": dm, "unique_gain": du,
                  "folio_wins": wins, "n_folios": len(folios), "folio_stability": wins / len(folios),
                  "unique_gain_subsets": sub}
    return out


def verdicts(real, null):
    out = {}
    for X in COMPONENTS:
        r = real[X]
        crit = {
            "1_marginal_ge_0.05": r["marginal_gain"] >= MARGIN,
            "2_unique_ge_0.05": r["unique_gain"] >= MARGIN,
            "3_folio_stability_ge_2/3": r["folio_stability"] >= STABILITY,
            "4_currier_A_and_B_positive": r["unique_gain_subsets"]["currier:A"] > 0
            and r["unique_gain_subsets"]["currier:B"] > 0,
            "5_exceeds_N1_by_0.05": r["unique_gain"] - null[X]["unique_gain"] >= MARGIN,
        }
        if all(crit.values()):
            v = "INFORMATIVE"
        elif r["marginal_gain"] < MARGIN and r["unique_gain"] < MARGIN:
            v = "NOT_INFORMATIVE"
        else:
            v = "MIXED"
        out[X] = {"verdict": v, "criteria": crit, "unique_gain_N1": null[X]["unique_gain"]}
    return out


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv) -> int:
    dev_only = "--dev-only" in argv
    if not DATA.is_file():
        raise SystemExit("data/raw/ZL3b-n.txt missing; run scripts/fetch_zl3b.py")
    raw = DATA.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"source identity mismatch: {blob} != {EXPECTED_BLOB}")

    by_folio = load_lines()
    order = sorted(by_folio)
    toks = materialize(by_folio, order)
    N = len(toks)
    sigma_chars = sorted({ch for t in toks for ch in t.value})
    sigma = len(sigma_chars)
    cache = {}
    dev = [t for t in toks if t.fold in DEV_FOLDS]
    hold = [t for t in toks if t.fold in HOLD_FOLDS]

    # ---- W selection: development-only prequential bits of B1+C (PLAN §6.4) ----
    w_dev = {}
    for W in W_GRID:
        m = Model(("B1", frozenset("C")), W, sigma, cache)
        w_dev[W] = sum(m.code(t, True) for t in dev)
    W = min(W_GRID, key=lambda w: (w_dev[w], w))
    W_index = W_GRID.index(W)
    check_lossless(toks, W)
    print(f"population N={N} sigma={sigma} dev={len(dev)} hold={len(hold)} "
          f"W_dev_bits={ {w: round(b) for w, b in w_dev.items()} } -> W={W}")

    if dev_only:
        # smoke every model on the first two development folios only; no holdout, no file
        smoke = [t for t in dev if t.folio in sorted({t.folio for t in dev})[:2]]
        for spec in SPECS:
            m = Model(spec, W, sigma, cache)
            for t in smoke:
                m.code(t, True)
        print("DEV_ONLY_OK (no holdout token coded, no results.json)")
        return 0

    # ---- real data: all 16 models ----
    def run_all(dev_t, hold_t):
        dev_bits, hold_bits = {}, {}
        for spec in SPECS:
            dev_bits[spec], hold_bits[spec] = dev_holdout(spec, W, sigma, cache, dev_t, hold_t)
        return dev_bits, hold_bits

    dev_bits, hold_bits = run_all(dev, hold)

    # subsets of holdout
    idx = {}
    for name, pred in (("currier:A", lambda t: t.language == "A"), ("currier:B", lambda t: t.language == "B")):
        idx[name] = np.array([i for i, t in enumerate(hold) if pred(t)])
    for s in MAJOR_SECTIONS:
        idx["section:" + s] = np.array([i for i, t in enumerate(hold) if t.section == s])
    ll = sorted(t.line_len for t in toks)
    t1, t2 = ll[len(ll) // 3], ll[2 * len(ll) // 3]
    for name, lo, hi in (("short", 0, t1 - 1), ("medium", t1, t2 - 1), ("long", t2, 10**9)):
        idx["linelen:" + name] = np.array([i for i, t in enumerate(hold) if lo <= t.line_len <= hi])
    for name, lo, hi in TOKLEN_BINS:
        idx["toklen:" + name] = np.array([i for i, t in enumerate(hold) if lo <= len(t.value) <= hi])
    hands = Counter(t.hand for t in hold)
    if len([h for h in hands if h is not None]) >= 2:
        for h in sorted(k for k in hands if k is not None):
            idx["hand:" + str(h)] = np.array([i for i, t in enumerate(hold) if t.hand == h])
    for f in sorted({t.folio for t in hold}):
        idx["folio:" + f] = np.array([i for i, t in enumerate(hold) if t.folio == f])
    idx = {k: v for k, v in idx.items() if len(v) > 0}

    real_contr = {b: contrasts(hold_bits, hold, b, idx) for b in BASES}

    # ---- nulls ----
    def null_run(seed, per_line):
        shuf = shuffled_copy(by_folio, order, seed, per_line)
        ntoks = materialize(shuf, order)
        ndev = [t for t in ntoks if t.fold in DEV_FOLDS]
        nhold = [t for t in ntoks if t.fold in HOLD_FOLDS]
        assert [t.folio for t in nhold] == [t.folio for t in hold]
        nd, nh = run_all(ndev, nhold)
        return nd, nh, {b: contrasts(nh, nhold, b, idx) for b in BASES}

    n1_dev, n1_hold, n1_contr = null_run(SEED_N1, per_line=False)
    n0_dev, n0_hold, n0_contr = null_run(SEED_N0, per_line=True)

    # ---- verdicts ----
    verd = {b: verdicts(real_contr[b], n1_contr[b]) for b in BASES}
    for X in COMPONENTS:
        same_dir = (real_contr["B0"][X]["unique_gain"] > 0) == (real_contr["B1"][X]["unique_gain"] > 0)
        verd["B1"][X]["base_dependent"] = not same_dir
    family = {
        "copy_modify_generator_signature": verd["B1"]["C"]["verdict"] == "INFORMATIVE"
        and real_contr["B1"]["C"]["unique_gain"] >= real_contr["B1"]["S"]["unique_gain"],
        "sequential_dependency_signature": verd["B1"]["S"]["verdict"] == "INFORMATIVE",
        "line_as_unit_signature": verd["B1"]["L"]["verdict"] == "INFORMATIVE",
        "note": "Ordinal readout only (PLAN §9); not a decision between language, cipher or generator.",
    }

    # ---- sensitivity: natural folio order for the development pass (B1 family) ----
    nat_order = sorted(by_folio, key=natural_folio_key)
    nat_toks = materialize(by_folio, nat_order)
    nat_dev = [t for t in nat_toks if t.fold in DEV_FOLDS]
    nat_sens = {}
    for spec in SPECS:
        if spec[0] == "B1":
            _d, hb = dev_holdout(spec, W, sigma, cache, nat_dev, hold)
            nat_sens[spec_name(spec)] = float(hb.mean())

    def table(dev_b, hold_b):
        out = {}
        for spec in SPECS:
            mb = model_bits(spec, W_index, sigma)
            hb = float(hold_b[spec].mean())
            out[spec_name(spec)] = {
                "dev_prequential_bits_per_token": dev_b[spec] / len(dev),
                "holdout_bits_per_token": hb,
                "model_bits": mb,
                "holdout_total_bits_per_token": hb + mb / len(hold),
            }
        return out

    src_share = Counter()
    for t in hold:
        _v, d = src_slot(t, W)
        src_share["exact" if d == 0 else "edit" if d == 1 else "none"] += 1

    result = {
        "experiment": "E008", "stage": "A", "hypotheses": {"H011": "S", "H012": "C", "H013": "L"},
        "evidence_class": "FROZEN_HOLDOUT (component contrasts); bases known from E007; P70 base NON-PROSPECTIVE",
        "source_identity": {"path": "data/raw/ZL3b-n.txt", "git_blob_sha1": blob,
                            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)},
        "frozen_plan_commit": "9563bc4", "amendment_commits": {"001": "f71a588"},
        "run_head_commit": head_commit(),
        "first_reveal_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "seeds": {"N1": SEED_N1, "N0": SEED_N0},
        "population": {"n_tokens": N, "n_folios": len(by_folio), "n_lines": sum(len(v) for v in by_folio.values()),
                       "sigma_size": sigma, "sigma": "".join(sigma_chars),
                       "n_development_tokens": len(dev), "n_holdout_tokens": len(hold),
                       "n_holdout_folios": len({t.folio for t in hold}),
                       "S_feature_counts": dict(Counter("BOL" if t.S == "BOL" else "UNC" if t.S == "UNC" else "glyph" for t in toks)),
                       "L_feature_counts": dict(Counter(t.L for t in toks)),
                       "line_length_terciles": [t1, t2],
                       "holdout_src_path_share": {k: v / len(hold) for k, v in src_share.items()}},
        "W_selection": {"grid": list(W_GRID), "development_data_bits_B1+C": {str(w): b for w, b in w_dev.items()},
                        "chosen_W": W, "selection_cost_bits": elias_gamma(W_index + 1) + 2},
        "lossless": True,
        "models_real": table(dev_bits, hold_bits),
        "contrasts_real": {b: real_contr[b] for b in BASES},
        "null_N1_within_folio": {"models": table(n1_dev, n1_hold), "contrasts": n1_contr},
        "null_N0_within_line": {"models": table(n0_dev, n0_hold), "contrasts": n0_contr},
        "verdicts": verd,
        "hypothesis_outcomes": {
            "H011": verd["B1"]["S"]["verdict"], "H012": verd["B1"]["C"]["verdict"], "H013": verd["B1"]["L"]["verdict"]},
        "family_readout": family,
        "best_model_by_holdout_total_bits": min(table(dev_bits, hold_bits).items(),
                                                key=lambda kv: kv[1]["holdout_total_bits_per_token"])[0],
        "sensitivity_natural_order_dev_B1_holdout_bits_per_token": nat_sens,
        "claim_ceiling": "Structural predictive-information claims only; no morphemes/language/cipher/hoax/meaning.",
    }
    out = EXP_DIR / "results.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    print(json.dumps({"W": W, "verdicts_B1": {X: verd["B1"][X]["verdict"] for X in COMPONENTS},
                      "family": {k: v for k, v in family.items() if k != "note"},
                      "holdout_bpt": {k: round(v["holdout_bits_per_token"], 3) for k, v in result["models_real"].items()}},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
