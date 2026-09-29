"""operating_point_sizing, step 2: the CONDITIONAL sizing step (DESIGN_PANEL quant-ml-canon-bet-sizing merged with
decision-making-5-kelly-bounded-sizing; Judge 1 / Judge 2: it runs ONLY when a gate_family candidate exists in OUT/candidates/ for
the timeframe and has passed harness.go_no_go with CPCV 5th-percentile kept expectancy > 0; otherwise the verdict is written and
nothing is fitted). This script checks the precondition and writes sizing_verdict.json. It fits nothing, scores nothing and
appends no ledger row. The default verdict of the design is 'lots = 1 or skip'."""
import os, sys, json, glob, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
CAND = os.path.join(OUT, "candidates")


def candidates_for(tf):
    if not os.path.isdir(CAND): return []
    out = []
    for p in sorted(glob.glob(os.path.join(CAND, "*.json"))):
        try: j = json.load(open(p, encoding="utf-8"))
        except ValueError: continue
        t = j.get("tf") or j.get("timeframe") or (j.get("provenance") or {}).get("tf")
        if t == tf or (t is None and tf in os.path.basename(p)): out.append(dict(file=os.path.relpath(p, OUT), passed=((j.get("provenance") or {}).get("go_no_go") or {}).get("passed")))
    return out


def main():
    gf = json.load(open(os.path.join(OUT, "studies", "gate_family", "findings.json"), encoding="utf-8"))
    out = dict(study="operating_point_sizing", step="sizing (conditional)", checked_at=D.datetime.now().isoformat(timespec="seconds"),
               candidates_folder_exists=os.path.isdir(CAND), gate_family_null_result=bool(gf.get("null_result")), gate_family_candidates=gf.get("candidates"),
               timeframes={})
    for tf in ("minute", "5minute"):
        c = candidates_for(tf); passed = [x for x in c if x["passed"]]
        gfc = (gf.get("timeframes", {}).get(tf, {}) or {}).get("candidate")
        out["timeframes"][tf] = dict(candidate_files=c, gate_family_candidate=gfc,
                                     verdict=("not run: no gate passed" if not passed else "precondition met: run the sizing step"),
                                     size_block=None,
                                     detail=("No candidate JSON for this timeframe in OUT/candidates/ (the folder does not exist) and gate_family's candidate is null: "
                                             "the finalists fail harness.go_no_go (minute: 6 items incl. control_pct 21.9, PBO 0.40, SPA p 0.94, kept mean at 8 pts "
                                             "slippage -1,378, the segment-tape p95; 5minute: 11 items, CPCV p5 -434). Both judges: sizing multiplies an edge that is "
                                             "not shown to exist (raw Kelly at a 16-28% win rate is negative); it runs only after a gate passes with CPCV 5th-percentile "
                                             "kept expectancy > 0. Nothing fitted; no Platt map, payoff table, lot bins, lot-aware control or ledger row was produced. "
                                             "The design's default verdict stands: lots = 1 or skip." if not passed else None))
    json.dump(out, open(os.path.join(HERE, "sizing_verdict.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
