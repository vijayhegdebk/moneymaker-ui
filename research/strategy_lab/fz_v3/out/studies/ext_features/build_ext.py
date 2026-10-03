"""Study ext_features: the extended as-of scalar features the design panel hands to the importance study (and nothing else).

    python build_ext.py --tf minute   --data ../../data/minute                         --out ../../features_ext/minute
    python build_ext.py --tf minute   --data ../../data/minute/trunc_20250630_120000   --out ../../features_ext/minute/trunc_20250630_120000

Writes <out>/ext_features_all.parquet (one row per SETUP of <data>/features.parquet, keyed by setup_i; every candidate column,
before the truncation diff) and <out>/ext_fit_report.json (d*, ADF tables, BOCPD priors, state means, jump lambda, timings, coverage).

Sources (DESIGN_PANEL.md, judges' fixes binding): quant-ml-canon-feature-importance (FFD), quant-ml-canon-regime-breaks (BSADF,
CUSUM filter, CSW; features only, no gate), deep-sequence-regime-states (BOCPD, GMM, forward-filtered HMM, jump model; features
only, no tau grid), deep-sequence-motif-shapelet (nn_dist_prefix / p1_dist_prefix only), deep-sequence-rocket-probe (three window
scalars only). Hindsight proxies (deep-sequence-vision-labels) are labels and are not computed here.

Fit window for every unsupervised fit and every z-scoring statistic: the IS bars of sessions 2021-10-01 .. 2023-09-30 (the first
IS half). Label-free. The second IS half and OOS never enter a fit; inference is a forward pass over the whole tape from bar 0
with the frozen model. Every feature at SETUP bar k uses bars <= k.
"""
import os, sys, json, time, argparse, warnings
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext_lib as L                                                    # noqa: E402

warnings.filterwarnings("ignore")
FIT_FROM, FIT_TO = "2021-10-01", "2023-09-30"
IS_END = "2025-12-31"
FFD_D_GRID = [round(0.1 * i, 1) for i in range(1, 11)]
FFD_CUT, FFD_Z = 1e-4, 60
TF = {"minute": dict(bsadf_W=375, bsadf_min=60, novelty_m=(30, 60), win_L=60),
      "5minute": dict(bsadf_W=75, bsadf_min=15, novelty_m=(12, 24), win_L=12)}
CUSUM_WIN = 60
CSW_B = 4.6                                                            # Chu-Stinchcombe-White b_0.05 (AFML 17.4.1)
BOCPD_H, BOCPD_RMAX = (60, 240), 400
STATE_K = (3, 4)
JUMP_LAMBDAS = [1, 2, 4, 8, 16, 32, 64, 128]
RV_N = 36
RV_NAMES = ["absret", "range_atr", "body_frac", "logvol_rel20", "ev36", "choch_since_bos", "range36_atr", "ret36_atr"]
SEED = 0


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", required=True, choices=list(TF)); ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n_jobs", type=int, default=4)
    A = ap.parse_args()
    P = TF[A.tf]; os.makedirs(A.out, exist_ok=True)
    T0 = time.time(); rep = dict(tf=A.tf, data=os.path.abspath(A.data), fit_window=[FIT_FROM, FIT_TO], timings={})

    # ------------------------------------------------------------ load
    t0 = time.time()
    B = pd.read_parquet(os.path.join(A.data, "bars.parquet"), columns=["i", "datetime", "date", "session_idx", "session_bar", "open", "high", "low", "close", "volume", "atr14", "split"])
    E = pd.read_parquet(os.path.join(A.data, "events.parquet"), columns=["seq", "i", "kind"]).sort_values("seq")
    F = pd.read_parquet(os.path.join(A.data, "features.parquet"), columns=["setup_i", "dir_sign", "n_choch_since_bos"]).sort_values("setup_i").reset_index(drop=True)
    S = pd.read_parquet(os.path.join(A.data, "sessions.parquet"))
    n = len(B); assert (B.i.to_numpy() == np.arange(n)).all()
    o, h, l, c, v, atr = (B[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close", "volume", "atr14"))
    sbar = B.session_bar.to_numpy(dtype=np.int64); sidx = B.session_idx.to_numpy(dtype=np.int64)
    date = B.date.astype(str).to_numpy()
    is_mask = (B.split.astype(str) == "IS").to_numpy()
    fit_mask = is_mask & (date >= FIT_FROM) & (date <= FIT_TO)
    ks = F.setup_i.to_numpy(dtype=np.int64); sg = F.dir_sign.to_numpy(dtype=np.int64)
    assert ks.max() < n
    rep.update(bars=int(n), setups=int(len(ks)), fit_bars=int(fit_mask.sum()), fit_sessions=int(len(set(sidx[fit_mask].tolist()))),
               fit_last_bar=int(np.flatnonzero(fit_mask).max()), is_bars=int(is_mask.sum()))
    log(f"{A.tf}: {n} bars, {len(ks)} setups, fit window {rep['fit_bars']} bars / {rep['fit_sessions']} sessions (bars 0..{rep['fit_last_bar']})")
    logc = np.log(c); logv = np.log(np.maximum(v, 1.0))
    r = L.gapfree_logret(c, o, sbar)
    out = {"setup_i": ks}
    rep["timings"]["load"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ FFD family (AFML ch. 5) + ADF (statsmodels, constant + 2 lags)
    t0 = time.time()
    from statsmodels.tsa.stattools import adfuller
    ffd = {}
    for name, y in (("close", logc), ("vol", logv)):
        tab = []; d_fit = None; d_is = None
        for d in FFD_D_GRID:
            w = L.ffd_weights(d, FFD_CUT); x = L.ffd_series(y, w)
            row = dict(d=d, window=int(len(w)))
            for tag, msk in (("fit", fit_mask), ("is", is_mask)):
                xx = x[msk]; xx = xx[np.isfinite(xx)]
                res = adfuller(xx, maxlag=2, autolag=None, regression="c")
                row[f"adf_{tag}"] = round(float(res[0]), 3); row[f"crit5_{tag}"] = round(float(res[4]["5%"]), 3); row[f"nobs_{tag}"] = int(res[3])
                row[f"pass_{tag}"] = bool(res[0] < res[4]["5%"])
            tab.append(row)
            if d_fit is None and row["pass_fit"]: d_fit = d
            if d_is is None and row["pass_is"]: d_is = d
        d_star = d_fit                                                   # chosen on the fit window (a subset of IS); the IS-wide d* is reported next to it
        w = L.ffd_weights(d_star, FFD_CUT); x = L.ffd_series(y, w)
        ffd[name] = dict(table=tab, d_star_fit=d_fit, d_star_is=d_is, d_star_used=d_star, window_used=int(len(w)), agree=bool(d_fit == d_is))
        out[f"ffd_{name}_dstar"] = x[ks]; out[f"ffd_{name}_dstar_z60"] = L.rolling_z(x, FFD_Z)[ks]
        log(f"FFD {name}: d*(fit) = {d_fit}, d*(IS) = {d_is}, window {len(w)} bars")
    rep["ffd"] = ffd; rep["timings"]["ffd"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ BSADF at SETUP bars (numba)
    t0 = time.time()
    bs = np.full(len(ks), np.nan); bl = np.full(len(ks), np.nan)
    for q, k in enumerate(ks):
        bs[q], bl[q] = L.bsadf_at(logc, int(k), P["bsadf_W"], P["bsadf_min"])
    out["bsadf_close"] = bs; out["bsadf_close_win"] = bl
    rep["bsadf"] = dict(W=P["bsadf_W"], min_window=P["bsadf_min"], lags=2, series="log close (window demeaned by its first value)")
    rep["timings"]["bsadf"] = round(time.time() - t0, 1); log(f"BSADF done ({rep['timings']['bsadf']}s)")

    # ------------------------------------------------------------ CUSUM filter on gap-free log returns, h = atr14 / close
    t0 = time.time()
    ev = L.cusum_filter(r, atr / c)
    cnt, since = L.events_window_and_since(ev, CUSUM_WIN)
    out["cusum_events_60"] = cnt[ks].astype(float); out["cusum_bars_since"] = since[ks]
    rep["cusum"] = dict(threshold="atr14_t / close_t", lookback=CUSUM_WIN, events_total=int(ev.sum()), events_per_session=round(float(ev.sum()) / len(S), 2))
    rep["timings"]["cusum"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ CSW on the session's levels at SETUP bars
    t0 = time.time()
    ca = np.full(len(ks), np.nan); ce = np.full(len(ks), np.nan); cs_ = np.full(len(ks), np.nan)
    for q, k in enumerate(ks):
        a_, e_, s_ = L.csw_at(logc, int(k), int(k - sbar[k]), CSW_B)
        ca[q], ce[q], cs_[q] = a_, e_, s_ * sg[q] if s_ == s_ else np.nan
    out["csw_max_abs"] = ca; out["csw_max_exceed"] = ce; out["csw_sign_dir"] = cs_
    rep["csw"] = dict(b_alpha=CSW_B, series="log close over the session's bars up to k")
    rep["timings"]["csw"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ BOCPD on gap-free log returns and on log range (numba)
    t0 = time.time()
    logrng = np.log(np.maximum(h - l, 0.05))
    boc = {}
    for sname, series in (("ret", r), ("rng", logrng)):
        mu_f = float(np.mean(series[fit_mask])); sd_f = float(np.std(series[fit_mask]))
        x = (series - mu_f) / sd_f
        boc[sname] = dict(fit_mean=mu_f, fit_std=sd_f, prior=dict(mu0=0.0, kappa0=1.0, alpha0=1.0, beta0=1.0), rmax=BOCPD_RMAX)
        for H in BOCPD_H:
            m_, p_, s_ = L.bocpd(x, 1.0 / H, BOCPD_RMAX, 0.0, 1.0, 1.0, 1.0)
            out[f"bocpd_{sname}_h{H}_map"] = m_[ks].astype(float); out[f"bocpd_{sname}_h{H}_p10"] = p_[ks]; out[f"bocpd_{sname}_h{H}_since_reset"] = s_[ks]
            boc[sname][f"h{H}_resets_per_session"] = round(float(np.sum(np.diff(m_) < 0)) / len(S), 2)
        log(f"BOCPD {sname} done")
    rep["bocpd"] = boc; rep["timings"]["bocpd"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ the per-bar regime vector (8 features)
    t0 = time.time()
    ev_bar = E.i.to_numpy(dtype=np.int64); ev_bos = (E.kind.astype(str) == "BOS").to_numpy()
    ev_at, csb = L.event_counts(n, ev_bar, ev_bos)
    evN, rngN, retN = L.session_windows(h, l, c, o, atr, sbar, ev_at, RV_N)
    rng = h - l
    body = np.where(rng > 0, np.abs(c - o) / np.where(rng > 0, rng, 1.0), 0.0)
    med20 = pd.Series(v).rolling(20).median().shift(1).to_numpy()
    logvol_rel = np.log(np.maximum(v, 1.0) / np.maximum(med20, 1.0))
    RV = np.column_stack([np.abs(r), rng / atr, body, logvol_rel, evN.astype(float), csb.astype(float), rngN, retN])
    chk = F.n_choch_since_bos.to_numpy(dtype=float); mism = int(np.sum(chk != csb[ks]))
    rep["rv_check_choch_since_bos_mismatch"] = mism
    log(f"regime vector built; n_choch_since_bos mismatches vs the base table: {mism}")
    mu_z = np.nanmean(RV[fit_mask], axis=0); sd_z = np.nanstd(RV[fit_mask], axis=0)
    Z = (RV - mu_z) / sd_z; Z = np.where(np.isfinite(Z), Z, 0.0)
    rep["rv_fit_stats"] = {nm: dict(mean=float(mu_z[j]), std=float(sd_z[j])) for j, nm in enumerate(RV_NAMES)}
    rep["rv_nan_share"] = {nm: float(np.mean(~np.isfinite(RV[:, j]))) for j, nm in enumerate(RV_NAMES)}
    for j, nm in enumerate(RV_NAMES):
        if nm != "choch_since_bos": out[f"rv_{nm}"] = RV[ks, j]                   # choch_since_bos duplicates the base column
    Zfit = Z[fit_mask]
    rep["timings"]["regime_vector"] = round(time.time() - t0, 1)

    def relabel(means_z):
        return np.argsort(means_z[:, 1])                                 # state 0 = lowest mean (high-low)/atr14

    def means_table(means_z):
        return [[round(float(m), 4) for m in (row * sd_z + mu_z)] for row in means_z]

    # ------------------------------------------------------------ GMM (K = 3, 4) fit on the fit window, posterior per bar
    t0 = time.time()
    from sklearn.mixture import GaussianMixture
    from sklearn.cluster import KMeans
    gmm_rep = {}
    for K in STATE_K:
        g = GaussianMixture(K, covariance_type="full", random_state=SEED, n_init=3, max_iter=300, reg_covar=1e-6).fit(Zfit)
        order = relabel(g.means_); post = g.predict_proba(Z)[:, order]
        for j in range(K): out[f"gmm{K}_p{j}"] = post[ks, j]
        out[f"gmm{K}_map"] = np.argmax(post, axis=1)[ks].astype(float)
        gmm_rep[f"K{K}"] = dict(converged=bool(g.converged_), n_iter=int(g.n_iter_), weights=[round(float(x), 4) for x in g.weights_[order]],
                                bic_fit=float(g.bic(Zfit)), state_means=means_table(g.means_[order]), feature_names=RV_NAMES,
                                state_share_tape=[round(float(x), 4) for x in np.bincount(np.argmax(post, axis=1), minlength=K) / n])
        log(f"GMM K={K} fitted ({g.n_iter_} it)")
    rep["gmm"] = gmm_rep; rep["timings"]["gmm"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ Gaussian HMM (hmmlearn, diag) fit on the fit window; FORWARD filter over the tape
    t0 = time.time()
    from hmmlearn.hmm import GaussianHMM
    hmm_rep = {}
    for K in STATE_K:
        hm = GaussianHMM(n_components=K, covariance_type="diag", n_iter=200, tol=1e-3, random_state=SEED).fit(Zfit)
        means = np.asarray(hm.means_, dtype=float); var = np.asarray(hm._covars_, dtype=float)
        post, ll = L.hmm_forward_filter(Z, np.asarray(hm.startprob_, float), np.asarray(hm.transmat_, float), means, var)
        # validation of the filter against hmmlearn on a short prefix: filtered posterior at the last bar = smoothed posterior there
        nv = 600; pv, llv = L.hmm_forward_filter(Z[:nv], np.asarray(hm.startprob_, float), np.asarray(hm.transmat_, float), means, var)
        ref = hm.predict_proba(Z[:nv])[-1]; ref_ll = hm.score(Z[:nv])
        val = dict(max_abs_diff_last_bar_posterior=float(np.max(np.abs(pv[-1] - ref))), loglik_diff=float(abs(llv - ref_ll)))
        order = relabel(means); post = post[:, order]
        mp = np.argmax(post, axis=1)
        for j in range(K): out[f"hmm{K}_p{j}"] = post[ks, j]
        out[f"hmm{K}_map"] = mp[ks].astype(float); out[f"hmm{K}_map_run"] = L.run_length_of(mp)[ks].astype(float)
        tm = np.asarray(hm.transmat_)[np.ix_(order, order)]
        w_, v_ = np.linalg.eig(tm.T); st = np.real(v_[:, np.argmin(np.abs(w_ - 1))]); st = st / st.sum()
        hmm_rep[f"K{K}"] = dict(converged=bool(hm.monitor_.converged), n_iter=int(hm.monitor_.iter), loglik_fit=float(hm.monitor_.history[-1]) if len(hm.monitor_.history) else None,
                                state_means=means_table(means[order]), state_std=[[round(float(x), 4) for x in np.sqrt(var[s]) * sd_z] for s in order],
                                feature_names=RV_NAMES, transmat=[[round(float(x), 4) for x in row] for row in tm],
                                stationary=[round(float(x), 4) for x in st], expected_dwell_bars=[round(float(1 / (1 - tm[s, s])), 1) for s in range(K)],
                                state_share_tape=[round(float(x), 4) for x in np.bincount(mp, minlength=K) / n], filter_validation=val,
                                tape_forward_loglik=float(ll))
        log(f"HMM K={K} fitted ({hm.monitor_.iter} it, converged {hm.monitor_.converged}); filter check {val}")
    rep["hmm"] = hmm_rep; rep["timings"]["hmm"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ statistical jump model (K = 3, 4): lambda by a BIC-like penalty on the fit window, online prefix state
    t0 = time.time()
    jump_rep = {}
    nf, pf = Zfit.shape
    for K in STATE_K:
        km = KMeans(K, random_state=SEED, n_init=10).fit(Zfit)
        grid = []
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
            J = int(np.sum(st[1:] != st[:-1]))
            sse = float(np.sum((Zfit - C[st]) ** 2))
            bic = nf * pf * np.log(sse / (nf * pf)) + (K * pf + J) * np.log(nf * pf)
            grid.append(dict(lam=lam, iters=it + 1, jumps=J, sse=round(sse, 1), bic=round(float(bic), 1), state_share=[round(float(x), 4) for x in np.bincount(st, minlength=K) / nf]))
            if best is None or bic < best[0]: best = (bic, lam, C.copy())
        _, lam_star, C = best
        order = relabel(C); Cs = C[order]
        st_on = L.jump_online(Z, Cs, float(lam_star))
        out[f"jump{K}_state"] = st_on[ks].astype(float); out[f"jump{K}_run"] = L.run_length_of(st_on)[ks].astype(float)
        jump_rep[f"K{K}"] = dict(lambda_grid=grid, lambda_star=lam_star, criterion="n p log(SSE/(n p)) + (K p + jumps) log(n p) on the fit window",
                                 state_means=means_table(Cs), feature_names=RV_NAMES, state_share_tape=[round(float(x), 4) for x in np.bincount(st_on, minlength=K) / n])
        log(f"jump model K={K}: lambda* = {lam_star}")
    rep["jump"] = jump_rep; rep["timings"]["jump"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ novelty: causal prefix MASS (nn and 1st-percentile distance)
    t0 = time.time()
    from joblib import Parallel, delayed
    m1, m2 = P["novelty_m"]
    chunks = np.array_split(np.arange(len(ks)), A.n_jobs * 8)
    res = Parallel(n_jobs=A.n_jobs)(delayed(_novelty_batch)(c, ks[ch], (m1, m2)) for ch in chunks if len(ch))
    nov = np.vstack(res)
    for j, (nm, m) in enumerate((("short", m1), ("long", m2))):
        out[f"nn_dist_prefix_{nm}"] = nov[:, 2 * j]; out[f"p1_dist_prefix_{nm}"] = nov[:, 2 * j + 1]
    rep["novelty"] = dict(m_short=m1, m_long=m2, definition="z-normalised MASS distance profile of close[k-m+1..k] against close[0..k-m-1] (bars strictly before k-m)")
    rep["timings"]["novelty"] = round(time.time() - t0, 1); log(f"novelty done ({rep['timings']['novelty']}s)")

    # ------------------------------------------------------------ window summaries (rocket probe scalars)
    t0 = time.time()
    ag, dd, sl = L.window_summaries(h, l, c, r, atr, sbar, ks, sg, P["win_L"])
    out["win_sign_agree10"] = ag; out["win_dd_extreme_atr"] = dd; out["win_range_slope"] = sl
    rep["window"] = dict(L=P["win_L"], sign_bars=10)
    rep["timings"]["window"] = round(time.time() - t0, 1)

    # ------------------------------------------------------------ write
    X = pd.DataFrame(out)
    X.to_parquet(os.path.join(A.out, "ext_features_all.parquet"), index=False)
    rep["columns"] = [c_ for c_ in X.columns if c_ != "setup_i"]
    rep["coverage"] = {c_: round(float(X[c_].notna().mean()), 4) for c_ in rep["columns"]}
    rep["timings"]["total"] = round(time.time() - T0, 1)
    json.dump(rep, open(os.path.join(A.out, "ext_fit_report.json"), "w"), indent=1, default=str)
    log(f"wrote {X.shape} to {A.out} in {rep['timings']['total']}s")


def _novelty_batch(close, ks, ms):
    import numpy as np, stumpy
    out = np.full((len(ks), 2 * len(ms)), np.nan)
    for q, k in enumerate(ks):
        for j, m in enumerate(ms):
            if k - m < m: continue                                        # the prefix must hold at least one m-bar subsequence
            T = close[:k - m]                                            # bars 0 .. k-m-1: strictly before k-m
            Q = close[k - m + 1:k + 1]
            if np.std(Q) <= 0: continue
            d = stumpy.mass(Q, T)
            d = d[np.isfinite(d)]
            if len(d) == 0: continue
            out[q, 2 * j] = float(np.min(d)); out[q, 2 * j + 1] = float(np.quantile(d, 0.01))
    return out


if __name__ == "__main__":
    main()
