"""Causality check and finalisation of the extended features: the same builder run on the truncated data (bars up to the cut,
same fit window) must reproduce every column for every SETUP before the cut. A column that differs is dropped and the reason
recorded; the surviving columns are written to features_ext/<tf>/ext_features.parquet; trunc_diff.json carries the per-column result.

    python finalize.py --tf minute
"""
import os, sys, json, argparse
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
CUT = "trunc_20250630_120000"
TOL = 1e-9

ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); A = ap.parse_args()
FE = os.path.join(OUT, "features_ext", A.tf)
full = pd.read_parquet(os.path.join(FE, "ext_features_all.parquet"))
trunc = pd.read_parquet(os.path.join(FE, CUT, "ext_features_all.parquet"))
nb = len(pd.read_parquet(os.path.join(OUT, "data", A.tf, CUT, "bars.parquet"), columns=["i"]))
full_pre = full[full.setup_i < nb].reset_index(drop=True); trunc = trunc.reset_index(drop=True)
R = dict(tf=A.tf, cut=CUT, bars_truncated=int(nb), setups_before_cut=[int(len(full_pre)), int(len(trunc))],
         same_setup_keys=bool(np.array_equal(full_pre.setup_i.to_numpy(), trunc.setup_i.to_numpy())), tolerance=TOL, columns={}, dropped=[], kept=[])
assert R["same_setup_keys"], "the truncated build must contain exactly the SETUPs before the cut"
for c in full.columns:
    if c == "setup_i": continue
    if c not in trunc.columns:
        R["columns"][c] = dict(identical=False, reason="column missing in the truncated build"); R["dropped"].append(c); continue
    x, y = full_pre[c].to_numpy(dtype=float), trunc[c].to_numpy(dtype=float)
    nan_eq = bool(np.array_equal(np.isnan(x), np.isnan(y)))
    both = ~np.isnan(x) & ~np.isnan(y)
    mad = float(np.max(np.abs(x[both] - y[both]))) if both.any() else 0.0
    n_diff = int(np.sum(np.abs(x[both] - y[both]) > TOL)) + int(np.sum(np.isnan(x) != np.isnan(y)))
    ident = nan_eq and mad <= TOL
    R["columns"][c] = dict(identical=ident, nan_pattern_equal=nan_eq, max_abs_diff=mad, rows_differing=n_diff)
    if ident: R["kept"].append(c)
    else:
        R["columns"][c]["reason"] = f"differs on {n_diff} SETUPs before the cut (max |diff| {mad:.3g}); not reproducible from bars <= k with the frozen fit -> dropped"
        R["dropped"].append(c)
# the fitted quantities themselves must agree (same fit window, fully before the cut)
rf = json.load(open(os.path.join(FE, "ext_fit_report.json"))); rt = json.load(open(os.path.join(FE, CUT, "ext_fit_report.json")))
fits = {}
for name in ("close", "vol"):
    fits[f"ffd_{name}_dstar_used"] = [rf["ffd"][name]["d_star_used"], rt["ffd"][name]["d_star_used"]]
for K in ("K3", "K4"):
    fits[f"hmm_{K}_state_means_equal"] = rf["hmm"][K]["state_means"] == rt["hmm"][K]["state_means"]
    fits[f"gmm_{K}_state_means_equal"] = rf["gmm"][K]["state_means"] == rt["gmm"][K]["state_means"]
    fits[f"jump_{K}_lambda"] = [rf["jump"][K]["lambda_star"], rt["jump"][K]["lambda_star"]]
    fits[f"jump_{K}_state_means_equal"] = rf["jump"][K]["state_means"] == rt["jump"][K]["state_means"]
fits["bocpd_fit_stats_equal"] = all(rf["bocpd"][s][k] == rt["bocpd"][s][k] for s in ("ret", "rng") for k in ("fit_mean", "fit_std"))
fits["rv_fit_stats_equal"] = rf["rv_fit_stats"] == rt["rv_fit_stats"]
R["fit_agreement"] = fits
R["PASS_all_columns"] = not R["dropped"]
final = full[["setup_i"] + R["kept"]]
final.to_parquet(os.path.join(FE, "ext_features.parquet"), index=False)
R["final_shape"] = list(final.shape)
json.dump(R, open(os.path.join(FE, "trunc_diff.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in R.items() if k != "columns"}, indent=1, default=str))
print("max |diff| by column:", {c: round(v["max_abs_diff"], 12) for c, v in R["columns"].items() if v.get("max_abs_diff", 0) > 0})
