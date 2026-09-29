"""The single OOS run of the FZ v3 program (BRIEF protocol: OOS = 2026-01-01 .. 2026-09-25, opened once, by this script alone).

    python oos_once.py            # refuses to run twice (results/oos.json exists) unless --force-second-look is given, which is
                                  # recorded in the output as a second look

What it scores, for each timeframe, on the OOS rows of harness.load(tf) (label L1; L0 as one robustness table):
  raw               the Foundation book (take everything)
  frozen_st7_st8    the frozen v2 gate (fz_traded), the comparator every table carries
  candidates/*.json at most three frozen candidates across all studies (a rule list, a scorecard, an online-learner cfg), each
                    read from its frozen JSON (sha checked against ledger/registrations.jsonl) and applied exactly as the study
                    defined it: a rule list via fz_feat.apply_rules on the feature row; a scorecard via bins + integer points;
                    the online learner by continuing its IS run through OOS with online.run (learning after every closed trade,
                    as it would live)
Every gate gets harness.metrics on OOS (kept-vs-skipped difference, session-matched random control, permutation p, loser recall
/ precision, |net|-weighted winner recall, top-decile winners skipped, top-1%-removed difference, kept mean at 8 pts slippage)
and its IS numbers beside it. The two standing caveats are printed on every table (DESIGN_PANEL, Judge 1): the OOS window is
also the published lab dashboard window and was used by the ST9-12 exit grid; the label is the recomputed intraday (15:25) book.
After the scoring, the label-free IS-vs-OOS adversarial validation (post-mortem, explanatory only) is run.
"""
import os, sys, json, glob, hashlib, datetime as D, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
LAB = os.path.abspath(os.path.join(HERE, "..", "..")); sys.path.insert(0, LAB)
import numpy as np, pandas as pd
import harness as H
import fz_feat

OUT_JSON = os.path.join(HERE, "results", "oos.json")
CAVEATS = ["OOS window (2026-01-01..2026-09-25) = the published lab dashboard window; it was also used by the ST9-12 exit grid (S50), so it is not pristine",
           "label = the recomputed intraday book (exit forced at the entry session's 15:25 bar); every comparator is priced on the same label",
           "the OOS mean net has a standard error of roughly 185 INR/trade (1m) and 375 (5m): differences below ~500 / ~1,000 INR/trade are not decidable here"]


def sha256(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()


def registered_shas():
    p = os.path.join(H.LEDGER, "registrations.jsonl")
    out = {}
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            try: d = json.loads(ln)
            except Exception: continue
            if d.get("sha256"): out[d["sha256"]] = d
    return out


def rule_list_mask(T, rules, default="take"):
    rows = T.F.to_dict("records")
    keep = np.zeros(T.n, dtype=bool)
    for i, row in enumerate(rows):
        dec, _ = fz_feat.apply_rules(rules, row, default=default)
        keep[i] = dec == "take"
    return keep


def scorecard_mask(T, sc):
    """bins: {feature: [cut points ascending]}, points: {feature: [ints, one per bin]}, skip_if_score_below: s."""
    score = np.zeros(T.n)
    for f, cuts in sc["bins"].items():
        x = pd.to_numeric(T.F[f], errors="coerce").to_numpy(dtype=float)
        b = np.searchsorted(np.asarray(cuts, dtype=float), x, side="right")
        pts = np.asarray(sc["points"][f], dtype=float)
        v = pts[np.clip(b, 0, len(pts) - 1)]
        v[np.isnan(x)] = sc.get("missing_points", {}).get(f, 0.0)
        score += v
    return score >= sc["skip_if_score_below"]


def online_mask(T, cand):
    spec = importlib.util.spec_from_file_location("online", os.path.join(HERE, "studies", "online_learner", "online.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    order = np.argsort(T.setup_i)                      # IS then OOS, strictly in time order; the learner reads nothing ahead
    decisions, journal, states = mod.run(T, cand["cfg"], order)
    keep = np.zeros(T.n, dtype=bool)
    for i, d in zip(order, decisions): keep[i] = bool(d.get("take") if isinstance(d, dict) else d)
    return keep, journal


def candidate_columns(c):
    """The as-of columns a frozen candidate reads (for the calendar-proxy refusal)."""
    k = c.get("kind")
    if k == "rule_list": return sorted({cond[0] for r in c["rules"] for cond in r.get("if", [])})
    if k == "scorecard": return sorted(c["scorecard"]["bins"].keys())
    return sorted(c.get("columns") or c.get("cfg", {}).get("features") or [])


def check_candidate(p, c):
    """A candidate is scored on OOS only if its frozen provenance carries the null-tape checks and a passed go/no-go, and it reads
    no calendar proxy (harness.TIME_PROXIES) - the program-level rules added 2026-09-29 12:55 UTC from the null_tapes_drift
    refuters. --accept-unchecked-candidates records the deviation instead of refusing (a user decision, written to the output)."""
    prov = c.get("provenance", {})
    problems = []
    if not prov.get("null_tape"): problems.append("provenance.null_tape missing (tapes.null_tape_check was not run on this candidate)")
    if not (prov.get("go_no_go") or {}).get("passed", False): problems.append("provenance.go_no_go.passed is not true")
    bad = [x for x in candidate_columns(c) if x in H.TIME_PROXIES]
    if bad: problems.append(f"reads calendar-proxy columns {bad}")
    if problems and "--accept-unchecked-candidates" not in sys.argv:
        sys.exit(f"{p}: refused - " + "; ".join(problems) + " (run with --accept-unchecked-candidates to score it anyway, recorded as a deviation)")
    return problems


def table(T, keep, tag, split):
    rows = np.flatnonzero(T.is_mask if split == "IS" else T.oos_mask)
    return H.metrics(T, keep, rows, f"oos_once|{T.tf}|{T.label}|{split}|{tag}")


def main():
    second = "--force-second-look" in sys.argv
    if os.path.exists(OUT_JSON) and not second:
        sys.exit("results/oos.json exists: OOS has been opened once already (BRIEF protocol). --force-second-look records a second look.")
    if os.path.basename(sys.argv[0]) != "oos_once.py": sys.exit("run as oos_once.py")
    cands = sorted(glob.glob(os.path.join(HERE, "candidates", "*.json")))
    reg = registered_shas()
    out = dict(run_at=D.datetime.now().isoformat(timespec="seconds"), second_look=second, caveats=CAVEATS, candidates=[], tables={})
    if len(cands) > 6: sys.exit(f"{len(cands)} candidate files: at most three per timeframe across all studies")
    for tf in ("minute", "5minute"):
        for label in ("L1", "L0"):
            T = H.load(tf, label)
            gates = {"raw": np.ones(T.n, dtype=bool), "frozen_st7_st8": T.F.fz_traded.astype(bool).to_numpy()}
            journals = {}
            for p in cands:
                c = json.load(open(p, encoding="utf-8"))
                if c.get("timeframe", tf) != tf and tf not in os.path.basename(p): continue
                if tf not in os.path.basename(p): continue
                sh = sha256(p)
                if sh not in reg: sys.exit(f"{p}: sha {sh[:16]} is not registered in ledger/registrations.jsonl; a candidate must be frozen before OOS")
                name = os.path.basename(p)[:-5]
                kind = c.get("kind")
                deviations = check_candidate(p, c)
                if kind == "rule_list": gates[name] = rule_list_mask(T, c["rules"], c.get("default", "take"))
                elif kind == "scorecard": gates[name] = scorecard_mask(T, c["scorecard"])
                elif kind == "online": gates[name], journals[name] = online_mask(T, c)
                else: sys.exit(f"{p}: unknown candidate kind {kind!r}")
                if label == "L1": out["candidates"].append(dict(file=os.path.relpath(p, HERE), sha256=sh, kind=kind, registration=reg[sh], columns=candidate_columns(c), accepted_with_deviations=deviations))
            for name, keep in gates.items():
                key = f"{tf}/{label}/{name}"
                out["tables"][key] = dict(OOS=table(T, keep, name, "OOS"), IS=table(T, keep, name, "IS"))
                o = out["tables"][key]["OOS"]
                print(f"{key:<40} OOS kept {o['kept_n']:>4}/{o['n']:<4} kept mean {o['kept_mean']!s:>9} skipped {o['skipped_mean']!s:>9} diff {o['diff']!s:>8} "
                      f"pct {o['control_pct']!s:>5} p {o['perm_p']!s:>6} winner-net recall {o['winner_recall_weighted']}", flush=True)
            for name, j in journals.items():
                pd.DataFrame(j).to_csv(os.path.join(HERE, "results", f"oos_journal_{name}_{label}.csv"), index=False)
    # post-mortem: label-free IS-vs-OOS adversarial validation (explanatory only)
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.model_selection import cross_val_predict, GroupKFold
        from sklearn.metrics import roc_auc_score
        for tf in ("minute", "5minute"):
            T = H.load(tf); X, _ = H.design(T)
            y = T.oos_mask.astype(int)
            pr = cross_val_predict(HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05), X, y, cv=GroupKFold(5), groups=T.session, method="predict_proba")[:, 1]
            out.setdefault("drift_is_vs_oos", {})[tf] = dict(auc=round(float(roc_auc_score(y, pr)), 4), note="label-free covariate shift IS vs OOS, run after the scoring, explanatory only")
    except Exception as ex:
        out["drift_is_vs_oos"] = dict(error=str(ex))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(OUT_JSON, "w"), indent=1, default=str)
    with open(os.path.join(H.LEDGER, "registrations.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(kind="oos_opened", at=out["run_at"], second_look=second, candidates=[c["file"] for c in out["candidates"]], results="results/oos.json")) + "\n")
    print("written", OUT_JSON)


if __name__ == "__main__":
    main()
