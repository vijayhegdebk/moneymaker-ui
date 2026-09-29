"""llm_round1 step 3: score the round-1 rule lists cross-fitted, through the harness (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1:
tables of one half, scored on the other, the cells shown logged as the family size for the max-T; Judge 2: the harness splitter, the
trials count = cells shown + rules proposed). Definitions fixed here and in r1_common.py before any round-1 rule existed.

    python scorer.py score --rules rules_round1_A.json      # registers the file (sha256, append-only), scores every rule on half B
    python scorer.py score --rules rules_round1_B.json      # ... on half A
    python scorer.py combine                                # Holm over the round, the greedy lists L_A / L_B, the cross-fitted verdict
    python scorer.py all --rules rules_round1_A.json rules_round1_B.json     # the three in one go
    python scorer.py smoke                                  # code-path test on synthetic rules with a REDIRECTED ledger (scratchpad):
                                                            # nothing it computes is a finding and nothing reaches OUT/ledger

Stage `score` (per rules file, both timeframes; the file's `half_seen` = X, the other half Y = the scoring rows):
  0. registration   appends {"kind": "pre_registration", "what": "LLM hypotheses round 1 half X", sha256, the seen tables' sha256 and cell
                    counts, the ledger sha} to ledger/registrations.jsonl (once per sha; never edited) and a byte-identical copy to
                    ledger/registered/; refuses to score a file whose sha does not match a registration line.
  1. protocol       r1_common.check_rule against the tables the proposer saw: REFUSED (no ledger row, still counted in the family):
                    a label / NOT_FEATURES column, a calendar-time proxy (n_events_asof, sl), depth > 3, a missing column. FLAGGED
                    (scored, ineligible for the combination): a column outside the shown vocabulary / listed pairs, a threshold that is
                    not a printed edge / level / split point.
  2. rule mask      a rule fires when every comparison holds; None / NaN -> the comparison is False (the SETUP is kept). keep = not fired.
  3. scoring        harness.score on a harness.Table built over half Y's rows alone (r1_common.sub_table; its IS split IS half Y, so the
                    kept-vs-skipped statistics, the session-matched random control (2,000 draws) and the permutation p are half Y's):
                    family "llm_round1/X" (X = the half the rules were proposed on; the config carries proposed_on / scored_on), each rule
                    on L1 and on L0 (robustness), the union of the round-1 rules, the 8 round-0 rules of the timeframe on the same rows
                    (family "llm_round1/X/round0"), and for a rule that uses a top-5 drifted source column (drift.json) the same rule
                    without that comparison (family "llm_round1/X/drift_refit").
  4. multiplicity   the max-T family on half Y = every labelled cell of tables_<tf>_X.json rebuilt on half Y's rows as a skip set (the
                    seen half's decile edges, levels and buckets; a cell whose kept or skipped side has < 2 rows cannot enter the
                    permutation but stays in the count) + the round-1 rules of X + the round-0 rules; statistic = the kept-vs-skipped
                    mean difference standardised by the pooled sd of the scored rows x sqrt(1/n_kept + 1/n_skipped) (pooled_z; the
                    Welch t round 0 used is reported per rule for the record but is unstable for 5-20-unit cells under permutation);
                    net permuted across half Y's rows, 2,000 seeded draws; per rule the single-step family-wise p
                    P(max over the family of |z*| >= |z_rule|), the null's 95th percentile of max |z|; Holm over the rules of the round
                    (m = every round-1 rule of both halves and both timeframes + the 16 round-0 rules; a refused or untestable rule
                    enters with p = 1) and, for the record, Holm at m = family size (degenerate: the permutation p's floor 1/2001 times
                    m exceeds 0.05 for m > 100, so it can never pass and is not the eligibility criterion; the max-T with the cells in
                    the family is); harness.pbo / spa / effective_trials over the direction's vectors (round-1 rules, union, round-0
                    rules); harness.deflated_sharpe of each kept book with n_trials = the family size; harness.bootstrap_ci per diff;
                    the per-block diff on half Y's six blocks.
Stage `combine` (needs at least one scored direction):
  5. eligibility    a round-1 rule is eligible when it is protocol-clean and, on the other half: max-T family-wise p < 0.05, Holm p over
                    the rules of the round < 0.05, control percentile >= 95, diff > 0.
  6. greedy         per direction, eligible rules in order of diff; a rule is added while the marginal diff >= 200 INR/trade and the
                    |net|-weighted winner recall does not fall; every step is a ledger row (family "llm_round1/X_combo"); L_X = the list.
  7. cross-fit      (a) fixed crossed list: L_A applied to half B's rows, L_B to half A's, one ledger row over all IS rows (family
                    "llm_round1/crossfit", rule "fixed_crossed"); (b) the shipped form L_A u L_B on every IS row (rule "shipped"; in-sample
                    for the proposing half, reported as such); (c) the 12-block OOF: for test block g of harness.purged_splits, the
                    candidate rules are those proposed on the OTHER half's tables and steps 5-6 are re-run on the training rows that lie
                    in g's half (labels the proposer never saw; harness.metrics with the 2,000-draw controls, the max-T family rebuilt on
                    those rows), the chosen list decides g; one ledger row (rule "oof12"); (d) CPCV: the same per test block of every
                    cpcv_splits split -> harness.cpcv_paths -> harness.score_paths (11 rows, family "llm_round1/crossfit/cpcv"); the
                    path distribution of the diff and of the control percentile is the number that counts; PBO / SPA / effective
                    trials over the crossfit family (fixed, shipped, oof12, 11 paths), DSR with n_trials = the whole round's family
                    size, bootstrap CI of the fixed crossed list, harness.go_no_go on it with the CPCV item, the declared columns
                    (no time proxy) and the null-tape certificate (studies/null_tapes_drift/tapes.null_tape_check on the certificate
                    tapes: real diff > gmm p95 AND > segment p95, session tapes carry the sign in >= 75%); a rule list with an
                    extended column (features_ext) cannot be replayed on the tapes and fails that item with the reason recorded.
  8. outputs        scores_<X>.json, results_round1.json (everything), scores_<tf>.csv, FINDINGS_draft.md (for the step-3 agent to finish
                    into FINDINGS.md / findings.json), candidate_<tf>.json only when go_no_go passes, with provenance
                    {"vocabulary": "outside the frozen shortlist (importance rule failed for every cluster)"} for the user to accept or
                    reject (never copied to OUT/candidates/ by this script). Log: scorer.log.
"""
import os, sys, json, time, shutil, hashlib, argparse, datetime as D
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import r1_common as C
H = C.H
from joblib import Parallel, delayed
os.environ["PYTHONPATH"] = os.pathsep.join([HERE, C.OUT] + ([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else []))   # the loky workers import harness / r1_common


def light_table(T):
    """A copy of T without its DataFrames (F, FX, TR, sessions): what harness.metrics needs, small enough to ship to a worker."""
    L = H.Table.__new__(H.Table); L.__dict__.update({k: v for k, v in T.__dict__.items() if k not in ("F", "FX", "TR", "sessions", "_asof")})
    return L

FAMILY = C.STUDY
MAXT_DRAWS, ALPHA, CONTROL_MIN, COMBO_MIN_GAIN = 2000, 0.05, 95.0, 200.0
N_ROUND0 = 16
ROUND0_PATH = os.path.join(C.OUT, "studies", "llm_hypotheses", "rules_round0.json")
ROUND0_SHA = open(os.path.join(C.OUT, "studies", "llm_hypotheses", "rules_round0.sha256"), encoding="utf-8").read().split()[0]
OUTDIR = HERE
_LOG = None


def log(*a):
    global _LOG
    if _LOG is None: _LOG = open(os.path.join(OUTDIR, "scorer.log"), "a", encoding="utf-8")
    s = " ".join(str(x) for x in a); print(s, flush=True); _LOG.write(s + "\n"); _LOG.flush()


def jdump(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))


# ---------------------------------------------------------------- inputs
def load_rules(path):
    J = json.load(open(path, encoding="utf-8"))
    half = J.get("half_seen")
    assert half in C.HALVES, f"{path}: half_seen must be A or B"
    for tf in C.TFS:
        J.setdefault(tf, [])
        assert len(J[tf]) <= 8, f"{path}: more than 8 rules for {tf}"
        for r in J[tf]: r.setdefault("then", "skip"); r.setdefault("id", f"r1{half}_{tf}_{len(r['if'])}")
    return J


def load_tables(tf, half):
    p = os.path.join(HERE, f"tables_{tf}_{half}.json")
    return json.load(open(p, encoding="utf-8")), C.sha256(p), C.rel(p)


def tables_registered(half):
    last = None
    for r in C.registration_lines():
        if r.get("kind") == "pre_registration" and r.get("what") == f"LLM hypotheses round 1 labelled tables half {half}": last = r
    return last


def register_rules(path, J, smoke=False):
    sha = C.sha256(path); half = J["half_seen"]
    tabs = {}
    for tf in C.TFS:
        tj, tsha, trel = load_tables(tf, half)
        tabs[tf] = dict(file=trel, sha256=tsha, n_cells_labelled=tj["n_cells_labelled"], n_rules_round1=len(J[tf]))
    reg_t = tables_registered(half)
    if reg_t is not None:
        for tf in C.TFS:
            if reg_t["files"][tf]["sha256"] != tabs[tf]["sha256"]:
                log(f"WARNING: tables_{tf}_{half}.json sha {tabs[tf]['sha256'][:16]} differs from the registered {reg_t['files'][tf]['sha256'][:16]}: the tables changed after their registration")
    rec = dict(kind="pre_registration", what=f"LLM hypotheses round 1 half {half}", file=C.rel(path), sha256=sha, written_at=J.get("written_at"),
               half_seen=half, scored_on=C.OTHER[half], tables=tabs, n_rules={tf: len(J[tf]) for tf in C.TFS},
               family_size_maxt={tf: tabs[tf]["n_cells_labelled"] + len(J[tf]) + 8 for tf in C.TFS},
               note=(f"cross-fitted (Judge 1): rules written from tables_<tf>_{half}.md only, scored on half {C.OTHER[half]} (harness blocks {C.HALVES[C.OTHER[half]][0]}-{C.HALVES[C.OTHER[half]][-1]}); "
                     f"the max-T family per timeframe = the labelled cells of the seen tables + the round-1 rules of this half + the 8 round-0 rules (Judge 2); "
                     f"EMPTY-SHORTLIST RULE: every rule is exploratory, 'outside the frozen shortlist'. Registered before any ledger row of family llm_round1/{half}."),
               registered_at=C.now(), ledger_sha_at_registration=H.ledger_sha(), ledger_rows_of_family_at_registration=len(H.read_ledger(f"{FAMILY}/{half}")))
    written = C.append_registration(rec)
    os.makedirs(os.path.join(os.path.dirname(C.REGISTRATIONS), "registered"), exist_ok=True)
    copy = os.path.join(os.path.dirname(C.REGISTRATIONS), "registered", f"rules_round1_{half}.{sha[:8]}.json")
    if not os.path.exists(copy): shutil.copyfile(path, copy)
    assert C.sha256(copy) == sha
    log(f"registration half {half}: sha256 {sha} {'appended' if written else 'already present'}; copy {copy}")
    return sha, rec


# ---------------------------------------------------------------- masks and the max-T family
def cell_masks(FX, tables):
    """Every labelled cell of a tables JSON rebuilt on the rows of FX as a skip set (bool matrix cells x rows) with names; the base
    row (skip everything) is counted in the family size but has no skip set."""
    masks, names = [], []
    for c in tables["cells"]:
        if c["table"] == "base": continue
        m = np.array(C.bin_mask(FX[c["a"]["column"]], c["a"]["bin"]), dtype=bool)
        if c.get("b"): m = m & np.asarray(C.bin_mask(FX[c["b"]["column"]], c["b"]["bin"]), dtype=bool)
        masks.append(m); names.append(c["table"] + ":" + c["a"]["bin"]["label"] + (("|" + c["b"]["bin"]["label"]) if c.get("b") else ""))
    return (np.stack(masks) if masks else np.zeros((0, len(FX)), dtype=bool)), names


def welch_t(net, fires):
    k, s = net[~fires], net[fires]
    if len(k) < 2 or len(s) < 2: return np.nan
    return float((k.mean() - s.mean()) / np.sqrt(k.var(ddof=1) / len(k) + s.var(ddof=1) / len(s)))


def pooled_z(net, R, sd):
    """Kept-vs-skipped mean difference standardised by the pooled sd of ALL scored rows: z = (mean_kept - mean_skipped) /
    (sd x sqrt(1/n_kept + 1/n_skipped)); NaN when a side has < 2 rows. The denominator is permutation-invariant, so a 5-unit cell
    cannot produce a huge |z| by drawing five similar nets (the Welch t did: with cells of 5-20 units in the family its permutation
    null of max |t| reached p95 ~ 10, which no rule could ever beat). Rows of R = skip sets."""
    Rs = R.astype(float); Rk = 1.0 - Rs
    nk, ns = Rk.sum(axis=1), Rs.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = ((Rk @ net) / nk - (Rs @ net) / ns) / (sd * np.sqrt(1.0 / nk + 1.0 / ns))
    z[(nk < 2) | (ns < 2)] = np.nan
    return z


def max_t(net, R_family, rule_idx, tag, draws=MAXT_DRAWS):
    """Westfall-Young single-step max-T over the family: R_family = bool (M x n) skip sets (cells + rules); rule_idx = the rows of
    R_family that are the proposed rules. Statistic = pooled_z (above). net is permuted across the n rows, 2,000 seeded draws; every
    draw gives max over the testable family members of |z*|. Returns per rule the observed z (and the Welch t for the record, the
    statistic round 0 reported), the family-wise p = (1 + #{max |z*| >= |z_rule|}) / (1 + draws), the null's p95 / p99, the best
    family member and its own family-wise p, the family bookkeeping."""
    n = len(net); M = R_family.shape[0]
    sd = float(np.std(net, ddof=1)) if n > 1 else np.nan
    obs = pooled_z(net, R_family, sd) if M else np.zeros(0)
    welch = [None if j >= M else (None if not np.isfinite(welch_t(net, R_family[j])) else round(welch_t(net, R_family[j]), 3)) for j in rule_idx]
    ok = np.isfinite(obs)
    out = dict(draws=draws, statistic="kept-vs-skipped mean difference over the pooled sd of the scored rows x sqrt(1/n_kept + 1/n_skipped) (permutation-invariant denominator); net permuted across the scored half's rows",
               family_masks=int(M), family_testable=int(ok.sum()), rule_t=[None if (j >= M or not np.isfinite(obs[j])) else round(float(obs[j]), 3) for j in rule_idx], rule_welch_t=welch,
               rule_fw_p=[1.0] * len(rule_idx), null_max_abs_t_p95=None, null_max_abs_t_p99=None, best_family_member=None, best_family_abs_t=None)
    if not ok.any() or n < 4 or not np.isfinite(sd) or sd <= 0: return out
    rng = np.random.default_rng(int(hashlib.sha1(f"fz|{FAMILY}|maxT|{tag}".encode()).hexdigest(), 16) % (2 ** 32))
    Rs = R_family[ok].astype(float); Rk = 1.0 - Rs
    nk, ns = Rk.sum(axis=1), Rs.sum(axis=1); den = sd * np.sqrt(1.0 / nk + 1.0 / ns)
    mx = np.empty(draws)
    for d in range(draws):
        p = net[rng.permutation(n)]
        mx[d] = np.max(np.abs(((Rk @ p) / nk - (Rs @ p) / ns) / den))
    a_obs = np.abs(obs)
    out["rule_fw_p"] = [1.0 if (j >= M or not np.isfinite(obs[j])) else round(float((1 + (mx >= a_obs[j] - 1e-12).sum()) / (1 + draws)), 4) for j in rule_idx]
    out["null_max_abs_t_p95"] = round(float(np.quantile(mx, 0.95)), 3); out["null_max_abs_t_p99"] = round(float(np.quantile(mx, 0.99)), 3)
    j_best = int(np.nanargmax(np.where(ok, a_obs, -np.inf))); out["best_family_member"] = j_best; out["best_family_abs_t"] = round(float(a_obs[j_best]), 3)
    out["best_family_fw_p"] = round(float((1 + (mx >= a_obs[j_best] - 1e-12).sum()) / (1 + draws)), 4)
    return out


def holm(p, m=None):
    """Holm step-down adjusted p over the given raw p (missing rules of the round padded with p = 1 up to m)."""
    p = np.asarray(p, dtype=float); k = len(p); m = max(m or k, k)
    order = np.argsort(p); out = np.empty(k); prev = 0.0
    for i, j in enumerate(order):
        v = min(1.0, (m - i) * p[j]); prev = max(prev, v); out[j] = prev
    return out


def block_table(T, fires, rows):
    bl = T.block[rows]; net = T.net[rows]; kp = ~fires[rows]; d = {}
    for b in sorted(set(bl.tolist())):
        m = bl == b
        d[f"b{b:02d}"] = round(float(net[m & kp].mean() - net[m & ~kp].mean()), 2) if (m & kp).sum() and (m & ~kp).sum() else None
    vals = [v for v in d.values() if v is not None]
    d["blocks_defined"] = len(vals); d["blocks_positive"] = int(sum(v > 0 for v in vals)); d["block_diff_min"] = round(float(min(vals)), 2) if vals else None
    return d


def kept_series(vec):
    with np.errstate(all="ignore"): km = np.where(vec["kept_n"] > 0, vec["kept_sum"] / np.maximum(vec["kept_n"], 1), np.nan)
    return km[np.isfinite(km)]


def rule_cfg(r, half, other, rules_sha, tables_sha, **kw):
    return dict(round=1, proposed_on=half, scored_on=other, rule=r["id"], **{"if": r["if"]}, then="skip", rules_sha256=rules_sha[:16], tables_sha256=tables_sha[:16], **kw)


# ---------------------------------------------------------------- stage: score one direction
def score_direction(path, J, tabs_T, smoke=False):
    half = J["half_seen"]; other = C.OTHER[half]
    rules_sha, reg = register_rules(path, J, smoke)
    round0 = json.load(open(ROUND0_PATH, encoding="utf-8"))
    assert C.sha256(ROUND0_PATH) == ROUND0_SHA, "rules_round0.json changed since its registration"
    res = dict(stage="score", half_seen=half, scored_on=other, rules_file=C.rel(path), rules_sha256=rules_sha, registration=reg, scored_at=C.now(), ledger_sha_before=H.ledger_sha(), timeframes={})
    for tf in C.TFS:
        t0 = time.time()
        T, T0 = tabs_T[tf]
        tables, tsha, trel = load_tables(tf, half)
        rows_o = C.half_rows(T, other); Ts = C.sub_table(T, rows_o); rows_s = np.flatnonzero(Ts.is_mask)
        Ts0 = C.sub_table(T0, C.half_rows(T0, other))
        proxies = C.time_proxies(tf); pairs = C.interaction_pairs(tf); drift = C.drift_info(tf)
        rules = J[tf]; r0 = round0[tf]
        n_cells = tables["n_cells_labelled"]
        fam_size = n_cells + len(rules) + len(r0)
        log(f"[{half}->{other} {tf}] {len(rules)} round-1 rules, {n_cells} labelled cells seen, family size {fam_size}; scoring rows {len(rows_s)} ({Ts.day[rows_s].min()}..{Ts.day[rows_s].max()})")
        per, vecs, masks_rules = [], [], []
        for r in rules:
            chk = C.check_rule(r, tf, Ts.FX, tables, pairs, proxies)
            entry = dict(id=r["id"], rule=r["if"], reason=r.get("reason"), cells_cited=r.get("cells"), check=chk, refused=chk["refused"] is not None, protocol_clean=(chk["refused"] is None and not chk["flags"]))
            if chk["refused"]:
                log(f"[{half}->{other} {tf}] {r['id']}: REFUSED ({chk['refused']}); counted in the family, no ledger row"); per.append(entry); masks_rules.append(None); continue
            fires = C.rule_fires(Ts.FX, r); fires0 = C.rule_fires(Ts0.FX, r)
            ns = int(fires[rows_s].sum()); untestable = ns <= 1 or ns >= len(rows_s) - 1
            cfg = rule_cfg(r, half, other, rules_sha, tsha)
            m1 = H.score(Ts, ~fires, f"{FAMILY}/{half}", cfg, script=__file__)
            m0 = H.score(Ts0, ~fires0, f"{FAMILY}/{half}", dict(cfg, label_note="L0 robustness"), script=__file__)
            vec = H.session_vectors(Ts, ~fires, rows_s); vecs.append(vec); masks_rules.append(fires)
            entry.update(untestable=untestable, L1=m1, L0=m0, blocks=block_table(Ts, fires, rows_s), boot=(H.bootstrap_ci(vec, tag=f"{tf}|{half}|{r['id']}") if not untestable else None), drift=[])
            for col in set(chk["columns"]):
                if col in drift["top20"]: entry["drift"].append(dict(column=col, caveat="top-20 drifted IS-early vs IS-late", **drift["top20"][col]))
                if col in drift["top5_sources"] and len(r["if"]) > 1:
                    red = dict(r, id=r["id"] + f"~{col}"); red["if"] = [c for c in r["if"] if c[0] != col]
                    fr = C.rule_fires(Ts.FX, red)
                    mr = H.score(Ts, ~fr, f"{FAMILY}/{half}/drift_refit", rule_cfg(red, half, other, rules_sha, tsha, refit_without=col), script=__file__)
                    entry["drift"].append(dict(column=col, caveat="top-5 drifted source column: the rule is also scored without it", refit_without=col, refit_diff=mr["diff"], refit_control_pct=mr["control_pct"], refit_kept_n=mr["kept_n"], refit_ledger_id=mr["id"]))
            log(f"[{half}->{other} {tf}] {r['id']:14s} skipped {m1['skipped_n']:5d} kept {m1['kept_n']:5d} diff {m1['diff']} top1off {m1['diff_top1_removed']} ctrl {m1['control_pct']} perm_p {m1['perm_p']} loserR {m1['loser_recall']} winR(w) {m1['winner_recall_weighted']} | L0 diff {m0['diff']} ctrl {m0['control_pct']}"
                + (" << UNTESTABLE" if untestable else "") + (f" flags {chk['flags']}" if chk["flags"] else ""))
            per.append(entry)
        # union of the round-1 rules
        union = None
        live = [m for m in masks_rules if m is not None]
        if live:
            U = np.any(np.stack(live), axis=0)
            mu = H.score(Ts, ~U, f"{FAMILY}/{half}", dict(round=1, proposed_on=half, scored_on=other, rule="union_round1", members=[p["id"] for p in per if not p["refused"]], then="skip", rules_sha256=rules_sha[:16], tables_sha256=tsha[:16]), script=__file__)
            vu = H.session_vectors(Ts, ~U, rows_s); vecs.append(vu)
            union = dict(L1=mu, blocks=block_table(Ts, U, rows_s), boot=H.bootstrap_ci(vu, tag=f"{tf}|{half}|union"))
            log(f"[{half}->{other} {tf}] union: skipped {mu['skipped_n']} kept {mu['kept_n']} diff {mu['diff']} ctrl {mu['control_pct']} perm_p {mu['perm_p']}")
        # round-0 rules on the same rows (their own family sub-key; they enter the max-T family and the PBO / SPA vectors)
        r0_masks, r0_res = [], []
        for r in r0:
            f0 = C.rule_fires(Ts.FX, r); r0_masks.append(f0)
            mr0 = H.score(Ts, ~f0, f"{FAMILY}/{half}/round0", dict(round=0, rule=r["id"], **{"if": r["if"]}, then="skip", scored_on=other, sha256_rules=ROUND0_SHA[:16]), script=__file__)
            r0_res.append(dict(id=r["id"], rule=r["if"], L1=mr0)); vecs.append(H.session_vectors(Ts, ~f0, rows_s))
        log(f"[{half}->{other} {tf}] round-0 on half {other}: " + ", ".join(f"{x['id']} {x['L1']['diff']}" for x in r0_res))
        # max-T family on half Y: cells (seen half's bins rebuilt here) + round-1 rules + round-0 rules
        CM, cnames = cell_masks(Ts.FX, tables)
        fam = [CM[i, rows_s] for i in range(CM.shape[0])] + [m[rows_s] for m in live] + [m[rows_s] for m in r0_masks]
        R = np.stack(fam) if fam else np.zeros((0, len(rows_s)), dtype=bool)
        rule_idx = list(range(CM.shape[0], CM.shape[0] + len(live)))
        mt = max_t(Ts.net[rows_s], R, rule_idx, tag=f"{tf}|{half}->{other}")
        mt.update(n_cells_labelled=n_cells, n_cells_with_skip_set=int(CM.shape[0]), n_rules_round1=len(rules), n_rules_round1_scored=len(live), n_rules_round0=len(r0), family_size=fam_size,
                  best_family_member_name=(cnames + [p["id"] for p in per if not p["refused"]] + [x["id"] for x in r0])[mt["best_family_member"]] if mt["best_family_member"] is not None else None)
        k = 0
        for p in per:
            if p["refused"]: p["maxt_t"], p["maxt_fw_p"] = None, 1.0; continue
            p["maxt_t"], p["maxt_fw_p"] = mt["rule_t"][k], mt["rule_fw_p"][k]; k += 1
            p["holm_p_family"] = round(float(min(1.0, fam_size * (p["L1"]["perm_p"] if p["L1"]["perm_p"] is not None else 1.0))), 4)
        log(f"[{half}->{other} {tf}] max-T: family {mt['family_masks']} masks ({mt['family_testable']} testable) of size {fam_size}; null p95 of max|t| {mt['null_max_abs_t_p95']}; best member {mt['best_family_member_name']} |t| {mt['best_family_abs_t']} fw p {mt.get('best_family_fw_p')}; rules: " + ", ".join(f"{p['id']} t {p['maxt_t']} fw_p {p['maxt_fw_p']}" for p in per))
        # family statistics of the direction
        fam_stats = dict(vectors=len(vecs))
        if len(vecs) >= 2:
            fam_stats.update(pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"{tf}|{half}->{other}"), effective_trials=H.effective_trials(vecs))
        srs = [(lambda x: float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan)(kept_series(v)) for v in vecs]
        sr_var = float(np.nanvar(np.array(srs), ddof=1)) if np.isfinite(srs).sum() > 1 else None
        j = 0
        for p in per:
            if p["refused"]: continue
            p["dsr"] = H.deflated_sharpe(kept_series(vecs[j]), fam_size, sr_var if sr_var and sr_var > 0 else None); j += 1
        log(f"[{half}->{other} {tf}] family: PBO(diff) {fam_stats.get('pbo_diff', {}).get('pbo')} SPA p {fam_stats.get('spa', {}).get('spa_p')} (unstud. {fam_stats.get('spa', {}).get('spa_p_unstudentised')}) eff. trials {fam_stats.get('effective_trials')}; {time.time() - t0:.0f} s")
        res["timeframes"][tf] = dict(tables_file=trel, tables_sha256=tsha, n_rows_scored=int(len(rows_s)), n_sessions_scored=int(len(Ts.active_sessions)), all_mean_L1=round(float(Ts.net[rows_s].mean()), 2),
                                     rules=per, union=union, round0=r0_res, max_t=mt, family=fam_stats, sharpe_var_family=sr_var, runtime_s=round(time.time() - t0, 1))
    res["ledger_sha_after"] = H.ledger_sha()
    jdump(res, os.path.join(OUTDIR, f"scores_{half}.json"))
    log(f"scores_{half}.json written; ledger {res['ledger_sha_before']} -> {res['ledger_sha_after']}")
    return res


# ---------------------------------------------------------------- nested selection (steps 5-6 on arbitrary rows; no ledger writes)
def eligible_and_greedy(T, rows, cand, fires_full, stats, maxt_fw_p, holm_p, tag, step_fn):
    """cand = rule dicts; fires_full = their fire masks over all rows of T; stats = per-rule metrics on `rows` (diff, control_pct,
    winner_recall_weighted); step_fn(keep_full, members) -> metrics of a combination step (harness.score in the outer run,
    harness.metrics inside the folds). Returns (chosen ids, steps, eligibility per rule)."""
    elig = []
    for j, r in enumerate(cand):
        st = stats[j]; e = dict(id=r["id"], clean=r.get("_clean", True), diff=st.get("diff") if st else None, control_pct=st.get("control_pct") if st else None, maxt_fw_p=maxt_fw_p[j], holm_p=holm_p[j])
        e["eligible"] = bool(r.get("_clean", True) and st and st.get("diff") is not None and st["diff"] > 0 and (st.get("control_pct") or 0) >= CONTROL_MIN and maxt_fw_p[j] < ALPHA and holm_p[j] < ALPHA)
        elig.append(e)
    order = sorted([j for j, e in enumerate(elig) if e["eligible"]], key=lambda j: -(stats[j]["diff"]))
    chosen, steps, cur, prev = [], [], np.zeros(T.n, dtype=bool), None
    for j in order:
        cand_mask = cur | fires_full[j]
        m = step_fn(~cand_mask, [cand[i]["id"] for i in chosen + [j]])
        step = dict(added=cand[j]["id"], kept_n=m.get("kept_n"), diff=m.get("diff"), control_pct=m.get("control_pct"), winner_recall_weighted=m.get("winner_recall_weighted"), ledger_id=m.get("id"))
        if prev is not None:
            marg = (m["diff"] or 0) - (prev["diff"] or 0); step["marginal_diff"] = round(marg, 2)
            if marg < COMBO_MIN_GAIN or (m.get("winner_recall_weighted") or 0) < (prev.get("winner_recall_weighted") or 0):
                step["accepted"] = False; steps.append(step); break
        step["accepted"] = True; steps.append(step); chosen.append(j); cur = cand_mask; prev = m
    return [cand[j]["id"] for j in chosen], steps, elig


def nested_select(T, sel_rows, cand, fires_full, CM_full, r0_full, holm_m, tag, draws_ctrl):
    """Steps 5-6 re-run on `sel_rows` (training rows of a split that lie in the test block's half): per-rule harness.metrics with the
    controls, the max-T family (cells of the proposer's seen tables rebuilt on these rows + the candidate rules + round 0), Holm over the
    rules of the round, the greedy combination by harness.metrics (no controls). Returns (chosen ids, diagnostics)."""
    if not cand: return [], dict(n_cand=0)
    stats = []
    for j, r in enumerate(cand):
        f = fires_full[j][sel_rows]
        if f.sum() <= 1 or (~f).sum() <= 1 or not r.get("_clean", True): stats.append(None); continue
        stats.append(H.metrics(T, ~fires_full[j], sel_rows, f"{tag}|{r['id']}", controls=True, draws=draws_ctrl))
    net = T.net[sel_rows]
    fam = [CM_full[i, sel_rows] for i in range(CM_full.shape[0])] + [fires_full[j][sel_rows] for j in range(len(cand))] + [m[sel_rows] for m in r0_full]
    R = np.stack(fam); rule_idx = list(range(CM_full.shape[0], CM_full.shape[0] + len(cand)))
    mt = max_t(net, R, rule_idx, tag=tag, draws=MAXT_DRAWS)
    raw = [1.0 if (s is None or s.get("perm_p") is None) else float(s["perm_p"]) for s in stats]
    hp = holm(raw, m=holm_m)
    def step_fn(keep_full, members): return H.metrics(T, keep_full, sel_rows, f"{tag}|combo|{'+'.join(members)}", controls=False)
    chosen, steps, elig = eligible_and_greedy(T, sel_rows, cand, fires_full, stats, mt["rule_fw_p"], hp, tag, step_fn)
    return chosen, dict(n_cand=len(cand), n_sel_rows=int(len(sel_rows)), eligible=[e["id"] for e in elig if e["eligible"]], chosen=chosen, maxt_null_p95=mt["null_max_abs_t_p95"], steps=steps)


def _cpcv_split_worker(Tl, dirs, tr, te, ab, holm_m, draws_ctrl, tf, maxt_draws):
    """One CPCV split (runs in a loky worker): per test block the nested selection on the training rows of that block's half."""
    global MAXT_DRAWS; MAXT_DRAWS = maxt_draws
    pred = np.ones(len(te)); chosen_ab = {}
    for g in ab:
        gh = "A" if g in C.HALVES["A"] else "B"; prop = C.OTHER[gh]
        if prop not in dirs: chosen_ab[g] = []; continue
        d = dirs[prop]; sel_rows = tr[np.isin(Tl.block[tr], C.HALVES[gh])]
        chosen, _ = nested_select(Tl, sel_rows, d["rules"], d["fires_full"], d["CM_full"], d["r0_full"], holm_m, f"{tf}|cpcv|{ab[0]}-{ab[1]}|g{g}", draws_ctrl)
        m = Tl.block[te] == g
        if chosen:
            fires = np.zeros(int(m.sum()), dtype=bool)
            for j, r in enumerate(d["rules"]):
                if r["id"] in chosen: fires |= d["fires_full"][j][te[m]]
            pred[m] = (~fires).astype(float)
        chosen_ab[g] = chosen
    return ab, pred, chosen_ab


def _san(d):
    """NaN -> None so the JSON stays standard."""
    return {k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in d.items()}


def null_tape_item(tf, rules_out, real_diff):
    """The null-tape certificate of studies/null_tapes_drift (tapes.null_tape_check on the certificate tapes) for a rule list; a failure
    to run (e.g. an extended column that the tape tables do not carry) is recorded as the reason and fails the item."""
    if not rules_out: return "no rule list (nothing to check)", None
    try:
        sys.path.insert(0, os.path.join(C.OUT, "studies", "null_tapes_drift")); import tapes
        passed, checks, summary = tapes.null_tape_check(real_diff, tf, {"rules": rules_out})
        return checks, dict(passed=bool(passed), null_tape_diff_inr=summary.get("null_tape_diff_inr"))
    except Exception as e:                                                      # noqa: BLE001  the reason is the record
        return f"null_tape_check failed: {type(e).__name__}: {e}", None


def crossfit_tf(tf, T, dirs, holm_m, fam_total, draws_ctrl, n_jobs):
    """dirs = {half_seen: dict(rules, fires_full, clean, CM_full, r0_full, L (outer chosen ids))} for the directions that exist."""
    t0 = time.time()
    out = dict(tf=tf, directions={h: dict(L=d["L"], n_rules=len(d["rules"])) for h, d in dirs.items()})
    is_rows = np.flatnonzero(T.is_mask)
    def fires_of(d, ids, rows):
        m = np.zeros(len(rows), dtype=bool)
        for j, r in enumerate(d["rules"]):
            if r["id"] in ids: m |= d["fires_full"][j][rows]
        return m
    cfg0 = dict(round=1, then="skip", members={h: d["L"] for h, d in dirs.items()}, rules_sha256={h: d["sha"][:16] for h, d in dirs.items()}, family_size_total=fam_total)
    # (a) fixed crossed list, (b) shipped
    fixed = np.zeros(T.n, dtype=bool)
    for h, d in dirs.items():
        rows_o = C.half_rows(T, C.OTHER[h]); fixed[rows_o] = fires_of(d, d["L"], rows_o)
    shipped = np.zeros(T.n, dtype=bool)
    for h, d in dirs.items(): shipped |= fires_of(d, d["L"], np.arange(T.n))
    any_rule = any(d["L"] for d in dirs.values())
    vecs, rows_out = [], {}
    if any_rule:
        r_fixed = H.score(T, ~fixed, f"{FAMILY}/crossfit", dict(cfg0, rule="fixed_crossed"), script=__file__)
        r_ship = H.score(T, ~shipped, f"{FAMILY}/crossfit", dict(cfg0, rule="shipped"), script=__file__)
        vecs += [H.session_vectors(T, ~fixed, is_rows), H.session_vectors(T, ~shipped, is_rows)]
        rows_out.update(fixed_crossed=r_fixed, shipped=r_ship)
        log(f"[crossfit {tf}] fixed crossed list: kept {r_fixed['kept_n']} skipped {r_fixed['skipped_n']} diff {r_fixed['diff']} ctrl {r_fixed['control_pct']} perm_p {r_fixed['perm_p']} sign_blocks {r_fixed['sign_blocks']}; shipped: kept {r_ship['kept_n']} diff {r_ship['diff']} ctrl {r_ship['control_pct']}")
    else:
        log(f"[crossfit {tf}] no rule chosen in either direction: the fixed crossed list is empty (no ledger row; keep everything)")
    # (c) 12-block OOF and (d) CPCV, nested selection per test block
    def select_for_block(g, tr, tag):
        gh = "A" if g in C.HALVES["A"] else "B"; prop = C.OTHER[gh]
        if prop not in dirs: return [], dict(n_cand=0, note=f"no rules file for half {prop}")
        d = dirs[prop]; sel_rows = tr[np.isin(T.block[tr], C.HALVES[gh])]
        return nested_select(T, sel_rows, d["rules"], d["fires_full"], d["CM_full"], d["r0_full"], holm_m, tag, draws_ctrl)
    oof_keep = np.ones(T.n, dtype=bool); oof_diag = {}
    for b, (tr, te) in enumerate(H.purged_splits(T)):
        chosen, diag = select_for_block(b, tr, f"{tf}|oof12|b{b}")
        gh = "A" if b in C.HALVES["A"] else "B"; prop = C.OTHER[gh]
        if chosen: oof_keep[te] = ~fires_of(dirs[prop], chosen, te)
        oof_diag[f"b{b:02d}"] = dict(proposer=prop, chosen=chosen, n_sel_rows=diag.get("n_sel_rows"), eligible=diag.get("eligible"))
        log(f"[crossfit {tf}] oof12 block {b}: rules of {prop} selected on {diag.get('n_sel_rows')} training rows of half {gh} -> chosen {chosen}")
    r_oof = H.score(T, oof_keep, f"{FAMILY}/crossfit", dict(cfg0, rule="oof12", selection="nested per test block"), script=__file__)
    vecs.append(H.session_vectors(T, oof_keep, is_rows)); rows_out["oof12"] = r_oof
    log(f"[crossfit {tf}] oof12: kept {r_oof['kept_n']} skipped {r_oof['skipped_n']} diff {r_oof['diff']} ctrl {r_oof['control_pct']} perm_p {r_oof['perm_p']} sign_blocks {r_oof['sign_blocks']}")
    splits = list(H.cpcv_splits(T))
    Tl = light_table(T); dirs_light = {h: dict(rules=d["rules"], fires_full=d["fires_full"], CM_full=d["CM_full"], r0_full=d["r0_full"]) for h, d in dirs.items()}
    results = Parallel(n_jobs=n_jobs, backend="loky")(delayed(_cpcv_split_worker)(Tl, dirs_light, tr, te, ab, holm_m, draws_ctrl, tf, MAXT_DRAWS) for tr, te, ab in splits)
    oof = {ab: pred for ab, pred, _ in results}; chosen_by_split = {f"{ab[0]}-{ab[1]}": ch for ab, _, ch in results}
    paths = H.cpcv_paths(T, oof)
    dist, prow = H.score_paths(T, paths, f"{FAMILY}/crossfit", dict(cfg0, rule="cpcv_nested"), script=__file__, controls=True, threshold=0.5)
    dist = _san(dist)
    for p in paths: vecs.append(H.session_vectors(T, np.nan_to_num(p, nan=1.0) >= 0.5, is_rows))
    n_sel = sum(1 for ch in chosen_by_split.values() for g, c in ch.items() if c)
    log(f"[crossfit {tf}] CPCV: {len(splits)} splits, blocks with a non-empty selection {n_sel} of {2 * len(splits)}; diff median {dist['diff_median']} p5 {dist['diff_p5']} share>0 {dist['diff_share_positive']} kept share median {dist['kept_share_median']} ctrl median {dist.get('control_pct_median')}")
    fam = dict(vectors=len(vecs))
    if len(vecs) >= 2: fam.update(pbo_diff=H.pbo(vecs, "diff"), pbo_kept_mean=H.pbo(vecs, "kept_mean"), spa=H.spa(vecs, tag=f"{tf}|crossfit"), effective_trials=H.effective_trials(vecs))
    verdict = None
    rules_out = [{"if": r["if"], "then": "skip", "id": r["id"], "proposed_on_tables_of_half": h} for h, d in dirs.items() for r in d["rules"] if r["id"] in d["L"]]
    columns = sorted({c[0] for r in rules_out for c in r["if"]})
    if any_rule:
        srs = [(lambda x: float(x.mean() / x.std(ddof=1)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan)(kept_series(v)) for v in vecs]
        sr_var = float(np.nanvar(np.array(srs), ddof=1)) if np.isfinite(srs).sum() > 1 else None
        dsr = H.deflated_sharpe(kept_series(vecs[0]), fam_total, sr_var if sr_var and sr_var > 0 else None)
        boot = H.bootstrap_ci(vecs[0], tag=f"{tf}|crossfit_fixed")
        nt, nt_summary = null_tape_item(tf, rules_out, rows_out["fixed_crossed"]["diff"])
        ok, ch = H.go_no_go(rows_out["fixed_crossed"], tf, cpcv=dist, pbo_value=fam.get("pbo_diff", {}).get("pbo"), dsr=dsr, spa_p=fam.get("spa", {}).get("spa_p"), boot=boot, null_tape=nt, columns=columns)
        verdict = dict(passed=bool(ok), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, dsr=dsr, boot=boot, null_tape=nt_summary if nt_summary else nt, columns=columns)
        log(f"[crossfit {tf}] null tapes: {nt if isinstance(nt, str) else nt_summary}")
        log(f"[crossfit {tf}] go/no-go on the fixed crossed list: {'PASS' if ok else 'fail'} " + ", ".join(f"{k}={'ok' if v[0] else 'FAIL'}" for k, v in ch.items()))
    else:
        dsr = H.deflated_sharpe(kept_series(vecs[0]), fam_total, None)
        ok, ch = H.go_no_go(r_oof, tf, cpcv=dist, pbo_value=fam.get("pbo_diff", {}).get("pbo"), dsr=dsr, spa_p=fam.get("spa", {}).get("spa_p"), boot=H.bootstrap_ci(vecs[0], tag=f"{tf}|oof12"), null_tape="no rule list (nothing to check)", columns=[])
        verdict = dict(passed=bool(ok), checks={k: [bool(v[0]), v[1]] for k, v in ch.items()}, dsr=dsr, note="no fixed crossed list (no rule chosen in either direction); go/no-go read on the oof12 row", columns=[])
        log(f"[crossfit {tf}] go/no-go on oof12: {'PASS' if ok else 'fail'}")
    out.update(rows=rows_out, rules_out=rules_out, oof12_selection=oof_diag, cpcv=dist, cpcv_selection=chosen_by_split, cpcv_blocks_with_selection=n_sel, family=fam, go_no_go=verdict, runtime_s=round(time.time() - t0, 1))
    return out


# ---------------------------------------------------------------- stage: combine
def combine(tabs_T, draws_ctrl=H.CONTROL_DRAWS, n_jobs=4):
    t0 = time.time()
    scores = {}
    for h in C.HALVES:
        p = os.path.join(OUTDIR, f"scores_{h}.json")
        if os.path.exists(p): scores[h] = json.load(open(p, encoding="utf-8"))
    assert scores, "no scores_<half>.json: run `score` first"
    rules_files = {h: json.load(open(os.path.join(C.OUT, s["rules_file"]), encoding="utf-8")) for h, s in scores.items()}
    for h, s in scores.items(): assert C.sha256(os.path.join(C.OUT, s["rules_file"])) == s["rules_sha256"], f"rules file of half {h} changed since scoring"
    round0 = json.load(open(ROUND0_PATH, encoding="utf-8"))
    # Holm over the rules of the round: every round-1 rule (both halves, both timeframes) + the 16 round-0 rules (refused / untestable -> p = 1)
    allp, index = [], []
    for h, s in scores.items():
        for tf in C.TFS:
            for j, p in enumerate(s["timeframes"][tf]["rules"]):
                pp = None if p["refused"] or p.get("untestable") else p["L1"]["perm_p"]
                allp.append(1.0 if pp is None else float(pp)); index.append((h, tf, j))
    holm_m = len(allp) + N_ROUND0
    hp = holm(allp, m=holm_m)
    for (h, tf, j), v in zip(index, hp): scores[h]["timeframes"][tf]["rules"][j]["holm_p_round"] = round(float(v), 4)
    log(f"combine: Holm over the rules of the round: {len(allp)} round-1 rules + {N_ROUND0} round-0 = m {holm_m}; min adjusted p {hp.min() if len(hp) else None}")
    results = dict(study=FAMILY, stage="combine", combined_at=C.now(), ledger_sha_before=H.ledger_sha(), directions_present=sorted(scores), holm=dict(m=holm_m, raw_p=[round(x, 4) for x in allp], holm_p=[round(float(x), 4) for x in hp],
                   rules=[f"{h}:{tf}:{scores[h]['timeframes'][tf]['rules'][j]['id']}" for h, tf, j in index]), eligibility_rule=f"protocol-clean and, on the other half: diff > 0, control pct >= {CONTROL_MIN}, max-T family-wise p < {ALPHA} (family = labelled cells shown + rules proposed), Holm p over the rules of the round (m = {holm_m}) < {ALPHA}",
                   greedy_rule=f"eligible rules in order of diff; add while the marginal diff >= {COMBO_MIN_GAIN} INR/trade and the |net|-weighted winner recall does not fall; every step a ledger row", timeframes={}, scores=scores)
    for tf in C.TFS:
        T, _ = tabs_T[tf]
        dirs = {}
        fam_total = 0
        for h, s in scores.items():
            other = C.OTHER[h]; st = s["timeframes"][tf]
            rules = [dict(r) for r in rules_files[h][tf]]
            per = st["rules"]
            for r, p in zip(rules, per): r["_clean"] = bool(p["protocol_clean"]); r.setdefault("then", "skip")
            fires_full = [np.zeros(T.n, dtype=bool) if p["refused"] else C.rule_fires(T.FX, r) for r, p in zip(rules, per)]
            tables, tsha, _ = load_tables(tf, h)
            CM_full, _ = cell_masks(T.FX, tables)
            r0_full = [C.rule_fires(T.FX, r) for r in round0[tf]]
            fam_total += st["max_t"]["n_cells_labelled"] + st["max_t"]["n_rules_round1"]
            # outer eligibility + greedy on the other half (ledger rows)
            rows_o = C.half_rows(T, other); Ts = C.sub_table(T, rows_o)
            stats = [None if p["refused"] or p.get("untestable") else p["L1"] for p in per]
            fw = [p.get("maxt_fw_p", 1.0) for p in per]; hpr = [p.get("holm_p_round", 1.0) for p in per]
            def step_fn(keep_full, members, _Ts=Ts, _rows=rows_o, _h=h, _o=other, _sha=s["rules_sha256"], _tsha=tsha):
                return H.score(_Ts, keep_full[_rows], f"{FAMILY}/{_h}_combo", dict(round=1, proposed_on=_h, scored_on=_o, rule="combo", members=members, then="skip", rules_sha256=_sha[:16], tables_sha256=_tsha[:16]), script=__file__)
            L, steps, elig = eligible_and_greedy(T, rows_o, rules, fires_full, stats, fw, hpr, f"{tf}|{h}", step_fn)
            log(f"[combine {tf}] direction {h}->{other}: eligible {[e['id'] for e in elig if e['eligible']]} -> L_{h} = {L}" + (f" steps {[(x['added'], x['diff'], x.get('marginal_diff'), x['accepted']) for x in steps]}" if steps else ""))
            dirs[h] = dict(rules=rules, fires_full=fires_full, CM_full=CM_full, r0_full=r0_full, L=L, steps=steps, eligibility=elig, sha=s["rules_sha256"])
        fam_total += 8                                  # the timeframe's round-0 rules, once
        cf = crossfit_tf(tf, T, dirs, holm_m, fam_total, draws_ctrl, n_jobs)
        cf["family_size_total"] = fam_total
        cf["outer"] = {h: dict(L=d["L"], steps=d["steps"], eligibility=d["eligibility"]) for h, d in dirs.items()}
        results["timeframes"][tf] = cf
        # candidate only when go_no_go passes (the step-3 agent decides on OUT/candidates/ and the registration)
        if cf["go_no_go"] and cf["go_no_go"]["passed"] and any(d["L"] for d in dirs.values()):
            rules_out = []
            for h, d in dirs.items():
                for r in d["rules"]:
                    if r["id"] in d["L"]: rules_out.append({"if": r["if"], "then": "skip", "id": r["id"], "reason": r.get("reason"), "proposed_on_tables_of_half": h})
            cand = dict(gate={tf: dict(rules=rules_out)}, provenance=dict(source="learned on IS 2021-10..2025-12", script="studies/llm_round1/scorer.py", study=FAMILY,
                        ledger_id=cf["rows"]["fixed_crossed"]["id"], statistic=dict(diff=cf["rows"]["fixed_crossed"]["diff"], control_pct=cf["rows"]["fixed_crossed"]["control_pct"], cpcv=cf["cpcv"]),
                        vocabulary="outside the frozen shortlist (importance rule failed for every cluster)", rules_sha256={h: d["sha"] for h, d in dirs.items()}, family_size_total=fam_total, user_decision_required=True))
            jdump(cand, os.path.join(OUTDIR, f"candidate_{tf}.json")); log(f"[combine {tf}] go/no-go PASSED: candidate_{tf}.json written (user decision: vocabulary outside the frozen shortlist)")
    results["null_result"] = not any(v["go_no_go"] and v["go_no_go"]["passed"] for v in results["timeframes"].values())
    results["ledger_sha_after"] = H.ledger_sha(); results["runtime_s"] = round(time.time() - t0, 1)
    jdump(results, os.path.join(OUTDIR, "results_round1.json"))
    write_csvs(results); write_findings_draft(results)
    log(f"combine done in {results['runtime_s']} s; null_result {results['null_result']}; ledger {results['ledger_sha_before']} -> {results['ledger_sha_after']}")
    return results


# ---------------------------------------------------------------- outputs
KEYS = ["kept_n", "skipped_n", "kept_share", "kept_mean", "skipped_mean", "diff", "diff_top1_removed", "perm_p", "control_pct", "loser_recall", "loser_precision", "winner_recall_weighted", "top_decile_winners_skipped", "kept_mean_slip8", "sign_blocks"]


def write_csvs(results):
    for tf in C.TFS:
        rows = []
        for h, s in results["scores"].items():
            st = s["timeframes"][tf]
            for p in st["rules"]:
                r = dict(direction=f"{h}->{C.OTHER[h]}", id=p["id"], rule=json.dumps(p["rule"]), refused=p["refused"], flags="; ".join(p["check"]["flags"]), protocol_clean=p["protocol_clean"], untestable=p.get("untestable"))
                if not p["refused"]:
                    r.update(ledger_id=p["L1"]["id"], **{k: p["L1"].get(k) for k in KEYS}, L0_diff=p["L0"]["diff"], L0_control_pct=p["L0"]["control_pct"], maxt_t=p.get("maxt_t"), maxt_fw_p=p.get("maxt_fw_p"), holm_p_round=p.get("holm_p_round"), holm_p_family=p.get("holm_p_family"),
                             boot_diff_ci=json.dumps(p["boot"]["diff_ci"]) if p.get("boot") else None, blocks_positive=p["blocks"]["blocks_positive"], blocks_defined=p["blocks"]["blocks_defined"], dsr_p=(p.get("dsr") or {}).get("p"))
                rows.append(r)
            if st.get("union"): rows.append(dict(direction=f"{h}->{C.OTHER[h]}", id="union_round1", ledger_id=st["union"]["L1"]["id"], **{k: st["union"]["L1"].get(k) for k in KEYS}))
            for x in st["round0"]: rows.append(dict(direction=f"{h}->{C.OTHER[h]}", id=x["id"] + " (round 0)", rule=json.dumps(x["rule"]), ledger_id=x["L1"]["id"], **{k: x["L1"].get(k) for k in KEYS}))
        cf = results["timeframes"][tf]
        for name, r in cf["rows"].items(): rows.append(dict(direction="crossfit (all IS rows)", id=name, ledger_id=r["id"], **{k: r.get(k) for k in KEYS}))
        pd.DataFrame(rows).to_csv(os.path.join(OUTDIR, f"scores_{tf}.csv"), index=False)


def f(v, nd=2):
    return "n/a" if v is None else (f"{v:,.{nd}f}" if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v))


def write_findings_draft(R):
    L = [f"# llm_round1: FINDINGS (draft written by scorer.py at {R['combined_at']}; the step-3 agent completes it into FINDINGS.md / findings.json)", ""]
    L.append(f"**Directions scored**: {', '.join(f'{h} -> {C.OTHER[h]}' for h in R['directions_present'])}. Holm over the rules of the round: m = {R['holm']['m']}. Eligibility: {R['eligibility_rule']}. Greedy: {R['greedy_rule']}. **null_result = {R['null_result']}** (harness.go_no_go on the fixed crossed list, with the CPCV item).")
    L.append("")
    L.append("## Definitions"); L.append(""); L.append("```"); L.append(__doc__.strip()); L.append("```"); L.append("")
    for tf in C.TFS:
        L.append(f"## {tf}"); L.append("")
        for h in R["directions_present"]:
            st = R["scores"][h]["timeframes"][tf]; o = C.OTHER[h]
            L.append(f"### Rules proposed on the tables of half {h}, scored on half {o} ({st['n_rows_scored']:,} L1 units in {st['n_sessions_scored']} sessions; all-rows mean {f(st['all_mean_L1'])} INR; labelled cells seen {st['max_t']['n_cells_labelled']}, family size {st['max_t']['family_size']}, max-T null p95 of max |t| {f(st['max_t']['null_max_abs_t_p95'], 3)}, best family member `{st['max_t'].get('best_family_member_name')}` |t| {f(st['max_t'].get('best_family_abs_t'), 3)})")
            L.append("")
            L.append("| id | rule | protocol | ledger id | kept n | skipped n | kept mean | skipped mean | diff | diff top1% off | perm p | Holm p (round) | max-T fw p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | blocks +/def | boot 90% CI | L0 diff | DSR p |")
            L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for p in st["rules"]:
                rule = " and ".join(f"`{c[0]} {c[1]} {c[2]}`" for c in p["rule"])
                if p["refused"]:
                    L.append(f"| {p['id']} | {rule} | REFUSED: {p['check']['refused']} | - | - | - | - | - | - | - | - | 1.0 | 1.0 | - | - | - | - | - | - | - | - | - |"); continue
                m = p["L1"]; prot = "clean" if p["protocol_clean"] else "; ".join(p["check"]["flags"])
                L.append(f"| {p['id']}{' (untestable)' if p.get('untestable') else ''} | {rule} | {prot} | {m['id']} | {m['kept_n']} | {m['skipped_n']} | {f(m['kept_mean'])} | {f(m['skipped_mean'])} | {f(m['diff'])} | {f(m['diff_top1_removed'])} | {f(m['perm_p'], 4)} | {f(p.get('holm_p_round'), 4)} | {f(p.get('maxt_fw_p'), 4)} | {f(m['control_pct'], 1)} | {f(m['loser_recall'], 3)} | {f(m['winner_recall_weighted'], 3)} | {f(m['top_decile_winners_skipped'], 3)} | {f(m['kept_mean_slip8'])} | {p['blocks']['blocks_positive']}/{p['blocks']['blocks_defined']} | {p['boot']['diff_ci'] if p.get('boot') else 'n/a'} | {f(p['L0']['diff'])} | {f((p.get('dsr') or {}).get('p'), 4)} |")
            if st.get("union"):
                m = st["union"]["L1"]; L.append(f"| union (round 1) | all scored rules | - | {m['id']} | {m['kept_n']} | {m['skipped_n']} | {f(m['kept_mean'])} | {f(m['skipped_mean'])} | {f(m['diff'])} | {f(m['diff_top1_removed'])} | {f(m['perm_p'], 4)} | - | - | {f(m['control_pct'], 1)} | {f(m['loser_recall'], 3)} | {f(m['winner_recall_weighted'], 3)} | {f(m['top_decile_winners_skipped'], 3)} | {f(m['kept_mean_slip8'])} | {st['union']['blocks']['blocks_positive']}/{st['union']['blocks']['blocks_defined']} | {st['union']['boot']['diff_ci']} | - | - |")
            L.append("")
            L.append("Round-0 rules on the same rows (family `llm_round1/" + h + "/round0`): " + "; ".join(f"{x['id']} diff {f(x['L1']['diff'])} ctrl {f(x['L1']['control_pct'], 1)} (`{x['L1']['id']}`)" for x in st["round0"]))
            fm = st["family"]
            L.append(f"Direction family ({fm.get('vectors')} vectors): PBO(diff) {f((fm.get('pbo_diff') or {}).get('pbo'), 4)}, PBO(kept mean) {f((fm.get('pbo_kept_mean') or {}).get('pbo'), 4)}, SPA p {f((fm.get('spa') or {}).get('spa_p'), 4)} (RC p {f((fm.get('spa') or {}).get('rc_p'), 4)}; unstudentised {f((fm.get('spa') or {}).get('spa_p_unstudentised'), 4)}), effective trials {fm.get('effective_trials')}.")
            drift_notes = [(p["id"], d) for p in st["rules"] if not p["refused"] for d in p.get("drift", [])]
            if drift_notes: L.append("Drift caveats: " + "; ".join(f"{i}: {d['column']} ({d['caveat']}" + (f"; refit without it diff {f(d['refit_diff'])} ctrl {f(d['refit_control_pct'], 1)} `{d['refit_ledger_id']}`" if 'refit_diff' in d else "") + ")" for i, d in drift_notes))
            L.append("")
        cf = R["timeframes"][tf]
        L.append(f"### Cross-fitted verdict ({tf}; family size of the round {cf['family_size_total']})"); L.append("")
        for h, o in cf["outer"].items():
            L.append(f"- Direction {h} -> {C.OTHER[h]}: eligible {[e['id'] for e in o['eligibility'] if e['eligible']]}; greedy list L_{h} = {o['L']}" + (f"; steps {[(s['added'], s['diff'], s.get('marginal_diff'), s['accepted'], s['ledger_id']) for s in o['steps']]}" if o["steps"] else ""))
        L.append("")
        if cf["rows"]:
            L.append("| row | ledger id | kept n | skipped n | kept share | diff | diff top1% off | perm p | control pct | loser recall | winner recall (w) | top-decile skipped | slip8 kept mean | sign blocks |")
            L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for name, m in cf["rows"].items():
                L.append(f"| {name} | {m['id']} | {m['kept_n']} | {m['skipped_n']} | {f(m['kept_share'], 4)} | {f(m['diff'])} | {f(m['diff_top1_removed'])} | {f(m['perm_p'], 4)} | {f(m['control_pct'], 1)} | {f(m['loser_recall'], 3)} | {f(m['winner_recall_weighted'], 3)} | {f(m['top_decile_winners_skipped'], 3)} | {f(m['kept_mean_slip8'])} | {m['sign_blocks']} |")
            L.append("")
        d = cf["cpcv"]
        L.append(f"CPCV (nested selection per test block, 66 splits, 11 paths, family `llm_round1/crossfit/cpcv`): blocks with a non-empty selection {cf['cpcv_blocks_with_selection']} of 132; diff median {f(d['diff_median'])}, p5 {f(d['diff_p5'])}, min {f(d['diff_min'])}, share > 0 {f(d['diff_share_positive'], 3)}, kept share median {f(d['kept_share_median'], 4)}, control pct median {f(d.get('control_pct_median'), 1)} / p5 {f(d.get('control_pct_p5'), 1)}.")
        L.append(f"12-block OOF selections: " + "; ".join(f"{b}: {v['proposer']} -> {v['chosen']}" for b, v in cf["oof12_selection"].items()))
        fm = cf["family"]
        L.append(f"Crossfit family ({fm.get('vectors')} vectors): PBO(diff) {f((fm.get('pbo_diff') or {}).get('pbo'), 4)}, SPA p {f((fm.get('spa') or {}).get('spa_p'), 4)}, effective trials {fm.get('effective_trials')}.")
        g = cf["go_no_go"]
        if g: L.append(f"go/no-go: **{'PASS' if g['passed'] else 'fail'}** " + ", ".join(f"{k} {'ok' if v[0] else 'FAIL'} ({v[1]})" for k, v in g["checks"].items()) + (f"; {g['note']}" if g.get("note") else "") + f"; DSR p {f((g.get('dsr') or {}).get('p'), 4)}" + (f"; bootstrap 90% CI of the diff {g['boot']['diff_ci']}" if g.get("boot") else ""))
        L.append("")
    L.append("## Files"); L.append("")
    for x in sorted(os.listdir(OUTDIR)):
        if x.endswith((".json", ".csv", ".md", ".py", ".log")): L.append(f"- `studies/llm_round1/{x}`")
    open(os.path.join(OUTDIR, "FINDINGS_draft.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- smoke test (redirected ledger; synthetic rules; never a finding)
def smoke(n_jobs, relax=False):
    global OUTDIR, _LOG, ALPHA, CONTROL_MIN
    if relax: ALPHA, CONTROL_MIN = 2.0, 0.0          # smoke only: every rule with diff > 0 is eligible (p < 2 always holds), so the selection / crossfit path runs
    scratch = os.environ.get("R1_SMOKE_DIR") or os.path.join(os.path.expanduser("~"), ".r1_smoke")
    scratch = os.path.abspath(scratch); os.makedirs(os.path.join(scratch, "ledger", "vectors"), exist_ok=True)
    OUTDIR = scratch; _LOG = None
    H.LEDGER = os.path.join(scratch, "ledger"); C.REGISTRATIONS = os.path.join(scratch, "ledger", "registrations.jsonl")
    import functools
    _score, _metrics = H.score, H.metrics
    H.score = functools.wraps(_score)(lambda *a, **k: _score(*a, **dict(k, draws=100)))
    H.metrics = functools.wraps(_metrics)(lambda *a, **k: _metrics(*a, **dict(k, draws=100)))
    global MAXT_DRAWS; MAXT_DRAWS = 100
    log(f"=== SMOKE TEST {C.now()}: ledger redirected to {H.LEDGER}; controls 100 draws, max-T 100 draws; synthetic rules; relaxed eligibility {relax}; NOTHING HERE IS A FINDING ===")
    # copy the tables (the scorer reads them from HERE) and build synthetic rule files from the printed edges
    tabs_T = {tf: (C.load_tf(tf), C.load_tf(tf, "L0")) for tf in C.TFS}
    files = []
    for h in C.HALVES:
        J = dict(round=1, half_seen=h, written_at=C.now(), inputs_read=["synthetic smoke test"], synthetic=True)
        for tf in C.TFS:
            tj, _, _ = load_tables(tf, h); voc = {v["column"]: v for v in tj["vocabulary"] if v.get("column")}
            rules = [dict(id=f"s{h}_{tf}_1", **{"if": [["fz_read", "in", ["THIN", "REJECT"]], ["hour_bin", "in", ["11", "12"]]]}, then="skip", reason="synthetic"),
                     dict(id=f"s{h}_{tf}_2", **{"if": [["n_choch_since_bos", ">=", 2], ["dir", "==", "up"]]}, then="skip", reason="synthetic"),
                     dict(id=f"s{h}_{tf}_3", **{"if": [["n_events_asof", ">", 100]]}, then="skip", reason="synthetic time proxy (must be refused)"),
                     dict(id=f"s{h}_{tf}_4", **{"if": [["hv3_dir_agree", "==", False], ["hv3_bars_since", "<=", voc["hv3_bars_since"]["allowed_thresholds"][2]]]}, then="skip", reason="synthetic"),
                     dict(id=f"s{h}_{tf}_5", **{"if": [["room_ahead_dist_atr", "<", 0.1234]]}, then="skip", reason="synthetic off-edge threshold (must be flagged)")]
            J[tf] = rules
        p = os.path.join(scratch, f"rules_round1_{h}.json"); jdump(J, p); files.append(p)
    for p in files:
        J = load_rules(p); score_direction(p, J, tabs_T, smoke=True)
    combine(tabs_T, draws_ctrl=100, n_jobs=n_jobs)
    log(f"smoke test done; outputs in {scratch}; the real ledger {os.path.join(C.OUT, 'ledger')} was not touched")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["score", "combine", "all", "smoke"])
    ap.add_argument("--rules", nargs="*", default=[], help="round-1 rules JSON file(s) (each with half_seen A or B)")
    ap.add_argument("--n-jobs", type=int, default=4)
    ap.add_argument("--relax", action="store_true", help="smoke only: eligibility thresholds off, to exercise the selection path")
    a = ap.parse_args()
    if a.stage == "smoke": smoke(a.n_jobs, a.relax); return
    log(f"=== scorer.py {a.stage} {C.now()} ===")
    tabs_T = {tf: (C.load_tf(tf), C.load_tf(tf, "L0")) for tf in C.TFS}
    if a.stage in ("score", "all"):
        assert a.rules, "--rules <file> required"
        for p in a.rules:
            p = os.path.abspath(p); J = load_rules(p); score_direction(p, J, tabs_T)
    if a.stage in ("combine", "all"): combine(tabs_T, n_jobs=a.n_jobs)


if __name__ == "__main__":
    main()
