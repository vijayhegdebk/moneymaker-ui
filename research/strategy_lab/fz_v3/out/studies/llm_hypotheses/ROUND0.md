# LLM hypotheses, round 0 (blind)

Written 2026-09-29T03:29:35+00:00 by the blind hypothesis proposer of the FZ v3 program (DESIGN_PANEL section
`deep-sequence-llm-hypotheses`, round 0). Machine-readable twin: `rules_round0.json`,
sha256 `a3c5c06382227c9504e08e40682244756bb58261419be6d53fbba95ada3a1182` (also in `rules_round0.sha256`).

## Inputs read (and nothing else)

1. `fz_v3/BRIEF.md`: the user's words in the first paragraph and the H1-H5 text.
2. `fz_v3/out/data/README.md`: the feature dictionary (column names, definitions, look-ahead status).
3. `FZ.md` sections 7, 8, 9 and 19: what the card reads (FIRST_PRINT / ACCEPTED / THIN / RECYCLE / PENDING / LEAVE / HUNT / REJECT / NEW),
   the gate branches and the watch machine mean, and what a room is.

No parquet, CSV, JSON, ledger, result, FINDINGS or study file was opened; no Python ran over the data; the DESIGN_PANEL
judges' numbers were not read. Every column below is listed as **as-of** in the dictionary (bars `<= k`, engine / FZ state
at the SETUP bar's close); no `fnd_`, `l1_`, `fwd_`, `fzpos_`, `fzpost_` or `fz_traded` column and no final-state column is used.

## Grammar

Each rule is a conjunction of at most 3 comparisons `[column, op, value]` (`>=`, `>`, `<=`, `<`, `==`, `in`) on named as-of
columns of `features.parquet`; `then` is always `skip`. Columns ending `_atr` are in units of `atr14` at the SETUP bar.
"1h" = 60 bars on minute, 12 bars on 5minute; "3h" = 180 / 36 bars (README convention). The two timeframes carry the same
eight ideas with time-adjusted thresholds because the user said the behaviour is "different for different time".

## The user's four observations, mapped to columns

| user's words | columns that carry the idea |
|---|---|
| "if CHoCH and CHoCH and no breaks then it's sideways; trades in sideways are hurting" | `n_choch_since_bos`, `n_choch_since_bos_today`, `choch_run`, `n_bos_1h` / `n_bos_3h`, `n_bos_today`, `alt_dir6`, `range_since_choch_atr`, `range_3h_atr`, `sess_range_atr`, `er_1h` |
| "check how price reacts in visibly high volume ... if it breaks there will be a large move, else price retests, retests and respects" | `hv3_dir_agree`, `hv3_bars_since` (the last bar with `vol_ratio20 >= 3`), `touch_swing_last`, `swing_ahead_dist_atr`, `fz_read`, `room_ahead_dist_atr` |
| "it's different for different time" | `hour`, `session_bar`, and 1m vs 5m thresholds |
| "avoid only loss trades and not profitable ones" | every rule is a conjunction (narrow), aimed at the SETUPs that have no room to run, not at a direction or a whole hour |

## minute (Strategy 1 Foundation, 1 min) - 8 rules

| id | if (all hold) | reading | reason (user's words) | expected effect |
|---|---|---|---|---|
| r0_m1 | `n_choch_since_bos >= 2` and `range_since_choch_atr <= 2.0` | Two or more CHoCHs since the last BOS and price has covered at most 2 ATR since the SETUP's own CHoCH: the market flips without breaking. | "if CHoCH and CHoCH and no breaks then it's sideways; trades in sideways are hurting" | skipped SETUPs have lower mean Foundation net than kept; mostly stop_loss / small next_choch exits; few winners of size lost |
| r0_m2 | `choch_run >= 3` and `n_bos_1h == 0` | The last three engine events are all CHoCHs and no BOS in the last 60 bars: flip-flop with no follow-through. | "CHoCH and CHoCH and no breaks" | skipped set concentrated in losers (fast reversals); kept-vs-skipped expectancy difference positive |
| r0_m3 | `alt_dir6 >= 4` and `er_1h <= 0.3` | Direction changed at least four times in the last six events and the last hour's efficiency ratio is 0.3 or less: chop. | "trades in sideways are hurting" | skipped SETUPs net negative on average; winners skipped are small |
| r0_m4 | `fz_read in [RECYCLE, THIN]` and `room_ahead_dist_atr > 0` and `room_ahead_dist_atr <= 1.0` | The card reads a revisit without conviction and the nearest room edge ahead is within 1 ATR: a bet on breaking a respected edge from inside. | "else price retests, retests and respects" | skipped trades die inside the room before the edge breaks; large winners rarely start from a THIN / RECYCLE read at the edge |
| r0_m5 | `hv3_dir_agree == False` and `hv3_bars_since <= 60` | Within the last 60 bars a bar printed >= 3x the prior median volume in the opposite direction: the SETUP fades the visibly high-volume move. | "check how price reacts in visibly high volume ... if it breaks there will be a large move" | skipped (fading) SETUPs lose more often than kept; kept SETUPs in agreement keep the large moves |
| r0_m6 | `touch_swing_last == held` and `swing_ahead_dist_atr > 0` and `swing_ahead_dist_atr <= 1.0` | The last touch of a swing level in the past hour held, and the swing ahead in the SETUP's direction is within 1 ATR. | "Those levels will be respected ... retests, retests and respects" | skipped SETUPs run into the held level and reverse; a level that just held rarely gives way on the next approach, so few winners lost |
| r0_m7 | `hour in [12, 13]` and `n_choch_since_bos_today >= 2` | Midday bar and this session already has two or more CHoCHs since its last BOS: midday chop. | "it's different for different time" + the sideways observation | midday sideways SETUPs are net negative; kept midday SETUPs after a BOS keep continuations |
| r0_m8 | `session_bar >= 60` and `n_bos_today == 0` and `sess_range_atr <= 2.5` | An hour in, no BOS today and the session range so far is at most 2.5 ATR: a range day with no break. | "if ... no breaks then it's sideways" | skipped SETUPs come from narrow break-less sessions and average a loss; days that have broken keep the runners |

## 5minute (Strategy 2 Foundation, 5 min) - 8 rules

| id | if (all hold) | reading | reason (user's words) | expected effect |
|---|---|---|---|---|
| r0_f1 | `n_choch_since_bos >= 2` and `range_3h_atr <= 4.0` | Two or more CHoCHs since the last BOS and the last 3 hours (36 bars) span at most 4 ATR: sideways. On 5 min two CHoCHs span hours, so the 3h range is the width of the box. | "if CHoCH and CHoCH and no breaks then it's sideways" | skipped SETUPs have lower mean net than kept; mostly next_choch / stop_loss exits inside the box |
| r0_f2 | `choch_run >= 3` and `n_bos_3h == 0` | Three CHoCHs in a row and no BOS in the last 36 bars. | "CHoCH and CHoCH and no breaks" | skipped set concentrated in losers; kept-vs-skipped expectancy positive |
| r0_f3 | `alt_dir6 >= 4` and `er_1h <= 0.35` | Alternating event directions and an inefficient last hour (12 bars). | "trades in sideways are hurting" | skipped SETUPs net negative on average; small winners lost only |
| r0_f4 | `fz_read in [RECYCLE, THIN]` and `room_ahead_dist_atr > 0` and `room_ahead_dist_atr <= 1.0` | A revisit without acceptance, aimed at a room edge less than 1 ATR away. | "price retests, retests and respects" | skipped trades die inside the room; large winners rarely start from a THIN / RECYCLE read at the edge |
| r0_f5 | `hv3_dir_agree == False` and `hv3_bars_since <= 12` | Within the last 12 bars a >= 3x-volume bar printed in the opposite direction: the SETUP fades it. | "check how price reacts in visibly high volume ... if it breaks there will be a large move" | skipped (fading) SETUPs lose more often; kept SETUPs in agreement keep the large moves |
| r0_f6 | `touch_swing_last == held` and `swing_ahead_dist_atr > 0` and `swing_ahead_dist_atr <= 1.0` | The last swing touch in the past hour held and the swing ahead is within 1 ATR. | "Those levels will be respected ... retests, retests and respects" | skipped SETUPs run into the held level and reverse; few winners lost |
| r0_f7 | `hour in [12, 13]` and `n_choch_since_bos_today >= 2` | Midday and this session already has two or more CHoCHs since its last BOS. | "it's different for different time" | midday sideways SETUPs net negative; kept midday SETUPs after a BOS keep continuations |
| r0_f8 | `session_bar >= 12` and `n_bos_today == 0` and `sess_range_atr <= 3.0` | One hour in, no BOS today and the session range so far is at most 3 ATR. | "if ... no breaks then it's sideways" | skipped SETUPs come from narrow break-less sessions and average a loss; days that broke keep the runners |

## How each rule should be judged (per the BRIEF protocol)

On IS only: net of kept vs net of skipped, share of winners skipped (recall of losers vs precision), the session-matched
random control percentile and the kept-vs-refused permutation p; every rule individually and the union. A rule whose skipped
set is not worse than its kept set, or which removes a material share of the big winners, is dropped before OOS is touched.
Thresholds (2.0 / 4.0 ATR, 0.3 / 0.35 efficiency, 60 / 12 bars, 1.0 ATR) are round guesses in the user's units, not fitted.

## What I deliberately did not use

I did not use any labelled statistic: no Foundation outcome, no `fnd_` / `l1_` / `fwd_` / `fzpos_` / `fzpost_` column, no
`fz_traded`, no ledger or result file, no DESIGN_PANEL number. FZ.md section 19 prints acceptance-window counts and priced
nets for ST7 / ST8 (TAKE / WATCH / BLOCK / REENTER counts, control percentiles); I read them only because they sit in the
permitted section and none of them shaped a rule: the rules use the card vocabulary (reads, rooms, edges, hunts) and the
event / volume / level columns, not the frozen gate's decisions (`fz_gate`, `fz_block_reason`, `fz_branch`, `fz_take_why`
are left out on purpose so round 0 is independent of ST7 / ST8, and because the gate's `hunt_fade` block already expresses
the "hunt then fade" reading). I also left out the today's-ledger columns (`today_net_asof` etc.), the gap, the day of week,
days to expiry and every raw price or id, because the user's observations say nothing about them and a blind rule on them
would be a fishing rule rather than a hypothesis. No SETUP direction rule (up vs down) was written for the same reason.

## Errata (repair round, 2026-09-29 05:09, appended after the adversarial refuters; `rules_round0.json` is unchanged and still hashes to `a3c5c063...a1182`)

1. **Registration wording.** The ledger registration of 03:51:33 said the rules were "hashed before any labelled table of the program
   existed". That is false by the artefacts' timestamps: `data/5minute/features.parquet` (with `fnd_*` / `l1_*` labels) was built at
   02:49:45, `data/minute/features.parquet` at 02:55:51, `results/pre_registration.json` (raw book and frozen ST7/ST8 statistics) at
   03:02:14, and this file's twin was written at 03:29:35. The proposer states none of those files was opened; blindness is a process
   claim (self-report plus an empty `llm` ledger before registration), not a data-ordering fact. A correcting line was appended to
   `ledger/registrations.jsonl` (`kind: correction`); nothing was edited.
2. **Inputs.** The judges' fix for round 0 was "the user's words and the README feature dictionary only". Sections 7-9 of `FZ.md` are the
   card vocabulary the dictionary points to; section 19 was also read and prints ST7/ST8 priced nets, control percentiles and permutation
   p over the 2026 lab tape, which coincides with the OOS window (no Foundation outcome by read or hour). This is the one deviation.
3. **Unit error.** `sess_range_atr` is in ATR14 units, and ATR14 on 1-minute bars has an IS median of 8.86 pts (5-minute: 22.6 pts), so a
   session range "<= 2.5 ATR an hour in" (r0_m8) or "<= 3.0 ATR" (r0_f8) is far below anything observed (1-minute IS median 15.1 ATR,
   minimum 1.34 at the session open; the single row with an hour elapsed and no BOS sits at 9.22 ATR). The claim in "How each rule should
   be judged" that the thresholds are "round guesses in the user's units" is wrong for these two rules.
4. **Support.** On IS, r0_m8 fires on 0 of 4,502 SETUPs, r0_m6 on 1 (`touch_swing_last == held` holds on 5 IS rows on 1 minute),
   r0_f8 on 1 of 832; they are untestable and are reported as such in `FINDINGS.md`, kept in the family for max-T / Holm / PBO. Two
   comparisons are no-ops given their companions (`room_ahead_dist_atr > 0` in r0_m4 / r0_f4; `swing_ahead_dist_atr <= 1.0` in r0_m6 /
   r0_f6). None of the sixteen rules is re-thresholded: a corrected proposal would be a new round with its own sha and the multiplicity
   carried forward. Scoring and the machine-readable results: `score_round0.py`, `round0_results.json`, `FINDINGS.md`, `findings.json`.
