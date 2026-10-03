# online_learner: the walk-forward learn-after-each-trade take / skip policy with the trade journal (IS only, 2026-09-29)

BRIEF addendum 4 (learning after each trade, the journal) composed with rl.py (addendum 6) under both judges' fixes of DESIGN_PANEL decision-making-1 (full-information rewards, the harness splitter's judgement, the kept-share / kept-n floors, the top-1%-removed value) and the program rules of 2026-09-29 12:55 UTC (null tapes, declared columns). Scripts: `online.py` (the module `oos_once.py` continues through OOS), `run_online.py` (fit / score / checks per timeframe), `finalize.py` (family statistics, selection, tapes, candidate), `write_findings.py`; logs `run_<tf>.log`, `finalize.log`, `smoke_timing.log`. Run history: the first 5minute run (`run_5minute.log`, 13:50-14:02 UTC) was cut off by the session limit after 50 of 81 fit jobs; it was resumed at 15:43 UTC (`run_5minute_resume.log`: the missing jobs, then score and checks) after the hgb_cls learner was given one nested tau per decision-side reward (its 3 finished k=1 checkpoints were deleted and re-run; before that the net / pf heads of hgb_cls were identical decisions); the minute run (`run_minute.log`, 3 workers) was helped by `run_tail.py` (`run_tail_minute.log`: the cheapest remaining jobs on the core freed when gate_family finished; same `run_online.run_job`, same outputs); `finalize_<tf>.nohup` are the finalize logs. Every kept-vs-skipped number is a `harness.score` row of family `online/<design>/<learner>/k<k>/<window>/<reward>` (the comparators: `online_comparator/*`). No OOS row was read. **The frozen feature shortlist has 0 clusters on both timeframes** (`features_shortlist/<tf>/shortlist.json`, sha 66f6e004… / 4747257f…), so the EMPTY-SHORTLIST RULE applies: the designed feature set is hour_bin one-hot + dir (`online/context/...`), and the two linear learners also run on the full as-of design as a labelled sensitivity (`online/full/...`, **outside the frozen shortlist** in every table and ledger note).

## 0. Result

**minute: null result.** 468 walk-forward paths (ledger rows; context 252, full 216 = outside the frozen shortlist), **0 pass the row-level go / no-go items**. Rows with kept share >= 20%: 180; with kept mean > 0 at 8 pts slippage: 0; with the sign in >= 8 of 12 blocks: 54; with control percentile >= 95: 1 (`53ea85eca9dfad20` full/lints/k50/300/pf e0.3 s2 (outside the frozen shortlist): kept share 0.3102, diff 153.62, top-1%-removed -6.34, sign blocks 8, kept mean at 8 pts -1,293.60). Best walk-forward kept PF: `19f7ff81224bafa0` context/lints/k1/1000/pf e0.3 s1: kept 68 of 4452 (0.0153), kept mean 112.36 vs skipped -1,027.01 (diff 1,139.37, top-1%-removed 292.69), kept PF 1.077 (take-all 0.323, frozen ST7/ST8 0.327), control percentile 0.1, perm p 0.0035, sign blocks 2/12, kept mean at 8 pts -277.61. Family: PBO (diff) 0.3065, SPA p 0.4075 (unstudentised 0.2980), effective trials 4.41 of 468. Full go / no-go of the best-by-PF row per design (null tapes included): `19f7ff81224bafa0` fails 9 items (kept_share>=20%, kept_n>=300, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:session_same_sign>=0.75); `750d04b5a33f2dd4` fails 7 items (kept_share>=20%, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10). Determinism and truncation checks: all pass (3767 SETUPs before the cut compared with the truncated build). The learning curves never reach a control percentile >= 95 that holds to the end (`first_control_ge95_to_end` is None for every finalist); 'beats take-all in cumulative net from the first checkpoint' is the cost saving of trading less (every skip saves ~1,050 INR), not selection. The half-Kelly sizing returns 0 lots on most takes (`take_and_zero_lots`: 38 of 68 on the best row): the calibrated p_win times the running W / L never clears the Kelly break-even, the honest result for a book with 15.6% / 27.7% winners. No candidate JSON written.

**5minute: null result.** 468 walk-forward paths (ledger rows; context 252, full 216 = outside the frozen shortlist), **0 pass the row-level go / no-go items**. Rows with kept share >= 20%: 275; with kept mean > 0 at 8 pts slippage: 0; with the sign in >= 8 of 12 blocks: 40; with control percentile >= 95: 1 (`8e7fe259a71bed6c` full/lints/k50/1000/pf e0.3 s2 (outside the frozen shortlist): kept share 0.3692, diff 223.97, top-1%-removed 384.01, sign blocks 6, kept mean at 8 pts -1,005.75). Best walk-forward kept PF: `e24ac736ebbfa6d5` context/logts/k10/300/net e0.0 s0: kept 140 of 826 (0.1695), kept mean -109.36 vs skipped -889.23 (diff 779.87, top-1%-removed 518.65), kept PF 0.942 (take-all 0.639, frozen ST7/ST8 0.563), control percentile 85.2, perm p 0.0665, sign blocks 4/12, kept mean at 8 pts -499.33. Family: PBO (diff) 0.5330, SPA p 0.7605 (unstudentised 0.6285), effective trials 3.58 of 468. Full go / no-go of the best-by-PF row per design (null tapes included): `e24ac736ebbfa6d5` fails 8 items (kept_share>=20%, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:session_same_sign>=0.75); `4d0b2708b7798f80` fails 8 items (kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:real_diff>segment_p95, null_tape:session_same_sign>=0.75). Determinism and truncation checks: all pass (712 SETUPs before the cut compared with the truncated build). The learning curves never reach a control percentile >= 95 that holds to the end (`first_control_ge95_to_end` is None for every finalist); 'beats take-all in cumulative net from the first checkpoint' is the cost saving of trading less (every skip saves ~1,050 INR), not selection. The half-Kelly sizing returns 0 lots on most takes (`take_and_zero_lots`: 68 of 140 on the best row): the calibrated p_win times the running W / L never clears the Kelly break-even, the honest result for a book with 15.6% / 27.7% winners. No candidate JSON written.

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

## 2. minute

Designs: context = 12 columns (11 one-hot levels of hour_bin / dir + bias); full = 305 columns (152 source columns, 62 missing indicators, bias; without `sl`, `n_events_asof`), standardised online. Paths (ledger rows): 468 (context 252, full 216).

### Comparators (family `online_comparator/*`)

| comparator | ledger id | kept n | kept share | kept mean | skipped mean | diff | kept PF | control pct | perm p | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|
| take_all | `4400f4789fdd3301` | 4452 | 1.0000 | -1,009.61 | - | - | 0.323 | - | - | - |
| frozen_st7_st8 | `85e208f5462727a6` | 745 | 0.1673 | -1,026.02 | -1,006.31 | -19.71 | 0.327 | 64.0 | 0.8681 | 6 |
| gate_family_oof/context/hgbc/finalist | `6251665baea5d9cf` | 3782 | 0.8495 | -981.74 | -1,166.91 | 185.17 | 0.350 | 11.6 | 0.0840 | 11 |
| gate_family_oof/h5_full/scorecard/finalist (outside the frozen shortlist) | `03876852c275192a` | 4261 | 0.9571 | -1,003.06 | -1,155.67 | 152.61 | 0.330 | 36.9 | 0.4378 | 4 |

### Finalists: the best path by walk-forward kept PF per (design, learner)

| ledger id | path (design/learner/k/window/reward explore seed) | kept n | kept share | kept mean | skipped mean | diff | diff top1% removed | kept PF (1 lot) | sized PF | control pct | perm p | sign blocks | kept mean slip 8 | loser recall | winner recall (net-wtd) | top-decile winners skipped | row-level pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `19f7ff81224bafa0` | context/lints/k1/1000/pf e0.3 s1 | 68 | 0.0153 | 112.36 | -1,027.01 | **1,139.37** | 292.69 | 1.077 | 0.310 | 0.1 | 0.0035 | 2 | -277.61 | 0.988 | 0.050 | 0.943 | no |
| `5c797e3cc7ae4435` | context/logts/k10/anchored/net e0.3 s4 | 103 | 0.0231 | 117.21 | -1,036.29 | **1,153.51** | 535.63 | 1.073 | 0.264 | 0.0 | 0.0005 | 4 | -272.75 | 0.982 | 0.083 | 0.886 | no |
| `750d04b5a33f2dd4` | full/lints/k50/anchored/pf e0.3 s4 (outside the frozen shortlist) | 448 | 0.1006 | -706.17 | -1,043.56 | **337.39** | 124.83 | 0.522 | 0.240 | 27.4 | 0.0095 | 6 | -1,096.13 | 0.903 | 0.162 | 0.829 | no |
| `4088c72f7461afba` | context/hgb_reg/k50/anchored/net e0.0 s0 | 119 | 0.0267 | -901.65 | -1,012.57 | **110.92** | 292.99 | 0.412 | 0.255 | 0.0 | 0.6542 | 4 | -1,291.62 | 0.975 | 0.035 | 0.971 | no |
| `f7bf12c9755185ff` | context/hgb_cls/k10/1000/net e0.0 s0 | 1681 | 0.3776 | -987.21 | -1,023.19 | **35.98** | -50.14 | 0.376 | 0.276 | 0.1 | 0.6502 | 5 | -1,377.18 | 0.628 | 0.468 | 0.557 | no |
| `ee3bb53f8c7251b8` | full/logts/k10/anchored/net e0.3 s1 (outside the frozen shortlist) | 2240 | 0.5031 | -959.28 | -1,060.57 | **101.29** | 76.45 | 0.344 | 0.310 | 81.2 | 0.2034 | 8 | -1,349.24 | 0.499 | 0.526 | 0.443 | no |

### The 25 paths with the highest walk-forward kept PF (all rows: `results/minute/scores.jsonl`, `all_rows` in `finalize.json`)

| ledger id | path (design/learner/k/window/reward explore seed) | kept n | kept share | kept mean | skipped mean | diff | diff top1% removed | kept PF (1 lot) | sized PF | control pct | perm p | sign blocks | kept mean slip 8 | loser recall | winner recall (net-wtd) | top-decile winners skipped | row-level pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `19f7ff81224bafa0` | context/lints/k1/1000/pf e0.3 s1 | 68 | 0.0153 | 112.36 | -1,027.01 | **1,139.37** | 292.69 | 1.077 | 0.310 | 0.1 | 0.0035 | 2 | -277.61 | 0.988 | 0.050 | 0.943 | no |
| `5c797e3cc7ae4435` | context/logts/k10/anchored/net e0.3 s4 | 103 | 0.0231 | 117.21 | -1,036.29 | **1,153.51** | 535.63 | 1.073 | 0.264 | 0.0 | 0.0005 | 4 | -272.75 | 0.982 | 0.083 | 0.886 | no |
| `05920e05ac605f17` | context/lints/k10/1000/pf e0.3 s1 | 69 | 0.0155 | 98.48 | -1,027.05 | **1,125.54** | 293.59 | 1.068 | 0.310 | 0.2 | 0.0020 | 2 | -291.48 | 0.988 | 0.050 | 0.943 | no |
| `137f51b05980afb1` | context/logts/k1/anchored/net e0.3 s4 | 101 | 0.0227 | 30.11 | -1,033.74 | **1,063.86** | 558.94 | 1.019 | 0.310 | 0.0 | 0.0010 | 4 | -359.85 | 0.982 | 0.077 | 0.900 | no |
| `08456c93d60e55b1` | context/lints/k10/anchored/pf e0.0 s0 | 72 | 0.0162 | 6.70 | -1,026.31 | **1,033.01** | 239.71 | 1.005 | 0.310 | 0.1 | 0.0030 | 3 | -383.27 | 0.987 | 0.050 | 0.943 | no |
| `b3d51d29532bce5d` | context/lints/k1/1000/pf e0.0 s0 | 69 | 0.0155 | 1.56 | -1,025.53 | **1,027.09** | 189.17 | 1.001 | 0.310 | 0.0 | 0.0045 | 2 | -388.40 | 0.987 | 0.049 | 0.943 | no |
| `98a8fb84a0baa0ca` | context/lints/k10/1000/pf e0.0 s0 | 69 | 0.0155 | 1.56 | -1,025.53 | **1,027.09** | 189.17 | 1.001 | 0.310 | 0.1 | 0.0030 | 2 | -388.40 | 0.987 | 0.049 | 0.943 | no |
| `dc94904c74449bd1` | context/lints/k1/anchored/pf e0.3 s5 | 74 | 0.0166 | -12.25 | -1,026.47 | **1,014.21** | 247.26 | 0.992 | 0.310 | 0.1 | 0.0015 | 3 | -402.22 | 0.986 | 0.051 | 0.943 | no |
| `96156bcff6976a70` | context/lints/k10/anchored/pf e0.3 s5 | 74 | 0.0166 | -12.25 | -1,026.47 | **1,014.21** | 247.26 | 0.992 | 0.310 | 0.0 | 0.0040 | 3 | -402.22 | 0.986 | 0.051 | 0.943 | no |
| `7cf7a826f748038c` | context/lints/k1/anchored/pf e0.0 s0 | 73 | 0.0164 | -20.83 | -1,026.09 | **1,005.26** | 224.28 | 0.986 | 0.310 | 0.1 | 0.0025 | 3 | -410.80 | 0.987 | 0.050 | 0.943 | no |
| `011146fcd5d41b33` | context/lints/k1/1000/pf e0.3 s5 | 71 | 0.0159 | -40.27 | -1,025.32 | **985.04** | 174.60 | 0.973 | 0.310 | 0.0 | 0.0080 | 2 | -430.24 | 0.987 | 0.049 | 0.943 | no |
| `eee40fee6aecd223` | context/lints/k10/1000/pf e0.3 s5 | 71 | 0.0159 | -40.27 | -1,025.32 | **985.04** | 174.60 | 0.973 | 0.310 | 0.0 | 0.0035 | 2 | -430.24 | 0.987 | 0.049 | 0.943 | no |
| `21da642db6bdf9a6` | context/lints/k1/anchored/pf e0.3 s1 | 73 | 0.0164 | -41.41 | -1,025.75 | **984.34** | 202.16 | 0.973 | 0.310 | 0.0 | 0.0040 | 2 | -431.37 | 0.987 | 0.051 | 0.943 | no |
| `0b729a6961bc6af4` | context/lints/k1/1000/pf e0.3 s3 | 71 | 0.0159 | -50.00 | -1,025.16 | **975.16** | 164.13 | 0.967 | 0.310 | 0.1 | 0.0050 | 2 | -439.97 | 0.987 | 0.049 | 0.943 | no |
| `11549de03b47cbdf` | context/lints/k10/anchored/pf e0.3 s1 | 74 | 0.0166 | -52.27 | -1,025.79 | **973.52** | 204.28 | 0.966 | 0.310 | 0.0 | 0.0050 | 2 | -442.23 | 0.986 | 0.051 | 0.943 | no |
| `4e89d3a6e7ebee50` | context/logts/k1/anchored/net e0.0 s0 | 110 | 0.0247 | -60.42 | -1,033.65 | **973.24** | 522.15 | 0.962 | 0.310 | 0.0 | 0.0020 | 5 | -450.38 | 0.980 | 0.079 | 0.900 | no |
| `010a5f0e3d465933` | context/lints/k1/1000/pf e0.3 s4 | 65 | 0.0146 | -60.19 | -1,023.67 | **963.48** | 55.64 | 0.961 | 0.310 | 0.1 | 0.0050 | 2 | -450.16 | 0.988 | 0.045 | 0.943 | no |
| `d4925a5bfd170bd2` | context/lints/k10/1000/pf e0.3 s4 | 65 | 0.0146 | -60.19 | -1,023.67 | **963.48** | 55.64 | 0.961 | 0.310 | 0.1 | 0.0105 | 2 | -450.16 | 0.988 | 0.045 | 0.943 | no |
| `5c15349e821eebde` | context/lints/k10/1000/net e0.0 s0 | 84 | 0.0189 | -61.07 | -1,027.85 | **966.78** | 314.17 | 0.959 | 0.310 | 0.0 | 0.0020 | 5 | -451.03 | 0.985 | 0.056 | 0.943 | no |
| `facaeb737d8891b7` | context/lints/k1/anchored/pf e0.3 s4 | 67 | 0.0150 | -67.43 | -1,024.00 | **956.57** | 82.37 | 0.956 | 0.310 | 0.0 | 0.0055 | 3 | -457.40 | 0.988 | 0.046 | 0.943 | no |
| `21d17821cbe96ce6` | context/lints/k10/anchored/pf e0.3 s4 | 67 | 0.0150 | -67.43 | -1,024.00 | **956.57** | 82.37 | 0.956 | 0.310 | 0.0 | 0.0060 | 3 | -457.40 | 0.988 | 0.046 | 0.943 | no |
| `3456a8ba6e6fc1af` | context/lints/k10/1000/pf e0.3 s3 | 72 | 0.0162 | -77.14 | -1,024.94 | **947.79** | 149.55 | 0.950 | 0.310 | 0.1 | 0.0050 | 2 | -467.11 | 0.986 | 0.049 | 0.943 | no |
| `bceca63d8e649841` | context/logts/k1/anchored/net e0.3 s1 | 108 | 0.0243 | -84.82 | -1,032.60 | **947.78** | 483.81 | 0.947 | 0.310 | 0.0 | 0.0005 | 5 | -474.78 | 0.980 | 0.076 | 0.900 | no |
| `a55bbebac013f9cf` | context/lints/k1/1000/net e0.0 s0 | 84 | 0.0189 | -87.45 | -1,027.34 | **939.89** | 285.97 | 0.942 | 0.310 | 0.0 | 0.0035 | 5 | -477.41 | 0.985 | 0.056 | 0.943 | no |
| `ab498763f475d08b` | context/lints/k1/anchored/pf e0.3 s3 | 74 | 0.0166 | -94.93 | -1,025.07 | **930.13** | 158.45 | 0.939 | 0.310 | 0.0 | 0.0085 | 3 | -484.90 | 0.986 | 0.050 | 0.943 | no |

### Family summary by learner and design (mean over paths; every path is a ledger row)

| design | learner | paths | kept share mean | diff mean | diff min / max | diff > 0 | kept PF mean | control pct mean | control >= 95 | row-level passes |
|---|---|---|---|---|---|---|---|---|---|---|
| context | lints | 108 | 0.0258 | 543.27 | -107.90 / 1,139.37 | 103 | 0.716 | 0.1 | 0 | 0 |
| context | logts | 108 | 0.0169 | 438.39 | -79.74 / 1,153.51 | 101 | 0.629 | 0.2 | 0 | 0 |
| context | hgb_reg | 18 | 0.0116 | 99.73 | -126.23 / 208.98 | 14 | 0.290 | 37.4 | 0 | 0 |
| context | hgb_cls | 18 | 0.6080 | 10.45 | -119.74 / 86.20 | 13 | 0.349 | 7.0 | 0 | 0 |
| full (outside the frozen shortlist) | lints | 108 | 0.2121 | 72.07 | -71.56 / 337.39 | 87 | 0.391 | 22.7 | 1 | 0 |
| full (outside the frozen shortlist) | logts | 108 | 0.5042 | 40.18 | 2.49 / 101.29 | 108 | 0.324 | 57.9 | 0 | 0 |

### Seed spread of the Thompson heads (explore 0.3, seeds 1..5; per family of 5 rows)

| family | seeds | diff mean | diff sd | diff min / max | diff > 0 | kept PF mean | kept PF sd | kept share mean |
|---|---|---|---|---|---|---|---|---|
| online/context/lints/k1/1000/net | 5 | 820.67 | 89.19 | 676.24 / 906.90 | 5 | 0.868 | 0.051 | 0.0200 |
| online/context/lints/k1/1000/pf | 5 | 986.84 | 96.62 | 871.13 / 1,139.37 | 5 | 0.976 | 0.063 | 0.0154 |
| online/context/lints/k1/300/net | 5 | 336.14 | 116.30 | 242.65 / 530.88 | 5 | 0.621 | 0.061 | 0.0431 |
| online/context/lints/k1/300/pf | 5 | 222.29 | 65.70 | 152.41 / 312.97 | 5 | 0.542 | 0.033 | 0.0227 |
| online/context/lints/k1/anchored/net | 5 | 707.77 | 75.23 | 588.99 / 785.52 | 5 | 0.809 | 0.039 | 0.0313 |
| online/context/lints/k1/anchored/pf | 5 | 933.92 | 89.29 | 784.34 / 1,014.21 | 5 | 0.942 | 0.054 | 0.0161 |
| online/context/lints/k10/1000/net | 5 | 800.93 | 105.20 | 636.61 / 928.04 | 5 | 0.856 | 0.060 | 0.0203 |
| online/context/lints/k10/1000/pf | 5 | 972.95 | 101.32 | 842.91 / 1,125.54 | 5 | 0.967 | 0.066 | 0.0156 |
| online/context/lints/k10/300/net | 5 | 265.72 | 55.57 | 202.78 / 348.40 | 5 | 0.584 | 0.031 | 0.0441 |
| online/context/lints/k10/300/pf | 5 | 196.73 | 28.27 | 169.11 / 236.51 | 5 | 0.538 | 0.013 | 0.0229 |
| online/context/lints/k10/anchored/net | 5 | 669.72 | 73.90 | 564.91 / 772.43 | 5 | 0.789 | 0.039 | 0.0319 |
| online/context/lints/k10/anchored/pf | 5 | 926.31 | 89.36 | 782.80 / 1,014.21 | 5 | 0.938 | 0.054 | 0.0162 |
| online/context/lints/k50/1000/net | 5 | 559.81 | 47.42 | 499.13 / 628.44 | 5 | 0.695 | 0.027 | 0.0235 |
| online/context/lints/k50/1000/pf | 5 | 346.11 | 109.66 | 204.47 / 482.64 | 5 | 0.557 | 0.068 | 0.0192 |
| online/context/lints/k50/300/net | 5 | 131.36 | 63.73 | 56.41 / 219.92 | 5 | 0.504 | 0.034 | 0.0447 |
| online/context/lints/k50/300/pf | 5 | -39.73 | 101.88 | -107.90 / 137.43 | 1 | 0.391 | 0.053 | 0.0262 |
| online/context/lints/k50/anchored/net | 5 | 472.93 | 70.24 | 398.19 / 582.47 | 5 | 0.671 | 0.034 | 0.0348 |
| online/context/lints/k50/anchored/pf | 5 | 305.62 | 124.17 | 185.21 / 497.18 | 5 | 0.539 | 0.075 | 0.0198 |
| online/context/logts/k1/1000/net | 5 | 764.94 | 88.41 | 686.26 / 869.00 | 5 | 0.845 | 0.049 | 0.0190 |
| online/context/logts/k1/1000/pf | 5 | 538.74 | 40.76 | 497.12 / 594.60 | 5 | 0.684 | 0.030 | 0.0110 |
| online/context/logts/k1/300/net | 5 | 262.23 | 110.23 | 110.86 / 380.93 | 5 | 0.551 | 0.050 | 0.0189 |
| online/context/logts/k1/300/pf | 5 | 407.64 | 231.10 | 41.94 / 666.78 | 5 | 0.601 | 0.132 | 0.0101 |
| online/context/logts/k1/anchored/net | 5 | 902.38 | 103.11 | 824.28 / 1,063.86 | 5 | 0.922 | 0.061 | 0.0236 |
| online/context/logts/k1/anchored/pf | 5 | 538.74 | 40.76 | 497.12 / 594.60 | 5 | 0.684 | 0.030 | 0.0110 |
| online/context/logts/k10/1000/net | 5 | 793.72 | 75.61 | 726.97 / 913.59 | 5 | 0.861 | 0.044 | 0.0188 |
| online/context/logts/k10/1000/pf | 5 | 552.82 | 136.58 | 334.01 / 710.29 | 5 | 0.691 | 0.081 | 0.0108 |
| online/context/logts/k10/300/net | 5 | 311.51 | 139.83 | 112.57 / 504.55 | 5 | 0.579 | 0.069 | 0.0187 |
| online/context/logts/k10/300/pf | 5 | 424.81 | 208.30 | 99.77 / 666.78 | 5 | 0.610 | 0.124 | 0.0100 |
| online/context/logts/k10/anchored/net | 5 | 906.90 | 145.40 | 797.69 / 1,153.51 | 5 | 0.925 | 0.087 | 0.0238 |
| online/context/logts/k10/anchored/pf | 5 | 552.82 | 136.58 | 334.01 / 710.29 | 5 | 0.691 | 0.081 | 0.0108 |
| online/context/logts/k50/1000/net | 5 | 523.69 | 109.27 | 353.05 / 645.91 | 5 | 0.683 | 0.066 | 0.0229 |
| online/context/logts/k50/1000/pf | 5 | 82.40 | 120.32 | -64.78 / 270.58 | 4 | 0.375 | 0.068 | 0.0150 |
| online/context/logts/k50/300/net | 5 | 104.33 | 169.08 | -78.32 / 273.24 | 3 | 0.451 | 0.097 | 0.0221 |
| online/context/logts/k50/300/pf | 5 | 54.22 | 127.58 | -79.74 / 250.27 | 3 | 0.359 | 0.061 | 0.0141 |
| online/context/logts/k50/anchored/net | 5 | 637.05 | 67.93 | 554.26 / 698.48 | 5 | 0.757 | 0.044 | 0.0279 |
| online/context/logts/k50/anchored/pf | 5 | 91.76 | 119.82 | -64.78 / 270.58 | 4 | 0.379 | 0.069 | 0.0151 |
| online/full/lints/k1/1000/net (outside the frozen shortlist) | 5 | 65.37 | 47.69 | 15.80 / 143.47 | 5 | 0.393 | 0.024 | 0.2276 |
| online/full/lints/k1/1000/pf (outside the frozen shortlist) | 5 | -5.75 | 43.71 | -35.80 / 69.14 | 1 | 0.379 | 0.016 | 0.1398 |
| online/full/lints/k1/300/net (outside the frozen shortlist) | 5 | 32.67 | 48.65 | -45.06 / 86.00 | 4 | 0.361 | 0.017 | 0.3361 |
| online/full/lints/k1/300/pf (outside the frozen shortlist) | 5 | 11.52 | 58.06 | -71.56 / 54.27 | 3 | 0.365 | 0.021 | 0.2668 |
| online/full/lints/k1/anchored/net (outside the frozen shortlist) | 5 | -24.62 | 32.91 | -49.87 / 32.71 | 1 | 0.367 | 0.016 | 0.1463 |
| online/full/lints/k1/anchored/pf (outside the frozen shortlist) | 5 | 146.61 | 78.10 | 60.11 / 256.95 | 5 | 0.441 | 0.038 | 0.0861 |
| online/full/lints/k10/1000/net (outside the frozen shortlist) | 5 | 114.37 | 65.42 | 38.40 / 194.07 | 5 | 0.403 | 0.028 | 0.2400 |
| online/full/lints/k10/1000/pf (outside the frozen shortlist) | 5 | 60.81 | 64.18 | 8.73 / 167.27 | 5 | 0.397 | 0.032 | 0.1486 |
| online/full/lints/k10/300/net (outside the frozen shortlist) | 5 | 53.31 | 63.35 | -50.35 / 120.65 | 4 | 0.359 | 0.020 | 0.3656 |
| online/full/lints/k10/300/pf (outside the frozen shortlist) | 5 | 22.91 | 48.35 | -30.96 / 79.54 | 3 | 0.354 | 0.018 | 0.2976 |
| online/full/lints/k10/anchored/net (outside the frozen shortlist) | 5 | 36.59 | 40.45 | -11.24 / 94.62 | 4 | 0.385 | 0.021 | 0.1523 |
| online/full/lints/k10/anchored/pf (outside the frozen shortlist) | 5 | 158.09 | 90.76 | 36.96 / 251.48 | 5 | 0.444 | 0.041 | 0.0920 |
| online/full/lints/k50/1000/net (outside the frozen shortlist) | 5 | 86.12 | 84.42 | 5.64 / 178.20 | 5 | 0.383 | 0.037 | 0.2495 |
| online/full/lints/k50/1000/pf (outside the frozen shortlist) | 5 | 119.40 | 74.80 | -1.51 / 193.94 | 4 | 0.417 | 0.037 | 0.1595 |
| online/full/lints/k50/300/net (outside the frozen shortlist) | 5 | 62.22 | 58.32 | -15.94 / 130.11 | 4 | 0.355 | 0.019 | 0.3755 |
| online/full/lints/k50/300/pf (outside the frozen shortlist) | 5 | 61.64 | 59.75 | 3.34 / 153.62 | 5 | 0.362 | 0.018 | 0.3132 |
| online/full/lints/k50/anchored/net (outside the frozen shortlist) | 5 | 71.93 | 44.53 | 23.58 / 113.70 | 5 | 0.393 | 0.021 | 0.1601 |
| online/full/lints/k50/anchored/pf (outside the frozen shortlist) | 5 | 237.00 | 102.79 | 80.80 / 337.39 | 5 | 0.472 | 0.055 | 0.0992 |
| online/full/logts/k1/1000/net (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k1/1000/pf (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k1/300/net (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k1/300/pf (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k1/anchored/net (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k1/anchored/pf (outside the frozen shortlist) | 5 | 11.08 | 0.00 | 11.08 / 11.08 | 5 | 0.315 | 0.000 | 0.5034 |
| online/full/logts/k10/1000/net (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k10/1000/pf (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k10/300/net (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k10/300/pf (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k10/anchored/net (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k10/anchored/pf (outside the frozen shortlist) | 5 | 101.01 | 0.26 | 100.82 / 101.29 | 5 | 0.344 | 0.000 | 0.5030 |
| online/full/logts/k50/1000/net (outside the frozen shortlist) | 5 | 9.24 | 3.57 | 5.43 / 14.95 | 5 | 0.313 | 0.001 | 0.5066 |
| online/full/logts/k50/1000/pf (outside the frozen shortlist) | 5 | 7.67 | 3.20 | 2.49 / 10.16 | 5 | 0.312 | 0.001 | 0.5064 |
| online/full/logts/k50/300/net (outside the frozen shortlist) | 5 | 9.24 | 3.57 | 5.43 / 14.95 | 5 | 0.313 | 0.001 | 0.5066 |
| online/full/logts/k50/300/pf (outside the frozen shortlist) | 5 | 7.67 | 3.20 | 2.49 / 10.16 | 5 | 0.312 | 0.001 | 0.5064 |
| online/full/logts/k50/anchored/net (outside the frozen shortlist) | 5 | 9.24 | 3.57 | 5.43 / 14.95 | 5 | 0.313 | 0.001 | 0.5066 |
| online/full/logts/k50/anchored/pf (outside the frozen shortlist) | 5 | 7.67 | 3.20 | 2.49 / 10.16 | 5 | 0.312 | 0.001 | 0.5064 |

### Learning curves of the finalists (every 250 SETUPs; `curve_summary` in `finalize.json`; the control percentile = `fz_report.random_control`, 2,000 draws, at the path's own per-session take count on the prefix)

**context/lints** `19f7ff81224bafa0` (context/lints/k1/1000/pf e0.3 s1): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 34 | 0.1360 | 782.20 | -240.48 | 0.803 | 44.4 | 0.1354 | -8,176.23 | -229,074.80 |
| 500 | 48 | 0.0960 | 1,004.81 | 2.12 | 1.001 | 2.0 | 0.0255 | 101.59 | -453,116.63 |
| 750 | 55 | 0.0733 | 1,435.72 | 403.09 | 1.274 | 0.1 | 0.0015 | 22,170.11 | -695,502.33 |
| 1000 | 63 | 0.0630 | 1,159.71 | 138.40 | 1.092 | 0.2 | 0.0035 | 8,719.23 | -948,250.15 |
| 1250 | 68 | 0.0544 | 1,115.51 | 112.36 | 1.077 | 0.1 | 0.0020 | 7,640.45 | -1,178,082.77 |
| 1500 | 68 | 0.0453 | 1,100.03 | 112.36 | 1.077 | 0.1 | 0.0030 | 7,640.45 | -1,406,705.81 |
| 1750 | 68 | 0.0389 | 1,074.08 | 112.36 | 1.077 | 0.2 | 0.0020 | 7,640.45 | -1,609,970.37 |
| 2000 | 68 | 0.0340 | 1,082.40 | 112.36 | 1.077 | 0.1 | 0.0035 | 7,640.45 | -1,866,469.08 |
| 2250 | 68 | 0.0302 | 1,087.95 | 112.36 | 1.077 | 0.2 | 0.0010 | 7,640.45 | -2,121,098.24 |
| 2500 | 68 | 0.0272 | 1,106.70 | 112.36 | 1.077 | 0.2 | 0.0015 | 7,640.45 | -2,410,602.99 |
| 2750 | 68 | 0.0247 | 1,098.73 | 112.36 | 1.077 | 0.1 | 0.0005 | 7,640.45 | -2,637,791.68 |
| 3000 | 68 | 0.0227 | 1,101.60 | 112.36 | 1.077 | 0.2 | 0.0025 | 7,640.45 | -2,892,808.15 |
| 3250 | 68 | 0.0209 | 1,110.92 | 112.36 | 1.077 | 0.1 | 0.0035 | 7,640.45 | -3,169,770.01 |
| 3500 | 68 | 0.0194 | 1,109.66 | 112.36 | 1.077 | 0.1 | 0.0040 | 7,640.45 | -3,415,090.88 |
| 3750 | 68 | 0.0181 | 1,120.98 | 112.36 | 1.077 | 0.1 | 0.0035 | 7,640.45 | -3,706,113.37 |
| 4000 | 68 | 0.0170 | 1,132.91 | 112.36 | 1.077 | 0.1 | 0.0020 | 7,640.45 | -4,005,151.74 |
| 4250 | 68 | 0.0160 | 1,145.81 | 112.36 | 1.077 | 0.1 | 0.0025 | 7,640.45 | -4,314,243.40 |
| 4452 | 68 | 0.0153 | 1,139.37 | 112.36 | 1.077 | 0.1 | 0.0035 | 7,640.45 | -4,494,772.79 |

**context/logts** `5c797e3cc7ae4435` (context/logts/k10/anchored/net e0.3 s4): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 36 | 0.1440 | 1,143.38 | 62.44 | 1.052 | 44.1 | 0.0285 | 2,247.77 | -229,074.80 |
| 500 | 52 | 0.1040 | 1,213.29 | 180.87 | 1.130 | 2.2 | 0.0065 | 9,405.46 | -453,116.63 |
| 750 | 60 | 0.0800 | 1,540.03 | 489.49 | 1.336 | 0.0 | 0.0025 | 29,369.37 | -695,502.33 |
| 1000 | 69 | 0.0690 | 1,180.96 | 151.22 | 1.098 | 0.0 | 0.0025 | 10,434.44 | -948,250.15 |
| 1250 | 76 | 0.0608 | 1,216.20 | 199.79 | 1.135 | 0.0 | 0.0015 | 15,184.26 | -1,178,082.77 |
| 1500 | 84 | 0.0560 | 1,110.47 | 110.48 | 1.071 | 0.0 | 0.0020 | 9,280.07 | -1,406,705.81 |
| 1750 | 92 | 0.0526 | 1,274.29 | 287.32 | 1.187 | 0.0 | 0.0005 | 26,433.01 | -1,609,970.37 |
| 2000 | 101 | 0.0505 | 1,123.15 | 133.19 | 1.083 | 0.0 | 0.0005 | 13,452.59 | -1,866,469.08 |
| 2250 | 103 | 0.0458 | 1,110.77 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -2,121,098.24 |
| 2500 | 103 | 0.0412 | 1,127.92 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -2,410,602.99 |
| 2750 | 103 | 0.0375 | 1,118.30 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -2,637,791.68 |
| 3000 | 103 | 0.0343 | 1,119.93 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -2,892,808.15 |
| 3250 | 103 | 0.0317 | 1,128.28 | 117.21 | 1.073 | 0.0 | 0.0010 | 12,072.94 | -3,169,770.01 |
| 3500 | 103 | 0.0294 | 1,126.09 | 117.21 | 1.073 | 0.0 | 0.0010 | 12,072.94 | -3,415,090.88 |
| 3750 | 103 | 0.0275 | 1,136.73 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -3,706,113.37 |
| 4000 | 103 | 0.0257 | 1,148.06 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -4,005,151.74 |
| 4250 | 103 | 0.0242 | 1,160.45 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -4,314,243.40 |
| 4452 | 103 | 0.0231 | 1,153.51 | 117.21 | 1.073 | 0.0 | 0.0005 | 12,072.94 | -4,494,772.79 |

**full/lints (outside the frozen shortlist)** `750d04b5a33f2dd4` (full/lints/k50/anchored/pf e0.3 s4): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 135 | 0.5400 | 397.84 | -733.29 | 0.484 | 59.4 | 0.2939 | -98,994.73 | -229,074.80 |
| 500 | 199 | 0.3980 | 491.40 | -610.41 | 0.571 | 53.5 | 0.0735 | -121,472.23 | -453,116.63 |
| 750 | 239 | 0.3187 | 495.44 | -589.78 | 0.605 | 49.8 | 0.0430 | -140,957.24 | -695,502.33 |
| 1000 | 278 | 0.2780 | 549.54 | -551.48 | 0.618 | 75.5 | 0.0065 | -153,311.12 | -948,250.15 |
| 1250 | 314 | 0.2512 | 526.63 | -548.13 | 0.611 | 80.2 | 0.0035 | -172,111.31 | -1,178,082.77 |
| 1500 | 346 | 0.2307 | 523.74 | -534.87 | 0.621 | 84.3 | 0.0025 | -185,065.86 | -1,406,705.81 |
| 1750 | 364 | 0.2080 | 508.55 | -517.21 | 0.631 | 83.2 | 0.0010 | -188,264.84 | -1,609,970.37 |
| 2000 | 384 | 0.1920 | 422.56 | -591.81 | 0.586 | 64.2 | 0.0025 | -227,253.21 | -1,866,469.08 |
| 2250 | 413 | 0.1836 | 378.79 | -633.45 | 0.558 | 53.9 | 0.0020 | -261,613.88 | -2,121,098.24 |
| 2500 | 428 | 0.1712 | 376.08 | -652.55 | 0.543 | 47.4 | 0.0020 | -279,290.09 | -2,410,602.99 |
| 2750 | 429 | 0.1560 | 360.83 | -654.65 | 0.542 | 43.7 | 0.0035 | -280,846.15 | -2,637,791.68 |
| 3000 | 437 | 0.1457 | 385.13 | -635.24 | 0.555 | 57.2 | 0.0030 | -277,600.16 | -2,892,808.15 |
| 3250 | 441 | 0.1357 | 322.18 | -696.85 | 0.529 | 28.1 | 0.0195 | -307,311.29 | -3,169,770.01 |
| 3500 | 442 | 0.1263 | 320.36 | -695.83 | 0.529 | 31.3 | 0.0175 | -307,558.23 | -3,415,090.88 |
| 3750 | 444 | 0.1184 | 323.79 | -702.84 | 0.526 | 27.9 | 0.0160 | -312,061.05 | -3,706,113.37 |
| 4000 | 447 | 0.1118 | 334.21 | -704.43 | 0.523 | 28.5 | 0.0155 | -314,879.81 | -4,005,151.74 |
| 4250 | 448 | 0.1054 | 345.36 | -706.17 | 0.522 | 28.9 | 0.0095 | -316,361.96 | -4,314,243.40 |
| 4452 | 448 | 0.1006 | 337.39 | -706.17 | 0.522 | 29.2 | 0.0125 | -316,361.96 | -4,494,772.79 |

**context/hgb_reg** `4088c72f7461afba` (context/hgb_reg/k50/anchored/net e0.0 s0): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 1250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 50 | 0.2000 | -8.43 | -923.05 | 0.255 | 50.0 | 0.9815 | -46,152.34 | -229,074.80 |
| 500 | 50 | 0.1000 | -18.68 | -923.05 | 0.255 | 50.0 | 0.9685 | -46,152.34 | -453,116.63 |
| 750 | 50 | 0.0667 | 4.60 | -923.05 | 0.255 | 50.0 | 0.9945 | -46,152.34 | -695,502.33 |
| 1000 | 62 | 0.0620 | -117.89 | -1,058.83 | 0.206 | 13.4 | 0.7531 | -65,647.24 | -948,250.15 |
| 1250 | 75 | 0.0600 | 101.68 | -846.89 | 0.319 | 42.9 | 0.7526 | -63,516.75 | -1,178,082.77 |
| 1500 | 86 | 0.0573 | 87.46 | -855.36 | 0.366 | 6.3 | 0.7576 | -73,560.85 | -1,406,705.81 |
| 1750 | 93 | 0.0531 | 166.30 | -762.52 | 0.439 | 3.9 | 0.5527 | -70,914.10 | -1,609,970.37 |
| 2000 | 102 | 0.0510 | 116.69 | -822.50 | 0.430 | 0.1 | 0.6512 | -83,894.52 | -1,866,469.08 |
| 2250 | 113 | 0.0502 | 55.61 | -889.89 | 0.408 | 0.0 | 0.8201 | -100,557.65 | -2,121,098.24 |
| 2500 | 119 | 0.0476 | 65.72 | -901.65 | 0.412 | 0.0 | 0.7656 | -107,296.40 | -2,410,602.99 |
| 2750 | 119 | 0.0433 | 60.15 | -901.65 | 0.412 | 0.0 | 0.7981 | -107,296.40 | -2,637,791.68 |
| 3000 | 119 | 0.0397 | 65.21 | -901.65 | 0.412 | 0.0 | 0.8036 | -107,296.40 | -2,892,808.15 |
| 3250 | 119 | 0.0366 | 76.46 | -901.65 | 0.412 | 0.0 | 0.7681 | -107,296.40 | -3,169,770.01 |
| 3500 | 119 | 0.0340 | 76.70 | -901.65 | 0.412 | 0.0 | 0.7641 | -107,296.40 | -3,415,090.88 |
| 3750 | 119 | 0.0317 | 89.49 | -901.65 | 0.412 | 0.0 | 0.7456 | -107,296.40 | -3,706,113.37 |
| 4000 | 119 | 0.0297 | 102.69 | -901.65 | 0.412 | 0.0 | 0.6762 | -107,296.40 | -4,005,151.74 |
| 4250 | 119 | 0.0280 | 116.73 | -901.65 | 0.412 | 0.0 | 0.6307 | -107,296.40 | -4,314,243.40 |
| 4452 | 119 | 0.0267 | 110.92 | -901.65 | 0.412 | 0.0 | 0.6757 | -107,296.40 | -4,494,772.79 |

**context/hgb_cls** `f7bf12c9755185ff` (context/hgb_cls/k10/1000/net e0.0 s0): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 750; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 215 | 0.8600 | -121.63 | -933.33 | 0.398 | 43.9 | 0.8161 | -200,665.41 | -229,074.80 |
| 500 | 440 | 0.8800 | -71.50 | -914.81 | 0.412 | 31.6 | 0.8641 | -402,517.77 | -453,116.63 |
| 750 | 628 | 0.8373 | 229.55 | -890.00 | 0.441 | 52.5 | 0.4608 | -558,917.84 | -695,502.33 |
| 1000 | 780 | 0.7800 | 225.21 | -898.70 | 0.420 | 49.0 | 0.3093 | -700,989.54 | -948,250.15 |
| 1250 | 878 | 0.7024 | 230.12 | -873.98 | 0.422 | 64.6 | 0.1754 | -767,356.82 | -1,178,082.77 |
| 1500 | 959 | 0.6393 | 140.34 | -887.19 | 0.416 | 39.0 | 0.3138 | -850,811.71 | -1,406,705.81 |
| 1750 | 1011 | 0.5777 | 119.03 | -869.72 | 0.425 | 30.8 | 0.3248 | -879,286.64 | -1,609,970.37 |
| 2000 | 1099 | 0.5495 | 80.93 | -896.78 | 0.405 | 14.8 | 0.4703 | -985,557.68 | -1,866,469.08 |
| 2250 | 1138 | 0.5058 | 76.48 | -904.91 | 0.400 | 4.8 | 0.4493 | -1,029,788.78 | -2,121,098.24 |
| 2500 | 1160 | 0.4640 | 92.94 | -914.42 | 0.396 | 1.8 | 0.3088 | -1,060,730.55 | -2,410,602.99 |
| 2750 | 1174 | 0.4269 | 130.30 | -884.52 | 0.416 | 1.8 | 0.1589 | -1,038,431.89 | -2,637,791.68 |
| 3000 | 1196 | 0.3987 | 136.70 | -882.07 | 0.420 | 0.3 | 0.1344 | -1,054,949.87 | -2,892,808.15 |
| 3250 | 1263 | 0.3886 | 109.50 | -908.37 | 0.419 | 0.2 | 0.2574 | -1,147,265.25 | -3,169,770.01 |
| 3500 | 1359 | 0.3883 | 90.91 | -920.13 | 0.414 | 0.3 | 0.3408 | -1,250,454.02 | -3,415,090.88 |
| 3750 | 1483 | 0.3955 | 86.71 | -935.88 | 0.403 | 0.3 | 0.3213 | -1,387,904.66 | -3,706,113.37 |
| 4000 | 1580 | 0.3950 | 58.24 | -966.06 | 0.386 | 0.4 | 0.5017 | -1,526,367.22 | -4,005,151.74 |
| 4250 | 1670 | 0.3929 | 41.62 | -989.85 | 0.374 | 0.2 | 0.6022 | -1,653,050.54 | -4,314,243.40 |
| 4452 | 1681 | 0.3776 | 35.98 | -987.21 | 0.376 | 0.1 | 0.6507 | -1,659,501.02 | -4,494,772.79 |

**full/logts (outside the frozen shortlist)** `ee3bb53f8c7251b8` (full/logts/k10/anchored/net e0.3 s1): first checkpoint from which the cumulative kept net exceeds take-all's to the end: 250; from which diff > 0 to the end: 250; from which control pct >= 95 to the end: -.

| SETUPs | kept n | kept share | diff | kept mean | kept PF | control pct | perm p | kept sum | take-all sum |
|---|---|---|---|---|---|---|---|---|---|
| 250 | 140 | 0.5600 | 1,164.79 | -403.79 | 0.707 | 97.3 | 0.0005 | -56,530.62 | -229,074.80 |
| 500 | 260 | 0.5200 | 398.12 | -715.14 | 0.520 | 54.6 | 0.1364 | -185,935.42 | -453,116.63 |
| 750 | 390 | 0.5200 | 420.90 | -725.30 | 0.517 | 88.8 | 0.0660 | -282,868.49 | -695,502.33 |
| 1000 | 510 | 0.5100 | 243.90 | -828.74 | 0.446 | 68.7 | 0.1754 | -422,657.96 | -948,250.15 |
| 1250 | 640 | 0.5120 | 174.42 | -857.35 | 0.413 | 57.4 | 0.2454 | -548,703.35 | -1,178,082.77 |
| 1500 | 760 | 0.5067 | 174.05 | -851.94 | 0.414 | 38.1 | 0.2064 | -647,474.89 | -1,406,705.81 |
| 1750 | 890 | 0.5086 | 193.09 | -825.09 | 0.425 | 55.0 | 0.1284 | -734,330.78 | -1,609,970.37 |
| 2000 | 1010 | 0.5050 | 172.10 | -848.04 | 0.403 | 68.3 | 0.1259 | -856,523.17 | -1,866,469.08 |
| 2250 | 1140 | 0.5067 | 157.65 | -864.94 | 0.381 | 79.0 | 0.1269 | -986,029.38 | -2,121,098.24 |
| 2500 | 1260 | 0.5040 | 117.57 | -905.93 | 0.352 | 79.5 | 0.2134 | -1,141,469.97 | -2,410,602.99 |
| 2750 | 1390 | 0.5055 | 169.13 | -875.55 | 0.378 | 88.9 | 0.0690 | -1,217,017.54 | -2,637,791.68 |
| 3000 | 1510 | 0.5033 | 186.61 | -871.59 | 0.388 | 94.5 | 0.0415 | -1,316,098.03 | -2,892,808.15 |
| 3250 | 1640 | 0.5046 | 104.66 | -923.47 | 0.364 | 76.2 | 0.2564 | -1,514,486.40 | -3,169,770.01 |
| 3500 | 1760 | 0.5029 | 109.54 | -921.28 | 0.370 | 75.8 | 0.2434 | -1,621,454.58 | -3,415,090.88 |
| 3750 | 1890 | 0.5040 | 112.12 | -932.68 | 0.362 | 86.3 | 0.2214 | -1,762,772.12 | -3,706,113.37 |
| 4000 | 2010 | 0.5025 | 96.27 | -953.39 | 0.349 | 81.2 | 0.2549 | -1,916,323.62 | -4,005,151.74 |
| 4250 | 2140 | 0.5035 | 84.78 | -973.02 | 0.337 | 78.1 | 0.2819 | -2,082,272.42 | -4,314,243.40 |
| 4452 | 2240 | 0.5031 | 101.29 | -959.28 | 0.344 | 83.2 | 0.1984 | -2,148,784.90 | -4,494,772.79 |

### Multiplicity over the online family (every `online/*` row of the timeframe, both designs)

| candidates | PBO (diff) | IS-best below 0 OOS | degradation slope | PBO (kept mean) | SPA p (studentised) | RC p | SPA p (unstudentised) | SPA best mean gain / session | excluded from studentised | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|
| 468 | **0.3065** | 0.2113 | -0.0240 | 0.2775 | **0.4075** | 0.6520 | 0.2980 | 149.62 | 78 | 4.41 |

| design | candidates | PBO (diff) | SPA p (studentised) | SPA p (unstudentised) | effective trials |
|---|---|---|---|---|---|
| context | 252 | 0.4705 | 0.8650 | 0.8860 | 2.59 |
| full (outside the frozen shortlist) | 216 | 0.4110 | 0.3215 | 0.2890 | 2.96 |

### Selection and go / no-go

Rows passing the row-level items (kept share, kept n, diff > 0, diff top-1%-removed > 0, kept mean at 8 pts > 0, sign blocks >= 8, control >= 95): **0** of 468. Selected (highest kept PF among them): none.

**`19f7ff81224bafa0`** (context/lints/k1/1000/pf e0.3 s1; the best-by-PF row of its design, for the record): full go / no-go **FAILED**; failing items: kept_share>=20%, kept_n>=300, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:session_same_sign>=0.75.

| item | ok | value |
|---|---|---|
| kept_share>=20% | no | 0.0153 |
| kept_n>=300 | no | 68 |
| diff>0 | yes | 1139.37 |
| diff_top1_removed>0 | yes | 292.69 |
| kept_mean_slip8>0 | no | -277.61 |
| sign_blocks>=8/12 | no | 2 |
| control_pct>=95 | no | 0.1 |
| pbo<=0.2 | no | 0.3065 |
| dsr_p<0.1 | no | 0.9955 |
| spa_p<=0.10 | no | 0.4075 |
| boot_ci_excludes_0 | yes | [21.09, 3064.45] |
| null_tape:real_diff>gmm_p95 | yes | 216.6 |
| null_tape:real_diff>segment_p95 | yes | 701.34 |
| null_tape:session_same_sign>=0.75 | no | 0.25 |
| no_time_proxy_columns | yes | ["dir", "hour_bin"] |

Bootstrap (2,000 stationary draws of sessions): diff 90% CI [21.09, 3064.45], kept mean CI [-997.77, 2034.0], P(diff <= 0) 0.0465. DSR of the per-session kept series against 468 trials: SR 0.1184, SR0 0.4868, p 0.9955.

Null-tape replay (the same cfg run on each certificate tape's own table; `tapes.null_tape_check_from_diffs`):

| generator | tapes | tape diff p50 | tape diff p95 | real diff | real pct among tapes | same sign share |
|---|---|---|---|---|---|---|
| gmm | 8 | -112.31 | 216.60 | 1,139.37 | 100.0 | - |
| segment | 8 | -64.09 | 701.34 | 1,139.37 | 100.0 | - |
| session | 8 | -161.73 | 231.68 | 1,139.37 | - | 0.250 |

**`750d04b5a33f2dd4`** (full/lints/k50/anchored/pf e0.3 s4 (outside the frozen shortlist); the best-by-PF row of its design, for the record): full go / no-go **FAILED**; failing items: kept_share>=20%, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10.

| item | ok | value |
|---|---|---|
| kept_share>=20% | no | 0.1006 |
| kept_n>=300 | yes | 448 |
| diff>0 | yes | 337.39 |
| diff_top1_removed>0 | yes | 124.83 |
| kept_mean_slip8>0 | no | -1096.13 |
| sign_blocks>=8/12 | no | 6 |
| control_pct>=95 | no | 27.4 |
| pbo<=0.2 | no | 0.3065 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | no | 0.4075 |
| boot_ci_excludes_0 | yes | [73.25, 591.36] |
| null_tape:real_diff>gmm_p95 | yes | 76.3 |
| null_tape:real_diff>segment_p95 | yes | 328.17 |
| null_tape:session_same_sign>=0.75 | yes | 0.75 |
| no_time_proxy_columns | yes | ["alt_dir6", "alt_kind6", "atr14", "atr_bps", "bar_body_pts", "bar_range_atr", "bar_range_pts", "bars_since_bos", "bars_since_choch", "bars_since_prev_choch", " |

Bootstrap (2,000 stationary draws of sessions): diff 90% CI [73.25, 591.36], kept mean CI [-952.3, -465.06], P(diff <= 0) 0.018. DSR of the per-session kept series against 468 trials: SR -0.0556, SR0 0.4868, p 1.0000.

Null-tape replay (the same cfg run on each certificate tape's own table; `tapes.null_tape_check_from_diffs`):

| generator | tapes | tape diff p50 | tape diff p95 | real diff | real pct among tapes | same sign share |
|---|---|---|---|---|---|---|
| gmm | 8 | -37.96 | 76.30 | 337.39 | 100.0 | - |
| segment | 8 | -39.32 | 328.17 | 337.39 | 87.5 | - |
| session | 8 | 116.19 | 288.51 | 337.39 | - | 0.750 |

### Determinism and truncation (`results/minute/checks.json`)

Rows before the cut 2025-06-30 12:00:00: 3767 (truncated build: 3767, common SETUPs 3767); L1 nets of the 3767 trades closed before the cut identical in both builds: yes. Checked jobs (a fresh double run; the fit stage's stored decisions; the prefix run; the truncated-build run):

| job | head | deterministic | = stored | prefix identical | truncated build identical | SETUPs compared | decisions differing |
|---|---|---|---|---|---|---|---|
| context__lints__k1__anchored__net | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__lints__k1__anchored__net | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| context__lints__k10__300__pf | e0.0 s0 pf | yes | yes | yes | yes | 3767 | 0 |
| context__lints__k10__300__pf | e0.3 s1 pf | yes | yes | yes | yes | 3767 | 0 |
| context__lints__k50__1000__net | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__lints__k50__1000__net | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k1__anchored__x | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k1__anchored__x | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k10__300__x | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k10__300__x | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k50__1000__x | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__logts__k50__1000__x | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| context__hgb_reg__k50__anchored__net | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| context__hgb_cls__k50__1000__x | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| full__lints__k10__1000__net | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| full__lints__k10__1000__net | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |
| full__logts__k50__anchored__x | e0.0 s0 net | yes | yes | yes | yes | 3767 | 0 |
| full__logts__k50__anchored__x | e0.3 s1 net | yes | yes | yes | yes | 3767 | 0 |

All checks pass: **yes**.

### Verdict: **null result** on minute (no path passes the row-level go / no-go items); no candidate JSON written.

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
| gate_family_oof/h5_full/dt3 (outside the frozen shortlist) | `09864e169a147a5b` | 793 | 0.9600 | -754.51 | -818.14 | 63.63 | 0.637 | 95.8 | 0.9415 | 4 |
| gate_family_oof/h5_full/h5rules (outside the frozen shortlist) | `1b17e868368d3f90` | 183 | 0.2215 | -595.02 | -803.17 | 208.14 | 0.742 | 47.1 | 0.5717 | 8 |
| gate_family_oof/h5_full/hgbc (outside the frozen shortlist) | `85609292abd34abb` | 790 | 0.9564 | -740.20 | -1,126.95 | 386.75 | 0.650 | 45.2 | 0.6197 | 7 |
| gate_family_oof/h5_full/scorecard (outside the frozen shortlist) | `a95e69eb73313fdf` | 824 | 0.9976 | -752.40 | -2,675.05 | 1,922.65 | 0.641 | 62.8 | 0.5082 | 1 |

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

- `FINDINGS.md`
- `finalize.log`
- `finalize.py`
- `finalize_5minute.nohup`
- `finalize_minute.nohup`
- `findings.json`
- `online.py`
- `results` (per timeframe: spec_*.json, jobs/*.pkl, journals/*.parquet, features_full.parquet, scores.jsonl, curves.jsonl, checks.json, finalize.json)
- `run_5minute.log`
- `run_5minute_resume.log`
- `run_minute.log`
- `run_online.py`
- `run_tail.py`
- `run_tail_minute.log`
- `smoke_timing.log`
- `smoke_timing.py`
- `write_findings.py`