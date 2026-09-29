"""gate_family: the ONE learned-gate trial family of the FZ v3 program (DESIGN_PANEL quant-ml-canon-meta-label-gate merged with
decision-making-1-fullinfo-bandit-policy-tree-gate and BRIEF H5; both judges' fixes on both studies are binding). Every definition
below was fixed before any number of this study was looked at; the numbers of the earlier studies (importance, null_tapes_drift,
exit_policy, h1, h2_h3_h4, session_stop) were read, as the task requires.

EMPTY-SHORTLIST RULE (in force: features_shortlist/<tf>/shortlist.json has n_shortlisted = 0 on both timeframes, allowed_columns = []):
two sub-families are run and reported side by side.
  (I)  "context"  features = hour_bin one-hot (9 levels) + dir (dir=down; dir=up is its complement and is dropped): the context the
       design always includes and the user's own words ("it is different for different times"). Inside the frozen vocabulary.
  (II) "h5_full"  H5 as pre-registered in docs/STRATEGY_ANALYSIS_TODO.md S49 on the FULL as-of table: imp_lib.assemble(tf) (the same
       276 / 238-feature matrix the importance study used: harness.design + the 61 features_ext columns, > 40% NaN / constant /
       duplicate / second-one-hot-level drops, missing indicators) MINUS the two calendar proxies drift.json names (`sl`,
       `n_events_asof`; null_tapes_drift FINDINGS section 6: "a rule on a time proxy is a calendar rule, not a market rule ...
       the gate studies refuse it on the real tape by the same rule"). OUTSIDE THE FROZEN SHORTLIST: every table row and ledger
       note of this sub-family says so; a candidate from it carries provenance.vocabulary = "outside the frozen shortlist
       (importance rule failed for every cluster)".

Unit / labels     harness.load(tf) (L1 = the 15:25 intraday book: the training and judging label). Robustness labels (one table,
                  never candidates): L0 = harness.load(tf, "L0"); L2x1 / L2x2 = symmetric triple barrier built from bars.parquet
                  (labels.py: lower barrier = the Foundation stop `sl`, upper = entry + 1x / 2x the stop distance, vertical = the
                  entry session's 15:25 bar (build.py eod_bar) capped at the contract's last candle; first touch with the engine's
                  same-bar conventions: stop before target on the same bar, a fill at the bar's open when it opens beyond the level,
                  else at the level, a session's first candle fills at its close; priced as build.py price()); L3 = trend scanning
                  (OLS slope t-value of close over bars k+1..k+h, h = 5..60, same session; net_L3 = dir_sign x t at the horizon of
                  max |t|, exit bar = k + h*; a row with fewer than 5 same-session bars after k has weight 0). A robustness gate is
                  trained on its label's table (splits purged by that label's exit bar) and scored on the same table AND on L1 (the
                  book ST13/ST14 trade) when the rows coincide (L2/L3); L0 is scored on L0 (its row set differs: the SETUPs at or
                  after 15:25).
Weights           one scheme: |net| winsorised at the TRAINING fold's 99th percentile, times class balance (equal total weight per
                  class), normalised to mean 1. Sensitivity only (12-block OOF, no CPCV): the AFML time-decay c = 0.5 variant
                  (oldest training row x 0.5 .. newest x 1, linear in time rank), because the pre-registered break tests found no
                  break inside IS. The regressor (c) is fit on net winsorised at the training fold's 1st / 99th percentile with
                  uniform weights.
Splits            harness.purged_splits (12 blocks, purge by the label's exit bar, 3-session embargo) for the OOF tables;
                  harness.cpcv_splits -> cpcv_paths -> score_paths (66 splits, 11 paths, controls ON) for every learner; every
                  threshold is chosen INSIDE the training fold.
tau (nested)      for a probability learner: the p_win threshold on the coarse grid {0.10, 0.15, ..., 0.40} maximising the kept mean
                  net of the training fold's out-of-fold predictions (an inner 4-fold purged CV over the training blocks; the
                  bagging uses its out-of-bag probabilities instead) subject to |net|-weighted winner recall >= 0.90; when no grid
                  value satisfies the constraint the grid floor 0.10 is used (the importance study's rule). For the regressor (c):
                  tau_r on {-1500, -1250, ..., 0, 250} INR with the same rule. For the scorecard (e): the integer score is mapped to
                  p_win by a 1-D logistic (Platt) fit on the inner-CV scores, and tau is applied to that p_win (s = the equivalent
                  score threshold). Every tau of the grid is also scored as a pooled fixed-tau OOF gate: one ledger row per tau
                  (family gate_family/<sub>/<model>/tau, controls off: they are trials for PBO / SPA, never candidates).
Models            (a) BaggingClassifier(DecisionTreeClassifier(max_depth 4 (3 and 5 as a sensitivity), min_weight_fraction_leaf 0.05,
                      class_weight balanced), 300 trees, bootstrap, max_samples = the label's average uniqueness, oob_score) on
                      the training-fold-median-imputed matrix;
                  (b) HistGradientBoostingClassifier(max_depth 3, max_iter 200, learning_rate 0.05, l2_regularization 1.0,
                      early_stopping off, class balance via the weights, interaction_cst = the importance study's clusters plus
                      the top-5 interaction pairs (h5_full) / one group (context), monotonic_cst = -1 on n_choch_since_bos,
                      n_choch_since_bos_today, alt_dir6 (H2: more CHoCH churn = sideways = worse; the only hypothesis with a
                      stated direction); the unconstrained variant is a sensitivity row);
                  (c) HistGradientBoostingRegressor (same shape) on winsorised net, take iff E[net | x] > tau_r;
                  (d) value-maximising policy trees (Zhou-Athey-Wager form, two actions: take = net, skip = 0): exact depth 1,
                      greedy depth 2 / 3; split candidates = every feature x 30 training-fold quantile thresholds (0.5 for binary
                      columns); split criterion = the sum of winsorised (1 / 99) net over each child's take decision
                      (child value = max(0, sum)); min leaf 100 rows (1m) / 40 (5m); a leaf takes iff its sum > 0; NaN rows fall
                      out of every condition (the rule grammar: NaN never satisfies a comparison) and are taken by default;
                  (e) the binned logistic scorecard: 5 quantile bins per numeric feature (training-fold edges; NaN = no bin, 0
                      points), binary / one-hot columns as indicators; L1 LogisticRegression (liblinear) with the study weights;
                      C lowered on a geometric path until at most 12 (1m) / 6 (5m) source features carry a non-zero coefficient;
                      coefficients rounded to integer points on a 20-point scale; skip if score < s (s from tau via the Platt map);
                  H5 (sub-family II only, as pre-registered): dt3 = DecisionTreeClassifier(max_depth 3, min_samples_leaf 100 / 40)
                      with the study weights and the nested tau; h5rules = the greedy rule-list search (<= 8 conjunctive rules of
                      depth <= 3, thresholds at 30 quantile grid points, greedy by kept expectancy on the TRAINING fold, a rule
                      is extended to depth 2 / 3 while that improves the kept mean, the search stops when the marginal training
                      gain < 200 INR/trade or a leaf would fall under the min-leaf floor).
Distillation      to each probability / value learner's OOF DECISION (p_win >= tau, never the label): a depth-3
                  DecisionTreeClassifier (min leaf 100 / 40) and a greedy rule list (<= 8 rules, depth <= 3, greedy by
                  covered-skip minus covered-take over the still-uncovered rows, thresholds at the quantile grid). Nested form
                  (honest): inside every split the rule list is fit to the learner's inner-CV decisions on the training rows and
                  applied to the test rows (its own 12-block OOF and CPCV are ledger rows). Frozen form: the rule list fit to the
                  pooled 12-block OOF decisions over all IS rows (a selection on pooled OOF: one ledger row, family
                  gate_family/<sub>/<model>/frozen_rules). Fidelity = agreement with the learner's decisions; skip precision /
                  recall reported. The policy trees, dt3 and h5rules are rule lists already (fidelity 1 by construction).
Rule grammar      the LLM-round-0 grammar tapes.rule_mask evaluates: [{"if": [[column, op, value], ...] (<= 3), "then": "skip"}],
                  default take; a one-hot design column `src=level` becomes [src, "==", level] (present) / [src, "!=", level]
                  (absent, source not missing); a missing indicator `__na` and a `=nan` level are not expressible and are excluded
                  from every rule search; an ext-features column is expressible on the real tape (joined on setup_i) but not on
                  the null tapes (flagged). Every rule-list keep mask in this study is computed by tapes.rule_mask on the feature
                  frame (the shipped semantics), never by the tree that produced it.
Judgement         harness.score rows (kept-vs-skipped diff, control percentile, permutation p, loser recall / precision, |net|-weighted
                  winner recall, top-decile winners skipped, top-1%-removed diff (a hard pass), kept mean at 8 pts slippage, block
                  sign count, kept floors), the CPCV distribution (median, 5th percentile), harness.pbo("diff") / spa /
                  effective_trials over every gate_family ledger row of the timeframe with label L1, deflated_sharpe with n_trials =
                  the family size, bootstrap_ci; harness.go_no_go with every argument filled; the null-tape check
                  (tapes.null_tape_check) and the drift refit (drift.json top5_sources) for the finalist.
Why not RL        one-step decision per SETUP, the counterfactual (Foundation's own trade) is observed for every SETUP taken or not,
                  0 overlapping positions on L1 by construction: the take / skip choice is supervised meta-labelling / a
                  full-information contextual bandit whose off-policy value is exact (sum of pi(x) net(x)); no state carries over
                  from one decision to the next, so there is no return to bootstrap and nothing for a sequential learner to do.
"""
import os, sys, json, time, math, hashlib, datetime as D, warnings, pickle
sys.dont_write_bytecode = True
import numpy as np, pandas as pd, psutil
from sklearn.ensemble import BaggingClassifier, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (OUT, os.path.join(OUT, "studies", "importance"), os.path.join(OUT, "studies", "null_tapes_drift")):
    if p not in sys.path: sys.path.insert(0, p)
import harness as H          # noqa: E402
import imp_lib               # noqa: E402  the importance study's feature assembly (the same 276 / 238 matrix)
import tapes                 # noqa: E402  the rule grammar evaluator and the null tapes

RES = os.path.join(HERE, "results")
STUDY = "gate_family"
TAU_GRID = [round(x, 2) for x in np.arange(0.10, 0.401, 0.05)]
TAUR_GRID = [-1500.0, -1250.0, -1000.0, -750.0, -500.0, -250.0, 0.0, 250.0]
WREC_MIN = 0.90
MIN_LEAF = {"minute": 100, "5minute": 40}
N_Q, INNER_K = 30, 4
SC_BINS, SC_MAX, SC_SCALE = 5, {"minute": 12, "5minute": 6}, 20
SC_C_PATH = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.0039, 0.002, 0.001]
H5_STOP_GAIN, MAX_RULES, MAX_DEPTH = 200.0, 8, 3
N_TREES, BAG_DEPTH_MAIN, BAG_DEPTHS_SENS, BAG_MIN_LEAF_FRAC = 300, 4, (3, 5), 0.05
HGB = dict(max_depth=3, max_iter=200, learning_rate=0.05, l2_regularization=1.0, early_stopping=False, random_state=0)
DECAY_C = 0.5
MONO = {"n_choch_since_bos": -1, "n_choch_since_bos_today": -1, "alt_dir6": -1}
N_JOBS = int(os.environ.get("GF_JOBS", "4"))
CEILING_IDS = {"minute": "7359bf6294568ac8", "5minute": "1a12e823ea7cf4c7"}   # the importance study's bagging ceiling (not refit)
SUB_NOTE = {"context": "sub-family I (context: hour_bin one-hot + dir; inside the frozen vocabulary)",
            "h5_full": "sub-family II (h5_full: the full as-of table; OUTSIDE THE FROZEN SHORTLIST: the importance rule failed for every cluster)"}


def rss_mb(): return round(psutil.Process().memory_info().rss / 2 ** 20, 1)


class Log:
    def __init__(self, path):
        self.fh = open(path, "a", encoding="utf-8"); self.t0 = time.time()
    def __call__(self, msg):
        line = f"[{D.datetime.now().strftime('%H:%M:%S')} +{time.time() - self.t0:7.1f}s rss {rss_mb():6.1f} MB] {msg}"
        print(line, flush=True); self.fh.write(line + "\n"); self.fh.flush()


def jdump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=lambda z: z.item() if hasattr(z, "item") else (list(z) if isinstance(z, (set, tuple)) else str(z)))


def sha256_file(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- features
def ext_frame(tf, setup_i):
    E = pd.read_parquet(os.path.join(OUT, "features_ext", tf, "ext_features.parquet"))
    cols = [c for c in E.columns if c != "setup_i"]
    return E.set_index("setup_i").reindex(setup_i)[cols].reset_index(drop=True), cols


def context_features(T):
    """Sub-family I: hour_bin one-hot (all 9 levels) + dir=down."""
    X, src = H.design(T, cols=["hour_bin", "dir"])
    X = X.drop(columns=[c for c in X.columns if c == "dir=up"])
    src = {c: s for c, s in src.items() if c in X.columns}
    info = {c: col_info(c, T.F, [], src) for c in X.columns}
    return X.reset_index(drop=True), info, dict(sub="context", n_features=int(X.shape[1]), columns=list(X.columns))


def full_features(tf, log=None):
    """Sub-family II: imp_lib.assemble(tf) (the importance matrix) minus the drift.json time proxies."""
    T, Xa, meta = imp_lib.assemble(tf, None)
    proxies = sorted(tapes.time_proxies(tf))
    drop = [c for c in Xa.columns if c.split("=")[0].replace("__na", "") in proxies]
    Xa = Xa.drop(columns=drop).reset_index(drop=True)
    meta["dropped_time_proxies"] = drop; meta["time_proxies"] = proxies; meta["n_features_final_after_proxies"] = int(Xa.shape[1])
    _, src = H.design(T)
    E, ext_cols = ext_frame(tf, T.setup_i)
    info = {c: col_info(c, T.F, ext_cols, src, meta["missing_indicators"]) for c in Xa.columns}
    cl = json.load(open(os.path.join(OUT, "studies", "importance", f"clusters_{tf}.json")))["clusters"]
    sl = json.load(open(os.path.join(OUT, "features_shortlist", tf, "shortlist.json")))
    pairs = [(p["feature_a"], p["feature_b"]) for p in sl["interaction_pairs_top5"]]
    meta.update(sub="h5_full", clusters_n=len(cl), interaction_pairs=pairs, shortlist_n=sl["n_shortlisted"],
                pairs_with_time_proxy=[list(p) for p in pairs if p[0] in proxies or p[1] in proxies])
    if log: log(f"{tf} h5_full: {Xa.shape[1]} features after dropping time proxies {drop}; clusters {len(cl)}; pairs {pairs}")
    return T, Xa, info, meta, cl, pairs, E


def matrix_for(T, template_cols, ind_cover, tf):
    """The same feature matrix (template columns) on another Table's rows (L0: the L1 rows plus the SETUPs at / after 15:25)."""
    X, _ = H.design(T)
    E, _ = ext_frame(tf, T.setup_i)
    X = pd.concat([X.reset_index(drop=True), E], axis=1)
    out = {}
    for c in template_cols:
        if c in X.columns: out[c] = X[c].to_numpy(dtype=float)
        elif c.endswith("__na"):
            cover = ind_cover.get(c, [c[:-4]])
            out[c] = X[cover[0]].isna().astype(float).to_numpy() if cover[0] in X.columns else np.zeros(T.n)
        elif "=" in c: out[c] = np.zeros(T.n)
        else: out[c] = np.full(T.n, np.nan)
    return pd.DataFrame(out)


def col_info(col, F, ext_cols, src_map, ind_cover=None):
    """kind: numeric | binary | onehot | na (inexpressible in the rule grammar) ; src, level, ext flag."""
    if col.endswith("__na"): return dict(kind="na", src=col[:-4], ext=False)
    if "=" in col:
        s, lv = col.split("=", 1)
        if lv == "nan": return dict(kind="na", src=s, level=lv, ext=False)
        return dict(kind="onehot", src=s, level=lv, ext=False)
    ext = col in ext_cols
    return dict(kind="numeric", src=col, ext=ext)


# ---------------------------------------------------------------- labels
def load_labels(tf):
    p = os.path.join(RES, f"labels_{tf}.parquet")
    return pd.read_parquet(p) if os.path.exists(p) else None


def label_table(T, tf, name, L):
    """A harness.Table under a robustness label built on the L1 rows (L2x1 / L2x2 / L3), or None for L0 (loaded separately)."""
    if name == "L1": return T
    L = L.set_index("setup_i").reindex(T.setup_i)
    if name in ("L2x1", "L2x2"):
        m = name[-1]
        return T.with_label(name, L[f"l2m{m}_net"].to_numpy(dtype=float), L[f"l2m{m}_exit_i"].to_numpy(dtype=float).astype(int),
                            pts=L[f"l2m{m}_pts"].to_numpy(dtype=float))
    if name == "L3":
        net = L["l3_net"].to_numpy(dtype=float); net = np.where(np.isnan(net), 0.0, net)
        return T.with_label(name, net, L["l3_exit_i"].to_numpy(dtype=float).astype(int))
    raise ValueError(name)


def avg_uniqueness(T, rows):
    """AFML average uniqueness of the label lifetimes [entry, exit] among rows (1.0 when no two lifetimes overlap)."""
    e0, e1 = T.entry_bar[rows], T.exit_bar[rows]
    lo, hi = int(e0.min()), int(e1.max()) + 1
    conc = np.zeros(hi - lo + 1)
    np.add.at(conc, e0 - lo, 1); np.add.at(conc, e1 - lo + 1, -1)
    conc = np.cumsum(conc)[:-1]
    u = np.array([np.mean(1.0 / conc[a - lo:b - lo + 1]) for a, b in zip(e0, e1)])
    return float(u.mean())


# ---------------------------------------------------------------- weights and the nested threshold
def make_weights(net, win, decay=None):
    a = np.abs(net); cap = float(np.quantile(a, 0.99)); w = np.minimum(a, cap)
    w = w / max(w.mean(), 1e-12)
    for cls in (True, False):
        m = win == cls
        if m.any() and w[m].sum() > 0: w[m] *= 0.5 * w.sum() / w[m].sum()
    if decay is not None: w = w * decay
    w = w / max(w.mean(), 1e-12)
    return w, cap


def decay_weights(order_key, c=DECAY_C):
    r = np.argsort(np.argsort(order_key)).astype(float); n = len(r)
    return c + (1 - c) * (r / max(n - 1, 1))


def choose_tau(p, net, win, grid):
    """max kept mean net s.t. |net|-weighted winner recall >= 0.90 over the grid; the grid floor when nothing satisfies it."""
    tot = float(net[win].sum()); best, best_val, table = None, -np.inf, []
    for tau in grid:
        kept = p >= tau
        if kept.sum() == 0: table.append(dict(tau=tau, kept_n=0, wrec=None, kept_mean=None)); continue
        wrec = float(net[kept & win].sum() / tot) if tot > 0 else 1.0
        km = float(net[kept].mean())
        table.append(dict(tau=tau, kept_n=int(kept.sum()), wrec=round(wrec, 4), kept_mean=round(km, 2)))
        if wrec >= WREC_MIN and km > best_val: best, best_val = tau, km
    return (best if best is not None else grid[0]), table, best is not None


def inner_groups(T, tr, k=INNER_K):
    """Inner purged CV over the training fold: its blocks split into k contiguous groups; purge + embargo by harness._purge."""
    blocks = np.array(sorted(set(T.block[tr].tolist())))
    out = []
    for g in np.array_split(blocks, min(k, len(blocks))):
        g = [int(x) for x in g]
        te_i = tr[np.isin(T.block[tr], g)]
        tr_i = H._purge(T, tr[~np.isin(T.block[tr], g)], g)
        if len(te_i) and len(tr_i): out.append((tr_i, te_i))
    return out


def impute_fit(Xtr):
    med = np.nanmedian(Xtr, axis=0); return np.where(np.isnan(med), 0.0, med)


def impute_apply(X, med): return np.where(np.isnan(X), med, X)


# ---------------------------------------------------------------- the condition bank (rule grammar) and rule evaluation
class CondBank:
    """Every rule-grammar condition over the feature matrix, thresholds from the fit rows: numeric `<= t` / `> t` at 30 quantile
    points, binary / one-hot `absent` / `present` (0.5); NaN never satisfies a condition. B is uint8 (rows x conditions)."""

    def __init__(self, X, cols, info, Fx, fit_rows, n_q=N_Q):
        self.cols, self.info = cols, info
        conds, mats = [], []
        for j, c in enumerate(cols):
            inf = info[c]
            if inf["kind"] == "na": continue
            x = X[:, j]
            if inf["kind"] == "onehot":
                s = Fx[inf["src"]].astype(object).map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else str(z))
                present = (s == inf["level"]).to_numpy() & s.notna().to_numpy()
                absent = (~(s == inf["level"]).to_numpy()) & s.notna().to_numpy()
                conds += [(j, "!=", 0.5), (j, "==", 0.5)]; mats += [absent, present]; continue
            xf = x[fit_rows]; xf = xf[~np.isnan(xf)]
            if len(xf) == 0: continue
            u = np.unique(xf)
            if len(u) <= 2 and set(np.round(u, 9).tolist()) <= {0.0, 1.0}:
                conds += [(j, "<=", 0.5), (j, ">", 0.5)]
                with np.errstate(invalid="ignore"): mats += [(x <= 0.5) & np.isfinite(x), (x > 0.5) & np.isfinite(x)]
                continue
            thr = np.unique(np.quantile(xf, np.linspace(0, 1, n_q + 2)[1:-1]))
            thr = [float(t) for t in thr if (xf <= t).any() and (xf > t).any()]
            for t in thr:
                with np.errstate(invalid="ignore"):
                    mats += [(x <= t) & np.isfinite(x), (x > t) & np.isfinite(x)]
                conds += [(j, "<=", t), (j, ">", t)]
        self.conds = conds
        self.B = np.stack(mats, axis=1).astype(np.uint8) if mats else np.zeros((len(X), 0), dtype=np.uint8)
        self.feature_of = np.array([c[0] for c in conds], dtype=int)
        self.complement = np.array([i + 1 if i % 2 == 0 else i - 1 for i in range(len(conds))], dtype=int)  # <= / > pairs

    def cond_json(self, i):
        j, op, t = self.conds[i]; c = self.cols[j]; inf = self.info[c]
        if inf["kind"] == "onehot": return [inf["src"], "==" if op == "==" else "!=", inf["level"]]
        return [c, op, round(float(t), 6)]


def rules_json(rule_conds, bank):
    """[(cond indices)] -> the grammar list; conditions on the same feature collapse to the tightest bound."""
    out = []
    for conds in rule_conds:
        cj = [bank.cond_json(i) for i in conds]
        out.append({"if": cj, "then": "skip"})
    return out


def rule_features(rules):
    return sorted({c[0] for r in rules for c in r["if"]})


def rules_keep(Fx, rules, tf):
    """The shipped semantics: tapes.rule_mask over the feature frame (default take)."""
    if not rules: return np.ones(len(Fx), dtype=bool)
    fires, mode = tapes.rule_mask(Fx, rules, tf)
    return ~fires if mode == "skip" else fires


def greedy_rules(bank, rows, v, mode, min_support, max_rules=MAX_RULES, max_depth=MAX_DEPTH, stop_gain=None):
    """Greedy conjunctive rule list over the bank's conditions on `rows`.
    mode 'fidelity': v = +1 (target skip) / -1 (target take) [weights allowed]; gain = covered sum of v; stop when gain <= 0.
    mode 'expectancy': v = winsorised net; gain = kept mean after skipping the covered rows minus the kept mean before; stop when
    gain < stop_gain (H5: 200 INR/trade) or a leaf floor would be broken (covered >= min_support, remaining kept >= min_support)."""
    B = bank.B[rows].astype(np.float32); n, m = B.shape
    alive = np.ones(n, dtype=bool); rules, trace = [], []
    vv = np.asarray(v, dtype=np.float32)
    for r in range(max_rules):
        S_rem, N_rem = float(vv[alive].sum()), int(alive.sum())
        def gains(mask):
            cov_sum = B.T @ (vv * mask); cov_n = B.T @ mask.astype(np.float32)
            if mode == "fidelity":
                g = cov_sum.copy(); ok = cov_n >= min_support
            else:
                rem_n = N_rem - cov_n
                with np.errstate(all="ignore"):
                    g = (S_rem - cov_sum) / np.maximum(rem_n, 1) - S_rem / max(N_rem, 1)
                ok = (cov_n >= min_support) & (rem_n >= min_support)
            g = np.where(ok, g, -np.inf); return g, cov_sum, cov_n
        g, cs, cn = gains(alive)
        if not np.isfinite(g).any(): break
        c1 = int(np.argmax(g)); best_g = float(g[c1]); conds = [c1]; mask = alive & (B[:, c1] > 0)
        for _ in range(max_depth - 1):
            g2, _, _ = gains(mask)
            g2[bank.feature_of == bank.feature_of[c1]] = g2[bank.feature_of == bank.feature_of[c1]]  # same-feature ranges allowed
            for c in conds: g2[c] = -np.inf; g2[bank.complement[c]] = -np.inf
            if not np.isfinite(g2).any(): break
            c2 = int(np.argmax(g2))
            if g2[c2] <= best_g + 1e-9: break
            conds.append(c2); best_g = float(g2[c2]); mask = mask & (B[:, c2] > 0)
        thr = 0.0 if stop_gain is None else stop_gain
        if mode == "fidelity" and best_g <= 0: break
        if mode == "expectancy" and best_g < thr: break
        rules.append(conds); trace.append(dict(rule=r + 1, depth=len(conds), gain=round(best_g, 3), covered=int(mask.sum())))
        alive &= ~mask
        if alive.sum() < min_support: break
    return rules, trace


# ---------------------------------------------------------------- the value-maximising policy tree (d)
def policy_tree(bank, rows, r, depth, min_leaf):
    """Greedy (depth 1 = exact) value-maximising tree over the bank's `<=` / `>` condition pairs. Returns the skip rules (condition
    index lists) and the tree value on `rows`. Rows falling out of both children (NaN) are taken by default."""
    B = bank.B[rows].astype(np.float32); rr = np.asarray(r, dtype=np.float32)
    left_idx = np.array([i for i in range(len(bank.conds)) if i % 2 == 0], dtype=int)   # the `<=` / `!=` half; complement = i + 1
    skip_rules, nodes = [], []

    def grow(mask, path, d):
        S = float(rr[mask].sum()); n = int(mask.sum())
        leaf_val = max(0.0, S)
        if d >= depth or n < 2 * min_leaf:
            if S <= 0 and n > 0: skip_rules.append(list(path))
            nodes.append(dict(path=[bank.cond_json(i) for i in path], n=n, sum=round(S, 1), take=S > 0)); return leaf_val
        m = mask.astype(np.float32)
        cs_l = B[:, left_idx].T @ (rr * m); cn_l = B[:, left_idx].T @ m
        cs_r = B[:, left_idx + 1].T @ (rr * m); cn_r = B[:, left_idx + 1].T @ m
        drop = S - cs_l - cs_r                                          # NaN rows: taken by default
        val = np.maximum(0, cs_l) + np.maximum(0, cs_r) + drop
        ok = (cn_l >= min_leaf) & (cn_r >= min_leaf)
        val = np.where(ok, val, -np.inf)
        if not np.isfinite(val).any() or val.max() <= leaf_val + 1e-6:
            if S <= 0 and n > 0: skip_rules.append(list(path))
            nodes.append(dict(path=[bank.cond_json(i) for i in path], n=n, sum=round(S, 1), take=S > 0)); return leaf_val
        k = int(np.argmax(val)); cl, cr = int(left_idx[k]), int(left_idx[k] + 1)
        vl = grow(mask & (B[:, cl] > 0), path + [cl], d + 1)
        vr = grow(mask & (B[:, cr] > 0), path + [cr], d + 1)
        return vl + vr + float(drop[k])

    value = grow(np.ones(len(rows), dtype=bool), [], 0)
    return skip_rules, value, nodes


def tree_to_rules(tree, cols, info, bank_like_round=6):
    """Skip rules (leaves predicting class 0 = skip) of a fitted sklearn DecisionTreeClassifier, in the grammar; rules with an
    inexpressible condition (missing indicator / =nan level) are dropped and counted."""
    t = tree.tree_; rules, dropped = [], 0
    def walk(node, path):
        nonlocal dropped
        if t.children_left[node] == -1:
            if np.argmax(t.value[node][0]) == 0 and len(path):
                cj = []
                for j, op, thr in path:
                    inf = info[cols[j]]
                    if inf["kind"] == "na": cj = None; break
                    if inf["kind"] == "onehot": cj.append([inf["src"], "!=" if op == "<=" else "==", inf["level"]])
                    else: cj.append([cols[j], op, round(float(thr), bank_like_round)])
                if cj is None: dropped += 1
                else: rules.append({"if": cj, "then": "skip"})
            return
        j, thr = int(t.feature[node]), float(t.threshold[node])
        walk(t.children_left[node], path + [(j, "<=", thr)]); walk(t.children_right[node], path + [(j, ">", thr)])
    walk(0, [])
    return rules, dropped


# ---------------------------------------------------------------- learners
class Learner:
    kind = "prob"          # prob | enet | score | policy
    grid = TAU_GRID
    needs_impute = False
    def fit(self, X, y, w, r, ctx): raise NotImplementedError
    def score(self, X): raise NotImplementedError


class BagLearner(Learner):
    needs_impute = True
    def __init__(self, depth=BAG_DEPTH_MAIN): self.depth = depth
    def fit(self, X, y, w, r, ctx):
        self.med = impute_fit(X)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.m = BaggingClassifier(DecisionTreeClassifier(max_depth=self.depth, min_weight_fraction_leaf=BAG_MIN_LEAF_FRAC),
                                       n_estimators=N_TREES, bootstrap=True, oob_score=True, max_samples=ctx.get("uniq", 1.0),
                                       n_jobs=N_JOBS, random_state=ctx.get("seed", 0)).fit(impute_apply(X, self.med), y, sample_weight=w)
        oob = self.m.oob_decision_function_[:, 1]
        self.oob = np.where(np.isnan(oob), np.nanmean(oob), oob)
        return self
    def score(self, X): return self.m.predict_proba(impute_apply(X, self.med))[:, 1]


class HGBCLearner(Learner):
    def __init__(self, interaction_cst=None, monotonic_cst=None): self.icst, self.mcst = interaction_cst, monotonic_cst
    def fit(self, X, y, w, r, ctx):
        self.m = HistGradientBoostingClassifier(**HGB, interaction_cst=self.icst, monotonic_cst=self.mcst).fit(X, y, sample_weight=w)
        return self
    def score(self, X): return self.m.predict_proba(X)[:, 1]


class HGBRLearner(Learner):
    kind = "enet"; grid = TAUR_GRID
    def __init__(self, interaction_cst=None, monotonic_cst=None): self.icst, self.mcst = interaction_cst, monotonic_cst
    def fit(self, X, y, w, r, ctx):
        lo, hi = np.quantile(r, [0.01, 0.99]); rw = np.clip(r, lo, hi)
        self.m = HistGradientBoostingRegressor(**HGB, interaction_cst=self.icst, monotonic_cst=self.mcst).fit(X, rw)
        return self
    def score(self, X): return self.m.predict(X)


class DT3Learner(Learner):
    needs_impute = True
    def __init__(self, min_leaf): self.min_leaf = min_leaf
    def fit(self, X, y, w, r, ctx):
        self.med = impute_fit(X)
        self.m = DecisionTreeClassifier(max_depth=3, min_samples_leaf=self.min_leaf, random_state=0).fit(impute_apply(X, self.med), y, sample_weight=w)
        return self
    def score(self, X): return self.m.predict_proba(impute_apply(X, self.med))[:, 1]


class ScorecardLearner(Learner):
    kind = "score"
    def __init__(self, max_feats): self.max_feats = max_feats
    def _bins(self, X, cols, info, fit_rows):
        self.edges, self.binary = {}, {}
        for j, c in enumerate(cols):
            x = X[fit_rows, j]; x = x[~np.isnan(x)]
            if len(x) == 0: continue
            u = np.unique(x)
            if len(u) <= 2 and set(np.round(u, 9).tolist()) <= {0.0, 1.0}: self.binary[j] = True; continue
            e = np.unique(np.quantile(x, np.linspace(0, 1, SC_BINS + 1)[1:-1]))
            if len(e) >= 1: self.edges[j] = e
    def _design(self, X):
        cols, names = [], []
        for j in sorted(self.binary):
            x = X[:, j]; cols.append(((x > 0.5) & np.isfinite(x)).astype(np.float32)); names.append((j, "bin", 1))
        for j, e in self.edges.items():
            x = X[:, j]; b = np.searchsorted(e, x, side="right"); b = np.where(np.isnan(x), -1, b)
            for k in range(len(e) + 1):
                cols.append((b == k).astype(np.float32)); names.append((j, "q", k))
        return (np.stack(cols, axis=1) if cols else np.zeros((len(X), 0), dtype=np.float32)), names
    def fit(self, X, y, w, r, ctx):
        self._bins(X, ctx["cols"], ctx["info"], np.arange(len(X)))
        Z, names = self._design(X)
        self.names = names
        feats_of = np.array([n[0] for n in names])
        chosen = None
        for C in SC_C_PATH:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = LogisticRegression(penalty="l1", C=C, solver="liblinear", max_iter=300, random_state=0).fit(Z, y, sample_weight=w)
            nz = np.abs(m.coef_[0]) > 1e-9
            n_src = len(set(feats_of[nz].tolist()))
            chosen = (C, m, n_src)
            if n_src <= self.max_feats: break
        self.C, self.m, self.n_src = chosen
        coef = self.m.coef_[0]; mx = np.abs(coef).max()
        self.points = np.round(coef * SC_SCALE / mx).astype(int) if mx > 0 else np.zeros(len(coef), dtype=int)
        self.selected = sorted(set(feats_of[self.points != 0].tolist()))
        return self
    def score(self, X):
        Z, _ = self._design(X); return Z @ self.points.astype(float)
    def to_json(self, cols, info):
        card = {"features": {}, "scale": SC_SCALE}
        for (j, kind, k), p in zip(self.names, self.points):
            if p == 0: continue
            c = cols[j]; inf = info[c]
            f = card["features"].setdefault(c, dict(kind=inf["kind"], src=inf.get("src", c), level=inf.get("level"), ext=inf.get("ext", False),
                                                    bins=None, points={}))
            if kind == "bin": f["points"]["present"] = int(p)
            else:
                f["bins"] = [round(float(e), 6) for e in self.edges[j]]; f["points"][str(k)] = int(p)
        return card


def scorecard_keep_from_json(Fx, card, s_min, X=None, cols=None):
    """Apply a frozen scorecard JSON to a feature frame (real tape or null tape): NaN / absent level = 0 points; keep iff score >= s_min.
    Returns (keep, score, missing_columns)."""
    n = len(Fx); score = np.zeros(n); missing = []
    for c, f in card["features"].items():
        if f["kind"] == "onehot":
            if f["src"] not in Fx.columns: missing.append(c); continue
            s = Fx[f["src"]].astype(object).map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else str(z))
            hit = (s == f["level"]).to_numpy() & s.notna().to_numpy()
            score += hit * f["points"].get("present", 0)
        else:
            if c in Fx.columns: x = pd.to_numeric(Fx[c], errors="coerce").to_numpy(dtype=float)
            elif X is not None and c in cols: x = X[:, cols.index(c)]
            else: missing.append(c); continue
            if f["bins"] is None: score += ((x > 0.5) & np.isfinite(x)) * f["points"].get("present", 0)
            else:
                b = np.searchsorted(np.array(f["bins"]), x, side="right"); b = np.where(np.isnan(x), -1, b)
                for k, p in f["points"].items(): score += (b == int(k)) * p
    return score >= s_min, score, missing


def platt(s, y, w):
    """1-D logistic map score -> p_win with the study weights (class-balanced), used for the scorecard's tau."""
    s = np.asarray(s, dtype=float).reshape(-1, 1)
    if len(np.unique(s)) < 2 or y.sum() == 0 or (~y).sum() == 0: return (0.0, 0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = LogisticRegression(C=1e6, solver="lbfgs", max_iter=500).fit(s, y, sample_weight=w)
    return (float(m.intercept_[0]), float(m.coef_[0][0]))


def sigmoid(z): return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


class PolicyLearner(Learner):
    """(d) policy trees and the H5 kept-expectancy rule list: decisions are the rule list itself."""
    kind = "policy"
    def __init__(self, form, depth=None, min_leaf=100):
        self.form, self.depth, self.min_leaf = form, depth, min_leaf
    def fit(self, X, y, w, r, ctx):
        bank = ctx["bank"]; rows = ctx["rows"]
        lo, hi = np.quantile(r, [0.01, 0.99]); rw = np.clip(r, lo, hi)
        if self.form == "ptree":
            conds, value, nodes = policy_tree(bank, rows, rw, self.depth, self.min_leaf)
            self.rules = rules_json(conds, bank); self.value, self.nodes = value, nodes; self.trace = None
        else:
            conds, trace = greedy_rules(bank, rows, rw, "expectancy", self.min_leaf, stop_gain=H5_STOP_GAIN)
            self.rules = rules_json(conds, bank); self.trace = trace; self.value = None; self.nodes = None
        return self
    def decide(self, Fx, tf): return rules_keep(Fx, self.rules, tf)


# ---------------------------------------------------------------- one split: fit, nest the threshold, decide
def fit_split(name, make, T, X, Fx, cols, info, tr, te, tf, ctx, decay=False):
    """Fit `make()` on tr, choose tau inside tr (inner CV / OOB / Platt), decide on te. Returns the split record."""
    Xn = X; y = T.win; net = T.net
    dec = decay_weights(T.setup_i[tr]) if decay else None
    w_tr, cap = make_weights(net[tr], y[tr], dec)
    rec = dict(name=name, n_tr=int(len(tr)), n_te=int(len(te)), cap=round(cap, 1))
    L = make()
    if L.kind == "policy":
        bank = CondBank(Xn, cols, info, Fx, tr)
        L.fit(Xn[tr], y[tr], w_tr, net[tr], dict(bank=bank, rows=tr, uniq=ctx.get("uniq", 1.0)))
        keep_all = L.decide(Fx, tf)
        rec.update(rules=L.rules, tau=None, keep_te=keep_all[te], keep_tr=keep_all[tr], score_te=None, value=L.value, trace=L.trace,
                   n_rules=len(L.rules))
        return rec
    lctx = dict(uniq=ctx.get("uniq", 1.0), cols=cols, info=info, seed=0)
    if isinstance(L, BagLearner):
        L.fit(Xn[tr], y[tr], w_tr, net[tr], lctx); inner = L.oob
    else:
        inner = np.full(len(tr), np.nan); pos = {i: k for k, i in enumerate(tr)}
        for tr_i, te_i in inner_groups(T, tr):
            w_i, _ = make_weights(net[tr_i], y[tr_i], decay_weights(T.setup_i[tr_i]) if decay else None)
            Li = make().fit(Xn[tr_i], y[tr_i], w_i, net[tr_i], lctx)
            inner[[pos[i] for i in te_i]] = Li.score(Xn[te_i])
        L.fit(Xn[tr], y[tr], w_tr, net[tr], lctx)
        if np.isnan(inner).any(): inner = np.where(np.isnan(inner), np.nanmean(inner), inner)
    s_te = L.score(Xn[te]); s_tr = L.score(Xn[tr])
    if L.kind == "score":
        a, b = platt(inner, y[tr], w_tr); rec["platt"] = (round(a, 4), round(b, 5))
        p_inner = sigmoid(a + b * inner); p_te = sigmoid(a + b * s_te); p_tr = sigmoid(a + b * s_tr)
        tau, table, satisfied = choose_tau(p_inner, net[tr], y[tr], TAU_GRID)
        s_min = (math.log(tau / (1 - tau)) - a) / b if b > 0 else -np.inf
        rec.update(score_min=round(float(s_min), 3), n_src=L.n_src, C=L.C, selected=[cols[j] for j in L.selected], card=L.to_json(cols, info))
        keep_te, keep_tr = p_te >= tau, p_tr >= tau
        rec.update(p_te=p_te, p_inner=p_inner, score_te=s_te)
    else:
        tau, table, satisfied = choose_tau(inner, net[tr], y[tr], L.grid)
        keep_te, keep_tr = s_te >= tau, inner >= tau
        rec.update(score_te=s_te, p_inner=inner)
    rec.update(tau=tau, tau_table=table, tau_constraint_satisfied=bool(satisfied), keep_te=keep_te, keep_tr=keep_tr, model=L)
    return rec


def distill(rec, X, Fx, cols, info, tr, te, tf, min_leaf):
    """Fit a depth-3 tree and a greedy rule list to the learner's inner decisions on tr; apply both to te (grammar semantics)."""
    target_skip = ~rec["keep_tr"]
    out = {}
    bank = CondBank(X, cols, info, Fx, tr)
    v = np.where(target_skip, 1.0, -1.0)
    conds, trace = greedy_rules(bank, tr, v, "fidelity", min_leaf)
    rules = rules_json(conds, bank)
    keep_all = rules_keep(Fx, rules, tf)
    out["rules"] = dict(rules=rules, n_rules=len(rules), trace=trace, keep_te=keep_all[te], keep_tr=keep_all[tr],
                        fidelity_tr=float((keep_all[tr] == rec["keep_tr"]).mean()))
    med = impute_fit(X[tr])
    dt = DecisionTreeClassifier(max_depth=3, min_samples_leaf=min_leaf, random_state=0).fit(impute_apply(X[tr], med), rec["keep_tr"].astype(int))
    trules, dropped = tree_to_rules(dt, cols, info)
    keep_t = rules_keep(Fx, trules, tf)
    out["tree"] = dict(rules=trules, n_rules=len(trules), dropped_inexpressible=dropped, keep_te=keep_t[te], keep_tr=keep_t[tr],
                       fidelity_tr=float((keep_t[tr] == rec["keep_tr"]).mean()))
    return out


def fidelity(keep_rule, keep_model):
    a = keep_rule == keep_model
    skip_m, skip_r = ~keep_model, ~keep_rule
    return dict(agreement=round(float(a.mean()), 4),
                skip_precision=round(float((skip_r & skip_m).sum() / max(skip_r.sum(), 1)), 4) if skip_r.any() else None,
                skip_recall=round(float((skip_r & skip_m).sum() / max(skip_m.sum(), 1)), 4) if skip_m.any() else None,
                model_skip_share=round(float(skip_m.mean()), 4), rule_skip_share=round(float(skip_r.mean()), 4))


# ---------------------------------------------------------------- diagnostics
def calibration(p, y, bins=10):
    p = np.asarray(p, dtype=float); y = np.asarray(y, dtype=float)
    base = y.mean(); bs = float(np.mean((p - y) ** 2)); bs0 = float(base * (1 - base))
    edges = np.linspace(0, 1, bins + 1); idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, bins - 1)
    rows, ece = [], 0.0
    for b in range(bins):
        m = idx == b
        if not m.any(): continue
        conf, acc = float(p[m].mean()), float(y[m].mean()); ece += abs(acc - conf) * m.sum() / len(p)
        rows.append(dict(bin=b, lo=round(edges[b], 2), hi=round(edges[b + 1], 2), n=int(m.sum()), mean_p=round(conf, 4), win_rate=round(acc, 4)))
    return dict(brier=round(bs, 5), brier_base=round(bs0, 5), brier_skill=round(1 - bs / bs0, 4) if bs0 > 0 else None, ece=round(ece, 4),
                mean_p=round(float(p.mean()), 4), base_rate=round(float(base), 4), reliability=rows)


def kept_share_by(T, keep, rows, key):
    F = T.F.iloc[rows]
    if key == "regime":
        g = np.where(F.n_choch_since_bos.to_numpy(dtype=float) >= 2, "choch>=2_since_bos", "choch<2_since_bos")
    else: g = F[key].astype(str).to_numpy()
    out = {}
    for lv in sorted(set(g.tolist())):
        m = g == lv; k = keep[rows][m]
        out[lv] = dict(n=int(m.sum()), kept_share=round(float(k.mean()), 4), kept_mean=round(float(T.net[rows][m][k].mean()), 1) if k.any() else None,
                       skipped_mean=round(float(T.net[rows][m][~k].mean()), 1) if (~k).any() else None)
    return out
