from __future__ import annotations

from itertools import combinations, product
import math
import time

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import torch

from src.crypto.secure_aggregation import secure_average_deltas
from src.fl.aggregation import Delta


def _standardize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    scale = values.std(axis=0, keepdims=True)
    scale[scale < 1e-12] = 1.0
    return (values - values.mean(axis=0, keepdims=True)) / scale


def _last_matrix_key(delta: Delta) -> str:
    matrix_keys = [key for key, value in delta.items() if value.ndim >= 2]
    return matrix_keys[-1] if matrix_keys else next(reversed(delta))


def _group_principal_component(deltas: list[Delta], matrix: np.ndarray) -> np.ndarray:
    key = _last_matrix_key(deltas[0])
    group_vectors = []
    for row in matrix:
        members = np.flatnonzero(row)
        group_vectors.append(
            torch.stack([deltas[idx][key].reshape(-1).float() for idx in members])
            .mean(dim=0)
            .numpy()
        )
    centered = np.stack(group_vectors)
    centered -= centered.mean(axis=0, keepdims=True)
    if np.allclose(centered, 0.0):
        return np.zeros(len(matrix), dtype=np.float64)
    left, singular, _ = np.linalg.svd(centered, full_matrices=False)
    return left[:, 0] * singular[0]


def _dunn_index(points: np.ndarray, labels: np.ndarray) -> float:
    clusters = [points[labels == label] for label in np.unique(labels)]
    if len(clusters) < 2:
        return 0.0
    centers = np.stack([cluster.mean(axis=0) for cluster in clusters])
    center_distances = np.linalg.norm(centers[:, None, :] - centers[None, :, :], axis=2)
    np.fill_diagonal(center_distances, np.inf)
    min_separation = float(center_distances.min())
    max_diameter = 0.0
    for cluster in clusters:
        if len(cluster) > 1:
            distances = np.linalg.norm(cluster[:, None, :] - cluster[None, :, :], axis=2)
            max_diameter = max(max_diameter, float(distances.max()))
    return min_separation / max(max_diameter, 1e-12)


def make_binary_group_tests(
    deltas: list[Delta],
    group_matrix: np.ndarray,
    group_utilities: list[float],
    silhouette_threshold: float = 0.0,
    seed: int = 0,
) -> np.ndarray:
    """Adapt FedGT's utility/PCA clustering test to a generic model."""
    matrix = np.asarray(group_matrix, dtype=np.float64)
    utilities = np.asarray(group_utilities, dtype=np.float64)
    if matrix.shape != (len(utilities), len(deltas)):
        raise ValueError("FedGT assignment matrix does not match utilities or clients")
    principal = _group_principal_component(deltas, matrix)
    points = _standardize(np.column_stack([utilities, principal]))
    if len(points) < 3 or np.allclose(points, points[0]):
        return np.zeros(len(points), dtype=np.int8)

    max_clusters = min(int(matrix.sum(axis=1).max()) + 1, len(points) - 1)
    candidates: list[tuple[float, float, np.ndarray]] = []
    for n_clusters in range(2, max_clusters + 1):
        labels = KMeans(n_clusters=n_clusters, n_init=20, random_state=seed).fit_predict(points)
        if len(np.unique(labels)) < 2:
            continue
        silhouette = float(silhouette_score(points, labels))
        candidates.append((silhouette, _dunn_index(points, labels), labels))
    if not candidates:
        return np.zeros(len(points), dtype=np.int8)
    max_silhouette = max(item[0] for item in candidates)
    if max_silhouette < silhouette_threshold:
        return np.zeros(len(points), dtype=np.int8)
    _, _, labels = max(candidates, key=lambda item: item[1])
    cluster_utilities = {
        label: float(utilities[labels == label].mean()) for label in np.unique(labels)
    }
    benign_cluster = max(cluster_utilities, key=cluster_utilities.get)
    return (labels != benign_cluster).astype(np.int8)


def _syndrome(matrix: np.ndarray, defective: np.ndarray) -> np.ndarray:
    return (matrix @ defective > 0).astype(np.int8)


def estimate_malicious_count(
    group_matrix: np.ndarray,
    test_results: np.ndarray,
    max_malicious: int,
) -> int:
    """Implement FedGT's zero-syndrome maximum-likelihood count estimate."""
    matrix = np.asarray(group_matrix, dtype=np.int8)
    observed_zeros = int((np.asarray(test_results) == 0).sum())
    n_clients = matrix.shape[1]
    scores = []
    for count in range(max(0, min(max_malicious, n_clients - 1)) + 1):
        matches = 0
        total = 0
        for chosen in combinations(range(n_clients), count):
            defective = np.zeros(n_clients, dtype=np.int8)
            defective[list(chosen)] = 1
            matches += int((_syndrome(matrix, defective) == 0).sum() == observed_zeros)
            total += 1
        scores.append(matches / max(total, 1))
    return int(max(range(len(scores)), key=lambda idx: (scores[idx], -idx)))


def posterior_malicious_probabilities(
    group_matrix: np.ndarray,
    test_results: np.ndarray,
    prevalence: float,
    crossover_probability: float = 0.05,
) -> np.ndarray:
    """Compute exact client posterior probabilities for small cross-silo systems."""
    matrix = np.asarray(group_matrix, dtype=np.int8)
    tests = np.asarray(test_results, dtype=np.int8)
    n_clients = matrix.shape[1]
    prevalence = float(np.clip(prevalence, 1e-6, 1.0 - 1e-6))
    crossover_probability = float(np.clip(crossover_probability, 1e-6, 1.0 - 1e-6))
    patterns = np.asarray(list(product([0, 1], repeat=n_clients)), dtype=np.int8)
    log_weights = np.empty(len(patterns), dtype=np.float64)
    for idx, defective in enumerate(patterns):
        syndrome = _syndrome(matrix, defective)
        errors = int((syndrome != tests).sum())
        malicious = int(defective.sum())
        log_prior = malicious * math.log(prevalence) + (n_clients - malicious) * math.log(
            1.0 - prevalence
        )
        log_likelihood = errors * math.log(crossover_probability) + (
            len(tests) - errors
        ) * math.log(1.0 - crossover_probability)
        log_weights[idx] = log_prior + log_likelihood
    weights = np.exp(log_weights - log_weights.max())
    weights /= weights.sum()
    return weights @ patterns


def fedgt_nhat_aggregate(
    deltas: list[Delta],
    group_matrix: np.ndarray,
    group_validation_scores: list[float],
    max_malicious: int,
    crossover_probability: float = 0.05,
    silhouette_threshold: float = 0.0,
    seed: int = 0,
) -> tuple[Delta, list[int], dict[str, float]]:
    """Paper-aligned FedGT-n_hat adaptation with exact small-system LLRs."""
    start = time.perf_counter()
    matrix = np.asarray(group_matrix, dtype=np.float64)
    tests = make_binary_group_tests(
        deltas,
        matrix,
        group_validation_scores,
        silhouette_threshold=silhouette_threshold,
        seed=seed,
    )
    estimated = estimate_malicious_count(matrix, tests, max_malicious=max_malicious)
    if estimated == 0:
        selected = list(range(len(deltas)))
    else:
        posterior = posterior_malicious_probabilities(
            matrix,
            tests,
            prevalence=estimated / len(deltas),
            crossover_probability=crossover_probability,
        )
        malicious = set(np.argsort(-posterior)[:estimated].tolist())
        selected = [idx for idx in range(len(deltas)) if idx not in malicious]
    avg = secure_average_deltas([deltas[idx] for idx in selected], seed=seed + 1701)
    model_elements = sum(value.numel() for value in deltas[0].values())
    communication = int(model_elements * 4 * (matrix.sum() + len(selected)))
    return avg, selected, {
        "crypto_time_ms": 0.0,
        "aggregation_time_ms": (time.perf_counter() - start) * 1000,
        "communication_bytes": communication,
        "protocol_online_bytes": communication,
        "fedgt_estimated_malicious": estimated,
        "fedgt_positive_tests": int(tests.sum()),
    }
