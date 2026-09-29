#!/bin/bash
# The real run: both timeframes concurrently, one thread per fit (bag_probe.log / xgb_probe.log: on the shared 4-core box a 1-thread
# fit is faster than a 4-thread one; the fitted trees are identical either way, random_state fixes them). Then the shortlist.
cd "$(dirname "$0")"
export IMP_BAG_JOBS=1 IMP_XGB_JOBS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nohup python run_importance.py --tf 5minute > run_5minute.nohup 2>&1 &
nohup python run_importance.py --tf minute > run_minute.nohup 2>&1 &
wait
python shortlist.py > shortlist.log 2>&1
echo "run_all done $(date -Is)" >> shortlist.log
