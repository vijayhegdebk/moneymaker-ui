"""POST-HOC (declared after the primary runs were read): the nested-CV selection with a minimum skipped share.

The pre-registered selection (largest training-fold kept-vs-skipped diff subject to the harness KEPT floors) has no floor on the
skipped set. On 5 min H2 it is degenerate: the same cell {kc=2, scope=today, W=3h, q=0.1, AND} won all 12 folds and 64-65 of the
66 CPCV training sets, skipping 2 of 826 (L1) / 2 of 832 (L0) rows, so the "nested-CV answer" for H2 on 5 min is the raw book
minus two trades. On the other tables the chosen cells skip real shares of the training rows (1 min H2 1-9 %, H3 2-25 %, H4 7-39 %),
apart from three folds that chose {prot, broke} (3 rows): two of 12 on 1 min H4 L1, one of 12 on 5 min H4 L1 (FINDINGS.md section 3
has the per-table numbers; this paragraph's ranges were tightened after the run, so the ledger rows' script_sha predates this
docstring edit; no code path changed). This variant adds `skipped share >= 0.10` to the eligibility inside each training fold
(nothing else changes: same cells, same folds, same criterion) and is counted in the family as one more nested-CV trial
(family '<study>/nested_cv_minskip' + its 11 CPCV paths, ledger note "repair": these rows were produced in the repair round after
the adversarial refuters found the script had never been run). The pre-registered nested row's family statistics (PBO / SPA /
effective trials / DSR / go-no-go) are recomputed here over the completed family (post-hoc row included) and written next to
the original ones. Both variants are reported; neither is chosen on the pooled OOF.

    python posthoc_minskip.py [--tf minute,5minute] [--labels L1,L0] [--studies h2,h3,h4] [--note repair]
"""
import os, sys, json, time, itertools, argparse
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="minute,5minute"); ap.add_argument("--labels", default="L1,L0")
ap.add_argument("--studies", default="h2,h3,h4"); ap.add_argument("--note", default="repair"); A = ap.parse_args()
sys.argv = [sys.argv[0]]                                   # the study modules parse their own args at import
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


def prereg_family_recomputed(T, study, tag):
    """The pre-registered nested-CV row's family statistics over the family as it now stands (the post-hoc rows included)."""
    p = os.path.join(HERE, f"{study}_{tag}_summary.json")
    if not os.path.exists(p): return None
    S = json.load(open(p, encoding="utf-8"))
    fam = C.family_stats(T, study, S["nested"], S["cpcv"], tag + "_prereg_final")
    fam["nested_id"] = S["nested"]["id"]; fam["original_candidates"] = S["family"]["candidates"]
    return fam


if __name__ == "__main__":
    log(f"posthoc_minskip start {time.ctime()} ledger sha {H.ledger_sha()} min_skip_share {MIN_SKIP} tf {A.tf} labels {A.labels} studies {A.studies} note {A.note!r}")
    S = {}
    for tf in A.tf.split(","):
        for label in A.labels.split(","):
            T = H.load(tf, label); tag = f"{tf}_{label}"
            for study in A.studies.split(","):
                cells = {"h2": lambda: H2.cells_h2(), "h3": lambda: h3_cells(T, tf), "h4": lambda: H4.cells_h4()}[study]()
                log(f"== {study} {tag}: {len(cells)} cells")
                res, chosen, dist, prow, cp_chosen = C.nested_cv(T, cells, study, __file__, log, min_skip_share=MIN_SKIP, suffix="_minskip", note=A.note)
                fam = C.family_stats(T, study, res, dist, tag + "_minskip")
                log(f"  family (incl. this row): {fam['candidates']} candidates, eff {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} best {fam['spa_best_config']}, boot {fam['bootstrap_nested']['diff_ci']}, DSR p {fam['dsr_nested'].get('p')}, go {fam['go_no_go_nested']['passed']}")
                pre = prereg_family_recomputed(T, study, tag)
                if pre is not None:
                    log(f"  pre-registered row {pre['nested_id']} over the completed family: {pre['candidates']} candidates, PBO diff {pre['pbo_diff']['pbo']}, SPA p {pre['spa']['spa_p']}, DSR p {pre['dsr_nested'].get('p')}, go {pre['go_no_go_nested']['passed']}")
                pd.DataFrame([{k: r.get(k) for k in ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "sign_blocks"]} | {"path": r["config"]["path"]} for r in prow]).to_csv(os.path.join(HERE, f"{study}_{tag}_cpcv_paths_minskip.csv"), index=False)
                S[f"{study}/{tag}"] = dict(tf=tf, label=label, study=study, min_skip_share=MIN_SKIP, ledger_note=A.note, n_is=int(T.is_mask.sum()),
                                           nested={k: res.get(k) for k in C.GRID_COLS if k != "cell"} | dict(chosen_per_block=chosen), cpcv=dist, cpcv_chosen=cp_chosen,
                                           family=fam, family_prereg_recomputed=pre)
                C.jdump(S[f"{study}/{tag}"], os.path.join(HERE, f"posthoc_{study}_{tag}_summary.json"))
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    C.jdump(S, os.path.join(HERE, f"posthoc_minskip_summary_{A.tf.replace(',', '_')}_{A.labels.replace(',', '_')}_{A.studies.replace(',', '_')}.json"))
    log(f"posthoc done in {S['run_s']}s; ledger sha {S['ledger_sha_after']}")
