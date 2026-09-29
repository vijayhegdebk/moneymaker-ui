"""Learner C: the parametric exit grid priced by exact lab.manage replay on every IS entry (both timeframes).

Grid (never shrunk): stop in {35, 50, 75 pts, foundation (features.sl via exact_R)} x scale_out in {none, 1R, 2R, 3R, 4R (1 lot:
the target IS the exit), ladder 1R/2R, ladder 2R/4R (3 lots, the rest trails / holds)} x trail in {none, (2,1), (2,2), (3,1), (3,2),
(4,1), (4,2)} x time stop in {none, 30, 60, 120 bars} x exit-on-CHoCH-against {off, on}; square_off 15:25 always.
= 196 lab.manage positions x 8 post-processing cuts = 1,568 variants per timeframe.

Every variant is priced exactly as the lab would price ST13/ST14: a strategy-row dict st (lot_size 65, slippage_pts 5,
position_json), rec as rl.setups builds it, cap = the contract's last candle (rl.contract_end), charges ZERODHA_NFO_FUT.
The time stop and CHoCH-against exits are a cut of lab.manage's tranches (exlib docstring: cut convention), re-priced with
lab.price_trade. Output: c_grid_<tf>.npz (per trade x variant: position net, last exit bar, last exit reason), c_variants.json,
c_grid_check_<tf>.json (the Foundation-stop-only variant reproduces the L1 label on its stop / cap exits)."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, psutil
import exlib as X, lab
import multiprocessing as mp

STOPS = [35, 50, 75, "foundation"]
SCALE = {"none": (1, []), "t1": (1, [{"lots": 1, "target_r": 1}]), "t2": (1, [{"lots": 1, "target_r": 2}]), "t3": (1, [{"lots": 1, "target_r": 3}]),
         "t4": (1, [{"lots": 1, "target_r": 4}]), "L12": (3, [{"lots": 1, "target_r": 1}, {"lots": 1, "target_r": 2}]),
         "L24": (3, [{"lots": 1, "target_r": 2}, {"lots": 1, "target_r": 4}])}
TRAILS = {"none": None, "2_1": {"start_r": 2, "lag_r": 1}, "2_2": {"start_r": 2, "lag_r": 2}, "3_1": {"start_r": 3, "lag_r": 1},
          "3_2": {"start_r": 3, "lag_r": 2}, "4_1": {"start_r": 4, "lag_r": 1}, "4_2": {"start_r": 4, "lag_r": 2}}
TIME_STOPS = [None, 30, 60, 120]
CHOCH = [False, True]
REASONS = {"stop_loss": 0, "trail_stop": 1, "target": 2, "eod": 3, "expiry": 4, "time_stop": 5, "choch_against": 6, "open": 7}

BASE = [(s, sc, tr) for s in STOPS for sc in SCALE for tr in TRAILS]
CUTS = [(ts, ch) for ts in TIME_STOPS for ch in CHOCH]


def variant_config(s, sc, tr, ts, ch):
    lots, so = SCALE[sc]
    return dict(stop=({"futures_pts": s, "option_pct": 5} if s != "foundation" else {"futures": "foundation_sl", "option_pct": 5}), lots=lots,
                scale_out=so, trail=TRAILS[tr], square_off=X.SQUARE_OFF, time_stop_bars=ts, exit_on_choch_against=ch,
                keys=dict(stop=s, scale=sc, trail=tr, time_stop=ts, choch=ch))


VARIANTS = [variant_config(s, sc, tr, ts, ch) for (s, sc, tr) in BASE for (ts, ch) in CUTS]
assert len(VARIANTS) == 1568
# the lab must accept every position block (lab.position_of validation, stop 50 as a stand-in for the per-trade Foundation R)
for (s, sc, tr) in BASE:
    lots, so = SCALE[sc]
    lab.position_of({"position": X.position(lots, 50 if s == "foundation" else s, so, TRAILS[tr])})

D = None


def work(js):
    n, nv = len(js), len(VARIANTS)
    net = np.empty((n, nv)); xbar = np.empty((n, nv), dtype=np.int32); reason = np.empty((n, nv), dtype=np.int8)
    for a, j in enumerate(js):
        rec = D.rec(j); cap, exp = D.cap_time(j)
        e, sg, sl = float(D.e[j]), int(D.sg[j]), float(D.sl[j])
        Rf, _ = X.exact_R(e, sl, sg)
        k0 = int(D.entry[j]); Jc = int(D.J_cap[j]); ca = int(D.choch_against[j])
        col = 0
        for (s, sc, tr) in BASE:
            lots, so = SCALE[sc]
            st = X.st_of(X.position(lots, Rf if s == "foundation" else s, so, TRAILS[tr]))
            trs = lab.manage(st, rec, D.tl, D.ol, D.hl, D.ll, D.cl, cap, exp)
            for t_ in trs:
                assert not t_["open"], (j, s, sc, tr, t_)
                lab.price_trade(st, X.CS, t_)
            bars = [D.tix[t_["exit_time"]] for t_ in trs]
            for (ts, ch) in CUTS:
                cut = None
                if ts is not None and k0 + ts <= Jc: cut = k0 + ts
                if ch and 0 <= ca <= Jc: cut = ca if cut is None else min(cut, ca)
                tot = 0.0; last_bar = -1; last_reason = None
                for t_, kb in zip(trs, bars):
                    if cut is not None and kb > cut:
                        why = "time_stop" if (ts is not None and cut == k0 + ts and not (ch and cut == ca)) else "choch_against"
                        if ts is not None and ch and cut == k0 + ts and cut == ca: why = "time_stop"          # the same bar: label it a time stop
                        t2 = lab.price_trade(st, X.CS, dict(t_, exit_time=D.tl[cut], exit_px=D.cl[cut], exit_reason=why, open=False))
                        nt, kb2, rs = t2["net"], cut, why
                    else:
                        nt, kb2, rs = t_["net"], kb, t_["exit_reason"]
                    tot += nt
                    if kb2 >= last_bar: last_bar, last_reason = kb2, rs
                net[a, col] = tot; xbar[a, col] = last_bar
                reason[a, col] = REASONS["target" if last_reason.startswith("target") else last_reason]
                col += 1
    return net, xbar, reason


if __name__ == "__main__":
    tfs = sys.argv[1:] or ["5minute", "minute"]
    json.dump(VARIANTS, open(os.path.join(HERE, "c_variants.json"), "w"), indent=0)
    for tf in tfs:
        t0 = time.time()
        D = X.Data(tf)
        print(f"{tf}: {D.n} IS units, {len(VARIANTS)} variants, rss {psutil.Process().memory_info().rss / 1e6:.0f} MB", flush=True)
        chunks = np.array_split(np.arange(D.n), 32)
        with mp.get_context("fork").Pool(4) as pool:
            parts = pool.map(work, chunks)
        net = np.vstack([p[0] for p in parts]); xbar = np.vstack([p[1] for p in parts]); reason = np.vstack([p[2] for p in parts])
        lots = np.array([v["lots"] for v in VARIANTS])
        np.savez_compressed(os.path.join(HERE, f"c_grid_{tf}.npz"), net_pos=net, exit_bar=xbar, reason=reason, lots=lots, entry=D.entry, fnd_net=D.fnd_net)
        # check: the Foundation-stop-only variant (no target / trail / cut) reproduces the L1 label on its stop-loss and cap exits
        vi = next(i for i, v in enumerate(VARIANTS) if v["keys"] == dict(stop="foundation", scale="none", trail="none", time_stop=None, choch=False))
        m = np.isin(D.l1_reason, ["stop_loss", "eod", "expiry"])
        chk = dict(variant=vi, l1_stop_or_cap_exits=int(m.sum()),
                   net_matches_l1_within_0_005=bool(np.all(np.abs(np.round(net[m, vi], 2) - D.fnd_net[m]) <= 0.005)),
                   exit_bar_matches_l1=bool(np.array_equal(xbar[m, vi], D.fnd_exit[m])),
                   l1_next_choch_exits=int((~m).sum()), variant_later_than_choch_on_those=bool((xbar[~m, vi] >= D.fnd_exit[~m]).all()),
                   seconds=round(time.time() - t0, 1), rss_mb=round(psutil.Process().memory_info().rss / 1e6))
        json.dump(chk, open(os.path.join(HERE, f"c_grid_check_{tf}.json"), "w"), indent=1)
        print(tf, json.dumps(chk), flush=True)
        st9 = next(i for i, v in enumerate(VARIANTS) if v["keys"] == dict(stop=50, scale="L12", trail="3_1", time_stop=None, choch=False))
        print(f"{tf}: Foundation L1 mean {D.fnd_net.mean():.1f}; ST9 ladder per position {net[:, st9].mean():.1f} per lot {net[:, st9].mean() / 3:.1f}; "
              f"best per-lot variant in-sample {(net / lots).mean(axis=0).max():.1f}", flush=True)
