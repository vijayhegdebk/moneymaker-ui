"""Evaluate gates on a synthetic null tape's own feature table (study null_tapes_drift; DESIGN_PANEL decision-making-3 (c)).

A tape folder is what build.py --path <tape.csv> --out <folder> wrote: features.parquet, trades.parquet, sessions.parquet,
bars.parquet, events.parquet, setups.parquet, meta.json. Nothing here touches OUT/ledger: tape results stay in the study
folder (the ledger is for the real tape only).

    import tapes
    T = tapes.load_tape(folder)                       # a harness.Table over the tape's L1 units (all rows are IS by construction)
    res = tapes.evaluate_rule_list(folder, rules)     # rules: a rule-list JSON (grammar below) -> kept-vs-skipped diff, control pct, ...
    res = tapes.evaluate_keep(T, keep_mask, tag)      # any boolean keep mask through harness.metrics (2,000-draw controls)
    h = tapes.tape_health(folder)                     # the engine-health check of one tape (lock-out share, SETUP rate vs real, healthy flag)
    tapes.tape_folders(tf, gen)                       # the CERTIFICATE tape set: the first DESIGN_N healthy tapes per generator (healthy=False: every tape built)
    tapes.null_tape_check(real_diff, tf, rules)       # the pass rule of FINDINGS section 7 as go_no_go-shaped items

Rule-list grammar (the one the LLM-hypothesis study uses, rules_round0.json): a list of rules, each
    {"if": [[column, op, value], ...] (at most 3 comparisons, conjunction), "then": "skip"}
over as-of columns of features.parquet; ops >=, >, <=, <, ==, !=, in, not_in. A SETUP is skipped when ANY rule fires
(disjunction of conjunctions); NaN never satisfies a comparison. A dict {"rules": [...]} or {"minute": [...], "5minute": [...]}
is accepted too (the timeframe list is picked by the tape's tf). A rule may carry "then": "keep" — then the listed rules are
the KEEP set (a SETUP is kept when any keep rule fires); mixing keep and skip rules in one list is refused.

Refused columns (PermissionError): label columns (harness.LABEL_PREFIX), harness.NOT_FEATURES (fz_traded, raw prices, ids), and
the calendar proxies drift.py found (|Spearman rho| >= 0.9 with session_idx: `n_events_asof`, `sl`; read from drift.json,
TIME_PROXIES_FALLBACK when the file is missing). A rule on a time proxy is a calendar rule, not a market rule (FINDINGS section 6).

Engine health of a tape (repair round): on a driftless random-walk tape the engine's protected level can freeze — the anchored
AVWAP of the last flip lags a long one-directional walk, no new swing qualifies as a protected-level candidate (engine.qualifies:
a low below / a high above that AVWAP), `prot` stays at the last candidate and a CHoCH (a close beyond `prot` against the trend)
becomes unreachable while BOS continues. Sessions inside a frozen-`prot`, CHoCH-free run longer than the real tape's longest such
run (68 / 69 sessions on 5minute / minute) are counted as dead; a tape is HEALTHY when its dead share is < HEALTH["dead_share_max"]
(0.2) AND its SETUP rate is >= HEALTH["setup_rate_ratio_min"] (1/3) x the real tape's. The health flag never reads a label or a
gate statistic. The certificate (null_distributions.json `gates`, FINDINGS section 4) is read on the first DESIGN_N healthy
tapes per generator (by seed index k); the sets with the locked tapes are published beside it (`gates_all_original`,
`gates_healthy_original`).

How a candidate is evaluated on the tapes later: for every tape folder of tape_folders(tf, gen) (the certificate set),
evaluate_rule_list(folder, rules) gives the tape's diff and control percentile; the candidate's real-tape diff (its ledger row)
is compared with the p95 of the tape diffs per generator: it passes the null-tape check when its real-tape diff is above the
GMM-Markov p95 AND above the segment p95, and its session-bootstrap diffs are of the same sign as the real one in at least 75%
of the certificate session tapes (null_tape_check does exactly this; see FINDINGS.md section 7).
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
    "choch2_skip": "skip when n_choch_since_bos >= 2 (mechanical reference gate 1: fixed in tapes.py before any tape was scored; a reference point, not a candidate; BRIEF H2 names the family without k)",
    "sl_above_median_skip": "skip when sl_dist_atr > the tape's own IS median of sl_dist_atr (mechanical reference gate 2: fixed in tapes.py before any tape was scored; a reference point, not a candidate)",
}
DESIGN_N = {"5minute": 20, "minute": 8}                                # tapes per generator the design fixes (DESIGN_PANEL (c), Judge 1 / 2)
HEALTH = dict(dead_share_max=0.2, setup_rate_ratio_min=1.0 / 3.0)    # per-tape poor-null rule (repair round)
TIME_PROXIES_FALLBACK = ("n_events_asof", "sl")                         # drift.py's calendar proxies, used when drift.json is absent
PASS_RULE = dict(session_same_sign_min=0.75)                           # FINDINGS section 7


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


# ---------------------------------------------------------------- time proxies (refused in rule lists)
def time_proxies(tf):
    """The calendar proxies drift.py found for the timeframe (|Spearman rho| >= 0.9 with session_idx), from drift.json or
    drift_<tf>.json; TIME_PROXIES_FALLBACK when neither file exists. A rule on one of these is refused by rule_mask."""
    cols = set(TIME_PROXIES_FALLBACK)
    for name in ("drift.json", f"drift_{tf}.json"):
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                tp = d.get("timeframes", {}).get(tf, {}).get("time_proxies")
                if tp: cols |= set(tp.keys() if isinstance(tp, dict) else tp)
            except (ValueError, OSError):
                pass
    return cols


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
    """(fires, mode): fires[i] = any rule's conjunction holds on row i; mode = 'skip' or 'keep'.
    Refuses (PermissionError) a label column, a harness.NOT_FEATURES column and a calendar proxy (time_proxies(tf))."""
    rules = rules_for(rules, tf)
    modes = {str(r.get("then", "skip")).lower() for r in rules}
    if len(modes) > 1: raise ValueError(f"a rule list mixes {sorted(modes)}; use one mode")
    mode = modes.pop() if modes else "skip"
    proxies = time_proxies(tf)
    fires = np.zeros(len(F), dtype=bool)
    for r in rules:
        conds = r["if"]
        if len(conds) > 3: raise ValueError(f"rule {r.get('id')} has depth {len(conds)} > 3")
        m = np.ones(len(F), dtype=bool)
        for col, op, val in conds:
            if col not in F.columns: raise KeyError(f"rule {r.get('id')}: column {col} not in the feature table")
            if col.startswith(H.LABEL_PREFIX) or col in H.NOT_FEATURES: raise PermissionError(f"rule {r.get('id')}: {col} is not an as-of feature")
            if col in proxies: raise PermissionError(f"rule {r.get('id')}: {col} is a time proxy (drift.json time_proxies, |rho| >= 0.9 with session_idx): a calendar rule, refused")
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


# ---------------------------------------------------------------- engine health of a tape (per-tape poor-null flag)
def _tape_k(folder):
    try: return int(os.path.basename(os.path.normpath(folder)).rsplit("_", 1)[1])
    except (IndexError, ValueError): return -1


def _tape_gen(folder):
    return os.path.basename(os.path.normpath(folder)).rsplit("_", 1)[0]


def _frozen_runs(folder):
    """Per IS session: prot frozen (no change inside the session and equal to the previous session's last prot) and no CHoCH.
    Returns (n_sessions, run lengths of consecutive frozen sessions, per-session frozen flags, position of the last CHoCH session,
    the longest CHoCH-free stretch in sessions, the session dates)."""
    B = pd.read_parquet(os.path.join(folder, "bars.parquet"), columns=["i", "session_idx", "close", "prot", "split"])
    if "split" in B.columns: B = B[B.split.astype(str) == "IS"]
    E = pd.read_parquet(os.path.join(folder, "events.parquet"), columns=["i", "kind"])
    S = pd.read_parquet(os.path.join(folder, "sessions.parquet"))
    S = S[S.split.astype(str) == "IS"].sort_values("session_idx")
    sess = S.session_idx.to_numpy(); n_s = len(sess); pos = {int(s): j for j, s in enumerate(sess)}
    pr = B.prot.fillna(-1.0)
    g = pd.DataFrame(dict(session_idx=B.session_idx.to_numpy(), prot=pr.to_numpy())).groupby("session_idx").prot.agg(["first", "last", "nunique"])
    g = g.reindex(sess)
    prev_last = g["last"].shift(1)
    moved = (g["nunique"] > 1) | (g["first"] != prev_last)
    moved.iloc[0] = True
    b2s = dict(zip(B.i.to_numpy(), B.session_idx.to_numpy()))
    ch_sess = {b2s[i] for i in E[E.kind == "CHoCH"].i.to_numpy() if i in b2s}
    has_ch = np.array([s in ch_sess for s in sess])
    frozen = ~(moved.to_numpy() | has_ch)
    runs = []; c = 0
    for v in frozen:
        if v: c += 1
        elif c: runs.append(c); c = 0
    if c: runs.append(c)
    ch_pos = sorted(pos[s] for s in ch_sess)
    last_ch = ch_pos[-1] if ch_pos else -1
    stretches = np.diff(np.array([-1] + ch_pos + [n_s])) - 1
    return dict(n_sessions=int(n_s), runs=np.array(runs, dtype=int) if runs else np.zeros(0, dtype=int), frozen=frozen, last_choch_pos=int(last_ch),
                longest_choch_free=int(stretches.max()) if len(stretches) else int(n_s), dates=S.date.astype(str).to_numpy(),
                prot_last=(None if np.isnan(B.prot.iloc[-1]) else float(B.prot.iloc[-1])), close_last=float(B.close.iloc[-1]), is_bar_ids=set(B.i.tolist()))


def real_health(tf):
    """The real tape's IS engine-health reference (cached in real_health_<tf>.json): longest frozen-prot run, longest CHoCH-free
    stretch, SETUPs per session. Reads bars / events / sessions / setups of OUT/data/<tf>, IS rows only, never a label."""
    p = os.path.join(HERE, f"real_health_{tf}.json")
    if os.path.exists(p): return json.load(open(p, encoding="utf-8"))
    folder = os.path.join(OUT, "data", tf)
    fr = _frozen_runs(folder)
    P = pd.read_parquet(os.path.join(folder, "setups.parquet"), columns=["setup_i"])
    setups = int(P.setup_i.isin(fr["is_bar_ids"]).sum())
    out = dict(tf=tf, sessions=fr["n_sessions"], longest_frozen_run_sessions=int(fr["runs"].max()) if len(fr["runs"]) else 0,
               frozen_sessions_total=int(fr["frozen"].sum()), longest_choch_free_sessions=fr["longest_choch_free"], setups=setups,
               setups_per_session=round(setups / fr["n_sessions"], 4), dead_tail_share=round((fr["n_sessions"] - 1 - fr["last_choch_pos"]) / fr["n_sessions"], 4),
               definition="a session is frozen when prot does not change inside it, equals the previous session's last prot and no CHoCH occurs; IS sessions only")
    json.dump(out, open(p, "w"), indent=1)
    return out


def tape_health(folder, real=None, write=True):
    """The engine-health check of one tape (its poor-null flag). Dead sessions = sessions inside frozen-prot, CHoCH-free runs
    longer than the real tape's longest such run; healthy = dead share < HEALTH['dead_share_max'] and SETUP rate >=
    HEALTH['setup_rate_ratio_min'] x real. Writes tape_health.json into the folder (write=True). Reads no label."""
    tf = json.load(open(os.path.join(folder, "meta.json")))["timeframe"]
    real = real or real_health(tf)
    fr = _frozen_runs(folder)
    P = pd.read_parquet(os.path.join(folder, "setups.parquet"), columns=["setup_i", "time"])
    P = P[P.setup_i.isin(fr["is_bar_ids"])]
    n_s = fr["n_sessions"]; L = real["longest_frozen_run_sessions"]
    dead_runs = fr["runs"][fr["runs"] > L]
    dead = int(dead_runs.sum()); dead_share = dead / n_s
    setups_ps = len(P) / n_s; ratio = setups_ps / real["setups_per_session"] if real["setups_per_session"] else None
    reasons = []
    if dead_share >= HEALTH["dead_share_max"]: reasons.append(f"dead share {dead_share:.3f} >= {HEALTH['dead_share_max']}")
    if ratio is not None and ratio < HEALTH["setup_rate_ratio_min"]: reasons.append(f"setup rate {ratio:.3f} x real < {HEALTH['setup_rate_ratio_min']:.3f}")
    # the longest frozen run's calendar position (first session of the first run of maximal length)
    start = None
    if len(fr["runs"]):
        longest = int(fr["runs"].max()); fz = fr["frozen"]; i = 0
        while i < n_s and start is None:
            if fz[i]:
                s0 = i
                while i < n_s and fz[i]: i += 1
                if i - s0 == longest: start = s0
            else: i += 1
    out = dict(tape=os.path.relpath(folder, HERE), tf=tf, gen=_tape_gen(folder), k=_tape_k(folder), sessions=n_s,
               longest_frozen_run_sessions=int(fr["runs"].max()) if len(fr["runs"]) else 0,
               longest_frozen_run_start=(fr["dates"][start] if start is not None else None),
               dead_sessions=dead, dead_share=round(dead_share, 4), dead_runs=[int(x) for x in dead_runs],
               dead_tail_share=round((n_s - 1 - fr["last_choch_pos"]) / n_s, 4), longest_choch_free_sessions=fr["longest_choch_free"],
               last_choch_date=(fr["dates"][fr["last_choch_pos"]] if fr["last_choch_pos"] >= 0 else None),
               last_setup_time=(str(P.time.max()) if len(P) else None), setups=int(len(P)), setups_per_session=round(setups_ps, 4),
               setup_rate_ratio_to_real=(round(ratio, 4) if ratio is not None else None), prot_last=fr["prot_last"], close_last=fr["close_last"],
               prot_gap_pts=(round(fr["close_last"] - fr["prot_last"], 2) if fr["prot_last"] is not None else None),
               real_longest_frozen_run_sessions=L, real_setups_per_session=real["setups_per_session"],
               healthy=(len(reasons) == 0), reasons=reasons, rule=dict(HEALTH, dead_run_longer_than=L))
    if write:
        json.dump(out, open(os.path.join(folder, "tape_health.json"), "w"), indent=1)
    return out


def read_health(folder, compute=True):
    p = os.path.join(folder, "tape_health.json")
    if os.path.exists(p): return json.load(open(p, encoding="utf-8"))
    return tape_health(folder) if compute else None


def all_tape_folders(tf, gen=None):
    """Every built tape folder of the timeframe (and generator), sorted by generator then seed index k (numeric)."""
    pat = os.path.join(HERE, "tapes", tf, f"{gen or '*'}_*")
    fs = [p for p in glob.glob(pat) if os.path.exists(os.path.join(p, "features.parquet"))]
    return sorted(fs, key=lambda p: (_tape_gen(p), _tape_k(p)))


def tape_folders(tf, gen=None, healthy=True, n=None, original_only=False):
    """The tape set a candidate is evaluated on.
    healthy=True (default, the CERTIFICATE set): per generator the first n (= DESIGN_N[tf]) tapes by seed index k whose
    tape_health.json says healthy (computed when missing). healthy=False: every tape built (n=None) or the first n per generator.
    original_only=True restricts to k < DESIGN_N[tf] (the tapes of the first build, locked ones included when healthy=False)."""
    n = DESIGN_N[tf] if n is None and healthy else n
    out = []
    for g in sorted({_tape_gen(p) for p in all_tape_folders(tf, gen)}):
        fs = all_tape_folders(tf, g)
        if original_only: fs = [p for p in fs if _tape_k(p) < DESIGN_N[tf]]
        if healthy: fs = [p for p in fs if read_health(p)["healthy"]]
        if n is not None: fs = fs[:n]
        out.extend(fs)
    return out


# ---------------------------------------------------------------- the pass rule (FINDINGS section 7) as go_no_go-shaped items
def null_tape_check_from_diffs(real_diff, diffs, session_same_sign_min=PASS_RULE["session_same_sign_min"]):
    """diffs = {'gmm': [...], 'segment': [...], 'session': [...]} (one diff per certificate tape). Returns (passed, checks, summary):
    checks are (ok, value) pairs like harness.go_no_go's; passed = real diff > gmm p95 AND > segment p95 AND the session tapes
    carry the real sign in >= 75% of tapes."""
    q = lambda v, p: (round(float(np.nanquantile(v, p)), 2) if len(v) and np.isfinite(v).any() else None)
    ch, summ = {}, {}
    for g in ("gmm", "segment"):
        v = np.asarray(diffs.get(g, []), dtype=float); p95 = q(v, 0.95)
        ch[f"null_tape:real_diff>{g}_p95"] = (real_diff is not None and p95 is not None and real_diff > p95, p95)
        summ[g] = dict(n=int(len(v)), p50=q(v, 0.5), p95=q(v, 0.95), real_pct=(round(float(100 * np.nanmean(v < real_diff)), 1) if len(v) and real_diff is not None else None))
    v = np.asarray(diffs.get("session", []), dtype=float)
    same = float(np.nanmean(np.sign(v) == np.sign(real_diff))) if len(v) and real_diff is not None else None
    ch[f"null_tape:session_same_sign>={session_same_sign_min}"] = (same is not None and same >= session_same_sign_min, round(same, 3) if same is not None else None)
    summ["session"] = dict(n=int(len(v)), p50=q(v, 0.5), p95=q(v, 0.95), same_sign_share=(round(same, 3) if same is not None else None))
    summ["null_tape_diff_inr"] = {g: {"p50": summ[g]["p50"], "p95": summ[g]["p95"]} for g in ("gmm", "segment", "session") if g in summ}
    return all(v[0] for v in ch.values()), ch, summ


def null_tape_check(real_diff, tf, rules, controls=False, draws=H.CONTROL_DRAWS, label="L1", verbose=False):
    """The FINDINGS section 7 pass rule for a candidate rule list: evaluate it on the certificate tapes (tape_folders(tf, gen),
    healthy, the design count per generator), compare the real-tape diff (the candidate's ledger row) with the gmm / segment p95
    and the session sign share. Returns (passed, checks, summary); summary['per_tape'] holds every tape's result. Tape numbers
    never enter the ledger. Call it only after the candidate's real-tape ledger row exists (the tapes are not a search space)."""
    per, diffs = [], {}
    for g in ("gmm", "segment", "session"):
        diffs[g] = []
        for folder in tape_folders(tf, g):
            r = evaluate_rule_list(folder, rules, controls=controls, draws=draws, label=label)
            r.update(gen=g, k=_tape_k(folder)); per.append(r); diffs[g].append(np.nan if r["diff"] is None else r["diff"])
            if verbose: print(f"  {g}_{r['k']}: diff {r['diff']} kept_share {r['kept_share']}", flush=True)
    passed, ch, summ = null_tape_check_from_diffs(real_diff, diffs)
    summ.update(tf=tf, real_diff=real_diff, per_tape=per, tape_set="certificate (healthy, first DESIGN_N per generator)")
    return passed, ch, summ


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
