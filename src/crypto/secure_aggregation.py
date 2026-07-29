from __future__ import annotations

import torch

from src.fl.aggregation import Delta, flatten_delta, unflatten_vector


def secure_average_deltas(deltas: list[Delta], seed: int = 0) -> Delta:
    if not deltas:
        raise ValueError("No deltas to aggregate")
    vectors = [flatten_delta(d) for d in deltas]
    generator = torch.Generator().manual_seed(seed)
    masks = [torch.zeros_like(vectors[0]) for _ in vectors]
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            pair_mask = torch.randn(vectors[0].shape, generator=generator, dtype=vectors[0].dtype)
            masks[i] += pair_mask
            masks[j] -= pair_mask
    masked_sum = torch.stack([v + m for v, m in zip(vectors, masks)]).sum(dim=0)
    avg = masked_sum / len(vectors)
    return unflatten_vector(avg, deltas[0])
