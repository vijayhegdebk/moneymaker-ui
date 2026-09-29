# gate_family: FINDINGS (the ONE learned-gate trial family; DESIGN_PANEL quant-ml-canon-meta-label-gate merged with decision-making-1-fullinfo-bandit-policy-tree-gate and BRIEF H5; both judges' fixes binding)

Generated 2026-09-29T15:37:35 by `finalize.py` from `results/<tf>/<sub>/<model>.pkl`, the harness ledger and `results/labels_<tf>.json`. **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 intraday book) trains and judges; L0 / L2 / L3 are one robustness table (never candidates). Every number below is a harness ledger row (id given) or an output file of this folder; nothing is invented. Scripts: `labels.py`, `gf_lib.py`, `run_gf.py`, `finalize.py` (shas {'gf_lib.py': 'a063503fe27c74c3', 'run_gf.py': '1649d1af57952260', 'labels.py': '89883855c50a5a10', 'finalize.py': 'e054ead72f373fc7'}); logs `labels_<tf>.log`, `run_<tf>_<sub>.log`, `procA.nohup`, `procB.nohup`, `finalize.log`.

## 0. Result in one paragraph

**Null result on both timeframes: no candidate file is written.** **minute**: 272 ledger rows in the family (PBO(diff) 0.525, SPA p 0.907, effective trials 1.21); context finalist hgbc -> distilled tree CPCV p5 159.75, go/no-go FAIL (6 items); h5_full finalist scorecard -> distilled tree CPCV p5 -5.92, go/no-go FAIL (10 items); candidate: NONE. **5minute**: 532 ledger rows in the family (PBO(diff) 0.522, SPA p 0.057, effective trials 1.22); context finalist pt2 (rule list by construction) CPCV p5 -433.92, go/no-go FAIL (9 items); h5_full finalist scorecard -> distilled rules CPCV p5 53.58, go/no-go FAIL (9 items); candidate: NONE. Read against the ceiling (section 3): the full-information bagging ranks winners at AUC 0.59 / 0.50 and its gate keeps everything; the learned gates here, inside the frozen vocabulary (hour and direction) and outside it (the full table, H5 as pre-registered), move the kept-vs-skipped difference within the random band on the CPCV paths and fail the pre-registered pass rule. Sequential RL was not used: section 6.

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

#### OOF (12 purged blocks, nested tau; controls on)

| sub-family | model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (I) context, inside the frozen vocabulary | bag4 | (a) BaggingClassifier 300 x depth-4 trees | `a47fc3656fa5ee4d` | 3,987 | 0.8956 | -989.53 | -1,181.76 | **192.23** | 51.91 | 0.1304 | 47.2 | 0.110 / 0.888 | 0.943 | 0.057 | 10 | -1,379.49 | 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.30 0.35 0.30 | 12 |
| (I) context, inside the frozen vocabulary | hgbc | (b) HGB classifier, one interaction group (hour x dir), no monotone constraint | `3290c2619d4cae8f` | 3,782 | 0.8495 | -981.74 | -1,166.91 | **185.17** | -1.85 | 0.0840 | 11.9 | 0.158 / 0.888 | 0.932 | 0.071 | 11 | -1,371.71 | 0.35 0.30 0.30 0.30 0.30 0.30 0.30 0.35 0.35 0.35 0.35 0.35 | 12 |
| (I) context, inside the frozen vocabulary | hgbr | (c) HGB regressor E[net|x] > tau_r | `cd52214f7daee5ac` | 4,223 | 0.9486 | -997.02 | -1,241.73 | **244.71** | 114.83 | 0.1679 | 56.4 | 0.054 / 0.891 | 0.966 | 0.043 | 7 | -1,386.99 | -1,250.00 -1,500.00 -1,500.00 -1,500.00 -1,250.00 -1,250.00 -1,500.00 -1,250.00 -1,250.00 -1,250.00 -1,500.00 -1,250.00 | 12 |

Reading: `-` in a kept-vs-skipped column = the gate skipped nothing (or kept nothing) in the pooled OOF, so the difference is undefined. A tau of 0.10 = the grid floor: no threshold on the grid kept >= 90% of the |net|-weighted winner net with a higher kept mean than keeping everything (the column 'tau constraint met' counts the folds where a grid value satisfied the recall constraint).

#### The fixed-tau grid (every tau tried = a trial; controls off)

| model | tau | OOF id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|
| bag4 | 0.1 | `d612d8bcf8106e10` | 1.0000 | - | - | - |
| bag4 | 0.15 | `eb641a6118634fe1` | 1.0000 | - | - | - |
| bag4 | 0.2 | `c16ab7b6879aa7b4` | 1.0000 | - | - | - |
| bag4 | 0.25 | `664d46888aa9648c` | 1.0000 | - | - | - |
| bag4 | 0.3 | `c838c27a9b97aa5f` | 0.9724 | 178.30 | 99.24 | 2 |
| bag4 | 0.35 | `028a45c8a33aad94` | 0.8956 | 192.23 | 51.91 | 10 |
| bag4 | 0.4 | `1f3ca010f86b6ee7` | 0.6123 | 153.49 | 36.34 | 8 |
| hgbc | 0.1 | `328f4e1e81d3aee3` | 0.9876 | 64.16 | -115.20 | 9 |
| hgbc | 0.15 | `175b1421fbd4c5c6` | 0.9847 | 6.02 | -173.88 | 9 |
| hgbc | 0.2 | `2f6bec6c000c7292` | 0.9582 | 130.93 | -53.94 | 10 |
| hgbc | 0.25 | `6127846e60291608` | 0.9167 | 222.37 | 29.17 | 11 |
| hgbc | 0.3 | `d728a6111a5cd821` | 0.8711 | 218.57 | 39.81 | 11 |
| hgbc | 0.35 | `32e0e09ecb175262` | 0.7866 | 108.92 | -65.51 | 10 |
| hgbc | 0.4 | `d8b5b3a644b5e39d` | 0.6584 | 208.29 | 29.57 | 10 |
| hgbr | -1500.0 | `2c59fbd6700b9d30` | 1.0000 | - | - | - |
| hgbr | -1250.0 | `7055c317105abecb` | 0.9153 | 274.92 | 117.25 | 12 |
| hgbr | -1000.0 | `d4ce6750ff1db542` | 0.2969 | -16.29 | -111.78 | 5 |
| hgbr | -750.0 | `1f579546afe3379e` | 0.0281 | -1,224.50 | -1,042.57 | 1 |
| hgbr | -500.0 | `65e4913a9709e758` | 0.0020 | -2,057.79 | -1,880.34 | 0 |
| hgbr | -250.0 | `6b0f5e133a6ad8b3` | 0.0000 | - | - | - |
| hgbr | 0.0 | `c603ed5811602614` | 0.0000 | - | - | - |
| hgbr | 250.0 | `8133652345bbbf31` | 0.0000 | - | - | - |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| bag4 | learner | 11 | 203.11 | **135.86** | 124.71 | 1.000 | 0.8843 | 44.5 / 19.5 | `9102caac8e5384f9`, `4407d03f5ec86e7e`, `f8f6ab2f03af6fe0` |
| bag4 | distilled rules (nested) | 11 | 206.26 | **152.97** | 152.37 | 1.000 | 0.8913 | 47.0 / 22.4 | `597042d8ebb31da1`, `bdbc3bfa214c0993`, `f7fa6e3fa36a258c` |
| bag4 | distilled tree (nested) | 11 | 206.26 | **152.97** | 152.37 | 1.000 | 0.8913 | 47.2 / 21.9 | `b71c0571fc0360b4`, `a2225fd0ead3c148`, `b5e7c71a3ef7a8d2` |
| hgbc | learner | 11 | 167.98 | **130.89** | 128.77 | 1.000 | 0.8255 | 4.8 / 1.4 | `eef8c817b6df2734`, `2fb18ea25b3f05c2`, `393b0c7475b0c440` |
| hgbc | distilled rules (nested) | 11 | 184.81 | **131.65** | 129.30 | 1.000 | 0.8652 | 17.9 / 4.3 | `110f9fab93ca532a`, `fd1da59ece575666`, `4093a9031af2740c` |
| hgbc | distilled tree (nested) | 11 | 199.36 | **159.75** | 147.59 | 1.000 | 0.8695 | 22.2 / 7.5 | `4e13901cfe3b2036`, `e1e9ff1326bae0eb`, `ef392f2db3389d72` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | rules | `78097a5957985c81` | 0.8956 | 192.23 | 51.91 | 46.6 | 10 | 1.000 / 1.000 / 1.000 | 1.0 | `f4cda9399a97d95b` | 0.9263 | 326.05 | 86.2 | 0.969 | hour_bin == 11 AND dir == down |
| bag4 | tree | `0bdf6e7acdcaa71a` | 0.8956 | 192.23 | 51.91 | 47.8 | 10 | 1.000 / 1.000 / 1.000 | 1.0 | - | - | - | - | - | - |
| hgbc | rules | `928767d51d8c5cbd` | 0.8973 | 199.59 | 32.13 | 16.0 | 10 | 0.952 / 1.000 / 0.682 | 2.0 | `f773bc09dbf984b2` | 0.8969 | 288.86 | 56.4 | 0.953 | hour_bin == 15 AND dir == down; hour_bin == 11 AND dir == down |
| hgbc | tree | `d753e432605450f5` | 0.8875 | 189.88 | 17.86 | 21.9 | 9 | 0.962 / 1.000 / 0.748 | 2.0 | - | - | - | - | - | - |
| hgbr | rules | `0cf6289283799682` | 0.9917 | 125.67 | -52.94 | 38.3 | 1 | 0.957 / 1.000 / 0.162 | 0.0 | - | - | - | - | - | - |
| hgbr | tree | `3907f3c02154d00e` | 0.9358 | 178.54 | 78.84 | 32.7 | 6 | 0.987 / 0.801 / 1.000 | 1.0 | - | - | - | - | - | - |

#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)

| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | L0 | 4,502 | 1.000 | 0.35 0.35 0.35 0.35 0.35 0.35 0.40 0.10 0.35 0.35 0.40 0.40 | `18d338d24bc419c4` | 0.6753 | 285.32 | -125.54 | 8 | 0.850 | n/a (other rows) | - | - | - | - |
| bag4 | L2x1 | 4,452 | 0.741 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `92e38733cdd4f918` | 1.0000 | - | - | - | - | `1fbc1472c0383916` | 1.0000 | - | - | - |
| bag4 | L2x2 | 4,452 | 0.620 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `6520d619a0ca4a88` | 1.0000 | - | - | - | - | `d27f53346b04023a` | 1.0000 | - | - | - |
| bag4 | L3 | 4,452 | 0.622 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `22a27f0f32532bba` | 1.0000 | - | - | - | - | `8d55b27ba3542187` | 1.0000 | - | - | - |
| hgbc | L0 | 4,502 | 1.000 | 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.35 0.30 | `b6aa5bd8e0128d61` | 0.8818 | 271.52 | -114.42 | 11 | 0.954 | n/a (other rows) | - | - | - | - |
| hgbc | L2x1 | 4,452 | 0.741 | 0.30 0.25 0.30 0.30 0.25 0.30 0.30 0.25 0.30 0.30 0.25 0.25 | `ce3431b1b84a64f6` | 0.9582 | 66.47 | -20.24 | 6 | 0.991 | `59dc592f4eacd789` | 0.9582 | 130.93 | -53.94 | 10 |
| hgbc | L2x2 | 4,452 | 0.620 | 0.35 0.35 0.30 0.15 0.30 0.35 0.20 0.20 0.20 0.35 0.30 0.30 | `f489b5c792995712` | 0.9380 | 85.44 | -42.73 | 8 | 0.988 | `4c9753c65334f6db` | 0.9380 | 30.96 | -157.98 | 7 |
| hgbc | L3 | 4,452 | 0.622 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `01a72f88c48d0e90` | 1.0000 | - | - | - | - | `122ffb8faa38918f` | 1.0000 | - | - | - |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| bag4 | time decay c = 0.5 | `180ca8e6a8aef97b` | 0.8951 | 124.22 | 17.77 | 9 | 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.30 0.35 0.30 |
| bag4 | bag3 | `438779f7e7b766d9` | 0.9625 | 228.79 | 121.62 | 4 | 0.35 0.10 0.10 0.10 0.10 0.10 0.10 0.35 0.10 0.35 0.10 0.30 |
| bag4 | bag5 | `0b6aeb16616684b3` | 0.8077 | 209.44 | 45.59 | 9 | 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.30 0.30 0.35 0.35 |
| hgbc | time decay c = 0.5 | `9226f7aba02c4baf` | 0.8535 | 194.44 | 8.94 | 10 | 0.30 0.30 0.35 0.30 0.30 0.30 0.30 0.35 0.30 0.30 0.30 0.35 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | bag4 kept share | hgbc kept share | hgbr kept share |
|---|---|---|---|---|
| 09 | 369 | 1.000 | 1.000 | 1.000 |
| 10 | 592 | 1.000 | 1.000 | 1.000 |
| 11 | 677 | 0.515 | 0.515 | 0.734 |
| 12 | 740 | 0.815 | 0.845 | 0.934 |
| 13 | 764 | 1.000 | 1.000 | 1.000 |
| 14 | 808 | 1.000 | 1.000 | 1.000 |
| 15 | 258 | 1.000 | 0.333 | 1.000 |
| <09:25 | 189 | 1.000 | 1.000 | 1.000 |
| >=15:20 | 55 | 1.000 | 0.000 | 1.000 |
| **regime** | |  |  |  |
| choch<2_since_bos | 2,908 | 0.900 | 0.851 | 0.947 |
| choch>=2_since_bos | 1,544 | 0.888 | 0.847 | 0.952 |
| dir = down | 2,209 | 0.803 | 0.749 | 0.896 |
| dir = up | 2,243 | 0.986 | 0.948 | 1.000 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| bag4 | 0.5639 | 0.4212 | 0.1559 | 0.20278 | 0.13158 | -0.5411 | 0.2653 | [0.2,0.3): 123, 0.275, 0.122; [0.3,0.4): 1603, 0.364, 0.125; [0.4,0.5): 2210, 0.439, 0.165; [0.5,0.6): 393, 0.544, 0.237; [0.6,0.7): 123, 0.614, 0.171 |
| hgbc | 0.5598 | 0.4131 | 0.1559 | 0.20258 | 0.13158 | -0.5396 | 0.2572 | [0.0,0.1): 55, 0.010, 0.000; [0.1,0.2): 131, 0.165, 0.153; [0.2,0.3): 388, 0.255, 0.111; [0.3,0.4): 947, 0.356, 0.139; [0.4,0.5): 2474, 0.453, 0.163; [0.5,0.6): 369, 0.560, 0.225; [0.6,0.7): 88, 0.620, 0.148 |

#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)

| rank | feature | mean abs SHAP (log-odds, OOF rows, 12 fold models) |
|---|---|---|
| 1 | `hour_bin=11` | 0.12702 |
| 2 | `hour_bin=12` | 0.10970 |
| 3 | `hour_bin=>=15:20` | 0.10581 |
| 4 | `hour_bin=15` | 0.09977 |
| 5 | `dir=down` | 0.07937 |
| 6 | `hour_bin=<09:25` | 0.04851 |
| 7 | `hour_bin=09` | 0.04794 |
| 8 | `hour_bin=10` | 0.02103 |
| 9 | `hour_bin=13` | 0.01114 |
| 10 | `hour_bin=14` | 0.00118 |

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p, boot, columns and (for the finalist) the null-tape checks filled

| sub-family | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (I) context, inside the frozen vocabulary | bag4 -> distilled rules | `78097a5957985c81` | 0.8956 | 192.23 | 51.91 | 46.6 | 10 | 152.97 | 206.26 | 1.000 | 1.0000 | [68.14, 328.62] | 6 / 14 | kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | bag4 -> distilled tree | `0bdf6e7acdcaa71a` | 0.8956 | 192.23 | 51.91 | 47.8 | 10 | 152.97 | 206.26 | 1.000 | 1.0000 | [68.28, 328.94] | 6 / 14 | kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbc -> distilled rules | `928767d51d8c5cbd` | 0.8973 | 199.59 | 32.13 | 16.0 | 10 | 131.65 | 184.81 | 0.952 | 1.0000 | [80.68, 320.08] | 6 / 14 | kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbc -> distilled tree | `d753e432605450f5` | 0.8875 | 189.88 | 17.86 | 21.9 | 9 | 159.75 | 199.36 | 0.962 | 1.0000 | [70.2, 306.07] | 6 / 14 | kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbr -> distilled rules | `0cf6289283799682` | 0.9917 | 125.67 | -52.94 | 38.3 | 1 | - | - | 0.957 | 1.0000 | [-226.15, 390.81] | 9 / 13 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbr -> distilled tree | `3907f3c02154d00e` | 0.9358 | 178.54 | 78.84 | 32.7 | 6 | - | - | 0.987 | 1.0000 | [17.79, 344.07] | 7 / 13 | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **hgbc -> distilled tree** — nested OOF `d753e432605450f5`, CPCV p5 159.75, go/no-go **FAIL** (6 items failed). Frozen form: `-` kept share -, diff -, control pct -; features used: [].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.8875 |
| kept_n>=300 | yes | 3951 |
| diff>0 | yes | 189.88 |
| diff_top1_removed>0 | yes | 17.86 |
| kept_mean_slip8>0 | no | -1378.21 |
| sign_blocks>=8/12 | yes | 9 |
| control_pct>=95 | no | 21.9 |
| cpcv_p5_diff>0 | yes | 159.75 |
| pbo<=0.2 | no | 0.525 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | no | 0.9075 |
| boot_ci_excludes_0 | yes | [70.2, 306.07] |
| null_tape:evaluated | no | not evaluable: quick dry run: null tapes not evaluated |
| no_time_proxy_columns | yes | [] |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'days_to_expiry', 'gap_pts', 'sess_cumvol_ratio20s']); nothing to refit.

### minute / sub-family (II) h5_full — OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)

Feature matrix: base design 244 + ext 61 -> 276 after the importance study's drops -> **274** after dropping the time proxies ['sl', 'n_events_asof']. HGB interaction_cst: 38 importance clusters + 2 interaction pairs (pairs with a time proxy dropped: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl']]); monotonic_cst: {'n_choch_since_bos': -1, 'n_choch_since_bos_today': -1, 'alt_dir6': -1}. Interaction pairs of the shortlist file: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl'], ['room_ahead_dist_atr', 'room_behind_dist_atr'], ['card_vol_ratio', 'room_behind_dist_atr']] (pairs with a time proxy: [['sl', 'ffd_close_dstar'], ['sl', 'n_events_asof'], ['card_this_bars', 'sl']]; both rooms pairs are used as HGB interaction groups; the rule searches of this sub-family are H5 as pre-registered, i.e. over the whole table, outside the shortlist).

#### OOF (12 purged blocks, nested tau; controls on)

| sub-family | model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | dt3 | H5 DecisionTreeClassifier depth <= 3, min leaf 100, nested tau | `6eb8d4e138950e9a` | 4,096 | 0.9200 | -1,016.37 | -931.74 | **-84.63** | -242.61 | 0.5617 | 0.0 | 0.082 / 0.865 | 0.955 | 0.029 | 2 | -1,406.34 | 0.15 0.10 0.10 0.10 0.25 0.20 0.10 0.20 0.10 0.10 0.10 0.15 | 12 |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | h5rules | H5 greedy rule list by training kept expectancy (stop < 200 INR/trade) | `fb304f64598b7850` | 1,041 | 0.2338 | -930.99 | -1,033.60 | **102.61** | -3.13 | 0.2599 | 0.1 | 0.777 / 0.857 | 0.327 | 0.643 | 7 | -1,320.96 | - | - |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc | (b) HGB classifier, interaction_cst = clusters + pairs, monotone H2 columns | `ed555607c723ea4a` | 4,185 | 0.9400 | -1,006.66 | -1,055.85 | **49.20** | -93.45 | 0.7646 | 2.4 | 0.064 / 0.903 | 0.974 | 0.029 | 8 | -1,396.62 | 0.15 0.10 0.20 0.10 0.10 0.20 0.10 0.15 0.20 0.20 0.15 0.15 | 12 |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard | (e) scorecard, <= 12 source features by the L1 path | `a84520b8ab87f49e` | 4,261 | 0.9571 | -1,003.06 | -1,155.67 | **152.61** | -32.47 | 0.4353 | 37.4 | 0.047 / 0.921 | 0.981 | 0.029 | 4 | -1,393.03 | 0.30 0.30 0.30 0.35 0.25 0.30 0.10 0.35 0.30 0.30 0.35 0.35 | 12 |

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
| hgbc | 0.1 | `aa2c5ef10090d730` | 0.9870 | 176.57 | -2.89 | 8 |
| hgbc | 0.15 | `8f8fca415a5d94f5` | 0.9504 | 34.68 | -151.78 | 6 |
| hgbc | 0.2 | `e8af452f321ddac8` | 0.8735 | 35.13 | -114.29 | 6 |
| hgbc | 0.25 | `13ab658263f638d8` | 0.7466 | 93.40 | -25.09 | 10 |
| hgbc | 0.3 | `75200b8ea70e97cf` | 0.5901 | 60.63 | -86.77 | 8 |
| hgbc | 0.35 | `edc18a0d97c17daf` | 0.4272 | 40.98 | -54.08 | 6 |
| hgbc | 0.4 | `711813e105818172` | 0.2803 | 27.60 | -59.04 | 7 |
| scorecard | 0.1 | `879bbfbcb957786e` | 1.0000 | - | - | - |
| scorecard | 0.15 | `a119915459b56a7b` | 1.0000 | - | - | - |
| scorecard | 0.2 | `bf645d44f429a4b5` | 1.0000 | - | - | - |
| scorecard | 0.25 | `7daa3385c88b7d5c` | 0.9899 | 6.35 | -172.60 | 0 |
| scorecard | 0.3 | `b4327fddf2d63f33` | 0.9796 | 63.46 | -117.38 | 2 |
| scorecard | 0.35 | `b92136a3686afa6c` | 0.8178 | -19.30 | -118.98 | 4 |
| scorecard | 0.4 | `1ab6a19922d30c07` | 0.6222 | 68.56 | -118.97 | 7 |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| dt3 | learner | 11 | -50.77 | **-452.25** | -777.06 | 0.364 | 0.9382 | 5.0 / 1.0 | `af9669b3c17cb21f`, `740dddc38417d3a1`, `c75b5982d6d7c950` |
| h5rules | learner | 11 | -20.02 | **-98.24** | -106.65 | 0.364 | 0.2682 | 0.1 / 0.0 | `7bbdf3df8611628d`, `ff5ccbb5f3ef322f`, `cb7f3e23d48fb7b5` |
| hgbc | learner | 11 | 59.29 | **-56.56** | -102.23 | 0.818 | 0.9566 | 11.8 / 5.2 | `49f24b99ddfd04d4`, `0c9b83f7be6362e5`, `01f6e3cb742cfcfc` |
| hgbc | distilled rules (nested) | 11 | 27.83 | **-102.12** | -108.12 | 0.727 | 0.9681 | 11.1 / 5.2 | `35482bb9951c63c4`, `6adda2be98839cb7`, `b315b4e0cd344349` |
| hgbc | distilled tree (nested) | 11 | 43.83 | **-113.35** | -124.71 | 0.545 | 0.9677 | 9.7 / 3.9 | `08e37ef3903e8112`, `c3c03e3253158f91`, `69ddff43e8d0a7df` |
| scorecard | learner | 11 | 63.54 | **-14.58** | -39.95 | 0.909 | 0.8798 | 1.5 / 0.0 | `55be8dcd9c40f8b8`, `4ab237aa6966f086`, `70a7036cb8b6bd1e` |
| scorecard | distilled rules (nested) | 11 | 56.10 | **-24.96** | -52.59 | 0.909 | 0.8953 | 4.4 / 0.0 | `d93c9f9e5d8128b8`, `24cc5930030c1e23`, `4c50888862a0d537` |
| scorecard | distilled tree (nested) | 11 | 75.34 | **-5.92** | -23.01 | 0.909 | 0.8819 | 3.2 / 0.1 | `fed08ba43eb0c2c2`, `73b4ba1453daa303`, `99092ad6865bc751` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | tree refit on all IS | - | - | - | - | - | - | by construction | 0 | `befd646cea1b2866` | 1.0000 | - | - | - | (empty: take everything) |
| h5rules | policy refit on all IS | - | - | - | - | - | - | by construction | 1 | `d6038024f7398392` | 0.2520 | 417.74 | 0.0 | - | last_closed_net_asof > -2783.156129 AND win_range_slope > -0.025986 AND bocpd_rng_h60_map <= 222.419355 |
| hgbc | rules | `992945112fc07f5b` | 0.9769 | -132.31 | -313.71 | 2.8 | 2 | 0.940 / 0.505 / 0.195 | 0.0 | `905b2888192fedb7` | 1.0000 | - | - | 0.940 |  |
| hgbc | tree | `855b2d2f4462116b` | 0.9751 | -104.60 | -286.33 | 12.2 | 2 | 0.939 / 0.486 / 0.202 | 0.0 | - | - | - | - | - | - |
| scorecard | rules | `af93af8ebc3ae9f5` | 0.9937 | 130.08 | -48.16 | 63.0 | 2 | 0.960 / 0.750 / 0.110 | 0.0 | `4ecc5c62750ac629` | 1.0000 | - | - | 0.957 |  |
| scorecard | tree | `cbc8df04b485a517` | 0.9553 | 70.27 | -115.20 | 11.1 | 2 | 0.976 / 0.709 / 0.738 | 0.0 | - | - | - | - | - | - |
| scorecard | scorecard refit on all IS | - | - | - | - | - | - | 0.955 | 0 | `603b3e7e57bb46b0` | 0.9823 | 323.89 | 53.4 | - | last_bos_same_session: {'present': -5}; touch_prot_last=pending: {'present': -7}; card_cluster_sit: {'present': -20}; fz_level_in_band: {'present': -3}; session_bar: bins [78.0, 160.0, 233.0, 302.0] points {'0': 6}; hour: bins [10.0, 11.0, 13.0, 14.0] points {'2': -6}; n_swings_1h: bins [16.0, 18.0, 20.0, 22.0] points {'3': -1}; bocpd_ret_h60_p10: bins [0.057761, 0.083156, 0.112787, 0.196778] poin |

#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)

| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | L0 | 4,502 | 1.000 | 0.20 0.15 0.10 0.20 0.10 0.15 0.20 0.20 0.20 0.10 0.10 0.10 | `996006bdd8e9353e` | 0.9904 | -140.75 | -525.24 | 1 | 0.995 | n/a (other rows) | - | - | - | - |
| dt3 | L2x1 | 4,452 | 0.741 | 0.30 0.30 0.30 0.30 0.35 0.40 0.35 0.35 0.35 0.35 0.35 0.35 | `7810fcd01ee1e874` | 0.4425 | 134.34 | -54.11 | 9 | 0.936 | `127fc05e2bfd2073` | 0.4425 | 68.00 | -145.52 | 5 |
| dt3 | L2x2 | 4,452 | 0.620 | 0.20 0.20 0.10 0.10 0.15 0.30 0.10 0.20 0.20 0.30 0.20 0.30 | `53f62da56ba102ce` | 0.8347 | 102.24 | -41.85 | 11 | 0.976 | `0f231445b4a70b00` | 0.8347 | 18.89 | -169.96 | 6 |
| dt3 | L3 | 4,452 | 0.622 | 0.10 0.35 0.10 0.35 0.40 0.30 0.30 0.30 0.35 0.10 0.30 0.10 | `a60282aff12a5a74` | 0.9742 | -0.23 | 0.52 | 2 | 0.972 | `808dea02513f1880` | 0.9742 | -721.30 | -363.49 | 2 |
| h5rules | L0 | 4,502 | 1.000 | - | `136cd22e32aabac5` | 0.2541 | -114.55 | 67.16 | 5 | 0.231 | n/a (other rows) | - | - | - | - |
| h5rules | L2x1 | 4,452 | 0.741 | - | `4ae7d9814d164834` | 0.3333 | 1.61 | -203.77 | 5 | 0.593 | `57a77e99ad7d99d3` | 0.3333 | 4.62 | -124.11 | 4 |
| h5rules | L2x2 | 4,452 | 0.620 | - | `79c0a2d0fcdf95e9` | 0.2588 | 103.22 | -200.96 | 6 | 0.414 | `f9aac60b5006dd9d` | 0.2588 | 12.01 | -94.35 | 8 |
| h5rules | L3 | 4,452 | 0.622 | - | `4e3620624f3991b7` | 1.0000 | - | - | - | - | `06a85ec50b01c870` | 1.0000 | - | - | - |
| hgbc | L0 | 4,502 | 1.000 | 0.20 0.15 0.20 0.15 0.15 0.20 0.15 0.20 0.15 0.15 0.15 0.15 | `23c48aa1deebdc63` | 0.9329 | 349.00 | 63.36 | 8 | 0.967 | n/a (other rows) | - | - | - | - |
| hgbc | L2x1 | 4,452 | 0.741 | 0.30 0.35 0.30 0.30 0.30 0.30 0.25 0.35 0.30 0.35 0.35 0.30 | `4a154ac6ba7d54e2` | 0.4418 | 146.65 | -35.88 | 9 | 0.925 | `71a9eaf6901ede71` | 0.4418 | 144.41 | -83.59 | 10 |
| hgbc | L2x2 | 4,452 | 0.620 | 0.30 0.25 0.30 0.25 0.25 0.25 0.25 0.30 0.25 0.25 0.25 0.25 | `a9cf420fbbdfe2c3` | 0.7698 | 80.66 | -62.56 | 7 | 0.955 | `320823f1ae0cc02d` | 0.7698 | -49.70 | -215.05 | 4 |
| hgbc | L3 | 4,452 | 0.622 | 0.35 0.35 0.40 0.25 0.25 0.30 0.30 0.35 0.30 0.35 0.10 0.25 | `68beab665d43ad6a` | 0.9778 | -0.78 | -0.36 | 3 | 0.972 | `d55014d7f54b840a` | 0.9778 | -949.44 | 25.48 | 2 |
| scorecard | L0 | 4,502 | 1.000 | 0.10 0.10 0.40 0.10 0.10 0.40 0.10 0.40 0.10 0.40 0.10 0.10 | `f683b02e882755ce` | 0.9922 | 350.71 | -33.05 | 2 | 0.999 | n/a (other rows) | - | - | - | - |
| scorecard | L2x1 | 4,452 | 0.741 | 0.35 0.35 0.30 0.30 0.30 0.35 0.35 0.35 0.25 0.30 0.25 0.25 | `bf1084518fc1b1be` | 0.4528 | 135.73 | -48.34 | 9 | 0.924 | `b88fa4a6e73ba8a5` | 0.4528 | 135.65 | -103.14 | 9 |
| scorecard | L2x2 | 4,452 | 0.620 | 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 0.30 | `04fdf04f553cf385` | 0.7545 | 53.00 | -106.66 | 8 | 0.943 | `2ff908b97f65ba60` | 0.7545 | 22.72 | -131.02 | 6 |
| scorecard | L3 | 4,452 | 0.622 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `f5fe0519724630cd` | 1.0000 | - | - | - | - | `86a53d2eeed05711` | 1.0000 | - | - | - |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| dt3 | time decay c = 0.5 | `32fdbf3942dbc4b0` | 0.8951 | 98.21 | -72.17 | 4 | 0.10 0.10 0.15 0.10 0.25 0.20 0.10 0.15 0.25 0.10 0.30 0.10 |
| hgbc | time decay c = 0.5 | `4a8a074c495b58e7` | 0.9472 | -17.70 | -100.14 | 8 | 0.20 0.20 0.20 0.10 0.10 0.15 0.10 0.10 0.15 0.20 0.10 0.10 |
| hgbc | hgbc_nomono | `f77c1a0ac2a1d34c` | 0.9452 | 100.26 | -37.05 | 9 | 0.10 0.10 0.20 0.10 0.10 0.20 0.10 0.15 0.20 0.20 0.15 0.15 |
| scorecard | time decay c = 0.5 | `a47403af1a596c57` | 0.9551 | 88.66 | -96.84 | 1 | 0.30 0.30 0.30 0.35 0.25 0.30 0.30 0.10 0.30 0.35 0.35 0.35 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | dt3 kept share | h5rules kept share | hgbc kept share | scorecard kept share |
|---|---|---|---|---|---|
| 09 | 369 | 0.970 | 0.561 | 0.984 | 1.000 |
| 10 | 592 | 0.932 | 0.299 | 0.961 | 1.000 |
| 11 | 677 | 0.913 | 0.186 | 0.944 | 0.874 |
| 12 | 740 | 0.893 | 0.141 | 0.916 | 0.857 |
| 13 | 764 | 0.911 | 0.156 | 0.936 | 1.000 |
| 14 | 808 | 0.910 | 0.150 | 0.969 | 1.000 |
| 15 | 258 | 0.930 | 0.136 | 0.864 | 1.000 |
| <09:25 | 189 | 1.000 | 0.757 | 1.000 | 1.000 |
| >=15:20 | 55 | 0.855 | 0.164 | 0.473 | 1.000 |
| **regime** | |  |  |  |  |
| choch<2_since_bos | 2,908 | 0.926 | 0.188 | 0.940 | 0.962 |
| choch>=2_since_bos | 1,544 | 0.909 | 0.320 | 0.940 | 0.948 |
| dir = down | 2,209 | 0.923 | 0.229 | 0.947 | 0.959 |
| dir = up | 2,243 | 0.917 | 0.238 | 0.934 | 0.955 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| dt3 | 0.5463 | 0.3949 | 0.1559 | 0.20427 | 0.13158 | -0.5524 | 0.2399 | [0.0,0.1): 4, 0.016, 0.500; [0.1,0.2): 817, 0.176, 0.125; [0.2,0.3): 276, 0.235, 0.145; [0.3,0.4): 1069, 0.356, 0.149; [0.4,0.5): 1278, 0.453, 0.143; [0.5,0.6): 616, 0.532, 0.200; [0.6,0.7): 233, 0.636, 0.228; [0.7,0.8): 159, 0.723, 0.201 |
| hgbc | 0.5813 | 0.3377 | 0.1559 | 0.17059 | 0.13158 | -0.2964 | 0.1818 | [0.0,0.1): 58, 0.082, 0.052; [0.1,0.2): 505, 0.162, 0.107; [0.2,0.3): 1262, 0.253, 0.134; [0.3,0.4): 1379, 0.348, 0.158; [0.4,0.5): 779, 0.445, 0.177; [0.5,0.6): 329, 0.540, 0.225; [0.6,0.7): 109, 0.639, 0.275; [0.7,0.8): 30, 0.735, 0.267; [0.8,0.9): 1, 0.827, 0.000 |
| scorecard | 0.5782 | 0.4306 | 0.1559 | 0.20735 | 0.13158 | -0.5758 | 0.2747 | [0.2,0.3): 91, 0.267, 0.099; [0.3,0.4): 1591, 0.352, 0.116; [0.4,0.5): 1958, 0.456, 0.173; [0.5,0.6): 739, 0.533, 0.187; [0.6,0.7): 73, 0.619, 0.329 |

#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)

| rank | feature | mean abs SHAP (log-odds, OOF rows, 12 fold models) |
|---|---|---|
| 1 | `n_swings_1h` | 0.08167 |
| 2 | `session_bar` | 0.08024 |
| 3 | `atr_bps` | 0.07434 |
| 4 | `last_closed_net_asof` | 0.06899 |
| 5 | `fz_band_width` | 0.06661 |
| 6 | `bocpd_ret_h60_p10` | 0.06373 |
| 7 | `hv2_ratio` | 0.06016 |
| 8 | `bocpd_ret_h60_map` | 0.05723 |
| 9 | `bars_since_bos` | 0.05101 |
| 10 | `ffd_close_dstar` | 0.05052 |
| 11 | `room_behind_dist_atr` | 0.04905 |
| 12 | `range_since_choch_atr` | 0.04777 |
| 13 | `fz_band_width_atr` | 0.04751 |
| 14 | `bsadf_close_win` | 0.04550 |
| 15 | `p1_dist_prefix_short` | 0.04520 |
| 16 | `choch_bar_range_atr` | 0.04332 |
| 17 | `bar_range_pts` | 0.04312 |
| 18 | `win_range_slope` | 0.03872 |
| 19 | `move_since_choch_pts` | 0.03822 |
| 20 | `win_dd_extreme_atr` | 0.03719 |

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p, boot, columns and (for the finalist) the null-tape checks filled

| sub-family | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | dt3 (tree rules at the nested tau) | `6eb8d4e138950e9a` | 0.9200 | -84.63 | -242.61 | 0.0 | 2 | -452.25 | -50.77 | - | 1.0000 | [-231.87, 17.63] | 11 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | h5rules (rule list by construction) | `fb304f64598b7850` | 0.2338 | 102.61 | -3.13 | 0.1 | 7 | -98.24 | -20.02 | - | 1.0000 | [-101.81, 299.25] | 10 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc -> distilled rules | `992945112fc07f5b` | 0.9769 | -132.31 | -313.71 | 2.8 | 2 | -102.12 | 27.83 | 0.940 | 1.0000 | [-267.86, 33.49] | 11 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc -> distilled tree | `855b2d2f4462116b` | 0.9751 | -104.60 | -286.33 | 12.2 | 2 | -113.35 | 43.83 | 0.939 | 1.0000 | [-284.04, 103.26] | 11 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard -> distilled rules | `af93af8ebc3ae9f5` | 0.9937 | 130.08 | -48.16 | 63.0 | 2 | -24.96 | 56.10 | 0.960 | 1.0000 | [-137.8, 444.41] | 10 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard -> distilled tree | `cbc8df04b485a517` | 0.9553 | 70.27 | -115.20 | 11.1 | 2 | -5.92 | 75.34 | 0.976 | 1.0000 | [-60.68, 193.72] | 10 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard (scorecard) | `a84520b8ab87f49e` | 0.9571 | 152.61 | -32.47 | 37.4 | 4 | -14.58 | 63.54 | - | 1.0000 | [15.29, 281.3] | 9 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **scorecard -> distilled tree** — nested OOF `cbc8df04b485a517`, CPCV p5 -5.92, go/no-go **FAIL** (10 items failed). Frozen form: `-` kept share -, diff -, control pct -; features used: [].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.9553 |
| kept_n>=300 | yes | 4253 |
| diff>0 | yes | 70.27 |
| diff_top1_removed>0 | no | -115.2 |
| kept_mean_slip8>0 | no | -1396.43 |
| sign_blocks>=8/12 | no | 2 |
| control_pct>=95 | no | 11.1 |
| cpcv_p5_diff>0 | no | -5.92 |
| pbo<=0.2 | no | 0.525 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | no | 0.9075 |
| boot_ci_excludes_0 | no | [-60.68, 193.72] |
| null_tape:evaluated | no | not evaluable: quick dry run: null tapes not evaluated |
| no_time_proxy_columns | yes | [] |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'days_to_expiry', 'gap_pts', 'sess_cumvol_ratio20s']); nothing to refit.

### minute family multiplicity (every `gate_family/*` ledger row of the timeframe)

| rows (all labels) | rows (L1) | vectors | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials | SR variance across the family |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 272 | 248 | 248 | **0.5250** | 0.3874 | 0.0013 | **0.9075** | 0.9360 | 16.17 (2.297) | 29 | 0.6305 | 1.21 | 0.016355 |

Rows by family: {'gate_family/context/bag4': 1, 'gate_family/context/bag4/cpcv': 11, 'gate_family/context/bag4/decay': 1, 'gate_family/context/bag4/distill_rules': 1, 'gate_family/context/bag4/distill_rules/cpcv': 11, 'gate_family/context/bag4/distill_tree': 1, 'gate_family/context/bag4/distill_tree/cpcv': 11, 'gate_family/context/bag4/frozen_rules': 1, 'gate_family/context/bag4/robust': 7, 'gate_family/context/bag4/sens': 2, 'gate_family/context/bag4/tau': 7, 'gate_family/context/hgbc': 1, 'gate_family/context/hgbc/cpcv': 11, 'gate_family/context/hgbc/decay': 1, 'gate_family/context/hgbc/distill_rules': 1, 'gate_family/context/hgbc/distill_rules/cpcv': 11, 'gate_family/context/hgbc/distill_tree': 1, 'gate_family/context/hgbc/distill_tree/cpcv': 11, 'gate_family/context/hgbc/frozen_rules': 1, 'gate_family/context/hgbc/robust': 7, 'gate_family/context/hgbc/tau': 7, 'gate_family/context/hgbr': 1, 'gate_family/context/hgbr/distill_rules': 1, 'gate_family/context/hgbr/distill_tree': 1, 'gate_family/context/hgbr/tau': 8, 'gate_family/h5_full/dt3': 1, 'gate_family/h5_full/dt3/cpcv': 11, 'gate_family/h5_full/dt3/decay': 1, 'gate_family/h5_full/dt3/frozen_rules': 1, 'gate_family/h5_full/dt3/frozen_tree': 1, 'gate_family/h5_full/dt3/robust': 7, 'gate_family/h5_full/dt3/tau': 7, 'gate_family/h5_full/h5rules': 1, 'gate_family/h5_full/h5rules/cpcv': 11, 'gate_family/h5_full/h5rules/frozen_rules': 1, 'gate_family/h5_full/h5rules/robust': 7, 'gate_family/h5_full/hgbc': 1, 'gate_family/h5_full/hgbc/cpcv': 11, 'gate_family/h5_full/hgbc/decay': 1, 'gate_family/h5_full/hgbc/distill_rules': 1, 'gate_family/h5_full/hgbc/distill_rules/cpcv': 11, 'gate_family/h5_full/hgbc/distill_tree': 1, 'gate_family/h5_full/hgbc/distill_tree/cpcv': 11, 'gate_family/h5_full/hgbc/frozen_rules': 1, 'gate_family/h5_full/hgbc/robust': 7, 'gate_family/h5_full/hgbc/sens': 1, 'gate_family/h5_full/hgbc/tau': 7, 'gate_family/h5_full/scorecard': 1, 'gate_family/h5_full/scorecard/cpcv': 11, 'gate_family/h5_full/scorecard/decay': 1, 'gate_family/h5_full/scorecard/distill_rules': 1, 'gate_family/h5_full/scorecard/distill_rules/cpcv': 11, 'gate_family/h5_full/scorecard/distill_tree': 1, 'gate_family/h5_full/scorecard/distill_tree/cpcv': 11, 'gate_family/h5_full/scorecard/frozen_rules': 1, 'gate_family/h5_full/scorecard/frozen_scorecard': 1, 'gate_family/h5_full/scorecard/robust': 7, 'gate_family/h5_full/scorecard/tau': 7}

### minute candidate: **none** (null result)

No rule-list or scorecard form of either sub-family passes `harness.go_no_go` with every argument filled AND the null-tape certificate. The near-miss table is the finalist-set table of each sub-family above; the finalists' items:

- context / hgbc -> distilled tree: go/no-go FAIL (6 failed: kept_mean_slip8>0, control_pct>=95, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, null_tape:evaluated); null tapes not evaluable: quick dry run: null tapes not evaluated.
- h5_full / scorecard -> distilled tree: go/no-go FAIL (10 failed: diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, spa_p<=0.10, boot_ci_excludes_0, null_tape:evaluated); null tapes not evaluable: quick dry run: null tapes not evaluated.

### minute compute log

| sub-family | model | stage | seconds | RSS MB |
|---|---|---|---|---|
| context | bag4 | oof12 | 120.0 | 326.5 |
| context | bag4 | cpcv | 329.8 | 327.2 |
| context | bag4 | frozen | 6.7 | - |
| context | bag4 | robust | 126.5 | - |
| context | hgbc | oof12 | 195.6 | 460.6 |
| context | hgbc | cpcv | 461.3 | 472.4 |
| context | hgbc | frozen | 6.8 | - |
| context | hgbc | robust | 53.8 | - |
| context | hgbr | oof12 | 33.0 | 340.7 |
| h5_full | dt3 | oof12 | 29.5 | 308.2 |
| h5_full | dt3 | cpcv | 145.9 | 309.9 |
| h5_full | dt3 | frozen | 2.3 | - |
| h5_full | dt3 | robust | 47.1 | - |
| h5_full | h5rules | oof12 | 29.6 | 404.8 |
| h5_full | h5rules | cpcv | 176.3 | 460.3 |
| h5_full | h5rules | frozen | 9.1 | - |
| h5_full | h5rules | robust | 79.2 | - |
| h5_full | hgbc | oof12 | 234.3 | 590.4 |
| h5_full | hgbc | cpcv | 682.0 | 621.5 |
| h5_full | hgbc | frozen | 1.5 | - |
| h5_full | hgbc | robust | 242.0 | - |
| h5_full | scorecard | oof12 | 189.0 | 392.9 |
| h5_full | scorecard | cpcv | 685.1 | 420.6 |
| h5_full | scorecard | frozen | 15.1 | - |
| h5_full | scorecard | robust | 314.0 | - |
| h5_full | all | wall | 1207 | peak 458.1 MB |

## 5. 5minute (L1: IS units 826, mean -757.05 INR/trade, win rate 0.2772)

### Labels built here (robustness only; `results/labels_5minute.json`)

| label | definition | IS mean | IS win rate / share positive | exits | check |
|---|---|---|---|---|---|
| L2x1 | triple barrier, upper = entry + 1 x stop distance | -1,067.52 INR | 0.4346 | {'stop': 358, 'target': 345, 'eod': 123} | the L2 stop leg reproduces 353 of the 415 L1 stop exits bar-for-bar and price-for-price (the rest are target-first by design); mismatches 0 |
| L2x2 | upper = entry + 2 x stop distance | -877.88 INR | 0.3620 | {'stop': 418, 'eod': 207, 'target': 201} | same stop leg |
| L3 | trend-scanning t at the max-|t| horizon, signed by dir | 0.1544 (t units) | 0.4952 | h* median 21.0 bars; units with < 5 same-session bars 39 | dimensionless: the `kept mean slip 8` column of an L3 row is meaningless and not read |

### 5minute / sub-family (I) context — inside the frozen vocabulary

#### OOF (12 purged blocks, nested tau; controls on)

| sub-family | model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (I) context, inside the frozen vocabulary | bag4 | (a) BaggingClassifier 300 x depth-4 trees | `2a247b7b7b53b5c4` | 819 | 0.9915 | -771.80 | 968.07 | **-1,739.87** | 1,208.27 | 0.2984 | 51.4 | 0.008 / 0.714 | 0.977 | 0.043 | 0 | -1,161.76 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.35 0.10 0.10 | 12 |
| (I) context, inside the frozen vocabulary | hgbc | (b) HGB classifier, one interaction group (hour x dir), no monotone constraint | `1b7f25ee4704bca2` | 765 | 0.9262 | -827.91 | 131.57 | **-959.48** | -838.85 | 0.1129 | 2.5 | 0.070 / 0.689 | 0.919 | 0.130 | 5 | -1,217.88 | 0.15 0.10 0.15 0.30 0.15 0.10 0.15 0.15 0.30 0.30 0.15 0.15 | 12 |
| (I) context, inside the frozen vocabulary | hgbr | (c) HGB regressor E[net|x] > tau_r | `d20e8bc19d96ac6c` | 734 | 0.8886 | -885.18 | 265.17 | **-1,150.35** | -920.18 | 0.0160 | 95.8 | 0.101 / 0.652 | 0.823 | 0.261 | 7 | -1,275.14 | -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 | 1 |
| (I) context, inside the frozen vocabulary | pt1 | (d) exact depth-1 policy tree | `feb78729208ed323` | 794 | 0.9613 | -791.20 | 90.31 | **-881.52** | -1,107.42 | 0.2839 | 23.2 | 0.034 / 0.625 | 0.956 | 0.000 | 1 | -1,181.17 | - | - |
| (I) context, inside the frozen vocabulary | pt2 | (d) greedy depth-2 policy tree | `2aae111dbdd37a49` | 491 | 0.5944 | -699.21 | -841.83 | **142.62** | -26.24 | 0.6482 | 79.6 | 0.414 / 0.737 | 0.635 | 0.304 | 5 | -1,089.18 | - | - |
| (I) context, inside the frozen vocabulary | pt3 | (d) greedy depth-3 policy tree | `79038c5a5197c2b6` | 434 | 0.5254 | -860.88 | -642.11 | **-218.77** | -259.36 | 0.4783 | 14.9 | 0.474 / 0.722 | 0.530 | 0.435 | 5 | -1,250.84 | - | - |
| (I) context, inside the frozen vocabulary | scorecard | (e) hour-bin / dir scorecard (L1 logistic, integer points) | `a8c1cd3ea062d7dd` | 812 | 0.9831 | -755.92 | -822.49 | **66.56** | -153.88 | 0.9615 | 96.0 | 0.017 / 0.714 | 0.981 | 0.000 | 2 | -1,145.89 | 0.40 0.40 0.35 0.40 0.40 0.40 0.10 0.35 0.10 0.40 0.40 0.40 | 12 |
| (I) context, inside the frozen vocabulary | scorecard_linear | (e) hour-bin / dir scorecard (L1 logistic, integer points) | `7b7417541e9b90fc` | 791 | 0.9576 | -738.69 | -1,172.13 | **433.44** | 207.28 | 0.5737 | 88.0 | 0.047 / 0.800 | 0.980 | 0.000 | 1 | -1,128.65 | 0.10 0.40 0.10 0.40 0.40 0.10 0.40 0.35 0.10 0.10 0.10 0.40 | 12 |

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
| hgbr | -1500.0 | `35d039a81f26e242` | 0.8886 | -1,150.35 | -920.18 | 7 |
| hgbr | -1250.0 | `863e9dddaa6e85e3` | 0.8063 | 120.33 | 165.89 | 8 |
| hgbr | -1000.0 | `1954f2093370f356` | 0.6889 | -293.59 | -384.11 | 5 |
| hgbr | -750.0 | `978ce31377878d47` | 0.5073 | -188.32 | -225.20 | 5 |
| hgbr | -500.0 | `6a2248095d62fe92` | 0.2893 | -508.21 | -326.58 | 3 |
| hgbr | -250.0 | `03c8dfcf1a16b4ca` | 0.1501 | -1,308.29 | -1,055.39 | 2 |
| hgbr | 0.0 | `637f0bb7dca09c31` | 0.0521 | -2,478.63 | -2,251.42 | 1 |
| hgbr | 250.0 | `c6db8c4a0a77bc9d` | 0.0218 | -3,298.51 | -3,077.76 | 0 |
| scorecard | 0.1 | `ab2e382566d50a19` | 1.0000 | - | - | - |
| scorecard | 0.15 | `7e5fc7bacfa37100` | 1.0000 | - | - | - |
| scorecard | 0.2 | `1b51eab72695cf6e` | 1.0000 | - | - | - |
| scorecard | 0.25 | `9188ba25f61a1dce` | 1.0000 | - | - | - |
| scorecard | 0.3 | `8bedc798d0715768` | 1.0000 | - | - | - |
| scorecard | 0.35 | `e4af63da3274a901` | 0.9939 | -251.18 | -469.21 | 1 |
| scorecard | 0.4 | `2d80767f4f229b98` | 0.9818 | -31.58 | -252.32 | 2 |
| scorecard_linear | 0.1 | `eb85e1906523f5af` | 1.0000 | - | - | - |
| scorecard_linear | 0.15 | `5824945da703fcac` | 1.0000 | - | - | - |
| scorecard_linear | 0.2 | `890caa711e64585f` | 1.0000 | - | - | - |
| scorecard_linear | 0.25 | `336432fd15bb1e5a` | 1.0000 | - | - | - |
| scorecard_linear | 0.3 | `9a92fb45115c0484` | 0.9952 | -731.35 | -949.13 | 1 |
| scorecard_linear | 0.35 | `93a34555d5bc541b` | 0.9939 | -251.18 | -469.21 | 1 |
| scorecard_linear | 0.4 | `b589f23f3b9293d0` | 0.9576 | 433.44 | 207.28 | 1 |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| bag4 | learner | 11 | -1,461.27 | **-3,446.53** | -3,958.69 | 0.091 | 0.9794 | 42.2 / 23.1 | `fa66afbb6d98b1b7`, `ce0359b18ce9a47a`, `212036b5bbf4d266` |
| bag4 | distilled rules (nested) | 11 | -1,240.46 | **-3,019.05** | -3,412.07 | 0.091 | 0.9806 | 46.2 / 27.6 | `09da355437d1783e`, `31df57def4da37e2`, `938f7b83369d7044` |
| bag4 | distilled tree (nested) | 11 | -1,461.27 | **-3,173.23** | -3,412.07 | 0.091 | 0.9794 | 46.5 / 28.9 | `ec1c31defb5d407c`, `b45a2e9475cdad05`, `5360c246de4150e0` |
| hgbc | learner | 11 | -549.70 | **-915.46** | -928.63 | 0.091 | 0.9286 | 0.0 / 0.0 | `5f7a0b5ecf2776b1`, `42ba4857a9ead3d9`, `166a1766b6481ecd` |
| hgbc | distilled rules (nested) | 11 | -1,196.40 | **-3,777.70** | -3,958.69 | 0.273 | 0.9867 | 15.3 / 2.2 | `0341c9e4b694076e`, `89b8fb299cc3123c`, `cba723621c6c42d4` |
| hgbc | distilled tree (nested) | 11 | -3,412.07 | **-6,373.71** | -6,930.53 | 0.182 | 0.9867 | 13.3 / 2.0 | `7652b34cf5008ae1`, `6df70742f30687cb`, `21e564e972bb1dad` |
| hgbr | learner | 11 | -538.44 | **-2,156.07** | -2,497.51 | 0.000 | 0.8959 | 94.5 / 77.8 | `9ee09b3b6614ce17`, `b0c16d2cf56e1872`, `5bd52dddfc7e1f4d` |
| hgbr | distilled rules (nested) | 11 | -1,148.29 | **-2,717.22** | -2,897.75 | 0.000 | 0.9576 | 52.6 / 27.5 | `f2cffea998aad92c`, `bbb7acf6c344543e`, `252eb1badc3fa132` |
| hgbr | distilled tree (nested) | 11 | -728.38 | **-2,248.77** | -2,475.85 | 0.091 | 0.9370 | 78.2 / 47.4 | `d4c8ab19e56694d8`, `ccfbf9de6deea8be`, `0807c0c3608b4ff1` |
| pt1 | learner | 11 | -165.19 | **-1,010.88** | -1,194.65 | 0.364 | 0.8777 | 62.4 / 26.6 | `6dc75dc97c9010fa`, `eb195047238db461`, `ad2db63aedf32486` |
| pt2 | learner | 11 | -45.08 | **-433.92** | -586.07 | 0.364 | 0.5981 | 87.7 / 30.8 | `134dd9c3514c157a`, `f5f6e29b5fd9e4e5`, `58a51792c5d567f2` |
| pt3 | learner | 11 | -60.44 | **-600.53** | -725.90 | 0.455 | 0.3898 | 78.2 / 24.1 | `3c0fd89cd091da98`, `7b3213e9a0b41120`, `ed34510c9b5a0f9d` |
| scorecard | learner | 11 | -56.96 | **-1,805.81** | -1,821.80 | 0.364 | 0.9794 | 93.2 / 52.6 | `643ba297c92cde6c`, `1f7b52bb1b0ea186`, `08874b98634fa007` |
| scorecard | distilled rules (nested) | 11 | 92.89 | **-835.66** | -1,041.38 | 0.455 | 0.9831 | 82.1 / 71.0 | `d54820effaca030f`, `8709e7fec1fcb70f`, `67c5f4455c7d2b56` |
| scorecard | distilled tree (nested) | 11 | 92.89 | **-835.66** | -1,041.38 | 0.455 | 0.9831 | 82.2 / 71.6 | `96c2dd0e659e4360`, `3e7d78d22f34fcb8`, `3e21ab5162f28348` |
| scorecard_linear | learner | 11 | -171.36 | **-1,479.50** | -1,786.26 | 0.273 | 0.9782 | 95.8 / 50.9 | `7ff75f435ca28ab2`, `80d18ef69aceadcd`, `b42d9544e3b36950` |
| scorecard_linear | distilled rules (nested) | 11 | -293.76 | **-1,126.76** | -1,144.90 | 0.364 | 0.9794 | 92.8 / 53.5 | `83374910b0a83add`, `c7d4174fc01b6a16`, `f1596ef406efb38c` |
| scorecard_linear | distilled tree (nested) | 11 | -293.76 | **-1,126.76** | -1,144.90 | 0.364 | 0.9794 | 93.8 / 54.5 | `60a5b79bdf5f7b84`, `56a6491dfe5f6a16`, `8eb1652c030ea88e` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bag4 | rules | `e9bc055bff7405fc` | 0.9915 | -1,739.87 | 1,208.27 | 51.5 | 0 | 1.000 / 1.000 / 1.000 | 0.0 | `7c5b055bf54ec853` | 1.0000 | - | - | 0.992 |  |
| bag4 | tree | `a9e09e9c126efee7` | 0.9915 | -1,739.87 | 1,208.27 | 49.9 | 0 | 1.000 / 1.000 / 1.000 | 0.0 | - | - | - | - | - | - |
| hgbc | rules | `d0995de69ff4f094` | 0.9479 | -1,467.28 | -1,213.24 | 6.2 | 4 | 0.978 / 1.000 / 0.705 | 1.0 | `0c3c8524a607387c` | 0.9455 | 352.01 | 0.0 | 0.961 | hour_bin == 15 |
| hgbc | tree | `07fcb847059f709f` | 0.9552 | -524.22 | -167.24 | 12.9 | 5 | 0.971 / 1.000 / 0.607 | 1.0 | - | - | - | - | - | - |
| hgbr | rules | `941e5d7c5643a1c9` | 0.9443 | -1,368.22 | -1,143.22 | 73.5 | 2 | 0.944 / 1.000 / 0.500 | 0.5 | `7ff56f28fc132b35` | 0.9274 | 900.83 | 99.3 | 0.927 | hour_bin == 10 AND dir != down |
| hgbr | tree | `f14ee2085ca8422a` | 0.9274 | -1,053.00 | -928.08 | 81.5 | 4 | 0.942 / 0.867 / 0.565 | 1.0 | - | - | - | - | - | - |
| pt1 | policy refit on all IS | - | - | - | - | - | - | by construction | 0 | `5ac568113e0c89cc` | 1.0000 | - | - | - | (empty: take everything) |
| pt2 | policy refit on all IS | - | - | - | - | - | - | by construction | 1 | `2d8274db7c53c831` | 0.8789 | 370.33 | 40.2 | - | hour_bin != <09:25 AND hour_bin == 11 |
| pt3 | policy refit on all IS | - | - | - | - | - | - | by construction | 2 | `e87371689d7a8bb1` | 0.8874 | 686.75 | 4.5 | - | hour_bin != <09:25 AND hour_bin != 11 AND hour_bin == 15; hour_bin != <09:25 AND hour_bin == 11 AND dir == down |
| scorecard | rules | `d046eab79137a8d4` | 0.9806 | 438.95 | 218.04 | 99.2 | 2 | 0.998 / 0.875 / 1.000 | 0.0 | `2d301fb8cfd1283d` | 1.0000 | - | - | 0.983 |  |
| scorecard | tree | `d1a54a0269bfdb8a` | 0.9806 | 438.95 | 218.04 | 98.8 | 2 | 0.998 / 0.875 / 1.000 | 0.0 | - | - | - | - | - | - |
| scorecard | scorecard refit on all IS | - | - | - | - | - | - | 0.983 | 0 | `b240129da9a45d13` | 1.0000 | - | - | - | hour_bin=10: {'present': -3}; hour_bin=11: {'present': -5}; hour_bin=15: {'present': -12}; hour_bin=<09:25: {'present': 20}; dir=down: {'present': 7}; skip if score < -12.00 |
| scorecard_linear | rules | `29131490d4e9bddf` | 0.9600 | 746.93 | 521.47 | 87.0 | 1 | 0.998 / 1.000 / 0.943 | 0.0 | `9413b9fe52f004c7` | 1.0000 | - | - | 0.958 |  |
| scorecard_linear | tree | `22350b9a76f71657` | 0.9600 | 746.93 | 521.47 | 88.4 | 1 | 0.998 / 1.000 / 0.943 | 0.0 | - | - | - | - | - | - |
| scorecard_linear | scorecard refit on all IS | - | - | - | - | - | - | 0.924 | 0 | `92bbdec26a2a3976` | 0.9661 | 268.61 | 0.1 | - | hour_bin=10: {'present': -3}; hour_bin=11: {'present': -5}; hour_bin=15: {'present': -12}; hour_bin=<09:25: {'present': 20}; dir=down: {'present': 7}; skip if score < -5.00 |

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
| hgbr | L0 | 832 | 1.000 | -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 | `2563655c736259f7` | 0.8209 | -1,544.59 | -1,585.89 | 3 | 0.764 | n/a (other rows) | - | - | - | - |
| hgbr | L2x1 | 826 | 0.954 | -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 | `4f0cb63167458a6f` | 0.8584 | 226.53 | 117.84 | 8 | 0.835 | `8ea889248e905a6b` | 0.8584 | 32.90 | 184.58 | 9 |
| hgbr | L2x2 | 826 | 0.931 | -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 | `4565919adbdb290d` | 0.8717 | -97.68 | 29.87 | 7 | 0.838 | `397b5e21af313b9d` | 0.8717 | -158.17 | 29.79 | 8 |
| hgbr | L3 | 826 | 0.761 | -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 -1,500.00 | `dacb69e043df5f7e` | 1.0000 | - | - | - | - | `48e205fc37be3d9a` | 1.0000 | - | - | - |
| pt1 | L0 | 832 | 1.000 | - | `c684fc3f0f32311f` | 0.9663 | 2,498.24 | 1,694.88 | 2 | 0.999 | n/a (other rows) | - | - | - | - |
| pt1 | L2x1 | 826 | 0.954 | - | `7923e9cb61d98657` | 0.9600 | -717.81 | -353.56 | 1 | 0.926 | `50974fdbecbf08eb` | 0.9600 | -1,045.76 | -745.64 | 1 |
| pt1 | L2x2 | 826 | 0.931 | - | `3ee52e4c76fce0a6` | 0.4843 | 209.26 | 42.73 | 5 | 0.532 | `b21a47792f33b123` | 0.4843 | 300.04 | 149.25 | 5 |
| pt1 | L3 | 826 | 0.761 | - | `809b4f736e374ee1` | 0.8644 | -2.54 | -1.54 | 3 | 0.789 | `02f686087a34a85a` | 0.8644 | 73.33 | 261.59 | 8 |
| pt2 | L0 | 832 | 1.000 | - | `0ae1cb7cd280f77e` | 0.4928 | 182.05 | 267.46 | 6 | 0.511 | n/a (other rows) | - | - | - | - |
| pt2 | L2x1 | 826 | 0.954 | - | `633e6685371077ff` | 0.3571 | 182.96 | 57.59 | 7 | 0.404 | `30f13611f1a5022c` | 0.3571 | 368.21 | 393.10 | 7 |
| pt2 | L2x2 | 826 | 0.931 | - | `988a9a35599be80b` | 0.4879 | -684.07 | -551.88 | 3 | 0.423 | `c95887574a411acd` | 0.4879 | -380.89 | -451.06 | 5 |
| pt2 | L3 | 826 | 0.761 | - | `83a9d83ed3a14e3b` | 0.7397 | 0.82 | 1.43 | 8 | 0.678 | `c06447aa1a204d19` | 0.7397 | 297.55 | 396.97 | 7 |
| pt3 | L0 | 832 | 1.000 | - | `59d6a53951848b77` | 0.5072 | -750.75 | -243.98 | 6 | 0.421 | n/a (other rows) | - | - | - | - |
| pt3 | L2x1 | 826 | 0.954 | - | `9776920c463534f6` | 0.3559 | 23.29 | -2.54 | 6 | 0.360 | `deb9bbf4285dc241` | 0.3559 | -113.64 | 18.92 | 5 |
| pt3 | L2x2 | 826 | 0.931 | - | `9a80aa4121067751` | 0.3947 | 123.99 | 168.10 | 6 | 0.402 | `53a7f7b2c8c70dcf` | 0.3947 | -0.06 | 66.28 | 7 |
| pt3 | L3 | 826 | 0.761 | - | `d8e961afb65e4bb5` | 0.6937 | -2.18 | -1.59 | 2 | 0.575 | `6d8894910f83e8c4` | 0.6937 | 114.14 | 262.54 | 6 |
| scorecard | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.40 0.10 0.10 0.10 | `4fb070344f836d10` | 0.9940 | 1,810.53 | 1,028.96 | 1 | 0.999 | n/a (other rows) | - | - | - | - |
| scorecard | L2x1 | 826 | 0.954 | 0.10 0.40 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `619691079746d502` | 0.9915 | 891.51 | 2,513.29 | 1 | 0.982 | `c69a74a57d8cd778` | 0.9915 | -1,324.79 | 1,652.21 | 0 |
| scorecard | L2x2 | 826 | 0.931 | 0.10 0.40 0.40 0.40 0.10 0.40 0.10 0.40 0.10 0.10 0.40 0.10 | `b301ad65879db77b` | 0.9927 | 2,313.77 | 2,180.83 | 1 | 0.997 | `364ab6d800ed4965` | 0.9927 | 1,620.27 | 1,402.12 | 1 |
| scorecard | L3 | 826 | 0.761 | 0.10 0.40 0.40 0.10 0.40 0.10 0.10 0.10 0.40 0.10 0.40 0.40 | `b4622ba94b77671c` | 0.9528 | 1.12 | 0.77 | 3 | 0.961 | `8b929131d44814f1` | 0.9528 | 424.32 | 769.16 | 2 |
| scorecard_linear | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.40 0.10 0.10 0.10 | `0a071ad410042ccb` | 0.9940 | 1,810.53 | 1,028.96 | 1 | 0.999 | n/a (other rows) | - | - | - | - |
| scorecard_linear | L2x1 | 826 | 0.954 | 0.10 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.35 0.40 0.40 0.10 | `497743145b8559d0` | 0.9867 | -226.49 | -321.28 | 0 | 0.985 | `809dcbd7b8c13322` | 0.9867 | -1,240.76 | 500.01 | 0 |
| scorecard_linear | L2x2 | 826 | 0.931 | 0.10 0.10 0.40 0.40 0.40 0.10 0.10 0.40 0.10 0.10 0.10 0.10 | `928652aa6d957c55` | 1.0000 | - | - | - | - | `b8f47cfaf8e24674` | 1.0000 | - | - | - |
| scorecard_linear | L3 | 826 | 0.761 | 0.40 0.40 0.40 0.10 0.40 0.10 0.40 0.40 0.40 0.10 0.40 0.40 | `8efa7dbaec617da5` | 0.9358 | 1.44 | 1.08 | 4 | 0.957 | `69a9238be25a279f` | 0.9358 | 430.05 | 624.32 | 3 |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| bag4 | time decay c = 0.5 | `150cdcb63ae63acf` | 0.9843 | -1,583.14 | -193.24 | 1 | 0.40 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.10 0.35 0.10 0.10 |
| bag4 | bag3 | `981e363680e8349a` | 0.9867 | -1,015.59 | -1,235.37 | 1 | 0.10 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.35 0.10 0.10 0.10 |
| bag4 | bag5 | `58fd5e8db9cbdc19` | 0.9915 | -1,739.87 | 1,208.27 | 0 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.35 0.10 0.10 |
| hgbc | time decay c = 0.5 | `2b35a23b5c097597` | 0.9358 | -1,056.75 | -885.37 | 5 | 0.15 0.10 0.15 0.35 0.10 0.10 0.15 0.15 0.30 0.30 0.15 0.15 |
| scorecard | time decay c = 0.5 | `7c04a820ecdf73b5` | 0.9855 | 2,696.73 | 2,477.26 | 3 | 0.10 0.10 0.40 0.40 0.40 0.40 0.10 0.40 0.40 0.10 0.40 0.10 |
| scorecard_linear | time decay c = 0.5 | `0fd7996e6f84842e` | 1.0000 | - | - | - | 0.40 0.40 0.40 0.40 0.40 0.40 0.10 0.40 0.10 0.10 0.40 0.40 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | bag4 kept share | hgbc kept share | hgbr kept share | pt1 kept share | pt2 kept share | pt3 kept share | scorecard kept share | scorecard_linear kept share |
|---|---|---|---|---|---|---|---|---|---|
| 09 | 96 | 1.000 | 1.000 | 0.885 | 0.979 | 0.562 | 0.542 | 1.000 | 0.969 |
| 10 | 123 | 0.943 | 0.943 | 0.626 | 0.919 | 0.585 | 0.537 | 1.000 | 1.000 |
| 11 | 100 | 1.000 | 0.890 | 0.760 | 0.990 | 0.470 | 0.310 | 1.000 | 0.950 |
| 12 | 126 | 1.000 | 0.952 | 0.952 | 0.976 | 0.587 | 0.500 | 1.000 | 0.936 |
| 13 | 149 | 1.000 | 1.000 | 1.000 | 0.960 | 0.658 | 0.577 | 1.000 | 0.953 |
| 14 | 132 | 1.000 | 1.000 | 1.000 | 0.985 | 0.636 | 0.591 | 1.000 | 0.970 |
| 15 | 45 | 1.000 | 0.178 | 1.000 | 0.867 | 0.467 | 0.400 | 1.000 | 0.978 |
| <09:25 | 50 | 1.000 | 1.000 | 0.900 | 0.960 | 0.760 | 0.760 | 0.720 | 0.860 |
| >=15:20 | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 0.600 | 0.400 | 1.000 | 1.000 |
| **regime** | |  |  |  |  |  |  |  |  |
| choch<2_since_bos | 567 | 0.989 | 0.926 | 0.894 | 0.956 | 0.600 | 0.520 | 0.986 | 0.958 |
| choch>=2_since_bos | 259 | 0.996 | 0.927 | 0.876 | 0.973 | 0.583 | 0.537 | 0.977 | 0.958 |
| dir = down | 400 | 1.000 | 0.922 | 0.912 | 0.990 | 0.875 | 0.772 | 0.975 | 0.920 |
| dir = up | 426 | 0.984 | 0.930 | 0.866 | 0.934 | 0.331 | 0.293 | 0.991 | 0.993 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| bag4 | 0.5097 | 0.4646 | 0.2772 | 0.23931 | 0.20038 | -0.1943 | 0.1888 | [0.3,0.4): 83, 0.366, 0.373; [0.4,0.5): 523, 0.447, 0.258; [0.5,0.6): 207, 0.538, 0.299; [0.6,0.7): 13, 0.616, 0.077 |
| hgbc | 0.5136 | 0.4494 | 0.2772 | 0.23959 | 0.20038 | -0.1957 | 0.1922 | [0.0,0.1): 15, 0.091, 0.267; [0.1,0.2): 30, 0.113, 0.100; [0.2,0.3): 34, 0.276, 0.441; [0.3,0.4): 97, 0.364, 0.237; [0.4,0.5): 360, 0.455, 0.281; [0.5,0.6): 269, 0.538, 0.297; [0.6,0.7): 21, 0.625, 0.143 |
| scorecard | 0.4810 | 0.4686 | 0.2772 | 0.23852 | 0.20038 | -0.1903 | 0.1914 | [0.3,0.4): 15, 0.365, 0.333; [0.4,0.5): 760, 0.466, 0.276; [0.5,0.6): 44, 0.535, 0.273; [0.6,0.7): 7, 0.609, 0.286 |
| scorecard_linear | 0.4970 | 0.4692 | 0.2772 | 0.23829 | 0.20038 | -0.1892 | 0.1919 | [0.2,0.3): 4, 0.287, 0.250; [0.3,0.4): 31, 0.386, 0.194; [0.4,0.5): 736, 0.469, 0.279; [0.5,0.6): 55, 0.536, 0.309 |

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

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p, boot, columns and (for the finalist) the null-tape checks filled

| sub-family | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (I) context, inside the frozen vocabulary | bag4 -> distilled rules | `e9bc055bff7405fc` | 0.9915 | -1,739.87 | 1,208.27 | 51.5 | 0 | -3,019.05 | -1,240.46 | 1.000 | 1.0000 | [-6838.65, 3943.34] | 9 / 14 | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | bag4 -> distilled tree | `a9e09e9c126efee7` | 0.9915 | -1,739.87 | 1,208.27 | 49.9 | 0 | -3,173.23 | -1,461.27 | 1.000 | 1.0000 | [-6363.56, 3855.08] | 9 / 14 | diff>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbc -> distilled rules | `d0995de69ff4f094` | 0.9479 | -1,467.28 | -1,213.24 | 6.2 | 4 | -3,777.70 | -1,196.40 | 0.978 | 1.0000 | [-2684.74, -79.19] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbc -> distilled tree | `07fcb847059f709f` | 0.9552 | -524.22 | -167.24 | 12.9 | 5 | -6,373.71 | -3,412.07 | 0.971 | 1.0000 | [-1771.28, 614.12] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbr -> distilled rules | `941e5d7c5643a1c9` | 0.9443 | -1,368.22 | -1,143.22 | 73.5 | 2 | -2,717.22 | -1,148.29 | 0.944 | 1.0000 | [-2731.32, 52.0] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | hgbr -> distilled tree | `f14ee2085ca8422a` | 0.9274 | -1,053.00 | -928.08 | 81.5 | 4 | -2,248.77 | -728.38 | 0.942 | 1.0000 | [-2235.04, 78.35] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | pt1 (rule list by construction) | `feb78729208ed323` | 0.9613 | -881.52 | -1,107.42 | 23.2 | 1 | -1,010.88 | -165.19 | - | 1.0000 | [-1692.94, 153.68] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | pt2 (rule list by construction) | `2aae111dbdd37a49` | 0.5944 | 142.62 | -26.24 | 79.6 | 5 | -433.92 | -45.08 | - | 1.0000 | [-466.35, 796.56] | 9 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | pt3 (rule list by construction) | `79038c5a5197c2b6` | 0.5254 | -218.77 | -259.36 | 14.9 | 5 | -600.53 | -60.44 | - | 1.0000 | [-938.85, 455.95] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard -> distilled rules | `d046eab79137a8d4` | 0.9806 | 438.95 | 218.04 | 99.2 | 2 | -835.66 | 92.89 | 0.998 | 1.0000 | [-1092.37, 2173.47] | 7 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard -> distilled tree | `d1a54a0269bfdb8a` | 0.9806 | 438.95 | 218.04 | 98.8 | 2 | -835.66 | 92.89 | 0.998 | 1.0000 | [-1021.6, 2115.21] | 7 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard (scorecard) | `a8c1cd3ea062d7dd` | 0.9831 | 66.56 | -153.88 | 96.0 | 2 | -1,805.81 | -56.96 | - | 1.0000 | [-1458.99, 1885.6] | 8 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard_linear -> distilled rules | `29131490d4e9bddf` | 0.9600 | 746.93 | 521.47 | 87.0 | 1 | -1,126.76 | -293.76 | 0.998 | 1.0000 | [-292.6, 1319.35] | 8 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard_linear -> distilled tree | `22350b9a76f71657` | 0.9600 | 746.93 | 521.47 | 88.4 | 1 | -1,126.76 | -293.76 | 0.998 | 1.0000 | [-203.58, 1334.36] | 8 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (I) context, inside the frozen vocabulary | scorecard_linear (scorecard) | `7b7417541e9b90fc` | 0.9576 | 433.44 | 207.28 | 88.0 | 1 | -1,479.50 | -171.36 | - | 1.0000 | [-627.94, 1087.85] | 8 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **pt2 (rule list by construction)** — nested OOF `2aae111dbdd37a49`, CPCV p5 -433.92, go/no-go **FAIL** (9 items failed). Frozen form: `2d8274db7c53c831` kept share 0.8789, diff 370.33, control pct 40.2; features used: ['hour_bin'].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 0.5944 |
| kept_n>=80 | yes | 491 |
| diff>0 | yes | 142.62 |
| diff_top1_removed>0 | no | -26.24 |
| kept_mean_slip8>0 | no | -1089.18 |
| sign_blocks>=8/12 | no | 5 |
| control_pct>=95 | no | 79.6 |
| cpcv_p5_diff>0 | no | -433.92 |
| pbo<=0.2 | no | 0.5225 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | yes | 0.0565 |
| boot_ci_excludes_0 | no | [-466.35, 796.56] |
| null_tape:evaluated | no | not evaluable: quick dry run: null tapes not evaluated |
| no_time_proxy_columns | yes | ['hour_bin'] |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'hv3_ratio', 'n_rooms_alive', 'range_3h_pts']); nothing to refit.

### 5minute / sub-family (II) h5_full — OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)

Feature matrix: base design 236 + ext 61 -> 238 after the importance study's drops -> **236** after dropping the time proxies ['sl', 'n_events_asof']. HGB interaction_cst: 39 importance clusters + 4 interaction pairs (pairs with a time proxy dropped: [['ffd_close_dstar', 'sl']]); monotonic_cst: {'n_choch_since_bos': -1, 'n_choch_since_bos_today': -1, 'alt_dir6': -1}. Interaction pairs of the shortlist file: [['touch_prot_bars_ago', 'ffd_close_dstar'], ['room_ahead_dist_atr', 'n_rooms_alive'], ['room_ahead_dist_atr', 'fz_take_why=nan'], ['ffd_close_dstar', 'sl'], ['room_ahead_dist_atr', 'ffd_close_dstar']] (pairs with a time proxy: [['ffd_close_dstar', 'sl']]; both rooms pairs are used as HGB interaction groups; the rule searches of this sub-family are H5 as pre-registered, i.e. over the whole table, outside the shortlist).

#### OOF (12 purged blocks, nested tau; controls on)

| sub-family | model | description | OOF id | kept n | kept share | kept mean | skipped mean | diff | diff top-1% off | perm p | control pct | loser recall / precision | wtd winner recall | top-decile skipped | sign blocks | kept mean slip 8 | taus (12 folds) | tau constraint met (folds) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | dt3 | H5 DecisionTreeClassifier depth <= 3, min leaf 40, nested tau | `6087330066520d4b` | 793 | 0.9600 | -754.51 | -818.14 | **63.63** | -162.14 | 0.9365 | 94.8 | 0.038 / 0.697 | 0.948 | 0.043 | 4 | -1,144.48 | 0.10 0.15 0.10 0.10 0.20 0.10 0.10 0.10 0.10 0.10 0.15 0.10 | 9 |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | h5rules | H5 greedy rule list by training kept expectancy (stop < 200 INR/trade) | `d0fc4ce5f0aa3614` | 183 | 0.2215 | -595.02 | -803.17 | **208.14** | 236.44 | 0.5942 | 47.4 | 0.786 / 0.729 | 0.283 | 0.565 | 8 | -984.99 | - | - |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc | (b) HGB classifier, interaction_cst = clusters + pairs, monotone H2 columns | `af1365485c4b5c84` | 790 | 0.9564 | -740.20 | -1,126.95 | **386.75** | 160.28 | 0.6057 | 44.9 | 0.044 / 0.722 | 0.981 | 0.000 | 7 | -1,130.16 | 0.15 0.10 0.10 0.15 0.15 0.15 0.10 0.10 0.10 0.10 0.10 0.10 | 12 |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard | (e) scorecard, <= 6 source features by the L1 path | `d469afb88301a1e3` | 824 | 0.9976 | -752.40 | -2,675.05 | **1,922.65** | 1,705.49 | 0.4883 | 62.7 | 0.003 / 1.000 | 1.000 | 0.000 | 1 | -1,142.36 | 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.10 0.10 0.40 0.10 0.10 | 12 |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard_linear | (e) scorecard, <= 6 source features by the L1 path | `fcd1323d61d635df` | 826 | 1.0000 | -757.05 | - | **-** | - | - | - | - / - | - | - | - | - | 0.10 0.40 0.10 0.40 0.40 0.40 0.10 0.40 0.10 0.40 0.40 0.10 | 12 |

Reading: `-` in a kept-vs-skipped column = the gate skipped nothing (or kept nothing) in the pooled OOF, so the difference is undefined. A tau of 0.10 = the grid floor: no threshold on the grid kept >= 90% of the |net|-weighted winner net with a higher kept mean than keeping everything (the column 'tau constraint met' counts the folds where a grid value satisfied the recall constraint).

#### The fixed-tau grid (every tau tried = a trial; controls off)

| model | tau | OOF id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|
| dt3 | 0.1 | `b75281a5fdecfc21` | 0.9600 | 63.63 | -162.14 | 4 |
| dt3 | 0.15 | `74db90ec896f6d38` | 0.9588 | 89.69 | -136.36 | 4 |
| dt3 | 0.2 | `533d2b0e6ca00fbd` | 0.8692 | 112.30 | -137.19 | 5 |
| dt3 | 0.25 | `22cc9fce31339741` | 0.7688 | 382.67 | 251.19 | 6 |
| dt3 | 0.3 | `64e7f06768443376` | 0.7615 | 336.64 | 198.94 | 6 |
| dt3 | 0.35 | `e398062a14fd13cf` | 0.6840 | -24.45 | -220.56 | 5 |
| dt3 | 0.4 | `0a20d174c5f77df6` | 0.5823 | -85.33 | -247.67 | 3 |
| hgbc | 0.1 | `fcd06180b5a79b9c` | 0.9794 | 846.97 | 625.88 | 5 |
| hgbc | 0.15 | `b65182b5e3bc9a77` | 0.9189 | 66.10 | 178.54 | 9 |
| hgbc | 0.2 | `3e6cc95852955ee3` | 0.8196 | -42.84 | 27.05 | 6 |
| hgbc | 0.25 | `36f7c4d9c1fb434c` | 0.7058 | 258.59 | 191.14 | 8 |
| hgbc | 0.3 | `90810ddb108f40ea` | 0.5545 | -98.05 | -291.86 | 5 |
| hgbc | 0.35 | `8b7a9d274406d711` | 0.4443 | 114.91 | 35.90 | 7 |
| hgbc | 0.4 | `05e3f5696c62e9f4` | 0.3487 | -214.90 | -303.71 | 4 |
| scorecard | 0.1 | `09d29eb19ed29ba3` | 1.0000 | - | - | - |
| scorecard | 0.15 | `22060821a9cd2ffa` | 1.0000 | - | - | - |
| scorecard | 0.2 | `9c5a90702fdd8a58` | 1.0000 | - | - | - |
| scorecard | 0.25 | `c5bfb377acc0a9bb` | 1.0000 | - | - | - |
| scorecard | 0.3 | `bd34a578aaed336d` | 1.0000 | - | - | - |
| scorecard | 0.35 | `0597ae2123d08560` | 1.0000 | - | - | - |
| scorecard | 0.4 | `3345c311d152da81` | 0.9976 | 1,922.65 | 1,705.49 | 1 |
| scorecard_linear | 0.1 | `bc762d6ce478953c` | 1.0000 | - | - | - |
| scorecard_linear | 0.15 | `4f358442cfddc4ac` | 1.0000 | - | - | - |
| scorecard_linear | 0.2 | `8cd1d9b307e36876` | 1.0000 | - | - | - |
| scorecard_linear | 0.25 | `7f76f954569d08fa` | 1.0000 | - | - | - |
| scorecard_linear | 0.3 | `07e4273ca04e4de1` | 1.0000 | - | - | - |
| scorecard_linear | 0.35 | `9dd7cb17899468b6` | 1.0000 | - | - | - |
| scorecard_linear | 0.4 | `b11e90df0d32688d` | 1.0000 | - | - | - |

#### CPCV (66 splits, 11 paths; controls on)

| model | form | paths | diff median | diff p5 | diff min | share > 0 | kept share median | control pct median / p5 | path ids (first 3) |
|---|---|---|---|---|---|---|---|---|---|
| dt3 | learner | 11 | -18.31 | **-2,965.69** | -4,825.39 | 0.455 | 0.9588 | 50.0 / 9.0 | `759346810fc1e163`, `1fcb049987972f6f`, `e82be834c3db4e84` |
| h5rules | learner | 11 | 37.83 | **-589.23** | -710.91 | 0.545 | 0.2252 | 75.6 / 10.4 | `074f71371a53fef1`, `9c521ad0aa5eecd0`, `956dd533c382dfcc` |
| hgbc | learner | 11 | -116.54 | **-855.27** | -985.13 | 0.364 | 0.9528 | 44.5 / 21.6 | `815484311f406efd`, `5149dd406769c330`, `84c6eaecfd1f2c2a` |
| hgbc | distilled rules (nested) | 11 | - | **-** | - | 0.000 | 1.0000 | - / - | `5553fde00c17588c`, `f6fedbc580130424`, `0b09c97ca6f75d98` |
| hgbc | distilled tree (nested) | 11 | -1,163.91 | **-1,177.48** | -1,178.99 | 0.091 | 1.0000 | 59.2 / 58.0 | `99d11324bec0569f`, `bbe451a3f76b8c6f`, `92b3b2c0d311e86c` |
| scorecard | learner | 11 | 82.48 | **-744.59** | -760.02 | 0.364 | 0.9915 | 72.3 / 14.0 | `2db64279966f561e`, `e3e2a9fcca7b93d1`, `aeb5bb7490a97b63` |
| scorecard | distilled rules (nested) | 11 | 826.61 | **53.58** | -79.50 | 0.455 | 0.9976 | 70.7 / 31.9 | `585cf619cd93f692`, `80fe5aa0fbe06b06`, `bd4b58399f9dba66` |
| scorecard | distilled tree (nested) | 11 | 140.31 | **-3,147.84** | -4,042.40 | 0.273 | 0.9952 | 81.0 / 20.7 | `d9f063c3b85091ed`, `201ec856e5593fa9`, `b4e113c36f8c7239` |
| scorecard_linear | learner | 11 | 1,055.94 | **-2,533.43** | -3,566.56 | 0.545 | 0.9952 | 88.5 / 28.6 | `9b3a2634a40a83d5`, `9bbef9a23dfa3fa5`, `57cc0188647cea28` |
| scorecard_linear | distilled rules (nested) | 11 | 786.89 | **-130.87** | -286.05 | 0.364 | 1.0000 | 83.5 / 54.6 | `da136aed659ec872`, `ca8d3d99a464f2a6`, `b0fa9fcdcfb9c9b1` |
| scorecard_linear | distilled tree (nested) | 11 | 1,345.64 | **-641.80** | -1,105.52 | 0.455 | 0.9964 | 92.1 / 21.5 | `4d3367faf8be2b78`, `78fd35c2baa6e9f8`, `fd90a5bcf62d12ce` |

#### Distillation (nested: fit inside every split to the learner's training-fold decisions; frozen: fit to the pooled OOF decisions / refit on all IS)

| model | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | fidelity to the learner's OOF decision (agreement / skip precision / skip recall) | rules per fold (median) | frozen form id | frozen kept share | frozen diff | frozen control pct | frozen fidelity | frozen rules |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | tree refit on all IS | - | - | - | - | - | - | by construction | 1 | `ac3d6f426fe58f1b` | 0.9504 | 2,247.69 | 100.0 | - | bocpd_ret_h240_map <= 136.5 AND vol_max_ratio20_choch_to_k <= 1.3535 AND nn_dist_prefix_long <= 1.718179 |
| h5rules | policy refit on all IS | - | - | - | - | - | - | by construction | 2 | `280c2eca02529d69` | 0.2203 | 2,114.72 | 93.9 | - | vol_max_ratio20_5 <= 4.352839 AND today_net_asof > -10235.729355 AND jump4_run <= 70.387097; room_ahead_dist_atr > 0.781445 AND room_edge_dist_dir_atr > -1.828755 |
| hgbc | rules | `4a2a1dcbb411cf89` | 1.0000 | - | - | - | - | 0.956 / - / 0.000 | 0.0 | `a8337faa323f839c` | 1.0000 | - | - | 0.956 |  |
| hgbc | tree | `60ce5055a1b965e4` | 1.0000 | - | - | - | - | 0.956 / - / 0.000 | 0.0 | - | - | - | - | - | - |
| scorecard | rules | `d14eb10f08c1c59e` | 1.0000 | - | - | - | - | 0.998 / - / 0.000 | 0.0 | `37233722aa7f64b3` | 1.0000 | - | - | 0.998 |  |
| scorecard | tree | `e98d53dffbcf095b` | 1.0000 | - | - | - | - | 0.998 / - / 0.000 | 0.0 | - | - | - | - | - | - |
| scorecard | scorecard refit on all IS | - | - | - | - | - | - | 0.998 | 0 | `4351f112da779e8e` | 1.0000 | - | - | - | choch_same_session: {'present': -17}; gmm4_map: bins [1.0, 2.0, 3.0] points {'1': -20}; skip if score < -37.00 |
| scorecard_linear | rules | `ef9aa00a9b77c2e4` | 1.0000 | - | - | - | - | 1.000 / - / - | 0.0 | `c1f2ea8de14c0c64` | 1.0000 | - | - | 1.000 |  |
| scorecard_linear | tree | `5e4c095fbd18996e` | 1.0000 | - | - | - | - | 1.000 / - / - | 0.0 | - | - | - | - | - | - |
| scorecard_linear | scorecard refit on all IS | - | - | - | - | - | - | 1.000 | 0 | `73790fb19b225b36` | 1.0000 | - | - | - | choch_same_session: {'present': -17}; gmm4_map: bins [1.0, 2.0, 3.0] points {'1': -20}; skip if score < - |

#### Robustness labels (trained on the label, scored on the label's table and on the L1 book; controls off; never candidates)

| model | train label | IS units | label uniqueness | taus | scored on label: id | kept share | diff | diff top-1% off | sign blocks | wtd winner recall | scored on L1: id | kept share | diff | diff top-1% off | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dt3 | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `aa1c5d6630cbc315` | 0.9423 | -626.77 | -1,452.25 | 3 | 0.942 | n/a (other rows) | - | - | - | - |
| dt3 | L2x1 | 826 | 0.954 | 0.20 0.10 0.20 0.20 0.10 0.20 0.10 0.20 0.20 0.15 0.20 0.20 | `ed2d6c00dc7c2dee` | 0.8971 | -297.11 | -401.82 | 2 | 0.953 | `d23be6c075737154` | 0.8971 | -317.49 | -559.73 | 5 |
| dt3 | L2x2 | 826 | 0.931 | 0.15 0.20 0.20 0.20 0.20 0.10 0.10 0.20 0.10 0.15 0.15 0.15 | `2d1c536c2fcc14c9` | 0.9213 | -120.05 | -263.73 | 3 | 0.930 | `74ce7c3a46364f35` | 0.9213 | -359.16 | -594.91 | 5 |
| dt3 | L3 | 826 | 0.761 | 0.25 0.25 0.25 0.30 0.25 0.25 0.25 0.20 0.10 0.20 0.25 0.15 | `aa3c02053c570fec` | 0.9419 | 2.32 | 2.57 | 4 | 0.936 | `82fa7af4709c95b6` | 0.9419 | -1,108.62 | -885.90 | 4 |
| h5rules | L0 | 832 | 1.000 | - | `27f63d4a3d4cccc8` | 0.2644 | -266.20 | -4.73 | 5 | 0.259 | n/a (other rows) | - | - | - | - |
| h5rules | L2x1 | 826 | 0.954 | - | `35eaf94859f7bc08` | 0.2421 | -453.07 | -671.10 | 4 | 0.361 | `2caed1359884303a` | 0.2421 | -440.61 | -548.46 | 4 |
| h5rules | L2x2 | 826 | 0.931 | - | `599b3e6834abf935` | 0.2155 | -601.14 | -803.87 | 5 | 0.258 | `eba079093fe93e4e` | 0.2155 | -569.66 | -557.39 | 5 |
| h5rules | L3 | 826 | 0.761 | - | `453a469c902a8640` | 1.0000 | - | - | - | - | `77b07adb2544e78f` | 1.0000 | - | - | - |
| hgbc | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `fe0d60c33b4ba267` | 0.8918 | 1,603.83 | 1,469.01 | 10 | 0.944 | n/a (other rows) | - | - | - | - |
| hgbc | L2x1 | 826 | 0.954 | 0.25 0.20 0.15 0.20 0.15 0.25 0.15 0.20 0.20 0.20 0.20 0.20 | `dbbeb6ee11557d35` | 0.8692 | 406.54 | 299.50 | 8 | 0.975 | `d05a232d6b15906a` | 0.8692 | 633.05 | 384.41 | 10 |
| hgbc | L2x2 | 826 | 0.931 | 0.20 0.20 0.20 0.10 0.20 0.10 0.15 0.10 0.15 0.15 0.10 0.15 | `3b5ec1baf0a069af` | 0.9746 | -312.01 | -447.74 | 3 | 0.979 | `e4f25c74b2814117` | 0.9746 | -1,205.19 | -406.75 | 5 |
| hgbc | L3 | 826 | 0.761 | 0.15 0.25 0.25 0.25 0.25 0.25 0.25 0.20 0.20 0.20 0.20 0.25 | `7aab6e461831cd5a` | 0.9818 | 4.41 | 4.06 | 4 | 0.984 | `86502609fce38c7d` | 0.9818 | 556.12 | 335.50 | 5 |
| scorecard | L0 | 832 | 1.000 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `54353055b7790568` | 1.0000 | - | - | - | - | n/a (other rows) | - | - | - | - |
| scorecard | L2x1 | 826 | 0.954 | 0.10 0.35 0.10 0.10 0.35 0.10 0.35 0.10 0.40 0.10 0.10 0.10 | `77e9ec4d1143ba67` | 0.8971 | 6.29 | -98.03 | 0 | 0.937 | `fda40b9603281347` | 0.8971 | -522.37 | -490.56 | 0 |
| scorecard | L2x2 | 826 | 0.931 | 0.40 0.40 0.40 0.40 0.40 0.10 0.40 0.40 0.10 0.10 0.40 0.40 | `616b7933b27c8e66` | 0.9879 | 606.75 | 473.05 | 2 | 0.995 | `ac51d595a53b7819` | 0.9879 | 339.27 | 119.96 | 1 |
| scorecard | L3 | 826 | 0.761 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `f64d1faf477ed1bb` | 1.0000 | - | - | - | - | `38a10932912c16a1` | 1.0000 | - | - | - |
| scorecard_linear | L0 | 832 | 1.000 | 0.10 0.35 0.35 0.10 0.10 0.10 0.10 0.10 0.10 0.40 0.40 0.40 | `58294e18b9145ae0` | 0.9964 | 542.92 | -236.84 | 1 | 0.999 | n/a (other rows) | - | - | - | - |
| scorecard_linear | L2x1 | 826 | 0.954 | 0.10 0.10 0.10 0.10 0.10 0.35 0.35 0.35 0.10 0.35 0.10 0.10 | `4bb615090ebc25a3` | 0.9056 | 312.79 | 209.81 | 1 | 0.957 | `9ce61c1ce260e069` | 0.9056 | 381.51 | 142.40 | 1 |
| scorecard_linear | L2x2 | 826 | 0.931 | 0.10 0.10 0.40 0.40 0.40 0.40 0.40 0.10 0.40 0.10 0.10 0.40 | `6dee321976547f5d` | 0.9891 | 587.79 | 454.25 | 2 | 0.996 | `21ec38b3bf7c2052` | 0.9891 | 613.60 | 394.59 | 2 |
| scorecard_linear | L3 | 826 | 0.761 | 0.10 0.10 0.10 0.40 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 | `0e9cb51ca66b0876` | 1.0000 | - | - | - | - | `e75cdd49e00b2a00` | 1.0000 | - | - | - |

#### Sensitivities (controls off)

| model | variant | id | kept share | diff | diff top-1% off | sign blocks | taus |
|---|---|---|---|---|---|---|---|
| dt3 | time decay c = 0.5 | `672be58674c08cfd` | 0.9891 | 435.52 | 216.48 | 1 | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 |
| hgbc | time decay c = 0.5 | `04728e67c94b4b9d` | 0.9588 | -7.72 | -233.81 | 5 | 0.15 0.15 0.15 0.15 0.15 0.10 0.10 0.10 0.10 0.10 0.10 0.10 |
| hgbc | hgbc_nomono | `235635bfaa2cf6a1` | 0.9407 | 492.24 | 262.08 | 9 | 0.15 0.10 0.10 0.15 0.15 0.15 0.10 0.10 0.15 0.15 0.10 0.10 |
| scorecard | time decay c = 0.5 | `9cc34afbfe3e801b` | 1.0000 | - | - | - | 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 0.10 |
| scorecard_linear | time decay c = 0.5 | `a82b74c70ccf2977` | 1.0000 | - | - | - | 0.10 0.10 0.10 0.35 0.10 0.40 0.10 0.40 0.10 0.10 0.40 0.10 |

#### Kept share by hour bin, regime and direction (pooled OOF decisions)

| hour_bin | n | dt3 kept share | h5rules kept share | hgbc kept share | scorecard kept share | scorecard_linear kept share |
|---|---|---|---|---|---|---|
| 09 | 96 | 0.948 | 0.385 | 0.990 | 1.000 | 1.000 |
| 10 | 123 | 0.959 | 0.179 | 0.951 | 1.000 | 1.000 |
| 11 | 100 | 0.940 | 0.130 | 0.950 | 1.000 | 1.000 |
| 12 | 126 | 0.960 | 0.111 | 0.952 | 1.000 | 1.000 |
| 13 | 149 | 0.960 | 0.154 | 0.940 | 1.000 | 1.000 |
| 14 | 132 | 0.962 | 0.250 | 0.955 | 0.985 | 1.000 |
| 15 | 45 | 0.978 | 0.267 | 0.933 | 1.000 | 1.000 |
| <09:25 | 50 | 1.000 | 0.540 | 1.000 | 1.000 | 1.000 |
| >=15:20 | 5 | 1.000 | 0.400 | 1.000 | 1.000 | 1.000 |
| **regime** | |  |  |  |  |  |
| choch<2_since_bos | 567 | 0.947 | 0.219 | 0.963 | 0.997 | 1.000 |
| choch>=2_since_bos | 259 | 0.988 | 0.228 | 0.942 | 1.000 | 1.000 |
| dir = down | 400 | 0.970 | 0.255 | 0.963 | 0.995 | 1.000 |
| dir = up | 426 | 0.951 | 0.190 | 0.951 | 1.000 | 1.000 |

#### Calibration of the probability learners on OOF (unweighted)

| model | OOF AUC | mean p | base rate | Brier | Brier (base rate) | Brier skill | ECE | reliability (bin: n, mean p, win rate) |
|---|---|---|---|---|---|---|---|---|
| dt3 | 0.4874 | 0.4356 | 0.2772 | 0.26334 | 0.20038 | -0.3142 | 0.1978 | [0.0,0.1): 33, 0.070, 0.303; [0.1,0.2): 75, 0.188, 0.280; [0.2,0.3): 89, 0.228, 0.247; [0.3,0.4): 148, 0.353, 0.311; [0.4,0.5): 166, 0.436, 0.301; [0.5,0.6): 120, 0.535, 0.183; [0.6,0.7): 129, 0.642, 0.310; [0.7,0.8): 51, 0.764, 0.294; [0.8,0.9): 15, 0.830, 0.200 |
| hgbc | 0.5036 | 0.3518 | 0.2772 | 0.23146 | 0.20038 | -0.1551 | 0.1461 | [0.0,0.1): 17, 0.077, 0.294; [0.1,0.2): 132, 0.158, 0.258; [0.2,0.3): 219, 0.252, 0.310; [0.3,0.4): 170, 0.348, 0.253; [0.4,0.5): 131, 0.442, 0.275; [0.5,0.6): 81, 0.548, 0.259; [0.6,0.7): 53, 0.645, 0.302; [0.7,0.8): 17, 0.735, 0.235; [0.8,0.9): 6, 0.820, 0.333 |
| scorecard | 0.5077 | 0.4823 | 0.2772 | 0.24278 | 0.20038 | -0.2116 | 0.2051 | [0.3,0.4): 2, 0.396, 0.000; [0.4,0.5): 473, 0.462, 0.283; [0.5,0.6): 351, 0.510, 0.271 |
| scorecard_linear | 0.5171 | 0.4660 | 0.2772 | 0.23610 | 0.20038 | -0.1783 | 0.1888 | [0.4,0.5): 714, 0.458, 0.275; [0.5,0.6): 112, 0.519, 0.295 |

#### SHAP drivers of (b) hgbc (TreeExplainer on the 12 fold models, OOF rows)

| rank | feature | mean abs SHAP (log-odds, OOF rows, 12 fold models) |
|---|---|---|
| 1 | `bocpd_ret_h240_map` | 0.20127 |
| 2 | `room_ahead_dist_atr` | 0.13298 |
| 3 | `dist_prot_dir_atr` | 0.09827 |
| 4 | `bocpd_rng_h60_p10` | 0.09340 |
| 5 | `ffd_close_dstar` | 0.08514 |
| 6 | `touch_prot_bars_ago` | 0.08357 |
| 7 | `today_net_asof` | 0.08027 |
| 8 | `bocpd_rng_h240_since_reset` | 0.07331 |
| 9 | `dist_sl_atr` | 0.06608 |
| 10 | `p1_dist_prefix_long` | 0.06521 |
| 11 | `today_pts_asof` | 0.06370 |
| 12 | `range_3h_pts` | 0.05475 |
| 13 | `bar_range_atr` | 0.05348 |
| 14 | `range_1h_atr` | 0.05238 |
| 15 | `room_edge_dist_dir_atr` | 0.05196 |
| 16 | `close_vs_sess_open_pts` | 0.05115 |
| 17 | `fz_take_why=nan` | 0.04942 |
| 18 | `dist_choch_lvl_atr` | 0.04923 |
| 19 | `gmm4_p2` | 0.04800 |
| 20 | `bars_since_prev_choch` | 0.04771 |

#### Finalist set of the sub-family: every rule-list / scorecard form, judged by its own nested CPCV 5th percentile and `harness.go_no_go` with cpcv, pbo, dsr, spa_p, boot, columns and (for the finalist) the null-tape checks filled

| sub-family | form | nested OOF id | kept share | diff | diff top-1% off | control pct | sign blocks | CPCV p5 | CPCV median | fidelity | DSR p | boot 90% CI of diff | go/no-go items failed | failing items |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | dt3 (tree rules at the nested tau) | `6087330066520d4b` | 0.9600 | 63.63 | -162.14 | 94.8 | 4 | -2,965.69 | -18.31 | - | 1.0000 | [-1611.29, 1141.7] | 9 / 14 | diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | h5rules (rule list by construction) | `d0fc4ce5f0aa3614` | 0.2215 | 208.14 | 236.44 | 47.4 | 8 | -589.23 | 37.83 | - | 1.0000 | [-364.33, 750.22] | 7 / 14 | kept_mean_slip8>0, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc -> distilled rules | `4a2a1dcbb411cf89` | 1.0000 | - | - | - | - | - | - | 0.956 | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | hgbc -> distilled tree | `60ce5055a1b965e4` | 1.0000 | - | - | - | - | -1,177.48 | -1,163.91 | 0.956 | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard -> distilled rules | `d14eb10f08c1c59e` | 1.0000 | - | - | - | - | 53.58 | 826.61 | 0.998 | 1.0000 | [nan, nan] | 9 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard -> distilled tree | `e98d53dffbcf095b` | 1.0000 | - | - | - | - | -3,147.84 | 140.31 | 0.998 | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard (scorecard) | `d469afb88301a1e3` | 0.9976 | 1,922.65 | 1,705.49 | 62.7 | 1 | -744.59 | 82.48 | - | 1.0000 | [1650.23, 2174.99] | 7 / 14 | kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard_linear -> distilled rules | `ef9aa00a9b77c2e4` | 1.0000 | - | - | - | - | -130.87 | 786.89 | 1.000 | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard_linear -> distilled tree | `5e4c095fbd18996e` | 1.0000 | - | - | - | - | -641.80 | 1,345.64 | 1.000 | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |
| (II) h5_full, OUTSIDE THE FROZEN SHORTLIST | scorecard_linear (scorecard) | `fcd1323d61d635df` | 1.0000 | - | - | - | - | -2,533.43 | 1,055.94 | - | 1.0000 | [nan, nan] | 10 / 14 | diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated |

**Finalist of the sub-family** (best nested CPCV 5th percentile): **scorecard -> distilled rules** — nested OOF `d14eb10f08c1c59e`, CPCV p5 53.58, go/no-go **FAIL** (9 items failed). Frozen form: `37233722aa7f64b3` kept share 1.0000, diff -, control pct -; features used: [].

| go/no-go item | ok | value |
|---|---|---|
| kept_share>=20% | yes | 1.0 |
| kept_n>=80 | yes | 826 |
| diff>0 | no | None |
| diff_top1_removed>0 | no | None |
| kept_mean_slip8>0 | no | None |
| sign_blocks>=8/12 | no | None |
| control_pct>=95 | no | None |
| cpcv_p5_diff>0 | yes | 53.58 |
| pbo<=0.2 | no | 0.5225 |
| dsr_p<0.1 | no | 1.0 |
| spa_p<=0.10 | yes | 0.0565 |
| boot_ci_excludes_0 | no | [nan, nan] |
| null_tape:evaluated | no | not evaluable: quick dry run: null tapes not evaluated |
| no_time_proxy_columns | yes | [] |

Null tapes: not evaluable — quick dry run: null tapes not evaluated.

Drift refit: the frozen form uses none of the top-5 drifted source features (['atr14', 'atr_bps', 'hv3_ratio', 'n_rooms_alive', 'range_3h_pts']); nothing to refit.

### 5minute family multiplicity (every `gate_family/*` ledger row of the timeframe)

| rows (all labels) | rows (L1) | vectors | PBO (diff) | IS-best below zero OOS | PBO (kept mean) | SPA p (studentised) | RC p | best mean gain / session (t) | excluded from studentised | SPA p (unstudentised) | effective trials | SR variance across the family |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 532 | 480 | 480 | **0.5225** | 0.6297 | 0.0000 | **0.0565** | 0.0840 | 126.38 (3.762) | 286 | 0.0100 | 1.22 | 0.008038 |

Rows by family: {'gate_family/context/bag4': 1, 'gate_family/context/bag4/cpcv': 11, 'gate_family/context/bag4/decay': 1, 'gate_family/context/bag4/distill_rules': 1, 'gate_family/context/bag4/distill_rules/cpcv': 11, 'gate_family/context/bag4/distill_tree': 1, 'gate_family/context/bag4/distill_tree/cpcv': 11, 'gate_family/context/bag4/frozen_rules': 1, 'gate_family/context/bag4/robust': 7, 'gate_family/context/bag4/sens': 2, 'gate_family/context/bag4/tau': 7, 'gate_family/context/hgbc': 1, 'gate_family/context/hgbc/cpcv': 11, 'gate_family/context/hgbc/decay': 1, 'gate_family/context/hgbc/distill_rules': 1, 'gate_family/context/hgbc/distill_rules/cpcv': 11, 'gate_family/context/hgbc/distill_tree': 1, 'gate_family/context/hgbc/distill_tree/cpcv': 11, 'gate_family/context/hgbc/frozen_rules': 1, 'gate_family/context/hgbc/robust': 7, 'gate_family/context/hgbc/tau': 7, 'gate_family/context/hgbr': 1, 'gate_family/context/hgbr/cpcv': 11, 'gate_family/context/hgbr/distill_rules': 1, 'gate_family/context/hgbr/distill_rules/cpcv': 11, 'gate_family/context/hgbr/distill_tree': 1, 'gate_family/context/hgbr/distill_tree/cpcv': 11, 'gate_family/context/hgbr/frozen_rules': 1, 'gate_family/context/hgbr/robust': 7, 'gate_family/context/hgbr/tau': 8, 'gate_family/context/pt1': 1, 'gate_family/context/pt1/cpcv': 11, 'gate_family/context/pt1/frozen_rules': 1, 'gate_family/context/pt1/robust': 7, 'gate_family/context/pt2': 1, 'gate_family/context/pt2/cpcv': 11, 'gate_family/context/pt2/frozen_rules': 1, 'gate_family/context/pt2/robust': 7, 'gate_family/context/pt3': 1, 'gate_family/context/pt3/cpcv': 11, 'gate_family/context/pt3/frozen_rules': 1, 'gate_family/context/pt3/robust': 7, 'gate_family/context/scorecard': 2, 'gate_family/context/scorecard/cpcv': 22, 'gate_family/context/scorecard/decay': 2, 'gate_family/context/scorecard/distill_rules': 2, 'gate_family/context/scorecard/distill_rules/cpcv': 22, 'gate_family/context/scorecard/distill_tree': 2, 'gate_family/context/scorecard/distill_tree/cpcv': 22, 'gate_family/context/scorecard/frozen_rules': 2, 'gate_family/context/scorecard/frozen_scorecard': 2, 'gate_family/context/scorecard/robust': 14, 'gate_family/context/scorecard/tau': 14, 'gate_family/h5_full/dt3': 1, 'gate_family/h5_full/dt3/cpcv': 11, 'gate_family/h5_full/dt3/decay': 1, 'gate_family/h5_full/dt3/frozen_rules': 1, 'gate_family/h5_full/dt3/frozen_tree': 1, 'gate_family/h5_full/dt3/robust': 7, 'gate_family/h5_full/dt3/tau': 7, 'gate_family/h5_full/h5rules': 1, 'gate_family/h5_full/h5rules/cpcv': 11, 'gate_family/h5_full/h5rules/frozen_rules': 1, 'gate_family/h5_full/h5rules/robust': 7, 'gate_family/h5_full/hgbc': 1, 'gate_family/h5_full/hgbc/cpcv': 11, 'gate_family/h5_full/hgbc/decay': 1, 'gate_family/h5_full/hgbc/distill_rules': 1, 'gate_family/h5_full/hgbc/distill_rules/cpcv': 11, 'gate_family/h5_full/hgbc/distill_tree': 1, 'gate_family/h5_full/hgbc/distill_tree/cpcv': 11, 'gate_family/h5_full/hgbc/frozen_rules': 1, 'gate_family/h5_full/hgbc/robust': 7, 'gate_family/h5_full/hgbc/sens': 1, 'gate_family/h5_full/hgbc/tau': 7, 'gate_family/h5_full/scorecard': 2, 'gate_family/h5_full/scorecard/cpcv': 22, 'gate_family/h5_full/scorecard/decay': 2, 'gate_family/h5_full/scorecard/distill_rules': 2, 'gate_family/h5_full/scorecard/distill_rules/cpcv': 22, 'gate_family/h5_full/scorecard/distill_tree': 2, 'gate_family/h5_full/scorecard/distill_tree/cpcv': 22, 'gate_family/h5_full/scorecard/frozen_rules': 2, 'gate_family/h5_full/scorecard/frozen_scorecard': 2, 'gate_family/h5_full/scorecard/robust': 14, 'gate_family/h5_full/scorecard/tau': 14}

### 5minute candidate: **none** (null result)

No rule-list or scorecard form of either sub-family passes `harness.go_no_go` with every argument filled AND the null-tape certificate. The near-miss table is the finalist-set table of each sub-family above; the finalists' items:

- context / pt2 (rule list by construction): go/no-go FAIL (9 failed: diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, cpcv_p5_diff>0, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated); null tapes not evaluable: quick dry run: null tapes not evaluated.
- h5_full / scorecard -> distilled rules: go/no-go FAIL (9 failed: diff>0, diff_top1_removed>0, kept_mean_slip8>0, sign_blocks>=8/12, control_pct>=95, pbo<=0.2, dsr_p<0.1, boot_ci_excludes_0, null_tape:evaluated); null tapes not evaluable: quick dry run: null tapes not evaluated.

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
| context | hgbr | oof12 | 18.8 | 404.1 |
| context | hgbr | cpcv | 130.0 | 402.8 |
| context | hgbr | frozen | 2.4 | - |
| context | hgbr | robust | 44.3 | - |
| context | pt1 | oof12 | 2.8 | 402.2 |
| context | pt1 | cpcv | 23.0 | 402.2 |
| context | pt1 | frozen | 0.0 | - |
| context | pt1 | robust | 1.6 | - |
| context | pt2 | oof12 | 2.1 | 404.9 |
| context | pt2 | cpcv | 23.3 | 404.6 |
| context | pt2 | frozen | 2.1 | - |
| context | pt2 | robust | 1.6 | - |
| context | pt3 | oof12 | 2.2 | 404.9 |
| context | pt3 | cpcv | 16.6 | 404.5 |
| context | pt3 | frozen | 2.4 | - |
| context | pt3 | robust | 2.0 | - |
| context | scorecard | oof12 | 7.5 | 236.1 |
| context | scorecard | cpcv | 61.7 | 236.3 |
| context | scorecard | frozen | 0.0 | - |
| context | scorecard | robust | 2.8 | - |
| context | scorecard_linear | oof12 | 10.4 | 407.5 |
| context | scorecard_linear | cpcv | 76.3 | 414.7 |
| context | scorecard_linear | frozen | 2.6 | - |
| context | scorecard_linear | robust | 6.6 | - |
| h5_full | dt3 | oof12 | 6.0 | 249.9 |
| h5_full | dt3 | cpcv | 31.1 | 249.9 |
| h5_full | dt3 | frozen | 2.6 | - |
| h5_full | dt3 | robust | 9.4 | - |
| h5_full | h5rules | oof12 | 5.6 | 265.6 |
| h5_full | h5rules | cpcv | 35.8 | 264.2 |
| h5_full | h5rules | frozen | 1.5 | - |
| h5_full | h5rules | robust | 22.5 | - |
| h5_full | hgbc | oof12 | 112.7 | 395.8 |
| h5_full | hgbc | cpcv | 240.8 | 394.4 |
| h5_full | hgbc | frozen | 0.3 | - |
| h5_full | hgbc | robust | 136.3 | - |
| h5_full | scorecard | oof12 | 29.2 | 246.4 |
| h5_full | scorecard | cpcv | 113.7 | 248.5 |
| h5_full | scorecard | frozen | 1.2 | - |
| h5_full | scorecard | robust | 35.3 | - |
| h5_full | scorecard_linear | oof12 | 110.1 | 420.4 |
| h5_full | scorecard_linear | cpcv | 283.2 | 429.6 |
| h5_full | scorecard_linear | frozen | 3.6 | - |
| h5_full | scorecard_linear | robust | 187.0 | - |
| context | all | wall | 0 | peak 235.2 MB |
| h5_full | all | wall | 1 | peak 246.8 MB |

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
- Two processes appended to the ledger concurrently (procA: 5minute context / 5minute h5_full / minute context; procB / procB2: minute h5_full; procC / procD: the 5minute scorecard and 5minute h5_full reruns with jobs=1); every line was parsed back by finalize (ids unique per config).
- The minute / context run (procA) was killed with its agent at 14:03 UTC during the hgbc robustness stage (L0 fold 4 of 12; no ledger row of that stage had been written: the stage scores after its 12 folds). It was restarted at 15:35 UTC (procA2.nohup, GF_JOBS=4) from its checkpoints: bag4 (all stages) and hgbc (oof12, cpcv, frozen) were not rerun; hgbc robust, hgbr, pt1-pt3, scorecard and diag ran in the restart. Every model is seeded (random_state 0 / per-estimator seeds), so the job count changes timings only.
- On 5minute the scorecard's C-search was run twice: the first runs walked the C grid linearly (`c_search = linear`; results kept as `scorecard_linear.pkl`, its rows are separate trials in the ledger because `c_search` is part of the config), the rerun bisects (`bisect`, `scorecard.pkl`, the procedure every other (tf, sub) uses). Both are in the family; the bisect one is the reported scorecard.
- The L3 label is dimensionless (a t-value); its rows' slippage column is not read; the L2 labels use the engine's same-bar conventions and are checked against the L1 stop exits.
- IS/OOS: no OOS row was read; the OOS window is the published lab window (BRIEF caveat).

## 9. Files

- `FINDINGS_dry.md`
- `finalize.log`
- `finalize.py`
- `finalize_dry2.log`
- `findings_dry.json`
- `gf_lib.py`
- `labels.py`
- `labels_5minute.log`
- `labels_minute.log`
- `procA.nohup`
- `procA2.nohup`
- `procB.nohup`
- `procB2.nohup`
- `procC.nohup`
- `procD.nohup`
- `results`
- `run_5minute_context.log`
- `run_5minute_h5_full.log`
- `run_gf.py`
- `run_minute_context.log`
- `run_minute_h5_full.log`
- `results/labels_5minute.json`
- `results/labels_5minute.parquet`
- `results/labels_minute.json`
- `results/labels_minute.parquet`
- `results/oof_5minute_context.parquet`
- `results/oof_5minute_h5_full.parquet`
- `results/oof_minute_h5_full.parquet`
- `results/minute/context/bag4.json`
- `results/minute/context/bag4.pkl`
- `results/minute/context/features.json`
- `results/minute/context/hgbc.json`
- `results/minute/context/hgbc.pkl`
- `results/minute/context/hgbr.pkl`
- `results/minute/h5_full/dt3.json`
- `results/minute/h5_full/dt3.pkl`
- `results/minute/h5_full/features.json`
- `results/minute/h5_full/h5rules.json`
- `results/minute/h5_full/h5rules.pkl`
- `results/minute/h5_full/hgbc.json`
- `results/minute/h5_full/hgbc.pkl`
- `results/minute/h5_full/scorecard.json`
- `results/minute/h5_full/scorecard.pkl`
- `results/5minute/context/bag4.json`
- `results/5minute/context/bag4.pkl`
- `results/5minute/context/features.json`
- `results/5minute/context/hgbc.json`
- `results/5minute/context/hgbc.pkl`
- `results/5minute/context/hgbr.json`
- `results/5minute/context/hgbr.pkl`
- `results/5minute/context/pt1.json`
- `results/5minute/context/pt1.pkl`
- `results/5minute/context/pt2.json`
- `results/5minute/context/pt2.pkl`
- `results/5minute/context/pt3.json`
- `results/5minute/context/pt3.pkl`
- `results/5minute/context/scorecard.json`
- `results/5minute/context/scorecard.pkl`
- `results/5minute/context/scorecard_linear.json`
- `results/5minute/context/scorecard_linear.pkl`
- `results/5minute/h5_full/dt3.json`
- `results/5minute/h5_full/dt3.pkl`
- `results/5minute/h5_full/features.json`
- `results/5minute/h5_full/h5rules.json`
- `results/5minute/h5_full/h5rules.pkl`
- `results/5minute/h5_full/hgbc.json`
- `results/5minute/h5_full/hgbc.pkl`
- `results/5minute/h5_full/scorecard.json`
- `results/5minute/h5_full/scorecard.pkl`
- `results/5minute/h5_full/scorecard_linear.json`
- `results/5minute/h5_full/scorecard_linear.pkl`
