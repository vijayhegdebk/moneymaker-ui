# online_learner: the walk-forward learn-after-each-trade take / skip policy with the trade journal (IS only, 2026-09-29)

BRIEF addendum 4 (learning after each trade, the journal) composed with rl.py (addendum 6) under both judges' fixes of DESIGN_PANEL decision-making-1 (full-information rewards, the harness splitter's judgement, the kept-share / kept-n floors, the top-1%-removed value) and the program rules of 2026-09-29 12:55 UTC (null tapes, declared columns). Scripts: `online.py` (the module `oos_once.py` continues through OOS), `run_online.py` (fit / score / checks per timeframe), `finalize.py` (family statistics, selection, tapes, candidate), `write_findings.py`; logs `run_<tf>.log`, `finalize.log`, `smoke_timing.log`. Every kept-vs-skipped number is a `harness.score` row of family `online/<design>/<learner>/k<k>/<window>/<reward>` (the comparators: `online_comparator/*`). No OOS row was read. **The frozen feature shortlist has 0 clusters on both timeframes** (`features_shortlist/<tf>/shortlist.json`, sha 66f6e004… / 4747257f…), so the EMPTY-SHORTLIST RULE applies: the designed feature set is hour_bin one-hot + dir (`online/context/...`), and the two linear learners also run on the full as-of design as a labelled sensitivity (`online/full/...`, **outside the frozen shortlist** in every table and ledger note).

## 1. Definitions (fixed before the numbers)

```
unit / label   a harness row: a Foundation SETUP taken under the L1 (15:25) book; net = l1_net_inr (lot 65, 5 pts slippage,
                 lab.trade_charges); exit = Foundation L1 (studies/exit_policy: no exit variant rescues the book; the exit is
                 not learned here; rl.py's exit / size bandit is not duplicated: the action is take / skip plus lots).
  design         "context" = hour_bin one-hot + dir one-hot (the EMPTY-SHORTLIST RULE: the frozen shortlist has 0 clusters on
                 both timeframes) + a bias column; "full" = every harness.Table.asof_columns() column except the calendar
                 proxies harness.TIME_PROXIES (`sl`, `n_events_asof`, refused at the candidate by go_no_go, so excluded from the
                 design from the start and reported, not silently dropped), encoded as harness.design does (numeric as is,
                 booleans 0/1, text one-hot over the levels present on the real table's IS rows, <= 16 levels), plus a missing
                 indicator `<col>__na` for every numeric column with a NaN on IS, standardised ONLINE per column with the
                 running mean / std of the PAST rows only (Welford; a row's z uses the rows processed before it; NaN -> 0 with
                 the indicator 1; |z| clipped at 5; a column with < 2 past values or zero spread -> 0), plus a bias column.
                 The encoded column list (`cfg["encoded"]`) is frozen from the real IS table so the same learner replays on a
                 null tape or on OOS rows (a level unseen on IS is all-zero). "full" is labelled "outside the frozen shortlist"
                 everywhere.
  cadence_k      the model is refitted when >= k closed outcomes are pending (k in {1, 10, 50}); pending outcomes wait.
  window         "anchored" = every closed outcome so far; N in {300, 1000} = the last N closed outcomes (exit order).
  reward         "net" = the L1 net; "pf" = net with losses x 1.5 (rl.py's `pf` reward). For the linear reward learner and the
                 boosted regressor the reward enters the FIT target; for the win-label learners (logistic, boosted classifier)
                 it enters the DECISION as L -> 1.5 L (the profit-factor surrogate on the loss side).
  learners       lints    Bayesian linear regression of the take reward on x (ridge prior precision 1.0, rl.LinTS's arm model;
                          skip = 0): A = ridge I + X'X, b = X'r over the window, mu = A^-1 b; the reward is rl.reward_of's
                          per-lot value: net / (LOT x BASE_STOP) clipped to +-CLIP (rl.py BASE_STOP 50, CLIP 10), x 1.5 when
                          negative under `pf`. Decision: take iff x . (mu + explore x chol(A^-1) z) > 0 (explore 0 = the
                          posterior mean; explore 0.3 = linear Thompson sampling).
                 logts    Bayesian logistic regression of the win label (Laplace approximation: MAP by Newton / IRLS with a
                          Gaussian prior of precision 1.0, warm-started from the previous fit, stop when max |step| < 1e-6 or
                          25 steps; H = ridge I + X' diag(p(1-p)) X). Decision: p = sigmoid(x . (w + explore x chol(H^-1) z));
                          take iff p W - (1 - p) L > 0 with W = the running mean net of the closed winners and L = the running
                          mean |net| of the closed losers (class-conditional means over every closed SETUP; L x 1.5 under `pf`;
                          before the first closed winner W := L).
                 hgb_reg  HistGradientBoostingRegressor (squared error, 100 iterations, learning rate 0.1, <= 15 leaves, min
                          leaf 50 (minute) / 20 (5minute), l2 1.0, no early stopping, seeded) refit every k closed outcomes on
                          the window's net winsorised at the window's own 1st / 99th percentiles (x 1.5 for losses under `pf`);
                          take iff the prediction > 0.
                 hgb_cls  the same booster as a classifier on the win label with sample weight |net| winsorised at the window's
                          99th percentile (mean 1) and class_weight balanced (the importance study's weighting); take iff
                          p >= tau, tau NESTED IN THE PAST: chosen at every refit on the record of the policy's own earlier
                          predictions (each made before its outcome was known, so an honest walk-forward sample) as the grid
                          value 0.05..0.95 (step 0.01) maximising the kept mean (penalised) net subject to kept share >= 20%
                          and kept n >= 50 of the record; fallback 0.5 while the record holds < 100 closed rows. One tau per
                          decision-side reward (the `net` head's on the record's net, the `pf` head's on the penalised net).
  warm-up        until 30 closed outcomes have been applied the policy takes every SETUP with 1 lot (the Foundation book is
                 the prior; `warmup_min_closed`, `warmup_policy` are cfg keys).
  sizing         lots in {0, 1, 2, 3} by half Kelly (fraction 0.5) on the calibrated p_win and the running W / L: for a bet
                 paying b = W / L to 1, f* = p - (1 - p) / b (Kelly 1956; MacLean, Thorp & Ziemba 2010), f = 0.5 f*, INR at
                 risk = f x capital, lots = clip(floor(f x capital / L), 0, max_lots = 3) with capital = 3 x futures_margin
                 120,000 + 60,000 buffer = 420,000 (strategy files; DESIGN_PANEL decision-making-5) and L (the running mean
                 loss) as one lot's risk; lots = 0 for a skip. p_win = the record-calibrated probability: the win rate of the
                 closed SETUPs whose model score fell in the same score decile as the current one (deciles of the record,
                 >= 100 closed rows and >= 20 in the bin, else the record's win rate, else 0.5). Daily loss stop: a cfg key,
                 value None (studies/session_stop: no session memory). The gate statistic (the ledger keep mask) is lots-free;
                 lots enter the journal's sized book only.
  journal        one row per SETUP: time, setup_i, session, dir, hour_bin, features (the context vector inline; the full
                 vector by row reference into features_full_<tf>.parquet plus its sha), n_closed (outcomes applied),
                 n_pending, decision, reason (which term won), score, p_model, p_win (calibrated), tau, W, L, kelly_f, lots,
                 state (model-state id: sha1 of the fitted parameters + update count; "prior:0" before the first refit), fill
                 (the SETUP close: the Foundation enters at the SETUP bar's close), exit_time, exit_reason, mfe_pts, mae_pts,
                 pts, gross, costs, net, R (= net / (stop distance x 65)), running equity / drawdown / rolling profit factor
                 (last 100 closed taken trades) of the 1-lot book and the sized book AS OF the decision (closed before this
                 bar), taken_net (net x lots when taken).
  determinism    the same cfg + seed reproduces decisions, journal and state ids bit for bit (asserted by the driver: run
                 twice, compare); truncation: the run on the rows before 2025-06-30 12:00, and the run on the truncated build
                 `data/<tf>/trunc_20250630_120000`, give the same decisions for every SETUP before the cut (asserted).
  threads        every BLAS / OpenMP pool is limited to one thread inside run_heads (threadpoolctl) so reductions are
                 bit-reproducible.
```

Grid (the task's, nothing shrunk): cadence k in {1, 10, 50} x window {anchored, last 300, last 1000 closed} x reward {net, pf} x learner {lints, logts, hgb_reg, hgb_cls} on the context design; {lints, logts} on the full design; explore {0.0, 0.3} for the two linear learners with 5 seeds (1..5) at explore 0.3; HGB seeded 0. One fit sequence per (design, learner, k, window, fit reward), one ledger row per decision head. Judgement = `harness.score` on the path's keep mask (the path IS the test: no CV); selection = the highest walk-forward profit factor of the taken 1-lot book among the rows that pass the row-level go / no-go items, then the full `harness.go_no_go` (family PBO on `diff`, studentised SPA over the family, DSR, block bootstrap, null-tape replay of the learner on every certificate tape, declared columns). rl.py conventions reused and cited: LinTS per action with a ridge prior (rl.LinTS), full-information updates in exit order (rl.walk's queue), one Gaussian draw per SETUP whatever the decision (rl.LinTS.choose), the reward unit net / (lot x 50) clipped +-10 with `pf` = losses x 1.5 (rl.reward_of, BASE_STOP, CLIP). rl.py's exit / size bandit is not duplicated: the exit is Foundation L1 (studies/exit_policy: no exit variant rescues the book) and the action here is take / skip plus lots.

Static comparators on the same rows: take-all (the raw book), the frozen ST7/ST8 gate (`fz_traded`), the gate_family finalist's OOF decisions if `studies/gate_family/oof_<tf>.parquet` exists at scoring time (it did not: that study was still running; recorded as absent). Prior findings the study does not re-run: H1 (the frozen gate is not a loser filter), H2 / H3 / H4 (null on both timeframes), session_stop (no session memory shown: the daily loss stop key is None), null_tapes_drift (the certificate and the time proxies `sl`, `n_events_asof`, excluded from the full design from the start and reported here rather than dropped silently), importance (the empty shortlist).

## 2. 5minute

Designs: context = 12 columns (11 one-hot levels of hour_bin / dir + bias); full = 294 columns (152 source columns, 59 missing indicators, bias; without `sl`, `n_events_asof`), standardised online. Paths (ledger rows): 468 (context 252, full 216).

### Comparators (family `online_comparator/*`)

| comparator | ledger id | kept n | kept share | kept mean | skipped mean | diff | kept PF | control pct | perm p | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|
| take_all | `795d53ca33802620` | 826 | 1.0000 | -757.05 | - | - | 0.639 | - | - | - |
| frozen_st7_st8 | `e091066c98af187c` | 325 | 0.3935 | -978.81 | -613.20 | -365.62 | 0.563 | 12.7 | 0.2554 | 3 |
| gate_family_oof/context/bag4 | `e152f57ee17327da` | 819 | 0.9915 | -771.80 | 968.07 | -1,739.87 | 0.632 | 51.8 | 0.3058 | 0 |
| gate_family_oof/context/hgbc | `8897ac7523cd4a4b` | 765 | 0.9262 | -827.91 | 131.57 | -959.48 | 0.617 | 1.9 | 0.1084 | 5 |
| gate_family_oof/context/hgbr | `93c6f749ed37341b` | 734 | 0.8886 | -885.18 | 265.17 | -1,150.35 | 0.584 | 95.7 | 0.0205 | 7 |
| gate_family_oof/context/pt1 | `f0fa0f15b8f3f688` | 794 | 0.9613 | -791.20 | 90.31 | -881.52 | 0.628 | 22.8 | 0.2784 | 1 |
| gate_family_oof/context/pt2 | `b004e46fa4b836a6` | 491 | 0.5944 | -699.21 | -841.83 | 142.62 | 0.672 | 80.2 | 0.6732 | 5 |
| gate_family_oof/context/pt3 | `251e5940fb6b14de` | 434 | 0.5254 | -860.88 | -642.11 | -218.77 | 0.611 | 14.9 | 0.4893 | 5 |
| gate_family_oof/context/scorecard | `d2ecb14c8b9a2e46` | 812 | 0.9831 | -755.92 | -822.49 | 66.56 | 0.639 | 94.1 | 0.9570 | 2 |
| gate_family_oof/h5_full/dt3 | `09864e169a147a5b` | 793 | 0.9600 | -754.51 | -818.14 | 63.63 | 0.637 | 95.8 | 0.9415 | 4 |
| gate_family_oof/h5_full/h5rules | `1b17e868368d3f90` | 183 | 0.2215 | -595.02 | -803.17 | 208.14 | 0.742 | 47.1 | 0.5717 | 8 |
| gate_family_oof/h5_full/hgbc | `85609292abd34abb` | 790 | 0.9564 | -740.20 | -1,126.95 | 386.75 | 0.650 | 45.2 | 0.6197 | 7 |
| gate_family_oof/h5_full/scorecard | `a95e69eb73313fdf` | 824 | 0.9976 | -752.40 | -2,675.05 | 1,922.65 | 0.641 | 62.8 | 0.5082 | 1 |

### Finalists: the best path by walk-forward kept PF per (design, learner)

| ledger id | path (design/learner/k/window/reward explore seed) | kept n | kept share | kept mean | skipped mean | diff | diff top1% removed | kept PF (1 lot) | sized PF | control pct | perm p | sign blocks | kept mean slip 8 | loser recall | winner recall (net-wtd) | top-decile winners skipped | row-level pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `e24ac736ebbfa6d5` | context/logts/k10/300/net e0.0 s0 | 140 | 0.1695 | -109.36 | -889.23 | **779.87** | 518.65 | 0.942 | 0.645 | 85.2 | 0.0665 | 4 | -499.33 | 0.854 | 0.224 | 0.783 | no |
| `26e4d18d50b7ee01` | context/lints/k10/anchored/pf e0.3 s5 | 62 | 0.0751 | -158.97 | -805.59 | **646.62** | 549.53 | 0.926 | 0.688 | 0.1 | 0.2734 | 4 | -548.93 | 0.935 | 0.111 | 0.913 | no |
| `4d0b2708b7798f80` | full/logts/k10/anchored/net e0.3 s4 (outside the frozen shortlist) | 432 | 0.5230 | -561.06 | -971.94 | **410.88** | 487.43 | 0.718 | 0.712 | 61.4 | 0.1864 | 9 | -951.03 | 0.489 | 0.556 | 0.478 | no |
| `e53061ce54722fbc` | full/lints/k1/anchored/pf e0.3 s1 (outside the frozen shortlist) | 289 | 0.3499 | -566.72 | -859.48 | **292.76** | 438.57 | 0.698 | 0.466 | 85.8 | 0.3863 | 6 | -956.69 | 0.658 | 0.341 | 0.739 | no |
| `8c50ca7ee6910430` | context/hgb_cls/k10/anchored/net e0.0 s0 | 525 | 0.6356 | -684.91 | -882.87 | **197.96** | -34.55 | 0.688 | 0.713 | 14.8 | 0.5277 | 7 | -1,074.88 | 0.380 | 0.715 | 0.261 | no |
| `2c148b95f5668db2` | context/hgb_reg/k50/300/net e0.0 s0 | 173 | 0.2094 | -638.04 | -788.58 | **150.54** | 3.06 | 0.686 | 0.500 | 4.6 | 0.6982 | 5 | -1,028.01 | 0.801 | 0.217 | 0.739 | no |

### The 25 paths with the highest walk-forward kept PF (all rows: `results/5minute/scores.jsonl`, `all_rows` in `finalize.json`)

| ledger id | path (design/learner/k/window/reward explore seed) | kept n | kept share | kept mean | skipped mean | diff | diff top1% removed | kept PF (1 lot) | sized PF | control pct | perm p | sign blocks | kept mean slip 8 | loser recall | winner recall (net-wtd) | top-decile winners skipped | row-level pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `e24ac736ebbfa6d5` | context/logts/k10/300/net e0.0 s0 | 140 | 0.1695 | -109.36 | -889.23 | **779.87** | 518.65 | 0.942 | 0.645 | 85.2 | 0.0665 | 4 | -499.33 | 0.854 | 0.224 | 0.783 | no |
| `26e4d18d50b7ee01` | context/lints/k10/anchored/pf e0.3 s5 | 62 | 0.0751 | -158.97 | -805.59 | **646.62** | 549.53 | 0.926 | 0.688 | 0.1 | 0.2734 | 4 | -548.93 | 0.935 | 0.111 | 0.913 | no |
| `2ea17c9fa4380e17` | context/lints/k10/1000/pf e0.3 s5 | 62 | 0.0751 | -158.97 | -805.59 | **646.62** | 549.53 | 0.926 | 0.688 | 0.3 | 0.2544 | 4 | -548.93 | 0.935 | 0.111 | 0.913 | no |
| `2c0062ee6ebad116` | context/lints/k50/300/pf e0.3 s4 | 78 | 0.0944 | -191.62 | -816.01 | **624.39** | 304.01 | 0.912 | 0.728 | 3.0 | 0.2444 | 4 | -581.59 | 0.918 | 0.140 | 0.870 | no |
| `4c84d0979206ffda` | context/lints/k1/300/pf e0.3 s5 | 62 | 0.0751 | -212.78 | -801.22 | **588.44** | 490.42 | 0.903 | 0.783 | 0.2 | 0.3113 | 3 | -602.74 | 0.933 | 0.110 | 0.913 | no |
| `2f05ec7c41487e38` | context/logts/k1/300/net e0.3 s5 | 138 | 0.1671 | -185.47 | -871.70 | **686.24** | 416.26 | 0.902 | 0.619 | 74.7 | 0.1129 | 4 | -575.43 | 0.853 | 0.212 | 0.783 | no |
| `cb7893869c89e6ee` | context/lints/k50/300/pf e0.0 s0 | 80 | 0.0969 | -209.72 | -815.75 | **606.03** | 298.67 | 0.902 | 0.728 | 2.2 | 0.2459 | 4 | -599.68 | 0.916 | 0.140 | 0.870 | no |
| `38d028e86692749b` | context/logts/k10/300/net e0.3 s5 | 138 | 0.1671 | -208.44 | -867.09 | **658.65** | 388.12 | 0.891 | 0.583 | 76.0 | 0.1114 | 4 | -598.41 | 0.854 | 0.211 | 0.783 | no |
| `ebf334906956b1e1` | context/lints/k50/300/pf e0.3 s5 | 81 | 0.0981 | -241.05 | -813.15 | **572.11** | 270.43 | 0.888 | 0.728 | 4.3 | 0.2694 | 4 | -631.01 | 0.915 | 0.140 | 0.870 | no |
| `aa4bdb15cb7e4ab4` | context/lints/k1/anchored/pf e0.3 s5 | 64 | 0.0775 | -262.28 | -798.61 | **536.33** | 447.80 | 0.880 | 0.783 | 0.2 | 0.3728 | 3 | -652.24 | 0.931 | 0.111 | 0.913 | no |
| `0523d1e0b3c479a6` | context/lints/k1/1000/pf e0.3 s5 | 64 | 0.0775 | -262.28 | -798.61 | **536.33** | 447.80 | 0.880 | 0.783 | 0.3 | 0.3533 | 3 | -652.24 | 0.931 | 0.111 | 0.913 | no |
| `42791db035a34138` | context/lints/k50/300/pf e0.3 s1 | 81 | 0.0981 | -270.68 | -809.93 | **539.26** | 236.80 | 0.876 | 0.697 | 1.5 | 0.3178 | 5 | -660.64 | 0.915 | 0.140 | 0.870 | no |
| `087cba1e5ad6a046` | context/logts/k1/300/net e0.0 s0 | 139 | 0.1683 | -227.94 | -864.11 | **636.17** | 537.51 | 0.875 | 0.549 | 86.2 | 0.1209 | 3 | -617.90 | 0.856 | 0.200 | 0.870 | no |
| `117fe4c26cd41c69` | context/lints/k10/300/pf e0.3 s5 | 59 | 0.0714 | -276.77 | -794.00 | **517.23** | 401.31 | 0.873 | 0.731 | 0.3 | 0.3918 | 3 | -666.73 | 0.936 | 0.102 | 0.913 | no |
| `a5337fbe0b2413dd` | context/logts/k10/anchored/net e0.0 s0 | 171 | 0.2070 | -248.32 | -889.87 | **641.54** | 337.31 | 0.871 | 0.567 | 91.4 | 0.1074 | 6 | -638.29 | 0.811 | 0.258 | 0.739 | no |
| `9d7889741771fdeb` | context/logts/k10/1000/net e0.0 s0 | 171 | 0.2070 | -248.32 | -889.87 | **641.54** | 337.31 | 0.871 | 0.567 | 92.0 | 0.0970 | 6 | -638.29 | 0.811 | 0.258 | 0.739 | no |
| `e84c41bb82929deb` | context/lints/k50/300/pf e0.3 s2 | 83 | 0.1005 | -278.43 | -810.52 | **532.09** | 242.03 | 0.871 | 0.728 | 1.4 | 0.3038 | 5 | -668.39 | 0.913 | 0.141 | 0.870 | no |
| `f14da81724be99e9` | context/lints/k50/anchored/pf e0.0 s0 | 83 | 0.1005 | -283.70 | -809.93 | **526.23** | 236.03 | 0.868 | 0.728 | 2.0 | 0.3058 | 4 | -673.67 | 0.911 | 0.140 | 0.870 | no |
| `627a578a9b0b5780` | context/lints/k50/1000/pf e0.0 s0 | 83 | 0.1005 | -283.70 | -809.93 | **526.23** | 236.03 | 0.868 | 0.728 | 2.0 | 0.3178 | 4 | -673.67 | 0.911 | 0.140 | 0.870 | no |
| `5640408839fa7148` | context/lints/k50/anchored/pf e0.3 s5 | 84 | 0.1017 | -313.03 | -807.32 | **494.29** | 209.43 | 0.855 | 0.728 | 2.8 | 0.3398 | 4 | -703.00 | 0.909 | 0.140 | 0.870 | no |
| `231951e5da26df09` | context/lints/k50/1000/pf e0.3 s5 | 84 | 0.1017 | -313.03 | -807.32 | **494.29** | 209.43 | 0.855 | 0.728 | 3.0 | 0.3363 | 4 | -703.00 | 0.909 | 0.140 | 0.870 | no |
| `2577a2a622338d3f` | context/logts/k10/300/net e0.3 s4 | 130 | 0.1574 | -284.13 | -845.39 | **561.26** | 437.94 | 0.854 | 0.537 | 43.3 | 0.1949 | 3 | -674.09 | 0.858 | 0.195 | 0.826 | no |
| `be6060f9302eb9b1` | context/logts/k10/300/net e0.3 s3 | 145 | 0.1755 | -282.26 | -858.15 | **575.89** | 143.15 | 0.853 | 0.623 | 68.2 | 0.1554 | 5 | -672.22 | 0.844 | 0.214 | 0.826 | no |
| `fb74f95f696304a8` | context/logts/k1/300/net e0.3 s4 | 136 | 0.1646 | -288.40 | -849.42 | **561.02** | 453.75 | 0.851 | 0.501 | 48.9 | 0.1874 | 5 | -678.37 | 0.854 | 0.203 | 0.826 | no |
| `32309173620321a8` | context/lints/k50/anchored/pf e0.3 s1 | 83 | 0.1005 | -344.90 | -803.09 | **458.19** | 166.42 | 0.844 | 0.697 | 0.8 | 0.3838 | 4 | -734.86 | 0.911 | 0.140 | 0.870 | no |

### Family summary by learner and design (mean over paths; every path is a ledger row)

| design | learner | paths | kept share mean | diff mean | diff min / max | diff > 0 | kept PF mean | control pct mean | control >= 95 | row-level passes |
|---|---|---|---|---|---|---|---|---|---|---|
| context | lints | 108 | 0.1268 | 177.72 | -398.73 / 646.62 | 82 | 0.732 | 9.3 | 0 | 0 |
| context | logts | 108 | 0.1439 | 19.15 | -780.69 / 779.87 | 60 | 0.654 | 37.5 | 0 | 0 |
| context | hgb_reg | 18 | 0.1466 | -263.47 | -499.22 / 150.54 | 2 | 0.536 | 4.9 | 0 | 0 |
| context | hgb_cls | 18 | 0.5942 | 36.23 | -157.03 / 197.96 | 12 | 0.660 | 9.5 | 0 | 0 |
| full (outside the frozen shortlist) | lints | 108 | 0.4170 | -78.89 | -697.71 / 292.76 | 50 | 0.611 | 62.9 | 1 | 0 |
| full (outside the frozen shortlist) | logts | 108 | 0.5158 | -174.62 | -477.93 / 410.88 | 36 | 0.604 | 37.9 | 0 | 0 |

### Seed spread of the Thompson heads (explore 0.3, seeds 1..5; per family of 5 rows)

| family | seeds | diff mean | diff sd | diff min / max | diff > 0 | kept PF mean | kept PF sd | kept share mean |
|---|---|---|---|---|---|---|---|---|
| online/context/lints/k1/1000/net | 5 | -99.28 | 187.37 | -398.73 / 121.15 | 1 | 0.638 | 0.051 | 0.1697 |
| online/context/lints/k1/1000/pf | 5 | 181.33 | 208.29 | -10.96 / 536.33 | 4 | 0.740 | 0.081 | 0.0794 |
| online/context/lints/k1/300/net | 5 | 186.78 | 131.20 | -36.11 / 306.13 | 4 | 0.721 | 0.044 | 0.1484 |
| online/context/lints/k1/300/pf | 5 | 227.90 | 217.51 | 5.07 / 588.44 | 5 | 0.759 | 0.084 | 0.0773 |
| online/context/lints/k1/anchored/net | 5 | -99.28 | 187.37 | -398.73 / 121.15 | 1 | 0.638 | 0.051 | 0.1697 |
| online/context/lints/k1/anchored/pf | 5 | 181.33 | 208.29 | -10.96 / 536.33 | 4 | 0.740 | 0.081 | 0.0794 |
| online/context/lints/k10/1000/net | 5 | -68.27 | 201.06 | -373.87 / 126.20 | 3 | 0.648 | 0.059 | 0.1668 |
| online/context/lints/k10/1000/pf | 5 | 199.67 | 288.54 | -77.67 / 646.62 | 3 | 0.751 | 0.112 | 0.0770 |
| online/context/lints/k10/300/net | 5 | 318.82 | 108.54 | 234.59 / 498.94 | 5 | 0.761 | 0.045 | 0.1458 |
| online/context/lints/k10/300/pf | 5 | 223.61 | 234.90 | -28.42 / 517.23 | 4 | 0.759 | 0.091 | 0.0743 |
| online/context/lints/k10/anchored/net | 5 | -68.27 | 201.06 | -373.87 / 126.20 | 3 | 0.648 | 0.059 | 0.1668 |
| online/context/lints/k10/anchored/pf | 5 | 199.67 | 288.54 | -77.67 / 646.62 | 3 | 0.751 | 0.112 | 0.0770 |
| online/context/lints/k50/1000/net | 5 | 90.61 | 154.85 | -41.37 / 352.59 | 4 | 0.688 | 0.051 | 0.1908 |
| online/context/lints/k50/1000/pf | 5 | 437.28 | 45.50 | 370.42 / 494.29 | 5 | 0.835 | 0.016 | 0.1017 |
| online/context/lints/k50/300/net | 5 | 369.24 | 108.12 | 193.03 / 482.17 | 5 | 0.768 | 0.045 | 0.1746 |
| online/context/lints/k50/300/pf | 5 | 542.24 | 66.21 | 443.33 / 624.39 | 5 | 0.878 | 0.026 | 0.0981 |
| online/context/lints/k50/anchored/net | 5 | 90.61 | 154.85 | -41.37 / 352.59 | 4 | 0.688 | 0.051 | 0.1908 |
| online/context/lints/k50/anchored/pf | 5 | 437.28 | 45.50 | 370.42 / 494.29 | 5 | 0.835 | 0.016 | 0.1017 |
| online/context/logts/k1/1000/net | 5 | 104.96 | 287.69 | -289.38 / 432.15 | 3 | 0.683 | 0.092 | 0.2099 |
| online/context/logts/k1/1000/pf | 5 | -317.99 | 244.74 | -615.63 / 46.38 | 1 | 0.531 | 0.090 | 0.0768 |
| online/context/logts/k1/300/net | 5 | 371.28 | 265.93 | 81.09 / 686.24 | 5 | 0.775 | 0.105 | 0.1671 |
| online/context/logts/k1/300/pf | 5 | -297.00 | 200.63 | -571.08 / -15.47 | 0 | 0.535 | 0.076 | 0.0767 |
| online/context/logts/k1/anchored/net | 5 | 104.96 | 287.69 | -289.38 / 432.15 | 3 | 0.683 | 0.092 | 0.2099 |
| online/context/logts/k1/anchored/pf | 5 | -317.99 | 244.74 | -615.63 / 46.38 | 1 | 0.531 | 0.090 | 0.0768 |
| online/context/logts/k10/1000/net | 5 | 193.87 | 171.02 | -23.25 / 405.08 | 4 | 0.712 | 0.057 | 0.2092 |
| online/context/logts/k10/1000/pf | 5 | -288.49 | 361.29 | -589.47 / 295.64 | 1 | 0.548 | 0.133 | 0.0768 |
| online/context/logts/k10/300/net | 5 | 481.36 | 178.29 | 209.21 / 658.65 | 5 | 0.818 | 0.073 | 0.1654 |
| online/context/logts/k10/300/pf | 5 | -292.94 | 286.35 | -543.17 / 119.05 | 1 | 0.543 | 0.101 | 0.0758 |
| online/context/logts/k10/anchored/net | 5 | 193.87 | 171.02 | -23.25 / 405.08 | 4 | 0.712 | 0.057 | 0.2092 |
| online/context/logts/k10/anchored/pf | 5 | -288.49 | 361.29 | -589.47 / 295.64 | 1 | 0.548 | 0.133 | 0.0768 |
| online/context/logts/k50/1000/net | 5 | 139.29 | 197.24 | -43.62 / 460.85 | 4 | 0.697 | 0.066 | 0.2305 |
| online/context/logts/k50/1000/pf | 5 | -49.13 | 365.74 | -447.61 / 441.23 | 3 | 0.648 | 0.133 | 0.1077 |
| online/context/logts/k50/300/net | 5 | 437.06 | 75.75 | 312.82 / 509.36 | 5 | 0.795 | 0.027 | 0.1911 |
| online/context/logts/k50/300/pf | 5 | -27.48 | 302.41 | -414.83 / 300.66 | 3 | 0.655 | 0.110 | 0.1041 |
| online/context/logts/k50/anchored/net | 5 | 139.29 | 197.24 | -43.62 / 460.85 | 4 | 0.697 | 0.066 | 0.2305 |
| online/context/logts/k50/anchored/pf | 5 | -49.13 | 365.74 | -447.61 / 441.23 | 3 | 0.648 | 0.133 | 0.1077 |
| online/full/lints/k1/1000/net (outside the frozen shortlist) | 5 | -112.86 | 194.37 | -274.74 / 215.15 | 1 | 0.599 | 0.047 | 0.4383 |
| online/full/lints/k1/1000/pf (outside the frozen shortlist) | 5 | 156.53 | 118.24 | -9.40 / 292.76 | 4 | 0.660 | 0.032 | 0.3533 |
| online/full/lints/k1/300/net (outside the frozen shortlist) | 5 | -481.06 | 124.93 | -609.08 / -307.34 | 0 | 0.537 | 0.023 | 0.4734 |
| online/full/lints/k1/300/pf (outside the frozen shortlist) | 5 | -238.98 | 188.64 | -564.33 / -89.51 | 0 | 0.573 | 0.038 | 0.3956 |
| online/full/lints/k1/anchored/net (outside the frozen shortlist) | 5 | -112.86 | 194.37 | -274.74 / 215.15 | 1 | 0.599 | 0.047 | 0.4383 |
| online/full/lints/k1/anchored/pf (outside the frozen shortlist) | 5 | 156.53 | 118.24 | -9.40 / 292.76 | 4 | 0.660 | 0.032 | 0.3533 |
| online/full/lints/k10/1000/net (outside the frozen shortlist) | 5 | -101.95 | 159.41 | -296.71 / 28.18 | 3 | 0.601 | 0.038 | 0.4404 |
| online/full/lints/k10/1000/pf (outside the frozen shortlist) | 5 | 74.96 | 70.26 | -11.41 / 158.57 | 4 | 0.638 | 0.018 | 0.3644 |
| online/full/lints/k10/300/net (outside the frozen shortlist) | 5 | -526.24 | 106.84 | -697.71 / -408.62 | 0 | 0.528 | 0.022 | 0.4780 |
| online/full/lints/k10/300/pf (outside the frozen shortlist) | 5 | -362.35 | 113.99 | -515.96 / -216.91 | 0 | 0.542 | 0.026 | 0.4104 |
| online/full/lints/k10/anchored/net (outside the frozen shortlist) | 5 | -101.95 | 159.41 | -296.71 / 28.18 | 3 | 0.601 | 0.038 | 0.4404 |
| online/full/lints/k10/anchored/pf (outside the frozen shortlist) | 5 | 74.96 | 70.26 | -11.41 / 158.57 | 4 | 0.638 | 0.018 | 0.3644 |
| online/full/lints/k50/1000/net (outside the frozen shortlist) | 5 | 88.16 | 95.55 | -81.05 / 146.29 | 4 | 0.652 | 0.022 | 0.4516 |
| online/full/lints/k50/1000/pf (outside the frozen shortlist) | 5 | 210.58 | 67.25 | 93.36 / 260.34 | 5 | 0.679 | 0.020 | 0.3787 |
| online/full/lints/k50/300/net (outside the frozen shortlist) | 5 | -167.85 | 119.02 | -376.03 / -79.78 | 0 | 0.601 | 0.023 | 0.4901 |
| online/full/lints/k50/300/pf (outside the frozen shortlist) | 5 | -106.83 | 149.59 | -350.80 / 21.75 | 2 | 0.604 | 0.033 | 0.4305 |
| online/full/lints/k50/anchored/net (outside the frozen shortlist) | 5 | 88.16 | 95.55 | -81.05 / 146.29 | 4 | 0.652 | 0.022 | 0.4516 |
| online/full/lints/k50/anchored/pf (outside the frozen shortlist) | 5 | 210.58 | 67.25 | 93.36 / 260.34 | 5 | 0.679 | 0.020 | 0.3787 |
| online/full/logts/k1/1000/net (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k1/1000/pf (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k1/300/net (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k1/300/pf (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k1/anchored/net (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k1/anchored/pf (outside the frozen shortlist) | 5 | -477.93 | 0.00 | -477.93 / -477.93 | 0 | 0.538 | 0.000 | 0.5182 |
| online/full/logts/k10/1000/net (outside the frozen shortlist) | 5 | 332.51 | 71.79 | 237.94 / 410.88 | 5 | 0.701 | 0.015 | 0.5218 |
| online/full/logts/k10/1000/pf (outside the frozen shortlist) | 5 | 308.90 | 46.78 | 247.37 / 361.81 | 5 | 0.696 | 0.010 | 0.5196 |
| online/full/logts/k10/300/net (outside the frozen shortlist) | 5 | 332.51 | 71.79 | 237.94 / 410.88 | 5 | 0.701 | 0.015 | 0.5218 |
| online/full/logts/k10/300/pf (outside the frozen shortlist) | 5 | 308.90 | 46.78 | 247.37 / 361.81 | 5 | 0.696 | 0.010 | 0.5196 |
| online/full/logts/k10/anchored/net (outside the frozen shortlist) | 5 | 332.51 | 71.79 | 237.94 / 410.88 | 5 | 0.701 | 0.015 | 0.5218 |
| online/full/logts/k10/anchored/pf (outside the frozen shortlist) | 5 | 308.90 | 46.78 | 247.37 / 361.81 | 5 | 0.696 | 0.010 | 0.5196 |
| online/full/logts/k50/1000/net (outside the frozen shortlist) | 5 | -356.51 | 27.48 | -393.34 / -319.25 | 0 | 0.578 | 0.005 | 0.5092 |
| online/full/logts/k50/1000/pf (outside the frozen shortlist) | 5 | -390.31 | 53.94 | -462.31 / -348.74 | 0 | 0.572 | 0.010 | 0.5068 |
| online/full/logts/k50/300/net (outside the frozen shortlist) | 5 | -356.51 | 27.48 | -393.34 / -319.25 | 0 | 0.578 | 0.005 | 0.5092 |
| online/full/logts/k50/300/pf (outside the frozen shortlist) | 5 | -390.31 | 53.94 | -462.31 / -348.74 | 0 | 0.572 | 0.010 | 0.5068 |
| online/full/logts/k50/anchored/net (outside the frozen shortlist) | 5 | -356.51 | 27.48 | -393.34 / -319.25 | 0 | 0.578 | 0.005 | 0.5092 |
| online/full/logts/k50/anchored/pf (outside the frozen shortlist) | 5 | -390.31 | 53.94 | -462.31 / -348.74 | 0 | 0.572 | 0.010 | 0.5068 |

### Learning curves of the finalists (every 250 SETUPs; `curve_summary` in `finalize.json`; the control percentile = `fz_report.random_control`, 2,000 draws, at the path's own per-session take count on the prefix)

**context/logts** `e24ac736ebbfa6d5` (context/logts/k10/300/net e0.0 s0): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 101 | 0.4040 | 1,152.98 | 280.97 | 1.150 | 93.5 | 0.0720 | 28,377.89 | -101,551.39 |
| 500 | 140 | 0.2800 | 888.67 | -109.36 | 0.942 | 85.0 | 0.0340 | -15,310.48 | -374,600.69 |
| 750 | 140 | 0.1867 | 862.44 | -109.36 | 0.942 | 85.5 | 0.0400 | -15,310.48 | -608,105.97 |
| 826 | 140 | 0.1695 | 779.87 | -109.36 | 0.942 | 86.1 | 0.0600 | -15,310.48 | -625,325.16 |

**context/lints** `26e4d18d50b7ee01` (context/lints/k10/anchored/pf e0.3 s5): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 50 | 0.2000 | 482.16 | -20.48 | 0.990 | 2.1 | 0.5407 | -1,023.84 | -101,551.39 |
| 500 | 60 | 0.1200 | 555.93 | -259.98 | 0.879 | 0.1 | 0.3383 | -15,599.08 | -374,600.69 |
| 750 | 62 | 0.0827 | 710.58 | -158.97 | 0.926 | 0.1 | 0.2319 | -9,855.87 | -608,105.97 |
| 826 | 62 | 0.0751 | 646.62 | -158.97 | 0.926 | 0.1 | 0.2754 | -9,855.87 | -625,325.16 |

**full/logts (outside the frozen shortlist)** `4d0b2708b7798f80` (full/logts/k10/anchored/net e0.3 s4): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 750; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 146 | 0.5840 | 68.52 | -377.70 | 0.811 | 85.3 | 0.9095 | -55,144.13 | -101,551.39 |
| 500 | 266 | 0.5320 | -81.65 | -787.41 | 0.603 | 49.9 | 0.8291 | -209,451.73 | -374,600.69 |
| 750 | 396 | 0.5280 | 219.06 | -707.41 | 0.655 | 55.6 | 0.5017 | -280,134.86 | -608,105.97 |
| 826 | 432 | 0.5230 | 410.88 | -561.06 | 0.718 | 62.8 | 0.1994 | -242,379.10 | -625,325.16 |

**full/lints (outside the frozen shortlist)** `e53061ce54722fbc` (full/lints/k1/anchored/pf e0.3 s1): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 127 | 0.5080 | 188.95 | -313.24 | 0.831 | 78.0 | 0.7661 | -39,781.59 | -101,551.39 |
| 500 | 224 | 0.4480 | 94.00 | -697.31 | 0.623 | 70.2 | 0.7906 | -156,198.03 | -374,600.69 |
| 750 | 274 | 0.3653 | 278.66 | -633.95 | 0.666 | 75.3 | 0.4408 | -173,703.40 | -608,105.97 |
| 826 | 289 | 0.3499 | 292.76 | -566.72 | 0.698 | 85.2 | 0.3688 | -163,783.24 | -625,325.16 |

**context/hgb_cls** `8c50ca7ee6910430` (context/hgb_cls/k10/anchored/net e0.0 s0): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 205 | 0.8200 | 161.43 | -377.15 | 0.816 | 37.0 | 0.8441 | -77,315.44 | -101,551.39 |
| 500 | 290 | 0.5800 | 415.90 | -574.52 | 0.717 | 14.8 | 0.2599 | -166,611.72 | -374,600.69 |
| 750 | 469 | 0.6253 | 163.86 | -749.41 | 0.667 | 6.4 | 0.6307 | -351,475.63 | -608,105.97 |
| 826 | 525 | 0.6356 | 197.96 | -684.91 | 0.688 | 13.1 | 0.5357 | -359,579.95 | -625,325.16 |

**context/hgb_reg** `2c148b95f5668db2` (context/hgb_reg/k50/300/net e0.0 s0): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 500; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 90 | 0.3600 | -28.02 | -424.14 | 0.782 | 19.3 | 0.9695 | -38,172.57 | -101,551.39 |
| 500 | 151 | 0.3020 | 361.71 | -496.73 | 0.724 | 12.9 | 0.3823 | -75,006.17 | -374,600.69 |
| 750 | 169 | 0.2253 | 253.06 | -614.77 | 0.698 | 4.9 | 0.5342 | -103,896.76 | -608,105.97 |
| 826 | 173 | 0.2094 | 150.54 | -638.04 | 0.686 | 4.2 | 0.7116 | -110,381.18 | -625,325.16 |

### Multiplicity over the online family (every `online/*` row of the timeframe, both designs)

| candidates | PBO (diff) | IS-best below 0 OOS | degradation slope | PBO (kept mean) | SPA p (studentised) | RC p | SPA p (unstudentised) | SPA best mean gain / session | excluded from studentised | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|
| 468 | **0.5330** | 0.5615 | -0.0119 | 0.4925 | **0.7605** | 0.8105 | 0.6285 | 111.47 | 55 | 3.58 |

| design | candidates | PBO (diff) | SPA p (studentised) | SPA p (unstudentised) | effective trials |
|---|---|---|---|---|---|
| context | 252 | 0.4978 | 0.6855 | 0.5175 | 2.43 |
| full (outside the frozen shortlist) | 216 | 0.3975 | 0.5145 | 0.4925 | 2.54 |

### Selection and go / no-go

Rows passing the row-level items (kept share, kept n, diff > 0, diff top-1%-removed > 0, kept mean at 8 pts > 0, sign blocks >= 8, control >= 95): **0** of 468. Selected (highest kept PF among them): none.

**`e24ac736ebbfa6d5`** (context/logts/k10/300/net e0.0 s0; the best-by-PF row of its design, for the record): full go / no-go **FAILED**; failing items: kept_share>=20%, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:session_same_sign>=0.75.

| item | ok | value |
|---|---|---|
| kept_share>=20% | no | 0.1695 |
| kept_n>=80 | yes | 140 |
| diff>0 | yes | 779.87 |
| diff_top1_removed>0 | yes | 518.65 |
| kept_mean_slip8>0 | no | -499.33 |
| sign_blocks>=8/12 | no | 4 |
| control_pct>=95 | no | 85.2 |
| pbo<=0.2 | no | 0.533 |
| dsr_p<0.1 | no | 0.9842 |
| spa_p<=0.10 | no | 0.7605 |
| boot_ci_excludes_0 | yes | [181.09, 1407.26] |
| null_tape:real_diff>gmm_p95 | yes | 616.89 |
| null_tape:real_diff>segment_p95 | yes | 492.49 |
| null_tape:session_same_sign>=0.75 | no | 0.5 |
| no_time_proxy_columns | yes | ["dir", "hour_bin"] |

Bootstrap (2,000 stationary draws of sessions): diff 90% CI [181.09, 1407.26], kept mean CI [-678.92, 513.54], P(diff <= 0) 0.0205. DSR of the per-session kept series against 468 trials: SR 0.0585, SR0 0.2517, p 0.9842.

Null-tape replay (the same cfg run on each certificate tape's own table; `tapes.null_tape_check_from_diffs`):

| generator | tapes | tape diff p50 | tape diff p95 | real diff | real pct among tapes | same sign share |
|---|---|---|---|---|---|---|
| gmm | 20 | -172.52 | 616.89 | 779.87 | 95.0 | - |
| segment | 20 | 116.81 | 492.49 | 779.87 | 100.0 | - |
| session | 20 | -75.36 | 692.74 | 779.87 | - | 0.500 |

**`4d0b2708b7798f80`** (full/logts/k10/anchored/net e0.3 s4 (outside the frozen shortlist); the best-by-PF row of its design, for the record): full go / no-go **FAILED**; failing items: kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:real_diff>segment_p95, null_tape:session_same_sign>=0.75.

| item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.523 |
| kept_n>=80 | yes | 432 |
| diff>0 | yes | 410.88 |
| diff_top1_removed>0 | yes | 487.43 |
| kept_mean_slip8>0 | no | -951.03 |
| sign_blocks>=8/12 | yes | 9 |
| control_pct>=95 | no | 61.4 |
| pbo<=0.2 | no | 0.533 |
| dsr_p<0.1 | no | 0.999 |
| spa_p<=0.10 | no | 0.7605 |
| boot_ci_excludes_0 | no | [-174.93, 1003.94] |
| null_tape:real_diff>gmm_p95 | yes | 333.44 |
| null_tape:real_diff>segment_p95 | no | 575.62 |
| null_tape:session_same_sign>=0.75 | no | 0.5 |
| no_time_proxy_columns | yes | ["alt_dir6", "alt_kind6", "atr14", "atr_bps", "bar_body_pts", "bar_range_atr", "bar_range_pts", "bars_since_bos", "bars_since_choch", "bars_since_prev_choch", " |

Bootstrap (2,000 stationary draws of sessions): diff 90% CI [-174.93, 1003.94], kept mean CI [-893.82, -198.71], P(diff <= 0) 0.1255. DSR of the per-session kept series against 468 trials: SR 0.0623, SR0 0.2517, p 0.9990.

Null-tape replay (the same cfg run on each certificate tape's own table; `tapes.null_tape_check_from_diffs`):

| generator | tapes | tape diff p50 | tape diff p95 | real diff | real pct among tapes | same sign share |
|---|---|---|---|---|---|---|
| gmm | 20 | -132.54 | 333.44 | 410.88 | 100.0 | - |
| segment | 20 | -96.03 | 575.62 | 410.88 | 90.0 | - |
| session | 20 | -1.36 | 436.57 | 410.88 | - | 0.500 |

### Determinism and truncation (`results/5minute/checks.json`)

Rows before the cut 2025-06-30 12:00:00: 712 (truncated build: 712, common SETUPs 712); L1 nets of the 712 trades closed before the cut identical in both builds: yes. Checked jobs (a fresh double run; the fit stage's stored decisions; the prefix run; the truncated-build run):

| job | head | deterministic | = stored | prefix identical | truncated build identical | SETUPs compared | decisions differing |
|---|---|---|---|---|---|---|---|
| context__lints__k1__anchored__net | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__lints__k1__anchored__net | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| context__lints__k10__300__pf | e0.0 s0 pf | yes | yes | yes | yes | 712 | 0 |
| context__lints__k10__300__pf | e0.3 s1 pf | yes | yes | yes | yes | 712 | 0 |
| context__lints__k50__1000__net | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__lints__k50__1000__net | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k1__anchored__x | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k1__anchored__x | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k10__300__x | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k10__300__x | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k50__1000__x | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__logts__k50__1000__x | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| context__hgb_reg__k50__anchored__net | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| context__hgb_cls__k50__1000__x | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| full__lints__k10__1000__net | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| full__lints__k10__1000__net | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |
| full__logts__k50__anchored__x | e0.0 s0 net | yes | yes | yes | yes | 712 | 0 |
| full__logts__k50__anchored__x | e0.3 s1 net | yes | yes | yes | yes | 712 | 0 |

All checks pass: **yes**.

### Verdict: **null result** on 5minute (no path passes the row-level go / no-go items); no candidate JSON written.

## 3. What would falsify these findings

- A walk-forward path whose kept-vs-skipped difference is positive with the top 1% winners removed, whose control percentile is >= 95 at its own per-session take count, whose sign holds in >= 8 of 12 blocks, whose real-tape difference exceeds the GMM-Markov and segment certificate p95 and whose family SPA p is <= 0.10 would be a candidate; none is reported above unless the verdict says so.
- The learners see the outcome of every SETUP (full information). A version that learns from the taken trades only would learn slower and explore more; it cannot be better informed, so it cannot rescue a null here.
- The warm-up (30 closed outcomes, take-all) and the running standardisation are the only fixed numbers besides the task's grid; the learning curves show whether anything is learned after them.
- The sized book (half Kelly on 420,000 INR of capital with the running mean loss as one lot's risk) saturates at 0 or 3 lots for almost any signed edge (one lot's risk is < 0.5% of that capital); it is reported (sized PF) and does not enter the ledger statistic.

## 4. Files

- `finalize.log`
- `finalize.py`
- `finalize_5minute.nohup`
- `online.py`
- `results` (per timeframe: spec_*.json, jobs/*.pkl, journals/*.parquet, features_full.parquet, scores.jsonl, curves.jsonl, checks.json, finalize.json)
- `run_5minute.log`
- `run_5minute_resume.log`
- `run_minute.log`
- `run_online.py`
- `smoke_timing.log`
- `smoke_timing.py`
- `write_findings.py`