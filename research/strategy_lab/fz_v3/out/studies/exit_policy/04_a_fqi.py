"""Learner A: fitted Q-iteration on the extended trajectories (Exo-MDP: the tape does not react, both actions' outcomes are
on it). Actions {hold, exit_all}; a decision state is every trajectory bar but the terminal one; exit reward = the net per lot
of exiting at the bar's close (lab.price_trade arithmetic, slipped); hold reward = 0, or the terminal fill's net when the next
bar ends the trajectory (Foundation stop / 15:25 / contract end); gamma 1. Q(s, a) = HistGradientBoostingRegressor on
(state, action), 20 iterations (Q_{k+1} = r + max_a' Q_k(s', a')), 5 bootstrap members (trajectories resampled with
replacement, seeded), greedy on mean - 1.0 x std over members (pessimistic value). No off-policy correction is needed: every
transition's outcome is observed (DR-OPE was reserved for limit-target fills, which this action set has none of).
CV: the 3 session-block folds of learner B (exlib.FOLDS3, purge by the trajectory, 3-session embargo); Q-ensembles refit per
fold; OOF over IS. The state count and RSS are logged. Outputs: a_oof_<tf>.npz, a_result_<tf>.json."""
import sys, os, json, time
sys.dont_write_bytecode = True
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, psutil
from joblib import Parallel, delayed
from sklearn.ensemble import HistGradientBoostingRegressor
import exlib as X

tf = sys.argv[1]
ITER, MEMBERS, KAPPA = 20, 5, 1.0
HGB = dict(max_iter=200, learning_rate=0.1, max_leaf_nodes=31, min_samples_leaf=100, l2_regularization=1.0, random_state=11)
t0 = time.time(); proc = psutil.Process()
D = X.Data(tf)
J, hit, fill = X.floor(D)
S, trade, bar, xpx, term, snet = X.states(D, J, hit, fill)
starts, ends = X.segments(trade, D.n)
dec = np.flatnonzero(~term)                                   # decision states; the next row is the same trade's next bar
assert (trade[dec + 1] == trade[dec]).all()
nxt = dec + 1
r_exit = snet[dec]
term_next = term[nxt]
r_hold = np.where(term_next, snet[nxt], 0.0)
S32 = S.astype(np.float32)
print(f"{tf}: {D.n} trades, {len(S)} states, {len(dec)} decision states x 2 actions = {2 * len(dec)} regression rows per fit, "
      f"rss {proc.memory_info().rss / 1e6:.0f} MB", flush=True)


def with_action(Sx, a):
    return np.hstack([Sx, np.full((len(Sx), 1), a, dtype=np.float32)])


def fit_member(m, tr_trades, seed):
    """One bootstrap member: FQI over ITER iterations on the transitions of a resample of the training trades."""
    rng = np.random.default_rng(seed)
    js = np.flatnonzero(tr_trades); boot = rng.choice(js, size=len(js), replace=True)
    rows = np.concatenate([np.arange(starts[j], ends[j] - 1) for j in boot])          # decision rows with multiplicity
    d_idx = np.searchsorted(dec, rows); assert (dec[d_idx] == rows).all()
    Xe = with_action(S32[rows], 1.0); Xh = with_action(S32[rows], 0.0)
    Xfit = np.vstack([Xe, Xh])
    re, rh, tn = r_exit[d_idx], r_hold[d_idx], term_next[d_idx]
    Sn = S32[rows + 1]                                                              # next states (terminal ones unused)
    Xn_e, Xn_h = with_action(Sn, 1.0), with_action(Sn, 0.0)
    boot_v = np.zeros(len(rows))
    q = None
    for k in range(ITER):
        y = np.concatenate([re, rh + np.where(tn, 0.0, boot_v)])
        q = HistGradientBoostingRegressor(**HGB).fit(Xfit, y)
        boot_v = np.maximum(q.predict(Xn_e), q.predict(Xn_h))
    return q


oof_net = np.full(D.n, np.nan); oof_bar = np.full(D.n, -1)
q_exit_all = np.full((len(S), MEMBERS), np.nan, dtype=np.float32); q_hold_all = np.full((len(S), MEMBERS), np.nan, dtype=np.float32)
folds_out = []
for fi, test_blocks in enumerate(X.FOLDS3):
    t1 = time.time()
    tr, te = X.fold_masks(D, J, test_blocks, np.ones(D.n, dtype=bool))
    members = Parallel(n_jobs=min(4, MEMBERS), backend="loky")(delayed(fit_member)(m, tr, 1000 * fi + m) for m in range(MEMBERS))
    te_rows = np.flatnonzero(te[trade])
    Qe = np.stack([q.predict(with_action(S32[te_rows], 1.0)) for q in members], axis=1)
    Qh = np.stack([q.predict(with_action(S32[te_rows], 0.0)) for q in members], axis=1)
    q_exit_all[te_rows] = Qe; q_hold_all[te_rows] = Qh
    pess_e = Qe.mean(axis=1) - KAPPA * Qe.std(axis=1); pess_h = Qh.mean(axis=1) - KAPPA * Qh.std(axis=1)
    flag = np.zeros(len(S), dtype=bool); flag[te_rows] = pess_e > pess_h
    js, net, xb, _ = X.first_exit_policy(starts, ends, flag, snet, bar, te)
    oof_net[js] = net; oof_bar[js] = xb
    folds_out.append(dict(fold=fi, test_blocks=test_blocks, train_trades=int(tr.sum()), test_trades=int(te.sum()), purged=int(D.n - tr.sum() - te.sum()),
                          test_states=int(len(te_rows)), test_mean=round(float(net.mean()), 2), test_fnd_mean=round(float(D.fnd_net[te].mean()), 2),
                          exit_early_share=round(float((xb < J[js]).mean()), 4), exit_flag_share=round(float((pess_e > pess_h).mean()), 4),
                          q_exit_fit_mae=round(float(np.abs(Qe.mean(axis=1) - snet[te_rows]).mean()), 2),
                          seconds=round(time.time() - t1, 1), rss_mb=round(proc.memory_info().rss / 1e6)))
    print(json.dumps(folds_out[-1]), flush=True)
assert np.isfinite(oof_net).all()
visited = np.zeros(len(S), dtype=bool); decision = np.zeros(len(S), dtype=bool)
for j in range(D.n):
    r = starts[j] + (oof_bar[j] - D.entry[j] - 1); visited[starts[j]:r + 1] = True; decision[r] = oof_bar[j] < J[j]
np.savez_compressed(os.path.join(HERE, f"a_oof_{tf}.npz"), net=oof_net, exit_bar=oof_bar, q_exit=q_exit_all, q_hold=q_hold_all, visited=visited, decision=decision, trade=trade, bar=bar, term=term, snet=snet)
ctrl = np.load(os.path.join(HERE, f"controls_{tf}.npz"))
fl_net = ctrl["oracle_floor_net"]
res = dict(tf=tf, trades=int(D.n), states=int(len(S)), decision_states=int(len(dec)), iterations=ITER, members=MEMBERS, kappa=KAPPA, hgb=HGB, folds=folds_out, **X.summary(D, oof_net),
           random_pct=X.pct_rank(oof_net.mean(), ctrl["rc_means"]), regret_vs_oracle_free=round(float(ctrl["oracle_free_net"].mean() - oof_net.mean()), 2),
           regret_vs_oracle_floor=round(float(fl_net.mean() - oof_net.mean()), 2), exit_early_share=round(float((oof_bar < J).mean()), 4),
           sign_flip=dict(blocks=X.sign_flip_blocks(oof_net - D.fnd_net, D.block), sessions=X.sign_flip_sessions(oof_net - D.fnd_net, D.session, tag=f"{tf}|A")),
           seconds=round(time.time() - t0, 1), rss_mb=round(proc.memory_info().rss / 1e6))
cfg = dict(learner="FQI HGB on (state, action), 20 iterations, 5 bootstrap members, greedy on mean - 1.0 std", hgb=HGB, folds=3)
rec = dict(id=X.ledger_id("exit_policy/A", cfg, tf), family="exit_policy/A", tf=tf, label="L1-entries", split="IS", config=cfg, script=os.path.basename(__file__), note="OOF over IS",
           **{k: res[k] for k in ("n", "mean", "fnd_mean", "diff", "win_rate", "pf", "t", "mean_per_session", "sign_blocks", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor")})
X.ledger_append(rec, X.session_vectors(D, oof_net)); res["ledger_id"] = rec["id"]
json.dump(res, open(os.path.join(HERE, f"a_result_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print(f"{tf}: learner A OOF mean {res['mean']} (Foundation {res['fnd_mean']}, diff {res['diff']}), random pct {res['random_pct']}, regret free {res['regret_vs_oracle_free']}, "
      f"sign-flip blocks p1 {res['sign_flip']['blocks']['p_one_sided']}; {res['seconds']}s, rss {res['rss_mb']} MB")
