from __future__ import annotations

import argparse

from src.fl.trainer import run_experiment
from src.utils.config import load_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/smoke.yaml")
    parser.add_argument("--method", default="pp_srsf")
    parser.add_argument("--output", default="outputs/csv/results.csv")
    args = parser.parse_args()
    config = load_config(args.config)
    run_experiment(config, method=args.method, output_path=args.output)


if __name__ == "__main__":
    main()
