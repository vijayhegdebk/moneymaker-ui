# ext_features: FINDINGS

**What this study is.** The extended as-of scalar features the design panel hands to the importance study (quant-ml-canon-feature-importance; regime-breaks and regime-states judges: features only; motif-shapelet judges: the two novelty scalars only; rocket-probe judges: the three window scalars only; vision-labels Judge 1: hindsight proxies are labels and are not computed). No gate search, no threshold, no ledger row: `ledger_families = []`. The only label-side read is the row count through `harness.load`. Definitions were fixed in `build_ext.py` before any output was looked at; they are repeated column by column in `features_ext/README.md`.

## Definitions (fixed before the numbers)

See `features_ext/README.md`, section *Columns* (definition, causal argument, fit-window statement per column). Fit window = IS bars of sessions 2021-10-01..2023-09-30 for every unsupervised fit and z-scoring statistic; inference = forward pass over the whole tape from bar 0 with the frozen model; every value at SETUP bar k uses bars <= k.

## Row counts, columns, coverage

| tf | SETUP rows | L1 units (row count only) | feature columns | bars | fit-window bars | min coverage | median coverage |
|---|---|---|---|---|---|---|---|
| minute | 5326 | 5266 | 61 | 443826 | 182557 | 0.9812 | 1.0 |
| 5minute | 1012 | 1002 | 61 | 88771 | 36514 | 0.9427 | 1.0 |

Per-column coverage: README *Coverage*. Columns below 0.95 coverage: minute: ; 5minute: `csw_max_abs` 0.9427, `csw_max_exceed` 0.9427, `csw_sign_dir` 0.9427, `win_range_slope` 0.9427 (CSW and the range slope need >= 3 session bars; the FFD needs its weight window).

## d* per timeframe

| tf | series | d* fit window | d* all IS | used | weight window (bars) |
|---|---|---|---|---|---|
| minute | close | 0.2 | 0.3 | 0.2 | 497 |
| minute | vol | 0.1 | 0.1 | 0.1 | 503 |
| 5minute | close | 0.2 | 0.3 | 0.2 | 497 |
| 5minute | vol | 0.1 | 0.1 | 0.1 | 503 |

## HMM state means (original units; state 0 = quietest by (high-low)/atr14)

**minute, K = 3** (converged True, 71 it; forward-filter check vs hmmlearn: max |diff| 8.4e-14)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.8825 | 0.4539 | -0.0487 | 4.028 | 1.975 | 5.722 | -0.1306 | 0.1301 | 0.1327 | 7.9 |
| 1 | 0.0002 | 0.9465 | 0.4833 | 0.0207 | 3.028 | -0 | 6.269 | 0.2435 | 0.8419 | 0.8368 | 46.0 |
| 2 | 0.001 | 1.908 | 0.7356 | 0.9041 | 3.201 | 0.9528 | 6.376 | -0.3366 | 0.028 | 0.0306 | 1.5 |

**minute, K = 4** (converged True, 59 it; forward-filter check vs hmmlearn: max |diff| 0.0e+00)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.866 | 0.4333 | -0.0746 | 2.93 | -0 | 5.759 | -0.4458 | 0.6349 | 0.5931 | 7.0 |
| 1 | 0.0002 | 0.8918 | 0.4681 | 0.0308 | 3.55 | -0 | 8.539 | 6.038 | 0.0918 | 0.1124 | 12.6 |
| 2 | 0.0003 | 0.9737 | 0.4877 | 0.0486 | 3.964 | 1.915 | 5.785 | -0.1443 | 0.1469 | 0.152 | 15.5 |
| 3 | 0.0006 | 1.442 | 0.7254 | 0.5046 | 2.995 | 0 | 6.628 | -1.517 | 0.1264 | 0.1425 | 1.7 |

**5minute, K = 3** (converged True, 51 it; forward-filter check vs hmmlearn: max |diff| 2.0e-13)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8442 | 0.4032 | -0.0966 | 2.961 | 1.689 | 5.32 | -0.3381 | 0.1253 | 0.114 | 6.1 |
| 1 | 0.0005 | 0.9355 | 0.452 | 0.0052 | 2.498 | -0 | 5.653 | 0.2184 | 0.8398 | 0.8496 | 38.3 |
| 2 | 0.0021 | 1.971 | 0.7267 | 0.9451 | 2.476 | 0.8472 | 4.73 | -0.4804 | 0.0349 | 0.0363 | 1.3 |

**5minute, K = 4** (converged True, 91 it; forward-filter check vs hmmlearn: max |diff| 3.1e-14)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8323 | 0.3906 | -0.1223 | 2.175 | 0 | 4.706 | 0.078 | 0.505 | 0.4777 | 5.4 |
| 1 | 0.0004 | 0.8908 | 0.4405 | -0.0221 | 3.254 | -0 | 7.952 | 0.8312 | 0.2197 | 0.2427 | 11.2 |
| 2 | 0.0006 | 0.9645 | 0.4512 | 0.0332 | 2.954 | 1.657 | 5.246 | -0.3269 | 0.1442 | 0.1351 | 14.1 |
| 3 | 0.0014 | 1.513 | 0.7055 | 0.6025 | 2.234 | -0 | 4.808 | -0.4523 | 0.1311 | 0.1445 | 1.5 |

GMM and jump-model tables, transition matrices and the lambda grids: README *State models*.

## Truncation check (causality)

| tf | cut | bars kept | SETUPs before cut | columns identical | columns dropped | max abs diff | PASS |
|---|---|---|---|---|---|---|---|
| minute | trunc_20250630_120000 | 335934 | 3807 | 61 | none | 0 | True |
| 5minute | trunc_20250630_120000 | 67192 | 718 | 61 | none | 0 | True |

Fitted quantities (d*, GMM / HMM / jump state means, lambda*, BOCPD and z-scoring statistics) are identical between the full and the truncated build on both timeframes (`trunc_diff.json` -> `fit_agreement`).

## Run times

| tf | total s | bocpd s | hmm s | novelty s |
|---|---|---|---|---|
| minute | 358.6 | 33.4 | 40.3 | 238.2 |
| 5minute | 39.6 | 7.2 | 8.8 | 13.8 |

## What would falsify this deliverable

- A column that changes for a SETUP before the cut when the tape is truncated (it did not: max |diff| 0 on both timeframes).
- A model-based column whose value at k depends on bars after k: excluded by construction (forward filter, prefix DP, per-bar mixture posterior); the hmmlearn check shows the filter equals hmmlearn's own posterior at the last observed bar.
- A d* that flips when the ADF is run on a different IS subset: it does, by one step for log close (0.2 on the fit window vs 0.3 on all IS bars); recorded as a caveat, not hidden.
- Whether any of these columns carries information about the L1 outcome is not a claim of this study; the importance study decides it under the harness splitter.

## Candidates

None (feature-building study). `null_result = false` in the sense that the deliverable exists; no gate claim is made.

## Caveats

- Feature-building study: no gate was searched, no label read except the row counts; nothing is proposed as a candidate.
- d*(fit window) = 0.2 for log close on both timeframes while d* over all IS bars = 0.3; the fit-window value is used so the truncated rebuild reproduces the column; the two FFD series are one grid step apart.
- Every model-based column is in-sample for bars inside the fit window (label-free); the truncation cut (2025-06-30) lies after the fit window, so the causality check covers inference, not the fit's own bars.
- The CUSUM filter with h = atr14/close fires every few bars (a volatility clock); BSADF with 2 lags on 375 one-minute bars is microstructure-dominated (Judge 2).
- The HMM / GMM states split mainly on bar volatility and on the CHoCH-since-BOS count already in the base table (Judge 1's expectation); whether they add anything is for the importance study.

## Files

- `features_ext/minute/ext_features.parquet`
- `features_ext/minute/ext_features_all.parquet`
- `features_ext/minute/ext_fit_report.json`
- `features_ext/minute/trunc_diff.json`
- `features_ext/minute/trunc_20250630_120000/ext_features_all.parquet`
- `features_ext/minute/trunc_20250630_120000/ext_fit_report.json`
- `features_ext/5minute/ext_features.parquet`
- `features_ext/5minute/ext_features_all.parquet`
- `features_ext/5minute/ext_fit_report.json`
- `features_ext/5minute/trunc_diff.json`
- `features_ext/5minute/trunc_20250630_120000/ext_features_all.parquet`
- `features_ext/5minute/trunc_20250630_120000/ext_fit_report.json`
- `features_ext/README.md`
- `studies/ext_features/build_ext.py`
- `studies/ext_features/ext_lib.py`
- `studies/ext_features/finalize.py`
- `studies/ext_features/write_docs.py`
- `studies/ext_features/run_minute.sh`
- `studies/ext_features/build_minute.log`
- `studies/ext_features/build_minute_trunc.log`
- `studies/ext_features/build_5minute.log`
- `studies/ext_features/build_5minute_trunc.log`
- `studies/ext_features/finalize_minute.log`
- `studies/ext_features/finalize_5minute.log`
