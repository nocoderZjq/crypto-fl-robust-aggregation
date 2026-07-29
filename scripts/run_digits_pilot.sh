#!/usr/bin/env bash
set -euo pipefail
python experiments/run_grid.py \
  --config configs/digits_pilot.yaml \
  --output outputs/csv/digits_pilot.csv \
  --methods fedavg secure_fedavg krum trimmed_mean coordinate_median plain_srsf pp_srsf \
  --attacks label_flip sign_flip gaussian_noise \
  --ratios 0.0 0.2 0.3
python experiments/summarize.py --results outputs/csv/digits_pilot.csv
