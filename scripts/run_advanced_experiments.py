from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.fl.trainer import run_experiment
from src.utils.config import load_config


def base_config() -> dict:
    return load_config(str(ROOT / "configs" / "mnist_tinycnn_advanced.yaml"))


def run_suite():
    out_dir = ROOT / "outputs" / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)

    label_out = out_dir / "advanced_label_flip.csv"
    if label_out.exists():
        label_out.unlink()
    for attack in ["label_flip", "label_flip_pairwise", "label_flip_all_to_one"]:
        for method in ["fedavg", "pp_srsf", "pp_srsf_trust", "fedgt_proxy"]:
            cfg = base_config()
            cfg.update({"attack_type": attack, "seed": 2131, "overwrite_results": False})
            run_experiment(cfg, method=method, output_path=str(label_out))

    sketch_out = out_dir / "advanced_sketch_ablation.csv"
    if sketch_out.exists():
        sketch_out.unlink()
    for seed in [2161, 2162, 2163]:
        for sketch_dim in [8, 16, 32, 64, 128]:
            for method in ["pp_srsf", "pp_srsf_trust"]:
                cfg = base_config()
                cfg.update(
                    {
                        "num_rounds": 15,
                        "attack_type": "sign_flip",
                        "seed": seed,
                        "sketch_dim": sketch_dim,
                        "overwrite_results": False,
                    }
                )
                run_experiment(cfg, method=method, output_path=str(sketch_out))

    seeds_out = out_dir / "advanced_seed_stats.csv"
    if seeds_out.exists():
        seeds_out.unlink()
    for seed in [2141, 2142, 2143]:
        for method in ["fedavg", "pp_srsf", "pp_srsf_trust", "fedgt_proxy"]:
            cfg = base_config()
            cfg.update({"attack_type": "label_flip", "seed": seed, "overwrite_results": False})
            run_experiment(cfg, method=method, output_path=str(seeds_out))

    majority_out = out_dir / "advanced_majority.csv"
    if majority_out.exists():
        majority_out.unlink()
    for attack in ["sign_flip", "label_flip"]:
        for ratio in [0.4, 0.5, 0.6]:
            for method in ["fedavg", "pp_srsf", "pp_srsf_trust", "fedgt_proxy"]:
                cfg = base_config()
                cfg.update(
                    {
                        "num_rounds": 15,
                        "attack_type": attack,
                        "malicious_ratio": ratio,
                        "seed": 2180,
                        "overwrite_results": False,
                    }
                )
                run_experiment(cfg, method=method, output_path=str(majority_out))


if __name__ == "__main__":
    run_suite()
