"""POST-HOC trial (declared after h1_gate_audit.py's numbers were seen; counted in the h1 family): the as-of translation of
the diagnostic `not_block` variant. `not_block` keeps fzpost_outcome_gate != BLOCK (a post column); the as-of rule a strategy
file could carry is fz_gate != BLOCK. The two differ only where a BLOCK-as-of SETUP later became a REENTER's R5 (1 min: 11 IS
rows; 5 min: 0). Scored on both timeframes and both labels under family h1/not_block_asof, then the family statistics are
recomputed over every h1 row (h1_family_posthoc.json).

    python h1_posthoc.py
"""
import os, sys, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np
import harness as H

t0 = time.time(); out = {}
for tf in ("minute", "5minute"):
    for label in ("L1", "L0"):
        T = H.load(tf, label)
        keep = (T.F.fz_gate.astype(str) != "BLOCK").to_numpy()
        post = (T.F.fzpost_outcome_gate.astype(str) != "BLOCK").to_numpy()
        r = H.score(T, keep, "h1/not_block_asof", {"keep": "fz_gate != BLOCK", "uses_post_column": False, "post_hoc": True},
                    script=__file__, note="post-hoc as-of translation of h1/not_block (declared after the audit's numbers were seen)")
        base_loser = float((~T.win[T.is_mask]).mean())
        r["lift"] = round(r["loser_precision"] / base_loser, 3); r["go_no_go"] = H.go_no_go(r, tf)[1]
        r["rows_differing_from_not_block_IS"] = int((keep != post)[T.is_mask].sum())
        rows = [x for x in H.read_ledger("h1", tf=tf, label=label) if x["family"] != "h1/cpcv"]
        ids = list(dict.fromkeys(x["id"] for x in rows)); vecs = [H.load_vectors(i) for i in ids]
        fam = dict(candidates=len(ids), ids=ids, pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"),
                   spa=H.spa(vecs, tag=f"h1|{tf}_{label}|posthoc"), effective_trials=H.effective_trials(vecs))
        fam["spa_best_id"] = ids[fam["spa"]["best"]]
        out[f"{tf}/{label}"] = dict(not_block_asof={k: r[k] for k in ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p",
                                                                    "loser_recall", "loser_precision", "lift", "winner_recall", "winner_recall_weighted", "top_decile_winners_skipped",
                                                                    "kept_pf", "kept_mean_slip8", "sign_blocks", "rows_differing_from_not_block_IS", "go_no_go")}, family=fam)
        print(tf, label, "not_block_asof", r["id"], "kept", r["kept_n"], "diff", r["diff"], "pct", r["control_pct"], "p", r["perm_p"], "slip8", r["kept_mean_slip8"], "blocks", r["sign_blocks"],
              "| family", len(ids), "PBO(diff)", fam["pbo_diff"]["pbo"], "SPA p", fam["spa"]["spa_p"], "best", fam["spa_best_id"], flush=True)
out["ledger_sha_after"] = H.ledger_sha(); out["run_s"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "h1_family_posthoc.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print("done", out["run_s"], "s; ledger sha", out["ledger_sha_after"])
