from __future__ import annotations

import numpy as np


def share(x, modulus: int = 2**61 - 1, seed: int | None = None):
    arr = np.asarray(x, dtype=object)
    rng = np.random.default_rng(seed)
    share_a = rng.integers(0, min(modulus, np.iinfo(np.int64).max), size=arr.shape, dtype=np.int64).astype(object)
    share_b = np.mod(arr - share_a, modulus).astype(object)
    return share_a, share_b


def reconstruct(share_a, share_b, modulus: int = 2**61 - 1):
    return np.mod(np.asarray(share_a, dtype=object) + np.asarray(share_b, dtype=object), modulus).astype(object)
