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
| L1 units (IS) | 5266 (4452) |
| base design columns (harness.design) | 244 (text column dropped by design, > 16 levels: `last6_kinds`) |
| extended columns | 61 |
| dropped, > 40% NaN on IS | 11: `card_first_clock_lived` 0.973, `fz_entered_visit_n` 0.862, `card_bars_since_hunt` 0.661, `card_hunt_dir_agree` 0.661, `card_wick_depth` 0.636, `card_leave_vol_ok` 0.611, `fz_leave_vol_ok` 0.611, `ret_3h_pts` 0.453, `hv2_low_held` 0.422, `hv2_high_held` 0.422, `card_prev_bars` 0.412 |
| dropped, constant on IS | 6: `choch_flip`, `vol_na`, `card_vol_na`, `card_first_vol_na`, `fz_vol_na`, `fz_first_vol_na` |
| dropped, second level of a two-level one-hot | 4: `dir=up`, `last_choch_dir=up`, `swing_near_kind=L`, `fz_zone_kind=nan` |
| dropped, exact duplicate (|Spearman| > 0.999) | 32: `dir_sign` = `dir=down`, `choch_trend_before` = `dir=down`, `n_flip_since_bos` = `n_choch_since_bos`, `last_bos_dir=up` = `last_bos_dir=down`, `choch_run` = `n_choch_since_bos`, `swing_near_dist_dir_atr` = `swing_ahead_dist_atr`, `room_edge_kind=` = `last_bos_dir=none`, `room_edge_kind=lo` = `room_edge_kind=hi`, `touch_room_last=na` = `last_bos_dir=none`, `today_n_setups_before` = `today_n_closed_asof`, `card_leave_side=nan` = `card_read=LEAVE`, `card_leave_kind=nan` = `card_read=LEAVE`, `fz_visit_n` = `card_visit_n`, `fz_this_bars` = `card_this_bars`, `fz_first_bars` = `card_first_bars`, `fz_read=ACCEPTED` = `card_read=ACCEPTED`, `fz_read=FIRST_PRINT` = `card_read=FIRST_PRINT`, `fz_read=HUNT` = `card_read=HUNT`, `fz_read=LEAVE` = `card_read=LEAVE`, `fz_read=NEW` = `card_read=NEW`, `fz_read=PENDING` = `card_read=PENDING`, `fz_read=RECYCLE` = `card_read=RECYCLE`, `fz_read=REJECT` = `card_read=REJECT`, `fz_read=THIN` = `card_read=THIN`, `fz_block_reason=clock` = `hour_bin=>=15:20`, `fz_take_why=leave_into_recycle` = `fz_block_reason=leave_into_recycle`, `fz_leave_kind=gap` = `card_leave_kind=gap`, `fz_leave_kind=nan` = `card_read=LEAVE`, `fz_leave_kind=normal` = `card_leave_kind=normal`, `fz_watch_kind=nan` = `fz_gate=WATCH`, `card_ref_room_live` = `fz_zone_kind=B`, `rv_range_atr` = `bar_range_atr` |
| missing indicators (one per NaN pattern) | 24: `gap_pts__na` (2 cols), `ret_1h_pts__na` (1 cols), `er_1h__na` (5 cols), `bars_since_bos__na` (4 cols), `bars_since_prev_choch__na` (4 cols), `sess_cumvol_ratio20s__na` (1 cols), `hv2_bars_since__na` (3 cols), `hv3_bars_since__na` (3 cols), `hv3_low_held__na` (2 cols), `vol_ratio20_at_choch__na` (1 cols), `vol_max_ratio20_choch_to_k__na` (1 cols), `dist_prot_dir_atr__na` (2 cols), `room_ahead_dist_atr__na` (1 cols), `room_behind_dist_atr__na` (1 cols), `touch_prot_bars_ago__na` (1 cols), `touch_room_bars_ago__na` (1 cols), `last_closed_net_asof__na` (1 cols), `card_visit_n__na` (14 cols), `card_bars_since_reject__na` (1 cols), `ffd_close_dstar__na` (4 cols), `bsadf_close__na` (4 cols), `csw_max_abs__na` (4 cols), `bocpd_ret_h60_since_reset__na` (2 cols), `nn_dist_prefix_long__na` (2 cols) |
| **features in the model** | **276** |
| clustering | silhouette best k = 38 (0.1136), clusters formed 38 |
| run | three parallel single-thread processes (run_all.sh): main 5871 s (05:33-07:11 UTC), sfi 5592 s (-07:06), cpcv 6047 s (-07:14); finalize 11:27 after the usage-limit pause (the cpcv log lacks its two closing lines: the process wrote them to an inode unlinked by the 06:24 checkout; cpcv_minute.json and its 11 ledger rows are complete). Max RSS 448 MB (main). |

### The full bagged model (ceiling; not a candidate)

| depth | OOF weighted log-loss | OOF AUC | gate kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | perm p | control pct | loser recall | weighted winner recall | top-decile winners skipped | sign blocks | kept mean slip 8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 (main) | 0.74474 | 0.5935 | 4452 | 1.0000 | -1009.61 | - | - | - | - | - | - | - | - | - | - | `7359bf6294568ac8` |
| 3 | 0.76515 | 0.5915 | - | 0.9077 | - | - | 44.70 | - | 0.7416 | 0.0 | - | - | - | - | - | `29409a5bd96ec8d6` |
| 5 | 0.73096 | 0.5943 | - | 1.0000 | - | - | - | - | - | - | - | - | - | - | - | `b32c519d11ab77a8` |

In 12 of 12 folds the OOF gate kept every test row (a '-' in the gate columns = nothing skipped, the difference is undefined). In 11 folds the training-fold rule chose the grid floor tau = 0.05: on the training fold's OOB probabilities no threshold that kept >= 90% of the |net|-weighted winner net had a higher kept mean than keeping everything; in the other 1 fold(s) (tau [0.31]) the test probabilities all lay above it. The full model's OOF gate is therefore close to 'take everything' and its kept-vs-skipped numbers, where defined, are a ceiling of no practical value.

Per fold (depth 4): tau chosen on the training fold's OOB probabilities.

| fold | n train | n test | |net| cap (train p99) | tau | OOF weighted log-loss | OOF diff | kept share |
|---|---|---|---|---|---|---|---|
| 0 | 4034 | 396 | 10274.2 | 0.05 | 0.77388 | - | 1.0000 |
| 1 | 4058 | 388 | 10382.5 | 0.05 | 0.78495 | - | 1.0000 |
| 2 | 4048 | 384 | 11586.5 | 0.05 | 0.78604 | - | 1.0000 |
| 3 | 3914 | 509 | 11395.2 | 0.05 | 0.71873 | - | 1.0000 |
| 4 | 4062 | 390 | 11463.3 | 0.05 | 0.69301 | - | 1.0000 |
| 5 | 4082 | 341 | 11523.6 | 0.31 | 0.71679 | - | 1.0000 |
| 6 | 4012 | 424 | 10291.0 | 0.05 | 0.71495 | - | 1.0000 |
| 7 | 4186 | 266 | 10323.3 | 0.05 | 0.76236 | - | 1.0000 |
| 8 | 4282 | 170 | 10528.2 | 0.05 | 0.80748 | - | 1.0000 |
| 9 | 3953 | 499 | 10583.0 | 0.05 | 0.77097 | - | 1.0000 |
| 10 | 4259 | 173 | 11215.0 | 0.05 | 0.73581 | - | 1.0000 |
| 11 | 3940 | 512 | 11291.0 | 0.05 | 0.71674 | - | 1.0000 |

CPCV of the full model's OOF gate (66 splits, 11 paths, family `importance/full_model/cpcv`): diff median -18.66, 5th percentile -114.95, min -119.62, share of paths with diff > 0 0.455, kept share median 0.9679, control pct median 0.7 / p5 0.0.

Family `importance/*` on minute (52 ledger rows: full model x3 depths, 38 SFI clusters, 11 CPCV paths): PBO (diff) 0.0308 (IS-best below zero OOS 0.761); SPA studentised p 0.724 (RC p 0.829, best mean gain 26.3 INR/session, 33 candidates excluded for < 28 active sessions), SPA unstudentised p 0.4045 (RC p 0.417, best mean gain 26.3); effective trials 1.04; full model: bootstrap 90% CI of diff [-, -] (undefined: the OOF gate skipped nothing), kept mean CI [-1062.23, -954.79], DSR p 1.0; go/no-go passed = False (kept_share>=20%=ok, kept_n>=300=ok, diff>0=FAIL, diff_top1_removed>0=FAIL, kept_mean_slip8>0=FAIL, sign_blocks>=8/12=FAIL, control_pct>=95=FAIL, cpcv_p5_diff>0=FAIL, pbo<=0.2=ok, dsr_p<0.1=FAIL, spa_p<=0.10=FAIL, boot_ci_excludes_0=FAIL). The family exists for the ledger's PBO / SPA bookkeeping; none of its rows is a candidate.

### Clustered importance table (all clusters, sorted by log-loss MDA)

Full table with members, per-period MDA values and SFI ledger ids: `importance_clusters_minute.csv`; per-feature MDI, tier, coverage and README definition: `importance_features_minute.csv`.

| rank | cluster | representative | n | MDA ll mean | std | ratio | pass | MDA diff mean | std | pass | MDI | SFI ll | SFI AUC | SFI diff | SFI kept | SFI ctrl pct | rank 2022 | rank 2023 | rank 2024 | rank 2025 | top-8 periods | stable | eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7 | `card_read=PENDING` | 13 | 0.00030 | 0.00059 | 0.50 | no | - | - | no | 0.0188 | 0.8080 | 0.543 | 105.8 | 0.859 | 37.0 | 6 | 1 | 32 | 1 | 3 | yes | no |
| 2 | 11 | `card_read=ACCEPTED` | 7 | 0.00016 | 0.00048 | 0.33 | no | - | - | no | 0.0113 | 0.8183 | 0.503 | - | 1.000 | - | 2 | 2 | 1 | 34 | 3 | yes | no |
| 3 | 13 | `card_read=FIRST_PRINT` | 4 | 0.00008 | 0.00011 | 0.67 | no | - | - | no | 0.0036 | 0.8398 | 0.493 | -930.4 | 0.982 | 3.9 | 5 | 26 | 2 | 2 | 3 | yes | no |
| 4 | 15 | `n_events_asof` | 3 | 0.00002 | 0.00005 | 0.36 | no | - | - | no | 0.0147 | 0.7993 | 0.522 | 182.7 | 0.830 | 81.5 | 3 | 32 | 4 | 28 | 2 | no | no |
| 5 | 9 | `card_last_reject_dir=nan` | 9 | 0.00001 | 0.00025 | 0.06 | no | - | - | no | 0.0063 | 0.8194 | 0.524 | 140.5 | 0.931 | 96.0 | 29 | 3 | 27 | 30 | 1 | no | no |
| 6 | 8 | `last_bos_dir=none` | 9 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 7 | 8 | 8 | 8 | 4 | yes | no |
| 7 | 37 | `touch_swing_last=held` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 22 | 25 | 22 | 25 | 0 | no | no |
| 8 | 33 | `hour_bin=>=15:20` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 24 | 23 | 24 | 21 | 0 | no | no |
| 9 | 35 | `touch_prot_last=broke` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 23 | 22 | 23 | 22 | 0 | no | no |
| 10 | 30 | `hour_bin=10` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8419 | 0.511 | - | 1.000 | - | 21 | 17 | 19 | 17 | 0 | no | no |
| 11 | 28 | `fz_take_why=defend_opposite_in_visit` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 17 | 24 | 17 | 16 | 0 | no | no |
| 12 | 27 | `fz_entered_read=REJECT` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 20 | 20 | 20 | 20 | 0 | no | no |
| 13 | 14 | `hv3_dir=flat` | 3 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 8 | 16 | 7 | 7 | 3 | yes | no |
| 14 | 16 | `touch_prot_last=na` | 3 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8408 | 0.504 | - | 1.000 | - | 16 | 15 | 13 | 24 | 0 | no | no |
| 15 | 20 | `card_read=HUNT` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 13 | 12 | 11 | 13 | 0 | no | no |
| 16 | 19 | `fz_entered_read=FIRST_PRINT` | 2 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 14 | 13 | 12 | 14 | 0 | no | no |
| 17 | 21 | `csw_sign_dir` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 11 | 11 | 10 | 11 | 0 | no | no |
| 18 | 18 | `fz_branch=watch` | 2 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 15 | 14 | 14 | 23 | 0 | no | no |
| 19 | 26 | `fz_entered_read=RECYCLE` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 19 | 19 | 6 | 19 | 1 | no | no |
| 20 | 25 | `fz_entered_read=HUNT` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 10 | 7 | 15 | 10 | 1 | no | no |
| 21 | 24 | `fz_entered_read=ACCEPTED` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 9 | 9 | 16 | 9 | 0 | no | no |
| 22 | 23 | `fz_block_reason=hunt_fade` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 12 | 10 | 9 | 12 | 0 | no | no |
| 23 | 29 | `fz_take_why=defend_wrong_half` | 1 | 0.00000 | 0.00000 | - | no | - | - | no | 0.0000 | 0.8421 | 0.501 | - | 1.000 | - | 18 | 18 | 18 | 15 | 0 | no | no |
| 24 | 34 | `last_bos_dir=down` | 1 | -0.00000 | 0.00004 | -0.08 | no | - | - | no | 0.0002 | 0.8421 | 0.497 | - | 1.000 | - | 25 | 5 | 26 | 6 | 2 | no | no |
| 25 | 31 | `hour_bin=11` | 1 | -0.00000 | 0.00002 | -0.29 | no | - | - | no | 0.0001 | 0.8382 | 0.513 | 129.3 | 0.862 | 44.7 | 28 | 21 | 21 | 18 | 0 | no | no |
| 26 | 32 | `hour_bin=12` | 1 | -0.00001 | 0.00002 | -0.62 | no | - | - | no | 0.0002 | 0.8386 | 0.518 | 203.9 | 0.834 | 30.8 | 27 | 27 | 28 | 27 | 0 | no | no |
| 27 | 22 | `fz_band_width` | 1 | -0.00003 | 0.00015 | -0.18 | no | - | - | no | 0.0025 | 0.8332 | 0.498 | -773.8 | 0.994 | 16.6 | 30 | 28 | 5 | 26 | 1 | no | no |
| 28 | 36 | `touch_prot_last=pending` | 1 | -0.00003 | 0.00007 | -0.50 | no | - | - | no | 0.0007 | 0.8367 | 0.510 | - | 1.000 | - | 26 | 30 | 25 | 5 | 1 | no | no |
| 29 | 17 | `dow` | 2 | -0.00005 | 0.00021 | -0.24 | no | - | - | no | 0.0060 | 0.8415 | 0.488 | -149.9 | 0.965 | 50.0 | 31 | 4 | 3 | 29 | 2 | no | no |
| 30 | 6 | `swing_near_kind=H` | 15 | -0.00006 | 0.00053 | -0.11 | no | - | - | no | 0.0213 | 0.8001 | 0.539 | - | 1.000 | - | 4 | 31 | 33 | 3 | 2 | no | no |
| 31 | 12 | `dir=down` | 6 | -0.00011 | 0.00013 | -0.84 | no | - | - | no | 0.0021 | 0.8158 | 0.551 | 215.5 | 0.993 | 48.1 | 32 | 29 | 30 | 4 | 1 | no | no |
| 32 | 10 | `last_sl_bars_ago` | 8 | -0.00022 | 0.00076 | -0.28 | no | - | - | no | 0.0243 | 0.8100 | 0.510 | -216.3 | 0.987 | 33.4 | 34 | 6 | 29 | 32 | 1 | no | no |
| 33 | 5 | `fz_watch_kind=WATCH` | 20 | -0.00039 | 0.00089 | -0.43 | no | - | - | no | 0.0126 | 0.8046 | 0.566 | -106.0 | 0.932 | 1.0 | 33 | 33 | 31 | 31 | 0 | no | no |
| 34 | 3 | `n_bos_since_choch` | 22 | -0.00096 | 0.00233 | -0.41 | no | - | - | no | 0.0592 | 0.7958 | 0.540 | 33.1 | 0.922 | 3.6 | 1 | 34 | 34 | 33 | 1 | no | no |
| 35 | 2 | `n_choch_since_bos` | 23 | -0.00274 | 0.00252 | -1.09 | no | - | - | no | 0.1153 | 0.7852 | 0.541 | -29.7 | 0.959 | 28.1 | 35 | 35 | 35 | 35 | 0 | no | no |
| 36 | 1 | `n_events_today` | 25 | -0.00711 | 0.00633 | -1.12 | no | - | - | no | 0.1522 | 0.7741 | 0.567 | 105.0 | 0.903 | 35.7 | 38 | 37 | 36 | 36 | 0 | no | no |
| 37 | 0 | `hour_bin=<09:25` | 61 | -0.00937 | 0.00967 | -0.97 | no | - | - | no | 0.3318 | 0.7634 | 0.596 | -2935.8 | 0.998 | 9.1 | 37 | 36 | 37 | 37 | 0 | no | no |
| 38 | 4 | `card_leave_kind=normal` | 21 | -0.01163 | 0.01219 | -0.95 | no | - | - | no | 0.2170 | 0.7776 | 0.577 | -16.5 | 0.866 | 0.0 | 36 | 38 | 38 | 38 | 0 | no | no |

Reading the table: 0 of 38 clusters pass the MDA rule (mean > std across the 12 folds). 18 clusters have an MDA of exactly 0 in every fold: the forest never split on any of their members (single one-hot levels or rare flags under min_weight_fraction_leaf 0.05 with balanced class weights), so permuting them changes nothing; 15 clusters have a negative mean MDA (permuting them lowers the OOF weighted log-loss), 5 a positive one. The best cluster is 7 (`card_read=PENDING`, 13 members) with mean 0.00030 against std 0.00059 (ratio 0.50), positive in 9 of 12 folds. The large clusters, the ones the forest actually splits on (MDI), all sit at a negative log-loss MDA: cluster 0 (`hour_bin=<09:25`, 61 members, MDI 0.332) -0.00937 +- 0.00967; cluster 1 (`n_events_today`, 25 members, MDI 0.152) -0.00711 +- 0.00633; cluster 2 (`n_choch_since_bos`, 23 members, MDI 0.115) -0.00274 +- 0.00252; cluster 3 (`n_bos_since_choch`, 22 members, MDI 0.059) -0.00096 +- 0.00233; cluster 4 (`card_leave_kind=normal`, 21 members, MDI 0.217) -0.01163 +- 0.01219; cluster 5 (`fz_watch_kind=WATCH`, 20 members, MDI 0.013) -0.00039 +- 0.00089; cluster 6 (`swing_near_kind=H`, 15 members, MDI 0.021) -0.00006 +- 0.00053; cluster 7 (`card_read=PENDING`, 13 members, MDI 0.019) +0.00030 +- 0.00059. The supplementary diagnostic below asks whether that is 'no ranking information' or a calibration effect of the balanced-weight forest; either way the pre-registered rule is the log-loss one and no cluster passes it.

Stability: periods 2022 (1428 rows, 243 winners), 2023 (1096 rows, 146 winners), 2024 (840 rows, 134 winners), 2025 (1088 rows, 171 winners); rule top-8 in >= 3 of 4 periods; Spearman rank correlation of the cluster MDA vectors across periods: 2022|2023: 0.2705, 2022|2024: 0.4746, 2022|2025: 0.4459, 2023|2024: 0.4432, 2023|2025: 0.2884, 2024|2025: 0.2302. 5 clusters pass the stability filter, but with 33 of 38 clusters at a mean MDA <= 0 a cluster whose MDA is exactly 0 in every fold ranks inside the top 8 of a period by default (its rank is a tie among zeros above the negative clusters), so the stability column is meaningful only together with the MDA pass, which no cluster achieves; the filter is applied as the conjunction the design specifies.

### Supplementary diagnostic (not the pass rule; `mda_diag.py`, from the saved OOF arrays, no refit, no ledger row)

| item | value |
|---|---|
| log-loss MDA recomputed from `oof_minute.npz` vs the table | max abs diff 7.64e-10 (agree) |
| full model OOF AUC, pooled / per-fold mean +- std | 0.5935 / 0.5841 +- 0.0567 |
| mean OOF probability vs winner share (unweighted / |net|-weighted) | 0.5261 vs 0.1559 / 0.2185 |
| OOF weighted log-loss: model vs the constant predictor at the weighted winner share | 0.74474 vs 0.52502 (the constant is better: the forest is mis-calibrated under balanced class weights) |
| clusters passing an AUC-drop version of the same rule (mean drop > std across folds) | 2 of 38 |
| clusters with negative / exactly-zero log-loss MDA | 15 / 0 |

| AUC rank | cluster | representative | AUC drop mean | std | ratio | folds positive | pooled-OOF AUC drop | log-loss MDA mean |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | `hour_bin=<09:25` | 0.0300 | 0.0165 | 1.82 | 12 | 0.0225 | -0.00937 |
| 2 | 4 | `card_leave_kind=normal` | 0.0200 | 0.0396 | 0.50 | 9 | 0.0268 | -0.01163 |
| 3 | 3 | `n_bos_since_choch` | 0.0040 | 0.0068 | 0.59 | 10 | 0.0027 | -0.00096 |
| 4 | 13 | `card_read=FIRST_PRINT` | 0.0008 | 0.0008 | 1.09 | 12 | 0.0003 | +0.00008 |
| 5 | 10 | `last_sl_bars_ago` | 0.0003 | 0.0025 | 0.13 | 8 | 0.0009 | -0.00022 |

Full table: `mda_diag_minute.csv`. Reading: the constant predictor at the weighted winner share beats the forest in weighted log-loss, so the OOF probabilities are mis-calibrated (balanced class weights centre them near 0.5 while the weighted winner share is 0.2185); permuting a cluster the forest splits on shrinks its predictions toward the centre, which lowers the log-loss even where the ranking degrades. The AUC drop asks the ranking question alone: 2 cluster(s) would pass a mean > std rule on it, and the pooled OOF AUC of the whole forest is 0.5935. This diagnostic is reported for the reader's judgement of the null; it is not the pre-registered statistic, it changes no rank in the shortlist rule, and it proposes nothing.

Orthogonal check: 276 components (139 carry 95% of the variance); weighted Kendall tau between the MDI of the PC-score forest and the eigenvalues = **0.4059** (Kendall tau 0.2624, p 1.54e-10). The MDI ranking follows the variance structure of the features.

### Cluster membership

| cluster | representative (tier; why) | members |
|---|---|---|
| 0 | `hour_bin=<09:25` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.255) | `hour_bin=09`, `hour_bin=<09:25`, `sl_dist_pts`, `sl_dist_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir=none`, `hv2_dir_agree`, `hv2_ratio`, `hv3_dir=none`, `hv3_dir_agree`, `hv3_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `touch_room_last=none`, `touch_swing_last=broke`, `today_net_asof`, `today_pts_asof`, `last_closed_reason_asof=nan`, `card_leave_kind=gap`, `fz_block_reason=open_pierce`, `fz_take_why=leave_gap_quiet`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `bocpd_rng_h60_p10`, `bocpd_rng_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `ret_1h_pts__na`, `er_1h__na`, `hv2_bars_since__na`, `hv3_bars_since__na`, `hv3_low_held__na`, `vol_ratio20_at_choch__na`, `vol_max_ratio20_choch_to_k__na`, `touch_room_bars_ago__na`, `last_closed_net_asof__na`, `csw_max_abs__na` |
| 1 | `n_events_today` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.421) | `session_bar`, `hour`, `hour_bin=13`, `hour_bin=14`, `hour_bin=15`, `choch_same_session`, `range_3h_atr`, `sess_range_atr`, `last_bos_same_session`, `n_events_today`, `n_choch_today`, `n_bos_today`, `today_n_closed_asof`, `today_n_stops_asof`, `last_closed_net_asof`, `last_closed_reason_asof=next_choch`, `bocpd_ret_h60_map`, `bocpd_ret_h60_since_reset`, `bocpd_ret_h240_map`, `bocpd_ret_h240_since_reset`, `bocpd_rng_h60_map`, `bocpd_rng_h60_since_reset`, `bocpd_rng_h240_map`, `bocpd_rng_h240_since_reset`, `win_range_slope` |
| 2 | `n_choch_since_bos` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.370) | `n_choch_since_bos`, `bars_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `n_choch_1h`, `n_choch_3h`, `touch_prot_n`, `touch_swing_n`, `last_closed_reason_asof=stop_loss`, `bsadf_close_win`, `cusum_bars_since`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump3_state`, `jump4_state`, `nn_dist_prefix_short`, `p1_dist_prefix_short`, `nn_dist_prefix_long`, `p1_dist_prefix_long` |
| 3 | `n_bos_since_choch` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.457) | `bars_since_choch`, `n_bos_since_choch`, `alt_kind6`, `n_bos_1h`, `n_bos_3h`, `hv2_bars_since`, `hv3_bars_since`, `swing_ahead_dist_atr`, `n_swings_1h`, `touch_room_n`, `touch_room_last=pending`, `touch_swing_last=pending`, `touch_swing_bars_ago`, `rv_ev36`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3`, `win_dd_extreme_atr` |
| 4 | `card_leave_kind=normal` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.288) | `days_to_expiry`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_3h_pts`, `sess_cumvol_ratio20s`, `sess_vol_vs_prev_sess`, `n_rooms_alive`, `card_read=LEAVE`, `card_leave_side=down`, `card_leave_side=up`, `card_leave_kind=normal`, `fz_gate=TAKE`, `fz_block_reason=leave_into_recycle`, `fz_branch=leave`, `fz_take_why=leave_vol_fail`, `fz_entered_read=THIN`, `card_bars_since_reject`, `cusum_events_60`, `rv_range36_atr` |
| 5 | `fz_watch_kind=WATCH` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.311) | `card_visit_n`, `card_read=RECYCLE`, `card_read=REJECT`, `card_read=THIN`, `card_out_side=nan`, `card_last_hunt_dir=down`, `card_last_hunt_dir=up`, `card_last_reject_dir=down`, `card_last_reject_dir=up`, `card_cluster_sit`, `card_last_leave_failed`, `card_touches`, `fz_zone_kind=B`, `fz_gate=WATCH`, `fz_block_reason=nan`, `fz_branch=nan`, `fz_watch_kind=WATCH`, `fz_band_width_atr`, `fz_dist_band_edge_ahead`, `card_in_room` |
| 6 | `swing_near_kind=H` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.503) | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `hv3_low_held`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_out_side=up`, `fz_pos_in_band`, `ffd_close_dstar_z60`, `rv_ret36_atr` |
| 7 | `card_read=PENDING` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.431) | `room_ahead_dist_atr`, `touch_room_last=broke`, `card_this_bars`, `card_read=PENDING`, `card_out_run`, `card_out_side=down`, `fz_take_why=nan`, `fz_entered_read=nan`, `fz_watch_kind=WATCH_EDGE`, `fz_pos_in_band_dir`, `fz_dist_band_edge_behind`, `card_vol_ratio`, `room_ahead_dist_atr__na` |
| 8 | `last_bos_dir=none` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.594) | `last_bos_dir=none`, `gap_pts__na`, `bars_since_bos__na`, `bars_since_prev_choch__na`, `sess_cumvol_ratio20s__na`, `ffd_close_dstar__na`, `bsadf_close__na`, `bocpd_ret_h60_since_reset__na`, `nn_dist_prefix_long__na` |
| 9 | `card_last_reject_dir=nan` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.500) | `room_behind_dist_atr`, `card_read=NEW`, `card_last_hunt_dir=nan`, `card_last_reject_dir=nan`, `fz_gate=BLOCK`, `fz_block_reason=new`, `room_behind_dist_atr__na`, `card_visit_n__na`, `card_bars_since_reject__na` |
| 10 | `last_sl_bars_ago` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.160) | `bars_since_prev_choch`, `last_sh_bars_ago`, `last_sl_bars_ago`, `touch_prot_last=held`, `touch_prot_bars_ago`, `jump3_run`, `jump4_run`, `win_sign_agree10` |
| 11 | `card_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.292) | `room_edge_dist_dir_atr`, `touch_room_last=held`, `touch_room_bars_ago`, `card_read=ACCEPTED`, `fz_level_in_band`, `fz_branch=defend`, `fz_take_why=accepted_no_defend` |
| 12 | `dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.537) | `dir=down`, `last_choch_dir=down`, `hv2_dir=down`, `hv3_dir=down`, `hv3_high_held`, `dist_sh_atr` |
| 13 | `card_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.502) | `card_first_bars`, `card_read=FIRST_PRINT`, `fz_branch=first_print`, `fz_take_why=first_print_against` |
| 14 | `hv3_dir=flat` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.201) | `hv2_dir=flat`, `hv3_dir=flat`, `touch_prot_last=none` |
| 15 | `n_events_asof` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.936) | `sl`, `n_events_asof`, `ffd_close_dstar` |
| 16 | `touch_prot_last=na` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.996) | `touch_prot_last=na`, `dist_prot_dir_atr__na`, `touch_prot_bars_ago__na` |
| 17 | `dow` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.068) | `dow`, `gap_pts` |
| 18 | `fz_branch=watch` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.963) | `fz_gate=REENTER`, `fz_branch=watch` |
| 19 | `fz_entered_read=FIRST_PRINT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 0.111) | `fz_take_why=leave_against`, `fz_entered_read=FIRST_PRINT` |
| 20 | `card_read=HUNT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `card_read=HUNT` |
| 21 | `csw_sign_dir` (tier 0 (integer/boolean/one-hot/card field), coverage 0.982, mean |rho| to members 1.000) | `csw_sign_dir` |
| 22 | `fz_band_width` (tier 2 (raw points/level), coverage 0.734, mean |rho| to members 1.000) | `fz_band_width` |
| 23 | `fz_block_reason=hunt_fade` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_block_reason=hunt_fade` |
| 24 | `fz_entered_read=ACCEPTED` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=ACCEPTED` |
| 25 | `fz_entered_read=HUNT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=HUNT` |
| 26 | `fz_entered_read=RECYCLE` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=RECYCLE` |
| 27 | `fz_entered_read=REJECT` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_entered_read=REJECT` |
| 28 | `fz_take_why=defend_opposite_in_visit` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_take_why=defend_opposite_in_visit` |
| 29 | `fz_take_why=defend_wrong_half` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `fz_take_why=defend_wrong_half` |
| 30 | `hour_bin=10` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=10` |
| 31 | `hour_bin=11` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=11` |
| 32 | `hour_bin=12` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=12` |
| 33 | `hour_bin=>=15:20` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `hour_bin=>=15:20` |
| 34 | `last_bos_dir=down` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `last_bos_dir=down` |
| 35 | `touch_prot_last=broke` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_prot_last=broke` |
| 36 | `touch_prot_last=pending` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_prot_last=pending` |
| 37 | `touch_swing_last=held` (tier 0 (integer/boolean/one-hot/card field), coverage 1.000, mean |rho| to members 1.000) | `touch_swing_last=held` |

### Interactions (xgboost on the top-40 features by clustered MDA; OOF weighted log-loss 0.74727, OOF AUC 0.5338)

| rank | feature a | feature b | mean abs SHAP interaction (OOF rows) | paths with both | split a (gain-weighted median) | split b | common splits a | common splits b |
|---|---|---|---|---|---|---|---|---|
| 1 | `sl` | `ffd_close_dstar` | 0.038240 | 328 | 24640.0000 | 2.5029 | [24661.0, 24655.0, 24640.0] | [2.5142, 2.4166, 2.4046] |
| 2 | `sl` | `n_events_asof` | 0.031623 | 294 | 24640.0000 | 23656.0000 | [26025.8008, 18146.0, 24651.1992] | [28203.0, 32889.0, 18033.0] |
| 3 | `card_this_bars` | `sl` | 0.027015 | 169 | 11.0000 | 18127.8496 | [11.0, 6.0, 3.0] | [24661.0, 18127.8496, 26025.0] |
| 4 | `room_ahead_dist_atr` | `room_behind_dist_atr` | 0.022748 | 761 | 0.9548 | 0.6324 | [17.8071, 14.4066, 0.0125] | [9.3641, 0.18, 0.5243] |
| 5 | `card_vol_ratio` | `room_behind_dist_atr` | 0.019978 | 442 | 0.0691 | 0.1800 | [0.0289, 0.0493, 0.0691] | [0.18, 0.1561, 0.006] |

Pairs that involve a calendar-time proxy (a price level or a cumulative count that trends over the four years; a split on it separates periods, not trade contexts): `sl` x `ffd_close_dstar` **calendar-time proxy**: `sl` = the Foundation stop price (a price level); `ffd_close_dstar` = FFD of log close at d* = 0.2 (keeps most of the level); `sl` x `n_events_asof` **calendar-time proxy**: `sl` = the Foundation stop price (a price level); `n_events_asof` = cumulative engine events since the tape start; `card_this_bars` x `sl` **calendar-time proxy**: `sl` = the Foundation stop price (a price level). Such a pair is listed because the design ranks by mean |SHAP interaction|, but a gate study that uses it must show the rule holds inside every period.

All ranked pairs: `interaction_pairs_minute.csv`; the full mean |interaction| matrix: `shap_interactions_minute.csv`. The gate studies may use only these five pairs as depth-2/3 conjunctions (and only where both features are shortlisted columns: none of the five lies inside the shortlist).

### Do the H2 CHoCH counts and the state-model posteriors share a cluster?

| H2 count column | cluster |
|---|---|
| `n_choch_since_bos` | 2 |
| `n_choch_since_bos_today` | 2 |
| `alt_dir6` | 2 |
| `alt_kind6` | 3 |

| state-model column | cluster |
|---|---|
| `gmm3_p0` | 2 |
| `gmm3_p1` | 3 |
| `gmm3_p2` | 0 |
| `gmm3_map` | 0 |
| `gmm4_p0` | 3 |
| `gmm4_p1` | 2 |
| `gmm4_p2` | 3 |
| `gmm4_p3` | 0 |
| `gmm4_map` | 0 |
| `hmm3_p0` | 2 |
| `hmm3_p1` | 3 |
| `hmm3_p2` | 0 |
| `hmm3_map` | 0 |
| `hmm3_map_run` | 2 |
| `hmm4_p0` | 3 |
| `hmm4_p1` | 3 |
| `hmm4_p2` | 2 |
| `hmm4_p3` | 3 |
| `hmm4_map` | 0 |
| `hmm4_map_run` | 2 |
| `jump3_state` | 2 |
| `jump3_run` | 10 |
| `jump4_state` | 2 |
| `jump4_run` | 10 |

**Yes, in part**: cluster 2 holds `n_choch_since_bos`, `n_choch_since_bos_today`, `alt_dir6`, `gmm3_p0`, `gmm4_p1`, `hmm3_p0`, `hmm3_map_run`, `hmm4_p2`, `hmm4_map_run`, `jump3_state`, `jump4_state`; cluster 3 holds `alt_kind6`, `gmm3_p1`, `gmm4_p0`, `gmm4_p2`, `hmm3_p1`, `hmm4_p0`, `hmm4_p1`, `hmm4_p3`. Where an HMM / GMM / jump posterior sits in the same cluster as `n_choch_since_bos`, the state model adds nothing the count does not already say (Judge 1 of regime-states): no HMM gate is run later for those states.

### FFD columns

| ffd column | cluster |
|---|---|
| `ffd_close_dstar` | 15 |
| `ffd_close_dstar_z60` | 6 |
| `ffd_vol_dstar` | 0 |
| `ffd_vol_dstar_z60` | 0 |
| `ffd_close_dstar__na` | 8 |

| cluster | members | MDA ll mean | std | pass | stable | mixed with non-FFD columns |
|---|---|---|---|---|---|---|
| 0 | `hour_bin=09`, `hour_bin=<09:25`, `sl_dist_pts`, `sl_dist_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir=none`, `hv2_dir_agree`, `hv2_ratio`, `hv3_dir=none`, `hv3_dir_agree`, `hv3_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `touch_room_last=none`, `touch_swing_last=broke`, `today_net_asof`, `today_pts_asof`, `last_closed_reason_asof=nan`, `card_leave_kind=gap`, `fz_block_reason=open_pierce`, `fz_take_why=leave_gap_quiet`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `bocpd_rng_h60_p10`, `bocpd_rng_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `ret_1h_pts__na`, `er_1h__na`, `hv2_bars_since__na`, `hv3_bars_since__na`, `hv3_low_held__na`, `vol_ratio20_at_choch__na`, `vol_max_ratio20_choch_to_k__na`, `touch_room_bars_ago__na`, `last_closed_net_asof__na`, `csw_max_abs__na` | -0.00937 | 0.00967 | no | no | yes |
| 6 | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `hv3_low_held`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_out_side=up`, `fz_pos_in_band`, `ffd_close_dstar_z60`, `rv_ret36_atr` | -0.00006 | 0.00053 | no | no | yes |
| 8 | `last_bos_dir=none`, `gap_pts__na`, `bars_since_bos__na`, `bars_since_prev_choch__na`, `sess_cumvol_ratio20s__na`, `ffd_close_dstar__na`, `bsadf_close__na`, `bocpd_ret_h60_since_reset__na`, `nn_dist_prefix_long__na` | 0.00000 | 0.00000 | no | yes | yes |
| 15 | `sl`, `n_events_asof`, `ffd_close_dstar` | 0.00002 | 0.00005 | no | no | yes |

### The shortlist (0 clusters; 0 of 38 pass MDA, 5 pass stability, 0 pass both; cap 8)

Frozen at `features_shortlist/minute/shortlist.json`, sha256 `66f6e004bd93e47c55ca219785a9a30f36d618cbbbd215cfcbad5a44412b5bdb`, registered in `ledger/registrations.jsonl`. Allowed columns for the gate studies: 0.

**Empty**: no cluster passes both the MDA rule and the stability filter on this timeframe (none passes the MDA rule alone). The gate studies have no shortlisted column here; a null vocabulary is a result, not a failure of the pipeline. Consequence under the frozen rule: the downstream gate studies (gate_family, llm_round1, regime_gate) may not draw features on this timeframe from this study's vocabulary; any re-opening of the vocabulary (a weaker rule, a different statistic, a different model) is a user decision that would be a new registration with its own sha and the multiplicity carried forward, never an edit of this one. For that decision only, the clusters with a positive mean MDA (none exceeds its std): cluster 7 `card_read=PENDING` (13 members) +0.00030 +- 0.00059, ratio 0.50, top-8 in 3 periods; cluster 11 `card_read=ACCEPTED` (7 members) +0.00016 +- 0.00048, ratio 0.33, top-8 in 3 periods; cluster 13 `card_read=FIRST_PRINT` (4 members) +0.00008 +- 0.00011, ratio 0.67, top-8 in 3 periods; cluster 15 `n_events_asof` (3 members) +0.00002 +- 0.00005, ratio 0.36, top-8 in 2 periods; cluster 9 `card_last_reject_dir=nan` (9 members) +0.00001 +- 0.00025, ratio 0.06, top-8 in 1 periods. These are NOT allowed columns.


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
| run | one single-thread process (--stage all, started before the stage split): 3682 s (05:14-06:15 UTC), finalize included. Max RSS 391 MB. |

### The full bagged model (ceiling; not a candidate)

| depth | OOF weighted log-loss | OOF AUC | gate kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | perm p | control pct | loser recall | weighted winner recall | top-decile winners skipped | sign blocks | kept mean slip 8 | ledger id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 (main) | 0.72748 | 0.4974 | 819 | 0.9915 | -750.12 | -1568.06 | 817.94 | 599.47 | 0.6292 | 88.4 | 0.0084 | 0.9967 | 0.0000 | 1 | -1140.09 | `1a12e823ea7cf4c7` |
| 3 | 0.7388 | 0.4939 | - | 0.9915 | - | - | 817.94 | - | 0.6232 | 88.6 | - | - | - | - | - | `4f227fe28b9c61a8` |
| 5 | 0.71863 | 0.5004 | - | 0.9976 | - | - | -626.91 | - | 0.8501 | 49.5 | - | - | - | - | - | `246d743c0ec34f2f` |

In 11 of 12 folds the OOF gate kept every test row (a '-' in the gate columns = nothing skipped, the difference is undefined). In 10 folds the training-fold rule chose the grid floor tau = 0.05: on the training fold's OOB probabilities no threshold that kept >= 90% of the |net|-weighted winner net had a higher kept mean than keeping everything; in the other 2 fold(s) (tau [0.36, 0.37]) the test probabilities mostly lay above it. The full model's OOF gate is therefore close to 'take everything' and its kept-vs-skipped numbers, where defined, are a ceiling of no practical value.

Per fold (depth 4): tau chosen on the training fold's OOB probabilities.

| fold | n train | n test | |net| cap (train p99) | tau | OOF weighted log-loss | OOF diff | kept share |
|---|---|---|---|---|---|---|---|
| 0 | 741 | 82 | 16029.2 | 0.05 | 0.72312 | - | 1.0000 |
| 1 | 741 | 83 | 14989.1 | 0.37 | 0.70687 | 1366.55 | 0.9157 |
| 2 | 784 | 42 | 16746.1 | 0.05 | 0.68526 | - | 1.0000 |
| 3 | 742 | 76 | 17645.5 | 0.05 | 0.74704 | - | 1.0000 |
| 4 | 754 | 72 | 17388.5 | 0.05 | 0.72101 | - | 1.0000 |
| 5 | 747 | 73 | 17538.4 | 0.05 | 0.76038 | - | 1.0000 |
| 6 | 745 | 77 | 15993.9 | 0.05 | 0.71142 | - | 1.0000 |
| 7 | 775 | 51 | 14972.0 | 0.05 | 0.6948 | - | 1.0000 |
| 8 | 747 | 76 | 15251.0 | 0.05 | 0.74818 | - | 1.0000 |
| 9 | 746 | 80 | 15279.1 | 0.05 | 0.75725 | - | 1.0000 |
| 10 | 794 | 31 | 16532.0 | 0.36 | 0.78761 | - | 1.0000 |
| 11 | 743 | 83 | 17624.1 | 0.05 | 0.6974 | - | 1.0000 |

CPCV of the full model's OOF gate (66 splits, 11 paths, family `importance/full_model/cpcv`): diff median 259.06, 5th percentile -314.33, min -352.25, share of paths with diff > 0 0.364, kept share median 0.9915, control pct median 56.0 / p5 38.2.

Family `importance/*` on 5minute (53 ledger rows: full model x3 depths, 39 SFI clusters, 11 CPCV paths): PBO (diff) 0.0267 (IS-best below zero OOS 0.7488); SPA studentised p 0.0345 (RC p 0.0345, best mean gain 155.98 INR/session, 43 candidates excluded for < 20 active sessions), SPA unstudentised p 0.014 (RC p 0.014, best mean gain 155.98); effective trials 1.04; full model: bootstrap 90% CI of diff [-11.94, 3374.62], kept mean CI [-997.83, -496.90], DSR p 1.0; go/no-go passed = False (kept_share>=20%=ok, kept_n>=80=ok, diff>0=ok, diff_top1_removed>0=ok, kept_mean_slip8>0=FAIL, sign_blocks>=8/12=FAIL, control_pct>=95=FAIL, cpcv_p5_diff>0=FAIL, pbo<=0.2=ok, dsr_p<0.1=FAIL, spa_p<=0.10=ok, boot_ci_excludes_0=FAIL). The family exists for the ledger's PBO / SPA bookkeeping; none of its rows is a candidate.

### Clustered importance table (all clusters, sorted by log-loss MDA)

Full table with members, per-period MDA values and SFI ledger ids: `importance_clusters_5minute.csv`; per-feature MDI, tier, coverage and README definition: `importance_features_5minute.csv`.

| rank | cluster | representative | n | MDA ll mean | std | ratio | pass | MDA diff mean | std | pass | MDI | SFI ll | SFI AUC | SFI diff | SFI kept | SFI ctrl pct | rank H1_2021-10..2023-09 | rank H2_2023-10..2025-12 | top-8 periods | stable | eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 17 | `touch_room_last=broke` | 4 | 0.00177 | 0.00710 | 0.25 | no | 1713.1 | - | no | 0.0421 | 0.7613 | 0.532 | 897.1 | 0.903 | 97.5 | 1 | 5 | 2 | yes | no |
| 2 | 7 | `fz_gate=TAKE` | 6 | 0.00050 | 0.00499 | 0.10 | no | -114.1 | - | no | 0.0254 | 0.7816 | 0.517 | - | 1.000 | - | 25 | 24 | 0 | no | no |
| 3 | 12 | `card_read=LEAVE` | 5 | 0.00021 | 0.00160 | 0.13 | no | -59.1 | - | no | 0.0084 | 0.7794 | 0.535 | - | 1.000 | - | 32 | 3 | 1 | no | no |
| 4 | 22 | `days_to_expiry` | 2 | 0.00009 | 0.00098 | 0.10 | no | 0.0 | - | no | 0.0107 | 0.7796 | 0.498 | 501.6 | 0.993 | 46.7 | 3 | 31 | 1 | no | no |
| 5 | 16 | `touch_prot_last=held` | 4 | 0.00000 | 0.00355 | 0.00 | no | -40.2 | - | no | 0.0301 | 0.7831 | 0.494 | -2505.9 | 0.992 | 8.9 | 28 | 4 | 1 | no | no |
| 6 | 21 | `n_events_asof` | 3 | 0.00000 | 0.00037 | 0.00 | no | 0.0 | - | no | 0.0165 | 0.7732 | 0.482 | - | 1.000 | - | 23 | 7 | 1 | no | no |
| 7 | 8 | `gap_pts__na` | 6 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 4 | 8 | 2 | yes | no |
| 8 | 38 | `touch_prot_last=broke` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 19 | 18 | 0 | no | no |
| 9 | 35 | `hv2_dir=flat` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 18 | 19 | 0 | no | no |
| 10 | 37 | `room_behind_dist_atr__na` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 17 | 21 | 0 | no | no |
| 11 | 31 | `fz_entered_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 6 | 14 | 1 | no | no |
| 12 | 27 | `card_read=FIRST_PRINT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 11 | 11 | 0 | no | no |
| 13 | 28 | `card_read=REJECT` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 8 | 17 | 1 | no | no |
| 14 | 26 | `touch_swing_last=none` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 10 | 10 | 0 | no | no |
| 15 | 19 | `card_read=ACCEPTED` | 3 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 14 | 12 | 0 | no | no |
| 16 | 15 | `fz_block_reason=hunt_fade` | 4 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7842 | 0.527 | - | 1.000 | - | 7 | 13 | 1 | no | no |
| 17 | 32 | `fz_gate=REENTER` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 16 | 20 | 0 | no | no |
| 18 | 30 | `fz_entered_read=ACCEPTED` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 12 | 16 | 0 | no | no |
| 19 | 29 | `csw_sign_dir` | 1 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 13 | 15 | 0 | no | no |
| 20 | 24 | `card_read=RECYCLE` | 2 | 0.00000 | 0.00000 | - | no | 0.0 | - | no | 0.0000 | 0.7853 | 0.534 | - | 1.000 | - | 9 | 9 | 0 | no | no |
| 21 | 33 | `hour_bin=10` | 1 | -0.00001 | 0.00002 | -0.34 | no | 0.0 | - | no | 0.0001 | 0.7851 | 0.533 | - | 1.000 | - | 20 | 23 | 0 | no | no |
| 22 | 18 | `touch_prot_last=na` | 4 | -0.00003 | 0.00010 | -0.27 | no | 0.0 | - | no | 0.0002 | 0.7841 | 0.518 | 150.3 | 0.920 | 78.5 | 5 | 25 | 1 | no | no |
| 23 | 36 | `last_bos_dir=down` | 1 | -0.00003 | 0.00009 | -0.30 | no | 0.0 | - | no | 0.0002 | 0.7849 | 0.498 | - | 1.000 | - | 21 | 22 | 0 | no | no |
| 24 | 34 | `hour_bin=11` | 1 | -0.00004 | 0.00015 | -0.27 | no | 0.0 | - | no | 0.0002 | 0.7868 | 0.525 | -630.6 | 0.932 | 8.3 | 15 | 26 | 0 | no | no |
| 25 | 1 | `n_events_today` | 26 | -0.00015 | 0.01112 | -0.01 | no | 1084.8 | - | no | 0.1275 | 0.7448 | 0.529 | -397.4 | 0.956 | 64.0 | 36 | 1 | 1 | no | no |
| 26 | 13 | `last_choch_dir=down` | 5 | -0.00031 | 0.00059 | -0.53 | no | 93.6 | - | no | 0.0054 | 0.7685 | 0.553 | 738.7 | 0.909 | 58.6 | 24 | 27 | 0 | no | no |
| 27 | 11 | `fz_block_reason=new` | 6 | -0.00038 | 0.00188 | -0.20 | no | 138.7 | - | no | 0.0182 | 0.7715 | 0.502 | 335.8 | 0.908 | 61.9 | 31 | 30 | 0 | no | no |
| 28 | 5 | `n_bos_since_choch` | 14 | -0.00043 | 0.00134 | -0.32 | no | 0.0 | - | no | 0.0230 | 0.7702 | 0.490 | -514.2 | 0.966 | 69.4 | 29 | 32 | 0 | no | no |
| 29 | 10 | `touch_swing_last=pending` | 6 | -0.00044 | 0.00113 | -0.39 | no | 0.0 | - | no | 0.0075 | 0.7655 | 0.518 | 82.0 | 0.983 | 49.0 | 27 | 28 | 0 | no | no |
| 30 | 20 | `touch_prot_last=pending` | 3 | -0.00057 | 0.00093 | -0.61 | no | 0.0 | - | no | 0.0039 | 0.7795 | 0.498 | -2442.2 | 0.976 | 6.1 | 26 | 33 | 0 | no | no |
| 31 | 6 | `fz_watch_kind=WATCH` | 12 | -0.00058 | 0.00400 | -0.14 | no | 137.8 | - | no | 0.0356 | 0.7579 | 0.509 | -270.4 | 0.921 | 27.4 | 30 | 34 | 0 | no | no |
| 32 | 4 | `swing_near_kind=H` | 16 | -0.00074 | 0.00790 | -0.09 | no | 98.4 | - | no | 0.1057 | 0.7518 | 0.528 | 357.6 | 0.937 | 68.7 | 2 | 36 | 1 | no | no |
| 33 | 25 | `jump3_run` | 2 | -0.00104 | 0.00242 | -0.43 | no | 0.0 | - | no | 0.0091 | 0.7925 | 0.478 | 827.0 | 0.868 | 100.0 | 34 | 29 | 0 | no | no |
| 34 | 23 | `dow` | 2 | -0.00105 | 0.00488 | -0.21 | no | 0.0 | - | no | 0.0169 | 0.7727 | 0.528 | -1522.3 | 0.983 | 50.0 | 37 | 6 | 1 | no | no |
| 35 | 14 | `touch_room_last=held` | 5 | -0.00108 | 0.00147 | -0.73 | no | 134.4 | - | no | 0.0237 | 0.7553 | 0.532 | -4678.7 | 0.990 | 17.2 | 33 | 35 | 0 | no | no |
| 36 | 2 | `hv2_dir=none` | 18 | -0.00141 | 0.00791 | -0.18 | no | 253.0 | - | no | 0.0604 | 0.7652 | 0.515 | -775.6 | 0.975 | 2.6 | 38 | 2 | 1 | no | no |
| 37 | 9 | `cusum_events_60` | 6 | -0.00142 | 0.00668 | -0.21 | no | 96.7 | - | no | 0.0559 | 0.7609 | 0.498 | -1130.4 | 0.976 | 27.7 | 22 | 37 | 0 | no | no |
| 38 | 3 | `n_choch_since_bos` | 17 | -0.00298 | 0.00358 | -0.83 | no | 201.6 | - | no | 0.0673 | 0.7502 | 0.501 | 631.2 | 0.949 | 63.4 | 35 | 38 | 0 | no | no |
| 39 | 0 | `gmm4_map` | 43 | -0.01345 | 0.00974 | -1.38 | no | -257.0 | - | no | 0.3059 | 0.7451 | 0.497 | - | 1.000 | - | 39 | 39 | 0 | no | no |

Reading the table: 0 of 39 clusters pass the MDA rule (mean > std across the 12 folds). 14 clusters have an MDA of exactly 0 in every fold: the forest never split on any of their members (single one-hot levels or rare flags under min_weight_fraction_leaf 0.05 with balanced class weights), so permuting them changes nothing; 19 clusters have a negative mean MDA (permuting them lowers the OOF weighted log-loss), 6 a positive one. The best cluster is 17 (`touch_room_last=broke`, 4 members) with mean 0.00177 against std 0.00710 (ratio 0.25), positive in 10 of 12 folds. The large clusters, the ones the forest actually splits on (MDI), all sit at a negative log-loss MDA: cluster 0 (`gmm4_map`, 43 members, MDI 0.306) -0.01345 +- 0.00974; cluster 1 (`n_events_today`, 26 members, MDI 0.127) -0.00015 +- 0.01112; cluster 2 (`hv2_dir=none`, 18 members, MDI 0.060) -0.00141 +- 0.00791; cluster 3 (`n_choch_since_bos`, 17 members, MDI 0.067) -0.00298 +- 0.00358; cluster 4 (`swing_near_kind=H`, 16 members, MDI 0.106) -0.00074 +- 0.00790; cluster 5 (`n_bos_since_choch`, 14 members, MDI 0.023) -0.00043 +- 0.00134; cluster 6 (`fz_watch_kind=WATCH`, 12 members, MDI 0.036) -0.00058 +- 0.00400. The supplementary diagnostic below asks whether that is 'no ranking information' or a calibration effect of the balanced-weight forest; either way the pre-registered rule is the log-loss one and no cluster passes it.

Stability: periods H1_2021-10..2023-09 (412 rows, 124 winners), H2_2023-10..2025-12 (414 rows, 105 winners); rule top-8 in >= 2 of 2 periods; Spearman rank correlation of the cluster MDA vectors across periods: H1_2021-10..2023-09|H2_2023-10..2025-12: 0.1422. 2 clusters pass the stability filter, but with 33 of 39 clusters at a mean MDA <= 0 a cluster whose MDA is exactly 0 in every fold ranks inside the top 8 of a period by default (its rank is a tie among zeros above the negative clusters), so the stability column is meaningful only together with the MDA pass, which no cluster achieves; the filter is applied as the conjunction the design specifies.

### Supplementary diagnostic (not the pass rule; `mda_diag.py`, from the saved OOF arrays, no refit, no ledger row)

| item | value |
|---|---|
| log-loss MDA recomputed from `oof_5minute.npz` vs the table | max abs diff 1.91e-09 (agree) |
| full model OOF AUC, pooled / per-fold mean +- std | 0.4974 / 0.4915 +- 0.0833 |
| mean OOF probability vs winner share (unweighted / |net|-weighted) | 0.5222 vs 0.2772 / 0.3766 |
| OOF weighted log-loss: model vs the constant predictor at the weighted winner share | 0.72748 vs 0.66239 (the constant is better: the forest is mis-calibrated under balanced class weights) |
| clusters passing an AUC-drop version of the same rule (mean drop > std across folds) | 0 of 39 |
| clusters with negative / exactly-zero log-loss MDA | 19 / 0 |

| AUC rank | cluster | representative | AUC drop mean | std | ratio | folds positive | pooled-OOF AUC drop | log-loss MDA mean |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | `n_events_today` | 0.0109 | 0.0442 | 0.25 | 7 | 0.0117 | -0.00015 |
| 2 | 2 | `hv2_dir=none` | 0.0022 | 0.0252 | 0.09 | 8 | 0.0061 | -0.00141 |
| 3 | 12 | `card_read=LEAVE` | 0.0017 | 0.0080 | 0.21 | 9 | 0.0020 | +0.00021 |
| 4 | 7 | `fz_gate=TAKE` | 0.0013 | 0.0178 | 0.07 | 8 | 0.0031 | +0.00050 |
| 5 | 17 | `touch_room_last=broke` | 0.0012 | 0.0171 | 0.07 | 8 | 0.0028 | +0.00177 |

Full table: `mda_diag_5minute.csv`. Reading: the constant predictor at the weighted winner share beats the forest in weighted log-loss, so the OOF probabilities are mis-calibrated (balanced class weights centre them near 0.5 while the weighted winner share is 0.3766); permuting a cluster the forest splits on shrinks its predictions toward the centre, which lowers the log-loss even where the ranking degrades. The AUC drop asks the ranking question alone: no cluster passes a mean > std rule on it either, and the pooled OOF AUC of the whole forest is 0.4974. This diagnostic is reported for the reader's judgement of the null; it is not the pre-registered statistic, it changes no rank in the shortlist rule, and it proposes nothing.

Orthogonal check: 238 components (111 carry 95% of the variance); weighted Kendall tau between the MDI of the PC-score forest and the eigenvalues = **0.1393** (Kendall tau 0.2156, p 9.63e-07). A low tau is the AFML warning that the importance ranking may be fitting noise rather than variance-bearing directions.

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

### Interactions (xgboost on the top-40 features by clustered MDA; OOF weighted log-loss 0.78825, OOF AUC 0.5359)

| rank | feature a | feature b | mean abs SHAP interaction (OOF rows) | paths with both | split a (gain-weighted median) | split b | common splits a | common splits b |
|---|---|---|---|---|---|---|---|---|
| 1 | `touch_prot_bars_ago` | `ffd_close_dstar` | 0.051618 | 661 | 8.0000 | 2.4232 | [8.0, 6.0, 7.0] | [2.419, 2.4189, 2.4232] |
| 2 | `room_ahead_dist_atr` | `n_rooms_alive` | 0.044289 | 846 | 0.7394 | 8.0000 | [0.7394, 0.7617, 4.1739] | [7.0, 6.0, 8.0] |
| 3 | `room_ahead_dist_atr` | `fz_take_why=nan` | 0.042425 | 247 | 0.1701 | 1.0000 | [0.1701, 0.0776, 0.3558] | [1.0] |
| 4 | `ffd_close_dstar` | `sl` | 0.039569 | 701 | 2.4245 | 16705.2500 | [2.4159, 2.5133, 2.4189] | [15985.5, 16086.5, 25184.0] |
| 5 | `room_ahead_dist_atr` | `ffd_close_dstar` | 0.037084 | 614 | 0.3787 | 2.4698 | [0.1618, 0.1598, 0.4549] | [2.5133, 2.5277, 2.4698] |

Pairs that involve a calendar-time proxy (a price level or a cumulative count that trends over the four years; a split on it separates periods, not trade contexts): `touch_prot_bars_ago` x `ffd_close_dstar` **calendar-time proxy**: `ffd_close_dstar` = FFD of log close at d* = 0.2 (keeps most of the level); `ffd_close_dstar` x `sl` **calendar-time proxy**: `ffd_close_dstar` = FFD of log close at d* = 0.2 (keeps most of the level); `sl` = the Foundation stop price (a price level); `room_ahead_dist_atr` x `ffd_close_dstar` **calendar-time proxy**: `ffd_close_dstar` = FFD of log close at d* = 0.2 (keeps most of the level). Such a pair is listed because the design ranks by mean |SHAP interaction|, but a gate study that uses it must show the rule holds inside every period.

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
| 0 | `sl_dist_pts`, `sl_dist_atr`, `atr14`, `atr_bps`, `range_1h_pts`, `range_1h_atr`, `range_since_choch_atr`, `bar_range_pts`, `bar_range_atr`, `er_1h`, `bars_since_prev_choch`, `vol_ratio20`, `vol_ratio60`, `vol_max_ratio20_5`, `vol_max_ratio20_15`, `hv2_dir_agree`, `hv2_ratio`, `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k`, `dist_prot_dir_atr`, `dist_choch_lvl_atr`, `choch_bar_range_atr`, `move_since_choch_pts`, `ffd_vol_dstar`, `ffd_vol_dstar_z60`, `bsadf_close`, `csw_max_abs`, `csw_max_exceed`, `bocpd_ret_h60_p10`, `bocpd_ret_h240_p10`, `rv_absret`, `rv_body_frac`, `rv_logvol_rel20`, `gmm3_p2`, `gmm3_map`, `gmm4_p3`, `gmm4_map`, `hmm3_p2`, `hmm3_map`, `hmm4_map`, `jump4_run`, `win_sign_agree10`, `win_range_slope` | -0.01345 | 0.00974 | no | no | yes |
| 4 | `bar_body_pts`, `close_pos_in_bar`, `close_vs_sess_open_pts`, `pos_in_session_range`, `ret_1h_pts`, `hv2_dir=up`, `hv3_dir=up`, `dist_sl_atr`, `swing_near_kind=H`, `room_edge_kind=hi`, `card_read=PENDING`, `card_out_side=up`, `card_last_reject_dir=down`, `fz_watch_kind=WATCH_EDGE`, `ffd_close_dstar_z60`, `rv_ret36_atr` | -0.00074 | 0.00790 | no | no | yes |
| 21 | `sl`, `n_events_asof`, `ffd_close_dstar` | 0.00000 | 0.00037 | no | no | yes |

### The shortlist (0 clusters; 0 of 39 pass MDA, 2 pass stability, 0 pass both; cap 8)

Frozen at `features_shortlist/5minute/shortlist.json`, sha256 `4747257f41ecb40f1b3c27ea35cc50868d7c6b91f84f61ab7666911aef019dc9`, registered in `ledger/registrations.jsonl`. Allowed columns for the gate studies: 0.

**Empty**: no cluster passes both the MDA rule and the stability filter on this timeframe (none passes the MDA rule alone). The gate studies have no shortlisted column here; a null vocabulary is a result, not a failure of the pipeline. Consequence under the frozen rule: the downstream gate studies (gate_family, llm_round1, regime_gate) may not draw features on this timeframe from this study's vocabulary; any re-opening of the vocabulary (a weaker rule, a different statistic, a different model) is a user decision that would be a new registration with its own sha and the multiplicity carried forward, never an edit of this one. For that decision only, the clusters with a positive mean MDA (none exceeds its std): cluster 17 `touch_room_last=broke` (4 members) +0.00177 +- 0.00710, ratio 0.25, top-8 in 2 periods; cluster 7 `fz_gate=TAKE` (6 members) +0.00050 +- 0.00499, ratio 0.10, top-8 in 0 periods; cluster 12 `card_read=LEAVE` (5 members) +0.00021 +- 0.00160, ratio 0.13, top-8 in 1 periods; cluster 22 `days_to_expiry` (2 members) +0.00009 +- 0.00098, ratio 0.10, top-8 in 1 periods; cluster 16 `touch_prot_last=held` (4 members) +0.00000 +- 0.00355, ratio 0.00, top-8 in 1 periods. These are NOT allowed columns.


## FFD verdict (both timeframes)

**FFD not adopted (clustered MDA <= 1 std on minute, 5minute).** MDA pass of the cluster(s) holding the `ffd_*` columns: minute: no (mixed with non-FFD columns: {'0': True, '6': True, '8': True, '15': True}), 5minute: no (mixed with non-FFD columns: {'0': True, '4': True, '21': True}). The rule (Judge 2): adopted only if the FFD cluster's MDA > 1 std on BOTH timeframes; adoption would need a per-bar FFD routine in fz code (a new key type, a user decision) with keys d* close 0.2 / volume 0.1, weight cut 1e-4, windows 497 / 503 bars, z-window 60.

## What would falsify these findings

- A shortlisted cluster whose MDA sign flips when the permutation seeds change (5 permutations x 12 folds are recorded per row in `oof_<tf>.npz`; rerunning with other seeds is one command).
- A shortlisted cluster whose top-8 rank in the held-out periods does not survive a different block partition (the harness fixes 12 blocks; the per-period decomposition is of the same OOF rows).
- A feature in the shortlist that the truncation check would have dropped: none can be, every column comes from `harness.design` or from `ext_features.parquet`, which passed the truncation check at tolerance 1e-9.
- The full model's kept-vs-skipped numbers are a ceiling for a model that cannot ship; if the gate studies' rule lists come nowhere near them, the vocabulary is not the bottleneck; if a rule list beats them, the forest under-fits and this table under-states the vocabulary.
- A low weighted Kendall tau in the orthogonal check says the MDI ranking is not aligned with the variance-bearing directions; the shortlist rests on MDA, not on MDI, but the two are reported side by side so a disagreement is visible.
- The null vocabulary rests on the pre-registered statistic (OOF weighted log-loss of a balanced-weight bagging). It would be falsified as a statement about information, not about the rule, by a cluster that passes mean > std under a calibration-free statistic (the AUC-drop diagnostic already shows 2 such clusters on minute and 0 on 5minute) or under a calibrated learner (the same forest with its OOF probabilities isotonic-calibrated inside the training fold, or the meta-label study's HGB with NaN kept); either would be a new registration, not an edit of this shortlist.
- It would also be falsified by a gate study that, using columns outside this vocabulary, passes `harness.go_no_go` with a CPCV 5th percentile above zero: that would say the vocabulary pass was too blunt an instrument, and the program's rule that gate studies draw only from this shortlist would have cost a real gate.

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
- The stability ranks are ranks of a mostly non-positive vector: a cluster with an MDA of exactly 0 in every fold (never split on) ranks in the top 8 above the negative clusters. The filter is the conjunction 'MDA > 1 std AND top-8 in the periods' as designed, so this quirk cannot admit a cluster; it does make the stability column alone unreadable as evidence.
- The pre-registered MDA statistic is the OOF weighted log-loss. `mda_diag.py` shows (from the saved OOF arrays, no refit, no ledger row) that the balanced-weight forest is mis-calibrated under that loss, which is why the clusters the forest splits on have a negative log-loss MDA; the AUC-drop diagnostic is reported next to it for the reader and is not a pass rule.
- Resume: the run was interrupted by the model's usage limit (12:00-16:30 IST) after every stage process had finished on its own; only the minute finalize (11:27 UTC), the shortlist writer and this document were produced after the pause. Nothing was rerun; the minute cpcv log lacks its two closing lines (orphaned inode, see PROGRESS.md), cpcv_minute.json and the 11 ledger rows are complete.

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
- `studies/importance/main_minute.json`
- `studies/importance/mda_minute.csv`
- `studies/importance/sfi_minute.csv`
- `studies/importance/cpcv_minute.json`
- `studies/importance/run_minute_main.nohup`
- `studies/importance/run_minute_sfi.nohup`
- `studies/importance/run_minute_cpcv.nohup`
- `studies/importance/run_minute_finalize.nohup`
- `studies/importance/run_5minute.nohup`
- `studies/importance/mda_diag.py`
- `studies/importance/mda_diag.json`
- `studies/importance/mda_diag_minute.csv`
- `studies/importance/mda_diag_5minute.csv`
- `studies/importance/mda_diag.log`
- `studies/importance/imp_lib.py`
- `studies/importance/run_importance.py`
- `studies/importance/run_all.sh`
- `studies/importance/shortlist.py`
- `studies/importance/shortlist.log`
- `studies/importance/probe.py`
- `studies/importance/bag_probe.py`
- `studies/importance/bag_probe.log`
- `studies/importance/xgb_probe.py`
- `studies/importance/xgb_probe.log`
- `ledger/registrations.jsonl`
