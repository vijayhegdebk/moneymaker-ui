"""Label-free diagnostics for FINDINGS section 7b: where in the session the chop states sit (explains a within-session statistic
such as the session-matched control / SPA gain against the between-session checks). Reads hour_bin, today_n_setups_before and the
session's SETUP count (the last flag is post-SETUP information, used only to describe the control's mechanics, never as a feature).
No label is read, no ledger row is written; appends `diagnostics` to results.json."""
import os, sys, json
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rg_lib as R
H = R.H
T = H.load(R.TF, R.LABEL); is_idx = np.flatnonzero(T.is_mask); ext = R.load_ext(R.TF)
res = json.load(open(os.path.join(HERE, "results.json")))
F = T.F.iloc[is_idx].reset_index(drop=True)
cnt = F.groupby("session_idx").setup_i.transform("count").to_numpy()
rank = F.today_n_setups_before.to_numpy(dtype=float)
last = (rank + 1 >= cnt)                                 # the session's last L1 unit (post-SETUP fact; diagnostic only)
hour = F.hour_bin.astype(str).to_numpy()
diag = {}
for m in R.MODEL_ORDER:
    P = R.posterior_matrix(ext, m, T.setup_i[is_idx]); mp = np.argmax(P, axis=1); chop = res["fixed_rule"][m]["chop"]
    inchop = mp == chop
    by_hour = {h: dict(n=int((hour == h).sum()), chop_share=round(float(inchop[hour == h].mean()), 3)) for h in sorted(set(hour))}
    by_rank = {str(int(r)): dict(n=int((rank == r).sum()), chop_share=round(float(inchop[rank == r].mean()), 3)) for r in sorted(set(rank)) if (rank == r).sum() >= 10}
    diag[m] = dict(chop=chop, chop_share_all=round(float(inchop.mean()), 3),
                   chop_share_last_unit_of_session=round(float(inchop[last].mean()), 3), chop_share_not_last=round(float(inchop[~last].mean()), 3),
                   chop_share_single_unit_sessions=round(float(inchop[cnt == 1].mean()), 3), chop_share_multi_unit_sessions=round(float(inchop[cnt > 1].mean()), 3),
                   n_last=int(last.sum()), n_single=int((cnt == 1).sum()), by_hour_bin=by_hour, by_rank_in_session=by_rank,
                   mean_session_bar_chop=round(float(F.session_bar.to_numpy()[inchop].mean()), 1), mean_session_bar_other=round(float(F.session_bar.to_numpy()[~inchop].mean()), 1))
    print(m, json.dumps({k: v for k, v in diag[m].items() if k not in ("by_hour_bin", "by_rank_in_session")}))
    print("  by hour", {h: v["chop_share"] for h, v in by_hour.items()})
    print("  by rank", {r: v["chop_share"] for r, v in by_rank.items()})
res["diagnostics"] = dict(note="label-free; the 'last unit of the session' flag is post-SETUP information used only to describe the session-matched control's mechanics (session_stop FINDINGS R.3), never as a feature", per_model=diag)
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
print("appended diagnostics to results.json")
