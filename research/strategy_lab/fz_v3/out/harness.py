"""FZ v3 validation harness: the ONE evaluator every gate candidate goes through (DESIGN_PANEL: quant-ml-canon-purged-cpcv-pbo
merged with decision-making-3; both judges' fixes).

    import harness as H
    T = H.load("minute")                     # the unit table: one row per Foundation SETUP taken under the L1 (15:25) book
    for tr, te in H.purged_splits(T): ...    # 12 contiguous IS session blocks, purge by the label's own exit bar, 3-session embargo
    res = H.score(T, keep_mask, family="h2", config={...}, script=__file__)      # appends to the ledger; the only way to get numbers
    paths = H.cpcv_paths(T, oof_by_split)    # 11 CPCV backtest paths from the 66 (train, test) splits
    H.pbo(T, ids)  H.deflated_sharpe(...)  H.bootstrap_ci(...)  H.spa(...)  H.break_tests(T)  H.go_no_go(res, ...)

Pre-registered (BRIEF.md + DESIGN_PANEL.md, fixed before any candidate was scored):
  unit        a Foundation SETUP with its own engine trade, taken under the book ST13/ST14 will trade: label L1 = the engine's
              stop / next-CHoCH exit cut at the entry session's 15:25 bar (lab.eod_cut), priced at lot 65, 5 pts slippage per
              side, lab.trade_charges(ZERODHA_NFO_FUT). A SETUP opening at or after 15:25 is not a unit (not taken). L0 (the
              engine's uncut trade) is a robustness label only.
  IS / OOS    IS = sessions 2021-10-01 .. 2025-12-31; OOS = 2026-01-01 .. 2026-09-25, opened once by oos_once.py alone.
  splitter    12 contiguous blocks of IS sessions (equal session counts); a training row is purged when its label lifetime
              [entry bar, exit bar] intersects the test block's bar range; 3 sessions after each test block are embargoed.
  CPCV        N = 12, k = 2: 66 splits, 11 paths; a candidate's path distribution (median, 5th percentile) is what counts.
  statistic   kept-vs-skipped mean net (INR per trade), never net alone (every skip saves ~1,100 INR of costs); the
              session-matched random control percentile (fz_report.random_control, 2,000 draws, seed 'fz'); the kept-vs-refused
              permutation p (fz_report.permutation_p); loser recall / precision; |net|-weighted winner recall; the top-decile
              winners skipped; the same difference with the top 1% winners removed; slippage 3 / 5 / 8 pts per side.
  ledger      append-only JSONL (ledger/trials.jsonl) + per-candidate per-session vectors (ledger/vectors/<id>.npz); PBO, DSR
              and SPA read the ledger, so every trial counts.
  go / no-go  PBO <= 0.2 over the family; CPCV 5th-percentile diff > 0; DSR p < 0.1; kept share >= 20%; kept n >= 300 (1m) /
              80 (5m); diff > 0 with the top 1% winners removed; the kept book's mean net > 0 at 8 pts slippage per side (the
              difference itself is slippage-invariant: every trade moves by the same amount); diff > 0 in >= 8 of 12 blocks;
              control percentile >= 95; SPA p <= 0.10; bootstrap 90% CI of the diff excludes 0. At most three frozen candidates
              across all studies reach OOS.
"""
import os, sys, json, hashlib, itertools, math, datetime as D
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from scipy import stats as sst
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", ".."))
if LAB not in sys.path: sys.path.insert(0, LAB)
import fz_report                                                       # noqa: E402  read-only: the lab's control definitions
import lab                                                             # noqa: E402  trade_charges only

DATA = os.path.join(HERE, "data")
LEDGER = os.path.join(HERE, "ledger")
IS_END = "2025-12-31"
N_BLOCKS, EMBARGO_SESSIONS, CPCV_K, CSCV_S = 12, 3, 2, 16
CONTROL_DRAWS, SEED = 2000, "fz"
BOOT_DRAWS, BOOT_MEAN_BLOCK = 2000, 10
LOT, SLIP = 65, 5.0
CS = json.load(open(os.path.join(LAB, "config", "charges.json"), encoding="utf-8"))["ZERODHA_NFO_FUT"]
GO = dict(pbo_max=0.2, cpcv_p5_diff_min=0.0, dsr_p_max=0.1, kept_share_min=0.20, kept_n_min={"minute": 300, "5minute": 80},
          top1_removed_diff_min=0.0, slip8_kept_mean_min=0.0, sign_blocks_min=8, control_pct_min=95.0, spa_p_max=0.10, boot_ci=0.90)
LABEL_PREFIX = ("fnd_", "l1_", "fwd_", "fzpos_", "fzpost_")            # never features
NOT_FEATURES = {"setup_i", "time", "date", "session_idx", "choch_i", "choch_time", "contract", "split", "in_warmup", "fz_traded",
                "open", "high", "low", "close", "sess_open", "prev_close", "prot_lvl", "last_sh_px", "last_sl_px", "choch_lvl",
                "room_edge", "room_edge_id", "card_zone_id", "card_left_id", "card_in_id", "card_last_hunt_at", "card_last_reject_at",
                "fz_zone_id", "fz_left_id", "fz_in_id", "fz_entered_zone_id", "fz_watch_band_id", "fz_band_lo", "fz_band_hi",
                "card_gap_pts", "vol", "vol_med20_prior", "vol_med60_prior", "card_this_vol", "card_first_vol", "card_prev_vol",
                "fz_this_vol", "fz_first_vol", "traded", "engine_skipped", "minute_of_day", "hhmm"}
MAX_LEVELS = 16


def _sha(s): return hashlib.sha1(s.encode() if isinstance(s, str) else s).hexdigest()[:16]


def file_sha(path):
    return _sha(open(path, "rb").read().replace(b"\r\n", b"\n")) if path and os.path.exists(path) else None


# ---------------------------------------------------------------- the unit table
class Table:
    """One row per unit (a Foundation SETUP taken under the label's book), IS rows first in time order then OOS."""

    def __init__(self, tf, label, F, TR, sessions):
        self.tf, self.label, self.F, self.TR, self.sessions = tf, label, F, TR, sessions
        self.n = len(F)
        self.setup_i = F.setup_i.to_numpy()
        self.entry_bar = self.setup_i
        self.session = F.session_idx.to_numpy()
        self.day = F.date.astype(str).to_numpy()
        self.is_mask = (F.split.astype(str) == "IS").to_numpy()
        self.oos_mask = ~self.is_mask
        pre = "l1_" if label == "L1" else "fnd_"
        self.net = F[pre + "net_inr"].to_numpy(dtype=float)
        self.pts = F[pre + "pts"].to_numpy(dtype=float)
        self.exit_bar = F[pre + "exit_i"].to_numpy(dtype=float).astype(int)
        self.win = self.net > 0
        self.entry_px = TR.entry_px.to_numpy(dtype=float); self.exit_px = TR[pre + "exit_px" if label == "L1" else "exit_px"].to_numpy(dtype=float)
        self.up = (F.dir.astype(str) == "up").to_numpy()
        self.net_slip = {s: self._net_at_slip(s) for s in (3.0, 5.0, 8.0)}
        assert np.allclose(self.net_slip[5.0], self.net, atol=0.02), "slippage 5 must reproduce the label's net"
        # 12 contiguous blocks of IS sessions (all IS sessions, active or not, so the blocks are time-contiguous)
        is_sess = sessions[sessions.split.astype(str) == "IS"].session_idx.to_numpy()
        edges = np.linspace(0, len(is_sess), N_BLOCKS + 1).round().astype(int)
        self.block_sessions = [is_sess[edges[b]:edges[b + 1]] for b in range(N_BLOCKS)]
        sess2block = {int(s): b for b in range(N_BLOCKS) for s in self.block_sessions[b]}
        self.block = np.array([sess2block.get(int(s), -1) for s in self.session])
        first_bar = dict(zip(sessions.session_idx, sessions.first_bar)); last_bar = dict(zip(sessions.session_idx, sessions.last_bar))
        self.block_range = [(int(first_bar[int(bs[0])]), int(last_bar[int(bs[-1])])) for bs in self.block_sessions]
        self.block_embargo = [set(int(s) for s in is_sess[edges[b + 1]:edges[b + 1] + EMBARGO_SESSIONS]) for b in range(N_BLOCKS)]
        self.active_sessions = np.array(sorted(set(self.session[self.is_mask].tolist())))
        self._asof = None

    def _net_at_slip(self, s):
        out = np.empty(self.n)
        for i in range(self.n):
            e, x = self.entry_px[i], self.exit_px[i]
            if self.up[i]: buy, sell = e + s, x - s
            else: sell, buy = e - s, x + s
            out[i] = (sell - buy) * LOT - lab.trade_charges(CS, buy, sell, LOT)["total"]
        return out

    def asof_columns(self):
        """Feature-eligible columns: every column that is not a label, a post-SETUP field, an identity or a raw price / id."""
        if self._asof is None:
            self._asof = [c for c in self.F.columns if not c.startswith(LABEL_PREFIX) and c not in NOT_FEATURES]
        return list(self._asof)

    def with_label(self, name, net, exit_bar, pts=None):
        """A copy of the table under another label (L2 / L3 ...): net and exit bar per row; the splitter purges by exit_bar."""
        T = Table.__new__(Table); T.__dict__.update(self.__dict__)
        T.label, T.net, T.exit_bar = name, np.asarray(net, dtype=float), np.asarray(exit_bar).astype(int)
        T.pts = np.asarray(pts, dtype=float) if pts is not None else T.pts; T.win = T.net > 0
        T.net_slip = {s: self.net_slip[s] + (T.net - self.net) for s in self.net_slip}
        return T


def load(tf, label="L1"):
    """The unit table of a timeframe from fz_v3/out/data/<tf>/ (label L1 by default; L0 = the engine's uncut trade)."""
    F = pd.read_parquet(os.path.join(DATA, tf, "features.parquet"))
    TR = pd.read_parquet(os.path.join(DATA, tf, "trades.parquet")).set_index("entry_i")
    S = pd.read_parquet(os.path.join(DATA, tf, "sessions.parquet"))
    F = F[F.traded.astype(bool)]
    if label == "L1": F = F[F.l1_taken.astype(bool)]
    F = F.sort_values("setup_i").reset_index(drop=True)
    TR = TR.loc[F.setup_i.to_numpy()].reset_index()
    return Table(tf, label, F, TR, S)


def design(T, cols=None, max_levels=MAX_LEVELS):
    """Numeric design matrix over as-of columns: floats as they are (None -> NaN), booleans 0 / 1, text one-hot (<= max_levels
    levels, else dropped). Returns (X DataFrame, {encoded column: source column})."""
    cols = list(cols) if cols is not None else T.asof_columns()
    out, src = {}, {}
    for c in cols:
        s = T.F[c]
        if pd.api.types.is_bool_dtype(s): out[c] = s.astype(float).to_numpy(); src[c] = c; continue
        if pd.api.types.is_numeric_dtype(s): out[c] = s.to_numpy(dtype=float); src[c] = c; continue
        so = s.astype(object)
        vals = so.map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else z)
        if all(isinstance(z, (bool, np.bool_)) or z is None for z in vals):
            out[c] = vals.map(lambda z: np.nan if z is None else float(z)).to_numpy(dtype=float); src[c] = c; continue
        levels = sorted({str(z) for z in vals if z is not None})
        if len(levels) > max_levels: continue
        for lv in levels:
            k = f"{c}={lv}"; out[k] = (vals.map(lambda z: None if z is None else str(z)) == lv).astype(float).to_numpy(); src[k] = c
    return pd.DataFrame(out), src


# ---------------------------------------------------------------- the splitter
def _purge(T, train_idx, test_blocks):
    """Training rows whose label lifetime intersects a test block's bar range, or whose session is in its embargo, are dropped."""
    keep = np.ones(len(train_idx), dtype=bool)
    e0, e1 = T.entry_bar[train_idx], T.exit_bar[train_idx]
    ses = T.session[train_idx]
    for b in test_blocks:
        lo, hi = T.block_range[b]
        keep &= ~((e0 <= hi) & (e1 >= lo))
        keep &= ~np.isin(ses, list(T.block_embargo[b]))
    return train_idx[keep]


def purged_splits(T):
    """12 (train_idx, test_idx) over IS rows: test = one block; train = the other blocks, purged and embargoed."""
    is_idx = np.flatnonzero(T.is_mask)
    for b in range(N_BLOCKS):
        te = is_idx[T.block[is_idx] == b]
        tr = _purge(T, is_idx[T.block[is_idx] != b], [b])
        yield tr, te


def cpcv_splits(T):
    """66 (train_idx, test_idx, (a, b)) with two test blocks each (N = 12, k = 2), purged against both and their embargoes."""
    is_idx = np.flatnonzero(T.is_mask)
    for a, b in itertools.combinations(range(N_BLOCKS), CPCV_K):
        te = is_idx[np.isin(T.block[is_idx], [a, b])]
        tr = _purge(T, is_idx[~np.isin(T.block[is_idx], [a, b])], [a, b])
        yield tr, te, (a, b)


def cpcv_paths(T, oof_by_split):
    """11 backtest paths from the 66 CPCV splits. oof_by_split: {(a, b): array of decisions / scores for the rows of that
    split's test set, in the order cpcv_splits yields them}. Returns a list of 11 arrays over all rows (NaN outside IS): in
    path p, block g takes its prediction from the split that pairs g with its p-th other block."""
    is_idx = np.flatnonzero(T.is_mask)
    paths = [np.full(T.n, np.nan) for _ in range(N_BLOCKS - 1)]
    for (a, b), pred in oof_by_split.items():
        te = is_idx[np.isin(T.block[is_idx], [a, b])]
        pred = np.asarray(pred, dtype=float); assert len(pred) == len(te), "prediction length must match the split's test rows"
        for g, other in ((a, b), (b, a)):
            p = [x for x in range(N_BLOCKS) if x != g].index(other)
            m = T.block[te] == g
            paths[p][te[m]] = pred[m]
    for p in paths: assert not np.isnan(p[is_idx]).any(), "every IS row must have a prediction in every path"
    return paths


def check_splits(T):
    """Leakage checks of the splitter: no training row's lifetime intersects its test block, no training row sits in the
    embargo, every IS row is tested once in the 12-block scheme; returns the counts."""
    n_te = np.zeros(T.n, dtype=int); purged = []
    for b, (tr, te) in enumerate(purged_splits(T)):
        lo, hi = T.block_range[b]
        assert not ((T.entry_bar[tr] <= hi) & (T.exit_bar[tr] >= lo)).any()
        assert not np.isin(T.session[tr], list(T.block_embargo[b])).any()
        assert (T.block[te] == b).all()
        n_te[te] += 1; purged.append(int(T.is_mask.sum() - len(te) - len(tr)))
    assert (n_te[T.is_mask] == 1).all() and (n_te[T.oos_mask] == 0).all()
    return dict(blocks=N_BLOCKS, rows_is=int(T.is_mask.sum()), rows_oos=int(T.oos_mask.sum()), purged_per_block=purged,
                block_sessions=[len(bs) for bs in T.block_sessions], block_rows=[int((T.block == b).sum()) for b in range(N_BLOCKS)],
                cpcv_splits=sum(1 for _ in cpcv_splits(T)))


# ---------------------------------------------------------------- scoring (the only way to a number)
def _units(T, idx, gate="RAW"):
    return [dict(entry=int(T.setup_i[i]), setup=int(T.setup_i[i]), gate=gate, day=str(T.day[i]), exit_day=str(T.day[i]), legs=1,
                 net=float(T.net[i]), gross=float(T.net[i]), charges=0.0, slip=0.0, open=False) for i in idx]


def _split_rows(T, split):
    if split == "IS": return np.flatnonzero(T.is_mask)
    if split == "OOS":
        if os.path.basename(sys.argv[0]) != "oos_once.py":
            raise PermissionError("OOS rows are scored by oos_once.py alone (BRIEF protocol: OOS is opened once)")
        return np.flatnonzero(T.oos_mask)
    raise ValueError(split)


def metrics(T, keep, rows, tag, controls=True, draws=CONTROL_DRAWS):
    """Kept-vs-skipped metrics of a boolean keep mask over the rows `rows` of T (a subset of one split)."""
    keep = np.asarray(keep, dtype=bool)
    k = rows[keep[rows]]; s = rows[~keep[rows]]
    net, win = T.net, T.win
    nk, ns = len(k), len(s)
    m = dict(n=int(len(rows)), kept_n=int(nk), skipped_n=int(ns), kept_share=round(nk / len(rows), 4) if len(rows) else None,
             kept_net=round(float(net[k].sum()), 2), skipped_net=round(float(net[s].sum()), 2),
             kept_mean=round(float(net[k].mean()), 2) if nk else None, skipped_mean=round(float(net[s].mean()), 2) if ns else None,
             all_mean=round(float(net[rows].mean()), 2) if len(rows) else None,
             kept_win_rate=round(float(win[k].mean()), 4) if nk else None, skipped_win_rate=round(float(win[s].mean()), 4) if ns else None,
             kept_pf=None, kept_t=None, diff=None, diff_top1_removed=None, kept_mean_slip3=None, kept_mean_slip8=None,
             loser_recall=None, loser_precision=None, winner_recall=None, winner_recall_weighted=None, top_decile_winners_skipped=None,
             kept_sessions=int(len(set(T.session[k].tolist()))), sign_blocks=None, perm_p=None, control_pct=None, control_p_beat=None)
    if nk:
        w_, l_ = net[k][net[k] > 0], net[k][net[k] <= 0]
        m["kept_pf"] = round(float(w_.sum() / -l_.sum()), 3) if len(l_) and l_.sum() else None
        m["kept_t"] = round(float(net[k].mean() / (net[k].std(ddof=1) / math.sqrt(nk))), 2) if nk > 1 and net[k].std(ddof=1) else None
    if nk and ns:
        m["diff"] = round(float(net[k].mean() - net[s].mean()), 2)
        # slippage moves every trade's net by the same amount, so the kept-vs-skipped difference is invariant; what a marginal
        # gate must survive is the kept book's own expectancy at 3 / 8 pts per side
        for sl_ in (3.0, 8.0): m[f"kept_mean_slip{int(sl_)}"] = round(float(T.net_slip[sl_][k].mean()), 2)
        top = np.quantile(net[rows], 0.99); kk, ss_ = k[net[k] < top], s[net[s] < top]
        m["diff_top1_removed"] = round(float(net[kk].mean() - net[ss_].mean()), 2) if len(kk) and len(ss_) else None
        L = ~win[rows]; W = win[rows]
        skp = ~keep[rows]
        m["loser_recall"] = round(float((skp & L).sum() / L.sum()), 4) if L.sum() else None
        m["loser_precision"] = round(float((skp & L).sum() / skp.sum()), 4) if skp.sum() else None
        m["winner_recall"] = round(float((~skp & W).sum() / W.sum()), 4) if W.sum() else None
        wn = net[rows]
        m["winner_recall_weighted"] = round(float(wn[~skp & W].sum() / wn[W].sum()), 4) if W.sum() and wn[W].sum() else None
        if W.sum():
            q = np.quantile(wn[W], 0.9); big = W & (wn >= q)
            m["top_decile_winners_skipped"] = round(float((skp & big).sum() / big.sum()), 4) if big.sum() else None
        bl = T.block[rows]
        if (bl >= 0).all():
            m["sign_blocks"] = int(sum(1 for b in range(N_BLOCKS) if (keep[rows] & (bl == b)).sum() and (~keep[rows] & (bl == b)).sum()
                                      and net[rows][keep[rows] & (bl == b)].mean() > net[rows][~keep[rows] & (bl == b)].mean()))
        if controls:
            pp = fz_report.permutation_p(net[k].tolist(), net[s].tolist(), draws, SEED, tag)
            m["perm_p"] = pp["p"]
            rc = fz_report.random_control(_units(T, rows), _units(T, k, "SEL"), draws, SEED, tag)
            m["control_pct"], m["control_p_beat"], m["control_p50"] = rc["fz_pct"], rc["p_beat"], rc["p50"]
    return m


def session_vectors(T, keep, rows):
    """Per active session (sessions with a unit among rows): kept sum / n, skipped sum / n, all sum / n."""
    keep = np.asarray(keep, dtype=bool)
    ses = T.session[rows]; net = T.net[rows]; kp = keep[rows]
    S = np.array(sorted(set(ses.tolist())))
    idx = np.searchsorted(S, ses)
    out = {}
    for name, msk in (("kept", kp), ("skipped", ~kp), ("all", np.ones(len(rows), dtype=bool))):
        out[name + "_sum"] = np.bincount(idx, weights=net * msk, minlength=len(S))
        out[name + "_n"] = np.bincount(idx, weights=msk.astype(float), minlength=len(S))
    out["sessions"] = S
    return out


def candidate_id(family, config, label, tf):
    return _sha(json.dumps([family, config, label, tf], sort_keys=True, default=str))


def score(T, keep, family, config, script=None, split="IS", controls=True, draws=CONTROL_DRAWS, note=None):
    """Score a keep mask (boolean over T's rows) on one split and append the trial to the ledger. Returns the metrics dict
    with the candidate id. Every configuration a study tries goes through here, so PBO / DSR / SPA see the whole search."""
    rows = _split_rows(T, split)
    cid = candidate_id(family, config, T.label, T.tf)
    tag = f"{T.tf}|{T.label}|{split}|{cid}"
    m = metrics(T, keep, rows, tag, controls=controls, draws=draws)
    vec = session_vectors(T, keep, rows)
    os.makedirs(os.path.join(LEDGER, "vectors"), exist_ok=True)
    np.savez_compressed(os.path.join(LEDGER, "vectors", f"{cid}_{split}.npz"), **vec)
    rec = dict(id=cid, family=family, tf=T.tf, label=T.label, split=split, config=config, script=os.path.basename(script) if script else None,
               script_sha=file_sha(script), at=D.datetime.now().isoformat(timespec="seconds"), note=note, **m)
    with open(os.path.join(LEDGER, "trials.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, default=lambda z: z.item() if hasattr(z, "item") else str(z)) + "\n")
    return dict(rec)


def score_paths(T, paths, family, config, script=None, controls=False, threshold=None):
    """CPCV: score each of the 11 path masks (a path is a decision array over rows: booleans, or scores compared with
    `threshold` when given). Returns the per-path metrics and the distribution of diff (median, 5th percentile, min) and of
    the control percentile when controls is set; every path is a ledger row of family '<family>/cpcv'."""
    out = []
    for p, arr in enumerate(paths):
        keep = np.asarray(arr) >= threshold if threshold is not None else np.asarray(arr).astype(bool)
        out.append(score(T, keep, f"{family}/cpcv", dict(config, path=p), script=script, controls=controls))
    d = np.array([x["diff"] if x["diff"] is not None else np.nan for x in out], dtype=float)
    res = dict(paths=len(out), diff_median=round(float(np.nanmedian(d)), 2), diff_p5=round(float(np.nanquantile(d, 0.05)), 2),
               diff_min=round(float(np.nanmin(d)), 2), diff_share_positive=round(float((d > 0).mean()), 3),
               kept_share_median=round(float(np.median([x["kept_share"] for x in out])), 4))
    if controls:
        c = np.array([x["control_pct"] if x["control_pct"] is not None else np.nan for x in out], dtype=float)
        res.update(control_pct_median=round(float(np.nanmedian(c)), 1), control_pct_p5=round(float(np.nanquantile(c, 0.05)), 1))
    return res, out


# ---------------------------------------------------------------- the ledger
def read_ledger(family=None, tf=None, label=None, split="IS"):
    p = os.path.join(LEDGER, "trials.jsonl")
    if not os.path.exists(p): return []
    rows = [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]
    return [r for r in rows if (family is None or r["family"] == family or r["family"].startswith(family + "/"))
            and (tf is None or r["tf"] == tf) and (label is None or r["label"] == label) and (split is None or r["split"] == split)]


def load_vectors(cid, split="IS"):
    z = np.load(os.path.join(LEDGER, "vectors", f"{cid}_{split}.npz"))
    return {k: z[k] for k in z.files}


def ledger_sha():
    p = os.path.join(LEDGER, "trials.jsonl")
    return file_sha(p) if os.path.exists(p) else None


# ---------------------------------------------------------------- multiplicity: CSCV / PBO, deflated Sharpe, effective trials
def _partitions(S=CSCV_S):
    """All C(S, S/2) IS / pseudo-OOS block assignments as a boolean matrix (partitions x S), True = in-sample half."""
    combs = list(itertools.combinations(range(S), S // 2))
    M = np.zeros((len(combs), S), dtype=bool)
    for i, cmb in enumerate(combs): M[i, list(cmb)] = True
    return M


def pbo(vectors, statistic="kept_mean", S=CSCV_S):
    """CSCV probability of backtest overfitting (Bailey, Borwein, Lopez de Prado & Zhu 2017) over a family of candidates.
    vectors: list of session_vectors dicts (one per candidate, same sessions). Each candidate's per-session series is split into
    S contiguous blocks; for every C(S, S/2) partition the IS-best candidate's OOS rank is recorded; PBO = share of partitions
    where that rank is below the median (logit < 0). statistic: 'kept_mean' = kept net per kept trade over the half, or 'diff'
    = kept mean minus skipped mean over the half. Also the IS-vs-OOS performance degradation slope and the share of partitions
    where the IS-best is below zero OOS."""
    M = len(vectors)
    if M < 2: return dict(candidates=M, pbo=None, note="needs at least 2 candidates")
    T_ = len(vectors[0]["sessions"]); edges = np.linspace(0, T_, S + 1).round().astype(int)
    def blocks(v, key):
        return np.array([v[key][edges[b]:edges[b + 1]].sum() for b in range(S)])
    KS = np.array([blocks(v, "kept_sum") for v in vectors]); KN = np.array([blocks(v, "kept_n") for v in vectors])
    SS = np.array([blocks(v, "skipped_sum") for v in vectors]); SN = np.array([blocks(v, "skipped_n") for v in vectors])
    P = _partitions(S).astype(float)                                           # partitions x S
    def perf(Pm):
        ks, kn = Pm @ KS.T, Pm @ KN.T                                           # partitions x M
        with np.errstate(all="ignore"):
            km = np.where(kn > 0, ks / kn, np.nan)
            if statistic == "kept_mean": return km
            ss, sn = Pm @ SS.T, Pm @ SN.T
            return km - np.where(sn > 0, ss / sn, np.nan)
    ins, oos = perf(P), perf(1 - P)
    ins = np.where(np.isnan(ins), -np.inf, ins)
    best = np.argmax(ins, axis=1)
    oos_best = oos[np.arange(len(P)), best]
    ranks = np.array([(np.nan_to_num(oos[i], nan=-np.inf) < oos_best[i]).sum() / (M - 1) if M > 1 else 0.5 for i in range(len(P))])
    ranks = np.clip(ranks, 1e-6, 1 - 1e-6)
    logit = np.log(ranks / (1 - ranks))
    ins_best = ins[np.arange(len(P)), best]
    ok = np.isfinite(oos_best) & np.isfinite(ins_best)
    slope = float(np.polyfit(ins_best[ok], oos_best[ok], 1)[0]) if ok.sum() > 2 else None
    return dict(candidates=M, partitions=int(len(P)), statistic=statistic, pbo=round(float((logit < 0).mean()), 4),
                oos_best_below_zero=round(float((oos_best[ok] < 0).mean()), 4) if ok.any() else None,
                degradation_slope=round(slope, 4) if slope is not None else None,
                is_best_mean=round(float(ins_best[ok].mean()), 2) if ok.any() else None,
                oos_best_mean=round(float(oos_best[ok].mean()), 2) if ok.any() else None)


def effective_trials(vectors, key="kept_sum"):
    """Participation-ratio count of independent trials from the correlation matrix of the candidates' per-session series."""
    X = np.array([v[key] for v in vectors], dtype=float)
    X = X[:, X.std(axis=0) > 0] if X.shape[0] > 1 else X
    if X.shape[0] < 2: return float(X.shape[0])
    C = np.corrcoef(X); C = np.nan_to_num(C, nan=0.0); np.fill_diagonal(C, 1.0)
    lam = np.clip(np.linalg.eigvalsh(C), 0, None)
    return round(float(lam.sum() ** 2 / (lam ** 2).sum()), 2)


def deflated_sharpe(per_session, n_trials, sr_var_trials=None):
    """Bailey & Lopez de Prado (2014): the probability that the per-session Sharpe of a book is above the expected maximum
    Sharpe of n_trials trials with variance sr_var_trials (the variance of Sharpe across the family; estimated from
    per_session's own scale when None), with the skew / kurtosis correction. Returns SR, SR0, DSR, p = 1 - DSR."""
    x = np.asarray(per_session, dtype=float); T_ = len(x)
    if T_ < 3 or x.std(ddof=1) == 0: return dict(sr=None, sr0=None, dsr=None, p=None, T=T_)
    sr = float(x.mean() / x.std(ddof=1)); g3 = float(sst.skew(x)); g4 = float(sst.kurtosis(x, fisher=False))
    V = sr_var_trials if sr_var_trials is not None else 1.0 / T_
    N = max(2, n_trials); em = 0.5772156649
    sr0 = math.sqrt(V) * ((1 - em) * sst.norm.ppf(1 - 1 / N) + em * sst.norm.ppf(1 - 1 / (N * math.e)))
    den = 1 - g3 * sr + (g4 - 1) / 4 * sr * sr
    if den <= 0: return dict(sr=round(sr, 4), sr0=round(sr0, 4), dsr=None, p=None, T=T_, note="denominator <= 0")
    z = (sr - sr0) * math.sqrt(T_ - 1) / math.sqrt(den)
    dsr = float(sst.norm.cdf(z))
    return dict(sr=round(sr, 4), sr0=round(float(sr0), 4), dsr=round(dsr, 4), p=round(1 - dsr, 4), T=T_, n_trials=n_trials, skew=round(g3, 3), kurt=round(g4, 3))


def min_backtest_length(sr, n_trials, sr_var_trials):
    """Sessions needed for the observed per-session Sharpe to clear the expected maximum of n_trials (AFML 14.7)."""
    N = max(2, n_trials); em = 0.5772156649
    sr0 = math.sqrt(sr_var_trials) * ((1 - em) * sst.norm.ppf(1 - 1 / N) + em * sst.norm.ppf(1 - 1 / (N * math.e)))
    return round(float((sr0 / sr) ** 2 + 1), 1) if sr > 0 else None


# ---------------------------------------------------------------- resampling: stationary block bootstrap of sessions, SPA
def stationary_bootstrap_idx(T_, draws=BOOT_DRAWS, mean_block=BOOT_MEAN_BLOCK, seed=SEED, tag=""):
    """Politis & Romano stationary bootstrap indices (draws x T_) over T_ ordered sessions; seeded and reproducible."""
    rng = np.random.default_rng(int(_sha(f"{seed}|boot|{tag}"), 16) % (2 ** 32))
    p = 1.0 / mean_block
    starts = rng.integers(0, T_, size=(draws, T_)); cont = rng.random((draws, T_)) >= p
    idx = np.empty((draws, T_), dtype=int)
    idx[:, 0] = starts[:, 0]
    for t_ in range(1, T_):
        idx[:, t_] = np.where(cont[:, t_], (idx[:, t_ - 1] + 1) % T_, starts[:, t_])
    return idx


def bootstrap_ci(vec, draws=BOOT_DRAWS, ci=GO["boot_ci"], tag=""):
    """Block-bootstrap CI (sessions resampled) of the kept-vs-skipped difference and of the kept mean from a session_vectors dict."""
    T_ = len(vec["sessions"]); idx = stationary_bootstrap_idx(T_, draws, tag=tag)
    ks, kn, ss, sn = (vec[k][idx].sum(axis=1) for k in ("kept_sum", "kept_n", "skipped_sum", "skipped_n"))
    with np.errstate(all="ignore"):
        km = np.where(kn > 0, ks / kn, np.nan); sm = np.where(sn > 0, ss / sn, np.nan); d = km - sm
    a = (1 - ci) / 2
    q = lambda v: [round(float(np.nanquantile(v, a)), 2), round(float(np.nanquantile(v, 1 - a)), 2)]
    return dict(draws=draws, ci=ci, diff_ci=q(d), kept_mean_ci=q(km), diff_p_le0=round(float(np.nanmean(d <= 0)), 4),
                diff_point=round(float(np.nansum(vec["kept_sum"]) / max(1, vec["kept_n"].sum()) - np.nansum(vec["skipped_sum"]) / max(1, vec["skipped_n"].sum())), 2))


def selection_gain(vec):
    """Per-session selection gain d_t = kept mean in session t minus the session's mean over all units (0 when nothing kept):
    the per-session statistic behind the session-matched random control (its expectation under random selection is 0)."""
    with np.errstate(all="ignore"):
        km = np.where(vec["kept_n"] > 0, vec["kept_sum"] / vec["kept_n"], np.nan)
        am = vec["all_sum"] / vec["all_n"]
    d = km - am
    return np.where(np.isnan(d), 0.0, d), vec["kept_n"] > 0


def spa(vectors, draws=BOOT_DRAWS, tag=""):
    """White's Reality Check and Hansen's SPA over a family of candidates: H0 = no candidate has positive expected selection
    gain (per-session kept mean minus the session mean). Stationary bootstrap of sessions, studentised statistics, Hansen's
    consistent recentring. Returns the best candidate's statistic and the RC / SPA p-values."""
    Dm = np.array([selection_gain(v)[0] for v in vectors], dtype=float)       # M x T
    M, T_ = Dm.shape
    mu = Dm.mean(axis=1); se = Dm.std(axis=1, ddof=1) / math.sqrt(T_); se = np.where(se > 0, se, np.inf)
    tstat = np.sqrt(T_) * mu / (Dm.std(axis=1, ddof=1) + 1e-12)
    idx = stationary_bootstrap_idx(T_, draws, tag=tag)
    best = int(np.argmax(tstat)); rc_stat = float(tstat[best])
    # bootstrap of the max studentised statistic under the recentred null
    mub = np.stack([Dm[:, idx[d]].mean(axis=1) for d in range(draws)])           # draws x M
    sdb = np.stack([Dm[:, idx[d]].std(axis=1, ddof=1) for d in range(draws)]) + 1e-12
    rc_max = np.max(np.sqrt(T_) * (mub - mu) / sdb, axis=1)                       # White: recentre at the sample mean
    thr = np.sqrt(np.var(Dm, axis=1, ddof=1) / T_ * 2 * math.log(math.log(T_)))
    mu_c = np.where(mu < -thr, mu, 0.0)                                            # Hansen's consistent recentring
    spa_max = np.max(np.sqrt(T_) * (mub - mu + mu_c) / sdb, axis=1)
    return dict(candidates=M, sessions=T_, best=best, best_mean_gain=round(float(mu[best]), 2), best_t=round(rc_stat, 3),
                rc_p=round(float((rc_max >= rc_stat).mean()), 4), spa_p=round(float((spa_max >= rc_stat).mean()), 4), draws=draws)


# ---------------------------------------------------------------- structural breaks of the book's own expectancy
def _hac_var(x, lag=5):
    x = np.asarray(x, dtype=float) - np.mean(x); T_ = len(x)
    s = float((x * x).sum())
    for k in range(1, lag + 1):
        w = 1 - k / (lag + 1); s += 2 * w * float((x[k:] * x[:-k]).sum())
    return s / T_ / T_                                                             # variance of the mean


def chow_mean(x, y, lag=5):
    """HAC (Newey-West, Bartlett, lag 5) t-test of a difference of means between two consecutive segments."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 5 or len(y) < 5: return dict(t=None, p=None, n=[len(x), len(y)])
    t_ = (y.mean() - x.mean()) / math.sqrt(_hac_var(x, lag) + _hac_var(y, lag))
    return dict(t=round(float(t_), 3), p=round(float(2 * (1 - sst.norm.cdf(abs(t_)))), 4), mean_before=round(float(x.mean()), 2),
                mean_after=round(float(y.mean()), 2), n=[len(x), len(y)])


def bde_cusum(x, k=10):
    """Brown-Durbin-Evans CUSUM of recursive residuals of the constant-mean model on the ordered series x: the maximum
    crossing of the 5% bands +-0.948 sqrt(T-k) (1 + 2 (r-k)/(T-k)); reports whether the path leaves the band and where."""
    x = np.asarray(x, dtype=float); T_ = len(x)
    if T_ <= k + 2: return dict(break_detected=None)
    w = np.array([(x[t_] - x[:t_].mean()) / math.sqrt(1 + 1 / t_) for t_ in range(k, T_)])
    sig = w.std(ddof=1)
    W = np.cumsum(w) / sig
    r = np.arange(k + 1, T_ + 1)
    band = 0.948 * math.sqrt(T_ - k) * (1 + 2 * (r - k) / (T_ - k))
    ex = np.abs(W) > band
    return dict(break_detected=bool(ex.any()), first_crossing_index=int(np.argmax(ex)) + k if ex.any() else None,
                max_ratio=round(float(np.max(np.abs(W) / band)), 3), T=T_)


def break_tests(T, lag=5):
    """The pre-registration step: has the book's per-session expectancy (active sessions, label L1) changed inside IS or at the
    IS / OOS boundary? Rolling 60-session mean with block-bootstrap bands, BDE CUSUM, HAC Chow tests per calendar year, and the
    one permitted OOS aggregate read: the Chow test at 2026-01-01 (it decides the OOS caveat, never a key)."""
    rows = np.arange(T.n)
    ses = T.session[rows]; net = T.net[rows]
    S = np.array(sorted(set(ses.tolist()))); idx = np.searchsorted(S, ses)
    per = np.bincount(idx, weights=net, minlength=len(S)) / np.bincount(idx, minlength=len(S))
    day = dict(zip(T.session, T.day)); days = np.array([day[int(s)] for s in S])
    is_ = days <= IS_END
    x_is = per[is_]
    years = sorted({d[:4] for d in days[is_]})
    chow_years = {}
    for y in years[1:]:
        before = x_is[np.array([d[:4] < y for d in days[is_]])]; after = x_is[np.array([d[:4] == y for d in days[is_]])]
        chow_years[y] = chow_mean(before, after, lag)
    boundary = chow_mean(x_is, per[~is_], lag)
    roll = pd.Series(x_is).rolling(60).mean().to_numpy()
    idxb = stationary_bootstrap_idx(len(x_is), 500, tag="roll")
    rb = np.array([pd.Series(x_is[idxb[d]]).rolling(60).mean().to_numpy() for d in range(500)])
    lo, hi = np.nanquantile(rb, 0.05, axis=0), np.nanquantile(rb, 0.95, axis=0)
    outside = int(np.nansum((roll < lo) | (roll > hi)))
    return dict(label=T.label, active_is_sessions=int(is_.sum()), is_mean_per_session=round(float(x_is.mean()), 2),
                bde=bde_cusum(x_is), chow_per_year=chow_years, chow_is_oos_boundary=boundary,
                rolling60_outside_band=outside, rolling60_points=int(np.isfinite(roll).sum()),
                winners_only_boundary=chow_mean(x_is[x_is > 0], per[~is_][per[~is_] > 0], lag) if (per[~is_] > 0).sum() >= 5 else None,
                caveat=("IS/OOS boundary Chow p < 0.05: the OOS window is not from the same process; every OOS table carries this"
                        if boundary["p"] is not None and boundary["p"] < 0.05 else "no boundary break at 5%"))


# ---------------------------------------------------------------- go / no-go
def go_no_go(res, tf, cpcv=None, pbo_value=None, dsr=None, spa_p=None, boot=None):
    """The pre-registered pass rule on a candidate's IS results. Returns (passed, {check: (ok, value)})."""
    ch = {}
    ch["kept_share>=20%"] = (res.get("kept_share") is not None and res["kept_share"] >= GO["kept_share_min"], res.get("kept_share"))
    ch[f"kept_n>={GO['kept_n_min'][tf]}"] = (res.get("kept_n", 0) >= GO["kept_n_min"][tf], res.get("kept_n"))
    ch["diff>0"] = (res.get("diff") is not None and res["diff"] > 0, res.get("diff"))
    ch["diff_top1_removed>0"] = (res.get("diff_top1_removed") is not None and res["diff_top1_removed"] > GO["top1_removed_diff_min"], res.get("diff_top1_removed"))
    ch["kept_mean_slip8>0"] = (res.get("kept_mean_slip8") is not None and res["kept_mean_slip8"] > GO["slip8_kept_mean_min"], res.get("kept_mean_slip8"))
    ch[f"sign_blocks>={GO['sign_blocks_min']}/12"] = (res.get("sign_blocks") is not None and res["sign_blocks"] >= GO["sign_blocks_min"], res.get("sign_blocks"))
    ch["control_pct>=95"] = (res.get("control_pct") is not None and res["control_pct"] >= GO["control_pct_min"], res.get("control_pct"))
    if cpcv is not None: ch["cpcv_p5_diff>0"] = (cpcv.get("diff_p5") is not None and cpcv["diff_p5"] > GO["cpcv_p5_diff_min"], cpcv.get("diff_p5"))
    if pbo_value is not None: ch["pbo<=0.2"] = (pbo_value <= GO["pbo_max"], pbo_value)
    if dsr is not None: ch["dsr_p<0.1"] = (dsr.get("p") is not None and dsr["p"] < GO["dsr_p_max"], dsr.get("p"))
    if spa_p is not None: ch["spa_p<=0.10"] = (spa_p <= GO["spa_p_max"], spa_p)
    if boot is not None: ch["boot_ci_excludes_0"] = (boot["diff_ci"][0] > 0, boot["diff_ci"])
    return all(v[0] for v in ch.values()), ch


# ---------------------------------------------------------------- self-test
if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser(); ap.add_argument("--tf", default="5minute"); ap.add_argument("--selftest", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    T = load(a.tf)
    print(f"{a.tf} L1 units: {T.n} (IS {T.is_mask.sum()}, OOS {T.oos_mask.sum()}), as-of columns {len(T.asof_columns())}, active IS sessions {len(T.active_sessions)}")
    print("splits:", json.dumps(check_splits(T)))
    X, src = design(T); print(f"design matrix {X.shape}, NaN share {X.isna().mean().mean():.3f}")
    frozen = T.F.fz_traded.astype(bool).to_numpy()
    r1 = score(T, frozen, "selftest/frozen_gate", dict(gate="ST7/ST8 as traded"), script=__file__)
    print("frozen gate:", {k: r1[k] for k in ("kept_n", "kept_share", "kept_mean", "skipped_mean", "diff", "perm_p", "control_pct", "loser_recall", "winner_recall_weighted", "sign_blocks", "kept_mean_slip8")})
    rng = np.random.default_rng(1)
    vecs = [session_vectors(T, frozen, np.flatnonzero(T.is_mask))]
    for j in range(5):
        kp = rng.random(T.n) < 0.5
        score(T, kp, "selftest/random", dict(seed=j), script=__file__, controls=False)
        vecs.append(session_vectors(T, kp, np.flatnonzero(T.is_mask)))
    print("pbo (kept_mean):", pbo(vecs, "kept_mean")); print("pbo (diff):", pbo(vecs, "diff"))
    print("effective trials:", effective_trials(vecs))
    gain, _ = selection_gain(vecs[0])
    print("dsr (frozen, per-session kept net, 6 trials):", deflated_sharpe(np.where(vecs[0]["kept_n"] > 0, vecs[0]["kept_sum"] / np.maximum(vecs[0]["kept_n"], 1), 0.0)[vecs[0]["kept_n"] > 0], 6, 0.01))
    print("bootstrap:", bootstrap_ci(vecs[0], draws=500))
    print("spa:", spa(vecs, draws=500))
    print("break tests:", json.dumps(break_tests(T), default=str)[:1500])
    print("go/no-go frozen:", go_no_go(r1, a.tf))
    print(f"self-test done in {time.time() - t0:.1f}s; ledger sha {ledger_sha()}")
