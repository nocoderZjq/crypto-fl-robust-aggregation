from __future__ import annotations

import numpy as np

from .secret_sharing import reconstruct, share


def generate_beaver_triple(shape, modulus: int = 2**61 - 1, seed: int | None = None):
    """Simulate trusted preprocessing of shares of (a, b, a*b)."""
    rng = np.random.default_rng(seed)
    limit = min(modulus, np.iinfo(np.int64).max)
    a = rng.integers(0, limit, size=shape, dtype=np.int64).astype(object)
    b = rng.integers(0, limit, size=shape, dtype=np.int64).astype(object)
    c = np.mod(a * b, modulus).astype(object)
    return (
        share(a, modulus=modulus, seed=None if seed is None else seed + 1),
        share(b, modulus=modulus, seed=None if seed is None else seed + 2),
        share(c, modulus=modulus, seed=None if seed is None else seed + 3),
    )


def secure_multiply(x_shares, y_shares, modulus: int = 2**61 - 1, seed: int | None = None):
    """Multiply additive shares by opening only Beaver-masked differences."""
    x_a, x_b = (np.asarray(part, dtype=object) for part in x_shares)
    y_a, y_b = (np.asarray(part, dtype=object) for part in y_shares)
    if x_a.shape != y_a.shape:
        raise ValueError("secure_multiply inputs must have matching shapes")

    (a_a, a_b), (b_a, b_b), (c_a, c_b) = generate_beaver_triple(x_a.shape, modulus, seed)
    e = reconstruct(np.mod(x_a - a_a, modulus), np.mod(x_b - a_b, modulus), modulus)
    f = reconstruct(np.mod(y_a - b_a, modulus), np.mod(y_b - b_b, modulus), modulus)

    z_a = np.mod(c_a + e * b_a + f * a_a + e * f, modulus).astype(object)
    z_b = np.mod(c_b + e * b_b + f * a_b, modulus).astype(object)
    return z_a, z_b


def simulated_secure_multiply(x_shares, y_shares, modulus: int = 2**61 - 1, seed: int | None = None):
    return secure_multiply(x_shares, y_shares, modulus=modulus, seed=seed)
