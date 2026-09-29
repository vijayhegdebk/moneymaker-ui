"""exit_policy study: shared definitions (DESIGN_PANEL decision-making-2-exit-policy-fqi-exomdp, both judges' fixes; BRIEF
addendum 6: the managed replay is lab.manage / lab.price_trade, never a second implementation of the same exits).

Entries are frozen: every IS unit of harness.load(tf) (label L1), entry at the SETUP bar's close, direction = the SETUP's.
Everything here is IS only: OOS rows are never read (the unit table is cut to T.is_mask before anything else).

Definitions fixed before any number was looked at
  square-off bar   the last bar of the entry session opening at or before 15:25 (lab.eod_cut / build.eod_bar)
  cap              min(square-off bar, the contract's last candle in the file) — the contract end closes a position ('expiry')
  Foundation stop  features.sl (prev_swing on 1 min, choch_candle on 5 min), engine touch convention: on bar k > entry the
                   stop fires when the bar opens beyond it (fill = open) or its wick touches it (fill = the stop); on a
                   session's first bar the fill is the close (no fill on the opening print). Identical to lab.manage's stop.
  extended trajectory (learners A / B, the oracle with floor)  bars entry+1 .. J_end, J_end = the Foundation stop bar when the
                   stop fires before the cap, else the cap; at bars < J_end the exit is at the bar's close; at J_end the exit is
                   the stop fill (stop bar) or the close (cap). The engine's next-CHoCH exit is NOT applied (the tape is
                   exogenous: every exit policy can be replayed on it).
  pricing          lab.price_trade arithmetic: lot 65, 5 pts slippage per side, lab.trade_charges(ZERODHA_NFO_FUT) on the
                   slipped prices; net per lot = net / lots. price_np mirrors it operation by operation and is checked bit
                   for bit against lab.price_trade (parity.json).
  oracle_free      the best close exit over entry+1 .. cap (no stop): an upper bound for any policy exiting at closes
  oracle_floor     the best exit on the extended trajectory (ties -> earliest): learner B's imitation target
  random control   exit at a uniformly drawn bar of entry+1 .. cap (close fill, no stop), 2,000 seeded draws (seed 'fz|exit');
                   a policy's percentile = share of draws whose mean net per lot is below the policy's (+ half the ties)
  CHoCH against    an events.parquet CHoCH with i > entry, i <= t, dir opposite to the position (known at its own bar under
                   touch rules)
  time stop N      exit at the close of bar entry + N when the position is still open there
  cut convention   learner C's time stop and CHoCH-against exits are a cut of lab.manage's tranches: every tranche whose lab
                   exit bar is later than the cut bar exits at the cut bar's close instead ('time_stop' / 'choch_against');
                   a tranche the lab already closed at or before the cut bar (stop, target, trail) keeps the lab exit (the
                   stop / target on the cut bar itself is assumed first, as lab.manage assumes the stop first on a candle).
                   When both cuts are on, the earlier bar wins.
"""
import os, sys, json, math, bisect, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import numpy as np, pandas as pd
import numba as nb
import harness as H
import lab

LOT, SLIP, SQUARE_OFF = 65, 5.0, "15:25"
CS = H.CS
READS = ("LEAVE", "PENDING", "THIN", "NEW", "REJECT", "ACCEPTED", "FIRST_PRINT", "RECYCLE", "HUNT")
STATE_COLS = ["bars_held", "unreal_pts", "unreal_R", "unreal_atr", "mfe_R", "mae_R", "dd_from_mfe_R", "session_bar", "bars_to_sqoff",
              "atr14", "vol_ratio20"] + [f"read_{r}" for r in READS] + ["room_ahead_atr", "room_behind_atr", "n_choch_since_bos",
              "choch_against", "lots_remaining"]
SEED = "fz|exit"
CONTROL_DRAWS = 2000
LEDGER = os.path.join(HERE, "exit_ledger.jsonl")
VECDIR = os.path.join(HERE, "vectors")


def rng_of(tag):
    return np.random.default_rng(int(hashlib.sha1(f"{SEED}|{tag}".encode()).hexdigest()[:8], 16))


# ---------------------------------------------------------------- pricing (lab.price_trade mirrored operation by operation)
def price_np(entry_px, exit_px, sg, lots=1):
    """Net INR of a futures round trip per lab.price_trade / lab.trade_charges (same operation order, so bit for bit).
    entry_px, exit_px, sg arrays (sg +1 long / -1 short); lots per position. Returns the position's net."""
    e, x = np.asarray(entry_px, dtype=float), np.asarray(exit_px, dtype=float)
    long = np.asarray(sg) > 0
    qty = LOT * lots
    buy_px = np.where(long, e + SLIP, x + SLIP)
    sell_px = np.where(long, x - SLIP, e - SLIP)
    pts = sell_px - buy_px
    gross = pts * qty
    buy, sell = buy_px * qty, sell_px * qty
    pct = lambda v, p: v * p / 100
    if CS.get("brokerage_flat"):
        brokerage = 2 * CS["brokerage_flat"] + 0 * buy
    else:
        brokerage = np.minimum(pct(buy, CS["brokerage_pct"]), CS["brokerage_cap"]) + np.minimum(pct(sell, CS["brokerage_pct"]), CS["brokerage_cap"])
    stt = pct(buy, CS["stt_buy_pct"]) + pct(sell, CS["stt_sell_pct"])
    exch = pct(buy + sell, CS["exchange_pct"])
    sebi = pct(buy + sell, CS["sebi_pct"])
    stamp = pct(buy, CS["stamp_buy_pct"])
    gst = pct(brokerage + exch + sebi, CS["gst_pct"])
    total = brokerage + stt + exch + sebi + stamp + gst
    return gross - total


def exact_R(e, sl, sg):
    """The stop distance R such that lab.manage's stop e - sg * R equals the Foundation stop sl bit for bit (a few ulps of
    search); falls back to sg * (e - sl) when no such double exists. Returns (R, exact)."""
    R = sg * (e - sl)
    if e - sg * R == sl: return R, True
    for k in range(1, 8):
        for cand in (np.nextafter(R, np.inf), np.nextafter(R, -np.inf)):
            r = R
            for _ in range(k): r = np.nextafter(r, np.inf if cand > R else -np.inf)
            if e - sg * float(r) == sl: return float(r), True
    return R, False


# ---------------------------------------------------------------- data
class Data:
    """Bars and the IS unit table of one timeframe with everything the study needs per bar and per trade."""

    def __init__(self, tf):
        self.tf = tf
        B = pd.read_parquet(os.path.join(H.DATA, tf, "bars.parquet"))
        self.B = B
        self.tl = B.datetime.tolist()
        self.o, self.h, self.l, self.c = (B[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
        self.ol, self.hl, self.ll, self.cl = self.o.tolist(), self.h.tolist(), self.l.tolist(), self.c.tolist()
        self.atr = B.atr14.to_numpy(dtype=float)
        self.vr20 = B.vol_ratio20.to_numpy(dtype=float)
        self.sess = B.session_idx.to_numpy(); self.sbar = B.session_bar.to_numpy()
        self.hhmm = B.datetime.str.slice(11, 16).to_numpy()
        self.contract = B.contract.to_numpy(); self.expiry = B.expiry.to_numpy()
        self.nb = len(self.tl)
        self.tix = {t: i for i, t in enumerate(self.tl)}
        # square-off bar per session: the last bar opening at or before 15:25
        last = B.groupby("session_idx").i.max(); first = B.groupby("session_idx").i.min()
        self.sess_first = first.to_numpy(); self.sess_last = last.to_numpy()
        ok = self.hhmm <= SQUARE_OFF
        eod = np.full(len(last), -1, dtype=int)
        idx_ok = np.flatnonzero(ok)
        eod_by = pd.Series(idx_ok).groupby(self.sess[idx_ok]).max()
        eod[eod_by.index.to_numpy()] = eod_by.to_numpy()
        self.sess_eod = eod
        self.contract_last = {}
        for i, cst in enumerate(self.contract): self.contract_last[cst] = i
        # units (IS only)
        T = H.load(tf)
        self.T = T
        self.is_idx = np.flatnonzero(T.is_mask)
        F = T.F.iloc[self.is_idx].reset_index(drop=True)
        self.F = F
        self.n = len(F)
        self.entry = F.setup_i.to_numpy().astype(int)
        self.sg = np.where(F.dir.astype(str).to_numpy() == "up", 1, -1)
        self.e = self.c[self.entry]
        assert np.array_equal(self.e, F.close.to_numpy(dtype=float))
        self.sl = F.sl.to_numpy(dtype=float)
        self.sl_dist = F.sl_dist_pts.to_numpy(dtype=float)
        assert (self.sl_dist > 0).all()
        self.session = F.session_idx.to_numpy().astype(int)
        self.block = T.block[self.is_idx]
        self.eod = self.sess_eod[self.session]
        self.capbar = np.array([self.contract_last[self.contract[i]] for i in self.entry])
        self.J_cap = np.minimum(self.eod, self.capbar)
        assert (self.J_cap > self.entry).all(), "an IS unit with no bar after entry before the cap"
        self.fnd_net = T.net[self.is_idx]                       # the Foundation L1 exit's net (the comparator)
        self.fnd_exit = T.exit_bar[self.is_idx]
        self.l1_reason = F.l1_exit_reason.astype(str).to_numpy()
        self.l1_px = F.l1_exit_px.to_numpy(dtype=float)
        self.fz_traded = F.fz_traded.astype(bool).to_numpy()
        # events: CHoCH bars per direction, n_choch_since_bos per bar
        E = pd.read_parquet(os.path.join(H.DATA, tf, "events.parquet"))
        E = E.sort_values(["i", "seq"]).reset_index(drop=True)
        self.choch_up = np.sort(E.i[(E.kind == "CHoCH") & (E.dir == "up")].to_numpy().astype(int))
        self.choch_dn = np.sort(E.i[(E.kind == "CHoCH") & (E.dir == "down")].to_numpy().astype(int))
        cnt, vals = 0, np.empty(len(E), dtype=int)
        for j, kind in enumerate(E.kind.to_numpy()):
            cnt = 0 if kind == "BOS" else cnt + 1
            vals[j] = cnt
        ev_i = E.i.to_numpy().astype(int)
        pos = np.searchsorted(ev_i, np.arange(self.nb), side="right") - 1
        self.ncsb = np.where(pos >= 0, vals[np.maximum(pos, 0)], 0)           # events with i <= bar
        # the first CHoCH against each position after its entry (or -1)
        self.choch_against = np.full(self.n, -1, dtype=int)
        for j in range(self.n):
            arr = self.choch_dn if self.sg[j] > 0 else self.choch_up
            p = np.searchsorted(arr, self.entry[j], side="right")
            if p < len(arr): self.choch_against[j] = int(arr[p])
        # card read per bar
        C = pd.read_parquet(os.path.join(H.DATA, tf, "fz_card.parquet"), columns=["i", "read"])
        assert (C.i.to_numpy() == np.arange(self.nb)).all()
        rd = C.read.astype(str).to_numpy()
        code = {r: k for k, r in enumerate(READS)}
        self.read_code = np.array([code.get(r, -1) for r in rd], dtype=np.int8)
        assert (self.read_code >= 0).all(), set(rd) - set(READS)
        # rooms alive by bar: birth_bar <= t < retired_bar
        Z = pd.read_parquet(os.path.join(H.DATA, tf, "fz_zones.parquet"))
        self.z_lo = Z.lo.to_numpy(dtype=float); self.z_hi = Z.hi.to_numpy(dtype=float)
        self.z_birth = Z.birth_bar.to_numpy().astype(int)
        self.z_ret = np.where(Z.retired_bar.isna(), self.nb + 1, Z.retired_bar.fillna(self.nb + 1)).astype(int)

    # -- lab.manage inputs
    def cap_time(self, j):
        """(cap, expiry) for lab.manage as rl.contract_end does: the contract's last candle when before the data end."""
        i = self.entry[j]; cst = self.contract[i]; k = self.contract_last[cst]
        if k < self.nb - 1: return self.tl[k], min(self.expiry[i], self.tl[k][:10]) if self.expiry[i] else self.tl[k][:10]
        return self.tl[-1], self.expiry[i]

    def rec(self, j):
        i = self.entry[j]; up = self.sg[j] > 0
        return dict(dir="up" if up else "down", signal="BULLISH" if up else "BEARISH", position="LONG" if up else "SHORT", opt_type="FUT",
                    kind="FUT", instrument=self.contract[i], strike=None, expiry=self.expiry[i], entry_time=self.tl[i], exit_time=self.tl[i],
                    exit_reason="open", open=True, sl=None, entry_px=float(self.c[i]), exit_px=None, und_entry=None, und_exit=None)


def st_of(position):
    """A lab strategy-row dict as rl.py builds it: lot 65, 5 pts slippage, the position block as JSON."""
    return dict(lot_size=LOT, slippage_pts=SLIP, position_json=json.dumps(position, sort_keys=True), atr_period=14)


def position(lots, stop_pts, scale_out, trail):
    p = dict(lots=lots, lock="none", exit="position", stop={"futures_pts": float(stop_pts), "option_pct": 5}, scale_out=scale_out,
             trail=trail, square_off=SQUARE_OFF, reverse=None)
    return p


# ---------------------------------------------------------------- the extended trajectory (numba)
@nb.njit(cache=True)
def _floor(entry, sg, sl, Jcap, o, h, l, c, sess):
    """Per trade: (J_end, stop_hit, fill_px) with the engine / lab.manage touch convention."""
    n = len(entry)
    J = np.empty(n, np.int64); hit = np.zeros(n, np.bool_); px = np.empty(n, np.float64)
    for j in range(n):
        k0 = entry[j]; s = sl[j]; g = sg[j]; end = Jcap[j]
        J[j] = end; px[j] = c[end]
        for k in range(k0 + 1, end + 1):
            if g > 0:
                gap = o[k] <= s; touch = l[k] <= s
            else:
                gap = o[k] >= s; touch = h[k] >= s
            if gap or touch:
                first = k > 0 and sess[k] != sess[k - 1]
                if first: p = c[k]
                elif gap: p = o[k]
                else: p = s
                J[j] = k; hit[j] = True; px[j] = p
                break
    return J, hit, px


def floor(D):
    return _floor(D.entry, D.sg, D.sl, D.J_cap, D.o, D.h, D.l, D.c, D.sess)


@nb.njit(cache=True)
def _states(entry, sg, e, sl_dist, J, hit, fill, eod, choch_against, o, h, l, c, atr, vr20, sbar, read_code, ncsb,
            z_lo, z_hi, z_birth, z_ret, n_reads):
    n = len(entry)
    total = 0
    for j in range(n): total += J[j] - entry[j]
    nf = 11 + n_reads + 5
    X = np.empty((total, nf), np.float32)
    trade = np.empty(total, np.int32); bar = np.empty(total, np.int32)
    exit_net_px = np.empty(total, np.float64)                                # the exit fill at this bar (close, or the terminal fill)
    terminal = np.zeros(total, np.bool_)
    r = 0
    nz = len(z_lo)
    for j in range(n):
        k0 = entry[j]; g = sg[j]; ep = e[j]; sd = sl_dist[j]; end = J[j]
        # rooms possibly alive during this trade
        zi = np.empty(nz, np.int64); m = 0
        for z in range(nz):
            if z_birth[z] <= end and z_ret[z] > k0 + 1:
                zi[m] = z; m += 1
        mfe = 0.0; mae = 0.0
        for k in range(k0 + 1, end + 1):
            fav = g * (h[k] - ep) if g > 0 else g * (l[k] - ep)
            adv = g * (l[k] - ep) if g > 0 else g * (h[k] - ep)
            if fav > mfe: mfe = fav
            if adv < mae: mae = adv
            un = g * (c[k] - ep)
            a = atr[k] if atr[k] > 0 else 1e-9
            X[r, 0] = k - k0
            X[r, 1] = un
            X[r, 2] = un / sd
            X[r, 3] = un / a
            X[r, 4] = mfe / sd
            X[r, 5] = mae / sd
            X[r, 6] = (mfe - un) / sd
            X[r, 7] = sbar[k]
            X[r, 8] = eod[j] - k
            X[r, 9] = atr[k]
            X[r, 10] = vr20[k]
            for q in range(n_reads): X[r, 11 + q] = 1.0 if read_code[k] == q else 0.0
            ahead = np.inf; behind = np.inf
            for q in range(m):
                z = zi[q]
                if z_birth[z] <= k and k < z_ret[z]:
                    for edge in (z_lo[z], z_hi[z]):
                        d = g * (edge - c[k])
                        if d > 0 and d < ahead: ahead = d
                        elif d < 0 and -d < behind: behind = -d
            X[r, 11 + n_reads] = ahead / a if ahead < np.inf else np.nan
            X[r, 12 + n_reads] = behind / a if behind < np.inf else np.nan
            X[r, 13 + n_reads] = ncsb[k]
            X[r, 14 + n_reads] = 1.0 if (choch_against[j] >= 0 and choch_against[j] <= k) else 0.0
            X[r, 15 + n_reads] = 1.0
            trade[r] = j; bar[r] = k
            if k == end:
                terminal[r] = True; exit_net_px[r] = fill[j]
            else:
                exit_net_px[r] = c[k]
            r += 1
    return X, trade, bar, exit_net_px, terminal


def states(D, J, hit, fill):
    X, trade, bar, xpx, term = _states(D.entry, D.sg, D.e, D.sl_dist, J, hit, fill, D.eod, D.choch_against, D.o, D.h, D.l, D.c, D.atr,
                                       D.vr20, D.sbar, D.read_code, D.ncsb, D.z_lo, D.z_hi, D.z_birth, D.z_ret, len(READS))
    net = price_np(D.e[trade], xpx, D.sg[trade], 1)
    return X, trade, bar, xpx, term, net


# ---------------------------------------------------------------- oracles, random control
def oracle_free(D):
    """Best close exit over entry+1 .. J_cap per trade (no stop): (net, bar)."""
    best = np.full(D.n, -np.inf); barb = np.empty(D.n, dtype=int)
    for j in range(D.n):
        ks = np.arange(D.entry[j] + 1, D.J_cap[j] + 1)
        nets = price_np(np.full(len(ks), D.e[j]), D.c[ks], np.full(len(ks), D.sg[j]), 1)
        a = int(np.argmax(nets)); best[j] = nets[a]; barb[j] = ks[a]
    return best, barb


def oracle_floor_from_states(D, trade, bar, net):
    """Best exit on the extended trajectory per trade (ties -> earliest): (net, bar, state row)."""
    best = np.full(D.n, -np.inf); barb = np.full(D.n, -1); row = np.full(D.n, -1)
    order = np.lexsort((bar, trade))                                        # by trade then bar: the first max is the earliest
    for r in order:
        j = trade[r]
        if net[r] > best[j]: best[j], barb[j], row[j] = net[r], bar[r], r
    return best, barb, row


def random_control(D, draws=CONTROL_DRAWS):
    """Mean net per lot per draw over the IS trades: exit at a uniform bar of entry+1 .. J_cap at its close."""
    rng = rng_of(f"random_exit|{D.tf}")
    span = D.J_cap - D.entry
    u = rng.random((draws, D.n))
    k = D.entry[None, :] + 1 + np.floor(u * span[None, :]).astype(int)
    assert (k > D.entry[None, :]).all() and (k <= D.J_cap[None, :]).all()
    nets = price_np(np.broadcast_to(D.e, k.shape), D.c[k], np.broadcast_to(D.sg, k.shape), 1)
    return nets.mean(axis=1), nets


def pct_rank(v, xs):
    xs = np.asarray(xs, dtype=float)
    return round(100 * (float((xs < v).sum()) + 0.5 * float((xs == v).sum())) / len(xs), 1)


# ---------------------------------------------------------------- statistics on per-trade nets
def sign_flip_blocks(diff, block, n_blocks=H.N_BLOCKS):
    """Paired session-block sign-flip test of a per-trade difference: blocks = the harness's 12 IS blocks; the statistic is
    the mean over blocks of the block mean; exact enumeration of the 2^12 sign patterns. Returns one- and two-sided p."""
    d = np.array([diff[block == b].mean() if (block == b).any() else np.nan for b in range(n_blocks)])
    d = d[np.isfinite(d)]; m = len(d); S = d.mean()
    signs = ((np.arange(2 ** m)[:, None] >> np.arange(m)[None, :]) & 1) * 2 - 1
    Ss = (signs * d[None, :]).mean(axis=1)
    return dict(stat=round(float(S), 2), blocks=int(m), p_one_sided=round(float((Ss >= S).mean()), 4), p_two_sided=round(float((np.abs(Ss) >= abs(S)).mean()), 4),
                blocks_positive=int((d > 0).sum()))


def sign_flip_sessions(diff, session, draws=2000, tag=""):
    """The same with sessions as the paired blocks (the per-session sum of the difference), 2,000 seeded random flips."""
    S_ = np.array(sorted(set(session.tolist()))); idx = np.searchsorted(S_, session)
    d = np.bincount(idx, weights=diff, minlength=len(S_))
    rng = rng_of(f"signflip|{tag}")
    flips = rng.integers(0, 2, size=(draws, len(d))) * 2 - 1
    Ss = (flips * d[None, :]).mean(axis=1); S = d.mean()
    return dict(stat_per_session=round(float(S), 2), sessions=int(len(d)), p_one_sided=round(float((Ss >= S).mean()), 4),
                p_two_sided=round(float((np.abs(Ss) >= abs(S)).mean()), 4), sessions_positive=int((d > 0).sum()), sessions_negative=int((d < 0).sum()))


def session_vectors(D, net_variant, mask=None):
    """Harness-compatible per-session vectors: kept = the variant's net (per lot) and count, skipped and all = the Foundation
    L1 exit on the same entries (so harness 'diff' / selection_gain = variant minus Foundation)."""
    rows = np.arange(D.n) if mask is None else np.flatnonzero(mask)
    ses = D.session[rows]; S_ = np.array(sorted(set(ses.tolist()))); idx = np.searchsorted(S_, ses)
    out = dict(sessions=S_)
    out["kept_sum"] = np.bincount(idx, weights=net_variant[rows], minlength=len(S_)); out["kept_n"] = np.bincount(idx, minlength=len(S_)).astype(float)
    out["skipped_sum"] = np.bincount(idx, weights=D.fnd_net[rows], minlength=len(S_)); out["skipped_n"] = out["kept_n"].copy()
    out["all_sum"] = out["skipped_sum"].copy(); out["all_n"] = out["kept_n"].copy()
    return out


def ledger_id(family, config, tf):
    return hashlib.sha1(json.dumps([family, config, tf], sort_keys=True, default=str).encode()).hexdigest()[:16]


def ledger_append(rec, vec):
    os.makedirs(VECDIR, exist_ok=True)
    np.savez_compressed(os.path.join(VECDIR, f"{rec['id']}.npz"), **vec)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, default=lambda z: z.item() if hasattr(z, "item") else str(z)) + "\n")


def read_exit_ledger(family=None, tf=None):
    if not os.path.exists(LEDGER): return []
    rows = [json.loads(x) for x in open(LEDGER, encoding="utf-8") if x.strip()]
    return [r for r in rows if (family is None or r["family"] == family or r["family"].startswith(family + "/")) and (tf is None or r["tf"] == tf)]


def load_vec(cid):
    z = np.load(os.path.join(VECDIR, f"{cid}.npz")); return {k: z[k] for k in z.files}


def summary(D, net, lots=1):
    """Headline numbers of a per-trade net (per lot) against the Foundation L1 exit on the same entries."""
    d = net - D.fnd_net
    w, l_ = net[net > 0], net[net <= 0]
    return dict(n=int(D.n), mean=round(float(net.mean()), 2), fnd_mean=round(float(D.fnd_net.mean()), 2), diff=round(float(d.mean()), 2),
                win_rate=round(float((net > 0).mean()), 4), pf=round(float(w.sum() / -l_.sum()), 3) if len(l_) and l_.sum() else None,
                t=round(float(d.mean() / (d.std(ddof=1) / math.sqrt(len(d)))), 2) if d.std(ddof=1) > 0 else None,
                mean_per_session=round(float(np.bincount(np.searchsorted(np.array(sorted(set(D.session.tolist()))), D.session), weights=net).mean()), 2),
                sign_blocks=int(sum(1 for b in range(H.N_BLOCKS) if (D.block == b).any() and d[D.block == b].mean() > 0)))
