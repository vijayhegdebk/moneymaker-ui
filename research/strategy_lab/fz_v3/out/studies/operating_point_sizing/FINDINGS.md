# operating_point_sizing: FINDINGS (the merged operating-point step + the conditional sizing step; IS only)

Generated 2026-09-29T16:52:45 by `write_findings.py` from `results_minute.json`, `results_5minute.json` (`operating_point.py`, logs `run_minute.log`, `run_5minute.log`) and `sizing_verdict.json` (`sizing_verdict.py`, `sizing_verdict.log`). Script shas {'operating_point.py': 'cbf332b71c008acf', 'sizing_verdict.py': '5f953d9cc2654a66', 'write_findings.py': 'af758426ac97e318'}. DESIGN_PANEL: quant-ml-canon-conformal-skip + decision-making-4-selective-gate-conformal-risk-control (Judge 2's merge into ONE operating-point step; both judges' caveats binding) and quant-ml-canon-bet-sizing + decision-making-5-kelly-bounded-sizing (merged; conditional on a passed gate). **IS only** (SETUP date <= 2025-12-31); label **L1**; both timeframes. Every kept-vs-skipped number below is a harness ledger row (id given); kept-only statistics (selective risk, coverage, utilities, the uncapped-brokerage mean) are computed from the same keep mask as the row and carry its id.

## 0. Result in one paragraph

**This step adds no OOS candidate and none is written.** It re-parameterises the OOF scores of the gate_family sub-family finalists (a threshold on a score another study produced is not a gate: Judge 1), and gate_family itself wrote no candidate on either timeframe, so every kept book here is a re-parameterisation of a gate that already failed `harness.go_no_go`. **minute**: 174 ledger rows (family `operating_point/*`; PBO(diff) 0.5469, SPA p 0.9245, effective trials 1.72); the best controlled row by diff is operating_point/crc {'sub': 'h5_full', 'model': 'scorecard'} with diff 249.89, control percentile 0.0, kept mean at 8 pts slippage -1,160.29, go/no-go FAIL (11 items). **5minute**: 144 rows (PBO(diff) 0.6395, SPA p 0.066, effective trials 2.16); best controlled row operating_point/conformal {'sub': 'h5_full', 'model': 'scorecard', 'alpha': 0.1} diff 481.16, control percentile 82.8, kept mean at 8 pts -1,082.94, go/no-go FAIL (7 items). The conformal winner-coverage guarantee holds on the pooled OOF at every alpha within the CV+ band (1 - 2 alpha) on both timeframes, and it costs nothing to state because the book it certifies is negative at every coverage: of the 326 kept books evaluated (both timeframes, four scored models each), 0 have a kept mean > 0 at 8 pts slippage (the harness item) and 1 at 3 pts. The session-unit CRC certificate on the last 200 active IS sessions does not transfer to the earlier IS rows (realised clipped risk before the block is 1.3-4x the certificate on every model: the exchangeability failure Judge 1 predicted, here already inside IS). The cost-aware Pareto front is presented for the user (Rule 0(c)); at w = 0 its optimum is the smallest coverage on every model because every kept book is negative. **Sizing: not run: no gate passed** (both timeframes; `sizing_verdict.json`); the design's default verdict 'lots = 1 or skip' stands.

## 1. Definitions (fixed before the numbers; `operating_point.py` docstring verbatim)

```
operating_point_sizing, step 1: the OPERATING POINT of the gate_family finalists (DESIGN_PANEL quant-ml-canon-conformal-skip
merged with decision-making-4-selective-gate-conformal-risk-control; Judge 2's merge, both judges' caveats binding). IS only.

THIS STEP ADDS NO OOS CANDIDATE. It re-parameterises the gate_family sub-family finalists' OOF scores (a threshold on a score
another study produced is not a gate: Judge 1); gate_family itself wrote NO candidate (null on both timeframes), so every kept
book here is a re-parameterisation of a gate that already failed harness.go_no_go. Every threshold evaluated for a kept-vs-skipped
number is a harness.score row (family operating_point/<sub>); the kept-vs-skipped numbers below come from those rows only.

Inputs   studies/gate_family/results/oof_<tf>.parquet: the 12-block purged OOF probability p (column `p`) of every probability
         learner of the two sub-families ((I) context: hour_bin one-hot + dir, inside the frozen vocabulary; (II) h5_full: the
         full as-of table, OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)). Scored models = the
         deployable scorecard of each sub-family (Platt-mapped integer score -> p, per fold) and the HGB classifier (the
         gradient-boosting ceiling / the (I) finalist on minute). The policy trees (pt1-3, the 5minute (I) finalist pt2) and the
         H5 rule list carry no score: they cannot be thresholded and are not here (stated in FINDINGS).
Score    s = 1 - p (nonconformity of the label 'win'). Everything is a threshold on s; keep iff s <= threshold.
Labels   L1 (harness.load(tf)); folds = harness blocks (the OOF parquet's `fold` equals T.block on every IS row, asserted).

(1) Cross-conformal, Mondrian by class (winner coverage): for fold f, calibration = the OOF scores of the TRUE WINNERS of the
    other 11 folds; q_alpha = the ceil((n_win + 1)(1 - alpha))-th smallest; the prediction set of a fold-f row contains 'win' iff
    s <= q_alpha; skip iff 'win' is not in the set. alpha in {0.05, 0.10, 0.15, 0.20, 0.30}. Reported per fold: nominal alpha vs
    empirical OOF winner coverage (count and |net|-weighted), kept share; pooled: the ledger row (controls on). CV+ caveat (Judge
    2): the calibration scores come from models that saw fold f, so the finite-sample guarantee is the weaker cross-conformal /
    CV+ form (about 1 - 2 alpha), not 1 - alpha; both are printed next to the empirical coverage.
    Time-bin taxonomy (class x bin; minute only, Judge 2): bins 09:15-10:29 / 10:30-12:59 / 13:00-15:19 by the SETUP bar's clock
    (`time`; the bins do not align with hour_bin's edges, so the taxonomy reads the clock, an identity column - a deployable
    form would need a clock key); calibration winners and q_alpha per bin.
    ACI (Gibbs & Candes 2021), winner-conditional: rows in time order; alpha_{t+1} = alpha_t + gamma (alpha - err_t) updated at
    every TRUE WINNER row (err_t = 1 when that winner was skipped), gamma in {0.005, 0.01}; the quantile at row t is the
    Mondrian quantile at level alpha_t over the OOF scores of the winners seen BEFORE t (expanding window; first ACI_BURN_IN
    winners: keep everything, counted); alpha_t clipped to [0, 1] (alpha_t <= 0 keeps everything, >= 1 skips everything).
    Its final state (alpha_T, q_T, n winners) is what oos_once would carry forward; no OOS row is read.
(2) Selective risk-coverage curve: coverage c in {0.10, 0.15, ..., 1.00}; nested: the fold-f threshold is the c-quantile of s over
    the other 11 folds' rows; selective risk = mean of min(max(-net, 0), 6000) among kept; the loser share among kept; the
    realised coverage. Every c is a ledger row (controls off: trials).
(3) Conformal Risk Control (Angelopoulos, Bates, Candes, Jordan & Lei 2022) with SESSIONS as units: calibration block = the last
    200 IS sessions with a SETUP (n stated as sessions-with-SETUPs; the OOF scores of its rows come from the purged folds, so the
    block is not disjoint in time from every score's training folds - the CV+ caveat again, stated); for coverage lambda on the
    grid the threshold is the lambda-quantile of s over the block's rows; per session r_s(lambda) = mean clipped loss of the
    session's kept units (0 when none kept: no trade, no loss); R_hat = mean over the n sessions; certificate =
    (n R_hat + B) / (n + 1), B = 6000; lambda* = the largest lambda with certificate <= alpha, alpha in {800, 1000, 1200} INR
    (the cost level); the gate s <= threshold(lambda*) on all IS is a ledger row (controls on); the realised risk on the IS rows
    before the block is reported beside the certificate. Per-bin certificates on minute only (dropped on 5m: Judge 2).
(4) Cost-aware Pareto front: for every coverage-curve row U_w = kept net - w x sum over skipped of max(net, 0), w in {0, 0.5, 1};
    winner-net retained = kept winners' net / all winners' net (the row's winner_recall_weighted); loser-net avoided = skipped
    losers' |net| / all losers' |net|; the non-dominated points are flagged; the argmax per w is printed for the user to pick
    (Rule 0(c)). Nothing is chosen here.
(5) Cost sensitivity of every kept book: kept mean at 3 / 5 / 8 pts slippage per side (the ledger row's kept_mean_slip3 /
    kept_mean / kept_mean_slip8) and with the brokerage cap of 20 INR per order replaced by uncapped 0.03% (lab.trade_charges with
    brokerage_cap = inf, slippage 5); the harness item is kept_mean_slip8 > 0.

Family: operating_point/<conformal | conformal_timebin | aci | coverage | crc | crc_timebin>; PBO (diff), SPA, effective trials,
DSR over every operating_point row of the timeframe; harness.go_no_go on the best row with null_tape = 'not run: this step adds no
candidate' (fails by design) and the model's source columns declared.
```

Constants: alphas [0.05, 0.1, 0.15, 0.2, 0.3]; ACI gammas [0.005, 0.01], burn-in 30 winners; coverage grid 0.1..1.0 step 0.05; CRC lambda grid 0.05..1.00 step 0.05, alphas [800.0, 1000.0, 1200.0] INR, calibration 200 sessions, clip B 6000.0; w grid [0.0, 0.5, 1.0]; time bins ['09:15-10:29', '10:30-12:59', '13:00-15:19']; scored models [('context', 'hgbc'), ('context', 'scorecard'), ('h5_full', 'hgbc'), ('h5_full', 'scorecard')].

## 2. Inputs: the scored models of `oof_<tf>.parquet`

| tf | sub/model | role | vocabulary | OOF AUC | p min / median / max | gate_family nested kept share | source columns |
|---|---|---|---|---|---|---|---|
| minute | context/hgbc | finalist of sub-family (I) (hgbc -> distilled tree; this is the hgbc OOF p) | inside the frozen vocabulary (context columns) | 0.5598 | 0.0088 / 0.4399 / 0.6385 | 0.8495 | 2 |
| minute | context/scorecard | the deployable scorecard of sub-family (I) | inside the frozen vocabulary (context columns) | 0.5478 | 0.0384 / 0.4478 / 0.5761 | 0.9290 | 2 |
| minute | h5_full/hgbc | gradient-boosting ceiling of sub-family (II) (reference) | outside the frozen shortlist (importance rule failed for every cluster) | 0.5813 | 0.0458 / 0.3273 / 0.8269 | 0.9400 | 183 |
| minute | h5_full/scorecard | finalist of sub-family (II) (scorecard -> distilled tree; this is the scorecard OOF p) | outside the frozen shortlist (importance rule failed for every cluster) | 0.5782 | 0.2409 / 0.4397 / 0.6537 | 0.9571 | 183 |
| 5minute | context/hgbc | probability learner of sub-family (I) (its finalist pt2 is a policy tree with no score) | inside the frozen vocabulary (context columns) | 0.5136 | 0.0858 / 0.4693 / 0.6524 | 0.9262 | 2 |
| 5minute | context/scorecard | the deployable scorecard of sub-family (I) | inside the frozen vocabulary (context columns) | 0.4810 | 0.3215 / 0.4711 / 0.6136 | 0.9831 | 2 |
| 5minute | h5_full/hgbc | gradient-boosting ceiling of sub-family (II) (reference) | outside the frozen shortlist (importance rule failed for every cluster) | 0.5036 | 0.0426 / 0.3238 / 0.8478 | 0.9564 | 160 |
| 5minute | h5_full/scorecard | finalist of sub-family (II) (scorecard -> distilled rules; this is the scorecard OOF p) | outside the frozen shortlist (importance rule failed for every cluster) | 0.5077 | 0.3964 / 0.4826 / 0.5920 | 0.9976 | 160 |

The policy trees (pt1-pt3; the 5minute sub-family (I) finalist `pt2`) and the H5 rule list carry no score (their OOF column is a boolean keep), so they cannot be thresholded and are not in this step; on 5minute the sub-family (I) probability learner is `context/hgbc`. The scorecard's p is a per-fold Platt map of an integer score: its OOF scale differs by fold and has heavy ties (visible as flat stretches of the coverage curve).

## 3. minute (L1: IS units 4452, mean -1,009.61 INR/trade, win rate 0.1559, winners 694, active sessions 578, mean cost 1,047.54; uncapped brokerage adds 895.40 per trade; winners per time bin {'09:15-10:29': 191, '10:30-12:59': 211, '13:00-15:19': 292})

### minute / context/hgbc - finalist of sub-family (I) (hgbc -> distilled tree; this is the hgbc OOF p) - inside the frozen vocabulary (context columns)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9524 | 0.9817 | 0.8955 / 1.0000 | 6 / 1 | 0.9295 | -995.29 | -1,198.31 | 203.02 | 12.46 | 0.1834 | 3.9 | 0.0748 | 0.0000 | 10 | -735.31 | -1,385.25 | -1,888.48 | 0.9200 | `3ff24927705534fa` |
| 0.1 | 0.90 | 0.80 | 0.9006 | 0.9442 | 0.8000 / 0.9524 | 5 / 0 | 0.8655 | -984.39 | -1,171.80 | 187.40 | 6.36 | 0.1129 | 11.0 | 0.1410 | 0.0429 | 11 | -724.42 | -1,374.36 | -1,879.75 | 0.9733 | `062ea0b0cf6b4be4` |
| 0.15 | 0.85 | 0.70 | 0.8530 | 0.9057 | 0.6885 / 0.9524 | 5 / 1 | 0.8196 | -989.62 | -1,100.45 | 110.83 | -69.36 | 0.2794 | 2.6 | 0.1865 | 0.0857 | 10 | -729.64 | -1,379.58 | -1,889.03 | 0.9643 | `6f3c976ed46d5b13` |
| 0.2 | 0.80 | 0.60 | 0.8098 | 0.8727 | 0.6400 / 0.8875 | 5 / 0 | 0.7576 | -972.71 | -1,124.95 | 152.25 | -35.03 | 0.0945 | 1.2 | 0.2520 | 0.1143 | 9 | -712.73 | -1,362.67 | -1,870.21 | 0.9081 | `b4f9d9e4311762ab` |
| 0.3 | 0.70 | 0.40 | 0.7075 | 0.8024 | 0.4800 / 0.8400 | 6 / 0 | 0.6399 | -932.65 | -1,146.39 | 213.74 | 44.14 | 0.0105 | 1.6 | 0.3725 | 0.1714 | 9 | -672.67 | -1,322.61 | -1,823.54 | 0.7904 | `42db16f8b647b578` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05, 0.1]; chosen **0.1**.

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 627 | 0.6843 | 396 | 67 | 0.8737 | 0.8955 | 0.9516 | 0.1307 |
| 1 | 628 | 0.6843 | 388 | 66 | 0.8711 | 0.8939 | 0.9609 | 0.1335 |
| 2 | 622 | 0.6843 | 384 | 72 | 0.8490 | 0.9028 | 0.9300 | 0.1635 |
| 3 | 619 | 0.6972 | 509 | 75 | 0.8743 | 0.9200 | 0.9590 | 0.1336 |
| 4 | 633 | 0.6843 | 390 | 61 | 0.8667 | 0.8852 | 0.9420 | 0.1368 |
| 5 | 655 | 0.6972 | 341 | 39 | 0.8739 | 0.9231 | 0.9206 | 0.1325 |
| 6 | 630 | 0.6972 | 424 | 64 | 0.8797 | 0.9375 | 0.9857 | 0.1306 |
| 7 | 652 | 0.6972 | 266 | 42 | 0.9173 | 0.9524 | 0.9970 | 0.0893 |
| 8 | 668 | 0.6972 | 170 | 26 | 0.8941 | 0.9231 | 0.9615 | 0.1111 |
| 9 | 617 | 0.6741 | 499 | 77 | 0.7735 | 0.8442 | 0.8212 | 0.2393 |
| 10 | 669 | 0.6741 | 173 | 25 | 0.8671 | 0.8000 | 0.9077 | 0.1216 |
| 11 | 614 | 0.6972 | 512 | 80 | 0.8926 | 0.9125 | 0.9630 | 0.1111 |

#### (1b) Class x time-bin taxonomy (minute only; the taxonomy reads the SETUP clock)

| alpha | CV+ 1-2a | OOF winner coverage | |net|-wtd | coverage 09:15-10:29 (min cal winners) | coverage 10:30-12:59 (min cal winners) | coverage 13:00-15:19 (min cal winners) | kept share | diff | perm p | control pct | loser recall | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.90 | 0.9467 | 0.9202 | 0.9319 (163) | 0.9479 (181) | 0.9555 (256) | 0.9441 | -379.53 | 0.0235 | 0.1 | 0.0564 | -1,420.80 | `de1059c3a09a9e91` |
| 0.1 | 0.80 | 0.9078 | 0.8940 | 0.9110 (163) | 0.9052 (181) | 0.9075 (256) | 0.8911 | -94.91 | 0.4573 | 1.4 | 0.1120 | -1,409.91 | `a2bf08aec27cd591` |
| 0.15 | 0.70 | 0.8357 | 0.8279 | 0.8586 (163) | 0.8341 (181) | 0.8219 (256) | 0.8147 | -66.91 | 0.5072 | 0.4 | 0.1892 | -1,411.97 | `04dd22679e69cd21` |
| 0.2 | 0.60 | 0.8098 | 0.8006 | 0.8115 (163) | 0.8104 (181) | 0.8082 (256) | 0.7808 | -60.82 | 0.5207 | 0.1 | 0.2246 | -1,412.90 | `537deeb705e47556` |
| 0.3 | 0.40 | 0.6974 | 0.6975 | 0.7016 (163) | 0.6919 (181) | 0.6986 (256) | 0.6954 | -147.07 | 0.0890 | 0.0 | 0.3049 | -1,444.37 | `22c2ee6ff9781179` |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 202 | 694 | 0.9481 | 0.9458 | 0.9249 | 0.0425 / 0.0900 | 0.0435 | 0.7672 | 0.2328 | 0.9133 | 245.55 | 0.0790 | 23.9 | 0.0931 | 11 | -1,378.28 | `6cdd080c65cae1f0` |
| 0.005 | 0.1 | 202 | 694 | 0.8991 | 0.8946 | 0.8671 | 0.0950 / 0.1470 | 0.0970 | 0.6972 | 0.3028 | 0.8666 | 156.54 | 0.1754 | 5.5 | 0.1394 | 9 | -1,378.69 | `2a14d9a46ac0eee8` |
| 0.005 | 0.15 | 202 | 694 | 0.8602 | 0.8539 | 0.8497 | 0.1507 / 0.2105 | 0.1855 | 0.6467 | 0.3533 | 0.8230 | 138.14 | 0.1799 | 1.4 | 0.1839 | 9 | -1,375.12 | `cb8a2c8664c73e19` |
| 0.005 | 0.2 | 202 | 694 | 0.8040 | 0.7952 | 0.7977 | 0.1800 / 0.2760 | 0.2140 | 0.6379 | 0.3621 | 0.7457 | 217.91 | 0.0220 | 5.1 | 0.2650 | 10 | -1,344.17 | `a443c3819b307978` |
| 0.005 | 0.3 | 202 | 694 | 0.6945 | 0.6807 | 0.6879 | 0.2605 / 0.3575 | 0.2810 | 0.6023 | 0.3977 | 0.6292 | 154.06 | 0.0615 | 0.6 | 0.3829 | 9 | -1,342.44 | `59bd5dcaccd87c7c` |
| 0.01 | 0.05 | 202 | 694 | 0.9481 | 0.9458 | 0.9422 | 0.0295 / 0.1100 | 0.0370 | 0.7742 | 0.2258 | 0.9160 | 210.40 | 0.1469 | 13.9 | 0.0899 | 10 | -1,381.90 | `357ba4a239f35835` |
| 0.01 | 0.1 | 202 | 694 | 0.8991 | 0.8946 | 0.8844 | 0.0750 / 0.1740 | 0.0940 | 0.6991 | 0.3009 | 0.8634 | 164.62 | 0.1629 | 6.0 | 0.1432 | 9 | -1,377.09 | `ba43f214cd81f270` |
| 0.01 | 0.15 | 202 | 694 | 0.8545 | 0.8479 | 0.8497 | 0.1340 / 0.2465 | 0.1810 | 0.6488 | 0.3512 | 0.8160 | 165.59 | 0.1099 | 4.3 | 0.1911 | 9 | -1,369.11 | `b728248d4cbd3d5c` |
| 0.01 | 0.2 | 202 | 694 | 0.8040 | 0.7952 | 0.8208 | 0.1660 / 0.2920 | 0.2280 | 0.6313 | 0.3687 | 0.7478 | 175.53 | 0.0445 | 5.6 | 0.2626 | 9 | -1,355.29 | `385fb33ca05e5372` |
| 0.01 | 0.3 | 202 | 694 | 0.6988 | 0.6852 | 0.7110 | 0.2310 / 0.4150 | 0.2920 | 0.59 | 0.4100 | 0.6321 | 149.23 | 0.0845 | 0.3 | 0.3803 | 9 | -1,344.67 | `fefaa41f6e04a3bb` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.0979 | 1,818.65 | 0.7844 | 0.2257 | 0.8774 | -330,480.70 | 1,657,525.62 | -330,480.70 | -1,159,243.51 | -1,988,006.32 | -757.98 | 278.94 | -1,147.95 | -1,648.58 | yes | `30c33f63bba85be8` |
| 0.15 | 0.1599 | 1,708.09 | 0.7992 | 0.2739 | 0.8132 | -653,319.16 | 1,554,450.34 | -653,319.16 | -1,430,544.33 | -2,207,769.50 | -917.58 | 109.54 | -1,307.55 | -1,796.55 | yes | `bafd197626a0b576` |
| 0.2 | 0.1954 | 1,667.88 | 0.7931 | 0.3201 | 0.7778 | -789,293.13 | 1,455,504.95 | -789,293.13 | -1,517,045.60 | -2,244,798.08 | -907.23 | 127.24 | -1,297.20 | -1,799.96 | yes | `f6392d196e66b31c` |
| 0.25 | 0.2594 | 1,630.61 | 0.8087 | 0.3778 | 0.7126 | -1,098,044.89 | 1,331,954.32 | -1,098,044.89 | -1,764,022.05 | -2,429,999.21 | -950.69 | 79.56 | -1,340.65 | -1,855.24 | yes | `8869aa790a35a51e` |
| 0.3 | 0.3019 | 1,605.48 | 0.8103 | 0.4196 | 0.6712 | -1,283,316.77 | 1,242,479.97 | -1,283,316.77 | -1,904,556.75 | -2,525,796.74 | -954.85 | 78.44 | -1,344.81 | -1,862.38 | yes | `646a12ca5080df44` |
| 0.35 | 0.3585 | 1,604.67 | 0.8152 | 0.4610 | 0.6104 | -1,598,010.30 | 1,153,814.11 | -1,598,010.30 | -2,174,917.35 | -2,751,824.41 | -1,001.26 | 13.01 | -1,391.22 | -1,915.22 | yes | `fdf2adee193d552a` |
| 0.4 | 0.4012 | 1,584.99 | 0.8214 | 0.4739 | 0.5698 | -1,840,190.25 | 1,126,252.66 | -1,840,190.25 | -2,403,316.58 | -2,966,442.91 | -1,030.34 | -34.62 | -1,420.31 | -1,950.66 | yes | `97f3ab4fbaa0bf5d` |
| 0.45 | 0.4501 | 1,573.55 | 0.8214 | 0.5746 | 0.5212 | -1,947,230.02 | 910,694.57 | -1,947,230.02 | -2,402,577.31 | -2,857,924.59 | -971.67 | 68.99 | -1,361.64 | -1,892.62 | yes | `714bd6e71d5122e7` |
| 0.5 | 0.4998 | 1,566.34 | 0.8234 | 0.6385 | 0.4705 | -2,146,783.27 | 773,837.24 | -2,146,783.27 | -2,533,701.89 | -2,920,620.51 | -964.85 | 89.48 | -1,354.81 | -1,880.01 | yes | `848878e043adf7db` |
| 0.55 | 0.5546 | 1,555.56 | 0.8238 | 0.7077 | 0.4167 | -2,355,382.20 | 625,691.84 | -2,355,382.20 | -2,668,228.12 | -2,981,074.04 | -953.98 | 124.88 | -1,343.95 | -1,862.10 | yes | `4337e4c411815845` |
| 0.6 | 0.5966 | 1,539.62 | 0.8234 | 0.7564 | 0.3792 | -2,500,022.09 | 521,562.15 | -2,500,022.09 | -2,760,803.17 | -3,021,584.24 | -941.27 | 169.39 | -1,331.24 | -1,839.34 | yes | `7f28caf5702675a4` |
| 0.65 | 0.6482 | 1,526.27 | 0.8288 | 0.8047 | 0.3316 | -2,712,611.50 | 418,091.51 | -2,712,611.50 | -2,921,657.25 | -3,130,703.01 | -939.92 | 198.11 | -1,329.89 | -1,831.38 | yes | `fa465c19fc5944a9` |
| 0.7 | 0.7008 | 1,520.54 | 0.8288 | 0.8604 | 0.2802 | -2,934,232.83 | 298,884.99 | -2,934,232.83 | -3,083,675.33 | -3,233,117.82 | -940.46 | 231.12 | -1,330.42 | -1,836.98 | yes | `8b90a99f864c4d1f` |
| 0.75 | 0.7576 | 1,517.10 | 0.8334 | 0.8727 | 0.2240 | -3,280,946.79 | 272,498.22 | -3,280,946.79 | -3,417,195.90 | -3,553,445.01 | -972.71 | 152.25 | -1,362.67 | -1,870.21 | yes | `276f3a9638987aec` |
| 0.8 | 0.8046 | 1,516.19 | 0.8375 | 0.8937 | 0.1767 | -3,549,887.52 | 227,622.97 | -3,549,887.52 | -3,663,699.00 | -3,777,510.49 | -991.04 | 95.04 | -1,381.00 | -1,891.48 | yes | `b5ddf262f5518d6f` |
| 0.85 | 0.8486 | 1,505.06 | 0.8383 | 0.9302 | 0.1383 | -3,726,745.63 | 149,371.25 | -3,726,745.63 | -3,801,431.26 | -3,876,116.88 | -986.43 | 153.07 | -1,376.40 | -1,882.50 | yes | `12cfa9372ea05057` |
| 0.9 | 0.9043 | 1,495.85 | 0.8383 | 0.9755 | 0.0875 | -3,966,553.60 | 52,415.18 | -3,966,553.60 | -3,992,761.19 | -4,018,968.78 | -985.23 | 254.72 | -1,375.20 | -1,879.28 | yes | `e8ec422e302ec68f` |
| 0.95 | 0.9461 | 1,495.04 | 0.8414 | 0.9872 | 0.0457 | -4,218,736.86 | 27,474.93 | -4,218,736.86 | -4,232,474.33 | -4,246,211.79 | -1,001.60 | 148.55 | -1,391.56 | -1,898.08 | yes | `7fe7dbd7385e1bd1` |
| 1.0 | 1.0000 | 1,482.62 | 0.8441 | 1.0000 | -0.0000 | -4,494,772.79 | 0.00 | -4,494,772.79 | -4,494,772.79 | -4,494,772.79 | -1,009.61 | - | - | -1,905.01 | yes | `c8b74d55b9709d55` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.1, w = 1 -> 0.1. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4074 | 0.0505 | 914.35 | 939.65 | 75 |
| 0.1 | 0.4986 | 0.1003 | 1,287.64 | 1,311.09 | 126 |
| 0.15 | 0.5208 | 0.1701 | 1,351.95 | 1,375.08 | 150 |
| 0.2 | 0.5341 | 0.2243 | 1,382.32 | 1,405.29 | 162 |
| 0.25 | 0.5363 | 0.2685 | 1,417.76 | 1,440.56 | 166 |
| 0.3 | 0.5414 | 0.3190 | 1,435.59 | 1,458.29 | 176 |
| 0.35 | 0.5435 | 0.3751 | 1,458.82 | 1,481.41 | 182 |
| 0.4 | 0.5448 | 0.4199 | 1,486.71 | 1,509.16 | 184 |
| 0.45 | 0.5469 | 0.4685 | 1,488.01 | 1,510.46 | 185 |
| 0.5 | 0.5508 | 0.5178 | 1,464.75 | 1,487.31 | 187 |
| 0.55 | 0.5537 | 0.5576 | 1,459.61 | 1,482.20 | 189 |
| 0.6 | 0.5634 | 0.6062 | 1,477.21 | 1,499.71 | 195 |
| 0.65 | 0.6025 | 0.6592 | 1,459.62 | 1,482.21 | 196 |
| 0.7 | 0.6298 | 0.7097 | 1,446.39 | 1,469.04 | 197 |
| 0.75 | 0.6417 | 0.7514 | 1,435.05 | 1,457.76 | 197 |
| 0.8 | 0.6467 | 0.8019 | 1,440.95 | 1,463.63 | 197 |
| 0.85 | 0.6843 | 0.8579 | 1,441.24 | 1,463.92 | 198 |
| 0.9 | 0.7436 | 0.9040 | 1,445.12 | 1,467.78 | 198 |
| 0.95 | 0.7672 | 0.9583 | 1,445.90 | 1,468.56 | 198 |
| 1.0 | - | 1.0000 | 1,435.99 | 1,458.70 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | - | - | - | - | - | - | - | - | - | - | no lambda with a certificate <= alpha |
| 1000.0 | 0.05 | 0.4074 | 939.65 | 2,170.28 | 0.0190 | 2,338.67 | 0.0303 | -892.91 | 0.0 | -2,265.40 | `9a570fb0ab738060` |
| 1200.0 | 0.05 | 0.4074 | 939.65 | 2,170.28 | 0.0190 | 2,338.67 | 0.0303 | -892.91 | 0.0 | -2,265.40 | `51a814548e959587` |

Per-bin certificates (minute only):

| alpha (INR) | lambda* 09:15-10:29 | lambda* 10:30-12:59 | lambda* 13:00-15:19 | realised risk before the block | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.1 (cert 695.58; n 159, slack 37.50) | 0.15 (cert 735.88; n 146, slack 40.82) | 0.2 (cert 681.22; n 158, slack 37.74) | 1,467.49 | 0.1321 | -309.23 | 1.7 | -1,667.96 | `a629daccfff818d7` |
| 1000.0 | 0.15 (cert 917.77; n 159, slack 37.50) | 0.3 (cert 945.16; n 146, slack 40.82) | 0.3 (cert 994.93; n 158, slack 37.74) | 1,470.90 | 0.2385 | -243.19 | 3.8 | -1,584.75 | `5037720e6fcb7b7a` |
| 1200.0 | 0.2 (cert 1,100.90; n 159, slack 37.50) | 0.4 (cert 1,189.62; n 146, slack 40.82) | 0.65 (cert 1,138.44; n 158, slack 37.74) | 1,491.46 | 0.3432 | -303.80 | 0.3 | -1,599.10 | `b55008689ae5c0e3` |

#### (5) Cost sensitivity of every kept book of this model: 44 books; kept mean > 0 at 8 pts slippage: **0** (best -1,147.95); at 3 pts: 0 (best -498.01); with uncapped 0.03% brokerage (+895.40 INR/trade): best kept mean -1,648.58. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### minute / context/scorecard - the deployable scorecard of sub-family (I) - inside the frozen vocabulary (context columns)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9467 | 0.9680 | 0.8182 / 1.0000 | 4 / 2 | 0.9353 | -1,003.67 | -1,095.41 | 91.74 | -52.43 | 0.5957 | 0.3 | 0.0668 | 0.0429 | 4 | -743.70 | -1,393.64 | -1,893.65 | 0.9712 | `3318c6a4b8255b7d` |
| 0.1 | 0.90 | 0.80 | 0.8833 | 0.9203 | 0.6234 / 0.9744 | 3 / 2 | 0.8742 | -1,002.18 | -1,061.20 | 59.01 | -12.35 | 0.6037 | 0.0 | 0.1275 | 0.1000 | 7 | -742.21 | -1,392.15 | -1,887.38 | 0.9452 | `dc92f339f6fe60de` |
| 0.15 | 0.85 | 0.70 | 0.8588 | 0.9045 | 0.6234 / 0.9615 | 4 / 1 | 0.8493 | -1,000.14 | -1,062.96 | 62.83 | -33.12 | 0.5872 | 0.1 | 0.1525 | 0.1000 | 8 | -740.16 | -1,390.10 | -1,888.48 | 0.9203 | `1eed9b5b23a55529` |
| 0.2 | 0.80 | 0.60 | 0.8040 | 0.8671 | 0.4800 / 0.9524 | 6 / 1 | 0.7761 | -976.10 | -1,125.71 | 149.60 | 48.40 | 0.1064 | 0.2 | 0.2291 | 0.1286 | 9 | -716.13 | -1,366.07 | -1,850.76 | 0.8470 | `b8a2b4c3e8cab563` |
| 0.3 | 0.70 | 0.40 | 0.7046 | 0.7925 | 0.4800 / 0.9200 | 7 / 0 | 0.6462 | -944.07 | -1,129.32 | 185.25 | 56.82 | 0.0230 | 1.0 | 0.3646 | 0.2000 | 10 | -684.10 | -1,334.04 | -1,834.81 | 0.7172 | `7b0eb96b9401d239` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05]; chosen **0.05** (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9).

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 627 | 0.6402 | 396 | 67 | 0.9217 | 0.9254 | 0.9808 | 0.0790 |
| 1 | 628 | 0.6463 | 388 | 66 | 0.9459 | 0.9394 | 0.9688 | 0.0528 |
| 2 | 622 | 0.6463 | 384 | 72 | 0.9219 | 0.9444 | 0.9617 | 0.0833 |
| 3 | 619 | 0.6402 | 509 | 75 | 0.9214 | 0.9200 | 0.9793 | 0.0783 |
| 4 | 633 | 0.6402 | 390 | 61 | 0.9333 | 0.9016 | 0.9514 | 0.0608 |
| 5 | 655 | 0.6463 | 341 | 39 | 0.9091 | 0.9744 | 0.9956 | 0.0993 |
| 6 | 630 | 0.6463 | 424 | 64 | 0.9434 | 0.9531 | 0.9971 | 0.0583 |
| 7 | 652 | 0.6402 | 266 | 42 | 0.9361 | 0.9524 | 0.9933 | 0.0670 |
| 8 | 668 | 0.6402 | 170 | 26 | 0.9588 | 0.9615 | 0.9987 | 0.0417 |
| 9 | 617 | 0.6365 | 499 | 77 | 0.5671 | 0.6234 | 0.5826 | 0.4431 |
| 10 | 669 | 0.6402 | 173 | 25 | 0.9422 | 0.8800 | 0.9627 | 0.0473 |
| 11 | 614 | 0.6402 | 512 | 80 | 0.7910 | 0.7875 | 0.8291 | 0.2083 |

#### (1b) Class x time-bin taxonomy (minute only; the taxonomy reads the SETUP clock)

| alpha | CV+ 1-2a | OOF winner coverage | |net|-wtd | coverage 09:15-10:29 (min cal winners) | coverage 10:30-12:59 (min cal winners) | coverage 13:00-15:19 (min cal winners) | kept share | diff | perm p | control pct | loser recall | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.90 | 0.9481 | 0.9462 | 0.9476 (163) | 0.9526 (181) | 0.9452 (256) | 0.9414 | -84.36 | 0.6087 | 0.4 | 0.0599 | -1,404.52 | `42c618a2bb002535` |
| 0.1 | 0.80 | 0.8804 | 0.8887 | 0.9058 (163) | 0.8199 (181) | 0.9075 (256) | 0.8845 | -89.45 | 0.4918 | 0.1 | 0.1147 | -1,409.90 | `b678d8db2757f5d7` |
| 0.15 | 0.70 | 0.8271 | 0.8358 | 0.8534 (163) | 0.8199 (181) | 0.8151 (256) | 0.8347 | -79.10 | 0.4628 | 0.0 | 0.1639 | -1,412.65 | `59a220e7cc4f0294` |
| 0.2 | 0.60 | 0.7925 | 0.7720 | 0.7853 (163) | 0.8199 (181) | 0.7774 (256) | 0.8062 | -184.51 | 0.0670 | 0.0 | 0.1913 | -1,435.34 | `75eb7c24fd476831` |
| 0.3 | 0.40 | 0.6686 | 0.6686 | 0.7382 (163) | 0.6682 (181) | 0.6233 (256) | 0.6846 | -163.97 | 0.0510 | 0.0 | 0.3124 | -1,451.28 | `e855abead8768595` |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 202 | 694 | 0.9467 | 0.9443 | 0.9306 | 0.0350 / 0.0785 | 0.0385 | 0.673 | 0.3270 | 0.9315 | 107.64 | 0.5012 | 0.3 | 0.0713 | 6 | -1,392.20 | `046156a86081968e` |
| 0.005 | 0.1 | 202 | 694 | 0.8934 | 0.8886 | 0.8671 | 0.0540 / 0.1515 | 0.0770 | 0.6508 | 0.3492 | 0.8702 | 23.04 | 0.8331 | 0.0 | 0.1341 | 7 | -1,396.58 | `79858fc201543e6d` |
| 0.005 | 0.15 | 202 | 694 | 0.8300 | 0.8223 | 0.8150 | 0.0730 / 0.2208 | 0.0805 | 0.6508 | 0.3492 | 0.8133 | 69.98 | 0.4718 | 0.1 | 0.1897 | 6 | -1,386.51 | `7b103781ed33b789` |
| 0.005 | 0.2 | 202 | 694 | 0.7752 | 0.7651 | 0.7514 | 0.1040 / 0.2660 | 0.1140 | 0.6402 | 0.3598 | 0.7437 | 137.23 | 0.1304 | 0.4 | 0.2621 | 9 | -1,364.40 | `0bb79c57c12a81c1` |
| 0.005 | 0.3 | 202 | 694 | 0.6974 | 0.6837 | 0.6590 | 0.2810 / 0.3575 | 0.2910 | 0.6009 | 0.3991 | 0.6262 | 222.50 | 0.0045 | 3.5 | 0.3869 | 10 | -1,316.41 | `936e93793948472e` |
| 0.01 | 0.05 | 202 | 694 | 0.9467 | 0.9443 | 0.9422 | 0.0200 / 0.0870 | 0.0270 | 0.6917 | 0.3083 | 0.9394 | 30.16 | 0.8511 | 0.0 | 0.0620 | 5 | -1,397.74 | `a539c7b092ebc039` |
| 0.01 | 0.1 | 202 | 694 | 0.8963 | 0.8916 | 0.8960 | 0.0380 / 0.2030 | 0.0740 | 0.6508 | 0.3492 | 0.8713 | 84.16 | 0.4598 | 0.2 | 0.1333 | 7 | -1,388.74 | `63fe1352efb3279f` |
| 0.01 | 0.15 | 202 | 694 | 0.8401 | 0.8328 | 0.8439 | 0.0570 / 0.2710 | 0.0810 | 0.6508 | 0.3492 | 0.8217 | 46.22 | 0.6617 | 0.0 | 0.1817 | 7 | -1,391.33 | `4d93c428048ca63d` |
| 0.01 | 0.2 | 202 | 694 | 0.7853 | 0.7756 | 0.8035 | 0.0740 / 0.2940 | 0.0980 | 0.6402 | 0.3598 | 0.7558 | 87.96 | 0.3453 | 0.3 | 0.2496 | 7 | -1,378.10 | `eebfdea4e9555ece` |
| 0.01 | 0.3 | 202 | 694 | 0.6931 | 0.6792 | 0.6590 | 0.2320 / 0.4150 | 0.2520 | 0.6061 | 0.3939 | 0.6242 | 204.60 | 0.0130 | 1.8 | 0.3885 | 10 | -1,322.69 | `d861c3a34f364520` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.1116 | 1,793.19 | 0.7948 | 0.2072 | 0.8622 | -471,072.29 | 1,697,284.49 | -471,072.29 | -1,319,714.54 | -2,168,356.78 | -947.83 | 69.54 | -1,337.80 | -1,856.29 | yes | `2ec837b4071faf62` |
| 0.15 | 0.1487 | 1,780.63 | 0.8036 | 0.2721 | 0.8188 | -620,034.22 | 1,558,204.72 | -620,034.22 | -1,399,136.58 | -2,178,238.94 | -936.61 | 85.75 | -1,326.57 | -1,858.16 | yes | `71e89fed0f22baa7` |
| 0.2 | 0.2123 | 1,693.31 | 0.8095 | 0.3271 | 0.7553 | -923,869.51 | 1,440,634.69 | -923,869.51 | -1,644,186.85 | -2,364,504.20 | -977.64 | 40.58 | -1,367.60 | -1,886.03 | yes | `8cdfea8e0840202f` |
| 0.25 | 0.2415 | 1,685.83 | 0.8121 | 0.3981 | 0.7233 | -983,811.51 | 1,288,485.17 | -983,811.51 | -1,628,054.10 | -2,272,296.68 | -915.17 | 124.50 | -1,305.14 | -1,832.39 | yes | `944cb0d70095120a` |
| 0.3 | 0.3378 | 1,594.78 | 0.8238 | 0.4535 | 0.6349 | -1,451,632.48 | 1,170,009.18 | -1,451,632.48 | -2,036,637.07 | -2,621,641.66 | -965.18 | 67.09 | -1,355.15 | -1,911.82 | yes | `15dbfd5b6157d176` |
| 0.35 | 0.3693 | 1,569.41 | 0.8254 | 0.4751 | 0.6076 | -1,586,922.59 | 1,123,735.89 | -1,586,922.59 | -2,148,790.54 | -2,710,658.48 | -965.28 | 70.28 | -1,355.25 | -1,898.48 | yes | `7717788b1bcd602f` |
| 0.4 | 0.4106 | 1,566.26 | 0.8228 | 0.5284 | 0.5642 | -1,760,527.04 | 1,009,655.73 | -1,760,527.04 | -2,265,354.91 | -2,770,182.77 | -963.09 | 78.93 | -1,353.05 | -1,879.23 | yes | `d4374032a55d4cd5` |
| 0.45 | 0.4297 | 1,558.81 | 0.8228 | 0.5426 | 0.5463 | -1,848,916.98 | 979,164.46 | -1,848,916.98 | -2,338,499.21 | -2,828,081.44 | -966.50 | 75.58 | -1,356.47 | -1,877.11 | yes | `08aa0179ae5f93b4` |
| 0.5 | 0.5108 | 1,551.05 | 0.8228 | 0.6472 | 0.4639 | -2,171,615.44 | 755,308.18 | -2,171,615.44 | -2,549,269.53 | -2,926,923.62 | -954.98 | 111.67 | -1,344.94 | -1,868.44 | yes | `ef23cbd08580fa46` |
| 0.55 | 0.5445 | 1,535.73 | 0.8214 | 0.6860 | 0.4345 | -2,283,973.09 | 672,145.90 | -2,283,973.09 | -2,620,046.04 | -2,956,118.99 | -942.23 | 147.90 | -1,332.20 | -1,844.06 | yes | `20114e50627218de` |
| 0.6 | 0.5901 | 1,522.87 | 0.8222 | 0.7402 | 0.3926 | -2,446,048.86 | 556,232.76 | -2,446,048.86 | -2,724,165.24 | -3,002,281.62 | -931.12 | 191.47 | -1,321.08 | -1,834.20 | yes | `72841c005c0742a6` |
| 0.65 | 0.6462 | 1,523.35 | 0.8300 | 0.7925 | 0.3350 | -2,716,096.77 | 444,202.66 | -2,716,096.77 | -2,938,198.10 | -3,160,299.43 | -944.07 | 185.25 | -1,334.04 | -1,834.81 | yes | `7bda52791f5b92b5` |
| 0.7 | 0.7165 | 1,507.75 | 0.8357 | 0.8354 | 0.2706 | -3,051,380.37 | 352,425.64 | -3,051,380.37 | -3,227,593.19 | -3,403,806.01 | -956.55 | 187.19 | -1,346.51 | -1,836.99 | yes | `5573d18d54998d10` |
| 0.75 | 0.7579 | 1,504.45 | 0.8373 | 0.8594 | 0.2305 | -3,266,168.11 | 300,932.44 | -3,266,168.11 | -3,416,634.33 | -3,567,100.55 | -968.04 | 171.67 | -1,358.01 | -1,840.17 | yes | `7237a263b81be7ec` |
| 0.8 | 0.8055 | 1,506.11 | 0.8408 | 0.8824 | 0.1815 | -3,541,907.40 | 251,767.81 | -3,541,907.40 | -3,667,791.31 | -3,793,675.21 | -987.70 | 112.60 | -1,377.67 | -1,870.98 | yes | `1f0f1bdbe64b4b56` |
| 0.85 | 0.8493 | 1,504.18 | 0.8424 | 0.9045 | 0.1383 | -3,781,523.41 | 204,519.69 | -3,781,523.41 | -3,883,783.26 | -3,986,043.10 | -1,000.14 | 62.83 | -1,390.10 | -1,888.48 | yes | `806243864fd30dd4` |
| 0.9 | 0.8816 | 1,498.89 | 0.8423 | 0.9224 | 0.1088 | -3,939,089.07 | 166,218.74 | -3,939,089.07 | -4,022,198.44 | -4,105,307.81 | -1,003.59 | 50.84 | -1,393.55 | -1,887.96 | yes | `f2c182c1125b7d74` |
| 0.95 | 0.9353 | 1,493.66 | 0.8422 | 0.9680 | 0.0579 | -4,179,293.85 | 68,409.62 | -4,179,293.85 | -4,213,498.66 | -4,247,703.47 | -1,003.67 | 91.74 | -1,393.64 | -1,893.65 | yes | `a0a64c4f662ef2c0` |
| 1.0 | 1.0000 | 1,482.62 | 0.8441 | 1.0000 | -0.0000 | -4,494,772.79 | 0.00 | -4,494,772.79 | -4,494,772.79 | -4,494,772.79 | -1,009.61 | - | - | -1,905.01 | yes | `c28e2585b8859295` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.1, w = 1 -> 0.1. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4616 | 0.0548 | 862.93 | 888.49 | 75 |
| 0.1 | 0.4986 | 0.1016 | 1,184.40 | 1,208.36 | 119 |
| 0.15 | 0.5106 | 0.1502 | 1,316.98 | 1,340.28 | 145 |
| 0.2 | 0.5349 | 0.2368 | 1,427.06 | 1,449.81 | 161 |
| 0.25 | 0.5379 | 0.3134 | 1,437.90 | 1,460.60 | 169 |
| 0.3 | 0.5379 | 0.3134 | 1,437.90 | 1,460.60 | 169 |
| 0.35 | 0.5410 | 0.4760 | 1,480.44 | 1,502.92 | 188 |
| 0.4 | 0.5410 | 0.4760 | 1,480.44 | 1,502.92 | 188 |
| 0.45 | 0.5410 | 0.4760 | 1,480.44 | 1,502.92 | 188 |
| 0.5 | 0.5472 | 0.5109 | 1,472.33 | 1,494.85 | 192 |
| 0.55 | 0.5709 | 0.6137 | 1,472.59 | 1,495.12 | 196 |
| 0.6 | 0.5709 | 0.6137 | 1,472.59 | 1,495.12 | 196 |
| 0.65 | 0.6124 | 0.6611 | 1,446.98 | 1,469.63 | 196 |
| 0.7 | 0.6154 | 0.7065 | 1,438.22 | 1,460.91 | 196 |
| 0.75 | 0.6213 | 0.7788 | 1,428.22 | 1,450.96 | 196 |
| 0.8 | 0.6402 | 0.8330 | 1,441.82 | 1,464.50 | 197 |
| 0.85 | 0.6508 | 0.8791 | 1,431.18 | 1,453.91 | 197 |
| 0.9 | 0.6730 | 0.9427 | 1,439.74 | 1,462.43 | 197 |
| 0.95 | 0.6821 | 0.9508 | 1,453.72 | 1,476.34 | 199 |
| 1.0 | - | 1.0000 | 1,435.99 | 1,458.70 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | - | - | - | - | - | - | - | - | - | - | no lambda with a certificate <= alpha |
| 1000.0 | 0.05 | 0.4616 | 888.49 | 2,204.33 | 0.0144 | 2,305.72 | 0.0290 | -414.42 | 0.0 | -1,801.98 | `cbd2d48efcc022fd` |
| 1200.0 | 0.05 | 0.4616 | 888.49 | 2,204.33 | 0.0144 | 2,305.72 | 0.0290 | -414.42 | 0.0 | -1,801.98 | `d4e9f75827ac0543` |

Per-bin certificates (minute only):

| alpha (INR) | lambda* 09:15-10:29 | lambda* 10:30-12:59 | lambda* 13:00-15:19 | realised risk before the block | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.1 (cert 726.75; n 159, slack 37.50) | 0.15 (cert 746.45; n 146, slack 40.82) | 0.25 (cert 634.40; n 158, slack 37.74) | 1,344.31 | 0.1130 | -289.69 | 1.1 | -1,656.53 | `bbddc366ee32862c` |
| 1000.0 | 0.15 (cert 842.45; n 159, slack 37.50) | 0.25 (cert 860.62; n 146, slack 40.82) | 0.25 (cert 634.40; n 158, slack 37.74) | 1,392.02 | 0.2823 | -275.09 | 0.2 | -1,596.99 | `0bda40d978f7eff3` |
| 1200.0 | 0.25 (cert 1,116.16; n 159, slack 37.50) | 0.55 (cert 1,116.15; n 146, slack 40.82) | 0.5 (cert 1,060.76; n 158, slack 37.74) | 1,404.72 | 0.4093 | -304.01 | 0.1 | -1,579.16 | `074d04798473d683` |

#### (5) Cost sensitivity of every kept book of this model: 44 books; kept mean > 0 at 8 pts slippage: **0** (best -1,305.14); at 3 pts: 0 (best -655.20); with uncapped 0.03% brokerage (+895.40 INR/trade): best kept mean -1,818.34. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### minute / h5_full/hgbc - gradient-boosting ceiling of sub-family (II) (reference) - outside the frozen shortlist (importance rule failed for every cluster)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9481 | 0.9679 | 0.7692 / 1.0000 | 4 / 1 | 0.9182 | -1,006.65 | -1,042.82 | 36.17 | -156.87 | 0.7926 | 5.2 | 0.0873 | 0.0143 | 8 | -746.67 | -1,396.62 | -1,902.97 | 0.9481 | `c5c4afdc3d68689c` |
| 0.1 | 0.90 | 0.80 | 0.8948 | 0.9132 | 0.6667 / 1.0000 | 5 / 1 | 0.8428 | -1,006.51 | -1,026.19 | 19.68 | -106.55 | 0.8526 | 9.6 | 0.1668 | 0.0714 | 8 | -746.54 | -1,396.48 | -1,901.47 | 0.9027 | `9f3fcad2ab03303e` |
| 0.15 | 0.85 | 0.70 | 0.8516 | 0.8885 | 0.6154 / 0.9600 | 3 / 1 | 0.7776 | -985.34 | -1,094.46 | 109.12 | -36.09 | 0.2484 | 21.2 | 0.2360 | 0.1000 | 8 | -725.37 | -1,375.31 | -1,880.13 | 0.8376 | `c1468ba1c5115c81` |
| 0.2 | 0.80 | 0.60 | 0.7939 | 0.8242 | 0.4872 / 0.9600 | 5 / 1 | 0.7186 | -990.07 | -1,059.50 | 69.43 | -42.11 | 0.4328 | 4.6 | 0.2954 | 0.1571 | 8 | -730.09 | -1,380.03 | -1,883.26 | 0.7785 | `e976daeab32d7612` |
| 0.3 | 0.70 | 0.40 | 0.7017 | 0.7469 | 0.4359 / 0.8611 | 6 / 0 | 0.6179 | -983.80 | -1,051.35 | 67.55 | -75.31 | 0.3913 | 2.2 | 0.3976 | 0.2143 | 9 | -723.82 | -1,373.76 | -1,873.27 | 0.6779 | `cabfc4d96b7f85e1` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05]; chosen **0.05** (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9).

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 627 | 0.7936 | 396 | 67 | 0.8763 | 0.9552 | 0.9560 | 0.1398 |
| 1 | 628 | 0.7877 | 388 | 66 | 0.8814 | 0.8636 | 0.8279 | 0.1149 |
| 2 | 622 | 0.7904 | 384 | 72 | 0.9167 | 0.9306 | 0.8963 | 0.0865 |
| 3 | 619 | 0.7878 | 509 | 75 | 0.8153 | 0.8933 | 0.9267 | 0.1982 |
| 4 | 633 | 0.7904 | 390 | 61 | 0.8359 | 0.9344 | 0.9462 | 0.1824 |
| 5 | 655 | 0.7786 | 341 | 39 | 0.6686 | 0.6667 | 0.6397 | 0.3311 |
| 6 | 630 | 0.7885 | 424 | 64 | 0.8208 | 0.9062 | 0.9389 | 0.1944 |
| 7 | 652 | 0.7923 | 266 | 42 | 0.9023 | 0.9762 | 0.9394 | 0.1116 |
| 8 | 668 | 0.7923 | 170 | 26 | 0.9176 | 1.0000 | 1.0000 | 0.0972 |
| 9 | 617 | 0.7885 | 499 | 77 | 0.8577 | 0.8961 | 0.9539 | 0.1493 |
| 10 | 669 | 0.7886 | 173 | 25 | 0.9017 | 0.9600 | 0.9802 | 0.1081 |
| 11 | 614 | 0.7816 | 512 | 80 | 0.8086 | 0.8125 | 0.8967 | 0.1921 |

#### (1b) Class x time-bin taxonomy (minute only; the taxonomy reads the SETUP clock)

| alpha | CV+ 1-2a | OOF winner coverage | |net|-wtd | coverage 09:15-10:29 (min cal winners) | coverage 10:30-12:59 (min cal winners) | coverage 13:00-15:19 (min cal winners) | kept share | diff | perm p | control pct | loser recall | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.90 | 0.9539 | 0.9689 | 0.9581 (163) | 0.9479 (181) | 0.9555 (256) | 0.9239 | 26.51 | 0.8646 | 4.2 | 0.0817 | -1,397.55 | `67fa5014f1d1635b` |
| 0.1 | 0.80 | 0.9020 | 0.9125 | 0.8953 (163) | 0.9052 (181) | 0.9041 (256) | 0.8578 | 29.35 | 0.8056 | 21.2 | 0.1503 | -1,395.40 | `0d23934adec77645` |
| 0.15 | 0.70 | 0.8530 | 0.8585 | 0.8534 (163) | 0.8531 (181) | 0.8527 (256) | 0.7987 | 22.84 | 0.7986 | 26.3 | 0.2113 | -1,394.97 | `c0f11759167d2fbd` |
| 0.2 | 0.60 | 0.7954 | 0.8060 | 0.8010 (163) | 0.7962 (181) | 0.7911 (256) | 0.7350 | 26.78 | 0.7811 | 32.6 | 0.2762 | -1,392.47 | `5f55ed7081fe062d` |
| 0.3 | 0.40 | 0.7089 | 0.7044 | 0.7120 (163) | 0.7062 (181) | 0.7089 (256) | 0.6345 | 7.36 | 0.9270 | 34.0 | 0.3792 | -1,396.88 | `92d5574b7bed01e0` |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 202 | 694 | 0.9481 | 0.9458 | 0.9364 | 0.0285 / 0.0683 | 0.0435 | 0.8375 | 0.1625 | 0.9212 | 63.42 | 0.6697 | 3.9 | 0.0838 | 9 | -1,394.57 | `c7613bdc8b2b30d8` |
| 0.005 | 0.1 | 202 | 694 | 0.8977 | 0.8931 | 0.8728 | 0.0685 / 0.1370 | 0.0920 | 0.7941 | 0.2059 | 0.8286 | 133.84 | 0.1989 | 42.6 | 0.1841 | 9 | -1,376.64 | `b6ba1b0243041d37` |
| 0.005 | 0.15 | 202 | 694 | 0.8473 | 0.8404 | 0.8439 | 0.0953 / 0.1925 | 0.1405 | 0.7674 | 0.2326 | 0.7761 | 134.32 | 0.1469 | 46.5 | 0.2371 | 10 | -1,369.49 | `fdadb23a3992d87f` |
| 0.005 | 0.2 | 202 | 694 | 0.8012 | 0.7922 | 0.8150 | 0.1360 / 0.2490 | 0.2040 | 0.74 | 0.2600 | 0.7109 | 166.16 | 0.0570 | 47.2 | 0.3057 | 11 | -1,351.54 | `d89f5765d09f4be5` |
| 0.005 | 0.3 | 202 | 694 | 0.6960 | 0.6822 | 0.7283 | 0.1980 / 0.3705 | 0.2860 | 0.7131 | 0.2869 | 0.6116 | 74.86 | 0.3693 | 5.7 | 0.4039 | 9 | -1,370.50 | `d1b9242ee318b4b7` |
| 0.01 | 0.05 | 202 | 694 | 0.9467 | 0.9443 | 0.9306 | 0.0140 / 0.0865 | 0.0270 | 0.8493 | 0.1507 | 0.9241 | -61.15 | 0.6832 | 10.4 | 0.0801 | 6 | -1,404.22 | `5912513ee28132dc` |
| 0.01 | 0.1 | 202 | 694 | 0.8963 | 0.8916 | 0.8671 | 0.0370 / 0.1630 | 0.0740 | 0.8053 | 0.1947 | 0.8349 | 139.76 | 0.2024 | 29.3 | 0.1764 | 9 | -1,376.50 | `83bf657116a625d5` |
| 0.01 | 0.15 | 202 | 694 | 0.8487 | 0.8419 | 0.8439 | 0.0670 / 0.2235 | 0.1410 | 0.7674 | 0.2326 | 0.7776 | 120.47 | 0.1899 | 41.6 | 0.2355 | 9 | -1,372.78 | `b806d7b00d390c3e` |
| 0.01 | 0.2 | 202 | 694 | 0.8012 | 0.7922 | 0.8092 | 0.0920 / 0.2940 | 0.2080 | 0.7396 | 0.2604 | 0.7228 | 108.36 | 0.2094 | 38.8 | 0.2916 | 10 | -1,369.54 | `ccf077c24e498548` |
| 0.01 | 0.3 | 202 | 694 | 0.7003 | 0.6867 | 0.7110 | 0.1530 / 0.4310 | 0.3020 | 0.7061 | 0.2939 | 0.6166 | 78.26 | 0.3253 | 3.0 | 0.3989 | 8 | -1,369.57 | `b8128a93486e6ec3` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.1002 | 1,750.75 | 0.7668 | 0.1735 | 0.8800 | -425,144.14 | 1,769,353.69 | -425,144.14 | -1,309,820.98 | -2,194,497.83 | -953.24 | 62.65 | -1,343.20 | -1,843.70 | yes | `584027e5543aedca` |
| 0.15 | 0.1500 | 1,686.76 | 0.7740 | 0.2468 | 0.8277 | -614,842.92 | 1,612,363.24 | -614,842.92 | -1,421,024.54 | -2,227,206.16 | -920.42 | 104.93 | -1,310.39 | -1,813.15 | yes | `0dd8af9e9834ce85` |
| 0.2 | 0.2004 | 1,685.48 | 0.7960 | 0.2884 | 0.7709 | -903,070.76 | 1,523,421.96 | -903,070.76 | -1,664,781.74 | -2,426,492.72 | -1,012.41 | -3.51 | -1,402.38 | -1,902.17 | yes | `25ceb25575dd9da6` |
| 0.25 | 0.2500 | 1,665.74 | 0.7996 | 0.3540 | 0.7180 | -1,113,170.34 | 1,382,976.52 | -1,113,170.34 | -1,804,658.60 | -2,496,146.86 | -1,000.15 | 12.61 | -1,390.12 | -1,889.43 | yes | `15a8b12a155698da` |
| 0.3 | 0.3005 | 1,636.73 | 0.8012 | 0.4204 | 0.6674 | -1,307,017.82 | 1,240,854.93 | -1,307,017.82 | -1,927,445.28 | -2,547,872.75 | -976.84 | 46.84 | -1,366.81 | -1,866.32 | yes | `42f647abfbb7c723` |
| 0.35 | 0.3500 | 1,615.94 | 0.8036 | 0.4808 | 0.6180 | -1,505,298.20 | 1,111,441.87 | -1,505,298.20 | -2,061,019.13 | -2,616,740.07 | -966.17 | 66.82 | -1,356.14 | -1,857.33 | yes | `d9e3a1f9ff790ac1` |
| 0.4 | 0.4003 | 1,594.80 | 0.8025 | 0.5352 | 0.5687 | -1,715,834.43 | 994,990.65 | -1,715,834.43 | -2,213,329.75 | -2,710,825.08 | -962.87 | 77.93 | -1,352.83 | -1,853.61 | yes | `ff3a9d4827a5e02e` |
| 0.45 | 0.4504 | 1,581.91 | 0.8085 | 0.5870 | 0.5190 | -1,934,781.68 | 884,143.25 | -1,934,781.68 | -2,376,853.30 | -2,818,924.93 | -964.98 | 81.20 | -1,354.94 | -1,855.50 | yes | `f0747da38fc0756b` |
| 0.5 | 0.4993 | 1,577.06 | 0.8111 | 0.6482 | 0.4687 | -2,137,769.29 | 753,064.60 | -2,137,769.29 | -2,514,301.59 | -2,890,833.89 | -961.66 | 95.77 | -1,351.62 | -1,852.68 | yes | `1ec350a6080a0e55` |
| 0.55 | 0.5494 | 1,572.42 | 0.8185 | 0.6733 | 0.4174 | -2,424,417.98 | 699,367.57 | -2,424,417.98 | -2,774,101.77 | -3,123,785.55 | -991.18 | 40.90 | -1,381.14 | -1,881.24 | yes | `635272b580139ba5` |
| 0.6 | 0.6011 | 1,564.62 | 0.8229 | 0.7296 | 0.3661 | -2,644,789.40 | 578,964.05 | -2,644,789.40 | -2,934,271.43 | -3,223,753.45 | -988.34 | 53.32 | -1,378.30 | -1,877.72 | yes | `b71f3d5384be09a3` |
| 0.65 | 0.6503 | 1,544.55 | 0.8235 | 0.7736 | 0.3228 | -2,837,522.27 | 484,741.13 | -2,837,522.27 | -3,079,892.83 | -3,322,263.40 | -980.15 | 84.24 | -1,370.11 | -1,871.96 | yes | `fdaf411d2346dd79` |
| 0.7 | 0.6986 | 1,534.18 | 0.8251 | 0.8193 | 0.2776 | -3,039,487.33 | 386,878.14 | -3,039,487.33 | -3,232,926.40 | -3,426,365.47 | -977.33 | 107.09 | -1,367.29 | -1,869.68 | yes | `377adbd05eff0d13` |
| 0.75 | 0.7498 | 1,528.79 | 0.8289 | 0.8511 | 0.2276 | -3,303,256.29 | 318,727.13 | -3,303,256.29 | -3,462,619.85 | -3,621,983.42 | -989.59 | 79.99 | -1,379.56 | -1,884.07 | yes | `99216d48f1bd4651` |
| 0.8 | 0.8008 | 1,520.45 | 0.8303 | 0.8986 | 0.1785 | -3,527,608.95 | 217,137.68 | -3,527,608.95 | -3,636,177.79 | -3,744,746.63 | -989.51 | 100.86 | -1,379.48 | -1,884.98 | yes | `d55dca9a6334d134` |
| 0.85 | 0.8502 | 1,517.92 | 0.8346 | 0.9162 | 0.1290 | -3,818,258.57 | 179,328.78 | -3,818,258.57 | -3,907,922.96 | -3,997,587.35 | -1,008.79 | 5.48 | -1,398.75 | -1,904.65 | yes | `3ce0d8352ea50790` |
| 0.9 | 0.8987 | 1,508.21 | 0.8375 | 0.9572 | 0.0853 | -4,020,082.29 | 91,606.76 | -4,020,082.29 | -4,065,885.67 | -4,111,689.05 | -1,004.77 | 47.76 | -1,394.73 | -1,901.08 | yes | `c2ef3c5e5d9f8bad` |
| 0.95 | 0.9481 | 1,497.89 | 0.8403 | 0.9842 | 0.0419 | -4,250,679.95 | 33,929.63 | -4,250,679.95 | -4,267,644.76 | -4,284,609.58 | -1,007.03 | 49.65 | -1,397.00 | -1,902.78 | yes | `e599a254f53cc5c6` |
| 1.0 | 1.0000 | 1,482.62 | 0.8441 | 1.0000 | -0.0000 | -4,494,772.79 | 0.00 | -4,494,772.79 | -4,494,772.79 | -4,494,772.79 | -1,009.61 | - | - | -1,905.01 | yes | `5a210c343ff1e3b6` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.1, w = 1 -> 0.1. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4399 | 0.0505 | 640.89 | 667.55 | 63 |
| 0.1 | 0.4922 | 0.1003 | 954.23 | 979.33 | 104 |
| 0.15 | 0.5259 | 0.1502 | 1,084.25 | 1,108.71 | 128 |
| 0.2 | 0.5576 | 0.2000 | 1,310.75 | 1,334.08 | 155 |
| 0.25 | 0.5844 | 0.2505 | 1,329.86 | 1,353.09 | 166 |
| 0.3 | 0.6018 | 0.3003 | 1,372.40 | 1,395.43 | 175 |
| 0.35 | 0.6217 | 0.3502 | 1,411.68 | 1,434.51 | 182 |
| 0.4 | 0.6400 | 0.4000 | 1,428.82 | 1,451.56 | 189 |
| 0.45 | 0.6557 | 0.4498 | 1,450.51 | 1,473.15 | 190 |
| 0.5 | 0.6703 | 0.5003 | 1,426.82 | 1,449.57 | 191 |
| 0.55 | 0.6845 | 0.5502 | 1,454.55 | 1,477.17 | 193 |
| 0.6 | 0.7020 | 0.6000 | 1,457.40 | 1,480.00 | 194 |
| 0.65 | 0.7149 | 0.6498 | 1,451.43 | 1,474.06 | 195 |
| 0.7 | 0.7296 | 0.6997 | 1,444.18 | 1,466.84 | 197 |
| 0.75 | 0.7448 | 0.7502 | 1,439.08 | 1,461.77 | 197 |
| 0.8 | 0.7619 | 0.8000 | 1,438.06 | 1,460.76 | 198 |
| 0.85 | 0.7816 | 0.8498 | 1,456.62 | 1,479.22 | 199 |
| 0.9 | 0.8017 | 0.8997 | 1,459.01 | 1,481.60 | 199 |
| 0.95 | 0.8340 | 0.9495 | 1,447.19 | 1,469.84 | 199 |
| 1.0 | - | 1.0000 | 1,435.99 | 1,458.70 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.05 | 0.4399 | 667.55 | 1,704.23 | 0.0520 | 1,843.58 | 0.0514 | 164.78 | 2.0 | -1,243.27 | `d8726140dfc60b24` |
| 1000.0 | 0.1 | 0.4922 | 979.33 | 1,658.87 | 0.0941 | 1,764.29 | 0.0964 | 63.53 | 0.0 | -1,342.17 | `9978692f3f0b888f` |
| 1200.0 | 0.15 | 0.5259 | 1,108.71 | 1,586.21 | 0.1356 | 1,679.58 | 0.1408 | 145.09 | 1.6 | -1,274.91 | `a9556b0dc93db272` |

Per-bin certificates (minute only):

| alpha (INR) | lambda* 09:15-10:29 | lambda* 10:30-12:59 | lambda* 13:00-15:19 | realised risk before the block | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.2 (cert 792.01; n 159, slack 37.50) | 0.15 (cert 747.19; n 146, slack 40.82) | 0.2 (cert 781.37; n 158, slack 37.74) | 1,570.26 | 0.1898 | 78.54 | 48.9 | -1,335.94 | `0d8e032e207459ea` |
| 1000.0 | 0.3 (cert 983.23; n 159, slack 37.50) | 0.2 (cert 923.11; n 146, slack 40.82) | 0.25 (cert 923.26; n 158, slack 37.74) | 1,553.96 | 0.2428 | 61.17 | 20.4 | -1,353.26 | `4ec11996703b3f10` |
| 1200.0 | 0.4 (cert 1,186.33; n 159, slack 37.50) | 0.35 (cert 1,172.25; n 146, slack 40.82) | 0.35 (cert 1,124.78; n 158, slack 37.74) | 1,515.00 | 0.3612 | -34.00 | 21.1 | -1,421.29 | `1098cf66a3479293` |

#### (5) Cost sensitivity of every kept book of this model: 45 books; kept mean > 0 at 8 pts slippage: **0** (best -1,243.27); at 3 pts: 0 (best -593.33); with uncapped 0.03% brokerage (+895.40 INR/trade): best kept mean -1,737.90. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### minute / h5_full/scorecard - finalist of sub-family (II) (scorecard -> distilled tree; this is the scorecard OOF p) - outside the frozen shortlist (importance rule failed for every cluster)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9452 | 0.9580 | 0.8312 / 1.0000 | 4 / 3 | 0.9322 | -1,009.69 | -1,008.47 | -1.22 | -143.67 | 0.9925 | 4.7 | 0.0703 | 0.0571 | 3 | -749.71 | -1,399.65 | -1,904.44 | 0.9301 | `89647c4f27f98764` |
| 0.1 | 0.90 | 0.80 | 0.8934 | 0.9202 | 0.7436 / 1.0000 | 6 / 2 | 0.8731 | -1,011.07 | -999.55 | -11.52 | -164.18 | 0.9195 | 0.1 | 0.1307 | 0.0857 | 5 | -751.09 | -1,401.03 | -1,907.26 | 0.8783 | `78436f8c2101acb3` |
| 0.15 | 0.85 | 0.70 | 0.8473 | 0.8766 | 0.6883 / 1.0000 | 6 / 1 | 0.8032 | -1,012.28 | -998.69 | -13.59 | -123.97 | 0.8906 | 0.0 | 0.2049 | 0.1286 | 6 | -752.31 | -1,402.25 | -1,910.20 | 0.8461 | `091449d9ef04de43` |
| 0.2 | 0.80 | 0.60 | 0.8040 | 0.8533 | 0.5385 / 1.0000 | 6 / 1 | 0.7300 | -998.33 | -1,040.10 | 41.77 | -112.58 | 0.6577 | 0.0 | 0.2837 | 0.1286 | 5 | -738.35 | -1,388.29 | -1,900.31 | 0.7729 | `ebb091878a0d43a7` |
| 0.3 | 0.70 | 0.40 | 0.6945 | 0.7843 | 0.3333 / 0.8788 | 6 / 1 | 0.5876 | -972.74 | -1,062.14 | 89.41 | -106.46 | 0.2644 | 0.0 | 0.4321 | 0.1571 | 7 | -712.76 | -1,362.70 | -1,866.21 | 0.6305 | `8940f06abb09a48d` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas []; chosen **None** - no alpha satisfies both constraints.

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 627 | 0.6669 | 396 | 67 | 0.8283 | 0.8358 | 0.8883 | 0.1733 |
| 1 | 628 | 0.6669 | 388 | 66 | 0.9046 | 0.9394 | 0.9659 | 0.1025 |
| 2 | 622 | 0.6665 | 384 | 72 | 0.7656 | 0.8056 | 0.8130 | 0.2436 |
| 3 | 619 | 0.6671 | 509 | 75 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 4 | 633 | 0.6671 | 390 | 61 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 5 | 655 | 0.6665 | 341 | 39 | 0.8094 | 0.7436 | 0.6952 | 0.1821 |
| 6 | 630 | 0.6665 | 424 | 64 | 0.7524 | 0.8125 | 0.8547 | 0.2583 |
| 7 | 652 | 0.6669 | 266 | 42 | 0.9398 | 0.9762 | 0.9848 | 0.0670 |
| 8 | 668 | 0.6669 | 170 | 26 | 0.8059 | 0.8462 | 0.9738 | 0.2014 |
| 9 | 617 | 0.6659 | 499 | 77 | 0.6974 | 0.7662 | 0.8421 | 0.3152 |
| 10 | 669 | 0.6669 | 173 | 25 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 11 | 614 | 0.6671 | 512 | 80 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

#### (1b) Class x time-bin taxonomy (minute only; the taxonomy reads the SETUP clock)

| alpha | CV+ 1-2a | OOF winner coverage | |net|-wtd | coverage 09:15-10:29 (min cal winners) | coverage 10:30-12:59 (min cal winners) | coverage 13:00-15:19 (min cal winners) | kept share | diff | perm p | control pct | loser recall | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.90 | 0.9496 | 0.9606 | 0.9372 (163) | 0.9526 (181) | 0.9555 (256) | 0.9360 | 28.06 | 0.8676 | 12.6 | 0.0665 | -1,397.78 | `005e47fe130354c5` |
| 0.1 | 0.80 | 0.8948 | 0.9176 | 0.8953 (163) | 0.8957 (181) | 0.8938 (256) | 0.8886 | -94.91 | 0.4423 | 0.8 | 0.1126 | -1,410.15 | `78d38f8a4bf49f0b` |
| 0.15 | 0.70 | 0.8429 | 0.8660 | 0.8482 (163) | 0.8199 (181) | 0.8562 (256) | 0.8340 | -149.36 | 0.1544 | 0.0 | 0.1676 | -1,424.37 | `84d366c95f7e4310` |
| 0.2 | 0.60 | 0.7968 | 0.8207 | 0.7906 (163) | 0.7962 (181) | 0.8014 (256) | 0.7859 | -166.96 | 0.0790 | 0.0 | 0.2161 | -1,435.31 | `397f69fa82bebaf1` |
| 0.3 | 0.40 | 0.6988 | 0.7100 | 0.7120 (163) | 0.6919 (181) | 0.6952 (256) | 0.6566 | -144.09 | 0.0880 | 0.0 | 0.3513 | -1,449.06 | `d81aa46e54af277a` |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 202 | 694 | 0.9553 | 0.9533 | 0.9595 | 0.0420 / 0.0958 | 0.0685 | 0.6737 | 0.3263 | 0.9429 | 41.53 | 0.8111 | 1.4 | 0.0593 | 5 | -1,397.20 | `a3598a47ed5d210a` |
| 0.005 | 0.1 | 202 | 694 | 0.9092 | 0.9051 | 0.9364 | 0.0790 / 0.1540 | 0.1320 | 0.6618 | 0.3382 | 0.8765 | 33.40 | 0.7836 | 0.3 | 0.1296 | 7 | -1,395.45 | `b7d1dd94aabb81af` |
| 0.005 | 0.15 | 202 | 694 | 0.8602 | 0.8539 | 0.9133 | 0.1060 / 0.2010 | 0.1855 | 0.6338 | 0.3662 | 0.8156 | -15.65 | 0.8776 | 0.0 | 0.1927 | 7 | -1,402.46 | `3ecbc041d3483246` |
| 0.005 | 0.2 | 202 | 694 | 0.8098 | 0.8012 | 0.8902 | 0.1330 / 0.2550 | 0.2340 | 0.6204 | 0.3796 | 0.7601 | -4.92 | 0.9585 | 0.0 | 0.2491 | 7 | -1,400.75 | `a8f9ff73c6e1c011` |
| 0.005 | 0.3 | 202 | 694 | 0.7017 | 0.6883 | 0.7919 | 0.1890 / 0.3620 | 0.3060 | 0.5875 | 0.4125 | 0.6128 | 72.81 | 0.3898 | 0.0 | 0.4037 | 8 | -1,371.38 | `a2a5991fa224217e` |
| 0.01 | 0.05 | 202 | 694 | 0.9553 | 0.9533 | 0.9769 | 0.0240 / 0.1140 | 0.0870 | 0.6671 | 0.3329 | 0.9438 | 46.39 | 0.7891 | 2.8 | 0.0583 | 6 | -1,396.97 | `c0a461ea1b0cdc0c` |
| 0.01 | 0.1 | 202 | 694 | 0.9092 | 0.9051 | 0.9422 | 0.0580 / 0.1780 | 0.1640 | 0.6461 | 0.3539 | 0.8720 | 55.44 | 0.6252 | 0.9 | 0.1349 | 7 | -1,392.47 | `5104318d0e90d3d8` |
| 0.01 | 0.15 | 202 | 694 | 0.8631 | 0.8569 | 0.9133 | 0.0920 / 0.2410 | 0.2410 | 0.6187 | 0.3813 | 0.8259 | 1.38 | 0.9880 | 0.0 | 0.1809 | 7 | -1,399.33 | `5e25d457c97d75fa` |
| 0.01 | 0.2 | 202 | 694 | 0.8112 | 0.8027 | 0.8728 | 0.1160 / 0.2920 | 0.2780 | 0.6017 | 0.3983 | 0.7657 | 8.59 | 0.9290 | 0.0 | 0.2427 | 7 | -1,397.56 | `7947bd3ca9b54544` |
| 0.01 | 0.3 | 202 | 694 | 0.7032 | 0.6898 | 0.7514 | 0.1480 / 0.4240 | 0.3220 | 0.5809 | 0.4191 | 0.6116 | 91.40 | 0.2729 | 0.0 | 0.4053 | 8 | -1,364.08 | `929eb639a3182d99` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.0993 | 1,847.41 | 0.7624 | 0.2139 | 0.8726 | -387,339.93 | 1,682,819.58 | -387,339.93 | -1,228,749.72 | -2,070,159.51 | -876.33 | 147.96 | -1,266.30 | -1,761.14 | yes | `0a17ab5c018a8b54` |
| 0.15 | 0.1456 | 1,834.15 | 0.7901 | 0.2649 | 0.8163 | -651,809.65 | 1,573,667.49 | -651,809.65 | -1,438,643.40 | -2,225,477.14 | -1,005.88 | 4.36 | -1,395.84 | -1,892.74 | yes | `9f4ed78452c79ad7` |
| 0.2 | 0.2028 | 1,770.91 | 0.7940 | 0.3440 | 0.7538 | -897,041.66 | 1,404,415.27 | -897,041.66 | -1,599,249.29 | -2,301,456.93 | -993.40 | 20.33 | -1,383.37 | -1,888.09 | yes | `a592187258853456` |
| 0.25 | 0.2525 | 1,733.31 | 0.7989 | 0.4298 | 0.7012 | -1,062,396.49 | 1,220,645.16 | -1,062,396.49 | -1,672,719.07 | -2,283,041.65 | -945.19 | 86.17 | -1,335.16 | -1,838.05 | yes | `432c762189395a19` |
| 0.3 | 0.3003 | 1,709.98 | 0.8003 | 0.4786 | 0.6503 | -1,295,978.22 | 1,116,149.97 | -1,295,978.22 | -1,854,053.21 | -2,412,128.19 | -969.32 | 57.58 | -1,359.28 | -1,861.09 | yes | `f10688d72326a049` |
| 0.35 | 0.3518 | 1,678.44 | 0.7989 | 0.5549 | 0.5987 | -1,474,932.66 | 952,902.63 | -1,474,932.66 | -1,951,383.97 | -2,427,835.29 | -941.85 | 104.53 | -1,331.81 | -1,836.93 | yes | `cc9256cfda1ec240` |
| 0.4 | 0.4009 | 1,654.70 | 0.8028 | 0.6091 | 0.5497 | -1,684,071.70 | 836,842.67 | -1,684,071.70 | -2,102,493.04 | -2,520,914.37 | -943.46 | 110.42 | -1,333.42 | -1,831.93 | yes | `c1dc0fb650bdfcd7` |
| 0.45 | 0.4524 | 1,633.73 | 0.8098 | 0.6571 | 0.4990 | -1,917,959.33 | 734,032.55 | -1,917,959.33 | -2,284,975.60 | -2,651,991.88 | -952.31 | 104.62 | -1,342.28 | -1,843.04 | yes | `6fc7e74d87325b8f` |
| 0.5 | 0.5018 | 1,615.04 | 0.8124 | 0.6826 | 0.4511 | -2,180,992.14 | 679,403.51 | -2,180,992.14 | -2,520,693.90 | -2,860,395.65 | -976.27 | 66.91 | -1,366.24 | -1,860.81 | yes | `3a5e27e23960bd40` |
| 0.55 | 0.5460 | 1,615.50 | 0.8161 | 0.7336 | 0.4030 | -2,391,080.83 | 570,217.91 | -2,391,080.83 | -2,676,189.79 | -2,961,298.74 | -983.58 | 57.34 | -1,373.54 | -1,869.23 | yes | `2a8091bdd978acf4` |
| 0.6 | 0.5946 | 1,601.48 | 0.8160 | 0.7925 | 0.3559 | -2,577,479.11 | 444,220.78 | -2,577,479.11 | -2,799,589.50 | -3,021,699.89 | -973.74 | 88.48 | -1,363.70 | -1,869.31 | yes | `0d96f25ba8250f67` |
| 0.65 | 0.6498 | 1,578.85 | 0.8220 | 0.8109 | 0.3064 | -2,866,595.28 | 404,840.73 | -2,866,595.28 | -3,069,015.64 | -3,271,436.01 | -990.87 | 53.50 | -1,380.84 | -1,896.88 | yes | `d7b00f47e80e7133` |
| 0.7 | 0.6923 | 1,563.66 | 0.8248 | 0.8393 | 0.2685 | -3,057,353.75 | 344,019.21 | -3,057,353.75 | -3,229,363.35 | -3,401,372.96 | -992.00 | 57.21 | -1,381.97 | -1,897.04 | yes | `a6ff4abe3e8e3cc7` |
| 0.75 | 0.7394 | 1,544.46 | 0.8290 | 0.8568 | 0.2285 | -3,285,056.30 | 306,560.59 | -3,285,056.30 | -3,438,336.60 | -3,591,616.89 | -997.89 | 44.97 | -1,387.86 | -1,900.91 | yes | `e88477d5c0480c39` |
| 0.8 | 0.7956 | 1,527.29 | 0.8340 | 0.8766 | 0.1795 | -3,567,902.78 | 264,109.24 | -3,567,902.78 | -3,699,957.40 | -3,832,012.02 | -1,007.31 | 11.23 | -1,397.28 | -1,905.67 | yes | `9b10aa2de45026f9` |
| 0.85 | 0.8488 | 1,513.97 | 0.8394 | 0.8918 | 0.1325 | -3,847,077.22 | 231,647.82 | -3,847,077.22 | -3,962,901.13 | -4,078,725.04 | -1,018.01 | -55.61 | -1,407.98 | -1,914.08 | yes | `288f2d3ddf06fbc4` |
| 0.9 | 0.8951 | 1,505.92 | 0.8419 | 0.9308 | 0.0904 | -4,043,302.68 | 148,087.01 | -4,043,302.68 | -4,117,346.18 | -4,191,389.69 | -1,014.63 | -47.89 | -1,404.60 | -1,910.79 | yes | `01ad102b9afb1307` |
| 0.95 | 0.9508 | 1,491.15 | 0.8420 | 0.9753 | 0.0435 | -4,259,057.10 | 52,885.82 | -4,259,057.10 | -4,285,500.01 | -4,311,942.92 | -1,006.16 | 70.17 | -1,396.12 | -1,901.12 | yes | `e981d58fb50ca035` |
| 1.0 | 1.0000 | 1,482.62 | 0.8441 | 1.0000 | -0.0000 | -4,494,772.79 | 0.00 | -4,494,772.79 | -4,494,772.79 | -4,494,772.79 | -1,009.61 | - | - | -1,905.01 | yes | `f3902b0de78e71fc` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.1, w = 1 -> 0.1. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4359 | 0.0505 | 755.13 | 781.23 | 65 |
| 0.1 | 0.4756 | 0.1003 | 1,169.91 | 1,193.94 | 112 |
| 0.15 | 0.4927 | 0.1576 | 1,345.91 | 1,369.06 | 142 |
| 0.2 | 0.5025 | 0.2100 | 1,428.48 | 1,451.22 | 160 |
| 0.25 | 0.5141 | 0.2542 | 1,497.52 | 1,519.92 | 170 |
| 0.3 | 0.5252 | 0.3009 | 1,539.75 | 1,561.94 | 179 |
| 0.35 | 0.5264 | 0.3502 | 1,534.41 | 1,556.63 | 183 |
| 0.4 | 0.5450 | 0.4069 | 1,520.65 | 1,542.93 | 189 |
| 0.45 | 0.5488 | 0.4517 | 1,488.96 | 1,511.40 | 190 |
| 0.5 | 0.5663 | 0.5034 | 1,491.81 | 1,514.24 | 193 |
| 0.55 | 0.5770 | 0.5713 | 1,510.89 | 1,533.23 | 197 |
| 0.6 | 0.5873 | 0.6000 | 1,507.17 | 1,529.52 | 198 |
| 0.65 | 0.5980 | 0.6579 | 1,518.29 | 1,540.58 | 199 |
| 0.7 | 0.6017 | 0.7053 | 1,506.82 | 1,529.18 | 199 |
| 0.75 | 0.6232 | 0.7502 | 1,495.57 | 1,517.98 | 199 |
| 0.8 | 0.6326 | 0.8044 | 1,482.64 | 1,505.12 | 199 |
| 0.85 | 0.6573 | 0.8523 | 1,469.19 | 1,491.74 | 200 |
| 0.9 | 0.6771 | 0.9196 | 1,453.58 | 1,476.20 | 200 |
| 0.95 | 0.6869 | 0.9502 | 1,443.33 | 1,466.00 | 200 |
| 1.0 | - | 1.0000 | 1,435.99 | 1,458.70 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.05 | 0.4359 | 781.23 | 1,729.46 | 0.0379 | 2,029.91 | 0.0425 | 249.89 | 0.0 | -1,160.29 | `2ae774587330de07` |
| 1000.0 | 0.05 | 0.4359 | 781.23 | 1,729.46 | 0.0379 | 2,029.91 | 0.0425 | 249.89 | 0.0 | -1,160.29 | `bd3864bf3e52902c` |
| 1200.0 | 0.1 | 0.4756 | 1,193.94 | 1,645.61 | 0.1033 | 1,848.19 | 0.1022 | 120.28 | 0.0 | -1,291.59 | `9e8499e7dd81e646` |

Per-bin certificates (minute only):

| alpha (INR) | lambda* 09:15-10:29 | lambda* 10:30-12:59 | lambda* 13:00-15:19 | realised risk before the block | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.15 (cert 747.92; n 159, slack 37.50) | 0.15 (cert 794.11; n 146, slack 40.82) | 0.15 (cert 764.50; n 158, slack 37.74) | 1,634.87 | 0.1503 | -96.36 | 0.0 | -1,481.45 | `3b181f391b7179d4` |
| 1000.0 | 0.2 (cert 913.73; n 159, slack 37.50) | 0.3 (cert 996.11; n 146, slack 40.82) | 0.25 (cert 984.28; n 158, slack 37.74) | 1,580.57 | 0.2740 | -102.80 | 0.0 | -1,474.20 | `b923ee423823e972` |
| 1200.0 | 0.3 (cert 1,159.96; n 159, slack 37.50) | 0.4 (cert 1,091.59; n 146, slack 40.82) | 0.4 (cert 1,179.16; n 158, slack 37.74) | 1,540.80 | 0.3996 | -45.77 | 0.0 | -1,427.05 | `9a1e7d26ea26dbde` |

#### (5) Cost sensitivity of every kept book of this model: 45 books; kept mean > 0 at 8 pts slippage: **0** (best -1,160.29); at 3 pts: 0 (best -510.35); with uncapped 0.03% brokerage (+895.40 INR/trade): best kept mean -1,676.26. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### minute family multiplicity (every `operating_point/*` ledger row of the timeframe with a defined diff)

| rows | by family | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|
| 174 | {'operating_point/aci': 40, 'operating_point/conformal': 20, 'operating_point/conformal_timebin': 20, 'operating_point/coverage': 72, 'operating_point/crc': 10, 'operating_point/crc_timebin': 12} | 0.5469 | 0.4709 | 0.5273 | 0.9245 | 0.9685 | 32.28 (1.164) | 0 | 0.9305 | 1.72 |

Best controlled row by diff: operating_point/crc `2ae774587330de07` config {'tf': 'minute', 'sub': 'h5_full', 'model': 'scorecard', 'vocabulary': 'outside the frozen shortlist (importance rule failed for every cluster)', 'score': '1 - p_oof', 'step': 'crc', 'alpha_inr': 800.0, 'coverage_lambda': 0.05, 'calibration_sessions': 200, 'B': 6000.0}: diff 249.89, control pct 0.0, kept share 0.0425, kept mean slip8 -1,160.29, bootstrap 90% CI of diff [-483.52, 1061.13], DSR p 1.0 (n_trials 174); `harness.go_no_go` **FAIL**:

| item | ok | value |
|---|---|---|
| kept_share>=20% | no | 0.0425 |
| kept_n>=300 | no | 189 |
| diff>0 | yes | 249.89 |
| diff_top1_removed>0 | no | -129.88 |
| kept_mean_slip8>0 | no | -1160.29 |
| sign_blocks>=8/12 | no | 7 |
| control_pct>=95 | no | 0.0 |
| pbo<=0.2 | no | 0.5469 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | no | 0.9245 |
| boot_ci_excludes_0 | no | [-483.52, 1061.13] |
| null_tape:evaluated | no | not run: this step adds no candidate (it re-parameterises a gate_family score; gate_family wrote no candidate) |
| no_time_proxy_columns | yes | 183 columns |

### minute candidate: **none** (this step adds no candidate by design; the null-tape item reads 'not run' for that reason)

## 4. 5minute (L1: IS units 826, mean -757.05 INR/trade, win rate 0.2772, winners 229, active sessions 408, mean cost 1,049.86; uncapped brokerage adds 901.57 per trade; winners per time bin {'09:15-10:29': 71, '10:30-12:59': 60, '13:00-15:19': 98})

### 5minute / context/hgbc - probability learner of sub-family (I) (its finalist pt2 is a policy tree with no score) - inside the frozen vocabulary (context columns)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9476 | 0.9892 | 0.7500 / 1.0000 | 4 / 1 | 0.9383 | -750.78 | -852.36 | 101.58 | -129.46 | 0.8731 | 0.0 | 0.0653 | 0.0000 | 8 | -490.80 | -1,140.75 | -1,654.50 | 0.9685 | `5b19f07e3fff4ad6` |
| 0.1 | 0.90 | 0.80 | 0.9039 | 0.9077 | 0.7500 / 1.0000 | 4 / 2 | 0.9019 | -810.52 | -265.29 | -545.22 | -507.08 | 0.2894 | 1.6 | 0.0988 | 0.1304 | 7 | -550.54 | -1,200.48 | -1,712.69 | 0.9758 | `b80cdcc7605d8fb5` |
| 0.15 | 0.85 | 0.70 | 0.8472 | 0.8498 | 0.7143 / 1.0000 | 5 / 0 | 0.8232 | -772.73 | -684.01 | -88.72 | -180.35 | 0.8251 | 52.5 | 0.1859 | 0.2174 | 9 | -512.76 | -1,162.70 | -1,670.66 | 0.8971 | `2d0e587363b4c3c9` |
| 0.2 | 0.80 | 0.60 | 0.8035 | 0.7698 | 0.4615 / 0.9375 | 5 / 1 | 0.7869 | -868.64 | -344.95 | -523.68 | -513.93 | 0.1609 | 44.0 | 0.2194 | 0.3478 | 8 | -608.66 | -1,258.60 | -1,767.93 | 0.8608 | `9b5278ce21328fe0` |
| 0.3 | 0.70 | 0.40 | 0.6987 | 0.6569 | 0.3846 / 0.8889 | 6 / 1 | 0.6816 | -864.05 | -528.00 | -336.05 | -433.17 | 0.3203 | 50.5 | 0.3250 | 0.3913 | 6 | -604.07 | -1,254.01 | -1,758.37 | 0.7554 | `d9c5e0f1dabcaa35` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05]; chosen **0.05** (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9).

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 203 | 0.7041 | 82 | 26 | 0.9634 | 0.9615 | 0.9935 | 0.0357 |
| 1 | 202 | 0.6727 | 83 | 27 | 0.8434 | 0.8889 | 0.9401 | 0.1786 |
| 2 | 212 | 0.7041 | 42 | 17 | 0.8810 | 0.9412 | 0.9468 | 0.1600 |
| 3 | 209 | 0.6469 | 76 | 20 | 0.8684 | 0.7500 | 0.8995 | 0.0893 |
| 4 | 208 | 0.7041 | 72 | 21 | 0.9167 | 0.9048 | 0.9933 | 0.0784 |
| 5 | 213 | 0.7041 | 73 | 16 | 0.9315 | 1.0000 | 1.0000 | 0.0877 |
| 6 | 216 | 0.7041 | 77 | 13 | 0.9221 | 0.9231 | 0.9932 | 0.0781 |
| 7 | 216 | 0.7041 | 51 | 13 | 0.9412 | 1.0000 | 1.0000 | 0.0789 |
| 8 | 208 | 0.6575 | 76 | 21 | 0.8421 | 0.7619 | 0.6336 | 0.1273 |
| 9 | 213 | 0.6727 | 80 | 16 | 0.8375 | 0.8125 | 0.7578 | 0.1562 |
| 10 | 220 | 0.7041 | 31 | 9 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 11 | 199 | 0.7041 | 83 | 30 | 0.9398 | 0.9667 | 0.9910 | 0.0755 |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 96 | 229 | 0.9651 | 0.9598 | 0.9649 | 0.0503 / 0.0680 | 0.0673 | 0.7385 | 0.2615 | 0.9516 | 215.86 | 0.7611 | 0.1 | 0.0536 | 5 | -1,136.56 | `7d12d6ecc09dfd2b` |
| 0.005 | 0.1 | 96 | 229 | 0.9039 | 0.8894 | 0.9123 | 0.0880 / 0.1165 | 0.1045 | 0.6727 | 0.3273 | 0.9128 | -888.11 | 0.1134 | 2.8 | 0.0838 | 6 | -1,224.43 | `9a0705878aa63b66` |
| 0.005 | 0.15 | 96 | 229 | 0.8472 | 0.8241 | 0.8070 | 0.1447 / 0.1817 | 0.1467 | 0.6245 | 0.3755 | 0.8293 | -89.93 | 0.8171 | 37.0 | 0.1776 | 7 | -1,162.37 | `26c59ff049b70648` |
| 0.005 | 0.2 | 96 | 229 | 0.7948 | 0.7638 | 0.7719 | 0.1910 / 0.2490 | 0.1940 | 0.6065 | 0.3935 | 0.7627 | -30.28 | 0.9420 | 65.3 | 0.2496 | 6 | -1,154.20 | `625b5ce652333ac0` |
| 0.005 | 0.3 | 96 | 229 | 0.6900 | 0.6432 | 0.5614 | 0.2845 / 0.3685 | 0.2885 | 0.5728 | 0.4272 | 0.6671 | -67.21 | 0.8501 | 22.3 | 0.3417 | 6 | -1,169.39 | `11d478ceb6d7510e` |
| 0.01 | 0.05 | 96 | 229 | 0.9607 | 0.9548 | 0.9649 | 0.0420 / 0.0760 | 0.0745 | 0.7355 | 0.2645 | 0.9492 | 178.23 | 0.8026 | 0.1 | 0.0553 | 5 | -1,137.95 | `ef582aef86e25a51` |
| 0.01 | 0.1 | 96 | 229 | 0.9039 | 0.8894 | 0.9298 | 0.0760 / 0.1330 | 0.1090 | 0.6575 | 0.3425 | 0.9128 | -1,086.54 | 0.0570 | 0.0 | 0.0838 | 6 | -1,241.73 | `84a90ef2f2108255` |
| 0.01 | 0.15 | 96 | 229 | 0.8472 | 0.8241 | 0.8246 | 0.1390 / 0.2135 | 0.1435 | 0.6245 | 0.3755 | 0.8196 | -28.21 | 0.9495 | 47.0 | 0.1910 | 8 | -1,152.11 | `f72d5a8b7b6fcec6` |
| 0.01 | 0.2 | 96 | 229 | 0.7904 | 0.7588 | 0.7895 | 0.1720 / 0.2900 | 0.1780 | 0.6145 | 0.3855 | 0.7591 | -20.22 | 0.9585 | 69.0 | 0.2529 | 7 | -1,151.89 | `66eca8117d699595` |
| 0.01 | 0.3 | 96 | 229 | 0.6812 | 0.6332 | 0.5965 | 0.2390 / 0.4270 | 0.2570 | 0.5808 | 0.4192 | 0.6550 | -90.46 | 0.7906 | 32.8 | 0.3551 | 4 | -1,178.23 | `990ee4ac1a85a40a` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.0944 | 2,859.30 | 0.7692 | 0.0751 | 0.8652 | -150,562.91 | 1,025,649.86 | -150,562.91 | -663,387.84 | -1,176,212.77 | -1,930.29 | -1,295.58 | -2,320.26 | -2,901.01 | yes | `c2e611a5067dcc42` |
| 0.15 | 0.1453 | 2,546.60 | 0.7667 | 0.0927 | 0.8176 | -213,616.05 | 1,006,136.67 | -213,616.05 | -716,684.39 | -1,219,752.72 | -1,780.13 | -1,196.98 | -2,170.10 | -2,693.03 | yes | `44ea83a5778af232` |
| 0.2 | 0.2082 | 2,492.67 | 0.7616 | 0.1623 | 0.7461 | -260,234.33 | 928,910.45 | -260,234.33 | -724,689.55 | -1,189,144.78 | -1,512.99 | -954.75 | -1,902.96 | -2,428.64 | yes | `621e4ac7402482fb` |
| 0.25 | 0.2530 | 2,371.27 | 0.7512 | 0.2250 | 0.6975 | -275,013.13 | 859,368.33 | -275,013.13 | -704,697.29 | -1,134,381.46 | -1,315.85 | -748.09 | -1,705.82 | -2,219.04 | yes | `971574cca6a1ddff` |
| 0.3 | 0.3015 | 2,267.61 | 0.7229 | 0.3046 | 0.6575 | -256,213.46 | 771,154.04 | -256,213.46 | -641,790.48 | -1,027,367.50 | -1,028.97 | -389.26 | -1,418.93 | -1,938.03 | yes | `fde992ea842c61fb` |
| 0.35 | 0.3402 | 2,195.87 | 0.7082 | 0.3488 | 0.6273 | -259,565.02 | 722,099.89 | -259,565.02 | -620,614.96 | -981,664.91 | -923.72 | -252.60 | -1,313.68 | -1,831.36 | yes | `3bf0b6ffb4d7f6bf` |
| 0.4 | 0.3959 | 2,116.71 | 0.6972 | 0.3955 | 0.5840 | -282,914.55 | 670,325.75 | -282,914.55 | -618,077.43 | -953,240.30 | -865.18 | -178.99 | -1,255.15 | -1,771.77 | yes | `9b8746ac04601f47` |
| 0.45 | 0.4479 | 2,063.21 | 0.6946 | 0.4557 | 0.5429 | -287,409.49 | 603,594.77 | -287,409.49 | -589,206.88 | -891,004.26 | -776.78 | -35.74 | -1,166.75 | -1,683.21 | yes | `489012292ed51b49` |
| 0.5 | 0.4988 | 2,088.64 | 0.7039 | 0.4910 | 0.4869 | -345,382.88 | 564,439.67 | -345,382.88 | -627,602.71 | -909,822.55 | -838.31 | -162.12 | -1,228.27 | -1,745.94 | yes | `28b51ea63e3cdb16` |
| 0.55 | 0.5508 | 2,104.44 | 0.7055 | 0.5505 | 0.4300 | -378,041.26 | 498,411.70 | -378,041.26 | -627,247.11 | -876,452.96 | -830.86 | -164.33 | -1,220.82 | -1,743.04 | yes | `d44ef08a2b452d64` |
| 0.6 | 0.6077 | 2,123.82 | 0.7151 | 0.6035 | 0.3647 | -432,501.76 | 439,672.95 | -432,501.76 | -652,338.23 | -872,174.71 | -861.56 | -266.42 | -1,251.52 | -1,761.21 | yes | `791d0dd33f74af9d` |
| 0.65 | 0.6513 | 2,089.15 | 0.7119 | 0.6424 | 0.3314 | -447,166.52 | 396,531.68 | -447,166.52 | -645,432.36 | -843,698.20 | -831.16 | -212.56 | -1,221.13 | -1,727.86 | yes | `d947c3bbe485e842` |
| 0.7 | 0.6985 | 2,103.33 | 0.7158 | 0.6734 | 0.2781 | -505,167.15 | 362,212.67 | -505,167.15 | -686,273.48 | -867,379.82 | -875.51 | -392.94 | -1,265.47 | -1,770.28 | yes | `d668487e660c5b5d` |
| 0.75 | 0.7482 | 2,095.29 | 0.7152 | 0.7364 | 0.2313 | -516,529.00 | 292,303.69 | -516,529.00 | -662,680.84 | -808,832.69 | -835.81 | -312.75 | -1,225.77 | -1,731.25 | yes | `195f7ab5a07795cc` |
| 0.8 | 0.7869 | 2,119.09 | 0.7169 | 0.7698 | 0.1822 | -564,613.37 | 255,224.33 | -564,613.37 | -692,225.54 | -819,837.70 | -868.64 | -523.68 | -1,258.60 | -1,767.93 | yes | `f70935afec9b2277` |
| 0.85 | 0.8450 | 2,102.41 | 0.7149 | 0.8701 | 0.1289 | -545,707.75 | 144,004.65 | -545,707.75 | -617,710.08 | -689,712.40 | -781.82 | -159.81 | -1,171.78 | -1,682.80 | yes | `35a0f426cd18e28d` |
| 0.9 | 0.9007 | 2,105.26 | 0.7218 | 0.9077 | 0.0720 | -602,877.33 | 102,346.00 | -602,877.33 | -654,050.33 | -705,223.33 | -810.32 | -536.56 | -1,200.28 | -1,712.55 | yes | `e8c749140c30708e` |
| 0.95 | 0.9492 | 2,089.14 | 0.7168 | 0.9963 | 0.0288 | -579,523.51 | 4,097.17 | -579,523.51 | -581,572.09 | -583,620.68 | -739.19 | 351.33 | -1,129.15 | -1,641.31 | yes | `d29b3078ad307593` |
| 1.0 | 1.0000 | 2,043.33 | 0.7228 | 1.0000 | -0.0000 | -625,325.16 | 0.00 | -625,325.16 | -625,325.16 | -625,325.16 | -757.05 | - | - | -1,658.62 | yes | `9bd6357b38dfb7ee` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.95, w = 1 -> 0.95. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4208 | 0.0515 | 338.86 | 367.03 | 21 |
| 0.1 | 0.4312 | 0.1054 | 578.37 | 605.34 | 40 |
| 0.15 | 0.4555 | 0.1642 | 838.79 | 864.46 | 63 |
| 0.2 | 0.4636 | 0.2034 | 925.07 | 950.32 | 75 |
| 0.25 | 0.4749 | 0.2574 | 1,137.68 | 1,161.87 | 89 |
| 0.3 | 0.4924 | 0.3088 | 1,297.16 | 1,320.56 | 107 |
| 0.35 | 0.4965 | 0.3505 | 1,371.62 | 1,394.65 | 119 |
| 0.4 | 0.5042 | 0.4044 | 1,521.82 | 1,544.10 | 132 |
| 0.45 | 0.5185 | 0.4559 | 1,538.56 | 1,560.76 | 137 |
| 0.5 | 0.5270 | 0.5000 | 1,648.67 | 1,670.32 | 147 |
| 0.55 | 0.5310 | 0.5564 | 1,742.66 | 1,763.84 | 152 |
| 0.6 | 0.5425 | 0.6029 | 1,749.99 | 1,771.13 | 156 |
| 0.65 | 0.5728 | 0.6618 | 1,804.30 | 1,825.17 | 163 |
| 0.7 | 0.5905 | 0.7083 | 1,795.02 | 1,815.94 | 168 |
| 0.75 | 0.5979 | 0.7500 | 1,810.82 | 1,831.66 | 172 |
| 0.8 | 0.6202 | 0.7990 | 1,828.10 | 1,848.86 | 180 |
| 0.85 | 0.6309 | 0.8480 | 1,835.25 | 1,855.97 | 185 |
| 0.9 | 0.6752 | 0.9020 | 1,919.73 | 1,940.03 | 190 |
| 0.95 | 0.7385 | 0.9510 | 1,954.79 | 1,974.91 | 197 |
| 1.0 | - | 1.0000 | 1,943.64 | 1,963.82 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.1 | 0.4312 | 605.34 | 2,723.78 | 0.0574 | 2,826.23 | 0.0811 | -1,290.42 | 0.2 | -2,332.77 | `7b4c137696915466` |
| 1000.0 | 0.2 | 0.4636 | 950.32 | 2,280.25 | 0.1866 | 2,423.90 | 0.1949 | -767.23 | 1.4 | -1,764.70 | `53f9b6270baee739` |
| 1200.0 | 0.25 | 0.4749 | 1,161.87 | 2,148.24 | 0.2321 | 2,388.94 | 0.2446 | -925.61 | 0.5 | -1,846.27 | `5280a2aa93ca87c4` |

#### (5) Cost sensitivity of every kept book of this model: 37 books; kept mean > 0 at 8 pts slippage: **0** (best -1,129.15); at 3 pts: 0 (best -479.21); with uncapped 0.03% brokerage (+901.57 INR/trade): best kept mean -1,641.31. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### 5minute / context/scorecard - the deployable scorecard of sub-family (I) - inside the frozen vocabulary (context columns)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9476 | 0.9505 | 0.7143 / 1.0000 | 5 / 2 | 0.9370 | -729.63 | -1,165.19 | 435.56 | 638.03 | 0.5037 | 99.8 | 0.0670 | 0.0435 | 3 | -469.66 | -1,119.60 | -1,638.60 | 0.9540 | `f06ba77e637b3c42` |
| 0.1 | 0.90 | 0.80 | 0.8996 | 0.9046 | 0.4706 / 1.0000 | 3 / 2 | 0.9019 | -739.07 | -922.41 | 183.34 | 227.19 | 0.7371 | 99.8 | 0.0972 | 0.0870 | 6 | -479.10 | -1,129.04 | -1,648.21 | 0.9189 | `153e362fd9eadc39` |
| 0.15 | 0.85 | 0.70 | 0.8297 | 0.8568 | 0.4706 / 1.0000 | 4 / 2 | 0.8559 | -767.76 | -693.43 | -74.34 | -126.83 | 0.8756 | 72.5 | 0.1340 | 0.0870 | 6 | -507.79 | -1,157.73 | -1,677.22 | 0.8729 | `3c9460d8e5d96276` |
| 0.2 | 0.80 | 0.60 | 0.7860 | 0.7963 | 0.4231 / 1.0000 | 4 / 2 | 0.8063 | -775.65 | -679.64 | -96.01 | -54.97 | 0.8201 | 91.8 | 0.1859 | 0.2174 | 7 | -515.67 | -1,165.62 | -1,688.87 | 0.8232 | `436ec6a35392a535` |
| 0.3 | 0.70 | 0.40 | 0.6987 | 0.7473 | 0.3333 / 1.0000 | 5 / 1 | 0.7228 | -738.01 | -806.70 | 68.70 | 10.98 | 0.8481 | 64.8 | 0.2680 | 0.2174 | 7 | -478.03 | -1,127.97 | -1,651.26 | 0.7397 | `58c8dd23f312496d` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05]; chosen **0.05** (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9).

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 203 | 0.5582 | 82 | 26 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 1 | 202 | 0.5582 | 83 | 27 | 0.9157 | 0.8889 | 0.8180 | 0.0714 |
| 2 | 212 | 0.5570 | 42 | 17 | 0.6190 | 0.4706 | 0.4417 | 0.2800 |
| 3 | 209 | 0.5582 | 76 | 20 | 0.9605 | 1.0000 | 1.0000 | 0.0536 |
| 4 | 208 | 0.5570 | 72 | 21 | 0.5694 | 0.7143 | 0.7682 | 0.4902 |
| 5 | 213 | 0.5582 | 73 | 16 | 0.9178 | 0.9375 | 0.9283 | 0.0877 |
| 6 | 216 | 0.5582 | 77 | 13 | 0.9870 | 1.0000 | 1.0000 | 0.0156 |
| 7 | 216 | 0.5582 | 51 | 13 | 0.9216 | 0.9231 | 0.8863 | 0.0789 |
| 8 | 208 | 0.5582 | 76 | 21 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 9 | 213 | 0.5582 | 80 | 16 | 0.9625 | 1.0000 | 1.0000 | 0.0469 |
| 10 | 220 | 0.5582 | 31 | 9 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 11 | 199 | 0.5582 | 83 | 30 | 0.8795 | 0.9000 | 0.8633 | 0.1321 |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 96 | 229 | 0.9563 | 0.9497 | 1.0000 | 0.0333 / 0.0605 | 0.0573 | 0.5669 | 0.4331 | 0.9540 | 82.30 | 0.9150 | 99.5 | 0.0469 | 3 | -1,143.23 | `183462c51c17ebc8` |
| 0.005 | 0.1 | 96 | 229 | 0.9258 | 0.9146 | 0.9474 | 0.0915 / 0.1365 | 0.1295 | 0.557 | 0.4430 | 0.9165 | 353.01 | 0.5182 | 100.0 | 0.0871 | 6 | -1,117.53 | `a39d5ddc448b383f` |
| 0.005 | 0.15 | 96 | 229 | 0.8646 | 0.8442 | 0.7719 | 0.1497 / 0.2042 | 0.1668 | 0.5516 | 0.4484 | 0.8741 | 117.74 | 0.7976 | 98.5 | 0.1223 | 6 | -1,132.19 | `5d7fcde76c6ca919` |
| 0.005 | 0.2 | 96 | 229 | 0.8341 | 0.8090 | 0.6842 | 0.2010 / 0.2850 | 0.2390 | 0.5436 | 0.4564 | 0.8414 | 333.95 | 0.4378 | 98.5 | 0.1558 | 8 | -1,094.05 | `a803528dc0659027` |
| 0.005 | 0.3 | 96 | 229 | 0.7380 | 0.6985 | 0.4737 | 0.3015 / 0.4155 | 0.3435 | 0.5369 | 0.4631 | 0.7554 | 92.63 | 0.8101 | 82.5 | 0.2379 | 6 | -1,124.36 | `d2f469c6a836213d` |
| 0.01 | 0.05 | 96 | 229 | 0.9563 | 0.9497 | 0.9825 | 0.0265 / 0.0710 | 0.0645 | 0.5669 | 0.4331 | 0.9588 | -185.98 | 0.8091 | 99.7 | 0.0402 | 3 | -1,154.67 | `0c8b88db402f02a3` |
| 0.01 | 0.1 | 96 | 229 | 0.9170 | 0.9045 | 0.9123 | 0.0830 / 0.1630 | 0.1390 | 0.5521 | 0.4479 | 0.9092 | 353.99 | 0.5132 | 99.7 | 0.0938 | 6 | -1,114.88 | `65e59f5b062b6d7b` |
| 0.01 | 0.15 | 96 | 229 | 0.8559 | 0.8342 | 0.7368 | 0.1495 / 0.2450 | 0.1635 | 0.5516 | 0.4484 | 0.8668 | 48.99 | 0.9255 | 97.3 | 0.1290 | 6 | -1,140.49 | `85c377da0bcc68c1` |
| 0.01 | 0.2 | 96 | 229 | 0.8079 | 0.7789 | 0.6316 | 0.2020 / 0.3240 | 0.2180 | 0.5436 | 0.4564 | 0.8196 | 165.48 | 0.6827 | 93.5 | 0.1759 | 7 | -1,117.17 | `b2159527f8b58a9f` |
| 0.01 | 0.3 | 96 | 229 | 0.7162 | 0.6734 | 0.4737 | 0.3030 / 0.4810 | 0.3370 | 0.5387 | 0.4613 | 0.7264 | 244.36 | 0.4938 | 74.9 | 0.2697 | 6 | -1,080.16 | `9324a7ea929bcb91` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.0969 | 1,567.04 | 0.6875 | 0.1030 | 0.9267 | -12,878.37 | 994,763.24 | -12,878.37 | -510,259.99 | -1,007,641.61 | -160.98 | 659.99 | -550.95 | -1,050.70 | yes | `c31c8a75f860f1e8` |
| 0.15 | 0.1525 | 1,664.02 | 0.6984 | 0.1537 | 0.8781 | -40,882.60 | 938,464.36 | -40,882.60 | -510,114.78 | -979,346.96 | -324.47 | 510.45 | -714.43 | -1,219.48 | yes | `b58579c19dbb147b` |
| 0.2 | 0.1949 | 1,708.60 | 0.7267 | 0.1726 | 0.8404 | -85,421.33 | 917,584.85 | -85,421.33 | -544,213.76 | -1,003,006.18 | -530.57 | 281.32 | -920.53 | -1,417.65 | yes | `b580b1c68f16703a` |
| 0.25 | 0.2663 | 1,838.23 | 0.7364 | 0.2360 | 0.7655 | -144,949.77 | 847,191.43 | -144,949.77 | -568,545.48 | -992,141.20 | -658.86 | 133.84 | -1,048.83 | -1,591.90 | yes | `b18774e063888ff8` |
| 0.3 | 0.3002 | 1,898.90 | 0.7419 | 0.2867 | 0.7252 | -158,707.43 | 791,037.96 | -158,707.43 | -554,226.41 | -949,745.39 | -639.95 | 167.35 | -1,029.91 | -1,569.79 | yes | `7d2a983bf5b931ed` |
| 0.35 | 0.3608 | 1,914.45 | 0.7349 | 0.3248 | 0.6675 | -216,484.13 | 748,697.31 | -216,484.13 | -590,832.78 | -965,181.44 | -726.46 | 47.86 | -1,116.42 | -1,629.62 | yes | `b7f1a453d2df52c6` |
| 0.4 | 0.4128 | 1,954.10 | 0.7390 | 0.3926 | 0.6120 | -237,595.56 | 673,558.11 | -237,595.56 | -574,374.61 | -911,153.67 | -696.76 | 102.68 | -1,086.73 | -1,604.52 | yes | `034310a213618161` |
| 0.45 | 0.4516 | 1,966.12 | 0.7373 | 0.4351 | 0.5726 | -258,607.84 | 626,389.25 | -258,607.84 | -571,802.46 | -884,997.09 | -693.32 | 116.21 | -1,083.28 | -1,586.32 | yes | `4518781cdcc002e0` |
| 0.5 | 0.4927 | 1,995.70 | 0.7322 | 0.4918 | 0.5259 | -276,805.46 | 563,587.04 | -276,805.46 | -558,598.98 | -840,392.50 | -680.11 | 151.68 | -1,070.08 | -1,589.92 | yes | `954714fdf5e45d74` |
| 0.55 | 0.5533 | 2,060.11 | 0.7374 | 0.5316 | 0.4473 | -368,929.38 | 519,372.81 | -368,929.38 | -628,615.79 | -888,302.19 | -807.29 | -112.45 | -1,197.25 | -1,725.06 | yes | `702169d53aacfde0` |
| 0.6 | 0.5981 | 2,064.95 | 0.7409 | 0.5644 | 0.4020 | -411,220.70 | 483,049.27 | -411,220.70 | -652,745.33 | -894,269.97 | -832.43 | -187.54 | -1,222.40 | -1,747.13 | yes | `e2103593cb5a7548` |
| 0.65 | 0.6538 | 2,046.76 | 0.7296 | 0.6794 | 0.3407 | -390,058.45 | 355,565.18 | -390,058.45 | -567,841.04 | -745,623.63 | -722.33 | 100.28 | -1,112.30 | -1,626.63 | yes | `220a2a556cabfae0` |
| 0.7 | 0.6804 | 2,044.74 | 0.7331 | 0.7000 | 0.3154 | -411,055.70 | 332,666.48 | -411,055.70 | -577,388.94 | -743,722.18 | -731.42 | 80.21 | -1,121.38 | -1,642.53 | yes | `e9c53ed56700925e` |
| 0.75 | 0.7615 | 2,050.69 | 0.7329 | 0.7562 | 0.2337 | -490,367.06 | 270,345.44 | -490,367.06 | -625,539.78 | -760,712.50 | -779.60 | -94.53 | -1,169.56 | -1,689.70 | yes | `52bc200ab1b8819c` |
| 0.8 | 0.7809 | 2,050.26 | 0.7287 | 0.7779 | 0.2144 | -499,850.36 | 246,325.36 | -499,850.36 | -623,013.04 | -746,175.72 | -774.96 | -81.73 | -1,164.93 | -1,688.86 | yes | `7ce2df79bcb52980` |
| 0.85 | 0.8450 | 2,050.41 | 0.7321 | 0.8426 | 0.1506 | -538,717.85 | 174,492.21 | -538,717.85 | -625,963.95 | -713,210.06 | -771.80 | -95.18 | -1,161.77 | -1,683.11 | yes | `86ef14f6c06ba001` |
| 0.9 | 0.9019 | 2,029.24 | 0.7235 | 0.9046 | 0.1041 | -550,609.72 | 105,789.42 | -550,609.72 | -603,504.43 | -656,399.14 | -739.07 | 183.34 | -1,129.04 | -1,648.21 | yes | `df9e071d5d4591bb` |
| 0.95 | 0.9455 | 2,045.80 | 0.7183 | 0.9769 | 0.0520 | -560,839.49 | 25,652.34 | -560,839.49 | -573,665.66 | -586,491.83 | -718.10 | 714.91 | -1,108.07 | -1,625.41 | yes | `1d053fd152f2b264` |
| 1.0 | 1.0000 | 2,043.33 | 0.7228 | 1.0000 | -0.0000 | -625,325.16 | 0.00 | -625,325.16 | -625,325.16 | -625,325.16 | -757.05 | - | - | -1,658.62 | yes | `be02ecc5c908a402` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.15, w = 1 -> 0.95. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4984 | 0.0564 | 192.05 | 220.94 | 21 |
| 0.1 | 0.5114 | 0.1152 | 399.92 | 427.78 | 44 |
| 0.15 | 0.5182 | 0.1593 | 534.20 | 561.39 | 57 |
| 0.2 | 0.5201 | 0.2059 | 697.68 | 724.06 | 72 |
| 0.25 | 0.5204 | 0.2525 | 802.67 | 828.53 | 82 |
| 0.3 | 0.5206 | 0.3113 | 951.72 | 976.83 | 97 |
| 0.35 | 0.5236 | 0.3995 | 1,141.50 | 1,165.67 | 120 |
| 0.4 | 0.5236 | 0.3995 | 1,141.50 | 1,165.67 | 120 |
| 0.45 | 0.5288 | 0.5172 | 1,356.05 | 1,379.15 | 139 |
| 0.5 | 0.5288 | 0.5172 | 1,356.05 | 1,379.15 | 139 |
| 0.55 | 0.5289 | 0.5588 | 1,473.34 | 1,495.86 | 147 |
| 0.6 | 0.5323 | 0.6103 | 1,554.13 | 1,576.25 | 154 |
| 0.65 | 0.5342 | 0.6593 | 1,664.25 | 1,685.82 | 160 |
| 0.7 | 0.5361 | 0.7328 | 1,734.29 | 1,755.52 | 170 |
| 0.75 | 0.5387 | 0.8015 | 1,810.43 | 1,831.27 | 178 |
| 0.8 | 0.5387 | 0.8015 | 1,810.43 | 1,831.27 | 178 |
| 0.85 | 0.5439 | 0.8676 | 1,820.55 | 1,841.34 | 187 |
| 0.9 | 0.5474 | 0.9020 | 1,870.06 | 1,890.61 | 189 |
| 0.95 | 0.5575 | 0.9534 | 1,895.18 | 1,915.61 | 196 |
| 1.0 | - | 1.0000 | 1,943.64 | 1,963.82 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.2 | 0.5201 | 724.06 | 1,527.02 | 0.2225 | 1,777.26 | 0.2143 | 168.74 | 92.9 | -1,014.43 | `24c4791c406a1e34` |
| 1000.0 | 0.3 | 0.5206 | 976.83 | 1,527.02 | 0.2225 | 1,838.23 | 0.2663 | 133.84 | 84.5 | -1,048.83 | `cdd5fa5f712fddd9` |
| 1200.0 | 0.4 | 0.5236 | 1,165.67 | 1,773.33 | 0.3828 | 1,906.98 | 0.3910 | 199.44 | 82.0 | -1,025.57 | `d81a3d5c7614cfa1` |

#### (5) Cost sensitivity of every kept book of this model: 37 books; kept mean > 0 at 8 pts slippage: **0** (best -550.95); at 3 pts: 1 (best 99.00); with uncapped 0.03% brokerage (+901.57 INR/trade): best kept mean -1,050.70. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### 5minute / h5_full/hgbc - gradient-boosting ceiling of sub-family (II) (reference) - outside the frozen shortlist (importance rule failed for every cluster)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9563 | 0.9638 | 0.6923 / 1.0000 | 3 / 1 | 0.9540 | -757.15 | -754.98 | -2.18 | 367.09 | 0.9975 | 74.0 | 0.0469 | 0.0435 | 7 | -497.18 | -1,147.12 | -1,658.63 | 0.9661 | `2f64d2c7eff61033` |
| 0.1 | 0.90 | 0.80 | 0.9039 | 0.9085 | 0.6154 / 1.0000 | 3 / 1 | 0.9031 | -768.04 | -654.56 | -113.49 | -59.61 | 0.8336 | 70.7 | 0.0972 | 0.0435 | 9 | -508.07 | -1,158.01 | -1,668.25 | 0.9467 | `021febfc5d8f03f4` |
| 0.15 | 0.85 | 0.70 | 0.8472 | 0.8590 | 0.5385 / 0.9412 | 4 / 1 | 0.8426 | -750.84 | -790.30 | 39.46 | -23.62 | 0.9285 | 78.0 | 0.1591 | 0.0870 | 8 | -490.87 | -1,140.81 | -1,651.45 | 0.8862 | `dbe1f985c6c453bb` |
| 0.2 | 0.80 | 0.60 | 0.7991 | 0.8074 | 0.5385 / 0.9412 | 5 / 1 | 0.7845 | -730.72 | -852.93 | 122.21 | 139.58 | 0.7421 | 91.7 | 0.2211 | 0.1739 | 8 | -470.74 | -1,120.68 | -1,630.35 | 0.8281 | `d2aaaa370fe56917` |
| 0.3 | 0.70 | 0.40 | 0.6987 | 0.7185 | 0.4615 / 0.9375 | 6 / 0 | 0.6889 | -702.23 | -878.42 | 176.19 | 92.82 | 0.6067 | 85.5 | 0.3149 | 0.2609 | 7 | -442.26 | -1,092.20 | -1,597.21 | 0.7324 | `3ed31945502c4cdf` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas []; chosen **None** - no alpha satisfies both constraints.

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 203 | 0.8441 | 82 | 26 | 0.9512 | 0.9615 | 0.9630 | 0.0536 |
| 1 | 202 | 0.8441 | 83 | 27 | 0.9157 | 0.9630 | 0.8735 | 0.1071 |
| 2 | 212 | 0.8403 | 42 | 17 | 0.9524 | 0.9412 | 0.9902 | 0.0400 |
| 3 | 209 | 0.8353 | 76 | 20 | 0.8684 | 0.8000 | 0.6992 | 0.1071 |
| 4 | 208 | 0.8403 | 72 | 21 | 0.9167 | 0.9048 | 0.9556 | 0.0784 |
| 5 | 213 | 0.8354 | 73 | 16 | 0.8630 | 0.8125 | 0.6575 | 0.1228 |
| 6 | 216 | 0.8333 | 77 | 13 | 0.8312 | 0.6154 | 0.7496 | 0.1250 |
| 7 | 216 | 0.8403 | 51 | 13 | 0.9216 | 0.9231 | 0.9725 | 0.0789 |
| 8 | 208 | 0.8441 | 76 | 21 | 0.9079 | 0.9524 | 0.9850 | 0.1091 |
| 9 | 213 | 0.8403 | 80 | 16 | 0.9125 | 0.9375 | 0.9911 | 0.0938 |
| 10 | 220 | 0.8403 | 31 | 9 | 0.9355 | 1.0000 | 1.0000 | 0.0909 |
| 11 | 199 | 0.8403 | 83 | 30 | 0.9036 | 0.9333 | 0.9466 | 0.1132 |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 96 | 229 | 0.9432 | 0.9347 | 0.9649 | 0.0288 / 0.0620 | 0.0423 | 0.8807 | 0.1193 | 0.9564 | -722.30 | 0.3288 | 67.7 | 0.0385 | 5 | -1,178.50 | `9dd8441864a200f2` |
| 0.005 | 0.1 | 96 | 229 | 0.8952 | 0.8794 | 0.9298 | 0.0785 / 0.1190 | 0.0945 | 0.8441 | 0.1559 | 0.9092 | -704.47 | 0.1874 | 21.6 | 0.0854 | 4 | -1,210.98 | `56aebd9971dc85d8` |
| 0.005 | 0.15 | 96 | 229 | 0.8646 | 0.8442 | 0.8947 | 0.1450 / 0.1762 | 0.1668 | 0.8003 | 0.1997 | 0.8608 | -92.09 | 0.8391 | 76.3 | 0.1407 | 7 | -1,159.84 | `8cb4668653851bf0` |
| 0.005 | 0.2 | 96 | 229 | 0.8166 | 0.7889 | 0.8421 | 0.1950 / 0.2350 | 0.2190 | 0.7782 | 0.2218 | 0.8099 | 7.09 | 0.9835 | 83.8 | 0.1926 | 7 | -1,145.67 | `97b3702938169048` |
| 0.005 | 0.3 | 96 | 229 | 0.7118 | 0.6683 | 0.7719 | 0.2900 / 0.3450 | 0.3135 | 0.742 | 0.2580 | 0.7022 | 336.01 | 0.3308 | 77.2 | 0.3015 | 7 | -1,046.95 | `05eaa4e81736fe49` |
| 0.01 | 0.05 | 96 | 229 | 0.9476 | 0.9397 | 0.9649 | 0.0170 / 0.0740 | 0.0445 | 0.8794 | 0.1206 | 0.9613 | -846.97 | 0.3078 | 60.2 | 0.0335 | 5 | -1,179.83 | `40893fa4b0deb352` |
| 0.01 | 0.1 | 96 | 229 | 0.8996 | 0.8844 | 0.9298 | 0.0600 / 0.1380 | 0.0990 | 0.8403 | 0.1597 | 0.9092 | -635.16 | 0.2324 | 27.6 | 0.0871 | 5 | -1,204.69 | `6474a3666a341dd9` |
| 0.01 | 0.15 | 96 | 229 | 0.8603 | 0.8392 | 0.8947 | 0.1300 / 0.2025 | 0.1735 | 0.8002 | 0.1998 | 0.8571 | -89.48 | 0.8471 | 79.2 | 0.1441 | 7 | -1,159.80 | `08e7bcc9dfb10d0d` |
| 0.01 | 0.2 | 96 | 229 | 0.8122 | 0.7839 | 0.8421 | 0.1700 / 0.2660 | 0.2280 | 0.7751 | 0.2249 | 0.8039 | 68.46 | 0.8651 | 70.3 | 0.1993 | 7 | -1,133.59 | `312c12b279d09778` |
| 0.01 | 0.3 | 96 | 229 | 0.7074 | 0.6633 | 0.7719 | 0.2650 / 0.3900 | 0.3170 | 0.742 | 0.2580 | 0.7034 | 344.86 | 0.3273 | 83.8 | 0.2982 | 7 | -1,044.73 | `8a8053b6f020a249` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.1005 | 2,420.25 | 0.7108 | 0.1255 | 0.8773 | -73,530.06 | 969,722.48 | -73,530.06 | -558,391.30 | -1,043,252.54 | -885.90 | -143.25 | -1,275.87 | -1,765.06 | yes | `7d7cc6c6a973f93b` |
| 0.15 | 0.1489 | 2,386.99 | 0.7236 | 0.1444 | 0.8230 | -146,772.55 | 948,766.74 | -146,772.55 | -621,155.92 | -1,095,539.29 | -1,193.27 | -512.54 | -1,583.24 | -2,074.53 | yes | `f7b4a4cee9f9f7ed` |
| 0.2 | 0.2034 | 2,282.49 | 0.7321 | 0.1783 | 0.7693 | -202,355.59 | 911,175.48 | -202,355.59 | -657,943.33 | -1,113,531.07 | -1,204.50 | -561.69 | -1,594.46 | -2,091.64 | yes | `ed2f80d117038d17` |
| 0.25 | 0.2506 | 2,194.16 | 0.7246 | 0.2399 | 0.7285 | -204,773.64 | 842,860.07 | -204,773.64 | -626,203.68 | -1,047,633.71 | -989.24 | -309.84 | -1,379.21 | -1,867.87 | yes | `cc14e7994d043d46` |
| 0.3 | 0.3027 | 2,153.02 | 0.7240 | 0.2847 | 0.6781 | -242,529.44 | 793,169.76 | -242,529.44 | -639,114.32 | -1,035,699.20 | -970.12 | -305.54 | -1,360.08 | -1,853.31 | yes | `7269463b4f25263c` |
| 0.35 | 0.3499 | 2,157.25 | 0.7266 | 0.3450 | 0.6290 | -260,847.01 | 726,298.44 | -260,847.01 | -623,996.23 | -987,145.45 | -902.58 | -223.85 | -1,292.55 | -1,788.52 | yes | `bf1d69b135c62b51` |
| 0.4 | 0.4031 | 2,145.97 | 0.7327 | 0.3838 | 0.5764 | -309,022.03 | 683,308.39 | -309,022.03 | -650,676.23 | -992,330.42 | -927.99 | -286.41 | -1,317.96 | -1,811.51 | yes | `d8de4ebfefc6e5fd` |
| 0.45 | 0.4516 | 2,107.55 | 0.7212 | 0.4689 | 0.5346 | -287,113.84 | 588,999.86 | -287,113.84 | -581,613.77 | -876,113.70 | -769.74 | -23.14 | -1,159.71 | -1,658.15 | yes | `ea1b7c4903a643ae` |
| 0.5 | 0.4976 | 2,092.74 | 0.7202 | 0.5204 | 0.4920 | -303,937.88 | 531,822.12 | -303,937.88 | -569,848.94 | -835,760.00 | -739.51 | 34.92 | -1,129.47 | -1,629.58 | yes | `8d9e6d85a24a536d` |
| 0.55 | 0.5521 | 2,120.89 | 0.7303 | 0.5730 | 0.4297 | -353,676.16 | 473,481.40 | -353,676.16 | -590,416.86 | -827,157.56 | -775.61 | -41.42 | -1,165.57 | -1,667.81 | yes | `daa97a12198e3a33` |
| 0.6 | 0.5920 | 2,089.31 | 0.7198 | 0.6397 | 0.3982 | -334,325.23 | 399,583.68 | -334,325.23 | -534,117.07 | -733,908.91 | -683.69 | 179.81 | -1,073.66 | -1,577.68 | yes | `f92b53489e73c504` |
| 0.65 | 0.6489 | 2,046.87 | 0.7127 | 0.7029 | 0.3547 | -339,657.54 | 329,469.13 | -339,657.54 | -504,392.10 | -669,126.67 | -633.69 | 351.37 | -1,023.65 | -1,528.15 | yes | `090b558c2cb6029f` |
| 0.7 | 0.6961 | 2,054.86 | 0.7165 | 0.7276 | 0.3059 | -396,969.76 | 302,072.20 | -396,969.76 | -548,005.86 | -699,041.96 | -690.38 | 219.40 | -1,080.35 | -1,585.57 | yes | `78c539ed0b9cfaf0` |
| 0.75 | 0.7446 | 2,056.65 | 0.7171 | 0.7765 | 0.2575 | -426,599.10 | 247,809.88 | -426,599.10 | -550,504.04 | -674,408.98 | -693.66 | 248.17 | -1,083.62 | -1,592.95 | yes | `59db810b46766600` |
| 0.8 | 0.7954 | 2,049.08 | 0.7184 | 0.8083 | 0.2006 | -490,057.80 | 212,553.96 | -490,057.80 | -596,334.78 | -702,611.76 | -745.90 | 54.50 | -1,135.87 | -1,643.89 | yes | `2ec26c2a8e34311b` |
| 0.85 | 0.8475 | 2,051.47 | 0.7186 | 0.8685 | 0.1488 | -513,116.31 | 145,827.63 | -513,116.31 | -586,030.12 | -658,943.94 | -733.02 | 157.52 | -1,122.99 | -1,633.17 | yes | `734425db9af4dd12` |
| 0.9 | 0.8983 | 2,054.46 | 0.7224 | 0.8938 | 0.0951 | -578,153.85 | 117,751.35 | -578,153.85 | -637,029.53 | -695,905.20 | -779.18 | -217.62 | -1,169.15 | -1,678.33 | yes | `7934ced695aa7a12` |
| 0.95 | 0.9492 | 2,058.67 | 0.7219 | 0.9617 | 0.0432 | -592,845.93 | 42,481.85 | -592,845.93 | -614,086.86 | -635,327.78 | -756.18 | 17.13 | -1,146.15 | -1,657.19 | yes | `0a01a6c0648c825a` |
| 1.0 | 1.0000 | 2,043.33 | 0.7228 | 1.0000 | -0.0000 | -625,325.16 | 0.00 | -625,325.16 | -625,325.16 | -625,325.16 | -757.05 | - | - | -1,658.62 | yes | `f7e82fb2707ed46a` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.65, w = 1 -> 1.0. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.3594 | 0.0515 | 338.83 | 366.99 | 20 |
| 0.1 | 0.4190 | 0.1005 | 559.67 | 586.74 | 39 |
| 0.15 | 0.4908 | 0.1520 | 649.01 | 675.63 | 51 |
| 0.2 | 0.5217 | 0.2010 | 730.98 | 757.20 | 64 |
| 0.25 | 0.5680 | 0.2500 | 832.27 | 857.98 | 75 |
| 0.3 | 0.5900 | 0.3015 | 930.52 | 955.74 | 87 |
| 0.35 | 0.6195 | 0.3505 | 1,059.90 | 1,084.47 | 98 |
| 0.4 | 0.6440 | 0.3995 | 1,133.01 | 1,157.23 | 113 |
| 0.45 | 0.6735 | 0.4510 | 1,291.50 | 1,314.92 | 123 |
| 0.5 | 0.6943 | 0.5000 | 1,407.54 | 1,430.39 | 132 |
| 0.55 | 0.7109 | 0.5490 | 1,462.86 | 1,485.44 | 142 |
| 0.6 | 0.7250 | 0.6005 | 1,588.98 | 1,610.92 | 153 |
| 0.65 | 0.7427 | 0.6495 | 1,607.18 | 1,629.04 | 162 |
| 0.7 | 0.7585 | 0.6985 | 1,684.31 | 1,705.78 | 171 |
| 0.75 | 0.7739 | 0.7500 | 1,759.83 | 1,780.92 | 177 |
| 0.8 | 0.7922 | 0.7990 | 1,843.00 | 1,863.68 | 185 |
| 0.85 | 0.8204 | 0.8480 | 1,885.24 | 1,905.71 | 190 |
| 0.9 | 0.8461 | 0.8995 | 1,923.74 | 1,944.02 | 192 |
| 0.95 | 0.8774 | 0.9485 | 1,924.07 | 1,944.35 | 193 |
| 1.0 | - | 1.0000 | 1,943.64 | 1,963.82 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.2 | 0.5217 | 757.20 | 2,110.77 | 0.2273 | 2,252.64 | 0.2143 | -423.13 | 54.2 | -1,479.48 | `cc9384222890c5f9` |
| 1000.0 | 0.3 | 0.5900 | 955.74 | 2,014.96 | 0.3445 | 2,141.42 | 0.3232 | -295.93 | 67.8 | -1,347.29 | `15e27ea4dd97c091` |
| 1200.0 | 0.4 | 0.6440 | 1,157.23 | 2,000.16 | 0.4665 | 2,082.59 | 0.4334 | 120.83 | 91.3 | -1,078.56 | `569746c623a1c655` |

#### (5) Cost sensitivity of every kept book of this model: 37 books; kept mean > 0 at 8 pts slippage: **0** (best -1,023.65); at 3 pts: 0 (best -373.71); with uncapped 0.03% brokerage (+901.57 INR/trade): best kept mean -1,528.15. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### 5minute / h5_full/scorecard - finalist of sub-family (II) (scorecard -> distilled rules; this is the scorecard OOF p) - outside the frozen shortlist (importance rule failed for every cluster)

#### (1) Cross-conformal, Mondrian by class (winner coverage); pooled OOF gate = ledger row (controls on)

| alpha | nominal 1-a | CV+ 1-2a | OOF winner coverage | |net|-wtd coverage | per-fold min / max | folds < nominal / < CV+ | kept share | kept mean | skipped mean | diff | diff top1% off | perm p | control pct | loser recall | top-decile winners skipped | sign blocks | kept mean slip3 | kept mean slip8 | kept mean uncapped brokerage | agreement w/ gate_family nested | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0.95 | 0.90 | 0.9389 | 0.9089 | 0.4375 / 1.0000 | 3 / 2 | 0.9165 | -730.93 | -1,043.63 | 312.70 | 762.40 | 0.5857 | 83.5 | 0.0921 | 0.0870 | 1 | -470.95 | -1,120.90 | -1,629.43 | 0.9189 | `a67e800feba69177` |
| 0.1 | 0.90 | 0.80 | 0.8996 | 0.8742 | 0.4375 / 1.0000 | 3 / 2 | 0.8668 | -692.97 | -1,174.14 | 481.16 | 924.18 | 0.2739 | 82.8 | 0.1457 | 0.1304 | 4 | -433.00 | -1,082.94 | -1,599.61 | 0.8692 | `a28e09da4070d513` |
| 0.15 | 0.85 | 0.70 | 0.8341 | 0.8269 | 0.4375 / 1.0000 | 5 / 3 | 0.8245 | -726.24 | -901.78 | 175.55 | 455.67 | 0.6782 | 54.3 | 0.1792 | 0.1739 | 4 | -466.26 | -1,116.20 | -1,627.25 | 0.8269 | `8cdf81e1f7c80444` |
| 0.2 | 0.80 | 0.60 | 0.7686 | 0.7760 | 0.2333 / 1.0000 | 4 / 2 | 0.7615 | -735.26 | -826.65 | 91.39 | 236.02 | 0.8011 | 69.0 | 0.2412 | 0.1739 | 5 | -475.28 | -1,125.22 | -1,627.19 | 0.7639 | `98f05c4fae402352` |
| 0.3 | 0.70 | 0.40 | 0.6856 | 0.7442 | 0.1429 / 1.0000 | 5 / 2 | 0.6755 | -659.58 | -960.00 | 300.42 | 336.29 | 0.3793 | 76.5 | 0.3283 | 0.1739 | 6 | -399.60 | -1,049.54 | -1,565.75 | 0.6780 | `04f33f3a581135f5` |

Pre-registered alpha rule of the conformal design ('largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0'): feasible alphas [0.05]; chosen **0.05** (the smallest alpha of the grid: at every larger alpha the kept-vs-skipped difference is not positive, or coverage falls below 0.9).

Per-fold coverage of alpha = 0.10 (nominal 0.90, CV+ 0.80):

| fold | cal winners | q | n | winners | kept share | winner coverage | |net|-wtd coverage | loser recall |
|---|---|---|---|---|---|---|---|---|
| 0 | 203 | 0.5484 | 82 | 26 | 0.9390 | 0.9615 | 0.9980 | 0.0714 |
| 1 | 202 | 0.5433 | 83 | 27 | 0.5542 | 0.6667 | 0.6024 | 0.5000 |
| 2 | 212 | 0.5484 | 42 | 17 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 3 | 209 | 0.5456 | 76 | 20 | 0.7105 | 0.8000 | 0.8216 | 0.3214 |
| 4 | 208 | 0.5508 | 72 | 21 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 5 | 213 | 0.5484 | 73 | 16 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 6 | 216 | 0.5484 | 77 | 13 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 7 | 216 | 0.5484 | 51 | 13 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 8 | 208 | 0.5508 | 76 | 21 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 9 | 213 | 0.5433 | 80 | 16 | 0.4250 | 0.4375 | 0.4333 | 0.5781 |
| 10 | 220 | 0.5467 | 31 | 9 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 11 | 199 | 0.5508 | 83 | 30 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

#### (1c) ACI, winner-conditional, IS in time order (final state = what oos_once would carry; no OOS row read)

| gamma | alpha | burn-in rows | winners updated | winner coverage (all) | after burn-in | last quarter | alpha_t min / max | alpha_T | q_T | skip if p < | kept share | diff | perm p | control pct | loser recall | sign blocks | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 | 0.05 | 96 | 229 | 0.9476 | 0.9397 | 0.8772 | 0.0362 / 0.0688 | 0.0473 | 0.5679 | 0.4321 | 0.9383 | -36.42 | 0.9455 | 77.8 | 0.0653 | 1 | -1,149.27 | `b987b6c699da2bc0` |
| 0.005 | 0.1 | 96 | 229 | 0.9258 | 0.9146 | 0.8421 | 0.0985 / 0.1475 | 0.1295 | 0.5433 | 0.4567 | 0.9104 | 251.75 | 0.6447 | 85.3 | 0.0955 | 2 | -1,124.46 | `587a467c9ed2dea1` |
| 0.005 | 0.15 | 96 | 229 | 0.8603 | 0.8392 | 0.7193 | 0.1505 / 0.2013 | 0.1618 | 0.5433 | 0.4567 | 0.8366 | 250.89 | 0.5317 | 31.4 | 0.1725 | 3 | -1,106.01 | `67aababd029916fc` |
| 0.005 | 0.2 | 96 | 229 | 0.7773 | 0.7437 | 0.5088 | 0.1700 / 0.2600 | 0.1740 | 0.5398 | 0.4602 | 0.7785 | -120.12 | 0.7696 | 38.5 | 0.2211 | 3 | -1,173.63 | `681ef105a125fe60` |
| 0.005 | 0.3 | 96 | 229 | 0.6943 | 0.6482 | 0.4386 | 0.2935 / 0.3725 | 0.2935 | 0.5363 | 0.4637 | 0.6949 | 92.49 | 0.7886 | 71.2 | 0.3049 | 4 | -1,118.80 | `560187649d32ac5a` |
| 0.01 | 0.05 | 96 | 229 | 0.9520 | 0.9447 | 0.9123 | 0.0290 / 0.0775 | 0.0545 | 0.5648 | 0.4352 | 0.9443 | -93.44 | 0.8891 | 78.8 | 0.0586 | 1 | -1,152.22 | `e8abcd06673091ec` |
| 0.01 | 0.1 | 96 | 229 | 0.9214 | 0.9095 | 0.8421 | 0.0970 / 0.1850 | 0.1490 | 0.5433 | 0.4567 | 0.9080 | 242.38 | 0.6422 | 79.6 | 0.0972 | 2 | -1,124.72 | `b7b4c8f9625980de` |
| 0.01 | 0.15 | 96 | 229 | 0.8603 | 0.8392 | 0.7368 | 0.1480 / 0.2425 | 0.1735 | 0.5398 | 0.4602 | 0.8305 | 321.93 | 0.4643 | 40.2 | 0.1809 | 3 | -1,092.45 | `09bc46083ba6c272` |
| 0.01 | 0.2 | 96 | 229 | 0.7860 | 0.7538 | 0.5614 | 0.1520 / 0.3100 | 0.1680 | 0.5433 | 0.4567 | 0.7639 | 231.40 | 0.5187 | 47.2 | 0.2446 | 4 | -1,092.39 | `ce9d45717c7fbdcb` |
| 0.01 | 0.3 | 96 | 229 | 0.6900 | 0.6432 | 0.4386 | 0.2770 / 0.4350 | 0.2770 | 0.5363 | 0.4637 | 0.6864 | 124.64 | 0.7281 | 72.9 | 0.3149 | 4 | -1,107.93 | `f567d1541157bd50` |

#### (2) + (4) Selective risk-coverage curve (nested thresholds; trials, controls off) and the cost-aware utilities U_w = kept net - w x skipped winner net

| coverage c | realised | selective risk (clipped 6000) | loser share kept | winner-net retained | loser-net avoided | kept net | skipped winner net | U w=0 | U w=0.5 | U w=1 | kept mean | diff | kept mean slip8 | kept mean uncapped | Pareto-efficient | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.0932 | 2,125.61 | 0.6883 | 0.1074 | 0.9024 | -50,259.35 | 989,884.07 | -50,259.35 | -545,201.39 | -1,040,143.42 | -652.72 | 115.06 | -1,042.68 | -1,629.06 | yes | `372c78298500df23` |
| 0.15 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `82724f77f8630120` |
| 0.2 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `bd0facbd8f406033` |
| 0.25 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `8c4157acb2b16e6c` |
| 0.3 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `7a27d7a12c041827` |
| 0.35 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `598052e2dcd96b35` |
| 0.4 | 0.4249 | 2,140.08 | 0.7293 | 0.4716 | 0.5498 | -257,745.54 | 585,932.08 | -257,745.54 | -550,711.58 | -843,677.62 | -734.32 | 39.53 | -1,124.28 | -1,679.01 | yes | `3a5776138f085bdd` |
| 0.45 | 0.4334 | 2,120.43 | 0.7263 | 0.4774 | 0.5452 | -259,244.18 | 579,486.61 | -259,244.18 | -548,987.49 | -838,730.79 | -724.15 | 58.08 | -1,114.11 | -1,665.64 | yes | `ca7e74d4d80a645c` |
| 0.5 | 0.4891 | 2,108.19 | 0.7252 | 0.5410 | 0.4896 | -285,254.47 | 508,980.86 | -285,254.47 | -539,744.90 | -794,235.33 | -706.08 | 99.78 | -1,096.04 | -1,631.01 | yes | `f8d51a1451ded07f` |
| 0.55 | 0.5061 | 2,089.38 | 0.7225 | 0.5589 | 0.4771 | -287,019.36 | 489,094.20 | -287,019.36 | -531,566.46 | -776,113.56 | -686.65 | 142.53 | -1,076.61 | -1,607.08 | yes | `dd1928f2fd4843fb` |
| 0.6 | 0.5763 | 2,098.03 | 0.7248 | 0.6103 | 0.4036 | -357,622.11 | 432,156.77 | -357,622.11 | -573,700.49 | -789,778.88 | -751.31 | 13.56 | -1,141.27 | -1,678.20 | yes | `10de39a8076e0bbc` |
| 0.65 | 0.6392 | 2,083.90 | 0.7159 | 0.7203 | 0.3446 | -337,882.95 | 310,118.92 | -337,882.95 | -492,942.41 | -648,001.87 | -639.93 | 324.64 | -1,029.89 | -1,553.56 | yes | `69f9ab664dd5a97c` |
| 0.7 | 0.6755 | 2,073.29 | 0.7186 | 0.7442 | 0.3119 | -368,045.34 | 283,683.73 | -368,045.34 | -509,887.20 | -651,729.07 | -659.58 | 300.42 | -1,049.54 | -1,565.75 | yes | `8b23bb5886e2c847` |
| 0.75 | 0.7494 | 2,030.55 | 0.7173 | 0.7758 | 0.2543 | -433,040.86 | 248,661.83 | -433,040.86 | -557,371.78 | -681,702.69 | -699.58 | 229.33 | -1,089.55 | -1,593.24 | yes | `3a1674e33f2c81fb` |
| 0.8 | 0.7615 | 2,038.40 | 0.7202 | 0.7760 | 0.2371 | -462,476.02 | 248,396.27 | -462,476.02 | -586,674.16 | -710,872.29 | -735.26 | 91.39 | -1,125.22 | -1,627.19 | yes | `e6a936bca01661ac` |
| 0.85 | 0.8584 | 1,977.25 | 0.7109 | 0.8742 | 0.1681 | -473,265.84 | 139,471.89 | -473,265.84 | -543,001.79 | -612,737.73 | -667.51 | 632.14 | -1,057.48 | -1,575.25 | yes | `54c215eee00bd0f5` |
| 0.9 | 0.8826 | 1,994.64 | 0.7133 | 0.8812 | 0.1372 | -519,078.28 | 131,723.07 | -519,078.28 | -584,939.81 | -650,801.35 | -712.04 | 383.29 | -1,102.01 | -1,616.13 | yes | `7b6b6c14491bc8be` |
| 0.95 | 0.9298 | 2,002.90 | 0.7174 | 0.9204 | 0.0880 | -561,101.19 | 88,320.40 | -561,101.19 | -605,261.39 | -649,421.59 | -730.60 | 376.71 | -1,120.57 | -1,626.62 | yes | `91738559ed0a2cca` |
| 1.0 | 1.0000 | 2,043.33 | 0.7228 | 1.0000 | -0.0000 | -625,325.16 | 0.00 | -625,325.16 | -625,325.16 | -625,325.16 | -757.05 | - | - | -1,658.62 | yes | `0ff7a7e7d1511cd7` |

Argmax coverage of U_w on the grid: w = 0 -> 0.1, w = 0.5 -> 0.65, w = 1 -> 0.85. Presented for the user to pick w and the coverage (Rule 0(c)); nothing is chosen here. At w = 0 the optimum is the smallest coverage on the grid because every kept book's net is negative (skipping everything, coverage 0, is not on the grid and would be the true argmax).

#### (3) Conformal Risk Control with sessions as units (calibration = the last 200 active IS sessions; B = 6000; slack B/(n+1) = 29.85 INR)

| coverage lambda | threshold s | kept share (block) | R_hat (block) | certificate (n R_hat + B)/(n+1) | sessions with a kept unit |
|---|---|---|---|---|---|
| 0.05 | 0.4560 | 0.0858 | 241.58 | 270.22 | 22 |
| 0.1 | 0.4702 | 0.1005 | 276.39 | 304.87 | 28 |
| 0.15 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.2 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.25 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.3 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.35 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.4 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.45 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.5 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.55 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.6 | 0.5000 | 0.6422 | 1,368.65 | 1,391.69 | 135 |
| 0.65 | 0.5067 | 0.6495 | 1,400.70 | 1,423.58 | 137 |
| 0.7 | 0.5267 | 0.7353 | 1,674.93 | 1,696.45 | 161 |
| 0.75 | 0.5340 | 0.7500 | 1,699.65 | 1,721.04 | 163 |
| 0.8 | 0.5383 | 0.8235 | 1,733.44 | 1,754.66 | 177 |
| 0.85 | 0.5433 | 0.8848 | 1,751.57 | 1,772.70 | 185 |
| 0.9 | 0.5598 | 0.9044 | 1,798.49 | 1,819.39 | 188 |
| 0.95 | 0.5748 | 0.9534 | 1,888.76 | 1,909.22 | 197 |
| 1.0 | - | 1.0000 | 1,943.64 | 1,963.82 | 200 |

| alpha (INR) | lambda* | threshold s | certificate | realised risk before the block | kept share before the block | realised risk all IS | kept share IS | diff | control pct | kept mean slip8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 800.0 | 0.1 | 0.4702 | 304.87 | 1,488.92 | 0.0263 | 1,966.17 | 0.0630 | -220.91 | 51.9 | -1,354.02 | `f5ac436f5e47be27` |
| 1000.0 | 0.1 | 0.4702 | 304.87 | 1,488.92 | 0.0263 | 1,966.17 | 0.0630 | -220.91 | 52.2 | -1,354.02 | `31b746bf27296810` |
| 1200.0 | 0.1 | 0.4702 | 304.87 | 1,488.92 | 0.0263 | 1,966.17 | 0.0630 | -220.91 | 52.4 | -1,354.02 | `7c7239506e10ad36` |

#### (5) Cost sensitivity of every kept book of this model: 37 books; kept mean > 0 at 8 pts slippage: **0** (best -1,029.89); at 3 pts: 0 (best -379.95); with uncapped 0.03% brokerage (+901.57 INR/trade): best kept mean -1,553.56. The kept-vs-skipped difference is slippage-invariant (every trade moves by the same amount); the brokerage cap makes the uncapped delta almost constant across trades too.

### 5minute family multiplicity (every `operating_point/*` ledger row of the timeframe with a defined diff)

| rows | by family | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|
| 144 | {'operating_point/aci': 40, 'operating_point/conformal': 20, 'operating_point/coverage': 72, 'operating_point/crc': 12} | 0.6395 | 0.6507 | 0.3862 | 0.066 | 0.123 | 87.43 (3.015) | 4 | 0.7205 | 2.16 |

Best controlled row by diff: operating_point/conformal `a28e09da4070d513` config {'tf': '5minute', 'sub': 'h5_full', 'model': 'scorecard', 'vocabulary': 'outside the frozen shortlist (importance rule failed for every cluster)', 'score': '1 - p_oof', 'step': 'conformal', 'taxonomy': 'class', 'alpha': 0.1}: diff 481.16, control pct 82.8, kept share 0.8668, kept mean slip8 -1,082.94, bootstrap 90% CI of diff [-400.02, 1407.91], DSR p 1.0 (n_trials 144); `harness.go_no_go` **FAIL**:

| item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.8668 |
| kept_n>=80 | yes | 716 |
| diff>0 | yes | 481.16 |
| diff_top1_removed>0 | yes | 924.18 |
| kept_mean_slip8>0 | no | -1082.94 |
| sign_blocks>=8/12 | no | 4 |
| control_pct>=95 | no | 82.8 |
| pbo<=0.2 | no | 0.6395 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | yes | 0.066 |
| boot_ci_excludes_0 | no | [-400.02, 1407.91] |
| null_tape:evaluated | no | not run: this step adds no candidate (it re-parameterises a gate_family score; gate_family wrote no candidate) |
| no_time_proxy_columns | yes | 160 columns |

### 5minute candidate: **none** (this step adds no candidate by design; the null-tape item reads 'not run' for that reason)

## 5. Sizing (conditional step): **not run: no gate passed**

- **minute**: verdict **not run: no gate passed**. Candidate files for the timeframe in `OUT/candidates/`: [] (folder exists: False); gate_family candidate: None. No candidate JSON for this timeframe in OUT/candidates/ (the folder does not exist) and gate_family's candidate is null: the finalists fail harness.go_no_go (minute: 6 items incl. control_pct 21.9, PBO 0.40, SPA p 0.94, kept mean at 8 pts slippage -1,378, the segment-tape p95; 5minute: 11 items, CPCV p5 -434). Both judges: sizing multiplies an edge that is not shown to exist (raw Kelly at a 16-28% win rate is negative); it runs only after a gate passes with CPCV 5th-percentile kept expectancy > 0. Nothing fitted; no Platt map, payoff table, lot bins, lot-aware control or ledger row was produced. The design's default verdict stands: lots = 1 or skip.
- **5minute**: verdict **not run: no gate passed**. Candidate files for the timeframe in `OUT/candidates/`: [] (folder exists: False); gate_family candidate: None. No candidate JSON for this timeframe in OUT/candidates/ (the folder does not exist) and gate_family's candidate is null: the finalists fail harness.go_no_go (minute: 6 items incl. control_pct 21.9, PBO 0.40, SPA p 0.94, kept mean at 8 pts slippage -1,378, the segment-tape p95; 5minute: 11 items, CPCV p5 -434). Both judges: sizing multiplies an edge that is not shown to exist (raw Kelly at a 16-28% win rate is negative); it runs only after a gate passes with CPCV 5th-percentile kept expectancy > 0. Nothing fitted; no Platt map, payoff table, lot bins, lot-aware control or ledger row was produced. The design's default verdict stands: lots = 1 or skip.

Nothing of the sizing design was fitted (no Platt calibration, reliability curve, Brier skill, ECE, payoff quintiles, AFML 10.3 comparison, half-Kelly bins, expected-net bins, lot-aware random control or block bootstrap), because every one of those numbers would size a book whose gated edge is not shown to exist; the design's default verdict 'lots = 1 or skip' is recorded and no 'size' block is output.

## 6. What would falsify these findings

- A scored gate_family model whose conformal or coverage-chosen kept book has a kept mean > 0 at 8 pts slippage AND a session-matched control percentile >= 95 AND a positive bootstrap 90% CI of the diff: none of the kept books here has any of the three on either timeframe (see the per-model tables).
- A CRC certificate that transfers: realised clipped risk on the IS rows before the calibration block within the certificate at the chosen lambda; here it is 1.3-4x above it on every model.
- A gate_family candidate in `OUT/candidates/` with a passed go/no-go: the sizing step then runs as designed (Platt, payoff quintiles, expected-net bins, lot-aware control, CPCV 5th percentile of the net-per-lot improvement).

## 7. Caveats

- The conformal guarantee is the cross-conformal / CV+ form (about 1 - 2 alpha): the calibration OOF scores of the 11 other folds come from models that saw the 12th fold. The empirical pooled OOF coverage sits near the nominal 1 - alpha on every model; per-fold coverage varies by about +-0.1 with 12-40 winners per fold on 5minute.
- The guarantee is on winner COUNT (or, as reported beside it, on winners' |net|), not on P&L in the tail: Judge 1's trap. The |net|-weighted coverage is reported next to the count coverage on every row.
- The CRC calibration block's scores are OOF from the purged folds, so the block is not disjoint in time from every score's training folds (the same CV+ caveat); its certificate also assumes session exchangeability, which the IS-early vs IS-late drift (null_tapes_drift, AUC 0.95 / 0.97) already violates: the realised risk before the block exceeds the certificate everywhere.
- The time-bin taxonomy reads the SETUP clock (`time`, an identity column in `harness.NOT_FEATURES`): its bins (10:30, 13:00) do not align with `hour_bin`'s edges; a deployable form would need a clock key. It is a diagnostic here.
- The scorecard's p is a per-fold Platt map of an integer score: pooled thresholds mix fold scales and the score has heavy ties, so several coverage-grid points coincide (identical keep masks under different configs c: separate ledger rows, separate ids).
- Sub-family (II) rows are OUTSIDE THE FROZEN SHORTLIST (the importance rule failed for every cluster); they are labelled so in every ledger note and counted in the same family for PBO / SPA.
- The coverage-curve rows are scored with controls off (trials); the conformal, ACI and CRC rows with controls on. All are in the family for PBO / SPA / effective trials.
- The online_learner study was appending to the ledger concurrently; ids are unique per config (the ledger is append-only).
- No OOS row was read; the OOS window is the published lab window (BRIEF caveat).

## 8. Files

- `finalize_chain.nohup`
- `operating_point.py`
- `results_5minute.json`
- `results_minute.json`
- `run_5minute.log`
- `run_minute.log`
- `sizing_verdict.json`
- `sizing_verdict.log`
- `sizing_verdict.py`
- `write_findings.log`
- `write_findings.py`
