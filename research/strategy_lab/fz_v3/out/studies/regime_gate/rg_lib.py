"""regime_gate library (DESIGN_PANEL deep-sequence-regime-states as conditioned by both judges; 5 minutes only, Judge 1).

Definitions fixed before any number was looked at (also in FINDINGS.md section 1):

  unit / label   a harness row: a Foundation SETUP taken under the L1 (15:25) book, harness.load("5minute"); IS rows only
  models         hmm3, hmm4 (forward-filtered posteriors P(s_k = j | x_<=k), features_ext/5minute/ext_features.parquet columns
                 hmm{K}_p{j}), gmm4 (the no-dynamics posterior gmm4_p{j}), jump4 and jump3 (the ONLINE prefix state jump{K}_state,
                 a hard state: P(state = j) is its one-hot, so P(chop) is 0 or 1 and the tau grid is degenerate for them; every
                 tau cell is still a ledger row). jump3 was added after the importance study: its two columns form their own
                 cluster 25 on 5 minutes and that cluster's SFI gate was the importance family's SPA-best row (ledger
                 4535288bcf0f1148: kept share 0.868, diff +827 INR, control 100th pct, permutation p 0.078, 8/12 blocks); the claim
                 "the jump3 state marks losers" is exactly what this study tests with a nested threshold, so it is in the family.
  MAP state      argmax_j P_j at the SETUP bar (for a jump model the state itself)
  chop state     identified on the TRAINING rows of a fold as the MAP state with the lowest mean L1 net among the states with at
                 least one training row (the state with the worst L1 expectancy); nothing else is read on the test rows
  gate           skip the SETUP when P(chop) >= tau, tau in {0.5, 0.6, 0.7, 0.8, 0.9}
  nested tau     chosen on the training rows: the tau with the largest training kept-vs-skipped difference among the taus whose
                 training kept share is >= 0.20 (harness.GO kept_share_min) and which skip at least one training row; ties ->
                 the larger tau (skips less); no feasible tau -> tau 0.9 (recorded)
  grid cell      chop and tau on ALL IS rows (a trial), one ledger row per (model, tau): family regime_gate/<model>
  nested OOF     harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo), chop + tau per training
                 fold, the test-fold decisions concatenated: one ledger row per model, family regime_gate/<model>/nested
  CPCV           harness.cpcv_splits (66) with the same nested procedure -> harness.cpcv_paths (11 paths) -> harness.score_paths:
                 11 ledger rows per model, family regime_gate/<model>/nested/cpcv
  fixed rule     the (chop, tau) the same criterion picks on all IS rows = the in-sample-selected grid cell; it is what a config
                 would ship and what is replayed on the certificate null tapes
  comparator     the H2 hand rule "skip when n_choch_since_bos >= k" (family h2/choch, scope all: k = 2, 3, 4; ledger rows
                 cdd9b4281b0e451c, 6e32c51940ce5a11, 58431928cdcb8a87) at MATCHED skip fraction: the cell whose kept share is
                 closest to the nested OOF row's kept share; the scope-today cells are reported beside it
  family         every ledger row with family prefix regime_gate (grid cells, nested rows, CPCV paths, distilled rows): PBO
                 (diff and kept_mean), SPA (studentised and unstudentised), effective trials, DSR n_trials
  null tapes     the fixed rule replayed on the certificate tapes (studies/null_tapes_drift/tapes.py::tape_folders, healthy,
                 20 per generator): the frozen state models (fit window 2021-10-01..2023-09-30 of the REAL tape, exactly as
                 studies/ext_features/build_ext.py fitted them; the refit is verified against ext_features.parquet at every real
                 SETUP before any tape is touched) are run forward over each tape's bars, the rule applied at the tape's L1
                 units; tapes.null_tape_check_from_diffs on the per-tape differences; tape numbers never enter the ledger
  distillation   DecisionTreeClassifier(max_depth=3, random_state=0) on harness.design(T) (base as-of columns; the time proxies
                 sl and n_events_asof removed) predicting the fixed rule's skip decision; fidelity = out-of-fold accuracy under
                 harness.purged_splits (tree refit per fold) and in-sample accuracy, both read against the majority-class share;
                 >= 0.85 out of fold = expressible, else "not expressible compactly"; only then is the tree's OOF gate a ledger
                 row (family regime_gate/<model>/distilled)
  vocabulary     the frozen shortlist is EMPTY on both timeframes (features_shortlist/<tf>/shortlist.json, n_shortlisted 0), so
                 every column this study reads is "outside the frozen shortlist (importance rule failed for every cluster)";
                 every ledger row carries that note and any candidate would carry it in its provenance for the user to accept
                 or reject
"""
import os, sys, json, math
sys.dont_write_bytecode = True
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
EXT_DIR = os.path.join(OUT, "studies", "ext_features")
if EXT_DIR not in sys.path: sys.path.insert(0, EXT_DIR)
TAPES_DIR = os.path.join(OUT, "studies", "null_tapes_drift")
if TAPES_DIR not in sys.path: sys.path.insert(0, TAPES_DIR)
import harness as H                                                     # noqa: E402
import ext_lib as L                                                     # noqa: E402

TF = "5minute"
LABEL = "L1"
MODELS = {"hmm3": ("hmm", 3), "hmm4": ("hmm", 4), "gmm4": ("gmm", 4), "jump4": ("jump", 4), "jump3": ("jump", 3)}
MODEL_ORDER = ["hmm3", "hmm4", "gmm4", "jump4", "jump3"]
TAUS = [0.5, 0.6, 0.7, 0.8, 0.9]
KEPT_SHARE_MIN = H.GO["kept_share_min"]
FIDELITY_MIN = 0.85
VOCAB_NOTE = "outside the frozen shortlist (importance rule failed for every cluster)"
CHOP_RULE = "training-fold MAP state with the lowest mean L1 net"
TAU_RULE = "training-fold max kept-vs-skipped diff s.t. kept share >= 0.20 and >= 1 skip; ties -> larger tau; none -> 0.9"
H2_IDS = {("all", 2): "cdd9b4281b0e451c", ("all", 3): "6e32c51940ce5a11", ("all", 4): "58431928cdcb8a87",
          ("today", 2): "60d25ea57daf33dd", ("today", 3): "1210d3613c329844", ("today", 4): "d31cdd229b2fb904"}
SFI25_ID = "4535288bcf0f1148"

# the ext_features build constants (studies/ext_features/build_ext.py), copied so the refit is the same fit
FIT_FROM, FIT_TO = "2021-10-01", "2023-09-30"
RV_N = 36
RV_NAMES = ["absret", "range_atr", "body_frac", "logvol_rel20", "ev36", "choch_since_bos", "range36_atr", "ret36_atr"]
JUMP_LAMBDAS = [1, 2, 4, 8, 16, 32, 64, 128]
SEED = 0


# ---------------------------------------------------------------- posteriors at the SETUP bars (from ext_features.parquet)
def posterior_columns(model):
    kind, K = MODELS[model]
    return [f"jump{K}_state"] if kind == "jump" else [f"{kind}{K}_p{j}" for j in range(K)]


def load_ext(tf=TF):
    return pd.read_parquet(os.path.join(OUT, "features_ext", tf, "ext_features.parquet")).set_index("setup_i")


def posterior_matrix(ext, model, setup_i):
    """(n x K) P(state = j) at the given SETUP bars: the filtered / static posterior, or the one-hot of the online jump state."""
    kind, K = MODELS[model]
    sub = ext.loc[np.asarray(setup_i)]
    if kind == "jump":
        st = sub[f"jump{K}_state"].to_numpy(dtype=float)
        assert np.isfinite(st).all()
        P = np.zeros((len(st), K)); P[np.arange(len(st)), st.astype(int)] = 1.0
        return P
    P = sub[[f"{kind}{K}_p{j}" for j in range(K)]].to_numpy(dtype=float)
    assert np.isfinite(P).all()
    return P


def run_columns(model):
    kind, K = MODELS[model]
    return f"jump{K}_run" if kind == "jump" else f"hmm{K}_map_run" if kind == "hmm" else None


# ---------------------------------------------------------------- the chop state and the threshold (training rows only)
def state_table(P, net, win, idx):
    """MAP-state expectancy on rows idx: per state n, share, mean net, win rate, posterior mass share."""
    mp = np.argmax(P[idx], axis=1); K = P.shape[1]
    rows = []
    for j in range(K):
        m = mp == j
        rows.append(dict(state=j, n=int(m.sum()), share=round(float(m.mean()), 4) if len(idx) else None,
                         mean_net=round(float(net[idx][m].mean()), 2) if m.any() else None,
                         win_rate=round(float(win[idx][m].mean()), 4) if m.any() else None,
                         posterior_mass_share=round(float(P[idx, j].sum() / len(idx)), 4) if len(idx) else None))
    return rows


def chop_state(P, net, win, idx):
    tab = state_table(P, net, win, idx)
    means = [r["mean_net"] if r["mean_net"] is not None else np.inf for r in tab]
    return int(np.argmin(means)), tab


def choose_tau(P, chop, net, idx, taus=TAUS, kept_share_min=KEPT_SHARE_MIN):
    """The training-fold threshold: max training kept-vs-skipped diff s.t. kept share >= kept_share_min and >= 1 skipped row;
    ties -> the larger tau; none feasible -> max(taus). Returns (tau, trace)."""
    pc = P[idx, chop]; nn = net[idx]
    trace = []; best = None
    for tau in taus:
        skip = pc >= tau; nk = int((~skip).sum()); ns = int(skip.sum()); share = nk / len(idx)
        feas = share >= kept_share_min and ns > 0 and nk > 0
        diff = float(nn[~skip].mean() - nn[skip].mean()) if (ns > 0 and nk > 0) else None
        trace.append(dict(tau=tau, kept_share=round(share, 4), skipped_n=ns, train_diff=(round(diff, 2) if diff is not None else None), feasible=bool(feas)))
        if feas and (best is None or diff >= best[1]): best = (tau, diff)
    if best is None: return float(max(taus)), dict(trace=trace, feasible_any=False)
    return float(best[0]), dict(trace=trace, feasible_any=True)


def skip_mask(P, chop, tau):
    return P[:, chop] >= tau


def nested_decisions(P, net, win, splits, n_rows):
    """Apply the nested procedure over (train_idx, test_idx[, key]) splits; returns per-split records and, for purged splits,
    the OOF skip decision over all rows (NaN where no decision)."""
    recs = []; dec = np.full(n_rows, np.nan)
    for sp in splits:
        tr, te = sp[0], sp[1]; key = sp[2] if len(sp) > 2 else None
        chop, tab = chop_state(P, net, win, tr)
        tau, tr_ = choose_tau(P, chop, net, tr)
        sk = skip_mask(P, chop, tau)[te]
        dec[te] = sk.astype(float)
        recs.append(dict(key=key, n_train=int(len(tr)), n_test=int(len(te)), chop=chop, tau=tau, feasible_any=tr_["feasible_any"],
                         chop_train_n=tab[chop]["n"], chop_train_mean=tab[chop]["mean_net"], test_skipped=int(sk.sum()),
                         test_kept_share=round(float(1 - sk.mean()), 4) if len(te) else None, trace=tr_["trace"], state_table=tab))
    return recs, dec


# ---------------------------------------------------------------- the frozen state models: refit as build_ext.py did, verified, replayed
def regime_vector(bars, events):
    """The 8-feature per-bar vector of build_ext.py (same code path, same conventions), plus what the fits need."""
    B = bars; E = events.sort_values("seq")
    n = len(B); assert (B.i.to_numpy() == np.arange(n)).all()
    o, h, l, c, v, atr = (B[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close", "volume", "atr14"))
    sbar = B.session_bar.to_numpy(dtype=np.int64)
    r = L.gapfree_logret(c, o, sbar)
    ev_bar = E.i.to_numpy(dtype=np.int64); ev_bos = (E.kind.astype(str) == "BOS").to_numpy()
    ev_at, csb = L.event_counts(n, ev_bar, ev_bos)
    evN, rngN, retN = L.session_windows(h, l, c, o, atr, sbar, ev_at, RV_N)
    rng = h - l
    body = np.where(rng > 0, np.abs(c - o) / np.where(rng > 0, rng, 1.0), 0.0)
    med20 = pd.Series(v).rolling(20).median().shift(1).to_numpy()
    logvol_rel = np.log(np.maximum(v, 1.0) / np.maximum(med20, 1.0))
    RV = np.column_stack([np.abs(r), rng / atr, body, logvol_rel, evN.astype(float), csb.astype(float), rngN, retN])
    return RV


def zscore(RV, mu_z, sd_z):
    Z = (RV - mu_z) / sd_z
    return np.where(np.isfinite(Z), Z, 0.0)


def fit_frozen_models(data_dir, log=print):
    """Refit the 5minute state models exactly as build_ext.py did (same fit window, seeds, library calls); returns the frozen
    parameters. Deterministic: the build used random_state=0 everywhere."""
    from sklearn.mixture import GaussianMixture
    from sklearn.cluster import KMeans
    from hmmlearn.hmm import GaussianHMM
    B = pd.read_parquet(os.path.join(data_dir, "bars.parquet"), columns=["i", "date", "session_idx", "session_bar", "open", "high", "low", "close", "volume", "atr14", "split"])
    E = pd.read_parquet(os.path.join(data_dir, "events.parquet"), columns=["seq", "i", "kind"])
    date = B.date.astype(str).to_numpy(); is_mask = (B.split.astype(str) == "IS").to_numpy()
    fit_mask = is_mask & (date >= FIT_FROM) & (date <= FIT_TO)
    RV = regime_vector(B, E)
    mu_z = np.nanmean(RV[fit_mask], axis=0); sd_z = np.nanstd(RV[fit_mask], axis=0)
    Z = zscore(RV, mu_z, sd_z); Zfit = Z[fit_mask]
    frozen = dict(mu_z=mu_z, sd_z=sd_z, fit_bars=int(fit_mask.sum()), n_bars=int(len(B)))
    g = GaussianMixture(4, covariance_type="full", random_state=SEED, n_init=3, max_iter=300, reg_covar=1e-6).fit(Zfit)
    frozen["gmm4"] = dict(model=g, order=np.argsort(g.means_[:, 1]))
    log(f"  gmm4 refit: converged {g.converged_} in {g.n_iter_} it")
    for K in (3, 4):
        hm = GaussianHMM(n_components=K, covariance_type="diag", n_iter=200, tol=1e-3, random_state=SEED).fit(Zfit)
        means = np.asarray(hm.means_, dtype=float); var = np.asarray(hm._covars_, dtype=float)
        frozen[f"hmm{K}"] = dict(startprob=np.asarray(hm.startprob_, float), transmat=np.asarray(hm.transmat_, float), means=means, var=var,
                                 order=np.argsort(means[:, 1]))
        log(f"  hmm{K} refit: converged {hm.monitor_.converged} in {hm.monitor_.iter} it")
    nf, pf = Zfit.shape
    for K in (3, 4):
        km = KMeans(K, random_state=SEED, n_init=10).fit(Zfit)
        best = None
        for lam in JUMP_LAMBDAS:
            C = km.cluster_centers_.copy(); prev = None
            for it in range(50):
                st, obj = L.jump_viterbi(Zfit, C, float(lam))
                if prev is not None and np.array_equal(st, prev): break
                prev = st
                for s in range(K):
                    m = st == s
                    if m.any(): C[s] = Zfit[m].mean(axis=0)
            J = int(np.sum(st[1:] != st[:-1])); sse = float(np.sum((Zfit - C[st]) ** 2))
            bic = nf * pf * np.log(sse / (nf * pf)) + (K * pf + J) * np.log(nf * pf)
            if best is None or bic < best[0]: best = (bic, lam, C.copy())
        _, lam_star, C = best
        order = np.argsort(C[:, 1])
        frozen[f"jump{K}"] = dict(C=C[order], lam=float(lam_star))
        log(f"  jump{K} refit: lambda* = {lam_star}")
    frozen["Z_real"] = Z
    return frozen


def posteriors_on_bars(frozen, Z):
    """Per-bar posteriors / one-hot states of every model over a z-scored tape (frozen parameters, forward passes only)."""
    out = {}
    g = frozen["gmm4"]; out["gmm4"] = g["model"].predict_proba(Z)[:, g["order"]]
    for K in (3, 4):
        f = frozen[f"hmm{K}"]
        post, _ = L.hmm_forward_filter(Z, f["startprob"], f["transmat"], f["means"], f["var"])
        out[f"hmm{K}"] = post[:, f["order"]]
        j = frozen[f"jump{K}"]
        st = L.jump_online(Z, j["C"], j["lam"])
        P = np.zeros((len(st), K)); P[np.arange(len(st)), st] = 1.0
        out[f"jump{K}"] = P
    return out


def verify_refit(frozen, ext, setup_i_all):
    """The refit reproduces ext_features.parquet at every real SETUP bar: max |posterior diff| per model; jump states identical."""
    post = posteriors_on_bars(frozen, frozen["Z_real"])
    ks = np.asarray(setup_i_all)
    rep = {}
    for m in MODEL_ORDER:
        P_ref = posterior_matrix(ext, m, ks); P_new = post[m][ks]
        rep[m] = dict(max_abs_diff=float(np.max(np.abs(P_ref - P_new))), identical_map=bool((np.argmax(P_ref, 1) == np.argmax(P_new, 1)).all()))
    return rep


def tape_posteriors(frozen, folder):
    B = pd.read_parquet(os.path.join(folder, "bars.parquet"), columns=["i", "session_idx", "session_bar", "open", "high", "low", "close", "volume", "atr14", "split"])
    E = pd.read_parquet(os.path.join(folder, "events.parquet"), columns=["seq", "i", "kind"])
    Z = zscore(regime_vector(B, E), frozen["mu_z"], frozen["sd_z"])
    return posteriors_on_bars(frozen, Z)


# ---------------------------------------------------------------- distillation (depth-3 tree on the base as-of features)
def base_design(T):
    X, src = H.design(T)
    keep = [c for c in X.columns if src[c] not in H.TIME_PROXIES]
    return X[keep], {c: src[c] for c in keep}


def tree_rules(tree, columns, src, skip_class=1):
    """Leaves predicting `skip_class` as rule-list conjunctions over source columns (one-hot splits -> ==/!= on the text column).
    NaN routing is not representable in the rule grammar (NaN never satisfies a comparison): translation agreement is reported."""
    t = tree.tree_; rules = []
    def walk(node, conds):
        if t.children_left[node] == -1:
            cls = int(np.argmax(t.value[node][0]))
            if cls == skip_class and len(conds) <= 3: rules.append({"if": [list(c) for c in conds], "then": "skip", "leaf_n": int(t.n_node_samples[node])})
            return
        col = columns[t.feature[node]]; thr = float(t.threshold[node]); s = src[col]
        if s != col and "=" in col:
            lv = col.split("=", 1)[1]
            walk(t.children_left[node], conds + [(s, "!=", lv)]); walk(t.children_right[node], conds + [(s, "==", lv)])
        else:
            walk(t.children_left[node], conds + [(col, "<=", round(thr, 6))]); walk(t.children_right[node], conds + [(col, ">", round(thr, 6))])
    walk(0, [])
    return rules


def distil(T, X, src, y_skip, is_idx, log=print):
    """Depth-3 tree fidelity to a skip decision y_skip (over all rows, read on is_idx): purged-CV OOF accuracy and in-sample."""
    from sklearn.tree import DecisionTreeClassifier
    Xv = X.to_numpy(dtype=float)
    oof = np.full(T.n, np.nan)
    for tr, te in H.purged_splits(T):
        clf = DecisionTreeClassifier(max_depth=3, random_state=SEED).fit(Xv[tr], y_skip[tr])
        oof[te] = clf.predict(Xv[te])
    y = y_skip[is_idx].astype(int); p = oof[is_idx].astype(int)
    full = DecisionTreeClassifier(max_depth=3, random_state=SEED).fit(Xv[is_idx], y)
    pin = full.predict(Xv[is_idx]).astype(int)
    def acc(a, b): return round(float((a == b).mean()), 4)
    def bal(a, b):
        r = []
        for c in (0, 1):
            m = a == c
            if m.any(): r.append(float((b[m] == c).mean()))
        return round(float(np.mean(r)), 4) if r else None
    skip_share = float(y.mean())
    rec = dict(n=int(len(y)), skip_share=round(skip_share, 4), majority_baseline=round(max(skip_share, 1 - skip_share), 4),
               fidelity_oof=acc(y, p), balanced_acc_oof=bal(y, p),
               skip_recall_oof=(round(float((p[y == 1] == 1).mean()), 4) if (y == 1).any() else None),
               skip_precision_oof=(round(float((y[p == 1] == 1).mean()), 4) if (p == 1).any() else None),
               fidelity_in_sample=acc(y, pin), balanced_acc_in_sample=bal(y, pin),
               features_used=sorted({X.columns[i] for i in full.tree_.feature if i >= 0}))
    rec["expressible"] = bool(rec["fidelity_oof"] >= FIDELITY_MIN and skip_share > 0)
    rules = tree_rules(full, list(X.columns), src)
    rec["rules"] = rules
    # translation agreement of the rule list (grammar: NaN never satisfies) with the tree's own in-sample prediction
    if rules:
        import tapes
        fires, _ = tapes.rule_mask(T.F.iloc[is_idx].reset_index(drop=True), [{"if": r["if"], "then": "skip"} for r in rules], T.tf)
        rec["rule_list_agreement_with_tree"] = acc(pin, fires.astype(int))
    else:
        rec["rule_list_agreement_with_tree"] = None
    return rec, oof


# ---------------------------------------------------------------- family statistics
def per_session_kept_mean(vec):
    m = vec["kept_n"] > 0
    return vec["kept_sum"][m] / vec["kept_n"][m]


def sharpe(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan


def family_stats(rows, tag):
    vecs = [H.load_vectors(r["id"]) for r in rows]
    srs = np.array([sharpe(per_session_kept_mean(v)) for v in vecs], dtype=float)
    out = dict(n_rows=len(rows), pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"),
               spa=H.spa(vecs, tag=tag), effective_trials=H.effective_trials(vecs),
               sr_var_trials=(float(np.nanvar(srs, ddof=1)) if np.isfinite(srs).sum() > 1 else None))
    sp = out["spa"]
    if sp.get("best") is not None: out["spa_best_row"] = dict(id=rows[sp["best"]]["id"], family=rows[sp["best"]]["family"], config=rows[sp["best"]]["config"])
    if sp.get("best_unstudentised") is not None:
        b = sp["best_unstudentised"]; out["spa_best_row_unstudentised"] = dict(id=rows[b]["id"], family=rows[b]["family"], config=rows[b]["config"])
    return out, vecs


def block_diffs(T, keep, is_idx):
    out = []
    for b in range(H.N_BLOCKS):
        rows = is_idx[T.block[is_idx] == b]; k = rows[keep[rows]]; s = rows[~keep[rows]]
        out.append(dict(block=b, n=int(len(rows)), kept_n=int(len(k)), diff=(round(float(T.net[k].mean() - T.net[s].mean()), 2) if len(k) and len(s) else None)))
    return out
