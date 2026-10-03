"""Timing / determinism smoke test of online.run on the 5minute IS rows (worst-case configs); log smoke_timing.log."""
import sys, time, json, numpy as np
sys.path.insert(0, "."); sys.path.insert(0, "../..")
import harness as H, online as O
T = H.load("5minute"); rows = np.flatnonzero(T.is_mask)
specs = {d: O.design_spec(T, d) for d in O.DESIGNS}
tests = [("full","lints",1,"anchored"), ("full","lints",1,1000), ("full","logts",1,"anchored"), ("full","logts",10,300),
         ("context","hgb_reg",1,"anchored"), ("context","hgb_cls",1,"anchored"), ("context","logts",1,"anchored")]
for design, learner, k, win in tests:
    cfg = dict(design=design, learner=learner, cadence_k=k, window=win, reward="net", explore=0.3, seed=1, hgb=dict(min_samples_leaf=20), encoded=specs[design])
    t0 = time.time(); d1, j1, s1 = O.run(T, cfg, rows); t1 = time.time() - t0
    take = np.array([d["take"] for d in d1]); lots = np.array([d["lots"] for d in d1])
    line = f"{design:8s} {learner:8s} k={k:<3} win={str(win):9s} d={len(specs[design])+1:<4} {t1:7.1f}s take_share={take.mean():.3f} lots_taken_mean={lots[take].mean() if take.any() else 0:.2f} states={len(set(s1))} last={j1[-1]['reason']}"
    if (design, learner) == ("full", "lints") and win == "anchored":
        d2, j2, s2 = O.run(T, cfg, rows)
        line += f" deterministic={O.journal_sha(j1) == O.journal_sha(j2) and d1 == d2 and s1 == s2}"
        # accumulated sums vs a recompute over the same closed rows
        Xf = []; O.run_heads(T, cfg, rows, [dict(explore=0.0, seed=0, reward="net")], features_out=Xf); Xf = np.asarray(Xf)
        closed = [i for i in range(len(rows)) if T.exit_bar[rows][i] < T.setup_i[rows][-1]]
        A = np.eye(Xf.shape[1]) + Xf[closed].T @ Xf[closed]; b = Xf[closed].T @ O.fit_reward(T.net[rows][closed], "net", O.DEFAULTS["reward_unit"])
        mu = np.linalg.solve(A, b)
        L = O.LinTS(Xf.shape[1], 1.0); Aa = np.eye(Xf.shape[1]); ba = np.zeros(Xf.shape[1])
        for i in closed: Aa = Aa + np.outer(Xf[i], Xf[i]); ba = ba + O.fit_reward(T.net[rows][i], "net", O.DEFAULTS["reward_unit"]) * Xf[i]
        line += f" incremental_vs_recompute_max_abs_dmu={np.max(np.abs(np.linalg.solve(Aa, ba) - mu)):.2e}"
    print(line, flush=True)
print(json.dumps(j1[-1], default=str)[:1200])
