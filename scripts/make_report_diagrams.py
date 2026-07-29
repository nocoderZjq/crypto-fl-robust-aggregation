from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


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
    return patch


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


def main():
    out = Path("outputs/figures")
    out.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    box(ax, (0.45, 4.55), "FL server\nbroadcast w_t", color="#f8fafc")
    box(ax, (0.45, 2.55), "Clients\nlocal training", color="#ecfdf5")
    box(ax, (2.9, 2.55), "Sketch + quantize\nq_i = round(SR Delta_i)", width=2.0, color="#fefce8")
    box(ax, (5.5, 3.65), "Aggregator A\nshare q_i^(A)", width=1.85, color="#eff6ff")
    box(ax, (5.5, 1.45), "Aggregator B\nshare q_i^(B)", width=1.85, color="#eff6ff")
    box(ax, (7.95, 2.55), "Secure distance\nand filtering", width=1.85, color="#fff7ed")
    box(ax, (7.95, 4.55), "Selected clients\nsecure aggregation", width=1.85, color="#f0f9ff")

    arrow(ax, (1.32, 4.55), (1.32, 3.17), "model")
    arrow(ax, (2.2, 2.86), (2.9, 2.86), "updates")
    arrow(ax, (4.9, 3.05), (5.5, 3.95), "share A")
    arrow(ax, (4.9, 2.65), (5.5, 1.75), "share B")
    arrow(ax, (7.35, 3.95), (7.95, 3.1), "MPC stats")
    arrow(ax, (7.35, 1.75), (7.95, 2.65), "MPC stats")
    arrow(ax, (8.88, 3.17), (8.88, 4.55), "filter set")
    arrow(ax, (2.2, 3.17), (7.95, 4.85), "masked updates", rad=-0.24)
    arrow(ax, (8.85, 5.17), (2.2, 5.17), "new global model", rad=0.12)

    ax.text(
        5.0,
        0.45,
        "Privacy boundary: a single aggregator sees only one random share; the server receives filtering output and aggregate update.",
        ha="center",
        fontsize=8,
        color="#475569",
    )
    fig.tight_layout()
    fig.savefig(out / "protocol_architecture.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
