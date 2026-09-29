#!/bin/bash
# dry test of the staged script (20 trees, no ledger rows): main and sfi in parallel, then finalize, then the shortlist writer
cd "$(dirname "$0")"
export IMP_BAG_JOBS=1 IMP_XGB_JOBS=1 OMP_NUM_THREADS=1
rm -f dry/run_5minute.log
python run_importance.py --tf 5minute --dry --stage main > dry_stage_main.nohup 2>&1 &
python run_importance.py --tf 5minute --dry --stage sfi > dry_stage_sfi.nohup 2>&1 &
wait
python run_importance.py --tf 5minute --dry --stage finalize > dry_stage_finalize.nohup 2>&1
python shortlist.py --dry > dry_shortlist.nohup 2>&1
echo "dry_stages done $(date -Is)" >> dry_stage_finalize.nohup
