# llm_round1: FINDINGS (draft written by scorer.py at 2026-09-29T17:12:17; the step-3 agent completes it into FINDINGS.md / findings.json)

**Directions scored**: A -> B, B -> A. Holm over the rules of the round: m = 48. Eligibility: protocol-clean and, on the other half: diff > 0, control pct >= 95.0, max-T family-wise p < 0.05 (family = labelled cells shown + rules proposed), Holm p over the rules of the round (m = 48) < 0.05. Greedy: eligible rules in order of diff; add while the marginal diff >= 200.0 INR/trade and the |net|-weighted winner recall does not fall; every step a ledger row. **null_result = True** (harness.go_no_go on the fixed crossed list, with the CPCV item).

## Definitions

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

## minute

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

## 5minute

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

## Files

- `studies/llm_round1/NOTES.md`
- `studies/llm_round1/r1_common.py`
- `studies/llm_round1/results_round1.json`
- `studies/llm_round1/rules_round1_A.json`
- `studies/llm_round1/rules_round1_B.json`
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
