"""Evaluation on IS CV (one timeframe per run): the table of exit policies on the same frozen entries, all cut at 15:25 —
Foundation L1 exit, ST9 R-ladder, learner C's nested-CV pick (and the in-sample best as a trial), learner B, learner A (when
run), the hindsight oracles and the random-exit control — with the exit regret, the random-exit percentile, the paired
session-block sign-flip test against the Foundation exit and the block bootstrap CI. Then the distillation of the best
learner's decisions into a depth-3 tree -> 'exit_rules' JSON (fidelity reported), and the multiplication with the frozen
ST7/ST8 gate (the exit applied to the fz_traded rows), scored through harness.score under the exit's label
(Table.with_label) so the gate x exit book is a harness ledger row.
Follow-up (2026-09-29 16:45 IST): the family SPA is recomputed here with the current harness.spa (near-degenerate candidates
excluded from the studentised family, White's unstudentised statistic reported too; the excluded candidates are listed), over the
same 1,568-variant family and bootstrap tag 02_c_select.py used, and over every exit trial of the timeframe; a gate x exit row
already in the harness ledger is reused by id, a new one is appended with note="followup".
REPAIR (2026-09-29, refuters' material issues): (1) the family holds near-duplicates of the benchmark (stop foundation / no target /
no trail / CHoCH-against on, with and without a 120-bar time stop): the CHoCH-against cut is the engine's own next-CHoCH exit, so
they reproduce the Foundation L1 exit on all but a few trades, and their selection gain was non-zero in every session only because the
variant net is lab.price_trade's unrounded value while the label l1_net_inr is 2 dp (|gain| <= 0.005 INR of rounding noise per
session) — harness.spa's 1e-9 activity rule excluded nothing. Fix (harness.py untouched): the family's vectors are rebuilt from the
per-trade nets rounded to 2 dp, the label's own precision, so a duplicate has an exactly-zero gain wherever it agrees with the label and
the min-active rule applies as designed; `spa_family` / `spa_all_trials` are the repaired blocks (the pass-rule items), `*_as_coded` the
stored-vector ones, a material-tolerance check (|gain| > 0.01 INR) and the near-duplicate diagnostics (differing trades, active sessions
per tolerance, argmax share of the null draws) are written beside them. (2) each statistic appears once: the table's block-bootstrap CI
and session sign-flip reuse the seed tag under which the statistic was first reported (02_c_select.py: bootstrap `exit|nested|<tf>` /
`exit|best|<tf>`, sign-flip `<tf>|C_nested` / `<tf>|C_best_is` / `<tf>|ST9`; 03_b / 04_a: sign-flip `<tf>|B` / `<tf>|A`), so the section 6
table and sections 3-5 / 9 carry the same Monte-Carlo estimate; a statistic no earlier stage reported (the oracles, the bootstrap CI of
ST9 / A / B) keeps the eval tag (`boot_tag` / `flip_tag` columns). (3) the top-1% item: both definitions are computed — the harness's
pre-registered `diff_top1_removed` analogue (top 1% winners by the policy's net removed: `diff_top1_winners_removed`, the pass-rule
item) and the study's post-hoc `diff_top1_gains_removed` (top 1% of per-trade gains removed; negative-biased by construction) with its
zero-mean reference (the same trim on the centred difference) and the trades' contribution to the mean gain.
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
# REPAIR (issue 2): the seed tags under which each policy's bootstrap CI / session sign-flip was first reported (02_c_select.py, 03_b_imitation.py,
# 04_a_fqi.py) are reused here, so the statistic appears once in FINDINGS instead of as two Monte-Carlo estimates under two tags.
OWN_TAGS = {"C nested-CV pick (OOF)": dict(boot=f"exit|nested|{tf}", flip=f"{tf}|C_nested"),
            "C in-sample best (a trial)": dict(boot=f"exit|best|{tf}", flip=f"{tf}|C_best_is"),
            "ST9 R-ladder (3 lots, stop 50, 1R/2R, trail 3R lag 1) per lot": dict(flip=f"{tf}|ST9"),
            "B hindsight imitation (OOF)": dict(flip=f"{tf}|B"), "A FQI pessimistic ensemble (OOF)": dict(flip=f"{tf}|A")}

rows = []
for name, (net, xb, note) in policies.items():
    d = net - D.fnd_net; s = X.summary(D, net)
    r = dict(policy=name, mean_per_lot=s["mean"], diff_vs_foundation=s["diff"], t=s["t"], random_pct=X.pct_rank(net.mean(), rc), regret_vs_oracle_free=round(float(of_net.mean() - net.mean()), 2),
             regret_vs_oracle_floor=round(float(fl_net.mean() - net.mean()), 2), win_rate=s["win_rate"], pf=s["pf"], mean_per_session=s["mean_per_session"], sign_blocks=s["sign_blocks"],
             bars_held_mean=round(float((xb - D.entry).mean()), 1), note=note)
    if np.abs(d).sum() > 0:
        own = OWN_TAGS.get(name, {}); flip_tag = own.get("flip", f"{tf}|eval|{name}"); boot_tag = own.get("boot", f"eval|{tf}|{name}")
        sb = X.sign_flip_blocks(d, D.block); ss = X.sign_flip_sessions(d, D.session, tag=flip_tag)
        b = H.bootstrap_ci(X.session_vectors(D, net), tag=boot_tag)
        r.update(boot_tag=boot_tag, flip_tag=flip_tag)
        # two top-1% definitions (repair): the harness's pre-registered GO item removes the top 1% WINNERS by net (here: the trades whose
        # policy net is in its own top 1%) — `diff_top1_winners_removed`, the pass-rule item; the study's earlier `diff_top1_gains_removed`
        # removes the top 1% of the per-trade GAIN d itself, which is negative-biased by construction (removing the largest values of a
        # dispersed difference lowers its mean even at zero true mean): its zero-mean reference is the same trim applied to d - mean(d).
        top = np.quantile(d, 0.99); keep_g = d < top                         # the 1% of trades where the policy gained most over the Foundation exit
        dz = d - d.mean(); topz = np.quantile(dz, 0.99)
        lo1, hi1 = np.quantile(d, 0.01), np.quantile(d, 0.99)
        r.update(signflip_blocks_p1=sb["p_one_sided"], signflip_blocks_p2=sb["p_two_sided"], blocks_positive=sb["blocks_positive"], signflip_sessions_p1=ss["p_one_sided"],
                 signflip_sessions_p2=ss["p_two_sided"], boot_diff_ci90=b["diff_ci"], boot_diff_p_le0=b["diff_p_le0"],
                 diff_top1_winners_removed=round(float(d[net < np.quantile(net, 0.99)].mean()), 2),
                 diff_top1_gains_removed=round(float(d[keep_g].mean()), 2), diff_top1_gains_removed_zero_mean_ref=round(float(dz[dz < topz].mean()), 2),
                 top1_gains_n=int((~keep_g).sum()), top1_gains_mean=round(float(d[~keep_g].mean()), 2) if (~keep_g).any() else None,
                 top1_gains_contribution_per_trade=round(float(d[~keep_g].sum() / len(d)), 2), rest_mean_gain=round(float(d[keep_g].mean()), 2),
                 diff_both_1pct_tails_trimmed=round(float(d[(d > lo1) & (d < hi1)].mean()), 2),
                 mean_slip8=round(float(net.mean() - 2 * 3.0 * X.LOT * (3 if "ladder" in name else 1) / (3 if "ladder" in name else 1)), 2))
    rows.append(r)
rows.append(dict(policy="random exit (2,000 draws): mean of means", mean_per_lot=round(float(rc.mean()), 2), diff_vs_foundation=round(float(rc.mean() - D.fnd_net.mean()), 2),
                 random_pct=50.0, regret_vs_oracle_free=round(float(of_net.mean() - rc.mean()), 2), regret_vs_oracle_floor=round(float(fl_net.mean() - rc.mean()), 2),
                 note=f"p5 {np.quantile(rc, .05):.1f}, p95 {np.quantile(rc, .95):.1f}"))
tab = pd.DataFrame(rows); tab.to_csv(os.path.join(HERE, f"eval_table_{tf}.csv"), index=False)
print(tab[["policy", "mean_per_lot", "diff_vs_foundation", "random_pct", "regret_vs_oracle_free", "signflip_blocks_p1", "boot_diff_ci90"]].to_string(), flush=True)

# effective trials of the family on the selection-gain series (variant minus Foundation per session), beside the harness's kept_sum figure
fam = X.read_exit_ledger("exit_policy/C", tf)
fam_vecs = [X.load_vec(r["id"]) for r in fam]
gains = np.array([H.selection_gain(v)[0] for v in fam_vecs])
Cm = np.corrcoef(gains[:, gains.std(axis=0) > 0]); Cm = np.nan_to_num(Cm); np.fill_diagonal(Cm, 1.0)
lam = np.clip(np.linalg.eigvalsh(Cm), 0, None); eff_gain = round(float(lam.sum() ** 2 / (lam ** 2).sum()), 2)
distinct = len({tuple(np.round(g, 6)) for g in gains})

# ---------------------------------------------------------------- family SPA with the current harness.spa (follow-up 2026-09-29 16:45 IST)
# 02_c_select.py computed the family SPA with the earlier harness.spa; the harness now excludes near-degenerate candidates (selection
# gain non-zero in fewer than max(10, 5% of T) sessions) from the studentised family and reports White's unstudentised statistic too.
# Same family (the 1,568 learner C variants, ledger order), same bootstrap tag as 02_c_select.py, so only the harness revision changes.
# REPAIR (2026-09-29): the stored vectors carry the variant net at lab.price_trade's full precision while the label l1_net_inr is 2 dp, so
# a variant that reproduces the Foundation exit has |gain| <= 0.0049 in every session and harness.spa's 1e-9 activity rule (a
# duplicate-of-the-benchmark guard) excluded nothing. The family's vectors are rebuilt here from the per-trade nets rounded to 2 dp (the
# label's own precision): where the variant equals the label the gain is exactly 0 and the harness's min-active rule applies as designed.
# harness.py is not modified (outside this study's scope); the as-coded statistics stay beside the repaired ones.
VKEY = {json.dumps(v["keys"], sort_keys=True): i for i, v in enumerate(V)}
def net_of_row(r):
    """The per-trade net (per lot) behind an exit-ledger row, from the study's own output files (the same arrays that built its vector)."""
    f = r["family"]
    if f == "exit_policy/C": return N[:, VKEY[json.dumps(r["keys"], sort_keys=True)]]
    if f == "exit_policy/C_nested": return cpick["nested_net"]
    if f == "exit_policy/C_best_is": return cpick["best_is_net"]
    if f in ("exit_policy/B", "exit_policy/A"): return extra[f[-1]]["net"]
    raise KeyError(f)


def first_choch_against(D_):
    """Bar of the first CHoCH against the position after entry (events with i > entry), or -1."""
    out = np.full(D_.n, -1, dtype=int)
    for j in range(D_.n):
        arr = D_.choch_dn if D_.sg[j] > 0 else D_.choch_up
        k = np.searchsorted(arr, D_.entry[j], side="right")
        if k < len(arr): out[j] = int(arr[k])
    return out


def null_argmax_counts(vecs_, tag_, ok):
    """Diagnostic replica of harness.spa's studentised bootstrap null (same draws via the same tag): how often each candidate is the
    argmax of the null statistic. Read-only mirror of harness.spa lines 481-502; never a p-value source."""
    Dm = np.array([H.selection_gain(v)[0] for v in vecs_], dtype=float); M, T_ = Dm.shape
    mu = Dm.mean(axis=1); idx = H.stationary_bootstrap_idx(T_, H.BOOT_DRAWS, tag=tag_)
    thr = np.sqrt(np.var(Dm, axis=1, ddof=1) / T_ * 2 * np.log(np.log(T_))); mu_c = np.where(mu < -thr, mu, 0.0)
    counts = np.zeros(M, dtype=int)
    for dr in range(idx.shape[0]):
        sub = Dm[:, idx[dr]]; mub = sub.mean(axis=1); sdb = sub.std(axis=1, ddof=1) + 1e-12
        counts[int(np.argmax(np.where(ok, np.sqrt(T_) * (mub - mu + mu_c) / sdb, -np.inf)))] += 1
    return counts


def spa_block(rows_, vecs_, tag_, label_, precision):
    sp = H.spa(vecs_, tag=tag_)
    Dm = np.array([H.selection_gain(v)[0] for v in vecs_]); T_ = Dm.shape[1]
    active = (np.abs(Dm) > 1e-9).sum(axis=1); active01 = (np.abs(Dm) > 0.01).sum(axis=1); active50 = (np.abs(Dm) > 0.5).sum(axis=1)
    mu = Dm.mean(axis=1); sd = Dm.std(axis=1, ddof=1) + 1e-12
    def who(i):
        r = rows_[i]
        return dict(index=int(i), id=r["id"], family=r["family"], keys=r.get("keys") or r.get("config"), active_sessions=int(active[i]), active_sessions_gt_0_01=int(active01[i]),
                    active_sessions_gt_0_5=int(active50[i]), mean_gain=round(float(mu[i]), 2), t_studentised=round(float(np.sqrt(T_) * mu[i] / sd[i]), 3), diff_vs_foundation=r.get("diff"))
    excluded = [who(i) for i in np.flatnonzero(active < sp["min_active_sessions"])]
    return dict(family=label_, vector_precision=precision, harness_sha=H.file_sha(H.__file__), tag=tag_, **sp, best_keys=who(sp["best"]) if sp.get("best") is not None else None,
                best_keys_unstudentised=who(sp["best_unstudentised"]), excluded_candidates=excluded), Dm, active01


def spa_family_repaired(rows_, vecs_, tag_, label_):
    """The as-coded block (stored vectors), the repaired block (vectors from the nets rounded to 2 dp, the label's precision), the
    material-tolerance check (candidates with fewer than min_active sessions of |gain| > 0.01 INR dropped from the list before
    harness.spa: they leave both statistics' families there, unlike the harness's own rule) and the near-duplicate diagnostics."""
    as_coded, Dm, active01 = spa_block(rows_, vecs_, tag_, label_, "as stored in vectors/*.npz (variant net unrounded, label 2 dp)")
    nets = [net_of_row(r) for r in rows_]
    # the mapping row -> per-trade net is proved against the stored vector before it is used
    rebuilt = [X.session_vectors(D, nt) for nt in nets]
    mapping_ok = all(np.array_equal(a["sessions"], b["sessions"]) and np.allclose(a["kept_sum"], b["kept_sum"], rtol=0, atol=1e-6) and np.array_equal(a["kept_n"], b["kept_n"])
                     for a, b in zip(rebuilt, vecs_))
    assert mapping_ok, "row -> net mapping does not reproduce the stored vectors"
    vecs2 = [X.session_vectors(D, np.round(nt, 2)) for nt in nets]
    repaired, Dm2, _ = spa_block(rows_, vecs2, tag_, label_, "per-trade nets rounded to 2 dp before the session sums (the label's precision)")
    min_active = as_coded["min_active_sessions"]
    keep = active01 >= min_active
    tol = H.spa([v for v, k in zip(vecs_, keep) if k], tag=tag_)
    kept_idx = np.flatnonzero(keep)
    tol_block = dict(rule="candidates with fewer than min_active sessions of |gain| > 0.01 INR removed from the list (both statistics)", tolerance_inr=0.01, min_active_sessions=int(min_active),
                     excluded=int((~keep).sum()), excluded_indices=[int(i) for i in np.flatnonzero(~keep)], candidates=int(keep.sum()), spa_p=tol["spa_p"], rc_p=tol["rc_p"],
                     best_index=int(kept_idx[tol["best"]]) if tol.get("best") is not None else None, best_mean_gain=tol.get("best_mean_gain"), best_t=tol.get("best_t"),
                     spa_p_unstudentised=tol["spa_p_unstudentised"], rc_p_unstudentised=tol["rc_p_unstudentised"], best_index_unstudentised=int(kept_idx[tol["best_unstudentised"]]))
    # near-duplicates of the benchmark: the candidates the repaired rule excludes (and any the tolerance check excludes)
    dup_idx = sorted(set(e["index"] for e in repaired["excluded_candidates"]) | set(tol_block["excluded_indices"]))
    ok_all = np.ones(len(vecs_), dtype=bool)
    counts = null_argmax_counts(vecs_, tag_, ok_all) if dup_idx else None
    dups = []
    for i in dup_idx:
        nt = nets[i]; dd = np.abs(nt - D.fnd_net); differing = dd > 0.005
        e = next((x for x in repaired["excluded_candidates"] if x["index"] == i), None)
        xb_row = G["exit_bar"][:, VKEY[json.dumps(rows_[i]["keys"], sort_keys=True)]] if rows_[i]["family"] == "exit_policy/C" else None
        dups.append(dict(index=int(i), id=rows_[i]["id"], family=rows_[i]["family"], keys=rows_[i].get("keys") or rows_[i].get("config"),
                         trades_differing_from_L1_gt_0_005=int(differing.sum()), trades=int(len(nt)), max_abs_diff_on_agreeing_trades=round(float(dd[~differing].max()), 4) if (~differing).any() else None,
                         mean_diff_on_differing_trades=round(float((nt - D.fnd_net)[differing].mean()), 2) if differing.any() else None,
                         exit_bar_equals_L1_share=round(float((xb_row == D.fnd_exit).mean()), 4) if xb_row is not None else None,
                         sessions_active_gt_1e_9=int((np.abs(Dm[i]) > 1e-9).sum()), sessions_active_gt_0_01=int((np.abs(Dm[i]) > 0.01).sum()), sessions_active_gt_0_5=int((np.abs(Dm[i]) > 0.5).sum()),
                         sessions_active_after_2dp=int((np.abs(Dm2[i]) > 1e-9).sum()), max_abs_gain_as_coded=round(float(np.abs(Dm[i]).max()), 4),
                         mean_gain_as_coded=round(float(Dm[i].mean()), 4), t_studentised_as_coded=round(float(np.sqrt(Dm.shape[1]) * Dm[i].mean() / (Dm[i].std(ddof=1) + 1e-12)), 3),
                         null_argmax_draws_as_coded=int(counts[i]), null_draws=int(H.BOOT_DRAWS),
                         excluded_by_repaired_rule=e is not None, excluded_by_tolerance_check=bool(i in tol_block["excluded_indices"])))
    return dict(as_coded=as_coded, repaired=repaired, tolerance_check=tol_block, near_duplicates=dups, vector_mapping_verified=bool(mapping_ok),
                null_argmax_top5_as_coded=[dict(index=int(i), draws=int(counts[i]), keys=rows_[i].get("keys") or rows_[i].get("config")) for i in np.argsort(-counts)[:5]] if counts is not None else None)


# why the duplicates exist: the L1 next-CHoCH exit is the close of the first CHoCH-against bar, i.e. exactly the CHoCH-against cut
fca = first_choch_against(D); m_nc = D.l1_reason == "next_choch"
l1_choch_facts = dict(next_choch_exits=int(m_nc.sum()), exit_px_equals_close_of_exit_bar_share=round(float((np.abs(D.l1_px[m_nc] - D.c[D.fnd_exit[m_nc]]) < 1e-9).mean()), 4),
                      exit_bar_equals_first_choch_against_share=round(float((D.fnd_exit[m_nc] == fca[m_nc]).mean()), 4),
                      l1_net_inr_decimals_gt_2=int((np.abs(D.fnd_net * 100 - np.round(D.fnd_net * 100)) > 1e-6).sum()),
                      grid_nets_decimals_gt_2=int((np.abs(N * 100 - np.round(N * 100)) > 1e-6).sum()), grid_cells=int(N.size))
SPA_C = spa_family_repaired(fam, fam_vecs, f"exit|{tf}", "learner C grid, 1568 variants (the pre-registered family of 02_c_select.py)")
spa_c = SPA_C["repaired"]
all_rows = [r for r in X.read_exit_ledger("exit_policy", tf) if r["family"] in ("exit_policy/C", "exit_policy/C_nested", "exit_policy/C_best_is", "exit_policy/B", "exit_policy/A")]
all_vecs = [X.load_vec(r["id"]) for r in all_rows]
SPA_ALL = spa_family_repaired(all_rows, all_vecs, f"exit|all|{tf}", f"every exit trial of the timeframe: {len(all_rows)} rows (C variants + C nested pick + C in-sample best + learners B and A); comparators and CPCV paths excluded")
spa_all = SPA_ALL["repaired"]
print(json.dumps(dict(l1_choch_facts=l1_choch_facts, spa_family_C_as_coded={k: v for k, v in SPA_C["as_coded"].items() if k != "excluded_candidates"},
                      spa_family_C_repaired={k: v for k, v in spa_c.items() if k != "excluded_candidates"}, excluded_repaired=spa_c["excluded_candidates"],
                      tolerance_check=SPA_C["tolerance_check"], near_duplicates=SPA_C["near_duplicates"], null_argmax_top5=SPA_C["null_argmax_top5_as_coded"],
                      spa_all_trials_as_coded={k: v for k, v in SPA_ALL["as_coded"].items() if k != "excluded_candidates"},
                      spa_all_trials_repaired={k: v for k, v in spa_all.items() if k != "excluded_candidates"}, all_tolerance_check=SPA_ALL["tolerance_check"]), indent=1, default=str), flush=True)
json.dump(dict(tf=tf, l1_choch_facts=l1_choch_facts, family_C=SPA_C, all_trials=SPA_ALL), open(os.path.join(HERE, f"spa_repair_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))

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
# the harness ledger is append-only: a (family, config, label, tf) already scored is reused by its id (same deterministic numbers), a new
# one is appended with note="followup" (the follow-up of 2026-09-29 16:45 IST: learner A on 1 min, the whole 5 min evaluation)
existing = {r["id"]: r for r in H.read_ledger("exit_policy/gate_x_exit", tf)}
GATE_FAMILY = "exit_policy/gate_x_exit"
for name, net in (("C_nested", cpick["nested_net"]), *[(k, v) for k, v in learners.items() if k != "C"]):
    net_all = T.net.copy(); xb_all = T.exit_bar.copy()
    net_all[D.is_idx] = net                                                 # IS rows take the exit policy's OOF net; OOS rows are untouched copies
    xb_all[D.is_idx] = (cpick["nested_exit_bar"] if name == "C_nested" else extra[name]["exit_bar"])
    T2 = T.with_label(f"L1entries_x_{name}", net_all, xb_all)
    cfg = dict(gate="ST7/ST8 as traded (fz_traded)", exit=name, note="exit applied to every IS unit; the gate's kept set is judged under it")
    cid = H.candidate_id(GATE_FAMILY, cfg, T2.label, T2.tf)
    if cid in existing:
        res = existing[cid]; ledger_row = "existing row reused (scored " + str(res.get("at")) + ")"
    else:
        res = H.score(T2, gate, GATE_FAMILY, cfg, script=__file__, note="followup"); ledger_row = "new row, note=followup"
    g = gate[D.is_idx]
    d = net[g] - D.fnd_net[g]
    mult[name] = dict(harness_id=res["id"], ledger_row=ledger_row, kept_n=res["kept_n"], kept_mean=res["kept_mean"], skipped_mean=res["skipped_mean"], diff=res["diff"], control_pct=res["control_pct"], perm_p=res["perm_p"],
                      sign_blocks=res["sign_blocks"], kept_mean_slip8=res["kept_mean_slip8"], winner_recall_weighted=res["winner_recall_weighted"],
                      gate_rows=dict(n=int(g.sum()), foundation_mean=round(float(D.fnd_net[g].mean()), 2), exit_mean=round(float(net[g].mean()), 2), diff=round(float(d.mean()), 2),
                                     signflip_blocks=X.sign_flip_blocks(d, D.block[g]), signflip_sessions=X.sign_flip_sessions(d, D.session[g], tag=f"{tf}|gate|{name}"),
                                     boot=H.bootstrap_ci(X.session_vectors(D, net, mask=g), tag=f"gate|{tf}|{name}"),
                                     book_net_foundation=round(float(D.fnd_net[g].sum()), 2), book_net_exit=round(float(net[g].sum()), 2)),
                      non_gate_rows=dict(n=int((~g).sum()), foundation_mean=round(float(D.fnd_net[~g].mean()), 2), exit_mean=round(float(net[~g].mean()), 2)))
frozen_l1 = [r for r in H.read_ledger("selftest/frozen_gate", tf) + H.read_ledger("comparator", tf) if r.get("label") == "L1"]
out = dict(tf=tf, n=int(D.n), table=rows, effective_trials_kept_sum=csel["effective_trials"], effective_trials_selection_gain=eff_gain, distinct_gain_vectors=distinct,
           spa_family=spa_c, spa_family_as_coded=SPA_C["as_coded"], spa_family_tolerance_check=SPA_C["tolerance_check"], near_duplicates=SPA_C["near_duplicates"],
           null_argmax_top5_as_coded=SPA_C["null_argmax_top5_as_coded"], vector_mapping_verified=SPA_C["vector_mapping_verified"], l1_choch_facts=l1_choch_facts,
           spa_all_trials=spa_all, spa_all_trials_as_coded=SPA_ALL["as_coded"], spa_all_trials_tolerance_check=SPA_ALL["tolerance_check"], near_duplicates_all_trials=SPA_ALL["near_duplicates"],
           spa_superseded_02_c_select=dict(csel["spa"], note="computed by 02_c_select.py with the harness.spa before its revision; superseded by spa_family"),
           spa_note="spa_family / spa_all_trials = REPAIRED (vectors at the label's 2-dp precision; the pass-rule items); *_as_coded = the stored vectors (the follow-up's numbers)",
           learners_present=sorted(learners), distillation=dist, exit_rules=rules, gate_multiplication=mult,
           frozen_gate_under_L1=[dict(id=r["id"], kept_n=r["kept_n"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"], control_pct=r["control_pct"]) for r in frozen_l1[:1]],
           seconds=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(HERE, f"eval_{tf}.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print(json.dumps(dict(distillation=dist, rules=rules, gate=mult, eff_gain=eff_gain, distinct=distinct), indent=1, default=str)[:5000])
