# rocket_ceiling: is there information in the shape of the last 60 bars beyond the hand-built as-of features?

Study folder `fz_v3/out/studies/rocket_ceiling/` (DESIGN_PANEL `deep-sequence-rocket-probe`, reduced to the single ceiling check both judges allow; the `deep-sequence-pretrain-probe` rung 1 = PCA-16 linear probe runs inside it as a comparator). Scripts `rocket_lib.py` (windows, kernel bank, numba PPV transform), `rocket_ceiling.py` (the study; runtime 7,864 s; log `rocket_ceiling.log`, `run.nohup`), `finalize_family.py` (resume step: the family statistics recomputed from the ledger vectors with the current `harness.spa`, the run-integrity checks; `family_recheck.json`, `finalize.log`), `write_findings.py` (this file and `findings.json` from `results.json` + `family_recheck.json`). **IS only** (SETUP date <= 2025-12-31); timeframe **1 minute** only; label **L1** (the 15:25 book). Ledger sha after `621159330c8bb103`. **This study never gets a candidate slot** (Judge 1); its 144 ledger rows still count toward the program's multiplicity.

## 0. Result in one paragraph

**The pre-registered stop fired.** Over the 11 CPCV paths the AUC gain of the stacked model (tabular HGB + the top 16 PCA components of the 2,000 PPV kernel features) over the tabular HGB alone has 5th percentile **-0.0073** (median -0.0016, min -0.0079, max +0.0076, share > 0 0.455) against the threshold 0.03. The rocket probe alone reaches path AUC median 0.5846 vs tabular 0.5927 (gain median -0.0063, 5th pct -0.0165); the PCA-16 window probe (the pretrain footnote) 0.5468 (gain median -0.0447). 12-block pooled OOF AUC: tabular 0.5887, stacked 0.5892, rocket 0.5884, pca16 0.5474. No distillation was run and nothing is proposed for ST13/ST14. Every gate evaluated (4 models x skip 30/50/70 %) is a ledger row; the best OOF kept-vs-skipped difference in the family is +125.03 INR/trade (tabular at skip 0.3), PBO(diff) 0.4298, SPA p 0.762 (revised `harness.spa`, recomputed from the ledger vectors: studentised 0.762, unstudentised 0.783); `go_no_go` on it: False (information only, no slot).

## 1. Definitions (fixed before any number was looked at; the script's docstring, verbatim)

```
rocket_ceiling: DESIGN_PANEL deep-sequence-rocket-probe REDUCED to the single ceiling check both judges allow.

    nohup python rocket_ceiling.py > run.nohup 2>&1 &          # 1 minute only, label L1, IS only; log = rocket_ceiling.log

Question. Does the shape of the last 60 one-minute bars before a Foundation SETUP carry information about the L1 outcome beyond
the hand-built as-of features? Judge 2's reduction: 1m only, L = 60, 2,000 kernels, one probe, the harness splitter, and a
PRE-REGISTERED STOP: if the CPCV 5th-percentile AUC gain of the stacked model over the tabular HGB is < 0.03 the study ends with
that number and no distillation. Judge 1: alpha by nested GroupKFold (never RidgeClassifierCV's LOO); this study never gets a
candidate slot; its trials still go to the ledger. Pretrain-probe footnote (both judges): the PCA-16 linear probe on the flattened
z-scored window is a comparator here; sequence pretraining is deferred until a longer tape (torch is present in the cloud, the
design's sample-size objection is unchanged).

Definitions (fixed before any number was looked at):
  unit        a harness row: a Foundation SETUP taken under the L1 (15:25) book, harness.load("minute"); IS rows only (4,452);
              label y = L1 net > 0 (the training and judging label); windows are built for IS rows only (OOS features are never read)
  window      L = 60 bars ending at the SETUP bar k inclusive, 7 channels (rocket_lib.build_windows docstring): sg x log return
              (bps), (high-low)/atr14[k], sg x (close-open)/atr14[k], log(volume / vol_med20_prior[k]) with NaN -> 0, its NA flag,
              sg x (close - choch_lvl[k])/atr14[k], same-session indicator; float32; bars from data/minute/bars.parquet; verified on
              data/minute/trunc_20250630_120000 (windows of the SETUPs before the cut must be identical, else the study stops)
  kernels     2,000 MiniRocket-style kernels (rocket_lib.make_kernels): length 9, weights {-1, +2} centred, dilation log-uniform
              on 1 .. L/4 = 15, one channel or a random pair, zero padding, a quantile level per kernel; biases fitted per training
              fold from the quantiles of the convolution outputs of 32 sampled training windows (seed = fold seed); PPV pooling
  probe       "rocket": StandardScaler + L2 LogisticRegression (lbfgs) on the 2,000 PPV features; alpha = the PER-SAMPLE L2
              penalty (objective (1/n) sum loss + alpha/2 |w|^2, i.e. sklearn C = 1 / (alpha n), so that the inner 80 % fits and
              the full-fold refit carry the same regularisation and the same score scale) on the design's grid 1e-3 .. 1e3
              (7 values), chosen by nested GroupKFold(5) inside each training fold with groups = the harness block of the row
              (time-contiguous groups), criterion = inner OOF AUC; the path is fitted with warm starts from the smallest alpha
              upward (a fit that reports 0 iterations is refitted cold); refit on the whole training fold at the chosen alpha.
              (A timing benchmark on one chronological IS split before the study ran, no ledger row, showed that with sklearn's
              unnormalised C the optimum sat on the grid's edge and the refit's logit scale drifted; the per-sample convention
              was adopted for that reason before any fold of the study was run.)
  comparators (in the same folds)
              "tabular": HistGradientBoostingClassifier(max_depth 3, max_iter 200, learning_rate 0.05, random_state 0) on
                         harness.design(T) (244 base as-of columns; NaN native)
              "pca16":   StandardScaler + PCA(16) on the flattened z-scored window (7 x 60 = 420) + the same nested-alpha logistic
              "stacked": the same HGB on [design(T), the top 16 PCA components of the standardised PPV features], scaler + PCA fit
                         on the training fold (and inside every inner fold for the threshold OOF)
  splitter    harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo) -> the OOF probabilities;
              harness.cpcv_splits (66) -> harness.cpcv_paths (11 paths) -> the path distribution
  statistic   per-fold test AUC (and average precision) of every model; pooled 12-block OOF AUC; per path: the pooled AUC over
              IS rows of each model and the gains stacked - tabular, rocket - tabular, pca16 - tabular; the distribution over
              the 11 paths (median, 5th percentile = np.quantile(., 0.05), min, share > 0). Judge 1's per-fold form (stacked -
              tabular < 0.02 in every fold) is reported next to it as a footnote.
  STOP        pre-registered: CPCV 5th-percentile gain (stacked - tabular) < 0.03 -> the study ends with that number; no
              distillation, no candidate. >= 0.03 -> distil the probe score's bottom tercile to a depth-3 tree on scalar as-of
              features (design(T) + win_sign_agree10, win_dd_extreme_atr, win_range_slope from features_ext) and report fidelity
  gates       every model x skip fraction q in {0.30, 0.50, 0.70}: the threshold = the q-quantile of the model's inner-fold OOF
              scores on the TRAINING fold (never the test rows); keep = test score >= threshold; the 12-block OOF mask is one
              harness.score row (family rocket/<model>, config = model, q, L, K, seed); the 66 CPCV decisions -> 11 path masks ->
              harness.score_paths (family rocket/<model>/cpcv, controls on). 12 + 132 ledger rows; nothing is chosen on them.
  family      window lengths x kernel counts x probes = 1 x 1 x 3 (Judge 2's count for the design's multiplicity statement; the
              third probe = pca16); PBO / SPA / effective trials over the 12 OOF gate rows; DSR and the block bootstrap for the
              gate with the largest OOF diff; harness.go_no_go for information only (no candidate slot)
  never       a label inside the transform, a bias or a scaler fitted on test rows, an OOS row (features or labels), a threshold
              from the pooled OOF
```

## 2. Data, windows, kernel bank, causality check

| item | value |
|---|---|
| units (IS / OOS row count) | 4,452 / 814 (OOS never read) |
| IS win rate / mean L1 net (INR) | 0.1559 / -1,009.61 |
| window tensor | [4452, 7, 60] float32 = 7.1 MB, built in 0.09 s |
| channel means | [0.13590000569820404, 0.9807999730110168, 0.02239999920129776, 0.11599999666213989, 0.030500000342726707, -0.6485000252723694, 0.9110000133514404] |
| channel sds | [4.241600036621094, 0.46720001101493835, 0.6825000047683716, 0.7559000253677368, 0.1720999926328659, 2.75570011138916, 0.2847000062465668] |
| NA-flag share (ch4) / same-session share (ch6) / windows crossing the session start | 0.0305 / 0.911 / 0.1584 |
| kernel bank | K = 2000, length 9, seed 3795216026, dilation counts (d = 1..15) [496, 303, 205, 176, 123, 110, 89, 93, 86, 66, 67, 77, 61, 48, 0], pair share 0.504, channel use [439, 466, 443, 402, 392, 442, 425]; frozen in `kernels.npz` |
| truncation check (`windows_trunc_check.json`) | cut trunc_20250630_120000, bars 335,934, SETUPs before the cut [3767, 3767], same keys True, max |diff| 0.0, **PASS True** |
| base design | 244 as-of columns (`harness.design`); flattened window 420 |
| PPV feature matrix per fold | n_train x 2000 float32 (34 MB for all IS rows, one transform 23.92 s single-threaded; the design's 5,266 x 2,000 = 42 MB figure counts the OOS rows, which were not built) |

## 3. Per-fold AUC (12 purged blocks; `fold_auc.csv`)

| block | AUC rocket | AUC pca16 | AUC tabular | AUC stacked | stacked - tabular | rocket - tabular | alpha rocket | alpha pca16 |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.5732 | 0.5112 | 0.6023 | 0.6155 | +0.0132 | -0.0291 | 10.0 | 1.0 |
| 1 | 0.5825 | 0.6113 | 0.6456 | 0.6252 | -0.0204 | -0.0631 | 10.0 | 1.0 |
| 2 | 0.5323 | 0.5839 | 0.5582 | 0.5399 | -0.0183 | -0.0259 | 10.0 | 1.0 |
| 3 | 0.6356 | 0.5310 | 0.5955 | 0.6031 | +0.0076 | +0.0400 | 10.0 | 0.1 |
| 4 | 0.6311 | 0.5933 | 0.6651 | 0.6714 | +0.0063 | -0.0340 | 10.0 | 0.1 |
| 5 | 0.4494 | 0.5233 | 0.4566 | 0.4638 | +0.0072 | -0.0072 | 100.0 | 1.0 |
| 6 | 0.6495 | 0.5303 | 0.6247 | 0.6220 | -0.0026 | +0.0248 | 10.0 | 0.1 |
| 7 | 0.5994 | 0.6076 | 0.5340 | 0.5381 | +0.0040 | +0.0654 | 10.0 | 1.0 |
| 8 | 0.4410 | 0.4848 | 0.5323 | 0.5272 | -0.0051 | -0.0913 | 10.0 | 0.1 |
| 9 | 0.5932 | 0.5472 | 0.5689 | 0.5726 | +0.0037 | +0.0243 | 10.0 | 0.1 |
| 10 | 0.6184 | 0.5316 | 0.6176 | 0.6692 | +0.0516 | +0.0008 | 10.0 | 1.0 |
| 11 | 0.6185 | 0.5395 | 0.5885 | 0.5800 | -0.0084 | +0.0300 | 10.0 | 1.0 |

Pooled 12-block OOF AUC: rocket **0.5884**, pca16 **0.5474**, tabular **0.5887**, stacked **0.5892**; average precision: rocket 0.2021, pca16 0.1842, tabular 0.2131, stacked 0.2059. Judge 1's footnote form (stacked - tabular < 0.02 in every block): **False**. Inner-fold OOF AUC at the chosen alpha, mean over blocks: rocket 0.5897, pca16 0.5508, tabular 0.5836, stacked 0.5821.

## 4. The CPCV path distribution (66 splits -> 11 paths; `path_auc.csv`) and the pre-registered stop

| path | AUC rocket | AUC pca16 | AUC tabular | AUC stacked | stacked - tabular | rocket - tabular | pca16 - tabular |
|---|---|---|---|---|---|---|---|
| 0 | 0.5896 | 0.5505 | 0.5900 | 0.5884 | -0.0016 | -0.0004 | -0.0395 |
| 1 | 0.5904 | 0.5462 | 0.5935 | 0.5869 | -0.0067 | -0.0031 | -0.0473 |
| 2 | 0.5874 | 0.5571 | 0.6037 | 0.5958 | -0.0079 | -0.0162 | -0.0466 |
| 3 | 0.5783 | 0.5476 | 0.5742 | 0.5766 | +0.0024 | +0.0041 | -0.0266 |
| 4 | 0.5817 | 0.5496 | 0.5855 | 0.5931 | +0.0076 | -0.0038 | -0.0359 |
| 5 | 0.5844 | 0.5399 | 0.5988 | 0.6011 | +0.0023 | -0.0144 | -0.0588 |
| 6 | 0.5846 | 0.5498 | 0.5927 | 0.5901 | -0.0026 | -0.0082 | -0.0430 |
| 7 | 0.5876 | 0.5458 | 0.5887 | 0.5949 | +0.0062 | -0.0010 | -0.0428 |
| 8 | 0.5825 | 0.5468 | 0.5992 | 0.6027 | +0.0034 | -0.0167 | -0.0525 |
| 9 | 0.5878 | 0.5440 | 0.5941 | 0.5897 | -0.0044 | -0.0063 | -0.0500 |
| 10 | 0.5826 | 0.5456 | 0.5903 | 0.5851 | -0.0052 | -0.0077 | -0.0447 |

| statistic over 11 paths | median | 5th pct | min | max | share > 0 |
|---|---|---|---|---|---|
| gain_stacked | -0.0016 | -0.0073 | -0.0079 | +0.0076 | 0.455 |
| gain_rocket | -0.0063 | -0.0165 | -0.0167 | +0.0041 | 0.091 |
| gain_pca16 | -0.0447 | -0.0556 | -0.0588 | -0.0266 | 0.0 |
| auc_rocket | 0.5846 | 0.5800 | 0.5783 | 0.5904 | 1.0 |
| auc_pca16 | 0.5468 | 0.5420 | 0.5399 | 0.5571 | 1.0 |
| auc_tabular | 0.5927 | 0.5798 | 0.5742 | 0.6037 | 1.0 |
| auc_stacked | 0.5901 | 0.5808 | 0.5766 | 0.6027 | 1.0 |

Per-split (66) gains stacked - tabular: min -0.0267, median -0.0011, share < 0.02 0.955; rocket - tabular: min -0.0915, median -0.0053. Alpha chosen by the nested GroupKFold across the 66 CPCV training folds: rocket {'0.001': 0, '0.01': 0, '0.1': 0, '1.0': 3, '10.0': 57, '100.0': 6, '1000.0': 0}, pca16 {'0.001': 1, '0.01': 2, '0.1': 20, '1.0': 43, '10.0': 0, '100.0': 0, '1000.0': 0}.

**Pre-registered stop** (Judge 2): CPCV 5th-percentile AUC gain of stacked over tabular = **-0.0073** < 0.03 -> **the study ends with that number; no distillation, no candidate.**

## 5. Every gate evaluated (ledger families `rocket/<model>`; CPCV paths `rocket/<model>/cpcv`; `gates.csv`, `cpcv_gate_paths.csv`)

Threshold = the q-quantile of the training fold's inner-OOF scores (never the test rows), so the realised kept share is near, not exactly, 1 - q. Skip = score below the threshold. INR per trade.

| model | skip q | ledger id | kept n | kept share | kept mean | skipped mean | diff | diff top1 removed | control pct | perm p | loser recall | |net|-w winner recall | top-decile winners skipped | sign blocks /12 | kept mean slip 8 | CPCV diff median | CPCV diff p5 | CPCV share > 0 | CPCV control pct median | CPCV control pct p5 | go (raw checks) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rocket | 0.3 | 80e5e282bcb601dc | 3,091 | 0.6943 | -971.99 | -1,095.05 | 123.06 | -88.80 | 0.0 | 0.1474 | 0.3254 | 0.8737 | 0.0571 | 9 | -1,361.95 | 134.04 | 102.97 | 1.0 | 0.0 | 0.0 | False |
| rocket | 0.5 | d3a34084752ef27a | 2,209 | 0.4962 | -957.54 | -1,060.89 | 103.35 | -162.99 | 0.0 | 0.1909 | 0.5237 | 0.7305 | 0.1571 | 9 | -1,347.50 | 91.68 | 66.98 | 1.0 | 0.0 | 0.0 | False |
| rocket | 0.7 | b2195fdc6cc1b267 | 1,373 | 0.3084 | -981.06 | -1,022.34 | 41.28 | -307.90 | 0.0 | 0.6222 | 0.7076 | 0.5199 | 0.3857 | 4 | -1,371.02 | 50.36 | 7.21 | 1.0 | 0.0 | 0.0 | False |
| pca16 | 0.3 | 07b5eb852d6512bc | 3,135 | 0.7042 | -1,016.03 | -994.31 | -21.72 | -126.84 | 0.0 | 0.7991 | 0.3007 | 0.7895 | 0.1714 | 4 | -1,406.00 | -26.98 | -67.66 | 0.273 | 0.0 | 0.0 | False |
| pca16 | 0.5 | 10128de1aa08e6fe | 2,225 | 0.4998 | -1,015.82 | -1,003.40 | -12.42 | -103.23 | 0.0 | 0.8781 | 0.513 | 0.6103 | 0.3571 | 4 | -1,405.78 | -7.20 | -74.62 | 0.455 | 0.0 | 0.0 | False |
| pca16 | 0.7 | e6729c6012216484 | 1,290 | 0.2898 | -1,004.58 | -1,011.66 | 7.08 | -179.48 | 0.0 | 0.9275 | 0.7227 | 0.4349 | 0.5143 | 6 | -1,394.54 | 24.11 | -46.31 | 0.636 | 0.0 | 0.0 | False |
| tabular | 0.3 | 7594408d55b3a8c9 | 3,319 | 0.7455 | -977.79 | -1,102.82 | 125.03 | -60.08 | 4.9 | 0.1774 | 0.2717 | 0.8819 | 0.1143 | 9 | -1,367.75 | 98.01 | 6.15 | 1.0 | 15.4 | 0.3 | False |
| tabular | 0.5 | 1d2af8d85982e293 | 2,386 | 0.5359 | -1,022.02 | -995.27 | -26.75 | -109.90 | 0.1 | 0.7321 | 0.4808 | 0.6573 | 0.3571 | 5 | -1,411.98 | 9.87 | -24.62 | 0.727 | 0.3 | 0.0 | False |
| tabular | 0.7 | 6263d2e353f32624 | 1,417 | 0.3183 | -955.20 | -1,035.01 | 79.81 | -116.37 | 0.4 | 0.3548 | 0.6982 | 0.4771 | 0.4857 | 8 | -1,345.17 | 88.52 | 56.95 | 1.0 | 0.5 | 0.1 | False |
| stacked | 0.3 | 2034e749729ecff3 | 3,286 | 0.7381 | -991.04 | -1,061.95 | 70.91 | -29.13 | 2.4 | 0.4343 | 0.2797 | 0.8508 | 0.1429 | 7 | -1,381.00 | 50.80 | -10.48 | 0.818 | 4.5 | 0.7 | False |
| stacked | 0.5 | 887ddb6af27a2514 | 2,376 | 0.5337 | -995.86 | -1,025.34 | 29.48 | -80.31 | 0.1 | 0.7131 | 0.4843 | 0.6754 | 0.3143 | 5 | -1,385.82 | 10.58 | -37.45 | 0.636 | 1.1 | 0.1 | False |
| stacked | 0.7 | 334a8df20e257596 | 1,441 | 0.3237 | -1,012.70 | -1,008.13 | -4.57 | -105.73 | 0.0 | 0.958 | 0.6943 | 0.4483 | 0.5143 | 5 | -1,402.67 | 69.75 | -65.31 | 0.545 | 0.1 | 0.0 | False |

## 6. Family statistics (the 12 OOF gate rows; PBO / SPA / effective trials from the ledger)

| statistic | value |
|---|---|
| design family (window lengths x kernel counts x probes) | window lengths x kernel counts x probes = 1 x 1 x 3; probes: rocket (L2 logistic on PPV); pca16 (L2 logistic on PCA-16 of the window); stacked (HGB on base + PCA-16 of PPV) |
| ledger rows: OOF gates / CPCV path rows | 12 / 132 |
| effective trials (participation ratio) | 1.49 |
| PBO (diff) / PBO (kept mean) | 0.4298 / 0.6926 (partitions 12870; degradation slope -1.067) |
| SPA: best gain / t / RC p / SPA p | 5.34 / 0.218 / 0.9445 / **0.762** (best = tabular skip 0.3, id 7594408d55b3a8c9) |
| best by OOF diff | tabular skip 0.3, id 7594408d55b3a8c9, diff +125.03 |
| DSR of the best (n_trials = 12) | SR 0.0105, SR0 0.0735, DSR 0.0629, p 0.9371 |
| block bootstrap 90 % CI of the best's diff | [22.03, 224.11] (P(diff <= 0) 0.026) |
| go / no-go on the best (information only) | passed **False**; failed: diff_top1_removed>0, kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10 |

### 6a. The same family recomputed from the ledger vectors with the current harness (`finalize_family.py` -> `family_recheck.json`; harness sha `0fe3d75a0bd6e78d`)

`harness.spa` was revised after this run (the exit-policy refuter's finding: a candidate active in fewer than max(10, 5 % T) sessions leaves the studentised family; White's unstudentised statistic is reported too). The same 12 vectors, the same bootstrap tag (so the same 2,000 stationary-bootstrap draws), no ledger row written.

| statistic | results.json (harness at 07:12) | recomputed (current harness) | reproduces |
|---|---|---|---|
| effective trials | 1.49 | 1.49 | True |
| PBO (diff) / PBO (kept mean) | 0.4298 / 0.6926 | 0.4298 / 0.6926 | True / True |
| SPA studentised (Hansen): best / t / RC p / SPA p | tabular skip 0.3 / 0.218 / 0.9445 / 0.762 | tabular skip 0.3 / 0.218 / 0.9445 / **0.762** | True / True / True / True |
| SPA: candidates excluded from the studentised family (min active sessions) | n/a | 0 of 12 (min 28; active sessions per candidate [281, 357, 365, 431, 462, 460, 365, 434, 429, 363, 438, 423]) |  |
| SPA unstudentised (White): best / mean gain / RC p / SPA p | n/a | tabular skip 0.3 / 5.34 / 0.9545 / **0.783** |  |
| DSR p of the best | 0.9371 | 0.9371 | True |
| block bootstrap 90 % CI of the best's diff | [22.03, 224.11] | [22.03, 224.11] | True |
| go / no-go on the best | False | False | True |

## 7. Distillation

Not run: pre-registered stop: CPCV p5 gain stacked - tabular = -0.0073 < 0.03. The design's distillation step (depth-3 tree on base + `win_sign_agree10`, `win_dd_extreme_atr`, `win_range_slope`) is implemented in `rocket_ceiling.py::distillation` and did not execute; the three window summaries are already in `features_ext/minute/ext_features.parquet` for the importance study (Judge 2): 5,326 SETUP rows, coverage on the 4,452 IS units {'win_sign_agree10': 1.0, 'win_dd_extreme_atr': 1.0, 'win_range_slope': 0.9816} (checked by `finalize_family.py`, never read by the run).

## 8. Timing, memory, seeds

| item | value |
|---|---|
| kernel seed (sha1 of 'fz|rocket_ceiling|minute|L60|K2000' mod 2^32) | 3795216026 |
| per-fold bias seed | sha1(f'{seed}|purged|{block}') or sha1(f'{seed}|cpcv|{a}|{b}') mod 2^32 (in `fold_auc.csv` rows via results.json `folds`) |
| numba JIT / one full transform (4,452 windows x 2,000 kernels x 60 bars) | 1.38 s / 23.92 s |
| per-fold wall time (purged blocks) | [416.4, 425.8, 429.9, 418.5, 412.6, 439.6, 419.2, 442.3, 443.7, 423.9, 420.5, 392.4] |
| per-fold wall time, CPCV mean | 347.6 s |
| mean stage seconds per fold | {'transform': 97.44, 'rocket': 122.6, 'pca16': 5.77, 'tabular': 54.59, 'stacked': 78.75} |
| 78 folds done at / total (with the 144 ledger rows and their 2,000-draw controls) | 7,102 s / 7,864 s |
| RSS after the folds / peak RSS (ru_maxrss) | 476 MB / 504 MB (the box ran other studies concurrently: load average ~16 on 4 cores during this run) |
| family size recorded for the multiplicity statement | window lengths x kernel counts x probes = 1 x 1 x 3; 12 OOF gate rows + 132 CPCV path rows in the ledger (`rocket/<model>`, `rocket/<model>/cpcv`) |

### 8a. Run integrity (resume after the 2026-09-29 usage-limit pause; `finalize_family.py`)

| check | result |
|---|---|
| the 12 OOF gate rows of `results.json` re-read from the ledger, field by field | match **True** (mismatches: []) |
| rocket rows in the ledger | 144 = 12 OOF + 132 CPCV, {'rocket/rocket': 3, 'rocket/rocket/cpcv': 33, 'rocket/pca16': 3, 'rocket/pca16/cpcv': 33, 'rocket/tabular': 3, 'rocket/tabular/cpcv': 33, 'rocket/stacked': 3, 'rocket/stacked/cpcv': 33}, written 2026-09-29T07:00:02 .. 2026-09-29T07:12:37 (UTC); 11 rows of the concurrently running importance study interleaved (append-only shared ledger) |
| script that wrote the rows | ledger `script_sha` ['771f509e5cc4faf8'] == sha of `rocket_ceiling.py` on disk: **True** |
| `results.json` -> `ledger_sha_after` `621159330c8bb103` | = sha of the ledger's first 1746 rows: **True**; the last rocket row is row 1745 (2026-09-29T07:12:37), the next row is {'index': 1746, 'family': 'importance/full_model/cpcv', 'at': '2026-09-29T07:14:41'}. results.json was written when the ledger held exactly the rows up to and including the last rocket CPCV row: the run finished and wrote its results itself. |
| the log on disk | 50 lines, `rocket_ceiling.log` == `run.nohup` True; last line 07:12:37 is the last gate row (True); the run finished at 07:12:37.5 (first line + timing.total_s 7864.5 s). The script's final three log calls (3/3 present in the file that ran) are **not** in the log (0/3): PROGRESS.md (Git incident): the 06:24 checkout replaced every tracked file's inode; the running process kept writing to the unlinked inodes; a mirror loop copied the orphaned logs back from /proc/<pid>/fd until the process exited, and the last copy predates the run's final second. results.json holds the family / distillation / timing values those lines would have printed, and its ledger sha reproduces (above). |

## 9. What would falsify this finding

- A CPCV 5th-percentile stacked-minus-tabular AUC gain >= 0.03 on a re-run with another kernel seed (the bank is random; the seed is logged and the study is deterministic given it). The per-path gains here are the evidence that the window shape adds nothing the base features do not already carry; a different seed changing that verdict would mean the 2,000-kernel bank is too small to be stable, not that the tape has changed.
- A window length or channel set outside the reduced design (L = 120, the 5-minute frame) showing a gain: not tested here by the judges' cut; it would be a new family with its own multiplicity count.
- A leakage in the window tensor: excluded by the truncation check (identical windows for every SETUP before the 2025-06-30 cut) and by construction (bars <= k only; biases, scalers and PCA fitted on training rows).
- The AUC statistic is rank-based and label-balanced; a gate that adds expectancy without adding AUC (a tail effect on the few large winners) would not be seen by the stop rule. The gate rows (section 5) carry the INR numbers for that reading: none of the 12 clears the control percentile / block-sign / CPCV checks together.

## 10. Candidates

None. This study never gets a candidate slot (Judge 1); the stop rule decides only whether distillation runs. `null_result = true`.

## 11. Caveats

- Reduced design (both judges): 1 minute only, L = 60, 2,000 kernels, one probe family; the 5-minute frame, L = 120 and the ridge / net-regression probes of the original design were cut and are not tested.
- The pre-SETUP window is templated by the engine's own SETUP definition (CHoCH then continuation), so shape motifs are the rule rather than information (Judge 1); the result is consistent with that.
- Thresholds for the skip fractions come from the training fold's inner-OOF score distribution; the test-fold scores come from the model refit on the whole training fold (same per-sample regularisation, so the same scale up to sampling), and the test block's own score distribution shifts with its regime, so the realised kept share deviates from 1 - q (reported per gate).
- The alpha grid is the design's 1e-3 .. 1e3 read as a per-sample L2 penalty (sklearn C = 1/(alpha n)); with sklearn's unnormalised C the same numbers would have put the optimum on the grid's edge (seen in a one-split timing benchmark before the study ran, no ledger row).
- The stacked model is the same HGB with 16 extra columns; a gain of exactly zero is not guaranteed by construction (the extra columns can hurt), so negative gains are possible and are reported as such.
- Windows crossing the session start carry the overnight gap in the log-return channel; the same-session channel flags those bars. Bars before the tape start (session 0 only) are zero-padded.
- Sequence pretraining (the design's rungs 2-3) is deferred: torch is present in the cloud but the sample-size objection of both judges is unchanged; the PCA-16 rung ran as a comparator and is the weakest of the four models.
- The box ran other studies concurrently; wall-clock timings are inflated, CPU seconds are not reported.
- The log on disk ends at the last gate row: the run's final three log lines (family statistics, 'distillation not run', 'done in') were lost to the 06:24 checkout-inode incident (PROGRESS.md); results.json carries their values and its ledger sha reproduces as a ledger prefix (section 8a). The agent that launched the run was cut off by the usage limit at 06:44 UTC while the run was between CPCV splits 43 and 49 (logged 06:39:50 and 06:47:17); FINDINGS.md, findings.json and the family recheck were written by the resuming agent from results.json and the ledger, nothing was rerun.
- results.json's SPA is the harness's SPA as of 07:12; the revised harness.spa (min-active-session filter, unstudentised statistic) is reported next to it in section 6a. Both agree on the studentised p because no rocket gate is near-degenerate: the 12 candidates have a non-zero selection gain in 281-462 of the 578 active sessions, against the exclusion threshold of 28.

## 12. Files

- `studies/rocket_ceiling/rocket_lib.py`
- `studies/rocket_ceiling/rocket_ceiling.py`
- `studies/rocket_ceiling/finalize_family.py`
- `studies/rocket_ceiling/write_findings.py`
- `studies/rocket_ceiling/rocket_ceiling.log`
- `studies/rocket_ceiling/run.nohup`
- `studies/rocket_ceiling/finalize.log`
- `studies/rocket_ceiling/results.json`
- `studies/rocket_ceiling/family_recheck.json`
- `studies/rocket_ceiling/fold_auc.csv`
- `studies/rocket_ceiling/path_auc.csv`
- `studies/rocket_ceiling/gates.csv`
- `studies/rocket_ceiling/cpcv_gate_paths.csv`
- `studies/rocket_ceiling/windows_trunc_check.json`
- `studies/rocket_ceiling/kernels.npz`
- `studies/rocket_ceiling/oof_scores.npz`
- `studies/rocket_ceiling/FINDINGS.md`
- `studies/rocket_ceiling/findings.json`
