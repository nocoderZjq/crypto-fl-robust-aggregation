from __future__ import annotations

from itertools import combinations
import time

import numpy as np

from src.crypto.secure_aggregation import secure_average_deltas
from src.fl.aggregation import Delta


def make_group_matrix(n_clients: int, n_tests: int, group_size: int, seed: int) -> np.ndarray:
    """Create a balanced, code-like assignment matrix for overlapping groups."""
    n_tests = max(2, n_tests)
    group_size = max(2, min(group_size, n_clients - 1))
    rng = np.random.default_rng(seed)
    column_weight = int(round(n_tests * group_size / n_clients))
    column_weight = max(1, min(column_weight, n_tests - 1))
    candidates = np.zeros((0, n_tests), dtype=np.int8)
    candidate_rows = []
    for positions in combinations(range(n_tests), column_weight):
        column = np.zeros(n_tests, dtype=np.int8)
        column[list(positions)] = 1
        candidate_rows.append(column)
    if candidate_rows:
        candidates = np.stack(candidate_rows)
    if len(candidates) < n_clients:
        raise ValueError("Not enough distinct group-assignment columns")

    best_matrix = None
    best_score = float("-inf")
    for _ in range(512):
        columns = candidates[rng.choice(len(candidates), size=n_clients, replace=False)]
        matrix = columns.T
        pairwise = np.abs(columns[:, None, :] - columns[None, :, :]).sum(axis=2)
        pairwise += np.eye(n_clients, dtype=np.int64) * n_tests
        minimum_distance = int(pairwise.min())
        row_sizes = matrix.sum(axis=1)
        row_penalty = float(np.abs(row_sizes - group_size).sum())
        empty_penalty = float((row_sizes < 2).sum() * n_tests)
        score = 10.0 * minimum_distance - row_penalty - empty_penalty
        if score > best_score:
            best_score = score
            best_matrix = matrix
    return np.asarray(best_matrix, dtype=np.float64)


def fedgt_proxy_aggregate(
    deltas: list[Delta],
    f: int,
    group_matrix: np.ndarray,
    group_validation_scores: list[float],
    seed: int = 0,
) -> tuple[Delta, list[int], dict[str, float]]:
    """Decode public-validation group utilities with a transparent ridge proxy."""
    start = time.perf_counter()
    matrix = np.asarray(group_matrix, dtype=np.float64)
    scores = np.asarray(group_validation_scores, dtype=np.float64)
    if matrix.shape != (len(scores), len(deltas)):
        raise ValueError("FedGT proxy group matrix does not match scores or clients")
    normalized = matrix / np.maximum(matrix.sum(axis=1, keepdims=True), 1.0)
    ridge = 1e-3 * np.eye(len(deltas))
    client_utility = np.linalg.solve(normalized.T @ normalized + ridge, normalized.T @ scores)
    keep = max(1, len(deltas) - f)
    selected = np.argsort(-client_utility)[:keep].tolist()
    avg = secure_average_deltas([deltas[i] for i in selected], seed=seed + 1701)
    model_elements = sum(value.numel() for value in deltas[0].values())
    return avg, selected, {
        "crypto_time_ms": 0.0,
        "aggregation_time_ms": (time.perf_counter() - start) * 1000,
        "communication_bytes": int(model_elements * 4 * matrix.sum()),
    }
