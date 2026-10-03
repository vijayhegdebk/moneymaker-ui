"""H3 "visibly high volume" (BRIEF H3) through the harness. IS only; L1 primary, L0 robustness.

    python h3_volume.py [--tf minute|5minute] [--labels L1,L0]

Definitions (fixed before any number was read):
  high-volume bar   volume >= v x median(volume of the previous N bars of the same session, at least 5 of them), v in {2,3,4},
                    N in {20,60}; bars that are not the front month or have zero volume are never high-volume (bars.fm_na).
                    The N = 20 / 60 medians are recomputed here and asserted equal to bars.vol_med20_prior / vol_ratio20 / vol_ratio60.
  bar direction     sign(close - open): up / down / flat (flat bars are counted and excluded from the direction tables).
  aftermath (labels of the bar, from IS bars only, every window inside the bar's session, the full window required):
    fwd_{5,15,30}   sg x (close[j+n] - close[j]) in pts and / atr14[j]; share > 0
    mfe30 / mae30   max over j+1..j+30 of sg x (high|low - close[j]) / atr14 (the best excursion), min (the worst)
    high_held_n     max(high[j+1..j+n]) <= high[j];  low_held_n: min(low[j+1..j+n]) >= low[j];  n in {15, 30}
    own_extreme_held = the extreme in the bar's direction held (no continuation); opp_extreme_held = the other one held (respect)
    baseline        the same statistics over every IS bar with a defined ratio and a non-flat direction
  per SETUP (as-of, bars <= k; re-run on the truncated build and diffed): for each (v, N) the latest high-volume bar j of the
    session with j <= k (the SETUP bar itself counts, as the build's hv{2,3}_* do): hv_bars_since = k - j, hv_dir. For M in
    {5,15,30}: category agree (k - j <= M and hv_dir == dir), disagree (k - j <= M and hv_dir opposite), none (no such bar
    within M bars, or a flat bar). (v=2, N=20) and (v=3, N=20) are asserted equal to the build's hv2_* / hv3_* columns.
  gate cells (family h3/gate; 3 x 2 x 3 x 3 = 54 cells, each a ledger row): skip_if_disagree, skip_if_none, take_only_agree
    (= skip disagree and none) per (v, N, M). Nested CV chooses the cell inside each training fold (h234_common.nested_cv).
"""
import os, sys, json, time, argparse, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import h234_common as C
import harness as H

ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="minute,5minute"); ap.add_argument("--labels", default="L1,L0"); A = ap.parse_args()
log = C.Log(os.path.join(HERE, "h3_volume.log"))
T0 = time.time()
VS, NS, MS = (2, 3, 4), (20, 60), (5, 15, 30)
GATES = ("skip_if_disagree", "skip_if_none", "take_only_agree")


def fwd_max(x, n, fill):
    """out[j] = max(x[j+1 .. j+n]) (NaN where the window runs past the array)."""
    pad = np.concatenate([x[1:], np.full(n, fill)])
    w = np.lib.stride_tricks.sliding_window_view(pad, n)
    return w.max(axis=1)


def fwd_min(x, n, fill):
    pad = np.concatenate([x[1:], np.full(n, fill)])
    return np.lib.stride_tricks.sliding_window_view(pad, n).min(axis=1)


def bar_frame(tf, folder):
    b = pd.read_parquet(os.path.join(C.OUT, "data", tf, folder, "bars.parquet") if folder else os.path.join(C.OUT, "data", tf, "bars.parquet"))
    V = b.volume.to_numpy(dtype=float); g = b.groupby("session_idx")["volume"]
    med = {N: g.transform(lambda s, N=N: s.shift(1).rolling(N, min_periods=5).median()).to_numpy() for N in NS}
    usable = ~b.fm_na.to_numpy()
    with np.errstate(all="ignore"):
        ratio = {N: np.where(usable & (med[N] > 0), V / med[N], np.nan) for N in NS}
    if not folder:
        same = lambda x, y: bool(np.all((np.isnan(x) & np.isnan(y)) | (np.abs(x - y) <= 1e-9)))
        assert same(med[20], b.vol_med20_prior.to_numpy(dtype=float)) and same(ratio[20], b.vol_ratio20.to_numpy(dtype=float)) and same(ratio[60], b.vol_ratio60.to_numpy(dtype=float)), "volume baselines differ from the build"
    b["dir_num"] = np.sign(b.close.to_numpy() - b.open.to_numpy()).astype(int)
    for N in NS:
        b[f"ratio{N}"] = ratio[N]
        for v in VS:
            flag = np.where(np.isnan(ratio[N]), False, ratio[N] >= v)
            b[f"hv{v}_{N}"] = flag
            idx = pd.Series(np.where(flag, np.arange(len(b)), np.nan)); b[f"last_hv{v}_{N}"] = idx.groupby(b.session_idx.to_numpy()).ffill().to_numpy()
    b["last_i"] = b.groupby("session_idx")["i"].transform("max").to_numpy()
    return b


def aftermath(b):
    """The IS bar-level aftermath tables: per (v, N) x direction, plus the baseline."""
    isb = (b.split.to_numpy() == "IS")
    C_, Hh, Ll, A_ = (b[c].to_numpy(dtype=float) for c in ("close", "high", "low", "atr14"))
    last = b.last_i.to_numpy(); i = b.i.to_numpy(); d = b.dir_num.to_numpy()
    full = {n: (i + n <= last) for n in (5, 15, 30)}
    fwd = {n: np.where(full[n], np.roll(C_, -n) - C_, np.nan) for n in (5, 15, 30)}
    hi30, lo30 = fwd_max(Hh, 30, -np.inf), fwd_min(Ll, 30, np.inf)
    hi15, lo15 = fwd_max(Hh, 15, -np.inf), fwd_min(Ll, 15, np.inf)
    sg = d.astype(float)
    with np.errstate(all="ignore"):
        mfe30 = np.where(full[30], np.where(sg > 0, hi30 - C_, C_ - lo30) / A_, np.nan)
        mae30 = np.where(full[30], np.where(sg > 0, lo30 - C_, C_ - hi30) / A_, np.nan)
        hh15, hh30 = np.where(full[15], hi15 <= Hh, np.nan), np.where(full[30], hi30 <= Hh, np.nan)
        lh15, lh30 = np.where(full[15], lo15 >= Ll, np.nan), np.where(full[30], lo30 >= Ll, np.nan)
    rows = []

    def stats(m, name, v, N, dr):
        m = m & isb
        r = dict(set=name, v=v, N=N, dir=dr, n=int(m.sum()))
        if r["n"] == 0: return r
        s = sg[m]
        for n in (5, 15, 30):
            f = s * fwd[n][m]; fa = f / A_[m]; ok = ~np.isnan(f)
            r.update({f"fwd{n}_n": int(ok.sum()), f"fwd{n}_pts_mean": round(float(np.nanmean(f)), 2), f"fwd{n}_atr_mean": round(float(np.nanmean(fa)), 3),
                      f"fwd{n}_atr_median": round(float(np.nanmedian(fa)), 3), f"fwd{n}_pos_share": round(float(np.nanmean(f[ok] > 0)), 4) if ok.any() else None,
                      f"fwd{n}_abs_atr_mean": round(float(np.nanmean(np.abs(fa))), 3)})
        r.update(mfe30_atr_mean=round(float(np.nanmean(mfe30[m])), 3), mfe30_atr_median=round(float(np.nanmedian(mfe30[m])), 3),
                 mae30_atr_mean=round(float(np.nanmean(mae30[m])), 3), mae30_atr_median=round(float(np.nanmedian(mae30[m])), 3),
                 high_held_15=round(float(np.nanmean(hh15[m])), 4), high_held_30=round(float(np.nanmean(hh30[m])), 4),
                 low_held_15=round(float(np.nanmean(lh15[m])), 4), low_held_30=round(float(np.nanmean(lh30[m])), 4))
        own15 = np.where(s > 0, hh15[m], lh15[m]); own30 = np.where(s > 0, hh30[m], lh30[m]); opp15 = np.where(s > 0, lh15[m], hh15[m]); opp30 = np.where(s > 0, lh30[m], hh30[m])
        r.update(own_extreme_held_15=round(float(np.nanmean(own15)), 4), own_extreme_held_30=round(float(np.nanmean(own30)), 4),
                 opp_extreme_held_15=round(float(np.nanmean(opp15)), 4), opp_extreme_held_30=round(float(np.nanmean(opp30)), 4))
        return r
    base_ok = ~np.isnan(b.ratio20.to_numpy())
    for dr, dm in (("up", d > 0), ("down", d < 0), ("both", d != 0)):
        rows.append(stats(base_ok & dm, "baseline_all_bars", None, 20, dr))
    for v, N in itertools.product(VS, NS):
        f = b[f"hv{v}_{N}"].to_numpy()
        rows.append(dict(set="hv_flat_count", v=v, N=N, dir="flat", n=int((f & isb & (d == 0)).sum())))
        for dr, dm in (("up", d > 0), ("down", d < 0), ("both", d != 0)):
            rows.append(stats(f & dm, "high_volume", v, N, dr))
    return pd.DataFrame(rows)


def setup_feats(b, setups):
    """Per-SETUP as-of features for each (v, N): bars since the latest high-volume bar of the session (<= k) and its direction."""
    k = setups.setup_i.to_numpy(); out = pd.DataFrame(dict(setup_i=k))
    d = b.dir_num.to_numpy()
    for v, N in itertools.product(VS, NS):
        j = b[f"last_hv{v}_{N}"].to_numpy()[k]
        bs = np.where(np.isnan(j), np.nan, k - j)
        dn = np.where(np.isnan(j), 0, d[np.nan_to_num(j, nan=0).astype(int)])
        out[f"hv{v}_{N}_bars_since"] = bs; out[f"hv{v}_{N}_dir"] = np.where(np.isnan(j), "none", np.where(dn > 0, "up", np.where(dn < 0, "down", "flat")))
    return out


def category(feat, v, N, M, sg):
    bs = feat[f"hv{v}_{N}_bars_since"].to_numpy(dtype=float); dr = feat[f"hv{v}_{N}_dir"].to_numpy().astype(str)
    hv_sg = np.where(dr == "up", 1, np.where(dr == "down", -1, 0))
    within = ~np.isnan(bs) & (bs <= M) & (hv_sg != 0)
    return np.where(~within, "none", np.where(hv_sg == sg, "agree", "disagree"))


def cells_h3(cats):
    cells = []
    for v, N, M, g in itertools.product(VS, NS, MS, GATES):
        key = (v, N, M)
        def ap_(T, r, t, key=key, g=g):
            c = cats[key][r]
            if g == "skip_if_disagree": return c != "disagree"
            if g == "skip_if_none": return c != "none"
            return c == "agree"
        cells.append(C.Cell("h3/gate", dict(v=v, N=N, M=M, gate=g), apply=ap_))
    return cells


def run(tf, label, b, feats, trunc):
    T = H.load(tf, label); tag = f"{tf}_{label}"
    log(f"== H3 {tag}: IS units {int(T.is_mask.sum())}")
    f = feats.set_index("setup_i").loc[T.F.setup_i.to_numpy()].reset_index()
    sg = np.where(T.F.dir.astype(str).to_numpy() == "up", 1, -1)
    # cross-check with the build's hv2_* / hv3_* (N = 20, M unbounded within the session)
    chk = {}
    for v in (2, 3):
        bs_b = T.F[f"hv{v}_bars_since"].to_numpy(dtype=float); dr_b = T.F[f"hv{v}_dir"].astype(str).to_numpy()
        bs_m = f[f"hv{v}_20_bars_since"].to_numpy(dtype=float); dr_m = f[f"hv{v}_20_dir"].to_numpy().astype(str)
        chk[f"hv{v}_20"] = bool(np.all((np.isnan(bs_b) & np.isnan(bs_m)) | (bs_b == bs_m)) and np.all(dr_b == dr_m))
    log(f"  build cross-check hv2/hv3 (N=20): {chk}")
    assert all(chk.values()), chk
    cats = {(v, N, M): category(f, v, N, M, sg) for v, N, M in itertools.product(VS, NS, MS)}
    rows_is = np.flatnonzero(T.is_mask)
    tabs = [C.bucket_table(T, cats[(v, N, M)], f"hv v{v} N{N} M{M}", rows_is, ["agree", "disagree", "none"]) for v, N, M in itertools.product(VS, NS, MS)]
    D = pd.concat(tabs, ignore_index=True); D.to_csv(os.path.join(HERE, f"h3_{tag}_by_agreement.csv"), index=False)
    for v, N in itertools.product(VS, NS):
        bs = f[f"hv{v}_{N}_bars_since"].to_numpy(dtype=float)
        lab = np.where(np.isnan(bs), "none", np.where(bs == 0, "0", np.where(bs <= 5, "1-5", np.where(bs <= 15, "6-15", np.where(bs <= 30, "16-30", ">30")))))
        tabs.append(C.bucket_table(T, lab, f"hv v{v} N{N} bars_since", rows_is, ["0", "1-5", "6-15", "16-30", ">30", "none"]))
    pd.concat(tabs[len(list(itertools.product(VS, NS, MS))):], ignore_index=True).to_csv(os.path.join(HERE, f"h3_{tag}_by_bars_since.csv"), index=False)
    cells = cells_h3(cats)
    rows = C.score_cells(T, cells, __file__, log)
    G = pd.concat([pd.DataFrame([r["config"] for r in rows]), C.grid_frame(rows)], axis=1)
    G.to_csv(os.path.join(HERE, f"h3_{tag}_grid.csv"), index=False)
    nested, chosen, dist, prow, cp_chosen = C.nested_cv(T, cells, "h3", __file__, log)
    pd.DataFrame([{k: r.get(k) for k in ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "sign_blocks"]} | {"path": r["config"]["path"]} for r in prow]).to_csv(os.path.join(HERE, f"h3_{tag}_cpcv_paths.csv"), index=False)
    fam = C.family_stats(T, "h3", nested, dist, tag)
    log(f"  family: {fam['candidates']} candidates, eff {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} best {fam['spa_best_config']}, boot {fam['bootstrap_nested']['diff_ci']}, DSR p {fam['dsr_nested'].get('p')}, go {fam['go_no_go_nested']['passed']}")
    summ = dict(tf=tf, label=label, n_is=int(T.is_mask.sum()), build_crosscheck=chk, trunc_check=trunc, grid_cells=len(cells), grid_cells_go_raw=int(G.go_raw.sum()),
                grid_pct_ge95=int((G.control_pct >= 95).sum()), grid_diff_pos=int((G["diff"] > 0).sum()),
                top10_by_diff=G.sort_values("diff", ascending=False).head(10)[["cell", "id", "kept_n", "kept_share", "diff", "control_pct", "perm_p", "sign_blocks", "go_raw"]].to_dict("records"),
                nested={k: nested.get(k) for k in C.GRID_COLS if k != "cell"} | dict(chosen_per_block=chosen), cpcv=dist, cpcv_chosen=cp_chosen, family=fam)
    C.jdump(summ, os.path.join(HERE, f"h3_{tag}_summary.json"))
    return summ


if __name__ == "__main__":
    log(f"h3_volume start {time.ctime()} ledger sha {H.ledger_sha()}")
    S = {}
    for tf in A.tf.split(","):
        b = bar_frame(tf, None)
        am = aftermath(b); am.to_csv(os.path.join(HERE, f"h3_{tf}_bar_aftermath.csv"), index=False)
        log(f"  {tf}: bar aftermath table {len(am)} rows; hv counts IS " + str({f"v{v}N{N}": int((b[f'hv{v}_{N}'] & (b.split == 'IS')).sum()) for v, N in itertools.product(VS, NS)}))
        setups = pd.read_parquet(os.path.join(C.OUT, "data", tf, "features.parquet"), columns=["setup_i"])
        feats = setup_feats(b, setups)
        # causality: the same features from the truncated build, identical for every SETUP before the cut
        bt = bar_frame(tf, C.CUT); st = pd.read_parquet(os.path.join(C.OUT, "data", tf, C.CUT, "features.parquet"), columns=["setup_i"])
        ft = setup_feats(bt, st)
        trunc = C.trunc_diff_setups(feats, ft, [c for c in feats.columns if c != "setup_i"], len(bt)); trunc["cut"] = C.CUT
        log(f"  {tf}: truncation check {trunc}")
        assert trunc["PASS"], "new per-SETUP features are not causal"
        feats.to_parquet(os.path.join(HERE, f"h3_{tf}_setup_hv_features.parquet"))
        del bt, ft
        for label in A.labels.split(","):
            S[f"{tf}/{label}"] = run(tf, label, b, feats, trunc)
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    C.jdump(S, os.path.join(HERE, f"h3_summary_{A.tf.replace(',', '_')}.json"))
    log(f"h3 done in {S['run_s']}s; ledger sha {S['ledger_sha_after']}")
