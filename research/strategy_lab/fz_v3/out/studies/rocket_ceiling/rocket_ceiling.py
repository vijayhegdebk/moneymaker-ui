"""rocket_ceiling: DESIGN_PANEL deep-sequence-rocket-probe REDUCED to the single ceiling check both judges allow.

    nohup python rocket_ceiling.py > run.nohup 2>&1 &          # 1 minute only, label L1, IS only; log = rocket_ceiling.log

Question. Does the shape of the last 60 one-minute bars before a Foundation SETUP carry information about the L1 outcome beyond
the hand-built as-of features? Judge 2's reduction: 1m only, L = 60, 2,000 kernels, one probe, the harness splitter, and a
PRE-REGISTERED STOP: if the CPCV 5th-percentile AUC gain of the stacked model over the tabular HGB is < 0.03 the study ends with
that number and no distillation. Judge 1: alpha by nested GroupKFold (never RidgeClassifierCV's LOO); this study never gets a
candidate slot; its trials still go to the ledger. Pretrain-probe footnote (both judges): the PCA-16 linear probe on the flattened
z-scored window is a comparator here; sequence pretraining is deferred until a longer tape (torch is present in the cloud, the
design's sample-size objection is unchanged).

Definitions (fixed before any number was looked at):
  unit        a harness row: a Foundation SETUP taken under the L1 (15:25) book, harness.load("minute"); IS rows only (4,452);
              label y = L1 net > 0 (the training and judging label); windows are built for IS rows only (OOS features are never read)
  window      L = 60 bars ending at the SETUP bar k inclusive, 7 channels (rocket_lib.build_windows docstring): sg x log return
              (bps), (high-low)/atr14[k], sg x (close-open)/atr14[k], log(volume / vol_med20_prior[k]) with NaN -> 0, its NA flag,
              sg x (close - choch_lvl[k])/atr14[k], same-session indicator; float32; bars from data/minute/bars.parquet; verified on
              data/minute/trunc_20250630_120000 (windows of the SETUPs before the cut must be identical, else the study stops)
  kernels     2,000 MiniRocket-style kernels (rocket_lib.make_kernels): length 9, weights {-1, +2} centred, dilation log-uniform
              on 1 .. L/4 = 15, one channel or a random pair, zero padding, a quantile level per kernel; biases fitted per training
              fold from the quantiles of the convolution outputs of 32 sampled training windows (seed = fold seed); PPV pooling
  probe       "rocket": StandardScaler + L2 LogisticRegression (lbfgs) on the 2,000 PPV features; alpha (= 1 / C) on the grid
              1e-3 .. 1e3 (7 values) chosen by nested GroupKFold(5) inside each training fold with groups = the harness block
              of the row (time-contiguous groups), criterion = mean inner AUC; refit on the whole training fold at the chosen alpha
  comparators (in the same folds)
              "tabular": HistGradientBoostingClassifier(max_depth 3, max_iter 200, learning_rate 0.05, random_state 0) on
                         harness.design(T) (244 base as-of columns; NaN native)
              "pca16":   StandardScaler + PCA(16) on the flattened z-scored window (7 x 60 = 420) + the same nested-alpha logistic
              "stacked": the same HGB on [design(T), the top 16 PCA components of the standardised PPV features], scaler + PCA fit
                         on the training fold (and inside every inner fold for the threshold OOF)
  splitter    harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo) -> the OOF probabilities;
              harness.cpcv_splits (66) -> harness.cpcv_paths (11 paths) -> the path distribution
  statistic   per-fold test AUC (and average precision) of every model; pooled 12-block OOF AUC; per path: the pooled AUC over
              IS rows of each model and the gains stacked - tabular, rocket - tabular, pca16 - tabular; the distribution over
              the 11 paths (median, 5th percentile = np.quantile(., 0.05), min, share > 0). Judge 1's per-fold form (stacked -
              tabular < 0.02 in every fold) is reported next to it as a footnote.
  STOP        pre-registered: CPCV 5th-percentile gain (stacked - tabular) < 0.03 -> the study ends with that number; no
              distillation, no candidate. >= 0.03 -> distil the probe score's bottom tercile to a depth-3 tree on scalar as-of
              features (design(T) + win_sign_agree10, win_dd_extreme_atr, win_range_slope from features_ext) and report fidelity
  gates       every model x skip fraction q in {0.30, 0.50, 0.70}: the threshold = the q-quantile of the model's inner-fold OOF
              scores on the TRAINING fold (never the test rows); keep = test score >= threshold; the 12-block OOF mask is one
              harness.score row (family rocket/<model>, config = model, q, L, K, seed); the 66 CPCV decisions -> 11 path masks ->
              harness.score_paths (family rocket/<model>/cpcv, controls on). 12 + 132 ledger rows; nothing is chosen on them.
  family      window lengths x kernel counts x probes = 1 x 1 x 3 (Judge 2's count for the design's multiplicity statement; the
              third probe = pca16); PBO / SPA / effective trials over the 12 OOF gate rows; DSR and the block bootstrap for the
              gate with the largest OOF diff; harness.go_no_go for information only (no candidate slot)
  never       a label inside the transform, a bias or a scaler fitted on test rows, an OOS row (features or labels), a threshold
              from the pooled OOF
"""
import os, sys, json, time, hashlib, resource, argparse
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT); sys.path.insert(0, HERE)
import numpy as np, pandas as pd, psutil
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.tree import DecisionTreeClassifier, export_text
import harness as H
import rocket_lib as R

ap = argparse.ArgumentParser(); ap.add_argument("--skip-controls", action="store_true", help="debug only: score() without the 2,000-draw controls")
ARGS = ap.parse_args()

TF, LABEL, L, K, C = "minute", "L1", 60, 2000, 7
SEED = int(hashlib.sha1(f"fz|rocket_ceiling|{TF}|L{L}|K{K}".encode()).hexdigest(), 16) % (2 ** 32)
ALPHAS = [10.0 ** e for e in range(-3, 4)]                       # 1e-3 .. 1e3; C = 1 / alpha
N_INNER, N_BIAS = 5, 32
SKIP_Q = (0.30, 0.50, 0.70)
STOP_P5 = 0.03
MODELS = ("rocket", "pca16", "tabular", "stacked")
HGB = dict(max_depth=3, max_iter=200, learning_rate=0.05, random_state=0)
WIN_EXT = ("win_sign_agree10", "win_dd_extreme_atr", "win_range_slope")
T0 = time.time()
LOGF = open(os.path.join(HERE, "rocket_ceiling.log"), "a", encoding="utf-8")


def log(s):
    line = f"[{time.strftime('%H:%M:%S')} +{time.time() - T0:7.1f}s rss {rss_mb():5d}MB] {s}"
    print(line, flush=True); LOGF.write(line + "\n"); LOGF.flush()


def rss_mb(): return int(psutil.Process().memory_info().rss / 2 ** 20)


def peak_rss_mb(): return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)


def jdump(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else (z.tolist() if hasattr(z, "tolist") else str(z)))


def fold_seed(tag): return int(hashlib.sha1(f"{SEED}|{tag}".encode()).hexdigest(), 16) % (2 ** 32)


# ---------------------------------------------------------------- the truncation (causality) check of the window tensor
def trunc_check(W_full, F_is, bars_cols):
    d = os.path.join(OUT, "data", TF, "trunc_20250630_120000")
    bt = pd.read_parquet(os.path.join(d, "bars.parquet"), columns=bars_cols)
    ft = pd.read_parquet(os.path.join(d, "features.parquet"))
    ft = ft[ft.traded.astype(bool) & ft.l1_taken.astype(bool)].sort_values("setup_i").reset_index(drop=True)
    nb = len(bt)
    a = F_is[F_is.setup_i < nb].reset_index(drop=True)
    b = ft[ft.setup_i.isin(a.setup_i)].reset_index(drop=True)
    out = dict(cut="trunc_20250630_120000", bars_truncated=int(nb), setups_before_cut=[int(len(a)), int(len(b))],
               same_setup_keys=bool(len(a) == len(b) and (a.setup_i.to_numpy() == b.setup_i.to_numpy()).all()))
    if not out["same_setup_keys"]:
        out["PASS"] = False; return out
    Wt = R.build_windows(bt, b, L)
    Wf = W_full[np.flatnonzero((F_is.setup_i < nb).to_numpy())]
    diff = np.abs(Wf.astype(np.float64) - Wt.astype(np.float64))
    out["channels"] = {f"ch{c}": dict(max_abs_diff=float(diff[:, c].max()), identical=bool((diff[:, c] == 0).all())) for c in range(C)}
    out["max_abs_diff"] = float(diff.max()); out["PASS"] = bool(diff.max() == 0)
    return out


# ---------------------------------------------------------------- the models inside one fold
def logit_nested(Ztr_fn, y_tr, groups, tag):
    """Nested GroupKFold alpha choice for a linear probe. Ztr_fn(itr, ite) -> (Z_inner_train, Z_inner_test) with every scaler / PCA
    fitted on the inner training rows only. Returns best alpha, the inner OOF scores at every alpha, the per-alpha inner AUC."""
    gkf = GroupKFold(n_splits=N_INNER)
    splits = list(gkf.split(np.zeros(len(y_tr)), y_tr, groups))

    def one(itr, ite):
        Zi, Zo = Ztr_fn(itr, ite)
        res = {}
        for a in ALPHAS:
            m = LogisticRegression(C=1.0 / a, penalty="l2", solver="lbfgs", max_iter=5000, tol=1e-4).fit(Zi, y_tr[itr])
            res[a] = (m.decision_function(Zo), int(m.n_iter_[0]))
        return res
    parts = Parallel(n_jobs=min(4, N_INNER), prefer="processes")(delayed(one)(itr, ite) for itr, ite in splits)
    oof = {a: np.full(len(y_tr), np.nan) for a in ALPHAS}; iters = {a: [] for a in ALPHAS}
    for (itr, ite), res in zip(splits, parts):
        for a in ALPHAS: oof[a][ite] = res[a][0]; iters[a].append(res[a][1])
    auc = {a: float(roc_auc_score(y_tr, oof[a])) for a in ALPHAS}
    best = max(ALPHAS, key=lambda a: auc[a])
    return best, oof, auc, {a: int(max(v)) for a, v in iters.items()}


def hgb_nested(Xtr_fn, y_tr, groups):
    """Inner OOF scores of the fixed HGB (thresholds only). Xtr_fn(itr, ite) -> (X_inner_train, X_inner_test)."""
    gkf = GroupKFold(n_splits=N_INNER); oof = np.full(len(y_tr), np.nan)
    for itr, ite in gkf.split(np.zeros(len(y_tr)), y_tr, groups):
        Xi, Xo = Xtr_fn(itr, ite)
        oof[ite] = HistGradientBoostingClassifier(**HGB).fit(Xi, y_tr[itr]).predict_proba(Xo)[:, 1]
    return oof


def fit_fold(ctx, tr, te, tag):
    """One outer fold: fit every model on tr, score te. Returns scores, thresholds (from the training fold's inner OOF), AUCs."""
    W, kern, Xb, Wflat, y, block, pos = ctx["W"], ctx["kern"], ctx["Xb"], ctx["Wflat"], ctx["y"], ctx["block"], ctx["pos"]
    t_fold = time.time(); times = {}
    ptr, pte = pos[tr], pos[te]                                        # positions in the IS-only arrays
    y_tr, y_te, groups = y[ptr], y[pte], block[tr]
    fs = fold_seed(tag)
    # -- kernel biases from the training fold, PPV features
    t = time.time(); bias, samp = R.fit_biases(W, ptr, kern, fs, N_BIAS)
    Ptr, Pte = R.transform(W, ptr, kern, bias), R.transform(W, pte, kern, bias); times["transform"] = round(time.time() - t, 2)
    out = dict(tag=tag, seed=int(fs), n_train=int(len(tr)), n_test=int(len(te)), bias_sample_rows=[int(ptr[i] == 0) for i in []], scores={}, thr={}, auc={}, ap={}, alpha={}, inner_auc={}, iters={})
    out["bias_sample_first5"] = [int(x) for x in samp[:5]]
    # -- rocket probe
    t = time.time()
    def z_ppv(itr, ite):
        sc = StandardScaler().fit(Ptr[itr]); return sc.transform(Ptr[itr]), sc.transform(Ptr[ite])
    a_r, oof_r, auc_r, it_r = logit_nested(z_ppv, y_tr, groups, tag)
    sc = StandardScaler().fit(Ptr)
    m = LogisticRegression(C=1.0 / a_r, penalty="l2", solver="lbfgs", max_iter=5000, tol=1e-4).fit(sc.transform(Ptr), y_tr)
    s_te = m.decision_function(sc.transform(Pte)); s_in = oof_r[a_r]
    out["scores"]["rocket"], out["alpha"]["rocket"], out["inner_auc"]["rocket"], out["iters"]["rocket"] = s_te, a_r, auc_r, it_r
    out["thr"]["rocket"] = {q: float(np.quantile(s_in, q)) for q in SKIP_Q}; out["iters"]["rocket_final"] = int(m.n_iter_[0])
    times["rocket"] = round(time.time() - t, 2)
    # -- pca16 probe on the flattened z-scored window
    t = time.time()
    Ftr, Fte = Wflat[ptr], Wflat[pte]
    def z_pca(itr, ite):
        sc_ = StandardScaler().fit(Ftr[itr]); p_ = PCA(16, random_state=0).fit(sc_.transform(Ftr[itr]))
        return p_.transform(sc_.transform(Ftr[itr])), p_.transform(sc_.transform(Ftr[ite]))
    a_p, oof_p, auc_p, it_p = logit_nested(z_pca, y_tr, groups, tag + "|pca")
    sc2 = StandardScaler().fit(Ftr); pca_w = PCA(16, random_state=0).fit(sc2.transform(Ftr))
    m2 = LogisticRegression(C=1.0 / a_p, penalty="l2", solver="lbfgs", max_iter=5000, tol=1e-4).fit(pca_w.transform(sc2.transform(Ftr)), y_tr)
    out["scores"]["pca16"] = m2.decision_function(pca_w.transform(sc2.transform(Fte)))
    out["alpha"]["pca16"], out["inner_auc"]["pca16"], out["iters"]["pca16"] = a_p, auc_p, it_p
    out["thr"]["pca16"] = {q: float(np.quantile(oof_p[a_p], q)) for q in SKIP_Q}
    out["pca16_window_evr"] = float(pca_w.explained_variance_ratio_.sum())
    times["pca16"] = round(time.time() - t, 2)
    # -- tabular HGB on the base as-of design
    t = time.time()
    Btr, Bte = Xb[ptr], Xb[pte]
    oof_t = hgb_nested(lambda itr, ite: (Btr[itr], Btr[ite]), y_tr, groups)
    h = HistGradientBoostingClassifier(**HGB).fit(Btr, y_tr)
    out["scores"]["tabular"] = h.predict_proba(Bte)[:, 1]; out["thr"]["tabular"] = {q: float(np.quantile(oof_t, q)) for q in SKIP_Q}
    times["tabular"] = round(time.time() - t, 2)
    # -- stacked: base + top-16 PCA components of the standardised PPV features
    t = time.time()
    def stack(itr, ite):
        sc_ = StandardScaler().fit(Ptr[itr]); p_ = PCA(16, random_state=0).fit(sc_.transform(Ptr[itr]))
        return (np.hstack([Btr[itr], p_.transform(sc_.transform(Ptr[itr]))]), np.hstack([Btr[ite], p_.transform(sc_.transform(Ptr[ite]))]))
    oof_s = hgb_nested(stack, y_tr, groups)
    sc3 = StandardScaler().fit(Ptr); pca_p = PCA(16, random_state=0).fit(sc3.transform(Ptr))
    Str, Ste = np.hstack([Btr, pca_p.transform(sc3.transform(Ptr))]), np.hstack([Bte, pca_p.transform(sc3.transform(Pte))])
    hs = HistGradientBoostingClassifier(**HGB).fit(Str, y_tr)
    out["scores"]["stacked"] = hs.predict_proba(Ste)[:, 1]; out["thr"]["stacked"] = {q: float(np.quantile(oof_s, q)) for q in SKIP_Q}
    out["pca16_ppv_evr"] = float(pca_p.explained_variance_ratio_.sum())
    times["stacked"] = round(time.time() - t, 2)
    for mname in MODELS:
        out["auc"][mname] = float(roc_auc_score(y_te, out["scores"][mname])); out["ap"][mname] = float(average_precision_score(y_te, out["scores"][mname]))
    out["inner_oof_auc_at_chosen"] = dict(rocket=auc_r[a_r], pca16=auc_p[a_p], tabular=float(roc_auc_score(y_tr, oof_t)), stacked=float(roc_auc_score(y_tr, oof_s)))
    out["times"] = times; out["fold_s"] = round(time.time() - t_fold, 1)
    return out


def keep_from(scores, thr):
    return {q: (scores >= thr[q]) for q in SKIP_Q}


# ---------------------------------------------------------------- main
def main():
    log(f"rocket_ceiling start; ledger sha {H.ledger_sha()}; SEED {SEED}; L {L} K {K} C {C}; alphas {ALPHAS}; inner {N_INNER}; n_bias {N_BIAS}; skip_q {SKIP_Q}; STOP p5 < {STOP_P5}")
    T = H.load(TF, LABEL)
    is_rows = np.flatnonzero(T.is_mask); n_is = len(is_rows)
    pos = np.full(T.n, -1); pos[is_rows] = np.arange(n_is)               # row -> position in the IS-only arrays
    y = T.win[is_rows].astype(int)
    log(f"units {T.n} (IS {n_is}, OOS {int(T.oos_mask.sum())} = row count only); IS win rate {y.mean():.4f}; blocks {np.bincount(T.block[is_rows]).tolist()}")
    bars_cols = ["i", "session_idx", "open", "high", "low", "close", "volume", "atr14"]
    bars = pd.read_parquet(os.path.join(OUT, "data", TF, "bars.parquet"), columns=bars_cols)
    F_is = T.F.iloc[is_rows].reset_index(drop=True)
    t = time.time(); W = R.build_windows(bars, F_is, L); t_win = round(time.time() - t, 2)
    log(f"windows {W.shape} float32 {W.nbytes / 2 ** 20:.1f} MB in {t_win}s; channel means {np.round(W.mean(axis=(0, 2)), 3).tolist()} sds {np.round(W.std(axis=(0, 2)), 3).tolist()}; NA-flag share {W[:, 4].mean():.4f}; same-session share {W[:, 6].mean():.4f}; windows crossing the session start {(W[:, 6].min(axis=1) == 0).mean():.4f}")
    tc = trunc_check(W, F_is, bars_cols); jdump(tc, os.path.join(HERE, "windows_trunc_check.json"))
    log(f"truncation check: setups before cut {tc['setups_before_cut']} same keys {tc['same_setup_keys']} max |diff| {tc.get('max_abs_diff')} PASS {tc['PASS']}")
    if not tc["PASS"]:
        log("window tensor differs on the truncated tape: the feature is dropped and the study stops (BRIEF rule)"); return
    del bars
    kern = R.make_kernels(K, L, C, SEED)
    np.savez_compressed(os.path.join(HERE, "kernels.npz"), pos2=kern["pos2"], dil=kern["dil"], ch=kern["ch"], qlev=kern["qlev"], weights=kern["weights"], seed=SEED, L=L, K=K, C=C)
    log(f"kernel bank saved (seed {SEED}): dilation counts {np.bincount(kern['dil'], minlength=L // 4 + 1)[1:].tolist()}, pair share {(kern['ch'][:, 1] >= 0).mean():.3f}, channel use {np.bincount(kern['ch'][kern['ch'] >= 0], minlength=C).tolist()}")
    X, src = H.design(T); Xb = X.to_numpy(dtype=np.float64)[is_rows]; base_cols = list(X.columns)
    Wflat = W.reshape(n_is, -1)
    log(f"design matrix {Xb.shape} (base as-of columns), flattened window {Wflat.shape}")
    ctx = dict(W=W, kern=kern, Xb=Xb, Wflat=Wflat, y=y, block=T.block, pos=pos)
    # -- JIT warm-up (excluded from the fold timings) and a transform benchmark
    t = time.time(); b0, _ = R.fit_biases(W, np.arange(min(64, n_is)), kern, 0, N_BIAS); _ = R.transform(W, np.arange(64), kern, b0); t_jit = round(time.time() - t, 2)
    t = time.time(); Pall = R.transform(W, np.arange(n_is), kern, b0); t_tr = round(time.time() - t, 2)
    log(f"numba JIT {t_jit}s; one full transform {Pall.shape} in {t_tr}s ({Pall.nbytes / 2 ** 20:.1f} MB float32); PPV mean {Pall.mean():.4f}, constant kernels {(Pall.std(axis=0) == 0).sum()}")
    del Pall

    # ---------------- 12 purged splits: OOF probabilities and per-fold AUC
    oof = {m: np.full(T.n, np.nan) for m in MODELS}; keep12 = {(m, q): np.ones(T.n, dtype=bool) for m in MODELS for q in SKIP_Q}
    folds = []
    for b, (tr, te) in enumerate(H.purged_splits(T)):
        r = fit_fold(ctx, tr, te, f"purged|{b}")
        for m in MODELS:
            oof[m][te] = r["scores"][m]
            for q, kp in keep_from(r["scores"][m], r["thr"][m]).items(): keep12[(m, q)][te] = kp
        folds.append(dict(split="purged", block=b, **{k: r[k] for k in ("seed", "n_train", "n_test", "auc", "ap", "alpha", "inner_auc", "inner_oof_auc_at_chosen", "iters", "thr", "times", "fold_s", "pca16_window_evr", "pca16_ppv_evr", "bias_sample_first5")}))
        log(f"purged block {b}: n {len(tr)}/{len(te)} AUC " + " ".join(f"{m} {r['auc'][m]:.4f}" for m in MODELS) + f" | alpha rocket {r['alpha']['rocket']} pca16 {r['alpha']['pca16']} | {r['fold_s']}s {r['times']}")
    is_y = T.win[is_rows]
    oof_auc = {m: float(roc_auc_score(is_y, oof[m][is_rows])) for m in MODELS}
    oof_ap = {m: float(average_precision_score(is_y, oof[m][is_rows])) for m in MODELS}
    per_block_auc = {m: [f["auc"][m] for f in folds] for m in MODELS}
    log("12-block pooled OOF AUC " + " ".join(f"{m} {oof_auc[m]:.4f}" for m in MODELS) + "; mean per-block AUC " + " ".join(f"{m} {np.mean(per_block_auc[m]):.4f}" for m in MODELS))
    gain12 = {f"{a}-tabular": [f["auc"][a] - f["auc"]["tabular"] for f in folds] for a in ("stacked", "rocket", "pca16")}
    log("per-block gains stacked-tabular " + " ".join(f"{g:+.4f}" for g in gain12["stacked-tabular"]) + f" | Judge-1 footnote: every block < 0.02 = {all(g < 0.02 for g in gain12['stacked-tabular'])}")

    # ---------------- 66 CPCV splits -> 11 paths
    oof_scores = {m: {} for m in MODELS}; oof_keep = {(m, q): {} for m in MODELS for q in SKIP_Q}; cp = []
    for j, (tr, te, (a, b)) in enumerate(H.cpcv_splits(T)):
        r = fit_fold(ctx, tr, te, f"cpcv|{a}|{b}")
        for m in MODELS:
            oof_scores[m][(a, b)] = r["scores"][m].astype(float)
            for q, kp in keep_from(r["scores"][m], r["thr"][m]).items(): oof_keep[(m, q)][(a, b)] = kp.astype(float)
        cp.append(dict(split="cpcv", blocks=[a, b], **{k: r[k] for k in ("seed", "n_train", "n_test", "auc", "ap", "alpha", "inner_auc", "inner_oof_auc_at_chosen", "iters", "thr", "times", "fold_s", "pca16_window_evr", "pca16_ppv_evr", "bias_sample_first5")}))
        if j % 6 == 0 or j == 65:
            log(f"cpcv split {j + 1}/66 ({a},{b}): AUC " + " ".join(f"{m} {r['auc'][m]:.4f}" for m in MODELS) + f" | {r['fold_s']}s")
    paths = {m: H.cpcv_paths(T, oof_scores[m]) for m in MODELS}
    path_rows = []
    for p in range(len(paths["tabular"])):
        row = dict(path=p)
        for m in MODELS:
            row[f"auc_{m}"] = float(roc_auc_score(is_y, paths[m][p][is_rows])); row[f"ap_{m}"] = float(average_precision_score(is_y, paths[m][p][is_rows]))
            row[f"mean_block_auc_{m}"] = float(np.mean([roc_auc_score(is_y[T.block[is_rows] == g], paths[m][p][is_rows][T.block[is_rows] == g]) for g in range(H.N_BLOCKS)]))
        for a_ in ("stacked", "rocket", "pca16"): row[f"gain_{a_}"] = row[f"auc_{a_}"] - row["auc_tabular"]
        path_rows.append(row)
    PD = pd.DataFrame(path_rows); PD.to_csv(os.path.join(HERE, "path_auc.csv"), index=False)
    def dist(v):
        v = np.asarray(v, dtype=float)
        return dict(median=round(float(np.median(v)), 4), p5=round(float(np.quantile(v, 0.05)), 4), min=round(float(v.min()), 4), max=round(float(v.max()), 4), share_positive=round(float((v > 0).mean()), 3), n=int(len(v)))
    cpcv = {f"gain_{a_}": dist(PD[f"gain_{a_}"]) for a_ in ("stacked", "rocket", "pca16")}
    cpcv.update({f"auc_{m}": dist(PD[f"auc_{m}"]) for m in MODELS})
    split_gain = {f"{a_}-tabular": [c["auc"][a_] - c["auc"]["tabular"] for c in cp] for a_ in ("stacked", "rocket", "pca16")}
    stop = cpcv["gain_stacked"]["p5"] < STOP_P5
    log(f"CPCV 11 paths: AUC tabular {cpcv['auc_tabular']} | stacked {cpcv['auc_stacked']} | rocket {cpcv['auc_rocket']} | pca16 {cpcv['auc_pca16']}")
    log(f"CPCV gain stacked-tabular {cpcv['gain_stacked']}; rocket-tabular {cpcv['gain_rocket']}; pca16-tabular {cpcv['gain_pca16']}")
    log(f"66-split gains stacked-tabular: min {min(split_gain['stacked-tabular']):+.4f} median {np.median(split_gain['stacked-tabular']):+.4f} share < 0.02 {np.mean(np.array(split_gain['stacked-tabular']) < 0.02):.3f}")
    log(f"PRE-REGISTERED STOP: p5(stacked - tabular) = {cpcv['gain_stacked']['p5']} {'<' if stop else '>='} {STOP_P5} -> {'STOP: the study ends with that number, no distillation' if stop else 'continue to distillation'}")
    pd.DataFrame([dict(split=f["split"], block=f.get("block"), blocks=str(f.get("blocks")), n_train=f["n_train"], n_test=f["n_test"], **{f"auc_{m}": f["auc"][m] for m in MODELS}, **{f"ap_{m}": f["ap"][m] for m in MODELS},
                       alpha_rocket=f["alpha"]["rocket"], alpha_pca16=f["alpha"]["pca16"], **{f"inner_auc_{m}": f["inner_oof_auc_at_chosen"][m] for m in MODELS}, fold_s=f["fold_s"]) for f in folds + cp]).to_csv(os.path.join(HERE, "fold_auc.csv"), index=False)
    np.savez_compressed(os.path.join(HERE, "oof_scores.npz"), is_rows=is_rows, setup_i=T.setup_i, **{f"oof_{m}": oof[m] for m in MODELS}, **{f"paths_{m}": np.stack(paths[m]) for m in MODELS})
    t_models = round(time.time() - T0, 1); rss_models = rss_mb(); peak_models = peak_rss_mb()
    log(f"all 78 folds done at {t_models}s; RSS now {rss_models} MB, peak {peak_models} MB")

    # ---------------- the ledger: every OOF gate and its CPCV paths
    cfg0 = dict(L=L, kernels=K, channels=C, seed=SEED, n_bias=N_BIAS, alphas=ALPHAS, inner_folds=N_INNER, threshold="q-quantile of the training fold's inner OOF scores", label=LABEL)
    gates = []; gate_paths = {}
    controls = not ARGS.skip_controls
    for m in MODELS:
        for q in SKIP_Q:
            cfg = dict(cfg0, model=m, skip_q=q)
            note = json.dumps(dict(fold_thresholds=[round(f["thr"][m][q], 5) for f in folds], alpha=[f["alpha"].get(m) for f in folds]))
            res = H.score(T, keep12[(m, q)], f"rocket/{m}", cfg, script=__file__, controls=controls, note=note)
            res["go_raw"] = H.go_no_go(res, TF)[0]
            pth = H.cpcv_paths(T, oof_keep[(m, q)])
            d, prow = H.score_paths(T, pth, f"rocket/{m}", cfg, script=__file__, controls=controls)
            res["cpcv"] = d; gates.append(res); gate_paths[(m, q)] = prow
            log(f"gate {m} q {q}: kept {res['kept_n']} ({res['kept_share']}) kept mean {res['kept_mean']} skipped {res['skipped_mean']} diff {res['diff']} pct {res['control_pct']} p {res['perm_p']} wrecall_w {res['winner_recall_weighted']} lrecall {res['loser_recall']} blocks {res['sign_blocks']} slip8 {res['kept_mean_slip8']} | CPCV diff median {d['diff_median']} p5 {d['diff_p5']} share>0 {d['diff_share_positive']} ctl median {d.get('control_pct_median')} | id {res['id']}")
    GC = ["id", "family", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall", "loser_precision", "winner_recall", "winner_recall_weighted",
          "top_decile_winners_skipped", "kept_pf", "kept_mean_slip8", "sign_blocks", "kept_win_rate", "skipped_win_rate", "go_raw"]
    G = pd.DataFrame([dict(model=r["config"]["model"], skip_q=r["config"]["skip_q"], **{c: r.get(c) for c in GC}, **{f"cpcv_{k}": v for k, v in r["cpcv"].items()}) for r in gates])
    G.to_csv(os.path.join(HERE, "gates.csv"), index=False)
    pd.DataFrame([dict(model=m, skip_q=q, path=r["config"]["path"], **{c: r.get(c) for c in ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "loser_recall", "sign_blocks")})
                  for (m, q), rows in gate_paths.items() for r in rows]).to_csv(os.path.join(HERE, "cpcv_gate_paths.csv"), index=False)
    # ---------------- family statistics over the 12 OOF gate rows
    ids = [r["id"] for r in gates]; vecs = [H.load_vectors(i) for i in ids]
    fam = dict(design_family="window lengths x kernel counts x probes = 1 x 1 x 3", probes=["rocket (L2 logistic on PPV)", "pca16 (L2 logistic on PCA-16 of the window)", "stacked (HGB on base + PCA-16 of PPV)"],
               ledger_rows_oof=len(gates), ledger_rows_cpcv=sum(len(v) for v in gate_paths.values()), effective_trials=H.effective_trials(vecs),
               pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag="rocket_ceiling"))
    fam["spa_best"] = dict(model=gates[fam["spa"]["best"]]["config"]["model"], skip_q=gates[fam["spa"]["best"]]["config"]["skip_q"], id=ids[fam["spa"]["best"]])
    best = max(range(len(gates)), key=lambda i: gates[i]["diff"] if gates[i]["diff"] is not None else -np.inf)
    v = vecs[best]; msk = v["kept_n"] > 0
    def sharpe(vv):
        mm = vv["kept_n"] > 0; s = vv["kept_sum"][mm] / vv["kept_n"][mm]
        return float(s.mean() / s.std(ddof=1)) if len(s) > 2 and s.std(ddof=1) else np.nan
    srs = np.array([sharpe(x) for x in vecs]); srs = srs[np.isfinite(srs)]
    fam["best_by_diff"] = dict(model=gates[best]["config"]["model"], skip_q=gates[best]["config"]["skip_q"], id=ids[best], diff=gates[best]["diff"])
    fam["dsr_best"] = H.deflated_sharpe(v["kept_sum"][msk] / v["kept_n"][msk], len(ids), float(srs.var(ddof=1)) if len(srs) > 1 else None)
    fam["bootstrap_best"] = H.bootstrap_ci(v, tag="rocket_ceiling|best")
    passed, checks = H.go_no_go(gates[best], TF, cpcv=gates[best]["cpcv"], pbo_value=fam["pbo_diff"]["pbo"], dsr=fam["dsr_best"], spa_p=fam["spa"]["spa_p"], boot=fam["bootstrap_best"])
    fam["go_no_go_best"] = dict(passed=passed, checks=checks, note="information only: this study never gets a candidate slot (Judge 1)")
    log(f"family: eff trials {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} (best {fam['spa_best']}), best-by-diff {fam['best_by_diff']} DSR p {fam['dsr_best'].get('p')} boot {fam['bootstrap_best']['diff_ci']} go {passed}")

    # ---------------- distillation (only past the pre-registered stop)
    distil = dict(ran=False, reason=f"pre-registered stop: CPCV p5 gain stacked - tabular = {cpcv['gain_stacked']['p5']} < {STOP_P5}") if stop else distillation(T, oof, folds, Xb, base_cols, is_rows, pos)
    if distil["ran"]: log(f"distillation: {json.dumps({k: distil[k] for k in ('fidelity_oof', 'fidelity_balanced_oof', 'rule_ledger_id', 'rule_diff', 'probe_diff', 'share_of_probe_effect')}, default=str)}")
    else: log(f"distillation not run: {distil['reason']}")

    res = dict(study="rocket_ceiling", tf=TF, label=LABEL, seed=SEED, L=L, K=K, C=C, alphas=ALPHAS, inner_folds=N_INNER, n_bias=N_BIAS, skip_q=list(SKIP_Q), stop_rule=f"CPCV p5 gain (stacked - tabular) < {STOP_P5}",
               units=dict(n=T.n, is_=n_is, oos_row_count_only=int(T.oos_mask.sum()), is_win_rate=round(float(y.mean()), 4), is_mean_net=round(float(T.net[is_rows].mean()), 2)),
               windows=dict(shape=list(W.shape), mb=round(W.nbytes / 2 ** 20, 1), build_s=t_win, channel_means=np.round(W.mean(axis=(0, 2)), 4).tolist(), channel_sds=np.round(W.std(axis=(0, 2)), 4).tolist(),
                            na_flag_share=round(float(W[:, 4].mean()), 4), same_session_share=round(float(W[:, 6].mean()), 4), share_windows_crossing_session_start=round(float((W[:, 6].min(axis=1) == 0).mean()), 4)),
               trunc_check=tc, kernels=dict(seed=SEED, dilation_counts=np.bincount(kern["dil"], minlength=L // 4 + 1)[1:].tolist(), pair_share=round(float((kern["ch"][:, 1] >= 0).mean()), 3), channel_use=np.bincount(kern["ch"][kern["ch"] >= 0], minlength=C).tolist(), file="kernels.npz"),
               design=dict(base_columns=len(base_cols), flattened_window=int(Wflat.shape[1])),
               timing=dict(jit_s=t_jit, one_transform_s=t_tr, models_done_s=t_models, fold_s_purged=[f["fold_s"] for f in folds], fold_s_cpcv_mean=round(float(np.mean([c["fold_s"] for c in cp])), 1),
                           stage_s_mean={k: round(float(np.mean([f["times"][k] for f in folds + cp])), 2) for k in folds[0]["times"]}, rss_after_models_mb=rss_models, peak_rss_models_mb=peak_models),
               oof12=dict(auc=oof_auc, ap=oof_ap, per_block_auc=per_block_auc, per_block_gain=gain12, judge1_all_blocks_below_0_02=bool(all(g < 0.02 for g in gain12["stacked-tabular"])),
                          alpha_rocket=[f["alpha"]["rocket"] for f in folds], alpha_pca16=[f["alpha"]["pca16"] for f in folds], inner_auc_at_chosen=[f["inner_oof_auc_at_chosen"] for f in folds]),
               cpcv=dict(paths=len(path_rows), **cpcv, split_gain_stacked=dict(min=round(min(split_gain["stacked-tabular"]), 4), median=round(float(np.median(split_gain["stacked-tabular"])), 4), share_below_0_02=round(float(np.mean(np.array(split_gain["stacked-tabular"]) < 0.02)), 3)),
                         split_gain_rocket=dict(min=round(min(split_gain["rocket-tabular"]), 4), median=round(float(np.median(split_gain["rocket-tabular"])), 4)),
                         alpha_rocket_counts={str(a): int(sum(1 for c in cp if c["alpha"]["rocket"] == a)) for a in ALPHAS}, alpha_pca16_counts={str(a): int(sum(1 for c in cp if c["alpha"]["pca16"] == a)) for a in ALPHAS}),
               stop=dict(triggered=bool(stop), p5_gain_stacked=cpcv["gain_stacked"]["p5"], threshold=STOP_P5),
               gates=[dict(model=r["config"]["model"], skip_q=r["config"]["skip_q"], **{c: r.get(c) for c in GC}, cpcv=r["cpcv"]) for r in gates],
               family=fam, distillation=distil, candidate_slot="none (Judge 1: this study never gets a candidate slot; its trials still count)")
    res["timing"]["total_s"] = round(time.time() - T0, 1); res["timing"]["peak_rss_mb"] = peak_rss_mb(); res["ledger_sha_after"] = H.ledger_sha()
    jdump(res, os.path.join(HERE, "results.json"))
    log(f"done in {res['timing']['total_s']}s; peak RSS {res['timing']['peak_rss_mb']} MB; ledger sha {res['ledger_sha_after']}")


def distillation(T, oof, folds, Xb, base_cols, is_rows, pos):
    """Past the stop only: the probe's bottom tercile (per-fold threshold from the training fold's inner OOF) -> depth-3 tree on
    scalar as-of features (base + the three win_* summaries); OOF fidelity; the tree's rule as a ledger row rocket/distilled."""
    ext = pd.read_parquet(os.path.join(OUT, "features_ext", TF, "ext_features.parquet"), columns=["setup_i", *WIN_EXT]).set_index("setup_i")
    E = ext.reindex(T.setup_i[is_rows])[list(WIN_EXT)].to_numpy(dtype=float)
    Xd = np.hstack([Xb, E]); cols = base_cols + list(WIN_EXT)
    target = np.zeros(T.n, dtype=bool)                                 # True = predicted loser (bottom tercile of the probe score)
    for b, (tr, te) in enumerate(H.purged_splits(T)):
        thr = float(np.quantile(oof["rocket"][T.is_mask & (T.block != b)], 1 / 3)) if False else None
        # the tercile threshold from the training fold's inner OOF is not stored per fold; use the training-fold OOF of the 12-block
        # scheme restricted to the training blocks (out-of-fold for those rows, never the test block)
        tr_scores = oof["rocket"][tr]; thr = float(np.quantile(tr_scores, 1 / 3))
        target[te] = oof["rocket"][te] < thr
    yt = target[is_rows].astype(int)
    fid = np.full(T.n, np.nan)
    for tr, te in H.purged_splits(T):
        d = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=0).fit(np.nan_to_num(Xd[pos[tr]], nan=-999.0), target[tr])
        fid[te] = d.predict(np.nan_to_num(Xd[pos[te]], nan=-999.0))
    f = fid[is_rows].astype(bool)
    acc = float((f == target[is_rows]).mean()); bal = float(0.5 * ((f & target[is_rows]).sum() / max(1, target[is_rows].sum()) + (~f & ~target[is_rows]).sum() / max(1, (~target[is_rows]).sum())))
    d = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=0).fit(np.nan_to_num(Xd, nan=-999.0), yt)
    rules = export_text(d, feature_names=cols, max_depth=3)
    keep_rule = ~fid.astype(bool); keep_rule[~T.is_mask] = True
    keep_probe = ~target; keep_probe[~T.is_mask] = True
    r_rule = H.score(T, keep_rule, "rocket/distilled", dict(model="tree_depth3_on_probe_bottom_tercile", min_samples_leaf=50, features="base+win_*"), script=__file__)
    r_probe = H.score(T, keep_probe, "rocket/rocket", dict(model="rocket", skip_q=round(1 / 3, 4), threshold="tercile of training-fold OOF"), script=__file__)
    share = (r_rule["diff"] / r_probe["diff"]) if r_probe["diff"] else None
    return dict(ran=True, fidelity_oof=round(acc, 4), fidelity_balanced_oof=round(bal, 4), rule_ledger_id=r_rule["id"], rule_diff=r_rule["diff"], probe_ledger_id=r_probe["id"], probe_diff=r_probe["diff"],
                share_of_probe_effect=None if share is None else round(float(share), 3), tree_text=rules, passes=dict(fidelity_ge_085=acc >= 0.85, keeps_ge_70pct=(share is not None and share >= 0.7)))


if __name__ == "__main__":
    main()
