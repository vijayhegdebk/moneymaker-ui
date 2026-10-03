"""Levels Likely to Break (Zeiierman), reconstructed from its published description and backtested on NIFTY near-month
futures (see PREREG.md in this folder for what is known, what is assumed, and the judgement fixed before any run).

    python levels_break.py            # both timeframes -> results.json, trades_<tf>.csv, REPORT.md numbers
    python levels_break.py --trunc    # look-ahead check: signals before 2025-06-30 12:00 identical on truncated bars
"""
import os, sys, json, math, argparse
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, LAB)
import lab  # noqa: E402  (trade_charges)

CFG = dict(pivot_left=5, pivot_right=5, tol_atr=0.25, life_sessions=3, stop_atr=1.0, target_r=2.0,
           squeeze_bars=10, square_off="15:25", lot=65, slippage_pts=5.0, draws=1000, seed=20261003)
CHARGES = json.load(open(os.path.join(LAB, "config", "charges.json")))["ZERODHA_NFO_FUT"]
BARS_PER_SESSION = {"minute": 375, "5minute": 75}
CUT = "2025-06-30 12:00:00"
OOS_FROM = "2026-01-01"


def load(tf, upto=None):
    b = pd.read_parquet(os.path.join(LAB, "fz_v3", "out", "data", tf, "bars.parquet"))
    b["t"] = b["datetime"].astype(str)
    if upto: b = b[b.t <= upto].reset_index(drop=True)
    return b


# ---------------------------------------------------------------- the indicator (causal: a pivot is used from bar k+R)
def levels_and_breaks(b, tf, cfg=CFG):
    L, R, tol = cfg["pivot_left"], cfg["pivot_right"], cfg["tol_atr"]
    life = cfg["life_sessions"] * BARS_PER_SESSION[tf]
    H, Lo, C = b.high.to_numpy(), b.low.to_numpy(), b.close.to_numpy()
    A = b.atr14.to_numpy(); K = b.contract.to_numpy()
    n = len(b)
    cand = {+1: [], -1: []}          # side -> list of (pivot bar, price)   (+1 = high / resistance, -1 = low / support)
    active = []                      # dicts: side, level, formed, p1, p2, retests
    sig = []
    for j in range(n):
        # contract change: everything resets (a level of the old contract is not a price on the new one)
        if j > 0 and K[j] != K[j - 1]:
            cand = {+1: [], -1: []}; active = []
        # 1) confirm the pivot at k = j - R (needs L bars before and R bars after, all of the same contract)
        k = j - R
        if k - L >= 0 and K[k - L] == K[j] and not np.isnan(A[j]):
            for side, arr in ((+1, H), (-1, Lo)):
                v = arr[k]
                before, after = arr[k - L:k], arr[k + 1:j + 1]
                is_piv = (v > before.max() and v >= after.max()) if side > 0 else (v < before.min() and v <= after.min())
                if not is_piv: continue
                # drop candidates that expired or were closed through since they formed
                keep = []
                for (pk, pv) in cand[side]:
                    if j - pk > life: continue
                    seg = C[pk + 1:j + 1]
                    if (side > 0 and seg.size and seg.max() > pv) or (side < 0 and seg.size and seg.min() < pv): continue
                    keep.append((pk, pv))
                cand[side] = keep
                match = None
                for idx in range(len(cand[side]) - 1, -1, -1):            # most recent matching candidate
                    pk, pv = cand[side][idx]
                    if abs(v - pv) <= tol * A[j]:
                        match = idx; break
                if match is None:
                    cand[side].append((k, v))
                else:
                    pk, pv = cand[side].pop(match)
                    lvl = max(v, pv) if side > 0 else min(v, pv)
                    active.append(dict(side=side, level=lvl, formed=j, p1=pk, p2=k, retests=0))
        # 2) breaks and retests on bar j (a level formed on bar j can only break from bar j + 1)
        still = []
        for lv in active:
            if j - lv["formed"] > life: continue
            if lv["formed"] == j: still.append(lv); continue
            s, lvl = lv["side"], lv["level"]
            broke = C[j] > lvl if s > 0 else C[j] < lvl
            if broke:
                lo_ = Lo[j - cfg["squeeze_bars"] + 1:j + 1] if s > 0 else H[j - cfg["squeeze_bars"] + 1:j + 1]
                slope = np.polyfit(np.arange(len(lo_)), lo_, 1)[0] if len(lo_) >= 3 else 0.0
                squeeze = slope > 0 if s > 0 else slope < 0
                sig.append(dict(i=j, t=b.t.iat[j], side=s, level=lvl, formed=lv["formed"], pivot1=lv["p1"], pivot2=lv["p2"],
                                retests=lv["retests"], squeeze_slope=float(slope), pressure=bool(lv["retests"] >= 1 and squeeze)))
                continue
            near = (H[j] >= lvl - tol * A[j]) if s > 0 else (Lo[j] <= lvl + tol * A[j])
            if near: lv["retests"] += 1
            still.append(lv)
        active = still
    return pd.DataFrame(sig)


# ---------------------------------------------------------------- trade simulation (lab fill conventions)
def session_cutoffs(b, square_off):
    """For every bar: the index of the last bar of its session opening at or before square_off, capped at the contract's last bar."""
    t = b.t.to_numpy(); d = b.date.astype(str).to_numpy(); K = b.contract.to_numpy()
    n = len(b); cut = np.empty(n, dtype=int)
    last_sess = {}
    for i in range(n):
        if t[i][11:16] <= square_off: last_sess[d[i]] = i
    last_k = {}
    for i in range(n): last_k[K[i]] = i
    for i in range(n): cut[i] = min(last_sess.get(d[i], i), last_k[K[i]])
    return cut


def price(entry, exit_, side, cfg=CFG):
    lot, slip = cfg["lot"], cfg["slippage_pts"]
    buy, sell = (entry + slip, exit_ - slip) if side > 0 else (exit_ + slip, entry - slip)
    pts = sell - buy
    chg = lab.trade_charges(CHARGES, buy, sell, lot)["total"]
    return pts * lot - chg, (exit_ - entry) * side * lot, pts


def simulate(b, i, side, stop_dist, cut, cfg=CFG):
    """Enter at close[i] in `side`; stop at stop_dist points, target target_r x stop_dist; exit by cut[i]."""
    O, H, Lo, C = b.open.to_numpy(), b.high.to_numpy(), b.low.to_numpy(), b.close.to_numpy()
    e = C[i]; stop = e - side * stop_dist; tgt = e + side * cfg["target_r"] * stop_dist
    end = cut[i]
    mfe = mae = 0.0
    for j in range(i + 1, end + 1):
        fav = (H[j] - e) if side > 0 else (e - Lo[j]); adv = (Lo[j] - e) if side > 0 else (e - H[j])
        mfe, mae = max(mfe, fav), min(mae, adv)
        if (side > 0 and O[j] <= stop) or (side < 0 and O[j] >= stop): return j, O[j], "stop_gap", mfe, mae
        if (side > 0 and Lo[j] <= stop) or (side < 0 and H[j] >= stop): return j, stop, "stop", mfe, mae
        if (side > 0 and H[j] >= tgt) or (side < 0 and Lo[j] <= tgt): return j, tgt, "target", mfe, mae
    return end, C[end], "eod", mfe, mae


def run_trades(b, sig, cut, variant, cfg=CFG):
    A, sb, t = b.atr14.to_numpy(), b.session_bar.to_numpy(), b.t.to_numpy()
    rows, busy_until = [], -1
    s = sig if variant == "A" else sig[sig.pressure]
    for r in s.itertuples():
        i = r.i
        if i <= busy_until or sb[i] == 0 or t[i][11:16] >= cfg["square_off"] or i >= cut[i]: continue
        stop_dist = abs(b.close.iat[i] - (r.level - r.side * cfg["stop_atr"] * A[i]))
        j, px, why, mfe, mae = simulate(b, i, r.side, stop_dist, cut, cfg)
        net, gross_nocost, pts = price(b.close.iat[i], px, r.side, cfg)
        rows.append(dict(entry_i=i, entry_time=t[i], side="LONG" if r.side > 0 else "SHORT", level=round(r.level, 2), entry_px=b.close.iat[i],
                         stop_dist=round(stop_dist, 2), stop_atr=round(stop_dist / A[i], 3), exit_i=j, exit_time=t[j], exit_px=round(px, 2),
                         exit_reason=why, gross_pts=round((px - b.close.iat[i]) * r.side, 2), net=round(net, 2), mfe=round(mfe, 2), mae=round(mae, 2),
                         retests=r.retests, pressure=r.pressure))
        busy_until = j
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- statistics and controls
def stats(tr):
    if not len(tr): return dict(n=0)
    x = tr.net.to_numpy(); g = tr.gross_pts.to_numpy()
    wk = tr.groupby(pd.to_datetime(tr.entry_time).dt.to_period("W")).net.sum()
    wins, losses = x[x > 0].sum(), -x[x <= 0].sum()
    return dict(n=int(len(x)), net_total=round(float(x.sum()), 0), net_mean=round(float(x.mean()), 1),
                t_stat=round(float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))), 2) if len(x) > 1 else None,
                win_rate=round(float((x > 0).mean()), 3), profit_factor=round(float(wins / losses), 3) if losses > 0 else None,
                gross_pts_mean=round(float(g.mean()), 2), cost_per_trade=round(float((g * CFG["lot"] - x).mean()), 1),
                worst_week=round(float(wk.min()), 0), positive_weeks=round(float((wk > 0).mean()), 3), weeks=int(len(wk)),
                mfe_mean=round(float(tr.mfe.mean()), 1), mae_mean=round(float(tr.mae.mean()), 1),
                exits={k: int(v) for k, v in tr.exit_reason.value_counts().items()})


def controls(b, tr, cut, cfg=CFG):
    """Direction control (same bars, random side) and timing control (random bar of the same session, same side, same stop in ATR)."""
    if not len(tr): return {}
    rng = np.random.default_rng(cfg["seed"])
    A, sb, t, d = b.atr14.to_numpy(), b.session_bar.to_numpy(), b.t.to_numpy(), b.date.astype(str).to_numpy()
    sess_bars = {}
    for i in range(len(b)):
        if sb[i] >= 1 and t[i][11:16] < cfg["square_off"] and not np.isnan(A[i]): sess_bars.setdefault(d[i], []).append(i)
    real = tr.net.mean()
    # pre-simulate both sides at the real bars (direction control draws from these)
    both = []
    for r in tr.itertuples():
        out = []
        for s in (+1, -1):
            j, px, why, _, _ = simulate(b, r.entry_i, s, r.stop_dist, cut, cfg)
            out.append(price(b.close.iat[r.entry_i], px, s, cfg)[0])
        both.append(out)
    both = np.array(both)
    dir_means = np.array([both[np.arange(len(both)), rng.integers(0, 2, len(both))].mean() for _ in range(cfg["draws"])])
    # timing control (amended 2026-10-03, PREREG.md "Amendment 1"): the same time of day (session_bar), the same side and the
    # same stop in ATR units, in a randomly drawn OTHER session of the same window. The first version drew a random bar of the
    # SAME session, which leaks the day's direction (the side is the break direction) into entries placed before the break.
    tim_means = []
    sides = np.where(tr.side.to_numpy() == "LONG", 1, -1); satr = tr.stop_atr.to_numpy()
    sbar = sb[tr.entry_i.to_numpy()]; days = np.array([d[i] for i in tr.entry_i])
    lo_d, hi_d = min(days), max(days)
    window_days = [x for x in sorted(sess_bars) if lo_d <= x <= hi_d]
    by_day_bar = {}
    for i in range(len(b)):
        if d[i] in sess_bars: by_day_bar[(d[i], sb[i])] = i
    cache = {}
    for _ in range(cfg["draws"]):
        tot, cnt = 0.0, 0
        for k in range(len(tr)):
            i = None
            for _try in range(20):
                dd = window_days[rng.integers(0, len(window_days))]
                if dd == days[k]: continue
                i = by_day_bar.get((dd, sbar[k]))
                if i is not None and not np.isnan(A[i]) and t[i][11:16] < cfg["square_off"]: break
                i = None
            if i is None: continue
            key = (i, sides[k], satr[k])
            if key not in cache:
                j, px, why, _, _ = simulate(b, i, sides[k], satr[k] * A[i], cut, cfg)
                cache[key] = price(b.close.iat[i], px, sides[k], cfg)[0]
            tot += cache[key]; cnt += 1
        tim_means.append(tot / max(cnt, 1))
    tim_means = np.array(tim_means)
    pct = lambda arr: round(float(100 * (np.mean(arr < real) + 0.5 * np.mean(arr == real))), 1)
    return dict(direction_control=dict(pct=pct(dir_means), mean=round(float(dir_means.mean()), 1), p95=round(float(np.quantile(dir_means, 0.95)), 1)),
                timing_control=dict(pct=pct(tim_means), mean=round(float(tim_means.mean()), 1), p95=round(float(np.quantile(tim_means, 0.95)), 1)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--trunc", action="store_true"); a = ap.parse_args()
    if a.trunc:
        out = {}
        for tf in ("5minute", "minute"):
            full = levels_and_breaks(load(tf), tf); part = levels_and_breaks(load(tf, CUT), tf)
            f = full[full.t <= CUT].reset_index(drop=True)
            same = f.equals(part.reset_index(drop=True))
            out[tf] = dict(signals_before_cut=int(len(f)), truncated=int(len(part)), identical=bool(same))
            print(tf, out[tf], flush=True)
        json.dump(out, open(os.path.join(HERE, "trunc_check.json"), "w"), indent=1)
        return
    res = dict(config=CFG, prereg="PREREG.md", timeframes={})
    for tf in ("5minute", "minute"):
        b = load(tf); cut = session_cutoffs(b, CFG["square_off"])
        sig = levels_and_breaks(b, tf)
        sig.to_csv(os.path.join(HERE, f"signals_{tf}.csv"), index=False)
        R = dict(levels_broken=int(len(sig)), with_pressure=int(sig.pressure.sum()) if len(sig) else 0, variants={})
        for v in ("A", "B"):
            tr = run_trades(b, sig, cut, v)
            tr.to_csv(os.path.join(HERE, f"trades_{tf}_{v}.csv"), index=False)
            V = {}
            for win, m in (("IS", tr.entry_time < OOS_FROM), ("2026", tr.entry_time >= OOS_FROM)):
                sub = tr[m].reset_index(drop=True)
                V[win] = dict(stats=stats(sub), **controls(b, sub, cut))
                print(tf, v, win, json.dumps(V[win]), flush=True)
            for side in ("LONG", "SHORT"):
                V[f"IS_{side}"] = stats(tr[(tr.entry_time < OOS_FROM) & (tr.side == side)])
            R["variants"][v] = V
        res["timeframes"][tf] = R
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    print("written results.json")


if __name__ == "__main__":
    main()
