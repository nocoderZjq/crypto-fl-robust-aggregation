# Reproducibility Guide

This repository contains all source code, CSV logs, figures, LaTeX sources, and the compiled PDF for the Modern Cryptography course report.

## Environment

```powershell
python -m pip install -r requirements.txt
```

For the exact final-run environment, use `requirements-lock.txt`.

The report PDF is compiled with XeLaTeX and BibTeX. The latest compiled file is:


## Quick Check

```powershell
pytest -q
python experiments/run_single.py --config configs/smoke.yaml --method pp_srsf --output outputs/csv/results.csv --overwrite-results
python experiments/summarize.py --results outputs/csv/results.csv
```

## Main Experiment Commands

MNIST pilot:

```powershell
python experiments/run_grid.py --config configs/mnist_pilot.yaml --output outputs/csv/mnist_pilot.csv --methods fedavg secure_fedavg krum trimmed_mean coordinate_median plain_srsf pp_srsf --attacks label_flip sign_flip gaussian_noise --ratios 0.0 0.2 0.3
python experiments/summarize.py --results outputs/csv/mnist_pilot.csv
```

MNIST+TinyCNN 20-round focused experiment:

```powershell
python experiments/run_grid.py --config configs/mnist_tinycnn_long.yaml --output outputs/csv/mnist_tinycnn_long.csv --methods fedavg plain_srsf pp_srsf --attacks label_flip sign_flip gaussian_noise --ratios 0.0 0.2
python experiments/summarize.py --results outputs/csv/mnist_tinycnn_long.csv
```

MNIST/Fashion-MNIST malicious-ratio stress experiments:

```powershell
python experiments/run_grid.py --config configs/mnist_tinycnn_strength.yaml --output outputs/csv/mnist_tinycnn_strength.csv --methods fedavg trimmed_mean plain_srsf pp_srsf --attacks label_flip sign_flip gaussian_noise --ratios 0.0 0.1 0.2 0.3
python experiments/run_grid.py --config configs/fashion_tinycnn_strength.yaml --output outputs/csv/fashion_tinycnn_strength.csv --methods fedavg trimmed_mean plain_srsf pp_srsf --attacks label_flip sign_flip gaussian_noise --ratios 0.0 0.2
python experiments/summarize.py --results outputs/csv/mnist_tinycnn_strength.csv
```

Advanced supplementary experiments:

```powershell
python scripts/run_advanced_experiments.py
python scripts/run_completion_experiments.py
python scripts/summarize_advanced_experiments.py
python scripts/benchmark_secure_distance.py
python scripts/localize_report_figures.py
```

## Output Map

```text
outputs/csv/mnist_pilot.csv
outputs/csv/mnist_tinycnn_long.csv
outputs/csv/mnist_tinycnn_strength.csv
outputs/csv/fashion_tinycnn_strength.csv
outputs/csv/advanced_label_flip.csv
outputs/csv/advanced_sketch_ablation.csv
outputs/csv/advanced_seed_stats.csv
outputs/csv/advanced_majority.csv
outputs/csv/fedgt_aligned_mnist.csv
outputs/csv/fashion_multiseed.csv
outputs/csv/secure_distance_benchmark.csv

outputs/tables/*.csv
outputs/figures/*.png
```

## Rebuild the PDF

```powershell
Copy-Item report\main.tex report\jcr_main.tex -Force
Set-Location report
xelatex --interaction=nonstopmode --halt-on-error main.tex
bibtex main
xelatex --interaction=nonstopmode --halt-on-error main.tex
xelatex --interaction=nonstopmode --halt-on-error main.tex
Set-Location ..
Copy-Item report\main.pdf output\pdf\现代密码学课程报告_曾嘉祺_最终提交版.pdf -Force
```

## Notes

All experiment configs expose random seeds. `configs/mnist_tinycnn_advanced.yaml` reserves 600 training samples as a public validation set, so Trust/FedGT-style scoring never reads the test set. The current implementation is a semi-honest Beaver-triple prototype with simulated preprocessing, not a malicious-secure MPC deployment.
