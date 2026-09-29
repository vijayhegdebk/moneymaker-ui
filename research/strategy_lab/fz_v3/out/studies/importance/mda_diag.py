"""Supplementary diagnostic of the clustered MDA (NOT the pass rule; changes nothing in the shortlist).
python mda_diag.py   -> mda_diag_<tf>.csv, mda_diag.json

Reads only the saved arrays of the main stage (oof_<tf>.npz: p_oof, the per-cluster per-permutation OOF probabilities
p_perm[K, 5, n], the fold of every row, the test-fold weights) and the L1 label through harness.load. No model is fitted, no
threshold is chosen, no ledger row is written, no OOS row is read (IS rows only, as the main stage).

Why: the design's primary MDA statistic is the permutation increase in the OOF |net|-weighted log-loss. A depth-limited bagging
with class_weight="balanced" answers a log-loss through its calibration as much as through its ranking: when every large cluster
has a NEGATIVE log-loss MDA (permuting its features lowers the loss), the reader must know whether that is "no ranking
information" or "the permuted, shrunken probabilities are better calibrated". This script reports, per cluster and fold:
  (1) a consistency check: the log-loss MDA recomputed from the saved arrays against mda_<tf>.csv (must agree to 1e-6);
  (2) the AUC drop (base OOF AUC on the fold's test rows minus the AUC with the cluster permuted; mean of the 5 permutations),
      its mean / std across the 12 folds, the number of folds with a positive drop, and the pooled-OOF AUC drop;
  (3) the calibration context of the full model: mean OOF probability, the unweighted and |net|-weighted winner share, the
      weighted log-loss of the constant predictor at the weighted winner share next to the model's OOF weighted log-loss."""
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
    K = pp.shape[0]
    is_idx = np.flatnonzero(z["is_mask"])
    mda_tab = pd.read_csv(os.path.join(HERE, f"mda_{tf}.csv")) if os.path.exists(os.path.join(HERE, f"mda_{tf}.csv")) else None
    if mda_tab is None:  # 5minute ran as one process before the stage split: the table lives in the clusters CSV
        mda_tab = pd.read_csv(os.path.join(HERE, f"importance_clusters_{tf}.csv"))[["cluster", "mda_ll_mean", "mda_ll_std"]]
    mda_tab = mda_tab.set_index("cluster").sort_index()
    ll_drop = np.zeros((12, K)); auc_drop = np.zeros((12, K)); base_auc = np.zeros(12)
    for f in range(12):
        te = is_idx[fold[is_idx] == f]
        base_ll = L.wlogloss(y[te], p[te], w[te]); base_auc[f] = roc_auc_score(y[te], p[te])
        for ci in range(K):
            ll_drop[f, ci] = np.mean([L.wlogloss(y[te], pp[ci, r, te].astype(float), w[te]) - base_ll for r in range(L.N_PERM)])
            auc_drop[f, ci] = np.mean([base_auc[f] - roc_auc_score(y[te], pp[ci, r, te].astype(float)) for r in range(L.N_PERM)])
    ll_mean = ll_drop.mean(axis=0)
    check = float(np.max(np.abs(ll_mean - mda_tab["mda_ll_mean"].to_numpy())))
    pooled_base = float(roc_auc_score(y[is_idx], p[is_idx]))
    pooled_drop = [pooled_base - float(np.mean([roc_auc_score(y[is_idx], pp[ci, r, is_idx].astype(float)) for r in range(L.N_PERM)])) for ci in range(K)]
    rows = []
    for ci in range(K):
        m, s = float(auc_drop[:, ci].mean()), float(auc_drop[:, ci].std(ddof=1))
        rows.append(dict(cluster=ci, ll_mda_recomputed=round(float(ll_mean[ci]), 6), ll_mda_table=round(float(mda_tab.loc[ci, "mda_ll_mean"]), 6),
                         auc_mda_mean=round(m, 5), auc_mda_std=round(s, 5), auc_mda_ratio=(round(m / s, 3) if s > 0 else None),
                         auc_mda_pass_mean_gt_std=bool(m > s), auc_mda_folds_positive=int((auc_drop[:, ci] > 0).sum()),
                         auc_mda_pooled=round(float(pooled_drop[ci]), 5)))
    tab = pd.DataFrame(rows).sort_values("auc_mda_mean", ascending=False).reset_index(drop=True)
    tab["auc_rank"] = np.arange(1, K + 1)
    tab.to_csv(os.path.join(HERE, f"mda_diag_{tf}.csv"), index=False)
    wi = w[is_idx]
    pbar_w = float((wi * y[is_idx]).sum() / wi.sum()); pbar = float(y[is_idx].mean())
    const_ll = L.wlogloss(y[is_idx], np.full(len(is_idx), pbar_w), wi)
    model_ll = L.wlogloss(y[is_idx], p[is_idx], wi)
    out[tf] = dict(n_is=int(len(is_idx)), n_clusters=K, ll_mda_check_max_abs_diff=check, ll_mda_check_pass=bool(check < 1e-6),
                   pooled_oof_auc=round(pooled_base, 4), fold_auc=[round(float(a), 4) for a in base_auc],
                   fold_auc_mean=round(float(base_auc.mean()), 4), fold_auc_std=round(float(base_auc.std(ddof=1)), 4),
                   mean_oof_probability=round(float(p[is_idx].mean()), 4), winner_share=round(pbar, 4), winner_share_net_weighted=round(pbar_w, 4),
                   wlogloss_constant_at_weighted_share=round(const_ll, 5), wlogloss_model_oof=round(model_ll, 5),
                   model_beats_constant_in_wlogloss=bool(model_ll < const_ll),
                   n_clusters_auc_pass=int(tab.auc_mda_pass_mean_gt_std.sum()), n_clusters_ll_negative=int((ll_mean < 0).sum()),
                   n_clusters_ll_zero=int((ll_drop == 0).all(axis=0).sum()),
                   top5_by_auc_mda=tab.head(5)[["cluster", "auc_mda_mean", "auc_mda_std", "auc_mda_ratio", "auc_mda_folds_positive", "auc_mda_pooled"]].to_dict(orient="records"))
    print(tf, json.dumps({k: v for k, v in out[tf].items() if k not in ("fold_auc", "top5_by_auc_mda")}))
    print(tab.head(8).to_string())
json.dump(out, open(os.path.join(HERE, "mda_diag.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
