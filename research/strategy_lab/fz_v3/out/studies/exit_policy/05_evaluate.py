"""Evaluation on IS CV (one timeframe per run): the table of exit policies on the same frozen entries, all cut at 15:25 —
Foundation L1 exit, ST9 R-ladder, learner C's nested-CV pick (and the in-sample best as a trial), learner B, learner A (when
run), the hindsight oracles and the random-exit control — with the exit regret, the random-exit percentile, the paired
session-block sign-flip test against the Foundation exit and the block bootstrap CI. Then the distillation of the best
learner's decisions into a depth-3 tree -> 'exit_rules' JSON (fidelity reported), and the multiplication with the frozen
ST7/ST8 gate (the exit applied to the fz_traded rows), scored through harness.score under the exit's label
(Table.with_label) so the gate x exit book is a harness ledger row.
Outputs: eval_table_<tf>.csv, eval_<tf>.json, exit_rules_<tf>.json."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
import exlib as X, harness as H

tf = sys.argv[1]
t0 = time.time()
D = X.Data(tf); T = D.T
ctrl = np.load(os.path.join(HERE, f"controls_{tf}.npz")); rc = ctrl["rc_means"]
of_net, fl_net = ctrl["oracle_free_net"], ctrl["oracle_floor_net"]; J = ctrl["J"]
csel = json.load(open(os.path.join(HERE, f"c_select_{tf}.json"))); cpick = np.load(os.path.join(HERE, f"c_pick_{tf}.npz"))
V = json.load(open(os.path.join(HERE, "c_variants.json")))
G = np.load(os.path.join(HERE, f"c_grid_{tf}.npz")); N = G["net_pos"] / G["lots"]
st9 = next(i for i, v in enumerate(V) if v["keys"] == dict(stop=50, scale="L12", trail="3_1", time_stop=None, choch=False))
policies = {"Foundation L1 exit (stop / next CHoCH / 15:25)": (D.fnd_net, D.fnd_exit, None),
            "ST9 R-ladder (3 lots, stop 50, 1R/2R, trail 3R lag 1) per lot": (N[:, st9], G["exit_bar"][:, st9], "tuned on 2026 = OOS; per position x3"),
            "C nested-CV pick (OOF)": (cpick["nested_net"], cpick["nested_exit_bar"], "picks: " + "; ".join(sorted({json.dumps(f["pick"]) for f in csel["nested"]["folds"]}))),
            "C in-sample best (a trial)": (cpick["best_is_net"], cpick["best_is_exit_bar"], json.dumps(V[int(cpick["best_is"])]["keys"]))}
learners = {"C": cpick["nested_net"]}
extra = {}
for name, key in (("B hindsight imitation (OOF)", "b"), ("A FQI pessimistic ensemble (OOF)", "a")):
    p = os.path.join(HERE, f"{key}_oof_{tf}.npz")
    if os.path.exists(p):
        z = np.load(p); policies[name] = (z["net"], z["exit_bar"], None); learners[key.upper()] = z["net"]; extra[key.upper()] = z
policies["hindsight oracle, best close exit, no stop (upper bound)"] = (of_net, ctrl["oracle_free_bar"], None)
policies["hindsight oracle on the Foundation-stop trajectory"] = (fl_net, ctrl["oracle_floor_bar"], None)

rows = []
for name, (net, xb, note) in policies.items():
    d = net - D.fnd_net; s = X.summary(D, net)
    r = dict(policy=name, mean_per_lot=s["mean"], diff_vs_foundation=s["diff"], t=s["t"], random_pct=X.pct_rank(net.mean(), rc), regret_vs_oracle_free=round(float(of_net.mean() - net.mean()), 2),
             regret_vs_oracle_floor=round(float(fl_net.mean() - net.mean()), 2), win_rate=s["win_rate"], pf=s["pf"], mean_per_session=s["mean_per_session"], sign_blocks=s["sign_blocks"],
             bars_held_mean=round(float((xb - D.entry).mean()), 1), note=note)
    if np.abs(d).sum() > 0:
        sb = X.sign_flip_blocks(d, D.block); ss = X.sign_flip_sessions(d, D.session, tag=f"{tf}|eval|{name}")
        b = H.bootstrap_ci(X.session_vectors(D, net), tag=f"eval|{tf}|{name}")
        top = np.quantile(d, 0.99)                                        # the 1% of trades where the policy gained most over the Foundation exit
        r.update(signflip_blocks_p1=sb["p_one_sided"], signflip_blocks_p2=sb["p_two_sided"], blocks_positive=sb["blocks_positive"], signflip_sessions_p1=ss["p_one_sided"],
                 signflip_sessions_p2=ss["p_two_sided"], boot_diff_ci90=b["diff_ci"], boot_diff_p_le0=b["diff_p_le0"],
                 diff_top1_gains_removed=round(float(d[d < top].mean()), 2), diff_top1_winners_removed=round(float(d[net < np.quantile(net, 0.99)].mean()), 2),
                 mean_slip8=round(float(net.mean() - 2 * 3.0 * X.LOT * (3 if "ladder" in name else 1) / (3 if "ladder" in name else 1)), 2))
    rows.append(r)
rows.append(dict(policy="random exit (2,000 draws): mean of means", mean_per_lot=round(float(rc.mean()), 2), diff_vs_foundation=round(float(rc.mean() - D.fnd_net.mean()), 2),
                 random_pct=50.0, regret_vs_oracle_free=round(float(of_net.mean() - rc.mean()), 2), regret_vs_oracle_floor=round(float(fl_net.mean() - rc.mean()), 2),
                 note=f"p5 {np.quantile(rc, .05):.1f}, p95 {np.quantile(rc, .95):.1f}"))
tab = pd.DataFrame(rows); tab.to_csv(os.path.join(HERE, f"eval_table_{tf}.csv"), index=False)
print(tab[["policy", "mean_per_lot", "diff_vs_foundation", "random_pct", "regret_vs_oracle_free", "signflip_blocks_p1", "boot_diff_ci90"]].to_string(), flush=True)

# effective trials of the family on the selection-gain series (variant minus Foundation per session), beside the harness's kept_sum figure
fam = X.read_exit_ledger("exit_policy/C", tf)
gains = np.array([H.selection_gain(X.load_vec(r["id"]))[0] for r in fam])
Cm = np.corrcoef(gains[:, gains.std(axis=0) > 0]); Cm = np.nan_to_num(Cm); np.fill_diagonal(Cm, 1.0)
lam = np.clip(np.linalg.eigvalsh(Cm), 0, None); eff_gain = round(float(lam.sum() ** 2 / (lam ** 2).sum()), 2)
distinct = len({tuple(np.round(g, 6)) for g in gains})

# ---------------------------------------------------------------- distillation of the best learner
best = max(learners, key=lambda k: learners[k].mean())
Jf, hit, fill = X.floor(D)
S, trade, bar, xpx, term, snet = X.states(D, Jf, hit, fill)
starts, ends = X.segments(trade, D.n)
if best == "C":
    xb = cpick["nested_exit_bar"]
    visited = np.zeros(len(S), dtype=bool); decision = np.zeros(len(S), dtype=bool)
    for j in range(D.n):
        last = min(int(xb[j]), int(Jf[j])); r = starts[j] + (last - D.entry[j] - 1)
        visited[starts[j]:r + 1] = True; decision[r] = xb[j] < Jf[j]
else:
    z = extra[best]; visited, decision = z["visited"].astype(bool), z["decision"].astype(bool)
vis = np.flatnonzero(visited & ~term)
dist = dict(best_learner=best, best_learner_oof_mean=round(float(learners[best].mean()), 2), visited_decision_states=int(len(vis)), exit_decisions=int(decision[vis].sum()))
rules = []
if decision[vis].sum() >= 20:
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=max(50, len(vis) // 200), class_weight="balanced", random_state=3).fit(S[vis], decision[vis])
    pred = tree.predict(S[vis])
    tp = int((pred & decision[vis]).sum()); dist.update(fidelity_accuracy=round(float((pred == decision[vis]).mean()), 4),
        fidelity_exit_recall=round(float(tp / max(1, decision[vis].sum())), 4), fidelity_exit_precision=round(float(tp / max(1, pred.sum())), 4))
    t_ = tree.tree_; feat = X.STATE_COLS
    def walk(node, conds):
        if t_.children_left[node] == -1:
            if tree.classes_[np.argmax(t_.value[node][0])]:
                rules.append(dict(**{"if": {f: [op, round(float(th), 4)] for f, op, th in conds}}, then="exit_all", support=int(t_.n_node_samples[node]),
                                  exit_share=round(float(t_.value[node][0][1] / t_.value[node][0].sum()), 3)))
            return
        f = feat[t_.feature[node]]; th = t_.threshold[node]
        walk(t_.children_left[node], conds + [(f, "<=", th)]); walk(t_.children_right[node], conds + [(f, ">", th)])
    walk(0, [])
    rules = sorted(rules, key=lambda r: -r["support"])[:6]
    # the distilled policy replayed on the IS trajectories (in-sample for the tree)
    flag = np.zeros(len(S), dtype=bool); flag[vis] = tree.predict(S[vis]) if len(vis) else False
    js, dnet, dxb, _ = X.first_exit_policy(starts, ends, flag, snet, bar, np.ones(D.n, dtype=bool))
    dist.update(distilled_policy_is_mean=round(float(dnet.mean()), 2), distilled_policy_diff_vs_foundation=round(float((dnet - D.fnd_net).mean()), 2),
                distilled_policy_random_pct=X.pct_rank(dnet.mean(), rc), distilled_early_exit_share=round(float((dxb < Jf).mean()), 4), rules_n=len(rules))
else:
    dist["note"] = "the best learner exits early on fewer than 20 visited states: nothing to distil (the policy is 'hold to the stop / 15:25')"
exit_rules = dict(tf=tf, best_learner=best, exit_rules=rules, fields_per_bar=X.STATE_COLS, shippable_form_learner_C=csel["nested"]["folds"][0]["pick"] if best == "C" else None,
                  note="a new key type (a per-bar rule evaluator): a user decision; learner C's keys {stop, scale_out, trail, square_off, time_stop_bars, exit_on_choch_against} are the shippable form",
                  provenance=dict(source="learned on IS 2021-10..2025-12", script=os.path.basename(__file__), statistic=dist))
json.dump(exit_rules, open(os.path.join(HERE, f"exit_rules_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))

# ---------------------------------------------------------------- multiplication with the frozen ST7/ST8 gate
gate = T.F.fz_traded.astype(bool).to_numpy()
mult = {}
for name, net in (("C_nested", cpick["nested_net"]), *[(k, v) for k, v in learners.items() if k != "C"]):
    net_all = T.net.copy(); xb_all = T.exit_bar.copy()
    net_all[D.is_idx] = net                                                 # IS rows take the exit policy's OOF net; OOS rows are untouched copies
    xb_all[D.is_idx] = (cpick["nested_exit_bar"] if name == "C_nested" else extra[name]["exit_bar"])
    T2 = T.with_label(f"L1entries_x_{name}", net_all, xb_all)
    res = H.score(T2, gate, "exit_policy/gate_x_exit", dict(gate="ST7/ST8 as traded (fz_traded)", exit=name, note="exit applied to every IS unit; the gate's kept set is judged under it"), script=__file__)
    g = gate[D.is_idx]
    d = net[g] - D.fnd_net[g]
    mult[name] = dict(harness_id=res["id"], kept_n=res["kept_n"], kept_mean=res["kept_mean"], skipped_mean=res["skipped_mean"], diff=res["diff"], control_pct=res["control_pct"], perm_p=res["perm_p"],
                      sign_blocks=res["sign_blocks"], kept_mean_slip8=res["kept_mean_slip8"], winner_recall_weighted=res["winner_recall_weighted"],
                      gate_rows=dict(n=int(g.sum()), foundation_mean=round(float(D.fnd_net[g].mean()), 2), exit_mean=round(float(net[g].mean()), 2), diff=round(float(d.mean()), 2),
                                     signflip_blocks=X.sign_flip_blocks(d, D.block[g]), signflip_sessions=X.sign_flip_sessions(d, D.session[g], tag=f"{tf}|gate|{name}"),
                                     boot=H.bootstrap_ci(X.session_vectors(D, net, mask=g), tag=f"gate|{tf}|{name}"),
                                     book_net_foundation=round(float(D.fnd_net[g].sum()), 2), book_net_exit=round(float(net[g].sum()), 2)),
                      non_gate_rows=dict(n=int((~g).sum()), foundation_mean=round(float(D.fnd_net[~g].mean()), 2), exit_mean=round(float(net[~g].mean()), 2)))
frozen_l1 = [r for r in H.read_ledger("selftest/frozen_gate", tf) + H.read_ledger("comparator", tf) if r.get("label") == "L1"]
out = dict(tf=tf, n=int(D.n), table=rows, effective_trials_kept_sum=csel["effective_trials"], effective_trials_selection_gain=eff_gain, distinct_gain_vectors=distinct,
           distillation=dist, exit_rules=rules, gate_multiplication=mult,
           frozen_gate_under_L1=[dict(id=r["id"], kept_n=r["kept_n"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"], control_pct=r["control_pct"]) for r in frozen_l1[:1]],
           seconds=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(HERE, f"eval_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print(json.dumps(dict(distillation=dist, rules=rules, gate=mult, eff_gain=eff_gain, distinct=distinct), indent=1, default=str)[:5000])
