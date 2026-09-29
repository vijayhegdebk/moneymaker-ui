"""Study null_tapes_drift, part (c): generate the null tapes, push every one through the real pipeline (build.py), evaluate the
frozen ST7/ST8 gate and the two mechanical reference gates (fixed in tapes.py before any tape was scored) on each tape's own
feature table, run the reality check and the engine-health check, and write the null distributions. Tape numbers never enter
OUT/ledger; the real-tape reference gates are scored once through harness.score (family null_tapes_drift/real_ref) so the
comparison numbers are ledger rows.

    python run_tapes.py --tf 5minute --n 20 --workers 3            # 20 full-length (IS calendar, 1,026 sessions) tapes per generator
    python run_tapes.py --tf minute --n 8 --one-year --workers 2   # 8 one-year (247 IS sessions) tapes per generator
    python run_tapes.py --tf 5minute --n 20 --workers 3 --target-healthy 20   # repair round: top up with the next seeds (k = n, n+1, ...)
                                                                              # until 20 HEALTHY tapes per generator exist (tapes.tape_health)
    python run_tapes.py --tf 5minute --n 20 --aggregate-only       # recompute health, sets and null_distributions.json only

Outputs (study folder): fit_<tf>.json, tapes/<tf>/<gen>_<k>/{tape_meta.json, build.log, meta.json, tape_health.json, *.parquet},
tape_results.jsonl (one line per tape x gate), tape_results.csv, reality_check.csv, tape_health.csv, real_reference_<tf>.json,
real_health_<tf>.json, null_distributions.json (all timeframes merged, rewritten on every run). fz_card.parquet and swings.parquet
of a built tape are removed (never read here; ~10 MB each) and tape.csv is kept for k = 0 only (every tape reproduces from its
seed: gen_tapes.write_tape).

Tape sets in null_distributions.json (repair round; the refuters found the engine locked out on 12 of the 84 first-build tapes):
  gates                  = the CERTIFICATE: the first DESIGN_N healthy tapes per generator by seed index k (tapes.tape_folders default)
  gates_all_original     = the first build (k < DESIGN_N), locked tapes included (what the first FINDINGS reported)
  gates_healthy_original = the first build restricted to its healthy tapes (the refuters' recomputation)
"""
import os, sys, json, time, argparse, subprocess, glob, math
sys.dont_write_bytecode = True
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, OUT)
import gen_tapes as G, tapes, harness as H                             # noqa: E402

BUILD = os.path.join(OUT, "build", "build.py")
RESULTS = os.path.join(HERE, "tape_results.jsonl")
REALITY = os.path.join(HERE, "reality.jsonl")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_tape(tf, folder):
    """build.py on the tape (subprocess, its own log); returns (ok, seconds, peak rss MB)."""
    csv_path = os.path.join(folder, "tape.csv")
    t0 = time.time()
    with open(os.path.join(folder, "build.log"), "w") as lf:
        p = subprocess.run([sys.executable, BUILD, "--tf", tf, "--path", csv_path, "--out", folder], stdout=lf, stderr=subprocess.STDOUT, cwd=HERE)
    ok = p.returncode == 0 and os.path.exists(os.path.join(folder, "features.parquet"))
    rss = None
    if ok:
        rss = json.load(open(os.path.join(folder, "meta.json"))).get("peak_rss_mb")
    return ok, round(time.time() - t0, 1), rss


def evaluate_tape(tf, gen, k, folder):
    """The three reference gates through harness.metrics on the tape's own L1 units + the reality check + the health check."""
    T = tapes.load_tape(folder)
    masks, info = tapes.mechanical_masks(T)
    rows = []
    for name, keep in masks.items():
        m = tapes.evaluate_keep(T, keep, f"tape|{tf}|{gen}_{k}|{name}")
        rows.append(dict(tf=tf, gen=gen, k=k, gate=name, tape=os.path.relpath(folder, HERE), **info, **m))
    rc = dict(tf=tf, gen=gen, k=k, tape=os.path.relpath(folder, HERE), **tapes.reality_check(folder))
    hl = tapes.tape_health(folder)
    return rows, rc, hl


def tidy(folder, keep_csv):
    for f in ("fz_card.parquet", "swings.parquet"):
        p = os.path.join(folder, f)
        if os.path.exists(p): os.remove(p)
    if not keep_csv and os.path.exists(os.path.join(folder, "tape.csv")): os.remove(os.path.join(folder, "tape.csv"))


def real_reference(tf, script):
    """The same three gates on the real tape, IS rows, as ledger rows (family null_tapes_drift/real_ref) + the reality check."""
    T = H.load(tf)
    masks, info = tapes.mechanical_masks(T)
    out = {}
    for name, keep in masks.items():
        cfg = dict(gate=name, definition=tapes.MECHANICAL_GATES[name], **({"sl_dist_atr_is_median": info["sl_dist_atr_is_median"]} if name == "sl_above_median_skip" else {}))
        r = H.score(T, keep, "null_tapes_drift/real_ref", cfg, script=script, note="reference gate for the null-tape certificate (part c)")
        out[name] = {k: r[k] for k in ("id", "n", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct",
                                       "loser_recall", "winner_recall_weighted", "top_decile_winners_skipped", "sign_blocks", "kept_mean_slip8")}
    real_rc = dict(tf=tf, gen="REAL", k=-1, tape=os.path.relpath(os.path.join(OUT, "data", tf), HERE), **tapes.reality_check(os.path.join(OUT, "data", tf)))
    return dict(tf=tf, label="L1", split="IS", gates=out, sl_dist_atr_is_median=info["sl_dist_atr_is_median"], reality=real_rc)


# ---------------------------------------------------------------- aggregation
HEALTH_COLS = ["healthy", "dead_share", "dead_sessions", "dead_tail_share", "longest_frozen_run_sessions", "longest_choch_free_sessions",
               "setup_rate_ratio_to_real", "last_choch_date", "last_setup_time", "prot_last", "close_last", "prot_gap_pts"]


def health_table():
    """tape_health.json for every built tape (computed when missing) -> DataFrame (+ tape_health.csv)."""
    rows = []
    for tf in ("5minute", "minute"):
        for f in tapes.all_tape_folders(tf):
            rows.append(tapes.read_health(f))
    if not rows: return pd.DataFrame(columns=["tf", "gen", "k"] + HEALTH_COLS)
    HL = pd.DataFrame(rows).sort_values(["tf", "gen", "k"])
    cert = set()
    for tf in HL.tf.unique():
        cert |= {os.path.relpath(p, HERE) for p in tapes.tape_folders(tf)}
    HL["in_certificate"] = HL.tape.isin(cert)
    HL["original"] = [k < tapes.DESIGN_N[tf] for tf, k in zip(HL.tf, HL.k)]
    HL.to_csv(os.path.join(HERE, "tape_health.csv"), index=False)
    return HL


def gate_stats(s, real):
    """Null-distribution summary of one (tf, gen, gate) set of tape rows against the real-tape gate `real`."""
    q = lambda v, p: round(float(np.nanquantile(v, p)), 2) if len(v) and np.isfinite(v).any() else None
    dv = s["diff"].to_numpy(dtype=float); cv = s["control_pct"].to_numpy(dtype=float)
    rd = real.get("diff")
    return dict(n=int(len(s)), tapes=sorted(int(k) for k in s.k), diff_p5=q(dv, 0.05), diff_p50=q(dv, 0.5), diff_p95=q(dv, 0.95),
                diff_mean=(round(float(np.nanmean(dv)), 2) if len(dv) else None), diff_min=q(dv, 0.0), diff_max=q(dv, 1.0),
                diff_share_positive=(round(float(np.nanmean(dv > 0)), 3) if len(dv) else None),
                control_pct_p50=q(cv, 0.5), control_pct_p95=q(cv, 0.95), control_pct_share_ge95=(round(float(np.nanmean(cv >= 95)), 3) if len(cv) else None),
                kept_share_p50=q(s.kept_share.to_numpy(dtype=float), 0.5), units_p50=q(s.n.to_numpy(dtype=float), 0.5),
                units_min=q(s.n.to_numpy(dtype=float), 0.0), units_max=q(s.n.to_numpy(dtype=float), 1.0),
                real_diff=rd, real_control_pct=real.get("control_pct"),
                real_above_tape_p95=(rd is not None and q(dv, 0.95) is not None and rd > q(dv, 0.95)),
                real_diff_percentile_in_tapes=(round(float(100 * np.nanmean(dv < rd)), 1) if rd is not None and len(dv) else None),
                tapes_same_sign_as_real=(round(float(np.nanmean(np.sign(dv) == np.sign(rd))), 3) if rd is not None and len(dv) else None))


def aggregate():
    """null_distributions.json + tape_results.csv + reality_check.csv + tape_health.csv from tape_results.jsonl, reality.jsonl and
    the per-tape tape_health.json files. Three tape sets per gate (module docstring)."""
    rows = [json.loads(x) for x in open(RESULTS, encoding="utf-8") if x.strip()] if os.path.exists(RESULTS) else []
    if not rows: return None
    HL = health_table()
    hcols = ["tape"] + HEALTH_COLS + ["in_certificate", "original"]
    R = pd.DataFrame(rows).drop_duplicates(subset=["tf", "gen", "k", "gate"], keep="last").sort_values(["tf", "gen", "k", "gate"])
    R = R.merge(HL[hcols], on="tape", how="left")
    R.to_csv(os.path.join(HERE, "tape_results.csv"), index=False)
    rc_rows = [json.loads(x) for x in open(REALITY, encoding="utf-8") if x.strip()]
    RC = pd.DataFrame(rc_rows).drop_duplicates(subset=["tf", "gen", "k"], keep="last").sort_values(["tf", "gen", "k"])
    RC = RC.merge(HL[[c for c in hcols if c == "tape" or c not in RC.columns]], on="tape", how="left")   # bar_stats already carries close_last
    RC.to_csv(os.path.join(HERE, "reality_check.csv"), index=False)
    ref = {}
    for p in glob.glob(os.path.join(HERE, "real_reference_*.json")): d = json.load(open(p)); ref[d["tf"]] = d
    q = lambda v, p: round(float(np.nanquantile(v, p)), 2) if len(v) and np.isfinite(v).any() else None
    null = dict(study="null_tapes_drift", statistic="kept-vs-skipped mean L1 net (INR per unit) on the tape's own feature table, all tape rows (IS calendar)",
                certificate_set=("gates = the first DESIGN_N healthy tapes per generator by seed index k (tapes.tape_folders(tf, gen) default; "
                                 "tapes.tape_health: dead share < 0.2 of sessions inside frozen-prot CHoCH-free runs longer than the real tape's longest, "
                                 "and SETUP rate >= 1/3 x real). gates_all_original = the first build (k < DESIGN_N) with the locked tapes; "
                                 "gates_healthy_original = the first build's healthy tapes only. The pass rule reads `gates`."),
                how_to_compare=("a candidate's real-tape diff (its ledger row) is compared with p95 of the tape diffs of the SAME gate family shape on the certificate "
                                "set; the certificate field null_tape_diff_inr = {p50, p95} per generator; pass = real diff > gmm p95 and > segment p95 (the two "
                                "memory-free nulls), and the session-bootstrap diffs share the real diff's sign in >= 75% of tapes (stability); evaluate a rule list "
                                "on the tapes with tapes.null_tape_check(real_diff, tf, rules) (= tapes.evaluate_rule_list(folder, rules) over tapes.tape_folders(tf, gen))"),
                health_rule=dict(tapes.HEALTH, dead_run_longer_than_real_longest_frozen_run=True, design_n=tapes.DESIGN_N), timeframes={})
    for tf in sorted(R.tf.unique()):
        rh = tapes.real_health(tf)
        d = dict(real_reference=ref.get(tf, {}).get("gates"), real_reality=ref.get(tf, {}).get("reality"), real_health=rh, generators={})
        for gen in sorted(R[R.tf == tf].gen.unique()):
            Rg = R[(R.tf == tf) & (R.gen == gen)]; Hg = HL[(HL.tf == tf) & (HL.gen == gen)]
            n0 = tapes.DESIGN_N[tf]
            sets = {"gates": Rg[Rg.in_certificate.astype(bool)], "gates_all_original": Rg[Rg.k < n0], "gates_healthy_original": Rg[(Rg.k < n0) & Rg.healthy.astype(bool)]}
            g = dict(tapes=int(Rg.k.nunique()), tapes_built=int(Hg.k.nunique()), tapes_original=int((Hg.k < n0).sum()), tapes_healthy=int(Hg.healthy.astype(bool).sum()),
                     tapes_certificate=int(Hg.in_certificate.astype(bool).sum()), tapes_locked_original=int(((Hg.k < n0) & ~Hg.healthy.astype(bool)).sum()),
                     lockout_rate_original=round(float(((Hg.k < n0) & ~Hg.healthy.astype(bool)).sum() / max(1, (Hg.k < n0).sum())), 3),
                     lockout_rate_all_built=round(float((~Hg.healthy.astype(bool)).sum() / max(1, len(Hg))), 3),
                     certificate_tapes=sorted(int(k) for k in Hg[Hg.in_certificate.astype(bool)].k),
                     locked_tapes=[{k_: (None if (isinstance(v, float) and np.isnan(v)) else v) for k_, v in r.items()} for r in
                                   Hg[~Hg.healthy.astype(bool)][["k", "tape", "dead_sessions", "dead_share", "dead_tail_share", "longest_frozen_run_sessions",
                                                                 "longest_choch_free_sessions", "last_choch_date", "last_setup_time", "setups_per_session",
                                                                 "setup_rate_ratio_to_real", "prot_last", "close_last", "prot_gap_pts", "reasons"]].to_dict("records")])
            for name, S_ in sets.items():
                g[name] = {}
                for gate in sorted(R.gate.unique()):
                    real = (ref.get(tf, {}).get("gates") or {}).get(gate, {})
                    g[name][gate] = gate_stats(S_[S_.gate == gate], real)
            # units per tape in the locked tapes (the refuters' 78 vs 1,211 spread) from the frozen gate rows
            fr = Rg[Rg.gate == "frozen_st7_st8"]
            g["units_per_tape"] = dict(all_built_min=int(fr.n.min()), all_built_max=int(fr.n.max()), certificate_min=int(fr[fr.in_certificate.astype(bool)].n.min()) if fr.in_certificate.astype(bool).any() else None,
                                       certificate_max=int(fr[fr.in_certificate.astype(bool)].n.max()) if fr.in_certificate.astype(bool).any() else None,
                                       locked=[int(x) for x in fr[~fr.healthy.astype(bool)].n])
            rcg = RC[(RC.tf == tf) & (RC.gen == gen)]; rcr = RC[(RC.tf == tf) & (RC.gen == "REAL")]
            keys = ["ret_std_bps", "ret_kurt_excess", "absret_ac1", "absret_ac2", "absret_ac3", "absret_ac4", "absret_ac5", "choch_per_session", "bos_per_session",
                    "setups_per_session", "l1_units_per_session", "l1_mean_net", "l1_win_rate", "frozen_kept_share", "close_last", "atr14_median"]
            def reality_of(sub):
                return {kk: dict(tape_p50=q(sub[kk].to_numpy(dtype=float), 0.5), tape_min=q(sub[kk].to_numpy(dtype=float), 0), tape_max=q(sub[kk].to_numpy(dtype=float), 1),
                                 real=(float(rcr[kk].iloc[0]) if len(rcr) else None),
                                 ratio_p50_to_real=(round(float(np.nanmedian(sub[kk]) / rcr[kk].iloc[0]), 3) if len(rcr) and rcr[kk].iloc[0] and len(sub) else None)) for kk in keys}
            g["reality"] = reality_of(rcg)                                                     # every tape built (the generator as it is)
            g["reality_certificate"] = reality_of(rcg[rcg.in_certificate.astype(bool)])         # the certificate tapes
            g["poor_null_flag"] = (g["reality"]["setups_per_session"]["ratio_p50_to_real"] is not None and
                                   not (1 / 3 <= g["reality"]["setups_per_session"]["ratio_p50_to_real"] <= 3))   # the generator-level flag (median rate)
            g["poor_null_tapes"] = sorted(int(k) for k in Hg[~Hg.healthy.astype(bool)].k)                       # the per-tape flag (repair round)
            d["generators"][gen] = g
        null["timeframes"][tf] = d
    json.dump(null, open(os.path.join(HERE, "null_distributions.json"), "w"), indent=1, default=str)
    return null


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", required=True, choices=("minute", "5minute")); ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--one-year", action="store_true"); ap.add_argument("--gens", default=",".join(G.GENS))
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--target-healthy", type=int, default=None, help="top up with the next seeds until this many HEALTHY tapes per generator exist")
    a = ap.parse_args()
    if a.aggregate_only:
        null = aggregate(); log("aggregated")
        if null:
            for tf, d in null["timeframes"].items():
                for g_, v in d["generators"].items():
                    log(f"{tf} {g_}: built {v['tapes_built']}, healthy {v['tapes_healthy']}, certificate {v['tapes_certificate']}, locked (original) {v['tapes_locked_original']}: "
                        + json.dumps({gt: (x['diff_p50'], x['diff_p95']) for gt, x in v['gates'].items()}))
        return
    t0 = time.time()
    fit = G.fit_generators(a.tf)
    cal = G.one_year_calendar(fit) if a.one_year else None
    fs = G.fit_summary(fit); fs.update(one_year=a.one_year, tapes_per_generator=a.n, sessions_per_tape=int(len(cal) if cal is not None else fit["n_pool"] and len(fit["calendar"])),
                                       target_healthy=a.target_healthy)
    old = os.path.join(HERE, f"fit_{a.tf}.json")
    if os.path.exists(old):
        prev = json.load(open(old))
        same = all(abs(float(prev["gmm_bic"][str(k_)]) - float(fs["gmm_bic"][k_])) < 1e-6 for k_ in fs["gmm_bic"]) and prev["gmm_k"] == fs["gmm_k"]
        log(f"generator refit reproduces the first build's GMM (BIC per K identical, K = {fs['gmm_k']}): {same}")
        fs["refit_reproduces_first_build"] = same
    json.dump(fs, open(old, "w"), indent=1, default=str)
    gens = a.gens.split(",")
    # the real-tape reference (ledger rows) once per timeframe
    ref_path = os.path.join(HERE, f"real_reference_{a.tf}.json")
    if not os.path.exists(ref_path):
        ref = real_reference(a.tf, __file__); json.dump(ref, open(ref_path, "w"), indent=1, default=str)
        with open(REALITY, "a") as f: f.write(json.dumps(ref["reality"], default=str) + "\n")
        log(f"real reference {a.tf}: " + json.dumps({g_: (v['diff'], v['control_pct'], v['id']) for g_, v in ref['gates'].items()}))
    done = {(r["gen"], r["k"]) for r in (json.loads(x) for x in open(RESULTS)) if r["tf"] == a.tf} if os.path.exists(RESULTS) else set()

    def make_job(gen, k):
        folder = os.path.join(HERE, "tapes", a.tf, f"{gen}_{k}")
        if os.path.exists(os.path.join(folder, "features.parquet")): return (gen, k, folder, False)
        G.write_tape(fit, gen, k, os.path.join(folder, "tape.csv"), cal)
        return (gen, k, folder, True)

    def work(job):
        gen, k, folder, need = job
        if need:
            ok, secs, rss = build_tape(a.tf, folder)
            if not ok: log(f"BUILD FAILED {gen}_{k} (see build.log)"); return None
            log(f"built {a.tf} {gen}_{k}: {secs}s, peak rss {rss} MB")
        if (gen, k) in done:
            if not os.path.exists(os.path.join(folder, "tape_health.json")): tapes.tape_health(folder)
            return None
        rows, rc, hl = evaluate_tape(a.tf, gen, k, folder)
        tidy(folder, keep_csv=(k == 0))
        return rows, rc, hl

    def run_jobs(jobs):
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            for res in ex.map(work, jobs):
                if res is None: continue
                rows, rc, hl = res
                with open(RESULTS, "a") as f:
                    for r in rows: f.write(json.dumps(r, default=str) + "\n")
                with open(REALITY, "a") as f: f.write(json.dumps(rc, default=str) + "\n")
                done.add((rc["gen"], rc["k"]))
                log(f"evaluated {a.tf} {rc['gen']}_{rc['k']}: units {rc['l1_units']}, setups/sess {rc['setups_per_session']}, "
                    f"healthy {hl['healthy']} (dead share {hl['dead_share']}, longest frozen run {hl['longest_frozen_run_sessions']} sessions), " +
                    " ".join(f"{r['gate']} diff {r['diff']} pct {r['control_pct']}" for r in rows))

    # the design's n tapes per generator (generation is cheap and sequential; the build runs in the pool)
    jobs = [make_job(gen, k) for gen in gens for k in range(a.n)]
    log(f"{a.tf}: {len(jobs)} tapes ({sum(1 for j in jobs if j[3])} to build) in {time.time() - t0:.0f}s")
    run_jobs(jobs)
    # repair round: top up per generator until target_healthy healthy tapes exist, next seeds first; the certificate is the first
    # DESIGN_N healthy by k whatever the batch boundaries, so no tape is chosen on its statistic
    if a.target_healthy:
        for round_ in range(1, 8):
            todo = []
            for gen in gens:
                fs_ = tapes.all_tape_folders(a.tf, gen)
                healthy = sum(1 for p in fs_ if tapes.read_health(p)["healthy"]); locked = len(fs_) - healthy
                need = a.target_healthy - healthy
                if need <= 0: continue
                rate = locked / max(1, len(fs_))
                batch = int(math.ceil(need / max(0.5, 1.0 - rate)))
                k0 = max(tapes._tape_k(p) for p in fs_) + 1 if fs_ else 0
                log(f"top-up round {round_} {a.tf} {gen}: healthy {healthy} / {len(fs_)} built (lock-out rate {rate:.2f}), need {need}, generating {batch} tapes k = {k0}..{k0 + batch - 1}")
                todo += [make_job(gen, k) for k in range(k0, k0 + batch)]
            if not todo: break
            run_jobs(todo)
    null = aggregate()
    log(f"{a.tf} done in {time.time() - t0:.0f}s")
    if null:
        for g_, d in null["timeframes"][a.tf]["generators"].items():
            log(f"{a.tf} {g_}: built {d['tapes_built']}, healthy {d['tapes_healthy']}, certificate {d['tapes_certificate']} " +
                json.dumps({gt: dict(cert=(v['diff_p50'], v['diff_p95']), all_orig=(d['gates_all_original'][gt]['diff_p50'], d['gates_all_original'][gt]['diff_p95']), real=v['real_diff'])
                            for gt, v in d['gates'].items()}))


if __name__ == "__main__":
    main()
