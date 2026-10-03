"""Causality check: the build on the bars up to a cut (build.py --truncate) against the full build. For every SETUP at or
before the cut, every as-of column of the feature table must be identical; the per-bar tables (bars, fz_card) and the
as-of columns of the engine / FZ tables must be identical up to the cut. Only the labels and post-SETUP columns may differ.

    python trunc_diff.py --tf minute --cut "2025-06-30 12:00:00"
"""
import os, sys, json, argparse
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import harness as H                                                   # the as-of allowlist (LABEL_PREFIX / NOT_FEATURES)
ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); ap.add_argument("--cut", required=True); A = ap.parse_args()
FULL = os.path.join(HERE, "..", "data", A.tf)
TR = os.path.join(FULL, "trunc_" + A.cut.replace("-", "").replace(":", "").replace(" ", "_"))
rd = lambda folder, name: pd.read_parquet(os.path.join(folder, name + ".parquet"))
R = {}

def same(a, b):
    a = a.reset_index(drop=True); b = b.reset_index(drop=True)
    if len(a) != len(b): return False
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
        x, y = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
        return bool(np.all((np.isnan(x) & np.isnan(y)) | (np.abs(x - y) <= 1e-9)))
    return bool((a.astype(object).map(str) == b.astype(object).map(str)).all())

bf, bt = rd(FULL, "bars"), rd(TR, "bars")
nb = len(bt); R["bars_truncated"] = nb; R["cut_time"] = A.cut
R["bars_identical_cols"] = {c: same(bf[c].iloc[:nb], bt[c]) for c in ("atr14", "prot", "vol_med20_prior", "vol_ratio20", "sess_cumvol_ratio20s", "fm_na")}
cf, ct = rd(FULL, "fz_card"), rd(TR, "fz_card")
R["card_identical_cols"] = {c: same(cf[c].iloc[:nb], ct[c]) for c in cf.columns if c not in ("i", "time")}
ff, ft = rd(FULL, "features"), rd(TR, "features")
ff = ff[ff.setup_i < nb].reset_index(drop=True); ft = ft.reset_index(drop=True)
R["setups_before_cut"] = [len(ff), len(ft)]
asof = [c for c in ff.columns if not c.startswith(H.LABEL_PREFIX) and c != "fz_traded"]
labels = [c for c in ff.columns if c.startswith(H.LABEL_PREFIX) or c == "fz_traded"]
R["asof_columns"] = len(asof); R["asof_differ"] = [c for c in asof if not same(ff[c], ft[c])]
R["label_columns_differ"] = [c for c in labels if not same(ff[c], ft[c])]
sf, st_ = rd(FULL, "swings"), rd(TR, "swings")
sf = sf[sf.conf_bar < nb].reset_index(drop=True)
R["swings_identical_asof"] = len(sf) == len(st_) and all(same(sf[c], st_[c]) for c in ("kind", "bar", "price", "conf_bar"))
ef, et = rd(FULL, "events"), rd(TR, "events")
ef = ef[ef.i < nb].reset_index(drop=True)
R["events_identical_asof"] = len(ef) == len(et) and all(same(ef[c], et[c]) for c in ("i", "kind", "dir", "flip", "lvl"))
tf_, tt = rd(FULL, "trades"), rd(TR, "trades")
closed = tf_[(tf_.exit_i < nb - 1) & (~tf_.open.astype(bool))].reset_index(drop=True); tt2 = tt[tt.entry_i.isin(closed.entry_i)].reset_index(drop=True)
R["closed_trades_identical"] = len(closed) == len(tt2) and all(same(closed[c], tt2[c]) for c in ("entry_i", "exit_i", "exit_px", "pts", "net_inr", "exit_reason"))
zf, zt = rd(FULL, "fz_zones"), rd(TR, "fz_zones")
zf = zf[zf.birth_bar < nb].reset_index(drop=True)
R["rooms_identical_asof"] = len(zf) == len(zt) and all(same(zf[c], zt[c]) for c in ("id", "lo", "hi", "birth_bar"))
lf, lt = rd(FULL, "fz_ledger"), rd(TR, "fz_ledger")
lf = lf[lf.i < nb].reset_index(drop=True)
gate_cols = ["zone_id", "read", "gate", "block_reason", "branch", "take_why", "entered_read", "watch_kind"]
R["ledger_gate_identical"] = len(lf) == len(lt) and all(same(lf[c], lt[c]) for c in gate_cols)
R["ledger_gate_differ"] = [c for c in gate_cols if len(lf) == len(lt) and not same(lf[c], lt[c])]
ok = (all(R["bars_identical_cols"].values()) and all(R["card_identical_cols"].values()) and not R["asof_differ"] and R["swings_identical_asof"]
      and R["events_identical_asof"] and R["closed_trades_identical"] and R["rooms_identical_asof"] and R["ledger_gate_identical"])
R["PASS"] = bool(ok)
json.dump(R, open(os.path.join(TR, "trunc_diff.json"), "w"), indent=1, default=str)
print(json.dumps(R, indent=1, default=str))
