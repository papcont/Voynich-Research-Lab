"""E022 pre-freeze power simulation (committed with the freeze), driven ONLY by per-stratum
marginals (N_s, n_y,s, k_qo,s) from prefreeze_marginals.py: paragraph strata for the line-break
class, folio strata for the paragraph-break class. Synthetic tables: a_s ~ Bin(n_y,s, p_y,s),
c_s ~ Bin(n_o,s, p_o,s) with p_y,s = R·p_o,s and E[a_s + c_s] = k_qo,s; the pairing null is the
exact hypergeometric distribution of a_s given (N_s, n_y,s, m_s). Reports the null 97.5% quantile
of R_MH and P(SUPPORTED_DEV) = P(R_MH >= 1.5 and p <= 0.01) on a grid of true R. Adapted from the
2026-10-20 review's simulation. No manuscript joint cell is used.

Run:  python experiments/E022_line_break_coupling/prefreeze_marginals.py > /path/marginals.json  (strip the sha line)
      python experiments/E022_line_break_coupling/prefreeze_power.py /path/marginals.json
"""
from __future__ import annotations

import json
import sys

import numpy as np

N_PERM, N_SIM, SEED = 1000, 400, 12345
GRID_LINE = [1.0, 1.2, 1.5, 1.7, 2.0, 2.5, 3.0]
GRID_PARA = [1.0, 2.0, 3.0, 4.0, 6.0]


def mh(a, c, ny, no, N):
    inf = ((ny > 0) & (no > 0)).reshape(-1)
    num = (a * no / np.maximum(N, 1))[..., inf].sum(-1); den = (c * ny / np.maximum(N, 1))[..., inf].sum(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den > 0, num / den, np.nan)


def simulate(table, R, rng):
    N = np.array([v["N"] for v in table.values()]); ny = np.array([v["n_y"] for v in table.values()])
    k = np.array([v["k_qo"] for v in table.values()]); no = N - ny
    p_o = np.where(R * ny + no > 0, k / np.maximum(R * ny + no, 1e-9), 0.0); p_y = np.minimum(1.0, R * p_o)
    sup = 0; q975s = []; ps = []; nan_frac = []
    for _ in range(N_SIM):
        a = rng.binomial(ny, p_y); c = rng.binomial(no, p_o); m = a + c
        R_obs = float(mh(a, c, ny, no, N))
        A = np.empty((N_PERM, len(N)))
        for s in range(len(N)):
            A[:, s] = rng.hypergeometric(ny[s], no[s], m[s], size=N_PERM) if (m[s] > 0 and N[s] > 0) else 0
        R_null = mh(A, m[None, :] - A, ny[None, :], no[None, :], N[None, :])
        n_undef = int(np.isnan(R_null).sum())
        p = (1 + np.nansum(R_null >= R_obs) + n_undef) / (N_PERM + 1)
        q975s.append(float(np.nanquantile(R_null, 0.975))); ps.append(p); nan_frac.append(n_undef / N_PERM)
        if not np.isnan(R_obs) and R_obs >= 1.5 and p <= 0.01:
            sup += 1
    inf = (ny > 0) & (no > 0)
    return {"R_true": R, "P_supported": sup / N_SIM, "P_p_le_0.01": float(np.mean(np.array(ps) <= 0.01)),
            "null_q975_mean": float(np.mean(q975s)), "null_undefined_fraction": float(np.mean(nan_frac)),
            "n_strata_informative": int(inf.sum()), "qo_events_informative": int(k[inf].sum())}


def main():
    marg = json.load(open(sys.argv[1]))["per_stratum_marginals"]
    rng = np.random.default_rng(SEED)
    out = {}
    for pop in ("bio_B", "other_B", "A"):
        out[f"{pop}/line"] = [simulate(marg[pop]["line"], R, rng) for R in GRID_LINE]
    pooled = {**{"bio:" + s: v for s, v in marg["bio_B"]["para"].items()}, **{"oth:" + s: v for s, v in marg["other_B"]["para"].items()}}
    out["B_pooled/para"] = [simulate(pooled, R, rng) for R in GRID_PARA]
    for key, rows in out.items():
        print(f"== {key}: informative strata {rows[0]['n_strata_informative']}, qo events in them {rows[0]['qo_events_informative']}")
        for r in rows:
            print(f"   R={r['R_true']:.1f}  P(SUPPORTED) {r['P_supported']:.2f}  P(p<=.01) {r['P_p_le_0.01']:.2f}  null q975 {r['null_q975_mean']:.2f}  undefined {r['null_undefined_fraction']:.3f}")
    json.dump(out, open(sys.argv[2], "w"), indent=1) if len(sys.argv) > 2 else None


if __name__ == "__main__":
    main()
