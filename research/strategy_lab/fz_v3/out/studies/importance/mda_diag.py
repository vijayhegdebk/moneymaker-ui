"""Supplementary diagnostic of the clustered MDA (NOT the pass rule; changes nothing in the shortlist).
python mda_diag.py   -> mda_diag_<tf>.csv, mda_diag.json

Reads only the saved arrays of the main stage (oof_<tf>.npz: p_oof, the per-cluster per-permutation OOF probabilities
p_perm[K, 5, n], the fold of every row, the test-fold weights) and the L1 label through harness.load. No model is fitted, no
threshold is chosen, no ledger row is written, no OOS row is read (IS rows only, as the main stage).

Why: the design's primary MDA statistic is the permutation increase in the OOF |net|-weighted log-loss. A depth-limited bagging
with class_weight="balanced" answers a log-loss through its calibration as much as through its ranking: when every large cluster
has a NEGATIVE log-loss MDA (permuting its features lowers the loss), the reader must know whether that is "no ranking
information" or "the permuted, shrunken probabilities are better calibrated". This script reports, per cluster and fold:
  (1) a consistency check: the log-loss MDA recomputed from the saved arrays against mda_<tf>.csv;
  (2) the AUC drop (base OOF AUC on the fold's test rows minus the AUC with the cluster permuted; mean of the 5 permutations),
      its mean / std across the 12 folds, the number of folds with a positive drop, and the pooled-OOF AUC drop;
  (3) the calibration context of the full model: mean OOF probability, the unweighted and |net|-weighted winner share, the
      weighted log-loss of the constant predictor at the weighted winner share next to the model's OOF weighted log-loss.

Repair (2026-09-29, refuters' issue 4). p_perm is stored as float32 while p_oof is float64. The first version of this script
compared the two directly, so a cluster the forest never split on (p_perm identical to float32(p_oof) on every row) got a
recomputed drop of ~1e-9 instead of 0 and the exact-zero test `(ll_drop == 0).all()` never fired: the json said 0 exactly-zero
clusters while the table (computed in float64 in the main stage) has 18 (minute) / 14 (5minute). Now: (a) the base predictions
are rounded to float32 before every comparison (like-for-like), so the never-split clusters recompute to exactly 0 in log-loss
and in AUC; (b) 'exactly zero' is also tested by prediction identity (p_perm == float32(p_oof) on every IS row and permutation),
which is the definition ('permuting changes nothing'); (c) the per-period ranks of the stability step are recomputed two ways,
as run (imp_lib.period_mda: float64 base vs float32 permuted) and float32-consistent, and compared: the rounding noise is one
constant per period shared by every never-split cluster (a tie, not a re-order), and the check reports whether any cluster's
rank or stability flag differs between the two."""
import os, sys, json
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imp_lib as L
import harness as H
from sklearn.metrics import roc_auc_score

out = {}
for tf in ("minute", "5minute"):
    z = np.load(os.path.join(HERE, f"oof_{tf}.npz"), allow_pickle=True)
    T = H.load(tf)
    assert (z["setup_i"] == T.setup_i).all() and (z["is_mask"] == T.is_mask).all()
    y = T.win.astype(int)
    p, pp, w, fold = z["p_oof"], z["p_perm"], z["w_row"], z["fold_row"]
    p32 = p.astype(np.float32).astype(float)            # the base at the precision p_perm was stored in (like-for-like)
    K = pp.shape[0]
    is_idx = np.flatnonzero(z["is_mask"])
    tab_path = os.path.join(HERE, f"mda_{tf}.csv")
    if os.path.exists(tab_path): mda_tab = pd.read_csv(tab_path)
    else:  # 5minute ran as one process before the stage split: the table lives in the clusters CSV
        mda_tab = pd.read_csv(os.path.join(HERE, f"importance_clusters_{tf}.csv"))
    clus_tab = pd.read_csv(os.path.join(HERE, f"importance_clusters_{tf}.csv")).set_index("cluster").sort_index()
    mda_tab = mda_tab.set_index("cluster").sort_index()
    # exactly zero by identity: the permuted predictions equal float32(p_oof) on every IS row and every permutation
    ident = np.array([bool(np.all(pp[ci][:, is_idx] == p[is_idx].astype(np.float32))) for ci in range(K)])
    ll_drop = np.zeros((12, K)); ll_drop64 = np.zeros((12, K)); auc_drop = np.zeros((12, K)); base_auc = np.zeros(12)
    for f in range(12):
        te = is_idx[fold[is_idx] == f]
        base_ll32 = L.wlogloss(y[te], p32[te], w[te]); base_ll64 = L.wlogloss(y[te], p[te], w[te])
        base_auc[f] = roc_auc_score(y[te], p32[te])
        for ci in range(K):
            # per-permutation differences, then the mean (as the main stage does): five exact zeros average to exactly 0, whereas
            # mean(five identical losses) - base can drift by an ulp
            perm_ll = [L.wlogloss(y[te], pp[ci, r, te].astype(float), w[te]) for r in range(L.N_PERM)]
            ll_drop[f, ci] = np.mean([v - base_ll32 for v in perm_ll])          # float32-consistent (repair)
            ll_drop64[f, ci] = np.mean([v - base_ll64 for v in perm_ll])        # as the first version compared (float64 base): the rounding noise
            auc_drop[f, ci] = np.mean([base_auc[f] - roc_auc_score(y[te], pp[ci, r, te].astype(float)) for r in range(L.N_PERM)])
    ll_mean = ll_drop.mean(axis=0); ll_mean64 = ll_drop64.mean(axis=0)
    check = float(np.max(np.abs(ll_mean - mda_tab["mda_ll_mean"].to_numpy())))
    check64 = float(np.max(np.abs(ll_mean64 - mda_tab["mda_ll_mean"].to_numpy())))
    zero_exact = (ll_drop == 0).all(axis=0)
    assert (zero_exact == ident).all(), "exact-zero by log-loss and by prediction identity must agree at float32 precision"
    noise_by_fold = np.array([np.unique(np.round(ll_drop64[f, ident], 15)) for f in range(12)], dtype=object) if ident.any() else None
    pooled_base = float(roc_auc_score(y[is_idx], p32[is_idx]))
    pooled_drop = [pooled_base - float(np.mean([roc_auc_score(y[is_idx], pp[ci, r, is_idx].astype(float)) for r in range(L.N_PERM)])) for ci in range(K)]
    rows = []
    for ci in range(K):
        m, s = float(auc_drop[:, ci].mean()), float(auc_drop[:, ci].std(ddof=1))
        rows.append(dict(cluster=ci, ll_mda_recomputed=round(float(ll_mean[ci]), 6), ll_mda_table=round(float(mda_tab.loc[ci, "mda_ll_mean"]), 6),
                         ll_mda_exactly_zero_all_folds=bool(zero_exact[ci]), never_split_identity=bool(ident[ci]),
                         ll_mda_float64_base_noise=float(ll_mean64[ci] - ll_mean[ci]),
                         auc_mda_mean=round(m, 5), auc_mda_std=round(s, 5), auc_mda_ratio=(round(m / s, 3) if s > 0 else None),
                         auc_mda_pass_mean_gt_std=bool(m > s), auc_mda_folds_positive=int((auc_drop[:, ci] > 0).sum()),
                         auc_mda_pooled=round(float(pooled_drop[ci]), 5)))
    tab = pd.DataFrame(rows).sort_values("auc_mda_mean", ascending=False).reset_index(drop=True)
    tab["auc_rank"] = np.arange(1, K + 1)
    tab.to_csv(os.path.join(HERE, f"mda_diag_{tf}.csv"), index=False)
    # (c) the per-period ranks of the stability step, as run vs float32-consistent
    per = np.array([L.PERIODS[tf](d) for d in T.day]); pnames = sorted(set(per[is_idx]))
    prc = dict(periods={}, rank_as_run_matches_table=True, clusters_rank_changed=[], clusters_rank_changed_never_split=None, clusters_stab_changed=[],
               eligible_as_run=int((clus_tab["mda_ll_pass"] & clus_tab["stab_pass"]).sum()), eligible_consistent=None, mda_ll_pass_any=bool(clus_tab["mda_ll_pass"].any()))
    top8_run = np.zeros(K, dtype=int); top8_con = np.zeros(K, dtype=int)
    for pn in pnames:
        rws = is_idx[per[is_idx] == pn]; wr = w[rws]
        b64 = L.wlogloss(y[rws], p[rws], wr); b32 = L.wlogloss(y[rws], p32[rws], wr)
        pl = [[L.wlogloss(y[rws], pp[ci, r, rws].astype(float), wr) for r in range(L.N_PERM)] for ci in range(K)]
        v_run = np.array([np.mean([v - b64 for v in pl[ci]]) for ci in range(K)])   # imp_lib.period_mda as run (float64 base)
        v_con = np.array([np.mean([v - b32 for v in pl[ci]]) for ci in range(K)])   # float32-consistent: never-split clusters are exactly 0
        assert (v_con[ident] == 0).all()
        r_run = (-v_run).argsort().argsort() + 1; r_con = (-v_con).argsort().argsort() + 1
        r_tab = clus_tab[f"rank_{pn}"].to_numpy()
        prc["rank_as_run_matches_table"] &= bool((r_run == r_tab).all())
        top8_run += (r_run <= L.TOP_K_STAB); top8_con += (r_con <= L.TOP_K_STAB)
        nz = ~ident & (v_con != 0)
        prc["periods"][pn] = dict(n_rows=int(len(rws)), noise_constant_never_split=(float(np.unique(np.round(v_run[ident], 15))[0]) if ident.any() else None),
                                  noise_is_one_constant=(bool(len(np.unique(np.round(v_run[ident], 15))) == 1) if ident.any() else None),
                                  min_abs_mda_of_split_clusters=(float(np.min(np.abs(v_con[nz]))) if nz.any() else None),
                                  n_clusters_rank_differs=int((r_run != r_con).sum()), rank_as_run_matches_table=bool((r_run == r_tab).all()))
    stab_run = top8_run >= L.STAB_MIN_PERIODS[tf]; stab_con = top8_con >= L.STAB_MIN_PERIODS[tf]
    ch = np.flatnonzero(top8_run != top8_con)
    prc["clusters_rank_changed"] = [int(c) for c in ch]; prc["clusters_rank_changed_never_split"] = bool(ident[ch].all()) if len(ch) else True
    prc["clusters_stab_changed"] = [dict(cluster=int(c), stab_as_run=bool(stab_run[c]), stab_consistent=bool(stab_con[c]), never_split=bool(ident[c]),
                                         mda_ll_pass=bool(clus_tab.loc[c, "mda_ll_pass"])) for c in np.flatnonzero(stab_run != stab_con)]
    prc["stab_as_run_matches_table"] = bool((stab_run == clus_tab["stab_pass"].to_numpy()).all())
    prc["eligible_consistent"] = int((clus_tab["mda_ll_pass"].to_numpy() & stab_con).sum())
    wi = w[is_idx]
    pbar_w = float((wi * y[is_idx]).sum() / wi.sum()); pbar = float(y[is_idx].mean())
    const_ll = L.wlogloss(y[is_idx], np.full(len(is_idx), pbar_w), wi)
    model_ll = L.wlogloss(y[is_idx], p[is_idx], wi)
    n_zero_table = int(((mda_tab["mda_ll_mean"] == 0) & (mda_tab["mda_ll_folds_positive"] == 0)).sum()) if "mda_ll_folds_positive" in mda_tab else None
    out[tf] = dict(n_is=int(len(is_idx)), n_clusters=K, ll_mda_check_max_abs_diff=check, ll_mda_check_pass=bool(check < 1e-6),
                   ll_mda_check_float64_base_max_abs_diff=check64,
                   float32_precision_note="p_perm is float32; the base p_oof is rounded to float32 before every comparison here (like-for-like); the main stage computed its table in float64 before storage",
                   pooled_oof_auc=round(pooled_base, 4), fold_auc=[round(float(a), 4) for a in base_auc],
                   fold_auc_mean=round(float(base_auc.mean()), 4), fold_auc_std=round(float(base_auc.std(ddof=1)), 4),
                   mean_oof_probability=round(float(p[is_idx].mean()), 4), winner_share=round(pbar, 4), winner_share_net_weighted=round(pbar_w, 4),
                   wlogloss_constant_at_weighted_share=round(const_ll, 5), wlogloss_model_oof=round(model_ll, 5),
                   model_beats_constant_in_wlogloss=bool(model_ll < const_ll),
                   n_clusters_auc_pass=int(tab.auc_mda_pass_mean_gt_std.sum()), n_clusters_ll_negative=int((ll_mean < 0).sum()), n_clusters_ll_positive=int((ll_mean > 0).sum()),
                   n_clusters_ll_zero=int(zero_exact.sum()), n_clusters_ll_zero_by_identity=int(ident.sum()),
                   text_claim_exactly_zero_from_table=n_zero_table, zero_counts_agree=bool(n_zero_table is None or n_zero_table == int(zero_exact.sum())),
                   never_split_clusters=[int(c) for c in np.flatnonzero(ident)],
                   float64_base_noise_max_abs=float(np.max(np.abs(ll_mean64[ident] - ll_mean[ident]))) if ident.any() else 0.0,
                   period_rank_check=prc,
                   top5_by_auc_mda=tab.head(5)[["cluster", "auc_mda_mean", "auc_mda_std", "auc_mda_ratio", "auc_mda_folds_positive", "auc_mda_pooled"]].to_dict(orient="records"))
    print(tf, json.dumps({k: v for k, v in out[tf].items() if k not in ("fold_auc", "top5_by_auc_mda", "period_rank_check", "never_split_clusters")}))
    print(tf, "period_rank_check", json.dumps(prc))
    print(tab.head(8).to_string())
json.dump(out, open(os.path.join(HERE, "mda_diag.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
