# FZ v3 cloud build: quality log (2026-09-29)

BRIEF addendum 5: the cloud run starts from scratch; `fz_v3/built/` (the local build under a 1 GB / 2-process limit) is a
cross-check only; a local number the cloud rebuild does not reproduce is discarded and recorded here.

## Environment

Cloud container: 4 cores, 15 GB RAM, no GPU. Python 3.11.15; numpy 2.4.6, pandas 3.0.6 (the local build used 2.3.3 on
Python 3.10), pyarrow 25.0.1, scipy 1.17.1, scikit-learn 1.9.1, xgboost 3.2.0, lightgbm 4.7.0, shap 0.51.0, numba 0.67.0,
statsmodels 0.15.0, hmmlearn 0.3.3, mapie 1.5.0, ruptures 1.1.10, arch 8.0.0, stumpy 1.14.1, torch 2.14.0 (CPU wheel; the
pytorch.org index is blocked by the proxy, PyPI served it), joblib 1.6.0, matplotlib 3.11.2, psutil 7.2.2. Every library the
design panel names is present, so nothing is hand-coded for lack of a package.

## Build (`out/build/build.py`, one process per timeframe, `engine.load` on the full committed files)

| | 1 minute | 5 minute |
|---|---|---|
| bars / sessions | 443,826 / 1,188 | 88,771 / 1,188 |
| first / last bar | 2021-10-01 09:15 / 2026-09-25 15:29 | 2021-10-01 09:15 / 2026-09-25 15:25 |
| front_month = 0 bars / zero-volume bars | 0 / 4 | 0 / 2 |
| engine.run wall time | 306 s (local box: 958 s) | 10 s (local: 51 s) |
| whole build, peak RSS | 351 s, 1.66 GB | 20 s, 0.54 GB |
| swings / events (CHoCH, BOS) | 130,843 / 39,608 (8,054, 31,554) | 26,578 / 7,950 (1,532, 6,418) |
| SETUPs = Foundation trades, engine-skipped | 5,326, 0 | 1,012, 0 |
| rooms / watches / ST7-ST8 positions (TAKE + REENTER) | 6,802 / 2,644 / 711 + 164 | 4,673 / 476 / 269 + 124 |

## Cross-check against the local build (`out/build/compare.py`, `data/<tf>/compare.json`)

**Identical on both timeframes:** the SETUP list, every Foundation trade (entry, exit bar, exit price, pts, charges, net, stop,
exit reason), every FZ position (entry, exit, pts, net, gate, room id, fill, reenter reason), the per-bar room card (zone, visit,
bars, read, left room, outside run, containing room, wick depth, touches, cluster sit, leave R4), every room (id, edges, birth,
retirement), the event list and the swing list. The local numbers in `built/*/README.md` and `meta.json` are therefore all
reproduced (IS 1m: 4,502 trades, net -4,150,085.95, 684 wins; 5m: 832, -230,262.16, 184; ST7 745 kept IS / 130 OOS, ST8 325 / 68),
and nothing from the local build is discarded.

**Feature columns that differ, by definition (cloud definitions are the ones the studies use):**
- `range_1h/3h_atr` (local 5m `range12/36_atr`): the cloud windows stop at the session's first bar (157 / 378 of 1,012 rows differ,
  the ones whose window crossed the overnight gap in the local build).
- `hv3_*` (5m): the cloud baseline is the same-session median of the previous 20 bars with at least 5 of them (the local 5m build
  used a cross-session 20-bar median): 466 rows differ in `hv3_bars_since`, 600 in `hv3_dir`. The 1m `vol_hv*` columns (same
  definition as the cloud) are identical.
- `fnd_mfe_pts` / `fnd_mae_pts` (5m): the cloud follows `lab.excursion` (MFE >= 0, MAE <= 0); the local 5m build kept raw signs
  (1,008 MAE rows differ in sign, 7 MFE rows where the high never exceeded the entry). The 1m columns are identical.
- 1m `reg_range60_atr` and `reg_prior_closed_pts_today` have no cloud twin (`range_1h_atr` is same-session; `today_pts_asof` uses
  `exit <= k`, the same rule); every other shared 1m feature column is identical, including all `lvl_touch_*` verdicts and the
  `card_*` / `st7_*` (now `fz_*`) gate columns.
- New in the cloud table (not in either local table): the L1 label (`l1_*`), `n_choch_since_bos_today`, `alt_dir6` + `alt_kind6`,
  `er_1h`, `ret_1h/3h_pts`, `today_pts_asof`, `fz_pos_in_band_dir`, `fz_band_width_atr`, `fzpos_l1_*`.

## Causality (`out/build/trunc_diff.py`, cut 2025-06-30 12:00:00, mid-session)

The same build on the bars up to the cut against the full build: **PASS on both timeframes.** 1 minute: 335,934 bars, 3,807 SETUPs
at or before the cut, all 201 as-of columns identical, bars (atr14, protected level, volume baselines) and the whole room card
identical, swings / events / rooms as of the cut identical, the ledger's gate columns identical, the 3,806 closed trades identical;
only the `fnd_*` label columns of the trades still open at the cut differ. 5 minutes: 67,192 bars, 718 SETUPs, the same result.
So no as-of column depends on bars after the SETUP bar. Any extended feature a study adds must pass the same diff
(`data/<tf>/trunc_20250630_120000/` holds the truncated bars and tables for that).

## The two labels (pre-registration, `results/pre_registration.json`)

| IS book | 1m L0 (engine exit) | 1m L1 (15:25 cut) | 5m L0 | 5m L1 |
|---|---|---|---|---|
| units | 4,502 | 4,452 (50 SETUPs open at / after 15:25 not taken) | 832 | 826 |
| net INR / mean per trade | -4,150,086 / -922 | -4,494,773 / -1,010 | -230,262 / -277 | -625,325 / -757 |
| win rate | 15.2% | 15.6% | 22.1% | 27.7% |
| trades the cut changed | | 473 (`eod` 471, `expiry` 2) | | 289 (`eod` 280, `expiry` 9) |
| top-decile winners' share of gross wins | 57.9% | 44.7% | 45.5% | 31.3% |
| mean cost (charges + 650 slippage) | 1,048 | 1,048 | 1,050 | 1,050 |

The 15:25 cut removes the overnight holds, which were the profitable part of the engine's book (S47), so the L1 book that
ST13/ST14 would trade is worse than the engine's, most on 5 minutes (-757 vs -277 per trade). Every gate is judged on L1 (the
book a `square_off 15:25` strategy trades) with L0 as the robustness table; this is stated on every OOS table.

**The frozen ST7/ST8 gate on L1 (the comparator):** 1m kept 745 of 4,452 (16.7%), kept mean -1,026 vs skipped -1,006 (diff -20,
permutation p 0.85, session-matched control 62.6th percentile, loser recall 0.84 but it also skips 82% of the winners' net and
84% of the top-decile winners); 5m kept 325 of 826 (39%), kept mean -979 vs skipped -613 (diff -366, p 0.24, 13.6th percentile).
The frozen gate fails every go / no-go item except the kept-n floors: it is not a loser filter (H1 in `studies/h1_gate_audit`).

**Break tests on the per-session L1 net (active IS sessions, 578 on 1m / 408 on 5m):** BDE CUSUM finds no break inside IS
(max band ratio 0.56 / 0.53); the HAC Chow tests per calendar year are all p > 0.14 except 5m 2023 (t -2.40, p 0.017: the 5m
book's mean per session fell from +631 to -498 in 2023); the IS / OOS boundary Chow test is p 0.63 (1m) / 0.56 (5m): no boundary
break at 5%, so OOS is read as the same process and no time-decay weighting is forced (the c = 0.5 variant is still reported as a
sensitivity in the meta-label study, as the design says).

## Run log: interruptions, repairs, harness changes (2026-09-29)

- **Two cut-offs by the model's usage limit** (about 06:30-11:00 UTC and 14:05-15:20 UTC). The studies' own `nohup` processes
  kept running; the agents were resumed with the workflow journal cache and continued from the files (`STUDY_AGENT_BRIEF.md`,
  "Resuming"). Nothing was rerun that had finished; the logs that lost their final lines are named in the affected FINDINGS.
- **Git incident** (06:24 UTC): the re-signing rebase stalled and its checkout replaced every tracked file's inode, so the running
  processes wrote their logs to unlinked inodes until a mirror loop copied them back (`PROGRESS.md`). One ledger row was restored
  from the unpicked commit; the ledger is append-only and its ids are unique (checked at every checkpoint).
- **Harness changes during the run**, each traced to a refuter's finding and applied so that a pass can only become a fail:
  `spa` excludes near-degenerate candidates from the studentised family (min active sessions) and reports White's unstudentised
  statistic; the activity test is a 0.01 INR tolerance (`SPA_ACTIVE_TOL_INR`), not 1e-9 (lab replays carry ~1e-3 INR of float
  noise against the 2-dp labels); `go_no_go` requires the null-tape checks and the candidate's columns (`TIME_PROXIES` = `sl`,
  `n_events_asof` refused as calendar rules; they stay in the design matrices of the studies that were running, so the refusal
  is at the candidate). `oos_once.py` refuses a candidate whose provenance lacks those checks.
- **Registrations corrected, never rewritten**: the shortlist note "frozen before any gate search" -> "frozen before the phase-3
  gate studies" (1,600 pre-registered grid rows preceded it); the round-0 rule with a unit error; all as appended lines.
- **OOS opened once** (`oos_once.py`, `results/oos.json`, registration line `oos_opened`): no candidate had passed, so only the
  comparators were scored (raw book and the frozen ST7/ST8 gate, both labels, both timeframes).

## Splitter (`harness.check_splits`)

12 contiguous blocks of 85-86 IS sessions; IS rows per block 1m 170-512, 5m 31-83; purged training rows per block 0-29 (1m),
0-8 (5m); 66 CPCV splits; every IS row tested exactly once in the 12-block scheme; no training row's label lifetime intersects
its test block; no training row sits in the 3-session embargo (asserted).
