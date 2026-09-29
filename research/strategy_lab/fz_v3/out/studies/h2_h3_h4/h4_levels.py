"""H4 "levels respected or broken" (BRIEF H4) through the harness. IS only; L1 primary, L0 robustness.

    python h4_levels.py [--tf minute|5minute] [--labels L1,L0]

Part A, the SETUP table (the build's as-of touch_* columns, data/README.md): touch episodes of the protected level / the nearest
  room edge / the nearest confirmed swing in the hour before k (a bar touches when low <= L <= high; consecutive touching bars
  are one episode); the last episode's verdict within 15 minutes after it, never past k: broke (a close beyond by > 0.5 x atr14
  on the far side), held, pending (window still open at k), none (no touch), na (no level).
  Descriptive: Foundation outcome by touch_<level>_last and by touch_<level>_n (0,1,2,3+). Gate cells (family h4/touch_gate, 9
  cells): skip when touch_<level>_last == broke / held / pending, level in {prot, room, swing}; nested CV over the 9; CPCV.
Part B, the episode study (IS bars only; labels of the level, not features): every touch episode of
  - a protected level: a maximal run of bars with the same engine `prot` value (bars.prot, as of the bar),
  - a room edge: lo and hi of every ST7/ST8 room over birth_bar <= i < retired_bar (fz_zones; retired_bar used only as the life end),
  - a confirmed swing: swings.price from conf_bar until the first close beyond it by > 0.5 x atr14 or the end of its session,
  with the same touch / episode / side / verdict rule as the build (verdict window 15 bars on 1 min, 3 bars on 5 min = 15 minutes,
  inside the touch bar's session). A window cut by the session end (last touch bar + 15 minutes past the session's last bar) is
  `session_end` whatever happened inside the truncated window: `broke` and `held` are verdicts of a full window only, so late
  touches cannot bias P(broke). A break close inside a truncated window is recorded as `cut_break = True` (counted in the
  verdicts table, never a `broke`, no aftermath, not a break for the retest bookkeeping). Repair round: the first run labelled
  such episodes `broke` (520 on 5 min, 3,825 on 1 min) while `held` was impossible for a cut window.
  side = sign(close before the episode - L) (open of the first touch bar when equal); break = a close on the far side by
  > 0.5 x atr14[last touch bar] inside the window.
  Aftermath from the verdict bar v (the breaking close for broke, the window end for held): move_n = sg x (close[v+n] - close[v]) /
  atr14[v] for n in {15, 30, 60} bars, sg = the break direction (broke) or the bounce direction away from the level (held);
  mfe_n = the best excursion in that direction; beyond_n = sg x (close[v+n] - L) / atr14[v] (the distance past the level, broke only);
  all inside v's session. Baseline: |close[i+n] - close[i]| / atr14[i] over every IS bar with the window inside its session.
  Retests: episodes of one level instance are numbered; prior_held = held episodes of the instance before this one; after_break =
  a broke episode of the instance came before. P(broke | prior_held) uses broke + held verdicts of episodes not after a break.
"""
import os, sys, json, time, argparse, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import h234_common as C
import harness as H

ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="minute,5minute"); ap.add_argument("--labels", default="L1,L0")
ap.add_argument("--part", default="all", choices=["all", "episodes"], help="episodes = Part B only (no ledger rows), rewrites <tf>/episodes in h4_summary_<tf>.json")
A = ap.parse_args()
log = C.Log(os.path.join(HERE, "h4_levels.log"))
T0 = time.time()
LEVELS, VERDICTS, NS = ("prot", "room", "swing"), ("broke", "held", "pending"), (15, 30, 60)
BREAK_ATR = 0.5


class Tape:
    def __init__(self, tf):
        D = os.path.join(C.OUT, "data", tf)
        b = pd.read_parquet(os.path.join(D, "bars.parquet"))
        self.n_is = int((b.split == "IS").sum())
        b = b.iloc[:self.n_is]
        self.O, self.Hh, self.Ll, self.Cc, self.A = (b[c].to_numpy(dtype=float) for c in ("open", "high", "low", "close", "atr14"))
        self.prot = b.prot.to_numpy(dtype=float); self.sess = b.session_idx.to_numpy(); self.hhmm = b.datetime.str[11:16].to_numpy()
        self.last = b.groupby("session_idx")["i"].transform("max").to_numpy()
        self.W = 15 if tf == "minute" else 3
        self.zones = pd.read_parquet(os.path.join(D, "fz_zones.parquet")); self.swings = pd.read_parquet(os.path.join(D, "swings.parquet"))


def episodes(tp, L, a, b, kind, inst):
    """All touch episodes of level L over bars a..b (inclusive) with verdicts and aftermath."""
    lo, hi = tp.Ll[a:b + 1], tp.Hh[a:b + 1]
    hit = (lo <= L) & (hi >= L)
    if not hit.any(): return []
    idx = np.flatnonzero(hit) + a
    brk = np.diff(idx) > 1
    starts, ends = idx[np.r_[True, brk]], idx[np.r_[brk, True]]
    out = []; prior_held = 0; after_break = False
    for n_ep, (js, je) in enumerate(zip(starts, ends), start=1):
        ref = tp.Cc[js - 1] if js >= 1 else tp.O[js]
        side = np.sign(ref - L) or np.sign(tp.O[js] - L)
        rec = dict(kind=kind, inst=inst, level=float(L), js=int(js), je=int(je), touch_bars=int(je - js + 1), side=int(side), ep_index=n_ep,
                   prior_held=prior_held, after_break=after_break, session=int(tp.sess[js]), hhmm=tp.hhmm[js], verdict="na", v=None, cut_break=False)
        if side == 0:
            out.append(rec); continue
        a_ = tp.A[je]; w0, w1 = je + 1, min(je + tp.W, tp.last[je])
        cut = je + tp.W > tp.last[je]                         # the 15-minute window runs past the session's last bar
        v = None
        if w1 >= w0:
            cc = tp.Cc[w0:w1 + 1]
            beyond = (L - cc) > BREAK_ATR * a_ if side > 0 else (cc - L) > BREAK_ATR * a_
            if cut: rec["verdict"] = "session_end"; rec["cut_break"] = bool(beyond.any())
            elif beyond.any(): rec["verdict"] = "broke"; v = w0 + int(np.argmax(beyond))
            else: rec["verdict"] = "held"; v = je + tp.W
        else: rec["verdict"] = "session_end"
        if v is not None:
            rec["v"] = int(v); sg = -side if rec["verdict"] == "broke" else side
            av = tp.A[v]
            for n in NS:
                if v + n <= tp.last[v] and av > 0:
                    rec[f"move_{n}"] = round(float(sg * (tp.Cc[v + n] - tp.Cc[v]) / av), 4)
                    ex = tp.Hh[v + 1:v + n + 1] if sg > 0 else tp.Ll[v + 1:v + n + 1]
                    rec[f"mfe_{n}"] = round(float(sg * (ex.max() if sg > 0 else ex.min()) - sg * tp.Cc[v]) / av, 4)
                    rec[f"beyond_{n}"] = round(float(sg * (tp.Cc[v + n] - L) / av), 4) if rec["verdict"] == "broke" else None
                else:
                    rec[f"move_{n}"] = rec[f"mfe_{n}"] = rec[f"beyond_{n}"] = None
        if rec["verdict"] == "held": prior_held += 1
        out.append(rec)
        if rec["verdict"] == "broke": after_break = True
    return out


def level_instances(tp):
    """(kind, inst, L, a, b) for every level instance alive inside the IS bars."""
    inst = []
    p = tp.prot; ok = ~np.isnan(p)
    change = np.r_[True, (p[1:] != p[:-1]) | (ok[1:] != ok[:-1])]
    starts = np.flatnonzero(change); ends = np.r_[starts[1:] - 1, len(p) - 1]
    for k_, (a, b) in enumerate(zip(starts, ends)):
        if ok[a]: inst.append(("prot", f"prot{k_}", float(p[a]), int(a), int(b)))
    z = tp.zones[tp.zones.birth_bar < tp.n_is]
    for r in z.itertuples():
        b = int(min((r.retired_bar - 1) if pd.notna(r.retired_bar) else tp.n_is - 1, tp.n_is - 1))
        if b >= r.birth_bar:
            inst.append(("room", f"{r.id}|lo", float(r.lo), int(r.birth_bar), b)); inst.append(("room", f"{r.id}|hi", float(r.hi), int(r.birth_bar), b))
    s = tp.swings[tp.swings.conf_bar < tp.n_is]
    for r in s.itertuples():
        a = int(r.conf_bar); L = float(r.price); end = int(tp.last[a])
        seg = tp.Cc[a:end + 1]; at = tp.A[a:end + 1]
        beyond = (seg > L + BREAK_ATR * at) if r.kind == "H" else (seg < L - BREAK_ATR * at)
        b = a + int(np.argmax(beyond)) if beyond.any() else end
        inst.append(("swing", f"sw{r.seq}{r.kind}", L, a, b))
    return inst


def q(x, p): return round(float(np.nanquantile(x, p)), 3) if len(x) else None


def episode_study(tf):
    tp = Tape(tf); t0 = time.time()
    inst = level_instances(tp)
    log(f"  {tf}: level instances " + str(pd.Series([i[0] for i in inst]).value_counts().to_dict()))
    recs = []
    for kind, iid, L, a, b in inst: recs.extend(episodes(tp, L, a, b, kind, iid))
    E = pd.DataFrame(recs)
    E.to_parquet(os.path.join(HERE, f"h4_{tf}_episodes.parquet"))
    log(f"  {tf}: {len(E)} episodes in {time.time() - t0:.0f}s; verdicts " + str(E.groupby("kind").verdict.value_counts().to_dict()) +
        f"; cut windows with a break close (session_end, cut_break) {int(E.cut_break.sum())}")
    # 1. verdict counts (cut_break_n = session_end episodes whose truncated window held a break close; never a `broke`)
    vc = E.groupby(["kind", "verdict"]).agg(n=("verdict", "size"), cut_break_n=("cut_break", "sum")).reset_index()
    vc["cut_break_n"] = vc.cut_break_n.astype(int)
    vc["share"] = vc.n / vc.groupby("kind").n.transform("sum"); vc["share"] = vc.share.round(4)
    vc.to_csv(os.path.join(HERE, f"h4_{tf}_episode_verdicts.csv"), index=False)
    # 2. P(broke | prior held), episodes not after a break, verdict in broke / held
    D = E[E.verdict.isin(["broke", "held"]) & ~E.after_break].copy()
    D["prior_held_bin"] = np.where(D.prior_held >= 3, "3+", D.prior_held.astype(str))
    pb = D.groupby(["kind", "prior_held_bin"]).agg(n=("verdict", "size"), p_broke=("verdict", lambda s: round(float((s == "broke").mean()), 4))).reset_index()
    pb.to_csv(os.path.join(HERE, f"h4_{tf}_p_break_by_prior_held.csv"), index=False)
    # 3. aftermath by kind x verdict x n, plus the baseline over all IS bars
    rows = []
    for n in NS:
        full = np.arange(tp.n_is) + n <= tp.last
        with np.errstate(all="ignore"): mv = np.abs(np.roll(tp.Cc, -n) - tp.Cc) / tp.A
        mv = mv[full & (tp.A > 0)]
        rows.append(dict(kind="baseline_all_bars", verdict="any", n_bars=n, n=int(len(mv)), abs_mean=round(float(mv.mean()), 3), abs_median=q(mv, .5), abs_p75=q(mv, .75),
                         abs_p90=q(mv, .9), abs_share_gt1=round(float((mv > 1).mean()), 4), abs_share_gt2=round(float((mv > 2).mean()), 4)))
    for (kind, verdict), g in E[E.verdict.isin(["broke", "held"])].groupby(["kind", "verdict"]):
        for n in NS:
            m = g[f"move_{n}"].to_numpy(dtype=float); m = m[~np.isnan(m)]
            f = g[f"mfe_{n}"].to_numpy(dtype=float); f = f[~np.isnan(f)]
            r = dict(kind=kind, verdict=verdict, n_bars=n, n=int(len(m)), move_mean=round(float(m.mean()), 3) if len(m) else None, move_median=q(m, .5), move_p25=q(m, .25), move_p75=q(m, .75),
                     move_share_pos=round(float((m > 0).mean()), 4) if len(m) else None, move_share_gt1=round(float((m > 1).mean()), 4) if len(m) else None,
                     move_share_gt2=round(float((m > 2).mean()), 4) if len(m) else None, abs_mean=round(float(np.abs(m).mean()), 3) if len(m) else None, abs_median=q(np.abs(m), .5), abs_p75=q(np.abs(m), .75), abs_p90=q(np.abs(m), .9),
                     abs_share_gt1=round(float((np.abs(m) > 1).mean()), 4) if len(m) else None, abs_share_gt2=round(float((np.abs(m) > 2).mean()), 4) if len(m) else None,
                     mfe_mean=round(float(f.mean()), 3) if len(f) else None, mfe_median=q(f, .5), mfe_p75=q(f, .75))
            if verdict == "broke":
                bb = g[f"beyond_{n}"].to_numpy(dtype=float); bb = bb[~np.isnan(bb)]
                r.update(beyond_mean=round(float(bb.mean()), 3) if len(bb) else None, beyond_median=q(bb, .5), beyond_share_pos=round(float((bb > 0).mean()), 4) if len(bb) else None)
            rows.append(r)
    AM = pd.DataFrame(rows); AM.to_csv(os.path.join(HERE, f"h4_{tf}_aftermath.csv"), index=False)
    # 4. retests before the first break, per instance that broke
    first_break = E[E.verdict == "broke"].groupby(["kind", "inst"]).prior_held.min().reset_index()
    first_break["retests_bin"] = np.where(first_break.prior_held >= 3, "3+", first_break.prior_held.astype(str))
    inst_broke = first_break.groupby(["kind", "retests_bin"]).size().rename("instances").reset_index()
    inst_all = E.groupby("kind").inst.nunique().rename("instances_touched").reset_index()
    inst_broke = inst_broke.merge(inst_all, on="kind"); inst_broke["share_of_touched_instances"] = (inst_broke.instances / inst_broke.instances_touched).round(4)
    inst_broke.to_csv(os.path.join(HERE, f"h4_{tf}_retests_before_break.csv"), index=False)
    # 5. held episodes: was the level touched again (a retest) later in its life?
    E["retested_later"] = E.groupby(["kind", "inst"]).ep_index.transform("max") > E.ep_index
    rt = E[E.verdict == "held"].groupby("kind").retested_later.agg(n="size", share_retested=lambda s: round(float(s.mean()), 4)).reset_index()
    rt.to_csv(os.path.join(HERE, f"h4_{tf}_held_then_retested.csv"), index=False)
    return dict(instances={k: int(v) for k, v in pd.Series([i[0] for i in inst]).value_counts().items()}, episodes=int(len(E)), verdicts=vc.to_dict("records"),
                cut_windows=int((E.verdict == "session_end").sum()), cut_windows_with_break_close=int(E.cut_break.sum()),
                p_break_by_prior_held=pb.to_dict("records"), aftermath=AM.to_dict("records"), retests_before_break=inst_broke.to_dict("records"), held_then_retested=rt.to_dict("records"),
                run_s=round(time.time() - t0, 1))


def cells_h4():
    cells = []
    for lvl, vd in itertools.product(LEVELS, VERDICTS):
        cells.append(C.Cell("h4/touch_gate", dict(level=lvl, skip_when_last=vd), apply=lambda T, r, t, lvl=lvl, vd=vd: T.F[f"touch_{lvl}_last"].astype(str).to_numpy()[r] != vd))
    return cells


def run(tf, label):
    T = H.load(tf, label); tag = f"{tf}_{label}"; F = T.F; rows_is = np.flatnonzero(T.is_mask)
    log(f"== H4 {tag}: IS units {len(rows_is)}")
    tabs = []
    for lvl in LEVELS:
        tabs.append(C.bucket_table(T, C.txt(F[f"touch_{lvl}_last"]).to_numpy(), f"touch_{lvl}_last", rows_is, ["broke", "held", "pending", "none", "na"]))
        n = F[f"touch_{lvl}_n"].to_numpy(dtype=float)
        lab = np.where(np.isnan(n), "na", np.where(n >= 3, "3+", np.nan_to_num(n).astype(int).astype(str)))
        tabs.append(C.bucket_table(T, lab, f"touch_{lvl}_n", rows_is, ["0", "1", "2", "3+", "na"]))
    D = pd.concat(tabs, ignore_index=True); D.to_csv(os.path.join(HERE, f"h4_{tag}_by_touch.csv"), index=False)
    for lvl in LEVELS:
        s = D[D.variable == f"touch_{lvl}_last"]
        log(f"  by touch_{lvl}_last: " + "; ".join(f"{r.bucket}: n {r.n} mean {r.net_mean} win {r.win_rate}" for r in s.itertuples()))
    cells = cells_h4()
    rows = C.score_cells(T, cells, __file__, log)
    G = pd.concat([pd.DataFrame([r["config"] for r in rows]), C.grid_frame(rows)], axis=1); G.to_csv(os.path.join(HERE, f"h4_{tag}_grid.csv"), index=False)
    nested, chosen, dist, prow, cp_chosen = C.nested_cv(T, cells, "h4", __file__, log)
    pd.DataFrame([{k: r.get(k) for k in ["id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "winner_recall_weighted", "sign_blocks"]} | {"path": r["config"]["path"]} for r in prow]).to_csv(os.path.join(HERE, f"h4_{tag}_cpcv_paths.csv"), index=False)
    fam = C.family_stats(T, "h4", nested, dist, tag)
    log(f"  family: {fam['candidates']} candidates, eff {fam['effective_trials']}, PBO diff {fam['pbo_diff']['pbo']} kept {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} best {fam['spa_best_config']}, boot {fam['bootstrap_nested']['diff_ci']}, DSR p {fam['dsr_nested'].get('p')}, go {fam['go_no_go_nested']['passed']}")
    return dict(tf=tf, label=label, n_is=int(len(rows_is)), grid_cells=len(cells), grid_cells_go_raw=int(G.go_raw.sum()), grid_pct_ge95=int((G.control_pct >= 95).sum()), grid_diff_pos=int((G["diff"] > 0).sum()),
                grid=G[["cell", "id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "control_pct", "perm_p", "loser_recall", "loser_precision", "winner_recall_weighted", "sign_blocks", "go_raw"]].to_dict("records"),
                nested={k: nested.get(k) for k in C.GRID_COLS if k != "cell"} | dict(chosen_per_block=chosen), cpcv=dist, cpcv_chosen=cp_chosen, family=fam)


if __name__ == "__main__" and A.part == "episodes":
    log(f"h4_levels --part episodes (repair round: cut windows are session_end, cut_break recorded) start {time.ctime()}; no ledger row is written")
    for tf in A.tf.split(","):
        p = os.path.join(HERE, f"h4_summary_{tf}.json")
        S = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        S[f"{tf}/episodes"] = episode_study(tf)
        S[f"{tf}/episodes"]["repair"] = dict(at=time.strftime("%Y-%m-%dT%H:%M:%S"), what="verdict of a window cut by the session end = session_end (was broke when a break close fell inside the truncated window); cut_break added",
                                             script_sha=H.file_sha(__file__))
        C.jdump(S, p)
    log(f"h4 episodes done in {time.time() - T0:.1f}s")
elif __name__ == "__main__":
    log(f"h4_levels start {time.ctime()} ledger sha {H.ledger_sha()}")
    S = {}
    for tf in A.tf.split(","):
        S[f"{tf}/episodes"] = episode_study(tf)
        for label in A.labels.split(","):
            S[f"{tf}/{label}"] = run(tf, label)
            C.jdump(S[f"{tf}/{label}"], os.path.join(HERE, f"h4_{tf}_{label}_summary.json"))
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    C.jdump(S, os.path.join(HERE, f"h4_summary_{A.tf.replace(',', '_')}.json"))
    log(f"h4 done in {S['run_s']}s; ledger sha {S['ledger_sha_after']}")
