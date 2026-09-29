"""LLM hypotheses, round 1 = scoring of the 16 blind round-0 rules on IS (DESIGN_PANEL deep-sequence-llm-hypotheses, both judges'
fixes; REPAIR ROUND of 2026-09-29 after the adversarial refuters).

    python score_round0.py            # both timeframes, label L1 (primary) and L0 (robustness), IS only; every mask is a ledger row

What this script does, in order (definitions fixed before any number was looked at):
  0. registration   verifies that studies/llm_hypotheses/rules_round0.json still hashes to the registered sha256 (and that the copy
                    under ledger/registered/ is byte-identical); appends (never edits) a correcting line to ledger/registrations.jsonl
                    stating the true ordering of the artefacts (labelled tables existed from 02:49, the rules were hashed at 03:29;
                    blindness is the proposer's process claim, not a data-ordering fact). Idempotent: the line is written once.
  1. support        label-free: for every rule and every comparison, how many IS rows it fires on (features only, no label column is
                    read); the sess_range_atr / atr14 distributions behind the unit error of r0_m8 / r0_f8; the touch_swing_last counts
                    behind r0_m6. A rule with skipped_n <= 1 on the L1 IS table is "untestable (no IS support)": it is still scored
                    (its ledger row carries diff = None) and still counts in the family for max-T, Holm, PBO and SPA.
  2. rule mask      a rule fires when every comparison holds; a None / NaN in a rule column makes the comparison False, so the rule
                    does not fire and the SETUP is kept (a skip rule never fires on an undefined value). keep = not fired.
  3. scoring        harness.score(T, keep, "llm_hypotheses/round0", config, note="repair") for each rule on L1 and on L0, the union of
                    the 8 rules per timeframe (pre-registered in ROUND0.md: "every rule individually and the union"), and the design's
                    step-4 greedy combination (rules with Holm p < 0.05 and control pct >= 95, ordered by diff, stop when the marginal
                    diff < 200 INR/trade or the |net|-weighted winner recall falls): family "llm_hypotheses/round0_combo".
  4. multiplicity   max-T permutation across the 8 rules of a timeframe (net permuted across the IS rows, 2,000 draws, seeded; the
                    statistic is the two-sided Welch t of kept vs skipped, matching the sign convention of fz_report.permutation_p);
                    Westfall-Young step-down adjusted p per rule; Holm over the 16 rules of the round (m = 16, an untestable rule
                    enters with p = 1); harness.pbo (diff and kept_mean), harness.spa, harness.effective_trials over the 8 rule
                    vectors + the union per timeframe; harness.deflated_sharpe of each kept book with n_trials = 16 and the family's
                    Sharpe variance; harness.bootstrap_ci of each diff; per-block diff (12 harness blocks) and the two halves
                    (blocks 0-5 / 6-11) as the stability table. CPCV does not apply: a round-0 rule has no fitted threshold, so all
                    11 paths would be the rule itself; go_no_go therefore runs without the cpcv item and says so.
  5. outputs        round0_results.json (everything), round0_scores_<tf>.csv (one row per ledger row), round0_blocks_<tf>.csv,
                    support_<tf>.json, score_round0.log. FINDINGS.md / findings.json are written by write_findings.py from these.
"""
import os, sys, json, time, hashlib, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, OUT)
import numpy as np, pandas as pd
from scipy import stats as sst
import harness as H

RULES = os.path.join(HERE, "rules_round0.json")
REGISTERED_SHA = open(os.path.join(HERE, "rules_round0.sha256"), encoding="utf-8").read().split()[0]
REG_COPY = os.path.join(OUT, "ledger", "registered", f"rules_round0.{REGISTERED_SHA[:8]}.json")
REGISTRATIONS = os.path.join(OUT, "ledger", "registrations.jsonl")
FAMILY, FAMILY_COMBO = "llm_hypotheses/round0", "llm_hypotheses/round0_combo"
NOTE = "repair"
MAXT_DRAWS, HOLM_M, N_TRIALS_ROUND = 2000, 16, 16
COMBO_MIN_GAIN, COMBO_HOLM_ALPHA, COMBO_CONTROL_MIN = 200.0, 0.05, 95.0
TFS = ("minute", "5minute")
LOG = open(os.path.join(HERE, "score_round0.log"), "a", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- 0. registration check + correcting line (append-only)
def registration():
    sha = sha256(RULES)
    assert sha == REGISTERED_SHA, f"rules_round0.json hashes to {sha}, registered {REGISTERED_SHA}: the hashed file was changed"
    assert os.path.exists(REG_COPY) and sha256(REG_COPY) == sha, "ledger/registered copy missing or not byte-identical"
    lines = [json.loads(x) for x in open(REGISTRATIONS, encoding="utf-8") if x.strip()]
    if any(r.get("kind") == "correction" and r.get("corrects_sha256") == sha for r in lines):
        log("registration correction already present; not duplicated"); return sha, False
    def mt(p): return D.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")
    rules_written_at = json.load(open(RULES, encoding="utf-8"))["written_at"]
    rec = dict(kind="correction", corrects="pre_registration 'LLM hypotheses round 0 (blind)' registered 2026-09-29T03:51:33",
               corrects_sha256=sha, file="studies/llm_hypotheses/rules_round0.json", registered_at=D.datetime.now().isoformat(timespec="seconds"),
               false_claim="hashed before any labelled table of the program existed",
               true_ordering=dict(labelled_tables_built={"data/5minute/features.parquet (fnd_*, l1_* labels)": mt(os.path.join(OUT, "data", "5minute", "features.parquet")),
                                                         "data/minute/features.parquet": mt(os.path.join(OUT, "data", "minute", "features.parquet"))},
                                  labelled_aggregates_written={"results/pre_registration.json (raw book, frozen ST7/ST8 statistics)": mt(os.path.join(OUT, "results", "pre_registration.json")),
                                                               "ledger/trials.jsonl rows family comparator/frozen_st7_st8": "2026-09-29T03:02:06 .. 03:02:13"},
                                  rules_written_at=rules_written_at, rules_file_mtime=mt(RULES), first_registration="2026-09-29T03:51:33",
                                  llm_ledger_rows_before_registration=0),
               statement=("Labelled tables existed from 02:49, about 40 minutes before the rules were hashed. The proposer states that none of them "
                          "was opened (inputs_read = BRIEF.md first paragraph and H1-H5; data/README.md; FZ.md sections 7-9 and 19). Blindness is "
                          "therefore a process claim resting on the proposer's self-report and on the empty ledger (0 llm rows before registration), "
                          "not a verifiable data-ordering fact. Deviation from the judges' 'user's words + dictionary' rule: FZ.md section 19 was also "
                          "read; it prints ST7/ST8 priced nets, control percentiles and permutation p over the 2026 lab tape (= the OOS window) and "
                          "no Foundation outcome by read or hour, so no rule cell is visibly informed by it. The same wording goes into "
                          "studies/llm_hypotheses/FINDINGS.md and REPORT.md."),
               unit_error=("sess_range_atr is in ATR14 units and ATR14 on 1-minute bars is ~9 pts, so 'session range <= 2.5 ATR an hour in' (r0_m8) "
                           "and '<= 3.0 ATR' (r0_f8) are far below the observed range; the rules are untestable on IS (see support_<tf>.json). "
                           "The hashed rules are not re-thresholded; a corrected proposal would be a new round with its own sha and the multiplicity carried forward."),
               note=NOTE)
    with open(REGISTRATIONS, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")
    log("appended correcting registration line"); return sha, True


# ---------------------------------------------------------------- 2. rule masks
def comp_mask(F, col, op, val):
    s = F[col]
    if op == "in":
        return s.astype(object).isin(list(val)).to_numpy()
    if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
        x = s.to_numpy(dtype=float)
        with np.errstate(invalid="ignore"):
            return {">=": x >= val, ">": x > val, "<=": x <= val, "<": x < val, "==": x == val}[op]
    so = s.astype(object).to_numpy()
    def eq(z):
        if z is None or (isinstance(z, float) and np.isnan(z)): return False
        if isinstance(val, bool): return isinstance(z, (bool, np.bool_)) and bool(z) == val
        return z == val or str(z) == str(val)
    if op == "==": return np.array([eq(z) for z in so], dtype=bool)
    raise ValueError(f"operator {op} on non-numeric column {col}")


def rule_fires(F, rule):
    m = np.ones(len(F), dtype=bool)
    for col, op, val in rule["if"]: m &= comp_mask(F, col, op, val)
    return m


# ---------------------------------------------------------------- 1. label-free support
def support(T, T0, rules, tf):
    """Counts over features only. T = L1 table (4,452 / 826 IS units), T0 = L0 table (all traded IS SETUPs, 4,502 / 832)."""
    out = dict(tf=tf, is_units_L1=int(T.is_mask.sum()), is_setups_L0=int(T0.is_mask.sum()), rules={}, no_op_comparisons=[], distributions={})
    for T_, key in ((T, "L1"), (T0, "L0")):
        rows = np.flatnonzero(T_.is_mask); F = T_.F.iloc[rows]
        for r in rules:
            d = out["rules"].setdefault(r["id"], {})
            fires = rule_fires(F, r); d[f"fired_{key}"] = int(fires.sum())
            per = []
            for j, (col, op, val) in enumerate(r["if"]):
                alone = comp_mask(F, col, op, val)
                others = np.ones(len(F), dtype=bool)
                for jj, (c2, o2, v2) in enumerate(r["if"]):
                    if jj != j: others &= comp_mask(F, c2, o2, v2)
                excl = int((others & ~alone).sum())      # rows the comparison removes given the other comparisons hold
                per.append(dict(comparison=[col, op, val], holds_alone=int(alone.sum()), excludes_alone=int((~alone).sum()),
                                excludes_given_others=excl, rows_where_others_hold=int(others.sum()), na_rows=int(F[col].isna().sum())))
                if excl == 0 and others.sum() > 0 and key == "L1": out["no_op_comparisons"].append(dict(rule=r["id"], comparison=[col, op, val], rows_where_others_hold=int(others.sum())))
            d[f"comparisons_{key}"] = per
        if key == "L1":
            union = np.zeros(len(F), dtype=bool)
            for r in rules: union |= rule_fires(F, r)
            out["union_fired_L1"] = int(union.sum()); out["union_kept_L1"] = int((~union).sum())
    rows = np.flatnonzero(T.is_mask); F = T.F.iloc[rows]
    q = lambda s: {f"p{int(round(k * 100)):02d}": round(float(v), 3) for k, v in s.quantile([0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0]).items()}
    out["distributions"]["atr14_pts"] = q(F.atr14); out["distributions"]["sess_range_atr"] = q(F.sess_range_atr)
    out["distributions"]["sess_range_pts"] = q(F.sess_range_atr * F.atr14)
    hb = 60 if tf == "minute" else 12
    m = (F.session_bar >= hb) & (F.n_bos_today == 0)
    out["distributions"]["session_bar_ge_1h_and_no_bos_today"] = dict(rows=int(m.sum()), sess_range_atr_min=round(float(F.sess_range_atr[m].min()), 3) if m.any() else None,
                                                                       sess_range_atr_median=round(float(F.sess_range_atr[m].median()), 3) if m.any() else None,
                                                                       rows_le_2p5=int((F.sess_range_atr[m] <= 2.5).sum()), rows_le_3p0=int((F.sess_range_atr[m] <= 3.0).sum()),
                                                                       rows_le_6p0=int((F.sess_range_atr[m] <= 6.0).sum()), rows_le_10p0=int((F.sess_range_atr[m] <= 10.0).sum()))
    out["distributions"]["touch_swing_last"] = {str(k): int(v) for k, v in F.touch_swing_last.astype(object).value_counts(dropna=False).items()}
    out["distributions"]["fz_read"] = {str(k): int(v) for k, v in F.fz_read.astype(object).value_counts(dropna=False).items()}
    out["distributions"]["hv3_dir_agree"] = {str(k): int(v) for k, v in F.hv3_dir_agree.astype(object).value_counts(dropna=False).items()}
    return out


# ---------------------------------------------------------------- 4. multiplicity helpers
def welch_t(net, fires):
    """Two-sided Welch t of kept (not fired) vs skipped (fired) mean net; NaN when either side has < 2 rows."""
    k, s = net[~fires], net[fires]
    if len(k) < 2 or len(s) < 2: return np.nan
    return float((k.mean() - s.mean()) / np.sqrt(k.var(ddof=1) / len(k) + s.var(ddof=1) / len(s)))


def max_t(net, R, tag, draws=MAXT_DRAWS):
    """Westfall-Young max-T over the rules (rows of R = fired masks): permute net across rows, recompute every rule's |t|, take the
    max. Returns the observed t per rule, the family-wise p of the best rule and the step-down adjusted p per rule. Rules with an
    undefined t (skipped_n <= 1) are excluded from the max but keep their place in the family (adjusted p = 1)."""
    n = len(net); M = R.shape[0]
    obs = np.array([welch_t(net, R[j]) for j in range(M)])
    ok = np.isfinite(obs)
    rng = np.random.default_rng(int(hashlib.sha1(f"fz|llm_hypotheses|maxT|{tag}".encode()).hexdigest(), 16) % (2 ** 32))
    Rk = (~R[ok]).astype(float); Rs = R[ok].astype(float)
    nk, ns = Rk.sum(axis=1), Rs.sum(axis=1)
    T_perm = np.empty((draws, int(ok.sum())))
    for d in range(draws):
        p = net[rng.permutation(n)]
        sk, ss = Rk @ p, Rs @ p; qk, qs = Rk @ (p * p), Rs @ (p * p)
        mk, ms = sk / nk, ss / ns
        vk = (qk - nk * mk * mk) / (nk - 1); vs = (qs - ns * ms * ms) / (ns - 1)
        T_perm[d] = (mk - ms) / np.sqrt(vk / nk + vs / ns)
    A = np.abs(T_perm); a_obs = np.abs(obs[ok])
    best = int(np.argmax(a_obs)); fw_p = float((1 + (A.max(axis=1) >= a_obs[best] - 1e-12).sum()) / (1 + draws))
    # step-down: order rules by |t| descending; adjusted p_i = P(max over rules ranked i.. of |t*| >= |t_i|), monotone
    order = np.argsort(-a_obs); adj = np.empty(len(a_obs))
    prev = 0.0
    for i, j in enumerate(order):
        sub = A[:, order[i:]].max(axis=1)
        p = float((1 + (sub >= a_obs[j] - 1e-12).sum()) / (1 + draws)); prev = max(prev, p); adj[j] = prev
    adj_all = np.ones(M); adj_all[ok] = adj
    ids_ok = np.flatnonzero(ok)
    return dict(draws=draws, statistic="two-sided Welch t of kept vs skipped mean net, net permuted across IS rows",
                t_obs=[None if not np.isfinite(x) else round(float(x), 3) for x in obs], best_rule_index=int(ids_ok[best]),
                best_abs_t=round(float(a_obs[best]), 3), familywise_p_best=round(fw_p, 4),
                maxt_null_p95=round(float(np.quantile(A.max(axis=1), 0.95)), 3), adjusted_p=[round(float(x), 4) for x in adj_all],
                rules_in_family=M, rules_testable=int(ok.sum()))


def holm(p):
    p = np.asarray(p, dtype=float); m = len(p); order = np.argsort(p); out = np.empty(m); prev = 0.0
    for i, j in enumerate(order):
        v = min(1.0, (m - i) * p[j]); prev = max(prev, v); out[j] = prev
    return out


def block_table(T, fires, rows):
    bl = T.block[rows]; net = T.net[rows]; kp = ~fires[rows]
    d = {}
    for b in range(H.N_BLOCKS):
        m = bl == b
        d[f"b{b:02d}"] = round(float(net[m & kp].mean() - net[m & ~kp].mean()), 2) if (m & kp).sum() and (m & ~kp).sum() else None
    def half(bs):
        m = np.isin(bl, bs)
        return round(float(net[m & kp].mean() - net[m & ~kp].mean()), 2) if (m & kp).sum() and (m & ~kp).sum() else None
    d["half_0_5"] = half(range(0, 6)); d["half_6_11"] = half(range(6, 12))
    vals = [v for v in (d[f"b{b:02d}"] for b in range(H.N_BLOCKS)) if v is not None]
    d["blocks_defined"] = len(vals); d["blocks_positive"] = int(sum(v > 0 for v in vals))
    d["block_diff_p5"] = round(float(np.quantile(vals, 0.05)), 2) if vals else None; d["block_diff_min"] = round(float(min(vals)), 2) if vals else None
    return d


def kept_session_series(vec):
    with np.errstate(all="ignore"):
        km = np.where(vec["kept_n"] > 0, vec["kept_sum"] / np.maximum(vec["kept_n"], 1), np.nan)
    return km[np.isfinite(km)]


# ---------------------------------------------------------------- main
def run_tf(tf, rules_all, results):
    t0 = time.time()
    rules = rules_all[tf]
    T, T0 = H.load(tf), H.load(tf, "L0")
    log(f"[{tf}] L1 units {T.n} (IS {T.is_mask.sum()}), L0 {T0.n} (IS {T0.is_mask.sum()}); {len(rules)} round-0 rules")
    sup = support(T, T0, rules, tf)
    json.dump(sup, open(os.path.join(HERE, f"support_{tf}.json"), "w", encoding="utf-8"), indent=1)
    log(f"[{tf}] support (label-free): " + ", ".join(f"{r['id']} {sup['rules'][r['id']]['fired_L1']}" for r in rules) + f"; union {sup['union_fired_L1']}; no-op comparisons {len(sup['no_op_comparisons'])}")
    rows = np.flatnonzero(T.is_mask); rows0 = np.flatnonzero(T0.is_mask)
    R = np.stack([rule_fires(T.F, r) for r in rules])            # rules x all rows (IS + OOS; only IS rows are ever scored)
    R0 = np.stack([rule_fires(T0.F, r) for r in rules])
    per, vecs, ledger_ids = [], [], []
    for j, r in enumerate(rules):
        fires, fires0 = R[j], R0[j]
        ns = int(fires[rows].sum())
        untestable = ns <= 1
        cfg = dict(round=0, rule=r["id"], **{"if": r["if"]}, then="skip", sha256_rules=REGISTERED_SHA[:16])
        res = H.score(T, ~fires, FAMILY, cfg, script=__file__, note=NOTE)
        res0 = H.score(T0, ~fires0, FAMILY, cfg, script=__file__, note=NOTE)
        vec = H.session_vectors(T, ~fires, rows); vecs.append(vec); ledger_ids.append(res["id"])
        boot = H.bootstrap_ci(vec, tag=f"{tf}|{r['id']}") if not untestable else None
        blocks = block_table(T, fires, rows)
        log(f"[{tf}] {r['id']:6s} skipped {res['skipped_n']:5d} kept {res['kept_n']:5d} diff {res['diff']} ctrl {res['control_pct']} perm_p {res['perm_p']} "
            f"loserR {res['loser_recall']} winR(w) {res['winner_recall_weighted']} topdec_skipped {res['top_decile_winners_skipped']} | L0 diff {res0['diff']} ctrl {res0['control_pct']}"
            + ("  << UNTESTABLE (no IS support)" if untestable else ""))
        per.append(dict(id=r["id"], rule=r["if"], reason=r["reason"], expected=r["expected"], untestable=untestable,
                        support_note=(f"no IS support: skipped_n = {ns} on the L1 table ({sup['rules'][r['id']]['fired_L0']} of {sup['is_setups_L0']} IS SETUPs); no diff, control percentile or permutation p can be computed" if untestable else None),
                        L1=res, L0=res0, boot=boot, blocks=blocks))
    # union of the 8 rules (pre-registered)
    U, U0 = R.any(axis=0), R0.any(axis=0)
    cfg_u = dict(round=0, rule="union_all8", members=[r["id"] for r in rules], then="skip", sha256_rules=REGISTERED_SHA[:16])
    res_u = H.score(T, ~U, FAMILY, cfg_u, script=__file__, note=NOTE); res_u0 = H.score(T0, ~U0, FAMILY, cfg_u, script=__file__, note=NOTE)
    vec_u = H.session_vectors(T, ~U, rows); boot_u = H.bootstrap_ci(vec_u, tag=f"{tf}|union")
    log(f"[{tf}] union  skipped {res_u['skipped_n']} kept {res_u['kept_n']} diff {res_u['diff']} ctrl {res_u['control_pct']} perm_p {res_u['perm_p']} loserR {res_u['loser_recall']} winR(w) {res_u['winner_recall_weighted']} | L0 diff {res_u0['diff']} ctrl {res_u0['control_pct']}")
    # multiplicity
    mt = max_t(T.net[rows], R[:, rows], tag=f"{tf}|L1")
    fam_vecs = vecs + [vec_u]
    pbo_diff, pbo_km = H.pbo(fam_vecs, "diff"), H.pbo(fam_vecs, "kept_mean")
    spa_ = H.spa(fam_vecs, tag=f"{tf}|llm_round0"); eff = H.effective_trials(fam_vecs)
    srs = []
    for v in fam_vecs:
        x = kept_session_series(v); srs.append(float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan)
    sr_var = float(np.nanvar(np.array(srs), ddof=1)) if np.isfinite(srs).sum() > 1 else None
    dsrs = [H.deflated_sharpe(kept_session_series(v), N_TRIALS_ROUND, sr_var if sr_var and sr_var > 0 else None) for v in fam_vecs]
    log(f"[{tf}] max-T: best |t| {mt['best_abs_t']} (rule {rules[mt['best_rule_index']]['id']}), family-wise p {mt['familywise_p_best']}, null 95th pct of max|t| {mt['maxt_null_p95']}; PBO(diff) {pbo_diff['pbo']} PBO(kept_mean) {pbo_km['pbo']}; SPA p {spa_['spa_p']} (RC p {spa_['rc_p']}); effective trials {eff}")
    # go / no-go per rule and for the union (no cpcv item: a fixed rule has no fitted threshold)
    gng = {}
    for j, p in enumerate(per):
        ok, ch = H.go_no_go(p["L1"], tf, cpcv=None, pbo_value=pbo_diff["pbo"], dsr=dsrs[j], spa_p=spa_["spa_p"], boot=p["boot"]) if not p["untestable"] else (False, {"untestable": (False, "no IS support")})
        p["go_no_go"] = dict(passed=bool(ok), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, cpcv="not applicable: fixed rule, no fitted threshold"); p["dsr"] = dsrs[j]
        p["maxt_t"] = mt["t_obs"][j]; p["maxt_adjusted_p"] = mt["adjusted_p"][j]; gng[p["id"]] = bool(ok)
    ok_u, ch_u = H.go_no_go(res_u, tf, cpcv=None, pbo_value=pbo_diff["pbo"], dsr=dsrs[-1], spa_p=spa_["spa_p"], boot=boot_u)
    union = dict(L1=res_u, L0=res_u0, boot=boot_u, blocks=block_table(T, U, rows), dsr=dsrs[-1],
                 go_no_go=dict(passed=bool(ok_u), checks={k: [bool(v[0]), v[1]] for k, v in ch_u.items()}, cpcv="not applicable: fixed rule list, no fitted threshold"))
    log(f"[{tf}] go/no-go: " + ", ".join(f"{k} {'PASS' if v else 'fail'}" for k, v in gng.items()) + f", union {'PASS' if ok_u else 'fail'}")
    results["timeframes"][tf] = dict(n_is_L1=int(T.is_mask.sum()), n_is_L0=int(T0.is_mask.sum()), all_mean_L1=round(float(T.net[rows].mean()), 2), all_mean_L0=round(float(T0.net[rows0].mean()), 2),
                                     rules=per, union=union, max_t=mt, pbo_diff=pbo_diff, pbo_kept_mean=pbo_km, spa=spa_, effective_trials=eff,
                                     sharpe_family=[None if not np.isfinite(s) else round(s, 4) for s in srs], sharpe_var_family=sr_var,
                                     support=sup, runtime_s=round(time.time() - t0, 1))
    return T, R, per, res_u


def combination(tf, T, R, per, rules, results):
    """Design step 4 (pre-specified): rules with Holm p < 0.05 (m = 16 over the round) and control pct >= 95, greedily combined in
    order of diff; stop when the marginal diff < 200 INR/trade or the |net|-weighted winner recall falls. Every step is a ledger row."""
    rows = np.flatnonzero(T.is_mask)
    elig = [j for j, p in enumerate(per) if not p["untestable"] and p["holm_p_round"] < COMBO_HOLM_ALPHA and (p["L1"]["control_pct"] or 0) >= COMBO_CONTROL_MIN]
    out = dict(eligible=[per[j]["id"] for j in elig], steps=[], final=None,
               rule=f"Holm p (m={HOLM_M}) < {COMBO_HOLM_ALPHA} and control pct >= {COMBO_CONTROL_MIN}; greedy by diff; stop when marginal diff < {COMBO_MIN_GAIN} or |net|-weighted winner recall falls")
    if not elig:
        out["final"] = "no rule qualifies; no combination scored"; log(f"[{tf}] combination: no rule qualifies"); results["timeframes"][tf]["combination"] = out; return
    elig.sort(key=lambda j: -(per[j]["L1"]["diff"] or -1e9))
    chosen, cur, prev_res = [], np.zeros(T.n, dtype=bool), None
    for j in elig:
        cand = cur | R[j]; cfg = dict(round=0, rule="combo", members=[per[i]["id"] for i in chosen + [j]], then="skip", sha256_rules=REGISTERED_SHA[:16])
        res = H.score(T, ~cand, FAMILY_COMBO, cfg, script=__file__, note=NOTE)
        step = dict(added=per[j]["id"], id=res["id"], kept_n=res["kept_n"], diff=res["diff"], control_pct=res["control_pct"], winner_recall_weighted=res["winner_recall_weighted"])
        if prev_res is not None:
            marginal = (res["diff"] or 0) - (prev_res["diff"] or 0)
            step["marginal_diff"] = round(marginal, 2)
            if marginal < COMBO_MIN_GAIN or (res["winner_recall_weighted"] or 0) < (prev_res["winner_recall_weighted"] or 0):
                step["accepted"] = False; out["steps"].append(step); log(f"[{tf}] combination: stop before {per[j]['id']} (marginal {marginal:.1f})"); break
        step["accepted"] = True; out["steps"].append(step); chosen.append(j); cur = cand; prev_res = res
        log(f"[{tf}] combination: + {per[j]['id']} -> kept {res['kept_n']} diff {res['diff']} ctrl {res['control_pct']}")
    out["final"] = dict(members=[per[i]["id"] for i in chosen], ledger_id=prev_res["id"] if prev_res else None, L1=prev_res)
    results["timeframes"][tf]["combination"] = out


def main():
    t0 = time.time()
    log(f"=== score_round0.py {D.datetime.now().isoformat(timespec='seconds')} (repair round) ===")
    sha, appended = registration()
    rules_all = json.load(open(RULES, encoding="utf-8"))
    results = dict(study="llm_hypotheses", round_scored=0, scored_at=D.datetime.now().isoformat(timespec="seconds"), rules_sha256=sha,
                   registration_correction_appended=appended, ledger_sha_before=H.ledger_sha(), family=FAMILY, family_combo=FAMILY_COMBO, note=NOTE,
                   label_primary="L1", label_robustness="L0", split="IS", holm_m=HOLM_M, n_trials_round=N_TRIALS_ROUND, maxt_draws=MAXT_DRAWS, timeframes={})
    keep = {}
    for tf in TFS: keep[tf] = run_tf(tf, rules_all, results)
    # Holm over the 16 rules of the round (both timeframes; an untestable rule enters with p = 1)
    allp, index = [], []
    for tf in TFS:
        for j, p in enumerate(results["timeframes"][tf]["rules"]):
            pp = p["L1"]["perm_p"]; allp.append(1.0 if pp is None else float(pp)); index.append((tf, j))
    hp = holm(allp)
    for (tf, j), v in zip(index, hp): results["timeframes"][tf]["rules"][j]["holm_p_round"] = round(float(v), 4)
    results["holm"] = dict(m=HOLM_M, raw_p=[round(x, 4) for x in allp], holm_p=[round(float(x), 4) for x in hp], min_holm_p=round(float(hp.min()), 4),
                           rules=[f"{tf}:{results['timeframes'][tf]['rules'][j]['id']}" for tf, j in index])
    log(f"Holm over the {len(allp)} rules of round 0: min adjusted p {hp.min():.4f}")
    for tf in TFS:
        T, R, per, _ = keep[tf]; combination(tf, T, R, per, rules_all[tf], results)
    results["ledger_sha_after"] = H.ledger_sha()
    results["ledger_rows"] = dict(round0=len(H.read_ledger(FAMILY)), combo=len(H.read_ledger(FAMILY_COMBO)))
    results["null_result"] = not any(p["go_no_go"]["passed"] for tf in TFS for p in results["timeframes"][tf]["rules"]) and not any(results["timeframes"][tf]["union"]["go_no_go"]["passed"] for tf in TFS)
    results["runtime_s"] = round(time.time() - t0, 1)
    json.dump(results, open(os.path.join(HERE, "round0_results.json"), "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
    # flat CSVs
    keys = ["n", "kept_n", "skipped_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct", "loser_recall", "loser_precision",
            "winner_recall", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks", "kept_pf"]
    for tf in TFS:
        rows_ = []
        R_ = results["timeframes"][tf]
        for p in R_["rules"] + [dict(id="union_all8", untestable=False, L1=R_["union"]["L1"], L0=R_["union"]["L0"], boot=R_["union"]["boot"], holm_p_round=None, maxt_adjusted_p=None, go_no_go=R_["union"]["go_no_go"], blocks=R_["union"]["blocks"])]:
            for lab in ("L1", "L0"):
                r = dict(id=p["id"], label=lab, ledger_id=p[lab]["id"], untestable=p["untestable"], **{k: p[lab].get(k) for k in keys})
                if lab == "L1":
                    r.update(holm_p_round=p.get("holm_p_round"), maxt_adjusted_p=p.get("maxt_adjusted_p"), boot_diff_ci=p["boot"]["diff_ci"] if p["boot"] else None,
                             go_no_go=p["go_no_go"]["passed"], blocks_positive=p["blocks"]["blocks_positive"], blocks_defined=p["blocks"]["blocks_defined"], half_0_5=p["blocks"]["half_0_5"], half_6_11=p["blocks"]["half_6_11"])
                rows_.append(r)
        pd.DataFrame(rows_).to_csv(os.path.join(HERE, f"round0_scores_{tf}.csv"), index=False)
        pd.DataFrame([dict(id=p["id"], **p["blocks"]) for p in R_["rules"]] + [dict(id="union_all8", **R_["union"]["blocks"])]).to_csv(os.path.join(HERE, f"round0_blocks_{tf}.csv"), index=False)
    log(f"null_result {results['null_result']}; ledger rows {results['ledger_rows']}; ledger sha {results['ledger_sha_before']} -> {results['ledger_sha_after']}; done in {results['runtime_s']} s")


if __name__ == "__main__":
    main()
