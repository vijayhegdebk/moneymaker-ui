"""rocket_ceiling library: the pre-SETUP window tensor, the MiniRocket-style kernel bank, the fold-fitted PPV transform (numba).

Everything here is deterministic given the seeds logged by rocket_ceiling.py. No label enters any function of this module.

Window (per SETUP row, L bars ending at the SETUP bar k inclusive, float32, shape (n, C, L)); sg = +1 up / -1 down; a = atr14[k]:
  ch0  sg x log return per bar, in bps: 1e4 x sg x (log close[t] - log close[t-1]); t-1 is the previous tape bar (the overnight gap
       enters here when the window crosses the session start; ch6 flags those bars); 0 for bar 0 of the tape
  ch1  (high[t] - low[t]) / a
  ch2  sg x (close[t] - open[t]) / a
  ch3  log(volume[t] / vol_med20_prior[k]) with NaN -> 0 (NaN when vol_med20_prior[k] is NaN, i.e. fewer than 5 prior bars in the
       SETUP's session, or volume[t] <= 0); vol_med20_prior[k] is the as-of median of the SETUP bar's own session
  ch4  the NA flag of ch3 (1 where ch3 was NaN)
  ch5  sg x (close[t] - choch_lvl[k]) / a   (choch_lvl = the level the SETUP's CHoCH broke; a features.parquet as-of column)
  ch6  same-session indicator: 1 when session_idx[t] == session_idx[k]
  bars before the tape start (t < 0) are zero in every channel (ch6 = 0).
Kernel bank (K kernels, seeded): length 9, weights -1 at six positions and +2 at three random positions (sum 0, MiniRocket's
  centred weights); dilation d = floor(2 ** (u log2(L / 4))), u ~ U[0, 1) (log-uniform on 1 .. L/4); channels: one channel (p = 1/2)
  or a random pair (the conv is the sum over the selected channels with the same weights, MiniRocket's multivariate form); zero
  padding (9 - 1) d / 2 on both sides so the output has L positions for every dilation; a quantile level q ~ U(0.05, 0.95).
Bias (per training fold): for kernel j, the q_j-quantile of the convolution outputs of `n_bias` training windows sampled with the
  fold's seed (MiniRocket draws its biases from the quantiles of training-example convolution outputs). Feature = PPV = the share
  of the L output positions with conv > bias.
"""
import numpy as np
from numba import njit, prange

KLEN = 9


def build_windows(bars, F, L):
    """Window tensor (n, 7, L) float32 for the SETUP rows F (needs setup_i, dir, atr14, vol_med20_prior, choch_lvl, session_idx)."""
    close = bars.close.to_numpy(dtype=np.float64); opn = bars.open.to_numpy(dtype=np.float64)
    high = bars.high.to_numpy(dtype=np.float64); low = bars.low.to_numpy(dtype=np.float64)
    vol = bars.volume.to_numpy(dtype=np.float64); ses = bars.session_idx.to_numpy()
    assert (bars.i.to_numpy() == np.arange(len(bars))).all(), "bars must be indexed 0..n-1 by i"
    logc = np.log(close)
    lr = np.zeros_like(logc); lr[1:] = logc[1:] - logc[:-1]
    k = F.setup_i.to_numpy().astype(int); n = len(k)
    sg = np.where(F.dir.astype(str).to_numpy() == "up", 1.0, -1.0)
    a = F.atr14.to_numpy(dtype=np.float64); vm = F.vol_med20_prior.to_numpy(dtype=np.float64); lvl = F.choch_lvl.to_numpy(dtype=np.float64)
    ks = F.session_idx.to_numpy().astype(int)
    assert np.allclose(a, bars.atr14.to_numpy()[k]), "features.atr14 must equal bars.atr14 at k"
    assert (ks == ses[k]).all(), "features.session_idx must equal bars.session_idx at k"
    idx = k[:, None] + np.arange(-L + 1, 1)[None, :]
    valid = idx >= 0; ii = np.where(valid, idx, 0)
    W = np.zeros((n, 7, L), dtype=np.float32)
    W[:, 0] = 1e4 * sg[:, None] * lr[ii]
    W[:, 1] = (high[ii] - low[ii]) / a[:, None]
    W[:, 2] = sg[:, None] * (close[ii] - opn[ii]) / a[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        v = np.log(vol[ii] / vm[:, None])
    na = ~np.isfinite(v)
    W[:, 3] = np.where(na, 0.0, v); W[:, 4] = na.astype(np.float32)
    W[:, 5] = sg[:, None] * (close[ii] - lvl[:, None]) / a[:, None]
    W[:, 6] = (ses[ii] == ks[:, None]).astype(np.float32)
    W[~valid[:, None, :].repeat(7, axis=1)] = 0.0
    assert np.isfinite(W).all()
    return W


def make_kernels(K, L, C, seed):
    """The kernel bank: (pos2 (K, 3) int, dil (K,) int, ch (K, 2) int with ch[:,1] = -1 for single-channel kernels, qlev (K,) float)."""
    rng = np.random.default_rng(seed)
    pos2 = np.array([rng.choice(KLEN, 3, replace=False) for _ in range(K)], dtype=np.int64)
    max_d = L // 4
    dil = np.floor(2.0 ** (rng.random(K) * np.log2(max_d))).astype(np.int64)
    dil = np.clip(dil, 1, max_d)
    ch = np.full((K, 2), -1, dtype=np.int64)
    pair = rng.random(K) < 0.5
    for j in range(K):
        if pair[j]: ch[j] = rng.choice(C, 2, replace=False)
        else: ch[j, 0] = rng.integers(C)
    qlev = rng.uniform(0.05, 0.95, K)
    weights = np.full((K, KLEN), -1.0, dtype=np.float32)
    for j in range(K): weights[j, pos2[j]] = 2.0
    return dict(pos2=pos2, dil=dil, ch=ch, qlev=qlev, weights=weights, K=K, L=L, C=C, seed=seed)


@njit(cache=False)
def _conv_one(W, i, weights, d, c0, c1, out):
    """Padded dilated convolution of window i with kernel (weights, d) over channels c0 (+ c1 when >= 0); writes L values to out."""
    L = W.shape[2]
    pad = (KLEN - 1) * d // 2
    for t in range(L):
        s = 0.0
        for m in range(KLEN):
            u = t - pad + m * d
            if 0 <= u < L:
                s += weights[m] * W[i, c0, u]
                if c1 >= 0: s += weights[m] * W[i, c1, u]
        out[t] = s


@njit(parallel=True, cache=False)
def conv_samples(W, rows, weights, dil, ch):
    """Convolution outputs (K, len(rows), L) for the sampled windows `rows` (used for the bias quantiles)."""
    K = weights.shape[0]; n = rows.shape[0]; L = W.shape[2]
    out = np.empty((K, n, L), dtype=np.float32)
    for j in prange(K):
        buf = np.empty(L, dtype=np.float64)
        for r in range(n):
            _conv_one(W, rows[r], weights[j], dil[j], ch[j, 0], ch[j, 1], buf)
            for t in range(L): out[j, r, t] = buf[t]
    return out


@njit(parallel=True, cache=False)
def ppv_transform(W, rows, weights, dil, ch, bias):
    """PPV features (len(rows), K) float32: the share of output positions with conv > bias[j]."""
    K = weights.shape[0]; n = rows.shape[0]; L = W.shape[2]
    out = np.empty((n, K), dtype=np.float32)
    for j in prange(K):
        buf = np.empty(L, dtype=np.float64)
        for r in range(n):
            _conv_one(W, rows[r], weights[j], dil[j], ch[j, 0], ch[j, 1], buf)
            cnt = 0
            for t in range(L):
                if buf[t] > bias[j]: cnt += 1
            out[r, j] = cnt / L
    return out


def fit_biases(W, train_rows, kern, seed, n_bias=32):
    """Per kernel: the q_j-quantile of the convolution outputs over n_bias training windows sampled with `seed`."""
    rng = np.random.default_rng(seed)
    samp = rng.choice(np.asarray(train_rows), size=min(n_bias, len(train_rows)), replace=False).astype(np.int64)
    cv = conv_samples(W, samp, kern["weights"], kern["dil"], kern["ch"])          # (K, n_bias, L)
    flat = cv.reshape(cv.shape[0], -1).astype(np.float64)
    bias = np.array([np.quantile(flat[j], kern["qlev"][j]) for j in range(cv.shape[0])])
    return bias, samp


def transform(W, rows, kern, bias):
    return ppv_transform(W, np.asarray(rows, dtype=np.int64), kern["weights"], kern["dil"], kern["ch"], np.asarray(bias, dtype=np.float64))
