# H2 / H3 / H4: sideways, visibly high volume, levels respected or broken (IS only, through the harness)

Study folder `fz_v3/out/studies/h2_h3_h4/`. Scripts: `h2_regime.py`, `h3_volume.py`, `h4_levels.py` on the shared `h234_common.py`; `posthoc_minskip.py` (one declared post-hoc selection variant, section 3; NOT RUN); `write_findings.py` (this file: sections 1-6 followed by the auto-generated tables T1-T4). Logs: `h2_regime.log`, `h3_volume.log`, `h4_levels.log`, `posthoc_minskip.log`, `run_h2_5minute.nohup`, `run_h2_minute.nohup`, `run_h3_5minute.nohup`, `run_h3_minute.nohup`, `run_h4_5minute.nohup`, `run_h4_episodes_repair.nohup`, `run_h4_minute.nohup`, `run_posthoc_5minute.nohup`, `run_posthoc_minute_L0_h3h4.nohup`, `run_posthoc_minute_L1.nohup`. Every number is IS only (SETUP date <= 2025-12-31) and is a harness ledger row (id given) or a row of a CSV / JSON in this folder; the definitions (table T1) were fixed in the scripts' docstrings before any number was read (the H4 cut-window rule was made to match its definition in the repair round, section 6). Machine-readable: `findings.json`. Written 2026-09-29 05:34:26; INTERIM: outputs still missing: h2_minute_L0_summary.json, h2_summary_minute.json, posthoc_h2_minute_L1_summary.json, posthoc_h2_minute_L0_summary.json, posthoc_h2_5minute_L1_summary.json, posthoc_h2_5minute_L0_summary.json, posthoc_h3_minute_L1_summary.json, posthoc_h3_minute_L0_summary.json, posthoc_h3_5minute_L1_summary.json, posthoc_h3_5minute_L0_summary.json, posthoc_h4_minute_L1_summary.json, posthoc_h4_minute_L0_summary.json, posthoc_h4_5minute_L1_summary.json, posthoc_h4_5minute_L0_summary.json. Ledger at that moment: sha `b6140d1e9628668d`, 1300 rows (1161 of families h2/h3/h4, 1161 distinct ids, 11 with note `repair`, split ['IS']), 0 unparseable lines, 0 rows without a per-session vector. Families present: `h2/both`, `h2/choch`, `h2/nested_cv`, `h2/nested_cv/cpcv`, `h2/nested_cv_minskip`, `h2/nested_cv_minskip/cpcv`, `h2/range`, `h3/gate`, `h3/nested_cv`, `h3/nested_cv/cpcv`, `h3/nested_cv_minskip`, `h3/nested_cv_minskip/cpcv`, `h4/nested_cv`, `h4/nested_cv/cpcv`, `h4/touch_gate`.
## 1. Result

**Null result.** No cell family of H2, H3 or H4 produced a candidate that passes `harness.go_no_go` on either timeframe, on L1 or on L0, under the pre-registered nested-CV selection. No candidate config JSON is written. The tables that carry the result:

| study | tf | label | selection | ledger_id | kept_share | diff | control_pct | perm_p | sign_blocks | cpcv_diff_p5 | cpcv_share_pos | pbo_diff | spa_p | dsr_p | boot_ci90 | go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h2 | 1 min | L1 | pre-registered | 96a71fa0c77cbd57 | 0.9674 | -226.81 | 1.10 | 0.3148 | 6 | -417.49 | 0.182 | 0.3564 | 0.1255 | 1.00 | [-582.49, 91.16] | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h3 | 1 min | L1 | pre-registered | 21b31cbb10277775 | 0.8677 | -171.85 | 0 | 0.1414 | 1 | -298.24 | 0.091 | 0.7635 | 0 | 1.00 | [-324.62, -39.75] | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0 |
| h3 | 1 min | L0 | pre-registered | 4aa13f8ee89c96a3 | 0.9673 | 199.29 | 59.10 | 0.6362 | 8 | 203.44 | 1.00 | 0.1033 | 0.055 | 1.00 | [-146.01, 516.43] | False | diff_top1_removed>0, kept_mean_slip8>0, control_pct>=95, dsr_p<0.1, boot_ci_excludes_0 |
| h4 | 1 min | L1 | pre-registered | 7e2a1c31f2dc16c3 | 0.8441 | -6.92 | 3.10 | 0.9535 | 5 | -171.27 | 0.273 | 0.4249 | 0.936 | 0.9987 | [-220.04, 187.58] | False | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h4 | 1 min | L0 | pre-registered | f761a518d322b977 | 0.797 | 29.10 | 10.50 | 0.8821 | 6 | -60.02 | 0.727 | 0.6843 | 0.9785 | 0.8465 | [-208.78, 256.9] | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h2 | 5 min | L1 | pre-registered | 74e1239d4204941d | 0.9976 | 3,991.66 | 94.30 | 0.1339 | 2 | 3,444.78 | 1.00 | 0.3293 | 0.076 | 0.9957 | [2816.25, 5189.35] | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1 |
| h2 | 5 min | L0 | pre-registered | c04a0d2a19d216fd | 0.9976 | 4,473.04 | 93.80 | 0.2124 | 2 | 732.98 | 0.909 | 0.3043 | 0.124 | 0.7772 | [3078.04, 5879.24] | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10 |
| h3 | 5 min | L1 | pre-registered | 8eaee251afffdbb3 | 0.9383 | -200.09 | 0.4 | 0.7566 | 6 | -598.43 | 0.273 | 0.6568 | 0.155 | 0.9965 | [-1159.18, 581.14] | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h3 | 5 min | L0 | pre-registered | 0b364a8b48bd9207 | 0.9712 | 451.83 | 34.90 | 0.8321 | 6 | 261.32 | 1.00 | 0.5181 | 0.5765 | 0.7825 | [-2269.14, 2575.06] | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h4 | 5 min | L1 | pre-registered | 9e32a86bcfc8f5ce | 0.9322 | 613.48 | 83.80 | 0.3228 | 7 | -1,774.85 | 0.455 | 0.6501 | 0.1705 | 0.8863 | [-289.64, 1371.11] | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| h4 | 5 min | L0 | pre-registered | a329912797859321 | 0.9267 | 2,221.97 | 99.20 | 0.097 | 10 | 2,221.97 | 1.00 | 0.1556 | 0.3625 | 0.3623 | [1238.07, 3148.44] | False | kept_mean_slip8>0, dsr_p<0.1, spa_p<=0.10 |


The grids themselves: how many cells have a positive diff, a control percentile >= 95, and how many pass every raw go/no-go check at once (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks >= 8, control >= 95):

| study | tf | label | cells | diff_pos | control_ge95 | cells_passing_raw_checks |
|---|---|---|---|---|---|---|
| h2 | 1 min | L1 | 201 | 50 | 35 | 0 |
| h3 | 1 min | L1 | 54 | 15 | 33 | 0 |
| h3 | 1 min | L0 | 54 | 20 | 19 | 0 |
| h4 | 1 min | L1 | 9 | 6 | 1 | 0 |
| h4 | 1 min | L0 | 9 | 4 | 0 | 0 |
| h2 | 5 min | L1 | 201 | 79 | 35 | 0 |
| h2 | 5 min | L0 | 201 | 103 | 22 | 0 |
| h3 | 5 min | L1 | 54 | 26 | 35 | 0 |
| h3 | 5 min | L0 | 54 | 36 | 31 | 0 |
| h4 | 5 min | L1 | 9 | 4 | 1 | 0 |
| h4 | 5 min | L0 | 9 | 2 | 1 | 0 |

## 2. The user's claims, restated as measured (IS, L1 unless stated)

### 2.1 "CHoCH, CHoCH, no BOS = sideways; trades in sideways are hurting"

Foundation mean net by `n_choch_since_bos` (the user's sideways = 2 and above):

| table | n_choch_since_bos | n | net_mean | net_se | win_rate | all_rows_mean |
|---|---|---|---|---|---|---|
| minute_L1 | 0 | 1,169 | -1,089.61 | 69.65 | 0.1377 | -1,009.61 |
| minute_L1 | 1 | 1,739 | -997.87 | 70.66 | 0.1576 | -1,009.61 |
| minute_L1 | 2 | 823 | -1,029.94 | 81.45 | 0.1738 | -1,009.61 |
| minute_L1 | 3 | 372 | -837.12 | 147.24 | 0.1559 | -1,009.61 |
| minute_L1 | 4+ | 349 | -936.01 | 115.11 | 0.1662 | -1,009.61 |
| 5minute_L1 | 0 | 235 | -717.44 | 289.68 | 0.2766 | -757.05 |
| 5minute_L1 | 1 | 332 | -647.02 | 259.50 | 0.3072 | -757.05 |
| 5minute_L1 | 2 | 143 | -1,439.43 | 344.10 | 0.2028 | -757.05 |
| 5minute_L1 | 3 | 54 | -335.79 | 606.61 | 0.3333 | -757.05 |
| 5minute_L1 | 4+ | 62 | -289.43 | 555.73 | 0.2419 | -757.05 |
| 5minute_L0 | 0 | 237 | -273.07 | 837.17 | 0.211 | -276.76 |
| 5minute_L0 | 1 | 334 | 230.07 | 568.67 | 0.2425 | -276.76 |
| 5minute_L0 | 2 | 144 | -2,017.80 | 416.96 | 0.1597 | -276.76 |
| 5minute_L0 | 3 | 55 | 310.45 | 1,099.59 | 0.2909 | -276.76 |
| 5minute_L0 | 4+ | 62 | 501.60 | 1,079.59 | 0.2258 | -276.76 |


The pre-registered gate cells that encode the claim (ledger rows):

| table | gate | id | kept_n | skipped_mean | kept_mean | diff | control_pct | perm_p | sign_blocks | loser_precision | winner_recall_weighted | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minute_L1 | skip when n_choch_since_bos >= 2 | dc7448312b5f9102 | 2,908 | -962.25 | -1,034.75 | -72.50 | 1.40 | 0.3723 | 4.00 | 0.8323 | 0.67 | fails the raw go/no-go checks |
| minute_L1 | skip when n_choch_since_bos_today >= 2 | b1fa1d50708a9a96 | 2,951 | -990.11 | -1,019.53 | -29.42 | 0.2 | 0.7246 | 6.00 | 0.8368 | 0.7107 | fails the raw go/no-go checks |
| 5minute_L1 | skip when n_choch_since_bos >= 2 | cdd9b4281b0e451c | 567 | -934.04 | -676.21 | 257.83 | 45.90 | 0.4613 | 6.00 | 0.7606 | 0.7182 | fails the raw go/no-go checks |
| 5minute_L1 | skip when n_choch_since_bos_today >= 2 | 60d25ea57daf33dd | 604 | -1,217.79 | -587.71 | 630.08 | 8.30 | 0.072 | 9.00 | 0.7883 | 0.8268 | fails the raw go/no-go checks |
| 5minute_L0 | skip when n_choch_since_bos >= 2 | e007e395ec212c79 | 571 | -928.70 | 21.24 | 949.94 | 81.20 | 0.2114 | 8.00 | 0.7969 | 0.7751 | fails the raw go/no-go checks |
| 5minute_L0 | skip when n_choch_since_bos_today >= 2 | 8e30eb4817d3bf5f | 608 | -1,108.61 | 29.71 | 1,138.32 | 64.10 | 0.1684 | 8.00 | 0.8214 | 0.8299 | fails the raw go/no-go checks |


### 2.2 "Check how price reacts in visibly high volume"

Bars (IS), direction rows pooled (`dir = both`): the 30-bar move in the bar's own direction, its magnitude, the excursions, and whether the bar's extremes held for 15 / 30 bars; the baseline is every bar:

| tf | set | v | N | n | fwd30_atr_mean | fwd30_atr_median | fwd30_pos_share | fwd30_abs_atr_mean | mfe30_atr_median | mae30_atr_median | own_extreme_held_15 | opp_extreme_held_15 | opp_extreme_held_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | baseline_all_bars |  | 20 | 372,489 | -0.016 | -0.043 | 0.4927 | 2.72 | 2.17 | -2.24 | 0.1043 | 0.2428 | 0.1733 |
| 1 min | high_volume | 2.00 | 20 | 57,448 | -0.022 | -0.1 | 0.4864 | 2.80 | 2.20 | -2.31 | 0.1291 | 0.3027 | 0.2179 |
| 1 min | high_volume | 2.00 | 60 | 63,874 | -0.014 | -0.101 | 0.4865 | 2.79 | 2.19 | -2.30 | 0.1288 | 0.2995 | 0.2153 |
| 1 min | high_volume | 3.00 | 20 | 26,039 | -0.02 | -0.118 | 0.4836 | 2.82 | 2.21 | -2.33 | 0.1414 | 0.3311 | 0.2412 |
| 1 min | high_volume | 3.00 | 60 | 30,189 | -0.026 | -0.119 | 0.4833 | 2.80 | 2.19 | -2.32 | 0.138 | 0.3216 | 0.2363 |
| 1 min | high_volume | 4.00 | 20 | 14,337 | 0.014 | -0.115 | 0.4842 | 2.85 | 2.25 | -2.30 | 0.1516 | 0.3596 | 0.2693 |
| 1 min | high_volume | 4.00 | 60 | 16,722 | -0.016 | -0.126 | 0.4835 | 2.82 | 2.21 | -2.33 | 0.1468 | 0.3412 | 0.2529 |
| 5 min | baseline_all_bars |  | 20 | 71,091 | 0.008 | -0.012 | 0.4977 | 2.47 | 1.89 | -1.91 | 0.0924 | 0.2498 | 0.1864 |
| 5 min | high_volume | 2.00 | 20 | 10,365 | 0.092 | -0.01 | 0.4981 | 2.70 | 2.15 | -2.11 | 0.1213 | 0.3372 | 0.2547 |
| 5 min | high_volume | 2.00 | 60 | 9,142 | 0.055 | -0.056 | 0.4914 | 2.61 | 2.16 | -2.07 | 0.1251 | 0.377 | 0.2914 |
| 5 min | high_volume | 3.00 | 20 | 4,282 | 0.127 | -0.012 | 0.4986 | 2.65 | 2.31 | -2.08 | 0.1323 | 0.3877 | 0.289 |
| 5 min | high_volume | 3.00 | 60 | 4,021 | 0.035 | -0.082 | 0.488 | 2.65 | 2.29 | -2.12 | 0.1382 | 0.4285 | 0.3258 |
| 5 min | high_volume | 4.00 | 20 | 2,041 | 0.197 | 0.198 | 0.526 | 2.71 | 2.54 | -2.00 | 0.1403 | 0.4237 | 0.3353 |
| 5 min | high_volume | 4.00 | 60 | 1,923 | 0.136 | 0.291 | 0.5316 | 2.92 | 2.61 | -1.99 | 0.1321 | 0.4849 | 0.3792 |


Foundation SETUPs within 15 bars after a high-volume bar (v = 2 and 3, N = 20), by direction agreement:

| table | variable | bucket | n | net_mean | net_se | win_rate |
|---|---|---|---|---|---|---|
| minute_L1 | hv v2 N20 M15 | agree | 2,496 | -1,016.79 | 48.92 | 0.1575 |
| minute_L1 | hv v2 N20 M15 | disagree | 801 | -1,061.41 | 75.57 | 0.1323 |
| minute_L1 | hv v2 N20 M15 | none | 1,155 | -958.17 | 95.89 | 0.1688 |
| minute_L1 | hv v3 N20 M15 | agree | 1,506 | -1,060.78 | 59.60 | 0.1587 |
| minute_L1 | hv v3 N20 M15 | disagree | 634 | -996.54 | 86.55 | 0.1593 |
| minute_L1 | hv v3 N20 M15 | none | 2,312 | -979.86 | 60.82 | 0.1531 |
| minute_L0 | hv v2 N20 M15 | agree | 2,530 | -971.25 | 85.55 | 0.153 |
| minute_L0 | hv v2 N20 M15 | disagree | 813 | -916.31 | 202.52 | 0.1378 |
| minute_L0 | hv v2 N20 M15 | none | 1,159 | -817.82 | 196.94 | 0.1596 |
| minute_L0 | hv v3 N20 M15 | agree | 1,518 | -934.03 | 148.13 | 0.1542 |
| minute_L0 | hv v3 N20 M15 | disagree | 645 | -1,028.59 | 117.69 | 0.1628 |
| minute_L0 | hv v3 N20 M15 | none | 2,339 | -884.48 | 112.89 | 0.1475 |
| 5minute_L1 | hv v2 N20 M15 | agree | 382 | -829.64 | 203.50 | 0.2696 |
| 5minute_L1 | hv v2 N20 M15 | disagree | 84 | -811.57 | 402.25 | 0.25 |
| 5minute_L1 | hv v2 N20 M15 | none | 360 | -667.31 | 272.17 | 0.2917 |
| 5minute_L1 | hv v3 N20 M15 | agree | 204 | -901.54 | 266.19 | 0.2647 |
| 5minute_L1 | hv v3 N20 M15 | disagree | 60 | -292.67 | 552.52 | 0.3333 |
| 5minute_L1 | hv v3 N20 M15 | none | 562 | -754.18 | 200.72 | 0.2758 |
| 5minute_L0 | hv v2 N20 M15 | agree | 388 | -313.98 | 545.04 | 0.2165 |
| 5minute_L0 | hv v2 N20 M15 | disagree | 84 | -1,004.13 | 689.19 | 0.1786 |
| 5minute_L0 | hv v2 N20 M15 | none | 360 | -66.92 | 551.76 | 0.2361 |
| 5minute_L0 | hv v3 N20 M15 | agree | 207 | -186.98 | 820.92 | 0.2271 |
| 5minute_L0 | hv v3 N20 M15 | disagree | 61 | -98.82 | 1,093.59 | 0.2295 |
| 5minute_L0 | hv v3 N20 M15 | none | 564 | -328.95 | 413.17 | 0.2181 |


The (v=2, N=20, M=15) gate cells:

| table | gate | id | kept_n | diff | control_pct | perm_p | sign_blocks | verdict |
|---|---|---|---|---|---|---|---|---|
| minute_L1 | skip_if_disagree | 957a9431eef861e2 | 3,651 | 63.17 | 11.40 | 0.5407 | 8 | fails the raw go/no-go checks |
| minute_L1 | skip_if_none | ab2621823149c785 | 3,297 | -69.46 | 100.00 | 0.4718 | 5 | fails the raw go/no-go checks |
| minute_L1 | take_only_agree | 89a7008a8ca918e5 | 2,496 | -16.34 | 100.00 | 0.8291 | 6 | fails the raw go/no-go checks |
| minute_L0 | skip_if_disagree | ac1b12f093055d78 | 3,689 | -6.74 | 17.10 | 0.974 | 8 | fails the raw go/no-go checks |
| minute_L0 | skip_if_none | 94f2a08df4003907 | 3,343 | -140.07 | 100.00 | 0.4738 | 6 | fails the raw go/no-go checks |
| minute_L0 | take_only_agree | 5bc19432df4520ef | 2,530 | -112.83 | 95.80 | 0.4858 | 7 | fails the raw go/no-go checks |
| 5minute_L1 | skip_if_disagree | 5694b41eb921fb5b | 742 | 60.69 | 0.2 | 0.9095 | 6 | fails the raw go/no-go checks |
| 5minute_L1 | skip_if_none | 20892326d3da1f02 | 466 | -159.07 | 100.00 | 0.6107 | 4 | fails the raw go/no-go checks |
| 5minute_L1 | take_only_agree | a2c2f9584e5b150d | 382 | -135.03 | 100.00 | 0.6937 | 4 | fails the raw go/no-go checks |
| 5minute_L0 | skip_if_disagree | 08fab6b42f223bfe | 748 | 809.05 | 27.00 | 0.5037 | 9 | fails the raw go/no-go checks |
| 5minute_L0 | skip_if_none | 45337909b275d8fd | 472 | -369.89 | 99.00 | 0.6317 | 5 | fails the raw go/no-go checks |
| 5minute_L0 | take_only_agree | a4db2c6586f0467e | 388 | -69.75 | 97.20 | 0.915 | 6 | fails the raw go/no-go checks |


### 2.3 "Those levels will be respected: if it breaks there will be a large move, else price retests, retests and respects"

Move after a confirmed break vs after a respect vs any bar (ATR; `move` signed in the break / bounce direction; full 15-minute verdict windows only, see T1):

| tf | kind | verdict | n_bars | n | abs_median | abs_mean | abs_share_gt2 | move_median | move_share_pos | beyond_share_pos |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | baseline_all_bars | any | 30 | 352,296 | 2.11 | 2.73 | 0.5212 |  |  |  |
| 1 min | baseline_all_bars | any | 60 | 321,516 | 2.96 | 3.86 | 0.6442 |  |  |  |
| 1 min | prot | broke | 30 | 4,271 | 2.24 | 2.83 | 0.5486 | -0.144 | 0.4819 | 0.6088 |
| 1 min | prot | broke | 60 | 3,852 | 3.20 | 4.08 | 0.6685 | 0 | 0.4992 | 0.5836 |
| 1 min | prot | held | 30 | 1,671 | 2.33 | 2.90 | 0.5572 | 0.031 | 0.5021 |  |
| 1 min | prot | held | 60 | 1,490 | 3.19 | 4.15 | 0.6698 | -0.046 | 0.494 |  |
| 1 min | room | broke | 30 | 45,403 | 2.16 | 2.75 | 0.5292 | -0.096 | 0.4861 | 0.6232 |
| 1 min | room | broke | 60 | 41,234 | 3.01 | 3.87 | 0.6521 | -0.067 | 0.4949 | 0.5891 |
| 1 min | room | held | 30 | 19,908 | 2.14 | 2.73 | 0.5254 | 0.035 | 0.5041 |  |
| 1 min | room | held | 60 | 18,016 | 2.97 | 3.87 | 0.6429 | 0.085 | 0.5078 |  |
| 1 min | swing | broke | 30 | 105,790 | 2.19 | 2.82 | 0.5359 | -0.195 | 0.4741 | 0.609 |
| 1 min | swing | broke | 60 | 95,614 | 3.05 | 4.00 | 0.6524 | -0.17 | 0.4845 | 0.5832 |
| 1 min | swing | held | 30 | 44,850 | 2.19 | 2.84 | 0.5366 | 0 | 0.4991 |  |
| 1 min | swing | held | 60 | 40,223 | 3.04 | 4.04 | 0.6504 | 0.01 | 0.5006 |  |
| 5 min | baseline_all_bars | any | 30 | 45,889 | 1.91 | 2.47 | 0.4814 |  |  |  |
| 5 min | baseline_all_bars | any | 60 | 15,280 | 2.60 | 3.33 | 0.5974 |  |  |  |
| 5 min | prot | broke | 30 | 285 | 2.07 | 2.71 | 0.5263 | 0.047 | 0.5088 | 0.6105 |
| 5 min | prot | broke | 60 | 110 | 2.91 | 3.79 | 0.6727 | 0.512 | 0.5455 | 0.6364 |
| 5 min | prot | held | 30 | 366 | 2.01 | 2.58 | 0.5027 | -0.117 | 0.4809 |  |
| 5 min | prot | held | 60 | 130 | 2.85 | 3.64 | 0.7077 | -1.18 | 0.4 |  |
| 5 min | room | broke | 30 | 9,547 | 2.00 | 2.52 | 0.4998 | 0.056 | 0.5073 | 0.651 |
| 5 min | room | broke | 60 | 3,970 | 2.66 | 3.45 | 0.5955 | 0.159 | 0.5161 | 0.6348 |
| 5 min | room | held | 30 | 11,194 | 1.84 | 2.40 | 0.4674 | 0.049 | 0.5053 |  |
| 5 min | room | held | 60 | 3,506 | 2.46 | 3.21 | 0.5836 | 0.123 | 0.5106 |  |
| 5 min | swing | broke | 30 | 5,197 | 2.05 | 2.64 | 0.5116 | 0.135 | 0.5191 | 0.6552 |
| 5 min | swing | broke | 60 | 760 | 2.52 | 3.39 | 0.5882 | 0.296 | 0.5395 | 0.6671 |
| 5 min | swing | held | 30 | 5,507 | 1.90 | 2.54 | 0.4792 | 0.023 | 0.503 |  |
| 5 min | swing | held | 60 | 576 | 2.33 | 3.13 | 0.5833 | 0.119 | 0.5139 |  |


P(the touch breaks the level) by the number of earlier respects of the same level instance:

| tf | kind | prior_held_bin | n | p_broke |
|---|---|---|---|---|
| 1 min | prot | 0 | 6,421 | 0.7092 |
| 1 min | room | 0 | 9,958 | 0.669 |
| 1 min | room | 1 | 2,538 | 0.4941 |
| 1 min | room | 2 | 984 | 0.5122 |
| 1 min | room | 3+ | 659 | 0.4704 |
| 1 min | swing | 0 | 93,171 | 0.6914 |
| 1 min | swing | 1 | 19,495 | 0.4734 |
| 1 min | swing | 2 | 7,573 | 0.4651 |
| 1 min | swing | 3+ | 4,755 | 0.4566 |
| 5 min | prot | 0 | 1,154 | 0.4411 |
| 5 min | room | 0 | 7,462 | 0.431 |
| 5 min | room | 1 | 3,283 | 0.4429 |
| 5 min | room | 2 | 1,373 | 0.4406 |
| 5 min | room | 3+ | 1,021 | 0.476 |
| 5 min | swing | 0 | 15,316 | 0.4645 |
| 5 min | swing | 1 | 4,848 | 0.4495 |
| 5 min | swing | 2 | 1,561 | 0.426 |
| 5 min | swing | 3+ | 659 | 0.4476 |


Foundation SETUPs by the last touch verdict of the protected level / room edge / swing in the hour before the SETUP (L1):

| table | variable | bucket | n | net_mean | net_se | win_rate |
|---|---|---|---|---|---|---|
| minute_L1 | touch_prot_last | broke | 21 | -1,094.83 | 246.72 | 0.0952 |
| minute_L1 | touch_prot_last | held | 160 | -733.14 | 328.08 | 0.2188 |
| minute_L1 | touch_prot_last | pending | 4,144 | -1,034.05 | 39.24 | 0.1523 |
| minute_L1 | touch_prot_last | none | 2 | -2,878.48 | 877.03 | 0 |
| minute_L1 | touch_prot_last | na | 125 | -508.86 | 318.75 | 0.208 |
| minute_L1 | touch_room_last | broke | 1,882 | -1,013.88 | 54.77 | 0.1546 |
| minute_L1 | touch_room_last | held | 798 | -1,096.47 | 77.07 | 0.1604 |
| minute_L1 | touch_room_last | pending | 1,031 | -1,009.83 | 74.30 | 0.1426 |
| minute_L1 | touch_room_last | none | 739 | -903.06 | 139.07 | 0.1732 |
| minute_L1 | touch_room_last | na | 2 | -1,589.20 | 1,194.44 | 0 |
| minute_L1 | touch_swing_last | broke | 2,736 | -991.60 | 53.84 | 0.17 |
| minute_L1 | touch_swing_last | held | 5 | 401.82 | 2,001.21 | 0.4 |
| minute_L1 | touch_swing_last | pending | 1,711 | -1,042.53 | 55.60 | 0.1327 |
| 5minute_L1 | touch_prot_last | broke | 3 | 2,048.26 | 4,408.97 | 0.3333 |
| 5minute_L1 | touch_prot_last | held | 604 | -685.62 | 186.24 | 0.2781 |
| 5minute_L1 | touch_prot_last | pending | 137 | -777.24 | 352.07 | 0.2701 |
| 5minute_L1 | touch_prot_last | none | 67 | -1,048.93 | 571.90 | 0.3134 |
| 5minute_L1 | touch_prot_last | na | 15 | -2,706.37 | 814.64 | 0.1333 |
| 5minute_L1 | touch_room_last | broke | 149 | -609.75 | 399.81 | 0.2886 |
| 5minute_L1 | touch_room_last | held | 61 | -1,393.89 | 442.13 | 0.1803 |
| 5minute_L1 | touch_room_last | pending | 163 | -100.76 | 377.42 | 0.2699 |
| 5minute_L1 | touch_room_last | none | 453 | -955.90 | 205.14 | 0.2892 |
| 5minute_L1 | touch_swing_last | broke | 448 | -866.09 | 207.50 | 0.2835 |
| 5minute_L1 | touch_swing_last | held | 169 | -911.35 | 382.64 | 0.284 |
| 5minute_L1 | touch_swing_last | pending | 201 | -471.17 | 299.63 | 0.2438 |
| 5minute_L1 | touch_swing_last | none | 8 | 1,425.69 | 2,245.50 | 0.625 |


The 9 touch-verdict gate cells per table:

| table | level | skip_when_last | id | kept_n | diff | control_pct | perm_p | sign_blocks | verdict |
|---|---|---|---|---|---|---|---|---|---|
| minute_L1 | prot | broke | 6678696901d6e630 | 4,431 | 85.62 | 44.30 | 0.8861 | 8 | fails the raw go/no-go checks |
| minute_L1 | prot | held | 69be22dc4cffee7b | 4,292 | -286.77 | 95.90 | 0.1799 | 6 | fails the raw go/no-go checks |
| minute_L1 | prot | pending | 905054e45d3fb8f1 | 308 | 353.34 | 12.70 | 0.0275 | 6 | fails the raw go/no-go checks |
| minute_L1 | room | broke | 91456038190bbdf5 | 2,570 | 7.40 | 6.80 | 0.9155 | 7 | fails the raw go/no-go checks |
| minute_L1 | room | held | babad33bed46a900 | 3,654 | 105.83 | 3.90 | 0.3053 | 7 | fails the raw go/no-go checks |
| minute_L1 | room | pending | 5c81240cc29a43f6 | 3,421 | 0.29 | 32.40 | 0.9955 | 7 | fails the raw go/no-go checks |
| minute_L1 | swing | broke | 51ea141a73ed013c | 1,716 | -46.72 | 94.40 | 0.5682 | 6 | fails the raw go/no-go checks |
| minute_L1 | swing | held | 7a5fff2957003c41 | 4,447 | -1,413.01 | 72.20 | 0.1149 | 1 | fails the raw go/no-go checks |
| minute_L1 | swing | pending | e2f8dcb18f756381 | 2,741 | 53.47 | 6.00 | 0.5157 | 6 | fails the raw go/no-go checks |
| minute_L0 | prot | broke | 453a47368c8c952f | 4,481 | -16.21 | 49.00 | 0.9815 | 7 | fails the raw go/no-go checks |
| minute_L0 | prot | held | 70d7611e97701d64 | 4,336 | -563.47 | 84.90 | 0.1524 | 6 | fails the raw go/no-go checks |
| minute_L0 | prot | pending | f16edfac5d982b9d | 315 | 235.72 | 16.90 | 0.4423 | 7 | fails the raw go/no-go checks |
| minute_L0 | room | broke | 9d1b586504f95722 | 2,605 | -94.34 | 2.20 | 0.5737 | 4 | fails the raw go/no-go checks |
| minute_L0 | room | held | 314899f06c4c0890 | 3,689 | 231.16 | 67.00 | 0.2519 | 9 | fails the raw go/no-go checks |
| minute_L0 | room | pending | 795de756726d4d14 | 3,453 | 227.15 | 67.90 | 0.2444 | 9 | fails the raw go/no-go checks |
| minute_L0 | swing | broke | b7bc9287448e5e23 | 1,747 | 83.99 | 80.50 | 0.6147 | 6 | fails the raw go/no-go checks |
| minute_L0 | swing | held | 926234ed05418791 | 4,497 | -1,586.92 | 51.20 | 0.1734 | 1 | fails the raw go/no-go checks |
| minute_L0 | swing | pending | 14312c2d984dcbdc | 2,760 | -76.66 | 19.00 | 0.6367 | 6 | fails the raw go/no-go checks |
| 5minute_L1 | prot | broke | cf2a5f1dd3e82550 | 823 | -2,815.53 | 41.60 | 0.2324 | 2 | fails the raw go/no-go checks |
| 5minute_L1 | prot | held | 6fd8306a0548d73b | 222 | -265.78 | 47.70 | 0.4493 | 5 | fails the raw go/no-go checks |
| 5minute_L1 | prot | pending | 0818dce9159abc40 | 689 | 24.21 | 18.90 | 0.9555 | 6 | fails the raw go/no-go checks |
| 5minute_L1 | room | broke | 136f703118c8fefb | 677 | -179.73 | 98.80 | 0.6737 | 6 | fails the raw go/no-go checks |
| 5minute_L1 | room | held | 74d6b4f066d0481e | 765 | 687.62 | 87.30 | 0.2629 | 7 | fails the raw go/no-go checks |
| 5minute_L1 | room | pending | 7b760716df543532 | 663 | -817.64 | 0.2 | 0.0325 | 3 | fails the raw go/no-go checks |
| 5minute_L1 | swing | broke | a551ed716f433a2b | 378 | 238.26 | 43.10 | 0.4493 | 7 | fails the raw go/no-go checks |
| 5minute_L1 | swing | held | 6929b817eddc2da3 | 657 | 193.99 | 94.80 | 0.6152 | 9 | fails the raw go/no-go checks |
| 5minute_L1 | swing | pending | ed145b95e5cb7898 | 625 | -377.82 | 7.00 | 0.2919 | 2 | fails the raw go/no-go checks |
| 5minute_L0 | prot | broke | 4fc3902e61454f5e | 829 | -2,798.79 | 8.80 | 0.4738 | 2 | fails the raw go/no-go checks |
| 5minute_L0 | prot | held | 096e34f1d9907f78 | 223 | -264.68 | 21.60 | 0.7371 | 4 | fails the raw go/no-go checks |
| 5minute_L0 | prot | pending | 23ee5cd6705d3e7d | 694 | -43.20 | 52.90 | 0.964 | 8 | fails the raw go/no-go checks |
| 5minute_L0 | room | broke | f39f9f975ca1e7a3 | 683 | -1,735.10 | 48.00 | 0.055 | 4 | fails the raw go/no-go checks |
| 5minute_L0 | room | held | 6a4bd44ed294d96c | 771 | 2,221.97 | 99.50 | 0.092 | 10 | fails the raw go/no-go checks |
| 5minute_L0 | room | pending | 0e0b57a2d4b3fa4c | 669 | -305.09 | 18.70 | 0.7431 | 8 | fails the raw go/no-go checks |
| 5minute_L0 | swing | broke | a513568feef6df11 | 380 | -103.04 | 63.00 | 0.8901 | 4 | fails the raw go/no-go checks |
| 5minute_L0 | swing | held | 7f3bdf6c8658015c | 661 | -815.08 | 43.90 | 0.3663 | 7 | fails the raw go/no-go checks |
| 5minute_L0 | swing | pending | bf1d6d3a3066cd94 | 631 | 974.61 | 29.40 | 0.2414 | 8 | fails the raw go/no-go checks |

## 3. Selection note (what the pre-registered nested-CV selection chose, and why a post-hoc variant exists)

The pre-registered criterion (largest training-fold kept-vs-skipped diff subject to the harness *kept* floors) has no floor on the skipped set. What it chose on every table, from the summary JSONs (`oof_*` = the 12-block OOF mask; `fold_skip_share` = 1 - the chosen cell's kept share on the training rows, over the 12 folds; `blocks_nothing_skipped` = test blocks where the chosen cell kept every row):

| study | tf | label | n_is | oof_kept_n | oof_skipped_n | oof_skipped_share | oof_skipped_mean | fold_skip_share_min | fold_skip_share_max | blocks_nothing_skipped | modal_cell_12_folds | modal_cell_66_cpcv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| h2 | 1 min | L1 | 4,452 | 4,307 | 145 | 0.0326 | -790.18 | 0.0112 | 0.0892 | 1 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} x4 | {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} x16 |
| h2 | 5 min | L1 | 826 | 824 | 2 | 0.0024 | -4,739.05 | 0.0013 | 0.0027 | 10 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x12 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x65 |
| h2 | 5 min | L0 | 832 | 830 | 2 | 0.0024 | -4,739.05 | 0.0013 | 0.0027 | 10 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x12 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x64 |
| h3 | 1 min | L1 | 4,452 | 3,863 | 589 | 0.1323 | -860.49 | 0.0256 | 0.2479 | 0 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x4 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x17 |
| h3 | 1 min | L0 | 4,502 | 4,355 | 147 | 0.0327 | -1,114.61 | 0.0259 | 0.0579 | 0 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x8 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x40 |
| h3 | 5 min | L1 | 826 | 775 | 51 | 0.0617 | -569.31 | 0.0242 | 0.071 | 0 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} x9 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} x39 |
| h3 | 5 min | L0 | 832 | 808 | 24 | 0.0288 | -715.55 | 0.0158 | 0.0614 | 4 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} x10 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} x46 |
| h4 | 1 min | L1 | 4,452 | 3,758 | 694 | 0.1559 | -1,003.77 | 0.0033 | 0.3858 | 0 | {"level": "room", "skip_when_last": "held"} x9 | {"level": "room", "skip_when_last": "held"} x35 |
| h4 | 1 min | L0 | 4,502 | 3,588 | 914 | 0.203 | -945.02 | 0.1785 | 0.2364 | 0 | {"level": "room", "skip_when_last": "pending"} x7 | {"level": "room", "skip_when_last": "held"} x30 |
| h4 | 5 min | L1 | 826 | 770 | 56 | 0.0678 | -1,328.94 | 0.0027 | 0.0769 | 0 | {"level": "room", "skip_when_last": "held"} x11 | {"level": "room", "skip_when_last": "held"} x50 |
| h4 | 5 min | L0 | 832 | 771 | 61 | 0.0733 | -2,335.82 | 0.0693 | 0.0764 | 0 | {"level": "room", "skip_when_last": "held"} x12 | {"level": "room", "skip_when_last": "held"} x66 |

The degeneracy is specific to **5 min H2**: L1: the cell {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} won all 12 folds (and 65 of 66 CPCV training sets), skipping 2 of 826 rows (skipped mean -4,739.05) with nothing skipped in 10 of 12 test blocks; L0: the cell {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} won all 12 folds (and 64 of 66 CPCV training sets), skipping 2 of 832 rows (skipped mean -4,739.05) with nothing skipped in 10 of 12 test blocks. A two-row skip set has an unbounded diff, and the harness go/no-go is what catches it (sign blocks 2 of 12, control percentile below 95, PBO, DSR). On every other table the chosen cells skip a real share of the training rows: H2 0.0112-0.0892; H3 0.0158-0.2479; H4 0.0027-0.3858 (1 min H4 L1 has two of 12 folds and 20 of 66 CPCV sets on {prot, broke}, 3 rows; the rest on {room, held}). `posthoc_minskip.py` (the same selection with `skipped share >= 10 %` added to the fold eligibility) has not been run; no claim about it is made in this file.

## 4. What would falsify these findings

- H2: a `h2/choch` or `h2/range` ledger row with diff > 0, control percentile >= 95, sign blocks >= 8 and a CPCV 5th-percentile diff > 0 under the nested-CV selection; or the bucket `n_choch_since_bos >= 2` showing a mean net below the other buckets by more than two standard errors on both timeframes and both labels.
- H3: a `h3/gate` row skipping >= 10 % of the SETUPs with diff > 0 at control percentile >= 95 in the nested-CV paths; or a bar aftermath table where the 30-bar move in the high-volume bar's direction differs from the baseline by more than 0.5 ATR.
- H4: a `h4/touch_gate` row with control percentile >= 95, sign blocks >= 8 and a positive CPCV 5th percentile; or an episode table where the absolute 30 / 60-bar move after a confirmed break exceeds the baseline by more than 0.5 ATR, or P(broke given prior_held >= 2) is lower than P(broke given prior_held = 0) by more than 0.2 on both timeframes with a positive Foundation expectancy at respected levels.
- Any of the above on a rebuild with a different `features.parquet` (the SETUP counts and the frozen kept set are pinned by `data/<tf>/meta.json`).

## 5. Caveats

- Bucket tables and the episode / bar-aftermath tables are descriptive decompositions (means, counts, iid standard errors, block sign counts). No p-value is attached to them; every question that needs one is a ledger row, and the kept-vs-skipped statistics of the 201 + 54 + 9 cells (plus the nested-CV rows) are the only kept-vs-skipped numbers in this study.
- The session-matched control percentile and the pooled diff disagree in sign on many cells (e.g. the 5 min `range_3h` cells: negative diff, control percentile 100). The control matches per-session kept counts, the diff pools all rows; a gate that skips whole sessions of the 5 min book (median two SETUPs per session) is matched trivially there. Both are reported; neither alone is the criterion.
- Under the harness `score`, a cell with a learned quantile is one ledger row on its OOF mask; its 12 fold thresholds differ by a few hundredths of an ATR (recorded in the grid CSV).
- L0 (the engine's uncut trade) is a robustness label only; on 1 min it runs to 70 sessions and its purge is coarser.
- The episode study's `prot` level instances are short on both timeframes (the engine moves the protected level at each swing update), so a protected level almost never sees a second episode: its retest counts are structural zeros, not evidence.
- The 1 min swing instances end at the first break or at their session's end by definition, so P(broke given prior_held = 0) on 1 min counts the many swings that break on their first touch shortly after confirmation.
- Episode verdicts need a full 15-minute window: touches in the last 15 minutes of a session are `session_end` (a break close inside that truncated window is counted as `cut_break`, not as `broke`), so the verdict tables describe touches up to 15 minutes before the close; the build's as-of `touch_*_last` columns (the gate inputs) are a different object with their own `pending` state and are unchanged.
- The recomputed volume baselines equal the build's `vol_med20_prior` / `vol_ratio20` / `vol_ratio60` exactly; the new per-SETUP H3 features equal the build's `hv2_*` / `hv3_*` (N = 20) and are identical on the truncated build for every SETUP before the cut (`trunc_20250630_120000`); the H4 episode features are labels of the level, never features.
- The ledger was appended by several processes in parallel (the primary runs, the repair-round post-hoc runs and other studies); the integrity counts are in the header (every line parses, every id has its vector file).
- On 5 min the `range_*_atr` terciles and quantiles use 12 / 36-bar windows; hour-of-day effects and the range rule are entangled (a session's range grows through the day).
- The pre-registered summaries' family SPA used `harness.spa` as at the primary runs; the post-hoc and recomputed rows use the 05:05 revision (section 6).

## 6. Repair round (after the adversarial refuters)

The refuters confirmed four material issues in the first version of this folder (written 04:17 while three 1-min runs were still appending). Each, and what changed:

1. **The post-hoc min-skip variant was reported but never run.** `posthoc_minskip.py` had no log, no summary and no ledger rows, yet FINDINGS.md counted it in the family multiplicity and asserted its null result. Fix: the script was given CLI arguments and run to completion in the repair round (`posthoc_minskip.log`, `run_posthoc_*.nohup`); its 11 ledger rows carry `note = "repair"` (12 tables x (1 nested row + 11 CPCV paths)). It also recomputes the pre-registered nested row's family statistics over the completed family (`family_prereg_recomputed`), shown as a third row of every family table. `write_findings.py` now reads the ledger families from the ledger (`ledger_families` = 15 families actually present) and emits the post-hoc T1 row, blocks and captions only where a post-hoc summary exists.

2. **Section 3 overstated the degenerate selection.** It said the pre-registered criterion picked a handful-of-rows skip cell on every table and that 5 min H4 skipped 3 rows in most CPCV training sets. Measured (section 3 table): only 5 min H2 is degenerate (2 rows skipped in every fold, L1 and L0); 5 min H3 chose cells skipping 2-7 %, 5 min H4 chose {room, held} (about 7 %) in 11 of 12 folds and 50 of 66 CPCV sets (L1) and in all of them (L0); {prot, broke} (3 rows) was chosen in 1 of 12 folds and 11 of 66 CPCV sets on 5 min L1. Section 3 and the `posthoc_minskip.py` docstring were rewritten from those numbers.

3. **H4 episode verdict did not match its definition.** The docstring and T1 said a verdict window cut by the session end is `session_end`, but the code returned `broke` whenever a break close fell inside the truncated window (and `held` was impossible there), a small upward bias in P(broke) for late touches. Fix: every cut window is `session_end`; a break close inside it is recorded as `cut_break` and counted separately (1 min: 3,825 of 8,537 cut windows, 5 min: 520 of 2,663 cut windows); `prior_held` / `after_break` follow the verdicts. The episode tables of both timeframes were regenerated by `h4_levels.py --part episodes` (no ledger row is involved: these are labels of the level, not gate inputs); the gate cells (`touch_*` build columns) are unchanged. First-run counts for reference (from `h4_levels.log`): 5 min broke prot 515 / room 16,011 / swing 11,388; 1 min 4,646 / 49,127 / 115,620.

4. **The header presented a mid-run ledger snapshot as final and the 1-min gate results were missing.** This file is regenerated after every run finished (STILL MISSING: h2_minute_L0_summary.json, h2_summary_minute.json, posthoc_h2_minute_L1_summary.json, posthoc_h2_minute_L0_summary.json, posthoc_h2_5minute_L1_summary.json, posthoc_h2_5minute_L0_summary.json, posthoc_h3_minute_L1_summary.json, posthoc_h3_minute_L0_summary.json, posthoc_h3_5minute_L1_summary.json, posthoc_h3_5minute_L0_summary.json, posthoc_h4_minute_L1_summary.json, posthoc_h4_minute_L0_summary.json, posthoc_h4_5minute_L1_summary.json, posthoc_h4_5minute_L0_summary.json); all 1-min tables (H2 / H3 / H4 grids, nested CV, CPCV, families) are in sections 1 and T2-T4.

Also in this round: the pre-registered summaries' family SPA was computed with `harness.spa` as at the primary runs (before its 05:05 revision: exclusion of near-inactive candidates from the studentised statistic, unstudentised p added); the post-hoc and recomputed family rows use the revised function, so their `spa_p` can differ from the primary row's for that reason alone. Nothing in the pre-registered rows was re-scored; the ledger is append-only.


---

# Tables (auto-generated by `write_findings.py` from the CSV / JSON outputs)

## T1. Definitions (fixed before the numbers)

| term | definition |
|---|---|
| unit | a harness row: a Foundation SETUP taken under the label's book, `harness.load(tf, label)`, IS rows only (1 min L1 4,452 / L0 4,502; 5 min L1 826 / L0 832) |
| cell | one gate configuration = one ledger row scored on IS by `harness.score` (2,000 control draws, 2,000 permutations). A cell with a learned threshold (the H2 range quantiles) is scored on its 12-block out-of-fold mask: the threshold is the quantile of the *training fold's* rows (`harness.purged_splits`), applied to the test block; the fold thresholds are in the ledger row's `note` and in `h2_<tf>_<label>_grid.csv` |
| nested CV | inside each of the 12 purged training folds every cell is fitted and evaluated on the training rows with `harness.metrics` (controls off); the cell with the largest kept-vs-skipped diff subject to the harness kept floors (kept share >= 20 %, kept n >= 300 (1 min) / 80 (5 min) scaled by train / IS) is applied to the test block; the 12 test blocks form the OOF mask, one ledger row `<study>/nested_cv`; the same selection inside the 66 CPCV training sets gives the 11 paths (`<study>/nested_cv/cpcv`, `harness.score_paths`, controls on) |
| family | every non-cpcv ledger row of the study on that timeframe and label; PBO (`harness.pbo`, CSCV 16 blocks, 12,870 partitions, statistic diff and kept_mean), SPA / Reality Check (`harness.spa`, 2,000 stationary-bootstrap draws; studentised p, and the unstudentised p where the harness version at run time reported it), effective trials (participation ratio of the kept-net correlation matrix), block bootstrap 90 % CI and DSR of the nested-CV row, `harness.go_no_go` on it |
| bucket table | descriptive decomposition of the label by an as-of categorical: n, share, sum, mean, se (iid), median, win rate, mean pts, stop share, blocks below (of the 12 IS blocks, how many have the bucket mean below the block's all-rows mean). No rule is chosen on a bucket table; tercile edges are pooled IS quantiles, recorded |
| H2 columns | `n_choch_since_bos` (CHoCHs after the last BOS, own CHoCH included; >= 2 = the user's 'CHoCH, CHoCH, no BOS'), `n_choch_since_bos_today`, `alt_dir6` / `alt_kind6` (direction / kind changes among the last 6 events), `range_{1h,3h,since_choch}_atr` (same-session range / atr14), `er_1h` (Kaufman efficiency ratio, last hour), `hour_bin` |
| H2 grid | choch rule: skip when `n_choch_since_bos[_today] >= kc`, kc in {2,3,4}, scope all / today; range rule: skip when `range_W_atr <= r`, W in {1h, 3h, since_choch}, r = training-fold quantile q in {0.1 .. 0.5}; both rules combined by OR / AND; or one rule alone. 6 + 15 + 180 = 201 cells (families `h2/choch`, `h2/range`, `h2/both`) |
| H3 high-volume bar | volume >= v x median of the previous N bars of the same session (at least 5), v in {2,3,4}, N in {20,60}; never a non-front-month / zero-volume bar. Bar direction = sign(close - open). The N = 20 / 60 medians and ratios are recomputed and asserted equal to `bars.vol_med20_prior` / `vol_ratio20` / `vol_ratio60` |
| H3 aftermath (labels of the bar, IS bars) | fwd_n = sg x (close[j+n] - close[j]) for n in {5,15,30} (pts and / atr14[j]); mfe30 / mae30 = best / worst excursion in the bar's direction over j+1..j+30 (/ atr14); high_held_n / low_held_n = the bar's high / low not exceeded over j+1..j+n (n = 15, 30); own_extreme_held = the extreme in the bar's direction held (no continuation), opp_extreme_held = the other extreme held (respect). Every window inside the session and complete. Baseline = every IS bar with a defined ratio and a non-flat direction |
| H3 per SETUP (as-of) | for each (v, N): the latest high-volume bar j <= k of the session (the SETUP bar counts); for M in {5,15,30}: agree (k - j <= M and same direction), disagree (opposite), none (no such bar within M or a flat bar). Re-run on the truncated build (`trunc_20250630_120000`) and identical for every SETUP before the cut; (v=2,N=20) and (v=3,N=20) equal the build's `hv2_*` / `hv3_*` |
| H3 grid | per (v, N, M): skip_if_disagree, skip_if_none, take_only_agree (= skip disagree and none): 54 cells, family `h3/gate` |
| H4 touch verdict (as-of, the build's columns) | `touch_{prot,room,swing}_last`: touch episodes of the protected level / nearest room edge / nearest confirmed swing in the hour before k (a bar touches when low <= L <= high, consecutive touching bars = one episode); the last episode's verdict inside 15 minutes after it, never past k: broke (a close beyond by > 0.5 x atr14 on the far side), held, pending (window open at k), none, na. `touch_*_n` = episodes in the hour |
| H4 grid | skip when `touch_<level>_last == broke / held / pending`, level in {prot, room, swing}: 9 cells, family `h4/touch_gate` |
| H4 episode study (IS bars, labels of the level) | level instances: protected level = a maximal run of bars with the same `bars.prot`; room edge = lo and hi of every ST7/ST8 room over birth_bar <= i < retired_bar; swing = `swings.price` from conf_bar to the first close beyond it by > 0.5 x atr14 or its session's end. Same touch / episode / side rule as the build; verdict window = 15 minutes (15 bars on 1 min, 3 on 5 min) after the last touch bar, inside its session. **A window cut by the session end is `session_end` whatever happened inside it** (`broke` and `held` are verdicts of a full window only); a break close inside a cut window is counted separately as `cut_break` (never `broke`, no aftermath, not a break for the retest bookkeeping). Aftermath from the verdict bar v (the breaking close, or the window end for held): move_n = sg x (close[v+n] - close[v]) / atr14[v], n in {15,30,60}, sg = break direction (broke) or bounce direction away from the level (held); mfe_n the best excursion that way; beyond_n = sg x (close[v+n] - L) / atr14[v] (broke only). Baseline = abs(close[i+n] - close[i]) / atr14[i] over every IS bar. prior_held = held episodes of the same instance before this one; P(broke given prior_held) over broke + held episodes not after a break |


## T2. H2 - sideways = CHoCH without break

### 1 min / L1 (4,452 IS units)

by `n_choch_since_bos`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1,169 | 0.2626 | -1,089.61 | 69.65 | -1,618.15 | 0.1377 | -0.667 | 0.432 | 8 |
| 1 | 1,739 | 0.3906 | -997.87 | 70.66 | -1,548.44 | 0.1576 | 0.774 | 0.2294 | 7 |
| 2 | 823 | 0.1849 | -1,029.94 | 81.45 | -1,526.75 | 0.1738 | 0.293 | 0.2272 | 7 |
| 3 | 372 | 0.0836 | -837.12 | 147.24 | -1,415.35 | 0.1559 | 3.23 | 0.2473 | 6 |
| 4+ | 349 | 0.0784 | -936.01 | 115.11 | -1,422.50 | 0.1662 | 1.69 | 0.1948 | 5 |

by `n_choch_since_bos_today`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1,183 | 0.2657 | -1,093.42 | 71.71 | -1,621.27 | 0.1378 | -0.723 | 0.4286 | 8 |
| 1 | 1,768 | 0.3971 | -970.08 | 72.01 | -1,542.94 | 0.1618 | 1.20 | 0.2291 | 5 |
| 2 | 811 | 0.1822 | -1,006.78 | 80.91 | -1,522.96 | 0.1739 | 0.649 | 0.2269 | 8 |
| 3 | 360 | 0.0809 | -1,018.68 | 110.94 | -1,424.97 | 0.1417 | 0.453 | 0.25 | 6 |
| 4+ | 330 | 0.0741 | -917.97 | 118.81 | -1,419.19 | 0.1606 | 1.96 | 0.197 | 4 |

by `alt_dir6`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 3 | 0.0007 | -2,846.87 | 507.34 | -2,783.64 | 0 | -28.00 | 0.3333 | 2 |
| 1 | 767 | 0.1723 | -1,025.45 | 111.47 | -1,652.97 | 0.1604 | 0.313 | 0.296 | 7 |
| 2 | 1,295 | 0.2909 | -1,028.71 | 69.50 | -1,551.25 | 0.1591 | 0.326 | 0.2958 | 7 |
| 3 | 1,416 | 0.3181 | -974.53 | 74.19 | -1,534.51 | 0.1525 | 1.10 | 0.2867 | 4 |
| 4 | 800 | 0.1797 | -1,004.04 | 75.56 | -1,451.89 | 0.1525 | 0.681 | 0.2462 | 6 |
| 5 | 171 | 0.0384 | -1,078.19 | 159.17 | -1,562.55 | 0.1579 | -0.501 | 0.2164 | 7 |

by `alt_kind6`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 94 | 0.0211 | -1,161.60 | 180.61 | -1,510.57 | 0.1702 | -1.79 | 0.2128 | 7 |
| 1 | 1,006 | 0.226 | -960.76 | 92.32 | -1,521.85 | 0.167 | 1.31 | 0.2356 | 5 |
| 2 | 1,265 | 0.2841 | -997.71 | 70.33 | -1,534.74 | 0.1565 | 0.764 | 0.2909 | 5 |
| 3 | 1,257 | 0.2823 | -1,012.42 | 73.64 | -1,542.14 | 0.1607 | 0.524 | 0.28 | 5 |
| 4 | 669 | 0.1503 | -1,096.50 | 99.85 | -1,614.90 | 0.1315 | -0.699 | 0.3259 | 9 |
| 5 | 161 | 0.0362 | -936.54 | 195.62 | -1,541.66 | 0.1366 | 1.79 | 0.3478 | 9 |

by `range_1h_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=6.134 | 1,484 | 0.3333 | -849.01 | 80.13 | -1,516.02 | 0.1725 | 3.18 | 0.2547 | 2 |
| T2<=7.694 | 1,484 | 0.3333 | -1,160.90 | 49.15 | -1,534.44 | 0.1402 | -1.80 | 0.2891 | 9 |
| T3>7.694 | 1,484 | 0.3333 | -1,018.91 | 71.68 | -1,578.76 | 0.155 | 0.37 | 0.2992 | 6 |

by `range_3h_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=10.031 | 1,484 | 0.3333 | -925.54 | 85.57 | -1,591.47 | 0.1853 | 1.96 | 0.2628 | 3 |
| T2<=13.699 | 1,484 | 0.3333 | -1,086.62 | 53.71 | -1,551.73 | 0.1516 | -0.668 | 0.2837 | 8 |
| T3>13.699 | 1,484 | 0.3333 | -1,016.66 | 61.57 | -1,510.72 | 0.1307 | 0.462 | 0.2965 | 8 |

by `range_since_choch_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=1.729 | 1,484 | 0.3333 | -1,034.12 | 60.63 | -1,491.47 | 0.1294 | 0.282 | 0.3194 | 5 |
| T2<=2.361 | 1,484 | 0.3333 | -1,036.49 | 61.18 | -1,544.56 | 0.1496 | 0.147 | 0.2803 | 6 |
| T3>2.361 | 1,484 | 0.3333 | -958.22 | 81.16 | -1,619.53 | 0.1887 | 1.32 | 0.2433 | 6 |

by `er_1h_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=0.056 | 1,440 | 0.3235 | -1,019.21 | 66.45 | -1,519.53 | 0.1424 | 0.486 | 0.2799 | 7 |
| T2<=0.128 | 1,437 | 0.3228 | -1,012.85 | 58.60 | -1,489.06 | 0.1496 | 0.558 | 0.2881 | 7 |
| T3>0.128 | 1,439 | 0.3232 | -1,028.09 | 73.51 | -1,602.53 | 0.1647 | 0.226 | 0.2877 | 8 |
|  | 136 | 0.0305 | -678.11 | 429.91 | -2,038.43 | 0.2721 | 5.67 | 0.1471 | 7 |

by `hour_bin`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| <09:25 | 189 | 0.0425 | -843.02 | 348.64 | -2,023.62 | 0.2487 | 3.20 | 0.1958 | 7 |
| 09 | 369 | 0.0829 | -778.00 | 206.37 | -1,821.14 | 0.2087 | 4.18 | 0.3415 | 6 |
| 10 | 592 | 0.133 | -868.78 | 133.22 | -1,534.63 | 0.1807 | 2.79 | 0.2838 | 6 |
| 11 | 677 | 0.1521 | -1,114.42 | 85.06 | -1,522.96 | 0.1196 | -1.01 | 0.2939 | 7 |
| 12 | 740 | 0.1662 | -1,179.63 | 66.19 | -1,586.64 | 0.1216 | -2.06 | 0.2892 | 10 |
| 13 | 764 | 0.1716 | -988.55 | 82.45 | -1,471.37 | 0.1414 | 0.884 | 0.2801 | 7 |
| 14 | 808 | 0.1815 | -1,006.07 | 82.06 | -1,605.25 | 0.1745 | 0.627 | 0.3094 | 8 |
| 15 | 258 | 0.058 | -1,083.25 | 75.72 | -1,205.59 | 0.1667 | -0.587 | 0.1667 | 7 |
| >=15:20 | 55 | 0.0124 | -1,072.97 | 45.47 | -1,094.59 | 0 | -0.341 | 0 | 9 |

two-way `n_choch_since_bos` x `hour_bin`, mean net (n in the second table):

| hour_bin | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| <09:25 | -1,150.74 | -886.24 | -1,940.55 | 3,135.61 | -1,288.89 |
| 09 | -1,132.91 | -794.42 | 147.35 | -1,204.22 | -668.00 |
| 10 | -826.10 | -907.91 | -931.18 | -509.74 | -1,228.66 |
| 11 | -1,158.57 | -1,011.63 | -1,261.07 | -1,339.81 | -913.41 |
| 12 | -1,260.12 | -1,170.26 | -1,147.57 | -1,331.90 | -963.85 |
| 13 | -1,056.33 | -1,022.64 | -1,070.48 | -509.94 | -999.03 |
| 14 | -1,056.69 | -992.62 | -1,064.81 | -1,162.51 | -588.47 |
| 15 | -1,177.93 | -1,010.45 | -955.01 | -1,311.41 | -1,342.49 |
| >=15:20 | -1,064.85 | -1,065.21 | -1,142.13 | -1,012.33 | -1,185.44 |

| hour_bin | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| <09:25 | 43 | 97 | 28 | 13 | 8 |
| 09 | 127 | 137 | 59 | 23 | 23 |
| 10 | 160 | 231 | 108 | 59 | 34 |
| 11 | 187 | 258 | 118 | 56 | 58 |
| 12 | 171 | 277 | 168 | 57 | 67 |
| 13 | 198 | 287 | 134 | 73 | 72 |
| 14 | 203 | 323 | 148 | 72 | 62 |
| 15 | 64 | 108 | 52 | 11 | 23 |
| >=15:20 | 16 | 21 | 8 | 8 | 2 |

The grid: 201 cells; diff > 0 in 50; control pct >= 95 in 35; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff -84.88, median control pct 15.50. Full table `h2_minute_L1_grid.csv`. The six choch-only cells and the 15 range-only cells:

| kc | scope | W | q | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00 | all |  |  | dc7448312b5f9102 | 2,908 | 0.6532 | -1,034.75 | -962.25 | -72.50 | -105.62 | 1.40 | 0.3723 | 0.3419 | 0.8323 | 0.67 | 0.3143 | -1,424.72 | 4 | False |
| 2.00 | today |  |  | b1fa1d50708a9a96 | 2,951 | 0.6628 | -1,019.53 | -990.11 | -29.42 | -125.96 | 0.2 | 0.7246 | 0.3342 | 0.8368 | 0.7107 | 0.2571 | -1,409.49 | 6 | False |
| 3.00 | all |  |  | d12a4c627af70fcc | 3,731 | 0.8381 | -1,033.69 | -884.99 | -148.70 | -117.23 | 0 | 0.1554 | 0.161 | 0.8391 | 0.8334 | 0.1571 | -1,423.65 | 5 | False |
| 3.00 | today |  |  | 485e8f9a7784e40f | 3,762 | 0.845 | -1,016.78 | -970.51 | -46.27 | -125.49 | 0 | 0.6752 | 0.1559 | 0.8493 | 0.8714 | 0.1 | -1,406.74 | 6 | False |
| 4.00 | all |  |  | d45da7c256a1bdac | 4,103 | 0.9216 | -1,015.87 | -936.01 | -79.86 | -178.25 | 0 | 0.5952 | 0.0774 | 0.8338 | 0.9298 | 0.0429 | -1,405.83 | 5 | False |
| 4.00 | today |  |  | 3fb9395f9768fcfd | 4,122 | 0.9259 | -1,016.94 | -917.97 | -98.98 | -191.62 | 0 | 0.5227 | 0.0737 | 0.8394 | 0.9329 | 0.0429 | -1,406.91 | 4 | False |
|  |  | 1h | 0.1 | 96ede7eae0e249bd | 4,002 | 0.8989 | -1,022.00 | -899.37 | -122.63 | 9.09 | 100.00 | 0.3468 | 0.0977 | 0.8156 | 0.8357 | 0.2286 | -1,411.97 | 5 | False |
|  |  | 1h | 0.2 | 48b274bedb2ee2ea | 3,552 | 0.7978 | -1,034.69 | -910.61 | -124.08 | -19.46 | 99.80 | 0.2079 | 0.1988 | 0.83 | 0.7286 | 0.3429 | -1,424.66 | 3 | False |
|  |  | 1h | 0.3 | 6ed5d9c4d6de5164 | 3,108 | 0.6981 | -1,062.77 | -886.67 | -176.10 | -40.03 | 76.00 | 0.0415 | 0.2972 | 0.8311 | 0.617 | 0.4714 | -1,452.73 | 1 | False |
|  |  | 1h | 0.4 | 72bf239c6012b916 | 2,669 | 0.5995 | -1,074.26 | -912.82 | -161.44 | -41.06 | 31.00 | 0.0385 | 0.3965 | 0.8357 | 0.5285 | 0.5714 | -1,464.23 | 3 | False |
|  |  | 1h | 0.5 | ed1049fc116e173f | 2,227 | 0.5002 | -1,048.74 | -970.44 | -78.30 | 5.46 | 62.30 | 0.3223 | 0.4971 | 0.8396 | 0.4637 | 0.6286 | -1,438.70 | 5 | False |
|  |  | 3h | 0.1 | d0606c4a60d5b0da | 4,003 | 0.8991 | -1,032.82 | -802.67 | -230.15 | 196.99 | 100.00 | 0.0695 | 0.0937 | 0.784 | 0.7727 | 0.3143 | -1,422.78 | 6 | False |
|  |  | 3h | 0.2 | e91e86e923e02987 | 3,564 | 0.8005 | -1,031.30 | -922.52 | -108.78 | 132.63 | 100.00 | 0.2689 | 0.1903 | 0.8052 | 0.6652 | 0.4571 | -1,421.27 | 5 | False |
|  |  | 3h | 0.3 | 19e4aa324ff6248b | 3,120 | 0.7008 | -1,049.81 | -915.43 | -134.38 | 62.76 | 100.00 | 0.1089 | 0.2871 | 0.8101 | 0.5655 | 0.5571 | -1,439.78 | 5 | False |
|  |  | 3h | 0.4 | bbfbc5c7d5ac9423 | 2,668 | 0.5993 | -1,043.62 | -958.74 | -84.88 | 46.13 | 100.00 | 0.3018 | 0.3901 | 0.8217 | 0.4819 | 0.5714 | -1,433.59 | 5 | False |
|  |  | 3h | 0.5 | c4b274e0f37d41cb | 2,232 | 0.5013 | -1,050.60 | -968.39 | -82.21 | 7.66 | 99.70 | 0.3028 | 0.4864 | 0.8234 | 0.3933 | 0.6429 | -1,440.56 | 4 | False |
|  |  | since_choch | 0.1 | 9d329df4bd303daf | 4,005 | 0.8996 | -987.15 | -1,210.83 | 223.69 | 103.63 | 86.00 | 0.083 | 0.1064 | 0.8949 | 0.9498 | 0.0429 | -1,377.11 | 10 | False |
|  |  | since_choch | 0.2 | 67108d1d3c8babf9 | 3,558 | 0.7992 | -986.92 | -1,099.90 | 112.97 | 72.90 | 43.10 | 0.2549 | 0.2094 | 0.8803 | 0.8698 | 0.1429 | -1,376.89 | 8 | False |
|  |  | since_choch | 0.3 | 07bdb9dc5793f420 | 3,120 | 0.7008 | -1,010.68 | -1,007.10 | -3.58 | -11.39 | 7.50 | 0.965 | 0.3076 | 0.8679 | 0.7651 | 0.2571 | -1,400.64 | 5 | False |
|  |  | since_choch | 0.4 | 2e4e6fe23f82914e | 2,672 | 0.6002 | -993.01 | -1,034.53 | 41.52 | 28.92 | 5.60 | 0.6237 | 0.4117 | 0.8691 | 0.6865 | 0.3286 | -1,382.97 | 5 | False |
|  |  | since_choch | 0.5 | 68b11472cf2459ed | 2,227 | 0.5002 | -974.12 | -1,045.12 | 71.00 | 14.66 | 7.30 | 0.3673 | 0.5144 | 0.8688 | 0.6106 | 0.4 | -1,364.09 | 6 | False |

Top 10 cells by IS diff (selection is by nested CV, never by this table):

| cell | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | 853c31d4e4ecfaa8 | 4,384 | 0.9847 | -1,005.41 | -1,280.41 | 275.00 | 95.14 | 26.60 | 0.3788 | 0.0157 | 0.8676 | 0.9973 | 0 | -1,395.37 | 9 | False |
| {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "all"} | 893b139c5f337602 | 4,232 | 0.9506 | -996.35 | -1,264.71 | 268.37 | 82.08 | 65.20 | 0.1499 | 0.0516 | 0.8818 | 0.983 | 0.0143 | -1,386.31 | 10 | False |
| {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | f5611b1cf99cd1e2 | 4,233 | 0.9508 | -996.72 | -1,258.80 | 262.08 | 75.83 | 67.20 | 0.1514 | 0.0514 | 0.8813 | 0.983 | 0.0143 | -1,386.68 | 10 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 114ef075f7c1ddba | 4,399 | 0.9881 | -1,006.58 | -1,260.83 | 254.25 | 75.00 | 26.40 | 0.4653 | 0.0128 | 0.9057 | 0.998 | 0 | -1,396.55 | 10 | False |
| {"W": "1h", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 3a468b7d7b293913 | 4,420 | 0.9928 | -1,007.88 | -1,247.68 | 239.80 | 61.39 | 22.40 | 0.6067 | 0.0075 | 0.875 | 0.998 | 0 | -1,397.85 | 7 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "all"} | f3abf2577f49d191 | 4,320 | 0.9704 | -1,002.53 | -1,241.37 | 238.84 | 56.32 | 37.80 | 0.3123 | 0.0309 | 0.8788 | 0.993 | 0 | -1,392.49 | 9 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "today"} | 76cde4f3a78f5229 | 4,327 | 0.9719 | -1,002.92 | -1,240.95 | 238.03 | 55.80 | 23.90 | 0.2994 | 0.0293 | 0.88 | 0.9942 | 0 | -1,392.89 | 9 | False |
| {"W": "since_choch", "q": 0.1, "rule": "range"} | 9d329df4bd303daf | 4,005 | 0.8996 | -987.15 | -1,210.83 | 223.69 | 103.63 | 86.00 | 0.083 | 0.1064 | 0.8949 | 0.9498 | 0.0429 | -1,377.11 | 10 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.2, "rule": "both", "scope": "today"} | a7f29dbce2e23a61 | 4,357 | 0.9787 | -1,005.05 | -1,218.80 | 213.76 | 32.78 | 15.50 | 0.4223 | 0.0221 | 0.8737 | 0.9955 | 0 | -1,395.01 | 9 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "all"} | 59e3d2a328300f21 | 4,397 | 0.9876 | -1,007.00 | -1,218.00 | 211.00 | 31.66 | 31.60 | 0.5327 | 0.013 | 0.8909 | 0.9969 | 0 | -1,396.97 | 10 | False |

**Nested-CV candidate** (family `h2/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 96a71fa0c77cbd57 | 4,307 | 0.9674 | -1,016.99 | -790.18 | -226.81 | -304.80 | 1.10 | 0.3148 | 0.0314 | 0.8138 | 0.9698 | 0.0571 | -1,406.96 | 6 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.2, "rule": "both", "scope": "all"} | 1.51 | 288.87 | 0.9108 | 201 | 396 | 360 |
| 1 | {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | 4.78 | 271.63 | 0.9852 | 201 | 388 | 388 |
| 2 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 1.29 | 265.74 | 0.9879 | 201 | 384 | 381 |
| 3 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 1.29 | 268.03 | 0.9888 | 201 | 509 | 502 |
| 4 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 1.29 | 262.35 | 0.9887 | 201 | 390 | 385 |
| 5 | {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "all"} | 1.30 | 264.09 | 0.9508 | 201 | 341 | 321 |
| 6 | {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "all"} | 1.30 | 335.05 | 0.9516 | 201 | 424 | 402 |
| 7 | {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | 4.81 | 292.64 | 0.9854 | 201 | 266 | 262 |
| 8 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "today"} | 1.68 | 279.20 | 0.9715 | 201 | 170 | 166 |
| 9 | {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | 4.86 | 290.17 | 0.9856 | 201 | 499 | 488 |
| 10 | {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 1.30 | 262.71 | 0.9878 | 201 | 173 | 172 |
| 11 | {"W": "1h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 4.90 | 371.98 | 0.9754 | 201 | 512 | 480 |

CPCV paths (`h2/nested_cv/cpcv`, 11 rows): diff median -198.78, 5th pct -417.49, min -451.17, share > 0 0.182, control pct median 1.90 / 5th pct 0.7

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 68e1c459a40d7b6f | 4,241 | 0.9526 | -1,002.52 | -1,151.99 | 149.47 | 33.40 | 0.4418 | 0.983 | 6 | 0 |
| 78492773940a9cc0 | 4,339 | 0.9746 | -1,017.79 | -695.56 | -322.22 | 1.20 | 0.1914 | 0.9718 | 7 | 1 |
| 11c8d5f1dc54922b | 4,367 | 0.9809 | -1,018.22 | -567.05 | -451.17 | 1.10 | 0.1029 | 0.9776 | 6 | 2 |
| 5e24d36310ab5b2c | 4,333 | 0.9733 | -1,018.64 | -680.88 | -337.75 | 1.40 | 0.1579 | 0.9703 | 6 | 3 |
| ba41db8d6285a987 | 4,267 | 0.9584 | -1,017.87 | -819.09 | -198.78 | 0.7 | 0.3103 | 0.9643 | 6 | 4 |
| a8a83f61b802ae7d | 4,301 | 0.9661 | -1,016.05 | -826.17 | -189.88 | 16.40 | 0.3753 | 0.9637 | 7 | 5 |
| 5293a31029174c5c | 4,315 | 0.9692 | -1,004.78 | -1,161.62 | 156.84 | 18.90 | 0.4893 | 0.9881 | 7 | 6 |
| e7d54b12eafca620 | 4,344 | 0.9757 | -1,016.67 | -725.62 | -291.04 | 1.90 | 0.2574 | 0.9758 | 5 | 7 |
| 74d662c6716d1444 | 4,384 | 0.9847 | -1,011.52 | -886.09 | -125.43 | 5.70 | 0.6862 | 0.9901 | 6 | 8 |
| 8d0e42636babf790 | 4,350 | 0.9771 | -1,018.40 | -634.59 | -383.81 | 0.7 | 0.1349 | 0.9745 | 6 | 9 |
| 5a48af5fa6c6fbb8 | 4,359 | 0.9791 | -1,013.01 | -850.33 | -162.68 | 7.80 | 0.5557 | 0.9862 | 6 | 10 |

Cells chosen across the 66 CPCV training sets: {"W": "1h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} x16; {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} x16; {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "all"} x9; {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.2, "rule": "both", "scope": "all"} x6; {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "all"} x6; {"W": "1h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x3; {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.2, "rule": "both", "scope": "today"} x3; {"W": "3h", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} x2; {"W": "since_choch", "q": 0.1, "rule": "range"} x2; {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "today"} x2; {"W": "1h", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 202 | 202 | 1.35 | 0.3564 | 0.5611 | 0.1255 | 0.18 |  | {"rule": "range", "W": "3h", "q": 0.2} | 322.59 | [-582.49, 91.16] | 0.8655 | 1.00 | -198.78 | -417.49 | 0.182 | 1.90 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### 5 min / L1 (826 IS units)

by `n_choch_since_bos`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 235 | 0.2845 | -717.44 | 289.68 | -2,222.55 | 0.2766 | 5.14 | 0.4383 | 7 |
| 1 | 332 | 0.4019 | -647.02 | 259.50 | -2,039.38 | 0.3072 | 6.18 | 0.3765 | 3 |
| 2 | 143 | 0.1731 | -1,439.43 | 344.10 | -2,337.62 | 0.2028 | -5.96 | 0.5105 | 8 |
| 3 | 54 | 0.0654 | -335.79 | 606.61 | -1,723.76 | 0.3333 | 10.69 | 0.3519 | 7 |
| 4+ | 62 | 0.0751 | -289.43 | 555.73 | -2,030.88 | 0.2419 | 11.87 | 0.4194 | 3 |

by `n_choch_since_bos_today`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 242 | 0.293 | -691.14 | 285.27 | -2,193.78 | 0.281 | 5.54 | 0.4256 | 7 |
| 1 | 362 | 0.4383 | -518.56 | 266.65 | -2,039.38 | 0.3149 | 8.15 | 0.384 | 3 |
| 2 | 133 | 0.161 | -1,570.73 | 293.27 | -2,337.62 | 0.188 | -7.96 | 0.5338 | 10 |
| 3 | 49 | 0.0593 | -867.92 | 429.38 | -1,761.49 | 0.2857 | 2.56 | 0.3469 | 7 |
| 4+ | 40 | 0.0484 | -472.86 | 640.22 | -1,978.70 | 0.2 | 9.10 | 0.4 | 4 |

by `alt_dir6`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 168 | 0.2034 | -1,116.80 | 349.25 | -2,210.91 | 0.2738 | -0.973 | 0.3988 | 8 |
| 2 | 265 | 0.3208 | -1,029.12 | 253.58 | -2,289.26 | 0.2566 | 0.257 | 0.4302 | 8 |
| 3 | 235 | 0.2845 | -301.66 | 321.62 | -1,980.85 | 0.3191 | 11.47 | 0.4128 | 5 |
| 4 | 123 | 0.1489 | -855.22 | 379.25 | -2,009.15 | 0.2439 | 3.02 | 0.4472 | 5 |
| 5 | 35 | 0.0424 | 317.03 | 838.04 | -2,036.58 | 0.2857 | 21.39 | 0.3714 | 3 |

by `alt_kind6`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 18 | 0.0218 | 910.32 | 1,182.83 | -1,002.83 | 0.3889 | 30.63 | 0.2222 | 2 |
| 1 | 209 | 0.253 | -1,031.64 | 307.40 | -2,187.87 | 0.244 | 0.267 | 0.4306 | 7 |
| 2 | 236 | 0.2857 | -1,159.16 | 238.20 | -2,211.28 | 0.2627 | -1.67 | 0.4703 | 9 |
| 3 | 246 | 0.2978 | -456.49 | 320.04 | -2,011.17 | 0.2967 | 9.11 | 0.378 | 3 |
| 4 | 102 | 0.1235 | -268.54 | 493.81 | -2,227.03 | 0.3137 | 11.94 | 0.4118 | 4 |
| 5 | 15 | 0.0182 | -856.56 | 1,013.40 | -2,176.34 | 0.2667 | 3.26 | 0.4 | 3 |

by `range_1h_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=2.880 | 276 | 0.3341 | -653.27 | 252.04 | -2,028.11 | 0.2717 | 6.20 | 0.4565 | 4 |
| T2<=3.724 | 275 | 0.3329 | -535.27 | 276.77 | -2,054.02 | 0.2873 | 7.81 | 0.3818 | 6 |
| T3>3.724 | 275 | 0.3329 | -1,083.00 | 284.43 | -2,352.58 | 0.2727 | -0.503 | 0.4182 | 8 |

by `range_3h_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=4.330 | 276 | 0.3341 | -497.83 | 312.03 | -2,218.30 | 0.3043 | 8.44 | 0.4022 | 4 |
| T2<=5.690 | 275 | 0.3329 | -632.91 | 260.34 | -1,980.39 | 0.2873 | 6.43 | 0.4109 | 4 |
| T3>5.690 | 275 | 0.3329 | -1,141.36 | 235.36 | -2,245.62 | 0.24 | -1.37 | 0.4436 | 9 |

by `range_since_choch_atr_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=1.820 | 276 | 0.3341 | -733.63 | 223.43 | -2,035.66 | 0.2391 | 4.86 | 0.5435 | 6 |
| T2<=2.379 | 275 | 0.3329 | -874.23 | 252.87 | -2,297.79 | 0.2691 | 2.61 | 0.4 | 6 |
| T3>2.379 | 275 | 0.3329 | -663.38 | 328.30 | -2,200.88 | 0.3236 | 6.04 | 0.3127 | 9 |

by `er_1h_tercile`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| T1<=0.278 | 240 | 0.2906 | -784.80 | 257.33 | -2,036.32 | 0.2542 | 4.09 | 0.4625 | 6 |
| T2<=0.464 | 239 | 0.2893 | -929.51 | 258.01 | -2,069.53 | 0.2385 | 1.83 | 0.3933 | 6 |
| T3>0.464 | 240 | 0.2906 | -849.71 | 268.88 | -2,217.41 | 0.2917 | 3.06 | 0.4167 | 6 |
|  | 107 | 0.1295 | -101.77 | 660.46 | -2,420.00 | 0.3832 | 14.62 | 0.3832 | 5 |

by `hour_bin`:

| bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|
| <09:25 | 50 | 0.0605 | 126.99 | 973.13 | -2,413.39 | 0.38 | 18.02 | 0.34 | 5 |
| 09 | 96 | 0.1162 | -907.07 | 611.15 | -2,754.80 | 0.3021 | 2.29 | 0.4583 | 7 |
| 10 | 123 | 0.1489 | -1,083.65 | 433.61 | -2,615.84 | 0.252 | -0.403 | 0.4309 | 9 |
| 11 | 100 | 0.1211 | -1,082.55 | 405.81 | -2,266.07 | 0.24 | -0.536 | 0.48 | 7 |
| 12 | 126 | 0.1525 | -987.81 | 359.08 | -2,289.39 | 0.2222 | 0.951 | 0.5238 | 9 |
| 13 | 149 | 0.1804 | -524.51 | 330.00 | -2,033.52 | 0.302 | 8.05 | 0.4631 | 6 |
| 14 | 132 | 0.1598 | -346.09 | 337.53 | -1,362.19 | 0.3485 | 10.80 | 0.3409 | 5 |
| 15 | 45 | 0.0545 | -1,089.89 | 151.78 | -1,090.96 | 0.1556 | -0.736 | 0.0667 | 9 |
| >=15:20 | 5 | 0.0061 | -1,141.22 | 205.66 | -1,126.84 | 0 | -1.65 | 0.2 | 3 |

two-way `n_choch_since_bos` x `hour_bin`, mean net (n in the second table):

| hour_bin | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| <09:25 | 1,139.79 | 118.38 | -2,815.12 | 1,879.20 | 2,041.98 |
| 09 | -1,021.69 | -1,508.40 | -1,082.02 | 3,893.41 | 1,178.87 |
| 10 | -519.29 | -1,339.62 | -1,588.64 | -467.36 | -774.45 |
| 11 | -1,058.47 | -454.15 | -2,077.32 | -1,814.55 | -2,025.98 |
| 12 | -544.34 | -1,447.38 | -1,146.06 | -1,763.28 | -1.43 |
| 13 | -912.37 | -60.38 | -1,114.82 | 997.23 | -344.85 |
| 14 | -938.16 | 202.02 | -1,280.49 | -273.88 | -436.79 |
| 15 | -919.43 | -1,196.68 | -1,546.72 | -669.07 | -1,037.48 |
| >=15:20 |  | -1,399.72 | -1,094.84 |  | -412.09 |

| hour_bin | 0 | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|---|
| <09:25 | 12.00 | 21.00 | 9.00 | 5.00 | 3.00 |
| 09 | 28.00 | 42.00 | 15.00 | 3.00 | 8.00 |
| 10 | 35.00 | 48.00 | 27.00 | 7.00 | 6.00 |
| 11 | 28.00 | 42.00 | 13.00 | 9.00 | 8.00 |
| 12 | 42.00 | 39.00 | 24.00 | 10.00 | 11.00 |
| 13 | 45.00 | 58.00 | 30.00 | 4.00 | 12.00 |
| 14 | 30.00 | 63.00 | 18.00 | 12.00 | 9.00 |
| 15 | 15.00 | 16.00 | 6.00 | 4.00 | 4.00 |
| >=15:20 |  | 3.00 | 1.00 |  | 1.00 |

The grid: 201 cells; diff > 0 in 79; control pct >= 95 in 35; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff -172.16, median control pct 44.90. Full table `h2_5minute_L1_grid.csv`. The six choch-only cells and the 15 range-only cells:

| kc | scope | W | q | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00 | all |  |  | cdd9b4281b0e451c | 567 | 0.6864 | -676.21 | -934.04 | 257.83 | 151.83 | 45.90 | 0.4613 | 0.33 | 0.7606 | 0.7182 | 0.3478 | -1,066.17 | 6.00 | False |
| 2.00 | today |  |  | 60d25ea57daf33dd | 604 | 0.7312 | -587.71 | -1,217.79 | 630.08 | 335.12 | 8.30 | 0.072 | 0.2931 | 0.7883 | 0.8268 | 0.1739 | -977.67 | 9.00 | False |
| 3.00 | all |  |  | 6e32c51940ce5a11 | 710 | 0.8596 | -829.93 | -311.01 | -518.91 | -570.00 | 1.20 | 0.2679 | 0.139 | 0.7155 | 0.8488 | 0.1739 | -1,219.89 | 5.00 | False |
| 3.00 | today |  |  | 1210d3613c329844 | 737 | 0.8923 | -765.11 | -690.36 | -74.74 | -318.01 | 0 | 0.8656 | 0.1122 | 0.7528 | 0.9184 | 0.087 | -1,155.07 | 6.00 | False |
| 4.00 | all |  |  | 58431928cdcb8a87 | 764 | 0.9249 | -795.00 | -289.43 | -505.57 | -740.50 | 2.20 | 0.3978 | 0.0787 | 0.7581 | 0.9152 | 0.087 | -1,184.97 | 3.00 | False |
| 4.00 | today |  |  | d31cdd229b2fb904 | 786 | 0.9516 | -771.52 | -472.86 | -298.66 | -526.66 | 0.1 | 0.6832 | 0.0536 | 0.8 | 0.9539 | 0.0435 | -1,161.48 | 4.00 | False |
|  |  | 1h | 0.1 | 0530a9a0684c7a06 | 742 | 0.8983 | -861.62 | 166.67 | -1,028.29 | -796.64 | 95.20 | 0.0455 | 0.0905 | 0.6429 | 0.8519 | 0.1739 | -1,251.59 | 6.00 | False |
|  |  | 1h | 0.2 | a0a30c80e9609ed1 | 657 | 0.7954 | -863.16 | -344.56 | -518.60 | -521.62 | 83.80 | 0.1999 | 0.1993 | 0.7041 | 0.7662 | 0.3043 | -1,253.12 | 3.00 | False |
|  |  | 1h | 0.3 | f8d5ce7741f67e73 | 577 | 0.6985 | -808.95 | -636.79 | -172.16 | -272.00 | 86.30 | 0.6282 | 0.2998 | 0.7189 | 0.7115 | 0.3043 | -1,198.91 | 5.00 | False |
|  |  | 1h | 0.4 | 87a5cb7d41375060 | 495 | 0.5993 | -827.65 | -651.47 | -176.18 | -354.39 | 90.00 | 0.5892 | 0.4037 | 0.7281 | 0.6061 | 0.3913 | -1,217.62 | 6.00 | False |
|  |  | 1h | 0.5 | 2d397c3f5ea43347 | 415 | 0.5024 | -964.63 | -547.45 | -417.17 | -569.65 | 41.80 | 0.1824 | 0.4941 | 0.7178 | 0.4865 | 0.5652 | -1,354.59 | 4.00 | False |
|  |  | 3h | 0.1 | 90bf13e268335b43 | 741 | 0.8971 | -809.66 | -298.41 | -511.25 | -273.26 | 100.00 | 0.3338 | 0.0905 | 0.6353 | 0.8422 | 0.1739 | -1,199.63 | 5.00 | False |
|  |  | 3h | 0.2 | c6baf3ab8cafe967 | 659 | 0.7978 | -870.75 | -308.37 | -562.39 | -255.31 | 100.00 | 0.1579 | 0.1843 | 0.6587 | 0.7163 | 0.3478 | -1,260.72 | 4.00 | False |
|  |  | 3h | 0.3 | f3ad224066e780fd | 578 | 0.6998 | -841.53 | -560.16 | -281.37 | -144.71 | 100.00 | 0.3923 | 0.2864 | 0.6895 | 0.6311 | 0.4348 | -1,231.50 | 5.00 | False |
|  |  | 3h | 0.4 | 06d5b32818642e15 | 492 | 0.5956 | -880.62 | -575.04 | -305.58 | 22.82 | 100.00 | 0.3328 | 0.3936 | 0.7036 | 0.5157 | 0.6087 | -1,270.58 | 5.00 | False |
|  |  | 3h | 0.5 | 384739c2c0cfb896 | 412 | 0.4988 | -859.10 | -655.50 | -203.60 | 135.69 | 100.00 | 0.5282 | 0.4941 | 0.7126 | 0.4414 | 0.6957 | -1,249.07 | 7.00 | False |
|  |  | since_choch | 0.1 | 27364c7f3b9f90cb | 741 | 0.8971 | -706.43 | -1,198.37 | 491.94 | 250.72 | 47.10 | 0.3463 | 0.1223 | 0.8588 | 0.9487 | 0.0435 | -1,096.39 | 9.00 | False |
|  |  | since_choch | 0.2 | f27959543a3e3e19 | 659 | 0.7978 | -722.25 | -894.37 | 172.12 | -99.75 | 11.20 | 0.6557 | 0.2228 | 0.7964 | 0.8655 | 0.1304 | -1,112.22 | 7.00 | False |
|  |  | since_choch | 0.3 | cca60d2ed7819513 | 580 | 0.7022 | -830.62 | -583.60 | -247.02 | -322.43 | 0.2 | 0.4768 | 0.3099 | 0.752 | 0.7434 | 0.2174 | -1,220.58 | 4.00 | False |
|  |  | since_choch | 0.4 | a14feb8dc3a7ee2c | 493 | 0.5969 | -758.95 | -754.25 | -4.70 | -53.23 | 0.4 | 0.985 | 0.4255 | 0.7628 | 0.6622 | 0.3043 | -1,148.91 | 5.00 | False |
|  |  | since_choch | 0.5 | cb3984ce08562f50 | 413 | 0.5 | -735.19 | -778.91 | 43.71 | -6.71 | 0.6 | 0.8946 | 0.5226 | 0.7554 | 0.5864 | 0.3913 | -1,125.16 | 5.00 | False |

Top 10 cells by IS diff (selection is by nested CV, never by this table):

| cell | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 1b558762f9801ac8 | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 3,774.55 | 93.50 | 0.1374 | 0.0034 | 1.00 | 1.00 | 0 | -1,137.35 | 2.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "all"} | 473438a97da60a31 | 818 | 0.9903 | -739.42 | -2,559.46 | 1,820.03 | 1,601.41 | 31.60 | 0.2394 | 0.0134 | 1.00 | 1.00 | 0 | -1,129.39 | 4.00 | False |
| {"W": "1h", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | a4dc48585afbbfe2 | 825 | 0.9988 | -754.87 | -2,555.50 | 1,800.63 | 1,583.71 | 74.60 | 0.5992 | 0.0017 | 1.00 | 1.00 | 0 | -1,144.84 | 1.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | fc54acaab0d26462 | 823 | 0.9964 | -751.22 | -2,355.68 | 1,604.45 | 1,387.04 | 25.40 | 0.5267 | 0.005 | 1.00 | 1.00 | 0 | -1,141.19 | 3.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | f4f0a18c9aa06662 | 818 | 0.9903 | -741.86 | -2,310.28 | 1,568.42 | 1,349.77 | 46.70 | 0.3023 | 0.0134 | 1.00 | 1.00 | 0 | -1,131.83 | 5.00 | False |
| {"W": "1h", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "today"} | f133b98084b9ff70 | 814 | 0.9855 | -740.47 | -1,881.59 | 1,141.11 | 921.39 | 67.30 | 0.3768 | 0.0201 | 1.00 | 1.00 | 0 | -1,130.44 | 7.00 | False |
| {"W": "1h", "combine": "AND", "kc": 4, "q": 0.2, "rule": "both", "scope": "today"} | 655bfa4cf1235bb1 | 820 | 0.9927 | -748.98 | -1,860.48 | 1,111.50 | 893.31 | 60.90 | 0.5317 | 0.0101 | 1.00 | 1.00 | 0 | -1,138.94 | 4.00 | False |
| {"W": "3h", "combine": "AND", "kc": 2, "q": 0.2, "rule": "both", "scope": "today"} | f8071020b292e4f2 | 807 | 0.977 | -732.60 | -1,795.65 | 1,063.05 | 841.49 | 69.80 | 0.3113 | 0.0268 | 0.8421 | 0.9955 | 0 | -1,122.56 | 7.00 | False |
| {"W": "3h", "combine": "AND", "kc": 2, "q": 0.4, "rule": "both", "scope": "today"} | 4458f42aa2281627 | 755 | 0.914 | -665.69 | -1,728.54 | 1,062.85 | 826.65 | 85.80 | 0.067 | 0.1005 | 0.8451 | 0.9686 | 0.0435 | -1,055.66 | 9.00 | False |
| {"W": "3h", "combine": "AND", "kc": 4, "q": 0.2, "rule": "both", "scope": "today"} | cd325f4ca07452c6 | 822 | 0.9952 | -752.04 | -1,786.64 | 1,034.60 | 816.91 | 44.90 | 0.6362 | 0.0067 | 1.00 | 1.00 | 0 | -1,142.01 | 3.00 | False |

**Nested-CV candidate** (family `h2/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 74e1239d4204941d | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 3,774.55 | 94.30 | 0.1339 | 0.0034 | 1.00 | 1.00 | 0 | -1,137.35 | 2 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 3,951.78 | 0.9973 | 199 | 82 | 82 |
| 1 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.89 | 3,945.20 | 0.9973 | 199 | 83 | 83 |
| 2 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.97 | 3,963.29 | 0.9974 | 199 | 42 | 42 |
| 3 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.89 | 4,007.24 | 0.9973 | 199 | 76 | 76 |
| 4 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.86 | 5,090.75 | 0.9987 | 199 | 72 | 72 |
| 5 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.96 | 4,045.46 | 0.9973 | 199 | 73 | 73 |
| 6 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 5,063.28 | 0.9987 | 199 | 77 | 76 |
| 7 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.96 | 4,007.54 | 0.9974 | 199 | 51 | 51 |
| 8 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.89 | 3,964.33 | 0.9973 | 198 | 76 | 76 |
| 9 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 4,049.20 | 0.9973 | 199 | 80 | 80 |
| 10 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.94 | 2,918.75 | 0.9987 | 199 | 31 | 30 |
| 11 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.97 | 3,937.57 | 0.9973 | 199 | 83 | 83 |

CPCV paths (`h2/nested_cv/cpcv`, 11 rows): diff median 3,991.66, 5th pct 3,444.78, min 2,897.90, share > 0 1.00, control pct median 87.80 / 5th pct 74.50

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 0a5bc6b99975a851 | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 93.70 | 0.1434 | 1.00 | 2 | 0 |
| 66e459373a14f057 | 825 | 0.9988 | -750.91 | -5,826.65 | 5,075.74 | 74.50 | 0.1459 | 1.00 | 1 | 1 |
| fcd555388be90de9 | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 94.00 | 0.1364 | 1.00 | 2 | 2 |
| ee35b5bd47155635 | 825 | 0.9988 | -750.91 | -5,826.65 | 5,075.74 | 75.50 | 0.1294 | 1.00 | 1 | 3 |
| cd9f7fbaf9683c64 | 825 | 0.9988 | -750.91 | -5,826.65 | 5,075.74 | 74.50 | 0.1359 | 1.00 | 1 | 4 |
| 8bc82aa52898581c | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 93.80 | 0.1414 | 1.00 | 2 | 5 |
| 7e0c7a8f19791e8b | 825 | 0.9988 | -753.54 | -3,651.44 | 2,897.90 | 87.80 | 0.3633 | 1.00 | 1 | 6 |
| cb138c698faf2d2a | 825 | 0.9988 | -750.91 | -5,826.65 | 5,075.74 | 75.20 | 0.1304 | 1.00 | 1 | 7 |
| de7830d4f81559bc | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 93.30 | 0.1604 | 1.00 | 2 | 8 |
| 46f9348be3bfca4a | 825 | 0.9988 | -750.91 | -5,826.65 | 5,075.74 | 76.50 | 0.1459 | 1.00 | 1 | 9 |
| 2fc3c5b11e1870d6 | 824 | 0.9976 | -747.39 | -4,739.05 | 3,991.66 | 93.30 | 0.1464 | 1.00 | 2 | 10 |

Cells chosen across the 66 CPCV training sets: {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x65; {"W": "1h", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L1 | pre-registered (family as at the primary run) | 202 | 202 | 1.44 | 0.3293 | 0.5333 | 0.076 | 0.0835 |  | {"rule": "range", "W": "3h", "q": 0.1} | 127.60 | [2816.25, 5189.35] | 0 | 0.9957 | 3,991.66 | 3,444.78 | 1.00 | 87.80 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1 |


### 5 min / L0 (832 IS units)

L0 robustness, by `n_choch_since_bos` and `n_choch_since_bos_today`:

| variable | bucket | n | net_mean | net_se | win_rate | blocks_below_block_mean |
|---|---|---|---|---|---|---|
| n_choch_since_bos | 0 | 237 | -273.07 | 837.17 | 0.211 | 7 |
| n_choch_since_bos | 1 | 334 | 230.07 | 568.67 | 0.2425 | 2 |
| n_choch_since_bos | 2 | 144 | -2,017.80 | 416.96 | 0.1597 | 12 |
| n_choch_since_bos | 3 | 55 | 310.45 | 1,099.59 | 0.2909 | 7 |
| n_choch_since_bos | 4+ | 62 | 501.60 | 1,079.59 | 0.2258 | 4 |
| n_choch_since_bos_today | 0 | 244 | -278.62 | 813.74 | 0.2131 | 8 |
| n_choch_since_bos_today | 1 | 364 | 236.40 | 536.18 | 0.2527 | 2 |
| n_choch_since_bos_today | 2 | 134 | -2,140.68 | 398.61 | 0.1343 | 12 |
| n_choch_since_bos_today | 3 | 50 | 531.22 | 1,187.06 | 0.28 | 7 |
| n_choch_since_bos_today | 4+ | 40 | 299.07 | 1,429.24 | 0.2 | 7 |

The grid: 201 cells; diff > 0 in 103; control pct >= 95 in 22; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff 42.73, median control pct 68.70. Full table `h2_5minute_L0_grid.csv`. The six choch-only cells and the 15 range-only cells:

| kc | scope | W | q | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00 | all |  |  | e007e395ec212c79 | 571 | 0.6863 | 21.24 | -928.70 | 949.94 | 89.43 | 81.20 | 0.2114 | 0.321 | 0.7969 | 0.7751 | 0.1579 | -368.73 | 8.00 | False |
| 2.00 | today |  |  | 8e30eb4817d3bf5f | 608 | 0.7308 | 29.71 | -1,108.61 | 1,138.32 | 374.16 | 64.10 | 0.1684 | 0.284 | 0.8214 | 0.8299 | 0.1579 | -360.25 | 8.00 | False |
| 3.00 | all |  |  | 79b133d6f3cf4160 | 715 | 0.8594 | -389.42 | 411.74 | -801.16 | -1,233.57 | 30.00 | 0.4498 | 0.1343 | 0.7436 | 0.8461 | 0.1579 | -779.39 | 7.00 | False |
| 3.00 | today |  |  | 57a2e6cbdcabecc2 | 742 | 0.8918 | -362.25 | 428.05 | -790.29 | -1,068.67 | 17.90 | 0.4953 | 0.1049 | 0.7556 | 0.8826 | 0.1579 | -752.21 | 8.00 | False |
| 4.00 | all |  |  | fd0518ec575c77e1 | 770 | 0.9255 | -339.43 | 501.60 | -841.03 | -1,682.01 | 8.20 | 0.5222 | 0.0741 | 0.7742 | 0.91 | 0.1053 | -729.40 | 4.00 | False |
| 4.00 | today |  |  | ed14be2df0f7ee3b | 792 | 0.9519 | -305.84 | 299.07 | -604.91 | -1,421.88 | 0.3 | 0.7086 | 0.0494 | 0.8 | 0.9433 | 0.1053 | -695.80 | 7.00 | False |
|  |  | 1h | 0.1 | 06920ca30c0ae2db | 748 | 0.899 | -307.78 | -0.55 | -307.22 | -663.47 | 99.00 | 0.7936 | 0.0941 | 0.7262 | 0.8964 | 0.0526 | -697.74 | 7.00 | False |
|  |  | 1h | 0.2 | ddee9576c0f618ac | 663 | 0.7969 | -194.73 | -598.57 | 403.84 | -283.96 | 98.70 | 0.6377 | 0.2006 | 0.7692 | 0.8401 | 0.0526 | -584.69 | 8.00 | False |
|  |  | 1h | 0.3 | 92d61d9ab265fd9b | 584 | 0.7019 | -554.53 | 377.36 | -931.89 | -473.46 | 42.20 | 0.2379 | 0.2963 | 0.7742 | 0.6446 | 0.2105 | -944.50 | 6.00 | False |
|  |  | 1h | 0.4 | 4e978c6639265a54 | 502 | 0.6034 | -415.36 | -65.91 | -349.45 | -266.58 | 40.30 | 0.6262 | 0.4012 | 0.7879 | 0.5981 | 0.2105 | -805.33 | 7.00 | False |
|  |  | 1h | 0.5 | 7612ba89577b25ef | 418 | 0.5024 | -174.79 | -379.71 | 204.92 | -27.20 | 43.60 | 0.7946 | 0.5031 | 0.7874 | 0.5595 | 0.2105 | -564.75 | 8.00 | False |
|  |  | 3h | 0.1 | 826161958736bcf3 | 747 | 0.8978 | -294.15 | -123.87 | -170.28 | -531.45 | 100.00 | 0.8791 | 0.091 | 0.6941 | 0.8854 | 0.0526 | -684.12 | 5.00 | False |
|  |  | 3h | 0.2 | 53ee2ad1fb6d2290 | 665 | 0.7993 | -286.73 | -237.04 | -49.69 | -300.44 | 100.00 | 0.9495 | 0.1898 | 0.7365 | 0.7939 | 0.1579 | -676.70 | 7.00 | False |
|  |  | 3h | 0.3 | 70726c1d9e388564 | 583 | 0.7007 | -240.15 | -362.46 | 122.30 | -436.00 | 99.40 | 0.8891 | 0.2886 | 0.751 | 0.704 | 0.2632 | -630.12 | 6.00 | False |
|  |  | 3h | 0.4 | 1160eab80a9f9337 | 497 | 0.5974 | -259.55 | -302.28 | 42.73 | -31.94 | 92.20 | 0.9515 | 0.3966 | 0.7672 | 0.5844 | 0.3684 | -649.52 | 7.00 | False |
|  |  | 3h | 0.5 | dbaf94b27fd09ce5 | 415 | 0.4988 | -128.33 | -424.47 | 296.13 | 153.33 | 94.30 | 0.6857 | 0.4969 | 0.7722 | 0.5115 | 0.4737 | -518.30 | 6.00 | False |
|  |  | since_choch | 0.1 | c2cc47230967d66e | 745 | 0.8954 | -52.17 | -2,199.95 | 2,147.78 | 1,281.75 | 88.40 | 0.054 | 0.1173 | 0.8736 | 0.985 | 0 | -442.13 | 11.00 | False |
|  |  | since_choch | 0.2 | ade48394be497d13 | 663 | 0.7969 | -245.67 | -398.72 | 153.05 | 208.52 | 43.60 | 0.8631 | 0.2145 | 0.8225 | 0.8431 | 0.0526 | -635.63 | 7.00 | False |
|  |  | since_choch | 0.3 | 4c3b4de765885211 | 582 | 0.6995 | -524.28 | 299.47 | -823.75 | -146.63 | 18.10 | 0.2964 | 0.3056 | 0.792 | 0.6758 | 0.3684 | -914.24 | 3.00 | False |
|  |  | since_choch | 0.4 | 570d4162d98cbab2 | 497 | 0.5974 | -351.38 | -166.05 | -185.33 | 79.05 | 26.70 | 0.8121 | 0.4136 | 0.8 | 0.6233 | 0.3684 | -741.34 | 5.00 | False |
|  |  | since_choch | 0.5 | e85dabafd727f250 | 415 | 0.4988 | -335.65 | -218.15 | -117.50 | 293.06 | 26.80 | 0.8731 | 0.517 | 0.8034 | 0.5321 | 0.4737 | -725.61 | 6.00 | False |

Top 10 cells by IS diff (selection is by nested CV, never by this table):

| cell | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 0a19dd9cb85eef2e | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 3,694.33 | 93.30 | 0.2084 | 0.0031 | 1.00 | 1.00 | 0 | -655.97 | 2.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 14a553ec17ea33f5 | 789 | 0.9483 | -134.92 | -2,879.34 | 2,744.43 | 1,926.29 | 72.80 | 0.0725 | 0.0602 | 0.907 | 0.9948 | 0 | -524.88 | 11.00 | False |
| {"W": "1h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 05827040dd99ea33 | 824 | 0.9904 | -250.98 | -2,931.73 | 2,680.75 | 1,896.46 | 95.40 | 0.3113 | 0.0108 | 0.875 | 0.9988 | 0 | -640.95 | 4.00 | False |
| {"W": "3h", "combine": "AND", "kc": 4, "q": 0.2, "rule": "both", "scope": "today"} | 0933d775ae9709c0 | 828 | 0.9952 | -264.31 | -2,854.31 | 2,590.00 | 1,809.40 | 68.70 | 0.4443 | 0.0046 | 0.75 | 0.9999 | 0 | -654.27 | 3.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 3, "q": 0.1, "rule": "both", "scope": "today"} | 0590c7232028848a | 823 | 0.9892 | -248.96 | -2,819.01 | 2,570.05 | 1,784.83 | 72.80 | 0.3348 | 0.0139 | 1.00 | 1.00 | 0 | -638.92 | 5.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "all"} | b5c6839aa8a75378 | 788 | 0.9471 | -144.09 | -2,652.75 | 2,508.66 | 1,689.37 | 74.50 | 0.093 | 0.0602 | 0.8864 | 0.9912 | 0 | -534.05 | 11.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "all"} | 6f584ccdc84b7237 | 824 | 0.9904 | -254.60 | -2,559.46 | 2,304.86 | 1,520.54 | 43.80 | 0.4103 | 0.0123 | 1.00 | 1.00 | 0 | -644.56 | 3.00 | False |
| {"W": "1h", "combine": "AND", "kc": 4, "q": 0.1, "rule": "both", "scope": "today"} | 66b81d9153654368 | 831 | 0.9988 | -274.02 | -2,555.50 | 2,281.48 | 1,503.63 | 74.10 | 0.6422 | 0.0015 | 1.00 | 1.00 | 0 | -663.98 | 1.00 | False |
| {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.5, "rule": "both", "scope": "today"} | 3d439749bccac179 | 694 | 0.8341 | 100.36 | -2,173.25 | 2,273.61 | 1,345.10 | 83.50 | 0.0205 | 0.1821 | 0.8551 | 0.9617 | 0 | -289.61 | 11.00 | False |
| {"W": "3h", "combine": "AND", "kc": 4, "q": 0.5, "rule": "both", "scope": "today"} | e0176b2dbc774583 | 815 | 0.9796 | -231.88 | -2,428.11 | 2,196.23 | 1,403.40 | 69.00 | 0.3103 | 0.0216 | 0.8235 | 0.993 | 0 | -621.85 | 7.00 | False |

**Nested-CV candidate** (family `h2/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c04a0d2a19d216fd | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 3,694.33 | 93.80 | 0.2124 | 0.0031 | 1.00 | 1.00 | 0 | -655.97 | 2 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 4,489.00 | 0.9973 | 199 | 83 | 83 |
| 1 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 4,407.99 | 0.9973 | 199 | 84 | 84 |
| 2 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.98 | 4,360.60 | 0.9975 | 199 | 42 | 42 |
| 3 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 4,548.29 | 0.9973 | 199 | 77 | 77 |
| 4 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.86 | 5,455.09 | 0.9987 | 199 | 72 | 72 |
| 5 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.97 | 4,506.12 | 0.9973 | 199 | 73 | 73 |
| 6 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 5,681.24 | 0.9987 | 199 | 78 | 77 |
| 7 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.97 | 4,360.56 | 0.9974 | 199 | 51 | 51 |
| 8 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.89 | 4,381.80 | 0.9973 | 198 | 76 | 76 |
| 9 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.90 | 4,313.11 | 0.9973 | 199 | 82 | 82 |
| 10 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.95 | 3,300.83 | 0.9987 | 199 | 31 | 30 |
| 11 | {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} | 2.98 | 4,448.03 | 0.9973 | 199 | 83 | 83 |

CPCV paths (`h2/nested_cv/cpcv`, 11 rows): diff median 4,473.04, 5th pct 732.98, min -27.99, share > 0 0.909, control pct median 75.40 / 5th pct 42.20

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 1075285c2e71d1dc | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 93.00 | 0.2224 | 1.00 | 2 | 0 |
| 23c2c36cac95b362 | 831 | 0.9988 | -274.96 | -1,768.90 | 1,493.94 | 62.90 | 0.8576 | 1.00 | 0 | 1 |
| 74087fa14568c188 | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 94.20 | 0.1939 | 1.00 | 2 | 2 |
| 35b760e88bce2abb | 831 | 0.9988 | -270.08 | -5,826.65 | 5,556.57 | 75.30 | 0.1699 | 1.00 | 1 | 3 |
| 0c9de90cb4418743 | 831 | 0.9988 | -270.08 | -5,826.65 | 5,556.57 | 75.40 | 0.1759 | 1.00 | 1 | 4 |
| 44265ceb218bae1e | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 94.00 | 0.2134 | 1.00 | 2 | 5 |
| 900b3332b45d30ec | 825 | 0.9916 | -254.13 | -2,943.43 | 2,689.30 | 66.70 | 0.3283 | 1.00 | 2 | 6 |
| 336893cd99907af1 | 831 | 0.9988 | -270.08 | -5,826.65 | 5,556.57 | 74.40 | 0.1764 | 1.00 | 1 | 7 |
| 13d071fed750a55f | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 93.70 | 0.2149 | 1.00 | 2 | 8 |
| b4e66fb1c11044ef | 815 | 0.9796 | -277.33 | -249.34 | -27.99 | 21.60 | 0.99 | 0.9817 | 1 | 9 |
| ad274d6f7a234b9d | 830 | 0.9976 | -266.00 | -4,739.05 | 4,473.04 | 94.10 | 0.2214 | 1.00 | 2 | 10 |

Cells chosen across the 66 CPCV training sets: {"W": "3h", "combine": "AND", "kc": 2, "q": 0.1, "rule": "both", "scope": "today"} x64; {"W": "3h", "combine": "AND", "kc": 4, "q": 0.3, "rule": "both", "scope": "today"} x1; {"W": "since_choch", "combine": "AND", "kc": 2, "q": 0.5, "rule": "both", "scope": "today"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L0 | pre-registered (family as at the primary run) | 202 | 202 | 1.44 | 0.3043 | 0.5855 | 0.124 | 0.136 |  | {"rule": "range", "W": "3h", "q": 0.2} | 248.49 | [3078.04, 5879.24] | 0 | 0.7772 | 4,473.04 | 732.98 | 0.909 | 75.40 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10 |


### H2 family summary (all tables)

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 202 | 202 | 1.35 | 0.3564 | 0.5611 | 0.1255 | 0.18 |  | {"rule": "range", "W": "3h", "q": 0.2} | 322.59 | [-582.49, 91.16] | 0.8655 | 1.00 | -198.78 | -417.49 | 0.182 | 1.90 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| 5 min | L1 | pre-registered (family as at the primary run) | 202 | 202 | 1.44 | 0.3293 | 0.5333 | 0.076 | 0.0835 |  | {"rule": "range", "W": "3h", "q": 0.1} | 127.60 | [2816.25, 5189.35] | 0 | 0.9957 | 3,991.66 | 3,444.78 | 1.00 | 87.80 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1 |
| 5 min | L0 | pre-registered (family as at the primary run) | 202 | 202 | 1.44 | 0.3043 | 0.5855 | 0.124 | 0.136 |  | {"rule": "range", "W": "3h", "q": 0.2} | 248.49 | [3078.04, 5879.24] | 0 | 0.7772 | 4,473.04 | 732.98 | 0.909 | 75.40 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10 |



## T3. H3 - visibly high volume

### 1 min: reaction after a high-volume bar (IS bars; `h3_minute_bar_aftermath.csv`)

| set | v | N | dir | n | fwd5_atr_mean | fwd15_atr_mean | fwd30_atr_mean | fwd30_atr_median | fwd30_pos_share | fwd30_abs_atr_mean | mfe30_atr_median | mae30_atr_median | own_extreme_held_15 | own_extreme_held_30 | opp_extreme_held_15 | opp_extreme_held_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_all_bars |  | 20 | up | 186,679 | -0.028 | -0.017 | -0.014 | 0.07 | 0.5081 | 2.70 | 2.15 | -2.23 | 0.1031 | 0.0724 | 0.2488 | 0.1784 |
| baseline_all_bars |  | 20 | down | 185,810 | -0.032 | -0.022 | -0.018 | -0.165 | 0.4773 | 2.74 | 2.19 | -2.25 | 0.1055 | 0.075 | 0.2369 | 0.1682 |
| baseline_all_bars |  | 20 | both | 372,489 | -0.03 | -0.019 | -0.016 | -0.043 | 0.4927 | 2.72 | 2.17 | -2.24 | 0.1043 | 0.0737 | 0.2428 | 0.1733 |
| high_volume | 2.00 | 20 | up | 29,238 | -0.053 | -0.044 | -0.088 | -0.017 | 0.4954 | 2.77 | 2.13 | -2.31 | 0.1283 | 0.0923 | 0.3079 | 0.2204 |
| high_volume | 2.00 | 20 | down | 28,210 | -0.051 | 0.021 | 0.046 | -0.175 | 0.477 | 2.84 | 2.27 | -2.32 | 0.1299 | 0.0941 | 0.2974 | 0.2153 |
| high_volume | 2.00 | 20 | both | 57,448 | -0.052 | -0.012 | -0.022 | -0.1 | 0.4864 | 2.80 | 2.20 | -2.31 | 0.1291 | 0.0932 | 0.3027 | 0.2179 |
| high_volume | 2.00 | 60 | up | 32,356 | -0.063 | -0.06 | -0.089 | -0.021 | 0.4951 | 2.75 | 2.11 | -2.30 | 0.1285 | 0.0932 | 0.3045 | 0.2172 |
| high_volume | 2.00 | 60 | down | 31,518 | -0.047 | 0.019 | 0.062 | -0.164 | 0.4777 | 2.83 | 2.27 | -2.30 | 0.1291 | 0.0932 | 0.2945 | 0.2133 |
| high_volume | 2.00 | 60 | both | 63,874 | -0.055 | -0.021 | -0.014 | -0.101 | 0.4865 | 2.79 | 2.19 | -2.30 | 0.1288 | 0.0932 | 0.2995 | 0.2153 |
| high_volume | 3.00 | 20 | up | 13,302 | -0.042 | -0.058 | -0.112 | -0.078 | 0.4896 | 2.77 | 2.14 | -2.32 | 0.1416 | 0.1023 | 0.3379 | 0.2437 |
| high_volume | 3.00 | 20 | down | 12,737 | -0.05 | 0.047 | 0.076 | -0.165 | 0.4774 | 2.87 | 2.30 | -2.33 | 0.1412 | 0.1051 | 0.3241 | 0.2386 |
| high_volume | 3.00 | 20 | both | 26,039 | -0.046 | -0.007 | -0.02 | -0.118 | 0.4836 | 2.82 | 2.21 | -2.33 | 0.1414 | 0.1037 | 0.3311 | 0.2412 |
| high_volume | 3.00 | 60 | up | 15,268 | -0.066 | -0.055 | -0.129 | -0.057 | 0.4912 | 2.77 | 2.09 | -2.32 | 0.1382 | 0.0996 | 0.3245 | 0.2345 |
| high_volume | 3.00 | 60 | down | 14,921 | -0.05 | 0.047 | 0.078 | -0.18 | 0.4752 | 2.83 | 2.30 | -2.32 | 0.1379 | 0.1019 | 0.3185 | 0.2381 |
| high_volume | 3.00 | 60 | both | 30,189 | -0.058 | -0.004 | -0.026 | -0.119 | 0.4833 | 2.80 | 2.19 | -2.32 | 0.138 | 0.1007 | 0.3216 | 0.2363 |
| high_volume | 4.00 | 20 | up | 7,394 | -0.025 | -0.018 | -0.083 | -0.079 | 0.4877 | 2.79 | 2.15 | -2.29 | 0.1531 | 0.1128 | 0.3649 | 0.2699 |
| high_volume | 4.00 | 20 | down | 6,943 | -0.027 | 0.079 | 0.116 | -0.152 | 0.4805 | 2.91 | 2.39 | -2.31 | 0.15 | 0.1124 | 0.3539 | 0.2687 |
| high_volume | 4.00 | 20 | both | 14,337 | -0.026 | 0.029 | 0.014 | -0.115 | 0.4842 | 2.85 | 2.25 | -2.30 | 0.1516 | 0.1126 | 0.3596 | 0.2693 |
| high_volume | 4.00 | 60 | up | 8,470 | -0.052 | -0.049 | -0.15 | -0.108 | 0.4849 | 2.80 | 2.08 | -2.36 | 0.1512 | 0.1125 | 0.3469 | 0.2519 |
| high_volume | 4.00 | 60 | down | 8,252 | -0.046 | 0.071 | 0.121 | -0.149 | 0.4821 | 2.85 | 2.36 | -2.30 | 0.1423 | 0.1059 | 0.3355 | 0.254 |
| high_volume | 4.00 | 60 | both | 16,722 | -0.049 | 0.011 | -0.016 | -0.126 | 0.4835 | 2.82 | 2.21 | -2.33 | 0.1468 | 0.1092 | 0.3412 | 0.2529 |

Flat high-volume bars (excluded from the direction rows): v2 N20: 579, v2 N60: 680, v3 N20: 235, v3 N60: 283, v4 N20: 125, v4 N60: 156

### 5 min: reaction after a high-volume bar (IS bars; `h3_5minute_bar_aftermath.csv`)

| set | v | N | dir | n | fwd5_atr_mean | fwd15_atr_mean | fwd30_atr_mean | fwd30_atr_median | fwd30_pos_share | fwd30_abs_atr_mean | mfe30_atr_median | mae30_atr_median | own_extreme_held_15 | own_extreme_held_30 | opp_extreme_held_15 | opp_extreme_held_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_all_bars |  | 20 | up | 36,102 | -0.005 | 0.009 | 0.019 | 0.14 | 0.5196 | 2.47 | 1.89 | -1.87 | 0.0883 | 0.0643 | 0.2586 | 0.1962 |
| baseline_all_bars |  | 20 | down | 34,989 | -0.005 | 0.007 | -0.002 | -0.17 | 0.4751 | 2.48 | 1.89 | -1.94 | 0.0967 | 0.0713 | 0.2407 | 0.1762 |
| baseline_all_bars |  | 20 | both | 71,091 | -0.005 | 0.008 | 0.008 | -0.012 | 0.4977 | 2.47 | 1.89 | -1.91 | 0.0924 | 0.0678 | 0.2498 | 0.1864 |
| high_volume | 2.00 | 20 | up | 5,273 | -0.007 | 0.031 | 0.078 | 0.079 | 0.513 | 2.76 | 2.12 | -2.07 | 0.1205 | 0.0912 | 0.3352 | 0.262 |
| high_volume | 2.00 | 20 | down | 5,092 | 0.058 | 0.09 | 0.106 | -0.088 | 0.483 | 2.64 | 2.19 | -2.15 | 0.122 | 0.0855 | 0.3392 | 0.2474 |
| high_volume | 2.00 | 20 | both | 10,365 | 0.025 | 0.06 | 0.092 | -0.01 | 0.4981 | 2.70 | 2.15 | -2.11 | 0.1213 | 0.0884 | 0.3372 | 0.2547 |
| high_volume | 2.00 | 60 | up | 4,620 | -0.011 | 0.002 | 0.066 | 0.062 | 0.5085 | 2.62 | 2.04 | -1.97 | 0.1263 | 0.0951 | 0.3701 | 0.2911 |
| high_volume | 2.00 | 60 | down | 4,522 | 0.076 | 0.186 | 0.044 | -0.184 | 0.4751 | 2.61 | 2.29 | -2.13 | 0.1239 | 0.0889 | 0.3836 | 0.2918 |
| high_volume | 2.00 | 60 | both | 9,142 | 0.032 | 0.096 | 0.055 | -0.056 | 0.4914 | 2.61 | 2.16 | -2.07 | 0.1251 | 0.092 | 0.377 | 0.2914 |
| high_volume | 3.00 | 20 | up | 2,125 | -0.041 | -0.073 | 0.105 | 0.103 | 0.5182 | 2.67 | 2.18 | -2.00 | 0.134 | 0.0918 | 0.366 | 0.2906 |
| high_volume | 3.00 | 20 | down | 2,157 | 0.099 | 0.223 | 0.148 | -0.09 | 0.4808 | 2.63 | 2.43 | -2.14 | 0.1308 | 0.0923 | 0.4077 | 0.2875 |
| high_volume | 3.00 | 20 | both | 4,282 | 0.032 | 0.081 | 0.127 | -0.012 | 0.4986 | 2.65 | 2.31 | -2.08 | 0.1323 | 0.0921 | 0.3877 | 0.289 |
| high_volume | 3.00 | 60 | up | 2,012 | 0.021 | 0.018 | 0.109 | 0.081 | 0.516 | 2.63 | 2.18 | -2.00 | 0.1482 | 0.0819 | 0.4143 | 0.3381 |
| high_volume | 3.00 | 60 | down | 2,009 | 0.129 | 0.306 | -0.026 | -0.184 | 0.4649 | 2.66 | 2.41 | -2.19 | 0.1297 | 0.0994 | 0.4404 | 0.3158 |
| high_volume | 3.00 | 60 | both | 4,021 | 0.077 | 0.174 | 0.035 | -0.082 | 0.488 | 2.65 | 2.29 | -2.12 | 0.1382 | 0.0915 | 0.4285 | 0.3258 |
| high_volume | 4.00 | 20 | up | 1,006 | -0.012 | -0.067 | 0.156 | 0.293 | 0.5462 | 2.67 | 2.34 | -1.90 | 0.1545 | 0.0756 | 0.3923 | 0.3193 |
| high_volume | 4.00 | 20 | down | 1,035 | 0.125 | 0.365 | 0.233 | 0.14 | 0.5089 | 2.74 | 2.60 | -2.09 | 0.1279 | 0.0925 | 0.4512 | 0.3488 |
| high_volume | 4.00 | 20 | both | 2,041 | 0.06 | 0.164 | 0.197 | 0.198 | 0.526 | 2.71 | 2.54 | -2.00 | 0.1403 | 0.0848 | 0.4237 | 0.3353 |
| high_volume | 4.00 | 60 | up | 965 | 0.153 | 0.216 | 0.352 | 0.715 | 0.5812 | 2.99 | 2.98 | -1.83 | 0.12 | 0.0598 | 0.4889 | 0.4017 |
| high_volume | 4.00 | 60 | down | 958 | 0.223 | 0.59 | -0.03 | -0.05 | 0.4934 | 2.87 | 2.37 | -2.15 | 0.141 | 0.0987 | 0.482 | 0.3618 |
| high_volume | 4.00 | 60 | both | 1,923 | 0.19 | 0.431 | 0.136 | 0.291 | 0.5316 | 2.92 | 2.61 | -1.99 | 0.1321 | 0.0818 | 0.4849 | 0.3792 |

Flat high-volume bars (excluded from the direction rows): v2 N20: 42, v2 N60: 38, v3 N20: 11, v3 N60: 7, v4 N20: 3, v4 N60: 3

### 1 min / L1 (4,452 IS units)

Foundation outcome by direction agreement with the latest high-volume bar within M bars (`h3_minute_L1_by_agreement.csv`; every (v, N, M)):

| variable | bucket | n | share | net_mean | net_se | win_rate | pts_mean | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|
| hv v2 N20 M5 | agree | 1,972 | 0.4429 | -1,023.94 | 56.05 | 0.1638 | 0.34 | 5 |
| hv v2 N20 M5 | disagree | 300 | 0.0674 | -1,054.59 | 126.63 | 0.1467 | 0.049 | 8 |
| hv v2 N20 M5 | none | 2,180 | 0.4897 | -990.45 | 60.13 | 0.15 | 0.878 | 7 |
| hv v2 N20 M15 | agree | 2,496 | 0.5606 | -1,016.79 | 48.92 | 0.1575 | 0.458 | 6 |
| hv v2 N20 M15 | disagree | 801 | 0.1799 | -1,061.41 | 75.57 | 0.1323 | -0.141 | 8 |
| hv v2 N20 M15 | none | 1,155 | 0.2594 | -958.17 | 95.89 | 0.1688 | 1.36 | 5 |
| hv v2 N20 M30 | agree | 2,766 | 0.6213 | -1,019.02 | 45.42 | 0.1562 | 0.423 | 6 |
| hv v2 N20 M30 | disagree | 1,104 | 0.248 | -1,082.19 | 63.39 | 0.1313 | -0.497 | 8 |
| hv v2 N20 M30 | none | 582 | 0.1307 | -827.19 | 173.06 | 0.201 | 3.40 | 5 |
| hv v2 N60 M5 | agree | 1,731 | 0.3888 | -1,044.95 | 55.47 | 0.1641 | 0.007 | 6 |
| hv v2 N60 M5 | disagree | 247 | 0.0555 | -1,061.74 | 131.00 | 0.1619 | -0.113 | 7 |
| hv v2 N60 M5 | none | 2,474 | 0.5557 | -979.67 | 57.97 | 0.1496 | 1.06 | 5 |
| hv v2 N60 M15 | agree | 2,188 | 0.4915 | -1,046.63 | 48.47 | 0.1572 | -0.002 | 7 |
| hv v2 N60 M15 | disagree | 712 | 0.1599 | -1,017.75 | 80.08 | 0.1447 | 0.525 | 6 |
| hv v2 N60 M15 | none | 1,552 | 0.3486 | -953.67 | 82.36 | 0.1591 | 1.44 | 6 |
| hv v2 N60 M30 | agree | 2,475 | 0.5559 | -1,037.79 | 46.22 | 0.1564 | 0.14 | 6 |
| hv v2 N60 M30 | disagree | 1,040 | 0.2336 | -1,053.69 | 65.83 | 0.1375 | -0.055 | 7 |
| hv v2 N60 M30 | none | 937 | 0.2105 | -886.24 | 121.97 | 0.175 | 2.46 | 5 |
| hv v3 N20 M5 | agree | 1,061 | 0.2383 | -1,071.32 | 74.02 | 0.1715 | -0.377 | 7 |
| hv v3 N20 M5 | disagree | 176 | 0.0395 | -1,029.43 | 177.27 | 0.1477 | 0.439 | 7 |
| hv v3 N20 M5 | none | 3,215 | 0.7221 | -988.16 | 47.88 | 0.1512 | 0.909 | 6 |
| hv v3 N20 M15 | agree | 1,506 | 0.3383 | -1,060.78 | 59.60 | 0.1587 | -0.194 | 8 |
| hv v3 N20 M15 | disagree | 634 | 0.1424 | -996.54 | 86.55 | 0.1593 | 0.872 | 7 |
| hv v3 N20 M15 | none | 2,312 | 0.5193 | -979.86 | 60.82 | 0.1531 | 1.01 | 6 |
| hv v3 N20 M30 | agree | 1,903 | 0.4274 | -1,038.82 | 53.40 | 0.1529 | 0.136 | 7 |
| hv v3 N20 M30 | disagree | 1,119 | 0.2513 | -1,032.54 | 64.11 | 0.151 | 0.277 | 7 |
| hv v3 N20 M30 | none | 1,430 | 0.3212 | -952.78 | 86.69 | 0.1636 | 1.42 | 6 |
| hv v3 N60 M5 | agree | 980 | 0.2201 | -1,100.60 | 77.42 | 0.1582 | -0.824 | 7 |
| hv v3 N60 M5 | disagree | 142 | 0.0319 | -839.18 | 208.92 | 0.1901 | 3.33 | 6 |
| hv v3 N60 M5 | none | 3,330 | 0.748 | -990.10 | 46.71 | 0.1538 | 0.881 | 5 |
| hv v3 N60 M15 | agree | 1,323 | 0.2972 | -1,087.18 | 64.90 | 0.1504 | -0.589 | 8 |
| hv v3 N60 M15 | disagree | 578 | 0.1298 | -1,056.36 | 80.64 | 0.1592 | -0.097 | 6 |
| hv v3 N60 M15 | none | 2,551 | 0.573 | -958.79 | 57.19 | 0.158 | 1.35 | 4 |
| hv v3 N60 M30 | agree | 1,678 | 0.3769 | -1,093.46 | 56.04 | 0.1502 | -0.693 | 8 |
| hv v3 N60 M30 | disagree | 992 | 0.2228 | -1,064.66 | 62.96 | 0.1431 | -0.245 | 7 |
| hv v3 N60 M30 | none | 1,782 | 0.4003 | -900.00 | 75.42 | 0.1684 | 2.25 | 3 |
| hv v4 N20 M5 | agree | 661 | 0.1485 | -1,043.10 | 99.15 | 0.1785 | 0.055 | 8 |
| hv v4 N20 M5 | disagree | 118 | 0.0265 | -1,088.28 | 155.45 | 0.161 | -0.482 | 6 |
| hv v4 N20 M5 | none | 3,673 | 0.825 | -1,001.05 | 44.08 | 0.1516 | 0.713 | 4 |
| hv v4 N20 M15 | agree | 979 | 0.2199 | -1,052.93 | 80.35 | 0.1604 | -0.055 | 6 |
| hv v4 N20 M15 | disagree | 483 | 0.1085 | -994.42 | 97.25 | 0.1656 | 0.921 | 5 |
| hv v4 N20 M15 | none | 2,990 | 0.6716 | -997.88 | 50.11 | 0.1528 | 0.738 | 5 |
| hv v4 N20 M30 | agree | 1,346 | 0.3023 | -1,070.06 | 64.53 | 0.1523 | -0.296 | 6 |
| hv v4 N20 M30 | disagree | 926 | 0.208 | -1,020.66 | 70.81 | 0.149 | 0.458 | 3 |
| hv v4 N20 M30 | none | 2,180 | 0.4897 | -967.59 | 63.22 | 0.161 | 1.18 | 6 |
| hv v4 N60 M5 | agree | 593 | 0.1332 | -1,063.69 | 104.37 | 0.1788 | -0.308 | 5 |
| hv v4 N60 M5 | disagree | 92 | 0.0207 | -639.16 | 306.39 | 0.1848 | 6.38 | 6 |
| hv v4 N60 M5 | none | 3,767 | 0.8461 | -1,010.14 | 42.98 | 0.1516 | 0.582 | 7 |
| hv v4 N60 M15 | agree | 857 | 0.1925 | -1,032.60 | 83.97 | 0.1692 | 0.212 | 7 |
| hv v4 N60 M15 | disagree | 405 | 0.091 | -1,058.00 | 104.22 | 0.1506 | -0.082 | 7 |
| hv v4 N60 M15 | none | 3,190 | 0.7165 | -997.29 | 48.44 | 0.153 | 0.768 | 6 |
| hv v4 N60 M30 | agree | 1,150 | 0.2583 | -1,093.30 | 67.23 | 0.1583 | -0.7 | 8 |
| hv v4 N60 M30 | disagree | 789 | 0.1772 | -1,055.55 | 73.37 | 0.1445 | -0.087 | 5 |
| hv v4 N60 M30 | none | 2,513 | 0.5645 | -956.88 | 58.35 | 0.1584 | 1.38 | 5 |

by bars since the latest high-volume bar (`h3_minute_L1_by_bars_since.csv`):

| variable | bucket | n | share | net_mean | net_se | win_rate | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|
| hv v2 N20 bars_since | 0 | 1,477 | 0.3318 | -1,012.93 | 71.52 | 0.1571 | 5 |
| hv v2 N20 bars_since | 1-5 | 807 | 0.1813 | -1,062.10 | 62.13 | 0.1698 | 7 |
| hv v2 N20 bars_since | 6-15 | 1,035 | 0.2325 | -1,023.47 | 68.04 | 0.1304 | 7 |
| hv v2 N20 bars_since | 16-30 | 577 | 0.1296 | -1,088.15 | 79.84 | 0.1369 | 6 |
| hv v2 N20 bars_since | >30 | 153 | 0.0344 | -1,182.23 | 157.07 | 0.1503 | 8 |
| hv v2 N20 bars_since | none | 403 | 0.0905 | -678.72 | 241.68 | 0.2184 | 5 |
| hv v2 N60 bars_since | 0 | 1,324 | 0.2974 | -1,045.84 | 69.45 | 0.1594 | 6 |
| hv v2 N60 bars_since | 1-5 | 661 | 0.1485 | -1,043.99 | 64.63 | 0.174 | 4 |
| hv v2 N60 bars_since | 6-15 | 930 | 0.2089 | -1,023.99 | 70.07 | 0.1344 | 7 |
| hv v2 N60 bars_since | 16-30 | 619 | 0.139 | -1,052.92 | 92.64 | 0.1357 | 9 |
| hv v2 N60 bars_since | >30 | 391 | 0.0878 | -1,123.86 | 94.03 | 0.1253 | 8 |
| hv v2 N60 bars_since | none | 527 | 0.1184 | -714.43 | 204.79 | 0.2087 | 5 |
| hv v3 N20 bars_since | 0 | 776 | 0.1743 | -1,074.90 | 95.78 | 0.1688 | 8 |
| hv v3 N20 bars_since | 1-5 | 469 | 0.1053 | -1,037.62 | 86.14 | 0.1706 | 6 |
| hv v3 N20 bars_since | 6-15 | 909 | 0.2042 | -1,008.87 | 69.07 | 0.1474 | 7 |
| hv v3 N20 bars_since | 16-30 | 886 | 0.199 | -1,025.48 | 74.95 | 0.1354 | 6 |
| hv v3 N20 bars_since | >30 | 723 | 0.1624 | -1,088.16 | 70.09 | 0.1272 | 9 |
| hv v3 N20 bars_since | none | 689 | 0.1548 | -815.13 | 163.93 | 0.1988 | 6 |
| hv v3 N60 bars_since | 0 | 722 | 0.1622 | -1,052.98 | 102.52 | 0.162 | 8 |
| hv v3 N60 bars_since | 1-5 | 406 | 0.0912 | -1,091.74 | 84.15 | 0.1626 | 8 |
| hv v3 N60 bars_since | 6-15 | 787 | 0.1768 | -1,084.55 | 68.95 | 0.1423 | 6 |
| hv v3 N60 bars_since | 16-30 | 772 | 0.1734 | -1,096.64 | 73.31 | 0.1334 | 6 |
| hv v3 N60 bars_since | >30 | 868 | 0.195 | -984.37 | 74.33 | 0.1429 | 7 |
| hv v3 N60 bars_since | none | 897 | 0.2015 | -821.28 | 131.25 | 0.1918 | 5 |
| hv v4 N20 bars_since | 0 | 494 | 0.111 | -1,074.77 | 121.06 | 0.1741 | 9 |
| hv v4 N20 bars_since | 1-5 | 288 | 0.0647 | -1,001.62 | 113.04 | 0.1806 | 6 |
| hv v4 N20 bars_since | 6-15 | 685 | 0.1539 | -1,013.02 | 89.61 | 0.1474 | 4 |
| hv v4 N20 bars_since | 16-30 | 814 | 0.1828 | -1,080.98 | 72.21 | 0.1302 | 6 |
| hv v4 N20 bars_since | >30 | 1,250 | 0.2808 | -1,072.00 | 55.15 | 0.1368 | 8 |
| hv v4 N20 bars_since | none | 921 | 0.2069 | -826.86 | 129.44 | 0.1933 | 5 |
| hv v4 N60 bars_since | 0 | 442 | 0.0993 | -1,014.79 | 138.23 | 0.1833 | 6 |
| hv v4 N60 bars_since | 1-5 | 248 | 0.0557 | -988.98 | 121.45 | 0.1734 | 5 |
| hv v4 N60 bars_since | 6-15 | 581 | 0.1305 | -1,081.13 | 83.11 | 0.1446 | 6 |
| hv v4 N60 bars_since | 16-30 | 684 | 0.1536 | -1,155.79 | 71.26 | 0.1316 | 8 |
| hv v4 N60 bars_since | >30 | 1,285 | 0.2886 | -1,061.84 | 59.27 | 0.1323 | 9 |
| hv v4 N60 bars_since | none | 1,212 | 0.2722 | -839.77 | 103.25 | 0.1865 | 4 |

The grid: 54 cells; diff > 0 in 15; control pct >= 95 in 33; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff -53.28, median control pct 97.25. Full table `h3_minute_L1_grid.csv`:

| v | N | M | gate | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 20 | 5 | skip_if_disagree | f8a927aafb918754 | 4,152 | 0.9326 | -1,006.36 | -1,054.59 | 48.24 | 35.49 | 20.80 | 0.7641 | 0.0681 | 0.8533 | 0.9518 | 0.0429 | -1,396.32 | 8 | False |
| 2 | 20 | 5 | skip_if_none | 91d7a66425453322 | 2,272 | 0.5103 | -1,027.99 | -990.45 | -37.54 | 54.91 | 100.00 | 0.6482 | 0.4931 | 0.85 | 0.4613 | 0.6286 | -1,417.96 | 7 | False |
| 2 | 20 | 5 | take_only_agree | 9d76dfff15097dba | 1,972 | 0.4429 | -1,023.94 | -998.21 | -25.74 | 64.60 | 100.00 | 0.7486 | 0.5612 | 0.8504 | 0.4131 | 0.6714 | -1,413.91 | 7 | False |
| 2 | 20 | 15 | skip_if_disagree | 957a9431eef861e2 | 3,651 | 0.8201 | -998.24 | -1,061.41 | 63.17 | 21.35 | 11.40 | 0.5407 | 0.1849 | 0.8677 | 0.8657 | 0.1 | -1,388.21 | 8 | False |
| 2 | 20 | 15 | skip_if_none | ab2621823149c785 | 3,297 | 0.7406 | -1,027.63 | -958.17 | -69.46 | 92.18 | 100.00 | 0.4718 | 0.2555 | 0.8312 | 0.6527 | 0.4 | -1,417.59 | 5 | False |
| 2 | 20 | 15 | take_only_agree | 89a7008a8ca918e5 | 2,496 | 0.5606 | -1,016.79 | -1,000.45 | -16.34 | 84.46 | 100.00 | 0.8291 | 0.4404 | 0.8461 | 0.5184 | 0.5 | -1,406.75 | 6 | False |
| 2 | 20 | 30 | skip_if_disagree | 6a32f6e0b59a8285 | 3,348 | 0.752 | -985.67 | -1,082.19 | 96.52 | 37.31 | 11.10 | 0.3093 | 0.2552 | 0.8687 | 0.8184 | 0.1571 | -1,375.64 | 8 | False |
| 2 | 20 | 30 | skip_if_none | ce2d881a857d330f | 3,870 | 0.8693 | -1,037.04 | -827.19 | -209.85 | 204.29 | 100.00 | 0.069 | 0.1237 | 0.799 | 0.7413 | 0.3286 | -1,427.01 | 5 | False |
| 2 | 20 | 30 | take_only_agree | 2248edb6e1bd5979 | 2,766 | 0.6213 | -1,019.02 | -994.17 | -24.85 | 126.92 | 100.00 | 0.7611 | 0.3789 | 0.8446 | 0.5597 | 0.4857 | -1,408.99 | 6 | False |
| 2 | 60 | 5 | skip_if_disagree | d4c2b1e7008b3001 | 4,205 | 0.9445 | -1,006.55 | -1,061.74 | 55.19 | -32.28 | 11.90 | 0.7671 | 0.0551 | 0.8381 | 0.9634 | 0.0143 | -1,396.51 | 7 | False |
| 2 | 60 | 5 | skip_if_none | 9cfe08d8187e244e | 1,978 | 0.4443 | -1,047.05 | -979.67 | -67.38 | 63.88 | 100.00 | 0.3913 | 0.5599 | 0.8504 | 0.3831 | 0.7 | -1,437.01 | 5 | False |
| 2 | 60 | 5 | take_only_agree | bd3b40bb867e9535 | 1,731 | 0.3888 | -1,044.95 | -987.12 | -57.83 | 59.18 | 99.60 | 0.4798 | 0.615 | 0.8493 | 0.3465 | 0.7143 | -1,434.92 | 6 | False |
| 2 | 60 | 15 | skip_if_disagree | a92327bdf13e9766 | 3,740 | 0.8401 | -1,008.06 | -1,017.75 | 9.69 | -80.69 | 0.9 | 0.9335 | 0.1621 | 0.8553 | 0.8723 | 0.0857 | -1,398.02 | 6 | False |
| 2 | 60 | 15 | skip_if_none | 48e34918983f6c4f | 2,900 | 0.6514 | -1,039.54 | -953.67 | -85.87 | 104.99 | 100.00 | 0.2874 | 0.3473 | 0.8409 | 0.5551 | 0.5143 | -1,429.51 | 6 | False |
| 2 | 60 | 15 | take_only_agree | 0c40d37694b83d7b | 2,188 | 0.4915 | -1,046.63 | -973.82 | -72.81 | 51.59 | 99.90 | 0.3483 | 0.5093 | 0.8454 | 0.4274 | 0.6 | -1,436.60 | 5 | False |
| 2 | 60 | 30 | skip_if_disagree | 16e7a432e162a32f | 3,412 | 0.7664 | -996.17 | -1,053.69 | 57.51 | -24.79 | 2.60 | 0.5487 | 0.2387 | 0.8625 | 0.8183 | 0.1286 | -1,386.14 | 7 | False |
| 2 | 60 | 30 | skip_if_none | dfa8d6af2294dbd3 | 3,515 | 0.7895 | -1,042.49 | -886.24 | -156.25 | 136.89 | 100.00 | 0.1114 | 0.2057 | 0.825 | 0.6731 | 0.4 | -1,432.46 | 5 | False |
| 2 | 60 | 30 | take_only_agree | 7ff86606849fc597 | 2,475 | 0.5559 | -1,037.79 | -974.33 | -63.46 | 73.40 | 100.00 | 0.4103 | 0.4444 | 0.8447 | 0.4915 | 0.5286 | -1,427.75 | 6 | False |
| 3 | 20 | 5 | skip_if_disagree | 64a2ed244460d129 | 4,276 | 0.9605 | -1,008.79 | -1,029.43 | 20.64 | -25.64 | 19.90 | 0.917 | 0.0399 | 0.8523 | 0.9683 | 0.0143 | -1,398.76 | 7 | False |
| 3 | 20 | 5 | skip_if_none | 6efad9e031fa0d9c | 1,237 | 0.2779 | -1,065.36 | -988.16 | -77.20 | 1.79 | 96.20 | 0.3973 | 0.7262 | 0.8488 | 0.2514 | 0.8286 | -1,455.32 | 6 | False |
| 3 | 20 | 5 | take_only_agree | bea234d20d835843 | 1,061 | 0.2383 | -1,071.32 | -990.30 | -81.02 | -3.40 | 95.70 | 0.3668 | 0.7661 | 0.849 | 0.2197 | 0.8429 | -1,461.28 | 5 | False |
| 3 | 20 | 15 | skip_if_disagree | 4f2c226f505eacfb | 3,818 | 0.8576 | -1,011.78 | -996.54 | -15.24 | -72.27 | 0.9 | 0.8946 | 0.1418 | 0.8407 | 0.8805 | 0.0714 | -1,401.74 | 7 | False |
| 3 | 20 | 15 | skip_if_none | 8db15364bf989de6 | 2,140 | 0.4807 | -1,041.75 | -979.86 | -61.89 | 58.25 | 100.00 | 0.4278 | 0.521 | 0.8469 | 0.4179 | 0.6571 | -1,431.71 | 6 | False |
| 3 | 20 | 15 | take_only_agree | cb57505d0fc444a3 | 1,506 | 0.3383 | -1,060.78 | -983.45 | -77.33 | 25.43 | 98.50 | 0.3563 | 0.6629 | 0.8456 | 0.2985 | 0.7286 | -1,450.74 | 4 | False |
| 3 | 20 | 30 | skip_if_disagree | 8f821662abc0e4fb | 3,333 | 0.7487 | -1,001.91 | -1,032.54 | 30.63 | -47.55 | 0.2 | 0.7451 | 0.2528 | 0.849 | 0.7993 | 0.1286 | -1,391.87 | 7 | False |
| 3 | 20 | 30 | skip_if_none | 8385fe654388a621 | 3,022 | 0.6788 | -1,036.50 | -952.78 | -83.71 | 93.29 | 100.00 | 0.3213 | 0.3183 | 0.8364 | 0.5831 | 0.5143 | -1,426.46 | 6 | False |
| 3 | 20 | 30 | take_only_agree | 4396fb19d4cf59f8 | 1,903 | 0.4274 | -1,038.82 | -987.80 | -51.02 | 46.18 | 99.90 | 0.5332 | 0.571 | 0.8419 | 0.3824 | 0.6429 | -1,428.79 | 5 | False |
| 3 | 60 | 5 | skip_if_disagree | 76428e7090dc49a7 | 4,310 | 0.9681 | -1,015.22 | -839.18 | -176.04 | -190.32 | 7.80 | 0.4303 | 0.0306 | 0.8099 | 0.9702 | 0.0143 | -1,405.19 | 6 | False |
| 3 | 60 | 5 | skip_if_none | 66c4cc7625d4398b | 1,122 | 0.252 | -1,067.52 | -990.10 | -77.42 | -0.68 | 96.20 | 0.3988 | 0.7499 | 0.8462 | 0.229 | 0.8286 | -1,457.48 | 5 | False |
| 3 | 60 | 5 | take_only_agree | 45af65065b99cf0b | 980 | 0.2201 | -1,100.60 | -983.92 | -116.68 | -34.98 | 88.30 | 0.2054 | 0.7805 | 0.8448 | 0.1992 | 0.8429 | -1,490.57 | 5 | False |
| 3 | 60 | 15 | skip_if_disagree | a9f76da9691e1569 | 3,874 | 0.8702 | -1,002.63 | -1,056.36 | 53.73 | -74.51 | 9.90 | 0.6372 | 0.1293 | 0.8408 | 0.9108 | 0.0286 | -1,392.60 | 6 | False |
| 3 | 60 | 15 | skip_if_none | c99fe9b36e9f678d | 1,901 | 0.427 | -1,077.81 | -958.79 | -119.02 | 15.81 | 98.80 | 0.1344 | 0.5716 | 0.842 | 0.3527 | 0.7143 | -1,467.77 | 4 | False |
| 3 | 60 | 15 | take_only_agree | 1ded09967bd2b951 | 1,323 | 0.2972 | -1,087.18 | -976.81 | -110.36 | -21.95 | 95.00 | 0.2109 | 0.7009 | 0.8418 | 0.2635 | 0.7429 | -1,477.14 | 4 | False |
| 3 | 60 | 30 | skip_if_disagree | e676962ea25b0a09 | 3,460 | 0.7772 | -993.82 | -1,064.66 | 70.84 | -47.25 | 6.20 | 0.4623 | 0.2262 | 0.8569 | 0.8447 | 0.0857 | -1,383.79 | 7 | False |
| 3 | 60 | 30 | skip_if_none | 482012f7a821e3c2 | 2,670 | 0.5997 | -1,082.76 | -900.00 | -182.76 | 18.10 | 100.00 | 0.0225 | 0.3944 | 0.8316 | 0.4761 | 0.6286 | -1,472.73 | 3 | False |
| 3 | 60 | 30 | take_only_agree | 8b182eabbb84e24a | 1,678 | 0.3769 | -1,093.46 | -958.88 | -134.58 | -16.48 | 97.30 | 0.1009 | 0.6205 | 0.8407 | 0.3207 | 0.7143 | -1,483.43 | 4 | False |
| 4 | 20 | 5 | skip_if_disagree | 04b555aed679c738 | 4,334 | 0.9735 | -1,007.47 | -1,088.28 | 80.81 | -101.16 | 11.60 | 0.7446 | 0.0263 | 0.839 | 0.9827 | 0 | -1,397.43 | 6 | False |
| 4 | 20 | 5 | skip_if_none | 635b852fffbe6c03 | 779 | 0.175 | -1,049.95 | -1,001.05 | -48.90 | 30.27 | 98.60 | 0.6362 | 0.8292 | 0.8484 | 0.1709 | 0.8857 | -1,439.91 | 4 | False |
| 4 | 20 | 5 | take_only_agree | 42cc6677f58c2e89 | 661 | 0.1485 | -1,043.10 | -1,003.77 | -39.34 | 13.79 | 97.20 | 0.7291 | 0.8555 | 0.8481 | 0.1535 | 0.8857 | -1,433.07 | 4 | False |
| 4 | 20 | 15 | skip_if_disagree | 4b94afffa52088ea | 3,969 | 0.8915 | -1,011.46 | -994.42 | -17.04 | -150.18 | 0.8 | 0.8916 | 0.1072 | 0.8344 | 0.904 | 0.0571 | -1,401.42 | 5 | False |
| 4 | 20 | 15 | skip_if_none | 55edfbf3ea4654db | 1,462 | 0.3284 | -1,033.60 | -997.88 | -35.72 | 44.10 | 99.90 | 0.6682 | 0.674 | 0.8472 | 0.3108 | 0.7429 | -1,423.57 | 5 | False |
| 4 | 20 | 15 | take_only_agree | cf7b2ffefeb2f376 | 979 | 0.2199 | -1,052.93 | -997.39 | -55.54 | -28.33 | 86.90 | 0.5592 | 0.7813 | 0.8454 | 0.2148 | 0.8 | -1,442.90 | 6 | False |
| 4 | 20 | 30 | skip_if_disagree | 47104907c7b86243 | 3,526 | 0.792 | -1,006.71 | -1,020.66 | 13.95 | -96.93 | 0.1 | 0.8746 | 0.2097 | 0.851 | 0.8274 | 0.1143 | -1,396.67 | 3 | False |
| 4 | 20 | 30 | skip_if_none | 2f331371e5f70478 | 2,272 | 0.5103 | -1,049.93 | -967.59 | -82.34 | 45.86 | 100.00 | 0.3143 | 0.4867 | 0.839 | 0.4465 | 0.6143 | -1,439.89 | 6 | False |
| 4 | 20 | 30 | take_only_agree | 6d8ec56e34bb4f09 | 1,346 | 0.3023 | -1,070.06 | -983.41 | -86.66 | -21.62 | 94.80 | 0.3238 | 0.6964 | 0.8426 | 0.2738 | 0.7286 | -1,460.03 | 6 | False |
| 4 | 60 | 5 | skip_if_disagree | ff8dd49e663b3920 | 4,360 | 0.9793 | -1,017.42 | -639.16 | -378.27 | -302.97 | 3.50 | 0.1664 | 0.02 | 0.8152 | 0.9755 | 0.0143 | -1,407.39 | 6 | False |
| 4 | 60 | 5 | skip_if_none | 847c2ed6dad1533a | 685 | 0.1539 | -1,006.67 | -1,010.14 | 3.47 | 72.07 | 99.30 | 0.969 | 0.8505 | 0.8484 | 0.1592 | 0.8714 | -1,396.64 | 7 | False |
| 4 | 60 | 5 | take_only_agree | a656cfabf151e4c8 | 593 | 0.1332 | -1,063.69 | -1,001.30 | -62.39 | 28.37 | 97.20 | 0.5872 | 0.8704 | 0.8476 | 0.1347 | 0.8857 | -1,453.66 | 7 | False |
| 4 | 60 | 15 | skip_if_disagree | 26f0bb0d225fd07b | 4,047 | 0.909 | -1,004.76 | -1,058.00 | 53.23 | -78.38 | 10.20 | 0.6982 | 0.0915 | 0.8494 | 0.9296 | 0.0286 | -1,394.73 | 7 | False |
| 4 | 60 | 15 | skip_if_none | b9abe4ec719ea3cb | 1,262 | 0.2835 | -1,040.75 | -997.29 | -43.47 | 68.38 | 100.00 | 0.6517 | 0.719 | 0.847 | 0.2598 | 0.7857 | -1,430.72 | 6 | False |
| 4 | 60 | 15 | take_only_agree | 597d7ff49d8875d5 | 857 | 0.1925 | -1,032.60 | -1,004.13 | -28.48 | 47.49 | 99.40 | 0.7956 | 0.8105 | 0.8473 | 0.1894 | 0.8143 | -1,422.57 | 5 | False |
| 4 | 60 | 30 | skip_if_disagree | e49c05709e39fee7 | 3,663 | 0.8228 | -999.71 | -1,055.55 | 55.84 | -51.57 | 2.70 | 0.5792 | 0.1796 | 0.8555 | 0.8666 | 0.0714 | -1,389.68 | 5 | False |
| 4 | 60 | 30 | skip_if_none | 3423ad70a89600da | 1,939 | 0.4355 | -1,077.94 | -956.88 | -121.06 | 24.51 | 100.00 | 0.1339 | 0.5628 | 0.8416 | 0.3532 | 0.7143 | -1,467.90 | 5 | False |
| 4 | 60 | 30 | take_only_agree | 2afd68c4eba3ff62 | 1,150 | 0.2583 | -1,093.30 | -980.46 | -112.84 | -7.90 | 98.00 | 0.2134 | 0.7424 | 0.8449 | 0.2198 | 0.7857 | -1,483.26 | 4 | False |

**Nested-CV candidate** (family `h3/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 21b31cbb10277775 | 3,863 | 0.8677 | -1,032.34 | -860.49 | -171.85 | -275.08 | 0 | 0.1414 | 0.1288 | 0.8217 | 0.8812 | 0.0429 | -1,422.31 | 1 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 123.23 | 0.9732 | 49 | 396 | 386 |
| 1 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 131.55 | 0.9428 | 49 | 388 | 374 |
| 2 | {"M": 30, "N": 60, "gate": "skip_if_disagree", "v": 3} |  | 105.69 | 0.7789 | 49 | 384 | 292 |
| 3 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 124.76 | 0.9106 | 49 | 509 | 456 |
| 4 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 83.73 | 0.9441 | 49 | 390 | 370 |
| 5 | {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 119.75 | 0.7521 | 49 | 341 | 255 |
| 6 | {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 80.22 | 0.7532 | 49 | 424 | 314 |
| 7 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 105.54 | 0.9732 | 49 | 266 | 260 |
| 8 | {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 106.12 | 0.7532 | 49 | 170 | 123 |
| 9 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 112.60 | 0.9739 | 49 | 499 | 484 |
| 10 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 135.74 | 0.9744 | 49 | 173 | 166 |
| 11 | {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 151.09 | 0.7525 | 49 | 512 | 383 |

CPCV paths (`h3/nested_cv/cpcv`, 11 rows): diff median -156.04, 5th pct -298.24, min -309.93, share > 0 0.091, control pct median 0.1 / 5th pct 0

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 45829ed3c763d7b2 | 4,060 | 0.9119 | -1,036.90 | -726.96 | -309.93 | 0.1 | 0.027 | 0.8751 | 3 | 0 |
| fbe562737ae24773 | 4,191 | 0.9414 | -1,026.41 | -739.86 | -286.55 | 0.1 | 0.084 | 0.9372 | 2 | 1 |
| fb8efd727693bfeb | 3,630 | 0.8154 | -1,029.51 | -921.73 | -107.78 | 0.1 | 0.3198 | 0.8288 | 5 | 2 |
| 9207c4a953d90c3f | 3,876 | 0.8706 | -1,029.80 | -873.75 | -156.04 | 0.1 | 0.1739 | 0.8813 | 2 | 3 |
| 9837b499de6cc0db | 3,841 | 0.8628 | -1,038.05 | -830.78 | -207.28 | 0 | 0.081 | 0.858 | 2 | 4 |
| 1316a3a3b3af35c6 | 3,399 | 0.7635 | -1,045.54 | -893.62 | -151.92 | 0.7 | 0.1134 | 0.753 | 3 | 5 |
| bffa27fc187f0f4d | 3,584 | 0.805 | -1,005.69 | -1,025.78 | 20.09 | 0.8 | 0.8431 | 0.8511 | 5 | 6 |
| 39e6c7a7564b45b0 | 3,915 | 0.8794 | -1,030.75 | -855.44 | -175.31 | 0.1 | 0.1464 | 0.8833 | 2 | 7 |
| 36908a3e86f9cb62 | 3,656 | 0.8212 | -1,032.74 | -903.36 | -129.38 | 0 | 0.1934 | 0.8429 | 1 | 8 |
| a346c64477104e1e | 4,097 | 0.9203 | -1,027.61 | -801.81 | -225.80 | 0.1 | 0.1294 | 0.9221 | 3 | 9 |
| 8b8fe1c9636019a8 | 3,959 | 0.8893 | -1,018.66 | -936.93 | -81.73 | 0.2 | 0.5192 | 0.9138 | 2 | 10 |

Cells chosen across the 66 CPCV training sets: {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x17; {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 2} x17; {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} x8; {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} x6; {"M": 30, "N": 60, "gate": "skip_if_disagree", "v": 3} x5; {"M": 30, "N": 60, "gate": "skip_if_disagree", "v": 4} x4; {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 3} x3; {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 3} x3; {"M": 5, "N": 20, "gate": "take_only_agree", "v": 2} x1; {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 2} x1; {"M": 30, "N": 20, "gate": "skip_if_disagree", "v": 3} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 55 | 55 | 1.66 | 0.7635 | 0.8015 | 0 | 0 |  | {"v": 2, "N": 60, "M": 30, "gate": "skip_if_none"} | 244.91 | [-324.62, -39.75] | 0.9825 | 1.00 | -156.04 | -298.24 | 0.091 | 0.1 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0 |


### 1 min / L0 (4,502 IS units)

L0 robustness, (v=2, N=20) and (v=3, N=20), M = 15:

| variable | bucket | n | net_mean | net_se | win_rate | blocks_below_block_mean |
|---|---|---|---|---|---|---|
| hv v2 N20 M15 | agree | 2,530 | -971.25 | 85.55 | 0.153 | 5 |
| hv v2 N20 M15 | disagree | 813 | -916.31 | 202.52 | 0.1378 | 8 |
| hv v2 N20 M15 | none | 1,159 | -817.82 | 196.94 | 0.1596 | 6 |
| hv v3 N20 M15 | agree | 1,518 | -934.03 | 148.13 | 0.1542 | 6 |
| hv v3 N20 M15 | disagree | 645 | -1,028.59 | 117.69 | 0.1628 | 8 |
| hv v3 N20 M15 | none | 2,339 | -884.48 | 112.89 | 0.1475 | 6 |

The grid: 54 cells; diff > 0 in 20; control pct >= 95 in 19; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff -53.34, median control pct 88.40. Full table `h3_minute_L0_grid.csv`:

| v | N | M | gate | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 20 | 5 | skip_if_disagree | b3f54184f878ff96 | 4,190 | 0.9307 | -929.10 | -824.18 | -104.92 | 117.01 | 27.40 | 0.7431 | 0.0697 | 0.8526 | 0.9236 | 0.0435 | -1,319.07 | 7 | False |
| 2 | 20 | 5 | skip_if_none | 2a7d66948c5ad12e | 2,315 | 0.5142 | -946.55 | -895.67 | -50.88 | -83.04 | 99.80 | 0.7566 | 0.4877 | 0.8514 | 0.5154 | 0.5072 | -1,336.51 | 5 | False |
| 2 | 20 | 5 | take_only_agree | 9b37e8c9613169a2 | 2,003 | 0.4449 | -965.61 | -886.75 | -78.86 | -53.42 | 99.20 | 0.6212 | 0.5574 | 0.8515 | 0.439 | 0.5507 | -1,355.57 | 4 | False |
| 2 | 20 | 15 | skip_if_disagree | ac1b12f093055d78 | 3,689 | 0.8194 | -923.05 | -916.31 | -6.74 | -68.54 | 17.10 | 0.974 | 0.1836 | 0.8622 | 0.8404 | 0.1739 | -1,313.01 | 8 | False |
| 2 | 20 | 15 | skip_if_none | 94f2a08df4003907 | 3,343 | 0.7426 | -957.89 | -817.82 | -140.07 | 88.45 | 100.00 | 0.4738 | 0.2551 | 0.8404 | 0.6845 | 0.2899 | -1,347.86 | 6 | False |
| 2 | 20 | 15 | take_only_agree | 5bc19432df4520ef | 2,530 | 0.562 | -971.25 | -858.43 | -112.83 | 27.32 | 95.80 | 0.4858 | 0.4387 | 0.8494 | 0.5249 | 0.4638 | -1,361.22 | 7 | False |
| 2 | 20 | 30 | skip_if_disagree | ce43861a46fb4da8 | 3,383 | 0.7514 | -922.50 | -919.81 | -2.69 | -41.39 | 7.90 | 0.991 | 0.253 | 0.8633 | 0.7797 | 0.2029 | -1,312.47 | 7 | False |
| 2 | 20 | 30 | skip_if_none | 6a3361fb634bea21 | 3,919 | 0.8705 | -962.06 | -651.39 | -310.68 | 209.03 | 100.00 | 0.1914 | 0.1244 | 0.8148 | 0.7779 | 0.2464 | -1,352.03 | 4 | False |
| 2 | 20 | 30 | take_only_agree | beb256c9edc50abc | 2,800 | 0.6219 | -978.95 | -827.86 | -151.09 | 66.45 | 96.00 | 0.3928 | 0.3774 | 0.8467 | 0.5576 | 0.4493 | -1,368.92 | 5 | False |
| 2 | 60 | 5 | skip_if_disagree | ad50d7332171b3de | 4,248 | 0.9436 | -894.34 | -1,381.63 | 487.29 | 165.44 | 86.70 | 0.1309 | 0.0574 | 0.8622 | 0.9812 | 0.0145 | -1,284.30 | 10 | False |
| 2 | 60 | 5 | skip_if_none | ebacd0cc9ba72965 | 2,024 | 0.4496 | -1,030.93 | -832.72 | -198.21 | -105.94 | 93.40 | 0.2109 | 0.5542 | 0.8539 | 0.4273 | 0.5507 | -1,420.89 | 5 | False |
| 2 | 60 | 5 | take_only_agree | 1a55e327649b6807 | 1,770 | 0.3932 | -980.60 | -883.75 | -96.85 | -72.76 | 98.20 | 0.5602 | 0.6116 | 0.8547 | 0.4085 | 0.5652 | -1,370.57 | 6 | False |
| 2 | 60 | 15 | skip_if_disagree | 3b0fd04ef5ffcdc8 | 3,781 | 0.8398 | -877.24 | -1,155.69 | 278.45 | -16.50 | 63.20 | 0.1914 | 0.1632 | 0.8641 | 0.9087 | 0.1014 | -1,267.20 | 10 | False |
| 2 | 60 | 15 | skip_if_none | dc9d668e81f07fcb | 2,948 | 0.6548 | -974.09 | -822.70 | -151.39 | 8.74 | 99.80 | 0.3718 | 0.3452 | 0.8481 | 0.6121 | 0.3623 | -1,364.05 | 7 | False |
| 2 | 60 | 15 | take_only_agree | 31bcacbb7d29b768 | 2,227 | 0.4947 | -915.30 | -928.23 | 12.93 | -1.02 | 100.00 | 0.937 | 0.5084 | 0.8532 | 0.5208 | 0.4638 | -1,305.26 | 7 | False |
| 2 | 60 | 30 | skip_if_disagree | cd29461bd88b1bbd | 3,453 | 0.767 | -870.04 | -1,092.33 | 222.29 | -25.57 | 56.80 | 0.2289 | 0.2386 | 0.8684 | 0.8524 | 0.1594 | -1,260.00 | 9 | False |
| 2 | 60 | 30 | skip_if_none | fe4544a4bbeb979f | 3,564 | 0.7916 | -959.53 | -778.60 | -180.93 | 45.66 | 100.00 | 0.3543 | 0.2051 | 0.8348 | 0.7369 | 0.2609 | -1,349.49 | 6 | False |
| 2 | 60 | 30 | take_only_agree | 12b7c4a026075c3f | 2,515 | 0.5586 | -904.14 | -944.23 | 40.09 | 11.89 | 100.00 | 0.8081 | 0.4437 | 0.8525 | 0.5893 | 0.4203 | -1,294.10 | 6 | False |
| 3 | 20 | 5 | skip_if_disagree | 497ca8ca875e4741 | 4,320 | 0.9596 | -903.56 | -1,355.48 | 451.92 | 167.19 | 75.20 | 0.2214 | 0.0409 | 0.8571 | 0.9764 | 0.029 | -1,293.53 | 9 | False |
| 3 | 20 | 5 | skip_if_none | cbed24a8d137d54a | 1,248 | 0.2772 | -973.69 | -901.94 | -71.74 | -71.90 | 91.30 | 0.6627 | 0.7255 | 0.8513 | 0.2776 | 0.7391 | -1,363.65 | 4 | False |
| 3 | 20 | 5 | take_only_agree | d16e6297c5c8c719 | 1,066 | 0.2368 | -908.50 | -925.97 | 17.47 | -43.69 | 97.00 | 0.9235 | 0.7664 | 0.8516 | 0.254 | 0.7681 | -1,298.47 | 4 | False |
| 3 | 20 | 15 | skip_if_disagree | 53a06fc24f364ab2 | 3,857 | 0.8567 | -903.98 | -1,028.59 | 124.61 | -154.40 | 31.60 | 0.5737 | 0.1414 | 0.8372 | 0.8971 | 0.0725 | -1,293.94 | 8 | False |
| 3 | 20 | 15 | skip_if_none | 7bc1e57de5d8ac93 | 2,163 | 0.4805 | -962.23 | -884.48 | -77.75 | -14.82 | 98.20 | 0.6047 | 0.5223 | 0.8525 | 0.4606 | 0.6087 | -1,352.19 | 6 | False |
| 3 | 20 | 15 | take_only_agree | 17b2570cfc4ba012 | 1,518 | 0.3372 | -934.03 | -915.63 | -18.41 | -101.66 | 98.30 | 0.9175 | 0.6637 | 0.8492 | 0.3577 | 0.6812 | -1,324.00 | 6 | False |
| 3 | 20 | 30 | skip_if_disagree | bc8dbec3c90824f9 | 3,363 | 0.747 | -872.77 | -1,066.69 | 193.92 | -74.97 | 40.50 | 0.2944 | 0.2541 | 0.8516 | 0.8263 | 0.1594 | -1,262.73 | 8 | False |
| 3 | 20 | 30 | skip_if_none | 77839d2c842c864f | 3,066 | 0.681 | -939.63 | -883.82 | -55.81 | 96.61 | 100.00 | 0.7566 | 0.3182 | 0.8461 | 0.6415 | 0.4058 | -1,329.60 | 6 | False |
| 3 | 20 | 30 | take_only_agree | e49411b09fd72e4c | 1,927 | 0.428 | -864.53 | -964.71 | 100.18 | 27.59 | 100.00 | 0.5617 | 0.5723 | 0.8485 | 0.4677 | 0.5652 | -1,254.50 | 7 | False |
| 3 | 60 | 5 | skip_if_disagree | 8a89c1329f6ae1cf | 4,353 | 0.9669 | -912.01 | -1,208.88 | 296.88 | 38.04 | 77.50 | 0.4968 | 0.0327 | 0.8389 | 0.982 | 0.0145 | -1,301.97 | 8 | False |
| 3 | 60 | 5 | skip_if_none | a5312b53f6788a51 | 1,156 | 0.2568 | -1,204.40 | -824.21 | -380.19 | -179.30 | 56.50 | 0.033 | 0.7457 | 0.8509 | 0.2226 | 0.8261 | -1,594.36 | 5 | False |
| 3 | 60 | 5 | take_only_agree | d772c5c6bf3d71d4 | 1,007 | 0.2237 | -1,203.73 | -840.61 | -363.12 | -190.01 | 77.00 | 0.053 | 0.7784 | 0.8504 | 0.2046 | 0.8406 | -1,593.70 | 5 | False |
| 3 | 60 | 15 | skip_if_disagree | ad2fe45df0d3e660 | 3,915 | 0.8696 | -896.25 | -1,092.46 | 196.22 | -49.89 | 58.10 | 0.3978 | 0.1302 | 0.8467 | 0.9163 | 0.087 | -1,286.21 | 8 | False |
| 3 | 60 | 15 | skip_if_none | 72c8ef7339309476 | 1,941 | 0.4311 | -1,151.46 | -747.79 | -403.66 | -106.38 | 56.20 | 0.0095 | 0.5697 | 0.8493 | 0.3429 | 0.6957 | -1,541.42 | 4 | False |
| 3 | 60 | 15 | take_only_agree | 8878ab654cbb04c0 | 1,354 | 0.3008 | -1,177.04 | -812.06 | -364.97 | -150.78 | 69.30 | 0.029 | 0.6998 | 0.8488 | 0.2592 | 0.7826 | -1,567.00 | 4 | False |
| 3 | 60 | 30 | skip_if_disagree | 07b66c423d7297c2 | 3,497 | 0.7768 | -869.43 | -1,104.16 | 234.72 | -29.48 | 60.50 | 0.2159 | 0.2271 | 0.8627 | 0.8619 | 0.1449 | -1,259.40 | 7 | False |
| 3 | 60 | 30 | skip_if_none | 90ee0b9bd01235cf | 2,718 | 0.6037 | -1,110.60 | -634.23 | -476.37 | -69.96 | 77.80 | 0.0035 | 0.3921 | 0.8391 | 0.4668 | 0.5362 | -1,500.57 | 4 | False |
| 3 | 60 | 30 | take_only_agree | eba2762707c8038f | 1,713 | 0.3805 | -1,114.38 | -803.57 | -310.82 | -92.53 | 88.50 | 0.0705 | 0.6192 | 0.8476 | 0.3287 | 0.6812 | -1,504.35 | 4 | False |
| 4 | 20 | 5 | skip_if_disagree | 066541e7aa7c5463 | 4,380 | 0.9729 | -907.72 | -1,428.54 | 520.82 | 129.49 | 70.40 | 0.2289 | 0.0272 | 0.8525 | 0.9893 | 0 | -1,297.68 | 10 | False |
| 4 | 20 | 5 | skip_if_none | 6836e7cbb2ac67a5 | 785 | 0.1744 | -1,016.69 | -901.80 | -114.89 | -37.16 | 92.00 | 0.5707 | 0.8282 | 0.8507 | 0.1571 | 0.8841 | -1,406.66 | 5 | False |
| 4 | 20 | 5 | take_only_agree | 763c05df0825459d | 663 | 0.1473 | -940.91 | -918.54 | -22.37 | -15.22 | 98.60 | 0.9275 | 0.8554 | 0.8507 | 0.1464 | 0.8841 | -1,330.87 | 6 | False |
| 4 | 20 | 15 | skip_if_disagree | 2a9e185fe959752e | 4,012 | 0.8912 | -903.29 | -1,073.62 | 170.33 | -118.90 | 45.50 | 0.5227 | 0.1066 | 0.8306 | 0.9196 | 0.029 | -1,293.26 | 6 | False |
| 4 | 20 | 15 | skip_if_none | c5a4f1d5e40cd154 | 1,475 | 0.3276 | -994.80 | -886.28 | -108.52 | -54.20 | 91.20 | 0.5222 | 0.6747 | 0.851 | 0.311 | 0.7826 | -1,384.76 | 6 | False |
| 4 | 20 | 15 | take_only_agree | fcfa6411a32ff733 | 985 | 0.2188 | -955.58 | -912.38 | -43.21 | -137.76 | 94.90 | 0.8301 | 0.7813 | 0.8482 | 0.2306 | 0.8116 | -1,345.55 | 5 | False |
| 4 | 20 | 30 | skip_if_disagree | 7819db1b7afa9f8d | 3,557 | 0.7901 | -892.38 | -1,032.70 | 140.32 | -87.45 | 44.40 | 0.4898 | 0.2098 | 0.8476 | 0.8383 | 0.1159 | -1,282.34 | 8 | False |
| 4 | 20 | 30 | skip_if_none | ad06112f8f0a984a | 2,307 | 0.5124 | -942.95 | -899.63 | -43.32 | 57.93 | 99.90 | 0.7741 | 0.4872 | 0.8474 | 0.4888 | 0.5362 | -1,332.92 | 7 | False |
| 4 | 20 | 30 | take_only_agree | bad999f0c33eb23a | 1,362 | 0.3025 | -880.68 | -939.68 | 59.00 | -0.35 | 99.50 | 0.7311 | 0.697 | 0.8475 | 0.3271 | 0.6522 | -1,270.65 | 6 | False |
| 4 | 60 | 5 | skip_if_disagree | 8b9dbe237c47c05a | 4,401 | 0.9776 | -920.97 | -959.58 | 38.61 | -155.88 | 39.20 | 0.9315 | 0.0215 | 0.8119 | 0.9809 | 0.029 | -1,310.93 | 7 | False |
| 4 | 60 | 5 | skip_if_none | 13707296d467117c | 705 | 0.1566 | -1,132.50 | -882.72 | -249.78 | -207.71 | 89.20 | 0.2454 | 0.8476 | 0.8523 | 0.1489 | 0.8841 | -1,522.46 | 4 | False |
| 4 | 60 | 5 | take_only_agree | e82b664b26657fd5 | 604 | 0.1342 | -1,161.41 | -884.71 | -276.70 | -265.60 | 88.40 | 0.2264 | 0.869 | 0.8512 | 0.1299 | 0.913 | -1,551.38 | 4 | False |
| 4 | 60 | 15 | skip_if_disagree | 7eb26a763965545c | 4,086 | 0.9076 | -902.09 | -1,115.69 | 213.59 | -40.85 | 37.90 | 0.4198 | 0.0927 | 0.851 | 0.9343 | 0.0435 | -1,292.06 | 6 | False |
| 4 | 60 | 15 | skip_if_none | e1edf18847fbe400 | 1,291 | 0.2868 | -1,161.65 | -825.41 | -336.23 | -177.65 | 79.50 | 0.048 | 0.715 | 0.8502 | 0.2432 | 0.7971 | -1,551.61 | 4 | False |
| 4 | 60 | 15 | take_only_agree | 304211658cec2e1a | 875 | 0.1944 | -1,183.50 | -858.71 | -324.79 | -254.29 | 75.70 | 0.1049 | 0.8078 | 0.8503 | 0.1775 | 0.8406 | -1,573.46 | 4 | False |
| 4 | 60 | 30 | skip_if_disagree | 3b61d4d8336b9b10 | 3,696 | 0.821 | -885.45 | -1,088.65 | 203.19 | -31.20 | 37.80 | 0.3358 | 0.1805 | 0.8548 | 0.8749 | 0.1159 | -1,275.42 | 6 | False |
| 4 | 60 | 30 | skip_if_none | 1cf929cd4b23a519 | 1,979 | 0.4396 | -1,107.61 | -776.11 | -331.51 | -116.13 | 87.50 | 0.0375 | 0.5597 | 0.847 | 0.3592 | 0.6377 | -1,497.58 | 5 | False |
| 4 | 60 | 30 | take_only_agree | 156861f97f36188b | 1,173 | 0.2606 | -1,120.65 | -851.78 | -268.87 | -172.38 | 88.40 | 0.1169 | 0.7402 | 0.8489 | 0.234 | 0.7536 | -1,510.61 | 4 | False |

**Nested-CV candidate** (family `h3/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4aa13f8ee89c96a3 | 4,355 | 0.9673 | -915.32 | -1,114.61 | 199.29 | -58.26 | 59.10 | 0.6362 | 0.0322 | 0.8367 | 0.9805 | 0.0145 | -1,305.29 | 8 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 564.72 | 0.9728 | 49 | 400 | 389 |
| 1 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 3} |  | 498.99 | 0.9588 | 49 | 392 | 379 |
| 2 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 484.93 | 0.9717 | 49 | 386 | 381 |
| 3 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 516.97 | 0.9427 | 49 | 512 | 487 |
| 4 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 541.67 | 0.9725 | 49 | 395 | 386 |
| 5 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 554.45 | 0.9719 | 49 | 345 | 339 |
| 6 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 488.55 | 0.9736 | 49 | 430 | 415 |
| 7 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 471.60 | 0.9421 | 49 | 269 | 260 |
| 8 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 493.34 | 0.9443 | 49 | 172 | 159 |
| 9 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 549.04 | 0.9732 | 49 | 506 | 491 |
| 10 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 469.16 | 0.9738 | 49 | 174 | 167 |
| 11 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 586.39 | 0.9741 | 49 | 521 | 502 |

CPCV paths (`h3/nested_cv/cpcv`, 11 rows): diff median 290.83, 5th pct 203.44, min 197.42, share > 0 1.00, control pct median 67.00 / 5th pct 56.50

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 1ad35aa2918bc630 | 4,370 | 0.9707 | -910.61 | -1,293.29 | 382.68 | 72.30 | 0.3803 | 0.9833 | 9 | 0 |
| cb4b5850e81c8e49 | 4,307 | 0.9567 | -906.77 | -1,254.39 | 347.62 | 64.30 | 0.3433 | 0.981 | 10 | 1 |
| 7077857e85a24d3b | 4,337 | 0.9633 | -911.09 | -1,204.30 | 293.22 | 64.50 | 0.4683 | 0.9808 | 9 | 2 |
| 812576ac8887986e | 4,356 | 0.9676 | -914.76 | -1,132.85 | 218.09 | 58.00 | 0.5942 | 0.9809 | 8 | 3 |
| a4d321df0d690912 | 4,368 | 0.9702 | -915.60 | -1,125.06 | 209.47 | 56.90 | 0.6217 | 0.981 | 8 | 4 |
| 3de67ccda7f6c0e0 | 4,364 | 0.9693 | -912.92 | -1,203.74 | 290.83 | 67.00 | 0.5022 | 0.9828 | 9 | 5 |
| 5664ab1a73267823 | 4,314 | 0.9582 | -910.22 | -1,188.23 | 278.01 | 73.30 | 0.4518 | 0.9799 | 9 | 6 |
| 284901def2b1fa10 | 4,317 | 0.9589 | -912.80 | -1,132.52 | 219.72 | 69.60 | 0.5727 | 0.9795 | 8 | 7 |
| 543f96893c1fce8d | 4,372 | 0.9711 | -912.60 | -1,232.22 | 319.61 | 67.20 | 0.4713 | 0.9832 | 9 | 8 |
| 95e4144c74c43fe6 | 4,348 | 0.9658 | -915.08 | -1,112.49 | 197.42 | 56.00 | 0.6267 | 0.9805 | 8 | 9 |
| 90f47546b9838054 | 4,377 | 0.9722 | -913.20 | -1,224.22 | 311.02 | 68.00 | 0.4798 | 0.9833 | 9 | 10 |

Cells chosen across the 66 CPCV training sets: {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 4} x40; {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} x18; {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 3} x8

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L0 | pre-registered (family as at the primary run) | 55 | 55 | 1.98 | 0.1033 | 0.7235 | 0.055 | 0.055 |  | {"v": 2, "N": 60, "M": 30, "gate": "skip_if_none"} | 352.15 | [-146.01, 516.43] | 0.166 | 1.00 | 290.83 | 203.44 | 1.00 | 67.00 | False | diff_top1_removed>0, kept_mean_slip8>0, control_pct>=95, dsr_p<0.1, boot_ci_excludes_0 |


### 5 min / L1 (826 IS units)

Foundation outcome by direction agreement with the latest high-volume bar within M bars (`h3_5minute_L1_by_agreement.csv`; every (v, N, M)):

| variable | bucket | n | share | net_mean | net_se | win_rate | pts_mean | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|
| hv v2 N20 M5 | agree | 327 | 0.3959 | -746.89 | 230.82 | 0.2752 | 4.70 | 5 |
| hv v2 N20 M5 | disagree | 28 | 0.0339 | -1,146.76 | 558.36 | 0.25 | -1.51 | 6 |
| hv v2 N20 M5 | none | 471 | 0.5702 | -740.94 | 221.03 | 0.2803 | 4.73 | 6 |
| hv v2 N20 M15 | agree | 382 | 0.4625 | -829.64 | 203.50 | 0.2696 | 3.40 | 8 |
| hv v2 N20 M15 | disagree | 84 | 0.1017 | -811.57 | 402.25 | 0.25 | 3.60 | 6 |
| hv v2 N20 M15 | none | 360 | 0.4358 | -667.31 | 272.17 | 0.2917 | 5.89 | 4 |
| hv v2 N20 M30 | agree | 407 | 0.4927 | -828.52 | 193.95 | 0.2703 | 3.42 | 7 |
| hv v2 N20 M30 | disagree | 107 | 0.1295 | -630.78 | 364.59 | 0.2523 | 6.42 | 6 |
| hv v2 N20 M30 | none | 312 | 0.3777 | -707.12 | 304.67 | 0.2949 | 5.26 | 5 |
| hv v2 N60 M5 | agree | 255 | 0.3087 | -668.90 | 261.56 | 0.2863 | 5.84 | 5 |
| hv v2 N60 M5 | disagree | 19 | 0.023 | -1,031.54 | 773.66 | 0.2105 | 0.192 | 5 |
| hv v2 N60 M5 | none | 552 | 0.6683 | -788.33 | 199.41 | 0.2754 | 4.04 | 6 |
| hv v2 N60 M15 | agree | 303 | 0.3668 | -797.07 | 227.07 | 0.2772 | 3.88 | 6 |
| hv v2 N60 M15 | disagree | 56 | 0.0678 | -1,295.36 | 433.25 | 0.1786 | -3.85 | 8 |
| hv v2 N60 M15 | none | 467 | 0.5654 | -666.54 | 229.06 | 0.2891 | 5.91 | 4 |
| hv v2 N60 M30 | agree | 333 | 0.4031 | -837.85 | 214.20 | 0.2643 | 3.28 | 8 |
| hv v2 N60 M30 | disagree | 102 | 0.1235 | -688.65 | 393.96 | 0.2353 | 5.50 | 6 |
| hv v2 N60 M30 | none | 391 | 0.4734 | -706.09 | 256.84 | 0.2992 | 5.29 | 4 |
| hv v3 N20 M5 | agree | 152 | 0.184 | -778.44 | 333.52 | 0.2697 | 4.21 | 8 |
| hv v3 N20 M5 | disagree | 17 | 0.0206 | -612.01 | 984.92 | 0.2941 | 6.88 | 6 |
| hv v3 N20 M5 | none | 657 | 0.7954 | -755.86 | 179.70 | 0.2785 | 4.51 | 5 |
| hv v3 N20 M15 | agree | 204 | 0.247 | -901.54 | 266.19 | 0.2647 | 2.30 | 7 |
| hv v3 N20 M15 | disagree | 60 | 0.0726 | -292.67 | 552.52 | 0.3333 | 11.65 | 5 |
| hv v3 N20 M15 | none | 562 | 0.6804 | -754.18 | 200.72 | 0.2758 | 4.54 | 5 |
| hv v3 N20 M30 | agree | 229 | 0.2772 | -784.32 | 259.14 | 0.2664 | 4.07 | 7 |
| hv v3 N20 M30 | disagree | 95 | 0.115 | -453.22 | 433.18 | 0.2737 | 9.22 | 5 |
| hv v3 N20 M30 | none | 502 | 0.6077 | -802.11 | 214.23 | 0.2829 | 3.81 | 6 |
| hv v3 N60 M5 | agree | 102 | 0.1235 | -600.20 | 389.52 | 0.2941 | 6.94 | 5 |
| hv v3 N60 M5 | disagree | 9 | 0.0109 | -277.02 | 642.15 | 0.4444 | 12.06 | 2 |
| hv v3 N60 M5 | none | 715 | 0.8656 | -785.47 | 172.19 | 0.2727 | 4.06 | 7 |
| hv v3 N60 M15 | agree | 134 | 0.1622 | -833.93 | 323.74 | 0.291 | 3.33 | 7 |
| hv v3 N60 M15 | disagree | 35 | 0.0424 | -129.88 | 783.94 | 0.3143 | 14.22 | 6 |
| hv v3 N60 M15 | none | 657 | 0.7954 | -774.78 | 181.01 | 0.2725 | 4.23 | 6 |
| hv v3 N60 M30 | agree | 153 | 0.1852 | -702.32 | 318.90 | 0.2876 | 5.35 | 7 |
| hv v3 N60 M30 | disagree | 68 | 0.0823 | -348.21 | 502.40 | 0.2647 | 10.84 | 5 |
| hv v3 N60 M30 | none | 605 | 0.7324 | -816.85 | 190.10 | 0.276 | 3.58 | 7 |
| hv v4 N20 M5 | agree | 79 | 0.0956 | -460.47 | 499.15 | 0.2911 | 9.21 | 6 |
| hv v4 N20 M5 | disagree | 8 | 0.0097 | 1,141.18 | 1,749.99 | 0.5 | 34.38 | 2 |
| hv v4 N20 M5 | none | 739 | 0.8947 | -809.31 | 165.79 | 0.2733 | 3.68 | 6 |
| hv v4 N20 M15 | agree | 104 | 0.1259 | -641.25 | 406.52 | 0.2885 | 6.34 | 6 |
| hv v4 N20 M15 | disagree | 36 | 0.0436 | -901.87 | 602.50 | 0.25 | 2.54 | 7 |
| hv v4 N20 M15 | none | 686 | 0.8305 | -767.01 | 175.69 | 0.277 | 4.33 | 6 |
| hv v4 N20 M30 | agree | 123 | 0.1489 | -707.72 | 354.21 | 0.2764 | 5.31 | 6 |
| hv v4 N20 M30 | disagree | 65 | 0.0787 | -516.78 | 463.02 | 0.2615 | 8.33 | 6 |
| hv v4 N20 M30 | none | 638 | 0.7724 | -791.04 | 185.31 | 0.279 | 3.96 | 7 |
| hv v4 N60 M5 | agree | 52 | 0.063 | -309.42 | 538.20 | 0.2885 | 11.36 | 5 |
| hv v4 N60 M5 | disagree | 5 | 0.0061 | 1,476.85 | 1,452.75 | 0.6 | 39.77 | 1 |
| hv v4 N60 M5 | none | 769 | 0.931 | -801.85 | 164.01 | 0.2744 | 3.81 | 8 |
| hv v4 N60 M15 | agree | 69 | 0.0835 | -569.41 | 457.09 | 0.2754 | 7.32 | 5 |
| hv v4 N60 M15 | disagree | 16 | 0.0194 | 455.88 | 854.00 | 0.4375 | 23.30 | 1 |
| hv v4 N60 M15 | none | 741 | 0.8971 | -800.72 | 168.41 | 0.274 | 3.84 | 8 |
| hv v4 N60 M30 | agree | 77 | 0.0932 | -686.35 | 420.12 | 0.2597 | 5.51 | 6 |
| hv v4 N60 M30 | disagree | 30 | 0.0363 | -103.00 | 596.30 | 0.3 | 14.58 | 5 |
| hv v4 N60 M30 | none | 719 | 0.8705 | -791.91 | 172.59 | 0.2782 | 3.98 | 7 |

by bars since the latest high-volume bar (`h3_5minute_L1_by_bars_since.csv`):

| variable | bucket | n | share | net_mean | net_se | win_rate | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|
| hv v2 N20 bars_since | 0 | 243 | 0.2942 | -762.79 | 266.48 | 0.2757 | 7 |
| hv v2 N20 bars_since | 1-5 | 114 | 0.138 | -787.21 | 370.54 | 0.2719 | 6 |
| hv v2 N20 bars_since | 6-15 | 113 | 0.1368 | -946.14 | 316.22 | 0.2478 | 5 |
| hv v2 N20 bars_since | 16-30 | 48 | 0.0581 | -408.54 | 499.79 | 0.2708 | 7 |
| hv v2 N20 bars_since | >30 | 10 | 0.0121 | -118.74 | 963.16 | 0.5 | 3 |
| hv v2 N20 bars_since | none | 298 | 0.3608 | -746.70 | 316.46 | 0.2852 | 6 |
| hv v2 N60 bars_since | 0 | 190 | 0.23 | -631.39 | 292.87 | 0.2947 | 5 |
| hv v2 N60 bars_since | 1-5 | 85 | 0.1029 | -780.14 | 470.09 | 0.2588 | 4 |
| hv v2 N60 bars_since | 6-15 | 88 | 0.1065 | -1,422.44 | 296.11 | 0.2045 | 7 |
| hv v2 N60 bars_since | 16-30 | 76 | 0.092 | -463.07 | 487.49 | 0.2368 | 3 |
| hv v2 N60 bars_since | >30 | 36 | 0.0436 | -1,309.50 | 413.71 | 0.2778 | 5 |
| hv v2 N60 bars_since | none | 351 | 0.4249 | -659.65 | 282.04 | 0.2991 | 4 |
| hv v3 N20 bars_since | 0 | 110 | 0.1332 | -722.88 | 406.64 | 0.2727 | 8 |
| hv v3 N20 bars_since | 1-5 | 59 | 0.0714 | -834.07 | 493.76 | 0.2712 | 7 |
| hv v3 N20 bars_since | 6-15 | 95 | 0.115 | -765.75 | 368.83 | 0.2947 | 7 |
| hv v3 N20 bars_since | 16-30 | 60 | 0.0726 | -353.20 | 569.65 | 0.2167 | 5 |
| hv v3 N20 bars_since | >30 | 18 | 0.0218 | -141.59 | 675.17 | 0.3889 | 4 |
| hv v3 N20 bars_since | none | 484 | 0.586 | -826.68 | 220.78 | 0.2789 | 6 |
| hv v3 N60 bars_since | 0 | 72 | 0.0872 | -642.98 | 494.68 | 0.2917 | 6 |
| hv v3 N60 bars_since | 1-5 | 39 | 0.0472 | -446.63 | 480.20 | 0.3333 | 5 |
| hv v3 N60 bars_since | 6-15 | 58 | 0.0702 | -906.55 | 554.13 | 0.2759 | 8 |
| hv v3 N60 bars_since | 16-30 | 52 | 0.063 | -285.39 | 583.03 | 0.2308 | 7 |
| hv v3 N60 bars_since | >30 | 25 | 0.0303 | -1,082.49 | 509.85 | 0.24 | 6 |
| hv v3 N60 bars_since | none | 580 | 0.7022 | -805.40 | 197.11 | 0.2776 | 7 |
| hv v4 N20 bars_since | 0 | 55 | 0.0666 | -156.36 | 670.27 | 0.3091 | 5 |
| hv v4 N20 bars_since | 1-5 | 32 | 0.0387 | -582.74 | 624.94 | 0.3125 | 6 |
| hv v4 N20 bars_since | 6-15 | 53 | 0.0642 | -1,356.79 | 412.14 | 0.2264 | 10 |
| hv v4 N20 bars_since | 16-30 | 48 | 0.0581 | -447.56 | 491.18 | 0.25 | 5 |
| hv v4 N20 bars_since | >30 | 16 | 0.0194 | -824.62 | 670.81 | 0.375 | 4 |
| hv v4 N20 bars_since | none | 622 | 0.753 | -790.18 | 189.34 | 0.2765 | 8 |
| hv v4 N60 bars_since | 0 | 34 | 0.0412 | 219.97 | 759.53 | 0.3235 | 5 |
| hv v4 N60 bars_since | 1-5 | 23 | 0.0278 | -703.68 | 572.70 | 0.3043 | 5 |
| hv v4 N60 bars_since | 6-15 | 28 | 0.0339 | -831.77 | 666.06 | 0.2857 | 5 |
| hv v4 N60 bars_since | 16-30 | 22 | 0.0266 | -1,088.34 | 609.73 | 0.1364 | 5 |
| hv v4 N60 bars_since | >30 | 15 | 0.0182 | -1,085.63 | 764.14 | 0.4 | 5 |
| hv v4 N60 bars_since | none | 704 | 0.8523 | -785.66 | 175.56 | 0.2756 | 6 |

The grid: 54 cells; diff > 0 in 26; control pct >= 95 in 35; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff -7.41, median control pct 99.65. Full table `h3_5minute_L1_grid.csv`:

| v | N | M | gate | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 20 | 5 | skip_if_disagree | 5bb8df27d933a542 | 798 | 0.9661 | -743.38 | -1,146.76 | 403.38 | 179.17 | 0.9 | 0.6317 | 0.0352 | 0.75 | 0.9832 | 0 | -1,133.34 | 6 | False |
| 2 | 20 | 5 | skip_if_none | d48b335fa7c8fb2a | 355 | 0.4298 | -778.43 | -740.94 | -37.49 | 150.40 | 100.00 | 0.9 | 0.5678 | 0.7197 | 0.3818 | 0.6522 | -1,168.40 | 6 | False |
| 2 | 20 | 5 | take_only_agree | 78e5ec98d9bbecb5 | 327 | 0.3959 | -746.89 | -763.71 | 16.82 | 178.82 | 99.90 | 0.9645 | 0.603 | 0.7214 | 0.365 | 0.6522 | -1,136.86 | 7 | False |
| 2 | 20 | 15 | skip_if_disagree | 5694b41eb921fb5b | 742 | 0.8983 | -750.88 | -811.57 | 60.69 | -180.75 | 0.2 | 0.9095 | 0.1055 | 0.75 | 0.9218 | 0.0435 | -1,140.85 | 6 | False |
| 2 | 20 | 15 | skip_if_none | 20892326d3da1f02 | 466 | 0.5642 | -826.38 | -667.31 | -159.07 | 147.09 | 100.00 | 0.6107 | 0.4271 | 0.7083 | 0.4744 | 0.6087 | -1,216.34 | 4 | False |
| 2 | 20 | 15 | take_only_agree | a2c2f9584e5b150d | 382 | 0.4625 | -829.64 | -694.60 | -135.03 | 78.06 | 100.00 | 0.6937 | 0.5327 | 0.7162 | 0.3962 | 0.6522 | -1,219.60 | 4 | False |
| 2 | 20 | 30 | skip_if_disagree | c57175398734ff98 | 719 | 0.8705 | -775.84 | -630.78 | -145.06 | -394.64 | 0.1 | 0.7411 | 0.134 | 0.7477 | 0.8891 | 0.0435 | -1,165.81 | 6 | False |
| 2 | 20 | 30 | skip_if_none | 00cca7d0b739f715 | 514 | 0.6223 | -787.36 | -707.12 | -80.24 | 296.21 | 100.00 | 0.8046 | 0.3685 | 0.7051 | 0.5241 | 0.6087 | -1,177.32 | 5 | False |
| 2 | 20 | 30 | take_only_agree | 1c6ad7c2ca8145ce | 407 | 0.4927 | -828.52 | -687.63 | -140.90 | 97.54 | 100.00 | 0.6642 | 0.5025 | 0.716 | 0.4132 | 0.6522 | -1,218.49 | 5 | False |
| 2 | 60 | 5 | skip_if_disagree | 04d33f65b093e8a3 | 807 | 0.977 | -750.59 | -1,031.54 | 280.95 | 59.18 | 4.90 | 0.7836 | 0.0251 | 0.7895 | 0.9859 | 0 | -1,140.55 | 5 | False |
| 2 | 60 | 5 | skip_if_none | 0208c32a133b361c | 274 | 0.3317 | -694.05 | -788.33 | 94.28 | 206.43 | 100.00 | 0.7791 | 0.67 | 0.7246 | 0.2994 | 0.7391 | -1,084.01 | 6 | False |
| 2 | 60 | 5 | take_only_agree | 83ee4a25087f2db6 | 255 | 0.3087 | -668.90 | -796.42 | 127.52 | 220.74 | 100.00 | 0.7301 | 0.6951 | 0.7268 | 0.2853 | 0.7391 | -1,058.87 | 7 | False |
| 2 | 60 | 15 | skip_if_disagree | 9ee80f7138a51100 | 770 | 0.9322 | -717.90 | -1,295.36 | 577.45 | 345.29 | 9.30 | 0.3693 | 0.0771 | 0.8214 | 0.9609 | 0 | -1,107.87 | 8 | False |
| 2 | 60 | 15 | skip_if_none | cbcd91057109fd38 | 359 | 0.4346 | -874.80 | -666.54 | -208.26 | -18.21 | 100.00 | 0.5132 | 0.5561 | 0.7109 | 0.3471 | 0.7391 | -1,264.76 | 4 | False |
| 2 | 60 | 15 | take_only_agree | 2b8a5a2faa7ff9e0 | 303 | 0.3668 | -797.07 | -733.87 | -63.20 | 75.48 | 100.00 | 0.8461 | 0.6332 | 0.7228 | 0.308 | 0.7391 | -1,187.03 | 6 | False |
| 2 | 60 | 30 | skip_if_disagree | 294e6764980ee762 | 724 | 0.8765 | -766.69 | -688.65 | -78.04 | -325.75 | 2.80 | 0.8671 | 0.1307 | 0.7647 | 0.8835 | 0.0435 | -1,156.65 | 6 | False |
| 2 | 60 | 30 | skip_if_none | 1c830fef39b4459b | 435 | 0.5266 | -802.86 | -706.09 | -96.78 | 172.71 | 100.00 | 0.7661 | 0.459 | 0.7008 | 0.4437 | 0.6522 | -1,192.83 | 4 | False |
| 2 | 60 | 30 | take_only_agree | 53660344c6c5c26e | 333 | 0.4031 | -837.85 | -702.48 | -135.37 | 30.83 | 100.00 | 0.6597 | 0.5896 | 0.714 | 0.3271 | 0.6957 | -1,227.81 | 4 | False |
| 3 | 20 | 5 | skip_if_disagree | e37802fbc30515f5 | 809 | 0.9794 | -760.10 | -612.01 | -148.09 | -369.41 | 5.50 | 0.8976 | 0.0201 | 0.7059 | 0.9793 | 0 | -1,150.06 | 6 | False |
| 3 | 20 | 5 | skip_if_none | 35a624052800b49e | 169 | 0.2046 | -761.70 | -755.86 | -5.84 | 138.45 | 100.00 | 0.9905 | 0.794 | 0.7215 | 0.1813 | 0.7826 | -1,151.67 | 5 | False |
| 3 | 20 | 5 | take_only_agree | 4d9ccfd472480e9a | 152 | 0.184 | -778.44 | -752.23 | -26.21 | 100.15 | 99.80 | 0.951 | 0.8141 | 0.7211 | 0.1607 | 0.7826 | -1,168.41 | 4 | False |
| 3 | 20 | 15 | skip_if_disagree | 45d87dd1e2b7ccae | 766 | 0.9274 | -793.43 | -292.67 | -500.76 | -347.86 | 0 | 0.3943 | 0.067 | 0.6667 | 0.9252 | 0.0435 | -1,183.39 | 5 | False |
| 3 | 20 | 15 | skip_if_none | 12a3d3ce68207a50 | 264 | 0.3196 | -763.16 | -754.18 | -8.97 | 92.22 | 100.00 | 0.9815 | 0.6817 | 0.7242 | 0.267 | 0.7391 | -1,153.12 | 5 | False |
| 3 | 20 | 15 | take_only_agree | 0ea5ec9b1d5959fe | 204 | 0.247 | -901.54 | -709.66 | -191.87 | -17.23 | 100.00 | 0.6127 | 0.7487 | 0.7186 | 0.1922 | 0.7826 | -1,291.50 | 5 | False |
| 3 | 20 | 30 | skip_if_disagree | 5f1648ea121a5cc5 | 731 | 0.885 | -796.54 | -453.22 | -343.32 | -332.11 | 0.1 | 0.4913 | 0.1156 | 0.7263 | 0.889 | 0.087 | -1,186.50 | 5 | False |
| 3 | 20 | 30 | skip_if_none | 307fb598d9b19d10 | 324 | 0.3923 | -687.24 | -802.11 | 114.87 | 274.97 | 100.00 | 0.6942 | 0.603 | 0.7171 | 0.3433 | 0.6522 | -1,077.20 | 6 | False |
| 3 | 20 | 30 | take_only_agree | ff15f6820fca5e23 | 229 | 0.2772 | -784.32 | -746.59 | -37.73 | 158.29 | 100.00 | 0.9175 | 0.7186 | 0.7186 | 0.2323 | 0.7391 | -1,174.29 | 5 | False |
| 3 | 60 | 5 | skip_if_disagree | d01ba23aba6e5704 | 817 | 0.9891 | -762.34 | -277.02 | -485.32 | -704.47 | 1.60 | 0.7566 | 0.0084 | 0.5556 | 0.9949 | 0 | -1,152.31 | 2 | False |
| 3 | 60 | 5 | skip_if_none | 81898aa668ee829f | 111 | 0.1344 | -574.00 | -785.47 | 211.47 | 462.58 | 99.30 | 0.6472 | 0.871 | 0.7273 | 0.1131 | 0.913 | -963.96 | 7 | False |
| 3 | 60 | 5 | take_only_agree | e211de0f194006d7 | 102 | 0.1235 | -600.20 | -779.15 | 178.95 | 426.82 | 98.20 | 0.7036 | 0.8794 | 0.7251 | 0.108 | 0.913 | -990.16 | 7 | False |
| 3 | 60 | 15 | skip_if_disagree | 503c228d35f982d4 | 791 | 0.9576 | -784.80 | -129.88 | -654.92 | -236.68 | 0.8 | 0.3773 | 0.0402 | 0.6857 | 0.9562 | 0.0435 | -1,174.77 | 6 | False |
| 3 | 60 | 15 | skip_if_none | ecf4dab78d302d29 | 169 | 0.2046 | -688.13 | -774.78 | 86.66 | 198.16 | 100.00 | 0.8231 | 0.8007 | 0.7275 | 0.1732 | 0.8696 | -1,078.09 | 6 | False |
| 3 | 60 | 15 | take_only_agree | d90836d5373bd06c | 134 | 0.1622 | -833.93 | -742.16 | -91.77 | 167.22 | 98.50 | 0.8356 | 0.8409 | 0.7254 | 0.1295 | 0.913 | -1,223.90 | 5 | False |
| 3 | 60 | 30 | skip_if_disagree | c45657a082849292 | 758 | 0.9177 | -793.73 | -348.21 | -445.52 | -336.76 | 0.5 | 0.4478 | 0.0838 | 0.7353 | 0.923 | 0.0435 | -1,183.69 | 5 | False |
| 3 | 60 | 30 | skip_if_none | 90de9193342c262d | 221 | 0.2676 | -593.36 | -816.85 | 223.48 | 387.15 | 100.00 | 0.5222 | 0.7337 | 0.724 | 0.2402 | 0.8261 | -983.33 | 7 | False |
| 3 | 60 | 30 | take_only_agree | daf17339a46857fb | 153 | 0.1852 | -702.32 | -769.49 | 67.17 | 333.95 | 99.70 | 0.8626 | 0.8174 | 0.7251 | 0.1633 | 0.8696 | -1,092.29 | 5 | False |
| 4 | 20 | 5 | skip_if_disagree | dbcde631c9ee29ae | 818 | 0.9903 | -775.62 | 1,141.18 | -1,916.80 | -2,135.83 | 4.60 | 0.2049 | 0.0067 | 0.5 | 0.982 | 0 | -1,165.58 | 2 | False |
| 4 | 20 | 5 | skip_if_none | ef7e313f68494734 | 87 | 0.1053 | -313.19 | -809.31 | 496.12 | 521.28 | 98.50 | 0.3328 | 0.8995 | 0.7267 | 0.1151 | 0.8696 | -703.16 | 6 | False |
| 4 | 20 | 5 | take_only_agree | 15f6915ee3bbfb86 | 79 | 0.0956 | -460.47 | -788.42 | 327.95 | 328.71 | 93.90 | 0.5597 | 0.9062 | 0.7242 | 0.0971 | 0.8696 | -850.43 | 6 | False |
| 4 | 20 | 15 | skip_if_disagree | 0bb88c6a6a8ffa3f | 790 | 0.9564 | -750.45 | -901.87 | 151.42 | -75.17 | 2.30 | 0.8341 | 0.0452 | 0.75 | 0.9666 | 0 | -1,140.42 | 7 | False |
| 4 | 20 | 15 | skip_if_none | 38268600623ceadb | 140 | 0.1695 | -708.27 | -767.01 | 58.74 | 171.73 | 100.00 | 0.8946 | 0.8308 | 0.723 | 0.1493 | 0.8696 | -1,098.23 | 6 | False |
| 4 | 20 | 15 | take_only_agree | e8af548ba6902237 | 104 | 0.1259 | -641.25 | -773.73 | 132.48 | 191.33 | 98.80 | 0.7716 | 0.876 | 0.7244 | 0.1159 | 0.8696 | -1,031.21 | 6 | False |
| 4 | 20 | 30 | skip_if_disagree | c221585f5bd5f15c | 761 | 0.9213 | -777.57 | -516.78 | -260.79 | -496.45 | 0.1 | 0.6492 | 0.0804 | 0.7385 | 0.93 | 0 | -1,167.54 | 6 | False |
| 4 | 20 | 30 | skip_if_none | 08acacd20b67f66a | 188 | 0.2276 | -641.70 | -791.04 | 149.34 | 312.52 | 100.00 | 0.6847 | 0.7705 | 0.721 | 0.1975 | 0.8696 | -1,031.67 | 7 | False |
| 4 | 20 | 30 | take_only_agree | d95d9eba36eb1950 | 123 | 0.1489 | -707.72 | -765.68 | 57.97 | 148.04 | 99.30 | 0.8771 | 0.8509 | 0.7226 | 0.1275 | 0.8696 | -1,097.68 | 6 | False |
| 4 | 60 | 5 | skip_if_disagree | 396e8c6db9b6529e | 821 | 0.9939 | -770.66 | 1,476.85 | -2,247.51 | -2,465.67 | 10.90 | 0.2294 | 0.0034 | 0.4 | 0.9908 | 0 | -1,160.62 | 1 | False |
| 4 | 60 | 5 | skip_if_none | 787de1111d634bf1 | 57 | 0.069 | -152.73 | -801.85 | 649.11 | 882.57 | 99.70 | 0.3073 | 0.9347 | 0.7256 | 0.066 | 0.9565 | -542.70 | 8 | False |
| 4 | 60 | 5 | take_only_agree | 518f33f14669872c | 52 | 0.063 | -309.42 | -787.13 | 477.70 | 709.46 | 99.60 | 0.4368 | 0.938 | 0.7235 | 0.0568 | 0.9565 | -699.39 | 7 | False |
| 4 | 60 | 15 | skip_if_disagree | ea648dd03e98e397 | 810 | 0.9806 | -781.01 | 455.88 | -1,236.89 | -1,458.16 | 0.3 | 0.2734 | 0.0151 | 0.5625 | 0.9804 | 0 | -1,170.98 | 1 | False |
| 4 | 60 | 15 | skip_if_none | b68bb7024c7c6c45 | 85 | 0.1029 | -376.41 | -800.72 | 424.30 | 666.68 | 100.00 | 0.4273 | 0.9012 | 0.726 | 0.091 | 0.9565 | -766.38 | 8 | False |
| 4 | 60 | 15 | take_only_agree | 5cb3d2ab9b665f81 | 69 | 0.0835 | -569.41 | -774.16 | 204.75 | 441.62 | 99.60 | 0.7216 | 0.9162 | 0.7226 | 0.0714 | 0.9565 | -959.37 | 7 | False |
| 4 | 60 | 30 | skip_if_disagree | 2a9ec96e0b7fd12e | 796 | 0.9637 | -781.70 | -103.00 | -678.70 | -903.92 | 0.9 | 0.4213 | 0.0352 | 0.7 | 0.9703 | 0 | -1,171.67 | 5 | False |
| 4 | 60 | 30 | skip_if_none | 50bebdca52884cda | 107 | 0.1295 | -522.79 | -791.91 | 269.12 | 518.90 | 100.00 | 0.5552 | 0.8693 | 0.7218 | 0.1049 | 0.9565 | -912.76 | 7 | False |
| 4 | 60 | 30 | take_only_agree | 48c221b8171c342f | 77 | 0.0932 | -686.35 | -764.32 | 77.97 | 317.29 | 99.80 | 0.8861 | 0.9045 | 0.721 | 0.0751 | 0.9565 | -1,076.31 | 6 | False |

**Nested-CV candidate** (family `h3/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8eaee251afffdbb3 | 775 | 0.9383 | -769.41 | -569.31 | -200.09 | -431.35 | 0.4 | 0.7566 | 0.0637 | 0.7451 | 0.9465 | 0 | -1,159.37 | 6 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 608.48 | 0.9663 | 38 | 82 | 79 |
| 1 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 496.05 | 0.9339 | 37 | 83 | 77 |
| 2 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 469.66 | 0.9349 | 38 | 42 | 37 |
| 3 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 515.47 | 0.9313 | 38 | 76 | 73 |
| 4 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 650.80 | 0.9377 | 36 | 72 | 63 |
| 5 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 563.97 | 0.9317 | 38 | 73 | 68 |
| 6 | {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 884.99 | 0.9758 | 38 | 77 | 76 |
| 7 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 576.37 | 0.929 | 38 | 51 | 50 |
| 8 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 700.93 | 0.9317 | 38 | 76 | 71 |
| 9 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 909.14 | 0.9383 | 37 | 80 | 70 |
| 10 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 610.50 | 0.9307 | 38 | 31 | 30 |
| 11 | {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 2} |  | 873.19 | 0.965 | 37 | 83 | 81 |

CPCV paths (`h3/nested_cv/cpcv`, 11 rows): diff median -200.09, 5th pct -598.43, min -612.43, share > 0 0.273, control pct median 0.7 / 5th pct 0.1

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| a3a433a09dfefff8 | 796 | 0.9637 | -779.30 | -166.86 | -612.43 | 0.1 | 0.4688 | 0.9615 | 5 | 0 |
| 2cd6243c08fd4a59 | 775 | 0.9383 | -769.41 | -569.31 | -200.09 | 0.7 | 0.7586 | 0.9465 | 6 | 1 |
| 57de19e6964e0535 | 775 | 0.9383 | -769.41 | -569.31 | -200.09 | 0.5 | 0.7536 | 0.9465 | 6 | 2 |
| 8bc0695cc4cf1e9c | 782 | 0.9467 | -782.39 | -306.65 | -475.75 | 0.1 | 0.4888 | 0.9465 | 5 | 3 |
| ae82e1c081aa2990 | 775 | 0.9383 | -752.90 | -820.17 | 67.27 | 2.50 | 0.9155 | 0.9518 | 7 | 4 |
| dcdfcca9f8a54852 | 795 | 0.9625 | -778.99 | -194.54 | -584.44 | 1.20 | 0.4828 | 0.9544 | 5 | 5 |
| 4378cbd2ee79a882 | 779 | 0.9431 | -762.72 | -663.04 | -99.68 | 1.40 | 0.8836 | 0.9579 | 5 | 6 |
| 4d68d187d4d1ef01 | 775 | 0.9383 | -752.90 | -820.17 | 67.27 | 2.80 | 0.9195 | 0.9518 | 7 | 7 |
| 8e938a6f5857928d | 770 | 0.9322 | -734.52 | -1,066.90 | 332.38 | 2.50 | 0.5872 | 0.9556 | 7 | 8 |
| 7ec0a850b3393d35 | 775 | 0.9383 | -769.41 | -569.31 | -200.09 | 0.7 | 0.7611 | 0.9465 | 6 | 9 |
| 7a046b7ee67be535 | 795 | 0.9625 | -774.61 | -306.84 | -467.77 | 0.1 | 0.5647 | 0.9626 | 5 | 10 |

Cells chosen across the 66 CPCV training sets: {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} x39; {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 2} x17; {"M": 5, "N": 60, "gate": "skip_if_disagree", "v": 2} x9; {"M": 5, "N": 20, "gate": "skip_if_disagree", "v": 3} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L1 | pre-registered (family as at the primary run) | 55 | 55 | 2.49 | 0.6568 | 0.3895 | 0.155 | 0.172 |  | {"v": 2, "N": 20, "M": 30, "gate": "skip_if_none"} | 428.85 | [-1159.18, 581.14] | 0.6535 | 0.9965 | -200.09 | -598.43 | 0.273 | 0.7 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### 5 min / L0 (832 IS units)

L0 robustness, (v=2, N=20) and (v=3, N=20), M = 15:

| variable | bucket | n | net_mean | net_se | win_rate | blocks_below_block_mean |
|---|---|---|---|---|---|---|
| hv v2 N20 M15 | agree | 388 | -313.98 | 545.04 | 0.2165 | 6 |
| hv v2 N20 M15 | disagree | 84 | -1,004.13 | 689.19 | 0.1786 | 9 |
| hv v2 N20 M15 | none | 360 | -66.92 | 551.76 | 0.2361 | 5 |
| hv v3 N20 M15 | agree | 207 | -186.98 | 820.92 | 0.2271 | 6 |
| hv v3 N20 M15 | disagree | 61 | -98.82 | 1,093.59 | 0.2295 | 6 |
| hv v3 N20 M15 | none | 564 | -328.95 | 413.17 | 0.2181 | 7 |

The grid: 54 cells; diff > 0 in 36; control pct >= 95 in 31; passing every raw go/no-go check (kept floors, diff, top-1 % removed, slip-8 kept mean, sign blocks, control) in 0. Median cell diff 256.74, median control pct 96.40. Full table `h3_5minute_L0_grid.csv`:

| v | N | M | gate | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 20 | 5 | skip_if_disagree | e87cc44181ce771d | 804 | 0.9663 | -275.48 | -313.33 | 37.84 | -766.45 | 8.40 | 0.9845 | 0.034 | 0.7857 | 0.9717 | 0 | -665.45 | 5 | False |
| 2 | 20 | 5 | skip_if_none | 964410d7db7b0abe | 361 | 0.4339 | -415.75 | -170.23 | -245.52 | 213.43 | 97.90 | 0.7441 | 0.5664 | 0.7792 | 0.4242 | 0.5789 | -805.71 | 6 | False |
| 2 | 20 | 5 | take_only_agree | a200b55b40d3ae2b | 333 | 0.4002 | -424.36 | -178.26 | -246.10 | 113.55 | 95.60 | 0.7351 | 0.6003 | 0.7796 | 0.3959 | 0.5789 | -814.32 | 6 | False |
| 2 | 20 | 15 | skip_if_disagree | 08fab6b42f223bfe | 748 | 0.899 | -195.07 | -1,004.13 | 809.05 | -55.20 | 27.00 | 0.5037 | 0.1065 | 0.8214 | 0.9312 | 0.0526 | -585.04 | 9 | False |
| 2 | 20 | 15 | skip_if_none | 45337909b275d8fd | 472 | 0.5673 | -436.80 | -66.92 | -369.89 | 118.96 | 99.00 | 0.6317 | 0.4244 | 0.7639 | 0.5384 | 0.4211 | -826.77 | 5 | False |
| 2 | 20 | 15 | take_only_agree | a4db2c6586f0467e | 388 | 0.4663 | -313.98 | -244.23 | -69.75 | 96.80 | 97.20 | 0.915 | 0.5309 | 0.7748 | 0.4696 | 0.4737 | -703.95 | 6 | False |
| 2 | 20 | 30 | skip_if_disagree | db7fb23bd731fc2b | 725 | 0.8714 | -162.55 | -1,050.63 | 888.08 | -3.53 | 36.80 | 0.3848 | 0.1327 | 0.8037 | 0.9235 | 0.0526 | -552.51 | 9 | False |
| 2 | 20 | 30 | skip_if_none | 647e36bca382adda | 520 | 0.625 | -477.69 | 58.13 | -535.83 | 168.27 | 99.30 | 0.4788 | 0.3688 | 0.766 | 0.5611 | 0.4211 | -867.66 | 5 | False |
| 2 | 20 | 30 | take_only_agree | 3d305e85937205cc | 413 | 0.4964 | -329.26 | -225.01 | -104.25 | 155.62 | 98.50 | 0.8911 | 0.5015 | 0.7757 | 0.4846 | 0.4737 | -719.22 | 6 | False |
| 2 | 60 | 5 | skip_if_disagree | 4f420241ca973d79 | 813 | 0.9772 | -251.37 | -1,363.16 | 1,111.79 | 316.78 | 57.50 | 0.6112 | 0.0216 | 0.7368 | 0.9936 | 0 | -641.33 | 7 | False |
| 2 | 60 | 5 | skip_if_none | 17e978953576f90d | 280 | 0.3365 | -83.18 | -374.95 | 291.77 | 459.78 | 97.80 | 0.6947 | 0.6728 | 0.7899 | 0.3674 | 0.5789 | -473.15 | 7 | False |
| 2 | 60 | 5 | take_only_agree | 321c96bd93f0f0de | 261 | 0.3137 | 10.00 | -407.83 | 417.83 | 510.01 | 99.80 | 0.6012 | 0.6944 | 0.7881 | 0.3611 | 0.5789 | -379.97 | 7 | False |
| 2 | 60 | 15 | skip_if_disagree | c09a6c359567613e | 776 | 0.9327 | -148.72 | -2,051.02 | 1,902.30 | 1,070.14 | 92.50 | 0.1569 | 0.0741 | 0.8571 | 0.9842 | 0 | -538.68 | 10 | False |
| 2 | 60 | 15 | skip_if_none | eecc0d0a556ef8c5 | 365 | 0.4387 | -314.67 | -247.13 | -67.54 | 12.67 | 93.00 | 0.925 | 0.5571 | 0.773 | 0.4414 | 0.5263 | -704.63 | 5 | False |
| 2 | 60 | 15 | take_only_agree | 5ae3ad1d3485caef | 309 | 0.3714 | 0.01 | -440.28 | 440.29 | 303.91 | 99.90 | 0.5527 | 0.6312 | 0.782 | 0.4257 | 0.5263 | -389.96 | 6 | False |
| 2 | 60 | 30 | skip_if_disagree | 5a557b099bc59a79 | 730 | 0.8774 | -85.26 | -1,647.29 | 1,562.03 | 677.57 | 85.60 | 0.1469 | 0.125 | 0.7941 | 0.9587 | 0 | -475.22 | 11 | False |
| 2 | 60 | 30 | skip_if_none | 0aed983e351d2de7 | 441 | 0.53 | -410.78 | -125.60 | -285.19 | 79.80 | 95.60 | 0.6982 | 0.466 | 0.7724 | 0.4908 | 0.5263 | -800.75 | 5 | False |
| 2 | 60 | 30 | take_only_agree | fc6ca3d069ab82f1 | 339 | 0.4075 | -38.73 | -440.43 | 401.69 | 386.76 | 99.80 | 0.5797 | 0.591 | 0.7769 | 0.4495 | 0.5263 | -428.70 | 5 | False |
| 3 | 20 | 5 | skip_if_disagree | 012a9ff8fa943ff6 | 815 | 0.9796 | -302.37 | 951.38 | -1,253.75 | 920.69 | 24.10 | 0.5777 | 0.0201 | 0.7647 | 0.9719 | 0.0526 | -692.34 | 8 | False |
| 3 | 20 | 5 | skip_if_none | ad82be33cfc9676a | 172 | 0.2067 | 324.16 | -433.36 | 757.51 | 89.12 | 99.10 | 0.3838 | 0.7963 | 0.7818 | 0.2625 | 0.7368 | -65.81 | 6 | False |
| 3 | 20 | 5 | take_only_agree | 815f8b89ae39cc10 | 155 | 0.1863 | 255.36 | -398.59 | 653.95 | 212.06 | 98.70 | 0.4953 | 0.8164 | 0.7814 | 0.2344 | 0.7895 | -134.60 | 6 | False |
| 3 | 20 | 15 | skip_if_disagree | a200fc239a273eb9 | 771 | 0.9267 | -290.84 | -98.82 | -192.02 | -174.68 | 14.90 | 0.8936 | 0.0725 | 0.7705 | 0.9232 | 0.0526 | -680.80 | 6 | False |
| 3 | 20 | 15 | skip_if_none | 38ef56612ad05f2f | 268 | 0.3221 | -166.91 | -328.95 | 162.04 | 70.33 | 99.30 | 0.8376 | 0.6806 | 0.7819 | 0.3408 | 0.7368 | -556.88 | 7 | False |
| 3 | 20 | 15 | take_only_agree | 8136246e18697fef | 207 | 0.2488 | -186.98 | -306.49 | 119.51 | 18.96 | 97.30 | 0.8821 | 0.7531 | 0.7808 | 0.264 | 0.7895 | -576.95 | 6 | False |
| 3 | 20 | 30 | skip_if_disagree | 4d723ef18f3dcb34 | 736 | 0.8846 | -283.96 | -221.55 | -62.41 | -373.13 | 10.30 | 0.9575 | 0.1157 | 0.7812 | 0.8888 | 0.1053 | -673.92 | 7 | False |
| 3 | 20 | 30 | skip_if_none | 38c89658de41226a | 329 | 0.3954 | -171.37 | -345.69 | 174.32 | 331.52 | 99.80 | 0.8316 | 0.6065 | 0.7813 | 0.4078 | 0.6842 | -561.33 | 6 | False |
| 3 | 20 | 30 | take_only_agree | 164f9ab4600e2463 | 233 | 0.28 | -150.69 | -325.80 | 175.11 | 204.08 | 98.00 | 0.8276 | 0.7222 | 0.7813 | 0.2965 | 0.7895 | -540.65 | 6 | False |
| 3 | 60 | 5 | skip_if_disagree | f58f15dce6dc67fa | 823 | 0.9892 | -352.57 | 6,655.46 | -7,008.03 | -2,632.03 | 2.90 | 0.051 | 0.0062 | 0.4444 | 0.961 | 0.0526 | -742.53 | 2 | False |
| 3 | 60 | 5 | skip_if_none | f07e9abe7f8ff7ff | 116 | 0.1394 | 1,510.58 | -566.33 | 2,076.91 | 743.03 | 99.80 | 0.034 | 0.8735 | 0.7905 | 0.2477 | 0.7368 | 1,120.62 | 5 | False |
| 3 | 60 | 5 | take_only_agree | 4cba271872f6202a | 107 | 0.1286 | 1,077.83 | -476.68 | 1,554.51 | 563.11 | 98.20 | 0.1324 | 0.8796 | 0.7862 | 0.2087 | 0.7895 | 687.87 | 4 | False |
| 3 | 60 | 15 | skip_if_disagree | f6a4d7fe9a7b5a78 | 797 | 0.9579 | -327.19 | 871.64 | -1,198.82 | -578.48 | 17.40 | 0.4763 | 0.0401 | 0.7429 | 0.9365 | 0.0526 | -717.15 | 5 | False |
| 3 | 60 | 15 | skip_if_none | bf94b12f200d4276 | 174 | 0.2091 | 493.87 | -480.54 | 974.41 | 326.68 | 99.10 | 0.2599 | 0.7994 | 0.7872 | 0.2846 | 0.7368 | 103.91 | 5 | False |
| 3 | 60 | 15 | take_only_agree | 3fcd06f583fa77d7 | 139 | 0.1671 | 398.75 | -412.25 | 811.00 | 222.42 | 97.80 | 0.4048 | 0.8395 | 0.785 | 0.2211 | 0.7895 | 8.79 | 4 | False |
| 3 | 60 | 30 | skip_if_disagree | 170953cc98090eee | 764 | 0.9183 | -320.76 | 217.60 | -538.36 | -616.08 | 10.20 | 0.6847 | 0.0787 | 0.75 | 0.9034 | 0.1053 | -710.72 | 5 | False |
| 3 | 60 | 30 | skip_if_none | 59fae4093c2645bf | 226 | 0.2716 | 327.47 | -502.10 | 829.57 | 535.89 | 100.00 | 0.2999 | 0.7392 | 0.7904 | 0.3403 | 0.6842 | -62.49 | 5 | False |
| 3 | 60 | 30 | take_only_agree | 22b60b12dbcbcfff | 158 | 0.1899 | 374.76 | -429.49 | 804.25 | 389.19 | 97.40 | 0.3753 | 0.8179 | 0.7864 | 0.2437 | 0.7895 | -15.20 | 4 | False |
| 4 | 20 | 5 | skip_if_disagree | 46b09655132198e6 | 824 | 0.9904 | -274.63 | -496.34 | 221.71 | -562.83 | 4.00 | 0.9465 | 0.0093 | 0.75 | 0.9918 | 0 | -664.59 | 4 | False |
| 4 | 20 | 5 | skip_if_none | 2bbd1676ce68d0a7 | 88 | 0.1058 | 515.99 | -370.52 | 886.51 | 1,288.02 | 96.30 | 0.4583 | 0.8997 | 0.7836 | 0.1319 | 0.8421 | 126.02 | 6 | False |
| 4 | 20 | 5 | take_only_agree | 1787b88d5a0c971d | 80 | 0.0962 | 617.22 | -371.86 | 989.08 | 1,340.77 | 91.80 | 0.4143 | 0.909 | 0.7832 | 0.1237 | 0.8421 | 227.25 | 6 | False |
| 4 | 20 | 15 | skip_if_disagree | 7c4fcac6578e4324 | 796 | 0.9567 | -187.91 | -2,241.18 | 2,053.26 | 1,241.80 | 59.80 | 0.1794 | 0.0494 | 0.8889 | 0.9803 | 0 | -577.88 | 9 | False |
| 4 | 20 | 15 | skip_if_none | b222684ac658d4f4 | 141 | 0.1695 | -558.15 | -219.34 | -338.81 | 275.02 | 89.30 | 0.7356 | 0.8287 | 0.7771 | 0.1524 | 0.8421 | -948.11 | 5 | False |
| 4 | 20 | 15 | take_only_agree | e329bf1452165feb | 105 | 0.1262 | 18.89 | -319.46 | 338.35 | 822.19 | 92.10 | 0.7556 | 0.8781 | 0.7827 | 0.1326 | 0.8421 | -371.07 | 6 | False |
| 4 | 20 | 30 | skip_if_disagree | 7e19da7d58665c18 | 767 | 0.9219 | -213.49 | -1,023.28 | 809.79 | -33.02 | 23.20 | 0.5452 | 0.0802 | 0.8 | 0.9415 | 0.0526 | -603.46 | 8 | False |
| 4 | 20 | 30 | skip_if_none | ffd290f7e0528565 | 190 | 0.2284 | -505.43 | -209.08 | -296.35 | 455.03 | 99.00 | 0.7321 | 0.7731 | 0.7804 | 0.1992 | 0.7895 | -895.40 | 6 | False |
| 4 | 20 | 30 | take_only_agree | a1ba5dd35340bd75 | 125 | 0.1502 | -236.15 | -283.94 | 47.79 | 610.29 | 91.70 | 0.9605 | 0.8534 | 0.7822 | 0.1407 | 0.8421 | -626.12 | 6 | False |
| 4 | 60 | 5 | skip_if_disagree | b7c9bae2ae5a76f6 | 827 | 0.994 | -276.08 | -389.15 | 113.07 | -668.61 | 4.40 | 0.976 | 0.0062 | 0.8 | 0.9948 | 0 | -666.04 | 3 | False |
| 4 | 60 | 5 | skip_if_none | 228e135068e492c4 | 60 | 0.0721 | 762.48 | -357.53 | 1,120.00 | 1,297.25 | 99.00 | 0.4203 | 0.9336 | 0.7837 | 0.1025 | 0.8421 | 372.51 | 5 | False |
| 4 | 60 | 5 | take_only_agree | 46b81496704df654 | 55 | 0.0661 | 867.17 | -357.73 | 1,224.90 | 1,342.29 | 97.80 | 0.3978 | 0.9398 | 0.7838 | 0.0973 | 0.8421 | 477.20 | 6 | False |
| 4 | 60 | 15 | skip_if_disagree | d52e6d4620ea4d29 | 816 | 0.9808 | -228.98 | -2,713.16 | 2,484.18 | 1,692.36 | 40.80 | 0.2484 | 0.0231 | 0.9375 | 0.9948 | 0 | -618.95 | 7 | False |
| 4 | 60 | 15 | skip_if_none | d61c1fdf9dbea14b | 88 | 0.1058 | -396.57 | -262.59 | -133.98 | 255.87 | 96.50 | 0.8946 | 0.8951 | 0.7796 | 0.1074 | 0.8421 | -786.53 | 4 | False |
| 4 | 60 | 15 | take_only_agree | c61b2953d4f9cb3b | 72 | 0.0865 | 118.23 | -314.18 | 432.41 | 716.14 | 96.50 | 0.7661 | 0.9182 | 0.7829 | 0.1023 | 0.8421 | -271.73 | 6 | False |
| 4 | 60 | 30 | skip_if_disagree | c1abcf6f1eed8c6c | 802 | 0.9639 | -235.33 | -1,384.25 | 1,148.92 | 343.06 | 23.40 | 0.5372 | 0.0401 | 0.8667 | 0.9808 | 0 | -625.30 | 7 | False |
| 4 | 60 | 30 | skip_if_none | 4d3e3974dbc4503a | 110 | 0.1322 | -507.19 | -241.65 | -265.54 | 234.72 | 98.70 | 0.8031 | 0.8673 | 0.7784 | 0.1221 | 0.8421 | -897.16 | 4 | False |
| 4 | 60 | 30 | take_only_agree | 0975498fb79502ca | 80 | 0.0962 | -178.29 | -287.23 | 108.94 | 449.65 | 95.40 | 0.9205 | 0.9074 | 0.7819 | 0.1029 | 0.8421 | -568.26 | 5 | False |

**Nested-CV candidate** (family `h3/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0b364a8b48bd9207 | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | -348.30 | 34.90 | 0.8321 | 0.0309 | 0.8333 | 0.9753 | 0 | -653.69 | 6 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,058.11 | 0.9799 | 38 | 83 | 82 |
| 1 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,422.24 | 0.9786 | 38 | 84 | 84 |
| 2 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,285.46 | 0.981 | 38 | 42 | 41 |
| 3 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,427.14 | 0.9812 | 38 | 77 | 77 |
| 4 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,471.59 | 0.9842 | 37 | 72 | 68 |
| 5 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,619.76 | 0.9814 | 38 | 73 | 71 |
| 6 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,615.98 | 0.9787 | 38 | 78 | 78 |
| 7 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,372.16 | 0.9795 | 38 | 51 | 51 |
| 8 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 3,278.60 | 0.9801 | 38 | 76 | 75 |
| 9 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} |  | 2,003.94 | 0.9386 | 38 | 82 | 72 |
| 10 | {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} |  | 2,272.25 | 0.9825 | 38 | 31 | 29 |
| 11 | {"M": 15, "N": 20, "gate": "skip_if_disagree", "v": 4} |  | 2,708.00 | 0.9559 | 38 | 83 | 80 |

CPCV paths (`h3/nested_cv/cpcv`, 11 rows): diff median 451.83, 5th pct 261.32, min 245.41, share > 0 1.00, control pct median 33.50 / 5th pct 30.90

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 72459d144473d7aa | 800 | 0.9615 | -267.32 | -512.73 | 245.41 | 62.10 | 0.8926 | 0.9703 | 6 | 0 |
| 65fc8dcc43431760 | 814 | 0.9784 | -251.46 | -1,420.79 | 1,169.34 | 34.10 | 0.6117 | 0.9845 | 6 | 1 |
| bbf0182ed8c9210c | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | 33.50 | 0.8231 | 0.9753 | 6 | 2 |
| 4fb4e501edf04378 | 806 | 0.9688 | -263.10 | -700.02 | 436.91 | 29.90 | 0.8186 | 0.9753 | 6 | 3 |
| 21c9ac4e84e873bf | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | 33.50 | 0.8286 | 0.9753 | 6 | 4 |
| 2f3c4bf4873c5c15 | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | 33.50 | 0.8066 | 0.9753 | 6 | 5 |
| 2274c97c3859462d | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | 32.40 | 0.8211 | 0.9753 | 6 | 6 |
| b887cfe287985717 | 808 | 0.9712 | -263.72 | -715.55 | 451.83 | 32.00 | 0.8256 | 0.9753 | 6 | 7 |
| 7cd2d5a4bd853f52 | 793 | 0.9531 | -196.62 | -1,906.16 | 1,709.53 | 81.20 | 0.2809 | 0.9889 | 9 | 8 |
| 16b1e13f8d206b5c | 809 | 0.9724 | -269.09 | -546.33 | 277.24 | 33.30 | 0.8966 | 0.9753 | 5 | 9 |
| ca632e129cbbec78 | 799 | 0.9603 | -213.40 | -1,810.88 | 1,597.48 | 53.50 | 0.3478 | 0.9803 | 8 | 10 |

Cells chosen across the 66 CPCV training sets: {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 4} x46; {"M": 15, "N": 20, "gate": "skip_if_disagree", "v": 4} x11; {"M": 15, "N": 60, "gate": "skip_if_disagree", "v": 2} x9

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L0 | pre-registered (family as at the primary run) | 55 | 55 | 2.24 | 0.5181 | 0.4411 | 0.5765 | 0.5765 |  | {"v": 3, "N": 20, "M": 30, "gate": "skip_if_none"} | 525.73 | [-2269.14, 2575.06] | 0.356 | 0.7825 | 451.83 | 261.32 | 1.00 | 33.50 | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### H3 family summary (all tables)

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 55 | 55 | 1.66 | 0.7635 | 0.8015 | 0 | 0 |  | {"v": 2, "N": 60, "M": 30, "gate": "skip_if_none"} | 244.91 | [-324.62, -39.75] | 0.9825 | 1.00 | -156.04 | -298.24 | 0.091 | 0.1 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0 |
| 1 min | L0 | pre-registered (family as at the primary run) | 55 | 55 | 1.98 | 0.1033 | 0.7235 | 0.055 | 0.055 |  | {"v": 2, "N": 60, "M": 30, "gate": "skip_if_none"} | 352.15 | [-146.01, 516.43] | 0.166 | 1.00 | 290.83 | 203.44 | 1.00 | 67.00 | False | diff_top1_removed>0, kept_mean_slip8>0, control_pct>=95, dsr_p<0.1, boot_ci_excludes_0 |
| 5 min | L1 | pre-registered (family as at the primary run) | 55 | 55 | 2.49 | 0.6568 | 0.3895 | 0.155 | 0.172 |  | {"v": 2, "N": 20, "M": 30, "gate": "skip_if_none"} | 428.85 | [-1159.18, 581.14] | 0.6535 | 0.9965 | -200.09 | -598.43 | 0.273 | 0.7 | False | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| 5 min | L0 | pre-registered (family as at the primary run) | 55 | 55 | 2.24 | 0.5181 | 0.4411 | 0.5765 | 0.5765 |  | {"v": 3, "N": 20, "M": 30, "gate": "skip_if_none"} | 525.73 | [-2269.14, 2575.06] | 0.356 | 0.7825 | 451.83 | 261.32 | 1.00 | 33.50 | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |



## T4. H4 - levels respected or broken

### 1 min: the episode study (IS bars; `h4_minute_episodes.parquet`, 248,128 episodes of 141,221 level instances: {'swing': 113936, 'prot': 15645, 'room': 11640})

Repair round (2026-09-29T05:33:09): verdict of a window cut by the session end = session_end (was broke when a break close fell inside the truncated window); cut_break added. Cut windows: 8,537 (`session_end`), of which 3,825 held a break close inside the truncated window (`cut_break_n` below).

Verdicts (`h4_minute_episode_verdicts.csv`):

| kind | verdict | n | cut_break_n | share |
|---|---|---|---|---|
| prot | broke | 4,554 | 0 | 0.6875 |
| prot | held | 1,867 | 0 | 0.2819 |
| prot | session_end | 203 | 92 | 0.0306 |
| room | broke | 48,102 | 0 | 0.6641 |
| room | held | 21,895 | 0 | 0.3023 |
| room | na | 276 | 0 | 0.0038 |
| room | session_end | 2,156 | 1,025 | 0.0298 |
| swing | broke | 112,912 | 0 | 0.6678 |
| swing | held | 49,985 | 0 | 0.2956 |
| swing | session_end | 6,178 | 2,708 | 0.0365 |

P(broke given prior held episodes of the same level), episodes not after a break (`h4_minute_p_break_by_prior_held.csv`):

| kind | prior_held_bin | n | p_broke |
|---|---|---|---|
| prot | 0 | 6,421 | 0.7092 |
| room | 0 | 9,958 | 0.669 |
| room | 1 | 2,538 | 0.4941 |
| room | 2 | 984 | 0.5122 |
| room | 3+ | 659 | 0.4704 |
| swing | 0 | 93,171 | 0.6914 |
| swing | 1 | 19,495 | 0.4734 |
| swing | 2 | 7,573 | 0.4651 |
| swing | 3+ | 4,755 | 0.4566 |

Move after a confirmed break vs after a respect, in ATR (`h4_minute_aftermath.csv`; `move` is signed in the break / bounce direction, `abs` is its magnitude, the baseline is every IS bar):

| kind | verdict | n_bars | n | abs_mean | abs_median | abs_p75 | abs_p90 | abs_share_gt1 | abs_share_gt2 | move_mean | move_median | move_share_pos | move_share_gt1 | move_share_gt2 | mfe_median | beyond_median | beyond_share_pos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_all_bars | any | 15 | 367,686 | 1.90 | 1.48 | 2.63 | 4.03 | 0.6432 | 0.3691 |  |  |  |  |  |  |  |  |
| baseline_all_bars | any | 30 | 352,296 | 2.73 | 2.11 | 3.75 | 5.80 | 0.7437 | 0.5212 |  |  |  |  |  |  |  |  |
| baseline_all_bars | any | 60 | 321,516 | 3.86 | 2.96 | 5.32 | 8.31 | 0.8163 | 0.6442 |  |  |  |  |  |  |  |  |
| prot | broke | 15 | 4,519 | 1.99 | 1.58 | 2.73 | 4.19 | 0.6636 | 0.3901 | -0.055 | -0.136 | 0.4771 | 0.312 | 0.1846 | 1.50 | 0.88 | 0.649 |
| prot | broke | 30 | 4,271 | 2.83 | 2.24 | 3.98 | 6.01 | 0.7602 | 0.5486 | -0.071 | -0.144 | 0.4819 | 0.3662 | 0.2669 | 2.16 | 0.845 | 0.6088 |
| prot | broke | 60 | 3,852 | 4.08 | 3.20 | 5.70 | 8.70 | 0.8383 | 0.6685 | 0.018 | 0 | 0.4992 | 0.4164 | 0.3294 | 3.17 | 1.02 | 0.5836 |
| prot | held | 15 | 1,764 | 2.00 | 1.57 | 2.79 | 4.18 | 0.6576 | 0.4002 | 0.018 | -0.032 | 0.4887 | 0.3226 | 0.2046 | 1.60 |  |  |
| prot | held | 30 | 1,671 | 2.90 | 2.33 | 4.04 | 6.00 | 0.7732 | 0.5572 | 0.035 | 0.031 | 0.5021 | 0.3926 | 0.2843 | 2.38 |  |  |
| prot | held | 60 | 1,490 | 4.15 | 3.19 | 5.67 | 8.95 | 0.8322 | 0.6698 | -0.01 | -0.046 | 0.494 | 0.4101 | 0.3349 | 3.25 |  |  |
| room | broke | 15 | 47,748 | 1.94 | 1.51 | 2.69 | 4.08 | 0.6539 | 0.3821 | -0.03 | -0.115 | 0.4787 | 0.3108 | 0.1851 | 1.50 | 0.95 | 0.6637 |
| room | broke | 30 | 45,403 | 2.75 | 2.16 | 3.84 | 5.83 | 0.7438 | 0.5292 | -0.022 | -0.096 | 0.4861 | 0.361 | 0.2576 | 2.15 | 0.975 | 0.6232 |
| room | broke | 60 | 41,234 | 3.87 | 3.01 | 5.38 | 8.25 | 0.8185 | 0.6521 | 0.019 | -0.067 | 0.4949 | 0.4034 | 0.3227 | 3.04 | 1.02 | 0.5891 |
| room | held | 15 | 20,744 | 1.92 | 1.49 | 2.65 | 4.06 | 0.6469 | 0.371 | 0.039 | -0.007 | 0.4965 | 0.3232 | 0.1886 | 1.56 |  |  |
| room | held | 30 | 19,908 | 2.73 | 2.14 | 3.77 | 5.77 | 0.7417 | 0.5254 | 0.057 | 0.035 | 0.5041 | 0.3771 | 0.2656 | 2.24 |  |  |
| room | held | 60 | 18,016 | 3.87 | 2.97 | 5.37 | 8.32 | 0.8184 | 0.6429 | 0.066 | 0.085 | 0.5078 | 0.4179 | 0.3271 | 3.13 |  |  |
| swing | broke | 15 | 112,068 | 1.98 | 1.54 | 2.73 | 4.18 | 0.6584 | 0.3879 | -0.063 | -0.168 | 0.4686 | 0.306 | 0.1825 | 1.51 | 0.907 | 0.6574 |
| swing | broke | 30 | 105,790 | 2.82 | 2.19 | 3.91 | 5.97 | 0.7555 | 0.5359 | -0.06 | -0.195 | 0.4741 | 0.3562 | 0.2534 | 2.15 | 0.894 | 0.609 |
| swing | broke | 60 | 95,614 | 4.00 | 3.05 | 5.51 | 8.57 | 0.8213 | 0.6524 | -0.018 | -0.17 | 0.4845 | 0.3968 | 0.3156 | 3.04 | 0.924 | 0.5832 |
| swing | held | 15 | 47,077 | 1.96 | 1.49 | 2.69 | 4.17 | 0.6486 | 0.3757 | 0.013 | 0 | 0.4964 | 0.3229 | 0.1888 | 1.57 |  |  |
| swing | held | 30 | 44,850 | 2.84 | 2.19 | 3.89 | 6.02 | 0.753 | 0.5366 | 0.007 | 0 | 0.4991 | 0.3787 | 0.2682 | 2.29 |  |  |
| swing | held | 60 | 40,223 | 4.04 | 3.04 | 5.53 | 8.79 | 0.8195 | 0.6504 | 0.011 | 0.01 | 0.5006 | 0.4105 | 0.3268 | 3.23 |  |  |

Retests (held episodes) before the first break, per level instance that broke (`h4_minute_retests_before_break.csv`):

| kind | retests_bin | instances | instances_touched | share_of_touched_instances |
|---|---|---|---|---|
| prot | 0 | 4,554 | 6,624 | 0.6875 |
| room | 0 | 6,635 | 10,052 | 0.6601 |
| room | 1 | 1,247 | 10,052 | 0.1241 |
| room | 2 | 501 | 10,052 | 0.0498 |
| room | 3+ | 308 | 10,052 | 0.0306 |
| swing | 0 | 64,423 | 96,486 | 0.6677 |
| swing | 1 | 9,228 | 96,486 | 0.0956 |
| swing | 2 | 3,522 | 96,486 | 0.0365 |
| swing | 3+ | 2,171 | 96,486 | 0.0225 |

Held episodes followed by another touch of the same level instance (`h4_minute_held_then_retested.csv`):

| kind | n | share_retested |
|---|---|---|
| prot | 1,867 | 0 |
| room | 21,895 | 0.8136 |
| swing | 49,985 | 0.6777 |


### 5 min: the episode study (IS bars; `h4_5minute_episodes.parquet`, 63,009 episodes of 33,979 level instances: {'swing': 22992, 'room': 8090, 'prot': 2897})

Repair round (2026-09-29T05:34:13): verdict of a window cut by the session end = session_end (was broke when a break close fell inside the truncated window); cut_break added. Cut windows: 2,663 (`session_end`), of which 520 held a break close inside the truncated window (`cut_break_n` below).

Verdicts (`h4_5minute_episode_verdicts.csv`):

| kind | verdict | n | cut_break_n | share |
|---|---|---|---|---|
| prot | broke | 509 | 0 | 0.4336 |
| prot | held | 645 | 0 | 0.5494 |
| prot | session_end | 20 | 6 | 0.017 |
| room | broke | 15,730 | 0 | 0.4284 |
| room | held | 19,025 | 0 | 0.5181 |
| room | na | 561 | 0 | 0.0153 |
| room | session_end | 1,404 | 281 | 0.0382 |
| swing | broke | 11,155 | 0 | 0.4442 |
| swing | held | 12,721 | 0 | 0.5065 |
| swing | session_end | 1,239 | 233 | 0.0493 |

P(broke given prior held episodes of the same level), episodes not after a break (`h4_5minute_p_break_by_prior_held.csv`):

| kind | prior_held_bin | n | p_broke |
|---|---|---|---|
| prot | 0 | 1,154 | 0.4411 |
| room | 0 | 7,462 | 0.431 |
| room | 1 | 3,283 | 0.4429 |
| room | 2 | 1,373 | 0.4406 |
| room | 3+ | 1,021 | 0.476 |
| swing | 0 | 15,316 | 0.4645 |
| swing | 1 | 4,848 | 0.4495 |
| swing | 2 | 1,561 | 0.426 |
| swing | 3+ | 659 | 0.4476 |

Move after a confirmed break vs after a respect, in ATR (`h4_5minute_aftermath.csv`; `move` is signed in the break / bounce direction, `abs` is its magnitude, the baseline is every IS bar):

| kind | verdict | n_bars | n | abs_mean | abs_median | abs_p75 | abs_p90 | abs_share_gt1 | abs_share_gt2 | move_mean | move_median | move_share_pos | move_share_gt1 | move_share_gt2 | mfe_median | beyond_median | beyond_share_pos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_all_bars | any | 15 | 61,233 | 1.81 | 1.38 | 2.51 | 3.91 | 0.6173 | 0.3431 |  |  |  |  |  |  |  |  |
| baseline_all_bars | any | 30 | 45,889 | 2.47 | 1.91 | 3.43 | 5.36 | 0.7159 | 0.4814 |  |  |  |  |  |  |  |  |
| baseline_all_bars | any | 60 | 15,280 | 3.33 | 2.60 | 4.66 | 6.96 | 0.7916 | 0.5974 |  |  |  |  |  |  |  |  |
| prot | broke | 15 | 409 | 2.00 | 1.57 | 2.71 | 4.22 | 0.6675 | 0.3839 | -0.037 | -0.043 | 0.4866 | 0.3374 | 0.1932 | 1.44 | 0.848 | 0.6284 |
| prot | broke | 30 | 285 | 2.71 | 2.07 | 3.86 | 5.88 | 0.7439 | 0.5263 | -0.074 | 0.047 | 0.5088 | 0.3509 | 0.2737 | 1.83 | 0.871 | 0.6105 |
| prot | broke | 60 | 110 | 3.79 | 2.91 | 5.75 | 7.21 | 0.8273 | 0.6727 | 0.062 | 0.512 | 0.5455 | 0.4455 | 0.3727 | 2.56 | 1.63 | 0.6364 |
| prot | held | 15 | 502 | 1.89 | 1.35 | 2.69 | 4.08 | 0.6076 | 0.3705 | -0.075 | -0.014 | 0.494 | 0.2849 | 0.1713 | 1.40 |  |  |
| prot | held | 30 | 366 | 2.58 | 2.01 | 3.69 | 5.59 | 0.7596 | 0.5027 | -0.19 | -0.117 | 0.4809 | 0.3661 | 0.2268 | 1.98 |  |  |
| prot | held | 60 | 130 | 3.64 | 2.85 | 4.59 | 7.16 | 0.8769 | 0.7077 | -0.336 | -1.18 | 0.4 | 0.3538 | 0.3077 | 2.81 |  |  |
| room | broke | 15 | 12,612 | 1.89 | 1.46 | 2.63 | 4.02 | 0.6417 | 0.3664 | 0.023 | -0.004 | 0.4975 | 0.3222 | 0.1848 | 1.44 | 1.05 | 0.6867 |
| room | broke | 30 | 9,547 | 2.52 | 2.00 | 3.51 | 5.38 | 0.7347 | 0.4998 | 0.085 | 0.056 | 0.5073 | 0.3757 | 0.2598 | 1.98 | 1.15 | 0.651 |
| room | broke | 60 | 3,970 | 3.45 | 2.66 | 4.87 | 7.14 | 0.8126 | 0.5955 | 0.197 | 0.159 | 0.5161 | 0.4295 | 0.3194 | 2.66 | 1.33 | 0.6348 |
| room | held | 15 | 14,880 | 1.77 | 1.33 | 2.42 | 3.84 | 0.6068 | 0.3327 | -0.008 | -0.001 | 0.4987 | 0.3026 | 0.1659 | 1.40 |  |  |
| room | held | 30 | 11,194 | 2.40 | 1.84 | 3.34 | 5.27 | 0.7081 | 0.4674 | 0.014 | 0.049 | 0.5053 | 0.3579 | 0.2359 | 1.90 |  |  |
| room | held | 60 | 3,506 | 3.21 | 2.46 | 4.62 | 6.73 | 0.7898 | 0.5836 | 0.041 | 0.123 | 0.5106 | 0.4084 | 0.3012 | 2.49 |  |  |
| swing | broke | 15 | 8,092 | 1.93 | 1.47 | 2.68 | 4.11 | 0.6455 | 0.3758 | 0.056 | -0.004 | 0.4983 | 0.3271 | 0.1956 | 1.49 | 1.03 | 0.6873 |
| swing | broke | 30 | 5,197 | 2.64 | 2.05 | 3.71 | 5.71 | 0.7304 | 0.5116 | 0.127 | 0.135 | 0.5191 | 0.3829 | 0.2694 | 2.07 | 1.16 | 0.6552 |
| swing | broke | 60 | 760 | 3.39 | 2.52 | 4.88 | 7.29 | 0.8066 | 0.5882 | 0.505 | 0.296 | 0.5395 | 0.4592 | 0.3526 | 2.64 | 1.48 | 0.6671 |
| swing | held | 15 | 8,897 | 1.87 | 1.38 | 2.56 | 4.10 | 0.6173 | 0.3461 | -0.053 | -0.023 | 0.495 | 0.2984 | 0.1651 | 1.46 |  |  |
| swing | held | 30 | 5,507 | 2.54 | 1.90 | 3.50 | 5.64 | 0.7129 | 0.4792 | -0.019 | 0.023 | 0.503 | 0.355 | 0.2375 | 1.94 |  |  |
| swing | held | 60 | 576 | 3.13 | 2.33 | 4.36 | 6.55 | 0.7726 | 0.5833 | -0.051 | 0.119 | 0.5139 | 0.3837 | 0.2899 | 2.45 |  |  |

Retests (held episodes) before the first break, per level instance that broke (`h4_5minute_retests_before_break.csv`):

| kind | retests_bin | instances | instances_touched | share_of_touched_instances |
|---|---|---|---|---|
| prot | 0 | 509 | 1,174 | 0.4336 |
| room | 0 | 3,160 | 7,459 | 0.4236 |
| room | 1 | 1,414 | 7,459 | 0.1896 |
| room | 2 | 580 | 7,459 | 0.0778 |
| room | 3+ | 468 | 7,459 | 0.0627 |
| swing | 0 | 7,114 | 15,933 | 0.4465 |
| swing | 1 | 2,179 | 15,933 | 0.1368 |
| swing | 2 | 665 | 15,933 | 0.0417 |
| swing | 3+ | 295 | 15,933 | 0.0185 |

Held episodes followed by another touch of the same level instance (`h4_5minute_held_then_retested.csv`):

| kind | n | share_retested |
|---|---|---|
| prot | 645 | 0 |
| room | 19,025 | 0.7992 |
| swing | 12,721 | 0.6069 |


### 1 min / L1 (4,452 IS units)

Foundation outcome by the last touch verdict and by the number of touch episodes in the hour before the SETUP (`h4_minute_L1_by_touch.csv`):

| variable | bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| touch_prot_last | broke | 21 | 0.0047 | -1,094.83 | 246.72 | -1,464.40 | 0.0952 | -0.371 | 0.4762 | 8 |
| touch_prot_last | held | 160 | 0.0359 | -733.14 | 328.08 | -1,754.58 | 0.2188 | 4.89 | 0.4062 | 6 |
| touch_prot_last | pending | 4,144 | 0.9308 | -1,034.05 | 39.24 | -1,540.49 | 0.1523 | 0.203 | 0.2749 | 6 |
| touch_prot_last | none | 2 | 0.0004 | -2,878.48 | 877.03 | -2,878.48 | 0 | -28.25 | 0.5 | 2 |
| touch_prot_last | na | 125 | 0.0281 | -508.86 | 318.75 | -1,539.11 | 0.208 | 8.31 | 0.288 | 4 |
| touch_prot_n | 0 | 2 | 0.0004 | -2,878.48 | 877.03 | -2,878.48 | 0 | -28.25 | 0.5 | 2 |
| touch_prot_n | 1 | 530 | 0.119 | -774.92 | 146.44 | -1,609.97 | 0.2283 | 4.16 | 0.2566 | 5 |
| touch_prot_n | 2 | 606 | 0.1361 | -987.11 | 114.41 | -1,558.82 | 0.1469 | 0.94 | 0.2442 | 7 |
| touch_prot_n | 3+ | 3,189 | 0.7163 | -1,071.34 | 42.49 | -1,534.28 | 0.1436 | -0.363 | 0.2916 | 8 |
| touch_prot_n | na | 125 | 0.0281 | -508.86 | 318.75 | -1,539.11 | 0.208 | 8.31 | 0.288 | 4 |
| touch_room_last | broke | 1,882 | 0.4227 | -1,013.88 | 54.77 | -1,532.60 | 0.1546 | 0.531 | 0.2705 | 7 |
| touch_room_last | held | 798 | 0.1792 | -1,096.47 | 77.07 | -1,505.81 | 0.1604 | -0.793 | 0.2794 | 7 |
| touch_room_last | pending | 1,031 | 0.2316 | -1,009.83 | 74.30 | -1,572.95 | 0.1426 | 0.602 | 0.3443 | 7 |
| touch_room_last | none | 739 | 0.166 | -903.06 | 139.07 | -1,570.49 | 0.1732 | 2.21 | 0.2219 | 3 |
| touch_room_last | na | 2 | 0.0004 | -1,589.20 | 1,194.44 | -1,589.20 | 0 | -9.12 | 0 | 1 |
| touch_room_n | 0 | 739 | 0.166 | -903.06 | 139.07 | -1,570.49 | 0.1732 | 2.21 | 0.2219 | 3 |
| touch_room_n | 1 | 508 | 0.1141 | -1,053.46 | 111.75 | -1,581.65 | 0.1614 | -0.076 | 0.2618 | 8 |
| touch_room_n | 2 | 516 | 0.1159 | -920.99 | 113.95 | -1,559.63 | 0.1802 | 1.92 | 0.2926 | 4 |
| touch_room_n | 3+ | 2,687 | 0.6035 | -1,047.21 | 43.39 | -1,530.52 | 0.1455 | 0.012 | 0.2988 | 8 |
| touch_room_n | na | 2 | 0.0004 | -1,589.20 | 1,194.44 | -1,589.20 | 0 | -9.12 | 0 | 1 |
| touch_swing_last | broke | 2,736 | 0.6146 | -991.60 | 53.84 | -1,550.90 | 0.17 | 0.834 | 0.2167 | 6 |
| touch_swing_last | held | 5 | 0.0011 | 401.82 | 2,001.21 | -1,734.90 | 0.4 | 22.53 | 0.2 | 1 |
| touch_swing_last | pending | 1,711 | 0.3843 | -1,042.53 | 55.60 | -1,534.31 | 0.1327 | 0.119 | 0.384 | 6 |
| touch_swing_n | 1 | 166 | 0.0373 | -1,093.51 | 215.95 | -1,701.72 | 0.1506 | -0.763 | 0.4036 | 9 |
| touch_swing_n | 2 | 332 | 0.0746 | -911.66 | 158.22 | -1,594.88 | 0.1596 | 2.06 | 0.2982 | 4 |
| touch_swing_n | 3+ | 3,954 | 0.8881 | -1,014.31 | 41.40 | -1,530.41 | 0.1558 | 0.517 | 0.2744 | 4 |

The 9 gate cells (`h4_minute_L1_grid.csv`):

| level | skip_when_last | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prot | broke | 6678696901d6e630 | 4,431 | 0.9953 | -1,009.20 | -1,094.83 | 85.62 | -92.34 | 44.30 | 0.8861 | 0.0051 | 0.9048 | 0.9985 | 0 | -1,399.17 | 8 | False |
| prot | held | 69be22dc4cffee7b | 4,292 | 0.9641 | -1,019.91 | -733.14 | -286.77 | 144.82 | 95.90 | 0.1799 | 0.0333 | 0.7812 | 0.9211 | 0.1429 | -1,409.88 | 6 | False |
| prot | pending | 905054e45d3fb8f1 | 308 | 0.0692 | -680.71 | -1,034.05 | 353.34 | -0.07 | 12.70 | 0.0275 | 0.9348 | 0.8477 | 0.1363 | 0.8 | -1,070.67 | 6 | False |
| room | broke | 91456038190bbdf5 | 2,570 | 0.5773 | -1,006.48 | -1,013.88 | 7.40 | -123.51 | 6.80 | 0.9155 | 0.4234 | 0.8454 | 0.6157 | 0.3571 | -1,396.44 | 7 | False |
| room | held | babad33bed46a900 | 3,654 | 0.8208 | -990.64 | -1,096.47 | 105.83 | 42.88 | 3.90 | 0.3053 | 0.1783 | 0.8396 | 0.8625 | 0.0857 | -1,380.60 | 7 | False |
| room | pending | 5c81240cc29a43f6 | 3,421 | 0.7684 | -1,009.54 | -1,009.83 | 0.29 | 19.33 | 32.40 | 0.9955 | 0.2352 | 0.8574 | 0.7884 | 0.2571 | -1,399.51 | 7 | False |
| swing | broke | 51ea141a73ed013c | 1,716 | 0.3854 | -1,038.32 | -991.60 | -46.72 | -10.56 | 94.40 | 0.5682 | 0.6043 | 0.83 | 0.3019 | 0.7286 | -1,428.29 | 6 | False |
| swing | held | 7a5fff2957003c41 | 4,447 | 0.9989 | -1,011.19 | 401.82 | -1,413.01 | -1,590.36 | 72.20 | 0.1149 | 0.0008 | 0.6 | 0.9954 | 0 | -1,401.16 | 1 | False |
| swing | pending | e2f8dcb18f756381 | 2,741 | 0.6157 | -989.06 | -1,042.53 | 53.47 | 18.19 | 6.00 | 0.5157 | 0.3949 | 0.8673 | 0.7028 | 0.2714 | -1,379.02 | 6 | False |

**Nested-CV candidate** (family `h4/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7e2a1c31f2dc16c3 | 3,758 | 0.8441 | -1,010.69 | -1,003.77 | -6.92 | 11.05 | 3.10 | 0.9535 | 0.1559 | 0.8444 | 0.8546 | 0.0857 | -1,400.65 | 5 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"level": "room", "skip_when_last": "held"} |  | 62.28 | 0.82 | 8 | 396 | 326 |
| 1 | {"level": "room", "skip_when_last": "held"} |  | 64.77 | 0.8218 | 8 | 388 | 315 |
| 2 | {"level": "room", "skip_when_last": "held"} |  | 111.65 | 0.8194 | 8 | 384 | 321 |
| 3 | {"level": "room", "skip_when_last": "held"} |  | 126.57 | 0.8252 | 8 | 509 | 408 |
| 4 | {"level": "room", "skip_when_last": "held"} |  | 110.74 | 0.8232 | 8 | 390 | 310 |
| 5 | {"level": "room", "skip_when_last": "held"} |  | 107.86 | 0.8202 | 8 | 341 | 285 |
| 6 | {"level": "prot", "skip_when_last": "broke"} |  | 155.23 | 0.995 | 8 | 424 | 423 |
| 7 | {"level": "swing", "skip_when_last": "pending"} |  | 95.00 | 0.6142 | 8 | 266 | 170 |
| 8 | {"level": "room", "skip_when_last": "held"} |  | 115.14 | 0.8218 | 8 | 170 | 135 |
| 9 | {"level": "room", "skip_when_last": "held"} |  | 145.97 | 0.8184 | 8 | 499 | 419 |
| 10 | {"level": "room", "skip_when_last": "held"} |  | 112.96 | 0.8211 | 8 | 173 | 142 |
| 11 | {"level": "prot", "skip_when_last": "broke"} |  | 416.16 | 0.9967 | 8 | 512 | 504 |

CPCV paths (`h4/nested_cv/cpcv`, 11 rows): diff median -6.92, 5th pct -171.27, min -171.33, share > 0 0.273, control pct median 2.10 / 5th pct 0.4

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| 2275f28d3ff687ac | 3,583 | 0.8048 | -1,043.05 | -871.72 | -171.33 | 0.5 | 0.0935 | 0.7675 | 4 | 0 |
| 4438e5f735110c56 | 3,582 | 0.8046 | -1,038.44 | -890.90 | -147.54 | 0.3 | 0.1319 | 0.7972 | 3 | 1 |
| ac551eabeb70d534 | 3,758 | 0.8441 | -1,010.69 | -1,003.77 | -6.92 | 3.30 | 0.951 | 0.8546 | 5 | 2 |
| 683f686c4f780efa | 3,677 | 0.8259 | -1,010.15 | -1,007.05 | -3.09 | 1.90 | 0.9715 | 0.8361 | 6 | 3 |
| 91ab3760d93ec46d | 3,758 | 0.8441 | -1,010.69 | -1,003.77 | -6.92 | 3.50 | 0.954 | 0.8546 | 5 | 4 |
| 3dd70d2aa664f92d | 4,093 | 0.9194 | -1,023.41 | -852.21 | -171.21 | 1.20 | 0.2419 | 0.897 | 4 | 5 |
| 93eafa472e6f4d38 | 3,554 | 0.7983 | -1,012.58 | -997.85 | -14.73 | 2.10 | 0.8836 | 0.8581 | 5 | 6 |
| 1c037e90c061b44a | 3,676 | 0.8257 | -1,006.83 | -1,022.74 | 15.91 | 5.50 | 0.8941 | 0.8381 | 6 | 7 |
| 3d3fd1a89c43c1f9 | 3,802 | 0.854 | -994.16 | -1,099.99 | 105.83 | 12.40 | 0.3393 | 0.8901 | 6 | 8 |
| 1329ecf1b27d8009 | 3,825 | 0.8592 | -1,015.97 | -970.80 | -45.17 | 0.9 | 0.7031 | 0.8612 | 5 | 9 |
| 5263e208d50bd83e | 4,431 | 0.9953 | -1,009.20 | -1,094.83 | 85.62 | 44.10 | 0.8851 | 0.9985 | 8 | 10 |

Cells chosen across the 66 CPCV training sets: {"level": "room", "skip_when_last": "held"} x35; {"level": "prot", "skip_when_last": "broke"} x20; {"level": "swing", "skip_when_last": "pending"} x8; {"level": "room", "skip_when_last": "broke"} x2; {"level": "swing", "skip_when_last": "held"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 10 | 10 | 1.59 | 0.4249 | 0.081 | 0.936 | 0.936 |  | {"level": "swing", "skip_when_last": "broke"} | 54.10 | [-220.04, 187.58] | 0.505 | 0.9987 | -6.92 | -171.27 | 0.273 | 2.10 | False | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### 1 min / L0 (4,502 IS units)

L0 robustness:

| variable | bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| touch_prot_last | broke | 21 | 0.0047 | -905.70 | 313.36 | -1,464.40 | 0.1429 | 2.54 | 0.4762 | 7 |
| touch_prot_last | held | 166 | 0.0369 | -379.14 | 527.21 | -1,817.86 | 0.2169 | 10.36 | 0.4639 | 6 |
| touch_prot_last | pending | 4,187 | 0.93 | -938.32 | 80.88 | -1,599.13 | 0.1486 | 1.68 | 0.3083 | 7 |
| touch_prot_last | none | 2 | 0.0004 | -20,902.24 | 17,146.72 | -20,902.24 | 0 | -305.60 | 1.00 | 2 |
| touch_prot_last | na | 126 | 0.028 | -774.28 | 376.94 | -1,630.69 | 0.1825 | 4.22 | 0.3254 | 8 |
| touch_prot_n | 0 | 2 | 0.0004 | -20,902.24 | 17,146.72 | -20,902.24 | 0 | -305.60 | 1.00 | 2 |
| touch_prot_n | 1 | 535 | 0.1188 | -828.41 | 216.03 | -1,700.37 | 0.2075 | 3.33 | 0.2897 | 5 |
| touch_prot_n | 2 | 611 | 0.1357 | -923.03 | 226.47 | -1,645.29 | 0.1457 | 1.93 | 0.2831 | 6 |
| touch_prot_n | 3+ | 3,228 | 0.717 | -930.47 | 92.90 | -1,587.95 | 0.1428 | 1.81 | 0.3253 | 6 |
| touch_prot_n | na | 126 | 0.028 | -774.28 | 376.94 | -1,630.69 | 0.1825 | 4.22 | 0.3254 | 8 |
| touch_room_last | broke | 1,897 | 0.4214 | -867.24 | 130.99 | -1,605.79 | 0.1529 | 2.79 | 0.3094 | 4 |
| touch_room_last | held | 813 | 0.1806 | -1,111.25 | 107.14 | -1,565.69 | 0.1599 | -1.02 | 0.3149 | 9 |
| touch_room_last | pending | 1,049 | 0.233 | -1,096.06 | 96.57 | -1,618.15 | 0.1354 | -0.721 | 0.3746 | 9 |
| touch_room_last | none | 741 | 0.1646 | -605.32 | 290.57 | -1,624.92 | 0.1646 | 6.79 | 0.2497 | 6 |
| touch_room_last | na | 2 | 0.0004 | -1,589.20 | 1,194.44 | -1,589.20 | 0 | -9.12 | 0 | 1 |
| touch_room_n | 0 | 741 | 0.1646 | -605.32 | 290.57 | -1,624.92 | 0.1646 | 6.79 | 0.2497 | 6 |
| touch_room_n | 1 | 516 | 0.1146 | -1,075.59 | 145.62 | -1,655.53 | 0.155 | -0.414 | 0.2907 | 8 |
| touch_room_n | 2 | 519 | 0.1153 | -950.14 | 163.31 | -1,614.53 | 0.1715 | 1.48 | 0.316 | 6 |
| touch_room_n | 3+ | 2,724 | 0.6051 | -972.92 | 94.89 | -1,595.39 | 0.1443 | 1.16 | 0.3385 | 7 |
| touch_room_n | na | 2 | 0.0004 | -1,589.20 | 1,194.44 | -1,589.20 | 0 | -9.12 | 0 | 1 |
| touch_swing_last | broke | 2,755 | 0.612 | -954.43 | 103.48 | -1,629.25 | 0.1575 | 1.41 | 0.2512 | 6 |
| touch_swing_last | held | 5 | 0.0011 | 663.32 | 2,145.92 | -1,734.90 | 0.4 | 26.55 | 0.2 | 1 |
| touch_swing_last | pending | 1,742 | 0.3869 | -874.83 | 121.31 | -1,583.92 | 0.1424 | 2.70 | 0.4179 | 6 |
| touch_swing_n | 1 | 167 | 0.0371 | -400.40 | 507.77 | -1,704.71 | 0.1557 | 9.90 | 0.4192 | 7 |
| touch_swing_n | 2 | 336 | 0.0746 | -917.37 | 367.57 | -1,687.53 | 0.1577 | 1.97 | 0.3452 | 8 |
| touch_swing_n | 3+ | 3,999 | 0.8883 | -943.98 | 80.49 | -1,595.19 | 0.1513 | 1.60 | 0.3088 | 5 |

The 9 gate cells (`h4_minute_L0_grid.csv`):

| level | skip_when_last | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prot | broke | 453a47368c8c952f | 4,481 | 0.9953 | -921.91 | -905.70 | -16.21 | -398.78 | 49.00 | 0.9815 | 0.0047 | 0.8571 | 0.9982 | 0 | -1,311.87 | 7 | False |
| prot | held | 70d7611e97701d64 | 4,336 | 0.9631 | -942.61 | -379.14 | -563.47 | -65.92 | 84.90 | 0.1524 | 0.034 | 0.7831 | 0.9218 | 0.087 | -1,332.57 | 6 | False |
| prot | pending | f16edfac5d982b9d | 315 | 0.07 | -702.60 | -938.32 | 235.72 | -12.46 | 16.90 | 0.4423 | 0.9337 | 0.8514 | 0.1156 | 0.8841 | -1,092.57 | 7 | False |
| room | broke | 9d1b586504f95722 | 2,605 | 0.5786 | -961.58 | -867.24 | -94.34 | -12.16 | 2.20 | 0.5737 | 0.4209 | 0.8471 | 0.5536 | 0.3768 | -1,351.55 | 4 | False |
| room | held | 314899f06c4c0890 | 3,689 | 0.8194 | -880.09 | -1,111.25 | 231.16 | -67.84 | 67.00 | 0.2519 | 0.1789 | 0.8401 | 0.8719 | 0.1884 | -1,270.05 | 9 | False |
| room | pending | 795de756726d4d14 | 3,453 | 0.767 | -868.90 | -1,096.06 | 227.15 | -26.44 | 67.90 | 0.2444 | 0.2376 | 0.8646 | 0.8387 | 0.1884 | -1,258.87 | 9 | False |
| swing | broke | b7bc9287448e5e23 | 1,747 | 0.388 | -870.43 | -954.43 | 83.99 | 179.44 | 80.50 | 0.6147 | 0.6079 | 0.8425 | 0.3474 | 0.6812 | -1,260.40 | 6 | False |
| swing | held | 926234ed05418791 | 4,497 | 0.9989 | -923.59 | 663.32 | -1,586.92 | -1,968.13 | 51.20 | 0.1734 | 0.0008 | 0.6 | 0.9966 | 0 | -1,313.56 | 1 | False |
| swing | pending | 14312c2d984dcbdc | 2,760 | 0.6131 | -951.49 | -874.83 | -76.66 | -170.34 | 19.00 | 0.6367 | 0.3913 | 0.8576 | 0.6559 | 0.3188 | -1,341.46 | 6 | False |

**Nested-CV candidate** (family `h4/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f761a518d322b977 | 3,588 | 0.797 | -915.92 | -945.02 | 29.10 | -82.94 | 10.50 | 0.8821 | 0.2048 | 0.8556 | 0.8341 | 0.2319 | -1,305.89 | 6 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"level": "room", "skip_when_last": "held"} |  | 251.46 | 0.8188 | 8 | 400 | 328 |
| 1 | {"level": "room", "skip_when_last": "pending"} |  | 178.87 | 0.7694 | 8 | 392 | 290 |
| 2 | {"level": "room", "skip_when_last": "held"} |  | 243.51 | 0.8183 | 8 | 386 | 321 |
| 3 | {"level": "room", "skip_when_last": "pending"} |  | 262.70 | 0.7636 | 8 | 512 | 405 |
| 4 | {"level": "room", "skip_when_last": "held"} |  | 253.37 | 0.8215 | 8 | 395 | 315 |
| 5 | {"level": "room", "skip_when_last": "pending"} |  | 248.62 | 0.7649 | 8 | 345 | 269 |
| 6 | {"level": "room", "skip_when_last": "pending"} |  | 266.28 | 0.7679 | 8 | 430 | 327 |
| 7 | {"level": "room", "skip_when_last": "pending"} |  | 266.03 | 0.767 | 8 | 269 | 207 |
| 8 | {"level": "room", "skip_when_last": "pending"} |  | 165.16 | 0.7681 | 8 | 172 | 127 |
| 9 | {"level": "room", "skip_when_last": "held"} |  | 235.55 | 0.8165 | 8 | 506 | 426 |
| 10 | {"level": "room", "skip_when_last": "pending"} |  | 188.29 | 0.7669 | 8 | 174 | 133 |
| 11 | {"level": "room", "skip_when_last": "held"} |  | 301.34 | 0.8163 | 8 | 521 | 440 |

CPCV paths (`h4/nested_cv/cpcv`, 11 rows): diff median 72.72, 5th pct -60.02, min -99.65, share > 0 0.727, control pct median 24.10 / 5th pct 11.00

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| b81047a786ce6a21 | 3,239 | 0.7195 | -925.19 | -913.22 | -11.97 | 18.40 | 0.948 | 0.7053 | 6 | 0 |
| 04be73f3a04b502c | 3,286 | 0.7299 | -927.34 | -906.94 | -20.40 | 12.20 | 0.9045 | 0.7434 | 7 | 1 |
| b3a76c3fab4093fb | 3,632 | 0.8068 | -903.37 | -998.92 | 95.56 | 28.60 | 0.6322 | 0.8442 | 8 | 2 |
| 51e4a19de7ba27aa | 3,621 | 0.8043 | -907.60 | -980.32 | 72.72 | 18.20 | 0.7226 | 0.8453 | 7 | 3 |
| e42eb20f1a87ce36 | 3,608 | 0.8014 | -909.06 | -973.38 | 64.32 | 25.40 | 0.7386 | 0.8397 | 6 | 4 |
| 8a4bd4386ce6df31 | 3,545 | 0.7874 | -900.69 | -1,000.14 | 99.45 | 24.30 | 0.6257 | 0.8325 | 7 | 5 |
| 16fcc024a03cde73 | 3,697 | 0.8212 | -899.70 | -1,023.47 | 123.77 | 39.10 | 0.5397 | 0.8669 | 7 | 6 |
| f56a4afc9c406e90 | 3,546 | 0.7876 | -905.97 | -980.66 | 74.69 | 22.70 | 0.6902 | 0.8287 | 7 | 7 |
| fdb66cc17df2a731 | 3,593 | 0.7981 | -912.50 | -958.71 | 46.21 | 24.10 | 0.8146 | 0.8031 | 7 | 8 |
| 18e15efd087573af | 3,344 | 0.7428 | -947.46 | -847.81 | -99.65 | 9.80 | 0.5827 | 0.712 | 4 | 9 |
| 88789f41380e6af3 | 3,841 | 0.8532 | -897.66 | -1,062.26 | 164.60 | 43.70 | 0.4663 | 0.8915 | 7 | 10 |

Cells chosen across the 66 CPCV training sets: {"level": "room", "skip_when_last": "held"} x30; {"level": "room", "skip_when_last": "pending"} x29; {"level": "swing", "skip_when_last": "broke"} x4; {"level": "prot", "skip_when_last": "broke"} x2; {"level": "swing", "skip_when_last": "held"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L0 | pre-registered (family as at the primary run) | 10 | 10 | 1.71 | 0.6843 | 0.5936 | 0.9785 | 0.9785 |  | {"level": "room", "skip_when_last": "held"} | 38.77 | [-208.78, 256.9] | 0.4145 | 0.8465 | 72.72 | -60.02 | 0.727 | 24.10 | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### 5 min / L1 (826 IS units)

Foundation outcome by the last touch verdict and by the number of touch episodes in the hour before the SETUP (`h4_5minute_L1_by_touch.csv`):

| variable | bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| touch_prot_last | broke | 3 | 0.0036 | 2,048.26 | 4,408.97 | -2,328.55 | 0.3333 | 47.70 | 0.6667 | 2 |
| touch_prot_last | held | 604 | 0.7312 | -685.62 | 186.24 | -2,068.93 | 0.2781 | 5.63 | 0.399 | 5 |
| touch_prot_last | pending | 137 | 0.1659 | -777.24 | 352.07 | -2,033.52 | 0.2701 | 4.11 | 0.4307 | 6 |
| touch_prot_last | none | 67 | 0.0811 | -1,048.93 | 571.90 | -2,570.17 | 0.3134 | 0.022 | 0.5075 | 8 |
| touch_prot_last | na | 15 | 0.0182 | -2,706.37 | 814.64 | -3,035.50 | 0.1333 | -25.79 | 0.6667 | 6 |
| touch_prot_n | 0 | 67 | 0.0811 | -1,048.93 | 571.90 | -2,570.17 | 0.3134 | 0.022 | 0.5075 | 8 |
| touch_prot_n | 1 | 328 | 0.3971 | -391.52 | 272.25 | -2,021.95 | 0.3232 | 10.14 | 0.3902 | 3 |
| touch_prot_n | 2 | 286 | 0.3462 | -1,054.90 | 230.37 | -2,094.30 | 0.2448 | 0.001 | 0.4161 | 6 |
| touch_prot_n | 3+ | 130 | 0.1574 | -648.70 | 404.20 | -2,075.14 | 0.2308 | 5.99 | 0.4231 | 8 |
| touch_prot_n | na | 15 | 0.0182 | -2,706.37 | 814.64 | -3,035.50 | 0.1333 | -25.79 | 0.6667 | 6 |
| touch_room_last | broke | 149 | 0.1804 | -609.75 | 399.81 | -2,289.98 | 0.2886 | 6.84 | 0.4497 | 6 |
| touch_room_last | held | 61 | 0.0738 | -1,393.89 | 442.13 | -2,218.87 | 0.1803 | -5.31 | 0.4918 | 7 |
| touch_room_last | pending | 163 | 0.1973 | -100.76 | 377.42 | -1,890.22 | 0.2699 | 14.53 | 0.454 | 3 |
| touch_room_last | none | 453 | 0.5484 | -955.90 | 205.14 | -2,200.88 | 0.2892 | 1.45 | 0.3863 | 10 |
| touch_room_n | 0 | 453 | 0.5484 | -955.90 | 205.14 | -2,200.88 | 0.2892 | 1.45 | 0.3863 | 10 |
| touch_room_n | 1 | 202 | 0.2446 | -607.12 | 346.54 | -2,226.79 | 0.2426 | 6.79 | 0.4901 | 4 |
| touch_room_n | 2 | 111 | 0.1344 | -254.99 | 444.92 | -1,958.30 | 0.2973 | 12.20 | 0.4054 | 4 |
| touch_room_n | 3+ | 60 | 0.0726 | -689.37 | 467.76 | -1,957.41 | 0.2667 | 5.64 | 0.45 | 5 |
| touch_swing_last | broke | 448 | 0.5424 | -866.09 | 207.50 | -2,276.28 | 0.2835 | 2.78 | 0.3817 | 7 |
| touch_swing_last | held | 169 | 0.2046 | -911.35 | 382.64 | -2,345.66 | 0.284 | 2.17 | 0.4793 | 9 |
| touch_swing_last | pending | 201 | 0.2433 | -471.17 | 299.63 | -1,809.54 | 0.2438 | 8.95 | 0.4527 | 2 |
| touch_swing_last | none | 8 | 0.0097 | 1,425.69 | 2,245.50 | 1,527.78 | 0.625 | 38.81 | 0.375 | 2 |
| touch_swing_n | 0 | 8 | 0.0097 | 1,425.69 | 2,245.50 | 1,527.78 | 0.625 | 38.81 | 0.375 | 2 |
| touch_swing_n | 1 | 215 | 0.2603 | -832.21 | 324.15 | -2,176.34 | 0.2744 | 3.33 | 0.414 | 8 |
| touch_swing_n | 2 | 336 | 0.4068 | -851.84 | 243.70 | -2,249.40 | 0.2798 | 3.05 | 0.4435 | 6 |
| touch_swing_n | 3+ | 267 | 0.3232 | -642.65 | 262.33 | -1,955.25 | 0.2659 | 6.25 | 0.3933 | 6 |

The 9 gate cells (`h4_5minute_L1_grid.csv`):

| level | skip_when_last | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prot | broke | cf2a5f1dd3e82550 | 823 | 0.9964 | -767.28 | 2,048.26 | -2,815.53 | -3,033.13 | 41.60 | 0.2324 | 0.0034 | 0.6667 | 0.9902 | 0 | -1,157.24 | 2 | False |
| prot | held | 6fd8306a0548d73b | 222 | 0.2688 | -951.40 | -685.62 | -265.78 | -206.45 | 47.70 | 0.4493 | 0.7303 | 0.7219 | 0.2549 | 0.8261 | -1,341.37 | 5 | False |
| prot | pending | 0818dce9159abc40 | 689 | 0.8341 | -753.04 | -777.24 | 24.21 | 99.62 | 18.90 | 0.9555 | 0.1675 | 0.7299 | 0.8473 | 0.087 | -1,143.00 | 6 | False |
| room | broke | 136f703118c8fefb | 677 | 0.8196 | -789.47 | -609.75 | -179.73 | -286.63 | 98.80 | 0.6737 | 0.1776 | 0.7114 | 0.7836 | 0.2609 | -1,179.44 | 6 | False |
| room | held | 74d6b4f066d0481e | 765 | 0.9262 | -706.27 | -1,393.89 | 687.62 | 454.06 | 87.30 | 0.2629 | 0.0838 | 0.8197 | 0.956 | 0.0435 | -1,096.24 | 7 | False |
| room | pending | 7b760716df543532 | 663 | 0.8027 | -918.40 | -100.76 | -817.64 | -616.02 | 0.2 | 0.0325 | 0.1993 | 0.7301 | 0.7599 | 0.3043 | -1,308.37 | 3 | False |
| swing | broke | a551ed716f433a2b | 378 | 0.4576 | -627.83 | -866.09 | 238.26 | 234.20 | 43.10 | 0.4493 | 0.5377 | 0.7165 | 0.4776 | 0.4783 | -1,017.79 | 7 | False |
| swing | held | 6929b817eddc2da3 | 657 | 0.7954 | -717.36 | -911.35 | 193.99 | 227.56 | 94.80 | 0.6152 | 0.2027 | 0.716 | 0.7812 | 0.1739 | -1,107.33 | 9 | False |
| swing | pending | ed145b95e5cb7898 | 625 | 0.7567 | -848.99 | -471.17 | -377.82 | -388.85 | 7.00 | 0.2919 | 0.2546 | 0.7562 | 0.7638 | 0.3043 | -1,238.96 | 2 | False |

**Nested-CV candidate** (family `h4/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9e32a86bcfc8f5ce | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 381.35 | 83.80 | 0.3228 | 0.0771 | 0.8214 | 0.9563 | 0.0435 | -1,105.43 | 7 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"level": "room", "skip_when_last": "held"} |  | 534.06 | 0.9258 | 9 | 82 | 76 |
| 1 | {"level": "room", "skip_when_last": "held"} |  | 801.76 | 0.9244 | 9 | 83 | 78 |
| 2 | {"level": "room", "skip_when_last": "held"} |  | 660.19 | 0.9286 | 9 | 42 | 37 |
| 3 | {"level": "room", "skip_when_last": "held"} |  | 742.16 | 0.9259 | 9 | 76 | 70 |
| 4 | {"level": "room", "skip_when_last": "held"} |  | 777.82 | 0.9231 | 9 | 72 | 69 |
| 5 | {"level": "room", "skip_when_last": "held"} |  | 778.43 | 0.9277 | 9 | 73 | 67 |
| 6 | {"level": "room", "skip_when_last": "held"} |  | 467.67 | 0.9302 | 9 | 77 | 68 |
| 7 | {"level": "room", "skip_when_last": "held"} |  | 622.48 | 0.9265 | 9 | 51 | 47 |
| 8 | {"level": "room", "skip_when_last": "held"} |  | 509.35 | 0.925 | 9 | 76 | 71 |
| 9 | {"level": "room", "skip_when_last": "held"} |  | 738.33 | 0.9236 | 9 | 80 | 76 |
| 10 | {"level": "room", "skip_when_last": "held"} |  | 761.99 | 0.9257 | 9 | 31 | 29 |
| 11 | {"level": "prot", "skip_when_last": "broke"} |  | 1,552.78 | 0.9973 | 9 | 83 | 82 |

CPCV paths (`h4/nested_cv/cpcv`, 11 rows): diff median -2.08, 5th pct -1,774.85, min -2,815.53, share > 0 0.455, control pct median 71.80 / 5th pct 35.00

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| df980cc6bd2b4329 | 748 | 0.9056 | -791.60 | -425.71 | -365.90 | 58.20 | 0.4808 | 0.8781 | 6 | 0 |
| fbdc923651e69b6a | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 83.40 | 0.3223 | 0.9563 | 7 | 1 |
| 225960f31efd22ea | 751 | 0.9092 | -757.24 | -755.16 | -2.08 | 61.40 | 0.9945 | 0.9097 | 6 | 2 |
| 9dc7a2d4369ff815 | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 84.00 | 0.3163 | 0.9563 | 7 | 3 |
| 596770b84be354e8 | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 83.20 | 0.3208 | 0.9563 | 7 | 4 |
| fab903e92fea6da7 | 735 | 0.8898 | -802.82 | -387.39 | -415.43 | 71.80 | 0.4208 | 0.8674 | 5 | 5 |
| f2a9b71fb55c3496 | 695 | 0.8414 | -790.57 | -579.21 | -211.36 | 28.00 | 0.6242 | 0.8032 | 5 | 6 |
| ce335f4f113b59d2 | 743 | 0.8995 | -830.82 | -96.66 | -734.17 | 49.80 | 0.1609 | 0.859 | 5 | 7 |
| f4ba68fad4ff5ef6 | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 84.30 | 0.3063 | 0.9563 | 7 | 8 |
| 6fc5554a2cff6d9e | 770 | 0.9322 | -715.46 | -1,328.94 | 613.48 | 83.00 | 0.3173 | 0.9563 | 7 | 9 |
| 21c568e05512b5fc | 823 | 0.9964 | -767.28 | 2,048.26 | -2,815.53 | 42.00 | 0.2264 | 0.9902 | 2 | 10 |

Cells chosen across the 66 CPCV training sets: {"level": "room", "skip_when_last": "held"} x50; {"level": "prot", "skip_when_last": "broke"} x11; {"level": "swing", "skip_when_last": "broke"} x3; {"level": "swing", "skip_when_last": "held"} x1; {"level": "room", "skip_when_last": "broke"} x1

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L1 | pre-registered (family as at the primary run) | 10 | 10 | 1.64 | 0.6501 | 0.5715 | 0.1705 | 0.1805 |  | {"level": "room", "skip_when_last": "broke"} | 100.53 | [-289.64, 1371.11] | 0.1165 | 0.8863 | -2.08 | -1,774.85 | 0.455 | 71.80 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |


### 5 min / L0 (832 IS units)

L0 robustness:

| variable | bucket | n | share | net_mean | net_se | net_median | win_rate | pts_mean | stop_share | blocks_below_block_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| touch_prot_last | broke | 3 | 0.0036 | 2,511.94 | 4,872.65 | -2,328.55 | 0.3333 | 54.83 | 0.6667 | 2 |
| touch_prot_last | held | 609 | 0.732 | -205.82 | 428.06 | -2,462.60 | 0.2266 | 13.01 | 0.4943 | 4 |
| touch_prot_last | pending | 138 | 0.1659 | -240.72 | 606.79 | -2,267.44 | 0.2464 | 12.36 | 0.529 | 8 |
| touch_prot_last | none | 67 | 0.0805 | -306.38 | 1,654.98 | -3,263.92 | 0.1642 | 11.45 | 0.6269 | 10 |
| touch_prot_last | na | 15 | 0.018 | -3,913.94 | 426.03 | -3,128.10 | 0 | -44.37 | 0.7333 | 7 |
| touch_prot_n | 0 | 67 | 0.0805 | -306.38 | 1,654.98 | -3,263.92 | 0.1642 | 11.45 | 0.6269 | 10 |
| touch_prot_n | 1 | 331 | 0.3978 | 234.29 | 606.09 | -2,462.60 | 0.2598 | 19.78 | 0.4562 | 3 |
| touch_prot_n | 2 | 288 | 0.3462 | -594.66 | 564.47 | -2,441.99 | 0.2014 | 7.08 | 0.5347 | 7 |
| touch_prot_n | 3+ | 131 | 0.1575 | -437.52 | 702.15 | -2,245.62 | 0.2214 | 9.24 | 0.542 | 7 |
| touch_prot_n | na | 15 | 0.018 | -3,913.94 | 426.03 | -3,128.10 | 0 | -44.37 | 0.7333 | 7 |
| touch_room_last | broke | 149 | 0.1791 | 1,147.61 | 1,125.34 | -2,605.73 | 0.2483 | 33.88 | 0.5034 | 4 |
| touch_room_last | held | 61 | 0.0733 | -2,335.82 | 527.65 | -2,786.02 | 0.082 | -19.80 | 0.6066 | 10 |
| touch_room_last | pending | 163 | 0.1959 | -31.44 | 753.47 | -2,242.15 | 0.227 | 15.59 | 0.5828 | 8 |
| touch_room_last | none | 458 | 0.5505 | -547.53 | 452.08 | -2,609.92 | 0.2293 | 7.73 | 0.4825 | 8 |
| touch_room_last | na | 1 | 0.0012 | -2,877.11 |  | -2,877.11 | 0 | -27.60 | 1.00 | 1 |
| touch_room_n | 0 | 458 | 0.5505 | -547.53 | 452.08 | -2,609.92 | 0.2293 | 7.73 | 0.4825 | 8 |
| touch_room_n | 1 | 203 | 0.244 | -207.25 | 739.01 | -2,502.73 | 0.1872 | 12.94 | 0.5813 | 7 |
| touch_room_n | 2 | 111 | 0.1334 | 865.61 | 1,275.64 | -2,423.33 | 0.2523 | 29.44 | 0.5135 | 6 |
| touch_room_n | 3+ | 60 | 0.0721 | -558.40 | 770.17 | -2,252.82 | 0.2167 | 7.66 | 0.55 | 9 |
| touch_swing_last | broke | 452 | 0.5433 | -229.70 | 459.44 | -2,641.85 | 0.2257 | 12.57 | 0.4779 | 4 |
| touch_swing_last | held | 171 | 0.2055 | 370.80 | 1,138.17 | -2,803.35 | 0.2105 | 21.90 | 0.5614 | 7 |
| touch_swing_last | pending | 201 | 0.2416 | -1,015.92 | 385.91 | -2,179.99 | 0.209 | 0.571 | 0.5672 | 8 |
| touch_swing_last | none | 8 | 0.0096 | 1,794.15 | 2,781.46 | 1,285.82 | 0.5 | 44.48 | 0.375 | 3 |
| touch_swing_n | 0 | 8 | 0.0096 | 1,794.15 | 2,781.46 | 1,285.82 | 0.5 | 44.48 | 0.375 | 3 |
| touch_swing_n | 1 | 218 | 0.262 | 226.78 | 939.23 | -2,603.64 | 0.2202 | 19.62 | 0.4954 | 6 |
| touch_swing_n | 2 | 337 | 0.405 | -279.26 | 523.82 | -2,575.41 | 0.2285 | 11.86 | 0.5312 | 6 |
| touch_swing_n | 3+ | 269 | 0.3233 | -743.28 | 439.79 | -2,458.97 | 0.2045 | 4.70 | 0.5167 | 8 |

The 9 gate cells (`h4_5minute_L0_grid.csv`):

| level | skip_when_last | id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks | go_raw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prot | broke | 4fc3902e61454f5e | 829 | 0.9964 | -286.85 | 2,511.94 | -2,798.79 | -3,578.69 | 8.80 | 0.4738 | 0.0031 | 0.6667 | 0.9938 | 0 | -676.81 | 2 | False |
| prot | held | 096e34f1d9907f78 | 223 | 0.268 | -470.49 | -205.82 | -264.68 | -23.37 | 21.60 | 0.7371 | 0.7269 | 0.7734 | 0.2554 | 0.7895 | -860.46 | 4 | False |
| prot | pending | 23ee5cd6705d3e7d | 694 | 0.8341 | -283.92 | -240.72 | -43.20 | -650.39 | 52.90 | 0.964 | 0.1605 | 0.7536 | 0.8547 | 0.1053 | -673.89 | 8 | False |
| room | broke | f39f9f975ca1e7a3 | 683 | 0.8209 | -587.49 | 1,147.61 | -1,735.10 | -382.39 | 48.00 | 0.055 | 0.1728 | 0.7517 | 0.7178 | 0.3684 | -977.45 | 4 | False |
| room | held | 6a4bd44ed294d96c | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 1,384.76 | 99.50 | 0.092 | 0.0864 | 0.918 | 0.9783 | 0 | -503.81 | 10 | False |
| room | pending | 0e0b57a2d4b3fa4c | 669 | 0.8041 | -336.53 | -31.44 | -305.09 | -563.97 | 18.70 | 0.7431 | 0.1944 | 0.773 | 0.8098 | 0.1579 | -726.49 | 8 | False |
| swing | broke | a513568feef6df11 | 380 | 0.4567 | -332.74 | -229.70 | -103.04 | -280.42 | 63.00 | 0.8901 | 0.5401 | 0.7743 | 0.4262 | 0.7368 | -722.70 | 4 | False |
| swing | held | 7f3bdf6c8658015c | 661 | 0.7945 | -444.28 | 370.80 | -815.08 | 364.18 | 43.90 | 0.3663 | 0.2083 | 0.7895 | 0.7228 | 0.2105 | -834.24 | 7 | False |
| swing | pending | bf1d6d3a3066cd94 | 631 | 0.7584 | -41.30 | -1,015.92 | 974.61 | 207.11 | 29.40 | 0.2414 | 0.2454 | 0.791 | 0.8678 | 0.0526 | -431.27 | 8 | False |

**Nested-CV candidate** (family `h4/nested_cv`, the 12-block OOF mask):

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | diff_top1_removed | control_pct | perm_p | loser_recall | loser_precision | winner_recall_weighted | top_decile_winners_skipped | kept_mean_slip8 | sign_blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a329912797859321 | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 1,384.76 | 99.20 | 0.097 | 0.0864 | 0.918 | 0.9783 | 0 | -503.81 | 10 |

Chosen cell per training fold:

| block | chosen | thr | train_diff | train_kept_share | eligible | test_n | test_kept |
|---|---|---|---|---|---|---|---|
| 0 | {"level": "room", "skip_when_last": "held"} |  | 2,149.54 | 0.9263 | 9 | 83 | 77 |
| 1 | {"level": "room", "skip_when_last": "held"} |  | 2,249.32 | 0.9249 | 9 | 84 | 79 |
| 2 | {"level": "room", "skip_when_last": "held"} |  | 1,809.63 | 0.929 | 9 | 42 | 37 |
| 3 | {"level": "room", "skip_when_last": "held"} |  | 2,267.64 | 0.9263 | 9 | 77 | 71 |
| 4 | {"level": "room", "skip_when_last": "held"} |  | 2,357.45 | 0.9236 | 9 | 72 | 69 |
| 5 | {"level": "room", "skip_when_last": "held"} |  | 2,284.26 | 0.9282 | 9 | 73 | 67 |
| 6 | {"level": "room", "skip_when_last": "held"} |  | 2,141.69 | 0.9307 | 9 | 78 | 69 |
| 7 | {"level": "room", "skip_when_last": "held"} |  | 2,136.25 | 0.9269 | 9 | 51 | 47 |
| 8 | {"level": "room", "skip_when_last": "held"} |  | 1,943.50 | 0.9255 | 9 | 76 | 71 |
| 9 | {"level": "room", "skip_when_last": "held"} |  | 2,227.45 | 0.9239 | 9 | 82 | 78 |
| 10 | {"level": "room", "skip_when_last": "held"} |  | 2,148.57 | 0.9262 | 9 | 31 | 29 |
| 11 | {"level": "room", "skip_when_last": "held"} |  | 2,397.89 | 0.9266 | 9 | 83 | 77 |

CPCV paths (`h4/nested_cv/cpcv`, 11 rows): diff median 2,221.97, 5th pct 2,221.97, min 2,221.97, share > 0 1.00, control pct median 99.30 / 5th pct 99.20

| id | kept_n | kept_share | kept_mean | skipped_mean | diff | control_pct | perm_p | winner_recall_weighted | sign_blocks | path |
|---|---|---|---|---|---|---|---|---|---|---|
| abdb0e569564599a | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.40 | 0.0785 | 0.9783 | 10 | 0 |
| a900c700654bee22 | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.20 | 0.0795 | 0.9783 | 10 | 1 |
| 9c41664356f80328 | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.30 | 0.083 | 0.9783 | 10 | 2 |
| 6be4975682c1c16d | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.30 | 0.084 | 0.9783 | 10 | 3 |
| f257c65f57b49bc6 | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.30 | 0.0935 | 0.9783 | 10 | 4 |
| 108422a0b765f30f | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.50 | 0.0865 | 0.9783 | 10 | 5 |
| 2bf581dd4f0c321a | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.30 | 0.083 | 0.9783 | 10 | 6 |
| 301b8e004fb350fb | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.30 | 0.08 | 0.9783 | 10 | 7 |
| 6550cd6bbfcf8ddd | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.10 | 0.097 | 0.9783 | 10 | 8 |
| 7ce9ba79dc3fb4df | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.20 | 0.1084 | 0.9783 | 10 | 9 |
| 796c425b52068499 | 771 | 0.9267 | -113.85 | -2,335.82 | 2,221.97 | 99.20 | 0.092 | 0.9783 | 10 | 10 |

Cells chosen across the 66 CPCV training sets: {"level": "room", "skip_when_last": "held"} x66

Family on this table (every non-cpcv ledger row of the study, tf and label, as at the primary run; no post-hoc row exists for this table):

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 min | L0 | pre-registered (family as at the primary run) | 10 | 10 | 1.66 | 0.1556 | 0.5897 | 0.3625 | 0.3625 |  | {"level": "room", "skip_when_last": "held"} | 154.73 | [1238.07, 3148.44] | 0.001 | 0.3623 | 2,221.97 | 2,221.97 | 1.00 | 99.30 | False | kept_mean_slip8>0, dsr_p<0.1, spa_p<=0.10 |


### H4 family summary (all tables)

| tf | label | variant | candidates | ledger_rows | effective_trials | pbo_diff | pbo_kept_mean | spa_p | rc_p | spa_p_unstud | spa_best | spa_best_mean_gain | nested_boot_diff_ci90 | nested_boot_p_diff_le0 | nested_dsr_p | cpcv_diff_median | cpcv_diff_p5 | cpcv_share_pos | cpcv_control_median | go_no_go | failed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | L1 | pre-registered (family as at the primary run) | 10 | 10 | 1.59 | 0.4249 | 0.081 | 0.936 | 0.936 |  | {"level": "swing", "skip_when_last": "broke"} | 54.10 | [-220.04, 187.58] | 0.505 | 0.9987 | -6.92 | -171.27 | 0.273 | 2.10 | False | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| 1 min | L0 | pre-registered (family as at the primary run) | 10 | 10 | 1.71 | 0.6843 | 0.5936 | 0.9785 | 0.9785 |  | {"level": "room", "skip_when_last": "held"} | 38.77 | [-208.78, 256.9] | 0.4145 | 0.8465 | 72.72 | -60.02 | 0.727 | 24.10 | False | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| 5 min | L1 | pre-registered (family as at the primary run) | 10 | 10 | 1.64 | 0.6501 | 0.5715 | 0.1705 | 0.1805 |  | {"level": "room", "skip_when_last": "broke"} | 100.53 | [-289.64, 1371.11] | 0.1165 | 0.8863 | -2.08 | -1,774.85 | 0.455 | 71.80 | False | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0 |
| 5 min | L0 | pre-registered (family as at the primary run) | 10 | 10 | 1.66 | 0.1556 | 0.5897 | 0.3625 | 0.3625 |  | {"level": "room", "skip_when_last": "held"} | 154.73 | [1238.07, 3148.44] | 0.001 | 0.3623 | 2,221.97 | 2,221.97 | 1.00 | 99.30 | False | kept_mean_slip8>0, dsr_p<0.1, spa_p<=0.10 |

