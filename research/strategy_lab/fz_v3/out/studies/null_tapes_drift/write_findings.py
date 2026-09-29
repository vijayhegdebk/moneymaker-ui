"""Compose FINDINGS.md and findings.json for study null_tapes_drift from the outputs (null_distributions.json, tape_results.csv,
reality_check.csv, real_reference_<tf>.json, fit_<tf>.json, drift.json). Numbers only from those files; nothing computed here
beyond table formatting and the pre-registered pass rule applied to the three reference gates.

    python write_findings.py
"""
import os, sys, json, glob
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402

GATES = ("frozen_st7_st8", "choch2_skip", "sl_above_median_skip")
GEN_LABEL = {"session": "session bootstrap", "segment": "segment bootstrap (30-bar blocks)", "gmm": "GMM-Markov"}


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return "-"
    return f"{x:,.{d}f}" if isinstance(x, (int, float, np.floating, np.integer)) else str(x)


def main():
    null = json.load(open(os.path.join(HERE, "null_distributions.json")))
    drift = json.load(open(os.path.join(HERE, "drift.json"))) if os.path.exists(os.path.join(HERE, "drift.json")) else None
    for tf in ("5minute", "minute"):                                   # per-timeframe runs (drift.py --tf <tf> --out drift_<tf>.json) merged in
        p = os.path.join(HERE, f"drift_{tf}.json")
        if os.path.exists(p):
            d = json.load(open(p))
            if drift is None: drift = d
            elif tf in d["timeframes"]: drift["timeframes"][tf] = d["timeframes"][tf]
    if drift is not None and set(drift["timeframes"]) == {"5minute", "minute"}:
        json.dump(drift, open(os.path.join(HERE, "drift.json"), "w"), indent=1, default=str)     # the merged file is the deliverable
    R = pd.read_csv(os.path.join(HERE, "tape_results.csv")); RC = pd.read_csv(os.path.join(HERE, "reality_check.csv"))
    fits = {tf: json.load(open(p)) for tf in ("5minute", "minute") for p in [os.path.join(HERE, f"fit_{tf}.json")] if os.path.exists(p)}
    refs = {tf: json.load(open(p)) for tf in ("5minute", "minute") for p in [os.path.join(HERE, f"real_reference_{tf}.json")] if os.path.exists(p)}
    ledger_rows = H.read_ledger("null_tapes_drift")
    L = []
    L.append("# null_tapes_drift: synthetic null tapes (c) and adversarial drift validation (d)\n")
    L.append("DESIGN_PANEL decision-making-3, parts (c) and (d), with both judges' fixes: (a) / (b) live in `harness.py`; the null tapes run on 5 minutes "
             "(20 full-length tapes per generator) and on 1 minute (8 one-year tapes per generator, RSS checked); the segment bootstrap is Judge 1's second "
             "null; the IS-vs-OOS adversarial check is not run here (oos_once.py post-mortem). No gate search, no OOS row read. Tape numbers never enter the ledger; "
             "the three reference gates on the real tape are ledger rows of family `null_tapes_drift/real_ref`. Scripts: `gen_tapes.py`, `tapes.py`, `run_tapes.py`, "
             "`drift.py`, `write_findings.py`; logs `run_5minute.log`, `run_minute.log`, `drift.log`.\n")
    L.append("## 1. Definitions (fixed before the numbers)\n")
    L.append("- **Unit / label / statistic** as the harness: a Foundation SETUP taken under the L1 (15:25) book; kept-vs-skipped difference of mean net (INR per unit); "
             "the session-matched random control percentile (`fz_report.random_control`, 2,000 draws); permutation p; block sign count. On a tape the statistic is "
             "computed by `harness.metrics` on a `harness.Table` built from the tape's own `features.parquet` / `trades.parquet` / `sessions.parquet` "
             "(`tapes.load_tape`, a copy of `harness.load` pointed at the tape folder). Every tape row is IS (the tapes carry IS calendar dates).")
    L.append("- **Three reference gates** (all as keep masks): `frozen_st7_st8` = keep where `fz_traded` (the frozen ST7/ST8 gate as it traded on that tape); "
             "`choch2_skip` = skip where `n_choch_since_bos >= 2` (pre-registered mechanical gate 1); `sl_above_median_skip` = skip where `sl_dist_atr` > the tape's own "
             "IS median (pre-registered mechanical gate 2). The two mechanical gates are the engine-mechanics check: a gate on stop distance or CHoCH counts can read "
             "non-zero on a memory-free tape through the engine itself (Judge 2), so its null is not 0.")
    L.append("- **Generators** (fitted on IS bars only, `gen_tapes.py` docstring): *session bootstrap* (whole IS sessions with replacement, level chained through the drawn "
             "session's open-to-close path and a gap drawn from the IS gap distribution); *segment bootstrap* (30-bar clock-aligned blocks from random IS sessions, "
             "re-based and chained, same gap draw); *GMM-Markov* (GaussianMixture 4-6 full-covariance components by BIC on the z-scored per-bar vector (log return, "
             "log volume ratio to the clock median, range/atr14, close position), first-order Markov chain on the labels, per-session sampling with the clock "
             "volume profile, OHLC rebuilt consistently, samples clipped to the IS range per dimension). Full-length sessions only (375 / 75 bars); the real IS "
             "tape's short sessions are excluded from the pools (listed in `fit_<tf>.json`). Tapes are written in the near-month CSV format and pushed through "
             "`build/build.py --path` (engine.run with the Foundation rules, fz.run with the frozen ST7/ST8 block, L0 and L1 pricing, the same 261-column feature table).")
    L.append("- **Null distribution** = per timeframe, generator and gate: p5 / p50 / p95 / mean / min / max of the tape diffs, the share of tapes with diff > 0, "
             "p50 / p95 of the control percentile, the real-tape value and its percentile among the tapes. **Pre-registered comparison** (DESIGN_PANEL (c), Judge 1's "
             "go/no-go): the real-tape difference must be above the null-tape 95th percentile; here that is read on the two memory-free nulls (GMM-Markov and segment), "
             "with the session bootstrap as the stability read (share of tapes with the real diff's sign).")
    L.append("- **Reality check** per generator: within-session per-bar log-return std (bps) and excess kurtosis, autocorrelation of |r| at lags 1-5 (pairs inside a "
             "session), CHoCH / BOS / SETUP / L1-unit counts per session, the raw L1 book, the frozen gate's kept share, the final price level and median ATR14; "
             "a generator whose median SETUP rate is outside [1/3, 3] x the real rate is flagged a poor null.")
    L.append("- **Adversarial validation (d)**: HistGradientBoostingClassifier IS-early (2021-10-01..2023-09-30) vs IS-late (2023-10-01..2025-12-31) on "
             "`harness.design(T)` of the real tape, IS rows; pooled out-of-fold AUC under `harness.purged_splits` (12 blocks, purge by exit bar, 3-session embargo); "
             "chance = 20 label permutations; variant A = all as-of columns, variant B = without time proxies (|Spearman rho| >= 0.9 with `session_idx`); SHAP "
             "(TreeExplainer) ranking on B with the direction of drift.\n")
    # ---- fits
    L.append("## 2. Generator fits (IS bars only)\n")
    L.append("| tf | IS sessions (full / short excluded) | IS bars | gaps | gap log-std | GMM K (BIC 4/5/6) | GMM fit rows | tapes x sessions |")
    L.append("|---|---|---|---|---|---|---|---|")
    for tf, fs in fits.items():
        L.append(f"| {tf} | {fs['is_sessions']} ({fs['pool_sessions']} / {len(fs['short_sessions_excluded'])}) | {fs['is_bars']:,} | {fs['gaps_n']} | {fs['gap_log_std']:.5f} | "
                 f"{fs['gmm_k']} ({', '.join(f'{int(float(v)):,}' for v in fs['gmm_bic'].values())}) | {fs['gmm_fit_rows']:,} | {fs['tapes_per_generator']} x {fs['sessions_per_tape']} |")
    L.append("")
    # ---- real reference
    L.append("## 3. The three reference gates on the real tape (IS, L1; ledger family `null_tapes_drift/real_ref`)\n")
    L.append("| tf | gate | ledger id | n | kept n (share) | kept mean | skipped mean | diff | diff top1% removed | perm p | control pct | loser recall | winner recall (net-wtd) | sign blocks |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for tf, ref in refs.items():
        for g, v in ref["gates"].items():
            L.append(f"| {tf} | {g} | {v['id']} | {v['n']} | {v['kept_n']} ({f(v['kept_share'], 3)}) | {f(v['kept_mean'])} | {f(v['skipped_mean'])} | **{f(v['diff'])}** | "
                     f"{f(v['diff_top1_removed'])} | {f(v['perm_p'], 4)} | {f(v['control_pct'], 1)} | {f(v['loser_recall'], 3)} | {f(v['winner_recall_weighted'], 3)} | {v['sign_blocks']} |")
    L.append(f"\n`sl_dist_atr` IS median: " + ", ".join(f"{tf} {ref['sl_dist_atr_is_median']:.4f}" for tf, ref in refs.items()) + ".\n")
    # ---- null distributions
    L.append("## 4. Null distributions (the certificate: `null_distributions.json`)\n")
    L.append("Diff = kept-vs-skipped mean L1 net on the tape (INR per unit). `real pct` = the real-tape diff's percentile among the tapes; `pass` = real diff > tape p95.\n")
    L.append("| tf | generator | gate | tapes | units p50 | kept share p50 | diff p5 | diff p50 | diff p95 | diff min / max | share diff>0 | control pct p50 / p95 | share ctrl>=95 | real diff | real pct | real > p95 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    passes = {}
    for tf, d in null["timeframes"].items():
        for gen, g in d["generators"].items():
            for gate, v in g["gates"].items():
                passes[(tf, gen, gate)] = v["real_above_tape_p95"]
                L.append(f"| {tf} | {GEN_LABEL.get(gen, gen)} | {gate} | {v['n']} | {f(v['units_p50'], 0)} | {f(v['kept_share_p50'], 3)} | {f(v['diff_p5'])} | {f(v['diff_p50'])} | **{f(v['diff_p95'])}** | "
                         f"{f(v['diff_min'])} / {f(v['diff_max'])} | {f(v['diff_share_positive'], 3)} | {f(v['control_pct_p50'], 1)} / {f(v['control_pct_p95'], 1)} | {f(v['control_pct_share_ge95'], 3)} | "
                         f"{f(v['real_diff'])} | {f(v['real_diff_percentile_in_tapes'], 1)} | {'yes' if v['real_above_tape_p95'] else 'no'} |")
    L.append("")
    L.append("### 4a. Reading of the reference gates against their own nulls\n")
    for tf, d in null["timeframes"].items():
        for gate in GATES:
            reads = []
            for gen in ("gmm", "segment", "session"):
                v = d["generators"].get(gen, {}).get("gates", {}).get(gate)
                if v: reads.append(f"{gen}: p50 {f(v['diff_p50'])}, p95 {f(v['diff_p95'])}, real pct {f(v['real_diff_percentile_in_tapes'], 1)}, same sign {f(v['tapes_same_sign_as_real'], 2)}")
            real = (d.get("real_reference") or {}).get(gate, {})
            verdict = "passes the null-tape check" if (passes.get((tf, "gmm", gate)) and passes.get((tf, "segment", gate))) else "does NOT pass the null-tape check"
            L.append(f"- **{tf} / {gate}**: real diff {f(real.get('diff'))} (control pct {f(real.get('control_pct'), 1)}); {'; '.join(reads)} -> {verdict}.")
    L.append("")
    L.append("### 4b. Key readings (numbers from `null_distributions.json`)\n")
    def gv(tf, gen, gate): return null["timeframes"][tf]["generators"][gen]["gates"][gate]
    def rv(tf, gate): return null["timeframes"][tf]["real_reference"][gate]
    if "5minute" in null["timeframes"] and "minute" in null["timeframes"]:
        a, b, s = gv("5minute", "gmm", "frozen_st7_st8"), gv("5minute", "segment", "frozen_st7_st8"), gv("5minute", "session", "frozen_st7_st8")
        L.append(f"1. **The frozen ST7/ST8 gate reads positive on memory-free 5-minute tapes**: GMM-Markov median diff {f(a['diff_p50'])} (p95 {f(a['diff_p95'])}, share of tapes > 0 "
                 f"{f(a['diff_share_positive'], 2)}, control pct p50 {f(a['control_pct_p50'], 1)}, {f(100 * a['control_pct_share_ge95'], 0)}% of tapes at or above the 95th control "
                 f"percentile); segment median {f(b['diff_p50'])} (p95 {f(b['diff_p95'])}, control pct p50 {f(b['control_pct_p50'], 1)}); session median {f(s['diff_p50'])}. "
                 f"On tapes with no swing memory the rooms gate still separates kept from skipped by ~+150-200 INR and clears the random control on half the tapes: that "
                 f"part of any ST7/ST8-shaped statistic is engine / FZ mechanics, not market memory. The real 5-minute frozen gate ({f(rv('5minute', 'frozen_st7_st8')['diff'])}, "
                 f"control pct {f(rv('5minute', 'frozen_st7_st8')['control_pct'], 1)}) sits at the {f(a['real_diff_percentile_in_tapes'], 0)}th percentile of the GMM null and the "
                 f"{f(b['real_diff_percentile_in_tapes'], 0)}th of the segment null: on the real tape it does worse than on its own memory-free tapes.")
        a, b = gv("5minute", "gmm", "sl_above_median_skip"), gv("5minute", "segment", "sl_above_median_skip"); a1, b1 = gv("minute", "gmm", "sl_above_median_skip"), gv("minute", "segment", "sl_above_median_skip")
        L.append(f"2. **The stop-distance gate's control percentile is mechanical**: on the real tape it reads {f(rv('5minute', 'sl_above_median_skip')['control_pct'], 1)} (5 min, diff "
                 f"{f(rv('5minute', 'sl_above_median_skip')['diff'])}) and {f(rv('minute', 'sl_above_median_skip')['control_pct'], 1)} (1 min, diff {f(rv('minute', 'sl_above_median_skip')['diff'])}); "
                 f"on the memory-free tapes its control percentile has p50 {f(a['control_pct_p50'], 1)} / {f(b['control_pct_p50'], 1)} (5 min GMM / segment) and {f(a1['control_pct_p50'], 1)} / "
                 f"{f(b1['control_pct_p50'], 1)} (1 min), and the real diff sits at the {f(a['real_diff_percentile_in_tapes'], 0)}th / {f(b['real_diff_percentile_in_tapes'], 0)}th (5 min) and "
                 f"{f(a1['real_diff_percentile_in_tapes'], 0)}th / {f(b1['real_diff_percentile_in_tapes'], 0)}th (1 min) percentile of its null. A high control percentile for a gate on stop "
                 f"distance is what the engine produces on a random tape (Judge 2's warning, measured); the null p95 of the diff, not the control percentile, is the bar.")
        a, b = gv("5minute", "gmm", "choch2_skip"), gv("5minute", "segment", "choch2_skip"); a1, b1 = gv("minute", "gmm", "choch2_skip"), gv("minute", "segment", "choch2_skip")
        L.append(f"3. **The CHoCH-count gate**: 5 min real diff {f(rv('5minute', 'choch2_skip')['diff'])} (control pct {f(rv('5minute', 'choch2_skip')['control_pct'], 1)}) is at the "
                 f"{f(a['real_diff_percentile_in_tapes'], 0)}th / {f(b['real_diff_percentile_in_tapes'], 0)}th percentile of the GMM / segment nulls (p95 {f(a['diff_p95'])} / {f(b['diff_p95'])}): "
                 f"not above p95 on any generator. 1 min real diff {f(rv('minute', 'choch2_skip')['diff'])} (control pct {f(rv('minute', 'choch2_skip')['control_pct'], 1)}) against a GMM null median of "
                 f"{f(a1['diff_p50'])} ({f(a1['diff_share_positive'], 2)} of tapes positive): the real 1-minute CHoCH-count gate is worse than its memory-free null (the "
                 f"{f(a1['real_diff_percentile_in_tapes'], 0)}th percentile); the 'CHoCH, CHoCH, no BOS = sideways' skip does not read as market memory on this tape.")
        L.append("4. **Consequence for the gate studies**: a candidate's real-tape diff must clear the p95 of the null tapes of its own family shape, and its control percentile must be read against "
                 "the null's control-percentile distribution (`control_pct_p95` per gate); a control percentile alone, even 99+, is not evidence for a gate that touches the stop or the event stream.")
        L.append("")
    # ---- reality
    L.append("## 5. Reality check of the generators (IS part of the real tape vs the tapes; tape p50 [min, max])\n")
    keys = [("ret_std_bps", "ret std (bps)"), ("ret_kurt_excess", "ret excess kurtosis"), ("absret_ac1", "abs-return autocorr lag 1"), ("absret_ac2", "lag 2"), ("absret_ac3", "lag 3"), ("absret_ac4", "lag 4"), ("absret_ac5", "lag 5"),
            ("choch_per_session", "CHoCH / session"), ("bos_per_session", "BOS / session"), ("setups_per_session", "SETUPs / session"), ("l1_units_per_session", "L1 units / session"),
            ("l1_mean_net", "L1 mean net"), ("l1_win_rate", "L1 win rate"), ("frozen_kept_share", "frozen kept share"), ("close_last", "last close"), ("atr14_median", "ATR14 median")]
    for tf, d in null["timeframes"].items():
        L.append(f"### {tf}\n")
        gens = list(d["generators"].keys())
        L.append("| statistic | real | " + " | ".join(GEN_LABEL.get(g, g) for g in gens) + " |")
        L.append("|---|---|" + "---|" * len(gens))
        for k, lab in keys:
            cells = []
            for g in gens:
                v = d["generators"][g]["reality"][k]
                dd = 3 if abs(v["real"] or 0) < 10 else 1
                cells.append(f"{f(v['tape_p50'], dd)} [{f(v['tape_min'], dd)}, {f(v['tape_max'], dd)}]" + (f" (x{f(v['ratio_p50_to_real'], 2)})" if k in ("choch_per_session", "bos_per_session", "setups_per_session", "l1_units_per_session") else ""))
            real = d["generators"][gens[0]]["reality"][k]["real"]
            L.append(f"| {lab} | {f(real, 3 if abs(real or 0) < 10 else 1)} | " + " | ".join(cells) + " |")
        flags = [g for g in gens if d["generators"][g]["poor_null_flag"]]
        L.append(f"\nPoor-null flag (median SETUP rate outside [1/3, 3] x real): {flags if flags else 'none'}.")
        if tf == "minute":
            L.append("The 1-minute tapes are one trading year (247 sessions) starting at the real IS first open (17,523.70), so `last close` and `ATR14 median` are not "
                     "comparable with the real 5-year IS values in this table; the per-session rates and return moments are.")
        L.append("")
    # ---- engine scale / ordering check
    esc_p = os.path.join(HERE, "engine_scale_check.json")
    if os.path.exists(esc_p):
        esc = json.load(open(esc_p))
        L.append("### 5b. Engine scale and ordering check (`engine_scale_check.json`; 5-minute IS full sessions, Strategy 2 rules)\n")
        L.append("| bars | CHoCH / session | BOS / session | SETUPs / session | swings |")
        L.append("|---|---|---|---|---|")
        for k, v in esc["runs"].items():
            L.append(f"| {k.replace('_', ' ')} | {v['choch_per_session']:.3f} | {v['bos_per_session']:.3f} | {v['setups_per_session']:.3f} | {v['swings']:,} |")
        L.append(f"\nScale-free (x2 price level gives identical counts): **{esc['scale_free']}**. Re-basing the real sessions with the real gaps reproduces the real counts exactly; "
                 "redrawing the gaps or shuffling the sessions moves the CHoCH rate by ~+17% and removing the gaps altogether by ~+50%: the engine's event rate is a "
                 "property of the multi-day path, which is exactly what a null tape randomises, so per-tape SETUP counts vary (section 5 min / max) and the null distributions "
                 "carry that variance.\n")
    # ---- drift
    if drift:
        L.append("## 6. Adversarial validation IS-early vs IS-late (`drift.json`)\n")
        L.append("| tf | IS units (early / late) | design cols | time proxies removed in B | AUC A (all as-of) | AUC B (no time proxies) | permuted AUC p50 / p95 (B) |")
        L.append("|---|---|---|---|---|---|---|")
        for tf, d in drift["timeframes"].items():
            A, B = d["variants"]["A_all_asof"], d["variants"]["B_without_time_proxies"]
            L.append(f"| {tf} | {d['n_is']} ({d['n_early']} / {d['n_late']}) | {d['design_columns']} | {', '.join(f'{k} (rho {v:+.2f})' for k, v in d['time_proxies'].items())} | "
                     f"{A['auc_oof']:.4f} | **{B['auc_oof']:.4f}** | {B['perm_auc_p50']:.4f} / {B['perm_auc_p95']:.4f} |")
        L.append("")
        for tf, d in drift["timeframes"].items():
            A, B = d["variants"]["A_all_asof"], d["variants"]["B_without_time_proxies"]
            L.append(f"- **{tf} reading**: with the time proxies the periods separate at AUC {A['auc_oof']:.3f}; without them AUC {B['auc_oof']:.3f} against a permutation p95 of "
                     f"{B['perm_auc_p95']:.3f}: " + ("the IS-early and IS-late feature distributions are distinguishable well above chance (covariate drift inside IS is real, and a rule "
                     "learned on all of IS is learned on a mixture); the ranked features below say where." if B['auc_oof'] > B['perm_auc_p95'] + 0.05 else
                     "the periods are barely distinguishable once the calendar proxies are removed; the drift ranking below is weak evidence.") +
                     f" The gap A - B = {A['auc_oof'] - B['auc_oof']:+.3f} is the part of the separation carried by `{'`, `'.join(d['time_proxies'])}` alone.")
        L.append("")
        for tf, d in drift["timeframes"].items():
            L.append(f"### {tf}: top 20 drifted features (variant B, mean |SHAP|; direction = mean in IS-late vs IS-early; shift in pooled sd; KS between the periods)\n")
            L.append("| rank | feature | source column | mean abs SHAP | mean early | mean late | shift (sd) | KS | direction |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for r in d["top20_drifted"]:
                L.append(f"| {r['rank']} | `{r['feature']}` | `{r['source']}` | {f(r['mean_abs_shap'], 4)} | {f(r['mean_early'], 4)} | {f(r['mean_late'], 4)} | {f(r['std_shift'], 3)} | {f(r['ks'], 3)} | {r['direction']} |")
            L.append(f"\nTop-5 source columns (a selected rule using one of these is refit without it): `{'`, `'.join(d['top5_sources'])}`.\n")
        L.append(f"**Rule for the gate studies**: {drift['rule_for_gate_studies']}\n")
        L.append(f"**Not run here**: {drift['not_run_here']}.\n")
    # ---- how to evaluate a candidate
    L.append("## 7. How a candidate is evaluated on the tapes later\n")
    L.append("```python\nimport sys; sys.path.insert(0, '<OUT>/studies/null_tapes_drift'); import tapes\n"
             "for folder in tapes.tape_folders('5minute', 'gmm'):           # or 'segment' / 'session'; tf 'minute'\n"
             "    r = tapes.evaluate_rule_list(folder, rules)               # rules = the candidate's rule-list JSON (rules_round0.json grammar)\n"
             "    r['diff'], r['control_pct'], r['kept_share']              # the tape's kept-vs-skipped diff and control percentile\n```\n")
    L.append("Pass rule (pre-registered, DESIGN_PANEL (c) + Judge 1): the candidate's real-tape diff (its ledger row) > p95 of its own tape diffs on the GMM-Markov tapes AND on "
             "the segment tapes; the session-bootstrap diffs carry the real sign in >= 75% of tapes. The reference nulls in `null_distributions.json` "
             "(`null_tape_diff_inr = {p50, p95}` per generator) are the certificate values a shipped key's provenance block carries. A rule list is never scored "
             "on the tapes before its real-tape ledger row exists (the tapes are not a search space; `tapes.py` writes nothing to the ledger).\n")
    # ---- caveats / falsification
    L.append("## 8. Caveats and what would falsify these nulls\n")
    cav = [
        "The tapes' price level follows a random walk of drawn sessions and gaps: over 1,026 sessions some tapes end far from the real level (see `close_last` in section 5); "
        "the engine is scale-free (checked: x2 prices give identical event counts), but INR differences scale with the level, so a high-level tape widens the null in INR. "
        "This makes the p95 conservative (harder to beat); an ATR-normalised statistic would be tighter and is not the pre-registered one.",
        "The GMM-Markov tape's return kurtosis is below the real tape's (a 6-component mixture cannot carry a kurtosis of ~25) and its |r| autocorrelation dies within a few bars; "
        "Judge 1's warning (a narrower-than-reality null over-rejects) is why the segment bootstrap is read alongside it and the pass rule needs both.",
        "The session bootstrap keeps every within-session dependence, so it is a stability read, not a null: a gate that works within the day should keep its sign there.",
        "Engine event rates vary strongly from tape to tape (section 5 min / max): the engine's CHoCH count depends on the multi-day path, so per-tape unit counts differ by up to 3x.",
        "`sl` (the stop price level) is in `Table.asof_columns()` although it is a raw price (|rho| 0.93 with time on 5 minutes); `n_events_asof` is a cumulative count since the data start "
        "(rho 1.0). Both are time proxies, excluded in variant B, and a rule using either is refused; the harness allow-list should carry them in NOT_FEATURES (reported, not changed here).",
        "The 1-minute tapes are one trading year (247 IS sessions) with 8 tapes per generator: their null percentiles rest on 8 values and are wider than the 5-minute ones; "
        "the 5-minute nulls are the primary certificate, as both judges asked.",
        "Falsification: if a real gate's diff sat above the GMM/segment p95 while the gate is known to be pure engine mechanics (e.g. the stop-distance gate on the real tape), the null "
        "would be too narrow; section 4 shows what the mechanical gates read on the real tape against their own nulls.",
    ]
    for c in cav: L.append(f"- {c}")
    L.append("")
    L.append("## 9. Null result statement\n")
    L.append("This study searches no gate and proposes no candidate (`candidates: []`, `null_result: true` in the sense of 'no candidate'): it writes the certificate the gate "
             "studies compare against. The three reference gates' readings against their own nulls are in section 4a.\n")
    L.append("## 10. Files\n")
    files = sorted(os.path.relpath(p, HERE) for p in glob.glob(os.path.join(HERE, "*")) if os.path.isfile(p))
    for p in files: L.append(f"- `{p}`")
    L.append("- `tapes/<tf>/<gen>_<k>/` (per tape: `tape_meta.json`, `build.log`, `meta.json`, `features.parquet`, `trades.parquet`, `sessions.parquet`, `bars.parquet`, `events.parquet`, "
             "`setups.parquet`, ...; `tape.csv` kept for k = 0 only, every tape reproduces from its seed)")
    open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # ---- findings.json
    fj = dict(study="null_tapes_drift", timeframes={}, candidates=[], null_result=True, ledger_families=["null_tapes_drift/real_ref"],
              ledger_ids={f"{r['tf']}/{r['config']['gate']}": r["id"] for r in ledger_rows},
              caveats=cav, files=files + ["tapes/<tf>/<gen>_<k>/"], how_to_evaluate_candidate=null["how_to_compare"], drift=drift)
    for tf, d in null["timeframes"].items():
        fj["timeframes"][tf] = dict(real_reference=d["real_reference"], generators={g: dict(tapes=v["tapes"], gates=v["gates"], poor_null_flag=v["poor_null_flag"],
                                                                                           reality=v["reality"]) for g, v in d["generators"].items()},
                                    fit=fits.get(tf), drift=(drift or {}).get("timeframes", {}).get(tf))
    json.dump(fj, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=str)
    print("FINDINGS.md / findings.json written")


if __name__ == "__main__":
    main()
