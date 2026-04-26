# experiment-YYYY-MM-DD-<technique>

## Setup

- **模型**：Qwen-VL-8B vX.Y.Z
- **后端**：vLLM 0.17.1
- **数据集**：golden-vN-stage（M 样本）
- **种子**：model=42, sampling=42
- **Manifest hash**：`<sha256>`
- **代码 commit**：`<git-sha>`（是否 clean？Y/N）

## Question

本实验在检验什么假设？

> 例：「Self-Consistency 用 N=5 抽样能通过减少单次方差，提升 noisy 数据上的 F1。」

## Method

简述技术做了什么。链接到技术文件：
- 实现：`techniques/vl_self_refinement/<name>.py`
- 设计参考：ts-platform/docs/design-vl-self-refinement.md §X

## Result

### 总体

| 指标 | Baseline | +<Technique> | Δ | 95% CI | p-value |
|---|---|---|---|---|---|
| F1 (Range, IoU=0.5) | | | | | |
| F1 (Range, IoU=0.3) | | | | | |
| F1 (Point) | | | | | |
| Precision | | | | | |
| Recall | | | | | |
| Mean IoU (TP) | | | | | |
| Latency P50 (s) | | | | | |
| Latency P99 (s) | | | | | |
| Token cost (mean) | | | | | |

### 按 data_type 分层

| data_type | N | Baseline F1 | +<Technique> F1 | Δ |
|---|---|---|---|---|
| step | | | | |
| noisy | | | | |
| constant | | | | |
| continuous | | | | |

### Failure cases

技术在哪些样本上比 baseline 更差：
- `series_NNN`：简述
- `series_MMM`：简述

## Conclusion

- **一句话结论**：
- **在哪类有效**：
- **在哪类有害**：
- **代价**：延迟 / token / GPU 时长开销
- **建议**：
  - [ ] 始终启用
  - [ ] 按 data_type 启用：……
  - [ ] 按优先级层启用：……
  - [ ] 弃用

## Next

具体的后续实验：
- [ ] 试参数 X = …… 的变体
- [ ] 与技术 Y 组合
- [ ] 调查 failure case Z
