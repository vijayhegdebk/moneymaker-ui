# Extended as-of features (`fz_v3/out/features_ext/<tf>/ext_features.parquet`)

Built by `studies/ext_features/build_ext.py` (kernels in `ext_lib.py`), verified by `finalize.py` on the truncated tape, documented by `write_docs.py`.
One row per Foundation SETUP of `data/<tf>/features.parquet`, keyed by `setup_i` (join on it; the label and the split come from the base table through `harness.load`).
These columns are candidate features for the importance study (DESIGN_PANEL: quant-ml-canon-feature-importance, both judges) and nowhere else: no gate was searched here, no label was read.

Rows: minute 5326 SETUPs (5266 L1 units), 5minute 1012 SETUPs (1002 L1 units). Columns: 61 per timeframe (identical names on both).

## Conventions

- **as-of**: every value at SETUP bar `k` is a function of bars `<= k` (the SETUP bar included) and, for the fitted families, of a model frozen on the fit window.
- **fit window** = the IS bars of sessions 2021-10-01 .. 2023-09-30, the first IS half (489 sessions; 182,557 bars on 1m, 36,514 on 5m). Every z-scoring statistic, mixture, HMM, jump-model centroid and lambda, BOCPD standardisation and the FFD d* is estimated there and nowhere else: unsupervised, label-free; the second IS half and OOS never enter a fit. Inference is a forward pass over the whole tape from bar 0 with the frozen model. For bars inside the fit window the frozen statistics are, by construction, in-sample (a label-free in-sample effect, stated here; the truncation check below cannot see it because the cut is after the fit window).
- **gap-free log return**: `log(close_t / close_{t-1})`, except at a session's first bar where it is `log(close_t / open_t)`, so the overnight gap never enters a return-based statistic (the base README's window convention). FFD and BSADF work on the log close level itself and therefore see the gap as a level step (causal, stated).
- **same-session window**: cut at the session's first bar `s0 = k - session_bar`.
- **state relabelling**: for every GMM / HMM / jump model the states are ordered by ascending mean `(high-low)/atr14` so that state 0 is the quietest; the tables below give the means in original units.
- **truncation check**: the same builder ran on `data/<tf>/trunc_20250630_120000/` (bars up to 2025-06-30 12:00, same fit window) and every column was compared for every SETUP before the cut at tolerance 1e-9 (NaN pattern included); a differing column is dropped. Result below.

## Columns

| column | definition | causal argument | fit-window statement |
|---|---|---|---|
| `ffd_close_dstar` | fixed-width fractionally differentiated log close at d* (weights w_0 = 1, w_j = -w_{j-1}(d-j+1)/j, cut at |w| < 1e-4; the window length is reported below) | x_k = sum_j w_j log close_{k-j}: bars <= k only; direct convolution so the value does not depend on the tape length | fit window: IS bars of sessions 2021-10-01..2023-09-30 chooses d* by ADF (constant + 2 lags, statsmodels adfuller, 5% MacKinnon): the smallest d on the 0.1..1.0 grid whose ADF statistic passes; the ADF over all IS bars is reported next to it |
| `ffd_close_dstar_z60` | ffd_close_dstar minus its 60-bar rolling mean, over the 60-bar rolling std (ddof 1), bars k-59..k | rolling window ends at k | same d* |
| `ffd_vol_dstar` | the same FFD on log(max(volume, 1)) | as above | fit window: IS bars of sessions 2021-10-01..2023-09-30 chooses d* by the same ADF rule |
| `ffd_vol_dstar_z60` | 60-bar rolling z of ffd_vol_dstar | as above | same d* |
| `bsadf_close` | backward SADF (Phillips, Shi & Yu 2015): max over start bars s in [k-W+1, k-m+1] of the ADF t-statistic (constant, y_{t-1}, 2 lags of dy) of log close over bars s..k; W = 375 / 75 bars, m = 60 / 15 (1m / 5m); the window is demeaned by its first value (the intercept absorbs it) | every regression uses bars s..k <= k; the backward window may cross the previous session (bars, not time) | no fit: a deterministic function of bars <= k |
| `bsadf_close_win` | the window length (bars) at which bsadf_close attains its maximum | as above | no fit: a deterministic function of bars <= k |
| `cusum_events_60` | symmetric CUSUM filter (AFML 2.5.2.1) on gap-free log returns with the per-bar threshold h_t = atr14_t / close_t (S+ = max(0, S+ + r), S- = min(0, S- + r); an event when S+ > h or S- < -h, then both reset): events in bars (k-60, k] | the filter runs forward over the tape; the count reads events at bars <= k | no fit: a deterministic function of bars <= k |
| `cusum_bars_since` | bars since the last CUSUM event (0 when the SETUP bar is one; NaN before the first event of the tape) | as above | no fit: a deterministic function of bars <= k |
| `csw_max_abs` | Chu-Stinchcombe-White (AFML 17.4.1) on the session's log-close levels: max over n in [s0, k-1] of |S_{n,k}|, S_{n,k} = (y_k - y_n) / (sigma_k sqrt(k-n)), sigma_k^2 = mean squared level change over the session's bars s0+1..k; NaN when the SETUP is in the session's first two bars | n < k and sigma from bars <= k of the same session | no fit: a deterministic function of bars <= k |
| `csw_max_exceed` | max over n of |S_{n,k}| - c_{n,k}, c = sqrt(4.6 + log(k-n)) (b_0.05 = 4.6); > 0 = the session's level has moved beyond the 5% band from some earlier bar | as above | no fit: a deterministic function of bars <= k |
| `csw_sign_dir` | sign(y_k - y_n) at the argmax of |S| - c, times dir_sign (+1 = the session's strongest move so far is in the SETUP's direction) | as above; dir_sign is the SETUP's own as-of column | no fit: a deterministic function of bars <= k |
| `bocpd_{ret,rng}_h{60,240}_map` | Bayesian online change-point detection (Adams & MacKay 2007) with a normal-inverse-gamma prior (Student-t predictive) on the standardised series (ret = gap-free log return; rng = log(max(high-low, 0.05))), constant hazard 1/60 or 1/240, run length truncated at 400 (mass beyond 400 folded into the last bin): the MAP run length at k | the run-length posterior at k conditions on observations <= k only (a forward recursion) | fit window: IS bars of sessions 2021-10-01..2023-09-30 gives the standardisation mean / std of each series (the prior is mu0 = 0, kappa0 = 1, alpha0 = 1, beta0 = 1 in standardised units); label-free |
| `bocpd_{ret,rng}_h{60,240}_p10` | P(run length < 10 | observations <= k) | as above | as above |
| `bocpd_{ret,rng}_h{60,240}_since_reset` | bars since the last bar at which the MAP run length fell (a declared change point); NaN before the first | as above | as above |
| `rv_absret` | |gap-free log return| of bar k (state-model input 1) | bar k | none for the raw value |
| `rv_range_atr` | (high - low) / atr14 at k (input 2) | bar k | none |
| `rv_body_frac` | |close - open| / (high - low) at k, 0 when high = low (input 3) | bar k | none |
| `rv_logvol_rel20` | log(max(volume_k, 1) / max(median volume of bars k-20..k-1, 1)) (input 4; the previous 20 tape bars, crossing the session break) | bars k-20..k | none |
| `rv_ev36` | BOS + CHoCH events at bars in [max(k-35, s0), k] (input 5; same-session window) | events are stamped at their bar i <= k | none |
| `(rv_choch_since_bos)` | input 6 = CHoCH events after the last BOS at k; equals the base column n_choch_since_bos on every SETUP (checked) and is therefore not written again | as the base column | none |
| `rv_range36_atr` | (max high - min low over [max(k-35, s0), k]) / atr14_k (input 7) | same-session window ending at k | none |
| `rv_ret36_atr` | (close_k - close_{k-36}) / atr14_k, the session's open replacing close_{k-36} when k-36 is before the session (input 8) | as above | none |
| `gmm{3,4}_p{j}` | sklearn GaussianMixture(K, full covariance, 3 inits, seed 0) posterior P(component j | x_k) over the 8 z-scored inputs; components relabelled by ascending mean (high-low)/atr14 (state 0 = quietest) | a per-bar map of x_k | fit window: IS bars of sessions 2021-10-01..2023-09-30 for the z-scoring statistics and the mixture parameters; frozen; NaN inputs (first 20 tape bars' volume) are set to the fit mean |
| `gmm{3,4}_map` | argmax_j of the GMM posterior | as above | as above |
| `hmm{3,4}_p{j}` | hmmlearn GaussianHMM(K, diagonal covariance, seed 0, <= 200 EM iterations) FORWARD-filtered posterior P(s_k = j | x_{<= k}) (own numba filter from the fitted start / transition / emission parameters, validated against hmmlearn on a 600-bar prefix; the smoothed posterior is never computed); states relabelled as the GMM's | the forward recursion over the whole tape from bar 0 with the frozen model reads x_{<= k} only | fit window: IS bars of sessions 2021-10-01..2023-09-30 for the z-scoring and the EM fit as one sequence; frozen |
| `hmm{3,4}_map` | argmax_j of the filtered posterior at k | as above | as above |
| `hmm{3,4}_map_run` | consecutive bars ending at k with the same filtered MAP state (>= 1) | as above | as above |
| `jump{3,4}_state` | statistical jump model (Bemporad et al. 2018; Nystrup et al. 2020): centroids C fitted on the fit window by alternating the Viterbi DP of sum ||x_t - c_{s_t}||^2 + lambda 1[s_t != s_{t-1}] with centroid updates (k-means init, seed 0); lambda from {1,2,...,128} by the BIC-like criterion n p log(SSE/(n p)) + (K p + jumps) log(n p) on the fit window; at inference the ONLINE PREFIX state argmin_s V_k(s), V_k(s) = min_u (V_{k-1}(u) + lambda 1[s != u]) + ||x_k - c_s||^2; states relabelled as the GMM's | the prefix DP at k reads x_{<= k} only (the offline Viterbi path is used for fitting on the fit window and never as a feature) | fit window: IS bars of sessions 2021-10-01..2023-09-30 for z-scoring, centroids and lambda; frozen |
| `jump{3,4}_run` | consecutive bars ending at k with the same online state | as above | as above |
| `nn_dist_prefix_{short,long}` | causal novelty (matrix-profile discord applied online): the minimum of the z-normalised Euclidean distance profile (stumpy.mass) of the m-bar close window close_{k-m+1..k} against every m-bar subsequence of close_{0..k-m-1} (the tape strictly before k-m); m = 30 / 60 (1m), 12 / 24 (5m) for short / long; NaN when the prefix holds no m-bar subsequence or the window is constant | the query ends at k, the library ends at k-m-1: no bar after k enters and the query never matches itself | no fit: a deterministic function of bars <= k |
| `p1_dist_prefix_{short,long}` | the 1st percentile of the same distance profile | as above | no fit: a deterministic function of bars <= k |
| `win_sign_agree10` | bars among k-9..k whose gap-free log return has the SETUP's sign (0..10) | bars <= k | no fit: a deterministic function of bars <= k |
| `win_dd_extreme_atr` | for an up SETUP (max high over the same-session window [max(k-L+1, s0), k] - close_k) / atr14_k; for a down SETUP (close_k - min low) / atr14_k; L = 60 / 12 bars (1m / 5m) | same-session window ending at k | no fit: a deterministic function of bars <= k |
| `win_range_slope` | OLS slope of (high-low)/atr14_k against the bar index over the same window (ATR per bar; NaN with fewer than 3 bars) | as above | no fit: a deterministic function of bars <= k |

## Coverage (share of SETUPs with a value)

| column | minute | 5minute |
|---|---|---|
| `ffd_close_dstar` | 0.997 | 0.9911 |
| `ffd_close_dstar_z60` | 0.997 | 0.9911 |
| `ffd_vol_dstar` | 0.997 | 0.9911 |
| `ffd_vol_dstar_z60` | 0.997 | 0.9911 |
| `bsadf_close` | 0.9994 | 0.999 |
| `bsadf_close_win` | 0.9994 | 0.999 |
| `cusum_events_60` | 1.0 | 1.0 |
| `cusum_bars_since` | 1.0 | 1.0 |
| `csw_max_abs` | 0.9812 | 0.9427 |
| `csw_max_exceed` | 0.9812 | 0.9427 |
| `csw_sign_dir` | 0.9812 | 0.9427 |
| `bocpd_ret_h60_map` | 1.0 | 1.0 |
| `bocpd_ret_h60_p10` | 1.0 | 1.0 |
| `bocpd_ret_h60_since_reset` | 0.9992 | 0.9951 |
| `bocpd_ret_h240_map` | 1.0 | 1.0 |
| `bocpd_ret_h240_p10` | 1.0 | 1.0 |
| `bocpd_ret_h240_since_reset` | 0.9992 | 0.9951 |
| `bocpd_rng_h60_map` | 1.0 | 1.0 |
| `bocpd_rng_h60_p10` | 1.0 | 1.0 |
| `bocpd_rng_h60_since_reset` | 0.9998 | 0.998 |
| `bocpd_rng_h240_map` | 1.0 | 1.0 |
| `bocpd_rng_h240_p10` | 1.0 | 1.0 |
| `bocpd_rng_h240_since_reset` | 0.9998 | 0.998 |
| `rv_absret` | 1.0 | 1.0 |
| `rv_range_atr` | 1.0 | 1.0 |
| `rv_body_frac` | 1.0 | 1.0 |
| `rv_logvol_rel20` | 0.9998 | 0.999 |
| `rv_ev36` | 1.0 | 1.0 |
| `rv_range36_atr` | 1.0 | 1.0 |
| `rv_ret36_atr` | 1.0 | 1.0 |
| `gmm3_p0` | 1.0 | 1.0 |
| `gmm3_p1` | 1.0 | 1.0 |
| `gmm3_p2` | 1.0 | 1.0 |
| `gmm3_map` | 1.0 | 1.0 |
| `gmm4_p0` | 1.0 | 1.0 |
| `gmm4_p1` | 1.0 | 1.0 |
| `gmm4_p2` | 1.0 | 1.0 |
| `gmm4_p3` | 1.0 | 1.0 |
| `gmm4_map` | 1.0 | 1.0 |
| `hmm3_p0` | 1.0 | 1.0 |
| `hmm3_p1` | 1.0 | 1.0 |
| `hmm3_p2` | 1.0 | 1.0 |
| `hmm3_map` | 1.0 | 1.0 |
| `hmm3_map_run` | 1.0 | 1.0 |
| `hmm4_p0` | 1.0 | 1.0 |
| `hmm4_p1` | 1.0 | 1.0 |
| `hmm4_p2` | 1.0 | 1.0 |
| `hmm4_p3` | 1.0 | 1.0 |
| `hmm4_map` | 1.0 | 1.0 |
| `hmm4_map_run` | 1.0 | 1.0 |
| `jump3_state` | 1.0 | 1.0 |
| `jump3_run` | 1.0 | 1.0 |
| `jump4_state` | 1.0 | 1.0 |
| `jump4_run` | 1.0 | 1.0 |
| `nn_dist_prefix_short` | 0.9994 | 0.999 |
| `p1_dist_prefix_short` | 0.9994 | 0.999 |
| `nn_dist_prefix_long` | 0.9989 | 0.997 |
| `p1_dist_prefix_long` | 0.9989 | 0.997 |
| `win_sign_agree10` | 1.0 | 1.0 |
| `win_dd_extreme_atr` | 1.0 | 1.0 |
| `win_range_slope` | 0.9812 | 0.9427 |

## FFD: the ADF table and d*

ADF with constant and 2 lags (statsmodels `adfuller(maxlag=2, autolag=None, regression='c')`), 5% MacKinnon critical value. d* (used) = the smallest d passing on the fit window; the same rule over all IS bars is shown for comparison. The two disagree by one grid step for log close on both timeframes (the fit window passes at 0.2, all IS bars at 0.3); the fit-window value is used so that the truncated rebuild reproduces the column exactly, and the disagreement is recorded as a caveat.

**minute, log close**: d*(fit) = 0.2, d*(all IS) = 0.3, used = 0.2, weight window = 497 bars.

| d | window (bars) | ADF fit | n fit | pass fit | ADF all IS | n IS | pass IS | 5% crit |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 503 | -2.756 | 182052 | False | -1.213 | 382571 | False | -2.862 |
| 0.2 | 497 | -5.347 | 182058 | True | -2.538 | 382577 | False | -2.862 |
| 0.3 | 388 | -9.625 | 182167 | True | -4.687 | 382686 | True | -2.862 |
| 0.4 | 282 | -16.526 | 182273 | True | -8.153 | 382792 | True | -2.862 |
| 0.5 | 200 | -27.403 | 182355 | True | -13.695 | 382874 | True | -2.862 |
| 0.6 | 140 | -44.234 | 182415 | True | -22.548 | 382934 | True | -2.862 |
| 0.7 | 97 | -70.176 | 182458 | True | -37.147 | 382977 | True | -2.862 |
| 0.8 | 64 | -108.708 | 182491 | True | -62.085 | 383010 | True | -2.862 |
| 0.9 | 38 | -166.019 | 182517 | True | -113.887 | 383036 | True | -2.862 |
| 1.0 | 2 | -246.175 | 182553 | True | -358.613 | 383072 | True | -2.862 |

**minute, log vol**: d*(fit) = 0.1, d*(all IS) = 0.1, used = 0.1, weight window = 503 bars.

| d | window (bars) | ADF fit | n fit | pass fit | ADF all IS | n IS | pass IS | 5% crit |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 503 | -127.384 | 182052 | True | -185.053 | 382571 | True | -2.862 |
| 0.2 | 497 | -166.781 | 182058 | True | -240.937 | 382577 | True | -2.862 |
| 0.3 | 388 | -202.557 | 182167 | True | -292.526 | 382686 | True | -2.862 |
| 0.4 | 282 | -233.571 | 182273 | True | -337.816 | 382792 | True | -2.862 |
| 0.5 | 200 | -261.472 | 182355 | True | -378.813 | 382874 | True | -2.862 |
| 0.6 | 140 | -286.096 | 182415 | True | -415.137 | 382934 | True | -2.862 |
| 0.7 | 97 | -307.994 | 182458 | True | -447.483 | 382977 | True | -2.862 |
| 0.8 | 64 | -327.728 | 182491 | True | -476.709 | 383010 | True | -2.862 |
| 0.9 | 38 | -345.824 | 182517 | True | -503.554 | 383036 | True | -2.862 |
| 1.0 | 2 | -362.616 | 182553 | True | -528.493 | 383072 | True | -2.862 |

**5minute, log close**: d*(fit) = 0.2, d*(all IS) = 0.3, used = 0.2, weight window = 497 bars.

| d | window (bars) | ADF fit | n fit | pass fit | ADF all IS | n IS | pass IS | 5% crit |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 503 | -2.771 | 36009 | False | -1.203 | 76116 | False | -2.862 |
| 0.2 | 497 | -5.246 | 36015 | True | -2.543 | 76122 | False | -2.862 |
| 0.3 | 388 | -9.232 | 36124 | True | -4.686 | 76231 | True | -2.862 |
| 0.4 | 282 | -15.438 | 36230 | True | -8.134 | 76337 | True | -2.862 |
| 0.5 | 200 | -24.61 | 36312 | True | -13.547 | 76419 | True | -2.862 |
| 0.6 | 140 | -37.346 | 36372 | True | -22.033 | 76479 | True | -2.862 |
| 0.7 | 97 | -53.77 | 36415 | True | -35.477 | 76522 | True | -2.862 |
| 0.8 | 64 | -72.519 | 36448 | True | -56.633 | 76555 | True | -2.862 |
| 0.9 | 38 | -91.868 | 36474 | True | -92.176 | 76581 | True | -2.862 |
| 1.0 | 2 | -109.518 | 36510 | True | -157.319 | 76617 | True | -2.862 |

**5minute, log vol**: d*(fit) = 0.1, d*(all IS) = 0.1, used = 0.1, weight window = 503 bars.

| d | window (bars) | ADF fit | n fit | pass fit | ADF all IS | n IS | pass IS | 5% crit |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 503 | -55.194 | 36009 | True | -81.329 | 76116 | True | -2.862 |
| 0.2 | 497 | -69.062 | 36015 | True | -100.612 | 76122 | True | -2.862 |
| 0.3 | 388 | -81.528 | 36124 | True | -118.457 | 76231 | True | -2.862 |
| 0.4 | 282 | -92.913 | 36230 | True | -135.141 | 76337 | True | -2.862 |
| 0.5 | 200 | -103.952 | 36312 | True | -151.372 | 76419 | True | -2.862 |
| 0.6 | 140 | -114.596 | 36372 | True | -167.014 | 76479 | True | -2.862 |
| 0.7 | 97 | -124.837 | 36415 | True | -181.956 | 76522 | True | -2.862 |
| 0.8 | 64 | -134.467 | 36448 | True | -195.972 | 76555 | True | -2.862 |
| 0.9 | 38 | -143.612 | 36474 | True | -209.194 | 76581 | True | -2.862 |
| 1.0 | 2 | -152.304 | 36510 | True | -221.691 | 76617 | True | -2.862 |

## BOCPD standardisation and reset rates

| tf | series | fit mean | fit std | MAP resets / session (h = 1/60) | MAP resets / session (h = 1/240) |
|---|---|---|---|---|---|
| minute | ret | -1.45557e-07 | 0.000369868 | 17.22 | 9.79 |
| minute | rng | 1.98481 | 0.546534 | 20.24 | 14.21 |
| 5minute | ret | -7.27734e-07 | 0.000812737 | 3.88 | 2.38 |
| 5minute | rng | 2.84807 | 0.530716 | 4.38 | 3.21 |

CUSUM filter: minute: 115478 events, 97.2 per session; 5minute: 21092 events, 17.75 per session (with h = atr14/close the filter fires every few bars: it is a volatility clock, as Judge 1 predicted; kept as specified).

## State models: means per state (original units)

Inputs: `absret`, `range_atr`, `body_frac`, `logvol_rel20`, `ev36`, `choch_since_bos`, `range36_atr`, `ret36_atr`. Fit-window mean / std used for z-scoring:

| tf | input | mean | std |
|---|---|---|---|
| minute | absret | 0.00025647 | 0.00026651 |
| minute | range_atr | 0.96745 | 0.40503 |
| minute | body_frac | 0.48708 | 0.27995 |
| minute | logvol_rel20 | 0.038509 | 0.66898 |
| minute | ev36 | 3.166 | 1.6291 |
| minute | choch_since_bos | 0.29111 | 0.87873 |
| minute | range36_atr | 6.1995 | 1.7774 |
| minute | ret36_atr | 0.17617 | 3.7439 |
| 5minute | absret | 0.00056301 | 0.00058614 |
| 5minute | range_atr | 0.96276 | 0.41288 |
| 5minute | body_frac | 0.45641 | 0.26336 |
| 5minute | logvol_rel20 | 0.02779 | 0.67684 |
| 5minute | ev36 | 2.5504 | 1.6893 |
| 5minute | choch_since_bos | 0.22331 | 0.67537 |
| 5minute | range36_atr | 5.5818 | 1.9755 |
| 5minute | ret36_atr | 0.12961 | 3.5608 |

### minute, HMM K = 3 (converged True after 71 EM iterations; filter check: max |diff| of the last-bar posterior vs hmmlearn 8.36e-14, log-likelihood diff 2.05e-11)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.8825 | 0.4539 | -0.0487 | 4.028 | 1.975 | 5.722 | -0.1306 | 0.1301 | 0.1327 | 7.9 |
| 1 | 0.0002 | 0.9465 | 0.4833 | 0.0207 | 3.028 | -0 | 6.269 | 0.2435 | 0.8419 | 0.8368 | 46.0 |
| 2 | 0.001 | 1.908 | 0.7356 | 0.9041 | 3.201 | 0.9528 | 6.376 | -0.3366 | 0.028 | 0.0306 | 1.5 |

Transition matrix (rows from, columns to):

| from \ to | 0 | 1 | 2 |
|---|---|---|---|
| 0 | 0.8741 | 0.0638 | 0.0621 |
| 1 | 0.0064 | 0.9783 | 0.0153 |
| 2 | 0.3701 | 0.3181 | 0.3118 |

### minute, GMM K = 3 (weights [0.1344, 0.8354, 0.0302])

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.9027 | 0.46 | -0.0267 | 4.062 | 1.985 | 5.704 | -0.2014 | 0.1325 |
| 1 | 0.0002 | 0.948 | 0.4829 | 0.0237 | 3.032 | 0 | 6.265 | 0.2419 | 0.8426 |
| 2 | 0.001 | 1.794 | 0.7233 | 0.7388 | 2.872 | 0.8053 | 6.594 | 0.0392 | 0.0249 |

### minute, jump model K = 3 (lambda* = 16)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.9531 | 0.4828 | 0.0181 | 3.169 | 0.1113 | 5.924 | 1.785 | 0.7138 |
| 1 | 0.0003 | 0.9706 | 0.4853 | 0.079 | 4.547 | 3.185 | 5.461 | -0.1895 | 0.0509 |
| 2 | 0.0003 | 1.006 | 0.4992 | 0.0851 | 2.836 | 0.1116 | 7.128 | -4.154 | 0.2353 |

| lambda | jumps (fit window) | SSE | BIC-like | state share |
|---|---|---|---|---|
| 1 | 42032 | 1110811.8 | 197288.9 | [0.7467, 0.0655, 0.1878] |
| 2 | 27830 | 1131386.2 | 22505.0 | [0.8108, 0.0663, 0.1229] |
| 4 | 15112 | 1167439.7 | -112203.9 | [0.8708, 0.0665, 0.0627] |
| 8 | 3517 | 1212133.3 | -221918.7 | [0.6591, 0.0646, 0.2762] |
| 16 | 2733 | 1221170.7 | -222198.5 | [0.69, 0.0585, 0.2515] |
| 32 | 1882 | 1241061.7 | -210680.9 | [0.7792, 0.0496, 0.1712] |
| 64 | 1010 | 1280631.5 | -177220.3 | [0.8798, 0.0383, 0.0818] |
| 128 | 418 | 1320839.1 | -140475.0 | [0.818, 0.0186, 0.1633] |

### minute, HMM K = 4 (converged True after 59 EM iterations; filter check: max |diff| of the last-bar posterior vs hmmlearn 0.00e+00, log-likelihood diff 9.55e-12)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.866 | 0.4333 | -0.0746 | 2.93 | -0 | 5.759 | -0.4458 | 0.6349 | 0.5931 | 7.0 |
| 1 | 0.0002 | 0.8918 | 0.4681 | 0.0308 | 3.55 | -0 | 8.539 | 6.038 | 0.0918 | 0.1124 | 12.6 |
| 2 | 0.0003 | 0.9737 | 0.4877 | 0.0486 | 3.964 | 1.915 | 5.785 | -0.1443 | 0.1469 | 0.152 | 15.5 |
| 3 | 0.0006 | 1.442 | 0.7254 | 0.5046 | 2.995 | 0 | 6.628 | -1.517 | 0.1264 | 0.1425 | 1.7 |

Transition matrix (rows from, columns to):

| from \ to | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | 0.8567 | 0.0027 | 0.0126 | 0.1279 |
| 1 | 0.0219 | 0.9208 | 0.0059 | 0.0514 |
| 2 | 0.0333 | 0.0043 | 0.9356 | 0.0268 |
| 3 | 0.5434 | 0.0465 | 0.0116 | 0.3985 |

### minute, GMM K = 4 (weights [0.4801, 0.1333, 0.3582, 0.0284])

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0002 | 0.8989 | 0.46 | -0.0203 | 3.138 | -0 | 6.174 | 2.563 | 0.5223 |
| 1 | 0.0002 | 0.9001 | 0.459 | -0.0293 | 4.066 | 1.985 | 5.695 | -0.2224 | 0.132 |
| 2 | 0.0003 | 1.023 | 0.5163 | 0.0891 | 2.886 | -0 | 6.369 | -2.929 | 0.3225 |
| 3 | 0.0009 | 1.744 | 0.7078 | 0.7123 | 2.943 | 0.9331 | 6.856 | 0.8682 | 0.0231 |

### minute, jump model K = 4 (lambda* = 32)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0003 | 0.9459 | 0.491 | 0.0577 | 3.52 | 0.0811 | 8.33 | 5.553 | 0.1251 |
| 1 | 0.0002 | 0.9618 | 0.4829 | 0.0199 | 3.013 | 0.1428 | 5.433 | 0.2022 | 0.6958 |
| 2 | 0.0002 | 0.9713 | 0.4833 | 0.0892 | 4.625 | 3.383 | 5.461 | -0.0931 | 0.0394 |
| 3 | 0.0003 | 1.011 | 0.5029 | 0.0858 | 3.026 | 0.123 | 7.822 | -4.916 | 0.1397 |

| lambda | jumps (fit window) | SSE | BIC-like | state share |
|---|---|---|---|---|
| 1 | 37532 | 1004197.9 | -13834.7 | [0.0646, 0.5819, 0.1452, 0.2083] |
| 2 | 26242 | 1020528.5 | -150528.4 | [0.065, 0.6158, 0.0998, 0.2194] |
| 4 | 15817 | 1050153.6 | -256711.5 | [0.0653, 0.6478, 0.0556, 0.2313] |
| 8 | 8584 | 1090692.2 | -304062.2 | [0.0636, 0.6824, 0.024, 0.23] |
| 16 | 4759 | 1132786.5 | -303050.7 | [0.0596, 0.7239, 0.009, 0.2074] |
| 32 | 2949 | 1141915.7 | -317019.6 | [0.0494, 0.6604, 0.1494, 0.1408] |
| 64 | 1610 | 1202558.6 | -260455.6 | [0.0387, 0.7966, 0.0859, 0.0788] |
| 128 | 654 | 1272817.0 | -191099.0 | [0.0186, 0.7654, 0.1849, 0.031] |

### 5minute, HMM K = 3 (converged True after 51 EM iterations; filter check: max |diff| of the last-bar posterior vs hmmlearn 2.03e-13, log-likelihood diff 1.41e-11)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8442 | 0.4032 | -0.0966 | 2.961 | 1.689 | 5.32 | -0.3381 | 0.1253 | 0.114 | 6.1 |
| 1 | 0.0005 | 0.9355 | 0.452 | 0.0052 | 2.498 | -0 | 5.653 | 0.2184 | 0.8398 | 0.8496 | 38.3 |
| 2 | 0.0021 | 1.971 | 0.7267 | 0.9451 | 2.476 | 0.8472 | 4.73 | -0.4804 | 0.0349 | 0.0363 | 1.3 |

Transition matrix (rows from, columns to):

| from \ to | 0 | 1 | 2 |
|---|---|---|---|
| 0 | 0.8356 | 0.0713 | 0.0931 |
| 1 | 0.0047 | 0.9739 | 0.0214 |
| 2 | 0.4061 | 0.3864 | 0.2076 |

### 5minute, GMM K = 3 (weights [0.1062, 0.8482, 0.0456])

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8379 | 0.3865 | -0.1007 | 3.002 | 1.697 | 5.361 | -0.3624 | 0.1205 |
| 1 | 0.0005 | 0.9366 | 0.4523 | 0.0078 | 2.504 | 0 | 5.657 | 0.2168 | 0.8417 |
| 2 | 0.0019 | 1.742 | 0.6954 | 0.6988 | 2.369 | 0.9436 | 4.701 | -0.3462 | 0.0378 |

### 5minute, jump model K = 3 (lambda* = 32)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.9217 | 0.4533 | 0.01 | 3.583 | 0.0853 | 7.823 | 5.327 | 0.1368 |
| 1 | 0.0006 | 0.9568 | 0.4452 | 0.06 | 3.128 | 2.748 | 5.125 | -0.6213 | 0.0527 |
| 2 | 0.0006 | 0.9703 | 0.4576 | 0.0291 | 2.337 | 0.1064 | 5.215 | -0.7382 | 0.8105 |

| lambda | jumps (fit window) | SSE | BIC-like | state share |
|---|---|---|---|---|
| 1 | 8297 | 217214.3 | 18179.9 | [0.4809, 0.3558, 0.1633] |
| 2 | 6089 | 220397.8 | -5357.4 | [0.4992, 0.378, 0.1228] |
| 4 | 3706 | 227077.9 | -26625.1 | [0.5283, 0.4022, 0.0695] |
| 8 | 2155 | 235740.5 | -35208.0 | [0.5464, 0.4136, 0.04] |
| 16 | 972 | 248526.1 | -34667.7 | [0.7145, 0.2738, 0.0116] |
| 32 | 438 | 244159.8 | -46565.7 | [0.8124, 0.1422, 0.0454] |
| 64 | 224 | 257990.7 | -33163.2 | [0.8866, 0.0353, 0.0781] |
| 128 | 71 | 271470.9 | -20211.0 | [0.951, 0.0207, 0.0284] |

### 5minute, HMM K = 4 (converged True after 91 EM iterations; filter check: max |diff| of the last-bar posterior vs hmmlearn 3.06e-14, log-likelihood diff 2.73e-12)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | stationary | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8323 | 0.3906 | -0.1223 | 2.175 | 0 | 4.706 | 0.078 | 0.505 | 0.4777 | 5.4 |
| 1 | 0.0004 | 0.8908 | 0.4405 | -0.0221 | 3.254 | -0 | 7.952 | 0.8312 | 0.2197 | 0.2427 | 11.2 |
| 2 | 0.0006 | 0.9645 | 0.4512 | 0.0332 | 2.954 | 1.657 | 5.246 | -0.3269 | 0.1442 | 0.1351 | 14.1 |
| 3 | 0.0014 | 1.513 | 0.7055 | 0.6025 | 2.234 | -0 | 4.808 | -0.4523 | 0.1311 | 0.1445 | 1.5 |

Transition matrix (rows from, columns to):

| from \ to | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | 0.8151 | 0.0088 | 0.0123 | 0.1637 |
| 1 | 0.0122 | 0.9108 | 0.008 | 0.069 |
| 2 | 0.0268 | 0.014 | 0.9289 | 0.0304 |
| 3 | 0.5657 | 0.1075 | 0.0124 | 0.3144 |

### 5minute, GMM K = 4 (weights [0.4611, 0.1064, 0.3959, 0.0367])

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0003 | 0.8346 | 0.396 | -0.0882 | 2.625 | -0 | 5.569 | 2.263 | 0.492 |
| 1 | 0.0004 | 0.8529 | 0.4009 | -0.0935 | 3.026 | 1.699 | 5.14 | -0.7201 | 0.1204 |
| 2 | 0.0008 | 1.083 | 0.5231 | 0.1427 | 2.339 | -0 | 5.685 | -2.221 | 0.3565 |
| 3 | 0.0017 | 1.59 | 0.6566 | 0.5975 | 2.51 | 1.162 | 5.914 | 1.141 | 0.0311 |

### 5minute, jump model K = 4 (lambda* = 16)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0005 | 0.9346 | 0.4526 | 0.0425 | 3.753 | 0.0954 | 7.314 | 4.541 | 0.1826 |
| 1 | 0.0006 | 0.9582 | 0.4513 | 0.0026 | 1.825 | 0.0845 | 4.497 | 0.0818 | 0.5776 |
| 2 | 0.0006 | 0.9582 | 0.4481 | 0.0667 | 3.142 | 2.67 | 5.104 | -0.5804 | 0.058 |
| 3 | 0.0007 | 1.007 | 0.4773 | 0.0744 | 3.22 | 0.107 | 7.011 | -4.17 | 0.1818 |

| lambda | jumps (fit window) | SSE | BIC-like | state share |
|---|---|---|---|---|
| 1 | 8300 | 193801.4 | -14997.1 | [0.2313, 0.5533, 0.1646, 0.0507] |
| 2 | 6073 | 196994.5 | -38250.1 | [0.2355, 0.592, 0.1216, 0.0509] |
| 4 | 3729 | 203664.2 | -58022.7 | [0.241, 0.639, 0.0686, 0.0514] |
| 8 | 2111 | 212806.3 | -65558.5 | [0.2183, 0.6951, 0.0344, 0.0522] |
| 16 | 997 | 219507.8 | -70521.0 | [0.2021, 0.5541, 0.1927, 0.0512] |
| 32 | 667 | 227108.8 | -64730.1 | [0.1473, 0.6707, 0.1359, 0.0461] |
| 64 | 360 | 240545.2 | -51803.4 | [0.0773, 0.8134, 0.0748, 0.0344] |
| 128 | 106 | 261671.2 | -30409.8 | [0.0441, 0.4907, 0.444, 0.0212] |

## Truncation check

**minute**: cut trunc_20250630_120000, 335934 bars kept, SETUPs before the cut [3807, 3807], identical keys True; columns dropped: none; PASS = True; max |diff| over all columns = 0; fitted quantities agree: True.

**5minute**: cut trunc_20250630_120000, 67192 bars kept, SETUPs before the cut [718, 718], identical keys True; columns dropped: none; PASS = True; max |diff| over all columns = 0; fitted quantities agree: True.

## Run times (seconds)

| tf | ffd | bsadf | cusum | csw | bocpd | regime vector | gmm | hmm | jump | novelty | window | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minute | 6.5 | 2.7 | 0.0 | 0.0 | 33.4 | 0.8 | 22.4 | 40.3 | 13.0 | 238.2 | 0.0 | 358.6 |
| 5minute | 1.9 | 0.1 | 0.0 | 0.0 | 7.2 | 0.2 | 3.8 | 8.8 | 2.1 | 13.8 | 0.8 | 39.6 |

## What is deliberately not here

- No hindsight proxy (hour-bin range / ATR, |net move| / range): those are labels (deep-sequence-vision-labels, Judge 1's fix), not features.
- No regime gate, no tau grid, no BSADF percentile flag: features only (both judges on regime-breaks and regime-states).
- No motif, cluster or shapelet search; no ROCKET transform: only the causal novelty scalars and the three window summaries the judges kept.
- No smoothed HMM posterior, no offline Viterbi path as a feature.
- The ATR-normalised BSADF variant of the regime-breaks design was not built (the task fixed BSADF on log close).
