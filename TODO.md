# ts-lab Project TODO

> **当前最新方向**：[ts-platform/docs/design-vl-self-refinement.md](../ts-platform/docs/design-vl-self-refinement.md)
> **讨论档案**：[ts-platform/docs/session-2026-04-25.md](../ts-platform/docs/session-2026-04-25.md)
> **Last updated**：2026-05-07（增补 Code Review 节）

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
| **A 工程** | ts-lab 仓库 + backend/client SDK + baseline | 1-2 小时 | 🟡 骨架 ✅ + push 远程 ✅ + 文档全中文 ✅；SDK 抽取未启动（已发现 `backend/tests/examples/client.py` 509 行半成品） |
| **B 数据** | audit + 50 pilot 标注 + kappa | 1-2 小时 | 🔴 未开始 |
| **C 平台** | ~~3 个 ts-platform issue + 跟进合并~~ → 直接实装 3 个 ts-platform 改动 | 1-2 小时 | 🟡 草稿完成；**单人维护，无需走 issue tracker**（详见下方 §"本次会话关键发现"） |

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

## 关键 Deadline（2026-04-26 校准：单人维护下无外部排期，所谓"deadline"即"自我实施窗口"）

| 任务 | 实施窗口 | 阻塞 |
|---|---|---|
| ~~Issue 1 提交~~ → Issue 1 实装（#36） | 半天 | 待 Python 环境（#35）+ 拍板即可启动 |
| Issue 2 实装 | 半天 | guided_json 跑通后再做更划算 |
| Issue 3 实装 | 1-2 小时 | **紧迫性已降**，因 `vllm_client.py` 已 graceful 失败（详见 §"本次会话关键发现"） |
| golden v1-pilot 完成（#13） | Day 10 | baseline 阻塞 |

---

# 📋 Code Review 关键发现（2026-05-07）

> 在 llm-platform session 间隙做的 ts-lab 代码 + 文档复审。
> 结论：**设计意图清晰、骨架质量高；项目自 2026-04-26 起停滞 11 天，决策瘫痪是主要瓶颈**。

## 🟢 已就绪 / 应保留

- 单一事实源贯彻（[docs/README.md](docs/README.md) 跨仓库引用，无副本）
- Reference Cards RC-1~10 把高频判断点卡片化，是文档工程亮点
- [docs/pending-decisions.md](docs/pending-decisions.md)（2026-05-06）的「选项 + 推荐 + 连锁动作」格式可作为决策文档模板复用
- 全部 technique 文件 `raise NotImplementedError` 风格符合「显式失败优于隐式兜底」（与 llm-platform 工程原则 1 一致）
- `eval/metrics.py::iou` + `tests/test_smoke.py::test_iou_basic` 是唯一真实现 + 真覆盖，作为后续 self_consistency 投票 / range_f1 的基础选得对

## 🟡 漂移 / 需更新

| 项 | 现状 | 建议 |
|---|---|---|
| TODO.md 11 天未动 | 2026-04-26 → 2026-05-07 三轨除空窗记录外无推进 | 加进度日志条目说明原因（已加，见上方 §完成日志） |
| `.venv/` 已存在但 pytest 未装 | `python -m pytest` 报 `No module named pytest`，与 #35 状态「本机无 venv」矛盾 | 要么收尾 `.venv/bin/pip install -e ".[dev]"`，要么删 `.venv` 重来 |
| README.md 「Development Status (2026-04-26)」 | 日期硬编码 | 改为 `see TODO.md` 或自动从 git log 生成 |
| `docs/annotation-spec.md` 标 TODO 但已有边界规则 / 置信度尺度 / kappa 门 | 实际是「框架就绪，等 pilot 试标补示例」 | 状态描述精化 |
| `pyproject.toml` 依赖（pandas/numpy/sklearn/matplotlib/pyyaml/requests/pydantic）当前任何 .py 都未实际 import | 声明意图但无实证 | 加注释说明每个 dep 给哪个 technique 用，或等真用时再加（呼应 llm-platform 今天清 ts-platform 死依赖思路） |

## 🔴 设计层面真问题

### A. 决策瘫痪 = 项目阻塞

[docs/pending-decisions.md](docs/pending-decisions.md) 三项（env / SDK / SOP）连环阻塞 #2 / #14-16 / #36。11 天没拍 = 在为不存在的他人保留选择权。

按 llm-platform 同类决策的判断逻辑（工程原则 + 单人维护语境），自拍推荐：

- **env → o1 uv** —— 无 sudo、单二进制、未来管 pyproject 也省事；pending-decisions.md 里推荐就是它
- **SDK → e2 薄壳** —— 「lab 阶段验证完技术再回头抽干净 SDK」，符合「不要 premature abstraction」；e1 走干净 package 是在还没验证 API surface 时投 2-3 天，风险/收益不划算
- **SOP → l2 自测+merge** —— 单人维护无外部用户，l1 影子+canary 是 ceremony；若未来 ts-platform 接入他人，再升级到 l3

### B. `data: Any` 抹平了 technique 契约

8 个 technique 文件签名都是 `def detect(data: Any, params: dict | None = None) -> list[dict]`。`Any` 让「所有 technique 在调用层可互换」这个 harness 核心假设失去类型保证 —— IDE 不补全、benchmark runner 拿到 technique 时无法静态校验、未来组合消融时数据形状漂移会运行时炸。

建议新建 `techniques/types.py`：

```python
from typing import Protocol, TypedDict, Literal

class TimeSeriesInput(TypedDict):
    series_id: str
    values: list[float]
    timestamps: list[int] | None
    data_type: Literal["step", "noisy", "constant", "continuous"]
    inference_mode: Literal["text", "grounding"]

class AnomalyInterval(TypedDict):
    interval: tuple[int, int]
    type: str
    reason: str

class Technique(Protocol):
    def detect(self, data: TimeSeriesInput, params: dict | None = None) -> list[AnomalyInterval]: ...
```

未来 ts-platform SDK 抽完后（#15），types.py 这层可以引用 SDK schema，避免重复定义。

## 复用 llm-platform 的工程原则（2026-05-07 沉淀）

[../llm-platform/docs/engineering-principles.md](../llm-platform/docs/engineering-principles.md) 7 条原则中以下 5 条直接适用 ts-lab：

| 原则 | 在 ts-lab 的应用 |
|---|---|
| 1 显式失败优于隐式兜底 | NotImplementedError 已遵守；后续实装 robust_parser Tier 5 失败时也必须显式抛错而非返回空 list |
| 2 错误出现在使用现场 | benchmark runner 调 ts-platform API 失败时，不允许 `except: pass`，必须 log + 抛；与 llm-platform 前端 `.catch(() => {})` 普查同源 |
| 5 单一事实源 | 已遵守；持续维护时注意 pyproject 依赖 / README 安装段不漂移（llm-platform 此处出过漂移） |
| 6 发布可复现 | `docs/reproducibility.md` manifest 设计已对齐；实施时严守 |
| 7 运维可验证 | 所有 RC 卡片已是「可验证形式」（数字门槛 + 决策树）；继续保持 |

并新建 `fallback by design:` 注释规范：robust_parser 5 级链中如果 Tier N 故意 silent fallback 到 Tier N+1（不抛），必须加该注释说明 why，避免后人误以为是 silent swallow。

---

# 🧭 技术路线讨论补遗（2026-05-07）

> 同日讨论 ts-lab 7 件套 vs Function Calling / Constrained Decoding 与 llm-platform 复用边界后的结论沉淀。**保留这节是为了避免下次重新讨论"FC 是新技术吗"、"llm-platform 要不要内嵌 robust_parser"等已经判断过的问题**。

## 稳定性 vs 准确性 — 两轴正交分解

7 件套不是"7 个独立的提升 trick"，而是分别打**两条独立失败路径**：

```
                          稳定性                      准确性
                  (输出能不能解析、能不能用)    (区间是否检对、IoU 多少)
                  ─────────────────────────    ──────────────────────
失败模式 →        JSON 不合法 / truncation /     模型漏检 / 误检 / 边界偏 /
                  格式漂移                       长序列细节丢失

技术映射 →
  稳定性侧 4 件套                              准确性侧 3 件套
  ━━━━━━━━━━━━━━━                          ━━━━━━━━━━━━━━━
  robust_parser 🔴   (5 级 fallback)         self_consistency 🟡 (N=5 IoU 投票)
  guided_json 🔴     (vLLM 约束解码)         self_critique 🟡    (KEEP/REMOVE/REVISE)
  format_locking 🟢  (few-shot 例子)         chain_of_zoom 🟡    (二审，最高潜力)
  token_budget 🟢    (自适应 max_tokens)
```

**为什么两轴必须分开验证**：
- 稳定性 = 让"白跑率"（解析失败 / truncation）→ 0；用同一批样本前后对比 parse_success_rate 即可
- 准确性 = F1 提升；需配对样本 + bootstrap CI + McNemar p-value（详见 RC-8）
- 一个技术只在一轴有提升而另一轴没动是常态（如 token_budget 主减白跑率，但不一定让 F1 涨）

**实施时务必分开报指标，否则会出现"看起来 F1 涨了 3%"但实际只是稳定性堵住了 truncation 的假胜出**。

## Function Calling 与 Constrained Decoding ≠ 新技术

| 文中术语 | ts-lab 7 件套对应 | 关系 |
|---|---|---|
| Constrained Decoding（约束解码） | `guided_json` | **完全相同** —— 都是 vLLM 生成层 logits mask |
| Function Calling | （**未在 7 件套**） | **独立第 8 种解法**，与 guided_json 同位（事前约束） |
| （未提及） | `robust_parser` | **事后兜底**，与上两者**互补不互斥** |

**事前约束 vs 事后兜底的统一框架**：

```
理想链路:
  request → vLLM (guided_json 强约束) → response
                                          │
                                          ▼
                              json.loads OK? ──Yes──► done
                                          │
                                         No (极少发生，约束失效 / 模型 OOM 截断)
                                          │
                                          ▼
                              robust_parser 5 级兜底
                                          │
                                          ▼
                              仍失败 → log + 标记任务失败（不静默吞）

Function Calling 是另一条平行路径（vs guided_json 的对照实验）:
  request (with tools spec) → vLLM tool_calling mode → tool_calls JSON
```

**给 ts-lab 的判断**：
- guided_json + robust_parser 已能闭环，不需要 Function Calling 也能解决稳定性
- Function Calling 在 Qwen-VL 上未知有效（视觉模型工具调用训练通常弱于文本模型）
- 优先级：**低 nice-to-have**，作为对照实验留存（见 #45）
- ⚠️ **不要把 Function Calling 当"新发现的银弹"重新规划技术路线** —— 它既不解决"内容正确性"（只是结构化），也只是事前约束的另一种形式

## 约束解码不是银弹（重要警告）

> 约束解码保证**格式**容错 0，**不**保证**内容**容错 0

```
约束解码保证的         约束解码不保证的
─────────────         ─────────────────
JSON 语法合法         字段值语义正确
schema 字段齐全       数字/区间是真的
枚举值在白名单内      模型没漏检 / 没误检
                      模型没"放弃挣扎"输出空对象 / 空数组
```

**所以**：
- 在 ts-lab 异常检测、医疗诊断、金融风控这类**内容必须对**的场景，约束解码 + Function Calling 都只是必要不充分条件
- 仍必须配合**多次采样投票**（self_consistency）+ **二次审查**（self_critique）+ 关键场景**人工 review**
- 这正是 7 件套同时设计稳定性 4 件 + 准确性 3 件的根本原因

## 实施顺序的微调

design §15.6 默认序：robust_parser → guided_json → baseline → ...

但考虑到本机环境/上游阻塞，2026-05-07 调整为：

| 步骤 | 任务 | 阻塞情况 | 时间 |
|---|---|---|---|
| **A** | `robust_parser` 5 级 fallback 实装 + 单元测试 | **无依赖**，纯 Python | 2-3 小时 |
| **B** | 收集 ~10 条真实 raw_text fixture（从 vllm_client.py 已捕获的 raw_text） | 需要环境拍板（#35） | 30 分钟 |
| **C** | ts-platform Issue 1 实装（#36，response_format 透传） | 需要环境 + Python 环境 | 半天 |
| **D** | `guided_json` 实装 + ANOMALY_SCHEMA 透传 | 等 C | 半天 |
| **E** | A/B 对比 baseline：解析失败率 / F1 / latency | 等 baseline + golden v1 | Day 10+ |

**A 是真正可立即开工的任务**（不需要 venv 也能写，单测用 stdlib pytest 风格也行）。

## llm-platform 复用边界（与本项目无直接代码关系）

讨论结论摘要（详细分析见 [../llm-platform/docs/gateway-stability-strategy.md](../llm-platform/docs/gateway-stability-strategy.md) 2026-05-07）：

| 维度 | 结论 |
|---|---|
| llm-platform import ts-lab 代码 | ❌ **不做** —— 域不同（llm-platform 是通用 OpenAI 网关，不解析 LLM 输出） |
| llm-platform 内嵌 robust_parser / guided_json | ❌ **不做** —— 是客户端的事；网关无状态代理是定位 |
| llm-platform 增加"开关"启用稳定性增强 | 🟡 **晚一步** —— 先验 Layer A 透传完整，再看是否真有需求 |
| llm-platform 透传 `extra_body.guided_json` / `tools` / `response_format` | ✅ **必须验证** —— 写集成测试确认默认透传无丢字段 |

**对 ts-lab 的指导意义**：
- ts-lab `guided_json` technique 的入口是 ts-platform Issue 1（不是 llm-platform）—— 路径已明确
- 未来 RC-10 沉淀时，沉到 ts-platform 而不是 llm-platform
- 不要尝试把 robust_parser 抽成跨仓库共享 package（**0 LoC 真实现，premature extraction**）；等 ≥ 2 个真消费者再说

## 新增 #45（Function Calling 评估，低优先）

- [ ] **#45** 评估 Function Calling 作为第 8 种 technique（vs guided_json 对照实验）
  - **何时做**：guided_json technique 跑通且有 baseline 数据后
  - **依赖**：vLLM tools API 支持（0.6+ 已稳定）+ Qwen-VL 是否支持 tool calling 待核（推测弱）
  - **成功判据**：tool_calls 路径 vs guided_json 路径在同 50 样本上的 parse_success_rate / F1 差异
  - **不做的情况**：guided_json 已把 parse_success_rate 打到 99.9%+ → FC 边际收益太小，不值
  - **写入位置**：未来加 `techniques/vl_self_refinement/function_calling.py`

---

# 📌 本次会话关键发现（2026-04-26）

> 本节记录 2026-04-26 会话中颠覆性发现，影响 Track A/C 走向。详细决策记录见 `~/.claude/projects/-home-dff652-my-project/memory/`。

## 重大语境变更

- **同一人维护 ts-lab 与 ts-platform** —— Track C 原"提 issue 等平台团队合并"流程作废；三个 issue 草稿现作 ts-platform 改动的设计 spec，直接实装。
- **ts-platform 在私有 Atlassian 栈**：Bitbucket Server 5.1.4 @ `http://192.168.199.94:7990/projects/IAILP/repos/ts-platform/browse` + Jira 7.4.1 @ `:8080`（项目 key 待核实，未必是 IAILP）。`gh` CLI 不适用。
- **ts-lab 已推送到 GitHub** `https://github.com/dff652/ts-lab`（main 分支，2 个 commit：Day 1 骨架 `42eeae9` + 文档中文化 `401927f`）。
- **ts-lab/docs 全部统一中文**（11 份文件，commit `401927f`）。

## 草稿与现实出入（核查 ts-platform 真实代码后修正）

- `vllm_backend.py` 实际位于 `backend/app/adapters/vllm_backend.py`（107 行），**不在** `gpu_algorithms/` 子目录 —— 草稿（issue-1-response-format.md）路径误写
- **`vllm_client.py:303-339` 解析失败时已 graceful 返回** `VLLMResult(success=False, raw_text=raw_text, error_code=ERR_PARSE)`，**不是**草稿描述的 "hard error"。原始文本已被捕获在 `raw_text` 字段，仅缺持久化到 DB → **Issue 3 紧迫性大降**（见 #38 修订草稿）
- ts-platform `backend/tests/examples/client.py` 已存在 509 行 SDK 草稿（CLAUDE.md 称为"外部系统直接复制使用"）+ `backend/tests/example_api_usage.py` 390 行已跑通 → Track A #14 #15 #16 抽取工作有现成起点

## ts-platform 关键约束（来自 ts-platform/CLAUDE.md，影响后续实装）

- 字节/大小字段 ORM 必须 `BigInteger`（Issue 3 若加字节计数字段需注意；`raw_model_output` 用 `Text` 不影响）
- Alembic 删除 revision 必须同步改所有 `down_revision` 引用，否则 DAG `KeyError`
- 不删 git 分支
- 大文件（>5MB）不入 git，已配 pre-commit hook 拦截
- vLLM 0.17.1 + tensor-parallel-2 需要 `--disable-custom-all-reduce --enforce-eager` + `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False`
- ts-platform 已有 250+ pytest（`backend/tests/`，conftest 提供 `async_db / client / auth_headers` fixtures）

## 本机环境现状（影响 #2 pytest）

- Python 3.12.3 已装，但**无 pip / 无 venv / 无 conda**
- 装了 docker（无容器在跑）+ curl + wget + claude
- ts-platform 在本机也无 venv，开发可能在别处（容器 / 别的机器）
- ts-lab 跑 pytest（TODO #2）卡在 Python 环境 → 待决方案见 #35

## 待决问题（合并问 / 等用户拍板）

> **完整选项 / 推荐 / 连锁动作见 [docs/pending-decisions.md](docs/pending-decisions.md)**（2026-05-06 剥离）

| 编号 | 问题 | 选项（详见 pending-decisions.md） |
|---|---|---|
| **env** | Python 环境（TODO #35） | o1 uv / o2 apt / o3 docker / o4 跳过 |
| **e** | SDK 抽取路线（TODO #39） | e1 抽干净 package / e2 requests 薄壳 |
| **l** | RC-10 沉淀 SOP（TODO #37） | l1 全保留 / l2 砍成两步 / l3 折中（flag + 自测） |
| **j** | Jira 项目 key | 单人维护下不需 Jira，**已自动失效** |

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

- [x] **#1** 初次提交 ts-lab Day 1 骨架 + push 到 `origin/main`（commit `42eeae9`，43 文件 / 2054 行；远程 `https://github.com/dff652/ts-lab`）
- [~] **#2** 创建 venv，`pip install -e ".[dev]"`，运行 `pytest tests/ -v` 验证骨架 — **Blocked on**：本机无 pip/venv/conda → 见 #35

## Track C — ts-platform 改动（单人维护，直接实装，无需提 issue）

- [x] **#3** 起草 3 个 ts-platform issue（按 RC-7 规格）→ 已完成于 [docs/track-c/](docs/track-c/)
- [~] **#4** ~~提交 3 个 issue 到 ts-platform 仓库~~ → **改为**：直接实装 3 个 ts-platform 改动（草稿作设计 spec 用）
  - **#4.1** Issue 1 实装 → 见 #36（半天，最高优先）
  - **#4.2** Issue 2 实装（渲染图回传，半天）
  - **#4.3** Issue 3 实装（`raw_model_output` DB 列，1-2 小时；**紧迫性已降**，因 vllm_client 已 graceful 失败 + 草稿待修订 #38）
- [x] **#5** ~~与平台团队同步会议~~ → **作废**（单人维护，无需）

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

- [ ] **#14** 阅读 `ts-platform/backend/tests/example_api_usage.py`（390 行，已跑通）+ `tests/integration/`，规划 `backend/client/` 抽取边界。**起点已存在**：`backend/tests/examples/client.py`（509 行 SDK 草稿，CLAUDE.md 称"外部系统直接复制使用"）—— 抽取本质是把这份从 examples/ 提升为正式 package + 拆模块（auth/inference/data_pool/comparisons/results）
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

- [~] **#23** 实现 `robust_parser.py` 5 级 fallback 链（按 RC-6，最高优先零依赖）—— Tier 1-4 已实装 + 29 个单元测试覆盖；Tier 5 框架就绪（`llm_rewrite_fn` 注入点 + 异常处理 + 测试），等 baseline runner 提供 ts-platform client SDK 后注入真实 LLM call。新增 `ParseFailure` 显式异常符合工程原则 1（不返回空 list 假装"成功无异常"）。bug 发现：`_normalize_to_intervals` 对裸 list 输入需要至少 1 项可归一化才算成功，否则散文输入"Anomalies at [50, 60]"会被 tier 2 误判为空成功而不降级到 tier 4 正则抽取（已修）
- [ ] **#24** 跑 robust_parser benchmark，写实验报告
- [ ] **#25** 实现 `guided_json.py`（**Blocked on**: Track C Issue 1 合并），跑 benchmark + 写报告
- [ ] **#26** 实现 `self_consistency.py` 含 N=5 IoU 投票，跑 benchmark + 写报告
- [ ] **#27** 实现 `self_critique.py` 含保守再审 prompt，跑 benchmark + 写报告
- [ ] **#28** 实现 `format_locking.py` 含 few-shot 例子，跑 benchmark + 写报告
- [ ] **#29** 实现 `chain_of_zoom.py`（**Blocked on**: Track C Issue 2 合并），跑 benchmark + 写报告
- [ ] **#29b** 实现 `token_budget.py` 自适应 max_tokens（消除 truncation 失败），跑 benchmark + 写报告
- [ ] **#30** 组合消融：堆叠胜出 technique，画 cost-F1 帕累托前沿

## 本次会话新增（2026-04-26）

- [~] **#35** 解决 ts-lab Python 环境（**待用户拍板**，详见 §"待决问题"的 env）
  - o1：curl 装 `uv` 到 `~/.local/bin`（无需 sudo，单二进制，推荐）
  - o2：`sudo apt install python3.12-venv python3-pip`（标准 Debian 路线）
  - o3：用 docker（需指定 image）
  - o4：跳过 pytest #2 直接进 #36（pytest 仅测 import + iou 函数，ceremony 含量极高）
- [ ] **#36** 实装 Issue 1 —— `response_format` 透传到 ts-platform（**最高优先，半天**）
  - 设计 spec：[docs/track-c/issue-1-response-format.md](docs/track-c/issue-1-response-format.md)（路径已纠正：`vllm_backend.py` 在 `adapters/` 下，**不在** `gpu_algorithms/`）
  - **Step 1**（10 min）读 5 文件：`adapters/vllm_backend.py`(107 行) + `adapters/vllm_client.py` payload 段 + `adapters/gpu_algorithms/qwen.py` + `api/inference_external.py` + `schemas/inference_service.py`
  - **Step 2**（30 min）改 10-20 行：vllm_client.py payload 加 `extra_body={"guided_json": schema}`；其余 4 文件参数透传 + Pydantic schema 加 `response_format: dict | None = None`
  - **Step 3**（20 min）加集成测试到 `backend/tests/integration/`：用 ts-lab `ANOMALY_SCHEMA` 提交推理任务，校验输出 100% 合法 JSON
  - **Step 4**（auto）跑 ts-platform 现有 250+ 测试确认零回归
  - 完成后回 ts-lab 把 [techniques/vl_self_refinement/guided_json.py](techniques/vl_self_refinement/guided_json.py) 的 `NotImplementedError` 实装掉
- [ ] **#37** 决策 RC-10 沉淀 SOP（**待用户拍板** l1/l2/l3，详见 §"待决问题"）
- [x] **#38** 修订 [docs/track-c/issue-3-raw-output.md](docs/track-c/issue-3-raw-output.md) 背景段 —— 已加注 2026-04-26 核查结论："vllm_client 已 graceful 失败，原始文本已捕获在 raw_text 字段，仅缺持久化到 DB + API 暴露"
- [ ] **#39** 决策 SDK 抽取路线（**待用户拍板** e1/e2，详见 §"待决问题"）

## 本次复审新增（2026-05-07，详见 §Code Review 2026-05-07）

- [ ] **#40** 拍板 [docs/pending-decisions.md](docs/pending-decisions.md) 三项（env / SDK / SOP），按推荐 o1 + e2 + l2 执行连锁动作
- [ ] **#41** 新建 `techniques/types.py`：`TimeSeriesInput` / `AnomalyInterval` / `Technique` Protocol，统一 8 个 technique 的 contract
- [ ] **#42** 加 LICENSE（github.com/dff652/ts-lab 是公开仓，缺 LICENSE 是 hygiene 问题）
- [ ] **#43** 重审 `pyproject.toml` 依赖：每条加注释说明给哪个 technique 用，或暂删未用条目（参考 llm-platform 同日清 ts-platform 死依赖的判断标准）
- [ ] **#44** README.md 「Development Status (2026-04-26)」日期改为 `see TODO.md` 或脚本生成，避免每次同步

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
- 2026-04-26 #1 ✅ 初次提交 ts-lab Day 1 骨架 + push 到 origin/main（commit 42eeae9，43 文件 / 2054 行；远程 `https://github.com/dff652/ts-lab`）
- 2026-04-26 docs 11 份全部转中文 + Track C/README 反映单人维护现实（commit 401927f）
- 2026-04-26 ts-platform 真实状况核查：`vllm_backend.py` 路径修正、`vllm_client.py` 已 graceful 失败（Issue 3 紧迫性降）、`backend/tests/examples/client.py` 是 SDK 半成品（509 行）
- 2026-04-26 #5 ~~平台同步会议~~ 作废（单人维护，无需）
- 2026-04-26 Track C 流程从"提 issue 等合并"改为"直接实装 ts-platform 改动"
- 2026-04-26 #38 修订 issue-3 背景段 + README.md 状态表更新（C 项从"not filed"改为"spec ready, urgency reduced"）
- 2026-05-06 待决问题（env / e / l）剥离到 [docs/pending-decisions.md](docs/pending-decisions.md)，每项给出推荐 + 拍板后连锁动作
- 2026-05-07 11 天空窗：Day 1 三轨除已记录条目外无实质推进；llm-platform 那边推进了一轮 silent-swallow 普查 + 工程原则文档化（[../llm-platform/docs/engineering-principles.md](../llm-platform/docs/engineering-principles.md)），其方法论可反哺本项目（详见下方 §Code Review 2026-05-07）
- 2026-05-07 增补 §Code Review 2026-05-07 节（来自 llm-platform session 间隙的 ts-lab 复审）+ 4 个新 TODO 项（#40-#43）+ #2 #14-16 #35 #36 #39 状态实际未变，仍待 pending-decisions 拍板
- 2026-05-07 #23 robust_parser Tier 1-4 实装 + 29 单元测试通过；Tier 5 框架就绪；env 走 o2 路线（apt 装 python3-pip + python3-venv，重建 .venv），#35 隐式按 o2 推进。bug 修：tier 2 在散文输入上的空 list 误判（详见 commit）

---

# 📚 Cross-Reference

## ts-lab 内部
- [README.md](README.md) — 项目入口
- 远程仓库 https://github.com/dff652/ts-lab
- [docs/golden-dataset.md](docs/golden-dataset.md) — 数据集规范（中文）
- [docs/annotation-spec.md](docs/annotation-spec.md) — 标注规范（中文）
- [docs/benchmark-methodology.md](docs/benchmark-methodology.md) — F1 定义权威文档（中文）
- [docs/reproducibility.md](docs/reproducibility.md) — 复现 SOP（中文）
- [docs/experiments/template.md](docs/experiments/template.md) — 实验报告模板（中文）
- [docs/track-c/](docs/track-c/) — ts-platform 改动设计 spec（3 份，已转单人维护视角）
- [docs/pending-decisions.md](docs/pending-decisions.md) — 待决问题清单（env / SDK / SOP，2026-05-06）

## ts-platform（治理 / 设计决策）
- [design-vl-self-refinement.md](../ts-platform/docs/design-vl-self-refinement.md) — 主设计 ⭐
- [session-2026-04-25.md](../ts-platform/docs/session-2026-04-25.md) — 完整讨论档案（八轮）
- [design-agent-layer.md](../ts-platform/docs/design-agent-layer.md) — 历史方案（已弃用）
