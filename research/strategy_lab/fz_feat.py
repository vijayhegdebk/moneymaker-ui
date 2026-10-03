"""FZ v3 as-of features at a Foundation SETUP bar: the vocabulary a learned gate (Strategies 13 / 14, entry_rule fz_v3) reads.

One function, `features_at(ctx, k, direction, choch_bar)`, returns the named as-of columns of the FZ v3 study table
(fz_v3/out/data/<tf>/features.parquet: identity / clock, price window, regime from the engine's event stream, volume, levels,
the session's closed-trade ledger, the room card and the frozen gate's ledger row) for the SETUP at bar k, from bars <= k
only. fz_v3/out/build/build.py builds the study table with this module, and the lab evaluates a strategy file's gate rules
with it, so a rule learned on the table reads exactly the number the lab computes live (tests/test_fz_parity.py check 7).

Information boundary (declared, tested by truncation): candles up to k; the frozen engine view (swings by confirmation bar,
CHoCH / BOS events by bar, the protected level per bar); fz.run's card row at k and its ledger row for the SETUP (as-of
columns only: never outcome_gate / fill_* / watch_outcome); the rooms alive at k (birth_bar <= k < retired_bar); and the
session's Foundation trades that have EXITED by k (the desk's own closed ledger). Never a trade still open, never a label.
"""
import bisect, datetime as D
import numpy as np

H1_OF = {1: 60, 5: 12}                        # bars in one hour per timeframe (minutes per bar -> bars)
MED_MIN_BARS = 5                              # prior same-session bars a volume baseline needs
BREAK_ATR = 0.5                               # a touch 'broke' when a close beyond the level exceeds this x ATR14
CARD_KEYS = ("zone_id", "visit_n", "this_bars", "this_vol", "vol_na", "first_bars", "first_vol", "first_vol_na", "read", "left_id",
             "out_run", "out_side", "gap_pts", "wick_depth", "last_hunt_at", "last_hunt_dir", "last_reject_at", "last_reject_dir",
             "cluster_sit", "prev_bars", "prev_vol", "last_leave_failed", "in_id", "leave_side", "leave_vol_ok", "leave_kind",
             "first_clock_lived", "touches")
LEDGER_ASOF = ("zone_id", "zone_kind", "band_lo", "band_hi", "visit_n", "this_bars", "this_vol", "first_bars", "first_vol", "vol_na",
               "first_vol_na", "read", "left_id", "in_id", "level_in_band", "gate", "block_reason", "branch", "take_why",
               "entered_zone_id", "entered_visit_n", "entered_read", "leave_vol_ok", "leave_kind", "watch_kind", "watch_band_id")


def hour_bin(hm, open_until, no_entry_from):
    return "<" + open_until if hm < open_until else ">=" + no_entry_from if hm >= no_entry_from else hm[:2]


class Context:
    """Everything features_at reads, built once per candle series. bars: t/o/h/l/c/v + fm_na + atr14 (as fz.run gets them);
    view: fz_exec.view(r) plus r['events'] (kind, dir, i, flip) - the frozen engine view; card / ledger_rows: fz.run's outputs;
    zones: fz.run's zones (birth_bar, retired_bar, lo, hi, id); closed_trades: [(entry, exit, pts, net, exit_reason, session)]
    for the session ledger (Foundation trades, read only once exited); tf_min: 1 or 5; clocks: the fz block's
    open_window_until / no_entry_from (for hour_bin); contract / expiry per bar (optional)."""

    def __init__(self, bars, view, events, card, ledger_rows, zones, closed_trades, tf_min, open_until, no_entry_from,
                 contract=None, expiry=None, setups=None):
        t, o, h, l, c, v = (bars[k] for k in "tohlcv")
        self.t = t; self.n = n = len(t)
        self.O, self.H, self.L, self.C, self.V = (np.asarray(x, dtype=float) for x in (o, h, l, c, v))
        self.ATR = np.asarray(bars["atr14"], dtype=float); self.FMNA = np.asarray(bars["fm_na"], dtype=bool)
        self.tf_min, self.H1, self.H3 = tf_min, H1_OF[tf_min], 3 * H1_OF[tf_min]
        self.touch_lookback, self.touch_verdict = self.H1, 15 // tf_min
        self.open_until, self.no_entry_from = open_until, no_entry_from
        sess, sbar = [0] * n, [0] * n
        for i in range(1, n):
            if t[i][:10] != t[i - 1][:10]: sess[i], sbar[i] = sess[i - 1] + 1, 0
            else: sess[i], sbar[i] = sess[i - 1], sbar[i - 1] + 1
        self.sess, self.sbar = np.asarray(sess), np.asarray(sbar)
        self.sess_open_i = {}
        for i in range(n):
            if sbar[i] == 0: self.sess_open_i[sess[i]] = i
        self.contract, self.expiry = contract, expiry
        # volume baselines: median of the previous 20 / 60 bars of the same session (excluding the bar), at least 5 of them
        self.vol_med20, self.vol_med60 = self._rolling_median(20), self._rolling_median(60)
        usable = ~self.FMNA
        with np.errstate(all="ignore"):
            self.r20 = np.where(usable & (self.vol_med20 > 0), self.V / self.vol_med20, np.nan)
            self.r60 = np.where(usable & (self.vol_med60 > 0), self.V / self.vol_med60, np.nan)
        cum = np.zeros(n); acc = 0.0
        for i in range(n):
            acc = self.V[i] if sbar[i] == 0 else acc + self.V[i]; cum[i] = acc
        self.sess_cumvol = cum
        S = int(self.sess.max()) + 1; SB = int(self.sbar.max()) + 1
        M = np.full((S, SB), np.nan); M[self.sess, self.sbar] = cum
        ref = np.full((S, SB), np.nan)
        for s_ in range(1, S):
            lo_ = max(0, s_ - 20)
            if s_ - lo_ >= 5:
                with np.errstate(all="ignore"): ref[s_] = np.nanmedian(M[lo_:s_], axis=0)
        with np.errstate(all="ignore"): self.cumratio = np.where(usable, cum / ref[self.sess, self.sbar], np.nan)
        # the engine view
        self.ev_i = np.array([e["i"] for e in events]); self.ev_kind = np.array([e["kind"] for e in events])
        self.ev_dir = np.array([e["dir"] for e in events]); self.ev_flip = np.array([int(bool(e.get("flip"))) for e in events])
        self.ch_lvl = {i: lvl for i, d, lvl in view["chs"]}
        self.ch_dir = {i: d for i, d, lvl in view["chs"]}
        sw = view["swings"]                                    # (kind, bar, price, conf) in confirmation order
        self.swH = [(s[3], s[2], s[1]) for s in sw if s[0] == "H"]; self.swL = [(s[3], s[2], s[1]) for s in sw if s[0] == "L"]
        self.swH_conf = [x[0] for x in self.swH]; self.swL_conf = [x[0] for x in self.swL]
        self.sw_conf_all = np.array([s[3] for s in sw])
        self.PROT = np.array([np.nan if p is None else p for p in view["prot"]], dtype=float)
        self.card = card; self.ledger = {row["i"]: row for row in ledger_rows}
        self.z_lo = np.array([z["lo"] for z in zones], dtype=float); self.z_hi = np.array([z["hi"] for z in zones], dtype=float)
        self.z_birth = np.array([z["birth_bar"] for z in zones]); self.z_id = np.array([z["id"] for z in zones])
        self.z_ret = np.array([z["retired_bar"] if z["retired_bar"] is not None else np.inf for z in zones], dtype=float)
        self.closed_by_sess = {}
        for tr in closed_trades: self.closed_by_sess.setdefault(tr[5], []).append(tr)
        self.setups_by_sess = {}
        for i, d, ch in (setups or view["setups"]): self.setups_by_sess.setdefault(int(self.sess[i]), []).append(i)

    def _rolling_median(self, N):
        out = np.full(self.n, np.nan)
        v, sbar = self.V, self.sbar
        for i in range(self.n):
            m = min(N, int(sbar[i]))
            if m >= MED_MIN_BARS: out[i] = np.median(v[i - m:i])
        return out


def features_at(ctx, k, d, ch):
    """The as-of feature dict of the SETUP at bar k (direction d, CHoCH bar ch). Column names as the study table."""
    t = ctx.t; H_, L_, C_, O_, V, ATR = ctx.H, ctx.L, ctx.C, ctx.O, ctx.V, ctx.ATR
    up, sg, s = d == "up", (1 if d == "up" else -1), int(ctx.sess[k])
    j0 = ctx.sess_open_i[s]; a = float(ATR[k]) or None; ck = float(C_[k])
    row = dict(setup_i=int(k), time=t[k], date=t[k][:10], session_idx=s, session_bar=int(ctx.sbar[k]), hhmm=t[k][11:16], hour=int(t[k][11:13]),
               hour_bin=hour_bin(t[k][11:16], ctx.open_until, ctx.no_entry_from), minute_of_day=int(t[k][11:13]) * 60 + int(t[k][14:16]),
               dow=D.date.fromisoformat(t[k][:10]).weekday(), dir=d, dir_sign=sg, choch_i=int(ch), choch_time=t[ch], bars_since_choch=int(k - ch),
               choch_same_session=bool(ctx.sess[ch] == s), open=float(O_[k]), high=float(H_[k]), low=float(L_[k]), close=ck)
    if ctx.contract is not None:
        row["contract"] = ctx.contract[k]
        row["days_to_expiry"] = (D.date.fromisoformat(ctx.expiry[k]) - D.date.fromisoformat(t[k][:10])).days
    # ---- price window
    def rng(lo_i): return float(H_[lo_i:k + 1].max() - L_[lo_i:k + 1].min())
    r1, r3 = rng(max(j0, k - ctx.H1 + 1)), rng(max(j0, k - ctx.H3 + 1))
    so = float(O_[j0]); sh_, sl_ = float(H_[j0:k + 1].max()), float(L_[j0:k + 1].min())
    prev_close = float(C_[j0 - 1]) if j0 > 0 else None
    seg = C_[max(j0, k - ctx.H1):k + 1]
    er = float(abs(seg[-1] - seg[0]) / np.abs(np.diff(seg)).sum()) if len(seg) >= 6 and np.abs(np.diff(seg)).sum() > 0 else None
    row.update(atr14=round(float(ATR[k]), 4), atr_bps=round(1e4 * ATR[k] / ck, 3),
               range_1h_pts=round(r1, 2), range_1h_atr=round(r1 / a, 4) if a else None,
               range_3h_pts=round(r3, 2), range_3h_atr=round(r3 / a, 4) if a else None,
               range_since_choch_atr=round(float(H_[ch:k + 1].max() - L_[ch:k + 1].min()) / a, 4) if a else None,
               bar_range_pts=round(float(H_[k] - L_[k]), 2), bar_body_pts=round(float(C_[k] - O_[k]), 2),
               bar_range_atr=round(float(H_[k] - L_[k]) / a, 4) if a else None,
               close_pos_in_bar=round(float((C_[k] - L_[k]) / (H_[k] - L_[k])), 4) if H_[k] > L_[k] else None,
               sess_open=so, close_vs_sess_open_pts=round(ck - so, 2), sess_range_atr=round((sh_ - sl_) / a, 4) if a else None,
               pos_in_session_range=round((ck - sl_) / (sh_ - sl_), 4) if sh_ > sl_ else None,
               gap_pts=round(so - prev_close, 2) if prev_close is not None else None, prev_close=prev_close,
               ret_1h_pts=round(float(C_[k] - C_[k - ctx.H1]), 2) if k - ctx.H1 >= j0 else None,
               ret_3h_pts=round(float(C_[k] - C_[k - ctx.H3]), 2) if k - ctx.H3 >= j0 else None, er_1h=round(er, 4) if er is not None else None)
    # ---- regime from the event stream
    m = bisect.bisect_right(ctx.ev_i, k)
    K, Dd, F, I = ctx.ev_kind[:m], ctx.ev_dir[:m], ctx.ev_flip[:m], ctx.ev_i[:m]
    bos_pos = np.flatnonzero(K == "BOS"); ch_pos = np.flatnonzero(K == "CHoCH")
    lb = bos_pos[-1] if len(bos_pos) else -1; lc = ch_pos[-1] if len(ch_pos) else -1
    since_bos = K[lb + 1:]
    row.update(n_events_asof=int(m), n_choch_since_bos=int((since_bos == "CHoCH").sum()),
               n_flip_since_bos=int(F[lb + 1:][since_bos == "CHoCH"].sum()) if len(since_bos) else 0,
               n_bos_since_choch=int((K[lc + 1:] == "BOS").sum()),
               bars_since_bos=int(k - I[lb]) if lb >= 0 else None, last_bos_dir=str(Dd[lb]) if lb >= 0 else "none",
               last_bos_same_session=bool(ctx.sess[I[lb]] == s) if lb >= 0 else None)
    today = ctx.sess[I] == s; Kt = K[today]
    bt = np.flatnonzero(Kt == "BOS"); lbt = bt[-1] if len(bt) else -1
    row["n_choch_since_bos_today"] = int((Kt[lbt + 1:] == "CHoCH").sum())
    row["bars_since_prev_choch"] = int(k - I[ch_pos[-2]]) if len(ch_pos) >= 2 else None
    row["last_choch_dir"] = str(Dd[lc]) if lc >= 0 else "none"
    last6 = list(zip(K[-6:], Dd[-6:]))
    row["alt_dir6"] = int(sum(1 for (_, d1), (_, d2) in zip(last6, last6[1:]) if d1 != d2))
    row["alt_kind6"] = int(sum(1 for (k1, _), (k2, _) in zip(last6, last6[1:]) if k1 != k2))
    row["last6_kinds"] = " ".join(("C" if kk == "CHoCH" else "B") + ("u" if dd == "up" else "d") for kk, dd in last6)
    run_ = 0
    for kk in K[::-1]:
        if kk == "CHoCH": run_ += 1
        else: break
    row["choch_run"] = int(run_)
    for name, N in (("1h", ctx.H1), ("3h", ctx.H3)):
        w = I > k - N
        row[f"n_choch_{name}"] = int((K[w] == "CHoCH").sum()); row[f"n_bos_{name}"] = int((K[w] == "BOS").sum())
    row["n_events_today"] = int(today.sum()); row["n_choch_today"] = int((Kt == "CHoCH").sum()); row["n_bos_today"] = row["n_events_today"] - row["n_choch_today"]
    # ---- volume
    r20, r60 = ctx.r20, ctx.r60
    f = dict(vol=float(V[k]), vol_med20_prior=None if np.isnan(ctx.vol_med20[k]) else float(ctx.vol_med20[k]),
             vol_med60_prior=None if np.isnan(ctx.vol_med60[k]) else float(ctx.vol_med60[k]),
             vol_ratio20=None if np.isnan(r20[k]) else round(float(r20[k]), 4), vol_ratio60=None if np.isnan(r60[k]) else round(float(r60[k]), 4),
             vol_na=bool(ctx.FMNA[k]), sess_cumvol_ratio20s=None if np.isnan(ctx.cumratio[k]) else round(float(ctx.cumratio[k]), 4))
    for N in (5, 15):
        seg = r20[max(j0, k - N + 1):k + 1]
        f[f"vol_max_ratio20_{N}"] = round(float(np.nanmax(seg)), 4) if np.isfinite(seg).any() else None
    for thr in (2, 3):
        seg = r20[j0:k + 1]
        with np.errstate(invalid="ignore"): ok = np.flatnonzero(seg >= thr)
        if len(ok) == 0: hv = dict(bars_since=None, dir="none", dir_agree=None, low_held=None, high_held=None, ratio=None)
        else:
            j = j0 + ok[-1]
            hd = "up" if C_[j] > O_[j] else "down" if C_[j] < O_[j] else "flat"
            if j == k: hv = dict(bars_since=0, dir=hd, dir_agree=None, low_held=None, high_held=None, ratio=round(float(r20[j]), 3))
            else: hv = dict(bars_since=int(k - j), dir=hd, dir_agree=None, low_held=bool(L_[j + 1:k + 1].min() >= L_[j]),
                            high_held=bool(H_[j + 1:k + 1].max() <= H_[j]), ratio=round(float(r20[j]), 3))
        hv["dir_agree"] = (hv["dir"] == d) if hv["dir"] != "none" else None
        f.update({f"hv{thr}_{kk}": vv for kk, vv in hv.items()})
    seg = r20[ch:k + 1]
    f["vol_ratio20_at_choch"] = None if np.isnan(r20[ch]) else round(float(r20[ch]), 4)
    f["vol_max_ratio20_choch_to_k"] = round(float(np.nanmax(seg)), 4) if np.isfinite(seg).any() else None
    j_prev = ctx.sess_open_i.get(s - 1)
    if j_prev is not None:
        cumv = float(V[j0:k + 1].sum()); prev = float(V[j_prev:min(j_prev + int(ctx.sbar[k]) + 1, j0)].sum())
        f["sess_vol_vs_prev_sess"] = round(cumv / prev, 4) if prev else None
    else: f["sess_vol_vs_prev_sess"] = None
    row.update(f)
    # ---- levels
    lvl = ctx.ch_lvl.get(ch)
    jH, jL = bisect.bisect_right(ctx.swH_conf, k) - 1, bisect.bisect_right(ctx.swL_conf, k) - 1
    shp = ctx.swH[jH][1] if jH >= 0 else None; slp = ctx.swL[jL][1] if jL >= 0 else None
    p = ctx.PROT[k]; p = None if np.isnan(p) else float(p)
    row.update(prot_lvl=p, dist_prot_dir_atr=round(sg * (ck - p) / a, 4) if (p is not None and a) else None,
               last_sh_px=shp, last_sl_px=slp,
               dist_sh_atr=round((shp - ck) / a, 4) if (shp is not None and a) else None,
               dist_sl_atr=round((ck - slp) / a, 4) if (slp is not None and a) else None,
               last_sh_bars_ago=int(k - ctx.swH[jH][2]) if jH >= 0 else None, last_sl_bars_ago=int(k - ctx.swL[jL][2]) if jL >= 0 else None,
               swing_ahead_dist_atr=(round((shp - ck) / a, 4) if (shp is not None and a) else None) if up else (round((ck - slp) / a, 4) if (slp is not None and a) else None),
               choch_lvl=lvl, dist_choch_lvl_atr=round(sg * (ck - lvl) / a, 4) if (lvl is not None and a) else None,
               n_swings_1h=int(((ctx.sw_conf_all <= k) & (ctx.sw_conf_all > k - ctx.H1)).sum()),
               choch_bar_range_atr=round(float(H_[ch] - L_[ch]) / a, 4) if a else None,
               move_since_choch_pts=round(float(sg * (ck - C_[ch])), 2))
    cands = ([(abs(shp - ck), "H", shp)] if shp is not None else []) + ([(abs(slp - ck), "L", slp)] if slp is not None else [])
    Ls = None
    if cands:
        _, kind_, Ls = min(cands); row.update(swing_near_kind=kind_, swing_near_dist_dir_atr=round(sg * (Ls - ck) / a, 4) if a else None)
    else: row.update(swing_near_kind="", swing_near_dist_dir_atr=None)
    alive = (ctx.z_birth <= k) & (ctx.z_ret > k)
    row["n_rooms_alive"] = int(alive.sum())
    Lr = None
    if alive.any():
        lo_, hi_, ids = ctx.z_lo[alive], ctx.z_hi[alive], ctx.z_id[alive]
        edges = np.concatenate([lo_, hi_]); eids = np.concatenate([ids, ids]); ekind = np.array(["lo"] * len(lo_) + ["hi"] * len(hi_))
        dd = edges - ck; jn = int(np.argmin(np.abs(dd)))
        Lr = float(edges[jn])
        row.update(room_edge=Lr, room_edge_dist_dir_atr=round(sg * dd[jn] / a, 4) if a else None, room_edge_id=str(eids[jn]), room_edge_kind=str(ekind[jn]))
        ahead = sg * dd; ah = ahead[ahead > 1e-9]; bh = -ahead[ahead < -1e-9]
        row["room_ahead_dist_atr"] = round(float(ah.min() / a), 4) if (len(ah) and a) else None
        row["room_behind_dist_atr"] = round(float(bh.min() / a), 4) if (len(bh) and a) else None
    else:
        row.update(room_edge=None, room_edge_dist_dir_atr=None, room_edge_id="", room_edge_kind="", room_ahead_dist_atr=None, room_behind_dist_atr=None)
    for name, Lv in (("prot", p), ("room", Lr), ("swing", Ls)):
        ne, verdict, ago = touch_stats(ctx, Lv, k)
        row.update({f"touch_{name}_n": ne, f"touch_{name}_last": verdict, f"touch_{name}_bars_ago": ago})
    # ---- the session's closed ledger
    closed = [x for x in ctx.closed_by_sess.get(s, []) if x[1] <= k and x[0] < k]
    row.update(today_n_closed_asof=len(closed), today_net_asof=round(sum(x[3] for x in closed), 2), today_pts_asof=round(sum(x[2] for x in closed), 2),
               today_n_stops_asof=sum(1 for x in closed if x[4] == "stop_loss"),
               today_n_setups_before=sum(1 for i in ctx.setups_by_sess.get(s, []) if i < k),
               last_closed_net_asof=closed[-1][3] if closed else None, last_closed_reason_asof=closed[-1][4] if closed else None)
    # ---- the card and the frozen gate's ledger row (as-of columns)
    cd = ctx.card[k]
    row.update({"card_" + kk: cd[kk] for kk in CARD_KEYS})
    Lg = ctx.ledger.get(k)
    if Lg is not None:
        row.update({"fz_" + kk: Lg[kk] for kk in LEDGER_ASOF})
        lo_, hi_ = Lg["band_lo"], Lg["band_hi"]
        if lo_ is not None and hi_ is not None and hi_ > lo_:
            row.update(fz_band_width=round(hi_ - lo_, 2), fz_band_width_atr=round((hi_ - lo_) / ATR[k], 4) if ATR[k] else None,
                       fz_pos_in_band=round((ck - lo_) / (hi_ - lo_), 4),
                       fz_pos_in_band_dir=round(((ck - lo_) if up else (hi_ - ck)) / (hi_ - lo_), 4),
                       fz_dist_band_edge_ahead=round((hi_ - ck) if up else (ck - lo_), 2),
                       fz_dist_band_edge_behind=round((ck - lo_) if up else (hi_ - ck), 2))
        else:
            row.update(fz_band_width=None, fz_band_width_atr=None, fz_pos_in_band=None, fz_pos_in_band_dir=None, fz_dist_band_edge_ahead=None, fz_dist_band_edge_behind=None)
    live = (not cd["vol_na"]) and cd["first_vol_na"] is False and (cd["first_vol"] or 0) > 0 and cd["this_vol"] is not None
    row["card_vol_ratio"] = round(cd["this_vol"] / cd["first_vol"], 4) if live else None
    row["card_bars_since_hunt"] = (k - cd["last_hunt_at"]) if cd["last_hunt_at"] is not None else None
    row["card_bars_since_reject"] = (k - cd["last_reject_at"]) if cd["last_reject_at"] is not None else None
    row["card_hunt_dir_agree"] = (cd["last_hunt_dir"] == d) if cd["last_hunt_dir"] is not None else None
    row["card_in_room"] = cd["in_id"] is not None; row["card_ref_room_live"] = cd["zone_id"] is not None
    return row


def touch_stats(ctx, Lv, k):
    """Touch episodes of level Lv in the last hour before k (a bar touches when low <= Lv <= high); the last episode's verdict
    within 15 minutes after it, never past k: broke / held / pending / none / na. Returns (episodes, verdict, bars since)."""
    if Lv is None or not np.isfinite(Lv): return None, "na", None
    L_, H_, C_, O_, ATR = ctx.L, ctx.H, ctx.C, ctx.O, ctx.ATR
    j0 = max(0, k - ctx.touch_lookback)
    hit = (L_[j0:k] <= Lv) & (H_[j0:k] >= Lv)
    if not hit.any(): return 0, "none", None
    idx = np.flatnonzero(hit) + j0
    starts = idx[np.r_[True, np.diff(idx) > 1]]
    js, je = int(starts[-1]), int(idx[-1])
    ref_px = C_[js - 1] if js >= 1 else O_[js]
    side = np.sign(ref_px - Lv) or np.sign(O_[js] - Lv)
    if side == 0: return int(len(starts)), "na", int(k - je)
    a = ATR[je]; w0, w1 = je + 1, min(je + ctx.touch_verdict, k)
    broke = False
    if w1 >= w0:
        cc = C_[w0:w1 + 1]
        broke = bool(((Lv - cc) > BREAK_ATR * a).any() if side > 0 else ((cc - Lv) > BREAK_ATR * a).any())
    verdict = "broke" if broke else "pending" if je + ctx.touch_verdict > k else "held"
    return int(len(starts)), verdict, int(k - je)


# ---------------------------------------------------------------- rule lists
OPS = {">=": lambda x, y: x >= y, ">": lambda x, y: x > y, "<=": lambda x, y: x <= y, "<": lambda x, y: x < y,
       "==": lambda x, y: x == y, "!=": lambda x, y: x != y, "in": lambda x, y: x in y, "not_in": lambda x, y: x not in y}


def holds(cond, row):
    """One comparison [column, op, value] on a feature row; a None / NaN feature never satisfies a comparison."""
    col, op, val = cond
    x = row.get(col)
    if x is None or (isinstance(x, float) and x != x): return False
    if isinstance(x, bool) and isinstance(val, (int, float)) and not isinstance(val, bool): x = int(x)
    return bool(OPS[op](x, val))


def apply_rules(rules, row, default="take"):
    """A rule list [{'if': [cond, ...], 'then': 'skip' | 'take', ...}] in order: the first rule whose conditions all hold
    decides; else `default`. Returns (decision, the rule's id or None)."""
    for r in rules:
        if all(holds(c, row) for c in r["if"]): return r["then"], r.get("id")
    return default, None
