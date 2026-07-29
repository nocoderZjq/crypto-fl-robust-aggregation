from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def generate_figures(results_csv: str = "outputs/csv/results.csv", out_dir: str = "outputs/figures"):
    df = pd.read_csv(results_csv)
    out = Path(out_dir)
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    for method, g in df.groupby("method"):
        curve = g.groupby("round")["test_accuracy"].mean()
        ax.plot(curve.index, curve.values, marker="o", label=method)
    ax.set_xlabel("Round")
    ax.set_ylabel("Test accuracy")
    ax.legend()
    _save(fig, out / "accuracy_vs_round.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    for method, g in df.groupby("method"):
        curve = g.groupby("round")["test_loss"].mean()
        ax.plot(curve.index, curve.values, marker="o", label=method)
    ax.set_xlabel("Round")
    ax.set_ylabel("Test loss")
    ax.legend()
    _save(fig, out / "loss_vs_round.png")

    final = df.sort_values("round").groupby(["method", "attack_type", "malicious_ratio"]).tail(1)
    fig, ax = plt.subplots(figsize=(8, 4))
    final.groupby("method")["test_accuracy"].mean().sort_values().plot(kind="bar", ax=ax)
    ax.set_ylabel("Final accuracy")
    _save(fig, out / "final_accuracy_bar.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    final.groupby("method")[["true_positive_rate", "false_positive_rate"]].mean().plot(kind="bar", ax=ax)
    ax.set_ylabel("Rate")
    _save(fig, out / "detection_rate_bar.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    df.groupby("method")["crypto_time_ms"].mean().sort_values().plot(kind="bar", ax=ax)
    ax.set_ylabel("Crypto time per round (ms)")
    _save(fig, out / "crypto_overhead_bar.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    df.groupby("method")["communication_bytes"].mean().sort_values().plot(kind="bar", ax=ax)
    ax.set_ylabel("Communication bytes")
    _save(fig, out / "communication_cost_bar.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    summary = final.groupby("method").agg(
        accuracy=("test_accuracy", "mean"),
        detection=("true_positive_rate", "mean"),
        overhead=("crypto_time_ms", "mean"),
    )
    ax.scatter(summary["overhead"], summary["accuracy"], s=120 * (summary["detection"] + 0.1))
    for method, row in summary.iterrows():
        ax.annotate(method, (row["overhead"], row["accuracy"]))
    ax.set_xlabel("Crypto overhead (ms)")
    ax.set_ylabel("Final accuracy")
    _save(fig, out / "robustness_tradeoff.png")


def generate_tables(results_csv: str = "outputs/csv/results.csv", out_dir: str = "outputs/tables"):
    df = pd.read_csv(results_csv)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    final = df.sort_values("round").groupby(["method", "attack_type", "malicious_ratio"]).tail(1)
    final.groupby(["method", "attack_type", "malicious_ratio"])["test_accuracy"].mean().reset_index().to_csv(
        out / "table_final_accuracy.csv", index=False
    )
    final.groupby("method")[["true_positive_rate", "false_positive_rate"]].mean().reset_index().to_csv(
        out / "table_detection_metrics.csv", index=False
    )
    df.groupby("method")[["crypto_time_ms", "aggregation_time_ms", "communication_bytes"]].mean().reset_index().to_csv(
        out / "table_crypto_overhead.csv", index=False
    )
    final.groupby("method")[["test_accuracy", "macro_f1", "true_positive_rate", "crypto_time_ms"]].mean().reset_index().to_csv(
        out / "table_ablation.csv", index=False
    )
