"""Learner C selection and the yardsticks (one timeframe per run): every variant to the exit ledger (append-only,
exit_ledger.jsonl + vectors/*.npz, harness-compatible per-session vectors: kept = the variant, skipped / all = the Foundation
L1 exit on the same entries), the nested-CV pick inside harness.purged_splits (choose by mean net per lot on the training
fold, apply to the test fold), the 11 CPCV paths (pick per split), the multiplicity certificate over the family
(harness.pbo 'diff', harness.spa, harness.effective_trials, harness.bootstrap_ci), the random-exit control (2,000 seeded
draws) and the hindsight oracles, the ST9 R-ladder comparator (tuned on 2026 = OOS: not an OOS comparator), and the paired
session-block sign-flip tests against the Foundation exit.
Value = net per trade per lot (INR): a 1-lot variant's net; a ladder's position net / 3 (per position also reported)."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import exlib as X, harness as H

tf = sys.argv[1]
t0 = time.time()
D = X.Data(tf); T = D.T
G = np.load(os.path.join(HERE, f"c_grid_{tf}.npz")); V = json.load(open(os.path.join(HERE, "c_variants.json")))
assert np.array_equal(G["entry"], D.entry) and np.array_equal(G["fnd_net"], D.fnd_net)
lots = G["lots"]; NP = G["net_pos"]; N = NP / lots; XB = G["exit_bar"]; RS = G["reason"]
nV = len(V)
REASON_NAMES = ["stop_loss", "trail_stop", "target", "eod", "expiry", "time_stop", "choch_against", "open"]
local = np.full(T.n, -1); local[D.is_idx] = np.arange(D.n)

# ---------------------------------------------------------------- yardsticks
rc_means, _ = X.random_control(D)
of_net, of_bar = X.oracle_free(D)
J, hit, fill = X.floor(D)
Xs, trade, bar, xpx, term, snet = X.states(D, J, hit, fill)
fl_net, fl_bar, fl_row = X.oracle_floor_from_states(D, trade, bar, snet)
np.savez_compressed(os.path.join(HERE, f"controls_{tf}.npz"), rc_means=rc_means, oracle_free_net=of_net, oracle_free_bar=of_bar,
                    oracle_floor_net=fl_net, oracle_floor_bar=fl_bar, J=J, hit=hit, fill=fill, fnd_net=D.fnd_net, entry=D.entry)
print(f"{tf}: random control mean of means {rc_means.mean():.1f} (p5 {np.quantile(rc_means, .05):.1f}, p95 {np.quantile(rc_means, .95):.1f}); "
      f"oracle free {of_net.mean():.1f}, oracle floor {fl_net.mean():.1f}, Foundation {D.fnd_net.mean():.1f}", flush=True)


def yard(net):
    s = X.summary(D, net)
    s.update(random_pct=X.pct_rank(net.mean(), rc_means), regret_vs_oracle_free=round(float(of_net.mean() - net.mean()), 2),
             regret_vs_oracle_floor=round(float(fl_net.mean() - net.mean()), 2))
    return s


def ledger(family, config, net, extra=None, note=None):
    rec = dict(id=X.ledger_id(family, config, tf), family=family, tf=tf, label="L1-entries", split="IS", config=config, script=os.path.basename(__file__),
               note=note, **yard(net))
    if extra: rec.update(extra)
    X.ledger_append(rec, X.session_vectors(D, net))
    return rec


# ---------------------------------------------------------------- every variant -> the exit ledger
rows = []
for v in range(nV):
    cfg = {k: V[v][k] for k in ("stop", "lots", "scale_out", "trail", "square_off", "time_stop_bars", "exit_on_choch_against")}
    mix = {r: round(float((RS[:, v] == k).mean()), 4) for k, r in enumerate(REASON_NAMES) if (RS[:, v] == k).any()}
    extra = dict(keys=V[v]["keys"], mean_per_position=round(float(NP[:, v].mean()), 2), lots=int(lots[v]), bars_held_mean=round(float((XB[:, v] - D.entry).mean()), 1), exit_mix=mix)
    rows.append(ledger("exit_policy/C", cfg, N[:, v], extra))
tab = pd.DataFrame([dict(v=i, **r["keys"], mean_per_lot=r["mean"], mean_per_position=r["mean_per_position"], diff_vs_fnd=r["diff"], t=r["t"], win_rate=r["win_rate"], pf=r["pf"],
                         random_pct=r["random_pct"], regret_free=r["regret_vs_oracle_free"], sign_blocks=r["sign_blocks"], bars_held=r["bars_held_mean"], id=r["id"], **{"mix_" + k: v_ for k, v_ in r["exit_mix"].items()})
                    for i, r in enumerate(rows)])
tab.to_csv(os.path.join(HERE, f"c_variants_{tf}.csv"), index=False)
means = N.mean(axis=0)
best_is = int(np.argmax(means))
print(f"{tf}: {nV} variants ledgered in {time.time() - t0:.0f}s; in-sample best {V[best_is]['keys']} mean per lot {means[best_is]:.1f} (Foundation {D.fnd_net.mean():.1f}); "
      f"variants above Foundation: {(means > D.fnd_net.mean()).sum()}", flush=True)
marg = {dim: tab.groupby(dim, dropna=False).mean_per_lot.agg(["mean", "max", "count"]).round(1).reset_index().to_dict("records") for dim in ("stop", "scale", "trail", "time_stop", "choch")}

# ---------------------------------------------------------------- nested selection: harness.purged_splits (12 folds)
oof = np.full(D.n, np.nan); oof_bar = np.full(D.n, -1); folds = []
for b, (tr, te) in enumerate(H.purged_splits(T)):
    trl, tel = local[tr], local[te]; assert (trl >= 0).all() and (tel >= 0).all()
    pick = int(np.argmax(N[trl].mean(axis=0)))
    oof[tel] = N[tel, pick]; oof_bar[tel] = XB[tel, pick]
    folds.append(dict(block=b, train_n=int(len(trl)), test_n=int(len(tel)), pick=V[pick]["keys"], pick_v=pick, train_mean=round(float(N[trl, pick].mean()), 2),
                      test_mean=round(float(N[tel, pick].mean()), 2), test_fnd_mean=round(float(D.fnd_net[tel].mean()), 2),
                      train_rank_of_foundation_like=None))
assert np.isfinite(oof).all()
nested = ledger("exit_policy/C_nested", dict(selection="argmax mean net per lot on the training fold of harness.purged_splits", folds=12), oof,
                dict(picks=[f["pick"] for f in folds]), note="learner C nested-CV pick (OOF)")
np.savez_compressed(os.path.join(HERE, f"c_pick_{tf}.npz"), nested_net=oof, nested_exit_bar=oof_bar, best_is_net=N[:, best_is], best_is_exit_bar=XB[:, best_is], best_is=best_is)
best_rec = ledger("exit_policy/C_best_is", dict(V[best_is]["keys"]), N[:, best_is], note="the in-sample best variant (a trial, never a candidate on its own)")

# ---------------------------------------------------------------- CPCV: 66 splits, the pick per split, 11 paths
oof_by = {}; picks66 = []
for tr, te, (a, b) in H.cpcv_splits(T):
    trl, tel = local[tr], local[te]
    pick = int(np.argmax(N[trl].mean(axis=0))); picks66.append(pick)
    oof_by[(a, b)] = N[tel, pick]
paths = H.cpcv_paths(T, oof_by)
pstats = []
for p, arr in enumerate(paths):
    pn = arr[D.is_idx]; d = pn - D.fnd_net
    pstats.append(dict(path=p, mean=round(float(pn.mean()), 2), diff=round(float(d.mean()), 2), random_pct=X.pct_rank(pn.mean(), rc_means),
                       sign_blocks=int(sum(1 for bb in range(H.N_BLOCKS) if (D.block == bb).any() and d[D.block == bb].mean() > 0))))
    ledger("exit_policy/C_nested/cpcv", dict(path=p), pn, note="CPCV path of learner C's per-split pick")
dd = np.array([s["diff"] for s in pstats])
cpcv = dict(paths=11, diff_median=round(float(np.median(dd)), 2), diff_p5=round(float(np.quantile(dd, 0.05)), 2), diff_min=round(float(dd.min()), 2),
            diff_share_positive=round(float((dd > 0).mean()), 3), mean_median=round(float(np.median([s["mean"] for s in pstats])), 2),
            distinct_picks=len(set(picks66)), picks=[dict(keys=V[k]["keys"], n_splits=int(sum(1 for q in picks66 if q == k))) for k in sorted(set(picks66))], per_path=pstats)

# ---------------------------------------------------------------- multiplicity over the family (all 1,568 variants)
vecs = [X.load_vec(r["id"]) for r in rows]
t1 = time.time()
pbo = H.pbo(vecs, "diff"); spa = H.spa(vecs, tag=f"exit|{tf}"); eff = H.effective_trials(vecs)
boot_best = H.bootstrap_ci(vecs[best_is], tag=f"exit|best|{tf}"); boot_nested = H.bootstrap_ci(X.load_vec(nested["id"]), tag=f"exit|nested|{tf}")
gain_best = H.selection_gain(vecs[best_is])[0]
dsr = H.deflated_sharpe(gain_best, nV, float(np.var([H.selection_gain(v)[0].mean() / (H.selection_gain(v)[0].std(ddof=1) or 1) for v in vecs])))
print(f"{tf}: multiplicity in {time.time() - t1:.0f}s: pbo {pbo['pbo']}, spa_p {spa['spa_p']}, rc_p {spa['rc_p']}, effective trials {eff}", flush=True)

# ---------------------------------------------------------------- comparators
st9 = next(i for i, v in enumerate(V) if v["keys"] == dict(stop=50, scale="L12", trail="3_1", time_stop=None, choch=False))
fnd = ledger("exit_policy/comparator", dict(exit="Foundation L1 (stop / next CHoCH / 15:25)"), D.fnd_net, note="the label itself: diff 0 by construction")
st9r = ledger("exit_policy/comparator", dict(exit="ST9 R-ladder", keys=V[st9]["keys"]), N[:, st9], dict(mean_per_position=round(float(NP[:, st9].mean()), 2), lots=3),
              note="tuned on 2026 = this study's OOS; not an OOS comparator")
orf = ledger("exit_policy/comparator", dict(exit="hindsight oracle, best close exit entry+1..cap, no stop"), of_net, note="upper bound")
orl = ledger("exit_policy/comparator", dict(exit="hindsight oracle on the extended trajectory (Foundation stop floor)"), fl_net, note="learner B's target")
ran = dict(draws=int(len(rc_means)), mean=round(float(rc_means.mean()), 2), p5=round(float(np.quantile(rc_means, .05)), 2), p50=round(float(np.median(rc_means)), 2),
           p95=round(float(np.quantile(rc_means, .95)), 2), foundation_pct=X.pct_rank(D.fnd_net.mean(), rc_means))
tests = {name: dict(blocks=X.sign_flip_blocks(net - D.fnd_net, D.block), sessions=X.sign_flip_sessions(net - D.fnd_net, D.session, tag=f"{tf}|{name}"))
         for name, net in (("C_nested", oof), ("C_best_is", N[:, best_is]), ("ST9", N[:, st9]))}

res = dict(tf=tf, n=int(D.n), active_sessions=int(len(set(D.session.tolist()))), variants=nV, seconds=round(time.time() - t0, 1),
           foundation=dict(id=fnd["id"], mean=fnd["mean"], random_pct=fnd["random_pct"], regret_free=fnd["regret_vs_oracle_free"], regret_floor=fnd["regret_vs_oracle_floor"]),
           st9=dict(id=st9r["id"], **{k: st9r[k] for k in ("mean", "mean_per_position", "diff", "t", "random_pct", "regret_vs_oracle_free", "sign_blocks", "win_rate", "pf")}),
           oracle_free=dict(id=orf["id"], mean=orf["mean"], random_pct=orf["random_pct"]), oracle_floor=dict(id=orl["id"], mean=orl["mean"], random_pct=orl["random_pct"]),
           random_control=ran, marginals=marg,
           best_is=dict(id=best_rec["id"], keys=V[best_is]["keys"], **{k: best_rec[k] for k in ("mean", "diff", "t", "random_pct", "regret_vs_oracle_free", "sign_blocks", "win_rate", "pf")},
                        variants_above_foundation=int((means > D.fnd_net.mean()).sum())),
           nested=dict(id=nested["id"], **{k: nested[k] for k in ("mean", "diff", "t", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor", "sign_blocks", "win_rate", "pf")}, folds=folds),
           cpcv=cpcv, pbo=pbo, spa=spa, effective_trials=eff, dsr_best=dsr, bootstrap_best=boot_best, bootstrap_nested=boot_nested, sign_flip=tests,
           top10=tab.sort_values("mean_per_lot", ascending=False).head(10).to_dict("records"))
json.dump(res, open(os.path.join(HERE, f"c_select_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print(json.dumps({k: res[k] for k in ("foundation", "st9", "best_is", "random_control", "cpcv", "pbo", "spa", "effective_trials", "bootstrap_nested")}, indent=1, default=str)[:6000])
print(f"{tf}: nested pick mean {nested['mean']} diff {nested['diff']} random pct {nested['random_pct']}; sign-flip blocks p1 {tests['C_nested']['blocks']['p_one_sided']}; done in {time.time() - t0:.0f}s")
