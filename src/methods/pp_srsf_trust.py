from __future__ import annotations

import time

import numpy as np
import torch

from src.crypto.fixed_point import encode_float
from src.crypto.secret_sharing import share
from src.crypto.secure_aggregation import secure_average_deltas
from src.crypto.secure_distance import secure_pairwise_distance_matrix
from src.fl.aggregation import Delta, flatten_delta, flatten_deltas, krum_scores_from_distance
from src.methods.plaintext_srsf import random_projection


def _zscore(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.float64)
    std = values.std()
    if std < 1e-12:
        return np.zeros_like(values)
    return (values - values.mean()) / std


def pp_srsf_trust_aggregate(
    deltas: list[Delta],
    f: int,
    sketch_dim: int = 64,
    quantization_scale: int = 1000,
    modulus: int = 2**61 - 1,
    seed: int = 0,
    history_scores: list[float] | None = None,
    validation_scores: list[float] | None = None,
    distance_weight: float = 1.0,
    norm_weight: float = 0.25,
    history_weight: float = 0.35,
    validation_weight: float = 0.75,
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

    krum_scores = krum_scores_from_distance(distance, f=f).numpy()
    norm_values = np.asarray([float(torch.linalg.vector_norm(flatten_delta(delta))) for delta in deltas])
    norm_deviation = np.abs(norm_values - np.median(norm_values))
    history = np.asarray(history_scores if history_scores is not None else [0.0] * len(deltas), dtype=np.float64)
    validation = np.asarray(validation_scores if validation_scores is not None else [0.0] * len(deltas), dtype=np.float64)

    composite = (
        distance_weight * _zscore(krum_scores)
        + norm_weight * _zscore(norm_deviation)
        - history_weight * _zscore(history)
        - validation_weight * _zscore(validation)
    )
    keep = max(1, len(deltas) - f)
    selected = np.argsort(composite)[:keep].tolist()
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
        "trust_score_mean": float(np.mean(validation)) if len(validation) else 0.0,
        **protocol_metrics,
    }
