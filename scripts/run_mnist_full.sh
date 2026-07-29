#!/usr/bin/env bash
set -euo pipefail
python experiments/run_single.py --config configs/mnist_label_flip.yaml --method fedavg --output outputs/csv/results.csv --overwrite-results
python experiments/run_single.py --config configs/mnist_label_flip.yaml --method krum --output outputs/csv/results.csv
python experiments/run_single.py --config configs/mnist_label_flip.yaml --method trimmed_mean --output outputs/csv/results.csv
python experiments/run_single.py --config configs/mnist_label_flip.yaml --method plain_srsf --output outputs/csv/results.csv
python experiments/run_single.py --config configs/mnist_label_flip.yaml --method pp_srsf --output outputs/csv/results.csv
python experiments/summarize.py --results outputs/csv/results.csv
