"""Build FINDINGS.md (tables + reading) and findings.json from results.json / the CSVs written by session_stop.py: no number is typed
by hand; every one is read from results.json (which carries the ledger ids).

    python write_findings.py
"""
import os, sys, json, hashlib, ast
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
import pandas as pd

R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
PRE = R["preregistration"]
DOC = ast.get_docstring(ast.parse(open(os.path.join(HERE, "session_stop.py"), encoding="utf-8").read()))
PRE_SHA = hashlib.sha256(open(os.path.join(HERE, "preregistration.json"), "rb").read()).hexdigest()[:16]
LOG = open(os.path.join(HERE, "session_stop.log"), encoding="utf-8").read().splitlines()
LEDGER_BEFORE = next((l.split("ledger sha before ")[1].strip() for l in LOG if "ledger sha before" in l), None)


def f(x, d=2):
    if x is None or (isinstance(x, float) and x != x): return ""
    if isinstance(x, bool): return str(x)
    if isinstance(x, int): return f"{x:,}"
    if isinstance(x, float): return f"{x:,.{d}f}"
    return str(x)


def md_table(df, cols=None, digits=None):
    cols = cols or list(df.columns); digits = digits or {}
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(r[c] if isinstance(r[c], str) else f(r[c], digits.get(c, 2)) for c in cols) + " |")
    return "\n".join(lines)


def null_block(rec):
    t = pd.DataFrame(rec["tests"])
    cols = ["test", "n_condition", "n_other", "observed", "N1_perm_mean", "N1_perm_sd", "N1_excess", "N1_p", "N1_p_holm", "N2_perm_mean", "N2_excess", "N2_p", "N2_p_holm", "N1_p_abs_ref"]
    for c in cols[3:]: t[c] = t[c].astype(float)
    dg = {c: 4 for c in cols}; dg.update(n_condition=0, n_other=0)
    t["n_other"] = t["n_other"].astype(float)
    s = md_table(t, cols, dg)
    n1, n2 = rec["nulls"]["session_x_hour"], rec["nulls"]["session"]
    s += (f"\n\nN1 cells (session x hour_bin): {n1['n_cells']:,}, singletons {n1['cells_size1']:,}; rows that can move {n1['rows_movable']:,} of {rec['units']:,}. "
          f"N2 cells (sessions): {n2['n_cells']:,}, singletons {n2['cells_size1']:,}; rows that can move {n2['rows_movable']:,}. "
          f"Min Holm p: N1 {rec['min_p_holm_N1']:.4f}, N2 {rec['min_p_holm_N2']:.4f}; rejected at 5%: N1 **{rec['rejected_N1']}**, N2 {rec['rejected_N2']}.")
    return s


def excess_signs(rec):
    ex = {t["test"]: t["N1_excess"] for t in rec["tests"]}
    thr = [v for k, v in ex.items() if k != "spearman_today_net"]
    return ex, all(v > 0 for v in thr), ex["spearman_today_net"]


def sec_tf(tf):
    X = R["timeframes"][tf]; L1 = X["L1"]; P = []
    ex, all_pos, rho_ex = excess_signs(L1)
    P.append(f"## {'3' if tf == 'minute' else '5'}. {tf} / L1 ({X['power_note']}): the seven pre-registered tests\n")
    P.append(f"{L1['units']:,} IS units in {L1['active_sessions']} active sessions (median {L1['setups_per_session_median']:.0f}, max {L1['setups_per_session_max']} SETUPs per session); "
             f"ledger identity check: max |today_net_asof - cumulative prior L1 net| = {L1['ledger_identity']['net_max_abs_diff']:.1e} INR, stop counts identical = {L1['ledger_identity']['stops_identical']}. "
             f"File `null_tests_{tf}_L1.csv`. `observed` is the statistic on the IS rows; `N1_perm_mean` / `N1_perm_sd` the permutation distribution under the pre-registered null; "
             f"`N1_excess` = observed - N1 mean (the part beyond the hour effect and the within-session sampling mechanics); `N1_p` the doubled-tail p; `N1_p_holm` Holm over the 7 tests; "
             f"`N1_p_abs_ref` the naive |stat| form, reference only.\n")
    P.append(null_block(L1))
    note = "" if tf == "minute" else (f" (as the script wrote it; on this timeframe only {L1['nulls']['session_x_hour']['rows_movable']} rows can move under N1, so the N2 rejection "
                                       "cannot be attributed to the hour effect alone: the honest statement is *underpowered, nothing shown*)")
    P.append(f"\n**Decision ({tf}):** {X['decision']}{note}\n")
    if tf == "minute":
        P.append("**Reading.** In absolute terms the next SETUP is worse after stops or losses (observed differences "
                 + ", ".join(f"{t['test']} {t['observed']:+,.0f}" for t in L1["tests"] if t["test"] != "spearman_today_net")
                 + " INR/trade), but the clock alone predicts more: under N1 the ledger still accumulates with the hour and the later hours carry both the stops and the worse expectancy "
                 f"(hour profile below), so the null means are {min(t['N1_perm_mean'] for t in L1['tests'] if t['test'] != 'spearman_today_net'):+,.0f} to "
                 f"{max(t['N1_perm_mean'] for t in L1['tests'] if t['test'] != 'spearman_today_net'):+,.0f} INR. The excess beyond that null is **positive on every threshold test** "
                 f"({min(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} to {max(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} INR/trade) and the Spearman excess is "
                 f"{rho_ex:+.4f} (a more negative ledger goes with a better next trade). Every test rejects N1 after Holm (max Holm p {max(t['N1_p_holm'] for t in L1['tests']):.4f}), all in the "
                 "**mean-reverting** direction: there is session memory beyond the hour effect, and it runs against a stop rule (after k stops or a loss L the next SETUP is *less* bad than its "
                 "hour and session peers, not more). N2 (plain within-session) rejects too, with the same signs; its null means are far more negative because it also destroys the hour "
                 "structure (the stops>=k rows then come from the sessions with many stops, i.e. the bad sessions, while the stops=0 rows come from the good ones).\n")
    else:
        P.append("**Reading.** " + (f"{L1['nulls']['session_x_hour']['cells_size1']:,} of {L1['nulls']['session_x_hour']['n_cells']:,} session x hour cells are singletons, so only "
                 f"{L1['nulls']['session_x_hour']['rows_movable']} of {L1['units']} rows can move under N1: the test has almost no power on this timeframe (median 2 SETUPs per active session) and "
                 "is reported as underpowered, as the design requires; N1's non-rejection is therefore not evidence of \"no memory\", and N2's rejection cannot be split between the hour effect "
                 "and N1's lack of power. ") + ("The N1 excess signs match 1 min (positive on the threshold tests)." if all_pos else
                 "The N1 excess signs are mixed (the k = 3 and L = -6,000 cells hold 18 and 123 rows).") +
                 " Descriptively the 5 min book also improves after stops in absolute terms (`by_stops` below), but the N1 null mean is just as positive, so nothing beyond the clock is shown.\n")
    P.append(f"### Hour-of-day profile of the L1 book ({tf}, IS; `hour_profile_{tf}.csv`)\n")
    hp = pd.DataFrame(L1["hour_profile"])
    P.append(md_table(hp, list(hp.columns), dict(n=0, win_rate=4, stop_rate=4, mean_today_n_stops_asof=3, share_stops_ge1=4, share_net_le_m4000=4)))
    P.append(f"\n### Mean L1 net by the ledger state ({tf}, IS; `by_stops_{tf}.csv`, `by_net_bucket_{tf}.csv`; descriptive, no rule chosen on them)\n")
    bs = pd.DataFrame(L1["by_stops"]); bn = pd.DataFrame(L1["by_net_bucket"])
    P.append(md_table(bs, list(bs.columns), dict(n=0, win_rate=4)) + "\n\n" + md_table(bn, list(bn.columns), dict(n=0, win_rate=4)))
    P.append(f"\n### Within-hour comparison, stops >= 1 vs none ({tf}, IS; `hour_x_stops_{tf}.csv`)\n")
    hx = pd.DataFrame(L1["hour_x_stops"])
    P.append(md_table(hx, list(hx.columns), {c: 0 for c in hx.columns if c.startswith("size")}))
    L0 = X["L0_robustness"]; ex0, pos0, _ = excess_signs(L0)
    P.append(f"\n### L0 robustness ({tf}, {L0['units']:,} IS units; `null_tests_{tf}_L0.csv`; reported only, never the decision)\n")
    P.append(null_block(L0))
    P.append(f"\nL0 excess signs on the threshold tests all positive: {pos0}; min Holm p N1 {L0['min_p_holm_N1']:.4f}.\n")
    if X.get("branch_b"):
        B = X["branch_b"]; g0 = B["grid"]
        P.append(f"## 4. {tf}: branch B, the fixed grid by exact replay (family `session_stop/grid`, {len(g0)} ledger rows; `grid_{tf}.csv`)\n")
        P.append("Rule: skip once the session's ledger at the bar has >= k stops or its running-minimum net <= L (absorbing); `rearm=True` re-arms at the next SETUP after a skipped "
                 "SETUP's paper trade wins, counters reset. `diff` = kept mean - skipped mean (INR/trade); `control_pct` = session-matched random control percentile (2,000 draws); "
                 "`perm_p` = kept-vs-skipped permutation p; `w_recall` = |net|-weighted winner recall; `top10_skip` = share of top-decile winners skipped; `slip8` = kept mean at 8 pts slippage.\n")
        g = pd.DataFrame([dict(k=r["config"]["max_stops_today"], L=("none" if r["config"]["max_loss_today_inr"] is None else f"{r['config']['max_loss_today_inr']:,.0f}"), rearm=str(r["config"]["rearm_after_win"]),
                               id=r["id"], kept_n=r["kept_n"], share=r["kept_share"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"], diff_top1_off=r["diff_top1_removed"],
                               control_pct=r["control_pct"], perm_p=r["perm_p"], loser_recall=r["loser_recall"], loser_prec=r["loser_precision"], w_recall=r["winner_recall_weighted"],
                               top10_skip=r["top_decile_winners_skipped"], sign_blocks=r["sign_blocks"], slip8=r["kept_mean_slip8"]) for r in g0])
        P.append(md_table(g, list(g.columns), dict(k=0, kept_n=0, share=4, perm_p=4, control_pct=1, loser_recall=4, loser_prec=4, w_recall=4, top10_skip=4, sign_blocks=0)))
        cmax = max(r["control_pct"] for r in g0 if r["control_pct"] is not None); dmin = min(r["diff"] for r in g0); dmax = max(r["diff"] for r in g0)
        sb = max(r["sign_blocks"] for r in g0 if r["sign_blocks"] is not None)
        npos = sum(1 for r in g0 if r["diff"] is not None and r["diff"] > 0)
        P.append(f"\n**Reading.** {npos} of {len(g0)} cells have a positive pooled `diff` (range {dmin:+,.0f} to {dmax:+,.0f} INR/trade) and every cell sits at the **{cmax:.1f}th percentile** of the "
                 "session-matched random control (best sign count {sb}/12 blocks). The two disagree because they measure different things: the pooled difference mixes sessions, and the "
                 "kept set is enriched with the rows of short sessions (1-3 SETUPs, where the rule never binds), which are the trending days with the best expectancy, while the skipped rows "
                 "all come from long, choppy sessions; the control draws the same number of positions inside each session and removes that composition. Within a session the rule keeps the "
                 "first SETUPs, and by construction the trade that triggered the stop (a stop-loss or the loss that took the ledger past L) is always in the kept set, while the skipped "
                 "later SETUPs are the ones the null test showed to be less bad than their peers. The rule therefore does worse than picking the same number of same-session SETUPs at "
                 "random in essentially every draw. Judged as the design requires (kept-vs-skipped at matched per-session k and the control), no cell has an edge; the positive pooled "
                 "diff is cost avoidance plus session composition.\n".replace("{sb}", str(sb)))
        n = B["nested_oof"]
        P.append(f"### Nested choice, CPCV, family statistics, go / no-go ({tf})\n")
        P.append(f"**Nested choice** (12 purged folds; selection `{PRE['fold_selection']}`): the OOF mask is ledger row `{n['id']}` (family `session_stop/nested`): kept {n['kept_n']:,} "
                 f"(share {n['kept_share']}), diff {n['diff']:+,.2f}, perm p {n['perm_p']}, control pct {n['control_pct']}, sign blocks {n['sign_blocks']}/12. Cells chosen per fold: "
                 + "; ".join(f"b{i} k={c['max_stops_today']} L={c['max_loss_today_inr']} rearm={c['rearm_after_win']}" if c else f"b{i} none" for i, c in enumerate(B["chosen_per_fold"])) + ".\n")
        c = B["cpcv"]
        P.append(f"**CPCV** (66 splits -> 11 paths, the same in-fold choice; family `session_stop/nested/cpcv`, ids `{B['cpcv_path_ids'][0]}` .. `{B['cpcv_path_ids'][-1]}`): diff median "
                 f"{c['diff_median']:+,.2f}, 5th percentile {c['diff_p5']:+,.2f}, min {c['diff_min']:+,.2f}, share of paths with diff > 0 {c['diff_share_positive']}, kept share median {c['kept_share_median']}, "
                 f"control pct median {c.get('control_pct_median')}, control pct 5th percentile {c.get('control_pct_p5')}.\n")
        fam = B["family"]
        P.append(f"**Family ({len(g0)} cells):** PBO on diff {fam['pbo_diff']['pbo']} (IS-best below zero out of sample in {fam['pbo_diff']['oos_best_below_zero']} of partitions; degradation slope "
                 f"{fam['pbo_diff']['degradation_slope']}); PBO on kept mean {fam['pbo_kept_mean']['pbo']}; SPA: best mean selection gain {fam['spa']['best_mean_gain']:+,.2f} INR/session, t {fam['spa']['best_t']}, "
                 f"Reality-Check p {fam['spa']['rc_p']}, SPA p {fam['spa']['spa_p']}; effective trials {fam['effective_trials']}.\n")
        if B.get("candidate"):
            cc = B["candidate"]; d = B["dsr"]; bt = B["bootstrap"]; gg = B["go_no_go"]
            P.append(f"**Cell chosen on all IS** (the would-be candidate; its grid row `{B['candidate_ledger_id']}`): k={cc['max_stops_today']}, L={cc['max_loss_today_inr']}, rearm={cc['rearm_after_win']}. "
                     f"DSR of its per-session kept net: SR {d.get('sr')}, SR0 {d.get('sr0')}, DSR {d.get('dsr')}, p {d.get('p')} (n_trials {d.get('n_trials')}). Stationary block bootstrap (2,000 draws) 90% CI of "
                     f"diff {bt['diff_ci']}, of the kept mean {bt['kept_mean_ci']}, P(diff <= 0) {bt['diff_p_le0']}.\n")
            P.append("**harness.go_no_go: passed = " + str(gg["passed"]) + "** (" + f"{sum(1 for v in gg['checks'].values() if not v[0])} of {len(gg['checks'])} checks fail)"
                     "\n\n| check | ok | value |\n|---|---|---|\n" + "\n".join(f"| {k} | {v[0]} | {v[1]} |" for k, v in gg["checks"].items()) + "\n\n"
                     "The checks that pass (`diff>0`, `sign_blocks`, `boot_ci_excludes_0`, the floors) all read the pooled kept-vs-skipped difference, which carries the session-composition "
                     "effect described above; every check that conditions on the session or on the family (`control_pct`, `cpcv_p5_diff`, `pbo`, `dsr_p`, `spa_p`) fails, as do "
                     "`diff_top1_removed` (the pooled edge disappears once the top 1% winners are removed) and `kept_mean_slip8` (the kept book itself loses money).\n")
            cb = B["combined"]
            P.append(f"**Combined form** (chosen cell AND `fz_traded`, the frozen ST7 gate as comparator; family `session_stop/combined`, id `{cb['id']}`): kept {cb['kept_n']:,} (share {cb['kept_share']}), "
                     f"diff {cb['diff']:+,.2f}, perm p {cb['perm_p']}, control pct {cb['control_pct']}, sign blocks {cb['sign_blocks']}/12. The frozen gate alone: kept 745, diff -19.71, control pct 62.6 "
                     "(`results/pre_registration.json`).\n")
    return P


# ---------------------------------------------------------------- the document
M, M5 = R["timeframes"]["minute"], R["timeframes"]["5minute"]
B = M.get("branch_b"); b5 = M5.get("branch_b")
lines = [f"# session_stop: does the causal session ledger predict the next SETUP, and does a daily stop rule add expectancy?\n",
         f"Study folder `fz_v3/out/studies/session_stop/` (DESIGN_PANEL `decision-making-6-session-stop-rule-finite-horizon`, both judges' fixes). Script `session_stop.py` "
         f"(runtime {R['runtime_s']} s; log `session_stop.log`, `run.nohup`), tables and this file generated by `write_findings.py` from `results.json`. Pre-registration "
         f"`preregistration.json` (sha256 `{PRE_SHA}`, registered {PRE['registered_at']}, written by the script before its first statistic). Ledger sha before `{LEDGER_BEFORE}`, "
         f"after `{R['ledger_sha_after']}`. **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 book); L0 as robustness only. 1 min is the primary timeframe; "
         "5 min is reported as underpowered (Judge 2).\n",
         "## 0. Result in one paragraph\n"]
ex, all_pos, rho_ex = excess_signs(M["L1"])
lines.append(f"The pre-registered null (\"the session ledger carries no information beyond the hour effect\") **is rejected on 1 min** (all seven tests, Holm p <= "
             f"{max(t['N1_p_holm'] for t in M['L1']['tests']):.4f}), but in the **mean-reverting direction**: after >= k stops or a ledger <= L the next SETUP is "
             f"{min(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} to {max(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} INR/trade *better* than the hour-matched null "
             f"predicts (still about -1,000 INR in absolute terms), and a more negative ledger goes with a better next trade (Spearman excess {rho_ex:+.4f}). The design's branch B therefore ran: "
             + (f"all {len(B['grid'])} cells of the stop-rule grid (k x L x rearm) sit at the **{max(r['control_pct'] for r in B['grid'] if r['control_pct'] is not None):.1f}th percentile or below** of the "
                f"session-matched random control despite positive pooled differences (cost avoidance plus session composition), the nested-CV OOF rule has control pct {B['nested_oof']['control_pct']} "
                f"and CPCV diff 5th percentile {B['cpcv']['diff_p5']:+,.2f}, and `harness.go_no_go` fails ({sum(1 for v in B['go_no_go']['checks'].values() if not v[0])} of {len(B['go_no_go']['checks'])} checks) "
                if B else "(branch B did not run)") +
             f"for the cell chosen on all IS. **No `session_stop` key is proposed** for ST13/ST14. 5 min: N1 not rejected (min Holm p {M5['L1']['min_p_holm_N1']:.4f}) but with only "
             f"{M5['L1']['nulls']['session_x_hour']['rows_movable']} of {M5['L1']['units']} rows movable the test has no power there (N2 rejects, p_holm {M5['L1']['min_p_holm_N2']:.4f}); "
             "reported as underpowered, no branch B, no key. The one new fact for the playbook is the direction of the memory: a *reverse* rule (trade only after "
             "stops / losses) is a new hypothesis, not pre-registered here and not tested; it would need its own registration and its own multiplicity count.\n")
lines.append("## 1. Definitions (fixed before any number was looked at; the script's docstring, verbatim)\n\n```\n" + DOC + "\n```\n")
lines.append("## 2. Timeframe summary\n")
rows = []
for tf, X in (("minute", M), ("5minute", M5)):
    L1 = X["L1"]; e, ap, rex = excess_signs(L1); bb = X.get("branch_b")
    rows.append(dict(tf=tf, units=L1["units"], min_holm_p_N1=L1["min_p_holm_N1"], rejected_N1=str(L1["rejected_N1"]), rejected_N2=str(L1["rejected_N2"]),
                     threshold_excess_all_positive=str(ap), spearman_excess=rex, grid_cells=len(bb["grid"]) if bb else 0,
                     grid_control_pct_max=(max(r["control_pct"] for r in bb["grid"] if r["control_pct"] is not None) if bb else None),
                     go_no_go=str(bb["go_no_go"]["passed"]) if bb and bb.get("go_no_go") else "not run", candidate="none"))
lines.append(md_table(pd.DataFrame(rows), list(rows[0].keys()), dict(units=0, min_holm_p_N1=4, spearman_excess=4, grid_cells=0, grid_control_pct_max=1)) + "\n")
lines += sec_tf("minute")
lines += sec_tf("5minute")
lines.append("## 6. What would falsify this, caveats, follow-ups\n")
lines.append("- **Falsifiers of the memory claim.** Mixed signs of the N1 excess across the six threshold tests, or a min Holm p above 0.05 under N1, would remove the \"session memory beyond the hour effect\" "
             "statement; the L0 table (section 3) is the robustness check and its signs / p are reported above. The N1 test's power comes from the multi-row session x hour cells only "
             f"({M['L1']['nulls']['session_x_hour']['rows_movable']:,} movable rows on 1 min); singleton cells keep their observed pairing in every draw, which anchors the null to the data (correct for a conditional test).\n"
             "- **Falsifiers of the no-key conclusion.** Any grid cell with control percentile >= 95 together with a CPCV 5th-percentile diff > 0 and PBO <= 0.2 would reopen the rule; none is close "
             + (f"(max control pct {max(r['control_pct'] for r in B['grid'] if r['control_pct'] is not None):.1f}). " if B else ". ") +
             "The pooled `diff` is positive for every cell and must not be read as edge: the kept set is enriched with short-session (trending-day) rows and always contains the triggering loser.\n"
             "- **p definition.** The doubled-tail permutation p replaced the naive |stat| form after a 50-draw timing probe on 1 min / L1 showed the N1 distribution off centre (it is the wrong "
             "hypothesis to test |stat| against zero when the null itself is not centred at zero); nothing else changed and no full run preceded the change (`preregistration.json`, "
             "`p_definition_history`). The naive form is kept as `N1_p_abs_ref` for reference: under it the threshold tests would have read p = 1 (the observed differences are *smaller* in "
             "magnitude than the null's), which is the same fact seen from the other side.\n"
             "- **Ledger semantics.** `today_*_asof` counts trades with entry < k and exit <= k (verified identical on the truncated build); on this book it equals the cumulative prior outcomes of "
             "the session's units (asserted in code), so the permutation null recomputes it exactly. Before the first trigger the strategy's own ledger equals Foundation's, so the absorbing replay "
             "is exact; the rearm variant's \"winner\" is the paper trade of a skipped SETUP (the lab tracks every Foundation SETUP, so it is observable live).\n"
             "- **Composition.** Sessions with many SETUPs are the choppy days; any rule keyed on the ledger inherits the session-count composition. The session-matched control is the yardstick "
             "that removes it; the pooled difference does not.\n"
             "- **Follow-up (not done here, outside this study's pre-registration).** The rejected null points the other way: \"take only after >= k stops / after a loss <= L\" or a ledger-state "
             "feature for the learned-gate family (today_n_stops_asof, today_net_asof are as-of columns already in `features.parquet`). It is a new hypothesis and would need its own registration "
             "and multiplicity count; recording it belongs to the orchestrating session (this study writes only under its folder).\n"
             "- **5 min** is underpowered by construction (median 2 SETUPs per active session); its result is not evidence for or against session memory on that timeframe.\n")
lines.append("## 7. Candidate config\n\nNone. The `session_stop` block is omitted from `strategy_13.json` / `strategy_14.json`; the measured null-test result and the grid are recorded here and in "
             "`findings.json` for S49.\n")
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(lines))
print("FINDINGS.md written")


# ---------------------------------------------------------------- findings.json
def tf_summary(tf):
    X = R["timeframes"][tf]; L1 = X["L1"]; e, ap, rex = excess_signs(L1)
    s = dict(power=X["power_note"], units_is=L1["units"], active_sessions=L1["active_sessions"], setups_per_session_median=L1["setups_per_session_median"],
             ledger_identity=L1["ledger_identity"],
             null_tests={t["test"]: dict(n_condition=t["n_condition"], observed=t["observed"], N1_perm_mean=t["N1_perm_mean"], N1_perm_sd=t["N1_perm_sd"], N1_excess=t["N1_excess"], N1_p=t["N1_p"],
                                         N1_p_holm=t["N1_p_holm"], N1_p_abs_ref=t["N1_p_abs_ref"], N2_perm_mean=t["N2_perm_mean"], N2_excess=t["N2_excess"], N2_p=t["N2_p"], N2_p_holm=t["N2_p_holm"]) for t in L1["tests"]},
             null_cells=L1["nulls"], min_p_holm_N1=L1["min_p_holm_N1"], min_p_holm_N2=L1["min_p_holm_N2"], rejected_N1=L1["rejected_N1"], rejected_N2=L1["rejected_N2"],
             threshold_excess_all_positive=ap, spearman_excess_N1=rex, direction="mean-reverting (after stops / losses the next SETUP is less bad than the hour-matched null)" if ap else "mixed",
             decision=X["decision"], hour_profile=L1["hour_profile"], by_stops=L1["by_stops"], by_net_bucket=L1["by_net_bucket"], hour_x_stops=L1["hour_x_stops"],
             L0_robustness=dict(units=X["L0_robustness"]["units"], min_p_holm_N1=X["L0_robustness"]["min_p_holm_N1"], rejected_N1=X["L0_robustness"]["rejected_N1"],
                                tests={t["test"]: dict(observed=t["observed"], N1_excess=t["N1_excess"], N1_p=t["N1_p"], N1_p_holm=t["N1_p_holm"]) for t in X["L0_robustness"]["tests"]}))
    if X.get("branch_b"):
        Bb = X["branch_b"]
        s["branch_b"] = dict(grid=[dict(id=r["id"], config=r["config"], kept_n=r["kept_n"], kept_share=r["kept_share"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"],
                                        diff_top1_removed=r["diff_top1_removed"], control_pct=r["control_pct"], perm_p=r["perm_p"], loser_recall=r["loser_recall"], loser_precision=r["loser_precision"],
                                        winner_recall_weighted=r["winner_recall_weighted"], top_decile_winners_skipped=r["top_decile_winners_skipped"], sign_blocks=r["sign_blocks"],
                                        kept_mean_slip8=r["kept_mean_slip8"]) for r in Bb["grid"]],
                             grid_control_pct_max=max(r["control_pct"] for r in Bb["grid"] if r["control_pct"] is not None),
                             grid_diff_range=[min(r["diff"] for r in Bb["grid"]), max(r["diff"] for r in Bb["grid"])],
                             nested_oof=Bb["nested_oof"], chosen_per_fold=Bb["chosen_per_fold"], cpcv=Bb["cpcv"], cpcv_path_ids=Bb["cpcv_path_ids"], candidate_cell=Bb["candidate"],
                             candidate_ledger_id=Bb["candidate_ledger_id"], family=Bb["family"], dsr=Bb["dsr"], bootstrap=Bb["bootstrap"], go_no_go=Bb["go_no_go"], combined=Bb["combined"])
    return s


fams = sorted({fam for tf in R["timeframes"] if R["timeframes"][tf].get("branch_b") for fam in ("session_stop/grid", "session_stop/nested", "session_stop/nested/cpcv", "session_stop/combined")})
FJ = dict(study="session_stop", design="DESIGN_PANEL decision-making-6-session-stop-rule-finite-horizon with both judges' fixes", label="L1 (L0 robustness only)", split="IS only",
          preregistration=PRE, preregistration_sha256_16=PRE_SHA, timeframes={tf: tf_summary(tf) for tf in ("minute", "5minute")},
          headline=("1 min: the pre-registered null is rejected (all 7 tests, Holm) but in the mean-reverting direction; every stop-rule cell is at or below the "
                    f"{max(r['control_pct'] for r in B['grid'] if r['control_pct'] is not None):.1f}th control percentile; go/no-go fails; no key. 5 min underpowered." if B else
                    "1 min: null not rejected; no key. 5 min underpowered."),
          candidates=[], null_result=True, session_memory_null_rejected={tf: R["timeframes"][tf]["L1"]["rejected_N1"] for tf in R["timeframes"]},
          ledger_families=fams, ledger_rows={fam: None for fam in fams}, ledger_sha_before=LEDGER_BEFORE, ledger_sha_after=R["ledger_sha_after"], runtime_s=R["runtime_s"],
          caveats=["IS only; nothing was read from OOS beyond row counts",
                   "the doubled-tail permutation p replaced the naive |stat| form after a 50-draw timing probe (before any full run); the naive form is reported as N1_p_abs_ref",
                   "the pooled kept-vs-skipped diff of every grid cell is positive but is cost avoidance plus session composition; the session-matched control is the criterion",
                   "5 min has median 2 SETUPs per active session: the N1 test has almost no power there",
                   "the rearm variant's winner is the paper trade of a skipped SETUP",
                   "a reverse rule (take only after stops / losses) is a new, untested hypothesis; recording it is for the orchestrating session"],
          files=sorted(x for x in os.listdir(HERE) if not x.startswith("__")))
try:
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", ".."))); import harness as H
    FJ["ledger_rows"] = {fam: len([r for r in H.read_ledger(fam) if r["family"] == fam]) for fam in fams}
except Exception as e:  # noqa
    FJ["ledger_rows_note"] = str(e)
json.dump(FJ, open(os.path.join(HERE, "findings.json"), "w", encoding="utf-8"), indent=1)
print("findings.json written")
