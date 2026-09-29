# exit_policy — FINDINGS (IS only, 2026-09-29)

Study `decision-making-2-exit-policy-fqi-exomdp` (DESIGN_PANEL, both judges' fixes) with BRIEF addendum 6: the managed replay is `lab.manage` / `lab.price_trade`, never a second implementation. Entries are frozen (every IS unit of `harness.load(tf)`, label L1, both timeframes); only the exit changes. No OOS row was read.

## 1. Definitions (fixed before the numbers)

- **Entries**: the L1 units, entry at the SETUP bar's close in the SETUP's direction; 1 min = Strategy 1 rules (prev_swing stop), 5 min = Strategy 2 rules (choch_candle stop).
- **Square-off bar**: the last bar of the entry session opening at or before 15:25 (`lab.eod_cut`); **cap** = min(square-off bar, the contract's last candle) — every comparator is cut there.
- **Foundation stop**: `features.sl`, engine touch convention (open beyond the stop -> fill at the open; wick touch -> fill at the stop; a session's first bar -> the close). Identical to `lab.manage`'s stop (proved on every IS trade, section 2).
- **Extended trajectory** (learners A / B, the floor oracle): bars entry+1 .. J_end, J_end = the Foundation stop bar when it fires before the cap, else the cap. Exits before J_end are at the bar's close; at J_end the exit is the stop fill or the cap close. The engine's next-CHoCH exit is not applied (Exo-MDP: the tape does not react, so every exit policy is replayable).
- **Value**: net INR per trade per lot = `lab.price_trade` arithmetic (lot 65, 5 pts slippage per side, `lab.trade_charges(ZERODHA_NFO_FUT)` on the slipped prices); a 3-lot ladder is reported per position and per lot (position net / 3); selection and every comparison use per lot.
- **Oracle (free)**: the best close exit over entry+1 .. cap with no stop (an upper bound for any close-exit policy; a target filled intrabar can exceed it by at most that bar's range). **Oracle (floor)**: the best exit on the extended trajectory, ties -> earliest (learner B's target). **Exit regret** = oracle - policy.
- **Random-exit control**: exit at a uniformly drawn bar of entry+1 .. cap at its close, 2,000 seeded draws (`fz|exit`); a policy's percentile = share of draws whose mean net per lot is below the policy's (+ half the ties).
- **CHoCH against**: an `events.parquet` CHoCH with i > entry, i <= t, direction opposite to the position (known at its own bar under touch rules). **Time stop N**: exit at the close of bar entry+N if still open.
- **Cut convention (learner C)**: the time stop and the CHoCH-against exit are a post-processing cut of `lab.manage`'s tranches: every tranche whose lab exit bar is later than the cut bar exits at the cut bar's close instead; a tranche the lab closed at or before the cut bar keeps its exit (the stop / target on the cut bar is assumed first, as `lab.manage` assumes the stop first on a candle); with both cuts on, the earlier bar wins.
- **Learner C grid** (never shrunk): stop {35, 50, 75 pts, Foundation stop via `exact_R`} x scale_out {none, 1R, 2R, 3R, 4R with 1 lot (the target is the exit), ladder 1R/2R, ladder 2R/4R with 3 lots} x trail {none, (2,1), (2,2), (3,1), (3,2), (4,1), (4,2)} x time stop {none, 30, 60, 120 bars} x CHoCH-against {off, on}; square_off 15:25 always: 196 `lab.manage` positions x 8 cuts = **1,568 variants per timeframe**, each a strategy-row dict as `rl.py` builds it (lot 65, slippage 5, `position_json`, cap = the contract's last candle as `rl.contract_end`).
- **Selection (C)**: nested in `harness.purged_splits` (argmax of the training fold's mean net per lot, applied to the test fold) and in the 66 CPCV splits -> 11 paths (`harness.cpcv_paths`). **Learners A / B**: 3 contiguous session-block folds (harness blocks 0-3 / 4-7 / 8-11), purge of training trades whose trajectory intersects the test fold's bars, 3-session embargo; B's p* by an inner 3-fold on the training fold; A's Q-ensembles refit per fold.
- **Multiplicity**: every variant and every learner is a row of the append-only `exit_ledger.jsonl` + `vectors/*.npz` (harness-compatible per-session vectors: kept = the variant, skipped / all = the Foundation L1 exit on the same entries, so `harness.pbo(vecs, 'diff')`, `harness.spa`, `harness.effective_trials`, `harness.bootstrap_ci` read them unchanged). The harness ledger (`OUT/ledger/`) is for gates; this study writes to it only the gate x exit rows of section 8.
- **Pass rule** for an exit candidate (adapted from `harness.GO` to a policy-vs-Foundation difference on frozen entries): nested-CV diff > 0; CPCV 5th percentile diff > 0; random-exit percentile >= 95; 12-block sign-flip one-sided p <= 0.05 with >= 8 blocks positive; 90% block-bootstrap CI of the diff excludes 0; diff with the top 1% of per-trade gains removed > 0; PBO <= 0.2; SPA p <= 0.10 over the family.

## 2. Parity of the study's arithmetic with the lab (`parity.json`, `c_grid_check_*.json`)

**minute**: 4452 IS units, 443826 bars. `price_np` == `lab.price_trade` on 500 random (trade, exit bar) pairs: True (max |diff| 0.0); == `l1_net_inr` on every L1 exit: True. Floor vs the L1 label: 1251 stop_loss exits at the same bar and price: True; 473 eod / expiry exits with no stop before the cap: True; 2728 next_choch exits with the stop after the CHoCH bar (or the CHoCH on the cap bar, 8 cases): True. `exact_R` exact on 4452 / 4452 trades. **Floor vs `lab.manage` (Foundation stop, 1 lot, no target / trail, square_off 15:25) on every IS trade: 0 mismatches** (bar, price, reason). The grid's Foundation-stop-only variant reproduces the L1 label on its 1724 stop / cap exits (net within 0.005: True, exit bar: True); states per trade (extended trajectory): 74.6 mean, 331993 in all; the stop fires on 67.3% of trajectories.

**5minute**: 826 IS units, 88771 bars. `price_np` == `lab.price_trade` on 500 random (trade, exit bar) pairs: True (max |diff| 0.0); == `l1_net_inr` on every L1 exit: True. Floor vs the L1 label: 346 stop_loss exits at the same bar and price: True; 289 eod / expiry exits with no stop before the cap: True; 191 next_choch exits with the stop after the CHoCH bar (or the CHoCH on the cap bar, 1 cases): True. `exact_R` exact on 826 / 826 trades. **Floor vs `lab.manage` (Foundation stop, 1 lot, no target / trail, square_off 15:25) on every IS trade: 0 mismatches** (bar, price, reason). The grid's Foundation-stop-only variant reproduces the L1 label on its 635 stop / cap exits (net within 0.005: True, exit bar: True); states per trade (extended trajectory): 21.9 mean, 18124 in all; the stop fires on 55.1% of trajectories.

## 3. Learner C — the parametric grid by exact `lab.manage` replay

### minute (4452 IS units, 578 active sessions, 1568 variants; `c_variants_minute.csv`, `c_select_minute.json`)

Foundation L1 exit: mean **-1009.61** INR per trade, random-exit percentile 97.0, regret vs the free oracle 3569.61 (floor oracle 2367.55). Random control: mean of means -1078.86 (p5 -1135.97, p95 -1017.54). Oracles: free 2560.0, floor 1357.95.

Variants above the Foundation exit in sample: 226 / 1568. In-sample best (a trial): stop foundation / scale none / trail none / time_stop None / choch False: mean -904.77, diff 104.84 (t 2.59), random pct 100.0, sign blocks 10/12, bootstrap 90% CI of the diff [39.26, 173.51].

Marginal means per lot by grid dimension (mean / best over the other dimensions):

- **stop**: 35: -1045.8 (best -957.4); 50: -1050.9 (best -959.6); 75: -1056.8 (best -1002.2); foundation: -1030.7 (best -904.8)
- **scale**: L12: -1049.7 (best -967.5); L24: -1039.7 (best -938.1); none: -1034.2 (best -904.8); t1: -1068.0 (best -1038.4); t2: -1047.1 (best -959.3); t3: -1046.0 (best -966.4); t4: -1037.7 (best -943.1)
- **trail**: 2_1: -1047.4 (best -944.8); 2_2: -1046.0 (best -911.8); 3_1: -1047.8 (best -954.4); 3_2: -1045.2 (best -919.5); 4_1: -1046.1 (best -941.4); 4_2: -1045.4 (best -925.0); none: -1044.4 (best -904.8)
- **time_stop**: 30.0: -1072.3 (best -1038.4); 60.0: -1046.5 (best -970.0); 120.0: -1039.8 (best -927.2); nan: -1025.5 (best -904.8)
- **choch**: False: -1026.6 (best -904.8); True: -1065.5 (best -1010.4)

**Nested-CV pick** (`harness.purged_splits`, 12 folds): OOF mean **-923.04**, diff vs Foundation **86.57** (t 2.17), random pct 100.0, regret free 3483.03 / floor 2280.98, sign blocks 10/12, win rate 0.219, PF 0.499; bootstrap 90% CI of the diff [25.24, 151.11] (p(diff<=0) 0.0105). Ledger id `03637b2591d2f3f4`.

| fold | pick | train mean | test mean | test Foundation |
|---|---|---|---|---|
| 0 | stop foundation / scale none / trail none / time_stop None / choch False | -907.89 | -867.66 | -893.06 |
| 1 | stop foundation / scale none / trail none / time_stop None / choch False | -885.08 | -1112.54 | -945.49 |
| 2 | stop foundation / scale none / trail none / time_stop None / choch False | -896.15 | -963.89 | -962.3 |
| 3 | stop foundation / scale none / trail none / time_stop None / choch False | -906.93 | -860.31 | -961.76 |
| 4 | stop foundation / scale none / trail none / time_stop None / choch False | -910.43 | -845.88 | -900.12 |
| 5 | stop foundation / scale none / trail none / time_stop None / choch False | -893.64 | -975.92 | -1102.24 |
| 6 | stop foundation / scale none / trail 2_2 / time_stop None / choch False | -922.82 | -778.39 | -955.35 |
| 7 | stop foundation / scale none / trail none / time_stop None / choch False | -908.39 | -847.83 | -929.47 |
| 8 | stop foundation / scale none / trail none / time_stop None / choch False | -914.46 | -660.85 | -1262.9 |
| 9 | stop foundation / scale none / trail none / time_stop None / choch False | -883.36 | -1074.42 | -1085.95 |
| 10 | stop foundation / scale none / trail none / time_stop None / choch False | -907.99 | -851.83 | -1213.36 |
| 11 | stop foundation / scale none / trail 2_2 / time_stop None / choch False | -900.32 | -999.96 | -1112.32 |

**CPCV** (66 splits, 11 paths): diff median 80.19, p5 54.17, min 47.06, share of paths positive 1.0; 3 distinct picks: stop foundation / scale none / trail none / time_stop None / choch False (44 splits); stop foundation / scale none / trail 2_2 / time_stop None / choch False (20 splits); stop foundation / scale none / trail 3_2 / time_stop 120 / choch False (2 splits).

**Multiplicity over the family** (1568 variants): PBO ('diff', 12870 partitions) **0.0866**, IS-best OOS below zero 0.1806, degradation slope -0.9354; SPA (`harness.spa` sha `0fe3d75a0bd6e78d`, 2000 stationary-bootstrap draws, tag `exit|minute`, the same draws as 02_c_select.py): studentised (Hansen) best = stop 75 / scale none / trail none / time_stop None / choch True, mean selection gain 82.84 per session (t 1.683; active in 578 / 578 sessions; its per-trade diff vs Foundation is -13.27 — the SPA statistic is a per-session mean, so a variant can lead it with a negative per-trade diff), RC p 0.501, **SPA p 0.396**; unstudentised (White) best = stop 50 / scale none / trail none / time_stop None / choch False, mean gain 87.83 (per-trade diff 50.06), RC p 0.6845, **SPA p 0.5405**; min-active rule max(10, 5% of T) = 28 sessions: 0 of 1568 candidates excluded from the studentised family (none). Over every exit trial of the timeframe (1572 rows: the C variants, the C nested pick, the C in-sample best, learners B and A; tag `exit|all|minute`): studentised best = stop 75 / scale none / trail none / time_stop None / choch True (family `exit_policy/C`), RC p 0.5075, SPA p 0.3965; unstudentised RC p 0.695, SPA p 0.538; 0 excluded by the min-active rule. Effective trials 1.39 on the kept_sum series (harness) and **1.44** on the variant-minus-Foundation series (957 distinct gain vectors; variants that differ only by an inert key — e.g. a 120-bar time stop on 5 min, a CHoCH exit that never fires — are identical by construction). DSR of the in-sample best against 1568 trials: p 1.0.

**ST9 R-ladder** (stop 50, 1R / 2R, trail 3R lag 1, 3 lots): per position -3032.12, per lot -1010.71 (diff -1.1, t -0.02), random pct 97.0, sign blocks 8/12, win rate 0.3504, PF 0.498. It was tuned on 2026 (= this study's OOS window), so it cannot serve as an OOS comparator; here it is an IS comparator only.

Paired sign-flip tests of policy - Foundation (12 blocks exact; sessions 2,000 flips): C_nested: blocks p1 0.0149 (10/12 positive), sessions p1 0.0415; C_best_is: blocks p1 0.0125 (10/12 positive), sessions p1 0.018; ST9: blocks p1 0.3286 (8/12 positive), sessions p1 0.489.

### 5minute (826 IS units, 408 active sessions, 1568 variants; `c_variants_5minute.csv`, `c_select_5minute.json`)

Foundation L1 exit: mean **-757.05** INR per trade, random-exit percentile 96.8, regret vs the free oracle 3558.52 (floor oracle 2617.97). Random control: mean of means -932.62 (p5 -1091.13, p95 -773.85). Oracles: free 2801.47, floor 1860.92.

Variants above the Foundation exit in sample: 173 / 1568. In-sample best (a trial): stop 75 / scale t4 / trail 2_2 / time_stop None / choch False: mean -648.81, diff 108.24 (t 0.98), random pct 99.9, sign blocks 7/12, bootstrap 90% CI of the diff [-65.25, 293.9].

Marginal means per lot by grid dimension (mean / best over the other dimensions):

- **stop**: 35: -955.2 (best -838.0); 50: -882.7 (best -748.1); 75: -773.8 (best -648.8); foundation: -881.3 (best -741.5)
- **scale**: L12: -898.0 (best -768.4); L24: -840.8 (best -700.2); none: -803.2 (best -661.7); t1: -997.8 (best -864.3); t2: -892.9 (best -769.4); t3: -853.7 (best -713.0); t4: -826.2 (best -648.8)
- **trail**: 2_1: -874.1 (best -662.6); 2_2: -862.6 (best -648.8); 3_1: -879.1 (best -670.1); 3_2: -869.6 (best -666.8); 4_1: -880.0 (best -666.8); 4_2: -874.7 (best -666.8); none: -872.6 (best -666.8)
- **time_stop**: 30.0: -895.7 (best -756.0); 60.0: -877.8 (best -704.2); 120.0: -859.7 (best -648.8); nan: -859.7 (best -648.8)
- **choch**: False: -877.1 (best -648.8); True: -869.3 (best -660.2)

**Nested-CV pick** (`harness.purged_splits`, 12 folds): OOF mean **-818.36**, diff vs Foundation **-61.31** (t -0.68), random pct 88.3, regret free 3619.83 / floor 2679.28, sign blocks 5/12, win rate 0.3414, PF 0.651; bootstrap 90% CI of the diff [-182.92, 53.4] (p(diff<=0) 0.798). Ledger id `22e810e216567349`.

| fold | pick | train mean | test mean | test Foundation |
|---|---|---|---|---|
| 0 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch True | -718.09 | -290.06 | -474.91 |
| 1 | stop 75 / scale t4 / trail 2_1 / time_stop None / choch True | -709.01 | -391.19 | -316.76 |
| 2 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -647.57 | -671.99 | -219.17 |
| 3 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -603.15 | -928.56 | -789.91 |
| 4 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -628.61 | -860.37 | -907.87 |
| 5 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -552.83 | -1552.22 | -1232.75 |
| 6 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch True | -684.99 | -645.09 | -937.51 |
| 7 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -615.92 | -1148.69 | -988.08 |
| 8 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -668.17 | -569.03 | -616.93 |
| 9 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch True | -577.08 | -1435.51 | -1282.51 |
| 10 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -641.6 | -881.17 | -1337.85 |
| 11 | stop 75 / scale t4 / trail 2_2 / time_stop None / choch False | -651.31 | -626.49 | -264.51 |

**CPCV** (66 splits, 11 paths): diff median -9.41, p5 -65.24, min -73.11, share of paths positive 0.273; 5 distinct picks: stop 75 / scale none / trail 2_2 / time_stop None / choch False (3 splits); stop 75 / scale t4 / trail 2_1 / time_stop None / choch False (5 splits); stop 75 / scale t4 / trail 2_1 / time_stop None / choch True (5 splits); stop 75 / scale t4 / trail 2_2 / time_stop None / choch False (32 splits); stop 75 / scale t4 / trail 2_2 / time_stop None / choch True (21 splits).

**Multiplicity over the family** (1568 variants): PBO ('diff', 12870 partitions) **0.1426**, IS-best OOS below zero 0.504, degradation slope -0.6991; SPA (`harness.spa` sha `0fe3d75a0bd6e78d`, 2000 stationary-bootstrap draws, tag `exit|5minute`, the same draws as 02_c_select.py): studentised (Hansen) best = stop 75 / scale t4 / trail 2_2 / time_stop None / choch True, mean selection gain 281.96 per session (t 2.761; active in 408 / 408 sessions; its per-trade diff vs Foundation is 96.83), RC p 0.5175, **SPA p 0.4965**; unstudentised (White) best = stop 75 / scale t4 / trail 2_2 / time_stop None / choch True, mean gain 281.96 (per-trade diff 96.83), RC p 0.2465, **SPA p 0.1505**; min-active rule max(10, 5% of T) = 20 sessions: 0 of 1568 candidates excluded from the studentised family (none). Over every exit trial of the timeframe (1572 rows: the C variants, the C nested pick, the C in-sample best, learners B and A; tag `exit|all|5minute`): studentised best = stop 75 / scale t4 / trail 2_2 / time_stop None / choch True (family `exit_policy/C`), RC p 0.5045, SPA p 0.4825; unstudentised RC p 0.2565, SPA p 0.1505; 0 excluded by the min-active rule. Effective trials 1.61 on the kept_sum series (harness) and **2.28** on the variant-minus-Foundation series (720 distinct gain vectors; variants that differ only by an inert key — e.g. a 120-bar time stop on 5 min, a CHoCH exit that never fires — are identical by construction). DSR of the in-sample best against 1568 trials: p 0.9998.

**ST9 R-ladder** (stop 50, 1R / 2R, trail 3R lag 1, 3 lots): per position -2747.78, per lot -915.93 (diff -158.88, t -1.47), random pct 56.4, sign blocks 1/12, win rate 0.3644, PF 0.554. It was tuned on 2026 (= this study's OOS window), so it cannot serve as an OOS comparator; here it is an IS comparator only.

Paired sign-flip tests of policy - Foundation (12 blocks exact; sessions 2,000 flips): C_nested: blocks p1 0.7454 (5/12 positive), sessions p1 0.7725; C_best_is: blocks p1 0.219 (7/12 positive), sessions p1 0.153; ST9: blocks p1 0.9951 (1/12 positive), sessions p1 0.915.

## 4. Learner B — hindsight imitation (`b_result_*.json`, `b_oof_*.npz`)

**minute**: 331993 states over 4452 trades (25 features), HGB {'max_iter': 300, 'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 200, 'l2_regularization': 1.0, 'class_weight': 'balanced', 'random_state': 7}. OOF mean **-908.8** vs Foundation -1009.61 (diff 100.8, t 2.48), random pct 100.0, regret free 3468.8 / floor 2266.75, early-exit share 0.0705, OOF AUC of 'this is the oracle bar' 0.9467, sign-flip blocks p1 0.0129, sessions p1 0.027. Ledger id `2c42dc9484b1ea05`. 554.4 s, RSS 963 MB.

| fold | train / test trades (purged) | p* | inner value at p* / never-exit / Foundation | test mean | test Foundation | test AUC | early exits |
|---|---|---|---|---|---|---|---|
| 0 | 2746 / 1677 (29) | never exit | -875.57 / -875.57 / -1047.17 | -944.12 | -941.9 | 0.9441 | 0.0 |
| 1 | 3031 / 1421 (0) | 0.9506 | -932.16 / -941.19 / -1027.9 | -839.71 | -970.6 | 0.9484 | 0.221 |
| 2 | 3098 / 1354 (0) | never exit | -890.44 / -890.44 / -955.06 | -937.57 | -1134.41 | 0.9486 | 0.0 |

Plainly: on minute the learner B exit is above the Foundation exit on the pooled OOF by 100.8 INR per trade (t 2.48) (the 90% block-bootstrap CI of the diff excludes 0); it is below the Foundation exit in 1 of 3 folds (folds 0) and above it in 2 (folds 1, 2); random-exit percentile 100.0; bootstrap 90% CI of the diff [32.95, 167.98]; diff with the top 1% of per-trade gains removed -54.75; C nested pick OOF mean -923.04; A OOF mean -972.05 (this learner -908.8). Pass rule: oof_diff>0: pass (100.8), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: pass (100.0), signflip_blocks_p1<=0.05: pass (0.0129), blocks_positive>=8/12: pass (10), boot_ci90_excludes_0: pass ([32.95, 167.98]), diff_top1_gains_removed>0: FAIL (-54.75), pbo<=0.2: pass (0.0866), spa_p<=0.10: FAIL (0.3965). **no candidate**.

**5minute**: 18124 states over 826 trades (25 features), HGB {'max_iter': 300, 'learning_rate': 0.05, 'max_leaf_nodes': 31, 'min_samples_leaf': 200, 'l2_regularization': 1.0, 'class_weight': 'balanced', 'random_state': 7}. OOF mean **-777.31** vs Foundation -757.05 (diff -20.26, t -0.38), random pct 94.6, regret free 3578.78 / floor 2638.23, early-exit share 0.0, OOF AUC of 'this is the oracle bar' 0.8921, sign-flip blocks p1 0.5745, sessions p1 0.6685. Ledger id `89209a10789d61cc`. 257.9 s, RSS 508 MB.

| fold | train / test trades (purged) | p* | inner value at p* / never-exit / Foundation | test mean | test Foundation | test AUC | early exits |
|---|---|---|---|---|---|---|---|
| 0 | 535 / 283 (8) | 0.942 | -892.84 / -908.14 / -890.79 | -493.55 | -475.16 | 0.8967 | 0.0 |
| 1 | 553 / 273 (0) | never exit | -647.46 / -647.46 / -628.19 | -1040.36 | -1018.09 | 0.8784 | 0.0 |
| 2 | 556 / 270 (0) | 0.9583 | -754.34 / -762.04 / -741.74 | -808.77 | -788.58 | 0.9011 | 0.0 |

Plainly: on 5minute the learner B exit is below the Foundation exit on the pooled OOF by 20.26 INR per trade (t -0.38) (the 90% block-bootstrap CI of the diff includes 0: not significantly); it is below the Foundation exit in 3 of 3 folds (folds 0, 1, 2); random-exit percentile 94.6; bootstrap 90% CI of the diff [-100.38, 59.33]; diff with the top 1% of per-trade gains removed -127.5; C nested pick OOF mean -818.36; A OOF mean -902.39 (this learner -777.31). Pass rule: oof_diff>0: FAIL (-20.26), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: FAIL (94.6), signflip_blocks_p1<=0.05: FAIL (0.5745), blocks_positive>=8/12: FAIL (4), boot_ci90_excludes_0: FAIL ([-100.38, 59.33]), diff_top1_gains_removed>0: FAIL (-127.5), pbo<=0.2: pass (0.1426), spa_p<=0.10: FAIL (0.4825). **no candidate**.

## 5. Learner A — fitted Q-iteration, pessimistic ensemble (`a_result_*.json`, `a_oof_*.npz`)

**minute**: 327541 decision states (331993 states, 4452 trades), 20 iterations x 5 members, kappa 1.0, HGB {'max_iter': 200, 'learning_rate': 0.1, 'max_leaf_nodes': 31, 'min_samples_leaf': 100, 'l2_regularization': 1.0, 'random_state': 11}. OOF mean **-972.05** vs Foundation -1009.61 (diff 37.56, t 1.01), random pct 99.8, regret free 3532.05 / floor 2329.99, early-exit share 0.3064, sign-flip blocks p1 0.2034 (7/12 positive), sessions p1 0.169. Ledger id `25190ffebaf1dc07`. 9693.2 s, RSS 1000 MB.

| fold | train / test trades (purged) | test mean | test Foundation | test diff | early exits | exit-flag share of states | MAE of Q(s, exit) vs the exact exit value | seconds |
|---|---|---|---|---|---|---|---|---|
| 0 | 2746 / 1677 (29) | -969.21 | -941.9 | -27.31 | 0.2815 | 0.0415 | 120.2 | 3078.2 |
| 1 | 3031 / 1421 (0) | -1010.4 | -970.6 | -39.8 | 0.3174 | 0.0695 | 211.52 | 4408.9 |
| 2 | 3098 / 1354 (0) | -935.3 | -1134.41 | 199.11 | 0.3257 | 0.023 | 118.78 | 2199.4 |

Plainly: on minute the learner A exit is above the Foundation exit on the pooled OOF by 37.56 INR per trade (t 1.01) (the 90% block-bootstrap CI of the diff includes 0: not a significant gain); it is below the Foundation exit in 2 of 3 folds (folds 0, 1) and above it in 1 (folds 2); random-exit percentile 99.8; bootstrap 90% CI of the diff [-26.69, 99.52]; diff with the top 1% of per-trade gains removed -51.5; C nested pick OOF mean -923.04; B OOF mean -908.8 (this learner -972.05). Pass rule: oof_diff>0: pass (37.56), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: pass (99.8), signflip_blocks_p1<=0.05: FAIL (0.2034), blocks_positive>=8/12: FAIL (7), boot_ci90_excludes_0: FAIL ([-26.69, 99.52]), diff_top1_gains_removed>0: FAIL (-51.5), pbo<=0.2: pass (0.0866), spa_p<=0.10: FAIL (0.3965). **no candidate**.

**5minute**: 17298 decision states (18124 states, 826 trades), 20 iterations x 5 members, kappa 1.0, HGB {'max_iter': 200, 'learning_rate': 0.1, 'max_leaf_nodes': 31, 'min_samples_leaf': 100, 'l2_regularization': 1.0, 'random_state': 11}. OOF mean **-902.39** vs Foundation -757.05 (diff -145.34, t -1.37), random pct 62.7, regret free 3703.86 / floor 2763.31, early-exit share 0.5811, sign-flip blocks p1 0.9597 (4/12 positive), sessions p1 0.9175. Ledger id `142df5863c0422ba`. 902.1 s, RSS 510 MB.

| fold | train / test trades (purged) | test mean | test Foundation | test diff | early exits | exit-flag share of states | MAE of Q(s, exit) vs the exact exit value | seconds |
|---|---|---|---|---|---|---|---|---|
| 0 | 535 / 283 (8) | -655.89 | -475.16 | -180.73 | 0.576 | 0.1285 | 155.1 | 300.7 |
| 1 | 553 / 273 (0) | -1184.61 | -1018.09 | -166.52 | 0.5275 | 0.1322 | 116.41 | 290.2 |
| 2 | 556 / 270 (0) | -875.4 | -788.58 | -86.82 | 0.6407 | 0.195 | 142.66 | 305.9 |

Plainly: on 5minute the learner A exit is below the Foundation exit on the pooled OOF by 145.34 INR per trade (t -1.37): **it hurts** (the 90% block-bootstrap CI of the diff lies entirely below 0); it is below the Foundation exit in 3 of 3 folds (folds 0, 1, 2); random-exit percentile 62.7; bootstrap 90% CI of the diff [-301.88, -1.01]; diff with the top 1% of per-trade gains removed -246.11; C nested pick OOF mean -818.36; B OOF mean -777.31 (this learner -902.39). Pass rule: oof_diff>0: FAIL (-145.34), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: FAIL (62.7), signflip_blocks_p1<=0.05: FAIL (0.9597), blocks_positive>=8/12: FAIL (4), boot_ci90_excludes_0: FAIL ([-301.88, -1.01]), diff_top1_gains_removed>0: FAIL (-246.11), pbo<=0.2: pass (0.1426), spa_p<=0.10: FAIL (0.4825). **no candidate**.

## 6. Evaluation on IS CV — net per trade per lot on the same entries, all cut at 15:25 (`eval_table_*.csv`)

### minute

| policy | mean_per_lot | diff_vs_foundation | random_pct | regret_vs_oracle_free | regret_vs_oracle_floor | win_rate | pf | sign_blocks | signflip_blocks_p1 | signflip_sessions_p1 | boot_diff_ci90 | diff_top1_gains_removed | bars_held_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Foundation L1 exit (stop / next CHoCH / 15:25) | -1009.61 | 0.0 | 97.0 | 3569.61 | 2367.55 | 0.1559 | 0.323 | 0.0 |  |  |  |  | 33.1 |
| ST9 R-ladder (3 lots, stop 50, 1R/2R, trail 3R lag 1) per lot | -1010.71 | -1.1 | 97.0 | 3570.71 | 2368.65 | 0.3504 | 0.498 | 8.0 | 0.3286 | 0.5015 | [-66.95, 63.6] | -90.32 | 114.6 |
| C nested-CV pick (OOF) | -923.04 | 86.57 | 100.0 | 3483.03 | 2280.98 | 0.219 | 0.499 | 10.0 | 0.0149 | 0.039 | [22.1, 151.74] | -67.49 | 71.4 |
| C in-sample best (a trial) | -904.77 | 104.84 | 100.0 | 3464.77 | 2262.72 | 0.2156 | 0.515 | 10.0 | 0.0125 | 0.0195 | [36.72, 172.77] | -51.21 | 74.6 |
| B hindsight imitation (OOF) | -908.8 | 100.8 | 100.0 | 3468.8 | 2266.75 | 0.2098 | 0.508 | 10.0 | 0.0129 | 0.018 | [32.95, 167.98] | -54.75 | 72.4 |
| A FQI pessimistic ensemble (OOF) | -972.05 | 37.56 | 99.8 | 3532.05 | 2329.99 | 0.263 | 0.441 | 7.0 | 0.2034 | 0.1715 | [-26.69, 99.52] | -51.5 | 49.2 |
| hindsight oracle, best close exit, no stop (upper bound) | 2560.0 | 3569.61 | 100.0 | 0.0 | -1202.05 | 0.7013 | 12.139 | 12.0 | 0.0002 | 0.0 | [3289.45, 3881.03] | 3351.64 | 87.6 |
| hindsight oracle on the Foundation-stop trajectory | 1357.95 | 2367.55 | 100.0 | 1202.05 | 0.0 | 0.4843 | 3.834 | 12.0 | 0.0002 | 0.0 | [2186.03, 2544.05] | 2191.29 | 44.2 |
| random exit (2,000 draws): mean of means | -1078.86 | -69.25 | 50.0 | 3638.86 | 2436.8 |  |  |  |  |  |  |  |  |


### 5minute

| policy | mean_per_lot | diff_vs_foundation | random_pct | regret_vs_oracle_free | regret_vs_oracle_floor | win_rate | pf | sign_blocks | signflip_blocks_p1 | signflip_sessions_p1 | boot_diff_ci90 | diff_top1_gains_removed | bars_held_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Foundation L1 exit (stop / next CHoCH / 15:25) | -757.05 | 0.0 | 96.8 | 3558.52 | 2617.97 | 0.2772 | 0.639 | 0.0 |  |  |  |  | 19.3 |
| ST9 R-ladder (3 lots, stop 50, 1R/2R, trail 3R lag 1) per lot | -915.93 | -158.88 | 56.4 | 3717.4 | 2776.85 | 0.3644 | 0.554 | 1.0 | 0.9951 | 0.9355 | [-348.04, 26.56] | -279.47 | 23.6 |
| C nested-CV pick (OOF) | -818.36 | -61.31 | 88.3 | 3619.83 | 2679.28 | 0.3414 | 0.651 | 5.0 | 0.7454 | 0.742 | [-182.33, 65.72] | -204.16 | 26.3 |
| C in-sample best (a trial) | -648.81 | 108.24 | 99.9 | 3450.28 | 2509.73 | 0.3814 | 0.73 | 7.0 | 0.219 | 0.1575 | [-58.21, 287.68] | -73.42 | 29.3 |
| B hindsight imitation (OOF) | -777.31 | -20.26 | 94.6 | 3578.78 | 2638.23 | 0.3027 | 0.655 | 4.0 | 0.5745 | 0.6545 | [-100.38, 59.33] | -127.5 | 21.9 |
| A FQI pessimistic ensemble (OOF) | -902.39 | -145.34 | 62.7 | 3703.86 | 2763.31 | 0.2579 | 0.489 | 4.0 | 0.9597 | 0.908 | [-301.88, -1.01] | -246.11 | 11.0 |
| hindsight oracle, best close exit, no stop (upper bound) | 2801.47 | 3558.52 | 100.0 | 0.0 | -940.55 | 0.6671 | 9.855 | 12.0 | 0.0002 | 0.0 | [3156.44, 4023.84] | 3251.26 | 20.2 |
| hindsight oracle on the Foundation-stop trajectory | 1860.92 | 2617.97 | 100.0 | 940.55 | 0.0 | 0.5448 | 4.47 | 12.0 | 0.0002 | 0.0 | [2401.45, 2839.8] | 2487.41 | 13.3 |
| random exit (2,000 draws): mean of means | -932.62 | -175.57 | 50.0 | 3734.09 | 2793.54 |  |  |  |  |  |  |  |  |


The per-trade difference is slippage-invariant for the 1-lot policies (one round trip per lot each); at 8 pts per side every per-lot mean above moves by -390 INR (`mean_slip8` in the CSV).

## 7. Distillation (`exit_rules_*.json`)

**minute**: best learner by OOF mean = **B** (-908.8); visited decision states 317981, early-exit decisions 314. Depth-3 tree fidelity: accuracy 0.9822, exit recall 0.9873, exit precision 0.0518; the distilled policy replayed on IS (in sample for the tree): mean -1075.16, diff vs Foundation -65.55, random pct 56.5, early exits 0.9861; 3 exit rules.

- `{"bars_held": ["<=", 1.5], "dd_from_mfe_R": ["<=", 0.2595]}` -> exit_all (support 2780 states, exit share 0.785)
- `{"bars_held": ["<=", 1.5], "dd_from_mfe_R": [">", 0.2595]}` -> exit_all (support 1610 states, exit share 0.995)
- `{"bars_held": [">", 1.5], "session_bar": [">", 355.5], "dd_from_mfe_R": ["<=", 0.1228]}` -> exit_all (support 1589 states, exit share 0.96)

**5minute**: best learner by OOF mean = **B** (-777.31); visited decision states 17298, early-exit decisions 0. the best learner exits early on fewer than 20 visited states: nothing to distil (the policy is 'hold to the stop / 15:25')


The `exit_rules` list is a new key type (a per-bar rule evaluator the lab does not have): a user decision. Learner C's keys `{stop, scale_out, trail, square_off, time_stop_bars, exit_on_choch_against}` are the shippable form; `stop: foundation_sl` combined with targets / trail is also not an existing key (today `exit: "strategy"` gives the Foundation stop with the next-CHoCH exit, `exit: "position"` a fixed-points stop).

## 8. Multiplication with the frozen ST7/ST8 gate (`harness.score` rows, family `exit_policy/gate_x_exit`)

**minute** frozen gate under the L1 exit (harness id `f8ea66553101dc24`): kept 745, kept mean -1026.02, skipped mean -1006.31, diff -19.71, control pct 62.6.

| exit applied | harness id | kept n | kept mean | skipped mean | diff | control pct | perm p | sign blocks | gate rows: Foundation -> exit mean (diff) | gate-row sign-flip blocks p1 | gate-row bootstrap CI | book net Foundation -> exit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C_nested | `ac28bea0c7c26c6f` | 745 | -1007.56 | -906.05 | -101.51 | 47.2 | 0.4808 | 6 | -1026.02 -> -1007.56 (18.46) | 0.2639 (7/12) | [-131.98, 182.55] | -764386.22 -> -750630.5 |
| B | `aee3ef4df479e783` | 745 | -1003.52 | -889.77 | -113.75 | 37.6 | 0.4473 | 6 | -1026.02 -> -1003.52 (22.5) | 0.2544 (7/12) | [-135.29, 184.67] | -764386.22 -> -747620.79 |
| A | `d8498e6c63bb83d2` | 745 | -1077.61 | -950.83 | -126.78 | 18.3 | 0.2309 | 4 | -1026.02 -> -1077.61 (-51.59) | 0.4924 (5/12) | [-171.72, 77.15] | -764386.22 -> -802821.02 |

**5minute** frozen gate under the L1 exit (harness id `60662a5e5ab612f8`): kept 325, kept mean -978.81, skipped mean -613.2, diff -365.62, control pct 13.6.

| exit applied | harness id | kept n | kept mean | skipped mean | diff | control pct | perm p | sign blocks | gate rows: Foundation -> exit mean (diff) | gate-row sign-flip blocks p1 | gate-row bootstrap CI | book net Foundation -> exit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C_nested | `c848ec6556660c33` | 325 | -1060.71 | -661.15 | -399.56 | 20.4 | 0.2694 | 4 | -978.81 -> -1060.71 (-81.9) | 0.4773 (5/12) | [-268.59, 111.44] | -318113.81 -> -344730.07 |
| B | `9761a89581b47c91` | 325 | -1016.89 | -621.9 | -394.99 | 12.3 | 0.2334 | 3 | -978.81 -> -1016.89 (-38.08) | 0.5012 (5/12) | [-157.93, 89.84] | -318113.81 -> -330488.47 |
| A | `244ab07b9f1c0f15` | 325 | -862.61 | -928.19 | 65.58 | 8.3 | 0.7921 | 4 | -978.81 -> -862.61 (116.2) | 0.1079 (8/12) | [-81.51, 312.38] | -318113.81 -> -280349.06 |

## 9. Pass rule, candidates, verdict

**minute** — learner C nested pick: nested_diff>0: pass (86.57), cpcv_p5_diff>0: pass (54.17), random_pct>=95: pass (100.0), signflip_blocks_p1<=0.05: pass (0.0149), blocks_positive>=8/12: pass (10), boot_ci90_excludes_0: pass ([25.24, 151.11]), diff_top1_gains_removed>0: FAIL (-67.49), pbo<=0.2: pass (0.0866), spa_p<=0.10: FAIL (0.396). **no candidate**.

**minute** — learner B (OOF; the CPCV item is not evaluable for the 3-fold learners, PBO is the C family's, SPA p the studentised p over every exit trial): oof_diff>0: pass (100.8), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: pass (100.0), signflip_blocks_p1<=0.05: pass (0.0129), blocks_positive>=8/12: pass (10), boot_ci90_excludes_0: pass ([32.95, 167.98]), diff_top1_gains_removed>0: FAIL (-54.75), pbo<=0.2: pass (0.0866), spa_p<=0.10: FAIL (0.3965). **no candidate**.

**minute** — learner A (OOF; the CPCV item is not evaluable for the 3-fold learners, PBO is the C family's, SPA p the studentised p over every exit trial): oof_diff>0: pass (37.56), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: pass (99.8), signflip_blocks_p1<=0.05: FAIL (0.2034), blocks_positive>=8/12: FAIL (7), boot_ci90_excludes_0: FAIL ([-26.69, 99.52]), diff_top1_gains_removed>0: FAIL (-51.5), pbo<=0.2: pass (0.0866), spa_p<=0.10: FAIL (0.3965). **no candidate**.

**5minute** — learner C nested pick: nested_diff>0: FAIL (-61.31), cpcv_p5_diff>0: FAIL (-65.24), random_pct>=95: FAIL (88.3), signflip_blocks_p1<=0.05: FAIL (0.7454), blocks_positive>=8/12: FAIL (5), boot_ci90_excludes_0: FAIL ([-182.92, 53.4]), diff_top1_gains_removed>0: FAIL (-204.16), pbo<=0.2: pass (0.1426), spa_p<=0.10: FAIL (0.4965). **no candidate**.

**5minute** — learner B (OOF; the CPCV item is not evaluable for the 3-fold learners, PBO is the C family's, SPA p the studentised p over every exit trial): oof_diff>0: FAIL (-20.26), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: FAIL (94.6), signflip_blocks_p1<=0.05: FAIL (0.5745), blocks_positive>=8/12: FAIL (4), boot_ci90_excludes_0: FAIL ([-100.38, 59.33]), diff_top1_gains_removed>0: FAIL (-127.5), pbo<=0.2: pass (0.1426), spa_p<=0.10: FAIL (0.4825). **no candidate**.

**5minute** — learner A (OOF; the CPCV item is not evaluable for the 3-fold learners, PBO is the C family's, SPA p the studentised p over every exit trial): oof_diff>0: FAIL (-145.34), cpcv_p5_diff>0: FAIL (n/a: 3-fold OOF by design, no CPCV paths), random_pct>=95: FAIL (62.7), signflip_blocks_p1<=0.05: FAIL (0.9597), blocks_positive>=8/12: FAIL (4), boot_ci90_excludes_0: FAIL ([-301.88, -1.01]), diff_top1_gains_removed>0: FAIL (-246.11), pbo<=0.2: pass (0.1426), spa_p<=0.10: FAIL (0.4825). **no candidate**.

## 10. Follow-up (2026-09-29 16:45 IST)

What changed and why (the two refuters' minor findings, plus the one finalize step that had not run). Nothing else was rerun: the learner C grid (`01_c_grid.py`), the C selection (`02_c_select.py`), learner B (`03_b_imitation.py`) and every FQI fold (`04_a_fqi.py`) are the runs already on disk.

1. **Learner A on 1 min.** Judge 2's condition for the 1-minute FQI (learner B or C beating the Foundation exit OOF on 1 min) was met (B +100.8, C nested +86.57); `04_a_fqi.py minute` ran under nohup and finished at 07:08 UTC (`a_result_minute.json`, `a_oof_minute.npz`, exit-ledger row `25190ffebaf1dc07`, family `exit_policy/A`; `04_a_minute.log` holds the three per-fold JSON lines — its final summary line was lost when the 06:24 checkout replaced the file's inode, the JSON was written before it). The earlier section 5 sentence "not run: the condition ... was not met" was `06_findings.py`'s fallback text while the run was in progress and was wrong; it is replaced by the measured numbers. Per fold (test mean vs Foundation): fold 0: -969.21 vs -941.9 (-27.31), early exits 0.2815, Q-fit MAE 120.2; fold 1: -1010.4 vs -970.6 (-39.8), early exits 0.3174, Q-fit MAE 211.52; fold 2: -935.3 vs -1134.41 (199.11), early exits 0.3257, Q-fit MAE 118.78. Pooled OOF mean -972.05 vs -1009.61 (diff 37.56, t 1.01), random-exit percentile 99.8, early-exit share 0.3064; below the Foundation exit in 2 of 3 folds; it does not beat learner B (-908.8) or the C nested pick (-923.04); pass rule: **no candidate** (section 9). On 5 min (already in `a_result_5minute.json`, now also in sections 6, 8, 9): pooled OOF -902.39 vs -757.05 (diff -145.34, t -1.37), random pct 62.7, below the Foundation exit in 3 of 3 folds: **it hurts**.

2. **Family SPA with the current `harness.spa`** (sha `0fe3d75a0bd6e78d`; `harness.py` was not modified here). The earlier numbers came from `02_c_select.py` with the harness before its revision; the harness now excludes from the studentised (Hansen) family any candidate whose selection gain is non-zero in fewer than max(10, 5% of T) sessions (1 min: 28 of 578 sessions; 5 min: 20 of 408) and reports White's unstudentised reality-check statistic beside it. Re-run over the same family (the 1,568 C variants, ledger order) with the same bootstrap tag, so the only change is the harness: **1 min** studentised SPA p 0.396 -> **0.396** (RC p 0.501 -> 0.501; best variant 785 -> 785), unstudentised SPA p **0.5405** (RC p 0.6845); **5 min** studentised SPA p 0.4965 -> **0.4965** (RC p 0.5175 -> 0.5175; best 1025 -> 1025), unstudentised SPA p **0.1505** (RC p 0.2465). Candidates excluded by the min-active rule: 1 min 0, 5 min 0 — **none on either timeframe**: every grid variant's selection gain is non-zero in every active session (no variant applies the Foundation's next-CHoCH exit, so every variant differs from the benchmark wherever a session has a trade), so the studentised numbers are unchanged and the revision adds the unstudentised p. The extended family (every exit trial, learners included) is in section 3. `c_select_<tf>.json`'s `spa` block is the finished stage's output and was not edited; `eval_<tf>.json` `spa_family` / `spa_all_trials` and `findings.json` carry the new block, `spa_superseded_02_c_select` the old one.

3. **`05_evaluate.py 5minute` ran for the first time** (it had not been run when the 5 min learners finished): `eval_table_5minute.csv`, `eval_5minute.json`, `exit_rules_5minute.json` (best learner B exits early on 0 states: nothing to distil), the 5 min effective-trials figure on the gain series and the top-1%-removed pass item, the gate x exit rows; the PRELIMINARY status of section 9 is closed.

**Ledgers.** Exit ledger (`exit_ledger.jsonl`): 3174 rows, nothing appended by the follow-up (learner A's rows were written by `04_a_fqi.py`). Harness ledger (`OUT/ledger/trials.jsonl`): 4 new rows, note `followup`: `d8498e6c63bb83d2` (minute, L1entries_x_A); `c848ec6556660c33` (5minute, L1entries_x_C_nested); `9761a89581b47c91` (5minute, L1entries_x_B); `244ab07b9f1c0f15` (5minute, L1entries_x_A); reused by id, no duplicate written: minute: C_nested `ac28bea0c7c26c6f`, B `aee3ef4df479e783`.

**Verdict after the follow-up**: unchanged — minute: learner C nested pick no candidate, learner B no candidate, learner A no candidate; 5minute: learner C nested pick no candidate, learner B no candidate, learner A no candidate. No exit policy rescues the book on either timeframe; the null result stands.

