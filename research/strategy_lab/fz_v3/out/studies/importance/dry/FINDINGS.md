# importance: FINDINGS (DESIGN_PANEL quant-ml-canon-feature-importance, both judges' fixes)

**What this study is.** The feature-vocabulary pass: which clusters of as-of columns (base design + the 61 extended columns handed here by the regime-breaks, regime-states, motif-shapelet and rocket-probe judges) carry information about the L1 outcome under the harness splitter; the shortlist of at most 8 clusters per timeframe that the gate studies may draw features from, frozen in the ledger before any gate search; the FFD verdict; the five interaction pairs that are the only depth-2/3 conjunctions allowed downstream. This study proposes **no gate**: the only kept-vs-skipped numbers are the ledger rows of the OOF gates it had to evaluate (the full bagged model at its training-fold tau, each SFI cluster at its tau, the CPCV paths of the full model), reported as ceilings, never as candidates. IS only.

## Definitions (fixed before the numbers)

```
Importance study library (DESIGN_PANEL: quant-ml-canon-feature-importance, both judges' fixes; feature hand-offs from
regime-breaks, regime-states, motif-shapelet, rocket-probe). Every definition below is fixed before any number is looked at.

Feature set        harness.design(T) (base as-of columns, one-hot text, 0/1 booleans) + the 61 extended as-of columns of
                   features_ext/<tf>/ext_features.parquet joined on setup_i. Columns with > 40% NaN on IS rows dropped and listed;
                   constant columns dropped; exact duplicates (|Spearman| > 0.999 on IS) dropped, the first kept; of a two-level
                   one-hot the second level is dropped (its complement carries the same information). Missing indicators
                   `<col>__na` for every kept column with a NaN on IS, de-duplicated by NaN pattern (one indicator per pattern,
                   named after its first column; the covered columns are listed). Median imputation uses the TRAINING fold's
                   medians (bagging); xgboost sees NaN as such.
Label / weights    L1 binary (net > 0); sample weight = |net| winsorised at the training fold's 99th percentile, normalised to
                   mean 1; class balance by DecisionTreeClassifier(class_weight="balanced"). Test-fold weights for the weighted
                   log-loss: |net| of the test rows winsorised at the SAME training-fold p99, normalised to mean 1 on the fold.
Model              BaggingClassifier(DecisionTreeClassifier(max_depth=4 (3 and 5 as a sensitivity), min_weight_fraction_leaf=0.05,
                   class_weight="balanced"), n_estimators=300, bootstrap, oob_score) under harness.purged_splits (12 blocks).
tau                chosen INSIDE the training fold on the bagging's out-of-bag probabilities: the p_win threshold on the grid
                   0.05..0.95 (step 0.01) maximising the kept mean net subject to |net|-weighted winner recall >= 0.90.
Clustering         Spearman correlation on IS rows (pairwise-complete; undefined -> 0), distance sqrt(0.5 (1 - rho)), scipy
                   average linkage, the cut with the best silhouette (precomputed distance) over 20..40 clusters.
Representative     per cluster, by config-expressibility tier (0 = integer-valued / boolean / one-hot / card or fz field;
                   1 = ATR ratio or other dimensionless; 2 = raw points / levels), then coverage, then centrality (mean |rho| to
                   the cluster's members).
Clustered MDA      per fold, the features of a cluster are permuted JOINTLY on the test rows (same row permutation for every
                   member, missing indicators included), 5 permutations; recorded per fold: the increase in OOF weighted log-loss
                   (primary: the pass rule and the ranks) and the decrease in the OOF kept-vs-skipped mean-net difference at the
                   fold's tau (harness.metrics, controls off; secondary, reported with its own ratio). Mean and std across the 12
                   folds; a cluster passes MDA when mean > std (log-loss).
MDI                per fold forest: sum over trees of feature_importances_ / n_trees, summed per cluster, averaged over folds.
SFI                each cluster alone (its members + indicators), same folds, same weights, same tau rule; its OOF gate is a
                   ledger row (family importance/sfi).
Stability          the per-fold, per-permutation OOF probabilities are kept per row, so the log-loss MDA is re-computed on the
                   rows of each period (minute: calendar years 2022 (with 2021-10..12), 2023, 2024, 2025; 5minute: halves
                   2021-10..2023-09 and 2023-10..2025-12); a cluster ranks top-8 in >= 3 of 4 years (minute) / in both halves
                   (5minute) or it is not shortlisted. The models are the 12 fold models (trained on the other 11 purged blocks).
Orthogonal check   PCA on the standardised (IS-median-imputed, z-scored) IS features; a bagging of the same shape on the PC
                   scores; scipy.stats.weightedtau between its MDI per component and the eigenvalues.
Interactions       xgboost max_depth 3, 200 rounds, eta 0.05, the same folds, on the top-40 features by clustered MDA (clusters
                   in MDA order, members in MDI order); shap.TreeExplainer(...).shap_interaction_values on the OOF rows; pairs
                   ranked by mean |interaction|; the top 5 pairs carry the gain-weighted median split point of each feature over
                   the tree paths where both features occur (all 12 fold boosters pooled).
```

Constants: trees 300, min_weight_fraction_leaf 0.05, main depth 4 (sensitivity (3, 5)), permutations per fold 5, tau grid 0.05..0.95 step 0.01, weighted winner recall floor 0.9, silhouette range 20..40 clusters, stability top-8, interactions on the top-40 features, 5 pairs; xgboost depth 3, 200 rounds, eta 0.05. Every model fit uses `harness.purged_splits` (12 blocks, purge by the L1 exit bar, 3-session embargo); nothing is fitted on OOS rows; OOS labels and features are never read.


## minute

### Feature set

| item | value |
|---|---|
| L1 units (IS) | 1002 (826) |
| base design columns (harness.design) | 236 (text column dropped by design, > 16 levels: `last6_kinds`) |
| extended columns | 61 |
| dropped, > 40% NaN on IS | 38: `card_first_clock_lived` 0.992, `card_bars_since_hunt` 0.906, `card_hunt_dir_agree` 0.906, `fz_entered_visit_n` 0.803, `card_wick_depth` 0.724, `hv3_low_held` 0.719, `hv3_high_held` 0.719, `hv2_low_held` 0.655, `hv2_high_held` 0.655, `card_bars_since_reject` 0.614, `hv3_bars_since` 0.586, `hv3_dir_agree` 0.586, `hv3_ratio` 0.586, `touch_room_bars_ago` 0.548, `last_closed_net_asof` 0.494, `card_prev_bars` 0.489, `ret_3h_pts` 0.487, `card_leave_vol_ok` 0.436, `fz_leave_vol_ok` 0.436, `card_visit_n` 0.403, `card_this_bars` 0.403, `card_first_bars` 0.403, `card_first_vol_na` 0.403, `card_out_run` 0.403, `card_last_leave_failed` 0.403, `card_touches` 0.403, `fz_visit_n` 0.403, `fz_this_bars` 0.403, `fz_first_bars` 0.403, `fz_first_vol_na` 0.403, `fz_level_in_band` 0.403, `fz_band_width` 0.403, `fz_band_width_atr` 0.403, `fz_pos_in_band` 0.403, `fz_pos_in_band_dir` 0.403, `fz_dist_band_edge_ahead` 0.403, `fz_dist_band_edge_behind` 0.403, `card_vol_ratio` 0.403 |
| dropped, constant on IS | 4: `choch_flip`, `vol_na`, `card_vol_na`, `fz_vol_na` |
| dropped, second level of a two-level one-hot | 6: `dir=up`, `last_bos_dir=up`, `last_choch_dir=up`, `swing_near_kind=L`, `room_edge_kind=lo`, `fz_zone_kind=nan` |
| dropped, exact duplicate (|Spearman| > 0.999) | 28: `dir_sign` = `dir=down`, `choch_trend_before` = `dir=down`, `n_flip_since_bos` = `n_choch_since_bos`, `choch_run` = `n_choch_since_bos`, `swing_near_dist_dir_atr` = `swing_ahead_dist_atr`, `today_n_setups_before` = `today_n_closed_asof`, `card_leave_side=nan` = `card_read=LEAVE`, `card_leave_kind=nan` = `card_read=LEAVE`, `fz_read=ACCEPTED` = `card_read=ACCEPTED`, `fz_read=FIRST_PRINT` = `card_read=FIRST_PRINT`, `fz_read=HUNT` = `card_read=HUNT`, `fz_read=LEAVE` = `card_read=LEAVE`, `fz_read=NEW` = `card_read=NEW`, `fz_read=PENDING` = `card_read=PENDING`, `fz_read=RECYCLE` = `card_read=RECYCLE`, `fz_read=REJECT` = `card_read=REJECT`, `fz_read=THIN` = `card_read=THIN`, `fz_block_reason=clock` = `hour_bin=>=15:20`, `fz_branch=first_print` = `card_read=FIRST_PRINT`, `fz_branch=watch` = `fz_gate=REENTER`, `fz_take_why=leave_into_recycle` = `fz_block_reason=leave_into_recycle`, `fz_leave_kind=gap` = `card_leave_kind=gap`, `fz_leave_kind=nan` = `card_read=LEAVE`, `fz_leave_kind=normal` = `card_leave_kind=normal`, `fz_watch_kind=nan` = `fz_gate=WATCH`, `card_ref_room_live` = `fz_zone_kind=B`, `rv_range_atr` = `bar_range_atr`, `rv_range36_atr` = `range_3h_atr` |
| missing indicators (one per NaN pattern) | 17: `gap_pts__na` (2 cols), `ret_1h_pts__na` (1 cols), `er_1h__na` (5 cols), `bars_since_prev_choch__na` (6 cols), `sess_cumvol_ratio20s__na` (5 cols), `hv2_bars_since__na` (3 cols), `vol_ratio20_at_choch__na` (1 cols), `vol_max_ratio20_choch_to_k__na` (1 cols), `dist_prot_dir_atr__na` (2 cols), `room_ahead_dist_atr__na` (1 cols), `room_behind_dist_atr__na` (1 cols), `touch_prot_bars_ago__na` (1 cols), `touch_swing_bars_ago__na` (1 cols), `csw_max_abs__na` (4 cols), `bocpd_ret_h60_since_reset__na` (2 cols), `bocpd_rng_h60_since_reset__na` (2 cols), `nn_dist_prefix_long__na` (2 cols) |
| **features in the model** | **238** |
| clustering | silhouette best k = 39 (0.1502), clusters formed 39 |
| runtime / max RSS | 252.4 s / 371.7 MB |

### The full bagged model (ceiling; not a candidate)

| depth | OOF weighted log-loss | OOF AUC | gate kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | perm p | control pct | loser recall | weighted winner recall | top-decile winners skipped | sign blocks | kept mean slip 8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 (main) | 0.734 | 0.5158 | 800 | 0.9685 | -760.09 | -663.59 | -96.5 | -320.34 | None | None | 0.0335 | 0.9774 | 0.0 | 2 | -1150.05 | `DRY` |
| 3 | 0.73752 | 0.5304 | - | 0.9504 | - | - | 239.82 | - | None | None | - | - | - | - | - | `DRY` |
| 5 | 0.72506 | 0.5227 | - | 0.9758 | - | - | -119.27 | - | None | None | - | - | - | - | - | `DRY` |

Per fold (depth 4): tau chosen on the training fold's OOB probabilities.

| fold | n train | n test | |net| cap (train p99) | tau | OOF weighted log-loss | OOF diff | kept share |
|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 16029.2 | 0.05 | 0.71655 | - | 1.0000 |
| 1 | 741 | 83 | 14989.1 | 0.05 | 0.71332 | - | 1.0000 |
| 2 | 784 | 42 | 16746.1 | 0.35 | 0.70383 | 431.03 | 0.9286 |
| 3 | 742 | 76 | 17645.5 | 0.42 | 0.81188 | -451.18 | 0.8816 |
| 4 | 754 | 72 | 17388.5 | 0.22 | 0.7428 | - | 1.0000 |
| 5 | 747 | 73 | 17538.4 | 0.12 | 0.73973 | - | 1.0000 |
| 6 | 745 | 77 | 15993.9 | 0.33 | 0.69817 | -1839.19 | 0.9610 |
| 7 | 775 | 51 | 14972.0 | 0.35 | 0.69378 | 482.32 | 0.8431 |
| 8 | 747 | 76 | 15251.0 | 0.05 | 0.75791 | - | 1.0000 |
| 9 | 746 | 80 | 15279.1 | 0.05 | 0.75471 | - | 1.0000 |
| 10 | 794 | 31 | 16532.0 | 0.4 | 0.8235 | -301.11 | 0.9032 |
| 11 | 743 | 83 | 17624.1 | 0.05 | 0.68586 | - | 1.0000 |

CPCV: not run (dry mode).

### Clustered importance table (all clusters, sorted by log-loss MDA)

Full table with members, per-period MDA values and SFI ledger ids: `importance_clusters_minute.csv`; per-feature MDI, tier, coverage and README definition: `importance_features_minute.csv`.

| rank | cluster | representative | n | MDA ll mean | std | ratio | pass | MDA diff mean | std | pass | MDI | SFI ll | SFI AUC | SFI diff | SFI kept | SFI ctrl pct | rank H1_2021-10..2023-09 | rank H2_2023-10..2025-12 | top-8 periods | stable | eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | `fz_block_reason=new` | 6 | 0.00159 | 0.00290 | 0.55 | no | -185.3 | 401.7 | no | 0.0191 | 0.7739 | 0.498 | 83.8 | 0.869 | - | 2 | 1 | 2 | yes | no |
| 2 | 17 | `touch_room_last=broke` | 4 | 0.00148 | 0.00653 | 0.23 | no | 259.4 | 1604.1 | no | 0.0405 | 0.7688 | 0.526 | 567.9 | 0.874 | - | 1 | 4 | 2 | yes | no |
| 3 | 12 | `card_read=LEAVE` | 5 | 0.00120 | 0.00317 | 0.38 | no | 23.5 | 209.4 | no | 0.0093 | 0.7779 | 0.533 | - | 1.000 | - | 22 | 5 | 1 | no | no |
| 4 | 22 | `days_to_expiry` | 2 | 0.00054 | 0.00391 | 0.14 | no | -80.7 | 180.4 | no | 0.0086 | 0.7837 | 0.489 | -558.0 | 0.952 | - | 26 | 8 | 1 | no | no |
| 5 | 23 | `dow` | 2 | 0.00000 | 0.00604 | 0.00 | no | 50.6 | 113.2 | no | 0.0172 | 0.7744 | 0.525 | 278.4 | 0.956 | - | 30 | 6 | 1 | no | no |
| 6 | 15 | `fz_block_reason=hunt_fade` | 4 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7844 | 0.515 | - | 1.000 | - | 8 | 16 | 1 | no | no |
| 7 | 8 | `gap_pts__na` | 6 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 4 | 15 | 1 | no | no |
| 8 | 35 | `hv2_dir=flat` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 17 | 25 | 0 | no | no |
| 9 | 32 | `fz_gate=REENTER` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 16 | 24 | 0 | no | no |
| 10 | 33 | `hour_bin=10` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7849 | 0.535 | 317.8 | 0.866 | - | 15 | 23 | 0 | no | no |
| 11 | 34 | `hour_bin=11` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7865 | 0.506 | -167.4 | 0.912 | - | 21 | 29 | 0 | no | no |
| 12 | 37 | `room_behind_dist_atr__na` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 19 | 27 | 0 | no | no |
| 13 | 36 | `last_bos_dir=down` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0001 | 0.7840 | 0.492 | - | 1.000 | - | 20 | 28 | 0 | no | no |
| 14 | 38 | `touch_prot_last=broke` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 18 | 26 | 0 | no | no |
| 15 | 18 | `touch_prot_last=na` | 4 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7847 | 0.504 | 369.7 | 0.908 | - | 13 | 11 | 0 | no | no |
| 16 | 31 | `fz_entered_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 14 | 21 | 0 | no | no |
| 17 | 30 | `fz_entered_read=ACCEPTED` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 5 | 17 | 1 | no | no |
| 18 | 28 | `card_read=REJECT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 12 | 20 | 0 | no | no |
| 19 | 29 | `csw_sign_dir` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 7 | 22 | 1 | no | no |
| 20 | 27 | `card_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 11 | 19 | 0 | no | no |
| 21 | 26 | `touch_swing_last=none` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 10 | 18 | 0 | no | no |
| 22 | 24 | `card_read=RECYCLE` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 9 | 13 | 0 | no | no |
| 23 | 19 | `card_read=ACCEPTED` | 3 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 6 | 12 | 1 | no | no |
| 24 | 16 | `touch_prot_last=held` | 4 | -0.00022 | 0.00741 | -0.03 | no | -135.1 | 139.6 | no | 0.0251 | 0.7827 | 0.496 | 1834.6 | 0.999 | - | 36 | 2 | 1 | no | no |
| 25 | 20 | `touch_prot_last=pending` | 3 | -0.00028 | 0.00094 | -0.30 | no | 0.0 | 0.0 | no | 0.0024 | 0.7787 | 0.499 | -398.6 | 0.940 | - | 24 | 32 | 0 | no | no |
| 26 | 7 | `fz_gate=TAKE` | 6 | -0.00032 | 0.00909 | -0.04 | no | -24.5 | 688.1 | no | 0.0328 | 0.7815 | 0.515 | 186.0 | 0.899 | - | 32 | 9 | 0 | no | no |
| 27 | 21 | `n_events_asof` | 3 | -0.00043 | 0.00154 | -0.28 | no | 0.0 | 0.0 | no | 0.0108 | 0.7783 | 0.483 | - | 1.000 | - | 28 | 14 | 0 | no | no |
| 28 | 10 | `touch_swing_last=pending` | 6 | -0.00047 | 0.00127 | -0.37 | no | 9.3 | 20.8 | no | 0.0075 | 0.7704 | 0.508 | - | 1.000 | - | 25 | 33 | 0 | no | no |
| 29 | 13 | `last_choch_dir=down` | 5 | -0.00048 | 0.00240 | -0.20 | no | 105.4 | 321.5 | no | 0.0061 | 0.7731 | 0.548 | 973.7 | 0.890 | - | 23 | 35 | 0 | no | no |
| 30 | 4 | `swing_near_kind=H` | 16 | -0.00074 | 0.01014 | -0.07 | no | -398.6 | 1089.6 | no | 0.1129 | 0.7547 | 0.526 | 12.4 | 0.946 | - | 35 | 10 | 0 | no | no |
| 31 | 25 | `jump3_run` | 2 | -0.00080 | 0.00105 | -0.76 | no | -101.7 | 237.7 | no | 0.0062 | 0.7913 | 0.490 | 888.1 | 0.895 | - | 27 | 36 | 0 | no | no |
| 32 | 14 | `touch_room_last=held` | 5 | -0.00091 | 0.00288 | -0.32 | no | 5.8 | 598.1 | no | 0.0198 | 0.7557 | 0.525 | 1823.6 | 0.978 | - | 33 | 7 | 1 | no | no |
| 33 | 6 | `fz_watch_kind=WATCH` | 12 | -0.00103 | 0.00368 | -0.28 | no | -164.3 | 283.6 | no | 0.0347 | 0.7555 | 0.514 | 316.5 | 0.898 | - | 31 | 30 | 0 | no | no |
| 34 | 5 | `n_bos_since_choch` | 14 | -0.00129 | 0.00265 | -0.49 | no | -215.3 | 481.4 | no | 0.0213 | 0.7660 | 0.499 | -51.1 | 0.948 | - | 3 | 37 | 1 | no | no |
| 35 | 1 | `n_events_today` | 26 | -0.00190 | 0.01659 | -0.11 | no | -296.9 | 1248.4 | no | 0.1413 | 0.7477 | 0.516 | 164.6 | 0.904 | - | 34 | 31 | 0 | no | no |
| 36 | 2 | `hv2_dir=none` | 18 | -0.00209 | 0.00842 | -0.25 | no | -76.3 | 279.1 | no | 0.0473 | 0.7698 | 0.511 | -48.3 | 0.936 | - | 38 | 3 | 1 | no | no |
| 37 | 3 | `n_choch_since_bos` | 17 | -0.00324 | 0.00586 | -0.55 | no | 36.6 | 602.1 | no | 0.0697 | 0.7582 | 0.487 | 405.7 | 0.941 | - | 37 | 34 | 0 | no | no |
| 38 | 9 | `cusum_events_60` | 6 | -0.00328 | 0.01142 | -0.29 | no | -395.1 | 765.5 | no | 0.0636 | 0.7657 | 0.488 | -582.7 | 0.959 | - | 29 | 38 | 0 | no | no |
| 39 | 0 | `gmm4_map` | 43 | -0.01500 | 0.02122 | -0.71 | no | -232.7 | 955.6 | no | 0.3037 | 0.7484 | 0.472 | 933.0 | 0.989 | - | 39 | 39 | 0 | no | no |

Stability: periods H1_2021-10..2023-09 (412 rows, 124 winners), H2_2023-10..2025-12 (414 rows, 105 winners); rule top-8 in >= 2 of 2 periods; Spearman rank correlation of the cluster MDA vectors across periods: H1_2021-10..2023-09|H2_2023-10..2025-12: 0.0827.

Orthogonal check: 238 components (111 carry 95% of the variance); weighted Kendall tau between the MDI of the PC-score forest and the eigenvalues = **0.0813** (Kendall tau 0.1206, p 0.0123). A low tau is the AFML warning that the importance ranking may be fitting noise rather than variance-bearing directions.

### Cluster membership

| cluster | representative (tier; why) | members |
|---|---|---|
| 0 | `gmm4_map` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.348) | `sl_dist_pts`, `sl_dist_atr`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `bars_since_prev_choch`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir_agree`, `hv2_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `jump4_run`, `win_sign_agree10`, `win_range_slope` |
| 1 | `n_events_today` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.442) | `session_bar`, `hour`, `hour_bin=13`, `hour_bin=14`, `hour_bin=15`, `choch_same_session`, `sess_range_atr`, `last_bos_same_session`, `n_events_today`, `n_choch_today`, `n_bos_today`, `hv2_dir=down`, `hv3_dir=down`, `today_n_closed_asof`, `today_n_stops_asof`, `last_closed_reason_asof=next_choch`, `last_closed_reason_asof=stop_loss`, `bocpd_ret_h60_map`, `bocpd_ret_h60_since_reset`, `bocpd_ret_h240_map`, `bocpd_ret_h240_since_reset`, `bocpd_rng_h60_map`, `bocpd_rng_h60_since_reset`, `bocpd_rng_h240_map`, `bocpd_rng_h240_since_reset`, `rv_ev36` |
| 2 | `hv2_dir=none` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.423) | `hour_bin=09`, `hour_bin=<09:25`, `hv2_dir=none`, `hv3_dir=none`, `today_net_asof`, `today_pts_asof`, `last_closed_reason_asof=nan`, `card_leave_kind=gap`, `fz_block_reason=open_pierce`, `fz_take_why=leave_gap_quiet`, `bocpd_rng_h60_p10`, `bocpd_rng_h240_p10`, `ret_1h_pts__na`, `er_1h__na`, `hv2_bars_since__na`, `vol_ratio20_at_choch__na`, `vol_max_ratio20_choch_to_k__na`, `csw_max_abs__na` |
| 3 | `n_choch_since_bos` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.496) | `n_choch_since_bos`, `bars_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `n_choch_1h`, `n_choch_3h`, `touch_swing_n`, `touch_swing_last=broke`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump4_state`, `nn_dist_prefix_long`, `p1_dist_prefix_long` |
| 4 | `swing_near_kind=H` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.495) | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_read=PENDING`, `card_out_side=up`, `card_last_reject_dir=down`, `fz_watch_kind=WATCH_EDGE`, `ffd_close_dstar_z60`, `rv_ret36_atr` |
| 5 | `n_bos_since_choch` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.730) | `bars_since_choch`, `n_bos_since_choch`, `alt_kind6`, `n_bos_1h`, `n_bos_3h`, `touch_swing_last=held`, `touch_swing_bars_ago`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3` |
| 6 | `fz_watch_kind=WATCH` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.431) | `room_edge_dist_dir_atr`, `touch_room_last=none`, `card_read=THIN`, `card_last_reject_dir=up`, `fz_zone_kind=B`, `fz_gate=WATCH`, `fz_block_reason=leave_into_recycle`, `fz_branch=nan`, `fz_entered_read=RECYCLE`, `fz_entered_read=THIN`, `fz_watch_kind=WATCH`, `card_in_room` |
| 7 | `fz_gate=TAKE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.453) | `card_last_hunt_dir=nan`, `fz_gate=TAKE`, `fz_block_reason=nan`, `fz_branch=leave`, `fz_take_why=nan`, `fz_entered_read=nan` |
| 8 | `gap_pts__na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.726 (missing indicator, the cluster's only member)) | `gap_pts__na`, `bars_since_prev_choch__na`, `sess_cumvol_ratio20s__na`, `bocpd_ret_h60_since_reset__na`, `bocpd_rng_h60_since_reset__na`, `nn_dist_prefix_long__na` |
| 9 | `cusum_events_60` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.186) | `hour_bin=12`, `range_3h_pts`, `range_3h_atr`, `sess_cumvol_ratio20s`, `sess_vol_vs_prev_sess`, `cusum_events_60` |
| 10 | `touch_swing_last=pending` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.326) | `hv2_bars_since`, `swing_ahead_dist_atr`, `touch_room_last=pending`, `touch_swing_last=pending`, `card_cluster_sit`, `cusum_bars_since` |
| 11 | `fz_block_reason=new` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.434) | `room_behind_dist_atr`, `card_read=NEW`, `card_out_side=nan`, `card_last_reject_dir=nan`, `fz_gate=BLOCK`, `fz_block_reason=new` |
| 12 | `card_read=LEAVE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.483) | `card_read=LEAVE`, `card_leave_side=up`, `card_leave_kind=normal`, `fz_take_why=leave_vol_fail`, `fz_entered_read=REJECT` |
| 13 | `last_choch_dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.736) | `dir=down`, `last_choch_dir=down`, `dist_sh_atr`, `card_out_side=down`, `card_leave_side=down` |
| 14 | `touch_room_last=held` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.128) | `touch_room_last=held`, `bsadf_close_win`, `nn_dist_prefix_short`, `p1_dist_prefix_short`, `win_dd_extreme_atr` |
| 15 | `fz_block_reason=hunt_fade` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.359) | `card_read=HUNT`, `card_last_hunt_dir=down`, `card_last_hunt_dir=up`, `fz_block_reason=hunt_fade` |
| 16 | `touch_prot_last=held` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.390) | `last_sh_bars_ago`, `last_sl_bars_ago`, `touch_prot_last=held`, `touch_prot_bars_ago` |
| 17 | `touch_room_last=broke` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.391) | `room_ahead_dist_atr`, `touch_room_n`, `touch_room_last=broke`, `room_ahead_dist_atr__na` |
| 18 | `touch_prot_last=na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.483) | `touch_prot_last=na`, `touch_prot_last=none`, `dist_prot_dir_atr__na`, `touch_prot_bars_ago__na` |
| 19 | `card_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.603) | `card_read=ACCEPTED`, `fz_take_why=accepted_no_defend`, `fz_take_why=defend_wrong_half` |
| 20 | `touch_prot_last=pending` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.292) | `n_swings_1h`, `touch_prot_n`, `touch_prot_last=pending` |
| 21 | `n_events_asof` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.930) | `sl`, `n_events_asof`, `ffd_close_dstar` |
| 22 | `days_to_expiry` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.151) | `days_to_expiry`, `n_rooms_alive` |
| 23 | `dow` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.108) | `dow`, `gap_pts` |
| 24 | `card_read=RECYCLE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.127) | `hour_bin=>=15:20`, `card_read=RECYCLE` |
| 25 | `jump3_run` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.436) | `jump3_state`, `jump3_run` |
| 26 | `touch_swing_last=none` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_swing_last=none`, `touch_swing_bars_ago__na` |
| 27 | `card_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `card_read=FIRST_PRINT` |
| 28 | `card_read=REJECT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `card_read=REJECT` |
| 29 | `csw_sign_dir` (tier 0 (integer/boolean/one-hot/card field), coverage 0.939, mean |rho| to members 1.000) | `csw_sign_dir` |
| 30 | `fz_entered_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=ACCEPTED` |
| 31 | `fz_entered_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=FIRST_PRINT` |
| 32 | `fz_gate=REENTER` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_gate=REENTER` |
| 33 | `hour_bin=10` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=10` |
| 34 | `hour_bin=11` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=11` |
| 35 | `hv2_dir=flat` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hv2_dir=flat` |
| 36 | `last_bos_dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `last_bos_dir=down` |
| 37 | `room_behind_dist_atr__na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000 (missing indicator, the cluster's only member)) | `room_behind_dist_atr__na` |
| 38 | `touch_prot_last=broke` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_prot_last=broke` |

### Interactions (xgboost on the top-40 features by clustered MDA; OOF weighted log-loss 0.73033, OOF AUC 0.5355)

| rank | feature a | feature b | mean abs SHAP interaction (OOF rows) | paths with both | split a (gain-weighted median) | split b | common splits a | common splits b |
|---|---|---|---|---|---|---|---|---|
| 1 | `room_ahead_dist_atr` | `n_rooms_alive` | 0.052708 | 746 | 0.7548 | 8.0000 | [0.7394, 0.7617, 0.7664] | [7.0, 8.0, 10.0] |
| 2 | `room_behind_dist_atr` | `room_ahead_dist_atr` | 0.040988 | 1509 | 0.7312 | 0.5646 | [3.4141, 3.3514, 3.4717] | [4.1739, 0.0284, 0.1638] |
| 3 | `room_ahead_dist_atr` | `days_to_expiry` | 0.039840 | 973 | 0.5124 | 12.0000 | [0.0284, 0.3419, 4.1739] | [27.0, 8.0, 29.0] |
| 4 | `room_behind_dist_atr` | `days_to_expiry` | 0.032939 | 655 | 0.2798 | 10.0000 | [0.2798, 0.2764, 0.1888] | [9.0, 29.0, 10.0] |
| 5 | `n_rooms_alive` | `dow` | 0.027953 | 180 | 10.0000 | 3.0000 | [10.0, 11.0, 7.0] | [3.0, 1.0, 4.0] |

All ranked pairs: `interaction_pairs_minute.csv`; the full mean |interaction| matrix: `shap_interactions_minute.csv`. The gate studies may use only these five pairs as depth-2/3 conjunctions (and only where both features are shortlisted columns: none of the five lies inside the shortlist).

### Do the H2 CHoCH counts and the state-model posteriors share a cluster?

| H2 count column | cluster |
|---|---|
| `n_choch_since_bos` | 3 |
| `n_choch_since_bos_today` | 3 |
| `alt_dir6` | 3 |
| `alt_kind6` | 5 |

| state-model column | cluster |
|---|---|
| `gmm3_p0` | 3 |
| `gmm3_p1` | 5 |
| `gmm3_p2` | 0 |
| `gmm3_map` | 0 |
| `gmm4_p0` | 5 |
| `gmm4_p1` | 3 |
| `gmm4_p2` | 5 |
| `gmm4_p3` | 0 |
| `gmm4_map` | 0 |
| `hmm3_p0` | 3 |
| `hmm3_p1` | 5 |
| `hmm3_p2` | 0 |
| `hmm3_map` | 0 |
| `hmm3_map_run` | 3 |
| `hmm4_p0` | 5 |
| `hmm4_p1` | 5 |
| `hmm4_p2` | 3 |
| `hmm4_p3` | 5 |
| `hmm4_map` | 0 |
| `hmm4_map_run` | 3 |
| `jump3_state` | 25 |
| `jump3_run` | 25 |
| `jump4_state` | 3 |
| `jump4_run` | 0 |

**Yes, in part**: cluster 3 holds `n_choch_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump4_state`; cluster 5 holds `alt_kind6`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3`. Where an HMM / GMM / jump posterior sits in the same cluster as `n_choch_since_bos`, the state model adds nothing the count does not already say (Judge 1 of regime-states): no HMM gate is run later for those states.

### FFD columns

| ffd column | cluster |
|---|---|
| `ffd_close_dstar` | 21 |
| `ffd_close_dstar_z60` | 4 |
| `ffd_vol_dstar` | 0 |
| `ffd_vol_dstar_z60` | 0 |

| cluster | members | MDA ll mean | std | pass | stable | mixed with non-FFD columns |
|---|---|---|---|---|---|---|
| 0 | `sl_dist_pts`, `sl_dist_atr`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `bars_since_prev_choch`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir_agree`, `hv2_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `jump4_run`, `win_sign_agree10`, `win_range_slope` | -0.01500 | 0.02122 | no | no | yes |
| 4 | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_read=PENDING`, `card_out_side=up`, `card_last_reject_dir=down`, `fz_watch_kind=WATCH_EDGE`, `ffd_close_dstar_z60`, `rv_ret36_atr` | -0.00074 | 0.01014 | no | no | yes |
| 21 | `sl`, `n_events_asof`, `ffd_close_dstar` | -0.00043 | 0.00154 | no | no | yes |

### The shortlist (0 clusters; 0 of 39 pass MDA, 2 pass stability, 0 pass both; cap 8)

Frozen at `features_shortlist/minute/shortlist.json`, sha256 `163bbd6e1dddb1c19524227b5195b6e372ecfa55997a4dc3a4d4dc8f5bfd456a`, registered in `ledger/registrations.jsonl`. Allowed columns for the gate studies: 0.

**Empty**: no cluster passes both the MDA rule and the stability filter on this timeframe. The gate studies have no shortlisted column here; a null vocabulary is a result, not a failure of the pipeline.


## 5minute

### Feature set

| item | value |
|---|---|
| L1 units (IS) | 1002 (826) |
| base design columns (harness.design) | 236 (text column dropped by design, > 16 levels: `last6_kinds`) |
| extended columns | 61 |
| dropped, > 40% NaN on IS | 38: `card_first_clock_lived` 0.992, `card_bars_since_hunt` 0.906, `card_hunt_dir_agree` 0.906, `fz_entered_visit_n` 0.803, `card_wick_depth` 0.724, `hv3_low_held` 0.719, `hv3_high_held` 0.719, `hv2_low_held` 0.655, `hv2_high_held` 0.655, `card_bars_since_reject` 0.614, `hv3_bars_since` 0.586, `hv3_dir_agree` 0.586, `hv3_ratio` 0.586, `touch_room_bars_ago` 0.548, `last_closed_net_asof` 0.494, `card_prev_bars` 0.489, `ret_3h_pts` 0.487, `card_leave_vol_ok` 0.436, `fz_leave_vol_ok` 0.436, `card_visit_n` 0.403, `card_this_bars` 0.403, `card_first_bars` 0.403, `card_first_vol_na` 0.403, `card_out_run` 0.403, `card_last_leave_failed` 0.403, `card_touches` 0.403, `fz_visit_n` 0.403, `fz_this_bars` 0.403, `fz_first_bars` 0.403, `fz_first_vol_na` 0.403, `fz_level_in_band` 0.403, `fz_band_width` 0.403, `fz_band_width_atr` 0.403, `fz_pos_in_band` 0.403, `fz_pos_in_band_dir` 0.403, `fz_dist_band_edge_ahead` 0.403, `fz_dist_band_edge_behind` 0.403, `card_vol_ratio` 0.403 |
| dropped, constant on IS | 4: `choch_flip`, `vol_na`, `card_vol_na`, `fz_vol_na` |
| dropped, second level of a two-level one-hot | 6: `dir=up`, `last_bos_dir=up`, `last_choch_dir=up`, `swing_near_kind=L`, `room_edge_kind=lo`, `fz_zone_kind=nan` |
| dropped, exact duplicate (|Spearman| > 0.999) | 28: `dir_sign` = `dir=down`, `choch_trend_before` = `dir=down`, `n_flip_since_bos` = `n_choch_since_bos`, `choch_run` = `n_choch_since_bos`, `swing_near_dist_dir_atr` = `swing_ahead_dist_atr`, `today_n_setups_before` = `today_n_closed_asof`, `card_leave_side=nan` = `card_read=LEAVE`, `card_leave_kind=nan` = `card_read=LEAVE`, `fz_read=ACCEPTED` = `card_read=ACCEPTED`, `fz_read=FIRST_PRINT` = `card_read=FIRST_PRINT`, `fz_read=HUNT` = `card_read=HUNT`, `fz_read=LEAVE` = `card_read=LEAVE`, `fz_read=NEW` = `card_read=NEW`, `fz_read=PENDING` = `card_read=PENDING`, `fz_read=RECYCLE` = `card_read=RECYCLE`, `fz_read=REJECT` = `card_read=REJECT`, `fz_read=THIN` = `card_read=THIN`, `fz_block_reason=clock` = `hour_bin=>=15:20`, `fz_branch=first_print` = `card_read=FIRST_PRINT`, `fz_branch=watch` = `fz_gate=REENTER`, `fz_take_why=leave_into_recycle` = `fz_block_reason=leave_into_recycle`, `fz_leave_kind=gap` = `card_leave_kind=gap`, `fz_leave_kind=nan` = `card_read=LEAVE`, `fz_leave_kind=normal` = `card_leave_kind=normal`, `fz_watch_kind=nan` = `fz_gate=WATCH`, `card_ref_room_live` = `fz_zone_kind=B`, `rv_range_atr` = `bar_range_atr`, `rv_range36_atr` = `range_3h_atr` |
| missing indicators (one per NaN pattern) | 17: `gap_pts__na` (2 cols), `ret_1h_pts__na` (1 cols), `er_1h__na` (5 cols), `bars_since_prev_choch__na` (6 cols), `sess_cumvol_ratio20s__na` (5 cols), `hv2_bars_since__na` (3 cols), `vol_ratio20_at_choch__na` (1 cols), `vol_max_ratio20_choch_to_k__na` (1 cols), `dist_prot_dir_atr__na` (2 cols), `room_ahead_dist_atr__na` (1 cols), `room_behind_dist_atr__na` (1 cols), `touch_prot_bars_ago__na` (1 cols), `touch_swing_bars_ago__na` (1 cols), `csw_max_abs__na` (4 cols), `bocpd_ret_h60_since_reset__na` (2 cols), `bocpd_rng_h60_since_reset__na` (2 cols), `nn_dist_prefix_long__na` (2 cols) |
| **features in the model** | **238** |
| clustering | silhouette best k = 39 (0.1502), clusters formed 39 |
| runtime / max RSS | 252.4 s / 371.7 MB |

### The full bagged model (ceiling; not a candidate)

| depth | OOF weighted log-loss | OOF AUC | gate kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | perm p | control pct | loser recall | weighted winner recall | top-decile winners skipped | sign blocks | kept mean slip 8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 (main) | 0.734 | 0.5158 | 800 | 0.9685 | -760.09 | -663.59 | -96.5 | -320.34 | None | None | 0.0335 | 0.9774 | 0.0 | 2 | -1150.05 | `DRY` |
| 3 | 0.73752 | 0.5304 | - | 0.9504 | - | - | 239.82 | - | None | None | - | - | - | - | - | `DRY` |
| 5 | 0.72506 | 0.5227 | - | 0.9758 | - | - | -119.27 | - | None | None | - | - | - | - | - | `DRY` |

Per fold (depth 4): tau chosen on the training fold's OOB probabilities.

| fold | n train | n test | |net| cap (train p99) | tau | OOF weighted log-loss | OOF diff | kept share |
|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 16029.2 | 0.05 | 0.71655 | - | 1.0000 |
| 1 | 741 | 83 | 14989.1 | 0.05 | 0.71332 | - | 1.0000 |
| 2 | 784 | 42 | 16746.1 | 0.35 | 0.70383 | 431.03 | 0.9286 |
| 3 | 742 | 76 | 17645.5 | 0.42 | 0.81188 | -451.18 | 0.8816 |
| 4 | 754 | 72 | 17388.5 | 0.22 | 0.7428 | - | 1.0000 |
| 5 | 747 | 73 | 17538.4 | 0.12 | 0.73973 | - | 1.0000 |
| 6 | 745 | 77 | 15993.9 | 0.33 | 0.69817 | -1839.19 | 0.9610 |
| 7 | 775 | 51 | 14972.0 | 0.35 | 0.69378 | 482.32 | 0.8431 |
| 8 | 747 | 76 | 15251.0 | 0.05 | 0.75791 | - | 1.0000 |
| 9 | 746 | 80 | 15279.1 | 0.05 | 0.75471 | - | 1.0000 |
| 10 | 794 | 31 | 16532.0 | 0.4 | 0.8235 | -301.11 | 0.9032 |
| 11 | 743 | 83 | 17624.1 | 0.05 | 0.68586 | - | 1.0000 |

CPCV: not run (dry mode).

### Clustered importance table (all clusters, sorted by log-loss MDA)

Full table with members, per-period MDA values and SFI ledger ids: `importance_clusters_5minute.csv`; per-feature MDI, tier, coverage and README definition: `importance_features_5minute.csv`.

| rank | cluster | representative | n | MDA ll mean | std | ratio | pass | MDA diff mean | std | pass | MDI | SFI ll | SFI AUC | SFI diff | SFI kept | SFI ctrl pct | rank H1_2021-10..2023-09 | rank H2_2023-10..2025-12 | top-8 periods | stable | eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | `fz_block_reason=new` | 6 | 0.00159 | 0.00290 | 0.55 | no | -185.3 | 401.7 | no | 0.0191 | 0.7739 | 0.498 | 83.8 | 0.869 | - | 2 | 1 | 2 | yes | no |
| 2 | 17 | `touch_room_last=broke` | 4 | 0.00148 | 0.00653 | 0.23 | no | 259.4 | 1604.1 | no | 0.0405 | 0.7688 | 0.526 | 567.9 | 0.874 | - | 1 | 4 | 2 | yes | no |
| 3 | 12 | `card_read=LEAVE` | 5 | 0.00120 | 0.00317 | 0.38 | no | 23.5 | 209.4 | no | 0.0093 | 0.7779 | 0.533 | - | 1.000 | - | 22 | 5 | 1 | no | no |
| 4 | 22 | `days_to_expiry` | 2 | 0.00054 | 0.00391 | 0.14 | no | -80.7 | 180.4 | no | 0.0086 | 0.7837 | 0.489 | -558.0 | 0.952 | - | 26 | 8 | 1 | no | no |
| 5 | 23 | `dow` | 2 | 0.00000 | 0.00604 | 0.00 | no | 50.6 | 113.2 | no | 0.0172 | 0.7744 | 0.525 | 278.4 | 0.956 | - | 30 | 6 | 1 | no | no |
| 6 | 15 | `fz_block_reason=hunt_fade` | 4 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7844 | 0.515 | - | 1.000 | - | 8 | 16 | 1 | no | no |
| 7 | 8 | `gap_pts__na` | 6 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 4 | 15 | 1 | no | no |
| 8 | 35 | `hv2_dir=flat` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 17 | 25 | 0 | no | no |
| 9 | 32 | `fz_gate=REENTER` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 16 | 24 | 0 | no | no |
| 10 | 33 | `hour_bin=10` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7849 | 0.535 | 317.8 | 0.866 | - | 15 | 23 | 0 | no | no |
| 11 | 34 | `hour_bin=11` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7865 | 0.506 | -167.4 | 0.912 | - | 21 | 29 | 0 | no | no |
| 12 | 37 | `room_behind_dist_atr__na` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 19 | 27 | 0 | no | no |
| 13 | 36 | `last_bos_dir=down` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0001 | 0.7840 | 0.492 | - | 1.000 | - | 20 | 28 | 0 | no | no |
| 14 | 38 | `touch_prot_last=broke` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 18 | 26 | 0 | no | no |
| 15 | 18 | `touch_prot_last=na` | 4 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7847 | 0.504 | 369.7 | 0.908 | - | 13 | 11 | 0 | no | no |
| 16 | 31 | `fz_entered_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 14 | 21 | 0 | no | no |
| 17 | 30 | `fz_entered_read=ACCEPTED` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 5 | 17 | 1 | no | no |
| 18 | 28 | `card_read=REJECT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 12 | 20 | 0 | no | no |
| 19 | 29 | `csw_sign_dir` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 7 | 22 | 1 | no | no |
| 20 | 27 | `card_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 11 | 19 | 0 | no | no |
| 21 | 26 | `touch_swing_last=none` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 10 | 18 | 0 | no | no |
| 22 | 24 | `card_read=RECYCLE` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 9 | 13 | 0 | no | no |
| 23 | 19 | `card_read=ACCEPTED` | 3 | 0.00000 | 0.00000 | - | no | 0.0 | 0.0 | no | 0.0000 | 0.7852 | 0.530 | - | 1.000 | - | 6 | 12 | 1 | no | no |
| 24 | 16 | `touch_prot_last=held` | 4 | -0.00022 | 0.00741 | -0.03 | no | -135.1 | 139.6 | no | 0.0251 | 0.7827 | 0.496 | 1834.6 | 0.999 | - | 36 | 2 | 1 | no | no |
| 25 | 20 | `touch_prot_last=pending` | 3 | -0.00028 | 0.00094 | -0.30 | no | 0.0 | 0.0 | no | 0.0024 | 0.7787 | 0.499 | -398.6 | 0.940 | - | 24 | 32 | 0 | no | no |
| 26 | 7 | `fz_gate=TAKE` | 6 | -0.00032 | 0.00909 | -0.04 | no | -24.5 | 688.1 | no | 0.0328 | 0.7815 | 0.515 | 186.0 | 0.899 | - | 32 | 9 | 0 | no | no |
| 27 | 21 | `n_events_asof` | 3 | -0.00043 | 0.00154 | -0.28 | no | 0.0 | 0.0 | no | 0.0108 | 0.7783 | 0.483 | - | 1.000 | - | 28 | 14 | 0 | no | no |
| 28 | 10 | `touch_swing_last=pending` | 6 | -0.00047 | 0.00127 | -0.37 | no | 9.3 | 20.8 | no | 0.0075 | 0.7704 | 0.508 | - | 1.000 | - | 25 | 33 | 0 | no | no |
| 29 | 13 | `last_choch_dir=down` | 5 | -0.00048 | 0.00240 | -0.20 | no | 105.4 | 321.5 | no | 0.0061 | 0.7731 | 0.548 | 973.7 | 0.890 | - | 23 | 35 | 0 | no | no |
| 30 | 4 | `swing_near_kind=H` | 16 | -0.00074 | 0.01014 | -0.07 | no | -398.6 | 1089.6 | no | 0.1129 | 0.7547 | 0.526 | 12.4 | 0.946 | - | 35 | 10 | 0 | no | no |
| 31 | 25 | `jump3_run` | 2 | -0.00080 | 0.00105 | -0.76 | no | -101.7 | 237.7 | no | 0.0062 | 0.7913 | 0.490 | 888.1 | 0.895 | - | 27 | 36 | 0 | no | no |
| 32 | 14 | `touch_room_last=held` | 5 | -0.00091 | 0.00288 | -0.32 | no | 5.8 | 598.1 | no | 0.0198 | 0.7557 | 0.525 | 1823.6 | 0.978 | - | 33 | 7 | 1 | no | no |
| 33 | 6 | `fz_watch_kind=WATCH` | 12 | -0.00103 | 0.00368 | -0.28 | no | -164.3 | 283.6 | no | 0.0347 | 0.7555 | 0.514 | 316.5 | 0.898 | - | 31 | 30 | 0 | no | no |
| 34 | 5 | `n_bos_since_choch` | 14 | -0.00129 | 0.00265 | -0.49 | no | -215.3 | 481.4 | no | 0.0213 | 0.7660 | 0.499 | -51.1 | 0.948 | - | 3 | 37 | 1 | no | no |
| 35 | 1 | `n_events_today` | 26 | -0.00190 | 0.01659 | -0.11 | no | -296.9 | 1248.4 | no | 0.1413 | 0.7477 | 0.516 | 164.6 | 0.904 | - | 34 | 31 | 0 | no | no |
| 36 | 2 | `hv2_dir=none` | 18 | -0.00209 | 0.00842 | -0.25 | no | -76.3 | 279.1 | no | 0.0473 | 0.7698 | 0.511 | -48.3 | 0.936 | - | 38 | 3 | 1 | no | no |
| 37 | 3 | `n_choch_since_bos` | 17 | -0.00324 | 0.00586 | -0.55 | no | 36.6 | 602.1 | no | 0.0697 | 0.7582 | 0.487 | 405.7 | 0.941 | - | 37 | 34 | 0 | no | no |
| 38 | 9 | `cusum_events_60` | 6 | -0.00328 | 0.01142 | -0.29 | no | -395.1 | 765.5 | no | 0.0636 | 0.7657 | 0.488 | -582.7 | 0.959 | - | 29 | 38 | 0 | no | no |
| 39 | 0 | `gmm4_map` | 43 | -0.01500 | 0.02122 | -0.71 | no | -232.7 | 955.6 | no | 0.3037 | 0.7484 | 0.472 | 933.0 | 0.989 | - | 39 | 39 | 0 | no | no |

Stability: periods H1_2021-10..2023-09 (412 rows, 124 winners), H2_2023-10..2025-12 (414 rows, 105 winners); rule top-8 in >= 2 of 2 periods; Spearman rank correlation of the cluster MDA vectors across periods: H1_2021-10..2023-09|H2_2023-10..2025-12: 0.0827.

Orthogonal check: 238 components (111 carry 95% of the variance); weighted Kendall tau between the MDI of the PC-score forest and the eigenvalues = **0.0813** (Kendall tau 0.1206, p 0.0123). A low tau is the AFML warning that the importance ranking may be fitting noise rather than variance-bearing directions.

### Cluster membership

| cluster | representative (tier; why) | members |
|---|---|---|
| 0 | `gmm4_map` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.348) | `sl_dist_pts`, `sl_dist_atr`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `bars_since_prev_choch`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir_agree`, `hv2_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `jump4_run`, `win_sign_agree10`, `win_range_slope` |
| 1 | `n_events_today` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.442) | `session_bar`, `hour`, `hour_bin=13`, `hour_bin=14`, `hour_bin=15`, `choch_same_session`, `sess_range_atr`, `last_bos_same_session`, `n_events_today`, `n_choch_today`, `n_bos_today`, `hv2_dir=down`, `hv3_dir=down`, `today_n_closed_asof`, `today_n_stops_asof`, `last_closed_reason_asof=next_choch`, `last_closed_reason_asof=stop_loss`, `bocpd_ret_h60_map`, `bocpd_ret_h60_since_reset`, `bocpd_ret_h240_map`, `bocpd_ret_h240_since_reset`, `bocpd_rng_h60_map`, `bocpd_rng_h60_since_reset`, `bocpd_rng_h240_map`, `bocpd_rng_h240_since_reset`, `rv_ev36` |
| 2 | `hv2_dir=none` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.423) | `hour_bin=09`, `hour_bin=<09:25`, `hv2_dir=none`, `hv3_dir=none`, `today_net_asof`, `today_pts_asof`, `last_closed_reason_asof=nan`, `card_leave_kind=gap`, `fz_block_reason=open_pierce`, `fz_take_why=leave_gap_quiet`, `bocpd_rng_h60_p10`, `bocpd_rng_h240_p10`, `ret_1h_pts__na`, `er_1h__na`, `hv2_bars_since__na`, `vol_ratio20_at_choch__na`, `vol_max_ratio20_choch_to_k__na`, `csw_max_abs__na` |
| 3 | `n_choch_since_bos` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.496) | `n_choch_since_bos`, `bars_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `n_choch_1h`, `n_choch_3h`, `touch_swing_n`, `touch_swing_last=broke`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump4_state`, `nn_dist_prefix_long`, `p1_dist_prefix_long` |
| 4 | `swing_near_kind=H` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.495) | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_read=PENDING`, `card_out_side=up`, `card_last_reject_dir=down`, `fz_watch_kind=WATCH_EDGE`, `ffd_close_dstar_z60`, `rv_ret36_atr` |
| 5 | `n_bos_since_choch` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.730) | `bars_since_choch`, `n_bos_since_choch`, `alt_kind6`, `n_bos_1h`, `n_bos_3h`, `touch_swing_last=held`, `touch_swing_bars_ago`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3` |
| 6 | `fz_watch_kind=WATCH` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.431) | `room_edge_dist_dir_atr`, `touch_room_last=none`, `card_read=THIN`, `card_last_reject_dir=up`, `fz_zone_kind=B`, `fz_gate=WATCH`, `fz_block_reason=leave_into_recycle`, `fz_branch=nan`, `fz_entered_read=RECYCLE`, `fz_entered_read=THIN`, `fz_watch_kind=WATCH`, `card_in_room` |
| 7 | `fz_gate=TAKE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.453) | `card_last_hunt_dir=nan`, `fz_gate=TAKE`, `fz_block_reason=nan`, `fz_branch=leave`, `fz_take_why=nan`, `fz_entered_read=nan` |
| 8 | `gap_pts__na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.726 (missing indicator, the cluster's only member)) | `gap_pts__na`, `bars_since_prev_choch__na`, `sess_cumvol_ratio20s__na`, `bocpd_ret_h60_since_reset__na`, `bocpd_rng_h60_since_reset__na`, `nn_dist_prefix_long__na` |
| 9 | `cusum_events_60` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.186) | `hour_bin=12`, `range_3h_pts`, `range_3h_atr`, `sess_cumvol_ratio20s`, `sess_vol_vs_prev_sess`, `cusum_events_60` |
| 10 | `touch_swing_last=pending` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.326) | `hv2_bars_since`, `swing_ahead_dist_atr`, `touch_room_last=pending`, `touch_swing_last=pending`, `card_cluster_sit`, `cusum_bars_since` |
| 11 | `fz_block_reason=new` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.434) | `room_behind_dist_atr`, `card_read=NEW`, `card_out_side=nan`, `card_last_reject_dir=nan`, `fz_gate=BLOCK`, `fz_block_reason=new` |
| 12 | `card_read=LEAVE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.483) | `card_read=LEAVE`, `card_leave_side=up`, `card_leave_kind=normal`, `fz_take_why=leave_vol_fail`, `fz_entered_read=REJECT` |
| 13 | `last_choch_dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.736) | `dir=down`, `last_choch_dir=down`, `dist_sh_atr`, `card_out_side=down`, `card_leave_side=down` |
| 14 | `touch_room_last=held` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.128) | `touch_room_last=held`, `bsadf_close_win`, `nn_dist_prefix_short`, `p1_dist_prefix_short`, `win_dd_extreme_atr` |
| 15 | `fz_block_reason=hunt_fade` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.359) | `card_read=HUNT`, `card_last_hunt_dir=down`, `card_last_hunt_dir=up`, `fz_block_reason=hunt_fade` |
| 16 | `touch_prot_last=held` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.390) | `last_sh_bars_ago`, `last_sl_bars_ago`, `touch_prot_last=held`, `touch_prot_bars_ago` |
| 17 | `touch_room_last=broke` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.391) | `room_ahead_dist_atr`, `touch_room_n`, `touch_room_last=broke`, `room_ahead_dist_atr__na` |
| 18 | `touch_prot_last=na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.483) | `touch_prot_last=na`, `touch_prot_last=none`, `dist_prot_dir_atr__na`, `touch_prot_bars_ago__na` |
| 19 | `card_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.603) | `card_read=ACCEPTED`, `fz_take_why=accepted_no_defend`, `fz_take_why=defend_wrong_half` |
| 20 | `touch_prot_last=pending` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.292) | `n_swings_1h`, `touch_prot_n`, `touch_prot_last=pending` |
| 21 | `n_events_asof` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.930) | `sl`, `n_events_asof`, `ffd_close_dstar` |
| 22 | `days_to_expiry` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.151) | `days_to_expiry`, `n_rooms_alive` |
| 23 | `dow` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.108) | `dow`, `gap_pts` |
| 24 | `card_read=RECYCLE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.127) | `hour_bin=>=15:20`, `card_read=RECYCLE` |
| 25 | `jump3_run` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.436) | `jump3_state`, `jump3_run` |
| 26 | `touch_swing_last=none` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_swing_last=none`, `touch_swing_bars_ago__na` |
| 27 | `card_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `card_read=FIRST_PRINT` |
| 28 | `card_read=REJECT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `card_read=REJECT` |
| 29 | `csw_sign_dir` (tier 0 (integer/boolean/one-hot/card field), coverage 0.939, mean |rho| to members 1.000) | `csw_sign_dir` |
| 30 | `fz_entered_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=ACCEPTED` |
| 31 | `fz_entered_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=FIRST_PRINT` |
| 32 | `fz_gate=REENTER` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_gate=REENTER` |
| 33 | `hour_bin=10` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=10` |
| 34 | `hour_bin=11` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=11` |
| 35 | `hv2_dir=flat` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hv2_dir=flat` |
| 36 | `last_bos_dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `last_bos_dir=down` |
| 37 | `room_behind_dist_atr__na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000 (missing indicator, the cluster's only member)) | `room_behind_dist_atr__na` |
| 38 | `touch_prot_last=broke` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_prot_last=broke` |

### Interactions (xgboost on the top-40 features by clustered MDA; OOF weighted log-loss 0.73033, OOF AUC 0.5355)

| rank | feature a | feature b | mean abs SHAP interaction (OOF rows) | paths with both | split a (gain-weighted median) | split b | common splits a | common splits b |
|---|---|---|---|---|---|---|---|---|
| 1 | `room_ahead_dist_atr` | `n_rooms_alive` | 0.052708 | 746 | 0.7548 | 8.0000 | [0.7394, 0.7617, 0.7664] | [7.0, 8.0, 10.0] |
| 2 | `room_behind_dist_atr` | `room_ahead_dist_atr` | 0.040988 | 1509 | 0.7312 | 0.5646 | [3.4141, 3.3514, 3.4717] | [4.1739, 0.0284, 0.1638] |
| 3 | `room_ahead_dist_atr` | `days_to_expiry` | 0.039840 | 973 | 0.5124 | 12.0000 | [0.0284, 0.3419, 4.1739] | [27.0, 8.0, 29.0] |
| 4 | `room_behind_dist_atr` | `days_to_expiry` | 0.032939 | 655 | 0.2798 | 10.0000 | [0.2798, 0.2764, 0.1888] | [9.0, 29.0, 10.0] |
| 5 | `n_rooms_alive` | `dow` | 0.027953 | 180 | 10.0000 | 3.0000 | [10.0, 11.0, 7.0] | [3.0, 1.0, 4.0] |

All ranked pairs: `interaction_pairs_5minute.csv`; the full mean |interaction| matrix: `shap_interactions_5minute.csv`. The gate studies may use only these five pairs as depth-2/3 conjunctions (and only where both features are shortlisted columns: none of the five lies inside the shortlist).

### Do the H2 CHoCH counts and the state-model posteriors share a cluster?

| H2 count column | cluster |
|---|---|
| `n_choch_since_bos` | 3 |
| `n_choch_since_bos_today` | 3 |
| `alt_dir6` | 3 |
| `alt_kind6` | 5 |

| state-model column | cluster |
|---|---|
| `gmm3_p0` | 3 |
| `gmm3_p1` | 5 |
| `gmm3_p2` | 0 |
| `gmm3_map` | 0 |
| `gmm4_p0` | 5 |
| `gmm4_p1` | 3 |
| `gmm4_p2` | 5 |
| `gmm4_p3` | 0 |
| `gmm4_map` | 0 |
| `hmm3_p0` | 3 |
| `hmm3_p1` | 5 |
| `hmm3_p2` | 0 |
| `hmm3_map` | 0 |
| `hmm3_map_run` | 3 |
| `hmm4_p0` | 5 |
| `hmm4_p1` | 5 |
| `hmm4_p2` | 3 |
| `hmm4_p3` | 5 |
| `hmm4_map` | 0 |
| `hmm4_map_run` | 3 |
| `jump3_state` | 25 |
| `jump3_run` | 25 |
| `jump4_state` | 3 |
| `jump4_run` | 0 |

**Yes, in part**: cluster 3 holds `n_choch_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump4_state`; cluster 5 holds `alt_kind6`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3`. Where an HMM / GMM / jump posterior sits in the same cluster as `n_choch_since_bos`, the state model adds nothing the count does not already say (Judge 1 of regime-states): no HMM gate is run later for those states.

### FFD columns

| ffd column | cluster |
|---|---|
| `ffd_close_dstar` | 21 |
| `ffd_close_dstar_z60` | 4 |
| `ffd_vol_dstar` | 0 |
| `ffd_vol_dstar_z60` | 0 |

| cluster | members | MDA ll mean | std | pass | stable | mixed with non-FFD columns |
|---|---|---|---|---|---|---|
| 0 | `sl_dist_pts`, `sl_dist_atr`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `bars_since_prev_choch`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir_agree`, `hv2_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `jump4_run`, `win_sign_agree10`, `win_range_slope` | -0.01500 | 0.02122 | no | no | yes |
| 4 | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_read=PENDING`, `card_out_side=up`, `card_last_reject_dir=down`, `fz_watch_kind=WATCH_EDGE`, `ffd_close_dstar_z60`, `rv_ret36_atr` | -0.00074 | 0.01014 | no | no | yes |
| 21 | `sl`, `n_events_asof`, `ffd_close_dstar` | -0.00043 | 0.00154 | no | no | yes |

### The shortlist (0 clusters; 0 of 39 pass MDA, 2 pass stability, 0 pass both; cap 8)

Frozen at `features_shortlist/5minute/shortlist.json`, sha256 `f6a6a9b5ae2850727f01f41b3110c0a0654db5728329ae6cbbd62ee97c1cf3e9`, registered in `ledger/registrations.jsonl`. Allowed columns for the gate studies: 0.

**Empty**: no cluster passes both the MDA rule and the stability filter on this timeframe. The gate studies have no shortlisted column here; a null vocabulary is a result, not a failure of the pipeline.


## FFD verdict (both timeframes)

**FFD not adopted (clustered MDA <= 1 std on minute, 5minute).** MDA pass of the cluster(s) holding the `ffd_*` columns: minute: no (mixed with non-FFD columns: {'0': True, '4': True, '21': True}), 5minute: no (mixed with non-FFD columns: {'0': True, '4': True, '21': True}). The rule (Judge 2): adopted only if the FFD cluster's MDA > 1 std on BOTH timeframes; adoption would need a per-bar FFD routine in fz code (a new key type, a user decision) with keys d* close 0.2 / volume 0.1, weight cut 1e-4, windows 497 / 503 bars, z-window 60.

## What would falsify these findings

- A shortlisted cluster whose MDA sign flips when the permutation seeds change (5 permutations x 12 folds are recorded per row in `oof_<tf>.npz`; rerunning with other seeds is one command).
- A shortlisted cluster whose top-8 rank in the held-out periods does not survive a different block partition (the harness fixes 12 blocks; the per-period decomposition is of the same OOF rows).
- A feature in the shortlist that the truncation check would have dropped: none can be, every column comes from `harness.design` or from `ext_features.parquet`, which passed the truncation check at tolerance 1e-9.
- The full model's kept-vs-skipped numbers are a ceiling for a model that cannot ship; if the gate studies' rule lists come nowhere near them, the vocabulary is not the bottleneck; if a rule list beats them, the forest under-fits and this table under-states the vocabulary.
- A low weighted Kendall tau in the orthogonal check says the MDI ranking is not aligned with the variance-bearing directions; the shortlist rests on MDA, not on MDI, but the two are reported side by side so a disagreement is visible.

## Candidates

None. This study fixes the vocabulary (the shortlist JSON + the five interaction pairs) and proposes no gate; the full model and the SFI gates are ledger rows for the family's PBO / SPA and are ceilings, not configs.

## Caveats

- The primary MDA statistic is the permutation drop in OOF weighted log-loss; the kept-vs-skipped MDA at the fold's tau is reported with its own mean / std but is not the pass rule (on 70-370 test rows per fold its std exceeds its mean for nearly every cluster, as Judge 1 foresaw).
- Per-period stability re-scores the same 12 fold models on the rows of each period (no refit inside a year: a 12-block CV does not exist inside ~1,100 rows / 170 winners, and refitting there would be the noise Judge 2 warns of); it measures whether the relation learned on the other blocks holds in that period.
- tau is chosen on the training fold's out-of-bag probabilities (the bagging's own inner out-of-fold estimate), not on an inner CV; OOB probabilities of a 300-tree bagging are out-of-fold for every training row.
- Two-level one-hots keep one level; exact duplicates are dropped; missing indicators are de-duplicated by NaN pattern: these are stated preprocessing steps, not searches.
- The design's distance sqrt(0.5 (1 - rho)) puts anti-correlated features at maximum distance; substitution between a feature and its negative is therefore not removed by the clustering (mitigated by the duplicate / complement drops above).
- On 5minute the FZ card's numeric fields sit at 40.3% NaN (no ref room on 40% of SETUPs): a hair over the 40% rule, so they are dropped while their categorical reads (`fz_read=...`, `card_read=...`, `fz_gate=...`) stay.
- `sl` (the Foundation stop price) and `atr14` are price-level / volatility-level columns that also proxy calendar time; if they appear in a shortlist the stability filter is what stands between them and a year effect.
- The other studies' processes shared the 4 cores during this run (load average 15-19); runtimes above are wall-clock under that load. Every fit ran single-threaded (IMP_BAG_JOBS=1, IMP_XGB_JOBS=1 in run_all.sh): on this loaded box a 300-tree bagging fit took 35 s at 1 thread vs 50 s at 4 (bag_probe.log) and a 200-round xgboost fit 0.7 s at 1 thread vs 14 s at 2 (xgb_probe.log, OpenMP spin-wait); the fitted trees do not depend on the thread count (random_state fixes them), so no model was shrunk. The run logs' header line prints the module constant n_jobs=4; the environment variable is what the fits used.

## Files

- `studies/importance/results_minute.json`
- `studies/importance/clusters_minute.json`
- `studies/importance/importance_clusters_minute.csv`
- `studies/importance/importance_features_minute.csv`
- `studies/importance/interaction_pairs_minute.csv`
- `studies/importance/shap_interactions_minute.csv`
- `studies/importance/spearman_minute.csv`
- `studies/importance/folds_minute.csv`
- `studies/importance/oof_minute.npz`
- `studies/importance/run_minute.log`
- `features_shortlist/minute/shortlist.json`
- `studies/importance/results_5minute.json`
- `studies/importance/clusters_5minute.json`
- `studies/importance/importance_clusters_5minute.csv`
- `studies/importance/importance_features_5minute.csv`
- `studies/importance/interaction_pairs_5minute.csv`
- `studies/importance/shap_interactions_5minute.csv`
- `studies/importance/spearman_5minute.csv`
- `studies/importance/folds_5minute.csv`
- `studies/importance/oof_5minute.npz`
- `studies/importance/run_5minute.log`
- `features_shortlist/5minute/shortlist.json`
- `studies/importance/imp_lib.py`
- `studies/importance/run_importance.py`
- `studies/importance/shortlist.py`
- `studies/importance/probe.py`
- `studies/importance/xgb_probe.py`
- `ledger/registrations.jsonl`
