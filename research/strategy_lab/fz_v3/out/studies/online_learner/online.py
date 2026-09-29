"""online.py - the walk-forward learn-after-each-trade take / skip policy of FZ v3 (BRIEF addendum 4, composed with rl.py per
addendum 6). Study `online_learner`. Pure, seeded, replayable:

    decisions, journal, states = online.run(T, cfg, rows)

processes the SETUPs `rows` (row indices into harness.Table T, strictly increasing setup_i; IS rows for the study, IS then OOS
when oos_once.py continues the same run) one at a time in time order and returns one decision dict per row
({take, lots, score, p_win, reason, state}), one journal row per row (BRIEF addendum 4 schema, section "Journal" below) and
the model-state id used at each row. Nothing is read ahead: at SETUP t the policy is fitted only on the outcomes of SETUPs whose
label exit bar is < t's bar (a heap keyed by exit bar, as rl.walk queues outcomes by exit time; the exit bar is read at push
time and the outcome at pop time, rl.py's convention), the running standardiser uses the features of the SETUPs processed
before t, and every random draw is one seeded standard-normal vector per SETUP (drawn whatever the decision, so the sequence
does not depend on the path: rl.LinTS.choose's rule).

Full information (rl.py: "once a SETUP's candles have played out, the outcome of EVERY feasible action ... is known"; BRIEF
addendum 4: the journal holds every SETUP, taken or skipped): the Foundation L1 trade of a skipped SETUP is observed too, so the
journal's training rows do not depend on the decisions. The fitted model sequence is therefore a function of (design, learner,
cadence, window, fit reward) only; explore, seed and a decision-side reward are "heads" over one fit sequence (run_heads), and
run() is run_heads with a single head. This is exact, not an approximation.

Definitions (fixed before any number was looked at)
  unit / label   a harness row: a Foundation SETUP taken under the L1 (15:25) book; net = l1_net_inr (lot 65, 5 pts slippage,
                 lab.trade_charges); exit = Foundation L1 (studies/exit_policy: no exit variant rescues the book; the exit is
                 not learned here; rl.py's exit / size bandit is not duplicated: the action is take / skip plus lots).
  design         "context" = hour_bin one-hot + dir one-hot (the EMPTY-SHORTLIST RULE: the frozen shortlist has 0 clusters on
                 both timeframes) + a bias column; "full" = every harness.Table.asof_columns() column except the calendar
                 proxies harness.TIME_PROXIES (`sl`, `n_events_asof`, refused at the candidate by go_no_go, so excluded from the
                 design from the start and reported, not silently dropped), encoded as harness.design does (numeric as is,
                 booleans 0/1, text one-hot over the levels present on the real table's IS rows, <= 16 levels), plus a missing
                 indicator `<col>__na` for every numeric column with a NaN on IS, standardised ONLINE per column with the
                 running mean / std of the PAST rows only (Welford; a row's z uses the rows processed before it; NaN -> 0 with
                 the indicator 1; |z| clipped at 5; a column with < 2 past values or zero spread -> 0), plus a bias column.
                 The encoded column list (`cfg["encoded"]`) is frozen from the real IS table so the same learner replays on a
                 null tape or on OOS rows (a level unseen on IS is all-zero). "full" is labelled "outside the frozen shortlist"
                 everywhere.
  cadence_k      the model is refitted when >= k closed outcomes are pending (k in {1, 10, 50}); pending outcomes wait.
  window         "anchored" = every closed outcome so far; N in {300, 1000} = the last N closed outcomes (exit order).
  reward         "net" = the L1 net; "pf" = net with losses x 1.5 (rl.py's `pf` reward). For the linear reward learner and the
                 boosted regressor the reward enters the FIT target; for the win-label learners (logistic, boosted classifier)
                 it enters the DECISION as L -> 1.5 L (the profit-factor surrogate on the loss side).
  learners       lints    Bayesian linear regression of the take reward on x (ridge prior precision 1.0, rl.LinTS's arm model;
                          skip = 0): A = ridge I + X'X, b = X'r over the window, mu = A^-1 b; the reward is rl.reward_of's
                          per-lot value: net / (LOT x BASE_STOP) clipped to +-CLIP (rl.py BASE_STOP 50, CLIP 10), x 1.5 when
                          negative under `pf`. Decision: take iff x . (mu + explore x chol(A^-1) z) > 0 (explore 0 = the
                          posterior mean; explore 0.3 = linear Thompson sampling).
                 logts    Bayesian logistic regression of the win label (Laplace approximation: MAP by Newton / IRLS with a
                          Gaussian prior of precision 1.0, warm-started from the previous fit, stop when max |step| < 1e-6 or
                          25 steps; H = ridge I + X' diag(p(1-p)) X). Decision: p = sigmoid(x . (w + explore x chol(H^-1) z));
                          take iff p W - (1 - p) L > 0 with W = the running mean net of the closed winners and L = the running
                          mean |net| of the closed losers (class-conditional means over every closed SETUP; L x 1.5 under `pf`;
                          before the first closed winner W := L).
                 hgb_reg  HistGradientBoostingRegressor (squared error, 100 iterations, learning rate 0.1, <= 15 leaves, min
                          leaf 50 (minute) / 20 (5minute), l2 1.0, no early stopping, seeded) refit every k closed outcomes on
                          the window's net winsorised at the window's own 1st / 99th percentiles (x 1.5 for losses under `pf`);
                          take iff the prediction > 0.
                 hgb_cls  the same booster as a classifier on the win label with sample weight |net| winsorised at the window's
                          99th percentile (mean 1) and class_weight balanced (the importance study's weighting); take iff
                          p >= tau, tau NESTED IN THE PAST: chosen at every refit on the record of the policy's own earlier
                          predictions (each made before its outcome was known, so an honest walk-forward sample) as the grid
                          value 0.05..0.95 (step 0.01) maximising the kept mean (penalised) net subject to kept share >= 20%
                          and kept n >= 50 of the record; fallback 0.5 while the record holds < 100 closed rows. One tau per
                          decision-side reward (the `net` head's on the record's net, the `pf` head's on the penalised net).
  warm-up        until 30 closed outcomes have been applied the policy takes every SETUP with 1 lot (the Foundation book is
                 the prior; `warmup_min_closed`, `warmup_policy` are cfg keys).
  sizing         lots in {0, 1, 2, 3} by half Kelly (fraction 0.5) on the calibrated p_win and the running W / L: for a bet
                 paying b = W / L to 1, f* = p - (1 - p) / b (Kelly 1956; MacLean, Thorp & Ziemba 2010), f = 0.5 f*, INR at
                 risk = f x capital, lots = clip(floor(f x capital / L), 0, max_lots = 3) with capital = 3 x futures_margin
                 120,000 + 60,000 buffer = 420,000 (strategy files; DESIGN_PANEL decision-making-5) and L (the running mean
                 loss) as one lot's risk; lots = 0 for a skip. p_win = the record-calibrated probability: the win rate of the
                 closed SETUPs whose model score fell in the same score decile as the current one (deciles of the record,
                 >= 100 closed rows and >= 20 in the bin, else the record's win rate, else 0.5). Daily loss stop: a cfg key,
                 value None (studies/session_stop: no session memory). The gate statistic (the ledger keep mask) is lots-free;
                 lots enter the journal's sized book only.
  journal        one row per SETUP: time, setup_i, session, dir, hour_bin, features (the context vector inline; the full
                 vector by row reference into features_full_<tf>.parquet plus its sha), n_closed (outcomes applied),
                 n_pending, decision, reason (which term won), score, p_model, p_win (calibrated), tau, W, L, kelly_f, lots,
                 state (model-state id: sha1 of the fitted parameters + update count; "prior:0" before the first refit), fill
                 (the SETUP close: the Foundation enters at the SETUP bar's close), exit_time, exit_reason, mfe_pts, mae_pts,
                 pts, gross, costs, net, R (= net / (stop distance x 65)), running equity / drawdown / rolling profit factor
                 (last 100 closed taken trades) of the 1-lot book and the sized book AS OF the decision (closed before this
                 bar), taken_net (net x lots when taken).
  determinism    the same cfg + seed reproduces decisions, journal and state ids bit for bit (asserted by the driver: run
                 twice, compare); truncation: the run on the rows before 2025-06-30 12:00, and the run on the truncated build
                 `data/<tf>/trunc_20250630_120000`, give the same decisions for every SETUP before the cut (asserted).
  threads        every BLAS / OpenMP pool is limited to one thread inside run_heads (threadpoolctl) so reductions are
                 bit-reproducible.
"""
import os, sys, json, math, heapq, hashlib, pickle
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
from threadpoolctl import threadpool_limits
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier   # imported here so that the OpenMP
                                                                                              # runtime is loaded before
                                                                                              # threadpool_limits(1) is entered

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
if OUT not in sys.path: sys.path.insert(0, OUT)
import harness as H                                                     # noqa: E402

LOT = 65
BASE_STOP = 50.0          # rl.py BASE_STOP: the reward unit is one lot's 50-point risk (LOT x 50 INR)
CLIP = 10.0               # rl.py CLIP: the per-lot reward is clipped to +-10 units
PF_LOSS_MULT = 1.5        # rl.py reward 'pf': losses x 1.5
FUTURES_MARGIN = 120000   # strategies/strategy_9.json capital.futures_margin
CAPITAL_INR = 3 * FUTURES_MARGIN + 60000   # DESIGN_PANEL decision-making-5: 3 lots of margin + 60,000 buffer
Z_CLIP = 5.0
CUT = "2025-06-30 12:00:00"
LEARNERS = ("lints", "logts", "hgb_reg", "hgb_cls")
DESIGNS = ("context", "full")

DEFAULTS = dict(
    design="context", learner="lints", cadence_k=1, window="anchored", reward="net", explore=0.0, seed=0, ridge=1.0,
    warmup_min_closed=30, warmup_policy="take",
    sizing=dict(rule="half_kelly", fraction=0.5, max_lots=3, capital_inr=CAPITAL_INR, risk_per_lot="running_mean_loss",
                p_win="record_calibrated_decile", daily_loss_stop=None),
    hgb=dict(max_iter=100, learning_rate=0.1, max_leaf_nodes=15, min_samples_leaf=50, l2_regularization=1.0),
    tau_rule=dict(grid=[0.05, 0.95, 0.01], objective="max kept mean of the record's (penalised) net", kept_share_min=0.2,
                  kept_n_min=50, min_record=100, fallback=0.5),
    calibration=dict(bins=10, min_record=100, min_bin=20),
    newton=dict(max_steps=25, tol=1e-6),
    reward_unit=dict(base_stop=BASE_STOP, clip=CLIP, pf_loss_mult=PF_LOSS_MULT),
    exit="foundation_L1", label="L1", lot=LOT, encoded=None, columns=None)


def _sha(b): return hashlib.sha1(b).hexdigest()[:16]


def with_defaults(cfg):
    out = json.loads(json.dumps(DEFAULTS))
    for k, v in cfg.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict): out[k] = dict(out[k], **v)
        else: out[k] = v
    if out["learner"] not in LEARNERS: raise ValueError(f"learner must be one of {LEARNERS}")
    if out["design"] not in DESIGNS: raise ValueError(f"design must be one of {DESIGNS}")
    if out["design"] == "full" and out["learner"].startswith("hgb"): raise ValueError("the HGB learners run on the context design only (task)")
    if out["reward"] not in ("net", "pf"): raise ValueError("reward must be net or pf")
    if out["window"] != "anchored" and not (isinstance(out["window"], int) and out["window"] > 0): raise ValueError("window: 'anchored' or a positive int")
    if not (isinstance(out["cadence_k"], int) and out["cadence_k"] >= 1): raise ValueError("cadence_k: a whole number >= 1")
    return out


# ---------------------------------------------------------------- the design (encoded column spec, frozen from the real IS rows)
def _clean(series):
    return series.astype(object).map(lambda z: None if z is None or (isinstance(z, float) and np.isnan(z)) else z)


def design_spec(T, design, rows=None):
    """The encoded columns of a design, from the rows `rows` (default: T's IS rows) of the real table: a list of
    {name, source, kind (num | bool | na | onehot), level}. harness.design's encoding, restricted to the levels present on the
    given rows and without the calendar proxies harness.TIME_PROXIES."""
    rows = np.flatnonzero(T.is_mask) if rows is None else np.asarray(rows)
    F = T.F.iloc[rows]
    cols = ["hour_bin", "dir"] if design == "context" else [c for c in T.asof_columns() if c not in H.TIME_PROXIES]
    spec = []
    for c in cols:
        s = F[c]
        if pd.api.types.is_bool_dtype(s) or pd.api.types.is_numeric_dtype(s):
            spec.append(dict(name=c, source=c, kind="num", level=None))
            if design == "full" and np.isnan(s.to_numpy(dtype=float)).any(): spec.append(dict(name=c + "__na", source=c, kind="na", level=None))
            continue
        vals = _clean(s)
        if all(isinstance(z, (bool, np.bool_)) or z is None for z in vals):
            spec.append(dict(name=c, source=c, kind="bool", level=None))
            if design == "full" and any(z is None for z in vals): spec.append(dict(name=c + "__na", source=c, kind="na", level=None))
            continue
        levels = sorted({str(z) for z in vals if z is not None})
        if len(levels) > H.MAX_LEVELS: continue
        for lv in levels: spec.append(dict(name=f"{c}={lv}", source=c, kind="onehot", level=lv))
    return spec


def encode(T, spec, rows):
    """The raw (un-standardised) matrix of a spec over rows: numeric as is (NaN kept), bool 0/1/NaN, `__na` = isnan(source),
    one-hot 0/1 (a level absent from the table is all-zero, a source column absent is NaN / 0)."""
    F = T.F.iloc[np.asarray(rows)]
    X = np.zeros((len(F), len(spec)), dtype=float); cache = {}
    for j, e in enumerate(spec):
        c = e["source"]
        if c not in F.columns:
            X[:, j] = np.nan if e["kind"] in ("num", "bool") else 0.0
            continue
        if e["kind"] == "num": X[:, j] = F[c].to_numpy(dtype=float)
        elif e["kind"] == "bool": X[:, j] = _clean(F[c]).map(lambda z: np.nan if z is None else float(z)).to_numpy(dtype=float)
        elif e["kind"] == "na":
            s = F[c]
            X[:, j] = np.isnan(s.to_numpy(dtype=float)).astype(float) if (pd.api.types.is_bool_dtype(s) or pd.api.types.is_numeric_dtype(s)) \
                else _clean(s).map(lambda z: 1.0 if z is None else 0.0).to_numpy(dtype=float)
        else:
            if c not in cache: cache[c] = _clean(F[c]).map(lambda z: None if z is None else str(z))
            X[:, j] = (cache[c] == e["level"]).to_numpy().astype(float)
    return X


class Standardiser:
    """Running per-column mean / std (Welford) over the rows processed so far; z of a new row uses the past rows only."""

    def __init__(self, d, cols):
        self.n = np.zeros(d); self.mean = np.zeros(d); self.m2 = np.zeros(d); self.cols = np.asarray(cols, dtype=int)

    def transform(self, x):
        z = x.copy()
        c = self.cols
        v = x[c]; miss = np.isnan(v)
        n = self.n[c]; sd = np.sqrt(np.where(n > 1, self.m2[c] / np.maximum(n - 1, 1), 0.0))
        ok = (n >= 2) & (sd > 1e-12) & ~miss
        out = np.zeros(len(c))
        out[ok] = np.clip((v[ok] - self.mean[c][ok]) / sd[ok], -Z_CLIP, Z_CLIP)
        z[c] = out
        return z

    def update(self, x):
        c = self.cols; v = x[c]; ok = ~np.isnan(v)
        idx = c[ok]; val = v[ok]
        self.n[idx] += 1
        delta = val - self.mean[idx]
        self.mean[idx] += delta / self.n[idx]
        self.m2[idx] += delta * (val - self.mean[idx])


# ---------------------------------------------------------------- rewards, sizing, calibration
def fit_reward(net, reward, ru):
    """rl.reward_of's per-lot value for one lot: net / (LOT x BASE_STOP) clipped to +-CLIP, losses x 1.5 under `pf`
    (vectorised over an array of nets)."""
    v = np.clip(np.asarray(net, dtype=float) / (LOT * ru["base_stop"]), -ru["clip"], ru["clip"])
    return np.where(v < 0, v * ru["pf_loss_mult"], v) if reward == "pf" else v


def penalised_net(net, reward, ru):
    return net * ru["pf_loss_mult"] if (reward == "pf" and net < 0) else net


def kelly_lots(p, W, L, sz):
    """Half-Kelly lots for a bet paying b = W / L to 1: f* = p - (1 - p) / b, f = fraction x f*, lots = clip(floor(f x capital / L), 0, max)."""
    if W is None and L is None: return 1, None
    if W is None: W = L
    if L is None or L <= 0: L = W
    if W <= 0 or L <= 0: return 0, 0.0
    b = W / L
    f_star = p - (1.0 - p) / b
    f = sz["fraction"] * f_star
    lots = int(np.clip(math.floor(f * sz["capital_inr"] / L), 0, sz["max_lots"])) if f > 0 else 0
    return lots, float(f)


class Record:
    """The walk-forward record of (score at decision time, net, win) of the closed SETUPs: calibration and the nested tau."""

    def __init__(self, cal, tau_rule):
        self.scores, self.nets, self.wins = [], [], []
        self.cal, self.tau_rule = cal, tau_rule
        self.n_win = 0; self.sum_win = 0.0; self.n_loss = 0; self.sum_loss = 0.0

    def add(self, score, net):
        self.scores.append(score); self.nets.append(net); self.wins.append(net > 0)
        if net > 0: self.n_win += 1; self.sum_win += net
        else: self.n_loss += 1; self.sum_loss += -net

    def W(self): return self.sum_win / self.n_win if self.n_win else None

    def L(self): return self.sum_loss / self.n_loss if self.n_loss else None

    def p_cal(self, score):
        n = len(self.scores)
        if n == 0 or score is None or not np.isfinite(score): return 0.5
        base = float(np.mean(self.wins))
        if n < self.cal["min_record"]: return base
        s = np.asarray(self.scores); w = np.asarray(self.wins, dtype=float)
        edges = np.quantile(s, np.linspace(0, 1, self.cal["bins"] + 1)[1:-1])
        b = int(np.searchsorted(edges, score, side="right")); bins = np.searchsorted(edges, s, side="right")
        m = bins == b
        return float(w[m].mean()) if m.sum() >= self.cal["min_bin"] else base

    def tau(self, reward, ru):
        r = self.tau_rule
        if len(self.scores) < r["min_record"]: return r["fallback"], "fallback"
        s = np.asarray(self.scores); pn = np.asarray([penalised_net(v, reward, ru) for v in self.nets])
        g0, g1, st = r["grid"]; grid = np.round(np.arange(g0, g1 + st / 2, st), 4)
        best, best_v = None, -np.inf
        for t in grid:
            k = s >= t
            if k.sum() < r["kept_n_min"] or k.mean() < r["kept_share_min"]: continue
            v = float(pn[k].mean())
            if v > best_v: best, best_v = float(t), v
        return (best, "record") if best is not None else (r["fallback"], "fallback")


# ---------------------------------------------------------------- learners (one fit sequence; heads decide)
def _sigmoid(a): return 1.0 / (1.0 + np.exp(-np.clip(a, -35, 35)))


class LinTS:
    """rl.LinTS's arm model for the single arm `take` (skip = 0), refitted from the window."""

    def __init__(self, d, ridge):
        self.d, self.ridge = d, ridge
        self.A = np.eye(d) * ridge; self.b = np.zeros(d); self.mu = np.zeros(d); self.chol = np.linalg.cholesky(np.eye(d) / ridge); self.n = 0

    def refit(self, X, r, y, w):
        """Recompute A, b from the window (the rolling windows)."""
        self.set_sums(np.eye(self.d) * self.ridge + X.T @ X, X.T @ r, len(r))

    def set_sums(self, A, b, n):
        """A = ridge I + sum x x', b = sum r x (the anchored window accumulates them exactly, one batch of closed outcomes at
        a time, instead of recomputing X'X over every closed row at every refit: the same estimator, O(d^2) per outcome)."""
        self.A = A; self.b = b
        self.mu = np.linalg.solve(self.A, self.b)
        Ainv = np.linalg.inv(self.A); Ainv = (Ainv + Ainv.T) / 2
        self.chol = np.linalg.cholesky(Ainv + 1e-12 * np.eye(self.d)); self.n = n

    def score(self, x): return float(x @ self.mu)

    def decide(self, x, score, head, z, W, L, ru):
        if head["explore"] > 0:
            v = float(x @ (self.mu + head["explore"] * (self.chol @ z)))
            return v > 0, ("TS sample > 0" if v > 0 else "TS sample <= 0"), v
        return score > 0, ("posterior mean > 0" if score > 0 else "posterior mean <= 0"), score

    def state_id(self, n_applied): return _sha(self.A.tobytes() + self.b.tobytes() + str(n_applied).encode())


class LogTS:
    """Bayesian logistic regression (Laplace) of the win label; decision by expected net p W - (1 - p) L."""

    def __init__(self, d, ridge, newton):
        self.d, self.ridge, self.newton = d, ridge, newton
        self.w = np.zeros(d); self.chol = np.linalg.cholesky(np.eye(d) / ridge); self.n = 0; self.steps = 0

    def refit(self, X, r, y, w):
        wv = self.w.copy(); ridge = self.ridge; I = np.eye(self.d)
        for it in range(self.newton["max_steps"]):
            p = _sigmoid(X @ wv)
            g = X.T @ (p - y) + ridge * wv
            Hm = (X * (p * (1 - p))[:, None]).T @ X + ridge * I
            step = np.linalg.solve(Hm, g)
            wv = wv - step
            self.steps = it + 1
            if np.max(np.abs(step)) < self.newton["tol"]: break
        p = _sigmoid(X @ wv)
        Hm = (X * (p * (1 - p))[:, None]).T @ X + ridge * I
        Hinv = np.linalg.inv(Hm); Hinv = (Hinv + Hinv.T) / 2
        self.w = wv; self.chol = np.linalg.cholesky(Hinv + 1e-12 * I); self.n = len(y)

    def score(self, x): return float(_sigmoid(x @ self.w))

    def decide(self, x, score, head, z, W, L, ru):
        p = float(_sigmoid(x @ (self.w + head["explore"] * (self.chol @ z)))) if head["explore"] > 0 else score
        if W is None and L is None: return True, "no closed outcome with a sign yet: take", None
        Wv = W if W is not None else L; Lv = L if L is not None else Wv
        Lp = Lv * ru["pf_loss_mult"] if head["reward"] == "pf" else Lv
        e = p * Wv - (1 - p) * Lp
        return e > 0, ("pW-(1-p)L > 0" if e > 0 else "pW-(1-p)L <= 0"), float(e)

    def state_id(self, n_applied): return _sha(self.w.tobytes() + str(n_applied).encode())


class HGB:
    """HistGradientBoosting regressor (winsorised net) or classifier (win label, |net| weights, nested tau)."""

    def __init__(self, kind, params, seed, reward, ru, tau_rule):
        self.kind, self.params, self.seed, self.reward, self.ru = kind, dict(params), seed, reward, ru
        self.model = None; self.n = 0; self._sid = None
        # the classifier's nested tau, one per decision-side reward (the `pf` head chooses tau on the record's penalised net,
        # the `net` head on the net: the reward enters the DECISION for the win-label learners)
        self.taus = {r: (tau_rule["fallback"], "fallback") for r in ("net", "pf")}

    def refit(self, X, r, y, w, record=None):
        P = dict(self.params, early_stopping=False, random_state=self.seed)
        if self.kind == "reg":
            lo, hi = np.quantile(r, [0.01, 0.99])
            t = np.clip(r, lo, hi)
            if self.reward == "pf": t = np.where(t < 0, t * self.ru["pf_loss_mult"], t)
            self.model = HistGradientBoostingRegressor(loss="squared_error", **P).fit(X, t)
        else:
            a = np.abs(r); cap = np.quantile(a, 0.99); sw = np.minimum(a, cap); sw = sw / sw.mean() if sw.mean() > 0 else np.ones_like(sw)
            if y.min() == y.max():
                self.model = None; self.const = float(y[0])
            else:
                self.model = HistGradientBoostingClassifier(class_weight="balanced", **P).fit(X, y.astype(int), sample_weight=sw)
            if record is not None: self.taus = {rw: record.tau(rw, self.ru) for rw in ("net", "pf")}
        self.n = len(r); self._sid = _sha(pickle.dumps(self.model) + str(self.n).encode())

    def tau_for(self, head_reward):
        return self.taus[head_reward if head_reward in self.taus else "net"]

    def score(self, x):
        if self.model is None: return 0.0 if self.kind == "reg" else getattr(self, "const", 0.5)
        if self.kind == "reg": return float(self.model.predict(x[None, :])[0])
        return float(self.model.predict_proba(x[None, :])[0, 1])

    def decide(self, x, score, head, z, W, L, ru):
        if self.kind == "reg": return score > 0, ("E[net] > 0" if score > 0 else "E[net] <= 0"), score
        tau, src = self.tau_for(head["reward"])
        return score >= tau, (f"p >= tau ({src}, {head['reward']})" if score >= tau else f"p < tau ({src}, {head['reward']})"), score

    def state_id(self, n_applied): return self._sid or "prior:0"


def make_learner(cfg, d):
    if cfg["learner"] == "lints": return LinTS(d, cfg["ridge"])
    if cfg["learner"] == "logts": return LogTS(d, cfg["ridge"], cfg["newton"])
    return HGB("reg" if cfg["learner"] == "hgb_reg" else "cls", cfg["hgb"], cfg["seed"], cfg["reward"], cfg["reward_unit"], cfg["tau_rule"])


# ---------------------------------------------------------------- the walk
def run_heads(T, cfg, rows, heads, features_out=None):
    """One fit sequence, several decision heads. heads: list of {explore, seed, reward}. Returns {head index: dict(decisions,
    journal, states)}; features_out (list) receives the standardised feature vector of every row when given."""
    cfg = with_defaults(cfg)
    rows = np.asarray(rows, dtype=int)
    if len(rows) > 1 and not (np.diff(T.setup_i[rows]) > 0).all(): raise ValueError("rows must be strictly increasing in setup_i (time order)")
    spec = cfg["encoded"] if cfg.get("encoded") else design_spec(T, cfg["design"])
    with threadpool_limits(limits=1):
        return _walk(T, cfg, rows, heads, spec, features_out)


def _walk(T, cfg, rows, heads, spec, features_out):
    F = T.F
    Xraw = encode(T, spec, rows)
    kinds = [e["kind"] for e in spec]
    std_cols = [j for j, k in enumerate(kinds) if cfg["design"] == "full" and k in ("num", "bool")]
    d = len(spec) + 1
    std = Standardiser(len(spec), std_cols)
    ru, sz, k_cad, win = cfg["reward_unit"], cfg["sizing"], cfg["cadence_k"], cfg["window"]
    learner = make_learner(cfg, d)
    record = Record(cfg["calibration"], cfg["tau_rule"])
    setup_i = T.setup_i[rows]; exit_bar = T.exit_bar[rows]; net_all = T.net[rows]
    col = lambda c: F[c].iloc[rows].to_numpy() if c in F.columns else np.array([None] * len(rows))
    time_ = col("time").astype(str); dir_ = col("dir").astype(str); hb = col("hour_bin").astype(str); ses = T.session[rows]
    fill = col("close"); sl_dist = col("sl_dist_pts"); x_time = col("l1_exit_time"); x_reason = col("l1_exit_reason")
    mfe = col("l1_mfe_pts"); mae = col("l1_mae_pts"); pts = col("l1_pts"); gross = col("l1_gross_inr"); cost = col("l1_cost_inr")
    n = len(rows)
    Xs = np.zeros((n, d)); scores = np.full(n, np.nan)
    queue, pending, closed = [], [], []                    # closed = indices (into rows) of every closed outcome in exit order
    n_applied = 0; state_id = "prior:0"
    A_acc = np.eye(d) * cfg["ridge"]; b_acc = np.zeros(d)   # the anchored lints sums (exact accumulation)
    hs = []
    for h in heads:
        hs.append(dict(rng=np.random.RandomState(int(h["seed"])), explore=float(h["explore"]), reward=h.get("reward", cfg["reward"]),
                       book=[], eq1=0.0, eqs=0.0, pk1=0.0, pks=0.0, last100=[], n_taken_closed=0, today=None, today_net=0.0,
                       decisions=[], journal=[], states=[]))
    for i in range(n):
        k = int(setup_i[i])
        # 1. outcomes whose exit bar is before this bar become known (rl.walk: the queue is popped by exit time)
        while queue and queue[0][0] < k:
            _, j = heapq.heappop(queue)
            record.add(scores[j], float(net_all[j])); closed.append(j); pending.append(j)
            if len(pending) >= k_cad:
                sel = closed if win == "anchored" else closed[-int(win):]
                if cfg["learner"] == "lints" and win == "anchored":
                    Xp = Xs[pending]; rp = fit_reward(net_all[pending], cfg["reward"], ru)
                    A_acc = A_acc + Xp.T @ Xp; b_acc = b_acc + Xp.T @ rp
                    learner.set_sums(A_acc, b_acc, len(closed))
                else:
                    Xw = Xs[sel]; nets = net_all[sel].astype(float)
                    y = (nets > 0).astype(float)
                    if isinstance(learner, HGB): learner.refit(Xw, nets, y, None, record=record)
                    elif cfg["learner"] == "lints": learner.refit(Xw, fit_reward(nets, cfg["reward"], ru), y, None)
                    else: learner.refit(Xw, nets, y, None)
                n_applied += len(pending); pending = []
                state_id = learner.state_id(n_applied)
        for h in hs:
            while h["book"] and h["book"][0][0] < k:
                _, j, lots = heapq.heappop(h["book"])
                nv = float(net_all[j]); h["eq1"] += nv; h["eqs"] += nv * lots
                h["pk1"] = max(h["pk1"], h["eq1"]); h["pks"] = max(h["pks"], h["eqs"])
                h["last100"].append(nv); h["last100"] = h["last100"][-100:]; h["n_taken_closed"] += 1
                day = str(time_[j])[:10]
                if h["today"] != str(time_[i])[:10]: h["today"], h["today_net"] = str(time_[i])[:10], 0.0
                if day == h["today"]: h["today_net"] += nv * lots
        # 2. the feature vector (past-only standardisation), the model score, the calibrated p_win
        x = np.append(std.transform(Xraw[i]), 1.0); Xs[i] = x
        if features_out is not None: features_out.append(x)
        sc = learner.score(x); scores[i] = sc
        p_cal = record.p_cal(sc); W, L = record.W(), record.L()
        warm = n_applied < cfg["warmup_min_closed"]
        # 3. every head decides (one normal vector per head per SETUP, drawn whatever happens)
        for h in hs:
            z = h["rng"].standard_normal(d)
            if h["today"] != str(time_[i])[:10]: h["today"], h["today_net"] = str(time_[i])[:10], 0.0
            if warm:
                take, reason, val = (cfg["warmup_policy"] == "take"), f"warm-up (< {cfg['warmup_min_closed']} closed): {cfg['warmup_policy']}-all", None
                lots, f = (1, None) if take else (0, None)
            else:
                take, reason, val = learner.decide(x, sc, h, z, W, L, ru)
                if take and sz.get("daily_loss_stop") is not None and h["today_net"] <= -float(sz["daily_loss_stop"]):
                    take, reason = False, f"daily loss stop {sz['daily_loss_stop']}"
                lots, f = kelly_lots(p_cal, W, L, sz) if take else (0, None)
            tau = learner.tau_for(h["reward"])[0] if isinstance(learner, HGB) and learner.kind == "cls" else None
            wl = [] if h["last100"] == [] else h["last100"]
            gw = sum(v for v in wl if v > 0); gl = -sum(v for v in wl if v <= 0)
            pf100 = round(gw / gl, 3) if gl > 0 else None
            nv = float(net_all[i])
            R = nv / (float(sl_dist[i]) * LOT) if sl_dist[i] is not None and np.isfinite(float(sl_dist[i])) and float(sl_dist[i]) > 0 else None
            feat = json.dumps([round(float(v), 6) for v in x]) if cfg["design"] == "context" else f"ref:{i}|sha:{_sha(x.tobytes())}"
            h["decisions"].append(dict(take=bool(take), lots=int(lots), score=None if sc is None else round(float(sc), 6), p_win=round(float(p_cal), 4),
                                       reason=reason, state=state_id))
            h["states"].append(state_id)
            h["journal"].append(dict(
                time=str(time_[i]), setup_i=k, session_idx=int(ses[i]), dir=str(dir_[i]), hour_bin=str(hb[i]), features=feat,
                n_closed=int(n_applied), n_pending=int(len(pending)), decision="take" if take else "skip", reason=reason,
                score=round(float(sc), 6), value=None if val is None else round(float(val), 6),
                p_model=round(float(sc), 6) if cfg["learner"] in ("logts", "hgb_cls") else None, p_win=round(float(p_cal), 4), tau=tau,
                W=None if W is None else round(W, 2), L=None if L is None else round(L, 2), kelly_f=None if f is None else round(f, 5), lots=int(lots),
                state=state_id, fill=None if fill[i] is None else float(fill[i]), exit_time=None if x_time[i] is None else str(x_time[i]),
                exit_reason=None if x_reason[i] is None else str(x_reason[i]), mfe_pts=_f(mfe[i]), mae_pts=_f(mae[i]), pts=_f(pts[i]),
                gross=_f(gross[i]), costs=_f(cost[i]), net=round(nv, 2), R=None if R is None else round(R, 4),
                equity_1lot=round(h["eq1"], 2), drawdown_1lot=round(h["eq1"] - h["pk1"], 2), equity_sized=round(h["eqs"], 2),
                drawdown_sized=round(h["eqs"] - h["pks"], 2), rolling_pf100=pf100, n_taken_closed=int(h["n_taken_closed"]),
                taken_net=round(nv * lots, 2) if take else 0.0))
            if take: heapq.heappush(h["book"], (int(exit_bar[i]), i, int(lots)))
        # 4. this SETUP's outcome joins the queue (known at its exit bar); the standardiser learns this row's features
        heapq.heappush(queue, (int(exit_bar[i]), i))
        std.update(Xraw[i])
    return {hi: dict(decisions=h["decisions"], journal=h["journal"], states=h["states"]) for hi, h in enumerate(hs)}


def _f(v):
    try:
        v = float(v)
        return None if not np.isfinite(v) else round(v, 4)
    except (TypeError, ValueError): return None


def run(T, cfg, rows):
    """The pure, seeded, replayable single-policy run: (decisions, journal rows, model-state ids) for `rows` in time order.
    cfg carries explore / seed / reward (one head)."""
    c = with_defaults(cfg)
    out = run_heads(T, c, rows, [dict(explore=c["explore"], seed=c["seed"], reward=c["reward"])])[0]
    return out["decisions"], out["journal"], out["states"]


def journal_sha(journal):
    return hashlib.sha1(json.dumps(journal, sort_keys=True, default=str).encode()).hexdigest()


def load_table(folder, tf, label="L1"):
    """harness.load for another build folder (the truncated build, a null tape): the L1 units as a harness.Table."""
    F = pd.read_parquet(os.path.join(folder, "features.parquet"))
    TR = pd.read_parquet(os.path.join(folder, "trades.parquet")).set_index("entry_i")
    S = pd.read_parquet(os.path.join(folder, "sessions.parquet"))
    F = F[F.traded.astype(bool)]
    if label == "L1": F = F[F.l1_taken.astype(bool)]
    F = F.sort_values("setup_i").reset_index(drop=True)
    TR = TR.loc[F.setup_i.to_numpy()].reset_index()
    return H.Table(tf, label, F, TR, S)
