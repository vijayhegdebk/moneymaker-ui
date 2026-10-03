# llm_round1: study notes (step 1, written 2026-09-29 by the tables agent)

Study folder of the round-1 LLM hypotheses (DESIGN_PANEL `deep-sequence-llm-hypotheses`; Judge 1: cross-fitted halves, the cells shown
logged as the family size; Judge 2: the trials count = cells shown, the harness splitter, a proposer agent distinct from any study author).
Round 0 (blind) lives in `studies/llm_hypotheses/` (null result, 16 rules, sha `a3c5c063...`).

## What step 1 produced

| file | what |
|---|---|
| `r1_common.py` | the definitions shared by the tables and the scorer (halves, vocabulary and swap rule, bins, cell, family size, rule grammar, protocol check); fixed before any labelled number of this study was looked at |
| `tables.py` -> `tables_<tf>_<half>.md` / `.json`, `tables_summary.json`, `tables.log` | the labelled summary tables a round-1 proposer may see: half A = harness blocks 0-5 (2021-10-01 .. 2023-11-06), half B = blocks 6-11 (2023-11-07 .. 2025-12-31); label L1; IS only; no raw rows (cells with < 5 units show the count only) |
| `scorer.py` | step 3: registration of a rules file (sha256, append-only), scoring of every rule on the OTHER half through `harness.score` on a sub-table of that half (family `llm_round1/<half seen>`), L0 robustness, the union, the round-0 rules on the same rows, drift refits, the max-T over the family (labelled cells rebuilt on the scored half + the rules), Holm over the rules of the round, the greedy combination (ledger rows), the cross-fitted verdict (fixed crossed list, shipped list, nested 12-block OOF, nested CPCV via `score_paths`), PBO / SPA / DSR / bootstrap, `harness.go_no_go` with the CPCV, declared-columns and null-tape items, `FINDINGS_draft.md`, `candidate_<tf>.json` only on a pass |

## Shortlist state and the EMPTY-SHORTLIST RULE

`features_shortlist/<tf>/shortlist.json` (registered 2026-09-29T11:31:33; no newer shortlist line in `ledger/registrations.jsonl`, lines 5-6
are sha-unchanged corrections of the registration note) has `n_shortlisted = 0` and `allowed_columns = []` on both timeframes. The tables
therefore cover `hour_bin`, `fz_read`, `dir` (always) plus an exploratory vocabulary labelled **"outside the frozen shortlist"** in every
file header and vocabulary row: the representative of each of the top-8 clusters by log-loss MDA rank of `studies/importance/
importance_clusters_<tf>.csv` (shown through the swap rule of `r1_common.py` when the representative is a one-hot of an always-included
column, an exact duplicate of one (`card_read` == `fz_read` on every IS row), a calendar-time proxy (`n_events_asof`, `sl`) or a column
already shown) and the columns of the design's four two-way tables. Every labelled cell counts toward the family size exactly as a
shortlisted cell would. Anything found here can be frozen as a candidate only with the provenance
`{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` for the user to accept or reject.

Swaps made (all stated in the file headers): minute cluster 7 / 11 / 13 (`card_read=PENDING` / `=ACCEPTED` / `=FIRST_PRINT`, duplicates of
`fz_read`) -> `room_ahead_dist_atr`, `touch_room_bars_ago`, `card_first_bars`; cluster 15 (`n_events_asof`, time proxy; `sl` too) ->
`ffd_close_dstar` (an extended column; FFD not adopted; a level proxy: caveat printed); cluster 33 (`hour_bin=>=15:20`) covered by the
`hour_bin` table, zero own cells. 5minute cluster 12 (`card_read=LEAVE`) -> `card_leave_kind`; cluster 21 (`n_events_asof`) ->
`ffd_close_dstar`; cluster 8 (`gap_pts__na`) -> `gap_pts` as an NA indicator; cluster 38 (`touch_prot_last=broke`) covered by the
`touch_prot_last` table (cluster 16).

## Cell counts (the family size for the max-T; also in `tables_summary.json` and the registration lines)

| file | rows | sessions | columns shown | two-way tables | labelled cells | suppressed (< 5 units) | empty |
|---|---|---|---|---|---|---|---|
| `tables_minute_A` | 2,408 | 324 | 14 | 4 | **184** | 21 | 39 |
| `tables_minute_B` | 2,044 | 254 | 14 | 4 | **181** | 23 | 39 |
| `tables_5minute_A` | 428 | 214 | 14 | 4 | **122** | 42 | 69 |
| `tables_5minute_B` | 398 | 194 | 14 | 4 | **118** | 46 | 68 |

Half A shows 306 labelled cells in all, half B 299. The scorer's family per timeframe and direction = the labelled cells of the seen
tables + the round-1 rules of that half + the 8 round-0 rules of the timeframe.

## Registration

`ledger/registrations.jsonl` lines 7-8 (`kind: pre_registration`, `what: LLM hypotheses round 1 labelled tables half A|B`): the four
files' sha256 and cell counts, written before any round-1 rule existed (0 ledger rows of family `llm_round1` at that moment). The
scorer appends a registration line per rules file before it scores it and refuses a file whose sha does not match.

## Code smoke test (not a finding; nothing reached the program's ledger)

`scorer.py smoke` (and `smoke --relax`, which switches the eligibility thresholds off so that the selection / crossfit / CPCV / null-tape
code path runs) was executed three times on 2026-09-29 12:45-13:00 UTC (logs kept, labelled, in `smoke_logs/`) on **synthetic rules** with the harness ledger and the registrations
file **redirected to the session scratchpad** (`H.LEDGER`, `r1_common.REGISTRATIONS`), controls and max-T at 100 draws. Its purpose was
to exercise every code path end to end (refusal of a time-proxy rule, the off-edge threshold flag, the sub-table scoring, the max-T
family, PBO / SPA, the nested OOF and CPCV, `score_paths`, `go_no_go` with the null-tape item). No number from it is retained or
reported; `OUT/ledger/trials.jsonl` still has 0 rows of family `llm_round1` and `registrations.jsonl` carries no smoke line (verified:
1,762 ledger rows before and after). The third run (relaxed) exercised the selection path end to end: a fixed crossed list, the shipped list, the nested 12-block OOF and the nested CPCV (128 of 132 test blocks with a selection on minute), the null-tape certificate on the tapes and `go_no_go` with the columns and null-tape items. The first smoke run showed that the Welch t of round 0 is unusable as the max-T statistic once
5-20-unit cells enter the family (the permutation null of max |t| reached p95 ~ 10.6): the statistic was changed to the pooled-sd
standardised mean difference (`scorer.pooled_z`) BEFORE any round-1 rule existed; the Welch t is still reported per rule for the record.

## What the step-3 agent must do (in this order)

1. Wait for `rules_round1_A.json` and `rules_round1_B.json` (the two proposers; each reads only its half's tables).
2. `python scorer.py score --rules rules_round1_A.json` then `... rules_round1_B.json` (each registers its file first), then
   `python scorer.py combine` (or `python scorer.py all --rules rules_round1_A.json rules_round1_B.json`). The combine stage runs the
   nested CPCV with `joblib` on 4 cores; expect 20-60 minutes: start it with `nohup ... > combine.nohup 2>&1 &` and poll `scorer.log`.
3. Finish `FINDINGS_draft.md` into `FINDINGS.md` and write `findings.json` (`{study, timeframes, candidates, null_result,
   ledger_families, caveats, files}`); cite the round-0 ledger ids from `studies/llm_hypotheses/FINDINGS.md` for the round-0 rules on
   the full IS table (the scorer re-scores them on each half under `llm_round1/<half>/round0` because the half rows differ).
4. Only when `go_no_go` passes for a timeframe: copy `candidate_<tf>.json` to `OUT/candidates/llm_round1_<tf>.json` with a registration
   line; the candidate carries `"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"` and
   `user_decision_required: true`. Otherwise the null result is the deliverable.
