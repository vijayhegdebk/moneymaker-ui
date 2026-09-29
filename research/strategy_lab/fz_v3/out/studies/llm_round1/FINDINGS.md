# llm_round1: the round-1 (table-informed, cross-fitted) LLM hypotheses scored on the other half (IS only)

Study folder `fz_v3/out/studies/llm_round1/` (DESIGN_PANEL `deep-sequence-llm-hypotheses`; Judge 1: tables of one half, rules scored on the other, the cells shown logged as the family size; Judge 2: the harness splitter, trials = cells shown + rules proposed, a proposer agent distinct from any study author). Step 1 (`r1_common.py`, `tables.py`, `scorer.py`, `NOTES.md`) by the tables agent; step 2 the two proposer agents (`rules_round1_A.json`, `rules_round1_B.json`); step 3 `scorer.py all` (log `scorer.log`, `run_all.nohup`; outputs `scores_A.json`, `scores_B.json`, `results_round1.json`, `scores_<tf>.csv`, `FINDINGS_draft.md`) and this file / `findings.json` (`write_findings.py`). **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 book), L0 robustness only. Round 0 (blind) is `studies/llm_hypotheses/`.

Every column of every rule and cell below is **outside the frozen shortlist (importance rule failed for every cluster)**: `features_shortlist/<tf>/shortlist.json` has `n_shortlisted = 0`, `allowed_columns = []` on both timeframes.

## 0. Result in one paragraph

**Null result.** Both round-1 rule files were registered (sha256 + byte-identical copy under `ledger/registered/`) before any ledger row of family `llm_round1` existed, and every rule was scored on the half whose tables its proposer never saw (A -> B, B -> A), through `harness.score` on a sub-table of that half.

**minute**: direction A -> B: 8 rules (0 refused, 0 untestable, 0 flagged), 6 with diff > 0, best max-T family-wise p 1.0000 (`r1A_m3`: diff 294.57, control pct 75.0, perm p 0.4088, Holm p over the round 1.0000, ledger `04c389cc8c5f4f69`), highest control percentile 78.0, eligible none, L_A = []; direction B -> A: 8 rules (0 refused, 0 untestable, 0 flagged), 4 with diff > 0, best max-T family-wise p 0.1449 (`r1B_m1`: diff -1,325.28, control pct 100.0, perm p 0.0020, Holm p over the round 0.0960, ledger `a6e37c1d1033559b`), highest control percentile 100.0, eligible none, L_B = []. Cross-fit: no rule was eligible in either direction, so the fixed crossed list is empty (no ledger row: keep everything); nested 12-block OOF `188e8939ee98df0e`: kept 4452 / skipped 0, diff n/a, control pct n/a; nested CPCV (66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): 0 of 132 test blocks had a non-empty selection, diff median n/a, p5 n/a, share > 0 0.000. `harness.go_no_go` on the oof12 row: **fail** (10 of 13 items fail: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated).

**5minute**: direction A -> B: 8 rules (0 refused, 0 untestable, 0 flagged), 4 with diff > 0, best max-T family-wise p 1.0000 (`r1A_f4`: diff 1,023.69, control pct 70.1, perm p 0.1064, Holm p over the round 1.0000, ledger `b17b23f2469ad58b`), highest control percentile 88.2, eligible none, L_A = []; direction B -> A: 8 rules (0 refused, 0 untestable, 0 flagged), 4 with diff > 0, best max-T family-wise p 0.9905 (`r1B_f7`: diff -905.82, control pct 83.8, perm p 0.0620, Holm p over the round 1.0000, ledger `de41f9ab8006384b`), highest control percentile 93.1, eligible none, L_B = []. Cross-fit: no rule was eligible in either direction, so the fixed crossed list is empty (no ledger row: keep everything); nested 12-block OOF `592d42e2a466698e`: kept 826 / skipped 0, diff n/a, control pct n/a; nested CPCV (66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): 0 of 132 test blocks had a non-empty selection, diff median n/a, p5 n/a, share > 0 0.000. `harness.go_no_go` on the oof12 row: **fail** (10 of 13 items fail: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated).

What this settles: a table-informed proposer, shown the cell means of one half, does not write a skip rule that survives on the other half under the family of every cell it saw; the round-0 (blind) result of `studies/llm_hypotheses/` stands, and the frozen ST7/ST8 gate remains the only gate in `candidates/` consideration for this study (none from here).

## 1. Shortlist state and the EMPTY-SHORTLIST RULE

Every column of every rule and cell below is **outside the frozen shortlist (importance rule failed for every cluster)**: `features_shortlist/<tf>/shortlist.json` has `n_shortlisted = 0`, `allowed_columns = []` on both timeframes.

| tf | shortlist sha256 | frozen at | clusters | MDA pass | stability pass | n_shortlisted | allowed_columns | newer shortlist line in `registrations.jsonl` |
|---|---|---|---|---|---|---|---|---|
| minute | `66f6e004bd93e47c55ca219785a9a30f36d618cbbbd215cfcbad5a44412b5bdb` | 2026-09-29T11:31:33 | 38 | 0 | 5 | 0 | [] | no |
| 5minute | `4747257f41ecb40f1b3c27ea35cc50868d7c6b91f84f61ab7666911aef019dc9` | 2026-09-29T11:31:33 | 39 | 0 | 2 | 0 | [] | no |

The tables shown to the proposers (`tables_<tf>_<half>.md`) therefore carried `hour_bin`, `fz_read`, `dir` plus the representatives of the top-8 log-loss-MDA clusters (swaps stated in the file headers and in `NOTES.md`: duplicates of `fz_read`, the calendar-time proxies `n_events_asof` / `sl`, and already-shown columns were replaced by the highest-MDI admissible member) and the columns of the four two-way tables. The five interaction pairs of each shortlist were listed with their split points; the proposers used none (both files say why: no two-way cell of those pairs was shown, and three pairs contain a time proxy and were refused). Every labelled cell counts toward the max-T family exactly as a shortlisted cell would.

A rule found here can be frozen as a candidate only with the provenance `{"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"}` and `user_decision_required: true`. The ledger rows of families `llm_round1/*` do not carry that string in their `config` (the ledger is append-only and the scorer's config schema was fixed at step 1); the label is carried by the two registration lines of the rules files (`note`: 'EMPTY-SHORTLIST RULE: every rule is exploratory, outside the frozen shortlist'), by the rules files themselves (`vocabulary_provenance` / `vocabulary`) and by every table of this file.

## 2. Registration and ordering

| what | file | sha256 | written_at (file) | registered_at | ledger sha at registration | `llm_round1` ledger rows at registration |
|---|---|---|---|---|---|---|
| LLM hypotheses round 1 labelled tables half A | studies/llm_round1/tables_minute_A.json, studies/llm_round1/tables_5minute_A.json | `eb2659777007ee01ed3f2373096bda0a2b5bb8ab1ad3dda5f20295eaf5d557b9` | 12:36 UTC | 2026-09-29T12:36:07 | `5bcee0a7bee8937f` | 0 |
| LLM hypotheses round 1 labelled tables half B | studies/llm_round1/tables_minute_B.json, studies/llm_round1/tables_5minute_B.json | `3d00a5c1b408d9c34eb2dbd641f5534c8462f9019d02a1f1770508c5b31c9c3a` | 12:36 UTC | 2026-09-29T12:36:07 | `5bcee0a7bee8937f` | 0 |
| LLM hypotheses round 1 half A | `studies/llm_round1/rules_round1_A.json` | `b9d335bc05bd42eb0d508c16a6cb08fee08fc0ba333846f44d4fa2dcfa7f29bc` | 2026-09-29T16:20:02+00:00 | 2026-09-29T17:08:47 | `39263cc8a1e76151` | 0 |
| LLM hypotheses round 1 half B | `studies/llm_round1/rules_round1_B.json` | `a65f06b9226ceda2a2eab9d81a3f1a942522d44e4474a5ca43a8dcbb1de9a18d` | 2026-09-29T16:22:54+00:00 | 2026-09-29T17:10:27 | `a03c3dc0277bb5ab` | 0 |
| LLM hypotheses round 0 (blind) (scored in `studies/llm_hypotheses/`) | `studies/llm_hypotheses/rules_round0.json` | `a3c5c06382227c9504e08e40682244756bb58261419be6d53fbba95ada3a1182` | - | 2026-09-29T03:51:33 (correction appended 2026-09-29T05:09:16) | - | - |

Ordering: the labelled tables were hashed at 12:36:07 UTC with 0 `llm_round1` ledger rows; the proposers wrote their files at 2026-09-29T16:20:02+00:00 (A) and 2026-09-29T16:22:54+00:00 (B) from `tables_<tf>_<half>.md` of ONE half each (their `inputs_read` lists; neither lists the other half's tables, a ledger file or any study's FINDINGS); the scorer registered each file (sha256, copy under `ledger/registered/`) as its first action, then scored. Proposer A also read `data/README.md`, `features_ext/README.md` and both shortlist JSONs; so did proposer B. Blindness to the scoring half is a process claim (the files' `inputs_read`) plus the ordering above; the tables of the other half existed on disk from 12:36 UTC, so it is not a data-ordering fact.
Ledger: `2253e804fdfa3ab9` before the combine stage -> `92dc548b205f174f` after; rows of family `llm_round1/*` now: 124 (A: 50, B: 50, crossfit: 24, combos: 0). Scoring stage: half A's file scored on half B at 2026-09-29T17:08:47, half B's on half A at 2026-09-29T17:10:27; combine at 2026-09-29T17:12:17, runtime 1496.5 s.

## 3. Definitions (fixed before any round-1 rule existed; `scorer.py` docstring, verbatim)

```
llm_round1 step 3: score the round-1 rule lists cross-fitted, through the harness (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1:
tables of one half, scored on the other, the cells shown logged as the family size for the max-T; Judge 2: the harness splitter, the
trials count = cells shown + rules proposed). Definitions fixed here and in r1_common.py before any round-1 rule existed.

    python scorer.py score --rules rules_round1_A.json      # registers the file (sha256, append-only), scores every rule on half B
    python scorer.py score --rules rules_round1_B.json      # ... on half A
    python scorer.py combine                                # Holm over the round, the greedy lists L_A / L_B, the cross-fitted verdict
    python scorer.py all --rules rules_round1_A.json rules_round1_B.json     # the three in one go
    python scorer.py smoke                                  # code-path test on synthetic rules with a REDIRECTED ledger (scratchpad):
                                                            # nothing it computes is a finding and nothing reaches OUT/ledger

Stage `score` (per rules file, both timeframes; the file's `half_seen` = X, the other half Y = the scoring rows):
  0. registration   appends {"kind": "pre_registration", "what": "LLM hypotheses round 1 half X", sha256, the seen tables' sha256 and cell
                    counts, the ledger sha} to ledger/registrations.jsonl (once per sha; never edited) and a byte-identical copy to
                    ledger/registered/; refuses to score a file whose sha does not match a registration line.
  1. protocol       r1_common.check_rule against the tables the proposer saw: REFUSED (no ledger row, still counted in the family):
                    a label / NOT_FEATURES column, a calendar-time proxy (n_events_asof, sl), depth > 3, a missing column. FLAGGED
                    (scored, ineligible for the combination): a column outside the shown vocabulary / listed pairs, a threshold that is
                    not a printed edge / level / split point.
  2. rule mask      a rule fires when every comparison holds; None / NaN -> the comparison is False (the SETUP is kept). keep = not fired.
  3. scoring        harness.score on a harness.Table built over half Y's rows alone (r1_common.sub_table; its IS split IS half Y, so the
                    kept-vs-skipped statistics, the session-matched random control (2,000 draws) and the permutation p are half Y's):
                    family "llm_round1/X" (X = the half the rules were proposed on; the config carries proposed_on / scored_on), each rule
                    on L1 and on L0 (robustness), the union of the round-1 rules, the 8 round-0 rules of the timeframe on the same rows
                    (family "llm_round1/X/round0"), and for a rule that uses a top-5 drifted source column (drift.json) the same rule
                    without that comparison (family "llm_round1/X/drift_refit").
  4. multiplicity   the max-T family on half Y = every labelled cell of tables_<tf>_X.json rebuilt on half Y's rows as a skip set (the
                    seen half's decile edges, levels and buckets; a cell whose kept or skipped side has < 2 rows cannot enter the
                    permutation but stays in the count) + the round-1 rules of X + the round-0 rules; statistic = the kept-vs-skipped
                    mean difference standardised by the pooled sd of the scored rows x sqrt(1/n_kept + 1/n_skipped) (pooled_z; the
                    Welch t round 0 used is reported per rule for the record but is unstable for 5-20-unit cells under permutation);
                    net permuted across half Y's rows, 2,000 seeded draws; per rule the single-step family-wise p
                    P(max over the family of |z*| >= |z_rule|), the null's 95th percentile of max |z|; Holm over the rules of the round
                    (m = every round-1 rule of both halves and both timeframes + the 16 round-0 rules; a refused or untestable rule
                    enters with p = 1) and, for the record, Holm at m = family size (degenerate: the permutation p's floor 1/2001 times
                    m exceeds 0.05 for m > 100, so it can never pass and is not the eligibility criterion; the max-T with the cells in
                    the family is); harness.pbo / spa / effective_trials over the direction's vectors (round-1 rules, union, round-0
                    rules); harness.deflated_sharpe of each kept book with n_trials = the family size; harness.bootstrap_ci per diff;
                    the per-block diff on half Y's six blocks.
Stage `combine` (needs at least one scored direction):
  5. eligibility    a round-1 rule is eligible when it is protocol-clean and, on the other half: max-T family-wise p < 0.05, Holm p over
                    the rules of the round < 0.05, control percentile >= 95, diff > 0.
  6. greedy         per direction, eligible rules in order of diff; a rule is added while the marginal diff >= 200 INR/trade and the
                    |net|-weighted winner recall does not fall; every step is a ledger row (family "llm_round1/X_combo"); L_X = the list.
  7. cross-fit      (a) fixed crossed list: L_A applied to half B's rows, L_B to half A's, one ledger row over all IS rows (family
                    "llm_round1/crossfit", rule "fixed_crossed"); (b) the shipped form L_A u L_B on every IS row (rule "shipped"; in-sample
                    for the proposing half, reported as such); (c) the 12-block OOF: for test block g of harness.purged_splits, the
                    candidate rules are those proposed on the OTHER half's tables and steps 5-6 are re-run on the training rows that lie
                    in g's half (labels the proposer never saw; harness.metrics with the 2,000-draw controls, the max-T family rebuilt on
                    those rows), the chosen list decides g; one ledger row (rule "oof12"); (d) CPCV: the same per test block of every
                    cpcv_splits split -> harness.cpcv_paths -> harness.score_paths (11 rows, family "llm_round1/crossfit/cpcv"); the
                    path distribution of the diff and of the control percentile is the number that counts; PBO / SPA / effective
                    trials over the crossfit family (fixed, shipped, oof12, 11 paths), DSR with n_trials = the whole round's family
                    size, bootstrap CI of the fixed crossed list, harness.go_no_go on it with the CPCV item, the declared columns
                    (no time proxy) and the null-tape certificate (studies/null_tapes_drift/tapes.null_tape_check on the certificate
                    tapes: real diff > gmm p95 AND > segment p95, session tapes carry the sign in >= 75%); a rule list with an
                    extended column (features_ext) cannot be replayed on the tapes and fails that item with the reason recorded.
  8. outputs        scores_<X>.json, results_round1.json (everything), scores_<tf>.csv, FINDINGS_draft.md (for the step-3 agent to finish
                    into FINDINGS.md / findings.json), candidate_<tf>.json only when go_no_go passes, with provenance
                    {"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"} for the user to accept or
                    reject (never copied to OUT/candidates/ by this script). Log: scorer.log.
```

Metric names are the harness's (`harness.metrics`): `diff` = kept mean net - skipped mean net (INR per trade) on the scored half; `control_pct` = the session-matched random control (2,000 draws) on that half; `perm_p` = the two-sided kept-vs-skipped permutation p (2,000 shuffles); loser recall = P(skipped | loser); winner recall (w) = kept winners' net / all winners' net; top-decile skipped = share of the top-decile winners skipped; slip8 = the kept book's mean at 8 pts slippage per side; blocks +/def = of the scored half's six harness blocks, those with kept mean > skipped mean / those with both sides populated; boot 90% CI = `harness.bootstrap_ci` of the diff (session blocks); L0 diff = the same rule on the uncut engine trade; DSR p = `harness.deflated_sharpe` of the kept book with n_trials = the family size. A rule's expected direction is always diff > 0.

## 4-5. Per-rule scores on the OTHER half, the union, the cross-fitted verdict (every number a ledger row; all columns outside the frozen shortlist (importance rule failed for every cluster))

### minute

### Rules proposed on the tables of half A, scored on half B (2,044 L1 units in 254 sessions; all-rows mean -1,070.60 INR; labelled cells seen 184, family size 200, max-T null p95 of max |t| 5.756, best family member `two_way:fz_readxhour_bin:NEW|10` |t| 4.429)

| id | rule | protocol | ledger id | kept n | skipped n | kept mean | skipped mean | diff | diff top1% off | perm p | Holm p (round) | max-T fw p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | blocks +/def | boot 90% CI | L0 diff | DSR p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r1A_m1 | `fz_read in ['THIN', 'REJECT', 'ACCEPTED']` | clean | 9486f9ece0a6d7d0 | 1665 | 379 | -1,069.17 | -1,076.86 | 7.69 | -52.31 | 0.9650 | 1.0000 | 1.0000 | 5.4 | 0.192 | 0.874 | 0.156 | -1,459.14 | 4/6 | [-228.75, 222.44] | 116.91 | 0.9949 |
| r1A_m2 | `hour_bin == 11` | clean | 99ee767ffbfcb0bc | 1723 | 321 | -1,058.47 | -1,135.73 | 77.27 | 100.91 | 0.6757 | 1.0000 | 1.0000 | 24.4 | 0.158 | 0.881 | 0.125 | -1,448.43 | 2/6 | [-206.71, 351.34] | 184.75 | 0.9951 |
| r1A_m3 | `hour_bin in ['11', '12']` and `fz_read in ['NEW', 'FIRST_PRINT', 'RECYCLE']` | clean | 04c389cc8c5f4f69 | 1978 | 66 | -1,061.09 | -1,355.66 | 294.57 | 83.02 | 0.4088 | 1.0000 | 1.0000 | 75.0 | 0.035 | 0.995 | 0.000 | -1,451.05 | 5/6 | [12.98, 628.29] | 428.82 | 0.9861 |
| r1A_m4 | `n_choch_since_bos == 0` | clean | 180567a92a79568f | 1511 | 533 | -1,072.80 | -1,064.36 | -8.44 | 25.43 | 0.9515 | 1.0000 | 1.0000 | 74.2 | 0.266 | 0.724 | 0.312 | -1,462.77 | 3/6 | [-242.31, 215.37] | -24.75 | 0.9976 |
| r1A_m5 | `hv3_dir_agree == True` and `hv3_bars_since >= 6` | clean | 02900b275f97e097 | 1496 | 548 | -1,087.13 | -1,025.47 | -61.66 | -213.94 | 0.6812 | 1.0000 | 1.0000 | 1.9 | 0.271 | 0.775 | 0.188 | -1,477.09 | 3/6 | [-274.94, 173.78] | -77.39 | 0.9970 |
| r1A_m6 | `fz_visit_n == 3` and `fz_read != LEAVE` | clean | 01ded11f8cec3b97 | 1887 | 157 | -1,051.40 | -1,301.42 | 250.02 | 28.27 | 0.3063 | 1.0000 | 1.0000 | 78.0 | 0.080 | 0.963 | 0.000 | -1,441.36 | 6/6 | [97.44, 408.17] | 470.46 | 0.9862 |
| r1A_m7 | `room_ahead_dist_atr >= 1.4782` and `room_ahead_dist_atr < 2.4394` | clean | d67b003cf69acea7 | 1730 | 314 | -1,057.38 | -1,143.41 | 86.02 | -9.35 | 0.6227 | 1.0000 | 1.0000 | 76.0 | 0.160 | 0.888 | 0.094 | -1,447.35 | 4/6 | [-208.18, 357.28] | 281.11 | 0.9973 |
| r1A_m8 | `hour_bin == >=15:20` | clean | 2e465ec9d9a8062c | 2018 | 26 | -1,069.16 | -1,182.44 | 113.28 | -94.11 | 0.8381 | 1.0000 | 1.0000 | 18.1 | 0.015 | 1.000 | 0.000 | -1,459.12 | 6/6 | [10.43, 220.06] | 51.90 | 0.9890 |
| union (round 1) | all scored rules | - | de1662598749599e | 629 | 1415 | -1,088.40 | -1,062.69 | -25.71 | -52.60 | 0.8551 | - | - | 17.2 | 0.704 | 0.360 | 0.688 | -1,478.36 | 3/6 | [-207.42, 182.73] | - | - |

Round-0 rules on the same rows (family `llm_round1/A/round0`): r0_m1 diff 56.08 ctrl 33.1 (`6c69cb72a07bf021`); r0_m2 diff 263.92 ctrl 42.4 (`2366c457a4ba3176`); r0_m3 diff 85.15 ctrl 0.7 (`705d36b9224ec3e2`); r0_m4 diff -194.95 ctrl 10.1 (`8e73cec17b092c01`); r0_m5 diff 5.93 ctrl 0.1 (`ed25a34d119ff559`); r0_m6 diff 664.63 ctrl 75.2 (`a565ae714ff947e1`); r0_m7 diff 144.52 ctrl 25.4 (`ef922129dbaab7ed`); r0_m8 diff n/a ctrl n/a (`4a862af1a78b0cf6`)
Direction family (17 vectors): PBO(diff) 0.7010, PBO(kept mean) 0.9424, SPA p 0.7465 (RC p 0.7830; unstudentised 0.6630), effective trials 1.19.

### Rules proposed on the tables of half B, scored on half A (2,408 L1 units in 324 sessions; all-rows mean -957.84 INR; labelled cells seen 181, family size 197, max-T null p95 of max |t| 4.673, best family member `one_way:hour_bin:<09:25` |t| 4.473)

| id | rule | protocol | ledger id | kept n | skipped n | kept mean | skipped mean | diff | diff top1% off | perm p | Holm p (round) | max-T fw p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | blocks +/def | boot 90% CI | L0 diff | DSR p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r1B_m1 | `hour_bin == <09:25` and `fz_read != LEAVE` | clean | a6e37c1d1033559b | 2356 | 52 | -986.45 | 338.82 | -1,325.28 | -349.36 | 0.0020 | 0.0960 | 0.1449 | 100.0 | 0.017 | 0.902 | 0.158 | -1,376.42 | 2/6 | [-2922.88, 37.47] | -1,217.05 | 0.9988 |
| r1B_m2 | `hour_bin == >=15:20` | clean | 6b0de2d11705c8c5 | 2379 | 29 | -957.63 | -974.83 | 17.20 | -139.60 | 0.9625 | 1.0000 | 1.0000 | 3.0 | 0.014 | 1.000 | 0.000 | -1,347.59 | 3/6 | [-90.78, 127.55] | 321.17 | 0.9818 |
| r1B_m3 | `fz_read == FIRST_PRINT` | clean | 89e097218440cfff | 2346 | 62 | -955.90 | -1,030.96 | 75.06 | -83.95 | 0.8056 | 1.0000 | 1.0000 | 15.9 | 0.026 | 0.987 | 0.000 | -1,345.87 | 3/6 | [-259.3, 381.07] | 338.14 | 0.9830 |
| r1B_m4 | `fz_read == ACCEPTED` and `hour_bin in ['11', '12', '13']` | clean | e900342e50104684 | 2362 | 46 | -953.12 | -1,200.12 | 247.00 | 89.11 | 0.4793 | 1.0000 | 1.0000 | 34.9 | 0.020 | 0.996 | 0.000 | -1,343.08 | 4/6 | [32.38, 476.3] | 299.88 | 0.9823 |
| r1B_m5 | `fz_read == LEAVE` and `hour_bin == 12` | clean | 31e444ec72e0ecec | 2257 | 151 | -949.38 | -1,084.23 | 134.86 | 50.70 | 0.5017 | 1.0000 | 1.0000 | 34.7 | 0.063 | 0.956 | 0.053 | -1,339.34 | 4/6 | [-65.92, 333.29] | 190.63 | 0.9832 |
| r1B_m6 | `hv3_bars_since <= 0.0` and `hv3_dir_agree == True` | clean | 0ff091e7372de925 | 1970 | 438 | -969.78 | -904.12 | -65.66 | -107.70 | 0.5962 | 1.0000 | 1.0000 | 1.1 | 0.176 | 0.787 | 0.158 | -1,359.74 | 2/6 | [-293.32, 169.71] | -286.96 | 0.9940 |
| r1B_m7 | `n_choch_since_bos >= 2.0` and `dir == up` | clean | 9b8b193661cf7c71 | 1989 | 419 | -988.38 | -812.82 | -175.57 | -64.29 | 0.1594 | 1.0000 | 1.0000 | 4.5 | 0.171 | 0.794 | 0.184 | -1,378.35 | 2/6 | [-388.47, 20.79] | -383.48 | 0.9985 |
| r1B_m8 | `touch_room_bars_ago >= 38.0` | clean | 68f4cc8c1e02dfdb | 2197 | 211 | -969.66 | -834.72 | -134.94 | -50.45 | 0.4278 | 1.0000 | 1.0000 | 18.8 | 0.087 | 0.886 | 0.105 | -1,359.62 | 3/6 | [-418.99, 135.6] | -328.36 | 0.9925 |
| union (round 1) | all scored rules | - | 3f7e85e910c63d1e | 1274 | 1134 | -1,034.32 | -871.91 | -162.41 | -100.52 | 0.0975 | - | - | 4.2 | 0.463 | 0.446 | 0.553 | -1,424.28 | 1/6 | [-286.89, -24.89] | - | - |

Round-0 rules on the same rows (family `llm_round1/B/round0`): r0_m1 diff -69.76 ctrl 2.5 (`1485dc5d83c14d34`); r0_m2 diff -40.79 ctrl 53.5 (`cf5fde85c9d3e5e5`); r0_m3 diff -77.34 ctrl 0.0 (`b71da929fd20d0fc`); r0_m4 diff -9.51 ctrl 77.0 (`46c5a9216b7a7271`); r0_m5 diff 27.24 ctrl 2.2 (`1ff56308d0a09217`); r0_m6 diff n/a ctrl n/a (`8095b3e9670478b9`); r0_m7 diff -87.59 ctrl 0.5 (`d8d06918e4c9d14e`); r0_m8 diff n/a ctrl n/a (`20ae3f57dc61c9dd`)
Direction family (17 vectors): PBO(diff) 0.5449, PBO(kept mean) 0.7406, SPA p 0.4365 (RC p 0.4435; unstudentised 0.6925), effective trials 1.14.

### Cross-fitted verdict (minute; family size of the round 389)

- Direction A -> B: eligible []; greedy list L_A = []
- Direction B -> A: eligible []; greedy list L_B = []

| row | ledger id | kept n | skipped n | kept share | diff | diff top1% off | perm p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| oof12 | 188e8939ee98df0e | 4452 | 0 | 1.0000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | None |

CPCV (nested selection per test block, 66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): blocks with a non-empty selection 0 of 132; diff median n/a, p5 n/a, min n/a, share > 0 0.000, kept share median 1.0000, control pct median n/a / p5 n/a.
12-block OOF selections: b00: B -> []; b01: B -> []; b02: B -> []; b03: B -> []; b04: B -> []; b05: B -> []; b06: A -> []; b07: A -> []; b08: A -> []; b09: A -> []; b10: A -> []; b11: A -> []
Crossfit family (12 vectors): PBO(diff) 1.0000, SPA p n/a, effective trials 1.0.
go/no-go: **fail** kept_share>=20% ok (1.0), kept_n>=300 ok (4452), diff>0 FAIL (None), diff_top1_removed>0 FAIL (None), kept_mean_slip8>0 FAIL (None), sign_blocks>=8/12 FAIL (None), control_pct>=95 FAIL (None), cpcv_p5_diff>0 FAIL (None), pbo<=0.2 FAIL (1.0), dsr_p<0.1 FAIL (0.9933), boot_ci_excludes_0 FAIL ([nan, nan]), null_tape:evaluated FAIL (no rule list (nothing to check)), no_time_proxy_columns ok ([]); no fixed crossed list (no rule chosen in either direction); go/no-go read on the oof12 row; DSR p 0.9933

### 5minute

### Rules proposed on the tables of half A, scored on half B (398 L1 units in 194 sessions; all-rows mean -842.96 INR; labelled cells seen 122, family size 138, max-T null p95 of max |t| 3.869, best family member `one_way:card_leave_kind:normal` |t| 2.617)

| id | rule | protocol | ledger id | kept n | skipped n | kept mean | skipped mean | diff | diff top1% off | perm p | Holm p (round) | max-T fw p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | blocks +/def | boot 90% CI | L0 diff | DSR p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r1A_f1 | `fz_gate == TAKE` | clean | 1a67dc2d1859b4aa | 286 | 112 | -1,021.88 | -386.07 | -635.81 | -417.92 | 0.2319 | 1.0000 | 1.0000 | 49.6 | 0.264 | 0.600 | 0.545 | -1,411.84 | 2/6 | [-1423.61, 87.81] | -1,218.69 | 0.9996 |
| r1A_f2 | `fz_read == PENDING` | clean | 532bd54b69c6ba44 | 310 | 88 | -702.99 | -1,336.02 | 633.03 | 637.39 | 0.2704 | 1.0000 | 1.0000 | 87.9 | 0.233 | 0.860 | 0.091 | -1,092.96 | 5/6 | [-108.36, 1376.36] | 1,165.49 | 0.9732 |
| r1A_f3 | `hour_bin in ['11', '12']` | clean | 933b1a9ab1418dba | 291 | 107 | -912.58 | -653.62 | -258.96 | -285.01 | 0.6297 | 1.0000 | 1.0000 | 20.4 | 0.274 | 0.704 | 0.364 | -1,302.54 | 3/6 | [-1114.69, 657.05] | 360.68 | 0.9944 |
| r1A_f4 | `n_choch_since_bos == 2` | clean | b17b23f2469ad58b | 325 | 73 | -655.19 | -1,678.89 | 1,023.69 | 780.46 | 0.1064 | 1.0000 | 1.0000 | 70.1 | 0.206 | 0.895 | 0.091 | -1,045.16 | 4/6 | [215.03, 1940.85] | 1,988.77 | 0.9762 |
| r1A_f5 | `hv3_dir_agree == True` and `hv3_bars_since >= 2` and `hv3_bars_since < 13` | clean | 4f2674ed8b5dd26d | 366 | 32 | -803.15 | -1,298.24 | 495.08 | 277.77 | 0.5872 | 1.0000 | 1.0000 | 10.9 | 0.078 | 0.957 | 0.000 | -1,193.12 | 4/6 | [-310.27, 1232.54] | 1,249.09 | 0.9745 |
| r1A_f6 | `touch_room_last == held` | clean | 53560fc1a3ef67e7 | 368 | 30 | -768.16 | -1,760.51 | 992.35 | 776.61 | 0.2734 | 1.0000 | 1.0000 | 88.2 | 0.085 | 0.967 | 0.000 | -1,158.12 | 4/6 | [-120.42, 1913.86] | 2,131.32 | 0.9745 |
| r1A_f7 | `touch_prot_last in ['none', 'na']` | clean | da8191d05262d10a | 362 | 36 | -867.29 | -598.22 | -269.07 | -489.53 | 0.7496 | 1.0000 | 1.0000 | 55.9 | 0.078 | 0.890 | 0.091 | -1,257.26 | 2/6 | [-1717.5, 948.67] | -2,493.64 | 0.9921 |
| r1A_f8 | `fz_visit_n == 3` and `fz_read in ['LEAVE', 'PENDING']` | clean | 534f94d8adbd8276 | 373 | 25 | -864.52 | -521.24 | -343.28 | -557.14 | 0.7361 | 1.0000 | 1.0000 | 8.5 | 0.061 | 0.950 | 0.000 | -1,254.48 | 4/6 | [-1473.35, 679.08] | 1,086.55 | 0.9830 |
| union (round 1) | all scored rules | - | a904c96c914f0712 | 94 | 304 | -1,308.29 | -699.07 | -609.22 | -657.24 | 0.2894 | - | - | 17.6 | 0.753 | 0.195 | 0.818 | -1,698.26 | 0/6 | [-1306.71, 109.16] | - | - |

Round-0 rules on the same rows (family `llm_round1/A/round0`): r0_f1 diff -411.80 ctrl 97.2 (`dbeedf6c80c4d6de`); r0_f2 diff -1,364.52 ctrl 0.1 (`26fcb4cfb7b55e0d`); r0_f3 diff -507.82 ctrl 0.3 (`5dd8f278f7b4f153`); r0_f4 diff -381.59 ctrl 87.0 (`a531609e781d283c`); r0_f5 diff -481.09 ctrl 0.9 (`806be1a25e1851b3`); r0_f6 diff 181.12 ctrl 56.8 (`0bdd90882fc7efbc`); r0_f7 diff -116.82 ctrl 8.9 (`c22b7ac28608b506`); r0_f8 diff 2,815.56 ctrl 87.5 (`3aed47e0e991f16c`)
Direction family (17 vectors): PBO(diff) 0.6615, PBO(kept mean) 0.1601, SPA p 0.4040 (RC p 0.4715; unstudentised 0.3905), effective trials 1.32.

### Rules proposed on the tables of half B, scored on half A (428 L1 units in 214 sessions; all-rows mean -677.17 INR; labelled cells seen 118, family size 134, max-T null p95 of max |t| 3.862, best family member `two_way:fz_readxhour_bin:LEAVE|<09:25` |t| 2.644)

| id | rule | protocol | ledger id | kept n | skipped n | kept mean | skipped mean | diff | diff top1% off | perm p | Holm p (round) | max-T fw p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | blocks +/def | boot 90% CI | L0 diff | DSR p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r1B_f1 | `fz_read == NEW` | clean | eaf53fdc0790c410 | 389 | 39 | -702.03 | -429.16 | -272.87 | 492.46 | 0.6847 | 1.0000 | 1.0000 | 66.5 | 0.080 | 0.872 | 0.154 | -1,092.00 | 2/6 | [-2154.3, 1474.96] | -298.91 | 0.9562 |
| r1B_f2 | `n_choch_since_bos == 2.0` | clean | 065cf63cc2e5c415 | 358 | 70 | -576.95 | -1,189.72 | 612.77 | 337.70 | 0.2629 | 1.0000 | 1.0000 | 82.0 | 0.176 | 0.841 | 0.231 | -966.92 | 4/6 | [-125.24, 1367.44] | 2,229.44 | 0.9116 |
| r1B_f3 | `touch_room_last == held` | clean | 5d6cb8947fafba79 | 397 | 31 | -648.91 | -1,039.10 | 390.19 | 141.57 | 0.6297 | 1.0000 | 1.0000 | 61.8 | 0.083 | 0.945 | 0.077 | -1,038.87 | 3/6 | [-604.74, 1342.89] | 2,309.62 | 0.9205 |
| r1B_f4 | `hour_bin in ['<09:25', '15']` | clean | 9cefdef775d05cc0 | 373 | 55 | -810.74 | 228.67 | -1,039.41 | -487.37 | 0.0885 | 1.0000 | 0.9990 | 93.1 | 0.123 | 0.799 | 0.385 | -1,200.70 | 2/6 | [-2468.77, 238.8] | -10.50 | 0.9873 |
| r1B_f5 | `fz_read == PENDING` and `hour_bin in ['09', '10', '11', '12']` | clean | d7f6099c80b81aaf | 375 | 53 | -569.91 | -1,436.08 | 866.18 | 603.84 | 0.1629 | 1.0000 | 1.0000 | 91.5 | 0.136 | 0.927 | 0.000 | -959.87 | 4/6 | [30.13, 1817.49] | 1,832.51 | 0.8912 |
| r1B_f6 | `touch_prot_last == pending` | clean | d7e8f342fa877b00 | 350 | 78 | -737.42 | -406.80 | -330.63 | -614.40 | 0.5432 | 1.0000 | 1.0000 | 10.7 | 0.169 | 0.811 | 0.077 | -1,127.39 | 2/6 | [-1130.62, 466.07] | -774.55 | 0.9687 |
| r1B_f7 | `fz_gate == BLOCK` | clean | de41f9ab8006384b | 325 | 103 | -895.16 | 10.66 | -905.82 | -508.48 | 0.0620 | 1.0000 | 0.9905 | 83.8 | 0.213 | 0.623 | 0.462 | -1,285.12 | 1/6 | [-1924.71, 81.05] | -463.41 | 0.9981 |
| r1B_f8 | `fz_visit_n == 2.0` and `fz_read == PENDING` | clean | c3ab2a20872e1683 | 403 | 25 | -668.47 | -817.33 | 148.85 | -96.27 | 0.8751 | 1.0000 | 1.0000 | 29.8 | 0.057 | 0.949 | 0.077 | -1,058.44 | 4/6 | [-1181.73, 1390.13] | 2,898.41 | 0.9390 |
| union (round 1) | all scored rules | - | a604066a11ff9dd8 | 159 | 269 | -691.39 | -668.76 | -22.62 | -86.55 | 0.9525 | - | - | 75.5 | 0.625 | 0.351 | 0.692 | -1,081.35 | 4/6 | [-659.76, 659.77] | - | - |

Round-0 rules on the same rows (family `llm_round1/B/round0`): r0_f1 diff -1,344.08 ctrl 99.3 (`b73369b876e56a3c`); r0_f2 diff -1,059.10 ctrl 0.3 (`62b7fc0ffd1f1dd6`); r0_f3 diff 359.23 ctrl 9.8 (`3bd2a58afe20b8f4`); r0_f4 diff -1,068.15 ctrl 11.3 (`1bb6db09f46a5220`); r0_f5 diff -632.10 ctrl 0.8 (`97e525a4b046e078`); r0_f6 diff 270.04 ctrl 4.7 (`77f5e8aa5923604e`); r0_f7 diff 319.59 ctrl 14.0 (`fbbe19e589805ccc`); r0_f8 diff n/a ctrl n/a (`4fba89aee8f57a38`)
Direction family (17 vectors): PBO(diff) 0.4267, PBO(kept mean) 0.3958, SPA p 0.2190 (RC p 0.2995; unstudentised 0.3750), effective trials 1.34.

### Cross-fitted verdict (5minute; family size of the round 264)

- Direction A -> B: eligible []; greedy list L_A = []
- Direction B -> A: eligible []; greedy list L_B = []

| row | ledger id | kept n | skipped n | kept share | diff | diff top1% off | perm p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| oof12 | 592d42e2a466698e | 826 | 0 | 1.0000 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | None |

CPCV (nested selection per test block, 66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): blocks with a non-empty selection 0 of 132; diff median n/a, p5 n/a, min n/a, share > 0 0.000, kept share median 1.0000, control pct median n/a / p5 n/a.
12-block OOF selections: b00: B -> []; b01: B -> []; b02: B -> []; b03: B -> []; b04: B -> []; b05: B -> []; b06: A -> []; b07: A -> []; b08: A -> []; b09: A -> []; b10: A -> []; b11: A -> []
Crossfit family (12 vectors): PBO(diff) 1.0000, SPA p n/a, effective trials 1.0.
go/no-go: **fail** kept_share>=20% ok (1.0), kept_n>=80 ok (826), diff>0 FAIL (None), diff_top1_removed>0 FAIL (None), kept_mean_slip8>0 FAIL (None), sign_blocks>=8/12 FAIL (None), control_pct>=95 FAIL (None), cpcv_p5_diff>0 FAIL (None), pbo<=0.2 FAIL (1.0), dsr_p<0.1 FAIL (0.9915), boot_ci_excludes_0 FAIL ([nan, nan]), null_tape:evaluated FAIL (no rule list (nothing to check)), no_time_proxy_columns ok ([]); no fixed crossed list (no rule chosen in either direction); go/no-go read on the oof12 row; DSR p 0.9915

## 6. The round-0 (blind) rules inside this family

The 16 round-0 rules (`studies/llm_hypotheses/rules_round0.json`, sha `a3c5c063...`) were already scored on the full IS table in `studies/llm_hypotheses/` (family `llm_hypotheses/round0`; null result, no rule under Holm p 0.05, min raw p 0.0625). Those ledger ids are cited here and are NOT re-scored on the full table. Because this study's scoring rows are one half at a time, the scorer re-scored each round-0 rule on each half (families `llm_round1/A/round0` = half B rows, `llm_round1/B/round0` = half A rows) so that they enter the max-T family, PBO and SPA of every direction: the family size per timeframe and direction = labelled cells shown + round-1 rules of that half + 8 round-0 rules.

| id | full-IS ledger id (`llm_hypotheses/round0`) | untestable on full IS | half B rows: diff / ctrl (`llm_round1/A/round0`) | half A rows: diff / ctrl (`llm_round1/B/round0`) |
|---|---|---|---|---|
| r0_m1 | `1c3b030ae6d8d040` | no | 56.08 / 33.1 (`6c69cb72a07bf021`) | -69.76 / 2.5 (`1485dc5d83c14d34`) |
| r0_m2 | `6bc2dafc5db55758` | no | 263.92 / 42.4 (`2366c457a4ba3176`) | -40.79 / 53.5 (`cf5fde85c9d3e5e5`) |
| r0_m3 | `6a0004c624ff8136` | no | 85.15 / 0.7 (`705d36b9224ec3e2`) | -77.34 / 0.0 (`b71da929fd20d0fc`) |
| r0_m4 | `44c18f849dbe54a5` | no | -194.95 / 10.1 (`8e73cec17b092c01`) | -9.51 / 77.0 (`46c5a9216b7a7271`) |
| r0_m5 | `b9e8b3ca7cfe53b0` | no | 5.93 / 0.1 (`ed25a34d119ff559`) | 27.24 / 2.2 (`1ff56308d0a09217`) |
| r0_m6 | `7e2e3b02928d00c0` | yes | 664.63 / 75.2 (`a565ae714ff947e1`) | n/a / n/a (`8095b3e9670478b9`) |
| r0_m7 | `eb1806faee8fe097` | no | 144.52 / 25.4 (`ef922129dbaab7ed`) | -87.59 / 0.5 (`d8d06918e4c9d14e`) |
| r0_m8 | `5645244e4b0400db` | yes | n/a / n/a (`4a862af1a78b0cf6`) | n/a / n/a (`20ae3f57dc61c9dd`) |
| r0_f1 | `3b66a4e1aa363c21` | no | -411.80 / 97.2 (`dbeedf6c80c4d6de`) | -1,344.08 / 99.3 (`b73369b876e56a3c`) |
| r0_f2 | `d9bdb49fd0899705` | no | -1,364.52 / 0.1 (`26fcb4cfb7b55e0d`) | -1,059.10 / 0.3 (`62b7fc0ffd1f1dd6`) |
| r0_f3 | `d1995f0e96e190f4` | no | -507.82 / 0.3 (`5dd8f278f7b4f153`) | 359.23 / 9.8 (`3bd2a58afe20b8f4`) |
| r0_f4 | `82b3a4bb1a3d7cb8` | no | -381.59 / 87.0 (`a531609e781d283c`) | -1,068.15 / 11.3 (`1bb6db09f46a5220`) |
| r0_f5 | `d92c44d6adc501ac` | no | -481.09 / 0.9 (`806be1a25e1851b3`) | -632.10 / 0.8 (`97e525a4b046e078`) |
| r0_f6 | `71acfc38786c1cdf` | no | 181.12 / 56.8 (`0bdd90882fc7efbc`) | 270.04 / 4.7 (`77f5e8aa5923604e`) |
| r0_f7 | `d62b114016d51dcb` | no | -116.82 / 8.9 (`c22b7ac28608b506`) | 319.59 / 14.0 (`fbbe19e589805ccc`) |
| r0_f8 | `af6b26dbc455e8f7` | yes | 2,815.56 / 87.5 (`3aed47e0e991f16c`) | n/a / n/a (`4fba89aee8f57a38`) |

## 7. What the earlier studies already found (read, not re-run)

| study | result (its FINDINGS.md) | bearing on this round |
|---|---|---|
| `h1_gate_audit` | null: the frozen ST7/ST8 gate is not a loser filter (precision = base rate; 1 min skips 84% of top-decile winners; its gain is cost avoidance) | `fz_gate` rules (r1A_f1 skips TAKE, r1B_f7 skips BLOCK) are re-readings of that gate on one half each; both directions are in this family |
| `h2_h3_h4` | null on both timeframes: `n_choch_since_bos >= k` SETUPs are not the losers (1 min -1,030 / -837 / -936 vs -1,090 after a BOS); high-volume agreement and level verdicts do not select | the `n_choch_since_bos`, `hv3_*`, `touch_*` rules here are the same hypotheses in cell form; the proposers' own files record that the two halves disagree on the direction of the CHoCH-count effect on 1 min (A: 0 is worst; B: >= 2 up is below base) |
| `session_stop` | null on 1 min, inconclusive on 5 min (N3 alone rejects); the first 'session memory' finding was an artefact of outcome-dependent durations | no session-ledger column was in the shown vocabulary |
| `exit_policy` | null: no exit variant rescues the book; the label stays the Foundation L1 exit | every number here is on the L1 book with Foundation exits |
| `null_tapes_drift` | no real gate beats a tape p95 (0 of 18 cells); IS-early vs IS-late drift AUC 0.95 / 0.97; time proxies `sl`, `n_events_asof` refused; top-5 drifted sources 1 min: atr14, atr_bps, days_to_expiry, gap_pts, sess_cumvol_ratio20s; 5 min: atr14, atr_bps, hv3_ratio, n_rooms_alive, range_3h_pts | no round-1 rule uses a time proxy or a top-5 drifted source column (the scorer's drift refit therefore has no row); the null-tape certificate is a required `go_no_go` item and runs on the fixed crossed list when one exists |
| `importance` | 0 of 38 / 39 clusters pass the pre-registered MDA rule; the shortlist is empty; the full 276-feature bagging is a ceiling with OOF AUC 0.59 (1 min), gate keeps every row, CPCV diff median -19 | the reason for the EMPTY-SHORTLIST RULE (section 1) |

## 8. Multiplicity: the family and its statistics

| tf | direction | labelled cells shown | cells with a skip set on the scored half | round-1 rules | round-0 rules | family size (max-T) | testable masks | null p95 of max |z| | best family member | its |z| / fw p | direction vectors | PBO(diff) | SPA p (unstud.) | effective trials |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minute | A -> B | 184 | 183 | 8 (8 scored) | 8 | **200** | 188 | 5.756 | `two_way:fz_readxhour_bin:NEW|10` | 4.429 / 0.1959 | 17 | 0.7010 | 0.7465 (0.6630) | 1.19 |
| minute | B -> A | 181 | 180 | 8 (8 scored) | 8 | **197** | 185 | 4.673 | `one_way:hour_bin:<09:25` | 4.473 / 0.0655 | 17 | 0.5449 | 0.4365 (0.6925) | 1.14 |
| 5minute | A -> B | 122 | 121 | 8 (8 scored) | 8 | **138** | 126 | 3.869 | `one_way:card_leave_kind:normal` | 2.617 / 0.6607 | 17 | 0.6615 | 0.4040 (0.3905) | 1.32 |
| 5minute | B -> A | 118 | 117 | 8 (8 scored) | 8 | **134** | 123 | 3.862 | `two_way:fz_readxhour_bin:LEAVE|<09:25` | 2.644 / 0.6222 | 17 | 0.4267 | 0.2190 (0.3750) | 1.34 |

Holm over the rules of the round: m = 48 (32 round-1 rules of both halves and both timeframes + 16 round-0 rules); minimum adjusted p 0.0960; raw p per rule in `results_round1.json` (`holm.raw_p`, `holm.rules`). The family size of the whole round per timeframe (DSR `n_trials`, `family_size_total`): minute 389, 5minute 264. The max-T statistic is the pooled-sd standardised mean difference (`scorer.pooled_z`; fixed at step 1 before any round-1 rule existed, because the Welch t round 0 used has a permutation null of max |t| near 10 once 5-20-unit cells enter the family: `NOTES.md`); the Welch t is reported per rule in `scores_<half>.json` (`max_t.rule_welch_t`) for the record.

## 9. Candidate or null

- **minute: null.** No rule eligible in either direction; `harness.go_no_go` on the nested 12-block OOF row (`188e8939ee98df0e`) fails: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated. Nothing is written to `candidates/`.
- **5minute: null.** No rule eligible in either direction; `harness.go_no_go` on the nested 12-block OOF row (`592d42e2a466698e`) fails: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated. Nothing is written to `candidates/`.

Observations (from the tables above; no new statistic):

- `r1B_m1` (minute, proposed on half B: `hour_bin == <09:25` and `fz_read != LEAVE`) is the only rule of the round with a permutation p below 0.05 on the other half (perm p 0.0020, Holm p over the round 0.0960, max-T fw p 0.1449), and it has the WRONG sign: the 52 units it skips on half A are the better ones (skipped mean 338.82 vs kept -986.45, diff -1,325.28; L0 diff -1,217.05). The cell it was written from (`hour_bin = <09:25`, the worst bin of half B) is the best family member on half A in the opposite direction (`one_way:hour_bin:<09:25`, |z| 4.473, fw p 0.0655): the opening-minutes effect flips sign between 2021-10..2023-11 and 2023-11..2025-12, which is the IS-early vs IS-late drift `null_tapes_drift` measured (AUC 0.95 / 0.97), not a gate. The control percentile of 100.0 beside a negative diff is the known disagreement of the session-matched control with the pooled diff for a near-complete keep (h1_gate_audit, section 1).

- Cross-half agreement: of the 16 minute rules, 6 (A -> B) and 4 (B -> A) have diff > 0 on the other half, none with control percentile >= 95 or max-T fw p < 0.05; the two proposers read the same `n_choch_since_bos` table in opposite directions (A: skip 0, B: skip >= 2 up) and both lose on the other half (r1A_m4 -8, r1B_m7 -176). On 5 minutes the four positive-diff rules per direction (best r1A_f4 +1,024 / r1B_f5 +866) carry control percentiles 70-92 with 25-73 skipped units and bootstrap CIs that include 0 (tables above). The unions skip 45-76% of the book and lose on every direction (minute -26 / -162; 5 minutes -609 / -23).

## 10. What would falsify this finding

- A round-1 rule (unchanged sha) whose OTHER-half ledger row shows diff > 0, control percentile >= 95, max-T family-wise p < 0.05 with the labelled cells of its seen tables in the family, and Holm p over the rules of the round < 0.05, AND whose fixed crossed list passes every `harness.go_no_go` item including the CPCV p5, the null-tape certificate and the declared-columns item.
- A rebuild of the L1 table (`build/build.py`) on which the per-half re-scores of the same rules change sign for the eligible set (the half boundaries are the harness's 12 IS blocks; a different block count is a different study and a new registration).
- A user decision to re-open the vocabulary (a non-empty shortlist under a re-registered importance rule): the same two files could then be re-scored under a smaller family; that is a new round with its own sha and the multiplicity of this one carried forward.

## 11. Caveats

- Every column used is outside the frozen shortlist (importance rule failed for every cluster); the vocabulary of the tables was an exploratory choice (top-8 MDA clusters, swaps stated) and any survivor would need the user's acceptance of that vocabulary.
- The ledger rows of `llm_round1/*` carry the exploratory label only through the registration lines and the rules files, not in each row's `config` (schema fixed at step 1; the ledger is append-only).
- The proposers are Claude agents; their `reason` texts cite the seen half's cells and the user's words. Blindness to the scoring half is their `inputs_read` self-report plus the ordering of the artefacts, not a verifiable data-ordering fact (the other half's tables existed on disk from 12:36 UTC).
- The proposers read `features_ext/README.md`, `data/README.md` and both shortlist JSONs beside their half's tables; none of those carries a labelled number of the scoring half.
- The cells of the seen half are rebuilt on the scored half with the SEEN half's decile edges, so a decile cell on the other half is not a decile there; the family therefore counts the proposer's choice set, not equal-sized cells.
- The 5-minute halves hold 398 / 428 L1 units; rules firing on 40-100 units have 90% bootstrap CIs of the diff several hundred INR wide (see the tables): the 5-minute verdicts are underpowered, as every 5-minute study of the program has been.
- Holm at m = family size (`holm_p_family` in `scores_<half>.json`) is degenerate (permutation p floor 1/2001 x m > 0.05 for m > 100) and is reported for the record only; the max-T with the cells in the family is the eligibility criterion.
- The nested CPCV re-runs the eligibility and greedy steps on the training rows of each test block's half with `harness.metrics` (no ledger row per inner fit); only the 11 path rows and the oof12 row are ledger rows, as the design says.
- Round-0 full-IS numbers are cited from `studies/llm_hypotheses/findings.json` and not re-scored; the per-half re-scores of the round-0 rules are new ledger rows (`llm_round1/<half>/round0`), needed for the family on each half.

## 12. Files

- `studies/llm_round1/FINDINGS.md`
- `studies/llm_round1/NOTES.md`
- `studies/llm_round1/findings.json`
- `studies/llm_round1/r1_common.py`
- `studies/llm_round1/results_round1.json`
- `studies/llm_round1/rules_round1_A.json`
- `studies/llm_round1/rules_round1_B.json`
- `studies/llm_round1/run_all.nohup`
- `studies/llm_round1/scorer.log`
- `studies/llm_round1/scorer.py`
- `studies/llm_round1/scores_5minute.csv`
- `studies/llm_round1/scores_A.json`
- `studies/llm_round1/scores_B.json`
- `studies/llm_round1/scores_minute.csv`
- `studies/llm_round1/tables.log`
- `studies/llm_round1/tables.py`
- `studies/llm_round1/tables_5minute_A.json`
- `studies/llm_round1/tables_5minute_A.md`
- `studies/llm_round1/tables_5minute_B.json`
- `studies/llm_round1/tables_5minute_B.md`
- `studies/llm_round1/tables_minute_A.json`
- `studies/llm_round1/tables_minute_A.md`
- `studies/llm_round1/tables_minute_B.json`
- `studies/llm_round1/tables_minute_B.md`
- `studies/llm_round1/tables_summary.json`
- `studies/llm_round1/write_findings.py`
- `studies/llm_round1/smoke_logs/smoke_relax_1_no_selection.log`
- `studies/llm_round1/smoke_logs/smoke_relax_2_selection_path.log`
- `studies/llm_round1/smoke_logs/smoke_strict_1.log`
- `ledger/registrations.jsonl` (lines: tables half A / B, rules half A / B)
- `ledger/registered/rules_round1_A.*.json`, `ledger/registered/rules_round1_B.*.json`
- `ledger/trials.jsonl` (families `llm_round1/A`, `llm_round1/A/round0`, `llm_round1/B`, `llm_round1/B/round0`, `llm_round1/crossfit`, `llm_round1/crossfit/cpcv`)
