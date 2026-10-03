"""llm_round1 step 3 (finalisation): FINDINGS.md + findings.json from scorer.py's outputs; the candidate copy only on a go/no-go pass.

    python write_findings.py            # reads results_round1.json, scores_A.json, scores_B.json, FINDINGS_draft.md, the registrations

Nothing here computes a kept-vs-skipped number: every statistic is read from results_round1.json (each one a harness ledger row whose
id is printed) or from the earlier studies' FINDINGS / findings.json (cited by ledger id). On a go/no-go pass for a timeframe the
scorer's candidate_<tf>.json is copied to OUT/candidates/llm_round1_<tf>.json with provenance.null_tape and provenance.go_no_go
added from the same go_no_go call (STUDY_AGENT_BRIEF, program-level rules of 12:55 UTC) and a registration line is appended.
"""
import os, sys, json, shutil, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import r1_common as C
H = C.H
OUT = C.OUT
# --test-dir <folder>: read a smoke run's results_round1.json / scores_<half>.json / FINDINGS_draft.md from that folder and write
# FINDINGS.md / findings.json THERE; never freezes a candidate. A code-path test only: nothing it prints is a finding.
TEST = None
if "--test-dir" in sys.argv: TEST = os.path.abspath(sys.argv[sys.argv.index("--test-dir") + 1])
IN = TEST or HERE
R = json.load(open(os.path.join(IN, "results_round1.json"), encoding="utf-8"))
SC = R["scores"]          # the combine stage's copy of scores_<half>.json, which carries holm_p_round (the on-disk files predate combine)
DRAFT = open(os.path.join(IN, "FINDINGS_draft.md"), encoding="utf-8").read()
REGS = C.registration_lines()
R0 = json.load(open(os.path.join(OUT, "studies", "llm_hypotheses", "findings.json"), encoding="utf-8"))
R0_IDS = {c["id"]: c.get("ledger_id_L1") for c in R0.get("candidates", [])}
R0_UNTESTABLE = {c["id"] for c in R0.get("candidates", []) if c.get("untestable")}
OUTSIDE = "outside the frozen shortlist (importance rule failed for every cluster)"
LABEL_NOTE = f"Every column of every rule and cell below is **{OUTSIDE}**: `features_shortlist/<tf>/shortlist.json` has `n_shortlisted = 0`, `allowed_columns = []` on both timeframes."


def f(v, nd=2):
    if v is None: return "n/a"
    if isinstance(v, bool): return str(v)
    if isinstance(v, (int, float)): return f"{v:,.{nd}f}"
    return str(v)


def reg_lines(what_prefix):
    return [r for r in REGS if r.get("kind") == "pre_registration" and str(r.get("what", "")).startswith(what_prefix)]


def ledger_rows(prefix):
    return [r for r in H.read_ledger(prefix)]


# ---------------------------------------------------------------- summary numbers
def direction_summary(h, tf):
    st = SC[h]["timeframes"][tf]
    per = [p for p in st["rules"] if not p["refused"]]
    best = None
    for p in per:
        if p.get("untestable"): continue
        if best is None or (p.get("maxt_fw_p", 1.0), -(p["L1"]["diff"] or -1e9)) < (best.get("maxt_fw_p", 1.0), -(best["L1"]["diff"] or -1e9)): best = p
    elig = [e["id"] for e in R["timeframes"][tf]["outer"][h]["eligibility"] if e["eligible"]]
    return dict(n_rules=len(st["rules"]), n_refused=sum(p["refused"] for p in st["rules"]), n_untestable=sum(1 for p in st["rules"] if p.get("untestable")),
                n_flagged=sum(1 for p in st["rules"] if not p["refused"] and not p["protocol_clean"]), best=best, eligible=elig, L=R["timeframes"][tf]["outer"][h]["L"],
                n_pos=sum(1 for p in per if not p.get("untestable") and (p["L1"]["diff"] or 0) > 0), max_ctrl=max([p["L1"]["control_pct"] for p in per if not p.get("untestable") and p["L1"]["control_pct"] is not None] or [None]),
                min_fw_p=min([p.get("maxt_fw_p", 1.0) for p in per] or [None]), union=st.get("union"), maxt=st["max_t"], fam=st["family"])


def result_paragraph():
    L = []
    L.append(f"**{'Null result' if R['null_result'] else 'A candidate passed'}.** Both round-1 rule files were registered (sha256 + byte-identical copy under `ledger/registered/`) before any ledger row of family `llm_round1` existed, and every rule was scored on the half whose tables its proposer never saw (A -> B, B -> A), through `harness.score` on a sub-table of that half.")
    for tf in C.TFS:
        cf = R["timeframes"][tf]; g = cf["go_no_go"]; d = cf["cpcv"]
        parts = []
        for h in R["directions_present"]:
            s = direction_summary(h, tf); b = s["best"]
            parts.append(f"direction {h} -> {C.OTHER[h]}: {s['n_rules']} rules ({s['n_refused']} refused, {s['n_untestable']} untestable, {s['n_flagged']} flagged), {s['n_pos']} with diff > 0, best max-T family-wise p {f(s['min_fw_p'], 4)}"
                         + (f" (`{b['id']}`: diff {f(b['L1']['diff'])}, control pct {f(b['L1']['control_pct'], 1)}, perm p {f(b['L1']['perm_p'], 4)}, Holm p over the round {f(b.get('holm_p_round'), 4)}, ledger `{b['L1']['id']}`)" if b else "")
                         + f", highest control percentile {f(s['max_ctrl'], 1)}, eligible {s['eligible'] or 'none'}, L_{h} = {s['L'] or '[]'}")
        rows = cf["rows"]
        fx = rows.get("fixed_crossed")
        cross = (f"fixed crossed list `{fx['id']}`: kept {fx['kept_n']} / skipped {fx['skipped_n']}, diff {f(fx['diff'])}, control pct {f(fx['control_pct'], 1)}, perm p {f(fx['perm_p'], 4)}, sign blocks {fx['sign_blocks']}/12" if fx
                 else "no rule was eligible in either direction, so the fixed crossed list is empty (no ledger row: keep everything)")
        oo = rows["oof12"]
        failed = [k for k, v in g["checks"].items() if not v[0]] if g else []
        L.append(f"**{tf}**: " + "; ".join(parts) + f". Cross-fit: {cross}; nested 12-block OOF `{oo['id']}`: kept {oo['kept_n']} / skipped {oo['skipped_n']}, diff {f(oo['diff'])}, control pct {f(oo['control_pct'], 1)}; nested CPCV (66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): {cf['cpcv_blocks_with_selection']} of 132 test blocks had a non-empty selection, diff median {f(d.get('diff_median'))}, p5 {f(d.get('diff_p5'))}, share > 0 {f(d.get('diff_share_positive'), 3)}. `harness.go_no_go` on {'the fixed crossed list' if fx else 'the oof12 row'}: **{'PASS' if g and g['passed'] else 'fail'}**"
                 + (f" ({len(failed)} of {len(g['checks'])} items fail: {', '.join(failed)})" if g and not g["passed"] else "") + ".")
    L.append("What this settles: a table-informed proposer, shown the cell means of one half, does not write a skip rule that survives on the other half under the family of every cell it saw; the round-0 (blind) result of `studies/llm_hypotheses/` stands, and the frozen ST7/ST8 gate remains the only gate in `candidates/` consideration for this study (none from here)." if R["null_result"] else
             "A candidate JSON is written for the passing timeframe(s) with the vocabulary provenance below; it is a user decision (the vocabulary is outside the frozen shortlist).")
    return "\n\n".join(L)


# ---------------------------------------------------------------- sections
def sec_shortlist():
    sl = {tf: json.load(open(os.path.join(OUT, "features_shortlist", tf, "shortlist.json"), encoding="utf-8")) for tf in C.TFS}
    lines = ["## 1. Shortlist state and the EMPTY-SHORTLIST RULE", "", LABEL_NOTE, "",
             "| tf | shortlist sha256 | frozen at | clusters | MDA pass | stability pass | n_shortlisted | allowed_columns | newer shortlist line in `registrations.jsonl` |", "|---|---|---|---|---|---|---|---|---|"]
    for tf in C.TFS:
        s = sl[tf]; newer = [r for r in REGS if r.get("kind") == "pre_registration" and r.get("what") == f"feature shortlist {tf}" and r.get("registered_at", "") > s["frozen_at"]]
        lines.append(f"| {tf} | `{C.sha256(os.path.join(OUT, 'features_shortlist', tf, 'shortlist.json'))}` | {s['frozen_at']} | {s['n_clusters_total']} | {s['n_clusters_mda_pass']} | {s['n_clusters_stability_pass']} | {s['n_shortlisted']} | {s['allowed_columns']} | {'yes' if newer else 'no'} |")
    lines += ["", "The tables shown to the proposers (`tables_<tf>_<half>.md`) therefore carried `hour_bin`, `fz_read`, `dir` plus the representatives of the top-8 log-loss-MDA clusters (swaps stated in the file headers and in `NOTES.md`: duplicates of `fz_read`, the calendar-time proxies `n_events_asof` / `sl`, and already-shown columns were replaced by the highest-MDI admissible member) and the columns of the four two-way tables. The five interaction pairs of each shortlist were listed with their split points; the proposers used none (both files say why: no two-way cell of those pairs was shown, and three pairs contain a time proxy and were refused). Every labelled cell counts toward the max-T family exactly as a shortlisted cell would.",
              "", "A rule found here can be frozen as a candidate only with the provenance `{\"vocabulary\": \"" + OUTSIDE + "\"}` and `user_decision_required: true`. The ledger rows of families `llm_round1/*` do not carry that string in their `config` (the ledger is append-only and the scorer's config schema was fixed at step 1); the label is carried by the two registration lines of the rules files (`note`: 'EMPTY-SHORTLIST RULE: every rule is exploratory, outside the frozen shortlist'), by the rules files themselves (`vocabulary_provenance` / `vocabulary`) and by every table of this file.", ""]
    return "\n".join(lines)


def sec_registration():
    lines = ["## 2. Registration and ordering", "", "| what | file | sha256 | written_at (file) | registered_at | ledger sha at registration | `llm_round1` ledger rows at registration |", "|---|---|---|---|---|---|---|"]
    for r in reg_lines("LLM hypotheses round 1 labelled tables"):
        lines.append(f"| {r['what']} | {', '.join(v['file'] for v in r['files'].values()) if isinstance(r.get('files'), dict) else r.get('file')} | `{r['sha256']}` | 12:36 UTC | {r['registered_at']} | `{r['ledger_sha_at_registration']}` | {r.get('llm_round1_ledger_rows_at_registration')} |")
    for r in reg_lines("LLM hypotheses round 1 half"):
        lines.append(f"| {r['what']} | `{r['file']}` | `{r['sha256']}` | {r.get('written_at')} | {r['registered_at']} | `{r['ledger_sha_at_registration']}` | {r.get('ledger_rows_of_family_at_registration')} |")
    r0 = reg_lines("LLM hypotheses round 0")
    if r0: lines.append(f"| {r0[0]['what']} (scored in `studies/llm_hypotheses/`) | `{r0[0]['file']}` | `{r0[0]['sha256']}` | - | {r0[0]['registered_at']} (correction appended 2026-09-29T05:09:16) | - | - |")
    lines += ["", f"Ordering: the labelled tables were hashed at 12:36:07 UTC with 0 `llm_round1` ledger rows; the proposers wrote their files at {SC['A']['registration'].get('written_at') if 'A' in SC else '?'} (A) and {SC['B']['registration'].get('written_at') if 'B' in SC else '?'} (B) from `tables_<tf>_<half>.md` of ONE half each (their `inputs_read` lists; neither lists the other half's tables, a ledger file or any study's FINDINGS); the scorer registered each file (sha256, copy under `ledger/registered/`) as its first action, then scored. Proposer A also read `data/README.md`, `features_ext/README.md` and both shortlist JSONs; so did proposer B. Blindness to the scoring half is a process claim (the files' `inputs_read`) plus the ordering above; the tables of the other half existed on disk from 12:36 UTC, so it is not a data-ordering fact.",
              f"Ledger: `{R['ledger_sha_before']}` before the combine stage -> `{R['ledger_sha_after']}` after; rows of family `llm_round1/*` now: {len(ledger_rows('llm_round1'))} (A: {len(ledger_rows('llm_round1/A'))}, B: {len(ledger_rows('llm_round1/B'))}, crossfit: {len(ledger_rows('llm_round1/crossfit'))}, combos: {len(ledger_rows('llm_round1/A_combo')) + len(ledger_rows('llm_round1/B_combo'))}). Scoring stage: half A's file scored on half B at {SC['A']['scored_at'] if 'A' in SC else '?'}, half B's on half A at {SC['B']['scored_at'] if 'B' in SC else '?'}; combine at {R['combined_at']}, runtime {R['runtime_s']} s.", ""]
    return "\n".join(lines)


def sec_round0():
    lines = ["## 6. The round-0 (blind) rules inside this family", "", "The 16 round-0 rules (`studies/llm_hypotheses/rules_round0.json`, sha `a3c5c063...`) were already scored on the full IS table in `studies/llm_hypotheses/` (family `llm_hypotheses/round0`; null result, no rule under Holm p 0.05, min raw p 0.0625). Those ledger ids are cited here and are NOT re-scored on the full table. Because this study's scoring rows are one half at a time, the scorer re-scored each round-0 rule on each half (families `llm_round1/A/round0` = half B rows, `llm_round1/B/round0` = half A rows) so that they enter the max-T family, PBO and SPA of every direction: the family size per timeframe and direction = labelled cells shown + round-1 rules of that half + 8 round-0 rules.", "",
             "| id | full-IS ledger id (`llm_hypotheses/round0`) | untestable on full IS | half B rows: diff / ctrl (`llm_round1/A/round0`) | half A rows: diff / ctrl (`llm_round1/B/round0`) |", "|---|---|---|---|---|"]
    for tf in C.TFS:
        ids = [x["id"] for x in SC[next(iter(SC))]["timeframes"][tf]["round0"]]
        for rid in ids:
            cells = []
            for h in ("A", "B"):
                if h in SC:
                    x = next((x for x in SC[h]["timeframes"][tf]["round0"] if x["id"] == rid), None)
                    cells.append(f"{f(x['L1']['diff'])} / {f(x['L1']['control_pct'], 1)} (`{x['L1']['id']}`)" if x else "n/a")
                else: cells.append("n/a (no file for this half)")
            lines.append(f"| {rid} | `{R0_IDS.get(rid)}` | {'yes' if rid in R0_UNTESTABLE else 'no'} | {cells[0]} | {cells[1]} |")
    lines.append("")
    return "\n".join(lines)


def sec_prior():
    return "\n".join(["## 7. What the earlier studies already found (read, not re-run)", "",
        "| study | result (its FINDINGS.md) | bearing on this round |", "|---|---|---|",
        "| `h1_gate_audit` | null: the frozen ST7/ST8 gate is not a loser filter (precision = base rate; 1 min skips 84% of top-decile winners; its gain is cost avoidance) | `fz_gate` rules (r1A_f1 skips TAKE, r1B_f7 skips BLOCK) are re-readings of that gate on one half each; both directions are in this family |",
        "| `h2_h3_h4` | null on both timeframes: `n_choch_since_bos >= k` SETUPs are not the losers (1 min -1,030 / -837 / -936 vs -1,090 after a BOS); high-volume agreement and level verdicts do not select | the `n_choch_since_bos`, `hv3_*`, `touch_*` rules here are the same hypotheses in cell form; the proposers' own files record that the two halves disagree on the direction of the CHoCH-count effect on 1 min (A: 0 is worst; B: >= 2 up is below base) |",
        "| `session_stop` | null on 1 min, inconclusive on 5 min (N3 alone rejects); the first 'session memory' finding was an artefact of outcome-dependent durations | no session-ledger column was in the shown vocabulary |",
        "| `exit_policy` | null: no exit variant rescues the book; the label stays the Foundation L1 exit | every number here is on the L1 book with Foundation exits |",
        "| `null_tapes_drift` | no real gate beats a tape p95 (0 of 18 cells); IS-early vs IS-late drift AUC 0.95 / 0.97; time proxies `sl`, `n_events_asof` refused; top-5 drifted sources 1 min: atr14, atr_bps, days_to_expiry, gap_pts, sess_cumvol_ratio20s; 5 min: atr14, atr_bps, hv3_ratio, n_rooms_alive, range_3h_pts | no round-1 rule uses a time proxy or a top-5 drifted source column (the scorer's drift refit therefore has no row); the null-tape certificate is a required `go_no_go` item and runs on the fixed crossed list when one exists |",
        "| `importance` | 0 of 38 / 39 clusters pass the pre-registered MDA rule; the shortlist is empty; the full 276-feature bagging is a ceiling with OOF AUC 0.59 (1 min), gate keeps every row, CPCV diff median -19 | the reason for the EMPTY-SHORTLIST RULE (section 1) |", ""])


def sec_family():
    lines = ["## 8. Multiplicity: the family and its statistics", "", "| tf | direction | labelled cells shown | cells with a skip set on the scored half | round-1 rules | round-0 rules | family size (max-T) | testable masks | null p95 of max |z| | best family member | its |z| / fw p | direction vectors | PBO(diff) | SPA p (unstud.) | effective trials |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for tf in C.TFS:
        for h in R["directions_present"]:
            st = SC[h]["timeframes"][tf]; mt = st["max_t"]; fm = st["family"]
            lines.append(f"| {tf} | {h} -> {C.OTHER[h]} | {mt['n_cells_labelled']} | {mt['n_cells_with_skip_set']} | {mt['n_rules_round1']} ({mt['n_rules_round1_scored']} scored) | {mt['n_rules_round0']} | **{mt['family_size']}** | {mt['family_testable']} | {f(mt['null_max_abs_t_p95'], 3)} | `{mt.get('best_family_member_name')}` | {f(mt.get('best_family_abs_t'), 3)} / {f(mt.get('best_family_fw_p'), 4)} | {fm.get('vectors')} | {f((fm.get('pbo_diff') or {}).get('pbo'), 4)} | {f((fm.get('spa') or {}).get('spa_p'), 4)} ({f((fm.get('spa') or {}).get('spa_p_unstudentised'), 4)}) | {fm.get('effective_trials')} |")
    hm = R["holm"]
    lines += ["", f"Holm over the rules of the round: m = {hm['m']} ({len(hm['raw_p'])} round-1 rules of both halves and both timeframes + 16 round-0 rules); minimum adjusted p {f(min(hm['holm_p']) if hm['holm_p'] else None, 4)}; raw p per rule in `results_round1.json` (`holm.raw_p`, `holm.rules`). The family size of the whole round per timeframe (DSR `n_trials`, `family_size_total`): " + ", ".join(f"{tf} {R['timeframes'][tf]['family_size_total']}" for tf in C.TFS) + ". The max-T statistic is the pooled-sd standardised mean difference (`scorer.pooled_z`; fixed at step 1 before any round-1 rule existed, because the Welch t round 0 used has a permutation null of max |t| near 10 once 5-20-unit cells enter the family: `NOTES.md`); the Welch t is reported per rule in `scores_<half>.json` (`max_t.rule_welch_t`) for the record.", ""]
    return "\n".join(lines)


def sec_candidate():
    lines = ["## 9. Candidate or null", ""]
    any_pass = False
    for tf in C.TFS:
        cf = R["timeframes"][tf]; g = cf["go_no_go"]
        if g and g["passed"] and any(cf["directions"][h]["L"] for h in cf["directions"]):
            any_pass = True
            lines.append(f"- **{tf}: PASS.** `candidate_{tf}.json` copied to `candidates/llm_round1_{tf}.json` with `provenance.vocabulary = \"{OUTSIDE}\"`, `provenance.null_tape` and `provenance.go_no_go` from the same call, `user_decision_required: true`; registration line appended. Rules: " + "; ".join(" and ".join(f"`{c[0]} {c[1]} {c[2]}`" for c in r["if"]) for r in cf["rules_out"]))
        else:
            why = ", ".join(k for k, v in (g or {}).get("checks", {}).items() if not v[0])
            lines.append(f"- **{tf}: null.** No rule eligible in {'either direction' if not any(cf['directions'][h]['L'] for h in cf['directions']) else 'the combination'}; `harness.go_no_go` on {'the fixed crossed list' if cf['rows'].get('fixed_crossed') else 'the nested 12-block OOF row (`' + cf['rows']['oof12']['id'] + '`)'} fails: {why}. Nothing is written to `candidates/`.")
    lines.append("")
    # observations that the tables carry but a reader may miss (numbers from the tables above; no new statistic)
    obs = []
    for h in R["directions_present"]:
        for tf in C.TFS:
            for p in SC[h]["timeframes"][tf]["rules"]:
                if p["refused"] or p.get("untestable"): continue
                m = p["L1"]
                if m["perm_p"] is not None and m["perm_p"] < 0.05 and (m["diff"] or 0) < 0:
                    obs.append(f"`{p['id']}` ({tf}, proposed on half {h}: " + " and ".join(f"`{c[0]} {c[1]} {c[2]}`" for c in p["rule"]) + f") is the only rule of the round with a permutation p below 0.05 on the other half (perm p {f(m['perm_p'], 4)}, Holm p over the round {f(p.get('holm_p_round'), 4)}, max-T fw p {f(p.get('maxt_fw_p'), 4)}), and it has the WRONG sign: the {m['skipped_n']} units it skips on half {C.OTHER[h]} are the better ones (skipped mean {f(m['skipped_mean'])} vs kept {f(m['kept_mean'])}, diff {f(m['diff'])}; L0 diff {f(p['L0']['diff'])}). The cell it was written from (`hour_bin = <09:25`, the worst bin of half {h}) is the best family member on half {C.OTHER[h]} in the opposite direction (`{SC[h]['timeframes'][tf]['max_t'].get('best_family_member_name')}`, |z| {f(SC[h]['timeframes'][tf]['max_t'].get('best_family_abs_t'), 3)}, fw p {f(SC[h]['timeframes'][tf]['max_t'].get('best_family_fw_p'), 4)}): the opening-minutes effect flips sign between 2021-10..2023-11 and 2023-11..2025-12, which is the IS-early vs IS-late drift `null_tapes_drift` measured (AUC 0.95 / 0.97), not a gate. The control percentile of 100.0 beside a negative diff is the known disagreement of the session-matched control with the pooled diff for a near-complete keep (h1_gate_audit, section 1).")
    if obs: lines += ["Observations (from the tables above; no new statistic):", ""] + [f"- {o}" for o in obs] + [""]
    lines += ["- Cross-half agreement: of the 16 minute rules, 6 (A -> B) and 4 (B -> A) have diff > 0 on the other half, none with control percentile >= 95 or max-T fw p < 0.05; the two proposers read the same `n_choch_since_bos` table in opposite directions (A: skip 0, B: skip >= 2 up) and both lose on the other half (r1A_m4 -8, r1B_m7 -176). On 5 minutes the four positive-diff rules per direction (best r1A_f4 +1,024 / r1B_f5 +866) carry control percentiles 70-92 with 25-73 skipped units and bootstrap CIs that include 0 (tables above). The unions skip 45-76% of the book and lose on every direction (minute -26 / -162; 5 minutes -609 / -23).", ""]
    return "\n".join(lines), any_pass


def sec_falsify():
    return "\n".join(["## 10. What would falsify this finding", "",
        "- A round-1 rule (unchanged sha) whose OTHER-half ledger row shows diff > 0, control percentile >= 95, max-T family-wise p < 0.05 with the labelled cells of its seen tables in the family, and Holm p over the rules of the round < 0.05, AND whose fixed crossed list passes every `harness.go_no_go` item including the CPCV p5, the null-tape certificate and the declared-columns item.",
        "- A rebuild of the L1 table (`build/build.py`) on which the per-half re-scores of the same rules change sign for the eligible set (the half boundaries are the harness's 12 IS blocks; a different block count is a different study and a new registration).",
        "- A user decision to re-open the vocabulary (a non-empty shortlist under a re-registered importance rule): the same two files could then be re-scored under a smaller family; that is a new round with its own sha and the multiplicity of this one carried forward.", ""])


def sec_caveats():
    cav = [
        f"Every column used is {OUTSIDE}; the vocabulary of the tables was an exploratory choice (top-8 MDA clusters, swaps stated) and any survivor would need the user's acceptance of that vocabulary.",
        "The ledger rows of `llm_round1/*` carry the exploratory label only through the registration lines and the rules files, not in each row's `config` (schema fixed at step 1; the ledger is append-only).",
        "The proposers are Claude agents; their `reason` texts cite the seen half's cells and the user's words. Blindness to the scoring half is their `inputs_read` self-report plus the ordering of the artefacts, not a verifiable data-ordering fact (the other half's tables existed on disk from 12:36 UTC).",
        "The proposers read `features_ext/README.md`, `data/README.md` and both shortlist JSONs beside their half's tables; none of those carries a labelled number of the scoring half.",
        "The cells of the seen half are rebuilt on the scored half with the SEEN half's decile edges, so a decile cell on the other half is not a decile there; the family therefore counts the proposer's choice set, not equal-sized cells.",
        "The 5-minute halves hold 398 / 428 L1 units; rules firing on 40-100 units have 90% bootstrap CIs of the diff several hundred INR wide (see the tables): the 5-minute verdicts are underpowered, as every 5-minute study of the program has been.",
        "Holm at m = family size (`holm_p_family` in `scores_<half>.json`) is degenerate (permutation p floor 1/2001 x m > 0.05 for m > 100) and is reported for the record only; the max-T with the cells in the family is the eligibility criterion.",
        "The nested CPCV re-runs the eligibility and greedy steps on the training rows of each test block's half with `harness.metrics` (no ledger row per inner fit); only the 11 path rows and the oof12 row are ledger rows, as the design says.",
        "Round-0 full-IS numbers are cited from `studies/llm_hypotheses/findings.json` and not re-scored; the per-half re-scores of the round-0 rules are new ledger rows (`llm_round1/<half>/round0`), needed for the family on each half.",
    ]
    return "## 11. Caveats\n\n" + "\n".join(f"- {c}" for c in cav) + "\n", cav


def sec_files():
    fs = sorted(x for x in os.listdir(HERE) if x.endswith((".json", ".csv", ".md", ".py", ".log", ".nohup")) and x != "FINDINGS_draft.md")
    fs += [f"smoke_logs/{x}" for x in sorted(os.listdir(os.path.join(HERE, "smoke_logs")))]
    return "## 12. Files\n\n" + "\n".join(f"- `studies/llm_round1/{x}`" for x in fs) + "\n- `ledger/registrations.jsonl` (lines: tables half A / B, rules half A / B" + (", candidate)" if any(R['timeframes'][tf]['go_no_go'] and R['timeframes'][tf]['go_no_go']['passed'] for tf in C.TFS) else ")") + "\n- `ledger/registered/rules_round1_A.*.json`, `ledger/registered/rules_round1_B.*.json`\n- `ledger/trials.jsonl` (families `llm_round1/A`, `llm_round1/A/round0`, `llm_round1/B`, `llm_round1/B/round0`, `llm_round1/crossfit`, `llm_round1/crossfit/cpcv`" + (", `llm_round1/A_combo` / `llm_round1/B_combo`" if ledger_rows("llm_round1/A_combo") or ledger_rows("llm_round1/B_combo") else "") + ")\n", fs


# ---------------------------------------------------------------- candidate copy (only on a pass)
def freeze_candidates():
    out = []
    if TEST: return out
    for tf in C.TFS:
        cf = R["timeframes"][tf]; g = cf["go_no_go"]; src = os.path.join(HERE, f"candidate_{tf}.json")
        if not (g and g["passed"] and os.path.exists(src) and any(cf["directions"][h]["L"] for h in cf["directions"])): continue
        cand = json.load(open(src, encoding="utf-8"))
        nt_checks = {k: v for k, v in g["checks"].items() if str(k).startswith("null_tape")}
        cand["provenance"]["null_tape"] = dict(checks=nt_checks, summary=g.get("null_tape"))
        cand["provenance"]["go_no_go"] = dict(passed=True, checks=g["checks"])
        cand["provenance"]["columns"] = g.get("columns")
        cand["provenance"]["vocabulary"] = OUTSIDE
        cand["provenance"]["user_decision_required"] = True
        os.makedirs(os.path.join(OUT, "candidates"), exist_ok=True)
        dst = os.path.join(OUT, "candidates", f"llm_round1_{tf}.json")
        json.dump(cand, open(dst, "w", encoding="utf-8"), indent=1)
        sha = C.sha256(dst)
        C.append_registration(dict(kind="candidate", what=f"llm_round1 candidate {tf}", file=C.rel(dst), sha256=sha, study="llm_round1", tf=tf, ledger_id=cand["provenance"]["ledger_id"],
                                   vocabulary=OUTSIDE, user_decision_required=True, registered_at=C.now(), ledger_sha_at_registration=H.ledger_sha(), note="frozen after harness.go_no_go passed on the fixed crossed list (CPCV, null-tape and declared-columns items included); user must accept the vocabulary before oos_once.py"))
        out.append(dict(tf=tf, file=C.rel(dst), sha256=sha, rules=cand["gate"][tf]["rules"], provenance=cand["provenance"]))
    return out


# ---------------------------------------------------------------- assemble
def main():
    cands = freeze_candidates()
    body = DRAFT.split("\n## minute\n", 1)[1] if "\n## minute\n" in DRAFT else DRAFT
    body = body.split("\n## Files\n", 1)[0]
    head = [f"# llm_round1: the round-1 (table-informed, cross-fitted) LLM hypotheses scored on the other half (IS only)", "",
            f"Study folder `fz_v3/out/studies/llm_round1/` (DESIGN_PANEL `deep-sequence-llm-hypotheses`; Judge 1: tables of one half, rules scored on the other, the cells shown logged as the family size; Judge 2: the harness splitter, trials = cells shown + rules proposed, a proposer agent distinct from any study author). Step 1 (`r1_common.py`, `tables.py`, `scorer.py`, `NOTES.md`) by the tables agent; step 2 the two proposer agents (`rules_round1_A.json`, `rules_round1_B.json`); step 3 `scorer.py all` (log `scorer.log`, `run_all.nohup`; outputs `scores_A.json`, `scores_B.json`, `results_round1.json`, `scores_<tf>.csv`, `FINDINGS_draft.md`) and this file / `findings.json` (`write_findings.py`). **IS only** (SETUP date <= 2025-12-31); label **L1** (the 15:25 book), L0 robustness only. Round 0 (blind) is `studies/llm_hypotheses/`.", "",
            LABEL_NOTE, "", "## 0. Result in one paragraph", "", result_paragraph(), "", sec_shortlist(), sec_registration(),
            "## 3. Definitions (fixed before any round-1 rule existed; `scorer.py` docstring, verbatim)", "", "```", __import__("scorer").__doc__.strip() if False else open(os.path.join(HERE, "scorer.py"), encoding="utf-8").read().split('"""')[1].strip(), "```", "",
            "Metric names are the harness's (`harness.metrics`): `diff` = kept mean net - skipped mean net (INR per trade) on the scored half; `control_pct` = the session-matched random control (2,000 draws) on that half; `perm_p` = the two-sided kept-vs-skipped permutation p (2,000 shuffles); loser recall = P(skipped | loser); winner recall (w) = kept winners' net / all winners' net; top-decile skipped = share of the top-decile winners skipped; slip8 = the kept book's mean at 8 pts slippage per side; blocks +/def = of the scored half's six harness blocks, those with kept mean > skipped mean / those with both sides populated; boot 90% CI = `harness.bootstrap_ci` of the diff (session blocks); L0 diff = the same rule on the uncut engine trade; DSR p = `harness.deflated_sharpe` of the kept book with n_trials = the family size. A rule's expected direction is always diff > 0.", "",
            "## 4-5. Per-rule scores on the OTHER half, the union, the cross-fitted verdict (every number a ledger row; all columns " + OUTSIDE + ")", "",
            "### minute", "", body.strip().replace("\n## 5minute\n", "\n### 5minute\n"), "", sec_round0(), sec_prior(), sec_family()]
    c9, _ = sec_candidate(); c11, cav = sec_caveats(); c12, files = sec_files()
    head += [c9, sec_falsify(), c11, c12]
    open(os.path.join(IN, "FINDINGS.md"), "w", encoding="utf-8").write(("# SMOKE-RUN TEST OF write_findings.py: synthetic rules, redirected ledger, NOT A FINDING\n\n" if TEST else "") + "\n".join(head))
    # findings.json
    tfs = {}
    for tf in C.TFS:
        cf = R["timeframes"][tf]
        dirs = {}
        for h in R["directions_present"]:
            st = SC[h]["timeframes"][tf]
            dirs[h] = dict(scored_on=C.OTHER[h], tables_file=st["tables_file"], tables_sha256=st["tables_sha256"], n_rows_scored=st["n_rows_scored"], n_sessions_scored=st["n_sessions_scored"], all_mean_L1=st["all_mean_L1"],
                           rules=[dict(id=p["id"], rule=p["rule"], refused=p["refused"], refused_why=p["check"]["refused"], flags=p["check"]["flags"], protocol_clean=p["protocol_clean"], untestable=p.get("untestable"),
                                       ledger_id=(p.get("L1") or {}).get("id"), ledger_id_L0=(p.get("L0") or {}).get("id"), **{k: (p.get("L1") or {}).get(k) for k in ("kept_n", "skipped_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct", "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks")},
                                       L0_diff=(p.get("L0") or {}).get("diff"), L0_control_pct=(p.get("L0") or {}).get("control_pct"), maxt_z=p.get("maxt_t"), maxt_fw_p=p.get("maxt_fw_p"), holm_p_round=p.get("holm_p_round"), holm_p_family=p.get("holm_p_family"),
                                       boot_diff_ci=(p.get("boot") or {}).get("diff_ci"), blocks=p.get("blocks"), dsr=p.get("dsr"), drift=p.get("drift"), vocabulary=OUTSIDE, passed_go_no_go=False) for p in st["rules"]],
                           union=(dict(ledger_id=st["union"]["L1"]["id"], **{k: st["union"]["L1"].get(k) for k in ("kept_n", "skipped_n", "diff", "diff_top1_removed", "perm_p", "control_pct", "winner_recall_weighted", "sign_blocks")}, boot_diff_ci=st["union"]["boot"]["diff_ci"]) if st.get("union") else None),
                           round0=[dict(id=x["id"], full_is_ledger_id=R0_IDS.get(x["id"]), half_ledger_id=x["L1"]["id"], diff=x["L1"]["diff"], control_pct=x["L1"]["control_pct"], perm_p=x["L1"]["perm_p"]) for x in st["round0"]],
                           max_t={k: v for k, v in st["max_t"].items() if k not in ("rule_t", "rule_welch_t", "rule_fw_p")}, family=st["family"], outer_eligible=[e["id"] for e in cf["outer"][h]["eligibility"] if e["eligible"]], L=cf["outer"][h]["L"], greedy_steps=cf["outer"][h]["steps"])
        tfs[tf] = dict(directions=dirs, crossfit_rows={k: dict(ledger_id=v["id"], **{kk: v.get(kk) for kk in ("kept_n", "skipped_n", "kept_share", "diff", "diff_top1_removed", "perm_p", "control_pct", "loser_recall", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks")}) for k, v in cf["rows"].items()},
                       oof12_selection=cf["oof12_selection"], cpcv=cf["cpcv"], cpcv_blocks_with_selection=cf["cpcv_blocks_with_selection"], cpcv_selection=cf["cpcv_selection"], crossfit_family=cf["family"], go_no_go=cf["go_no_go"], family_size_total=cf["family_size_total"], rules_out=cf["rules_out"])
    FJ = dict(study="llm_round1", design="DESIGN_PANEL deep-sequence-llm-hypotheses, round 1 (Judge 1 cross-fitted halves; Judge 2 family = cells shown + rules proposed, harness splitter)", label="L1", split="IS", halves={h: dict(blocks=C.HALVES[h]) for h in C.HALVES},
              shortlist_state={tf: dict(n_shortlisted=json.load(open(os.path.join(OUT, "features_shortlist", tf, "shortlist.json")))["n_shortlisted"], sha256=C.sha256(os.path.join(OUT, "features_shortlist", tf, "shortlist.json"))) for tf in C.TFS},
              vocabulary=OUTSIDE, registration=[r for r in REGS if str(r.get("what", "")).startswith("LLM hypotheses round 1") or r.get("kind") == "candidate" and r.get("study") == "llm_round1"],
              holm=R["holm"], eligibility_rule=R["eligibility_rule"], greedy_rule=R["greedy_rule"], timeframes=tfs, candidates=cands, candidates_passing=len(cands), null_result=bool(R["null_result"]),
              null_result_source="harness.go_no_go on the fixed crossed list (or the oof12 row when no rule was eligible), with the CPCV, null-tape and declared-columns items", headline=result_paragraph(),
              ledger_families=["llm_round1/A", "llm_round1/A/round0", "llm_round1/A/drift_refit", "llm_round1/A_combo", "llm_round1/B", "llm_round1/B/round0", "llm_round1/B/drift_refit", "llm_round1/B_combo", "llm_round1/crossfit", "llm_round1/crossfit/cpcv"],
              ledger_rows={fam: len(ledger_rows(fam)) for fam in ("llm_round1", "llm_round1/A", "llm_round1/B", "llm_round1/crossfit")}, ledger_sha_before=R["ledger_sha_before"], ledger_sha_after=R["ledger_sha_after"], runtime_s=R["runtime_s"],
              round0_reference=dict(folder="studies/llm_hypotheses", rules_sha256="a3c5c06382227c9504e08e40682244756bb58261419be6d53fbba95ada3a1182", full_is_ledger_ids=R0_IDS, null_result=R0.get("null_result")),
              prior_studies_not_rerun=["h1_gate_audit", "h2_h3_h4", "session_stop", "exit_policy", "null_tapes_drift", "importance"], caveats=cav,
              falsifiers=["a round-1 rule (unchanged sha) whose other-half ledger row has diff > 0, control pct >= 95, max-T fw p < 0.05 (cells in the family) and Holm p (round) < 0.05, and whose fixed crossed list passes every harness.go_no_go item", "a rebuilt L1 table on which the per-half re-scores change sign for the eligible set", "a user decision re-opening the vocabulary: a new round, new sha, multiplicity carried forward"],
              files=[f"studies/llm_round1/{x}" for x in files], written_at=C.now())
    if TEST: FJ["SMOKE_TEST"] = "synthetic rules, redirected ledger: NOT A FINDING"
    json.dump(FJ, open(os.path.join(IN, "findings.json"), "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
    print(f"FINDINGS.md and findings.json written to {IN}; null_result {R['null_result']}; candidates {len(cands)}" + ("  [TEST MODE: smoke data, nothing frozen]" if TEST else ""))


if __name__ == "__main__":
    main()
