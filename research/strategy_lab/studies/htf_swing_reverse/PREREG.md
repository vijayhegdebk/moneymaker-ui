# 1-hour swing direction, one 1-minute trade, one reverse if it fails: pre-registration

Written 2026-10-03 before any result was computed. User's rule: "Check for 1 hour swing, do one trade in that direction in
1 min, if failed do one reverse trade."

## Rule (every number fixed here; each one not stated by the user is marked "assumption")

| item | rule | status |
|---|---|---|
| 1-hour bars | built from the 1-minute near-month futures bars: hours starting 09:15, 10:15, 11:15, 12:15, 13:15, 14:15, and a last 15-minute bar 15:15-15:29; a 1-hour bar is known only at the close of its last 1-minute bar | assumption (NSE session hours) |
| 1-hour swing | our engine's swing detector (`engine.run`, Strategy 1 settings: break_mode touch) on the 1-hour bars; a swing counts from the close of its confirmation hour | ours |
| direction | the direction of the current 1-hour swing leg: last confirmed swing a low -> **up**, a high -> **down** | assumption (reading of "1 hour swing") |
| cadence | one cycle per session: the first trade of the day in the 1-hour direction current at the entry bar; if it fails, one reverse trade; then nothing more that day | user |
| entry E1 (primary) | the first Strategy 1 SETUP of the day on 1 minute (our Foundation entry: CHoCH + AVWAP pair, `fz_v3/out/data/minute/trades.parquet`) whose direction equals the 1-hour direction at that bar; enter at its close; stop = Strategy 1's stop (latest confirmed 1-minute swing against the trade) | ours |
| entry E2 (plain) | the close of the 09:20 bar in the 1-hour direction; stop = the latest confirmed 1-minute engine swing against the trade (Strategy 1's rule); a day whose stop is on the wrong side is skipped | assumption (tests the 1-hour direction without a 1-minute trigger) |
| exits (both trades) | stop, target 2R (R = entry-to-stop distance), or the last bar opening at or before 15:25 | assumption (target 2R); 15:25 square-off as Strategies 1-12 |
| "failed" | the first trade is stopped out (a target or the 15:25 exit is not a failure) | assumption |
| reverse trade | entered on the stop bar at the stop's fill price, opposite direction, stop = R on the other side, target 2R, 15:25 exit; not taken if the stop fills at or after 15:25 | user (one reverse); distances assumption |
| fills | the lab's: no fill on a session's first bar; an open beyond the stop fills at the open; a bar touching stop and target counts as the stop | lab |
| pricing | lot 65, 5 pts slippage per side, `lab.trade_charges(ZERODHA_NFO_FUT)`, each trade its own round trip | lab |

## Windows and judgement

IS 2021-10-01..2025-12-31 and 2026-01-01..2026-09-25, reported separately. Per variant: the day-cycle book (first + reverse),
the first trades alone, the reverse trades alone; net INR per trade and per day, win rate, profit factor, t-stat, worst week,
positive weeks, gross points.

Controls: (1) **direction control**: the same days and entry bars with the first trade's direction drawn at random (the
reverse logic then applied as usual), 1,000 seeded draws: does the 1-hour direction carry information? (2) **no-reverse
book**: the same first trades without the reverse: does the reverse add or subtract? (3) gross points beside every net.

Pass: the day-cycle book's net mean > 0 in both windows and at or above the 95th percentile of the direction control.

## Look-ahead check

The whole pipeline (1-hour bars, 1-hour swings, direction, entries) is rerun on 1-minute bars cut at 2025-06-30 12:00;
every trade entered before the cut must be identical.

## Amendment 1 (2026-10-03, after the first results; user: "Yes, SL is of 1 hour and risk is 1R")

Only the stop changes. The first trade's stop is the latest confirmed **1-hour** swing against the trade (long: the last
1-hour swing low, short: the last 1-hour swing high), known from the close of its confirmation hour. R = entry to that stop.
Target 2R and the 15:25 exit as before; the reverse trade starts at the stop price with the same 1R risk on the other side.
For E1, a SETUP whose 1-hour stop is on the wrong side of the entry is passed over for the next agreeing SETUP of the day;
for E2 the day is skipped. Results also in R multiples (`r_mean`). Files: `results_1h.json`, `trades_<E1|E2>_1h.csv`,
`trunc_check_1h.json`, `run_1h.log`. The 1-minute-stop run is unchanged and reproduces bit for bit.
