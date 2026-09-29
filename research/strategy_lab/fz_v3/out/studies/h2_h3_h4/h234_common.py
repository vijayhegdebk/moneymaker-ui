"""Shared machinery of the H2 / H3 / H4 study (fz_v3/out/studies/h2_h3_h4): the harness is the only evaluator.

Every gate cell is a `Cell`: `fit(T, rows)` returns the cell's threshold learned on `rows` (None when the cell has no learned
number), `apply(T, rows, thr)` returns the keep mask over `rows`. From that, uniformly for every family:

  cell_ledger_row   the cell's IS ledger row: the 12-block out-of-fold mask (threshold fitted on each purged training fold of
                    harness.purged_splits, applied to its test block), scored once by harness.score (2,000 control draws).
  nested_cv         inside each of the 12 training folds, every cell is fitted and evaluated on the training rows with
                    harness.metrics (controls off; the harness's own kept-vs-skipped arithmetic, never a private one); the
                    cell with the largest kept-vs-skipped diff subject to the harness kept floors (kept share >= 20 %, kept n >=
                    floor x |train| / |IS|) is applied to the test block; the 12 test blocks form the OOF mask, one ledger row
                    (family '<study>/nested_cv').
  cpcv              the same selection inside each of the 66 CPCV training sets; the 11 paths (harness.cpcv_paths) are scored by
                    harness.score_paths (family '<study>/nested_cv/cpcv', controls on).
  family_stats      PBO (diff and kept_mean), SPA, effective trials over every non-cpcv ledger row of the family (this tf, this
                    label), block bootstrap and DSR of the nested-CV row, harness.go_no_go on it.
  bucket_table      descriptive decomposition of the label by a categorical: n, mean, se, median, win rate, sum, mean pts, stop
                    share, blocks below (of 12 IS blocks, how many have the bucket's mean below the block's all-rows mean).
                    No rule is chosen on a bucket table; every question that needs a p-value is a ledger row.
"""
import os, sys, json, time, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import numpy as np, pandas as pd
import harness as H

FLOOR_SHARE = H.GO["kept_share_min"]
FLOOR_N = H.GO["kept_n_min"]
BPH = {"minute": 60, "5minute": 12}
CUT = "trunc_20250630_120000"


class Log:
    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); self.f.write(time.strftime("%H:%M:%S ") + s + "\n"); self.f.flush()


def jdump(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))


def txt(s):
    return s.astype(object).where(s.notna(), "none").astype(str)


class Cell:
    def __init__(self, family, config, fit=None, apply=None):
        self.family, self.config = family, config
        self._fit, self._apply = fit, apply

    @property
    def name(self):
        return json.dumps(self.config, sort_keys=True)

    def fit(self, T, rows):
        return None if self._fit is None else self._fit(T, rows)

    def apply(self, T, rows, thr):
        return np.asarray(self._apply(T, rows, thr), dtype=bool)


# ---------------------------------------------------------------- descriptive tables
def bucket_table(T, cat, name, rows=None, order=None):
    rows = np.flatnonzero(T.is_mask) if rows is None else rows
    cat = np.asarray(cat).astype(str)
    net, win, pts, blk = T.net, T.win, T.pts, T.block
    pre = "l1_" if T.label == "L1" else "fnd_"
    stop = (T.F[pre + "exit_reason"].astype(str) == "stop_loss").to_numpy()
    cats = order if order is not None else sorted(set(cat[rows].tolist()))
    block_mean = {b: float(net[rows][blk[rows] == b].mean()) for b in range(H.N_BLOCKS) if (blk[rows] == b).any()}
    out = []
    for c in cats:
        r = rows[cat[rows] == c]
        if len(r) == 0: continue
        below = sum(1 for b, m in block_mean.items() if (blk[r] == b).sum() >= 1 and net[r][blk[r] == b].mean() < m)
        out.append(dict(variable=name, bucket=c, n=int(len(r)), share=round(len(r) / len(rows), 4), net_sum=round(float(net[r].sum()), 2),
                        net_mean=round(float(net[r].mean()), 2), net_se=round(float(net[r].std(ddof=1) / math.sqrt(len(r))), 2) if len(r) > 1 else None,
                        net_median=round(float(np.median(net[r])), 2), win_rate=round(float(win[r].mean()), 4), pts_mean=round(float(pts[r].mean()), 3),
                        stop_share=round(float(stop[r].mean()), 4), blocks_present=int(len(set(blk[r].tolist()))), blocks_below_block_mean=int(below)))
    return pd.DataFrame(out)


def two_way(T, cat_a, cat_b, name_a, name_b, rows=None):
    rows = np.flatnonzero(T.is_mask) if rows is None else rows
    d = pd.DataFrame({name_a: np.asarray(cat_a).astype(str)[rows], name_b: np.asarray(cat_b).astype(str)[rows], "net": T.net[rows], "win": T.win[rows].astype(int)})
    g = d.groupby([name_a, name_b], observed=True).agg(n=("net", "size"), net_mean=("net", "mean"), net_sum=("net", "sum"), win_rate=("win", "mean")).round(2).reset_index()
    return g


def tercile_labels(x, q=(1 / 3, 2 / 3), edges=None):
    """Descriptive terciles of an as-of column over the IS rows (pooled edges, recorded); NaN -> 'nan'."""
    x = np.asarray(x, dtype=float)
    if edges is None: edges = np.nanquantile(x, q)
    lab = np.where(np.isnan(x), "nan", np.where(x <= edges[0], f"T1<={edges[0]:.3f}", np.where(x <= edges[1], f"T2<={edges[1]:.3f}", f"T3>{edges[1]:.3f}")))
    return lab, [round(float(e), 4) for e in edges]


# ---------------------------------------------------------------- the cells through the harness
def oof_mask(T, cell):
    """The 12-block out-of-fold keep mask of a cell (threshold from each purged training fold) and the fold thresholds."""
    keep = np.ones(T.n, dtype=bool); thrs = []
    for tr, te in H.purged_splits(T):
        thr = cell.fit(T, tr); keep[te] = cell.apply(T, te, thr); thrs.append(thr)
    return keep, thrs


def score_cells(T, cells, script, log, extra=None):
    """One ledger row per cell (its OOF mask on IS). Returns the rows (with the cell's fold thresholds in `note`)."""
    rows = []
    for i, c in enumerate(cells):
        keep, thrs = oof_mask(T, c)
        note = None if all(t is None for t in thrs) else json.dumps(dict(fold_thresholds=[None if t is None else round(float(t), 4) for t in thrs]))
        r = H.score(T, keep, c.family, c.config, script=script, note=note)
        r["fold_thresholds"] = thrs; r["cell"] = c.name
        r["go_raw"] = H.go_no_go(r, T.tf)[0]
        rows.append(r)
        if i % 20 == 0 or i == len(cells) - 1:
            log(f"    cell {i + 1}/{len(cells)} {c.name} kept {r['kept_n']} diff {r['diff']} pct {r['control_pct']} p {r['perm_p']}")
    return rows


def select_in_fold(T, cells, tr, tag, min_skip_share=0.0):
    """The nested-CV choice inside one training fold: the eligible cell with the largest kept-vs-skipped diff on the training rows.
    min_skip_share > 0 is the post-hoc variant (declared after the primary runs): the cell must also skip at least that share."""
    floor_n = FLOOR_N[T.tf] * len(tr) / T.is_mask.sum()
    best = None; n_elig = 0
    for c in cells:
        thr = c.fit(T, tr)
        full = np.ones(T.n, dtype=bool); full[tr] = c.apply(T, tr, thr)
        m = H.metrics(T, full, tr, tag, controls=False)
        if m["diff"] is None or m["kept_share"] < FLOOR_SHARE or m["kept_n"] < floor_n or (1 - m["kept_share"]) < min_skip_share: continue
        n_elig += 1
        if best is None or m["diff"] > best["diff"]:
            best = dict(diff=m["diff"], cell=c, thr=thr, kept_share=m["kept_share"], kept_n=m["kept_n"], control=None)
    return best, n_elig


def nested_cv(T, cells, study, script, log, cfg_extra=None, min_skip_share=0.0, suffix=""):
    """The 12-block nested-CV candidate (one ledger row) and its 11 CPCV paths (11 ledger rows)."""
    keep = np.ones(T.n, dtype=bool); chosen = []
    fam = f"{study}/nested_cv{suffix}"
    if min_skip_share: cfg_extra = dict(cfg_extra or {}, min_skip_share=min_skip_share)
    for b, (tr, te) in enumerate(H.purged_splits(T)):
        best, n_elig = select_in_fold(T, cells, tr, f"{study}|nested{suffix}|{T.tf}|{T.label}|{b}", min_skip_share)
        if best is None:
            chosen.append(dict(block=b, cell=None, eligible=n_elig, train_n=int(len(tr)), test_n=int(len(te)))); continue
        keep[te] = best["cell"].apply(T, te, best["thr"])
        chosen.append(dict(block=b, cell=best["cell"].config, thr=None if best["thr"] is None else round(float(best["thr"]), 4), train_diff=best["diff"],
                           train_kept_share=best["kept_share"], eligible=n_elig, train_n=int(len(tr)), test_n=int(len(te)), test_kept=int(keep[te].sum())))
    cfg = dict(selection="nested_cv_12_blocks", criterion="max train diff s.t. kept_share>=0.20 and kept_n>=floor*train/IS",
               chosen_per_block=[c["cell"] for c in chosen], **(cfg_extra or {}))
    res = H.score(T, keep, fam, cfg, script=script, note=json.dumps(chosen, default=str))
    res["go_raw"] = H.go_no_go(res, T.tf)[0]
    log(f"  nested-CV{suffix} OOF: kept {res['kept_n']} ({res['kept_share']}) diff {res['diff']} pct {res['control_pct']} p {res['perm_p']} blocks {res['sign_blocks']} id {res['id']}")
    # CPCV: the same selection inside each of the 66 training sets
    oof = {}; cp_chosen = []
    for tr, te, (a, b) in H.cpcv_splits(T):
        best, n_elig = select_in_fold(T, cells, tr, f"{study}|cpcv{suffix}|{T.tf}|{T.label}|{a}{b}", min_skip_share)
        dec = np.ones(len(te), dtype=bool) if best is None else best["cell"].apply(T, te, best["thr"])
        oof[(a, b)] = dec.astype(float)
        cp_chosen.append(dict(split=[a, b], cell=None if best is None else best["cell"].config, train_diff=None if best is None else best["diff"], eligible=n_elig))
    paths = H.cpcv_paths(T, oof)
    dist, prow = H.score_paths(T, paths, fam, dict(selection="nested_cv_cpcv", **(cfg_extra or {})), script=script, controls=True)
    log(f"  CPCV 11 paths: diff median {dist['diff_median']} p5 {dist['diff_p5']} min {dist['diff_min']} share>0 {dist['diff_share_positive']} control pct median {dist.get('control_pct_median')} p5 {dist.get('control_pct_p5')}")
    return res, chosen, dist, prow, cp_chosen


def family_stats(T, study, nested_res, dist, tag):
    rows = [r for r in H.read_ledger(study, tf=T.tf, label=T.label) if not r["family"].endswith("/cpcv")]
    ids = list(dict.fromkeys(r["id"] for r in rows)); vecs = [H.load_vectors(i) for i in ids]
    fam = dict(ledger_rows=len(rows), candidates=len(ids), effective_trials=H.effective_trials(vecs) if len(vecs) > 1 else 1.0,
               pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"{study}|{tag}"))
    fam["spa_best_config"] = next((r["config"] for r in rows if r["id"] == ids[fam["spa"]["best"]]), None)
    v = H.load_vectors(nested_res["id"])
    fam["bootstrap_nested"] = H.bootstrap_ci(v, tag=f"{study}|{tag}|nested")

    def sharpe(vv):
        m = vv["kept_n"] > 0; s = vv["kept_sum"][m] / vv["kept_n"][m]
        return float(s.mean() / s.std(ddof=1)) if len(s) > 2 and s.std(ddof=1) else np.nan
    srs = np.array([sharpe(x) for x in vecs]); srs = srs[np.isfinite(srs)]
    m = v["kept_n"] > 0
    fam["dsr_nested"] = H.deflated_sharpe(v["kept_sum"][m] / v["kept_n"][m], len(ids), float(srs.var(ddof=1)) if len(srs) > 1 else None)
    passed, checks = H.go_no_go(nested_res, T.tf, cpcv=dist, pbo_value=fam["pbo_diff"]["pbo"], dsr=fam["dsr_nested"], spa_p=fam["spa"]["spa_p"], boot=fam["bootstrap_nested"])
    fam["go_no_go_nested"] = dict(passed=passed, checks=checks)
    return fam


GRID_COLS = ["cell", "id", "family", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall",
             "loser_precision", "winner_recall", "winner_recall_weighted", "top_decile_winners_skipped", "kept_pf", "kept_mean_slip8", "sign_blocks",
             "kept_win_rate", "skipped_win_rate", "go_raw"]


def grid_frame(rows, extra_cols=()):
    cols = GRID_COLS + list(extra_cols)
    return pd.DataFrame([{c: r.get(c) for c in cols} for r in rows])


def candidate_json(study, tf, res, cfg_rules, statistic, script, note):
    return dict(study=study, timeframe=tf, label="L1", action="skip_setup_when", rules=cfg_rules,
                provenance=dict(source="learned on IS 2021-10..2025-12", script=os.path.basename(script), ledger_id=res["id"], statistic=statistic, note=note))


def trunc_diff_setups(full_df, trunc_df, cols, nb):
    """Causality check of new per-SETUP features: identical for every SETUP before the cut, or the feature is dropped."""
    a = full_df[full_df.setup_i < nb].reset_index(drop=True); b = trunc_df.reset_index(drop=True)
    out = dict(setups_before_cut=[int(len(a)), int(len(b))], differ=[])
    if len(a) != len(b): out["differ"] = ["ROW COUNT"]; return out
    for c in cols:
        x, y = a[c].astype(object).map(str), b[c].astype(object).map(str)
        if not (x == y).all(): out["differ"].append(c)
    out["PASS"] = len(out["differ"]) == 0
    return out
