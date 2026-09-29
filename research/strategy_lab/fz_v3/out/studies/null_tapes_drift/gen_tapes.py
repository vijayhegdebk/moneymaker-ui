"""Synthetic null tapes for the FZ v3 program (DESIGN_PANEL decision-making-3 part (c), both judges' fixes).

Three generators, every one fitted on the IS bars only (fz_v3/out/data/<tf>/bars.parquet rows with split == "IS"; the OOS bars
never enter a generator), writing CSV tapes in the near-month file format (datetime, open, high, low, close, volume, oi,
contract, expiry, front_month) that build.py reads in full through engine.load:

  session   whole IS sessions resampled with replacement; the level is chained through each drawn session's own open-to-close
            path (prices re-based to the drawn session's open) and a gap drawn from the IS gap distribution (log(open /
            previous close)) at every session start. Keeps everything inside a session (swing structure, CHoCH memory within
            the day, the time-of-day profile); breaks only the memory across sessions.
  segment   (Judge 1) 30-bar blocks stitched across sessions: block j of a synthetic session is bars [30j, 30j+30) of a random
            IS session, re-based to that block's previous close and chained; the gap as above. Keeps the short autocorrelation
            (up to 30 bars) and the clock profile; breaks the swing / CHoCH memory beyond 30 bars.
  gmm       GMM-Markov: GaussianMixture (4-6 components, full covariance, chosen by BIC on the IS bars) on the per-bar vector
            (log close-to-close return, log volume ratio to the session-clock median, range / atr14, close position in the bar),
            a first-order Markov chain on the component labels (transition counts within sessions, the initial distribution
            from the sessions' first bars), sampled per session with the time-of-day volume profile; OHLC rebuilt consistently
            (open = previous close, range >= |close - open|, high >= max(open, close), low <= min(open, close)); ATR14 tracked
            recursively on the generated bars for the range scale. Keeps volatility clustering (through the chain) and the
            volume shape; no swing / CHoCH memory and no time-of-day return structure: the null.

Sessions are full-length only (375 one-minute / 75 five-minute bars on the real clock; the real IS tape's short sessions are
excluded from the pools and reported), the calendar and the contract / expiry per session are the real IS session dates
(so build.py's IS / OOS split reads every tape row as IS and the L1 expiry cap works as on the real tape), prices are rounded
to the 0.05 tick, front_month = 1 everywhere, oi = 0. Seeds: numpy default_rng(sha1(tf | gen | k)); every tape reproduces.

    python gen_tapes.py --tf 5minute --gen session --k 0 --out tapes/5minute/session_0/tape.csv
    (or import: fit = fit_generators(tf); write_tape(fit, gen, k, path))
"""
import os, sys, json, hashlib, argparse, time
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from sklearn.mixture import GaussianMixture

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(OUT, "data")
FULL = {"minute": 375, "5minute": 75}
TF_MIN = {"minute": 1, "5minute": 5}
BLOCK = 30                               # segment bootstrap block length in bars (Judge 1)
GMM_COMPONENTS = (4, 5, 6)
ATR_N = 14
TICK = 0.05
GENS = ("session", "segment", "gmm")


def _seed(*parts):
    return int(hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:8], 16)


def _round_tick(x):
    return np.round(np.asarray(x, dtype=float) / TICK) * TICK


def clock(tf):
    n = FULL[tf]; m = TF_MIN[tf]
    return [f"{9 + (15 + k * m) // 60:02d}:{(15 + k * m) % 60:02d}:00" for k in range(n)]


# ---------------------------------------------------------------- fit (IS bars only)
def fit_generators(tf, verbose=True):
    """Everything the three generators need, from the IS bars of the real tape. Returns a dict (the 'fit')."""
    t0 = time.time()
    B = pd.read_parquet(os.path.join(DATA, tf, "bars.parquet"),
                        columns=["datetime", "session_idx", "session_bar", "open", "high", "low", "close", "volume", "atr14", "split"])
    S = pd.read_parquet(os.path.join(DATA, tf, "sessions.parquet"))
    B = B[B.split.astype(str) == "IS"].reset_index(drop=True)
    S_is = S[S.split.astype(str) == "IS"].reset_index(drop=True)
    n_full = FULL[tf]
    nb = B.groupby("session_idx").size()
    full_sessions = nb[nb == n_full].index.to_numpy()
    short_sessions = nb[nb != n_full]
    Bf = B[B.session_idx.isin(full_sessions)].sort_values(["session_idx", "session_bar"]).reset_index(drop=True)
    P = len(full_sessions)
    O = Bf.open.to_numpy().reshape(P, n_full); H = Bf.high.to_numpy().reshape(P, n_full)
    L = Bf.low.to_numpy().reshape(P, n_full); C = Bf.close.to_numpy().reshape(P, n_full); V = Bf.volume.to_numpy().reshape(P, n_full)
    # gaps: log(session open / previous session close), over consecutive IS sessions (all IS sessions, short ones included)
    first = B.groupby("session_idx").first(); last = B.groupby("session_idx").last()
    sidx = first.index.to_numpy()
    gaps = np.log(first.open.to_numpy()[1:] / last.close.to_numpy()[:-1])
    gaps = gaps[np.diff(sidx) == 1]
    # session-clock volume profile (median volume per session_bar over the full IS sessions)
    vol_profile = np.nanmedian(np.where(V > 0, V, np.nan), axis=0); vol_profile = np.where(np.isfinite(vol_profile), vol_profile, 1.0)
    # calendar: the IS session dates with their contract / expiry (the tape carries the real expiry structure)
    cal = S_is[["session_idx", "date", "contract", "expiry"]].copy()
    fit = dict(tf=tf, n_full=n_full, n_pool=P, short_sessions={int(k): int(v) for k, v in short_sessions.items()},
               O=O, H=H, L=L, C=C, V=V, gaps=gaps, vol_profile=vol_profile, calendar=cal,
               level0=float(first.open.iloc[0]), atr0=float(np.median(Bf.atr14.to_numpy())), clock=clock(tf),
               n_is_bars=int(len(B)), n_is_sessions=int(len(S_is)))
    # GMM-Markov: per-bar vector on every IS bar of the full sessions
    Cprev = np.concatenate([O[:, :1], C[:, :-1]], axis=1)
    r = np.log(C / Cprev)
    lvr = np.log(np.maximum(V, 1.0) / vol_profile[None, :])
    atr = Bf.atr14.to_numpy().reshape(P, n_full)
    rra = (H - L) / atr
    with np.errstate(invalid="ignore", divide="ignore"):
        cp = np.where(H > L, (C - L) / (H - L), 0.5)
    X = np.stack([r.ravel(), lvr.ravel(), rra.ravel(), cp.ravel()], axis=1)
    ok = np.isfinite(X).all(axis=1)
    Xf = X[ok]
    # z-score every dimension before the fit (the return dimension's variance ~6e-7 is below sklearn's reg_covar otherwise);
    # the sampler un-standardises and clips each dimension to the IS observed range
    z_mu, z_sd = Xf.mean(axis=0), Xf.std(axis=0)
    Zf = (Xf - z_mu) / z_sd
    best, bics = None, {}
    for kc in GMM_COMPONENTS:
        g = GaussianMixture(kc, covariance_type="full", random_state=_seed(tf, "gmm", kc) % (2 ** 31), max_iter=500, n_init=1, tol=1e-4, reg_covar=1e-6)
        g.fit(Zf); bics[kc] = float(g.bic(Zf))
        if best is None or bics[kc] < bics[best.n_components]: best = g
    lab = np.full(len(X), -1); lab[ok] = best.predict(Zf)
    fit.update(z_mu=z_mu, z_sd=z_sd, z_lo=Xf.min(axis=0), z_hi=Xf.max(axis=0),
               real_vector_moments=dict(std=Xf.std(axis=0).tolist(), kurtosis_excess=[float(pd.Series(Xf[:, j]).kurt()) for j in range(4)]))
    lab = lab.reshape(P, n_full)
    K = best.n_components
    trans = np.ones((K, K)) * 1e-3                                       # transition counts within sessions (tiny prior so every row sums > 0)
    a, b = lab[:, :-1].ravel(), lab[:, 1:].ravel(); m = (a >= 0) & (b >= 0)
    np.add.at(trans, (a[m], b[m]), 1.0)
    trans /= trans.sum(axis=1, keepdims=True)
    init = np.bincount(lab[:, 0][lab[:, 0] >= 0], minlength=K).astype(float) + 1e-3; init /= init.sum()
    fit.update(gmm=best, gmm_bic=bics, gmm_k=K, trans=trans, init=init,
               gmm_fit_rows=int(ok.sum()), gmm_means=best.means_.tolist(), gmm_weights=best.weights_.tolist())
    if verbose:
        print(f"[fit {tf}] IS sessions {fit['n_is_sessions']} (full {P}, short {len(short_sessions)}), IS bars {fit['n_is_bars']}, gaps {len(gaps)}, "
              f"GMM BIC {bics} -> K={K}, {time.time() - t0:.1f}s", flush=True)
    return fit


def fit_summary(fit):
    return dict(tf=fit["tf"], n_full_bars=fit["n_full"], pool_sessions=fit["n_pool"], is_sessions=fit["n_is_sessions"], is_bars=fit["n_is_bars"],
                short_sessions_excluded=fit["short_sessions"], gaps_n=int(len(fit["gaps"])), gap_log_std=float(np.std(fit["gaps"])),
                level0=fit["level0"], atr0=fit["atr0"], gmm_bic=fit["gmm_bic"], gmm_k=fit["gmm_k"], gmm_fit_rows=fit["gmm_fit_rows"],
                gmm_weights=[round(w, 4) for w in fit["gmm_weights"]], gmm_means=[[round(x, 5) for x in m] for m in fit["gmm_means"]],
                markov_transition=[[round(x, 4) for x in row] for row in fit["trans"].tolist()], markov_init=[round(x, 4) for x in fit["init"].tolist()],
                block_bars=BLOCK)


# ---------------------------------------------------------------- the three samplers (one session each)
def _session_bootstrap(fit, rng, level):
    j = rng.integers(fit["n_pool"])
    ref = fit["O"][j, 0]
    o, h, l, c = (fit[k][j] / ref * level for k in "OHLC")
    return o, h, l, c, fit["V"][j].copy()


def _segment_bootstrap(fit, rng, level):
    n = fit["n_full"]; o = np.empty(n); h = np.empty(n); l = np.empty(n); c = np.empty(n); v = np.empty(n)
    anchor = level
    for j0 in range(0, n, BLOCK):
        j1 = min(n, j0 + BLOCK); j = rng.integers(fit["n_pool"])
        ref = fit["O"][j, 0] if j0 == 0 else fit["C"][j, j0 - 1]
        for arr, k in ((o, "O"), (h, "H"), (l, "L"), (c, "C")): arr[j0:j1] = fit[k][j, j0:j1] / ref * anchor
        v[j0:j1] = fit["V"][j, j0:j1]
        anchor = c[j1 - 1]
    return o, h, l, c, v


def _gmm_markov(fit, rng, level, atr):
    n = fit["n_full"]; K = fit["gmm_k"]; g = fit["gmm"]
    states = np.empty(n, dtype=int); states[0] = rng.choice(K, p=fit["init"])
    for k in range(1, n): states[k] = rng.choice(K, p=fit["trans"][states[k - 1]])
    Z = np.empty((n, 4))
    for s in range(K):
        m = states == s
        if m.any(): Z[m] = rng.multivariate_normal(g.means_[s], g.covariances_[s], size=int(m.sum()))
    Z = np.clip(Z * fit["z_sd"] + fit["z_mu"], fit["z_lo"], fit["z_hi"])           # un-standardise; clip to the IS observed range per dimension
    o = np.empty(n); h = np.empty(n); l = np.empty(n); c = np.empty(n); v = np.empty(n)
    prev = level
    for k in range(n):
        r, lvr, rra, cp = Z[k]
        o[k] = prev; c[k] = prev * np.exp(r)
        rng_ = max(max(rra, 0.0) * atr, abs(c[k] - o[k]), TICK)
        cp = min(max(cp, 0.0), 1.0)
        lo = c[k] - cp * rng_; hi = lo + rng_
        l[k] = min(lo, o[k], c[k]); h[k] = max(hi, o[k], c[k])
        v[k] = max(1.0, round(np.exp(lvr) * fit["vol_profile"][k]))
        atr = atr + ((h[k] - l[k]) - atr) / ATR_N                       # Wilder update on the generated bar (TR = high - low since open = previous close)
        prev = c[k]
    return o, h, l, c, v, atr, states


def sample_tape(fit, gen, k, calendar=None):
    """One tape as a DataFrame in the near-month format. calendar: rows (date, contract, expiry) = the sessions to write
    (default: every IS session date). Session s opens at level_{s-1} x exp(gap) with gap drawn from the IS gaps (0 for s = 0)."""
    rng = np.random.default_rng(_seed(fit["tf"], gen, k))
    cal = fit["calendar"] if calendar is None else calendar
    n = fit["n_full"]; level = fit["level0"]; atr = fit["atr0"]
    frames = []; state_log = []
    for s, row in enumerate(cal.itertuples(index=False)):
        gap = 0.0 if s == 0 else float(rng.choice(fit["gaps"]))
        level_open = level * np.exp(gap)
        if gen == "session": o, h, l, c, v = _session_bootstrap(fit, rng, level_open)
        elif gen == "segment": o, h, l, c, v = _segment_bootstrap(fit, rng, level_open)
        elif gen == "gmm":
            o, h, l, c, v, atr, st = _gmm_markov(fit, rng, level_open, atr); state_log.append(np.bincount(st, minlength=fit["gmm_k"]))
        else: raise ValueError(gen)
        o, h, l, c = (_round_tick(x) for x in (o, h, l, c))
        h = np.maximum(h, np.maximum(o, c)); l = np.minimum(l, np.minimum(o, c))
        frames.append(pd.DataFrame(dict(datetime=[f"{row.date} {hm}" for hm in fit["clock"]], open=o, high=h, low=l, close=c,
                                        volume=v.astype(np.int64), oi=0, contract=row.contract, expiry=row.expiry, front_month=1)))
        level = float(c[-1])
    df = pd.concat(frames, ignore_index=True)
    return df, dict(state_counts=np.sum(state_log, axis=0).tolist() if state_log else None)


def write_tape(fit, gen, k, path, calendar=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df, info = sample_tape(fit, gen, k, calendar)
    for col in ("open", "high", "low", "close"): df[col] = df[col].map(lambda x: f"{x:.2f}")
    df.to_csv(path, index=False)
    meta = dict(tf=fit["tf"], gen=gen, k=k, seed=_seed(fit["tf"], gen, k), rows=int(len(df)), sessions=int(len(df) // fit["n_full"]),
                first=df.datetime.iloc[0], last=df.datetime.iloc[-1], fitted_on="IS bars only (split == IS of fz_v3/out/data/<tf>/bars.parquet)", **info)
    json.dump(meta, open(os.path.join(os.path.dirname(path), "tape_meta.json"), "w"), indent=1)
    return meta


def one_year_calendar(fit, sessions=247):
    """The last `sessions` IS session dates (the 1-minute tapes are one trading year long)."""
    return fit["calendar"].iloc[-sessions:].reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", required=True, choices=("minute", "5minute")); ap.add_argument("--gen", required=True, choices=GENS)
    ap.add_argument("--k", type=int, required=True); ap.add_argument("--out", required=True); ap.add_argument("--one-year", action="store_true")
    a = ap.parse_args()
    fit = fit_generators(a.tf)
    print(write_tape(fit, a.gen, a.k, a.out, one_year_calendar(fit) if a.one_year else None))
