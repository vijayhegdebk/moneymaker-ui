# Standing brief for every FZ v3 study agent (cloud run, 2026-09-29)

Repository: `/home/user/money-maker`, branch `research/strategy-lab-pwxiug`. Lab: `research/strategy_lab`. Program folder:
`research/strategy_lab/fz_v3/out` (call it OUT). Read, in this order, before writing a line of code:

1. `OUT/README.md` (the rules 1-7 and the harness API), `OUT/data/README.md` (every column and its look-ahead status).
2. `fz_v3/BRIEF.md` (protocol, H1-H5, addendum 1-6) and the section of `fz_v3/DESIGN_PANEL.md` your task names: the **method**,
   the **leakage controls** and **both judges' fixes are binding**; where a judge cut a step, do not run it, where a judge added
   one, run it.
3. `OUT/harness.py` docstrings; `OUT/results/pre_registration.json` (the raw book and the frozen ST7/ST8 comparator, both labels).
4. `research/strategy_lab/FZ.md` sections 7-9 and 19 when your study reads card / gate columns.

## Hardware and libraries

4 cores, 15 GB RAM, no GPU. Python 3.11; numpy 2.4, pandas 3.0 (string columns are `str` dtype; `None` / `NaN` mixed in object
columns: use `harness.design` for a numeric matrix), scipy 1.17, scikit-learn 1.9, xgboost 3.2, lightgbm 4.7, shap 0.51, numba 0.67,
statsmodels 0.15, hmmlearn 0.3.3, mapie 1.5, ruptures 1.1, arch 8, stumpy 1.14, torch 2.14 (CPU), joblib, matplotlib. **Never shrink a
grid, a model, a fold count or a resample count below what the design specifies** (BRIEF addendum 3); use `n_jobs=4` / joblib
where a fit allows it. A run over 10 minutes: start it with `nohup python ... > log 2>&1 &` in your study folder and poll the
log; keep every log in the folder.

## Rules that cannot be broken

- **IS only.** `harness.score(..., split="IS")` is the only source of a kept-vs-skipped number; it refuses `split="OOS"`. Never
  read the OOS rows' labels or features for any purpose but a row count; never look at `fz_v3/built/study/*` OOS files.
- **Every configuration you evaluate is a ledger row**: `harness.score(T, keep, "<study>/<sub-family>", config, script=__file__)`
  for every threshold, rule, model variant and path (`score_paths`). No private kept-vs-skipped arithmetic anywhere. The ledger
  (`OUT/ledger/`) is append-only; never edit or delete it.
- **Features** only from `Table.asof_columns()` / `harness.design(T)`. Never a column with prefix `fnd_`, `l1_`, `fwd_`, `fzpos_`,
  `fzpost_`, never `fz_traded`, never a final-state field of a side table (`swings.broken_final`, `events.window_end`,
  `fz_zones.retired_*` except through `birth_bar <= k < retired_bar`, `fz_visits.end*`). Any new per-bar feature you build
  must use bars `<= k` only and must be re-run on `OUT/data/<tf>/trunc_20250630_120000/` and diffed for SETUPs before the cut
  (identical, or the feature is dropped).
- **Cross-validation** with the harness splitter: `purged_splits` (12 blocks, purge by the label's exit bar, 3-session
  embargo) for training-fold threshold choice, `cpcv_splits` + `cpcv_paths` + `score_paths` for the path distribution of any
  learned or searched gate. Thresholds are chosen inside training folds; nothing is chosen on the pooled OOF unless the design
  says so and then it is counted as a trial.
- **Labels**: L1 (`harness.load(tf)`, the 15:25 intraday book) is the training and judging label; L0 (`harness.load(tf, "L0")`)
  is a robustness table. Both timeframes (`"minute"` = Strategy 1 rules with the ST7 card, `"5minute"` = Strategy 2 rules with
  the ST8 card) unless the design restricts a study to one.
- **Judgement** = the kept-vs-skipped difference of mean net (INR per trade), the session-matched random control percentile,
  the permutation p, loser recall / precision, |net|-weighted winner recall, top-decile winners skipped, the difference with the
  top 1% winners removed, the kept book's mean at 8 pts slippage, the block-wise sign count, the CPCV 5th percentile, PBO over
  the family (`harness.pbo`), SPA (`harness.spa`), DSR, the bootstrap CI (`harness.go_no_go` bundles the pass rule). Net alone is
  never the criterion: every skipped trade saves ~1,050 INR of costs.
- **Output as config**: a surviving candidate is at most 8 conjunctive rules of depth <= 3 over named as-of columns of
  `features.parquet` (or a scorecard: bins + integer points; or two numbers), written as JSON with provenance
  `{"source": "learned on IS 2021-10..2025-12", "script": ..., "ledger_id": ..., "statistic": ...}`. Anything larger (a model, a
  weight vector, a new per-bar routine) is offered as an alternative that needs a user decision, never assumed.
- **Scope**: write only under `OUT/studies/<study>/` (create it) and, when your task says so, `OUT/features_ext/<tf>/`. Never touch
  `engine.py`, `fz.py`, `fz_exec.py`, `fz_report.py`, `lab.py`, `rl.py`, `strategies/`, `results/`, `tests/`, the data folders, or
  another study's folder. Do not run `lab.py`. Do not commit.

## Resuming a study an earlier agent left unfinished

The run was cut off by the model's usage limit from about 12:00 to 16:30 IST on 2026-09-29; the agents died, most of their
`nohup` processes finished on their own. If your study folder already holds scripts, logs and outputs, you are **continuing that
work, not starting over**. Before launching anything: `ls -la` the folder, read every log to its end, `pgrep -af` the folder's
scripts (never start a second copy of a running one). A stage whose outputs exist and whose log ends normally is done: do not
rerun it (the design fixes every grid and fold count, so a rerun only reproduces the numbers hours later). Run only what is
missing (typically the finalize / shortlist / FINDINGS.md / findings.json / registration steps), then return the summary. Only
a stage that was killed mid-run (log stops without its final line, no output file) is restarted, and only that stage, from its
last checkpoint if the script saves per-fold or per-split results. States at the resume (16:45 IST):

- `importance`: the minute stages `main`, `sfi`, `cpcv` finished (`run_minute_*.nohup`, 07:11-07:14); `results_minute.json`,
  `--stage finalize` for both timeframes, `shortlist.py` (`features_shortlist/<tf>/shortlist.json` + the registration line) and
  FINDINGS are still to do. `results_5minute.json` is complete.
- `rocket_ceiling`: `rocket_ceiling.py` ran to the end (`results.json`, `fold_auc.csv`, `path_auc.csv`, `gates.csv`,
  `cpcv_gate_paths.csv`, `oof_scores.npz`, log to 07:12); only FINDINGS.md / findings.json are missing (`write_findings.py`
  exists). Never restart the run.
- `null_tapes_drift`: `drift_minute.json` was written at 06:38 after FINDINGS.md; fold the minute drift into FINDINGS / findings.json.
- `session_stop` (repair round): `session_stop_repair.py` finished (`results_repair.json`, 06:52); the "Repair" section of
  FINDINGS.md / findings.json is still to write.
- `exit_policy`: `04_a_fqi.py minute` finished (`a_result_minute.json`); a follow-up agent folds it in (task in PROGRESS.md).

## Program-level rules added 2026-09-29 12:55 UTC (from the null_tapes_drift refuters; binding for every candidate)

- `harness.go_no_go(...)` now has two more required items. `null_tape=` takes the `checks` dict of
  `studies/null_tapes_drift/tapes.py::null_tape_check(real_diff, tf, rules)` (import it with `sys.path.insert` of that folder):
  the candidate replayed on the certificate tapes (`tapes.tape_folders(tf, gen)`, healthy tapes, 20 / 8 per generator) must have
  a real-tape kept-vs-skipped difference above the gmm AND segment tapes' 95th percentile and the session tapes must carry its
  sign in >= 75% of them. A candidate that is not a rule list (a scorecard, an online learner) is replayed on each tape's table
  the same way (`tapes.evaluate_rule_list` shows how a tape folder is loaded; use `null_tape_check_from_diffs(real_diff, diffs)`
  with your own per-tape diffs). Without it the item fails ("not run") and nothing passes. `columns=` takes the as-of columns
  the candidate reads; `harness.TIME_PROXIES` (`sl`, `n_events_asof`: calendar proxies, |rho| with time 0.93 / 1.00) fail it.
  They stay in `harness.design(T)` for this run (studies were mid-flight), so a rule or split on them is refused at the candidate,
  never silently dropped: report it and refit without the column. `oos_once.py` refuses a candidate whose provenance lacks the
  `null_tape` block and a passed `go_no_go`, or that reads a time proxy.
- Write the tape result into the candidate JSON: `provenance.null_tape = {"checks": ..., "summary": ...}` and
  `provenance.go_no_go = {"passed": true, "checks": ...}` from the same call.

## Deliverables (every study)

- `OUT/studies/<study>/*.py` (the scripts, runnable end to end), their logs, and their outputs (CSV / JSON / parquet).
- `OUT/studies/<study>/FINDINGS.md`: definitions fixed before the numbers; every number with its ledger id or output file; IS
  only; the CPCV distribution for any searched gate; the family's PBO / SPA / effective trial count; what would falsify the
  finding; the candidate config JSON when `harness.go_no_go` passes, or the null result stated as such. Numbers in tables, not
  prose; nothing invented.
- `OUT/studies/<study>/findings.json`: the same, machine-readable: `{study, timeframes: {tf: {...}}, candidates: [...],
  null_result: bool, ledger_families: [...], caveats: [...], files: [...]}`.
- Your final message is a compact JSON-like summary (key numbers, candidate configs or null, files), not prose for a human.
