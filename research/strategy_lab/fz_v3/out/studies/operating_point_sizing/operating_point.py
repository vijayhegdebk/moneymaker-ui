"""operating_point_sizing, step 1: the OPERATING POINT of the gate_family finalists (DESIGN_PANEL quant-ml-canon-conformal-skip
merged with decision-making-4-selective-gate-conformal-risk-control; Judge 2's merge, both judges' caveats binding). IS only.

THIS STEP ADDS NO OOS CANDIDATE. It re-parameterises the gate_family sub-family finalists' OOF scores (a threshold on a score
another study produced is not a gate: Judge 1); gate_family itself wrote NO candidate (null on both timeframes), so every kept
book here is a re-parameterisation of a gate that already failed harness.go_no_go. Every threshold evaluated for a kept-vs-skipped
number is a harness.score row (family operating_point/<sub>); the kept-vs-skipped numbers below come from those rows only.

Inputs   studies/gate_family/results/oof_<tf>.parquet: the 12-block purged OOF probability p (column `p`) of every probability
         learner of the two sub-families ((I) context: hour_bin one-hot + dir, inside the frozen vocabulary; (II) h5_full: the
         full as-of table, OUTSIDE THE FROZEN SHORTLIST (importance rule failed for every cluster)). Scored models = the
         deployable scorecard of each sub-family (Platt-mapped integer score -> p, per fold) and the HGB classifier (the
         gradient-boosting ceiling / the (I) finalist on minute). The policy trees (pt1-3, the 5minute (I) finalist pt2) and the
         H5 rule list carry no score: they cannot be thresholded and are not here (stated in FINDINGS).
Score    s = 1 - p (nonconformity of the label 'win'). Everything is a threshold on s; keep iff s <= threshold.
Labels   L1 (harness.load(tf)); folds = harness blocks (the OOF parquet's `fold` equals T.block on every IS row, asserted).

(1) Cross-conformal, Mondrian by class (winner coverage): for fold f, calibration = the OOF scores of the TRUE WINNERS of the
    other 11 folds; q_alpha = the ceil((n_win + 1)(1 - alpha))-th smallest; the prediction set of a fold-f row contains 'win' iff
    s <= q_alpha; skip iff 'win' is not in the set. alpha in {0.05, 0.10, 0.15, 0.20, 0.30}. Reported per fold: nominal alpha vs
    empirical OOF winner coverage (count and |net|-weighted), kept share; pooled: the ledger row (controls on). CV+ caveat (Judge
    2): the calibration scores come from models that saw fold f, so the finite-sample guarantee is the weaker cross-conformal /
    CV+ form (about 1 - 2 alpha), not 1 - alpha; both are printed next to the empirical coverage.
    Time-bin taxonomy (class x bin; minute only, Judge 2): bins 09:15-10:29 / 10:30-12:59 / 13:00-15:19 by the SETUP bar's clock
    (`time`; the bins do not align with hour_bin's edges, so the taxonomy reads the clock, an identity column - a deployable
    form would need a clock key); calibration winners and q_alpha per bin.
    ACI (Gibbs & Candes 2021), winner-conditional: rows in time order; alpha_{t+1} = alpha_t + gamma (alpha - err_t) updated at
    every TRUE WINNER row (err_t = 1 when that winner was skipped), gamma in {0.005, 0.01}; the quantile at row t is the
    Mondrian quantile at level alpha_t over the OOF scores of the winners seen BEFORE t (expanding window; first ACI_BURN_IN
    winners: keep everything, counted); alpha_t clipped to [0, 1] (alpha_t <= 0 keeps everything, >= 1 skips everything).
    Its final state (alpha_T, q_T, n winners) is what oos_once would carry forward; no OOS row is read.
(2) Selective risk-coverage curve: coverage c in {0.10, 0.15, ..., 1.00}; nested: the fold-f threshold is the c-quantile of s over
    the other 11 folds' rows; selective risk = mean of min(max(-net, 0), 6000) among kept; the loser share among kept; the
    realised coverage. Every c is a ledger row (controls off: trials).
(3) Conformal Risk Control (Angelopoulos, Bates, Candes, Jordan & Lei 2022) with SESSIONS as units: calibration block = the last
    200 IS sessions with a SETUP (n stated as sessions-with-SETUPs; the OOF scores of its rows come from the purged folds, so the
    block is not disjoint in time from every score's training folds - the CV+ caveat again, stated); for coverage lambda on the
    grid the threshold is the lambda-quantile of s over the block's rows; per session r_s(lambda) = mean clipped loss of the
    session's kept units (0 when none kept: no trade, no loss); R_hat = mean over the n sessions; certificate =
    (n R_hat + B) / (n + 1), B = 6000; lambda* = the largest lambda with certificate <= alpha, alpha in {800, 1000, 1200} INR
    (the cost level); the gate s <= threshold(lambda*) on all IS is a ledger row (controls on); the realised risk on the IS rows
    before the block is reported beside the certificate. Per-bin certificates on minute only (dropped on 5m: Judge 2).
(4) Cost-aware Pareto front: for every coverage-curve row U_w = kept net - w x sum over skipped of max(net, 0), w in {0, 0.5, 1};
    winner-net retained = kept winners' net / all winners' net (the row's winner_recall_weighted); loser-net avoided = skipped
    losers' |net| / all losers' |net|; the non-dominated points are flagged; the argmax per w is printed for the user to pick
    (Rule 0(c)). Nothing is chosen here.
(5) Cost sensitivity of every kept book: kept mean at 3 / 5 / 8 pts slippage per side (the ledger row's kept_mean_slip3 /
    kept_mean / kept_mean_slip8) and with the brokerage cap of 20 INR per order replaced by uncapped 0.03% (lab.trade_charges with
    brokerage_cap = inf, slippage 5); the harness item is kept_mean_slip8 > 0.

Family: operating_point/<conformal | conformal_timebin | aci | coverage | crc | crc_timebin>; PBO (diff), SPA, effective trials,
DSR over every operating_point row of the timeframe; harness.go_no_go on the best row with null_tape = 'not run: this step adds no
candidate' (fails by design) and the model's source columns declared.
"""
import os, sys, json, math, time, argparse, datetime as D
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402
import lab                                                              # noqa: E402  trade_charges only (via harness.LAB path)

ALPHAS = [0.05, 0.10, 0.15, 0.20, 0.30]
GAMMAS = [0.005, 0.01]
ACI_BURN_IN = 30
COVERAGES = [round(0.10 + 0.05 * i, 2) for i in range(19)]             # 0.10 .. 1.00
CRC_LAMBDAS = [round(0.05 * i, 2) for i in range(1, 21)]                # 0.05 .. 1.00
CRC_ALPHAS = [800.0, 1000.0, 1200.0]
CRC_SESSIONS = 200
CLIP_B = 6000.0
W_GRID = [0.0, 0.5, 1.0]
BINS = [("09:15-10:29", 0, 630), ("10:30-12:59", 630, 780), ("13:00-15:19", 780, 10 ** 6)]
MODELS = [("context", "hgbc"), ("context", "scorecard"), ("h5_full", "hgbc"), ("h5_full", "scorecard")]
VOCAB = {"context": "inside the frozen vocabulary (context columns)",
         "h5_full": "outside the frozen shortlist (importance rule failed for every cluster)"}
ROLE = {("minute", "context", "hgbc"): "finalist of sub-family (I) (hgbc -> distilled tree; this is the hgbc OOF p)",
        ("minute", "context", "scorecard"): "the deployable scorecard of sub-family (I)",
        ("minute", "h5_full", "scorecard"): "finalist of sub-family (II) (scorecard -> distilled tree; this is the scorecard OOF p)",
        ("minute", "h5_full", "hgbc"): "gradient-boosting ceiling of sub-family (II) (reference)",
        ("5minute", "context", "hgbc"): "probability learner of sub-family (I) (its finalist pt2 is a policy tree with no score)",
        ("5minute", "context", "scorecard"): "the deployable scorecard of sub-family (I)",
        ("5minute", "h5_full", "scorecard"): "finalist of sub-family (II) (scorecard -> distilled rules; this is the scorecard OOF p)",
        ("5minute", "h5_full", "hgbc"): "gradient-boosting ceiling of sub-family (II) (reference)"}
GF_RES = os.path.join(OUT, "studies", "gate_family", "results")


def log(*a):
    print(D.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def r2(x): return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 2)
def r4(x): return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 4)


def source_columns(tf, sub):
    cols = json.load(open(os.path.join(GF_RES, tf, sub, "features.json")))["cols"]
    src = sorted({c.split("=")[0].replace("__na", "") for c in cols})
    return src


def mondrian_q(cal, alpha):
    """The ceil((n + 1)(1 - alpha))-th smallest calibration score; +inf when the rank exceeds n (keep everything)."""
    cal = np.sort(np.asarray(cal, dtype=float)); n = len(cal)
    if n == 0: return math.inf
    k = int(math.ceil((n + 1) * (1 - alpha)))
    return math.inf if k > n else (float(cal[k - 1]) if k >= 1 else -math.inf)


def clipped_loss(net): return np.minimum(np.maximum(-net, 0.0), CLIP_B)


def uncapped_net(T):
    """Every unit's net at 5 pts slippage with the brokerage cap removed (0.03% per order uncapped); lab.trade_charges."""
    cs = dict(H.CS); cs["brokerage_cap"] = float("inf")
    out = np.empty(T.n)
    for i in range(T.n):
        e, x = T.entry_px[i], T.exit_px[i]
        if T.up[i]: buy, sell = e + H.SLIP, x - H.SLIP
        else: sell, buy = e - H.SLIP, x + H.SLIP
        out[i] = (sell - buy) * H.LOT - lab.trade_charges(cs, buy, sell, H.LOT)["total"]
    return out


def book_stats(T, keep, rows, net_unc):
    """Kept-only / skipped-only statistics that are NOT kept-vs-skipped differences (those come from the ledger row)."""
    k = rows[keep[rows]]; s = rows[~keep[rows]]; net = T.net
    W = T.win[rows]; wn = net[rows]
    win_net = wn[W].sum(); loss_net = -wn[~W].sum()
    out = dict(selective_risk=r2(clipped_loss(net[k]).mean()) if len(k) else None,
               loser_share_kept=r4((~T.win[k]).mean()) if len(k) else None,
               skipped_winner_net=r2(net[s][net[s] > 0].sum()) if len(s) else 0.0,
               winner_net_retained=r4(net[k][net[k] > 0].sum() / win_net) if win_net else None,
               loser_net_avoided=r4(-net[s][net[s] <= 0].sum() / loss_net) if loss_net else None,
               kept_mean_uncapped=r2(net_unc[k].mean()) if len(k) else None,
               skipped_mean_uncapped=r2(net_unc[s].mean()) if len(s) else None)
    for w in W_GRID: out[f"U_w{w}"] = r2(net[k].sum() - w * (net[s][net[s] > 0].sum() if len(s) else 0.0))
    return out


def pick(res):
    keys = ("id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "kept_mean_slip3", "kept_mean_slip8",
            "loser_recall", "loser_precision", "winner_recall", "winner_recall_weighted", "top_decile_winners_skipped", "sign_blocks",
            "perm_p", "control_pct", "kept_net", "skipped_net", "kept_win_rate", "kept_pf")
    return {k: res.get(k) for k in keys}


def run(tf):
    t0 = time.time()
    T = H.load(tf)
    is_idx = np.flatnonzero(T.is_mask)
    order = is_idx[np.argsort(T.setup_i[is_idx], kind="stable")]              # IS rows in time order
    oof = pd.read_parquet(os.path.join(GF_RES, f"oof_{tf}.parquet"))
    hm = pd.to_datetime(T.F.time.astype(str)).dt.hour.to_numpy() * 60 + pd.to_datetime(T.F.time.astype(str)).dt.minute.to_numpy()
    tbin = np.array([next(name for name, lo, hi in BINS if lo <= m < hi) for m in hm])
    net_unc = uncapped_net(T)
    act = T.active_sessions; cal_sessions = set(int(s) for s in act[-CRC_SESSIONS:])
    cal_rows = is_idx[np.isin(T.session[is_idx], list(cal_sessions))]
    pre_rows = is_idx[~np.isin(T.session[is_idx], list(cal_sessions))]
    log(f"{tf}: {T.n} units, IS {len(is_idx)}, active IS sessions {len(act)}, CRC block = last {CRC_SESSIONS} active sessions -> {len(cal_rows)} rows "
        f"(from session {act[-CRC_SESSIONS]}, {T.day[cal_rows].min()} .. {T.day[cal_rows].max()}); rows before the block {len(pre_rows)}")
    meta = dict(tf=tf, label="L1", is_units=int(len(is_idx)), all_mean=r2(T.net[is_idx].mean()), win_rate=r4(T.win[is_idx].mean()),
                winners=int(T.win[is_idx].sum()), active_sessions=int(len(act)), mean_cost=r2(T.F.l1_cost_inr.to_numpy()[is_idx].mean()),
                mean_cost_uncapped_delta=r2((T.net - net_unc)[is_idx].mean()),
                crc_block=dict(sessions=CRC_SESSIONS, rows=int(len(cal_rows)), first_session=int(act[-CRC_SESSIONS]), first_date=str(T.day[cal_rows].min()),
                               last_date=str(T.day[cal_rows].max()), slack_B_over_n_plus_1=r2(CLIP_B / (CRC_SESSIONS + 1)), rows_before_block=int(len(pre_rows))),
                winners_per_bin={b: int((T.win[is_idx] & (tbin[is_idx] == b)).sum()) for b, _, _ in BINS},
                units_per_bin={b: int((tbin[is_idx] == b).sum()) for b, _, _ in BINS}, ledger_sha_before=H.ledger_sha(), started=D.datetime.now().isoformat(timespec="seconds"))
    results = dict(meta=meta, models={})
    for sub, model in MODELS:
        m = oof[(oof["sub"].astype(str) == sub) & (oof["model"].astype(str) == model)].set_index("setup_i")
        assert len(m) == len(is_idx) and set(m.index) == set(T.setup_i[is_idx].tolist()), f"{sub}/{model}: OOF rows do not match the IS units"
        m = m.loc[T.setup_i[is_idx]]
        assert (m["fold"].to_numpy() == T.block[is_idx]).all(), "OOF fold != harness block"
        p = np.full(T.n, np.nan); p[is_idx] = m["p"].to_numpy(dtype=float)
        gf_keep = np.zeros(T.n, dtype=bool); gf_keep[is_idx] = m["keep"].to_numpy(dtype=bool)
        gf_tau = m["tau"].to_numpy(dtype=float)
        assert np.isfinite(p[is_idx]).all(), "NaN probability"
        s = 1.0 - p
        vocab = VOCAB[sub]; role = ROLE[(tf, sub, model)]
        cols = source_columns(tf, sub)
        base = dict(tf=tf, sub=sub, model=model, vocabulary=vocab, score="1 - p_oof")
        R = dict(role=role, vocabulary=vocab, source_columns_n=len(cols), gate_family_nested=dict(
            kept_share=r4(gf_keep[is_idx].mean()), tau_per_fold=[r4(x) for x in pd.Series(gf_tau).groupby(T.block[is_idx]).first().to_numpy()]),
            p_summary=dict(min=r4(np.min(p[is_idx])), p25=r4(np.quantile(p[is_idx], .25)), p50=r4(np.median(p[is_idx])), p75=r4(np.quantile(p[is_idx], .75)), max=r4(np.max(p[is_idx])),
                           auc_oof=r4(_auc(p[is_idx], T.win[is_idx]))))
        log(f"== {tf} {sub}/{model}: {role}; gate_family nested kept share {R['gate_family_nested']['kept_share']}; OOF AUC {R['p_summary']['auc_oof']}")

        # ---------------- (1) cross-conformal, Mondrian by class (winners)
        conf = []
        for alpha in ALPHAS:
            keep = np.ones(T.n, dtype=bool); folds = []
            for f in range(H.N_BLOCKS):
                te = is_idx[T.block[is_idx] == f]; cal_idx = is_idx[(T.block[is_idx] != f) & T.win[is_idx]]
                q = mondrian_q(s[cal_idx], alpha)
                keep[te] = s[te] <= q
                W = T.win[te]; wn = T.net[te]
                folds.append(dict(fold=f, n_cal_winners=int(len(cal_idx)), q=r4(q) if np.isfinite(q) else None, n=int(len(te)), winners=int(W.sum()),
                                  kept_share=r4(keep[te].mean()), winner_coverage=r4(keep[te][W].mean()) if W.sum() else None,
                                  winner_coverage_weighted=r4(wn[keep[te] & W].sum() / wn[W].sum()) if W.sum() and wn[W].sum() else None,
                                  loser_recall=r4((~keep[te] & ~W).sum() / (~W).sum()) if (~W).sum() else None))
            cfg = dict(base, step="conformal", taxonomy="class", alpha=alpha)
            res = H.score(T, keep, "operating_point/conformal", cfg, script=__file__, note=f"{vocab}; re-parameterisation, no candidate")
            W = T.win[is_idx]; wn = T.net[is_idx]; kk = keep[is_idx]
            row = dict(alpha=alpha, nominal_coverage=1 - alpha, cv_plus_coverage=max(0.0, 1 - 2 * alpha),
                       winner_coverage=r4(kk[W].mean()), winner_coverage_weighted=r4(wn[kk & W].sum() / wn[W].sum()),
                       coverage_per_fold_min=min(x["winner_coverage"] for x in folds), coverage_per_fold_max=max(x["winner_coverage"] for x in folds),
                       folds_below_nominal=int(sum(1 for x in folds if x["winner_coverage"] < 1 - alpha)),
                       folds_below_cv_plus=int(sum(1 for x in folds if x["winner_coverage"] < 1 - 2 * alpha)),
                       agreement_with_gate_family_nested=r4((kk == gf_keep[is_idx]).mean()), ledger=pick(res), folds=folds, **book_stats(T, keep, is_idx, net_unc))
            conf.append(row)
            log(f"  conformal alpha {alpha}: kept {res['kept_share']} cov {row['winner_coverage']} (wtd {row['winner_coverage_weighted']}) diff {res['diff']} ctrl {res['control_pct']} slip8 {res['kept_mean_slip8']} id {res['id']}")
        R["conformal"] = conf
        # pre-registered alpha rule of the conformal design: largest loser recall s.t. winner coverage >= 0.9 and diff > 0
        ok = [c for c in conf if c["winner_coverage"] is not None and c["winner_coverage"] >= 0.9 and c["ledger"]["diff"] is not None and c["ledger"]["diff"] > 0]
        R["conformal_alpha_rule"] = dict(rule="largest loser recall s.t. OOF winner coverage >= 0.90 and kept-vs-skipped diff > 0",
                                         chosen=(max(ok, key=lambda c: c["ledger"]["loser_recall"] or -1)["alpha"] if ok else None), feasible_alphas=[c["alpha"] for c in ok])

        # ---------------- (1b) class x time-bin taxonomy, minute only
        if tf == "minute":
            confb = []
            for alpha in ALPHAS:
                keep = np.ones(T.n, dtype=bool); per_bin = {b: dict(n_cal_winners=[], q=[]) for b, _, _ in BINS}
                for f in range(H.N_BLOCKS):
                    te = is_idx[T.block[is_idx] == f]
                    for b, _, _ in BINS:
                        cal_idx = is_idx[(T.block[is_idx] != f) & T.win[is_idx] & (tbin[is_idx] == b)]
                        q = mondrian_q(s[cal_idx], alpha); tb = te[tbin[te] == b]
                        keep[tb] = s[tb] <= q
                        per_bin[b]["n_cal_winners"].append(int(len(cal_idx))); per_bin[b]["q"].append(r4(q) if np.isfinite(q) else None)
                cfg = dict(base, step="conformal", taxonomy="class_x_timebin", bins=[b for b, _, _ in BINS], alpha=alpha)
                res = H.score(T, keep, "operating_point/conformal_timebin", cfg, script=__file__, note=f"{vocab}; taxonomy reads the SETUP clock; re-parameterisation, no candidate")
                W = T.win[is_idx]; wn = T.net[is_idx]; kk = keep[is_idx]
                bins_out = {}
                for b, _, _ in BINS:
                    mb = tbin[is_idx] == b
                    bins_out[b] = dict(units=int(mb.sum()), winners=int((W & mb).sum()), kept_share=r4(kk[mb].mean()), winner_coverage=r4(kk[W & mb].mean()) if (W & mb).sum() else None,
                                       winner_coverage_weighted=r4(wn[kk & W & mb].sum() / wn[W & mb].sum()) if (W & mb).sum() else None,
                                       min_cal_winners=int(min(per_bin[b]["n_cal_winners"])), smallest_feasible_alpha=r4(1 / (min(per_bin[b]["n_cal_winners"]) + 1)))
                confb.append(dict(alpha=alpha, nominal_coverage=1 - alpha, cv_plus_coverage=max(0.0, 1 - 2 * alpha), winner_coverage=r4(kk[W].mean()),
                                  winner_coverage_weighted=r4(wn[kk & W].sum() / wn[W].sum()), bins=bins_out, ledger=pick(res), **book_stats(T, keep, is_idx, net_unc)))
                log(f"  conformal x timebin alpha {alpha}: kept {res['kept_share']} cov {confb[-1]['winner_coverage']} diff {res['diff']} ctrl {res['control_pct']} id {res['id']}")
            R["conformal_timebin"] = confb

        # ---------------- (1c) ACI, winner-conditional, IS in time order
        aci = []
        for gamma in GAMMAS:
            for alpha in ALPHAS:
                keep = np.ones(T.n, dtype=bool); a_t = alpha; past = []; path = []; burn = 0; n_dec = 0
                for i in order:
                    if len(past) < ACI_BURN_IN:
                        keep[i] = True; burn += 1
                    else:
                        if a_t <= 0: q = math.inf
                        elif a_t >= 1: q = -math.inf
                        else: q = mondrian_q(past, a_t)
                        keep[i] = s[i] <= q; n_dec += 1
                    if T.win[i]:
                        err = 0.0 if keep[i] else 1.0
                        a_t = min(1.0, max(0.0, a_t + gamma * (alpha - err)))
                        past.append(s[i]); path.append((int(T.setup_i[i]), round(a_t, 5), err))
                q_T = mondrian_q(past, a_t) if 0 < a_t < 1 else (math.inf if a_t <= 0 else -math.inf)
                cfg = dict(base, step="aci", taxonomy="class", alpha=alpha, gamma=gamma, burn_in_winners=ACI_BURN_IN)
                res = H.score(T, keep, "operating_point/aci", cfg, script=__file__, note=f"{vocab}; ACI winner-conditional, time order; final state carried to OOS by oos_once only; no candidate")
                W = T.win[is_idx]; wn = T.net[is_idx]; kk = keep[is_idx]
                errs = np.array([e for _, _, e in path]); last_q = max(1, len(errs) // 4)
                aci.append(dict(alpha=alpha, gamma=gamma, burn_in_rows=burn, decided_rows=n_dec, winners_updated=len(path),
                                winner_coverage=r4(kk[W].mean()), winner_coverage_weighted=r4(wn[kk & W].sum() / wn[W].sum()),
                                winner_coverage_after_burn_in=r4(1 - errs[ACI_BURN_IN:].mean()) if len(errs) > ACI_BURN_IN else None,
                                winner_coverage_last_quarter=r4(1 - errs[-last_q:].mean()), alpha_path_min=r4(min(a for _, a, _ in path)), alpha_path_max=r4(max(a for _, a, _ in path)),
                                final_state=dict(alpha_T=r4(a_t), q_T=(r4(q_T) if np.isfinite(q_T) else ("+inf" if q_T > 0 else "-inf")), n_winners=len(past), skip_if_p_below=(r4(1 - q_T) if np.isfinite(q_T) else None)),
                                ledger=pick(res), **book_stats(T, keep, is_idx, net_unc)))
                log(f"  ACI gamma {gamma} alpha {alpha}: kept {res['kept_share']} cov {aci[-1]['winner_coverage']} alpha_T {aci[-1]['final_state']['alpha_T']} diff {res['diff']} ctrl {res['control_pct']} id {res['id']}")
        R["aci"] = aci

        # ---------------- (2) + (4) selective risk-coverage curve, nested thresholds; Pareto utilities
        cov = []
        for c in COVERAGES:
            keep = np.ones(T.n, dtype=bool); thr = []
            for f in range(H.N_BLOCKS):
                te = is_idx[T.block[is_idx] == f]; tr = is_idx[T.block[is_idx] != f]
                t_f = float(np.quantile(s[tr], c)) if c < 1.0 else math.inf
                keep[te] = s[te] <= t_f; thr.append(r4(t_f) if np.isfinite(t_f) else None)
            cfg = dict(base, step="coverage", coverage=c)
            res = H.score(T, keep, "operating_point/coverage", cfg, script=__file__, controls=False, note=f"{vocab}; risk-coverage curve point (trial); no candidate")
            cov.append(dict(coverage=c, realised_coverage=res["kept_share"], threshold_per_fold=thr, ledger=pick(res), **book_stats(T, keep, is_idx, net_unc)))
        # Pareto flags over (winner_net_retained, loser_net_avoided): non-dominated points
        pts = [(x["winner_net_retained"] or 0, x["loser_net_avoided"] or 0) for x in cov]
        for i, x in enumerate(cov):
            x["pareto_efficient"] = not any((pts[j][0] >= pts[i][0] and pts[j][1] >= pts[i][1] and pts[j] != pts[i]) for j in range(len(cov)))
        argmax = {f"w{w}": max(cov, key=lambda x: x[f"U_w{w}"])["coverage"] for w in W_GRID}
        R["coverage_curve"] = cov; R["pareto_argmax_coverage_by_w"] = argmax
        log(f"  coverage curve done; U_w argmax coverage {argmax}; risk at c=0.5 {[x['selective_risk'] for x in cov if x['coverage'] == 0.5]}")

        # ---------------- (3) conformal risk control, sessions as units, calibration = last 200 active sessions
        crc = dict(n_sessions=CRC_SESSIONS, B=CLIP_B, slack=r2(CLIP_B / (CRC_SESSIONS + 1)), table=[], chosen=[])
        sess_cal = np.array(sorted(cal_sessions)); pos = np.searchsorted(sess_cal, T.session[cal_rows])
        for lam in CRC_LAMBDAS:
            thr = float(np.quantile(s[cal_rows], lam)) if lam < 1.0 else math.inf
            kc = s[cal_rows] <= thr
            loss = clipped_loss(T.net[cal_rows]) * kc
            per_s_sum = np.bincount(pos, weights=loss, minlength=len(sess_cal)); per_s_n = np.bincount(pos, weights=kc.astype(float), minlength=len(sess_cal))
            r_s = np.where(per_s_n > 0, per_s_sum / np.maximum(per_s_n, 1), 0.0)
            R_hat = float(r_s.mean()); cert = (CRC_SESSIONS * R_hat + CLIP_B) / (CRC_SESSIONS + 1)
            crc["table"].append(dict(coverage_lambda=lam, threshold=r4(thr) if np.isfinite(thr) else None, kept_share_block=r4(kc.mean()), R_hat=r2(R_hat), certificate=r2(cert),
                                     sessions_with_kept=int((per_s_n > 0).sum())))
        for alpha in CRC_ALPHAS:
            feas = [x for x in crc["table"] if x["certificate"] <= alpha]
            if not feas:
                crc["chosen"].append(dict(alpha=alpha, coverage_lambda=None, note="no lambda on the grid has a certificate <= alpha (even skipping everything: the slack alone exceeds it)" if CLIP_B / (CRC_SESSIONS + 1) > alpha else "no lambda with a certificate <= alpha"))
                continue
            best = max(feas, key=lambda x: x["coverage_lambda"])
            thr = float(np.quantile(s[cal_rows], best["coverage_lambda"])) if best["coverage_lambda"] < 1.0 else math.inf
            keep = np.ones(T.n, dtype=bool); keep[is_idx] = s[is_idx] <= thr
            cfg = dict(base, step="crc", alpha_inr=alpha, coverage_lambda=best["coverage_lambda"], calibration_sessions=CRC_SESSIONS, B=CLIP_B)
            res = H.score(T, keep, "operating_point/crc", cfg, script=__file__, note=f"{vocab}; CRC certificate on the last {CRC_SESSIONS} active IS sessions; no candidate")
            kp = keep[pre_rows]
            crc["chosen"].append(dict(alpha=alpha, coverage_lambda=best["coverage_lambda"], threshold=best["threshold"], certificate=best["certificate"], R_hat_block=best["R_hat"],
                                      realised_risk_before_block=r2(clipped_loss(T.net[pre_rows][kp]).mean()) if kp.any() else None, kept_share_before_block=r4(kp.mean()),
                                      realised_risk_all_is=r2(clipped_loss(T.net[is_idx][keep[is_idx]]).mean()) if keep[is_idx].any() else None,
                                      ledger=pick(res), **book_stats(T, keep, is_idx, net_unc)))
            log(f"  CRC alpha {alpha}: lambda {best['coverage_lambda']} cert {best['certificate']} realised pre-block {crc['chosen'][-1]['realised_risk_before_block']} kept {res['kept_share']} diff {res['diff']} ctrl {res['control_pct']} id {res['id']}")
        R["crc"] = crc
        if tf == "minute":
            crcb = dict(bins={}, chosen=[])
            for b, _, _ in BINS:
                cb = cal_rows[tbin[cal_rows] == b]; sb = np.array(sorted(set(T.session[cb].tolist()))); nb = len(sb); pb = np.searchsorted(sb, T.session[cb])
                tab = []
                for lam in CRC_LAMBDAS:
                    thr = float(np.quantile(s[cb], lam)) if lam < 1.0 else math.inf
                    kc = s[cb] <= thr; loss = clipped_loss(T.net[cb]) * kc
                    ps = np.bincount(pb, weights=loss, minlength=nb); pn = np.bincount(pb, weights=kc.astype(float), minlength=nb)
                    R_hat = float(np.where(pn > 0, ps / np.maximum(pn, 1), 0.0).mean()); cert = (nb * R_hat + CLIP_B) / (nb + 1)
                    tab.append(dict(coverage_lambda=lam, threshold=r4(thr) if np.isfinite(thr) else None, R_hat=r2(R_hat), certificate=r2(cert)))
                crcb["bins"][b] = dict(n_sessions_with_setup=int(nb), slack=r2(CLIP_B / (nb + 1)), rows=int(len(cb)), table=tab)
            for alpha in CRC_ALPHAS:
                keep = np.ones(T.n, dtype=bool); chosen = {}
                for b, _, _ in BINS:
                    feas = [x for x in crcb["bins"][b]["table"] if x["certificate"] <= alpha]
                    if not feas: chosen[b] = None; continue
                    best = max(feas, key=lambda x: x["coverage_lambda"]); cb = cal_rows[tbin[cal_rows] == b]
                    thr = float(np.quantile(s[cb], best["coverage_lambda"])) if best["coverage_lambda"] < 1.0 else math.inf
                    rb = is_idx[tbin[is_idx] == b]; keep[rb] = s[rb] <= thr
                    chosen[b] = dict(coverage_lambda=best["coverage_lambda"], threshold=best["threshold"], certificate=best["certificate"])
                if all(v is None for v in chosen.values()):
                    crcb["chosen"].append(dict(alpha=alpha, bins=chosen, note="no bin has a feasible lambda")); continue
                cfg = dict(base, step="crc", taxonomy="timebin", alpha_inr=alpha, coverage_lambda_by_bin={b: (v["coverage_lambda"] if v else None) for b, v in chosen.items()}, calibration_sessions=CRC_SESSIONS, B=CLIP_B)
                res = H.score(T, keep, "operating_point/crc_timebin", cfg, script=__file__, note=f"{vocab}; per-bin CRC certificates (minute only); no candidate")
                kp = keep[pre_rows]
                crcb["chosen"].append(dict(alpha=alpha, bins=chosen, realised_risk_before_block=r2(clipped_loss(T.net[pre_rows][kp]).mean()) if kp.any() else None,
                                           kept_share_before_block=r4(kp.mean()), ledger=pick(res), **book_stats(T, keep, is_idx, net_unc)))
                log(f"  CRC x timebin alpha {alpha}: {cfg['coverage_lambda_by_bin']} kept {res['kept_share']} diff {res['diff']} ctrl {res['control_pct']} id {res['id']}")
            R["crc_timebin"] = crcb

        # ---------------- (5) cost sensitivity: every kept book's slip 3 / 5 / 8 and uncapped brokerage (already on every row); summary
        books = [x for x in conf] + aci + [x for x in R.get("conformal_timebin", [])] + [x for x in crc["chosen"] if "ledger" in x] + [x for x in R.get("crc_timebin", {}).get("chosen", []) if "ledger" in x] + cov
        R["cost_sensitivity"] = dict(kept_books=len(books), books_with_kept_mean_slip8_gt_0=int(sum(1 for x in books if (x["ledger"]["kept_mean_slip8"] or -1) > 0)),
                                     books_with_kept_mean_slip3_gt_0=int(sum(1 for x in books if (x["ledger"]["kept_mean_slip3"] or -1) > 0)),
                                     best_kept_mean_slip8=r2(max((x["ledger"]["kept_mean_slip8"] or -1e9) for x in books)),
                                     best_kept_mean_slip3=r2(max((x["ledger"]["kept_mean_slip3"] or -1e9) for x in books)),
                                     best_kept_mean_uncapped=r2(max((x["kept_mean_uncapped"] or -1e9) for x in books)),
                                     uncapped_minus_capped_mean_delta=meta["mean_cost_uncapped_delta"])
        R["source_columns"] = cols
        results["models"][f"{sub}/{model}"] = R
        json.dump(results, open(os.path.join(HERE, f"results_{tf}.json"), "w"), indent=1, default=str)
        log(f"  {sub}/{model} done ({time.time() - t0:.0f}s so far)")

    # ---------------- family multiplicity over every operating_point row of the timeframe
    rows = H.read_ledger("operating_point", tf=tf, label="L1")
    rows = [r for r in rows if r["diff"] is not None]
    vecs = [H.load_vectors(r["id"]) for r in rows]
    fam = dict(rows=len(rows), pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"op|{tf}"), effective_trials=H.effective_trials(vecs),
               rows_by_family={f: int(sum(1 for r in rows if r["family"] == f)) for f in sorted({r["family"] for r in rows})})
    # best row by diff among the controlled rows: go/no-go with every argument (null_tape = not run, by design; no candidate)
    ctrl = [r for r in rows if r.get("control_pct") is not None]
    best = max(ctrl, key=lambda r: r["diff"]) if ctrl else None
    if best is not None:
        vb = H.load_vectors(best["id"]); boot = H.bootstrap_ci(vb, tag=f"op|{tf}|{best['id']}")
        gain = np.where(vb["kept_n"] > 0, vb["kept_sum"] / np.maximum(vb["kept_n"], 1), 0.0)[vb["kept_n"] > 0]
        sr_var = float(np.var([np.mean(np.where(v["kept_n"] > 0, v["kept_sum"] / np.maximum(v["kept_n"], 1), 0.0)[v["kept_n"] > 0]) / (np.std(np.where(v["kept_n"] > 0, v["kept_sum"] / np.maximum(v["kept_n"], 1), 0.0)[v["kept_n"] > 0], ddof=1) + 1e-9) for v in vecs]))
        dsr = H.deflated_sharpe(gain, len(rows), sr_var if sr_var > 0 else None)
        cols = results["models"][f"{best['config']['sub']}/{best['config']['model']}"]["source_columns"]
        passed, ch = H.go_no_go(best, tf, cpcv=None, pbo_value=fam["pbo_diff"]["pbo"], dsr=dsr, spa_p=fam["spa"].get("spa_p"), boot=boot,
                                null_tape="not run: this step adds no candidate (it re-parameterises a gate_family score; gate_family wrote no candidate)", columns=cols)
        fam["best_row"] = dict(id=best["id"], family=best["family"], config=best["config"], diff=best["diff"], control_pct=best["control_pct"], kept_share=best["kept_share"],
                               kept_mean_slip8=best["kept_mean_slip8"], boot=boot, dsr=dsr, go_no_go=dict(passed=passed, checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}))
    results["family"] = fam
    results["meta"]["ledger_sha_after"] = H.ledger_sha(); results["meta"]["seconds"] = round(time.time() - t0, 1)
    results["meta"]["finished"] = D.datetime.now().isoformat(timespec="seconds")
    json.dump(results, open(os.path.join(HERE, f"results_{tf}.json"), "w"), indent=1, default=str)
    log(f"{tf} ALL DONE in {time.time() - t0:.0f}s; family rows {fam['rows']}, PBO(diff) {fam['pbo_diff'].get('pbo')}, SPA p {fam['spa'].get('spa_p')}, eff trials {fam['effective_trials']}")


def _auc(score, y):
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y.astype(int), score)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", required=True); a = ap.parse_args()
    run(a.tf)
