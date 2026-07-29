from __future__ import annotations

from pathlib import Path

import pandas as pd


RESULT_COLUMNS = [
    "dataset",
    "model",
    "method",
    "attack_type",
    "malicious_ratio",
    "non_iid_alpha",
    "round",
    "test_accuracy",
    "test_loss",
    "macro_f1",
    "detected_malicious",
    "false_positive",
    "true_positive_rate",
    "false_positive_rate",
    "crypto_time_ms",
    "aggregation_time_ms",
    "communication_bytes",
    "total_round_time_ms",
    "seed",
    "sketch_dim",
    "public_validation_samples",
    "protocol_online_bytes",
    "protocol_offline_bytes",
    "secure_multiplications",
    "fedgt_estimated_malicious",
    "fedgt_positive_tests",
]


def append_result(row: dict, output_path: str = "outputs/csv/results.csv") -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([{col: row.get(col, "") for col in RESULT_COLUMNS}])
    df.to_csv(path, mode="a", header=not path.exists(), index=False)
