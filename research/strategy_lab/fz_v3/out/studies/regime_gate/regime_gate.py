"""regime_gate: the chop-state gate (DESIGN_PANEL deep-sequence-regime-states, both judges' fixes) on 5 minutes, L1, IS only.

    python regime_gate.py             # the real run: every cell / nested pick / CPCV path a ledger row; results.json + CSVs
    python regime_gate.py --smoke     # code-path check on a REDIRECTED ledger (scratchpad) with the L1 nets SHUFFLED within IS
                                      # (seed 0) so no real kept-vs-skipped number exists off-ledger; 2 tapes per generator

Definitions: rg_lib.py docstring (fixed before any number was looked at). Never reads an OOS label or feature: the posterior
matrices are filled for IS rows only (NaN elsewhere), every fit / choice / score runs on IS indices.
"""
import os, sys, json, time, argparse, resource
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rg_lib as R                                                      # noqa: E402
H = R.H
import tapes                                                            # noqa: E402  (studies/null_tapes_drift, on sys.path via rg_lib)

T0 = time.time()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - T0:7.1f}s] {msg}", flush=True)


def jsonable(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (np.bool_,)): return bool(o)
    return str(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tapes-per-gen", type=int, default=None, help="smoke only: tapes per generator")
    A = ap.parse_args()
    out_dir = HERE
    controls = True; draws = H.CONTROL_DRAWS
    if A.smoke:
        scratch = os.environ.get("RG_SMOKE_DIR", os.path.join(HERE, "smoke"))
        os.makedirs(scratch, exist_ok=True)
        H.LEDGER = os.path.join(scratch, "ledger"); os.makedirs(H.LEDGER, exist_ok=True)
        out_dir = scratch; controls = False; draws = 50
        log(f"SMOKE: ledger redirected to {H.LEDGER}; labels will be shuffled within IS (seed 0); controls off")
    note = f"{R.VOCAB_NOTE}; regime_gate {R.TF} {R.LABEL}" + ("; SMOKE (shuffled labels, redirected ledger)" if A.smoke else "")

    # ------------------------------------------------------------ the table, the posteriors (IS rows only)
    T = H.load(R.TF, R.LABEL)
    is_idx = np.flatnonzero(T.is_mask)
    if A.smoke:
        rng = np.random.default_rng(0); perm = rng.permutation(len(is_idx))
        T.net = T.net.copy(); T.pts = T.pts.copy()
        T.net[is_idx] = T.net[is_idx][perm]; T.pts[is_idx] = T.pts[is_idx][perm]
        for s in list(T.net_slip): T.net_slip[s] = T.net_slip[s].copy(); T.net_slip[s][is_idx] = T.net_slip[s][is_idx][perm]
        T.win = T.net > 0
        log("SMOKE: L1 net / pts / net_slip shuffled within the IS rows; nothing below is a real number")
    ext = R.load_ext(R.TF)
    P = {}
    for m in R.MODEL_ORDER:
        Pm = np.full((T.n, R.MODELS[m][1]), np.nan)
        Pm[is_idx] = R.posterior_matrix(ext, m, T.setup_i[is_idx])
        P[m] = Pm
    log(f"{R.TF} {R.LABEL}: {T.n} units, IS {len(is_idx)}; posteriors loaded for {R.MODEL_ORDER} (IS rows only)")
    res = dict(study="regime_gate", tf=R.TF, label=R.LABEL, smoke=bool(A.smoke), n_units=int(T.n), n_is=int(len(is_idx)),
               is_mean=round(float(T.net[is_idx].mean()), 2), is_win_rate=round(float(T.win[is_idx].mean()), 4),
               definitions=R.__doc__, taus=R.TAUS, models=R.MODEL_ORDER, vocabulary=R.VOCAB_NOTE, ledger_sha_before=H.ledger_sha())

    # ------------------------------------------------------------ the cluster question (importance study, frozen shortlist)
    sl = json.load(open(os.path.join(R.OUT, "features_shortlist", R.TF, "shortlist.json")))
    hv = sl["h2_vs_state_models"]
    h2_cl = set(hv["h2_clusters"].values()); n_choch_cl = hv["h2_clusters"]["n_choch_since_bos"]
    same = sorted(c for c, cl in hv["state_clusters"].items() if cl == n_choch_cl)
    other = {c: cl for c, cl in hv["state_clusters"].items() if cl != n_choch_cl}
    res["cluster_question"] = dict(shortlist_sha256=None, n_shortlisted=sl["n_shortlisted"], n_clusters_total=sl["n_clusters_total"],
                                   n_choch_since_bos_cluster=n_choch_cl, h2_clusters=hv["h2_clusters"], state_clusters=hv["state_clusters"],
                                   state_columns_in_n_choch_cluster=same, state_columns_elsewhere=other,
                                   any_state_column_shortlisted=bool(set(sl["allowed_columns"]) & set(hv["state_clusters"])),
                                   verdict=("one cluster" if not other else "in part: the CHoCH-like posterior of each model shares the "
                                            f"n_choch_since_bos cluster ({n_choch_cl}); the other posteriors sit in clusters "
                                            f"{sorted(set(other.values()))}; jump3_state / jump3_run form their own cluster {hv['state_clusters']['jump3_state']}"))
    import hashlib
    res["cluster_question"]["shortlist_sha256"] = hashlib.sha256(open(os.path.join(R.OUT, "features_shortlist", R.TF, "shortlist.json"), "rb").read()).hexdigest()
    log(f"cluster question: n_shortlisted {sl['n_shortlisted']}; states in the n_choch cluster {same}; elsewhere {other}")

    # ------------------------------------------------------------ state descriptions (fit report) and expectancy by MAP state (IS, descriptive)
    rep = json.load(open(os.path.join(R.OUT, "features_ext", R.TF, "ext_fit_report.json")))
    desc = {}
    for m in R.MODEL_ORDER:
        kind, K = R.MODELS[m]; r_ = rep[kind][f"K{K}"]
        desc[m] = dict(feature_names=r_["feature_names"], state_means=r_["state_means"], state_share_tape=r_["state_share_tape"],
                       transmat=r_.get("transmat"), expected_dwell_bars=r_.get("expected_dwell_bars"), lambda_star=r_.get("lambda_star"), weights=r_.get("weights"))
    res["state_descriptions"] = desc
    state_tabs = {}
    for m in R.MODEL_ORDER:
        tab = R.state_table(P[m], T.net, T.win, is_idx)
        rc = R.run_columns(m)
        if rc:
            run = ext.loc[T.setup_i[is_idx], rc].to_numpy(dtype=float); mp = np.argmax(P[m][is_idx], axis=1)
            for r_ in tab:
                mm = mp == r_["state"]
                r_["run_median_bars"] = round(float(np.median(run[mm])), 1) if mm.any() else None
        state_tabs[m] = tab
    res["state_tables_is"] = state_tabs
    log("state tables done")

    # ------------------------------------------------------------ grid cells (chop + tau on all IS: trials)
    grid = []; fixed = {}
    for m in R.MODEL_ORDER:
        chop_all, tab_all = R.chop_state(P[m], T.net, T.win, is_idx)
        tau_fixed, tr_ = R.choose_tau(P[m], chop_all, T.net, is_idx)
        fixed[m] = dict(chop=chop_all, tau=tau_fixed, feasible_any=tr_["feasible_any"], trace=tr_["trace"], state_table=tab_all)
        for tau in R.TAUS:
            keep = ~R.skip_mask(P[m], chop_all, tau)
            cfg = dict(model=m, tau=tau, chop_state=chop_all, chop_rule=R.CHOP_RULE, columns=R.posterior_columns(m), vocabulary=R.VOCAB_NOTE)
            r_ = H.score(T, keep, f"regime_gate/{m}", cfg, script=__file__, controls=controls, draws=draws, note=note)
            r_["is_fixed_rule"] = bool(tau == tau_fixed); grid.append(r_)
            log(f"  grid {m} tau {tau} chop {chop_all}: kept {r_['kept_n']} ({r_['kept_share']}) diff {r_['diff']} ctrl {r_['control_pct']} id {r_['id']}")
        fixed[m]["cell_id"] = [g["id"] for g in grid if g["config"]["model"] == m and g["config"]["tau"] == tau_fixed][0]
    res["grid"] = grid; res["fixed_rule"] = fixed

    # ------------------------------------------------------------ nested OOF (12 purged folds)
    nested = {}; fold_recs = {}
    for m in R.MODEL_ORDER:
        recs, dec = R.nested_decisions(P[m], T.net, T.win, list(H.purged_splits(T)), T.n)
        keep = np.where(np.isnan(dec), True, dec < 0.5)
        cfg = dict(model=m, tau="nested", tau_rule=R.TAU_RULE, chop_rule=R.CHOP_RULE, columns=R.posterior_columns(m), vocabulary=R.VOCAB_NOTE,
                   fold_chop=[r_["chop"] for r_ in recs], fold_tau=[r_["tau"] for r_ in recs])
        r_ = H.score(T, keep, f"regime_gate/{m}/nested", cfg, script=__file__, controls=controls, draws=draws, note=note)
        r_["block_diffs"] = R.block_diffs(T, keep, is_idx); r_["keep_mask_is"] = keep[is_idx].astype(int).tolist()
        nested[m] = r_; fold_recs[m] = recs
        log(f"  nested {m}: chops {[x['chop'] for x in recs]} taus {[x['tau'] for x in recs]} kept {r_['kept_n']} ({r_['kept_share']}) diff {r_['diff']} ctrl {r_['control_pct']} perm {r_['perm_p']} blocks {r_['sign_blocks']} id {r_['id']}")
    res["nested"] = nested; res["nested_folds"] = fold_recs

    # ------------------------------------------------------------ CPCV (66 splits -> 11 paths) of the nested procedure
    cpcv = {}; cpcv_splits_rec = {}
    for m in R.MODEL_ORDER:
        oof = {}; recs = []
        for tr, te, key in H.cpcv_splits(T):
            chop, tab = R.chop_state(P[m], T.net, T.win, tr)
            tau, tr_ = R.choose_tau(P[m], chop, T.net, tr)
            sk = R.skip_mask(P[m], chop, tau)[te]
            oof[key] = (~sk).astype(float)
            recs.append(dict(split=list(key), chop=chop, tau=tau, feasible_any=tr_["feasible_any"], test_kept_share=round(float(1 - sk.mean()), 4)))
        paths = H.cpcv_paths(T, oof)
        cfg = dict(model=m, tau="nested", tau_rule=R.TAU_RULE, chop_rule=R.CHOP_RULE, columns=R.posterior_columns(m), vocabulary=R.VOCAB_NOTE, scheme="cpcv 66 splits, 11 paths")
        dist, prows = H.score_paths(T, paths, f"regime_gate/{m}/nested", cfg, script=__file__, controls=controls, threshold=0.5)
        dist["path_rows"] = [dict(id=x["id"], path=x["config"]["path"], kept_share=x["kept_share"], diff=x["diff"], diff_top1_removed=x["diff_top1_removed"],
                                  control_pct=x["control_pct"], sign_blocks=x["sign_blocks"]) for x in prows]
        dist["distinct_picks"] = sorted({(r_["chop"], r_["tau"]) for r_ in recs}); dist["distinct_picks"] = [list(x) for x in dist["distinct_picks"]]
        dist["splits"] = recs
        cpcv[m] = dist
        log(f"  cpcv {m}: diff median {dist['diff_median']} p5 {dist['diff_p5']} min {dist['diff_min']} share>0 {dist['diff_share_positive']} kept median {dist['kept_share_median']} picks {dist['distinct_picks']}")
    res["cpcv"] = cpcv

    # ------------------------------------------------------------ distillation of the fixed rule (label-free target)
    X, src = R.base_design(T)
    res["distillation_features"] = dict(n_columns=int(X.shape[1]), removed_time_proxies=sorted(H.TIME_PROXIES))
    dist_rec = {}; distilled_rows = {}
    for m in R.MODEL_ORDER:
        y = R.skip_mask(P[m], fixed[m]["chop"], fixed[m]["tau"]).astype(int)
        rec, oof = R.distil(T, X, src, y, is_idx, log=log)
        dist_rec[m] = rec
        log(f"  distil {m}: skip share {rec['skip_share']} fidelity OOF {rec['fidelity_oof']} (majority {rec['majority_baseline']}) in-sample {rec['fidelity_in_sample']} expressible {rec['expressible']} features {rec['features_used']}")
        if rec["expressible"]:
            keep = np.where(np.isnan(oof), True, oof < 0.5)
            cfg = dict(model=m, form="depth-3 tree distilled from the fixed rule", fixed_chop=fixed[m]["chop"], fixed_tau=fixed[m]["tau"],
                       rules=[{"if": r_["if"], "then": "skip"} for r_ in rec["rules"]], vocabulary=R.VOCAB_NOTE)
            r_ = H.score(T, keep, f"regime_gate/{m}/distilled", cfg, script=__file__, controls=controls, draws=draws, note=note)
            distilled_rows[m] = r_
            log(f"  distilled gate {m}: kept {r_['kept_n']} diff {r_['diff']} id {r_['id']}")
    res["distillation"] = dist_rec; res["distilled_rows"] = distilled_rows

    # ------------------------------------------------------------ the family (every regime_gate ledger row) and per-row statistics
    fam_rows = H.read_ledger("regime_gate", tf=R.TF, label=R.LABEL)
    fam, fam_vecs = R.family_stats(fam_rows, tag=f"regime_gate|{R.TF}")
    sub_rows = [r_ for r_ in fam_rows if "/cpcv" not in r_["family"]]
    fam_sub, _ = R.family_stats(sub_rows, tag=f"regime_gate|{R.TF}|no_cpcv")
    res["family"] = dict(all_rows=fam, grid_nested_distilled_only=fam_sub, families=sorted({r_["family"] for r_ in fam_rows}))
    log(f"family: {fam['n_rows']} rows, PBO(diff) {fam['pbo_diff']['pbo']}, SPA p {fam['spa'].get('spa_p')} (unstud {fam['spa'].get('spa_p_unstudentised')}), eff trials {fam['effective_trials']}")
    per_row = {}
    for m in R.MODEL_ORDER:
        for kind, row in (("nested", nested[m]), ("fixed", [g for g in grid if g["id"] == fixed[m]["cell_id"]][0])):
            vec = H.load_vectors(row["id"])
            boot = H.bootstrap_ci(vec, draws=draws if A.smoke else H.BOOT_DRAWS, tag=f"regime_gate|{R.TF}|{m}|{kind}")
            dsr = H.deflated_sharpe(R.per_session_kept_mean(vec), n_trials=fam["n_rows"], sr_var_trials=fam["sr_var_trials"])
            per_row[f"{m}/{kind}"] = dict(id=row["id"], boot=boot, dsr=dsr)
    res["per_row"] = per_row

    # ------------------------------------------------------------ the matched H2 comparator (real ledger rows, by id)
    real_ledger = os.path.join(R.OUT, "ledger", "trials.jsonl")
    ledger_by_id = {}
    for line in open(real_ledger, encoding="utf-8"):
        if line.strip():
            rr = json.loads(line)
            if rr["id"] in set(R.H2_IDS.values()) | {R.SFI25_ID}: ledger_by_id[rr["id"]] = rr
    h2 = {k: ledger_by_id[v] for k, v in R.H2_IDS.items() if v in ledger_by_id}
    matched = {}
    for m in R.MODEL_ORDER:
        s = nested[m]["kept_share"]; out = {}
        for scope in ("all", "today"):
            cands = [(abs(h2[(scope, k)]["kept_share"] - s), k) for k in (2, 3, 4) if (scope, k) in h2]
            if not cands: continue
            k = min(cands)[1]; row = h2[(scope, k)]
            out[scope] = dict(kc=k, id=row["id"], kept_share=row["kept_share"], diff=row["diff"], diff_top1_removed=row["diff_top1_removed"],
                              control_pct=row["control_pct"], perm_p=row["perm_p"], sign_blocks=row["sign_blocks"],
                              nested_beats=(nested[m]["diff"] is not None and nested[m]["diff"] > row["diff"]))
        matched[m] = out
    res["matched_h2"] = matched
    res["sfi_cluster25_row"] = {k: ledger_by_id[R.SFI25_ID].get(k) for k in ("id", "config", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "sign_blocks", "kept_mean_slip8", "winner_recall_weighted")} if R.SFI25_ID in ledger_by_id else None

    # ------------------------------------------------------------ null tapes: refit the frozen models, verify, replay the fixed rule
    log("refitting the frozen state models on the real fit window (as build_ext.py did)")
    frozen = R.fit_frozen_models(os.path.join(R.OUT, "data", R.TF), log=log)
    setup_all = np.sort(pd.read_parquet(os.path.join(R.OUT, "data", R.TF, "features.parquet"), columns=["setup_i"]).setup_i.to_numpy())
    ver = R.verify_refit(frozen, ext, setup_all)
    res["refit_verification"] = ver
    ok_refit = all((v["max_abs_diff"] < 1e-6 and v["identical_map"]) for v in ver.values())
    log(f"refit verification vs ext_features.parquet at {len(setup_all)} SETUPs: {ver} -> {'OK' if ok_refit else 'MISMATCH'}")
    tape_res = {m: dict(diffs={"gmm": [], "segment": [], "session": []}, per_tape=[]) for m in R.MODEL_ORDER}
    tape_note = None
    if not ok_refit:
        tape_note = "refit of the frozen state models did not reproduce ext_features.parquet; tapes not replayed"
    else:
        n_per = A.tapes_per_gen if A.smoke else None
        for gen in ("gmm", "segment", "session"):
            folders = tapes.tape_folders(R.TF, gen)
            if n_per: folders = folders[:n_per]
            for folder in folders:
                post = R.tape_posteriors(frozen, folder)
                Tt = tapes.load_tape(folder, R.LABEL)
                if A.smoke:
                    rng = np.random.default_rng(1); pp = rng.permutation(Tt.n); Tt.net = Tt.net[pp]; Tt.win = Tt.net > 0
                for m in R.MODEL_ORDER:
                    Pt = post[m][Tt.setup_i]
                    keep = ~R.skip_mask(Pt, fixed[m]["chop"], fixed[m]["tau"])
                    met = tapes.evaluate_keep(Tt, keep, f"regime_gate|{m}|{os.path.basename(folder)}", controls=False)
                    d = np.nan if met["diff"] is None else met["diff"]
                    tape_res[m]["diffs"][gen].append(d)
                    tape_res[m]["per_tape"].append(dict(gen=gen, k=tapes._tape_k(folder), n=met["n"], kept_share=met["kept_share"], diff=met["diff"], sign_blocks=met["sign_blocks"]))
                log(f"  tape {gen}_{tapes._tape_k(folder)}: " + ", ".join(f"{m} {tape_res[m]['per_tape'][-1]['diff']}" for m in R.MODEL_ORDER))
    null_tape = {}
    for m in R.MODEL_ORDER:
        fixed_row = [g for g in grid if g["id"] == fixed[m]["cell_id"]][0]
        if tape_note:
            null_tape[m] = dict(reason=tape_note)
            continue
        passed, ch, summ = tapes.null_tape_check_from_diffs(fixed_row["diff"], tape_res[m]["diffs"])
        passed_n, ch_n, summ_n = tapes.null_tape_check_from_diffs(nested[m]["diff"], tape_res[m]["diffs"])
        null_tape[m] = dict(real_diff_fixed=fixed_row["diff"], passed_fixed=passed, checks_fixed=ch, summary_fixed=summ,
                            real_diff_nested=nested[m]["diff"], passed_nested=passed_n, checks_nested=ch_n, summary_nested=summ_n,
                            n_tapes={g: len(v) for g, v in tape_res[m]["diffs"].items()},
                            tape_set="certificate (healthy, first DESIGN_N per generator)" if not A.smoke else "smoke subset")
        log(f"  null tapes {m}: fixed diff {fixed_row['diff']} vs gmm p95 {summ['gmm']['p95']} / segment p95 {summ['segment']['p95']} / session same-sign {summ['session']['same_sign_share']} -> {passed}")
    res["null_tapes"] = dict(per_model=null_tape, per_tape={m: tape_res[m]["per_tape"] for m in R.MODEL_ORDER}, note=tape_note)

    # ------------------------------------------------------------ go / no-go and the verdict
    gng = {}
    for m in R.MODEL_ORDER:
        nt = null_tape[m]
        nt_arg = nt["checks_fixed"] if "checks_fixed" in nt else nt.get("reason")
        p, ch = H.go_no_go(nested[m], R.TF, cpcv=cpcv[m], pbo_value=fam["pbo_diff"]["pbo"], dsr=per_row[f"{m}/nested"]["dsr"], spa_p=fam["spa"].get("spa_p"),
                           boot=per_row[f"{m}/nested"]["boot"], null_tape=nt_arg, columns=R.posterior_columns(m))
        fixed_row = [g for g in grid if g["id"] == fixed[m]["cell_id"]][0]
        p2, ch2 = H.go_no_go(fixed_row, R.TF, cpcv=cpcv[m], pbo_value=fam["pbo_diff"]["pbo"], dsr=per_row[f"{m}/fixed"]["dsr"], spa_p=fam["spa"].get("spa_p"),
                             boot=per_row[f"{m}/fixed"]["boot"], null_tape=nt_arg, columns=R.posterior_columns(m))
        beats = matched[m].get("all", {}).get("nested_beats")
        gng[m] = dict(nested=dict(passed=p, checks=ch, failing=[k for k, v in ch.items() if not v[0]]), fixed=dict(passed=p2, checks=ch2, failing=[k for k, v in ch2.items() if not v[0]]),
                      beats_matched_h2_all=beats, candidate=bool(p and beats))
        log(f"  go/no-go {m}: nested passed {p} (failing {gng[m]['nested']['failing']}); fixed passed {p2}; beats matched H2 {beats}; candidate {gng[m]['candidate']}")
    res["go_no_go"] = gng
    cands = [m for m in R.MODEL_ORDER if gng[m]["candidate"]]
    res["candidates"] = []
    for m in cands:
        rec = dist_rec[m]; nt = null_tape[m]
        cand = dict(kind="regime_gate", tf=R.TF, label=R.LABEL, model=m,
                    config=(dict(rules=[{"if": r_["if"], "then": "skip"} for r_ in rec["rules"]]) if rec["expressible"] else
                            dict(alternative_needing_user_decision=f"fz key {{'regime': {{'model': '{m}', 'chop_state': {fixed[m]['chop']}, 'skip_if_p_chop_ge': {fixed[m]['tau']}, ...frozen parameters...}}}}: 40-60 numbers plus a forward filter in fz code; not expressible as a depth-3 tree (fidelity {rec['fidelity_oof']})")),
                    provenance=dict(source="learned on IS 2021-10..2025-12", script="studies/regime_gate/regime_gate.py", ledger_id=nested[m]["id"],
                                    fixed_rule_ledger_id=fixed[m]["cell_id"], statistic=dict(diff=nested[m]["diff"], control_pct=nested[m]["control_pct"], perm_p=nested[m]["perm_p"]),
                                    vocabulary=R.VOCAB_NOTE, null_tape=dict(checks=nt.get("checks_fixed"), summary={k: v for k, v in nt.get("summary_fixed", {}).items() if k != "per_tape"}),
                                    go_no_go=dict(passed=gng[m]["nested"]["passed"], checks=gng[m]["nested"]["checks"]), user_decision_required=True))
        res["candidates"].append(cand)
        json.dump(cand, open(os.path.join(out_dir, f"candidate_{m}.json"), "w"), indent=1, default=jsonable)
    res["null_result"] = not cands
    res["ledger_sha_after"] = H.ledger_sha()
    res["runtime_s"] = round(time.time() - T0, 1); res["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)

    # ------------------------------------------------------------ write
    json.dump(res, open(os.path.join(out_dir, "results.json"), "w"), indent=1, default=jsonable)
    pd.DataFrame([dict(model=g["config"]["model"], tau=g["config"]["tau"], chop=g["config"]["chop_state"], fixed_rule=g["is_fixed_rule"], id=g["id"],
                       **{k: g[k] for k in ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall",
                                            "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks")}) for g in grid]
                 ).to_csv(os.path.join(out_dir, "grid.csv"), index=False)
    pd.DataFrame([dict(model=m, fold=i, **{k: r_[k] for k in ("n_train", "n_test", "chop", "tau", "feasible_any", "chop_train_n", "chop_train_mean", "test_skipped", "test_kept_share")})
                  for m in R.MODEL_ORDER for i, r_ in enumerate(fold_recs[m])]).to_csv(os.path.join(out_dir, "nested_folds.csv"), index=False)
    pd.DataFrame([dict(model=m, **x) for m in R.MODEL_ORDER for x in cpcv[m]["path_rows"]]).to_csv(os.path.join(out_dir, "cpcv_paths.csv"), index=False)
    pd.DataFrame([dict(model=m, **x) for m in R.MODEL_ORDER for x in state_tabs[m]]).to_csv(os.path.join(out_dir, "state_tables_is.csv"), index=False)
    pd.DataFrame([dict(model=m, **x) for m in R.MODEL_ORDER for x in tape_res[m]["per_tape"]]).to_csv(os.path.join(out_dir, "tape_diffs.csv"), index=False)
    log(f"done: {len(fam_rows)} ledger rows in the family; candidates {cands or 'none (null result)'}; results -> {out_dir}/results.json; "
        f"runtime {res['runtime_s']}s, max RSS {res['max_rss_mb']} MB; ledger sha {res['ledger_sha_after']}")


if __name__ == "__main__":
    main()
