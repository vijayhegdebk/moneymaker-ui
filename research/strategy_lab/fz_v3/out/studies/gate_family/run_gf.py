"""gate_family driver: one timeframe x one sub-family per process (definitions: gf_lib docstring).

    python run_gf.py --tf 5minute --sub context            # every model, every stage
    python run_gf.py --tf minute --sub h5_full --models hgbc --stages oof12,cpcv

Stages per model (each checkpointed to results/<tf>/<sub>/<model>.pkl; a finished stage is never rerun):
  oof12    12 purged blocks, nested tau, the headline OOF ledger row (controls on); the fixed-tau grid rows (controls off); the
           nested distillation (rule list + depth-3 tree fit to the training-fold decisions, applied to the test fold) as their own
           OOF rows (controls on); the time-decay sensitivity and the model's structural sensitivities (controls off)
  cpcv     66 splits -> 11 paths for the learner and for its two distilled forms (controls on)
  frozen   the shipped forms fit on all IS rows: the rule list distilled from the pooled OOF decisions (fidelity reported), the
           scorecard / policy learner refit on all IS (one ledger row each; a selection on pooled OOF, counted as a trial)
  robust   the same learner trained on L0 / L2x1 / L2x2 / L3 (12-block OOF) scored on that label's table and, when the rows
           coincide, on L1 (controls off)
  diag     SHAP drivers (hgbc), calibration (hgbc, scorecard), per-hour / per-regime kept share, OOF AUC; oof_<tf>_<sub>.parquet
"""
import os, sys, json, time, argparse, pickle, traceback
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import gf_lib as G       # noqa: E402
H = G.H
SCRIPT = os.path.abspath(__file__)
ROBUST_LABELS = ["L0", "L2x1", "L2x2", "L3"]


def model_specs(sub, tf, cols, info, clusters, pairs, proxies):
    min_leaf = G.MIN_LEAF[tf]; p = len(cols); cidx = {c: i for i, c in enumerate(cols)}
    if sub == "context":
        icst = [list(range(p))]
        return {
            "bag4": dict(make=lambda: G.BagLearner(4), desc="(a) BaggingClassifier 300 x depth-4 trees", distil=True, decay=True,
                         sens={"bag3": (lambda: G.BagLearner(3)), "bag5": (lambda: G.BagLearner(5))}),
            "hgbc": dict(make=lambda: G.HGBCLearner(icst, None), desc="(b) HGB classifier, one interaction group (hour x dir), no monotone constraint", distil=True, decay=True, sens={}),
            "hgbr": dict(make=lambda: G.HGBRLearner(icst, None), desc="(c) HGB regressor E[net|x] > tau_r", distil=True, decay=False, sens={}),
            "pt1": dict(make=lambda: G.PolicyLearner("ptree", 1, min_leaf), desc="(d) exact depth-1 policy tree", distil=False, decay=False, sens={}),
            "pt2": dict(make=lambda: G.PolicyLearner("ptree", 2, min_leaf), desc="(d) greedy depth-2 policy tree", distil=False, decay=False, sens={}),
            "pt3": dict(make=lambda: G.PolicyLearner("ptree", 3, min_leaf), desc="(d) greedy depth-3 policy tree", distil=False, decay=False, sens={}),
            "scorecard": dict(make=lambda: G.ScorecardLearner(G.SC_MAX[tf]), desc="(e) hour-bin / dir scorecard (L1 logistic, integer points)", distil=True, decay=True, sens={}),
        }, dict(interaction_cst="one group (all context columns)", monotonic_cst=None)
    groups = [[cidx[c] for c in mem if c in cidx] for mem in clusters.values()]
    groups = [g for g in groups if len(g) >= 1]
    pgroups = [[cidx[a], cidx[b]] for a, b in pairs if a in cidx and b in cidx]
    icst = groups + pgroups
    mono = np.array([G.MONO.get(c, 0) for c in cols]); mono_arr = mono if (mono != 0).any() else None
    meta = dict(interaction_cst=f"{len(groups)} importance clusters + {len(pgroups)} interaction pairs (pairs with a time proxy dropped: {[list(pr) for pr in pairs if pr[0] in proxies or pr[1] in proxies]})",
                monotonic_cst={c: int(v) for c, v in zip(cols, mono) if v != 0})
    return {
        "dt3": dict(make=lambda: G.DT3Learner(min_leaf), desc="H5 DecisionTreeClassifier depth <= 3, min leaf %d, nested tau" % min_leaf, distil=False, decay=True, sens={}),
        "h5rules": dict(make=lambda: G.PolicyLearner("h5rules", None, min_leaf), desc="H5 greedy rule list by training kept expectancy (stop < 200 INR/trade)", distil=False, decay=False, sens={}),
        "hgbc": dict(make=lambda: G.HGBCLearner(icst, mono_arr), desc="(b) HGB classifier, interaction_cst = clusters + pairs, monotone H2 columns", distil=True, decay=True,
                     sens={"hgbc_nomono": (lambda: G.HGBCLearner(icst, None))}),
        "scorecard": dict(make=lambda: G.ScorecardLearner(G.SC_MAX[tf]), desc="(e) scorecard, <= %d source features by the L1 path" % G.SC_MAX[tf], distil=True, decay=True, sens={}),
    }, meta


def pooled(recs, T, key="keep_te", is_rows=None):
    keep = np.ones(T.n, dtype=bool)
    for r in recs: keep[r["te"]] = r[key]
    return keep


def strip(rec):
    r = {k: v for k, v in rec.items() if k not in ("model",)}
    for k in ("p_inner", "keep_tr"):
        r.pop(k, None)
    if "distill" in r:
        for f in ("rules", "tree"): r["distill"][f].pop("keep_tr", None)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", required=True); ap.add_argument("--sub", required=True, choices=["context", "h5_full"])
    ap.add_argument("--models", default=None); ap.add_argument("--stages", default="oof12,cpcv,frozen,robust,diag")
    a = ap.parse_args()
    tf, sub = a.tf, a.sub; stages = a.stages.split(",")
    rdir = os.path.join(G.RES, tf, sub); os.makedirs(rdir, exist_ok=True)
    log = G.Log(os.path.join(HERE, f"run_{tf}_{sub}.log"))
    log(f"start tf={tf} sub={sub} stages={stages} jobs={G.N_JOBS} OMP={os.environ.get('OMP_NUM_THREADS')}")
    t_all = time.time()
    # ---- features
    T = H.load(tf)
    if sub == "context":
        X, info, fmeta = G.context_features(T); Fx = T.F.reset_index(drop=True); clusters = pairs = None; ind_cover = {}
        proxies = sorted(G.tapes.time_proxies(tf))
    else:
        T, X, info, fmeta, clusters, pairs, E = G.full_features(tf, log)
        Fx = pd.concat([T.F.reset_index(drop=True), E.reset_index(drop=True)], axis=1); ind_cover = fmeta["missing_indicators"]
        proxies = fmeta["time_proxies"]
    cols = list(X.columns); Xn = X.to_numpy(dtype=float); is_rows = np.flatnonzero(T.is_mask)
    min_leaf = G.MIN_LEAF[tf]
    specs, smeta = model_specs(sub, tf, cols, info, clusters, pairs, proxies)
    if a.models: specs = {k: v for k, v in specs.items() if k in a.models.split(",")}
    G.jdump(dict(fmeta=fmeta, smeta=smeta, cols=cols, info=info, n_is=int(len(is_rows)), tau_grid=G.TAU_GRID, taur_grid=G.TAUR_GRID,
                 min_leaf=min_leaf), os.path.join(rdir, "features.json"))
    log(f"features {Xn.shape}, IS rows {len(is_rows)}, models {list(specs)}")
    labels = G.load_labels(tf)
    uniq_is = G.avg_uniqueness(T, is_rows); log(f"L1 average uniqueness on IS {uniq_is:.4f}")
    vocab = "inside the frozen vocabulary (context columns)" if sub == "context" else "outside the frozen shortlist (importance rule failed for every cluster)"

    def cfg(model, stage, **kw):
        d = dict(sub=sub, model=model, stage=stage, label="L1", vocabulary=vocab)
        if model == "scorecard": d["c_search"] = G.SC_SEARCH          # the C-search procedure is part of the trial's identity
        d.update(kw); return d

    def note(): return G.SUB_NOTE[sub]

    def run_oof(make, Tt, Xt, Fxt, decay=False, distil=False, tag=""):
        recs = []
        for b, (tr, te) in enumerate(H.purged_splits(Tt)):
            t0 = time.time()
            ctx = dict(uniq=G.avg_uniqueness(Tt, tr))
            rec = G.fit_split(tag, make, Tt, Xt, Fxt, cols, info, tr, te, tf, ctx, decay=decay)
            rec["te"] = te; rec["fold"] = b
            if distil: rec["distill"] = G.distill(rec, Xt, Fxt, cols, info, tr, te, tf, min_leaf)
            recs.append(rec)
            log(f"  {tag} fold {b}: tau={rec.get('tau')} kept_te={float(np.mean(rec['keep_te'])):.3f} "
                + (f"rules={rec.get('n_rules')} " if rec.get("n_rules") is not None else "") + f"{time.time() - t0:.1f}s")
        return recs

    for name, spec in specs.items():
        fam = f"{G.STUDY}/{sub}/{name}"
        pkl = os.path.join(rdir, f"{name}.pkl"); res = pickle.load(open(pkl, "rb")) if os.path.exists(pkl) else dict(model=name, desc=spec["desc"], stages={})
        def save(): pickle.dump(res, open(pkl, "wb"))
        log(f"=== {name}: {spec['desc']} (done: {list(res['stages'])})")
        try:
            # ------------------------------------------------ oof12
            if "oof12" in stages and "oof12" not in res["stages"]:
                t0 = time.time()
                recs = run_oof(spec["make"], T, Xn, Fx, distil=spec["distil"], tag=name)
                keep = pooled(recs, T)
                row = H.score(T, keep, fam, cfg(name, "oof12", taus=[r["tau"] for r in recs]), script=SCRIPT, controls=True, note=note())
                st = dict(row=row, taus=[r["tau"] for r in recs], tau_tables=[r.get("tau_table") for r in recs],
                          tau_constraint_satisfied=[r.get("tau_constraint_satisfied") for r in recs], n_rules=[r.get("n_rules") for r in recs],
                          rules_per_fold=[r.get("rules") for r in recs], caps=[r["cap"] for r in recs])
                log(f"  {name} OOF: id {row['id']} kept {row['kept_share']} diff {row['diff']} ctrl {row['control_pct']} perm {row['perm_p']} wrec {row['winner_recall_weighted']} signs {row['sign_blocks']}")
                kind = recs[0]["model"].kind if "model" in recs[0] else "policy"
                st["kind"] = kind
                # fixed-tau grid rows (trials)
                if kind in ("prob", "enet", "score"):
                    st["tau_rows"] = {}
                    grid = G.TAU_GRID if kind in ("prob", "score") else G.TAUR_GRID
                    for tau in grid:
                        k2 = np.ones(T.n, dtype=bool)
                        for r in recs:
                            s = r["p_te"] if kind == "score" else r["score_te"]
                            k2[r["te"]] = s >= tau
                        rr = H.score(T, k2, fam + "/tau", cfg(name, "fixed_tau", tau=tau), script=SCRIPT, controls=False, note=note())
                        st["tau_rows"][str(tau)] = dict(id=rr["id"], kept_share=rr["kept_share"], diff=rr["diff"], diff_top1_removed=rr["diff_top1_removed"], sign_blocks=rr["sign_blocks"])
                    # pooled OOF scores for diagnostics / the oof parquet
                    st["oof"] = dict(setup_i=np.concatenate([T.setup_i[r["te"]] for r in recs]), fold=np.concatenate([np.full(len(r["te"]), r["fold"]) for r in recs]),
                                     score=np.concatenate([np.asarray(r["score_te"], dtype=float) for r in recs]),
                                     p=np.concatenate([np.asarray(r["p_te"] if kind == "score" else r["score_te"], dtype=float) for r in recs]),
                                     tau=np.concatenate([np.full(len(r["te"]), r["tau"]) for r in recs]), keep=np.concatenate([r["keep_te"] for r in recs]))
                    if kind in ("prob", "score"):
                        from sklearn.metrics import roc_auc_score
                        st["oof_auc"] = round(float(roc_auc_score(T.win[np.concatenate([r["te"] for r in recs])], st["oof"]["p"])), 4)
                        st["calibration"] = G.calibration(st["oof"]["p"], T.win[np.concatenate([r["te"] for r in recs])])
                else:
                    st["oof"] = dict(setup_i=np.concatenate([T.setup_i[r["te"]] for r in recs]), fold=np.concatenate([np.full(len(r["te"]), r["fold"]) for r in recs]),
                                     score=np.full(len(is_rows), np.nan), p=np.full(len(is_rows), np.nan), tau=np.full(len(is_rows), np.nan),
                                     keep=np.concatenate([r["keep_te"] for r in recs]))
                if kind == "score":
                    st["scorecards_per_fold"] = [dict(card=r["card"], score_min=r["score_min"], n_src=r["n_src"], C=r["C"], selected=r["selected"], platt=r["platt"]) for r in recs]
                st["kept_share_by_hour"] = G.kept_share_by(T, keep, is_rows, "hour_bin"); st["kept_share_by_regime"] = G.kept_share_by(T, keep, is_rows, "regime")
                st["kept_share_by_dir"] = G.kept_share_by(T, keep, is_rows, "dir")
                # nested distillation rows
                if spec["distil"]:
                    st["distill"] = {}
                    for form in ("rules", "tree"):
                        kd = np.ones(T.n, dtype=bool)
                        for r in recs: kd[r["te"]] = r["distill"][form]["keep_te"]
                        rd = H.score(T, kd, fam + f"/distill_{form}", cfg(name, f"distill_{form}_oof12"), script=SCRIPT, controls=True, note=note())
                        fid = G.fidelity(kd[is_rows], keep[is_rows])
                        st["distill"][form] = dict(row=rd, fidelity_oof=fid, fidelity_train=[r["distill"][form]["fidelity_tr"] for r in recs],
                                                   n_rules=[r["distill"][form]["n_rules"] for r in recs], rules_per_fold=[r["distill"][form]["rules"] for r in recs])
                        log(f"  {name} distilled {form}: id {rd['id']} kept {rd['kept_share']} diff {rd['diff']} fidelity {fid['agreement']}")
                # SHAP (hgbc)
                if name == "hgbc":
                    try:
                        import shap
                        acc = np.zeros(len(cols)); n_acc = 0
                        for r in recs:
                            ex = shap.TreeExplainer(r["model"].m); sv = ex.shap_values(Xn[r["te"]])
                            sv = sv[1] if isinstance(sv, list) else sv
                            if sv.ndim == 3: sv = sv[:, :, -1]
                            acc += np.abs(sv).sum(axis=0); n_acc += len(r["te"])
                        imp = acc / max(n_acc, 1); order = np.argsort(-imp)[:20]
                        st["shap_top20"] = [dict(feature=cols[j], mean_abs_shap=round(float(imp[j]), 5)) for j in order]
                        log(f"  SHAP top5: {[(cols[j], round(float(imp[j]), 4)) for j in order[:5]]}")
                    except Exception as e:
                        st["shap_error"] = repr(e); log(f"  SHAP failed: {e!r}")
                # sensitivities
                st["decay"] = None
                if spec["decay"]:
                    recs_d = run_oof(spec["make"], T, Xn, Fx, decay=True, tag=name + "_decay")
                    rr = H.score(T, pooled(recs_d, T), fam + "/decay", cfg(name, "decay_c0.5"), script=SCRIPT, controls=False, note=note() + "; time-decay c=0.5 sensitivity")
                    st["decay"] = dict(id=rr["id"], kept_share=rr["kept_share"], diff=rr["diff"], diff_top1_removed=rr["diff_top1_removed"], sign_blocks=rr["sign_blocks"], taus=[r["tau"] for r in recs_d])
                st["sens"] = {}
                for sname, smake in spec["sens"].items():
                    recs_s = run_oof(smake, T, Xn, Fx, tag=sname)
                    rr = H.score(T, pooled(recs_s, T), fam + "/sens", cfg(name, "sensitivity", variant=sname), script=SCRIPT, controls=False, note=note())
                    st["sens"][sname] = dict(id=rr["id"], kept_share=rr["kept_share"], diff=rr["diff"], diff_top1_removed=rr["diff_top1_removed"], sign_blocks=rr["sign_blocks"], taus=[r["tau"] for r in recs_s])
                st["seconds"] = round(time.time() - t0, 1); st["rss_mb"] = G.rss_mb()
                st["recs"] = [strip(r) for r in recs]
                res["stages"]["oof12"] = st; save()
                log(f"  {name} oof12 done in {st['seconds']}s")
            # ------------------------------------------------ cpcv
            if "cpcv" in stages and "cpcv" not in res["stages"]:
                t0 = time.time(); by, byr, byt, taus = {}, {}, {}, []
                for i, (tr, te, (ba, bb)) in enumerate(H.cpcv_splits(T)):
                    rec = G.fit_split(name, spec["make"], T, Xn, Fx, cols, info, tr, te, tf, dict(uniq=G.avg_uniqueness(T, tr)))
                    by[(ba, bb)] = rec["keep_te"].astype(float); taus.append(rec.get("tau"))
                    if spec["distil"]:
                        d = G.distill(rec, Xn, Fx, cols, info, tr, te, tf, min_leaf)
                        byr[(ba, bb)] = d["rules"]["keep_te"].astype(float); byt[(ba, bb)] = d["tree"]["keep_te"].astype(float)
                    if i % 11 == 10: log(f"  {name} cpcv split {i + 1}/66 ({time.time() - t0:.0f}s)")
                paths = H.cpcv_paths(T, by)
                dist, rows = H.score_paths(T, paths, fam, cfg(name, "cpcv"), script=SCRIPT, controls=True, threshold=0.5)
                st = dict(dist=dist, path_ids=[r["id"] for r in rows], path_diffs=[r["diff"] for r in rows], path_ctrl=[r["control_pct"] for r in rows],
                          path_kept_share=[r["kept_share"] for r in rows], path_top1=[r["diff_top1_removed"] for r in rows], taus=taus, distill={})
                log(f"  {name} CPCV: median {dist['diff_median']} p5 {dist['diff_p5']} share>0 {dist['diff_share_positive']} ctrl med {dist.get('control_pct_median')}")
                if spec["distil"]:
                    for form, bd in (("rules", byr), ("tree", byt)):
                        pd_ = H.cpcv_paths(T, bd)
                        dd, rr = H.score_paths(T, pd_, fam + f"/distill_{form}", cfg(name, f"distill_{form}_cpcv"), script=SCRIPT, controls=True, threshold=0.5)
                        st["distill"][form] = dict(dist=dd, path_ids=[r["id"] for r in rr], path_diffs=[r["diff"] for r in rr], path_ctrl=[r["control_pct"] for r in rr])
                        log(f"  {name} distilled {form} CPCV: median {dd['diff_median']} p5 {dd['diff_p5']} share>0 {dd['diff_share_positive']}")
                st["seconds"] = round(time.time() - t0, 1); st["rss_mb"] = G.rss_mb()
                res["stages"]["cpcv"] = st; save()
            # ------------------------------------------------ frozen forms
            if "frozen" in stages and "frozen" not in res["stages"] and "oof12" in res["stages"]:
                t0 = time.time(); st = {}
                oof_keep = np.ones(T.n, dtype=bool)
                o = res["stages"]["oof12"]["oof"]; pos = {int(s): i for i, s in enumerate(T.setup_i)}
                for s, k in zip(o["setup_i"], o["keep"]): oof_keep[pos[int(s)]] = bool(k)
                kind = res["stages"]["oof12"]["kind"]
                if spec["distil"] or kind == "prob":
                    bank = G.CondBank(Xn, cols, info, Fx, is_rows)
                    v = np.where(~oof_keep[is_rows], 1.0, -1.0)
                    conds, trace = G.greedy_rules(bank, is_rows, v, "fidelity", min_leaf)
                    rules = G.rules_json(conds, bank); kr = G.rules_keep(Fx, rules, tf)
                    rr = H.score(T, kr, fam + "/frozen_rules", cfg(name, "frozen_rules", rules=rules), script=SCRIPT, controls=True, note=note() + "; distilled from the pooled OOF decisions (selection on pooled OOF, one trial)")
                    st["rules"] = dict(rules=rules, n_rules=len(rules), trace=trace, id=rr["id"], row=rr, fidelity=G.fidelity(kr[is_rows], oof_keep[is_rows]),
                                       features=G.rule_features(rules), ext_features=[f for f in G.rule_features(rules) if info.get(f, {}).get("ext") or any(info[c].get("ext") for c in cols if info[c].get("src") == f)])
                    log(f"  {name} frozen rules ({len(rules)}): id {rr['id']} kept {rr['kept_share']} diff {rr['diff']} ctrl {rr['control_pct']} fidelity {st['rules']['fidelity']['agreement']}")
                if kind == "policy":
                    L = spec["make"](); bank = G.CondBank(Xn, cols, info, Fx, is_rows)
                    net_is = T.net[is_rows]; lo, hi = np.quantile(net_is, [0.01, 0.99])
                    L.fit(Xn[is_rows], T.win[is_rows], None, net_is, dict(bank=bank, rows=is_rows))
                    kr = L.decide(Fx, tf)
                    rr = H.score(T, kr, fam + "/frozen_rules", cfg(name, "frozen_policy", rules=L.rules), script=SCRIPT, controls=True, note=note() + "; the policy learner refit on all IS rows (in-sample, one trial)")
                    st["policy"] = dict(rules=L.rules, n_rules=len(L.rules), id=rr["id"], row=rr, value=L.value, nodes=L.nodes, trace=L.trace, features=G.rule_features(L.rules))
                    log(f"  {name} frozen policy ({len(L.rules)} rules): id {rr['id']} kept {rr['kept_share']} diff {rr['diff']} ctrl {rr['control_pct']}")
                if kind == "score":
                    L = spec["make"](); w, _ = G.make_weights(T.net[is_rows], T.win[is_rows])
                    L.fit(Xn[is_rows], T.win[is_rows], w, T.net[is_rows], dict(cols=cols, info=info))
                    s_all = L.score(Xn); share = float(oof_keep[is_rows].mean())
                    s_min = float(np.quantile(s_all[is_rows], 1 - share)) if share < 1 else -np.inf
                    card = L.to_json(cols, info); card["skip_if_score_below"] = s_min
                    kr, sc, miss = G.scorecard_keep_from_json(Fx, card, s_min, Xn, cols)
                    rr = H.score(T, kr, fam + "/frozen_scorecard", cfg(name, "frozen_scorecard", card=card), script=SCRIPT, controls=True, note=note() + "; refit on all IS, s_min at the pooled OOF kept share (one trial)")
                    st["scorecard"] = dict(card=card, s_min=s_min, id=rr["id"], row=rr, n_src=L.n_src, C=L.C, selected=[cols[j] for j in L.selected],
                                           fidelity=G.fidelity(kr[is_rows], oof_keep[is_rows]))
                    log(f"  {name} frozen scorecard ({L.n_src} features): id {rr['id']} kept {rr['kept_share']} diff {rr['diff']} ctrl {rr['control_pct']}")
                if kind == "prob" and name == "dt3":
                    med = G.impute_fit(Xn[is_rows]); w, _ = G.make_weights(T.net[is_rows], T.win[is_rows])
                    from sklearn.tree import DecisionTreeClassifier
                    dt = DecisionTreeClassifier(max_depth=3, min_samples_leaf=min_leaf, random_state=0).fit(G.impute_apply(Xn[is_rows], med), T.win[is_rows], sample_weight=w)
                    tau_all, _, _ = G.choose_tau(o["p"], T.net[[pos[int(s)] for s in o["setup_i"]]], T.win[[pos[int(s)] for s in o["setup_i"]]], G.TAU_GRID)
                    trules, dropped = G.tree_to_rules(dt, cols, info, tau=tau_all); kt = G.rules_keep(Fx, trules, tf)
                    rr = H.score(T, kt, fam + "/frozen_tree", cfg(name, "frozen_tree", rules=trules, tau=tau_all), script=SCRIPT, controls=True, note=note() + "; the depth-3 tree refit on all IS with tau chosen on pooled OOF (one trial)")
                    st["tree"] = dict(rules=trules, dropped_inexpressible=dropped, tau=tau_all, id=rr["id"], row=rr, features=G.rule_features(trules))
                    log(f"  {name} frozen tree ({len(trules)} rules, tau {tau_all}): id {rr['id']} kept {rr['kept_share']} diff {rr['diff']}")
                st["seconds"] = round(time.time() - t0, 1)
                res["stages"]["frozen"] = st; save()
            # ------------------------------------------------ robustness labels
            if "robust" in stages and "robust" not in res["stages"]:
                t0 = time.time(); st = {}
                for lab in ROBUST_LABELS:
                    try:
                        if lab == "L0":
                            T0 = H.load(tf, "L0")
                            if sub == "context": X0, _, _ = G.context_features(T0); X0 = X0.reindex(columns=cols, fill_value=0.0)
                            else: X0 = G.matrix_for(T0, cols, ind_cover, tf)
                            E0, _ = G.ext_frame(tf, T0.setup_i)
                            Fx0 = pd.concat([T0.F.reset_index(drop=True), E0], axis=1) if sub == "h5_full" else T0.F.reset_index(drop=True)
                            Tt, Xt, Fxt, same_rows = T0, X0.to_numpy(dtype=float), Fx0, False
                        else:
                            if labels is None: raise RuntimeError("labels parquet missing: run labels.py first")
                            Tt, Xt, Fxt, same_rows = G.label_table(T, tf, lab, labels), Xn, Fx, True
                        recs = run_oof(spec["make"], Tt, Xt, Fxt, tag=f"{name}@{lab}")
                        keep = pooled(recs, Tt)
                        r1 = H.score(Tt, keep, fam + "/robust", cfg(name, "robust", train_label=lab, scored_on=lab), script=SCRIPT, controls=False, note=note() + f"; trained on {lab}, scored on {lab}")
                        e = dict(scored_on_label=dict(id=r1["id"], kept_share=r1["kept_share"], diff=r1["diff"], diff_top1_removed=r1["diff_top1_removed"], sign_blocks=r1["sign_blocks"],
                                                      kept_mean=r1["kept_mean"], skipped_mean=r1["skipped_mean"], winner_recall_weighted=r1["winner_recall_weighted"]),
                                 taus=[r["tau"] for r in recs], uniqueness=round(G.avg_uniqueness(Tt, np.flatnonzero(Tt.is_mask)), 4), n_is=int(Tt.is_mask.sum()))
                        if same_rows:
                            r2 = H.score(T, keep, fam + "/robust", cfg(name, "robust", train_label=lab, scored_on="L1"), script=SCRIPT, controls=False, note=note() + f"; trained on {lab}, scored on the L1 book")
                            e["scored_on_L1"] = dict(id=r2["id"], kept_share=r2["kept_share"], diff=r2["diff"], diff_top1_removed=r2["diff_top1_removed"], sign_blocks=r2["sign_blocks"],
                                                     kept_mean=r2["kept_mean"], skipped_mean=r2["skipped_mean"], winner_recall_weighted=r2["winner_recall_weighted"])
                        st[lab] = e
                        log(f"  {name} robust {lab}: on-label diff {r1['diff']} kept {r1['kept_share']}" + (f"; on L1 diff {e['scored_on_L1']['diff']}" if same_rows else ""))
                    except Exception as ex:
                        st[lab] = dict(error=repr(ex), trace=traceback.format_exc()); log(f"  {name} robust {lab} FAILED: {ex!r}")
                st["seconds"] = round(time.time() - t0, 1)
                res["stages"]["robust"] = st; save()
        except Exception as ex:
            log(f"!!! {name} failed: {ex!r}\n{traceback.format_exc()}"); res.setdefault("errors", []).append(dict(error=repr(ex), trace=traceback.format_exc())); save()
        # a JSON twin without arrays
        try:
            j = json.loads(json.dumps({k: v for k, v in res.items()}, default=lambda z: z.tolist() if isinstance(z, np.ndarray) else (z.item() if hasattr(z, "item") else str(z))))
            for stg in ("oof12",):
                if stg in j["stages"]:
                    j["stages"][stg].pop("oof", None); j["stages"][stg].pop("recs", None)
            G.jdump(j, os.path.join(rdir, f"{name}.json"))
        except Exception as ex:
            log(f"  json twin failed for {name}: {ex!r}")
    # ---- oof parquet for this (tf, sub)
    if "diag" in stages:
        frames = []
        for name in specs:
            pkl = os.path.join(rdir, f"{name}.pkl")
            if not os.path.exists(pkl): continue
            res = pickle.load(open(pkl, "rb")); o = res["stages"].get("oof12", {}).get("oof")
            if o is None: continue
            frames.append(pd.DataFrame(dict(setup_i=o["setup_i"].astype(int), tf=tf, sub=sub, model=name, fold=o["fold"].astype(int), score=o["score"], p=o["p"], tau=o["tau"], keep=o["keep"].astype(bool))))
        if frames:
            P = pd.concat(frames, ignore_index=True); P.to_parquet(os.path.join(G.RES, f"oof_{tf}_{sub}.parquet"), index=False)
            log(f"oof parquet: {len(P)} rows -> oof_{tf}_{sub}.parquet")
    log(f"ALL DONE tf={tf} sub={sub} in {time.time() - t_all:.0f}s, peak rss {G.rss_mb()} MB")


if __name__ == "__main__":
    main()
