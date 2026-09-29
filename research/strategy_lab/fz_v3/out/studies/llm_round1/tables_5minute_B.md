# LLM round 1, labelled tables: 5minute / half B (harness blocks 6-11; IS only; label L1)

**Study** `llm_round1` step 1 (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1: cross-fitted halves; Judge 2: the family size is the number of labelled cells shown). **Rows**: 398 L1 units of the 5minute table (Strategy 2 rules + ST8 card) in 194 sessions, 2023-11-07 .. 2025-12-31 (SETUP dates; the half is time-contiguous). Label = L1 net INR per trade (the 15:25 intraday book, lot 65, 5 pts slippage per side, charges included; every skipped trade saves ~1,050 INR of costs, so net alone is never the criterion). Nothing from OOS; no raw rows.

**SHORTLIST STATE.** The frozen feature shortlist (`features_shortlist/5minute/shortlist.json`, sha256 `4747257f41ecb40f...`) has `n_shortlisted = 0` and `allowed_columns = []`: **the EMPTY-SHORTLIST RULE applies**. The tables cover `hour_bin`, `fz_read`, `dir` (always included) plus an **exploratory vocabulary labelled "outside the frozen shortlist"**: the representative of each of the top-8 clusters by log-loss MDA rank of the importance study (none of which passes the shortlist rule; their MDA mean is below one std) and the columns of the design's four two-way tables. Every rule written from these tables is exploratory and must say so in its reason; a candidate frozen from them carries the provenance `{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` for the user to accept or reject. Every labelled cell below counts toward the family size of the scorer's max-T exactly as a shortlisted cell would.

**Family size of this file: 118 labelled cells** (count >= 5: mean net and win rate printed; 46 cells with 1-4 units show the count only ('·') and are not labelled; 68 empty cells). Base rate of the half (one labelled cell): n 398, mean net **-843** INR, win rate **0.256**.

## What the proposer may do with these tables

- Write at most 8 **skip** rules for `5minute`, each a conjunction of <= 3 comparisons `[column, op, value]` with ops `>=`, `>`, `<=`, `<`, `==`, `!=`, `in`, `not_in`; a None / NaN value never fires a comparison (the SETUP is kept).
- **Columns**: only the columns shown in this file (the vocabulary table below), or a listed interaction pair (section at the end). Numeric **thresholds must be values printed as decile edges / bucket boundaries / levels** of that column in this file (or a listed split point of an interaction pair); text comparisons use the printed levels.
- Read this half only. Your rules are scored on the OTHER half (A, blocks 0-5) through the harness; the scorer's family for the max-T is the 118 labelled cells of this file plus every rule proposed (round 0 and round 1), so a rule has to beat the best of everything you could have picked here, not just the other 7 rules.
- Columns ending `_pts`, `atr14`, `fz_band_width`, `gap_pts`, `days_to_expiry` drift with the price level / the calendar inside IS (null_tapes_drift study): prefer `_atr` / `_bps` / count / read forms. `n_events_asof` and `sl` are calendar-time proxies and are refused.
- For each rule give the reason in the user's words and the table cells that motivated it (`"cells": ["one_way:<column>:<bin label>", "two_way:<a>x<b>:<row label>|<col label>"]`).

## Vocabulary shown in this file

| column | kind | provenance | how it is shown (swap rule) | caveats |
|---|---|---|---|---|
| `hour_bin` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `fz_read` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `dir` | level | always included (design: hour_bin, fz_read, dir) | as is | - |
| `touch_room_last` | level | outside the frozen shortlist: importance cluster 17, log-loss MDA rank 1 of 39 (MDA mean 0.00177, std 0.00710; the cluster does NOT pass the shortlist rule) | representative `touch_room_last=broke` is a one-hot level: its source column `touch_room_last` is shown by level | - |
| `fz_gate` | level | outside the frozen shortlist: importance cluster 7, log-loss MDA rank 2 of 39 (MDA mean 0.00050, std 0.00499; the cluster does NOT pass the shortlist rule) | representative `fz_gate=TAKE` is a one-hot level: its source column `fz_gate` is shown by level | - |
| `card_leave_kind` | level | outside the frozen shortlist: importance cluster 12, log-loss MDA rank 3 of 39 (MDA mean 0.00021, std 0.00160; the cluster does NOT pass the shortlist rule) | representative `card_read=LEAVE` not shown (`card_read=LEAVE`: source column `fz_read` already shown (`card_read` == `fz_read` on every IS row)); shown through the highest-MDI admissible member `card_leave_kind=normal` (MDI 0.00217) -> column `card_leave_kind` | - |
| `days_to_expiry` | decile | outside the frozen shortlist: importance cluster 22, log-loss MDA rank 4 of 39 (MDA mean 0.00009, std 0.00098; the cluster does NOT pass the shortlist rule) | as is | top-20 drifted column: shift 0.18 sd, higher in IS-late |
| `touch_prot_last` | level | outside the frozen shortlist: importance cluster 16, log-loss MDA rank 5 of 39 (MDA mean 0.00000, std 0.00355; the cluster does NOT pass the shortlist rule) | representative `touch_prot_last=held` is a one-hot level: its source column `touch_prot_last` is shown by level | - |
| `ffd_close_dstar` | decile | outside the frozen shortlist: importance cluster 21, log-loss MDA rank 6 of 39 (MDA mean 0.00000, std 0.00037; the cluster does NOT pass the shortlist rule) | representative `n_events_asof` not shown (`n_events_asof`: calendar-time proxy (drift.json time_proxies), refused); shown through the highest-MDI admissible member `ffd_close_dstar` (MDI 0.00472) -> column `ffd_close_dstar` | extended as-of column (features_ext): not a features.parquet column; a rule on it needs a new per-bar routine in the lab (a user decision, never assumed); FFD of the log close at d* = 0.2 keeps most of the price level: the importance study calls it a calendar-time proxy and did not adopt FFD (MDA <= 1 std on both timeframes); a rule on it is a level rule and must hold inside every period |
| `gap_pts` | na_indicator | outside the frozen shortlist: importance cluster 8, log-loss MDA rank 7 of 39 (MDA mean 0.00000, std 0.00000; the cluster does NOT pass the shortlist rule) | representative `gap_pts__na` is a missing indicator: `gap_pts` is shown as an NA indicator (NA / not NA) | top-20 drifted column: shift 0.013 sd, higher in IS-late |
| (none) | - | outside the frozen shortlist: importance cluster 38, log-loss MDA rank 8 of 39 (MDA mean 0.00000, std 0.00000; the cluster does NOT pass the shortlist rule) | `touch_prot_last=broke`: source column `touch_prot_last` already shown | no admissible member: the cluster is covered by tables already shown; zero own cells |
| `n_choch_since_bos` | nchoch | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `hv3_dir_agree` | level | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `hv3_bars_since` | hv3b | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |
| `fz_visit_n` | visit | outside the frozen shortlist: a column of the design's two-way tables (not in any top-8 cluster) | as is | - |

Exact duplicates on every IS row (checked at run time): `card_read` == `fz_read`.

## One-way tables (per column: bin, count, share of the half, mean L1 net INR, win rate)

### `hour_bin` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 09 | 51 | 0.128 | -1,024 | 0.275 |
| 10 | 67 | 0.168 | -1,273 | 0.269 |
| 11 | 46 | 0.116 | -670 | 0.239 |
| 12 | 61 | 0.153 | -641 | 0.246 |
| 13 | 69 | 0.173 | -687 | 0.275 |
| 14 | 63 | 0.158 | -385 | 0.270 |
| 15 | 19 | 0.048 | -1,301 | 0.158 |
| <09:25 | 21 | 0.053 | -1,454 | 0.238 |
| >=15:20 | 1 | 0.003 | · | · |

### `fz_read` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| ACCEPTED | 2 | 0.005 | · | · |
| FIRST_PRINT | 3 | 0.007 | · | · |
| HUNT | 4 | 0.010 | · | · |
| LEAVE | 225 | 0.565 | -363 | 0.311 |
| NEW | 45 | 0.113 | -2,118 | 0.133 |
| PENDING | 88 | 0.221 | -1,336 | 0.216 |
| RECYCLE | 7 | 0.018 | -1,252 | 0.143 |
| REJECT | 4 | 0.010 | · | · |
| THIN | 20 | 0.050 | -433 | 0.250 |

### `dir` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 191 | 0.480 | -821 | 0.262 |
| up | 207 | 0.520 | -863 | 0.251 |

### `touch_room_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 79 | 0.199 | -918 | 0.266 |
| held | 30 | 0.075 | -1,761 | 0.167 |
| none | 215 | 0.540 | -1,140 | 0.246 |
| pending | 74 | 0.186 | 473 | 0.311 |

### `fz_gate` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| BLOCK | 110 | 0.276 | -1,268 | 0.236 |
| TAKE | 112 | 0.281 | -386 | 0.304 |
| WATCH | 176 | 0.442 | -868 | 0.239 |

### `card_leave_kind` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| gap | 25 | 0.063 | -1,580 | 0.280 |
| normal | 200 | 0.502 | -211 | 0.315 |
| NA | 173 | 0.435 | -1,468 | 0.185 |

### `days_to_expiry` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 2.0, 7.0, 10.0, 14.0, 15.5, 18.2, 21.0, 23.0, 26.3. NA rows: 0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 2.0 | 27 | 0.068 | -601 | 0.333 |
| [2.0, 7.0) | 45 | 0.113 | -923 | 0.267 |
| [7.0, 10.0) | 40 | 0.101 | 76 | 0.275 |
| [10.0, 14.0) | 31 | 0.078 | -1,058 | 0.290 |
| [14.0, 15.5) | 56 | 0.141 | -214 | 0.286 |
| [15.5, 18.2) | 40 | 0.101 | -1,308 | 0.200 |
| [18.2, 21.0) | 28 | 0.070 | -2,981 | 0.036 |
| [21.0, 23.0) | 44 | 0.111 | -403 | 0.295 |
| [23.0, 26.3) | 47 | 0.118 | -2,519 | 0.149 |
| >= 26.3 | 40 | 0.101 | 898 | 0.400 |
| NA | 0 | 0.000 | · | · |

### `touch_prot_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 1 | 0.003 | · | · |
| held | 302 | 0.759 | -828 | 0.258 |
| na | 4 | 0.010 | · | · |
| none | 32 | 0.080 | -95 | 0.406 |
| pending | 59 | 0.148 | -1,267 | 0.170 |

### `ffd_close_dstar` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 2.4777, 2.4828, 2.4873, 2.4959, 2.5035, 2.5086, 2.5117, 2.5149, 2.522. NA rows: 0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 2.4777 | 40 | 0.101 | -1,648 | 0.125 |
| [2.4777, 2.4828) | 41 | 0.103 | -655 | 0.244 |
| [2.4828, 2.4873) | 39 | 0.098 | -834 | 0.205 |
| [2.4873, 2.4959) | 39 | 0.098 | -1,590 | 0.179 |
| [2.4959, 2.5035) | 41 | 0.103 | -1,210 | 0.220 |
| [2.5035, 2.5086) | 38 | 0.096 | -515 | 0.289 |
| [2.5086, 2.5117) | 39 | 0.098 | -698 | 0.333 |
| [2.5117, 2.5149) | 43 | 0.108 | -795 | 0.256 |
| [2.5149, 2.522) | 38 | 0.096 | -170 | 0.342 |
| >= 2.522 | 40 | 0.101 | -279 | 0.375 |
| NA | 0 | 0.000 | · | · |

### `gap_pts` (na_indicator; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| gap_pts defined | 398 | 1.000 | -843 | 0.256 |
| gap_pts NA | 0 | 0.000 | · | · |

### `n_choch_since_bos` (nchoch; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 5.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 | 115 | 0.289 | -827 | 0.243 |
| 1 | 155 | 0.389 | -695 | 0.310 |
| 2 | 73 | 0.183 | -1,679 | 0.164 |
| 3 | 16 | 0.040 | -512 | 0.250 |
| 4 | 14 | 0.035 | -1,400 | 0.143 |
| >=5 | 25 | 0.063 | 710 | 0.320 |

### `hv3_dir_agree` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| False | 55 | 0.138 | -624 | 0.236 |
| True | 114 | 0.286 | -737 | 0.254 |
| NA | 229 | 0.575 | -948 | 0.262 |

### `hv3_bars_since` (hv3b; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 12.0, 13.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 bars | 59 | 0.148 | -453 | 0.220 |
| 1 bars | 8 | 0.020 | -1,591 | 0.375 |
| 2-3 bars | 10 | 0.025 | -310 | 0.300 |
| 4-12 bars | 48 | 0.121 | -938 | 0.292 |
| >=13 bars | 44 | 0.111 | -700 | 0.204 |
| NA (no bar with vol_ratio20 >= 3 in the session so far) | 229 | 0.575 | -948 | 0.262 |

### `fz_visit_n` (visit; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 1.0, 2.0, 3.0, 4.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 1 | 38 | 0.096 | -950 | 0.210 |
| 2 | 57 | 0.143 | -980 | 0.281 |
| 3 | 35 | 0.088 | -975 | 0.229 |
| >=4 | 101 | 0.254 | -565 | 0.247 |
| NA (no ref room) | 167 | 0.420 | -912 | 0.270 |

## Two-way tables (cell = mean net INR / win rate / n; '·' = fewer than 5 units, count only)

### `fz_read` (rows) x `hour_bin` (columns)

| fz_read \ hour_bin | 09 | 10 | 11 | 12 | 13 | 14 | 15 | <09:25 | >=15:20 |
|---|---|---|---|---|---|---|---|---|---|
| ACCEPTED | 0 | 0 | · / · / 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| FIRST_PRINT | 0 | · / · / 1 | · / · / 1 | 0 | 0 | 0 | · / · / 1 | 0 | 0 |
| HUNT | 0 | · / · / 1 | · / · / 1 | · / · / 1 | · / · / 1 | 0 | 0 | 0 | 0 |
| LEAVE | 596 / 0.357 / 28 | -906 / 0.333 / 39 | 222 / 0.286 / 28 | -126 / 0.303 / 33 | -442 / 0.325 / 40 | 345 / 0.382 / 34 | -1,505 / 0.182 / 11 | -3,543 / 0.083 / 12 | 0 |
| NEW | -4,301 / 0.167 / 6 | -1,932 / 0.182 / 11 | · / · / 2 | -1,015 / 0.125 / 8 | -1,590 / 0.143 / 7 | -2,041 / 0.000 / 7 | 0 | · / · / 3 | · / · / 1 |
| PENDING | -3,090 / 0.143 / 14 | -1,528 / 0.167 / 12 | -2,630 / 0.100 / 10 | -1,658 / 0.214 / 14 | -473 / 0.312 / 16 | -525 / 0.200 / 15 | · / · / 4 | · / · / 3 | 0 |
| RECYCLE | · / · / 3 | 0 | 0 | 0 | 0 | · / · / 1 | · / · / 2 | · / · / 1 | 0 |
| REJECT | 0 | · / · / 1 | 0 | · / · / 1 | · / · / 1 | 0 | · / · / 1 | 0 | 0 |
| THIN | 0 | · / · / 2 | · / · / 2 | · / · / 4 | · / · / 4 | -1,877 / 0.167 / 6 | 0 | · / · / 2 | 0 |

### `n_choch_since_bos` (rows) x `dir` (columns)

| n_choch_since_bos \ dir | down | up |
|---|---|---|
| 0 | -291 / 0.265 / 49 | -1,225 / 0.227 / 66 |
| 1 | -930 / 0.301 / 83 | -425 / 0.319 / 72 |
| 2 | -1,727 / 0.151 / 33 | -1,639 / 0.175 / 40 |
| >=3 | -323 / 0.269 / 26 | -56 / 0.241 / 29 |

### `hv3_dir_agree` (rows) x `hv3_bars_since` (columns)

| hv3_dir_agree \ hv3_bars_since | 0 bars | 1 bars | 2-3 bars | 4-12 bars | >=13 bars | NA (no bar with vol_ratio20 >= 3 in the session so far) |
|---|---|---|---|---|---|---|
| False | 0 | · / · / 1 | · / · / 4 | -645 / 0.273 / 22 | -845 / 0.179 / 28 | 0 |
| True | -453 / 0.220 / 59 | -1,234 / 0.429 / 7 | -1,786 / 0.167 / 6 | -1,186 / 0.308 / 26 | -447 / 0.250 / 16 | 0 |
| NA | 0 | 0 | 0 | 0 | 0 | -948 / 0.262 / 229 |

### `fz_visit_n` (rows) x `fz_read` (columns)

| fz_visit_n \ fz_read | ACCEPTED | FIRST_PRINT | HUNT | LEAVE | NEW | PENDING | RECYCLE | REJECT | THIN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | · / · / 3 | · / · / 3 | · / · / 2 | 0 | -965 / 0.233 / 30 | 0 | 0 | 0 |
| 2 | · / · / 2 | 0 | 0 | 220 / 0.400 / 25 | 0 | -2,320 / 0.136 / 22 | · / · / 2 | · / · / 1 | 129 / 0.400 / 5 |
| 3 | 0 | 0 | 0 | -221 / 0.267 / 15 | 0 | -972 / 0.300 / 10 | · / · / 1 | · / · / 2 | -2,231 / 0.143 / 7 |
| >=4 | 0 | 0 | · / · / 1 | -540 / 0.262 / 61 | 0 | -1,072 / 0.231 / 26 | · / · / 4 | · / · / 1 | 787 / 0.250 / 8 |
| NA (no ref room) | 0 | 0 | 0 | -468 / 0.320 / 122 | -2,118 / 0.133 / 45 | 0 | 0 | 0 | 0 |

## Listed interaction pairs (from the frozen shortlist; the only depth-2/3 conjunctions allowed beyond the columns above)

| feature a | feature b | split points a | split points b | status |
|---|---|---|---|---|
| `touch_prot_bars_ago` | `ffd_close_dstar` | 6.0, 7.0, 8.0 | 2.4189, 2.419, 2.4232 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `room_ahead_dist_atr` | `n_rooms_alive` | 0.7394, 0.7617, 4.1739 | 6.0, 7.0, 8.0 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `room_ahead_dist_atr` | `fz_take_why=nan` | 0.0776, 0.1701, 0.3558 | 1.0 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `ffd_close_dstar` | `sl` | 2.4159, 2.4189, 2.4245, 2.5133 | 15985.5, 16086.5, 16705.25, 25184.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `room_ahead_dist_atr` | `ffd_close_dstar` | 0.1598, 0.1618, 0.3787, 0.4549 | 2.4698, 2.5133, 2.5277 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |

Generated 2026-09-29T12:36:07 by `studies/llm_round1/tables.py` from `harness.load('5minute')` (label L1) and `features_ext/5minute/ext_features.parquet`. Definitions: `r1_common.py` docstring. Family size for the max-T = **118** labelled cells.
