"""Write FINDINGS.md and findings.json of operating_point_sizing from results_<tf>.json (operating_point.py) and sizing_verdict.json
(sizing_verdict.py). Every number in the tables is read from those files; the kept-vs-skipped numbers carry their ledger id."""
import os, sys, json, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402  file_sha, read_ledger only
import operating_point as OP                                            # noqa: E402  the docstring (definitions) and constants

TFS = ["minute", "5minute"]
f2 = lambda x: "-" if x is None else (f"{x:,.2f}" if isinstance(x, (int, float)) else str(x))
f4 = lambda x: "-" if x is None else (f"{x:.4f}" if isinstance(x, (int, float)) else str(x))
f1 = lambda x: "-" if x is None else (f"{x:.1f}" if isinstance(x, (int, float)) else str(x))
ID = lambda r: f"`{r['id']}`"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows: out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def main():
    R = {tf: json.load(open(os.path.join(HERE, f"results_{tf}.json"), encoding="utf-8")) for tf in TFS}
    SZ = json.load(open(os.path.join(HERE, "sizing_verdict.json"), encoding="utf-8"))
    shas = {f: H.file_sha(os.path.join(HERE, f)) for f in ("operating_point.py", "sizing_verdict.py", "write_findings.py")}
    L = []
    L.append("# operating_point_sizing: FINDINGS (the merged operating-point step + the conditional sizing step; IS only)\n")
    L.append(f"Generated {D.datetime.now().isoformat(timespec='seconds')} by `write_findings.py` from `results_minute.json`, `results_5minute.json` (`operating_point.py`, "
             f"logs `run_minute.log`, `run_5minute.log`) and `sizing_verdict.json` (`sizing_verdict.py`, `sizing_verdict.log`). Script shas {shas}. "
             "DESIGN_PANEL: quant-ml-canon-conformal-skip + decision-making-4-selective-gate-conformal-risk-control (Judge 2's merge into ONE operating-point step; "
             "both judges' caveats binding) and quant-ml-canon-bet-sizing + decision-making-5-kelly-bounded-sizing (merged; conditional on a passed gate). "
             "**IS only** (SETUP date <= 2025-12-31); label **L1**; both timeframes. Every kept-vs-skipped number below is a harness ledger row (id given); "
             "kept-only statistics (selective risk, coverage, utilities, the uncapped-brokerage mean) are computed from the same keep mask as the row and carry its id.\n")
    L.append("## 0. Result in one paragraph\n")
    m, m5 = R["minute"], R["5minute"]
    fam, fam5 = m["family"], m5["family"]
    L.append(f"**This step adds no OOS candidate and none is written.** It re-parameterises the OOF scores of the gate_family sub-family finalists (a threshold on a score "
             f"another study produced is not a gate: Judge 1), and gate_family itself wrote no candidate on either timeframe, so every kept book here is a re-parameterisation "
             f"of a gate that already failed `harness.go_no_go`. **minute**: {fam['rows']} ledger rows (family `operating_point/*`; PBO(diff) {fam['pbo_diff']['pbo']}, "
             f"SPA p {fam['spa'].get('spa_p')}, effective trials {fam['effective_trials']}); the best controlled row by diff is {fam['best_row']['family']} "
             f"{ {k: fam['best_row']['config'][k] for k in ('sub', 'model', 'alpha') if k in fam['best_row']['config']} } with diff {f2(fam['best_row']['diff'])}, control percentile "
             f"{fam['best_row']['control_pct']}, kept mean at 8 pts slippage {f2(fam['best_row']['kept_mean_slip8'])}, go/no-go FAIL "
             f"({sum(1 for v in fam['best_row']['go_no_go']['checks'].values() if not v[0])} items). **5minute**: {fam5['rows']} rows (PBO(diff) {fam5['pbo_diff']['pbo']}, "
             f"SPA p {fam5['spa'].get('spa_p')}, effective trials {fam5['effective_trials']}); best controlled row {fam5['best_row']['family']} "
             f"{ {k: fam5['best_row']['config'][k] for k in ('sub', 'model', 'alpha') if k in fam5['best_row']['config']} } diff {f2(fam5['best_row']['diff'])}, control percentile "
             f"{fam5['best_row']['control_pct']}, kept mean at 8 pts {f2(fam5['best_row']['kept_mean_slip8'])}, go/no-go FAIL "
             f"({sum(1 for v in fam5['best_row']['go_no_go']['checks'].values() if not v[0])} items). The conformal winner-coverage guarantee holds on the pooled OOF at every alpha "
             f"within the CV+ band (1 - 2 alpha) on both timeframes, and it costs nothing to state because the book it certifies is negative at every coverage: of the "
             f"{sum(R[tf]['models'][k]['cost_sensitivity']['kept_books'] for tf in TFS for k in R[tf]['models'])} kept books evaluated (both timeframes, four scored models each), "
             f"{sum(R[tf]['models'][k]['cost_sensitivity']['books_with_kept_mean_slip8_gt_0'] for tf in TFS for k in R[tf]['models'])} have a kept mean > 0 at 8 pts slippage "
             f"(the harness item) and {sum(R[tf]['models'][k]['cost_sensitivity']['books_with_kept_mean_slip3_gt_0'] for tf in TFS for k in R[tf]['models'])} at 3 pts. "
             f"The session-unit CRC certificate on the last 200 active IS sessions does not transfer to the earlier IS rows (realised clipped risk before the block is 1.3-4x the "
             f"certificate on every model: the exchangeability failure Judge 1 predicted, here already inside IS). The cost-aware Pareto front is presented for the user (Rule 0(c)); "
             f"at w = 0 its optimum is the smallest coverage on every model because every kept book is negative. **Sizing: not run: no gate passed** (both timeframes; "
             f"`sizing_verdict.json`); the design's default verdict 'lots = 1 or skip' stands.\n")
    L.append("## 1. Definitions (fixed before the numbers; `operating_point.py` docstring verbatim)\n")
    L.append("```\n" + OP.__doc__.strip() + "\n```\n")
    L.append(f"Constants: alphas {OP.ALPHAS}; ACI gammas {OP.GAMMAS}, burn-in {OP.ACI_BURN_IN} winners; coverage grid {OP.COVERAGES[0]}..{OP.COVERAGES[-1]} step 0.05; "
             f"CRC lambda grid 0.05..1.00 step 0.05, alphas {OP.CRC_ALPHAS} INR, calibration {OP.CRC_SESSIONS} sessions, clip B {OP.CLIP_B}; w grid {OP.W_GRID}; "
             f"time bins {[b for b, _, _ in OP.BINS]}; scored models {OP.MODELS}.\n")
    L.append("## 2. Inputs: the scored models of `oof_<tf>.parquet`\n")
    rows = []
    for tf in TFS:
        for k, M in R[tf]["models"].items():
            ps = M["p_summary"]
            rows.append([tf, k, M["role"], M["vocabulary"], f4(ps["auc_oof"]), f"{f4(ps['min'])} / {f4(ps['p50'])} / {f4(ps['max'])}", f4(M["gate_family_nested"]["kept_share"]), M["source_columns_n"]])
    L.append(table(["tf", "sub/model", "role", "vocabulary", "OOF AUC", "p min / median / max", "gate_family nested kept share", "source columns"], rows) + "\n")
    L.append("The policy trees (pt1-pt3; the 5minute sub-family (I) finalist `pt2`) and the H5 rule list carry no score (their OOF column is a boolean keep), so they cannot be "
             "thresholded and are not in this step; on 5minute the sub-family (I) probability learner is `context/hgbc`. The scorecard's p is a per-fold Platt map of an integer "
             "score: its OOF scale differs by fold and has heavy ties (visible as flat stretches of the coverage curve).\n")
    for tf in TFS:
        Rt = R[tf]; meta = Rt["meta"]
        L.append(f"## {3 if tf == 'minute' else 4}. {tf} (L1: IS units {meta['is_units']}, mean {f2(meta['all_mean'])} INR/trade, win rate {meta['win_rate']}, winners {meta['winners']}, "
                 f"active sessions {meta['active_sessions']}, mean cost {f2(meta['mean_cost'])}; uncapped brokerage adds {f2(meta['mean_cost_uncapped_delta'])} per trade; "
                 f"winners per time bin {meta['winners_per_bin']})\n")
        for k, M in Rt["models"].items():
            L.append(f"### {tf} / {k} - {M['role']} - {M['vocabulary']}\n")
            L.append("#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)\n")
            rows = []
            for c in M["conformal"]:
                r = c["ledger"]
                rows.append([c["alpha"], f2(c["nominal_coverage"]), f2(c["cv_plus_coverage"]), f4(c["winner_coverage"]), f4(c["winner_coverage_weighted"]),
                             f"{f4(c['coverage_per_fold_min'])} / {f4(c['coverage_per_fold_max'])}", f"{c['folds_below_nominal']} / {c['folds_below_cv_plus']}", f4(r["kept_share"]),
                             f2(r["kept_mean"]), f2(r["skipped_mean"]), f2(r["diff"]), f2(r["diff_top1_removed"]), f4(r["perm_p"]), f1(r["control_pct"]), f4(r["loser_recall"]),
                             f4(r["top_decile_winners_skipped"]), r["sign_blocks"], f2(r["kept_mean_slip3"]), f2(r["kept_mean_slip8"]), f2(c["kept_mean_uncapped"]),
                             f4(c["agreement_with_gate_family_nested"]), ID(r)])
            L.append(table(["alpha", "nominal 1-a", "CV+ 1-2a", "OOF winner coverage", "|net|-wtd coverage", "per-fold min / max", "folds < nominal / < CV+", "kept share", "kept mean",
                            "skipped mean", "diff", "diff top1% off", "perm p", "control pct", "loser recall", "top-decile winners skipped", "sign blocks", "kept mean slip3",
                            "kept mean slip8", "kept mean uncapped brokerage", "agreement w/ gate_family nested", "ledger id"], rows) + "\n")
            ar = M["conformal_alpha_rule"]
            L.append(f"Pre-registered alpha rule of the conformal design ('{ar['rule']}'): feasible alphas {ar['feasible_alphas']}; chosen **{ar['chosen']}**"
                     + (" (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9)." if ar["chosen"] == 0.05 else
                        (" - no alpha satisfies both constraints." if ar["chosen"] is None else ".")) + "\n")
            L.append("Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):\n")
            c10 = next(c for c in M["conformal"] if c["alpha"] == 0.1)
            L.append(table(["fold", "cal winners", "q", "n", "winners", "kept share", "winner coverage", "|net|-wtd coverage", "loser recall"],
                           [[f["fold"], f["n_cal_winners"], f4(f["q"]), f["n"], f["winners"], f4(f["kept_share"]), f4(f["winner_coverage"]), f4(f["winner_coverage_weighted"]), f4(f["loser_recall"])] for f in c10["folds"]]) + "\n")
            if "conformal_timebin" in M:
                L.append("#### (1b) Class x time-bin taxonomy (minute only; the taxonomy reads the SETUP clock)\n")
                rows = []
                for c in M["conformal_timebin"]:
                    r = c["ledger"]; b = c["bins"]
                    rows.append([c["alpha"], f2(c["cv_plus_coverage"]), f4(c["winner_coverage"]), f4(c["winner_coverage_weighted"])]
                                + [f"{f4(b[n]['winner_coverage'])} ({b[n]['min_cal_winners']})" for n, _, _ in OP.BINS]
                                + [f4(r["kept_share"]), f2(r["diff"]), f4(r["perm_p"]), f1(r["control_pct"]), f4(r["loser_recall"]), f2(r["kept_mean_slip8"]), ID(r)])
                L.append(table(["alpha", "CV+ 1-2a", "OOF winner coverage", "|net|-wtd"] + [f"coverage {n} (min cal winners)" for n, _, _ in OP.BINS]
                               + ["kept share", "diff", "perm p", "control pct", "loser recall", "kept mean slip8", "ledger id"], rows) + "\n")
            L.append("#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)\n")
            rows = []
            for c in M["aci"]:
                r = c["ledger"]; fs = c["final_state"]
                rows.append([c["gamma"], c["alpha"], c["burn_in_rows"], c["winners_updated"], f4(c["winner_coverage"]), f4(c["winner_coverage_after_burn_in"]), f4(c["winner_coverage_last_quarter"]),
                             f"{f4(c['alpha_path_min'])} / {f4(c['alpha_path_max'])}", f4(fs["alpha_T"]), fs["q_T"], f4(fs["skip_if_p_below"]), f4(r["kept_share"]), f2(r["diff"]), f4(r["perm_p"]),
                             f1(r["control_pct"]), f4(r["loser_recall"]), r["sign_blocks"], f2(r["kept_mean_slip8"]), ID(r)])
            L.append(table(["gamma", "alpha", "burn-in rows", "winners updated", "winner coverage (all)", "after burn-in", "last quarter", "alpha_t min / max", "alpha_T", "q_T",
                            "skip if p <", "kept share", "diff", "perm p", "control pct", "loser recall", "sign blocks", "kept mean slip8", "ledger id"], rows) + "\n")
            L.append("#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net\n")
            rows = []
            for c in M["coverage_curve"]:
                r = c["ledger"]
                rows.append([c["coverage"], f4(c["realised_coverage"]), f2(c["selective_risk"]), f4(c["loser_share_kept"]), f4(c["winner_net_retained"]), f4(c["loser_net_avoided"]),
                             f2(r["kept_net"]), f2(c["skipped_winner_net"]), f2(c["U_w0.0"]), f2(c["U_w0.5"]), f2(c["U_w1.0"]), f2(r["kept_mean"]), f2(r["diff"]), f2(r["kept_mean_slip8"]),
                             f2(c["kept_mean_uncapped"]), "yes" if c["pareto_efficient"] else "", ID(r)])
            L.append(table(["coverage c", "realised", "selective risk (clipped 6000)", "loser share kept", "winner-net retained", "loser-net avoided", "kept net", "skipped winner net",
                            "U w=0", "U w=0.5", "U w=1", "kept mean", "diff", "kept mean slip8", "kept mean uncapped", "Pareto-efficient", "ledger id"], rows) + "\n")
            am = M["pareto_argmax_coverage_by_w"]
            L.append(f"Argmax coverage of U_w on the grid: w = 0 -> {am['w0.0']}, w = 0.5 -> {am['w0.5']}, w = 1 -> {am['w1.0']}. Presented for the user to pick w and the coverage "
                     "(Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, "
                     "coverage 0, is not on the grid and would be the true argmax).\n")
            L.append("#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)\n")
            crc = M["crc"]
            L.append(table(["coverage lambda", "threshold s", "kept share (block)", "R_hat (block)", "certificate (n R_hat + B)/(n+1)", "sessions with a kept unit"],
                           [[x["coverage_lambda"], f4(x["threshold"]), f4(x["kept_share_block"]), f2(x["R_hat"]), f2(x["certificate"]), x["sessions_with_kept"]] for x in crc["table"]]) + "\n")
            rows = []
            for x in crc["chosen"]:
                if "ledger" not in x: rows.append([x["alpha"], "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", x.get("note")]); continue
                r = x["ledger"]
                rows.append([x["alpha"], x["coverage_lambda"], f4(x["threshold"]), f2(x["certificate"]), f2(x["realised_risk_before_block"]), f4(x["kept_share_before_block"]), f2(x["realised_risk_all_is"]),
                             f4(r["kept_share"]), f2(r["diff"]), f1(r["control_pct"]), f2(r["kept_mean_slip8"]), ID(r)])
            L.append(table(["alpha (INR)", "lambda*", "threshold s", "certificate", "realised risk before the block", "kept share before the block", "realised risk all IS", "kept share IS",
                            "diff", "control pct", "kept mean slip8", "ledger id"], rows) + "\n")
            if "crc_timebin" in M:
                L.append("Per-bin certificates (minute only):\n")
                rows = []
                for x in M["crc_timebin"]["chosen"]:
                    b = x["bins"]; r = x.get("ledger")
                    rows.append([x["alpha"]] + [(f"{b[n]['coverage_lambda']} (cert {f2(b[n]['certificate'])}; n {M['crc_timebin']['bins'][n]['n_sessions_with_setup']}, slack {f2(M['crc_timebin']['bins'][n]['slack'])})" if b.get(n) else "-") for n, _, _ in OP.BINS]
                                + ([f2(x["realised_risk_before_block"]), f4(r["kept_share"]), f2(r["diff"]), f1(r["control_pct"]), f2(r["kept_mean_slip8"]), ID(r)] if r else ["-"] * 6))
                L.append(table(["alpha (INR)"] + [f"lambda* {n}" for n, _, _ in OP.BINS] + ["realised risk before the block", "kept share IS", "diff", "control pct", "kept mean slip8", "ledger id"], rows) + "\n")
            cs = M["cost_sensitivity"]
            L.append(f"#### (5) Cost sensitivity of every kept book of this model: {cs['kept_books']} books; kept mean > 0 at 8 pts slippage: **{cs['books_with_kept_mean_slip8_gt_0']}** "
                     f"(best {f2(cs['best_kept_mean_slip8'])}); at 3 pts: {cs['books_with_kept_mean_slip3_gt_0']} (best {f2(cs['best_kept_mean_slip3'])}); with uncapped 0.03% brokerage "
                     f"(+{f2(cs['uncapped_minus_capped_mean_delta'])} INR/trade): best kept mean {f2(cs['best_kept_mean_uncapped'])}. The kept-vs-skipped difference is slippage-invariant "
                     "(every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.\n")
        # family
        fam = Rt["family"]; br = fam["best_row"]
        L.append(f"### {tf} family multiplicity (every `operating_point/*` ledger row of the timeframe with a defined diff)\n")
        L.append(table(["rows", "by family", "PBO (diff)", "IS-best below zero OOS", "PBO (kept mean)", "SPA p (studentised)", "RC p", "best mean gain / session (t)", "excluded from studentised",
                        "SPA p (unstudentised)", "effective trials"],
                       [[fam["rows"], fam["rows_by_family"], fam["pbo_diff"]["pbo"], fam["pbo_diff"]["oos_best_below_zero"], fam["pbo_kept_mean"]["pbo"], fam["spa"].get("spa_p"), fam["spa"].get("rc_p"),
                         f"{fam['spa'].get('best_mean_gain')} ({fam['spa'].get('best_t')})", fam["spa"].get("excluded_from_studentised"), fam["spa"].get("spa_p_unstudentised"), fam["effective_trials"]]]) + "\n")
        L.append(f"Best controlled row by diff: {br['family']} `{br['id']}` config {br['config']}: diff {f2(br['diff'])}, control pct {br['control_pct']}, kept share {br['kept_share']}, "
                 f"kept mean slip8 {f2(br['kept_mean_slip8'])}, bootstrap 90% CI of diff {br['boot']['diff_ci']}, DSR p {br['dsr'].get('p')} (n_trials {br['dsr'].get('n_trials')}); "
                 f"`harness.go_no_go` **{'PASS' if br['go_no_go']['passed'] else 'FAIL'}**:\n")
        L.append(table(["item", "ok", "value"], [[k, "yes" if v[0] else "no", (v[1] if not isinstance(v[1], list) or len(v[1]) <= 3 else f"{len(v[1])} columns")] for k, v in br["go_no_go"]["checks"].items()]) + "\n")
        L.append(f"### {tf} candidate: **none** (this step adds no candidate by design; the null-tape item reads 'not run' for that reason)\n")
    L.append("## 5. Sizing (conditional step): **not run: no gate passed**\n")
    for tf in TFS:
        s = SZ["timeframes"][tf]
        L.append(f"- **{tf}**: verdict **{s['verdict']}**. Candidate files for the timeframe in `OUT/candidates/`: {s['candidate_files']} (folder exists: {SZ['candidates_folder_exists']}); "
                 f"gate_family candidate: {s['gate_family_candidate']}. {s['detail']}")
    L.append("\nNothing of the sizing design was fitted (no Platt calibration, reliability curve, Brier skill, ECE, payoff quintiles, AFML 10.3 comparison, half-Kelly bins, expected-net "
             "bins, lot-aware random control or block bootstrap), because every one of those numbers would size a book whose gated edge is not shown to exist; the design's default "
             "verdict 'lots = 1 or skip' is recorded and no 'size' block is output.\n")
    L.append("## 6. What would falsify these findings\n")
    L.append("- A scored gate_family model whose conformal or coverage-chosen kept book has a kept mean > 0 at 8 pts slippage AND a session-matched control percentile >= 95 AND a "
             "positive bootstrap 90% CI of the diff: none of the kept books here has any of the three on either timeframe (see the per-model tables).\n"
             "- A CRC certificate that transfers: realised clipped risk on the IS rows before the calibration block within the certificate at the chosen lambda; here it is 1.3-4x above it on every model.\n"
             "- A gate_family candidate in `OUT/candidates/` with a passed go/no-go: the sizing step then runs as designed (Platt, payoff quintiles, expected-net bins, lot-aware control, CPCV 5th percentile of the net-per-lot improvement).\n")
    caveats = [
        "The conformal guarantee is the cross-conformal / CV+ form (about 1 - 2 alpha): the calibration OOF scores of the 11 other folds come from models that saw the 12th fold. The empirical pooled OOF coverage sits near the nominal 1 - alpha on every model; per-fold coverage varies by about +-0.1 with 12-40 winners per fold on 5minute.",
        "The guarantee is on winner COUNT (or, as reported beside it, on winners' |net|), not on P&L in the tail: Judge 1's trap. The |net|-weighted coverage is reported next to the count coverage on every row.",
        "The CRC calibration block's scores are OOF from the purged folds, so the block is not disjoint in time from every score's training folds (the same CV+ caveat); its certificate also assumes session exchangeability, which the IS-early vs IS-late drift (null_tapes_drift, AUC 0.95 / 0.97) already violates: the realised risk before the block exceeds the certificate everywhere.",
        "The time-bin taxonomy reads the SETUP clock (`time`, an identity column in `harness.NOT_FEATURES`): its bins (10:30, 13:00) do not align with `hour_bin`'s edges; a deployable form would need a clock key. It is a diagnostic here.",
        "The scorecard's p is a per-fold Platt map of an integer score: pooled thresholds mix fold scales and the score has heavy ties, so several coverage-grid points coincide (identical keep masks under different configs c: separate ledger rows, separate ids).",
        "Sub-family (II) rows are OUTSIDE THE FROZEN SHORTLIST (the importance rule failed for every cluster); they are labelled so in every ledger note and counted in the same family for PBO / SPA.",
        "The coverage-curve rows are scored with controls off (trials); the conformal, ACI and CRC rows with controls on. All are in the family for PBO / SPA / effective trials.",
        "The online_learner study was appending to the ledger concurrently; ids are unique per config (the ledger is append-only).",
        "No OOS row was read; the OOS window is the published lab window (BRIEF caveat).",
    ]
    L.append("## 7. Caveats\n")
    L.append("\n".join(f"- {c}" for c in caveats) + "\n")
    L.append("## 8. Files\n")
    files = sorted(f for f in os.listdir(HERE) if not f.startswith("__") and not f.endswith(".pyc"))
    L.append("\n".join(f"- `{f}`" for f in files) + "\n")
    open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L))

    # machine-readable
    fj = dict(study="operating_point_sizing", generated_at=D.datetime.now().isoformat(timespec="seconds"), scripts=shas, adds_oos_candidate=False,
              statement="re-parameterisation of the gate_family finalists' OOF scores; gate_family wrote no candidate; no candidate here; sizing not run: no gate passed",
              timeframes={}, candidates=[], null_result=True,
              ledger_families=sorted({f for tf in TFS for f in R[tf]["family"]["rows_by_family"]}),
              caveats=caveats, files=files, sizing=SZ)
    for tf in TFS:
        Rt = R[tf]; fam = Rt["family"]
        models = {}
        for k, M in Rt["models"].items():
            models[k] = dict(role=M["role"], vocabulary=M["vocabulary"], p_summary=M["p_summary"], gate_family_nested=M["gate_family_nested"],
                             conformal=[{kk: vv for kk, vv in c.items() if kk != "folds"} for c in M["conformal"]], conformal_alpha_rule=M["conformal_alpha_rule"],
                             conformal_timebin=M.get("conformal_timebin"), aci=M["aci"], coverage_curve=M["coverage_curve"], pareto_argmax_coverage_by_w=M["pareto_argmax_coverage_by_w"],
                             crc=M["crc"], crc_timebin=M.get("crc_timebin"), cost_sensitivity=M["cost_sensitivity"])
        fj["timeframes"][tf] = dict(meta=Rt["meta"], models=models, family=fam, candidate=None, sizing_verdict=SZ["timeframes"][tf]["verdict"])
    json.dump(fj, open(os.path.join(HERE, "findings.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("written FINDINGS.md, findings.json;", len(L), "sections")


if __name__ == "__main__":
    main()
