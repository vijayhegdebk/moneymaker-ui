"""Numba kernels and helpers for the extended as-of features (study ext_features). Every kernel reads bars <= t only.

Conventions shared by build_ext.py:
  * "gap-free log return" r_t = log(close_t / close_{t-1}) except at a session's first bar, where r_t = log(close_t / open_t),
    so the overnight gap never enters a return-based statistic (the dataset README's convention for windows).
  * same-session windows: a window of N bars ending at t is cut at the session's first bar s0 = t - session_bar[t].
"""
import math
import numpy as np
from numba import njit

NAN = np.nan


# ---------------------------------------------------------------- returns and per-bar helpers
@njit(cache=True)
def gapfree_logret(close, open_, session_bar):
    n = close.shape[0]; r = np.empty(n)
    for t in range(n):
        if t == 0 or session_bar[t] == 0: r[t] = math.log(close[t] / open_[t])
        else: r[t] = math.log(close[t] / close[t - 1])
    return r


def ffd_weights(d, thres=1e-4):
    """Fixed-width fractional-differentiation weights (AFML 5.5): w_0 = 1, w_k = -w_{k-1} (d - k + 1) / k, cut when |w_k| < thres."""
    w = [1.0]; k = 1
    while True:
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < thres: break
        w.append(wk); k += 1
    return np.array(w)


def ffd_series(y, w):
    """x_t = sum_j w_j y_{t-j} (direct convolution, so x_t depends on y_{t-L+1..t} only and is exact for any tape length); NaN for t < L-1."""
    L = len(w)
    x = np.convolve(y, w, mode="full")[:len(y)]
    x[:L - 1] = NAN
    return x


@njit(cache=True)
def rolling_z(x, win):
    """(x_t - mean(x_{t-win+1..t})) / std(x_{t-win+1..t}) (ddof 1), NaN until win values are available or when any is NaN."""
    n = x.shape[0]; out = np.full(n, NAN)
    for t in range(win - 1, n):
        s = 0.0; s2 = 0.0; ok = True
        for j in range(t - win + 1, t + 1):
            v = x[j]
            if v != v: ok = False; break
            s += v; s2 += v * v
        if not ok: continue
        m = s / win; var = (s2 - win * m * m) / (win - 1)
        if var > 1e-300: out[t] = (x[t] - m) / math.sqrt(var)
    return out


# ---------------------------------------------------------------- BSADF (Phillips, Shi & Yu 2015 backward SADF) at a bar
@njit(cache=True)
def _adf_t_from_sums(xtx, xty, yty, nrows):
    """t-statistic of the y_{t-1} coefficient (index 1) of dy = X b + e from accumulated normal-equation sums."""
    if nrows <= 5: return NAN
    inv = np.linalg.inv(xtx)
    b = inv @ xty
    rss = yty - b @ xty
    if rss <= 0: return NAN
    s2 = rss / (nrows - 4)
    v = s2 * inv[1, 1]
    if v <= 0: return NAN
    return b[1] / math.sqrt(v)


@njit(cache=True)
def bsadf_at(logc, k, W, mmin):
    """Backward SADF at bar k: max over start s of the ADF t-statistic (constant + y_{t-1} + 2 lags of dy) on log close over
    bars s..k, s in [k-W+1, k-mmin+1] (windows of at least mmin bars). Returns (max t, length of the maximising window).
    Sums are accumulated from the shortest window outwards, so every window's regression uses exactly its own bars."""
    i0 = k - W + 1
    if i0 < 0: i0 = 0
    ny = k - i0 + 1
    if ny < mmin: return NAN, NAN
    base = logc[i0]
    xtx = np.zeros((4, 4)); xty = np.zeros(4); yty = 0.0
    best = -1e300; bestlen = NAN
    nrows = 0
    for s in range(ny - 4, -1, -1):
        t = s + 3                                           # the row added when the window starts at s
        y_t = logc[i0 + t] - base; y_1 = logc[i0 + t - 1] - base; y_2 = logc[i0 + t - 2] - base; y_3 = logc[i0 + t - 3] - base
        dy = y_t - y_1; d1 = y_1 - y_2; d2 = y_2 - y_3
        x0 = 1.0; x1 = y_1; x2 = d1; x3 = d2
        xtx[0, 0] += x0 * x0; xtx[0, 1] += x0 * x1; xtx[0, 2] += x0 * x2; xtx[0, 3] += x0 * x3
        xtx[1, 1] += x1 * x1; xtx[1, 2] += x1 * x2; xtx[1, 3] += x1 * x3
        xtx[2, 2] += x2 * x2; xtx[2, 3] += x2 * x3
        xtx[3, 3] += x3 * x3
        xty[0] += x0 * dy; xty[1] += x1 * dy; xty[2] += x2 * dy; xty[3] += x3 * dy
        yty += dy * dy
        nrows += 1
        if ny - s >= mmin:
            for a in range(4):
                for b in range(a):
                    xtx[a, b] = xtx[b, a]
            tstat = _adf_t_from_sums(xtx, xty, yty, nrows)
            if tstat == tstat and tstat > best:
                best = tstat; bestlen = ny - s
    if best < -1e299: return NAN, NAN
    return best, bestlen


# ---------------------------------------------------------------- symmetric CUSUM filter (AFML 2.5.2.1)
@njit(cache=True)
def cusum_filter(r, h):
    """Symmetric CUSUM filter on returns r with a per-bar threshold h_t (NaN threshold: no event possible). Returns the event flag."""
    n = r.shape[0]; ev = np.zeros(n, dtype=np.int64)
    sp = 0.0; sn = 0.0
    for t in range(n):
        x = r[t]
        if x != x: continue
        sp = max(0.0, sp + x); sn = min(0.0, sn + x)
        ht = h[t]
        if ht != ht: continue
        if sp > ht or sn < -ht:
            ev[t] = 1; sp = 0.0; sn = 0.0
    return ev


@njit(cache=True)
def events_window_and_since(ev, win):
    """Events in (t-win, t] and bars since the last event (NaN before the first)."""
    n = ev.shape[0]; cnt = np.zeros(n, dtype=np.int64); since = np.full(n, NAN)
    cs = np.cumsum(ev); last = -1
    for t in range(n):
        lo = t - win
        cnt[t] = cs[t] - (cs[lo] if lo >= 0 else 0)
        if ev[t] > 0: last = t
        if last >= 0: since[t] = t - last
    return cnt, since


# ---------------------------------------------------------------- Chu-Stinchcombe-White (AFML 17.4.1) on the session's levels
@njit(cache=True)
def csw_at(logc, k, s0, b_alpha):
    """S_{n,t} = (y_t - y_n) / (sigma_t sqrt(t - n)) for n in [s0, t-1], sigma_t^2 = mean of the session's squared level changes
    up to t; critical value c = sqrt(b_alpha + log(t - n)). Returns (max |S|, max (|S| - c), sign of y_t - y_n at that argmax)."""
    t = k
    if t - s0 < 2: return NAN, NAN, NAN
    ss = 0.0
    for j in range(s0 + 1, t + 1):
        d = logc[j] - logc[j - 1]; ss += d * d
    var = ss / (t - s0)
    if var <= 0: return NAN, NAN, NAN
    sig = math.sqrt(var)
    best_abs = -1.0; best_ex = -1e300; sgn = 0.0
    for n_ in range(s0, t):
        S = (logc[t] - logc[n_]) / (sig * math.sqrt(t - n_))
        a = abs(S); c = math.sqrt(b_alpha + math.log(t - n_)); ex = a - c
        if a > best_abs: best_abs = a
        if ex > best_ex:
            best_ex = ex; sgn = 1.0 if S > 0 else (-1.0 if S < 0 else 0.0)
    return best_abs, best_ex, sgn


# ---------------------------------------------------------------- BOCPD (Adams & MacKay 2007), normal-inverse-gamma / Student-t predictive
@njit(cache=True)
def bocpd(x, hazard, rmax, mu0, kappa0, alpha0, beta0):
    """Run-length posterior over 0..rmax (mass beyond rmax folded into the rmax bin, whose sufficient statistics keep updating).
    Returns per bar: MAP run length, P(run length < 10), bars since the last MAP reset (a reset = the MAP run length fell)."""
    n = x.shape[0]; R = np.zeros(rmax + 1); R[0] = 1.0; Rn = np.zeros(rmax + 1)
    mu = np.full(rmax + 1, mu0); be = np.full(rmax + 1, beta0)
    mun = np.empty(rmax + 1); ben = np.empty(rmax + 1)
    kap = np.empty(rmax + 1); al = np.empty(rmax + 1); c = np.empty(rmax + 1); nu = np.empty(rmax + 1)
    for r in range(rmax + 1):
        kap[r] = kappa0 + r; al[r] = alpha0 + 0.5 * r; nu[r] = 2.0 * al[r]
        c[r] = math.lgamma(0.5 * (nu[r] + 1.0)) - math.lgamma(0.5 * nu[r]) - 0.5 * math.log(nu[r] * math.pi)
    pred = np.empty(rmax + 1)
    map_rl = np.zeros(n, dtype=np.int64); p_lt10 = np.full(n, NAN); since = np.full(n, NAN)
    last_reset = -1; prev_map = 0
    for t in range(n):
        xt = x[t]
        if xt != xt:                                        # no observation: carry the state, repeat the features
            map_rl[t] = prev_map; p_lt10[t] = p_lt10[t - 1] if t > 0 else NAN
            if last_reset >= 0: since[t] = t - last_reset
            continue
        for r in range(rmax + 1):
            sc2 = be[r] * (kap[r] + 1.0) / (al[r] * kap[r])
            z = (xt - mu[r]); z = z * z / (nu[r] * sc2)
            pred[r] = math.exp(c[r] - 0.5 * math.log(sc2) - 0.5 * (nu[r] + 1.0) * math.log1p(z))
        cp = 0.0
        for r in range(rmax + 1): Rn[r] = 0.0
        for r in range(rmax + 1):
            pr = R[r] * pred[r]; cp += pr * hazard
            if r < rmax: Rn[r + 1] += pr * (1.0 - hazard)
            else: Rn[rmax] += pr * (1.0 - hazard)
        Rn[0] = cp
        tot = 0.0
        for r in range(rmax + 1): tot += Rn[r]
        if tot <= 0:
            for r in range(rmax + 1): Rn[r] = 0.0
            Rn[0] = 1.0; tot = 1.0
        for r in range(rmax + 1): Rn[r] /= tot
        # sufficient statistics: bin r+1 <- bin r updated with x; bin 0 <- prior; bin rmax <- mass-weighted average of the two
        mun[0] = mu0; ben[0] = beta0
        for r in range(rmax):
            mun[r + 1] = (kap[r] * mu[r] + xt) / (kap[r] + 1.0)
            ben[r + 1] = be[r] + kap[r] * (xt - mu[r]) * (xt - mu[r]) / (2.0 * (kap[r] + 1.0))
        mu_self = (kap[rmax] * mu[rmax] + xt) / (kap[rmax] + 1.0)
        be_self = be[rmax] + kap[rmax] * (xt - mu[rmax]) * (xt - mu[rmax]) / (2.0 * (kap[rmax] + 1.0))
        w1 = R[rmax - 1] * pred[rmax - 1]; w2 = R[rmax] * pred[rmax]
        if w1 + w2 > 0:
            mun[rmax] = (w1 * mun[rmax] + w2 * mu_self) / (w1 + w2); ben[rmax] = (w1 * ben[rmax] + w2 * be_self) / (w1 + w2)
        for r in range(rmax + 1):
            R[r] = Rn[r]; mu[r] = mun[r]; be[r] = ben[r]
        m = 0; bestp = -1.0; p10 = 0.0
        for r in range(rmax + 1):
            if R[r] > bestp: bestp = R[r]; m = r
            if r < 10: p10 += R[r]
        map_rl[t] = m; p_lt10[t] = p10
        if t > 0 and m < prev_map: last_reset = t
        if last_reset >= 0: since[t] = t - last_reset
        prev_map = m
    return map_rl, p_lt10, since


# ---------------------------------------------------------------- the per-bar regime vector pieces
@njit(cache=True)
def event_counts(n, ev_bar, ev_is_bos):
    """Per bar: events at the bar (count) and CHoCHs since the last BOS after processing the bar's events in seq order."""
    ev_at = np.zeros(n, dtype=np.int64); csb = np.zeros(n, dtype=np.int64)
    cnt = 0; j = 0; m = ev_bar.shape[0]
    for t in range(n):
        while j < m and ev_bar[j] == t:
            ev_at[t] += 1
            if ev_is_bos[j]: cnt = 0
            else: cnt += 1
            j += 1
        csb[t] = cnt
    return ev_at, csb


@njit(cache=True)
def session_windows(high, low, close, open_, atr, session_bar, ev_at, N):
    """Same-session windows of N bars ending at t: events in the window, (max high - min low) / atr_t, (close_t - close_{t-N} or
    the session open when t-N is before the session) / atr_t."""
    n = close.shape[0]
    evN = np.zeros(n, dtype=np.int64); rngN = np.full(n, NAN); retN = np.full(n, NAN)
    for t in range(n):
        s0 = t - session_bar[t]
        lo = t - N + 1
        if lo < s0: lo = s0
        hi_ = -1e300; lo_ = 1e300; e = 0
        for j in range(lo, t + 1):
            if high[j] > hi_: hi_ = high[j]
            if low[j] < lo_: lo_ = low[j]
            e += ev_at[j]
        evN[t] = e
        a = atr[t]
        if a > 0:
            rngN[t] = (hi_ - lo_) / a
            ref = close[t - N] if t - N >= s0 else open_[s0]
            retN[t] = (close[t] - ref) / a
    return evN, rngN, retN


@njit(cache=True)
def window_summaries(high, low, close, r, atr, session_bar, ks, sg, L):
    """At SETUP bars ks with direction sg: sign-agreement count of the last 10 bar returns with sg (tape bars, gap-free returns),
    drawdown from the same-session L-bar window extreme against the direction in ATR, OLS slope of (high-low)/atr_k over the window."""
    m = ks.shape[0]; agree = np.full(m, NAN); dd = np.full(m, NAN); slope = np.full(m, NAN)
    for q in range(m):
        k = ks[q]; s = sg[q]
        c = 0
        for j in range(max(0, k - 9), k + 1):
            if (s > 0 and r[j] > 0) or (s < 0 and r[j] < 0): c += 1
        agree[q] = c
        s0 = k - session_bar[k]; lo = k - L + 1
        if lo < s0: lo = s0
        a = atr[k]
        if a <= 0: continue
        hi_ = -1e300; lo_ = 1e300; n = 0; sx = 0.0; sy = 0.0; sxx = 0.0; sxy = 0.0
        for j in range(lo, k + 1):
            if high[j] > hi_: hi_ = high[j]
            if low[j] < lo_: lo_ = low[j]
            x = float(j - lo); y = (high[j] - low[j]) / a
            n += 1; sx += x; sy += y; sxx += x * x; sxy += x * y
        dd[q] = (hi_ - close[k]) / a if s > 0 else (close[k] - lo_) / a
        if n >= 3:
            den = n * sxx - sx * sx
            if den > 0: slope[q] = (n * sxy - sx * sy) / den
    return agree, dd, slope


# ---------------------------------------------------------------- state models: HMM forward filter, jump model DP
@njit(cache=True)
def hmm_forward_filter(Z, startprob, transmat, means, variances):
    """Scaled forward filter of a diagonal-Gaussian HMM: P(s_t | x_{<=t}) for every bar (never the smoothed posterior)."""
    n, p = Z.shape; K = means.shape[0]
    post = np.empty((n, K)); alpha = np.empty(K); tmp = np.empty(K)
    logdet = np.empty(K)
    for s in range(K):
        v = 0.0
        for j in range(p): v += math.log(2.0 * math.pi * variances[s, j])
        logdet[s] = -0.5 * v
    loglik = 0.0
    for t in range(n):
        # emission log densities, shifted by their max for stability
        mx = -1e300
        for s in range(K):
            e = logdet[s]
            for j in range(p):
                d = Z[t, j] - means[s, j]; e -= 0.5 * d * d / variances[s, j]
            tmp[s] = e
            if e > mx: mx = e
        tot = 0.0
        for s in range(K):
            if t == 0: pr = startprob[s]
            else:
                pr = 0.0
                for u in range(K): pr += post[t - 1, u] * transmat[u, s]
            alpha[s] = pr * math.exp(tmp[s] - mx); tot += alpha[s]
        if tot <= 0:
            for s in range(K): alpha[s] = 1.0 / K
            tot = 1.0
        for s in range(K): post[t, s] = alpha[s] / tot
        loglik += math.log(tot) + mx
    return post, loglik


@njit(cache=True)
def jump_viterbi(Z, C, lam):
    """Offline DP for the statistical jump model on a fitted window: argmin over paths of sum ||x_t - c_{s_t}||^2 + lam 1[s_t != s_{t-1}]."""
    n, p = Z.shape; K = C.shape[0]
    V = np.empty((n, K)); B = np.zeros((n, K), dtype=np.int64)
    for s in range(K):
        d = 0.0
        for j in range(p): dd = Z[0, j] - C[s, j]; d += dd * dd
        V[0, s] = d
    for t in range(1, n):
        mn = 1e300; arg = 0
        for u in range(K):
            if V[t - 1, u] < mn: mn = V[t - 1, u]; arg = u
        for s in range(K):
            stay = V[t - 1, s]; sw = mn + lam
            if stay <= sw: prev = s; base = stay
            else: prev = arg; base = sw
            d = 0.0
            for j in range(p): dd = Z[t, j] - C[s, j]; d += dd * dd
            V[t, s] = base + d; B[t, s] = prev
    states = np.empty(n, dtype=np.int64)
    mn = 1e300; arg = 0
    for s in range(K):
        if V[n - 1, s] < mn: mn = V[n - 1, s]; arg = s
    states[n - 1] = arg
    for t in range(n - 1, 0, -1): states[t - 1] = B[t, states[t]]
    return states, mn


@njit(cache=True)
def jump_online(Z, C, lam):
    """Online prefix state: s_t = argmin_s V_t(s) with V_t(s) = min_u (V_{t-1}(u) + lam 1[s != u]) + ||x_t - c_s||^2 (bars <= t only)."""
    n, p = Z.shape; K = C.shape[0]
    Vp = np.zeros(K); Vn = np.empty(K); states = np.empty(n, dtype=np.int64)
    for t in range(n):
        mn = 1e300
        for u in range(K):
            if Vp[u] < mn: mn = Vp[u]
        for s in range(K):
            if t == 0: base = 0.0
            elif Vp[s] <= mn + lam: base = Vp[s]
            else: base = mn + lam
            d = 0.0
            for j in range(p): dd = Z[t, j] - C[s, j]; d += dd * dd
            Vn[s] = base + d
        mn2 = 1e300; arg = 0
        for s in range(K):
            if Vn[s] < mn2: mn2 = Vn[s]; arg = s
        states[t] = arg
        for s in range(K): Vp[s] = Vn[s] - mn2
    return states


@njit(cache=True)
def run_length_of(states):
    """Consecutive bars (ending at t) with the same state as at t (>= 1)."""
    n = states.shape[0]; out = np.ones(n, dtype=np.int64)
    for t in range(1, n):
        out[t] = out[t - 1] + 1 if states[t] == states[t - 1] else 1
    return out
