# H1 gate audit: what the frozen ST7 (1 min) / ST8 (5 min) gates skip vs keep

Study folder `fz_v3/out/studies/h1_gate_audit/`. Scripts `h1_gate_audit.py` (the audit, 138.6 s, log `h1_gate_audit.log` / `run.log`) and
`h1_posthoc.py` (one post-hoc ledger row, 18.2 s, log `h1_posthoc.log`). Every number below is IS only (SETUP date <= 2025-12-31) and
comes from a harness ledger row (id given) or from a CSV in this folder. Ledger sha after the audit `33170f8df9f5d50e`, after the
post-hoc row `1ee15dc04860b284`. All tables: `TABLES.md` (auto-generated), `h1_<tf>_<label>_*.csv`, `h1_summary.json`,
`h1_family_posthoc.json`; machine-readable summary `findings.json`.

## 1. Definitions (fixed before any number was looked at)

| term | definition |
|---|---|
| unit | a harness row: a Foundation SETUP taken under the label's book, `harness.load(tf, label)`; IS rows only (1 min L1 4,452, L0 4,502; 5 min L1 826, L0 832) |
| L1 / L0 | L1 = the 15:25 intraday book (primary); L0 = the engine's uncut trade (robustness) |
| kept | `T.F.fz_traded`: ST7/ST8 held a position on the SETUP, a TAKE or a REENTER whose R5 was the SETUP (post-SETUP; the comparator, never a feature). 745 (1 min) / 325 (5 min) IS rows on both labels |
| gate_at / outcome_gate | `fz_gate` as of the SETUP bar / `fzpost_outcome_gate` (REENTER when a later REENTER used the SETUP as its R5). They differ on 11 IS rows on 1 min (BLOCK -> REENTER, all filled one bar later) and 96 on 5 min (WATCH -> REENTER) |
| block_key | `BLOCK:<fz_block_reason>` when outcome_gate is BLOCK; `WATCH:<fz_block_reason>` when outcome_gate is WATCH and a refused TAKE branch set a reason (`leave_into_recycle`); else the outcome gate. Same definition as the local `h1_common.py`, so the cross-check is like for like |
| loser / winner | label net <= 0 / > 0 (costs included) |
| precision, recall, lift | P(loser given skipped); P(skipped given loser); precision / base loser rate (1.0 = skipping at random). `lift` is derived from the ledger row's `loser_precision` and the IS base loser rate |
| winner recall | count: P(kept given winner); net-weighted: kept winners' net / all winners' net |
| big / huge winner | label pts >= 50 / >= 100 |
| pts bucket | <=-50, (-50,-20], (-20,0], (0,20], (20,50], (50,100], >100 |
| hold bucket | label bars held: 1-5, 6-15, 16-30, 31-60, 61-120, 121-375, >375 (bars on both timeframes; a 5 min bar is five 1 min bars) |
| visit bin | `fz_visit_n`: 1 / 2 / 3 / 4+ / none (no ref room) |
| variants | pre-declared, each a ledger row of family `h1/<variant>`: `frozen` (kept = fz_traded), `take_only` (fz_gate == TAKE), `take_or_reenter_at_setup` (fz_gate in TAKE, REENTER), `not_block` (fzpost_outcome_gate != BLOCK: WATCH rows treated as taken; DIAGNOSTIC, post column), `skip_only:<block_key>` (keep = block_key != key, one row per key; DIAGNOSTIC, the key uses the post outcome gate) |
| post-hoc | `not_block_asof` (fz_gate != BLOCK), declared after the audit's numbers were seen because the SPA best on 1 min / L1 was the post-column `not_block`; counted in the family (`h1_posthoc.py`) |
| FZ book | the ST7/ST8 position's own net on the kept rows (`fzpos_l1_net_inr` under L1, `fzpos_net_inr` under L0), Foundation's label net on the other rows; scored as label `<label>_fzpos` under family `h1/fz_book`. A TAKE is Foundation's own position (identical net on every TAKE row); a REENTER fills a bar later and exits by its own rules (`band_reclaim`) |
| selection-only book | `frozen` on the label itself: Foundation's label net on the kept rows |
| bridge | Foundation IS net + avoided price move of the skipped rows (-sum pts x 65) + avoided costs of the skipped rows (sum `cost_inr` = charges + 2 x 5 pts x 65 slippage) + REENTER exit delta = FZ book net (asserted to close within 0.05 INR on all four tables) |
| group tables | descriptive decompositions of the `frozen` ledger row by as-of and post columns; no rule was chosen on them |

Control percentile = `fz_report.random_control` (2,000 session-matched draws, seeded by the candidate tag): the share of draws whose kept
net is below the candidate's. Permutation p = `fz_report.permutation_p` (kept vs skipped label net, 2,000 shuffles). Because the
control matches per-session position counts while `diff` pools all rows, the two can disagree in sign for a near-complete keep
(e.g. `skip_only:BLOCK:open_pierce`: the 53 skipped rows are better than the pool but worse than the other rows of their own
gap-open sessions). Both are reported; neither alone is the criterion.

## 2. The frozen gate vs the pre-registered comparator

The `h1/frozen` rows reproduce `results/pre_registration.json` (`comparator/frozen_st7_st8`) on every statistic; the control
percentile moves by 0.2-2.1 points because the draws are seeded by candidate tag (1 min L1 64.7 vs 62.6; L0 50.0 vs 49.2; 5 min L1
11.6 vs 13.6; L0 28.1 vs 26.5).

## 3. Variants (harness ledger rows, IS)

### 1 min / L1 (4,452 units, 745 kept; base loser rate 0.8441, all-rows mean -1,009.61 INR, mean cost 1,047.54)

| variant | id | kept n | share | kept mean | skipped mean | diff | diff top1% off | control pct | perm p | loser recall | loser precision | lift | winner recall (n / net) | top-decile skipped | big skipped | kept PF | kept mean slip 8 | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frozen | 127543888f5570fe | 745 | 0.167 | -1,026.02 | -1,006.31 | -19.71 | -8.44 | 64.7 | 0.855 | 0.835 | 0.847 | 1.003 | 0.182 / 0.173 | 0.843 | 225 / 268 | 0.327 | -1,415.99 | 6 |
| take_only | 4325428b222de52f | 605 | 0.136 | -991.46 | -1,012.46 | 21.00 | -13.10 | 66.9 | 0.854 | 0.867 | 0.847 | 1.003 | 0.150 / 0.161 | 0.843 | 228 | 0.364 | -1,381.42 | 5 |
| take_or_reenter_at_setup | b0b89957ada19605 | 734 | 0.165 | -1,022.43 | -1,007.08 | -15.35 | -7.11 | 65.3 | 0.891 | 0.838 | 0.847 | 1.003 | 0.180 / 0.173 | 0.843 | 225 | 0.331 | -1,412.39 | 6 |
| not_block (post) | 0d1bbb98d600860c | 2,996 | 0.673 | -990.12 | -1,049.71 | 59.59 | 87.24 | 99.3 | 0.489 | 0.330 | 0.852 | 1.009 | 0.689 / 0.664 | 0.329 | 87 | 0.324 | -1,380.08 | 6 |
| not_block_asof (post-hoc) | cb1c6c5d7876cae6 | 2,985 | 0.670 | -989.10 | | 62.23 | | 99.5 | 0.472 | 0.333 | 0.852 | 1.009 | / 0.664 | | | | -1,379.07 | 6 |
| skip_only:BLOCK:clock | f22c5d17af5e555b | 4,397 | 0.988 | -1,008.81 | -1,072.97 | 64.16 | -115.20 | 2.6 | 0.859 | 0.015 | 1.000 | 1.185 | 1.000 / 1.000 | 0.000 | 0 | 0.326 | -1,398.78 | 9 |
| skip_only:BLOCK:hunt_fade | 40451f8101be314c | 4,224 | 0.949 | -1,001.12 | -1,166.89 | 165.78 | 108.18 | 47.8 | 0.333 | 0.053 | 0.868 | 1.029 | 0.957 / 0.964 | 0.029 | 10 | 0.328 | -1,391.08 | 8 |
| skip_only:BLOCK:new | 6ffb55302debfae1 | 3,332 | 0.748 | -996.40 | -1,048.90 | 52.50 | 79.56 | 93.4 | 0.558 | 0.252 | 0.846 | 1.003 | 0.752 / 0.740 | 0.257 | 66 | 0.323 | -1,386.36 | 8 |
| skip_only:BLOCK:open_pierce | bcdd12dd001a1cbd | 4,399 | 0.988 | -1,015.28 | -538.48 | -476.80 | 32.53 | 100.0 | 0.169 | 0.010 | 0.736 | 0.872 | 0.980 / 0.960 | 0.043 | 11 | 0.315 | -1,405.25 | 6 |
| skip_only:WATCH:leave_into_recycle | ece4919a1486a7aa | 4,195 | 0.942 | -1,014.57 | -928.56 | -86.01 | -33.31 | 7.5 | 0.604 | 0.056 | 0.821 | 0.973 | 0.934 / 0.932 | 0.086 | 20 | 0.319 | -1,404.54 | 8 |

### 5 min / L1 (826 units, 325 kept; base loser rate 0.7228, all-rows mean -757.05, mean cost 1,049.86)

| variant | id | kept n | share | kept mean | skipped mean | diff | diff top1% off | control pct | perm p | loser recall | loser precision | lift | winner recall (n / net) | top-decile skipped | big skipped | kept PF | kept mean slip 8 | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frozen | daaf09471b73ca51 | 325 | 0.394 | -978.81 | -613.20 | -365.62 | -304.01 | 11.6 | 0.250 | 0.605 | 0.721 | 0.997 | 0.389 / 0.369 | 0.565 | 95 / 148 | 0.563 | -1,368.78 | 3 |
| take_only | ccbf6f37cc8a2977 | 228 | 0.276 | -876.24 | -711.61 | -164.63 | -110.57 | 18.0 | 0.630 | 0.724 | 0.722 | 0.999 | 0.275 / 0.291 | 0.609 | 109 | 0.618 | -1,266.20 | 4 |
| take_or_reenter_at_setup | 011fdac4f903ee79 | 229 | 0.277 | -864.05 | -716.01 | -148.05 | -92.65 | 19.8 | 0.675 | 0.724 | 0.724 | 1.001 | 0.280 / 0.293 | 0.609 | 109 | 0.622 | -1,254.02 | 4 |
| not_block (post) | f91cb4af52b1e52c | 613 | 0.742 | -794.39 | -649.61 | -144.77 | -80.21 | 87.0 | 0.699 | 0.248 | 0.695 | 0.961 | 0.716 / 0.689 | 0.304 | 49 | 0.611 | -1,184.35 | 5 |
| not_block_asof (post-hoc; identical rows) | 2fb21a08ab1608ea | 613 | 0.742 | -794.39 | | -144.77 | | 87.5 | 0.694 | 0.248 | 0.695 | 0.961 | / 0.689 | | | | -1,184.35 | 5 |
| skip_only:BLOCK:clock | 4f4bac1aa89ba8c6 | 821 | 0.994 | -754.71 | -1,141.22 | 386.51 | 168.52 | 0.1 | 0.860 | 0.008 | 1.000 | 1.384 | 1.000 / 1.000 | 0.000 | 0 | 0.642 | -1,144.68 | 3 |
| skip_only:BLOCK:hunt_fade | 4988ed3569672d4f | 808 | 0.978 | -770.15 | -169.03 | -601.12 | -822.83 | 5.8 | 0.579 | 0.020 | 0.667 | 0.922 | 0.974 / 0.982 | 0.000 | 5 | 0.636 | -1,160.12 | 4 |
| skip_only:BLOCK:new | 64d727bb357dcb0b | 667 | 0.808 | -750.14 | -786.05 | 35.91 | 211.40 | 61.0 | 0.929 | 0.188 | 0.704 | 0.975 | 0.795 / 0.773 | 0.261 | 35 | 0.631 | -1,140.10 | 6 |
| skip_only:BLOCK:open_pierce | 08047b56862edf0c | 795 | 0.963 | -780.74 | -149.55 | -631.19 | -856.68 | 100.0 | 0.443 | 0.032 | 0.613 | 0.848 | 0.948 / 0.934 | 0.043 | 9 | 0.625 | -1,170.71 | 4 |
| skip_only:WATCH:leave_into_recycle | f963132b4c147368 | 728 | 0.881 | -854.61 | -32.37 | -822.24 | -1,069.67 | 0.1 | 0.088 | 0.114 | 0.694 | 0.960 | 0.869 / 0.865 | 0.087 | 21 | 0.607 | -1,244.57 | 4 |

### L0 robustness (`h1_minute_L0_variants.csv`, `h1_5minute_L0_variants.csv`)

| tf | variant | id | kept n | kept mean | skipped mean | diff | control pct | perm p | loser recall | precision | lift | winner recall net | kept PF | sign blocks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min | frozen | d0f4d52bff2714d9 | 745 | -1,029.88 | -900.41 | -129.48 | 50.0 | 0.550 | 0.837 | 0.850 | 1.003 | 0.161 | 0.411 | 4 |
| 1 min | take_only | 2d2b8e1bf6447ad3 | 605 | -980.04 | -912.80 | -67.24 | 56.8 | 0.752 | 0.868 | 0.851 | 1.003 | 0.148 | 0.454 | 4 |
| 1 min | not_block | 903af46046234971 | 2,996 | -902.27 | -960.75 | 58.48 | 97.3 | 0.730 | 0.332 | 0.841 | 0.991 | 0.652 | 0.446 | 8 |
| 1 min | not_block_asof | 69096afdc57337c0 | 2,985 | -900.61 | | 62.98 | 97.6 | 0.743 | 0.334 | 0.841 | 0.992 | 0.652 | | 8 |
| 5 min | frozen | c08a962be699735d | 325 | -277.20 | -276.47 | -0.73 | 28.1 | 1.000 | 0.605 | 0.773 | 0.993 | 0.397 | 0.898 | 4 |
| 5 min | take_only | 2ad039c7d19cf22d | 228 | 126.30 | -428.91 | 555.21 | 28.9 | 0.477 | 0.727 | 0.780 | 1.001 | 0.328 | 1.046 | 4 |
| 5 min | take_or_reenter_at_setup | 5d3759e3d6038faa | 229 | 133.81 | -432.68 | 566.49 | 31.4 | 0.494 | 0.727 | 0.781 | 1.003 | 0.329 | 1.049 | 4 |
| 5 min | not_block | 5d2041d94e721b9d | 613 | -361.05 | -40.81 | -320.24 | 88.3 | 0.716 | 0.255 | 0.753 | 0.967 | 0.690 | 0.861 | 5 |
| 5 min | skip_only:BLOCK:clock | a43e3a6e6e22f60e | 821 | -440.47 | 11,942.06 | -12,382.53 | 7.8 | 0.008 | 0.011 | 0.636 | 0.817 | 0.921 | 0.835 | 3 |
| 5 min | skip_only:BLOCK:new | 8c64c9a221d3c493 | 673 | -129.69 | -899.24 | 769.55 | 92.2 | 0.421 | 0.194 | 0.793 | 1.018 | 0.828 | 0.950 | 6 |

The other L0 skip-only rows are in the CSVs. The one L0 row with a small permutation p (5 min `skip_only:BLOCK:clock`, p 0.008) is
the 5 SETUPs at or after 15:20 that the engine held for several sessions (mean +11,942 INR under L0); under L1 the same 5 rows are
all losers (-1,141): an artefact of the uncut label, not a gate property.

**Go / no-go:** no variant passes on any table (`h1_summary.json` -> `variants[*].go_no_go`; the frozen gate fails diff > 0,
diff-top1%-removed > 0, kept mean at 8 pts slippage > 0, sign blocks >= 8 and control >= 95 on both labels and both timeframes;
kept share < 20% on 1 min). Every kept book has mean net < 0 at 5 and at 8 pts slippage.

## 4. The ST7/ST8 book vs the selection-only book, and the bridge

| tf / label | selection-only kept mean (id) | FZ book kept mean (id) | REENTERs (rows changed) | Foundation IS net | avoided price move | avoided costs | REENTER exit delta | FZ book net | gain over Foundation | cost avoidance / gain | selection / gain |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 min / L1 | -1,026.02 (127543888f5570fe) | -1,027.81 (f4ade6c2d1bc063f) | 140 (11) | -4,494,772.79 | -151,339.50 | 3,881,726.07 | -1,332.02 | -765,718.24 | 3,729,054.55 | 1.041 | -0.041 |
| 1 min / L0 | -1,029.88 (d0f4d52bff2714d9) | -1,031.67 (223c25cc0ace7394) | 140 (11) | -4,150,085.95 | -552,058.00 | 3,934,880.17 | -1,332.02 | -768,595.80 | 3,381,490.15 | 1.164 | -0.164 |
| 5 min / L1 | -978.81 (daaf09471b73ca51) | -1,107.52 (9b0f6458034da26c) | 97 (94) | -625,325.16 | -218,799.75 | 526,011.10 | -41,829.97 | -359,943.78 | 265,381.38 | 1.982 | -0.982 |
| 5 min / L0 | -277.20 (c08a962be699735d) | -431.67 (e556a56ededbbbf4) | 97 (94) | -230,262.16 | -392,128.75 | 532,300.34 | -50,200.69 | -140,291.26 | 89,970.90 | 5.916 | -4.916 |

The bridge closes on all four tables. In words: **everything the frozen gate gains over Foundation is cost avoidance, and more.**
The skipped SETUPs had a positive price move in aggregate on every table (avoided price move is negative: -151k / -552k on 1 min,
-219k / -392k on 5 min), so the selection itself lost money before costs; the ~1,050 INR saved per skipped trade (3,707 skips on 1 min,
501 on 5 min) is 104% / 116% (1 min) and 198% / 592% (5 min) of the gain. On 5 min the REENTER exits make the FZ book worse than the
selection-only book by 41.8k under L1 (-431 INR per REENTER; 27 of 97 exit by `band_reclaim`, `fzpos_l1_exit_reason`) and 50.2k under
L0; on 1 min the 11 one-bar-late fills cost 1.3k in total and the TAKE rows are Foundation's own positions.

## 5. Group tables (frozen gate, IS; `h1_<tf>_<label>_by_*.csv`, full set in TABLES.md)

### 1 min / L1, by block key (what the gate did with each SETUP and how Foundation's L1 trade ended)

| block_key | n | kept | net | mean | win rate | winners | big | big skipped | huge | huge skipped |
|---|---|---|---|---|---|---|---|---|---|---|
| TAKE | 605 | 605 | -599,832 | -991 | 0.172 | 104 | 40 | 0 | 17 | 0 |
| REENTER | 140 | 140 | -164,554 | -1,175 | 0.157 | 22 | 3 | 0 | 0 | 0 |
| WATCH | 1,994 | 0 | -1,963,370 | -985 | 0.153 | 306 | 118 | 118 | 49 | 49 |
| WATCH:leave_into_recycle | 257 | 0 | -238,640 | -929 | 0.179 | 46 | 20 | 20 | 9 | 9 |
| BLOCK:new | 1,120 | 0 | -1,174,771 | -1,049 | 0.154 | 172 | 66 | 66 | 26 | 26 |
| BLOCK:hunt_fade | 228 | 0 | -266,052 | -1,167 | 0.132 | 30 | 10 | 10 | 4 | 4 |
| BLOCK:clock | 55 | 0 | -59,014 | -1,073 | 0.000 | 0 | 0 | 0 | 0 | 0 |
| BLOCK:open_pierce | 53 | 0 | -28,540 | -538 | 0.264 | 14 | 11 | 11 | 6 | 6 |

Kept rows (TAKE + REENTER) have a mean of -1,026 against -1,006 for the skipped; the kept win rate is 0.169 against 0.155. The only
block key with a mean clearly better than the pool is `open_pierce` (-538, 26% winners, 11 big winners in 53 rows, all skipped);
`clock` is the only key that skips losers only (0 winners in 55, all at or after 15:20 under a 15:25 cut: it is a cost rule, not a
read). By read, the gate keeps 55% of ACCEPTED, 49% of FIRST_PRINT, 31% of LEAVE and 2-3% of everything else; the kept LEAVE rows
(-972) do worse than the refused LEAVE rows (-935); NEW (-831) and RECYCLE (-539) are the best-reading pools and are skipped at 97-98%.
By take_why, the refused leave branch: `leave_vol_fail` 654 rows, -957, 111 winners, 49 big; `leave_into_recycle` 257, -929, 46
winners, 20 big; `leave_gap_quiet` 44, -341, 34% winners, 7 big. By hour, the gate keeps 2% of the 189 SETUPs before 09:25 (mean -843,
25% winners, 28 big winners all skipped) and 0% after 15:20; its kept share is 15-24% elsewhere; the kept rows beat the skipped only
in the 09, 11 and 13 bins (+636, +455, +108) and lose in 10, 12, 14 (-279, -148, -479). By direction: kept down -1,125 vs skipped -989;
kept up -915 vs -1,023. By visit bin nothing separates (kept minus skipped -228 / -94 / +94 / -119 / -10). By exit reason: the 471
`eod` rows (the 15:25 cut) are the book's only profitable class (+2,930 mean, 61% winners, 191 of the 268 big winners) and the gate
keeps 20% of them; `next_choch` -1,111 (kept 17%), `stop_loss` -2,278 (kept 15%).

### 5 min / L1, by block key

| block_key | n | kept | net | mean | win rate | winners | big | big skipped | huge | huge skipped |
|---|---|---|---|---|---|---|---|---|---|---|
| TAKE | 228 | 228 | -199,783 | -876 | 0.276 | 63 | 39 | 0 | 21 | 0 |
| REENTER | 97 | 97 | -118,331 | -1,220 | 0.268 | 26 | 14 | 0 | 4 | 0 |
| WATCH | 190 | 0 | -165,672 | -872 | 0.237 | 45 | 25 | 25 | 12 | 12 |
| WATCH:leave_into_recycle | 98 | 0 | -3,172 | -32 | 0.306 | 30 | 21 | 21 | 11 | 11 |
| BLOCK:new | 159 | 0 | -124,982 | -786 | 0.296 | 47 | 35 | 35 | 18 | 18 |
| BLOCK:hunt_fade | 18 | 0 | -3,043 | -169 | 0.333 | 6 | 5 | 5 | 1 | 1 |
| BLOCK:clock | 5 | 0 | -5,706 | -1,141 | 0.000 | 0 | 0 | 0 | 0 | 0 |
| BLOCK:open_pierce | 31 | 0 | -4,636 | -150 | 0.387 | 12 | 9 | 9 | 6 | 6 |

On 5 min the refusals of the leave branch pick the better rows: LEAVE reads that were refused average -125 (`leave_vol_fail` 113
rows -114, `leave_into_recycle` 98 rows -32, `leave_gap_quiet` 12 rows +170) against -838 for the 221 leave TAKEs; the 96 WATCH ->
REENTER rows (PENDING reads re-entered a bar later) average -1,253 against -1,279 for the PENDING rows that were not. THIN (48 rows,
-43) and `open_pierce` (31, -150) are the best pools and are skipped entirely. By hour the kept rows lose to the skipped in every bin
but 11 (09: -1,312 vs -642; 10: -1,706 vs -657); before 09:25 the 50 SETUPs average +127 with 15 big winners, 14 skipped. By exit
reason `eod` is again the only profitable class (280 rows, +3,467, 72% winners, 139 of 148 big winners; kept 38%).

## 6. The big-winner audit (`h1_<tf>_<label>_big_winners_all.csv` / `_skipped.csv`)

| tf / label | winners n / net | big (>= 50) n / net / share of winners' net | big skipped n / net | huge (>= 100) n / skipped / net skipped | median bars held big / all winners / losers | eod exit share of big |
|---|---|---|---|---|---|---|
| 1 min / L1 | 694 / 2,140,781 | 268 / 1,771,850 / 0.828 | 225 (0.840) / 1,478,374 | 111 / 94 / 1,032,621 | 119 / 75.5 / 12 | 0.713 |
| 1 min / L0 | 684 / 3,333,971 | 294 / 2,998,081 / 0.899 | 250 (0.850) / 2,536,017 | 146 / 121 / 2,103,263 | 271 / 104.5 / 12.5 | n/a (uncut) |
| 5 min / L1 | 229 / 1,108,931 | 148 / 1,029,787 / 0.929 | 95 (0.642) / 654,319 | 73 / 48 / 486,544 | 40 / 34 / 8 | 0.939 |
| 5 min / L0 | 184 / 1,992,523 | 128 / 1,935,215 / 0.971 | 82 (0.641) / 1,168,411 | 90 / 54 / 1,071,138 | 150 / 101.5 / 10 | n/a |

Where the L1 big winners are skipped (n skipped / n big in the group; net skipped):

| | 1 min / L1 | 5 min / L1 |
|---|---|---|
| by block key | WATCH 118/118 (745,686), BLOCK:new 66/66 (462,215), WATCH:leave_into_recycle 20/20 (125,340), BLOCK:open_pierce 11/11 (85,032), BLOCK:hunt_fade 10/10 (60,102); kept: TAKE 40, REENTER 3 | BLOCK:new 35/35 (241,543), WATCH 25/25 (179,927), WATCH:leave_into_recycle 21/21 (142,726), BLOCK:open_pierce 9/9 (71,098), BLOCK:hunt_fade 5/5 (19,025); kept: TAKE 39, REENTER 14 |
| by read | LEAVE 91/130, PENDING 82/82, THIN 19/20, NEW 17/17, RECYCLE 6/6, REJECT 6/6 | LEAVE 55/94, PENDING 15/29, NEW 14/14, THIN 9/9, RECYCLE 2/2 |
| by hour | 14: 58/62 (297,023); 10: 38/46; 13: 34/45; <09:25: 28/28 (242,281); 12: 27/30; 09: 22/30; 11: 15/23; 15: 3/4 | 10: 19/25; 13: 17/33; 09: 14/21; <09:25: 14/15 (128,259); 14: 13/22; 12: 10/19; 11: 8/13 |
| by hold bucket | 121-375 bars: 107/131 (888,704); 61-120: 80/92 (456,300); 31-60: 29/34; 16-30: 9/10 | 61-120 bars (> 5 h): 40/52 (320,680); 31-60: 22/38; 16-30: 21/41; 6-15: 12/17 |
| by exit reason | eod 159/191, next_choch 65/76, expiry 1/1 | eod 88/139, expiry 5/6, next_choch 2/3 |

The "late runners" under the intraday label are the trades that run to the 15:25 cut: on 1 min 238 of the 268 big winners are held
more than 60 bars (median 119 bars, 71% exit `eod`) and they carry 1.62M of the 1.77M big-winner net; the gate keeps 36 of them. Half
of the skipped big-winner net on 1 min sits in two clocks: before 09:25 (28 of 28 skipped, `open_pierce` / `new` blocks and WATCH)
and the 14:00 bin (58 of 62). On 5 min the analogue is the 09:15-10:15 entry held to the close (61-120 bars, 40 of 52 skipped), and
the pre-09:25 SETUPs (14 of 15 skipped, 128k). The skipped list is `h1_minute_L1_big_winners_skipped.csv` (225 rows) and
`h1_5minute_L1_big_winners_skipped.csv` (95 rows), columns setup_i, time, dir, hour_bin, read, gate_at, outcome_gate, block_reason,
block_key, branch, take_why, visit_n, pts, net, exit_reason, bars_held, hold_bucket, exit_time, kept, pos_kind, fz_net,
fz_exit_reason, mfe, mae, sl_dist_pts. The largest skipped 1 min winners: 2024-06-04 10:21 down NEW/BLOCK:new +631 pts (39,956),
2024-06-05 10:07 up NEW/BLOCK:new +559 pts (35,227), 2024-03-13 09:26 down LEAVE/WATCH `leave_vol_fail` +381 pts (23,685).

## 7. The family (10 candidates per table: 9 pre-declared + 1 post-hoc; `h1_family_posthoc.json`)

| tf / label | candidates | effective trials | PBO (diff) | PBO (kept mean) | SPA p | RC p | SPA best | frozen bootstrap 90% CI of diff | P(diff <= 0) | frozen DSR p |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 min / L1 | 10 | 1.54 | 0.582 | 0.780 | 0.036 | 0.084 (9-family) | not_block (0d1bbb98d600860c), mean gain 157 / session | [-183.18, 142.36] | 0.585 | 1.000 |
| 1 min / L0 | 10 | 1.72 | 0.930 | 0.878 | 0.183 | | not_block_asof | [-475.43, 246.50] | 0.737 | 1.000 |
| 5 min / L1 | 10 | 1.62 | 0.546 | 0.756 | 0.134 | | skip_only:BLOCK:open_pierce | [-954.18, 162.78] | 0.863 | 1.000 |
| 5 min / L0 | 10 | 1.68 | 0.724 | 0.577 | 0.520 | | skip_only:BLOCK:open_pierce | [-1,317.12, 1,281.64] | 0.526 | 0.467 |

(9-family values before the post-hoc row: PBO(diff) 0.520 / 0.871 / 0.523 / 0.704; SPA p 0.031 / 0.193 / 0.124 / 0.526.) The one
SPA p under 0.10 (1 min / L1) names `not_block`: "BLOCK rows are slightly worse than the rest" (BLOCK -1,050 vs pool -1,010, diff
+60 on a kept book of -990 per trade, permutation p 0.49, 6 of 12 blocks, control 99.3). It is not a candidate: its kept book loses
990 INR per trade at 5 pts slippage and 1,380 at 8, and it is the inverse of the gate (keep 67% of everything), not a gate. No
`candidates/` JSON is written.

## 8. Verdict per timeframe

**1 min (ST7, Strategy 1 rules).** The frozen gate is not a loser filter. Its skip pile is 84.7% losers against a base loser rate of
84.4% (lift 1.003 on L1, 1.003 on L0); its loser recall (0.835) equals its skip share (0.833). It keeps 745 of 4,452 SETUPs and
throws away 82.7% of the winners' net (L1; 83.9% on L0), 84.3% of the top-decile winners and 225 of the 268 pts >= 50 winners
(1.48M of 1.77M INR). Kept mean -1,026 vs skipped -1,006 (diff -19.7, control 64.7th percentile, permutation p 0.86; L0 diff -129,
50th percentile). Its 3.73M gain over Foundation on L1 is 3.88M of avoided costs and -0.15M of selection. The late runners are the
`eod`-cut trades held 61-375 bars, concentrated before 09:25 (all 28 skipped) and in the 14:00 bin (58 of 62 skipped); the gate
keeps them at 13-18%, no better than its base rate.

**5 min (ST8, Strategy 2 rules).** Not a loser filter either: precision 0.721 vs base 0.723 (lift 0.997; L0 0.993), recall 0.605 =
skip share 0.607. It keeps 325 of 826 and throws away 63.1% of the winners' net (L1; 60.3% on L0), 56.5% of the top-decile winners,
95 of 148 big winners (654k of 1.03M). Here the gate keeps the worse side: kept -979 vs skipped -613 (diff -366, 11.6th percentile,
p 0.25), and its own book is worse still (-1,108) because 97 REENTERs exit worse than Foundation's trade (-431 each). The gain over
Foundation (265k) is 526k of avoided costs and -261k of selection. The refused leave branch (`leave_into_recycle` 98 rows at -32,
`leave_vol_fail` 113 at -114, `leave_gap_quiet` 12 at +170) is where the winners it refuses sit; `skip_only:WATCH:leave_into_recycle`
(diff -822, 0.1th percentile, permutation p 0.088) is the family's nearest thing to a signal and it points against the frozen rule.
Late runners: the morning entry held to 15:25 (61-120 bars: 40 of 52 big winners skipped) and the pre-09:25 SETUPs (14 of 15).

**H1 answer:** on both timeframes the frozen ST7/ST8 gate skips losers exactly in proportion to how much it skips; it separates
nothing (kept-vs-skipped difference within the random band on all four tables), it removes 63-83% of the winners' net, and its
whole advantage over Foundation is the cost saved by trading less. **Null result: no candidate config.**

## 9. Cross-check against the local h1 tables (`fz_v3/built/study/h1_1m_IS_*.csv`: L0 label, 1 min, IS, local build)

Where the definitions coincide (L0 label, 1 min, IS) the cloud tables agree with the local ones exactly: all 16 group tables
(`outcome_gate`, `gate_at`, `block_key`, `read`, `branch`, `take_why`, `hour_bin`, `dir`, `visit_bin`, `zone_kind`, `exit_reason`,
`pts_bucket`, `hold_bucket`, `cross_session`, `pos_kind`, `entered_read`) match on n, kept, net, winners, big, huge, kept net,
skipped net and big skipped to < 0.01 INR with no unmatched group, and the skipped big-winner list is the same 250 SETUPs (pts sum
43,050.4 both sides) (`h1_summary.json` -> `crosscheck_local_1m_L0`). The local run's control percentile of the FZ book
(DESIGN_PANEL: 39.6th / 57th) and the cloud selection-only percentiles (1 min L0 50.0, 5 min L0 28.1) are not expected to
coincide (different tag seeds and, locally, the FZ book rather than the selection-only book), and all of them sit in the random band.
Only IS files under `built/study/` were read.

## 10. What would falsify these findings

- A frozen-gate ledger row with diff > 0 and control percentile >= 95 on either label: the four rows here have diff -19.7 / -129.5
  (1 min) and -365.6 / -0.7 (5 min) at percentiles 64.7 / 50.0 / 11.6 / 28.1.
- A skip-pile precision above the base loser rate by more than sampling error (about +-0.012 at 3,707 skips on 1 min, +-0.04 at 501
  on 5 min): observed +0.003 / -0.002.
- A positive avoided price move (the skipped rows losing money before costs) on any table: all four are negative.
- A big-winner kept share above the gate's own kept share (0.167 / 0.394): observed 0.160 / 0.358.
- A different `fz_traded` set on a rebuild (the QUALITY.md cross-check pins 745 / 325 kept and identical FZ positions to the local build).

## 11. Caveats

- The group tables and the big-winner audit are descriptive breakdowns of the `frozen` ledger row; they were not used to choose a rule,
  and nothing in them is a kept-vs-skipped candidate except the ledger rows in section 3.
- `block_key`, `not_block` and the `skip_only:*` variants use the post-SETUP outcome gate (11 IS rows on 1 min differ from the as-of
  gate; 96 on 5 min are WATCH-as-of rows that re-entered a bar later). The as-of translation of `not_block` was scored post-hoc.
- The FZ-book table (`h1/fz_book`) keeps the label's exit bar for `with_label` (the splitter is not used in this study).
- The control percentile matches per-session counts while `diff` pools rows, so their signs can disagree for near-complete keeps
  (section 1); neither is read alone.
- L0 on 1 min runs to 70 sessions and its big winners are multi-session; the L0 columns are robustness only.
- `lift` is not a harness metric; it is `loser_precision` (ledger) over the IS base loser rate.
