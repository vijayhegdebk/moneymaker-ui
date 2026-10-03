"""1-hour swing direction -> one 1-minute trade that way -> one reverse trade if it is stopped out (PREREG.md fixes every rule).

    python htf_swing_reverse.py           # results.json, trades_<E1|E2>.csv, run.log
    python htf_swing_reverse.py --trunc   # look-ahead check on bars cut at 2025-06-30 12:00
"""
import os, sys, json, math, argparse
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, LAB)
import lab, engine  # noqa: E402

DATA = os.path.join(LAB, "fz_v3", "out", "data", "minute")
TRUNC = os.path.join(DATA, "trunc_20250630_120000")
CUT = "2025-06-30 12:00:00"
OOS_FROM = "2026-01-01"
CFG = dict(target_r=2.0, square_off="15:25", e2_time="09:20", lot=65, slippage_pts=5.0, draws=1000, seed=20261003)
ENGINE_P = dict(break_mode="touch", choch_mode="touch", avwap_weight="volume", sl_rule="prev_swing", entry_rule="setup_v1", exit_rule="next_choch")
CHARGES = json.load(open(os.path.join(LAB, "config", "charges.json")))["ZERODHA_NFO_FUT"]


def load(folder):
    b = pd.read_parquet(os.path.join(folder, "bars.parquet")); b["t"] = b["datetime"].astype(str)
    return b, pd.read_parquet(os.path.join(folder, "trades.parquet")), pd.read_parquet(os.path.join(folder, "swings.parquet"))


# ---------------------------------------------------------------- 1-hour bars, 1-hour swings, direction per 1-minute bar
def hour_direction(b):
    """dir1h[i] = +1 / -1 / 0 for every 1-minute bar i: the current 1-hour swing leg as known at the close of bar i."""
    mins = b.t.str[11:13].astype(int) * 60 + b.t.str[14:16].astype(int) - (9 * 60 + 15)
    hour_key = b.date.astype(str) + "_" + (mins // 60).astype(str)
    g = b.groupby(hour_key, sort=False)
    hb = pd.DataFrame(dict(t=g.t.first(), o=g.open.first(), h=g.high.max(), l=g.low.min(), c=g.close.last(), v=g.volume.sum(),
                           last_i=g.i.last())).reset_index(drop=True)
    hb = hb.sort_values("last_i").reset_index(drop=True)
    res = engine.run({k: hb[k].tolist() for k in "tohlcv"}, ENGINE_P)
    known = np.full(len(b), 0)
    # a swing confirmed on hour bar `conf` is known from the close of that hour's last 1-minute bar
    ev = sorted((int(hb.last_i.iat[s["conf"]]), +1 if s["k"] == "L" else -1) for s in res["sw"])
    cur, p = 0, 0
    idx = b.i.to_numpy()
    for r in range(len(b)):
        while p < len(ev) and ev[p][0] <= idx[r]:
            cur = ev[p][1]; p += 1
        known[r] = cur
    sw1h = sorted((int(hb.last_i.iat[s["conf"]]), s["k"], float(s["p"])) for s in res["sw"])
    return known, hb, sw1h


# ---------------------------------------------------------------- trade mechanics (lab conventions)
def price(entry, exit_, side):
    slip, lot = CFG["slippage_pts"], CFG["lot"]
    buy, sell = (entry + slip, exit_ - slip) if side > 0 else (exit_ + slip, entry - slip)
    return (sell - buy) * lot - lab.trade_charges(CHARGES, buy, sell, lot)["total"]


def run_leg(O, H, L, C, first_bar_of_session, i, entry, side, stop, end):
    """From bar i+1 to end: stop (gap -> open; session's first bar -> close), else target 2R, else close at end."""
    R = abs(entry - stop); tgt = entry + side * CFG["target_r"] * R
    for j in range(i + 1, end + 1):
        gap = O[j] <= stop if side > 0 else O[j] >= stop
        hit = L[j] <= stop if side > 0 else H[j] >= stop
        if gap or hit:
            px = C[j] if first_bar_of_session[j] else (O[j] if gap else stop)
            return j, px, "stop"
        if (side > 0 and H[j] >= tgt) or (side < 0 and L[j] <= tgt):
            return j, tgt, "target"
    return end, C[end], "eod"


_CACHE = {}


def build(b, trades, swings, variant, dir_override=None, stop_mode="1m"):
    """One cycle per session. dir_override: {date: side} replaces the 1-hour direction (direction control).
    stop_mode "1m": the 1-minute stop of PREREG.md; "1h" (Amendment 1, user 2026-10-03: "SL is of 1 hour and risk is 1R"):
    the latest confirmed 1-HOUR swing against the trade (long: last 1-hour swing low, short: last 1-hour swing high)."""
    key1h = ("1h", id(b), len(b))
    if key1h not in _CACHE: _CACHE[key1h] = hour_direction(b)
    d1h, _, sw1h = _CACHE[key1h]
    idx_all = b.i.to_numpy()
    h_lo = np.array([(k, p) for k, kind, p in sw1h if kind == "L"]); h_hi = np.array([(k, p) for k, kind, p in sw1h if kind == "H"])
    t, D = b.t.to_numpy(), b.date.astype(str).to_numpy()
    O, H, L, C = (b[k].to_numpy() for k in ("open", "high", "low", "close"))
    sb = b.session_bar.to_numpy()
    first_bar = sb == 0
    key = (id(b), len(b))
    if key not in _CACHE:
        cut = {}
        for i in range(len(b)):
            if t[i][11:16] <= CFG["square_off"]: cut[D[i]] = i
        _CACHE[key] = (cut, b.groupby("contract").i.max().to_dict())
    cut, last_k = _CACHE[key]; K = b.contract.to_numpy()
    # candidate entries per day
    cands = {}
    if variant == "E1":
        for r in trades.itertuples():
            if r.entry_i >= len(b) or pd.isna(r.sl): continue
            cands.setdefault(D[r.entry_i], []).append((int(r.entry_i), +1 if r.dir == "up" else -1, float(r.sl)))
    else:
        sw = swings.sort_values("conf_bar")
        swH = sw[sw.kind == "H"][["conf_bar", "price"]].to_numpy(); swL = sw[sw.kind == "L"][["conf_bar", "price"]].to_numpy()
        for i in np.flatnonzero(b.t.str[11:16].to_numpy() == CFG["e2_time"]):
            cands[D[i]] = [(int(i), 0, None)]
    rows = []
    for day in sorted(cands):
        for (i, sdir, sl) in sorted(cands[day]):
            if t[i][11:16] >= CFG["square_off"] or first_bar[i]: continue
            want = dir_override[day] if dir_override is not None else d1h[i]
            if want == 0: continue
            if variant == "E1" and sdir != want: continue
            if stop_mode == "1h":
                arr = h_lo if want > 0 else h_hi
                k = np.searchsorted(arr[:, 0], idx_all[i], side="right") - 1
                if k < 0: continue
                stop = float(arr[k, 1])
            elif variant == "E1":
                stop = sl
            else:
                arr = swL if want > 0 else swH
                k = np.searchsorted(arr[:, 0], i, side="right") - 1
                if k < 0: break
                stop = float(arr[k, 1])
            side, e = want, C[i]
            if (side > 0 and stop >= e) or (side < 0 and stop <= e):
                if stop_mode == "1h" and variant == "E1": continue             # 1-hour stop above a long entry: wait for the next agreeing SETUP
                break                                                           # stop on the wrong side: no trade that day
            end = min(cut.get(day, i), last_k[K[i]])
            j, px, why = run_leg(O, H, L, C, first_bar, i, e, side, stop, end)
            rows.append(dict(day=day, leg="first", side=side, entry_i=i, entry_time=t[i], entry_px=e, stop=stop, R=abs(e - stop),
                             exit_i=j, exit_time=t[j], exit_px=px, exit_reason=why, gross_pts=(px - e) * side, r_mult=(px - e) * side / abs(e - stop), net=price(e, px, side)))
            if why == "stop" and t[j][11:16] < CFG["square_off"] and j < end:
                R = abs(e - stop); s2 = -side; e2 = px; st2 = e2 - s2 * R
                j2, px2, why2 = run_leg(O, H, L, C, first_bar, j, e2, s2, st2, end)
                rows.append(dict(day=day, leg="reverse", side=s2, entry_i=j, entry_time=t[j], entry_px=e2, stop=st2, R=R,
                                 exit_i=j2, exit_time=t[j2], exit_px=px2, exit_reason=why2, gross_pts=(px2 - e2) * s2, r_mult=(px2 - e2) * s2 / R, net=price(e2, px2, s2)))
            break                                                               # one cycle per day
    return pd.DataFrame(rows)


def stats(tr):
    if not len(tr): return dict(n=0)
    x = tr.net.to_numpy()
    wk = tr.groupby(pd.to_datetime(tr.entry_time).dt.to_period("W")).net.sum()
    w, l = x[x > 0].sum(), -x[x <= 0].sum()
    return dict(n=int(len(x)), net_total=round(float(x.sum())), net_mean=round(float(x.mean()), 1),
                t_stat=round(float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))), 2) if len(x) > 1 else None,
                win_rate=round(float((x > 0).mean()), 3), profit_factor=round(float(w / l), 3) if l > 0 else None,
                gross_pts_mean=round(float(tr.gross_pts.mean()), 2), r_mean=round(float(tr.r_mult.mean()), 3) if "r_mult" in tr else None,
                stop_pts_median=round(float(tr.R.median()), 1), worst_week=round(float(wk.min())), positive_weeks=round(float((wk > 0).mean()), 3),
                exits={k: int(v) for k, v in tr.exit_reason.value_counts().items()})


def summarise(tr):
    out = {}
    for win, m in (("IS", tr.entry_time < OOS_FROM), ("2026", tr.entry_time >= OOS_FROM)):
        s = tr[m]
        days = s.day.nunique()
        out[win] = dict(cycle=dict(stats(s), days=int(days), net_per_day=round(float(s.net.sum() / days), 1) if days else None),
                        first=stats(s[s.leg == "first"]), reverse=stats(s[s.leg == "reverse"]),
                        first_stopped_share=round(float((s[s.leg == "first"].exit_reason == "stop").mean()), 3) if len(s) else None)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--trunc", action="store_true"); ap.add_argument("--stop", default="1m", choices=["1m", "1h"])
    a = ap.parse_args(); SM = a.stop; sfx = "" if SM == "1m" else "_1h"
    if a.trunc:
        bf, tf_, sf = load(DATA); bt, tt, st = load(TRUNC)
        out = {}
        for v in ("E1", "E2"):
            full = build(bf, tf_, sf, v, stop_mode=SM); part = build(bt, tt, st, v, stop_mode=SM)
            f = full[full.entry_time <= CUT].reset_index(drop=True)
            p = part[part.entry_time <= CUT].reset_index(drop=True)
            # trades still open at the cut end differently on the truncated bars: compare entries and directions
            same = f[["day", "leg", "side", "entry_i", "entry_px", "stop"]].equals(p[["day", "leg", "side", "entry_i", "entry_px", "stop"]])
            closed = f[f.exit_time < CUT].reset_index(drop=True); pc = p[p.exit_time < CUT].reset_index(drop=True)
            out[v] = dict(entries_before_cut=int(len(f)), truncated=int(len(p)), entries_identical=bool(same),
                          closed_trades_identical=bool(closed.equals(pc)))
            print(v, out[v], flush=True)
        json.dump(out, open(os.path.join(HERE, f"trunc_check{sfx}.json"), "w"), indent=1)
        return
    b, trades, swings = load(DATA)
    d1h, hb, sw = hour_direction(b)
    res = dict(prereg="PREREG.md", stop_mode=SM, config=CFG, hour_bars=int(len(hb)), hour_swings=int(len(sw)),
               share_up=round(float((d1h > 0).mean()), 3), variants={})
    rng = np.random.default_rng(CFG["seed"])
    days = sorted(set(b.date.astype(str)))
    for v in ("E1", "E2"):
        tr = build(b, trades, swings, v, stop_mode=SM)
        tr.to_csv(os.path.join(HERE, f"trades_{v}{sfx}.csv"), index=False)
        S = summarise(tr)
        # direction control: random first-trade direction per day, reverse logic as usual
        ctrl = {"IS": [], "2026": []}
        for _ in range(CFG["draws"]):
            over = {d: int(x) for d, x in zip(days, rng.choice([-1, 1], len(days)))}
            r = build(b, trades, swings, v, dir_override=over, stop_mode=SM)   # E1: a SETUP in the drawn direction
            for win, m in (("IS", r.entry_time < OOS_FROM), ("2026", r.entry_time >= OOS_FROM)):
                s = r[m]; ctrl[win].append(s.net.sum() / max(s.day.nunique(), 1))
        for win in ("IS", "2026"):
            arr = np.array(ctrl[win]); real = S[win]["cycle"]["net_per_day"]
            S[win]["direction_control"] = dict(pct=round(float(100 * (np.mean(arr < real) + 0.5 * np.mean(arr == real))), 1),
                                               mean=round(float(arr.mean()), 1), p95=round(float(np.quantile(arr, 0.95)), 1))
        res["variants"][v] = S
        print(v, json.dumps(S), flush=True)
        json.dump(res, open(os.path.join(HERE, f"results{sfx}.json"), "w"), indent=1, default=str)
    print("written results.json")


if __name__ == "__main__":
    main()
