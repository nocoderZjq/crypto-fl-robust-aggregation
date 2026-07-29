from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.fl.trainer import run_experiment
from src.utils.config import load_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/mnist_label_flip.yaml")
    parser.add_argument("--output", default="outputs/csv/results.csv")
    parser.add_argument("--methods", nargs="+", default=["fedavg", "krum", "trimmed_mean", "plain_srsf", "pp_srsf"])
    parser.add_argument("--attacks", nargs="+", default=["label_flip", "sign_flip", "gaussian_noise"])
    parser.add_argument("--ratios", nargs="+", type=float, default=[0.0, 0.2, 0.3])
    args = parser.parse_args()
    base = load_config(args.config)
    output = Path(args.output)
    if output.exists():
        output.unlink()
    for method, attack, ratio in itertools.product(args.methods, args.attacks, args.ratios):
        config = dict(base)
        config["attack_type"] = attack
        config["malicious_ratio"] = ratio
        config["overwrite_results"] = False
        print(f"=== method={method} attack={attack} ratio={ratio} ===")
        run_experiment(config, method=method, output_path=args.output)


if __name__ == "__main__":
    main()
