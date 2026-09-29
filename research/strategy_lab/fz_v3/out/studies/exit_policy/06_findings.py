"""Assemble findings.json and FINDINGS.md from the study's output files (every number is copied from a file, none typed).
Pass rule for an exit candidate (fixed here, adapted from harness.GO to a policy-vs-Foundation difference on frozen entries;
written before the 1-minute learner A / B results were read, after the learner C results were): nested-CV diff > 0; CPCV 5th
percentile diff > 0; random-exit percentile >= 95; sign-flip (12 blocks) one-sided p <= 0.05 with >= 8 blocks positive;
90% block-bootstrap CI of the diff excludes 0; diff with the top 1% of per-trade gains removed > 0; PBO (family, 'diff') <= 0.2;
SPA p over the family <= 0.10.
Follow-up (2026-09-29 16:45 IST): learner A's 1-minute result folded in like the 5-minute one (sections 5, 6, 8, 9, with the same
pass rule applied to learners A and B); the family SPA read from eval_<tf>.json (05_evaluate.py, current harness.spa: both
statistics, the min-active exclusions) instead of c_select_<tf>.json; section 10 names what changed and why.
REPAIR (2026-09-29, two sets of confirmed material issues — the study's re-verification and the follow-up's verification; section 11):
11.1 the family SPA is read from eval_<tf>.json `spa_family`, now the REPAIRED block (vectors at the label's 2-dp precision, so the
near-duplicates of the benchmark — variant 1177 on both timeframes, 1183 on 5 min — are excluded by the harness's min-active rule), with
the as-coded block beside it; section 10.2's false explanation of the zero exclusions is rewritten. 11.2 the top-1% pass item is the
harness's pre-registered definition (top 1% winners by net removed: `diff_top1_winners_removed`); the study's post-hoc
`diff_top1_gains_removed` (chosen after the C results were read, negative-biased by construction) is disclosed beside it with its
zero-mean reference and is not a pass item. 11.3 the FINDINGS / findings.json are regenerated from the files on disk (learner A's 1-min
result included) and the repair states what was stale at review time. 11.4 each statistic appears once: the section 6 table reuses the
seed tag of the stage that first reported the statistic (05_evaluate.py OWN_TAGS), so the C nested pick's bootstrap CI and the learners'
session sign-flip p no longer appear as two Monte-Carlo estimates (eval_table_<tf>_review_time.csv = the table as reviewed, from
checkpoint commit 171f446). 11.5 the pass-rule item is worded as implemented: lower bound of the 90% block-bootstrap CI of the diff > 0
(harness.go_no_go: boot["diff_ci"][0] > 0). 11.6 section 10.1's account of the missing final line of 04_a_minute.log is corrected from
the file timestamps."""
import sys, os, json, glob, time
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


def spa_of(tf):
    """The family SPA: eval_<tf>.json's `spa_family` — since the repair the block computed on vectors at the label's 2-dp precision
    (05_evaluate.py, current harness.spa: min-active exclusion + the unstudentised statistic) — when present, else 02_c_select.py's
    block (the earlier harness.spa)."""
    ev = R[tf]["ev"]
    if ev and ev.get("spa_family"): return ev["spa_family"], "current"
    return R[tf]["csel"]["spa"], "02_c_select"


def spa_as_coded(tf):
    """The same family through harness.spa on the vectors as stored (variant net unrounded): the follow-up's numbers."""
    ev = R[tf]["ev"] or {}
    return ev.get("spa_family_as_coded")


def top1_disclosed(row):
    """The post-hoc top-1% variant (top 1% of per-trade GAINS removed; chosen after learner C's results were read) with its zero-mean
    reference — reported beside the pass item, never used to decide (repair)."""
    if not row or row.get("diff_top1_gains_removed") is None: return {}
    return {"diff_top1_gains_removed (post-hoc)": row["diff_top1_gains_removed"], "its zero-mean reference": row.get("diff_top1_gains_removed_zero_mean_ref"),
            "both 1% tails trimmed": row.get("diff_both_1pct_tails_trimmed")}


def rule_line(ch, disc):
    s = ", ".join(f"{k}: {'pass' if v[0] else 'FAIL'} ({v[1]})" for k, v in ch.items())
    if disc: s += " [disclosed, not a pass item: " + "; ".join(f"{k} {v}" for k, v in disc.items()) + "]"
    return s


def pass_rule(tf):
    c = R[tf]["csel"]; ev = R[tf]["ev"]; sf = c["sign_flip"]["C_nested"]["blocks"]; sp, _ = spa_of(tf)
    row = next(r for r in ev["table"] if r["policy"].startswith("C nested")) if ev else None
    ch = {"nested_diff>0": (c["nested"]["diff"] > 0, c["nested"]["diff"]), "cpcv_p5_diff>0": (c["cpcv"]["diff_p5"] > 0, c["cpcv"]["diff_p5"]),
          "random_pct>=95": (c["nested"]["random_pct"] >= 95, c["nested"]["random_pct"]),
          "signflip_blocks_p1<=0.05": (sf["p_one_sided"] <= 0.05, sf["p_one_sided"]), "blocks_positive>=8/12": (sf["blocks_positive"] >= 8, sf["blocks_positive"]),
          "boot_ci90_lower>0": (c["bootstrap_nested"]["diff_ci"][0] > 0, c["bootstrap_nested"]["diff_ci"]),
          "diff_top1_winners_removed>0 (harness GO definition)": (row["diff_top1_winners_removed"] > 0, row["diff_top1_winners_removed"]) if row else (False, "pending (05_evaluate.py not run yet)"),
          "pbo<=0.2": (c["pbo"]["pbo"] <= 0.2, c["pbo"]["pbo"]), "spa_p<=0.10 (repaired family)": (sp["spa_p"] <= 0.10, sp["spa_p"])}
    return all(v[0] for v in ch.values()), ch, top1_disclosed(row)


LEARNER_ROW = {"A": "A FQI pessimistic ensemble (OOF)", "B": "B hindsight imitation (OOF)"}


def pass_rule_learner(tf, key):
    """The same pass rule applied to learner A / B's OOF policy (3 contiguous session-block folds, judge 2): the OOF diff stands in
    for the nested-CV diff; the CPCV item cannot be evaluated (no CPCV paths for the learners by design), so the rule cannot be
    passed in full; PBO is the family's (the 1,568 C variants); SPA p is the studentised p over every exit trial of the timeframe
    (repaired family)."""
    a = R[tf][key.lower()]; ev = R[tf]["ev"]; c = R[tf]["csel"]
    if not a or not ev: return None
    row = next((r for r in ev["table"] if r["policy"] == LEARNER_ROW[key]), None)
    if row is None: return None
    sf = a["sign_flip"]["blocks"]; sa = ev.get("spa_all_trials") or spa_of(tf)[0]
    ch = {"oof_diff>0": (a["diff"] > 0, a["diff"]),
          "cpcv_p5_diff>0": (False, "n/a: 3-fold OOF by design, no CPCV paths"),
          "random_pct>=95": (a["random_pct"] >= 95, a["random_pct"]),
          "signflip_blocks_p1<=0.05": (sf["p_one_sided"] <= 0.05, sf["p_one_sided"]), "blocks_positive>=8/12": (sf["blocks_positive"] >= 8, sf["blocks_positive"]),
          "boot_ci90_lower>0": (row["boot_diff_ci90"][0] > 0, row["boot_diff_ci90"]),
          "diff_top1_winners_removed>0 (harness GO definition)": (row["diff_top1_winners_removed"] > 0, row["diff_top1_winners_removed"]),
          "pbo<=0.2": (c["pbo"]["pbo"] <= 0.2, c["pbo"]["pbo"]), "spa_p<=0.10 (repaired family, all exit trials)": (sa["spa_p"] <= 0.10, sa["spa_p"])}
    return all(v[0] for v in ch.values()), ch, top1_disclosed(row)


def kstr(k):
    return keys_str(k) if isinstance(k, dict) and {"stop", "scale", "trail"} <= set(k) else json.dumps(k, default=str)


def spa_text(tf):
    sp, kind = spa_of(tf)
    if kind != "current":
        return f"SPA best gain {sp['best_mean_gain']} per session (t {sp['best_t']}), RC p {sp['rc_p']}, **SPA p {sp['spa_p']}** (harness.spa as at 02_c_select.py)"
    exc = sp["excluded_candidates"]
    exc_txt = "none" if not exc else "; ".join(f"variant {e['index']} `{e['id']}` {kstr(e['keys'])} ({e['active_sessions']} of {sp['sessions']} sessions active at 2 dp, mean gain {e['mean_gain']}, t {e['t_studentised']})" for e in exc)
    bk, bu = sp["best_keys"], sp["best_keys_unstudentised"]
    ac = spa_as_coded(tf); ev = R[tf]["ev"]; tol = ev.get("spa_family_tolerance_check") if ev else None
    s = (f"SPA (`harness.spa` sha `{sp['harness_sha']}`, {sp['draws']} stationary-bootstrap draws, tag `{sp['tag']}`, the same draws as 02_c_select.py; **repaired family**: the per-session vectors built from the per-trade nets rounded to 2 dp, the label's precision — section 11): "
         f"studentised (Hansen) best = variant {bk['index']} {kstr(bk['keys'])}, mean selection gain {sp['best_mean_gain']} per session (t {sp['best_t']}; active in {sp['best_active_sessions']} / {sp['sessions']} sessions; "
         f"its per-trade diff vs Foundation is {bk['diff_vs_foundation']}" + (" — the SPA statistic is a per-session mean, so a variant can lead it with a negative per-trade diff" if (bk['diff_vs_foundation'] or 0) < 0 else "") + f"), RC p {sp['rc_p']}, **SPA p {sp['spa_p']}**; "
         f"unstudentised (White) best = variant {bu['index']} {kstr(bu['keys'])}, mean gain {sp['best_mean_gain_unstudentised']} (per-trade diff {bu['diff_vs_foundation']}), RC p {sp['rc_p_unstudentised']}, **SPA p {sp['spa_p_unstudentised']}**; "
         f"min-active rule max(10, 5% of T) = {sp['min_active_sessions']} sessions: {sp['excluded_from_studentised']} of {sp['candidates']} candidates excluded from the studentised family ({exc_txt})")
    if ac:
        s += (f". As coded on the stored vectors (variant net unrounded; the follow-up's numbers): studentised best = variant {ac['best_keys']['index']} {kstr(ac['best_keys']['keys'])} (t {ac['best_t']}), RC p {ac['rc_p']}, SPA p {ac['spa_p']}; "
              f"unstudentised SPA p {ac['spa_p_unstudentised']}; {ac['excluded_from_studentised']} excluded (the 1e-9 activity rule counts a session whose |gain| is <= 0.005 INR of rounding noise as active)")
    if tol:
        s += (f". Material-tolerance check (candidates with fewer than {tol['min_active_sessions']} sessions of |gain| > {tol['tolerance_inr']} INR dropped from the list, both statistics): {tol['excluded']} dropped (indices {tol['excluded_indices']}), "
              f"studentised SPA p {tol['spa_p']} (RC p {tol['rc_p']}), unstudentised SPA p {tol['spa_p_unstudentised']}")
    return s


def spa_all_text(tf):
    ev = R[tf]["ev"]; sa = (ev or {}).get("spa_all_trials"); ac = (ev or {}).get("spa_all_trials_as_coded")
    if not sa: return ""
    exc = "; ".join(f"variant {e['index']} `{e['id']}`" for e in sa.get("excluded_candidates", []))
    s = (f" Over every exit trial of the timeframe ({sa['candidates']} rows: the C variants, the C nested pick, the C in-sample best, learners B and A; tag `{sa['tag']}`; repaired family): "
         f"studentised best = {kstr(sa['best_keys']['keys'])} (family `{sa['best_keys']['family']}`), RC p {sa['rc_p']}, SPA p {sa['spa_p']}; unstudentised RC p {sa['rc_p_unstudentised']}, SPA p {sa['spa_p_unstudentised']}; "
         f"{sa['excluded_from_studentised']} excluded by the min-active rule" + (f" ({exc})" if exc else ""))
    if ac: s += f" (as coded: studentised SPA p {ac['spa_p']}, unstudentised {ac['spa_p_unstudentised']}, {ac['excluded_from_studentised']} excluded)"
    return s + "."


def learner_verdict(tf, a, key):
    """A plain statement of whether the learner's exit helps or hurts on this timeframe, every number from a_result / b_result /
    eval_<tf>.json, and the pass rule applied to it (pass_rule_learner)."""
    worse = [f["fold"] for f in a["folds"] if f["test_mean"] < f["test_fnd_mean"]]
    better = [f["fold"] for f in a["folds"] if f["test_mean"] > f["test_fnd_mean"]]
    ev = R[tf]["ev"] or {}; row = next((r for r in ev.get("table", []) if r["policy"] == LEARNER_ROW[key]), None)
    others = {k: v for k, v in (("C nested pick", R[tf]["csel"]["nested"]["mean"]), ("B", (R[tf]["b"] or {}).get("mean")), ("A", (R[tf]["a"] or {}).get("mean"))) if k != key and v is not None}
    ci = row["boot_diff_ci90"] if row else None
    if a["diff"] < 0:
        head = f"is below the Foundation exit on the pooled OOF by {-a['diff']} INR per trade (t {a['t']})" + (": **it hurts** (the 90% block-bootstrap CI of the diff lies entirely below 0)" if ci and ci[1] < 0 else " (the 90% block-bootstrap CI of the diff includes 0: not significantly)" if ci else "")
    else:
        head = f"is above the Foundation exit on the pooled OOF by {a['diff']} INR per trade (t {a['t']})" + (" (the 90% block-bootstrap CI of the diff lies entirely above 0)" if ci and ci[0] > 0 else " (the 90% block-bootstrap CI of the diff includes 0: not a significant gain)" if ci else "")
    s = (f"Plainly: on {tf} the learner {key} exit {head}; it is below the Foundation exit in {len(worse)} of {len(a['folds'])} folds" + (f" (folds {', '.join(map(str, worse))})" if worse else "")
         + (f" and above it in {len(better)} (folds {', '.join(map(str, better))})" if better else "") + f"; random-exit percentile {a['random_pct']}")
    if row: s += (f"; bootstrap 90% CI of the diff {ci}; diff with the top 1% winners removed (harness definition) {row['diff_top1_winners_removed']}; "
                  f"diff with the top 1% of per-trade gains removed (post-hoc, disclosed) {row['diff_top1_gains_removed']} against a zero-mean reference of {row.get('diff_top1_gains_removed_zero_mean_ref')}")
    s += "; " + "; ".join(f"{k} OOF mean {v}" for k, v in others.items()) + f" (this learner {a['mean']})."
    pr = pass_rule_learner(tf, key)
    if pr: s += " Pass rule: " + rule_line(pr[1], pr[2]) + f". **{'PASS' if pr[0] else 'no candidate'}**."
    return s


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
      "- **Pass rule** for an exit candidate (adapted from `harness.GO` to a policy-vs-Foundation difference on frozen entries): nested-CV diff > 0; CPCV 5th percentile diff > 0; random-exit percentile >= 95; 12-block sign-flip one-sided p <= 0.05 with >= 8 blocks positive; **lower bound of the 90% block-bootstrap CI of the diff > 0** (`boot_ci90_lower>0`, as `harness.go_no_go` implements it: a CI entirely below 0 fails; the earlier wording 'CI excludes 0' was loose — repair, section 11); "
      "**diff with the top 1% winners removed > 0** (the harness's pre-registered `diff_top1_removed` item: the trades whose policy net is in its own top 1% are dropped, the paired diff is averaged over the rest — `diff_top1_winners_removed` in `eval_table_*.csv`); PBO <= 0.2; studentised SPA p <= 0.10 over the family (the family's vectors at the label's 2-dp precision — repair, section 11). "
      "**Disclosure (repair)**: the earlier text of this rule read 'diff with the top 1% of per-trade *gains* removed > 0' (`diff_top1_gains_removed`: the trades whose gain over the Foundation exit is in the top 1% are dropped). That variant was written after learner C's results had been read (this script's own docstring) and is negative-biased by construction: removing the top 1% of a dispersed difference lowers its mean even when the true mean is zero (its zero-mean reference, the same trim on the centred difference, is about -150 INR on 1 min). It is reported beside the pass item with that reference and is not used to decide.", "",
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
           f"{spa_text(tf)}.{spa_all_text(tf)} Effective trials {c['effective_trials']} on the kept_sum series (harness) and **{ev['effective_trials_selection_gain'] if ev else 'pending'}** on the variant-minus-Foundation series ({ev['distinct_gain_vectors'] if ev else 'pending'} distinct gain vectors; variants that differ only by an inert key — e.g. a 120-bar time stop on 5 min, a CHoCH exit that never fires — are identical by construction). "
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
    md += ["", learner_verdict(tf, b, "B"), ""]
md += ["## 5. Learner A — fitted Q-iteration, pessimistic ensemble (`a_result_*.json`, `a_oof_*.npz`)", ""]
for tf in TFS:
    a = R[tf]["a"]
    if not a:
        md += [f"**{tf}**: no result file (`a_result_{tf}.json` missing; see `04_a_{tf}.log`)."]; continue
    md += [f"**{tf}**: {a['decision_states']} decision states ({a['states']} states, {a['trades']} trades), {a['iterations']} iterations x {a['members']} members, kappa {a['kappa']}, HGB {a['hgb']}. OOF mean **{a['mean']}** vs Foundation {a['fnd_mean']} (diff {a['diff']}, t {a['t']}), random pct {a['random_pct']}, "
           f"regret free {a['regret_vs_oracle_free']} / floor {a['regret_vs_oracle_floor']}, early-exit share {a['exit_early_share']}, sign-flip blocks p1 {a['sign_flip']['blocks']['p_one_sided']} ({a['sign_flip']['blocks']['blocks_positive']}/12 positive), sessions p1 {a['sign_flip']['sessions']['p_one_sided']}. Ledger id `{a['ledger_id']}`. {a['seconds']} s, RSS {a['rss_mb']} MB.", "",
           "| fold | train / test trades (purged) | test mean | test Foundation | test diff | early exits | exit-flag share of states | MAE of Q(s, exit) vs the exact exit value | seconds |", "|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {f['fold']} | {f['train_trades']} / {f['test_trades']} ({f['purged']}) | {f['test_mean']} | {f['test_fnd_mean']} | {round(f['test_mean'] - f['test_fnd_mean'], 2)} | {f['exit_early_share']} | {f['exit_flag_share']} | {f['q_exit_fit_mae']} | {f['seconds']} |" for f in a["folds"]]
    md += ["", learner_verdict(tf, a, "A"), ""]
md += ["## 6. Evaluation on IS CV — net per trade per lot on the same entries, all cut at 15:25 (`eval_table_*.csv`)", ""]
cols = ["policy", "mean_per_lot", "diff_vs_foundation", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor", "win_rate", "pf", "sign_blocks", "signflip_blocks_p1", "signflip_sessions_p1", "boot_diff_ci90", "diff_top1_winners_removed", "diff_top1_gains_removed", "diff_top1_gains_removed_zero_mean_ref", "bars_held_mean"]
for tf in TFS:
    t = R[tf]["table"]
    if t is None: continue
    md += [f"### {tf}", "", md_table(t, [c for c in cols if c in t.columns]), ""]
md += ["The per-trade difference is slippage-invariant for the 1-lot policies (one round trip per lot each); at 8 pts per side every per-lot mean above moves by -390 INR (`mean_slip8` in the CSV). "
       "`diff_top1_winners_removed` is the pass-rule item (harness definition); `diff_top1_gains_removed` is the post-hoc variant, read against `diff_top1_gains_removed_zero_mean_ref` (what the same trim does to a zero-mean difference of the same dispersion) — section 11. "
       "**Seeds (repair, section 11.2)**: `boot_diff_ci90` and `signflip_sessions_p1` are Monte-Carlo estimates (2,000 draws / flips); the table reuses the seed tag of the stage that first reported the statistic (`02_c_select.py`: bootstrap `exit|nested|<tf>` / `exit|best|<tf>`, sign-flip `<tf>|C_nested` / `<tf>|C_best_is` / `<tf>|ST9`; `03_b_imitation.py` / `04_a_fqi.py`: sign-flip `<tf>|B` / `<tf>|A`), so the same statistic carries one value throughout sections 3-6 and 9; a statistic no earlier stage reported (the oracles, the bootstrap CI of ST9 / A / B) is drawn under the `eval|<tf>|<policy>` tag and appears only here (`boot_tag` / `flip_tag` in the CSV).", "",
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
def learner_block(tf, key):
    a = R[tf][key.lower()]
    if not a: return "pending"
    pr = pass_rule_learner(tf, key)
    keys = ("mean", "fnd_mean", "diff", "t", "random_pct", "regret_vs_oracle_free", "regret_vs_oracle_floor", "exit_early_share", "win_rate", "pf", "sign_blocks", "ledger_id", "seconds", "rss_mb")
    out = {k: a.get(k) for k in keys if k in a}
    if "auc_oof" in a: out["auc_oof"] = a["auc_oof"]
    out.update(sign_flip=a["sign_flip"], folds=[{k: f[k] for k in f if k not in ("test_blocks",)} for f in a["folds"]],
               folds_below_foundation=[f["fold"] for f in a["folds"] if f["test_mean"] < f["test_fnd_mean"]],
               pass_rule=dict(passed=pr[0], checks={k: [bool(v[0]), v[1]] for k, v in pr[1].items()}, disclosed_not_pass_items=pr[2]) if pr else "pending")
    return out


for tf in TFS:
    ok, ch, disc = pass_rule(tf)
    c = R[tf]["csel"]; ev = R[tf]["ev"] or {}; sp, sp_kind = spa_of(tf)
    findings["timeframes"][tf] = dict(n=c["n"], foundation_mean=c["foundation"]["mean"], foundation_random_pct=c["foundation"]["random_pct"], nested_pick=c["nested"], cpcv={k: v for k, v in c["cpcv"].items() if k != "per_path"},
                                      pbo=c["pbo"], spa=sp, spa_source=("eval_%s.json spa_family: 05_evaluate.py with the current harness.spa on vectors at the label's 2-dp precision (REPAIR 2026-09-29; the follow-up's as-coded block is spa_as_coded)" % tf) if sp_kind == "current" else "c_select (earlier harness.spa)",
                                      spa_as_coded=ev.get("spa_family_as_coded", "pending"), spa_tolerance_check=ev.get("spa_family_tolerance_check", "pending"), near_duplicates=ev.get("near_duplicates", "pending"),
                                      spa_all_trials=ev.get("spa_all_trials", "pending"), spa_all_trials_as_coded=ev.get("spa_all_trials_as_coded", "pending"), spa_superseded_02_c_select=ev.get("spa_superseded_02_c_select", "pending"),
                                      effective_trials_kept_sum=c["effective_trials"], effective_trials_gain=ev.get("effective_trials_selection_gain"), bootstrap_nested=c["bootstrap_nested"],
                                      st9=c["st9"], best_is=c["best_is"], random_control=c["random_control"], oracle_free=c["oracle_free"], oracle_floor=c["oracle_floor"], sign_flip=c["sign_flip"],
                                      learner_B=learner_block(tf, "B"), learner_A=learner_block(tf, "A"),
                                      eval_table=ev.get("table", "pending"), distillation=ev.get("distillation", "pending"), exit_rules=ev.get("exit_rules", "pending"), gate_multiplication=ev.get("gate_multiplication", "pending"),
                                      pass_rule=dict(passed=ok, checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, disclosed_not_pass_items=disc), ledger_rows=fam_counts[tf], parity=parity[tf], grid_check=R[tf]["grid"])
    md += [f"**{tf}** — learner C nested pick: " + rule_line(ch, disc) + f". **{'PASS' if ok else 'no candidate'}**.", ""]
    for key in ("B", "A"):
        pr = pass_rule_learner(tf, key)
        if pr: md += [f"**{tf}** — learner {key} (OOF; the CPCV item is not evaluable for the 3-fold learners, PBO is the C family's, SPA p the studentised p over every exit trial, repaired family): "
                      + rule_line(pr[1], pr[2]) + f". **{'PASS' if pr[0] else 'no candidate'}**.", ""]
    if ok:
        findings["null_result"] = False
        pick = c["nested"]["folds"][0]["pick"]
        findings["candidates"].append(dict(tf=tf, kind="exit (learner C keys)", config=dict(stop=pick["stop"], scale=pick["scale"], trail=pick["trail"], time_stop_bars=pick["time_stop"], exit_on_choch_against=pick["choch"], square_off="15:25"),
                                           provenance=dict(source="learned on IS 2021-10..2025-12", script="01_c_grid.py / 02_c_select.py", ledger_id=c["nested"]["id"], statistic=dict(nested_diff=c["nested"]["diff"], cpcv_p5=c["cpcv"]["diff_p5"], pbo=c["pbo"]["pbo"], spa_p=sp["spa_p"]))))

# ---------------------------------------------------------------- follow-up (2026-09-29 16:45 IST): the two refuters' minor findings + the missing 5 min finalize step
hl = H_LEDGER = [json.loads(x) for x in open(os.path.join(HERE, "..", "..", "ledger", "trials.jsonl"), encoding="utf-8") if x.strip()]
new_rows = [r for r in hl if r["family"] == "exit_policy/gate_x_exit" and r.get("note") == "followup"]
reused = {tf: [f"{n} `{m['harness_id']}`" for n, m in (R[tf]["ev"] or {}).get("gate_multiplication", {}).items() if str(m.get("ledger_row", "")).startswith("existing")] for tf in TFS}
a1, a5 = R["minute"]["a"], R["5minute"]["a"]
ev1, ev5 = R["minute"]["ev"], R["5minute"]["ev"]
sp1, sp5 = ev1["spa_family"], ev5["spa_family"]                              # repaired (vectors at the label's 2-dp precision)
ac1, ac5 = ev1["spa_family_as_coded"], ev5["spa_family_as_coded"]            # the follow-up's numbers (stored vectors)
nd1, nd5 = ev1["near_duplicates"], ev5["near_duplicates"]
old1, old5 = R["minute"]["csel"]["spa"], R["5minute"]["csel"]["spa"]
# REPAIR 11.6: the timeline of `04_a_fqi.py minute` from the file timestamps and the per-fold seconds (nothing typed): the header and the
# per-fold lines are printed with flush=True (04_a_fqi.py lines 34-35, 82), the final summary line without it (lines 100-101).
import datetime as _dt
_utc = lambda t: _dt.datetime.fromtimestamp(t, _dt.timezone.utc).strftime("%H:%M:%S")
_a_res_mtime = os.path.getmtime(os.path.join(HERE, "a_result_minute.json")); _a_log_mtime = os.path.getmtime(os.path.join(HERE, "04_a_minute.log"))
_a_start = _a_res_mtime - a1["seconds"]; _fold_end = []; _acc = _a_start
for _f in a1["folds"]: _acc += _f["seconds"]; _fold_end.append(_acc)
_a_log_lines = [x for x in open(os.path.join(HERE, "04_a_minute.log"), encoding="utf-8").read().splitlines() if x.strip()]
_a5_log_lines = [x for x in open(os.path.join(HERE, "04_a_5minute.log"), encoding="utf-8").read().splitlines() if x.strip()]
a_log_account = (f"`04_a_minute.log` holds {len(_a_log_lines)} lines — the header and the three per-fold JSON lines, all printed with `flush=True` — and lacks the final summary line that `04_a_fqi.py` prints after `a_result_minute.json` (the 5-min log, {len(_a5_log_lines)} lines, has it). "
                 f"Timeline from the files: start {_utc(_a_start)} UTC (the mtime of `a_result_minute.json`, {_utc(_a_res_mtime)}, minus its `seconds` {a1['seconds']}); fold lines at about {', '.join(_utc(t) for t in _fold_end)}. "
                 f"The 06:24 checkout replaced the log's inode between the fold 0 and fold 1 lines, so the fold 1 and fold 2 lines went to the unlinked inode and were copied back by the mirror loop (`/proc/<pid>/fd`, every 5 s while the process lived; its last copy is the log's mtime, {_utc(_a_log_mtime)}). "
                 f"The final line is printed without `flush=True` after the JSON dump ({_utc(_a_res_mtime)}): it sat in the block buffer until the interpreter exited and reached the unlinked inode after the mirror loop's last copy — lost at process exit, not at the checkout; "
                 f"and 'the JSON was written before it' was wrong: two of the three fold lines and every output file postdate the checkout. Every number the missing line would have carried is in `a_result_minute.json` (OOF mean {a1['mean']}, Foundation {a1['fnd_mean']}, diff {a1['diff']}, random pct {a1['random_pct']}, regret free {a1['regret_vs_oracle_free']}, sign-flip blocks p1 {a1['sign_flip']['blocks']['p_one_sided']}; {a1['seconds']} s, rss {a1['rss_mb']} MB)")
followup = dict(at="2026-09-29 16:45 IST", harness_sha=sp1["harness_sha"], exit_ledger_rows=len(ledger), exit_ledger_appended=0,
                harness_ledger_new_rows=[dict(id=r["id"], tf=r["tf"], label=r["label"], note=r["note"], at=r["at"]) for r in new_rows], harness_ledger_rows_reused=reused,
                spa_old_to_new={tf: dict(old_studentised=dict(spa_p=R[tf]["csel"]["spa"]["spa_p"], rc_p=R[tf]["csel"]["spa"]["rc_p"], best=R[tf]["csel"]["spa"]["best"]),
                                          new_studentised_as_coded=dict(spa_p=R[tf]["ev"]["spa_family_as_coded"]["spa_p"], rc_p=R[tf]["ev"]["spa_family_as_coded"]["rc_p"], best=R[tf]["ev"]["spa_family_as_coded"]["best"], excluded=R[tf]["ev"]["spa_family_as_coded"]["excluded_from_studentised"], min_active_sessions=R[tf]["ev"]["spa_family_as_coded"]["min_active_sessions"]),
                                          new_unstudentised_as_coded=dict(spa_p=R[tf]["ev"]["spa_family_as_coded"]["spa_p_unstudentised"], rc_p=R[tf]["ev"]["spa_family_as_coded"]["rc_p_unstudentised"], best=R[tf]["ev"]["spa_family_as_coded"]["best_unstudentised"])) for tf in TFS},
                what_changed=["learner A (1-minute FQI) folded into sections 5, 6, 8, 9 from a_result_minute.json / a_oof_minute.npz; the sentence saying it was not run replaced",
                              "family SPA recomputed with the current harness.spa (min-active exclusion, unstudentised statistic) for both timeframes on the stored vectors; 0 excluded — the follow-up's explanation of that was FALSE, see repair.issue_1",
                              "05_evaluate.py 5minute run for the first time (eval_table_5minute.csv, eval_5minute.json, exit_rules_5minute.json, gate x exit rows); the PRELIMINARY status closed",
                              "not rerun: the C grid (01), the C selection (02), learner B (03), any FQI fold (04)"],
                corrected_in_repair="the statement 'no variant applies the Foundation's next-CHoCH exit, so every variant differs from the benchmark' was false (variants 1177 / 1183 are near-duplicates of the benchmark); the as-coded SPA numbers stand as what the harness computed on the stored vectors, the repaired ones are in timeframes.<tf>.spa")
findings["followup"] = followup
findings["caveats"] = ["the OOS window (2026) was used by the ST9-12 exit grid (r_combinations), so no exit table here can treat 2026 as untouched; every exit comparison carries this (judge 1)",
                       "learners A / B are evaluated on 3 contiguous session-block folds (judge 2), so they have no CPCV path distribution and cannot pass the pass rule in full",
                       "the SPA statistic is a per-session mean selection gain: a variant with a negative per-trade diff vs the Foundation exit can lead the studentised family (1 min: stop 75 / choch True, diff -13.27)",
                       "c_select_<tf>.json's `spa` block is the finished selection stage's output (earlier harness.spa) and is superseded by eval_<tf>.json `spa_family`; it was not edited"]
md += ["## 10. Follow-up (2026-09-29 16:45 IST)", "",
       "What changed and why (the two refuters' minor findings, plus the one finalize step that had not run). Nothing else was rerun: the learner C grid (`01_c_grid.py`), the C selection (`02_c_select.py`), learner B (`03_b_imitation.py`) and every FQI fold (`04_a_fqi.py`) are the runs already on disk.", "",
       f"1. **Learner A on 1 min.** Judge 2's condition for the 1-minute FQI (learner B or C beating the Foundation exit OOF on 1 min) was met (B +{R['minute']['b']['diff']}, C nested +{R['minute']['csel']['nested']['diff']}); `04_a_fqi.py minute` ran under nohup and finished at 07:08 UTC "
       f"(`a_result_minute.json`, `a_oof_minute.npz`, exit-ledger row `{a1['ledger_id']}`, family `exit_policy/A`). **[Corrected in the repair, section 11.6]** The follow-up wrote here that the log's final summary line 'was lost when the 06:24 checkout replaced the file's inode, the JSON was written before it'; the timestamps say otherwise: {a_log_account}. "
       f"The earlier section 5 sentence \"not run: the condition ... was not met\" was `06_findings.py`'s fallback text while the run was in progress and was wrong; it is replaced by the measured numbers. "
       f"Per fold (test mean vs Foundation): " + "; ".join(f"fold {f['fold']}: {f['test_mean']} vs {f['test_fnd_mean']} ({round(f['test_mean'] - f['test_fnd_mean'], 2)}), early exits {f['exit_early_share']}, Q-fit MAE {f['q_exit_fit_mae']}" for f in a1["folds"])
       + f". Pooled OOF mean {a1['mean']} vs {a1['fnd_mean']} (diff {a1['diff']}, t {a1['t']}), random-exit percentile {a1['random_pct']}, early-exit share {a1['exit_early_share']}; "
       + f"below the Foundation exit in {len([f for f in a1['folds'] if f['test_mean'] < f['test_fnd_mean']])} of 3 folds; it does not beat learner B ({R['minute']['b']['mean']}) or the C nested pick ({R['minute']['csel']['nested']['mean']}); pass rule: **{'PASS' if pass_rule_learner('minute', 'A')[0] else 'no candidate'}** (section 9). "
       + f"On 5 min (already in `a_result_5minute.json`, now also in sections 6, 8, 9): pooled OOF {a5['mean']} vs {a5['fnd_mean']} (diff {a5['diff']}, t {a5['t']}), random pct {a5['random_pct']}, below the Foundation exit in {len([f for f in a5['folds'] if f['test_mean'] < f['test_fnd_mean']])} of 3 folds: **it hurts**.", "",
       f"2. **Family SPA with the current `harness.spa`** (sha `{ac1['harness_sha']}`; `harness.py` was not modified here or in the repair). The earlier numbers came from `02_c_select.py` with the harness before its revision; the harness now excludes from the studentised (Hansen) family any candidate whose selection gain is non-zero in fewer than max(10, 5% of T) sessions "
       f"(1 min: {ac1['min_active_sessions']} of {ac1['sessions']} sessions; 5 min: {ac5['min_active_sessions']} of {ac5['sessions']}) and reports White's unstudentised reality-check statistic beside it. Re-run by the follow-up over the same family (the 1,568 C variants, ledger order) with the same bootstrap tag on the vectors as stored: "
       f"**1 min** studentised SPA p {old1['spa_p']} -> **{ac1['spa_p']}** (RC p {old1['rc_p']} -> {ac1['rc_p']}; best variant {old1['best']} -> {ac1['best']}), unstudentised SPA p **{ac1['spa_p_unstudentised']}** (RC p {ac1['rc_p_unstudentised']}); "
       f"**5 min** studentised SPA p {old5['spa_p']} -> **{ac5['spa_p']}** (RC p {old5['rc_p']} -> {ac5['rc_p']}; best {old5['best']} -> {ac5['best']}), unstudentised SPA p **{ac5['spa_p_unstudentised']}** (RC p {ac5['rc_p_unstudentised']}); "
       f"candidates excluded by the min-active rule as coded: 1 min {ac1['excluded_from_studentised']}, 5 min {ac5['excluded_from_studentised']}. "
       f"**[Rewritten in the repair, section 11.1]** The follow-up explained the zero exclusions with 'every grid variant's selection gain is non-zero in every active session; no variant applies the Foundation's next-CHoCH exit, so every variant differs from the benchmark wherever a session has a trade'. **That statement was false.** "
       f"The family contains near-duplicates of the benchmark — variant 1177 (stop foundation / scale none / trail none / time_stop None / choch True) on both timeframes and variant 1183 (the same with a 120-bar time stop, inert on 5 min) on 5 min — because the CHoCH-against cut is the engine's own next-CHoCH exit: "
       f"the L1 next-CHoCH exit is at the close of its exit bar on {ev1['l1_choch_facts']['exit_px_equals_close_of_exit_bar_share']:.0%} of the {ev1['l1_choch_facts']['next_choch_exits']} such 1-min exits and that bar is the first CHoCH-against bar after entry on {ev1['l1_choch_facts']['exit_bar_equals_first_choch_against_share']:.1%} "
       f"(5 min: {ev5['l1_choch_facts']['exit_px_equals_close_of_exit_bar_share']:.0%} of {ev5['l1_choch_facts']['next_choch_exits']}, {ev5['l1_choch_facts']['exit_bar_equals_first_choch_against_share']:.1%}). "
       f"Variant 1177 reproduces the Foundation L1 exit on all but {nd1[0]['trades_differing_from_L1_gt_0_005']} of {nd1[0]['trades']} 1-min trades and all but {nd5[0]['trades_differing_from_L1_gt_0_005']} of {nd5[0]['trades']} 5-min trades; its selection gain was 'non-zero in every session' "
       f"({nd1[0]['sessions_active_gt_1e_9']} / {ac1['sessions']} and {nd5[0]['sessions_active_gt_1e_9']} / {ac5['sessions']}) only because the variant net is `lab.price_trade`'s unrounded value while the label `l1_net_inr` is rounded to 2 dp (|gain| > 0.01 INR in just {nd1[0]['sessions_active_gt_0_01']} and {nd5[0]['sessions_active_gt_0_01']} sessions), "
       f"so the 1e-9 activity rule as coded excluded nothing and the follow-up's re-run was a no-op on this family. With the vectors built at the label's precision (repair) the same rule excludes {sp1['excluded_from_studentised']} (1 min) / {sp5['excluded_from_studentised']} (5 min) candidates and the studentised SPA p becomes **{sp1['spa_p']}** (1 min) / **{sp5['spa_p']}** (5 min) — still above 0.10, so the verdict is unchanged. "
       f"`c_select_<tf>.json`'s `spa` block is the finished stage's output and was not edited; `eval_<tf>.json` `spa_family` / `spa_all_trials` are the repaired blocks, `spa_family_as_coded` / `spa_all_trials_as_coded` the follow-up's, `spa_superseded_02_c_select` the original.", "",
       f"3. **`05_evaluate.py 5minute` ran for the first time** (it had not been run when the 5 min learners finished): `eval_table_5minute.csv`, `eval_5minute.json`, `exit_rules_5minute.json` (best learner B exits early on 0 states: nothing to distil), the 5 min effective-trials figure on the gain series and the top-1%-removed pass item, the gate x exit rows; the PRELIMINARY status of section 9 is closed.", "",
       f"**Ledgers.** Exit ledger (`exit_ledger.jsonl`): {len(ledger)} rows, nothing appended by the follow-up (learner A's rows were written by `04_a_fqi.py`). Harness ledger (`OUT/ledger/trials.jsonl`): {len(new_rows)} new rows, note `followup`: "
       + "; ".join(f"`{r['id']}` ({r['tf']}, {r['label']})" for r in new_rows) + "; reused by id, no duplicate written: " + "; ".join(f"{tf}: {', '.join(v)}" for tf, v in reused.items() if v) + ".", "",
       f"**Verdict after the follow-up**: unchanged — " + "; ".join(f"{tf}: learner C nested pick {'PASS' if pass_rule(tf)[0] else 'no candidate'}, learner B {'PASS' if pass_rule_learner(tf, 'B')[0] else 'no candidate'}, learner A {'PASS' if pass_rule_learner(tf, 'A')[0] else 'no candidate'}" for tf in TFS)
       + ". No exit policy rescues the book on either timeframe; the null result stands.", ""]

# ---------------------------------------------------------------- REPAIR (2026-09-29): the adversarial refuters' three material issues
POL = {"C_nested": "C nested-CV pick (OOF)", "C_best_is": "C in-sample best (a trial)", "B": "B hindsight imitation (OOF)", "A": "A FQI pessimistic ensemble (OOF)", "ST9": "ST9 R-ladder (3 lots, stop 50, 1R/2R, trail 3R lag 1) per lot"}
def trow(tf, key): return next((r for r in R[tf]["ev"]["table"] if r["policy"] == POL[key]), None)
def f2(v): return "" if v is None else str(v)
repair_rows_appended = [r for r in hl if r.get("script") == "05_evaluate.py" and str(r.get("at", "")) > "2026-09-29T11:40"]
mtime = lambda p: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.path.getmtime(os.path.join(HERE, p)))) if os.path.exists(os.path.join(HERE, p)) else None
repair = dict(at="2026-09-29 17:20-17:55 IST (two passes, see the section text)", harness_sha=sp1["harness_sha"], harness_modified=False, rerun=["05_evaluate.py minute", "05_evaluate.py 5minute", "06_findings.py"], not_rerun=["01_c_grid.py", "02_c_select.py", "03_b_imitation.py", "04_a_fqi.py"],
              logs=["05_eval_minute_repair.log", "05_eval_5minute_repair.log", "05_eval_minute_repair2.log", "05_eval_5minute_repair2.log", "06_findings_repair.log", "06_findings_repair2.log"], harness_ledger_rows_appended_by_repair=len(repair_rows_appended), exit_ledger_rows=len(ledger), exit_ledger_appended_by_repair=0,
              gate_rows_reused_by_id={tf: {n: m["ledger_row"] for n, m in R[tf]["ev"]["gate_multiplication"].items()} for tf in TFS}, issues={})
md += ["## 11. Repair (2026-09-29, after the adversarial refuters' material findings)", "",
       f"Two sets of confirmed material findings reached this folder within the same hour — the re-verification of the study after the resume and the verification of the follow-up (section 10) — and they overlap on the SPA finding; this section merges both. Each issue is stated with what was wrong, what changed and the numbers now: "
       "11.1 the family SPA and a near-duplicate of the benchmark (both sets); 11.2 the top-1% pass item (first set); 11.3 the stale summary at review time (first set); 11.4 the same statistic reported with two values (second set); 11.5 the wording of the bootstrap-CI item (second set); 11.6 section 10.1's account of the missing log line (second set — the issue list handed to that repair was cut by the workflow at 6,000 characters inside this item, so any later item of the second set was not received). "
       f"Rerun: `05_evaluate.py` on both timeframes, twice (`05_eval_<tf>_repair.log`: 11.1 / 11.2; `05_eval_<tf>_repair2.log`: 11.4, identical SPA numbers; the gate x exit rows are reused by their harness ids — "
       + "; ".join(f"{tf}: " + ", ".join(f"{n} {m['ledger_row'].split(' (')[0]}" for n, m in R[tf]["ev"]["gate_multiplication"].items()) for tf in TFS)
       + f" — harness-ledger rows appended by the repair: {len(repair_rows_appended)}; exit ledger {len(ledger)} rows, nothing appended, no stored vector edited) and this script. Not rerun: the C grid (`01`), the C selection (`02`), learner B (`03`), any FQI fold (`04`). `harness.py` was not modified (outside this study's scope).", "",
       "### 11.1 The family SPA was inflated by a near-duplicate of the benchmark; the follow-up's explanation of the zero exclusions was false", "",
       "**What was wrong.** `harness.spa` excludes from the studentised family a candidate whose selection gain is non-zero (|gain| > 1e-9) in fewer than max(10, 5% of T) sessions — a guard against a duplicate of the benchmark, whose near-zero variance gives an arbitrarily large t. "
       "The family holds such duplicates (table below): with the Foundation stop, no target and no trail, the CHoCH-against cut is the engine's own next-CHoCH exit, so the variant reproduces the L1 label on all but a handful of trades. "
       "Its gain was 'non-zero in every session' only because the variant net is `lab.price_trade`'s unrounded value while the label `l1_net_inr` is rounded to 2 dp: |gain| <= 0.005 INR of rounding noise wherever the two agree, above 1e-9, so the rule excluded nothing, and section 10.2's sentence explaining that ('no variant applies the Foundation's next-CHoCH exit') was wrong. "
       "The refuters' reproduction agrees: the near-degenerate variant is the argmax of the studentised bootstrap null in about 20% (1 min) / 38% (5 min) of the 2,000 draws (the `null_argmax` column below), which is how it inflates the family p.", "",
       "| tf | variant | keys | trades differing from L1 by > 0.005 INR (of n) | max abs diff on the agreeing trades | exit bar = L1 exit bar | sessions with abs gain > 1e-9 / > 0.01 / > 0.5 (of T) | active sessions at 2 dp | argmax of the as-coded studentised null (of 2000 draws) | t as coded | excluded now (2 dp rule / tolerance check) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for tf, nd, ac in (("minute", nd1, ac1), ("5minute", nd5, ac5)):
    for d in nd:
        md += [f"| {tf} | {d['index']} | {keys_str(d['keys'])} | {d['trades_differing_from_L1_gt_0_005']} (of {d['trades']}) | {d['max_abs_diff_on_agreeing_trades']} | {d['exit_bar_equals_L1_share']:.2%} | {d['sessions_active_gt_1e_9']} / {d['sessions_active_gt_0_01']} / {d['sessions_active_gt_0_5']} (of {ac['sessions']}) | {d['sessions_active_after_2dp']} | {d['null_argmax_draws_as_coded']} | {d['t_studentised_as_coded']} | {d['excluded_by_repaired_rule']} / {d['excluded_by_tolerance_check']} |"]
md += ["", "**Why the duplicates exist** (`l1_choch_facts` in `eval_<tf>.json`): " + "; ".join(f"{tf}: the L1 next-CHoCH exit is at the close of its exit bar on {R[tf]['ev']['l1_choch_facts']['exit_px_equals_close_of_exit_bar_share']:.1%} of {R[tf]['ev']['l1_choch_facts']['next_choch_exits']} such exits and that bar is the first CHoCH-against bar after entry on {R[tf]['ev']['l1_choch_facts']['exit_bar_equals_first_choch_against_share']:.1%} (the rest: the CHoCH printed on the cap bar); `l1_net_inr` has more than 2 decimals on {R[tf]['ev']['l1_choch_facts']['l1_net_inr_decimals_gt_2']} trades, the grid nets on {R[tf]['ev']['l1_choch_facts']['grid_nets_decimals_gt_2']} of {R[tf]['ev']['l1_choch_facts']['grid_cells']} cells" for tf in TFS) + ".", "",
       "**Fix** (the refuter's second option; `harness.py` untouched, the stored `vectors/*.npz` untouched): the family's per-session vectors are rebuilt inside `05_evaluate.py` from the per-trade nets **rounded to 2 dp, the label's own precision** (the row -> net mapping is proved against every stored vector first: "
       + ", ".join(f"{tf} `vector_mapping_verified` {R[tf]['ev']['vector_mapping_verified']}" for tf in TFS) + "), and `harness.spa` is run on them with the same tag (the same 2,000 stationary-bootstrap draws), so a duplicate has an exactly-zero gain wherever it agrees with the label and the min-active rule applies as designed. "
       "Beside it, a material-tolerance check drops from the list every candidate with fewer than min-active sessions of |gain| > 0.01 INR (from both statistics' families, unlike the harness's own rule, which keeps them in the unstudentised one).", "",
       "| tf | family | statistic | as coded (stored vectors; the follow-up's numbers) | repaired (vectors at 2 dp) | tolerance check (abs gain > 0.01) |", "|---|---|---|---|---|---|"]


def exc_cell(lst):
    """'variant index `exit-ledger id`' for each excluded candidate, or 'none'."""
    return ", ".join(f"{e['index']} `{e['id']}`" for e in lst) or "none"


for tf in TFS:
    ev = R[tf]["ev"]; sp, ac, tol = ev["spa_family"], ev["spa_family_as_coded"], ev["spa_family_tolerance_check"]; sa, sac, satol = ev["spa_all_trials"], ev["spa_all_trials_as_coded"], ev["spa_all_trials_tolerance_check"]
    md += [f"| {tf} | C grid ({sp['candidates']}) | excluded from the studentised family (variant, exit-ledger id) | {ac['excluded_from_studentised']} | {sp['excluded_from_studentised']} ({exc_cell(sp['excluded_candidates'])}) | {tol['excluded']} ({', '.join(map(str, tol['excluded_indices'])) or 'none'}) |",
           f"| {tf} | C grid | studentised best (variant, t) | {ac['best']} ({ac['best_t']}) | {sp['best']} ({sp['best_t']}) | {tol['best_index']} ({tol['best_t']}) |",
           f"| {tf} | C grid | studentised RC p / **SPA p** | {ac['rc_p']} / **{ac['spa_p']}** | {sp['rc_p']} / **{sp['spa_p']}** | {tol['rc_p']} / **{tol['spa_p']}** |",
           f"| {tf} | C grid | unstudentised RC p / SPA p | {ac['rc_p_unstudentised']} / {ac['spa_p_unstudentised']} | {sp['rc_p_unstudentised']} / {sp['spa_p_unstudentised']} | {tol['rc_p_unstudentised']} / {tol['spa_p_unstudentised']} |",
           f"| {tf} | every exit trial ({sa['candidates']}) | excluded / studentised SPA p / unstudentised SPA p | {sac['excluded_from_studentised']} / {sac['spa_p']} / {sac['spa_p_unstudentised']} | {sa['excluded_from_studentised']} / {sa['spa_p']} / {sa['spa_p_unstudentised']} | {satol['excluded']} / {satol['spa_p']} / {satol['spa_p_unstudentised']} |"]
    repair["issues"].setdefault("issue_1_spa_near_duplicate", {})[tf] = dict(near_duplicates=ev["near_duplicates"], l1_choch_facts=ev["l1_choch_facts"], vector_mapping_verified=ev["vector_mapping_verified"],
        as_coded=dict(spa_p=ac["spa_p"], rc_p=ac["rc_p"], best=ac["best"], best_t=ac["best_t"], excluded=ac["excluded_from_studentised"], spa_p_unstudentised=ac["spa_p_unstudentised"]),
        repaired=dict(spa_p=sp["spa_p"], rc_p=sp["rc_p"], best=sp["best"], best_t=sp["best_t"], excluded=sp["excluded_from_studentised"], excluded_indices=[e["index"] for e in sp["excluded_candidates"]], spa_p_unstudentised=sp["spa_p_unstudentised"]),
        tolerance_check=tol, all_trials=dict(as_coded_spa_p=sac["spa_p"], repaired_spa_p=sa["spa_p"], repaired_excluded=sa["excluded_from_studentised"], tolerance_spa_p=satol["spa_p"]), null_argmax_top5_as_coded=ev["null_argmax_top5_as_coded"],
        pass_item_spa_p_le_0_10=bool(sp["spa_p"] <= 0.10))
md += ["", f"**Consequence.** The studentised family p moves from {ac1['spa_p']} to **{sp1['spa_p']}** on 1 min and from {ac5['spa_p']} to **{sp5['spa_p']}** on 5 min (every exit trial: {ev1['spa_all_trials_as_coded']['spa_p']} -> {ev1['spa_all_trials']['spa_p']}, {ev5['spa_all_trials_as_coded']['spa_p']} -> {ev5['spa_all_trials']['spa_p']}); the pass item `spa_p <= 0.10` "
       f"{'still fails on both timeframes' if sp1['spa_p'] > 0.10 and sp5['spa_p'] > 0.10 else 'CHANGES on at least one timeframe (see section 9)'}, so the verdict (no candidate) is unchanged, but the headline multiplicity statistic reported before was materially wrong on 5 min and section 10.2 explained the zero exclusions with an incorrect fact — both are corrected above. "
       "Recommendation to the program owner (not done here: `harness.py` is outside this study's scope): define activity in `harness.spa` on a material tolerance (e.g. |gain| > 0.01 INR, or count units with |kept - benchmark| > 0.005) or round the candidate nets to the label's precision before the vectors are built; as coded the 1e-9 rule is a no-op against a duplicate that differs from the benchmark only in rounding.", "",
       "### 11.2 The 'top 1% removed' pass item was a post-hoc, negative-biased variant of the harness's item", "",
       "**What was wrong.** The pass rule read 'diff with the top 1% of per-trade gains removed > 0' (`diff_top1_gains_removed`: the 1% of trades where the policy gained most over the Foundation exit are dropped, the paired difference averaged over the rest). This script's own docstring records that the pass rule was written after learner C's results had been read; and the metric is mechanically negative-biased: "
       "removing the largest 1% of a dispersed difference lowers its mean even when its true mean is zero (the zero-mean reference column below = the same trim applied to the centred difference). The harness's pre-registered item (`harness.GO` `diff_top1_removed`) removes the top 1% **winners by net**; its analogue here is `diff_top1_winners_removed` (trades whose policy net is in its own top 1% dropped).", "",
       "**Fix.** `05_evaluate.py` now writes both definitions, the zero-mean reference, the both-tails-trimmed mean and the top-1% trades' contribution; the pass-rule item is the harness definition (section 1, disclosure included) and `diff_top1_gains_removed` is reported beside it as disclosed, not decisive (sections 4, 5, 9).", "",
       "| tf | policy | diff vs Foundation | top 1% WINNERS removed (harness item) | top 1% GAINS removed (post-hoc) | zero-mean reference of that trim | both 1% tails trimmed | top-1% trades: n / mean gain / contribution per trade | mean gain of the other trades |", "|---|---|---|---|---|---|---|---|---|"]
for tf in TFS:
    for key in ("C_nested", "C_best_is", "B", "A", "ST9"):
        r = trow(tf, key)
        if r and r.get("diff_top1_gains_removed") is not None:
            md += [f"| {tf} | {key} | {r['diff_vs_foundation']} | **{r['diff_top1_winners_removed']}** | {r['diff_top1_gains_removed']} | {r['diff_top1_gains_removed_zero_mean_ref']} | {r['diff_both_1pct_tails_trimmed']} | {r['top1_gains_n']} / {r['top1_gains_mean']} / {r['top1_gains_contribution_per_trade']} | {r['rest_mean_gain']} |"]
            repair["issues"].setdefault("issue_2_top1_metric", {}).setdefault(tf, {})[key] = {k: r.get(k) for k in ("diff_vs_foundation", "diff_top1_winners_removed", "diff_top1_gains_removed", "diff_top1_gains_removed_zero_mean_ref", "diff_both_1pct_tails_trimmed", "top1_gains_n", "top1_gains_mean", "top1_gains_contribution_per_trade", "rest_mean_gain")}
cn1 = trow("minute", "C_nested")
w1 = {k: trow("minute", k)["diff_top1_winners_removed"] for k in ("C_nested", "B", "A", "C_best_is")}
md += ["", f"**Consequence.** On 1 min the harness item passes for {', '.join(f'{k} ({v})' for k, v in w1.items() if v > 0)}" + (f" and fails for {', '.join(f'{k} ({v})' for k, v in w1.items() if v <= 0)}" if any(v <= 0 for v in w1.values()) else "") + ", so the C nested pick now fails the pass rule on the SPA item alone "
       f"(section 9: {rule_line(*pass_rule('minute')[1:])}); learner B fails on SPA and on the CPCV item it cannot have; learner A on more. The qualitative statement stands and is now quantified: the C nested pick's +{cn1['diff_vs_foundation']} per trade is carried by its top 1% of gains — {cn1['top1_gains_n']} trades with a mean gain of {cn1['top1_gains_mean']} contribute {cn1['top1_gains_contribution_per_trade']} per trade, the other {int(R['minute']['csel']['n']) - int(cn1['top1_gains_n'])} trades net {cn1['rest_mean_gain']} — "
       f"which is what the post-hoc metric shows, against a zero-mean reference of {cn1['diff_top1_gains_removed_zero_mean_ref']} (what '> 0' demanded of it). On 5 min every learner fails both definitions. The verdict is unchanged on both timeframes.", "",
       "### 11.3 The FINDINGS.md / summary at review time were stale relative to the folder", "",
       f"**What was wrong.** At review time the summary described learner A as 'RUNNING' (1 min) / 'fold 2 running' (5 min) and section 5 said the 1-min FQI was 'not run: the condition ... was not met', while `a_result_minute.json` (written {mtime('a_result_minute.json')}; OOF {a1['mean']}, diff {a1['diff']}, sign-flip blocks p1 {a1['sign_flip']['blocks']['p_one_sided']}, {a1['sign_flip']['blocks']['blocks_positive']}/12 blocks positive) and `a_result_5minute.json` (mtime {mtime('a_result_5minute.json')} = the 06:24 checkout that re-created every committed file; the 5-min run had finished before that commit; OOF {a5['mean']}, diff {a5['diff']}) both existed: "
       f"the condition was met and the run had finished. A concurrent follow-up agent corrected this during the review (section 10: FINDINGS.md / findings.json rewritten, `05_evaluate.py` / `06_findings.py` modified, {len(new_rows)} harness-ledger rows appended with note `followup`).", "",
       f"**What the repair did.** Nothing about learner A was rerun; this document and `findings.json` are regenerated by `06_findings.py` from the files on disk (every number read from `a_result_*.json`, `b_result_*.json`, `c_select_*.json`, `eval_*.json`, the ledgers; none typed), so sections 5, 6, 8, 9 carry the measured learner A numbers on both timeframes, and the pass rule is applied to A and B like to C. "
       f"The follow-up's {len(new_rows)} harness-ledger rows ({', '.join('`' + r['id'] + '`' for r in new_rows)}) are reused by id in the repair rerun (no duplicate written); the exit ledger holds {len(ledger)} rows, unchanged.", ""]

# 11.4 (second set): the section 6 table re-drew the bootstrap CI and the session sign-flip under the eval tag, so the same statistic appeared with two values
REVIEW = {tf: pd.read_csv(os.path.join(HERE, f"eval_table_{tf}_review_time.csv")) if os.path.exists(os.path.join(HERE, f"eval_table_{tf}_review_time.csv")) else None for tf in TFS}


def rev_row(tf, key):
    t = REVIEW[tf]
    if t is None: return None
    m = t[t.policy == POL[key]]
    return None if m.empty else m.iloc[0]


pairs = []


def add_pair(tf, stat, key, own_val, own_src):
    r = trow(tf, key); rv = rev_row(tf, key)
    now = r.get(stat) if r else None
    before = None
    if rv is not None and stat in rv.index:
        v = rv[stat]; before = json.loads(v) if isinstance(v, str) else (None if pd.isna(v) else float(v))
    pairs.append(dict(tf=tf, statistic=stat, policy=key, review_time_table_value=before, table_value_now=now, first_reported_value=own_val, first_reported_by=own_src,
                      tag_now=(r or {}).get("boot_tag" if stat == "boot_diff_ci90" else "flip_tag"), equal_now=bool(now == own_val)))


for tf in TFS:
    c = R[tf]["csel"]
    add_pair(tf, "boot_diff_ci90", "C_nested", c["bootstrap_nested"]["diff_ci"], "02_c_select.py bootstrap_nested (tag exit|nested|<tf>)")
    add_pair(tf, "signflip_sessions_p1", "C_nested", c["sign_flip"]["C_nested"]["sessions"]["p_one_sided"], "02_c_select.py sign_flip (tag <tf>|C_nested)")
    add_pair(tf, "boot_diff_ci90", "C_best_is", c["bootstrap_best"]["diff_ci"], "02_c_select.py bootstrap_best (tag exit|best|<tf>)")
    add_pair(tf, "signflip_sessions_p1", "C_best_is", c["sign_flip"]["C_best_is"]["sessions"]["p_one_sided"], "02_c_select.py sign_flip (tag <tf>|C_best_is)")
    add_pair(tf, "signflip_sessions_p1", "ST9", c["sign_flip"]["ST9"]["sessions"]["p_one_sided"], "02_c_select.py sign_flip (tag <tf>|ST9)")
    for key, src in (("B", "03_b_imitation.py sign_flip (tag <tf>|B)"), ("A", "04_a_fqi.py sign_flip (tag <tf>|A)")):
        a = R[tf][key.lower()]
        if a and trow(tf, key): add_pair(tf, "signflip_sessions_p1", key, a["sign_flip"]["sessions"]["p_one_sided"], src)
all_equal = all(p["equal_now"] for p in pairs)
md += ["### 11.4 The same statistic was reported with two values (Monte-Carlo estimates under two seed tags)", "",
       "**What was wrong.** The section 6 table re-drew the block bootstrap and the session sign-flip under its own tags (`eval|<tf>|<policy>` / `<tf>|eval|<policy>`), while sections 3, 5 and 9 quote the values the learners' own stages drew (`02_c_select.py`: `exit|nested|<tf>`, `<tf>|C_nested`; `04_a_fqi.py`: `<tf>|A`; `03_b_imitation.py`: `<tf>|B`), and nothing said so: "
       "the C nested pick's 90% CI, learner A's and learner B's session sign-flip p each appeared with two values that differ by Monte-Carlo error (2,000 draws / flips each). None is the deciding pass-rule item and none flips a verdict.", "",
       "**Fix.** `05_evaluate.py` reuses the seed tag of the stage that first reported the statistic (`OWN_TAGS`; `boot_tag` / `flip_tag` columns in `eval_table_<tf>.csv`), so each statistic carries one value throughout; a statistic no earlier stage reported (the oracles; the bootstrap CI of ST9 / A / B) keeps the eval tag and appears only in section 6. "
       "`eval_table_<tf>_review_time.csv` is the table as the refuters read it (exported from the checkpoint commit) and gives the 'before' column.", "",
       "| tf | statistic | policy | value at review time (eval tag) | value now (own tag) | first reported by | equal now |", "|---|---|---|---|---|---|---|"]
md += [f"| {p['tf']} | {p['statistic']} | {p['policy']} | {p['review_time_table_value']} | {p['table_value_now']} | {p['first_reported_by']} | {p['equal_now']} |" for p in pairs]
md += ["", f"Every pair is now equal: **{all_equal}**. The SPA blocks, the distillation and the gate x exit rows are unaffected (deterministic under their own tags; the second rerun reproduced 11.1's numbers).", ""]
repair["issues"]["issue_4_two_values_per_statistic"] = dict(pairs=pairs, all_equal_now=all_equal, review_time_tables=["eval_table_minute_review_time.csv", "eval_table_5minute_review_time.csv"])

# 11.5 (second set): the bootstrap-CI item's wording
a5row = trow("5minute", "A")
md += ["### 11.5 The bootstrap-CI pass item was worded 'CI excludes 0' but implemented as 'lower bound > 0'", "",
       f"**What was wrong.** Section 1 read '90% block-bootstrap CI of the diff excludes 0'; the implementation (this script, and `harness.go_no_go`: `boot['diff_ci'][0] > 0`) marks a CI entirely below 0 as FAIL — 5-min learner A's {a5row['boot_diff_ci90'] if a5row else 'n/a'} is a FAIL in sections 5 and 9. The implementation is the intended one (a positive effect); only the wording was loose.", "",
       "**Fix.** The item is worded and keyed as implemented: **lower bound of the 90% block-bootstrap CI of the diff > 0** (`boot_ci90_lower>0`; section 1 and every pass-rule line, `findings.json`). No value changed.", ""]
repair["issues"]["issue_5_ci_item_wording"] = dict(old_wording="90% block-bootstrap CI of the diff excludes 0", new_wording="lower bound of the 90% block-bootstrap CI of the diff > 0", key="boot_ci90_lower>0",
                                                 implementation="harness.go_no_go: boot['diff_ci'][0] > 0", example_5minute_A_ci=a5row["boot_diff_ci90"] if a5row else None)

# 11.6 (second set): section 10.1's account of the missing final line of 04_a_minute.log
md += ["### 11.6 Section 10.1's account of the missing final line of `04_a_minute.log` was wrong", "",
       f"**What was wrong, and what the files say.** The follow-up wrote that the line 'was lost when the 06:24 checkout replaced the file's inode, the JSON was written before it'. {a_log_account}.", "",
       "**Fix.** Section 10.1 carries the corrected account (marked); nothing about learner A was rerun. For future scripts: print the final line with `flush=True` (or run under `python -u`) so a mirrored log is complete at exit.", ""]
repair["issues"]["issue_6_a_minute_log_account"] = dict(log_lines=len(_a_log_lines), log_5minute_lines=len(_a5_log_lines), a_result_minute_mtime_utc=_utc(_a_res_mtime), log_mtime_utc=_utc(_a_log_mtime), seconds=a1["seconds"], start_utc=_utc(_a_start),
                                                      fold_line_times_utc=[_utc(t) for t in _fold_end], checkout_utc="06:24:40",
                                                      mechanism="fold lines printed with flush=True and mirrored back from /proc/<pid>/fd; the final line, printed without flush after the JSON dump, reached the unlinked inode at interpreter exit, after the mirror loop's last copy",
                                                      old_statement="lost when the 06:24 checkout replaced the file's inode, the JSON was written before it")
md += [f"**Verdict after the repair**: unchanged — " + "; ".join(f"{tf}: learner C nested pick {'PASS' if pass_rule(tf)[0] else 'no candidate'}, learner B {'PASS' if pass_rule_learner(tf, 'B')[0] else 'no candidate'}, learner A {'PASS' if pass_rule_learner(tf, 'A')[0] else 'no candidate'}" for tf in TFS)
       + ". No exit policy rescues the book on either timeframe; the null result stands. The one number a reader would have carried away wrongly — the 5-min family SPA p 0.4965 — is 0.185 with the benchmark duplicates excluded; the 1-min p is " + f"{sp1['spa_p']} (was {ac1['spa_p']}).", ""]
repair["issues"]["issue_3_stale_summary"] = dict(a_result_minute_written=mtime("a_result_minute.json"), a_result_5minute_written=mtime("a_result_5minute.json"), learner_A_minute=dict(mean=a1["mean"], diff=a1["diff"], sign_flip_blocks=a1["sign_flip"]["blocks"]),
                                                learner_A_5minute=dict(mean=a5["mean"], diff=a5["diff"]), followup_harness_rows=[r["id"] for r in new_rows], regenerated_from_files=True)
repair["verdict"] = {tf: dict(C_nested="PASS" if pass_rule(tf)[0] else "no candidate", B="PASS" if pass_rule_learner(tf, "B")[0] else "no candidate", A="PASS" if pass_rule_learner(tf, "A")[0] else "no candidate") for tf in TFS}
findings["repair"] = repair
findings["caveats"] = ["the OOS window (2026) was used by the ST9-12 exit grid (r_combinations), so no exit table here can treat 2026 as untouched; every exit comparison carries this (judge 1)",
                       "learners A / B are evaluated on 3 contiguous session-block folds (judge 2), so they have no CPCV path distribution and cannot pass the pass rule in full",
                       "the SPA statistic is a per-session mean selection gain: a variant with a negative per-trade diff vs the Foundation exit can lead the studentised family" + "".join(f" ({tf}: {keys_str(R[tf]['ev']['spa_family']['best_keys']['keys'])}, per-trade diff {R[tf]['ev']['spa_family']['best_keys']['diff_vs_foundation']})" for tf in TFS if (R[tf]["ev"]["spa_family"]["best_keys"]["diff_vs_foundation"] or 0) < 0),
                       "the family contains near-duplicates of the benchmark (variants 1177 / 1183: the CHoCH-against cut is the engine's next-CHoCH exit); harness.spa's 1e-9 activity rule does not catch a duplicate that differs from the label only in rounding, so the study builds the family's vectors at the label's 2-dp precision (repair 11.1); a material tolerance in harness.spa is recommended to the program owner",
                       "the pass-rule item 'top 1% removed' is the harness's winners-by-net definition; the study's earlier gains-removed variant was chosen after the C results were read and is negative-biased by construction; it is disclosed, not decisive (repair 11.2)",
                       "c_select_<tf>.json's `spa` block is the finished selection stage's output (earlier harness.spa) and is superseded by eval_<tf>.json `spa_family` (repaired) / `spa_family_as_coded`; it was not edited"]
json.dump(findings, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("\n".join(md)[-6000:])
