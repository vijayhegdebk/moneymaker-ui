"""FZ v3 cloud data build (the authoritative one): Foundation + FZ v2 rooms + the per-SETUP feature table + the labels,
one timeframe per process, from the committed files under fz_v3/data/ read in full through engine.load.

    python build.py --tf minute      python build.py --tf 5minute      [--truncate "YYYY-MM-DD HH:MM:SS"]

Read-only on the repository (bytecode writing off; lab imported for trade_charges / atr_series only). Never lab.sessions()
(config/data.json history_from would drop 2021-2025). Outputs go to fz_v3/out/data/<tf>/ as parquet (+ meta.json), with one
column contract for both timeframes (README.md next to the files, written by this script).

Pre-registered (BRIEF.md): IS = sessions 2021-10-01 .. 2025-12-31, OOS = 2026-01-01 .. 2026-09-25. Unit = a Foundation SETUP
with its own engine trade. Costs: lot 65, 5 pts slippage per side, lab.trade_charges(ZERODHA_NFO_FUT) on the slipped prices.
Every feature at SETUP bar k uses bars <= k only; labels (fnd_*, l1_*, fwd_*, fzpos_*, fzpost_*) are never features.

Labels written here
  L0  the engine's own trade (fnd_*): stop / next CHoCH / open at the data end; holds may cross sessions and rolls.
  L1  the intraday book ST13/ST14 will trade (l1_*): the same trade cut at the entry session's square-off, as lab.eod_cut
      does with position.square_off "15:25": exit at the close of the last candle opening at or before 15:25 of the entry
      day when the engine exit lies later; a SETUP whose bar opens at or after 15:25 is not taken (l1_taken = 0, no trade).
      Also the contract cap (lab: a position still open at its contract's last candle closes there, 'expiry').
"""
import sys, os, json, csv, time, hashlib, bisect, datetime as D, statistics, types, argparse
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", "..", ".."))            # research/strategy_lab
sys.path.insert(0, LAB)
import numpy as np, pandas as pd
import engine, fz, fz_exec, lab                                          # noqa: E402
import psutil

ap = argparse.ArgumentParser()
ap.add_argument("--tf", required=True, choices=("minute", "5minute"))
ap.add_argument("--truncate", default=None, help="causality check: build on the bars up to this time only")
A = ap.parse_args()
TF = A.tf; TF_MIN = lab.TF_MIN[TF]
OUT = os.path.join(LAB, "fz_v3", "out", "data", TF)
if A.truncate:
    OUT = os.path.join(OUT, "trunc_" + A.truncate.replace("-", "").replace(":", "").replace(" ", "_"))
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(LAB, "fz_v3", "data")
PATH = os.path.join(DATA, f"niftyfut_nearmonth_{TF}_2021-10-01_to_2026-09-25.csv")
FIRST, LAST, IS_END = "2021-10-01", "2026-09-25", "2025-12-31"
LOT, SLIP, SQUARE_OFF = 65, 5.0, "15:25"
# Foundation rules and the FZ block per timeframe: ST1 + ST7 (1 min), ST2 + ST8 (5 min)
FND = {"minute": "strategy_1.json", "5minute": "strategy_2.json"}[TF]
FZF = {"minute": "strategy_7.json", "5minute": "strategy_8.json"}[TF]
st_f = json.load(open(os.path.join(LAB, "strategies", FND), encoding="utf-8"))
st_z = json.load(open(os.path.join(LAB, "strategies", FZF), encoding="utf-8"))
RULES = dict(break_mode=st_f["rules"]["break_mode"], choch_mode=st_f["rules"].get("choch_mode", st_f["rules"]["break_mode"]),
             avwap_weight=st_f["rules"]["avwap_weight"], sl_rule=st_f["rules"]["sl_rule"])
assert RULES == dict(break_mode=st_z["rules"]["break_mode"], choch_mode=st_z["rules"].get("choch_mode"), avwap_weight=st_z["rules"]["avwap_weight"], sl_rule=st_z["rules"]["sl_rule"])
assert st_f["lot_size"] == LOT and st_z["types"]["FUT"]["slippage_pts"] == SLIP
WARMUP = st_z["warmup_days"]
CFG = fz.thresholds(st_z["fz"][TF])
ATR_N = st_z["options"]["atr_period"]
CS = json.load(open(os.path.join(LAB, "config", "charges.json"), encoding="utf-8"))["ZERODHA_NFO_FUT"]
# time windows in bars: 1 hour and 3 hours of the working timeframe
H1, H3 = 60 // TF_MIN, 180 // TF_MIN
TOUCH_LOOKBACK, TOUCH_VERDICT_BARS, BREAK_ATR = H1, 15 if TF == "minute" else 3, 0.5      # 1 hour back; 15-minute verdict window
MED_MIN_BARS = 5

T0 = time.time(); TIMES = {}
proc = psutil.Process()
def lap(name):
    TIMES[name] = round(time.time() - T0, 2)
    print(f"[{TIMES[name]:8.1f}s] {name}  [rss {proc.memory_info().rss / 1e6:.0f} MB]", flush=True)

def sha(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:16]

# ---------------------------------------------------------------- 1. bars
fut, s0 = engine.load(PATH, FIRST, LAST, 0)
assert s0 == 0 and fut["t"][0][:10] == FIRST and fut["t"][-1][:10] == LAST, (s0, fut["t"][0], fut["t"][-1])
extra = list(csv.DictReader(open(PATH)))
assert len(extra) == len(fut["t"]) and all(r["datetime"] == x for r, x in zip(extra, fut["t"])), "CSV rows do not align with engine.load"
if A.truncate:
    keep = sum(1 for x in fut["t"] if x <= A.truncate)
    fut = {k: fut[k][:keep] for k in "tohlcv"}; extra = extra[:keep]
    print(f"TRUNCATED at {A.truncate}: {keep} bars -> {OUT}", flush=True)
t, o, h, l, c, v = (fut[k] for k in "tohlcv")
n = len(t)
assert all(t[i] < t[i + 1] for i in range(n - 1)), "bars not strictly time-ordered"
oi = [float(r.get("oi") or 0) for r in extra]
contract = [r["contract"] for r in extra]; expiry = [r["expiry"] for r in extra]
front_month = [int(float(r.get("front_month") or 0)) for r in extra]
del extra
sess, sbar = [0] * n, [0] * n
for i in range(1, n):
    if t[i][:10] != t[i - 1][:10]: sess[i], sbar[i] = sess[i - 1] + 1, 0
    else: sess[i], sbar[i] = sess[i - 1], sbar[i - 1] + 1
days = sorted({x[:10] for x in t})
sess_open_i = {}
for i in range(n):
    if sbar[i] == 0: sess_open_i[sess[i]] = i
sess_last_i = {}
for i in range(n): sess_last_i[sess[i]] = i
# fm per session = the last row of the day, as lab.fm_by_day; fm_na = not the front month or zero volume
fm_day = {}
for i in range(n): fm_day[t[i][:10]] = front_month[i]
fm_na = [fm_day[t[i][:10]] == 0 or v[i] == 0 for i in range(n)]
atr14 = lab.atr_series(types.SimpleNamespace(t=t, h=h, l=l, c=c), ATR_N)
print(f"{TF}: bars {n}, sessions {len(days)}, first {t[0]}, last {t[-1]}, front_month==0 bars {sum(1 for x in front_month if x == 0)}, "
      f"zero-volume bars {sum(1 for x in v if x == 0)}, fm_na bars {sum(fm_na)}", flush=True)
lap("load")

# ---------------------------------------------------------------- 2. engine
r = engine.run(fut, RULES)
lap("engine.run")
sw, events, chs, prot, setups, trades, skipped = (r[k] for k in ("sw", "events", "chs", "prot", "setups", "trades", "skipped"))
print(f"swings {len(sw)}, events {len(events)} (CHoCH {len(chs)}, BOS {len(events) - len(chs)}), setups {len(setups)}, "
      f"trades {len(trades)}, engine-skipped {len(skipped)}", flush=True)

# ---------------------------------------------------------------- 3. pricing (lab.price_trade mirrored) and the L1 cut
def price(entry, exit_px, up):
    e = c[entry]
    if up: buy, sell = e + SLIP, exit_px - SLIP
    else: sell, buy = e - SLIP, exit_px + SLIP
    chg = lab.trade_charges(CS, buy, sell, LOT)
    gross = (sell - buy) * LOT
    return dict(gross_inr=round(gross, 2), charges_inr=round(chg["total"], 2), slip_inr=2 * SLIP * LOT,
                cost_inr=round(chg["total"] + 2 * SLIP * LOT, 2), net_inr=round(gross - chg["total"], 2))

def excursion(entry, exit_, up):
    """MFE / MAE on wicks over bars entry+1..exit, in points before slippage (MFE >= 0, MAE <= 0), and their bar offsets."""
    if exit_ <= entry: return 0.0, 0.0, 0, 0
    hs, ls = h[entry + 1:exit_ + 1], l[entry + 1:exit_ + 1]
    e = c[entry]
    jh = max(range(len(hs)), key=hs.__getitem__); jl = min(range(len(ls)), key=ls.__getitem__)
    if up: fav, adv, jf, ja = hs[jh] - e, ls[jl] - e, jh + 1, jl + 1
    else: fav, adv, jf, ja = e - ls[jl], e - hs[jh], jl + 1, jh + 1
    return round(max(fav, 0.0), 2), round(min(adv, 0.0), 2), jf, ja

def eod_bar(entry):
    """The square-off bar of the entry session: the last bar opening at or before 15:25 that day (lab.eod_cut)."""
    day = t[entry][:10]
    e = f"{day} {SQUARE_OFF}:00"
    j = bisect.bisect_right(t, e) - 1
    return j if (j >= 0 and t[j][:10] == day and j >= entry) else None

contract_last = {}
for i in range(n): contract_last[contract[i]] = i

def l1_cut(x):
    """The L1 (intraday 15:25) version of an engine-shaped trade: (exit bar, exit px, reason, taken)."""
    entry = x["entry"]
    if t[entry][11:16] >= SQUARE_OFF: return None, None, "not_taken", False
    xi, px, reason = x["exit"], x["exit_px"], x["exit_reason"]
    cap = contract_last[contract[entry]]                    # the contract's last candle ends the position (lab: 'expiry')
    if xi > cap: xi, px, reason = cap, c[cap], "expiry"
    j = eod_bar(entry)
    if j is not None and xi > j: xi, px, reason = j, c[j], "eod"
    return xi, px, reason, True

def trade_row(x, prefix=""):
    up = x["dir"] == "up"
    pr = price(x["entry"], x["exit_px"], up)
    mfe, mae, jf, ja = excursion(x["entry"], x["exit"], up)
    pts = round(x["pts"], 2)
    assert abs(pts * LOT - pr["cost_inr"] - pr["net_inr"]) < 0.05, "net != pts x lot - cost"
    row = dict(entry_i=x["entry"], entry_time=t[x["entry"]], date=t[x["entry"]][:10], session_idx=sess[x["entry"]], dir=x["dir"],
               choch_i=x["choch"], choch_time=t[x["choch"]], entry_px=c[x["entry"]], sl=x["sl"],
               sl_dist_pts=round((c[x["entry"]] - x["sl"]) if up else (x["sl"] - c[x["entry"]]), 2) if x["sl"] is not None else None,
               exit_i=x["exit"], exit_time=t[x["exit"]], exit_px=x["exit_px"], exit_reason=x["exit_reason"], open=bool(x["open"]),
               pts=pts, pts_x_lot=round(pts * LOT, 2), **pr, win=pr["net_inr"] > 0, win_pts=pts > 0,
               bars_held=x["exit"] - x["entry"], sessions_held=sess[x["exit"]] - sess[x["entry"]],
               crosses_roll=contract[x["entry"]] != contract[x["exit"]], contract=contract[x["entry"]],
               mfe_pts=mfe, mae_pts=mae, mfe_bar=jf, mae_bar=ja, split="IS" if t[x["entry"]][:10] <= IS_END else "OOS",
               in_warmup=sess[x["entry"]] < WARMUP)
    xi, px, reason, taken = l1_cut(x)
    if taken:
        pr1 = price(x["entry"], px, up); m1, a1, _, _ = excursion(x["entry"], xi, up)
        row.update(l1_taken=True, l1_exit_i=xi, l1_exit_time=t[xi], l1_exit_px=px, l1_exit_reason=reason,
                   l1_pts=round((1 if up else -1) * (px - c[x["entry"]]), 2), l1_gross_inr=pr1["gross_inr"], l1_charges_inr=pr1["charges_inr"],
                   l1_cost_inr=pr1["cost_inr"], l1_net_inr=pr1["net_inr"], l1_win=pr1["net_inr"] > 0, l1_bars_held=xi - x["entry"],
                   l1_mfe_pts=m1, l1_mae_pts=a1, l1_cut=reason != x["exit_reason"])
    else:
        row.update(l1_taken=False, l1_exit_i=None, l1_exit_time=None, l1_exit_px=None, l1_exit_reason="not_taken", l1_pts=None,
                   l1_gross_inr=None, l1_charges_inr=None, l1_cost_inr=None, l1_net_inr=None, l1_win=None, l1_bars_held=None,
                   l1_mfe_pts=None, l1_mae_pts=None, l1_cut=None)
    return row

trade_rows = [trade_row(x) for x in trades]
lap("price trades")

# ---------------------------------------------------------------- 4. FZ (the frozen ST7 / ST8 block), memory from bar 0
bars = dict(fut, fm_na=fm_na, atr14=atr14)
view = fz_exec.view(r)
touch = RULES["break_mode"] == "touch"
out = fz.run(bars, view, CFG, TF_MIN, 0, fz_exec.opener(bars, r, RULES["sl_rule"], touch))
lap("fz.run")
fz_trades = fz_exec.build_trades(bars, r, out, RULES["sl_rule"], touch)
card, ledger, zones, watches, stats = out["card"], out["ledger"], out["zones"], out["watches"], out["stats"]
assert len(card) == n and len(ledger) == len(setups), "card / ledger sizes"
print(f"fz: rooms {len(zones)}, ledger {len(ledger)}, watches {len(watches)}, positions {len(fz_trades)} "
      f"(TAKE {sum(1 for x in fz_trades if x['gate'] == 'TAKE')}, REENTER {sum(1 for x in fz_trades if x['gate'] == 'REENTER')})", flush=True)

def fz_trade_row(x):
    row = trade_row(x)
    row.update(gate=x["gate"], setup_i=x.get("setup_i", x["entry"]), zone_id=x.get("zone_id"), fill_used=x.get("fill_used"),
               reenter_reason=x.get("reenter_reason"), sl_bar=x.get("sl_bar"), sl_in_band=x.get("sl_in_band"))
    return row
fz_trade_rows = [fz_trade_row(x) for x in fz_trades]
lap("fz build_trades")

# ---------------------------------------------------------------- 5. per-bar volume baselines (same session, prior bars only)
V = np.array(v, dtype=float); SESS = np.array(sess); SBAR = np.array(sbar)
H_, L_, C_, O_ = (np.array(x, dtype=float) for x in (h, l, c, o))
ATR = np.array(atr14, dtype=float)
FMNA = np.array(fm_na)
bdf = pd.DataFrame(dict(session_idx=SESS, volume=V))
g = bdf.groupby("session_idx")["volume"]
vol_med20 = g.transform(lambda s: s.shift(1).rolling(20, min_periods=MED_MIN_BARS).median()).to_numpy()
vol_med60 = g.transform(lambda s: s.shift(1).rolling(60, min_periods=MED_MIN_BARS).median()).to_numpy()
usable = ~FMNA
with np.errstate(all="ignore"):
    r20 = np.where(usable & (vol_med20 > 0), V / vol_med20, np.nan)
    r60 = np.where(usable & (vol_med60 > 0), V / vol_med60, np.nan)
sess_cumvol = g.cumsum().to_numpy()
S = int(SESS.max()) + 1; SB = int(SBAR.max()) + 1
cum = np.full((S, SB), np.nan); cum[SESS, SBAR] = sess_cumvol
ref = np.full((S, SB), np.nan)
for s_ in range(1, S):
    lo_ = max(0, s_ - 20)
    if s_ - lo_ >= 5:
        with np.errstate(all="ignore"): ref[s_] = np.nanmedian(cum[lo_:s_], axis=0)
with np.errstate(all="ignore"):
    cumratio = np.where(usable, sess_cumvol / ref[SESS, SBAR], np.nan)
lap("volume baselines")

# ---------------------------------------------------------------- 6. per-SETUP features
ev_i = np.array([e["i"] for e in events]); ev_kind = np.array([e["kind"] for e in events]); ev_dir = np.array([e["dir"] for e in events])
ev_flip = np.array([int(bool(e.get("flip"))) for e in events])
ch_by_i = {e["i"]: e for e in chs}
swH = [(s["conf"], s["p"], s["bar"]) for s in sw if s["k"] == "H"]; swL = [(s["conf"], s["p"], s["bar"]) for s in sw if s["k"] == "L"]
swH_conf, swL_conf = [x[0] for x in swH], [x[0] for x in swL]
sw_conf_all = np.array([s["conf"] for s in sw])
trow_by_entry = {x["entry_i"]: x for x in trade_rows}
skipped_by_entry = {x["entry"]: x for x in skipped}
fz_by_setup = {}
for x in fz_trade_rows: fz_by_setup.setdefault(x["setup_i"], x)
ledger_by_i = {row["i"]: row for row in ledger}
setups_by_sess = {}
for x in setups: setups_by_sess.setdefault(sess[x["i"]], []).append(x["i"])
trades_by_sess = {}
for x in trade_rows: trades_by_sess.setdefault(x["session_idx"], []).append(x)
z_lo = np.array([z["lo"] for z in zones], dtype=float); z_hi = np.array([z["hi"] for z in zones], dtype=float)
z_birth = np.array([z["birth_bar"] for z in zones]); z_ret = np.array([z["retired_bar"] if z["retired_bar"] is not None else np.inf for z in zones], dtype=float)
z_id = np.array([z["id"] for z in zones])
PROT = np.array([np.nan if p is None else p for p in prot], dtype=float)

def hour_bin(hm): return "<" + CFG["open_window_until"] if hm < CFG["open_window_until"] else ">=" + CFG["no_entry_from"] if hm >= CFG["no_entry_from"] else hm[:2]

def regime(k, s):
    m = bisect.bisect_right(ev_i, k)
    K, Dd, F, I = ev_kind[:m], ev_dir[:m], ev_flip[:m], ev_i[:m]
    bos_pos = np.flatnonzero(K == "BOS"); ch_pos = np.flatnonzero(K == "CHoCH")
    lb = bos_pos[-1] if len(bos_pos) else -1; lc = ch_pos[-1] if len(ch_pos) else -1
    since_bos = K[lb + 1:]
    o_ = dict(n_events_asof=int(m), n_choch_since_bos=int((since_bos == "CHoCH").sum()),
              n_flip_since_bos=int(F[lb + 1:][since_bos == "CHoCH"].sum()) if len(since_bos) else 0,
              n_bos_since_choch=int((K[lc + 1:] == "BOS").sum()),
              bars_since_bos=int(k - I[lb]) if lb >= 0 else None, last_bos_dir=str(Dd[lb]) if lb >= 0 else "none",
              last_bos_same_session=bool(sess[I[lb]] == s) if lb >= 0 else None)
    today = SESS[I] == s
    Kt = K[today]
    bt = np.flatnonzero(Kt == "BOS"); lbt = bt[-1] if len(bt) else -1
    o_["n_choch_since_bos_today"] = int((Kt[lbt + 1:] == "CHoCH").sum())
    o_["bars_since_prev_choch"] = int(k - I[ch_pos[-2]]) if len(ch_pos) >= 2 else None
    o_["last_choch_dir"] = str(Dd[lc]) if lc >= 0 else "none"
    last6 = list(zip(K[-6:], Dd[-6:]))
    o_["alt_dir6"] = int(sum(1 for (_, d1), (_, d2) in zip(last6, last6[1:]) if d1 != d2))
    o_["alt_kind6"] = int(sum(1 for (k1, _), (k2, _) in zip(last6, last6[1:]) if k1 != k2))
    o_["last6_kinds"] = " ".join(("C" if kk == "CHoCH" else "B") + ("u" if dd == "up" else "d") for kk, dd in last6)
    run_ = 0
    for kk in K[::-1]:
        if kk == "CHoCH": run_ += 1
        else: break
    o_["choch_run"] = int(run_)
    for name, N in (("1h", H1), ("3h", H3)):
        w = I > k - N
        o_[f"n_choch_{name}"] = int((K[w] == "CHoCH").sum()); o_[f"n_bos_{name}"] = int((K[w] == "BOS").sum())
    o_["n_events_today"] = int(today.sum()); o_["n_choch_today"] = int((Kt == "CHoCH").sum()); o_["n_bos_today"] = o_["n_events_today"] - o_["n_choch_today"]
    return o_

def window_feats(k, s, ch):
    a = ATR[k]; j0 = sess_open_i[s]
    def rng(lo_i):
        return float(H_[lo_i:k + 1].max() - L_[lo_i:k + 1].min())
    r1, r3 = rng(max(j0, k - H1 + 1)), rng(max(j0, k - H3 + 1))
    so = O_[j0]; sh_, sl_ = float(H_[j0:k + 1].max()), float(L_[j0:k + 1].min())
    prev_close = float(C_[j0 - 1]) if j0 > 0 else None
    seg = C_[max(j0, k - H1):k + 1]
    er = float(abs(seg[-1] - seg[0]) / np.abs(np.diff(seg)).sum()) if len(seg) >= 6 and np.abs(np.diff(seg)).sum() > 0 else None
    return dict(atr14=round(float(a), 4), atr_bps=round(1e4 * a / C_[k], 3),
                range_1h_pts=round(r1, 2), range_1h_atr=round(r1 / a, 4) if a else None,
                range_3h_pts=round(r3, 2), range_3h_atr=round(r3 / a, 4) if a else None,
                range_since_choch_atr=round(float(H_[ch:k + 1].max() - L_[ch:k + 1].min()) / a, 4) if a else None,
                bar_range_pts=round(float(H_[k] - L_[k]), 2), bar_body_pts=round(float(C_[k] - O_[k]), 2),
                bar_range_atr=round(float(H_[k] - L_[k]) / a, 4) if a else None,
                close_pos_in_bar=round(float((C_[k] - L_[k]) / (H_[k] - L_[k])), 4) if H_[k] > L_[k] else None,
                sess_open=float(so), close_vs_sess_open_pts=round(float(C_[k] - so), 2),
                sess_range_atr=round((sh_ - sl_) / a, 4) if a else None,
                pos_in_session_range=round((C_[k] - sl_) / (sh_ - sl_), 4) if sh_ > sl_ else None,
                gap_pts=round(float(so - prev_close), 2) if prev_close is not None else None, prev_close=prev_close,
                ret_1h_pts=round(float(C_[k] - C_[k - H1]), 2) if k - H1 >= j0 else None,
                ret_3h_pts=round(float(C_[k] - C_[k - H3]), 2) if k - H3 >= j0 else None, er_1h=round(er, 4) if er is not None else None)

def hv_stats(k, s, thr):
    """Latest bar j in [session start, k] with vol_ratio20 >= thr: bars ago, its direction, whether its low / high held since."""
    j0 = sess_open_i[s]
    seg = r20[j0:k + 1]
    with np.errstate(invalid="ignore"): ok = np.flatnonzero(seg >= thr)
    if len(ok) == 0: return dict(bars_since=None, dir="none", dir_agree=None, low_held=None, high_held=None, ratio=None)
    j = j0 + ok[-1]
    d = "up" if c[j] > o[j] else "down" if c[j] < o[j] else "flat"
    if j == k: return dict(bars_since=0, dir=d, dir_agree=None, low_held=None, high_held=None, ratio=round(float(r20[j]), 3))
    return dict(bars_since=int(k - j), dir=d, dir_agree=None, low_held=bool(L_[j + 1:k + 1].min() >= L_[j]),
                high_held=bool(H_[j + 1:k + 1].max() <= H_[j]), ratio=round(float(r20[j]), 3))

def volume_feats(k, s, d, ch):
    j0 = sess_open_i[s]
    f = dict(vol=float(V[k]), vol_med20_prior=None if np.isnan(vol_med20[k]) else float(vol_med20[k]),
             vol_med60_prior=None if np.isnan(vol_med60[k]) else float(vol_med60[k]),
             vol_ratio20=None if np.isnan(r20[k]) else round(float(r20[k]), 4), vol_ratio60=None if np.isnan(r60[k]) else round(float(r60[k]), 4),
             vol_na=bool(FMNA[k]), sess_cumvol_ratio20s=None if np.isnan(cumratio[k]) else round(float(cumratio[k]), 4))
    for N in (5, 15):
        seg = r20[max(j0, k - N + 1):k + 1]
        f[f"vol_max_ratio20_{N}"] = round(float(np.nanmax(seg)), 4) if np.isfinite(seg).any() else None
    for thr in (2, 3):
        hv = hv_stats(k, s, thr)
        hv["dir_agree"] = (hv["dir"] == d) if hv["dir"] != "none" else None
        f.update({f"hv{thr}_{kk}": vv for kk, vv in hv.items()})
    seg = r20[ch:k + 1]
    f["vol_ratio20_at_choch"] = None if np.isnan(r20[ch]) else round(float(r20[ch]), 4)
    f["vol_max_ratio20_choch_to_k"] = round(float(np.nanmax(seg)), 4) if np.isfinite(seg).any() else None
    j_prev = sess_open_i.get(s - 1)
    if j_prev is not None:
        cumv = float(V[j0:k + 1].sum()); prev = float(V[j_prev:min(j_prev + sbar[k] + 1, j0)].sum())
        f["sess_vol_vs_prev_sess"] = round(cumv / prev, 4) if prev else None
    else: f["sess_vol_vs_prev_sess"] = None
    return f

def touch_stats(Lv, k):
    """Touch episodes of level Lv in bars [k-TOUCH_LOOKBACK, k-1] (l <= Lv <= h); the last episode's verdict within
    TOUCH_VERDICT_BARS bars after it (never past k): broke (a close beyond by > BREAK_ATR x atr14) / held / pending / none / na."""
    if Lv is None or not np.isfinite(Lv): return None, "na", None
    j0 = max(0, k - TOUCH_LOOKBACK)
    hit = (L_[j0:k] <= Lv) & (H_[j0:k] >= Lv)
    if not hit.any(): return 0, "none", None
    idx = np.flatnonzero(hit) + j0
    starts = idx[np.r_[True, np.diff(idx) > 1]]
    js, je = int(starts[-1]), int(idx[-1])
    ref_px = C_[js - 1] if js >= 1 else O_[js]
    side = np.sign(ref_px - Lv) or np.sign(O_[js] - Lv)
    if side == 0: return int(len(starts)), "na", int(k - je)
    a = ATR[je]; w0, w1 = je + 1, min(je + TOUCH_VERDICT_BARS, k)
    broke = False
    if w1 >= w0:
        cc = C_[w0:w1 + 1]
        broke = bool(((Lv - cc) > BREAK_ATR * a).any() if side > 0 else ((cc - Lv) > BREAK_ATR * a).any())
    verdict = "broke" if broke else "pending" if je + TOUCH_VERDICT_BARS > k else "held"
    return int(len(starts)), verdict, int(k - je)

def level_feats(k, d, ch, lvl):
    sg = 1 if d == "up" else -1
    a = ATR[k] or None
    ck = C_[k]
    jH, jL = bisect.bisect_right(swH_conf, k) - 1, bisect.bisect_right(swL_conf, k) - 1
    shp = swH[jH][1] if jH >= 0 else None; slp = swL[jL][1] if jL >= 0 else None
    p = PROT[k]; p = None if np.isnan(p) else float(p)
    f = dict(prot_lvl=p, dist_prot_dir_atr=round(sg * (ck - p) / a, 4) if (p is not None and a) else None,
             last_sh_px=shp, last_sl_px=slp,
             dist_sh_atr=round((shp - ck) / a, 4) if (shp is not None and a) else None,      # + = swing high above the close
             dist_sl_atr=round((ck - slp) / a, 4) if (slp is not None and a) else None,      # + = swing low below the close
             last_sh_bars_ago=int(k - swH[jH][2]) if jH >= 0 else None, last_sl_bars_ago=int(k - swL[jL][2]) if jL >= 0 else None,
             swing_ahead_dist_atr=(round((shp - ck) / a, 4) if (shp is not None and a) else None) if d == "up" else (round((ck - slp) / a, 4) if (slp is not None and a) else None),
             choch_lvl=lvl, dist_choch_lvl_atr=round(sg * (ck - lvl) / a, 4) if (lvl is not None and a) else None,
             n_swings_1h=int(((sw_conf_all <= k) & (sw_conf_all > k - H1)).sum()),
             choch_bar_range_atr=round(float(H_[ch] - L_[ch]) / a, 4) if a else None,
             move_since_choch_pts=round(float(sg * (ck - C_[ch])), 2))
    cands = ([(abs(shp - ck), "H", shp)] if shp is not None else []) + ([(abs(slp - ck), "L", slp)] if slp is not None else [])
    Ls = None
    if cands:
        _, kind_, Ls = min(cands); f.update(swing_near_kind=kind_, swing_near_dist_dir_atr=round(sg * (Ls - ck) / a, 4) if a else None)
    else: f.update(swing_near_kind="", swing_near_dist_dir_atr=None)
    alive = (z_birth <= k) & (z_ret > k)
    f["n_rooms_alive"] = int(alive.sum())
    Lr = None
    if alive.any():
        lo_, hi_, ids = z_lo[alive], z_hi[alive], z_id[alive]
        edges = np.concatenate([lo_, hi_]); eids = np.concatenate([ids, ids]); ekind = np.array(["lo"] * len(lo_) + ["hi"] * len(hi_))
        dd = edges - ck; jn = int(np.argmin(np.abs(dd)))
        Lr = float(edges[jn])
        f.update(room_edge=Lr, room_edge_dist_dir_atr=round(sg * dd[jn] / a, 4) if a else None, room_edge_id=str(eids[jn]), room_edge_kind=str(ekind[jn]))
        ahead = sg * dd; ah = ahead[ahead > 1e-9]; bh = -ahead[ahead < -1e-9]
        f["room_ahead_dist_atr"] = round(float(ah.min() / a), 4) if (len(ah) and a) else None
        f["room_behind_dist_atr"] = round(float(bh.min() / a), 4) if (len(bh) and a) else None
    else:
        f.update(room_edge=None, room_edge_dist_dir_atr=None, room_edge_id="", room_edge_kind="", room_ahead_dist_atr=None, room_behind_dist_atr=None)
    for name, Lv in (("prot", p), ("room", Lr), ("swing", Ls)):
        ne, verdict, ago = touch_stats(Lv, k)
        f.update({f"touch_{name}_n": ne, f"touch_{name}_last": verdict, f"touch_{name}_bars_ago": ago})
    return f

def asof_today(k, s):
    """The session's Foundation trades already closed by bar k (entry < k, exit <= k): known at k's close."""
    closed = [x for x in trades_by_sess.get(s, []) if x["exit_i"] <= k and x["entry_i"] < k]
    return dict(today_n_closed_asof=len(closed), today_net_asof=round(sum(x["net_inr"] for x in closed), 2),
                today_pts_asof=round(sum(x["pts"] for x in closed), 2),
                today_n_stops_asof=sum(1 for x in closed if x["exit_reason"] == "stop_loss"),
                today_n_setups_before=sum(1 for i in setups_by_sess[s] if i < k),
                last_closed_net_asof=closed[-1]["net_inr"] if closed else None,
                last_closed_reason_asof=closed[-1]["exit_reason"] if closed else None)

CARD_KEYS = ("zone_id", "visit_n", "this_bars", "this_vol", "vol_na", "first_bars", "first_vol", "first_vol_na", "read", "left_id",
             "out_run", "out_side", "gap_pts", "wick_depth", "last_hunt_at", "last_hunt_dir", "last_reject_at", "last_reject_dir",
             "cluster_sit", "prev_bars", "prev_vol", "last_leave_failed", "in_id", "leave_side", "leave_vol_ok", "leave_kind",
             "first_clock_lived", "touches")
LEDGER_ASOF = ("zone_id", "zone_kind", "band_lo", "band_hi", "visit_n", "this_bars", "this_vol", "first_bars", "first_vol", "vol_na",
               "first_vol_na", "read", "left_id", "in_id", "level_in_band", "gate", "block_reason", "branch", "take_why",
               "entered_zone_id", "entered_visit_n", "entered_read", "leave_vol_ok", "leave_kind", "watch_kind", "watch_band_id")
LEDGER_POST = ("outcome_gate", "refused", "watch_outcome", "reenter_reason", "fill_used", "fill_bar", "fill_delay_bars",
               "edge_dist_pts", "armed_bars", "rearmed_bars", "sl_bar")

feat_rows = []
for x in setups:
    k, d, ch = x["i"], x["dir"], x["ch"]
    up, sg, s = d == "up", (1 if d == "up" else -1), sess[k]
    e = ch_by_i[ch]; lvl = e["lvl"]
    row = dict(setup_i=k, time=t[k], date=t[k][:10], session_idx=s, session_bar=sbar[k], hhmm=t[k][11:16], hour=int(t[k][11:13]),
               hour_bin=hour_bin(t[k][11:16]), minute_of_day=int(t[k][11:13]) * 60 + int(t[k][14:16]),
               dow=D.date.fromisoformat(t[k][:10]).weekday(), dir=d, dir_sign=sg, choch_i=ch, choch_time=t[ch], bars_since_choch=k - ch,
               choch_flip=bool(e.get("flip")), choch_trend_before=e["tr"], choch_same_session=sess[ch] == s,
               open=o[k], high=h[k], low=l[k], close=c[k], contract=contract[k],
               days_to_expiry=(D.date.fromisoformat(expiry[k]) - D.date.fromisoformat(t[k][:10])).days,
               split="IS" if t[k][:10] <= IS_END else "OOS", in_warmup=s < WARMUP)
    tr = trow_by_entry.get(k)
    if tr is not None: sl = tr["sl"]; row.update(traded=True, engine_skipped=False)
    else: sl = skipped_by_entry[k]["sl"]; row.update(traded=False, engine_skipped=True)
    row.update(sl=sl, sl_dist_pts=round(sg * (c[k] - sl), 2) if sl is not None else None,
               sl_dist_atr=round(sg * (c[k] - sl) / atr14[k], 4) if (sl is not None and atr14[k]) else None)
    row.update(window_feats(k, s, ch)); row.update(regime(k, s)); row.update(volume_feats(k, s, d, ch)); row.update(level_feats(k, d, ch, lvl))
    row.update(asof_today(k, s))
    cd = card[k]
    row.update({"card_" + kk: cd[kk] for kk in CARD_KEYS})
    Lg = ledger_by_i[k]
    row.update({"fz_" + kk: Lg[kk] for kk in LEDGER_ASOF})
    row.update({"fzpost_" + kk: Lg[kk] for kk in LEDGER_POST})
    lo_, hi_ = Lg["band_lo"], Lg["band_hi"]
    if lo_ is not None and hi_ is not None and hi_ > lo_:
        row.update(fz_band_width=round(hi_ - lo_, 2), fz_band_width_atr=round((hi_ - lo_) / atr14[k], 4) if atr14[k] else None,
                   fz_pos_in_band=round((c[k] - lo_) / (hi_ - lo_), 4),
                   fz_pos_in_band_dir=round(((c[k] - lo_) if up else (hi_ - c[k])) / (hi_ - lo_), 4),
                   fz_dist_band_edge_ahead=round((hi_ - c[k]) if up else (c[k] - lo_), 2),
                   fz_dist_band_edge_behind=round((c[k] - lo_) if up else (hi_ - c[k]), 2))
    else:
        row.update(fz_band_width=None, fz_band_width_atr=None, fz_pos_in_band=None, fz_pos_in_band_dir=None, fz_dist_band_edge_ahead=None, fz_dist_band_edge_behind=None)
    live = (not cd["vol_na"]) and cd["first_vol_na"] is False and (cd["first_vol"] or 0) > 0 and cd["this_vol"] is not None
    row["card_vol_ratio"] = round(cd["this_vol"] / cd["first_vol"], 4) if live else None
    row["card_bars_since_hunt"] = (k - cd["last_hunt_at"]) if cd["last_hunt_at"] is not None else None
    row["card_bars_since_reject"] = (k - cd["last_reject_at"]) if cd["last_reject_at"] is not None else None
    row["card_hunt_dir_agree"] = (cd["last_hunt_dir"] == d) if cd["last_hunt_dir"] is not None else None
    row["card_in_room"] = cd["in_id"] is not None; row["card_ref_room_live"] = cd["zone_id"] is not None
    # ---- labels (never features)
    for N in (5, 15, 30):
        row[f"fwd_ret_{N}_dir_pts"] = round(sg * (c[k + N] - c[k]), 2) if k + N < n else None
    j1 = min(k + 30, n - 1)
    row["fwd_mfe30"] = round((float(H_[k + 1:j1 + 1].max()) - c[k] if up else c[k] - float(L_[k + 1:j1 + 1].min())), 2) if j1 > k else None
    row["fwd_mae30"] = round((float(L_[k + 1:j1 + 1].min()) - c[k] if up else c[k] - float(H_[k + 1:j1 + 1].max())), 2) if j1 > k else None
    FND = ("exit_i", "exit_time", "exit_px", "exit_reason", "open", "pts", "gross_inr", "charges_inr", "cost_inr", "net_inr", "win",
           "bars_held", "sessions_held", "crosses_roll", "mfe_pts", "mae_pts", "mfe_bar", "mae_bar")
    L1 = ("taken", "exit_i", "exit_time", "exit_px", "exit_reason", "pts", "gross_inr", "charges_inr", "cost_inr", "net_inr", "win",
          "bars_held", "mfe_pts", "mae_pts", "cut")
    if tr is not None:
        row.update({"fnd_" + kk: tr[kk] for kk in FND}); row.update({"l1_" + kk: tr["l1_" + kk] for kk in L1})
    else:
        row.update({"fnd_" + kk: None for kk in FND}); row.update({"l1_" + kk: None for kk in L1}); row["l1_taken"] = False; row["l1_exit_reason"] = "not_taken"
    fzx = fz_by_setup.get(k)
    row["fz_traded"] = fzx is not None                               # POST: a REENTER on this SETUP may fill on a later bar
    if fzx is not None:
        row.update(fzpos_kind=fzx["gate"], fzpos_entry_i=fzx["entry_i"], fzpos_entry_time=fzx["entry_time"], fzpos_exit_i=fzx["exit_i"],
                   fzpos_exit_time=fzx["exit_time"], fzpos_exit_reason=fzx["exit_reason"], fzpos_pts=fzx["pts"], fzpos_net_inr=fzx["net_inr"],
                   fzpos_l1_net_inr=fzx["l1_net_inr"], fzpos_l1_exit_reason=fzx["l1_exit_reason"])
    else:
        row.update(fzpos_kind=None, fzpos_entry_i=None, fzpos_entry_time=None, fzpos_exit_i=None, fzpos_exit_time=None, fzpos_exit_reason=None,
                   fzpos_pts=None, fzpos_net_inr=None, fzpos_l1_net_inr=None, fzpos_l1_exit_reason=None)
    feat_rows.append(row)
lap("features")

# ---------------------------------------------------------------- 7. write
def write(name, rows):
    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(OUT, name + ".parquet"), index=False)
    print(f"  wrote {name}: {len(df)} rows x {len(df.columns)} cols", flush=True)
    return df

write("bars", [dict(i=i, datetime=t[i], date=t[i][:10], session_idx=sess[i], session_bar=sbar[i], open=o[i], high=h[i], low=l[i], close=c[i],
                    volume=v[i], oi=oi[i], contract=contract[i], expiry=expiry[i], front_month=front_month[i], fm_na=fm_na[i],
                    atr14=round(atr14[i], 4), prot=prot[i], vol_med20_prior=None if np.isnan(vol_med20[i]) else float(vol_med20[i]),
                    vol_ratio20=None if np.isnan(r20[i]) else float(r20[i]), vol_ratio60=None if np.isnan(r60[i]) else float(r60[i]),
                    sess_cumvol=float(sess_cumvol[i]), sess_cumvol_ratio20s=None if np.isnan(cumratio[i]) else float(cumratio[i]),
                    split="IS" if t[i][:10] <= IS_END else "OOS") for i in range(n)])
nb = {}
for i in range(n): nb[sess[i]] = nb.get(sess[i], 0) + 1
write("sessions", [dict(session_idx=q, date=dd, split="IS" if dd <= IS_END else "OOS", in_warmup=q < WARMUP, n_bars=nb[q],
                        first_bar=sess_open_i[q], last_bar=sess_last_i[q], front_month=fm_day[dd], contract=contract[sess_open_i[q]],
                        expiry=expiry[sess_open_i[q]]) for q, dd in enumerate(days)])
write("swings", [dict(seq=q, kind=s_["k"], bar=s_["bar"], time=t[s_["bar"]], price=s_["p"], conf_bar=s_["conf"], conf_time=t[s_["conf"]],
                      broken_final=s_["broken"]) for q, s_ in enumerate(sw)])
write("events", [dict(seq=q, i=e["i"], time=t[e["i"]], kind=e["kind"], dir=e["dir"], flip=e.get("flip"), lvl=e.get("lvl"), av=e.get("av"),
                      trend_before=e.get("tr"), sh_bar=e["hi"]["bar"] if e.get("hi") else None, sh_px=e["hi"]["p"] if e.get("hi") else None,
                      sl_bar=e["lo"]["bar"] if e.get("lo") else None, sl_px=e["lo"]["p"] if e.get("lo") else None,
                      prot_swing_bar=e["sw"]["bar"] if e.get("sw") else None, prot_swing_kind=e["sw"]["k"] if e.get("sw") else None,
                      window_end=e.get("end")) for q, e in enumerate(events)])
write("setups", [dict(setup_i=x["i"], time=t[x["i"]], dir=x["dir"], choch_i=x["ch"], choch_time=t[x["ch"]], engine_skipped=x["i"] in skipped_by_entry) for x in setups])
write("skipped", [dict(entry_i=x["entry"], time=t[x["entry"]], dir=x["dir"], sl=x["sl"], close=c[x["entry"]]) for x in skipped] or [dict(entry_i=pd.NA)][:0])
write("trades", trade_rows)
write("fz_trades", fz_trade_rows)
write("fz_card", [dict(i=i, time=t[i], **{kk: cd[kk] for kk in cd}) for i, cd in enumerate(card)])
write("fz_ledger", [dict(**{kk: row[kk] for kk in row}, choch_time=t[row["choch_i"]], fill_time=t[row["fill_bar"]] if row.get("fill_bar") is not None else None) for row in ledger])
write("fz_zones", [dict(id=z["id"], kind=z["kind"], lo=z["lo"], hi=z["hi"], mid=z["mid"], origin_bar=z["origin_bar"], birth_bar=z["birth_bar"],
                        born_ts=z["born_ts"], merges=z["merges"], n_stays=len(z["visits"]), n_visits=sum(1 for V_ in z["visits"] if not V_.get("touch")),
                        touches=z["touches"], retired_bar=z["retired_bar"], retired_by=z["retired_by"],
                        retired_ts=t[z["retired_bar"]] if z["retired_bar"] is not None else None) for z in zones])
write("fz_visits", [dict(zone_id=z["id"], visit_n=V_["n"], start=V_["start"], start_time=t[V_["start"]], end=V_["end"],
                         end_time=t[V_["end"]] if V_["end"] is not None else None, ended_by=V_["ended_by"], bars=V_["bars"], vol=V_["vol"],
                         vol_na=V_["vol_na"], entry_dir=V_["entry_dir"], touch=bool(V_.get("touch")), defend_dir=V_.get("defend_dir"))
                    for z in zones for V_ in z["visits"]])
write("fz_watches", [dict(**w, opened_time=t[w["opened_at"]], outcome_time=t[w["outcome_bar"]] if w["outcome_bar"] is not None else None) for w in watches])
write("fz_decisions", [dict(kind=kd, entry=e_, entry_time=t[e_], dir=d_, setup_i=si, band_id=b["id"], band_lo=b["lo"], band_hi=b["hi"],
                            band_mid=b["mid"], band_sit_mean=b["sit_mean"], band_vol_na=b["vol_na"]) for kd, e_, d_, si, b in out["decisions"]])
feat_df = write("features", feat_rows)
json.dump(stats, open(os.path.join(OUT, "fz_stats.json"), "w"), indent=1)
lap("write")

# ---------------------------------------------------------------- 8. counts + meta
def book(rows, pre=""):
    rows = [x for x in rows if x.get(pre + "net_inr") is not None]
    nets = [x[pre + "net_inr"] for x in rows]
    return dict(n=len(rows), net_inr=round(sum(nets), 2), mean_net_inr=round(sum(nets) / len(nets), 2) if nets else None,
                wins=sum(1 for x in rows if x[pre + "win"]), pts=round(sum(x[pre + "pts"] for x in rows), 2),
                exit_reasons={k_: sum(1 for x in rows if x[pre + "exit_reason"] == k_) for k_ in sorted({x[pre + "exit_reason"] for x in rows})},
                median_cost_inr=statistics.median([x[pre + "cost_inr"] for x in rows]) if rows else None)
counts = {}
for sp in ("IS", "OOS", "ALL"):
    F_ = [x for x in feat_rows if sp == "ALL" or x["split"] == sp]
    TR = [x for x in trade_rows if sp == "ALL" or x["split"] == sp]
    FT = [x for x in fz_trade_rows if sp == "ALL" or x["split"] == sp]
    counts[sp] = dict(sessions=sum(1 for dd in days if sp == "ALL" or (dd <= IS_END) == (sp == "IS")),
                      bars=sum(1 for i in range(n) if sp == "ALL" or (t[i][:10] <= IS_END) == (sp == "IS")),
                      setups=len(F_), engine_skipped=sum(1 for x in F_ if x["engine_skipped"]),
                      foundation_L0=book(TR), foundation_L1=book(TR, "l1_"), l1_not_taken=sum(1 for x in TR if not x["l1_taken"]),
                      l1_cut=sum(1 for x in TR if x["l1_cut"]),
                      gate_at_setup={g_: sum(1 for x in F_ if x["fz_gate"] == g_) for g_ in ("TAKE", "WATCH", "BLOCK", "REENTER")},
                      outcome_gate={g_: sum(1 for x in F_ if x["fzpost_outcome_gate"] == g_) for g_ in ("TAKE", "WATCH", "BLOCK", "REENTER")},
                      fz_positions=dict(TAKE=sum(1 for x in FT if x["gate"] == "TAKE"), REENTER=sum(1 for x in FT if x["gate"] == "REENTER"),
                                        book_L0=book(FT), book_L1=book(FT, "l1_")),
                      fz_traded=sum(1 for x in F_ if x["fz_traded"]),
                      block_reasons={}, reads={})
    for x in F_:
        if x["fz_gate"] == "BLOCK": counts[sp]["block_reasons"][x["fz_block_reason"]] = counts[sp]["block_reasons"].get(x["fz_block_reason"], 0) + 1
        counts[sp]["reads"][x["fz_read"]] = counts[sp]["reads"].get(x["fz_read"], 0) + 1
TIMES["total"] = round(time.time() - T0, 2)
meta = dict(timeframe=TF, tf_min=TF_MIN, data_file=os.path.relpath(PATH, LAB), data_sha1_16=sha(PATH), first_bar=t[0], last_bar=t[-1], bars=n,
            sessions=len(days), is_window=[FIRST, IS_END], oos_window=["2026-01-01", LAST], warmup_sessions_flagged=WARMUP, truncated_at=A.truncate,
            engine_rules=RULES, engine_source=f"strategies/{FND} rules", fz_block_source=f"strategies/{FZF} fz.{TF}", fz_cfg=CFG,
            lot=LOT, slippage_pts_per_side=SLIP, square_off=SQUARE_OFF, charge_code="ZERODHA_NFO_FUT", charges=CS, atr_period=ATR_N,
            windows_bars=dict(h1=H1, h3=H3, touch_lookback=TOUCH_LOOKBACK, touch_verdict_bars=TOUCH_VERDICT_BARS, break_atr=BREAK_ATR, med_min_bars=MED_MIN_BARS),
            code_sha1_16={f: sha(os.path.join(LAB, f)) for f in ("engine.py", "fz.py", "fz_exec.py", "fz_report.py", "lab.py")},
            script_sha1_16=sha(os.path.abspath(__file__)), built_at=D.datetime.now().isoformat(timespec="seconds"),
            python=sys.version.split()[0], pandas=pd.__version__, numpy=np.__version__, peak_rss_mb=round(proc.memory_info().rss / 1e6, 1),
            run_times_s=TIMES, counts=counts)
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1, default=str)
print(json.dumps(counts, indent=1, default=str))
print("columns:", len(feat_df.columns))
print("done", TIMES)
