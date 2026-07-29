from __future__ import annotations

from copy import deepcopy
import random
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from src.crypto.secure_aggregation import secure_average_deltas
from src.data.datasets import extract_labels, load_dataset, split_public_validation
from src.data.partition import make_partitions
from src.fl.aggregation import add_delta_to_model
from src.fl.attacks import apply_update_attack
from src.fl.baselines import aggregate
from src.fl.client import Client
from src.methods.fedgt_proxy import make_group_matrix
from src.models import build_model
from src.utils.logging_utils import append_result
from src.utils.metrics import evaluate
from src.utils.seed import set_seed


def _detection_metrics(selected_local: list[int], round_client_ids: list[int], malicious_ids: set[int]):
    selected_ids = {round_client_ids[i] for i in selected_local}
    round_ids = set(round_client_ids)
    mal_round = round_ids & malicious_ids
    normal_round = round_ids - malicious_ids
    detected = len(mal_round - selected_ids)
    false_positive = len(normal_round - selected_ids)
    return {
        "detected_malicious": detected,
        "false_positive": false_positive,
        "true_positive_rate": detected / max(len(mal_round), 1),
        "false_positive_rate": false_positive / max(len(normal_round), 1),
    }


def estimate_model_bytes(model: torch.nn.Module, clients_per_round: int) -> int:
    return int(sum(p.numel() for p in model.parameters()) * clients_per_round * 4)


def _mean_loss(model: torch.nn.Module, loader: DataLoader, device: str, max_batches: int = 1) -> float:
    criterion = torch.nn.CrossEntropyLoss()
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        for batch_idx, (x, y) in enumerate(loader):
            if batch_idx >= max_batches:
                break
            x = x.to(device)
            y = y.to(device)
            total += float(criterion(model(x), y).item())
            count += 1
    return total / max(count, 1)


def _validation_improvements(
    model: torch.nn.Module,
    deltas: list,
    loader: DataLoader,
    device: str,
    max_batches: int = 1,
) -> list[float]:
    base_loss = _mean_loss(model, loader, device=device, max_batches=max_batches)
    scores: list[float] = []
    for delta in deltas:
        candidate = deepcopy(model).to(device)
        add_delta_to_model(candidate, delta)
        after_loss = _mean_loss(candidate, loader, device=device, max_batches=max_batches)
        scores.append(base_loss - after_loss)
    return scores


def _group_validation_improvements(
    model: torch.nn.Module,
    deltas: list,
    group_matrix,
    loader: DataLoader,
    device: str,
    max_batches: int,
    seed: int,
) -> list[float]:
    base_loss = _mean_loss(model, loader, device=device, max_batches=max_batches)
    scores: list[float] = []
    for row in group_matrix:
        members = [idx for idx, included in enumerate(row) if included]
        candidate = deepcopy(model).to(device)
        group_delta = secure_average_deltas(
            [deltas[idx] for idx in members],
            seed=seed + len(scores),
        )
        add_delta_to_model(candidate, group_delta)
        after_loss = _mean_loss(candidate, loader, device=device, max_batches=max_batches)
        scores.append(base_loss - after_loss)
    return scores


def run_experiment(config: dict, method: str, output_path: str = "outputs/csv/results.csv") -> list[dict]:
    seed = int(config.get("seed", 0))
    set_seed(seed)
    device = str(config.get("device", "cpu"))
    bundle = load_dataset(
        config["dataset"],
        max_train_samples=config.get("max_train_samples"),
        max_test_samples=config.get("max_test_samples"),
        seed=seed,
    )
    public_validation_samples = int(config.get("public_validation_samples", 0))
    federated_train, public_validation = split_public_validation(
        bundle.train,
        validation_samples=public_validation_samples,
        seed=seed + 701,
    )
    requires_validation = method.lower() in {
        "pp_srsf_trust",
        "trust_srsf",
        "fedgt_proxy",
        "fedgt_nhat",
        "fedgt_exact",
    }
    if requires_validation and public_validation is None:
        raise ValueError(f"{method} requires public_validation_samples > 0")

    labels = extract_labels(federated_train)
    partitions = make_partitions(
        labels,
        num_clients=int(config["num_clients"]),
        non_iid=bool(config.get("non_iid", False)),
        alpha=float(config.get("dirichlet_alpha", 0.5)),
        seed=seed,
    )
    clients = [
        Client(i, federated_train, partitions[i], batch_size=int(config.get("batch_size", 64)))
        for i in range(int(config["num_clients"]))
    ]
    test_loader = DataLoader(bundle.test, batch_size=256, shuffle=False)
    validation_loader = (
        DataLoader(public_validation, batch_size=256, shuffle=False)
        if public_validation is not None
        else None
    )
    model = build_model(config["model"], input_channels=bundle.input_channels, num_classes=bundle.num_classes).to(device)

    num_clients = int(config["num_clients"])
    clients_per_round = int(config.get("clients_per_round", num_clients))
    malicious_count = int(float(config.get("malicious_ratio", 0.0)) * num_clients)
    malicious_ids = set(range(malicious_count))
    rng = random.Random(seed)
    trust_state = [0.0 for _ in range(num_clients)]
    rows: list[dict] = []
    output = Path(output_path)
    if output.exists() and config.get("overwrite_results", False):
        output.unlink()

    for round_idx in range(1, int(config.get("num_rounds", 1)) + 1):
        round_start = time.perf_counter()
        if clients_per_round >= num_clients:
            round_client_ids = list(range(num_clients))
        else:
            round_client_ids = sorted(rng.sample(range(num_clients), clients_per_round))
        deltas = []
        attack_type = str(config.get("attack_type", "none")).lower()
        for cid in round_client_ids:
            is_malicious = cid in malicious_ids
            label_flip = is_malicious and attack_type in {"label_flip", "label_flip_pairwise", "label_flip_all_to_one"}
            delta = clients[cid].train(
                model,
                device=device,
                epochs=int(config.get("local_epochs", 1)),
                learning_rate=float(config.get("learning_rate", 0.01)),
                label_flip=label_flip,
                label_flip_mode=attack_type,
                num_classes=bundle.num_classes,
            )
            if is_malicious:
                delta = apply_update_attack(
                    delta,
                    str(config.get("attack_type", "none")),
                    scale=float(config.get("attack_scale", 5.0)),
                    sigma=float(config.get("noise_sigma", 1.0)),
                    seed=seed + round_idx + cid,
                )
            deltas.append(delta)

        f = int(float(config.get("malicious_ratio", 0.0)) * len(round_client_ids))
        local_history = [trust_state[cid] for cid in round_client_ids]
        local_validation = None
        if method.lower() in {"pp_srsf_trust", "trust_srsf"}:
            local_validation = _validation_improvements(
                model,
                deltas,
                validation_loader,
                device=device,
                max_batches=int(config.get("trust_validation_batches", 1)),
            )
        group_matrix = None
        group_validation_scores = None
        if method.lower() in {"fedgt_proxy", "fedgt_nhat", "fedgt_exact"}:
            group_matrix = make_group_matrix(
                len(deltas),
                n_tests=int(config.get("fedgt_num_tests", 6)),
                group_size=int(config.get("fedgt_group_size", max(2, len(deltas) // 2))),
                seed=seed + round_idx + 811,
            )
            group_validation_scores = _group_validation_improvements(
                model,
                deltas,
                group_matrix,
                validation_loader,
                device=device,
                max_batches=int(config.get("trust_validation_batches", 1)),
                seed=seed + round_idx + 1201,
            )
        avg_delta, selected_local, agg_metrics = aggregate(
            method,
            deltas,
            f=f,
            config=config,
            seed=seed + round_idx,
            history_scores=local_history,
            validation_scores=local_validation,
            group_matrix=group_matrix,
            group_validation_scores=group_validation_scores,
        )
        if local_validation is not None:
            decay = float(config.get("trust_decay", 0.8))
            selected_set = set(selected_local)
            for local_idx, cid in enumerate(round_client_ids):
                selection_bonus = 0.05 if local_idx in selected_set else -0.05
                trust_state[cid] = decay * trust_state[cid] + (1.0 - decay) * (local_validation[local_idx] + selection_bonus)
        add_delta_to_model(model, avg_delta)
        eval_metrics = evaluate(model, test_loader, device=device)
        det_metrics = _detection_metrics(selected_local, round_client_ids, malicious_ids)
        total_time = (time.perf_counter() - round_start) * 1000
        row = {
            "dataset": config["dataset"],
            "model": config["model"],
            "method": method,
            "attack_type": config.get("attack_type", "none"),
            "malicious_ratio": config.get("malicious_ratio", 0.0),
            "non_iid_alpha": config.get("dirichlet_alpha", ""),
            "round": round_idx,
            **eval_metrics,
            **det_metrics,
            "crypto_time_ms": agg_metrics.get("crypto_time_ms", 0.0),
            "aggregation_time_ms": agg_metrics.get("aggregation_time_ms", 0.0),
            "communication_bytes": agg_metrics.get("communication_bytes", estimate_model_bytes(model, len(round_client_ids))),
            "total_round_time_ms": total_time,
            "seed": seed,
            "sketch_dim": config.get("sketch_dim", ""),
            "public_validation_samples": public_validation_samples,
            "protocol_online_bytes": agg_metrics.get("protocol_online_bytes", 0),
            "protocol_offline_bytes": agg_metrics.get("protocol_offline_bytes", 0),
            "secure_multiplications": agg_metrics.get("secure_multiplications", 0),
            "fedgt_estimated_malicious": agg_metrics.get("fedgt_estimated_malicious", ""),
            "fedgt_positive_tests": agg_metrics.get("fedgt_positive_tests", ""),
        }
        append_result(row, output_path=output_path)
        rows.append(row)
        print(
            f"round={round_idx} method={method} acc={row['test_accuracy']:.4f} "
            f"f1={row['macro_f1']:.4f} tpr={row['true_positive_rate']:.3f} fpr={row['false_positive_rate']:.3f}"
        )
    return rows
