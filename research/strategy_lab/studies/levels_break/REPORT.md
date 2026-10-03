# Levels Likely to Break (Zeiierman): backtest on NIFTY near-month futures

Run 2026-10-03 by `levels_break.py` (pre-registration and its one amendment: `PREREG.md`; raw numbers: `results.json`,
`run.log`; every trade: `trades_<tf>_<A|B>.csv`; every signal: `signals_<tf>.csv`).

**Read this first.** TradingView and the author's site are blocked by this environment's network proxy, so the Pine source
was not available. The level rule is rebuilt from the published description (two same-side confirmed pivots within a
volatility-adjusted tolerance mark the level). The pivot length 5, the tolerance 0.25 x ATR14, the level life, the
"pressure" rule and the trade rule (enter on the first close through the level, stop 1 ATR on the other side of the level,
target 2R, square-off 15:25) are assumptions fixed before the run. A different reading of the original could give different
numbers. Simulated futures only; no real orders.

## Result

The rebuilt break rule loses money on both timeframes, in both windows, with and without the pressure filter.

| | 5 min A (every break) | 5 min B (break after pressure) | 1 min A | 1 min B |
|---|---|---|---|---|
| trades IS / 2026 | 717 / 121 | 434 / 78 | 4,680 / 780 | 2,960 / 540 |
| net INR per trade, IS | -828 | -693 | -1,089 | -1,088 |
| net INR per trade, 2026 | -900 | -670 | -1,286 | -1,241 |
| net total IS (INR) | -5.94 L | -3.01 L | -50.97 L | -32.21 L |
| t-stat of the mean, IS | -7.4 | -4.8 | -52.5 | -42.1 |
| win rate / profit factor, IS | 36% / 0.52 | 37% / 0.58 | 25% / 0.18 | 25% / 0.18 |
| gross points per trade, IS (before costs) | +3.5 | +5.6 | -0.5 | -0.5 |
| gross points per trade, 2026 | +3.3 | +6.8 | -2.6 | -2.0 |
| cost per trade (slippage + charges) | 1,057 INR (about 16 pts) | 1,056 | 1,055 | 1,056 |
| worst week, IS (INR) | -23,911 | -19,249 | -50,313 | -36,229 |
| positive weeks, IS | 32% | 36% | 1% | 1% |
| direction control percentile, IS / 2026 | 80.6 / 68.6 | 93.7 / 89.5 | 6.0 / 0.1 | 4.9 / 7.2 |
| timing control percentile, IS / 2026 | 96.9 / 74.5 | 99.2 / 85.4 | 4.2 / 0.5 | 9.4 / 5.6 |

L = lakh. Controls: direction = the same entry bars with a random side; timing = the same time of day, side and stop in
another random session of the same window (1,000 seeded draws each; a percentile of 95 or more means the rule beats chance).

## What it means

- **5 minutes**: breaks of matched double tops and bottoms do carry a small edge in direction and timing. The filtered
  version beats the random-timing control at the 99th percentile in sample and the pressure filter adds about 2 points.
  But the move is +3 to +7 points per trade against about 16 points of cost, so every variant loses about 700-900 INR per
  trade. The 2026 window keeps the sign of the gross edge but not the control percentile (74-89).
- **1 minute**: breaks are worse than random. The first close through a 1-minute double top or bottom is more often a
  fake-out (gross -0.5 to -2.6 points, below both controls). Fading them would not help: the gross is still a tiny fraction of
  the 16-point cost.
- The "pressure" filter (a retest plus price squeezing into the level) improves 5 minutes slightly and changes nothing on 1
  minute.
- Same conclusion as the FZ v3 program: on NIFTY futures at 1 lot with 5 points of slippage per side, intraday level signals
  that move a few points cannot pay the costs. Only signals with moves of several times 16 points can.

## Pass rule (fixed in PREREG.md)

A variant works only if its net mean is positive in both windows and it is at or above the 95th percentile of both controls.
**No variant passes**; none has a positive net mean in any window.

## Look-ahead check

`python levels_break.py --trunc`: signals regenerated on bars cut at 2025-06-30 12:00 are identical to the full run's signals
before the cut (5 min 872 / 872, 1 min 5,737 / 5,737; `trunc_check.json`).

## The one amendment

The first timing control drew random bars from the same session with the trade's side. The side is the break direction,
which reveals where price went later that day, so it flattered the random trades (+11 gross points). It was replaced by
the other-session version before the 1-minute run; the trade rule never changed (`PREREG.md`, Amendment 1; old numbers in
`run_v1.log`).

## Second run: the levels built from our own swings (PREREG.md, Amendment 2)

User, 2026-10-03: the levels have to come from "our swing high low or 4 ATR swings". Only the swing source changed; the
tolerance, level life, break, pressure filter, trades, costs, controls and pass rule are the ones above
(`results_sources.json`, `run_sources.log`, `trades_<source>_<tf>_<A|B>.csv`, `signals_<source>_<tf>.csv`).

- **engine** = our Foundation engine's swings (`engine.run`, the swing detector Strategies 1-12 use), from their confirmation bar.
- **atr4** = "4 ATR swings" read as an ATR zigzag: a swing is confirmed when a bar closes 4 x ATR14 beyond the extreme since
  the last opposite swing. No such swing exists anywhere in the code base, so this reading is an assumption.
- **atr4_life10** = sensitivity only, `atr4` with a 10-session level life (the 3-session life leaves too few levels).

| net INR per trade (trades) | 5 min IS | 5 min 2026 | 1 min IS | 1 min 2026 |
|---|---|---|---|---|
| pivot (first run), every break | -828 (717) | -900 (121) | -1,089 (4,680) | -1,286 (780) |
| **engine swings**, every break | -918 (2,175) | -1,157 (317) | -1,090 (11,666) | -1,199 (1,776) |
| **engine swings**, after pressure | -938 (1,503) | -1,116 (235) | -1,070 (8,299) | -1,182 (1,327) |
| **4 ATR swings**, every break | -1,659 (28) | none (0) | -934 (303) | -1,105 (51) |
| **4 ATR swings**, after pressure | -1,323 (16) | none (0) | -919 (164) | -960 (33) |
| 4 ATR, 10-session life, every break | -1,718 (34) | +2,700 (1) | -931 (337) | -1,103 (58) |

| gross points per trade, IS / 2026 · timing-control percentile IS / 2026 | 5 min | 1 min |
|---|---|---|
| engine swings, every break | +2.1 / -0.7 · 97.7 / 44.2 | -0.6 / -1.3 · 0.2 / 2.9 |
| engine swings, after pressure | +1.8 / -0.0 · 90.0 / 55.0 | -0.2 / -1.0 · 13.0 / 7.0 |
| 4 ATR swings, every break | -9.5 / - · 11.8 / - | +1.9 / +0.2 · 88.9 / 59.3 |
| 4 ATR swings, after pressure | -4.4 / - · 36.2 / - | +2.1 / +2.4 · 87.4 / 74.1 |

How many levels each source makes (5 min / 1 min): our engine marks 26,561 / 130,819 swings, which pair into 4,815 /
27,296 broken levels; the 4-ATR zigzag marks 1,901 / 9,737 swings and only 38 / 429 broken levels.

**Reading.**
- **Our engine's swings make it worse, not better.** They are small and frequent, so they produce three times more levels
  than the generic pivots, and those levels carry less move: on 5 minutes +2 gross points in sample and nothing in 2026;
  on 1 minute the breaks are fake-outs, below both controls (0-13th percentile).
- **The 4 ATR swings are cleaner on 1 minute but still far short.** Breaks of a level made by two 4-ATR swing highs (or
  lows) move about +2 points, beat random timing at the 87th-89th percentile in sample (not 95), and lose about 920-1,100
  INR per trade. On 5 minutes the zigzag makes too few double tops / bottoms to judge (16-34 trades in five years, none in
  2026), and those few lost.
- No source passes the pre-registered rule; none has a positive mean in any window with enough trades to read.
- Look-ahead check identical for `atr4` and `atr4_life10` on both timeframes (`trunc_check_sources.json`); the engine's
  swings were checked by the fz_v3 build.
- One mismatch to keep in mind: the stop stays 1 ATR beyond the level for every source, which is tight relative to a
  4-ATR swing. A stop scaled to the swing (for example beyond the last opposite 4-ATR swing) is a different trade rule and
  would be a new run.

## If you want to take it further

Each of these is a new pre-registered run, not a tweak of this one: the real Pine source if you can paste it (the biggest
unknown); 15-minute or hourly bars where moves are larger relative to cost; holding past 15:25 (S47: the overnight holds
are where the lab's books made money); or the 5-minute filtered break as a confirmation inside an existing strategy rather
than a stand-alone entry.
