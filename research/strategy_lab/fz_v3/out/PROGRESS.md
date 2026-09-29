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
| exit_policy (learner C grid via lab.manage, B hindsight imitation, A FQI both timeframes) | `studies/exit_policy/FINDINGS.md` | **null**: no exit rescues the book; the 1m nested pick is Foundation's own stop with no target / trail, +87 INR/trade vs Foundation, still -923/trade, fails SPA and top-1%-removed; the 1m FQI +37.6 (t 1.0, below Foundation in 2 of 3 folds), the 5m FQI hurts (-145). Follow-up workflow (wf_82d49a78-1f8): refuters found the family SPA still inflated by the near-benchmark variant (Foundation stop + CHoCH-against, 7 / 578 sessions active at label precision but "active" at 1e-9); repaired with label-precision vectors: studentised p 0.322 (1m) / 0.185 (5m); recheck clean. Harness fix that followed: `harness.spa` activity tolerance = 0.01 INR (`SPA_ACTIVE_TOL_INR`), which reproduces the repaired numbers from the stored vectors and changes nothing for gate candidates |
| session_stop repair (resumed) | `studies/session_stop/FINDINGS.md` | the "session memory" claim withdrawn (artifact of outcome-dependent trade duration); 1m null, 5m inconclusive (N3); recheck clean |
| null_tapes_drift (resumed, repaired) | `studies/null_tapes_drift/FINDINGS.md`, `tapes.py`, `null_distributions.json`, `drift.json` | certificate complete: 12-22 of 84 tapes had an engine lock-out (frozen protected level, no CHoCHs), flagged label-free (`tapes.tape_health`) and topped up with new seeds to 20 / 8 healthy tapes per generator; no real gate beats a tape p95 (0 of 18 cells; the frozen gate reads +150-200 INR on memory-free 5m tapes = engine mechanics); IS-early vs IS-late drift AUC 0.95 / 0.97 (level and volatility regime). Program-level gaps it raised, closed 12:55 UTC: `harness.go_no_go` now requires the null-tape checks and the candidate's columns (`harness.TIME_PROXIES` = `sl`, `n_events_asof` refused), `oos_once.py` refuses unchecked candidates; `STUDY_AGENT_BRIEF.md` tells the phase-3 agents |
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
- **GitHub.** kiran6154/money-maker still refuses pushes (the Claude GitHub App is not installed there) and the API refuses
  `create_repository`. After the user installed the app on their own account and named the target (17:15 IST), both branches were
  pushed with full history to **vijayhegdebk/moneymaker-ui** (remote `mirror`; `research/strategy-lab` at 0acda42 = the peers'
  latest, `research/strategy-lab-pwxiug` after merging that base in, merge commit f9f52d9) and the draft PR opened:
  https://github.com/vijayhegdebk/moneymaker-ui/pull/1 (base `research/strategy-lab`). Every later checkpoint is pushed there.
  User (17:30 IST): "Stop pushing to kiran6154" - the remotes are now `origin` = vijayhegdebk/moneymaker-ui (push target) and
  `upstream` = kiran6154/money-maker (fetch only, push URL disabled). **The environment resets `origin` to kiran6154 when the
  session reconnects** (seen 15:28 UTC): before every push run `git remote set-url origin https://github.com/vijayhegdebk/moneymaker-ui`.
- **Second cut-off** (session limit, ~14:05-15:20 UTC): phase 3 lost gate_family, llm_round1 (proposers + scorer),
  online_learner and the regime_gate refuters; regime_gate itself completed (null, 5 minutes: no state gate passes; the jump4
  cell's SPA gain is the within-session first-SETUP effect). Relaunched 15:30 UTC with `resumeFromRunId` wf_e200b95a-fcc; the
  hourly routine `FZ v3 hourly resume check` (trig_017kukM72FiSf5pDviLBoDy5) covers any further cut.

## Phase 2 result (17:40 IST) and phase 3 launch
- **The frozen shortlist is empty on both timeframes** (`features_shortlist/<tf>/shortlist.json`, sha 66f6e004... / 4747257f...,
  registered 11:31:33 UTC; correction lines 12:07 UTC: "frozen before the phase-3 gate studies", not "before any gate search"):
  0 of 38 / 39 clusters pass the pre-registered rule (log-loss MDA mean > std AND top-8 stability). The full 276 / 238-feature
  bagging is a ceiling: 1m OOF AUC 0.59, gate keeps every row, CPCV diff median -19; 5m AUC 0.50. Two refuters found material
  issues (the registration note, an unnamed SPA-best row, internal contradictions, dry runs outside the ledger); repaired and
  rechecked (minor left). The study itself notes the statistic's weakness: the balanced forest is mis-calibrated under weighted
  log-loss, and an AUC-drop version of the rule would pass 2 clusters on 1m (cluster 0 = the 09:15-09:25 hour bin group, cluster 13
  card_read=FIRST_PRINT); re-opening the vocabulary is a user decision (new registration). The 5m family's SPA-best row is SFI
  cluster 25 (`jump3_state`, `jump3_run`: diff +827, control 100th pct, perm p 0.078, 8/12 blocks) - handed to regime_gate.
- Rocket ceiling: null; the pre-registered stop fired (CPCV p5 of the stacked-minus-tabular AUC gain -0.0073 < 0.03); no
  distillation; refuters minor only.
- **Phase 3 launched 12:10 UTC** (`workflows/phase3.js`, run wf_e200b95a-fcc) under the EMPTY-SHORTLIST RULE written into the
  script: gate_family = (I) context-only family (hour_bin one-hot + dir) and (II) H5 as pre-registered in S49 on the full as-of
  table, labelled "outside the frozen shortlist"; llm_round1 tables = hour_bin / fz_read / dir plus the top-8 MDA cluster
  representatives as a labelled exploratory vocabulary; online_learner on the context features plus the linear learners on the
  full design as a labelled sensitivity; regime_gate on 5m with jump3 added (reason recorded); operating point / sizing as designed.
  Anything found outside the shortlist can be frozen as a candidate only with that provenance, for the user to accept or reject.

## If the usage limit cuts the run again (user, 18:30 IST: "if limit reached start after reset, store all required details and agents")
1. Everything is on disk and pushed at every checkpoint: this file, the study folders, the ledger, `audit/` (every agent's full
   transcript + verdict, regenerated by `python audit_export.py`; the phase-3 workflow is registered there as `phase3`).
2. An hourly routine ("FZ v3 hourly resume check", created 13:05 UTC) fires into this session; a firing that lands during the
   limit fails harmlessly, the first one after the reset resumes the work. Delete the routine when the program is done.
3. Resume order: (a) check the phase-3 journal (`audit/workflows/phase3/journal.jsonl` or the live one under
   `~/.claude/projects/.../subagents/workflows/wf_e200b95a-fcc/`) and the study folders `studies/gate_family`,
   `studies/operating_point_sizing`, `studies/llm_round1`, `studies/regime_gate`, `studies/online_learner` for what finished
   (their `nohup` processes keep running through a pause: `pgrep -af studies/`); (b) relaunch with
   `Workflow({scriptPath: "<OUT>/workflows/phase3.js", resumeFromRunId: "wf_e200b95a-fcc"})` - finished agents replay from the
   journal, the cut-off ones re-run with the same prompt and continue from the files (STUDY_AGENT_BRIEF.md "Resuming");
   (c) then steps 2-5 below; (d) `python audit_export.py`, commit, `git push origin research/strategy-lab-pwxiug` at each step.

## Next (in order)
1. Phase 3 running (above; run wf_e200b95a-fcc). Phases 1, 1b, 2 and the exit_policy follow-up are complete and verified.
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
