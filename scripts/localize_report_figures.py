from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "outputs" / "csv"
FIG = ROOT / "outputs" / "figures"
TABLE = ROOT / "outputs" / "tables"


ATTACK_ZH = {
    "none": "无攻击",
    "no_attack": "无攻击",
    "label_flip": "标签翻转",
    "label_flip_pairwise": "成对标签翻转",
    "label_flip_all_to_one": "单目标标签翻转",
    "sign_flip": "符号翻转",
    "gaussian_noise": "高斯噪声",
}

METHOD_LABEL = {
    "fedavg": "FedAvg",
    "plain_srsf": "Plain-SRSF",
    "pp_srsf": "PP-SRSF",
    "pp_srsf_trust": "PP-SRSF+Trust",
    "fedgt_proxy": "FedGT-Ridge",
    "fedgt_nhat": "FedGT-n-hat",
}


def setup_font():
    preferred = ["Microsoft YaHei", "SimHei", "KaiTi", "Microsoft JhengHei", "Noto Sans CJK SC"]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in preferred:
        if font in available:
            plt.rcParams["font.sans-serif"] = [font]
            break
    plt.rcParams["axes.unicode_minus"] = False


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=180)
    plt.close(fig)


def final_rows(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    group_columns = ["method", "attack_type", "malicious_ratio", "seed"]
    if "sketch_dim" in df.columns and df["sketch_dim"].nunique() > 1:
        group_columns.append("sketch_dim")
    return df.sort_values("round").groupby(group_columns).tail(1)


def draw_protocol():
    def box(ax, xy, text, width=1.75, height=0.62, color="#eef4ff"):
        patch = FancyBboxPatch(
            xy,
            width,
            height,
            boxstyle="round,pad=0.04,rounding_size=0.05",
            linewidth=1.2,
            edgecolor="#334155",
            facecolor=color,
        )
        ax.add_patch(patch)
        ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=9)

    def arrow(ax, start, end, label=None, rad=0.0):
        arr = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.1,
            color="#334155",
            connectionstyle=f"arc3,rad={rad}",
        )
        ax.add_patch(arr)
        if label:
            ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.1, label, ha="center", fontsize=8)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    box(ax, (0.45, 4.55), "联邦服务器\n广播 w_t", color="#f8fafc")
    box(ax, (0.45, 2.55), "客户端\n本地训练", color="#ecfdf5")
    box(ax, (2.9, 2.55), "草图与量化\nq_i=round(SRΔ_i)", width=2.0, color="#fefce8")
    box(ax, (5.5, 3.65), "聚合方 A\n份额 q_i^(A)", width=1.85, color="#eff6ff")
    box(ax, (5.5, 1.45), "聚合方 B\n份额 q_i^(B)", width=1.85, color="#eff6ff")
    box(ax, (7.95, 2.55), "安全距离\n与过滤", width=1.85, color="#fff7ed")
    box(ax, (7.95, 4.55), "选中客户端\n安全聚合", width=1.85, color="#f0f9ff")
    arrow(ax, (1.32, 4.55), (1.32, 3.17), "模型")
    arrow(ax, (2.2, 2.86), (2.9, 2.86), "更新")
    arrow(ax, (4.9, 3.05), (5.5, 3.95), "份额 A")
    arrow(ax, (4.9, 2.65), (5.5, 1.75), "份额 B")
    arrow(ax, (7.35, 3.95), (7.95, 3.1), "MPC 统计")
    arrow(ax, (7.35, 1.75), (7.95, 2.65), "MPC 统计")
    arrow(ax, (8.88, 3.17), (8.88, 4.55), "过滤集合")
    arrow(ax, (2.2, 3.17), (7.95, 4.85), "掩码更新", rad=-0.24)
    arrow(ax, (8.85, 5.17), (2.2, 5.17), "新全局模型", rad=0.12)
    ax.text(5.0, 0.45, "隐私边界：单个聚合方只看到一份随机份额，服务器只获得过滤结果与聚合更新。", ha="center", fontsize=8, color="#475569")
    save(fig, "protocol_architecture.png")


def draw_protocol_sequence():
    participants = ["联邦服务器", "客户端", "聚合方 A", "聚合方 B"]
    x_positions = np.arange(len(participants))
    events = [
        (0, 1, "广播全局模型"),
        (1, 2, "发送草图份额 A"),
        (1, 3, "发送草图份额 B"),
        (2, 3, "Beaver 掩码差值交互"),
        (3, 2, "距离结果份额"),
        (2, 0, "过滤统计"),
        (1, 0, "选中更新的成对掩码"),
        (0, 1, "广播新全局模型"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.set_xlim(-0.35, len(participants) - 0.65)
    ax.set_ylim(len(events) + 1.0, -0.8)
    ax.axis("off")
    for x, name in zip(x_positions, participants):
        ax.text(x, -0.25, name, ha="center", va="center", fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8fafc", edgecolor="#475569"))
        ax.plot([x, x], [0.2, len(events) + 0.4], linestyle="--", linewidth=1, color="#94a3b8")
    for idx, (source, target, label) in enumerate(events, start=1):
        y = idx
        ax.annotate("", xy=(target, y), xytext=(source, y), arrowprops=dict(arrowstyle="->", linewidth=1.2, color="#1f2937"))
        ax.text((source + target) / 2, y - 0.17, label, ha="center", va="bottom", fontsize=8, backgroundcolor="white")
    ax.text(1.5, len(events) + 0.72, "公开量仅包括 Beaver 掩码差值、距离统计、过滤集合与聚合结果。", ha="center", fontsize=8, color="#475569")
    save(fig, "protocol_sequence.png")


def draw_main_attack_figures():
    long = final_rows(CSV / "mnist_tinycnn_long.csv")
    long = long[long["method"].isin(["fedavg", "plain_srsf", "pp_srsf"])]
    pivot = long.pivot_table(index="attack_type", columns="method", values="test_accuracy").reindex(
        ["none", "label_flip", "sign_flip", "gaussian_noise"]
    )
    pivot.index = [ATTACK_ZH.get(x, x) for x in pivot.index]
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("MNIST+TinyCNN 不同攻击场景最终准确率")
    ax.set_xlabel("攻击场景")
    ax.set_ylabel("最终测试准确率")
    ax.legend(title="方法", fontsize=8)
    save(fig, "attack_accuracy_grouped.png")

    det = long[long["malicious_ratio"] == 0.2].pivot_table(index="attack_type", columns="method", values="true_positive_rate")
    det = det.reindex(["label_flip", "sign_flip", "gaussian_noise"])
    det.index = [ATTACK_ZH.get(x, x) for x in det.index]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    im = ax.imshow(det.values, vmin=0, vmax=1, cmap="YlGnBu")
    ax.set_title("恶意客户端检测率 TPR")
    ax.set_xticks(range(len(det.columns)), det.columns)
    ax.set_yticks(range(len(det.index)), det.index)
    for i in range(det.shape[0]):
        for j in range(det.shape[1]):
            ax.text(j, i, f"{det.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    save(fig, "detection_heatmap.png")

    strength = final_rows(CSV / "mnist_tinycnn_strength.csv")
    ratio = strength[strength["method"].eq("pp_srsf")].pivot_table(
        index="malicious_ratio", columns="attack_type", values="test_accuracy", aggfunc="mean"
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for attack in ["label_flip", "sign_flip", "gaussian_noise"]:
        if attack in ratio.columns:
            ax.plot(ratio.index, ratio[attack], marker="o", label=ATTACK_ZH.get(attack, attack))
    ax.set_title("PP-SRSF 多恶意比例鲁棒性")
    ax.set_xlabel("恶意客户端比例")
    ax.set_ylabel("最终测试准确率")
    ax.legend(title="攻击类型", fontsize=8)
    save(fig, "pp_srsf_accuracy_vs_malicious_ratio.png")


def draw_advanced_figures():
    label = final_rows(CSV / "advanced_label_flip.csv")
    pivot = label.pivot_table(index="attack_type", columns="method", values="test_accuracy")
    pivot.index = [ATTACK_ZH.get(x, x) for x in pivot.index]
    pivot = pivot.rename(columns=METHOD_LABEL)
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    pivot.plot(kind="bar", ax=ax)
    ax.set_ylabel("最终准确率")
    ax.set_xlabel("标签翻转变体")
    ax.legend(title="方法", fontsize=8)
    save(fig, "advanced_label_flip_accuracy.png")

    sketch = pd.read_csv(TABLE / "advanced_sketch_ablation_summary.csv")
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    for method, group in sketch.groupby("method"):
        ax.errorbar(group["sketch_dim"], group["accuracy_mean"], yerr=group["accuracy_std"], marker="o", capsize=4, label=method)
    ax.set_xlabel("草图维度")
    ax.set_ylabel("最终准确率")
    ax.legend(title="方法", fontsize=8)
    save(fig, "advanced_sketch_dim_ablation.png")

    seeds = pd.read_csv(TABLE / "advanced_seed_stats_summary.csv")
    seeds["method"] = seeds["method"].map(lambda value: METHOD_LABEL.get(value, value))
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.bar(seeds["method"], seeds["accuracy_mean"], yerr=seeds["accuracy_std"], capsize=5)
    ax.set_xlabel("方法")
    ax.set_ylabel("最终准确率（均值±标准差）")
    ax.tick_params(axis="x", labelrotation=18)
    save(fig, "advanced_seed_accuracy_mean_std.png")

    majority = final_rows(CSV / "advanced_majority.csv")
    majority["scenario"] = majority["attack_type"].map(lambda x: ATTACK_ZH.get(x, x)) + " / " + majority["malicious_ratio"].astype(str)
    majority["method"] = majority["method"].map(lambda value: METHOD_LABEL.get(value, value))
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 6.7), sharex=True)
    majority.pivot_table(index="scenario", columns="method", values="test_accuracy").plot(kind="bar", ax=axes[0])
    majority.pivot_table(index="scenario", columns="method", values="true_positive_rate").plot(kind="bar", ax=axes[1])
    axes[0].set_ylabel("最终准确率")
    axes[1].set_ylabel("检测率 TPR")
    axes[1].set_xlabel("多数恶意场景")
    axes[0].set_xlabel("")
    axes[0].legend(title="方法", fontsize=7, ncol=2)
    axes[1].legend(title="方法", fontsize=7, ncol=2)
    save(fig, "advanced_majority_detection.png")


def draw_cost_figures():
    df = pd.read_csv(CSV / "mnist_pilot.csv")
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    df.groupby("method")["crypto_time_ms"].mean().reindex(["fedavg", "plain_srsf", "pp_srsf"]).plot(kind="bar", ax=ax)
    ax.set_xlabel("方法")
    ax.set_ylabel("每轮密码计算时间（ms）")
    save(fig, "crypto_overhead_bar.png")

    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    df.groupby("method")["communication_bytes"].mean().reindex(["fedavg", "plain_srsf", "pp_srsf"]).plot(kind="bar", ax=ax)
    ax.set_xlabel("方法")
    ax.set_ylabel("通信开销（字节）")
    save(fig, "communication_cost_bar.png")


def main():
    setup_font()
    draw_protocol()
    draw_protocol_sequence()
    draw_main_attack_figures()
    draw_advanced_figures()
    draw_cost_figures()
    print("Localized report figures written to outputs/figures")


if __name__ == "__main__":
    main()
