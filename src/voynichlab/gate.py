"""Gate v2 — machine-checkable decipherment promotion gate (hypothesis-neutral).

Evaluates a *claim record* (JSON/dict produced by an experiment) against the
versioned specification in research/gate/gate_v2.json and returns one state per
evidence level:

    STRUCTURAL_MODEL_VALIDATED
    DECODING_MECHANISM_SUPPORTED
    LANGUAGE_IDENTIFICATION_SUPPORTED
    SEMANTIC_DECODING_SUPPORTED
    DECIPHERMENT_CONFIRMED

States: PASS, FAIL, INCONCLUSIVE, NOT_TESTED. A level can be PASS only if every
lower level is PASS; a compression PASS never promotes a language or semantic
level by itself. Nothing here reads the corpus: the record carries the numbers,
the gate applies the frozen rules. See research/protocol_amendments/A001_GATE_V2.md.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

LEVELS = (
    "STRUCTURAL_MODEL_VALIDATED",
    "DECODING_MECHANISM_SUPPORTED",
    "LANGUAGE_IDENTIFICATION_SUPPORTED",
    "SEMANTIC_DECODING_SUPPORTED",
    "DECIPHERMENT_CONFIRMED",
)
PASS, FAIL, INCONCLUSIVE, NOT_TESTED = "PASS", "FAIL", "INCONCLUSIVE", "NOT_TESTED"
DEFAULT_SPEC = Path(__file__).resolve().parents[2] / "research" / "gate" / "gate_v2.json"


def load_spec(path: str | Path | None = None) -> dict:
    return json.loads(Path(path or DEFAULT_SPEC).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# statistics (numpy only, deterministic)
# --------------------------------------------------------------------------- #
def bootstrap_mean_ci(diffs, resamples=10000, seed=20261019, lower_q=0.025):
    """Percentile bootstrap CI of the mean of folio-level paired differences."""
    d = np.asarray(diffs, dtype=float)
    if d.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, d.size, size=(resamples, d.size))
    means = d[idx].mean(axis=1)
    return float(d.mean()), float(np.quantile(means, lower_q)), float(np.quantile(means, 1 - lower_q))


def permutation_p(observed: float, null_values) -> float:
    """One-sided permutation p-value with the +1 correction (never exactly 0)."""
    null = np.asarray(null_values, dtype=float)
    return float((1 + np.sum(null >= observed)) / (1 + null.size))


def holm_adjust(pvalues: dict) -> dict:
    """Holm step-down adjusted p-values for a dict name -> p."""
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adjusted[name] = running
    return adjusted


# --------------------------------------------------------------------------- #
# result container
# --------------------------------------------------------------------------- #
@dataclass
class LevelResult:
    state: str
    reasons: list = field(default_factory=list)
    numbers: dict = field(default_factory=dict)


@dataclass
class GateResult:
    gate_version: str
    claim_id: str
    registration: LevelResult
    levels: dict
    flags: list = field(default_factory=list)

    @property
    def highest_pass(self) -> str | None:
        best = None
        for lv in LEVELS:
            if self.levels[lv].state == PASS:
                best = lv
            else:
                break
        return best

    def to_dict(self) -> dict:
        return {
            "gate_version": self.gate_version,
            "claim_id": self.claim_id,
            "registration": self.registration.__dict__,
            "levels": {k: v.__dict__ for k, v in self.levels.items()},
            "highest_pass": self.highest_pass,
            "flags": self.flags,
        }


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def check_registration(claim: dict, spec: dict, registry: dict | None) -> tuple[LevelResult, list]:
    reasons, flags = [], []
    for f in spec["registration"]["required_fields"]:
        if f not in claim or claim[f] in (None, "", {}):
            reasons.append(f"missing registration field: {f}")
    sha = claim.get("sha256", {}) or {}
    for k in spec["registration"]["sha256_required_for"]:
        v = sha.get(k)
        if not (isinstance(v, str) and len(v) == 64):
            reasons.append(f"missing or malformed sha256 for {k}")
    if claim.get("post_reveal_changes"):
        reasons.append("post_reveal_changes = true (scoring/tuning changed after reveal)")
    if registry is not None and claim.get("lockbox_id"):
        lb = registry.get("lockboxes", {}).get(claim["lockbox_id"])
        if lb is None:
            reasons.append(f"lockbox_id {claim['lockbox_id']} not in holdout registry")
        else:
            sel = set(registry.get("selection_folios", []))
            overlap = sorted(set(lb.get("folios", [])) & sel)
            if overlap:
                reasons.append(f"lockbox overlaps SELECTION folios: {overlap[:5]}…")
            if claim.get("lockbox_folios") is not None and sorted(claim["lockbox_folios"]) != sorted(lb.get("folios", [])):
                reasons.append("claim lockbox_folios differ from the registered lockbox")
            if lb.get("independence") != "INDEPENDENT":
                flags.append(f"lockbox {claim['lockbox_id']} is {lb.get('independence')}: "
                             "not a fully independent confirmation set")
    return LevelResult(FAIL if reasons else PASS, reasons), flags


def compression_test(block: dict, spec: dict) -> LevelResult:
    """Frozen MDL comparison on the lockbox: candidate total bits vs null total bits per folio."""
    cs = spec["compression"]
    reasons, numbers = [], {}
    if not block:
        return LevelResult(NOT_TESTED, ["no compression block"])
    # reconstruction of the observed text
    if block.get("reconstruction_sha256") != block.get("lockbox_text_sha256") or not block.get("lockbox_text_sha256"):
        return LevelResult(NOT_TESTED, ["candidate does not reconstruct the observed lockbox text (sha256 mismatch or missing)"])
    # model bits accounting
    mb = block.get("candidate_model_bits") or {}
    missing = [c for c in cs["model_bits_components"] if c not in mb]
    if missing:
        return LevelResult(FAIL, [f"model_bits components missing: {missing}"])
    if any((not isinstance(mb[c], (int, float))) or mb[c] < 0 for c in cs["model_bits_components"]):
        return LevelResult(FAIL, ["model_bits components must be numbers >= 0"])
    model_bits = float(sum(mb[c] for c in cs["model_bits_components"]))
    # margin provenance
    mg = block.get("margin") or {}
    margin = mg.get("bits_per_token")
    if not isinstance(margin, (int, float)) or margin <= 0:
        return LevelResult(FAIL, ["margin.bits_per_token missing or non-positive"])
    if mg.get("calibration_source") != "development" or not mg.get("justification"):
        return LevelResult(FAIL, ["margin must be calibrated on development data with a written justification"])
    # folio-level paired differences in bits/token (null total minus candidate total)
    folios = block.get("folios") or []
    N = sum(f["n_tokens"] for f in folios) if folios else 0
    if N == 0:
        return LevelResult(FAIL, ["no folio data"])
    diffs = []
    for f in folios:
        n = f["n_tokens"]
        cand = (f["candidate_data_bits"] + model_bits * n / N) / n
        null = f["null_total_bits"] / n
        diffs.append(null - cand)
    ci = cs["ci"]
    mean, lo, hi = bootstrap_mean_ci(diffs, ci["resamples"], ci["seed"], ci["lower_quantile"])
    numbers.update({"n_folios": len(folios), "n_tokens": N, "model_bits": model_bits,
                    "mean_delta_bits_per_token": mean, "ci_lower": lo, "ci_upper": hi, "margin": margin})
    if len(folios) < cs["min_folios"]:
        return LevelResult(INCONCLUSIVE, [f"underpowered: {len(folios)} folios < {cs['min_folios']}"], numbers)
    if mean >= margin and lo > 0:
        state = PASS
    elif hi < margin:
        state = FAIL
        reasons.append(f"ci_upper {hi:.3f} < margin {margin}")
    else:
        state = INCONCLUSIVE
        reasons.append("estimate imprecise relative to margin (not PASS, not FAIL)")
    # control gains are always reported
    controls = block.get("controls") or {}
    numbers["control_gains"] = {k: (v["null_total_bits_per_token"] - v["candidate_total_bits_per_token"])
                                for k, v in controls.items()}
    return LevelResult(state, reasons, numbers)


def specificity_test(block: dict, real_gain: float, margin: float, spec: dict) -> LevelResult:
    cs = spec["compression"]["specificity"]
    controls = (block or {}).get("controls") or {}
    missing = [c for c in cs["required_controls"] if c not in controls]
    if missing:
        return LevelResult(NOT_TESTED, [f"controls missing: {missing}"])
    bad, gains = [], {}
    for c in cs["required_controls"]:
        g = controls[c]["null_total_bits_per_token"] - controls[c]["candidate_total_bits_per_token"]
        gains[c] = g
        if g >= real_gain - margin:
            bad.append(f"{c}: control gain {g:.3f} >= real gain {real_gain:.3f} - margin {margin}")
    return LevelResult(FAIL if bad else PASS, bad, {"control_gains": gains})


def mechanism_test(claim: dict, spec: dict, compression: LevelResult) -> LevelResult:
    mech = claim.get("mechanism")
    if not mech:
        return LevelResult(NOT_TESTED, ["no mechanism block (structural claim only)"])
    reasons = []
    if not mech.get("produces_plaintext"):
        reasons.append("mechanism does not produce a plaintext")
    if not mech.get("deterministic"):
        reasons.append("mechanism not declared deterministic/executable")
    if not mech.get("plaintext_sha256"):
        reasons.append("plaintext_sha256 missing (output must be fixed before evaluation)")
    if mech.get("output_freedom_bits_per_token") is None:
        reasons.append("output_freedom_bits_per_token missing (log2 of admissible plaintext choices per token)")
    if reasons:
        return LevelResult(FAIL, reasons)
    if compression.state != PASS:
        return LevelResult(compression.state if compression.state != NOT_TESTED else NOT_TESTED,
                           ["requires compression PASS"] + compression.reasons)
    spec_res = specificity_test(claim.get("compression"), compression.numbers["mean_delta_bits_per_token"],
                                compression.numbers["margin"], spec)
    if spec_res.state != PASS:
        return LevelResult(spec_res.state if spec_res.state != NOT_TESTED else INCONCLUSIVE,
                           ["specificity: " + r for r in spec_res.reasons] or ["specificity controls missing"],
                           spec_res.numbers)
    return LevelResult(PASS, [], {"specificity": spec_res.numbers})


def language_test(block: dict, spec: dict, margin: float) -> LevelResult:
    if not block:
        return LevelResult(NOT_TESTED, ["no language block"])
    ls = spec["language"]
    alts = block.get("alternatives") or []
    reasons, numbers = [], {}
    if len(alts) < ls["min_alternatives"]:
        reasons.append(f"fewer than {ls['min_alternatives']} alternative languages")
    if block.get("control_prefers_target"):
        reasons.append("pipeline prefers the target language on the nonsemantic generator control")
    if not block.get("corpora_sha256"):
        reasons.append("training corpora hashes missing")
    if reasons:
        return LevelResult(FAIL, reasons)
    ci = spec["compression"]["ci"]
    worst = None
    for alt in alts:
        diffs = [(f["alt_bits"][alt] - f["target_bits"]) / f["n_tokens"] for f in block["folios"]]
        mean, lo, hi = bootstrap_mean_ci(diffs, ci["resamples"], ci["seed"], ci["lower_quantile"])
        numbers[alt] = {"mean_delta": mean, "ci_lower": lo, "ci_upper": hi}
        if worst is None or mean < worst[1]:
            worst = (alt, mean, lo, hi)
    if len(block["folios"]) < spec["compression"]["min_folios"]:
        return LevelResult(INCONCLUSIVE, ["underpowered"], numbers)
    alt, mean, lo, hi = worst
    if mean >= margin and lo > 0:
        return LevelResult(PASS, [], numbers)
    if hi < margin:
        return LevelResult(FAIL, [f"target does not beat {alt} by the margin"], numbers)
    return LevelResult(INCONCLUSIVE, [f"imprecise against {alt}"], numbers)


def semantic_test(block: dict, spec: dict) -> LevelResult:
    if not block:
        return LevelResult(NOT_TESTED, ["no semantic block"])
    ss = spec["semantic"]
    reasons = []
    if not block.get("predictions_registered_before_inspection"):
        reasons.append("predictions were not hash-registered before illustration inspection")
    if block.get("claims_true_word_error_rate"):
        reasons.append("a true word error rate is claimed; none can exist without known plaintext")
    for k in ss["coverage_report"]:
        if k not in block:
            reasons.append(f"coverage report field missing: {k}")
    for k in ss["separate_reports"]:
        if k not in (block.get("reports") or {}):
            reasons.append(f"separate report missing: {k}")
    fams = block.get("families") or []
    primary = [f for f in fams if f.get("primary", True)]
    if not primary:
        reasons.append("no primary prediction family")
    if reasons:
        return LevelResult(FAIL, reasons)
    raw = {f["name"]: permutation_p(f["observed_effect"], f["null_effects"]) for f in fams}
    adj = holm_adjust(raw)
    numbers = {"p_raw": raw, "p_holm": adj}
    fails, weak = [], []
    for f in primary:
        if len(f["null_effects"]) < 99:
            weak.append(f"{f['name']}: fewer than 99 permutations")
        if f["observed_effect"] < f["min_effect"]:
            fails.append(f"{f['name']}: effect {f['observed_effect']} < pre-registered minimum {f['min_effect']}")
        if adj[f["name"]] > 0.01:
            fails.append(f"{f['name']}: Holm-adjusted p {adj[f['name']]:.4f} > 0.01")
    if fails:
        return LevelResult(FAIL, fails, numbers)
    if weak:
        return LevelResult(INCONCLUSIVE, weak, numbers)
    return LevelResult(PASS, [], numbers)


def confirmation_test(block: dict, spec: dict, margin: float) -> LevelResult:
    if not block:
        return LevelResult(NOT_TESTED, ["no confirmation block"])
    cs = spec["confirmation"]
    reasons = []
    rep = block.get("independent_replication") or {}
    if not (rep.get("implementer") and rep.get("sha256") and rep.get("result_direction_same")):
        reasons.append("independent replication missing or not in the same direction")
    tr = block.get("transliterations") or {}
    for t in cs["transliterations"]["required"]:
        r = tr.get(t)
        if not r:
            reasons.append(f"transliteration {t} missing")
            continue
        clear = r.get("clear") or {}
        if not ("mean_delta" in clear and "ci_lower" in clear):
            reasons.append(f"{t}: clear-passage result missing")
        elif not (clear["mean_delta"] >= margin and clear["ci_lower"] > 0):
            reasons.append(f"{t}: clear passages do not reproduce the effect")
        if "uncertain" not in r:
            reasons.append(f"{t}: uncertain-passage result not reported separately")
    if block.get("retraction_condition_triggered"):
        reasons.append("registered retraction condition triggered")
    return LevelResult(FAIL if reasons else PASS, reasons)


# --------------------------------------------------------------------------- #
# evaluation
# --------------------------------------------------------------------------- #
def evaluate(claim: dict, spec: dict | None = None, registry: dict | None = None) -> GateResult:
    spec = spec or load_spec()
    reg, flags = check_registration(claim, spec, registry)
    levels = {}
    if reg.state != PASS:
        for lv in LEVELS:
            levels[lv] = LevelResult(FAIL, ["registration invalid"] + reg.reasons)
        return GateResult(spec["gate_version"], claim.get("claim_id", "?"), reg, levels, flags)

    comp = compression_test(claim.get("compression"), spec)
    levels[LEVELS[0]] = comp
    margin = comp.numbers.get("margin", spec["compression"]["margin_bits_per_token"]["provisional_default"])
    levels[LEVELS[1]] = mechanism_test(claim, spec, comp)
    lang = language_test(claim.get("language"), spec, margin)
    sem = semantic_test(claim.get("semantic"), spec)
    conf = confirmation_test(claim.get("confirmation"), spec, margin)
    # a level can only be PASS when every lower level is PASS
    chain = [comp, levels[LEVELS[1]], lang, sem, conf]
    for i in range(2, 5):
        r = chain[i]
        if r.state == PASS and any(c.state != PASS for c in chain[:i]):
            chain[i] = LevelResult(INCONCLUSIVE, ["own evidence passes but a lower level is not PASS"] + r.reasons, r.numbers)
    levels[LEVELS[2]], levels[LEVELS[3]], levels[LEVELS[4]] = chain[2], chain[3], chain[4]
    return GateResult(spec["gate_version"], claim.get("claim_id", "?"), reg, levels, flags)


def render_report(result: GateResult) -> str:
    lines = [f"# Gate v{result.gate_version} report — claim `{result.claim_id}`", "",
             f"Registration: **{result.registration.state}**"]
    lines += [f"- {r}" for r in result.registration.reasons]
    for fl in result.flags:
        lines.append(f"- ⚠ {fl}")
    lines += ["", "| level | state | reasons |", "|---|---|---|"]
    for lv in LEVELS:
        r = result.levels[lv]
        lines.append(f"| {lv} | **{r.state}** | {'; '.join(r.reasons) or '—'} |")
    lines += ["", f"Highest PASS level: **{result.highest_pass or 'none'}**", "",
              "Numbers:", "```json", json.dumps({lv: result.levels[lv].numbers for lv in LEVELS}, indent=1, default=str),
              "```"]
    return "\n".join(lines) + "\n"
