"""Probe: lab.manage cost per call, extended-trajectory state counts, and the stop-fill parity of a plain loop vs the L1 label."""
import sys, os, time, json, bisect
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT); import harness as H; import lab
import numpy as np, pandas as pd
for tf in ("5minute", "minute"):
    t0 = time.time()
    B = pd.read_parquet(os.path.join(H.DATA, tf, "bars.parquet"))
    T = H.load(tf)
    tl, ol, hl, ll, cl = (B[c].tolist() for c in ("datetime", "open", "high", "low", "close"))
    print(tf, "bars", len(tl), "units", T.n, "IS", T.is_mask.sum(), f"load {time.time()-t0:.1f}s")
    is_idx = np.flatnonzero(T.is_mask)
    # eod bar per trade and state count
    day = B.date.to_numpy(); first = B.groupby("session_idx").i.min().to_numpy(); last = B.groupby("session_idx").i.max().to_numpy()
    hhmm = B.datetime.str.slice(11, 16).to_numpy()
    sess = B.session_idx.to_numpy()
    eod = np.empty(T.n, dtype=int)
    for j, i in enumerate(T.setup_i):
        s = sess[i]; lo, hi = first[s], last[s]
        k = hi
        while hhmm[k] > "15:25" and k > lo: k -= 1
        eod[j] = k
    ext = eod - T.setup_i
    print("  extended bars to 15:25 (no stop): total", ext[is_idx].sum(), "mean", ext[is_idx].mean().round(1), "max", ext.max())
    print("  L1 bars held mean", T.F.l1_bars_held[T.is_mask].mean().round(1))
    # lab.manage timing on 50 trades, stop 50 with ladder and trail
    st = dict(lot_size=65, slippage_pts=5.0, position_json=json.dumps(dict(lots=3, lock="none", exit="position", stop={"futures_pts": 50, "option_pct": 5},
                                                                          scale_out=[{"lots": 1, "target_r": 1}, {"lots": 1, "target_r": 2}], trail={"start_r": 3, "lag_r": 1},
                                                                          square_off="15:25", reverse=None), sort_keys=True))
    contract = B.contract.to_numpy(); expiry = B.expiry.to_numpy()
    clast = {}
    for i in range(len(tl)): clast[contract[i]] = i
    t1 = time.time(); nb = 0
    for j in is_idx[:200]:
        i = int(T.setup_i[j]); c = contract[i]
        cap = tl[clast[c]] if clast[c] < len(tl) - 1 else tl[-1]
        rec = dict(position="LONG" if T.up[j] else "SHORT", kind="FUT", entry_time=tl[i], entry_px=cl[i], dir="up" if T.up[j] else "down", exit_time=tl[i], exit_reason="open", open=True, exit_px=None)
        trs = lab.manage(st, rec, tl, ol, hl, ll, cl, cap, expiry[i])
        for tr in trs: lab.price_trade(st, H.CS, tr)
        nb += ext[j]
    dt = time.time() - t1
    print(f"  lab.manage x200: {dt:.2f}s -> {dt/200*1000:.2f} ms/call, {nb} bars walked -> {dt/nb*1e6:.1f} us/bar")
