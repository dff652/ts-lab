# 评测方法论

> **状态**：TODO —— 在首次跑 baseline 之前定稿。

本文档对 **F1 定义**具有权威性。`eval/metrics.py` 中的代码必须与之一致。

## 指标

### 主指标：Range-based F1（Tatbul 2018 简化版）

对每个预测区间 `p`：
- TP：存在某个 ground-truth `g` 使 `IoU(p, g) >= 阈值`
- FP：否则

对每个 ground-truth 区间 `g`：
- TP：存在某个预测 `p` 使 `IoU(p, g) >= 阈值`
- FN：否则

报告**两档阈值**：0.3（宽松）和 0.5（严格）。

### 次指标：Point-level F1

每个时间点 `t` 二分类（异常 / 正常），标准 precision/recall/F1。

报告它用于细粒度对比，对边界精度敏感。

### 第三指标：Mean IoU

仅针对匹配上的（TP）区间计算。反映边界质量。

## 报告要求

每份实验报告必须含：

| 指标 | 理由 |
|---|---|
| Range F1 @ IoU=0.3 | 宽松视角 |
| Range F1 @ IoU=0.5 | 严格视角 |
| Point F1 | 细粒度 |
| Mean IoU（仅 TP） | 边界质量 |
| 按 data_type 分层 | 抓住局部 positive |

## 统计显著性

任何"+technique"声明**强制**包含：

1. **配对差值**：每个样本贡献 (technique_F1 − baseline_F1)
2. **Bootstrap CI**：1000 次重采样，95% 置信区间
3. **McNemar 检验**：基于每样本 TP/non-TP 结果
4. **CI 跨 0 则拒绝该声明**

## 样本量

为在 80% power 下检测 F1 +3% 改进：
- 大约 300 配对样本
- Pilot 50 **power 不足**，仅够找方向
- Alpha 200 → 单技术显著性测试可行
- Beta 500 → 组合消融可行

## 分层报告

总指标外，**始终**报告按 data_type 的分层结果。一个总指标提升但某个 stratum 下降的技术，往往是错误选择。

## Holdout

预留 20% 的 golden 数据集作为**最终 holdout** —— 开发期不参与决策。仅在阶段末做最终验证时使用。

## 可复现性

每个上报的数字必须随附：
- 代码 commit SHA
- 数据集版本 + manifest hash
- 随机种子（模型 + 抽样）
- vLLM / Qwen-VL checkpoint 版本

详见 `reproducibility.md`。
