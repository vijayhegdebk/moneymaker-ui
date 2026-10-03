"""run_online.py - the driver of study online_learner for one timeframe (IS rows, label L1, time order).

    python run_online.py --tf 5minute --workers 2 --stage all       # spec, fit, score, checks
    python run_online.py --tf minute --stage fit                    # one stage; every stage is resumable (checkpoints)

Stages
  spec    the two designs' encoded column lists from the real IS rows (results/<tf>/spec_<design>.json).
  fit     every fit sequence (job) = (design, learner, cadence_k, window, fit reward) with its decision heads (explore x seed x
          decision-side reward), run by online.run_heads in parallel worker processes (one BLAS thread each); per job a
          checkpoint results/<tf>/jobs/<job>.pkl (keep / lots arrays, state ids, per-head cfg) and the journal
          results/<tf>/journals/<job>.parquet (one row per SETUP per head). The full design's standardised feature vectors are
          written once (results/<tf>/features_full.parquet) and every full job's vectors are asserted identical to them.
  score   every head = one harness.score row (family online/<design>/<learner>/k<k>/<window>/<reward>, config = the cfg with
          explore / seed; controls 2,000 draws) appended to results/<tf>/scores.jsonl, plus the cheap learning curve every 250
          SETUPs (harness.metrics without controls on the prefix rows) in results/<tf>/curves.jsonl; the comparators take-all and
          the frozen ST7/ST8 gate as rows of family online_comparator/<name> (excluded from the online family's PBO / SPA).
  checks  determinism (a fresh double run of a fixed subset of jobs; journal sha, decisions and state ids must be identical, and
          equal to the fit stage's stored decisions) and truncation (the run on the rows before 2025-06-30 12:00 and the run on
          data/<tf>/trunc_20250630_120000 must give the same decisions for every SETUP before the cut): results/<tf>/checks.json.
The grids are the task's (k in {1, 10, 50}; window anchored / 300 / 1000; reward net / pf; explore 0 / 0.3; 5 seeds); nothing
is shrunk. OOS rows are never read.
"""
import os, sys, json, time, pickle, argparse, hashlib, datetime as D
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, OUT):
    if p not in sys.path: sys.path.insert(0, p)
import harness as H                                                     # noqa: E402
import online as O                                                      # noqa: E402

RES = os.path.join(HERE, "results")
CADENCES = (1, 10, 50)
WINDOWS = ("anchored", 300, 1000)
REWARDS = ("net", "pf")
EXPLORES = (0.0, 0.3)
SEEDS = (1, 2, 3, 4, 5)
MIN_LEAF = {"minute": 50, "5minute": 20}
CURVE_STEP = 250
_T = {}


def table(tf):
    if tf not in _T: _T[tf] = H.load(tf)
    return _T[tf]


def spec_path(tf, design): return os.path.join(RES, tf, f"spec_{design}.json")


def load_spec(tf, design): return json.load(open(spec_path(tf, design), encoding="utf-8"))


def spec_sha(spec): return hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- jobs
def job_id(design, learner, k, window, fr):
    return f"{design}__{learner}__k{k}__{window}__{fr or 'x'}"


def jobs(tf):
    out = []
    for design in O.DESIGNS:
        learners = ("lints", "logts", "hgb_reg", "hgb_cls") if design == "context" else ("lints", "logts")
        for learner in learners:
            for k in CADENCES:
                for window in WINDOWS:
                    fit_rewards = REWARDS if learner in ("lints", "hgb_reg") else (None,)
                    for fr in fit_rewards:
                        dec_rewards = (fr,) if fr else REWARDS
                        if learner in ("lints", "logts"):
                            hs = [dict(explore=0.0, seed=0, reward=rd) for rd in dec_rewards] + \
                                 [dict(explore=0.3, seed=s, reward=rd) for rd in dec_rewards for s in SEEDS]
                        else:
                            hs = [dict(explore=0.0, seed=0, reward=rd) for rd in dec_rewards]
                        cfg = dict(design=design, learner=learner, cadence_k=k, window=window, reward=fr or "net", explore=0.0, seed=0,
                                   hgb=dict(min_samples_leaf=MIN_LEAF[tf]))
                        out.append(dict(id=job_id(design, learner, k, window, fr), cfg=cfg, heads=hs))
    return out


def head_cfg(job_cfg, head, spec):
    """The complete cfg of one path (what the ledger row records and a candidate freezes)."""
    c = O.with_defaults(dict(job_cfg, reward=head["reward"], explore=head["explore"], seed=head["seed"]))
    c["encoded"] = spec; c["columns"] = sorted({e["source"] for e in spec})
    return c


def ledger_config(c):
    """The ledger's config dict: the cfg without the encoded list (its sha and the column count instead)."""
    d = {k: v for k, v in c.items() if k not in ("encoded", "columns")}
    d["encoded_sha"] = spec_sha(c["encoded"]); d["n_encoded"] = len(c["encoded"]); d["n_columns"] = len(c["columns"])
    if c["learner"] not in ("hgb_reg", "hgb_cls"): d.pop("hgb", None)
    if c["learner"] != "hgb_cls": d.pop("tau_rule", None)
    if c["learner"] != "logts": d.pop("newton", None)
    return d


def family(c):
    return f"online/{c['design']}/{c['learner']}/k{c['cadence_k']}/{c['window']}/{c['reward']}"


def run_job(tf, job, spec):
    """One fit sequence with all its heads (worker process)."""
    t0 = time.time()
    T = table(tf); rows = np.flatnonzero(T.is_mask)
    cfg = dict(job["cfg"], encoded=spec, columns=sorted({e["source"] for e in spec}))
    feats = [] if cfg["design"] == "full" else None
    res = O.run_heads(T, cfg, rows, job["heads"], features_out=feats)
    heads_out, frames = [], []
    for hi, h in enumerate(job["heads"]):
        r = res[hi]
        keep = np.array([d["take"] for d in r["decisions"]], dtype=bool)
        lots = np.array([d["lots"] for d in r["decisions"]], dtype=np.int8)
        c = head_cfg(job["cfg"], h, spec)
        heads_out.append(dict(head=h, keep=keep, lots=lots, states=r["states"], cfg_ledger=ledger_config(c), journal_sha=O.journal_sha(r["journal"])))
        J = pd.DataFrame(r["journal"]); J.insert(0, "head", f"e{h['explore']}_s{h['seed']}_{h['reward']}"); frames.append(J)
    os.makedirs(os.path.join(RES, tf, "jobs"), exist_ok=True); os.makedirs(os.path.join(RES, tf, "journals"), exist_ok=True)
    pd.concat(frames, ignore_index=True).to_parquet(os.path.join(RES, tf, "journals", job["id"] + ".parquet"), index=False)
    out = dict(id=job["id"], cfg=job["cfg"], heads=heads_out, rows=rows, seconds=round(time.time() - t0, 1), n_rows=int(len(rows)),
               features_sha=(hashlib.sha1(np.asarray(feats).tobytes()).hexdigest()[:16] if feats else None))
    if feats and not os.path.exists(os.path.join(RES, tf, "features_full.parquet")):
        Fm = pd.DataFrame(np.asarray(feats), columns=[e["name"] for e in spec] + ["bias"]); Fm.insert(0, "setup_i", T.setup_i[rows])
        Fm.to_parquet(os.path.join(RES, tf, "features_full.parquet"), index=False)
    pickle.dump(out, open(os.path.join(RES, tf, "jobs", job["id"] + ".pkl"), "wb"))
    return dict(id=job["id"], seconds=out["seconds"], features_sha=out["features_sha"], heads=len(heads_out))


# ---------------------------------------------------------------- stages
def stage_spec(tf):
    T = table(tf); os.makedirs(os.path.join(RES, tf), exist_ok=True)
    for design in O.DESIGNS:
        spec = O.design_spec(T, design)
        json.dump(spec, open(spec_path(tf, design), "w"), indent=0)
        print(f"[{tf}] spec {design}: {len(spec)} encoded columns from {len({e['source'] for e in spec})} source columns "
              f"(time proxies excluded: {sorted(H.TIME_PROXIES)}); sha {spec_sha(spec)}", flush=True)


def stage_fit(tf, workers):
    from joblib import Parallel, delayed
    specs = {d: load_spec(tf, d) for d in O.DESIGNS}
    todo = [j for j in jobs(tf) if not os.path.exists(os.path.join(RES, tf, "jobs", j["id"] + ".pkl"))]
    print(f"[{tf}] fit: {len(jobs(tf))} jobs, {len(todo)} to run, workers {workers}", flush=True)
    # the expensive ones first so the pool stays busy
    cost = lambda j: (0 if j["cfg"]["design"] == "full" else 1, j["cfg"]["cadence_k"], 0 if j["cfg"]["learner"] in ("logts", "hgb_reg", "hgb_cls") else 1)
    todo.sort(key=cost)
    t0 = time.time()
    for r in Parallel(n_jobs=workers, backend="loky", return_as="generator")(delayed(run_job)(tf, j, specs[j["cfg"]["design"]]) for j in todo):
        print(f"[{tf}] job {r['id']:<48} {r['seconds']:8.1f}s heads {r['heads']} features_sha {r['features_sha']}  ({time.time() - t0:.0f}s elapsed)", flush=True)
    shas = {p["features_sha"] for p in (pickle.load(open(os.path.join(RES, tf, "jobs", j["id"] + ".pkl"), "rb")) for j in jobs(tf) if j["cfg"]["design"] == "full")}
    print(f"[{tf}] full-design feature vectors identical across jobs: {len(shas) == 1} {sorted(shas)}", flush=True)


def curve(T, keep, rows, lots=None):
    out = []
    n = len(rows); pts = list(range(CURVE_STEP, n, CURVE_STEP)) + [n]
    net = T.net
    for m in pts:
        r = rows[:m]; mt = H.metrics(T, keep, r, "", controls=False)
        row = dict(n=m, kept_n=mt["kept_n"], kept_share=mt["kept_share"], diff=mt["diff"], kept_mean=mt["kept_mean"], kept_pf=mt["kept_pf"],
                   kept_sum=round(float(net[r][keep[r]].sum()), 2), all_sum=round(float(net[r].sum()), 2), sign_blocks=mt["sign_blocks"])
        if lots is not None: row["sized_sum"] = round(float((net[r] * lots[:m] * keep[r]).sum()), 2)
        out.append(row)
    return out


def stage_score(tf):
    T = table(tf); rows = np.flatnonzero(T.is_mask)
    sp = os.path.join(RES, tf, "scores.jsonl"); cp = os.path.join(RES, tf, "curves.jsonl")
    done = {json.loads(l)["id"] for l in open(sp, encoding="utf-8") if l.strip()} if os.path.exists(sp) else set()
    n_new = 0; t0 = time.time()
    for j in jobs(tf):
        p = os.path.join(RES, tf, "jobs", j["id"] + ".pkl")
        if not os.path.exists(p): print(f"[{tf}] score: job {j['id']} missing, skipped", flush=True); continue
        J = pickle.load(open(p, "rb"))
        for h in J["heads"]:
            c = h["cfg_ledger"]; fam = family(c)
            cid = H.candidate_id(fam, c, T.label, T.tf)
            if cid in done: continue
            keep = np.zeros(T.n, dtype=bool); keep[rows] = h["keep"]
            res = H.score(T, keep, fam, c, script=__file__)
            res["job"] = j["id"]; res["head"] = h["head"]; res["journal_sha"] = h["journal_sha"]
            res["lots_mean_taken"] = round(float(h["lots"][h["keep"]].mean()), 3) if h["keep"].any() else None
            res["take_and_zero_lots"] = int(((h["lots"] == 0) & h["keep"]).sum())
            res["sized_net"] = round(float((T.net[rows] * h["lots"] * h["keep"]).sum()), 2)
            w = T.net[rows] * h["lots"] * h["keep"]; gw, gl = w[w > 0].sum(), -w[w < 0].sum()
            res["sized_pf"] = round(float(gw / gl), 3) if gl > 0 else None
            with open(sp, "a", encoding="utf-8") as f: f.write(json.dumps(res, default=str) + "\n")
            with open(cp, "a", encoding="utf-8") as f: f.write(json.dumps(dict(id=res["id"], family=fam, curve=curve(T, keep, rows, h["lots"]))) + "\n")
            done.add(cid); n_new += 1
            if n_new % 20 == 0: print(f"[{tf}] scored {n_new} rows ({time.time() - t0:.0f}s)", flush=True)
    # comparators (own family, outside online/*)
    comps = {"take_all": (np.ones(T.n, dtype=bool), "pre_registration.json"), "frozen_st7_st8": (T.F.fz_traded.astype(bool).to_numpy(), "pre_registration.json")}
    # the gate_family study's OOF decisions (studies/gate_family/results/oof_<tf>_<sub>.parquet: one row per sub-family x model x IS
    # unit, columns setup_i, sub, model, keep): the sub-family's finalist model when gate_family/findings.json names one, else every
    # model in the file (labelled by sub / model; the h5_full sub is outside the frozen shortlist). Absent files are recorded.
    gf_dir = os.path.join(OUT, "studies", "gate_family"); gf_files = []
    fj = os.path.join(gf_dir, "findings.json"); fin = json.load(open(fj)).get("timeframes", {}).get(tf, {}).get("sub_families", {}) if os.path.exists(fj) else {}
    for sub in ("context", "h5_full"):
        gf = os.path.join(gf_dir, "results", f"oof_{tf}_{sub}.parquet")
        if not os.path.exists(gf): continue
        gf_files.append(os.path.relpath(gf, OUT)); G = pd.read_parquet(gf)
        fm = ((fin.get(sub) or {}).get("finalist") or {}).get("model")
        models = [fm] if fm and fm in set(G.model) else sorted(set(G.model))
        for mdl in models:
            m = dict(zip(G.setup_i[G.model == mdl], G.keep[G.model == mdl].astype(bool)))
            comps[f"gate_family_oof/{sub}/{mdl}" + ("/finalist" if fm == mdl else "")] = (np.array([bool(m.get(int(s), True)) for s in T.setup_i]), os.path.relpath(gf, OUT))
    for name, (keep, src) in comps.items():
        fam = f"online_comparator/{name}"; c = dict(comparator=name, source=src)
        if name.startswith("gate_family_oof/h5_full"): c["vocabulary"] = "outside the frozen shortlist"
        if H.candidate_id(fam, c, T.label, T.tf) in done: continue
        res = H.score(T, keep, fam, c, script=__file__); res["job"] = "comparator"; res["head"] = None
        with open(sp, "a", encoding="utf-8") as f: f.write(json.dumps(res, default=str) + "\n")
        with open(cp, "a", encoding="utf-8") as f: f.write(json.dumps(dict(id=res["id"], family=fam, curve=curve(T, keep, rows))) + "\n")
        done.add(res["id"])
    print(f"[{tf}] score: {n_new} new rows, gate_family OOF files {gf_files or 'absent'} ({time.time() - t0:.0f}s)", flush=True)


CHECK_JOBS = {  # design, learner, k, window, fit reward: the fixed subset the determinism / truncation checks run on
    "context": [("lints", 1, "anchored", "net"), ("lints", 10, 300, "pf"), ("lints", 50, 1000, "net"), ("logts", 1, "anchored", None), ("logts", 10, 300, None),
                ("logts", 50, 1000, None), ("hgb_reg", 50, "anchored", "net"), ("hgb_cls", 50, 1000, None)],
    "full": [("lints", 10, 1000, "net"), ("logts", 50, "anchored", None)]}


def stage_checks(tf):
    T = table(tf); rows = np.flatnonzero(T.is_mask)
    specs = {d: load_spec(tf, d) for d in O.DESIGNS}
    tfold = os.path.join(OUT, "data", tf, "trunc_20250630_120000")
    Ttr = O.load_table(tfold, tf)
    time_full = T.F.time.astype(str).to_numpy(); time_tr = Ttr.F.time.astype(str).to_numpy()
    rows_cut = rows[time_full[rows] < O.CUT]
    rows_tr = np.flatnonzero(Ttr.is_mask); rows_tr = rows_tr[time_tr[rows_tr] < O.CUT]
    common = sorted(set(T.setup_i[rows_cut].tolist()) & set(Ttr.setup_i[rows_tr].tolist()))
    # label sanity: trades closed before the cut bar carry the same net in both builds
    cut_bar = int(T.F.setup_i[time_full >= O.CUT].min()) if (time_full >= O.CUT).any() else int(T.setup_i.max()) + 1
    nf = dict(zip(T.setup_i, T.net)); nt = dict(zip(Ttr.setup_i, Ttr.net)); xb = dict(zip(T.setup_i, T.exit_bar))
    closed_before = [s for s in common if xb[s] < cut_bar]
    label_same = all(abs(nf[s] - nt[s]) < 0.005 for s in closed_before)
    out = dict(tf=tf, cut=O.CUT, rows_is=int(len(rows)), rows_before_cut=int(len(rows_cut)), trunc_rows_before_cut=int(len(rows_tr)), common_setups=len(common),
               closed_before_cut=len(closed_before), labels_identical_closed_before_cut=bool(label_same), jobs=[])
    print(f"[{tf}] checks: {len(rows_cut)} rows before the cut, trunc build {len(rows_tr)}, common {len(common)}, labels identical on closed trades: {label_same}", flush=True)
    for design, lst in CHECK_JOBS.items():
        for learner, k, window, fr in lst:
            jid = job_id(design, learner, k, window, fr)
            J = pickle.load(open(os.path.join(RES, tf, "jobs", jid + ".pkl"), "rb"))
            heads = [J["heads"][0]["head"]] + ([h["head"] for h in J["heads"] if h["head"]["explore"] > 0][:1])
            cfgj = dict(J["cfg"], encoded=specs[design], columns=sorted({e["source"] for e in specs[design]}))
            t0 = time.time()
            r1 = O.run_heads(T, cfgj, rows, heads); r2 = O.run_heads(T, cfgj, rows, heads)
            rc = O.run_heads(T, cfgj, rows_cut, heads); rt = O.run_heads(Ttr, cfgj, rows_tr, heads)
            rec = dict(job=jid, heads=heads, seconds=round(time.time() - t0, 1))
            for hi, h in enumerate(heads):
                stored = next(x for x in J["heads"] if x["head"] == h)
                d1 = [d["take"] for d in r1[hi]["decisions"]]; d2 = [d["take"] for d in r2[hi]["decisions"]]
                det = (O.journal_sha(r1[hi]["journal"]) == O.journal_sha(r2[hi]["journal"]) and r1[hi]["decisions"] == r2[hi]["decisions"] and r1[hi]["states"] == r2[hi]["states"])
                same_as_stored = (d1 == stored["keep"].tolist()) and (O.journal_sha(r1[hi]["journal"]) == stored["journal_sha"])
                m = len(rows_cut)
                trunc_a = r1[hi]["decisions"][:m] == rc[hi]["decisions"] and r1[hi]["states"][:m] == rc[hi]["states"]
                dfull = dict(zip(T.setup_i[rows_cut].tolist(), (d["take"] for d in r1[hi]["decisions"][:m])))
                dtr = dict(zip(Ttr.setup_i[rows_tr].tolist(), (d["take"] for d in rt[hi]["decisions"])))
                lfull = dict(zip(T.setup_i[rows_cut].tolist(), (d["lots"] for d in r1[hi]["decisions"][:m])))
                ltr = dict(zip(Ttr.setup_i[rows_tr].tolist(), (d["lots"] for d in rt[hi]["decisions"])))
                trunc_b = all(dfull[s] == dtr[s] and lfull[s] == ltr[s] for s in common)
                rec[f"head_{hi}"] = dict(head=h, deterministic=bool(det), equals_stored=bool(same_as_stored), truncation_prefix_identical=bool(trunc_a),
                                         truncation_build_identical=bool(trunc_b), n_compared=len(common), decisions_differ=int(sum(dfull[s] != dtr[s] for s in common)))
                print(f"[{tf}]  {jid} head {h}: deterministic {det}, = stored {same_as_stored}, prefix {trunc_a}, trunc build {trunc_b} ({rec['seconds']}s)", flush=True)
            out["jobs"].append(rec)
    out["all_pass"] = bool(label_same and all(v["deterministic"] and v["equals_stored"] and v["truncation_prefix_identical"] and v["truncation_build_identical"]
                                             for j in out["jobs"] for kk, v in j.items() if kk.startswith("head_")))
    json.dump(out, open(os.path.join(RES, tf, "checks.json"), "w"), indent=1, default=str)
    print(f"[{tf}] checks all pass: {out['all_pass']}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--stage", default="all", choices=["spec", "fit", "score", "checks", "all"]); a = ap.parse_args()
    t0 = time.time(); print(f"[{a.tf}] start {D.datetime.now().isoformat(timespec='seconds')} stage {a.stage}", flush=True)
    if a.stage in ("spec", "all"): stage_spec(a.tf)
    if a.stage in ("fit", "all"): stage_fit(a.tf, a.workers)
    if a.stage in ("score", "all"): stage_score(a.tf)
    if a.stage in ("checks", "all"): stage_checks(a.tf)
    print(f"[{a.tf}] done in {time.time() - t0:.0f}s; ledger sha {H.ledger_sha()}", flush=True)
