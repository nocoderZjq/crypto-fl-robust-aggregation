from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.fl.trainer import run_experiment
from src.utils.config import apply_overrides, load_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--method", default="fedavg")
    parser.add_argument("--output", default="outputs/csv/results.csv")
    parser.add_argument("--rounds", type=int)
    parser.add_argument("--clients", type=int)
    parser.add_argument("--clients-per-round", type=int)
    parser.add_argument("--malicious-ratio", type=float)
    parser.add_argument("--attack-type")
    parser.add_argument("--dataset")
    parser.add_argument("--model")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--overwrite-results", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    config = apply_overrides(
        config,
        {
            "num_rounds": args.rounds,
            "num_clients": args.clients,
            "clients_per_round": args.clients_per_round,
            "malicious_ratio": args.malicious_ratio,
            "attack_type": args.attack_type,
            "dataset": args.dataset,
            "model": args.model,
            "seed": args.seed,
            "overwrite_results": args.overwrite_results,
        },
    )
    run_experiment(config, method=args.method, output_path=args.output)


if __name__ == "__main__":
    main()
