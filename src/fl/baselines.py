from __future__ import annotations

import time

from src.crypto.secure_aggregation import secure_average_deltas
from src.fl.aggregation import Delta, coordinate_median, fedavg, krum, trimmed_mean
from src.methods.fedgt_exact import fedgt_nhat_aggregate
from src.methods.fedgt_proxy import fedgt_proxy_aggregate
from src.methods.plaintext_srsf import plaintext_srsf_aggregate
from src.methods.pp_srsf import pp_srsf_aggregate
from src.methods.pp_srsf_trust import pp_srsf_trust_aggregate


def aggregate(
    method: str,
    deltas: list[Delta],
    f: int,
    config: dict,
    seed: int,
    history_scores: list[float] | None = None,
    validation_scores: list[float] | None = None,
    group_matrix=None,
    group_validation_scores: list[float] | None = None,
):
    method = method.lower()
    start = time.perf_counter()
    metrics = {"crypto_time_ms": 0.0}
    if method == "fedavg":
        avg, selected = fedavg(deltas)
    elif method in {"secure_fedavg", "fedavg_secureagg"}:
        crypto_start = time.perf_counter()
        avg = secure_average_deltas(deltas, seed=seed)
        selected = list(range(len(deltas)))
        metrics["crypto_time_ms"] = (time.perf_counter() - crypto_start) * 1000
        metrics["communication_bytes"] = int(sum(v.numel() for v in deltas[0].values()) * len(deltas) * 4)
    elif method == "krum":
        avg, selected = krum(deltas, f=f)
    elif method == "trimmed_mean":
        avg, selected = trimmed_mean(deltas, trim_ratio=max(config.get("malicious_ratio", 0.0), 0.1))
    elif method in {"median", "coordinate_median"}:
        avg, selected = coordinate_median(deltas)
    elif method == "plain_srsf":
        return plaintext_srsf_aggregate(
            deltas,
            f=f,
            sketch_dim=int(config.get("sketch_dim", 64)),
            seed=seed,
        )
    elif method == "pp_srsf":
        return pp_srsf_aggregate(
            deltas,
            f=f,
            sketch_dim=int(config.get("sketch_dim", 64)),
            quantization_scale=int(config.get("quantization_scale", 1000)),
            modulus=int(config.get("modulus", 2**61 - 1)),
            seed=seed,
        )
    elif method in {"pp_srsf_trust", "trust_srsf"}:
        return pp_srsf_trust_aggregate(
            deltas,
            f=f,
            sketch_dim=int(config.get("sketch_dim", 64)),
            quantization_scale=int(config.get("quantization_scale", 1000)),
            modulus=int(config.get("modulus", 2**61 - 1)),
            seed=seed,
            history_scores=history_scores,
            validation_scores=validation_scores,
            distance_weight=float(config.get("trust_distance_weight", 1.0)),
            norm_weight=float(config.get("trust_norm_weight", 0.25)),
            history_weight=float(config.get("trust_history_weight", 0.35)),
            validation_weight=float(config.get("trust_validation_weight", 0.75)),
        )
    elif method == "fedgt_proxy":
        if group_matrix is None or group_validation_scores is None:
            raise ValueError("fedgt_proxy requires public-validation group scores")
        return fedgt_proxy_aggregate(
            deltas,
            f=f,
            group_matrix=group_matrix,
            group_validation_scores=group_validation_scores,
            seed=seed,
        )
    elif method in {"fedgt_nhat", "fedgt_exact"}:
        if group_matrix is None or group_validation_scores is None:
            raise ValueError("fedgt_nhat requires public-validation group scores")
        return fedgt_nhat_aggregate(
            deltas,
            group_matrix=group_matrix,
            group_validation_scores=group_validation_scores,
            max_malicious=int(config.get("fedgt_max_malicious", max(f, 1))),
            crossover_probability=float(config.get("fedgt_crossover_probability", 0.05)),
            silhouette_threshold=float(config.get("fedgt_silhouette_threshold", 0.0)),
            seed=seed,
        )
    else:
        raise ValueError(f"Unknown method: {method}")
    metrics["aggregation_time_ms"] = (time.perf_counter() - start) * 1000
    return avg, selected, metrics
