from __future__ import annotations

from collections import OrderedDict
from typing import Iterable

import torch


Delta = OrderedDict[str, torch.Tensor]


def clone_state(state: dict[str, torch.Tensor]) -> OrderedDict[str, torch.Tensor]:
    return OrderedDict((k, v.detach().clone()) for k, v in state.items())


def diff_states(new_state: dict[str, torch.Tensor], old_state: dict[str, torch.Tensor]) -> Delta:
    return OrderedDict((k, new_state[k].detach().cpu() - old_state[k].detach().cpu()) for k in old_state)


def add_delta_to_model(model: torch.nn.Module, delta: Delta, scale: float = 1.0) -> None:
    state = model.state_dict()
    updated = OrderedDict((k, state[k].detach().cpu() + delta[k] * scale) for k in state)
    model.load_state_dict(updated)


def average_deltas(deltas: list[Delta]) -> Delta:
    if not deltas:
        raise ValueError("Cannot average an empty delta list")
    return OrderedDict((k, torch.stack([d[k] for d in deltas]).mean(dim=0)) for k in deltas[0])


def flatten_delta(delta: Delta) -> torch.Tensor:
    return torch.cat([v.reshape(-1).float() for v in delta.values()])


def flatten_deltas(deltas: list[Delta]) -> torch.Tensor:
    return torch.stack([flatten_delta(d) for d in deltas])


def unflatten_vector(vector: torch.Tensor, template: Delta) -> Delta:
    out: Delta = OrderedDict()
    offset = 0
    for key, value in template.items():
        n = value.numel()
        out[key] = vector[offset : offset + n].reshape_as(value).to(value.dtype)
        offset += n
    return out


def apply_scale(delta: Delta, factor: float) -> Delta:
    return OrderedDict((k, v * factor) for k, v in delta.items())


def random_like_delta(delta: Delta, sigma: float, seed: int | None = None) -> Delta:
    generator = torch.Generator()
    if seed is not None:
        generator.manual_seed(seed)
    return OrderedDict((k, torch.randn(v.shape, generator=generator) * sigma) for k, v in delta.items())


def krum_scores_from_distance(distance: torch.Tensor, f: int) -> torch.Tensor:
    n = distance.shape[0]
    k = max(1, min(n - 1, n - f - 2))
    masked = distance.clone()
    masked.fill_diagonal_(float("inf"))
    nearest, _ = torch.topk(masked, k=k, largest=False, dim=1)
    return nearest.sum(dim=1)


def select_by_krum_scores(distance: torch.Tensor, f: int) -> list[int]:
    n = distance.shape[0]
    keep = max(1, n - f)
    scores = krum_scores_from_distance(distance, f)
    return torch.argsort(scores)[:keep].tolist()


def fedavg(deltas: list[Delta]) -> tuple[Delta, list[int]]:
    return average_deltas(deltas), list(range(len(deltas)))


def krum(deltas: list[Delta], f: int) -> tuple[Delta, list[int]]:
    vectors = flatten_deltas(deltas)
    distance = torch.cdist(vectors, vectors, p=2).pow(2)
    selected = select_by_krum_scores(distance, f)
    return average_deltas([deltas[i] for i in selected]), selected


def trimmed_mean(deltas: list[Delta], trim_ratio: float) -> tuple[Delta, list[int]]:
    vectors = flatten_deltas(deltas)
    n = vectors.shape[0]
    trim = min(int(trim_ratio * n), max(0, (n - 1) // 2))
    sorted_vals, _ = torch.sort(vectors, dim=0)
    trimmed = sorted_vals[trim : n - trim] if trim > 0 else sorted_vals
    return unflatten_vector(trimmed.mean(dim=0), deltas[0]), list(range(n))


def coordinate_median(deltas: list[Delta]) -> tuple[Delta, list[int]]:
    vectors = flatten_deltas(deltas)
    return unflatten_vector(vectors.median(dim=0).values, deltas[0]), list(range(len(deltas)))
