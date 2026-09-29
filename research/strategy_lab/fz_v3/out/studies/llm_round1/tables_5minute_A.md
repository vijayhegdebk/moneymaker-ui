# LLM round 1, labelled tables: 5minute / half A (harness blocks 0-5; IS only; label L1)

**Study** `llm_round1` step 1 (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1: cross-fitted halves; Judge 2: the family size is the number of labelled cells shown). **Rows**: 428 L1 units of the 5minute table (Strategy 2 rules + ST8 card) in 214 sessions, 2021-10-01 .. 2023-11-06 (SETUP dates; the half is time-contiguous). Label = L1 net INR per trade (the 15:25 intraday book, lot 65, 5 pts slippage per side, charges included; every skipped trade saves ~1,050 INR of costs, so net alone is never the criterion). Nothing from OOS; no raw rows.

**SHORTLIST STATE.** The frozen feature shortlist (`features_shortlist/5minute/shortlist.json`, sha256 `4747257f41ecb40f...`) has `n_shortlisted = 0` and `allowed_columns = []`: **the EMPTY-SHORTLIST RULE applies**. The tables cover `hour_bin`, `fz_read`, `dir` (always included) plus an **exploratory vocabulary labelled "outside the frozen shortlist"**: the representative of each of the top-8 clusters by log-loss MDA rank of the importance study (none of which passes the shortlist rule; their MDA mean is below one std) and the columns of the design's four two-way tables. Every rule written from these tables is exploratory and must say so in its reason; a candidate frozen from them carries the provenance `{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` for the user to accept or reject. Every labelled cell below counts toward the family size of the scorer's max-T exactly as a shortlisted cell would.

**Family size of this file: 122 labelled cells** (count >= 5: mean net and win rate printed; 42 cells with 1-4 units show the count only ('·') and are not labelled; 69 empty cells). Base rate of the half (one labelled cell): n 428, mean net **-677** INR, win rate **0.297**.

## What the proposer may do with these tables

- Write at most 8 **skip** rules for `5minute`, each a conjunction of <= 3 comparisons `[column, op, value]` with ops `>=`, `>`, `<=`, `<`, `==`, `!=`, `in`, `not_in`; a None / NaN value never fires a comparison (the SETUP is kept).
- **Columns**: only the columns shown in this file (the vocabulary table below), or a listed interaction pair (section at the end). Numeric **thresholds must be values printed as decile edges / bucket boundaries / levels** of that column in this file (or a listed split point of an interaction pair); text comparisons use the printed levels.
- Read this half only. Your rules are scored on the OTHER half (B, blocks 6-11) through the harness; the scorer's family for the max-T is the 122 labelled cells of this file plus every rule proposed (round 0 and round 1), so a rule has to beat the best of everything you could have picked here, not just the other 7 rules.
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
| 09 | 45 | 0.105 | -774 | 0.333 |
| 10 | 56 | 0.131 | -857 | 0.232 |
| 11 | 54 | 0.126 | -1,434 | 0.241 |
| 12 | 65 | 0.152 | -1,313 | 0.200 |
| 13 | 80 | 0.187 | -385 | 0.325 |
| 14 | 69 | 0.161 | -311 | 0.420 |
| 15 | 26 | 0.061 | -935 | 0.154 |
| <09:25 | 29 | 0.068 | 1,272 | 0.483 |
| >=15:20 | 4 | 0.009 | · | · |

### `fz_read` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| ACCEPTED | 2 | 0.005 | · | · |
| FIRST_PRINT | 4 | 0.009 | · | · |
| HUNT | 1 | 0.002 | · | · |
| LEAVE | 241 | 0.563 | -548 | 0.299 |
| NEW | 39 | 0.091 | -429 | 0.385 |
| PENDING | 106 | 0.248 | -1,208 | 0.264 |
| RECYCLE | 4 | 0.009 | · | · |
| REJECT | 3 | 0.007 | · | · |
| THIN | 28 | 0.065 | 235 | 0.357 |

### `dir` (level; design)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| down | 209 | 0.488 | -402 | 0.335 |
| up | 219 | 0.512 | -940 | 0.260 |

### `touch_room_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 70 | 0.164 | -262 | 0.314 |
| held | 31 | 0.072 | -1,039 | 0.194 |
| none | 238 | 0.556 | -789 | 0.328 |
| pending | 89 | 0.208 | -578 | 0.236 |

### `fz_gate` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| BLOCK | 103 | 0.241 | 11 | 0.379 |
| REENTER | 1 | 0.002 | · | · |
| TAKE | 116 | 0.271 | -1,350 | 0.250 |
| WATCH | 208 | 0.486 | -655 | 0.279 |

### `card_leave_kind` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| gap | 24 | 0.056 | 1,262 | 0.500 |
| normal | 217 | 0.507 | -749 | 0.277 |
| NA | 187 | 0.437 | -843 | 0.294 |

### `days_to_expiry` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 1.0, 5.0, 7.0, 9.0, 13.0, 16.0, 21.0, 23.0, 27.0. NA rows: 0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 1.0 | 17 | 0.040 | -878 | 0.294 |
| [1.0, 5.0) | 64 | 0.149 | -1,420 | 0.203 |
| [5.0, 7.0) | 32 | 0.075 | -1,463 | 0.156 |
| [7.0, 9.0) | 39 | 0.091 | -1,020 | 0.333 |
| [9.0, 13.0) | 45 | 0.105 | 425 | 0.311 |
| [13.0, 16.0) | 50 | 0.117 | -453 | 0.340 |
| [16.0, 21.0) | 49 | 0.115 | -690 | 0.286 |
| [21.0, 23.0) | 40 | 0.093 | 245 | 0.400 |
| [23.0, 27.0) | 30 | 0.070 | 153 | 0.400 |
| >= 27.0 | 62 | 0.145 | -1,202 | 0.290 |
| NA | 0 | 0.000 | · | · |

### `touch_prot_last` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| broke | 2 | 0.005 | · | · |
| held | 302 | 0.706 | -543 | 0.298 |
| na | 11 | 0.026 | -2,009 | 0.182 |
| none | 35 | 0.082 | -1,921 | 0.229 |
| pending | 78 | 0.182 | -407 | 0.346 |

### `ffd_close_dstar` (decile; outside the frozen shortlist)

Decile edges of this half (the allowed thresholds): 2.4071, 2.4159, 2.4193, 2.4234, 2.4284, 2.4314, 2.4347, 2.4432, 2.4515. NA rows: 9.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| < 2.4071 | 42 | 0.098 | 365 | 0.452 |
| [2.4071, 2.4159) | 41 | 0.096 | -1,163 | 0.244 |
| [2.4159, 2.4193) | 43 | 0.101 | 436 | 0.349 |
| [2.4193, 2.4234) | 41 | 0.096 | -724 | 0.220 |
| [2.4234, 2.4284) | 43 | 0.101 | -1,451 | 0.279 |
| [2.4284, 2.4314) | 42 | 0.098 | -331 | 0.333 |
| [2.4314, 2.4347) | 41 | 0.096 | -964 | 0.268 |
| [2.4347, 2.4432) | 42 | 0.098 | -754 | 0.309 |
| [2.4432, 2.4515) | 43 | 0.101 | -1,359 | 0.302 |
| >= 2.4515 | 41 | 0.096 | -1,005 | 0.171 |
| NA | 9 | 0.021 | 71 | 0.444 |

### `gap_pts` (na_indicator; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| gap_pts defined | 424 | 0.991 | -663 | 0.299 |
| gap_pts NA | 4 | 0.009 | · | · |

### `n_choch_since_bos` (nchoch; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 5.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 | 120 | 0.280 | -612 | 0.308 |
| 1 | 177 | 0.414 | -605 | 0.305 |
| 2 | 70 | 0.164 | -1,190 | 0.243 |
| 3 | 38 | 0.089 | -262 | 0.368 |
| 4 | 13 | 0.030 | -727 | 0.231 |
| >=5 | 10 | 0.023 | -664 | 0.200 |

### `hv3_dir_agree` (level; outside the frozen shortlist)


| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| False | 53 | 0.124 | -135 | 0.340 |
| True | 120 | 0.280 | -831 | 0.283 |
| NA | 255 | 0.596 | -718 | 0.294 |

### `hv3_bars_since` (hv3b; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 0.0, 1.0, 2.0, 3.0, 4.0, 12.0, 13.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 0 bars | 51 | 0.119 | -1,035 | 0.333 |
| 1 bars | 8 | 0.019 | 862 | 0.375 |
| 2-3 bars | 13 | 0.030 | -1,850 | 0.077 |
| 4-12 bars | 47 | 0.110 | -704 | 0.255 |
| >=13 bars | 54 | 0.126 | -71 | 0.352 |
| NA (no bar with vol_ratio20 >= 3 in the session so far) | 255 | 0.596 | -718 | 0.294 |

### `fz_visit_n` (visit; outside the frozen shortlist)

Bucket boundaries (the allowed thresholds): 1.0, 2.0, 3.0, 4.0.

| bin | n | share | mean net (INR) | win rate |
|---|---|---|---|---|
| 1 | 33 | 0.077 | -1,445 | 0.182 |
| 2 | 68 | 0.159 | -265 | 0.279 |
| 3 | 45 | 0.105 | -1,313 | 0.222 |
| >=4 | 116 | 0.271 | -456 | 0.310 |
| NA (no ref room) | 166 | 0.388 | -676 | 0.337 |

## Two-way tables (cell = mean net INR / win rate / n; '·' = fewer than 5 units, count only)

### `fz_read` (rows) x `hour_bin` (columns)

| fz_read \ hour_bin | 09 | 10 | 11 | 12 | 13 | 14 | 15 | <09:25 | >=15:20 |
|---|---|---|---|---|---|---|---|---|---|
| ACCEPTED | 0 | 0 | 0 | 0 | 0 | · / · / 1 | 0 | 0 | · / · / 1 |
| FIRST_PRINT | · / · / 1 | 0 | · / · / 1 | · / · / 1 | · / · / 1 | 0 | 0 | 0 | 0 |
| HUNT | 0 | 0 | · / · / 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| LEAVE | -839 / 0.310 / 29 | -889 / 0.222 / 36 | -1,161 / 0.258 / 31 | -1,195 / 0.222 / 36 | 131 / 0.317 / 41 | -553 / 0.368 / 38 | -812 / 0.286 / 14 | 2,117 / 0.533 / 15 | · / · / 1 |
| NEW | · / · / 2 | -540 / 0.200 / 5 | -1,108 / 0.500 / 6 | · / · / 4 | 17 / 0.444 / 9 | -70 / 0.667 / 6 | · / · / 1 | 1,249 / 0.400 / 5 | · / · / 1 |
| PENDING | -923 / 0.333 / 12 | -1,904 / 0.182 / 11 | -1,782 / 0.200 / 10 | -1,313 / 0.200 / 20 | -1,639 / 0.250 / 20 | -494 / 0.471 / 17 | -812 / 0.000 / 8 | -530 / 0.375 / 8 | 0 |
| RECYCLE | · / · / 1 | 0 | · / · / 2 | 0 | 0 | 0 | 0 | 0 | · / · / 1 |
| REJECT | 0 | 0 | · / · / 1 | · / · / 1 | 0 | · / · / 1 | 0 | 0 | 0 |
| THIN | 0 | · / · / 4 | · / · / 2 | · / · / 3 | -369 / 0.444 / 9 | 1,814 / 0.333 / 6 | · / · / 3 | · / · / 1 | 0 |

### `n_choch_since_bos` (rows) x `dir` (columns)

| n_choch_since_bos \ dir | down | up |
|---|---|---|
| 0 | -208 / 0.360 / 50 | -901 / 0.271 / 70 |
| 1 | -197 / 0.344 / 93 | -1,056 / 0.262 / 84 |
| 2 | -1,073 / 0.250 / 32 | -1,288 / 0.237 / 38 |
| >=3 | -617 / 0.353 / 34 | -187 / 0.259 / 27 |

### `hv3_dir_agree` (rows) x `hv3_bars_since` (columns)

| hv3_dir_agree \ hv3_bars_since | 0 bars | 1 bars | 2-3 bars | 4-12 bars | >=13 bars | NA (no bar with vol_ratio20 >= 3 in the session so far) |
|---|---|---|---|---|---|---|
| False | 0 | · / · / 2 | · / · / 2 | 473 / 0.409 / 22 | -185 / 0.333 / 27 | 0 |
| True | -1,035 / 0.333 / 51 | 2,234 / 0.500 / 6 | -1,635 / 0.091 / 11 | -1,740 / 0.120 / 25 | 43 / 0.370 / 27 | 0 |
| NA | 0 | 0 | 0 | 0 | 0 | -718 / 0.294 / 255 |

### `fz_visit_n` (rows) x `fz_read` (columns)

| fz_visit_n \ fz_read | ACCEPTED | FIRST_PRINT | HUNT | LEAVE | NEW | PENDING | RECYCLE | REJECT | THIN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | · / · / 4 | 0 | · / · / 2 | 0 | -1,777 / 0.185 / 27 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 607 / 0.294 / 34 | 0 | -817 / 0.320 / 25 | 0 | · / · / 1 | -1,841 / 0.125 / 8 |
| 3 | 0 | 0 | · / · / 1 | -2,096 / 0.143 / 21 | 0 | -1,675 / 0.286 / 14 | · / · / 2 | 0 | 1,816 / 0.429 / 7 |
| >=4 | · / · / 2 | 0 | 0 | -380 / 0.298 / 57 | 0 | -904 / 0.275 / 40 | · / · / 2 | · / · / 2 | 662 / 0.462 / 13 |
| NA (no ref room) | 0 | 0 | 0 | -751 / 0.323 / 127 | -429 / 0.385 / 39 | 0 | 0 | 0 | 0 |

## Listed interaction pairs (from the frozen shortlist; the only depth-2/3 conjunctions allowed beyond the columns above)

| feature a | feature b | split points a | split points b | status |
|---|---|---|---|---|
| `touch_prot_bars_ago` | `ffd_close_dstar` | 6.0, 7.0, 8.0 | 2.4189, 2.419, 2.4232 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `room_ahead_dist_atr` | `n_rooms_alive` | 0.7394, 0.7617, 4.1739 | 6.0, 7.0, 8.0 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `room_ahead_dist_atr` | `fz_take_why=nan` | 0.0776, 0.1701, 0.3558 | 1.0 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |
| `ffd_close_dstar` | `sl` | 2.4159, 2.4189, 2.4245, 2.5133 | 15985.5, 16086.5, 16705.25, 25184.0 | REFUSED: calendar-time proxy (drift.json time_proxies) |
| `room_ahead_dist_atr` | `ffd_close_dstar` | 0.1598, 0.1618, 0.3787, 0.4549 | 2.4698, 2.5133, 2.5277 | outside the frozen shortlist; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar) |

Generated 2026-09-29T12:36:07 by `studies/llm_round1/tables.py` from `harness.load('5minute')` (label L1) and `features_ext/5minute/ext_features.parquet`. Definitions: `r1_common.py` docstring. Family size for the max-T = **122** labelled cells.
