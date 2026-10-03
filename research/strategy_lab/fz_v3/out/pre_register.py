"""Pre-registration run (before any candidate is scored): the splitter checks, the break tests of the book's own expectancy
(they decide the time-decay weighting and the OOS caveat), the raw Foundation book and the frozen ST7/ST8 gate on both labels
and both timeframes (the comparators every OOS table carries). Writes results/pre_registration.json and the first ledger rows.

    python pre_register.py
"""
import os, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import harness as H

out = {}
for tf in ("minute", "5minute"):
    for label in ("L1", "L0"):
        T = H.load(tf, label)
        rows = np.flatnonzero(T.is_mask)
        raw = dict(units_is=int(len(rows)), units_oos=int(T.oos_mask.sum()), is_net=round(float(T.net[rows].sum()), 2),
                   is_mean=round(float(T.net[rows].mean()), 2), is_win_rate=round(float(T.win[rows].mean()), 4),
                   is_active_sessions=int(len(T.active_sessions)), is_sessions_median_setups=float(np.median(np.bincount(T.session[rows])[np.bincount(T.session[rows]) > 0])),
                   top_decile_winner_share_of_gross_wins=round(float(np.sort(T.net[rows][T.win[rows]])[-max(1, int(0.1 * T.win[rows].sum())):].sum() / T.net[rows][T.win[rows]].sum()), 4),
                   mean_cost_inr=round(float((T.F.loc[rows, ("l1_cost_inr" if label == "L1" else "fnd_cost_inr")].to_numpy(dtype=float)).mean()), 2))
        frozen = T.F.fz_traded.astype(bool).to_numpy()
        fz = H.score(T, frozen, "comparator/frozen_st7_st8", dict(gate="ST7/ST8 as traded (fz_traded)"), script=__file__, note="the frozen v2 gate, the comparator")
        rec = dict(splits=H.check_splits(T) if label == "L1" else None, raw_book=raw,
                   frozen_gate={k: fz[k] for k in ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "kept_mean_slip8",
                                                    "perm_p", "control_pct", "loser_recall", "loser_precision", "winner_recall", "winner_recall_weighted",
                                                    "top_decile_winners_skipped", "sign_blocks", "kept_pf")},
                   frozen_go_no_go=H.go_no_go(fz, tf)[1])
        if label == "L1": rec["break_tests"] = H.break_tests(T)
        out[f"{tf}/{label}"] = rec
        print(tf, label, "units", raw["units_is"], "mean", raw["is_mean"], "| frozen diff", fz["diff"], "pct", fz["control_pct"], "p", fz["perm_p"], flush=True)
out["go_no_go_rule"] = H.GO
out["ledger_sha_after"] = H.ledger_sha()
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "pre_registration.json"), "w"), indent=1, default=str)
print("written results/pre_registration.json")
