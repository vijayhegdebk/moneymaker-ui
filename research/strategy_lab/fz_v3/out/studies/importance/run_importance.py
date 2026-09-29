"""Importance study, one timeframe: python run_importance.py --tf minute|5minute [--stage all|main|sfi|cpcv|finalize] [--dry]
Stages are independent processes that share nothing but the deterministic feature assembly / clustering and the per-stage seeds
(main 1000+fold, sfi 2000+fold, cpcv 3000+split), so running them in parallel gives the same numbers as `--stage all`:
  main      features, clustering, the full bagged model with clustered MDA, stability, full-model ledger row, depth sensitivity,
            PCA check, interactions -> main_<tf>.json, mda_<tf>.csv, oof_<tf>.npz, importance_features_<tf>.csv, interaction CSVs
  sfi       each cluster alone under the same CV, one ledger row each -> sfi_<tf>.csv
  cpcv      the full model's OOF gate over the 66 CPCV splits -> cpcv_<tf>.json (+ 11 ledger rows)
  finalize  merges the three, computes the family statistics from the ledger -> results_<tf>.json, importance_clusters_<tf>.csv
--dry: 20 trees, no ledger rows (harness.metrics only), no CPCV; outputs under dry/. Debugging of the code paths only."""
import os, sys, json, time, argparse
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imp_lib as L
import harness as H

ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); ap.add_argument("--stage", default="all"); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
tf, dry, stage = a.tf, a.dry, a.stage
ODIR = os.path.join(HERE, "dry") if dry else HERE
os.makedirs(ODIR, exist_ok=True)
if dry: L.N_TREES = 20
logf = open(os.path.join(ODIR, f"run_{tf}.log"), "a", encoding="utf-8")
T0 = time.time()
L.log(f"=== importance {tf} stage={stage} dry={dry} trees={L.N_TREES} bag_jobs={L.BAG_JOBS} xgb_jobs={L.XGB_JOBS} ===", logf)
J = lambda z: z.item() if hasattr(z, "item") else str(z)


def scorer(T, keep, family, cfg):
    if dry:
        m = H.metrics(T, keep, np.flatnonzero(T.is_mask), "dry", controls=False); m["id"] = "DRY"; return m
    return H.score(T, keep, family, cfg, script=__file__)


if dry: L.H.score = lambda T, keep, family, cfg, script=None: scorer(T, keep, family, cfg)

# (1) features and (3) clustering: deterministic, recomputed by every stage
T, Xa, meta = L.assemble(tf, logf)
defs, card_def, fz_def = L.readme_defs()
is_idx = np.flatnonzero(T.is_mask)
y = T.win.astype(int)
cl = L.cluster(Xa, T.is_mask, logf)
clusters, reps = cl["clusters"], cl["reps"]
cfg_full = dict(model="bagging_dt", depth=L.DEPTH_MAIN, trees=L.N_TREES, min_weight_fraction_leaf=L.MIN_LEAF, features=int(Xa.shape[1]),
                weights="|net| winsorised at train p99, class_weight balanced", tau="train-fold OOB: max kept mean s.t. weighted winner recall >= 0.90")
P = lambda name: os.path.join(ODIR, name)


def stage_main():
    cl["rho"].round(4).to_csv(P(f"spearman_{tf}.csv"))
    json.dump(dict(k_best=cl["k_best"], silhouette=cl["silhouette"], clusters=clusters, representatives=reps), open(P(f"clusters_{tf}.json"), "w"), indent=1)
    # (4) full model with clustered MDA
    res = L.full_model_pass(T, Xa, clusters, L.DEPTH_MAIN, tf, logf, with_mda=True)
    mda = L.summarise_mda(res, clusters)
    keep_full = res["p_oof"] >= res["tau_row"]
    r_full = scorer(T, keep_full, "importance/full_model", cfg_full)
    auc_full = float(L.roc_auc_score(y[is_idx], res["p_oof"][is_idx]))
    ll_full = L.wlogloss(y[is_idx], res["p_oof"][is_idx], res["w_row"][is_idx])
    L.log(f"full model depth 4: OOF wlogloss {ll_full:.5f} auc {auc_full:.4f}; gate diff {r_full['diff']} kept {r_full['kept_share']} ctrl {r_full['control_pct']} id {r_full['id']}", logf)
    np.savez_compressed(P(f"oof_{tf}.npz"), p_oof=res["p_oof"], tau_row=res["tau_row"], w_row=res["w_row"], fold_row=res["fold_row"],
                        p_perm=res["p_perm"], is_mask=T.is_mask, setup_i=T.setup_i, mdi=res["mdi"], cols=np.array(res["cols"]))
    mdi_feat = res["mdi"].mean(axis=0); cidx = {c: i for i, c in enumerate(res["cols"])}
    mda["mdi"] = [float(sum(mdi_feat[cidx[c]] for c in clusters[ci])) for ci in mda.cluster]
    # (7) stability by period
    per = L.period_mda(T, res, clusters, tf)
    pnames = sorted(per)
    for pn in pnames: mda[f"rank_{pn}"] = per[pn]["rank"]; mda[f"mda_ll_{pn}"] = [round(v, 6) for v in per[pn]["mda_ll"]]
    mda["stab_top8_periods"] = [int(sum(per[pn]["rank"][ci] <= L.TOP_K_STAB for pn in pnames)) for ci in mda.cluster]
    mda["stab_pass"] = mda["stab_top8_periods"] >= L.STAB_MIN_PERIODS[tf]
    rank_corr = {}
    for i, p1 in enumerate(pnames):
        for p2 in pnames[i + 1:]:
            rank_corr[f"{p1}|{p2}"] = round(float(L.sst.spearmanr(per[p1]["mda_ll"], per[p2]["mda_ll"]).statistic), 4)
    L.log(f"stability periods {[(str(pn), per[pn]['n_rows'], per[pn]['n_winners']) for pn in pnames]}; rank corr {rank_corr}", logf)
    # depth sensitivity (full model only)
    sens = {}
    for d in L.DEPTHS_SENS:
        rd = L.full_model_pass(T, Xa, clusters, d, tf, logf, with_mda=False)
        kd = rd["p_oof"] >= rd["tau_row"]
        rr = scorer(T, kd, "importance/full_model", dict(cfg_full, depth=d))
        sens[d] = dict(oof_wlogloss=round(L.wlogloss(y[is_idx], rd["p_oof"][is_idx], rd["w_row"][is_idx]), 5),
                       oof_auc=round(float(L.roc_auc_score(y[is_idx], rd["p_oof"][is_idx])), 4), ledger_id=rr["id"], diff=rr["diff"],
                       kept_share=rr["kept_share"], control_pct=rr["control_pct"], perm_p=rr["perm_p"])
        L.log(f"depth {d}: {sens[d]}", logf)
    # (5) orthogonal check
    pca = L.pca_check(T, Xa, L.DEPTH_MAIN, logf)
    # (6) interactions on the top-40 features by clustered MDA (clusters in MDA-ll order, members in MDI order)
    order = mda.sort_values("mda_ll_mean", ascending=False).cluster.tolist()
    top_cols = []
    for ci in order:
        for c in sorted(clusters[ci], key=lambda c: -mdi_feat[cidx[c]]):
            if len(top_cols) < L.TOP_INTER and not c.endswith("__na"): top_cols.append(c)
    inter = L.interactions(T, Xa, top_cols, tf, logf)
    inter["matrix"].round(6).to_csv(P(f"shap_interactions_{tf}.csv"))
    L.log(f"interactions: xgb OOF ll {inter['xgb_oof_wlogloss']} auc {inter['xgb_oof_auc']}; top5 {[(p['feature_a'], p['feature_b'], p['mean_abs_interaction']) for p in inter['top5']]}", logf)
    pd.DataFrame(inter["pairs_ranked"]).to_csv(P(f"interaction_pairs_{tf}.csv"), index=False)
    pd.DataFrame(res["folds"]).drop(columns=["mda"]).to_csv(P(f"folds_{tf}.csv"), index=False)
    mda.to_csv(P(f"mda_{tf}.csv"), index=False)
    feat = pd.DataFrame(dict(feature=res["cols"], mdi_mean=mdi_feat, mdi_std=res["mdi"].std(axis=0)))
    c_of = {c: ci for ci, mem in clusters.items() for c in mem}
    feat["cluster"] = feat.feature.map(c_of)
    Xa_is = Xa[T.is_mask]
    feat["tier"] = [L.tier_of(c, Xa_is) for c in feat.feature]
    feat["coverage_is"] = [round(float(1 - Xa_is[c].isna().mean()), 4) for c in feat.feature]
    feat["readme"] = [L.define(c, defs, card_def, fz_def)["readme"] for c in feat.feature]
    feat["definition"] = [L.define(c, defs, card_def, fz_def)["definition"] for c in feat.feature]
    feat.sort_values("mdi_mean", ascending=False).to_csv(P(f"importance_features_{tf}.csv"), index=False)
    main = dict(tf=tf, dry=dry, at=L.D.datetime.now().isoformat(timespec="seconds"), runtime_s=round(time.time() - T0, 1), max_rss_mb=L.rss_mb(), meta=meta,
                clustering=dict(k_best=cl["k_best"], silhouette=cl["silhouette"], n_clusters=len(clusters)),
                full_model=dict(config=cfg_full, oof_wlogloss=round(ll_full, 5), oof_auc=round(auc_full, 4), ledger_id=r_full["id"],
                                gate={k: r_full.get(k) for k in ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct",
                                                                 "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "sign_blocks", "kept_mean_slip8")},
                                folds=[{k: v for k, v in f.items() if k != "mda"} for f in res["folds"]], depth_sensitivity=sens, cpcv=None),
                stability=dict(periods={str(pn): {k: v for k, v in per[pn].items() if k != "mda_ll"} for pn in pnames}, rank_corr=rank_corr, rule=f"top-{L.TOP_K_STAB} in >= {L.STAB_MIN_PERIODS[tf]} of {len(pnames)} periods"),
                pca_check=pca, interactions=dict(top_cols=top_cols, top5=inter["top5"], xgb_oof_wlogloss=inter["xgb_oof_wlogloss"], xgb_oof_auc=inter["xgb_oof_auc"]),
                mdi_feat={c: float(mdi_feat[cidx[c]]) for c in res["cols"]}, pnames=[str(p) for p in pnames])
    json.dump(main, open(P(f"main_{tf}.json"), "w"), indent=1, default=J)
    L.log(f"=== main done {tf} in {time.time() - T0:.0f}s ===", logf)


def stage_sfi():
    sfi = L.sfi_pass(T, Xa, clusters, L.DEPTH_MAIN, tf, __file__, logf)
    sfi.to_csv(P(f"sfi_{tf}.csv"), index=False)
    L.log(f"=== sfi done {tf} in {time.time() - T0:.0f}s ===", logf)


def stage_cpcv():
    if dry: L.log("cpcv skipped (dry)", logf); return
    Xn = Xa.to_numpy(dtype=float); oof = {}
    t0 = time.time()
    for s, (tr, te, ab) in enumerate(H.cpcv_splits(T)):
        w_tr, w_te, cap = L.fold_weights(T, tr, te)
        Xtr, Xte = L.impute(Xn[tr], Xn[te])
        bag, oob = L.fit_bag(Xtr, y[tr], w_tr, L.DEPTH_MAIN, 3000 + s)
        tau, _ = L.choose_tau(oob, T.net[tr], T.win[tr])
        oof[ab] = (L.bag_predict(bag, Xte) >= tau).astype(float)
        if s % 11 == 10: L.log(f"cpcv split {s + 1}/66 ({time.time() - t0:.0f}s)", logf)
    paths = H.cpcv_paths(T, oof)
    cpcv, rows = H.score_paths(T, paths, "importance/full_model", cfg_full, script=__file__, controls=True, threshold=0.5)
    json.dump(dict(cpcv=cpcv, rows=[{k: r.get(k) for k in ("id", "config", "kept_share", "diff", "control_pct", "perm_p")} for r in rows]), open(P(f"cpcv_{tf}.json"), "w"), indent=1, default=J)
    L.log(f"cpcv: {cpcv}", logf)
    L.log(f"=== cpcv done {tf} in {time.time() - T0:.0f}s ===", logf)


def stage_finalize():
    main = json.load(open(P(f"main_{tf}.json")))
    mda = pd.read_csv(P(f"mda_{tf}.csv"))
    sfi = pd.read_csv(P(f"sfi_{tf}.csv"))
    cpcv = json.load(open(P(f"cpcv_{tf}.json")))["cpcv"] if os.path.exists(P(f"cpcv_{tf}.json")) else None
    pnames = main["pnames"]
    mda = mda.merge(sfi, on="cluster", how="left")
    fam = None
    if not dry:
        rows = H.read_ledger("importance", tf=tf, label="L1")
        r_full = [r for r in rows if r["id"] == main["full_model"]["ledger_id"]][0]
        vecs = [H.load_vectors(r["id"]) for r in rows]
        v_full = H.load_vectors(r_full["id"])
        boot = H.bootstrap_ci(v_full, tag=r_full["id"])
        kn = v_full["kept_n"] > 0
        dsr = H.deflated_sharpe((v_full["kept_sum"] / np.maximum(v_full["kept_n"], 1))[kn], len(rows), 0.01)
        spa = H.spa(vecs, tag=f"importance|{tf}") if len(vecs) >= 2 else None
        pbo = H.pbo(vecs, "diff") if len(vecs) >= 2 else None
        eff = H.effective_trials(vecs) if len(vecs) >= 2 else None
        passed, checks = H.go_no_go(r_full, tf, cpcv=cpcv, pbo_value=pbo["pbo"] if pbo else None, dsr=dsr, spa_p=spa.get("spa_p") if spa else None, boot=boot)
        fam = dict(ledger_rows=len(rows), rows_by_family={f: sum(1 for r in rows if r["family"] == f) for f in sorted({r["family"] for r in rows})},
                   pbo=pbo, spa=spa, effective_trials=eff, bootstrap_full=boot, dsr_full=dsr,
                   go_no_go_full=dict(passed=bool(passed), checks={k: [bool(v[0]), v[1]] for k, v in checks.items()}))
        L.log(f"family: rows {len(rows)} pbo {pbo and pbo['pbo']} spa {spa and spa.get('spa_p')} eff {eff} boot {boot['diff_ci']} go {passed}", logf)
    mda["representative"] = [reps[ci]["representative"] for ci in mda.cluster]
    mda["rep_tier"] = [reps[ci]["tier"] for ci in mda.cluster]
    mda["rep_why"] = [reps[ci]["why"] for ci in mda.cluster]
    mda["n_members"] = [len(clusters[ci]) for ci in mda.cluster]
    mda["members"] = ["; ".join(clusters[ci]) for ci in mda.cluster]
    mda["shortlist_eligible"] = mda["mda_ll_pass"] & mda["stab_pass"]
    mda = mda.sort_values("mda_ll_mean", ascending=False).reset_index(drop=True)
    mda["mda_rank"] = np.arange(1, len(mda) + 1)
    front = ["mda_rank", "cluster", "representative", "n_members", "mda_ll_mean", "mda_ll_std", "mda_ll_ratio", "mda_ll_pass", "mda_ll_folds_positive",
             "mda_diff_mean", "mda_diff_std", "mda_diff_ratio", "mda_diff_pass", "mdi", "sfi_oof_wlogloss", "sfi_oof_auc", "diff", "kept_share",
             "control_pct", "perm_p", "winner_recall_weighted", "ledger_id"] + [f"rank_{pn}" for pn in pnames] + ["stab_top8_periods", "stab_pass", "shortlist_eligible"]
    mda = mda[front + [c for c in mda.columns if c not in front]]
    mda.to_csv(P(f"importance_clusters_{tf}.csv"), index=False)
    c_of = {c: ci for ci, mem in clusters.items() for c in mem}
    cols = list(Xa.columns)
    h2 = [c for c in cols if c in ("n_choch_since_bos", "n_choch_since_bos_today", "choch_run", "n_flip_since_bos", "alt_kind6", "alt_dir6")]
    states = [c for c in cols if c.startswith(("hmm", "gmm", "jump"))]
    same = dict(h2_clusters={c: c_of[c] for c in h2}, state_clusters={c: c_of[c] for c in states},
                shared={ci: [c for c in clusters[ci] if c in h2 + states] for ci in set(c_of[c] for c in h2) & set(c_of[c] for c in states)})
    ffd_cols = [c for c in cols if c.startswith("ffd_")]
    mi = mda.set_index("cluster")
    ffd = dict(columns={c: c_of[c] for c in ffd_cols},
               clusters={int(ci): dict(members=clusters[ci], mda_ll_mean=float(mi.loc[ci, "mda_ll_mean"]), mda_ll_std=float(mi.loc[ci, "mda_ll_std"]),
                                       mda_ll_pass=bool(mi.loc[ci, "mda_ll_pass"]), stab_pass=bool(mi.loc[ci, "stab_pass"]),
                                       mixed_with_non_ffd=bool(any(not c.startswith("ffd_") for c in clusters[ci]))) for ci in sorted(set(c_of[c] for c in ffd_cols))})
    main["full_model"]["cpcv"] = cpcv
    out = dict(main); out.pop("mdi_feat", None); out.pop("pnames", None)
    out.update(finalized_at=L.D.datetime.now().isoformat(timespec="seconds"), h2_vs_states=same, ffd=ffd, family=fam, clusters_table=mda.drop(columns=["members"]).to_dict(orient="records"))
    json.dump(out, open(P(f"results_{tf}.json"), "w"), indent=1, default=J)
    L.log(f"=== finalize done {tf}; eligible clusters {int(mda.shortlist_eligible.sum())} of {len(mda)} ===", logf)


if stage in ("all", "main"): stage_main()
if stage in ("all", "sfi"): stage_sfi()
if stage in ("all", "cpcv"): stage_cpcv()
if stage in ("all", "finalize"): stage_finalize()
