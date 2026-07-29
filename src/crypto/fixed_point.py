from __future__ import annotations

import numpy as np


def encode_float(x, scale: int = 1000, modulus: int = 2**61 - 1):
    arr = np.rint(np.asarray(x, dtype=np.float64) * scale).astype(np.int64)
    return np.mod(arr, modulus).astype(object)


def to_signed(x, modulus: int = 2**61 - 1):
    arr = np.asarray(x, dtype=object)
    half = modulus // 2
    signed = np.where(arr > half, arr - modulus, arr)
    return signed.astype(np.int64)


def decode_int(x, scale: int = 1000, modulus: int = 2**61 - 1):
    return to_signed(x, modulus).astype(np.float64) / scale
