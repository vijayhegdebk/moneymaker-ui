"""Repair audit (repair round of 2026-09-29, after the adversarial refuters): the facts behind the 'Repair' section of FINDINGS.md,
computed from the ledger, the registrations, the dry-run logs and the saved fold tables. python repair_audit.py
  -> repair_audit.json, and appends (never edits) one 'correction' record per shortlist registration to ledger/registrations.jsonl
     (idempotent: skipped when a correction for that sha already exists). Read-only on every other file: no model is fitted, no
     OOS row is read, no ledger trial row is written, the shortlist files are only hashed.

Issue 1  the registration note 'frozen before any gate search' is false as a data-ordering fact: the ledger rows before the
         registration are counted per family with first / last timestamps; the phase-3 gate studies (the ones the shortlist
         restricts) are checked for rows; the true ordering goes into the correction record.
Issue 2  the kept-vs-skipped MDA at the fold's tau is undefined wherever the fold's OOF gate skipped nothing: the folds with a
         defined difference are counted from the saved fold tables, the clusters with a defined mean / std from the CSVs.
Issue 3  the dry runs printed real 5minute kept-vs-skipped numbers off-ledger: every configuration-level and fold-level number in
         the four dry logs is inventoried (distinct configurations, evaluations, identical-by-seed check).
Issue 4  the exact-zero contradiction is handled in mda_diag.py (float32-consistent comparison); its json is summarised here."""
import os, re, json, hashlib, datetime as D, collections
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
LEDGER = os.path.join(OUT, "ledger")
PHASE3 = ("gate_family", "operating_point_sizing", "llm_round1", "regime_gate", "online_learner")   # PROGRESS.md 'Next' step 1
GATE_SEARCH = ("h2", "h3", "h4", "session_stop", "llm_hypotheses", "rocket", "exit_policy")          # searches for a NEW skip rule
OTHER = {"comparator": "the frozen ST7/ST8 comparator", "h1": "the H1 audit of the frozen gate's own components (not a new rule)",
         "null_tapes_drift": "the real-tape reference rows of the null-tape study", "importance": "this study's own OOF gates (ceilings)"}
DRY_LOGS = ["dry_5minute_attempt1.nohup", "dry_5minute.nohup", "dry_stage_main.nohup", "dry_stage_sfi.nohup"]
sha256 = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# ---------------------------------------------------------------- registrations
regs_path = os.path.join(LEDGER, "registrations.jsonl")
regs = [json.loads(x) for x in open(regs_path, encoding="utf-8") if x.strip()]
short = {r["what"].split()[-1]: r for r in regs if r.get("kind") == "pre_registration" and r.get("what", "").startswith("feature shortlist")}
assert set(short) == {"minute", "5minute"}, short.keys()
REG_AT = short["minute"]["registered_at"]; assert short["5minute"]["registered_at"] == REG_AT
sha_now = {tf: sha256(os.path.join(OUT, short[tf]["file"])) for tf in short}
sha_ok = {tf: sha_now[tf] == short[tf]["sha256"] for tf in short}
assert all(sha_ok.values()), sha_ok

# ---------------------------------------------------------------- issue 1: the ledger around the registration
rows = [json.loads(x) for x in open(os.path.join(LEDGER, "trials.jsonl"), encoding="utf-8") if x.strip()]
before = [r for r in rows if r["at"] < REG_AT]; after = [r for r in rows if r["at"] >= REG_AT]
top = lambda r: r["family"].split("/")[0]
def fam_table(rs, key):
    d = collections.defaultdict(list)
    for r in rs: d[key(r)].append(r["at"])
    return {f: dict(n=len(v), first=min(v), last=max(v)) for f, v in sorted(d.items())}
gate_rows = [r for r in before if top(r) in GATE_SEARCH]
other_rows = [r for r in before if top(r) not in GATE_SEARCH]
assert set(top(r) for r in other_rows) <= set(OTHER), set(top(r) for r in other_rows)
phase3_at_reg = [r for r in before if top(r) in PHASE3]; phase3_now = [r for r in rows if top(r) in PHASE3]
ordering = dict(
    registration_at=REG_AT, ledger_rows_total_now=len(rows), ledger_rows_before_registration=len(before), ledger_rows_after_registration=len(after),
    gate_search_rows_before=len(gate_rows), gate_search_families_before=fam_table(gate_rows, top), gate_search_subfamilies_before=fam_table(gate_rows, lambda r: r["family"]),
    other_rows_before={f: dict(OTHER=OTHER[f], **v) for f, v in fam_table(other_rows, top).items()},
    rows_after_registration=fam_table(after, lambda r: r["family"] + " " + r["tf"]),
    first_gate_search_row=min(gate_rows, key=lambda r: r["at"])["at"] + " " + min(gate_rows, key=lambda r: r["at"])["family"],
    last_gate_search_row_before_registration=max(gate_rows, key=lambda r: r["at"])["at"] + " " + max(gate_rows, key=lambda r: r["at"])["family"],
    phase3_families=list(PHASE3), phase3_rows_at_registration=len(phase3_at_reg), phase3_rows_now=len(phase3_now),
    importance_rows=dict(fam_table([r for r in rows if top(r) == "importance"], lambda r: r["family"])),
    shortlist_files=dict({tf: dict(file=short[tf]["file"], sha256_registered=short[tf]["sha256"], sha256_now=sha_now[tf], unchanged=sha_ok[tf],
                                   n_clusters=short[tf]["n_clusters"], n_allowed_columns=short[tf]["n_allowed_columns"]) for tf in short}),
    precedent="registrations.jsonl line 2: the 'correction' record of 2026-09-29T05:09:16 for the llm round 0 claim 'hashed before any labelled table ... existed'")

# ---------------------------------------------------------------- issue 2: where the kept-vs-skipped MDA was defined
mda_def = {}
for tf, src in (("minute", "main_minute.json"), ("5minute", "results_5minute.json")):
    folds = json.load(open(os.path.join(HERE, src)))["full_model"]["folds"]
    t = pd.read_csv(os.path.join(HERE, f"importance_clusters_{tf}.csv"))
    defined = [f for f in folds if f["oof_diff"] is not None]
    mda_def[tf] = dict(n_folds=len(folds), folds_with_defined_oof_diff=len(defined), folds_defined=[dict(fold=f["fold"], n_te=f["n_te"], tau=f["tau"], oof_diff=f["oof_diff"], kept_share=f["kept_share"]) for f in defined],
                       folds_kept_everything=sum(1 for f in folds if f["kept_share"] == 1.0), taus=[f["tau"] for f in folds],
                       n_clusters=len(t), clusters_with_mda_diff_mean=int(t.mda_diff_mean.notna().sum()), clusters_with_mda_diff_std=int(t.mda_diff_std.notna().sum()),
                       clusters_mda_diff_pass=int(t.mda_diff_pass.sum()), clusters_mda_ll_pass=int(t.mda_ll_pass.sum()),
                       largest_single_fold_diff_mean=(None if t.mda_diff_mean.isna().all() else dict(cluster=int(t.loc[t.mda_diff_mean.idxmax(), "cluster"]), value=float(t.mda_diff_mean.max()))))

# ---------------------------------------------------------------- issue 3: the dry-run inventory
ts = re.compile(r"^\[(\d\d:\d\d:\d\d) rss")
pat = dict(header=re.compile(r"=== importance (\S+)(?: stage=(\S+))? dry=True trees=(\d+)"),
           full=re.compile(r"full model depth (\d+): .*gate diff (\S+) kept (\S+)"),
           sens=re.compile(r"\] depth (\d): \{.*'diff': ([-\d.]+|None).*'kept_share': ([\d.]+|None)"),
           sfi=re.compile(r"SFI cluster (\d+) \((\d+) f\): .* diff (\S+) kept (\S+)"),
           fold=re.compile(r"depth (\d) fold (\d+): .* diff (\S+) kept (\S+)"))
configs = collections.defaultdict(list); logs = {}
for name in DRY_LOGS:
    p = os.path.join(HERE, name)
    if not os.path.exists(p): continue
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    stamps = [m.group(1) for m in map(ts.match, lines) if m]
    rec = dict(first=stamps[0] if stamps else None, last=stamps[-1] if stamps else None, header=None, config_numbers=0, config_numbers_defined=0,
               fold_numbers=0, fold_numbers_defined=0, ended_normally=any("done" in ln for ln in lines[-3:]))
    for ln in lines:
        m = pat["header"].search(ln)
        if m: rec["header"] = dict(tf=m.group(1), stage=m.group(2) or "all", trees=int(m.group(3)))
        m = pat["full"].search(ln)
        if m: configs[("full_model", int(m.group(1)))].append((name, m.group(2))); rec["config_numbers"] += 1; rec["config_numbers_defined"] += m.group(2) not in ("None", "nan")
        m = pat["sens"].search(ln)
        if m: configs[("full_model", int(m.group(1)))].append((name, m.group(2))); rec["config_numbers"] += 1; rec["config_numbers_defined"] += m.group(2) not in ("None", "nan")
        m = pat["sfi"].search(ln)
        if m: configs[("sfi", int(m.group(1)))].append((name, m.group(3))); rec["config_numbers"] += 1; rec["config_numbers_defined"] += m.group(3) not in ("None", "nan")
        m = pat["fold"].search(ln)
        if m: rec["fold_numbers"] += 1; rec["fold_numbers_defined"] += m.group(3) not in ("None", "nan")
    logs[name] = rec
identical = {f"{k[0]}:{k[1]}": len({v for _, v in vals}) == 1 for k, vals in configs.items()}
dry = dict(logs=logs, timeframe="5minute", label="L1 (real)", trees=20, scorer="harness.metrics(T, keep, IS rows, 'dry', controls=False) monkey-patched over harness.score: no ledger row",
           distinct_configurations=len(configs), distinct_by_kind={k: sum(1 for c in configs if c[0] == k) for k in ("full_model", "sfi")},
           configuration_numbers_total=sum(len(v) for v in configs.values()), configuration_numbers_defined=sum(1 for v in configs.values() for _, x in v if x not in ("None", "nan")),
           distinct_configurations_with_a_defined_number=sum(1 for v in configs.values() if any(x not in ("None", "nan") for _, x in v)),
           fold_numbers_total=sum(r["fold_numbers"] for r in logs.values()), fold_numbers_defined=sum(r["fold_numbers_defined"] for r in logs.values()),
           identical_across_logs=all(identical.values()), n_configs_not_identical=sum(1 for v in identical.values() if not v),
           ledger_rows_importance_5minute=sum(1 for r in rows if top(r) == "importance" and r["tf"] == "5minute"),
           fix="run_importance.py --dry now shuffles net / pts / net_slip within the IS rows (seed 0) before any fit; verification run: dry_repair_check_*.nohup, outputs dry_repair_check/")

# ---------------------------------------------------------------- issue 4: from mda_diag.json (re-run with the float32-consistent test)
diag = json.load(open(os.path.join(HERE, "mda_diag.json"))) if os.path.exists(os.path.join(HERE, "mda_diag.json")) else {}
zero = {tf: {k: d.get(k) for k in ("n_clusters", "n_clusters_ll_zero", "n_clusters_ll_zero_by_identity", "n_clusters_ll_negative", "n_clusters_ll_positive",
                                   "text_claim_exactly_zero_from_table", "zero_counts_agree", "period_rank_check", "float32_precision_note")} for tf, d in diag.items()}

audit = dict(kind="repair_audit", study="importance", at=D.datetime.now().isoformat(timespec="seconds"), registration_at=REG_AT,
             issue1_ordering=ordering, issue2_mda_diff_defined=mda_def, issue3_dry_runs=dry, issue4_exact_zero=zero)

# ---------------------------------------------------------------- the correction records (append-only, idempotent)
have = {r.get("corrects_sha256") for r in regs if r.get("kind") == "correction"}
appended = []
gs = ordering["gate_search_families_before"]
fam_txt = ", ".join(f"{f} {v['n']} ({v['first'][11:]}..{v['last'][11:]} UTC)" for f, v in gs.items())
for tf in ("minute", "5minute"):
    r0 = short[tf]
    if r0["sha256"] in have: continue
    rec = dict(kind="correction", corrects=f"pre_registration 'feature shortlist {tf}' registered {REG_AT}", corrects_sha256=r0["sha256"], file=r0["file"],
               registered_at=D.datetime.now().isoformat(timespec="seconds"), false_claim="frozen before any gate search",
               true_ordering=dict(ledger_rows_before_registration=len(before), gate_search_rows_before=len(gate_rows), gate_search_families_before=gs,
                                  other_rows_before={f: v["n"] for f, v in ordering["other_rows_before"].items()}, first_gate_search_row=ordering["first_gate_search_row"],
                                  last_gate_search_row_before_registration=ordering["last_gate_search_row_before_registration"],
                                  rows_after_registration={k: v["n"] for k, v in ordering["rows_after_registration"].items()},
                                  phase3_gate_studies=list(PHASE3), phase3_rows_at_registration=len(phase3_at_reg), phase3_rows_now=len(phase3_now)),
               statement=f"The shortlist was frozen at {REG_AT} AFTER the searches for new skip rules of {fam_txt}: {len(gate_rows)} gate-search rows, {len(before)} ledger rows in all "
                         f"(the rest: comparator, the H1 audit of the frozen gate's components, the null-tape reference rows, this study's own OOF ceilings), and BEFORE the phase-3 gate "
                         f"studies ({', '.join(PHASE3)}: 0 ledger rows at registration, {len(phase3_now)} now), which are the studies whose feature vocabulary this shortlist restricts and "
                         f"whose PBO the ordering matters for; 'frozen before the phase-3 gate studies' is the true claim. The earlier searches were not restricted to this vocabulary "
                         f"(no shortlist file existed before {REG_AT}); their multiplicity is carried by their own ledger families. The shortlist is empty on both timeframes "
                         f"(0 clusters, 0 allowed columns), so no column choice could have been informed by them. Same class of false provenance claim as the llm round 0 note "
                         f"corrected at 2026-09-29T05:09:16 (line 2). The shortlist file and its sha are unchanged (verified {sha_now[tf][:16]}...).",
               sha256_unchanged=bool(sha_ok[tf]), note="repair")
    with open(regs_path, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")
    appended.append(dict(tf=tf, registered_at=rec["registered_at"]))
audit["corrections_appended"] = appended
audit["corrections_present"] = [dict(corrects=r["corrects"], registered_at=r["registered_at"]) for r in
                                [json.loads(x) for x in open(regs_path, encoding="utf-8") if x.strip()] if r.get("kind") == "correction" and "feature shortlist" in r.get("corrects", "")]
json.dump(audit, open(os.path.join(HERE, "repair_audit.json"), "w"), indent=1, default=str)
print(json.dumps(dict(registration_at=REG_AT, rows_before=len(before), gate_search_rows_before=len(gate_rows), families={f: v["n"] for f, v in gs.items()},
                      rows_after=len(after), phase3_rows=len(phase3_now), mda_diff_folds_defined={tf: v["folds_with_defined_oof_diff"] for tf, v in mda_def.items()},
                      dry=dict(distinct=dry["distinct_configurations"], numbers=dry["configuration_numbers_total"], defined=dry["configuration_numbers_defined"],
                               fold_numbers=dry["fold_numbers_total"], identical=dry["identical_across_logs"]),
                      exact_zero={tf: (v.get("n_clusters_ll_zero"), v.get("zero_counts_agree")) for tf, v in zero.items()}, corrections_appended=appended), indent=1))
