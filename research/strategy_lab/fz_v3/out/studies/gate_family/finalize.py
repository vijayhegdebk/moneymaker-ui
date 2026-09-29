"""gate_family finalize: the family multiplicity (PBO / SPA / effective trials over every gate_family ledger row of the timeframe
with label L1; DSR with n_trials = the family size), the finalist per sub-family (the distilled rule list or the scorecard with
the better CPCV 5th percentile), harness.go_no_go with every argument filled, the null-tape certificate (tapes.null_tape_check),
the drift refit (drift.json top5_sources), the candidate JSON (at most one per timeframe, only when go/no-go AND the null-tape
check pass) or the null result, FINDINGS.md and findings.json.

    python finalize.py                 # both timeframes; reads results/<tf>/<sub>/<model>.pkl, the ledger, the labels JSON
"""
import os, sys, json, time, pickle, hashlib, datetime as D, traceback
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import gf_lib as G      # noqa: E402
H, tapes = G.H, G.tapes
SCRIPT = os.path.abspath(__file__)
TFS = ["minute", "5minute"]; SUBS = ["context", "h5_full"]
CAND_DIR = os.path.join(G.OUT, "candidates")
IMP = json.load(open(os.path.join(G.OUT, "studies", "importance", "findings.json")))
DRIFT = json.load(open(os.path.join(G.OUT, "studies", "null_tapes_drift", "drift.json")))
log = G.Log(os.path.join(HERE, "finalize.log"))


def fmt(x, nd=2):
    if x is None: return "-"
    if isinstance(x, (bool, np.bool_)): return "yes" if x else "no"
    if isinstance(x, (int, np.integer)): return f"{int(x):,}"
    if isinstance(x, float):
        if not np.isfinite(x): return "-"
        return f"{x:,.{nd}f}"
    return str(x)


def load_results(tf, sub):
    d = os.path.join(G.RES, tf, sub); out = {}
    if not os.path.isdir(d): return out
    for f in sorted(os.listdir(d)):
        if f.endswith(".pkl"):
            try: out[f[:-4]] = pickle.load(open(os.path.join(d, f), "rb"))
            except Exception as e: log(f"cannot load {f}: {e!r}")
    return out


def ledger_rows(tf):
    rows = H.read_ledger(G.STUDY, tf=tf, label=None)
    seen = {}
    for r in rows: seen[r["id"]] = r          # append-only ledger: a rerun of a finished stage cannot happen (checkpoints); keep the last copy per id
    return list(seen.values())


def family_stats(tf):
    rows = ledger_rows(tf); l1 = [r for r in rows if r["label"] == "L1"]
    vecs, ids = [], []
    for r in l1:
        try: vecs.append(H.load_vectors(r["id"])); ids.append(r["id"])
        except Exception: pass
    out = dict(n_rows_all_labels=len(rows), n_rows_L1=len(l1), n_vectors=len(vecs),
               rows_by_family={k: int(v) for k, v in pd.Series([r["family"] for r in rows]).value_counts().sort_index().items()},
               rows_by_sub={s: int(sum(1 for r in rows if r["family"].startswith(f"{G.STUDY}/{s}"))) for s in SUBS})
    if len(vecs) >= 2:
        t0 = time.time()
        out["pbo_diff"] = H.pbo(vecs, "diff"); out["pbo_kept_mean"] = H.pbo(vecs, "kept_mean")
        out["spa"] = H.spa(vecs, tag=f"gate_family|{tf}"); out["effective_trials"] = H.effective_trials(vecs)
        srs = []
        for v in vecs:
            m = v["kept_n"] > 0; x = v["kept_sum"][m] / v["kept_n"][m]
            srs.append(float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan)
        out["sr_var_family"] = float(np.nanvar(np.array(srs), ddof=1)) if np.isfinite(srs).sum() > 1 else None
        out["seconds"] = round(time.time() - t0, 1)
        log(f"{tf} family: {len(rows)} rows ({len(l1)} L1), PBO(diff) {out['pbo_diff']['pbo']}, SPA p {out['spa'].get('spa_p')} (unstud {out['spa'].get('spa_p_unstudentised')}), eff trials {out['effective_trials']}, {out['seconds']}s")
    out["vec_ids"] = ids
    return out, vecs, ids


def dsr_for(vec, n_trials, sr_var):
    m = vec["kept_n"] > 0; x = np.where(m, vec["kept_sum"] / np.maximum(vec["kept_n"], 1), 0.0)[m]
    return H.deflated_sharpe(x, n_trials, sr_var if sr_var and sr_var > 0 else None)


def rowsum(r):
    if r is None: return None
    return {k: r.get(k) for k in ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct",
                                  "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "sign_blocks", "kept_mean_slip8", "kept_pf")}


_FEAT = {}


def feats(tf, sub):
    """The (Table, design X, column info, feature frame) of a (tf, sub), as run_gf built them; cached per process."""
    if (tf, sub) not in _FEAT:
        T = H.load(tf)
        if sub == "context": X, info, _ = G.context_features(T); Fx = T.F.reset_index(drop=True)
        else:
            T, X, info, fmeta, cl, pairs, E = G.full_features(tf, None); Fx = pd.concat([T.F.reset_index(drop=True), E.reset_index(drop=True)], axis=1)
        _FEAT[(tf, sub)] = (T, X, info, Fx)
    return _FEAT[(tf, sub)]


def pooled_oof_keep(T, res):
    o = res["stages"]["oof12"]["oof"]; pos = {int(s): i for i, s in enumerate(T.setup_i)}
    oof_keep = np.ones(T.n, dtype=bool)
    for s, k in zip(o["setup_i"], o["keep"]): oof_keep[pos[int(s)]] = bool(k)
    return oof_keep


def frozen_tree_for(tf, sub, name, results):
    """The frozen counterpart of the nested 'distilled tree' form: the same depth-3 DecisionTreeClassifier (min leaf 100 / 40) fit on
    all IS rows to the learner's POOLED 12-block OOF decisions (never the label), converted to skip rules by gf_lib.tree_to_rules and
    scored once (family gate_family/<sub>/<model>/frozen_tree: a selection on pooled OOF, one trial, like the frozen rule list run_gf
    writes). Cached in results/<tf>/<sub>/frozen_tree.json so a rerun of finalize never appends a second ledger row."""
    cache_p = os.path.join(G.RES, tf, sub, "frozen_tree.json")
    cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    if name in cache: return cache[name]
    if QUICK: return None
    t0 = time.time()
    T, X, info, Fx = feats(tf, sub); cols = list(X.columns); Xn = X.to_numpy(float); is_rows = np.flatnonzero(T.is_mask)
    oof_keep = pooled_oof_keep(T, results[name])
    from sklearn.tree import DecisionTreeClassifier
    med = G.impute_fit(Xn[is_rows])
    dt = DecisionTreeClassifier(max_depth=3, min_samples_leaf=G.MIN_LEAF[tf], random_state=0).fit(G.impute_apply(Xn[is_rows], med), oof_keep[is_rows].astype(int))
    trules, dropped = G.tree_to_rules(dt, cols, info); kt = G.rules_keep(Fx, trules, tf)
    vocab = "inside the frozen vocabulary (context columns)" if sub == "context" else "outside the frozen shortlist (importance rule failed for every cluster)"
    rr = H.score(T, kt, f"{G.STUDY}/{sub}/{name}/frozen_tree", dict(sub=sub, model=name, stage="frozen_tree", label="L1", vocabulary=vocab, rules=trules), script=SCRIPT,
                 controls=True, note=G.SUB_NOTE[sub] + "; the depth-3 tree distilled from the pooled OOF decisions (selection on pooled OOF, one trial)")
    ent = dict(rules=trules, n_rules=len(trules), dropped_inexpressible=int(dropped), id=rr["id"], row=json.loads(json.dumps(rr, default=lambda z: z.item() if hasattr(z, "item") else str(z))),
               fidelity=G.fidelity(kt[is_rows], oof_keep[is_rows]), features=G.rule_features(trules), seconds=round(time.time() - t0, 1))
    cache[name] = ent; G.jdump(cache, cache_p)
    log(f"  {tf}/{sub}/{name} frozen tree ({len(trules)} rules): id {rr['id']} kept {rr['kept_share']} diff {rr['diff']} ctrl {rr['control_pct']} fidelity {ent['fidelity']['agreement']}")
    return ent


def finalist_set(tf, sub, results):
    """Every rule-list / scorecard form with a nested OOF row and a CPCV distribution."""
    out = []
    for name, res in results.items():
        st = res["stages"]; o = st.get("oof12"); c = st.get("cpcv"); f = st.get("frozen", {})
        if not o: continue
        kind = o.get("kind")
        if kind == "policy":
            out.append(dict(model=name, form="policy_rules", label=f"{name} (rule list by construction)", oof=rowsum(o["row"]), cpcv=(c or {}).get("dist"),
                            frozen=f.get("policy"), frozen_kind="rules", fidelity=None))
        if "distill" in o:
            for form in ("rules", "tree"):
                if form not in o["distill"]: continue
                d = o["distill"][form]
                out.append(dict(model=name, form=f"distill_{form}", label=f"{name} -> distilled {form}", oof=rowsum(d["row"]), cpcv=((c or {}).get("distill", {}).get(form) or {}).get("dist"),
                                frozen=f.get("rules") if form == "rules" else frozen_tree_for(tf, sub, name, results), frozen_kind="rules", fidelity=d.get("fidelity_oof")))
        if kind == "score":
            out.append(dict(model=name, form="scorecard", label=f"{name} (scorecard)", oof=rowsum(o["row"]), cpcv=(c or {}).get("dist"),
                            frozen=f.get("scorecard"), frozen_kind="scorecard", fidelity=None))
        if kind == "prob" and name == "dt3" and f.get("tree"):
            out.append(dict(model=name, form="tree_rules", label="dt3 (tree rules at the nested tau)", oof=rowsum(o["row"]), cpcv=(c or {}).get("dist"),
                            frozen=f.get("tree"), frozen_kind="rules", fidelity=None))
    return out


def null_tape_for(tf, fin):
    """The null-tape certificate for a frozen rule list / scorecard; ext-features columns are not on the tapes (not evaluable)."""
    fz = fin.get("frozen")
    if not fz: return dict(evaluable=False, reason="no frozen form")
    real_row = fz.get("row") or {}; real_diff = real_row.get("diff")
    if real_diff is None: return dict(evaluable=False, reason="the frozen form's real-tape diff is undefined (nothing skipped or nothing kept)")
    try:
        if fin["frozen_kind"] == "rules":
            rules = fz.get("rules") or []
            if not rules: return dict(evaluable=False, reason="the frozen rule list is empty (take everything)")
            passed, ch, summ = tapes.null_tape_check(real_diff, tf, {"rules": rules}, controls=False)
        else:
            card, s_min = fz["card"], fz["s_min"]; diffs, per = {}, []
            for g in ("gmm", "segment", "session"):
                diffs[g] = []
                for folder in tapes.tape_folders(tf, g):
                    Tt = tapes.load_tape(folder)
                    keep, sc, miss = G.scorecard_keep_from_json(Tt.F, card, s_min)
                    if miss: raise KeyError(f"columns not on the tapes: {miss}")
                    m = tapes.evaluate_keep(Tt, keep, f"tape|{os.path.basename(folder)}|scorecard", controls=False)
                    diffs[g].append(np.nan if m["diff"] is None else m["diff"]); per.append(dict(gen=g, tape=os.path.basename(folder), diff=m["diff"], kept_share=m["kept_share"]))
            passed, ch, summ = tapes.null_tape_check_from_diffs(real_diff, diffs); summ["per_tape"] = per
        summ.pop("per_tape_full", None)
        return dict(evaluable=True, passed=bool(passed), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, summary={k: v for k, v in summ.items() if k != "per_tape"},
                    n_tapes=len(summ.get("per_tape", [])), real_diff=real_diff)
    except Exception as e:
        return dict(evaluable=False, reason=f"{type(e).__name__}: {e}", real_diff=real_diff)


def frozen_features(fin):
    fz = fin.get("frozen") or {}
    if fin["frozen_kind"] == "rules": return sorted({c[0] for r in (fz.get("rules") or []) for c in r["if"]})
    card = fz.get("card") or {}
    return sorted({f.get("src", c) for c, f in card.get("features", {}).items()})


def drift_refit(tf, sub, fin, results):
    """The finalist's frozen form refit without the drift.json top-5 drifted source features it uses (frozen form only: the
    nested learner is not rerun)."""
    top5 = DRIFT["timeframes"][tf]["top5_sources"]
    used = [f for f in frozen_features(fin) if f in top5]
    if not used: return dict(uses_top5_drifted=[], refit=None)
    t0 = time.time()
    T = H.load(tf)
    if sub == "context": X, info, _ = G.context_features(T); Fx = T.F.reset_index(drop=True)
    else:
        T, X, info, fmeta, cl, pairs, E = G.full_features(tf, None); Fx = pd.concat([T.F.reset_index(drop=True), E.reset_index(drop=True)], axis=1)
    keep_cols = [c for c in X.columns if info[c].get("src", c) not in top5 and c.split("=")[0] not in top5]
    X2 = X[keep_cols]; cols = keep_cols; info2 = {c: info[c] for c in cols}; Xn = X2.to_numpy(float); is_rows = np.flatnonzero(T.is_mask)
    res = results[fin["model"]]; o = res["stages"]["oof12"]["oof"]; pos = {int(s): i for i, s in enumerate(T.setup_i)}
    oof_keep = np.ones(T.n, dtype=bool)
    for s, k in zip(o["setup_i"], o["keep"]): oof_keep[pos[int(s)]] = bool(k)
    fam = f"{G.STUDY}/{sub}/{fin['model']}"
    cfg = dict(sub=sub, model=fin["model"], stage="drift_refit", label="L1", dropped=used, form=fin["form"])
    if fin["frozen_kind"] == "rules" and fin["form"] == "distill_tree":
        from sklearn.tree import DecisionTreeClassifier
        med = G.impute_fit(Xn[is_rows])
        dt = DecisionTreeClassifier(max_depth=3, min_samples_leaf=G.MIN_LEAF[tf], random_state=0).fit(G.impute_apply(Xn[is_rows], med), oof_keep[is_rows].astype(int))
        rules, dropped = G.tree_to_rules(dt, cols, info2); kr = G.rules_keep(Fx, rules, tf)
        rr = H.score(T, kr, fam + "/drift_refit", dict(cfg, rules=rules), script=SCRIPT, controls=True, note="drift refit of the frozen distilled tree")
        ref = dict(rules=rules, dropped_inexpressible=int(dropped), row=rowsum(rr))
    elif fin["frozen_kind"] == "rules" and fin["form"].startswith("distill"):
        bank = G.CondBank(Xn, cols, info2, Fx, is_rows); v = np.where(~oof_keep[is_rows], 1.0, -1.0)
        conds, trace = G.greedy_rules(bank, is_rows, v, "fidelity", G.MIN_LEAF[tf]); rules = G.rules_json(conds, bank)
        kr = G.rules_keep(Fx, rules, tf); rr = H.score(T, kr, fam + "/drift_refit", dict(cfg, rules=rules), script=SCRIPT, controls=True, note="drift refit of the frozen distilled rule list")
        ref = dict(rules=rules, row=rowsum(rr))
    elif fin["frozen_kind"] == "rules":
        L = G.PolicyLearner("ptree" if fin["model"].startswith("pt") else "h5rules", int(fin["model"][-1]) if fin["model"].startswith("pt") else None, G.MIN_LEAF[tf])
        bank = G.CondBank(Xn, cols, info2, Fx, is_rows)
        L.fit(Xn[is_rows], T.win[is_rows], None, T.net[is_rows], dict(bank=bank, rows=is_rows)); kr = L.decide(Fx, tf)
        rr = H.score(T, kr, fam + "/drift_refit", dict(cfg, rules=L.rules), script=SCRIPT, controls=True, note="drift refit of the frozen policy rule list")
        ref = dict(rules=L.rules, row=rowsum(rr))
    else:
        L = G.ScorecardLearner(G.SC_MAX[tf]); w, _ = G.make_weights(T.net[is_rows], T.win[is_rows])
        L.fit(Xn[is_rows], T.win[is_rows], w, T.net[is_rows], dict(cols=cols, info=info2)); s_all = L.score(Xn); share = float(oof_keep[is_rows].mean())
        s_min = float(np.quantile(s_all[is_rows], 1 - share)) if share < 1 else -np.inf
        card = L.to_json(cols, info2); card["skip_if_score_below"] = s_min
        kr, sc, miss = G.scorecard_keep_from_json(Fx, card, s_min, Xn, cols)
        rr = H.score(T, kr, fam + "/drift_refit", dict(cfg, card=card), script=SCRIPT, controls=True, note="drift refit of the frozen scorecard")
        ref = dict(card=card, s_min=s_min, row=rowsum(rr))
    ref["seconds"] = round(time.time() - t0, 1)
    return dict(uses_top5_drifted=used, refit=ref)


def judge(tf, sub, fin, fam, vecs_by_id, null_tape=None):
    """go/no-go on the nested OOF row with the nested CPCV, the family PBO / SPA, the DSR (n_trials = family size), the bootstrap,
    the columns the frozen form reads (harness TIME_PROXIES / NOT_FEATURES refused) and the null-tape checks (the sub-family
    finalist is replayed on the certificate tapes; every other form records the reason and the item fails, as the harness requires)."""
    res = fin["oof"]; cpcv = fin["cpcv"]
    if res is None or res.get("id") not in vecs_by_id: return dict(passed=False, checks={}, reason="no vector for the OOF row")
    vec = vecs_by_id[res["id"]]
    dsr = dsr_for(vec, fam["n_rows_all_labels"], fam.get("sr_var_family"))
    boot = H.bootstrap_ci(vec, tag=f"gate_family|{tf}|{sub}|{fin['model']}|{fin['form']}")
    pbo_v = fam.get("pbo_diff", {}).get("pbo"); spa_p = fam.get("spa", {}).get("spa_p")
    cols = frozen_features(fin)
    nt_arg = null_tape if null_tape is not None else "not evaluated: only the sub-family finalist (best nested CPCV p5) is replayed on the certificate tapes"
    ok, ch = H.go_no_go(res, tf, cpcv=cpcv if cpcv else None, pbo_value=pbo_v, dsr=dsr, spa_p=spa_p, boot=boot, null_tape=nt_arg, columns=cols)
    return dict(passed=bool(ok), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, dsr=dsr, boot=boot, n_fail=int(sum(1 for v in ch.values() if not v[0])),
                cpcv_p5=(cpcv or {}).get("diff_p5"), columns=cols)


def sha256_file(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def write_candidate(tf, sub, fin, jd, nt, fam, script_sha):
    os.makedirs(CAND_DIR, exist_ok=True)
    fz = fin["frozen"]
    body = {"kind": "rule_list" if fin["frozen_kind"] == "rules" else "scorecard", "default": "take", "label": "foundation_intraday_1525", "square_off": "15:25", "tf": tf}
    if fin["frozen_kind"] == "rules": body["rules"] = fz["rules"]
    else: body["scorecard"] = fz["card"]
    prov = dict(source="learned on IS 2021-10..2025-12", script="studies/gate_family/run_gf.py + finalize.py", script_sha=script_sha, study=G.STUDY,
                sub_family=sub, model=fin["model"], form=fin["form"], ledger_id=fin["oof"]["id"], frozen_ledger_id=(fz.get("row") or {}).get("id"),
                cpcv=fin["cpcv"], pbo=fam.get("pbo_diff", {}).get("pbo"), dsr_p=(jd.get("dsr") or {}).get("p"), spa_p=fam.get("spa", {}).get("spa_p"),
                boot_ci=(jd.get("boot") or {}).get("diff_ci"), trials=fam["n_rows_all_labels"], effective_trials=fam.get("effective_trials"),
                fidelity=fin.get("fidelity"),
                # the two blocks oos_once.py requires (program rule of 2026-09-29 12:55 UTC): the tape checks / summary and the go/no-go from the same call
                null_tape={"checks": nt.get("checks"), "summary": nt.get("summary"), "real_diff": nt.get("real_diff"), "n_tapes": nt.get("n_tapes")},
                go_no_go={"passed": bool(jd.get("passed")), "checks": jd["checks"]},
                columns=jd.get("columns"),
                statistic="kept-vs-skipped mean L1 net (INR per trade)", is_window="2021-10-01..2025-12-31")
    if sub == "h5_full": prov["vocabulary"] = "outside the frozen shortlist (importance rule failed for every cluster)"
    else: prov["vocabulary"] = "inside the frozen vocabulary (hour_bin one-hot + dir: the design's context columns)"
    body["provenance"] = prov
    p = os.path.join(CAND_DIR, f"gate_family_{tf}.json")
    with open(p, "w", encoding="utf-8") as f: json.dump(body, f, indent=1, default=str)
    sha = sha256_file(p)
    with open(os.path.join(G.OUT, "ledger", "registrations.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"kind": "candidate", "what": f"gate_family candidate {tf}", "file": f"candidates/gate_family_{tf}.json", "sha256": sha,
                            "registered_at": D.datetime.now().isoformat(timespec="seconds"), "ledger_id": fin["oof"]["id"], "vocabulary": prov["vocabulary"]}) + "\n")
    return p, sha


# ---------------------------------------------------------------- the tables
SUB_TAG = {"context": "(I) context, inside the frozen vocabulary", "h5_full": "(II) h5_full, OUTSIDE THE FROZEN SHORTLIST"}


def model_table(results, sub):
    lines = ["| sub-family | model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        o = res["stages"].get("oof12")
        if not o: lines.append(f"| {SUB_TAG[sub]} | {name} | {res['desc']} | not run | | | | | | | | | | | | | | | |"); continue
        r = o["row"]; taus = o.get("taus")
        lines.append(f"| {SUB_TAG[sub]} | {name} | {res['desc']} | `{r['id']}` | {fmt(r['kept_n'])} | {fmt(r['kept_share'], 4)} | {fmt(r['kept_mean'])} | {fmt(r['skipped_mean'])} | **{fmt(r['diff'])}** | {fmt(r['diff_top1_removed'])} | {fmt(r['perm_p'], 4)} | {fmt(r['control_pct'], 1)} | "
                     f"{fmt(r['loser_recall'], 3)} / {fmt(r['loser_precision'], 3)} | {fmt(r['winner_recall_weighted'], 3)} | {fmt(r['top_decile_winners_skipped'], 3)} | {fmt(r['sign_blocks'])} | {fmt(r['kept_mean_slip8'])} | "
                     f"{' '.join(fmt(t, 2) for t in taus) if taus and taus[0] is not None else '-'} | {sum(1 for x in o.get('tau_constraint_satisfied', []) if x) if o.get('tau_constraint_satisfied') and o['tau_constraint_satisfied'][0] is not None else '-'} |")
    return "\n".join(lines)


def cpcv_table(results):
    lines = ["| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        c = res["stages"].get("cpcv")
        if not c: continue
        d = c["dist"]
        lines.append(f"| {name} | learner | {d['paths']} | {fmt(d['diff_median'])} | **{fmt(d['diff_p5'])}** | {fmt(d['diff_min'])} | {fmt(d['diff_share_positive'], 3)} | {fmt(d['kept_share_median'], 4)} | {fmt(d.get('control_pct_median'), 1)} / {fmt(d.get('control_pct_p5'), 1)} | {', '.join('`' + i + '`' for i in c['path_ids'][:3])} |")
        for form, dd in c.get("distill", {}).items():
            d = dd["dist"]
            lines.append(f"| {name} | distilled {form} (nested) | {d['paths']} | {fmt(d['diff_median'])} | **{fmt(d['diff_p5'])}** | {fmt(d['diff_min'])} | {fmt(d['diff_share_positive'], 3)} | {fmt(d['kept_share_median'], 4)} | {fmt(d.get('control_pct_median'), 1)} / {fmt(d.get('control_pct_p5'), 1)} | {', '.join('`' + i + '`' for i in dd['path_ids'][:3])} |")
    return "\n".join(lines)


def tau_table(results):
    lines = ["| model | tau | OOF id | kept share | diff | diff top-1% off | sign blocks |", "|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        o = res["stages"].get("oof12")
        if not o or not o.get("tau_rows"): continue
        for tau, r in o["tau_rows"].items():
            lines.append(f"| {name} | {tau} | `{r['id']}` | {fmt(r['kept_share'], 4)} | {fmt(r['diff'])} | {fmt(r['diff_top1_removed'])} | {fmt(r['sign_blocks'])} |")
    return "\n".join(lines)


def distill_table(results, ftrees=None):
    lines = ["| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        o = res["stages"].get("oof12"); f = res["stages"].get("frozen", {})
        if not o: continue
        for form in ("rules", "tree"):
            d = (o.get("distill") or {}).get(form)
            if not d: continue
            r = d["row"]; fid = d["fidelity_oof"]; fz = f.get("rules") if form == "rules" else (ftrees or {}).get(name)
            fr = (fz or {}).get("row") or {}
            rules_txt = "; ".join(" AND ".join(f"{c[0]} {c[1]} {c[2]}" for c in ru["if"]) for ru in (fz or {}).get("rules", [])) if fz else "-"
            lines.append(f"| {name} | {form} | `{r['id']}` | {fmt(r['kept_share'], 4)} | {fmt(r['diff'])} | {fmt(r['diff_top1_removed'])} | {fmt(r['control_pct'], 1)} | {fmt(r['sign_blocks'])} | {fmt(fid['agreement'], 3)} / {fmt(fid['skip_precision'], 3)} / {fmt(fid['skip_recall'], 3)} | "
                         f"{fmt(float(np.median(d['n_rules'])), 1)} | {('`' + fr['id'] + '`') if fr else '-'} | {fmt(fr.get('kept_share'), 4)} | {fmt(fr.get('diff'))} | {fmt(fr.get('control_pct'), 1)} | {fmt((fz or {}).get('fidelity', {}).get('agreement'), 3) if fz else '-'} | {rules_txt[:400]} |")
        for key, lab in (("policy", "policy refit on all IS"), ("scorecard", "scorecard refit on all IS"), ("tree", "tree refit on all IS")):
            fz = f.get(key)
            if not fz: continue
            fr = fz["row"]
            if key == "scorecard":
                txt = "; ".join(f"{c}: bins {v['bins']} points {v['points']}" if v["bins"] else f"{c}: {v['points']}" for c, v in fz["card"]["features"].items()) + f"; skip if score < {fmt(fz['s_min'], 2)}"
            else: txt = "; ".join(" AND ".join(f"{c[0]} {c[1]} {c[2]}" for c in ru["if"]) for ru in fz.get("rules", []))
            lines.append(f"| {name} | {lab} | - | - | - | - | - | - | {fmt((fz.get('fidelity') or {}).get('agreement'), 3) if fz.get('fidelity') else 'by construction'} | {len(fz.get('rules', []))} | `{fr['id']}` | {fmt(fr['kept_share'], 4)} | {fmt(fr['diff'])} | {fmt(fr['control_pct'], 1)} | - | {txt[:400] or '(empty: take everything)'} |")
    return "\n".join(lines)


def robust_table(results):
    lines = ["| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        rb = res["stages"].get("robust")
        if not rb: continue
        for lab in ("L0", "L2x1", "L2x2", "L3"):
            e = rb.get(lab)
            if not e: continue
            if "error" in e: lines.append(f"| {name} | {lab} | failed: {e['error'][:80]} | | | | | | | | | | | | | |"); continue
            a = e["scored_on_label"]; b = e.get("scored_on_L1") or {}
            taus = e.get("taus"); ts = " ".join(fmt(t, 2) for t in taus) if taus and taus[0] is not None else "-"
            lines.append(f"| {name} | {lab} | {fmt(e['n_is'])} | {fmt(e['uniqueness'], 3)} | {ts} | `{a['id']}` | {fmt(a['kept_share'], 4)} | {fmt(a['diff'])} | {fmt(a['diff_top1_removed'])} | {fmt(a['sign_blocks'])} | {fmt(a['winner_recall_weighted'], 3)} | "
                         f"{('`' + b['id'] + '`') if b else 'n/a (other rows)'} | {fmt(b.get('kept_share'), 4)} | {fmt(b.get('diff'))} | {fmt(b.get('diff_top1_removed'))} | {fmt(b.get('sign_blocks'))} |")
    return "\n".join(lines)


def sens_table(results):
    lines = ["| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |", "|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        o = res["stages"].get("oof12")
        if not o: continue
        if o.get("decay"):
            d = o["decay"]; lines.append(f"| {name} | time decay c = 0.5 | `{d['id']}` | {fmt(d['kept_share'], 4)} | {fmt(d['diff'])} | {fmt(d['diff_top1_removed'])} | {fmt(d['sign_blocks'])} | {' '.join(fmt(t, 2) for t in d['taus']) if d['taus'][0] is not None else '-'} |")
        for v, d in (o.get("sens") or {}).items():
            lines.append(f"| {name} | {v} | `{d['id']}` | {fmt(d['kept_share'], 4)} | {fmt(d['diff'])} | {fmt(d['diff_top1_removed'])} | {fmt(d['sign_blocks'])} | {' '.join(fmt(t, 2) for t in d['taus']) if d['taus'][0] is not None else '-'} |")
    return "\n".join(lines)


def hour_table(results):
    models = [n for n, r in results.items() if r["stages"].get("oof12")]
    if not models: return ""
    hours = list(results[models[0]]["stages"]["oof12"]["kept_share_by_hour"].keys())
    lines = ["| hour_bin | n | " + " | ".join(f"{m} kept share" for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for hb in hours:
        cells = [results[m]["stages"]["oof12"]["kept_share_by_hour"][hb] for m in models]
        lines.append(f"| {hb} | {fmt(cells[0]['n'])} | " + " | ".join(fmt(c['kept_share'], 3) for c in cells) + " |")
    lines.append("| **regime** | | " + " | ".join("" for _ in models) + " |")
    for rg in ("choch<2_since_bos", "choch>=2_since_bos"):
        cells = [results[m]["stages"]["oof12"]["kept_share_by_regime"].get(rg, dict(n=0, kept_share=None)) for m in models]
        lines.append(f"| {rg} | {fmt(cells[0]['n'])} | " + " | ".join(fmt(c['kept_share'], 3) for c in cells) + " |")
    for dd in ("down", "up"):
        cells = [results[m]["stages"]["oof12"]["kept_share_by_dir"].get(dd, dict(n=0, kept_share=None)) for m in models]
        lines.append(f"| dir = {dd} | {fmt(cells[0]['n'])} | " + " | ".join(fmt(c['kept_share'], 3) for c in cells) + " |")
    return "\n".join(lines)


def calib_table(results):
    lines = ["| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |", "|---|---|---|---|---|---|---|---|---|"]
    for name, res in results.items():
        o = res["stages"].get("oof12")
        if not o or not o.get("calibration"): continue
        c = o["calibration"]
        rel = "; ".join(f"[{b['lo']},{b['hi']}): {b['n']}, {b['mean_p']:.3f}, {b['win_rate']:.3f}" for b in c["reliability"])
        lines.append(f"| {name} | {fmt(o.get('oof_auc'), 4)} | {fmt(c['mean_p'], 4)} | {fmt(c['base_rate'], 4)} | {fmt(c['brier'], 5)} | {fmt(c['brier_base'], 5)} | {fmt(c['brier_skill'], 4)} | {fmt(c['ece'], 4)} | {rel} |")
    return "\n".join(lines)


def shap_table(results):
    o = (results.get("hgbc") or {}).get("stages", {}).get("oof12", {})
    if not o.get("shap_top20"): return f"SHAP not available: {o.get('shap_error', 'hgbc not run')}"
    return "| rank | feature | mean abs SHAP (log-odds, OOF rows, 12 fold models) |\n|---|---|---|\n" + "\n".join(f"| {i + 1} | `{d['feature']}` | {fmt(d['mean_abs_shap'], 5)} |" for i, d in enumerate(o["shap_top20"]))


def compute_table(tf):
    lines = ["| sub-family | model | stage | seconds | RSS MB |", "|---|---|---|---|---|"]
    for sub in SUBS:
        for name, res in load_results(tf, sub).items():
            for stg, st in res["stages"].items():
                lines.append(f"| {sub} | {name} | {stg} | {fmt(st.get('seconds'), 1)} | {fmt(st.get('rss_mb'), 1)} |")
    for sub in SUBS:
        lp = os.path.join(HERE, f"run_{tf}_{sub}.log")
        if os.path.exists(lp):
            last = [l for l in open(lp, encoding="utf-8") if "ALL DONE" in l]
            if last: lines.append(f"| {sub} | all | wall | {last[-1].split(' in ')[-1].split('s')[0]} | peak {last[-1].split('peak rss')[-1].strip()} |")
    return "\n".join(lines)


QUICK = "--quick" in sys.argv          # dry test on partial results: no null tapes, no drift refit (no ledger row), no candidate file


def main():
    out = dict(study=G.STUDY, generated_at=D.datetime.now().isoformat(timespec="seconds"), timeframes={}, candidates=[], null_result=True, ledger_families=[], caveats=[], files=[], quick_dry_run=QUICK)
    script_sha = {os.path.basename(p): G.sha256_file(p)[:16] for p in (os.path.join(HERE, "gf_lib.py"), os.path.join(HERE, "run_gf.py"), os.path.join(HERE, "labels.py"), SCRIPT)}
    md = [f"# gate_family: FINDINGS (the ONE learned-gate trial family; DESIGN_PANEL quant-ml-canon-meta-label-gate merged with decision-making-1-fullinfo-bandit-policy-tree-gate and BRIEF H5; both judges' fixes binding)", "",
          f"Generated {out['generated_at']} by `finalize.py` from `results/<tf>/<sub>/<model>.pkl`, the harness ledger and `results/labels_<tf>.json`. **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 intraday book) trains and judges; L0 / L2 / L3 are one robustness table (never candidates). Every number below is a harness ledger row (id given) or an output file of this folder; nothing is invented. Scripts: `labels.py`, `gf_lib.py`, `run_gf.py`, `finalize.py` (shas {script_sha}); logs `labels_<tf>.log`, `run_<tf>_<sub>.log` (the per-stage log of each (tf, sub); the minute / context log holds the killed first attempt and the restart), `procA.nohup` (5minute context, 5minute h5_full, minute context until the kill), `procA2.nohup` (the minute / context restart), `procB.nohup` / `procB2.nohup` (minute h5_full), `procC.nohup` / `procD.nohup` (the 5minute scorecard and 5minute h5_full reruns), `finalize.log`, `finalize_dry2.log`, `finalize_full.nohup`.", "",
          "## 0. Result in one paragraph", "", "@@RESULT@@", "",
          "## 1. The empty-shortlist rule and the two sub-families", "",
          "`features_shortlist/<tf>/shortlist.json` (sha-registered 2026-09-29T11:31:33, corrected 12:07:12) has **n_shortlisted = 0 on both timeframes** (0 of 38 / 39 clusters pass the pre-registered clustered-MDA rule; `allowed_columns = []`; no newer shortlist line exists in `ledger/registrations.jsonl`), so the EMPTY-SHORTLIST RULE of the task applies and TWO sub-families are run and reported side by side:", "",
          "- **(I) `context`** — features = `hour_bin` one-hot (9 levels) + `dir` (as `dir=down`; `dir=up` is its complement): the context the design always includes and the user's own words (\"it is different for different times\"). Inside the frozen vocabulary. Models (a)-(e) reduce to what two context columns allow; the policy trees over hour_bin x dir are the natural form; (e) is the hour-bin scorecard.",
          "- **(II) `h5_full`** — H5 exactly as pre-registered in `docs/STRATEGY_ANALYSIS_TODO.md` S49, on the FULL as-of table: `imp_lib.assemble(tf)` (the importance study's 276 / 238-feature matrix: `harness.design` + the 61 `features_ext` columns, its drops and missing indicators) MINUS the two calendar proxies `drift.json` names (`sl`, `n_events_asof`: null_tapes_drift FINDINGS section 6 — a rule on a time proxy is a calendar rule and the gate studies refuse it on the real tape by the same rule `tapes.rule_mask` enforces on the tapes) = **274 / 236 features**. **Every row of this sub-family is OUTSIDE THE FROZEN SHORTLIST** (the importance rule failed for every cluster); a candidate from it would carry `provenance.vocabulary = \"outside the frozen shortlist (importance rule failed for every cluster)\"` for the user to accept or reject. Its models: the H5 depth-3 tree (`dt3`), the H5 greedy rule list by kept expectancy (`h5rules`), the HGB (b) as the gradient-boosting ceiling (`hgbc`, with the unconstrained variant as a sensitivity), the scorecard (e) with at most 12 / 6 source features; the bagging ceiling is the importance study's own (cited, not refit).", "",
          "Both sub-families are ONE ledger family (`gate_family/*`): PBO, SPA and the effective trial count are computed over every row of the timeframe with label L1, and the DSR's `n_trials` is the number of gate_family rows of the timeframe over all labels.", "",
          "## 2. Definitions (fixed before the numbers; `gf_lib.py` docstring verbatim)", "", "```", G.__doc__.strip(), "```", "",
          f"Implementation notes that belong to the definitions: (i) {G.HGB_BINNING_NOTE} — sklearn 1.9's weighted bin mapper costs ~25 s per fit on this box (measured 1.8 s without weights / 27 s with / 22 s at 20 iterations) and changes only the bin edges; (ii) controls (2,000-draw session-matched random control, permutation p) are ON for every headline OOF row, every CPCV path, every distilled row and every frozen form, and OFF for the fixed-tau grid rows, the time-decay / structural sensitivity rows and the robustness-label rows (they are trials for PBO / SPA, never candidates; their per-session vectors are saved like every row's); (iii) the inner CV for the nested tau uses 4 contiguous groups of the training fold's blocks with the harness purge and embargo (`harness._purge`); the bagging uses its out-of-bag probabilities instead (the importance study's rule); (iv) the policy learners carry the DM-1 selection floor kept share >= 20% of the training rows inside their search (the value-maximising tree on a book whose expectancy is negative in every cell would otherwise skip everything: every leaf's sum is <= 0; the constrained optimum switches skip leaves to take in decreasing order of leaf mean until the floor is met, and the H5 rule list refuses a rule that would take the kept share under the floor); (v) the frozen rule list distilled from the pooled OOF decisions and the scorecard / policy learner refit on all IS are selections on pooled OOF and are counted as trials (one ledger row each); (vi) a rule list is evaluated everywhere with `tapes.rule_mask` on the feature frame (NaN never satisfies a comparison; a `__na` indicator or a `=nan` one-hot level is not expressible and is excluded from every rule / scorecard search), so what is scored is what would ship; ext-features columns are expressible on the real tape (joined on `setup_i`) but not on the null tapes, and a rule on one is flagged.", "",
          "## 3. The ceiling this family is read against (importance study, not refit)", "",
          "| tf | ledger id | model | OOF AUC | OOF weighted log-loss | gate kept share | diff | CPCV diff median / p5 / share > 0 | family PBO (diff) | SPA p |", "|---|---|---|---|---|---|---|---|---|---|"]
    for tf in TFS:
        fmx = IMP["timeframes"][tf]["full_model"]; famx = IMP["timeframes"][tf]["family"]; g = fmx["gate"]; c = fmx["cpcv"]
        md.append(f"| {tf} | `{fmx['ledger_id']}` | bagging 300 x depth-4 on {IMP['timeframes'][tf]['n_features']} features, training-fold tau | {fmt(fmx['oof_auc'], 4)} | {fmt(fmx['oof_wlogloss'], 5)} | {fmt(g['kept_share'], 4)} | {fmt(g['diff'])} | {fmt(c['diff_median'])} / {fmt(c['diff_p5'])} / {fmt(c['diff_share_positive'], 3)} | {fmt(famx['pbo']['pbo'], 4)} | {fmt(famx['spa']['spa_p'], 4)} |")
    md += ["", "The ceiling model (the 276-feature bagging, OOF AUC 0.59 on 1 min, 0.50 on 5 min, an OOF gate that keeps every row at the training-fold tau, CPCV diff median -19 / +259 with 5th percentiles -115 / -314) bounds what any learned gate on this table can do: a model with all the information the table holds ranks winners barely above chance and its gate cannot separate kept from skipped across the paths. Every number of this study is read against it.", ""]
    all_fin = {}
    for tf in TFS:
        log(f"=== {tf}")
        fam, vecs, ids = family_stats(tf); vecs_by_id = dict(zip(ids, vecs))
        tfo = dict(family=fam, sub_families={}, finalists={}, candidate=None)
        labj = json.load(open(os.path.join(G.RES, f"labels_{tf}.json"))) if os.path.exists(os.path.join(G.RES, f"labels_{tf}.json")) else None
        md += [f"## {4 if tf == 'minute' else 5}. {tf} (L1: {fam and ''}IS units {labj['is_units'] if labj else '-'}, mean {fmt(labj['l1_is_mean']) if labj else '-'} INR/trade, win rate {fmt(labj['l1_is_win_rate'], 4) if labj else '-'})", ""]
        if labj:
            md += ["### Labels built here (robustness only; `results/labels_" + tf + ".json`)", "",
                   "| label | definition | IS mean | IS win rate / share positive | exits | check |", "|---|---|---|---|---|---|",
                   f"| L2x1 | triple barrier, upper = entry + 1 x stop distance | {fmt(labj['L2x1']['is_mean'])} INR | {fmt(labj['L2x1']['is_win_rate'], 4)} | {labj['L2x1']['reasons']} | the L2 stop leg reproduces {labj['checks']['l2_reproduces_l1_stop']} of the {labj['checks']['l1_stop_exits']} L1 stop exits bar-for-bar and price-for-price (the rest are target-first by design); mismatches {labj['checks']['l2_stop_mismatch_n']} |",
                   f"| L2x2 | upper = entry + 2 x stop distance | {fmt(labj['L2x2']['is_mean'])} INR | {fmt(labj['L2x2']['is_win_rate'], 4)} | {labj['L2x2']['reasons']} | same stop leg |",
                   f"| L3 | trend-scanning t at the max-|t| horizon, signed by dir | {fmt(labj['L3']['is_mean_t'], 4)} (t units) | {fmt(labj['L3']['is_share_positive'], 4)} | h* median {labj['L3']['h_star_median']} bars; units with < 5 same-session bars {labj['L3']['is_nbars_lt5']} | dimensionless: the `kept mean slip 8` column of an L3 row is meaningless and not read |", ""]
        for sub in SUBS:
            results = load_results(tf, sub)
            tag = "(I) context — inside the frozen vocabulary" if sub == "context" else "(II) h5_full — OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)"
            md += [f"### {tf} / sub-family {tag}", ""]
            if not results: md += ["not run", ""]; continue
            fj = os.path.join(G.RES, tf, sub, "features.json"); fmeta = json.load(open(fj)) if os.path.exists(fj) else {}
            if sub == "h5_full" and fmeta:
                fm = fmeta.get("fmeta", {}); sm = fmeta.get("smeta", {})
                md += [f"Feature matrix: base design {fm.get('base_design_cols')} + ext {fm.get('ext_cols')} -> {fm.get('n_features_final')} after the importance study's drops -> **{fm.get('n_features_final_after_proxies')}** after dropping the time proxies {fm.get('dropped_time_proxies')}. HGB interaction_cst: {sm.get('interaction_cst')}; monotonic_cst: {sm.get('monotonic_cst')}. Interaction pairs of the shortlist file: {fm.get('interaction_pairs')} (pairs with a time proxy: {fm.get('pairs_with_time_proxy')}; both rooms pairs are used as HGB interaction groups; the rule searches of this sub-family are H5 as pre-registered, i.e. over the whole table, outside the shortlist).", ""]
            ftrees = {n: frozen_tree_for(tf, sub, n, results) for n, r in results.items() if (r["stages"].get("oof12") or {}).get("distill")}
            ftrees = {n: v for n, v in ftrees.items() if v}
            md += ["#### OOF (12 purged blocks, nested tau; controls on)", "", model_table(results, sub), "",
                   "Reading: `-` in a kept-vs-skipped column = the gate skipped nothing (or kept nothing) in the pooled OOF, so the difference is undefined. A tau of 0.10 = the grid floor: no threshold on the grid kept >= 90% of the |net|-weighted winner net with a higher kept mean than keeping everything (the column 'tau constraint met' counts the folds where a grid value satisfied the recall constraint).", "",
                   "#### The fixed-tau grid (every tau tried = a trial; controls off)", "", tau_table(results) or "no probability learner", "",
                   "#### CPCV (66 splits, 11 paths; controls on)", "", cpcv_table(results) or "not run", "",
                   "#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS; the frozen tree of a 'tree' row is fit by finalize.py, family `.../frozen_tree`)", "", distill_table(results, ftrees) or "no distillable learner", "",
                   "#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)", "", robust_table(results) or "not run", "",
                   "#### Sensitivities (controls off)", "", sens_table(results) or "none", "",
                   "#### Kept share by hour bin, regime and direction (pooled OOF decisions)", "", hour_table(results), "",
                   "#### Calibration of the probability learners on OOF (unweighted)", "", calib_table(results) or "none", "",
                   "#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)", "", shap_table(results), ""]
            # finalists of this sub-family
            fins = finalist_set(tf, sub, results)
            judged = []
            for fin in fins:
                jd = judge(tf, sub, fin, fam, vecs_by_id) if fam.get("pbo_diff") else dict(passed=False, checks={}, reason="family statistics unavailable")
                judged.append(dict(fin=fin, judge=jd))
            judged_ok = [j for j in judged if j["fin"]["cpcv"] and j["fin"]["cpcv"].get("diff_p5") is not None]
            best = max(judged_ok, key=lambda j: j["fin"]["cpcv"]["diff_p5"]) if judged_ok else None
            nt = dr = None
            if best:
                fin = best["fin"]
                if QUICK: nt, dr = dict(evaluable=False, reason="quick dry run: null tapes not evaluated"), dict(uses_top5_drifted=[f for f in frozen_features(fin) if f in DRIFT["timeframes"][tf]["top5_sources"]], refit=None, note="quick dry run")
                else:
                    nt = null_tape_for(tf, fin)
                    try: dr = drift_refit(tf, sub, fin, results)
                    except Exception as e: dr = dict(error=repr(e), trace=traceback.format_exc()[-800:])
                best["judge"] = judge(tf, sub, fin, fam, vecs_by_id, null_tape=(nt["checks"] if nt.get("evaluable") else f"not evaluable: {nt.get('reason')}")) if fam.get("pbo_diff") else best["judge"]
            md += ["#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p, boot, columns and (for the finalist) the null-tape checks filled", "",
                   "| sub-family | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for j in judged:
                f_, jd = j["fin"], j["judge"]; r = f_["oof"] or {}
                fails = [k for k, v in jd.get("checks", {}).items() if not v[0]]
                md.append(f"| {SUB_TAG[sub]} | {f_['label']} | `{r.get('id', '-')}` | {fmt(r.get('kept_share'), 4)} | {fmt(r.get('diff'))} | {fmt(r.get('diff_top1_removed'))} | {fmt(r.get('control_pct'), 1)} | {fmt(r.get('sign_blocks'))} | {fmt((f_['cpcv'] or {}).get('diff_p5'))} | {fmt((f_['cpcv'] or {}).get('diff_median'))} | {fmt((f_.get('fidelity') or {}).get('agreement'), 3) if f_.get('fidelity') else '-'} | {fmt((jd.get('dsr') or {}).get('p'), 4)} | {(jd.get('boot') or {}).get('diff_ci', '-')} | {jd.get('n_fail', '-')} / {len(jd.get('checks', {}))} | {', '.join(fails) if fails else ('PASS' if jd.get('passed') else jd.get('reason', '-'))} |")
            md.append("")
            sub_out = dict(models={n: json.loads(json.dumps({k: v for k, v in r["stages"].items() if k != "oof12"} | {"oof12": {kk: vv for kk, vv in r["stages"].get("oof12", {}).items() if kk not in ("oof", "recs")}} if "oof12" in r["stages"] else {k: v for k, v in r["stages"].items()}, default=lambda z: z.tolist() if isinstance(z, np.ndarray) else (z.item() if hasattr(z, "item") else str(z)))) for n, r in results.items()},
                           finalist_set=[dict(label=j["fin"]["label"], model=j["fin"]["model"], form=j["fin"]["form"], oof=j["fin"]["oof"], cpcv=j["fin"]["cpcv"], fidelity=j["fin"]["fidelity"], judge=j["judge"]) for j in judged],
                           vocabulary=("inside the frozen vocabulary" if sub == "context" else "outside the frozen shortlist (importance rule failed for every cluster)"))
            if best:
                fin, jd = best["fin"], best["judge"]
                fz = fin.get("frozen") or {}; fr = fz.get("row") or {}
                md += [f"**Finalist of the sub-family** (best nested CPCV 5th percentile): **{fin['label']}** — nested OOF `{(fin['oof'] or {}).get('id')}`, CPCV p5 {fmt(fin['cpcv']['diff_p5'])}, go/no-go **{'PASS' if jd['passed'] else 'FAIL'}** ({jd.get('n_fail')} items failed). Frozen form: `{fr.get('id', '-')}` kept share {fmt(fr.get('kept_share'), 4)}, diff {fmt(fr.get('diff'))}, control pct {fmt(fr.get('control_pct'), 1)}; features used: {frozen_features(fin)}.", "",
                       "| go/no-go item | ok | value |", "|---|---|---|"] + [f"| {k} | {fmt(v[0])} | {v[1]} |" for k, v in jd.get("checks", {}).items()] + [""]
                if nt.get("evaluable"):
                    s = nt["summary"]
                    md += [f"Null tapes (`tapes.null_tape_check`, certificate set, {nt['n_tapes']} tapes): real diff {fmt(nt['real_diff'])}; gmm p50 / p95 {fmt(s['gmm']['p50'])} / {fmt(s['gmm']['p95'])} (real pct {fmt(s['gmm']['real_pct'], 1)}); segment p50 / p95 {fmt(s['segment']['p50'])} / {fmt(s['segment']['p95'])} (real pct {fmt(s['segment']['real_pct'], 1)}); session same-sign share {fmt(s['session']['same_sign_share'], 3)}; **{'PASS' if nt['passed'] else 'FAIL'}** ({nt['checks']}).", ""]
                else: md += [f"Null tapes: not evaluable — {nt.get('reason')}.", ""]
                if dr and dr.get("refit"):
                    rr = dr["refit"]["row"]
                    md += [f"Drift refit (the frozen form uses top-5 drifted source features {dr['uses_top5_drifted']}; refit without them, ledger `{rr['id']}`): kept share {fmt(rr['kept_share'], 4)}, diff {fmt(rr['diff'])} (was {fmt(fr.get('diff'))}), diff top-1% off {fmt(rr['diff_top1_removed'])}, control pct {fmt(rr['control_pct'], 1)}, sign blocks {fmt(rr['sign_blocks'])}; refit rules / card: `{json.dumps(dr['refit'].get('rules', dr['refit'].get('card')), default=str)[:600]}`.", ""]
                elif dr and "error" in dr: md += [f"Drift refit failed: {dr['error']}", ""]
                else: md += [f"Drift refit: the frozen form uses none of the top-5 drifted source features ({DRIFT['timeframes'][tf]['top5_sources']}); nothing to refit.", ""]
                sub_out["finalist"] = dict(label=fin["label"], model=fin["model"], form=fin["form"], oof=fin["oof"], cpcv=fin["cpcv"], frozen=json.loads(json.dumps(fz, default=str)), judge=jd, null_tape=nt, drift_refit=json.loads(json.dumps(dr, default=str)), features=frozen_features(fin))
                all_fin[(tf, sub)] = dict(fin=fin, judge=jd, null_tape=nt, sub=sub)
            else:
                md += ["No form of this sub-family has a nested CPCV distribution (stage not finished): no finalist.", ""]
            tfo["sub_families"][sub] = sub_out
        # family
        md += [f"### {tf} family multiplicity (every `gate_family/*` ledger row of the timeframe)", ""]
        if fam.get("pbo_diff"):
            md += [f"| rows (all labels) | rows (L1) | vectors | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials | SR variance across the family |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                   f"| {fam['n_rows_all_labels']} | {fam['n_rows_L1']} | {fam['n_vectors']} | **{fmt(fam['pbo_diff']['pbo'], 4)}** | {fmt(fam['pbo_diff']['oos_best_below_zero'], 4)} | {fmt(fam['pbo_kept_mean']['pbo'], 4)} | **{fmt(fam['spa'].get('spa_p'), 4)}** | {fmt(fam['spa'].get('rc_p'), 4)} | {fmt(fam['spa'].get('best_mean_gain'))} ({fmt(fam['spa'].get('best_t'), 3)}) | {fam['spa'].get('excluded_from_studentised')} | {fmt(fam['spa'].get('spa_p_unstudentised'), 4)} | {fmt(fam['effective_trials'])} | {fmt(fam.get('sr_var_family'), 6)} |", "",
                   f"Rows by family: {fam['rows_by_family']}", ""]
        else: md += ["family statistics unavailable (fewer than 2 L1 rows)", ""]
        # candidate decision
        cands = [(k, v) for k, v in all_fin.items() if k[0] == tf and v["judge"].get("passed") and v["null_tape"].get("evaluable") and v["null_tape"].get("passed") and not QUICK]
        near = [(k, v) for k, v in all_fin.items() if k[0] == tf]
        if cands:
            cands.sort(key=lambda kv: -(kv[1]["fin"]["cpcv"]["diff_p5"]))
            (tf_, sub_), v = cands[0]
            p, sha = write_candidate(tf, sub_, v["fin"], v["judge"], v["null_tape"], fam, script_sha)
            tfo["candidate"] = dict(file=os.path.relpath(p, G.OUT), sha256=sha, sub=sub_, form=v["fin"]["form"], model=v["fin"]["model"])
            out["candidates"].append(dict(tf=tf, **tfo["candidate"])); out["null_result"] = False
            md += [f"### {tf} candidate", "", f"**Frozen**: `{os.path.relpath(p, G.OUT)}` (sha256 `{sha}`, registered in `ledger/registrations.jsonl`), sub-family {sub_} ({'OUTSIDE THE FROZEN SHORTLIST' if sub_ == 'h5_full' else 'inside the frozen vocabulary'}), form {v['fin']['form']} of {v['fin']['model']}.", ""]
        else:
            md += [f"### {tf} candidate: **none** (null result)", "",
                   "No rule-list or scorecard form of either sub-family passes `harness.go_no_go` with every argument filled AND the null-tape certificate. The near-miss table is the finalist-set table of each sub-family above; the finalists' items:", ""]
            for (tf_, sub_), v in near:
                fails = [k for k, vv in v["judge"].get("checks", {}).items() if not vv[0]]
                md.append(f"- {sub_} / {v['fin']['label']}: go/no-go {'PASS' if v['judge'].get('passed') else 'FAIL'} ({len(fails)} failed: {', '.join(fails)}); null tapes {('PASS' if v['null_tape'].get('passed') else 'FAIL') if v['null_tape'].get('evaluable') else 'not evaluable: ' + str(v['null_tape'].get('reason'))}.")
            md.append("")
        tfo["near_miss"] = [dict(sub=k[1], label=v["fin"]["label"], model=v["fin"]["model"], form=v["fin"]["form"], judge=v["judge"], null_tape=v["null_tape"]) for k, v in near]
        md += [f"### {tf} compute log", "", compute_table(tf), ""]
        # the merged OOF file the operating-point / sizing agent consumes: one row per (sub, model, IS unit) with the OOF score / p / tau / decision
        parts = [pd.read_parquet(os.path.join(G.RES, f"oof_{tf}_{s}.parquet")) for s in SUBS if os.path.exists(os.path.join(G.RES, f"oof_{tf}_{s}.parquet"))]
        if parts and not QUICK:
            P = pd.concat(parts, ignore_index=True); P["vocabulary"] = np.where(P["sub"] == "context", "inside the frozen vocabulary", "outside the frozen shortlist")
            P.to_parquet(os.path.join(G.RES, f"oof_{tf}.parquet"), index=False)
            tfo["oof_file"] = dict(file=f"results/oof_{tf}.parquet", rows=int(len(P)), models_by_sub={s: sorted(P.loc[P["sub"] == s, "model"].unique().tolist()) for s in SUBS})
            md += [f"OOF scores for the operating-point / sizing agent: `results/oof_{tf}.parquet` ({len(P)} rows = one per sub-family x model x IS unit; columns setup_i, tf, sub, model, fold, score, p, tau, keep, vocabulary; `p` is NaN for the policy learners, whose decision is `keep`).", ""]
        out["timeframes"][tf] = json.loads(json.dumps(tfo, default=lambda z: z.tolist() if isinstance(z, np.ndarray) else (z.item() if hasattr(z, "item") else str(z))))
    # result paragraph
    res_lines = []
    for tf in TFS:
        t = out["timeframes"].get(tf, {}); fam = t.get("family", {})
        fins = t.get("near_miss", [])
        s = f"**{tf}**: {fam.get('n_rows_all_labels', 0)} ledger rows in the family (PBO(diff) {fmt(fam.get('pbo_diff', {}).get('pbo'), 3)}, SPA p {fmt(fam.get('spa', {}).get('spa_p'), 3)}, effective trials {fmt(fam.get('effective_trials'))}); "
        s += "; ".join(f"{f['sub']} finalist {f['label']} CPCV p5 {fmt(((t.get('sub_families', {}).get(f['sub'], {}).get('finalist') or {}).get('cpcv') or {}).get('diff_p5'))}, go/no-go {'PASS' if f['judge'].get('passed') else 'FAIL (' + str(f['judge'].get('n_fail')) + ' items)'}" for f in fins) or "no finalist"
        s += f"; candidate: {'frozen ' + t['candidate']['file'] if t.get('candidate') else 'NONE'}."
        res_lines.append(s)
    result = ("**Null result on both timeframes: no candidate file is written.** " if out["null_result"] else "**A candidate is frozen** (see the timeframe sections). ") + " ".join(res_lines) + \
        " Read against the ceiling (section 3): the full-information bagging ranks winners at AUC 0.59 / 0.50 and its gate keeps everything, so no learned gate on this table can do more than shave its worst cells. What the family found (section 4 tables, ledger ids there) is one thing, on 1 min only: every probability / value learner of sub-family (I) distils to the same one- or two-rule list — skip the 11:00-11:59 SETUPs in `dir = down` (bag4, hgbr: frozen kept share 0.926, diff +326) plus skip the 15:00+ `dir = down` SETUPs (hgbc: kept 0.897, diff +289) — with a pooled OOF diff of +185 to +245 INR/trade, 9-11 of 12 blocks positive, every CPCV path positive (5th percentile +131 to +160) and a bootstrap 90% CI above zero; and that rule fails the pre-registered pass rule on exactly the items that separate a market rule from an artifact of the calendar and the book: the session-matched control percentile is 12-57 (the kept trades are no better than a random same-count pick inside their own sessions, so the pooled gain is the composition of sessions, not a selection within them), PBO 0.40, SPA p 0.94 and DSR p 1.0 over the 432-row family (the frozen-tree rows included), the kept book stays at -1,378 INR/trade at 8 pts slippage, and the segment-bootstrap null tapes reproduce a diff of +234 (median) / +562 (p95) for the same rule list on memoryless tapes (an hour x direction skip reads non-zero through the engine and the 15:25 cut alone; the real 289 sits at their 87.5th percentile), so the null-tape certificate fails. Sub-family (II) (H5 on the full table, OUTSIDE THE FROZEN SHORTLIST) does no better than (I) on either timeframe: its finalists' frozen forms skip nothing (kept share 1.0, the difference undefined), its HGB ceiling has an OOF gate diff of +49 (1 min) / +387 (5 min) with control percentiles 2 / 45. On 5 min the context finalist (pt2: skip the 11:00 hour) has a CPCV 5th percentile of -434 and fails 11 items; nothing on 5 min has a positive CPCV 5th percentile except the h5_full scorecard's distilled rule list (+54), whose frozen form skips nothing. Sequential RL was not used: section 6."
    md = [l.replace("@@RESULT@@", result) for l in md]
    md += ["## 6. Why sequential reinforcement learning is not used here", "",
           "The decision is one step per SETUP: take or skip at the SETUP bar. Foundation took every SETUP, so the reward of `take` (the L1 net) is observed for every context and the reward of `skip` is 0 by definition: the counterfactual is in the table, no arm is unobserved, no propensity model, no inverse-propensity weighting and no doubly-robust correction is needed (Dudik-Langford-Li's estimator collapses to the direct method), and the off-policy value of any gate is exact: sum over SETUPs of pi(x) x net(x). On L1 no two positions overlap by construction (average uniqueness 1.0 on the IS rows, logged in `run_<tf>_<sub>.log`), the next SETUP needs the CHoCH that exits the previous trade, and the 15:25 cut ends every position inside its session, so no state carries from one decision to the next: there is no return to bootstrap, no credit assignment across decisions and nothing a sequential learner (Q-learning, policy gradient, FQI) could exploit that supervised meta-labelling / a full-information contextual bandit does not already compute exactly. Sequential RL is justified only where today's action changes which future rewards remain reachable (the in-trade exit, studied in `exit_policy` as an Exo-MDP with FQI: no exit variant rescued the book; and the session-level stop, studied in `session_stop`: null). The 'generative' element the canon endorses at this sample size is the CPCV path distribution and the stationary block bootstrap of sessions (the harness), and the null tapes of `null_tapes_drift`.", "",
           "## 7. What would falsify these findings", "",
           "- A rule-list or scorecard form with a nested CPCV 5th percentile > 0, PBO <= 0.2 over the family, DSR p < 0.1 with n_trials = the family size, SPA p <= 0.10, a bootstrap 90% CI of the diff above 0, kept share >= 20%, kept n >= 300 / 80, diff > 0 with the top 1% winners removed, kept mean > 0 at 8 pts slippage, diff > 0 in >= 8 of 12 blocks, control percentile >= 95, AND a real-tape diff above the GMM-Markov and segment-bootstrap p95 of its own null tapes: the finalist-set tables show which items fail for every form.",
           "- A ceiling model with an OOF AUC materially above 0.59 (1 min) / 0.50 (5 min) on this table: the importance study's bagging and this study's HGB (b) are the two gradient / bagged ceilings and both sit there.",
           "- A tau grid on which the nested recall constraint (|net|-weighted winner recall >= 0.90) is met by a threshold above the floor in most folds: the 'tau constraint met' column shows how often the constraint bound at the floor.", "",
           "## 8. Caveats", ""]
    cav = ["The shortlist is empty on both timeframes; sub-family (II) is H5 on the whole as-of table and is OUTSIDE THE FROZEN SHORTLIST in every row; its multiplicity is counted in the same family as (I).",
           "Every HGB fit bins with unweighted quantiles (sklearn < 1.7 behaviour) because sklearn 1.9's weighted bin mapper costs ~25 s per fit; the study weights enter the loss unchanged.",
           "The fixed-tau, time-decay, structural-sensitivity and robustness-label rows are scored with controls off (they are trials, never candidates); their vectors are in the family for PBO / SPA.",
           "The frozen rule list distilled from the pooled OOF decisions and the scorecard / policy learner refit on all IS are in-sample selections (one trial each); the candidate rule judges the NESTED forms (their own OOF row and CPCV distribution), as both judges asked.",
           "The policy learners carry the DM-1 kept-share floor (>= 20% of the training rows) inside the search: without it the value-maximising tree skips every SETUP because the book's expectancy is negative in every hour x direction cell.",
           "A rule on an ext-features column (features_ext) is expressible on the real tape but cannot be replayed on the null tapes (their feature tables carry the 261 base columns): the null-tape item then reads 'not evaluable' and the form cannot be a candidate.",
           "`sl` and `n_events_asof` (drift.json time proxies) are excluded from sub-family (II); the interaction pairs that carry them are unusable and are listed.",
           "Two processes appended to the ledger concurrently (procA: 5minute context / 5minute h5_full / minute context; procB / procB2: minute h5_full; procC / procD: the 5minute scorecard and 5minute h5_full reruns with jobs=1); every line was parsed back by finalize (ids unique per config).",
           "The minute / context run (procA) was killed with its agent at 14:03 UTC during the hgbc robustness stage (L0 fold 4 of 12; no ledger row of that stage had been written: the stage scores after its 12 folds). It was restarted at 15:35 UTC (procA2.nohup, GF_JOBS=4) from its checkpoints: bag4 (all stages) and hgbc (oof12, cpcv, frozen) were not rerun; hgbc robust, hgbr, pt1-pt3, scorecard and diag ran in the restart. Every model is seeded (random_state 0 / per-estimator seeds), so the job count changes timings only.",
           "On 5minute the scorecard's C-search was run twice: the first runs walked the C grid linearly (`c_search = linear`; results kept as `scorecard_linear.pkl`, its rows are separate trials in the ledger because `c_search` is part of the config), the rerun bisects (`bisect`, `scorecard.pkl`, the procedure every other (tf, sub) uses). Both are in the family; the bisect one is the reported scorecard.",
           "The L3 label is dimensionless (a t-value); its rows' slippage column is not read; the L2 labels use the engine's same-bar conventions and are checked against the L1 stop exits.",
           "IS/OOS: no OOS row was read; the OOS window is the published lab window (BRIEF caveat)."]
    md += [f"- {c}" for c in cav] + ["", "## 9. Files", ""]
    files = sorted(f for f in os.listdir(HERE) if not f.startswith("__")) + [os.path.join("results", f) for f in sorted(os.listdir(G.RES)) if os.path.isfile(os.path.join(G.RES, f))] + \
        [os.path.join("results", tf, sub, f) for tf in TFS for sub in SUBS if os.path.isdir(os.path.join(G.RES, tf, sub)) for f in sorted(os.listdir(os.path.join(G.RES, tf, sub)))]
    md += [f"- `{f}`" for f in files]
    out["caveats"] = cav; out["files"] = files
    out["ledger_families"] = sorted({r["family"] for tf in TFS for r in ledger_rows(tf)})
    out["ceiling"] = {tf: dict(ledger_id=IMP["timeframes"][tf]["full_model"]["ledger_id"], oof_auc=IMP["timeframes"][tf]["full_model"]["oof_auc"], cpcv=IMP["timeframes"][tf]["full_model"]["cpcv"]) for tf in TFS}
    out["why_not_rl"] = "one-step decision per SETUP; the counterfactual (Foundation's own L1 trade) is observed for every SETUP; no position overlap on L1 (uniqueness 1.0); exact off-policy value; nothing for a sequential learner to bootstrap"
    suffix = "_dry" if QUICK else ""
    open(os.path.join(HERE, f"FINDINGS{suffix}.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    G.jdump(out, os.path.join(HERE, f"findings{suffix}.json"))
    log(f"FINDINGS.md and findings.json written; null_result={out['null_result']}; candidates={out['candidates']}")
    return out


if __name__ == "__main__":
    main()
