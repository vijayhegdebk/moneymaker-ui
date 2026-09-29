# FZ v3 audit index

Regenerated 2026-09-29T06:21:59 by `audit_export.py`. Every agent of the program is listed with its full transcript (every prompt, tool call, tool result and final report) and its structured verdict. The harness ledger (`ledger/trials.jsonl`, one row per configuration ever scored; `ledger/vectors/<id>_<split>.npz`, the per-session vectors behind PBO / SPA / bootstrap) and the registrations (`ledger/registrations.jsonl`, hashed pre-registrations, corrections, candidates, the OOS opening) are committed as they are. The main session's own record is the commit history of branch `research/strategy-lab-pwxiug` plus `PROGRESS.md`.

## Workflows

### phase1 (run wf_55c65499-a4f; script `workflows/phase1.js`; journal `audit/workflows/phase1/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:ext_features | Studies | a3de9c19dd17bae32 | `audit/workflows/phase1/agent-a3de9c19dd17bae32.jsonl` | `audit/workflows/phase1/results/study:ext_features.json` |
| study:llm_round0 | Studies | a3194d1a7088b8727 | `audit/workflows/phase1/agent-a3194d1a7088b8727.jsonl` | `audit/workflows/phase1/results/study:llm_round0.json` |
| study:h1_gate_audit | Studies | aafde4eaad2ffbc29 | `audit/workflows/phase1/agent-aafde4eaad2ffbc29.jsonl` | `audit/workflows/phase1/results/study:h1_gate_audit.json` |
| study:h2_h3_h4 | Studies | ac8fe72c83872bfde | `audit/workflows/phase1/agent-ac8fe72c83872bfde.jsonl` | `audit/workflows/phase1/results/study:h2_h3_h4.json` |
| study:session_stop | Studies | a07c85b4febd843d1 | `audit/workflows/phase1/agent-a07c85b4febd843d1.jsonl` | `audit/workflows/phase1/results/study:session_stop.json` |
| verify:llm_round0:leakage | Verify | a9dd44cb0345a6e48 | `audit/workflows/phase1/agent-a9dd44cb0345a6e48.jsonl` | `audit/workflows/phase1/results/verify:llm_round0:leakage.json` |
| verify:llm_round0:arithmetic | Verify | a0dafb56d058c04fe | `audit/workflows/phase1/agent-a0dafb56d058c04fe.jsonl` | `audit/workflows/phase1/results/verify:llm_round0:arithmetic.json` |
| verify:h1_gate_audit:leakage | Verify | a9562abd73478a1c2 | `audit/workflows/phase1/agent-a9562abd73478a1c2.jsonl` | `audit/workflows/phase1/results/verify:h1_gate_audit:leakage.json` |
| verify:h1_gate_audit:arithmetic | Verify | ad1e0a52c0b0578e7 | `audit/workflows/phase1/agent-ad1e0a52c0b0578e7.jsonl` | `audit/workflows/phase1/results/verify:h1_gate_audit:arithmetic.json` |
| verify:ext_features:leakage | Verify | a8b1339a7713e3bb6 | `audit/workflows/phase1/agent-a8b1339a7713e3bb6.jsonl` | `audit/workflows/phase1/results/verify:ext_features:leakage.json` |
| verify:ext_features:arithmetic | Verify | a8241582cdda501d3 | `audit/workflows/phase1/agent-a8241582cdda501d3.jsonl` | `audit/workflows/phase1/results/verify:ext_features:arithmetic.json` |
| verify:session_stop:leakage | Verify | a80e81d450c78d68c | `audit/workflows/phase1/agent-a80e81d450c78d68c.jsonl` | `audit/workflows/phase1/results/verify:session_stop:leakage.json` |
| verify:session_stop:arithmetic | Verify | afe6dd09508e6eea7 | `audit/workflows/phase1/agent-afe6dd09508e6eea7.jsonl` | `audit/workflows/phase1/results/verify:session_stop:arithmetic.json` |
| verify:h2_h3_h4:leakage | Verify | a60a2c993febdd7a5 | `audit/workflows/phase1/agent-a60a2c993febdd7a5.jsonl` | `audit/workflows/phase1/results/verify:h2_h3_h4:leakage.json` |
| verify:h2_h3_h4:arithmetic | Verify | a9e0abdbd7fb7639c | `audit/workflows/phase1/agent-a9e0abdbd7fb7639c.jsonl` | `audit/workflows/phase1/results/verify:h2_h3_h4:arithmetic.json` |
| repair:llm_round0 | Repair | ac2e54d13077cbbfc | `audit/workflows/phase1/agent-ac2e54d13077cbbfc.jsonl` | `audit/workflows/phase1/results/repair:llm_round0.json` |
| repair:session_stop | Repair | ab771f33db99f61c4 | `audit/workflows/phase1/agent-ab771f33db99f61c4.jsonl` | `audit/workflows/phase1/results/repair:session_stop.json` |
| repair:h2_h3_h4 | Repair | a18ed65f3524cbba5 | `audit/workflows/phase1/agent-a18ed65f3524cbba5.jsonl` | `audit/workflows/phase1/results/repair:h2_h3_h4.json` |
| recheck:llm_round0 | Repair | a56b18e1224f43f4d | `audit/workflows/phase1/agent-a56b18e1224f43f4d.jsonl` | `audit/workflows/phase1/results/recheck:llm_round0.json` |
| recheck:h2_h3_h4 | Repair | aae0d01b5691fc702 | `audit/workflows/phase1/agent-aae0d01b5691fc702.jsonl` | `audit/workflows/phase1/results/recheck:h2_h3_h4.json` |

### phase1b (run wf_9d4b7078-af8; script `workflows/phase1b.js`; journal `audit/workflows/phase1b/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:exit_policy | Studies | a522174ba8150a407 | `audit/workflows/phase1b/agent-a522174ba8150a407.jsonl` | `audit/workflows/phase1b/results/study:exit_policy.json` |
| study:null_tapes_drift | Studies | a672b3f04fd37340a | `audit/workflows/phase1b/agent-a672b3f04fd37340a.jsonl` | `audit/workflows/phase1b/results/study:null_tapes_drift.json` |
| verify:exit_policy:leakage | Verify | a8dbe4e991e1efee7 | `audit/workflows/phase1b/agent-a8dbe4e991e1efee7.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:leakage.json` |
| verify:exit_policy:arithmetic | Verify | ad997f004dc62e286 | `audit/workflows/phase1b/agent-ad997f004dc62e286.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json` |

### phase2 (run wf_b5100757-3f4; script `workflows/phase2.js`; journal `audit/workflows/phase2/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:importance | Studies | a7b1704339f2fe9f3 | `audit/workflows/phase2/agent-a7b1704339f2fe9f3.jsonl` | `audit/workflows/phase2/results/study:importance.json` |
| study:rocket_ceiling | Studies | a2fa1fcd6089ef4ee | `audit/workflows/phase2/agent-a2fa1fcd6089ef4ee.jsonl` | `audit/workflows/phase2/results/study:rocket_ceiling.json` |

## Studies

### exit_policy

- folder `studies/exit_policy/` (3225 files); FINDINGS: `studies/exit_policy/FINDINGS.md`; findings.json: yes
- study:exit_policy (phase1b, a522174ba8150a407): completed=False null_result=True -> `audit/workflows/phase1b/results/study:exit_policy.json`
- verify:exit_policy:leakage (phase1b, a8dbe4e991e1efee7): refuted=False severity=minor issues=4 -> `audit/workflows/phase1b/results/verify:exit_policy:leakage.json`
- verify:exit_policy:arithmetic (phase1b, ad997f004dc62e286): refuted=False severity=minor issues=6 -> `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json`

### ext_features

- folder `studies/ext_features/` (16 files); FINDINGS: `studies/ext_features/FINDINGS.md`; findings.json: yes
- study:ext_features (phase1, a3de9c19dd17bae32): completed=True null_result=False -> `audit/workflows/phase1/results/study:ext_features.json`
- verify:ext_features:leakage (phase1, a8b1339a7713e3bb6): refuted=False severity=minor issues=3 -> `audit/workflows/phase1/results/verify:ext_features:leakage.json`
- verify:ext_features:arithmetic (phase1, a8241582cdda501d3): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:ext_features:arithmetic.json`

### h1_gate_audit

- folder `studies/h1_gate_audit/` (106 files); FINDINGS: `studies/h1_gate_audit/FINDINGS.md`; findings.json: yes
- study:h1_gate_audit (phase1, aafde4eaad2ffbc29): completed=True null_result=True -> `audit/workflows/phase1/results/study:h1_gate_audit.json`
- verify:h1_gate_audit:leakage (phase1, a9562abd73478a1c2): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:h1_gate_audit:leakage.json`
- verify:h1_gate_audit:arithmetic (phase1, ad1e0a52c0b0578e7): refuted=False severity=minor issues=6 -> `audit/workflows/phase1/results/verify:h1_gate_audit:arithmetic.json`

### h2_h3_h4

- folder `studies/h2_h3_h4/` (132 files); FINDINGS: `studies/h2_h3_h4/FINDINGS.md`; findings.json: yes
- study:h2_h3_h4 (phase1, ac8fe72c83872bfde): completed=False null_result=True -> `audit/workflows/phase1/results/study:h2_h3_h4.json`
- verify:h2_h3_h4:leakage (phase1, a60a2c993febdd7a5): refuted=True severity=material issues=4 -> `audit/workflows/phase1/results/verify:h2_h3_h4:leakage.json`
- verify:h2_h3_h4:arithmetic (phase1, a9e0abdbd7fb7639c): refuted=True severity=material issues=4 -> `audit/workflows/phase1/results/verify:h2_h3_h4:arithmetic.json`
- repair:h2_h3_h4 (phase1, a18ed65f3524cbba5): completed=True null_result=True -> `audit/workflows/phase1/results/repair:h2_h3_h4.json`
- recheck:h2_h3_h4 (phase1, aae0d01b5691fc702): refuted=False severity=minor issues=2 -> `audit/workflows/phase1/results/recheck:h2_h3_h4.json`

### importance

- folder `studies/importance/` (58 files); FINDINGS: not written yet; findings.json: no
- study:importance (phase2, a7b1704339f2fe9f3):  -> `audit/workflows/phase2/results/study:importance.json`

### llm_hypotheses

- folder `studies/llm_hypotheses/` (16 files); FINDINGS: `studies/llm_hypotheses/FINDINGS.md`; findings.json: yes
- study:llm_round0 (phase1, a3194d1a7088b8727): completed=True null_result=False -> `audit/workflows/phase1/results/study:llm_round0.json`
- verify:llm_round0:leakage (phase1, a9dd44cb0345a6e48): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:llm_round0:leakage.json`
- verify:llm_round0:arithmetic (phase1, a0dafb56d058c04fe): refuted=True severity=material issues=5 -> `audit/workflows/phase1/results/verify:llm_round0:arithmetic.json`
- repair:llm_round0 (phase1, ac2e54d13077cbbfc): completed=True null_result=True -> `audit/workflows/phase1/results/repair:llm_round0.json`
- recheck:llm_round0 (phase1, a56b18e1224f43f4d): refuted=False severity=minor issues=3 -> `audit/workflows/phase1/results/recheck:llm_round0.json`

### null_tapes_drift

- folder `studies/null_tapes_drift/` (1557 files); FINDINGS: `studies/null_tapes_drift/FINDINGS.md`; findings.json: yes
- study:null_tapes_drift (phase1b, a672b3f04fd37340a):  -> `audit/workflows/phase1b/results/study:null_tapes_drift.json`

### rocket_ceiling

- folder `studies/rocket_ceiling/` (19 files); FINDINGS: not written yet; findings.json: no
- study:rocket_ceiling (phase2, a2fa1fcd6089ef4ee):  -> `audit/workflows/phase2/results/study:rocket_ceiling.json`

### session_stop

- folder `studies/session_stop/` (32 files); FINDINGS: `studies/session_stop/FINDINGS.md`; findings.json: yes
- study:session_stop (phase1, a07c85b4febd843d1): completed=True null_result=True -> `audit/workflows/phase1/results/study:session_stop.json`
- verify:session_stop:leakage (phase1, a80e81d450c78d68c): refuted=True severity=material issues=5 -> `audit/workflows/phase1/results/verify:session_stop:leakage.json`
- verify:session_stop:arithmetic (phase1, afe6dd09508e6eea7): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:session_stop:arithmetic.json`
- repair:session_stop (phase1, ab771f33db99f61c4):  -> `audit/workflows/phase1/results/repair:session_stop.json`

## Other agents

- github_api_mirror_attempt: `audit/other_agents/github_api_mirror_attempt.a323ac82be404d736.jsonl`

## Left out of git (regenerable bit for bit; everything else is committed)

- `data/<tf>/bars.parquet`, `fz_card.parquet`, `swings.parquet`, `events.parquet`, `fz_visits.parquet` and `data/<tf>/trunc_*/*.parquet`: `python build/build.py --tf <tf>` (and `--truncate "2025-06-30 12:00:00"`), about 6 minutes; their `meta.json`, `compare.json` and `trunc_diff.json` are committed.
- `studies/null_tapes_drift/tapes/**` (about 720 MB of synthetic tapes with their feature tables): `python studies/null_tapes_drift/gen_tapes.py` then `run_tapes.py` with the seeds recorded in `fit_<tf>.json` / `reality.jsonl`; the per-tape results (`tape_results.jsonl`, `null_distributions.json`, `reality_check.csv`) are committed.
- `__pycache__/`.
