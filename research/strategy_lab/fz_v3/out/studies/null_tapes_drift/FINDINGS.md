# null_tapes_drift: synthetic null tapes (c) and adversarial drift validation (d)

DESIGN_PANEL decision-making-3, parts (c) and (d), with both judges' fixes: (a) / (b) live in `harness.py`; the null tapes run on 5 minutes (20 full-length tapes per generator) and on 1 minute (8 one-year tapes per generator, RSS checked); the segment bootstrap is Judge 1's second null; the IS-vs-OOS adversarial check is not run here (oos_once.py post-mortem). No gate search, no OOS row read. Tape numbers never enter the ledger; the three reference gates on the real tape are ledger rows of family `null_tapes_drift/real_ref`. Scripts: `gen_tapes.py`, `tapes.py`, `run_tapes.py`, `drift.py`, `write_findings.py`; logs `run_5minute.log`, `run_minute.log`, `drift.log`.

## 1. Definitions (fixed before the numbers)

- **Unit / label / statistic** as the harness: a Foundation SETUP taken under the L1 (15:25) book; kept-vs-skipped difference of mean net (INR per unit); the session-matched random control percentile (`fz_report.random_control`, 2,000 draws); permutation p; block sign count. On a tape the statistic is computed by `harness.metrics` on a `harness.Table` built from the tape's own `features.parquet` / `trades.parquet` / `sessions.parquet` (`tapes.load_tape`, a copy of `harness.load` pointed at the tape folder). Every tape row is IS (the tapes carry IS calendar dates).
- **Three reference gates** (all as keep masks): `frozen_st7_st8` = keep where `fz_traded` (the frozen ST7/ST8 gate as it traded on that tape); `choch2_skip` = skip where `n_choch_since_bos >= 2` (pre-registered mechanical gate 1); `sl_above_median_skip` = skip where `sl_dist_atr` > the tape's own IS median (pre-registered mechanical gate 2). The two mechanical gates are the engine-mechanics check: a gate on stop distance or CHoCH counts can read non-zero on a memory-free tape through the engine itself (Judge 2), so its null is not 0.
- **Generators** (fitted on IS bars only, `gen_tapes.py` docstring): *session bootstrap* (whole IS sessions with replacement, level chained through the drawn session's open-to-close path and a gap drawn from the IS gap distribution); *segment bootstrap* (30-bar clock-aligned blocks from random IS sessions, re-based and chained, same gap draw); *GMM-Markov* (GaussianMixture 4-6 full-covariance components by BIC on the z-scored per-bar vector (log return, log volume ratio to the clock median, range/atr14, close position), first-order Markov chain on the labels, per-session sampling with the clock volume profile, OHLC rebuilt consistently, samples clipped to the IS range per dimension). Full-length sessions only (375 / 75 bars); the real IS tape's short sessions are excluded from the pools (listed in `fit_<tf>.json`). Tapes are written in the near-month CSV format and pushed through `build/build.py --path` (engine.run with the Foundation rules, fz.run with the frozen ST7/ST8 block, L0 and L1 pricing, the same 261-column feature table).
- **Null distribution** = per timeframe, generator and gate: p5 / p50 / p95 / mean / min / max of the tape diffs, the share of tapes with diff > 0, p50 / p95 of the control percentile, the real-tape value and its percentile among the tapes. **Pre-registered comparison** (DESIGN_PANEL (c), Judge 1's go/no-go): the real-tape difference must be above the null-tape 95th percentile; here that is read on the two memory-free nulls (GMM-Markov and segment), with the session bootstrap as the stability read (share of tapes with the real diff's sign).
- **Reality check** per generator: within-session per-bar log-return std (bps) and excess kurtosis, autocorrelation of |r| at lags 1-5 (pairs inside a session), CHoCH / BOS / SETUP / L1-unit counts per session, the raw L1 book, the frozen gate's kept share, the final price level and median ATR14; a generator whose median SETUP rate is outside [1/3, 3] x the real rate is flagged a poor null.
- **Adversarial validation (d)**: HistGradientBoostingClassifier IS-early (2021-10-01..2023-09-30) vs IS-late (2023-10-01..2025-12-31) on `harness.design(T)` of the real tape, IS rows; pooled out-of-fold AUC under `harness.purged_splits` (12 blocks, purge by exit bar, 3-session embargo); chance = 20 label permutations; variant A = all as-of columns, variant B = without time proxies (|Spearman rho| >= 0.9 with `session_idx`); SHAP (TreeExplainer) ranking on B with the direction of drift.

## 2. Generator fits (IS bars only)

| tf | IS sessions (full / short excluded) | IS bars | gaps | gap log-std | GMM K (BIC 4/5/6) | GMM fit rows | tapes x sessions |
|---|---|---|---|---|---|---|---|
| 5minute | 1026 (1016 / 10) | 76,621 | 1025 | 0.00488 | 6 (681,123, 675,927, 668,815) | 76,200 | 20 x 1026 |
| minute | 1026 (1012 / 14) | 383,076 | 1025 | 0.00488 | 6 (3,520,657, 2,912,397, 2,895,928) | 379,500 | 8 x 247 |

### 2a. build.py cost per tape (from each tape's `meta.json`; the box was shared with other studies, load 12-20)

| tf | generator | tapes | bars per tape | SETUPs p50 [min, max] | build seconds p50 [min, max] | peak RSS MB p50 [max] |
|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | 20 | 76,950 | 1005 [171, 1220] | 70 [54, 99] | 429 [453] |
| 5minute | segment bootstrap (30-bar blocks) | 20 | 76,950 | 904 [193, 1107] | 76 [62, 88] | 437 [451] |
| 5minute | session bootstrap | 20 | 76,950 | 756 [79, 1049] | 78 [53, 94] | 431 [445] |
| minute | GMM-Markov | 8 | 92,625 | 1460 [1261, 1676] | 88 [68, 98] | 483 [516] |
| minute | segment bootstrap (30-bar blocks) | 8 | 92,625 | 1134 [435, 1332] | 58 [42, 68] | 473 [519] |
| minute | session bootstrap | 8 | 92,625 | 1042 [494, 1457] | 76 [61, 91] | 475 [499] |

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

## 4. Null distributions (the certificate: `null_distributions.json`)

Diff = kept-vs-skipped mean L1 net on the tape (INR per unit). `real pct` = the real-tape diff's percentile among the tapes; `pass` = real diff > tape p95.

| tf | generator | gate | tapes | units p50 | kept share p50 | diff p5 | diff p50 | diff p95 | diff min / max | share diff>0 | control pct p50 / p95 | share ctrl>=95 | real diff | real pct | real > p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5minute | GMM-Markov | choch2_skip | 20 | 988 | 0.690 | -385.35 | 91.75 | **516.38** | -430.00 / 554.66 | 0.600 | 22.1 / 56.1 | 0.000 | 257.83 | 80.0 | no |
| 5minute | GMM-Markov | frozen_st7_st8 | 20 | 988 | 0.310 | -236.46 | 191.66 | **708.82** | -325.98 / 1,325.57 | 0.750 | 96.8 / 100.0 | 0.550 | -365.62 | 0.0 | no |
| 5minute | GMM-Markov | sl_above_median_skip | 20 | 988 | 0.500 | -262.72 | 97.75 | **483.41** | -903.77 / 642.33 | 0.700 | 94.4 / 100.0 | 0.500 | 33.65 | 40.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | choch2_skip | 20 | 894 | 0.680 | -230.95 | 35.06 | **441.96** | -267.98 / 579.55 | 0.550 | 5.9 / 36.6 | 0.000 | 257.83 | 80.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 20 | 894 | 0.360 | -244.33 | 164.72 | **566.42** | -317.41 / 642.26 | 0.650 | 93.8 / 99.8 | 0.500 | -365.62 | 0.0 | no |
| 5minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 20 | 894 | 0.500 | -721.53 | -212.74 | **620.74** | -833.01 / 860.19 | 0.400 | 97.9 / 99.8 | 0.750 | 33.65 | 65.0 | no |
| 5minute | session bootstrap | choch2_skip | 20 | 748 | 0.680 | -831.33 | 127.18 | **700.52** | -987.68 / 810.86 | 0.700 | 6.6 / 59.6 | 0.000 | 257.83 | 65.0 | no |
| 5minute | session bootstrap | frozen_st7_st8 | 20 | 748 | 0.380 | -401.58 | 85.92 | **420.40** | -425.86 / 662.10 | 0.650 | 82.7 / 98.9 | 0.250 | -365.62 | 10.0 | no |
| 5minute | session bootstrap | sl_above_median_skip | 20 | 748 | 0.500 | -957.84 | -331.03 | **131.37** | -1,136.17 / 137.76 | 0.100 | 80.2 / 99.0 | 0.250 | 33.65 | 90.0 | no |
| minute | GMM-Markov | choch2_skip | 8 | 1,436 | 0.670 | -1.13 | 105.34 | **246.98** | -4.22 / 286.72 | 0.875 | 61.5 / 89.2 | 0.000 | -72.50 | 0.0 | no |
| minute | GMM-Markov | frozen_st7_st8 | 8 | 1,436 | 0.150 | -251.78 | -93.89 | **23.00** | -299.94 / 37.28 | 0.125 | 42.8 / 83.8 | 0.000 | -19.71 | 75.0 | no |
| minute | GMM-Markov | sl_above_median_skip | 8 | 1,436 | 0.500 | -112.96 | 32.02 | **96.58** | -139.38 / 110.02 | 0.625 | 71.0 / 93.7 | 0.125 | 12.07 | 37.5 | no |
| minute | segment bootstrap (30-bar blocks) | choch2_skip | 8 | 1,126 | 0.650 | -381.90 | -61.29 | **144.79** | -483.88 / 176.70 | 0.375 | 7.8 / 36.1 | 0.000 | -72.50 | 50.0 | no |
| minute | segment bootstrap (30-bar blocks) | frozen_st7_st8 | 8 | 1,126 | 0.160 | -229.97 | 16.51 | **272.51** | -268.70 / 295.83 | 0.500 | 56.0 / 95.4 | 0.125 | -19.71 | 37.5 | no |
| minute | segment bootstrap (30-bar blocks) | sl_above_median_skip | 8 | 1,126 | 0.500 | -135.58 | 37.22 | **129.55** | -139.96 / 136.91 | 0.500 | 68.5 / 92.6 | 0.125 | 12.07 | 50.0 | no |
| minute | session bootstrap | choch2_skip | 8 | 1,032 | 0.660 | -297.26 | -78.84 | **136.47** | -315.34 / 222.48 | 0.125 | 8.3 / 35.8 | 0.000 | -72.50 | 62.5 | no |
| minute | session bootstrap | frozen_st7_st8 | 8 | 1,032 | 0.160 | -144.32 | 76.99 | **468.29** | -147.04 / 595.08 | 0.750 | 69.2 / 90.7 | 0.000 | -19.71 | 25.0 | no |
| minute | session bootstrap | sl_above_median_skip | 8 | 1,032 | 0.500 | -188.18 | -22.91 | **94.14** | -256.58 / 116.35 | 0.375 | 82.1 / 94.8 | 0.125 | 12.07 | 62.5 | no |

### 4a. Reading of the reference gates against their own nulls

- **5minute / frozen_st7_st8**: real diff -365.62 (control pct 12.4); gmm: p50 191.66, p95 708.82, real pct 0.0, same sign 0.25; segment: p50 164.72, p95 566.42, real pct 0.0, same sign 0.35; session: p50 85.92, p95 420.40, real pct 10.0, same sign 0.35 -> does NOT pass the null-tape check.
- **5minute / choch2_skip**: real diff 257.83 (control pct 46.6); gmm: p50 91.75, p95 516.38, real pct 80.0, same sign 0.60; segment: p50 35.06, p95 441.96, real pct 80.0, same sign 0.55; session: p50 127.18, p95 700.52, real pct 65.0, same sign 0.70 -> does NOT pass the null-tape check.
- **5minute / sl_above_median_skip**: real diff 33.65 (control pct 99.8); gmm: p50 97.75, p95 483.41, real pct 40.0, same sign 0.70; segment: p50 -212.74, p95 620.74, real pct 65.0, same sign 0.40; session: p50 -331.03, p95 131.37, real pct 90.0, same sign 0.10 -> does NOT pass the null-tape check.
- **minute / frozen_st7_st8**: real diff -19.71 (control pct 64.0); gmm: p50 -93.89, p95 23.00, real pct 75.0, same sign 0.88; segment: p50 16.51, p95 272.51, real pct 37.5, same sign 0.50; session: p50 76.99, p95 468.29, real pct 25.0, same sign 0.25 -> does NOT pass the null-tape check.
- **minute / choch2_skip**: real diff -72.50 (control pct 1.6); gmm: p50 105.34, p95 246.98, real pct 0.0, same sign 0.12; segment: p50 -61.29, p95 144.79, real pct 50.0, same sign 0.62; session: p50 -78.84, p95 136.47, real pct 62.5, same sign 0.88 -> does NOT pass the null-tape check.
- **minute / sl_above_median_skip**: real diff 12.07 (control pct 99.0); gmm: p50 32.02, p95 96.58, real pct 37.5, same sign 0.62; segment: p50 37.22, p95 129.55, real pct 50.0, same sign 0.50; session: p50 -22.91, p95 94.14, real pct 62.5, same sign 0.38 -> does NOT pass the null-tape check.

### 4b. Key readings (numbers from `null_distributions.json`)

1. **The frozen ST7/ST8 gate reads positive on memory-free 5-minute tapes**: GMM-Markov median diff 191.66 (p95 708.82, share of tapes > 0 0.75, control pct p50 96.8, 55% of tapes at or above the 95th control percentile); segment median 164.72 (p95 566.42, control pct p50 93.8); session median 85.92. On tapes with no swing memory the rooms gate still separates kept from skipped by ~+150-200 INR and clears the random control on half the tapes: that part of any ST7/ST8-shaped statistic is engine / FZ mechanics, not market memory. The real 5-minute frozen gate (-365.62, control pct 12.4) sits at the 0th percentile of the GMM null and the 0th of the segment null: on the real tape it does worse than on its own memory-free tapes.
2. **The stop-distance gate's control percentile is mechanical**: on the real tape it reads 99.8 (5 min, diff 33.65) and 99.0 (1 min, diff 12.07); on the memory-free tapes its control percentile has p50 94.4 / 97.9 (5 min GMM / segment) and 71.0 / 68.5 (1 min), and the real diff sits at the 40th / 65th (5 min) and 38th / 50th (1 min) percentile of its null. A high control percentile for a gate on stop distance is what the engine produces on a random tape (Judge 2's warning, measured); the null p95 of the diff, not the control percentile, is the bar.
3. **The CHoCH-count gate**: 5 min real diff 257.83 (control pct 46.6) is at the 80th / 80th percentile of the GMM / segment nulls (p95 516.38 / 441.96): not above p95 on any generator. 1 min real diff -72.50 (control pct 1.6) against a GMM null median of 105.34 (0.88 of tapes positive): the real 1-minute CHoCH-count gate is worse than its memory-free null (the 0th percentile); the 'CHoCH, CHoCH, no BOS = sideways' skip does not read as market memory on this tape.
4. **Consequence for the gate studies**: a candidate's real-tape diff must clear the p95 of the null tapes of its own family shape, and its control percentile must be read against the null's control-percentile distribution (`control_pct_p95` per gate); a control percentile alone, even 99+, is not evidence for a gate that touches the stop or the event stream.

## 5. Reality check of the generators (IS part of the real tape vs the tapes; tape p50 [min, max])

### 5minute

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| ret std (bps) | 7.369 | 7.060 [6.940, 7.150] | 7.320 [7.040, 7.500] | 7.350 [7.150, 7.550] |
| ret excess kurtosis | 14.6 | 6.2 [5.8, 6.8] | 8.9 [5.3, 22.4] | 14.9 [6.0, 27.9] |
| abs-return autocorr lag 1 | 0.234 | 0.110 [0.100, 0.120] | 0.220 [0.200, 0.250] | 0.230 [0.210, 0.250] |
| lag 2 | 0.234 | 0.030 [0.020, 0.040] | 0.210 [0.170, 0.260] | 0.230 [0.190, 0.280] |
| lag 3 | 0.218 | 0.010 [-0.000, 0.020] | 0.190 [0.160, 0.230] | 0.220 [0.180, 0.260] |
| lag 4 | 0.210 | 0.000 [-0.010, 0.010] | 0.180 [0.150, 0.220] | 0.210 [0.180, 0.250] |
| lag 5 | 0.211 | 0.000 [-0.000, 0.010] | 0.170 [0.140, 0.220] | 0.210 [0.170, 0.260] |
| CHoCH / session | 1.204 | 1.610 [0.250, 1.990] (x1.34) | 1.330 [0.290, 1.650] (x1.10) | 1.110 [0.120, 1.530] (x0.92) |
| BOS / session | 5.428 | 5.650 [5.510, 5.910] (x1.04) | 5.350 [5.180, 5.610] (x0.99) | 5.450 [5.300, 5.640] (x1.00) |
| SETUPs / session | 0.811 | 0.980 [0.170, 1.190] (x1.21) | 0.880 [0.190, 1.080] (x1.09) | 0.740 [0.080, 1.020] (x0.91) |
| L1 units / session | 0.805 | 0.960 [0.170, 1.180] (x1.20) | 0.870 [0.190, 1.070] (x1.08) | 0.730 [0.080, 1.020] (x0.91) |
| L1 mean net | -757.0 | -1,088.8 [-1,315.0, -846.1] | -1,047.5 [-1,350.1, -697.6] | -802.6 [-1,132.8, -451.9] |
| L1 win rate | 0.277 | 0.250 [0.210, 0.270] | 0.250 [0.220, 0.290] | 0.270 [0.240, 0.300] |
| frozen kept share | 0.394 | 0.310 [0.270, 0.350] | 0.360 [0.330, 0.400] | 0.380 [0.310, 0.440] |
| last close | 26,300.0 | 27,374.7 [18,001.3, 43,826.4] | 27,368.6 [18,891.4, 36,606.2] | 27,200.4 [21,160.7, 52,555.4] |
| ATR14 median | 20.3 | 23.7 [20.1, 35.6] | 21.5 [17.3, 28.5] | 21.7 [17.4, 30.9] |

Poor-null flag (median SETUP rate outside [1/3, 3] x real): none.

### minute

| statistic | real | GMM-Markov | segment bootstrap (30-bar blocks) | session bootstrap |
|---|---|---|---|---|
| ret std (bps) | 3.408 | 3.300 [3.260, 3.310] | 3.460 [3.350, 3.580] | 3.310 [3.120, 3.730] |
| ret excess kurtosis | 21.7 | 5.1 [5.0, 5.5] | 30.4 [9.6, 37.9] | 7.1 [4.6, 48.6] |
| abs-return autocorr lag 1 | 0.277 | 0.070 [0.060, 0.080] | 0.280 [0.260, 0.300] | 0.250 [0.220, 0.320] |
| lag 2 | 0.246 | 0.020 [0.010, 0.020] | 0.240 [0.220, 0.250] | 0.220 [0.200, 0.290] |
| lag 3 | 0.230 | 0.000 [0.000, 0.010] | 0.220 [0.200, 0.230] | 0.200 [0.180, 0.270] |
| lag 4 | 0.225 | -0.000 [-0.010, 0.000] | 0.200 [0.190, 0.220] | 0.200 [0.180, 0.260] |
| lag 5 | 0.222 | -0.000 [-0.010, 0.000] | 0.200 [0.180, 0.220] | 0.200 [0.180, 0.260] |
| CHoCH / session | 6.617 | 10.080 [8.840, 12.180] (x1.52) | 6.910 [2.650, 8.210] (x1.04) | 6.330 [2.920, 8.860] (x0.96) |
| BOS / session | 26.7 | 30.4 [30.0, 31.0] (x1.14) | 26.4 [25.9, 26.8] (x0.99) | 26.8 [26.4, 27.4] (x1.00) |
| SETUPs / session | 4.388 | 5.910 [5.110, 6.790] (x1.35) | 4.590 [1.760, 5.390] (x1.05) | 4.220 [2.000, 5.900] (x0.96) |
| L1 units / session | 4.339 | 5.820 [5.040, 6.680] (x1.34) | 4.560 [1.740, 5.330] (x1.05) | 4.180 [1.960, 5.850] (x0.96) |
| L1 mean net | -1,009.6 | -1,003.5 [-1,084.6, -900.1] | -1,019.2 [-1,081.2, -885.4] | -945.3 [-1,075.4, -719.9] |
| L1 win rate | 0.156 | 0.160 [0.150, 0.180] | 0.150 [0.130, 0.170] | 0.150 [0.130, 0.180] |
| frozen kept share | 0.167 | 0.150 [0.150, 0.170] | 0.160 [0.150, 0.180] | 0.160 [0.140, 0.180] |
| last close | 26,300.0 | 18,431.6 [16,727.3, 20,986.6] | 18,554.0 [15,184.8, 20,575.3] | 19,557.5 [14,767.5, 23,861.8] |
| ATR14 median | 8.568 | 9.720 [9.200, 11.120] | 7.640 [6.930, 7.900] | 7.310 [6.490, 8.350] |

Poor-null flag (median SETUP rate outside [1/3, 3] x real): none.
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

Scale-free (x2 price level gives identical counts): **True**. Re-basing the real sessions with the real gaps reproduces the real counts exactly; redrawing the gaps or shuffling the sessions moves the CHoCH rate by ~+17% and removing the gaps altogether by ~+50%: the engine's event rate is a property of the multi-day path, which is exactly what a null tape randomises, so per-tape SETUP counts vary (section 5 min / max) and the null distributions carry that variance.

## 7. How a candidate is evaluated on the tapes later

```python
import sys; sys.path.insert(0, '<OUT>/studies/null_tapes_drift'); import tapes
for folder in tapes.tape_folders('5minute', 'gmm'):           # or 'segment' / 'session'; tf 'minute'
    r = tapes.evaluate_rule_list(folder, rules)               # rules = the candidate's rule-list JSON (rules_round0.json grammar)
    r['diff'], r['control_pct'], r['kept_share']              # the tape's kept-vs-skipped diff and control percentile
```

Pass rule (pre-registered, DESIGN_PANEL (c) + Judge 1): the candidate's real-tape diff (its ledger row) > p95 of its own tape diffs on the GMM-Markov tapes AND on the segment tapes; the session-bootstrap diffs carry the real sign in >= 75% of tapes. The reference nulls in `null_distributions.json` (`null_tape_diff_inr = {p50, p95}` per generator) are the certificate values a shipped key's provenance block carries. A rule list is never scored on the tapes before its real-tape ledger row exists (the tapes are not a search space; `tapes.py` writes nothing to the ledger).

## 8. Caveats and what would falsify these nulls

- The tapes' price level follows a random walk of drawn sessions and gaps: over 1,026 sessions some tapes end far from the real level (see `close_last` in section 5); the engine is scale-free (checked: x2 prices give identical event counts), but INR differences scale with the level, so a high-level tape widens the null in INR. This makes the p95 conservative (harder to beat); an ATR-normalised statistic would be tighter and is not the pre-registered one.
- The GMM-Markov tape's return kurtosis is below the real tape's (a 6-component mixture cannot carry a kurtosis of ~25) and its |r| autocorrelation dies within a few bars; Judge 1's warning (a narrower-than-reality null over-rejects) is why the segment bootstrap is read alongside it and the pass rule needs both.
- The session bootstrap keeps every within-session dependence, so it is a stability read, not a null: a gate that works within the day should keep its sign there.
- Engine event rates vary strongly from tape to tape (section 5 min / max): the engine's CHoCH count depends on the multi-day path, so per-tape unit counts differ by up to 3x.
- `sl` (the stop price level) is in `Table.asof_columns()` although it is a raw price (|rho| 0.93 with time on 5 minutes); `n_events_asof` is a cumulative count since the data start (rho 1.0). Both are time proxies, excluded in variant B, and a rule using either is refused; the harness allow-list should carry them in NOT_FEATURES (reported, not changed here).
- The 1-minute tapes are one trading year (247 IS sessions) with 8 tapes per generator: their null percentiles rest on 8 values and are wider than the 5-minute ones; the 5-minute nulls are the primary certificate, as both judges asked.
- Falsification: if a real gate's diff sat above the GMM/segment p95 while the gate is known to be pure engine mechanics (e.g. the stop-distance gate on the real tape), the null would be too narrow; section 4 shows what the mechanical gates read on the real tape against their own nulls.

## 9. Null result statement

This study searches no gate and proposes no candidate (`candidates: []`, `null_result: true` in the sense of 'no candidate'): it writes the certificate the gate studies compare against. The three reference gates' readings against their own nulls are in section 4a.

## 10. Files

- `FINDINGS.md`
- `drift.log`
- `drift.py`
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
- `real_reference_5minute.json`
- `real_reference_minute.json`
- `reality.jsonl`
- `reality_check.csv`
- `run_5minute.log`
- `run_minute.log`
- `run_tapes.py`
- `tape_results.csv`
- `tape_results.jsonl`
- `tapes.py`
- `write_findings.py`
- `tapes/<tf>/<gen>_<k>/` (per tape: `tape_meta.json`, `build.log`, `meta.json`, `features.parquet`, `trades.parquet`, `sessions.parquet`, `bars.parquet`, `events.parquet`, `setups.parquet`, ...; `tape.csv` kept for k = 0 only, every tape reproduces from its seed)
