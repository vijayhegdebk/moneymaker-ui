# Levels Likely to Break (Zeiierman): reconstruction and backtest, pre-registration

Written 2026-10-03 before any result was computed. Source the user gave:
https://www.tradingview.com/script/S0JjlgsE-Levels-Likely-to-Break-Zeiierman/

## What is known about the indicator

The script page and the author's site are blocked by this environment's network proxy, so the Pine source and the full
description could not be read. What the published description says (via search snippets):

- It is "a market-structure and pressure-analysis indicator that identifies repeated price levels and monitors when
  conditions begin to build toward a potential break".
- It does not plot every swing: it "looks for two confirmed pivots forming around the same price area". The first pivot
  becomes a hidden candidate; if a second same-side pivot forms within the matching tolerance, the level is drawn.
- Highs and lows are compared "using a volatility-adjusted tolerance instead of requiring exact price equality".

Everything else (pivot lengths, the tolerance multiple, how "pressure" is scored, any signal rule) is unknown. The
reconstruction below fixes each unknown to one value now, labelled as an assumption. No value is tuned on the results.

## Reconstruction (every number fixed here)

| item | rule | status |
|---|---|---|
| pivot high / low | bar k is a pivot high if its high is above the 5 bars before and at least the 5 bars after; confirmed only at bar k+5 | assumption (L = R = 5) |
| tolerance | two same-side pivots match if their prices differ by at most 0.25 x ATR14 at the second pivot's confirmation bar | assumption (0.25) |
| level | resistance = the higher of the two pivot highs, support = the lower of the two lows; active from the second pivot's confirmation bar | assumption |
| candidate life | a pivot stays a candidate for 3 sessions' worth of bars (225 on 5 min, 1,125 on 1 min); a close beyond it kills it | assumption |
| level life | a level lives until it breaks, until the contract changes, or for the same 3 sessions' worth of bars | assumption |
| break | the first close beyond the level (above resistance, below support) after the level is active | the indicator's thesis |
| pressure (variant B) | before the break: at least one retest (a bar after formation whose high came within the tolerance of resistance, or low of support, and closed back inside) AND the last 10 bars' lows rising into resistance (highs falling into support), slope of a least-squares line > 0 / < 0 | assumption, the one "pressure" rule tested |

## Trade rule (both variants)

- Enter at the breaking bar's close in the break direction (long above resistance, short below support).
- Stop: the other side of the level by 1.0 x ATR14 at the entry bar. Target: 2R. Square-off at the last bar opening at or
  before 15:25 of the entry session, or the contract's last bar if earlier.
- Fill conventions (the lab's and the backtest-rules skill's): no entry on a session's first bar; an open beyond the stop
  fills at the open; a bar touching both stop and target counts as the stop; entries only before 15:25.
- One position at a time per timeframe; signals during an open position are skipped.
- Pricing: NIFTY near-month futures, lot 65, 5 pts slippage per side, `lab.trade_charges(ZERODHA_NFO_FUT)`, exactly as
  Strategies 1 / 2.

## Data and windows

`fz_v3/out/data/<tf>/bars.parquet` (the cloud rebuild of the committed near-month futures files, identical to the local
build), 1 minute and 5 minute. Reported separately: IS 2021-10-01..2025-12-31 and 2026-01-01..2026-09-25 (OOS for this
study: nothing is fitted, so OOS here only means "not the period most of the lab's earlier studies looked at").

## Judgement

Net INR per trade, win rate, profit factor, t-statistic of the per-trade mean, worst week, share of positive weeks, MFE /
MAE, for variants A (every break) and B (break after pressure), both timeframes, both windows. Controls beside every number:

1. **Direction control**: the same entry bars and the same stop / target distances with the direction drawn at random
   (1,000 seeded draws): does the break direction carry information?
2. **Timing control**: each trade moved to a random allowed bar of the same session, same direction, same stop distance in
   ATR units (1,000 seeded draws): does the level timing carry information?
3. The gross-points view (before slippage and charges), so cost and signal can be told apart.

A variant "works" only if its net mean is positive in both windows and it sits at or above the 95th percentile of both
controls. Anything else is reported as it is.

## Look-ahead check

Pivots are used only from their confirmation bar. A truncation test reruns the signal generation on bars cut at
2025-06-30 12:00 and asserts every signal before the cut is identical.

## Amendment 1 (2026-10-03, after the 5-minute results were seen; the trade rule is unchanged)

The timing control as first written drew a random bar of the **same session** and kept the trade's side. The side is the
break direction, which encodes where price went later that day, so random entries placed before the break inherited the
day's move: on 5 minutes the random trades averaged +11.1 gross points against +3.5 for the real trades. That control is
biased, not informative. Replaced by: the same time of day (session bar), the same side, the same stop in ATR units, in a
randomly drawn **other session of the same window** (1,000 seeded draws). The direction control (same bars, random side)
had no such leak and is unchanged. The first version's 5-minute numbers are kept in `run_v1.log` for the record.

## Amendment 2 (2026-10-03): the levels built from our own swings (user: "these have to be incorporated within our swing high low or 4 ATR swings")

Written after the first run's results were seen; nothing else is tuned. The only change is the source of the swings that
the level rule pairs; the tolerance (0.25 x ATR14), level life (3 sessions), break, pressure filter, trade rule, costs,
controls and pass rule are exactly as above.

| run | swing source |
|---|---|
| `pivot` | the generic 5 / 5 pivots of the first run (reference; reproduces its 1,186 / 5-minute signals bit for bit) |
| `engine` | our Foundation engine's swings (`engine.run`, Strategy 1 rules on 1 minute, Strategy 2 on 5 minutes; `fz_v3/out/data/<tf>/swings.parquet`), used from their confirmation bar |
| `atr4` | "4 ATR swings", read as the ATR zigzag: a swing high is confirmed when a bar closes at least 4 x ATR14 below the highest high since the last swing low (mirror for lows). No such swing exists in the code base (searched the lab, the Java app, every branch and the history), so this reading is an assumption |
| `atr4_life10` | sensitivity only: `atr4` with a 10-session candidate / level life, because the 4-ATR zigzag gives under two swings a session and the 3-session life leaves 38 broken levels in five years on 5 minutes. Labelled as a sensitivity, not a candidate |

Look-ahead: `pivot` and `atr4` are re-checked on the truncated bars (`trunc_check_sources.json`); the engine's swings were
checked by the fz_v3 build's truncation diff (`fz_v3/out/QUALITY.md`, swings as of the cut identical).
