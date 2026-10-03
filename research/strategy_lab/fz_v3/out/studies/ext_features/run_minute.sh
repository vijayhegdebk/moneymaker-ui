#!/bin/bash
# the 1-minute builds (full tape, then the truncated tape) and the finalisation; logs stay in this folder
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python build_ext.py --tf minute --data ../../data/minute --out ../../features_ext/minute > build_minute.log 2>&1
python build_ext.py --tf minute --data ../../data/minute/trunc_20250630_120000 --out ../../features_ext/minute/trunc_20250630_120000 > build_minute_trunc.log 2>&1
python finalize.py --tf minute > finalize_minute.log 2>&1
echo DONE >> finalize_minute.log
