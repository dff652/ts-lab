# ts-lab Project TODO

> **当前最新方向**：[ts-platform/docs/design-vl-self-refinement.md](../ts-platform/docs/design-vl-self-refinement.md)
> **讨论档案**：[ts-platform/docs/session-2026-04-25.md](../ts-platform/docs/session-2026-04-25.md)
> **Last updated**：2026-04-26

This file is the **single source of truth** for project planning. The session-internal TodoWrite list mirrors this when an agent is actively working.

---

## 项目定位（必读）

- **不是 agent 框架，是 harness**（推理时增强工程）—— Python 决定控制流，LLM 当函数调用
- **目标**：提高 Qwen-VL 推理 → JSON 解析的**稳定性**和**准确度**
- **不做**：L3 模型编排 / 微调 / 切换检测模型 / 重构 ts-platform pipeline
- **范围**：通过外部调用 ts-platform REST API + 后处理实现（ts-platform 仅需加 3 个 API 透传字段）

**预期收益**（来自文献推断）：
- 乐观（30%）：F1 +15~25%
- 中性（50%）：F1 +8~12%
- 悲观（20%）：F1 +0~5%（但稳定性提升仍真实）

---

## 三轨当前状态

| Track | 内容 | Day 1 投入 | 状态 |
|---|---|---|---|
| **A 工程** | ts-lab 仓库 + backend/client SDK + baseline | 1-2 小时 | ✅ 仓库骨架完成 |
| **B 数据** | audit + 50 pilot 标注 + kappa | 1-2 小时 | 🔴 未开始 |
| **C 平台** | 3 个 ts-platform issue + 跟进合并 | 1-2 小时 | 🔴 未开始 |

**三轨必须 Day 1 同步启动**，不是顺序。

---

## 阻塞链

```
Track A SDK ──┐
              ├──→ baseline ──┬──→ robust_parser ──→ self_consistency
Track B 50 样本 ┘             │                  ──→ self_critique
                              │                  ──→ format_locking
Track C Issue 1 ──────────────┴──→ guided_json
Track C Issue 2 ──────────────────→ chain_of_zoom
                                                  ──→ 组合消融 ──→ Sink
```

## 关键 Deadline

| 任务 | Deadline | 阻塞 |
|---|---|---|
| Issue 1 提交（#4） | Day 1 | 平台排期 |
| golden v1-pilot 完成（#13） | Day 10 | baseline 阻塞 |
| Issue 1 合并 | Day 14 | guided_json 阻塞 |
| Issue 2 合并 | Day 21 | chain_of_zoom 阻塞 |

---

# 📋 Reference Cards（行动前必看）

## RC-1：Audit 7 个必答问题（任务 #7）

任何 audit 报告必须回答这 7 个问题，每个 1-2 行 SQL 或 Python 即可：

1. **data_pool 总条数** —— 决定项目可行性
2. **results.label 不为空的多少？label 格式样例** —— 决定走 A/B/C 路径
3. **data_type 分布**（step / noisy / constant / continuous） —— 决定能否分层抽样
4. **长度分布**（min / median / max） —— 决定渲染参数选择
5. **跑过 Qwen-VL 推理的多少？raw_model_output 是否还在** —— 决定能否复用历史推理
6. **完全无异常的负样本多少** —— 决定能否构造负样本集
7. **数据来源 + 是否含公开数据集**（Yahoo S5 / KPI 等） —— 评估与 Qwen-VL 训练集泄露风险

**没回答这 7 个问题的 audit 不算完成。**

## RC-2：Track B 路径决策（任务 #8）

根据 RC-1 #2 的结果选路径：

| 情景 | 数据状态 | 工作 | 时间 |
|---|---|---|---|
| **A：标注好** | 有人工精确异常区间 + 类型 | 筛 50 → 抽样质检 → kappa → 直接用 | 3-5 天 |
| **B：需校准** | 仅 "任务对/错" 二值，无精确边界 | 选 50 → 补标边界 → kappa → 用 | 1.5-2 周 |
| **C：从零标** | 仅有原始时序，无任何标注 | 选 50 → 完全标注 → kappa → 用 | 2-3 周 |

**多数实际情况是 B**——粗粒度反馈存在，精确边界缺失。

## RC-3：50-Sample Pilot 分布目标（任务 #10）

| 维度 | 分布 | 备注 |
|---|---|---|
| **data_type** | step ~12 / noisy ~13 / constant ~12 / continuous ~13 | 平均分布 |
| **异常密度** | 稀疏(1-2) ~17 / 中等(3-5) ~17 / 密集(>10) ~16 | 平均分布 |
| **长度** | 短(<500) ~17 / 中(500-5000) ~17 / 长(>5000) ~16 | 平均分布 |
| **负样本** | 5-10 个完全无异常 | **必须有，抓 FP 金标** |

**50 个精心覆盖 > 500 个相似重复**。多样性优先于数量。

## RC-4：标注一致性质量门（任务 #12）

2 名标注员独立标 30 样本，按 segment-level IoU≥0.5 计算 Cohen's kappa：

| Kappa | 决策 |
|---|---|
| **< 0.6** | 🔴 **STOP**——回去对齐规范，不许批量启动 |
| **0.6 - 0.7** | 🟡 勉强启动，记录为风险 |
| **≥ 0.7** | 🟢 放心批量 |

跳过这一步，benchmark 数字就是噪音。

## RC-5：Baseline F1 情景应对（任务 #22）

跑完 baseline 3 次后，按总 F1 进入对应分支：

| Baseline F1 | 含义 | 应对策略 |
|---|---|---|
| **> 0.85** | 头部空间小 | 主攻**稳定性**（解析失败、方差），不指望 F1 大涨 |
| **0.5 - 0.85** | 经典优化区 | 7 大 technique 都适用，按 #23-29 计划走 |
| **< 0.5** | 模型本身不行 | 🔴 **STOP**——technique 救不了，先重做 prompt 或换模型；考虑微调（但微调不在本项目范围）|

**baseline 3 次 std > 0.02 也要警觉**——任务本身有显著随机性，需更多重复才能区分技术差异。

## RC-6：Robust Parser 5 级 Fallback（任务 #23）

按顺序尝试，先成功者返回：

1. **Tier 1**：`json.loads(raw)` 直接解析
2. **Tier 2**：剥离 markdown ` ```json ... ``` ` 包装后再解析
3. **Tier 3**：修复尾逗号 + 单引号转双引号 + 已知格式错误后再解析
4. **Tier 4**：正则 `\[(\d+)\s*,\s*(\d+)\]` 抽取所有 [s, e] 对（兜底，丢失 type/reason）
5. **Tier 5**：调 Qwen-VL 纯文本（不传图）让它"重写为合法 JSON"

**目标**：解析失败白跑率 → 0。当前 vllm_client.py:303-330 解析失败直接 error，是最该改的点。

## RC-7：3 个 ts-platform Issue 规格（任务 #3）

每个 issue 含 5 部分：背景 / 需求 / 验收 / 代码指引 / lab 依赖。

### Issue 1 — `response_format` 透传（最高优先，必须 Day 14 前合并）

- **背景**：guided_json technique 需要 vLLM 强约束 JSON schema 输出
- **改动**：`vllm_backend.py` 接受 `response_format` 参数，透传到 vLLM `extra_body.guided_json`
- **验收**：传入 schema → 输出 100% 符合 schema → 解析成功率 >99.9%
- **代码指引**：`backend/app/adapters/gpu_algorithms/vllm_backend.py`、`qwen.py`、`api/inference_external.py`
- **工作量**：10-20 行

### Issue 2 — 暴露渲染后图像

- **背景**：chain-of-zoom 需要知道实际渲染了什么图，才能截取对应区域
- **改动**：API 加 `return_rendered_image=True` 参数，response 含 base64 编码图像
- **验收**：传入参数后 response 多 `rendered_image_b64` 字段
- **工作量**：约 30 行
- **lab 依赖**：阻塞 #29 chain_of_zoom

### Issue 3 — 暴露原始 VL 输出

- **背景**：robust parser / self-critique 需要原始文本（不止解析后异常）
- **改动**：results 表加 `raw_model_output` 字段；API 返回此字段
- **验收**：results 查询返回 raw_model_output；DB migration 完成
- **工作量**：migration + 约 50 行
- **lab 依赖**：阻塞 #23 robust_parser 的 Tier 5、#27 self_critique

## RC-8：F1 定义 & 统计要求（任务 #17 #18 #21）

**F1 必须用以下三种一起报**：

1. **Range-based F1（主）**：IoU 阈值 0.3 + 0.5 两档（Tatbul 2018 简化版）
2. **Point-level F1（次）**：每时间点二分类，对边界精度敏感
3. **Mean IoU**（仅 TP）：边界质量

**所有"+technique"声明必须含**：
- 配对差值（per-sample technique − baseline）
- Bootstrap 95% CI（1000 次重采样）
- McNemar p-value
- **CI 跨 0 拒绝该声明**

**样本量要求**：
- 检测 +3% F1 改进 80% power → ~300 配对样本
- Pilot 50 → 仅够"找方向"，**不够单技术显著性测试**
- Alpha 200 → 单技术显著性测试
- Beta 500 → 组合消融 + 保留 100 做最终验证

**保留集**：20% golden 数据集**不参与开发期决策**，只在 phase 末用于最终验证。

## RC-9：Golden Dataset 版本演化

| 版本 | 样本 | 用途 | 触发条件 |
|---|---|---|---|
| v0-audit | - | 数据资产盘点 | audit 完成 |
| **v1-pilot** | **50** | **方向验证 + 流程跑通** | **当前阶段** |
| v2-alpha | 200 | 单技术显著性测试 | pilot 跑通后 |
| v3-beta | 500 | 组合消融 + holdout | alpha 验证后 |
| v4-production | 1000+ | 持续扩充（来自用户反馈） | 上线后 |

仓库归属：
- v1-pilot < 10MB → 直接 git 跟踪
- v2-alpha / v3-beta → 引入 git-lfs 或 DVC
- v4-production → 新建 `ts-data` 独立仓库

## RC-10：Sinking SOP（任务 #31-34）

**没有这个流程，不许把 lab 的胜出 technique 推到 ts-platform 生产**：

1. **Lab benchmark 验证**：≥ +3% F1 提升，p < 0.05
2. **写 ts-platform 沉淀 design doc**（如 `design-self-consistency-integration.md`）
3. **PR + feature flag**（默认 OFF，命名 `vl_<technique>_enabled`）
4. **影子模式 1 周**：新路径与 baseline 并行跑，diff 输出
5. **canary 10% 流量 1 周**，监控吞吐 / 延迟 / 用户反馈
6. **全量切换**；feature flag **保留 1 个月**做 fallback

任何一步失败都回退，不许跳步。

---

# 📋 Tasks

## Day 1 收尾（立即）

- [ ] **#1** 初次提交 ts-lab Day 1 骨架（`git add -A && git commit -m "init: ts-lab Day 1 skeleton"`）
- [ ] **#2** 创建 venv，`pip install -e ".[dev]"`，运行 `pytest tests/ -v` 验证骨架

## Track C — 平台配合（并行 Day 1）

- [x] **#3** 起草 3 个 ts-platform issue（按 RC-7 规格）→ 已完成于 [docs/track-c/](docs/track-c/)
- [ ] **#4** 提交 3 个 issue 到 ts-platform 仓库，加优先级标签（**Day 1 必须**）
- [ ] **#5** 与平台团队同步会议，确认 Issue 1 排期 ≤ Day 14

### Track C nice-to-have（不阻塞 lab，但提升体验，提交 issue 但不强制 deadline）

- [ ] **#5a** ts-platform API 返回延迟/token 计费字段（中间件 metrics）
- [ ] **#5b** ts-platform 自定义渲染参数 API 完善（dpi/figsize/linewidth 全部可调）
- [ ] **#5c** ts-platform 支持单图复用（chain-of-zoom 优化用，避免重复渲染）
- [ ] **#5d** ts-platform 数据集快照机制扩展（基于现有 dataset_snapshots）
- [ ] **#5e** ts-platform Prompt 模板 ID 化（便于版本追踪）

## Track B — 数据（并行 Day 1）

- [ ] **#6** 读 `ts-platform/backend/app/models/` 真实 schema，把 `benchmarks/scripts/audit.py` 改成可执行版本
- [ ] **#7** 跑 audit 回答 RC-1 七问，输出 `benchmarks/golden_dataset/audit/data-audit-YYYY-MM-DD.md`
- [ ] **#8** 根据 audit 决定路径 A/B/C（按 RC-2）
- [ ] **#9** 完善 `docs/annotation-spec.md`：10 个正反例 + 边界规则 + 置信度尺度
- [ ] **#10** 分层抽样 50 候选（按 RC-3 分布目标）
- [ ] **#11** 试标 5 个最难样本，发现 spec 歧义就改
- [ ] **#12** 两位标注员各标 30 样本，计算 Cohen's kappa（按 RC-4 质量门）
- [ ] **#13** 构建完整 golden v1-pilot 数据集（50 样本 + manifest + audit 报告）

## Track A — 工程（Day 2-7）

- [ ] **#14** 阅读 `ts-platform/backend/tests/example_api_usage.py` 与 `tests/integration/`，规划 `backend/client/` 抽取边界
- [ ] **#15** 在 ts-platform 实现 `backend/client/`（auth / inference / data_pool / comparisons / results）
- [ ] **#16** 重构 ts-platform `tests/` 改为 import client，验证 CI 通过
- [ ] **#17** 实现 `eval/metrics.py`（按 RC-8 三种 F1 + per_data_type breakdown）
- [ ] **#18** 实现 `eval/compare.py`（按 RC-8 paired_bootstrap / McNemar / comparison_table）
- [ ] **#19** 实现 `techniques/vl_self_refinement/baseline.py`（单次 Qwen-VL 调用 via client SDK）
- [ ] **#20** 实现 `benchmarks/run_benchmark.py` CLI runner 含 manifest 输出
- [ ] **#21** 在 golden v1-pilot 上跑 baseline 3 次，确立 F1 方差基线
- [ ] **#22** 应用 RC-5 baseline-F1 决策树

## Techniques — 实验（Week 3+）

按优先级顺序实施。每个 technique 完成后必须**立即写实验报告**到 `docs/experiments/YYYY-MM-DD-<technique>.md`（用 `docs/experiments/template.md`）。

- [ ] **#23** 实现 `robust_parser.py` 5 级 fallback 链（按 RC-6，最高优先零依赖）
- [ ] **#24** 跑 robust_parser benchmark，写实验报告
- [ ] **#25** 实现 `guided_json.py`（**Blocked on**: Track C Issue 1 合并），跑 benchmark + 写报告
- [ ] **#26** 实现 `self_consistency.py` 含 N=5 IoU 投票，跑 benchmark + 写报告
- [ ] **#27** 实现 `self_critique.py` 含保守再审 prompt，跑 benchmark + 写报告
- [ ] **#28** 实现 `format_locking.py` 含 few-shot 例子，跑 benchmark + 写报告
- [ ] **#29** 实现 `chain_of_zoom.py`（**Blocked on**: Track C Issue 2 合并），跑 benchmark + 写报告
- [ ] **#29b** 实现 `token_budget.py` 自适应 max_tokens（消除 truncation 失败），跑 benchmark + 写报告
- [ ] **#30** 组合消融：堆叠胜出 technique，画 cost-F1 帕累托前沿

## Sink — 沉淀回 ts-platform（按 RC-10 流程）

- [ ] **#31** 识别胜出组合（≥+3% F1，p<0.05），起草 ts-platform integration design doc + PR（feature flag 默认 OFF）
- [ ] **#32** 影子模式 1 周：新路径与 baseline 并行跑，diff 输出
- [ ] **#33** canary 10% 流量 1 周，监控吞吐 / 延迟 / 用户反馈
- [ ] **#34** 全量切换；feature flag 保留 1 个月做 fallback

---

# 🚦 操作约定

## 状态约定

- `[ ]` pending
- `[~]` in progress
- `[x]` completed
- `[!]` blocked（在末尾加 `**Blocked on**: <reason>`）

## 更新规则

1. 任何 todo 状态变化都要在这里改（不要只改 session todo）
2. 完成的 todo 不删除，标 `[x]` 留作时间线
3. 新发现的 todo 加到对应 Track 末尾，编号续接
4. 重要里程碑（baseline 完成、首个 technique 沉淀等）在文件末尾加日志
5. Session 结束前确保此文件与 session 状态一致

## 不要踩的坑（避免常见失败）

- ❌ 没跑 audit 就开始建数据集
- ❌ 没建 baseline 就开始写 technique
- ❌ 一上来就实现 chain-of-zoom（依赖最多，最复杂）
- ❌ 实验报告"待补"——必须 technique 一跑完就写
- ❌ 直接把 notebook 代码搬到 techniques/（要重写）
- ❌ 跳过 kappa 检验直接批量标注
- ❌ Lab 验证完直接 PR 上线（必须走 RC-10 影子+canary）
- ❌ 改 F1 定义没更新 `docs/benchmark-methodology.md`

---

# 📅 完成日志

> 第一条完成的 todo 起开始记录。格式：`YYYY-MM-DD #编号 简述`

- 2026-04-26 #3 起草 3 个 ts-platform issue（response_format / rendered image / raw output），存于 docs/track-c/

---

# 📚 Cross-Reference

## ts-lab 内部
- [README.md](README.md) — 项目入口
- [docs/golden-dataset.md](docs/golden-dataset.md) — 数据集规范
- [docs/annotation-spec.md](docs/annotation-spec.md) — 标注规范
- [docs/benchmark-methodology.md](docs/benchmark-methodology.md) — F1 定义权威文档
- [docs/reproducibility.md](docs/reproducibility.md) — 复现 SOP
- [docs/experiments/template.md](docs/experiments/template.md) — 实验报告模板

## ts-platform（治理 / 设计决策）
- [design-vl-self-refinement.md](../ts-platform/docs/design-vl-self-refinement.md) — 主设计 ⭐
- [session-2026-04-25.md](../ts-platform/docs/session-2026-04-25.md) — 完整讨论档案（八轮）
- [design-agent-layer.md](../ts-platform/docs/design-agent-layer.md) — 历史方案（已弃用）
