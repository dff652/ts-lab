# Golden Dataset 规范

> **状态**：TODO —— Track B Day 1 audit 完成后填充。

## Schema

（参见 `benchmarks/golden_dataset/README.md` 了解目录布局。）

## 版本历史

| 版本 | 样本数 | 创建时间 | 标注员 | kappa | 来源 |
|---|---|---|---|---|---|
| v0-audit | - | - | - | - | - |
| v1-pilot | 50 | TBD | TBD | TBD | TBD |

## 更新策略

1. 任何标注变化（新增或修改）都要升版本号
2. 每次变更后重算 manifest hash
3. 旧版本保留以便复现（小版本走 git；大版本走 DVC）
4. 每次 benchmark 运行都要记录所用的数据集版本

## 分布目标

Pilot v1（50 样本）的目标分布：

| 维度 | 目标 | 理由 |
|---|---|---|
| step | ~12 | data_type 平均 |
| noisy | ~13 | data_type 平均 |
| constant | ~12 | data_type 平均 |
| continuous | ~13 | data_type 平均 |
| 稀疏密度（1-2 异常） | ~17 | 平均 |
| 中等密度（3-5） | ~17 | 平均 |
| 密集密度（>10） | ~16 | 平均 |
| 短长度（<500） | ~17 | 平均 |
| 中长度（500-5000） | ~17 | 平均 |
| 长长度（>5000） | ~16 | 平均 |
| **负样本（无异常）** | **5-10** | **抓 FP** |
