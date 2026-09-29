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

## Deliverables (every study)

- `OUT/studies/<study>/*.py` (the scripts, runnable end to end), their logs, and their outputs (CSV / JSON / parquet).
- `OUT/studies/<study>/FINDINGS.md`: definitions fixed before the numbers; every number with its ledger id or output file; IS
  only; the CPCV distribution for any searched gate; the family's PBO / SPA / effective trial count; what would falsify the
  finding; the candidate config JSON when `harness.go_no_go` passes, or the null result stated as such. Numbers in tables, not
  prose; nothing invented.
- `OUT/studies/<study>/findings.json`: the same, machine-readable: `{study, timeframes: {tf: {...}}, candidates: [...],
  null_result: bool, ledger_families: [...], caveats: [...], files: [...]}`.
- Your final message is a compact JSON-like summary (key numbers, candidate configs or null, files), not prose for a human.
