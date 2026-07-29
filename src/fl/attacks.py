from __future__ import annotations

import torch

from .aggregation import Delta, apply_scale, random_like_delta


def flip_labels(y: torch.Tensor, num_classes: int = 10, mode: str = "reverse") -> torch.Tensor:
    mode = mode.lower()
    if mode in {"reverse", "label_flip"}:
        return (num_classes - 1) - y
    if mode in {"pairwise", "label_flip_pairwise"}:
        return (y + 1) % num_classes
    if mode in {"all_to_one", "label_flip_all_to_one"}:
        return torch.zeros_like(y)
    raise ValueError(f"Unknown label-flip mode: {mode}")


def apply_update_attack(
    delta: Delta,
    attack_type: str,
    scale: float = 5.0,
    sigma: float = 1.0,
    seed: int | None = None,
) -> Delta:
    attack_type = attack_type.lower()
    if attack_type in {"none", "no_attack", "label_flip", "label_flip_pairwise", "label_flip_all_to_one"}:
        return delta
    if attack_type == "sign_flip":
        return apply_scale(delta, -scale)
    if attack_type == "gaussian_noise":
        return random_like_delta(delta, sigma=sigma, seed=seed)
    raise ValueError(f"Unknown attack type: {attack_type}")
