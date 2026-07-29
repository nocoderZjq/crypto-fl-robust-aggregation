from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.fl.trainer import run_experiment
from src.utils.config import load_config


def advanced_config() -> dict:
    return load_config(str(ROOT / "configs" / "mnist_tinycnn_advanced.yaml"))


def run_suite() -> None:
    out_dir = ROOT / "outputs" / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)

    fedgt_out = out_dir / "fedgt_aligned_mnist.csv"
    if fedgt_out.exists():
        fedgt_out.unlink()
    for seed in [2141, 2142, 2143]:
        config = advanced_config()
        config.update(
            {
                "attack_type": "label_flip",
                "seed": seed,
                "overwrite_results": False,
            }
        )
        run_experiment(config, method="fedgt_nhat", output_path=str(fedgt_out))

    fashion_out = out_dir / "fashion_multiseed.csv"
    if fashion_out.exists():
        fashion_out.unlink()
    for seed in [2221, 2222, 2223]:
        for method in ["fedavg", "pp_srsf", "pp_srsf_trust", "fedgt_nhat"]:
            config = advanced_config()
            config.update(
                {
                    "dataset": "fashion_mnist",
                    "num_rounds": 10,
                    "attack_type": "label_flip",
                    "seed": seed,
                    "overwrite_results": False,
                }
            )
            run_experiment(config, method=method, output_path=str(fashion_out))


if __name__ == "__main__":
    run_suite()
