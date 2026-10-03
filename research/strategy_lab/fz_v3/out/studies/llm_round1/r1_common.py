"""llm_round1: definitions shared by step 1 (tables.py, the labelled summary tables) and step 3 (scorer.py).
DESIGN_PANEL deep-sequence-llm-hypotheses with Judge 1's cross-fitting and Judge 2's family-size rule; STUDY_AGENT_BRIEF rules.
Everything here was fixed before any labelled number of this study was looked at.

Unit / label / split   harness.load(tf) (label L1, the 15:25 book); IS rows only (SETUP date <= 2025-12-31). OOS rows are never read
                       (only the harness's own row counts).
Halves                 A = harness blocks 0-5, B = blocks 6-11 (Table.block of the IS rows; the 12 contiguous IS session blocks of the
                       harness splitter). A proposer sees the tables of ONE half; its rules are scored on the OTHER half (cross-fitted).
Vocabulary             the frozen shortlist (features_shortlist/<tf>/shortlist.json) is EMPTY on both timeframes (n_shortlisted = 0,
                       allowed_columns = [], sha registered 2026-09-29T11:31:33, no newer shortlist line), so the EMPTY-SHORTLIST RULE
                       applies: hour_bin, fz_read, dir (always) plus, as an exploratory vocabulary labelled "outside the frozen
                       shortlist", the representative of each of the top-8 clusters by log-loss MDA rank per timeframe
                       (studies/importance/importance_clusters_<tf>.csv, column mda_rank) and the columns of the design's four two-way
                       tables (fz_read x hour_bin, n_choch_since_bos x dir, hv3_dir_agree x hv3_bars_since bucket, fz_visit_n x fz_read).
Swap rule              a cluster is shown through its representative's SOURCE column (a one-hot `col=level` -> `col` by level; a missing
                       indicator `col__na` -> `col` as an NA indicator). When that source column is (a) always included, (b) an exact
                       duplicate of an always-included column on every IS row (card_read == fz_read), (c) a calendar-time proxy
                       (drift.json time_proxies: n_events_asof, sl) or (d) already shown for a higher-ranked cluster, the cluster is shown
                       through its highest-MDI member (importance_features_<tf>.csv mdi_mean) whose source column is not excluded by
                       (a)-(d); a single-member cluster with no admissible member is recorded as covered, with zero own cells. Every
                       swap is stated in the file header.
Bins                   text / boolean columns and integer columns with <= 12 distinct IS values: one row per level (+ NA when present);
                       other numeric columns: deciles of the HALF's own rows (np.nanquantile 0.1 .. 0.9, duplicate edges dropped,
                       bins [e_i, e_{i+1}), the first open below, the last open above) + an NA row. Fixed buckets: n_choch_since_bos
                       0 / 1 / 2 / 3 / 4 / >=5 (one-way) and 0 / 1 / 2 / >=3 (two-way); hv3_bars_since 0 / 1-5 / 6-15 / 16-60 / >60
                       bars on minute and 0 / 1 / 2-3 / 4-12 / >12 on 5minute (the same clock: 5 / 15 / 60 minutes) + NA;
                       fz_visit_n 1 / 2 / 3 / >=4 + NA (no ref room).
Cell                   one row of a one-way table or one populated cell of a two-way table: count, mean L1 net (INR per trade), win
                       rate. A cell with fewer than MIN_CELL_N = 5 units shows its count only (mean and win rate suppressed: no raw
                       rows) and is NOT a labelled cell. The half's base row (all rows) is one labelled cell.
Family size            labelled cells shown in tables_<tf>_<half>.json + rules proposed (round 0 and round 1): the max-T family of the
                       scorer (every labelled cell is a candidate skip set the proposer could have chosen).
Rule grammar           {"id", "if": [[column, op, value], ...] (<= 3 comparisons), "then": "skip", "reason", "cells"}; ops >=, >, <=,
                       <, ==, !=, in, not_in (the null-tape checker's tapes._cmp grammar); a None / NaN in a rule column makes the
                       comparison False (a skip rule never fires on an undefined value). Refused: a label column, a harness.NOT_FEATURES
                       column, a time proxy, depth > 3, a column absent from the table. Flagged (scored, but ineligible for the
                       combination): a column outside the vocabulary shown to the proposer, a numeric threshold that is not a table
                       edge / level / listed interaction split point of that column.
"""
import os, sys, json, hashlib, datetime as D
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H  # noqa: E402

STUDY = "llm_round1"
TFS = ("minute", "5minute")
HALVES = {"A": list(range(0, 6)), "B": list(range(6, 12))}
OTHER = {"A": "B", "B": "A"}
ALWAYS = ["hour_bin", "fz_read", "dir"]
TWOWAY = [("fz_read", "hour_bin"), ("n_choch_since_bos", "dir"), ("hv3_dir_agree", "hv3_bars_since"), ("fz_visit_n", "fz_read")]
TWOWAY_EXTRA_COLS = ["n_choch_since_bos", "hv3_dir_agree", "hv3_bars_since", "fz_visit_n"]
TOP_K_CLUSTERS = 8
MIN_CELL_N = 5
MAX_LEVELS_INT = 12
TIME_PROXIES_FALLBACK = ("n_events_asof", "sl")
OPS = (">=", ">", "<=", "<", "==", "!=", "in", "not_in")
OUTSIDE = "outside the frozen shortlist"
REGISTRATIONS = os.path.join(OUT, "ledger", "registrations.jsonl")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def now():
    return D.datetime.now().isoformat(timespec="seconds")


def rel(path):
    return os.path.relpath(path, OUT).replace(os.sep, "/")


# ---------------------------------------------------------------- data
def load_tf(tf, label="L1"):
    """harness.load(tf, label) with the 61 extended as-of columns joined on setup_i as T.FX (T.F itself is left as the harness built it)."""
    T = H.load(tf, label)
    E = pd.read_parquet(os.path.join(OUT, "features_ext", tf, "ext_features.parquet"))
    ext_cols = [c for c in E.columns if c != "setup_i"]
    FX = T.F.merge(E, on="setup_i", how="left", suffixes=("", "_ext"))
    assert len(FX) == len(T.F) and (FX.setup_i.to_numpy() == T.F.setup_i.to_numpy()).all(), "ext join changed the row order"
    T.FX = FX; T.ext_cols = ext_cols
    return T


def half_rows(T, half):
    """Row indices (into T) of the IS rows of a half."""
    return np.flatnonzero(T.is_mask & np.isin(T.block, HALVES[half]))


def sub_table(T, rows):
    """A harness.Table over a subset of T's rows (the OTHER half): harness.score on it reads exactly those rows as its IS split, so the
    kept-vs-skipped statistics, the session-matched control and the per-session vectors are those of that half alone."""
    F = T.F.iloc[rows].reset_index(drop=True); TR = T.TR.iloc[rows].reset_index(drop=True)
    S = H.Table(T.tf, T.label, F, TR, T.sessions)
    S.FX = T.FX.iloc[rows].reset_index(drop=True); S.ext_cols = getattr(T, "ext_cols", [])
    return S


def time_proxies(tf):
    cols = set(TIME_PROXIES_FALLBACK)
    p = os.path.join(OUT, "studies", "null_tapes_drift", "drift.json")
    if os.path.exists(p):
        tp = json.load(open(p, encoding="utf-8")).get("timeframes", {}).get(tf, {}).get("time_proxies")
        if tp: cols |= set(tp.keys() if isinstance(tp, dict) else tp)
    return cols


def drift_info(tf):
    """top-5 drifted source columns (a rule using one is also scored without it) and the top-20 (a caveat with the shift in sd)."""
    p = os.path.join(OUT, "studies", "null_tapes_drift", "drift.json")
    out = dict(top5_sources=[], top20={})
    if not os.path.exists(p): return out
    d = json.load(open(p, encoding="utf-8")).get("timeframes", {}).get(tf, {})
    out["top5_sources"] = list(d.get("top5_sources", []))
    for x in d.get("top20_drifted", []):
        src = x.get("source") or x.get("feature")
        if src: out["top20"][src] = dict(shift_sd=x.get("shift_sd", x.get("std_shift")), direction=x.get("direction"), ks=x.get("ks"))
    return out


def interaction_pairs(tf):
    """The five pairs of the frozen shortlist with their split points (the only depth-2/3 conjunctions the design allows beyond the
    table columns); a pair that involves a time proxy is listed as refused."""
    sl = json.load(open(os.path.join(OUT, "features_shortlist", tf, "shortlist.json"), encoding="utf-8"))
    proxies = time_proxies(tf)
    out = []
    for p in sl.get("interaction_pairs_top5", []):
        a, b = p["feature_a"], p["feature_b"]
        sa, sb = source_of(a)[0], source_of(b)[0]
        out.append(dict(feature_a=a, feature_b=b, source_a=sa, source_b=sb,
                        split_a=sorted({round(float(v), 4) for v in [p.get("split_a_gain_weighted_median")] + list(p.get("split_a_common", [])) if v is not None}),
                        split_b=sorted({round(float(v), 4) for v in [p.get("split_b_gain_weighted_median")] + list(p.get("split_b_common", [])) if v is not None}),
                        refused=(sa in proxies or sb in proxies), refused_why=("calendar-time proxy (drift.json time_proxies)" if (sa in proxies or sb in proxies) else None)))
    return dict(shortlist_sha256=sha256(os.path.join(OUT, "features_shortlist", tf, "shortlist.json")), n_shortlisted=sl.get("n_shortlisted"),
                allowed_columns=sl.get("allowed_columns", []), pairs=out)


# ---------------------------------------------------------------- vocabulary
def source_of(feat):
    """'col=level' -> (col, level); 'col__na' -> (col, '__na'); 'col' -> (col, None)."""
    if "=" in feat:
        c, lv = feat.split("=", 1); return c, lv
    if feat.endswith("__na"): return feat[:-4], "__na"
    return feat, None


def _levels(series):
    so = series.astype(object)
    return so.map(lambda z: None if z is None or z is pd.NA or (isinstance(z, float) and np.isnan(z)) else str(z))


def is_numeric(series):
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def kind_of(col, series):
    if col == "n_choch_since_bos": return "nchoch"
    if col == "hv3_bars_since": return "hv3b"
    if col == "fz_visit_n": return "visit"
    if is_numeric(series):
        return "level" if series.dropna().nunique() <= MAX_LEVELS_INT else "decile"
    return "level"


def resolve_vocabulary(tf, F_is):
    """The columns shown per timeframe under the EMPTY-SHORTLIST RULE and the swap rule (module docstring). F_is = the IS rows (FX)."""
    cl = pd.read_csv(os.path.join(OUT, "studies", "importance", f"importance_clusters_{tf}.csv")).sort_values("mda_rank")
    fe = pd.read_csv(os.path.join(OUT, "studies", "importance", f"importance_features_{tf}.csv"))
    mdi = dict(zip(fe.feature, fe.mdi_mean))
    proxies = time_proxies(tf)
    dups = {}
    if "card_read" in F_is.columns and (_levels(F_is["card_read"]).fillna("<NA>") == _levels(F_is["fz_read"]).fillna("<NA>")).all():
        dups["card_read"] = "fz_read"
    vocab, shown = [], set()
    for c in ALWAYS:
        vocab.append(dict(column=c, kind=kind_of(c, F_is[c]), provenance="always included (design: hour_bin, fz_read, dir)", label="design", cluster=None, mda_rank=None, representative=None, swap=None, caveats=[]))
        shown.add(c)
    for _, r in cl.head(TOP_K_CLUSTERS).iterrows():
        rep = str(r["representative"]); members = [m.strip() for m in str(r["members"]).split(";") if m.strip()]
        cand = [rep] + sorted([m for m in members if m != rep], key=lambda m: -float(mdi.get(m, 0.0)))
        chosen, notes = None, []
        for feat in cand:
            src, lv = source_of(feat)
            if src in proxies: notes.append(f"`{feat}`: calendar-time proxy (drift.json time_proxies), refused"); continue
            base = dups.get(src, src)
            if base in shown: notes.append(f"`{feat}`: source column `{base}` already shown" + (f" (`{src}` == `{base}` on every IS row)" if src in dups else "")); continue
            if src not in F_is.columns: notes.append(f"`{feat}`: column `{src}` not in the table"); continue
            chosen = (feat, src, lv); break
        entry = dict(cluster=int(r["cluster"]), mda_rank=int(r["mda_rank"]), representative=rep, n_members=int(r["n_members"]),
                     mda_ll_mean=float(r["mda_ll_mean"]), mda_ll_std=float(r["mda_ll_std"]), members=members,
                     provenance=f"{OUTSIDE}: importance cluster {int(r['cluster'])}, log-loss MDA rank {int(r['mda_rank'])} of {len(cl)} (MDA mean {float(r['mda_ll_mean']):.5f}, std {float(r['mda_ll_std']):.5f}; the cluster does NOT pass the shortlist rule)",
                     label=OUTSIDE)
        if chosen is None:
            entry.update(column=None, kind=None, swap="; ".join(notes), covered_by=[n for n in notes], caveats=["no admissible member: the cluster is covered by tables already shown; zero own cells"])
            vocab.append(entry); continue
        feat, src, lv = chosen
        kind = "na_indicator" if lv == "__na" else kind_of(src, F_is[src])
        swap = None
        if feat != rep:
            swap = f"representative `{rep}` not shown ({'; '.join(notes)}); shown through the highest-MDI admissible member `{feat}` (MDI {float(mdi.get(feat, 0.0)):.5f}) -> column `{src}`"
        elif lv is not None and lv != "__na":
            swap = f"representative `{rep}` is a one-hot level: its source column `{src}` is shown by level"
        elif lv == "__na":
            swap = f"representative `{rep}` is a missing indicator: `{src}` is shown as an NA indicator (NA / not NA)"
        caveats = []
        if src.startswith(("ffd_", "bsadf_", "csw_", "bocpd_", "gmm", "hmm", "jump", "nn_dist", "p1_dist", "rv_", "win_", "cusum_")):
            caveats.append("extended as-of column (features_ext): not a features.parquet column; a rule on it needs a new per-bar routine in the lab (a user decision, never assumed)")
        if src == "ffd_close_dstar":
            caveats.append("FFD of the log close at d* = 0.2 keeps most of the price level: the importance study calls it a calendar-time proxy and did not adopt FFD (MDA <= 1 std on both timeframes); a rule on it is a level rule and must hold inside every period")
        di = drift_info(tf)
        if src in di["top5_sources"]: caveats.append(f"top-5 drifted source column IS-early vs IS-late (drift.json): a selected rule on it is also scored without it")
        if src in di["top20"]: caveats.append(f"top-20 drifted column: shift {di['top20'][src].get('shift_sd')} sd, {di['top20'][src].get('direction')}")
        entry.update(column=src, kind=kind, swap=swap, caveats=caveats, via_member=feat)
        vocab.append(entry); shown.add(src)
    for c in TWOWAY_EXTRA_COLS:
        if c in shown: continue
        vocab.append(dict(column=c, kind=kind_of(c, F_is[c]), provenance=f"{OUTSIDE}: a column of the design's two-way tables (not in any top-8 cluster)", label=OUTSIDE, cluster=None, mda_rank=None, representative=None, swap=None, caveats=[]))
        shown.add(c)
    return vocab, dups


# ---------------------------------------------------------------- bins and cells
def decile_edges(x):
    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]
    if len(x) == 0: return []
    e = np.nanquantile(x, np.arange(0.1, 1.0, 0.1))
    out = []
    for v in e:
        v = round(float(v), 4)
        if not out or v > out[-1]: out.append(v)
    return out


def make_bins(col, series, kind, tf, edges=None):
    """The bins of a column for a half; `edges` overrides the decile edges (the scorer rebuilds the SEEN half's bins on the other half)."""
    bins = []
    if kind == "nchoch":
        for v in range(5): bins.append(dict(kind="range", lo=v, hi=v, hi_inclusive=True, label=str(v)))
        bins.append(dict(kind="range", lo=5, hi=None, hi_inclusive=True, label=">=5"))
    elif kind == "nchoch2":
        for v in range(3): bins.append(dict(kind="range", lo=v, hi=v, hi_inclusive=True, label=str(v)))
        bins.append(dict(kind="range", lo=3, hi=None, hi_inclusive=True, label=">=3"))
    elif kind == "hv3b":
        cuts = [(0, 0), (1, 5), (6, 15), (16, 60), (61, None)] if tf == "minute" else [(0, 0), (1, 1), (2, 3), (4, 12), (13, None)]
        for lo, hi in cuts: bins.append(dict(kind="range", lo=lo, hi=hi, hi_inclusive=True, label=(f"{lo}" if hi == lo else (f"{lo}-{hi}" if hi is not None else f">={lo}")) + " bars"))
        bins.append(dict(kind="na", label="NA (no bar with vol_ratio20 >= 3 in the session so far)"))
    elif kind == "visit":
        for v in (1, 2, 3): bins.append(dict(kind="range", lo=v, hi=v, hi_inclusive=True, label=str(v)))
        bins.append(dict(kind="range", lo=4, hi=None, hi_inclusive=True, label=">=4"))
        bins.append(dict(kind="na", label="NA (no ref room)"))
    elif kind == "na_indicator":
        bins.append(dict(kind="notna", label=f"{col} defined")); bins.append(dict(kind="na", label=f"{col} NA"))
    elif kind == "level":
        if is_numeric(series):
            lv = sorted(set(float(v) for v in series.dropna().unique()))
            for v in lv: bins.append(dict(kind="range", lo=v, hi=v, hi_inclusive=True, label=(str(int(v)) if float(v).is_integer() else str(v))))
        else:
            for v in sorted(set(_levels(series).dropna().unique())): bins.append(dict(kind="level", level=v, label=v))
        if series.isna().sum() or (not is_numeric(series) and _levels(series).isna().any()): bins.append(dict(kind="na", label="NA"))
    elif kind == "decile":
        e = decile_edges(series.to_numpy(dtype=float)) if edges is None else list(edges)
        if not e: bins.append(dict(kind="range", lo=None, hi=None, hi_inclusive=True, label="all defined"))
        else:
            bins.append(dict(kind="range", lo=None, hi=e[0], hi_inclusive=False, label=f"< {e[0]}"))
            for a, b in zip(e[:-1], e[1:]): bins.append(dict(kind="range", lo=a, hi=b, hi_inclusive=False, label=f"[{a}, {b})"))
            bins.append(dict(kind="range", lo=e[-1], hi=None, hi_inclusive=True, label=f">= {e[-1]}"))
        bins.append(dict(kind="na", label="NA"))
    else:
        raise ValueError(kind)
    for i, b in enumerate(bins): b["i"] = i
    return bins


def bin_mask(series, b):
    if b["kind"] == "na":
        return _levels(series).isna().to_numpy() if not is_numeric(series) else ~np.isfinite(series.to_numpy(dtype=float))
    if b["kind"] == "notna":
        return ~bin_mask(series, dict(kind="na"))
    if b["kind"] == "level":
        return (_levels(series) == b["level"]).to_numpy()
    x = pd.to_numeric(series.astype(object), errors="coerce").to_numpy(dtype=float) if not is_numeric(series) else series.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        m = np.isfinite(x)
        if b.get("lo") is not None: m &= x >= b["lo"]
        if b.get("hi") is not None: m &= (x <= b["hi"]) if b.get("hi_inclusive", True) else (x < b["hi"])
    return m


def allowed_thresholds(kind, bins):
    """The numeric values a proposer may use as thresholds for a column (the printed decile edges / bucket boundaries / levels)."""
    vals = set()
    for b in bins:
        if b["kind"] == "range":
            for k in ("lo", "hi"):
                if b.get(k) is not None: vals.add(round(float(b[k]), 4))
    return sorted(vals)


def cell_stats(net, win, mask):
    n = int(mask.sum())
    if n < MIN_CELL_N: return dict(n=n, mean_net=None, win_rate=None, labelled=False)
    return dict(n=n, mean_net=round(float(net[mask].mean()), 2), win_rate=round(float(win[mask].mean()), 4), labelled=True)


# ---------------------------------------------------------------- rule grammar (tapes._cmp semantics)
_NP = {">=": np.greater_equal, ">": np.greater, "<=": np.less_equal, "<": np.less, "==": np.equal, "!=": np.not_equal}


def comp_mask(series, op, value):
    if op in ("in", "not_in"):
        vals = [str(v) for v in (value if isinstance(value, (list, tuple, set)) else [value])]
        s = _levels(series); hit = s.isin(vals).to_numpy() & s.notna().to_numpy()
        return hit if op == "in" else (~hit & s.notna().to_numpy())
    if op not in _NP: raise ValueError(f"unknown op {op}")
    if is_numeric(series) or pd.api.types.is_bool_dtype(series):
        x = series.to_numpy(dtype=float)
        with np.errstate(invalid="ignore"): hit = _NP[op](x, float(value))
        return hit & np.isfinite(x)
    if op in ("==", "!="):
        s = _levels(series); hit = (s == str(value)).to_numpy() & s.notna().to_numpy()
        return hit if op == "==" else (~hit & s.notna().to_numpy())
    x = pd.to_numeric(series.astype(object), errors="coerce").to_numpy(dtype=float)
    with np.errstate(invalid="ignore"): hit = _NP[op](x, float(value))
    return hit & np.isfinite(x)


def rule_fires(F, rule):
    m = np.ones(len(F), dtype=bool)
    for col, op, val in rule["if"]: m &= comp_mask(F[col], op, val)
    return m


def check_rule(rule, tf, F, tables_json, pairs, proxies):
    """Protocol check of one proposed rule against the tables its proposer saw. Returns dict(refused, flags, columns)."""
    flags, refused = [], None
    conds = rule.get("if", [])
    if str(rule.get("then", "skip")).lower() != "skip": refused = f"then = {rule.get('then')}: only skip rules are scored"
    if len(conds) == 0 or len(conds) > 3: refused = refused or f"depth {len(conds)} (must be 1..3)"
    vocab_cols = {v["column"] for v in tables_json["vocabulary"] if v.get("column")}
    thr = {v["column"]: set(v.get("allowed_thresholds", [])) for v in tables_json["vocabulary"] if v.get("column")}
    levels = {v["column"]: set(v.get("levels", [])) for v in tables_json["vocabulary"] if v.get("column")}
    pair_cols, pair_thr = set(), {}
    for p in pairs["pairs"]:
        if p["refused"]: continue
        pair_cols |= {p["source_a"], p["source_b"]}
        pair_thr.setdefault(p["source_a"], set()).update(p["split_a"]); pair_thr.setdefault(p["source_b"], set()).update(p["split_b"])
    cols = []
    for c in conds:
        if not (isinstance(c, (list, tuple)) and len(c) == 3): refused = refused or f"malformed comparison {c}"; continue
        col, op, val = c; cols.append(col)
        if col not in F.columns: refused = refused or f"column {col} not in the feature table"; continue
        if str(col).startswith(H.LABEL_PREFIX) or col in H.NOT_FEATURES: refused = refused or f"{col} is not an as-of feature"; continue
        if col in proxies: refused = refused or f"{col} is a calendar-time proxy (drift.json time_proxies): a calendar rule, refused"; continue
        if op not in OPS: refused = refused or f"operator {op}"; continue
        if col not in vocab_cols and col not in pair_cols: flags.append(f"outside the shown vocabulary: {col}")
        if op in ("in", "not_in", "==", "!=") and not is_numeric(F[col]):
            vals = [str(v) for v in (val if isinstance(val, (list, tuple)) else [val])]
            bad = [v for v in vals if col in levels and levels[col] and v not in levels[col]]
            if bad: flags.append(f"level not in the table: {col} {op} {bad}")
        elif op in _NP:
            try: v = round(float(val), 4)
            except (TypeError, ValueError): refused = refused or f"non-numeric threshold {val} for {col}"; continue
            ok = (col in thr and v in thr[col]) or (col in pair_thr and v in pair_thr[col])
            if not ok: flags.append(f"threshold not a table edge / listed split point: {col} {op} {val}")
    return dict(refused=refused, flags=flags, columns=cols)


def registration_lines():
    if not os.path.exists(REGISTRATIONS): return []
    return [json.loads(x) for x in open(REGISTRATIONS, encoding="utf-8") if x.strip()]


def append_registration(rec):
    """Append-only; never edits. Returns True when written, False when an identical (kind, what, sha256) line exists."""
    for r in registration_lines():
        if r.get("kind") == rec.get("kind") and r.get("what") == rec.get("what") and r.get("sha256") == rec.get("sha256"): return False
    with open(REGISTRATIONS, "a", encoding="utf-8") as f: f.write(json.dumps(rec, default=str) + "\n")
    return True
