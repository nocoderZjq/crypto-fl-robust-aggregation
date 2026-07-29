import numpy as np

from src.crypto.fixed_point import encode_float
from src.crypto.beaver import secure_multiply
from src.crypto.secret_sharing import reconstruct, share
from src.crypto.secure_distance import secure_pairwise_distance_matrix, secure_squared_distance


def test_secure_distance_matches_quantized_plaintext_distance():
    p = 2**61 - 1
    scale = 1000
    x = np.array([0.1, -0.2, 0.3])
    y = np.array([0.0, 0.2, -0.1])
    qx = encode_float(x, scale=scale, modulus=p)
    qy = encode_float(y, scale=scale, modulus=p)
    sx = share(qx, modulus=p, seed=1)
    sy = share(qy, modulus=p, seed=2)
    expected = int(np.dot(np.rint((x - y) * scale), np.rint((x - y) * scale)))
    assert secure_squared_distance(sx, sy, modulus=p) == expected


def test_beaver_multiply_matches_plaintext_product():
    p = 2**61 - 1
    x = np.array([3, p - 4, 7], dtype=object)
    y = np.array([5, 6, p - 2], dtype=object)
    product_shares = secure_multiply(share(x, p, seed=3), share(y, p, seed=4), p, seed=5)
    assert reconstruct(*product_shares, modulus=p).tolist() == np.mod(x * y, p).tolist()


def test_secure_distance_reports_protocol_costs():
    p = 2**61 - 1
    shares = [share(np.array([i, i + 1], dtype=object), p, seed=i) for i in range(3)]
    matrix, metrics = secure_pairwise_distance_matrix(shares, p, seed=9, return_metrics=True)
    assert matrix.shape == (3, 3)
    assert metrics["secure_multiplications"] == 6
    assert metrics["protocol_online_bytes"] > 0
