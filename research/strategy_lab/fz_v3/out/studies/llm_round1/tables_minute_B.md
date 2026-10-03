# LLM round 1, labelled tables: minute / half B (harness blocks 6-11; IS only; label L1)

**Study** `llm_round1` step 1 (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1: cross-fitted halves; Judge 2: the family size is the number of labelled cells shown). **Rows**: 2,044 L1 units of the minute table (Strategy 1 rules + ST7 card) in 254 sessions, 2023-11-07 .. 2025-12-31 (SETUP dates; the half is time-contiguous). Label = L1 net INR per trade (the 15:25 intraday book, lot 65, 5 pts slippage per side, charges included; every skipped trade saves ~1,050 INR of costs, so net alone is never the criterion). Nothing from OOS; no raw rows.

**SHORTLIST STATE.** The frozen feature shortlist (`features_shortlist/minute/shortlist.json`, sha256 `66f6e004bd93e47c...`) has `n_shortlisted = 0` and `allowed_columns = []`: **the EMPTY-SHORTLIST RULE applies**. The tables cover `hour_bin`, `fz_read`, `dir` (always included) plus an **exploratory vocabulary labelled "outside the frozen shortlist"**: the representative of each of the top-8 clusters by log-loss MDA rank of the importance study (none of which passes the shortlist rule; their MDA mean is below one std) and the columns of the design's four two-way tables. Every rule written from these tables is exploratory and must say so in its reason; a candidate frozen from them carries the provenance `{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` for the user to accept or reject. Every labelled cell below counts toward the family size of the scorer's max-T exactly as a shortlisted cell would.

**Family size of this file: 181 labelled cells** (count >= 5: mean net and win rate printed; 23 cells with 1-4 units show the count only ('·') and are not labelled; 39 empty cells). Base rate of the half (one labelled cell): n 2,044, mean net **-1,071** INR, win rate **0.154**.

## What the proposer may do with these tables

- Write at most 8 **skip** rules for `minute`, each a conjunction of <= 3 comparisons `[column, op, value]` with ops `>=`, `>`, `<=`, `<`, `==`, `!=`, `in`, `not_in`; a None / NaN value never fires a comparison (the SETUP is kept).
- **Columns**: only the columns shown in this file (the vocabulary table below), or a listed interaction pair (section at the end). Numeric **thresholds must be values printed as decile edges / bucket boundaries / levels** of that column in this file (or a listed split point of an interaction pair); text comparisons use the printed levels.
- Read this half only. Your rules are scored on the OTHER half (A, blocks 0-5) through the harness; the scorer's family for the max-T is the 181 labelled cells of this file plus every rule proposed (round 0 and round 1), so a rule has to beat the best of everything you could have picked here, not just the other 7 rules.
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
| 09 | 172 | 0.084 | -525 | 0.250 |
| 10 | 285 | 0.139 | -848 | 0.172 |
| 11 | 321 | 0.157 | -1,136 | 0.146 |
| 12 | 333 | 0.163 | -1,221 | 0.114 |
| 13 | 343 | 0.168 | -1,115 | 0.137 |
| 14 | 365 | 0.179 | -1,046 | 0.162 |
| 15 | 108 | 0.053 | -1,138 | 0.157 |
| <09:25 | 91 | 0.044 | -1,839 | 0.154 |
| >=15:20 | 26 | 0.013 | -1,182 | 0.000 |

### `fz_read` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| ACCEPTED | 70 | 0.034 | -1,107 | 0.100 |
| FIRST_PRINT | 59 | 0.029 | -1,351 | 0.068 |
| HUNT | 1 | 0.001 | · | · |
| LEAVE | 800 | 0.391 | -1,003 | 0.168 |
| NEW | 144 | 0.070 | -904 | 0.132 |
| PENDING | 622 | 0.304 | -1,188 | 0.167 |
| RECYCLE | 39 | 0.019 | -690 | 0.154 |
| REJECT | 66 | 0.032 | -1,088 | 0.136 |
| THIN | 243 | 0.119 | -1,065 | 0.128 |

### `dir` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 1,008 | 0.493 | -1,091 | 0.145 |
| up | 1,036 | 0.507 | -1,050 | 0.162 |

### `room_ahead_dist_atr` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 0.171, 0.3559, 0.5496, 0.7863, 1.0181, 1.3011, 1.7067, 2.2388, 3.605. NA rows: 184.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 0.171 | 186 | 0.091 | -1,179 | 0.156 |
| [0.171, 0.3559) | 186 | 0.091 | -890 | 0.161 |
| [0.3559, 0.5496) | 186 | 0.091 | -963 | 0.194 |
| [0.5496, 0.7863) | 186 | 0.091 | -1,112 | 0.124 |
| [0.7863, 1.0181) | 186 | 0.091 | -920 | 0.194 |
| [1.0181, 1.3011) | 186 | 0.091 | -1,200 | 0.140 |
| [1.3011, 1.7067) | 186 | 0.091 | -918 | 0.118 |
| [1.7067, 2.2388) | 186 | 0.091 | -1,261 | 0.102 |
| [2.2388, 3.605) | 186 | 0.091 | -857 | 0.188 |
| >= 3.605 | 186 | 0.091 | -1,296 | 0.140 |
| NA | 184 | 0.090 | -1,182 | 0.174 |

### `touch_room_bars_ago` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 1.0, 3.0, 10.0, 15.0, 20.0, 28.0, 38.0. NA rows: 330.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 1.0 | 0 | 0.000 | · | · |
| [1.0, 3.0) | 649 | 0.318 | -1,066 | 0.154 |
| [3.0, 10.0) | 196 | 0.096 | -1,164 | 0.128 |
| [10.0, 15.0) | 172 | 0.084 | -1,320 | 0.122 |
| [15.0, 20.0) | 160 | 0.078 | -675 | 0.231 |
| [20.0, 28.0) | 192 | 0.094 | -1,183 | 0.146 |
| [28.0, 38.0) | 170 | 0.083 | -614 | 0.176 |
| >= 38.0 | 175 | 0.086 | -1,422 | 0.114 |
| NA | 330 | 0.161 | -1,070 | 0.161 |

### `card_first_bars` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 10.0, 11.0, 12.0, 13.0, 14.0, 16.0, 18.0, 21.0, 27.0. NA rows: 535.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 10.0 | 0 | 0.000 | · | · |
| [10.0, 11.0) | 241 | 0.118 | -1,098 | 0.145 |
| [11.0, 12.0) | 181 | 0.089 | -1,487 | 0.116 |
| [12.0, 13.0) | 154 | 0.075 | -1,008 | 0.156 |
| [13.0, 14.0) | 119 | 0.058 | -921 | 0.202 |
| [14.0, 16.0) | 166 | 0.081 | -1,130 | 0.157 |
| [16.0, 18.0) | 161 | 0.079 | -1,093 | 0.149 |
| [18.0, 21.0) | 157 | 0.077 | -1,202 | 0.146 |
| [21.0, 27.0) | 171 | 0.084 | -1,125 | 0.170 |
| >= 27.0 | 159 | 0.078 | -982 | 0.145 |
| NA | 535 | 0.262 | -914 | 0.159 |

### `ffd_close_dstar` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 2.4785, 2.4828, 2.4864, 2.4923, 2.4993, 2.5095, 2.5122, 2.5148, 2.522. NA rows: 0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 2.4785 | 206 | 0.101 | -829 | 0.141 |
| [2.4785, 2.4828) | 203 | 0.099 | -1,161 | 0.153 |
| [2.4828, 2.4864) | 204 | 0.100 | -623 | 0.186 |
| [2.4864, 2.4923) | 207 | 0.101 | -1,285 | 0.135 |
| [2.4923, 2.4993) | 202 | 0.099 | -1,200 | 0.163 |
| [2.4993, 2.5095) | 203 | 0.099 | -850 | 0.177 |
| [2.5095, 2.5122) | 208 | 0.102 | -1,410 | 0.115 |
| [2.5122, 2.5148) | 203 | 0.099 | -1,330 | 0.103 |
| [2.5148, 2.522) | 202 | 0.099 | -1,198 | 0.158 |
| >= 2.522 | 206 | 0.101 | -819 | 0.204 |
| NA | 0 | 0.000 | · | · |

### `card_last_reject_dir` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 668 | 0.327 | -1,113 | 0.157 |
| up | 699 | 0.342 | -1,169 | 0.142 |
| NA | 677 | 0.331 | -927 | 0.163 |

### `last_bos_dir` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 963 | 0.471 | -1,102 | 0.158 |
| up | 1,081 | 0.529 | -1,042 | 0.150 |

### `touch_swing_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 1,215 | 0.594 | -1,071 | 0.172 |
| held | 4 | 0.002 | · | · |
| pending | 825 | 0.404 | -1,082 | 0.125 |

### `n_choch_since_bos` (nchoch; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 5.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 | 533 | 0.261 | -1,064 | 0.137 |
| 1 | 805 | 0.394 | -1,018 | 0.154 |
| 2 | 388 | 0.190 | -1,158 | 0.173 |
| 3 | 173 | 0.085 | -1,079 | 0.150 |
| 4 | 73 | 0.036 | -1,033 | 0.151 |
| >=5 | 72 | 0.035 | -1,254 | 0.181 |

### `hv3_dir_agree` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| False | 720 | 0.352 | -1,064 | 0.144 |
| True | 1,017 | 0.498 | -1,156 | 0.145 |
| NA | 307 | 0.150 | -803 | 0.202 |

### `hv3_bars_since` (hv3b; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 5.0, 6.0, 15.0, 16.0, 60.0, 61.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 bars | 330 | 0.161 | -1,359 | 0.148 |
| 1-5 bars | 242 | 0.118 | -1,136 | 0.153 |
| 6-15 bars | 458 | 0.224 | -1,096 | 0.146 |
| 16-60 bars | 646 | 0.316 | -1,043 | 0.138 |
| >=61 bars | 61 | 0.030 | -695 | 0.164 |
| NA (no bar with vol_ratio20 >= 3 in the session so far) | 307 | 0.150 | -803 | 0.202 |

### `fz_visit_n` (visit; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 1.0, 2.0, 3.0, 4.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 1 | 321 | 0.157 | -1,205 | 0.156 |
| 2 | 272 | 0.133 | -1,017 | 0.151 |
| 3 | 213 | 0.104 | -1,130 | 0.141 |
| >=4 | 703 | 0.344 | -1,131 | 0.154 |
| NA (no ref room) | 535 | 0.262 | -914 | 0.159 |

## Two-way tables (cell = mean net INR / win rate / n; '·' = fewer than 5 units, count only)

### `fz_read` (rows) x `hour_bin` (columns)

| fz_read \ hour_bin | 09 | 10 | 11 | 12 | 13 | 14 | 15 | <09:25 | >=15:20 |
|---|---|---|---|---|---|---|---|---|---|
| ACCEPTED | · / · / 1 | · / · / 2 | -1,034 / 0.100 / 10 | -1,572 / 0.000 / 19 | -1,308 / 0.105 / 19 | -368 / 0.250 / 12 | · / · / 3 | · / · / 1 | · / · / 3 |
| FIRST_PRINT | -676 / 0.200 / 5 | -1,878 / 0.000 / 11 | -656 / 0.286 / 7 | -1,381 / 0.000 / 7 | -1,311 / 0.000 / 5 | -1,549 / 0.050 / 20 | · / · / 2 | · / · / 1 | · / · / 1 |
| HUNT | 0 | 0 | 0 | 0 | · / · / 1 | 0 | 0 | 0 | 0 |
| LEAVE | -242 / 0.274 / 95 | -778 / 0.218 / 119 | -957 / 0.128 / 117 | -1,524 / 0.073 / 124 | -1,188 / 0.165 / 109 | -1,054 / 0.171 / 152 | -1,304 / 0.150 / 40 | -920 / 0.229 / 35 | -1,267 / 0.000 / 9 |
| NEW | -1,740 / 0.143 / 7 | 1,562 / 0.167 / 24 | -1,832 / 0.000 / 17 | -1,350 / 0.115 / 26 | -1,148 / 0.125 / 24 | 123 / 0.273 / 22 | -868 / 0.125 / 8 | -4,129 / 0.077 / 13 | · / · / 3 |
| PENDING | -1,264 / 0.188 / 48 | -1,205 / 0.165 / 103 | -1,229 / 0.190 / 100 | -1,078 / 0.163 / 98 | -1,115 / 0.143 / 105 | -1,206 / 0.158 / 95 | -862 / 0.265 / 34 | -1,758 / 0.118 / 34 | -1,033 / 0.000 / 5 |
| RECYCLE | · / · / 4 | · / · / 2 | -644 / 0.167 / 6 | · / · / 3 | 117 / 0.200 / 15 | -308 / 0.200 / 5 | · / · / 3 | · / · / 1 | 0 |
| REJECT | · / · / 2 | -1,424 / 0.000 / 5 | -1,321 / 0.111 / 9 | -495 / 0.188 / 16 | -576 / 0.222 / 9 | -1,560 / 0.062 / 16 | -1,107 / 0.167 / 6 | · / · / 1 | · / · / 2 |
| THIN | 1,383 / 0.400 / 10 | -1,442 / 0.105 / 19 | -1,233 / 0.145 / 55 | -607 / 0.175 / 40 | -1,274 / 0.071 / 56 | -1,113 / 0.140 / 43 | -1,390 / 0.000 / 12 | -2,742 / 0.000 / 5 | · / · / 3 |

### `n_choch_since_bos` (rows) x `dir` (columns)

| n_choch_since_bos \ dir | down | up |
|---|---|---|
| 0 | -1,268 / 0.125 / 248 | -887 / 0.147 / 285 |
| 1 | -1,018 / 0.134 / 417 | -1,019 / 0.175 / 388 |
| 2 | -1,118 / 0.174 / 195 | -1,198 / 0.171 / 193 |
| >=3 | -969 / 0.169 / 148 | -1,229 / 0.147 / 170 |

### `hv3_dir_agree` (rows) x `hv3_bars_since` (columns)

| hv3_dir_agree \ hv3_bars_since | 0 bars | 1-5 bars | 6-15 bars | 16-60 bars | >=61 bars | NA (no bar with vol_ratio20 >= 3 in the session so far) |
|---|---|---|---|---|---|---|
| False | -833 / 0.200 / 5 | -1,076 / 0.163 / 98 | -1,172 / 0.129 / 233 | -1,013 / 0.146 / 356 | -797 / 0.179 / 28 | 0 |
| True | -1,368 / 0.148 / 325 | -1,178 / 0.146 / 144 | -1,016 / 0.164 / 225 | -1,080 / 0.128 / 290 | -608 / 0.151 / 33 | 0 |
| NA | 0 | 0 | 0 | 0 | 0 | -803 / 0.202 / 307 |

### `fz_visit_n` (rows) x `fz_read` (columns)

| fz_visit_n \ fz_read | ACCEPTED | FIRST_PRINT | HUNT | LEAVE | NEW | PENDING | RECYCLE | REJECT | THIN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | -1,351 / 0.068 / 59 | 0 | -1,668 / 0.118 / 34 | 0 | -1,152 / 0.179 / 224 | 0 | · / · / 4 | 0 |
| 2 | -990 / 0.100 / 20 | 0 | 0 | -797 / 0.193 / 83 | 0 | -1,228 / 0.134 / 97 | -1,279 / 0.111 / 9 | -1,361 / 0.100 / 10 | -878 / 0.151 / 53 |
| 3 | -1,594 / 0.000 / 16 | 0 | 0 | -651 / 0.196 / 56 | 0 | -1,123 / 0.156 / 77 | -1,702 / 0.000 / 7 | -1,284 / 0.111 / 9 | -1,436 / 0.125 / 48 |
| >=4 | -946 / 0.147 / 34 | 0 | · / · / 1 | -1,203 / 0.157 / 236 | 0 | -1,230 / 0.174 / 224 | -151 / 0.217 / 23 | -1,266 / 0.116 / 43 | -1,010 / 0.120 / 142 |
| NA (no ref room) | 0 | 0 | 0 | -918 / 0.169 / 391 | -904 / 0.132 / 144 | 0 | 0 | 0 | 0 |

## Listed interaction pairs (from the frozen shortlist; the only depth-2/3 conjunctions allowed beyond the columns above)

| feature a | feature b | split points a | split points b | status |
|---|---|---|---|---|
| `sl` | `ffd_close_dstar` | 24640.0, 24655.0, 24661.0 | 2.4046, 2.4166, 2.5029, 2.5142 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `sl` | `n_events_asof` | 18146.0, 24640.0, 24651.1992, 26025.8008 | 18033.0, 23656.0, 28203.0, 32889.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `card_this_bars` | `sl` | 3.0, 6.0, 11.0 | 18127.8496, 24661.0, 26025.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `room_ahead_dist_atr` | `room_behind_dist_atr` | 0.0125, 0.9548, 14.4066, 17.8071 | 0.18, 0.5243, 0.6324, 9.3641 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `card_vol_ratio` | `room_behind_dist_atr` | 0.0289, 0.0493, 0.0691 | 0.006, 0.1561, 0.18 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |

Generated 2026-09-29T12:36:07 by `studies/llm_round1/tables.py` from `harness.load('minute')` (label L1) and `features_ext/minute/ext_features.parquet`. Definitions: `r1_common.py` docstring. Family size for the max-T = **181** labelled cells.
