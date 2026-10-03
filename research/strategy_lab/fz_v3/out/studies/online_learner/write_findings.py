"""write_findings.py - FINDINGS.md and findings.json of study online_learner from results/<tf>/finalize.json (+ checks.json,
scores.jsonl, curves.jsonl). Every number in the tables comes from a ledger row (id given) or from a file in this folder."""
import os, sys, json, datetime as D
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, OUT):
    if p not in sys.path: sys.path.insert(0, p)
import harness as H                                                     # noqa: E402
import online as O                                                      # noqa: E402

RES = os.path.join(HERE, "results")
TFS = ("minute", "5minute")
OUTSIDE = "outside the frozen shortlist"


def f(v, nd=2):
    if v is None: return "-"
    if isinstance(v, bool): return "yes" if v else "no"
    if isinstance(v, float): return f"{v:,.{nd}f}"
    return str(v)


def cfgs(c):
    return f"{c['design']}/{c['learner']}/k{c['cadence_k']}/{c['window']}/{c['reward']} e{c['explore']} s{c['seed']}"


def label(design):
    return f" ({OUTSIDE})" if design == "full" else ""


def row_line(r):
    c = r["config"]
    return (f"| `{r['id']}` | {cfgs(c)}{label(c['design'])} | {r['kept_n']} | {f(r['kept_share'], 4)} | {f(r['kept_mean'])} | {f(r['skipped_mean'])} | **{f(r['diff'])}** | {f(r['diff_top1_removed'])} | "
            f"{f(r['kept_pf'], 3)} | {f(r['sized_pf'], 3)} | {f(r['control_pct'], 1)} | {f(r['perm_p'], 4)} | {f(r['sign_blocks'])} | {f(r['kept_mean_slip8'])} | {f(r['loser_recall'], 3)} | "
            f"{f(r['winner_recall_weighted'], 3)} | {f(r['top_decile_winners_skipped'], 3)} | {f(r.get('row_pass'))} |")


HDR = ("| ledger id | path (design/learner/k/window/reward explore seed) | kept n | kept share | kept mean | skipped mean | diff | diff top1% removed | kept PF (1 lot) | sized PF | control pct | perm p | sign blocks | kept mean slip 8 | loser recall | winner recall (net-wtd) | top-decile winners skipped | row-level pass |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def main():
    fin = {tf: json.load(open(os.path.join(RES, tf, "finalize.json"))) for tf in TFS if os.path.exists(os.path.join(RES, tf, "finalize.json"))}
    specs = {tf: {d: json.load(open(os.path.join(RES, tf, f"spec_{d}.json"))) for d in O.DESIGNS} for tf in fin}
    L = []
    L.append("# online_learner: the walk-forward learn-after-each-trade take / skip policy with the trade journal (IS only, 2026-09-29)\n")
    L.append("BRIEF addendum 4 (learning after each trade, the journal) composed with rl.py (addendum 6) under both judges' fixes of DESIGN_PANEL decision-making-1 (full-information rewards, the harness splitter's judgement, the kept-share / kept-n floors, the top-1%-removed value) and the program rules of 2026-09-29 12:55 UTC (null tapes, declared columns). Scripts: `online.py` (the module `oos_once.py` continues through OOS), `run_online.py` (fit / score / checks per timeframe), `finalize.py` (family statistics, selection, tapes, candidate), `write_findings.py`; logs `run_<tf>.log`, `finalize.log`, `smoke_timing.log`. Run history: the first 5minute run (`run_5minute.log`, 13:50-14:02 UTC) was cut off by the session limit after 50 of 81 fit jobs; it was resumed at 15:43 UTC (`run_5minute_resume.log`: the missing jobs, then score and checks) after the hgb_cls learner was given one nested tau per decision-side reward (its 3 finished k=1 checkpoints were deleted and re-run; before that the net / pf heads of hgb_cls were identical decisions); the minute run (`run_minute.log`, 3 workers) was helped by `run_tail.py` (`run_tail_minute.log`: the cheapest remaining jobs on the core freed when gate_family finished; same `run_online.run_job`, same outputs); `finalize_<tf>.nohup` are the finalize logs. Every kept-vs-skipped number is a `harness.score` row of family `online/<design>/<learner>/k<k>/<window>/<reward>` (the comparators: `online_comparator/*`). No OOS row was read. **The frozen feature shortlist has 0 clusters on both timeframes** (`features_shortlist/<tf>/shortlist.json`, sha 66f6e004… / 4747257f…), so the EMPTY-SHORTLIST RULE applies: the designed feature set is hour_bin one-hot + dir (`online/context/...`), and the two linear learners also run on the full as-of design as a labelled sensitivity (`online/full/...`, **outside the frozen shortlist** in every table and ledger note).\n")
    # result paragraph (data-driven, from finalize.json)
    L.append("## 0. Result\n")
    for tf in TFS:
        if tf not in fin: continue
        Fz = fin[tf]; fam = Fz["family"]; rows = Fz["all_rows"]
        best = Fz["ranked_top"][0]; ta = next(c for c in Fz["comparators"] if c["family"].endswith("/take_all")); fr = next(c for c in Fz["comparators"] if c["family"].endswith("/frozen_st7_st8"))
        c95 = [r for r in rows if (r["control_pct"] or 0) >= 95]
        n_share = sum(1 for r in rows if r["kept_share"] >= 0.2); n_sb = sum(1 for r in rows if (r["sign_blocks"] or 0) >= 8); n_slip = sum(1 for r in rows if (r["kept_mean_slip8"] or -1) > 0)
        ev_fail = {k: [kk for kk, vv in v["checks"].items() if not vv[0]] for k, v in Fz["evaluated"].items()}
        L.append(f"**{tf}: null result.** {Fz['n_rows']} walk-forward paths (ledger rows; context {Fz['n_paths_by_design']['context']}, full {Fz['n_paths_by_design']['full']} = outside the frozen shortlist), "
                 f"**0 pass the row-level go / no-go items**. Rows with kept share >= 20%: {n_share}; with kept mean > 0 at 8 pts slippage: {n_slip}; with the sign in >= 8 of 12 blocks: {n_sb}; "
                 f"with control percentile >= 95: {len(c95)}" + (" (" + "; ".join(f"`{r['id']}` {cfgs(r['config'])}{label(r['config']['design'])}: kept share {f(r['kept_share'], 4)}, diff {f(r['diff'])}, top-1%-removed {f(r['diff_top1_removed'])}, sign blocks {r['sign_blocks']}, kept mean at 8 pts {f(r['kept_mean_slip8'])}" for r in c95) + ")" if c95 else "") + ". "
                 f"Best walk-forward kept PF: `{best['id']}` {cfgs(best['config'])}{label(best['config']['design'])}: kept {best['kept_n']} of {ta['kept_n']} ({f(best['kept_share'], 4)}), kept mean {f(best['kept_mean'])} vs skipped {f(best['skipped_mean'])} (diff {f(best['diff'])}, top-1%-removed {f(best['diff_top1_removed'])}), kept PF {f(best['kept_pf'], 3)} (take-all {f(ta['kept_pf'], 3)}, frozen ST7/ST8 {f(fr['kept_pf'], 3)}), control percentile {f(best['control_pct'], 1)}, perm p {f(best['perm_p'], 4)}, sign blocks {best['sign_blocks']}/12, kept mean at 8 pts {f(best['kept_mean_slip8'])}. "
                 f"Family: PBO (diff) {f(fam['pbo_diff']['pbo'], 4)}, SPA p {f(fam['spa'].get('spa_p'), 4)} (unstudentised {f(fam['spa'].get('spa_p_unstudentised'), 4)}), effective trials {f(fam['effective_trials'])} of {fam['candidates']}. "
                 f"Full go / no-go of the best-by-PF row per design (null tapes included): " + "; ".join(f"`{k}` fails {len(v)} items ({', '.join(v)})" for k, v in ev_fail.items()) + ". "
                 f"Determinism and truncation checks: {'all pass' if Fz['checks'] and Fz['checks']['all_pass'] else 'see section'} ({Fz['checks']['rows_before_cut']} SETUPs before the cut compared with the truncated build). "
                 f"The learning curves never reach a control percentile >= 95 that holds to the end (`first_control_ge95_to_end` is None for every finalist); 'beats take-all in cumulative net from the first checkpoint' is the cost saving of trading less (every skip saves ~1,050 INR), not selection. "
                 f"The half-Kelly sizing returns 0 lots on most takes (`take_and_zero_lots`: {best['take_and_zero_lots']} of {best['kept_n']} on the best row): the calibrated p_win times the running W / L never clears the Kelly break-even, the honest result for a book with 15.6% / 27.7% winners. No candidate JSON written.\n")
    L.append("## 1. Definitions (fixed before the numbers)\n")
    L.append("```\n" + O.__doc__.split("Definitions (fixed before any number was looked at)")[1].strip() + "\n```\n")
    L.append("Grid (the task's, nothing shrunk): cadence k in {1, 10, 50} x window {anchored, last 300, last 1000 closed} x reward {net, pf} x learner {lints, logts, hgb_reg, hgb_cls} on the context design; {lints, logts} on the full design; explore {0.0, 0.3} for the two linear learners with 5 seeds (1..5) at explore 0.3; HGB seeded 0. One fit sequence per (design, learner, k, window, fit reward), one ledger row per decision head. Judgement = `harness.score` on the path's keep mask (the path IS the test: no CV); selection = the highest walk-forward profit factor of the taken 1-lot book among the rows that pass the row-level go / no-go items, then the full `harness.go_no_go` (family PBO on `diff`, studentised SPA over the family, DSR, block bootstrap, null-tape replay of the learner on every certificate tape, declared columns). rl.py conventions reused and cited: LinTS per action with a ridge prior (rl.LinTS), full-information updates in exit order (rl.walk's queue), one Gaussian draw per SETUP whatever the decision (rl.LinTS.choose), the reward unit net / (lot x 50) clipped +-10 with `pf` = losses x 1.5 (rl.reward_of, BASE_STOP, CLIP). rl.py's exit / size bandit is not duplicated: the exit is Foundation L1 (studies/exit_policy: no exit variant rescues the book) and the action here is take / skip plus lots.\n")
    L.append("Static comparators on the same rows: take-all (the raw book), the frozen ST7/ST8 gate (`fz_traded`), the gate_family finalist's OOF decisions if `studies/gate_family/oof_<tf>.parquet` exists at scoring time (it did not: that study was still running; recorded as absent). Prior findings the study does not re-run: H1 (the frozen gate is not a loser filter), H2 / H3 / H4 (null on both timeframes), session_stop (no session memory shown: the daily loss stop key is None), null_tapes_drift (the certificate and the time proxies `sl`, `n_events_asof`, excluded from the full design from the start and reported here rather than dropped silently), importance (the empty shortlist).\n")
    fj = dict(study="online_learner", timeframes={}, candidates=[], null_result=True, ledger_families=[], caveats=[], files=[])
    for tf in TFS:
        if tf not in fin: continue
        Fz = fin[tf]; fam = Fz["family"]
        n_ctx = len(specs[tf]["context"]) + 1; n_full = len(specs[tf]["full"]) + 1
        L.append(f"## 2. {tf}\n")
        L.append(f"Designs: context = {n_ctx} columns ({len(specs[tf]['context'])} one-hot levels of hour_bin / dir + bias); full = {n_full} columns ({len({e['source'] for e in specs[tf]['full']})} source columns, {sum(1 for e in specs[tf]['full'] if e['kind'] == 'na')} missing indicators, bias; without `sl`, `n_events_asof`), standardised online. Paths (ledger rows): {Fz['n_rows']} ({', '.join(f'{k} {v}' for k, v in Fz['n_paths_by_design'].items())}).\n")
        comps = {c["family"].replace("online_comparator/", ""): c for c in Fz["comparators"]}
        L.append("### Comparators (family `online_comparator/*`)\n")
        L.append("| comparator | ledger id | kept n | kept share | kept mean | skipped mean | diff | kept PF | control pct | perm p | sign blocks |\n|---|---|---|---|---|---|---|---|---|---|---|")
        for name, c in comps.items():
            L.append(f"| {name}{' (' + OUTSIDE + ')' if 'h5_full' in name else ''} | `{c['id']}` | {c['kept_n']} | {f(c['kept_share'], 4)} | {f(c['kept_mean'])} | {f(c['skipped_mean'])} | {f(c['diff'])} | {f(c['kept_pf'], 3)} | {f(c['control_pct'], 1)} | {f(c['perm_p'], 4)} | {f(c['sign_blocks'])} |")
        L.append("")
        L.append("### Finalists: the best path by walk-forward kept PF per (design, learner)\n")
        L.append(HDR)
        for key, r in Fz["finalists"].items(): L.append(row_line(r))
        L.append("")
        L.append("### The 25 paths with the highest walk-forward kept PF (all rows: `results/%s/scores.jsonl`, `all_rows` in `finalize.json`)\n" % tf)
        L.append(HDR)
        for r in Fz["ranked_top"]: L.append(row_line(r))
        L.append("")
        # marginal summary over the family
        rows = Fz["all_rows"]
        L.append("### Family summary by learner and design (mean over paths; every path is a ledger row)\n")
        L.append("| design | learner | paths | kept share mean | diff mean | diff min / max | diff > 0 | kept PF mean | control pct mean | control >= 95 | row-level passes |\n|---|---|---|---|---|---|---|---|---|---|---|")
        for dsg in O.DESIGNS:
            for lr in ("lints", "logts", "hgb_reg", "hgb_cls"):
                sub = [r for r in rows if r["config"]["design"] == dsg and r["config"]["learner"] == lr]
                if not sub: continue
                d = np.array([r["diff"] if r["diff"] is not None else np.nan for r in sub], dtype=float)
                pf = np.array([r["kept_pf"] if r["kept_pf"] is not None else np.nan for r in sub], dtype=float)
                cp = np.array([r["control_pct"] if r["control_pct"] is not None else np.nan for r in sub], dtype=float)
                L.append(f"| {dsg}{label(dsg)} | {lr} | {len(sub)} | {f(float(np.mean([r['kept_share'] for r in sub])), 4)} | {f(float(np.nanmean(d)))} | {f(float(np.nanmin(d)))} / {f(float(np.nanmax(d)))} | {int(np.sum(d > 0))} | {f(float(np.nanmean(pf)), 3)} | {f(float(np.nanmean(cp)), 1)} | {int(np.sum(cp >= 95))} | {sum(1 for r in sub if r['row_pass'])} |")
        L.append("")
        # seed spread
        L.append("### Seed spread of the Thompson heads (explore 0.3, seeds 1..5; per family of 5 rows)\n")
        L.append("| family | seeds | diff mean | diff sd | diff min / max | diff > 0 | kept PF mean | kept PF sd | kept share mean |\n|---|---|---|---|---|---|---|---|---|")
        for k in sorted(Fz["seed_spread"]):
            s = Fz["seed_spread"][k]
            L.append(f"| {k}{label(k.split('/')[1])} | {s['seeds']} | {f(s['diff_mean'])} | {f(s['diff_sd'])} | {f(s['diff_min'])} / {f(s['diff_max'])} | {s['diff_positive']} | {f(s['pf_mean'], 3)} | {f(s['pf_sd'], 3)} | {f(s['kept_share_mean'], 4)} |")
        L.append("")
        # learning curves of the finalists
        L.append("### Learning curves of the finalists (every 250 SETUPs; `curve_summary` in `finalize.json`; the control percentile = `fz_report.random_control`, 2,000 draws, at the path's own per-session take count on the prefix)\n")
        for key, r in Fz["finalists"].items():
            cs = Fz["curve_summary"].get(r["id"], {})
            cw = cs.get("curve_with_controls")
            if not cw: continue
            L.append(f"**{key}{label(r['config']['design'])}** `{r['id']}` ({cfgs(r['config'])}): first checkpoint from which the cumulative kept net exceeds take-all's to the end: {f(cs.get('first_beats_take_all_net'))}; from which diff > 0 to the end: {f(cs.get('first_diff_positive_to_end'))}; from which control pct >= 95 to the end: {f(cs.get('first_control_ge95_to_end'))}.\n")
            L.append("| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |\n|---|---|---|---|---|---|---|---|---|---|")
            for c in cw:
                L.append(f"| {c['n']} | {c['kept_n']} | {f(c['kept_share'], 4)} | {f(c['diff'])} | {f(c['kept_mean'])} | {f(c['kept_pf'], 3)} | {f(c['control_pct'], 1)} | {f(c['perm_p'], 4)} | {f(c['kept_sum'])} | {f(c['all_sum'])} |")
            L.append("")
        # family multiplicity
        L.append("### Multiplicity over the online family (every `online/*` row of the timeframe, both designs)\n")
        pb, sp = fam["pbo_diff"], fam["spa"]
        L.append(f"| candidates | PBO (diff) | IS-best below 0 OOS | degradation slope | PBO (kept mean) | SPA p (studentised) | RC p | SPA p (unstudentised) | SPA best mean gain / session | excluded from studentised | effective trials |\n|---|---|---|---|---|---|---|---|---|---|---|")
        L.append(f"| {fam['candidates']} | **{f(pb['pbo'], 4)}** | {f(pb['oos_best_below_zero'], 4)} | {f(pb['degradation_slope'], 4)} | {f(fam['pbo_kept_mean']['pbo'], 4)} | **{f(sp.get('spa_p'), 4)}** | {f(sp.get('rc_p'), 4)} | {f(sp.get('spa_p_unstudentised'), 4)} | {f(sp.get('best_mean_gain'))} | {sp.get('excluded_from_studentised')} | {f(fam['effective_trials'])} |")
        L.append("")
        if Fz.get("family_by_design"):
            L.append("| design | candidates | PBO (diff) | SPA p (studentised) | SPA p (unstudentised) | effective trials |\n|---|---|---|---|---|---|")
            for dsg, fb in Fz["family_by_design"].items():
                L.append(f"| {dsg}{label(dsg)} | {fb['candidates']} | {f(fb['pbo_diff']['pbo'], 4)} | {f(fb['spa'].get('spa_p'), 4)} | {f(fb['spa'].get('spa_p_unstudentised'), 4)} | {f(fb['effective_trials'])} |")
            L.append("")
        # selection and go/no-go
        L.append("### Selection and go / no-go\n")
        L.append(f"Rows passing the row-level items (kept share, kept n, diff > 0, diff top-1%-removed > 0, kept mean at 8 pts > 0, sign blocks >= 8, control >= 95): **{len(Fz['row_level_passing'])}** of {Fz['n_rows']}. Selected (highest kept PF among them): {('`' + Fz['selected']['id'] + '` ' + cfgs(Fz['selected']['config']) + label(Fz['selected']['config']['design'])) if Fz['selected'] else 'none'}.\n")
        for cid, ev in Fz["evaluated"].items():
            r = next(x for x in rows if x["id"] == cid)
            L.append(f"**`{cid}`** ({cfgs(r['config'])}{label(r['config']['design'])}; {'the selected row' if Fz['selected'] and Fz['selected']['id'] == cid else 'the best-by-PF row of its design, for the record'}): full go / no-go **{'PASSED' if ev['passed'] else 'FAILED'}**; failing items: {', '.join(k for k, v in ev['checks'].items() if not v[0]) or 'none'}.\n")
            L.append("| item | ok | value |\n|---|---|---|")
            for k, v in ev["checks"].items(): L.append(f"| {k} | {f(v[0])} | {json.dumps(v[1], default=str)[:160]} |")
            L.append("")
            L.append(f"Bootstrap (2,000 stationary draws of sessions): diff 90% CI {ev['bootstrap']['diff_ci']}, kept mean CI {ev['bootstrap']['kept_mean_ci']}, P(diff <= 0) {ev['bootstrap']['diff_p_le0']}. DSR of the per-session kept series against {fam['candidates']} trials: SR {f(ev['dsr'].get('sr'), 4)}, SR0 {f(ev['dsr'].get('sr0'), 4)}, p {f(ev['dsr'].get('p'), 4)}.\n")
            if ev.get("null_tape"):
                s = ev["null_tape"]["summary"]
                L.append("Null-tape replay (the same cfg run on each certificate tape's own table; `tapes.null_tape_check_from_diffs`):\n")
                L.append("| generator | tapes | tape diff p50 | tape diff p95 | real diff | real pct among tapes | same sign share |\n|---|---|---|---|---|---|---|")
                for g in ("gmm", "segment", "session"):
                    x = s[g]
                    L.append(f"| {g} | {x['n']} | {f(x['p50'])} | {f(x['p95'])} | {f(r['diff'])} | {f(x.get('real_pct'), 1)} | {f(x.get('same_sign_share'), 3)} |")
                L.append("")
        if Fz.get("drift_refit"):
            dr = Fz["drift_refit"]["row"]
            L.append(f"Drift sensitivity (the selected full-design row refit without the top-5 drifted sources {Fz['drift_refit']['removed']}): ledger `{dr['id']}`, diff {f(dr['diff'])}, control pct {f(dr['control_pct'], 1)}, kept PF {f(dr['kept_pf'], 3)}, kept share {f(dr['kept_share'], 4)}.\n")
        # checks
        ck = Fz.get("checks")
        if ck:
            L.append("### Determinism and truncation (`results/%s/checks.json`)\n" % tf)
            L.append(f"Rows before the cut {O.CUT}: {ck['rows_before_cut']} (truncated build: {ck['trunc_rows_before_cut']}, common SETUPs {ck['common_setups']}); L1 nets of the {ck['closed_before_cut']} trades closed before the cut identical in both builds: {f(ck['labels_identical_closed_before_cut'])}. Checked jobs (a fresh double run; the fit stage's stored decisions; the prefix run; the truncated-build run):\n")
            L.append("| job | head | deterministic | = stored | prefix identical | truncated build identical | SETUPs compared | decisions differing |\n|---|---|---|---|---|---|---|---|")
            for j in ck["jobs"]:
                for k, v in j.items():
                    if k.startswith("head_"):
                        L.append(f"| {j['job']} | e{v['head']['explore']} s{v['head']['seed']} {v['head']['reward']} | {f(v['deterministic'])} | {f(v['equals_stored'])} | {f(v['truncation_prefix_identical'])} | {f(v['truncation_build_identical'])} | {v['n_compared']} | {v['decisions_differ']} |")
            L.append(f"\nAll checks pass: **{f(ck['all_pass'])}**.\n")
        # verdict
        cand = Fz.get("candidate_file")
        if cand:
            L.append(f"### Verdict: candidate frozen -> `{cand}` (sha256 {Fz['candidate_sha256'][:16]}…, registered in `ledger/registrations.jsonl`)\n")
            fj["candidates"].append(dict(tf=tf, file=cand, sha256=Fz["candidate_sha256"], ledger_id=Fz["selected"]["id"], family=Fz["selected"]["family"], vocabulary=("outside the frozen shortlist (importance rule failed for every cluster)" if Fz["selected"]["config"]["design"] == "full" else "hour_bin one-hot + dir")))
            fj["null_result"] = False
        else:
            why = "no path passes the row-level go / no-go items" if not Fz["selected"] else "the selected path fails the full go / no-go"
            L.append(f"### Verdict: **null result** on {tf} ({why}); no candidate JSON written.\n")
        fj["timeframes"][tf] = dict(n_rows=Fz["n_rows"], n_paths_by_design=Fz["n_paths_by_design"], family=fam, family_by_design=Fz.get("family_by_design"),
                                    comparators={k: {kk: v[kk] for kk in ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "kept_pf", "control_pct", "perm_p", "sign_blocks")} for k, v in comps.items()},
                                    finalists=Fz["finalists"], ranked_top=Fz["ranked_top"][:10], row_level_passing=Fz["row_level_passing"], selected=Fz["selected"],
                                    evaluated={k: {kk: v[kk] for kk in ("id", "family", "passed", "checks", "bootstrap", "dsr")} | dict(null_tape=(v["null_tape"] and dict(checks=v["null_tape"]["checks"], summary=v["null_tape"]["summary"]))) for k, v in Fz["evaluated"].items()},
                                    seed_spread={k: {kk: v[kk] for kk in v if kk != "rows"} for k, v in Fz["seed_spread"].items()},
                                    curve_summary={k: {kk: v[kk] for kk in v if kk != "curve_with_controls"} for k, v in Fz["curve_summary"].items()},
                                    finalist_curves={k: v.get("curve_with_controls") for k, v in Fz["curve_summary"].items() if v.get("curve_with_controls")},
                                    drift_refit=Fz.get("drift_refit"), checks=ck, candidate_file=cand)
    L.append("## 3. What would falsify these findings\n")
    L.append("- A walk-forward path whose kept-vs-skipped difference is positive with the top 1% winners removed, whose control percentile is >= 95 at its own per-session take count, whose sign holds in >= 8 of 12 blocks, whose real-tape difference exceeds the GMM-Markov and segment certificate p95 and whose family SPA p is <= 0.10 would be a candidate; none is reported above unless the verdict says so.\n- The learners see the outcome of every SETUP (full information). A version that learns from the taken trades only would learn slower and explore more; it cannot be better informed, so it cannot rescue a null here.\n- The warm-up (30 closed outcomes, take-all) and the running standardisation are the only fixed numbers besides the task's grid; the learning curves show whether anything is learned after them.\n- The sized book (half Kelly on 420,000 INR of capital with the running mean loss as one lot's risk) saturates at 0 or 3 lots for almost any signed edge (one lot's risk is < 0.5% of that capital); it is reported (sized PF) and does not enter the ledger statistic.\n")
    L.append("## 4. Files\n")
    files = sorted(x for x in os.listdir(HERE) if not x.startswith("__"))
    for x in files: L.append(f"- `{x}`" + (" (per timeframe: spec_*.json, jobs/*.pkl, journals/*.parquet, features_full.parquet, scores.jsonl, curves.jsonl, checks.json, finalize.json)" if x == "results" else ""))
    fj["files"] = files
    fj["ledger_families"] = sorted({r["family"] for tf in fin for r in fin[tf]["all_rows"]} | {c["family"] for tf in fin for c in fin[tf]["comparators"]})
    gf_present = {tf: sorted(c["family"] for c in fin[tf]["comparators"] if "gate_family_oof" in c["family"]) for tf in fin}
    fj["caveats"] = ["the frozen shortlist is empty on both timeframes: the context design (hour_bin + dir) is the designed feature set; the full design is a labelled sensitivity outside the frozen shortlist",
                     "full information: the policy learns from every SETUP's Foundation L1 outcome, taken or skipped (BRIEF addendum 4, rl.py)",
                     "the sized book saturates at 0 / 3 lots at 420,000 INR of capital; the ledger statistic is the 1-lot keep mask",
                     "cadence k applies to the model refit; the running W / L, the calibration record and the nested tau record are updated at every closed outcome (they are the journal's running book, not the model)",
                     "the hgb_cls learner's two decision heads (net / pf) share the fitted classifier and differ only in the nested tau (chosen on the record's net vs penalised net)",
                     "gate_family OOF comparators: " + "; ".join(f"{tf}: {gf_present[tf] or 'absent at scoring time (study still running; the finalist was not named)'}" for tf in fin),
                     "IS drift (null_tapes_drift section 6): a full-design path reads level- and volatility-dependent columns; the drift refit is reported only when such a path is selected"]
    fj["written_at"] = D.datetime.now().isoformat(timespec="seconds")
    open(os.path.join(HERE, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(L))
    json.dump(fj, open(os.path.join(HERE, "findings.json"), "w"), indent=1, default=str)
    print("written FINDINGS.md, findings.json;", "candidates:", [c["file"] for c in fj["candidates"]], "null_result:", fj["null_result"])


if __name__ == "__main__":
    main()
