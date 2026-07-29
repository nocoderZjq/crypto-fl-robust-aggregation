# 当前实验摘要

## 实验状态

已完成可运行代码、单元测试、smoke test、一组离线真实手写数字数据 `sklearn_digits` pilot 实验，以及一组 MNIST pilot 主实验。

MNIST 最初下载失败，错误来自 torchvision 的两个默认源：

- `https://ossci-datasets.s3.amazonaws.com/mnist/`
- `http://yann.lecun.com/exdb/mnist/`

现已在代码中加入 CVDF / Google Storage 镜像 fallback，并成功完成 MNIST pilot。`sklearn_digits` 仍保留为无网络环境下的备用验证。

## MNIST Pilot 配置

- 配置文件：`configs/mnist_pilot.yaml`
- 数据集：MNIST
- 模型：MLP
- 客户端数：10
- 每轮客户端数：10
- 训练轮数：10
- Non-IID：Dirichlet alpha = 0.5
- 攻击：label_flip、sign_flip、gaussian_noise
- 恶意比例：0.0、0.2
- 方法：FedAvg、Krum、Trimmed Mean、Plain-SRSF、PP-SRSF

输出文件：

- `outputs/csv/mnist_pilot.csv`
- `outputs/figures/*.png`
- `outputs/tables/*.csv`

## 最终准确率

| attack_type | malicious_ratio | FedAvg | Krum | Trimmed Mean | Plain-SRSF | PP-SRSF |
|---|---:|---:|---:|---:|---:|---:|
| gaussian_noise | 0.0 | 0.805 | 0.805 | 0.763 | 0.805 | 0.805 |
| gaussian_noise | 0.2 | 0.343 | 0.707 | 0.675 | 0.707 | 0.707 |
| label_flip | 0.0 | 0.805 | 0.805 | 0.763 | 0.805 | 0.805 |
| label_flip | 0.2 | 0.602 | 0.645 | 0.588 | 0.639 | 0.639 |
| sign_flip | 0.0 | 0.805 | 0.805 | 0.763 | 0.805 | 0.805 |
| sign_flip | 0.2 | 0.124 | 0.707 | 0.505 | 0.707 | 0.707 |

## 恶意客户端检测率

恶意比例为 0.2 时的 true positive rate：

| attack_type | FedAvg | Krum | Trimmed Mean | Plain-SRSF | PP-SRSF |
|---|---:|---:|---:|---:|---:|
| gaussian_noise | 0.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| label_flip | 0.0 | 0.5 | 0.0 | 0.5 | 0.5 |
| sign_flip | 0.0 | 1.0 | 0.0 | 1.0 | 1.0 |

## 开销概览

平均每轮开销：

| method | crypto_time_ms | aggregation_time_ms | communication_bytes |
|---|---:|---:|---:|
| FedAvg | 0.000 | 0.313 | 4070800 |
| Krum | 0.000 | 3.310 | 4070800 |
| Trimmed Mean | 0.000 | 4.163 | 4070800 |
| Plain-SRSF | 0.000 | 0.386 | 4072080 |
| PP-SRSF | 12.809 | 4.051 | 4075920 |

## 初步结论

1. 无攻击时，FedAvg、Krum、Plain-SRSF、PP-SRSF 的最终准确率均约为 0.805，说明 PP-SRSF 的过滤流程不会明显破坏正常训练。
2. sign_flip 和 gaussian_noise 是容易通过距离异常发现的攻击，Krum、Plain-SRSF、PP-SRSF 都能达到 1.0 检测率，并显著优于 FedAvg。
3. label_flip 更隐蔽，当前草图相似度过滤只能达到 0.5 检测率，但最终准确率仍略优于 FedAvg 和 Trimmed Mean。
4. PP-SRSF 与 Plain-SRSF 在鲁棒性表现上接近，但引入了约 12.8 ms 的秘密共享距离计算开销和少量额外通信开销。

## 下一步建议

## 强化实验补充

已补充 MNIST + TinyCNN 强化实验，覆盖恶意比例 0.0、0.1、0.2、0.3。配置文件：

- `configs/mnist_tinycnn_strength.yaml`
- 输出：`outputs/csv/mnist_tinycnn_strength.csv`

MNIST + TinyCNN 最终准确率节选：

| attack_type | malicious_ratio | FedAvg | Trimmed Mean | Plain-SRSF | PP-SRSF |
|---|---:|---:|---:|---:|---:|
| gaussian_noise | 0.1 | 0.180 | 0.416 | 0.425 | 0.425 |
| gaussian_noise | 0.2 | 0.076 | 0.370 | 0.332 | 0.332 |
| gaussian_noise | 0.3 | 0.130 | 0.269 | 0.365 | 0.365 |
| label_flip | 0.1 | 0.365 | 0.361 | 0.311 | 0.311 |
| label_flip | 0.2 | 0.383 | 0.235 | 0.290 | 0.290 |
| label_flip | 0.3 | 0.244 | 0.181 | 0.286 | 0.286 |
| sign_flip | 0.1 | 0.141 | 0.260 | 0.425 | 0.425 |
| sign_flip | 0.2 | 0.106 | 0.179 | 0.332 | 0.332 |
| sign_flip | 0.3 | 0.104 | 0.186 | 0.365 | 0.365 |

同时补充 Fashion-MNIST + TinyCNN 轻量实验，验证第二数据集链路可复现。配置文件：

- `configs/fashion_tinycnn_strength.yaml`
- 输出：`outputs/csv/fashion_tinycnn_strength.csv`

Fashion-MNIST + TinyCNN 最终准确率节选：

| attack_type | malicious_ratio | FedAvg | PP-SRSF |
|---|---:|---:|---:|
| gaussian_noise | 0.2 | 0.161 | 0.358 |
| label_flip | 0.2 | 0.248 | 0.184 |
| sign_flip | 0.2 | 0.104 | 0.359 |

强化实验说明：

1. TinyCNN 在 6 轮、5000 样本下仍属轻量强化实验，收敛程度低于 MLP pilot，但已经补足更复杂模型和更多恶意比例。
2. PP-SRSF 在 sign_flip 和 gaussian_noise 下检测率稳定为 1.0，说明草图距离过滤对显著异常更新有效。
3. label_flip 仍然是难点，尤其在 Fashion-MNIST 上，单轮梯度相似度并不一定能稳定识别标签投毒。这应写入局限性和未来工作。

## 20 轮 MNIST + TinyCNN 聚焦实验

为获得更稳定的收敛趋势，已补充 20 轮 MNIST + TinyCNN 聚焦实验：

- 配置：`configs/mnist_tinycnn_long.yaml`
- 脚本：`scripts/run_mnist_tinycnn_long.sh`
- 输出：`outputs/csv/mnist_tinycnn_long.csv`

最终准确率：

| attack_type | malicious_ratio | FedAvg | Plain-SRSF | PP-SRSF |
|---|---:|---:|---:|---:|
| no attack | 0.0 | 0.704 | 0.705 | 0.705 |
| label_flip | 0.2 | 0.535 | 0.279 | 0.279 |
| sign_flip | 0.2 | 0.081 | 0.716 | 0.714 |
| gaussian_noise | 0.2 | 0.078 | 0.716 | 0.714 |

检测率：

| attack_type | FedAvg | Plain-SRSF | PP-SRSF |
|---|---:|---:|---:|
| label_flip | 0.0 | 0.5 | 0.5 |
| sign_flip | 0.0 | 1.0 | 1.0 |
| gaussian_noise | 0.0 | 1.0 | 1.0 |

这组结果可以作为报告主实验表之一。它比 6 轮强化实验更适合说明 PP-SRSF 的主线价值：在无攻击时不损伤收敛，在符号翻转和高斯噪声拜占庭攻击下显著优于 FedAvg，并与明文 Plain-SRSF 基本一致。label_flip 的结果则应作为诚实局限讨论。

## 下一步建议

1. 将 MNIST + TinyCNN 和 Fashion-MNIST + TinyCNN 训练轮数提升到 20-50 轮，作为最终版本主实验。
2. 补齐并人工核对 `report/references.bib` 中近三年文献的作者、页码、DOI。
3. 将 `report/main.tex` 按课程模板迁移到《密码学报》或学校推荐 LaTeX 模板。
4. 在报告中加入更严格的复杂度分析：草图维度 m、客户端数 n、模型维度 d 下的计算和通信复杂度。
