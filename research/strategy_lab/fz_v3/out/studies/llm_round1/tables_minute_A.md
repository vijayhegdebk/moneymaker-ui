# LLM round 1, labelled tables: minute / half A (harness blocks 0-5; IS only; label L1)

**Study** `llm_round1` step 1 (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1: cross-fitted halves; Judge 2: the family size is the number of labelled cells shown). **Rows**: 2,408 L1 units of the minute table (Strategy 1 rules + ST7 card) in 324 sessions, 2021-10-01 .. 2023-11-06 (SETUP dates; the half is time-contiguous). Label = L1 net INR per trade (the 15:25 intraday book, lot 65, 5 pts slippage per side, charges included; every skipped trade saves ~1,050 INR of costs, so net alone is never the criterion). Nothing from OOS; no raw rows.

**SHORTLIST STATE.** The frozen feature shortlist (`features_shortlist/minute/shortlist.json`, sha256 `66f6e004bd93e47c...`) has `n_shortlisted = 0` and `allowed_columns = []`: **the EMPTY-SHORTLIST RULE applies**. The tables cover `hour_bin`, `fz_read`, `dir` (always included) plus an **exploratory vocabulary labelled "outside the frozen shortlist"**: the representative of each of the top-8 clusters by log-loss MDA rank of the importance study (none of which passes the shortlist rule; their MDA mean is below one std) and the columns of the design's four two-way tables. Every rule written from these tables is exploratory and must say so in its reason; a candidate frozen from them carries the provenance `{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` for the user to accept or reject. Every labelled cell below counts toward the family size of the scorer's max-T exactly as a shortlisted cell would.

**Family size of this file: 184 labelled cells** (count >= 5: mean net and win rate printed; 21 cells with 1-4 units show the count only ('·') and are not labelled; 39 empty cells). Base rate of the half (one labelled cell): n 2,408, mean net **-958** INR, win rate **0.158**.

## What the proposer may do with these tables

- Write at most 8 **skip** rules for `minute`, each a conjunction of <= 3 comparisons `[column, op, value]` with ops `>=`, `>`, `<=`, `<`, `==`, `!=`, `in`, `not_in`; a None / NaN value never fires a comparison (the SETUP is kept).
- **Columns**: only the columns shown in this file (the vocabulary table below), or a listed interaction pair (section at the end). Numeric **thresholds must be values printed as decile edges / bucket boundaries / levels** of that column in this file (or a listed split point of an interaction pair); text comparisons use the printed levels.
- Read this half only. Your rules are scored on the OTHER half (B, blocks 6-11) through the harness; the scorer's family for the max-T is the 184 labelled cells of this file plus every rule proposed (round 0 and round 1), so a rule has to beat the best of everything you could have picked here, not just the other 7 rules.
- Columns ending `_pts`, `atr14`, `fz_band_width`, `gap_pts`, `days_to_expiry` drift with the price level / the calendar inside IS (null_tapes_drift study): prefer `_atr` / `_bps` / count / read forms. `n_events_asof` and `sl` are calendar-time proxies and are refused.
- For each rule give the reason in the user's words and the table cells that motivated it (`"cells": ["one_way:<column>:<bin label>", "two_way:<a>x<b>:<row label>|<col label>"]`).

## Vocabulary shown in this file

| column | kind | provenance | how it is shown (swap rule) | caveats |
|---|---|---|---|---|
| `hour_bin` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `fz_read` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `dir` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `room_ahead_dist_atr` | decile | outside the frozen shortlist: importance cluster 7, log-loss MDA rank 1 of 38 (MDA mean 0.00030, std 0.00059; the cluster does NOT pass the shortlist rule) | representative `card_read=PENDING` not shown (`card_read=PENDING`: source column `fz_read` already shown (`card_read` == `fz_read` on every IS row)); shown through the highest-MDI admissible member `room_ahead_dist_atr` (MDI 0.00847) -> column `room_ahead_dist_atr` | - |
| `touch_room_bars_ago` | decile | outside the frozen shortlist: importance cluster 11, log-loss MDA rank 2 of 38 (MDA mean 0.00016, std 0.00048; the cluster does NOT pass the shortlist rule) | representative `card_read=ACCEPTED` not shown (`card_read=ACCEPTED`: source column `fz_read` already shown (`card_read` == `fz_read` on every IS row)); shown through the highest-MDI admissible member `touch_room_bars_ago` (MDI 0.00578) -> column `touch_room_bars_ago` | - |
| `card_first_bars` | decile | outside the frozen shortlist: importance cluster 13, log-loss MDA rank 3 of 38 (MDA mean 0.00008, std 0.00011; the cluster does NOT pass the shortlist rule) | representative `card_read=FIRST_PRINT` not shown (`card_read=FIRST_PRINT`: source column `fz_read` already shown (`card_read` == `fz_read` on every IS row)); shown through the highest-MDI admissible member `card_first_bars` (MDI 0.00359) -> column `card_first_bars` | - |
| `ffd_close_dstar` | decile | outside the frozen shortlist: importance cluster 15, log-loss MDA rank 4 of 38 (MDA mean 0.00002, std 0.00005; the cluster does NOT pass the shortlist rule) | representative `n_events_asof` not shown (`n_events_asof`: calendar-time proxy (drift.json time_proxies), refused; `sl`: calendar-time proxy (drift.json time_proxies), refused); shown through the highest-MDI admissible member `ffd_close_dstar` (MDI 0.00483) -> column `ffd_close_dstar` | extended as-of column (features_ext): not a features.parquet column; a rule on it needs a new per-bar routine in the lab (a user decision, never assumed); FFD of the log close at d* = 0.2 keeps most of the price level: the importance study calls it a calendar-time proxy and did not adopt FFD (MDA <= 1 std on both timeframes); a rule on it is a level rule and must hold inside every period |
| `card_last_reject_dir` | level | outside the frozen shortlist: importance cluster 9, log-loss MDA rank 5 of 38 (MDA mean 0.00001, std 0.00025; the cluster does NOT pass the shortlist rule) | representative `card_last_reject_dir=nan` is a one-hot level: its source column `card_last_reject_dir` is shown by level | - |
| `last_bos_dir` | level | outside the frozen shortlist: importance cluster 8, log-loss MDA rank 6 of 38 (MDA mean 0.00000, std 0.00000; the cluster does NOT pass the shortlist rule) | representative `last_bos_dir=none` is a one-hot level: its source column `last_bos_dir` is shown by level | - |
| `touch_swing_last` | level | outside the frozen shortlist: importance cluster 37, log-loss MDA rank 7 of 38 (MDA mean 0.00000, std 0.00000; the cluster does NOT pass the shortlist rule) | representative `touch_swing_last=held` is a one-hot level: its source column `touch_swing_last` is shown by level | - |
| (none) | - | outside the frozen shortlist: importance cluster 33, log-loss MDA rank 8 of 38 (MDA mean 0.00000, std 0.00000; the cluster does NOT pass the shortlist rule) | `hour_bin=>=15:20`: source column `hour_bin` already shown | no admissible member: the cluster is covered by tables already shown; zero own cells |
| `n_choch_since_bos` | nchoch | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `hv3_dir_agree` | level | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `hv3_bars_since` | hv3b | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `fz_visit_n` | visit | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |

Exact duplicates on every IS row (checked at run time): `card_read` == `fz_read`.

## One-way tables (per column: bin, count, share of the half, mean L1 net INR, win rate)

### `hour_bin` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 09 | 197 | 0.082 | -999 | 0.173 |
| 10 | 307 | 0.128 | -888 | 0.189 |
| 11 | 356 | 0.148 | -1,095 | 0.096 |
| 12 | 407 | 0.169 | -1,146 | 0.128 |
| 13 | 421 | 0.175 | -886 | 0.145 |
| 14 | 443 | 0.184 | -973 | 0.185 |
| 15 | 150 | 0.062 | -1,044 | 0.173 |
| <09:25 | 98 | 0.041 | 82 | 0.337 |
| >=15:20 | 29 | 0.012 | -975 | 0.000 |

### `fz_read` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| ACCEPTED | 71 | 0.029 | -1,186 | 0.113 |
| FIRST_PRINT | 62 | 0.026 | -1,031 | 0.161 |
| HUNT | 1 | 0.000 | · | · |
| LEAVE | 934 | 0.388 | -899 | 0.187 |
| NEW | 162 | 0.067 | -766 | 0.123 |
| PENDING | 737 | 0.306 | -994 | 0.170 |
| RECYCLE | 54 | 0.022 | -430 | 0.111 |
| REJECT | 92 | 0.038 | -1,060 | 0.098 |
| THIN | 295 | 0.122 | -1,151 | 0.091 |

### `dir` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 1,201 | 0.499 | -947 | 0.154 |
| up | 1,207 | 0.501 | -968 | 0.162 |

### `room_ahead_dist_atr` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 0.2125, 0.4458, 0.6662, 0.8849, 1.1538, 1.4782, 1.8541, 2.4394, 3.538. NA rows: 196.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 0.2125 | 221 | 0.092 | -993 | 0.163 |
| [0.2125, 0.4458) | 222 | 0.092 | -922 | 0.144 |
| [0.4458, 0.6662) | 221 | 0.092 | -906 | 0.195 |
| [0.6662, 0.8849) | 221 | 0.092 | -798 | 0.190 |
| [0.8849, 1.1538) | 221 | 0.092 | -1,079 | 0.149 |
| [1.1538, 1.4782) | 221 | 0.092 | -989 | 0.140 |
| [1.4782, 1.8541) | 221 | 0.092 | -1,187 | 0.109 |
| [1.8541, 2.4394) | 221 | 0.092 | -1,085 | 0.136 |
| [2.4394, 3.538) | 221 | 0.092 | -896 | 0.140 |
| >= 3.538 | 222 | 0.092 | -866 | 0.167 |
| NA | 196 | 0.081 | -799 | 0.209 |

### `touch_room_bars_ago` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 1.0, 3.0, 9.0, 14.0, 20.0, 27.0, 38.0. NA rows: 411.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 1.0 | 0 | 0.000 | · | · |
| [1.0, 3.0) | 791 | 0.329 | -852 | 0.154 |
| [3.0, 9.0) | 190 | 0.079 | -1,034 | 0.168 |
| [9.0, 14.0) | 169 | 0.070 | -966 | 0.160 |
| [14.0, 20.0) | 227 | 0.094 | -1,152 | 0.150 |
| [20.0, 27.0) | 206 | 0.086 | -1,114 | 0.150 |
| [27.0, 38.0) | 203 | 0.084 | -1,420 | 0.123 |
| >= 38.0 | 211 | 0.088 | -835 | 0.161 |
| NA | 411 | 0.171 | -772 | 0.182 |

### `card_first_bars` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 10.0, 11.0, 12.0, 13.0, 14.0, 16.0, 18.0, 22.0, 28.0. NA rows: 649.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 10.0 | 0 | 0.000 | · | · |
| [10.0, 11.0) | 318 | 0.132 | -1,277 | 0.116 |
| [11.0, 12.0) | 147 | 0.061 | -677 | 0.157 |
| [12.0, 13.0) | 180 | 0.075 | -1,057 | 0.144 |
| [13.0, 14.0) | 131 | 0.054 | -1,048 | 0.168 |
| [14.0, 16.0) | 244 | 0.101 | -754 | 0.193 |
| [16.0, 18.0) | 159 | 0.066 | -1,134 | 0.132 |
| [18.0, 22.0) | 208 | 0.086 | -706 | 0.188 |
| [22.0, 28.0) | 191 | 0.079 | -1,008 | 0.152 |
| >= 28.0 | 181 | 0.075 | -902 | 0.160 |
| NA | 649 | 0.270 | -934 | 0.165 |

### `ffd_close_dstar` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 2.4083, 2.4185, 2.4221, 2.4265, 2.4295, 2.4321, 2.4351, 2.4412, 2.4506. NA rows: 16.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 2.4083 | 242 | 0.101 | -846 | 0.207 |
| [2.4083, 2.4185) | 233 | 0.097 | -903 | 0.184 |
| [2.4185, 2.4221) | 242 | 0.101 | -872 | 0.190 |
| [2.4221, 2.4265) | 236 | 0.098 | -927 | 0.161 |
| [2.4265, 2.4295) | 244 | 0.101 | -827 | 0.156 |
| [2.4295, 2.4321) | 239 | 0.099 | -1,060 | 0.142 |
| [2.4321, 2.4351) | 242 | 0.101 | -916 | 0.161 |
| [2.4351, 2.4412) | 242 | 0.101 | -1,030 | 0.149 |
| [2.4412, 2.4506) | 233 | 0.097 | -1,149 | 0.090 |
| >= 2.4506 | 239 | 0.099 | -1,055 | 0.130 |
| NA | 16 | 0.007 | -970 | 0.250 |

### `card_last_reject_dir` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 813 | 0.338 | -963 | 0.150 |
| up | 813 | 0.338 | -912 | 0.162 |
| NA | 782 | 0.325 | -1,000 | 0.161 |

### `last_bos_dir` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 1,196 | 0.497 | -939 | 0.161 |
| none | 2 | 0.001 | · | · |
| up | 1,210 | 0.502 | -975 | 0.155 |

### `touch_swing_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 1,521 | 0.632 | -928 | 0.168 |
| held | 1 | 0.000 | · | · |
| pending | 886 | 0.368 | -1,006 | 0.140 |

### `n_choch_since_bos` (nchoch; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 5.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 | 636 | 0.264 | -1,111 | 0.138 |
| 1 | 934 | 0.388 | -980 | 0.161 |
| 2 | 435 | 0.181 | -916 | 0.175 |
| 3 | 199 | 0.083 | -627 | 0.161 |
| 4 | 105 | 0.044 | -637 | 0.191 |
| >=5 | 99 | 0.041 | -951 | 0.141 |

### `hv3_dir_agree` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| False | 791 | 0.329 | -969 | 0.161 |
| True | 1,235 | 0.513 | -991 | 0.144 |
| NA | 382 | 0.159 | -825 | 0.196 |

### `hv3_bars_since` (hv3b; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 5.0, 6.0, 15.0, 16.0, 60.0, 61.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 bars | 446 | 0.185 | -864 | 0.184 |
| 1-5 bars | 227 | 0.094 | -932 | 0.189 |
| 6-15 bars | 451 | 0.187 | -921 | 0.149 |
| 16-60 bars | 818 | 0.340 | -1,104 | 0.127 |
| >=61 bars | 84 | 0.035 | -899 | 0.107 |
| NA (no bar with vol_ratio20 >= 3 in the session so far) | 382 | 0.159 | -825 | 0.196 |

### `fz_visit_n` (visit; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 1.0, 2.0, 3.0, 4.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 1 | 330 | 0.137 | -1,006 | 0.151 |
| 2 | 351 | 0.146 | -829 | 0.191 |
| 3 | 260 | 0.108 | -1,161 | 0.135 |
| >=4 | 818 | 0.340 | -948 | 0.148 |
| NA (no ref room) | 649 | 0.270 | -934 | 0.165 |

## Two-way tables (cell = mean net INR / win rate / n; '·' = fewer than 5 units, count only)

### `fz_read` (rows) x `hour_bin` (columns)

| fz_read \ hour_bin | 09 | 10 | 11 | 12 | 13 | 14 | 15 | <09:25 | >=15:20 |
|---|---|---|---|---|---|---|---|---|---|
| ACCEPTED | · / · / 4 | -1,383 / 0.000 / 6 | -1,351 / 0.059 / 17 | -1,083 / 0.188 / 16 | -1,146 / 0.077 / 13 | -968 / 0.200 / 10 | · / · / 3 | 0 | · / · / 2 |
| FIRST_PRINT | · / · / 2 | -1,235 / 0.125 / 8 | -1,423 / 0.000 / 13 | -1,459 / 0.091 / 11 | -638 / 0.250 / 12 | -622 / 0.286 / 14 | · / · / 1 | 0 | · / · / 1 |
| HUNT | 0 | 0 | 0 | · / · / 1 | 0 | 0 | 0 | 0 | 0 |
| LEAVE | -1,166 / 0.198 / 106 | -528 / 0.266 / 124 | -1,048 / 0.128 / 125 | -1,084 / 0.159 / 151 | -700 / 0.208 / 144 | -1,045 / 0.163 / 153 | -1,009 / 0.147 / 75 | -209 / 0.326 / 46 | -942 / 0.000 / 10 |
| NEW | -840 / 0.188 / 16 | -1,456 / 0.000 / 12 | -911 / 0.091 / 22 | -1,067 / 0.040 / 25 | -836 / 0.098 / 41 | -721 / 0.174 / 23 | -1,308 / 0.000 / 11 | 2,461 / 0.667 / 9 | · / · / 3 |
| PENDING | -554 / 0.164 / 55 | -1,102 / 0.173 / 104 | -862 / 0.140 / 93 | -1,144 / 0.151 / 119 | -1,270 / 0.091 / 121 | -961 / 0.217 / 161 | -1,099 / 0.233 / 43 | -237 / 0.333 / 33 | -991 / 0.000 / 8 |
| RECYCLE | · / · / 1 | · / · / 4 | -1,527 / 0.000 / 13 | -951 / 0.000 / 11 | 148 / 0.222 / 9 | 141 / 0.222 / 9 | · / · / 1 | · / · / 4 | · / · / 2 |
| REJECT | · / · / 4 | -1,458 / 0.000 / 11 | -1,300 / 0.000 / 14 | -1,026 / 0.105 / 19 | -658 / 0.174 / 23 | -1,197 / 0.083 / 12 | -495 / 0.333 / 6 | · / · / 1 | · / · / 2 |
| THIN | -1,504 / 0.000 / 9 | -992 / 0.132 / 38 | -1,341 / 0.034 / 59 | -1,381 / 0.056 / 54 | -824 / 0.103 / 58 | -1,119 / 0.147 / 61 | -1,105 / 0.200 / 10 | -1,427 / 0.000 / 5 | · / · / 1 |

### `n_choch_since_bos` (rows) x `dir` (columns)

| n_choch_since_bos \ dir | down | up |
|---|---|---|
| 0 | -1,114 / 0.139 / 316 | -1,107 / 0.138 / 320 |
| 1 | -948 / 0.154 / 466 | -1,012 / 0.167 / 468 |
| 2 | -765 / 0.183 / 218 | -1,068 / 0.166 / 217 |
| >=3 | -881 / 0.144 / 201 | -538 / 0.183 / 202 |

### `hv3_dir_agree` (rows) x `hv3_bars_since` (columns)

| hv3_dir_agree \ hv3_bars_since | 0 bars | 1-5 bars | 6-15 bars | 16-60 bars | >=61 bars | NA (no bar with vol_ratio20 >= 3 in the session so far) |
|---|---|---|---|---|---|---|
| False | 1,314 / 0.125 / 8 | -1,165 / 0.151 / 73 | -792 / 0.203 / 231 | -1,086 / 0.143 / 433 | -853 / 0.130 / 46 | 0 |
| True | -904 / 0.185 / 438 | -822 / 0.208 / 154 | -1,055 / 0.091 / 220 | -1,126 / 0.109 / 385 | -955 / 0.079 / 38 | 0 |
| NA | 0 | 0 | 0 | 0 | 0 | -825 / 0.196 / 382 |

### `fz_visit_n` (rows) x `fz_read` (columns)

| fz_visit_n \ fz_read | ACCEPTED | FIRST_PRINT | HUNT | LEAVE | NEW | PENDING | RECYCLE | REJECT | THIN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | -1,031 / 0.161 / 62 | 0 | -1,307 / 0.125 / 24 | 0 | -969 / 0.151 / 238 | 0 | -1,030 / 0.167 / 6 | 0 |
| 2 | -1,200 / 0.148 / 27 | 0 | · / · / 1 | -723 / 0.238 / 101 | 0 | -841 / 0.206 / 136 | 761 / 0.200 / 10 | -1,104 / 0.062 / 16 | -988 / 0.133 / 60 |
| 3 | -1,502 / 0.000 / 13 | 0 | 0 | -689 / 0.239 / 71 | 0 | -1,250 / 0.155 / 84 | -1,168 / 0.000 / 11 | -1,437 / 0.095 / 21 | -1,425 / 0.050 / 60 |
| >=4 | -1,040 / 0.129 / 31 | 0 | 0 | -811 / 0.175 / 251 | 0 | -1,014 / 0.172 / 279 | -545 / 0.121 / 33 | -888 / 0.102 / 49 | -1,113 / 0.091 / 175 |
| NA (no ref room) | 0 | 0 | 0 | -990 / 0.179 / 487 | -766 / 0.123 / 162 | 0 | 0 | 0 | 0 |

## Listed interaction pairs (from the frozen shortlist; the only depth-2/3 conjunctions allowed beyond the columns above)

| feature a | feature b | split points a | split points b | status |
|---|---|---|---|---|
| `sl` | `ffd_close_dstar` | 24640.0, 24655.0, 24661.0 | 2.4046, 2.4166, 2.5029, 2.5142 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `sl` | `n_events_asof` | 18146.0, 24640.0, 24651.1992, 26025.8008 | 18033.0, 23656.0, 28203.0, 32889.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `card_this_bars` | `sl` | 3.0, 6.0, 11.0 | 18127.8496, 24661.0, 26025.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `room_ahead_dist_atr` | `room_behind_dist_atr` | 0.0125, 0.9548, 14.4066, 17.8071 | 0.18, 0.5243, 0.6324, 9.3641 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `card_vol_ratio` | `room_behind_dist_atr` | 0.0289, 0.0493, 0.0691 | 0.006, 0.1561, 0.18 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |

Generated 2026-09-29T12:36:06 by `studies/llm_round1/tables.py` from `harness.load('minute')` (label L1) and `features_ext/minute/ext_features.parquet`. Definitions: `r1_common.py` docstring. Family size for the max-T = **184** labelled cells.
