"""llm_round1 step 1: the labelled summary tables a round-1 hypothesis proposer may see (DESIGN_PANEL deep-sequence-llm-hypotheses,
Judge 1's cross-fitting and Judge 2's family-size rule; definitions in r1_common.py, fixed before any number was looked at).

    python tables.py                 # both timeframes, both halves -> tables_<tf>_<half>.md / .json, tables_summary.json, a registration line

Per timeframe and half (A = harness blocks 0-5, B = blocks 6-11; label L1; IS rows only):
  * the base row (all rows of the half): count, mean L1 net, win rate;
  * per vocabulary column (r1_common.resolve_vocabulary: hour_bin, fz_read, dir always; the top-8 MDA clusters' representatives under the
    swap rule and the two-way columns as the exploratory vocabulary labelled "outside the frozen shortlist") the decile / level table of
    count, mean net, win rate; deciles are the half's own;
  * the design's four two-way tables: fz_read x hour_bin, n_choch_since_bos (0/1/2/>=3) x dir, hv3_dir_agree x hv3_bars_since bucket,
    fz_visit_n (1/2/3/>=4/NA) x fz_read;
  * the number of labelled cells shown (count >= 5: mean and win rate printed) = the family size for the scorer's max-T; cells with
    fewer than 5 units show the count only and are not labelled cells; no raw rows; nothing from OOS.
The proposer of half X reads tables_*_X.md only; scorer.py scores its rules on half Y and rebuilds the half-X bins on half Y for the
max-T family. The four files' sha256 and cell counts are appended to ledger/registrations.jsonl before any round-1 rule exists.
"""
import os, sys, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import r1_common as C
H = C.H

LOG = open(os.path.join(HERE, "tables.log"), "a", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def fmt_net(v): return "·" if v is None else f"{v:,.0f}"
def fmt_win(v): return "·" if v is None else f"{v:.3f}"


def build(tf, half, T, vocab):
    rows = C.half_rows(T, half)
    F = T.FX.iloc[rows].reset_index(drop=True); net = T.net[rows]; win = T.win[rows]
    n_all = len(rows)
    base = C.cell_stats(net, win, np.ones(n_all, dtype=bool)); base["share"] = 1.0
    out = dict(study=C.STUDY, step=1, kind="labelled_tables", tf=tf, half=half, blocks=C.HALVES[half], label="L1", split="IS",
               strategy=("Strategy 1 rules + ST7 card" if tf == "minute" else "Strategy 2 rules + ST8 card"),
               n_rows=int(n_all), n_sessions=int(len(set(T.session[rows].tolist()))), date_first=str(T.day[rows].min()), date_last=str(T.day[rows].max()),
               base=base, shortlist_state=None, vocabulary=[], one_way={}, two_way={}, cells=[], written_at=None)
    cells = []
    # one-way tables
    for v in vocab:
        col = v.get("column")
        if col is None: out["vocabulary"].append(dict(v)); continue
        s = F[col]; bins = C.make_bins(col, s, v["kind"], tf)
        ve = dict(v); ve["bins"] = bins; ve["allowed_thresholds"] = C.allowed_thresholds(v["kind"], bins); ve["levels"] = [b["level"] for b in bins if b["kind"] == "level"]
        ve["na_rows"] = int(C.bin_mask(s, dict(kind="na")).sum())
        table = []
        for b in bins:
            m = C.bin_mask(s, b); st = C.cell_stats(net, win, m); st["share"] = round(st["n"] / n_all, 4)
            table.append(dict(bin=b, **st))
            if st["labelled"]: cells.append(dict(table=f"one_way:{col}", a=dict(column=col, bin=b), b=None, **{k: st[k] for k in ("n", "mean_net", "win_rate")}))
        out["one_way"][col] = table; out["vocabulary"].append(ve)
    bins_of = {v["column"]: v["bins"] for v in out["vocabulary"] if v.get("column")}
    kinds = {v["column"]: v["kind"] for v in out["vocabulary"] if v.get("column")}
    # two-way tables
    for a, b in C.TWOWAY:
        ka = "nchoch2" if a == "n_choch_since_bos" else kinds[a]; kb = "nchoch2" if b == "n_choch_since_bos" else kinds[b]
        ba = C.make_bins(a, F[a], ka, tf) if ka == "nchoch2" else bins_of[a]
        bb = C.make_bins(b, F[b], kb, tf) if kb == "nchoch2" else bins_of[b]
        ba = [x for x in ba if C.bin_mask(F[a], x).sum() > 0]; bb = [x for x in bb if C.bin_mask(F[b], x).sum() > 0]
        grid = []
        for xa in ba:
            ma = C.bin_mask(F[a], xa); row = []
            for xb in bb:
                m = ma & C.bin_mask(F[b], xb); st = C.cell_stats(net, win, m)
                row.append(st)
                if st["labelled"]: cells.append(dict(table=f"two_way:{a}x{b}", a=dict(column=a, bin=xa), b=dict(column=b, bin=xb), **{k: st[k] for k in ("n", "mean_net", "win_rate")}))
            grid.append(row)
        out["two_way"][f"{a}x{b}"] = dict(row_column=a, col_column=b, row_bins=ba, col_bins=bb, grid=grid)
    cells.insert(0, dict(table="base", a=None, b=None, n=base["n"], mean_net=base["mean_net"], win_rate=base["win_rate"]))
    out["cells"] = cells
    out["n_cells_labelled"] = len(cells)
    out["n_cells_suppressed"] = int(sum(1 for t in out["one_way"].values() for c in t if c["n"] and not c["labelled"]) + sum(1 for g in out["two_way"].values() for r in g["grid"] for c in r if c["n"] and not c["labelled"]))
    out["n_cells_empty"] = int(sum(1 for t in out["one_way"].values() for c in t if not c["n"]) + sum(1 for g in out["two_way"].values() for r in g["grid"] for c in r if not c["n"]))
    out["n_columns_shown"] = len(out["one_way"]); out["n_two_way_tables"] = len(out["two_way"])
    return out


def render_md(J, pairs, dups, tf):
    L = []
    o = C.OUTSIDE
    L.append(f"# LLM round 1, labelled tables: {tf} / half {J['half']} (harness blocks {J['blocks'][0]}-{J['blocks'][-1]}; IS only; label L1)")
    L.append("")
    L.append(f"**Study** `llm_round1` step 1 (DESIGN_PANEL deep-sequence-llm-hypotheses; Judge 1: cross-fitted halves; Judge 2: the family size is the number of labelled cells shown). "
             f"**Rows**: {J['n_rows']:,} L1 units of the {tf} table ({J['strategy']}) in {J['n_sessions']} sessions, {J['date_first']} .. {J['date_last']} (SETUP dates; the half is time-contiguous). "
             f"Label = L1 net INR per trade (the 15:25 intraday book, lot 65, 5 pts slippage per side, charges included; every skipped trade saves ~1,050 INR of costs, so net alone is never the criterion). Nothing from OOS; no raw rows.")
    L.append("")
    L.append(f"**SHORTLIST STATE.** The frozen feature shortlist (`features_shortlist/{tf}/shortlist.json`, sha256 `{pairs['shortlist_sha256'][:16]}...`) has `n_shortlisted = {pairs['n_shortlisted']}` and `allowed_columns = {pairs['allowed_columns']}`: **the EMPTY-SHORTLIST RULE applies**. "
             f"The tables cover `hour_bin`, `fz_read`, `dir` (always included) plus an **exploratory vocabulary labelled \"{o}\"**: the representative of each of the top-8 clusters by log-loss MDA rank of the importance study (none of which passes the shortlist rule; their MDA mean is below one std) and the columns of the design's four two-way tables. "
             f"Every rule written from these tables is exploratory and must say so in its reason; a candidate frozen from them carries the provenance `{{\"vocabulary\": \"{o} (importance rule failed for every cluster)\"}}` for the user to accept or reject. Every labelled cell below counts toward the family size of the scorer's max-T exactly as a shortlisted cell would.")
    L.append("")
    L.append(f"**Family size of this file: {J['n_cells_labelled']} labelled cells** (count >= {C.MIN_CELL_N}: mean net and win rate printed; {J['n_cells_suppressed']} cells with 1-{C.MIN_CELL_N - 1} units show the count only ('·') and are not labelled; {J['n_cells_empty']} empty cells). "
             f"Base rate of the half (one labelled cell): n {J['base']['n']:,}, mean net **{fmt_net(J['base']['mean_net'])}** INR, win rate **{fmt_win(J['base']['win_rate'])}**.")
    L.append("")
    L.append("## What the proposer may do with these tables")
    L.append("")
    L.append(f"- Write at most 8 **skip** rules for `{tf}`, each a conjunction of <= 3 comparisons `[column, op, value]` with ops `>=`, `>`, `<=`, `<`, `==`, `!=`, `in`, `not_in`; a None / NaN value never fires a comparison (the SETUP is kept).")
    L.append(f"- **Columns**: only the columns shown in this file (the vocabulary table below), or a listed interaction pair (section at the end). Numeric **thresholds must be values printed as decile edges / bucket boundaries / levels** of that column in this file (or a listed split point of an interaction pair); text comparisons use the printed levels.")
    L.append(f"- Read this half only. Your rules are scored on the OTHER half ({C.OTHER[J['half']]}, blocks {C.HALVES[C.OTHER[J['half']]][0]}-{C.HALVES[C.OTHER[J['half']]][-1]}) through the harness; the scorer's family for the max-T is the {J['n_cells_labelled']} labelled cells of this file plus every rule proposed (round 0 and round 1), so a rule has to beat the best of everything you could have picked here, not just the other 7 rules.")
    L.append(f"- Columns ending `_pts`, `atr14`, `fz_band_width`, `gap_pts`, `days_to_expiry` drift with the price level / the calendar inside IS (null_tapes_drift study): prefer `_atr` / `_bps` / count / read forms. `n_events_asof` and `sl` are calendar-time proxies and are refused.")
    L.append(f"- For each rule give the reason in the user's words and the table cells that motivated it (`\"cells\": [\"one_way:<column>:<bin label>\", \"two_way:<a>x<b>:<row label>|<col label>\"]`).")
    L.append("")
    L.append("## Vocabulary shown in this file")
    L.append("")
    L.append("| column | kind | provenance | how it is shown (swap rule) | caveats |")
    L.append("|---|---|---|---|---|")
    for v in J["vocabulary"]:
        col = v.get("column")
        L.append(f"| {('`' + col + '`') if col else '(none)'} | {v.get('kind') or '-'} | {v['provenance']} | {v.get('swap') or ('as is')} | {'; '.join(v.get('caveats') or []) or '-'} |")
    if dups: L.append(""); L.append("Exact duplicates on every IS row (checked at run time): " + ", ".join(f"`{a}` == `{b}`" for a, b in dups.items()) + ".")
    L.append("")
    L.append("## One-way tables (per column: bin, count, share of the half, mean L1 net INR, win rate)")
    L.append("")
    for v in J["vocabulary"]:
        col = v.get("column")
        if not col: continue
        L.append(f"### `{col}` ({v['kind']}; {v['label']})")
        L.append("")
        if v["kind"] == "decile": L.append(f"Decile edges of this half (the allowed thresholds): {', '.join(str(x) for x in v['allowed_thresholds'])}. NA rows: {v['na_rows']}.")
        elif v["kind"] in ("nchoch", "hv3b", "visit"): L.append(f"Bucket boundaries (the allowed thresholds): {', '.join(str(x) for x in v['allowed_thresholds'])}.")
        elif v["kind"] == "level" and v["allowed_thresholds"]: L.append(f"Integer levels (the allowed thresholds): {', '.join(str(x) for x in v['allowed_thresholds'])}.")
        L.append("")
        L.append("| bin | n | share | mean net (INR) | win rate |")
        L.append("|---|---|---|---|---|")
        for c in J["one_way"][col]:
            L.append(f"| {c['bin']['label']} | {c['n']:,} | {c['share']:.3f} | {fmt_net(c['mean_net'])} | {fmt_win(c['win_rate'])} |")
        L.append("")
    L.append("## Two-way tables (cell = mean net INR / win rate / n; '·' = fewer than 5 units, count only)")
    L.append("")
    for name, g in J["two_way"].items():
        a, b = g["row_column"], g["col_column"]
        L.append(f"### `{a}` (rows) x `{b}` (columns)")
        L.append("")
        L.append("| " + a + " \\ " + b + " | " + " | ".join(x["label"] for x in g["col_bins"]) + " |")
        L.append("|---|" + "---|" * len(g["col_bins"]))
        for xa, row in zip(g["row_bins"], g["grid"]):
            cells = []
            for st in row:
                if st["n"] == 0: cells.append("0")
                elif not st["labelled"]: cells.append(f"· / · / {st['n']}")
                else: cells.append(f"{fmt_net(st['mean_net'])} / {fmt_win(st['win_rate'])} / {st['n']}")
            L.append(f"| {xa['label']} | " + " | ".join(cells) + " |")
        L.append("")
    L.append("## Listed interaction pairs (from the frozen shortlist; the only depth-2/3 conjunctions allowed beyond the columns above)")
    L.append("")
    L.append("| feature a | feature b | split points a | split points b | status |")
    L.append("|---|---|---|---|---|")
    for p in pairs["pairs"]:
        L.append(f"| `{p['feature_a']}` | `{p['feature_b']}` | {', '.join(str(x) for x in p['split_a'])} | {', '.join(str(x) for x in p['split_b'])} | {'REFUSED: ' + p['refused_why'] if p['refused'] else o + '; usable as a pair with these split points (a one-hot `col=nan` is not expressible in the grammar)'} |")
    L.append("")
    L.append(f"Generated {J['written_at']} by `studies/llm_round1/tables.py` from `harness.load('{tf}')` (label L1) and `features_ext/{tf}/ext_features.parquet`. Definitions: `r1_common.py` docstring. Family size for the max-T = **{J['n_cells_labelled']}** labelled cells.")
    return "\n".join(L) + "\n"


def main():
    t0 = time.time()
    log(f"=== tables.py {C.now()} ===")
    summary = dict(study=C.STUDY, step=1, written_at=None, halves={h: dict(blocks=C.HALVES[h], files={}) for h in C.HALVES}, shortlist=dict(), notes=[])
    for tf in C.TFS:
        T = C.load_tf(tf)
        assert not T.oos_mask[np.isin(T.block, list(range(12)))].any(), "OOS rows must not sit in an IS block"
        vocab, dups = C.resolve_vocabulary(tf, T.FX[T.is_mask].reset_index(drop=True))
        pairs = C.interaction_pairs(tf)
        summary["shortlist"][tf] = dict(sha256=pairs["shortlist_sha256"], n_shortlisted=pairs["n_shortlisted"], n_allowed_columns=len(pairs["allowed_columns"]))
        log(f"[{tf}] vocabulary: " + ", ".join(f"{v.get('column') or '(covered)'}<-cl{v['cluster']}" if v.get("cluster") is not None else str(v.get("column")) for v in vocab))
        for v in vocab:
            if v.get("swap"): log(f"[{tf}]   swap: cluster {v['cluster']}: {v['swap']}")
        for half in C.HALVES:
            J = build(tf, half, T, vocab)
            J["written_at"] = C.now()
            J["shortlist_state"] = dict(sha256=pairs["shortlist_sha256"], n_shortlisted=pairs["n_shortlisted"], allowed_columns=pairs["allowed_columns"], rule="EMPTY-SHORTLIST RULE applied" if not pairs["allowed_columns"] else "shortlist columns")
            J["interaction_pairs"] = pairs["pairs"]; J["duplicates"] = dups
            J["definitions"] = C.__doc__
            pj = os.path.join(HERE, f"tables_{tf}_{half}.json"); pm = os.path.join(HERE, f"tables_{tf}_{half}.md")
            json.dump(J, open(pj, "w", encoding="utf-8"), indent=1, default=lambda z: z.item() if hasattr(z, "item") else str(z))
            open(pm, "w", encoding="utf-8").write(render_md(J, pairs, dups, tf))
            summary["halves"][half]["files"][tf] = dict(json=C.rel(pj), md=C.rel(pm), sha256_json=C.sha256(pj), sha256_md=C.sha256(pm), n_rows=J["n_rows"], n_sessions=J["n_sessions"],
                                                        n_cells_labelled=J["n_cells_labelled"], n_cells_suppressed=J["n_cells_suppressed"], n_cells_empty=J["n_cells_empty"],
                                                        n_columns_shown=J["n_columns_shown"], n_two_way_tables=J["n_two_way_tables"])
            log(f"[{tf}] half {half}: rows {J['n_rows']} sessions {J['n_sessions']} columns {J['n_columns_shown']} two-way {J['n_two_way_tables']} -> labelled cells {J['n_cells_labelled']} (suppressed {J['n_cells_suppressed']}, empty {J['n_cells_empty']})")
    for half in C.HALVES:
        summary["halves"][half]["n_cells_labelled_total"] = int(sum(f["n_cells_labelled"] for f in summary["halves"][half]["files"].values()))
    summary["written_at"] = C.now()
    json.dump(summary, open(os.path.join(HERE, "tables_summary.json"), "w", encoding="utf-8"), indent=1)
    # registration: the tables' shas and cell counts, before any round-1 rule exists (append-only)
    fam_rows = len(H.read_ledger(C.STUDY))
    for half in C.HALVES:
        files = summary["halves"][half]["files"]
        rec = dict(kind="pre_registration", what=f"LLM hypotheses round 1 labelled tables half {half}",
                   sha256=C.hashlib.sha256("|".join(f["sha256_json"] for f in files.values()).encode()).hexdigest(), files={tf: dict(file=f["json"], sha256=f["sha256_json"], md=f["md"], sha256_md=f["sha256_md"], n_cells_labelled=f["n_cells_labelled"]) for tf, f in files.items()},
                   blocks=C.HALVES[half], n_cells_labelled_total=summary["halves"][half]["n_cells_labelled_total"], registered_at=C.now(),
                   note=(f"Judge 1 / Judge 2 fixes: tables of half {half} (harness blocks {C.HALVES[half][0]}-{C.HALVES[half][-1]}) shown to the round-1 proposer of half {half} only; its rules are scored on half {C.OTHER[half]}; "
                         f"the family size for the max-T = these labelled cells + every rule proposed (round 0 and round 1). EMPTY-SHORTLIST RULE: the frozen shortlist is empty on both timeframes, so the vocabulary is hour_bin / fz_read / dir plus the top-8 MDA clusters' representatives and the two-way columns, all labelled 'outside the frozen shortlist'."),
                   ledger_sha_at_registration=H.ledger_sha(), llm_round1_ledger_rows_at_registration=fam_rows)
        log(f"registration half {half}: {'appended' if C.append_registration(rec) else 'already present'}")
    log(f"done in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
