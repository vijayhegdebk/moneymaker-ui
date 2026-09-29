"""Study null_tapes_drift, part (c): generate the null tapes, push every one through the real pipeline (build.py), evaluate the
frozen ST7/ST8 gate and the two pre-registered mechanical gates on each tape's own feature table, run the reality check, and
write the null distributions. Tape numbers never enter OUT/ledger; the real-tape reference gates are scored once through
harness.score (family null_tapes_drift/real_ref) so the comparison numbers are ledger rows.

    python run_tapes.py --tf 5minute --n 20 --workers 3            # 20 full-length (IS calendar, 1,026 sessions) tapes per generator
    python run_tapes.py --tf minute --n 8 --one-year --workers 2   # 8 one-year (247 IS sessions) tapes per generator

Outputs (study folder): fit_<tf>.json, tapes/<tf>/<gen>_<k>/{tape_meta.json, build.log, meta.json, *.parquet}, tape_results.jsonl
(one line per tape x gate), tape_results.csv, reality_check.csv, real_reference.json, null_distributions.json (all timeframes
merged, rewritten on every run). fz_card.parquet and swings.parquet of a built tape are removed (never read here; ~10 MB each)
and tape.csv is kept for k = 0 only (every tape reproduces from its seed: gen_tapes.write_tape).
"""
import os, sys, json, time, argparse, subprocess, glob
sys.dont_write_bytecode = True
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, OUT)
import gen_tapes as G, tapes, harness as H                             # noqa: E402

BUILD = os.path.join(OUT, "build", "build.py")
RESULTS = os.path.join(HERE, "tape_results.jsonl")


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
    """The three reference gates through harness.metrics on the tape's own L1 units + the reality check."""
    T = tapes.load_tape(folder)
    masks, info = tapes.mechanical_masks(T)
    rows = []
    for name, keep in masks.items():
        m = tapes.evaluate_keep(T, keep, f"tape|{tf}|{gen}_{k}|{name}")
        rows.append(dict(tf=tf, gen=gen, k=k, gate=name, tape=os.path.relpath(folder, HERE), **info, **m))
    rc = dict(tf=tf, gen=gen, k=k, tape=os.path.relpath(folder, HERE), **tapes.reality_check(folder))
    return rows, rc


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


def aggregate():
    """null_distributions.json + tape_results.csv + reality_check.csv from tape_results.jsonl and reality_*.jsonl."""
    rows = [json.loads(x) for x in open(RESULTS, encoding="utf-8") if x.strip()] if os.path.exists(RESULTS) else []
    if not rows: return None
    R = pd.DataFrame(rows).drop_duplicates(subset=["tf", "gen", "k", "gate"], keep="last").sort_values(["tf", "gen", "k", "gate"])
    R.to_csv(os.path.join(HERE, "tape_results.csv"), index=False)
    rc_rows = [json.loads(x) for x in open(os.path.join(HERE, "reality.jsonl"), encoding="utf-8") if x.strip()]
    RC = pd.DataFrame(rc_rows).drop_duplicates(subset=["tf", "gen", "k"], keep="last").sort_values(["tf", "gen", "k"])
    RC.to_csv(os.path.join(HERE, "reality_check.csv"), index=False)
    ref = {}
    for p in glob.glob(os.path.join(HERE, "real_reference_*.json")): d = json.load(open(p)); ref[d["tf"]] = d
    q = lambda v, p: round(float(np.nanquantile(v, p)), 2) if np.isfinite(v).any() else None
    null = dict(study="null_tapes_drift", statistic="kept-vs-skipped mean L1 net (INR per unit) on the tape's own feature table, all tape rows (IS calendar)",
                how_to_compare=("a candidate's real-tape diff (its ledger row) is compared with p95 of the tape diffs of the SAME gate family shape; the certificate "
                                "field null_tape_diff_inr = {p50, p95} per generator; pass = real diff > gmm p95 and > segment p95 (the two memory-free nulls), "
                                "and the session-bootstrap diffs share the real diff's sign in >= 75% of tapes (stability); evaluate a rule list on the tapes with "
                                "tapes.evaluate_rule_list(folder, rules) over tapes.tape_folders(tf)"),
                timeframes={})
    for tf in sorted(R.tf.unique()):
        d = dict(real_reference=ref.get(tf, {}).get("gates"), real_reality=ref.get(tf, {}).get("reality"), generators={})
        for gen in sorted(R[R.tf == tf].gen.unique()):
            g = dict(tapes=int(R[(R.tf == tf) & (R.gen == gen)].k.nunique()), gates={})
            for gate in sorted(R.gate.unique()):
                s = R[(R.tf == tf) & (R.gen == gen) & (R.gate == gate)]
                dv = s["diff"].to_numpy(dtype=float); cv = s["control_pct"].to_numpy(dtype=float)
                real = (ref.get(tf, {}).get("gates") or {}).get(gate, {})
                g["gates"][gate] = dict(n=int(len(s)), diff_p5=q(dv, 0.05), diff_p50=q(dv, 0.5), diff_p95=q(dv, 0.95), diff_mean=round(float(np.nanmean(dv)), 2),
                                        diff_min=q(dv, 0.0), diff_max=q(dv, 1.0), diff_share_positive=round(float(np.nanmean(dv > 0)), 3),
                                        control_pct_p50=q(cv, 0.5), control_pct_p95=q(cv, 0.95), control_pct_share_ge95=round(float(np.nanmean(cv >= 95)), 3),
                                        kept_share_p50=q(s.kept_share.to_numpy(dtype=float), 0.5), units_p50=q(s.n.to_numpy(dtype=float), 0.5),
                                        real_diff=real.get("diff"), real_control_pct=real.get("control_pct"),
                                        real_above_tape_p95=(real.get("diff") is not None and q(dv, 0.95) is not None and real["diff"] > q(dv, 0.95)),
                                        real_diff_percentile_in_tapes=round(float(100 * np.nanmean(dv < real["diff"])), 1) if real.get("diff") is not None else None,
                                        tapes_same_sign_as_real=round(float(np.nanmean(np.sign(dv) == np.sign(real["diff"]))), 3) if real.get("diff") is not None else None)
            rcg = RC[(RC.tf == tf) & (RC.gen == gen)]; rcr = RC[(RC.tf == tf) & (RC.gen == "REAL")]
            keys = ["ret_std_bps", "ret_kurt_excess", "absret_ac1", "absret_ac2", "absret_ac3", "absret_ac4", "absret_ac5", "choch_per_session", "bos_per_session",
                    "setups_per_session", "l1_units_per_session", "l1_mean_net", "l1_win_rate", "frozen_kept_share", "close_last", "atr14_median"]
            g["reality"] = {kk: dict(tape_p50=q(rcg[kk].to_numpy(dtype=float), 0.5), tape_min=q(rcg[kk].to_numpy(dtype=float), 0), tape_max=q(rcg[kk].to_numpy(dtype=float), 1),
                                     real=(float(rcr[kk].iloc[0]) if len(rcr) else None),
                                     ratio_p50_to_real=(round(float(np.nanmedian(rcg[kk]) / rcr[kk].iloc[0]), 3) if len(rcr) and rcr[kk].iloc[0] else None)) for kk in keys}
            g["poor_null_flag"] = (g["reality"]["setups_per_session"]["ratio_p50_to_real"] is not None and
                                   not (1 / 3 <= g["reality"]["setups_per_session"]["ratio_p50_to_real"] <= 3))
            d["generators"][gen] = g
        null["timeframes"][tf] = d
    json.dump(null, open(os.path.join(HERE, "null_distributions.json"), "w"), indent=1, default=str)
    return null


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", required=True, choices=("minute", "5minute")); ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=3); ap.add_argument("--one-year", action="store_true"); ap.add_argument("--gens", default=",".join(G.GENS))
    ap.add_argument("--aggregate-only", action="store_true")
    a = ap.parse_args()
    if a.aggregate_only:
        aggregate(); log("aggregated"); return
    t0 = time.time()
    fit = G.fit_generators(a.tf)
    cal = G.one_year_calendar(fit) if a.one_year else None
    fs = G.fit_summary(fit); fs.update(one_year=a.one_year, tapes_per_generator=a.n, sessions_per_tape=int(len(cal) if cal is not None else fit["n_pool"] and len(fit["calendar"])))
    json.dump(fs, open(os.path.join(HERE, f"fit_{a.tf}.json"), "w"), indent=1, default=str)
    gens = a.gens.split(",")
    # the real-tape reference (ledger rows) once per timeframe
    ref_path = os.path.join(HERE, f"real_reference_{a.tf}.json")
    if not os.path.exists(ref_path):
        ref = real_reference(a.tf, __file__); json.dump(ref, open(ref_path, "w"), indent=1, default=str)
        with open(os.path.join(HERE, "reality.jsonl"), "a") as f: f.write(json.dumps(ref["reality"], default=str) + "\n")
        log(f"real reference {a.tf}: " + json.dumps({g_: (v['diff'], v['control_pct'], v['id']) for g_, v in ref['gates'].items()}))
    # generate (cheap, sequential)
    jobs = []
    for gen in gens:
        for k in range(a.n):
            folder = os.path.join(HERE, "tapes", a.tf, f"{gen}_{k}")
            if os.path.exists(os.path.join(folder, "features.parquet")): jobs.append((gen, k, folder, False)); continue
            m = G.write_tape(fit, gen, k, os.path.join(folder, "tape.csv"), cal)
            jobs.append((gen, k, folder, True))
    log(f"{a.tf}: {len(jobs)} tapes ({sum(1 for j in jobs if j[3])} to build) in {time.time() - t0:.0f}s")
    done = {(r["gen"], r["k"]) for r in (json.loads(x) for x in open(RESULTS)) if r["tf"] == a.tf} if os.path.exists(RESULTS) else set()

    def work(job):
        gen, k, folder, need = job
        if need:
            ok, secs, rss = build_tape(a.tf, folder)
            if not ok: log(f"BUILD FAILED {gen}_{k} (see build.log)"); return None
            log(f"built {a.tf} {gen}_{k}: {secs}s, peak rss {rss} MB")
        if (gen, k) in done: return None
        rows, rc = evaluate_tape(a.tf, gen, k, folder)
        tidy(folder, keep_csv=(k == 0))
        return rows, rc
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(work, jobs):
            if res is None: continue
            rows, rc = res
            with open(RESULTS, "a") as f:
                for r in rows: f.write(json.dumps(r, default=str) + "\n")
            with open(os.path.join(HERE, "reality.jsonl"), "a") as f: f.write(json.dumps(rc, default=str) + "\n")
            log(f"evaluated {a.tf} {rc['gen']}_{rc['k']}: units {rc['l1_units']}, setups/sess {rc['setups_per_session']}, " +
                " ".join(f"{r['gate']} diff {r['diff']} pct {r['control_pct']}" for r in rows))
    null = aggregate()
    log(f"{a.tf} done in {time.time() - t0:.0f}s")
    if null: print(json.dumps({g_: {gt: (v['diff_p50'], v['diff_p95'], v['real_diff']) for gt, v in d['gates'].items()} for g_, d in null['timeframes'][a.tf]['generators'].items()}, indent=1))


if __name__ == "__main__":
    main()
