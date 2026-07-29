# 课程报告正文建议结构

题目：基于秘密共享的密态异常梯度过滤与鲁棒安全聚合机制研究

英文题目：Privacy-Preserving Robust Federated Aggregation Against Label-Flipping and Byzantine Attacks via Secret-Shared Similarity Filtering

## 摘要

概述联邦学习中隐私保护与鲁棒聚合的冲突：安全聚合隐藏客户端更新，但难以过滤投毒更新；鲁棒聚合需要明文距离或坐标统计，又可能暴露客户端梯度。本文提出 PP-SRSF，通过低维随机投影草图、定点量化、加性秘密共享和草图域距离过滤，在不暴露完整明文更新的前提下剔除异常客户端，并对剩余客户端执行安全聚合。

## 1 引言

1. 联邦学习中的标签翻转、符号翻转和拜占庭噪声攻击。
2. 传统 Secure Aggregation 与 Krum/Trimmed Mean/Median 的目标冲突。
3. 本文贡献：
   - 设计秘密共享草图域异常过滤机制。
   - 将鲁棒过滤与安全聚合解耦。
   - 在模型性能、检测率、误杀率、通信和计算开销上进行联合评估。

## 2 相关工作

建议覆盖四类文献：

1. 安全聚合与可验证聚合。
2. 拜占庭鲁棒联邦学习。
3. 标签翻转和数据投毒攻击。
4. MPC、秘密共享与密态距离计算。

课程 PDF 要求至少 15 篇近三年高质量文献。当前仓库尚未完成完整文献表，后续需要重点补齐 2024-2026 年 USENIX Security、IEEE S&P、CCS、NDSS、NeurIPS、AAAI、IEEE TIFS/TDSC/TMC 等来源。

## 3 系统模型与威胁模型

系统参与方包括客户端、协调服务器、两个非共谋聚合方 AggA/AggB。客户端持有本地私有数据并上传模型更新；服务器协调全局模型训练；AggA/AggB 接收草图秘密共享份额并执行密态距离原型计算。

威胁模型采用课程原型级半诚实聚合方假设：

1. 单个聚合方遵循协议但试图从份额中推断客户端信息。
2. AggA 与 AggB 不共谋。
3. 部分客户端可为恶意客户端，执行标签翻转、符号翻转或高斯噪声更新。
4. 当前实现不声称抵抗恶意安全 MPC 中的任意偏离协议行为。

## 4 方法设计

1. 客户端本地训练得到模型更新。
2. 使用公共随机投影矩阵生成低维草图。
3. 将草图定点量化到整数有限域。
4. 对量化草图执行加性秘密共享。
5. 在草图域计算客户端间距离矩阵。
6. 使用 Krum 风格分数选择低异常分数客户端。
7. 对筛选后的客户端更新执行简化安全聚合。

可直接引用：

- `src/report_assets/algorithm_pp_srsf.tex`
- `src/report_assets/protocol_sequence_diagram.tex`
- `src/report_assets/threat_model.md`

## 5 安全性分析

需要重点论证：

1. 单个聚合方只能看到随机份额，无法重构客户端草图。
2. 服务器不直接访问完整明文更新用于异常过滤。
3. 安全聚合阶段的成对掩码在求和后抵消，服务器只获得聚合结果。
4. 泄露边界：当前原型会暴露 pairwise sketch distance 或过滤结果，报告中应明确这是鲁棒过滤所需的最小统计之一。
5. 局限：完整恶意安全 MPC、dropout-resilient SecAgg、抗多数恶意几何中位数和正式 game-based proof 属于后续工作。

## 6 实验设计

正式主实验建议：

1. 数据集：MNIST、Fashion-MNIST；当前离线 pilot 使用 `sklearn_digits`。
2. 模型：TinyCNN 作为主实验，MLP 作为快速验证。
3. 客户端：20 个客户端，Dirichlet alpha = 0.5。
4. 攻击：label_flip、sign_flip、gaussian_noise。
5. 恶意比例：0.0、0.1、0.2、0.3、0.4。
6. Baseline：FedAvg、SecureAgg、Krum、Trimmed Mean、Coordinate Median、Plain-SRSF、PP-SRSF。
7. 指标：Accuracy、Macro-F1、TPR、FPR、crypto_time_ms、aggregation_time_ms、communication_bytes。

## 7 实验结果与分析

先使用 `report/experiment_summary.md` 中的 pilot 结果写趋势分析。正式报告中应在 MNIST/Fashion-MNIST 结果跑完后替换这些离线 pilot 数字。

建议分析角度：

1. 无攻击时 PP-SRSF 与 FedAvg 接近，说明过滤机制不会明显破坏正常收敛。
2. sign_flip 和 gaussian_noise 下，Krum/Plain-SRSF/PP-SRSF 能有效识别异常更新。
3. label_flip 更隐蔽，单纯梯度相似度过滤并不总是优于 FedAvg，需要讨论局限。
4. PP-SRSF 相比 Plain-SRSF 增加秘密共享和密态距离开销，但保留了接近的鲁棒性。

## 8 结论与展望

总结 PP-SRSF 的系统级价值：在隐私保护、安全聚合和鲁棒过滤之间提供可运行折中。展望包括完整 MPC、密态几何中位数、抗多数恶意、可验证聚合和更大规模数据集。
