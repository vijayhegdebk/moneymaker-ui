# FZ v3 cloud run: progress and resume notes (written 2026-09-29 11:45 IST, session 01VHMKdbBr7QKs4ywojCNPue)

This is the memory of the run. A fresh session resumes from here: read this file, `README.md`, `STUDY_AGENT_BRIEF.md`,
`QUALITY.md`, then the `studies/*/FINDINGS.md` named below. Branch `research/strategy-lab-pwxiug`, base 39eff00 of
`research/strategy-lab`; every commit so far is local only (git push and the GitHub API both refuse with 403: the Claude GitHub
App is not installed on kiran6154/money-maker; the owner must install it at https://github.com/apps/claude/installations/select_target).

## Protocol (unchanged, pre-registered)
IS 2021-10-01..2025-12-31, OOS 2026-01-01..2026-09-25 opened once by `oos_once.py` for at most three sha-registered candidates.
Label L1 = the 15:25 intraday book (the one ST13/ST14 would trade), L0 = the engine's uncut trade (robustness). Judgement = the
kept-vs-skipped difference, session-matched random control, permutation p, winner recall, top-1%-removed, slippage-8 kept mean,
block sign test, CPCV 5th percentile, PBO, DSR, SPA, bootstrap CI (`harness.go_no_go`). Every trial is a ledger row
(`ledger/trials.jsonl`, 1,527 rows at the time of writing; `ledger/registrations.jsonl` holds the hashed pre-registrations).

## Done (verified by two adversarial refuters each, repaired once where a material issue was confirmed)

| step | where | result |
|---|---|---|
| datasets rebuilt from `fz_v3/data/` (both timeframes, one column contract, L1 label) | `build/`, `data/`, `QUALITY.md` | identical to the local build on every engine / FZ table; causality diff PASS |
| harness + pre-registration | `harness.py`, `pre_register.py`, `results/pre_registration.json` | break tests: no break inside IS, no IS/OOS boundary break; frozen ST7/ST8 fails every go/no-go item |
| lab-side feature module | `research/strategy_lab/fz_feat.py` | reproduces every study-table feature live at the SETUP bar on all 5,326 / 1,012 SETUPs |
| ext_features (FFD, BSADF, CUSUM, CSW, BOCPD, GMM/HMM/jump filtered states, novelty, window scalars) | `studies/ext_features/`, `features_ext/<tf>/ext_features.parquet` (61 columns) | truncation PASS both timeframes; refuters: minor only |
| H1 gate audit | `studies/h1_gate_audit/FINDINGS.md` | **null**: the frozen gate is not a loser filter (precision = base rate; 1m skips 84% of top-decile winners; all of its gain is cost avoidance); repair round ran the missing post-hoc variant |
| H2 / H3 / H4 | `studies/h2_h3_h4/FINDINGS.md` | **null** on both timeframes; "CHoCH, CHoCH, no BOS" SETUPs are not the losers (1m means -1,030 / -837 / -936 vs -1,090 after a BOS); high-volume agreement and level verdicts do not select; repaired + rechecked |
| session_stop | `studies/session_stop/FINDINGS.md` | **null**; the first "session memory" finding was a false positive from a mis-specified null (refuter) and was repaired |
| LLM round 0 (blind) | `studies/llm_hypotheses/` (sha a3c5c063..., copy in `ledger/registered/`) | 16 rules scored on IS: none survives Holm (min raw p 0.06); registration note corrected (blindness = process claim) |
| exit_policy (learner C grid via lab.manage, B hindsight imitation, A FQI on 5m; 1m FQI running) | `studies/exit_policy/FINDINGS.md` | no exit rescues the book: the 1m nested pick is Foundation's own stop with no target / trail, +87 INR/trade vs Foundation, still -923/trade; refuters minor; follow-up needed (task below) |
| null_tapes_drift | `studies/null_tapes_drift/FINDINGS.md`, `tapes.py`, `null_distributions.json`, `drift.json` | complete; refuters running |
| harness fix | `harness.spa` | near-degenerate candidates excluded from the studentised family (min active sessions); White's unstudentised statistic reported too |

## Running at the time of writing
- Workflow phase 1 (`workflows/phase1.js`, run wf_55c65499-a4f): rechecks of h2_h3_h4, repairs of session_stop and h1 in progress.
- Workflow phase 1b (`workflows/phase1b.js`, run wf_9d4b7078-af8): null_tapes_drift verification.
- Workflow phase 2 (`workflows/phase2.js`, run wf_b5100757-3f4): `studies/importance/` (clustered MDA, the frozen <= 8-cluster
  shortlist -> `features_shortlist/<tf>/shortlist.json` + a registration line) and `studies/rocket_ceiling/` (1m, 2,000 kernels;
  the purged 12-block gains are ~+0.003 AUC, far below the 0.03 stop; its 66 CPCV splits take ~8 min each: if it is still
  running when everything else is done, stop it and write FINDINGS from the completed splits, stating the truncation).
- `studies/exit_policy/04_a_fqi.py minute` (nohup, log `04_a_minute.log`): the 1m FQI; when it finishes run task "exit_policy
  follow-up" (fold the result into 05_evaluate / 06_findings, rerun the family SPA with the revised harness.spa, fix the FINDINGS
  sentence that says it was not run).

## Next (in order)
1. When `features_shortlist/minute/shortlist.json`, `features_shortlist/5minute/shortlist.json` and `studies/importance/FINDINGS.md`
   exist: launch `workflows/phase3.js` (Workflow tool, inline script or scriptPath): gate_family (meta-label + policy tree + H5,
   distilled rule list / scorecard, candidate frozen to `candidates/gate_family_<tf>.json` only if go/no-go passes),
   operating_point_sizing (conformal winner coverage, CRC, Pareto front for the user, slippage 3/5/8; sizing only if a gate passed,
   default "one lot or skip"), llm_round1 (cross-fitted tables A/B, two separate proposer agents, scorer with max-T over cells
   shown + rules), regime_gate (conditional on the importance verdict; 5m only), online_learner (walk-forward learn-after-each-trade
   policy with the journal, `studies/online_learner/online.py` with `run(T, cfg, rows)`; candidate `candidates/online_<tf>.json`).
2. `python oos_once.py` once, for the frozen candidates (at most three per timeframe) + the comparators -> `results/oos.json`.
3. `REPORT.md` (the trading playbook: what to take / skip by regime, time, volume, level; how to size and exit; IS and OOS numbers
   with the controls; the two caveats; what did NOT survive and why), update `QUALITY.md`, fill `docs/STRATEGY_ANALYSIS_TODO.md`
   S49 with the measured numbers (Rule 0; every unmeasured impact "Unquantified").
4. Tell the user the plan and the survivors BEFORE creating any strategy file. Then, if anything survived: `fz_learn.py` beside
   `fz.py` (entry_rule `fz_v3`: features via `fz_feat.features_at`, rule list / scorecard evaluator `fz_feat.apply_rules`, the
   online learner and its journal as an output table, deterministic replay), `strategies/strategy_13.json` / `_14.json` (list the
   folder first; 15-24 belong to the other session; every threshold / weight / hyper-parameter a sourced key; frozen ST7/ST8 `fz`
   block copied verbatim for the card), extend `tests/test_fz_parity.py` (check 7: fz_feat vs the study table) and
   `tests/test_truncation.py`, document in `FZ.md` and `research/strategy_lab/README.md`. If nothing survived: the sleeve stays a
   card; record that in S49 and REPORT.md; no strategy file.
5. Commit; push once GitHub access exists (else a git bundle of `39eff00..HEAD` in the scratchpad for the user); open the draft PR.

## Standing facts for the report
- 1m L1 book: 4,452 IS units, mean -1,010 INR/trade, 15.6% winners, costs ~1,048 per trade; 5m L1: 826 units, mean -757, 27.7%.
  The 15:25 cut removes the profitable overnight holds (S47): 5m L1 -757 vs L0 -277 per trade.
- OOS caveats: the window is the published lab window and was used by the ST9-12 exit grid; the label is the recomputed intraday
  book; the OOS mean has a standard error of ~185 (1m) / ~375 (5m) INR per trade.
- Peer sessions ("Buy only", "Trading dashboard redesign") cannot be messaged from this cloud session; they own strategies 9-12 and
  15-24 and branch `research/strategy-lab`.
