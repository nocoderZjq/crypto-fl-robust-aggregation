#!/usr/bin/env bash
set -euo pipefail
python experiments/run_grid.py --config configs/mnist_label_flip.yaml --output outputs/csv/results.csv
python experiments/summarize.py --results outputs/csv/results.csv
