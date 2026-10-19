"""E011 post-run EXPLORATORY decomposition (NOT gated, written after results.json).

Which previous-final glyphs carry the M_S gain, and which (previous final ->
prefix) transitions? Out-of-fold per-token differences M0 - M_S are grouped by
S value and by Currier language. Descriptive only; motivates nothing but a
future preregistration.

Run:  python experiments/E011_targeted_context_scorecard/exploratory.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP_DIR))

import run  # noqa: E402


def main() -> int:
    toks, _ = run.load_population()
    sigma = len({c for t in toks for c in t.value})
    p0 = run.crossfit(toks, run.MODELS["M0"], sigma)
    ps = run.crossfit(toks, run.MODELS["M_S"], sigma)
    gain = p0 - ps
    by_S, by_S_lang, n_S = defaultdict(float), defaultdict(float), Counter()
    pref_given_S = defaultdict(Counter)
    for t, g in zip(toks, gain):
        by_S[t.feat["S"]] += g
        by_S_lang[(t.feat["S"], t.language)] += g
        n_S[t.feat["S"]] += 1
        pref_given_S[t.feat["S"]][t.slots[0] or "∅"] += 1
    N = len(toks)
    rows = sorted(by_S, key=lambda s: -by_S[s])
    out = {
        "evidence_class": "EXPLORATORY_POST_RUN", "gated": False,
        "total_gain_bits_per_token": float(gain.mean()),
        "share_of_total_gain_by_previous_final": {s: {"n": n_S[s], "share": by_S[s] / gain.sum(),
                                                      "gain_per_token_in_group": by_S[s] / n_S[s],
                                                      "top_prefixes": pref_given_S[s].most_common(3)} for s in rows[:10]},
        "gain_per_token_by_previous_final_and_currier": {f"{s}|{L}": v / sum(1 for t in toks if t.feat['S'] == s and t.language == L)
                                                          for (s, L), v in by_S_lang.items() if L in ("A", "B") and n_S[s] >= 500},
        "note": "y-final previous tokens: check whether their gain concentrates on prefix qo (E002/H003 shape).",
    }
    (EXP_DIR / "exploratory_post_run.json").write_text(json.dumps(out, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, default=float)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
