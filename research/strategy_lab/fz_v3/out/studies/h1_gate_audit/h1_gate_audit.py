"""H1 gate audit (BRIEF H1) through the harness: what do the frozen ST7 (1 min) / ST8 (5 min) gates skip vs keep by
Foundation outcome? IS only; labels L1 (primary) and L0 (robustness).

    python h1_gate_audit.py            # both timeframes, both labels; writes CSV / JSON / TABLES.md next to this file

Definitions (fixed before any number was looked at):
  unit        a harness row: a Foundation SETUP taken under the label's book (harness.load(tf, label)); IS rows only
  kept        T.F.fz_traded: ST7/ST8 held a position on this SETUP (a TAKE, or a REENTER whose R5 was this SETUP). It is the
              frozen gate's kept set and is post-SETUP (the comparator, never a feature)
  gate_at     fz_gate (as of the SETUP bar); outcome_gate = fzpost_outcome_gate (post-SETUP: REENTER when a later REENTER
              used the SETUP as its R5)
  block_key   'BLOCK:<fz_block_reason>' when outcome_gate == BLOCK; 'WATCH:<fz_block_reason>' when outcome_gate == WATCH
              and a block reason is set (a refused TAKE branch that fell through to WATCH, e.g. leave_into_recycle);
              otherwise the outcome_gate itself (TAKE / REENTER / WATCH). Same definition as the local h1_common.py
  loser       label net <= 0 (costs included); winner = net > 0
  precision   P(loser | skipped); recall = P(skipped | loser); lift = precision / base loser rate (1.0 = random skipping)
  winner recall   count: P(kept | winner); |net|-weighted: kept winners' net / all winners' net
  big winner  label pts >= 50; huge >= 100 (the "late runners")
  pts bucket  (<=-50, (-50,-20], (-20,0], (0,20], (20,50], (50,100], >100); hold bucket (bars) 1-5, 6-15, 16-30, 31-60,
              61-120, 121-375, >375 on both timeframes (bars, not minutes)
  visit bin   fz_visit_n: 1 / 2 / 3 / 4+ / none (no ref room)
  variants    (all pre-declared; every one is a ledger row under family h1/<variant>)
              frozen                    keep = fz_traded
              take_only                 keep = fz_gate == TAKE (as of the bar)
              take_or_reenter_at_setup  keep = fz_gate in (TAKE, REENTER) (as of the bar)
              not_block                 keep = fzpost_outcome_gate != BLOCK (WATCH rows treated as taken; DIAGNOSTIC: uses a
                                        post column)
              skip_only:<block_key>     keep = block_key != key (skip only that key; DIAGNOSTIC: block_key uses the post
                                        outcome gate)
  FZ book     the ST7/ST8 position's own net on the kept rows (fzpos_l1_net_inr under L1, fzpos_net_inr under L0; REENTER
              fills a bar later and exits by its own rules, e.g. band_reclaim), Foundation's label net on the other rows;
              scored as label '<label>_fzpos' under family h1/fz_book. The selection-only book = frozen on the label itself
  bridge      Foundation IS net -> FZ book net = avoided price move of the skipped rows (-sum pts x 65) + avoided costs of
              the skipped rows (sum cost_inr = charges + 2 x 5 pts x 65 slippage) + REENTER exit delta (fzpos net - label net
              on kept rows). Cost avoidance is what any gate that trades less collects: reported, never counted as edge
  group tables  descriptive decompositions of the frozen ledger row by as-of and post columns (no rule is chosen on them)
"""
import os, sys, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np, pandas as pd
import harness as H

BIG, HUGE = 50.0, 100.0
PTS_BINS = [-np.inf, -50, -20, 0, 20, 50, 100, np.inf]
PTS_LABELS = ["<=-50", "(-50,-20]", "(-20,0]", "(0,20]", "(20,50]", "(50,100]", ">100"]
HOLD_BINS = [0, 5, 15, 30, 60, 120, 375, np.inf]
HOLD_LABELS = ["1-5", "6-15", "16-30", "31-60", "61-120", "121-375", ">375"]
GROUPS = ["outcome_gate", "gate_at", "block_key", "read", "branch", "take_why", "hour_bin", "dir", "visit_bin", "zone_kind",
          "exit_reason", "pts_bucket", "hold_bucket"]
TWO_WAY = [("read", "outcome_gate"), ("hour_bin", "kept"), ("pts_bucket", "kept"), ("hold_bucket", "kept"), ("read", "kept"),
           ("exit_reason", "kept"), ("hour_bin", "outcome_gate"), ("pts_bucket", "outcome_gate")]
LOCAL = os.path.join(OUT, "..", "built", "study")
T0 = time.time()
LOG = open(os.path.join(HERE, "h1_gate_audit.log"), "a", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def txt(s):
    return s.astype(object).where(s.notna(), "none").astype(str)


def audit_frame(T):
    """The IS audit frame: one row per IS unit with the gate columns, the label outcome and the buckets."""
    F = T.F
    pre = "l1_" if T.label == "L1" else "fnd_"
    x = pd.DataFrame(dict(
        row=np.arange(T.n), setup_i=F.setup_i.to_numpy(), time=F.time.astype(str).to_numpy(), date=F.date.astype(str).to_numpy(),
        session=T.session, dir=txt(F.dir), hour_bin=txt(F.hour_bin), read=txt(F.fz_read), gate_at=txt(F.fz_gate),
        outcome_gate=txt(F.fzpost_outcome_gate), block_reason=txt(F.fz_block_reason), branch=txt(F.fz_branch),
        take_why=txt(F.fz_take_why), watch_kind=txt(F.fz_watch_kind), zone_kind=txt(F.fz_zone_kind),
        entered_read=txt(F.fz_entered_read), visit_n=F.fz_visit_n.to_numpy(dtype=float),
        kept=F.fz_traded.astype(bool).to_numpy().astype(int), pos_kind=txt(F.fzpos_kind),
        net=T.net, pts=T.pts, win=T.win.astype(int), exit_reason=txt(F[pre + "exit_reason"]),
        bars_held=F[pre + "bars_held"].to_numpy(dtype=float), exit_time=F[pre + "exit_time"].astype(str).to_numpy(),
        cost=F[pre + "cost_inr"].to_numpy(dtype=float), gross_after_slip=F[pre + "gross_inr"].to_numpy(dtype=float),
        fz_net=np.where(F.fz_traded.astype(bool), F["fzpos_l1_net_inr" if T.label == "L1" else "fzpos_net_inr"].to_numpy(dtype=float), T.net),
        fz_exit_reason=txt(F["fzpos_l1_exit_reason" if T.label == "L1" else "fzpos_exit_reason"]),
        mfe=F[pre + "mfe_pts"].to_numpy(dtype=float), mae=F[pre + "mae_pts"].to_numpy(dtype=float),
        sl_dist_pts=F.sl_dist_pts.to_numpy(dtype=float)))
    x["skipped"] = 1 - x.kept
    x["loser"] = 1 - x.win
    x["big"] = (x.pts >= BIG).astype(int); x["huge"] = (x.pts >= HUGE).astype(int)
    x["pts_bucket"] = pd.cut(x.pts, PTS_BINS, labels=PTS_LABELS, right=True).astype(str)
    x["hold_bucket"] = pd.cut(x.bars_held, HOLD_BINS, labels=HOLD_LABELS, right=True).astype(str)
    x["visit_bin"] = x.visit_n.map(lambda v: "none" if pd.isna(v) else ("4+" if v >= 4 else str(int(v))))
    x["block_key"] = np.where(x.outcome_gate == "BLOCK", "BLOCK:" + x.block_reason,
                              np.where((x.outcome_gate == "WATCH") & (x.block_reason != "none"), "WATCH:" + x.block_reason, x.outcome_gate))
    x["block_key_asof"] = np.where(x.gate_at == "BLOCK", "BLOCK:" + x.block_reason,
                                   np.where((x.gate_at == "WATCH") & (x.block_reason != "none"), "WATCH:" + x.block_reason, x.gate_at))
    x["cross_session"] = (x.exit_time.str[:10] != x.date).astype(int)
    return x[T.is_mask].reset_index(drop=True)


def variants(x):
    v = {"frozen": x.kept == 1, "take_only": x.gate_at == "TAKE", "take_or_reenter_at_setup": x.gate_at.isin(["TAKE", "REENTER"]),
         "not_block": x.outcome_gate != "BLOCK"}
    for k in sorted(x.block_key[x.block_key.str.contains(":")].unique()):
        v[f"skip_only:{k}"] = x.block_key != k
    return v


def full_mask(T, x, m):
    keep = np.zeros(T.n, dtype=bool); keep[x.row.to_numpy()[np.asarray(m, dtype=bool)]] = True
    return keep


def group_table(x, by):
    g = x.groupby(by, observed=True, dropna=False)
    k = x[x.kept == 1].groupby(by, observed=True, dropna=False); s = x[x.kept == 0].groupby(by, observed=True, dropna=False)
    t = pd.DataFrame(dict(n=g.size(), kept=g.kept.sum(), kept_share=g.kept.mean().round(4), net=g.net.sum().round(2),
                          mean=g.net.mean().round(2), win_rate=g.win.mean().round(4), winners=g.win.sum(), pts=g.pts.sum().round(2),
                          big=g.big.sum(), big_skipped=s.big.sum(), huge=g.huge.sum(), huge_skipped=s.huge.sum(),
                          kept_net=k.net.sum().round(2), skipped_net=s.net.sum().round(2), kept_mean=k.net.mean().round(2),
                          skipped_mean=s.net.mean().round(2), kept_win_rate=k.win.mean().round(4), skipped_win_rate=s.win.mean().round(4)))
    for c in ("kept_net", "skipped_net", "big_skipped", "huge_skipped"): t[c] = t[c].fillna(0)
    t["kept_minus_skipped"] = (t.kept_mean - t.skipped_mean).round(2)
    return t.reset_index()


def two_way(x, a, b):
    ct = x.pivot_table(index=a, columns=b, values="net", aggfunc=["count", "sum", "mean"], observed=True, fill_value=0)
    ct.columns = [f"{s}_{c}" for s, c in ct.columns]
    w = x.pivot_table(index=a, columns=b, values="win", aggfunc="sum", observed=True, fill_value=0)
    for c in w.columns: ct[f"winners_{c}"] = w[c]
    return ct.round(2).reset_index()


def md_table(df, cols=None, maxrows=40):
    df = df if cols is None else df[cols]
    df = df.head(maxrows)
    head = "| " + " | ".join(str(c) for c in df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    body = "".join("| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else (f"{v:,.2f}" if isinstance(v, float) else str(v)) for v in r) + " |\n" for r in df.itertuples(index=False))
    return head + body


def run(tf, label, md):
    T = H.load(tf, label)
    x = audit_frame(T)
    tag = f"{tf}_{label}"
    log(f"== {tag}: IS units {len(x)} kept {int(x.kept.sum())} | as-of gate {dict(x.gate_at.value_counts())} | outcome {dict(x.outcome_gate.value_counts())}")
    R = dict(tf=tf, label=label, n_is=int(len(x)), kept_n=int(x.kept.sum()), base_loser_rate=round(float(x.loser.mean()), 4),
             base_win_rate=round(float(x.win.mean()), 4), all_mean=round(float(x.net.mean()), 2), all_net=round(float(x.net.sum()), 2),
             mean_cost=round(float(x.cost.mean()), 2), winners_n=int(x.win.sum()), winners_net=round(float(x.net[x.win == 1].sum()), 2),
             big_n=int(x.big.sum()), huge_n=int(x.huge.sum()),
             gate_at_counts={k: int(v) for k, v in x.gate_at.value_counts().items()},
             outcome_gate_counts={k: int(v) for k, v in x.outcome_gate.value_counts().items()},
             block_key_counts={k: int(v) for k, v in x.block_key.value_counts().items()},
             asof_vs_outcome=pd.crosstab(x.gate_at, x.outcome_gate).to_dict())
    md.append(f"\n# {tf} / {label} (IS: {len(x)} units, {int(x.kept.sum())} kept by ST7/ST8, base loser rate {R['base_loser_rate']}, mean cost {R['mean_cost']} INR)\n")
    # ---------------------------------------------------------------- the variants through the harness
    V = {}
    for name, m in variants(x).items():
        fam = "h1/skip_only" if name.startswith("skip_only:") else f"h1/{name}"
        cfg = {"keep": name, "block_key": name.split(":", 1)[1]} if name.startswith("skip_only:") else {"keep": name}
        cfg["uses_post_column"] = name in ("frozen", "not_block") or name.startswith("skip_only:")
        r = H.score(T, full_mask(T, x, m), fam, cfg, script=__file__)
        r["lift"] = round(r["loser_precision"] / R["base_loser_rate"], 3) if r["loser_precision"] is not None else None
        r["winners_net_skipped_share"] = round(1 - r["winner_recall_weighted"], 4) if r["winner_recall_weighted"] is not None else None
        sk = ~np.asarray(m, dtype=bool)
        r["big_skipped"] = int((x.big.to_numpy(dtype=bool) & sk).sum()); r["huge_skipped"] = int((x.huge.to_numpy(dtype=bool) & sk).sum())
        r["big_net_skipped"] = round(float(x.net[(x.big == 1) & sk].sum()), 2)
        r["go_no_go"] = H.go_no_go(r, tf)[1]
        V[name] = r
        log(f"  {name:38s} id {r['id']} kept {r['kept_n']:5d} ({r['kept_share']:.3f}) diff {r['diff']!s:>9} pct {r['control_pct']!s:>5} p {r['perm_p']!s:>6} "
            f"L-rec {r['loser_recall']} L-prec {r['loser_precision']} lift {r['lift']} W-rec {r['winner_recall']} W-rec$ {r['winner_recall_weighted']} "
            f"top10skip {r['top_decile_winners_skipped']} PF {r['kept_pf']} blocks {r['sign_blocks']}")
    R["variants"] = V
    cols = ["variant", "id", "kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "control_pct", "perm_p", "loser_recall",
            "loser_precision", "lift", "winner_recall", "winner_recall_weighted", "top_decile_winners_skipped", "big_skipped", "huge_skipped",
            "kept_pf", "kept_mean_slip8", "sign_blocks", "kept_win_rate", "skipped_win_rate"]
    vt = pd.DataFrame([dict(variant=k, **{c: v.get(c) for c in cols if c != "variant"}) for k, v in V.items()])
    vt.to_csv(os.path.join(HERE, f"h1_{tag}_variants.csv"), index=False)
    md.append("## Variants (harness ledger rows, IS)\n\n" + md_table(vt, cols))
    # ---------------------------------------------------------------- the FZ book vs the selection-only book, and the bridge
    fz_net_all = np.where(T.F.fz_traded.astype(bool), T.F["fzpos_l1_net_inr" if label == "L1" else "fzpos_net_inr"].to_numpy(dtype=float), T.net)
    Tb = T.with_label(f"{label}_fzpos", fz_net_all, T.exit_bar, T.pts)
    rb = H.score(Tb, T.F.fz_traded.astype(bool).to_numpy(), "h1/fz_book", {"keep": "frozen", "net": "fzpos net on kept rows, label net elsewhere", "uses_post_column": True},
                 script=__file__, note="the ST7/ST8 book itself (REENTER exits differ from Foundation's); the exit bar is the label's (splitter not used here)")
    k = x.kept == 1
    reenter = x.pos_kind == "REENTER"
    bridge = dict(foundation_is_net=round(float(x.net.sum()), 2), fz_book_net=round(float(x.fz_net[k].sum()), 2),
                  selection_only_net=round(float(x.net[k].sum()), 2), n_skipped=int((~k).sum()), n_kept=int(k.sum()), n_reenter=int(reenter.sum()),
                  avoided_price_move=round(float(-(x.gross_after_slip[~k] + 650.0).sum()), 2), avoided_costs=round(float(x.cost[~k].sum()), 2),
                  reenter_exit_delta=round(float((x.fz_net - x.net)[k].sum()), 2), reenter_rows_changed=int(((x.fz_net - x.net).abs() > 0.01).sum()),
                  fz_exit_reasons_on_reenter={kk: int(v) for kk, v in x.fz_exit_reason[reenter].value_counts().items()},
                  label_exit_reasons_on_reenter={kk: int(v) for kk, v in x.exit_reason[reenter].value_counts().items()})
    bridge["closes"] = abs(bridge["foundation_is_net"] + bridge["avoided_price_move"] + bridge["avoided_costs"] + bridge["reenter_exit_delta"] - bridge["fz_book_net"]) < 0.05
    gain = bridge["fz_book_net"] - bridge["foundation_is_net"]
    bridge["gain_over_foundation"] = round(gain, 2)
    bridge["cost_avoidance_share_of_gain"] = round(bridge["avoided_costs"] / gain, 4) if gain else None
    bridge["selection_share_of_gain"] = round((bridge["avoided_price_move"] + bridge["reenter_exit_delta"]) / gain, 4) if gain else None
    bridge["fz_book"] = {c: rb.get(c) for c in ("id", "kept_n", "kept_mean", "kept_pf", "kept_mean_slip8", "diff", "control_pct", "perm_p", "kept_win_rate")}
    bridge["selection_only"] = {c: V["frozen"].get(c) for c in ("id", "kept_n", "kept_mean", "kept_pf", "kept_mean_slip8", "diff", "control_pct", "perm_p", "kept_win_rate")}
    R["bridge"] = bridge
    log(f"  bridge: Foundation {bridge['foundation_is_net']:,.0f} + price {bridge['avoided_price_move']:,.0f} + costs {bridge['avoided_costs']:,.0f} + reenter {bridge['reenter_exit_delta']:,.0f} = FZ {bridge['fz_book_net']:,.0f} (closes {bridge['closes']}); "
        f"cost share of gain {bridge['cost_avoidance_share_of_gain']}; FZ book kept mean {rb['kept_mean']} vs selection-only {V['frozen']['kept_mean']}")
    md.append("## The ST7/ST8 book vs the selection-only book (IS)\n\n" + md_table(pd.DataFrame([
        dict(book="selection-only (Foundation label net on kept rows)", **bridge["selection_only"]),
        dict(book="FZ book (fzpos net on kept rows)", **bridge["fz_book"])])) +
        "\nBridge (INR): " + ", ".join(f"{kk} = {bridge[kk]:,.2f}" for kk in ("foundation_is_net", "avoided_price_move", "avoided_costs", "reenter_exit_delta", "fz_book_net")) +
        f"; closes = {bridge['closes']}; gain over Foundation = {gain:,.2f}, of which cost avoidance {bridge['cost_avoidance_share_of_gain']}, selection (price + REENTER exits) {bridge['selection_share_of_gain']}\n")
    # ---------------------------------------------------------------- group tables
    tabs = {}
    for by in GROUPS:
        t = group_table(x, by)
        t.to_csv(os.path.join(HERE, f"h1_{tag}_by_{by}.csv"), index=False)
        tabs[by] = t.to_dict(orient="records")
        md.append(f"## by {by}\n\n" + md_table(t, ["%s" % by, "n", "kept", "kept_share", "net", "mean", "win_rate", "winners", "big", "big_skipped", "huge", "huge_skipped", "kept_mean", "skipped_mean", "kept_minus_skipped"]))
    for a, b in TWO_WAY:
        ct = two_way(x, a, b)
        ct.to_csv(os.path.join(HERE, f"h1_{tag}_x_{a}_{b}.csv"), index=False)
        tabs[f"{a}_x_{b}"] = ct.to_dict(orient="records")
        if (a, b) in (("read", "outcome_gate"), ("hour_bin", "kept"), ("pts_bucket", "kept")):
            md.append(f"## {a} x {b}\n\n" + md_table(ct))
    R["tables"] = tabs
    # ---------------------------------------------------------------- the big-winner audit
    W = x[x.win == 1]; B = x[x.big == 1].sort_values("pts", ascending=False); Hg = x[x.huge == 1]
    def where(df, by):
        g = df.groupby(by, observed=True)
        return g.agg(n=("kept", "size"), kept=("kept", "sum"), skipped=("skipped", "sum"), pts=("pts", "sum"), net=("net", "sum"),
                     net_skipped=("net", lambda s: s[df.loc[s.index, "kept"] == 0].sum())).round(2).reset_index()
    big = dict(n=len(B), pts=round(float(B.pts.sum()), 2), net=round(float(B.net.sum()), 2), skipped_n=int(B.skipped.sum()),
               skipped_net=round(float(B.net[B.kept == 0].sum()), 2), skipped_share=round(float(B.skipped.mean()), 4) if len(B) else None,
               share_of_winners_net=round(float(B.net.sum() / W.net.sum()), 4) if len(W) else None,
               huge_n=len(Hg), huge_skipped=int(Hg.skipped.sum()), huge_net=round(float(Hg.net.sum()), 2), huge_net_skipped=round(float(Hg.net[Hg.kept == 0].sum()), 2),
               median_bars_held_big=float(B.bars_held.median()) if len(B) else None, median_bars_held_all_winners=float(W.bars_held.median()) if len(W) else None,
               median_bars_held_losers=float(x.bars_held[x.win == 0].median()),
               eod_exit_share_big=round(float((B.exit_reason == "eod").mean()), 4) if len(B) else None,
               by_block_key=where(B, "block_key").to_dict(orient="records"), by_read=where(B, "read").to_dict(orient="records"),
               by_hour=where(B, "hour_bin").to_dict(orient="records"), by_hold=where(B, "hold_bucket").to_dict(orient="records"),
               by_exit_reason=where(B, "exit_reason").to_dict(orient="records"),
               huge_by_block_key=where(Hg, "block_key").to_dict(orient="records") if len(Hg) else [],
               winners_by_hold=where(W, "hold_bucket").to_dict(orient="records"))
    cols = ["setup_i", "time", "dir", "hour_bin", "read", "gate_at", "outcome_gate", "block_reason", "block_key", "branch", "take_why", "visit_n",
            "pts", "net", "exit_reason", "bars_held", "hold_bucket", "exit_time", "kept", "pos_kind", "fz_net", "fz_exit_reason", "mfe", "mae", "sl_dist_pts"]
    B[cols].to_csv(os.path.join(HERE, f"h1_{tag}_big_winners_all.csv"), index=False)
    B[B.kept == 0][cols].to_csv(os.path.join(HERE, f"h1_{tag}_big_winners_skipped.csv"), index=False)
    R["big_winners"] = big
    md.append(f"## Big winners (pts >= {BIG:.0f}): {big['n']} rows, net {big['net']:,.0f} = {big['share_of_winners_net']} of all winners' net; skipped {big['skipped_n']} ({big['skipped_share']}) carrying {big['skipped_net']:,.0f}; "
              f"huge (>= {HUGE:.0f}) {big['huge_n']}, skipped {big['huge_skipped']} carrying {big['huge_net_skipped']:,.0f}\n\n"
              f"median bars held: big winners {big['median_bars_held_big']}, all winners {big['median_bars_held_all_winners']}, losers {big['median_bars_held_losers']}; eod-exit share of big winners {big['eod_exit_share_big']}\n\n"
              "### by block key\n\n" + md_table(where(B, "block_key")) + "\n### by read\n\n" + md_table(where(B, "read")) +
              "\n### by hour\n\n" + md_table(where(B, "hour_bin")) + "\n### by hold bucket\n\n" + md_table(where(B, "hold_bucket")) +
              "\n### all winners by hold bucket\n\n" + md_table(where(W, "hold_bucket")))
    log(f"  big winners {big['n']} skipped {big['skipped_n']} net skipped {big['skipped_net']:,.0f}; huge {big['huge_n']} skipped {big['huge_skipped']}")
    # ---------------------------------------------------------------- the family: PBO / SPA / effective trials / bootstrap / DSR
    rows = H.read_ledger("h1", tf=tf, label=label)
    rows = [r for r in rows if r["family"] != "h1/cpcv"]
    ids = list(dict.fromkeys(r["id"] for r in rows))
    vecs = [H.load_vectors(i) for i in ids]
    fam = dict(ledger_rows=len(rows), candidates=len(ids), ids=ids,
               pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"h1|{tag}"),
               effective_trials=H.effective_trials(vecs))
    fv = H.load_vectors(V["frozen"]["id"])
    fam["bootstrap_frozen"] = H.bootstrap_ci(fv, tag=f"h1|{tag}|frozen")
    def sharpe(v):
        m = v["kept_n"] > 0; s = v["kept_sum"][m] / v["kept_n"][m]
        return float(s.mean() / s.std(ddof=1)) if len(s) > 2 and s.std(ddof=1) else np.nan
    srs = np.array([sharpe(v) for v in vecs]); srs = srs[np.isfinite(srs)]
    m = fv["kept_n"] > 0
    fam["dsr_frozen"] = H.deflated_sharpe((fv["kept_sum"][m] / fv["kept_n"][m]), len(ids), float(srs.var(ddof=1)) if len(srs) > 1 else None)
    fam["go_no_go_frozen"] = H.go_no_go(V["frozen"], tf, pbo_value=fam["pbo_diff"]["pbo"], dsr=fam["dsr_frozen"], spa_p=fam["spa"]["spa_p"], boot=fam["bootstrap_frozen"])
    R["family"] = fam
    log(f"  family: {len(ids)} candidates, eff trials {fam['effective_trials']}, PBO(diff) {fam['pbo_diff']['pbo']}, PBO(kept) {fam['pbo_kept_mean']['pbo']}, SPA p {fam['spa']['spa_p']} (best = {ids[fam['spa']['best']]}), "
        f"boot diff CI {fam['bootstrap_frozen']['diff_ci']}, DSR p {fam['dsr_frozen'].get('p')}, frozen go/no-go {fam['go_no_go_frozen'][0]}")
    md.append("## Family (h1 variants, IS)\n\n" + md_table(pd.DataFrame([dict(candidates=len(ids), effective_trials=fam["effective_trials"], pbo_diff=fam["pbo_diff"]["pbo"],
              pbo_kept_mean=fam["pbo_kept_mean"]["pbo"], spa_p=fam["spa"]["spa_p"], rc_p=fam["spa"]["rc_p"], spa_best=[k for k, v in V.items() if v["id"] == ids[fam["spa"]["best"]]] or ids[fam["spa"]["best"]],
              spa_best_mean_gain=fam["spa"]["best_mean_gain"], frozen_boot_diff_ci90=str(fam["bootstrap_frozen"]["diff_ci"]), frozen_boot_p_diff_le0=fam["bootstrap_frozen"]["diff_p_le0"],
              frozen_dsr_p=fam["dsr_frozen"].get("p"))])))
    return R, x


def crosscheck(x_l0_1m):
    """The local h1 tables (fz_v3/built/study/h1_1m_IS_by_*.csv: L0 label, 1 min, IS, the local build) against the same
    definitions on the cloud table. Only IS files are read."""
    out = {}
    lx = x_l0_1m.copy()
    lx["exit_reason"] = lx.exit_reason
    ren = {"outcome_gate": "outcome_gate", "gate_at": "gate_at", "block_key": "block_key", "read": "read", "branch": "branch", "take_why": "take_why",
           "hour_bin": "hour_bin", "dir": "dir", "visit_bin": "visit_bin", "zone_kind": "zone_kind", "exit_reason": "exit_reason", "pts_bucket": "pts_bucket",
           "hold_bucket": "hold_bucket", "cross_session": "cross_session", "pos_kind": "pos_kind", "entered_read": "entered_read"}
    for by in ren:
        p = os.path.join(LOCAL, f"h1_1m_IS_by_{by}.csv")
        if not os.path.exists(p): out[by] = "local file missing"; continue
        loc = pd.read_csv(p, dtype={by: str}); loc[by] = loc[by].astype(str)
        g = lx.groupby(by, observed=True, dropna=False)
        s = lx[lx.kept == 0].groupby(by, observed=True, dropna=False); k = lx[lx.kept == 1].groupby(by, observed=True, dropna=False)
        mine = pd.DataFrame(dict(n=g.size(), kept=g.kept.sum(), net=g.net.sum().round(2), winners=g.win.sum(), big=g.big.sum(), huge=g.huge.sum(),
                                 kept_net=k.net.sum().round(2), skipped_net=s.net.sum().round(2), big_skipped=s.big.sum())).fillna(0).reset_index()
        mine[by] = mine[by].astype(str)
        if by == "cross_session": loc[by] = loc[by].astype(str)
        m = loc.merge(mine, on=by, how="outer", suffixes=("_local", "_cloud"), indicator=True)
        diffs = {c: float(np.nanmax(np.abs(m[f"{c}_local"].astype(float) - m[f"{c}_cloud"].astype(float)))) if len(m) else None
                 for c in ("n", "kept", "net", "winners", "big", "huge", "kept_net", "skipped_net", "big_skipped")}
        out[by] = dict(groups_local=int(len(loc)), groups_cloud=int(len(mine)), unmatched=int((m["_merge"] != "both").sum()),
                       max_abs_diff=diffs, agree=bool((m["_merge"] == "both").all() and all(v is not None and v < 0.01 for v in diffs.values())))
    # the big-winner list
    p = os.path.join(LOCAL, "h1_1m_big_winners_skipped_IS.csv")
    if os.path.exists(p):
        loc = pd.read_csv(p); mine = lx[(lx.big == 1) & (lx.kept == 0)]
        out["big_winners_skipped"] = dict(local_n=int(len(loc)), cloud_n=int(len(mine)), same_setups=bool(set(loc.setup_i) == set(mine.setup_i)),
                                          pts_sum_local=round(float(loc.fnd_pts.sum()), 2), pts_sum_cloud=round(float(mine.pts.sum()), 2))
    return out


if __name__ == "__main__":
    log(f"h1_gate_audit start {time.ctime()} ledger sha before {H.ledger_sha()}")
    md = ["# H1 gate audit: tables (auto-generated by h1_gate_audit.py; IS only)\n"]
    S = {"definitions": __doc__, "results": {}}
    frames = {}
    for tf in ("minute", "5minute"):
        for label in ("L1", "L0"):
            R, x = run(tf, label, md)
            S["results"][f"{tf}/{label}"] = R; frames[(tf, label)] = x
    S["crosscheck_local_1m_L0"] = crosscheck(frames[("minute", "L0")])
    log("crosscheck:", json.dumps({k: (v["agree"] if isinstance(v, dict) and "agree" in v else v) for k, v in S["crosscheck_local_1m_L0"].items()}))
    S["ledger_sha_after"] = H.ledger_sha(); S["run_s"] = round(time.time() - T0, 1)
    json.dump(S, open(os.path.join(HERE, "h1_summary.json"), "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
    open(os.path.join(HERE, "TABLES.md"), "w", encoding="utf-8").write("\n".join(md))
    log(f"done in {S['run_s']}s; ledger sha after {S['ledger_sha_after']}")
