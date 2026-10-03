"""rocket_ceiling finalize (resume step, 2026-09-29 after the usage-limit pause): the family statistics of the 12 OOF gate rows
recomputed from the ledger vectors with the CURRENT harness, plus the integrity checks of the finished run. No new number is
searched and no ledger row is written: harness.pbo / effective_trials / spa / deflated_sharpe / bootstrap_ci / go_no_go only read
ledger/vectors/<id>_IS.npz.

Why: harness.spa was revised after rocket_ceiling.py ran (the exit-policy refuter's finding): candidates with fewer than
max(10, 5% T) active sessions are excluded from the studentised family and White's unstudentised statistic is reported next to
Hansen's. results.json carries the SPA of the harness as it was at 07:12; this file carries the revised one (same bootstrap tag,
so the same stationary-bootstrap draws). The 12 rocket gates keep 29-75 % of the units and have a non-zero selection gain in
hundreds of the 578 active sessions (the exclusion threshold is max(10, 5 % T) = 28), so the exclusion cannot apply to them and
the studentised p must reproduce; the per-candidate active-session counts are written to family_recheck.json.

Integrity: (a) every OOF gate row of results.json is re-read from the ledger and compared field by field; (b) results.json's
`ledger_sha_after` is reproduced as the sha of a prefix of ledger/trials.jsonl (the ledger is append-only and shared with the
concurrently running importance study, so the prefix length tells when results.json was written relative to the other study's
rows); (c) the log on disk ends at the last gate row: the run's final three log lines (`family: ...`, `distillation not run: ...`,
`done in ...`) are missing from rocket_ceiling.log and run.nohup, which are byte-identical mirror copies (PROGRESS.md: the 06:24
checkout replaced every tracked file's inode, the running processes kept writing to unlinked inodes, a mirror loop copied the
orphaned logs back from /proc/<pid>/fd until the processes exited; the last copy predates the final second of the run). The
script that ran is the file on disk (ledger script_sha == sha of rocket_ceiling.py), and that file has the three log calls.

    python finalize_family.py          # writes family_recheck.json and finalize.log; seconds
"""
import os, sys, json, time, hashlib, resource
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np, pandas as pd, psutil
import harness as H

T0 = time.time()
LOGF = open(os.path.join(HERE, "finalize.log"), "a", encoding="utf-8")


def log(s):
    line = f"[{time.strftime('%H:%M:%S')} +{time.time() - T0:6.1f}s rss {int(psutil.Process().memory_info().rss / 2 ** 20):4d}MB] {s}"
    print(line, flush=True); LOGF.write(line + "\n"); LOGF.flush()


def jdump(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else (z.tolist() if hasattr(z, "tolist") else str(z)))


def close(a, b, tol=1e-9):
    if a is None or b is None: return a is None and b is None
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)): return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    try: return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError): return a == b


R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
ids = [g["id"] for g in R["gates"]]
log(f"finalize_family start; harness sha {H.file_sha(os.path.join(OUT, 'harness.py'))}; results.json ledger_sha_after {R['ledger_sha_after']}; {len(ids)} OOF gate ids")
OUTP = dict(study="rocket_ceiling", recomputed_at=time.strftime("%Y-%m-%dT%H:%M:%S"), harness_sha=H.file_sha(os.path.join(OUT, "harness.py")),
            script_sha_on_disk=H.file_sha(os.path.join(HERE, "rocket_ceiling.py")), ids=ids)

# ---------------------------------------------------------------- (a) the ledger rows behind results.json
raw = open(os.path.join(OUT, "ledger", "trials.jsonl"), "rb").read().replace(b"\r\n", b"\n")
lines = [l for l in raw.split(b"\n") if l.strip()]
rows = [json.loads(l) for l in lines]
roc_idx = [i for i, r in enumerate(rows) if r.get("family", "").startswith("rocket/")]
roc = [rows[i] for i in roc_idx]
byid = {r["id"]: r for r in rows}
FIELDS = ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall", "loser_precision", "winner_recall",
          "winner_recall_weighted", "top_decile_winners_skipped", "kept_pf", "kept_mean_slip8", "sign_blocks", "kept_win_rate", "skipped_win_rate")
mism = []
for g in R["gates"]:
    r = byid.get(g["id"])
    if r is None: mism.append((g["id"], "missing")); continue
    if r["family"] != g["family"]: mism.append((g["id"], "family", r["family"], g["family"]))
    for k in FIELDS:
        if not close(r.get(k), g.get(k)): mism.append((g["id"], k, r.get(k), g.get(k)))
fam_counts = {}
for r in roc: fam_counts[r["family"]] = fam_counts.get(r["family"], 0) + 1
script_shas = sorted({r.get("script_sha") for r in roc})
OUTP["ledger"] = dict(rows_total=len(rows), rocket_rows=len(roc), oof_rows=sum(1 for r in roc if not r["family"].endswith("/cpcv")), cpcv_rows=sum(1 for r in roc if r["family"].endswith("/cpcv")),
                      by_family=fam_counts, first_at=roc[0]["at"], last_at=roc[-1]["at"], row_index_range=[roc_idx[0], roc_idx[-1]],
                      interleaved_other_rows_in_span=[(i, rows[i]["family"], rows[i]["at"]) for i in range(roc_idx[0], roc_idx[-1] + 1) if not rows[i]["family"].startswith("rocket/")],
                      script_sha_of_rows=script_shas, script_sha_matches_file_on_disk=(script_shas == [OUTP["script_sha_on_disk"]]),
                      oof_rows_match_results_json=(len(mism) == 0), mismatches=mism, split=sorted({r["split"] for r in roc}), label=sorted({r["label"] for r in roc}), tf=sorted({r["tf"] for r in roc}))
log(f"ledger: {len(rows)} rows, rocket {len(roc)} ({OUTP['ledger']['oof_rows']} OOF + {OUTP['ledger']['cpcv_rows']} CPCV) {fam_counts}; OOF rows match results.json: {len(mism) == 0}; "
    f"script_sha {script_shas} == file on disk {OUTP['ledger']['script_sha_matches_file_on_disk']}; {len(OUTP['ledger']['interleaved_other_rows_in_span'])} other-study rows interleaved (append-only shared ledger)")

# ---------------------------------------------------------------- (b) reproduce ledger_sha_after as a prefix sha
target = R["ledger_sha_after"]; hit = None
for n in range(max(1, roc_idx[-1] - 2), min(len(lines), roc_idx[-1] + 40) + 1):
    if hashlib.sha1(b"\n".join(lines[:n]) + b"\n").hexdigest()[:16] == target: hit = n; break
OUTP["ledger_sha_after_reproduced"] = dict(target=target, prefix_rows=hit, match=hit is not None,
                                           last_rocket_row_index=roc_idx[-1], last_rocket_row_at=roc[-1]["at"],
                                           first_row_after_prefix=(dict(index=hit, family=rows[hit]["family"], at=rows[hit]["at"]) if hit is not None and hit < len(rows) else None),
                                           statement=("results.json was written when the ledger held exactly the rows up to and including the last rocket CPCV row: the run finished and wrote its results itself"
                                                      if hit is not None and hit == roc_idx[-1] + 1 else "prefix sha reproduced at another length" if hit is not None else "not reproduced"))
log(f"ledger_sha_after {target}: prefix of {hit} rows -> match {hit is not None}; last rocket row index {roc_idx[-1]} at {roc[-1]['at']}; next row {OUTP['ledger_sha_after_reproduced']['first_row_after_prefix']}")

# ---------------------------------------------------------------- (c) the truncated log
lg = open(os.path.join(HERE, "rocket_ceiling.log"), encoding="utf-8").read().splitlines()
nh = open(os.path.join(HERE, "run.nohup"), encoding="utf-8").read().splitlines()
src = open(os.path.join(HERE, "rocket_ceiling.py"), encoding="utf-8").read()
expected_tail = ['log(f"family: eff trials', 'log(f"distillation not run:', 'log(f"done in']
t_first, t_last = lg[0][1:9], lg[-1][1:9]
h, m, s = (int(x) for x in t_first.split(":")); fin = h * 3600 + m * 60 + s + R["timing"]["total_s"]
OUTP["log"] = dict(lines=len(lg), identical_to_run_nohup=(lg == nh), first_line_time=t_first, last_line_time=t_last, last_line_is_gate_row=lg[-1].split("] ", 1)[1].startswith("gate stacked q 0.7"),
                   run_finished_at_from_results_json=f"{int(fin // 3600):02d}:{int(fin % 3600 // 60):02d}:{fin % 60:04.1f} (first line + timing.total_s {R['timing']['total_s']} s)",
                   final_log_calls_in_script_present=[c for c in expected_tail if c in src], final_log_lines_present_in_log=[c for c in ("family: eff trials", "distillation not run:", "done in") if any(c in l for l in lg)],
                   explanation="PROGRESS.md (Git incident): the 06:24 checkout replaced every tracked file's inode; the running process kept writing to the unlinked inodes; a mirror loop copied the "
                               "orphaned logs back from /proc/<pid>/fd until the process exited, and the last copy predates the run's final second. results.json holds the family / distillation / "
                               "timing values those lines would have printed, and its ledger sha reproduces (above).")
log(f"log: {len(lg)} lines, identical to run.nohup {lg == nh}, last line {t_last} = gate row {OUTP['log']['last_line_is_gate_row']}; run finished at {OUTP['log']['run_finished_at_from_results_json']}; "
    f"final log calls in script {len(OUTP['log']['final_log_calls_in_script_present'])}/3, present in log {len(OUTP['log']['final_log_lines_present_in_log'])}/3")

# ---------------------------------------------------------------- the family statistics, recomputed with the current harness
vecs = [H.load_vectors(i) for i in ids]
fam = dict(effective_trials=H.effective_trials(vecs), pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag="rocket_ceiling"))
gates = R["gates"]
fam["spa_best"] = None if fam["spa"].get("best") is None else dict(model=gates[fam["spa"]["best"]]["model"], skip_q=gates[fam["spa"]["best"]]["skip_q"], id=ids[fam["spa"]["best"]])
fam["spa_best_unstudentised"] = dict(model=gates[fam["spa"]["best_unstudentised"]]["model"], skip_q=gates[fam["spa"]["best_unstudentised"]]["skip_q"], id=ids[fam["spa"]["best_unstudentised"]])
best = max(range(len(gates)), key=lambda i: gates[i]["diff"] if gates[i]["diff"] is not None else -np.inf)
v = vecs[best]; msk = v["kept_n"] > 0


def sharpe(vv):
    mm = vv["kept_n"] > 0; s_ = vv["kept_sum"][mm] / vv["kept_n"][mm]
    return float(s_.mean() / s_.std(ddof=1)) if len(s_) > 2 and s_.std(ddof=1) else np.nan


srs = np.array([sharpe(x) for x in vecs]); srs = srs[np.isfinite(srs)]
fam["best_by_diff"] = dict(model=gates[best]["model"], skip_q=gates[best]["skip_q"], id=ids[best], diff=gates[best]["diff"])
fam["dsr_best"] = H.deflated_sharpe(v["kept_sum"][msk] / v["kept_n"][msk], len(ids), float(srs.var(ddof=1)) if len(srs) > 1 else None)
fam["bootstrap_best"] = H.bootstrap_ci(v, tag="rocket_ceiling|best")
passed, checks = H.go_no_go(gates[best], "minute", cpcv=gates[best]["cpcv"], pbo_value=fam["pbo_diff"]["pbo"], dsr=fam["dsr_best"], spa_p=fam["spa"]["spa_p"], boot=fam["bootstrap_best"])
fam["go_no_go_best"] = dict(passed=passed, checks=checks, note="information only: this study never gets a candidate slot (Judge 1)")
fam["active_sessions_per_candidate"] = [int((np.abs(H.selection_gain(x)[0]) > 1e-9).sum()) for x in vecs]
F0 = R["family"]
rep = {"effective_trials": close(fam["effective_trials"], F0["effective_trials"]), "pbo_diff.pbo": close(fam["pbo_diff"]["pbo"], F0["pbo_diff"]["pbo"]),
       "pbo_kept_mean.pbo": close(fam["pbo_kept_mean"]["pbo"], F0["pbo_kept_mean"]["pbo"]), "spa.best": fam["spa"]["best"] == F0["spa"]["best"],
       "spa.best_t": close(fam["spa"]["best_t"], F0["spa"]["best_t"]), "spa.rc_p": close(fam["spa"]["rc_p"], F0["spa"]["rc_p"]), "spa.spa_p": close(fam["spa"]["spa_p"], F0["spa"]["spa_p"]),
       "best_by_diff.id": fam["best_by_diff"]["id"] == F0["best_by_diff"]["id"], "dsr_best.p": close(fam["dsr_best"].get("p"), F0["dsr_best"].get("p")),
       "bootstrap_best.diff_ci": close(fam["bootstrap_best"]["diff_ci"], F0["bootstrap_best"]["diff_ci"]), "go_no_go_best.passed": passed == F0["go_no_go_best"]["passed"]}
OUTP["family_recomputed"] = fam
OUTP["reproduces_results_json"] = rep
OUTP["spa_revised_extra"] = {k: fam["spa"].get(k) for k in ("min_active_sessions", "excluded_from_studentised", "best_active_sessions", "best_unstudentised", "best_mean_gain_unstudentised", "rc_p_unstudentised", "spa_p_unstudentised")}
log(f"family recomputed: eff trials {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA studentised best {fam['spa_best']} t {fam['spa']['best_t']} rc_p {fam['spa']['rc_p']} spa_p {fam['spa']['spa_p']} "
    f"(excluded {fam['spa']['excluded_from_studentised']}, min active {fam['spa']['min_active_sessions']}); unstudentised best {fam['spa_best_unstudentised']} gain {fam['spa']['best_mean_gain_unstudentised']} rc_p {fam['spa']['rc_p_unstudentised']} spa_p {fam['spa']['spa_p_unstudentised']}; "
    f"DSR p {fam['dsr_best'].get('p')}; boot {fam['bootstrap_best']['diff_ci']}; go {passed}")
log(f"reproduces results.json: {rep}; active sessions per candidate {fam['active_sessions_per_candidate']}")

# ---------------------------------------------------------------- the distillation inputs that were never used (existence + coverage on the IS units)
WIN = ["win_sign_agree10", "win_dd_extreme_atr", "win_range_slope"]
pth = os.path.join(OUT, "features_ext", "minute", "ext_features.parquet")
T = H.load("minute", "L1"); is_rows = np.flatnonzero(T.is_mask)
ext = pd.read_parquet(pth, columns=["setup_i", *WIN]).set_index("setup_i")
E = ext.reindex(T.setup_i[is_rows])
OUTP["win_ext"] = dict(file="features_ext/minute/ext_features.parquet", columns=WIN, rows=int(len(ext)), is_units=int(len(is_rows)), is_units_found=int(E.notna().any(axis=1).sum()),
                       coverage_is_units={c: round(float(E[c].notna().mean()), 4) for c in WIN}, note="never read by the run (the pre-registered stop fired before distillation); listed for the record")
log(f"win_* summaries: {OUTP['win_ext']}")

OUTP["timing_s"] = round(time.time() - T0, 1); OUTP["peak_rss_mb"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
OUTP["ledger_rows_written_by_this_script"] = 0; OUTP["ledger_sha_now"] = H.ledger_sha()
jdump(OUTP, os.path.join(HERE, "family_recheck.json"))
log(f"family_recheck.json written in {OUTP['timing_s']} s, peak RSS {OUTP['peak_rss_mb']} MB; ledger rows written by this script: 0; ledger sha now {OUTP['ledger_sha_now']}")
