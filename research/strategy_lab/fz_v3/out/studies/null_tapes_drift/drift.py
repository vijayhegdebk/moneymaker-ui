"""Study null_tapes_drift, part (d): adversarial validation for feature drift inside IS (DESIGN_PANEL decision-making-3 (d),
both judges' fixes: IS-early vs IS-late now; the IS-vs-OOS check is NOT run here, it belongs to oos_once.py's post-mortem).

    python drift.py                      # both timeframes -> drift.json, drift_<tf>_features.csv, drift.log

Definition (fixed before any number): unit = the L1 unit table (harness.load(tf), IS rows only). Label = 1 when the SETUP's session
date is in IS-late (2023-10-01 .. 2025-12-31), 0 when in IS-early (2021-10-01 .. 2023-09-30). Design matrix = harness.design(T)
over Table.asof_columns() (floats as they are, booleans 0/1, text one-hot <= 16 levels); HistGradientBoostingClassifier handles
NaN natively. Cross-validation = harness.purged_splits (12 contiguous IS blocks, purge by the label's exit bar, 3-session
embargo); the reported AUC is the pooled out-of-fold AUC over all IS rows (single blocks are mostly one class, so per-fold AUCs
are undefined). Chance level = the same pooled OOF AUC with the early / late label permuted across rows, 20 permutations
(p50, p95). Two design variants: (A) every as-of column; (B) without the time proxies = as-of columns whose |Spearman rho| with
session_idx over IS rows is >= 0.9 (n_events_asof is one by construction: the cumulative event count since the data start),
listed in the output; the drift ranking uses (B) so that the ranked features are drift in the market, not the calendar.
Ranking = mean |SHAP| (shap.TreeExplainer on the model refit on all IS rows of (B)); each of the top 20 carries its direction of
drift = the sign of (mean late - mean early) with the standardised shift, the KS statistic between the two periods, and the
sign of the SHAP-feature correlation (positive = higher values push toward 'late').
Rule for the gate studies (written to drift.json): a selected rule that uses one of the top-5 drifted features (variant B) is
refit without that feature and both versions are reported; a rule that uses a time proxy is refused.
"""
import os, sys, json, time
sys.dont_write_bytecode = True
os.environ.setdefault("OMP_NUM_THREADS", "1")                          # one thread per fit (OpenMP spin-waits under a loaded box); the permutations run in 4 processes
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy import stats as sst
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import shap
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402

EARLY_END = "2023-09-30"
N_PERM = 20
TIME_PROXY_RHO = 0.9
HGB = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40, l2_regularization=1.0, random_state=0, early_stopping=False)


def log(msg, fh):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"; print(line, flush=True); fh.write(line + "\n"); fh.flush()


def oof_auc(T, X, y, rng=None):
    """Pooled out-of-fold AUC over the IS rows under harness.purged_splits; y may be permuted (rng given)."""
    is_idx = np.flatnonzero(T.is_mask)
    yy = y.copy()
    if rng is not None: yy[is_idx] = rng.permutation(yy[is_idx])
    oof = np.full(T.n, np.nan)
    for tr, te in H.purged_splits(T):
        if len(np.unique(yy[tr])) < 2: oof[te] = yy[tr].mean(); continue
        m = HistGradientBoostingClassifier(**HGB).fit(X[tr], yy[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(yy[is_idx], oof[is_idx])), oof


def _perm_auc(T, X, y, seed):
    return oof_auc(T, X, y, np.random.default_rng(seed))[0]


def run_tf(tf, fh):
    T = H.load(tf)
    Xdf, src = H.design(T)
    is_idx = np.flatnonzero(T.is_mask)
    y = (T.day > EARLY_END).astype(int)
    n_early, n_late = int((y[is_idx] == 0).sum()), int((y[is_idx] == 1).sum())
    log(f"{tf}: IS units {len(is_idx)} (early {n_early}, late {n_late}), design {Xdf.shape}", fh)
    # time proxies: monotone-in-time as-of columns
    sess = T.session[is_idx].astype(float)
    rho = {}
    for c in Xdf.columns:
        x = Xdf[c].to_numpy(dtype=float)[is_idx]; ok = np.isfinite(x)
        if ok.sum() > 50 and np.nanstd(x[ok]) > 0: rho[c] = float(sst.spearmanr(x[ok], sess[ok]).statistic)
    proxies = sorted([c for c, r in rho.items() if abs(r) >= TIME_PROXY_RHO], key=lambda c: -abs(rho[c]))
    log(f"{tf}: time proxies (|rho| >= {TIME_PROXY_RHO} with session_idx): {[(c, round(rho[c], 3)) for c in proxies]}", fh)
    out = dict(tf=tf, label="IS-late (session date > %s) vs IS-early" % EARLY_END, n_is=int(len(is_idx)), n_early=n_early, n_late=n_late,
               design_columns=int(Xdf.shape[1]), cv="harness.purged_splits (12 blocks, purge by exit bar, 3-session embargo), pooled OOF AUC",
               hgb=HGB, time_proxies={c: round(rho[c], 4) for c in proxies}, variants={})
    for name, cols in (("A_all_asof", list(Xdf.columns)), ("B_without_time_proxies", [c for c in Xdf.columns if c not in proxies])):
        X = Xdf[cols].to_numpy(dtype=float)
        t0 = time.time(); auc, oof = oof_auc(T, X, y)
        rng = np.random.default_rng(int(H._sha(f"drift|{tf}|{name}"), 16) % (2 ** 32))
        seeds = [int(s) for s in rng.integers(0, 2 ** 32 - 1, size=N_PERM)]          # one seed per permutation: reproducible in parallel
        perm = Parallel(n_jobs=4)(delayed(_perm_auc)(T, X, y, s) for s in seeds)
        out["variants"][name] = dict(columns=len(cols), auc_oof=round(auc, 4), perm_auc_p50=round(float(np.median(perm)), 4), perm_auc_p95=round(float(np.quantile(perm, 0.95)), 4),
                                     perm_auc_max=round(float(np.max(perm)), 4), n_perm=N_PERM, seconds=round(time.time() - t0, 1))
        log(f"{tf} {name}: OOF AUC {auc:.4f} (permuted p50 {np.median(perm):.4f}, p95 {np.quantile(perm, 0.95):.4f}) in {time.time() - t0:.0f}s", fh)
        if name.startswith("B"):
            m = HistGradientBoostingClassifier(**HGB).fit(X[is_idx], y[is_idx])
            try:
                sv = shap.TreeExplainer(m).shap_values(X[is_idx])
                sv = sv[1] if isinstance(sv, list) else sv
                if sv.ndim == 3: sv = sv[:, :, -1]
            except Exception as e:                                   # fallback: NaN -> sentinel, refit, explain
                log(f"{tf}: TreeExplainer on native-NaN HGB failed ({e}); refitting on a sentinel-filled matrix for SHAP", fh)
                Xs = np.where(np.isfinite(X), X, -1e6); m = HistGradientBoostingClassifier(**HGB).fit(Xs[is_idx], y[is_idx])
                sv = shap.TreeExplainer(m).shap_values(Xs[is_idx]); sv = sv[1] if isinstance(sv, list) else sv
                if sv.ndim == 3: sv = sv[:, :, -1]
            imp = np.abs(sv).mean(axis=0)
            rows = []
            e_, l_ = is_idx[y[is_idx] == 0], is_idx[y[is_idx] == 1]
            for j, c in enumerate(cols):
                x = Xdf[c].to_numpy(dtype=float)
                xe, xl = x[e_][np.isfinite(x[e_])], x[l_][np.isfinite(x[l_])]
                sd = np.sqrt((np.var(xe) + np.var(xl)) / 2) if len(xe) > 1 and len(xl) > 1 else np.nan
                ks = sst.ks_2samp(xe, xl).statistic if len(xe) > 5 and len(xl) > 5 else np.nan
                xx = x[is_idx]; ok = np.isfinite(xx) & (np.std(sv[:, j]) > 0)
                corr = float(np.corrcoef(xx[ok], sv[ok, j])[0, 1]) if ok.sum() > 10 and np.std(xx[ok]) > 0 else np.nan
                rows.append(dict(feature=c, source=src[c], mean_abs_shap=float(imp[j]), mean_early=float(np.mean(xe)) if len(xe) else np.nan,
                                 mean_late=float(np.mean(xl)) if len(xl) else np.nan, std_shift=float((np.mean(xl) - np.mean(xe)) / sd) if sd and np.isfinite(sd) and sd > 0 else np.nan,
                                 ks=float(ks), nan_share_early=float(1 - len(xe) / len(e_)), nan_share_late=float(1 - len(xl) / len(l_)), shap_x_corr=corr,
                                 direction=("higher in IS-late" if len(xe) and len(xl) and np.mean(xl) > np.mean(xe) else "lower in IS-late" if len(xe) and len(xl) else "n/a")))
            D = pd.DataFrame(rows).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
            D["rank"] = np.arange(1, len(D) + 1)
            D.to_csv(os.path.join(HERE, f"drift_{tf}_features.csv"), index=False)
            top = D.head(20)
            out["top20_drifted"] = [dict(rank=int(r.rank), feature=r.feature, source=r.source, mean_abs_shap=round(r.mean_abs_shap, 5), mean_early=round(r.mean_early, 4) if np.isfinite(r.mean_early) else None,
                                         mean_late=round(r.mean_late, 4) if np.isfinite(r.mean_late) else None, std_shift=round(r.std_shift, 3) if np.isfinite(r.std_shift) else None,
                                         ks=round(r.ks, 4) if np.isfinite(r.ks) else None, shap_x_corr=round(r.shap_x_corr, 3) if np.isfinite(r.shap_x_corr) else None, direction=r.direction)
                                    for r in top.itertuples(index=False)]
            out["top5_sources"] = sorted({r.source for r in top.head(5).itertuples(index=False)})
            log(f"{tf} top-10 drifted (B): " + ", ".join(f"{r.feature} ({r.direction}, shift {r.std_shift:+.2f} sd)" for r in top.head(10).itertuples(index=False)), fh)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="5minute,minute", help="comma list; one timeframe per process lets both run in parallel")
    ap.add_argument("--out", default="drift.json", help="output file (drift_<tf>.json for a per-timeframe run; write_findings.py merges it)")
    a = ap.parse_args()
    fh = open(os.path.join(HERE, "drift.log"), "a")
    res = dict(study="null_tapes_drift", part="d: adversarial validation IS-early vs IS-late",
               not_run_here="IS-vs-OOS adversarial validation (runs after the single OOS evaluation, in oos_once.py's post-mortem, label-free, explanatory only)",
               rule_for_gate_studies=("a selected rule that uses one of top5_sources (variant B) is refit without that feature and both versions are reported "
                                      "in the study's FINDINGS; a rule that uses a time proxy (time_proxies) is refused as a calendar rule, not a market rule; "
                                      "a rule that uses any feature of top20_drifted carries the feature's std_shift as a caveat"),
               timeframes={})
    for tf in a.tf.split(","):
        res["timeframes"][tf] = run_tf(tf, fh)
        json.dump(res, open(os.path.join(HERE, a.out), "w"), indent=1, default=str)
    log(f"{a.out} written", fh)


if __name__ == "__main__":
    main()
