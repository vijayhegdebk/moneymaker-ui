"""N4 cross-check (repair round): the stratified within-hour_bin difference of session_stop_repair.strat_diff must equal the OLS
coefficient of net on the state indicator with hour_bin fixed effects (statsmodels); its session-cluster-robust SE and p are set
beside the session-block bootstrap sd and p of repair_null_tests_<tf>_L1.csv. Writes repair_n4_ols_crosscheck_<tf>.csv for every
timeframe whose repair table exists. Run after session_stop_repair.py; no ledger row (a check of the test statistic, not a candidate).

    python n4_ols_crosscheck.py
"""
import os, sys, warnings
sys.dont_write_bytecode = True; warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT); sys.path.insert(0, HERE)
import numpy as np, pandas as pd, statsmodels.api as sm
import harness as H, session_stop as SS, session_stop_repair as RP

for tf in ("minute", "5minute"):
    tab = os.path.join(HERE, f"repair_null_tests_{tf}_L1.csv")
    if not os.path.exists(tab): print(f"{tf}: no repair table yet"); continue
    boot = pd.read_csv(tab).set_index("test")
    T = H.load(tf, "L1"); rows = np.flatnonzero(T.is_mask); S = SS.session_frame(T, rows)
    hbc = np.array([RP.HB_CODE[h] for h in S["hour_bin"]]); net = S["net"]; sess = S["sess"]
    D = pd.get_dummies(pd.Series(hbc), prefix="h", drop_first=True).astype(float)
    out = []
    for name, cond in [(f"stops>={k}", S["today_stops"] >= k) for k in SS.K_TESTS] + [(f"net<={int(L)}", S["today_net"] <= L) for L in SS.L_TESTS]:
        if not cond.any() or cond.all(): continue
        X = sm.add_constant(pd.concat([pd.Series(cond.astype(float), name="state"), D], axis=1))
        m = sm.OLS(net, X).fit(cov_type="cluster", cov_kwds={"groups": sess})
        out.append(dict(tf=tf, test=name, strat_diff=RP.strat_diff(hbc, cond, net), ols_coef=m.params["state"], cluster_se=m.bse["state"], cluster_p=m.pvalues["state"],
                        boot_sd=boot.loc[name, "N4_boot_sd"], boot_p=boot.loc[name, "N4_p"]))
    df = pd.DataFrame(out).round(4); print(df.to_string(index=False))
    assert np.allclose(df.strat_diff, df.ols_coef, atol=1e-6), "the stratified statistic must equal the fixed-effects OLS coefficient"
    df.to_csv(os.path.join(HERE, f"repair_n4_ols_crosscheck_{tf}.csv"), index=False)
