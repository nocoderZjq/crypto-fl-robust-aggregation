import numpy as np

from src.methods.fedgt_exact import (
    estimate_malicious_count,
    posterior_malicious_probabilities,
)
from src.methods.fedgt_proxy import make_group_matrix


def test_group_matrix_has_distinct_nontrivial_columns():
    matrix = make_group_matrix(n_clients=10, n_tests=8, group_size=5, seed=4)
    assert matrix.shape == (8, 10)
    assert np.unique(matrix.T, axis=0).shape[0] == 10
    assert np.all(matrix.sum(axis=0) > 0)
    assert np.all(matrix.sum(axis=1) >= 2)


def test_exact_decoder_identifies_single_positive_identity_test():
    matrix = np.eye(4, dtype=np.int8)
    tests = np.array([0, 1, 0, 0], dtype=np.int8)
    estimated = estimate_malicious_count(matrix, tests, max_malicious=3)
    posterior = posterior_malicious_probabilities(
        matrix,
        tests,
        prevalence=0.25,
        crossover_probability=0.01,
    )
    assert estimated == 1
    assert int(np.argmax(posterior)) == 1
