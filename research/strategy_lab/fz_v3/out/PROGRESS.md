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

## Interruption (2026-09-29 12:00-16:30 IST) and resume

- **Usage limit.** At about 12:00 IST every running agent failed with the model's usage limit: phase 1 `repair:session_stop` and
  `recheck:session_stop`, phase 1b `study:null_tapes_drift`, phase 2 `study:importance` and `study:rocket_ceiling` (the three
  workflows completed with those failures; every other agent had finished). Per the user's instruction the run paused until
  16:30 IST. The studies' own `nohup` processes kept running and all finished by 07:15 UTC: importance minute `main` / `sfi` /
  `cpcv`, the whole rocket run (`results.json`), the 1m FQI (`a_result_minute.json`), the minute drift (`drift_minute.json`), the
  session_stop repair (`results_repair.json`). What each folder still needs is listed in `STUDY_AGENT_BRIEF.md` ("Resuming").
- **Resume = the same three workflows with `resumeFromRunId`** (finished agents replay from the journal cache; the failed ones
  re-run with the same prompt and continue from the files), plus a small follow-up workflow for exit_policy (fold the 1m FQI in,
  rerun the family SPA with the revised `harness.spa`, fix the FINDINGS sentence).
- **Git incident, repaired.** The re-signing rebase (`git rebase --exec "git commit --amend --no-edit --reset-author"`) had
  stopped before its last pick, so HEAD sat detached at 06:24 with the branch still on the unsigned tip; the checkout at 06:24
  also replaced every tracked file's inode, so the running processes kept writing their logs to unlinked inodes. Fixed at 12:00
  IST: `git rebase --quit`, branch re-pointed at the re-signed HEAD, the one ledger row (2919f2bb65d22f11) and vector from the
  unpicked commit restored (append-only union, ids unique; commit 9b82a7e), and a mirror loop copied every orphaned log back from
  `/proc/<pid>/fd` until the processes exited (scratchpad `mirror_logs.sh`), so the logs on disk are complete. 43 commits since
  the base, all signed.
- **GitHub.** Pushes are refused for kiran6154/money-maker and for the user's own repositories alike ("Claude doesn't have GitHub
  access ... for your organization"); the API refuses `create_repository` (403). The user must install the Claude GitHub App on
  the account that will hold the repository, then (for a new home) create an empty private `vijayhegdebk/money-maker`; then
  `add_repo` + push + draft PR from here.

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
