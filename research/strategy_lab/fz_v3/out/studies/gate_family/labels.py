"""gate_family labels: L2 (symmetric triple barrier, 1x and 2x the stop distance) and L3 (trend scanning) for every L1 unit, from
bars.parquet with the engine's same-bar conventions. Robustness labels only (never candidates). Definitions in gf_lib's docstring.

    python labels.py --tf 5minute      # -> results/labels_<tf>.parquet, results/labels_<tf>.json (checks)

L2: entry = close[k]; lower barrier = the Foundation stop `sl` (features.parquet); upper = entry + sg x m x |entry - sl|, m in {1, 2};
vertical = the entry session's square-off bar (the last bar opening at or before 15:25, build.py eod_bar) capped at the contract's
last candle. Bars k+1 .. vertical in order: on a session's first candle (never inside a session: stated for completeness) a touched
level fills at the close; else the stop is checked first (open beyond the stop -> fill at the open, wick touch -> fill at the stop),
then the target (open beyond -> the open, wick touch -> the target); no touch -> the vertical bar's close ('eod'). Priced as build.py
price(): 5 pts slippage per side, lot 65, lab.trade_charges(ZERODHA_NFO_FUT) on the slipped prices.
L3: for h = 5..60, y = close[k+1 .. k+h] restricted to the entry session (at least 5 bars, else the horizon is not available), x =
0..len-1: OLS slope t = b / se(b); h* = argmax |t|; net_L3 = sg x t(h*) (dimensionless: positive = the price trended in the trade's
direction), exit bar = k + len(h*) (for purging), win = net_L3 > 0. A unit with fewer than 5 same-session bars after k has l3_nbars < 5
and net 0 (weight 0 downstream).
Check: with m -> infinity L2 is the L1 stop-or-eod trajectory; the script asserts that every L1 stop exit before the target touch is
reproduced bar-for-bar and price-for-price by the L2 stop leg (L1 exits by next_choch are outside L2 by design).
"""
import os, sys, json, time, argparse, bisect
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H   # noqa: E402
import lab            # noqa: E402  trade_charges (read-only)

SQUARE_OFF = "15:25"


def price(entry_close, exit_px, up):
    if up: buy, sell = entry_close + H.SLIP, exit_px - H.SLIP
    else: sell, buy = entry_close - H.SLIP, exit_px + H.SLIP
    chg = lab.trade_charges(H.CS, buy, sell, H.LOT)["total"]
    gross = (sell - buy) * H.LOT
    return round(gross - chg, 2)


def build(tf):
    t0 = time.time()
    T = H.load(tf)
    B = pd.read_parquet(os.path.join(H.DATA, tf, "bars.parquet"))
    S = pd.read_parquet(os.path.join(H.DATA, tf, "sessions.parquet"))
    t = B.datetime.astype(str).to_numpy(); o, h, l, c = (B[x].to_numpy(dtype=float) for x in ("open", "high", "low", "close"))
    sess = B.session_idx.to_numpy(); sbar = B.session_bar.to_numpy(); contract = B.contract.astype(str).to_numpy()
    last_bar = dict(zip(S.session_idx, S.last_bar))
    contract_last = {}
    for i in range(len(B)): contract_last[contract[i]] = i
    tl = list(t)

    def eod_bar(k):
        day = t[k][:10]; e = f"{day} {SQUARE_OFF}:00"
        j = bisect.bisect_right(tl, e) - 1
        return j if (j >= 0 and t[j][:10] == day and j >= k) else None

    sl = T.F.sl.to_numpy(dtype=float); setup = T.setup_i; up = T.up
    l1_reason = T.F.l1_exit_reason.astype(str).to_numpy(); l1_exit = T.F.l1_exit_i.to_numpy(dtype=float)
    rows = []; chk = dict(l1_stop_exits=0, l2_reproduces_l1_stop=0, l2_stop_mismatch=[], no_bars=0)
    for i in range(T.n):
        k = int(setup[i]); sg = 1 if up[i] else -1; e = c[k]; s_ = sl[i]; d = abs(e - s_)
        j_eod = eod_bar(k); cap = contract_last[contract[k]]
        vert = min(j_eod if j_eod is not None else k, cap)
        rec = dict(setup_i=k)
        for m in (1, 2):
            U = e + sg * m * d
            xi, px, reason = vert, c[vert], "eod"
            if vert <= k: chk["no_bars"] += 1
            for j in range(k + 1, vert + 1):
                first = t[j][:10] != t[j - 1][:10]
                gap_s = (o[j] <= s_) if up[i] else (o[j] >= s_)
                hit_s = (l[j] <= s_) if up[i] else (h[j] >= s_)
                if gap_s or hit_s:
                    xi, reason = j, "stop"; px = c[j] if first else (o[j] if gap_s else s_); break
                gap_t = (o[j] >= U) if up[i] else (o[j] <= U)
                hit_t = (h[j] >= U) if up[i] else (l[j] <= U)
                if gap_t or hit_t:
                    xi, reason = j, "target"; px = c[j] if first else (o[j] if gap_t else U); break
            net = price(e, px, bool(up[i]))
            rec.update({f"l2m{m}_exit_i": xi, f"l2m{m}_exit_px": px, f"l2m{m}_reason": reason, f"l2m{m}_pts": round(sg * (px - e), 2),
                        f"l2m{m}_net": net, f"l2m{m}_win": net > 0})
            if m == 1 and l1_reason[i] == "stop_loss":
                chk["l1_stop_exits"] += 1
                if reason == "stop" and xi == int(l1_exit[i]) and abs(px - float(T.F.l1_exit_px.iloc[i])) < 1e-9: chk["l2_reproduces_l1_stop"] += 1
                elif reason == "stop": chk["l2_stop_mismatch"].append(dict(setup_i=k, l2_bar=xi, l1_bar=int(l1_exit[i])))
        # L3 trend scanning
        s_last = int(last_bar[int(sess[k])]); best = None
        for hz in range(5, 61):
            end = min(k + hz, s_last)
            y = c[k + 1:end + 1]; n = len(y)
            if n < 5: break
            x = np.arange(n, dtype=float); xm = x - x.mean(); ym = y - y.mean()
            sxx = float((xm * xm).sum()); b = float((xm * ym).sum() / sxx); resid = ym - b * xm
            s2 = float((resid * resid).sum() / (n - 2)); se = np.sqrt(s2 / sxx) if s2 > 0 else 1e-12
            tv = b / se
            if best is None or abs(tv) > abs(best[0]): best = (tv, hz, n)
            if end == s_last: break
        if best is None: rec.update(l3_t=np.nan, l3_h=0, l3_nbars=0, l3_exit_i=k, l3_net=0.0, l3_win=False)
        else:
            tv, hz, n = best
            rec.update(l3_t=round(float(tv), 4), l3_h=hz, l3_nbars=n, l3_exit_i=k + n, l3_net=round(float(sg * tv), 4), l3_win=sg * tv > 0)
        rows.append(rec)
    L = pd.DataFrame(rows)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    L.to_parquet(os.path.join(HERE, "results", f"labels_{tf}.parquet"), index=False)
    is_ = T.is_mask
    summ = dict(tf=tf, units=int(T.n), is_units=int(is_.sum()), seconds=round(time.time() - t0, 1), checks=chk,
                l1_is_mean=round(float(T.net[is_].mean()), 2), l1_is_win_rate=round(float(T.win[is_].mean()), 4))
    for m in (1, 2):
        summ[f"L2x{m}"] = dict(is_mean=round(float(L[f"l2m{m}_net"][is_].mean()), 2), is_win_rate=round(float(L[f"l2m{m}_win"][is_].mean()), 4),
                               reasons=L[f"l2m{m}_reason"][is_].value_counts().to_dict())
    summ["L3"] = dict(is_mean_t=round(float(L.l3_net[is_].mean()), 4), is_share_positive=round(float((L.l3_net[is_] > 0).mean()), 4),
                      is_nbars_lt5=int((L.l3_nbars[is_] < 5).sum()), h_star_median=float(L.l3_h[is_].median()))
    chk["l2_stop_mismatch_n"] = len(chk["l2_stop_mismatch"]); chk["l2_stop_mismatch"] = chk["l2_stop_mismatch"][:10]
    json.dump(summ, open(os.path.join(HERE, "results", f"labels_{tf}.json"), "w"), indent=1, default=str)
    print(json.dumps(summ, default=str))
    return L, summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); a = ap.parse_args()
    build(a.tf)
