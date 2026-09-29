"""Audit export: every agent's full record into the repository (the user's audit requirement, 2026-09-29).

    python audit_export.py        # idempotent; re-run at every stage

Copies, for every FZ v3 workflow run of this session, the workflow journal and each agent's complete transcript (agent-*.jsonl:
every prompt, tool call, tool result and final report) plus its meta.json into audit/workflows/<workflow name>/, writes each
agent's structured return value to audit/workflows/<name>/results/<label>.json, copies the non-workflow agents' transcripts
(audit/other_agents/), and regenerates audit/AUDIT.md: the index from study -> folder, FINDINGS, findings.json, the agents that
worked on it (study / verify / repair / recheck) with their transcript paths and their verdicts in full. The ledger
(ledger/trials.jsonl + ledger/vectors/*.npz), the registrations, every study's scripts, logs and outputs are committed as they are;
the only artefacts left out of git are listed in AUDIT.md with the command that regenerates them bit for bit.
"""
import os, sys, json, glob, shutil, datetime as D, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SESSION = "0a664a96-cf80-54bc-be94-bfb16658dea9"
SRC = os.path.join("/root/.claude/projects/-home-user-money-maker", SESSION)
WF_SRC = os.path.join(SRC, "subagents", "workflows")
TASKS_SRC = os.path.join("/tmp/claude-0/-home-user-money-maker", SESSION, "tasks")
AUDIT = os.path.join(HERE, "audit")
WF_NAMES = {"wf_55c65499-a4f": "phase1", "wf_9d4b7078-af8": "phase1b", "wf_b5100757-3f4": "phase2",
            "wf_82d49a78-1f8": "exit_policy_followup"}   # extended as phases run (phase3 added at its launch)
OTHER_AGENTS = {"a323ac82be404d736": "github_api_mirror_attempt"}


def safe(s): return re.sub(r"[^A-Za-z0-9_.:-]+", "_", s)


def export_workflows():
    index = {}
    for wf in sorted(glob.glob(os.path.join(WF_SRC, "wf_*"))):
        wid = os.path.basename(wf)
        name = WF_NAMES.get(wid, wid)
        dst = os.path.join(AUDIT, "workflows", name); os.makedirs(os.path.join(dst, "results"), exist_ok=True)
        for f in glob.glob(os.path.join(wf, "*")):
            if os.path.isfile(f): shutil.copy2(f, os.path.join(dst, os.path.basename(f)))
        agents = {}
        journal = os.path.join(wf, "journal.jsonl")
        if os.path.exists(journal):
            for ln in open(journal, encoding="utf-8"):
                try: d = json.loads(ln)
                except Exception: continue
                aid = d.get("agentId")
                if not aid: continue
                a = agents.setdefault(aid, dict(agentId=aid, label=None, phase=None, result=None, key=d.get("key")))
                if d.get("type") == "started": a["label"], a["phase"] = d.get("label"), d.get("phase")
                if d.get("type") == "result": a["result"] = d.get("result")
        for aid, a in agents.items():
            lab = a["label"] or aid
            with open(os.path.join(dst, "results", safe(lab) + ".json"), "w", encoding="utf-8") as f:
                json.dump(dict(a, transcript=f"audit/workflows/{name}/agent-{aid}.jsonl", meta=f"audit/workflows/{name}/agent-{aid}.meta.json"), f, indent=1, default=str)
        index[name] = dict(run_id=wid, agents=agents, script=f"workflows/{name}.js" if os.path.exists(os.path.join(HERE, "workflows", name + ".js")) else None)
    return index


def export_other_agents():
    dst = os.path.join(AUDIT, "other_agents"); os.makedirs(dst, exist_ok=True)
    out = {}
    for aid, name in OTHER_AGENTS.items():
        src = os.path.join(TASKS_SRC, aid + ".output")
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dst, f"{name}.{aid}.jsonl")); out[name] = f"audit/other_agents/{name}.{aid}.jsonl"
    return out


def write_index(index, others):
    studies = sorted(d for d in glob.glob(os.path.join(HERE, "studies", "*")) if os.path.isdir(d))
    by_study = {}
    for wname, w in index.items():
        for aid, a in w["agents"].items():
            lab = a["label"] or ""
            m = re.match(r"(study|verify|repair|recheck):([^:]+)", lab)
            if not m: continue
            by_study.setdefault(m.group(2), []).append((wname, a))
    L = ["# FZ v3 audit index", "",
         f"Regenerated {D.datetime.now().isoformat(timespec='seconds')} by `audit_export.py`. Every agent of the program is listed with its full "
         "transcript (every prompt, tool call, tool result and final report) and its structured verdict. The harness ledger "
         "(`ledger/trials.jsonl`, one row per configuration ever scored; `ledger/vectors/<id>_<split>.npz`, the per-session vectors "
         "behind PBO / SPA / bootstrap) and the registrations (`ledger/registrations.jsonl`, hashed pre-registrations, corrections, "
         "candidates, the OOS opening) are committed as they are. The main session's own record is the commit history of branch "
         "`research/strategy-lab-pwxiug` plus `PROGRESS.md`.", "",
         "## Workflows", ""]
    for wname, w in index.items():
        L.append(f"### {wname} (run {w['run_id']}; script `{w['script']}`; journal `audit/workflows/{wname}/journal.jsonl`)"); L.append("")
        L.append("| agent label | phase | agentId | transcript | structured result |"); L.append("|---|---|---|---|---|")
        for aid, a in w["agents"].items():
            lab = a["label"] or "(unlabelled)"
            L.append(f"| {lab} | {a['phase'] or ''} | {aid} | `audit/workflows/{wname}/agent-{aid}.jsonl` | `audit/workflows/{wname}/results/{safe(lab)}.json` |")
        L.append("")
    L += ["## Studies", ""]
    for d in studies:
        s = os.path.basename(d)
        L.append(f"### {s}"); L.append("")
        L.append(f"- folder `studies/{s}/` ({sum(1 for _ in glob.glob(os.path.join(d, '**', '*'), recursive=True))} files); FINDINGS: "
                 f"{'`studies/' + s + '/FINDINGS.md`' if os.path.exists(os.path.join(d, 'FINDINGS.md')) else 'not written yet'}; findings.json: "
                 f"{'yes' if os.path.exists(os.path.join(d, 'findings.json')) else 'no'}")
        for wname, a in by_study.get(s, []) + by_study.get({"llm_hypotheses": "llm_round0"}.get(s, "-"), []):
            r = a.get("result")
            verdict = ""
            if isinstance(r, dict):
                if "refuted" in r: verdict = f"refuted={r.get('refuted')} severity={r.get('severity')} issues={len(r.get('issues') or [])}"
                elif "completed" in r: verdict = f"completed={r.get('completed')} null_result={r.get('null_result')}"
            L.append(f"- {a['label']} ({wname}, {a['agentId']}): {verdict} -> `audit/workflows/{wname}/results/{safe(a['label'])}.json`")
        L.append("")
    L += ["## Other agents", ""] + [f"- {k}: `{v}`" for k, v in others.items()] + ["",
          "## Left out of git (regenerable bit for bit; everything else is committed)", "",
          "- `data/<tf>/bars.parquet`, `fz_card.parquet`, `swings.parquet`, `events.parquet`, `fz_visits.parquet` and `data/<tf>/trunc_*/*.parquet`: "
          "`python build/build.py --tf <tf>` (and `--truncate \"2025-06-30 12:00:00\"`), about 6 minutes; their `meta.json`, `compare.json` and `trunc_diff.json` are committed.",
          "- `studies/null_tapes_drift/tapes/**` (about 720 MB of synthetic tapes with their feature tables): `python studies/null_tapes_drift/gen_tapes.py` then "
          "`run_tapes.py` with the seeds recorded in `fit_<tf>.json` / `reality.jsonl`; the per-tape results (`tape_results.jsonl`, `null_distributions.json`, `reality_check.csv`) are committed.",
          "- `__pycache__/`.", ""]
    with open(os.path.join(AUDIT, "AUDIT.md"), "w", encoding="utf-8") as f: f.write("\n".join(L))


if __name__ == "__main__":
    os.makedirs(AUDIT, exist_ok=True)
    idx = export_workflows(); oth = export_other_agents(); write_index(idx, oth)
    n = sum(len(w["agents"]) for w in idx.values())
    print(f"exported {len(idx)} workflows, {n} agents, {len(oth)} other agents -> {AUDIT}")
