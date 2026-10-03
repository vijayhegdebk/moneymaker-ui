# FZ v3: the trading playbook (cloud run of 2026-09-29, branch `research/strategy-lab-pwxiug`)

Written 2026-09-29 from the files under `fz_v3/out/` only. Every number below is copied from one of them and the source is
named beside it (a study's `FINDINGS.md` with the ledger id where one exists, `results/pre_registration.json`,
`results/oos.json`, `QUALITY.md`, `PROGRESS.md`, `ledger/registrations.jsonl`, `features_shortlist/<tf>/shortlist.json`).
Nothing was recomputed and no OOS row was read: `results/oos.json` is the only OOS source. INR per trade unless stated;
1 min and 5 min side by side; every kept-vs-skipped number carries its session-matched random-control percentile (`ctrl`),
its permutation p (`perm p`) and, where a study computed one, its CPCV 5th percentile (`CPCV p5`).

Abbreviations: IS = 2021-10-01..2025-12-31; OOS = 2026-01-01..2026-09-25; L1 = the 15:25 intraday book (the one ST13/ST14
would trade), L0 = the engine's uncut trade (robustness only); `diff` = kept mean net minus skipped mean net; `slip8` = the
kept book's mean at 8 pts slippage per side; blocks = harness blocks of 12 where kept mean > skipped mean.

---

## 1. The answer in one page

**What the program found.** Fourteen studies, about 4,200 ledger rows (`ledger/trials.jsonl`, 4,226 lines at 18:12 UTC),
every one judged by the same pre-registered rule. **No gate, no exit, no session stop, no regime state, no LLM rule and no
online learner passed.** No candidate was frozen, `candidates/` does not exist, and the single OOS opening
(`results/oos.json`, 18:06:55 UTC, `candidates: []`) scored only the comparators. The book these rules were meant to
rescue loses 1,010 INR per trade on 1 min and 757 on 5 min in sample (`pre_registration.json` `raw_book.is_mean`), of which
about 1,050 is cost (`mean_cost_inr` 1,047.54 / 1,049.86). No kept book of any study has a positive mean at 8 pts slippage
(`operating_point_sizing/FINDINGS.md` §0: 0 of 326 kept books, 1 at 3 pts; `online_learner/FINDINGS.md` §0: 0 of 468 paths
per timeframe; the gate_family, regime_gate and online_learner finalists' kept books at 8 pts are -1,378 / -1,396 / -1,089,
-971 and -278 / -499, §4.8, §4.11, §4.12). At the label's 5 pts the only positive kept means are 68-103-trade 1 min
online-learner paths (best +112.36, `19f7ff81224bafa0`, kept 68 of 4,452; it fails the kept-share and kept-n floors, the
control (0.1) and the block test (2 / 12); `online_learner/FINDINGS.md` §0, §2) and L0 robustness rows of the H1 audit
(5 min take_only `2ad039c7d19cf22d` +126.30, take_or_reenter `5d3759e3d6038faa` +133.81, ctrl 28.9 / 31.4;
`h1_gate_audit/FINDINGS.md` §3).

**What to take and what to skip, in the user's terms.** The honest answer is "nothing beyond Foundation" in every column.
The measured reason for each:

| the user's question | what was measured (IS, L1) | 1 min | 5 min | control beside it | verdict | source |
|---|---|---|---|---|---|---|
| "CHoCH, CHoCH, no break = sideways; sideways hurts" | Foundation mean net by `n_choch_since_bos` 0 / 1 / 2 / 3 / 4+ | -1,090 / -998 / -1,030 / -837 / -936 (n 1,169 / 1,739 / 823 / 372 / 349) | -717 / -647 / -1,439 / -336 / -289 (n 235 / 332 / 143 / 54 / 62; se 290-607) | gate "skip when >= 2": 1 min diff -72.50, ctrl 1.4, perm p 0.37, 4/12 blocks; 5 min diff +257.83, ctrl 45.9, perm p 0.46, 6/12; on memory-free tapes the 5 min gate reaches +516 / +500 at p95, real at the 80th pct | **not the losers**; the two-CHoCH SETUPs are not worse than the rest on 1 min, and on 5 min the +258 sits inside the engine's own null | `h2_h3_h4/FINDINGS.md` §2.1 (ids `dc7448312b5f9102`, `cdd9b4281b0e451c`); `null_tapes_drift/FINDINGS.md` §4 |
| "check how price reacts at visibly high volume" | SETUPs within 15 bars after a volume >= 2 x median-20 bar, by direction agreement: agree / disagree / none | -1,017 / -1,061 / -958 (n 2,496 / 801 / 1,155) | -830 / -812 / -667 (n 382 / 84 / 360) | `skip_if_disagree`: 1 min diff +63, ctrl 11.4, perm p 0.54; 5 min +61, ctrl 0.2, p 0.91; nested H3 pick 1 min diff -172, ctrl 0, CPCV p5 -298 | **does not select**; the 30-bar move after a high-volume bar is the baseline's (1 min -0.02 ATR vs -0.02; 5 min +0.04 to +0.20 vs +0.01 across the six v x N cells; the v=2 / N=20 cell alone is +0.09) | `h2_h3_h4/FINDINGS.md` §2.2 (ids `957a9431eef861e2`, `5694b41eb921fb5b`), §1 |
| "levels are respected; a break means a large move, else retest, retest, respect" | P(break) by earlier respects of the same swing 0 / 1 / 2 / 3+ | 0.69 / 0.47 / 0.47 / 0.46 | 0.46 / 0.45 / 0.43 / 0.45 | move after a confirmed break vs after a respect vs any bar (30-bar abs median, ATR): 1 min prot 2.24 / 2.33 / 2.11; 5 min prot 2.07 / 2.01 / 1.91; SETUPs after a room "broke" vs "held": 1 min -1,014 vs -1,096; 5 min -610 vs -1,394 (n 149 / 61) | **measurable, not predictive**: a break does not lead to a larger move, and SETUPs at respected levels are not better; all 9 touch-verdict gate cells fail per table | `h2_h3_h4/FINDINGS.md` §2.3 |
| time of day | where the L1 winners are and what the frozen gate does with them | before 09:25: 189 SETUPs, mean -843, 25 % winners, 28 big winners, the gate keeps 2 % (all 28 skipped); 14:00 bin: 58 of 62 big winners skipped; `eod` (15:25-cut) exits are the only profitable class: 471 rows, +2,930 mean, 61 % winners | before 09:25: 50 SETUPs mean +127, 15 big winners, 14 skipped; `eod` 280 rows +3,467, 72 % winners | the only near-miss of the run is an hour rule: "skip 11:00-11:59 shorts" (1 min): frozen diff +326, ctrl 86.2; nested +190 to +192, ctrl 22-47, CPCV p5 +153 to +160, 9-10/12 blocks; fails slip8 (-1,378), PBO 0.40, DSR p 1.0, SPA p 0.94 and the segment-tape p95 (562 vs 289) | **no hour rule passes**; the opening-minutes effect flips sign between the two IS halves (`llm_round1`), and the 11:00 skip reads like the calendar plus the 15:25 cut on memory-free tapes | `h1_gate_audit/FINDINGS.md` §5; `gate_family/FINDINGS.md` §0, §4; `llm_round1/FINDINGS.md` §9 |
| room read (the ST7/ST8 card) | what the frozen gate keeps by read | keeps 55 % of ACCEPTED, 49 % FIRST_PRINT, 31 % LEAVE, 2-3 % of the rest; kept LEAVE -972 vs refused LEAVE -935; NEW -831 and RECYCLE -539 are the best pools and are skipped at 97-98 % | refused leave branch -125 vs -838 for the 221 leave TAKEs; THIN (48 rows, -43) and `open_pierce` (31, -150) are the best pools and are skipped entirely | `skip_only:WATCH:leave_into_recycle` (5 min) diff -822, ctrl 0.1, perm p 0.088: the nearest thing to a signal points **against** the frozen rule | **the card does not separate winners from losers**; precision of the skip pile = base loser rate (1 min 0.847 vs 0.844; 5 min 0.721 vs 0.723) | `h1_gate_audit/FINDINGS.md` §3, §5, §8 |
| sizing | conditional on a passed gate | not run | not run | half-Kelly on the online learner's calibrated p_win returned 0 lots on 38 of 68 takes (1 min) and 68 of 140 (5 min) | **lots = 1 or skip** (the design's default verdict) | `operating_point_sizing/FINDINGS.md` §5; `online_learner/FINDINGS.md` §0 |
| exit | 1,568 managed-exit variants, hindsight imitation, fitted Q-iteration on frozen entries | best nested pick = Foundation's own stop with no target, no trail, no next-CHoCH exit: +86.57 vs Foundation (t 2.17, random-exit pct 100, CPCV p5 +54, 10/12 blocks) but still -923 per trade; SPA p 0.322 fails; the +87 is 45 trades' runner effect (top 1 % of gains contribute +153 per trade, the other 4,407 net -67) | nested pick -61.31 (worse than Foundation); FQI -145.34 (CI [-302, -1]: hurts) | random-exit control and family SPA in the row | **keep the Foundation exit** (stop / next CHoCH / 15:25) | `exit_policy/FINDINGS.md` §3, §9, §11.2 |
| a learned rule (RL / generative) | meta-labelling, policy trees, scorecards, LLM rules (blind and table-informed), HMM/GMM/jump states, ROCKET shapes, contextual bandits with a journal | 0 of 432 gate_family rows, 0 of 468 online paths, 0 of 8 + 16 LLM rules (round 0 + round 1, per timeframe), 0 of 12 rocket gates pass | 0 of 540, 0 of 468, 0 of 8 + 16 LLM rules, regime gate 0 of 5 models | the ceiling model (276-feature bagging) ranks winners at OOF AUC 0.59 (1 min) / 0.50 (5 min) and its gate keeps every row | **nothing learnable at this sample and cost**; sequential RL is not justified (one-step decision, counterfactual observed) | `importance/FINDINGS.md`; `gate_family/FINDINGS.md` §6 |

**Why the frozen ST7/ST8 gate looks good and is not.** Its whole gain over Foundation is the cost it saves by trading less:
on 1 min L1 the gain is 3.73M INR of which 3.88M is avoided cost and -0.15M is selection (the skipped SETUPs had a positive
price move in aggregate); on 5 min 265k of which 526k is avoided cost and -261k selection (`h1_gate_audit/FINDINGS.md` §4,
bridge closes to 0.05 INR). It skips losers in exact proportion to how much it skips (1 min loser recall 0.835 = skip share
0.833) and throws away 83 % (1 min) / 63 % (5 min) of the winners' net.

**The OOS reading of the same gate** (`results/oos.json`, the comparator only): on 1 min it kept 130 of 814 with diff +485
(ctrl 93.2, perm p 0.075, kept mean -734), on 5 min 68 of 176 with diff -748 (ctrl 49.5, perm p 0.30, kept mean -1,283);
the OOS standard error is about 185 (1 min) / 375 (5 min) INR per trade, so neither number is decidable, and the window
is not pristine (§2). No candidate exists to compare it with.

**What the user can do next** is in §5: every option is a user decision under Rule 0(c); none is recommended by the data.

---

## 2. The book being judged

### 2.1 The two labels on IS (`results/pre_registration.json`; `QUALITY.md` "The two labels")

| IS book | 1 min L0 (engine exit) | 1 min L1 (15:25 cut) | 5 min L0 | 5 min L1 |
|---|---|---|---|---|
| units | 4,502 | 4,452 (50 SETUPs open at / after 15:25 not taken) | 832 | 826 |
| net INR / mean per trade | -4,150,086 / -921.83 | -4,494,773 / -1,009.61 | -230,262 / -276.76 | -625,325 / -757.05 |
| win rate | 15.2 % | 15.6 % | 22.1 % | 27.7 % |
| active IS sessions / median SETUPs per active session | 579 / 8 | 578 / 8 | 408 / 2 | 408 / 2 |
| trades the cut changed | | 473 (`eod` 471, `expiry` 2) | | 289 (`eod` 280, `expiry` 9) |
| top-decile winners' share of gross wins | 57.9 % | 44.7 % | 45.5 % | 31.3 % |
| mean cost (charges + 2 x 5 pts x 65 slippage) | 1,048 | 1,048 | 1,050 | 1,050 |

L1 is the training and judging label because it is the book a `square_off 15:25` strategy trades; L0 is robustness only.
The 15:25 cut removes the overnight holds, which were the profitable part of the engine's book (S47 in
`docs/STRATEGY_ANALYSIS_TODO.md`; `QUALITY.md`): 5 min L1 -757 vs L0 -277 per trade. The BRIEF's cost figure (1,114 INR per
1 min trade) predates the build; the measured mean cost is the 1,048 / 1,050 above (`pre_registration.json` `mean_cost_inr`).

### 2.2 The frozen ST7/ST8 comparator on IS and on OOS (`results/oos.json`, tables `frozen_st7_st8`; the IS rows reproduce `pre_registration.json` on every non-Monte-Carlo statistic; the control percentile and permutation p are re-drawn: 62.3 vs 62.6 and 14.3 vs 13.6)

| | 1 min L1 IS | 1 min L1 OOS | 5 min L1 IS | 5 min L1 OOS |
|---|---|---|---|---|
| n / kept n (share) | 4,452 / 745 (16.7 %) | 814 / 130 (16.0 %) | 826 / 325 (39.4 %) | 176 / 68 (38.6 %) |
| all-rows mean | -1,009.61 | -1,141.40 | -757.05 | -823.62 |
| kept mean / skipped mean | -1,026.02 / -1,006.31 | -733.59 / -1,218.91 | -978.81 / -613.20 | -1,282.73 / -534.55 |
| **diff** | **-19.71** | **+485.32** | **-365.62** | **-748.18** |
| diff, top 1 % winners removed | -8.44 | +233.21 | -304.01 | -355.07 |
| kept mean at 3 / 8 pts slippage | -766 / -1,416 | -474 / -1,124 | -719 / -1,369 | -1,023 / -1,673 |
| ctrl pct / perm p (re-drawn in `oos.json`; `pre_registration.json` rows `f8ea66553101dc24` / `60662a5e5ab612f8`: 62.6 / 0.847 and 13.6 / 0.236) | 62.3 / 0.845 | **93.2 / 0.075** | 14.3 / 0.242 | 49.5 / 0.304 |
| loser recall / precision | 0.835 / 0.847 | 0.854 / 0.847 | 0.605 / 0.721 | 0.598 / 0.704 |
| winner recall (count / net-weighted) | 0.182 / 0.173 | 0.228 / 0.243 | 0.389 / 0.369 | 0.347 / 0.286 |
| top-decile winners skipped | 0.843 | 0.714 | 0.565 | 0.800 |
| kept PF | 0.327 | 0.546 | 0.563 | 0.444 |
| blocks (IS only) | 6 / 12 | n/a | 3 / 12 | n/a |
| kept sessions | 394 | 69 | 243 | 47 |

L0 robustness (same file): 1 min OOS diff +743.24 (ctrl 91.0, perm p 0.156, top-1 %-removed -3.77), 5 min OOS diff -779.92
(ctrl 77.9, perm p 0.525). The frozen gate fails every IS go/no-go item except the kept-n floors, and on 1 min also the
kept-share floor (16.7 % < 20 %) (`pre_registration.json` `frozen_go_no_go`).

**Standing caveats on the OOS window** (`results/oos.json` `caveats`): (1) the window is the published lab dashboard window
and was used by the ST9-12 exit grid (S50), so it is not pristine; (2) the label is the recomputed intraday book (exit forced
at the entry session's 15:25 bar), and every comparator is priced on the same label; (3) the OOS mean has a standard error of
roughly 185 (1 min) / 375 (5 min) INR per trade, so differences below about 500 / 1,000 are not decidable. The label-free
IS-vs-OOS covariate shift is AUC 1.00 (1 min) / 0.999 (5 min) (`oos.json` `drift_is_vs_oos`, explanatory only).

### 2.3 Break tests (`pre_registration.json` `break_tests`; `QUALITY.md`)

BDE CUSUM on the per-session L1 net finds no break inside IS (max band ratio 0.557 / 0.531); the HAC Chow tests per calendar
year are all p > 0.14 except 5 min 2023 (t -2.40, p 0.017: the 5 min mean per session fell from +631 to -498); the IS/OOS
boundary Chow test is p 0.63 (1 min) / 0.56 (5 min), so OOS is read as the same process and no time-decay weighting is forced.

---

## 3. Protocol and controls

| element | as run | source |
|---|---|---|
| Splitter | 12 contiguous IS blocks of 85-86 sessions (1 min rows per block 170-512, 5 min 31-83); purge = training rows whose label lifetime intersects the test block (0-29 per block on 1 min, 0-8 on 5 min); 3-session embargo, asserted; 66 CPCV splits -> 11 paths | `QUALITY.md` "Splitter"; `pre_registration.json` `splits` |
| Ledger | `harness.score()` is the only source of a kept-vs-skipped number; every configuration tried is an append-only row (`ledger/trials.jsonl`, 4,226 lines at 18:12 UTC; per-session vectors in `ledger/vectors/`); `split="OOS"` refused unless the caller is `oos_once.py` | `README.md` rules 2-3; `harness.py` |
| Judgement per row | diff, ctrl pct (2,000 session-matched draws), perm p (2,000 shuffles), loser recall / precision, net-weighted winner recall, top-decile winners skipped, diff with the top 1 % winners removed, kept mean at 8 pts, block sign count, kept floors | `README.md` rule 5 |
| Family statistics | PBO on diff (12,870 partitions), DSR with n_trials = family size, SPA (Hansen studentised, White unstudentised beside it; candidates active in fewer than max(10, 5 % T) sessions leave the studentised family; activity = abs gain > `SPA_ACTIVE_TOL_INR` = 0.01 INR), effective trials, stationary block bootstrap of sessions (2,000 draws, 90 % CI) | `harness.py` lines 474-483; `exit_policy/FINDINGS.md` §11.1; `PROGRESS.md` |
| Go / no-go (pre-registered) | PBO <= 0.2; CPCV p5 diff > 0; DSR p < 0.1; kept share >= 20 %; kept n >= 300 (1 min) / 80 (5 min); diff > 0 with the top 1 % winners removed; kept mean at 8 pts > 0; >= 8 / 12 blocks; ctrl >= 95; SPA p <= 0.10; 90 % bootstrap CI of diff above 0 | `pre_registration.json` `go_no_go_rule` |
| Go / no-go items added 12:55 UTC | `null_tape:real_diff>gmm_p95`, `null_tape:real_diff>segment_p95`, `null_tape:session_same_sign>=0.75` (from `tapes.null_tape_check`), and `no_time_proxy_columns` (`harness.TIME_PROXIES` = {`sl`, `n_events_asof`}, abs rho with the session index 0.93 / 1.00); `oos_once.py` refuses an unchecked candidate | `harness.py` lines 581-619; `PROGRESS.md`; `null_tapes_drift/FINDINGS.md` §7 |
| Null tapes | three generators fitted on IS bars only (session bootstrap, 30-bar segment bootstrap, GMM-Markov); certificate = the first 20 (5 min) / 8 (1 min) **healthy** tapes per generator (engine lock-out flagged label-free: 22 of 84 first-build tapes, 32 of 122 built, topped up with new seeds); pass = real diff > GMM p95 AND > segment p95, session tapes carry the sign in >= 75 % | `null_tapes_drift/FINDINGS.md` §1, §2b, §5c, §7 |
| Pre-registrations (`ledger/registrations.jsonl`, 11 lines) | round-0 LLM rules (sha a3c5c063..., 03:51:33 UTC) + correction 05:09:16 ("hashed before any labelled table" was false: tables existed from 02:49, rules hashed 03:29; blindness is a process claim); shortlists minute / 5minute (sha 66f6e004... / 4747257f..., 11:31:33) + corrections 12:07:12 ("frozen before any gate search" was false: 1,600 gate-search rows preceded it; true claim = frozen before the phase-3 gate studies, 0 rows at registration); round-1 tables half A / B (12:36:07) and rules half A / B (17:08:47, 17:10:27; registered before any `llm_round1` ledger row); `oos_opened` 18:06:55 with `candidates: []`, `second_look: false` | `ledger/registrations.jsonl` |
| Refutation | two adversarial refuters (leakage / definitions; arithmetic / controls) per study; material findings repaired and rechecked | `audit/AUDIT.md` |

Two program-level flags the studies raised and that a reader of any control percentile should carry:
(a) the session-matched control is a hindsight-biased comparator for a within-session sequential rule (a rule that keeps a
session's later units beats it by construction: `session_stop/FINDINGS.md` R.3; `regime_gate/FINDINGS.md` §7b); (b) a
control percentile of 99+ is what the engine produces on a memory-free tape for a gate on stop distance or on the CHoCH
count (`null_tapes_drift/FINDINGS.md` §4c), so the tape p95 of the diff, not the control, is the bar for such gates.

---

## 4. Findings, study by study

Every study's verdict is **null** (no candidate); the near-misses are named with the items they fail. Refuter outcomes are
from `audit/AUDIT.md` ("Studies").

### 4.1 H1: the frozen gate is not a loser filter (`h1_gate_audit/FINDINGS.md`)

| variant (IS, L1) | id | kept n (share) | kept / skipped mean | diff | top-1 % off | ctrl | perm p | loser recall / precision (base) | winner recall net | top-decile skipped | blocks | slip8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min frozen | `127543888f5570fe` | 745 (0.167) | -1,026 / -1,006 | -19.71 | -8.44 | 64.7 | 0.855 | 0.835 / 0.847 (0.844) | 0.173 | 0.843 | 6 | -1,416 |
| 1 min take_only | `4325428b222de52f` | 605 (0.136) | -991 / -1,012 | +21.00 | -13.10 | 66.9 | 0.854 | 0.867 / 0.847 | 0.161 | 0.843 | 5 | -1,381 |
| 1 min not_block (post) | `0d1bbb98d600860c` | 2,996 (0.673) | -990 / -1,050 | +59.59 | +87.24 | 99.3 | 0.489 | 0.330 / 0.852 | 0.664 | 0.329 | 6 | -1,380 |
| 5 min frozen | `daaf09471b73ca51` | 325 (0.394) | -979 / -613 | -365.62 | -304.01 | 11.6 | 0.250 | 0.605 / 0.721 (0.723) | 0.369 | 0.565 | 3 | -1,369 |
| 5 min take_only | `ccbf6f37cc8a2977` | 228 (0.276) | -876 / -712 | -164.63 | -110.57 | 18.0 | 0.630 | 0.724 / 0.722 | 0.291 | 0.609 | 4 | -1,266 |
| 5 min skip_only:WATCH:leave_into_recycle | `f963132b4c147368` | 728 (0.881) | -855 / -32 | -822.24 | -1,069.67 | 0.1 | 0.088 | 0.114 / 0.694 | 0.865 | 0.087 | 4 | -1,245 |

Family (10 variants per table): 1 min L1 PBO 0.582, SPA p 0.036 naming `not_block` (the inverse of the gate, kept book
-990, not a candidate); 5 min L1 PBO 0.546, SPA p 0.134. Big winners: 1 min 225 of 268 pts >= 50 winners skipped (1.48M of
1.77M); the late runners are the 15:25-cut trades held 61-375 bars (238 of 268 big winners, 71 % `eod`). 5 min: 95 of 148
skipped (654k of 1.03M); the FZ book is worse than the selection-only book by 41.8k because 97 REENTERs exit at -431 each.
Refuters: minor only. **Verdict: null; the gate's gain is cost avoidance.**

### 4.2 H2 / H3 / H4: regime, volume, levels (`h2_h3_h4/FINDINGS.md` §1)

Pre-registered nested-CV selection (kept floors only) and the declared post-hoc minimum-skip-10 % variant, all 12 tables:

| study | tf | label | selection | id | kept share | diff | ctrl | perm p | blocks | CPCV p5 | PBO | SPA p | go |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H2 | 1 min | L1 | pre-registered | `96a71fa0c77cbd57` | 0.967 | -226.81 | 1.1 | 0.315 | 6 | -417.49 | 0.356 | 0.126 | fail (10 items) |
| H2 | 1 min | L1 | post-hoc min skip | `5229b4f39a9bce95` | 0.853 | +211.08 | 73.7 | 0.051 | 10 | +76.56 | 0.356 | 0.103 | fail: slip8, ctrl, PBO, DSR, SPA |
| H2 | 5 min | L1 | pre-registered (degenerate: skips 2 rows) | `74e1239d4204941d` | 0.998 | +3,991.66 | 94.3 | 0.134 | 2 | +3,444.78 | 0.329 | 0.076 | fail: slip8, blocks, ctrl, PBO, DSR |
| H2 | 5 min | L1 | post-hoc min skip | `12e06107b9d902d0` | 0.887 | +1,030.84 | 83.9 | 0.041 | 11 | +534.55 | 0.329 | 0.0065 | fail: slip8, ctrl, PBO, DSR |
| H3 | 1 min | L1 | pre-registered | `21b31cbb10277775` | 0.868 | -171.85 | 0 | 0.141 | 1 | -298.24 | 0.764 | 0 | fail (9 items) |
| H3 | 5 min | L1 | pre-registered | `8eaee251afffdbb3` | 0.938 | -200.09 | 0.4 | 0.757 | 6 | -598.43 | 0.657 | 0.155 | fail (10 items) |
| H4 | 1 min | L1 | pre-registered | `7e2a1c31f2dc16c3` | 0.844 | -6.92 | 3.1 | 0.954 | 5 | -171.27 | 0.425 | 0.936 | fail (9 items) |
| H4 | 5 min | L1 | pre-registered | `9e32a86bcfc8f5ce` | 0.932 | +613.48 | 83.8 | 0.323 | 7 | -1,774.85 | 0.650 | 0.171 | fail (8 items) |

Grids: 201 H2 cells, 54 H3 cells, 9 H4 cells per table; cells passing every raw check at once: **0 of 264 on every table**
(§1, second table). Family SPA flags with p <= 0.10 (H3 1 min L1 0; H2 5 min L1 0.0065; H3 5 min L1 0) all name cells with a
negative pooled diff and control 100 (a whole-session skip is matched trivially by the session-matched control): not a pass
for any row. Refuters: material (post-hoc variant unrun, H4 verdict window, mid-run snapshot) -> repaired and rechecked
(minor). **Verdict: null on both timeframes.**

### 4.3 session_stop: the "session memory" claim withdrawn (`session_stop/FINDINGS.md` §0, R)

| item | 1 min | 5 min |
|---|---|---|
| as-run null N1 (outcomes permuted over fixed positions) | rejected, Holm p <= 0.014, excess +53 to +106 | not rejected |
| memoryless generator with outcome-tied durations: share of streams N1 rejects | 1.00 (median min Holm p 0.007; excess +84 to +119) | 0.38 |
| hindsight-free N3 / N4 min Holm p | 1.000 / 1.000 -> **not rejected** | 0.0070 (`stops>=3`, 18 units) / 0.4198 -> **inconclusive**, sign positive (the next SETUP does better after stops) |
| 48-cell stop grid, nested OOF (`642553fa41dfcc97`) | diff -52.05, top-1 % off -61.27, CPCV p5 -80.12, PBO 0.825, SPA p 0.597; go/no-go fails with and without the control item | grid not run |
| session-matched control on memoryless streams for the k=2 rule | median percentile 0.0 (hindsight bias, R.3) | median 0.0 |

The N1 rejection was an artefact: winners hold about six times longer than losers, so the SETUP positions are generated by
the outcomes. **Verdict: no session memory shown beyond the hour effect; no `session_stop` key.**

### 4.4 exit_policy: no exit rescues the book (`exit_policy/FINDINGS.md` §3-§11)

| policy (IS, frozen L1 entries, per lot) | 1 min mean / diff vs Foundation | 1 min random-exit pct / blocks / boot 90 % CI | 5 min mean / diff | 5 min random pct / blocks / CI |
|---|---|---|---|---|
| Foundation L1 exit (stop / next CHoCH / 15:25) | -1,009.61 / 0 | 97.0 | -757.05 / 0 | 96.8 |
| C nested-CV pick (1,568-variant `lab.manage` grid; `03637b2591d2f3f4` / `22e810e216567349`) | -923.04 / **+86.57** (t 2.17) | 100.0 / 10 / [25.24, 151.11]; CPCV median 80.19, p5 54.17 | -818.36 / -61.31 | 88.3 / 5 / [-182.92, 53.4] |
| B hindsight imitation (OOF) | -908.80 / +100.80 (t 2.48) | 100.0 / 10 / [32.95, 167.98] | -777.31 / -20.26 | 94.6 / 4 / [-100.38, 59.33] |
| A fitted Q-iteration, pessimistic ensemble (OOF) | -972.05 / +37.56 (t 1.01) | 99.8 / 7 / [-26.69, 99.52] | -902.39 / **-145.34** (hurts) | 62.7 / 4 / [-301.88, -1.01] |
| ST9 R-ladder (IS comparator; tuned on 2026) | -1,010.71 / -1.10 | 97.0 / 8 | -915.93 / -158.88 | 56.4 / 1 |
| hindsight oracle, best close exit | +2,560.00 | | +2,801.47 | |

The 1 min nested pick is Foundation's own stop with no target, no trail and no CHoCH-against cut (44 of 66 CPCV splits): its
+86.57 passes every item but the family SPA (studentised p **0.322** after the repair; 0.396 as coded) and is carried by its
top 1 % of gains (45 trades, mean gain 15,174, +153.38 per trade; the other 4,407 trades net -67.49; §11.2). Applied under the
frozen gate the kept mean moves from -1,026 to -1,008 (1 min) and from -979 to -1,061 (5 min) (§8). PBO of the C family
0.087 / 0.143. Repairs: the family SPA was inflated by a rounding-level duplicate of the benchmark (variant 1177) -> vectors
at 2 dp, 5 min SPA p 0.4965 -> 0.185; the "top 1 % gains removed" item was post-hoc and negative-biased -> the harness's
"top 1 % winners removed" item is the pass item. **Verdict: null; the exit stays the Foundation exit; `exit_rules` would be
a new key type (a user decision).**

### 4.5 ext_features and importance: the vocabulary is empty (`ext_features/FINDINGS.md`; `importance/FINDINGS.md`; `features_shortlist/*/shortlist.json`)

61 extended as-of columns (FFD, BSADF, CUSUM, BOCPD, GMM / HMM / jump states, novelty, window scalars) built on a fit window
2021-10..2023-09 and verified on the truncated tape (max abs diff 0 on both timeframes; no gate, no ledger row).

| importance (IS, L1) | 1 min | 5 min |
|---|---|---|
| features in the model / clusters | 276 / 38 | 238 / 39 |
| clusters passing the pre-registered rule (log-loss MDA mean > std AND top-8 stability) | **0** (0 pass MDA, 5 pass stability) | **0** (0 pass MDA, 2 pass stability) |
| shortlist (sha, registered 11:31:33 UTC) | `66f6e004...`: 0 clusters, 0 allowed columns | `4747257f...`: 0 clusters, 0 allowed columns |
| full bagged model (ceiling; `7359bf6294568ac8` / `1a12e823ea7cf4c7`) | OOF AUC 0.5935, weighted log-loss 0.74474 (constant predictor 0.52502 is better); gate keeps every row; CPCV diff median -18.66, p5 -114.95 | OOF AUC 0.4974, log-loss 0.72748 (constant 0.66239); gate diff +817.94 at kept 0.9915, ctrl 88.4, 1/12 blocks; CPCV median +259.06, p5 -314.33 |
| the statistic caveat (`mda_diag.py`, not the pass rule) | the balanced forest is mis-calibrated under weighted log-loss (mean OOF p 0.526 vs weighted winner share 0.219); an AUC-drop version of the rule would pass **2 of 38** clusters: cluster 0 (`hour_bin=<09:25`, ratio 1.82) and cluster 13 (`card_read=FIRST_PRINT`, 1.09) | AUC-drop rule passes **0 of 39** |
| family (`importance/*`) | 52 rows, PBO 0.031, SPA p 0.724 | 53 rows, PBO 0.027, SPA p 0.0345; SPA-best row = SFI cluster 25 (`jump3_state`, `jump3_run`; `4535288bcf0f1148`): kept 0.868, diff +827, ctrl 100, perm p 0.078, 8/12, slip8 -1,038 -> handed to regime_gate |
| FFD | not adopted (clustered MDA <= 1 std on both) | same |

Repairs: the registration note corrected (§3 above); the "MDA at the fold's tau" statistic was undefined (the gate skipped
nothing in 12/12 and 11/12 folds), not noisy; 42 off-ledger 20-tree dry-run configurations on 5 min disclosed (`--dry` now
shuffles the label). **Verdict: an empty vocabulary; re-opening it under a calibration-free statistic is a user decision
(new registration).**

### 4.6 rocket_ceiling: the pre-registered stop fired (`rocket_ceiling/FINDINGS.md`)

1 min only, L = 60 bars, 2,000 MiniRocket kernels. CPCV 5th-percentile AUC gain of the stacked model over the tabular HGB
**-0.0073** (median -0.0016, max +0.0076) against the stop threshold 0.03: no distillation. Pooled OOF AUC tabular 0.5887,
stacked 0.5892, rocket 0.5884, PCA-16 window probe 0.5474. Best gate in the 12-row family: tabular at skip 0.3
(`7594408d55b3a8c9`) diff +125.03, ctrl 4.9, top-1 % off -60.08, PBO 0.430, SPA p 0.762, go/no-go fail (6 items). Refuters
minor. **Verdict: the window shape adds nothing the as-of features do not carry; no candidate slot by design.**

### 4.7 null_tapes_drift: the certificate and the drift (`null_tapes_drift/FINDINGS.md`)

| reference gate on the real tape (IS, L1) | 1 min diff (ctrl) | 1 min GMM / segment p95 -> real pct | 5 min diff (ctrl) | 5 min GMM / segment p95 -> real pct | passes |
|---|---|---|---|---|---|
| frozen ST7/ST8 (`249b8433a25f5b8a` / `9f4e08a75d0ab931`) | -19.71 (64.0) | 23.00 / 272.51 -> 75th / 37.5th | -365.62 (12.4) | 530.00 / 566.42 -> 5th / 5th | no |
| skip when `n_choch_since_bos >= 2` (`ace645aec2224464` / `c994cebf43aa41d5`) | -72.50 (1.6) | 246.98 / 144.79 -> 0th / 50th | +257.83 (46.6) | 516.38 / 500.14 -> 80th / 80th | no |
| skip when `sl_dist_atr` > IS median (`21f5c361c64d6fe8` / `71caa03d48830f17`) | +12.07 (99.0) | 96.58 / 129.55 -> 37.5th / 62.5th | +33.65 (99.8) | 419.69 / 620.74 -> 55th / 65th | no |

0 of 18 cells pass. The frozen gate reads a median diff of +192 (GMM) / +106 (segment) on memory-free 5 min tapes with
control p50 94.7 / 94.4: that part of any ST7/ST8-shaped statistic is engine mechanics. Engine lock-out (frozen protected
level, no CHoCH for 76-932 sessions) on 22 of 84 first-build tapes was flagged label-free and the certificate topped up to
20 / 8 healthy tapes per generator; 0 of 18 verdicts flipped. Drift IS-early vs IS-late (HGB, purged OOF, without the time
proxies): AUC **0.973** (1 min) / **0.947** (5 min) against a permutation p95 of 0.52; top drivers `atr_bps` (lower late),
`atr14` (higher), `days_to_expiry`, `gap_pts`, `range_3h_pts`: a level and volatility regime, so point-denominated
thresholds are level rules. Program-level gaps it raised were closed 12:55 UTC (§3). **Verdict: a certificate, no candidate.**

### 4.8 gate_family: the ONE learned-gate family (`gate_family/FINDINGS.md`)

Two sub-families under the EMPTY-SHORTLIST RULE: (I) context = `hour_bin` one-hot + `dir` (inside the frozen vocabulary);
(II) H5 on the full as-of table minus the time proxies (274 / 236 features, **outside the frozen shortlist**). Models:
bagging, HGB classifier and regressor, policy trees depth 1-3, scorecard, H5 tree and rule list; nested tau; distillation to
rule lists; robustness labels L0 / L2 / L3; null tapes and drift refit for the finalist.

| finalist (nested OOF row) | id | kept share | diff | top-1 % off | ctrl | blocks | CPCV p5 / median | boot 90 % CI | slip8 | fails | items |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min (I) hgbc -> distilled tree | `d753e432605450f5` | 0.888 | +189.88 | +17.86 | 21.9 | 9 | **+159.75** / 199.36 | [70.2, 306.07] | -1,378 | 6 / 16 | slip8, ctrl, PBO 0.4045, DSR p 1.0, SPA p 0.936, segment-tape p95 |
| 1 min (II) scorecard -> distilled tree | `cbc8df04b485a517` | 0.955 | +70.27 | -115.20 | 11.1 | 2 | -5.92 / 75.34 | [-60.68, 193.72] | -1,396 | 10 / 14 | frozen form skips nothing |
| 5 min (I) pt2 (skip the 11:00 hour) | `2aae111dbdd37a49` | 0.594 | +142.62 | -26.24 | 79.6 | 5 | -433.92 / -45.08 | [-466.35, 796.56] | -1,089 | 11 / 16 | incl. all three null-tape items (GMM p95 598.8, segment 484.3, same sign 0.70) |
| 5 min (II) scorecard -> distilled rules | `d14eb10f08c1c59e` | 1.000 | undefined | | | | +53.58 / 826.61 | | | 9 / 14 | frozen form skips nothing |

**The 1 min context near-miss, in full.** Every probability / value learner of (I) distils to the same one- or two-rule list:
`hour_bin == 11 AND dir == down` (bag4 / hgbr frozen forms `f4cda9399a97d95b` / `890ef76be2db79b5`: kept 0.926, diff
+326.05, ctrl 86.2) plus `hour_bin == 15 AND dir == down` (hgbc -> tree frozen `afd754b8cc67c0d6`, the finalist's frozen form: kept 0.897, diff
+288.86, ctrl 57.9; the hgbc -> rule-list frozen form `f773bc09dbf984b2` has the same kept share and diff, ctrl 56.4). Nested it is +185 to +245 per trade, 9-11 of 12 blocks, every CPCV path positive (p5 +131 to +160), bootstrap CI above
zero. It fails exactly the items that separate a market rule from an artefact of the calendar and the book: ctrl 12-57
(the kept trades are no better than a random same-count pick inside their own sessions: the pooled gain is session
composition), slip8 -1,378, PBO 0.4045, DSR p 1.0, SPA p 0.936 over the 432-row family, and the segment-bootstrap tapes
reproduce a diff of +234 (median) / +562 (p95) for the same rule list on memoryless tapes (real 289 at their 87.5th
percentile; GMM p95 70.14 is passed; session same-sign 0.875 is passed). Family multiplicity: 1 min 432 rows, PBO 0.4045,
SPA p 0.936, effective trials 1.25; 5 min 540 rows, PBO 0.517, SPA p 0.0565 (292 near-degenerate rows excluded from the
studentised family; unstudentised 0.010), effective trials 1.22. The HGB ceiling of (II): OOF gate diff +49 (1 min) /
+387 (5 min), ctrl 2 / 45. Sequential RL not used: the counterfactual is observed for every SETUP and no state carries
between decisions (§6). Refuters minor. **Verdict: null on both timeframes; no candidate file.**

### 4.9 operating_point_sizing: no operating point is positive; sizing not run (`operating_point_sizing/FINDINGS.md`)

Re-parameterises the gate_family finalists' OOF scores (conformal Mondrian by class, ACI, selective risk-coverage, CRC with
sessions as units, cost-aware Pareto front); adds no candidate by design.

| tf | rows | PBO | SPA p | best controlled row by diff | diff | ctrl | kept share | slip8 | fails |
|---|---|---|---|---|---|---|---|---|---|
| 1 min | 174 | 0.547 | 0.925 | CRC h5_full/scorecard alpha 800, lambda 0.05 (`2ae774587330de07`) | +249.89 | 0.0 | 0.043 | -1,160 | 11 |
| 5 min | 144 | 0.640 | 0.066 | conformal h5_full/scorecard alpha 0.1 (`a28e09da4070d513`) | +481.16 | 82.8 | 0.867 | -1,083 | 7 |

Of the 326 kept books evaluated, **0** have a kept mean > 0 at 8 pts slippage and **1** at 3 pts (5 min context/scorecard,
best +99.00). CRC caveat: the session-unit certificate calibrated on the last 200 active IS sessions does not transfer to the
earlier IS rows (realised clipped risk 1.3-4x the certificate on every model; e.g. 1 min context/hgbc certificate 939.65 vs
realised 2,170.28); the conformal guarantee is the CV+ form (about 1 - 2 alpha) and covers winner count, not P&L. **Sizing:
not run: no gate passed; lots = 1 or skip.** Refuters minor.

### 4.10 LLM hypotheses, rounds 0 and 1 (`llm_hypotheses/FINDINGS.md`; `llm_round1/FINDINGS.md`)

Round 0 (verbatim wording the study asks to carry): sixteen skip rules were written from the user's words and the feature
dictionary and hashed (sha256 `a3c5c06382227c95...`) at 03:29 on 2026-09-29. Labelled tables of the program existed from
02:49; the proposer states none was opened, so blindness is a process claim, not a data-ordering fact. Round 0's inputs also
included FZ.md section 19 (ST7/ST8 comparator aggregates over the 2026 lab tape, which coincides with the OOS window; no
Foundation outcome by read or hour), the one deviation from the judges' "user's words + dictionary" rule. Scored on IS (L1):
no rule and no union passes go/no-go; three rules (r0_m6, r0_m8, r0_f8) have no IS support because of a unit error in the
session-range thresholds and are untestable; Holm-adjusted p = 1.0 for all sixteen; on 5 minutes the "sideways" and
"retest" rules skip the better trades.

| round | tf | best rule on the scored rows | diff | ctrl | perm p | family-wise p | eligible | union |
|---|---|---|---|---|---|---|---|---|
| 0 | 1 min | r0_m4 (max-T best, abs t 0.62) | -95.55 | 28.9 | 0.522 | 0.991 | none | skips 2,607 of 4,452: diff +41, ctrl 0.0, 48 % of winners' net and 43 % of top-decile winners thrown away |
| 0 | 5 min | r0_f2 `choch_run >= 3 and n_bos_3h == 0` | -1,212.61 (skipped mean +375 vs kept -838) | 0.0 | 0.0625 | 0.509 | none | diff -322 |
| 1 A->B | 1 min | r1A_m3 (hour 11-12 x NEW/FIRST_PRINT/RECYCLE) | +294.57 | 75.0 | 0.409 | 1.000 (family 200) | none | -25.71 |
| 1 B->A | 1 min | r1B_m1 `hour_bin == <09:25 and fz_read != LEAVE` | **-1,325.28** (wrong sign; skipped mean +339 vs kept -986) | 100.0 | 0.0020 | 0.1449 (Holm over the round 0.096) | none | -162.41 |
| 1 A->B | 5 min | r1A_f4 `n_choch_since_bos == 2` | +1,023.69 | 70.1 | 0.106 | 1.000 (family 138) | none | -609.22 |
| 1 B->A | 5 min | r1B_f5 PENDING x 09-12 | +866.18 | 91.5 | 0.163 | 1.000 (family 134) | none | -22.62 |

Round 1 was cross-fitted (tables of one half shown, rules scored on the other; the family = every labelled cell shown + the
rules); no rule was eligible in either direction, the nested 12-block OOF keeps everything (`188e8939ee98df0e` /
`592d42e2a466698e`). The one rule with a small p (r1B_m1) has the wrong sign: the opening-minutes cell is the worst bin of
one half and the best of the other, the IS-early vs IS-late drift measured in §4.7, not a gate. Round-0 5 min SPA p 0.045 is a
session-composition artefact of r0_f1 (33 active sessions of 408). **Verdict: null in both rounds.**

### 4.11 regime_gate: the machine-found "chop" state (5 min only; `regime_gate/FINDINGS.md`)

| model | nested OOF id | kept share | diff | ctrl | perm p | blocks | CPCV p5 / share > 0 | boot 90 % CI | null tapes (fixed rule) | fails |
|---|---|---|---|---|---|---|---|---|---|---|
| hmm3 | `f04d658f0f2cd264` | 0.580 | -509.09 | 0.9 | 0.100 | 4 | -703.28 / 0.00 | [-1,007, -7] | GMM / segment p95 not cleared | 11 |
| hmm4 | `0af965c7aa190f00` | 0.720 | -910.40 | 6.7 | 0.009 | 3 | -883.41 / 0.00 | [-1,426, -363] | cleared | 9 |
| gmm4 | `760b31266f2a2979` | 0.695 | -108.90 | 11.2 | 0.743 | 7 | -298.33 / 0.18 | [-658, 406] | cleared | 9 |
| **jump4** | `9d7f9977cc402b7a` | 0.611 | **+453.10** | **100.0** | 0.155 | 7 | **-351.99** / 0.55 | [-47.92, 931.56] | GMM 389.70 and segment 431.20 cleared; **session same-sign 0.35** | 7 (slip8 -971, blocks, CPCV p5, PBO 0.319, DSR p 0.965, boot CI, session tapes) |
| jump3 | `16d86a30133971e4` | 0.647 | -731.58 | 0.4 | 0.028 | 2 | -689.87 / 0.00 | [-1,106, -361] | not cleared | 11 |

The jump4 chop state (state 1, the quiet state) is a first-SETUP effect: 0.79 of the 09-bin SETUPs and 0.58 of a session's
first SETUPs are in it against 0.10 of its third; "skip the quiet state" is "skip the session's first, early SETUP", the rule
shape that inflates the session-matched control and the SPA gain (family SPA p 0.0015 carried by that cell) by construction
(§7b). It beats the matched H2 hand rule on the pooled diff (+453 vs +258) and fails 7 items. The importance study's jump3 SFI
row (+827) does not reproduce as a nested gate (-731.58). The HMM / GMM / jump3 "chop" is the CHoCH count with a bar-size
condition (distillation fidelity 0.91 / 0.87 / 0.90). Refuters minor. **Verdict: null.**

### 4.12 online_learner: learn after each trade, with the journal (`online_learner/FINDINGS.md`)

Grid: cadence k {1, 10, 50} x window {anchored, 300, 1000} x reward {net, pf} x learner {LinTS, logistic TS, HGB regressor,
HGB classifier} on the context design, the two linear learners also on the full design (outside the shortlist); explore 0 /
0.3 with 5 seeds; half-Kelly lots 0-3; one row per SETUP in the journal; determinism and truncation asserted.

| tf | paths | pass row-level items | ctrl >= 95 | slip8 > 0 | best walk-forward kept PF row | kept n (share) | kept mean / diff | PF (take-all / frozen) | ctrl | perm p | blocks | slip8 | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | 468 | **0** | 1 | 0 | `19f7ff81224bafa0` context/lints/k1/1000/pf e0.3 s1 | **68** (0.015) | +112.36 / +1,139.37 | 1.077 (0.323 / 0.327) | 0.1 | 0.0035 | 2 | -277.61 | 9 (incl. session same-sign 0.25) |
| 5 min | 468 | **0** | 1 | 0 | `e24ac736ebbfa6d5` context/logts/k10/300/net | 140 (0.170) | -109.36 / +779.87 | 0.942 (0.639 / 0.563) | 85.2 | 0.0665 | 4 | -499.33 | 8 |

Family: PBO 0.307 / 0.533, SPA p 0.408 / 0.761, effective trials 4.41 / 3.58 of 468. The learning curves never reach a
control percentile >= 95 that holds to the end; "beats take-all in cumulative net" is the ~1,050 INR saved per skip, not
selection. Caveat on the path rows: the first 30 closed outcomes are taken by rule (the warm-up policy, §1 "warm-up"), so a
path's keep mask mixes the take-all warm-up with the learned decisions and the learning curves, not the pooled row, are the
honest reading of what was learned. Half-Kelly returned 0 lots on 38 of 68 takes (1 min) and 68 of 140 (5 min): the
calibrated p_win never clears the Kelly break-even at 15.6 % / 27.7 % winners. Refuters minor. **Verdict: null.**

---

## 5. What this means for Strategies 13 / 14

**No strategy file is created.** `strategies/strategy_13.json` / `strategy_14.json` stay reserved and empty; `fz_learn.py`
is not written; the FZ sleeve stays a card (Rule 0(c): no strategy's behaviour changes without the user, and there is
nothing measured to change it toward). ST5-ST8 stay frozen. The S49 entry in `docs/STRATEGY_ANALYSIS_TODO.md` records the
measured numbers of §2 and §4 with `Impact | Unquantified` wherever a trade impact was not measured.

The decisions only the user can take, each with its cost and what it would measure:

| decision | what it is | what it costs | what it would measure | protocol status |
|---|---|---|---|---|
| Re-open the vocabulary under a calibration-free statistic | a new importance registration with an AUC-drop (or isotonic-calibrated) MDA rule in place of the weighted log-loss of a balanced forest | a new sha, the multiplicity of this run carried forward; the phase-3 studies rerun on the new shortlist | whether the 2 clusters the diagnostic passes on 1 min (`hour_bin=<09:25`, `card_read=FIRST_PRINT`) and 0 on 5 min carry a gate; the ceiling AUC 0.59 / 0.50 says how little there is to find | allowed: a new registration, never an edit (`importance/FINDINGS.md` "What would falsify") |
| Accept a rule outside the frozen vocabulary for a second OOS look | freeze the 1 min "skip 11:00-11:59 shorts (+ 15:00 shorts)" list or the 5 min jump4 state as a candidate with provenance `outside the frozen shortlist`, and open OOS again | the OOS window is spent once already (`second_look: false` in `registrations.jsonl`); a second look on the same 2026 window is not an out-of-sample test | the rule's OOS kept-vs-skipped diff, control and perm p against SE ~185 / ~375 | **forbidden by the protocol as run** (one OOS opening, at most three sha-registered candidates, none frozen); it would need a new protocol and a new window |
| Change the cost model (S47) | remove or move the 15:25 cut (the L1 label), or price slippage below 5 pts per side | a different book: L0 is -277 vs L1 -757 on 5 min because the overnight holds are the profitable part; every gate would be re-judged on the new label; kept-vs-skipped differences are slippage-invariant, kept means move by -390 at 8 pts | whether any gate is positive on a book that keeps the overnight trades; the L0 comparator OOS 1 min diff +743 (ctrl 91.0, perm p 0.156, top-1 %-removed -3.77) is the one number already in hand | a user decision on the strategy's `square_off` and `slippage_pts` keys, then a new registration |
| The 11:00-11:59 shorts skip as a card diagnostic | show the rule on the dashboard card beside the frozen ST7/ST8 read, never as a trading rule | nothing in code that trades; a display key | its live kept-vs-skipped reading over time against the IS numbers (+326 frozen, ctrl 86; segment-tape p95 562) | allowed under Rule 0(c) as a diagnostic only |

What the data does not support, stated plainly: a `session_stop` key (no memory shown), an `exit_rules` key (no exit passes),
an HMM / jump state key (no state gate passes; a 40-60-number key in any case), a sizing rule other than lots = 1 or skip,
and any threshold on a point-denominated column (a level rule under the measured drift).

---

## 6. Audit trail

| artefact | where | what |
|---|---|---|
| Audit index | `audit/AUDIT.md` (regenerated by `audit_export.py`) | every agent of every workflow with its full transcript (`audit/workflows/<wf>/agent-<id>.jsonl`) and structured verdict (`.../results/<label>.json`); per study the chain study -> verify (leakage, arithmetic) -> repair -> recheck with `refuted` / `severity` |
| Workflows | `workflows/phase1.js` (wf_55c65499-a4f), `phase1b.js` (wf_9d4b7078-af8), `phase2.js` (wf_b5100757-3f4), `phase3.js` (wf_e200b95a-fcc), `exit_policy_followup.js` (wf_82d49a78-1f8), `closeout.js`; journals under `audit/workflows/<name>/journal.jsonl` | the orchestration scripts and their resume journals |
| Ledger | `ledger/trials.jsonl` (append-only; 4,226 lines at 18:12 UTC), `ledger/vectors/` (per-session vectors per row) | every configuration ever scored |
| Registrations | `ledger/registrations.jsonl` (11 lines), `ledger/registered/` (byte-identical copies of the hashed rule files) | pre-registrations, their two classes of correction (§3), the OOS opening |
| Study folders | `studies/<name>/FINDINGS.md`, `findings.json`, scripts, logs, `run.nohup` | the per-study record; refuter-confirmed repairs are sections of each FINDINGS |
| Build and quality | `build/`, `data/<tf>/`, `QUALITY.md` | rebuild from `fz_v3/data/`, cross-check against the local build (identical on every engine / FZ table), causality diff PASS at the 2025-06-30 12:00 cut |
| Memory of the run | `PROGRESS.md`, `STUDY_AGENT_BRIEF.md` | resume notes, standing facts, the instructions phase-3 agents received |

**Material refuter findings and repairs** (`audit/AUDIT.md` "Studies"): llm_round0 (arithmetic: false blindness note, unit
error, unrun rules), h2_h3_h4 (leakage and arithmetic: unrun post-hoc variant, H4 verdict window, mid-run snapshot),
session_stop (mis-specified null N1), exit_policy (family SPA inflated by a benchmark duplicate; post-hoc pass item),
null_tapes_drift (engine lock-out undisclosed; time-proxy refusal not in code), importance (false registration note; undefined
statistic; off-ledger dry runs; a precision contradiction). Each was repaired in the study folder and rechecked (minor left);
no ledger row was edited or removed.

**The two interruptions** (`PROGRESS.md`): (1) the model's usage limit at about 12:00 IST failed every running agent
(phase 1 repair / recheck of session_stop, phase 1b null_tapes_drift, phase 2 importance and rocket_ceiling); the studies'
own `nohup` processes finished by 07:15 UTC; the run paused to 16:30 IST and resumed the same workflows with
`resumeFromRunId`; (2) the session limit at about 14:05-15:20 UTC cut phase 3 (gate_family, llm_round1, online_learner, the
regime_gate refuters); relaunched 15:30 UTC (wf_e200b95a-fcc) with an hourly resume routine as the safety net.

**The git incident** (`PROGRESS.md`): the re-signing rebase stopped before its last pick, HEAD sat detached at 06:24 with the
branch on the unsigned tip, and the checkout replaced every tracked file's inode, so running processes wrote their logs to
unlinked inodes. Fixed at 12:00 IST: `git rebase --quit`, branch re-pointed, the one ledger row (2919f2bb65d22f11) and vector
from the unpicked commit restored (append-only union), a mirror loop copied every orphaned log back from `/proc/<pid>/fd`.
Two log tails were still lost at process exit (the rocket run's final three lines; the 1 min FQI's summary line); their
values are in `results.json` / `a_result_minute.json` and the ledger shas reproduce (`rocket_ceiling/FINDINGS.md` §8a;
`exit_policy/FINDINGS.md` §11.6). GitHub: pushes to kiran6154/money-maker were refused (Claude GitHub App not installed);
after the user installed the app on their own account, both branches were pushed to vijayhegdebk/moneymaker-ui and the draft
PR opened (https://github.com/vijayhegdebk/moneymaker-ui/pull/1); `origin` is reset to kiran6154 on reconnect and must be
re-pointed before each push.

**Harness changes made during the run and why** (`PROGRESS.md`; `harness.py`):

| change | when / trigger | effect on results |
|---|---|---|
| `harness.spa`: candidates active in fewer than max(10, 5 % T) sessions leave the studentised family; White's unstudentised statistic reported beside Hansen's | after the exit_policy refuters found a near-benchmark variant inflating the family p | exit_policy 1 min SPA p 0.396 -> 0.322, 5 min 0.4965 -> 0.185 (with 2-dp vectors); no gate candidate changed (rocket recheck reproduces) |
| `SPA_ACTIVE_TOL_INR = 0.01`: activity = abs gain > 0.01 INR, not > 1e-9 | after exit_policy repair §11.1 showed the 1e-9 rule was a no-op against a duplicate differing only in rounding | reproduces the repaired numbers from the stored vectors; nothing changes for gate candidates |
| `harness.go_no_go(..., null_tape=, columns=)`: three null-tape items and `no_time_proxy_columns` required; `harness.TIME_PROXIES` = {`sl`, `n_events_asof`}; `oos_once.py` refuses unchecked candidates | 12:55 UTC, Judge 1's binding fix from the null_tapes_drift refuters | every phase-3 finalist carries the tape items in its go/no-go table (§4.8, §4.11, §4.12) |

Study-level guards added in the same spirit: `tapes.rule_mask` refuses time proxies and label columns (PermissionError);
`run_importance.py --dry` shuffles the label so no real kept-vs-skipped number can be produced off-ledger.

---

## 7. Files

| path | content |
|---|---|
| `REPORT.md` | this document |
| `PROGRESS.md`, `QUALITY.md`, `README.md`, `STUDY_AGENT_BRIEF.md` | run memory, build quality log, folder map and rules, phase-3 agent instructions |
| `harness.py`, `pre_register.py`, `oos_once.py`, `audit_export.py` | the evaluator, the pre-registration run, the single OOS opening, the audit exporter |
| `results/pre_registration.json` | splits, raw books, frozen comparator on both labels, break tests, the go/no-go rule |
| `results/oos.json` | the one OOS run (comparators only; `candidates: []`) |
| `ledger/trials.jsonl`, `ledger/vectors/`, `ledger/registrations.jsonl`, `ledger/registered/` | trials, vectors, registrations and corrections, hashed rule files |
| `features_shortlist/minute/shortlist.json`, `features_shortlist/5minute/shortlist.json` | the empty frozen vocabularies (sha 66f6e004... / 4747257f...) |
| `features_ext/<tf>/` | the 61 extended as-of columns and their truncation check |
| `studies/ext_features/`, `h1_gate_audit/`, `h2_h3_h4/`, `session_stop/`, `llm_hypotheses/`, `exit_policy/`, `null_tapes_drift/`, `importance/`, `rocket_ceiling/`, `gate_family/`, `operating_point_sizing/`, `llm_round1/`, `regime_gate/`, `online_learner/` | one folder per study: `FINDINGS.md`, `findings.json`, scripts, outputs, logs |
| `build/`, `data/<tf>/` | the dataset build, cross-check and causality diff; the tables the studies read |
| `audit/AUDIT.md`, `audit/workflows/`, `audit/other_agents/` | the audit index, every agent transcript and verdict |
| `workflows/*.js` | the orchestration scripts |
| `../BRIEF.md`, `../DESIGN_PANEL.md` | the user's words and protocol; the design panel's program |
| `docs/STRATEGY_ANALYSIS_TODO.md` S49 (repo root) | the Rule 0 entry for this program (S47 = cost model, S50 = the ST9-12 exit grid on 2026) |

Not created: `candidates/`, `strategies/strategy_13.json`, `strategies/strategy_14.json`, `fz_learn.py`.
