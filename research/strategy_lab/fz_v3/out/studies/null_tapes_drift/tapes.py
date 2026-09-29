"""Evaluate gates on a synthetic null tape's own feature table (study null_tapes_drift; DESIGN_PANEL decision-making-3 (c)).

A tape folder is what build.py --path <tape.csv> --out <folder> wrote: features.parquet, trades.parquet, sessions.parquet,
bars.parquet, events.parquet, setups.parquet, meta.json. Nothing here touches OUT/ledger: tape results stay in the study
folder (the ledger is for the real tape only).

    import tapes
    T = tapes.load_tape(folder)                       # a harness.Table over the tape's L1 units (all rows are IS by construction)
    res = tapes.evaluate_rule_list(folder, rules)     # rules: a rule-list JSON (grammar below) -> kept-vs-skipped diff, control pct, ...
    res = tapes.evaluate_keep(T, keep_mask, tag)      # any boolean keep mask through harness.metrics (2,000-draw controls)

Rule-list grammar (the one the LLM-hypothesis study uses, rules_round0.json): a list of rules, each
    {"if": [[column, op, value], ...] (at most 3 comparisons, conjunction), "then": "skip"}
over as-of columns of features.parquet; ops >=, >, <=, <, ==, !=, in, not_in. A SETUP is skipped when ANY rule fires
(disjunction of conjunctions); NaN never satisfies a comparison. A dict {"rules": [...]} or {"minute": [...], "5minute": [...]}
is accepted too (the timeframe list is picked by the tape's tf). A rule may carry "then": "keep" — then the listed rules are
the KEEP set (a SETUP is kept when any keep rule fires); mixing keep and skip rules in one list is refused.

How a candidate is evaluated on the tapes later: for every tape folder under tapes/<tf>/, evaluate_rule_list(folder, rules)
gives the tape's diff and control percentile; the candidate's real-tape diff (its ledger row) is compared with the p95 of the
tape diffs per generator (null_distributions.json holds the frozen gate's and the mechanical gates' nulls as the reference;
a candidate passes the null-tape check when its real-tape diff is above the GMM-Markov p95 AND above the segment p95, and
its session-bootstrap diffs are of the same sign as the real one in at least 15 of 20 tapes; see FINDINGS.md).
"""
import os, sys, json, glob
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402

MECHANICAL_GATES = {
    "frozen_st7_st8": "keep = fz_traded (the frozen ST7/ST8 gate as traded on the tape)",
    "choch2_skip": "skip when n_choch_since_bos >= 2 (pre-registered mechanical gate 1)",
    "sl_above_median_skip": "skip when sl_dist_atr > the tape's own IS median of sl_dist_atr (pre-registered mechanical gate 2)",
}


def load_tape(folder, label="L1"):
    """harness.load for a tape folder: the L1 units (traded, l1_taken) as a harness.Table."""
    F = pd.read_parquet(os.path.join(folder, "features.parquet"))
    TR = pd.read_parquet(os.path.join(folder, "trades.parquet")).set_index("entry_i")
    S = pd.read_parquet(os.path.join(folder, "sessions.parquet"))
    tf = json.load(open(os.path.join(folder, "meta.json")))["timeframe"]
    F = F[F.traded.astype(bool)]
    if label == "L1": F = F[F.l1_taken.astype(bool)]
    F = F.sort_values("setup_i").reset_index(drop=True)
    TR = TR.loc[F.setup_i.to_numpy()].reset_index()
    return H.Table(tf, label, F, TR, S)


def evaluate_keep(T, keep, tag, controls=True, draws=H.CONTROL_DRAWS):
    """Kept-vs-skipped metrics of a keep mask over the tape's IS rows (every tape row is IS), through harness.metrics."""
    rows = np.flatnonzero(T.is_mask)
    m = H.metrics(T, np.asarray(keep, dtype=bool), rows, tag, controls=controls, draws=draws)
    return m


def mechanical_masks(T):
    """The three reference gates' keep masks on a Table (real or tape): frozen, choch2, sl above the table's own IS median."""
    F = T.F
    frozen = F.fz_traded.astype(bool).to_numpy()
    ncsb = F.n_choch_since_bos.to_numpy(dtype=float)
    choch2 = ~(ncsb >= 2)
    sl = F.sl_dist_atr.to_numpy(dtype=float)
    med = float(np.nanmedian(sl[T.is_mask]))
    slmed = ~(sl > med)
    return dict(frozen_st7_st8=frozen, choch2_skip=choch2, sl_above_median_skip=slmed), dict(sl_dist_atr_is_median=med)


# ---------------------------------------------------------------- rule lists
_OPS = {">=": np.greater_equal, ">": np.greater, "<=": np.less_equal, "<": np.less, "==": np.equal, "!=": np.not_equal}


def _cmp(series, op, value):
    if op in ("in", "not_in"):
        vals = [str(v) for v in (value if isinstance(value, (list, tuple, set)) else [value])]
        s = series.astype(object).map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else str(z))
        hit = s.isin(vals).to_numpy() & s.notna().to_numpy()
        return hit if op == "in" else (~hit & s.notna().to_numpy())
    if op not in _OPS: raise ValueError(f"unknown op {op}")
    if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
        x = series.to_numpy(dtype=float)
        v = float(value) if not isinstance(value, bool) else float(value)
        with np.errstate(invalid="ignore"): hit = _OPS[op](x, v)
        return hit & np.isfinite(x)
    so = series.astype(object)
    if op in ("==", "!="):
        s = so.map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else str(z))
        hit = (s == str(value)).to_numpy() & s.notna().to_numpy()
        return hit if op == "==" else (~hit & s.notna().to_numpy())
    x = pd.to_numeric(so, errors="coerce").to_numpy(dtype=float)
    with np.errstate(invalid="ignore"): hit = _OPS[op](x, float(value))
    return hit & np.isfinite(x)


def rules_for(rules, tf):
    if isinstance(rules, dict):
        if "rules" in rules: rules = rules["rules"]
        elif tf in rules: rules = rules[tf]
        else: raise ValueError("rule JSON needs 'rules' or a per-timeframe list")
    return list(rules)


def rule_mask(F, rules, tf):
    """(fires, mode): fires[i] = any rule's conjunction holds on row i; mode = 'skip' or 'keep'."""
    rules = rules_for(rules, tf)
    modes = {str(r.get("then", "skip")).lower() for r in rules}
    if len(modes) > 1: raise ValueError(f"a rule list mixes {sorted(modes)}; use one mode")
    mode = modes.pop() if modes else "skip"
    fires = np.zeros(len(F), dtype=bool)
    for r in rules:
        conds = r["if"]
        if len(conds) > 3: raise ValueError(f"rule {r.get('id')} has depth {len(conds)} > 3")
        m = np.ones(len(F), dtype=bool)
        for col, op, val in conds:
            if col not in F.columns: raise KeyError(f"rule {r.get('id')}: column {col} not in the feature table")
            if col.startswith(H.LABEL_PREFIX) or col in H.NOT_FEATURES: raise PermissionError(f"rule {r.get('id')}: {col} is not an as-of feature")
            m &= _cmp(F[col], op, val)
        fires |= m
    return fires, mode


def evaluate_rule_list(tape_folder, rules, controls=True, draws=H.CONTROL_DRAWS, label="L1"):
    """Apply a rule-list JSON (or a path to one) to a tape's feature table; returns the kept-vs-skipped difference, the
    session-matched control percentile and the other harness metrics, plus the rule count and the tape's identity."""
    if isinstance(rules, str): rules = json.load(open(rules, encoding="utf-8"))
    T = load_tape(tape_folder, label)
    fires, mode = rule_mask(T.F, rules, T.tf)
    keep = ~fires if mode == "skip" else fires
    tag = f"tape|{os.path.basename(os.path.normpath(tape_folder))}|{H._sha(json.dumps(rules, sort_keys=True, default=str))}"
    m = evaluate_keep(T, keep, tag, controls=controls, draws=draws)
    return dict(tape=os.path.relpath(tape_folder, HERE), tf=T.tf, label=label, n_rules=len(rules_for(rules, T.tf)), mode=mode,
                fired=int(fires[T.is_mask].sum()), **m)


def tape_folders(tf, gen=None):
    pat = os.path.join(HERE, "tapes", tf, f"{gen or '*'}_*")
    return sorted(p for p in glob.glob(pat) if os.path.exists(os.path.join(p, "features.parquet")))


# ---------------------------------------------------------------- reality check of a tape (or of the real IS tape)
def bar_stats(bars, sessions=None, is_only=True):
    """Per-bar within-session log-return std (bps), excess kurtosis, autocorrelation of |r| at lags 1-5 (pairs inside a session),
    the price level range and the median ATR14."""
    B = bars
    if is_only and "split" in B.columns: B = B[B.split.astype(str) == "IS"]
    B = B.sort_values("i") if "i" in B.columns else B
    c = B.close.to_numpy(dtype=float); s = B.session_idx.to_numpy()
    same = s[1:] == s[:-1]
    r = np.log(c[1:] / c[:-1])[same]                                     # within-session close-to-close returns
    ss = s[1:][same]
    out = dict(bars=int(len(B)), ret_std_bps=round(float(r.std() * 1e4), 3), ret_kurt_excess=round(float(pd.Series(r).kurt()), 3),
               ret_mean_bps=round(float(r.mean() * 1e4), 4))
    a = np.abs(r) - np.abs(r).mean()
    for lag in range(1, 6):
        m = ss[lag:] == ss[:-lag]
        x, y = a[lag:][m], a[:-lag][m]
        out[f"absret_ac{lag}"] = round(float((x * y).mean() / (a.var() + 1e-18)), 4)
    out.update(close_min=float(c.min()), close_max=float(c.max()), close_first=float(c[0]), close_last=float(c[-1]),
               atr14_median=round(float(B.atr14.median()), 3) if "atr14" in B.columns else None,
               volume_mean=round(float(B.volume.mean()), 1), zero_volume_bars=int((B.volume == 0).sum()))
    return out


def structure_stats(folder, is_only=True):
    """Engine / FZ event rates per session: CHoCH, BOS, SETUPs, L1 units, the raw L1 book and the frozen gate's kept share."""
    S = pd.read_parquet(os.path.join(folder, "sessions.parquet")); E = pd.read_parquet(os.path.join(folder, "events.parquet"))
    P = pd.read_parquet(os.path.join(folder, "setups.parquet")); F = pd.read_parquet(os.path.join(folder, "features.parquet"),
                                                                                    columns=["setup_i", "split", "traded", "l1_taken", "l1_net_inr", "l1_win", "fz_traded", "session_idx", "l1_exit_reason"])
    if is_only:
        is_sess = set(S[S.split.astype(str) == "IS"].session_idx.tolist()); n_s = len(is_sess)
        B = pd.read_parquet(os.path.join(folder, "bars.parquet"), columns=["i", "session_idx", "split"])
        is_bars = set(B[B.split.astype(str) == "IS"].i.tolist())
        E = E[E.i.isin(is_bars)]; P = P[P.setup_i.isin(is_bars)]; F = F[F.split.astype(str) == "IS"]
    else: n_s = len(S)
    U = F[F.traded.astype(bool) & F.l1_taken.astype(bool)]
    return dict(sessions=int(n_s), choch_per_session=round(len(E[E.kind == "CHoCH"]) / n_s, 4), bos_per_session=round(len(E[E.kind == "BOS"]) / n_s, 4),
                setups_per_session=round(len(P) / n_s, 4), l1_units=int(len(U)), l1_units_per_session=round(len(U) / n_s, 4),
                l1_mean_net=round(float(U.l1_net_inr.mean()), 2) if len(U) else None, l1_win_rate=round(float(U.l1_win.astype(float).mean()), 4) if len(U) else None,
                frozen_kept_share=round(float(U.fz_traded.astype(float).mean()), 4) if len(U) else None,
                l1_exit_reasons={k: int(v) for k, v in U.l1_exit_reason.value_counts().items()})


def reality_check(folder):
    B = pd.read_parquet(os.path.join(folder, "bars.parquet"), columns=["i", "session_idx", "close", "volume", "atr14", "split"])
    return dict(**bar_stats(B), **structure_stats(folder))
