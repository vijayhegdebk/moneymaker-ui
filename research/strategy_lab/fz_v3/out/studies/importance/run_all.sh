#!/bin/bash
# The real run. One thread per fit (bag_probe.log / xgb_probe.log: on the shared 4-core box a 1-thread fit is faster than a
# 4-thread one; the fitted trees are identical either way, random_state fixes them). The stages of one timeframe are independent
# processes (per-stage seeds), so they run in parallel; finalize merges them; shortlist.py freezes the vocabulary.
# In the 2026-09-29 run the 5minute timeframe ran as one `--stage all` process (started before the split) and minute as the
# three parallel stages below; the numbers do not depend on the split.
cd "$(dirname "$0")"
export IMP_BAG_JOBS=1 IMP_XGB_JOBS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for tf in 5minute minute; do
  for st in main sfi cpcv; do
    nohup python run_importance.py --tf $tf --stage $st > run_${tf}_${st}.nohup 2>&1 &
  done
done
wait
for tf in 5minute minute; do python run_importance.py --tf $tf --stage finalize > run_${tf}_finalize.nohup 2>&1; done
python shortlist.py > shortlist.log 2>&1
echo "run_all done $(date -Is)" >> shortlist.log
