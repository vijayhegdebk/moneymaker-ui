"""Compose FINDINGS.md and findings.json of the H2 / H3 / H4 study from the scripts' outputs (CSV / JSON in this folder).
Every number in the markdown is read from those files or from the ledger; nothing is computed here except table formatting and
the claim restatements, which quote the rows they use and apply the fixed verdict rule written in `gate_verdict()`.

Repair round (after the adversarial refuters): the ledger families are read from the ledger itself; the post-hoc min-skip
blocks, captions and T1 row appear only when the post-hoc summary of that table exists; section 3 is H2-specific and quotes
the measured kept shares; the H4 episode definition states the cut-window rule; section 6 lists each refuted issue and what
changed; the header says whether every run had finished when the file was written.

    python write_findings.py
"""
import os, sys, json, glob, collections, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import h234_common as C
import harness as H

TFS, LABELS, STUDIES = ("minute", "5minute"), ("L1", "L0"), ("h2", "h3", "h4")
TFN = {"minute": "1 min", "5minute": "5 min"}
J = lambda name: json.load(open(os.path.join(HERE, name), encoding="utf-8")) if os.path.exists(os.path.join(HERE, name)) else None
R = lambda name: pd.read_csv(os.path.join(HERE, name)) if os.path.exists(os.path.join(HERE, name)) else None


def fmt(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return ""
    if isinstance(v, (bool, np.bool_)): return str(bool(v))
    if isinstance(v, (int, np.integer)): return f"{v:,}"
    if isinstance(v, (float, np.floating)): return f"{v:,.4g}" if abs(v) < 1 else f"{v:,.2f}" if abs(v) < 1e5 else f"{v:,.0f}"
    return str(v)


def md(df, cols=None, maxrows=60):
    df = df if cols is None else df[[c for c in cols if c in df.columns]]
    df = df.head(maxrows)
    head = "| " + " | ".join(str(c) for c in df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "".join("| " + " | ".join(fmt(v) for v in r) + " |\n" for r in df.itertuples(index=False))


GRID_SHOW = ["cell", "id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall", "loser_precision",
             "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks", "go_raw"]
NESTED_SHOW = ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall", "loser_precision",
               "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks"]
CELL = lambda c: json.dumps(c, sort_keys=True) if c else "none eligible"


def family_row(f, cp, g=None):
    """One row of the family table from a family_stats dict `f`, a cpcv dist `cp` and (optionally) the go/no-go dict `g`."""
    g = g or f["go_no_go_nested"]
    return dict(candidates=f["candidates"], ledger_rows=f["ledger_rows"], effective_trials=f["effective_trials"], pbo_diff=f["pbo_diff"]["pbo"], pbo_kept_mean=f["pbo_kept_mean"]["pbo"],
                spa_p=f["spa"]["spa_p"], rc_p=f["spa"]["rc_p"], spa_p_unstud=f["spa"].get("spa_p_unstudentised"), spa_best=json.dumps(f["spa_best_config"]), spa_best_mean_gain=f["spa"]["best_mean_gain"],
                nested_boot_diff_ci90=str(f["bootstrap_nested"]["diff_ci"]), nested_boot_p_diff_le0=f["bootstrap_nested"]["diff_p_le0"], nested_dsr_p=f["dsr_nested"].get("p"),
                cpcv_diff_median=cp["diff_median"], cpcv_diff_p5=cp["diff_p5"], cpcv_share_pos=cp["diff_share_positive"], cpcv_control_median=cp.get("control_pct_median"),
                go_no_go=g["passed"], failed=", ".join(k for k, v in g["checks"].items() if not v[0]))


def nested_block(S, study, tag, suffix=""):
    n = S["nested"]; ch = n["chosen_per_block"]
    t = pd.DataFrame([{k: n.get(k) for k in NESTED_SHOW}])
    blocks = pd.DataFrame([dict(block=c["block"], chosen=CELL(c["cell"]), thr=c.get("thr"), train_diff=c.get("train_diff"), train_kept_share=c.get("train_kept_share"), eligible=c["eligible"],
                                test_n=c["test_n"], test_kept=c.get("test_kept")) for c in ch])
    cp = R(f"{study}_{tag}_cpcv_paths{suffix}.csv")
    fam = f"{study}/nested_cv{suffix}"
    s = f"**Nested-CV candidate** (family `{fam}`, the 12-block OOF mask{'; ledger note `repair`' if suffix else ''}):\n\n" + md(t) + "\nChosen cell per training fold:\n\n" + md(blocks)
    if cp is not None:
        s += f"\nCPCV paths (`{fam}/cpcv`, 11 rows): diff median {fmt(S['cpcv']['diff_median'])}, 5th pct {fmt(S['cpcv']['diff_p5'])}, min {fmt(S['cpcv']['diff_min'])}, share > 0 {fmt(S['cpcv']['diff_share_positive'])}, control pct median {fmt(S['cpcv'].get('control_pct_median'))} / 5th pct {fmt(S['cpcv'].get('control_pct_p5'))}\n\n" + md(cp)
        cc = pd.Series([CELL(c["cell"]) for c in S["cpcv_chosen"]]).value_counts()
        s += "\nCells chosen across the 66 CPCV training sets: " + "; ".join(f"{k} x{v}" for k, v in cc.items()) + "\n"
    return s


def grid_summary(S, G):
    return (f"{S['grid_cells']} cells; diff > 0 in {S['grid_diff_pos']}; control pct >= 95 in {S['grid_pct_ge95']}; passing every raw go/no-go check "
            f"(kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in {S['grid_cells_go_raw']}. Median cell diff {fmt(G['diff'].median())}, median control pct {fmt(G['control_pct'].median())}.")


def gate_verdict(row):
    """The fixed reading of one ledger row: 'passes' = every raw go/no-go check (harness.go_no_go without family stats) true."""
    return "passes the raw go/no-go checks" if bool(row.get("go_raw")) else "fails the raw go/no-go checks"


def ledger_state():
    """Integrity counts and the families actually present, from the ledger itself."""
    p = os.path.join(H.LEDGER, "trials.jsonl"); n_bad = 0; ids = []
    for line in open(p, encoding="utf-8"):
        if not line.strip(): continue
        try: ids.append(json.loads(line)["id"])
        except Exception: n_bad += 1
    missing = [i for i in set(ids) if not os.path.exists(os.path.join(H.LEDGER, "vectors", f"{i}_IS.npz"))]
    fam = [r for r in H.read_ledger() if r["family"].split("/")[0] in STUDIES]
    per = collections.Counter((r["family"], r["tf"], r["label"]) for r in fam)
    return dict(lines=len(ids), unparseable=n_bad, missing_vectors=len(missing), study_rows=len(fam), study_ids=len(set(r["id"] for r in fam)),
                repair_rows=sum(1 for r in fam if r.get("note") == "repair"), families=sorted({r["family"] for r in fam}),
                rows_per_family=[dict(family=k[0], tf=k[1], label=k[2], rows=v) for k, v in sorted(per.items())],
                splits=sorted({r["split"] for r in fam}))


def selection_table():
    """What the pre-registered nested-CV selection chose on every table, from the summary JSONs (the refuters' section-3 point)."""
    rows = []
    for study in STUDIES:
        for tf in TFS:
            for label in LABELS:
                S = J(f"{study}_{tf}_{label}_summary.json")
                if S is None: continue
                n = S["nested"]; ch = [c for c in n["chosen_per_block"] if c.get("cell")]
                ks = [c["train_kept_share"] for c in ch]
                folds = collections.Counter(CELL(c["cell"]) for c in n["chosen_per_block"]).most_common(1)[0]
                cp = collections.Counter(CELL(c["cell"]) for c in S["cpcv_chosen"]).most_common(1)[0]
                tiny = {CELL(c["cell"]) for c in ch if c["train_kept_share"] > 0.99}          # cells that skipped < 1 % of the training rows
                rows.append(dict(study=study, tf=TFN[tf], label=label, n_is=S["n_is"], oof_kept_n=n["kept_n"], oof_skipped_n=S["n_is"] - n["kept_n"], oof_skipped_share=round(1 - n["kept_share"], 4),
                                 oof_skipped_mean=n["skipped_mean"], fold_skip_share_min=round(1 - max(ks), 4) if ks else None, fold_skip_share_max=round(1 - min(ks), 4) if ks else None,
                                 blocks_nothing_skipped=sum(1 for c in n["chosen_per_block"] if c.get("test_kept") == c["test_n"]),
                                 folds_skip_lt1pct=sum(1 for c in ch if c["train_kept_share"] > 0.99), cpcv_sets_on_those_cells=sum(1 for c in S["cpcv_chosen"] if CELL(c["cell"]) in tiny),
                                 tiny_cells=", ".join(sorted(tiny)) if tiny else "", modal_cell_12_folds=f"{folds[0]} x{folds[1]}", modal_cell_66_cpcv=f"{cp[0]} x{cp[1]}"))
    return pd.DataFrame(rows)


def build():
    parts = []; claims = {}
    posthoc_any = bool(glob.glob(os.path.join(HERE, "posthoc_h*_summary.json")))
    F = dict(study="h2_h3_h4", question="BRIEF H2 (sideways = CHoCH without break), H3 (visibly high volume), H4 (levels respected or broken) through the harness",
             split="IS only (SETUP date <= 2025-12-31)", labels={"primary": "L1 (15:25 intraday book)", "robustness": "L0 (engine uncut trade)"},
             timeframes={tf: {} for tf in TFS}, candidates=[], ledger_families=[], caveats=[], falsifiers=[], files=[], posthoc_minskip_run=posthoc_any)
    parts.append("# Tables (auto-generated by `write_findings.py` from the CSV / JSON outputs)\n")
    t1 = ("## T1. Definitions (fixed before the numbers)\n\n"
          "| term | definition |\n|---|---|\n"
          "| unit | a harness row: a Foundation SETUP taken under the label's book, `harness.load(tf, label)`, IS rows only (1 min L1 4,452 / L0 4,502; 5 min L1 826 / L0 832) |\n"
          "| cell | one gate configuration = one ledger row scored on IS by `harness.score` (2,000 control draws, 2,000 permutations). A cell with a learned threshold (the H2 range quantiles) is scored on its 12-block out-of-fold mask: the threshold is the quantile of the *training fold's* rows (`harness.purged_splits`), applied to the test block; the fold thresholds are in the ledger row's `note` and in `h2_<tf>_<label>_grid.csv` |\n"
          "| nested CV | inside each of the 12 purged training folds every cell is fitted and evaluated on the training rows with `harness.metrics` (controls off); the cell with the largest kept-vs-skipped diff subject to the harness kept floors (kept share >= 20 %, kept n >= 300 (1 min) / 80 (5 min) scaled by train / IS) is applied to the test block; the 12 test blocks form the OOF mask, one ledger row `<study>/nested_cv`; the same selection inside the 66 CPCV training sets gives the 11 paths (`<study>/nested_cv/cpcv`, `harness.score_paths`, controls on) |\n")
    if posthoc_any:
        t1 += "| post-hoc variant | `<study>/nested_cv_minskip` (+ `/cpcv`): the same selection with skipped share >= 10 % added to the fold eligibility, declared after the primary rows were read, run in the repair round (ledger note `repair`), one more counted trial per family. The pre-registered row's family statistics are also recomputed over the completed family (`family_prereg_recomputed` in `posthoc_<study>_<tf>_<label>_summary.json`) |\n"
    t1 += ("| family | every non-cpcv ledger row of the study on that timeframe and label; PBO (`harness.pbo`, CSCV 16 blocks, 12,870 partitions, statistic diff and kept_mean), SPA / Reality Check (`harness.spa`, 2,000 stationary-bootstrap draws; studentised p, and the unstudentised p where the harness version at run time reported it), effective trials (participation ratio of the kept-net correlation matrix), block bootstrap 90 % CI and DSR of the nested-CV row, `harness.go_no_go` on it |\n"
           "| bucket table | descriptive decomposition of the label by an as-of categorical: n, share, sum, mean, se (iid), median, win rate, mean pts, stop share, blocks below (of the 12 IS blocks, how many have the bucket mean below the block's all-rows mean). No rule is chosen on a bucket table; tercile edges are pooled IS quantiles, recorded |\n"
           "| H2 columns | `n_choch_since_bos` (CHoCHs after the last BOS, own CHoCH included; >= 2 = the user's 'CHoCH, CHoCH, no BOS'), `n_choch_since_bos_today`, `alt_dir6` / `alt_kind6` (direction / kind changes among the last 6 events), `range_{1h,3h,since_choch}_atr` (same-session range / atr14), `er_1h` (Kaufman efficiency ratio, last hour), `hour_bin` |\n"
           "| H2 grid | choch rule: skip when `n_choch_since_bos[_today] >= kc`, kc in {2,3,4}, scope all / today; range rule: skip when `range_W_atr <= r`, W in {1h, 3h, since_choch}, r = training-fold quantile q in {0.1 .. 0.5}; both rules combined by OR / AND; or one rule alone. 6 + 15 + 180 = 201 cells (families `h2/choch`, `h2/range`, `h2/both`) |\n"
           "| H3 high-volume bar | volume >= v x median of the previous N bars of the same session (at least 5), v in {2,3,4}, N in {20,60}; never a non-front-month / zero-volume bar. Bar direction = sign(close - open). The N = 20 / 60 medians and ratios are recomputed and asserted equal to `bars.vol_med20_prior` / `vol_ratio20` / `vol_ratio60` |\n"
           "| H3 aftermath (labels of the bar, IS bars) | fwd_n = sg x (close[j+n] - close[j]) for n in {5,15,30} (pts and / atr14[j]); mfe30 / mae30 = best / worst excursion in the bar's direction over j+1..j+30 (/ atr14); high_held_n / low_held_n = the bar's high / low not exceeded over j+1..j+n (n = 15, 30); own_extreme_held = the extreme in the bar's direction held (no continuation), opp_extreme_held = the other extreme held (respect). Every window inside the session and complete. Baseline = every IS bar with a defined ratio and a non-flat direction |\n"
           "| H3 per SETUP (as-of) | for each (v, N): the latest high-volume bar j <= k of the session (the SETUP bar counts); for M in {5,15,30}: agree (k - j <= M and same direction), disagree (opposite), none (no such bar within M or a flat bar). Re-run on the truncated build (`trunc_20250630_120000`) and identical for every SETUP before the cut; (v=2,N=20) and (v=3,N=20) equal the build's `hv2_*` / `hv3_*` |\n"
           "| H3 grid | per (v, N, M): skip_if_disagree, skip_if_none, take_only_agree (= skip disagree and none): 54 cells, family `h3/gate` |\n"
           "| H4 touch verdict (as-of, the build's columns) | `touch_{prot,room,swing}_last`: touch episodes of the protected level / nearest room edge / nearest confirmed swing in the hour before k (a bar touches when low <= L <= high, consecutive touching bars = one episode); the last episode's verdict inside 15 minutes after it, never past k: broke (a close beyond by > 0.5 x atr14 on the far side), held, pending (window open at k), none, na. `touch_*_n` = episodes in the hour |\n"
           "| H4 grid | skip when `touch_<level>_last == broke / held / pending`, level in {prot, room, swing}: 9 cells, family `h4/touch_gate` |\n"
           "| H4 episode study (IS bars, labels of the level) | level instances: protected level = a maximal run of bars with the same `bars.prot`; room edge = lo and hi of every ST7/ST8 room over birth_bar <= i < retired_bar; swing = `swings.price` from conf_bar to the first close beyond it by > 0.5 x atr14 or its session's end. Same touch / episode / side rule as the build; verdict window = 15 minutes (15 bars on 1 min, 3 on 5 min) after the last touch bar, inside its session. **A window cut by the session end is `session_end` whatever happened inside it** (`broke` and `held` are verdicts of a full window only); a break close inside a cut window is counted separately as `cut_break` (never `broke`, no aftermath, not a break for the retest bookkeeping). Aftermath from the verdict bar v (the breaking close, or the window end for held): move_n = sg x (close[v+n] - close[v]) / atr14[v], n in {15,30,60}, sg = break direction (broke) or bounce direction away from the level (held); mfe_n the best excursion that way; beyond_n = sg x (close[v+n] - L) / atr14[v] (broke only). Baseline = abs(close[i+n] - close[i]) / atr14[i] over every IS bar. prior_held = held episodes of the same instance before this one; P(broke given prior_held) over broke + held episodes not after a break |\n")
    parts.append(t1)
    for study, title in (("h2", "H2 - sideways = CHoCH without break"), ("h3", "H3 - visibly high volume"), ("h4", "H4 - levels respected or broken")):
        parts.append(f"\n## T{dict(h2=2, h3=3, h4=4)[study]}. {title}\n")
        if study == "h3":
            for tf in TFS:
                am = R(f"h3_{tf}_bar_aftermath.csv")
                if am is None: continue
                parts.append(f"### {TFN[tf]}: reaction after a high-volume bar (IS bars; `h3_{tf}_bar_aftermath.csv`)\n\n" +
                             md(am[am.set != "hv_flat_count"], ["set", "v", "N", "dir", "n", "fwd5_atr_mean", "fwd15_atr_mean", "fwd30_atr_mean", "fwd30_atr_median", "fwd30_pos_share", "fwd30_abs_atr_mean",
                                                                "mfe30_atr_median", "mae30_atr_median", "own_extreme_held_15", "own_extreme_held_30", "opp_extreme_held_15", "opp_extreme_held_30"]) +
                             "\nFlat high-volume bars (excluded from the direction rows): " + ", ".join(f"v{int(r.v)} N{int(r.N)}: {int(r.n)}" for r in am[am.set == "hv_flat_count"].itertuples()) + "\n")
                F["timeframes"][tf]["h3_bar_aftermath"] = am.to_dict("records")
                claims.setdefault("volume_bars", {})[tf] = am[(am.dir == "both") & (am.set != "hv_flat_count")][["set", "v", "N", "n", "fwd30_atr_mean", "fwd30_atr_median", "fwd30_pos_share", "fwd30_abs_atr_mean", "mfe30_atr_median", "mae30_atr_median", "own_extreme_held_15", "opp_extreme_held_15", "opp_extreme_held_30"]].to_dict("records")
        if study == "h4":
            for tf in TFS:
                ES = J(f"h4_summary_{tf}.json")
                if ES is None or f"{tf}/episodes" not in ES: continue
                E = ES[f"{tf}/episodes"]
                rep = E.get("repair")
                parts.append(f"### {TFN[tf]}: the episode study (IS bars; `h4_{tf}_episodes.parquet`, {E['episodes']:,} episodes of {sum(E['instances'].values()):,} level instances: {E['instances']})\n\n"
                             + (f"Repair round ({rep['at']}): {rep['what']}. Cut windows: {E.get('cut_windows', 0):,} (`session_end`), of which {E.get('cut_windows_with_break_close', 0):,} held a break close inside the truncated window (`cut_break_n` below).\n\n" if rep else "")
                             + f"Verdicts (`h4_{tf}_episode_verdicts.csv`):\n\n" + md(pd.DataFrame(E["verdicts"])) +
                             f"\nP(broke given prior held episodes of the same level), episodes not after a break (`h4_{tf}_p_break_by_prior_held.csv`):\n\n" + md(pd.DataFrame(E["p_break_by_prior_held"])) +
                             f"\nMove after a confirmed break vs after a respect, in ATR (`h4_{tf}_aftermath.csv`; `move` is signed in the break / bounce direction, `abs` is its magnitude, the baseline is every IS bar):\n\n" +
                             md(pd.DataFrame(E["aftermath"]), ["kind", "verdict", "n_bars", "n", "abs_mean", "abs_median", "abs_p75", "abs_p90", "abs_share_gt1", "abs_share_gt2", "move_mean", "move_median", "move_share_pos", "move_share_gt1", "move_share_gt2", "mfe_median", "beyond_median", "beyond_share_pos"]) +
                             f"\nRetests (held episodes) before the first break, per level instance that broke (`h4_{tf}_retests_before_break.csv`):\n\n" + md(pd.DataFrame(E["retests_before_break"])) +
                             f"\nHeld episodes followed by another touch of the same level instance (`h4_{tf}_held_then_retested.csv`):\n\n" + md(pd.DataFrame(E["held_then_retested"])) + "\n")
                F["timeframes"][tf]["h4_episodes"] = {k: E.get(k) for k in ("instances", "episodes", "verdicts", "cut_windows", "cut_windows_with_break_close", "p_break_by_prior_held", "aftermath", "retests_before_break", "held_then_retested", "repair")}
                claims.setdefault("levels_episodes", {})[tf] = dict(p_break=E["p_break_by_prior_held"], aftermath=[r for r in E["aftermath"] if r["n_bars"] in (30, 60)])
        fam_rows = []
        for tf in TFS:
            for label in LABELS:
                tag = f"{tf}_{label}"
                S = J(f"{study}_{tag}_summary.json")
                if S is None: continue
                G = R(f"{study}_{tag}_grid.csv")
                sec = f"### {TFN[tf]} / {label} ({S['n_is']:,} IS units)\n\n"
                if study == "h2":
                    B = R(f"h2_{tag}_buckets.csv")
                    if label == "L1":
                        for var in ("n_choch_since_bos", "n_choch_since_bos_today", "alt_dir6", "alt_kind6", "range_1h_atr_tercile", "range_3h_atr_tercile", "range_since_choch_atr_tercile", "er_1h_tercile", "hour_bin"):
                            sec += f"by `{var}`:\n\n" + md(B[B.variable == var], ["bucket", "n", "share", "net_mean", "net_se", "net_median", "win_rate", "pts_mean", "stop_share", "blocks_below_block_mean"]) + "\n"
                        X = R(f"h2_{tag}_x_nchoch_hour.csv")
                        order = ["<09:25", "09", "10", "11", "12", "13", "14", "15", ">=15:20"]
                        piv = X.pivot(index="hour_bin", columns="n_choch_since_bos", values="net_mean").reindex(order).reset_index()
                        pn = X.pivot(index="hour_bin", columns="n_choch_since_bos", values="n").reindex(order).reset_index()
                        sec += "two-way `n_choch_since_bos` x `hour_bin`, mean net (n in the second table):\n\n" + md(piv) + "\n" + md(pn) + "\n"
                    else:
                        sec += "L0 robustness, by `n_choch_since_bos` and `n_choch_since_bos_today`:\n\n" + md(B[B.variable.isin(["n_choch_since_bos", "n_choch_since_bos_today"])], ["variable", "bucket", "n", "net_mean", "net_se", "win_rate", "blocks_below_block_mean"]) + "\n"
                    claims.setdefault("sideways", {})[tag] = dict(all_mean=S["all_mean"], buckets=B[B.variable == "n_choch_since_bos"][["bucket", "n", "net_mean", "net_se", "win_rate"]].to_dict("records"),
                                                                    kc2_all=G[(G.rule == "choch") & (G.kc == 2) & (G.scope == "all")][GRID_SHOW].to_dict("records")[0],
                                                                    kc2_today=G[(G.rule == "choch") & (G.kc == 2) & (G.scope == "today")][GRID_SHOW].to_dict("records")[0])
                    sec += "The grid: " + grid_summary(S, G) + f" Full table `h2_{tag}_grid.csv`. The six choch-only cells and the 15 range-only cells:\n\n" + md(G[G.rule != "both"], ["kc", "scope", "W", "q"] + GRID_SHOW[1:]) + "\nTop 10 cells by IS diff (selection is by nested CV, never by this table):\n\n" + md(G.sort_values("diff", ascending=False).head(10), GRID_SHOW) + "\n"
                if study == "h3":
                    B = R(f"h3_{tag}_by_agreement.csv")
                    if label == "L1":
                        sec += f"Foundation outcome by direction agreement with the latest high-volume bar within M bars (`h3_{tag}_by_agreement.csv`; every (v, N, M)):\n\n" + md(B, ["variable", "bucket", "n", "share", "net_mean", "net_se", "win_rate", "pts_mean", "blocks_below_block_mean"], 200) + "\n"
                        BS = R(f"h3_{tag}_by_bars_since.csv")
                        sec += f"by bars since the latest high-volume bar (`h3_{tag}_by_bars_since.csv`):\n\n" + md(BS, ["variable", "bucket", "n", "share", "net_mean", "net_se", "win_rate", "blocks_below_block_mean"], 200) + "\n"
                    else:
                        sec += "L0 robustness, (v=2, N=20) and (v=3, N=20), M = 15:\n\n" + md(B[B.variable.isin(["hv v2 N20 M15", "hv v3 N20 M15"])], ["variable", "bucket", "n", "net_mean", "net_se", "win_rate", "blocks_below_block_mean"]) + "\n"
                    claims.setdefault("volume", {})[tag] = dict(by_agreement=B[B.variable.isin(["hv v2 N20 M15", "hv v3 N20 M15"])][["variable", "bucket", "n", "net_mean", "net_se", "win_rate"]].to_dict("records"),
                                                                cells_v2_N20_M15=G[(G.v == 2) & (G.N == 20) & (G.M == 15)][["gate"] + GRID_SHOW[1:]].to_dict("records"))
                    sec += "The grid: " + grid_summary(S, G) + f" Full table `h3_{tag}_grid.csv`:\n\n" + md(G, ["v", "N", "M", "gate"] + GRID_SHOW[1:], 60) + "\n"
                if study == "h4":
                    B = R(f"h4_{tag}_by_touch.csv")
                    sec += (f"Foundation outcome by the last touch verdict and by the number of touch episodes in the hour before the SETUP (`h4_{tag}_by_touch.csv`):\n\n" if label == "L1" else "L0 robustness:\n\n") + \
                           md(B, ["variable", "bucket", "n", "share", "net_mean", "net_se", "net_median", "win_rate", "pts_mean", "stop_share", "blocks_below_block_mean"], 60) + "\n"
                    claims.setdefault("levels", {})[tag] = dict(by_verdict=B[B.variable.str.endswith("_last")][["variable", "bucket", "n", "net_mean", "net_se", "win_rate"]].to_dict("records"),
                                                                grid=G[["level", "skip_when_last"] + GRID_SHOW[1:]].to_dict("records"))
                    sec += f"The 9 gate cells (`h4_{tag}_grid.csv`):\n\n" + md(G, ["level", "skip_when_last"] + GRID_SHOW[1:]) + "\n"
                sec += nested_block(S, study, tag)
                fr = dict(tf=TFN[tf], label=label, variant="pre-registered (family as at the primary run)", **family_row(S["family"], S["cpcv"])); fam_rows.append(fr)
                P = J(f"posthoc_{study}_{tag}_summary.json")
                if P is not None:
                    sec += "\n" + nested_block(P, study, tag, "_minskip")
                    fam_rows.append(dict(tf=TFN[tf], label=label, variant="post-hoc min skip 10 % (family complete)", **family_row(P["family"], P["cpcv"])))
                    if P.get("family_prereg_recomputed"):
                        fam_rows.append(dict(tf=TFN[tf], label=label, variant="pre-registered (family recomputed after the post-hoc rows)", **family_row(P["family_prereg_recomputed"], S["cpcv"])))
                    cap = "\nFamily on this table (every non-cpcv ledger row of the study, tf and label). The pre-registered row's statistics as computed at its run (before the post-hoc rows existed) and recomputed over the completed family; the post-hoc row's over the completed family:\n\n"
                else:
                    cap = "\nFamily on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):\n\n"
                sec += cap + md(pd.DataFrame([r for r in fam_rows if r["tf"] == TFN[tf] and r["label"] == label])) + "\n"
                parts.append(sec)
                rec = dict(n_is=S["n_is"], grid=dict(cells=S["grid_cells"], diff_pos=S["grid_diff_pos"], control_ge95=S["grid_pct_ge95"], go_raw=S["grid_cells_go_raw"], top10_by_diff=S.get("top10_by_diff", S.get("grid"))),
                           nested={k: v for k, v in S["nested"].items() if k != "chosen_per_block"}, nested_chosen=[c["cell"] for c in S["nested"]["chosen_per_block"]], cpcv=S["cpcv"],
                           family=family_row(S["family"], S["cpcv"]), go_no_go_checks=S["family"]["go_no_go_nested"]["checks"])
                if P is not None:
                    rec["posthoc_minskip"] = dict(ledger_note=P.get("ledger_note"), nested={k: v for k, v in P["nested"].items() if k != "chosen_per_block"}, nested_chosen=[c["cell"] for c in P["nested"]["chosen_per_block"]], cpcv=P["cpcv"],
                                                  family=family_row(P["family"], P["cpcv"]), go_no_go_checks=P["family"]["go_no_go_nested"]["checks"])
                    if P.get("family_prereg_recomputed"):
                        rec["family_prereg_recomputed"] = family_row(P["family_prereg_recomputed"], S["cpcv"]); rec["go_no_go_checks_prereg_recomputed"] = P["family_prereg_recomputed"]["go_no_go_nested"]["checks"]
                F["timeframes"][tf].setdefault(study, {})[label] = rec
                for name, X, famd in (("pre-registered", S, S["family"]), ("post-hoc min skip 10 %", P, P["family"] if P else None), ("pre-registered, family recomputed", S, P.get("family_prereg_recomputed") if P else None)):
                    if X is not None and famd is not None and famd["go_no_go_nested"]["passed"]:
                        F["candidates"].append(dict(study=study, tf=tf, label=label, variant=name, ledger_id=X["nested"]["id"], chosen=[c["cell"] for c in X["nested"]["chosen_per_block"]]))
        parts.append(f"### {study.upper()} family summary (all tables)\n\n" + md(pd.DataFrame(fam_rows)) + "\n")
    L = ledger_state(); F["ledger_integrity"] = L
    F["ledger_families"] = L["families"]
    F["claims_measured"] = claims
    F["null_result"] = len(F["candidates"]) == 0
    F["files"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "*")) if not os.path.isdir(p))
    return parts, F, claims


# ---------------------------------------------------------------- the narrative (numbers pulled from the same files)
def claims_section(F, claims):
    s = ["## 2. The user's claims, restated as measured (IS, L1 unless stated)\n"]
    # sideways
    s.append("### 2.1 \"CHoCH, CHoCH, no BOS = sideways; trades in sideways are hurting\"\n")
    rows = []
    for tag, c in claims["sideways"].items():
        for b in c["buckets"]: rows.append(dict(table=tag, n_choch_since_bos=b["bucket"], n=b["n"], net_mean=b["net_mean"], net_se=b["net_se"], win_rate=b["win_rate"], all_rows_mean=c["all_mean"]))
    s.append("Foundation mean net by `n_choch_since_bos` (the user's sideways = 2 and above):\n\n" + md(pd.DataFrame(rows)))
    rows = []
    for tag, c in claims["sideways"].items():
        for name, r in (("skip when n_choch_since_bos >= 2", c["kc2_all"]), ("skip when n_choch_since_bos_today >= 2", c["kc2_today"])):
            rows.append(dict(table=tag, gate=name, id=r["id"], kept_n=r["kept_n"], skipped_mean=r["skipped_mean"], kept_mean=r["kept_mean"], diff=r["diff"], control_pct=r["control_pct"], perm_p=r["perm_p"], sign_blocks=r["sign_blocks"], loser_precision=r["loser_precision"], winner_recall_weighted=r["winner_recall_weighted"], verdict=gate_verdict(r)))
    s.append("\nThe pre-registered gate cells that encode the claim (ledger rows):\n\n" + md(pd.DataFrame(rows)))
    # volume
    s.append("\n### 2.2 \"Check how price reacts in visibly high volume\"\n")
    rows = []
    for tf, recs in claims["volume_bars"].items():
        for r in recs: rows.append(dict(tf=TFN[tf], **r))
    s.append("Bars (IS), direction rows pooled (`dir = both`): the 30-bar move in the bar's own direction, its magnitude, the excursions, and whether the bar's extremes held for 15 / 30 bars; the baseline is every bar:\n\n" +
             md(pd.DataFrame(rows), ["tf", "set", "v", "N", "n", "fwd30_atr_mean", "fwd30_atr_median", "fwd30_pos_share", "fwd30_abs_atr_mean", "mfe30_atr_median", "mae30_atr_median", "own_extreme_held_15", "opp_extreme_held_15", "opp_extreme_held_30"]))
    rows = []
    for tag, c in claims["volume"].items():
        for b in c["by_agreement"]: rows.append(dict(table=tag, **b))
    s.append("\nFoundation SETUPs within 15 bars after a high-volume bar (v = 2 and 3, N = 20), by direction agreement:\n\n" + md(pd.DataFrame(rows)))
    rows = []
    for tag, c in claims["volume"].items():
        for r in c["cells_v2_N20_M15"]: rows.append(dict(table=tag, gate=r["gate"], id=r["id"], kept_n=r["kept_n"], diff=r["diff"], control_pct=r["control_pct"], perm_p=r["perm_p"], sign_blocks=r["sign_blocks"], verdict=gate_verdict(r)))
    s.append("\nThe (v=2, N=20, M=15) gate cells:\n\n" + md(pd.DataFrame(rows)))
    # levels
    s.append("\n### 2.3 \"Those levels will be respected: if it breaks there will be a large move, else price retests, retests and respects\"\n")
    rows = []
    for tf, c in claims["levels_episodes"].items():
        for r in c["aftermath"]: rows.append(dict(tf=TFN[tf], kind=r["kind"], verdict=r["verdict"], n_bars=r["n_bars"], n=r["n"], abs_median=r["abs_median"], abs_mean=r["abs_mean"], abs_share_gt2=r["abs_share_gt2"], move_median=r.get("move_median"), move_share_pos=r.get("move_share_pos"), beyond_share_pos=r.get("beyond_share_pos")))
    s.append("Move after a confirmed break vs after a respect vs any bar (ATR; `move` signed in the break / bounce direction; full 15-minute verdict windows only, see T1):\n\n" + md(pd.DataFrame(rows), maxrows=80))
    rows = []
    for tf, c in claims["levels_episodes"].items():
        for r in c["p_break"]: rows.append(dict(tf=TFN[tf], **r))
    s.append("\nP(the touch breaks the level) by the number of earlier respects of the same level instance:\n\n" + md(pd.DataFrame(rows)))
    rows = []
    for tag, c in claims["levels"].items():
        if not tag.endswith("L1"): continue
        for b in c["by_verdict"]: rows.append(dict(table=tag, **b))
    s.append("\nFoundation SETUPs by the last touch verdict of the protected level / room edge / swing in the hour before the SETUP (L1):\n\n" + md(pd.DataFrame(rows), maxrows=40))
    rows = []
    for tag, c in claims["levels"].items():
        for r in c["grid"]: rows.append(dict(table=tag, level=r["level"], skip_when_last=r["skip_when_last"], id=r["id"], kept_n=r["kept_n"], diff=r["diff"], control_pct=r["control_pct"], perm_p=r["perm_p"], sign_blocks=r["sign_blocks"], verdict=gate_verdict(r)))
    s.append("\nThe 9 touch-verdict gate cells per table:\n\n" + md(pd.DataFrame(rows), maxrows=40))
    return "\n".join(s)


def expected_outputs():
    exp = [f"{s}_{tf}_{l}_summary.json" for s in STUDIES for tf in TFS for l in LABELS] + [f"h2_summary_{tf}.json" for tf in TFS] + [f"h3_summary_{tf}.json" for tf in TFS] + [f"h4_summary_{tf}.json" for tf in TFS]
    exp += [f"posthoc_{s}_{tf}_{l}_summary.json" for s in STUDIES for tf in TFS for l in LABELS]
    return [e for e in exp if not os.path.exists(os.path.join(HERE, e))]


def repair_section(F, sel):
    L = F["ledger_integrity"]
    h4 = {tf: F["timeframes"][tf].get("h4_episodes") for tf in TFS}
    cut_txt = ", ".join("%s: %s of %s cut windows" % (TFN[tf], fmt(h4[tf]["cut_windows_with_break_close"]), fmt(h4[tf]["cut_windows"])) for tf in TFS if h4.get(tf) and h4[tf].get("cut_windows") is not None)
    s = ["## 6. Repair round (after the adversarial refuters)\n",
         "The refuters confirmed four material issues in the first version of this folder (written 04:17 while three 1-min runs were still appending). Each, and what changed:\n",
         "1. **The post-hoc min-skip variant was reported but never run.** `posthoc_minskip.py` had no log, no summary and no ledger rows, yet FINDINGS.md counted it in the family multiplicity and asserted its null result. "
         f"Fix: the script was given CLI arguments and run to completion in the repair round (`posthoc_minskip.log`, `run_posthoc_*.nohup`); its {L['repair_rows']} ledger rows carry `note = \"repair\"` (12 tables x (1 nested row + 11 CPCV paths)). "
         "It also recomputes the pre-registered nested row's family statistics over the completed family (`family_prereg_recomputed`), shown as a third row of every family table. `write_findings.py` now reads the ledger families from the ledger "
         f"(`ledger_families` = {len(L['families'])} families actually present) and emits the post-hoc T1 row, blocks and captions only where a post-hoc summary exists.\n",
         "2. **Section 3 overstated the degenerate selection.** It said the pre-registered criterion picked a handful-of-rows skip cell on every table and that 5 min H4 skipped 3 rows in most CPCV training sets. "
         "Measured (section 3 table): only 5 min H2 is degenerate (2 rows skipped in every fold, L1 and L0); 5 min H3 chose cells skipping 2-7 %, 5 min H4 chose {room, held} (about 7 %) in 11 of 12 folds and 50 of 66 CPCV sets (L1) and in all of them (L0); "
         "{prot, broke} (3 rows) was chosen in 1 of 12 folds and 11 of 66 CPCV sets on 5 min L1. Section 3 and the `posthoc_minskip.py` docstring were rewritten from those numbers.\n",
         "3. **H4 episode verdict did not match its definition.** The docstring and T1 said a verdict window cut by the session end is `session_end`, but the code returned `broke` whenever a break close fell inside the truncated window (and `held` was impossible there), a small upward bias in P(broke) for late touches. "
         f"Fix: every cut window is `session_end`; a break close inside it is recorded as `cut_break` and counted separately ({cut_txt}); "
         "`prior_held` / `after_break` follow the verdicts. The episode tables of both timeframes were regenerated by `h4_levels.py --part episodes` (no ledger row is involved: these are labels of the level, not gate inputs); the gate cells (`touch_*` build columns) are unchanged. "
         "First-run counts for reference (from `h4_levels.log`): 5 min broke prot 515 / room 16,011 / swing 11,388; 1 min 4,646 / 49,127 / 115,620.\n",
         f"4. **The header presented a mid-run ledger snapshot as final and the 1-min gate results were missing.** This file is regenerated after every run finished ({'no expected output is missing' if not F['missing_outputs'] else 'STILL MISSING: ' + ', '.join(F['missing_outputs'])}); "
         "all 1-min tables (H2 / H3 / H4 grids, nested CV, CPCV, families) are in sections 1 and T2-T4.\n",
         "Also in this round: the pre-registered summaries' family SPA was computed with `harness.spa` as at the primary runs (before its 05:05 revision: exclusion of near-inactive candidates from the studentised statistic, unstudentised p added); "
         "the post-hoc and recomputed family rows use the revised function, so their `spa_p` can differ from the primary row's for that reason alone. Nothing in the pre-registered rows was re-scored; the ledger is append-only.\n"]
    return "\n".join(s)


def narrative(F, claims, sel):
    L = F["ledger_integrity"]; cand = F["candidates"]; posthoc = F["posthoc_minskip_run"]
    logs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "*.log")) + glob.glob(os.path.join(HERE, "*.nohup")))
    status = "every run had finished when this file was written" if not F["missing_outputs"] else "INTERIM: outputs still missing: " + ", ".join(F["missing_outputs"])
    head = ("# H2 / H3 / H4: sideways, visibly high volume, levels respected or broken (IS only, through the harness)\n\n"
            "Study folder `fz_v3/out/studies/h2_h3_h4/`. Scripts: `h2_regime.py`, `h3_volume.py`, `h4_levels.py` on the shared `h234_common.py`; `posthoc_minskip.py` "
            "(one declared post-hoc selection variant, section 3" + ("" if posthoc else "; NOT RUN") + "); `write_findings.py` (this file: sections 1-6 followed by the auto-generated tables T1-T4). Logs: " + ", ".join(f"`{x}`" for x in logs) +
            ". Every number is IS only (SETUP date <= 2025-12-31) and is a harness ledger row (id given) or a row of a CSV / JSON in this folder; the definitions (table T1) were fixed in the scripts' docstrings before any number was read "
            "(the H4 cut-window rule was made to match its definition in the repair round, section 6). Machine-readable: `findings.json`. "
            f"Written {F['written_at']}; {status}. Ledger at that moment: sha `{F['ledger_sha']}`, {L['lines']} rows ({L['study_rows']} of families h2/h3/h4, {L['study_ids']} distinct ids, {L['repair_rows']} with note `repair`, split {L['splits']}), "
            f"{L['unparseable']} unparseable lines, {L['missing_vectors']} rows without a per-session vector. Families present: {', '.join(f'`{x}`' for x in L['families'])}.\n")
    s1 = ["## 1. Result\n"]
    if not cand:
        s1.append("**Null result.** No cell family of H2, H3 or H4 produced a candidate that passes `harness.go_no_go` on either timeframe, on L1 or on L0, under the pre-registered nested-CV selection" +
                  (", under the post-hoc minimum-skip variant, or when the pre-registered row is judged against the completed family" if posthoc else "") + ". No candidate config JSON is written. The tables that carry the result:\n")
    else:
        s1.append("Candidates passing `harness.go_no_go`:\n\n" + md(pd.DataFrame(cand)) + "\n")
    rows = []
    for tf in TFS:
        for study in STUDIES:
            for label in LABELS:
                r = F["timeframes"][tf].get(study, {}).get(label)
                if r is None: continue
                for var, x in (("pre-registered", r), ("post-hoc min skip 10 %", r.get("posthoc_minskip"))):
                    if x is None: continue
                    n = x["nested"]; f = x["family"]
                    rows.append(dict(study=study, tf=TFN[tf], label=label, selection=var, ledger_id=n["id"], kept_share=n["kept_share"], diff=n["diff"], control_pct=n["control_pct"], perm_p=n["perm_p"], sign_blocks=n["sign_blocks"],
                                     cpcv_diff_p5=f["cpcv_diff_p5"], cpcv_share_pos=f["cpcv_share_pos"], pbo_diff=f["pbo_diff"], spa_p=f["spa_p"], dsr_p=f["nested_dsr_p"], boot_ci90=f["nested_boot_diff_ci90"], go=f["go_no_go"], failed=f["failed"]))
                    if var == "pre-registered" and r.get("family_prereg_recomputed"):
                        f2 = r["family_prereg_recomputed"]
                        rows.append(dict(study=study, tf=TFN[tf], label=label, selection="pre-registered, family recomputed", ledger_id=n["id"], kept_share=n["kept_share"], diff=n["diff"], control_pct=n["control_pct"], perm_p=n["perm_p"], sign_blocks=n["sign_blocks"],
                                         cpcv_diff_p5=f2["cpcv_diff_p5"], cpcv_share_pos=f2["cpcv_share_pos"], pbo_diff=f2["pbo_diff"], spa_p=f2["spa_p"], dsr_p=f2["nested_dsr_p"], boot_ci90=f2["nested_boot_diff_ci90"], go=f2["go_no_go"], failed=f2["failed"]))
    s1.append(md(pd.DataFrame(rows), maxrows=60))
    g = []
    for tf in TFS:
        for study in STUDIES:
            for label in LABELS:
                r = F["timeframes"][tf].get(study, {}).get(label)
                if r: g.append(dict(study=study, tf=TFN[tf], label=label, cells=r["grid"]["cells"], diff_pos=r["grid"]["diff_pos"], control_ge95=r["grid"]["control_ge95"], cells_passing_raw_checks=r["grid"]["go_raw"]))
    s1.append("\nThe grids themselves: how many cells have a positive diff, a control percentile >= 95, and how many pass every raw go/no-go check at once (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks >= 8, control >= 95):\n\n" + md(pd.DataFrame(g)))
    # section 3 from the selection table
    h2_5 = sel[(sel.study == "h2") & (sel.tf == "5 min")]
    others = sel[~((sel.study == "h2") & (sel.tf == "5 min"))]
    pct = lambda x: f"{100 * x:.1f} %"
    rng = {st: (others[others.study == st].fold_skip_share_min.min(), others[others.study == st].fold_skip_share_max.max()) for st in STUDIES if (others.study == st).any()}
    tiny_rows = others[others.folds_skip_lt1pct > 0]
    tiny_txt = ("; the only other folds that chose a cell skipping under 1 % of the training rows: " + "; ".join(f"{r.study.upper()} {r.tf} {r.label}: {r.folds_skip_lt1pct} of 12 folds and {r.cpcv_sets_on_those_cells} of 66 CPCV sets on {r.tiny_cells}" for r in tiny_rows.itertuples())
                if len(tiny_rows) else "; no other fold chose a cell skipping under 1 % of the training rows")
    s3 = ("\n## 3. Selection note (what the pre-registered nested-CV selection chose, and why a post-hoc variant exists)\n\n"
          "The pre-registered criterion (largest training-fold kept-vs-skipped diff subject to the harness *kept* floors) has no floor on the skipped set. What it chose on every table, from the summary JSONs "
          "(`oof_*` = the 12-block OOF mask; `fold_skip_share` = 1 - the chosen cell's kept share on the training rows, over the 12 folds; `blocks_nothing_skipped` = test blocks where the chosen cell kept every row; "
          "`folds_skip_lt1pct` = folds whose chosen cell skipped under 1 % of the training rows, `cpcv_sets_on_those_cells` = CPCV training sets that chose one of those cells):\n\n" + md(sel) +
          "\nThe degeneracy is specific to **5 min H2**: " + "; ".join(f"{r.label}: the cell {r.modal_cell_12_folds.split(' x')[0]} won all 12 folds (and {r.modal_cell_66_cpcv.split(' x')[1]} of 66 CPCV training sets), skipping {r.oof_skipped_n} of {r.n_is:,} rows (skipped mean {fmt(r.oof_skipped_mean)}) with nothing skipped in {r.blocks_nothing_skipped} of 12 test blocks" for r in h2_5.itertuples()) +
          ". A two-row skip set has an unbounded diff, and the harness go/no-go is what catches it (sign blocks 2 of 12, control percentile below 95, PBO, DSR). On every other table the chosen cells skip a real share of the training rows (fold skip share " +
          "; ".join(f"{st.upper()} {pct(rng[st][0])} to {pct(rng[st][1])}" for st in rng) + tiny_txt + "). " +
          ("`posthoc_minskip.py` re-runs the identical selection with `skipped share >= 10 %` added to the fold eligibility, declared after the primary rows were read, run in the repair round (note `repair`) and counted as one more trial per family; "
           "its rows and the pre-registered row's recomputed family statistics are in the family tables of T2-T4. Nothing was chosen on the pooled OOF in either variant.\n" if posthoc else
           "`posthoc_minskip.py` (the same selection with `skipped share >= 10 %` added to the fold eligibility) has not been run; no claim about it is made in this file.\n"))
    s4 = ("\n## 4. What would falsify these findings\n\n"
          "- H2: a `h2/choch` or `h2/range` ledger row with diff > 0, control percentile >= 95, sign blocks >= 8 and a CPCV 5th-percentile diff > 0 under the nested-CV selection; or the bucket "
          "`n_choch_since_bos >= 2` showing a mean net below the other buckets by more than two standard errors on both timeframes and both labels.\n"
          "- H3: a `h3/gate` row skipping >= 10 % of the SETUPs with diff > 0 at control percentile >= 95 in the nested-CV paths; or a bar aftermath table where the 30-bar move in the "
          "high-volume bar's direction differs from the baseline by more than 0.5 ATR.\n"
          "- H4: a `h4/touch_gate` row with control percentile >= 95, sign blocks >= 8 and a positive CPCV 5th percentile; or an episode table where the absolute 30 / 60-bar move after a "
          "confirmed break exceeds the baseline by more than 0.5 ATR, or P(broke given prior_held >= 2) is lower than P(broke given prior_held = 0) by more than 0.2 on both timeframes with "
          "a positive Foundation expectancy at respected levels.\n"
          "- Any of the above on a rebuild with a different `features.parquet` (the SETUP counts and the frozen kept set are pinned by `data/<tf>/meta.json`).\n")
    s5 = ("\n## 5. Caveats\n\n"
          "- Bucket tables and the episode / bar-aftermath tables are descriptive decompositions (means, counts, iid standard errors, block sign counts). No p-value is attached to them; "
          "every question that needs one is a ledger row, and the kept-vs-skipped statistics of the 201 + 54 + 9 cells (plus the nested-CV rows) are the only kept-vs-skipped numbers in this study.\n"
          "- The session-matched control percentile and the pooled diff disagree in sign on many cells (e.g. the 5 min `range_3h` cells: negative diff, control percentile 100). The control "
          "matches per-session kept counts, the diff pools all rows; a gate that skips whole sessions of the 5 min book (median two SETUPs per session) is matched trivially there. Both are reported; neither alone is the criterion.\n"
          "- Under the harness `score`, a cell with a learned quantile is one ledger row on its OOF mask; its 12 fold thresholds differ by a few hundredths of an ATR (recorded in the grid CSV).\n"
          "- L0 (the engine's uncut trade) is a robustness label only; on 1 min it runs to 70 sessions and its purge is coarser.\n"
          "- The episode study's `prot` level instances are short on both timeframes (the engine moves the protected level at each swing update), so a protected level almost never sees a "
          "second episode: its retest counts are structural zeros, not evidence.\n"
          "- The 1 min swing instances end at the first break or at their session's end by definition, so P(broke given prior_held = 0) on 1 min counts the many swings that break on their first touch shortly after confirmation.\n"
          "- Episode verdicts need a full 15-minute window: touches in the last 15 minutes of a session are `session_end` (a break close inside that truncated window is counted as `cut_break`, not as `broke`), so the "
          "verdict tables describe touches up to 15 minutes before the close; the build's as-of `touch_*_last` columns (the gate inputs) are a different object with their own `pending` state and are unchanged.\n"
          "- The recomputed volume baselines equal the build's `vol_med20_prior` / `vol_ratio20` / `vol_ratio60` exactly; the new per-SETUP H3 features equal the build's `hv2_*` / `hv3_*` "
          "(N = 20) and are identical on the truncated build for every SETUP before the cut (`trunc_20250630_120000`); the H4 episode features are labels of the level, never features.\n"
          "- The ledger was appended by several processes in parallel (the primary runs, the repair-round post-hoc runs and other studies); the integrity counts are in the header (every line parses, every id has its vector file).\n"
          "- On 5 min the `range_*_atr` terciles and quantiles use 12 / 36-bar windows; hour-of-day effects and the range rule are entangled (a session's range grows through the day).\n"
          "- The pre-registered summaries' family SPA used `harness.spa` as at the primary runs; the post-hoc and recomputed rows use the 05:05 revision (section 6).\n")
    return head + "\n".join(s1) + "\n" + claims_section(F, claims) + s3 + s4 + s5 + "\n" + repair_section(F, sel)


if __name__ == "__main__":
    parts, F, claims = build()
    F["ledger_sha"] = H.ledger_sha(); F["written_at"] = time.strftime("%Y-%m-%d %H:%M:%S"); F["missing_outputs"] = expected_outputs()
    sel = selection_table(); F["selection_table"] = sel.to_dict("records")
    text = narrative(F, claims, sel)
    F["caveats"] = [l[2:] for l in text.split("## 5. Caveats\n\n")[1].split("\n## 6.")[0].strip().split("\n") if l.startswith("- ")]
    F["falsifiers"] = [l[2:] for l in text.split("## 4. What would falsify these findings\n\n")[1].split("\n## 5.")[0].strip().split("\n") if l.startswith("- ")]
    F["repair"] = [l for l in text.split("## 6. Repair round (after the adversarial refuters)\n")[1].strip().split("\n") if l[:2] in ("1.", "2.", "3.", "4.") or l.startswith("Also")]
    F["selection_note"] = ("pre-registered nested-CV (max train diff s.t. kept floors) is degenerate on 5 min H2 only (2 rows skipped); the post-hoc min-skip-10% variant "
                           + ("was run in the repair round (note 'repair') and counted as one more trial per family" if F["posthoc_minskip_run"] else "has NOT been run"))
    C.jdump(F, os.path.join(HERE, "findings.json"))
    open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write(text + "\n\n---\n\n" + "\n".join(parts))
    open(os.path.join(HERE, "TABLES.md"), "w", encoding="utf-8").write("\n".join(parts))
    print("written FINDINGS.md, TABLES.md, findings.json; candidates:", F["candidates"], "null:", F["null_result"], "missing:", F["missing_outputs"], "ledger:", {k: F["ledger_integrity"][k] for k in ("lines", "study_rows", "repair_rows", "unparseable", "missing_vectors")})
