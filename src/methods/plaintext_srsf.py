from __future__ import annotations

import time

import torch

from src.fl.aggregation import Delta, average_deltas, flatten_deltas, select_by_krum_scores


def random_projection(vectors: torch.Tensor, sketch_dim: int, seed: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    projection = torch.randn(sketch_dim, vectors.shape[1], generator=generator) / (sketch_dim ** 0.5)
    return vectors @ projection.t()


def plaintext_srsf_aggregate(
    deltas: list[Delta],
    f: int,
    sketch_dim: int = 64,
    seed: int = 0,
) -> tuple[Delta, list[int], dict[str, float]]:
    start = time.perf_counter()
    vectors = flatten_deltas(deltas)
    sketches = random_projection(vectors, sketch_dim=sketch_dim, seed=seed)
    distance = torch.cdist(sketches, sketches, p=2).pow(2)
    selected = select_by_krum_scores(distance, f=f)
    aggregation_start = time.perf_counter()
    avg = average_deltas([deltas[i] for i in selected])
    end = time.perf_counter()
    model_bytes = int(sum(v.numel() for v in deltas[0].values()) * len(deltas) * 4)
    sketch_bytes = int(len(deltas) * sketch_dim * 4)
    return avg, selected, {
        "crypto_time_ms": 0.0,
        "aggregation_time_ms": (end - aggregation_start) * 1000,
        "filter_time_ms": (aggregation_start - start) * 1000,
        "communication_bytes": model_bytes + sketch_bytes,
    }
