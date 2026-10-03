# null_tapes_drift: synthetic null tapes (c) and adversarial drift validation (d)

DESIGN_PANEL decision-making-3, parts (c) and (d), with both judges' fixes: (a) / (b) live in `harness.py`; the null tapes run on 5 minutes (20 full-length tapes per generator) and on 1 minute (8 one-year tapes per generator, RSS checked); the segment bootstrap is Judge 1's second null; the IS-vs-OOS adversarial check is not run here (oos_once.py post-mortem). No gate search, no OOS row read. Tape numbers never enter the ledger; the three reference gates on the real tape are ledger rows of family `null_tapes_drift/real_ref`. Scripts: `gen_tapes.py`, `tapes.py`, `run_tapes.py`, `drift.py`, `write_findings.py`; logs `run_5minute.log`, `run_minute.log`, `drift.log`, `topup_5minute.log`, `topup_minute.log`. **Repair round (section 11)**: the adversarial refuters found the engine locked out on part of the tapes; the certificate is now read on healthy tapes (the first-build numbers stay published beside it), `tapes.py` refuses time proxies, the two mechanical gates are labelled as what they are, and the missing `go_no_go` item is stated as a program-level gap.

## 1. Definitions (fixed before the numbers)

- **Unit / label / statistic** as the harness: a Foundation SETUP taken under the L1 (15:25) book; kept-vs-skipped difference of mean net (INR per unit); the session-matched random control percentile (`fz_report.random_control`, 2,000 draws); permutation p; block sign count. On a tape the statistic is computed by `harness.metrics` on a `harness.Table` built from the tape's own `features.parquet` / `trades.parquet` / `sessions.parquet` (`tapes.load_tape`, a copy of `harness.load` pointed at the tape folder). Every tape row is IS (the tapes carry IS calendar dates).
- **Three reference gates** (all as keep masks): `frozen_st7_st8` = keep where `fz_traded` (the frozen ST7/ST8 gate as it traded on that tape); `choch2_skip` = skip where `n_choch_since_bos >= 2` (mechanical reference gate 1); `sl_above_median_skip` = skip where `sl_dist_atr` > the tape's own IS median (mechanical reference gate 2). The two mechanical gates were **fixed in `tapes.py` before any tape was scored**; they are reference points for the engine-mechanics check, not candidates, and appear in no registration file (BRIEF H2 names the family `n_choch_since_bos >= k` without k; the stop-distance gate exists only here). Their ledger rows (section 3) carry the earlier wording 'pre-registered' in the config text, which this file supersedes. The engine-mechanics check: a gate on stop distance or CHoCH counts can read non-zero on a memory-free tape through the engine itself (Judge 2), so its null is not 0.
- **Generators** (fitted on IS bars only, `gen_tapes.py` docstring): *session bootstrap* (whole IS sessions with replacement, level chained through the drawn session's open-to-close path and a gap drawn from the IS gap distribution); *segment bootstrap* (30-bar clock-aligned blocks from random IS sessions, re-based and chained, same gap draw); *GMM-Markov* (GaussianMixture 4-6 full-covariance components by BIC on the z-scored per-bar vector (log return, log volume ratio to the clock median, range/atr14, close position), first-order Markov chain on the labels, per-session sampling with the clock volume profile, OHLC rebuilt consistently, samples clipped to the IS range per dimension). Full-length sessions only (375 / 75 bars); the real IS tape's short sessions are excluded from the pools (listed in `fit_<tf>.json`). Tapes are written in the near-month CSV format and pushed through `build/build.py --path` (engine.run with the Foundation rules, fz.run with the frozen ST7/ST8 block, L0 and L1 pricing, the same 261-column feature table).
- **Engine health of a tape / per-tape poor-null flag (repair round; `tapes.tape_health`)**: an IS session is *frozen* when the engine's protected level `prot` (bars.parquet) does not change inside it, equals the previous session's last value and no CHoCH occurs; a *dead run* is a run of frozen sessions longer than the real tape's longest such run (5minute 68, minute 69 sessions); *dead share* = sessions inside dead runs / sessions. A tape is **healthy** when dead share < 0.2 AND its SETUP rate is >= 0.333 x the real tape's. The flag reads bars / events / sessions / setups only, never a label or a gate statistic. **Tape sets**: `gates` = the **certificate**: the first DESIGN_N (20 / 8) healthy tapes per generator by seed index k (`tapes.tape_folders(tf, gen)` default; when the first build held fewer, the next seeds k = 20, 21, ... were generated until the count was reached: `run_tapes.py --target-healthy`); `gates_all_original` = the first build (k < DESIGN_N) with its locked tapes (the numbers the first version of this file reported); `gates_healthy_original` = the first build's healthy tapes only. The pass rule (section 7) reads the certificate set.
- **Null distribution** = per timeframe, generator, gate and tape set: p5 / p50 / p95 / mean / min / max of the tape diffs, the share of tapes with diff > 0, p50 / p95 of the control percentile, the real-tape value and its percentile among the tapes. **Comparison** (DESIGN_PANEL (c), Judge 1's go/no-go): the real-tape difference must be above the null-tape 95th percentile; here that is read on the two memory-free nulls (GMM-Markov and segment), with the session bootstrap as the stability read (share of tapes with the real diff's sign).
- **Reality check** per generator: within-session per-bar log-return std (bps) and excess kurtosis, autocorrelation of |r| at lags 1-5 (pairs inside a session), CHoCH / BOS / SETUP / L1-unit counts per session, the raw L1 book, the frozen gate's kept share, the final price level and median ATR14, over every tape built (the generator as it is) and over the certificate tapes; a generator whose median SETUP rate is outside [1/3, 3] x the real rate is flagged a poor null (generator level); the per-tape flag above is the tape level.
- **Adversarial validation (d)**: HistGradientBoostingClassifier IS-early (2021-10-01..2023-09-30) vs IS-late (2023-10-01..2025-12-31) on `harness.design(T)` of the real tape, IS rows; pooled out-of-fold AUC under `harness.purged_splits` (12 blocks, purge by exit bar, 3-session embargo); chance = 20 label permutations; variant A = all as-of columns, variant B = without time proxies (|Spearman rho| >= 0.9 with `session_idx`); SHAP (TreeExplainer) ranking on B with the direction of drift.

## 2. Generator fits (IS bars only)

| tf | IS sessions (full / short excluded) | IS bars | gaps | gap log-std | GMM K (BIC 4/5/6) | GMM fit rows | design tapes x sessions | refit reproduces first build |
|---|---|---|---|---|---|---|---|---|
| 5minute | 1026 (1016 / 10) | 76,621 | 1025 | 0.00488 | 6 (681,123, 675,927, 668,815) | 76,200 | 20 x 1026 | True |
| minute | 1026 (1012 / 14) | 383,076 | 1025 | 0.00488 | 6 (3,520,657, 2,912,397, 2,895,928) | 379,500 | 8 x 247 | True |

### 2a. build.py cost per tape (from each tape's `meta.json`; the first build ran on a box shared with other studies, load 12-20; the top-up with 3-4 concurrent builds, load 4-9)

| tf | generator | tapes built (first build + top-up) | bars per tape | SETUPs p50 [min, max] | build seconds p50 [min, max] | peak RSS MB p50 [max] |
|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | 29 (20 + 9) | 76,950 | 1024 [171, 1272] | 66 [14, 99] | 428 [468] |
| 5minute | segment bootstrap (30-bar blocks) | 25 (20 + 5) | 76,950 | 911 [193, 1107] | 74 [16, 88] | 428 [461] |
| 5minute | session bootstrap | 40 (20 + 20) | 76,950 | 775 [79, 1111] | 57 [16, 94] | 429 [463] |
| minute | GMM-Markov | 8 (8 + 0) | 92,625 | 1460 [1261, 1676] | 88 [68, 98] | 483 [516] |
| minute | segment bootstrap (30-bar blocks) | 10 (8 + 2) | 92,625 | 988 [435, 1332] | 54 [26, 68] | 473 [519] |
| minute | session bootstrap | 10 (8 + 2) | 92,625 | 1033 [494, 1457] | 72 [25, 91] | 473 [499] |

### 2b. Tape sets after the health check (`tape_health.csv`, `null_distributions.json`)

| tf | generator | built | first build | healthy (first build) | lock-out rate (first build) | top-up tapes | healthy (all built) | certificate tapes | certificate k |
|---|---|---|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | 29 | 20 | 14 | 0.30 | 9 | 21 | 20 | 0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15, 17, 21, 22, 23, 24, 25, 26 |
| 5minute | segment bootstrap (30-bar blocks) | 25 | 20 | 16 | 0.20 | 5 | 21 | 20 | 0, 1, 2, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23 |
| 5minute | session bootstrap | 40 | 20 | 10 | 0.50 | 20 | 24 | 20 | 1, 4, 8, 9, 10, 11, 12, 14, 15, 19, 21, 23, 24, 25, 26, 29, 30, 32, 33, 34 |
| minute | GMM-Markov | 8 | 8 | 8 | 0.00 | 0 | 8 | 8 | 0, 1, 2, 3, 4, 5, 6, 7 |
| minute | segment bootstrap (30-bar blocks) | 10 | 8 | 7 | 0.12 | 2 | 8 | 8 | 0, 1, 2, 4, 5, 6, 7, 8 |
| minute | session bootstrap | 10 | 8 | 7 | 0.12 | 2 | 8 | 8 | 0, 1, 2, 4, 5, 6, 7, 9 |

## 3. The three reference gates on the real tape (IS, L1; ledger family `null_tapes_drift/real_ref`)

| tf | gate | ledger id | n | kept n (share) | kept mean | skipped mean | diff | diff top1% removed | perm p | control pct | loser recall | winner recall (net-wtd) | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5minute | frozen_st7_st8 | 9f4e08a75d0ab931 | 826 | 325 (0.394) | -978.81 | -613.20 | **-365.62** | -304.01 | 0.2489 | 12.4 | 0.605 | 0.369 | 3 |
| 5minute | choch2_skip | c994cebf43aa41d5 | 826 | 567 (0.686) | -676.21 | -934.04 | **257.83** | 151.83 | 0.4623 | 46.6 | 0.330 | 0.718 | 6 |
| 5minute | sl_above_median_skip | 71caa03d48830f17 | 826 | 414 (0.501) | -740.27 | -773.92 | **33.65** | 166.65 | 0.9185 | 99.8 | 0.479 | 0.415 | 6 |
| minute | frozen_st7_st8 | 249b8433a25f5b8a | 4452 | 745 (0.167) | -1,026.02 | -1,006.31 | **-19.71** | -8.44 | 0.8516 | 64.0 | 0.835 | 0.173 | 6 |
| minute | choch2_skip | ace645aec2224464 | 4452 | 2908 (0.653) | -1,034.75 | -962.25 | **-72.50** | -105.62 | 0.3798 | 1.6 | 0.342 | 0.670 | 4 |
| minute | sl_above_median_skip | 21f5c361c64d6fe8 | 4452 | 2226 (0.500) | -1,003.57 | -1,015.64 | **12.07** | 25.78 | 0.8696 | 99.0 | 0.485 | 0.418 | 8 |

`sl_dist_atr` IS median: 5minute 1.7106, minute 2.4000.

## 4. Null distributions (the certificate: `null_distributions.json` -> `gates`, read on the certificate tape set)

Diff = kept-vs-skipped mean L1 net on the tape (INR per unit). `real pct` = the real-tape diff's percentile among the tapes; `real > p95` = the pass-rule comparison for that generator. The certificate set = the first DESIGN_N healthy tapes per generator (section 1); the first-build numbers follow in 4a.

| tf | generator | gate | tapes | units p50 [min, max] | kept share p50 | diff p5 | diff p50 | diff p95 | diff min / max | share diff>0 | control pct p50 / p95 | share ctrl>=95 | real diff | real pct | real > p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | choch2_skip | 20 | 1,058 [917, 1,211] | 0.690 | -385.35 | 37.88 | **516.38** | -430.00 / 554.66 | 0.550 | 5.4 / 60.6 | 0.000 | 257.83 | 80.0 | no |
| 5minute | GMM-Markov | frozen_st7_st8 | 20 | 1,058 [917, 1,211] | 0.300 | -166.70 | 191.66 | **530.00** | -391.03 / 676.36 | 0.800 | 94.7 / 99.9 | 0.500 | -365.62 | 5.0 | no |
| 5minute | GMM-Markov | sl_above_median_skip | 20 | 1,058 [917, 1,211] | 0.500 | -231.37 | 16.74 | **419.69** | -276.78 / 642.33 | 0.600 | 95.0 / 100.0 | 0.500 | 33.65 | 55.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | choch2_skip | 20 | 918 [778, 1,100] | 0.670 | -230.95 | 5.46 | **500.14** | -267.98 / 579.55 | 0.500 | 4.8 / 29.1 | 0.000 | 257.83 | 80.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 20 | 918 [778, 1,100] | 0.360 | -248.99 | 105.51 | **566.42** | -410.61 / 642.26 | 0.600 | 94.4 / 99.8 | 0.500 | -365.62 | 5.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 20 | 918 [778, 1,100] | 0.500 | -656.69 | -191.32 | **620.74** | -715.66 / 860.19 | 0.450 | 97.9 / 99.8 | 0.750 | 33.65 | 65.0 | no |
| 5minute | session bootstrap | choch2_skip | 20 | 925 [727, 1,042] | 0.680 | -319.39 | 173.26 | **827.38** | -423.87 / 1,141.33 | 0.650 | 10.6 / 59.1 | 0.000 | 257.83 | 60.0 | no |
| 5minute | session bootstrap | frozen_st7_st8 | 20 | 925 [727, 1,042] | 0.390 | -240.81 | 45.80 | **554.71** | -405.87 / 588.05 | 0.650 | 92.8 / 98.5 | 0.400 | -365.62 | 5.0 | no |
| 5minute | session bootstrap | sl_above_median_skip | 20 | 925 [727, 1,042] | 0.500 | -778.07 | -346.06 | **148.62** | -884.52 / 354.87 | 0.200 | 79.7 / 99.0 | 0.350 | 33.65 | 80.0 | no |
| minute | GMM-Markov | choch2_skip | 8 | 1,436 [1,244, 1,650] | 0.670 | -1.13 | 105.34 | **246.98** | -4.22 / 286.72 | 0.875 | 61.5 / 89.2 | 0.000 | -72.50 | 0.0 | no |
| minute | GMM-Markov | frozen_st7_st8 | 8 | 1,436 [1,244, 1,650] | 0.150 | -251.78 | -93.89 | **23.00** | -299.94 / 37.28 | 0.125 | 42.8 / 83.8 | 0.000 | -19.71 | 75.0 | no |
| minute | GMM-Markov | sl_above_median_skip | 8 | 1,436 [1,244, 1,650] | 0.500 | -112.96 | 32.02 | **96.58** | -139.38 / 110.02 | 0.625 | 71.0 / 93.7 | 0.125 | 12.07 | 37.5 | no |
| minute | segment bootstrap (30-bar blocks) | choch2_skip | 8 | 1,126 [613, 1,316] | 0.640 | -425.10 | -100.32 | **144.79** | -483.88 / 176.70 | 0.375 | 6.7 / 36.1 | 0.000 | -72.50 | 50.0 | no |
| minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 8 | 1,126 [613, 1,316] | 0.160 | -124.59 | 16.51 | **272.51** | -158.04 / 295.83 | 0.500 | 56.0 / 95.4 | 0.125 | -19.71 | 37.5 | no |
| minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 8 | 1,126 [613, 1,316] | 0.500 | -226.02 | -61.20 | **129.55** | -272.36 / 136.91 | 0.375 | 61.4 / 92.6 | 0.125 | 12.07 | 62.5 | no |
| minute | session bootstrap | choch2_skip | 8 | 1,096 [840, 1,445] | 0.660 | -259.42 | -78.84 | **136.47** | -263.67 / 222.48 | 0.125 | 8.3 / 35.8 | 0.000 | -72.50 | 62.5 | no |
| minute | session bootstrap | frozen_st7_st8 | 8 | 1,096 [840, 1,445] | 0.160 | -206.16 | 29.83 | **225.03** | -237.99 / 232.81 | 0.625 | 53.5 / 83.0 | 0.000 | -19.71 | 37.5 | no |
| minute | session bootstrap | sl_above_median_skip | 8 | 1,096 [840, 1,445] | 0.500 | -208.64 | -22.91 | **94.14** | -256.58 / 116.35 | 0.375 | 89.8 / 98.2 | 0.250 | 12.07 | 62.5 | no |

### 4a. The same cells on the first build, with and without its locked tapes (`gates_all_original`, `gates_healthy_original`)

`all` = the 20 / 8 tapes of the first build, locked ones included (what the first version of this file reported); `healthy` = its healthy tapes; `certificate` = section 4. `delta p95` = certificate p95 vs first-build-all p95. The verdict (real > p95) is given for `all` and for the certificate.

| tf | generator | gate | tapes all / healthy / cert | units min all / cert | p50 all | p95 all | p50 healthy | p95 healthy | p50 cert | p95 cert | delta p95 | ctrl p95 all / cert | real diff | real pct all / cert | real > p95 all / cert |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | frozen_st7_st8 | 20 / 14 / 20 | 170 / 917 | 191.66 | 708.82 | 255.12 | 576.22 | 191.66 | **530.00** | -25% | 100.0 / 99.9 | -365.62 | 0.0 / 5.0 | no / no |
| 5minute | GMM-Markov | choch2_skip | 20 / 14 / 20 | 170 / 917 | 91.75 | 516.38 | 91.75 | 528.47 | 37.88 | **516.38** | +0% | 56.1 / 60.6 | 257.83 | 80.0 / 80.0 | no / no |
| 5minute | GMM-Markov | sl_above_median_skip | 20 / 14 / 20 | 170 / 917 | 97.75 | 483.41 | 97.75 | 490.00 | 16.74 | **419.69** | -13% | 100.0 / 100.0 | 33.65 | 40.0 / 55.0 | no / no |
| 5minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 20 / 16 / 20 | 191 / 778 | 164.72 | 566.42 | 147.05 | 582.39 | 105.51 | **566.42** | +0% | 99.8 / 99.8 | -365.62 | 0.0 / 5.0 | no / no |
| 5minute | segment bootstrap (30-bar blocks) | choch2_skip | 20 / 16 / 20 | 191 / 778 | 35.06 | 441.96 | 1.05 | 470.93 | 5.46 | **500.14** | +13% | 36.6 / 29.1 | 257.83 | 80.0 / 80.0 | no / no |
| 5minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 20 / 16 / 20 | 191 / 778 | -212.74 | 620.74 | -100.11 | 671.15 | -191.32 | **620.74** | +0% | 99.8 / 99.8 | 33.65 | 65.0 / 65.0 | no / no |
| 5minute | session bootstrap | frozen_st7_st8 | 20 / 10 / 20 | 78 / 727 | 85.92 | 420.40 | 45.80 | 244.03 | 45.80 | **554.71** | +32% | 98.9 / 98.5 | -365.62 | 10.0 / 5.0 | no / no |
| 5minute | session bootstrap | choch2_skip | 20 / 10 / 20 | 78 / 727 | 127.18 | 700.52 | 190.42 | 748.14 | 173.26 | **827.38** | +18% | 59.6 / 59.1 | 257.83 | 65.0 / 60.0 | no / no |
| 5minute | session bootstrap | sl_above_median_skip | 20 / 10 / 20 | 78 / 727 | -331.03 | 131.37 | -263.59 | 134.73 | -346.06 | **148.62** | +13% | 99.0 / 99.0 | 33.65 | 90.0 / 80.0 | no / no |
| minute | GMM-Markov | frozen_st7_st8 | 8 / 8 / 8 | 1,244 / 1,244 | -93.89 | 23.00 | -93.89 | 23.00 | -93.89 | **23.00** | +0% | 83.8 / 83.8 | -19.71 | 75.0 / 75.0 | no / no |
| minute | GMM-Markov | choch2_skip | 8 / 8 / 8 | 1,244 / 1,244 | 105.34 | 246.98 | 105.34 | 246.98 | 105.34 | **246.98** | +0% | 89.2 / 89.2 | -72.50 | 0.0 / 0.0 | no / no |
| minute | GMM-Markov | sl_above_median_skip | 8 / 8 / 8 | 1,244 / 1,244 | 32.02 | 96.58 | 32.02 | 96.58 | 32.02 | **96.58** | +0% | 93.7 / 93.7 | 12.07 | 37.5 / 37.5 | no / no |
| minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 8 / 7 / 8 | 430 / 613 | 16.51 | 272.51 | 50.07 | 275.84 | 16.51 | **272.51** | +0% | 95.4 / 95.4 | -19.71 | 37.5 / 37.5 | no / no |
| minute | segment bootstrap (30-bar blocks) | choch2_skip | 8 / 7 / 8 | 430 / 613 | -61.29 | 144.79 | -11.64 | 149.35 | -100.32 | **144.79** | +0% | 36.1 / 36.1 | -72.50 | 50.0 / 50.0 | no / no |
| minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 8 / 7 / 8 | 430 / 613 | 37.22 | 129.55 | -25.61 | 130.60 | -61.20 | **129.55** | +0% | 92.6 / 92.6 | 12.07 | 50.0 / 62.5 | no / no |
| minute | session bootstrap | frozen_st7_st8 | 8 / 7 / 8 | 485 / 840 | 76.99 | 468.29 | 52.46 | 226.14 | 29.83 | **225.03** | -52% | 90.7 / 83.0 | -19.71 | 25.0 / 37.5 | no / no |
| minute | session bootstrap | choch2_skip | 8 / 7 / 8 | 485 / 840 | -78.84 | 136.47 | -76.19 | 148.75 | -78.84 | **136.47** | +0% | 35.8 / 35.8 | -72.50 | 62.5 / 62.5 | no / no |
| minute | session bootstrap | sl_above_median_skip | 8 / 7 / 8 | 485 / 840 | -22.91 | 94.14 | -20.36 | 97.31 | -22.91 | **94.14** | +0% | 94.8 / 98.2 | 12.07 | 62.5 / 62.5 | no / no |

Verdict flips between the first-build-all set and the certificate set: **0 of 18**.

### 4b. Reading of the reference gates against their own nulls (certificate set)

- **5minute / frozen_st7_st8**: real diff -365.62 (control pct 12.4); gmm: n 20, p50 191.66, p95 530.00, real pct 5.0, same sign 0.20; segment: n 20, p50 105.51, p95 566.42, real pct 5.0, same sign 0.40; session: n 20, p50 45.80, p95 554.71, real pct 5.0, same sign 0.35 -> does NOT pass the null-tape check.
- **5minute / choch2_skip**: real diff 257.83 (control pct 46.6); gmm: n 20, p50 37.88, p95 516.38, real pct 80.0, same sign 0.55; segment: n 20, p50 5.46, p95 500.14, real pct 80.0, same sign 0.50; session: n 20, p50 173.26, p95 827.38, real pct 60.0, same sign 0.65 -> does NOT pass the null-tape check.
- **5minute / sl_above_median_skip**: real diff 33.65 (control pct 99.8); gmm: n 20, p50 16.74, p95 419.69, real pct 55.0, same sign 0.60; segment: n 20, p50 -191.32, p95 620.74, real pct 65.0, same sign 0.45; session: n 20, p50 -346.06, p95 148.62, real pct 80.0, same sign 0.20 -> does NOT pass the null-tape check.
- **minute / frozen_st7_st8**: real diff -19.71 (control pct 64.0); gmm: n 8, p50 -93.89, p95 23.00, real pct 75.0, same sign 0.88; segment: n 8, p50 16.51, p95 272.51, real pct 37.5, same sign 0.50; session: n 8, p50 29.83, p95 225.03, real pct 37.5, same sign 0.38 -> does NOT pass the null-tape check.
- **minute / choch2_skip**: real diff -72.50 (control pct 1.6); gmm: n 8, p50 105.34, p95 246.98, real pct 0.0, same sign 0.12; segment: n 8, p50 -100.32, p95 144.79, real pct 50.0, same sign 0.62; session: n 8, p50 -78.84, p95 136.47, real pct 62.5, same sign 0.88 -> does NOT pass the null-tape check.
- **minute / sl_above_median_skip**: real diff 12.07 (control pct 99.0); gmm: n 8, p50 32.02, p95 96.58, real pct 37.5, same sign 0.62; segment: n 8, p50 -61.20, p95 129.55, real pct 62.5, same sign 0.38; session: n 8, p50 -22.91, p95 94.14, real pct 62.5, same sign 0.38 -> does NOT pass the null-tape check.

### 4c. Key readings (numbers from `null_distributions.json`, certificate set)

1. **The frozen ST7/ST8 gate on memory-free 5-minute tapes**: GMM-Markov median diff 191.66 (p95 530.00, share of tapes > 0 0.80, control pct p50 94.7, 50% of tapes at or above the 95th control percentile); segment median 105.51 (p95 566.42, control pct p50 94.4, 50% at or above 95); session median 45.80 (p95 554.71). On tapes with no swing memory the rooms gate still separates kept from skipped by a positive median and clears the random control on a large share of tapes: that part of any ST7/ST8-shaped statistic is engine / FZ mechanics, not market memory. The real 5-minute frozen gate (-365.62, control pct 12.4) sits at the 5th percentile of the GMM null and the 5th of the segment null: on the real tape it does worse than on its own memory-free tapes.
2. **The stop-distance gate's control percentile is mechanical**: on the real tape it reads 99.8 (5 min, diff 33.65) and 99.0 (1 min, diff 12.07); on the memory-free tapes its control percentile has p50 95.0 / 97.9 (5 min GMM / segment) and 71.0 / 61.4 (1 min), and the real diff sits at the 55th / 65th (5 min) and 38th / 62nd (1 min) percentile of its null. A high control percentile for a gate on stop distance is what the engine produces on a random tape (Judge 2's warning, measured); the null p95 of the diff, not the control percentile, is the bar.
3. **The CHoCH-count gate**: 5 min real diff 257.83 (control pct 46.6) is at the 80th / 80th percentile of the GMM / segment nulls (p95 516.38 / 500.14): not above p95 on both memory-free generators. 1 min real diff -72.50 (control pct 1.6) against a GMM null median of 105.34 (0.88 of tapes positive): the real 1-minute CHoCH-count gate sits at the 0th percentile of its memory-free null; the 'CHoCH, CHoCH, no BOS = sideways' skip does not read as market memory on this tape.
4. **Consequence for the gate studies**: a candidate's real-tape diff must clear the p95 of the certificate tapes of its own family shape (section 7), and its control percentile must be read against the null's control-percentile distribution (`control_pct_p95` per gate); a control percentile alone, even 99+, is not evidence for a gate that touches the stop or the event stream.

## 5. Reality check of the generators (IS part of the real tape vs every tape built; tape p50 [min, max]; the min / max carry the locked tapes)

### 5minute

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| ret std (bps) | 7.369 | 7.070 [6.940, 7.150] | 7.330 [7.040, 7.500] | 7.350 [7.090, 7.790] |
| ret excess kurtosis | 14.6 | 6.2 [5.8, 6.8] | 13.8 [5.3, 22.4] | 14.9 [6.0, 28.0] |
| abs-return autocorr lag 1 | 0.234 | 0.110 [0.100, 0.120] | 0.220 [0.200, 0.250] | 0.230 [0.200, 0.270] |
| lag 2 | 0.234 | 0.030 [0.020, 0.040] | 0.210 [0.170, 0.260] | 0.230 [0.190, 0.300] |
| lag 3 | 0.218 | 0.010 [-0.000, 0.020] | 0.190 [0.160, 0.230] | 0.220 [0.180, 0.270] |
| lag 4 | 0.210 | 0.000 [-0.010, 0.010] | 0.180 [0.150, 0.220] | 0.210 [0.170, 0.260] |
| lag 5 | 0.211 | 0.000 [-0.010, 0.010] | 0.180 [0.140, 0.220] | 0.210 [0.170, 0.270] |
| CHoCH / session | 1.204 | 1.640 [0.250, 1.990] (x1.36) | 1.340 [0.290, 1.650] (x1.12) | 1.130 [0.120, 1.670] (x0.94) |
| BOS / session | 5.428 | 5.650 [5.510, 5.910] (x1.04) | 5.350 [5.180, 5.610] (x0.98) | 5.440 [5.300, 5.640] (x1.00) |
| SETUPs / session | 0.811 | 1.000 [0.170, 1.240] (x1.23) | 0.890 [0.190, 1.080] (x1.09) | 0.760 [0.080, 1.080] (x0.93) |
| L1 units / session | 0.805 | 0.990 [0.170, 1.220] (x1.23) | 0.880 [0.190, 1.070] (x1.09) | 0.750 [0.080, 1.070] (x0.93) |
| L1 mean net | -757.0 | -1,104.3 [-1,315.0, -846.1] | -1,041.8 [-1,350.1, -697.6] | -830.6 [-1,187.3, -180.3] |
| L1 win rate | 0.277 | 0.250 [0.210, 0.270] | 0.250 [0.220, 0.290] | 0.260 [0.230, 0.310] |
| frozen kept share | 0.394 | 0.300 [0.270, 0.350] | 0.360 [0.330, 0.400] | 0.370 [0.310, 0.440] |
| last close | 26,300.0 | 27,600.1 [18,001.3, 43,826.4] | 25,684.8 [18,891.4, 36,606.2] | 27,070.8 [18,194.5, 52,555.4] |
| ATR14 median | 20.3 | 24.3 [19.4, 35.6] | 21.4 [17.3, 28.5] | 22.2 [16.1, 30.9] |
| lock-out rate, first build (tapes) | 0 | 0.30 (6 / 20) | 0.20 (4 / 20) | 0.50 (10 / 20) |
| lock-out rate, all built (tapes) | 0 | 0.28 (8 / 29) | 0.16 (4 / 25) | 0.40 (16 / 40) |

Generator-level poor-null flag (median SETUP rate outside [1/3, 3] x real): none. Per-tape poor-null flags (locked tapes, section 5c): GMM-Markov k = [6, 13, 14, 16, 18, 19, 20, 27]; segment bootstrap (30-bar blocks) k = [3, 7, 9, 16]; session bootstrap k = [0, 2, 3, 5, 6, 7, 13, 16, 17, 18, 20, 22, 27, 28, 31, 36].

Engine rates on the certificate tapes only (p50, x real):

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| CHoCH / session | 1.204 | 1.690 [1.440, 1.990] (x1.41) | 1.390 [1.160, 1.650] (x1.16) | 1.360 [1.070, 1.530] (x1.13) |
| BOS / session | 5.428 | 5.610 [5.510, 5.750] (x1.03) | 5.330 [5.180, 5.410] (x0.98) | 5.420 [5.300, 5.550] (x1.00) |
| SETUPs / session | 0.811 | 1.040 [0.900, 1.190] (x1.29) | 0.900 [0.770, 1.080] (x1.11) | 0.920 [0.710, 1.020] (x1.13) |
| L1 units / session | 0.805 | 1.030 [0.890, 1.180] (x1.28) | 0.890 [0.760, 1.070] (x1.11) | 0.900 [0.710, 1.020] (x1.12) |
| L1 mean net | -757.0 | -1,125.0 [-1,315.0, -936.6] | -1,039.0 [-1,214.3, -697.6] | -923.4 [-1,077.9, -507.3] |
| frozen kept share | 0.394 | 0.300 [0.280, 0.350] | 0.360 [0.340, 0.380] | 0.390 [0.330, 0.420] |

### minute

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| ret std (bps) | 3.408 | 3.300 [3.260, 3.310] | 3.450 [3.350, 3.580] | 3.310 [3.120, 3.730] |
| ret excess kurtosis | 21.7 | 5.1 [5.0, 5.5] | 30.4 [9.6, 37.9] | 7.3 [4.6, 52.4] |
| abs-return autocorr lag 1 | 0.277 | 0.070 [0.060, 0.080] | 0.280 [0.260, 0.300] | 0.250 [0.220, 0.340] |
| lag 2 | 0.246 | 0.020 [0.010, 0.020] | 0.240 [0.220, 0.250] | 0.220 [0.200, 0.310] |
| lag 3 | 0.230 | 0.000 [0.000, 0.010] | 0.210 [0.200, 0.230] | 0.210 [0.180, 0.290] |
| lag 4 | 0.225 | -0.000 [-0.010, 0.000] | 0.200 [0.190, 0.220] | 0.210 [0.180, 0.270] |
| lag 5 | 0.222 | -0.000 [-0.010, 0.000] | 0.200 [0.180, 0.220] | 0.200 [0.180, 0.270] |
| CHoCH / session | 6.617 | 10.080 [8.840, 12.180] (x1.52) | 6.110 [2.650, 8.210] (x0.92) | 6.330 [2.920, 8.860] (x0.96) |
| BOS / session | 26.7 | 30.4 [30.0, 31.0] (x1.14) | 26.4 [25.9, 27.3] (x0.99) | 26.8 [26.4, 27.4] (x1.00) |
| SETUPs / session | 4.388 | 5.910 [5.110, 6.790] (x1.35) | 4.000 [1.760, 5.390] (x0.91) | 4.180 [2.000, 5.900] (x0.95) |
| L1 units / session | 4.339 | 5.820 [5.040, 6.680] (x1.34) | 3.970 [1.740, 5.330] (x0.91) | 4.160 [1.960, 5.850] (x0.96) |
| L1 mean net | -1,009.6 | -1,003.5 [-1,084.6, -900.1] | -1,000.3 [-1,081.2, -827.9] | -957.1 [-1,075.4, -719.9] |
| L1 win rate | 0.156 | 0.160 [0.150, 0.180] | 0.150 [0.130, 0.170] | 0.150 [0.130, 0.180] |
| frozen kept share | 0.167 | 0.150 [0.150, 0.170] | 0.160 [0.140, 0.180] | 0.160 [0.140, 0.180] |
| last close | 26,300.0 | 18,431.6 [16,727.3, 20,986.6] | 19,165.1 [15,184.8, 25,411.9] | 19,847.8 [14,767.5, 23,861.8] |
| ATR14 median | 8.568 | 9.720 [9.200, 11.120] | 7.760 [6.930, 8.500] | 7.470 [6.490, 8.350] |
| lock-out rate, first build (tapes) | 0 | 0.00 (0 / 8) | 0.12 (1 / 8) | 0.12 (1 / 8) |
| lock-out rate, all built (tapes) | 0 | 0.00 (0 / 8) | 0.20 (2 / 10) | 0.20 (2 / 10) |

Generator-level poor-null flag (median SETUP rate outside [1/3, 3] x real): none. Per-tape poor-null flags (locked tapes, section 5c): GMM-Markov k = []; segment bootstrap (30-bar blocks) k = [3, 9]; session bootstrap k = [3, 8].

Engine rates on the certificate tapes only (p50, x real):

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| CHoCH / session | 6.617 | 10.080 [8.840, 12.180] (x1.52) | 6.910 [3.790, 8.210] (x1.04) | 6.760 [5.280, 8.860] (x1.02) |
| BOS / session | 26.7 | 30.4 [30.0, 31.0] (x1.14) | 26.3 [25.9, 26.8] (x0.99) | 26.8 [26.4, 27.4] (x1.00) |
| SETUPs / session | 4.388 | 5.910 [5.110, 6.790] (x1.35) | 4.590 [2.520, 5.390] (x1.05) | 4.490 [3.430, 5.900] (x1.02) |
| L1 units / session | 4.339 | 5.820 [5.040, 6.680] (x1.34) | 4.560 [2.480, 5.330] (x1.05) | 4.440 [3.400, 5.850] (x1.02) |
| L1 mean net | -1,009.6 | -1,003.5 [-1,084.6, -900.1] | -1,018.8 [-1,081.2, -827.9] | -986.6 [-1,075.4, -719.9] |
| frozen kept share | 0.167 | 0.150 [0.150, 0.170] | 0.160 [0.150, 0.180] | 0.160 [0.150, 0.180] |

The 1-minute tapes are one trading year (247 sessions) starting at the real IS first open (17,523.70), so `last close` and `ATR14 median` are not comparable with the real 5-year IS values in this table; the per-session rates and return moments are.

### 5b. Engine scale and ordering check (`engine_scale_check.json`; 5-minute IS full sessions, Strategy 2 rules)

| bars | CHoCH / session | BOS / session | SETUPs / session | swings |
|---|---|---|---|---|
| real order | 1.168 | 5.460 | 0.788 | 22,868 |
| real order x2 price | 1.168 | 5.460 | 0.788 | 22,868 |
| real order rebased real gaps | 1.168 | 5.460 | 0.788 | 22,868 |
| real order random gaps | 1.377 | 5.412 | 0.912 | 22,798 |
| shuffled sessions real gap sequence | 1.368 | 5.343 | 0.909 | 22,786 |
| shuffled sessions zero gaps | 1.374 | 5.448 | 0.922 | 22,639 |
| real order zero gaps | 1.739 | 5.359 | 1.132 | 22,566 |

Scale-free (x2 price level gives identical counts): **True**. Re-basing the real sessions with the real gaps reproduces the real counts exactly; redrawing the gaps or shuffling the sessions moves the CHoCH rate by ~+17% and removing the gaps altogether by ~+50%: the engine's event rate is a property of the multi-day path, which is exactly what a null tape randomises. The per-tape variance this creates has two parts: the ordinary spread of healthy tapes (section 4, units min / max of the certificate set) and the lock-out of section 5c.

### 5c. Engine lock-out on the null tapes (repair round; `tape_health.csv`, `tapes/<tf>/<gen>_<k>/tape_health.json`)

**Mechanism** (engine.py, protected level): the protected level `prot` is the last unbroken *candidate* swing of the current trend; a swing becomes a candidate only when it lies on the far side of the AVWAP anchored at the last trend flip (`qualifies`: a low below that AVWAP in an up-trend, a high above it in a down-trend). On a driftless random-walk tape a long one-directional walk leaves the anchored AVWAP far behind, no new swing qualifies, `prot` freezes at the last candidate, and a CHoCH (a close beyond `prot` against the trend) becomes unreachable while BOS (a break of the last swing high / low with the trend) continues at its normal rate; no CHoCH means no SETUP. The real market returns to its anchored levels often enough that the real tape's longest frozen run is 68 / 69 sessions (5minute / minute); the locked tapes carry runs of 76-932 sessions. A run can end when the walk wanders back (a recovered mid-tape lock-out; the tail rule alone misses these) or last to the end of the tape.

| tf | tape | sessions | dead sessions (share) | dead tail share | longest frozen run (from) | last CHoCH | last SETUP | SETUPs / session (x real) | L1 units | prot at end | close at end | gap pts | reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5minute | gmm_6 | 1026 | 726 (0.708) | 0.625 | 641 (2023-05-04) | 2023-05-03 | 2023-05-03 | 0.364 (x0.45) | 370 | 24,642.1 | 43,826.4 | 19,184 | ['dead share 0.708 >= 0.2'] |
| 5minute | gmm_13 | 1026 | 643 (0.627) | 0.072 | 327 (2023-05-15) | 2025-09-12 | 2025-09-12 | 0.445 (x0.55) | 445 | 24,152.2 | 27,937.7 | 3,786 | ['dead share 0.627 >= 0.2'] |
| 5minute | gmm_14 | 1026 | 237 (0.231) | 0.002 | 163 (2023-05-08) | 2025-12-29 | 2025-12-29 | 0.906 (x1.12) | 917 | 21,375.0 | 21,876.9 | 502 | ['dead share 0.231 >= 0.2'] |
| 5minute | gmm_16 | 1026 | 498 (0.485) | 0.486 | 498 (2023-11-30) | 2023-11-28 | 2023-11-29 | 0.582 (x0.72) | 589 | 24,759.8 | 41,860.0 | 17,100 | ['dead share 0.485 >= 0.2'] |
| 5minute | gmm_18 | 1026 | 891 (0.868) | 0.871 | 891 (2022-04-26) | 2022-04-20 | 2022-04-20 | 0.167 (x0.21) | 170 | 18,425.3 | 40,508.9 | 22,084 | ['dead share 0.868 >= 0.2', 'setup rate 0.206 x real < 0.333'] |
| 5minute | gmm_19 | 1026 | 577 (0.562) | 0.565 | 577 (2023-08-03) | 2023-07-28 | 2023-07-28 | 0.460 (x0.57) | 467 | 25,011.4 | 41,861.2 | 16,850 | ['dead share 0.562 >= 0.2'] |
| 5minute | gmm_20 | 1026 | 236 (0.230) | 0.001 | 236 (2023-10-17) | 2025-12-30 | 2025-12-31 | 0.864 (x1.06) | 870 | 34,860.5 | 34,543.0 | -318 | ['dead share 0.230 >= 0.2'] |
| 5minute | gmm_27 | 1026 | 663 (0.646) | 0.526 | 539 (2023-09-28) | 2023-09-26 | 2023-09-26 | 0.451 (x0.56) | 457 | 19,241.7 | 30,578.8 | 11,337 | ['dead share 0.646 >= 0.2'] |
| 5minute | segment_3 | 1026 | 436 (0.425) | 0.425 | 436 (2024-02-28) | 2024-02-27 | 2024-02-27 | 0.571 (x0.70) | 578 | 21,537.2 | 36,606.2 | 15,069 | ['dead share 0.425 >= 0.2'] |
| 5minute | segment_7 | 1026 | 850 (0.829) | 0.831 | 850 (2022-06-27) | 2022-06-21 | 2022-06-21 | 0.188 (x0.23) | 191 | 16,273.4 | 29,884.5 | 13,611 | ['dead share 0.828 >= 0.2', 'setup rate 0.232 x real < 0.333'] |
| 5minute | segment_9 | 1026 | 283 (0.276) | 0.005 | 283 (2023-05-08) | 2025-12-23 | 2025-12-23 | 0.838 (x1.03) | 843 | 28,437.1 | 29,052.5 | 615 | ['dead share 0.276 >= 0.2'] |
| 5minute | segment_16 | 1026 | 221 (0.215) | 0.000 | 221 (2023-04-11) | 2025-12-31 | 2025-12-31 | 0.730 (x0.90) | 744 | 36,061.2 | 36,174.8 | 114 | ['dead share 0.215 >= 0.2'] |
| 5minute | session_0 | 1026 | 577 (0.562) | 0.574 | 577 (2023-08-03) | 2023-07-17 | 2023-07-17 | 0.324 (x0.40) | 328 | 24,505.7 | 49,313.4 | 24,808 | ['dead share 0.562 >= 0.2'] |
| 5minute | session_2 | 1026 | 352 (0.343) | 0.033 | 352 (2023-09-13) | 2025-11-12 | 2025-11-12 | 0.624 (x0.77) | 633 | 20,426.7 | 22,737.2 | 2,311 | ['dead share 0.343 >= 0.2'] |
| 5minute | session_3 | 1026 | 242 (0.236) | 0.009 | 242 (2022-12-30) | 2025-12-17 | 2025-12-17 | 0.718 (x0.89) | 727 | 29,550.5 | 31,359.7 | 1,809 | ['dead share 0.236 >= 0.2'] |
| 5minute | session_5 | 1026 | 297 (0.289) | 0.000 | 166 (2024-04-15) | 2025-12-31 | 2025-12-31 | 0.633 (x0.78) | 643 | - | 27,039.0 | - | ['dead share 0.289 >= 0.2'] |
| 5minute | session_6 | 1026 | 438 (0.427) | 0.000 | 438 (2022-02-18) | 2025-12-31 | 2025-12-31 | 0.470 (x0.58) | 478 | 35,184.8 | 35,136.3 | -48 | ['dead share 0.427 >= 0.2'] |
| 5minute | session_7 | 1026 | 730 (0.712) | 0.728 | 730 (2022-12-21) | 2022-11-25 | 2022-11-25 | 0.267 (x0.33) | 269 | 24,701.6 | 52,555.4 | 27,854 | ['dead share 0.712 >= 0.2', 'setup rate 0.329 x real < 0.333'] |
| 5minute | session_13 | 1026 | 305 (0.297) | 0.308 | 305 (2024-09-10) | 2024-08-23 | 2024-08-26 | 0.593 (x0.73) | 601 | 23,956.5 | 35,582.4 | 11,626 | ['dead share 0.297 >= 0.2'] |
| 5minute | session_16 | 1026 | 674 (0.657) | 0.522 | 535 (2023-10-05) | 2023-10-03 | 2023-10-03 | 0.279 (x0.34) | 280 | 18,630.0 | 32,423.0 | 13,793 | ['dead share 0.657 >= 0.2'] |
| 5minute | session_17 | 1026 | 343 (0.334) | 0.047 | 343 (2022-04-27) | 2025-10-21 | 2025-10-21 | 0.605 (x0.75) | 614 | 21,720.5 | 22,657.2 | 937 | ['dead share 0.334 >= 0.2'] |
| 5minute | session_18 | 1026 | 932 (0.908) | 0.909 | 932 (2022-02-17) | 2022-02-15 | 2022-02-15 | 0.077 (x0.10) | 78 | 16,205.3 | 35,770.3 | 19,565 | ['dead share 0.908 >= 0.2', 'setup rate 0.095 x real < 0.333'] |
| 5minute | session_20 | 1026 | 213 (0.208) | 0.006 | 121 (2023-02-22) | 2025-12-22 | 2025-12-22 | 0.656 (x0.81) | 665 | 24,124.5 | 24,854.7 | 730 | ['dead share 0.208 >= 0.2'] |
| 5minute | session_22 | 1026 | 631 (0.615) | 0.615 | 631 (2023-05-18) | 2023-05-17 | 2023-05-17 | 0.372 (x0.46) | 376 | 19,971.1 | 35,326.2 | 15,355 | ['dead share 0.615 >= 0.2'] |
| 5minute | session_27 | 1026 | 348 (0.339) | 0.016 | 348 (2022-06-06) | 2025-12-08 | 2025-12-08 | 0.591 (x0.73) | 600 | 29,019.0 | 31,800.3 | 2,781 | ['dead share 0.339 >= 0.2'] |
| 5minute | session_28 | 1026 | 222 (0.216) | 0.002 | 142 (2024-10-18) | 2025-12-29 | 2025-12-29 | 0.714 (x0.88) | 719 | 18,048.5 | 18,367.6 | 319 | ['dead share 0.216 >= 0.2'] |
| 5minute | session_31 | 1026 | 544 (0.530) | 0.001 | 451 (2023-03-10) | 2025-12-30 | 2025-12-30 | 0.444 (x0.55) | 452 | 29,350.7 | 29,700.8 | 350 | ['dead share 0.530 >= 0.2'] |
| 5minute | session_36 | 1026 | 889 (0.867) | 0.007 | 889 (2022-01-20) | 2025-12-19 | 2025-12-19 | 0.183 (x0.23) | 186 | 28,931.7 | 30,099.9 | 1,168 | ['dead share 0.866 >= 0.2', 'setup rate 0.226 x real < 0.333'] |
| minute | segment_3 | 247 | 168 (0.680) | 0.004 | 168 (2025-03-11) | 2025-12-30 | 2025-12-30 | 1.761 (x0.40) | 430 | 19,540.0 | 19,767.2 | 227 | ['dead share 0.680 >= 0.2'] |
| minute | segment_9 | 247 | 92 (0.372) | 0.372 | 92 (2025-08-19) | 2025-08-18 | 2025-08-18 | 3.271 (x0.75) | 800 | 19,072.7 | 25,411.9 | 6,339 | ['dead share 0.372 >= 0.2'] |
| minute | session_3 | 247 | 99 (0.401) | 0.583 | 99 (2025-08-07) | 2025-06-04 | 2025-06-06 | 2.000 (x0.46) | 485 | 16,809.7 | 19,938.5 | 3,129 | ['dead share 0.401 >= 0.2'] |
| minute | session_8 | 247 | 76 (0.308) | 0.312 | 76 (2025-09-11) | 2025-09-09 | 2025-09-09 | 3.130 (x0.71) | 762 | 18,967.8 | 21,806.9 | 2,839 | ['dead share 0.308 >= 0.2'] |

32 of 122 tapes built are locked (22 of 84 in the first build); the refuters' tail rule (share of sessions after the last CHoCH >= 0.2, or SETUP rate < 1/3 x real) flags 17 of them, the frozen-run rule adds the recovered mid-tape lock-outs (dead tail share ~0 with a dead run of hundreds of sessions). The session bootstrap locks most often: a whole real session's open-to-close return with an independent gap draw makes the chained level walk farthest. The generator-level poor-null flag (median SETUP rate) cannot see a dead tape; the per-tape flag can, and the certificate excludes them.

## 6. Adversarial validation IS-early vs IS-late (`drift.json`)

| tf | IS units (early / late) | design cols | time proxies removed in B | AUC A (all as-of) | AUC B (no time proxies) | permuted AUC p50 / p95 (B) |
|---|---|---|---|---|---|---|
| 5minute | 826 (412 / 414) | 236 | n_events_asof (rho +1.00), sl (rho +0.93) | 0.9031 | **0.9472** | 0.4930 / 0.5255 |
| minute | 4452 (2268 / 2184) | 244 | n_events_asof (rho +1.00), sl (rho +0.94) | 0.9961 | **0.9733** | 0.4985 / 0.5239 |

- **5minute reading**: with the time proxies the periods separate at AUC 0.903; without them AUC 0.947 against a permutation p95 of 0.525: the IS-early and IS-late feature distributions are distinguishable well above chance (covariate drift inside IS is real, and a rule learned on all of IS is learned on a mixture); the ranked features below say where. Removing the calendar proxies `n_events_asof`, `sl` did not lower the separation (A - B = -0.044): their information is redundant with the level- and volatility-dependent features, and a monotone-in-time column's cut points generalise slightly worse across purged blocks.
- **minute reading**: with the time proxies the periods separate at AUC 0.996; without them AUC 0.973 against a permutation p95 of 0.524: the IS-early and IS-late feature distributions are distinguishable well above chance (covariate drift inside IS is real, and a rule learned on all of IS is learned on a mixture); the ranked features below say where. The gap A - B = +0.023 is the part of the separation carried by `n_events_asof`, `sl` alone.

### 5minute: top 20 drifted features (variant B, mean |SHAP|; direction = mean in IS-late vs IS-early; shift in pooled sd; KS between the periods)

| rank | feature | source column | mean abs SHAP | mean early | mean late | shift (sd) | KS | direction |
|---|---|---|---|---|---|---|---|---|
| 1 | `atr_bps` | `atr_bps` | 2.8038 | 12.7425 | 10.5375 | -0.508 | 0.248 | lower in IS-late |
| 2 | `atr14` | `atr14` | 2.6572 | 22.2569 | 24.7663 | 0.304 | 0.173 | higher in IS-late |
| 3 | `range_3h_pts` | `range_3h_pts` | 0.2030 | 111.5757 | 127.9047 | 0.268 | 0.162 | higher in IS-late |
| 4 | `n_rooms_alive` | `n_rooms_alive` | 0.1484 | 10.1675 | 10.2198 | 0.019 | 0.060 | higher in IS-late |
| 5 | `hv3_ratio` | `hv3_ratio` | 0.1461 | 4.1320 | 4.3403 | 0.118 | 0.183 | higher in IS-late |
| 6 | `sess_cumvol_ratio20s` | `sess_cumvol_ratio20s` | 0.1404 | 1.0485 | 1.1296 | 0.175 | 0.103 | higher in IS-late |
| 7 | `days_to_expiry` | `days_to_expiry` | 0.1358 | 13.8083 | 15.4179 | 0.180 | 0.152 | higher in IS-late |
| 8 | `sess_vol_vs_prev_sess` | `sess_vol_vs_prev_sess` | 0.1236 | 1.0516 | 1.1328 | 0.161 | 0.102 | higher in IS-late |
| 9 | `choch_bar_range_atr` | `choch_bar_range_atr` | 0.1139 | 1.3922 | 1.3575 | -0.060 | 0.058 | lower in IS-late |
| 10 | `hv2_ratio` | `hv2_ratio` | 0.1105 | 2.9497 | 3.2557 | 0.193 | 0.115 | higher in IS-late |
| 11 | `close_vs_sess_open_pts` | `close_vs_sess_open_pts` | 0.1104 | -1.9495 | -5.7426 | -0.042 | 0.076 | lower in IS-late |
| 12 | `n_bos_today` | `n_bos_today` | 0.1097 | 2.1553 | 1.8019 | -0.206 | 0.097 | lower in IS-late |
| 13 | `sl_dist_atr` | `sl_dist_atr` | 0.1075 | 1.8906 | 1.8472 | -0.054 | 0.060 | lower in IS-late |
| 14 | `room_behind_dist_atr` | `room_behind_dist_atr` | 0.1073 | 0.6776 | 0.7028 | 0.030 | 0.059 | higher in IS-late |
| 15 | `er_1h` | `er_1h` | 0.1066 | 0.3868 | 0.3743 | -0.060 | 0.051 | lower in IS-late |
| 16 | `dist_choch_lvl_atr` | `dist_choch_lvl_atr` | 0.0824 | 1.1990 | 1.1315 | -0.057 | 0.093 | lower in IS-late |
| 17 | `gap_pts` | `gap_pts` | 0.0753 | 4.6369 | 5.8181 | 0.013 | 0.071 | higher in IS-late |
| 18 | `range_1h_atr` | `range_1h_atr` | 0.0708 | 3.4444 | 3.4208 | -0.023 | 0.066 | lower in IS-late |
| 19 | `card_first_bars` | `card_first_bars` | 0.0697 | 5.4000 | 6.4496 | 0.333 | 0.105 | higher in IS-late |
| 20 | `vol_max_ratio20_5` | `vol_max_ratio20_5` | 0.0667 | 2.2561 | 2.5349 | 0.157 | 0.080 | higher in IS-late |

Top-5 source columns (a selected rule using one of these is refit without it): `atr14`, `atr_bps`, `hv3_ratio`, `n_rooms_alive`, `range_3h_pts`.

### minute: top 20 drifted features (variant B, mean |SHAP|; direction = mean in IS-late vs IS-early; shift in pooled sd; KS between the periods)

| rank | feature | source column | mean abs SHAP | mean early | mean late | shift (sd) | KS | direction |
|---|---|---|---|---|---|---|---|---|
| 1 | `atr_bps` | `atr_bps` | 3.0734 | 5.2337 | 4.2373 | -0.474 | 0.233 | lower in IS-late |
| 2 | `atr14` | `atr14` | 2.7177 | 9.1659 | 9.8903 | 0.176 | 0.118 | higher in IS-late |
| 3 | `days_to_expiry` | `days_to_expiry` | 0.2120 | 13.5066 | 15.2967 | 0.196 | 0.143 | higher in IS-late |
| 4 | `gap_pts` | `gap_pts` | 0.2053 | -2.3843 | 6.2642 | 0.097 | 0.100 | higher in IS-late |
| 5 | `sess_cumvol_ratio20s` | `sess_cumvol_ratio20s` | 0.1687 | 1.0004 | 1.0517 | 0.117 | 0.078 | higher in IS-late |
| 6 | `range_3h_pts` | `range_3h_pts` | 0.1366 | 106.5850 | 113.6839 | 0.119 | 0.070 | higher in IS-late |
| 7 | `n_rooms_alive` | `n_rooms_alive` | 0.1044 | 7.7328 | 8.0440 | 0.120 | 0.070 | higher in IS-late |
| 8 | `sess_range_atr` | `sess_range_atr` | 0.0998 | 15.3851 | 14.8538 | -0.082 | 0.074 | lower in IS-late |
| 9 | `n_bos_today` | `n_bos_today` | 0.0978 | 12.6578 | 11.6680 | -0.127 | 0.061 | lower in IS-late |
| 10 | `hv3_ratio` | `hv3_ratio` | 0.0779 | 4.8150 | 4.9747 | 0.052 | 0.058 | higher in IS-late |
| 11 | `fz_band_width` | `fz_band_width` | 0.0777 | 17.2116 | 17.2318 | 0.009 | 0.045 | higher in IS-late |
| 12 | `today_net_asof` | `today_net_asof` | 0.0760 | -6,712.8549 | -7,946.2621 | -0.185 | 0.086 | lower in IS-late |
| 13 | `pos_in_session_range` | `pos_in_session_range` | 0.0729 | 0.4822 | 0.4927 | 0.037 | 0.030 | higher in IS-late |
| 14 | `sess_vol_vs_prev_sess` | `sess_vol_vs_prev_sess` | 0.0622 | 1.0139 | 1.0520 | 0.084 | 0.072 | higher in IS-late |
| 15 | `n_choch_3h` | `n_choch_3h` | 0.0602 | 7.8959 | 8.1795 | 0.071 | 0.053 | higher in IS-late |
| 16 | `dow` | `dow` | 0.0593 | 2.0207 | 2.0348 | 0.010 | 0.014 | higher in IS-late |
| 17 | `range_1h_pts` | `range_1h_pts` | 0.0496 | 66.1874 | 69.4325 | 0.085 | 0.036 | higher in IS-late |
| 18 | `fz_band_width_atr` | `fz_band_width_atr` | 0.0492 | 2.1622 | 2.0369 | -0.147 | 0.109 | lower in IS-late |
| 19 | `card_vol_ratio` | `card_vol_ratio` | 0.0482 | 0.5547 | 0.6304 | 0.112 | 0.037 | higher in IS-late |
| 20 | `close_pos_in_bar` | `close_pos_in_bar` | 0.0476 | 0.5055 | 0.5046 | -0.003 | 0.050 | lower in IS-late |

Top-5 source columns (a selected rule using one of these is refit without it): `atr14`, `atr_bps`, `days_to_expiry`, `gap_pts`, `sess_cumvol_ratio20s`.

**Rule for the gate studies**: a selected rule that uses one of top5_sources (variant B) is refit without that feature and both versions are reported in the study's FINDINGS; a rule that uses a time proxy (time_proxies) is a calendar rule, not a market rule: tapes.rule_mask refuses it (PermissionError) and the gate studies refuse it on the real tape by the same rule (harness.NOT_FEATURES does not carry these columns: reported, not changed here); a rule that uses any feature of top20_drifted carries the feature's std_shift as a caveat

**Where the time-proxy refusal is enforced**: on the tapes, in code (`tapes.rule_mask` raises `PermissionError` for any column in `drift.json` `timeframes[tf].time_proxies`, fallback `n_events_asof`, `sl`; tested in the repair round); on the real tape it is a study rule the gate studies apply, because `harness.NOT_FEATURES` does not carry these two columns (reported to the orchestrator, not changed here: `harness.py` is outside this study's scope).

**Not run here**: IS-vs-OOS adversarial validation (runs after the single OOS evaluation, in oos_once.py's post-mortem, label-free, explanatory only).

## 7. How a candidate is evaluated on the tapes later

```python
import sys; sys.path.insert(0, '<OUT>/studies/null_tapes_drift'); import tapes
# the pass rule in one call (real_diff = the candidate's real-tape ledger row 'diff'; rules = its rule-list JSON, rules_round0.json grammar):
passed, checks, summary = tapes.null_tape_check(real_diff, '5minute', rules)      # or 'minute'
# checks = {'null_tape:real_diff>gmm_p95': (ok, p95), 'null_tape:real_diff>segment_p95': (ok, p95), 'null_tape:session_same_sign>=0.75': (ok, share)}
# summary['null_tape_diff_inr'] = {gen: {'p50', 'p95'}} is the certificate block for the key's provenance; summary['per_tape'] = every tape's metrics
# the same by hand:
for folder in tapes.tape_folders('5minute', 'gmm'):           # the CERTIFICATE set: the first 20 (5minute) / 8 (minute) HEALTHY tapes by seed index k
    r = tapes.evaluate_rule_list(folder, rules)               # (healthy=False gives every tape built, locked ones included: a sensitivity read, never the pass rule)
    r['diff'], r['control_pct'], r['kept_share']
```

**Tape set of the pass rule**: the certificate set (`tapes.tape_folders(tf, gen)` default = healthy tapes, first DESIGN_N by k; section 2b lists the k of each generator). The locked tapes are never part of a pass / fail: the engine did not run on them for 21-91% of their sessions (section 5c), so their kept-vs-skipped statistic is noise on a few hundred units. Report the sensitivity read (`healthy=False`) beside it if a reader asks how the verdict moves.

**Pass rule** (DESIGN_PANEL (c) + Judge 1): the candidate's real-tape diff (its ledger row) > p95 of its own tape diffs on the GMM-Markov certificate tapes AND on the segment certificate tapes; the session-bootstrap certificate diffs carry the real sign in >= 75% of tapes. The reference nulls in `null_distributions.json` (`gates` -> `diff_p50`, `diff_p95` per generator) are the certificate values a shipped key's provenance block carries (`null_tape_diff_inr`). A rule list is never scored on the tapes before its real-tape ledger row exists (the tapes are not a search space; `tapes.py` writes nothing to the ledger).

**Program-level gap (Judge 1's binding fix, not in code here)**: `harness.go_no_go` has no null-tape item, so a gate study can pass `go_no_go` without ever running this check; `harness.py` is outside this study's write scope. `tapes.null_tape_check` returns the three items in `go_no_go`'s `(ok, value)` shape so the fix is a drop-in for the orchestrator:

```python
# harness.py (proposed, not applied here)
def go_no_go(res, tf, cpcv=None, pbo_value=None, dsr=None, spa_p=None, boot=None, null_tape=None):
    ...
    if null_tape is not None:                      # null_tape = tapes.null_tape_check(res['diff'], tf, rules)[1]
        ch.update(null_tape)                        # 'null_tape:real_diff>gmm_p95', 'null_tape:real_diff>segment_p95', 'null_tape:session_same_sign>=0.75'
    return all(v[0] for v in ch.values()), ch
```
Until that lands, the phase-3 workflow must call `tapes.null_tape_check` explicitly before freezing a candidate and record the three items in the candidate's FINDINGS and provenance.

## 8. Caveats and what would falsify these nulls

- The tapes' price level follows a random walk of drawn sessions and gaps: over 1,026 sessions some tapes end far from the real level (see `close_last` in section 5); the engine is scale-free (checked: x2 prices give identical event counts), but INR differences scale with the level, so a high-level tape widens the null in INR. This makes the p95 conservative (harder to beat); an ATR-normalised statistic would be tighter and is not the registered one.
- The GMM-Markov tape's return kurtosis is below the real tape's (a 6-component mixture cannot carry a kurtosis of ~25) and its |r| autocorrelation dies within a few bars; Judge 1's warning (a narrower-than-reality null over-rejects) is why the segment bootstrap is read alongside it and the pass rule needs both.
- The session bootstrap keeps every within-session dependence, so it is a stability read, not a null: a gate that works within the day should keep its sign there.
- Engine lock-out (section 5c, measured): on the first build the engine's protected level froze and the CHoCH stream stopped for 21-91% of the sessions on 5minute: GMM-Markov 6/20, segment bootstrap (30-bar blocks) 4/20, session bootstrap 10/20; minute: GMM-Markov 0/8, segment bootstrap (30-bar blocks) 1/8, session bootstrap 1/8 tapes (frozen-run rule; the refuters' tail rule finds 12 of 84), while BOS continued at the normal rate; the locked tapes carry as few as 78 L1 units (5minute) against 727-1211 on the certificate tapes; 430 L1 units (minute) against 613-1650 on the certificate tapes. The certificate (section 4) excludes them and was topped up to the design count with the next seeds; the first-build numbers with and without them are in section 4a (verdicts unchanged). The lock-out is itself a property of a memory-free tape (the real market returns to its anchored levels; a random walk need not), so the healthy set is conditioned on 'the engine ran', not on any gate statistic.
- `sl` (the stop price level) is in `Table.asof_columns()` although it is a raw price (|rho| 0.93 with time on 5 minutes); `n_events_asof` is a cumulative count since the data start (rho 1.0). Both are time proxies, excluded in variant B; `tapes.rule_mask` refuses them (PermissionError) and the gate studies refuse them on the real tape by rule; the harness allow-list should carry them in NOT_FEATURES (reported, not changed here).
- The 1-minute tapes are one trading year (247 IS sessions) with 8 tapes per generator: their null percentiles rest on 8 values and are wider than the 5-minute ones; the 5-minute nulls are the primary certificate, as both judges asked.
- The two mechanical reference gates are fixed reference points, not registered candidates (section 1); nothing in the ledger or the registrations depends on them.
- Falsification: if a real gate's diff sat above the GMM/segment p95 while the gate is known to be pure engine mechanics (e.g. the stop-distance gate on the real tape), the null would be too narrow; section 4 shows what the mechanical gates read on the real tape against their own nulls.
- Drift inside IS is large (section 6) and its top of the ranking is the volatility / price-level regime (5minute: `atr_bps` (lower, -0.51 sd), `atr14` (higher, +0.30 sd), `range_3h_pts` (higher, +0.27 sd), `n_rooms_alive` (higher, +0.02 sd), `hv3_ratio` (higher, +0.12 sd); minute: `atr_bps` (lower, -0.47 sd), `atr14` (higher, +0.18 sd), `days_to_expiry` (higher, +0.20 sd), `gap_pts` (higher, +0.10 sd), `sess_cumvol_ratio20s` (higher, +0.12 sd)): the tape went from ~17,500 to ~26,300 while volatility in bps fell, so every point-denominated column (`*_pts`, `atr14`, `sl_dist_pts`, `fz_band_width`, `fz_dist_band_edge_*`, `gap_pts`) drifts with the level. A rule on such a column is a level rule; the gate studies should express thresholds in the `_atr` / `_bps` forms and the CPCV path distribution, not the pooled IS number, is what a drifting IS supports.

## 9. Null result statement

This study searches no gate and proposes no candidate (`candidates: []`, `null_result: true` in the sense of 'no candidate'): it writes the certificate the gate studies compare against. The three reference gates' readings against their own nulls are in section 4b.

## 10. Files

- `FINDINGS.md`
- `drift.json`
- `drift.log`
- `drift.py`
- `drift_5minute.json`
- `drift_5minute_features.csv`
- `drift_cache_5minute_A_all_asof.json`
- `drift_cache_5minute_B_without_time_proxies.json`
- `drift_cache_minute_A_all_asof.json`
- `drift_cache_minute_B_without_time_proxies.json`
- `drift_minute.json`
- `drift_minute_features.csv`
- `drift_run.log`
- `drift_run2.log`
- `drift_run3_5minute.log`
- `drift_run3_minute.log`
- `drift_run_minute.log`
- `drift_smoke.log`
- `engine_scale_check.json`
- `engine_scale_check.log`
- `engine_scale_check.py`
- `findings.json`
- `fit_5minute.json`
- `fit_minute.json`
- `gen_tapes.py`
- `null_distributions.json`
- `real_health_5minute.json`
- `real_health_minute.json`
- `real_reference_5minute.json`
- `real_reference_minute.json`
- `reality.jsonl`
- `reality_check.csv`
- `run_5minute.log`
- `run_minute.log`
- `run_tapes.py`
- `tape_health.csv`
- `tape_results.csv`
- `tape_results.jsonl`
- `tapes.py`
- `topup_5minute.log`
- `topup_minute.log`
- `write_findings.py`
- `write_findings_resume.log`
- `tapes/<tf>/<gen>_<k>/` (per tape: `tape_meta.json`, `build.log`, `meta.json`, `tape_health.json`, `features.parquet`, `trades.parquet`, `sessions.parquet`, `bars.parquet`, `events.parquet`, `setups.parquet`, ...; `tape.csv` kept for k = 0 only, every tape reproduces from its seed)

## 11. Repair round (adversarial refuters' findings and what changed)

**1. Engine lock-out on part of the tapes undisclosed; the 'up to 3x' caveat mis-stated a 15.5x unit spread; the generator-level poor-null flag cannot see a dead tape; the certificate p95 moved when the locked tapes were excluded.**

- `tapes.tape_health(folder)` (per-tape flag: dead share of sessions inside frozen-prot CHoCH-free runs longer than the real tape's longest (5minute 68, minute 69 sessions) < 0.2 and SETUP rate >= 1/3 x real; written to `tapes/<tf>/<gen>_<k>/tape_health.json`; `tape_health.csv` at the study level; `real_health_<tf>.json`). It flags 32 of 122 tapes built (22 of the first build's 84); the refuters' tail rule is a special case (12 tapes) that misses the recovered mid-tape lock-outs.
- `tapes.tape_folders(tf, gen, healthy=True, n=DESIGN_N)` (default = the certificate set; `healthy=False` = every tape built; `original_only=True` = the first build); numeric ordering by k.
- `run_tapes.aggregate` publishes three sets per gate: `gates` (certificate), `gates_all_original`, `gates_healthy_original`, plus `locked_tapes`, `lockout_rate_*`, `units_per_tape`, `poor_null_tapes`, `reality_certificate`; `tape_results.csv` / `reality_check.csv` carry the health columns.
- `run_tapes.py --target-healthy N` topped the certificate up to the design count with the next seeds (k >= DESIGN_N, generated in seed order; the generator refit reproduces the first build's GMM: 5minute True, minute True); logs `topup_5minute.log`, `topup_minute.log`. Nothing of the first build was rebuilt or removed.
- FINDINGS: section 1 (definitions of health and the tape sets), 2b (counts), 4 (certificate) + 4a (first build with / without the locked tapes, delta p95, verdict flips), 5 (lock-out rates, certificate rates), 5c (the mechanism and the per-tape list), 7 (which tape set the pass rule uses), 8 (the caveat replaced by the measured lock-out).
- Reproduction of the refuters' recomputation (tail rule, first build): 5minute/gmm/frozen_st7_st8: all 191.66 / 708.82, tail-rule healthy 191.66 / 560.81 (n 16); 5minute/session/choch2_skip: all 127.18 / 700.52, tail-rule healthy 52.24 / 713.3 (n 15); minute/session/frozen_st7_st8: all 76.99 / 468.29, tail-rule healthy 52.46 / 226.14 (n 7).

**2. The time-proxy refusal was a written policy, not a property of `tapes.rule_mask` (a rule on `sl` or `n_events_asof` was accepted).**

- `tapes.time_proxies(tf)` reads `drift.json` (`timeframes[tf].time_proxies`; fallback `n_events_asof`, `sl`); `tapes.rule_mask` raises `PermissionError` for such a column. Tested: `[['sl', '>', 20000]]` and `[['n_events_asof', '>', 100]]` are refused on tape gmm_0; label columns and `fz_traded` were already refused.
- FINDINGS sections 6 and 8 now say where the refusal is enforced (in code on the tapes; by study rule on the real tape, since `harness.NOT_FEATURES` does not carry the two columns: reported, not changed); `drift.json` -> `rule_for_gate_studies` carries the same sentence (its numbers are untouched; `drift_<tf>.json` are the raw per-timeframe outputs).

**3. The two mechanical gates were called 'pre-registered' although no registration exists outside the study folder.**

- Reworded everywhere in the study (`tapes.MECHANICAL_GATES`, `run_tapes.py`, FINDINGS sections 1, 8): 'fixed in tapes.py before any tape was scored; reference points, not candidates'. The three `real_ref` ledger rows keep the earlier wording in their config text (the ledger is append-only); no ledger consequence: they are comparators, not candidates.

**4. Judge 1's binding fix (the null-tape pass rule as a `go_no_go` item) is not in `harness.go_no_go`; a gate study can pass `go_no_go` without running the tape check.**

- Program-level (outside this study's write scope): `tapes.null_tape_check(real_diff, tf, rules)` implements the section-7 rule on the certificate set and returns the three items in `go_no_go`'s `(ok, value)` shape; section 7 gives the drop-in patch for `harness.go_no_go(..., null_tape=...)` and tells the phase-3 workflow to call the check explicitly until it lands. Flagged for the orchestrator in findings.json (`program_level_gaps`).

