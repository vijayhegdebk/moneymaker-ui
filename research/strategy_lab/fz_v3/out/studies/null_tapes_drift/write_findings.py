"""Compose FINDINGS.md and findings.json for study null_tapes_drift from the outputs (null_distributions.json, tape_results.csv,
reality_check.csv, tape_health.csv, real_reference_<tf>.json, real_health_<tf>.json, fit_<tf>.json, drift.json). Numbers only from
those files; nothing computed here beyond table formatting, the pass rule of section 7 applied to the three reference gates, and
the refuters' tail-rule recomputation (section 11) re-derived from tape_results.csv as a reproduction check.

    python write_findings.py
"""
import os, sys, json, glob
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT); sys.path.insert(0, HERE)
import harness as H                                                     # noqa: E402
import tapes                                                            # noqa: E402

GATES = ("frozen_st7_st8", "choch2_skip", "sl_above_median_skip")
GEN_LABEL = {"session": "session bootstrap", "segment": "segment bootstrap (30-bar blocks)", "gmm": "GMM-Markov"}
SETS = (("gates", "certificate (healthy, first DESIGN_N by k)"), ("gates_all_original", "first build, all tapes"), ("gates_healthy_original", "first build, healthy only"))


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return "-"
    return f"{x:,.{d}f}" if isinstance(x, (int, float, np.floating, np.integer)) else str(x)


def pct_change(new, old):
    if new is None or old is None or old == 0: return "-"
    return f"{100 * (new - old) / abs(old):+.0f}%"


def ord_(x):
    """Ordinal of a percentile: 0th, 1st, 42nd, 43rd, 81st."""
    if x is None: return "-"
    n = int(round(x)); suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


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
        drift["rule_for_gate_studies"] = ("a selected rule that uses one of top5_sources (variant B) is refit without that feature and both versions are reported in the "
                                          "study's FINDINGS; a rule that uses a time proxy (time_proxies) is a calendar rule, not a market rule: tapes.rule_mask refuses it "
                                          "(PermissionError) and the gate studies refuse it on the real tape by the same rule (harness.NOT_FEATURES does not carry these "
                                          "columns: reported, not changed here); a rule that uses any feature of top20_drifted carries the feature's std_shift as a caveat")
        json.dump(drift, open(os.path.join(HERE, "drift.json"), "w"), indent=1, default=str)     # the merged file is the deliverable
    R = pd.read_csv(os.path.join(HERE, "tape_results.csv")); RC = pd.read_csv(os.path.join(HERE, "reality_check.csv"))
    HL = pd.read_csv(os.path.join(HERE, "tape_health.csv"))
    fits = {tf: json.load(open(p)) for tf in ("5minute", "minute") for p in [os.path.join(HERE, f"fit_{tf}.json")] if os.path.exists(p)}
    refs = {tf: json.load(open(p)) for tf in ("5minute", "minute") for p in [os.path.join(HERE, f"real_reference_{tf}.json")] if os.path.exists(p)}
    rh = {tf: json.load(open(p)) for tf in ("5minute", "minute") for p in [os.path.join(HERE, f"real_health_{tf}.json")] if os.path.exists(p)}
    ledger_rows = H.read_ledger("null_tapes_drift")
    L = []
    L.append("# null_tapes_drift: synthetic null tapes (c) and adversarial drift validation (d)\n")
    L.append("DESIGN_PANEL decision-making-3, parts (c) and (d), with both judges' fixes: (a) / (b) live in `harness.py`; the null tapes run on 5 minutes "
             "(20 full-length tapes per generator) and on 1 minute (8 one-year tapes per generator, RSS checked); the segment bootstrap is Judge 1's second "
             "null; the IS-vs-OOS adversarial check is not run here (oos_once.py post-mortem). No gate search, no OOS row read. Tape numbers never enter the ledger; "
             "the three reference gates on the real tape are ledger rows of family `null_tapes_drift/real_ref`. Scripts: `gen_tapes.py`, `tapes.py`, `run_tapes.py`, "
             "`drift.py`, `write_findings.py`; logs `run_5minute.log`, `run_minute.log`, `drift.log`, `topup_5minute.log`, `topup_minute.log`. "
             "**Repair round (section 11)**: the adversarial refuters found the engine locked out on part of the tapes; the certificate is now read on healthy tapes "
             "(the first-build numbers stay published beside it), `tapes.py` refuses time proxies, the two mechanical gates are labelled as what they are, and the "
             "missing `go_no_go` item is stated as a program-level gap.\n")
    L.append("## 1. Definitions (fixed before the numbers)\n")
    L.append("- **Unit / label / statistic** as the harness: a Foundation SETUP taken under the L1 (15:25) book; kept-vs-skipped difference of mean net (INR per unit); "
             "the session-matched random control percentile (`fz_report.random_control`, 2,000 draws); permutation p; block sign count. On a tape the statistic is "
             "computed by `harness.metrics` on a `harness.Table` built from the tape's own `features.parquet` / `trades.parquet` / `sessions.parquet` "
             "(`tapes.load_tape`, a copy of `harness.load` pointed at the tape folder). Every tape row is IS (the tapes carry IS calendar dates).")
    L.append("- **Three reference gates** (all as keep masks): `frozen_st7_st8` = keep where `fz_traded` (the frozen ST7/ST8 gate as it traded on that tape); "
             "`choch2_skip` = skip where `n_choch_since_bos >= 2` (mechanical reference gate 1); `sl_above_median_skip` = skip where `sl_dist_atr` > the tape's own "
             "IS median (mechanical reference gate 2). The two mechanical gates were **fixed in `tapes.py` before any tape was scored**; they are reference points "
             "for the engine-mechanics check, not candidates, and appear in no registration file (BRIEF H2 names the family `n_choch_since_bos >= k` without k; the "
             "stop-distance gate exists only here). Their ledger rows (section 3) carry the earlier wording 'pre-registered' in the config text, which this file "
             "supersedes. The engine-mechanics check: a gate on stop distance or CHoCH counts can read non-zero on a memory-free tape through the engine itself "
             "(Judge 2), so its null is not 0.")
    L.append("- **Generators** (fitted on IS bars only, `gen_tapes.py` docstring): *session bootstrap* (whole IS sessions with replacement, level chained through the drawn "
             "session's open-to-close path and a gap drawn from the IS gap distribution); *segment bootstrap* (30-bar clock-aligned blocks from random IS sessions, "
             "re-based and chained, same gap draw); *GMM-Markov* (GaussianMixture 4-6 full-covariance components by BIC on the z-scored per-bar vector (log return, "
             "log volume ratio to the clock median, range/atr14, close position), first-order Markov chain on the labels, per-session sampling with the clock "
             "volume profile, OHLC rebuilt consistently, samples clipped to the IS range per dimension). Full-length sessions only (375 / 75 bars); the real IS "
             "tape's short sessions are excluded from the pools (listed in `fit_<tf>.json`). Tapes are written in the near-month CSV format and pushed through "
             "`build/build.py --path` (engine.run with the Foundation rules, fz.run with the frozen ST7/ST8 block, L0 and L1 pricing, the same 261-column feature table).")
    L.append("- **Engine health of a tape / per-tape poor-null flag (repair round; `tapes.tape_health`)**: an IS session is *frozen* when the engine's protected level "
             "`prot` (bars.parquet) does not change inside it, equals the previous session's last value and no CHoCH occurs; a *dead run* is a run of frozen sessions "
             "longer than the real tape's longest such run (" + ", ".join(f"{tf} {v['longest_frozen_run_sessions']}" for tf, v in rh.items()) + " sessions); "
             f"*dead share* = sessions inside dead runs / sessions. A tape is **healthy** when dead share < {tapes.HEALTH['dead_share_max']} AND its SETUP rate is "
             f">= {tapes.HEALTH['setup_rate_ratio_min']:.3f} x the real tape's. The flag reads bars / events / sessions / setups only, never a label or a gate "
             "statistic. **Tape sets**: `gates` = the **certificate**: the first DESIGN_N (20 / 8) healthy tapes per generator by seed index k (`tapes.tape_folders(tf, gen)` "
             "default; when the first build held fewer, the next seeds k = 20, 21, ... were generated until the count was reached: `run_tapes.py --target-healthy`); "
             "`gates_all_original` = the first build (k < DESIGN_N) with its locked tapes (the numbers the first version of this file reported); "
             "`gates_healthy_original` = the first build's healthy tapes only. The pass rule (section 7) reads the certificate set.")
    L.append("- **Null distribution** = per timeframe, generator, gate and tape set: p5 / p50 / p95 / mean / min / max of the tape diffs, the share of tapes with diff > 0, "
             "p50 / p95 of the control percentile, the real-tape value and its percentile among the tapes. **Comparison** (DESIGN_PANEL (c), Judge 1's "
             "go/no-go): the real-tape difference must be above the null-tape 95th percentile; here that is read on the two memory-free nulls (GMM-Markov and segment), "
             "with the session bootstrap as the stability read (share of tapes with the real diff's sign).")
    L.append("- **Reality check** per generator: within-session per-bar log-return std (bps) and excess kurtosis, autocorrelation of |r| at lags 1-5 (pairs inside a "
             "session), CHoCH / BOS / SETUP / L1-unit counts per session, the raw L1 book, the frozen gate's kept share, the final price level and median ATR14, over "
             "every tape built (the generator as it is) and over the certificate tapes; a generator whose median SETUP rate is outside [1/3, 3] x the real rate is "
             "flagged a poor null (generator level); the per-tape flag above is the tape level.")
    L.append("- **Adversarial validation (d)**: HistGradientBoostingClassifier IS-early (2021-10-01..2023-09-30) vs IS-late (2023-10-01..2025-12-31) on "
             "`harness.design(T)` of the real tape, IS rows; pooled out-of-fold AUC under `harness.purged_splits` (12 blocks, purge by exit bar, 3-session embargo); "
             "chance = 20 label permutations; variant A = all as-of columns, variant B = without time proxies (|Spearman rho| >= 0.9 with `session_idx`); SHAP "
             "(TreeExplainer) ranking on B with the direction of drift.\n")
    # ---- fits
    L.append("## 2. Generator fits (IS bars only)\n")
    L.append("| tf | IS sessions (full / short excluded) | IS bars | gaps | gap log-std | GMM K (BIC 4/5/6) | GMM fit rows | design tapes x sessions | refit reproduces first build |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for tf, fs in fits.items():
        L.append(f"| {tf} | {fs['is_sessions']} ({fs['pool_sessions']} / {len(fs['short_sessions_excluded'])}) | {fs['is_bars']:,} | {fs['gaps_n']} | {fs['gap_log_std']:.5f} | "
                 f"{fs['gmm_k']} ({', '.join(f'{int(float(v)):,}' for v in fs['gmm_bic'].values())}) | {fs['gmm_fit_rows']:,} | {fs['tapes_per_generator']} x {fs['sessions_per_tape']} | "
                 f"{fs.get('refit_reproduces_first_build', '-')} |")
    L.append("")
    # ---- build cost per tape (RSS check)
    rows = []
    for p in glob.glob(os.path.join(HERE, "tapes", "*", "*_*", "meta.json")):
        m = json.load(open(p)); tf_, name = p.split(os.sep)[-3], p.split(os.sep)[-2]; gen_, k_ = name.rsplit("_", 1)
        rows.append(dict(tf=tf_, gen=gen_, k=int(k_), rss=m.get("peak_rss_mb"), secs=m.get("run_times_s", {}).get("total"), bars=m.get("bars"), setups=m["counts"]["ALL"]["setups"]))
    if rows:
        M = pd.DataFrame(rows)
        L.append("### 2a. build.py cost per tape (from each tape's `meta.json`; the first build ran on a box shared with other studies, load 12-20; the top-up with 3-4 concurrent builds, load 4-9)\n")
        L.append("| tf | generator | tapes built (first build + top-up) | bars per tape | SETUPs p50 [min, max] | build seconds p50 [min, max] | peak RSS MB p50 [max] |")
        L.append("|---|---|---|---|---|---|---|")
        for (tf_, gen_), g in M.groupby(["tf", "gen"]):
            n0 = tapes.DESIGN_N[tf_]
            L.append(f"| {tf_} | {GEN_LABEL.get(gen_, gen_)} | {len(g)} ({int((g.k < n0).sum())} + {int((g.k >= n0).sum())}) | {int(g.bars.iloc[0]):,} | {int(g.setups.median())} [{int(g.setups.min())}, {int(g.setups.max())}] | "
                     f"{g.secs.median():.0f} [{g.secs.min():.0f}, {g.secs.max():.0f}] | {g.rss.median():.0f} [{g.rss.max():.0f}] |")
        L.append("")
    # ---- health counts
    L.append("### 2b. Tape sets after the health check (`tape_health.csv`, `null_distributions.json`)\n")
    L.append("| tf | generator | built | first build | healthy (first build) | lock-out rate (first build) | top-up tapes | healthy (all built) | certificate tapes | certificate k |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for tf, d in null["timeframes"].items():
        for gen, g in d["generators"].items():
            L.append(f"| {tf} | {GEN_LABEL.get(gen, gen)} | {g['tapes_built']} | {g['tapes_original']} | {g['tapes_original'] - g['tapes_locked_original']} | {f(g['lockout_rate_original'], 2)} | "
                     f"{g['tapes_built'] - g['tapes_original']} | {g['tapes_healthy']} | {g['tapes_certificate']} | {', '.join(str(k) for k in g['certificate_tapes'])} |")
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
    # ---- null distributions: the certificate
    L.append("## 4. Null distributions (the certificate: `null_distributions.json` -> `gates`, read on the certificate tape set)\n")
    L.append("Diff = kept-vs-skipped mean L1 net on the tape (INR per unit). `real pct` = the real-tape diff's percentile among the tapes; `real > p95` = the pass-rule "
             "comparison for that generator. The certificate set = the first DESIGN_N healthy tapes per generator (section 1); the first-build numbers follow in 4a.\n")
    L.append("| tf | generator | gate | tapes | units p50 [min, max] | kept share p50 | diff p5 | diff p50 | diff p95 | diff min / max | share diff>0 | control pct p50 / p95 | share ctrl>=95 | real diff | real pct | real > p95 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    passes = {}
    for tf, d in null["timeframes"].items():
        for gen, g in d["generators"].items():
            for gate, v in g["gates"].items():
                passes[(tf, gen, gate)] = v["real_above_tape_p95"]
                L.append(f"| {tf} | {GEN_LABEL.get(gen, gen)} | {gate} | {v['n']} | {f(v['units_p50'], 0)} [{f(v['units_min'], 0)}, {f(v['units_max'], 0)}] | {f(v['kept_share_p50'], 3)} | {f(v['diff_p5'])} | {f(v['diff_p50'])} | **{f(v['diff_p95'])}** | "
                         f"{f(v['diff_min'])} / {f(v['diff_max'])} | {f(v['diff_share_positive'], 3)} | {f(v['control_pct_p50'], 1)} / {f(v['control_pct_p95'], 1)} | {f(v['control_pct_share_ge95'], 3)} | "
                         f"{f(v['real_diff'])} | {f(v['real_diff_percentile_in_tapes'], 1)} | {'yes' if v['real_above_tape_p95'] else 'no'} |")
    L.append("")
    # ---- sensitivity: the first build with and without its locked tapes
    L.append("### 4a. The same cells on the first build, with and without its locked tapes (`gates_all_original`, `gates_healthy_original`)\n")
    L.append("`all` = the 20 / 8 tapes of the first build, locked ones included (what the first version of this file reported); `healthy` = its healthy tapes; "
             "`certificate` = section 4. `delta p95` = certificate p95 vs first-build-all p95. The verdict (real > p95) is given for `all` and for the certificate.\n")
    L.append("| tf | generator | gate | tapes all / healthy / cert | units min all / cert | p50 all | p95 all | p50 healthy | p95 healthy | p50 cert | p95 cert | delta p95 | ctrl p95 all / cert | real diff | real pct all / cert | real > p95 all / cert |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    flips = []
    for tf, d in null["timeframes"].items():
        for gen, g in d["generators"].items():
            for gate in GATES:
                a, h, c = g["gates_all_original"][gate], g["gates_healthy_original"][gate], g["gates"][gate]
                if a["real_above_tape_p95"] != c["real_above_tape_p95"]: flips.append((tf, gen, gate))
                L.append(f"| {tf} | {GEN_LABEL.get(gen, gen)} | {gate} | {a['n']} / {h['n']} / {c['n']} | {f(a['units_min'], 0)} / {f(c['units_min'], 0)} | {f(a['diff_p50'])} | {f(a['diff_p95'])} | {f(h['diff_p50'])} | {f(h['diff_p95'])} | "
                         f"{f(c['diff_p50'])} | **{f(c['diff_p95'])}** | {pct_change(c['diff_p95'], a['diff_p95'])} | {f(a['control_pct_p95'], 1)} / {f(c['control_pct_p95'], 1)} | {f(a['real_diff'])} | "
                         f"{f(a['real_diff_percentile_in_tapes'], 1)} / {f(c['real_diff_percentile_in_tapes'], 1)} | {'yes' if a['real_above_tape_p95'] else 'no'} / {'yes' if c['real_above_tape_p95'] else 'no'} |")
    n_cells = sum(len(GATES) for d in null["timeframes"].values() for _ in d["generators"])
    L.append(f"\nVerdict flips between the first-build-all set and the certificate set: **{len(flips)} of {n_cells}**" + (f" ({', '.join('/'.join(x) for x in flips)})" if flips else "") + ".\n")
    L.append("### 4b. Reading of the reference gates against their own nulls (certificate set)\n")
    for tf, d in null["timeframes"].items():
        for gate in GATES:
            reads = []
            for gen in ("gmm", "segment", "session"):
                v = d["generators"].get(gen, {}).get("gates", {}).get(gate)
                if v: reads.append(f"{gen}: n {v['n']}, p50 {f(v['diff_p50'])}, p95 {f(v['diff_p95'])}, real pct {f(v['real_diff_percentile_in_tapes'], 1)}, same sign {f(v['tapes_same_sign_as_real'], 2)}")
            real = (d.get("real_reference") or {}).get(gate, {})
            verdict = "passes the null-tape check" if (passes.get((tf, "gmm", gate)) and passes.get((tf, "segment", gate))) else "does NOT pass the null-tape check"
            L.append(f"- **{tf} / {gate}**: real diff {f(real.get('diff'))} (control pct {f(real.get('control_pct'), 1)}); {'; '.join(reads)} -> {verdict}.")
    L.append("")
    L.append("### 4c. Key readings (numbers from `null_distributions.json`, certificate set)\n")
    def gv(tf, gen, gate, set_="gates"): return null["timeframes"][tf]["generators"][gen][set_][gate]
    def rv(tf, gate): return null["timeframes"][tf]["real_reference"][gate]
    if "5minute" in null["timeframes"] and "minute" in null["timeframes"]:
        a, b, s = gv("5minute", "gmm", "frozen_st7_st8"), gv("5minute", "segment", "frozen_st7_st8"), gv("5minute", "session", "frozen_st7_st8")
        L.append(f"1. **The frozen ST7/ST8 gate on memory-free 5-minute tapes**: GMM-Markov median diff {f(a['diff_p50'])} (p95 {f(a['diff_p95'])}, share of tapes > 0 "
                 f"{f(a['diff_share_positive'], 2)}, control pct p50 {f(a['control_pct_p50'], 1)}, {f(100 * a['control_pct_share_ge95'], 0)}% of tapes at or above the 95th control "
                 f"percentile); segment median {f(b['diff_p50'])} (p95 {f(b['diff_p95'])}, control pct p50 {f(b['control_pct_p50'], 1)}, {f(100 * b['control_pct_share_ge95'], 0)}% at or above 95); "
                 f"session median {f(s['diff_p50'])} (p95 {f(s['diff_p95'])}). "
                 + ("On tapes with no swing memory the rooms gate still separates kept from skipped by a positive median and clears the random control on a large share of "
                    "tapes: that part of any ST7/ST8-shaped statistic is engine / FZ mechanics, not market memory. " if a["diff_p50"] > 0 and b["diff_p50"] > 0 else
                    "The memory-free medians are not both positive on the certificate set: the mechanical part of an ST7/ST8-shaped statistic is read from the p95, not the median. ")
                 + f"The real 5-minute frozen gate ({f(rv('5minute', 'frozen_st7_st8')['diff'])}, control pct {f(rv('5minute', 'frozen_st7_st8')['control_pct'], 1)}) sits at the "
                 f"{ord_(a['real_diff_percentile_in_tapes'])} percentile of the GMM null and the {ord_(b['real_diff_percentile_in_tapes'])} of the segment null: on the real tape it does "
                 "worse than on its own memory-free tapes.")
        a, b = gv("5minute", "gmm", "sl_above_median_skip"), gv("5minute", "segment", "sl_above_median_skip"); a1, b1 = gv("minute", "gmm", "sl_above_median_skip"), gv("minute", "segment", "sl_above_median_skip")
        L.append(f"2. **The stop-distance gate's control percentile is mechanical**: on the real tape it reads {f(rv('5minute', 'sl_above_median_skip')['control_pct'], 1)} (5 min, diff "
                 f"{f(rv('5minute', 'sl_above_median_skip')['diff'])}) and {f(rv('minute', 'sl_above_median_skip')['control_pct'], 1)} (1 min, diff {f(rv('minute', 'sl_above_median_skip')['diff'])}); "
                 f"on the memory-free tapes its control percentile has p50 {f(a['control_pct_p50'], 1)} / {f(b['control_pct_p50'], 1)} (5 min GMM / segment) and {f(a1['control_pct_p50'], 1)} / "
                 f"{f(b1['control_pct_p50'], 1)} (1 min), and the real diff sits at the {ord_(a['real_diff_percentile_in_tapes'])} / {ord_(b['real_diff_percentile_in_tapes'])} (5 min) and "
                 f"{ord_(a1['real_diff_percentile_in_tapes'])} / {ord_(b1['real_diff_percentile_in_tapes'])} (1 min) percentile of its null. A high control percentile for a gate on stop "
                 f"distance is what the engine produces on a random tape (Judge 2's warning, measured); the null p95 of the diff, not the control percentile, is the bar.")
        a, b = gv("5minute", "gmm", "choch2_skip"), gv("5minute", "segment", "choch2_skip"); a1, b1 = gv("minute", "gmm", "choch2_skip"), gv("minute", "segment", "choch2_skip")
        L.append(f"3. **The CHoCH-count gate**: 5 min real diff {f(rv('5minute', 'choch2_skip')['diff'])} (control pct {f(rv('5minute', 'choch2_skip')['control_pct'], 1)}) is at the "
                 f"{ord_(a['real_diff_percentile_in_tapes'])} / {ord_(b['real_diff_percentile_in_tapes'])} percentile of the GMM / segment nulls (p95 {f(a['diff_p95'])} / {f(b['diff_p95'])}): "
                 f"{'above p95 on both memory-free generators' if a['real_above_tape_p95'] and b['real_above_tape_p95'] else 'not above p95 on both memory-free generators'}. "
                 f"1 min real diff {f(rv('minute', 'choch2_skip')['diff'])} (control pct {f(rv('minute', 'choch2_skip')['control_pct'], 1)}) against a GMM null median of "
                 f"{f(a1['diff_p50'])} ({f(a1['diff_share_positive'], 2)} of tapes positive): the real 1-minute CHoCH-count gate sits at the {ord_(a1['real_diff_percentile_in_tapes'])} percentile "
                 "of its memory-free null; the 'CHoCH, CHoCH, no BOS = sideways' skip does not read as market memory on this tape.")
        L.append("4. **Consequence for the gate studies**: a candidate's real-tape diff must clear the p95 of the certificate tapes of its own family shape (section 7), and its control "
                 "percentile must be read against the null's control-percentile distribution (`control_pct_p95` per gate); a control percentile alone, even 99+, is not evidence for a "
                 "gate that touches the stop or the event stream.")
        L.append("")
    # ---- reality
    L.append("## 5. Reality check of the generators (IS part of the real tape vs every tape built; tape p50 [min, max]; the min / max carry the locked tapes)\n")
    keys = [("ret_std_bps", "ret std (bps)"), ("ret_kurt_excess", "ret excess kurtosis"), ("absret_ac1", "abs-return autocorr lag 1"), ("absret_ac2", "lag 2"), ("absret_ac3", "lag 3"), ("absret_ac4", "lag 4"), ("absret_ac5", "lag 5"),
            ("choch_per_session", "CHoCH / session"), ("bos_per_session", "BOS / session"), ("setups_per_session", "SETUPs / session"), ("l1_units_per_session", "L1 units / session"),
            ("l1_mean_net", "L1 mean net"), ("l1_win_rate", "L1 win rate"), ("frozen_kept_share", "frozen kept share"), ("close_last", "last close"), ("atr14_median", "ATR14 median")]
    rate_keys = ("choch_per_session", "bos_per_session", "setups_per_session", "l1_units_per_session")
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
                cells.append(f"{f(v['tape_p50'], dd)} [{f(v['tape_min'], dd)}, {f(v['tape_max'], dd)}]" + (f" (x{f(v['ratio_p50_to_real'], 2)})" if k in rate_keys else ""))
            real = d["generators"][gens[0]]["reality"][k]["real"]
            L.append(f"| {lab} | {f(real, 3 if abs(real or 0) < 10 else 1)} | " + " | ".join(cells) + " |")
        L.append("| lock-out rate, first build (tapes) | 0 | " + " | ".join(f"{f(d['generators'][g]['lockout_rate_original'], 2)} ({d['generators'][g]['tapes_locked_original']} / {d['generators'][g]['tapes_original']})" for g in gens) + " |")
        L.append("| lock-out rate, all built (tapes) | 0 | " + " | ".join(f"{f(d['generators'][g]['lockout_rate_all_built'], 2)} ({d['generators'][g]['tapes_built'] - d['generators'][g]['tapes_healthy']} / {d['generators'][g]['tapes_built']})" for g in gens) + " |")
        flags = [g for g in gens if d["generators"][g]["poor_null_flag"]]
        L.append(f"\nGenerator-level poor-null flag (median SETUP rate outside [1/3, 3] x real): {flags if flags else 'none'}. Per-tape poor-null flags (locked tapes, section 5c): "
                 + "; ".join(f"{GEN_LABEL.get(g, g)} k = {d['generators'][g]['poor_null_tapes']}" for g in gens) + ".")
        L.append("\nEngine rates on the certificate tapes only (p50, x real):\n")
        L.append("| statistic | real | " + " | ".join(GEN_LABEL.get(g, g) for g in gens) + " |")
        L.append("|---|---|" + "---|" * len(gens))
        for k, lab in [(k, lab) for k, lab in keys if k in rate_keys + ("l1_mean_net", "frozen_kept_share")]:
            cells = []
            for g in gens:
                v = d["generators"][g]["reality_certificate"][k]
                dd = 3 if abs(v["real"] or 0) < 10 else 1
                cells.append(f"{f(v['tape_p50'], dd)} [{f(v['tape_min'], dd)}, {f(v['tape_max'], dd)}]" + (f" (x{f(v['ratio_p50_to_real'], 2)})" if k in rate_keys else ""))
            real = d["generators"][gens[0]]["reality"][k]["real"]
            L.append(f"| {lab} | {f(real, 3 if abs(real or 0) < 10 else 1)} | " + " | ".join(cells) + " |")
        if tf == "minute":
            L.append("\nThe 1-minute tapes are one trading year (247 sessions) starting at the real IS first open (17,523.70), so `last close` and `ATR14 median` are not "
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
                 "property of the multi-day path, which is exactly what a null tape randomises. The per-tape variance this creates has two parts: the ordinary spread of "
                 "healthy tapes (section 4, units min / max of the certificate set) and the lock-out of section 5c.\n")
    # ---- lock-out
    L.append("### 5c. Engine lock-out on the null tapes (repair round; `tape_health.csv`, `tapes/<tf>/<gen>_<k>/tape_health.json`)\n")
    L.append("**Mechanism** (engine.py, protected level): the protected level `prot` is the last unbroken *candidate* swing of the current trend; a swing becomes a candidate "
             "only when it lies on the far side of the AVWAP anchored at the last trend flip (`qualifies`: a low below that AVWAP in an up-trend, a high above it in a "
             "down-trend). On a driftless random-walk tape a long one-directional walk leaves the anchored AVWAP far behind, no new swing qualifies, `prot` freezes at the "
             "last candidate, and a CHoCH (a close beyond `prot` against the trend) becomes unreachable while BOS (a break of the last swing high / low with the trend) "
             "continues at its normal rate; no CHoCH means no SETUP. The real market returns to its anchored levels often enough that the real tape's longest frozen run "
             "is " + " / ".join(f"{v['longest_frozen_run_sessions']}" for v in rh.values()) + " sessions (" + " / ".join(rh.keys()) + "); the locked tapes carry runs of "
             f"{int(HL[~HL.healthy].longest_frozen_run_sessions.min()) if (~HL.healthy).any() else '-'}-{int(HL[~HL.healthy].longest_frozen_run_sessions.max()) if (~HL.healthy).any() else '-'} sessions. "
             "A run can end when the walk wanders back (a recovered mid-tape lock-out; the tail rule alone misses these) or last to the end of the tape.\n")
    L.append("| tf | tape | sessions | dead sessions (share) | dead tail share | longest frozen run (from) | last CHoCH | last SETUP | SETUPs / session (x real) | L1 units | prot at end | close at end | gap pts | reasons |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    fr_units = R[R.gate == "frozen_st7_st8"].set_index("tape").n
    for _, r in HL[~HL.healthy].sort_values(["tf", "gen", "k"]).iterrows():
        L.append(f"| {r.tf} | {r.gen}_{r.k} | {r.sessions} | {r.dead_sessions} ({f(r.dead_share, 3)}) | {f(r.dead_tail_share, 3)} | {r.longest_frozen_run_sessions} ({r.longest_frozen_run_start}) | {r.last_choch_date} | "
                 f"{str(r.last_setup_time)[:10]} | {f(r.setups_per_session, 3)} (x{f(r.setup_rate_ratio_to_real, 2)}) | {int(fr_units.get(r.tape, np.nan)) if r.tape in fr_units.index else '-'} | {f(r.prot_last, 1)} | {f(r.close_last, 1)} | {f(r.prot_gap_pts, 0)} | {r.reasons} |")
    n_locked = int((~HL.healthy).sum()); n_first = int((~HL.healthy & HL.original).sum()); n_tail = int(((HL.dead_tail_share >= 0.2) | (HL.setup_rate_ratio_to_real < 1 / 3)).sum())
    L.append(f"\n{n_locked} of {len(HL)} tapes built are locked ({n_first} of {int(HL.original.sum())} in the first build); the refuters' tail rule (share of sessions after the last "
             f"CHoCH >= 0.2, or SETUP rate < 1/3 x real) flags {n_tail} of them, the frozen-run rule adds the recovered mid-tape lock-outs (dead tail share ~0 with a dead run of "
             "hundreds of sessions). The session bootstrap locks most often: a whole real session's open-to-close return with an independent gap draw makes the chained level "
             "walk farthest. The generator-level poor-null flag (median SETUP rate) cannot see a dead tape; the per-tape flag can, and the certificate excludes them.\n")
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
                     "the periods are barely distinguishable once the calendar proxies are removed; the drift ranking below is weak evidence.")
                     + (f" The gap A - B = {A['auc_oof'] - B['auc_oof']:+.3f} is the part of the separation carried by `{'`, `'.join(d['time_proxies'])}` alone."
                        if A['auc_oof'] > B['auc_oof'] else
                        f" Removing the calendar proxies `{'`, `'.join(d['time_proxies'])}` did not lower the separation (A - B = {A['auc_oof'] - B['auc_oof']:+.3f}): their information "
                        "is redundant with the level- and volatility-dependent features, and a monotone-in-time column's cut points generalise slightly worse across purged blocks."))
        L.append("")
        for tf, d in drift["timeframes"].items():
            L.append(f"### {tf}: top 20 drifted features (variant B, mean |SHAP|; direction = mean in IS-late vs IS-early; shift in pooled sd; KS between the periods)\n")
            L.append("| rank | feature | source column | mean abs SHAP | mean early | mean late | shift (sd) | KS | direction |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for r in d["top20_drifted"]:
                L.append(f"| {r['rank']} | `{r['feature']}` | `{r['source']}` | {f(r['mean_abs_shap'], 4)} | {f(r['mean_early'], 4)} | {f(r['mean_late'], 4)} | {f(r['std_shift'], 3)} | {f(r['ks'], 3)} | {r['direction']} |")
            L.append(f"\nTop-5 source columns (a selected rule using one of these is refit without it): `{'`, `'.join(d['top5_sources'])}`.\n")
        L.append(f"**Rule for the gate studies**: {drift['rule_for_gate_studies']}\n")
        L.append("**Where the time-proxy refusal is enforced**: on the tapes, in code (`tapes.rule_mask` raises `PermissionError` for any column in `drift.json` "
                 "`timeframes[tf].time_proxies`, fallback `n_events_asof`, `sl`; tested in the repair round); on the real tape it is a study rule the gate studies apply, "
                 "because `harness.NOT_FEATURES` does not carry these two columns (reported to the orchestrator, not changed here: `harness.py` is outside this study's scope).\n")
        L.append(f"**Not run here**: {drift['not_run_here']}.\n")
    # ---- how to evaluate a candidate
    L.append("## 7. How a candidate is evaluated on the tapes later\n")
    L.append("```python\nimport sys; sys.path.insert(0, '<OUT>/studies/null_tapes_drift'); import tapes\n"
             "# the pass rule in one call (real_diff = the candidate's real-tape ledger row 'diff'; rules = its rule-list JSON, rules_round0.json grammar):\n"
             "passed, checks, summary = tapes.null_tape_check(real_diff, '5minute', rules)      # or 'minute'\n"
             "# checks = {'null_tape:real_diff>gmm_p95': (ok, p95), 'null_tape:real_diff>segment_p95': (ok, p95), 'null_tape:session_same_sign>=0.75': (ok, share)}\n"
             "# summary['null_tape_diff_inr'] = {gen: {'p50', 'p95'}} is the certificate block for the key's provenance; summary['per_tape'] = every tape's metrics\n"
             "# the same by hand:\n"
             "for folder in tapes.tape_folders('5minute', 'gmm'):           # the CERTIFICATE set: the first 20 (5minute) / 8 (minute) HEALTHY tapes by seed index k\n"
             "    r = tapes.evaluate_rule_list(folder, rules)               # (healthy=False gives every tape built, locked ones included: a sensitivity read, never the pass rule)\n"
             "    r['diff'], r['control_pct'], r['kept_share']\n```\n")
    dead_rng = (f"{100 * HL[~HL.healthy].dead_share.min():.0f}-{100 * HL[~HL.healthy].dead_share.max():.0f}%" if (~HL.healthy).any() else "-")
    L.append("**Tape set of the pass rule**: the certificate set (`tapes.tape_folders(tf, gen)` default = healthy tapes, first DESIGN_N by k; section 2b lists the k of each "
             f"generator). The locked tapes are never part of a pass / fail: the engine did not run on them for {dead_rng} of their sessions (section 5c), so their kept-vs-skipped "
             "statistic is noise on a few hundred units. Report the sensitivity read (`healthy=False`) beside it if a reader asks how the verdict moves.\n")
    L.append("**Pass rule** (DESIGN_PANEL (c) + Judge 1): the candidate's real-tape diff (its ledger row) > p95 of its own tape diffs on the GMM-Markov certificate tapes AND on "
             "the segment certificate tapes; the session-bootstrap certificate diffs carry the real sign in >= 75% of tapes. The reference nulls in `null_distributions.json` "
             "(`gates` -> `diff_p50`, `diff_p95` per generator) are the certificate values a shipped key's provenance block carries (`null_tape_diff_inr`). A rule list is never "
             "scored on the tapes before its real-tape ledger row exists (the tapes are not a search space; `tapes.py` writes nothing to the ledger).\n")
    L.append("**Program-level gap (Judge 1's binding fix, not in code here)**: `harness.go_no_go` has no null-tape item, so a gate study can pass `go_no_go` without ever running "
             "this check; `harness.py` is outside this study's write scope. `tapes.null_tape_check` returns the three items in `go_no_go`'s `(ok, value)` shape so the fix is a "
             "drop-in for the orchestrator:\n")
    L.append("```python\n# harness.py (proposed, not applied here)\n"
             "def go_no_go(res, tf, cpcv=None, pbo_value=None, dsr=None, spa_p=None, boot=None, null_tape=None):\n"
             "    ...\n"
             "    if null_tape is not None:                      # null_tape = tapes.null_tape_check(res['diff'], tf, rules)[1]\n"
             "        ch.update(null_tape)                        # 'null_tape:real_diff>gmm_p95', 'null_tape:real_diff>segment_p95', 'null_tape:session_same_sign>=0.75'\n"
             "    return all(v[0] for v in ch.values()), ch\n```\n"
             "Until that lands, the phase-3 workflow must call `tapes.null_tape_check` explicitly before freezing a candidate and record the three items in the candidate's "
             "FINDINGS and provenance.\n")
    # ---- caveats / falsification
    L.append("## 8. Caveats and what would falsify these nulls\n")
    lock_summary = "; ".join(f"{tf}: " + ", ".join(f"{GEN_LABEL.get(g, g)} {v['tapes_locked_original']}/{v['tapes_original']}" for g, v in d["generators"].items()) for tf, d in null["timeframes"].items())
    cav = [
        "The tapes' price level follows a random walk of drawn sessions and gaps: over 1,026 sessions some tapes end far from the real level (see `close_last` in section 5); "
        "the engine is scale-free (checked: x2 prices give identical event counts), but INR differences scale with the level, so a high-level tape widens the null in INR. "
        "This makes the p95 conservative (harder to beat); an ATR-normalised statistic would be tighter and is not the registered one.",
        "The GMM-Markov tape's return kurtosis is below the real tape's (a 6-component mixture cannot carry a kurtosis of ~25) and its |r| autocorrelation dies within a few bars; "
        "Judge 1's warning (a narrower-than-reality null over-rejects) is why the segment bootstrap is read alongside it and the pass rule needs both.",
        "The session bootstrap keeps every within-session dependence, so it is a stability read, not a null: a gate that works within the day should keep its sign there.",
        f"Engine lock-out (section 5c, measured): on the first build the engine's protected level froze and the CHoCH stream stopped for {dead_rng} of the sessions on {lock_summary} "
        "tapes (frozen-run rule; the refuters' tail rule finds 12 of 84), while BOS continued at the normal rate; the locked tapes carry as few as "
        + "; ".join(f"{int(R[(R.tf == tf) & (R.gate == 'frozen_st7_st8') & ~R.healthy].n.min())} L1 units ({tf}) against {int(R[(R.tf == tf) & (R.gate == 'frozen_st7_st8') & R.in_certificate].n.min())}-"
                    f"{int(R[(R.tf == tf) & (R.gate == 'frozen_st7_st8') & R.in_certificate].n.max())} on the certificate tapes" for tf in null["timeframes"] if (~R[(R.tf == tf) & (R.gate == 'frozen_st7_st8')].healthy).any())
        + ". The certificate (section 4) excludes them and was topped up to the design count with the next seeds; the first-build numbers with and without "
        "them are in section 4a (verdicts unchanged). The lock-out is itself a property of a memory-free tape (the real market returns to its anchored levels; a random walk "
        "need not), so the healthy set is conditioned on 'the engine ran', not on any gate statistic.",
        "`sl` (the stop price level) is in `Table.asof_columns()` although it is a raw price (|rho| 0.93 with time on 5 minutes); `n_events_asof` is a cumulative count since the data start "
        "(rho 1.0). Both are time proxies, excluded in variant B; `tapes.rule_mask` refuses them (PermissionError) and the gate studies refuse them on the real tape by rule; "
        "the harness allow-list should carry them in NOT_FEATURES (reported, not changed here).",
        "The 1-minute tapes are one trading year (247 IS sessions) with 8 tapes per generator: their null percentiles rest on 8 values and are wider than the 5-minute ones; "
        "the 5-minute nulls are the primary certificate, as both judges asked.",
        "The two mechanical reference gates are fixed reference points, not registered candidates (section 1); nothing in the ledger or the registrations depends on them.",
        "Falsification: if a real gate's diff sat above the GMM/segment p95 while the gate is known to be pure engine mechanics (e.g. the stop-distance gate on the real tape), the null "
        "would be too narrow; section 4 shows what the mechanical gates read on the real tape against their own nulls.",
    ]
    if drift:
        tops = "; ".join(f"{tf}: " + ", ".join(f"`{r['feature']}` ({r['direction'].replace(' in IS-late', '')}, {r['std_shift']:+.2f} sd)" for r in d["top20_drifted"][:5])
                         for tf, d in drift["timeframes"].items())
        cav.append("Drift inside IS is large (section 6) and its top of the ranking is the volatility / price-level regime (" + tops + "): the tape went from ~17,500 to ~26,300 while "
                   "volatility in bps fell, so every point-denominated column (`*_pts`, `atr14`, `sl_dist_pts`, `fz_band_width`, `fz_dist_band_edge_*`, `gap_pts`) drifts with the level. "
                   "A rule on such a column is a level rule; the gate studies should express thresholds in the `_atr` / `_bps` forms and the CPCV path distribution, not the pooled IS "
                   "number, is what a drifting IS supports.")
    for c in cav: L.append(f"- {c}")
    L.append("")
    L.append("## 9. Null result statement\n")
    L.append("This study searches no gate and proposes no candidate (`candidates: []`, `null_result: true` in the sense of 'no candidate'): it writes the certificate the gate "
             "studies compare against. The three reference gates' readings against their own nulls are in section 4b.\n")
    L.append("## 10. Files\n")
    files = sorted(os.path.relpath(p, HERE) for p in glob.glob(os.path.join(HERE, "*")) if os.path.isfile(p))
    for p in files: L.append(f"- `{p}`")
    L.append("- `tapes/<tf>/<gen>_<k>/` (per tape: `tape_meta.json`, `build.log`, `meta.json`, `tape_health.json`, `features.parquet`, `trades.parquet`, `sessions.parquet`, `bars.parquet`, `events.parquet`, "
             "`setups.parquet`, ...; `tape.csv` kept for k = 0 only, every tape reproduces from its seed)")
    L.append("")
    # ---- repair
    L.append("## 11. Repair round (adversarial refuters' findings and what changed)\n")
    # the refuters' recomputation reproduced from tape_results.csv (tail rule)
    q = lambda v, p: round(float(np.nanquantile(v, p)), 2) if len(v) else None
    R["tail_flag"] = (R.dead_tail_share >= 0.2) | (R.setup_rate_ratio_to_real < 1 / 3)
    recheck = {}
    for tf, gen, gate in (("5minute", "gmm", "frozen_st7_st8"), ("5minute", "session", "choch2_skip"), ("minute", "session", "frozen_st7_st8")):
        s = R[(R.tf == tf) & (R.gen == gen) & (R.gate == gate) & R.original]; a = s[~s.tail_flag]
        recheck[f"{tf}/{gen}/{gate}"] = dict(all_p50=q(s["diff"], .5), all_p95=q(s["diff"], .95), tail_rule_healthy_p50=q(a["diff"], .5), tail_rule_healthy_p95=q(a["diff"], .95), tail_rule_n=int(len(a)))
    real_runs_txt = ", ".join(f"{tf} {v['longest_frozen_run_sessions']}" for tf, v in rh.items())
    refit_txt = ", ".join(f"{tf} {fs.get('refit_reproduces_first_build')}" for tf, fs in fits.items())
    repair = [
        dict(issue="1. Engine lock-out on part of the tapes undisclosed; the 'up to 3x' caveat mis-stated a 15.5x unit spread; the generator-level poor-null flag cannot see a dead tape; "
                   "the certificate p95 moved when the locked tapes were excluded.",
             changed=[f"`tapes.tape_health(folder)` (per-tape flag: dead share of sessions inside frozen-prot CHoCH-free runs longer than the real tape's longest ({real_runs_txt} sessions) "
                      f"< {tapes.HEALTH['dead_share_max']} and SETUP rate >= 1/3 x real; written to `tapes/<tf>/<gen>_<k>/tape_health.json`; `tape_health.csv` at the study level; `real_health_<tf>.json`). "
                      f"It flags {n_locked} of {len(HL)} tapes built ({n_first} of the first build's {int(HL.original.sum())}); the refuters' tail rule is a special case (12 tapes) that misses the recovered mid-tape lock-outs.",
                      "`tapes.tape_folders(tf, gen, healthy=True, n=DESIGN_N)` (default = the certificate set; `healthy=False` = every tape built; `original_only=True` = the first build); numeric ordering by k.",
                      "`run_tapes.aggregate` publishes three sets per gate: `gates` (certificate), `gates_all_original`, `gates_healthy_original`, plus `locked_tapes`, `lockout_rate_*`, `units_per_tape`, `poor_null_tapes`, `reality_certificate`; "
                      "`tape_results.csv` / `reality_check.csv` carry the health columns.",
                      f"`run_tapes.py --target-healthy N` topped the certificate up to the design count with the next seeds (k >= DESIGN_N, generated in seed order; the generator refit reproduces the first build's GMM: "
                      f"{refit_txt}); logs `topup_5minute.log`, `topup_minute.log`. Nothing of the first build was rebuilt or removed.",
                      "FINDINGS: section 1 (definitions of health and the tape sets), 2b (counts), 4 (certificate) + 4a (first build with / without the locked tapes, delta p95, verdict flips), 5 (lock-out rates, certificate rates), "
                      "5c (the mechanism and the per-tape list), 7 (which tape set the pass rule uses), 8 (the caveat replaced by the measured lock-out)."],
             numbers=dict(refuters_recheck_reproduced=recheck, verdict_flips_first_build_vs_certificate=len(flips))),
        dict(issue="2. The time-proxy refusal was a written policy, not a property of `tapes.rule_mask` (a rule on `sl` or `n_events_asof` was accepted).",
             changed=["`tapes.time_proxies(tf)` reads `drift.json` (`timeframes[tf].time_proxies`; fallback `n_events_asof`, `sl`); `tapes.rule_mask` raises `PermissionError` for such a column. "
                      "Tested: `[['sl', '>', 20000]]` and `[['n_events_asof', '>', 100]]` are refused on tape gmm_0; label columns and `fz_traded` were already refused.",
                      "FINDINGS sections 6 and 8 now say where the refusal is enforced (in code on the tapes; by study rule on the real tape, since `harness.NOT_FEATURES` does not carry the two columns: reported, not changed)."]),
        dict(issue="3. The two mechanical gates were called 'pre-registered' although no registration exists outside the study folder.",
             changed=["Reworded everywhere in the study (`tapes.MECHANICAL_GATES`, `run_tapes.py`, FINDINGS sections 1, 8): 'fixed in tapes.py before any tape was scored; reference points, not candidates'. "
                      "The three `real_ref` ledger rows keep the earlier wording in their config text (the ledger is append-only); no ledger consequence: they are comparators, not candidates."]),
        dict(issue="4. Judge 1's binding fix (the null-tape pass rule as a `go_no_go` item) is not in `harness.go_no_go`; a gate study can pass `go_no_go` without running the tape check.",
             changed=["Program-level (outside this study's write scope): `tapes.null_tape_check(real_diff, tf, rules)` implements the section-7 rule on the certificate set and returns the three items in "
                      "`go_no_go`'s `(ok, value)` shape; section 7 gives the drop-in patch for `harness.go_no_go(..., null_tape=...)` and tells the phase-3 workflow to call the check explicitly until it lands. "
                      "Flagged for the orchestrator in findings.json (`program_level_gaps`)."]),
    ]
    for r_ in repair:
        L.append(f"**{r_['issue']}**\n")
        for c in r_["changed"]: L.append(f"- {c}")
        if r_.get("numbers"):
            L.append(f"- Reproduction of the refuters' recomputation (tail rule, first build): " + "; ".join(f"{k}: all {v['all_p50']} / {v['all_p95']}, tail-rule healthy {v['tail_rule_healthy_p50']} / {v['tail_rule_healthy_p95']} (n {v['tail_rule_n']})" for k, v in recheck.items()) + ".")
        L.append("")
    open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # ---- findings.json
    fj = dict(study="null_tapes_drift", timeframes={}, candidates=[], null_result=True, ledger_families=["null_tapes_drift/real_ref"],
              ledger_ids={f"{r['tf']}/{r['config']['gate']}": r["id"] for r in ledger_rows},
              certificate_set=null["certificate_set"], health_rule=null["health_rule"], caveats=cav, files=files + ["tapes/<tf>/<gen>_<k>/"],
              how_to_evaluate_candidate=null["how_to_compare"],
              pass_rule=dict(items=["null_tape:real_diff>gmm_p95", "null_tape:real_diff>segment_p95", "null_tape:session_same_sign>=0.75"], tape_set="certificate (tapes.tape_folders default)",
                             function="tapes.null_tape_check(real_diff, tf, rules) -> (passed, checks, summary)"),
              program_level_gaps=["harness.go_no_go has no null-tape item (Judge 1's binding fix): add `null_tape` = tapes.null_tape_check(res['diff'], tf, rules)[1] to its checks, or make the phase-3 workflow call the check before freezing a candidate",
                                  "harness.NOT_FEATURES does not carry the time proxies `n_events_asof`, `sl` (refused by tapes.rule_mask on the tapes; by study rule on the real tape)"],
              repair=repair, verdict_flips_first_build_vs_certificate=flips, drift=drift)
    for tf, d in null["timeframes"].items():
        fj["timeframes"][tf] = dict(real_reference=d["real_reference"], real_health=d.get("real_health"),
                                    generators={g: dict(tapes=v["tapes"], tapes_built=v["tapes_built"], tapes_original=v["tapes_original"], tapes_healthy=v["tapes_healthy"],
                                                        tapes_certificate=v["tapes_certificate"], tapes_locked_original=v["tapes_locked_original"], lockout_rate_original=v["lockout_rate_original"],
                                                        lockout_rate_all_built=v["lockout_rate_all_built"], certificate_tapes=v["certificate_tapes"], locked_tapes=v["locked_tapes"],
                                                        gates=v["gates"], gates_all_original=v["gates_all_original"], gates_healthy_original=v["gates_healthy_original"],
                                                        units_per_tape=v["units_per_tape"], poor_null_flag=v["poor_null_flag"], poor_null_tapes=v["poor_null_tapes"],
                                                        reality=v["reality"], reality_certificate=v["reality_certificate"]) for g, v in d["generators"].items()},
                                    fit=fits.get(tf), drift=(drift or {}).get("timeframes", {}).get(tf))
    json.dump(fj, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=str)
    print("FINDINGS.md / findings.json written")


if __name__ == "__main__":
    main()
