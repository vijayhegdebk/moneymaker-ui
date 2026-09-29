"""finalize.py - the family statistics, the selection, the null-tape replay, the candidate (or the null result) and the
FINDINGS of study online_learner, from the ledger rows the driver wrote (results/<tf>/scores.jsonl, curves.jsonl, checks.json).

    python finalize.py                 # both timeframes -> results/<tf>/finalize.json, FINDINGS.md, findings.json
    python finalize.py --tf minute     # one timeframe's finalize.json only (no FINDINGS)

Selection (pre-registered in the task): per timeframe, over every online/* path row, the candidate = the row with the highest
walk-forward profit factor of the taken 1-lot book (`kept_pf`) among the rows that pass the row-level go / no-go items
(kept share >= 20%, kept n >= 300 / 80, diff > 0, diff with the top 1% winners removed > 0, kept mean at 8 pts slippage > 0,
sign blocks >= 8 / 12, control percentile >= 95); then harness.go_no_go with the family PBO (statistic diff, every online/*
row of the timeframe), the studentised SPA p over the family, the DSR of the per-session kept series against the family's
size and Sharpe variance, the session block-bootstrap CI of the diff, the null-tape replay (the learner run on every certificate
tape's own table with the same cfg; tapes.null_tape_check_from_diffs) and the declared columns. A row from online/full carries
the provenance "outside the frozen shortlist (importance rule failed for every cluster)". If no row passes the row-level items
the result is null; the best-by-PF row per design is still put through the full go / no-go (tapes included) for the record.
The learning curve with the 2,000-draw control percentile at every 250 SETUPs is computed for the finalists (best by PF per
design x learner); the cheap curve of every path is in curves.jsonl. Tape numbers never enter the ledger.
"""
import os, sys, json, time, math, pickle, argparse, hashlib, datetime as D
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, OUT, os.path.join(OUT, "studies", "null_tapes_drift")):
    if p not in sys.path: sys.path.insert(0, p)
import harness as H                                                     # noqa: E402
import online as O                                                      # noqa: E402
import tapes                                                            # noqa: E402
import run_online as R                                                  # noqa: E402

RES = os.path.join(HERE, "results")
TFS = ("minute", "5minute")
ROW_ITEMS = ("kept_share>=20%", "diff>0", "diff_top1_removed>0", "kept_mean_slip8>0", "sign_blocks>=8/12", "control_pct>=95")
OUTSIDE = "outside the frozen shortlist (importance rule failed for every cluster)"


def read_scores(tf):
    p = os.path.join(RES, tf, "scores.jsonl")
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return [r for r in rows if r["family"].startswith("online/")], [r for r in rows if r["family"].startswith("online_comparator/")]


def read_curves(tf):
    p = os.path.join(RES, tf, "curves.jsonl")
    return {json.loads(l)["id"]: json.loads(l)["curve"] for l in open(p, encoding="utf-8") if l.strip()}


def row_pass(r, tf):
    ok, ch = H.go_no_go(r, tf)
    return all(ch[k][0] for k in ROW_ITEMS) and ch[f"kept_n>={H.GO['kept_n_min'][tf]}"][0], ch


def per_session_kept(vec):
    m = vec["kept_n"] > 0
    return np.where(m, vec["kept_sum"] / np.maximum(vec["kept_n"], 1), 0.0)[m]


def family_stats(tf, rows):
    vecs = [H.load_vectors(r["id"]) for r in rows]
    pb = H.pbo(vecs, "diff"); pk = H.pbo(vecs, "kept_mean")
    sp = H.spa(vecs, tag=f"online|{tf}")
    eff = H.effective_trials(vecs)
    srs = []
    for v in vecs:
        x = per_session_kept(v)
        srs.append(float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan)
    return dict(candidates=len(rows), pbo_diff=pb, pbo_kept_mean=pk, spa=sp, effective_trials=eff,
                sr_var_trials=float(np.nanvar(np.asarray(srs), ddof=1)) if np.isfinite(srs).sum() > 1 else None), vecs


def curve_with_controls(T, keep, rows):
    out = []
    pts = list(range(R.CURVE_STEP, len(rows), R.CURVE_STEP)) + [len(rows)]
    for m in pts:
        r = rows[:m]; mt = H.metrics(T, keep, r, f"online|curve|{T.tf}|{m}", controls=True)
        out.append(dict(n=m, kept_n=mt["kept_n"], kept_share=mt["kept_share"], diff=mt["diff"], kept_mean=mt["kept_mean"], kept_pf=mt["kept_pf"],
                        control_pct=mt["control_pct"], perm_p=mt["perm_p"], kept_sum=round(float(T.net[r][keep[r]].sum()), 2), all_sum=round(float(T.net[r].sum()), 2)))
    return out


def first_beat(curve, key, thr):
    """The first checkpoint from which the statistic stays above thr to the end (None when it never does)."""
    ok = [(c["n"], (c.get(key) is not None) and c[key] > thr) for c in curve]
    for i, (n, v) in enumerate(ok):
        if v and all(x for _, x in ok[i:]): return n
    return None


def head_of(r):
    return dict(explore=r["config"]["explore"], seed=r["config"]["seed"], reward=r["config"]["reward"])


def full_cfg(tf, r):
    spec = R.load_spec(tf, r["config"]["design"])
    c = dict(r["config"]); c.pop("encoded_sha", None); c.pop("n_encoded", None); c.pop("n_columns", None)
    c = O.with_defaults(c); c["encoded"] = spec; c["columns"] = sorted({e["source"] for e in spec})
    return c


def keep_of(tf, T, r):
    """The stored keep mask of a ledger row (from the job checkpoint) - the same decisions the row was scored on."""
    J = pickle.load(open(os.path.join(RES, tf, "jobs", r["job"] + ".pkl"), "rb"))
    h = next(x for x in J["heads"] if x["head"] == r["head"])
    keep = np.zeros(T.n, dtype=bool); keep[J["rows"]] = h["keep"]
    return keep, h


def tape_replay(tf, cfg, real_diff, log):
    """The learner with the same cfg on every certificate tape's own table (tapes.tape_folders(tf, gen)); the tape's
    kept-vs-skipped diff through harness.metrics (controls off). Returns (passed, checks, summary)."""
    diffs, per = {}, []
    for g in ("gmm", "segment", "session"):
        diffs[g] = []
        for folder in tapes.tape_folders(tf, g):
            t0 = time.time(); Tt = tapes.load_tape(folder); rows = np.flatnonzero(Tt.is_mask)
            dec, _, _ = O.run(Tt, cfg, rows)
            keep = np.zeros(Tt.n, dtype=bool); keep[rows] = [d["take"] for d in dec]
            m = tapes.evaluate_keep(Tt, keep, f"tape|{os.path.basename(folder)}|online", controls=False)
            d = m["diff"]; diffs[g].append(np.nan if d is None else d)
            per.append(dict(tape=os.path.relpath(folder, OUT), gen=g, n=m["n"], kept_n=m["kept_n"], kept_share=m["kept_share"], diff=d, kept_pf=m["kept_pf"], seconds=round(time.time() - t0, 1)))
            log(f"    tape {os.path.basename(folder):<12} n {m['n']:>5} kept {m['kept_share']!s:>6} diff {d!s:>9} ({time.time() - t0:.0f}s)")
    passed, ch, summ = tapes.null_tape_check_from_diffs(real_diff, diffs)
    summ.update(tf=tf, real_diff=real_diff, per_tape=per, tape_set="certificate (healthy, first DESIGN_N per generator)")
    return passed, ch, summ


def evaluate_finalist(tf, T, r, fam, vecs_by_id, log, run_tapes=True):
    """Everything harness.go_no_go needs for one row: family PBO / SPA / DSR, bootstrap, tapes, columns."""
    cfg = full_cfg(tf, r)
    vec = H.load_vectors(r["id"])
    boot = H.bootstrap_ci(vec, tag=f"online|{tf}|{r['id']}")
    x = per_session_kept(vec)
    dsr = H.deflated_sharpe(x, fam["candidates"], fam["sr_var_trials"] if fam["sr_var_trials"] else None)
    nt = None; nt_summary = None
    if run_tapes:
        log(f"  null tapes for {r['id']} ({r['family']}, explore {cfg['explore']}, seed {cfg['seed']})")
        passed_t, nt, nt_summary = tape_replay(tf, cfg, r["diff"], log)
    cols = cfg["columns"] + ["hour_bin", "dir"] if cfg["design"] == "context" else cfg["columns"]
    passed, ch = H.go_no_go(r, tf, cpcv=None, pbo_value=fam["pbo_diff"]["pbo"], dsr=dsr, spa_p=fam["spa"]["spa_p"], boot=boot, null_tape=nt, columns=sorted(set(cols)))
    return dict(id=r["id"], family=r["family"], head=r["head"], job=r["job"], passed=bool(passed), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()},
                bootstrap=boot, dsr=dsr, null_tape=(dict(checks={k: [bool(v[0]), v[1]] for k, v in nt.items()}, summary={k: v for k, v in nt_summary.items() if k != "per_tape"},
                                                       per_tape=nt_summary["per_tape"]) if nt is not None else None), cfg=cfg)


def finalize_tf(tf, log):
    T = H.load(tf); rows_is = np.flatnonzero(T.is_mask)
    onl, comps = read_scores(tf); curves = read_curves(tf)
    checks = json.load(open(os.path.join(RES, tf, "checks.json"))) if os.path.exists(os.path.join(RES, tf, "checks.json")) else None
    log(f"[{tf}] {len(onl)} online rows, {len(comps)} comparator rows")
    fam, vecs = family_stats(tf, onl)
    by_design = {}
    for dsg in O.DESIGNS:
        sub = [r for r in onl if r["config"]["design"] == dsg]
        if len(sub) >= 2: by_design[dsg] = family_stats(tf, sub)[0]
    # row-level pass, ranking by kept_pf
    for r in onl:
        r["row_pass"], ch = row_pass(r, tf); r["row_checks"] = {k: [bool(v[0]), v[1]] for k, v in ch.items()}
    ranked = sorted(onl, key=lambda r: (-(r["kept_pf"] if r["kept_pf"] is not None else -1), -(r["diff"] if r["diff"] is not None else -1e9)))
    passing = [r for r in ranked if r["row_pass"]]
    # finalists: best by kept_pf per (design, learner)
    finalists = {}
    for r in ranked:
        key = (r["config"]["design"], r["config"]["learner"])
        if key not in finalists: finalists[key] = r
    # learning curves with controls for the finalists
    curves_ctrl = {}
    for key, r in finalists.items():
        keep, _ = keep_of(tf, T, r)
        curves_ctrl[r["id"]] = curve_with_controls(T, keep, rows_is)
        log(f"[{tf}] finalist {key}: {r['id']} kept_pf {r['kept_pf']} diff {r['diff']} ctrl {r['control_pct']} row_pass {r['row_pass']}")
    # the selected candidate (best PF among the row-level passes) and the best-by-PF per design, with the full go / no-go
    evaluated = {}
    selected = passing[0] if passing else None
    to_eval = ([selected] if selected else []) + [next(r for r in ranked if r["config"]["design"] == dsg) for dsg in O.DESIGNS if any(r["config"]["design"] == dsg for r in ranked)]
    seen = set()
    for r in to_eval:
        if r["id"] in seen: continue
        seen.add(r["id"])
        evaluated[r["id"]] = evaluate_finalist(tf, T, r, fam, None, log)
        log(f"[{tf}] full go/no-go {r['id']}: passed {evaluated[r['id']]['passed']}; failing {[k for k, v in evaluated[r['id']]['checks'].items() if not v[0]]}")
    # drift sensitivity for a full-design finalist that is the selected candidate: refit without the top-5 drifted sources
    drift_refit = None
    if selected and selected["config"]["design"] == "full":
        dj = json.load(open(os.path.join(OUT, "studies", "null_tapes_drift", "drift.json")))
        top5 = list(dj.get("timeframes", {}).get(tf, {}).get("top5_sources") or [])
        if top5:
            cfg = full_cfg(tf, selected); cfg["encoded"] = [e for e in cfg["encoded"] if e["source"] not in top5]; cfg["columns"] = sorted({e["source"] for e in cfg["encoded"]})
            dec, _, _ = O.run(T, cfg, rows_is); keep = np.zeros(T.n, dtype=bool); keep[rows_is] = [d["take"] for d in dec]
            c2 = R.ledger_config(cfg); c2["drift_top5_removed"] = top5
            res = H.score(T, keep, R.family(c2).replace("online/full/", "online/full_minus_drift5/"), c2, script=__file__)
            drift_refit = dict(removed=top5, row=res)
            log(f"[{tf}] drift refit without {top5}: diff {res['diff']} ctrl {res['control_pct']} kept_pf {res['kept_pf']}")
    # seed spread of the Thompson heads
    spread = []
    for r in onl:
        if r["config"]["explore"] > 0: spread.append(r)
    sp_tab = {}
    for r in spread:
        key = r["family"]
        sp_tab.setdefault(key, []).append(dict(seed=r["config"]["seed"], diff=r["diff"], kept_share=r["kept_share"], kept_pf=r["kept_pf"], control_pct=r["control_pct"], id=r["id"]))
    spread_summary = {}
    for k, lst in sp_tab.items():
        d = np.array([x["diff"] if x["diff"] is not None else np.nan for x in lst], dtype=float)
        pf = np.array([x["kept_pf"] if x["kept_pf"] is not None else np.nan for x in lst], dtype=float)
        spread_summary[k] = dict(seeds=len(lst), diff_mean=round(float(np.nanmean(d)), 2) if np.isfinite(d).any() else None, diff_sd=round(float(np.nanstd(d, ddof=1)), 2) if np.isfinite(d).sum() > 1 else None,
                                 diff_min=round(float(np.nanmin(d)), 2) if np.isfinite(d).any() else None, diff_max=round(float(np.nanmax(d)), 2) if np.isfinite(d).any() else None,
                                 diff_positive=int((d > 0).sum()), pf_mean=round(float(np.nanmean(pf)), 3) if np.isfinite(pf).any() else None, pf_sd=round(float(np.nanstd(pf, ddof=1)), 3) if np.isfinite(pf).sum() > 1 else None,
                                 kept_share_mean=round(float(np.mean([x["kept_share"] for x in lst])), 4), rows=lst)
    # learning-curve summaries for every path (cheap curves)
    curve_summary = {}
    for r in onl:
        c = curves.get(r["id"])
        if not c: continue
        curve_summary[r["id"]] = dict(first_beats_take_all_net=first_beat([dict(n=x["n"], v=(x["kept_sum"] - x["all_sum"])) for x in c], "v", 0.0),
                                      first_diff_positive_to_end=first_beat(c, "diff", 0.0), final=c[-1])
    for cid, c in curves_ctrl.items():
        curve_summary[cid]["first_control_ge95_to_end"] = first_beat(c, "control_pct", 95.0 - 1e-9)
        curve_summary[cid]["curve_with_controls"] = c
    out = dict(tf=tf, n_rows=len(onl), n_paths_by_design={d: sum(1 for r in onl if r["config"]["design"] == d) for d in O.DESIGNS},
               family=fam, family_by_design=by_design, comparators=comps, ranked_top=[_brief(r) for r in ranked[:25]],
               row_level_passing=[_brief(r) for r in passing], selected=(_brief(selected) if selected else None),
               evaluated=evaluated, finalists={f"{k[0]}/{k[1]}": _brief(r) for k, r in finalists.items()}, seed_spread=spread_summary,
               curve_summary=curve_summary, drift_refit=drift_refit, checks=checks, all_rows=[_brief(r) for r in onl])
    # freeze the candidate when the full go / no-go passes
    cand = None
    if selected and evaluated[selected["id"]]["passed"]:
        ev = evaluated[selected["id"]]; cfg = ev["cfg"]
        cand = dict(kind="online", timeframe=tf, label="L1", study="online_learner", cfg=cfg, columns=cfg["columns"],
                    provenance=dict(source="learned walk-forward on IS 2021-10..2025-12 (the path is the test)", script="studies/online_learner/run_online.py + finalize.py",
                                    ledger_id=selected["id"], family=selected["family"], statistic={k: selected[k] for k in ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "kept_pf", "control_pct", "perm_p", "sign_blocks", "kept_mean_slip8")},
                                    vocabulary=(OUTSIDE if cfg["design"] == "full" else "hour_bin one-hot + dir (EMPTY-SHORTLIST RULE: the frozen shortlist has 0 clusters)"),
                                    null_tape=dict(checks=ev["null_tape"]["checks"], summary=ev["null_tape"]["summary"]), go_no_go=dict(passed=True, checks=ev["checks"]),
                                    pbo=fam["pbo_diff"], spa=fam["spa"], dsr=ev["dsr"], bootstrap=ev["bootstrap"], effective_trials=fam["effective_trials"],
                                    frozen_at=D.datetime.now().isoformat(timespec="seconds"), exit="Foundation L1 (studies/exit_policy: no exit variant rescues the book)",
                                    composition="rl.py conventions: full-information updates in exit-bar order, one seeded normal per SETUP, reward = net / (LOT x 50) clipped +-10, pf = losses x 1.5; the exit / size bandit of rl.py is not duplicated"))
        os.makedirs(os.path.join(OUT, "candidates"), exist_ok=True)
        cp = os.path.join(OUT, "candidates", f"online_{tf}.json")
        json.dump(cand, open(cp, "w"), indent=1, default=str)
        sh = hashlib.sha256(open(cp, "rb").read()).hexdigest()
        with open(os.path.join(H.LEDGER, "registrations.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(kind="candidate", what=f"online learner {tf}", file=os.path.relpath(cp, OUT), sha256=sh, ledger_id=selected["id"], family=selected["family"],
                                    registered_at=D.datetime.now().isoformat(timespec="seconds"), ledger_sha_at_registration=H.ledger_sha(), vocabulary=cand["provenance"]["vocabulary"])) + "\n")
        out["candidate_file"] = os.path.relpath(cp, OUT); out["candidate_sha256"] = sh
        log(f"[{tf}] CANDIDATE frozen: {cp} sha {sh[:16]}")
    else:
        out["candidate_file"] = None
        log(f"[{tf}] null result: {'no row passes the row-level items' if not selected else 'the selected row fails the full go/no-go'}")
    json.dump(out, open(os.path.join(RES, tf, "finalize.json"), "w"), indent=1, default=str)
    return out


def _brief(r):
    keys = ("id", "family", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "kept_pf", "kept_t", "control_pct", "perm_p", "sign_blocks",
            "kept_mean_slip8", "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "kept_sessions", "sized_pf", "sized_net", "lots_mean_taken", "take_and_zero_lots", "row_pass")
    d = {k: r.get(k) for k in keys}
    d["config"] = {k: r["config"].get(k) for k in ("design", "learner", "cadence_k", "window", "reward", "explore", "seed")}
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", default=None); a = ap.parse_args()
    logf = open(os.path.join(HERE, "finalize.log"), "a", encoding="utf-8")

    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    log(f"finalize start {D.datetime.now().isoformat(timespec='seconds')}")
    for tf in ([a.tf] if a.tf else TFS):
        finalize_tf(tf, log)
    log(f"finalize done {D.datetime.now().isoformat(timespec='seconds')}; ledger sha {H.ledger_sha()}")
