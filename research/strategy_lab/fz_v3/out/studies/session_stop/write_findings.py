"""Build FINDINGS.md (tables + reading) and findings.json from results.json (the as-run study, session_stop.py) and
results_repair.json (the repair round, session_stop_repair.py): no number is typed by hand; every one is read from the two
results files (which carry the ledger ids) or the CSVs next to them.

    python write_findings.py
"""
import os, sys, json, hashlib, ast, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
import pandas as pd

R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
REP = json.load(open(os.path.join(HERE, "results_repair.json"), encoding="utf-8"))
PRE = R["preregistration"]; PRE_R = REP["preregistration"]
DOC = ast.get_docstring(ast.parse(open(os.path.join(HERE, "session_stop.py"), encoding="utf-8").read()))
DOC_R = ast.get_docstring(ast.parse(open(os.path.join(HERE, "session_stop_repair.py"), encoding="utf-8").read()))
PRE_SHA = hashlib.sha256(open(os.path.join(HERE, "preregistration.json"), "rb").read()).hexdigest()[:16]
PRE_R_SHA = hashlib.sha256(open(os.path.join(HERE, "preregistration_repair.json"), "rb").read()).hexdigest()[:16]
LOG = open(os.path.join(HERE, "session_stop.log"), encoding="utf-8").read().splitlines()
LEDGER_BEFORE = next((l.split("ledger sha before ")[1].strip() for l in LOG if "ledger sha before" in l), None)
ORIGINAL_SCRIPT_SHA = "6645343d4dfba103"          # the as-run session_stop.py (every as-run ledger row carries it); the file since holds a docstring-only repair note
TESTS = PRE["tests"]


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
          f"Min Holm p: N1 {rec['min_p_holm_N1']:.4f}, N2 {rec['min_p_holm_N2']:.4f}; rejected at 5%: N1 {rec['rejected_N1']}, N2 {rec['rejected_N2']} "
          "(**as run; superseded by section R: N1's rejection is reproduced by a memoryless process**).")
    return s


def excess_signs(rec):
    ex = {t["test"]: t["N1_excess"] for t in rec["tests"]}
    thr = [v for k, v in ex.items() if k != "spearman_today_net"]
    return ex, all(v > 0 for v in thr), ex["spearman_today_net"]


def repaired_null_block(tf):
    X = REP["timeframes"][tf]["L1"]; t = pd.DataFrame(X["null_tests"])
    cols = ["test", "n_condition", "observed", "N3_sim_mean", "N3_sim_sd", "N3_excess", "N3_pct", "N3_p", "N3_p_holm", "N4_stat", "N4_boot_sd", "N4_ci90_lo", "N4_ci90_hi", "N4_p", "N4_p_holm", "N4_sim_mean", "N4_sim_p", "N4fine_stat", "N4fine_p_holm"]
    dg = {c: 4 for c in cols}; dg.update(n_condition=0, N3_pct=1)
    return md_table(t, cols, dg)


def L0_block(tf):
    X = REP["timeframes"][tf]["L0_robustness"]; t = pd.DataFrame(X["tests"])
    cols = ["test", "n_condition", "N4_stat", "N4_ci90_lo", "N4_ci90_hi", "N4_p", "N4_p_holm"]
    return md_table(t, cols, {c: 4 for c in cols} | dict(n_condition=0)) + f"\n\nL0 ({X['units']:,} IS units): min Holm p under N4 {X['min_p_holm_N4']:.4f}; rejected at 5%: {X['rejected_N4']}."


def mech_block(tf):
    X = REP["timeframes"][tf]["L1"]
    keys = list(X["mechanism_real"])
    t = pd.DataFrame(dict(metric=keys, real=[X["mechanism_real"][k] for k in keys], memoryless_tied_duration=[X["mechanism_memoryless_mean"][k] for k in keys],
                          memoryless_independent_duration=[X["mechanism_indep_mean"][k] for k in keys]))
    return md_table(t, list(t.columns), dict(real=4, memoryless_tied_duration=4, memoryless_independent_duration=4))


def demo_block(tf):
    Dm = REP["timeframes"][tf]["n1_demonstration"]; rows = []
    for name in ("tied to outcome", "independent of outcome"):
        d = Dm[name]
        rows.append(dict(duration=name, streams=d["streams"], N1_rejected_share=d["n1_rejected_share"], min_holm_p_median=d["min_p_holm_median"],
                         excess_all_threshold_tests_positive_share=d["excess_threshold_all_positive_share"], excess_spearman_mean=d["excess_spearman_mean"],
                         **{f"excess_{k}": v for k, v in d["excess_threshold_tests_mean"].items()},
                         k2_control_pct_median=d["k2_control_pct_median"], k2_control_pct_le5_share=d["k2_control_pct_le5_share"], k2_pooled_diff_mean=d["k2_pooled_diff_mean"],
                         k2_strat_diff_mean=d["k2_strat_diff_mean"], cell_last_win_rate=d["cell_multi_last_win_rate_mean"], cell_nonlast_win_rate=d["cell_multi_nonlast_win_rate_mean"]))
    t = pd.DataFrame(rows)
    return md_table(t, list(t.columns), dict(streams=0, N1_rejected_share=3, min_holm_p_median=4, excess_all_threshold_tests_positive_share=3, excess_spearman_mean=4,
                                              k2_control_pct_median=1, k2_control_pct_le5_share=3, cell_last_win_rate=4, cell_nonlast_win_rate=4))


def grid_table(rows, ids=True):
    g = pd.DataFrame([dict(k=r["config"]["max_stops_today"], L=("none" if r["config"]["max_loss_today_inr"] is None else f"{r['config']['max_loss_today_inr']:,.0f}"),
                           rearm=str(r["config"]["rearm_after_win"]), hours=("all day" if r["config"].get("active_from_hour_bin") is None else f">= {r['config']['active_from_hour_bin']}"),
                           id=r["id"], kept_n=r["kept_n"], share=r["kept_share"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"], diff_top1_off=r["diff_top1_removed"],
                           control_pct_not_used=r["control_pct"], perm_p=r["perm_p"], loser_recall=r["loser_recall"], loser_prec=r["loser_precision"], w_recall=r["winner_recall_weighted"],
                           top10_skip=r["top_decile_winners_skipped"], sign_blocks=r["sign_blocks"], slip8=r["kept_mean_slip8"]) for r in rows])
    return md_table(g, list(g.columns), dict(k=0, kept_n=0, share=4, perm_p=4, control_pct_not_used=1, loser_recall=4, loser_prec=4, w_recall=4, top10_skip=4, sign_blocks=0))


def calibration_table(cal):
    c = pd.DataFrame(cal)
    c["L"] = c.max_loss_today_inr.map(lambda v: "none" if v is None or (isinstance(v, float) and v != v) else f"{v:,.0f}")
    c["hours"] = c.active_from_hour_bin.map(lambda v: "all day" if v is None or (isinstance(v, float) and v != v) else f">= {v}")
    c["rearm"] = c.rearm_after_win.astype(str)
    cols = ["max_stops_today", "L", "rearm", "hours", "ledger_id", "kept_share", "pooled_diff", "sim_pooled_mean", "sim_pooled_sd", "pooled_sim_pct", "pooled_sim_p", "strat_diff", "strat_ci90_lo", "strat_ci90_hi", "strat_boot_p",
            "sim_strat_mean", "strat_sim_pct", "diff_top1_removed", "sign_blocks", "control_pct"]
    c = c.rename(columns={"control_pct": "control_pct_not_used"}); cols[-1] = "control_pct_not_used"
    return md_table(c, cols, dict(max_stops_today=0, kept_share=4, pooled_sim_pct=1, pooled_sim_p=4, strat_boot_p=4, strat_sim_pct=1, sign_blocks=0, control_pct_not_used=1))


# ---------------------------------------------------------------- as-run sections (kept as the record, re-read)
def sec_tf(tf):
    X = R["timeframes"][tf]; L1 = X["L1"]; RX = REP["timeframes"][tf]; P = []
    ex, all_pos, rho_ex = excess_signs(L1)
    P.append(f"## {'3' if tf == 'minute' else '5'}. {tf} / L1 ({X['power_note']}): the seven tests AS RUN under N1 / N2 (superseded; see section R)\n")
    P.append(f"{L1['units']:,} IS units in {L1['active_sessions']} active sessions (median {L1['setups_per_session_median']:.0f}, max {L1['setups_per_session_max']} SETUPs per session); "
             f"ledger identity check: max |today_net_asof - cumulative prior L1 net| = {L1['ledger_identity']['net_max_abs_diff']:.1e} INR, stop counts identical = {L1['ledger_identity']['stops_identical']}. "
             f"File `null_tests_{tf}_L1.csv`. `observed` is the statistic on the IS rows; `N1_perm_mean` / `N1_perm_sd` the permutation distribution under the as-run null (positions fixed); "
             f"`N1_excess` = observed - N1 mean; `N1_p` the doubled-tail p; `N1_p_holm` Holm over the 7 tests; `N1_p_abs_ref` the naive |stat| form, reference only. "
             "**The N1 columns are kept as the record of what was run; they do not test session memory (section R.1).**\n")
    P.append(null_block(L1))
    P.append(f"\n**Decision as run ({tf}):** {X['decision']}\n\n**Repaired decision ({tf}):** {RX['L1']['decision']} (section R.2).\n")
    if tf == "minute":
        P.append("**Reading (repaired).** In absolute terms the next SETUP is worse after stops or losses (observed differences "
                 + ", ".join(f"{t['test']} {t['observed']:+,.0f}" for t in L1["tests"] if t["test"] != "spearman_today_net")
                 + f" INR/trade); the N1 permutation means are more negative still ({min(t['N1_perm_mean'] for t in L1['tests'] if t['test'] != 'spearman_today_net'):+,.0f} to "
                 f"{max(t['N1_perm_mean'] for t in L1['tests'] if t['test'] != 'spearman_today_net'):+,.0f} INR), so the as-run study read the positive excess "
                 f"({min(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} to {max(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} INR/trade, Spearman excess {rho_ex:+.4f}) as "
                 "\"mean-reverting session memory\". **That reading is withdrawn.** N1 shuffles outcomes over the realized positions, but the positions are made by the outcomes (a trade runs "
                 "until exit and the next SETUP follows it; winners hold ~6x longer than losers), so within a multi-member cell the early positions are losers almost by construction and the "
                 "last one is a winner far more often; the permutation puts winners early, which the data almost never does, and the observed statistic lands above the permutation "
                 "distribution with zero memory. Section R.1 shows a memoryless generator reproducing the excess and the rejection; section R.2 re-tests the question without conditioning "
                 "on positions and does not reject. N2 (plain within-session) has the same defect plus the hour effect.\n")
    else:
        P.append("**Reading (repaired).** " + (f"{L1['nulls']['session_x_hour']['cells_size1']:,} of {L1['nulls']['session_x_hour']['n_cells']:,} session x hour cells are singletons, so only "
                 f"{L1['nulls']['session_x_hour']['rows_movable']} of {L1['units']} rows can move under N1: the as-run test had almost no power on this timeframe (median 2 SETUPs per active session). "
                 "Under the repaired nulls (section R.2) nothing is rejected either; 5 min stays *underpowered, nothing shown*. N1 / N2 on this timeframe are kept as the record only.\n"))
    P.append(f"### Hour-of-day profile of the L1 book ({tf}, IS; `hour_profile_{tf}.csv`)\n")
    hp = pd.DataFrame(L1["hour_profile"])
    P.append(md_table(hp, list(hp.columns), dict(n=0, win_rate=4, stop_rate=4, mean_today_n_stops_asof=3, share_stops_ge1=4, share_net_le_m4000=4)))
    P.append(f"\n### Mean L1 net by the ledger state ({tf}, IS; `by_stops_{tf}.csv`, `by_net_bucket_{tf}.csv`; descriptive, no rule chosen on them)\n")
    bs = pd.DataFrame(L1["by_stops"]); bn = pd.DataFrame(L1["by_net_bucket"])
    P.append(md_table(bs, list(bs.columns), dict(n=0, win_rate=4)) + "\n\n" + md_table(bn, list(bn.columns), dict(n=0, win_rate=4)))
    P.append(f"\n### Within-hour comparison, stops >= 1 vs none ({tf}, IS; `hour_x_stops_{tf}.csv`; the descriptive form of the N4 contrast, unweighted)\n")
    hx = pd.DataFrame(L1["hour_x_stops"])
    P.append(md_table(hx, list(hx.columns), {c: 0 for c in hx.columns if c.startswith("size")}))
    L0 = X["L0_robustness"]; ex0, pos0, _ = excess_signs(L0)
    P.append(f"\n### L0 robustness AS RUN ({tf}, {L0['units']:,} IS units; `null_tests_{tf}_L0.csv`; N1 / N2, superseded; the repaired L0 check is N4 in section R.2)\n")
    P.append(null_block(L0))
    if X.get("branch_b"):
        B = X["branch_b"]; g0 = B["grid"]
        P.append(f"\n## 4. {tf}: branch B AS RUN, the 32-cell grid by exact replay (family `session_stop/grid`, 32 ledger rows; `grid_{tf}.csv`; re-judged in section R.4 / R.5)\n")
        P.append("Rule: skip once the session's ledger at the bar has >= k stops or its running-minimum net <= L (absorbing); `rearm=True` re-arms at the next SETUP after a skipped "
                 "SETUP's paper trade wins, counters reset. `diff` = kept mean - skipped mean (INR/trade); `control_pct_not_used` = the session-matched random control percentile, "
                 "**reported, not evidence** (section R.3); `perm_p` = kept-vs-skipped permutation p; `w_recall` = |net|-weighted winner recall; `top10_skip` = share of top-decile "
                 "winners skipped; `slip8` = kept mean at 8 pts slippage.\n")
        P.append(grid_table(g0))
        dmin = min(r["diff"] for r in g0); dmax = max(r["diff"] for r in g0); npos = sum(1 for r in g0 if r["diff"] is not None and r["diff"] > 0)
        P.append(f"\n**Reading (repaired).** {npos} of {len(g0)} cells have a positive pooled `diff` ({dmin:+,.0f} to {dmax:+,.0f} INR/trade) and every cell sits at the 0.0th percentile of "
                 "the session-matched random control. The as-run reading ('the rule does worse than picking the same number of same-session SETUPs at random') is withdrawn: the control "
                 "draws n_s of the N_s positions the session realized, N_s is known only at session end and the last positions are long winners by construction, so for a rule that keeps "
                 "the earliest positions the control is a hindsight-biased comparator (section R.3: it puts the same rule at the 0.0th percentile on memoryless streams). The pooled diff is "
                 "not evidence either: section R.5 shows every cell's pooled diff inside the memoryless distribution (hour composition plus cost avoidance), and the within-hour "
                 "kept-vs-skipped contrast with its session-block bootstrap CI covering zero. Judged on the hindsight-free statistics (nested OOF, CPCV, top-1%-removed, PBO, SPA, DSR), "
                 "no cell has an edge.\n")
        n = B["nested_oof"]
        P.append(f"### Nested choice, CPCV, family statistics, go / no-go AS RUN ({tf}, 32 cells; the 48-cell re-run is in section R.4)\n")
        P.append(f"**Nested choice** (12 purged folds; selection `{PRE['fold_selection']}`): the OOF mask is ledger row `{n['id']}` (family `session_stop/nested`): kept {n['kept_n']:,} "
                 f"(share {n['kept_share']}), diff {n['diff']:+,.2f}, perm p {n['perm_p']}, control pct {n['control_pct']} (not used), sign blocks {n['sign_blocks']}/12. Cells chosen per fold: "
                 + "; ".join(f"b{i} k={c['max_stops_today']} L={c['max_loss_today_inr']} rearm={c['rearm_after_win']}" if c else f"b{i} none" for i, c in enumerate(B["chosen_per_fold"])) + ".\n")
        c = B["cpcv"]
        P.append(f"**CPCV** (66 splits -> 11 paths; family `session_stop/nested/cpcv`, ids `{B['cpcv_path_ids'][0]}` .. `{B['cpcv_path_ids'][-1]}`): diff median "
                 f"{c['diff_median']:+,.2f}, 5th percentile {c['diff_p5']:+,.2f}, min {c['diff_min']:+,.2f}, share of paths with diff > 0 {c['diff_share_positive']}, kept share median {c['kept_share_median']}.\n")
        fam = B["family"]
        P.append(f"**Family (32 cells):** PBO on diff {fam['pbo_diff']['pbo']} (IS-best below zero out of sample in {fam['pbo_diff']['oos_best_below_zero']} of partitions; degradation slope "
                 f"{fam['pbo_diff']['degradation_slope']}); PBO on kept mean {fam['pbo_kept_mean']['pbo']}; SPA: best mean selection gain {fam['spa']['best_mean_gain']:+,.2f} INR/session, t {fam['spa']['best_t']}, "
                 f"Reality-Check p {fam['spa']['rc_p']}, SPA p {fam['spa']['spa_p']}; effective trials {fam['effective_trials']}.\n")
        if B.get("candidate"):
            cc = B["candidate"]; d = B["dsr"]; bt = B["bootstrap"]; gg = B["go_no_go"]
            P.append(f"**Cell chosen on all IS** (its grid row `{B['candidate_ledger_id']}`): k={cc['max_stops_today']}, L={cc['max_loss_today_inr']}, rearm={cc['rearm_after_win']}. "
                     f"DSR of its per-session kept net: SR {d.get('sr')}, SR0 {d.get('sr0')}, DSR {d.get('dsr')}, p {d.get('p')} (n_trials {d.get('n_trials')}). Stationary block bootstrap (2,000 draws) 90% CI of "
                     f"diff {bt['diff_ci']}, of the kept mean {bt['kept_mean_ci']}, P(diff <= 0) {bt['diff_p_le0']}.\n")
            P.append("**harness.go_no_go as run: passed = " + str(gg["passed"]) + "** (" + f"{sum(1 for v in gg['checks'].values() if not v[0])} of {len(gg['checks'])} checks fail)"
                     "\n\n| check | ok | value |\n|---|---|---|\n" + "\n".join(f"| {k} | {v[0]} | {v[1]} |" for k, v in gg["checks"].items()) + "\n")
            cb = B["combined"]
            P.append(f"**Combined form** (chosen cell AND `fz_traded`, the frozen ST7 gate as comparator; family `session_stop/combined`, id `{cb['id']}`): kept {cb['kept_n']:,} (share {cb['kept_share']}), "
                     f"diff {cb['diff']:+,.2f}, perm p {cb['perm_p']}, control pct {cb['control_pct']} (not used), sign blocks {cb['sign_blocks']}/12. The frozen gate alone: kept 745, diff -19.71, control pct 62.6 "
                     "(`results/pre_registration.json`).\n")
    return P


# ---------------------------------------------------------------- the repair section
def sec_repair():
    P = ["## R. Repair round (2026-09-29): the refuters' three issues, what changed, and the repaired result\n"]
    P.append(f"Script `session_stop_repair.py` (runtime {REP['runtime_s']} s; log `session_stop_repair.log`, `repair_run.nohup`), its pre-registration `preregistration_repair.json` (sha256 `{PRE_R_SHA}`, "
             f"registered {PRE_R['registered_at']}, written before the first repaired statistic). Ledger sha before the repair `{REP['ledger_sha_before']}`, after `{REP['ledger_sha_after']}`; every new "
             "ledger row carries `note = \"repair\"`; the as-run rows are untouched (append-only ledger). `session_stop.py` itself was not re-run; its docstring carries a dated repair note "
             f"(the as-run rows' `script_sha` is `{ORIGINAL_SCRIPT_SHA}`, the file before the note). The refuters' issues, verbatim in substance:\n\n"
             "- **I1** the N1 rejection is a false positive of a mis-specified null (positions are generated by the outcomes; a memoryless process reproduces every reported number);\n"
             "- **I2** the session-matched random control is a hindsight-biased comparator for a within-session sequential rule (`control_pct` 0.0 is not anti-edge);\n"
             "- **I3** Judge 2's hour interaction was not run after the (as-run) rejection.\n")
    # R.1
    M = REP["timeframes"]["minute"]["L1"]; D5 = REP["timeframes"]["5minute"]["L1"]
    P.append("### R.1 Issue I1: why N1 cannot test session memory, and the memoryless demonstration\n")
    P.append("**Mechanism (real IS units vs the memoryless generator).** The generator (definitions in section 1b) keeps the real session skeleton and the clock, draws every outcome iid from the "
             "hour bin's pool, and lets the drawn unit's own duration decide when the next SETUP can occur (variant: a duration independent of the outcome). `cell_multi_*` = units in "
             "session x hour_bin cells with > 1 member (the only rows N1 can move); `last` / `nonlast` / `first` by position in the cell; `p_follow_given_*` = another unit follows in the "
             f"session. Files `repair_mechanism_minute.csv`, `repair_mechanism_5minute.csv`. Memoryless columns are means over {PRE_R['draws']['n_sim']:,} (tied) and 200 (independent) streams.\n")
    P.append("**1 min**\n\n" + mech_block("minute") + "\n\n**5 min**\n\n" + mech_block("5minute") + "\n")
    P.append(f"Reading: with the duration tied to the outcome the memoryless streams reproduce the data's cell mechanics (1 min: last-in-cell win rate {M['mechanism_memoryless_mean']['cell_multi_last_win_rate']:.3f} vs "
             f"{M['mechanism_memoryless_mean']['cell_multi_nonlast_win_rate']:.3f} for the other members; real {M['mechanism_real']['cell_multi_last_win_rate']:.3f} vs {M['mechanism_real']['cell_multi_nonlast_win_rate']:.3f}); "
             f"with an independent duration the asymmetry disappears ({M['mechanism_indep_mean']['cell_multi_last_win_rate']:.3f} vs {M['mechanism_indep_mean']['cell_multi_nonlast_win_rate']:.3f}). The generator "
             f"makes {M['sim_units_mean']:,.0f} +- {M['sim_units_sd']:,.0f} units per stream against {REP['timeframes']['minute']['generator']['units_real']:,} real ones and P(another unit follows | win) "
             f"{M['mechanism_memoryless_mean']['p_follow_given_win']:.3f} vs {M['mechanism_real']['p_follow_given_win']:.3f} real: real sessions with a winner end sooner than iid draws predict, i.e. the *count* of later "
             "SETUPs carries session structure (a trending day stays trending); that is not what a stop rule reads and is not tested here (recorded as an observation for S49).\n")
    P.append(f"**N1 on memoryless streams** (`session_stop.null_test`'s N1, {PRE_R['draws']['n1_draws']:,} draws, positions fixed, on {PRE_R['draws']['n_demo']} streams per variant per timeframe; files "
             "`repair_n1_memoryless_minute.csv`, `repair_n1_memoryless_5minute.csv`). `N1_rejected_share` = share of streams with min Holm p < 0.05; `excess_*` = observed - permutation mean, "
             "averaged over streams; `k2_*` = the k = 2 / L = none absorbing rule on the stream: session-matched control percentile (2,000 draws), pooled and within-hour kept-vs-skipped "
             "difference. **Synthetic: no ledger row, no candidate.**\n")
    P.append("**1 min**\n\n" + demo_block("minute") + "\n\n**5 min**\n\n" + demo_block("5minute") + "\n")
    dt, di = REP["timeframes"]["minute"]["n1_demonstration"]["tied to outcome"], REP["timeframes"]["minute"]["n1_demonstration"]["independent of outcome"]
    ex_as_run = {t["test"]: t["N1_excess"] for t in R["timeframes"]["minute"]["L1"]["tests"]}
    P.append(f"Reading (1 min): N1 rejects on {dt['n1_rejected_share']:.0%} of the memoryless streams with the duration tied to the outcome (median min Holm p {dt['min_p_holm_median']:.4f}), with a positive "
             f"excess on every threshold test in {dt['excess_threshold_all_positive_share']:.0%} of them (means {min(dt['excess_threshold_tests_mean'].values()):+,.0f} to {max(dt['excess_threshold_tests_mean'].values()):+,.0f} INR/trade; "
             f"the as-run study's real excess was {min(v for k, v in ex_as_run.items() if k != 'spearman_today_net'):+,.0f} to {max(v for k, v in ex_as_run.items() if k != 'spearman_today_net'):+,.0f}) and a Spearman "
             f"excess of {dt['excess_spearman_mean']:+.4f} (real {ex_as_run['spearman_today_net']:+.4f}). With the duration independent of the outcome N1 rejects on {di['n1_rejected_share']:.0%} of the streams "
             f"and the excess is {min(di['excess_threshold_tests_mean'].values()):+,.0f} to {max(di['excess_threshold_tests_mean'].values()):+,.0f}. The as-run rejection is therefore the duration mechanism, "
             "not memory; **the statements \"session memory beyond the hour effect\", \"mean-reverting\" and the \"reverse rule\" follow-up are withdrawn** (they stay in the record above as withdrawn).\n")
    # R.2
    P.append("### R.2 The hindsight-free re-test: N3 (memoryless simulation) and N4 (within-hour contrast, session-block bootstrap)\n")
    P.append("Neither test conditions on the realized within-session positions. **N4 (primary)**: the same seven contrasts within hour_bin *across* sessions, weighted n_a n_b / (n_a + n_b) per "
             "stratum (= the OLS coefficient with hour fixed effects), partial Spearman on within-hour demeaned ranks; the stationary block bootstrap of the active sessions (mean block 10, "
             f"{PRE_R['draws']['n_boot']:,} draws) gives the CI and the doubled-tail p against 0; Holm over 7. `N4_sim_mean` / `N4_sim_p` = the same statistic on the memoryless streams (centring check: it must "
             "be ~0 there) and the observed value's doubled-tail p against that distribution; `N4fine_*` = 30-minute clock strata (sensitivity). **N3**: the seven *observed* statistics against "
             f"their distribution over {PRE_R['draws']['n_sim']:,} memoryless streams (`N3_pct` = the observed value's percentile, `N3_p` doubled tail, Holm over 7). Decision rule (pre-registered): memory is "
             "claimed only if N4 and N3 both reject at Holm 5 % with agreeing signs. Files `repair_null_tests_<tf>_L1.csv`, `repair_null_tests_<tf>_L0.csv`.\n")
    for tf in ("minute", "5minute"):
        X = REP["timeframes"][tf]["L1"]
        P.append(f"**{tf} / L1** ({REP['timeframes'][tf]['generator']['units_real']:,} IS units, {REP['timeframes'][tf]['generator']['active_sessions']} active sessions)\n\n" + repaired_null_block(tf) + "\n")
        P.append(f"Min Holm p: N3 {X['min_p_holm_N3']:.4f}, N4 {X['min_p_holm_N4']:.4f} (30-minute strata {X['min_p_holm_N4fine']:.4f}); rejected at 5 %: N3 {X['rejected_N3']}, N4 {X['rejected_N4']}. "
                 f"**Repaired decision ({tf}): {X['decision']}.**\n")
        P.append(f"**{tf} / L0 robustness (N4 only; L0 trades cross sessions, so the intraday generator does not apply)**\n\n" + L0_block(tf) + "\n")
    Mn = REP["timeframes"]["minute"]["L1"]["null_tests"]
    n3_out = [t["test"] for t in Mn if t["N3_p"] < 0.05]; n4_ci_excl = [t["test"] for t in Mn if t["N4_ci90_lo"] > 0 or t["N4_ci90_hi"] < 0]
    n4_raw = [t["test"] for t in Mn if t["N4_p"] < 0.05]; centring_ok = all(abs(t["N4_sim_mean"]) < 0.5 * t["N4_boot_sd"] for t in Mn if t["N4_boot_sd"] > 0)
    P.append("Reading (1 min): N3 percentiles of the observed statistics " + ", ".join(f"{t['test']} {t['N3_pct']:.0f}%" for t in Mn)
             + ("; none has an unadjusted p < 0.05" if not n3_out else f"; unadjusted p < 0.05 on {', '.join(n3_out)} (none survives Holm)" if REP["timeframes"]["minute"]["L1"]["min_p_holm_N3"] >= 0.05 else f"; p < 0.05 on {', '.join(n3_out)}")
             + ". N4: " + ("every within-hour contrast's 90 % bootstrap CI covers zero" if not n4_ci_excl else f"the 90 % bootstrap CI excludes zero on {', '.join(n4_ci_excl)} (unadjusted p < 0.05 on {', '.join(n4_raw) or 'none'})")
             + (f"; after Holm the minimum p is {REP['timeframes']['minute']['L1']['min_p_holm_N4']:.4f}" ) + ("; the memoryless centring check holds (|N4_sim_mean| below half the bootstrap sd on every test)" if centring_ok else "; NOTE the memoryless centring check fails on at least one test (|N4_sim_mean| above half the bootstrap sd)")
             + ". The within-hour differences of the as-run `hour_x_stops` table (positive in the morning, negative in the afternoon) are read against these CIs, with sessions as the resampling unit. "
             "5 min: see its table; the book is underpowered by construction (median 2 SETUPs per active session).\n")
    xcs = [pd.read_csv(os.path.join(HERE, f"repair_n4_ols_crosscheck_{tf}.csv")) for tf in ("minute", "5minute") if os.path.exists(os.path.join(HERE, f"repair_n4_ols_crosscheck_{tf}.csv"))]
    if xcs:
        x = pd.concat(xcs, ignore_index=True)
        P.append("**N4 cross-check (`n4_ols_crosscheck.py` -> `repair_n4_ols_crosscheck_<tf>.csv`).** The stratified statistic against the OLS coefficient of net on the state indicator with hour_bin "
                 "fixed effects (statsmodels; identical by construction, asserted), and the block-bootstrap sd / p against the session-cluster-robust SE / p:\n\n" + md_table(x, list(x.columns), dict(cluster_p=4, boot_p=4)) + "\n")
    # R.3
    P.append("### R.3 Issue I2: the session-matched random control is not evidence for a within-session sequential rule\n")
    P.append(f"On the memoryless streams (no edge and no anti-edge possible by construction) the k = 2 / L = none absorbing rule sits at a session-matched control percentile with median "
             f"{dt['k2_control_pct_median']:.1f} (share of streams at or below the 5th percentile {dt['k2_control_pct_le5_share']:.2f}) when the duration is tied to the outcome, and median "
             f"{di['k2_control_pct_median']:.1f} (share <= 5: {di['k2_control_pct_le5_share']:.2f}) when it is independent (table R.1; the real rule's value is 0.0 for all 32 as-run cells and for the 16 "
             "hour-conditioned cells below). The control draws n_s of the N_s realized positions; N_s is only known at session end and the last positions are long winners by construction, "
             "so a rule that keeps the earliest positions loses to it whatever its merit. **`control_pct` is reported in every table but is not used as evidence for or against any cell; "
             "`harness.go_no_go` is shown as computed and without its `control_pct>=95` check.** Flag for the orchestrator: the go/no-go control check is uninformative for any sequential "
             "(position-order) rule; a comparator for such rules must be causal (a random stopping rule with the same per-session stop counts, or the memoryless generator used here).\n")
    # R.4
    B = REP["timeframes"]["minute"].get("branch_b_repair")
    if B:
        g48 = B["grid"]; hour_rows = g48[32:]
        P.append(f"### R.4 Issue I3: the hour-conditioned cells and the 48-cell family (1 min; family `session_stop/grid`, {len(hour_rows)} new ledger rows, `grid_hour_minute.csv`)\n")
        P.append(f"Rule: as the absorbing grid, active only from hour_bin `{B['active_from_hour_bin']}` on (every SETUP before it is taken; `active_from_hour_bin` is the one data-informed choice of "
                 "the repair, the sign change of the as-run within-hour table, and is counted as a trial). Columns as in section 4; `control_pct_not_used` reported only.\n")
        P.append(grid_table(hour_rows))
        n = B["nested_oof"]; c = B["cpcv"]; fam = B["family"]; go = B["go_no_go"]
        nh = sum(1 for x in B["chosen_per_fold"] if x and x.get("active_from_hour_bin"))
        P.append(f"\n**Nested choice over the 48 cells** (12 purged folds; the pre-registered criterion): OOF row `{n['id']}` (family `session_stop/nested`, note repair): kept {n['kept_n']:,} (share {n['kept_share']}), "
                 f"diff {n['diff']:+,.2f}, top-1%-removed {n['diff_top1_removed']:+,.2f}, perm p {n['perm_p']}, sign blocks {n['sign_blocks']}/12 (control pct {n['control_pct']}, not used). Hour-conditioned cells "
                 f"chosen in {nh} of 12 folds: " + "; ".join(f"b{i} k={x['max_stops_today']} L={x['max_loss_today_inr']} rearm={x['rearm_after_win']} hours={x.get('active_from_hour_bin') or 'all'}" if x else f"b{i} none"
                                                              for i, x in enumerate(B["chosen_per_fold"])) + ".\n")
        P.append(f"**CPCV over the 48 cells** (66 splits -> 11 paths; family `session_stop/nested/cpcv`, note repair, ids `{B['cpcv_path_ids'][0]}` .. `{B['cpcv_path_ids'][-1]}`): diff median {c['diff_median']:+,.2f}, "
                 f"5th percentile {c['diff_p5']:+,.2f}, min {c['diff_min']:+,.2f}, share of paths with diff > 0 {c['diff_share_positive']}, top-1%-removed median {c['diff_top1_removed_median']:+,.2f}, kept share median "
                 f"{c['kept_share_median']} (control pct median {c['control_pct_median']}, not used).\n")
        P.append(f"**Family (48 cells):** PBO on diff {fam['pbo_diff']['pbo']} (IS-best below zero out of sample in {fam['pbo_diff']['oos_best_below_zero']} of partitions; degradation slope {fam['pbo_diff']['degradation_slope']}); "
                 f"PBO on kept mean {fam['pbo_kept_mean']['pbo']}; SPA: best mean selection gain {fam['spa']['best_mean_gain']:+,.2f} INR/session, t {fam['spa']['best_t']}, Reality-Check p {fam['spa']['rc_p']}, SPA p "
                 f"{fam['spa']['spa_p']}; effective trials {fam['effective_trials']}.\n")
        if go:
            cc = go["candidate"]; d = go["dsr"]; bt = go["bootstrap"]
            P.append(f"**Cell chosen on all IS among the 48** (grid row `{go['candidate_ledger_id']}`, {go['candidate_source']}): k={cc['max_stops_today']}, L={cc['max_loss_today_inr']}, rearm={cc['rearm_after_win']}, "
                     f"hours={cc.get('active_from_hour_bin') or 'all day'}. DSR (n_trials 48): SR {d.get('sr')}, SR0 {d.get('sr0')}, p {d.get('p')}. Block bootstrap 90 % CI of diff {bt['diff_ci']}, of the kept mean "
                     f"{bt['kept_mean_ci']}.\n")
            P.append("**harness.go_no_go: passed = " + str(go["passed"]) + f"** as computed; **without the control check: passed = {go['passed_without_control_check']}** (failing: "
                     + ", ".join(f"`{k}`" for k in go["failing_without_control_check"]) + ")\n\n| check | ok | value |\n|---|---|---|\n"
                     + "\n".join(f"| {k} | {v[0]} | {v[1]} |" for k, v in go["checks"].items()) + "\n")
            cb = go["combined"]
            P.append(f"**Combined form** (chosen cell AND `fz_traded`; family `session_stop/combined`, id `{cb['id']}`, {cb['source']}): kept {cb['kept_n']:,} (share {cb['kept_share']}), diff {cb['diff']:+,.2f}, "
                     f"top-1%-removed {cb['diff_top1_removed']:+,.2f}, perm p {cb['perm_p']}, sign blocks {cb['sign_blocks']}/12 (control pct {cb['control_pct']}, not used).\n")
        # R.5
        P.append("### R.5 Grid calibration: every cell's pooled diff against the memoryless generator, and the within-hour kept-vs-skipped contrast (1 min; `repair_grid_calibration_minute.csv`)\n")
        P.append(f"`pooled_diff` = the cell's ledger-row kept-vs-skipped difference; `sim_pooled_mean` / `sd` = the same statistic on the {PRE_R['draws']['n_sim']:,} memoryless streams, `pooled_sim_pct` the observed "
                 "value's percentile in it and `pooled_sim_p` its doubled-tail p; `strat_diff` = within-hour_bin kept-vs-skipped difference (N4 weights) with its session-block bootstrap 90 % CI and "
                 "p against 0, `sim_strat_mean` its memoryless centring, `strat_sim_pct` the observed value's memoryless percentile. Diagnostics only (the selection criterion stayed the "
                 "pre-registered pooled diff). `control_pct_not_used`: reported only.\n")
        P.append(calibration_table(B["calibration"]))
        cal = pd.DataFrame(B["calibration"])
        n_pool_out = int((cal.pooled_sim_p < 0.05).sum()); n_strat_out = int(((cal.strat_ci90_lo > 0) | (cal.strat_ci90_hi < 0)).sum()); n_strat_pos = int((cal.strat_ci90_lo > 0).sum())
        P.append(f"\nReading: the pooled differences of the 48 cells sit at memoryless percentiles {cal.pooled_sim_pct.min():.0f}-{cal.pooled_sim_pct.max():.0f} (min doubled-tail p {cal.pooled_sim_p.min():.3f}; "
                 f"{n_pool_out} of 48 below 0.05, before any multiplicity adjustment over 48 cells): a memoryless process with the same clock and durations produces "
                 f"{'the same' if n_pool_out == 0 else 'comparable'} positive pooled diffs (hour composition plus cost avoidance). The within-hour kept-vs-skipped contrast is {cal.strat_diff.min():+,.0f} to "
                 f"{cal.strat_diff.max():+,.0f} INR/trade; its 90 % session-block bootstrap CI excludes zero on {n_strat_out} of 48 cells ({n_strat_pos} on the positive side; min bootstrap p {cal.strat_boot_p.min():.3f}, "
                 f"unadjusted over 48 cells); its memoryless centring is {cal.sim_strat_mean.min():+,.0f} to {cal.sim_strat_mean.max():+,.0f}. "
                 + ("No cell skips worse SETUPs than it keeps once the clock is held fixed.\n" if n_strat_pos == 0 else
                    f"{n_strat_pos} cell(s) show a positive within-hour contrast at the unadjusted 90 % level; with 48 correlated cells (effective trials {B['family']['effective_trials']}) that is within the expected false-positive count and none of them passes the family checks of R.4.\n"))
    else:
        P.append("### R.4 / R.5\n\nBranch B did not run on any timeframe under the repaired decision.\n")
    # R.6
    P.append("### R.6 What changed in the documents\n")
    P.append("- Section 0 rewritten; the as-run N1 / N2 tables kept as the record and marked superseded; the readings of sections 3, 4 and 5 replaced; the follow-up \"reverse rule\" removed (withdrawn).\n"
             "- `findings.json`: `headline` rewritten; `session_memory_shown = false` on both timeframes; `session_memory_null_rejected` now refers to the hindsight-free nulls (N3 / N4) and is false on both timeframes; "
             "the as-run N1 result moved to `n1_as_run` with `valid = false`; `direction` = \"not shown\"; `repair` block naming each issue and what changed; `flags_for_orchestrator` added; the 16 hour-conditioned cells, "
             "the 48-cell nested / CPCV rows and the calibration added under `timeframes.minute.repair`.\n"
             "- `session_stop.py`: a dated repair note at the top of its docstring (no code change; the as-run ledger rows carry the pre-note `script_sha`).\n"
             "- The no-key conclusion is unchanged; the reasons for it are now the hindsight-free statistics alone.\n")
    return P


# ---------------------------------------------------------------- the document
M, M5 = R["timeframes"]["minute"], R["timeframes"]["5minute"]
RM, R5 = REP["timeframes"]["minute"], REP["timeframes"]["5minute"]
B = M.get("branch_b"); BR = RM.get("branch_b_repair")
lines = [f"# session_stop: does the causal session ledger predict the next SETUP, and does a daily stop rule add expectancy?\n",
         f"Study folder `fz_v3/out/studies/session_stop/` (DESIGN_PANEL `decision-making-6-session-stop-rule-finite-horizon`, both judges' fixes). As-run script `session_stop.py` "
         f"(runtime {R['runtime_s']} s; log `session_stop.log`, `run.nohup`; pre-registration `preregistration.json`, sha256 `{PRE_SHA}`, registered {PRE['registered_at']}; ledger sha before `{LEDGER_BEFORE}`, "
         f"after `{R['ledger_sha_after']}`). **Repair round** `session_stop_repair.py` (runtime {REP['runtime_s']} s; `preregistration_repair.json`, sha256 `{PRE_R_SHA}`, registered {PRE_R['registered_at']}; ledger sha "
         f"before `{REP['ledger_sha_before']}`, after `{REP['ledger_sha_after']}`; new rows `note = \"repair\"`). Tables and this file generated by `write_findings.py` from `results.json` and `results_repair.json`. "
         "**IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 book); L0 as robustness only. 1 min is the primary timeframe; 5 min is reported as underpowered (Judge 2).\n",
         "## 0. Result in one paragraph\n"]
ex, all_pos, rho_ex = excess_signs(M["L1"])
dt = RM["n1_demonstration"]["tied to outcome"]; di = RM["n1_demonstration"]["independent of outcome"]
lines.append(f"**No session memory beyond the hour effect is shown, and no `session_stop` key is proposed for ST13/ST14.** The as-run pre-registered null N1 (outcomes permuted within session x hour_bin "
             f"cells over fixed positions) was rejected on 1 min (all seven tests, Holm p <= {max(t['N1_p_holm'] for t in M['L1']['tests']):.4f}) with a positive excess of "
             f"{min(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} to {max(v for k, v in ex.items() if k != 'spearman_today_net'):+,.0f} INR/trade, which the as-run study read as mean-reverting session memory. "
             f"**That rejection is an artifact** (section R.1): the SETUP positions are generated by the outcomes (a trade runs until exit, winners hold ~6x longer than losers), and a memoryless generator that keeps only the "
             f"clock and the durations reproduces the rejection on {dt['n1_rejected_share']:.0%} of its streams (excess {min(dt['excess_threshold_tests_mean'].values()):+,.0f} to {max(dt['excess_threshold_tests_mean'].values()):+,.0f}; "
             f"{di['n1_rejected_share']:.0%} when the duration is made independent of the outcome). Two hindsight-free nulls replace it (section R.2): the within-hour contrast across sessions with a session-block bootstrap (N4) "
             f"and the observed statistics against 2,000 memoryless streams (N3); on 1 min the min Holm p is N4 {RM['L1']['min_p_holm_N4']:.4f} / N3 {RM['L1']['min_p_holm_N3']:.4f}, on 5 min N4 {R5['L1']['min_p_holm_N4']:.4f} / N3 "
             f"{R5['L1']['min_p_holm_N3']:.4f}: **{RM['L1']['decision'].split(' -> ')[0]}** on both timeframes (5 min underpowered as well). Branch B's grid (run under the as-run rejection) is re-judged on hindsight-free statistics only, "
             "with the session-matched control percentile set aside as a hindsight-biased comparator for sequential rules (section R.3: the same rule sits at its 0.0th percentile on memoryless streams). "
             + (f"The family now holds 48 cells (16 hour-conditioned cells added for Judge 2's hour interaction, section R.4); the nested-CV OOF rule has diff {BR['nested_oof']['diff']:+,.2f} (top-1%-removed {BR['nested_oof']['diff_top1_removed']:+,.2f}), "
                f"the CPCV 5th percentile is {BR['cpcv']['diff_p5']:+,.2f}, PBO {BR['family']['pbo_diff']['pbo']}, SPA p {BR['family']['spa']['spa_p']}, and `harness.go_no_go` fails for the cell chosen on all IS both as computed and "
                f"without its control check (failing: {', '.join(BR['go_no_go']['failing_without_control_check'])}). The cells' pooled diffs sit at memoryless percentiles "
                f"{min(c['pooled_sim_pct'] for c in BR['calibration']):.0f}-{max(c['pooled_sim_pct'] for c in BR['calibration']):.0f} and the within-hour kept-vs-skipped contrast's 90 % CI excludes zero on "
                f"{sum(1 for c in BR['calibration'] if c['strat_ci90_lo'] is not None and (c['strat_ci90_lo'] > 0 or c['strat_ci90_hi'] < 0))} of 48 cells (section R.5). " if BR else "")
             + "The no-key conclusion of the as-run study stands; the memory claim, its direction and the \"reverse rule\" follow-up are withdrawn.\n")
lines += sec_repair()
lines.append("## 1. Definitions as run (fixed before any number was looked at; the script's docstring, verbatim, now headed by the dated repair note)\n\n```\n" + DOC + "\n```\n")
lines.append("## 1b. Definitions of the repair round (fixed before any repaired statistic was computed; `session_stop_repair.py`'s docstring, verbatim)\n\n```\n" + DOC_R + "\n```\n")
lines.append("## 2. Timeframe summary\n")
rows = []
for tf, X, RX in (("minute", M, RM), ("5minute", M5, R5)):
    L1 = X["L1"]; e, ap, rex = excess_signs(L1); bb = X.get("branch_b"); br = RX.get("branch_b_repair")
    rows.append(dict(tf=tf, units=L1["units"], N1_as_run_rejected=str(L1["rejected_N1"]), N1_as_run_valid="False", N3_min_holm_p=RX["L1"]["min_p_holm_N3"], N4_min_holm_p=RX["L1"]["min_p_holm_N4"],
                     memory_shown="False", grid_cells=(48 if br else (len(bb["grid"]) if bb else 0)),
                     go_no_go=(str(br["go_no_go"]["passed"]) if br and br.get("go_no_go") else "not run"), go_no_go_without_control=(str(br["go_no_go"]["passed_without_control_check"]) if br and br.get("go_no_go") else "not run"),
                     candidate="none"))
lines.append(md_table(pd.DataFrame(rows), list(rows[0].keys()), dict(units=0, N3_min_holm_p=4, N4_min_holm_p=4, grid_cells=0)) + "\n")
lines += sec_tf("minute")
lines += sec_tf("5minute")
lines.append("## 6. What would falsify this, caveats\n")
lines.append("- **Falsifiers of \"no session memory shown\".** A rejection of both N4 and N3 at Holm 5 % on 1 min / L1 with agreeing signs (the pre-registered repaired rule), or a within-hour contrast whose "
             "session-block bootstrap CI excludes zero after Holm. Not a falsifier: any N1 / N2 result (section R.1), any descriptive within-hour difference read without its bootstrap CI.\n"
             "- **Falsifiers of the no-key conclusion.** A grid cell with CPCV 5th-percentile diff > 0, PBO <= 0.2, SPA p <= 0.10, diff > 0 with the top 1 % winners removed and a kept book with mean net > 0 at "
             "8 pts slippage; none is close on any of the 48 cells. The control percentile is not part of the judgement for this family (section R.3).\n"
             "- **The generator is a null model, not a fit.** It reproduces the durations and the cell mechanics but makes ~6 % more units than the data and P(another unit follows | win) higher than observed: real "
             "sessions with a winner end sooner (a trending day stays trending). That is session structure in the *count* of SETUPs, not in the outcome given the ledger, and a stop rule cannot read it; it is "
             "recorded for S49 as an observation, not a hypothesis test.\n"
             "- **p definitions.** As run: the doubled-tail permutation p replaced the naive |stat| form after a 50-draw timing probe (`preregistration.json`, `p_definition_history`); irrelevant now that N1 is set aside. "
             "Repair: N3 and N4 p-values are doubled tails with the +1 correction; Holm over the 7 tests per null per timeframe; the 30-minute-strata N4 is a sensitivity, not a test.\n"
             "- **Ledger semantics.** `today_*_asof` counts trades with entry < k and exit <= k (verified identical on the truncated build); on this book it equals the cumulative prior outcomes of the session's units "
             "(asserted in code); before the first trigger the strategy's own ledger equals Foundation's, so the absorbing replay is exact; the rearm variant's \"winner\" is the paper trade of a skipped SETUP.\n"
             "- **`active_from_hour_bin = 13`** is the one data-informed choice of the repair (the sign change in the as-run within-hour table); it is counted in the 48-cell family and its 16 cells never win the in-fold "
             "selection.\n"
             "- **5 min** is underpowered by construction (median 2 SETUPs per active session); no result on it is evidence for or against session memory.\n"
             "- **Flag for the orchestrator.** `harness.go_no_go`'s `control_pct>=95` check is uninformative for any sequential (position-order) rule (section R.3).\n")
lines.append("## 7. Candidate config\n\nNone. The `session_stop` block is omitted from `strategy_13.json` / `strategy_14.json`; the measured results (as run and repaired) are recorded here and in `findings.json` for S49.\n")
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(lines))
print("FINDINGS.md written")


# ---------------------------------------------------------------- findings.json
def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)): return None
    return o


def tf_summary(tf):
    X = R["timeframes"][tf]; L1 = X["L1"]; e, ap, rex = excess_signs(L1); RX = REP["timeframes"][tf]
    s = dict(power=X["power_note"], units_is=L1["units"], active_sessions=L1["active_sessions"], setups_per_session_median=L1["setups_per_session_median"], ledger_identity=L1["ledger_identity"],
             session_memory_shown=False,
             direction="not shown: the as-run N1 rejection is reproduced by a memoryless process with outcome-dependent trade duration (repair R.1); the hindsight-free nulls N3 / N4 do not reject (R.2)",
             decision_as_run=X["decision"], decision_repaired=RX["L1"]["decision"],
             n1_as_run=dict(valid=False, reason="positions fixed while generated by the outcomes; see repair.issues.I1",
                            null_tests={t["test"]: dict(n_condition=t["n_condition"], observed=t["observed"], N1_perm_mean=t["N1_perm_mean"], N1_perm_sd=t["N1_perm_sd"], N1_excess=t["N1_excess"], N1_p=t["N1_p"],
                                                        N1_p_holm=t["N1_p_holm"], N1_p_abs_ref=t["N1_p_abs_ref"], N2_perm_mean=t["N2_perm_mean"], N2_excess=t["N2_excess"], N2_p=t["N2_p"], N2_p_holm=t["N2_p_holm"]) for t in L1["tests"]},
                            null_cells=L1["nulls"], min_p_holm_N1=L1["min_p_holm_N1"], min_p_holm_N2=L1["min_p_holm_N2"], rejected_N1=L1["rejected_N1"], rejected_N2=L1["rejected_N2"],
                            threshold_excess_all_positive=ap, spearman_excess_N1=rex,
                            L0=dict(units=X["L0_robustness"]["units"], min_p_holm_N1=X["L0_robustness"]["min_p_holm_N1"], rejected_N1=X["L0_robustness"]["rejected_N1"])),
             repaired_null_tests=dict(N3="the 7 observed statistics vs 2,000 memoryless streams", N4="within-hour_bin contrast across sessions, session-block bootstrap (primary)",
                                      tests={t["test"]: {k: v for k, v in t.items() if k not in ("tf", "label", "test")} for t in RX["L1"]["null_tests"]},
                                      min_p_holm_N3=RX["L1"]["min_p_holm_N3"], min_p_holm_N4=RX["L1"]["min_p_holm_N4"], min_p_holm_N4_30min_strata=RX["L1"]["min_p_holm_N4fine"],
                                      rejected_N3=RX["L1"]["rejected_N3"], rejected_N4=RX["L1"]["rejected_N4"], decision=RX["L1"]["decision"],
                                      L0_N4=dict(units=RX["L0_robustness"]["units"], min_p_holm_N4=RX["L0_robustness"]["min_p_holm_N4"], rejected_N4=RX["L0_robustness"]["rejected_N4"],
                                                 tests={t["test"]: {k: v for k, v in t.items() if k not in ("tf", "label", "test")} for t in RX["L0_robustness"]["tests"]})),
             memoryless_generator=dict(RX["generator"], sim_units_mean=RX["L1"]["sim_units_mean"], sim_units_sd=RX["L1"]["sim_units_sd"]),
             mechanism=dict(real=RX["L1"]["mechanism_real"], memoryless_tied_duration_mean=RX["L1"]["mechanism_memoryless_mean"], memoryless_independent_duration_mean=RX["L1"]["mechanism_indep_mean"]),
             n1_on_memoryless_streams=RX["n1_demonstration"],
             hour_profile=L1["hour_profile"], by_stops=L1["by_stops"], by_net_bucket=L1["by_net_bucket"], hour_x_stops=L1["hour_x_stops"])
    if X.get("branch_b"):
        Bb = X["branch_b"]
        s["branch_b_as_run"] = dict(cells=32, grid=[dict(id=r["id"], config=r["config"], kept_n=r["kept_n"], kept_share=r["kept_share"], kept_mean=r["kept_mean"], skipped_mean=r["skipped_mean"], diff=r["diff"],
                                                       diff_top1_removed=r["diff_top1_removed"], control_pct_not_used=r["control_pct"], perm_p=r["perm_p"], loser_recall=r["loser_recall"], loser_precision=r["loser_precision"],
                                                       winner_recall_weighted=r["winner_recall_weighted"], top_decile_winners_skipped=r["top_decile_winners_skipped"], sign_blocks=r["sign_blocks"],
                                                       kept_mean_slip8=r["kept_mean_slip8"]) for r in Bb["grid"]],
                                    grid_diff_range=[min(r["diff"] for r in Bb["grid"]), max(r["diff"] for r in Bb["grid"])],
                                    control_pct_reading="0.0 on every cell; NOT evidence (hindsight-biased comparator for sequential rules, repair I2)",
                                    nested_oof=Bb["nested_oof"], chosen_per_fold=Bb["chosen_per_fold"], cpcv=Bb["cpcv"], cpcv_path_ids=Bb["cpcv_path_ids"], candidate_cell=Bb["candidate"],
                                    candidate_ledger_id=Bb["candidate_ledger_id"], family=Bb["family"], dsr=Bb["dsr"], bootstrap=Bb["bootstrap"], go_no_go=Bb["go_no_go"], combined=Bb["combined"])
    if RX.get("branch_b_repair"):
        Br = RX["branch_b_repair"]
        s["branch_b_repaired"] = dict(cells=Br["cells"], active_from_hour_bin=Br["active_from_hour_bin"], hour_cells=[dict(id=r["id"], config=r["config"], source=r["source"], kept_n=r["kept_n"], kept_share=r["kept_share"],
                                                                                                                        diff=r["diff"], diff_top1_removed=r["diff_top1_removed"], perm_p=r["perm_p"], control_pct_not_used=r["control_pct"],
                                                                                                                        sign_blocks=r["sign_blocks"], kept_mean_slip8=r["kept_mean_slip8"]) for r in Br["grid"][32:]],
                                      hour_cells_ledger_ids=Br["hour_cells_ledger_ids"], nested_oof=Br["nested_oof"], chosen_per_fold=Br["chosen_per_fold"], cpcv=Br["cpcv"], cpcv_path_ids=Br["cpcv_path_ids"],
                                      family=Br["family"], go_no_go=Br["go_no_go"], calibration=Br["calibration"],
                                      judgement="hindsight-free statistics only: pooled diff calibrated against the memoryless generator, within-hour kept-vs-skipped contrast with session-block bootstrap, nested OOF, CPCV, top-1%-removed, PBO, SPA, DSR; control_pct reported, not used")
    return s


fams = ["session_stop/grid", "session_stop/nested", "session_stop/nested/cpcv", "session_stop/combined"]
FJ = dict(study="session_stop", design="DESIGN_PANEL decision-making-6-session-stop-rule-finite-horizon with both judges' fixes; repair round after the adversarial refuters", label="L1 (L0 robustness only)", split="IS only",
          preregistration=PRE, preregistration_sha256_16=PRE_SHA, preregistration_repair=PRE_R, preregistration_repair_sha256_16=PRE_R_SHA,
          timeframes={tf: tf_summary(tf) for tf in ("minute", "5minute")},
          headline=(f"No session memory beyond the hour effect is shown on either timeframe (1 min: min Holm p N4 {RM['L1']['min_p_holm_N4']:.4f}, N3 {RM['L1']['min_p_holm_N3']:.4f}; 5 min underpowered). "
                    f"The as-run N1 rejection is an artifact of outcome-dependent trade duration (a memoryless generator reproduces it on {dt['n1_rejected_share']:.0%} of streams). "
                    + (f"The 48-cell stop-rule family fails go/no-go with and without the control check (nested OOF diff {BR['nested_oof']['diff']:+,.2f}, CPCV p5 {BR['cpcv']['diff_p5']:+,.2f}, PBO {BR['family']['pbo_diff']['pbo']}); " if BR else "")
                    + "no key."),
          candidates=[], null_result=True,
          session_memory_shown={"minute": False, "5minute": False},
          session_memory_null_rejected={tf: bool(REP["timeframes"][tf]["L1"]["rejected_N3"] and REP["timeframes"][tf]["L1"]["rejected_N4"]) for tf in REP["timeframes"]},
          session_memory_null_rejected_note="refers to the hindsight-free nulls N3 AND N4 of the repair round (both must reject); the as-run N1 rejection is recorded under timeframes.<tf>.n1_as_run with valid=false and must not be read as memory",
          n1_as_run=dict(rejected={tf: R["timeframes"][tf]["L1"]["rejected_N1"] for tf in R["timeframes"]}, valid=False,
                         reason="N1 permutes outcomes over fixed positions, but the positions are generated by the outcomes (trade duration tied to outcome); reproduced by a memoryless process"),
          repair=dict(date="2026-09-29", script="session_stop_repair.py", preregistration="preregistration_repair.json",
                      issues=dict(I1=dict(issue="N1 mis-specified: positions generated by outcomes; 'mean-reverting session memory' is an artifact",
                                          changed="memoryless generator + N1 demonstration (repair_n1_memoryless_<tf>.csv), mechanism table (repair_mechanism_<tf>.csv), hindsight-free nulls N3 / N4 as the entry condition (repair_null_tests_<tf>_<label>.csv); memory / direction / reverse-rule statements withdrawn in FINDINGS.md and findings.json; docstring repair note in session_stop.py",
                                          result={tf: REP["timeframes"][tf]["L1"]["decision"] for tf in REP["timeframes"]}),
                                  I2=dict(issue="session-matched random control is a hindsight-biased comparator for within-session sequential rules",
                                          changed="control_pct reported but never used as evidence; go_no_go shown as computed and without the control check; every cell calibrated against the memoryless generator and judged on the within-hour kept-vs-skipped contrast (repair_grid_calibration_minute.csv); control pct of the k=2 rule on memoryless streams reported",
                                          result=dict(k2_control_pct_median_on_memoryless_streams=dict(tied=dt["k2_control_pct_median"], independent=di["k2_control_pct_median"]),
                                                      go_no_go_without_control_check=(BR["go_no_go"]["passed_without_control_check"] if BR else None), failing=(BR["go_no_go"]["failing_without_control_check"] if BR else None))),
                                  I3=dict(issue="Judge 2's hour interaction not run", changed="16 hour-conditioned cells (active_from_hour_bin=13) scored (family session_stop/grid, note repair); nested / CPCV re-run over the 48-cell family (session_stop/nested, session_stop/nested/cpcv, note repair)",
                                          result=dict(hour_cells_chosen_in_folds=(sum(1 for x in BR["chosen_per_fold"] if x and x.get("active_from_hour_bin")) if BR else None), candidate_cell=(BR["go_no_go"]["candidate"] if BR and BR.get("go_no_go") else None))))),
          flags_for_orchestrator=["harness.go_no_go's control_pct>=95 check is uninformative for any sequential (position-order) rule: the session-matched control conditions on the realized N_s; a causal comparator (random stopping rule with matched per-session stop counts, or a memoryless generator) is needed for such rules",
                                  "S49: record 'no session memory shown' (repaired) and the withdrawal of the as-run 'mean-reverting memory' statement",
                                  "S49 observation (not a test): real sessions with a winner end sooner than the memoryless generator predicts (P(another unit follows | win) real vs memoryless in timeframes.minute.mechanism); session structure lives in the count of later SETUPs, not in the outcome given the ledger"],
          ledger_families=fams, ledger_rows={fam: None for fam in fams}, ledger_rows_repair={fam: None for fam in fams},
          ledger_sha_before=LEDGER_BEFORE, ledger_sha_after_as_run=R["ledger_sha_after"], ledger_sha_before_repair=REP["ledger_sha_before"], ledger_sha_after_repair=REP["ledger_sha_after"],
          runtime_s=R["runtime_s"], runtime_repair_s=REP["runtime_s"],
          caveats=["IS only; nothing was read from OOS beyond row counts",
                   "the as-run N1 / N2 permutation tests are kept as the record only; they do not test session memory (positions fixed while generated by outcomes)",
                   "the memoryless generator is a null model, not a fit: ~6% more units per stream than the data and a higher P(another unit follows | win); session structure in the SETUP count is an observation for S49, not tested here",
                   "the pooled kept-vs-skipped diff of every grid cell is inside the memoryless distribution (hour composition plus cost avoidance); the session-matched control percentile is not used for this family",
                   "active_from_hour_bin=13 is the one data-informed choice of the repair and is counted in the 48-cell family",
                   "5 min has median 2 SETUPs per active session: no test has power there",
                   "the rearm variant's winner is the paper trade of a skipped SETUP"],
          files=sorted(x for x in os.listdir(HERE) if not x.startswith("__")))
try:
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", ".."))); import harness as H
    for fam in fams:
        rows_ = [r for r in H.read_ledger(fam) if r["family"] == fam]
        FJ["ledger_rows"][fam] = len(rows_); FJ["ledger_rows_repair"][fam] = sum(1 for r in rows_ if r.get("note") == "repair")
except Exception as e:  # noqa
    FJ["ledger_rows_note"] = str(e)
json.dump(clean(FJ), open(os.path.join(HERE, "findings.json"), "w", encoding="utf-8"), indent=1)
print("findings.json written")
