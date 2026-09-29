"""Step (8): the frozen shortlist per timeframe from results_<tf>.json, its registration in the ledger, FINDINGS.md and findings.json.
python shortlist.py            (both timeframes must have run; refuses to register twice)."""
import os, sys, json, hashlib, datetime as D
import numpy as np, pandas as pd
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imp_lib as L
import harness as H

OUT = L.OUT
TFS = ("minute", "5minute")
DRY = "--dry" in sys.argv                     # debugging of this writer on dry/ outputs: no registration, files under dry/
SRC = os.path.join(HERE, "dry") if DRY else HERE
def _src(tf, name):
    p = os.path.join(SRC, name.format(tf=tf))
    return p if (os.path.exists(p) or not DRY) else os.path.join(SRC, name.format(tf="5minute"))
R = {tf: json.load(open(_src(tf, "results_{tf}.json"))) for tf in TFS}
CL = {tf: json.load(open(_src(tf, "clusters_{tf}.json"))) for tf in TFS}
TAB = {tf: pd.read_csv(_src(tf, "importance_clusters_{tf}.csv")) for tf in TFS}
FEAT = {tf: pd.read_csv(_src(tf, "importance_features_{tf}.csv")) for tf in TFS}
defs, card_def, fz_def = L.readme_defs()
for tf in TFS: assert R[tf]["dry"] == DRY, tf


def fmt(v, nd=2):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "-"
    if isinstance(v, (bool, np.bool_)): return "yes" if v else "no"
    if isinstance(v, (int, np.integer)): return str(int(v))
    return f"{v:.{nd}f}"


# ---------------------------------------------------------------- the shortlist
shortlists, reg_lines = {}, []
for tf in TFS:
    t = TAB[tf]; res = R[tf]; clusters = {int(k): v for k, v in CL[tf]["clusters"].items()}; reps = {int(k): v for k, v in CL[tf]["representatives"].items()}
    pnames = sorted(res["stability"]["periods"])
    elig = t[t.shortlist_eligible].sort_values("mda_ll_mean", ascending=False).head(8)
    entries = []
    for _, r in elig.iterrows():
        ci = int(r.cluster); rep = reps[ci]["representative"]; d = L.define(rep, defs, card_def, fz_def)
        entries.append(dict(rank=int(r.mda_rank), cluster=ci, representative=rep, representative_tier=int(reps[ci]["tier"]), representative_why=reps[ci]["why"],
                            definition=d, members=clusters[ci],
                            member_definitions={c: L.define(c, defs, card_def, fz_def)["definition"] for c in clusters[ci]},
                            mda_ll_mean=float(r.mda_ll_mean), mda_ll_std=float(r.mda_ll_std), mda_ll_ratio=float(r.mda_ll_ratio),
                            mda_diff_mean=float(r.mda_diff_mean), mda_diff_std=float(r.mda_diff_std), mdi=float(r.mdi),
                            sfi=dict(oof_wlogloss=float(r.sfi_oof_wlogloss), oof_auc=float(r.sfi_oof_auc), gate_diff=None if pd.isna(r["diff"]) else float(r["diff"]),
                                     kept_share=None if pd.isna(r.kept_share) else float(r.kept_share), control_pct=None if pd.isna(r.control_pct) else float(r.control_pct),
                                     ledger_id=r.ledger_id),
                            per_period_rank={pn: int(r[f"rank_{pn}"]) for pn in pnames}, stab_top8_periods=int(r.stab_top8_periods)))
    allowed = sorted({c for e in entries for c in e["members"]})
    pairs = res["interactions"]["top5"]
    sl = dict(kind="feature_shortlist", tf=tf, label="L1", is_window="2021-10-01..2025-12-31", frozen_at=D.datetime.now().isoformat(timespec="seconds"),
              study="importance", script="studies/importance/run_importance.py + shortlist.py",
              rule=dict(mda="cluster mean permutation drop in OOF weighted log-loss > its std across the 12 purged folds (5 joint permutations per fold)",
                        stability=res["stability"]["rule"], cap=8, model=res["full_model"]["config"]),
              n_clusters_total=int(len(t)), n_clusters_mda_pass=int(t.mda_ll_pass.sum()), n_clusters_stability_pass=int(t.stab_pass.sum()),
              n_clusters_eligible=int(t.shortlist_eligible.sum()), n_shortlisted=len(entries),
              clusters=entries, allowed_columns=allowed,
              interaction_pairs_top5=pairs,
              interaction_rule="the gate studies may use depth-2/3 conjunctions only over these 5 pairs (both features must be allowed columns); the split points are xgboost path split points, gain-weighted medians over the 12 fold boosters",
              interaction_pairs_within_allowed=[p for p in pairs if p["feature_a"] in allowed and p["feature_b"] in allowed],
              ffd_verdict=None, h2_vs_state_models=res["h2_vs_states"], ledger_family_rows=res["family"]["ledger_rows"] if res["family"] else None)
    shortlists[tf] = sl

# FFD verdict needs both timeframes
ffd_pass = {tf: any(c["mda_ll_pass"] for c in R[tf]["ffd"]["clusters"].values()) for tf in TFS}
ffd_mixed = {tf: {ci: c["mixed_with_non_ffd"] for ci, c in R[tf]["ffd"]["clusters"].items()} for tf in TFS}
ffd_verdict = ("adopted (clustered MDA > 1 std on both timeframes; adoption needs a per-bar FFD routine in fz code, a new key type: user decision)"
               if all(ffd_pass.values()) else f"FFD not adopted (clustered MDA <= 1 std on {', '.join(tf for tf in TFS if not ffd_pass[tf])})")
for tf in TFS:
    shortlists[tf]["ffd_verdict"] = dict(verdict=ffd_verdict, mda_pass_by_tf=ffd_pass, ffd_clusters_by_tf={t: R[t]["ffd"]["clusters"] for t in TFS},
                                        ffd_keys_if_adopted=dict(ffd_d_close=0.2, ffd_d_vol=0.1, ffd_window_bars_close=497, ffd_window_bars_vol=503, ffd_weight_cut=1e-4, ffd_z_window=60,
                                                                 source="learned:quant-ml-canon-feature-importance") if all(ffd_pass.values()) else None)

# write + register
regs_path = os.path.join(OUT, "ledger", "registrations.jsonl")
existing = [json.loads(x) for x in open(regs_path, encoding="utf-8") if x.strip()] if os.path.exists(regs_path) else []
for tf in TFS:
    d = os.path.join(SRC, "features_shortlist", tf) if DRY else os.path.join(OUT, "features_shortlist", tf); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "shortlist.json")
    if not DRY and any(e.get("what") == f"feature shortlist {tf}" for e in existing):
        print(f"{tf}: already registered; not rewriting {p}"); shortlists[tf]["sha256"] = hashlib.sha256(open(p, "rb").read()).hexdigest(); continue
    json.dump(shortlists[tf], open(p, "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest(); shortlists[tf]["sha256"] = sha
    if DRY: print(f"{tf}: DRY shortlist written to {p} (not registered)"); continue
    rec = dict(kind="pre_registration", what=f"feature shortlist {tf}", file=f"features_shortlist/{tf}/shortlist.json", sha256=sha,
               registered_at=D.datetime.now().isoformat(timespec="seconds"), note="frozen before any gate search",
               n_clusters=len(shortlists[tf]["clusters"]), n_allowed_columns=len(shortlists[tf]["allowed_columns"]), interaction_pairs=5,
               ledger_sha_at_registration=H.ledger_sha())
    with open(regs_path, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")
    print(f"{tf}: registered {p} sha256 {sha}")

# ---------------------------------------------------------------- FINDINGS.md
M = []
M.append("# importance: FINDINGS (DESIGN_PANEL quant-ml-canon-feature-importance, both judges' fixes)\n")
M.append("**What this study is.** The feature-vocabulary pass: which clusters of as-of columns (base design + the 61 extended columns handed here by the "
         "regime-breaks, regime-states, motif-shapelet and rocket-probe judges) carry information about the L1 outcome under the harness splitter; the "
         "shortlist of at most 8 clusters per timeframe that the gate studies may draw features from, frozen in the ledger before any gate search; the FFD "
         "verdict; the five interaction pairs that are the only depth-2/3 conjunctions allowed downstream. This study proposes **no gate**: the only kept-vs-skipped "
         "numbers are the ledger rows of the OOF gates it had to evaluate (the full bagged model at its training-fold tau, each SFI cluster at its tau, the CPCV paths "
         "of the full model), reported as ceilings, never as candidates. IS only.\n")
M.append("## Definitions (fixed before the numbers)\n")
M.append("```\n" + L.__doc__.strip() + "\n```\n")
M.append(f"Constants: trees {L.N_TREES}, min_weight_fraction_leaf {L.MIN_LEAF}, main depth {L.DEPTH_MAIN} (sensitivity {L.DEPTHS_SENS}), permutations per fold {L.N_PERM}, "
         f"tau grid {L.TAU_GRID[0]}..{L.TAU_GRID[-1]} step 0.01, weighted winner recall floor {L.WREC_MIN}, silhouette range {min(L.K_RANGE)}..{max(L.K_RANGE)} clusters, "
         f"stability top-{L.TOP_K_STAB}, interactions on the top-{L.TOP_INTER} features, {L.TOP_PAIRS} pairs; xgboost depth {L.XGB_DEPTH}, {L.XGB_ROUNDS} rounds, eta {L.XGB_ETA}. "
         "Every model fit uses `harness.purged_splits` (12 blocks, purge by the L1 exit bar, 3-session embargo); nothing is fitted on OOS rows; OOS labels and features are never read.\n")

for tf in TFS:
    res, t, meta = R[tf], TAB[tf], R[tf]["meta"]
    pnames = sorted(res["stability"]["periods"])
    M.append(f"\n## {tf}\n")
    M.append("### Feature set\n")
    M.append("| item | value |\n|---|---|")
    M.append(f"| L1 units (IS) | {meta['n_units']} ({meta['n_is']}) |")
    M.append(f"| base design columns (harness.design) | {meta['base_design_cols']} (text column dropped by design, > 16 levels: {', '.join('`' + c + '`' for c in meta['text_cols_dropped_by_design'])}) |")
    M.append(f"| extended columns | {meta['ext_cols']} |")
    M.append(f"| dropped, > 40% NaN on IS | {len(meta['dropped_nan_gt_40pct'])}: " + ", ".join(f"`{c}` {v:.3f}" for c, v in sorted(meta['dropped_nan_gt_40pct'].items(), key=lambda z: -z[1])) + " |")
    M.append(f"| dropped, constant on IS | {len(meta['dropped_constant'])}: " + ", ".join(f"`{c}`" for c in meta['dropped_constant']) + " |")
    M.append(f"| dropped, second level of a two-level one-hot | {len(meta['dropped_second_level_of_binary_onehot'])}: " + ", ".join(f"`{c}`" for c in meta['dropped_second_level_of_binary_onehot']) + " |")
    dd = meta.get("dropped_duplicates", {})
    M.append(f"| dropped, exact duplicate (|Spearman| > 0.999) | {len(dd)}: " + ", ".join(f"`{c}` = `{k}`" for c, k in dd.items()) + " |")
    M.append(f"| missing indicators (one per NaN pattern) | {len(meta['missing_indicators'])}: " + ", ".join(f"`{k}` ({len(v)} cols)" for k, v in meta['missing_indicators'].items()) + " |")
    M.append(f"| **features in the model** | **{meta['n_features_final']}** |")
    M.append(f"| clustering | silhouette best k = {res['clustering']['k_best']} ({res['clustering']['silhouette'][str(res['clustering']['k_best'])]}), clusters formed {res['clustering']['n_clusters']} |")
    M.append(f"| runtime / max RSS | {res['runtime_s']} s / {res['max_rss_mb']} MB |\n")

    fm = res["full_model"]; g = fm["gate"]
    M.append("### The full bagged model (ceiling; not a candidate)\n")
    M.append("| depth | OOF weighted log-loss | OOF AUC | gate kept n | kept share | kept mean | skipped mean | diff | diff top-1% removed | perm p | control pct | loser recall | weighted winner recall | top-decile winners skipped | sign blocks | kept mean slip 8 | ledger id |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    M.append(f"| {fm['config']['depth']} (main) | {fm['oof_wlogloss']} | {fm['oof_auc']} | {g['kept_n']} | {g['kept_share']} | {g['kept_mean']} | {g['skipped_mean']} | {g['diff']} | {g['diff_top1_removed']} | {g['perm_p']} | {g['control_pct']} | {g['loser_recall']} | {g['winner_recall_weighted']} | {g['top_decile_winners_skipped']} | {g['sign_blocks']} | {g['kept_mean_slip8']} | `{fm['ledger_id']}` |")
    for d, s in fm["depth_sensitivity"].items():
        M.append(f"| {d} | {s['oof_wlogloss']} | {s['oof_auc']} | - | {s['kept_share']} | - | - | {s['diff']} | - | {s['perm_p']} | {s['control_pct']} | - | - | - | - | - | `{s['ledger_id']}` |")
    M.append("")
    M.append("Per fold (depth 4): tau chosen on the training fold's OOB probabilities.\n")
    M.append("| fold | n train | n test | |net| cap (train p99) | tau | OOF weighted log-loss | OOF diff | kept share |\n|---|---|---|---|---|---|---|---|")
    for f in fm["folds"]: M.append(f"| {f['fold']} | {f['n_tr']} | {f['n_te']} | {f['cap_p99']} | {f['tau']} | {f['oof_wlogloss']} | {fmt(f['oof_diff'])} | {fmt(f['kept_share'], 4)} |")
    c = fm["cpcv"]
    if c:
        M.append(f"\nCPCV of the full model's OOF gate (66 splits, 11 paths, family `importance/full_model/cpcv`): diff median {c['diff_median']}, 5th percentile {c['diff_p5']}, min {c['diff_min']}, "
                 f"share of paths with diff > 0 {c['diff_share_positive']}, kept share median {c['kept_share_median']}, control pct median {c.get('control_pct_median')} / p5 {c.get('control_pct_p5')}.\n")
    else:
        M.append("\nCPCV: not run (dry mode).\n")
    fam = res["family"]
    if fam:
        sp = fam["spa"] or {}
        M.append(f"Family `importance/*` on {tf} ({fam['ledger_rows']} ledger rows: full model x3 depths, {fam['ledger_rows'] - 3 - 11} SFI clusters, 11 CPCV paths): PBO (diff) {fam['pbo']['pbo']} "
                 f"(IS-best below zero OOS {fam['pbo']['oos_best_below_zero']}); SPA studentised p {sp.get('spa_p')} (RC p {sp.get('rc_p')}, best mean gain {sp.get('best_mean_gain')} INR/session, "
                 f"{sp.get('excluded_from_studentised')} candidates excluded for < {sp.get('min_active_sessions')} active sessions), SPA unstudentised p {sp.get('spa_p_unstudentised')} (RC p {sp.get('rc_p_unstudentised')}, "
                 f"best mean gain {sp.get('best_mean_gain_unstudentised')}); effective trials {fam['effective_trials']}; "
                 f"full model: bootstrap 90% CI of diff {fam['bootstrap_full']['diff_ci']}, DSR p {fam['dsr_full'].get('p')}; go/no-go passed = {fam['go_no_go_full']['passed']} "
                 f"({', '.join(k + ('=ok' if v[0] else '=FAIL') for k, v in fam['go_no_go_full']['checks'].items())}).\n")

    M.append("### Clustered importance table (all clusters, sorted by log-loss MDA)\n")
    M.append(f"Full table with members, per-period MDA values and SFI ledger ids: `importance_clusters_{tf}.csv`; per-feature MDI, tier, coverage and README definition: `importance_features_{tf}.csv`.\n")
    hdr = "| rank | cluster | representative | n | MDA ll mean | std | ratio | pass | MDA diff mean | std | pass | MDI | SFI ll | SFI AUC | SFI diff | SFI kept | SFI ctrl pct | " + " | ".join(f"rank {pn}" for pn in pnames) + " | top-8 periods | stable | eligible |"
    M.append(hdr); M.append("|" + "---|" * (hdr.count("|") - 1))
    for _, r in t.iterrows():
        M.append(f"| {r.mda_rank} | {r.cluster} | `{r.representative}` | {r.n_members} | {r.mda_ll_mean:.5f} | {r.mda_ll_std:.5f} | {fmt(r.mda_ll_ratio)} | {fmt(r.mda_ll_pass)} | {fmt(r.mda_diff_mean, 1)} | {fmt(r.mda_diff_std, 1)} | {fmt(r.mda_diff_pass)} | {r.mdi:.4f} | {r.sfi_oof_wlogloss:.4f} | {r.sfi_oof_auc:.3f} | {fmt(r['diff'], 1)} | {fmt(r.kept_share, 3)} | {fmt(r.control_pct, 1)} | "
                 + " | ".join(str(int(r[f'rank_{pn}'])) for pn in pnames) + f" | {int(r.stab_top8_periods)} | {fmt(r.stab_pass)} | {fmt(r.shortlist_eligible)} |")
    st = res["stability"]
    M.append(f"\nStability: periods " + ", ".join(f"{pn} ({v['n_rows']} rows, {v['n_winners']} winners)" for pn, v in st["periods"].items()) + f"; rule {st['rule']}; Spearman rank correlation of the cluster MDA vectors across periods: "
             + ", ".join(f"{k}: {v}" for k, v in st["rank_corr"].items()) + ".\n")
    pc = res["pca_check"]
    M.append(f"Orthogonal check: {pc['n_components']} components ({pc['n_components_95pct']} carry 95% of the variance); weighted Kendall tau between the MDI of the PC-score forest and the eigenvalues = **{pc['weighted_kendall_tau']}** "
             f"(Kendall tau {pc['kendall_tau']}, p {pc['kendall_p']:.3g}). " + ("A low tau is the AFML warning that the importance ranking may be fitting noise rather than variance-bearing directions." if pc['weighted_kendall_tau'] < 0.3 else "The MDI ranking follows the variance structure of the features.") + "\n")

    M.append("### Cluster membership\n")
    M.append("| cluster | representative (tier; why) | members |\n|---|---|---|")
    for ci in sorted({int(k) for k in CL[tf]["clusters"]}):
        rp = CL[tf]["representatives"][str(ci)]
        M.append(f"| {ci} | `{rp['representative']}` ({rp['why']}) | " + ", ".join(f"`{c}`" for c in CL[tf]["clusters"][str(ci)]) + " |")
    M.append("")

    it = res["interactions"]
    M.append(f"### Interactions (xgboost on the top-{L.TOP_INTER} features by clustered MDA; OOF weighted log-loss {it['xgb_oof_wlogloss']}, OOF AUC {it['xgb_oof_auc']})\n")
    M.append("| rank | feature a | feature b | mean abs SHAP interaction (OOF rows) | paths with both | split a (gain-weighted median) | split b | common splits a | common splits b |\n|---|---|---|---|---|---|---|---|---|")
    for i, p in enumerate(it["top5"], 1):
        M.append(f"| {i} | `{p['feature_a']}` | `{p['feature_b']}` | {p['mean_abs_interaction']:.6f} | {p['n_paths_with_both']} | {fmt(p.get('split_a_gain_weighted_median'), 4)} | {fmt(p.get('split_b_gain_weighted_median'), 4)} | {p.get('split_a_common')} | {p.get('split_b_common')} |")
    M.append(f"\nAll ranked pairs: `interaction_pairs_{tf}.csv`; the full mean |interaction| matrix: `shap_interactions_{tf}.csv`. The gate studies may use only these five pairs as depth-2/3 conjunctions (and only where both features are shortlisted columns: "
             + (", ".join(f"`{p['feature_a']}` x `{p['feature_b']}`" for p in shortlists[tf]['interaction_pairs_within_allowed']) or "none of the five lies inside the shortlist") + ").\n")

    hs = res["h2_vs_states"]
    M.append("### Do the H2 CHoCH counts and the state-model posteriors share a cluster?\n")
    M.append("| H2 count column | cluster |\n|---|---|"); M += [f"| `{c}` | {ci} |" for c, ci in hs["h2_clusters"].items()]
    M.append("\n| state-model column | cluster |\n|---|---|"); M += [f"| `{c}` | {ci} |" for c, ci in hs["state_clusters"].items()]
    if hs["shared"]:
        M.append("\n**Yes, in part**: " + "; ".join(f"cluster {ci} holds " + ", ".join(f"`{c}`" for c in cs) for ci, cs in hs["shared"].items()) + ". Where an HMM / GMM / jump posterior sits in the same cluster as `n_choch_since_bos`, the state model adds nothing the count does not already say (Judge 1 of regime-states): no HMM gate is run later for those states.\n")
    else:
        M.append("\n**No**: no state-model column shares a cluster with an H2 count column on this timeframe.\n")
    ff = res["ffd"]
    M.append("### FFD columns\n")
    M.append("| ffd column | cluster |\n|---|---|"); M += [f"| `{c}` | {ci} |" for c, ci in ff["columns"].items()]
    M.append("\n| cluster | members | MDA ll mean | std | pass | stable | mixed with non-FFD columns |\n|---|---|---|---|---|---|---|")
    for ci, c in ff["clusters"].items(): M.append(f"| {ci} | {', '.join('`' + m + '`' for m in c['members'])} | {c['mda_ll_mean']:.5f} | {c['mda_ll_std']:.5f} | {fmt(c['mda_ll_pass'])} | {fmt(c['stab_pass'])} | {fmt(c['mixed_with_non_ffd'])} |")
    M.append("")

    sl = shortlists[tf]
    M.append(f"### The shortlist ({sl['n_shortlisted']} clusters; {sl['n_clusters_mda_pass']} of {sl['n_clusters_total']} pass MDA, {sl['n_clusters_stability_pass']} pass stability, {sl['n_clusters_eligible']} pass both; cap 8)\n")
    M.append(f"Frozen at `features_shortlist/{tf}/shortlist.json`, sha256 `{sl['sha256']}`, registered in `ledger/registrations.jsonl`. Allowed columns for the gate studies: {len(sl['allowed_columns'])}.\n")
    if sl["clusters"]:
        M.append("| # | cluster | representative | definition (README) | members | MDA ll mean / std | MDA diff mean / std | " + " / ".join(pnames) + " ranks |\n|---|---|---|---|---|---|---|---|")
        for e in sl["clusters"]:
            M.append(f"| {e['rank']} | {e['cluster']} | `{e['representative']}` ({e['representative_why']}) | {e['definition']['definition']} ({e['definition']['readme']}) | " + ", ".join(f"`{c}`" for c in e['members'])
                     + f" | {e['mda_ll_mean']:.5f} / {e['mda_ll_std']:.5f} | {e['mda_diff_mean']:.1f} / {e['mda_diff_std']:.1f} | " + " / ".join(str(e['per_period_rank'][pn]) for pn in pnames) + " |")
    else:
        M.append("**Empty**: no cluster passes both the MDA rule and the stability filter on this timeframe. The gate studies have no shortlisted column here; a null vocabulary is a result, not a failure of the pipeline.")
    M.append("")

M.append("\n## FFD verdict (both timeframes)\n")
M.append(f"**{ffd_verdict}.** MDA pass of the cluster(s) holding the `ffd_*` columns: " + ", ".join(f"{tf}: {'yes' if ffd_pass[tf] else 'no'} (mixed with non-FFD columns: {ffd_mixed[tf]})" for tf in TFS)
         + ". The rule (Judge 2): adopted only if the FFD cluster's MDA > 1 std on BOTH timeframes; adoption would need a per-bar FFD routine in fz code (a new key type, a user decision) with keys d* close 0.2 / volume 0.1, weight cut 1e-4, windows 497 / 503 bars, z-window 60.\n")

M.append("## What would falsify these findings\n")
M.append("- A shortlisted cluster whose MDA sign flips when the permutation seeds change (5 permutations x 12 folds are recorded per row in `oof_<tf>.npz`; rerunning with other seeds is one command).\n"
         "- A shortlisted cluster whose top-8 rank in the held-out periods does not survive a different block partition (the harness fixes 12 blocks; the per-period decomposition is of the same OOF rows).\n"
         "- A feature in the shortlist that the truncation check would have dropped: none can be, every column comes from `harness.design` or from `ext_features.parquet`, which passed the truncation check at tolerance 1e-9.\n"
         "- The full model's kept-vs-skipped numbers are a ceiling for a model that cannot ship; if the gate studies' rule lists come nowhere near them, the vocabulary is not the bottleneck; if a rule list beats them, the forest under-fits and this table under-states the vocabulary.\n"
         "- A low weighted Kendall tau in the orthogonal check says the MDI ranking is not aligned with the variance-bearing directions; the shortlist rests on MDA, not on MDI, but the two are reported side by side so a disagreement is visible.\n")

M.append("## Candidates\n")
M.append("None. This study fixes the vocabulary (the shortlist JSON + the five interaction pairs) and proposes no gate; the full model and the SFI gates are ledger rows for the family's PBO / SPA and are ceilings, not configs.\n")

M.append("## Caveats\n")
cav = [
    "The primary MDA statistic is the permutation drop in OOF weighted log-loss; the kept-vs-skipped MDA at the fold's tau is reported with its own mean / std but is not the pass rule (on 70-370 test rows per fold its std exceeds its mean for nearly every cluster, as Judge 1 foresaw).",
    "Per-period stability re-scores the same 12 fold models on the rows of each period (no refit inside a year: a 12-block CV does not exist inside ~1,100 rows / 170 winners, and refitting there would be the noise Judge 2 warns of); it measures whether the relation learned on the other blocks holds in that period.",
    "tau is chosen on the training fold's out-of-bag probabilities (the bagging's own inner out-of-fold estimate), not on an inner CV; OOB probabilities of a 300-tree bagging are out-of-fold for every training row.",
    "Two-level one-hots keep one level; exact duplicates are dropped; missing indicators are de-duplicated by NaN pattern: these are stated preprocessing steps, not searches.",
    "The design's distance sqrt(0.5 (1 - rho)) puts anti-correlated features at maximum distance; substitution between a feature and its negative is therefore not removed by the clustering (mitigated by the duplicate / complement drops above).",
    "On 5minute the FZ card's numeric fields sit at 40.3% NaN (no ref room on 40% of SETUPs): a hair over the 40% rule, so they are dropped while their categorical reads (`fz_read=...`, `card_read=...`, `fz_gate=...`) stay.",
    "`sl` (the Foundation stop price) and `atr14` are price-level / volatility-level columns that also proxy calendar time; if they appear in a shortlist the stability filter is what stands between them and a year effect.",
    "The other studies' processes shared the 4 cores during this run (load average 15-19); runtimes above are wall-clock under that load. Every fit ran single-threaded "
    "(IMP_BAG_JOBS=1, IMP_XGB_JOBS=1 in run_all.sh): on this loaded box a 300-tree bagging fit took 35 s at 1 thread vs 50 s at 4 (bag_probe.log) and a 200-round xgboost fit "
    "0.7 s at 1 thread vs 14 s at 2 (xgb_probe.log, OpenMP spin-wait); the fitted trees do not depend on the thread count (random_state fixes them), so no model was shrunk. "
    "The run logs' header line prints the module constant n_jobs=4; the environment variable is what the fits used.",
]
M += [f"- {c}" for c in cav]
M.append("\n## Files\n")
files = []
for tf in TFS:
    files += [f"studies/importance/results_{tf}.json", f"studies/importance/clusters_{tf}.json", f"studies/importance/importance_clusters_{tf}.csv", f"studies/importance/importance_features_{tf}.csv",
              f"studies/importance/interaction_pairs_{tf}.csv", f"studies/importance/shap_interactions_{tf}.csv", f"studies/importance/spearman_{tf}.csv", f"studies/importance/folds_{tf}.csv",
              f"studies/importance/oof_{tf}.npz", f"studies/importance/run_{tf}.log", f"features_shortlist/{tf}/shortlist.json"]
files += ["studies/importance/imp_lib.py", "studies/importance/run_importance.py", "studies/importance/shortlist.py", "studies/importance/probe.py", "studies/importance/xgb_probe.py", "ledger/registrations.jsonl"]
M += [f"- `{f}`" for f in files]
open(os.path.join(SRC, "FINDINGS.md"), "w", encoding="utf-8").write("\n".join(M) + "\n")

# ---------------------------------------------------------------- findings.json
fj = dict(study="importance", design="quant-ml-canon-feature-importance (both judges' fixes; features from regime-breaks / regime-states / motif-shapelet / rocket-probe judges)",
          timeframes={tf: dict(n_is=R[tf]["meta"]["n_is"], n_features=R[tf]["meta"]["n_features_final"], dropped_nan_gt_40pct=sorted(R[tf]["meta"]["dropped_nan_gt_40pct"]),
                               n_clusters=R[tf]["clustering"]["n_clusters"], silhouette_k=R[tf]["clustering"]["k_best"],
                               full_model=dict(oof_wlogloss=R[tf]["full_model"]["oof_wlogloss"], oof_auc=R[tf]["full_model"]["oof_auc"], gate=R[tf]["full_model"]["gate"], ledger_id=R[tf]["full_model"]["ledger_id"],
                                               cpcv=R[tf]["full_model"]["cpcv"], depth_sensitivity=R[tf]["full_model"]["depth_sensitivity"]),
                               family=R[tf]["family"], stability=R[tf]["stability"], pca_check=R[tf]["pca_check"], interactions_top5=R[tf]["interactions"]["top5"],
                               xgb_oof=dict(wlogloss=R[tf]["interactions"]["xgb_oof_wlogloss"], auc=R[tf]["interactions"]["xgb_oof_auc"]),
                               h2_vs_states=R[tf]["h2_vs_states"], ffd=R[tf]["ffd"],
                               shortlist=dict(n=shortlists[tf]["n_shortlisted"], sha256=shortlists[tf]["sha256"], clusters=[dict(cluster=e["cluster"], representative=e["representative"], members=e["members"],
                                                                                                                                 mda_ll_mean=e["mda_ll_mean"], mda_ll_std=e["mda_ll_std"], per_period_rank=e["per_period_rank"]) for e in shortlists[tf]["clusters"]],
                                              allowed_columns=shortlists[tf]["allowed_columns"]),
                               clusters_table=R[tf]["clusters_table"]) for tf in TFS},
          ffd_verdict=ffd_verdict, candidates=[], null_result=all(shortlists[tf]["n_shortlisted"] == 0 for tf in TFS),
          ledger_families=["importance/full_model", "importance/full_model/cpcv", "importance/sfi"], caveats=cav, files=files)
json.dump(fj, open(os.path.join(SRC, "findings.json"), "w"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
print("FINDINGS.md and findings.json written;", {tf: shortlists[tf]["n_shortlisted"] for tf in TFS}, ffd_verdict)
