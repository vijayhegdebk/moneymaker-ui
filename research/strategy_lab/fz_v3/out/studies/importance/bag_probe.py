import sys, time, os
sys.path.insert(0, "/home/user/money-maker/research/strategy_lab/fz_v3/out")
import numpy as np, harness as H
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
T = H.load("minute"); X, _ = H.design(T); is_idx = np.flatnonzero(T.is_mask)
Xn = np.nan_to_num(X.to_numpy()[is_idx]); y = T.win[is_idx].astype(int)
for nj in (1, 4):
    t0 = time.time(); BaggingClassifier(DecisionTreeClassifier(max_depth=4, min_weight_fraction_leaf=0.05, class_weight="balanced"), n_estimators=300, oob_score=True, n_jobs=nj, random_state=0).fit(Xn, y); print("1m bagging n_jobs", nj, round(time.time()-t0, 1), "s", flush=True)
