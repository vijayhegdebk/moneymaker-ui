"""Write FINDINGS.md and findings.json for the regime_gate study from results.json (no computation, no ledger row)."""
import os, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rg_lib as R                                                      # noqa: E402

res = json.load(open(os.path.join(HERE, "results.json")))
M = res["models"]; TF = res["tf"]
VOC = "outside the frozen shortlist"


def f(x, nd=2):
    if x is None: return "-"
    if isinstance(x, bool): return "yes" if x else "no"
    if isinstance(x, float): return f"{x:.{nd}f}"
    return str(x)


def table(cols, rows):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows: out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


L = []
cq = res["cluster_question"]; fam = res["family"]["all_rows"]; fam_sub = res["family"]["grid_nested_distilled_only"]
gng = res["go_no_go"]; nested = res["nested"]; cpcv = res["cpcv"]; grid = res["grid"]; fixed = res["fixed_rule"]
nt = res["null_tapes"]["per_model"]; dist = res["distillation"]; matched = res["matched_h2"]; per_row = res["per_row"]
n_cand = len(res["candidates"])

L.append(f"# regime_gate: the machine-found 'chop' state as a gate (DESIGN_PANEL deep-sequence-regime-states, both judges' fixes; 5 minutes only)\n")
L.append(f"**What this study is.** The regime-states study as the two judges left it: Judge 1 cut it to 'run the HMM only if study 3 (importance) shows the H2 counts are not already the regime cluster, and then on 5m only'; Judge 2 kept it with the state posteriors emitted as candidate features to the importance study and the tau grid run only if a state shows a kept-vs-skipped signal at matched skip fraction against `n_choch_since_bos`. This is that conditional run on **5 minutes, label L1, IS only**: the chop-state gate *skip when P(chop) >= tau* for hmm3 / hmm4 / gmm4 / jump4 and jump3, tau in {{0.5, 0.6, 0.7, 0.8, 0.9}}, the chop state identified per TRAINING fold as the state with the worst L1 expectancy, nested tau, the 11 CPCV paths, `harness.go_no_go` with the null-tape replay, the depth-3 distillation, and the comparison with the H2 hand rule at matched skip fraction. Every column this study reads is **{VOC}** (`features_shortlist/{TF}/shortlist.json`: `n_shortlisted` = {cq['n_shortlisted']} of {cq['n_clusters_total']} clusters; sha256 `{cq['shortlist_sha256'][:16]}...`), so every ledger row carries that note and nothing here can be frozen as a candidate without the user accepting that provenance. Scripts `rg_lib.py` (definitions, the frozen-model replay), `regime_gate.py` (the run; log `regime_gate.log`), `diagnostics.py` (label-free, section 7b), `write_findings.py`; runtime {res['runtime_s']} s, max RSS {res['max_rss_mb']} MB; ledger sha before `{res['ledger_sha_before']}`, after `{res['ledger_sha_after']}`. **Result: {'a candidate' if n_cand else 'null'}** (section 12).\n")

L.append("## 0. The gating question: do the H2 CHoCH counts and the state posteriors share a cluster, and did a state column make the shortlist?\n")
L.append(f"Read from `studies/importance/FINDINGS.md` (5minute, 'Do the H2 CHoCH counts and the state-model posteriors share a cluster?') and `features_shortlist/{TF}/shortlist.json` (`h2_vs_state_models`):\n")
rows = [[c, cl, "yes" if cl == cq["n_choch_since_bos_cluster"] else "no"] for c, cl in cq["state_clusters"].items()]
L.append(table(["state-model column", "cluster", f"same cluster as `n_choch_since_bos` ({cq['n_choch_since_bos_cluster']})"], rows))
L.append(f"\n- H2 count columns: {', '.join(f'`{c}` -> {cl}' for c, cl in cq['h2_clusters'].items())}.")
L.append(f"- In the `n_choch_since_bos` cluster: {', '.join('`' + c + '`' for c in cq['state_columns_in_n_choch_cluster'])} (one posterior per model: the state whose mean `choch_since_bos` input is high, i.e. the 'recent CHoCH, no BOS' state, plus the HMM run lengths and `jump4_state`).")
L.append(f"- Elsewhere: {', '.join(f'`{c}` ({cl})' for c, cl in cq['state_columns_elsewhere'].items())}: the quiet / volatile states sit in the volatility cluster 0 and the `n_bos_since_choch` cluster 5; **`jump3_state` and `jump3_run` form their own cluster 25**.")
L.append(f"- Any state column shortlisted: **{f(cq['any_state_column_shortlisted'])}** (the shortlist is empty on both timeframes: 0 of 39 clusters pass the pre-registered MDA rule).")
L.append(f"\n**Verdict on the question: {cq['verdict']}.** The counts and the states are therefore NOT one cluster, so the conditional run proceeds (5 minutes only). jump3 was added to the design's four models because on 5 minutes its columns are a cluster of their own and that cluster's SFI gate was the importance family's SPA-best row (ledger `{res['sfi_cluster25_row']['id'] if res.get('sfi_cluster25_row') else R.SFI25_ID}`: kept share {f(res['sfi_cluster25_row']['kept_share'], 3) if res.get('sfi_cluster25_row') else '0.868'}, diff {f(res['sfi_cluster25_row']['diff']) if res.get('sfi_cluster25_row') else '+827'} INR, control {f(res['sfi_cluster25_row']['control_pct'], 1) if res.get('sfi_cluster25_row') else '100'}th pct, permutation p {f(res['sfi_cluster25_row']['perm_p'], 3) if res.get('sfi_cluster25_row') else '0.078'}, {res['sfi_cluster25_row']['sign_blocks'] if res.get('sfi_cluster25_row') else 8}/12 blocks); the claim 'the jump3 state marks losers' is exactly what a nested-threshold gate tests, so it is in this family and counted like every other cell. The importance study's own reading stands for the posteriors that share cluster 3 with the count: where a state posterior sits in the count's cluster the state model adds nothing the count does not say; this study measures whether the *gate built on it* adds anything at matched skip fraction.\n")

L.append("## 1. Definitions (fixed before the numbers; `rg_lib.py` docstring verbatim)\n")
L.append("```\n" + R.__doc__.strip() + "\n```\n")
L.append(f"IS book: {res['n_is']} L1 units, mean {f(res['is_mean'])} INR per trade, win rate {f(res['is_win_rate'], 4)}. Posteriors from `features_ext/{TF}/ext_features.parquet` (forward-filtered only, truncation check PASS in `features_ext/README.md`); no new per-bar feature is built here.\n")

L.append("## 2. The states (frozen models, fit window 2021-10-01..2023-09-30; means in original units, from `features_ext/{TF}/ext_fit_report.json`)\n".replace("{TF}", TF))
for m in M:
    d = res["state_descriptions"][m]; names = d["feature_names"]
    rows = []
    for j, mu in enumerate(d["state_means"]):
        extra = [f(d["state_share_tape"][j], 4)]
        if d.get("expected_dwell_bars"): extra.append(f(d["expected_dwell_bars"][j], 1))
        rows.append([j] + [f(x, 4) for x in mu] + extra)
    cols = ["state"] + names + ["tape share"] + (["dwell (bars)"] if d.get("expected_dwell_bars") else [])
    L.append(f"### {m}" + (f" (lambda* = {d['lambda_star']})" if d.get("lambda_star") else "") + "\n")
    L.append(table(cols, rows) + "\n")

L.append("## 3. Expectancy by MAP state at the IS SETUP bars (descriptive decomposition of the raw book, no rule chosen on it; `state_tables_is.csv`)\n")
L.append(f"MAP = argmax posterior at the SETUP bar (the jump state itself). `run median` = the median `hmm{{K}}_map_run` / `jump{{K}}_run` at the SETUPs in the state (how many bars the filtered state had already lasted: the confirmation lag the design asks about). All tables **{VOC}**.\n")
for m in M:
    rows = [[r["state"], r["n"], f(r["share"], 4), f(r["posterior_mass_share"], 4), f(r["mean_net"]), f(r["win_rate"], 4), f(r.get("run_median_bars"), 1),
             "**chop (all IS)**" if r["state"] == fixed[m]["chop"] else ""] for r in res["state_tables_is"][m]]
    L.append(f"**{m}**\n\n" + table(["state", "n", "share", "posterior mass share", "mean L1 net", "win rate", "run median (bars)", ""], rows) + "\n")

L.append(f"## 4. Grid cells: chop and tau on all IS (trials; family `regime_gate/<model>`; `grid.csv`; all rows {VOC})\n")
L.append("For a jump model P(chop) is 0 or 1, so its five tau cells are one mask scored five times (the design's grid, kept as such; the effective-trial count discounts them). `fixed` marks the cell the tau rule picks on all IS (the fixed rule: what a config would ship and what was replayed on the null tapes).\n")
rows = [[g["config"]["model"], g["config"]["tau"], g["config"]["chop_state"], "**yes**" if g["is_fixed_rule"] else "", f"`{g['id']}`", g["kept_n"], f(g["kept_share"], 4), f(g["kept_mean"]), f(g["skipped_mean"]),
         f"**{f(g['diff'])}**", f(g["diff_top1_removed"]), f(g["control_pct"], 1), f(g["perm_p"], 4), f(g["loser_recall"], 3), f(g["loser_precision"], 3), f(g["winner_recall_weighted"], 3),
         f(g["top_decile_winners_skipped"], 3), f(g["kept_mean_slip8"]), g["sign_blocks"]] for g in grid]
L.append(table(["model", "tau", "chop", "fixed", "ledger id", "kept n", "kept share", "kept mean", "skipped mean", "diff", "diff top-1% removed", "control pct", "perm p", "loser recall", "loser precision", "wtd winner recall", "top-decile winners skipped", "kept mean slip 8", "sign blocks"], rows) + "\n")

L.append(f"## 5. Nested pick (12 purged folds; chop and tau chosen on the training rows; one OOF ledger row per model, family `regime_gate/<model>/nested`; `nested_folds.csv`; all rows {VOC})\n")
for m in M:
    r = nested[m]; fr = res["nested_folds"][m]
    L.append(f"### {m}: OOF row `{r['id']}`\n")
    rows = [[i, x["n_train"], x["n_test"], x["chop"], x["tau"], "yes" if x["feasible_any"] else "**no -> 0.9**", x["chop_train_n"], f(x["chop_train_mean"]), x["test_skipped"], f(x["test_kept_share"], 4)] for i, x in enumerate(fr)]
    L.append(table(["fold", "n train", "n test", "chop", "tau", "feasible tau", "chop train n", "chop train mean", "test skipped", "test kept share"], rows))
    L.append(f"\nOOF: kept {r['kept_n']} ({f(r['kept_share'], 4)}), kept mean {f(r['kept_mean'])}, skipped mean {f(r['skipped_mean'])}, **diff {f(r['diff'])}**, diff top-1% removed {f(r['diff_top1_removed'])}, control pct {f(r['control_pct'], 1)}, perm p {f(r['perm_p'], 4)}, loser recall {f(r['loser_recall'], 3)}, loser precision {f(r['loser_precision'], 3)}, |net|-weighted winner recall {f(r['winner_recall_weighted'], 3)}, top-decile winners skipped {f(r['top_decile_winners_skipped'], 3)}, kept mean at 8 pts slippage {f(r['kept_mean_slip8'])}, sign blocks {r['sign_blocks']}/12, kept PF {f(r['kept_pf'], 3)}. Per-block kept-vs-skipped diff (decomposition of this row): " + ", ".join(f"b{b['block']} {f(b['diff'])}" for b in r["block_diffs"]) + ".\n")

L.append(f"## 6. CPCV of the nested procedure (66 splits, 11 paths; family `regime_gate/<model>/nested/cpcv`; `cpcv_paths.csv`; all rows {VOC})\n")
rows = [[m, cpcv[m]["paths"], f(cpcv[m]["diff_median"]), f"**{f(cpcv[m]['diff_p5'])}**", f(cpcv[m]["diff_min"]), f(cpcv[m]["diff_share_positive"], 3), f(cpcv[m]["kept_share_median"], 4),
         f(cpcv[m].get("control_pct_median"), 1), f(cpcv[m].get("control_pct_p5"), 1), "; ".join(f"chop {c} tau {t}" for c, t in cpcv[m]["distinct_picks"])] for m in M]
L.append(table(["model", "paths", "diff median", "diff p5", "diff min", "share of paths diff > 0", "kept share median", "control pct median", "control pct p5", "distinct (chop, tau) picks over the 66 splits"], rows) + "\n")

L.append("## 7. The H2 hand rule at matched skip fraction (family `h2/choch`, `studies/h2_h3_h4/h2_5minute_L1_grid.csv`)\n")
L.append("Matched cell = the `n_choch_since_bos >= k` cell (scope all; k = 2, 3, 4) whose kept share is closest to the model's nested OOF kept share; the scope-today cell (`n_choch_since_bos_today >= k`) beside it. `beats` = the nested OOF diff is above the matched cell's diff (the design's bar: the state model must beat the hand rule at the same trade count or it is not worth its parameters).\n")
rows = []
for m in M:
    a = matched[m].get("all", {}); t = matched[m].get("today", {})
    rows.append([m, f(nested[m]["kept_share"], 4), f(nested[m]["diff"]), a.get("kc"), f"`{a.get('id')}`", f(a.get("kept_share"), 4), f(a.get("diff")), f(a.get("control_pct"), 1), f(a.get("perm_p"), 4), a.get("sign_blocks"),
                 f"**{f(a.get('nested_beats'))}**", t.get("kc"), f(t.get("kept_share"), 4), f(t.get("diff")), f(t.get("nested_beats"))])
L.append(table(["model", "nested kept share", "nested diff", "H2 k (all)", "H2 id", "H2 kept share", "H2 diff", "H2 control pct", "H2 perm p", "H2 sign blocks", "beats (all)", "H2 k (today)", "kept share", "diff", "beats (today)"], rows) + "\n")
s25 = res.get("sfi_cluster25_row")
if s25:
    L.append(f"The importance study's SFI gate on cluster 25 (`{s25['id']}`: a 300-tree bagging on `jump3_state` + `jump3_run` at its OOB tau) kept {s25['kept_n']} ({f(s25['kept_share'], 3)}), diff {f(s25['diff'])}, top-1%-removed {f(s25['diff_top1_removed'])}, control {f(s25['control_pct'], 1)}, perm p {f(s25['perm_p'], 4)}, {s25['sign_blocks']}/12 blocks, kept mean at 8 pts slippage {f(s25['kept_mean_slip8'])}. The jump3 chop-state gate here (fixed rule: skip state {fixed['jump3']['chop']}) kept {[g for g in grid if g['id'] == fixed['jump3']['cell_id']][0]['kept_n']} with diff {f([g for g in grid if g['id'] == fixed['jump3']['cell_id']][0]['diff'])}; nested OOF diff {f(nested['jump3']['diff'])}, CPCV p5 {f(cpcv['jump3']['diff_p5'])}: section 12 says what that means for the SPA-best row.\n")

if res.get("diagnostics"):
    L.append("## 7b. Where the chop states sit in the session (label-free diagnostic; `diagnostics.py`; explains the within-session statistics)\n")
    L.append("The session-matched control percentile and the SPA selection gain are within-session contrasts (kept mean minus the session's mean, per session). session_stop FINDINGS R.3 showed that on this book a rule that keeps a session's LATER units beats that control by construction (the last unit of a session is a long winner by construction of the SETUP sequence: a winner holds to the cut and no SETUP follows it). This table asks whether a chop state is such a rule. `chop share` = share of IS SETUPs whose MAP state is the fixed rule's chop state, by hour bin and by rank in the session (`today_n_setups_before`); the 'last unit' column uses post-SETUP information (the session's later SETUPs) and is a description of the control's mechanics, never a feature.\n")
    dg = res["diagnostics"]["per_model"]
    hours = ["<09:25", "09", "10", "11", "12", "13", "14", "15", ">=15:20"]
    rows = [[m, dg[m]["chop"], f(dg[m]["chop_share_all"], 3)] + [f(dg[m]["by_hour_bin"].get(h, {}).get("chop_share"), 3) for h in hours] +
            [f(dg[m]["by_rank_in_session"].get(str(r), {}).get("chop_share"), 3) for r in range(4)] + [f(dg[m]["chop_share_last_unit_of_session"], 3), f(dg[m]["chop_share_not_last"], 3), f(dg[m]["mean_session_bar_chop"], 1), f(dg[m]["mean_session_bar_other"], 1)] for m in M]
    L.append(table(["model", "chop", "share all"] + [f"share {h}" for h in hours] + [f"share rank {r}" for r in range(4)] + ["share last unit", "share not last", "mean session bar (chop)", "mean session bar (other)"], rows))
    j = dg["jump4"]
    L.append(f"\nReading: the jump4 chop state (state 1, the quiet state: `ev36` 1.8, `range36_atr` 4.5) is a morning / first-SETUP state: {f(j['by_hour_bin']['09']['chop_share'], 2)} of the 09 bin's SETUPs and {f(j['by_hour_bin']['10']['chop_share'], 2)} of the 10 bin's are in it against {f(min(j['by_hour_bin'][h]['chop_share'] for h in ('12', '13', '14')), 2)}-{f(max(j['by_hour_bin'][h]['chop_share'] for h in ('12', '13', '14')), 2)} in the 12, 13 and 14 bins; {f(j['by_rank_in_session']['0']['chop_share'], 2)} of a session's first SETUPs against {f(j['by_rank_in_session']['2']['chop_share'], 2)} of its third; mean session bar {f(j['mean_session_bar_chop'], 1)} vs {f(j['mean_session_bar_other'], 1)}. 'Skip the quiet state' is therefore largely 'skip the session's first, early SETUP and keep the later ones': the rule shape that inflates the session-matched control and the SPA gain by construction, which is why jump4 reads control 100 / SPA p {f(fam['spa'].get('spa_p'), 4)} while its between-session checks (blocks {nested['jump4']['sign_blocks']}/12, CPCV p5 {f(cpcv['jump4']['diff_p5'])}, bootstrap CI [{f(per_row['jump4/nested']['boot']['diff_ci'][0])}, {f(per_row['jump4/nested']['boot']['diff_ci'][1])}], session-tape same sign {f(nt['jump4']['summary_fixed']['session']['same_sign_share'], 2)}) fail. The hmm3 / gmm4 / jump3 chop states (the CHoCH-count states) are spread over the day and the ranks and their gates sit at control percentiles 0-13 with positive pooled diffs: the between-session composition effect the H2 study already reported for `n_choch_since_bos`.\n")

L.append("## 8. The family (every `regime_gate` ledger row) and the per-row statistics\n")
rows = [["all regime_gate rows", fam["n_rows"], f(fam["pbo_diff"]["pbo"], 4), f(fam["pbo_diff"].get("oos_best_below_zero"), 4), f(fam["pbo_kept_mean"]["pbo"], 4), f(fam["spa"].get("spa_p"), 4), f(fam["spa"].get("rc_p"), 4), f(fam["spa"].get("best_mean_gain")),
         str(fam.get("spa_best_row", {}).get("family")) + " " + json.dumps({k: v for k, v in fam.get("spa_best_row", {}).get("config", {}).items() if k in ("model", "tau", "path", "form")}), f(fam["spa"].get("spa_p_unstudentised"), 4), fam["spa"].get("excluded_from_studentised"), f(fam["effective_trials"], 2)],
        ["grid + nested + distilled (no CPCV paths)", fam_sub["n_rows"], f(fam_sub["pbo_diff"]["pbo"], 4), f(fam_sub["pbo_diff"].get("oos_best_below_zero"), 4), f(fam_sub["pbo_kept_mean"]["pbo"], 4), f(fam_sub["spa"].get("spa_p"), 4), f(fam_sub["spa"].get("rc_p"), 4), f(fam_sub["spa"].get("best_mean_gain")),
         str(fam_sub.get("spa_best_row", {}).get("family")) + " " + json.dumps({k: v for k, v in fam_sub.get("spa_best_row", {}).get("config", {}).items() if k in ("model", "tau", "path", "form")}), f(fam_sub["spa"].get("spa_p_unstudentised"), 4), fam_sub["spa"].get("excluded_from_studentised"), f(fam_sub["effective_trials"], 2)]]
L.append(table(["family", "rows", "PBO (diff)", "IS-best below 0 OOS", "PBO (kept mean)", "SPA p (studentised)", "RC p", "best mean gain / session", "SPA best row", "SPA p (unstudentised)", "excluded (min active)", "effective trials"], rows))
L.append(f"\nFamilies: {', '.join('`' + x + '`' for x in res['family']['families'])}. The go/no-go items below use the all-rows family (the more inclusive count: PBO {f(fam['pbo_diff']['pbo'], 4)}, SPA p {f(fam['spa'].get('spa_p'), 4)}); DSR uses n_trials = {fam['n_rows']} and the variance of the per-session Sharpe across the family's rows ({f(fam.get('sr_var_trials'), 5)}).\n")
rows = []
for m in M:
    for kind in ("nested", "fixed"):
        pr = per_row[f"{m}/{kind}"]; b = pr["boot"]; d = pr["dsr"]
        rows.append([m, kind, f"`{pr['id']}`", f"[{f(b['diff_ci'][0])}, {f(b['diff_ci'][1])}]", f(b["diff_p_le0"], 4), f"[{f(b['kept_mean_ci'][0])}, {f(b['kept_mean_ci'][1])}]", f(d.get("sr"), 4), f(d.get("sr0"), 4), f(d.get("p"), 4), d.get("T")])
L.append(table(["model", "row", "ledger id", "bootstrap 90% CI of diff", "P(diff <= 0)", "kept mean CI", "SR per session", "SR0 (expected max)", "DSR p", "active sessions"], rows) + "\n")

L.append("## 9. Null tapes: the fixed rule replayed on the certificate tapes (`tape_diffs.csv`; tape numbers never enter the ledger)\n")
ver = res["refit_verification"]
L.append("The frozen state models were refitted exactly as `studies/ext_features/build_ext.py` fitted them (same fit window, seeds and library calls) and verified against `ext_features.parquet` at every real SETUP before any tape was touched: " + "; ".join(f"{m} max |posterior diff| {v['max_abs_diff']:.1e}, MAP identical {f(v['identical_map'])}" for m, v in ver.items()) + ". Each tape's bars were then z-scored with the real fit window's statistics and run forward through the frozen models; the fixed rule (chop*, tau*) was applied at the tape's L1 units and scored with `harness.metrics` (controls off, as `tapes.null_tape_check` does). Pass rule (FINDINGS null_tapes_drift section 7): real diff > GMM-Markov p95 AND > segment p95 AND the session tapes carry the real sign in >= 75%.\n")
if res["null_tapes"].get("note"): L.append(f"**Not run: {res['null_tapes']['note']}.**\n")
else:
    rows = []
    for m in M:
        x = nt[m]; s = x["summary_fixed"]
        rows.append([m, f"chop {fixed[m]['chop']} tau {fixed[m]['tau']}", f(x["real_diff_fixed"]), x["n_tapes"]["gmm"], f(s["gmm"]["p50"]), f(s["gmm"]["p95"]), f(s["gmm"]["real_pct"], 1), f(s["segment"]["p50"]), f(s["segment"]["p95"]), f(s["segment"]["real_pct"], 1),
                     f(s["session"]["p50"]), f(s["session"]["p95"]), f(s["session"]["same_sign_share"], 3), f"**{f(x['passed_fixed'])}**", f(x["real_diff_nested"]), f(x["passed_nested"])])
    L.append(table(["model", "fixed rule", "real diff (fixed cell)", "tapes / gen", "gmm p50", "gmm p95", "real pct (gmm)", "segment p50", "segment p95", "real pct (segment)", "session p50", "session p95", "session same-sign share", "pass (fixed)", "nested OOF diff", "pass (nested diff vs the same tapes)"], rows) + "\n")

L.append(f"## 10. Distillation: a depth-3 tree on the base as-of features predicting the fixed rule's skip decision (`results.json` -> `distillation`)\n")
L.append(f"Features: `harness.design(T)` ({res['distillation_features']['n_columns']} columns) without the time proxies {res['distillation_features']['removed_time_proxies']}; the extended columns are not in the tree (the question is whether the state is expressible in the base vocabulary). Fidelity = out-of-fold accuracy under `harness.purged_splits` (tree refit per fold) against the fixed rule's decision; read against the majority-class share (a skip share of 5% gives a 95% baseline to a tree that never skips). Rule >= 0.85 out of fold = expressible; only then is the tree's own OOF gate a ledger row (family `regime_gate/<model>/distilled`).\n")
rows = []
for m in M:
    d = dist[m]; dr = res["distilled_rows"].get(m)
    rows.append([m, f"chop {fixed[m]['chop']} tau {fixed[m]['tau']}", f(d["skip_share"], 4), f(d["majority_baseline"], 4), f"**{f(d['fidelity_oof'], 4)}**", f(d["balanced_acc_oof"], 4), f(d["skip_recall_oof"], 3), f(d["skip_precision_oof"], 3), f(d["fidelity_in_sample"], 4),
                 "**yes**" if d["expressible"] else "no: not expressible compactly", ", ".join("`" + c + "`" for c in d["features_used"]), f(d.get("rule_list_agreement_with_tree"), 4),
                 (f"`{dr['id']}` kept {dr['kept_n']} diff {f(dr['diff'])} ctrl {f(dr['control_pct'], 1)}" if dr else "-")])
L.append(table(["model", "target (fixed rule)", "skip share", "majority baseline", "fidelity OOF", "balanced acc OOF", "skip recall OOF", "skip precision OOF", "fidelity in-sample", "expressible (>= 0.85 OOF)", "features the full-IS tree splits on", "rule-list agreement with the tree", "distilled OOF gate (ledger)"], rows))
L.append("\nThe full-IS trees' skip leaves as rule lists (the shippable form when expressible; NaN routing is not representable in the grammar, hence the agreement column):\n")
for m in M:
    d = dist[m]
    if d["rules"]:
        L.append(f"- **{m}**: " + "; ".join("IF " + " AND ".join(f"`{c}` {op} {v}" for c, op, v in r["if"]) + f" -> skip (leaf n {r['leaf_n']})" for r in d["rules"]))
    else: L.append(f"- **{m}**: the tree has no skip leaf.")
L.append("")

L.append("## 11. `harness.go_no_go` per model (nested OOF row = the decision; the fixed rule's own row beside it)\n")
for m in M:
    g = gng[m]
    rows = [[k, "ok" if v[0] else "**FAIL**", f(v[1], 4) if not isinstance(v[1], (list, dict)) else json.dumps(v[1])[:120], "ok" if g["fixed"]["checks"][k][0] else "**FAIL**", f(g["fixed"]["checks"][k][1], 4) if not isinstance(g["fixed"]["checks"][k][1], (list, dict)) else json.dumps(g["fixed"]["checks"][k][1])[:120]] for k, v in g["nested"]["checks"].items()]
    L.append(f"**{m}** — nested passed **{f(g['nested']['passed'])}**, fixed passed {f(g['fixed']['passed'])}, beats the matched H2 rule (scope all) {f(g['beats_matched_h2_all'])}, candidate **{f(g['candidate'])}**\n")
    L.append(table(["check", "nested", "value", "fixed", "value"], rows) + "\n")

L.append("## 12. Verdict\n")
if n_cand:
    L.append(f"{n_cand} model(s) pass `harness.go_no_go` and beat the matched H2 rule: {', '.join(c['model'] for c in res['candidates'])}. Their candidate JSONs (`candidate_<model>.json`) carry the provenance `vocabulary: {R.VOCAB_NOTE}` and `user_decision_required: true`: the user accepts or rejects the vocabulary; where the tree distillation is not expressible the only config form is an fz key of 40-60 numbers plus a forward filter in fz code, which is offered, not assumed.\n")
else:
    best = max(M, key=lambda m: (nested[m]["diff"] if nested[m]["diff"] is not None else -1e9))
    L.append(f"**Null result: no regime gate is a candidate.** No model passes `harness.go_no_go` on its nested OOF row (failing items per model: " + "; ".join(f"{m}: {', '.join(gng[m]['nested']['failing'])}" for m in M) + "). "
             f"Beats the matched H2 hand rule at matched skip fraction: " + ", ".join(f"{m} {f(gng[m]['beats_matched_h2_all'])}" for m in M) + f". The best nested OOF difference is {best}'s {f(nested[best]['diff'])} INR per trade (kept share {f(nested[best]['kept_share'], 4)}, control pct {f(nested[best]['control_pct'], 1)}, perm p {f(nested[best]['perm_p'], 4)}, {nested[best]['sign_blocks']}/12 blocks, CPCV p5 {f(cpcv[best]['diff_p5'])}); the family's PBO is {f(fam['pbo_diff']['pbo'], 4)} over {fam['n_rows']} rows ({f(fam['effective_trials'], 2)} effective trials) and its SPA p {f(fam['spa'].get('spa_p'), 4)} is carried by the jump4 cell (the SPA-best row, `{fam.get('spa_best_row', {}).get('id')}`, mean selection gain {f(fam['spa'].get('best_mean_gain'))} INR per session, t {f(fam['spa'].get('best_t'), 2)} over {fam['spa'].get('best_active_sessions')} active sessions): the SPA gain is the same within-session contrast as the control percentile, and section 7b shows that contrast is inflated for this cell by construction, so the one item the family passes is the one item that cannot carry it. No `candidates/` JSON is written; no fz key is proposed (the 40-60-number HMM key would be a user decision in any case, and nothing here earns the offer).\n")
    j = nested["jump4"]; jn = nt["jump4"]; jb = per_row["jump4/nested"]["boot"]
    unstable_costs = ", ".join(f"{m} {f(nested[m]['diff'])}" for m in ("hmm3", "hmm4", "gmm4", "jump3"))
    L.append(f"**The one positive out-of-fold gate, jump4** (skip when the online jump4 state is state 1, the quiet state; the chop was state 1 in all 12 training folds and the tau grid is degenerate for a hard state, so the nested OOF row, the fixed rule and every grid cell are one mask, `{j['id']}` / `{fixed['jump4']['cell_id']}`): kept {j['kept_n']} ({f(j['kept_share'], 4)}), kept mean {f(j['kept_mean'])} vs skipped {f(j['skipped_mean'])}, diff **{f(j['diff'])}**, top-1%-removed {f(j['diff_top1_removed'])}, control pct {f(j['control_pct'], 1)}, permutation p {f(j['perm_p'], 4)}, {j['sign_blocks']}/12 blocks, kept mean at 8 pts slippage {f(j['kept_mean_slip8'])}, bootstrap 90% CI of the diff [{f(jb['diff_ci'][0])}, {f(jb['diff_ci'][1])}] (P(diff <= 0) {f(jb['diff_p_le0'], 3)}), CPCV median {f(cpcv['jump4']['diff_median'])} / p5 {f(cpcv['jump4']['diff_p5'])} ({f(cpcv['jump4']['diff_share_positive'], 2)} of paths positive), DSR p {f(per_row['jump4/nested']['dsr']['p'], 3)}; it beats the matched H2 cell (k = 2, diff {f(matched['jump4']['all']['diff'])}) on the pooled diff. On the certificate tapes its real diff {f(jn['real_diff_fixed'])} is above the GMM-Markov p95 {f(jn['summary_fixed']['gmm']['p95'])} and the segment p95 {f(jn['summary_fixed']['segment']['p95'])} (the memory-free tapes give the same rule a median of {f(jn['summary_fixed']['gmm']['p50'])} / {f(jn['summary_fixed']['segment']['p50'])} and reach +{f(jn['summary_fixed']['segment']['p95'])} at the 95th percentile by engine mechanics alone), but the session-bootstrap tapes carry its sign in only {f(jn['summary_fixed']['session']['same_sign_share'], 2)} of tapes (median {f(jn['summary_fixed']['session']['p50'])}): on tapes that keep every real session intact and only reorder the days, the gate reads negative more often than positive. Section 7b shows why the two within-session statistics it passes (control, SPA) are inflated: state 1 is the session's first, early SETUP. It fails {len(gng['jump4']['nested']['failing'])} go/no-go items ({', '.join(gng['jump4']['nested']['failing'])}) and is not a candidate; its distillation is not expressible (fidelity {f(dist['jump4']['fidelity_oof'], 3)} against a majority baseline {f(dist['jump4']['majority_baseline'], 3)}), so even a passing version would have been a 40-60-number fz key, a user decision.\n")
    L.append(f"**Judge 1's prediction, measured.** The chop states the training folds pick for hmm3 (state 0), gmm4 (state 1) and jump3 (state 1) are the CHoCH-count states (high mean `choch_since_bos` input: section 2), and their depth-3 distillations on the base features reproduce them at {f(dist['hmm3']['fidelity_oof'], 3)} / {f(dist['gmm4']['fidelity_oof'], 3)} / {f(dist['jump3']['fidelity_oof'], 3)} out-of-fold fidelity from `n_choch_since_bos_today`, `bars_since_choch`, `bar_range_atr`, `alt_dir6` / `n_flip_since_bos` and `bars_since_bos`: the HMM / GMM / jump 'chop' at a SETUP bar is the CHoCH count with a bar-size condition, which the importance study's clustering had already said, and the gates built on it sit at control percentiles 0-13 like the H2 hand rule. The chop pick itself is unstable across training folds for four of the five models (section 5: hmm3 0/1, hmm4 1/2/3, gmm4 1/2, jump3 0/1/2), which is the label-switching-plus-selection trap named in the design; the out-of-fold rows are what that instability costs ({unstable_costs}). hmm4's 'expressible' flag is the design's letter only: its skip share is {f(dist['hmm4']['skip_share'], 3)}, the majority baseline {f(dist['hmm4']['majority_baseline'], 3)} exceeds the fidelity {f(dist['hmm4']['fidelity_oof'], 3)}, balanced accuracy {f(dist['hmm4']['balanced_acc_oof'], 3)}: the tree does not express the state, it never skips.\n")
    if s25:
        L.append(f"On the jump3 claim specifically (the importance family's SPA-best row `{s25['id']}`, diff +{f(s25['diff'])} at kept share {f(s25['kept_share'], 3)}): the chop-state gate on the same columns, chosen inside training folds, gives a nested OOF diff of {f(nested['jump3']['diff'])} (CPCV median {f(cpcv['jump3']['diff_median'])}, p5 {f(cpcv['jump3']['diff_p5'])}, share of paths positive {f(cpcv['jump3']['diff_share_positive'], 3)}), control pct {f(nested['jump3']['control_pct'], 1)}, {nested['jump3']['sign_blocks']}/12 blocks; the fixed rule's real-tape diff {f(nt['jump3']['real_diff_fixed'])} sits at the {f(nt['jump3']['summary_fixed']['gmm']['real_pct'], 1)}th / {f(nt['jump3']['summary_fixed']['segment']['real_pct'], 1)}th percentile of the GMM-Markov / segment tapes (p95 {f(nt['jump3']['summary_fixed']['gmm']['p95'])} / {f(nt['jump3']['summary_fixed']['segment']['p95'])}) with the session tapes carrying its sign in {f(nt['jump3']['summary_fixed']['session']['same_sign_share'], 3)} of tapes. The SFI row's +827 was the bagging's OOB-tau gate on `jump3_state` + `jump3_run` (a learned function of both columns, kept share 0.868); the state-only skip at the nested threshold does not reproduce it as a gate that passes the program's rule.\n")

L.append("## 13. What would falsify these findings\n")
L.append(f"- A model whose nested OOF row shows diff > 0 with the top 1% winners removed, control pct >= 95, >= 8/12 blocks, CPCV 5th percentile > 0, a bootstrap 90% CI of the diff above 0, SPA p <= 0.10 over the family, and a real-tape diff above the GMM-Markov and segment tapes' 95th percentiles with the session tapes carrying its sign in >= 75% of them, AND a diff above the matched H2 cell's: none does here (section 11).")
L.append("- A chop state that is the same state in every training fold AND whose gate's kept-vs-skipped difference is positive in >= 8 of the 12 blocks (the fold trace in section 5 shows where the pick moved; the block diffs beside each OOF row show where the sign held).")
L.append("- The refit not reproducing `ext_features.parquet` (section 9: it does to 1e-8), or a tape replay that reads a label (it reads bars and events only).")
L.append("- A different chop definition (posterior-weighted expectancy instead of MAP grouping, or a minimum-support guard) or a different tau criterion would be a new registration with its own sha and the multiplicity carried forward, never an edit of this one.\n")

L.append("## 14. Caveats\n")
L.append(f"- Every column read is {VOC}: the frozen shortlist is empty on both timeframes, so this study ran under the EMPTY-SHORTLIST RULE of the phase-3 launch (PROGRESS.md); nothing here could be frozen as a candidate without the user accepting that provenance.")
L.append("- 5 minutes only (Judge 1); 826 IS units in 408 active sessions, 229 winners: the standard error of a kept-vs-skipped difference at a 60/40 split is several hundred INR per trade; a null here is 'not shown', not 'shown absent'.")
L.append("- The state models were fitted on the first IS half (2021-10..2023-09) and frozen; for SETUPs inside that window the posteriors are label-free in-sample (features_ext/README.md states it). The chop state and tau are the only supervised choices and they are made inside the training folds.")
L.append("- For the jump models the tau grid is degenerate (a hard state): their five grid cells are one mask scored five times; the effective-trial count of the family discounts them and the tau recorded for their fixed rule (0.9, the tie rule) is any tau in the grid.")
L.append("- The chop state is the worst-expectancy MAP state on the training rows with no minimum-support guard (the design's rule as written): a small state with a bad training mean can be picked, which the fold trace shows; the CPCV distribution is the honest reading of that instability.")
L.append("- The null-tape replay applies the fixed rule (chop*, tau* chosen on all IS) to tapes filtered through models fitted on the real fit window; a tape's states mean something else than the real tape's, which is the point of a memory-free null, and the same fixed rule is applied on both sides.")
L.append("- The distilled tree's fidelity is read against the majority baseline; a fidelity above 0.85 that is below the baseline is a tree that never skips, not an expressible state.")
L.append("- The session-matched control percentile of a gate that reads the CHoCH state is partly engine mechanics (null_tapes_drift section 4c): the tape p95 of the diff, not the control percentile, is the bar; both are reported.")
L.append("- The 55 CPCV path rows are written by `harness.score_paths`, which passes no `note`; their `config.vocabulary` field carries the 'outside the frozen shortlist' label (verified on all 89 rows), the 34 grid / nested / distilled rows carry it in both `note` and `config`.")
L.append(f"- Other phase-3 studies append to the ledger concurrently: the ledger sha `{res['ledger_sha_after']}` is the file at the moment this run finished; a later sha reflects their rows, not a change to these 89 (append-only; ids in `results.json`).")
L.append("- Section 7b's 'last unit of the session' column uses the session's later SETUPs (post-SETUP information) to describe the control's mechanics; it is a diagnostic, not a feature, and no rule reads it.")
L.append("- Smoke test: `regime_gate.py --smoke` ran once on a redirected ledger (scratchpad) with the L1 nets shuffled within IS (seed 0) and controls off, so no real kept-vs-skipped number exists off the program ledger; its outputs are not in this folder.\n")

L.append("## 15. Files\n")
files = ["studies/regime_gate/rg_lib.py", "studies/regime_gate/regime_gate.py", "studies/regime_gate/diagnostics.py", "studies/regime_gate/write_findings.py", "studies/regime_gate/regime_gate.log", "studies/regime_gate/results.json",
         "studies/regime_gate/grid.csv", "studies/regime_gate/nested_folds.csv", "studies/regime_gate/cpcv_paths.csv", "studies/regime_gate/state_tables_is.csv", "studies/regime_gate/tape_diffs.csv",
         "studies/regime_gate/FINDINGS.md", "studies/regime_gate/findings.json"] + [f"studies/regime_gate/candidate_{c['model']}.json" for c in res["candidates"]]
L.extend(f"- `{x}`" for x in files)
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

fj = dict(study="regime_gate", design="DESIGN_PANEL deep-sequence-regime-states (both judges' fixes; 5 minutes only)", label=res["label"],
          cluster_question=cq, vocabulary=R.VOCAB_NOTE,
          timeframes={TF: dict(n_is=res["n_is"], is_mean=res["is_mean"], models=M, taus=res["taus"],
                              grid=[dict(id=g["id"], model=g["config"]["model"], tau=g["config"]["tau"], chop=g["config"]["chop_state"], fixed=g["is_fixed_rule"], kept_n=g["kept_n"], kept_share=g["kept_share"], diff=g["diff"],
                                         diff_top1_removed=g["diff_top1_removed"], control_pct=g["control_pct"], perm_p=g["perm_p"], sign_blocks=g["sign_blocks"], kept_mean_slip8=g["kept_mean_slip8"]) for g in grid],
                              nested={m: dict(id=nested[m]["id"], fold_chop=nested[m]["config"]["fold_chop"], fold_tau=nested[m]["config"]["fold_tau"], **{k: nested[m][k] for k in ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks")}) for m in M},
                              cpcv={m: {k: cpcv[m][k] for k in ("paths", "diff_median", "diff_p5", "diff_min", "diff_share_positive", "kept_share_median", "control_pct_median", "control_pct_p5", "distinct_picks") if k in cpcv[m]} for m in M},
                              matched_h2=matched, sfi_cluster25_row=s25, family=dict(all_rows={k: v for k, v in fam.items()}, no_cpcv={k: v for k, v in fam_sub.items()}),
                              per_row=per_row, null_tapes={m: {k: v for k, v in nt[m].items() if not k.startswith("summary") or True} for m in M}, refit_verification=ver,
                              distillation={m: {k: v for k, v in dist[m].items()} for m in M}, distilled_rows={m: dict(id=r["id"], kept_n=r["kept_n"], diff=r["diff"], control_pct=r["control_pct"]) for m, r in res["distilled_rows"].items()},
                              go_no_go=gng)},
          candidates=res["candidates"], null_result=res["null_result"], ledger_families=res["family"]["families"],
          ledger=dict(sha_before=res["ledger_sha_before"], sha_after=res["ledger_sha_after"], rows_in_family=fam["n_rows"]),
          caveats=[x[2:] for x in L[L.index("## 14. Caveats\n") + 1: L.index("## 15. Files\n")] if x.startswith("- ")],
          files=files, runtime_s=res["runtime_s"], max_rss_mb=res["max_rss_mb"])
for m in M:
    if "summary_fixed" in fj["timeframes"][TF]["null_tapes"][m]:
        fj["timeframes"][TF]["null_tapes"][m]["summary_fixed"] = {k: v for k, v in nt[m]["summary_fixed"].items() if k != "per_tape"}
        fj["timeframes"][TF]["null_tapes"][m]["summary_nested"] = {k: v for k, v in nt[m]["summary_nested"].items() if k != "per_tape"}
json.dump(fj, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=str)
print("wrote FINDINGS.md and findings.json")
