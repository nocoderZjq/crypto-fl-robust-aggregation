from __future__ import annotations

import time
from pathlib import Path
import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.crypto.secret_sharing import share
from src.crypto.secure_distance import secure_pairwise_distance_matrix


OUT_CSV = ROOT / "outputs" / "csv" / "secure_distance_benchmark.csv"
OUT_TABLE = ROOT / "outputs" / "tables" / "secure_distance_benchmark_summary.csv"
OUT_FIG = ROOT / "outputs" / "figures" / "secure_distance_scaling.png"


def setup_font():
    available = {font.name for font in fm.fontManager.ttflist}
    for name in ["Microsoft YaHei", "SimHei", "KaiTi", "Noto Sans CJK SC"]:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name]
            break
    plt.rcParams["axes.unicode_minus"] = False


def main():
    rows = []
    modulus = 2**61 - 1
    for n_clients in [5, 10, 20]:
        for sketch_dim in [16, 32, 64, 128]:
            for repeat in range(10):
                rng = np.random.default_rng(3000 + n_clients * 100 + sketch_dim + repeat)
                sketches = rng.integers(-1000, 1001, size=(n_clients, sketch_dim), dtype=np.int64)
                shares = [share(row.astype(object), modulus, seed=4000 + repeat * 100 + idx) for idx, row in enumerate(sketches)]

                start = time.perf_counter()
                _, metrics = secure_pairwise_distance_matrix(
                    shares,
                    modulus=modulus,
                    seed=5000 + repeat,
                    return_metrics=True,
                )
                elapsed_ms = (time.perf_counter() - start) * 1000
                rows.append(
                    {
                        "n_clients": n_clients,
                        "sketch_dim": sketch_dim,
                        "repeat": repeat,
                        "protocol_time_ms": elapsed_ms,
                        **metrics,
                    }
                )

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    summary = df.groupby(["n_clients", "sketch_dim"], as_index=False).agg(
        time_mean_ms=("protocol_time_ms", "mean"),
        time_std_ms=("protocol_time_ms", "std"),
        online_kib=("protocol_online_bytes", lambda values: values.mean() / 1024),
        offline_kib=("protocol_offline_bytes", lambda values: values.mean() / 1024),
        secure_multiplications=("secure_multiplications", "mean"),
    )
    summary.to_csv(OUT_TABLE, index=False)

    setup_font()
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))
    for n_clients, group in summary.groupby("n_clients"):
        axes[0].errorbar(group["sketch_dim"], group["time_mean_ms"], yerr=group["time_std_ms"], marker="o", capsize=3, label=f"n={n_clients}")
        axes[1].plot(group["sketch_dim"], group["online_kib"], marker="o", label=f"n={n_clients}")
    axes[0].set_xlabel("草图维度 m")
    axes[0].set_ylabel("距离协议时间（毫秒）")
    axes[1].set_xlabel("草图维度 m")
    axes[1].set_ylabel("在线通信量（KiB）")
    axes[0].legend(title="客户端数")
    axes[1].legend(title="客户端数")
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=180)
    plt.close(fig)
    print(f"Wrote {OUT_TABLE} and {OUT_FIG}")


if __name__ == "__main__":
    main()
