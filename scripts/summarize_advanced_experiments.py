from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "outputs" / "csv"
FIG = ROOT / "outputs" / "figures"
TABLE = ROOT / "outputs" / "tables"


def final_rows(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    group_columns = ["method", "attack_type", "malicious_ratio", "seed"]
    if "sketch_dim" in df.columns and df["sketch_dim"].nunique() > 1:
        group_columns.append("sketch_dim")
    return df.sort_values("round").groupby(group_columns).tail(1)


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=170)
    plt.close(fig)


def main():
    TABLE.mkdir(parents=True, exist_ok=True)

    label = final_rows(CSV / "advanced_label_flip.csv")
    label_summary = label.pivot_table(
        index="attack_type",
        columns="method",
        values=["test_accuracy", "true_positive_rate", "false_positive_rate"],
        aggfunc="mean",
    )
    label_summary.to_csv(TABLE / "advanced_label_flip_summary.csv")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    label.pivot_table(index="attack_type", columns="method", values="test_accuracy").plot(kind="bar", ax=ax)
    ax.set_ylabel("Final accuracy")
    ax.set_xlabel("Label-flip variant")
    ax.legend(title="Method", fontsize=8)
    save(fig, "advanced_label_flip_accuracy.png")

    sketch = final_rows(CSV / "advanced_sketch_ablation.csv")
    sketch_summary = sketch.groupby(["method", "sketch_dim"], as_index=False).agg(
        accuracy_mean=("test_accuracy", "mean"),
        accuracy_std=("test_accuracy", "std"),
        tpr_mean=("true_positive_rate", "mean"),
        online_bytes=("protocol_online_bytes", "mean"),
    )
    sketch_summary.to_csv(TABLE / "advanced_sketch_ablation_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    for method, group in sketch_summary.groupby("method"):
        ax.errorbar(
            group["sketch_dim"],
            group["accuracy_mean"],
            yerr=group["accuracy_std"],
            marker="o",
            capsize=4,
            label=method,
        )
    ax.set_xlabel("Sketch dimension")
    ax.set_ylabel("Final accuracy")
    ax.legend(title="Method")
    save(fig, "advanced_sketch_dim_ablation.png")

    seeds = final_rows(CSV / "advanced_seed_stats.csv")
    aligned_path = CSV / "fedgt_aligned_mnist.csv"
    if aligned_path.exists():
        seeds = pd.concat([seeds, final_rows(aligned_path)], ignore_index=True)
    seed_summary = seeds.groupby("method").agg(
        accuracy_mean=("test_accuracy", "mean"),
        accuracy_std=("test_accuracy", "std"),
        f1_mean=("macro_f1", "mean"),
        tpr_mean=("true_positive_rate", "mean"),
        fpr_mean=("false_positive_rate", "mean"),
    )
    seed_summary.to_csv(TABLE / "advanced_seed_stats_summary.csv")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.bar(seed_summary.index, seed_summary["accuracy_mean"], yerr=seed_summary["accuracy_std"], capsize=5)
    ax.set_ylabel("Final accuracy (mean +/- std)")
    ax.set_xlabel("Method")
    save(fig, "advanced_seed_accuracy_mean_std.png")

    fashion_path = CSV / "fashion_multiseed.csv"
    if fashion_path.exists():
        fashion = final_rows(fashion_path)
        fashion_summary = fashion.groupby("method").agg(
            accuracy_mean=("test_accuracy", "mean"),
            accuracy_std=("test_accuracy", "std"),
            f1_mean=("macro_f1", "mean"),
            f1_std=("macro_f1", "std"),
            tpr_mean=("true_positive_rate", "mean"),
            fpr_mean=("false_positive_rate", "mean"),
        )
        fashion_summary.to_csv(TABLE / "fashion_multiseed_summary.csv")

    majority = final_rows(CSV / "advanced_majority.csv")
    majority_summary = majority.pivot_table(
        index=["attack_type", "malicious_ratio"],
        columns="method",
        values=["test_accuracy", "true_positive_rate", "false_positive_rate"],
        aggfunc="mean",
    )
    majority_summary.to_csv(TABLE / "advanced_majority_summary.csv")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    majority_plot = majority.copy()
    majority_plot["scenario"] = majority_plot["attack_type"] + " / " + majority_plot["malicious_ratio"].astype(str)
    majority_plot.pivot_table(index="scenario", columns="method", values="true_positive_rate").plot(kind="bar", ax=ax)
    ax.set_ylabel("Detection TPR")
    ax.set_xlabel("Majority-malicious scenario")
    ax.legend(title="Method", fontsize=8)
    save(fig, "advanced_majority_detection.png")

    print("Advanced summaries written to outputs/tables and outputs/figures")


if __name__ == "__main__":
    main()
