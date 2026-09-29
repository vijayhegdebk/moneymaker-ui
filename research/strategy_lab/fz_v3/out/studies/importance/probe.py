import sys, time, os, resource
sys.path.insert(0, "/home/user/money-maker/research/strategy_lab/fz_v3/out")
import numpy as np, pandas as pd
import harness as H
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb, shap, sklearn
print("versions", sklearn.__version__, xgb.__version__, shap.__version__)
T = H.load("minute"); X, src = H.design(T)
E = pd.read_parquet("/home/user/money-maker/research/strategy_lab/fz_v3/out/features_ext/minute/ext_features.parquet").set_index("setup_i").reindex(T.setup_i).reset_index(drop=True)
Xa = pd.concat([X, E], axis=1)
is_idx = np.flatnonzero(T.is_mask)
Xi = Xa.iloc[is_idx]; med = Xi.median()
Xf = Xi.fillna(med).to_numpy(); y = T.win[is_idx].astype(int); w = np.minimum(np.abs(T.net[is_idx]), np.quantile(np.abs(T.net[is_idx]), .99)); w = w / w.mean()
t0 = time.time()
bag = BaggingClassifier(DecisionTreeClassifier(max_depth=4, min_weight_fraction_leaf=0.05, class_weight="balanced"), n_estimators=300, oob_score=True, n_jobs=4, random_state=0)
bag.fit(Xf, y, sample_weight=w)
print("fit s", round(time.time()-t0, 1), "oob shape", bag.oob_decision_function_.shape, "nan in oob", np.isnan(bag.oob_decision_function_).sum())
t0 = time.time()
for _ in range(10): p = bag.predict_proba(Xf[:400])
print("10 predict_proba(400) s", round(time.time()-t0, 2))
# manual predict via estimators_ + estimators_features_
t0 = time.time()
for _ in range(10):
    acc = np.zeros(400)
    for est, feats in zip(bag.estimators_, bag.estimators_features_):
        acc += est.predict_proba(Xf[:400][:, feats])[:, 1]
    acc /= len(bag.estimators_)
print("10 manual predict s", round(time.time()-t0, 2), "max diff", np.abs(acc - p[:, 1]).max())
# xgb + shap
t0 = time.time()
Xn = Xi.to_numpy()[:, :40]
m = xgb.XGBClassifier(max_depth=3, n_estimators=200, learning_rate=0.05, n_jobs=4, tree_method="hist", random_state=0)
m.fit(Xn, y, sample_weight=w)
print("xgb fit s", round(time.time()-t0, 1))
t0 = time.time()
ex = shap.TreeExplainer(m)
iv = ex.shap_interaction_values(Xn[:400])
print("shap interaction s", round(time.time()-t0, 1), "shape", np.asarray(iv).shape)
df = m.get_booster().trees_to_dataframe(); print(df.head(3).to_string()); print(df.columns.tolist())
print("maxrss MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
