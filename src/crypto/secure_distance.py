from __future__ import annotations

import numpy as np

from .beaver import secure_multiply
from .secret_sharing import reconstruct


def secure_squared_distance(
    shares_i,
    shares_j,
    modulus: int = 2**61 - 1,
    seed: int | None = None,
) -> int:
    """Reveal a squared distance while keeping both input sketches shared."""
    diff_a = np.mod(
        np.asarray(shares_i[0], dtype=object) - np.asarray(shares_j[0], dtype=object),
        modulus,
    )
    diff_b = np.mod(
        np.asarray(shares_i[1], dtype=object) - np.asarray(shares_j[1], dtype=object),
        modulus,
    )
    square_a, square_b = secure_multiply(
        (diff_a, diff_b),
        (diff_a, diff_b),
        modulus=modulus,
        seed=seed,
    )
    distance = reconstruct(np.sum(square_a) % modulus, np.sum(square_b) % modulus, modulus)
    return int(np.asarray(distance, dtype=object).item())


def secure_pairwise_distance_matrix(
    all_shares,
    modulus: int = 2**61 - 1,
    seed: int = 0,
    return_metrics: bool = False,
):
    n = len(all_shares)
    sketch_dim = int(np.asarray(all_shares[0][0]).size) if n else 0
    distance = np.zeros((n, n), dtype=np.float64)
    pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = secure_squared_distance(all_shares[i], all_shares[j], modulus, seed=seed + pairs * 7)
            distance[i, j] = distance[j, i] = d
            pairs += 1
    if not return_metrics:
        return distance
    multiplications = pairs * sketch_dim
    metrics = {
        "secure_multiplications": multiplications,
        "protocol_online_bytes": (4 * multiplications + 2 * pairs) * 8,
        "protocol_offline_bytes": 6 * multiplications * 8,
    }
    return distance, metrics
