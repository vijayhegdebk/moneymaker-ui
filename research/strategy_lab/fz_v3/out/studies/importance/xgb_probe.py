import sys, time, os
sys.path.insert(0, "/home/user/money-maker/research/strategy_lab/fz_v3/out")
import numpy as np, harness as H, xgboost as xgb
T = H.load("5minute"); X, _ = H.design(T); is_idx = np.flatnonzero(T.is_mask)
Xn = X.to_numpy()[is_idx][:, :40]; y = T.win[is_idx].astype(int)
for nj in (1, 2, 4):
    t0 = time.time(); xgb.XGBClassifier(max_depth=3, n_estimators=200, learning_rate=0.05, tree_method="hist", n_jobs=nj).fit(Xn, y); print("5m n_jobs", nj, round(time.time()-t0, 1), "s", flush=True)
T = H.load("minute"); X, _ = H.design(T); is_idx = np.flatnonzero(T.is_mask)
Xn = X.to_numpy()[is_idx][:, :40]; y = T.win[is_idx].astype(int)
for nj in (1, 4):
    t0 = time.time(); xgb.XGBClassifier(max_depth=3, n_estimators=200, learning_rate=0.05, tree_method="hist", n_jobs=nj).fit(Xn, y); print("1m n_jobs", nj, round(time.time()-t0, 1), "s", flush=True)
