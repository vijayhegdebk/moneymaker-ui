# FZ v3 cloud program (`fz_v3/out/`)

The authoritative FZ v3 run (BRIEF.md addendum 5: from scratch, no hardware shortcuts; DESIGN_PANEL.md is the program). Everything
here was produced in the cloud session of 2026-09-29 on the four committed files under `fz_v3/data/`.

| path | what |
|---|---|
| `build/build.py`, `build/compare.py`, `build/trunc_diff.py` | the dataset build (both timeframes, one column contract), the cross-check against `fz_v3/built/`, the causality check |
| `data/<tf>/` | the datasets (`data/README.md` = every column and its look-ahead status; `meta.json`, `compare.json`, `trunc_*/trunc_diff.json`) |
| `harness.py` | **the one evaluator**: unit table, purged / embargoed splitter, CPCV paths, `score()` + the append-only ledger, PBO, DSR, block bootstrap, SPA, break tests, go / no-go |
| `pre_register.py` -> `results/pre_registration.json` | run first: splitter checks, the break tests, the raw book and the frozen ST7/ST8 gate on both labels (the comparators) |
| `ledger/trials.jsonl`, `ledger/vectors/` | every candidate ever scored (config, statistics, per-session vectors); never edited, only appended |
| `studies/<name>/` | one folder per study: its script(s), outputs, `FINDINGS.md` |
| `features_ext/<tf>/` | the extended as-of features (FFD, BSADF, CUSUM, BOCPD, state posteriors, novelty, window summaries) built by the regime / novelty studies, verified on the truncated data |
| `candidates/` | the frozen candidate JSONs (sha-stamped) that may reach OOS |
| `oos_once.py` -> `results/oos.json` | the single OOS run (at most three frozen candidates + the ST7/ST8 comparator) |
| `QUALITY.md`, `REPORT.md` | the build quality log (cross-check, truncation, environment) and the trading playbook with IS / OOS numbers and controls |

## Rules every study obeys

1. **Read the tables through `harness.load(tf)`** (label `L1` = the intraday 15:25 book, the training label; `L0` = the engine's
   uncut trade, robustness only). Features come from `Table.asof_columns()` / `harness.design(T)`; never a column with prefix
   `fnd_`, `l1_`, `fwd_`, `fzpos_`, `fzpost_`, nor `fz_traded`, nor a final-state field of the side tables.
2. **IS only.** `harness.score(..., split="IS")` is the only source of a kept-vs-skipped number; it refuses `split="OOS"` unless
   the caller is `oos_once.py`. Do not read `split == "OOS"` rows for anything but a row count.
3. **Every configuration tried is a ledger row**: call `score()` for every threshold / rule / model variant you evaluate, with
   `family="<study>/<sub-family>"` and the exact `config` dict. PBO, DSR and SPA are computed over the family from the ledger.
4. **Cross-validate with the harness splitter** (`purged_splits` / `cpcv_splits`, then `cpcv_paths` + `score_paths`); pick
   thresholds inside training folds; report the CPCV path distribution (median, 5th percentile), never one number.
5. **Judgement** = kept-vs-skipped expectancy (INR per trade), the session-matched random-control percentile, the permutation p,
   loser recall / precision, |net|-weighted winner recall, top-decile winners skipped, the difference with the top 1% winners
   removed, the kept book's mean at 8 pts slippage, the block-wise sign count. Net alone is never the criterion.
6. **Output as config**: a candidate is at most 8 conjunctive rules of depth <= 3 over named as-of columns, or a scorecard with
   bins and integer points, or two numbers; provenance = `learned on IS 2021-10..2025-12, script <name>, sha <ledger row id>`.
   Anything larger is offered as an alternative that needs a user decision, never assumed.
7. Every study writes `studies/<name>/FINDINGS.md` (definitions, every number with its ledger id, what would falsify it) and a
   `findings.json` for the report; an adversarial refuter reads both before anything reaches `candidates/`.

## Harness API (see the docstrings)

```python
import sys; sys.path.insert(0, "<repo>/research/strategy_lab/fz_v3/out"); import harness as H
T = H.load("minute")                          # or "5minute"; label="L0" for the uncut engine trade
T.F                                           # the unit rows (pandas), T.net / T.win / T.session / T.block / T.is_mask / T.oos_mask
X, src = H.design(T)                          # numeric design matrix over the as-of allow-list (one-hot text, 0/1 booleans)
for tr, te in H.purged_splits(T): ...         # 12 blocks; tr / te are row indices into T
for tr, te, (a, b) in H.cpcv_splits(T): ...   # 66 splits -> oof[(a, b)] = predictions for rows te
paths = H.cpcv_paths(T, oof)                  # 11 arrays over all rows (NaN outside IS)
res = H.score(T, keep_mask, "h2/choch_grid", dict(kc=2, scope="all"), script=__file__)     # one ledger row; res["id"]
dist, rows = H.score_paths(T, paths, "meta/hgb", cfg, script=__file__, threshold=0.5)     # the CPCV distribution
vecs = [H.load_vectors(r["id"]) for r in H.read_ledger("h2")]; H.pbo(vecs, "diff"); H.spa(vecs); H.effective_trials(vecs)
H.deflated_sharpe(per_session_kept_net, n_trials, sr_var_trials); H.bootstrap_ci(vecs[0]); H.break_tests(T)
H.go_no_go(res, "minute", cpcv=dist, pbo_value=..., dsr=..., spa_p=..., boot=...)
```

The frozen ST7/ST8 gate's kept set is `T.F.fz_traded` (post-SETUP: it is the comparator, never a feature).
