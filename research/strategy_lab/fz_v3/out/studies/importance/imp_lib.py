"""Importance study library (DESIGN_PANEL: quant-ml-canon-feature-importance, both judges' fixes; feature hand-offs from
regime-breaks, regime-states, motif-shapelet, rocket-probe). Every definition below is fixed before any number is looked at.

Feature set        harness.design(T) (base as-of columns, one-hot text, 0/1 booleans) + the 61 extended as-of columns of
                   features_ext/<tf>/ext_features.parquet joined on setup_i. Columns with > 40% NaN on IS rows dropped and listed;
                   constant columns dropped; exact duplicates (|Spearman| > 0.999 on IS) dropped, the first kept; of a two-level
                   one-hot the second level is dropped (its complement carries the same information). Missing indicators
                   `<col>__na` for every kept column with a NaN on IS, de-duplicated by NaN pattern (one indicator per pattern,
                   named after its first column; the covered columns are listed). Median imputation uses the TRAINING fold's
                   medians (bagging); xgboost sees NaN as such.
Label / weights    L1 binary (net > 0); sample weight = |net| winsorised at the training fold's 99th percentile, normalised to
                   mean 1; class balance by DecisionTreeClassifier(class_weight="balanced"). Test-fold weights for the weighted
                   log-loss: |net| of the test rows winsorised at the SAME training-fold p99, normalised to mean 1 on the fold.
Model              BaggingClassifier(DecisionTreeClassifier(max_depth=4 (3 and 5 as a sensitivity), min_weight_fraction_leaf=0.05,
                   class_weight="balanced"), n_estimators=300, bootstrap, oob_score) under harness.purged_splits (12 blocks).
tau                chosen INSIDE the training fold on the bagging's out-of-bag probabilities: the p_win threshold on the grid
                   0.05..0.95 (step 0.01) maximising the kept mean net subject to |net|-weighted winner recall >= 0.90.
Clustering         Spearman correlation on IS rows (pairwise-complete; undefined -> 0), distance sqrt(0.5 (1 - rho)), scipy
                   average linkage, the cut with the best silhouette (precomputed distance) over 20..40 clusters.
Representative     per cluster, by config-expressibility tier (0 = integer-valued / boolean / one-hot / card or fz field;
                   1 = ATR ratio or other dimensionless; 2 = raw points / levels), then coverage, then centrality (mean |rho| to
                   the cluster's members).
Clustered MDA      per fold, the features of a cluster are permuted JOINTLY on the test rows (same row permutation for every
                   member, missing indicators included), 5 permutations; recorded per fold: the increase in OOF weighted log-loss
                   (primary: the pass rule and the ranks) and the decrease in the OOF kept-vs-skipped mean-net difference at the
                   fold's tau (harness.metrics, controls off; secondary, reported with its own ratio). Mean and std across the 12
                   folds; a cluster passes MDA when mean > std (log-loss).
MDI                per fold forest: sum over trees of feature_importances_ / n_trees, summed per cluster, averaged over folds.
SFI                each cluster alone (its members + indicators), same folds, same weights, same tau rule; its OOF gate is a
                   ledger row (family importance/sfi).
Stability          the per-fold, per-permutation OOF probabilities are kept per row, so the log-loss MDA is re-computed on the
                   rows of each period (minute: calendar years 2022 (with 2021-10..12), 2023, 2024, 2025; 5minute: halves
                   2021-10..2023-09 and 2023-10..2025-12); a cluster ranks top-8 in >= 3 of 4 years (minute) / in both halves
                   (5minute) or it is not shortlisted. The models are the 12 fold models (trained on the other 11 purged blocks).
Orthogonal check   PCA on the standardised (IS-median-imputed, z-scored) IS features; a bagging of the same shape on the PC
                   scores; scipy.stats.weightedtau between its MDI per component and the eigenvalues.
Interactions       xgboost max_depth 3, 200 rounds, eta 0.05, the same folds, on the top-40 features by clustered MDA (clusters
                   in MDA order, members in MDI order); shap.TreeExplainer(...).shap_interaction_values on the OOF rows; pairs
                   ranked by mean |interaction|; the top 5 pairs carry the gain-weighted median split point of each feature over
                   the tree paths where both features occur (all 12 fold boosters pooled).
"""
import os, re, sys, json, time, hashlib, datetime as D
import numpy as np, pandas as pd
import psutil
from scipy import stats as sst
from scipy.cluster import hierarchy as sch
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import silhouette_score, roc_auc_score
from sklearn.decomposition import PCA

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H  # noqa: E402

NAN_DROP = 0.40
N_TREES, MIN_LEAF, DEPTH_MAIN, DEPTHS_SENS = 300, 0.05, 4, (3, 5)
N_PERM, TAU_GRID, WREC_MIN = 5, np.round(np.arange(0.05, 0.951, 0.01), 2), 0.90
K_RANGE = range(20, 41)
TOP_K_STAB, TOP_INTER, TOP_PAIRS, XGB_ROUNDS, XGB_ETA, XGB_DEPTH = 8, 40, 5, 200, 0.05, 3
N_JOBS = 4
XGB_JOBS = int(os.environ.get("IMP_XGB_JOBS", "1"))   # xgboost's OpenMP spin-wait is pathological on the shared box: 0.7 s at 1 thread vs 14 s at 2 (xgb_probe.log)
BAG_JOBS = int(os.environ.get("IMP_BAG_JOBS", str(N_JOBS)))
PERIODS = {"minute": lambda d: ("2022" if d[:4] in ("2021", "2022") else d[:4]),
           "5minute": lambda d: ("H1_2021-10..2023-09" if d <= "2023-09-30" else "H2_2023-10..2025-12")}
STAB_MIN_PERIODS = {"minute": 3, "5minute": 2}


def rss_mb(): return round(psutil.Process().memory_info().rss / 2 ** 20, 1)


def log(msg, fh=None):
    line = f"[{D.datetime.now().strftime('%H:%M:%S')} rss {rss_mb()} MB] {msg}"
    print(line, flush=True)
    if fh: fh.write(line + "\n"); fh.flush()


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- README definitions
def _expand(tok):
    m = re.search(r"\{([^}]*)\}", tok)
    if not m: return [tok]
    out = []
    for alt in m.group(1).split(","):
        out += _expand(tok[:m.start()] + alt.strip() + tok[m.end():])
    return out


def readme_defs():
    """column -> (readme, definition) from the tables of data/README.md and features_ext/README.md."""
    defs = {}
    for name, path in (("data/README.md", os.path.join(OUT, "data", "README.md")),
                       ("features_ext/README.md", os.path.join(OUT, "features_ext", "README.md"))):
        n_cols, parse = 0, False
        for line in open(path, encoding="utf-8"):
            if line.startswith("| column"):                      # a table header: parse only tables that carry a definition column
                n_cols, parse = line.count("|") - 1, "definition" in line; continue
            if not (parse and line.startswith("| `")): continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) > n_cols >= 2:                          # a literal '|' inside the definition cell: merge the extra splits into it
                extra = len(cells) - n_cols
                cells = [cells[0], " | ".join(cells[1:2 + extra])] + cells[2 + extra:]
            if len(cells) < 2: continue
            toks = [t.strip().strip("`").replace("{j}", "{0,1,2,3}") for t in re.findall(r"`([^`]*)`", cells[0])]
            base_prefix = None
            for t in toks:
                for col in _expand(t):
                    if col.startswith("_") and base_prefix is not None:
                        for bp in base_prefix: defs.setdefault(bp + col, (name, cells[1]))
                    else:
                        defs.setdefault(col, (name, cells[1]))
                if not t.startswith("_"):
                    ex = _expand(t)
                    # the prefix before the last underscore-suffix, e.g. hv{2,3}_bars_since -> hv2, hv3 ; touch_{..}_n -> touch_prot ...
                    base_prefix = [re.sub(r"_(bars_since|n)$", "", e) for e in ex]
    card = "the FZ card at the SETUP bar (card_*, as-of; FZ.md section 7): the field fz.run writes on the card as of bar k"
    fz = "the FZ ledger as of the SETUP bar (fz_*, as-of; FZ.md section 8): fz.run's row field as of bar k"
    return defs, card, fz


def define(col, defs, card, fz):
    src = col.split("=")[0].replace("__na", "")
    if src in defs: name, d = defs[src]
    elif src.startswith("card_"): name, d = "data/README.md", card
    elif src.startswith("fz_"): name, d = "data/README.md", fz
    elif src.startswith("rv_choch_since_bos"): name, d = "features_ext/README.md", "input 6 of the state models = n_choch_since_bos"
    else: name, d = "?", "no README row found"
    extra = ""
    if "=" in col: extra = f" [one-hot level `{col.split('=', 1)[1]}`]"
    if col.endswith("__na"): extra = " [missing indicator: 1 when the column is NaN]"
    return dict(source=src, readme=name, definition=d + extra)


# ---------------------------------------------------------------- feature assembly
def tier_of(col, X_is):
    """0 = integer-valued / boolean / one-hot / card or fz field; 1 = ratio or other dimensionless; 2 = raw points / levels."""
    if col.endswith("__na") or "=" in col: return 0
    v = X_is[col].dropna().to_numpy()
    if len(v) and np.all(np.abs(v - np.round(v)) < 1e-9): return 0
    src = col
    if src.startswith("card_") or src.startswith("fz_"):          # card / fz fields rank with the integer counts (the design's order)
        return 2 if (src.endswith("_pts") or src in ("fz_band_width", "fz_dist_band_edge_ahead", "fz_dist_band_edge_behind")) else 0
    if src.endswith("_pts") or src in ("sl", "atr14", "ffd_close_dstar", "ffd_vol_dstar", "rv_absret", "today_net_asof",
                                       "last_closed_net_asof"):
        return 2
    return 1


def assemble(tf, logf=None):
    T = H.load(tf)
    X, src = H.design(T)
    E = pd.read_parquet(os.path.join(OUT, "features_ext", tf, "ext_features.parquet"))
    ext_cols = [c for c in E.columns if c != "setup_i"]
    assert len(ext_cols) == 61, len(ext_cols)
    E = E.set_index("setup_i").reindex(T.setup_i).reset_index(drop=True)
    assert not set(ext_cols) & set(X.columns)
    Xa = pd.concat([X.reset_index(drop=True), E[ext_cols]], axis=1)
    is_mask = T.is_mask
    meta = dict(tf=tf, n_units=int(T.n), n_is=int(is_mask.sum()), base_design_cols=int(X.shape[1]), ext_cols=len(ext_cols),
                text_cols_dropped_by_design=[c for c in T.asof_columns() if c not in set(src.values())])
    nan_share = Xa[is_mask].isna().mean()
    drop_nan = nan_share[nan_share > NAN_DROP]
    meta["dropped_nan_gt_40pct"] = {c: round(float(v), 4) for c, v in drop_nan.items()}
    Xa = Xa.drop(columns=list(drop_nan.index))
    const = [c for c in Xa.columns if Xa.loc[is_mask, c].nunique(dropna=True) <= 1]
    meta["dropped_constant"] = const
    Xa = Xa.drop(columns=const)
    # two-level one-hot: keep the first level only
    onehot = {}
    for c in Xa.columns:
        if "=" in c: onehot.setdefault(c.split("=")[0], []).append(c)
    drop_lvl = [lv[1] for s, lv in onehot.items() if len(lv) == 2]
    meta["dropped_second_level_of_binary_onehot"] = drop_lvl
    Xa = Xa.drop(columns=drop_lvl)
    # exact duplicates on IS (|rho| > 0.999)
    rho = Xa[is_mask].rank().corr(min_periods=30).to_numpy()
    cols = list(Xa.columns); dup = []
    for j in range(len(cols)):
        if cols[j] in dup: continue
        for i in range(j):
            if cols[i] in dup: continue
            if abs(rho[i, j]) > 0.999:
                dup.append(cols[j]); meta.setdefault("dropped_duplicates", {})[cols[j]] = cols[i]; break
    Xa = Xa.drop(columns=dup)
    # missing indicators, de-duplicated by NaN pattern
    na = Xa[is_mask].isna()
    patterns = {}
    for c in Xa.columns:
        if na[c].any():
            key = hashlib.sha1(Xa[c].isna().to_numpy().tobytes()).hexdigest()
            patterns.setdefault(key, []).append(c)
    ind_cols, ind_cover = {}, {}
    for key, cs in patterns.items():
        nm = cs[0] + "__na"; ind_cols[nm] = Xa[cs[0]].isna().astype(float).to_numpy(); ind_cover[nm] = cs
    for nm, v in ind_cols.items(): Xa[nm] = v
    meta["missing_indicators"] = ind_cover
    meta["n_features_final"] = int(Xa.shape[1])
    log(f"{tf}: design {X.shape[1]} + ext {len(ext_cols)} -> dropped nan>{NAN_DROP:.0%} {len(drop_nan)}, const {len(const)}, "
        f"binary 2nd level {len(drop_lvl)}, duplicates {len(dup)}; + {len(ind_cols)} missing indicators = {Xa.shape[1]} features", logf)
    return T, Xa, meta


# ---------------------------------------------------------------- clustering
def cluster(Xa, is_mask, logf=None):
    Xi = Xa[is_mask]
    t0 = time.time()
    R = Xi.rank().corr(min_periods=30)          # Spearman: Pearson on ranks, pairwise-complete
    rho = np.nan_to_num(R.to_numpy(), nan=0.0); np.fill_diagonal(rho, 1.0); rho = np.clip((rho + rho.T) / 2, -1, 1)
    Dm = np.sqrt(np.clip(0.5 * (1 - rho), 0, None)); np.fill_diagonal(Dm, 0.0)
    Z = sch.linkage(sch.distance.squareform(Dm, checks=False), method="average")
    sil = {}
    for k in K_RANGE:
        lab = sch.fcluster(Z, k, criterion="maxclust")
        if len(set(lab)) < 2: continue
        sil[k] = float(silhouette_score(Dm, lab, metric="precomputed"))
    k_best = max(sil, key=sil.get)
    lab = sch.fcluster(Z, k_best, criterion="maxclust")
    cols = list(Xa.columns)
    clusters = {}
    for c, l in zip(cols, lab): clusters.setdefault(int(l), []).append(c)
    # rename clusters 0..K-1 by size then name
    order = sorted(clusters, key=lambda l: (-len(clusters[l]), clusters[l][0]))
    clusters = {i: clusters[l] for i, l in enumerate(order)}
    log(f"clustering: {len(cols)} features, silhouette best k={k_best} ({sil[k_best]:.4f}), clusters formed {len(clusters)}, {time.time() - t0:.1f}s", logf)
    # representatives
    coverage = 1 - Xi.isna().mean()
    idx = {c: i for i, c in enumerate(cols)}
    reps = {}
    for ci, mem in clusters.items():
        scored = []
        for c in mem:
            others = [idx[o] for o in mem if o != c]
            cent = float(np.mean([abs(rho[idx[c], o]) for o in others])) if others else 1.0
            scored.append((tier_of(c, Xi), -float(coverage[c]), -cent, c))
        scored.sort()
        t, cov, cent, c = scored[0]
        reps[ci] = dict(representative=c, tier=int(t), coverage=round(-cov, 4), centrality=round(-cent, 4),
                        why=f"tier {t} ({'integer/boolean/one-hot/card field' if t == 0 else 'ratio' if t == 1 else 'raw points/level'}), "
                            f"coverage {-cov:.3f}, mean |rho| to members {-cent:.3f}")
    return dict(clusters=clusters, reps=reps, silhouette={int(k): round(v, 4) for k, v in sil.items()}, k_best=int(k_best),
                rho=pd.DataFrame(rho, index=cols, columns=cols))


# ---------------------------------------------------------------- model pieces
def fold_weights(T, tr, te):
    a = np.abs(T.net)
    cap = float(np.quantile(a[tr], 0.99))
    w_tr = np.minimum(a[tr], cap); w_tr = w_tr / w_tr.mean()
    w_te = np.minimum(a[te], cap); w_te = w_te / w_te.mean()
    return w_tr, w_te, cap


def wlogloss(y, p, w):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return float(-(w * (y * np.log(p) + (1 - y) * np.log(1 - p))).sum() / w.sum())


def make_bag(depth, seed):
    return BaggingClassifier(DecisionTreeClassifier(max_depth=depth, min_weight_fraction_leaf=MIN_LEAF, class_weight="balanced"),
                             n_estimators=N_TREES, bootstrap=True, oob_score=True, n_jobs=BAG_JOBS, random_state=seed)


def fit_bag(Xtr, y, w, depth, seed):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bag = make_bag(depth, seed).fit(Xtr, y, sample_weight=w)
    oob = bag.oob_decision_function_[:, 1]
    oob = np.where(np.isnan(oob), np.nanmean(oob), oob)
    return bag, oob


def bag_predict(bag, X):
    acc = np.zeros(len(X))
    for est, feats in zip(bag.estimators_, bag.estimators_features_):
        acc += est.predict_proba(X[:, feats])[:, 1]
    return acc / len(bag.estimators_)


def bag_mdi(bag, n_features):
    imp = np.zeros(n_features)
    for est, feats in zip(bag.estimators_, bag.estimators_features_): imp[feats] += est.feature_importances_
    return imp / len(bag.estimators_)


def choose_tau(p, net, win):
    """The threshold on the training fold's OOB probabilities: max kept mean net s.t. |net|-weighted winner recall >= 0.90."""
    tot_w = net[win].sum()
    best, best_val, table = None, -np.inf, []
    for tau in TAU_GRID:
        kept = p >= tau
        if kept.sum() == 0: continue
        wrec = float(net[kept & win].sum() / tot_w) if tot_w > 0 else 1.0
        km = float(net[kept].mean())
        table.append((float(tau), int(kept.sum()), round(wrec, 4), round(km, 2)))
        if wrec >= WREC_MIN and km > best_val: best, best_val = float(tau), km
    if best is None: best = float(TAU_GRID[0])
    return best, table


def impute(Xtr, Xte):
    med = np.nanmedian(Xtr, axis=0); med = np.where(np.isnan(med), 0.0, med)
    return np.where(np.isnan(Xtr), med, Xtr), np.where(np.isnan(Xte), med, Xte)


def fold_diff(T, keep_te, te):
    keep = np.zeros(T.n, dtype=bool); keep[te] = keep_te
    m = H.metrics(T, keep, te, "mda", controls=False)
    return (np.nan if m["diff"] is None else float(m["diff"])), m


# ---------------------------------------------------------------- the full-model pass with clustered MDA
def full_model_pass(T, Xa, clusters, depth, tf, logf=None, with_mda=True):
    cols = list(Xa.columns); cidx = {c: i for i, c in enumerate(cols)}
    Xn = Xa.to_numpy(dtype=float)
    y = T.win.astype(int); net = T.net
    n = T.n
    p_oof = np.full(n, np.nan); tau_row = np.full(n, np.nan); w_row = np.full(n, np.nan); fold_row = np.full(n, -1)
    K = len(clusters)
    p_perm = np.full((K, N_PERM, n), np.nan, dtype=np.float32) if with_mda else None
    mdi = np.zeros((12, len(cols)))
    folds = []
    for f, (tr, te) in enumerate(H.purged_splits(T)):
        t0 = time.time()
        w_tr, w_te, cap = fold_weights(T, tr, te)
        Xtr, Xte = impute(Xn[tr], Xn[te])
        bag, oob = fit_bag(Xtr, y[tr], w_tr, depth, 1000 + f)
        tau, _ = choose_tau(oob, net[tr], T.win[tr])
        p = bag_predict(bag, Xte)
        p_oof[te] = p; tau_row[te] = tau; w_row[te] = w_te; fold_row[te] = f
        mdi[f] = bag_mdi(bag, len(cols))
        base_ll = wlogloss(y[te], p, w_te)
        base_diff, mbase = fold_diff(T, p >= tau, te)
        rec = dict(fold=f, n_tr=int(len(tr)), n_te=int(len(te)), cap_p99=round(cap, 1), tau=tau, oof_wlogloss=round(base_ll, 5),
                   oof_diff=None if np.isnan(base_diff) else round(base_diff, 2), kept_share=mbase["kept_share"],
                   oob_wlogloss_train=round(wlogloss(y[tr], oob, w_tr), 5), mda=None)
        if with_mda:
            ll_drop = np.zeros((K, N_PERM)); df_drop = np.zeros((K, N_PERM))
            for ci, mem in clusters.items():
                fi = [cidx[c] for c in mem]
                for r in range(N_PERM):
                    rng = np.random.default_rng(int(hashlib.sha1(f"{tf}|{depth}|{f}|{ci}|{r}".encode()).hexdigest()[:8], 16))
                    perm = rng.permutation(len(te))
                    Xp = Xte.copy(); Xp[:, fi] = Xte[perm][:, fi]
                    pp = bag_predict(bag, Xp)
                    p_perm[ci, r, te] = pp
                    ll_drop[ci, r] = wlogloss(y[te], pp, w_te) - base_ll
                    d, _ = fold_diff(T, pp >= tau, te)
                    df_drop[ci, r] = base_diff - d
            with np.errstate(all="ignore"), __import__("warnings").catch_warnings():
                __import__("warnings").simplefilter("ignore")
                rec["mda"] = dict(ll_drop=ll_drop.mean(axis=1).tolist(), diff_drop=np.nanmean(df_drop, axis=1).tolist(),
                                  diff_drop_nan=int(np.isnan(df_drop).sum()))
        folds.append(rec)
        log(f"depth {depth} fold {f}: n_tr {len(tr)} n_te {len(te)} tau {tau} ll {base_ll:.4f} diff {base_diff:.1f} kept {mbase['kept_share']} ({time.time() - t0:.1f}s)", logf)
    assert not np.isnan(p_oof[T.is_mask]).any()
    return dict(p_oof=p_oof, tau_row=tau_row, w_row=w_row, fold_row=fold_row, p_perm=p_perm, mdi=mdi, folds=folds, cols=cols)


def summarise_mda(res, clusters):
    K = len(clusters)
    ll = np.array([f["mda"]["ll_drop"] for f in res["folds"]])        # folds x K
    df = np.array([f["mda"]["diff_drop"] for f in res["folds"]])
    rows = []
    import warnings
    for ci in range(K):
        m_ll, s_ll = float(ll[:, ci].mean()), float(ll[:, ci].std(ddof=1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m_df, s_df = float(np.nanmean(df[:, ci])), float(np.nanstd(df[:, ci], ddof=1))
        rows.append(dict(cluster=ci, mda_ll_mean=m_ll, mda_ll_std=s_ll, mda_ll_ratio=(m_ll / s_ll if s_ll > 0 else np.nan),
                         mda_ll_pass=bool(m_ll > s_ll), mda_diff_mean=m_df, mda_diff_std=s_df,
                         mda_diff_ratio=(m_df / s_df if s_df > 0 else np.nan), mda_diff_pass=bool(m_df > s_df),
                         mda_ll_folds_positive=int((ll[:, ci] > 0).sum())))
    return pd.DataFrame(rows)


def period_mda(T, res, clusters, tf):
    """Log-loss MDA re-computed on the OOF rows of each period (the same fold models and permutations)."""
    is_idx = np.flatnonzero(T.is_mask)
    per = np.array([PERIODS[tf](d) for d in T.day])
    y = T.win.astype(int)
    out = {}
    for pname in sorted(set(per[is_idx])):
        rows = is_idx[per[is_idx] == pname]
        w = res["w_row"][rows]; base = wlogloss(y[rows], res["p_oof"][rows], w)
        vals = []
        for ci in range(len(clusters)):
            d = [wlogloss(y[rows], res["p_perm"][ci, r, rows].astype(float), w) - base for r in range(N_PERM)]
            vals.append(float(np.mean(d)))
        vals = np.array(vals)
        rank = (-vals).argsort().argsort() + 1
        out[pname] = dict(n_rows=int(len(rows)), n_winners=int(y[rows].sum()), mda_ll=vals.tolist(), rank=rank.tolist())
    return out


# ---------------------------------------------------------------- SFI
def sfi_pass(T, Xa, clusters, depth, tf, script, logf=None):
    Xn = Xa.to_numpy(dtype=float); cols = list(Xa.columns); cidx = {c: i for i, c in enumerate(cols)}
    y = T.win.astype(int); net = T.net
    rows = []
    for ci, mem in clusters.items():
        t0 = time.time()
        fi = [cidx[c] for c in mem]
        p_oof = np.full(T.n, np.nan); keep = np.zeros(T.n, dtype=bool); ll = []
        for f, (tr, te) in enumerate(H.purged_splits(T)):
            w_tr, w_te, cap = fold_weights(T, tr, te)
            Xtr, Xte = impute(Xn[tr][:, fi], Xn[te][:, fi])
            bag, oob = fit_bag(Xtr, y[tr], w_tr, depth, 2000 + f)
            tau, _ = choose_tau(oob, net[tr], T.win[tr])
            p = bag_predict(bag, Xte); p_oof[te] = p; keep[te] = p >= tau
            ll.append(wlogloss(y[te], p, w_te))
        cfg = dict(model="bagging_dt", depth=depth, trees=N_TREES, cluster=ci, n_features=len(mem), members=mem, tau="train-fold OOB rule")
        r = H.score(T, keep, "importance/sfi", cfg, script=script)
        is_idx = np.flatnonzero(T.is_mask)
        auc = float(roc_auc_score(y[is_idx], p_oof[is_idx]))
        rows.append(dict(cluster=ci, n_features=len(mem), sfi_oof_wlogloss=round(float(np.mean(ll)), 5), sfi_oof_auc=round(auc, 4),
                         ledger_id=r["id"], kept_share=r["kept_share"], kept_n=r["kept_n"], diff=r["diff"], perm_p=r["perm_p"],
                         control_pct=r["control_pct"], winner_recall_weighted=r["winner_recall_weighted"], loser_recall=r["loser_recall"],
                         sign_blocks=r["sign_blocks"], diff_top1_removed=r["diff_top1_removed"]))
        log(f"SFI cluster {ci} ({len(mem)} f): ll {np.mean(ll):.4f} auc {auc:.3f} diff {r['diff']} kept {r['kept_share']} ctrl {r['control_pct']} ({time.time() - t0:.1f}s)", logf)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- orthogonal check
def pca_check(T, Xa, depth, logf=None):
    is_idx = np.flatnonzero(T.is_mask)
    Xi = Xa.to_numpy(dtype=float)[is_idx]
    med = np.nanmedian(Xi, axis=0); med = np.where(np.isnan(med), 0.0, med)
    Xi = np.where(np.isnan(Xi), med, Xi)
    mu, sd = Xi.mean(axis=0), Xi.std(axis=0); sd = np.where(sd > 0, sd, 1.0)
    Zs = (Xi - mu) / sd
    pca = PCA(random_state=0).fit(Zs)
    S = pca.transform(Zs)
    a = np.abs(T.net[is_idx]); w = np.minimum(a, np.quantile(a, 0.99)); w = w / w.mean()
    bag, _ = fit_bag(S, T.win[is_idx].astype(int), w, depth, 4242)
    mdi = bag_mdi(bag, S.shape[1])
    ev = pca.explained_variance_
    wt = sst.weightedtau(mdi, ev)
    kt = sst.kendalltau(mdi, ev)
    n95 = int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_), 0.95) + 1)
    log(f"PCA check: {S.shape[1]} components, 95% variance in {n95}; weighted tau(MDI, eigenvalue) {wt.statistic:.4f}, Kendall tau {kt.statistic:.4f} (p {kt.pvalue:.3g})", logf)
    return dict(n_components=int(S.shape[1]), n_components_95pct=n95, weighted_kendall_tau=round(float(wt.statistic), 4),
                kendall_tau=round(float(kt.statistic), 4), kendall_p=float(kt.pvalue),
                top10_component_mdi=[round(float(v), 4) for v in mdi[:10]], top10_eigenvalue_share=[round(float(v), 4) for v in pca.explained_variance_ratio_[:10]])


# ---------------------------------------------------------------- interactions
def interactions(T, Xa, top_cols, tf, logf=None):
    import xgboost as xgb, shap, warnings
    Xn = Xa[top_cols].to_numpy(dtype=float)
    y = T.win.astype(int)
    safe = [f"f{i}" for i in range(len(top_cols))]
    M = np.zeros((len(top_cols), len(top_cols))); n_rows = 0
    ll, auc_p, auc_y = [], [], []
    splits = {}  # (a, b) -> list of (thr_a, thr_b, gain)
    for f, (tr, te) in enumerate(H.purged_splits(T)):
        t0 = time.time()
        w_tr, w_te, cap = fold_weights(T, tr, te)
        pos = y[tr].mean(); cw = np.where(y[tr] == 1, 0.5 / pos, 0.5 / (1 - pos))
        m = xgb.XGBClassifier(max_depth=XGB_DEPTH, n_estimators=XGB_ROUNDS, learning_rate=XGB_ETA, tree_method="hist", n_jobs=XGB_JOBS,
                              random_state=f)
        Dtr = pd.DataFrame(Xn[tr], columns=safe); Dte = pd.DataFrame(Xn[te], columns=safe)
        m.fit(Dtr, y[tr], sample_weight=w_tr * cw)
        p = m.predict_proba(Dte)[:, 1]
        ll.append(wlogloss(y[te], p, w_te)); auc_p.append(p); auc_y.append(y[te])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            iv = shap.TreeExplainer(m).shap_interaction_values(Dte)
        iv = np.asarray(iv)
        if iv.ndim == 4: iv = iv[..., -1]
        M += np.abs(iv).sum(axis=0); n_rows += len(te)
        # split points on paths where both features occur
        df = m.get_booster().trees_to_dataframe()
        parent = {}
        for _, r in df.iterrows():
            for ch in (r["Yes"], r["No"]):
                if isinstance(ch, str): parent[ch] = r["ID"]
        node = df.set_index("ID")
        for _, r in df[df["Feature"] != "Leaf"].iterrows():
            anc = parent.get(r["ID"]); a_feat = int(r["Feature"][1:])
            while anc is not None:
                ra = node.loc[anc]
                b_feat = int(ra["Feature"][1:])
                if b_feat != a_feat:
                    key = (min(a_feat, b_feat), max(a_feat, b_feat))
                    thr = (float(r["Split"]), float(ra["Split"])) if a_feat < b_feat else (float(ra["Split"]), float(r["Split"]))
                    splits.setdefault(key, []).append((thr[0], thr[1], float(r["Gain"]) + float(ra["Gain"])))
                anc = parent.get(anc)
        log(f"xgb fold {f}: ll {ll[-1]:.4f}, shap tensor {iv.shape} ({time.time() - t0:.1f}s)", logf)
    M /= n_rows
    auc = float(roc_auc_score(np.concatenate(auc_y), np.concatenate(auc_p)))
    pairs = []
    for i in range(len(top_cols)):
        for j in range(i + 1, len(top_cols)):
            pairs.append((float(M[i, j] + M[j, i]) / 2, i, j))
    pairs.sort(reverse=True)
    def wmedian(v, w):
        o = np.argsort(v); v, w = np.asarray(v)[o], np.asarray(w)[o]; c = np.cumsum(w); return float(v[np.searchsorted(c, c[-1] / 2)])
    top = []
    for s, i, j in pairs[:TOP_PAIRS * 4]:
        sp = splits.get((i, j), [])
        rec = dict(feature_a=top_cols[i], feature_b=top_cols[j], mean_abs_interaction=round(s, 6), n_paths_with_both=len(sp))
        if sp:
            ta, tb, g = zip(*sp)
            rec.update(split_a_gain_weighted_median=round(wmedian(ta, g), 4), split_b_gain_weighted_median=round(wmedian(tb, g), 4),
                       split_a_common=[round(float(v), 4) for v, _ in pd.Series(np.round(ta, 4)).value_counts().head(3).items()],
                       split_b_common=[round(float(v), 4) for v, _ in pd.Series(np.round(tb, 4)).value_counts().head(3).items()])
        top.append(rec)
    return dict(pairs_ranked=top, top5=top[:TOP_PAIRS], xgb_oof_wlogloss=round(float(np.mean(ll)), 5), xgb_oof_auc=round(auc, 4),
                matrix=pd.DataFrame(M, index=top_cols, columns=top_cols), main_effect_mean_abs=[round(float(M[i, i]), 6) for i in range(len(top_cols))])
