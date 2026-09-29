"""H2 "sideways = CHoCH without break" (BRIEF H2) through the harness. IS only; L1 primary, L0 robustness.

    python h2_regime.py [--tf minute|5minute] [--labels L1,L0]

Definitions (fixed before any number was read; the regime columns are the build's as-of columns, data/README.md):
  n_choch_since_bos        CHoCH events after the last BOS (all CHoCHs when no BOS yet); the SETUP's own CHoCH counts; >= 2 is
                           the user's "CHoCH, CHoCH, no BOS".  n_choch_since_bos_today: the same within the SETUP's session.
  alt_dir6 / alt_kind6     direction / kind changes among the last 6 events.
  range_{1h,3h}_atr        (max high - min low) over the last 60 / 180 bars (1 min) or 12 / 36 bars (5 min) of the session, / atr14.
  range_since_choch_atr    the same over bars choch_i .. k.   er_1h: Kaufman efficiency ratio over the last hour of the session.
  hour_bin                 fz_report.crosstabs bins: <09:25, 09 .. 15, >=15:20.
Descriptive tables (bucket_table; no rule chosen on them): Foundation L1 outcome by n_choch_since_bos (0,1,2,3,4+), by
  n_choch_since_bos_today, by alt_dir6, by alt_kind6, by terciles of range_1h_atr / range_3h_atr / range_since_choch_atr / er_1h
  (pooled IS edges, recorded), by hour_bin, and the two-way n_choch_since_bos x hour_bin. The same on L0.
Gate grid (the pre-registered grid of fz_v3/built/study/h2_regime.py; skip = do not take the SETUP):
  choch rule   skip when n_choch_since_bos >= kc (scope all) or n_choch_since_bos_today >= kc (scope today), kc in {2,3,4}
  range rule   skip when range_W_atr <= r, W in {1h, 3h, since_choch}, r = the quantile q in {0.1,0.2,0.3,0.4,0.5} of that
               range over the TRAINING FOLD's rows (fitted inside harness.purged_splits / cpcv_splits, never on pooled IS)
  combine      OR / AND when both rules are present; or one rule alone.   6 + 15 + 180 = 201 cells, each a ledger row
               (families h2/choch, h2/range, h2/both), scored on its 12-block out-of-fold mask.
Selection: nested CV only (h234_common.nested_cv): the cell is chosen inside each training fold by kept-vs-skipped diff subject
  to the harness kept floors; the 12 test blocks form the OOF mask (family h2/nested_cv); the 11 CPCV paths (h2/nested_cv/cpcv).
"""
import os, sys, json, time, argparse, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import h234_common as C
import harness as H

ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="minute,5minute"); ap.add_argument("--labels", default="L1,L0"); A = ap.parse_args()
log = C.Log(os.path.join(HERE, "h2_regime.log"))
T0 = time.time()
KC, SCOPES, WINDOWS, QS = (2, 3, 4), ("all", "today"), ("1h", "3h", "since_choch"), (0.1, 0.2, 0.3, 0.4, 0.5)


def choch_mask(T, rows, kc, scope):
    col = "n_choch_since_bos" if scope == "all" else "n_choch_since_bos_today"
    return T.F[col].to_numpy(dtype=float)[rows] >= kc                       # True = skip


def range_thr(T, rows, W, q):
    return float(np.nanquantile(T.F[f"range_{W}_atr"].to_numpy(dtype=float)[rows], q))


def range_mask(T, rows, W, thr):
    x = T.F[f"range_{W}_atr"].to_numpy(dtype=float)[rows]
    return np.where(np.isnan(x), False, x <= thr)                            # True = skip


def cells_h2():
    cells = []
    for kc, sc in itertools.product(KC, SCOPES):
        cells.append(C.Cell("h2/choch", dict(rule="choch", kc=kc, scope=sc), apply=lambda T, r, t, kc=kc, sc=sc: ~choch_mask(T, r, kc, sc)))
    for W, q in itertools.product(WINDOWS, QS):
        cells.append(C.Cell("h2/range", dict(rule="range", W=W, q=q), fit=lambda T, r, W=W, q=q: range_thr(T, r, W, q),
                            apply=lambda T, r, t, W=W: ~range_mask(T, r, W, t)))
    for (kc, sc), (W, q), comb in itertools.product(itertools.product(KC, SCOPES), itertools.product(WINDOWS, QS), ("OR", "AND")):
        def ap_(T, r, t, kc=kc, sc=sc, W=W, comb=comb):
            a, b = choch_mask(T, r, kc, sc), range_mask(T, r, W, t)
            return ~((a | b) if comb == "OR" else (a & b))
        cells.append(C.Cell("h2/both", dict(rule="both", kc=kc, scope=sc, W=W, q=q, combine=comb), fit=lambda T, r, W=W, q=q: range_thr(T, r, W, q), apply=ap_))
    return cells


def bucket(x, edges, labels):
    x = np.asarray(x, dtype=float)
    return np.array([labels[min(int(np.searchsorted(edges, v, side="right")), len(labels) - 1)] if not np.isnan(v) else "nan" for v in x])


def descriptive(T, tag):
    F = T.F; rows = np.flatnonzero(T.is_mask); tabs = []
    n5 = ["0", "1", "2", "3", "4+"]
    tabs.append(C.bucket_table(T, bucket(F.n_choch_since_bos, [1, 2, 3, 4], n5), "n_choch_since_bos", rows, n5))
    tabs.append(C.bucket_table(T, bucket(F.n_choch_since_bos_today, [1, 2, 3, 4], n5), "n_choch_since_bos_today", rows, n5))
    tabs.append(C.bucket_table(T, F.alt_dir6.astype(str).to_numpy(), "alt_dir6", rows))
    tabs.append(C.bucket_table(T, F.alt_kind6.astype(str).to_numpy(), "alt_kind6", rows))
    edges = {}
    for col in ("range_1h_atr", "range_3h_atr", "range_since_choch_atr", "er_1h"):
        x = F[col].to_numpy(dtype=float); lab, e = C.tercile_labels(np.where(T.is_mask, x, np.nan)); edges[col] = e
        tabs.append(C.bucket_table(T, lab, col + "_tercile", rows))
    hb = ["<09:25", "09", "10", "11", "12", "13", "14", "15", ">=15:20"]
    tabs.append(C.bucket_table(T, F.hour_bin.astype(str).to_numpy(), "hour_bin", rows, hb))
    D = pd.concat(tabs, ignore_index=True); D.to_csv(os.path.join(HERE, f"h2_{tag}_buckets.csv"), index=False)
    tw = C.two_way(T, bucket(F.n_choch_since_bos, [1, 2, 3, 4], n5), F.hour_bin.astype(str).to_numpy(), "n_choch_since_bos", "hour_bin", rows)
    tw.to_csv(os.path.join(HERE, f"h2_{tag}_x_nchoch_hour.csv"), index=False)
    return D, edges


def run(tf, label):
    T = H.load(tf, label); tag = f"{tf}_{label}"
    log(f"== H2 {tag}: IS units {int(T.is_mask.sum())} mean {T.net[T.is_mask].mean():.2f} win {T.win[T.is_mask].mean():.4f}")
    D, edges = descriptive(T, tag)
    s2 = D[(D.variable == "n_choch_since_bos")]
    log("  by n_choch_since_bos: " + "; ".join(f"{r.bucket}: n {r.n} mean {r.net_mean} win {r.win_rate}" for r in s2.itertuples()))
    cells = cells_h2()
    log(f"  grid: {len(cells)} cells")
    rows = C.score_cells(T, cells, __file__, log)
    G = C.grid_frame(rows, ["fold_thresholds"])
    cfgs = pd.DataFrame([r["config"] for r in rows]); G = pd.concat([cfgs, G], axis=1)
    G.to_csv(os.path.join(HERE, f"h2_{tag}_grid.csv"), index=False)
    nested, chosen, dist, prow, cp_chosen = C.nested_cv(T, cells, "h2", __file__, log)
    pd.DataFrame([{k: r.get(k) for k in ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "sign_blocks"]} | {"path": r["config"]["path"]} for r in prow]).to_csv(os.path.join(HERE, f"h2_{tag}_cpcv_paths.csv"), index=False)
    fam = C.family_stats(T, "h2", nested, dist, tag)
    log(f"  family: {fam['candidates']} candidates, eff {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} best {fam['spa_best_config']}, boot {fam['bootstrap_nested']['diff_ci']}, DSR p {fam['dsr_nested'].get('p')}, go {fam['go_no_go_nested']['passed']}")
    best_is = G.sort_values("diff", ascending=False).head(10)
    summ = dict(tf=tf, label=label, n_is=int(T.is_mask.sum()), all_mean=round(float(T.net[T.is_mask].mean()), 2), tercile_edges=edges, grid_cells=len(cells),
                grid_cells_go_raw=int(G.go_raw.sum()), grid_pct_ge95=int((G.control_pct >= 95).sum()), grid_diff_pos=int((G["diff"] > 0).sum()),
                top10_by_diff=best_is[["cell", "id", "kept_n", "kept_share", "diff", "control_pct", "perm_p", "sign_blocks", "go_raw"]].to_dict("records"),
                nested={k: nested.get(k) for k in C.GRID_COLS if k != "cell"} | dict(chosen_per_block=chosen),
                cpcv=dist, cpcv_chosen=cp_chosen, family=fam)
    C.jdump(summ, os.path.join(HERE, f"h2_{tag}_summary.json"))
    return summ


if __name__ == "__main__":
    log(f"h2_regime start {time.ctime()} ledger sha {H.ledger_sha()}")
    S = {}
    for tf in A.tf.split(","):
        for label in A.labels.split(","):
            S[f"{tf}/{label}"] = run(tf, label)
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    C.jdump(S, os.path.join(HERE, f"h2_summary_{A.tf.replace(',', '_')}.json"))
    log(f"h2 done in {S['run_s']}s; ledger sha {S['ledger_sha_after']}")
