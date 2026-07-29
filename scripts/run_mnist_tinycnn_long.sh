#!/usr/bin/env bash
set -euo pipefail
python experiments/run_grid.py \
  --config configs/mnist_tinycnn_long.yaml \
  --output outputs/csv/mnist_tinycnn_long.csv \
  --methods fedavg plain_srsf pp_srsf \
  --attacks label_flip sign_flip gaussian_noise \
  --ratios 0.0 0.2
python experiments/summarize.py --results outputs/csv/mnist_tinycnn_long.csv
