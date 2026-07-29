import numpy as np

from src.crypto.secret_sharing import reconstruct, share


def test_secret_sharing_reconstructs_vector():
    p = 2**61 - 1
    x = np.array([1, 2, p - 3, 42], dtype=object)
    a, b = share(x, modulus=p, seed=1)
    rec = reconstruct(a, b, modulus=p)
    assert rec.tolist() == x.tolist()
