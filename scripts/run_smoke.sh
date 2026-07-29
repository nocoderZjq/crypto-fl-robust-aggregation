#!/usr/bin/env bash
set -euo pipefail
python experiments/run_single.py --config configs/smoke.yaml --method pp_srsf --output outputs/csv/results.csv --overwrite-results
python experiments/summarize.py --results outputs/csv/results.csv
