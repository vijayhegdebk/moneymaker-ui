"""Assemble findings.json and FINDINGS.md from the study's output files (every number is copied from a file, none typed).
Pass rule for an exit candidate (fixed here, adapted from harness.GO to a policy-vs-Foundation difference on frozen entries;
written before the 1-minute learner A / B results were read, after the learner C results were): nested-CV diff > 0; CPCV 5th
percentile diff > 0; random-exit percentile >= 95; sign-flip (12 blocks) one-sided p <= 0.05 with >= 8 blocks positive;
90% block-bootstrap CI of the diff excludes 0; diff with the top 1% of per-trade gains removed > 0; PBO (family, 'diff') <= 0.2;
SPA p over the family <= 0.10."""
import sys, os, json, glob
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import exlib as X

TFS = ("minute", "5minute")
J = lambda p: json.load(open(os.path.join(HERE, p))) if os.path.exists(os.path.join(HERE, p)) else None
parity = J("parity.json"); variants = J("c_variants.json")
R = {tf: dict(grid=J(f"c_grid_check_{tf}.json"), csel=J(f"c_select_{tf}.json"), b=J(f"b_result_{tf}.json"), a=J(f"a_result_{tf}.json"), ev=J(f"eval_{tf}.json"),
              rules=J(f"exit_rules_{tf}.json"), table=pd.read_csv(os.path.join(HERE, f"eval_table_{tf}.csv")) if os.path.exists(os.path.join(HERE, f"eval_table_{tf}.csv")) else None) for tf in TFS}
ledger = X.read_exit_ledger()
fam_counts = {tf: {f: sum(1 for r in ledger if r["tf"] == tf and r["family"] == f) for f in sorted({r["family"] for r in ledger})} for tf in TFS}


def pass_rule(tf):
    c = R[tf]["csel"]; ev = R[tf]["ev"]; sf = c["sign_flip"]["C_nested"]["blocks"]
    row = next(r for r in ev["table"] if r["policy"].startswith("C nested")) if ev else None
    ch = {"nested_diff>0": (c["nested"]["diff"] > 0, c["nested"]["diff"]), "cpcv_p5_diff>0": (c["cpcv"]["diff_p5"] > 0, c["cpcv"]["diff_p5"]),
          "random_pct>=95": (c["nested"]["random_pct"] >= 95, c["nested"]["random_pct"]),
          "signflip_blocks_p1<=0.05": (sf["p_one_sided"] <= 0.05, sf["p_one_sided"]), "blocks_positive>=8/12": (sf["blocks_positive"] >= 8, sf["blocks_positive"]),
          "boot_ci90_excludes_0": (c["bootstrap_nested"]["diff_ci"][0] > 0, c["bootstrap_nested"]["diff_ci"]),
          "diff_top1_gains_removed>0": (row["diff_top1_gains_removed"] > 0, row["diff_top1_gains_removed"]) if row else (False, "pending (05_evaluate.py not run yet)"),
          "pbo<=0.2": (c["pbo"]["pbo"] <= 0.2, c["pbo"]["pbo"]), "spa_p<=0.10": (c["spa"]["spa_p"] <= 0.10, c["spa"]["spa_p"])}
    return all(v[0] for v in ch.values()), ch


def md_table(df, cols, fmt=None):
    fmt = fmt or {}
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    body = ""
    for _, r in df.iterrows():
        body += "| " + " | ".join(fmt.get(c, lambda v: "" if (isinstance(v, float) and np.isnan(v)) else str(v))(r[c]) for c in cols) + " |\n"
    return head + body


def keys_str(k): return f"stop {k['stop']} / scale {k['scale']} / trail {k['trail']} / time_stop {k['time_stop']} / choch {k['choch']}"


findings = dict(study="exit_policy", design="decision-making-2-exit-policy-fqi-exomdp (both judges' fixes; BRIEF addendum 6)", split="IS only", label="L1 entries (harness.load(tf), every IS unit)",
                timeframes={}, candidates=[], null_result=True, ledger_families=sorted({r["family"] for r in ledger}), caveats=[], files=sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "*")) if not p.endswith(".npz") and not os.path.isdir(p)))
md = ["# exit_policy — FINDINGS (IS only, 2026-09-29)", "",
      "Study `decision-making-2-exit-policy-fqi-exomdp` (DESIGN_PANEL, both judges' fixes) with BRIEF addendum 6: the managed replay is `lab.manage` / `lab.price_trade`, "
      "never a second implementation. Entries are frozen (every IS unit of `harness.load(tf)`, label L1, both timeframes); only the exit changes. No OOS row was read.", "",
      "## 1. Definitions (fixed before the numbers)", "",
      "- **Entries**: the L1 units, entry at the SETUP bar's close in the SETUP's direction; 1 min = Strategy 1 rules (prev_swing stop), 5 min = Strategy 2 rules (choch_candle stop).",
      "- **Square-off bar**: the last bar of the entry session opening at or before 15:25 (`lab.eod_cut`); **cap** = min(square-off bar, the contract's last candle) — every comparator is cut there.",
      "- **Foundation stop**: `features.sl`, engine touch convention (open beyond the stop -> fill at the open; wick touch -> fill at the stop; a session's first bar -> the close). Identical to `lab.manage`'s stop (proved on every IS trade, section 2).",
      "- **Extended trajectory** (learners A / B, the floor oracle): bars entry+1 .. J_end, J_end = the Foundation stop bar when it fires before the cap, else the cap. Exits before J_end are at the bar's close; at J_end the exit is the stop fill or the cap close. The engine's next-CHoCH exit is not applied (Exo-MDP: the tape does not react, so every exit policy is replayable).",
      "- **Value**: net INR per trade per lot = `lab.price_trade` arithmetic (lot 65, 5 pts slippage per side, `lab.trade_charges(ZERODHA_NFO_FUT)` on the slipped prices); a 3-lot ladder is reported per position and per lot (position net / 3); selection and every comparison use per lot.",
      "- **Oracle (free)**: the best close exit over entry+1 .. cap with no stop (an upper bound for any close-exit policy; a target filled intrabar can exceed it by at most that bar's range). **Oracle (floor)**: the best exit on the extended trajectory, ties -> earliest (learner B's target). **Exit regret** = oracle - policy.",
      "- **Random-exit control**: exit at a uniformly drawn bar of entry+1 .. cap at its close, 2,000 seeded draws (`fz|exit`); a policy's percentile = share of draws whose mean net per lot is below the policy's (+ half the ties).",
      "- **CHoCH against**: an `events.parquet` CHoCH with i > entry, i <= t, direction opposite to the position (known at its own bar under touch rules). **Time stop N**: exit at the close of bar entry+N if still open.",
      "- **Cut convention (learner C)**: the time stop and the CHoCH-against exit are a post-processing cut of `lab.manage`'s tranches: every tranche whose lab exit bar is later than the cut bar exits at the cut bar's close instead; a tranche the lab closed at or before the cut bar keeps its exit (the stop / target on the cut bar is assumed first, as `lab.manage` assumes the stop first on a candle); with both cuts on, the earlier bar wins.",
      "- **Learner C grid** (never shrunk): stop {35, 50, 75 pts, Foundation stop via `exact_R`} x scale_out {none, 1R, 2R, 3R, 4R with 1 lot (the target is the exit), ladder 1R/2R, ladder 2R/4R with 3 lots} x trail {none, (2,1), (2,2), (3,1), (3,2), (4,1), (4,2)} x time stop {none, 30, 60, 120 bars} x CHoCH-against {off, on}; square_off 15:25 always: 196 `lab.manage` positions x 8 cuts = **1,568 variants per timeframe**, each a strategy-row dict as `rl.py` builds it (lot 65, slippage 5, `position_json`, cap = the contract's last candle as `rl.contract_end`).",
      "- **Selection (C)**: nested in `harness.purged_splits` (argmax of the training fold's mean net per lot, applied to the test fold) and in the 66 CPCV splits -> 11 paths (`harness.cpcv_paths`). **Learners A / B**: 3 contiguous session-block folds (harness blocks 0-3 / 4-7 / 8-11), purge of training trades whose trajectory intersects the test fold's bars, 3-session embargo; B's p* by an inner 3-fold on the training fold; A's Q-ensembles refit per fold.",
      "- **Multiplicity**: every variant and every learner is a row of the append-only `exit_ledger.jsonl` + `vectors/*.npz` (harness-compatible per-session vectors: kept = the variant, skipped / all = the Foundation L1 exit on the same entries, so `harness.pbo(vecs, 'diff')`, `harness.spa`, `harness.effective_trials`, `harness.bootstrap_ci` read them unchanged). The harness ledger (`OUT/ledger/`) is for gates; this study writes to it only the gate x exit rows of section 8.",
      "- **Pass rule** for an exit candidate (adapted from `harness.GO` to a policy-vs-Foundation difference on frozen entries): nested-CV diff > 0; CPCV 5th percentile diff > 0; random-exit percentile >= 95; 12-block sign-flip one-sided p <= 0.05 with >= 8 blocks positive; 90% block-bootstrap CI of the diff excludes 0; diff with the top 1% of per-trade gains removed > 0; PBO <= 0.2; SPA p <= 0.10 over the family.", "",
      "## 2. Parity of the study's arithmetic with the lab (`parity.json`, `c_grid_check_*.json`)", ""]
for tf in TFS:
    p = parity[tf]; g = R[tf]["grid"]
    md += [f"**{tf}**: {p['units_is']} IS units, {p['bars']} bars. `price_np` == `lab.price_trade` on 500 random (trade, exit bar) pairs: {p['price_np_vs_lab_price_trade_500_pairs_identical']} (max |diff| {p['price_np_vs_lab_max_abs_diff']}); "
           f"== `l1_net_inr` on every L1 exit: {p['price_np_vs_l1_net_inr_all_within_0.005']}. Floor vs the L1 label: {p['l1_stop_loss_n']} stop_loss exits at the same bar and price: {p['floor_matches_l1_stop_bar_and_px']}; "
           f"{p['l1_cap_exits_n']} eod / expiry exits with no stop before the cap: {p['floor_no_stop_and_cap_on_l1_cap_exits']}; {p['l1_next_choch_n']} next_choch exits with the stop after the CHoCH bar (or the CHoCH on the cap bar, {p['l1_choch_exits_on_the_cap_bar']} cases): {p['floor_after_choch_or_choch_on_cap_bar_on_l1_choch_exits']}. "
           f"`exact_R` exact on {p['exact_R_trades']} / {p['units_is']} trades. **Floor vs `lab.manage` (Foundation stop, 1 lot, no target / trail, square_off 15:25) on every IS trade: {p['floor_vs_lab_manage_foundation_stop_mismatches']} mismatches** (bar, price, reason). "
           f"The grid's Foundation-stop-only variant reproduces the L1 label on its {g['l1_stop_or_cap_exits']} stop / cap exits (net within 0.005: {g['net_matches_l1_within_0_005']}, exit bar: {g['exit_bar_matches_l1']}); states per trade (extended trajectory): {p['states_mean_per_trade']} mean, {p['states_total']} in all; the stop fires on {p['floor_stop_hit_share']:.1%} of trajectories.", ""]
md += ["## 3. Learner C — the parametric grid by exact `lab.manage` replay", ""]
for tf in TFS:
    c = R[tf]["csel"]; ev = R[tf]["ev"]
    md += [f"### {tf} ({c['n']} IS units, {c['active_sessions']} active sessions, {c['variants']} variants; `c_variants_{tf}.csv`, `c_select_{tf}.json`)", "",
           f"Foundation L1 exit: mean **{c['foundation']['mean']}** INR per trade, random-exit percentile {c['foundation']['random_pct']}, regret vs the free oracle {c['foundation']['regret_free']} (floor oracle {c['foundation']['regret_floor']}). "
           f"Random control: mean of means {c['random_control']['mean']} (p5 {c['random_control']['p5']}, p95 {c['random_control']['p95']}). Oracles: free {c['oracle_free']['mean']}, floor {c['oracle_floor']['mean']}.", "",
           f"Variants above the Foundation exit in sample: {c['best_is']['variants_above_foundation']} / {c['variants']}. In-sample best (a trial): {keys_str(c['best_is']['keys'])}: mean {c['best_is']['mean']}, diff {c['best_is']['diff']} (t {c['best_is']['t']}), random pct {c['best_is']['random_pct']}, sign blocks {c['best_is']['sign_blocks']}/12, "
           f"bootstrap 90% CI of the diff {c['bootstrap_best']['diff_ci']}.", "",
           "Marginal means per lot by grid dimension (mean / best over the other dimensions):", ""]
    for dim, rows in c["marginals"].items():
        md += ["- **" + dim + "**: " + "; ".join(f"{r[dim]}: {r['mean']} (best {r['max']})" for r in rows)]
    md += ["", f"**Nested-CV pick** (`harness.purged_splits`, 12 folds): OOF mean **{c['nested']['mean']}**, diff vs Foundation **{c['nested']['diff']}** (t {c['nested']['t']}), random pct {c['nested']['random_pct']}, regret free {c['nested']['regret_vs_oracle_free']} / floor {c['nested']['regret_vs_oracle_floor']}, "
           f"sign blocks {c['nested']['sign_blocks']}/12, win rate {c['nested']['win_rate']}, PF {c['nested']['pf']}; bootstrap 90% CI of the diff {c['bootstrap_nested']['diff_ci']} (p(diff<=0) {c['bootstrap_nested']['diff_p_le0']}). Ledger id `{c['nested']['id']}`.", "",
           "| fold | pick | train mean | test mean | test Foundation |", "|---|---|---|---|---|"]
    md += [f"| {f['block']} | {keys_str(f['pick'])} | {f['train_mean']} | {f['test_mean']} | {f['test_fnd_mean']} |" for f in c["nested"]["folds"]]
    md += ["", f"**CPCV** (66 splits, 11 paths): diff median {c['cpcv']['diff_median']}, p5 {c['cpcv']['diff_p5']}, min {c['cpcv']['diff_min']}, share of paths positive {c['cpcv']['diff_share_positive']}; {c['cpcv']['distinct_picks']} distinct picks: "
           + "; ".join(f"{keys_str(p['keys'])} ({p['n_splits']} splits)" for p in c["cpcv"]["picks"]) + ".", "",
           f"**Multiplicity over the family** ({c['pbo']['candidates']} variants): PBO ('diff', {c['pbo']['partitions']} partitions) **{c['pbo']['pbo']}**, IS-best OOS below zero {c['pbo']['oos_best_below_zero']}, degradation slope {c['pbo']['degradation_slope']}; "
           f"SPA best gain {c['spa']['best_mean_gain']} per session (t {c['spa']['best_t']}), RC p {c['spa']['rc_p']}, **SPA p {c['spa']['spa_p']}**; effective trials {c['effective_trials']} on the kept_sum series (harness) and **{ev['effective_trials_selection_gain'] if ev else 'pending'}** on the variant-minus-Foundation series ({ev['distinct_gain_vectors'] if ev else 'pending'} distinct gain vectors; variants that differ only by an inert key — e.g. a 120-bar time stop on 5 min, a CHoCH exit that never fires — are identical by construction). "
           f"DSR of the in-sample best against {c['dsr_best'].get('n_trials')} trials: p {c['dsr_best'].get('p')}.", "",
           f"**ST9 R-ladder** (stop 50, 1R / 2R, trail 3R lag 1, 3 lots): per position {c['st9']['mean_per_position']}, per lot {c['st9']['mean']} (diff {c['st9']['diff']}, t {c['st9']['t']}), random pct {c['st9']['random_pct']}, sign blocks {c['st9']['sign_blocks']}/12, win rate {c['st9']['win_rate']}, PF {c['st9']['pf']}. "
           "It was tuned on 2026 (= this study's OOS window), so it cannot serve as an OOS comparator; here it is an IS comparator only.", "",
           "Paired sign-flip tests of policy - Foundation (12 blocks exact; sessions 2,000 flips): " + "; ".join(f"{k}: blocks p1 {v['blocks']['p_one_sided']} ({v['blocks']['blocks_positive']}/12 positive), sessions p1 {v['sessions']['p_one_sided']}" for k, v in c["sign_flip"].items()) + ".", ""]
md += ["## 4. Learner B — hindsight imitation (`b_result_*.json`, `b_oof_*.npz`)", ""]
for tf in TFS:
    b = R[tf]["b"]
    if not b: md += [f"**{tf}**: not run / not finished (see the log)."]; continue
    md += [f"**{tf}**: {b['states']} states over {b['trades']} trades ({len(b['features'])} features), HGB {b['hgb']}. OOF mean **{b['mean']}** vs Foundation {b['fnd_mean']} (diff {b['diff']}, t {b['t']}), random pct {b['random_pct']}, "
           f"regret free {b['regret_vs_oracle_free']} / floor {b['regret_vs_oracle_floor']}, early-exit share {b['exit_early_share']}, OOF AUC of 'this is the oracle bar' {b['auc_oof']}, sign-flip blocks p1 {b['sign_flip']['blocks']['p_one_sided']}, sessions p1 {b['sign_flip']['sessions']['p_one_sided']}. Ledger id `{b['ledger_id']}`. {b['seconds']} s, RSS {b['rss_mb']} MB.", "",
           "| fold | train / test trades (purged) | p* | inner value at p* / never-exit / Foundation | test mean | test Foundation | test AUC | early exits |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {f['fold']} | {f['train_trades']} / {f['test_trades']} ({f['purged']}) | {'never exit' if f['p_star_is_never_exit'] else f['p_star']} | {f['inner_value_at_p_star']} / {f['inner_value_never_exit']} / {f['inner_value_foundation']} | {f['test_mean']} | {f['test_fnd_mean']} | {f['test_auc']} | {f['exit_early_share']} |" for f in b["folds"]]
    md += [""]
md += ["## 5. Learner A — fitted Q-iteration, pessimistic ensemble (`a_result_*.json`, `a_oof_*.npz`)", ""]
for tf in TFS:
    a = R[tf]["a"]
    if not a:
        md += [f"**{tf}**: " + ("not run: the condition for the 1-minute FQI (learner B or C cutting the regret vs the oracle on IS CV, i.e. beating the Foundation exit OOF) was not met." if tf == "minute" else "not finished (see the log).")]; continue
    md += [f"**{tf}**: {a['decision_states']} decision states ({a['states']} states, {a['trades']} trades), {a['iterations']} iterations x {a['members']} members, kappa {a['kappa']}, HGB {a['hgb']}. OOF mean **{a['mean']}** vs Foundation {a['fnd_mean']} (diff {a['diff']}, t {a['t']}), random pct {a['random_pct']}, "
           f"regret free {a['regret_vs_oracle_free']} / floor {a['regret_vs_oracle_floor']}, early-exit share {a['exit_early_share']}, sign-flip blocks p1 {a['sign_flip']['blocks']['p_one_sided']}. Ledger id `{a['ledger_id']}`. {a['seconds']} s, RSS {a['rss_mb']} MB.", "",
           "| fold | train / test trades (purged) | test mean | test Foundation | early exits | exit-flag share of states | MAE of Q(s, exit) vs the exact exit value |", "|---|---|---|---|---|---|---|"]
    md += [f"| {f['fold']} | {f['train_trades']} / {f['test_trades']} ({f['purged']}) | {f['test_mean']} | {f['test_fnd_mean']} | {f['exit_early_share']} | {f['exit_flag_share']} | {f['q_exit_fit_mae']} |" for f in a["folds"]]
    md += [""]
md += ["## 6. Evaluation on IS CV — net per trade per lot on the same entries, all cut at 15:25 (`eval_table_*.csv`)", ""]
cols = ["policy", "mean_per_lot", "diff_vs_foundation", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor", "win_rate", "pf", "sign_blocks", "signflip_blocks_p1", "signflip_sessions_p1", "boot_diff_ci90", "diff_top1_gains_removed", "bars_held_mean"]
for tf in TFS:
    t = R[tf]["table"]
    if t is None: continue
    md += [f"### {tf}", "", md_table(t, [c for c in cols if c in t.columns]), ""]
md += ["The per-trade difference is slippage-invariant for the 1-lot policies (one round trip per lot each); at 8 pts per side every per-lot mean above moves by -390 INR (`mean_slip8` in the CSV).", "",
       "## 7. Distillation (`exit_rules_*.json`)", ""]
for tf in TFS:
    ev = R[tf]["ev"]
    if not ev: continue
    d = ev["distillation"]
    md += [f"**{tf}**: best learner by OOF mean = **{d['best_learner']}** ({d['best_learner_oof_mean']}); visited decision states {d['visited_decision_states']}, early-exit decisions {d['exit_decisions']}. "
           + (d.get("note") or f"Depth-3 tree fidelity: accuracy {d['fidelity_accuracy']}, exit recall {d['fidelity_exit_recall']}, exit precision {d['fidelity_exit_precision']}; the distilled policy replayed on IS (in sample for the tree): mean {d['distilled_policy_is_mean']}, diff vs Foundation {d['distilled_policy_diff_vs_foundation']}, random pct {d['distilled_policy_random_pct']}, early exits {d['distilled_early_exit_share']}; {d['rules_n']} exit rules."), ""]
    for r in ev["exit_rules"]: md += [f"- `{json.dumps(r['if'])}` -> exit_all (support {r['support']} states, exit share {r['exit_share']})"]
    md += [""]
md += ["The `exit_rules` list is a new key type (a per-bar rule evaluator the lab does not have): a user decision. Learner C's keys `{stop, scale_out, trail, square_off, time_stop_bars, exit_on_choch_against}` are the shippable form; `stop: foundation_sl` combined with targets / trail is also not an existing key (today `exit: \"strategy\"` gives the Foundation stop with the next-CHoCH exit, `exit: \"position\"` a fixed-points stop).", "",
       "## 8. Multiplication with the frozen ST7/ST8 gate (`harness.score` rows, family `exit_policy/gate_x_exit`)", ""]
for tf in TFS:
    ev = R[tf]["ev"]
    if not ev: continue
    fz = ev["frozen_gate_under_L1"][0] if ev["frozen_gate_under_L1"] else None
    if fz: md += [f"**{tf}** frozen gate under the L1 exit (harness id `{fz['id']}`): kept {fz['kept_n']}, kept mean {fz['kept_mean']}, skipped mean {fz['skipped_mean']}, diff {fz['diff']}, control pct {fz['control_pct']}.", ""]
    md += ["| exit applied | harness id | kept n | kept mean | skipped mean | diff | control pct | perm p | sign blocks | gate rows: Foundation -> exit mean (diff) | gate-row sign-flip blocks p1 | gate-row bootstrap CI | book net Foundation -> exit |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, m in ev["gate_multiplication"].items():
        g = m["gate_rows"]
        md += [f"| {name} | `{m['harness_id']}` | {m['kept_n']} | {m['kept_mean']} | {m['skipped_mean']} | {m['diff']} | {m['control_pct']} | {m['perm_p']} | {m['sign_blocks']} | {g['foundation_mean']} -> {g['exit_mean']} ({g['diff']}) | {g['signflip_blocks']['p_one_sided']} ({g['signflip_blocks']['blocks_positive']}/12) | {g['boot']['diff_ci']} | {g['book_net_foundation']} -> {g['book_net_exit']} |"]
    md += [""]
md += ["## 9. Pass rule, candidates, verdict", ""]
pending = [tf for tf in TFS if not R[tf]["ev"] or not R[tf]["b"] or not R[tf]["a"]]
if pending:
    md += [f"**STATUS: PRELIMINARY** — pending on {', '.join(pending)}: " + "; ".join(f"{tf}: " + ", ".join(k for k, v in (("05_evaluate.py (eval table, distillation, gate x exit)", R[tf]["ev"]), ("learner B", R[tf]["b"]), ("learner A", R[tf]["a"])) if not v) for tf in pending)
           + ". Learner C (grid, nested CV, CPCV, multiplicity), the yardsticks and the parity checks are final. Re-run `05_evaluate.py <tf>` when the learners finish, then `06_findings.py`.", ""]
for tf in TFS:
    ok, ch = pass_rule(tf)
    c = R[tf]["csel"]; ev = R[tf]["ev"] or {}
    findings["timeframes"][tf] = dict(n=c["n"], foundation_mean=c["foundation"]["mean"], foundation_random_pct=c["foundation"]["random_pct"], nested_pick=c["nested"], cpcv={k: v for k, v in c["cpcv"].items() if k != "per_path"},
                                      pbo=c["pbo"], spa=c["spa"], effective_trials_kept_sum=c["effective_trials"], effective_trials_gain=ev.get("effective_trials_selection_gain"), bootstrap_nested=c["bootstrap_nested"],
                                      st9=c["st9"], best_is=c["best_is"], random_control=c["random_control"], oracle_free=c["oracle_free"], oracle_floor=c["oracle_floor"], sign_flip=c["sign_flip"],
                                      learner_B={k: R[tf]["b"][k] for k in ("mean", "diff", "random_pct", "regret_vs_oracle_free", "exit_early_share", "auc_oof", "ledger_id")} if R[tf]["b"] else "pending",
                                      learner_A={k: R[tf]["a"][k] for k in ("mean", "diff", "random_pct", "regret_vs_oracle_free", "exit_early_share", "ledger_id")} if R[tf]["a"] else "pending",
                                      eval_table=ev.get("table", "pending"), distillation=ev.get("distillation", "pending"), exit_rules=ev.get("exit_rules", "pending"), gate_multiplication=ev.get("gate_multiplication", "pending"),
                                      pass_rule=dict(passed=ok, checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}), ledger_rows=fam_counts[tf], parity=parity[tf], grid_check=R[tf]["grid"])
    md += [f"**{tf}** — learner C nested pick: " + ", ".join(f"{k}: {'pass' if v[0] else 'FAIL'} ({v[1]})" for k, v in ch.items()) + f". **{'PASS' if ok else 'no candidate'}**.", ""]
    if ok:
        findings["null_result"] = False
        pick = c["nested"]["folds"][0]["pick"]
        findings["candidates"].append(dict(tf=tf, kind="exit (learner C keys)", config=dict(stop=pick["stop"], scale=pick["scale"], trail=pick["trail"], time_stop_bars=pick["time_stop"], exit_on_choch_against=pick["choch"], square_off="15:25"),
                                           provenance=dict(source="learned on IS 2021-10..2025-12", script="01_c_grid.py / 02_c_select.py", ledger_id=c["nested"]["id"], statistic=dict(nested_diff=c["nested"]["diff"], cpcv_p5=c["cpcv"]["diff_p5"], pbo=c["pbo"]["pbo"], spa_p=c["spa"]["spa_p"]))))
json.dump(findings, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md)[-6000:])
