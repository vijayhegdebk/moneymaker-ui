"""Cross-check of the cloud rebuild (fz_v3/out/data/<tf>/) against the local build (fz_v3/built/<tf>/): SETUP counts, the
Foundation trades, the ST7/ST8 room card and ledger, the FZ positions, and the shared as-of feature columns. The cloud
rebuild is authoritative (BRIEF addendum 5); every difference is listed for fz_v3/out/QUALITY.md.

    python compare.py --tf minute | 5minute        writes ../data/<tf>/compare.json and prints the summary
"""
import os, sys, json, argparse
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True, choices=("minute", "5minute")); A = ap.parse_args()
TF = A.tf
NEW = os.path.join(LAB, "fz_v3", "out", "data", TF)
OLD = os.path.join(LAB, "fz_v3", "built", TF)
R = {}

def rd(folder, name):
    p = os.path.join(folder, name + ".parquet")
    return pd.read_parquet(p) if os.path.exists(p) else None

def same_vals(a, b, tol=1e-6):
    a = pd.Series(a).reset_index(drop=True); b = pd.Series(b).reset_index(drop=True)
    if len(a) != len(b): return False, f"length {len(a)} vs {len(b)}"
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
        x = a.astype(float).to_numpy(); y = b.astype(float).to_numpy()
        both_nan = np.isnan(x) & np.isnan(y)
        d = np.abs(x - y); d[both_nan] = 0
        bad = int((~(d <= tol)).sum())
        return bad == 0, f"{bad} differ (max |diff| {np.nanmax(d) if len(d) else 0:.4g})"
    x = a.astype(object).where(a.notna(), None); y = b.astype(object).where(b.notna(), None)
    x = x.map(lambda z: None if z is None else (int(z) if isinstance(z, (bool, np.bool_)) else z))
    y = y.map(lambda z: None if z is None else (int(z) if isinstance(z, (bool, np.bool_)) else z))
    bad = int((x.map(str) != y.map(str)).sum())
    return bad == 0, f"{bad} differ"

new_f = rd(NEW, "features"); new_tr = rd(NEW, "trades"); new_fzt = rd(NEW, "fz_trades"); new_card = rd(NEW, "fz_card")
new_led = rd(NEW, "fz_ledger"); new_z = rd(NEW, "fz_zones"); new_ev = rd(NEW, "events"); new_sw = rd(NEW, "swings")
meta_new = json.load(open(os.path.join(NEW, "meta.json")))
R["new"] = dict(setups=len(new_f), trades=len(new_tr), fz_positions=len(new_fzt), rooms=len(new_z), events=len(new_ev), swings=len(new_sw))

if TF == "5minute":
    old_f = rd(OLD, "features"); old_tr = rd(OLD, "trades"); old_fzt = rd(OLD, "fz_trades"); old_card = rd(OLD, "fz_card")
    old_led = rd(OLD, "fz_ledger"); old_z = rd(OLD, "fz_zones"); old_ev = rd(OLD, "events"); old_sw = rd(OLD, "swings")
    # column map old -> new for the shared as-of features
    FMAP = {"setup_i": "setup_i", "dir": "dir", "session_idx": "session_idx", "session_bar": "session_bar", "choch_i": "choch_i", "close": "close",
            "sl": "sl", "sl_dist_pts": "sl_dist_pts", "atr14": "atr14", "range12_atr": "range_1h_atr", "range36_atr": "range_3h_atr",
            "bar_range_atr": "bar_range_atr", "gap_pts": "gap_pts", "n_choch_since_bos": "n_choch_since_bos", "n_bos_since_choch": "n_bos_since_choch",
            "bars_since_bos": "bars_since_bos", "alternations_last6": "alt_kind6", "choch_run": "choch_run", "n_choch_today": "n_choch_today",
            "n_bos_today": "n_bos_today", "vol": "vol", "hv3_bars_since": "hv3_bars_since", "hv3_dir": "hv3_dir", "prot_lvl": "prot_lvl",
            "dist_prot_atr": "dist_prot_dir_atr", "last_sh_px": "last_sh_px", "last_sl_px": "last_sl_px", "choch_lvl": "choch_lvl",
            "dist_choch_lvl_atr": "dist_choch_lvl_atr", "move_since_choch_pts": "move_since_choch_pts", "today_n_closed_asof": "today_n_closed_asof",
            "today_net_asof": "today_net_asof", "today_n_stops_asof": "today_n_stops_asof", "today_n_setups_before": "today_n_setups_before",
            "fz_zone_id": "fz_zone_id", "fz_visit_n": "fz_visit_n", "fz_this_bars": "fz_this_bars", "fz_read": "fz_read", "fz_gate": "fz_gate",
            "fz_block_reason": "fz_block_reason", "fz_branch": "fz_branch", "fz_take_why": "fz_take_why", "fzpost_outcome_gate": "fzpost_outcome_gate",
            "card_out_run": "card_out_run", "card_wick_depth": "card_wick_depth", "card_touches": "card_touches",
            "fnd_net_inr": "fnd_net_inr", "fnd_pts": "fnd_pts", "fnd_exit_reason": "fnd_exit_reason", "fnd_exit_i": "fnd_exit_i",
            "fzpos_kind": "fzpos_kind", "fzpos_net_inr": "fzpos_net_inr"}
    TMAP = {"entry_i": "entry_i", "exit_i": "exit_i", "exit_px": "exit_px", "pts": "pts", "net_inr": "net_inr", "charges_inr": "charges_inr",
            "exit_reason": "exit_reason", "sl": "sl", "mfe_pts": "mfe_pts", "mae_pts": "mae_pts"}
    ZMAP = {"id": "id", "lo": "lo", "hi": "hi", "birth_bar": "birth_bar", "retired_bar": "retired_bar", "retired_by": "retired_by", "touches": "touches"}
    old_fz_setup = old_fzt.setup_i; new_fz_setup = new_fzt.setup_i
else:
    old_f = rd(OLD, "setup_features"); old_tr = rd(OLD, "trades"); old_fzt = rd(OLD, "fz_trades"); old_card = rd(OLD, "card")
    old_led = rd(OLD, "ledger"); old_z = rd(OLD, "zones"); old_ev = rd(OLD, "events"); old_sw = rd(OLD, "swings")
    old_z = old_z.rename(columns={"zone_id": "id"})
    old_ev = old_ev.rename(columns={"i": "i"})
    FMAP = {"setup_i": "setup_i", "dir": "dir", "session_i": "session_idx", "session_bar": "session_bar", "ch": "choch_i", "close": "close",
            "sl": "sl", "sl_dist_pts": "sl_dist_pts", "atr14": "atr14", "reg_n_choch_since_bos": "n_choch_since_bos",
            "reg_n_bos_since_choch": "n_bos_since_choch", "reg_bars_since_bos": "bars_since_bos", "reg_alt6": "alt_dir6",
            "reg_n_choch_60": "n_choch_1h", "reg_n_bos_60": "n_bos_1h", "reg_range60_atr": None, "reg_session_range_atr": "sess_range_atr",
            "reg_pos_in_session_range": "pos_in_session_range", "reg_range_since_choch_atr": "range_since_choch_atr",
            "reg_prior_setups_today": "today_n_setups_before", "reg_prior_closed_pts_today": None,
            "vol_bar": "vol", "vol_ratio20": "vol_ratio20", "vol_ratio60": "vol_ratio60", "vol_med20_prior": "vol_med20_prior",
            "vol_sess_cumvol_ratio20s": "sess_cumvol_ratio20s", "vol_max_ratio20_5": "vol_max_ratio20_5", "vol_max_ratio20_15": "vol_max_ratio20_15",
            "vol_hv2_bars_ago": "hv2_bars_since", "vol_hv3_bars_ago": "hv3_bars_since", "vol_hv3_dir": "hv3_dir", "vol_hv3_ratio": "hv3_ratio",
            "vol_ratio20_at_choch": "vol_ratio20_at_choch", "vol_max_ratio20_choch_to_k": "vol_max_ratio20_choch_to_k",
            "lvl_prot": "prot_lvl", "lvl_prot_dist_dir_atr": "dist_prot_dir_atr", "lvl_choch_dist_dir_atr": "dist_choch_lvl_atr",
            "lvl_n_rooms_alive": "n_rooms_alive", "lvl_room_edge": "room_edge", "lvl_room_edge_dist_dir_atr": "room_edge_dist_dir_atr",
            "lvl_room_ahead_dist_atr": "room_ahead_dist_atr", "lvl_room_behind_dist_atr": "room_behind_dist_atr",
            "lvl_last_sh": "last_sh_px", "lvl_last_sl": "last_sl_px", "lvl_last_sh_age": "last_sh_bars_ago", "lvl_last_sl_age": "last_sl_bars_ago",
            "lvl_swing_ahead_dist_atr": "swing_ahead_dist_atr", "lvl_swing_near_kind": "swing_near_kind",
            "lvl_touch_prot_n60": "touch_prot_n", "lvl_touch_prot_last": "touch_prot_last", "lvl_touch_room_n60": "touch_room_n",
            "lvl_touch_room_last": "touch_room_last", "lvl_touch_swing_n60": "touch_swing_n", "lvl_touch_swing_last": "touch_swing_last",
            "card_zone_id": "card_zone_id", "card_visit_n": "card_visit_n", "card_this_bars": "card_this_bars", "card_read": "card_read",
            "card_out_run": "card_out_run", "card_wick_depth": "card_wick_depth", "card_touches": "card_touches", "card_in_id": "card_in_id",
            "st7_gate": "fz_gate", "st7_block_reason": "fz_block_reason", "st7_branch": "fz_branch", "st7_take_why": "fz_take_why",
            "st7_outcome_gate": "fzpost_outcome_gate", "st7_traded": "fz_traded",
            "fnd_net": "fnd_net_inr", "fnd_pts": "fnd_pts", "fnd_exit_reason": "fnd_exit_reason", "fnd_mfe": "fnd_mfe_pts", "fnd_mae": "fnd_mae_pts",
            "hour_bin": "hour_bin"}
    TMAP = {"entry": "entry_i", "exit": "exit_i", "exit_px": "exit_px", "pts": "pts", "net": "net_inr", "charges": "charges_inr",
            "exit_reason": "exit_reason", "sl": "sl", "mfe": "mfe_pts", "mae": "mae_pts"}
    ZMAP = {"id": "id", "lo": "lo", "hi": "hi", "birth_bar": "birth_bar", "retired_bar": "retired_bar", "retired_by": "retired_by", "touches": "touches"}
    old_fz_setup = old_fzt.setup_i; new_fz_setup = new_fzt.setup_i

R["old"] = dict(setups=len(old_f), trades=len(old_tr), fz_positions=len(old_fzt), rooms=len(old_z), events=len(old_ev), swings=len(old_sw))
R["setups_identical"] = bool((old_f.setup_i.to_numpy() == new_f.setup_i.to_numpy()).all()) if len(old_f) == len(new_f) else False
R["fz_position_setups_identical"] = sorted(old_fz_setup.astype(int)) == sorted(new_fz_setup.astype(int))
# trades
tr_cmp = {}
o_ = old_tr.sort_values(list(TMAP)[0]).reset_index(drop=True); n_ = new_tr.sort_values("entry_i").reset_index(drop=True)
for a, b in TMAP.items():
    ok, why = same_vals(o_[a], n_[b], tol=1e-6); tr_cmp[f"{a}->{b}"] = "identical" if ok else why
R["trades"] = tr_cmp
# fz trades
fo = old_fzt.sort_values(list(TMAP)[0]).reset_index(drop=True); fn = new_fzt.sort_values("entry_i").reset_index(drop=True)
fz_cmp = {}
if len(fo) == len(fn):
    for a, b in TMAP.items():
        if a not in fo.columns: fz_cmp[f"{a}->{b}"] = "not in the local table"; continue
        ok, why = same_vals(fo[a], fn[b]); fz_cmp[f"{a}->{b}"] = "identical" if ok else why
    for col in ("gate", "zone_id", "fill_used", "reenter_reason"):
        ok, why = same_vals(fo[col], fn[col]); fz_cmp[col] = "identical" if ok else why
else: fz_cmp["length"] = f"{len(fo)} vs {len(fn)}"
R["fz_trades"] = fz_cmp
# card (per bar)
cc = {}
for col in ("zone_id", "visit_n", "this_bars", "read", "left_id", "out_run", "in_id", "wick_depth", "touches", "cluster_sit", "leave_vol_ok"):
    ok, why = same_vals(old_card[col], new_card[col]); cc[col] = "identical" if ok else why
R["card"] = cc
# zones
zo = old_z.sort_values("birth_bar").reset_index(drop=True); zn = new_z.sort_values("birth_bar").reset_index(drop=True)
zc = {}
if len(zo) == len(zn):
    for a, b in ZMAP.items():
        ok, why = same_vals(zo[a], zn[b]); zc[a] = "identical" if ok else why
else: zc["length"] = f"{len(zo)} vs {len(zn)}"
R["zones"] = zc
# events / swings
R["events_identical"] = bool(len(old_ev) == len(new_ev) and (old_ev.i.to_numpy() == new_ev.i.to_numpy()).all() and (old_ev.kind.astype(str).to_numpy() == new_ev.kind.astype(str).to_numpy()).all())
R["swings_identical"] = bool(len(old_sw) == len(new_sw) and (old_sw.bar.to_numpy() == new_sw.bar.to_numpy()).all() and np.allclose(old_sw.price.to_numpy(dtype=float), new_sw.price.to_numpy(dtype=float)))
# features
fc = {}
of = old_f.sort_values("setup_i").reset_index(drop=True); nf = new_f.sort_values("setup_i").reset_index(drop=True)
for a, b in FMAP.items():
    if b is None or a not in of.columns or b not in nf.columns: fc[a] = f"not compared (old {a in of.columns}, new {b in nf.columns if b else None})"; continue
    ok, why = same_vals(of[a], nf[b], tol=1e-3)
    fc[f"{a}->{b}"] = "identical" if ok else why
R["features"] = fc
R["new_feature_columns_not_in_old"] = len(set(nf.columns) - set(FMAP.values()))
json.dump(R, open(os.path.join(NEW, "compare.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in R.items() if k not in ("features",)}, indent=1, default=str))
print("features differing:", {k: v for k, v in fc.items() if v != "identical"})
