"""rocket_ceiling: FINDINGS.md + findings.json from results.json (no number is computed here that is not in results.json or the ledger)."""
import os, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np, pandas as pd
import harness as H

R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
FR = json.load(open(os.path.join(HERE, "family_recheck.json"), encoding="utf-8"))     # finalize_family.py: current-harness recheck + run integrity
MODELS = ("rocket", "pca16", "tabular", "stacked")
DOC = open(os.path.join(HERE, "rocket_ceiling.py"), encoding="utf-8").read().split('"""')[1]


def f4(x): return "" if x is None else f"{x:.4f}"
def f2(x): return "" if x is None else f"{x:,.2f}"
def fi(x): return "" if x is None else f"{int(x):,}"


def table(cols, rows):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows: out.append("| " + " | ".join(str(v) for v in r) + " |")
    return "\n".join(out)


L = []
u, cp, o12, st, fam, tc, tm = R["units"], R["cpcv"], R["oof12"], R["stop"], R["family"], R["trunc_check"], R["timing"]
L.append("# rocket_ceiling: is there information in the shape of the last 60 bars beyond the hand-built as-of features?\n")
L.append(f"Study folder `fz_v3/out/studies/rocket_ceiling/` (DESIGN_PANEL `deep-sequence-rocket-probe`, reduced to the single ceiling check both judges allow; "
         f"the `deep-sequence-pretrain-probe` rung 1 = PCA-16 linear probe runs inside it as a comparator). Scripts `rocket_lib.py` (windows, kernel bank, numba PPV transform), "
         f"`rocket_ceiling.py` (the study; runtime {tm['total_s']:,.0f} s; log `rocket_ceiling.log`, `run.nohup`), `finalize_family.py` (resume step: the family statistics recomputed from the ledger "
         f"vectors with the current `harness.spa`, the run-integrity checks; `family_recheck.json`, `finalize.log`), `write_findings.py` (this file and `findings.json` from `results.json` + `family_recheck.json`). "
         f"**IS only** (SETUP date <= 2025-12-31); timeframe **1 minute** only; label **L1** (the 15:25 book). Ledger sha after `{R['ledger_sha_after']}`. "
         f"**This study never gets a candidate slot** (Judge 1); its {fam['ledger_rows_oof'] + fam['ledger_rows_cpcv']} ledger rows still count toward the program's multiplicity.\n")
L.append("## 0. Result in one paragraph\n")
verdict = ("**The pre-registered stop fired.**" if st["triggered"] else "**The pre-registered stop did not fire.**")
L.append(f"{verdict} Over the 11 CPCV paths the AUC gain of the stacked model (tabular HGB + the top 16 PCA components of the 2,000 PPV kernel features) over the tabular HGB alone has "
         f"5th percentile **{cp['gain_stacked']['p5']:+.4f}** (median {cp['gain_stacked']['median']:+.4f}, min {cp['gain_stacked']['min']:+.4f}, max {cp['gain_stacked']['max']:+.4f}, share > 0 {cp['gain_stacked']['share_positive']}) "
         f"against the threshold {st['threshold']}. The rocket probe alone reaches path AUC median {cp['auc_rocket']['median']:.4f} vs tabular {cp['auc_tabular']['median']:.4f} (gain median {cp['gain_rocket']['median']:+.4f}, 5th pct {cp['gain_rocket']['p5']:+.4f}); "
         f"the PCA-16 window probe (the pretrain footnote) {cp['auc_pca16']['median']:.4f} (gain median {cp['gain_pca16']['median']:+.4f}). 12-block pooled OOF AUC: tabular {o12['auc']['tabular']:.4f}, stacked {o12['auc']['stacked']:.4f}, rocket {o12['auc']['rocket']:.4f}, pca16 {o12['auc']['pca16']:.4f}. "
         f"{'No distillation was run and nothing is proposed for ST13/ST14.' if st['triggered'] else 'Distillation ran; see section 7.'} "
         f"Every gate evaluated (4 models x skip 30/50/70 %) is a ledger row; the best OOF kept-vs-skipped difference in the family is {fam['best_by_diff']['diff']:+,.2f} INR/trade "
         f"({fam['best_by_diff']['model']} at skip {fam['best_by_diff']['skip_q']}), PBO(diff) {fam['pbo_diff']['pbo']}, SPA p {fam['spa']['spa_p']} (revised `harness.spa`, recomputed from the ledger vectors: "
         f"studentised {FR['family_recomputed']['spa']['spa_p']}, unstudentised {FR['spa_revised_extra']['spa_p_unstudentised']}); `go_no_go` on it: {fam['go_no_go_best']['passed']} (information only, no slot).\n")
L.append("## 1. Definitions (fixed before any number was looked at; the script's docstring, verbatim)\n")
L.append("```\n" + DOC.strip() + "\n```\n")
L.append("## 2. Data, windows, kernel bank, causality check\n")
w = R["windows"]; kk = R["kernels"]
L.append(table(["item", "value"], [
    ["units (IS / OOS row count)", f"{u['is_']:,} / {u['oos_row_count_only']:,} (OOS never read)"],
    ["IS win rate / mean L1 net (INR)", f"{u['is_win_rate']} / {u['is_mean_net']:,.2f}"],
    ["window tensor", f"{w['shape']} float32 = {w['mb']} MB, built in {w['build_s']} s"],
    ["channel means", str(w["channel_means"])], ["channel sds", str(w["channel_sds"])],
    ["NA-flag share (ch4) / same-session share (ch6) / windows crossing the session start", f"{w['na_flag_share']} / {w['same_session_share']} / {w['share_windows_crossing_session_start']}"],
    ["kernel bank", f"K = {R['K']}, length 9, seed {kk['seed']}, dilation counts (d = 1..15) {kk['dilation_counts']}, pair share {kk['pair_share']}, channel use {kk['channel_use']}; frozen in `kernels.npz`"],
    ["truncation check (`windows_trunc_check.json`)", f"cut {tc['cut']}, bars {tc['bars_truncated']:,}, SETUPs before the cut {tc['setups_before_cut']}, same keys {tc['same_setup_keys']}, max |diff| {tc.get('max_abs_diff')}, **PASS {tc['PASS']}**"],
    ["base design", f"{R['design']['base_columns']} as-of columns (`harness.design`); flattened window {R['design']['flattened_window']}"],
    ["PPV feature matrix per fold", f"n_train x {R['K']} float32 ({u['is_'] * R['K'] * 4 / 2 ** 20:.0f} MB for all IS rows, one transform {tm['one_transform_s']} s single-threaded; the design's 5,266 x 2,000 = 42 MB figure counts the OOS rows, which were not built)"],
]))
L.append("\n## 3. Per-fold AUC (12 purged blocks; `fold_auc.csv`)\n")
rows = []
for b in range(12):
    rows.append([b] + [f4(o12["per_block_auc"][m][b]) for m in MODELS] + [f"{o12['per_block_gain']['stacked-tabular'][b]:+.4f}", f"{o12['per_block_gain']['rocket-tabular'][b]:+.4f}", o12["alpha_rocket"][b], o12["alpha_pca16"][b]])
L.append(table(["block", "AUC rocket", "AUC pca16", "AUC tabular", "AUC stacked", "stacked - tabular", "rocket - tabular", "alpha rocket", "alpha pca16"], rows))
L.append(f"\nPooled 12-block OOF AUC: " + ", ".join(f"{m} **{o12['auc'][m]:.4f}**" for m in MODELS) + "; average precision: " + ", ".join(f"{m} {o12['ap'][m]:.4f}" for m in MODELS) +
         f". Judge 1's footnote form (stacked - tabular < 0.02 in every block): **{o12['judge1_all_blocks_below_0_02']}**. Inner-fold OOF AUC at the chosen alpha, mean over blocks: " +
         ", ".join(f"{m} {np.mean([x[m] for x in o12['inner_auc_at_chosen']]):.4f}" for m in MODELS) + ".\n")
L.append("## 4. The CPCV path distribution (66 splits -> 11 paths; `path_auc.csv`) and the pre-registered stop\n")
P = pd.read_csv(os.path.join(HERE, "path_auc.csv"))
L.append(table(["path"] + [f"AUC {m}" for m in MODELS] + ["stacked - tabular", "rocket - tabular", "pca16 - tabular"],
               [[int(r.path)] + [f4(getattr(r, f"auc_{m}")) for m in MODELS] + [f"{r.gain_stacked:+.4f}", f"{r.gain_rocket:+.4f}", f"{r.gain_pca16:+.4f}"] for r in P.itertuples()]))
L.append("\n" + table(["statistic over 11 paths", "median", "5th pct", "min", "max", "share > 0"],
                      [[k, f"{v['median']:+.4f}" if k.startswith("gain") else f4(v["median"]), f"{v['p5']:+.4f}" if k.startswith("gain") else f4(v["p5"]), f"{v['min']:+.4f}" if k.startswith("gain") else f4(v["min"]),
                        f"{v['max']:+.4f}" if k.startswith("gain") else f4(v["max"]), v["share_positive"]] for k, v in cp.items() if isinstance(v, dict) and "p5" in v]))
L.append(f"\nPer-split (66) gains stacked - tabular: min {cp['split_gain_stacked']['min']:+.4f}, median {cp['split_gain_stacked']['median']:+.4f}, share < 0.02 {cp['split_gain_stacked']['share_below_0_02']}; rocket - tabular: min {cp['split_gain_rocket']['min']:+.4f}, median {cp['split_gain_rocket']['median']:+.4f}. "
         f"Alpha chosen by the nested GroupKFold across the 66 CPCV training folds: rocket {cp['alpha_rocket_counts']}, pca16 {cp['alpha_pca16_counts']}.\n")
L.append(f"**Pre-registered stop** (Judge 2): CPCV 5th-percentile AUC gain of stacked over tabular = **{st['p5_gain_stacked']:+.4f}** {'<' if st['triggered'] else '>='} {st['threshold']} -> "
         f"{'**the study ends with that number; no distillation, no candidate.**' if st['triggered'] else 'distillation ran (section 7).'}\n")
L.append("## 5. Every gate evaluated (ledger families `rocket/<model>`; CPCV paths `rocket/<model>/cpcv`; `gates.csv`, `cpcv_gate_paths.csv`)\n")
L.append("Threshold = the q-quantile of the training fold's inner-OOF scores (never the test rows), so the realised kept share is near, not exactly, 1 - q. Skip = score below the threshold. INR per trade.\n")
rows = []
for g in R["gates"]:
    c = g["cpcv"]
    rows.append([g["model"], g["skip_q"], g["id"], fi(g["kept_n"]), g["kept_share"], f2(g["kept_mean"]), f2(g["skipped_mean"]), f2(g["diff"]), f2(g["diff_top1_removed"]), g["control_pct"], g["perm_p"], g["loser_recall"], g["winner_recall_weighted"],
                 g["top_decile_winners_skipped"], g["sign_blocks"], f2(g["kept_mean_slip8"]), f2(c["diff_median"]), f2(c["diff_p5"]), c["diff_share_positive"], c.get("control_pct_median"), c.get("control_pct_p5"), g["go_raw"]])
L.append(table(["model", "skip q", "ledger id", "kept n", "kept share", "kept mean", "skipped mean", "diff", "diff top1 removed", "control pct", "perm p", "loser recall", "|net|-w winner recall", "top-decile winners skipped", "sign blocks /12", "kept mean slip 8",
                "CPCV diff median", "CPCV diff p5", "CPCV share > 0", "CPCV control pct median", "CPCV control pct p5", "go (raw checks)"], rows))
L.append("\n## 6. Family statistics (the 12 OOF gate rows; PBO / SPA / effective trials from the ledger)\n")
L.append(table(["statistic", "value"], [
    ["design family (window lengths x kernel counts x probes)", fam["design_family"] + "; probes: " + "; ".join(fam["probes"])],
    ["ledger rows: OOF gates / CPCV path rows", f"{fam['ledger_rows_oof']} / {fam['ledger_rows_cpcv']}"],
    ["effective trials (participation ratio)", fam["effective_trials"]],
    ["PBO (diff) / PBO (kept mean)", f"{fam['pbo_diff']['pbo']} / {fam['pbo_kept_mean']['pbo']} (partitions {fam['pbo_diff']['partitions']}; degradation slope {fam['pbo_diff']['degradation_slope']})"],
    ["SPA: best gain / t / RC p / SPA p", f"{fam['spa']['best_mean_gain']} / {fam['spa']['best_t']} / {fam['spa']['rc_p']} / **{fam['spa']['spa_p']}** (best = {fam['spa_best']['model']} skip {fam['spa_best']['skip_q']}, id {fam['spa_best']['id']})"],
    ["best by OOF diff", f"{fam['best_by_diff']['model']} skip {fam['best_by_diff']['skip_q']}, id {fam['best_by_diff']['id']}, diff {fam['best_by_diff']['diff']:+,.2f}"],
    ["DSR of the best (n_trials = 12)", f"SR {fam['dsr_best'].get('sr')}, SR0 {fam['dsr_best'].get('sr0')}, DSR {fam['dsr_best'].get('dsr')}, p {fam['dsr_best'].get('p')}"],
    ["block bootstrap 90 % CI of the best's diff", f"{fam['bootstrap_best']['diff_ci']} (P(diff <= 0) {fam['bootstrap_best']['diff_p_le0']})"],
    ["go / no-go on the best (information only)", f"passed **{fam['go_no_go_best']['passed']}**; failed: " + ", ".join(k for k, v in fam["go_no_go_best"]["checks"].items() if not v[0])],
]))
fr, fx, rep = FR["family_recomputed"], FR["spa_revised_extra"], FR["reproduces_results_json"]
L.append(f"\n### 6a. The same family recomputed from the ledger vectors with the current harness (`finalize_family.py` -> `family_recheck.json`; harness sha `{FR['harness_sha']}`)\n")
L.append("`harness.spa` was revised after this run (the exit-policy refuter's finding: a candidate active in fewer than max(10, 5 % T) sessions leaves the studentised family; White's unstudentised statistic is "
         "reported too). The same 12 vectors, the same bootstrap tag (so the same 2,000 stationary-bootstrap draws), no ledger row written.\n")
L.append(table(["statistic", "results.json (harness at 07:12)", "recomputed (current harness)", "reproduces"], [
    ["effective trials", fam["effective_trials"], fr["effective_trials"], rep["effective_trials"]],
    ["PBO (diff) / PBO (kept mean)", f"{fam['pbo_diff']['pbo']} / {fam['pbo_kept_mean']['pbo']}", f"{fr['pbo_diff']['pbo']} / {fr['pbo_kept_mean']['pbo']}", f"{rep['pbo_diff.pbo']} / {rep['pbo_kept_mean.pbo']}"],
    ["SPA studentised (Hansen): best / t / RC p / SPA p", f"{fam['spa_best']['model']} skip {fam['spa_best']['skip_q']} / {fam['spa']['best_t']} / {fam['spa']['rc_p']} / {fam['spa']['spa_p']}",
     f"{fr['spa_best']['model']} skip {fr['spa_best']['skip_q']} / {fr['spa']['best_t']} / {fr['spa']['rc_p']} / **{fr['spa']['spa_p']}**", f"{rep['spa.best']} / {rep['spa.best_t']} / {rep['spa.rc_p']} / {rep['spa.spa_p']}"],
    ["SPA: candidates excluded from the studentised family (min active sessions)", "n/a", f"{fx['excluded_from_studentised']} of 12 (min {fx['min_active_sessions']}; active sessions per candidate {fr['active_sessions_per_candidate']})", ""],
    ["SPA unstudentised (White): best / mean gain / RC p / SPA p", "n/a", f"{fr['spa_best_unstudentised']['model']} skip {fr['spa_best_unstudentised']['skip_q']} / {fx['best_mean_gain_unstudentised']} / {fx['rc_p_unstudentised']} / **{fx['spa_p_unstudentised']}**", ""],
    ["DSR p of the best", fam["dsr_best"].get("p"), fr["dsr_best"].get("p"), rep["dsr_best.p"]],
    ["block bootstrap 90 % CI of the best's diff", fam["bootstrap_best"]["diff_ci"], fr["bootstrap_best"]["diff_ci"], rep["bootstrap_best.diff_ci"]],
    ["go / no-go on the best", fam["go_no_go_best"]["passed"], fr["go_no_go_best"]["passed"], rep["go_no_go_best.passed"]],
]))
L.append("\n## 7. Distillation\n")
d = R["distillation"]
if d["ran"]:
    L.append(f"Ran (the stop did not fire). OOF fidelity {d['fidelity_oof']} (balanced {d['fidelity_balanced_oof']}); rule ledger id `{d['rule_ledger_id']}` diff {d['rule_diff']}; probe tercile ledger id `{d['probe_ledger_id']}` diff {d['probe_diff']}; share of the probe's effect kept {d['share_of_probe_effect']}; passes {d['passes']}.\n\n```\n{d['tree_text']}\n```\n")
else:
    we = FR["win_ext"]
    L.append(f"Not run: {d['reason']}. The design's distillation step (depth-3 tree on base + `win_sign_agree10`, `win_dd_extreme_atr`, `win_range_slope`) is implemented in `rocket_ceiling.py::distillation` and did not execute; "
             f"the three window summaries are already in `{we['file']}` for the importance study (Judge 2): {we['rows']:,} SETUP rows, coverage on the {we['is_units']:,} IS units {we['coverage_is_units']} (checked by `finalize_family.py`, never read by the run).\n")
L.append("## 8. Timing, memory, seeds\n")
L.append(table(["item", "value"], [
    ["kernel seed (sha1 of 'fz|rocket_ceiling|minute|L60|K2000' mod 2^32)", R["seed"]],
    ["per-fold bias seed", "sha1(f'{seed}|purged|{block}') or sha1(f'{seed}|cpcv|{a}|{b}') mod 2^32 (in `fold_auc.csv` rows via results.json `folds`)"],
    ["numba JIT / one full transform (4,452 windows x 2,000 kernels x 60 bars)", f"{tm['jit_s']} s / {tm['one_transform_s']} s"],
    ["per-fold wall time (purged blocks)", str(tm["fold_s_purged"])], ["per-fold wall time, CPCV mean", f"{tm['fold_s_cpcv_mean']} s"],
    ["mean stage seconds per fold", str(tm["stage_s_mean"])],
    ["78 folds done at / total (with the 144 ledger rows and their 2,000-draw controls)", f"{tm['models_done_s']:,.0f} s / {tm['total_s']:,.0f} s"],
    ["RSS after the folds / peak RSS (ru_maxrss)", f"{tm['rss_after_models_mb']} MB / {tm['peak_rss_mb']} MB (the box ran other studies concurrently: load average ~16 on 4 cores during this run)"],
    ["family size recorded for the multiplicity statement", f"{fam['design_family']}; 12 OOF gate rows + 132 CPCV path rows in the ledger (`rocket/<model>`, `rocket/<model>/cpcv`)"],
]))
lg, sh, ld = FR["log"], FR["ledger_sha_after_reproduced"], FR["ledger"]
L.append("\n### 8a. Run integrity (resume after the 2026-09-29 usage-limit pause; `finalize_family.py`)\n")
L.append(table(["check", "result"], [
    ["the 12 OOF gate rows of `results.json` re-read from the ledger, field by field", f"match **{ld['oof_rows_match_results_json']}** (mismatches: {ld['mismatches']})"],
    ["rocket rows in the ledger", f"{ld['rocket_rows']} = {ld['oof_rows']} OOF + {ld['cpcv_rows']} CPCV, {ld['by_family']}, written {ld['first_at']} .. {ld['last_at']} (UTC); {len(ld['interleaved_other_rows_in_span'])} rows of the concurrently running importance study interleaved (append-only shared ledger)"],
    ["script that wrote the rows", f"ledger `script_sha` {ld['script_sha_of_rows']} == sha of `rocket_ceiling.py` on disk: **{ld['script_sha_matches_file_on_disk']}**"],
    ["`results.json` -> `ledger_sha_after` `{}`".format(sh["target"]), f"= sha of the ledger's first {sh['prefix_rows']} rows: **{sh['match']}**; the last rocket row is row {sh['last_rocket_row_index']} ({sh['last_rocket_row_at']}), the next row is {sh['first_row_after_prefix']}. {sh['statement']}."],
    ["the log on disk", f"{lg['lines']} lines, `rocket_ceiling.log` == `run.nohup` {lg['identical_to_run_nohup']}; last line {lg['last_line_time']} is the last gate row ({lg['last_line_is_gate_row']}); the run finished at {lg['run_finished_at_from_results_json']}. "
                        f"The script's final three log calls ({len(lg['final_log_calls_in_script_present'])}/3 present in the file that ran) are **not** in the log ({len(lg['final_log_lines_present_in_log'])}/3): {lg['explanation']}"],
]))
L.append("\n## 9. What would falsify this finding\n")
L.append("- A CPCV 5th-percentile stacked-minus-tabular AUC gain >= 0.03 on a re-run with another kernel seed (the bank is random; the seed is logged and the study is deterministic given it). The per-path gains here are the evidence that the window shape adds nothing the base features do not already carry; a different seed changing that verdict would mean the 2,000-kernel bank is too small to be stable, not that the tape has changed.\n"
         "- A window length or channel set outside the reduced design (L = 120, the 5-minute frame) showing a gain: not tested here by the judges' cut; it would be a new family with its own multiplicity count.\n"
         "- A leakage in the window tensor: excluded by the truncation check (identical windows for every SETUP before the 2025-06-30 cut) and by construction (bars <= k only; biases, scalers and PCA fitted on training rows).\n"
         "- The AUC statistic is rank-based and label-balanced; a gate that adds expectancy without adding AUC (a tail effect on the few large winners) would not be seen by the stop rule. The gate rows (section 5) carry the INR numbers for that reading: none of the 12 clears the control percentile / block-sign / CPCV checks together.\n")
L.append("## 10. Candidates\n")
L.append("None. This study never gets a candidate slot (Judge 1); the stop rule decides only whether distillation runs. `null_result = true`.\n")
L.append("## 11. Caveats\n")
cav = [
    "Reduced design (both judges): 1 minute only, L = 60, 2,000 kernels, one probe family; the 5-minute frame, L = 120 and the ridge / net-regression probes of the original design were cut and are not tested.",
    "The pre-SETUP window is templated by the engine's own SETUP definition (CHoCH then continuation), so shape motifs are the rule rather than information (Judge 1); the result is consistent with that.",
    "Thresholds for the skip fractions come from the training fold's inner-OOF score distribution; the test-fold scores come from the model refit on the whole training fold (same per-sample regularisation, so the same scale up to sampling), and the test block's own score distribution shifts with its regime, so the realised kept share deviates from 1 - q (reported per gate).",
    "The alpha grid is the design's 1e-3 .. 1e3 read as a per-sample L2 penalty (sklearn C = 1/(alpha n)); with sklearn's unnormalised C the same numbers would have put the optimum on the grid's edge (seen in a one-split timing benchmark before the study ran, no ledger row).",
    "The stacked model is the same HGB with 16 extra columns; a gain of exactly zero is not guaranteed by construction (the extra columns can hurt), so negative gains are possible and are reported as such.",
    "Windows crossing the session start carry the overnight gap in the log-return channel; the same-session channel flags those bars. Bars before the tape start (session 0 only) are zero-padded.",
    "Sequence pretraining (the design's rungs 2-3) is deferred: torch is present in the cloud but the sample-size objection of both judges is unchanged; the PCA-16 rung ran as a comparator and is the weakest of the four models.",
    "The box ran other studies concurrently; wall-clock timings are inflated, CPU seconds are not reported.",
    "The log on disk ends at the last gate row: the run's final three log lines (family statistics, 'distillation not run', 'done in') were lost to the 06:24 checkout-inode incident (PROGRESS.md); results.json carries their values and its ledger sha reproduces as a ledger prefix (section 8a). The agent that launched the run was cut off by the usage limit at 06:44 UTC while the run was between CPCV splits 43 and 49 (logged 06:39:50 and 06:47:17); FINDINGS.md, findings.json and the family recheck were written by the resuming agent from results.json and the ledger, nothing was rerun.",
    f"results.json's SPA is the harness's SPA as of 07:12; the revised harness.spa (min-active-session filter, unstudentised statistic) is reported next to it in section 6a. Both agree on the studentised p because no rocket gate is near-degenerate: the 12 candidates have a non-zero selection gain in {min(FR['family_recomputed']['active_sessions_per_candidate'])}-{max(FR['family_recomputed']['active_sessions_per_candidate'])} of the {FR['family_recomputed']['spa']['sessions']} active sessions, against the exclusion threshold of {FR['spa_revised_extra']['min_active_sessions']}.",
]
L.extend(f"- {c}" for c in cav)
L.append("\n## 12. Files\n")
files = ["rocket_lib.py", "rocket_ceiling.py", "finalize_family.py", "write_findings.py", "rocket_ceiling.log", "run.nohup", "finalize.log", "results.json", "family_recheck.json", "fold_auc.csv", "path_auc.csv", "gates.csv", "cpcv_gate_paths.csv", "windows_trunc_check.json", "kernels.npz", "oof_scores.npz", "FINDINGS.md", "findings.json"]
L.extend(f"- `studies/rocket_ceiling/{f}`" for f in files)
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

FJ = dict(study="rocket_ceiling", design="deep-sequence-rocket-probe reduced to the single ceiling check (both judges); pretrain-probe rung 1 (PCA-16) as comparator",
          timeframes={"minute": dict(label="L1", units_is=u["is_"], oos_row_count_only=u["oos_row_count_only"], seed=R["seed"], L=R["L"], kernels=R["K"], channels=R["C"],
                                     trunc_check=dict(PASS=tc["PASS"], max_abs_diff=tc.get("max_abs_diff"), setups_before_cut=tc["setups_before_cut"]),
                                     oof12_auc=o12["auc"], oof12_ap=o12["ap"], per_block_auc=o12["per_block_auc"], per_block_gain=o12["per_block_gain"], judge1_all_blocks_below_0_02=o12["judge1_all_blocks_below_0_02"],
                                     cpcv=cp, stop=st, gates=R["gates"], family=fam, family_recheck_current_harness=FR["family_recomputed"], spa_revised_extra=FR["spa_revised_extra"],
                                     recheck_reproduces_results_json=FR["reproduces_results_json"], distillation=R["distillation"], win_ext=FR["win_ext"], timing=tm)},
          headline=dict(stop_triggered=st["triggered"], cpcv_p5_gain_stacked_minus_tabular=st["p5_gain_stacked"], threshold=st["threshold"], cpcv_gain_stacked=cp["gain_stacked"], cpcv_gain_rocket=cp["gain_rocket"], cpcv_gain_pca16=cp["gain_pca16"],
                        oof12_auc=o12["auc"], best_gate_by_diff=fam["best_by_diff"], pbo_diff=fam["pbo_diff"]["pbo"], spa_p_studentised=FR["family_recomputed"]["spa"]["spa_p"], spa_p_unstudentised=FR["spa_revised_extra"]["spa_p_unstudentised"],
                        effective_trials=fam["effective_trials"], go_no_go_best_passed=fam["go_no_go_best"]["passed"]),
          candidates=[], null_result=True, candidate_slot=R["candidate_slot"],
          ledger_families=sorted({f"rocket/{m}" for m in MODELS} | {f"rocket/{m}/cpcv" for m in MODELS} | ({"rocket/distilled"} if R["distillation"]["ran"] else set())),
          ledger_rows=dict(oof=fam["ledger_rows_oof"], cpcv=fam["ledger_rows_cpcv"], total=fam["ledger_rows_oof"] + fam["ledger_rows_cpcv"]), ledger_sha_after=R["ledger_sha_after"],
          run_integrity=dict(ledger_sha_after_reproduced=FR["ledger_sha_after_reproduced"], ledger=FR["ledger"], log=FR["log"]),
          resume_note="run finished on its own at 07:12:37 UTC during the usage-limit pause; FINDINGS / findings.json / family recheck written by the resuming agent from results.json and the ledger; nothing rerun",
          caveats=cav, files=[f"studies/rocket_ceiling/{f}" for f in files])
json.dump(FJ, open(os.path.join(HERE, "findings.json"), "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print("FINDINGS.md and findings.json written;", "stop triggered" if st["triggered"] else "stop not triggered", "p5 gain", st["p5_gain_stacked"])
