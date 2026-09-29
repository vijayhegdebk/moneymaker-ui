"""POST-HOC (declared after the primary runs were read): the nested-CV selection with a minimum skipped share.

The pre-registered selection (largest training-fold kept-vs-skipped diff subject to the harness KEPT floors) picked, on every
table, a cell that skips a handful of rows (2 of 826 on 5 min H2; 3 of 826 on 5 min H4 in the CPCV paths): a kept floor alone
does not bound the skipped set, and a two-row skip set has an unbounded diff. This variant adds `skipped share >= 0.10` to the
eligibility inside each training fold (nothing else changes: same cells, same folds, same criterion) and is counted in the family
as one more nested-CV trial (family '<study>/nested_cv_minskip' + its 11 CPCV paths). Both variants are reported; neither is
chosen on the pooled OOF.

    python posthoc_minskip.py
"""
import os, sys, json, time, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.argv = [sys.argv[0]]
import numpy as np, pandas as pd
import h234_common as C
import harness as H
import h2_regime as H2, h3_volume as H3, h4_levels as H4

MIN_SKIP = 0.10
log = C.Log(os.path.join(HERE, "posthoc_minskip.log"))
T0 = time.time()


def h3_cells(T, tf):
    feats = pd.read_parquet(os.path.join(HERE, f"h3_{tf}_setup_hv_features.parquet"))
    f = feats.set_index("setup_i").loc[T.F.setup_i.to_numpy()].reset_index()
    sg = np.where(T.F.dir.astype(str).to_numpy() == "up", 1, -1)
    cats = {(v, N, M): H3.category(f, v, N, M, sg) for v, N, M in itertools.product(H3.VS, H3.NS, H3.MS)}
    return H3.cells_h3(cats)


if __name__ == "__main__":
    log(f"posthoc_minskip start {time.ctime()} ledger sha {H.ledger_sha()} min_skip_share {MIN_SKIP}")
    S = {}
    for tf in ("minute", "5minute"):
        for label in ("L1", "L0"):
            T = H.load(tf, label); tag = f"{tf}_{label}"
            for study, cells in (("h2", H2.cells_h2()), ("h3", h3_cells(T, tf)), ("h4", H4.cells_h4())):
                log(f"== {study} {tag}")
                res, chosen, dist, prow, cp_chosen = C.nested_cv(T, cells, study, __file__, log, min_skip_share=MIN_SKIP, suffix="_minskip")
                fam = C.family_stats(T, study, res, dist, tag + "_minskip")
                log(f"  family (incl. this row): {fam['candidates']} candidates, PBO diff {fam['pbo_diff']['pbo']}, SPA p {fam['spa']['spa_p']}, boot {fam['bootstrap_nested']['diff_ci']}, DSR p {fam['dsr_nested'].get('p')}, go {fam['go_no_go_nested']['passed']}")
                pd.DataFrame([{k: r.get(k) for k in ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "sign_blocks"]} | {"path": r["config"]["path"]} for r in prow]).to_csv(os.path.join(HERE, f"{study}_{tag}_cpcv_paths_minskip.csv"), index=False)
                S[f"{study}/{tag}"] = dict(nested={k: res.get(k) for k in C.GRID_COLS if k != "cell"} | dict(chosen_per_block=chosen), cpcv=dist, cpcv_chosen=cp_chosen, family=fam)
                C.jdump(S[f"{study}/{tag}"], os.path.join(HERE, f"posthoc_{study}_{tag}_summary.json"))
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    C.jdump(S, os.path.join(HERE, "posthoc_minskip_summary.json"))
    log(f"posthoc done in {S['run_s']}s; ledger sha {S['ledger_sha_after']}")
