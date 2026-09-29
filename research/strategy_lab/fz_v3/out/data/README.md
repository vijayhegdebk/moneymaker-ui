# FZ v3 cloud datasets (`fz_v3/out/data/<timeframe>/`)

Built by `../build/build.py --tf minute | 5minute` from the committed files in `fz_v3/data/` read in full through
`engine.load` (never `lab.sessions()`). One column contract for both timeframes. `meta.json` next to the files carries the
provenance (data sha, code shas, thresholds, counts, run times); `compare.json` the cross-check against the local build
(`fz_v3/built/`); `trunc_<cut>/` the same build on the bars up to the cut with `trunc_diff.json` (the causality check).

**Foundation rules:** 1 min = Strategy 1 (`prev_swing` stop), 5 min = Strategy 2 (`choch_candle` stop); `break_mode touch`,
`choch_mode touch`, `avwap_weight volume`. **FZ block:** the frozen ST7 (1 min) / ST8 (5 min) `fz` block, memory from bar 0.
**Costs:** lot 65, 5 pts slippage per side, `lab.trade_charges(ZERODHA_NFO_FUT)` on the slipped prices (`net = pts x 65 -
cost`). **Split:** IS = SETUP date <= 2025-12-31, OOS = 2026-01-01 .. 2026-09-25.

## Look-ahead vocabulary

- **as-of**: computed from bars `<= k` (the SETUP bar) and engine / FZ state as of that bar's close. Feature-eligible.
- **label**: uses bars after `k`. Never a feature: prefixes `fnd_`, `l1_`, `fwd_`, `fzpos_`, `fzpost_`, and `fz_traded`.
- **final-state**: a value that keeps changing until the data end (`swings.broken_final`, `events.window_end`,
  `fz_zones.retired_*`, `fz_visits.end*`). Usable only through a bar-indexed condition (`birth_bar <= k < retired_bar`).

`harness.Table.asof_columns()` is the allow-list (label prefixes, identities, raw prices and ids removed).

## `features.parquet` — one row per Foundation SETUP (261 columns)

`sg` = +1 for `dir = up`, -1 for `dir = down`; `k` = `setup_i`; `a` = `atr14` at `k` (Wilder 14 on the futures bars, `lab.atr_series`);
"1h" / "3h" = 60 / 180 bars on 1 min, 12 / 36 bars on 5 min; None / NaN = not defined.

### identity and clock (as-of)
| column | definition |
|---|---|
| `setup_i`, `time`, `date`, `session_idx`, `session_bar`, `hhmm`, `hour`, `minute_of_day`, `dow` | the SETUP bar and its clock (bar open time; `dow` 0 = Monday) |
| `hour_bin` | `fz_report.crosstabs` bins with the frozen clocks: `<09:25`, `09` .. `15`, `>=15:20` |
| `dir`, `dir_sign` | SETUP direction |
| `choch_i`, `choch_time`, `bars_since_choch`, `choch_flip`, `choch_trend_before`, `choch_same_session` | the SETUP's own CHoCH |
| `open`, `high`, `low`, `close`, `contract`, `days_to_expiry` | the SETUP bar; the near-month contract and calendar days to its expiry |
| `split`, `in_warmup` | IS / OOS; session index < the strategy's `warmup_days` (flagged, not dropped) |
| `traded`, `engine_skipped` | the engine took / skipped the SETUP (wrong-side stop; 0 rows on both files) |
| `sl`, `sl_dist_pts`, `sl_dist_atr` | the Foundation stop at the SETUP close and its distance (`sg x (close - sl)`) |

### price window (as-of; all windows stop at the session's first bar: the overnight gap never enters)
| column | definition |
|---|---|
| `atr14`, `atr_bps` | ATR14; `1e4 x atr14 / close` |
| `range_1h_pts`, `range_1h_atr`, `range_3h_pts`, `range_3h_atr` | max high - min low over the last 1h / 3h of bars of this session ending at `k` |
| `range_since_choch_atr` | the same over bars `choch_i .. k` |
| `bar_range_pts`, `bar_body_pts`, `bar_range_atr`, `close_pos_in_bar` | the SETUP bar's range, body (`close - open`), range / a, `(close - low) / (high - low)` |
| `sess_open`, `close_vs_sess_open_pts`, `sess_range_atr`, `pos_in_session_range` | the session's open; the session so far: range / a, where the close sits in it (0 = at the low) |
| `gap_pts`, `prev_close` | `sess_open -` the previous session's last close |
| `ret_1h_pts`, `ret_3h_pts` | `close[k] - close[k - N]` when `k - N` is in the session, else NaN |
| `er_1h` | Kaufman efficiency ratio of the closes over the last hour of the session (at least 6 bars) |

### regime from the engine's event stream (as-of; events with bar `<= k`, the SETUP's own CHoCH included)
| column | definition |
|---|---|
| `n_events_asof` | events (BOS + CHoCH) up to `k` |
| `n_choch_since_bos` | CHoCH events after the last BOS (all CHoCHs when no BOS yet); `>= 2` = "CHoCH, CHoCH, no BOS" |
| `n_choch_since_bos_today` | the same restricted to this session's events |
| `n_flip_since_bos`, `n_bos_since_choch` | of those CHoCHs, the trend flips; BOS events after the last CHoCH |
| `bars_since_bos`, `last_bos_dir`, `last_bos_same_session` | the last BOS (NaN / `none` before the first) |
| `bars_since_prev_choch`, `last_choch_dir` | the CHoCH before the latest one; the latest CHoCH's direction |
| `alt_dir6`, `alt_kind6`, `last6_kinds` | direction changes / kind changes among the last 6 events; the last 6 as `Cu Cd Bu ...` |
| `choch_run` | consecutive CHoCH events at the end of the event list |
| `n_choch_1h`, `n_bos_1h`, `n_choch_3h`, `n_bos_3h` | events with `k - N < i <= k` |
| `n_events_today`, `n_choch_today`, `n_bos_today` | this session's events up to `k` |

### volume (as-of; baselines = the previous bars of the same session, excluding `k`, at least 5 of them)
| column | definition |
|---|---|
| `vol`, `vol_med20_prior`, `vol_med60_prior`, `vol_ratio20`, `vol_ratio60`, `vol_na` | the bar's volume, the prior medians, their ratios (NaN when NA / no baseline); NA = not the front month or zero volume |
| `sess_cumvol_ratio20s` | cumulative session volume at `k` / the median of the same at this `session_bar` over the previous 20 sessions (at least 5) |
| `vol_max_ratio20_5`, `vol_max_ratio20_15` | max `vol_ratio20` over the last 5 / 15 bars of the session |
| `hv{2,3}_bars_since`, `_dir`, `_dir_agree`, `_ratio`, `_low_held`, `_high_held` | the latest bar of this session with `vol_ratio20 >= 2` / `>= 3`: bars ago, its direction (`up` / `down` / `flat` / `none`), agreement with `dir`, its ratio, whether its low / high held over `j+1 .. k` (None when `j = k`) |
| `vol_ratio20_at_choch`, `vol_max_ratio20_choch_to_k` | `vol_ratio20` at the CHoCH bar; its max over `choch_i .. k` |
| `sess_vol_vs_prev_sess` | session volume up to `k` / the previous session's over the same bar count |

### levels (as-of)
| column | definition |
|---|---|
| `prot_lvl`, `dist_prot_dir_atr` | the engine's protected level at `k`; `sg x (close - prot) / a` (positive = the level is behind the entry) |
| `last_sh_px`, `last_sl_px`, `dist_sh_atr`, `dist_sl_atr`, `last_sh_bars_ago`, `last_sl_bars_ago` | the latest confirmed swing high / low (`conf <= k`): price, distance (`(sh - close) / a`, `(close - sl) / a`), age of the swing bar |
| `swing_ahead_dist_atr` | the swing high for a long / swing low for a short, ahead in ATR (negative when already beyond) |
| `swing_near_kind`, `swing_near_dist_dir_atr` | the nearer of the two |
| `choch_lvl`, `dist_choch_lvl_atr` | the level the SETUP's CHoCH broke; `sg x (close - lvl) / a` |
| `n_swings_1h`, `choch_bar_range_atr`, `move_since_choch_pts` | swings confirmed in the last hour; the CHoCH candle's range / a; `sg x (close - close[choch_i])` |
| `n_rooms_alive`, `room_edge`, `room_edge_dist_dir_atr`, `room_edge_id`, `room_edge_kind`, `room_ahead_dist_atr`, `room_behind_dist_atr` | ST7/ST8 rooms alive at `k` (`birth_bar <= k < retired_bar`): the nearest edge (signed by `dir`: positive = ahead), the nearest edge strictly ahead / behind |
| `touch_{prot,room,swing}_n`, `_last`, `_bars_ago` | touch episodes of that level in the last hour before `k` (a bar touches when `low <= L <= high`); the last episode's verdict within 15 minutes after it, never past `k`: `broke` (a close beyond by > 0.5 x atr14 on the far side), `held`, `pending` (window still open at `k`), `none`, `na` |

### the session's ledger so far (as-of; only trades with `exit <= k` count)
| column | definition |
|---|---|
| `today_n_closed_asof`, `today_net_asof`, `today_pts_asof`, `today_n_stops_asof` | the session's Foundation trades closed by `k` |
| `today_n_setups_before`, `last_closed_net_asof`, `last_closed_reason_asof` | earlier SETUPs today; the latest closed trade |

### the FZ card at the SETUP bar (`card_*`, as-of; FZ.md section 7)
The 28 card fields fz.run writes (`zone_id`, `visit_n`, `this_bars`, `this_vol`, `vol_na`, `first_bars`, `first_vol`, `first_vol_na`,
`read`, `left_id`, `out_run`, `out_side`, `gap_pts`, `wick_depth`, `last_hunt_at`, `last_hunt_dir`, `last_reject_at`, `last_reject_dir`,
`cluster_sit`, `prev_bars`, `prev_vol`, `last_leave_failed`, `in_id`, `leave_side`, `leave_vol_ok`, `leave_kind`, `first_clock_lived`,
`touches`), plus `card_vol_ratio` (`this_vol / first_vol` when both live), `card_bars_since_hunt`, `card_bars_since_reject`,
`card_hunt_dir_agree`, `card_in_room`, `card_ref_room_live`.

### the FZ ledger as of the SETUP bar (`fz_*`, as-of; FZ.md section 8)
`fz_zone_id`, `fz_zone_kind`, `fz_band_lo`, `fz_band_hi`, `fz_visit_n`, `fz_this_bars`, `fz_this_vol`, `fz_first_bars`, `fz_first_vol`, `fz_vol_na`,
`fz_first_vol_na`, `fz_read`, `fz_left_id`, `fz_in_id`, `fz_level_in_band`, **`fz_gate`** (TAKE / WATCH / BLOCK / REENTER as of the bar),
`fz_block_reason`, `fz_branch`, `fz_take_why`, `fz_entered_zone_id`, `fz_entered_visit_n`, `fz_entered_read`, `fz_leave_vol_ok`,
`fz_leave_kind`, `fz_watch_kind`, `fz_watch_band_id`, `fz_band_width`, `fz_band_width_atr`, `fz_pos_in_band`, `fz_pos_in_band_dir`
(1 = at the edge ahead), `fz_dist_band_edge_ahead`, `fz_dist_band_edge_behind`.

### post-SETUP (`fzpost_*`, never features)
`fzpost_outcome_gate` (REENTER when a later REENTER used this SETUP), `fzpost_refused`, `fzpost_watch_outcome`, `fzpost_reenter_reason`,
`fzpost_fill_used`, `fzpost_fill_bar`, `fzpost_fill_delay_bars`, `fzpost_edge_dist_pts`, `fzpost_armed_bars`, `fzpost_rearmed_bars`, `fzpost_sl_bar`;
**`fz_traded`** = ST7/ST8 held a position on this SETUP (a TAKE, or a REENTER whose R5 was this SETUP, possibly filled later): the
frozen gate's kept set, post-SETUP.

### labels (never features)
| column | definition |
|---|---|
| `fwd_ret_{5,15,30}_dir_pts`, `fwd_mfe30`, `fwd_mae30` | `sg x (close[k+N] - close[k])`; best / worst excursion in the trade direction over `k+1 .. k+30` |
| `fnd_*` | **L0**, the engine's own trade: `exit_i`, `exit_time`, `exit_px`, `exit_reason` (`stop_loss` / `next_choch` / `open`), `open`, `pts`, `gross_inr`, `charges_inr`, `cost_inr`, `net_inr`, `win`, `bars_held`, `sessions_held`, `crosses_roll`, `mfe_pts` (>= 0), `mae_pts` (<= 0), `mfe_bar`, `mae_bar` |
| `l1_*` | **L1**, the intraday book (the same trade cut at the entry session's 15:25 bar as `lab.eod_cut` does; a SETUP opening at or after 15:25 is `l1_taken = False`, `l1_exit_reason = not_taken`; the contract's last candle also ends a trade, `expiry`): `taken`, `exit_i`, `exit_time`, `exit_px`, `exit_reason` (`stop_loss` / `next_choch` / `eod` / `expiry`), `pts`, `gross_inr`, `charges_inr`, `cost_inr`, `net_inr`, `win`, `bars_held`, `mfe_pts`, `mae_pts`, `cut` (the cut changed the exit) |
| `fzpos_*` | the ST7/ST8 position opened on this SETUP: `kind`, `entry_i`, `entry_time`, `exit_i`, `exit_time`, `exit_reason`, `pts`, `net_inr`, and its L1 cut `l1_net_inr`, `l1_exit_reason` |

## The other tables

| file | rows | look-ahead status |
|---|---|---|
| `bars` | every bar | `i, datetime, date, session_idx, session_bar, open, high, low, close, volume, oi, contract, expiry, front_month, fm_na, atr14, prot` (the protected level as of the bar), `vol_med20_prior, vol_ratio20, vol_ratio60, sess_cumvol, sess_cumvol_ratio20s, split`: all as-of |
| `sessions` | 1,188 | `session_idx, date, split, in_warmup, n_bars, first_bar, last_bar, front_month, contract, expiry` |
| `swings` | engine swings | `seq, kind, bar, time, price, conf_bar, conf_time` as-of from `conf_bar`; `broken_final` **final-state** |
| `events` | CHoCH and BOS | `seq, i, time, kind, dir, flip, lvl, av, trend_before, sh_bar, sh_px, sl_bar, sl_px, prot_swing_bar, prot_swing_kind` as-of at bar `i`; `window_end` **final-state** |
| `setups` | every SETUP | `setup_i, time, dir, choch_i, choch_time, engine_skipped` |
| `trades` | every Foundation trade | the L0 trade priced (`entry_i .. mae_bar`, `split`, `in_warmup`) and its L1 cut (`l1_*`); outcome columns are labels |
| `fz_trades` | ST7/ST8 positions | the same columns plus `gate, setup_i, zone_id, fill_used, reenter_reason, sl_bar, sl_in_band` |
| `fz_card` | every bar | `i, time` + the card as of that bar (never rewritten) |
| `fz_ledger` | every SETUP | fz.run's row verbatim (as-of up to `watch_band_id`; post-SETUP from `outcome_gate`), `choch_time`, `fill_time` |
| `fz_zones` | every room | `id, kind, lo, hi, mid, origin_bar, birth_bar, born_ts` as-of from `birth_bar`; `merges, n_stays, n_visits, touches, retired_bar, retired_by, retired_ts` **final-state** |
| `fz_visits` | every stay | `zone_id, visit_n, start, start_time` as-of from `start`; `end, end_time, ended_by, bars, vol, vol_na, entry_dir, touch, defend_dir` **final-state** for the stay |
| `fz_watches`, `fz_decisions` | the watch log; every position fz.run opened with the pinned band | `opened_at .. setup_i` as-of at `opened_at`; outcomes post-open |
| `fz_stats.json` | | fz.run's counters over the whole file |

## Differences from the local build (`fz_v3/built/`), by definition

Engine, trades, FZ card, rooms, ledger and positions are identical (see `compare.json`). Feature definitions that differ on purpose:
same-session windows for `range_1h/3h` (the local 5-minute build crossed the session break), same-session volume baselines with at
least 5 prior bars everywhere (the local 5-minute `hv3_*` used a cross-session 20-bar median), MFE >= 0 / MAE <= 0 as
`lab.excursion` (the local 5-minute build kept the raw signs), touch windows of 1 hour / 15 minutes on both timeframes.
