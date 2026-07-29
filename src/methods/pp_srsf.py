from __future__ import annotations

import time

import numpy as np
import torch

from src.crypto.fixed_point import encode_float
from src.crypto.secret_sharing import share
from src.crypto.secure_aggregation import secure_average_deltas
from src.crypto.secure_distance import secure_pairwise_distance_matrix
from src.fl.aggregation import Delta, flatten_deltas, select_by_krum_scores
from src.methods.plaintext_srsf import random_projection


def pp_srsf_aggregate(
    deltas: list[Delta],
    f: int,
    sketch_dim: int = 64,
    quantization_scale: int = 1000,
    modulus: int = 2**61 - 1,
    seed: int = 0,
) -> tuple[Delta, list[int], dict[str, float]]:
    crypto_start = time.perf_counter()
    vectors = flatten_deltas(deltas)
    sketches = random_projection(vectors, sketch_dim=sketch_dim, seed=seed).numpy()
    encoded = [encode_float(s, scale=quantization_scale, modulus=modulus) for s in sketches]
    shares = [share(q, modulus=modulus, seed=seed + i + 17) for i, q in enumerate(encoded)]
    distance_np, protocol_metrics = secure_pairwise_distance_matrix(
        shares,
        modulus=modulus,
        seed=seed + 401,
        return_metrics=True,
    )
    distance = torch.as_tensor(distance_np, dtype=torch.float32)
    selected = select_by_krum_scores(distance, f=f)
    crypto_end = time.perf_counter()
    aggregation_start = time.perf_counter()
    avg = secure_average_deltas([deltas[i] for i in selected], seed=seed + 991)
    end = time.perf_counter()
    model_bytes = int(sum(v.numel() for v in deltas[0].values()) * len(deltas) * 4)
    sketch_share_bytes = int(len(deltas) * sketch_dim * 2 * 8)
    return avg, selected, {
        "crypto_time_ms": (crypto_end - crypto_start) * 1000,
        "aggregation_time_ms": (end - aggregation_start) * 1000,
        "communication_bytes": model_bytes + sketch_share_bytes,
        **protocol_metrics,
    }
