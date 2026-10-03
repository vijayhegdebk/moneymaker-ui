# regime_gate: the machine-found 'chop' state as a gate (DESIGN_PANEL deep-sequence-regime-states, both judges' fixes; 5 minutes only)

**What this study is.** The regime-states study as the two judges left it: Judge 1 cut it to 'run the HMM only if study 3 (importance) shows the H2 counts are not already the regime cluster, and then on 5m only'; Judge 2 kept it with the state posteriors emitted as candidate features to the importance study and the tau grid run only if a state shows a kept-vs-skipped signal at matched skip fraction against `n_choch_since_bos`. This is that conditional run on **5 minutes, label L1, IS only**: the chop-state gate *skip when P(chop) >= tau* for hmm3 / hmm4 / gmm4 / jump4 and jump3, tau in {0.5, 0.6, 0.7, 0.8, 0.9}, the chop state identified per TRAINING fold as the state with the worst L1 expectancy, nested tau, the 11 CPCV paths, `harness.go_no_go` with the null-tape replay, the depth-3 distillation, and the comparison with the H2 hand rule at matched skip fraction. Every column this study reads is **outside the frozen shortlist** (`features_shortlist/5minute/shortlist.json`: `n_shortlisted` = 0 of 39 clusters; sha256 `4747257f41ecb40f...`), so every ledger row carries that note and nothing here can be frozen as a candidate without the user accepting that provenance. Scripts `rg_lib.py` (definitions, the frozen-model replay), `regime_gate.py` (the run; log `regime_gate.log`), `diagnostics.py` (label-free, section 7b), `write_findings.py`; runtime 244.1 s, max RSS 535.9 MB; ledger sha before `9e7241f03ba435dd`, after `48625a58eac73cde`. **Result: null** (section 12).

## 0. The gating question: do the H2 CHoCH counts and the state posteriors share a cluster, and did a state column make the shortlist?

Read from `studies/importance/FINDINGS.md` (5minute, 'Do the H2 CHoCH counts and the state-model posteriors share a cluster?') and `features_shortlist/5minute/shortlist.json` (`h2_vs_state_models`):

| state-model column | cluster | same cluster as `n_choch_since_bos` (3) |
|---|---|---|
| gmm3_p0 | 3 | yes |
| gmm3_p1 | 5 | no |
| gmm3_p2 | 0 | no |
| gmm3_map | 0 | no |
| gmm4_p0 | 5 | no |
| gmm4_p1 | 3 | yes |
| gmm4_p2 | 5 | no |
| gmm4_p3 | 0 | no |
| gmm4_map | 0 | no |
| hmm3_p0 | 3 | yes |
| hmm3_p1 | 5 | no |
| hmm3_p2 | 0 | no |
| hmm3_map | 0 | no |
| hmm3_map_run | 3 | yes |
| hmm4_p0 | 5 | no |
| hmm4_p1 | 5 | no |
| hmm4_p2 | 3 | yes |
| hmm4_p3 | 5 | no |
| hmm4_map | 0 | no |
| hmm4_map_run | 3 | yes |
| jump3_state | 25 | no |
| jump3_run | 25 | no |
| jump4_state | 3 | yes |
| jump4_run | 0 | no |

- H2 count columns: `n_choch_since_bos` -> 3, `n_choch_since_bos_today` -> 3, `alt_dir6` -> 3, `alt_kind6` -> 5.
- In the `n_choch_since_bos` cluster: `gmm3_p0`, `gmm4_p1`, `hmm3_map_run`, `hmm3_p0`, `hmm4_map_run`, `hmm4_p2`, `jump4_state` (one posterior per model: the state whose mean `choch_since_bos` input is high, i.e. the 'recent CHoCH, no BOS' state, plus the HMM run lengths and `jump4_state`).
- Elsewhere: `gmm3_p1` (5), `gmm3_p2` (0), `gmm3_map` (0), `gmm4_p0` (5), `gmm4_p2` (5), `gmm4_p3` (0), `gmm4_map` (0), `hmm3_p1` (5), `hmm3_p2` (0), `hmm3_map` (0), `hmm4_p0` (5), `hmm4_p1` (5), `hmm4_p3` (5), `hmm4_map` (0), `jump3_state` (25), `jump3_run` (25), `jump4_run` (0): the quiet / volatile states sit in the volatility cluster 0 and the `n_bos_since_choch` cluster 5; **`jump3_state` and `jump3_run` form their own cluster 25**.
- Any state column shortlisted: **no** (the shortlist is empty on both timeframes: 0 of 39 clusters pass the pre-registered MDA rule).

**Verdict on the question: in part: the CHoCH-like posterior of each model shares the n_choch_since_bos cluster (3); the other posteriors sit in clusters [0, 5, 25]; jump3_state / jump3_run form their own cluster 25.** The counts and the states are therefore NOT one cluster, so the conditional run proceeds (5 minutes only). jump3 was added to the design's four models because on 5 minutes its columns are a cluster of their own and that cluster's SFI gate was the importance family's SPA-best row (ledger `4535288bcf0f1148`: kept share 0.868, diff 827.00 INR, control 100.0th pct, permutation p 0.078, 8/12 blocks); the claim 'the jump3 state marks losers' is exactly what a nested-threshold gate tests, so it is in this family and counted like every other cell. The importance study's own reading stands for the posteriors that share cluster 3 with the count: where a state posterior sits in the count's cluster the state model adds nothing the count does not say; this study measures whether the *gate built on it* adds anything at matched skip fraction.

## 1. Definitions (fixed before the numbers; `rg_lib.py` docstring verbatim)

```
regime_gate library (DESIGN_PANEL deep-sequence-regime-states as conditioned by both judges; 5 minutes only, Judge 1).

Definitions fixed before any number was looked at (also in FINDINGS.md section 1):

  unit / label   a harness row: a Foundation SETUP taken under the L1 (15:25) book, harness.load("5minute"); IS rows only
  models         hmm3, hmm4 (forward-filtered posteriors P(s_k = j | x_<=k), features_ext/5minute/ext_features.parquet columns
                 hmm{K}_p{j}), gmm4 (the no-dynamics posterior gmm4_p{j}), jump4 and jump3 (the ONLINE prefix state jump{K}_state,
                 a hard state: P(state = j) is its one-hot, so P(chop) is 0 or 1 and the tau grid is degenerate for them; every
                 tau cell is still a ledger row). jump3 was added after the importance study: its two columns form their own
                 cluster 25 on 5 minutes and that cluster's SFI gate was the importance family's SPA-best row (ledger
                 4535288bcf0f1148: kept share 0.868, diff +827 INR, control 100th pct, permutation p 0.078, 8/12 blocks); the claim
                 "the jump3 state marks losers" is exactly what this study tests with a nested threshold, so it is in the family.
  MAP state      argmax_j P_j at the SETUP bar (for a jump model the state itself)
  chop state     identified on the TRAINING rows of a fold as the MAP state with the lowest mean L1 net among the states with at
                 least one training row (the state with the worst L1 expectancy); nothing else is read on the test rows
  gate           skip the SETUP when P(chop) >= tau, tau in {0.5, 0.6, 0.7, 0.8, 0.9}
  nested tau     chosen on the training rows: the tau with the largest training kept-vs-skipped difference among the taus whose
                 training kept share is >= 0.20 (harness.GO kept_share_min) and which skip at least one training row; ties ->
                 the larger tau (skips less); no feasible tau -> tau 0.9 (recorded)
  grid cell      chop and tau on ALL IS rows (a trial), one ledger row per (model, tau): family regime_gate/<model>
  nested OOF     harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo), chop + tau per training
                 fold, the test-fold decisions concatenated: one ledger row per model, family regime_gate/<model>/nested
  CPCV           harness.cpcv_splits (66) with the same nested procedure -> harness.cpcv_paths (11 paths) -> harness.score_paths:
                 11 ledger rows per model, family regime_gate/<model>/nested/cpcv
  fixed rule     the (chop, tau) the same criterion picks on all IS rows = the in-sample-selected grid cell; it is what a config
                 would ship and what is replayed on the certificate null tapes
  comparator     the H2 hand rule "skip when n_choch_since_bos >= k" (family h2/choch, scope all: k = 2, 3, 4; ledger rows
                 cdd9b4281b0e451c, 6e32c51940ce5a11, 58431928cdcb8a87) at MATCHED skip fraction: the cell whose kept share is
                 closest to the nested OOF row's kept share; the scope-today cells are reported beside it
  family         every ledger row with family prefix regime_gate (grid cells, nested rows, CPCV paths, distilled rows): PBO
                 (diff and kept_mean), SPA (studentised and unstudentised), effective trials, DSR n_trials
  null tapes     the fixed rule replayed on the certificate tapes (studies/null_tapes_drift/tapes.py::tape_folders, healthy,
                 20 per generator): the frozen state models (fit window 2021-10-01..2023-09-30 of the REAL tape, exactly as
                 studies/ext_features/build_ext.py fitted them; the refit is verified against ext_features.parquet at every real
                 SETUP before any tape is touched) are run forward over each tape's bars, the rule applied at the tape's L1
                 units; tapes.null_tape_check_from_diffs on the per-tape differences; tape numbers never enter the ledger
  distillation   DecisionTreeClassifier(max_depth=3, random_state=0) on harness.design(T) (base as-of columns; the time proxies
                 sl and n_events_asof removed) predicting the fixed rule's skip decision; fidelity = out-of-fold accuracy under
                 harness.purged_splits (tree refit per fold) and in-sample accuracy, both read against the majority-class share;
                 >= 0.85 out of fold = expressible, else "not expressible compactly"; only then is the tree's OOF gate a ledger
                 row (family regime_gate/<model>/distilled)
  vocabulary     the frozen shortlist is EMPTY on both timeframes (features_shortlist/<tf>/shortlist.json, n_shortlisted 0), so
                 every column this study reads is "outside the frozen shortlist (importance rule failed for every cluster)";
                 every ledger row carries that note and any candidate would carry it in its provenance for the user to accept
                 or reject
```

IS book: 826 L1 units, mean -757.05 INR per trade, win rate 0.2772. Posteriors from `features_ext/5minute/ext_features.parquet` (forward-filtered only, truncation check PASS in `features_ext/README.md`); no new per-bar feature is built here.

## 2. The states (frozen models, fit window 2021-10-01..2023-09-30; means in original units, from `features_ext/5minute/ext_fit_report.json`)

### hmm3

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8442 | 0.4032 | -0.0966 | 2.9609 | 1.6892 | 5.3200 | -0.3381 | 0.1253 | 6.1 |
| 1 | 0.0005 | 0.9355 | 0.4520 | 0.0052 | 2.4985 | -0.0000 | 5.6533 | 0.2184 | 0.8398 | 38.3 |
| 2 | 0.0021 | 1.9707 | 0.7267 | 0.9451 | 2.4759 | 0.8472 | 4.7299 | -0.4804 | 0.0349 | 1.3 |

### hmm4

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share | dwell (bars) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.8323 | 0.3906 | -0.1223 | 2.1746 | 0.0000 | 4.7064 | 0.0780 | 0.5050 | 5.4 |
| 1 | 0.0004 | 0.8908 | 0.4405 | -0.0221 | 3.2542 | -0.0000 | 7.9522 | 0.8312 | 0.2197 | 11.2 |
| 2 | 0.0006 | 0.9645 | 0.4512 | 0.0332 | 2.9543 | 1.6566 | 5.2462 | -0.3269 | 0.1442 | 14.1 |
| 3 | 0.0014 | 1.5134 | 0.7055 | 0.6025 | 2.2343 | -0.0000 | 4.8078 | -0.4523 | 0.1311 | 1.5 |

### gmm4

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0003 | 0.8346 | 0.3960 | -0.0882 | 2.6252 | -0.0000 | 5.5686 | 2.2633 | 0.4920 |
| 1 | 0.0004 | 0.8529 | 0.4009 | -0.0935 | 3.0257 | 1.6986 | 5.1404 | -0.7201 | 0.1204 |
| 2 | 0.0008 | 1.0834 | 0.5231 | 0.1427 | 2.3393 | -0.0000 | 5.6850 | -2.2206 | 0.3565 |
| 3 | 0.0017 | 1.5902 | 0.6566 | 0.5975 | 2.5104 | 1.1618 | 5.9137 | 1.1414 | 0.0311 |

### jump4 (lambda* = 16)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0005 | 0.9346 | 0.4526 | 0.0425 | 3.7532 | 0.0954 | 7.3141 | 4.5406 | 0.1826 |
| 1 | 0.0006 | 0.9582 | 0.4513 | 0.0026 | 1.8246 | 0.0845 | 4.4973 | 0.0818 | 0.5776 |
| 2 | 0.0006 | 0.9582 | 0.4481 | 0.0667 | 3.1419 | 2.6702 | 5.1045 | -0.5804 | 0.0580 |
| 3 | 0.0007 | 1.0067 | 0.4773 | 0.0744 | 3.2195 | 0.1070 | 7.0107 | -4.1704 | 0.1818 |

### jump3 (lambda* = 32)

| state | absret | range_atr | body_frac | logvol_rel20 | ev36 | choch_since_bos | range36_atr | ret36_atr | tape share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0004 | 0.9217 | 0.4533 | 0.0100 | 3.5827 | 0.0853 | 7.8230 | 5.3266 | 0.1368 |
| 1 | 0.0006 | 0.9568 | 0.4452 | 0.0600 | 3.1285 | 2.7479 | 5.1246 | -0.6213 | 0.0527 |
| 2 | 0.0006 | 0.9703 | 0.4576 | 0.0291 | 2.3374 | 0.1064 | 5.2149 | -0.7382 | 0.8105 |

## 3. Expectancy by MAP state at the IS SETUP bars (descriptive decomposition of the raw book, no rule chosen on it; `state_tables_is.csv`)

MAP = argmax posterior at the SETUP bar (the jump state itself). `run median` = the median `hmm{K}_map_run` / `jump{K}_run` at the SETUPs in the state (how many bars the filtered state had already lasted: the confirmation lag the design asks about). All tables **outside the frozen shortlist**.

**hmm3**

| state | n | share | posterior mass share | mean L1 net | win rate | run median (bars) |  |
|---|---|---|---|---|---|---|---|
| 0 | 395 | 0.4782 | 0.4746 | -878.03 | 0.2354 | 3.0 | **chop (all IS)** |
| 1 | 211 | 0.2554 | 0.2551 | -808.89 | 0.2701 | 1.0 |  |
| 2 | 220 | 0.2663 | 0.2703 | -490.13 | 0.3591 | 1.0 |  |

**hmm4**

| state | n | share | posterior mass share | mean L1 net | win rate | run median (bars) |  |
|---|---|---|---|---|---|---|---|
| 0 | 65 | 0.0787 | 0.0783 | -557.58 | 0.2615 | 1.0 |  |
| 1 | 37 | 0.0448 | 0.0475 | -835.56 | 0.2432 | 1.0 | **chop (all IS)** |
| 2 | 591 | 0.7155 | 0.7161 | -772.80 | 0.2775 | 4.0 |  |
| 3 | 133 | 0.1610 | 0.1581 | -762.70 | 0.2932 | 1.0 |  |

**gmm4**

| state | n | share | posterior mass share | mean L1 net | win rate | run median (bars) |  |
|---|---|---|---|---|---|---|---|
| 0 | 84 | 0.1017 | 0.0983 | -510.18 | 0.2976 | - |  |
| 1 | 398 | 0.4818 | 0.4667 | -1008.06 | 0.2236 | - | **chop (all IS)** |
| 2 | 146 | 0.1768 | 0.1800 | -984.32 | 0.2534 | - |  |
| 3 | 198 | 0.2397 | 0.2550 | -189.66 | 0.3939 | - |  |

**jump4**

| state | n | share | posterior mass share | mean L1 net | win rate | run median (bars) |  |
|---|---|---|---|---|---|---|---|
| 0 | 140 | 0.1695 | 0.1695 | -293.70 | 0.2857 | 9.0 |  |
| 1 | 321 | 0.3886 | 0.3886 | -1034.07 | 0.2617 | 15.0 | **chop (all IS)** |
| 2 | 227 | 0.2748 | 0.2748 | -849.20 | 0.2555 | 7.0 |  |
| 3 | 138 | 0.1671 | 0.1671 | -431.18 | 0.3406 | 12.0 |  |

**jump3**

| state | n | share | posterior mass share | mean L1 net | win rate | run median (bars) |  |
|---|---|---|---|---|---|---|---|
| 0 | 70 | 0.0847 | 0.0847 | -545.99 | 0.3000 | 15.0 |  |
| 1 | 176 | 0.2131 | 0.2131 | -800.68 | 0.2443 | 10.0 | **chop (all IS)** |
| 2 | 580 | 0.7022 | 0.7022 | -769.29 | 0.2845 | 44.0 |  |

## 4. Grid cells: chop and tau on all IS (trials; family `regime_gate/<model>`; `grid.csv`; all rows outside the frozen shortlist)

For a jump model P(chop) is 0 or 1, so its five tau cells are one mask scored five times (the design's grid, kept as such; the effective-trial count discounts them). `fixed` marks the cell the tau rule picks on all IS (the fixed rule: what a config would ship and what was replayed on the null tapes).

| model | tau | chop | fixed | ledger id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | control pct | perm p | loser recall | loser precision | wtd winner recall | top-decile winners skipped | kept mean slip 8 | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | 0.5 | 0 |  | `37bac8efaad7a903` | 431 | 0.5218 | -646.18 | -878.03 | **231.85** | 22.42 | 6.5 | 0.4563 | 0.506 | 0.765 | 0.603 | 0.435 | -1036.14 | 7 |
| hmm3 | 0.6 | 0 |  | `e6d6b2f868d15341` | 445 | 0.5387 | -646.01 | -886.75 | **240.75** | -61.93 | 13.4 | 0.4348 | 0.489 | 0.766 | 0.627 | 0.391 | -1035.97 | 7 |
| hmm3 | 0.7 | 0 | **yes** | `78d1b8d699d3f11b` | 452 | 0.5472 | -638.30 | -900.57 | **262.27** | -33.60 | 12.7 | 0.4038 | 0.482 | 0.770 | 0.639 | 0.391 | -1028.27 | 7 |
| hmm3 | 0.8 | 0 |  | `dfcebb737e83c4c9` | 460 | 0.5569 | -644.31 | -898.75 | **254.44** | -34.12 | 11.4 | 0.4323 | 0.474 | 0.773 | 0.647 | 0.391 | -1034.27 | 7 |
| hmm3 | 0.9 | 0 |  | `7b81cc446973d21d` | 476 | 0.5763 | -683.61 | -856.94 | **173.33** | -101.67 | 7.1 | 0.5822 | 0.456 | 0.777 | 0.659 | 0.391 | -1073.57 | 6 |
| hmm4 | 0.5 | 1 |  | `d0233944f31dba83` | 790 | 0.9564 | -746.81 | -981.84 | **235.04** | 8.49 | 44.4 | 0.7531 | 0.047 | 0.778 | 0.966 | 0.000 | -1136.77 | 5 |
| hmm4 | 0.6 | 1 |  | `df871eff3b636a9c` | 795 | 0.9625 | -744.79 | -1071.61 | **326.82** | 101.74 | 57.0 | 0.6922 | 0.042 | 0.806 | 0.973 | 0.000 | -1134.75 | 5 |
| hmm4 | 0.7 | 1 |  | `5fdb6e5327a4311d` | 796 | 0.9637 | -744.56 | -1088.57 | **344.02** | 119.22 | 53.4 | 0.6862 | 0.040 | 0.800 | 0.973 | 0.000 | -1134.52 | 5 |
| hmm4 | 0.8 | 1 |  | `be15bfb43744b2a9` | 797 | 0.9649 | -738.77 | -1259.43 | **520.65** | 296.21 | 63.3 | 0.5497 | 0.040 | 0.828 | 0.977 | 0.000 | -1128.74 | 6 |
| hmm4 | 0.9 | 1 | **yes** | `3428d4310a05f59b` | 804 | 0.9734 | -727.00 | -1855.17 | **1128.16** | 905.83 | 77.5 | 0.2444 | 0.034 | 0.909 | 0.992 | 0.000 | -1116.97 | 8 |
| gmm4 | 0.5 | 1 | **yes** | `8983638faf6671d2` | 428 | 0.5182 | -523.64 | -1008.06 | **484.42** | 173.87 | 1.6 | 0.1269 | 0.518 | 0.776 | 0.633 | 0.391 | -913.61 | 10 |
| gmm4 | 0.6 | 1 |  | `8c01b08a82717fd2` | 443 | 0.5363 | -600.66 | -937.95 | **337.29** | 39.91 | 1.1 | 0.2944 | 0.496 | 0.773 | 0.635 | 0.391 | -990.62 | 8 |
| gmm4 | 0.7 | 1 |  | `e23aefb0f61d708b` | 461 | 0.5581 | -623.31 | -925.97 | **302.67** | 21.76 | 0.5 | 0.3353 | 0.472 | 0.773 | 0.655 | 0.391 | -1013.27 | 8 |
| gmm4 | 0.8 | 1 |  | `ce38ee11d026461b` | 490 | 0.5932 | -647.88 | -916.26 | **268.38** | -97.62 | 1.2 | 0.3878 | 0.435 | 0.774 | 0.686 | 0.348 | -1037.85 | 8 |
| gmm4 | 0.9 | 1 |  | `99cc849ba31c97bd` | 524 | 0.6344 | -714.56 | -830.78 | **116.22** | -226.77 | 3.4 | 0.7181 | 0.390 | 0.771 | 0.704 | 0.304 | -1104.52 | 7 |
| jump4 | 0.5 | 1 |  | `eae12cb14cca03b5` | 505 | 0.6114 | -580.97 | -1034.07 | **453.10** | 614.62 | 100.0 | 0.1524 | 0.397 | 0.738 | 0.622 | 0.435 | -970.93 | 7 |
| jump4 | 0.6 | 1 |  | `01c028a37ffc2d62` | 505 | 0.6114 | -580.97 | -1034.07 | **453.10** | 614.62 | 100.0 | 0.1584 | 0.397 | 0.738 | 0.622 | 0.435 | -970.93 | 7 |
| jump4 | 0.7 | 1 |  | `d74e83507b736d1f` | 505 | 0.6114 | -580.97 | -1034.07 | **453.10** | 614.62 | 100.0 | 0.1614 | 0.397 | 0.738 | 0.622 | 0.435 | -970.93 | 7 |
| jump4 | 0.8 | 1 |  | `b341f754fa37699c` | 505 | 0.6114 | -580.97 | -1034.07 | **453.10** | 614.62 | 100.0 | 0.1614 | 0.397 | 0.738 | 0.622 | 0.435 | -970.93 | 7 |
| jump4 | 0.9 | 1 | **yes** | `054bded46d11afe9` | 505 | 0.6114 | -580.97 | -1034.07 | **453.10** | 614.62 | 100.0 | 0.1619 | 0.397 | 0.738 | 0.622 | 0.435 | -970.93 | 7 |
| jump3 | 0.5 | 1 |  | `246ab9c4256e15f5` | 650 | 0.7869 | -745.24 | -800.68 | **55.44** | -72.03 | 24.4 | 0.8861 | 0.223 | 0.756 | 0.811 | 0.174 | -1135.20 | 7 |
| jump3 | 0.6 | 1 |  | `b3d51cf675b59b49` | 650 | 0.7869 | -745.24 | -800.68 | **55.44** | -72.03 | 23.4 | 0.8861 | 0.223 | 0.756 | 0.811 | 0.174 | -1135.20 | 7 |
| jump3 | 0.7 | 1 |  | `4146bc5fb78bb6dd` | 650 | 0.7869 | -745.24 | -800.68 | **55.44** | -72.03 | 22.2 | 0.8806 | 0.223 | 0.756 | 0.811 | 0.174 | -1135.20 | 7 |
| jump3 | 0.8 | 1 |  | `3980c2ad34d9a6ff` | 650 | 0.7869 | -745.24 | -800.68 | **55.44** | -72.03 | 21.8 | 0.8761 | 0.223 | 0.756 | 0.811 | 0.174 | -1135.20 | 7 |
| jump3 | 0.9 | 1 | **yes** | `0f3bf882433e2ef3` | 650 | 0.7869 | -745.24 | -800.68 | **55.44** | -72.03 | 21.9 | 0.8746 | 0.223 | 0.756 | 0.811 | 0.174 | -1135.20 | 7 |

## 5. Nested pick (12 purged folds; chop and tau chosen on the training rows; one OOF ledger row per model, family `regime_gate/<model>/nested`; `nested_folds.csv`; all rows outside the frozen shortlist)

### hmm3: OOF row `f04d658f0f2cd264`

| fold | n train | n test | chop | tau | feasible tau | chop train n | chop train mean | test skipped | test kept share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 1 | 0.5 | yes | 187 | -841.16 | 24 | 0.7073 |
| 1 | 741 | 83 | 0 | 0.5 | yes | 362 | -981.07 | 32 | 0.6145 |
| 2 | 784 | 42 | 0 | 0.8 | yes | 377 | -906.96 | 15 | 0.6429 |
| 3 | 742 | 76 | 0 | 0.8 | yes | 346 | -847.64 | 42 | 0.4474 |
| 4 | 754 | 72 | 0 | 0.7 | yes | 357 | -862.41 | 38 | 0.4722 |
| 5 | 747 | 73 | 0 | 0.8 | yes | 351 | -847.84 | 36 | 0.5068 |
| 6 | 745 | 77 | 0 | 0.7 | yes | 354 | -897.67 | 39 | 0.4935 |
| 7 | 775 | 51 | 1 | 0.5 | yes | 196 | -894.04 | 15 | 0.7059 |
| 8 | 747 | 76 | 0 | 0.7 | yes | 363 | -890.74 | 30 | 0.6053 |
| 9 | 746 | 80 | 1 | 0.5 | yes | 188 | -926.63 | 23 | 0.7125 |
| 10 | 794 | 31 | 0 | 0.7 | yes | 376 | -836.06 | 17 | 0.4516 |
| 11 | 743 | 83 | 0 | 0.8 | yes | 355 | -1003.89 | 36 | 0.5663 |

OOF: kept 479 (0.5799), kept mean -970.92, skipped mean -461.83, **diff -509.09**, diff top-1% removed -466.20, control pct 0.9, perm p 0.1000, loser recall 0.425, loser precision 0.732, |net|-weighted winner recall 0.589, top-decile winners skipped 0.478, kept mean at 8 pts slippage -1360.88, sign blocks 4/12, kept PF 0.584. Per-block kept-vs-skipped diff (decomposition of this row): b0 116.73, b1 -1073.82, b2 -855.47, b3 160.83, b4 247.56, b5 -391.41, b6 -628.50, b7 -1830.01, b8 -271.90, b9 -2015.53, b10 821.85, b11 -887.22.

### hmm4: OOF row `0af965c7aa190f00`

| fold | n train | n test | chop | tau | feasible tau | chop train n | chop train mean | test skipped | test kept share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 3 | 0.9 | yes | 115 | -979.93 | 12 | 0.8537 |
| 1 | 741 | 83 | 2 | 0.9 | yes | 529 | -844.46 | 61 | 0.2651 |
| 2 | 784 | 42 | 2 | 0.9 | yes | 561 | -820.35 | 30 | 0.2857 |
| 3 | 742 | 76 | 1 | 0.9 | yes | 36 | -1006.24 | 0 | 1.0000 |
| 4 | 754 | 72 | 1 | 0.9 | yes | 34 | -831.53 | 1 | 0.9861 |
| 5 | 747 | 73 | 1 | 0.9 | yes | 33 | -989.42 | 2 | 0.9726 |
| 6 | 745 | 77 | 2 | 0.9 | yes | 534 | -827.97 | 57 | 0.2597 |
| 7 | 775 | 51 | 3 | 0.9 | yes | 125 | -965.58 | 7 | 0.8627 |
| 8 | 747 | 76 | 1 | 0.9 | yes | 33 | -913.74 | 2 | 0.9737 |
| 9 | 746 | 80 | 1 | 0.9 | yes | 32 | -1003.79 | 4 | 0.9500 |
| 10 | 794 | 31 | 1 | 0.9 | yes | 37 | -835.56 | 0 | 1.0000 |
| 11 | 743 | 83 | 2 | 0.9 | yes | 536 | -841.41 | 55 | 0.3373 |

OOF: kept 595 (0.7203), kept mean -1011.66, skipped mean -101.25, **diff -910.40**, diff top-1% removed -836.37, control pct 6.7, perm p 0.0090, loser recall 0.255, loser precision 0.658, |net|-weighted winner recall 0.641, top-decile winners skipped 0.478, kept mean at 8 pts slippage -1401.62, sign blocks 3/12, kept PF 0.541. Per-block kept-vs-skipped diff (decomposition of this row): b0 -824.52, b1 -740.08, b2 -1174.00, b3 -, b4 1285.62, b5 220.88, b6 -2623.73, b7 -3212.02, b8 2512.56, b9 -501.27, b10 -, b11 -475.06.

### gmm4: OOF row `760b31266f2a2979`

| fold | n train | n test | chop | tau | feasible tau | chop train n | chop train mean | test skipped | test kept share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 2 | 0.9 | yes | 127 | -984.55 | 18 | 0.7805 |
| 1 | 741 | 83 | 2 | 0.9 | yes | 130 | -1139.98 | 12 | 0.8554 |
| 2 | 784 | 42 | 1 | 0.5 | yes | 382 | -1035.68 | 16 | 0.6190 |
| 3 | 742 | 76 | 2 | 0.9 | yes | 130 | -1076.67 | 12 | 0.8421 |
| 4 | 754 | 72 | 1 | 0.5 | yes | 359 | -987.56 | 39 | 0.4583 |
| 5 | 747 | 73 | 1 | 0.5 | yes | 352 | -956.96 | 42 | 0.4247 |
| 6 | 745 | 77 | 1 | 0.5 | yes | 355 | -1081.82 | 43 | 0.4416 |
| 7 | 775 | 51 | 2 | 0.9 | yes | 136 | -1161.90 | 8 | 0.8431 |
| 8 | 747 | 76 | 1 | 0.5 | yes | 363 | -1044.79 | 35 | 0.5395 |
| 9 | 746 | 80 | 2 | 0.9 | yes | 132 | -938.84 | 13 | 0.8375 |
| 10 | 794 | 31 | 2 | 0.9 | yes | 143 | -966.76 | 3 | 0.9032 |
| 11 | 743 | 83 | 2 | 0.8 | yes | 132 | -1110.82 | 11 | 0.8675 |

OOF: kept 574 (0.6949), kept mean -790.28, skipped mean -681.37, **diff -108.90**, diff top-1% removed -176.96, control pct 11.2, perm p 0.7431, loser recall 0.317, loser precision 0.750, |net|-weighted winner recall 0.716, top-decile winners skipped 0.348, kept mean at 8 pts slippage -1180.24, sign blocks 7/12, kept PF 0.636. Per-block kept-vs-skipped diff (decomposition of this row): b0 1074.81, b1 -840.12, b2 209.19, b3 -562.90, b4 630.20, b5 376.07, b6 -1219.37, b7 -3816.46, b8 18.76, b9 91.79, b10 535.23, b11 -938.79.

### jump4: OOF row `9d7f9977cc402b7a`

| fold | n train | n test | chop | tau | feasible tau | chop train n | chop train mean | test skipped | test kept share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 1 | 0.9 | yes | 291 | -1122.54 | 30 | 0.6341 |
| 1 | 741 | 83 | 1 | 0.9 | yes | 288 | -975.06 | 33 | 0.6024 |
| 2 | 784 | 42 | 1 | 0.9 | yes | 304 | -1030.83 | 17 | 0.5952 |
| 3 | 742 | 76 | 1 | 0.9 | yes | 284 | -1073.32 | 34 | 0.5526 |
| 4 | 754 | 72 | 1 | 0.9 | yes | 294 | -1061.99 | 27 | 0.6250 |
| 5 | 747 | 73 | 1 | 0.9 | yes | 288 | -995.09 | 31 | 0.5753 |
| 6 | 745 | 77 | 1 | 0.9 | yes | 296 | -1062.55 | 22 | 0.7143 |
| 7 | 775 | 51 | 1 | 0.9 | yes | 299 | -1136.53 | 22 | 0.5686 |
| 8 | 747 | 76 | 1 | 0.9 | yes | 294 | -901.48 | 25 | 0.6711 |
| 9 | 746 | 80 | 1 | 0.9 | yes | 291 | -925.83 | 30 | 0.6250 |
| 10 | 794 | 31 | 1 | 0.9 | yes | 305 | -1007.45 | 15 | 0.5161 |
| 11 | 743 | 83 | 1 | 0.9 | yes | 286 | -1166.65 | 35 | 0.5783 |

OOF: kept 505 (0.6114), kept mean -580.97, skipped mean -1034.07, **diff 453.10**, diff top-1% removed 614.62, control pct 100.0, perm p 0.1554, loser recall 0.397, loser precision 0.738, |net|-weighted winner recall 0.622, top-decile winners skipped 0.435, kept mean at 8 pts slippage -970.93, sign blocks 7/12, kept PF 0.702. Per-block kept-vs-skipped diff (decomposition of this row): b0 -471.46, b1 2045.67, b2 1466.31, b3 -324.58, b4 -284.45, b5 150.40, b6 1274.07, b7 -2368.00, b8 2452.31, b9 1282.42, b10 699.94, b11 -542.66.

### jump3: OOF row `16d86a30133971e4`

| fold | n train | n test | chop | tau | feasible tau | chop train n | chop train mean | test skipped | test kept share |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 2 | 0.9 | yes | 520 | -840.05 | 58 | 0.2927 |
| 1 | 741 | 83 | 1 | 0.9 | yes | 161 | -967.72 | 15 | 0.8193 |
| 2 | 784 | 42 | 2 | 0.9 | yes | 550 | -830.41 | 30 | 0.2857 |
| 3 | 742 | 76 | 1 | 0.9 | yes | 157 | -827.10 | 18 | 0.7632 |
| 4 | 754 | 72 | 1 | 0.9 | yes | 163 | -800.07 | 13 | 0.8194 |
| 5 | 747 | 73 | 1 | 0.9 | yes | 154 | -740.94 | 21 | 0.7123 |
| 6 | 745 | 77 | 1 | 0.9 | yes | 155 | -861.78 | 21 | 0.7273 |
| 7 | 775 | 51 | 1 | 0.9 | yes | 168 | -778.02 | 8 | 0.8431 |
| 8 | 747 | 76 | 0 | 0.9 | yes | 65 | -836.60 | 5 | 0.9342 |
| 9 | 746 | 80 | 1 | 0.9 | yes | 155 | -767.41 | 21 | 0.7375 |
| 10 | 794 | 31 | 2 | 0.9 | yes | 557 | -758.46 | 22 | 0.2903 |
| 11 | 743 | 83 | 2 | 0.9 | yes | 520 | -864.34 | 60 | 0.2771 |

OOF: kept 534 (0.6465), kept mean -1015.67, skipped mean -284.10, **diff -731.58**, diff top-1% removed -770.83, control pct 0.4, perm p 0.0275, loser recall 0.325, loser precision 0.664, |net|-weighted winner recall 0.603, top-decile winners skipped 0.348, kept mean at 8 pts slippage -1405.64, sign blocks 2/12, kept PF 0.552. Per-block kept-vs-skipped diff (decomposition of this row): b0 -660.40, b1 -1597.68, b2 -1996.70, b3 -242.13, b4 -121.50, b5 7.25, b6 -808.23, b7 341.99, b8 -4119.99, b9 -320.40, b10 -764.46, b11 -1151.08.

## 6. CPCV of the nested procedure (66 splits, 11 paths; family `regime_gate/<model>/nested/cpcv`; `cpcv_paths.csv`; all rows outside the frozen shortlist)

| model | paths | diff median | diff p5 | diff min | share of paths diff > 0 | kept share median | control pct median | control pct p5 | distinct (chop, tau) picks over the 66 splits |
|---|---|---|---|---|---|---|---|---|---|
| hmm3 | 11 | -482.50 | **-703.28** | -751.58 | 0.000 | 0.5860 | 1.3 | 0.5 | chop 0 tau 0.5; chop 0 tau 0.6; chop 0 tau 0.7; chop 0 tau 0.8; chop 1 tau 0.5; chop 1 tau 0.6; chop 2 tau 0.5 |
| hmm4 | 11 | -559.62 | **-883.41** | -885.20 | 0.000 | 0.7264 | 9.9 | 1.8 | chop 0 tau 0.5; chop 1 tau 0.9; chop 2 tau 0.9; chop 3 tau 0.9 |
| gmm4 | 11 | -130.68 | **-298.33** | -369.26 | 0.182 | 0.6913 | 10.2 | 1.1 | chop 0 tau 0.8; chop 1 tau 0.5; chop 2 tau 0.8; chop 2 tau 0.9 |
| jump4 | 11 | 203.49 | **-351.99** | -543.70 | 0.545 | 0.6259 | 100.0 | 95.6 | chop 1 tau 0.9; chop 2 tau 0.9 |
| jump3 | 11 | -615.15 | **-689.87** | -717.92 | 0.000 | 0.6356 | 2.0 | 0.4 | chop 0 tau 0.9; chop 1 tau 0.9; chop 2 tau 0.9 |

## 7. The H2 hand rule at matched skip fraction (family `h2/choch`, `studies/h2_h3_h4/h2_5minute_L1_grid.csv`)

Matched cell = the `n_choch_since_bos >= k` cell (scope all; k = 2, 3, 4) whose kept share is closest to the model's nested OOF kept share; the scope-today cell (`n_choch_since_bos_today >= k`) beside it. `beats` = the nested OOF diff is above the matched cell's diff (the design's bar: the state model must beat the hand rule at the same trade count or it is not worth its parameters).

| model | nested kept share | nested diff | H2 k (all) | H2 id | H2 kept share | H2 diff | H2 control pct | H2 perm p | H2 sign blocks | beats (all) | H2 k (today) | kept share | diff | beats (today) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | 0.5799 | -509.09 | 2 | `cdd9b4281b0e451c` | 0.6864 | 257.83 | 45.9 | 0.4613 | 6 | **no** | 2 | 0.7312 | 630.08 | no |
| hmm4 | 0.7203 | -910.40 | 2 | `cdd9b4281b0e451c` | 0.6864 | 257.83 | 45.9 | 0.4613 | 6 | **no** | 2 | 0.7312 | 630.08 | no |
| gmm4 | 0.6949 | -108.90 | 2 | `cdd9b4281b0e451c` | 0.6864 | 257.83 | 45.9 | 0.4613 | 6 | **no** | 2 | 0.7312 | 630.08 | no |
| jump4 | 0.6114 | 453.10 | 2 | `cdd9b4281b0e451c` | 0.6864 | 257.83 | 45.9 | 0.4613 | 6 | **yes** | 2 | 0.7312 | 630.08 | no |
| jump3 | 0.6465 | -731.58 | 2 | `cdd9b4281b0e451c` | 0.6864 | 257.83 | 45.9 | 0.4613 | 6 | **no** | 2 | 0.7312 | 630.08 | no |

The importance study's SFI gate on cluster 25 (`4535288bcf0f1148`: a 300-tree bagging on `jump3_state` + `jump3_run` at its OOB tau) kept 717 (0.868), diff 827.00, top-1%-removed 578.35, control 100.0, perm p 0.0780, 8/12 blocks, kept mean at 8 pts slippage -1037.88. The jump3 chop-state gate here (fixed rule: skip state 1) kept 650 with diff 55.44; nested OOF diff -731.58, CPCV p5 -689.87: section 12 says what that means for the SPA-best row.

## 7b. Where the chop states sit in the session (label-free diagnostic; `diagnostics.py`; explains the within-session statistics)

The session-matched control percentile and the SPA selection gain are within-session contrasts (kept mean minus the session's mean, per session). session_stop FINDINGS R.3 showed that on this book a rule that keeps a session's LATER units beats that control by construction (the last unit of a session is a long winner by construction of the SETUP sequence: a winner holds to the cut and no SETUP follows it). This table asks whether a chop state is such a rule. `chop share` = share of IS SETUPs whose MAP state is the fixed rule's chop state, by hour bin and by rank in the session (`today_n_setups_before`); the 'last unit' column uses post-SETUP information (the session's later SETUPs) and is a description of the control's mechanics, never a feature.

| model | chop | share all | share <09:25 | share 09 | share 10 | share 11 | share 12 | share 13 | share 14 | share 15 | share >=15:20 | share rank 0 | share rank 1 | share rank 2 | share rank 3 | share last unit | share not last | mean session bar (chop) | mean session bar (other) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | 0 | 0.478 | 0.240 | 0.417 | 0.512 | 0.560 | 0.579 | 0.430 | 0.470 | 0.467 | 0.800 | 0.414 | 0.555 | 0.516 | 0.542 | 0.444 | 0.512 | 35.9 | 34.1 |
| hmm4 | 1 | 0.045 | 0.000 | 0.000 | 0.008 | 0.070 | 0.087 | 0.074 | 0.045 | 0.022 | 0.000 | 0.044 | 0.042 | 0.065 | 0.021 | 0.039 | 0.050 | 44.8 | 34.5 |
| gmm4 | 1 | 0.482 | 0.260 | 0.427 | 0.512 | 0.600 | 0.516 | 0.436 | 0.500 | 0.444 | 1.000 | 0.404 | 0.542 | 0.540 | 0.625 | 0.451 | 0.512 | 36.0 | 34.0 |
| jump4 | 1 | 0.389 | 0.520 | 0.792 | 0.683 | 0.470 | 0.175 | 0.208 | 0.159 | 0.311 | 0.000 | 0.583 | 0.288 | 0.105 | 0.042 | 0.338 | 0.438 | 22.9 | 42.6 |
| jump3 | 1 | 0.213 | 0.220 | 0.156 | 0.179 | 0.230 | 0.254 | 0.208 | 0.212 | 0.289 | 0.200 | 0.167 | 0.225 | 0.290 | 0.312 | 0.184 | 0.242 | 36.8 | 34.5 |

Reading: the jump4 chop state (state 1, the quiet state: `ev36` 1.8, `range36_atr` 4.5) is a morning / first-SETUP state: 0.79 of the 09 bin's SETUPs and 0.68 of the 10 bin's are in it against 0.16-0.21 in the 12, 13 and 14 bins; 0.58 of a session's first SETUPs against 0.10 of its third; mean session bar 22.9 vs 42.6. 'Skip the quiet state' is therefore largely 'skip the session's first, early SETUP and keep the later ones': the rule shape that inflates the session-matched control and the SPA gain by construction, which is why jump4 reads control 100 / SPA p 0.0015 while its between-session checks (blocks 7/12, CPCV p5 -351.99, bootstrap CI [-47.92, 931.56], session-tape same sign 0.35) fail. The hmm3 / gmm4 / jump3 chop states (the CHoCH-count states) are spread over the day and the ranks and their gates sit at control percentiles 0-13 with positive pooled diffs: the between-session composition effect the H2 study already reported for `n_choch_since_bos`.

## 8. The family (every `regime_gate` ledger row) and the per-row statistics

| family | rows | PBO (diff) | IS-best below 0 OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session | SPA best row | SPA p (unstudentised) | excluded (min active) | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all regime_gate rows | 89 | 0.3194 | 0.3960 | 0.1768 | 0.0015 | 0.0020 | 358.93 | regime_gate/jump4 {"model": "jump4", "tau": 0.5} | 0.0000 | 2 | 1.80 |
| grid + nested + distilled (no CPCV paths) | 34 | 0.3751 | 0.3160 | 0.3099 | 0.0000 | 0.0000 | 358.93 | regime_gate/jump4 {"model": "jump4", "tau": 0.5} | 0.0000 | 2 | 1.59 |

Families: `regime_gate/gmm4`, `regime_gate/gmm4/distilled`, `regime_gate/gmm4/nested`, `regime_gate/gmm4/nested/cpcv`, `regime_gate/hmm3`, `regime_gate/hmm3/distilled`, `regime_gate/hmm3/nested`, `regime_gate/hmm3/nested/cpcv`, `regime_gate/hmm4`, `regime_gate/hmm4/distilled`, `regime_gate/hmm4/nested`, `regime_gate/hmm4/nested/cpcv`, `regime_gate/jump3`, `regime_gate/jump3/distilled`, `regime_gate/jump3/nested`, `regime_gate/jump3/nested/cpcv`, `regime_gate/jump4`, `regime_gate/jump4/nested`, `regime_gate/jump4/nested/cpcv`. The go/no-go items below use the all-rows family (the more inclusive count: PBO 0.3194, SPA p 0.0015); DSR uses n_trials = 89 and the variance of the per-session Sharpe across the family's rows (0.00182).

| model | row | ledger id | bootstrap 90% CI of diff | P(diff <= 0) | kept mean CI | SR per session | SR0 (expected max) | DSR p | active sessions |
|---|---|---|---|---|---|---|---|---|---|
| hmm3 | nested | `f04d658f0f2cd264` | [-1007.46, -7.24] | 0.9545 | [-1307.13, -610.60] | -0.1031 | 0.1062 | 0.9997 | 311 |
| hmm3 | fixed | `78d1b8d699d3f11b` | [-294.75, 807.77] | 0.2255 | [-1049.24, -258.74] | -0.0285 | 0.1062 | 0.9901 | 313 |
| hmm4 | nested | `0af965c7aa190f00` | [-1426.06, -362.50] | 0.9985 | [-1283.47, -742.21] | -0.0963 | 0.1062 | 0.9997 | 328 |
| hmm4 | fixed | `3428d4310a05f59b` | [371.67, 1915.52] | 0.0130 | [-966.62, -462.34] | 0.0280 | 0.1062 | 0.9451 | 403 |
| gmm4 | nested | `760b31266f2a2979` | [-657.61, 405.70] | 0.6510 | [-1117.40, -476.73] | -0.0431 | 0.1062 | 0.9962 | 338 |
| gmm4 | fixed | `8983638faf6671d2` | [-86.46, 1091.67] | 0.0835 | [-938.87, -93.57] | -0.0129 | 0.1062 | 0.9794 | 300 |
| jump4 | nested | `9d7f9977cc402b7a` | [-47.92, 931.56] | 0.0655 | [-869.30, -265.89] | -0.0007 | 0.1062 | 0.9653 | 290 |
| jump4 | fixed | `054bded46d11afe9` | [-65.46, 960.97] | 0.0760 | [-896.94, -262.81] | -0.0007 | 0.1062 | 0.9653 | 290 |
| jump3 | nested | `16d86a30133971e4` | [-1106.23, -360.51] | 0.9980 | [-1295.43, -744.92] | -0.0961 | 0.1062 | 0.9995 | 308 |
| jump3 | fixed | `0f3bf882433e2ef3` | [-449.10, 541.42] | 0.4315 | [-996.73, -484.51] | -0.0227 | 0.1062 | 0.9928 | 374 |

## 9. Null tapes: the fixed rule replayed on the certificate tapes (`tape_diffs.csv`; tape numbers never enter the ledger)

The frozen state models were refitted exactly as `studies/ext_features/build_ext.py` fitted them (same fit window, seeds and library calls) and verified against `ext_features.parquet` at every real SETUP before any tape was touched: hmm3 max |posterior diff| 6.7e-09, MAP identical yes; hmm4 max |posterior diff| 1.6e-09, MAP identical yes; gmm4 max |posterior diff| 0.0e+00, MAP identical yes; jump4 max |posterior diff| 0.0e+00, MAP identical yes; jump3 max |posterior diff| 0.0e+00, MAP identical yes. Each tape's bars were then z-scored with the real fit window's statistics and run forward through the frozen models; the fixed rule (chop*, tau*) was applied at the tape's L1 units and scored with `harness.metrics` (controls off, as `tapes.null_tape_check` does). Pass rule (FINDINGS null_tapes_drift section 7): real diff > GMM-Markov p95 AND > segment p95 AND the session tapes carry the real sign in >= 75%.

| model | fixed rule | real diff (fixed cell) | tapes / gen | gmm p50 | gmm p95 | real pct (gmm) | segment p50 | segment p95 | real pct (segment) | session p50 | session p95 | session same-sign share | pass (fixed) | nested OOF diff | pass (nested diff vs the same tapes) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | chop 0 tau 0.7 | 262.27 | 20 | -65.78 | 291.92 | 90.0 | 25.60 | 437.59 | 85.0 | 442.61 | 803.33 | 0.850 | **no** | -509.09 | no |
| hmm4 | chop 1 tau 0.9 | 1128.16 | 20 | 93.52 | 1001.22 | 100.0 | 189.69 | 1117.09 | 95.0 | 582.25 | 1496.30 | 0.750 | **yes** | -910.40 | no |
| gmm4 | chop 1 tau 0.5 | 484.42 | 20 | 1.30 | 282.19 | 100.0 | 17.21 | 353.91 | 95.0 | 408.26 | 852.91 | 0.850 | **yes** | -108.90 | no |
| jump4 | chop 1 tau 0.9 | 453.10 | 20 | 105.84 | 389.70 | 100.0 | 13.52 | 431.20 | 95.0 | -76.96 | 465.64 | 0.350 | **no** | 453.10 | no |
| jump3 | chop 1 tau 0.9 | 55.44 | 20 | 23.43 | 591.83 | 55.0 | -41.33 | 614.21 | 65.0 | 161.07 | 621.86 | 0.800 | **no** | -731.58 | no |

## 10. Distillation: a depth-3 tree on the base as-of features predicting the fixed rule's skip decision (`results.json` -> `distillation`)

Features: `harness.design(T)` (234 columns) without the time proxies ['n_events_asof', 'sl']; the extended columns are not in the tree (the question is whether the state is expressible in the base vocabulary). Fidelity = out-of-fold accuracy under `harness.purged_splits` (tree refit per fold) against the fixed rule's decision; read against the majority-class share (a skip share of 5% gives a 95% baseline to a tree that never skips). Rule >= 0.85 out of fold = expressible; only then is the tree's own OOF gate a ledger row (family `regime_gate/<model>/distilled`).

| model | target (fixed rule) | skip share | majority baseline | fidelity OOF | balanced acc OOF | skip recall OOF | skip precision OOF | fidelity in-sample | expressible (>= 0.85 OOF) | features the full-IS tree splits on | rule-list agreement with the tree | distilled OOF gate (ledger) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | chop 0 tau 0.7 | 0.4528 | 0.5472 | **0.9140** | 0.9150 | 0.925 | 0.889 | 0.9322 | **yes** | `bar_range_atr`, `bars_since_choch`, `dist_prot_dir_atr`, `move_since_choch_pts`, `n_choch_since_bos_today` | 1.0000 | `56df6406dda24d86` kept 437 diff 300.36 ctrl 8.1 |
| hmm4 | chop 1 tau 0.9 | 0.0266 | 0.9734 | **0.9625** | 0.5386 | 0.091 | 0.154 | 0.9818 | **yes** | `bar_body_pts`, `n_choch_since_bos`, `range_3h_atr` | 1.0000 | `d381c2c0921ed6cf` kept 813 diff -12.13 ctrl 22.1 |
| gmm4 | chop 1 tau 0.5 | 0.4818 | 0.5182 | **0.8692** | 0.8706 | 0.907 | 0.836 | 0.9031 | **yes** | `bar_range_atr`, `bar_range_pts`, `bars_since_choch`, `fz_dist_band_edge_behind`, `last_sl_bars_ago`, `n_choch_since_bos_today` | 1.0000 | `18d0cf5ba5b1f542` kept 394 diff 12.85 ctrl 6.2 |
| jump4 | chop 1 tau 0.9 | 0.3886 | 0.6114 | **0.8196** | 0.8042 | 0.735 | 0.787 | 0.8511 | no: not expressible compactly | `choch_run`, `gap_pts`, `n_choch_today`, `range_3h_atr`, `room_behind_dist_atr`, `sess_range_atr`, `vol_ratio60` | 1.0000 | - |
| jump3 | chop 1 tau 0.9 | 0.2131 | 0.7869 | **0.9031** | 0.8452 | 0.744 | 0.789 | 0.9298 | **yes** | `alt_dir6`, `bars_since_bos`, `n_flip_since_bos`, `room_edge_dist_dir_atr` | 1.0000 | `b4642aef127b8d07` kept 660 diff -657.35 ctrl 13.4 |

The full-IS trees' skip leaves as rule lists (the shippable form when expressible; NaN routing is not representable in the grammar, hence the agreement column):

- **hmm3**: IF `n_choch_since_bos_today` <= 0.5 AND `bars_since_choch` <= 1.5 -> skip (leaf n 1); IF `n_choch_since_bos_today` > 0.5 AND `bar_range_atr` <= 1.37135 AND `move_since_choch_pts` <= 22.2 -> skip (leaf n 357); IF `n_choch_since_bos_today` > 0.5 AND `bar_range_atr` > 1.37135 AND `dist_prot_dir_atr` <= 1.9269 -> skip (leaf n 8)
- **hmm4**: IF `range_3h_atr` > 6.264 AND `n_choch_since_bos` <= 0.5 AND `bar_body_pts` > -12.5 -> skip (leaf n 37)
- **gmm4**: IF `n_choch_since_bos_today` <= 0.5 AND `last_sl_bars_ago` <= 16.5 AND `bars_since_choch` <= 1.5 -> skip (leaf n 1); IF `n_choch_since_bos_today` <= 0.5 AND `last_sl_bars_ago` > 16.5 -> skip (leaf n 1); IF `n_choch_since_bos_today` > 0.5 AND `bar_range_pts` <= 37.9 AND `bar_range_atr` <= 1.6017 -> skip (leaf n 436)
- **jump4**: IF `n_choch_today` <= 2.5 AND `sess_range_atr` <= 6.9475 AND `choch_run` <= 1.5 -> skip (leaf n 258); IF `n_choch_today` > 2.5 AND `range_3h_atr` <= 3.69355 AND `room_behind_dist_atr` > 0.43745 -> skip (leaf n 6)
- **jump3**: IF `n_flip_since_bos` <= 2.5 AND `alt_dir6` <= 2.5 AND `bars_since_bos` > 65.0 -> skip (leaf n 1); IF `n_flip_since_bos` <= 2.5 AND `alt_dir6` > 2.5 AND `bars_since_bos` <= 1.5 -> skip (leaf n 86); IF `n_flip_since_bos` > 2.5 AND `room_edge_dist_dir_atr` <= 0.7908 -> skip (leaf n 115)

## 11. `harness.go_no_go` per model (nested OOF row = the decision; the fixed rule's own row beside it)

**hmm3** — nested passed **no**, fixed passed no, beats the matched H2 rule (scope all) no, candidate **no**

| check | nested | value | fixed | value |
|---|---|---|---|---|
| kept_share>=20% | ok | 0.5799 | ok | 0.5472 |
| kept_n>=80 | ok | 479 | ok | 452 |
| diff>0 | **FAIL** | -509.0900 | ok | 262.2700 |
| diff_top1_removed>0 | **FAIL** | -466.2000 | **FAIL** | -33.6000 |
| kept_mean_slip8>0 | **FAIL** | -1360.8800 | **FAIL** | -1028.2700 |
| sign_blocks>=8/12 | **FAIL** | 4 | **FAIL** | 7 |
| control_pct>=95 | **FAIL** | 0.9000 | **FAIL** | 12.7000 |
| cpcv_p5_diff>0 | **FAIL** | -703.2800 | **FAIL** | -703.2800 |
| pbo<=0.2 | **FAIL** | 0.3194 | **FAIL** | 0.3194 |
| dsr_p<0.1 | **FAIL** | 0.9997 | **FAIL** | 0.9901 |
| spa_p<=0.10 | ok | 0.0015 | ok | 0.0015 |
| boot_ci_excludes_0 | **FAIL** | [-1007.46, -7.24] | **FAIL** | [-294.75, 807.77] |
| null_tape:real_diff>gmm_p95 | **FAIL** | 291.9200 | **FAIL** | 291.9200 |
| null_tape:real_diff>segment_p95 | **FAIL** | 437.5900 | **FAIL** | 437.5900 |
| null_tape:session_same_sign>=0.75 | ok | 0.8500 | ok | 0.8500 |
| no_time_proxy_columns | ok | ["hmm3_p0", "hmm3_p1", "hmm3_p2"] | ok | ["hmm3_p0", "hmm3_p1", "hmm3_p2"] |

**hmm4** — nested passed **no**, fixed passed no, beats the matched H2 rule (scope all) no, candidate **no**

| check | nested | value | fixed | value |
|---|---|---|---|---|
| kept_share>=20% | ok | 0.7203 | ok | 0.9734 |
| kept_n>=80 | ok | 595 | ok | 804 |
| diff>0 | **FAIL** | -910.4000 | ok | 1128.1600 |
| diff_top1_removed>0 | **FAIL** | -836.3700 | ok | 905.8300 |
| kept_mean_slip8>0 | **FAIL** | -1401.6200 | **FAIL** | -1116.9700 |
| sign_blocks>=8/12 | **FAIL** | 3 | ok | 8 |
| control_pct>=95 | **FAIL** | 6.7000 | **FAIL** | 77.5000 |
| cpcv_p5_diff>0 | **FAIL** | -883.4100 | **FAIL** | -883.4100 |
| pbo<=0.2 | **FAIL** | 0.3194 | **FAIL** | 0.3194 |
| dsr_p<0.1 | **FAIL** | 0.9997 | **FAIL** | 0.9451 |
| spa_p<=0.10 | ok | 0.0015 | ok | 0.0015 |
| boot_ci_excludes_0 | **FAIL** | [-1426.06, -362.5] | ok | [371.67, 1915.52] |
| null_tape:real_diff>gmm_p95 | ok | 1001.2200 | ok | 1001.2200 |
| null_tape:real_diff>segment_p95 | ok | 1117.0900 | ok | 1117.0900 |
| null_tape:session_same_sign>=0.75 | ok | 0.7500 | ok | 0.7500 |
| no_time_proxy_columns | ok | ["hmm4_p0", "hmm4_p1", "hmm4_p2", "hmm4_p3"] | ok | ["hmm4_p0", "hmm4_p1", "hmm4_p2", "hmm4_p3"] |

**gmm4** — nested passed **no**, fixed passed no, beats the matched H2 rule (scope all) no, candidate **no**

| check | nested | value | fixed | value |
|---|---|---|---|---|
| kept_share>=20% | ok | 0.6949 | ok | 0.5182 |
| kept_n>=80 | ok | 574 | ok | 428 |
| diff>0 | **FAIL** | -108.9000 | ok | 484.4200 |
| diff_top1_removed>0 | **FAIL** | -176.9600 | ok | 173.8700 |
| kept_mean_slip8>0 | **FAIL** | -1180.2400 | **FAIL** | -913.6100 |
| sign_blocks>=8/12 | **FAIL** | 7 | ok | 10 |
| control_pct>=95 | **FAIL** | 11.2000 | **FAIL** | 1.6000 |
| cpcv_p5_diff>0 | **FAIL** | -298.3300 | **FAIL** | -298.3300 |
| pbo<=0.2 | **FAIL** | 0.3194 | **FAIL** | 0.3194 |
| dsr_p<0.1 | **FAIL** | 0.9962 | **FAIL** | 0.9794 |
| spa_p<=0.10 | ok | 0.0015 | ok | 0.0015 |
| boot_ci_excludes_0 | **FAIL** | [-657.61, 405.7] | **FAIL** | [-86.46, 1091.67] |
| null_tape:real_diff>gmm_p95 | ok | 282.1900 | ok | 282.1900 |
| null_tape:real_diff>segment_p95 | ok | 353.9100 | ok | 353.9100 |
| null_tape:session_same_sign>=0.75 | ok | 0.8500 | ok | 0.8500 |
| no_time_proxy_columns | ok | ["gmm4_p0", "gmm4_p1", "gmm4_p2", "gmm4_p3"] | ok | ["gmm4_p0", "gmm4_p1", "gmm4_p2", "gmm4_p3"] |

**jump4** — nested passed **no**, fixed passed no, beats the matched H2 rule (scope all) yes, candidate **no**

| check | nested | value | fixed | value |
|---|---|---|---|---|
| kept_share>=20% | ok | 0.6114 | ok | 0.6114 |
| kept_n>=80 | ok | 505 | ok | 505 |
| diff>0 | ok | 453.1000 | ok | 453.1000 |
| diff_top1_removed>0 | ok | 614.6200 | ok | 614.6200 |
| kept_mean_slip8>0 | **FAIL** | -970.9300 | **FAIL** | -970.9300 |
| sign_blocks>=8/12 | **FAIL** | 7 | **FAIL** | 7 |
| control_pct>=95 | ok | 100.0000 | ok | 100.0000 |
| cpcv_p5_diff>0 | **FAIL** | -351.9900 | **FAIL** | -351.9900 |
| pbo<=0.2 | **FAIL** | 0.3194 | **FAIL** | 0.3194 |
| dsr_p<0.1 | **FAIL** | 0.9653 | **FAIL** | 0.9653 |
| spa_p<=0.10 | ok | 0.0015 | ok | 0.0015 |
| boot_ci_excludes_0 | **FAIL** | [-47.92, 931.56] | **FAIL** | [-65.46, 960.97] |
| null_tape:real_diff>gmm_p95 | ok | 389.7000 | ok | 389.7000 |
| null_tape:real_diff>segment_p95 | ok | 431.2000 | ok | 431.2000 |
| null_tape:session_same_sign>=0.75 | **FAIL** | 0.3500 | **FAIL** | 0.3500 |
| no_time_proxy_columns | ok | ["jump4_state"] | ok | ["jump4_state"] |

**jump3** — nested passed **no**, fixed passed no, beats the matched H2 rule (scope all) no, candidate **no**

| check | nested | value | fixed | value |
|---|---|---|---|---|
| kept_share>=20% | ok | 0.6465 | ok | 0.7869 |
| kept_n>=80 | ok | 534 | ok | 650 |
| diff>0 | **FAIL** | -731.5800 | ok | 55.4400 |
| diff_top1_removed>0 | **FAIL** | -770.8300 | **FAIL** | -72.0300 |
| kept_mean_slip8>0 | **FAIL** | -1405.6400 | **FAIL** | -1135.2000 |
| sign_blocks>=8/12 | **FAIL** | 2 | **FAIL** | 7 |
| control_pct>=95 | **FAIL** | 0.4000 | **FAIL** | 21.9000 |
| cpcv_p5_diff>0 | **FAIL** | -689.8700 | **FAIL** | -689.8700 |
| pbo<=0.2 | **FAIL** | 0.3194 | **FAIL** | 0.3194 |
| dsr_p<0.1 | **FAIL** | 0.9995 | **FAIL** | 0.9928 |
| spa_p<=0.10 | ok | 0.0015 | ok | 0.0015 |
| boot_ci_excludes_0 | **FAIL** | [-1106.23, -360.51] | **FAIL** | [-449.1, 541.42] |
| null_tape:real_diff>gmm_p95 | **FAIL** | 591.8300 | **FAIL** | 591.8300 |
| null_tape:real_diff>segment_p95 | **FAIL** | 614.2100 | **FAIL** | 614.2100 |
| null_tape:session_same_sign>=0.75 | ok | 0.8000 | ok | 0.8000 |
| no_time_proxy_columns | ok | ["jump3_state"] | ok | ["jump3_state"] |

## 12. Verdict

**Null result: no regime gate is a candidate.** No model passes `harness.go_no_go` on its nested OOF row (failing items per model: hmm3: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:real_diff>gmm_p95, null_tape:real_diff>segment_p95; hmm4: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0; gmm4: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0; jump4: kept_mean_slip8>0, sign_blocks>=8/12, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:session_same_sign>=0.75; jump3: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:real_diff>gmm_p95, null_tape:real_diff>segment_p95). Beats the matched H2 hand rule at matched skip fraction: hmm3 no, hmm4 no, gmm4 no, jump4 yes, jump3 no. The best nested OOF difference is jump4's 453.10 INR per trade (kept share 0.6114, control pct 100.0, perm p 0.1554, 7/12 blocks, CPCV p5 -351.99); the family's PBO is 0.3194 over 89 rows (1.80 effective trials) and its SPA p 0.0015 is carried by the jump4 cell (the SPA-best row, `eae12cb14cca03b5`, mean selection gain 358.93 INR per session, t 5.17 over 136 active sessions): the SPA gain is the same within-session contrast as the control percentile, and section 7b shows that contrast is inflated for this cell by construction, so the one item the family passes is the one item that cannot carry it. No `candidates/` JSON is written; no fz key is proposed (the 40-60-number HMM key would be a user decision in any case, and nothing here earns the offer).

**The one positive out-of-fold gate, jump4** (skip when the online jump4 state is state 1, the quiet state; the chop was state 1 in all 12 training folds and the tau grid is degenerate for a hard state, so the nested OOF row, the fixed rule and every grid cell are one mask, `9d7f9977cc402b7a` / `054bded46d11afe9`): kept 505 (0.6114), kept mean -580.97 vs skipped -1034.07, diff **453.10**, top-1%-removed 614.62, control pct 100.0, permutation p 0.1554, 7/12 blocks, kept mean at 8 pts slippage -970.93, bootstrap 90% CI of the diff [-47.92, 931.56] (P(diff <= 0) 0.066), CPCV median 203.49 / p5 -351.99 (0.55 of paths positive), DSR p 0.965; it beats the matched H2 cell (k = 2, diff 257.83) on the pooled diff. On the certificate tapes its real diff 453.10 is above the GMM-Markov p95 389.70 and the segment p95 431.20 (the memory-free tapes give the same rule a median of 105.84 / 13.52 and reach +431.20 at the 95th percentile by engine mechanics alone), but the session-bootstrap tapes carry its sign in only 0.35 of tapes (median -76.96): on tapes that keep every real session intact and only reorder the days, the gate reads negative more often than positive. Section 7b shows why the two within-session statistics it passes (control, SPA) are inflated: state 1 is the session's first, early SETUP. It fails 7 go/no-go items (kept_mean_slip8>0, sign_blocks>=8/12, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:session_same_sign>=0.75) and is not a candidate; its distillation is not expressible (fidelity 0.820 against a majority baseline 0.611), so even a passing version would have been a 40-60-number fz key, a user decision.

**Judge 1's prediction, measured.** The chop states the training folds pick for hmm3 (state 0), gmm4 (state 1) and jump3 (state 1) are the CHoCH-count states (high mean `choch_since_bos` input: section 2), and their depth-3 distillations on the base features reproduce them at 0.914 / 0.869 / 0.903 out-of-fold fidelity from `n_choch_since_bos_today`, `bars_since_choch`, `bar_range_atr`, `alt_dir6` / `n_flip_since_bos` and `bars_since_bos`: the HMM / GMM / jump 'chop' at a SETUP bar is the CHoCH count with a bar-size condition, which the importance study's clustering had already said, and the gates built on it sit at control percentiles 0-13 like the H2 hand rule. The chop pick itself is unstable across training folds for four of the five models (section 5: hmm3 0/1, hmm4 1/2/3, gmm4 1/2, jump3 0/1/2), which is the label-switching-plus-selection trap named in the design; the out-of-fold rows are what that instability costs (hmm3 -509.09, hmm4 -910.40, gmm4 -108.90, jump3 -731.58). hmm4's 'expressible' flag is the design's letter only: its skip share is 0.027, the majority baseline 0.973 exceeds the fidelity 0.963, balanced accuracy 0.539: the tree does not express the state, it never skips.

On the jump3 claim specifically (the importance family's SPA-best row `4535288bcf0f1148`, diff +827.00 at kept share 0.868): the chop-state gate on the same columns, chosen inside training folds, gives a nested OOF diff of -731.58 (CPCV median -615.15, p5 -689.87, share of paths positive 0.000), control pct 0.4, 2/12 blocks; the fixed rule's real-tape diff 55.44 sits at the 55.0th / 65.0th percentile of the GMM-Markov / segment tapes (p95 591.83 / 614.21) with the session tapes carrying its sign in 0.800 of tapes. The SFI row's +827 was the bagging's OOB-tau gate on `jump3_state` + `jump3_run` (a learned function of both columns, kept share 0.868); the state-only skip at the nested threshold does not reproduce it as a gate that passes the program's rule.

## 13. What would falsify these findings

- A model whose nested OOF row shows diff > 0 with the top 1% winners removed, control pct >= 95, >= 8/12 blocks, CPCV 5th percentile > 0, a bootstrap 90% CI of the diff above 0, SPA p <= 0.10 over the family, and a real-tape diff above the GMM-Markov and segment tapes' 95th percentiles with the session tapes carrying its sign in >= 75% of them, AND a diff above the matched H2 cell's: none does here (section 11).
- A chop state that is the same state in every training fold AND whose gate's kept-vs-skipped difference is positive in >= 8 of the 12 blocks (the fold trace in section 5 shows where the pick moved; the block diffs beside each OOF row show where the sign held).
- The refit not reproducing `ext_features.parquet` (section 9: it does to 1e-8), or a tape replay that reads a label (it reads bars and events only).
- A different chop definition (posterior-weighted expectancy instead of MAP grouping, or a minimum-support guard) or a different tau criterion would be a new registration with its own sha and the multiplicity carried forward, never an edit of this one.

## 14. Caveats

- Every column read is outside the frozen shortlist: the frozen shortlist is empty on both timeframes, so this study ran under the EMPTY-SHORTLIST RULE of the phase-3 launch (PROGRESS.md); nothing here could be frozen as a candidate without the user accepting that provenance.
- 5 minutes only (Judge 1); 826 IS units in 408 active sessions, 229 winners: the standard error of a kept-vs-skipped difference at a 60/40 split is several hundred INR per trade; a null here is 'not shown', not 'shown absent'.
- The state models were fitted on the first IS half (2021-10..2023-09) and frozen; for SETUPs inside that window the posteriors are label-free in-sample (features_ext/README.md states it). The chop state and tau are the only supervised choices and they are made inside the training folds.
- For the jump models the tau grid is degenerate (a hard state): their five grid cells are one mask scored five times; the effective-trial count of the family discounts them and the tau recorded for their fixed rule (0.9, the tie rule) is any tau in the grid.
- The chop state is the worst-expectancy MAP state on the training rows with no minimum-support guard (the design's rule as written): a small state with a bad training mean can be picked, which the fold trace shows; the CPCV distribution is the honest reading of that instability.
- The null-tape replay applies the fixed rule (chop*, tau* chosen on all IS) to tapes filtered through models fitted on the real fit window; a tape's states mean something else than the real tape's, which is the point of a memory-free null, and the same fixed rule is applied on both sides.
- The distilled tree's fidelity is read against the majority baseline; a fidelity above 0.85 that is below the baseline is a tree that never skips, not an expressible state.
- The session-matched control percentile of a gate that reads the CHoCH state is partly engine mechanics (null_tapes_drift section 4c): the tape p95 of the diff, not the control percentile, is the bar; both are reported.
- The 55 CPCV path rows are written by `harness.score_paths`, which passes no `note`; their `config.vocabulary` field carries the 'outside the frozen shortlist' label (verified on all 89 rows), the 34 grid / nested / distilled rows carry it in both `note` and `config`.
- Other phase-3 studies append to the ledger concurrently: the ledger sha `48625a58eac73cde` is the file at the moment this run finished; a later sha reflects their rows, not a change to these 89 (append-only; ids in `results.json`).
- Section 7b's 'last unit of the session' column uses the session's later SETUPs (post-SETUP information) to describe the control's mechanics; it is a diagnostic, not a feature, and no rule reads it.
- Smoke test: `regime_gate.py --smoke` ran once on a redirected ledger (scratchpad) with the L1 nets shuffled within IS (seed 0) and controls off, so no real kept-vs-skipped number exists off the program ledger; its outputs are not in this folder.

## 15. Files

- `studies/regime_gate/rg_lib.py`
- `studies/regime_gate/regime_gate.py`
- `studies/regime_gate/diagnostics.py`
- `studies/regime_gate/write_findings.py`
- `studies/regime_gate/regime_gate.log`
- `studies/regime_gate/results.json`
- `studies/regime_gate/grid.csv`
- `studies/regime_gate/nested_folds.csv`
- `studies/regime_gate/cpcv_paths.csv`
- `studies/regime_gate/state_tables_is.csv`
- `studies/regime_gate/tape_diffs.csv`
- `studies/regime_gate/FINDINGS.md`
- `studies/regime_gate/findings.json`
