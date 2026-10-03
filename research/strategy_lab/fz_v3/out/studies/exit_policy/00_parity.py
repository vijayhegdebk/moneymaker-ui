"""Parity checks kept in the folder (run before any learner): the study's own arithmetic against the lab's.
  1. price_np == lab.price_trade bit for bit on 500 random (trade, exit bar) pairs per timeframe and on every L1 exit (== l1_net_inr)
  2. the numba Foundation-stop floor == the L1 label: stop_loss exits at the same bar and price; eod / expiry exits reach the cap
     with no stop; next_choch exits have the stop strictly later than the CHoCH bar
  3. the numba floor == lab.manage with the Foundation stop (exact_R), 1 lot, no targets, no trail, square_off 15:25: same exit bar,
     price and reason on EVERY IS trade (the learner A / B trajectories end where the lab's stop would end them)
  4. exact_R: how many trades get a stop distance whose lab stop equals the Foundation stop bit for bit
Writes parity.json."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import exlib as X, lab

out = {}
for tf in ("5minute", "minute"):
    t0 = time.time()
    D = X.Data(tf)
    rep = dict(units_is=int(D.n), bars=int(D.nb))
    # 1. pricing
    rng = X.rng_of(f"parity|{tf}")
    js = rng.integers(0, D.n, 500); ks = np.array([rng.integers(D.entry[j] + 1, D.J_cap[j] + 1) for j in js])
    mine = X.price_np(D.e[js], D.c[ks], D.sg[js], 1)
    st = X.st_of(X.position(1, 50, [], None))
    theirs = np.array([lab.price_trade(st, X.CS, dict(position="LONG" if D.sg[j] > 0 else "SHORT", entry_px=float(D.e[j]), exit_px=float(D.c[k]), lots=1))["net"]
                       for j, k in zip(js, ks)])
    rep["price_np_vs_lab_price_trade_500_pairs_identical"] = bool(np.array_equal(mine, theirs))
    rep["price_np_vs_lab_max_abs_diff"] = float(np.max(np.abs(mine - theirs)))
    l1 = X.price_np(D.e, D.l1_px, D.sg, 1)
    rep["price_np_vs_l1_net_inr_max_abs_diff"] = float(np.max(np.abs(np.round(l1, 2) - D.fnd_net)))
    rep["price_np_vs_l1_net_inr_all_within_0.005"] = bool(np.all(np.abs(np.round(l1, 2) - D.fnd_net) <= 0.005))
    # 2. the floor vs the L1 label
    J, hit, fill = X.floor(D)
    sl_ = D.l1_reason == "stop_loss"
    rep["l1_stop_loss_n"] = int(sl_.sum())
    rep["floor_matches_l1_stop_bar_and_px"] = bool(np.all(hit[sl_]) and np.array_equal(J[sl_], D.fnd_exit[sl_]) and np.array_equal(fill[sl_], D.l1_px[sl_]))
    cap_ = np.isin(D.l1_reason, ["eod", "expiry"])
    rep["l1_cap_exits_n"] = int(cap_.sum())
    rep["floor_no_stop_and_cap_on_l1_cap_exits"] = bool((~hit[cap_]).all() and np.array_equal(J[cap_], D.fnd_exit[cap_]) and np.array_equal(fill[cap_], D.l1_px[cap_]))
    ch_ = D.l1_reason == "next_choch"
    rep["l1_next_choch_n"] = int(ch_.sum())
    # the stop must not fire at or before the CHoCH bar (the engine checks the stop first on that candle); the floor may end
    # on the CHoCH bar only when that bar is the cap (15:25 / contract end) and no stop fired
    later = J[ch_] > D.fnd_exit[ch_]; same_cap = (J[ch_] == D.fnd_exit[ch_]) & ~hit[ch_] & (D.fnd_exit[ch_] == D.J_cap[ch_])
    rep["floor_after_choch_or_choch_on_cap_bar_on_l1_choch_exits"] = bool((later | same_cap).all())
    rep["l1_choch_exits_on_the_cap_bar"] = int(same_cap.sum())
    rep["floor_stop_hit_share"] = round(float(hit.mean()), 4)
    rep["states_total"] = int((J - D.entry).sum()); rep["states_mean_per_trade"] = round(float((J - D.entry).mean()), 1)
    # 3. the floor vs lab.manage with the Foundation stop
    exact = 0; mism = []
    for j in range(D.n):
        R, ok = X.exact_R(float(D.e[j]), float(D.sl[j]), int(D.sg[j])); exact += ok
        st = X.st_of(X.position(1, R, [], None))
        cap, exp = D.cap_time(j)
        trs = lab.manage(st, D.rec(j), D.tl, D.ol, D.hl, D.ll, D.cl, cap, exp)
        assert len(trs) == 1
        tr = trs[0]; k = D.tix[tr["exit_time"]]
        reason_ok = (tr["exit_reason"] == "stop_loss") == bool(hit[j]) and (hit[j] or tr["exit_reason"] in ("eod", "expiry"))
        if not (k == J[j] and tr["exit_px"] == fill[j] and reason_ok):
            mism.append(dict(j=int(j), lab_bar=int(k), lab_px=tr["exit_px"], lab_reason=tr["exit_reason"], floor_bar=int(J[j]), floor_px=float(fill[j]), floor_hit=bool(hit[j])))
    rep["exact_R_trades"] = int(exact); rep["exact_R_failed"] = int(D.n - exact)
    rep["floor_vs_lab_manage_foundation_stop_mismatches"] = len(mism); rep["floor_vs_lab_manage_examples"] = mism[:10]
    rep["seconds"] = round(time.time() - t0, 1)
    out[tf] = rep
    print(tf, json.dumps(rep, indent=1), flush=True)
json.dump(out, open(os.path.join(HERE, "parity.json"), "w"), indent=1)
