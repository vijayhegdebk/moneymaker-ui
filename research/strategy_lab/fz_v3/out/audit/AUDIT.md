# FZ v3 audit index

Regenerated 2026-09-29T18:08:23 by `audit_export.py`. Every agent of the program is listed with its full transcript (every prompt, tool call, tool result and final report) and its structured verdict. The harness ledger (`ledger/trials.jsonl`, one row per configuration ever scored; `ledger/vectors/<id>_<split>.npz`, the per-session vectors behind PBO / SPA / bootstrap) and the registrations (`ledger/registrations.jsonl`, hashed pre-registrations, corrections, candidates, the OOS opening) are committed as they are. The main session's own record is the commit history of branch `research/strategy-lab-pwxiug` plus `PROGRESS.md`.

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
| recheck:session_stop | Repair | aa90baa907599adc8 | `audit/workflows/phase1/agent-aa90baa907599adc8.jsonl` | `audit/workflows/phase1/results/recheck:session_stop.json` |
| verify:ext_features:leakage | Verify | ac554d2c4c3ed57e7 | `audit/workflows/phase1/agent-ac554d2c4c3ed57e7.jsonl` | `audit/workflows/phase1/results/verify:ext_features:leakage.json` |
| verify:ext_features:arithmetic | Verify | a22f88d60d0ef5c46 | `audit/workflows/phase1/agent-a22f88d60d0ef5c46.jsonl` | `audit/workflows/phase1/results/verify:ext_features:arithmetic.json` |
| verify:llm_round0:leakage | Verify | a68236ba5b85577d1 | `audit/workflows/phase1/agent-a68236ba5b85577d1.jsonl` | `audit/workflows/phase1/results/verify:llm_round0:leakage.json` |
| verify:llm_round0:arithmetic | Verify | a4917ef41f1da6bbc | `audit/workflows/phase1/agent-a4917ef41f1da6bbc.jsonl` | `audit/workflows/phase1/results/verify:llm_round0:arithmetic.json` |
| verify:h1_gate_audit:leakage | Verify | a60acc94d12d03442 | `audit/workflows/phase1/agent-a60acc94d12d03442.jsonl` | `audit/workflows/phase1/results/verify:h1_gate_audit:leakage.json` |
| verify:h1_gate_audit:arithmetic | Verify | a7d11ab374d476750 | `audit/workflows/phase1/agent-a7d11ab374d476750.jsonl` | `audit/workflows/phase1/results/verify:h1_gate_audit:arithmetic.json` |
| verify:h2_h3_h4:leakage | Verify | a5b6d6b55f34d172c | `audit/workflows/phase1/agent-a5b6d6b55f34d172c.jsonl` | `audit/workflows/phase1/results/verify:h2_h3_h4:leakage.json` |
| verify:h2_h3_h4:arithmetic | Verify | a68ace3d21ac75d88 | `audit/workflows/phase1/agent-a68ace3d21ac75d88.jsonl` | `audit/workflows/phase1/results/verify:h2_h3_h4:arithmetic.json` |
| verify:session_stop:leakage | Verify | abfafc66be6a6d8ee | `audit/workflows/phase1/agent-abfafc66be6a6d8ee.jsonl` | `audit/workflows/phase1/results/verify:session_stop:leakage.json` |
| verify:session_stop:arithmetic | Verify | abd9f684f36ef4935 | `audit/workflows/phase1/agent-abd9f684f36ef4935.jsonl` | `audit/workflows/phase1/results/verify:session_stop:arithmetic.json` |
| repair:session_stop | Repair | aab80629544f3a62c | `audit/workflows/phase1/agent-aab80629544f3a62c.jsonl` | `audit/workflows/phase1/results/repair:session_stop.json` |
| recheck:session_stop | Repair | a3c00cd6268108ba3 | `audit/workflows/phase1/agent-a3c00cd6268108ba3.jsonl` | `audit/workflows/phase1/results/recheck:session_stop.json` |

### exit_policy_followup (run wf_82d49a78-1f8; script `None`; journal `audit/workflows/exit_policy_followup/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| followup:exit_policy | Follow-up | affacd33b0caa9890 | `audit/workflows/exit_policy_followup/agent-affacd33b0caa9890.jsonl` | `audit/workflows/exit_policy_followup/results/followup:exit_policy.json` |
| verify:exit_policy_followup:leakage | Verify | af9e6d17aac42f178 | `audit/workflows/exit_policy_followup/agent-af9e6d17aac42f178.jsonl` | `audit/workflows/exit_policy_followup/results/verify:exit_policy_followup:leakage.json` |
| verify:exit_policy_followup:arithmetic | Verify | a5f9341e21cac7c31 | `audit/workflows/exit_policy_followup/agent-a5f9341e21cac7c31.jsonl` | `audit/workflows/exit_policy_followup/results/verify:exit_policy_followup:arithmetic.json` |
| repair:exit_policy_followup | Repair | a2086570640a363fe | `audit/workflows/exit_policy_followup/agent-a2086570640a363fe.jsonl` | `audit/workflows/exit_policy_followup/results/repair:exit_policy_followup.json` |
| recheck:exit_policy_followup | Repair | a2c71169fc9472778 | `audit/workflows/exit_policy_followup/agent-a2c71169fc9472778.jsonl` | `audit/workflows/exit_policy_followup/results/recheck:exit_policy_followup.json` |

### phase1b (run wf_9d4b7078-af8; script `workflows/phase1b.js`; journal `audit/workflows/phase1b/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:exit_policy | Studies | a522174ba8150a407 | `audit/workflows/phase1b/agent-a522174ba8150a407.jsonl` | `audit/workflows/phase1b/results/study:exit_policy.json` |
| study:null_tapes_drift | Studies | a672b3f04fd37340a | `audit/workflows/phase1b/agent-a672b3f04fd37340a.jsonl` | `audit/workflows/phase1b/results/study:null_tapes_drift.json` |
| verify:exit_policy:leakage | Verify | a8dbe4e991e1efee7 | `audit/workflows/phase1b/agent-a8dbe4e991e1efee7.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:leakage.json` |
| verify:exit_policy:arithmetic | Verify | ad997f004dc62e286 | `audit/workflows/phase1b/agent-ad997f004dc62e286.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json` |
| study:null_tapes_drift | Studies | aaf4bfe3c33b6b10c | `audit/workflows/phase1b/agent-aaf4bfe3c33b6b10c.jsonl` | `audit/workflows/phase1b/results/study:null_tapes_drift.json` |
| verify:exit_policy:leakage | Verify | a23436ca2aa96f5f0 | `audit/workflows/phase1b/agent-a23436ca2aa96f5f0.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:leakage.json` |
| verify:exit_policy:arithmetic | Verify | a27323cae47775d69 | `audit/workflows/phase1b/agent-a27323cae47775d69.jsonl` | `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json` |
| verify:null_tapes_drift:leakage | Verify | a76929d834615ef18 | `audit/workflows/phase1b/agent-a76929d834615ef18.jsonl` | `audit/workflows/phase1b/results/verify:null_tapes_drift:leakage.json` |
| verify:null_tapes_drift:arithmetic | Verify | af6dd0a604185cc01 | `audit/workflows/phase1b/agent-af6dd0a604185cc01.jsonl` | `audit/workflows/phase1b/results/verify:null_tapes_drift:arithmetic.json` |
| repair:exit_policy | Repair | a587fab1b464f38bc | `audit/workflows/phase1b/agent-a587fab1b464f38bc.jsonl` | `audit/workflows/phase1b/results/repair:exit_policy.json` |
| repair:null_tapes_drift | Repair | ab48a4b1b8f1b0821 | `audit/workflows/phase1b/agent-ab48a4b1b8f1b0821.jsonl` | `audit/workflows/phase1b/results/repair:null_tapes_drift.json` |
| recheck:exit_policy | Repair | a5ad42c6954f97d05 | `audit/workflows/phase1b/agent-a5ad42c6954f97d05.jsonl` | `audit/workflows/phase1b/results/recheck:exit_policy.json` |
| recheck:null_tapes_drift | Repair | a4441d9d6ae5fd3b7 | `audit/workflows/phase1b/agent-a4441d9d6ae5fd3b7.jsonl` | `audit/workflows/phase1b/results/recheck:null_tapes_drift.json` |

### phase2 (run wf_b5100757-3f4; script `workflows/phase2.js`; journal `audit/workflows/phase2/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:importance | Studies | a7b1704339f2fe9f3 | `audit/workflows/phase2/agent-a7b1704339f2fe9f3.jsonl` | `audit/workflows/phase2/results/study:importance.json` |
| study:rocket_ceiling | Studies | a2fa1fcd6089ef4ee | `audit/workflows/phase2/agent-a2fa1fcd6089ef4ee.jsonl` | `audit/workflows/phase2/results/study:rocket_ceiling.json` |
| study:rocket_ceiling | Studies | ac30beac6ae6623fe | `audit/workflows/phase2/agent-ac30beac6ae6623fe.jsonl` | `audit/workflows/phase2/results/study:rocket_ceiling.json` |
| study:importance | Studies | a04cad7c712ee4682 | `audit/workflows/phase2/agent-a04cad7c712ee4682.jsonl` | `audit/workflows/phase2/results/study:importance.json` |
| verify:rocket_ceiling:leakage | Verify | a2917b650223bf474 | `audit/workflows/phase2/agent-a2917b650223bf474.jsonl` | `audit/workflows/phase2/results/verify:rocket_ceiling:leakage.json` |
| verify:rocket_ceiling:arithmetic | Verify | ab61d12adcdaea20f | `audit/workflows/phase2/agent-ab61d12adcdaea20f.jsonl` | `audit/workflows/phase2/results/verify:rocket_ceiling:arithmetic.json` |
| verify:importance:leakage | Verify | a5b5429fe5c53d1d3 | `audit/workflows/phase2/agent-a5b5429fe5c53d1d3.jsonl` | `audit/workflows/phase2/results/verify:importance:leakage.json` |
| verify:importance:arithmetic | Verify | a8fa567e4387bd1b6 | `audit/workflows/phase2/agent-a8fa567e4387bd1b6.jsonl` | `audit/workflows/phase2/results/verify:importance:arithmetic.json` |
| repair:importance | Repair | ab1fe3b4846387a6c | `audit/workflows/phase2/agent-ab1fe3b4846387a6c.jsonl` | `audit/workflows/phase2/results/repair:importance.json` |
| recheck:importance | Repair | a1bfa346fb0ba633d | `audit/workflows/phase2/agent-a1bfa346fb0ba633d.jsonl` | `audit/workflows/phase2/results/recheck:importance.json` |

### phase3 (run wf_e200b95a-fcc; script `workflows/phase3.js`; journal `audit/workflows/phase3/journal.jsonl`)

| agent label | phase | agentId | transcript | structured result |
|---|---|---|---|---|
| study:gate_family | Studies | a9da6406214d23e57 | `audit/workflows/phase3/agent-a9da6406214d23e57.jsonl` | `audit/workflows/phase3/results/study:gate_family.json` |
| study:llm_round1:tables | Studies | ac13a14f7946836cc | `audit/workflows/phase3/agent-ac13a14f7946836cc.jsonl` | `audit/workflows/phase3/results/study:llm_round1:tables.json` |
| study:regime_gate | Studies | af6f46909faab524e | `audit/workflows/phase3/agent-af6f46909faab524e.jsonl` | `audit/workflows/phase3/results/study:regime_gate.json` |
| study:online_learner | Studies | a798e739d44c01f7d | `audit/workflows/phase3/agent-a798e739d44c01f7d.jsonl` | `audit/workflows/phase3/results/study:online_learner.json` |
| study:llm_round1:proposer_A | Studies | a59eebb3ce714bc53 | `audit/workflows/phase3/agent-a59eebb3ce714bc53.jsonl` | `audit/workflows/phase3/results/study:llm_round1:proposer_A.json` |
| study:llm_round1:proposer_B | Studies | a02b141249199e5b4 | `audit/workflows/phase3/agent-a02b141249199e5b4.jsonl` | `audit/workflows/phase3/results/study:llm_round1:proposer_B.json` |
| verify:regime_gate:leakage | Verify | a51df8ad85732a7a3 | `audit/workflows/phase3/agent-a51df8ad85732a7a3.jsonl` | `audit/workflows/phase3/results/verify:regime_gate:leakage.json` |
| verify:regime_gate:arithmetic | Verify | a306eb006a5e69b37 | `audit/workflows/phase3/agent-a306eb006a5e69b37.jsonl` | `audit/workflows/phase3/results/verify:regime_gate:arithmetic.json` |
| study:llm_round1:score | Studies | a4968154f969af0b2 | `audit/workflows/phase3/agent-a4968154f969af0b2.jsonl` | `audit/workflows/phase3/results/study:llm_round1:score.json` |
| study:llm_round1:tables | Studies | abda61f9a3efeb746 | `audit/workflows/phase3/agent-abda61f9a3efeb746.jsonl` | `audit/workflows/phase3/results/study:llm_round1:tables.json` |
| study:gate_family | Studies | a15f18296d7b28ce5 | `audit/workflows/phase3/agent-a15f18296d7b28ce5.jsonl` | `audit/workflows/phase3/results/study:gate_family.json` |
| study:regime_gate | Studies | a8e73b6b37a3982e4 | `audit/workflows/phase3/agent-a8e73b6b37a3982e4.jsonl` | `audit/workflows/phase3/results/study:regime_gate.json` |
| study:online_learner | Studies | a836873a7ae09333b | `audit/workflows/phase3/agent-a836873a7ae09333b.jsonl` | `audit/workflows/phase3/results/study:online_learner.json` |
| study:llm_round1:proposer_A | Studies | a54ccc74db3ab32f2 | `audit/workflows/phase3/agent-a54ccc74db3ab32f2.jsonl` | `audit/workflows/phase3/results/study:llm_round1:proposer_A.json` |
| study:llm_round1:proposer_B | Studies | a75c2ab06e26e21f4 | `audit/workflows/phase3/agent-a75c2ab06e26e21f4.jsonl` | `audit/workflows/phase3/results/study:llm_round1:proposer_B.json` |
| verify:regime_gate:leakage | Verify | a5fbf1af249c0b529 | `audit/workflows/phase3/agent-a5fbf1af249c0b529.jsonl` | `audit/workflows/phase3/results/verify:regime_gate:leakage.json` |
| verify:regime_gate:arithmetic | Verify | acb8cf7b76963b60f | `audit/workflows/phase3/agent-acb8cf7b76963b60f.jsonl` | `audit/workflows/phase3/results/verify:regime_gate:arithmetic.json` |
| study:operating_point_sizing | Studies | a76837570614e1d17 | `audit/workflows/phase3/agent-a76837570614e1d17.jsonl` | `audit/workflows/phase3/results/study:operating_point_sizing.json` |
| verify:gate_family:leakage | Verify | a09cca30a8483f610 | `audit/workflows/phase3/agent-a09cca30a8483f610.jsonl` | `audit/workflows/phase3/results/verify:gate_family:leakage.json` |
| verify:gate_family:arithmetic | Verify | a53099bef0eb0c65a | `audit/workflows/phase3/agent-a53099bef0eb0c65a.jsonl` | `audit/workflows/phase3/results/verify:gate_family:arithmetic.json` |
| study:llm_round1:score | Studies | afba0937dac5549ac | `audit/workflows/phase3/agent-afba0937dac5549ac.jsonl` | `audit/workflows/phase3/results/study:llm_round1:score.json` |
| verify:operating_point_sizing:leakage | Verify | a0aa69e1e12fbbbf8 | `audit/workflows/phase3/agent-a0aa69e1e12fbbbf8.jsonl` | `audit/workflows/phase3/results/verify:operating_point_sizing:leakage.json` |
| verify:operating_point_sizing:arithmetic | Verify | a3c836f8d66123c23 | `audit/workflows/phase3/agent-a3c836f8d66123c23.jsonl` | `audit/workflows/phase3/results/verify:operating_point_sizing:arithmetic.json` |
| verify:llm_round1:leakage | Verify | a02c85e0ec8a111e2 | `audit/workflows/phase3/agent-a02c85e0ec8a111e2.jsonl` | `audit/workflows/phase3/results/verify:llm_round1:leakage.json` |
| verify:llm_round1:arithmetic | Verify | a7482c8e6f57f6323 | `audit/workflows/phase3/agent-a7482c8e6f57f6323.jsonl` | `audit/workflows/phase3/results/verify:llm_round1:arithmetic.json` |
| verify:online_learner:leakage | Verify | ab8db6f2e5530fe5d | `audit/workflows/phase3/agent-ab8db6f2e5530fe5d.jsonl` | `audit/workflows/phase3/results/verify:online_learner:leakage.json` |
| verify:online_learner:arithmetic | Verify | a68f6d77fd54504ad | `audit/workflows/phase3/agent-a68f6d77fd54504ad.jsonl` | `audit/workflows/phase3/results/verify:online_learner:arithmetic.json` |

## Studies

### exit_policy

- folder `studies/exit_policy/` (3247 files); FINDINGS: `studies/exit_policy/FINDINGS.md`; findings.json: yes
- study:exit_policy (phase1b, a522174ba8150a407): completed=False null_result=True -> `audit/workflows/phase1b/results/study:exit_policy.json`
- verify:exit_policy:leakage (phase1b, a8dbe4e991e1efee7): refuted=False severity=minor issues=4 -> `audit/workflows/phase1b/results/verify:exit_policy:leakage.json`
- verify:exit_policy:arithmetic (phase1b, ad997f004dc62e286): refuted=False severity=minor issues=6 -> `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json`
- verify:exit_policy:leakage (phase1b, a23436ca2aa96f5f0): refuted=False severity=minor issues=5 -> `audit/workflows/phase1b/results/verify:exit_policy:leakage.json`
- verify:exit_policy:arithmetic (phase1b, a27323cae47775d69): refuted=True severity=material issues=4 -> `audit/workflows/phase1b/results/verify:exit_policy:arithmetic.json`
- repair:exit_policy (phase1b, a587fab1b464f38bc): completed=True null_result=True -> `audit/workflows/phase1b/results/repair:exit_policy.json`
- recheck:exit_policy (phase1b, a5ad42c6954f97d05): refuted=False severity=minor issues=1 -> `audit/workflows/phase1b/results/recheck:exit_policy.json`

### ext_features

- folder `studies/ext_features/` (28 files); FINDINGS: `studies/ext_features/FINDINGS.md`; findings.json: yes
- study:ext_features (phase1, a3de9c19dd17bae32): completed=True null_result=False -> `audit/workflows/phase1/results/study:ext_features.json`
- verify:ext_features:leakage (phase1, a8b1339a7713e3bb6): refuted=False severity=minor issues=3 -> `audit/workflows/phase1/results/verify:ext_features:leakage.json`
- verify:ext_features:arithmetic (phase1, a8241582cdda501d3): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:ext_features:arithmetic.json`
- verify:ext_features:leakage (phase1, ac554d2c4c3ed57e7): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:ext_features:leakage.json`
- verify:ext_features:arithmetic (phase1, a22f88d60d0ef5c46): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:ext_features:arithmetic.json`

### gate_family

- folder `studies/gate_family/` (100 files); FINDINGS: `studies/gate_family/FINDINGS.md`; findings.json: yes
- study:gate_family (phase3, a9da6406214d23e57):  -> `audit/workflows/phase3/results/study:gate_family.json`
- study:gate_family (phase3, a15f18296d7b28ce5): completed=True null_result=True -> `audit/workflows/phase3/results/study:gate_family.json`
- verify:gate_family:leakage (phase3, a09cca30a8483f610): refuted=False severity=minor issues=4 -> `audit/workflows/phase3/results/verify:gate_family:leakage.json`
- verify:gate_family:arithmetic (phase3, a53099bef0eb0c65a): refuted=False severity=minor issues=4 -> `audit/workflows/phase3/results/verify:gate_family:arithmetic.json`

### h1_gate_audit

- folder `studies/h1_gate_audit/` (106 files); FINDINGS: `studies/h1_gate_audit/FINDINGS.md`; findings.json: yes
- study:h1_gate_audit (phase1, aafde4eaad2ffbc29): completed=True null_result=True -> `audit/workflows/phase1/results/study:h1_gate_audit.json`
- verify:h1_gate_audit:leakage (phase1, a9562abd73478a1c2): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:h1_gate_audit:leakage.json`
- verify:h1_gate_audit:arithmetic (phase1, ad1e0a52c0b0578e7): refuted=False severity=minor issues=6 -> `audit/workflows/phase1/results/verify:h1_gate_audit:arithmetic.json`
- verify:h1_gate_audit:leakage (phase1, a60acc94d12d03442): refuted=False severity=minor issues=6 -> `audit/workflows/phase1/results/verify:h1_gate_audit:leakage.json`
- verify:h1_gate_audit:arithmetic (phase1, a7d11ab374d476750): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:h1_gate_audit:arithmetic.json`

### h2_h3_h4

- folder `studies/h2_h3_h4/` (132 files); FINDINGS: `studies/h2_h3_h4/FINDINGS.md`; findings.json: yes
- study:h2_h3_h4 (phase1, ac8fe72c83872bfde): completed=False null_result=True -> `audit/workflows/phase1/results/study:h2_h3_h4.json`
- verify:h2_h3_h4:leakage (phase1, a60a2c993febdd7a5): refuted=True severity=material issues=4 -> `audit/workflows/phase1/results/verify:h2_h3_h4:leakage.json`
- verify:h2_h3_h4:arithmetic (phase1, a9e0abdbd7fb7639c): refuted=True severity=material issues=4 -> `audit/workflows/phase1/results/verify:h2_h3_h4:arithmetic.json`
- repair:h2_h3_h4 (phase1, a18ed65f3524cbba5): completed=True null_result=True -> `audit/workflows/phase1/results/repair:h2_h3_h4.json`
- recheck:h2_h3_h4 (phase1, aae0d01b5691fc702): refuted=False severity=minor issues=2 -> `audit/workflows/phase1/results/recheck:h2_h3_h4.json`
- verify:h2_h3_h4:leakage (phase1, a5b6d6b55f34d172c): refuted=False severity=minor issues=3 -> `audit/workflows/phase1/results/verify:h2_h3_h4:leakage.json`
- verify:h2_h3_h4:arithmetic (phase1, a68ace3d21ac75d88): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:h2_h3_h4:arithmetic.json`

### importance

- folder `studies/importance/` (102 files); FINDINGS: `studies/importance/FINDINGS.md`; findings.json: yes
- study:importance (phase2, a7b1704339f2fe9f3):  -> `audit/workflows/phase2/results/study:importance.json`
- study:importance (phase2, a04cad7c712ee4682): completed=True null_result=True -> `audit/workflows/phase2/results/study:importance.json`
- verify:importance:leakage (phase2, a5b5429fe5c53d1d3): refuted=True severity=material issues=7 -> `audit/workflows/phase2/results/verify:importance:leakage.json`
- verify:importance:arithmetic (phase2, a8fa567e4387bd1b6): refuted=True severity=material issues=6 -> `audit/workflows/phase2/results/verify:importance:arithmetic.json`
- repair:importance (phase2, ab1fe3b4846387a6c): completed=True null_result=True -> `audit/workflows/phase2/results/repair:importance.json`
- recheck:importance (phase2, a1bfa346fb0ba633d): refuted=False severity=minor issues=1 -> `audit/workflows/phase2/results/recheck:importance.json`

### llm_hypotheses

- folder `studies/llm_hypotheses/` (16 files); FINDINGS: `studies/llm_hypotheses/FINDINGS.md`; findings.json: yes
- study:llm_round0 (phase1, a3194d1a7088b8727): completed=True null_result=False -> `audit/workflows/phase1/results/study:llm_round0.json`
- verify:llm_round0:leakage (phase1, a9dd44cb0345a6e48): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:llm_round0:leakage.json`
- verify:llm_round0:arithmetic (phase1, a0dafb56d058c04fe): refuted=True severity=material issues=5 -> `audit/workflows/phase1/results/verify:llm_round0:arithmetic.json`
- repair:llm_round0 (phase1, ac2e54d13077cbbfc): completed=True null_result=True -> `audit/workflows/phase1/results/repair:llm_round0.json`
- recheck:llm_round0 (phase1, a56b18e1224f43f4d): refuted=False severity=minor issues=3 -> `audit/workflows/phase1/results/recheck:llm_round0.json`
- verify:llm_round0:leakage (phase1, a68236ba5b85577d1): refuted=False severity=minor issues=4 -> `audit/workflows/phase1/results/verify:llm_round0:leakage.json`
- verify:llm_round0:arithmetic (phase1, a4917ef41f1da6bbc): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:llm_round0:arithmetic.json`

### llm_round1

- folder `studies/llm_round1/` (33 files); FINDINGS: `studies/llm_round1/FINDINGS.md`; findings.json: yes
- study:llm_round1:tables (phase3, ac13a14f7946836cc):  -> `audit/workflows/phase3/results/study:llm_round1:tables.json`
- study:llm_round1:proposer_A (phase3, a59eebb3ce714bc53):  -> `audit/workflows/phase3/results/study:llm_round1:proposer_A.json`
- study:llm_round1:proposer_B (phase3, a02b141249199e5b4):  -> `audit/workflows/phase3/results/study:llm_round1:proposer_B.json`
- study:llm_round1:score (phase3, a4968154f969af0b2):  -> `audit/workflows/phase3/results/study:llm_round1:score.json`
- study:llm_round1:tables (phase3, abda61f9a3efeb746):  -> `audit/workflows/phase3/results/study:llm_round1:tables.json`
- study:llm_round1:proposer_A (phase3, a54ccc74db3ab32f2):  -> `audit/workflows/phase3/results/study:llm_round1:proposer_A.json`
- study:llm_round1:proposer_B (phase3, a75c2ab06e26e21f4):  -> `audit/workflows/phase3/results/study:llm_round1:proposer_B.json`
- study:llm_round1:score (phase3, afba0937dac5549ac): completed=True null_result=True -> `audit/workflows/phase3/results/study:llm_round1:score.json`
- verify:llm_round1:leakage (phase3, a02c85e0ec8a111e2): refuted=False severity=minor issues=3 -> `audit/workflows/phase3/results/verify:llm_round1:leakage.json`
- verify:llm_round1:arithmetic (phase3, a7482c8e6f57f6323): refuted=False severity=minor issues=3 -> `audit/workflows/phase3/results/verify:llm_round1:arithmetic.json`

### null_tapes_drift

- folder `studies/null_tapes_drift/` (2373 files); FINDINGS: `studies/null_tapes_drift/FINDINGS.md`; findings.json: yes
- study:null_tapes_drift (phase1b, a672b3f04fd37340a):  -> `audit/workflows/phase1b/results/study:null_tapes_drift.json`
- study:null_tapes_drift (phase1b, aaf4bfe3c33b6b10c): completed=True null_result=True -> `audit/workflows/phase1b/results/study:null_tapes_drift.json`
- verify:null_tapes_drift:leakage (phase1b, a76929d834615ef18): refuted=True severity=material issues=4 -> `audit/workflows/phase1b/results/verify:null_tapes_drift:leakage.json`
- verify:null_tapes_drift:arithmetic (phase1b, af6dd0a604185cc01): refuted=False severity=minor issues=5 -> `audit/workflows/phase1b/results/verify:null_tapes_drift:arithmetic.json`
- repair:null_tapes_drift (phase1b, ab48a4b1b8f1b0821): completed=True null_result=True -> `audit/workflows/phase1b/results/repair:null_tapes_drift.json`
- recheck:null_tapes_drift (phase1b, a4441d9d6ae5fd3b7): refuted=False severity=minor issues=2 -> `audit/workflows/phase1b/results/recheck:null_tapes_drift.json`

### online_learner

- folder `studies/online_learner/` (363 files); FINDINGS: `studies/online_learner/FINDINGS.md`; findings.json: yes
- study:online_learner (phase3, a798e739d44c01f7d):  -> `audit/workflows/phase3/results/study:online_learner.json`
- study:online_learner (phase3, a836873a7ae09333b): completed=True null_result=True -> `audit/workflows/phase3/results/study:online_learner.json`
- verify:online_learner:leakage (phase3, ab8db6f2e5530fe5d): refuted=False severity=minor issues=1 -> `audit/workflows/phase3/results/verify:online_learner:leakage.json`
- verify:online_learner:arithmetic (phase3, a68f6d77fd54504ad): refuted=False severity=minor issues=3 -> `audit/workflows/phase3/results/verify:online_learner:arithmetic.json`

### operating_point_sizing

- folder `studies/operating_point_sizing/` (15 files); FINDINGS: `studies/operating_point_sizing/FINDINGS.md`; findings.json: yes
- study:operating_point_sizing (phase3, a76837570614e1d17): completed=False null_result=True -> `audit/workflows/phase3/results/study:operating_point_sizing.json`
- verify:operating_point_sizing:leakage (phase3, a0aa69e1e12fbbbf8): refuted=False severity=minor issues=5 -> `audit/workflows/phase3/results/verify:operating_point_sizing:leakage.json`
- verify:operating_point_sizing:arithmetic (phase3, a3c836f8d66123c23): refuted=False severity=minor issues=4 -> `audit/workflows/phase3/results/verify:operating_point_sizing:arithmetic.json`

### regime_gate

- folder `studies/regime_gate/` (13 files); FINDINGS: `studies/regime_gate/FINDINGS.md`; findings.json: yes
- study:regime_gate (phase3, af6f46909faab524e): completed=True null_result=True -> `audit/workflows/phase3/results/study:regime_gate.json`
- verify:regime_gate:leakage (phase3, a51df8ad85732a7a3):  -> `audit/workflows/phase3/results/verify:regime_gate:leakage.json`
- verify:regime_gate:arithmetic (phase3, a306eb006a5e69b37):  -> `audit/workflows/phase3/results/verify:regime_gate:arithmetic.json`
- study:regime_gate (phase3, a8e73b6b37a3982e4): completed=True null_result=True -> `audit/workflows/phase3/results/study:regime_gate.json`
- verify:regime_gate:leakage (phase3, a5fbf1af249c0b529): refuted=False severity=minor issues=5 -> `audit/workflows/phase3/results/verify:regime_gate:leakage.json`
- verify:regime_gate:arithmetic (phase3, acb8cf7b76963b60f): refuted=False severity=minor issues=4 -> `audit/workflows/phase3/results/verify:regime_gate:arithmetic.json`

### rocket_ceiling

- folder `studies/rocket_ceiling/` (30 files); FINDINGS: `studies/rocket_ceiling/FINDINGS.md`; findings.json: yes
- study:rocket_ceiling (phase2, a2fa1fcd6089ef4ee):  -> `audit/workflows/phase2/results/study:rocket_ceiling.json`
- study:rocket_ceiling (phase2, ac30beac6ae6623fe): completed=True null_result=True -> `audit/workflows/phase2/results/study:rocket_ceiling.json`
- verify:rocket_ceiling:leakage (phase2, a2917b650223bf474): refuted=False severity=minor issues=5 -> `audit/workflows/phase2/results/verify:rocket_ceiling:leakage.json`
- verify:rocket_ceiling:arithmetic (phase2, ab61d12adcdaea20f): refuted=False severity=minor issues=4 -> `audit/workflows/phase2/results/verify:rocket_ceiling:arithmetic.json`

### session_stop

- folder `studies/session_stop/` (40 files); FINDINGS: `studies/session_stop/FINDINGS.md`; findings.json: yes
- study:session_stop (phase1, a07c85b4febd843d1): completed=True null_result=True -> `audit/workflows/phase1/results/study:session_stop.json`
- verify:session_stop:leakage (phase1, a80e81d450c78d68c): refuted=True severity=material issues=5 -> `audit/workflows/phase1/results/verify:session_stop:leakage.json`
- verify:session_stop:arithmetic (phase1, afe6dd09508e6eea7): refuted=False severity=minor issues=5 -> `audit/workflows/phase1/results/verify:session_stop:arithmetic.json`
- repair:session_stop (phase1, ab771f33db99f61c4):  -> `audit/workflows/phase1/results/repair:session_stop.json`
- recheck:session_stop (phase1, aa90baa907599adc8):  -> `audit/workflows/phase1/results/recheck:session_stop.json`
- verify:session_stop:leakage (phase1, abfafc66be6a6d8ee): refuted=True severity=material issues=6 -> `audit/workflows/phase1/results/verify:session_stop:leakage.json`
- verify:session_stop:arithmetic (phase1, abd9f684f36ef4935): refuted=True severity=material issues=4 -> `audit/workflows/phase1/results/verify:session_stop:arithmetic.json`
- repair:session_stop (phase1, aab80629544f3a62c): completed=True null_result=True -> `audit/workflows/phase1/results/repair:session_stop.json`
- recheck:session_stop (phase1, a3c00cd6268108ba3): refuted=False severity=none issues=0 -> `audit/workflows/phase1/results/recheck:session_stop.json`

## Other agents

- github_api_mirror_attempt: `audit/other_agents/github_api_mirror_attempt.a323ac82be404d736.jsonl`

## Left out of git (regenerable bit for bit; everything else is committed)

- `data/<tf>/bars.parquet`, `fz_card.parquet`, `swings.parquet`, `events.parquet`, `fz_visits.parquet` and `data/<tf>/trunc_*/*.parquet`: `python build/build.py --tf <tf>` (and `--truncate "2025-06-30 12:00:00"`), about 6 minutes; their `meta.json`, `compare.json` and `trunc_diff.json` are committed.
- `studies/null_tapes_drift/tapes/**` (about 720 MB of synthetic tapes with their feature tables): `python studies/null_tapes_drift/gen_tapes.py` then `run_tapes.py` with the seeds recorded in `fit_<tf>.json` / `reality.jsonl`; the per-tape results (`tape_results.jsonl`, `null_distributions.json`, `reality_check.csv`) are committed.
- `__pycache__/`.
