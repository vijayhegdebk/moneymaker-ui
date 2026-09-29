# gate_family: FINDINGS (the ONE learned-gate trial family; DESIGN_PANEL quant-ml-canon-meta-label-gate merged with decision-making-1-fullinfo-bandit-policy-tree-gate and BRIEF H5; both judges' fixes binding)

Generated 2026-09-29T13:16:14 by `finalize.py` from `results/<tf>/<sub>/<model>.pkl`, the harness ledger and `results/labels_<tf>.json`. **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 intraday book) trains and judges; L0 / L2 / L3 are one robustness table (never candidates). Every number below is a harness ledger row (id given) or an output file of this folder; nothing is invented. Scripts: `labels.py`, `gf_lib.py`, `run_gf.py`, `finalize.py` (shas {'gf_lib.py': 'de9c8ad74f850231', 'run_gf.py': '62c259a099337976', 'labels.py': '89883855c50a5a10', 'finalize.py': 'a58dddeb15a2bcbf'}); logs `labels_<tf>.log`, `run_<tf>_<sub>.log`, `procA.nohup`, `procB.nohup`, `finalize.log`.

## 0. Result in one paragraph

**Null result on both timeframes: no candidate file is written.** **minute**: 47 ledger rows in the family (PBO(diff) 0.235, SPA p 0.855, effective trials 1.64); h5_full finalist h5rules (rule list by construction) CPCV p5 -98.24, go/no-go FAIL (11 items); candidate: NONE. **5minute**: 106 ledger rows in the family (PBO(diff) 0.606, SPA p 0.454, effective trials 1.06); context finalist bag4 -> distilled rules CPCV p5 -3,019.05, go/no-go FAIL (11 items); candidate: NONE. Read against the ceiling (section 3): the full-information bagging ranks winners at AUC 0.59 / 0.50 and its gate keeps everything; the learned gates here, inside the frozen vocabulary (hour and direction) and outside it (the full table, H5 as pre-registered), move the kept-vs-skipped difference within the random band on the CPCV paths and fail the pre-registered pass rule. Sequential RL was not used: section 7.

## 1. The empty-shortlist rule and the two sub-families

`features_shortlist/<tf>/shortlist.json` (sha-registered 2026-09-29T11:31:33, corrected 12:07:12) has **n_shortlisted = 0 on both timeframes** (0 of 38 / 39 clusters pass the pre-registered clustered-MDA rule; `allowed_columns = []`; no newer shortlist line exists in `ledger/registrations.jsonl`), so the EMPTY-SHORTLIST RULE of the task applies and TWO sub-families are run and reported side by side:

- **(I) `context`** — features = `hour_bin` one-hot (9 levels) + `dir` (as `dir=down`; `dir=up` is its complement): the context the design always includes and the user's own words ("it is different for different times"). Inside the frozen vocabulary. Models (a)-(e) reduce to what two context columns allow; the policy trees over hour_bin x dir are the natural form; (e) is the hour-bin scorecard.
- **(II) `h5_full`** — H5 exactly as pre-registered in `docs/STRATEGY_ANALYSIS_TODO.md` S49, on the FULL as-of table: `imp_lib.assemble(tf)` (the importance study's 276 / 238-feature matrix: `harness.design` + the 61 `features_ext` columns, its drops and missing indicators) MINUS the two calendar proxies `drift.json` names (`sl`, `n_events_asof`: null_tapes_drift FINDINGS section 6 — a rule on a time proxy is a calendar rule and the gate studies refuse it on the real tape by the same rule `tapes.rule_mask` enforces on the tapes) = **274 / 236 features**. **Every row of this sub-family is OUTSIDE THE FROZEN SHORTLIST** (the importance rule failed for every cluster); a candidate from it would carry `provenance.vocabulary = "outside the frozen shortlist (importance rule failed for every cluster)"` for the user to accept or reject. Its models: the H5 depth-3 tree (`dt3`), the H5 greedy rule list by kept expectancy (`h5rules`), the HGB (b) as the gradient-boosting ceiling (`hgbc`, with the unconstrained variant as a sensitivity), the scorecard (e) with at most 12 / 6 source features; the bagging ceiling is the importance study's own (cited, not refit).

Both sub-families are ONE ledger family (`gate_family/*`): PBO, SPA and the effective trial count are computed over every row of the timeframe with label L1, and the DSR's `n_trials` is the number of gate_family rows of the timeframe over all labels.

## 2. Definitions (fixed before the numbers; `gf_lib.py` docstring verbatim)

```
gate_family: the ONE learned-gate trial family of the FZ v3 program (DESIGN_PANEL quant-ml-canon-meta-label-gate merged with
decision-making-1-fullinfo-bandit-policy-tree-gate and BRIEF H5; both judges' fixes on both studies are binding). Every definition
below was fixed before any number of this study was looked at; the numbers of the earlier studies (importance, null_tapes_drift,
exit_policy, h1, h2_h3_h4, session_stop) were read, as the task requires.

EMPTY-SHORTLIST RULE (in force: features_shortlist/<tf>/shortlist.json has n_shortlisted = 0 on both timeframes, allowed_columns = []):
two sub-families are run and reported side by side.
  (I)  "context"  features = hour_bin one-hot (9 levels) + dir (dir=down; dir=up is its complement and is dropped): the context the
       design always includes and the user's own words ("it is different for different times"). Inside the frozen vocabulary.
  (II) "h5_full"  H5 as pre-registered in docs/STRATEGY_ANALYSIS_TODO.md S49 on the FULL as-of table: imp_lib.assemble(tf) (the same
       276 / 238-feature matrix the importance study used: harness.design + the 61 features_ext columns, > 40% NaN / constant /
       duplicate / second-one-hot-level drops, missing indicators) MINUS the two calendar proxies drift.json names (`sl`,
       `n_events_asof`; null_tapes_drift FINDINGS section 6: "a rule on a time proxy is a calendar rule, not a market rule ...
       the gate studies refuse it on the real tape by the same rule"). OUTSIDE THE FROZEN SHORTLIST: every table row and ledger
       note of this sub-family says so; a candidate from it carries provenance.vocabulary = "outside the frozen shortlist
       (importance rule failed for every cluster)".

Unit / labels     harness.load(tf) (L1 = the 15:25 intraday book: the training and judging label). Robustness labels (one table,
                  never candidates): L0 = harness.load(tf, "L0"); L2x1 / L2x2 = symmetric triple barrier built from bars.parquet
                  (labels.py: lower barrier = the Foundation stop `sl`, upper = entry + 1x / 2x the stop distance, vertical = the
                  entry session's 15:25 bar (build.py eod_bar) capped at the contract's last candle; first touch with the engine's
                  same-bar conventions: stop before target on the same bar, a fill at the bar's open when it opens beyond the level,
                  else at the level, a session's first candle fills at its close; priced as build.py price()); L3 = trend scanning
                  (OLS slope t-value of close over bars k+1..k+h, h = 5..60, same session; net_L3 = dir_sign x t at the horizon of
                  max |t|, exit bar = k + h*; a row with fewer than 5 same-session bars after k has weight 0). A robustness gate is
                  trained on its label's table (splits purged by that label's exit bar) and scored on the same table AND on L1 (the
                  book ST13/ST14 trade) when the rows coincide (L2/L3); L0 is scored on L0 (its row set differs: the SETUPs at or
                  after 15:25).
Weights           one scheme: |net| winsorised at the TRAINING fold's 99th percentile, times class balance (equal total weight per
                  class), normalised to mean 1. Sensitivity only (12-block OOF, no CPCV): the AFML time-decay c = 0.5 variant
                  (oldest training row x 0.5 .. newest x 1, linear in time rank), because the pre-registered break tests found no
                  break inside IS. The regressor (c) is fit on net winsorised at the training fold's 1st / 99th percentile with
                  uniform weights.
Splits            harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo) for the OOF tables;
                  harness.cpcv_splits -> cpcv_paths -> score_paths (66 splits, 11 paths, controls ON) for every learner; every
                  threshold is chosen INSIDE the training fold.
tau (nested)      for a probability learner: the p_win threshold on the coarse grid {0.10, 0.15, ..., 0.40} maximising the kept mean
                  net of the training fold's out-of-fold predictions (an inner 4-fold purged CV over the training blocks; the
                  bagging uses its out-of-bag probabilities instead) subject to |net|-weighted winner recall >= 0.90; when no grid
                  value satisfies the constraint the grid floor 0.10 is used (the importance study's rule). For the regressor (c):
                  tau_r on {-1500, -1250, ..., 0, 250} INR with the same rule. For the scorecard (e): the integer score is mapped to
                  p_win by a 1-D logistic (Platt) fit on the inner-CV scores, and tau is applied to that p_win (s = the equivalent
                  score threshold). Every tau of the grid is also scored as a pooled fixed-tau OOF gate: one ledger row per tau
                  (family gate_family/<sub>/<model>/tau, controls off: they are trials for PBO / SPA, never candidates).
Models            (a) BaggingClassifier(DecisionTreeClassifier(max_depth 4 (3 and 5 as a sensitivity), min_weight_fraction_leaf 0.05,
                      class_weight balanced), 300 trees, bootstrap, max_samples = the label's average uniqueness, oob_score) on
                      the training-fold-median-imputed matrix;
                  (b) HistGradientBoostingClassifier(max_depth 3, max_iter 200, learning_rate 0.05, l2_regularization 1.0,
                      early_stopping off, class balance via the weights, interaction_cst = the importance study's clusters plus
                      the top-5 interaction pairs (h5_full) / one group (context), monotonic_cst = -1 on n_choch_since_bos,
                      n_choch_since_bos_today, alt_dir6 (H2: more CHoCH churn = sideways = worse; the only hypothesis with a
                      stated direction); the unconstrained variant is a sensitivity row);
                  (c) HistGradientBoostingRegressor (same shape) on winsorised net, take iff E[net | x] > tau_r;
                  (d) value-maximising policy trees (Zhou-Athey-Wager form, two actions: take = net, skip = 0): exact depth 1,
                      greedy depth 2 / 3; split candidates = every feature x 30 training-fold quantile thresholds (0.5 for binary
                      columns); split criterion = the sum of winsorised (1 / 99) net over each child's take decision
                      (child value = max(0, sum)); min leaf 100 rows (1m) / 40 (5m); a leaf takes iff its sum > 0; NaN rows fall
                      out of every condition (the rule grammar: NaN never satisfies a comparison) and are taken by default;
                  (e) the binned logistic scorecard: 5 quantile bins per numeric feature (training-fold edges; NaN = no bin, 0
                      points), binary / one-hot columns as indicators; L1 LogisticRegression (liblinear) with the study weights;
                      C lowered on a geometric path until at most 12 (1m) / 6 (5m) source features carry a non-zero coefficient;
                      coefficients rounded to integer points on a 20-point scale; skip if score < s (s from tau via the Platt map);
                  H5 (sub-family II only, as pre-registered): dt3 = DecisionTreeClassifier(max_depth 3, min_samples_leaf 100 / 40)
                      with the study weights and the nested tau; h5rules = the greedy rule-list search (<= 8 conjunctive rules of
                      depth <= 3, thresholds at 30 quantile grid points, greedy by kept expectancy on the TRAINING fold, a rule
                      is extended to depth 2 / 3 while that improves the kept mean, the search stops when the marginal training
                      gain < 200 INR/trade or a leaf would fall under the min-leaf floor).
Distillation      to each probability / value learner's OOF DECISION (p_win >= tau, never the label): a depth-3
                  DecisionTreeClassifier (min leaf 100 / 40) and a greedy rule list (<= 8 rules, depth <= 3, greedy by
                  covered-skip minus covered-take over the still-uncovered rows, thresholds at the quantile grid). Nested form
                  (honest): inside every split the rule list is fit to the learner's inner-CV decisions on the training rows and
                  applied to the test rows (its own 12-block OOF and CPCV are ledger rows). Frozen form: the rule list fit to the
                  pooled 12-block OOF decisions over all IS rows (a selection on pooled OOF: one ledger row, family
                  gate_family/<sub>/<model>/frozen_rules). Fidelity = agreement with the learner's decisions; skip precision /
                  recall reported. The policy trees, dt3 and h5rules are rule lists already (fidelity 1 by construction).
Rule grammar      the LLM-round-0 grammar tapes.rule_mask evaluates: [{"if": [[column, op, value], ...] (<= 3), "then": "skip"}],
                  default take; a one-hot design column `src=level` becomes [src, "==", level] (present) / [src, "!=", level]
                  (absent, source not missing); a missing indicator `__na` and a `=nan` level are not expressible and are excluded
                  from every rule search; an ext-features column is expressible on the real tape (joined on setup_i) but not on
                  the null tapes (flagged). Every rule-list keep mask in this study is computed by tapes.rule_mask on the feature
                  frame (the shipped semantics), never by the tree that produced it.
Judgement         harness.score rows (kept-vs-skipped diff, control percentile, permutation p, loser recall / precision, |net|-weighted
                  winner recall, top-decile winners skipped, top-1%-removed diff (a hard pass), kept mean at 8 pts slippage, block
                  sign count, kept floors), the CPCV distribution (median, 5th percentile), harness.pbo("diff") / spa /
                  effective_trials over every gate_family ledger row of the timeframe with label L1, deflated_sharpe with n_trials =
                  the family size, bootstrap_ci; harness.go_no_go with every argument filled; the null-tape check
                  (tapes.null_tape_check) and the drift refit (drift.json top5_sources) for the finalist.
Why not RL        one-step decision per SETUP, the counterfactual (Foundation's own trade) is observed for every SETUP taken or not,
                  0 overlapping positions on L1 by construction: the take / skip choice is supervised meta-labelling / a
                  full-information contextual bandit whose off-policy value is exact (sum of pi(x) net(x)); no state carries over
                  from one decision to the next, so there is no return to bootstrap and nothing for a sequential learner to do.
```

Implementation notes that belong to the definitions: (i) bin thresholds = unweighted quantiles (sklearn < 1.7 behaviour); sample weights enter the loss only — sklearn 1.9's weighted bin mapper costs ~25 s per fit on this box (measured 1.8 s without weights / 27 s with / 22 s at 20 iterations) and changes only the bin edges; (ii) controls (2,000-draw session-matched random control, permutation p) are ON for every headline OOF row, every CPCV path, every distilled row and every frozen form, and OFF for the fixed-tau grid rows, the time-decay / structural sensitivity rows and the robustness-label rows (they are trials for PBO / SPA, never candidates; their per-session vectors are saved like every row's); (iii) the inner CV for the nested tau uses 4 contiguous groups of the training fold's blocks with the harness purge and embargo (`harness._purge`); the bagging uses its out-of-bag probabilities instead (the importance study's rule); (iv) the policy learners carry the DM-1 selection floor kept share >= 20% of the training rows inside their search (the value-maximising tree on a book whose expectancy is negative in every cell would otherwise skip everything: every leaf's sum is <= 0; the constrained optimum switches skip leaves to take in decreasing order of leaf mean until the floor is met, and the H5 rule list refuses a rule that would take the kept share under the floor); (v) the frozen rule list distilled from the pooled OOF decisions and the scorecard / policy learner refit on all IS are selections on pooled OOF and are counted as trials (one ledger row each); (vi) a rule list is evaluated everywhere with `tapes.rule_mask` on the feature frame (NaN never satisfies a comparison; a `__na` indicator or a `=nan` one-hot level is not expressible and is excluded from every rule / scorecard search), so what is scored is what would ship; ext-features columns are expressible on the real tape (joined on `setup_i`) but not on the null tapes, and a rule on one is flagged.

## 3. The ceiling this family is read against (importance study, not refit)

| tf | ledger id | model | OOF AUC | OOF weighted log-loss | gate kept share | diff | CPCV diff median / p5 / share > 0 | family PBO (diff) | SPA p |
|---|---|---|---|---|---|---|---|---|---|
| minute | `7359bf6294568ac8` | bagging 300 x depth-4 on 276 features, training-fold tau | 0.5935 | 0.74474 | 1.0000 | - | -18.66 / -114.95 / 0.455 | 0.0308 | 0.7240 |
| 5minute | `1a12e823ea7cf4c7` | bagging 300 x depth-4 on 238 features, training-fold tau | 0.4974 | 0.72748 | 0.9915 | 817.94 | 259.06 / -314.33 / 0.364 | 0.0267 | 0.0345 |

The ceiling model (the 276-feature bagging, OOF AUC 0.59 on 1 min, 0.50 on 5 min, an OOF gate that keeps every row at the training-fold tau, CPCV diff median -19 / +259 with 5th percentiles -115 / -314) bounds what any learned gate on this table can do: a model with all the information the table holds ranks winners barely above chance and its gate cannot separate kept from skipped across the paths. Every number of this study is read against it.

## 4. minute (L1: IS units 4452, mean -1,009.61 INR/trade, win rate 0.1559)

### Labels built here (robustness only; `results/labels_minute.json`)

| label | definition | IS mean | IS win rate / share positive | exits | check |
|---|---|---|---|---|---|
| L2x1 | triple barrier, upper = entry + 1 x stop distance | -1,038.40 INR | 0.3165 | {'stop': 2069, 'target': 2032, 'eod': 351} | the L2 stop leg reproduces 1348 of the 1508 L1 stop exits bar-for-bar and price-for-price (the rest are target-first by design); mismatches 0 |
| L2x2 | upper = entry + 2 x stop distance | -959.32 INR | 0.3194 | {'stop': 2555, 'target': 1267, 'eod': 630} | same stop leg |
| L3 | trend-scanning t at the max-|t| horizon, signed by dir | -0.1499 (t units) | 0.4971 | h* median 39.0 bars; units with < 5 same-session bars 0 | dimensionless: the `kept mean slip 8` column of an L3 row is meaningless and not read |

### minute / sub-family (I) context — inside the frozen vocabulary

not run

### minute / sub-family (II) h5_full — OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)

Feature matrix: base design 244 + ext 61 -> 276 after the importance study's drops -> **274** after dropping the time proxies ['sl', 'n_events_asof']. HGB interaction_cst: 38 importance clusters + 2 interaction pairs (pairs with a time proxy dropped: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl']]); monotonic_cst: {'n_choch_since_bos': -1, 'n_choch_since_bos_today': -1, 'alt_dir6': -1}. Interaction pairs of the shortlist file: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl'], ['room_ahead_dist_atr', 'room_behind_dist_atr'], ['card_vol_ratio', 'room_behind_dist_atr']] (pairs with a time proxy: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl']]; both rooms pairs are used as HGB interaction groups; the rule searches of this sub-family are H5 as pre-registered, i.e. over the whole table, outside the shortlist).

#### OOF (12 purged blocks, nested tau; controls on)

| model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | H5 DecisionTreeClassifier depth <= 3, min leaf 100, nested tau | `6eb8d4e138950e9a` | 4,096 | 0.9200 | -1,016.37 | -931.74 | **-84.63** | -242.61 | 0.5617 | 0.0 | 0.082 / 0.865 | 0.955 | 0.029 | 2 | -1,406.34 | 0.15 0.10 0.10 0.10 0.25 0.20 0.10 0.20 0.10 0.10 0.10 0.15 | 12 |
| h5rules | H5 greedy rule list by training kept expectancy (stop < 200 INR/trade) | `fb304f64598b7850` | 1,041 | 0.2338 | -930.99 | -1,033.60 | **102.61** | -3.13 | 0.2599 | 0.1 | 0.777 / 0.857 | 0.327 | 0.643 | 7 | -1,320.96 | - | - |

Reading: `-` in a kept-vs-skipped column = the gate skipped nothing (or kept nothing) in the pooled OOF, so the difference is undefined. A tau of 0.10 = the grid floor: no threshold on the grid kept >= 90% of the |net|-weighted winner net with a higher kept mean than keeping everything (the column 'tau constraint met' counts the folds where a grid value satisfied the recall constraint).

#### The fixed-tau grid (every tau tried = a trial; controls off)

| model | tau | OOF id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|
| dt3 | 0.1 | `49f989349a3b1cc2` | 0.9991 | -4,351.10 | -4,528.43 | 0 |
| dt3 | 0.15 | `ba374decf899d6fb` | 0.9654 | -212.22 | -395.84 | 0 |
| dt3 | 0.2 | `3ce288d778338667` | 0.8156 | 25.74 | -152.85 | 5 |
| dt3 | 0.25 | `17a711454154fa2c` | 0.7747 | 3.83 | -174.99 | 4 |
| dt3 | 0.3 | `1ab412d37e92ea8c` | 0.7536 | -48.51 | -173.51 | 4 |
| dt3 | 0.35 | `2ea39674e7fbc0ac` | 0.6905 | -14.34 | -126.33 | 3 |
| dt3 | 0.4 | `a746b5213bd3c1df` | 0.5135 | -14.77 | -155.45 | 6 |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| dt3 | learner | 11 | -50.77 | **-452.25** | -777.06 | 0.364 | 0.9382 | 5.0 / 1.0 | `af9669b3c17cb21f`, `740dddc38417d3a1`, `c75b5982d6d7c950` |
| h5rules | learner | 11 | -20.02 | **-98.24** | -106.65 | 0.364 | 0.2682 | 0.1 / 0.0 | `7bbdf3df8611628d`, `ff5ccbb5f3ef322f`, `cb7f3e23d48fb7b5` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | tree refit on all IS | - | - | - | - | - | - | by construction | 0 | `befd646cea1b2866` | 1.0000 | - | - | - | (empty: take everything) |
| h5rules | policy refit on all IS | - | - | - | - | - | - | by construction | 1 | `d6038024f7398392` | 0.2520 | 417.74 | 0.0 | - | last_closed_net_asof > -2783.156129 AND win_range_slope > -0.025986 AND bocpd_rng_h60_map <= 222.419355 |

#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)

| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | L0 | 4,502 | 1.000 | 0.20 0.15 0.10 0.20 0.10 0.15 0.20 0.20 0.20 0.10 0.10 0.10 | `996006bdd8e9353e` | 0.9904 | -140.75 | -525.24 | 1 | 0.995 | n/a (other rows) | - | - | - | - |
| dt3 | L2x1 | 4,452 | 0.741 | 0.30 0.30 0.30 0.30 0.35 0.40 0.35 0.35 0.35 0.35 0.35 0.35 | `7810fcd01ee1e874` | 0.4425 | 134.34 | -54.11 | 9 | 0.936 | `127fc05e2bfd2073` | 0.4425 | 68.00 | -145.52 | 5 |
| dt3 | L2x2 | 4,452 | 0.620 | 0.20 0.20 0.10 0.10 0.15 0.30 0.10 0.20 0.20 0.30 0.20 0.30 | `53f62da56ba102ce` | 0.8347 | 102.24 | -41.85 | 11 | 0.976 | `0f231445b4a70b00` | 0.8347 | 18.89 | -169.96 | 6 |
| dt3 | L3 | 4,452 | 0.622 | 0.10 0.35 0.10 0.35 0.40 0.30 0.30 0.30 0.35 0.10 0.30 0.10 | `a60282aff12a5a74` | 0.9742 | -0.23 | 0.52 | 2 | 0.972 | `808dea02513f1880` | 0.9742 | -721.30 | -363.49 | 2 |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| dt3 | time decay c = 0.5 | `32fdbf3942dbc4b0` | 0.8951 | 98.21 | -72.17 | 4 | 0.10 0.10 0.15 0.10 0.25 0.20 0.10 0.15 0.25 0.10 0.30 0.10 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | dt3 kept share | h5rules kept share |
|---|---|---|---|
| 09 | 369 | 0.970 | 0.561 |
| 10 | 592 | 0.932 | 0.299 |
| 11 | 677 | 0.913 | 0.186 |
| 12 | 740 | 0.893 | 0.141 |
| 13 | 764 | 0.911 | 0.156 |
| 14 | 808 | 0.910 | 0.150 |
| 15 | 258 | 0.930 | 0.136 |
| <09:25 | 189 | 1.000 | 0.757 |
| >=15:20 | 55 | 0.855 | 0.164 |
| **regime** | |  |  |
| choch<2_since_bos | 2,908 | 0.926 | 0.188 |
| choch>=2_since_bos | 1,544 | 0.909 | 0.320 |
| dir = down | 2,209 | 0.923 | 0.229 |
| dir = up | 2,243 | 0.917 | 0.238 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| dt3 | 0.5463 | 0.3949 | 0.1559 | 0.20427 | 0.13158 | -0.5524 | 0.2399 | [0.0,0.1): 4, 0.016, 0.500; [0.1,0.2): 817, 0.176, 0.125; [0.2,0.3): 276, 0.235, 0.145; [0.3,0.4): 1069, 0.356, 0.149; [0.4,0.5): 1278, 0.453, 0.143; [0.5,0.6): 616, 0.532, 0.200; [0.6,0.7): 233, 0.636, 0.228; [0.7,0.8): 159, 0.723, 0.201 |

#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)

SHAP not available: hgbc not run

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p and boot filled

| form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 (tree rules at the nested tau) | `6eb8d4e138950e9a` | 0.9200 | -84.63 | -242.61 | 0.0 | 2 | -452.25 | -50.77 | - | 0.9999 | [-231.87, 17.63] | 12 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |
| h5rules (rule list by construction) | `fb304f64598b7850` | 0.2338 | 102.61 | -3.13 | 0.1 | 7 | -98.24 | -20.02 | - | 1.0000 | [-101.81, 299.25] | 11 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **h5rules (rule list by construction)** — nested OOF `fb304f64598b7850`, CPCV p5 -98.24, go/no-go **FAIL** (11 items failed). Frozen form: `d6038024f7398392` kept share 0.2520, diff 417.74, control pct 0.0; features used: ['bocpd_rng_h60_map', 'last_closed_net_asof', 'win_range_slope'].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.2338 |
| kept_n>=300 | yes | 1041 |
| diff>0 | yes | 102.61 |
| diff_top1_removed>0 | no | -3.13 |
| kept_mean_slip8>0 | no | -1320.96 |
| sign_blocks>=8/12 | no | 7 |
| control_pct>=95 | no | 0.1 |
| cpcv_p5_diff>0 | no | -98.24 |
| pbo<=0.2 | no | 0.2353 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | no | 0.8545 |
| boot_ci_excludes_0 | no | [-101.81, 299.25] |
| null_tape:evaluated | no | not run |
| no_time_proxy_columns | no | columns not declared |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'days_to_expiry', 'gap_pts', 'sess_cumvol_ratio20s']); nothing to refit.

### minute family multiplicity (every `gate_family/*` ledger row of the timeframe)

| rows (all labels) | rows (L1) | vectors | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials | SR variance across the family |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 47 | 40 | 40 | **0.2353** | 0.2367 | 0.0013 | **0.8545** | 0.9195 | 73.33 (1.268) | 3 | 0.5000 | 1.64 | 0.005245 |

Rows by family: {'gate_family/h5_full/dt3': 1, 'gate_family/h5_full/dt3/cpcv': 11, 'gate_family/h5_full/dt3/decay': 1, 'gate_family/h5_full/dt3/frozen_rules': 1, 'gate_family/h5_full/dt3/frozen_tree': 1, 'gate_family/h5_full/dt3/robust': 7, 'gate_family/h5_full/dt3/tau': 7, 'gate_family/h5_full/h5rules': 1, 'gate_family/h5_full/h5rules/cpcv': 11, 'gate_family/h5_full/h5rules/frozen_rules': 1, 'gate_family/h5_full/h5rules/robust': 5}

### minute candidate: **none** (null result)

No rule-list or scorecard form of either sub-family passes `harness.go_no_go` with every argument filled AND the null-tape certificate. The near-miss table is the finalist-set table of each sub-family above; the finalists' items:

- h5_full / h5rules (rule list by construction): go/no-go FAIL (11 failed: diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns); null tapes not evaluable: quick dry run: null tapes not evaluated.

### minute compute log

| sub-family | model | stage | seconds | RSS MB |
|---|---|---|---|---|
| h5_full | dt3 | oof12 | 29.5 | 308.2 |
| h5_full | dt3 | cpcv | 145.9 | 309.9 |
| h5_full | dt3 | frozen | 2.3 | - |
| h5_full | dt3 | robust | 47.1 | - |
| h5_full | h5rules | oof12 | 29.6 | 404.8 |
| h5_full | h5rules | cpcv | 176.3 | 460.3 |
| h5_full | h5rules | frozen | 9.1 | - |

## 5. 5minute (L1: IS units 826, mean -757.05 INR/trade, win rate 0.2772)

### Labels built here (robustness only; `results/labels_5minute.json`)

| label | definition | IS mean | IS win rate / share positive | exits | check |
|---|---|---|---|---|---|
| L2x1 | triple barrier, upper = entry + 1 x stop distance | -1,067.52 INR | 0.4346 | {'stop': 358, 'target': 345, 'eod': 123} | the L2 stop leg reproduces 353 of the 415 L1 stop exits bar-for-bar and price-for-price (the rest are target-first by design); mismatches 0 |
| L2x2 | upper = entry + 2 x stop distance | -877.88 INR | 0.3620 | {'stop': 418, 'eod': 207, 'target': 201} | same stop leg |
| L3 | trend-scanning t at the max-|t| horizon, signed by dir | 0.1544 (t units) | 0.4952 | h* median 21.0 bars; units with < 5 same-session bars 39 | dimensionless: the `kept mean slip 8` column of an L3 row is meaningless and not read |

### 5minute / sub-family (I) context — inside the frozen vocabulary

#### OOF (12 purged blocks, nested tau; controls on)

| model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | (a) BaggingClassifier 300 x depth-4 trees | `2a247b7b7b53b5c4` | 819 | 0.9915 | -771.80 | 968.07 | **-1,739.87** | 1,208.27 | 0.2984 | 51.4 | 0.008 / 0.714 | 0.977 | 0.043 | 0 | -1,161.76 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.35 0.10 0.10 | 12 |
| hgbc | (b) HGB classifier, one interaction group (hour x dir), no monotone constraint | `1b7f25ee4704bca2` | 765 | 0.9262 | -827.91 | 131.57 | **-959.48** | -838.85 | 0.1129 | 2.5 | 0.070 / 0.689 | 0.919 | 0.130 | 5 | -1,217.88 | 0.15 0.10 0.15 0.30 0.15 0.10 0.15 0.15 0.30 0.30 0.15 0.15 | 12 |

Reading: `-` in a kept-vs-skipped column = the gate skipped nothing (or kept nothing) in the pooled OOF, so the difference is undefined. A tau of 0.10 = the grid floor: no threshold on the grid kept >= 90% of the |net|-weighted winner net with a higher kept mean than keeping everything (the column 'tau constraint met' counts the folds where a grid value satisfied the recall constraint).

#### The fixed-tau grid (every tau tried = a trial; controls off)

| model | tau | OOF id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|
| bag4 | 0.1 | `0338996a4cbf2c18` | 1.0000 | - | - | - |
| bag4 | 0.15 | `ede42c78e3300259` | 1.0000 | - | - | - |
| bag4 | 0.2 | `31a8c3615abf9f25` | 1.0000 | - | - | - |
| bag4 | 0.25 | `bab19f9f6aeb4864` | 1.0000 | - | - | - |
| bag4 | 0.3 | `283143deebbef8b7` | 1.0000 | - | - | - |
| bag4 | 0.35 | `98df121fdf17da8b` | 0.9734 | -1,575.75 | -866.12 | 0 |
| bag4 | 0.4 | `14d95cec9f1ea5bc` | 0.8995 | -1,140.59 | -1,116.33 | 5 |
| hgbc | 0.1 | `0dd6df4ddf56286d` | 0.9818 | -101.93 | -322.68 | 3 |
| hgbc | 0.15 | `798e71c3f5d9fd56` | 0.9455 | 352.01 | 122.93 | 9 |
| hgbc | 0.2 | `1acfa365838fcba3` | 0.9455 | 352.01 | 122.93 | 9 |
| hgbc | 0.25 | `f0ca7e166041783d` | 0.9455 | 352.01 | 122.93 | 9 |
| hgbc | 0.3 | `bf5bcd26e616e708` | 0.9044 | -597.22 | -552.73 | 7 |
| hgbc | 0.35 | `4d333bca485abbd2` | 0.8729 | -234.83 | -258.75 | 8 |
| hgbc | 0.4 | `78e94c68800cc823` | 0.7869 | -523.68 | -513.93 | 8 |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| bag4 | learner | 11 | -1,461.27 | **-3,446.53** | -3,958.69 | 0.091 | 0.9794 | 42.2 / 23.1 | `fa66afbb6d98b1b7`, `ce0359b18ce9a47a`, `212036b5bbf4d266` |
| bag4 | distilled rules (nested) | 11 | -1,240.46 | **-3,019.05** | -3,412.07 | 0.091 | 0.9806 | 46.2 / 27.6 | `09da355437d1783e`, `31df57def4da37e2`, `938f7b83369d7044` |
| bag4 | distilled tree (nested) | 11 | -1,461.27 | **-3,173.23** | -3,412.07 | 0.091 | 0.9794 | 46.5 / 28.9 | `ec1c31defb5d407c`, `b45a2e9475cdad05`, `5360c246de4150e0` |
| hgbc | learner | 11 | -549.70 | **-915.46** | -928.63 | 0.091 | 0.9286 | 0.0 / 0.0 | `5f7a0b5ecf2776b1`, `42ba4857a9ead3d9`, `166a1766b6481ecd` |
| hgbc | distilled rules (nested) | 11 | -1,196.40 | **-3,777.70** | -3,958.69 | 0.273 | 0.9867 | 15.3 / 2.2 | `0341c9e4b694076e`, `89b8fb299cc3123c`, `cba723621c6c42d4` |
| hgbc | distilled tree (nested) | 11 | -3,412.07 | **-6,373.71** | -6,930.53 | 0.182 | 0.9867 | 13.3 / 2.0 | `7652b34cf5008ae1`, `6df70742f30687cb`, `21e564e972bb1dad` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | rules | `e9bc055bff7405fc` | 0.9915 | -1,739.87 | 1,208.27 | 51.5 | 0 | 1.000 / 1.000 / 1.000 | 0.0 | `7c5b055bf54ec853` | 1.0000 | - | - | 0.992 |  |
| bag4 | tree | `a9e09e9c126efee7` | 0.9915 | -1,739.87 | 1,208.27 | 49.9 | 0 | 1.000 / 1.000 / 1.000 | 0.0 | - | - | - | - | - | - |
| hgbc | rules | `d0995de69ff4f094` | 0.9479 | -1,467.28 | -1,213.24 | 6.2 | 4 | 0.978 / 1.000 / 0.705 | 1.0 | `0c3c8524a607387c` | 0.9455 | 352.01 | 0.0 | 0.961 | hour_bin == 15 |
| hgbc | tree | `07fcb847059f709f` | 0.9552 | -524.22 | -167.24 | 12.9 | 5 | 0.971 / 1.000 / 0.607 | 1.0 | - | - | - | - | - | - |

#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)

| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | L0 | 832 | 1.000 | 0.35 0.10 0.10 0.10 0.35 0.40 0.40 0.10 0.30 0.10 0.40 0.35 | `184e93eac1d8a30a` | 0.9135 | -1,252.44 | -1,277.91 | 0 | 0.897 | n/a (other rows) | - | - | - | - |
| bag4 | L2x1 | 826 | 0.954 | 0.35 0.10 0.35 0.10 0.35 0.35 0.35 0.35 0.10 0.10 0.35 0.35 | `5bf03e2376ccb33e` | 0.9613 | 350.26 | 253.13 | 6 | 0.968 | `07b5c104da164314` | 0.9613 | 331.84 | 106.47 | 6 |
| bag4 | L2x2 | 826 | 0.931 | 0.10 0.40 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `5cbd00a5e310f5ae` | 1.0000 | - | - | - | - | `ad2a888c808087ec` | 1.0000 | - | - | - |
| bag4 | L3 | 826 | 0.761 | 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `391397588ccced5c` | 0.9927 | -14.75 | -15.09 | 0 | 0.978 | `0d87a9526ec27290` | 0.9927 | -1,698.52 | -1,916.94 | 0 |
| hgbc | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `fc9025a14653239b` | 0.9928 | -3,284.75 | -4,067.65 | 0 | 0.988 | n/a (other rows) | - | - | - | - |
| hgbc | L2x1 | 826 | 0.954 | 0.30 0.25 0.35 0.15 0.15 0.15 0.10 0.15 0.15 0.30 0.30 0.30 | `686cc4c617cb0ac4` | 0.9576 | -398.87 | -496.72 | 2 | 0.970 | `3e726eb1f1d55c7d` | 0.9576 | -246.64 | -473.13 | 3 |
| hgbc | L2x2 | 826 | 0.931 | 0.15 0.15 0.20 0.20 0.20 0.20 0.20 0.20 0.15 0.15 0.20 0.15 | `79c8141a27b04c2e` | 0.9455 | 224.23 | 84.52 | 8 | 0.996 | `435a8e5266d70016` | 0.9455 | 352.01 | 122.93 | 9 |
| hgbc | L3 | 826 | 0.761 | 0.10 0.10 0.10 0.40 0.40 0.15 0.10 0.10 0.10 0.10 0.30 0.10 | `1140d1d2d184e0d1` | 0.9855 | -12.71 | -10.28 | 0 | 0.957 | `7f15c1463e8a9b53` | 0.9855 | -1,937.31 | -2,157.53 | 0 |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| bag4 | time decay c = 0.5 | `150cdcb63ae63acf` | 0.9843 | -1,583.14 | -193.24 | 1 | 0.40 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.10 0.35 0.10 0.10 |
| bag4 | bag3 | `981e363680e8349a` | 0.9867 | -1,015.59 | -1,235.37 | 1 | 0.10 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.35 0.10 0.10 0.10 |
| bag4 | bag5 | `58fd5e8db9cbdc19` | 0.9915 | -1,739.87 | 1,208.27 | 0 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.35 0.10 0.10 |
| hgbc | time decay c = 0.5 | `2b35a23b5c097597` | 0.9358 | -1,056.75 | -885.37 | 5 | 0.15 0.10 0.15 0.35 0.10 0.10 0.15 0.15 0.30 0.30 0.15 0.15 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | bag4 kept share | hgbc kept share |
|---|---|---|---|
| 09 | 96 | 1.000 | 1.000 |
| 10 | 123 | 0.943 | 0.943 |
| 11 | 100 | 1.000 | 0.890 |
| 12 | 126 | 1.000 | 0.952 |
| 13 | 149 | 1.000 | 1.000 |
| 14 | 132 | 1.000 | 1.000 |
| 15 | 45 | 1.000 | 0.178 |
| <09:25 | 50 | 1.000 | 1.000 |
| >=15:20 | 5 | 1.000 | 1.000 |
| **regime** | |  |  |
| choch<2_since_bos | 567 | 0.989 | 0.926 |
| choch>=2_since_bos | 259 | 0.996 | 0.927 |
| dir = down | 400 | 1.000 | 0.922 |
| dir = up | 426 | 0.984 | 0.930 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| bag4 | 0.5097 | 0.4646 | 0.2772 | 0.23931 | 0.20038 | -0.1943 | 0.1888 | [0.3,0.4): 83, 0.366, 0.373; [0.4,0.5): 523, 0.447, 0.258; [0.5,0.6): 207, 0.538, 0.299; [0.6,0.7): 13, 0.616, 0.077 |
| hgbc | 0.5136 | 0.4494 | 0.2772 | 0.23959 | 0.20038 | -0.1957 | 0.1922 | [0.0,0.1): 15, 0.091, 0.267; [0.1,0.2): 30, 0.113, 0.100; [0.2,0.3): 34, 0.276, 0.441; [0.3,0.4): 97, 0.364, 0.237; [0.4,0.5): 360, 0.455, 0.281; [0.5,0.6): 269, 0.538, 0.297; [0.6,0.7): 21, 0.625, 0.143 |

#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)

| rank | feature | mean abs SHAP (log-odds, OOF rows, 12 fold models) |
|---|---|---|
| 1 | `hour_bin=15` | 0.20578 |
| 2 | `dir=down` | 0.11215 |
| 3 | `hour_bin=11` | 0.06397 |
| 4 | `hour_bin=<09:25` | 0.05298 |
| 5 | `hour_bin=14` | 0.04629 |
| 6 | `hour_bin=13` | 0.04388 |
| 7 | `hour_bin=10` | 0.03675 |
| 8 | `hour_bin=12` | 0.02839 |
| 9 | `hour_bin=09` | 0.01778 |
| 10 | `hour_bin=>=15:20` | 0.00000 |

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p and boot filled

| form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 -> distilled rules | `e9bc055bff7405fc` | 0.9915 | -1,739.87 | 1,208.27 | 51.5 | 0 | -3,019.05 | -1,240.46 | 1.000 | 0.6323 | [-6838.65, 3943.34] | 11 / 14 | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |
| bag4 -> distilled tree | `a9e09e9c126efee7` | 0.9915 | -1,739.87 | 1,208.27 | 49.9 | 0 | -3,173.23 | -1,461.27 | 1.000 | 0.6323 | [-6363.56, 3855.08] | 11 / 14 | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |
| hgbc -> distilled rules | `d0995de69ff4f094` | 0.9479 | -1,467.28 | -1,213.24 | 6.2 | 4 | -3,777.70 | -1,196.40 | 0.978 | 0.8248 | [-2684.74, -79.19] | 12 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |
| hgbc -> distilled tree | `07fcb847059f709f` | 0.9552 | -524.22 | -167.24 | 12.9 | 5 | -6,373.71 | -3,412.07 | 0.971 | 0.7095 | [-1771.28, 614.12] | 12 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **bag4 -> distilled rules** — nested OOF `e9bc055bff7405fc`, CPCV p5 -3,019.05, go/no-go **FAIL** (11 items failed). Frozen form: `7c5b055bf54ec853` kept share 1.0000, diff -, control pct -; features used: [].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.9915 |
| kept_n>=80 | yes | 819 |
| diff>0 | no | -1739.87 |
| diff_top1_removed>0 | yes | 1208.27 |
| kept_mean_slip8>0 | no | -1161.76 |
| sign_blocks>=8/12 | no | 0 |
| control_pct>=95 | no | 51.5 |
| cpcv_p5_diff>0 | no | -3019.05 |
| pbo<=0.2 | no | 0.606 |
| dsr_p<0.1 | no | 0.6323 |
| spa_p<=0.10 | no | 0.4535 |
| boot_ci_excludes_0 | no | [-6838.65, 3943.34] |
| null_tape:evaluated | no | not run |
| no_time_proxy_columns | no | columns not declared |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'hv3_ratio', 'n_rooms_alive', 'range_3h_pts']); nothing to refit.

### 5minute / sub-family (II) h5_full — OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)

not run

### 5minute family multiplicity (every `gate_family/*` ledger row of the timeframe)

| rows (all labels) | rows (L1) | vectors | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials | SR variance across the family |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 106 | 98 | 98 | **0.6060** | 0.8056 | 0.3570 | **0.4535** | 0.5625 | 27.65 (1.344) | 62 | 0.6660 | 1.06 | 0.000181 |

Rows by family: {'gate_family/context/bag4': 1, 'gate_family/context/bag4/cpcv': 11, 'gate_family/context/bag4/decay': 1, 'gate_family/context/bag4/distill_rules': 1, 'gate_family/context/bag4/distill_rules/cpcv': 11, 'gate_family/context/bag4/distill_tree': 1, 'gate_family/context/bag4/distill_tree/cpcv': 11, 'gate_family/context/bag4/frozen_rules': 1, 'gate_family/context/bag4/robust': 7, 'gate_family/context/bag4/sens': 2, 'gate_family/context/bag4/tau': 7, 'gate_family/context/hgbc': 1, 'gate_family/context/hgbc/cpcv': 11, 'gate_family/context/hgbc/decay': 1, 'gate_family/context/hgbc/distill_rules': 1, 'gate_family/context/hgbc/distill_rules/cpcv': 11, 'gate_family/context/hgbc/distill_tree': 1, 'gate_family/context/hgbc/distill_tree/cpcv': 11, 'gate_family/context/hgbc/frozen_rules': 1, 'gate_family/context/hgbc/robust': 7, 'gate_family/context/hgbc/tau': 7}

### 5minute candidate: **none** (null result)

No rule-list or scorecard form of either sub-family passes `harness.go_no_go` with every argument filled AND the null-tape certificate. The near-miss table is the finalist-set table of each sub-family above; the finalists' items:

- context / bag4 -> distilled rules: go/no-go FAIL (11 failed: diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated, no_time_proxy_columns); null tapes not evaluable: quick dry run: null tapes not evaluated.

### 5minute compute log

| sub-family | model | stage | seconds | RSS MB |
|---|---|---|---|---|
| context | bag4 | oof12 | 59.4 | 290.4 |
| context | bag4 | cpcv | 156.8 | 291.1 |
| context | bag4 | frozen | 0.0 | - |
| context | bag4 | robust | 54.0 | - |
| context | hgbc | oof12 | 34.7 | 393.0 |
| context | hgbc | cpcv | 159.4 | 392.9 |
| context | hgbc | frozen | 1.9 | - |
| context | hgbc | robust | 40.6 | - |

## 6. Why sequential reinforcement learning is not used here

The decision is one step per SETUP: take or skip at the SETUP bar. Foundation took every SETUP, so the reward of `take` (the L1 net) is observed for every context and the reward of `skip` is 0 by definition: the counterfactual is in the table, no arm is unobserved, no propensity model, no inverse-propensity weighting and no doubly-robust correction is needed (Dudik-Langford-Li's estimator collapses to the direct method), and the off-policy value of any gate is exact: sum over SETUPs of pi(x) x net(x). On L1 no two positions overlap by construction (average uniqueness 1.0 on the IS rows, logged in `run_<tf>_<sub>.log`), the next SETUP needs the CHoCH that exits the previous trade, and the 15:25 cut ends every position inside its session, so no state carries from one decision to the next: there is no return to bootstrap, no credit assignment across decisions and nothing a sequential learner (Q-learning, policy gradient, FQI) could exploit that supervised meta-labelling / a full-information contextual bandit does not already compute exactly. Sequential RL is justified only where today's action changes which future rewards remain reachable (the in-trade exit, studied in `exit_policy` as an Exo-MDP with FQI: no exit variant rescued the book; and the session-level stop, studied in `session_stop`: null). The 'generative' element the canon endorses at this sample size is the CPCV path distribution and the stationary block bootstrap of sessions (the harness), and the null tapes of `null_tapes_drift`.

## 7. What would falsify these findings

- A rule-list or scorecard form with a nested CPCV 5th percentile > 0, PBO <= 0.2 over the family, DSR p < 0.1 with n_trials = the family size, SPA p <= 0.10, a bootstrap 90% CI of the diff above 0, kept share >= 20%, kept n >= 300 / 80, diff > 0 with the top 1% winners removed, kept mean > 0 at 8 pts slippage, diff > 0 in >= 8 of 12 blocks, control percentile >= 95, AND a real-tape diff above the GMM-Markov and segment-bootstrap p95 of its own null tapes: the finalist-set tables show which items fail for every form.
- A ceiling model with an OOF AUC materially above 0.59 (1 min) / 0.50 (5 min) on this table: the importance study's bagging and this study's HGB (b) are the two gradient / bagged ceilings and both sit there.
- A tau grid on which the nested recall constraint (|net|-weighted winner recall >= 0.90) is met by a threshold above the floor in most folds: the 'tau constraint met' column shows how often the constraint bound at the floor.

## 8. Caveats

- The shortlist is empty on both timeframes; sub-family (II) is H5 on the whole as-of table and is OUTSIDE THE FROZEN SHORTLIST in every row; its multiplicity is counted in the same family as (I).
- Every HGB fit bins with unweighted quantiles (sklearn < 1.7 behaviour) because sklearn 1.9's weighted bin mapper costs ~25 s per fit; the study weights enter the loss unchanged.
- The fixed-tau, time-decay, structural-sensitivity and robustness-label rows are scored with controls off (they are trials, never candidates); their vectors are in the family for PBO / SPA.
- The frozen rule list distilled from the pooled OOF decisions and the scorecard / policy learner refit on all IS are in-sample selections (one trial each); the candidate rule judges the NESTED forms (their own OOF row and CPCV distribution), as both judges asked.
- The policy learners carry the DM-1 kept-share floor (>= 20% of the training rows) inside the search: without it the value-maximising tree skips every SETUP because the book's expectancy is negative in every hour x direction cell.
- A rule on an ext-features column (features_ext) is expressible on the real tape but cannot be replayed on the null tapes (their feature tables carry the 261 base columns): the null-tape item then reads 'not evaluable' and the form cannot be a candidate.
- `sl` and `n_events_asof` (drift.json time proxies) are excluded from sub-family (II); the interaction pairs that carry them are unusable and are listed.
- Two processes appended to the ledger concurrently (procA: 5minute context / 5minute h5_full / minute context; procB: minute h5_full); every line was parsed back by finalize (ids unique per config).
- The L3 label is dimensionless (a t-value); its rows' slippage column is not read; the L2 labels use the engine's same-bar conventions and are checked against the L1 stop exits.
- IS/OOS: no OOS row was read; the OOS window is the published lab window (BRIEF caveat).

## 9. Files

- `finalize.log`
- `finalize.py`
- `gf_lib.py`
- `labels.py`
- `labels_5minute.log`
- `labels_minute.log`
- `procA.nohup`
- `procB.nohup`
- `results`
- `run_5minute_context.log`
- `run_gf.py`
- `run_minute_h5_full.log`
- `results/labels_5minute.json`
- `results/labels_5minute.parquet`
- `results/labels_minute.json`
- `results/labels_minute.parquet`
- `results/minute/h5_full/dt3.json`
- `results/minute/h5_full/dt3.pkl`
- `results/minute/h5_full/features.json`
- `results/minute/h5_full/h5rules.pkl`
- `results/5minute/context/bag4.json`
- `results/5minute/context/bag4.pkl`
- `results/5minute/context/features.json`
- `results/5minute/context/hgbc.json`
- `results/5minute/context/hgbc.pkl`
