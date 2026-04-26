# ts-lab 文档

ts-lab 的执行细节文档。治理 / 设计文档放在 `ts-platform/docs/`。

## 文件清单

| 文件 | 用途 | 状态 |
|---|---|---|
| `golden-dataset.md` | 数据集 schema + 版本历史 | TODO |
| `annotation-spec.md` | 异常定义、边界规则、示例 | TODO |
| `benchmark-methodology.md` | F1 定义 + 统计检验 | TODO |
| `reproducibility.md` | manifest schema + 版本锁定 + 种子控制 | TODO |
| `experiments/` | 单实验报告 | 持续累积 |
| `experiments/template.md` | 报告模板（作起点） | ✅ |

## 文档分布

| 类型 | 位置 |
|---|---|
| **治理与设计决策** | `ts-platform/docs/` |
| **执行细节（本目录）** | `ts-lab/docs/` |
| **讨论档案** | `ts-platform/docs/session-*.md` |

### ts-platform/docs/ 中的权威文档

- [design-vl-self-refinement.md](../../ts-platform/docs/design-vl-self-refinement.md) —— 主设计 ⭐
  - §3 7 大技术清单
  - §9 harness vs agent 定位
  - §10 预期收益与对比实验方法
  - §11 设计缺口与补强清单（含 ts-platform 8 项配合改动）
  - §15 三轨执行计划 + Track B 详解
  - §16 7 条执行建议（避免常见坑）
  - **附录 A：当前 ts-platform Pipeline 状态参考（file:line）** ⭐ 实施 technique 前必读
  - 附录 B：References（Wang 2022 / Madaan 2023 / Tatbul 2018 / vLLM）
- [session-2026-04-25.md](../../ts-platform/docs/session-2026-04-25.md) —— 完整八轮讨论档案
- [design-agent-layer.md](../../ts-platform/docs/design-agent-layer.md) —— 已弃用（保留作 Hermes/OpenClaw 对比 + 三层架构讨论的历史档案）

**单一信息源 —— 不要跨仓库复制，只做交叉引用。**

## 快速参考

实施 technique 时一定要先看：
1. **设计文档** `design-vl-self-refinement.md` 对应 §3.X 节（技术规格）
2. **Pipeline 现状** `design-vl-self-refinement.md` 附录 A（当前状态 + 痛点）
3. **TODO Reference Cards** `../TODO.md` RC-1 到 RC-10（决策规则）
4. **方法论** `benchmark-methodology.md` + `reproducibility.md`（评测方法）
