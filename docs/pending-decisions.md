# 待决问题清单

> **登记日期**：2026-05-06
> **拍板日期**：2026-05-07
> **状态**：✅ 已拍板 `o2 + e2 + l2`（详见末尾 §历史）
> **关联 TODO**：#35（env）/ #37（RC-10 SOP）/ #39（SDK 路线）—— 全部已完成

---

## 决策 1 — Python 环境（TODO #35，阻塞 pytest #2）

**背景**：本机 Python 3.12.3 裸装，无 pip / venv / conda；docker 已装但无运行容器；ts-platform 在本机也无 venv（开发可能在容器或别的机器）。

| 选项 | 描述 | 优点 | 缺点 |
|---|---|---|---|
| **o1** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` 装 uv 到 `~/.local/bin` | 无需 sudo；单二进制；现代依赖管理；可同时管多 Python 版本 | 引入新工具栈 |
| **o2** | `sudo apt install python3.12-venv python3-pip` | 标准 Debian 路线；和系统包管理一致 | 需要 sudo |
| **o3** | docker 里跑（待指定 image） | 隔离彻底；和未来 CI 一致 | 启动慢；编辑体验差 |
| **o4** | 跳过 pytest #2，直接进 #36（Issue 1 实装） | 立刻有产出；pytest 仅测 import + iou 函数，ceremony 含量极高 | 后续 technique 实装时仍要补 |

**推荐**：**o1**（uv）—— 无 sudo、单二进制、未来管 pyproject 也省事。

---

## 决策 2 — SDK 抽取路线（TODO #39，阻塞 Track A baseline）

**背景**：`ts-platform/backend/tests/examples/client.py` 已有 509 行 SDK 草稿（CLAUDE.md 称"外部系统直接复制使用"），`example_api_usage.py` 390 行已跑通；ts-lab 的 baseline runner 阻塞在"用什么调 ts-platform API"。

| 选项 | 描述 | 工作量 | 长期质量 |
|---|---|---|---|
| **e1** | 把 examples/client.py 提升为正式 `ts-platform/backend/client/` package + 拆模块（auth / inference / data_pool / comparisons / results）+ 重构 `tests/` 改用 client | 2-3 天 | 干净、可复用、可发版 |
| **e2** | ts-lab 内先写 `requests` 薄壳（5-10 个函数），未来重写 | 半天 | 短期糙，重写时 sunk cost |

**推荐取舍**：
- 如果近期 baseline + 至少一个 technique 跑通是硬目标 → **e2**
- 如果允许花 2-3 天先把 client 搞干净 → **e1**

**默认建议 e2**：lab 阶段验证完技术再回头抽干净 SDK，避免提前投入在还没验证的 API surface 上。

---

## 决策 3 — RC-10 沉淀 SOP 是否保留（TODO #37）

**背景**：[TODO.md RC-10](../TODO.md) 定义了"lab → ts-platform 生产"6 步流程：benchmark 验证 → design doc → PR + feature flag → 影子模式 1 周 → canary 10% 1 周 → 全量；feature flag 保留 1 个月。单人维护下，影子 / canary / 1 个月 flag 这些步骤可能 ceremony 过重。

| 选项 | 描述 | 适用场景 |
|---|---|---|
| **l1** | 全保留 RC-10 六步 | 生产真有外部用户、回退成本高 |
| **l2** | 砍成"自测 → merge"两步 | 纯实验、用户即开发者、回退便宜 |
| **l3** | 折中：保留 feature flag + 自测 + 简化影子模式（只跑 diff 不限时） | 单人维护但生产仍有他人使用 |

**推荐**：取决于 ts-platform 当前是否有外部用户。
- 仅用户自己用 → **l2**
- 有他人在用 → **l3**（feature flag 是廉价保险）

---

## 决策模板（拍板时勾选）

```
环境：[ ] o1   [ ] o2   [ ] o3   [ ] o4
SDK ：[ ] e1   [ ] e2
SOP ：[ ] l1   [ ] l2   [ ] l3
```

拍板示例：`o1 + e2 + l3` —— 装 uv，ts-lab 写 requests 薄壳，沉淀走 feature flag + 自测 + 简化影子。

---

## 拍板后的连锁动作

| 决策结果 | 立即动作 |
|---|---|
| o1 | 跑 uv 安装命令 → `cd ts-lab && uv sync` → pytest 验收 |
| o2 | `sudo apt install python3.12-venv python3-pip` → 建 venv → `pip install -e ".[dev]"` |
| o3 | 选 image（推荐 `python:3.12-slim` 或 `ts-platform/docker/` 现有 image）→ 写 dev compose 段 |
| o4 | TODO #2 标 `[!]`，#36 立即启动 |
| e1 | TODO #14-16 立即启动；ts-platform 进入 SDK 抽取分支 |
| e2 | ts-lab 新建 `ts_lab/clients/ts_platform.py`（薄壳）；TODO #14-16 降优先到 baseline 跑通后 |
| l1 / l3 | TODO #31-34 保持当前措辞 |
| l2 | TODO #31-34 改写为两步流程，删除 #32 #33 |

---

## 历史

- 2026-05-06 创建本文档，从 [TODO.md](../TODO.md) §"待决问题"剥离出来作为独立可拍板单元
- 2026-05-07 ✅ **拍板 `o2 + e2 + l2`**：
  - **env = o2**（apt 装 `python3-pip` + `python3-venv`）—— 实际已在 llm-platform session 间隙隐式执行；本日 ts-lab 重建 `.venv` 并 `pip install pytest numpy`，34 项测试通过
  - **SDK = e2**（ts-lab 内 requests 薄壳）—— 避免 premature abstraction：lab 阶段先验证技术再回头抽干净 SDK；新建 [`clients/ts_platform.py`](../clients/ts_platform.py) 骨架；TODO #14-16（ts-platform `backend/client/` 抽取）降优先到 baseline 跑通后
  - **SOP = l2**（自测 + merge 两步）—— 单人维护无外部用户，影子 / canary / 1 个月 flag 是 ceremony；TODO #31-34 改写为「lab benchmark 验证 → 写 ts-platform integration design doc → PR + feature flag → merge」简化两步流程，删除 #32（影子模式）与 #33（canary 10%）
