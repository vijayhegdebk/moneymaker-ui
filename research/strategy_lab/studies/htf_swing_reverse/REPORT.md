# 1-hour swing direction, one 1-minute trade, one reverse if it fails: backtest

Run 2026-10-03 by `htf_swing_reverse.py` (rules fixed beforehand in `PREREG.md`; numbers in `results.json` / `run.log`;
every trade in `trades_E1.csv` / `trades_E2.csv`). NIFTY near-month futures, lot 65, 5 pts slippage per side, Zerodha
charges, square-off 15:25. Simulated only.

**The rule.** Build 1-hour bars from the 1-minute bars and run our engine's swing detector on them. The 1-hour direction is
up after a confirmed 1-hour swing low and down after a confirmed swing high. Once a day, take one 1-minute trade in that
direction: **E1** at the first Strategy 1 SETUP of the day that agrees with it (our Foundation entry and stop), **E2** at
the 09:20 close with the latest 1-minute swing as the stop. Exit at the stop, at 2R, or at 15:25. If the first trade is
stopped out, take one reverse trade at the stop price with the same risk, then stop for the day.

## Result: it loses money in both windows, and the 1-hour direction does not beat a coin flip

| | E1 (1-min SETUP entry) | E2 (09:20 entry) |
|---|---|---|
| days traded 2021-25 / 2026 | 523 / 95 | 792 / 123 |
| net per day 2021-25 / 2026 (INR) | -1,438 / -2,947 | -1,305 / -2,320 |
| net per trade 2021-25 / 2026 | -902 / -1,772 | -830 / -1,502 |
| total 2021-25 / 2026 (INR) | -7.52 L / -2.80 L | -10.34 L / -2.85 L |
| win rate / profit factor 2021-25 | 36% / 0.52 | 33% / 0.58 |
| first trade stopped out | 60% / 66% | 57% / 55% |
| first trades: net per trade 2021-25 / 2026 | -988 / -1,902 | -877 / -1,366 |
| reverse trades: net per trade 2021-25 / 2026 | -756 / -1,575 | -749 / -1,751 |
| gross points per trade 2021-25 / 2026 | +2.2 / -10.1 | +3.5 / -6.0 |
| worst week 2021-25 (INR) | -33,454 | -33,102 |
| positive weeks 2021-25 | 25% | 31% |
| **direction control percentile** 2021-25 / 2026 | **14.5 / 74.3** | **38.7 / 48.7** |

Direction control: the same days and entry bars with the first trade's direction chosen at random (the reverse rule then
applied as usual), 1,000 draws. A percentile of 50 means "no better than a coin flip"; the pass mark was 95.

## What it means

- **The 1-hour swing direction carries no information for the next 1-minute trade.** With random directions the book does
  about as well (E2: 39th-49th percentile) or better (E1 in 2021-25: the real direction is at the 15th percentile).
- **The first trade is stopped out more often than not (55-66%)**, because the 1-minute stop is tight relative to normal
  1-minute noise, so the reverse trade is taken on most days.
- **The reverse trade does not rescue the day.** It is slightly less bad than the first trade in 2021-25 (about +4 to +5
  gross points against about +1 to +3), but still loses about 750 INR after costs, and in 2026 it loses more than the first
  trade. Taking it doubles the number of round trips and so roughly doubles the cost per day.
- As in the other studies, a trade here moves a few points before costs while each round trip costs about 16 points.

## Pass rule (fixed in PREREG.md)

The day-cycle net per day must be positive in both windows and at or above the 95th percentile of the direction control.
**Neither variant passes**; both are negative everywhere.

## Second run: stop at the 1-hour swing, risk 1R (PREREG.md, Amendment 1)

User: "Yes, SL is of 1 hour and risk is 1R." The first trade's stop is the last 1-hour swing low (long) or high (short);
R = entry to that stop; target 2R; 15:25 exit; the reverse starts at the stop price with the same 1R. Nothing else changed
(`results_1h.json`, `run_1h.log`, `trades_E1_1h.csv`, `trades_E2_1h.csv`).

| | E1 (1-min SETUP entry) | E2 (09:20 entry) |
|---|---|---|
| days traded 2021-25 / 2026 | 520 / 94 | 897 / 133 |
| **net per day** 2021-25 / 2026 (INR) | **-842 / -189** | **-1,242 / -205** |
| net per trade 2021-25 / 2026 | -719 / -168 | -1,005 / -168 |
| total 2021-25 / 2026 (INR) | -4.38 L / -0.18 L | -11.14 L / -0.27 L |
| win rate / profit factor 2021-25 | 43% / 0.73 | 41% / 0.68 |
| win rate / profit factor 2026 | 48% / 0.94 | 46% / 0.95 |
| average result in R 2021-25 / 2026 | +0.10 R / +0.10 R | +0.05 R / -0.01 R |
| median stop (1R) in points | 130 (173 in 2026) | 132 (145 in 2026) |
| how trades end, 2021-25 | 76% at 15:25, 17% stop, 7% target | 63% at 15:25, 26% stop, 11% target |
| first trade stopped out | 17% / 13% | 24% / 22% |
| first trades: net per trade 2021-25 / 2026 | -979 / -361 | -1,014 / -37 |
| reverse trades: net per trade 2021-25 / 2026 | **+800 (89 trades) / +1,349 (12)** | -967 (211) / -773 (29) |
| worst week 2021-25 (INR) | -52,379 | -66,422 |
| direction control percentile 2021-25 / 2026 | 83.2 / 90.9 | 40.8 / 85.6 |

**What changes with the 1-hour stop.**
- The wide stop (about 130-170 points) means the first trade is rarely stopped (13-24%) and the 2R target (about 260-340
  points) is almost never reached in one day, so most trades simply close at 15:25. The trade becomes "hold in the 1-hour
  direction until the end of the day".
- **Losses fall sharply** (E1 from -1,438 to -842 INR per day in 2021-25, and to -189 in 2026), because there are far fewer
  stop-outs and reverses, so far fewer round trips paying about 16 points each.
- **E1's reverse trades made money**: +800 INR per trade in 2021-25 (89 trades, profit factor 1.56) and +1,349 in 2026
  (12 trades). When a Foundation SETUP in the 1-hour direction fails all the way through the 1-hour swing, the move tends
  to continue the other way. But 89 trades with a t-statistic of 1.2 is not enough to call it real, and it was found after
  looking at the data, so it needs its own test before anyone relies on it.
- E1's 1-hour direction now beats random directions more often (83rd and 91st percentile) but not at the 95th needed.
- In risk terms each day makes about +0.1R before costs on E1; at 1 lot the costs take more than that.

**Pass rule: neither variant passes** (net per day negative in both windows, direction control below 95).

## Look-ahead check

The whole pipeline rerun on 1-minute bars cut at 2025-06-30 12:00: E1 708 / 708 and E2 1,085 / 1,085 entries before the
cut identical, closed trades identical (`trunc_check.json`). With the 1-hour stop: E1 515 / 515, E2 981 / 981, identical
(`trunc_check_1h.json`).

## Assumptions to know

- "1-hour swing" = our engine's swing detector on 1-hour bars; the direction = the current swing leg. A different reading
  (for example the engine's CHoCH trend on 1 hour, or a 4-ATR zigzag on 1 hour) would be a new run.
- "Failed" = stopped out; target 2R; the reverse uses the same risk and starts at the stop price.
- The 1-hour bars are built across contract rolls on the continuous near-month series.

## If you want to take it further (each a new run)

A wider first-trade stop (the 1-hour swing point instead of the 1-minute swing), holding the first trade beyond 15:25 when
it agrees with the 1-hour leg, or the 1-hour direction as a filter on 5-minute entries.
