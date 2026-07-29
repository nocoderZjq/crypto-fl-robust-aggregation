# Privacy-Preserving Robust Federated Aggregation

This repository is a reproducible course-report prototype for the Modern Cryptography topic:
抗标签翻转与拜占庭攻击的密文域鲁棒安全聚合模型.

The implemented method is PP-SRSF: Privacy-Preserving Sketch-based Robust Similarity Filtering.
Each client trains locally, compresses its model update into a random-projection sketch, secret-shares
the quantized sketch to two non-colluding aggregators, evaluates sketch distances with Beaver triples,
and aggregates retained updates with pairwise canceling masks.

## What Is Included

- PyTorch federated learning on MNIST, Fashion-MNIST, CIFAR-10, and a fast FakeData smoke dataset.
- IID and Dirichlet non-IID partitioning.
- Label-flipping, sign-flipping, and Gaussian-noise Byzantine attacks.
- FedAvg, FedAvg + SecureAgg, Krum, Trimmed Mean, Coordinate Median, Plain-SRSF, PP-SRSF, PP-SRSF+History/Trust, a transparent FedGT-style ridge proxy, and a paper-aligned FedGT-n-hat adaptation.
- Additive sharing, fixed-point quantization, Beaver-triple sketch distance, and pairwise-masked aggregation.
- CSV logging, plotting, summary tables, tests, and report-ready protocol assets.

## Install

```bash
pip install -r requirements.txt
```

`requirements-lock.txt` records the exact package versions used for the final experiments.

## Quick Smoke Test

```bash
bash scripts/run_smoke.sh
```

On Windows without Bash:

```powershell
python experiments/run_single.py --config configs/smoke.yaml --method pp_srsf --output outputs/csv/results.csv --overwrite-results
python experiments/summarize.py --results outputs/csv/results.csv
```

## Offline Pilot Experiment

If MNIST cannot be downloaded in the current network environment, run the offline handwritten-digits pilot:

```bash
bash scripts/run_digits_pilot.sh
```

This uses `sklearn_digits`, not MNIST. It is useful for checking trends and generating a report draft, while
the final course report should replace it with MNIST/Fashion-MNIST results when the datasets are available.

## Main Experiments

```bash
bash scripts/run_mnist_pilot.sh
bash scripts/run_mnist_full.sh
bash scripts/run_attack_grid.sh
```

Results are written to `outputs/csv/results.csv`. Figures are written to `outputs/figures/`.
Tables are written to `outputs/tables/`.

MNIST loading includes a fallback downloader from the public CVDF/Google Storage mirror when the default
torchvision mirrors are unavailable.

## Methods

- `fedavg`: plain average of all client updates.
- `secure_fedavg`: masked aggregation without robust filtering.
- `krum`: plaintext distance-based robust filtering.
- `trimmed_mean`: coordinate-wise trimmed mean.
- `coordinate_median`: coordinate-wise median.
- `plain_srsf`: random-projection sketch filtering in plaintext.
- `pp_srsf`: secret-shared sketch filtering plus simplified secure aggregation.
- `pp_srsf_trust`: PP-SRSF with cross-round history and public-validation trust signals for label-flipping stress tests.
- `fedgt_proxy`: overlapping-group public-validation baseline inspired by FedGT; it uses ridge decoding and is not an exact reproduction of the published trellis forward-backward decoder.
- `fedgt_nhat`: paper-aligned small-system adaptation using utility/PCA group tests, malicious-count estimation, and exact posterior LLRs equivalent to exhaustive trellis decoding.

## Advanced Supplementary Experiments

```powershell
python scripts\run_advanced_experiments.py
python scripts\run_completion_experiments.py
python scripts\summarize_advanced_experiments.py
python scripts\benchmark_secure_distance.py
```

These scripts generate 20-round label-flipping results, three-seed sketch ablations, 60% malicious-client
stress tests, and protocol-scaling measurements under `outputs/csv/`, `outputs/tables/`, and `outputs/figures/`.
Trust and FedGT-style experiments reserve a stratified public validation subset from training data; the test
set is used only for evaluation.

## Security Model

This is a course prototype under a semi-honest, two-aggregator non-collusion assumption. The distance code
opens only Beaver-masked differences and final distance statistics, not input sketches. Triple preprocessing
is simulated by a trusted dealer, so authenticated malicious security, dropout resilience, an encrypted
geometric median, and formal convergence proofs remain future work.

## Reproducibility

All random operations accept a seed in the YAML configs. The smoke test is intentionally small enough for a CPU.
Full MNIST/Fashion-MNIST runs use a sample cap by default to keep course-report iteration practical.

For the exact command map used by the final course report, see `REPRODUCE.md`.
