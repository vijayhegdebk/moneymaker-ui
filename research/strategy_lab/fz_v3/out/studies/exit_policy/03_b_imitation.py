"""Learner B: hindsight imitation of the oracle exit on the extended trajectory (Foundation stop floor).
State per bar t of every IS trade (entry+1 .. J_end; exlib.STATE_COLS, all as-of bar t, no whole-trade quantity); label = the
oracle exits at this bar (oracle_floor, ties -> earliest); HistGradientBoostingClassifier (class_weight balanced); policy = exit
at the first bar with P > p*, else the trajectory's terminal fill (stop / 15:25 / contract end).
CV (judge 2): 3 contiguous session-block folds (harness blocks 0-3 / 4-7 / 8-11), a training trade is purged when its
extended trajectory [entry, J_end] intersects the test fold's bar range or its session is in the 3-session embargo after the
test fold; p* is chosen INSIDE the training fold by an inner 3-fold (by training blocks) on the OOF value of the policy
(mean net per trade), then the outer model is refit on the whole training fold. Everything reported is OOF over IS.
Outputs: b_oof_<tf>.npz (per-trade OOF net and exit bar, per-state P, p*, visited, decision), b_result_<tf>.json."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, psutil
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import exlib as X, harness as H

tf = sys.argv[1]
t0 = time.time(); proc = psutil.Process()
D = X.Data(tf); T = D.T
J, hit, fill = X.floor(D)
S, trade, bar, xpx, term, snet = X.states(D, J, hit, fill)
fl_net, fl_bar, fl_row = X.oracle_floor_from_states(D, trade, bar, snet)
y = np.zeros(len(S), dtype=int); y[fl_row] = 1
print(f"{tf}: {D.n} trades, {len(S)} states ({len(S) / D.n:.1f} per trade), {S.shape[1]} features, rss {proc.memory_info().rss / 1e6:.0f} MB", flush=True)
# segment bounds per trade (states are ordered by trade then bar)
starts = np.searchsorted(trade, np.arange(D.n), side="left"); ends = np.searchsorted(trade, np.arange(D.n), side="right")
assert (ends - starts == J - D.entry).all()
term_row = ends - 1
assert term[term_row].all() and not term[~np.isin(np.arange(len(S)), term_row)].any()

FOLDS = [list(range(0, 4)), list(range(4, 8)), list(range(8, 12))]
HGB = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=200, l2_regularization=1.0, class_weight="balanced", random_state=7)


def fold_masks(test_blocks, pool):
    """(train trades, test trades) among `pool` for a set of harness blocks as the test fold (purge + embargo)."""
    lo = min(T.block_range[b][0] for b in test_blocks); hi = max(T.block_range[b][1] for b in test_blocks)
    embargo = T.block_embargo[max(test_blocks)]
    te = pool & np.isin(D.block, test_blocks)
    tr = pool & ~np.isin(D.block, test_blocks) & ~((D.entry <= hi) & (J >= lo)) & ~np.isin(D.session, list(embargo))
    return tr, te


def policy_value(P, p_star, trades_mask):
    """Per-trade net of 'exit at the first state with P > p*, else the terminal fill' over the trades in trades_mask."""
    js = np.flatnonzero(trades_mask)
    net = np.empty(len(js)); xb = np.empty(len(js), dtype=int)
    for a, j in enumerate(js):
        s0, s1 = starts[j], ends[j]
        m = np.flatnonzero(P[s0:s1 - 1] > p_star)            # the terminal state is not a decision
        r = s0 + m[0] if len(m) else s1 - 1
        net[a] = snet[r]; xb[a] = bar[r]
    return js, net, xb


def choose_p(P_oof, trades_mask, grid):
    vals = []
    for p in grid:
        _, net, _ = policy_value(P_oof, p, trades_mask); vals.append(net.mean())
    k = int(np.argmax(vals)); return grid[k], vals, k


def state_mask(trades_mask):
    return trades_mask[trade]


oof_net = np.full(D.n, np.nan); oof_bar = np.full(D.n, -1); P_all = np.full(len(S), np.nan); pstar_state = np.full(len(S), np.nan)
folds_out = []
for fi, test_blocks in enumerate(FOLDS):
    t1 = time.time()
    tr, te = fold_masks(test_blocks, np.ones(D.n, dtype=bool))
    # inner OOF probabilities over the training trades: 3 inner folds by the training fold's blocks
    tr_blocks = sorted(set(D.block[tr].tolist())); inner = [tr_blocks[i::3] for i in range(3)]
    P_in = np.full(len(S), np.nan)
    for ib in inner:
        itr, ite = fold_masks(ib, tr)
        clf = HistGradientBoostingClassifier(**HGB).fit(S[state_mask(itr)], y[state_mask(itr)])
        P_in[state_mask(ite)] = clf.predict_proba(S[state_mask(ite)])[:, 1]
    covered = tr & np.isfinite(P_in[term_row])
    qs = np.quantile(P_in[state_mask(covered) & ~term], np.linspace(0.50, 0.999, 40))
    grid = np.concatenate([qs, [np.inf]])                     # inf = never exit early (hold to the trajectory's end)
    p_star, vals, k = choose_p(P_in, covered, grid)
    clf = HistGradientBoostingClassifier(**HGB).fit(S[state_mask(tr)], y[state_mask(tr)])
    P_te = clf.predict_proba(S[state_mask(te)])[:, 1]; P_all[state_mask(te)] = P_te; pstar_state[state_mask(te)] = p_star
    js, net, xb = policy_value(P_all, p_star, te)
    oof_net[js] = net; oof_bar[js] = xb
    auc = roc_auc_score(y[state_mask(te)], P_te) if y[state_mask(te)].sum() else None
    folds_out.append(dict(fold=fi, test_blocks=test_blocks, train_trades=int(tr.sum()), test_trades=int(te.sum()), purged=int(D.n - tr.sum() - te.sum()),
                          train_states=int(state_mask(tr).sum()), test_states=int(state_mask(te).sum()), p_star=None if np.isinf(p_star) else round(float(p_star), 4),
                          p_star_is_never_exit=bool(np.isinf(p_star)), inner_grid_best_index=int(k), inner_value_at_p_star=round(float(vals[k]), 2),
                          inner_value_never_exit=round(float(vals[-1]), 2), inner_value_foundation=round(float(D.fnd_net[covered].mean()), 2),
                          test_mean=round(float(net.mean()), 2), test_fnd_mean=round(float(D.fnd_net[te].mean()), 2), test_auc=round(float(auc), 4) if auc else None,
                          exit_early_share=round(float((xb < J[js]).mean()), 4), seconds=round(time.time() - t1, 1), rss_mb=round(proc.memory_info().rss / 1e6)))
    print(json.dumps(folds_out[-1]), flush=True)
assert np.isfinite(oof_net).all()
visited = np.zeros(len(S), dtype=bool); decision = np.zeros(len(S), dtype=bool)
for j in range(D.n):
    s0 = starts[j]; r = s0 + (oof_bar[j] - D.entry[j] - 1)
    visited[s0:r + 1] = True; decision[r] = oof_bar[j] < J[j]
np.savez_compressed(os.path.join(HERE, f"b_oof_{tf}.npz"), net=oof_net, exit_bar=oof_bar, P=P_all, p_star=pstar_state, visited=visited, decision=decision,
                    trade=trade, bar=bar, term=term, y=y, snet=snet)
ctrl = np.load(os.path.join(HERE, f"controls_{tf}.npz"))
res = dict(tf=tf, trades=int(D.n), states=int(len(S)), features=X.STATE_COLS, hgb=HGB, folds=folds_out, **X.summary(D, oof_net),
           random_pct=X.pct_rank(oof_net.mean(), ctrl["rc_means"]), regret_vs_oracle_free=round(float(ctrl["oracle_free_net"].mean() - oof_net.mean()), 2),
           regret_vs_oracle_floor=round(float(fl_net.mean() - oof_net.mean()), 2), exit_early_share=round(float((oof_bar < J).mean()), 4),
           sign_flip=dict(blocks=X.sign_flip_blocks(oof_net - D.fnd_net, D.block), sessions=X.sign_flip_sessions(oof_net - D.fnd_net, D.session, tag=f"{tf}|B")),
           auc_oof=round(float(roc_auc_score(y, P_all)), 4), seconds=round(time.time() - t0, 1), rss_mb=round(proc.memory_info().rss / 1e6))
rec = dict(id=X.ledger_id("exit_policy/B", dict(learner="hindsight imitation", hgb=HGB, folds=3), tf), family="exit_policy/B", tf=tf, label="L1-entries", split="IS",
           config=dict(learner="hindsight imitation HGB, exit when P > p* (p* by inner 3-fold)", hgb=HGB, folds=3), script=os.path.basename(__file__), note="OOF over IS",
           **{k: res[k] for k in ("n", "mean", "fnd_mean", "diff", "win_rate", "pf", "t", "mean_per_session", "sign_blocks", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor")})
X.ledger_append(rec, X.session_vectors(D, oof_net)); res["ledger_id"] = rec["id"]
json.dump(res, open(os.path.join(HERE, f"b_result_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print(f"{tf}: learner B OOF mean {res['mean']} (Foundation {res['fnd_mean']}, diff {res['diff']}), random pct {res['random_pct']}, regret free {res['regret_vs_oracle_free']}, "
      f"AUC {res['auc_oof']}, sign-flip blocks p1 {res['sign_flip']['blocks']['p_one_sided']}; {res['seconds']}s, rss {res['rss_mb']} MB")
