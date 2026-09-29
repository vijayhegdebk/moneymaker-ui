"""session_stop (DESIGN_PANEL decision-making-6, both judges' fixes): does the causal session ledger carry information about the
next SETUP's L1 net beyond the hour-of-day effect, and if so does a daily stop rule (k stops / loss L) add kept-vs-skipped
expectancy beyond the costs it saves?

    python session_stop.py               # both timeframes (minute = primary, 5minute = underpowered), label L1, IS only
    python session_stop.py --selftest    # pure-function checks only (no ledger row is written)

Definitions (fixed before any number was looked at; also written to preregistration.json before the first statistic):
  unit         a harness row: a Foundation SETUP taken under the L1 (15:25) book, harness.load(tf, "L1"); IS rows only
  ledger       the session's Foundation trades closed by the SETUP bar k (as built: entry < k, exit <= k; verified identical on the
               truncated build): today_net_asof (sum of their L1 net, INR), today_n_stops_asof (their stop_loss exits). On this book
               the ledger equals the cumulative outcomes of the session's earlier units (asserted in code), so a permuted sequence's
               ledger is recomputed exactly as the cumulative sum / count of the permuted outcomes before each position
  hour_bin     the build's clock bins: <09:25, 09, 10, 11, 12, 13, 14, 15, >=15:20
  7 tests      (a) Spearman rho(today_net_asof, own L1 net); (b) mean L1 net where today_n_stops_asof >= k minus mean where < k,
               k = 1, 2, 3; (c) mean L1 net where today_net_asof <= L minus mean where > L, L = -2000, -4000, -6000 INR
  null N1      (primary, pre-registered entry condition; Judge 1) outcomes (net, stop flag) permuted among the units of the same
               session x hour_bin cell, positions fixed, the ledger recomputed from the permuted sequence: the hour profile of
               outcomes is preserved exactly, so a rejection is session memory beyond the hour effect
  null N2      (secondary, the design's plain null) the same with cells = sessions
  draws / p    2,000 draws per null, seeded numpy default_rng(int(sha1("fz|session_stop|<tf>|<label>|<null>"), 16) % 2**32);
               the permutation distribution is NOT centred at zero (under N1 the ledger still grows with the clock, so a later
               position has both more stops and the later hours' expectancy; under both nulls sampling without replacement inside a
               session makes "k stops already" slightly favour a non-stop next), so the two-sided p is the doubled tail against the
               permutation distribution: p = min(1, 2 min(p_lo, p_hi)), p_lo = (1 + #{stat* <= stat}) / (1 + draws), p_hi the same
               for >=; the naive form (1 + #{|stat*| >= |stat|}) / (1 + draws) is reported as p_abs for reference only; the excess =
               stat - mean(stat*) is the part of the statistic beyond the hour effect. Holm over the 7 tests per null per timeframe.
               (This p definition replaced the naive form after a 50-draw timing probe on 1 min showed the N1 distribution off
               centre; nothing else changed and no full run had been made.)
  decision     branch B (the grid) runs on a timeframe iff min Holm-adjusted p under N1 on L1 < 0.05; otherwise the study ends
               there for that timeframe: "no session memory beyond the hour effect", no key, no ledger row
  robustness   the same 7 tests on L0 (harness.load(tf, "L0")), reported, never the decision
  branch B     fixed 16-cell grid k in {1,2,3,4} x L in {-2000,-4000,-6000,none}: a unit is skipped once the session's ledger at its
               bar has >= k stops or net <= L (absorbing for the rest of the session; before the first trigger the strategy's own
               ledger equals Foundation's, so the replay is exact); one more axis rearm_after_win: when stopped, a skipped SETUP whose
               Foundation paper trade closes with net > 0 re-arms the rule at the next SETUP with the counters reset (32 cells);
               every cell = ledger row family session_stop/grid; nested choice inside the 12 purged training folds (max diff among
               cells with kept_share >= 0.20; tie -> larger kept share), the OOF mask = one row session_stop/nested; the 66 CPCV
               splits -> 11 paths (session_stop/nested/cpcv); the cell chosen on all IS = the candidate (its grid row); PBO / SPA /
               effective trials over the grid family; DSR with n_trials = cells; block-bootstrap CI; harness.go_no_go; the combined
               form (candidate AND fz_traded) = one row session_stop/combined per timeframe
  judgement    kept-vs-skipped mean net (INR per trade), the session-matched control percentile (a within-session gate: the standard
               control applies directly), the permutation p, loser recall / precision, |net|-weighted winner recall; never net alone
"""
import os, sys, json, time, argparse, hashlib, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np, pandas as pd
from scipy import stats as sst
import harness as H

STUDY = "session_stop"
HOUR_ORDER = ["<09:25", "09", "10", "11", "12", "13", "14", "15", ">=15:20"]
K_GRID, L_GRID = [1, 2, 3, 4], [-2000.0, -4000.0, -6000.0, None]
REARM_AXIS = [False, True]
NULL_DRAWS, ALPHA = 2000, 0.05
TESTS = ["spearman_today_net", "stops>=1", "stops>=2", "stops>=3", "net<=-2000", "net<=-4000", "net<=-6000"]
K_TESTS, L_TESTS = [1, 2, 3], [-2000.0, -4000.0, -6000.0]
KEPT_SHARE_FLOOR = 0.20
T0 = time.time()
LOG = open(os.path.join(HERE, "session_stop.log"), "a", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def rng_for(tf, label, null):
    return np.random.default_rng(int(H._sha(f"{H.SEED}|{STUDY}|{tf}|{label}|{null}"), 16) % (2 ** 32))


# ---------------------------------------------------------------- the session frame
def session_frame(T, rows):
    """Rows (a split's row indices, time-ordered) as arrays plus the run structure: sessions and session x hour_bin cells are
    contiguous runs in row order (asserted), and the built ledger equals the cumulative prior outcomes (asserted)."""
    F = T.F.iloc[rows]
    sess = F.session_idx.to_numpy(); hb = F.hour_bin.astype(str).to_numpy()
    assert (np.diff(T.setup_i[rows]) > 0).all(), "rows must be time-ordered"
    net = T.net[rows].astype(float)
    pre = "l1_" if T.label == "L1" else "fnd_"
    stop = (F[pre + "exit_reason"].astype(str) == "stop_loss").to_numpy()
    today_net = F.today_net_asof.to_numpy(dtype=float); today_stops = F.today_n_stops_asof.to_numpy(dtype=int)
    # runs
    new_sess = np.r_[True, sess[1:] != sess[:-1]]
    sess_run = np.cumsum(new_sess) - 1
    new_cell = new_sess | np.r_[True, hb[1:] != hb[:-1]]
    cell_run = np.cumsum(new_cell) - 1
    assert len(set(sess.tolist())) == sess_run.max() + 1, "a session must be one contiguous run"
    assert len({(int(s), h) for s, h in zip(sess, hb)}) == cell_run.max() + 1, "a session x hour_bin cell must be one contiguous run"
    sess_first = np.flatnonzero(new_sess)
    tn, ts = recompute_ledger(net, stop, sess_first, sess_run)
    ledger_identity = dict(net_max_abs_diff=float(np.abs(tn - today_net).max()), stops_identical=bool((ts == today_stops).all()))
    return dict(rows=rows, sess=sess, hour_bin=hb, net=net, stop=stop, today_net=today_net, today_stops=today_stops, sess_run=sess_run,
                cell_run=cell_run, sess_first=sess_first, win=net > 0, ledger_identity=ledger_identity)


def recompute_ledger(net, stop, sess_first, sess_run):
    """The ledger before each position from a (possibly permuted) outcome sequence: cumulative sum / count within the session."""
    prior_net = np.cumsum(net) - net; prior_stop = np.cumsum(stop.astype(int)) - stop.astype(int)
    return prior_net - prior_net[sess_first][sess_run], prior_stop - prior_stop[sess_first][sess_run]


def stats7(today_net, today_stops, net):
    """The seven pre-registered statistics (nan when a side is empty)."""
    out = np.full(7, np.nan)
    rx, ry = sst.rankdata(today_net), sst.rankdata(net)
    if rx.std() > 0 and ry.std() > 0: out[0] = np.corrcoef(rx, ry)[0, 1]
    for j, k in enumerate(K_TESTS):
        m = today_stops >= k
        if m.any() and (~m).any(): out[1 + j] = net[m].mean() - net[~m].mean()
    for j, L in enumerate(L_TESTS):
        m = today_net <= L
        if m.any() and (~m).any(): out[4 + j] = net[m].mean() - net[~m].mean()
    return out


def holm(p):
    p = np.asarray(p, dtype=float); m = len(p); order = np.argsort(p); adj = np.empty(m); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i])); adj[i] = run
    return adj


def null_test(S, tf, label, null, draws=NULL_DRAWS):
    """Permute outcomes within cells (N1: session x hour_bin; N2: session), recompute the ledger, redo the 7 statistics."""
    cell = S["cell_run"] if null == "session_x_hour" else S["sess_run"]
    obs = stats7(S["today_net"], S["today_stops"], S["net"])
    rng = rng_for(tf, label, null)
    perm_stats = np.empty((draws, 7))
    for d in range(draws):
        perm = np.lexsort((rng.random(len(cell)), cell))                 # within each contiguous cell, a random order
        pn, ps = S["net"][perm], S["stop"][perm]
        tn, ts = recompute_ledger(pn, ps, S["sess_first"], S["sess_run"])
        perm_stats[d] = stats7(tn, ts, pn)
    valid = np.isfinite(perm_stats); n_valid = valid.sum(axis=0)
    with np.errstate(invalid="ignore"):
        lo = (1 + ((perm_stats <= obs[None, :] + 1e-12) & valid).sum(axis=0)) / (1 + n_valid)
        hi = (1 + ((perm_stats >= obs[None, :] - 1e-12) & valid).sum(axis=0)) / (1 + n_valid)
        p_abs = (1 + ((np.abs(perm_stats) >= np.abs(obs)[None, :] - 1e-12) & valid).sum(axis=0)) / (1 + n_valid)
    p = np.minimum(1.0, 2 * np.minimum(lo, hi))
    cells = np.bincount(cell)
    return dict(null=null, draws=draws, observed=obs, p=p, p_holm=holm(p), p_lo=lo, p_hi=hi, p_abs=p_abs, perm_mean=np.nanmean(perm_stats, axis=0),
                perm_sd=np.nanstd(perm_stats, axis=0), perm_valid=n_valid, excess=obs - np.nanmean(perm_stats, axis=0),
                n_cells=int(len(cells)), cells_size1=int((cells == 1).sum()), rows_movable=int(cells[cells > 1].sum()))


def null_table(S, results, tf, label):
    n = len(S["net"]); rows = []
    for j, t in enumerate(TESTS):
        if j == 0: n_a, n_b = n, None
        elif j <= 3: m = S["today_stops"] >= K_TESTS[j - 1]; n_a, n_b = int(m.sum()), int((~m).sum())
        else: m = S["today_net"] <= L_TESTS[j - 4]; n_a, n_b = int(m.sum()), int((~m).sum())
        r = dict(tf=tf, label=label, test=t, n_condition=n_a, n_other=n_b, observed=round(float(results[0]["observed"][j]), 4))
        for R in results:
            tag = "N1" if R["null"] == "session_x_hour" else "N2"
            r.update({f"{tag}_p": round(float(R["p"][j]), 4), f"{tag}_p_holm": round(float(R["p_holm"][j]), 4),
                      f"{tag}_perm_mean": round(float(R["perm_mean"][j]), 4), f"{tag}_perm_sd": round(float(R["perm_sd"][j]), 4),
                      f"{tag}_excess": round(float(R["excess"][j]), 4), f"{tag}_p_lo": round(float(R["p_lo"][j]), 4), f"{tag}_p_hi": round(float(R["p_hi"][j]), 4),
                      f"{tag}_p_abs_ref": round(float(R["p_abs"][j]), 4), f"{tag}_valid_draws": int(R["perm_valid"][j])})
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- descriptive tables (IS)
def hour_profile(S):
    df = pd.DataFrame(dict(hour_bin=S["hour_bin"], net=S["net"], win=S["win"], today_net=S["today_net"], today_stops=S["today_stops"], stop=S["stop"]))
    g = df.groupby("hour_bin")
    out = pd.DataFrame(dict(n=g.size(), mean_net=g.net.mean().round(2), median_net=g.net.median().round(2), win_rate=g.win.mean().round(4),
                            stop_rate=g.stop.mean().round(4), mean_today_net_asof=g.today_net.mean().round(2),
                            mean_today_n_stops_asof=g.today_stops.mean().round(3), share_stops_ge1=g.today_stops.apply(lambda x: (x >= 1).mean()).round(4),
                            share_net_le_m4000=g.today_net.apply(lambda x: (x <= -4000).mean()).round(4)))
    out = out.reindex([h for h in HOUR_ORDER if h in out.index]); out.index.name = "hour_bin"
    return out.reset_index()


def by_stops(S):
    b = np.minimum(S["today_stops"], 4); lab = np.where(b >= 4, "4+", b.astype(str))
    df = pd.DataFrame(dict(stops=lab, net=S["net"], win=S["win"]))
    g = df.groupby("stops")
    return pd.DataFrame(dict(n=g.size(), mean_net=g.net.mean().round(2), median_net=g.net.median().round(2), win_rate=g.win.mean().round(4))).reset_index()


def by_net_bucket(S):
    x = S["today_net"]
    lab = np.select([x > 0, x == 0, x > -2000, x > -4000, x > -6000], ["> 0", "= 0", "(-2000, 0)", "(-4000, -2000]", "(-6000, -4000]"], "<= -6000")
    order = ["> 0", "= 0", "(-2000, 0)", "(-4000, -2000]", "(-6000, -4000]", "<= -6000"]
    df = pd.DataFrame(dict(today_net_bucket=lab, net=S["net"], win=S["win"]))
    g = df.groupby("today_net_bucket")
    out = pd.DataFrame(dict(n=g.size(), mean_net=g.net.mean().round(2), median_net=g.net.median().round(2), win_rate=g.win.mean().round(4)))
    return out.reindex([o for o in order if o in out.index]).reset_index()


def hour_x_stops(S):
    df = pd.DataFrame(dict(hour_bin=S["hour_bin"], ge1=np.where(S["today_stops"] >= 1, "stops>=1", "stops=0"), net=S["net"]))
    g = df.groupby(["hour_bin", "ge1"]).net.agg(["size", "mean"]).round(2).unstack("ge1")
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.reindex([h for h in HOUR_ORDER if h in g.index])
    if "mean_stops>=1" in g and "mean_stops=0" in g: g["diff_within_hour"] = (g["mean_stops>=1"] - g["mean_stops=0"]).round(2)
    return g.reset_index()


# ---------------------------------------------------------------- branch B: the finite-horizon replay
def running_min_by_session(x, sess_first, sess_run):
    out = np.empty_like(x)
    for s in range(len(sess_first)):
        a = sess_first[s]; b = sess_first[s + 1] if s + 1 < len(sess_first) else len(x)
        out[a:b] = np.minimum.accumulate(x[a:b])
    return out


def grid_keep(today_stops, today_net_runmin, k, L):
    """Absorbing rule: skip once the session's ledger at the bar has >= k stops or its running minimum net <= L."""
    stopped = today_stops >= k
    if L is not None: stopped = stopped | (today_net_runmin <= L)
    return ~stopped


def rearm_keep(net, stop, sess_first, sess_run, k, L):
    """Re-arm after a winner: while armed, take and count (stops, net since the last arm); stop when the count reaches >= k stops
    or <= L; while stopped, skip, and re-arm at the next SETUP (counters reset) when the skipped SETUP's paper trade wins."""
    n = len(net); keep = np.zeros(n, dtype=bool)
    for s in range(len(sess_first)):
        a = sess_first[s]; b = sess_first[s + 1] if s + 1 < len(sess_first) else n
        armed, ns, nn = True, 0, 0.0
        for j in range(a, b):
            if armed:
                keep[j] = True; ns += int(stop[j]); nn += net[j]
                if ns >= k or (L is not None and nn <= L): armed = False
            else:
                keep[j] = False
                if net[j] > 0: armed, ns, nn = True, 0, 0.0
    return keep


def all_cells():
    return [dict(max_stops_today=k, max_loss_today_inr=L, rearm_after_win=r) for r in REARM_AXIS for k in K_GRID for L in L_GRID]


def cell_masks(T):
    """Keep masks over T's rows for every grid cell, built from the IS rows only (the rule reads the built as-of ledger; the rearm
    variant reads the IS outcomes of skipped SETUPs). Rows outside IS are left True and are never scored here."""
    rows = np.flatnonzero(T.is_mask); S = session_frame(T, rows)
    runmin = running_min_by_session(S["today_net"], S["sess_first"], S["sess_run"])
    masks = {}
    for c in all_cells():
        key = json.dumps(c, sort_keys=True)
        if not c["rearm_after_win"]: m = grid_keep(S["today_stops"], runmin, c["max_stops_today"], c["max_loss_today_inr"])
        else: m = rearm_keep(S["net"], S["stop"], S["sess_first"], S["sess_run"], c["max_stops_today"], c["max_loss_today_inr"])
        full = np.ones(T.n, dtype=bool); full[rows] = m; masks[key] = full
    return masks


def choose_cell(T, masks, tr):
    """Training-fold choice: the cell with the largest kept-vs-skipped diff among cells with kept_share >= 0.20; tie -> larger kept share."""
    best = None
    for key, m in masks.items():
        r = H.metrics(T, m, tr, tag="train", controls=False)
        if r["kept_share"] is None or r["kept_share"] < KEPT_SHARE_FLOOR or r["diff"] is None: continue
        cand = (r["diff"], r["kept_share"], key)
        if best is None or cand > best: best = cand
    return best


def branch_b(T, tf, out):
    log(f"[{tf}] branch B: the {len(all_cells())}-cell grid, nested choice, CPCV, go/no-go")
    masks = cell_masks(T); is_rows = np.flatnonzero(T.is_mask)
    grid_rows, vecs, keys = [], [], []
    for key, m in masks.items():
        cfg = json.loads(key)
        r = H.score(T, m, f"{STUDY}/grid", cfg, script=__file__)
        grid_rows.append(r); vecs.append(H.session_vectors(T, m, is_rows)); keys.append(key)
        log(f"  grid {cfg}: id {r['id']} kept {r['kept_n']} share {r['kept_share']} diff {r['diff']} ctrl {r['control_pct']} perm_p {r['perm_p']}")
    pd.DataFrame(grid_rows).to_csv(os.path.join(HERE, f"grid_{tf}.csv"), index=False)
    # nested choice inside the 12 purged training folds -> one OOF mask
    oof = np.zeros(T.n, dtype=bool); chosen_folds = []
    for b, (tr, te) in enumerate(H.purged_splits(T)):
        best = choose_cell(T, masks, tr)
        if best is None: chosen_folds.append(None); oof[te] = True; continue
        oof[te] = masks[best[2]][te]; chosen_folds.append(json.loads(best[2]))
    nested = H.score(T, oof, f"{STUDY}/nested", dict(selection="max diff | kept_share>=0.20 in training fold", folds=12), script=__file__)
    log(f"  nested OOF: id {nested['id']} kept {nested['kept_n']} diff {nested['diff']} ctrl {nested['control_pct']} perm_p {nested['perm_p']} sign_blocks {nested['sign_blocks']}")
    # CPCV: 66 splits -> 11 paths
    oof_split = {}
    for tr, te, (a, b) in H.cpcv_splits(T):
        best = choose_cell(T, masks, tr)
        oof_split[(a, b)] = (masks[best[2]][te] if best is not None else np.ones(len(te), dtype=bool)).astype(float)
    paths = H.cpcv_paths(T, oof_split)
    dist, path_rows = H.score_paths(T, paths, f"{STUDY}/nested", dict(selection="max diff | kept_share>=0.20 in training fold"), script=__file__, controls=True)
    log(f"  CPCV: {dist}")
    # the candidate: the cell chosen on all IS rows (its grid row is the ledger row)
    best_all = choose_cell(T, masks, is_rows)
    cand_cfg = json.loads(best_all[2]) if best_all else None
    res = next(r for r, k in zip(grid_rows, keys) if k == best_all[2]) if best_all else None
    fam = dict(pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"{STUDY}|{tf}"), effective_trials=H.effective_trials(vecs))
    go, checks, dsr, boot, combined = None, None, None, None, None
    if res is not None:
        vec = vecs[keys.index(best_all[2])]
        per = np.where(vec["kept_n"] > 0, vec["kept_sum"] / np.maximum(vec["kept_n"], 1), 0.0)[vec["kept_n"] > 0]
        srs = []
        for v in vecs:
            x = np.where(v["kept_n"] > 0, v["kept_sum"] / np.maximum(v["kept_n"], 1), 0.0)[v["kept_n"] > 0]
            if len(x) > 2 and x.std(ddof=1) > 0: srs.append(x.mean() / x.std(ddof=1))
        sr_var = float(np.var(srs, ddof=1)) if len(srs) > 1 and np.var(srs, ddof=1) > 0 else None
        dsr = H.deflated_sharpe(per, len(vecs), sr_var)
        boot = H.bootstrap_ci(vec, tag=f"{STUDY}|{tf}")
        go, checks = H.go_no_go(res, tf, cpcv=dist, pbo_value=fam["pbo_diff"]["pbo"], dsr=dsr, spa_p=fam["spa"]["spa_p"], boot=boot)
        log(f"  candidate {cand_cfg}: go={go} " + json.dumps(checks, default=str))
        comb = masks[best_all[2]] & T.F.fz_traded.astype(bool).to_numpy()
        combined = H.score(T, comb, f"{STUDY}/combined", dict(cand_cfg, and_gate="fz_traded (frozen ST7/ST8, comparator)"), script=__file__)
        log(f"  combined (rule AND fz_traded): id {combined['id']} kept {combined['kept_n']} diff {combined['diff']} ctrl {combined['control_pct']}")
    out.update(branch_b=dict(grid=[{k: r[k] for k in ("id", "config", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct",
                                                        "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "sign_blocks", "kept_mean_slip8")} for r in grid_rows],
                             nested_oof={k: nested[k] for k in ("id", "kept_n", "kept_share", "diff", "perm_p", "control_pct", "sign_blocks")}, chosen_per_fold=chosen_folds,
                             cpcv=dist, cpcv_path_ids=[r["id"] for r in path_rows], candidate=cand_cfg, candidate_ledger_id=res["id"] if res else None,
                             family=fam, dsr=dsr, bootstrap=boot, go_no_go=dict(passed=go, checks=checks) if checks else None,
                             combined={k: combined[k] for k in ("id", "kept_n", "kept_share", "diff", "perm_p", "control_pct", "sign_blocks")} if combined else None))
    return out


# ---------------------------------------------------------------- self-test of the pure functions (no ledger row)
def selftest():
    net = np.array([-1000.0, -2500.0, 3000.0, -1500.0, -1200.0, 500.0, -900.0]); stop = np.array([0, 1, 0, 1, 1, 0, 0], dtype=bool)
    sess_first = np.array([0, 4]); sess_run = np.array([0, 0, 0, 0, 1, 1, 1])
    tn, ts = recompute_ledger(net, stop, sess_first, sess_run)
    assert np.allclose(tn, [0, -1000, -3500, -500, 0, -1200, -700]) and (ts == [0, 0, 1, 1, 0, 1, 1]).all()
    rm = running_min_by_session(tn, sess_first, sess_run); assert np.allclose(rm, [0, -1000, -3500, -3500, 0, -1200, -1200])
    assert (grid_keep(ts, rm, 1, None) == [1, 1, 0, 0, 1, 0, 0]).all()
    assert (grid_keep(ts, rm, 4, -3000.0) == [1, 1, 0, 0, 1, 1, 1]).all()
    # rearm (k = 1): session 0 stops after position 1, position 2 is skipped and its paper trade wins -> re-armed, 3 taken;
    # session 1 stops after position 4, position 5 skipped and wins -> 6 taken
    assert (rearm_keep(net, stop, sess_first, sess_run, 1, None) == [1, 1, 0, 1, 1, 0, 1]).all()
    assert (rearm_keep(net, stop, sess_first, sess_run, 1, None) != grid_keep(ts, rm, 1, None)).sum() == 2
    # rearm (k = 9, L = -3000): session 0 stops at position 1 (net -3500), 2 skipped and wins -> 3 taken; session 1 never stops
    assert (rearm_keep(net, stop, sess_first, sess_run, 9, -3000.0) == [1, 1, 0, 1, 1, 1, 1]).all()
    p = holm([0.01, 0.04, 0.03]); assert np.allclose(p, [0.03, 0.06, 0.06])
    s = stats7(tn, ts, net); assert np.isfinite(s[1]) and np.isnan(s[3])
    print("selftest ok")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    if a.selftest: selftest(); return
    prereg = dict(study=STUDY, design="DESIGN_PANEL decision-making-6 with both judges' fixes", label="L1", split="IS", primary_tf="minute",
                  secondary_tf="5minute (reported as underpowered: median 2 SETUPs per active session)", tests=TESTS, k_tests=K_TESTS, l_tests=L_TESTS,
                  null_primary="N1: outcomes permuted within session x hour_bin cells, positions fixed, ledger recomputed from the permuted sequence",
                  null_secondary="N2: outcomes permuted within sessions", draws=NULL_DRAWS, two_sided=True, alpha=ALPHA,
                  p_definition="doubled tail against the permutation distribution: p = min(1, 2 min(p_lo, p_hi)), p_lo = (1 + #{stat* <= stat}) / (1 + draws), p_hi likewise for >=; "
                               "the naive (1 + #{|stat*| >= |stat|}) / (1 + draws) is reported as p_abs_ref only (the N1 distribution is off centre: the ledger grows with the clock)",
                  p_definition_history="the doubled-tail form replaced the naive form after a 50-draw timing probe on 1 min / L1 (before any full run); no other definition changed",
                  multiplicity="Holm over the 7 tests per null per timeframe", decision="branch B iff min Holm p under N1 (L1) < 0.05 on that timeframe; else no key, no ledger row",
                  seed="numpy default_rng(int(sha1('fz|session_stop|<tf>|<label>|<null>')[:16], 16) % 2**32)",
                  robustness="the 7 tests on L0 (reported only)", grid=dict(max_stops_today=K_GRID, max_loss_today_inr=L_GRID, rearm_after_win=REARM_AXIS),
                  rule="absorbing: skip once the ledger at the bar has >= k stops or running-min net <= L; rearm variant re-arms at the next SETUP after a skipped SETUP's paper trade wins, counters reset",
                  fold_selection=f"max diff among cells with kept_share >= {KEPT_SHARE_FLOOR}; tie -> larger kept share", registered_at=D.datetime.now().isoformat(timespec="seconds"))
    pp = os.path.join(HERE, "preregistration.json"); json.dump(prereg, open(pp, "w", encoding="utf-8"), indent=1)
    log(f"== {STUDY} {prereg['registered_at']} preregistration sha {hashlib.sha256(open(pp, 'rb').read()).hexdigest()[:16]} ledger sha before {H.ledger_sha()}")
    results = dict(study=STUDY, preregistration=prereg, timeframes={})
    for tf in ("minute", "5minute"):
        out = dict(power_note="primary" if tf == "minute" else "underpowered: median 2 SETUPs per active session, most session x hour cells are singletons")
        for label in ("L1", "L0"):
            T = H.load(tf, label); is_rows = np.flatnonzero(T.is_mask); S = session_frame(T, is_rows)
            g = pd.Series(S["sess"]).value_counts()
            log(f"[{tf}/{label}] IS units {len(is_rows)} active sessions {len(g)} setups/session median {g.median()} max {g.max()} ledger identity {S['ledger_identity']}")
            res = [null_test(S, tf, label, "session_x_hour"), null_test(S, tf, label, "session")]
            tab = null_table(S, res, tf, label)
            tab.to_csv(os.path.join(HERE, f"null_tests_{tf}_{label}.csv"), index=False)
            log(tab.to_string(index=False))
            for R in res: log(f"  {R['null']}: cells {R['n_cells']} singleton cells {R['cells_size1']} movable rows {R['rows_movable']}")
            rec = dict(units=int(len(is_rows)), active_sessions=int(len(g)), setups_per_session_median=float(g.median()), setups_per_session_max=int(g.max()),
                       ledger_identity=S["ledger_identity"], tests=tab.to_dict(orient="records"),
                       nulls={R["null"]: dict(n_cells=R["n_cells"], cells_size1=R["cells_size1"], rows_movable=R["rows_movable"]) for R in res},
                       min_p_holm_N1=float(res[0]["p_holm"].min()), min_p_holm_N2=float(res[1]["p_holm"].min()),
                       rejected_N1=bool(res[0]["p_holm"].min() < ALPHA), rejected_N2=bool(res[1]["p_holm"].min() < ALPHA))
            if label == "L1":
                hp = hour_profile(S); hp.to_csv(os.path.join(HERE, f"hour_profile_{tf}.csv"), index=False); log(hp.to_string(index=False))
                bs = by_stops(S); bs.to_csv(os.path.join(HERE, f"by_stops_{tf}.csv"), index=False); log(bs.to_string(index=False))
                bn = by_net_bucket(S); bn.to_csv(os.path.join(HERE, f"by_net_bucket_{tf}.csv"), index=False); log(bn.to_string(index=False))
                hx = hour_x_stops(S); hx.to_csv(os.path.join(HERE, f"hour_x_stops_{tf}.csv"), index=False); log(hx.to_string(index=False))
                rec.update(hour_profile=hp.to_dict(orient="records"), by_stops=bs.to_dict(orient="records"), by_net_bucket=bn.to_dict(orient="records"),
                           hour_x_stops=hx.to_dict(orient="records"))
                out["L1"] = rec
                out["decision"] = "REJECTED: session memory beyond the hour effect -> branch B" if rec["rejected_N1"] else \
                    ("NOT REJECTED under N1 (N2 rejected: the hour effect alone)" if rec["rejected_N2"] else "NOT REJECTED under either null") + " -> study ends: no session memory beyond the hour effect, no key"
                log(f"[{tf}] decision: {out['decision']}")
                if rec["rejected_N1"]: branch_b(T, tf, out)
            else:
                out["L0_robustness"] = rec
        results["timeframes"][tf] = out
    results["ledger_sha_after"] = H.ledger_sha(); results["runtime_s"] = round(time.time() - T0, 1)
    json.dump(results, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
    log(f"done in {results['runtime_s']}s; ledger sha after {results['ledger_sha_after']}")


if __name__ == "__main__":
    main()
