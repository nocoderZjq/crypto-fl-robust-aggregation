#!/usr/bin/env bash
set -euo pipefail

python experiments/run_grid.py \
  --config configs/mnist_tinycnn_strength.yaml \
  --output outputs/csv/mnist_tinycnn_strength.csv \
  --methods fedavg trimmed_mean plain_srsf pp_srsf \
  --attacks label_flip sign_flip gaussian_noise \
  --ratios 0.0 0.1 0.2 0.3

python experiments/run_grid.py \
  --config configs/fashion_tinycnn_strength.yaml \
  --output outputs/csv/fashion_tinycnn_strength.csv \
  --methods fedavg trimmed_mean plain_srsf pp_srsf \
  --attacks label_flip sign_flip gaussian_noise \
  --ratios 0.0 0.2

python experiments/summarize.py --results outputs/csv/mnist_tinycnn_strength.csv
