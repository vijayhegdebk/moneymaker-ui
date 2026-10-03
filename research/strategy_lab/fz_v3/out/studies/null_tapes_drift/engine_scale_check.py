"""Two facts the null tapes rely on, measured (study null_tapes_drift; 5-minute IS full sessions, engine.run with the Strategy 2 rules):

  1. the engine is scale-free: the same bars at 2x the price level give identical swing / CHoCH / BOS / SETUP counts, so the tapes'
     random-walk price level cannot change the engine's behaviour (INR statistics still scale with the level; see FINDINGS caveats);
  2. what the session bootstrap changes: the CHoCH / SETUP rate of the real IS sessions in their real order, re-based with the real
     gaps (identical to the real tape), with random gaps, in shuffled order with the real gap sequence, shuffled with zero gaps, and
     in real order with zero gaps. The engine's event rate depends on the multi-day path, which is what a null tape randomises.

    python engine_scale_check.py     -> engine_scale_check.json
"""
import os, sys, json, time
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, LAB)
import gen_tapes as G, engine                                            # noqa: E402

RULES = dict(break_mode="touch", choch_mode="touch", avwap_weight="volume", sl_rule="choch_candle")


def counts(O, H, L, C, V):
    P, n = O.shape
    bars = dict(t=[f"{s:05d} {k:03d}" for s in range(P) for k in range(n)], o=O.ravel().tolist(), h=H.ravel().tolist(), l=L.ravel().tolist(),
                c=C.ravel().tolist(), v=V.ravel().tolist())
    r = engine.run(bars, RULES)
    ch = sum(1 for e in r["events"] if e["kind"] == "CHoCH")
    return dict(sessions=P, choch=ch, bos=len(r["events"]) - ch, setups=len(r["setups"]), swings=len(r["sw"]),
                choch_per_session=round(ch / P, 4), bos_per_session=round((len(r["events"]) - ch) / P, 4), setups_per_session=round(len(r["setups"]) / P, 4))


def chain(fit, order, gaps):
    O, H, L, C, V = (fit[k] for k in "OHLCV")
    o = np.empty_like(O); h = np.empty_like(O); l = np.empty_like(O); c = np.empty_like(O); v = np.empty_like(O); level = O[order[0], 0]
    for s, j in enumerate(order):
        lo = level * np.exp(gaps[s]) if s else level
        for dst, src in ((o, O), (h, H), (l, L), (c, C)): dst[s] = src[j] / O[j, 0] * lo
        v[s] = V[j]; level = c[s, -1]
    return o, h, l, c, v


def main():
    t0 = time.time()
    fit = G.fit_generators("5minute", verbose=False)
    O, H, L, C, V = (fit[k] for k in "OHLCV"); P = O.shape[0]
    rng = np.random.default_rng(0)
    real_gaps = np.r_[0.0, np.log(O[1:, 0] / C[:-1, -1])]
    out = dict(tf="5minute", rules=RULES, pool="IS full sessions (75 bars)", sessions=int(P), runs={})
    out["runs"]["real_order"] = counts(O, H, L, C, V)
    out["runs"]["real_order_x2_price"] = counts(2 * O, 2 * H, 2 * L, 2 * C, V)
    out["runs"]["real_order_rebased_real_gaps"] = counts(*chain(fit, np.arange(P), real_gaps))
    out["runs"]["real_order_random_gaps"] = counts(*chain(fit, np.arange(P), rng.choice(fit["gaps"], P)))
    out["runs"]["shuffled_sessions_real_gap_sequence"] = counts(*chain(fit, rng.permutation(P), real_gaps))
    out["runs"]["shuffled_sessions_zero_gaps"] = counts(*chain(fit, rng.permutation(P), np.zeros(P)))
    out["runs"]["real_order_zero_gaps"] = counts(*chain(fit, np.arange(P), np.zeros(P)))
    out["scale_free"] = out["runs"]["real_order"] == out["runs"]["real_order_x2_price"]
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "engine_scale_check.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
