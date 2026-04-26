# Track C —— ts-platform 改动设计稿

> **状态说明**：ts-lab 与 ts-platform 由同一人维护，本目录的三份草稿现作为 **ts-platform 改动的设计 spec** 使用，**无需走 issue tracker**。
> 草稿原是按"另一团队提 issue"的语气写的（含 labels / milestone 等字段），保留以备未来扩团队时复用。

## 文档清单

| # | 标题 | 优先级 | Lab 依赖 | 文件 |
|---|---|---|---|---|
| 1 | 给 vLLM 后端加 `response_format` 透传 | 🔴 最高 | guided_json | [issue-1-response-format.md](issue-1-response-format.md) |
| 2 | 在推理响应中暴露渲染后图像 | 🟡 中 | chain_of_zoom | [issue-2-rendered-image.md](issue-2-rendered-image.md) |
| 3 | 持久化并暴露原始 VL 输出 | 🟡 中 | robust_parser Tier 5 + self_critique | [issue-3-raw-output.md](issue-3-raw-output.md) |

## 工作流（单人维护现实版）

1. 在此 review、修订设计稿
2. 直接在 ts-platform 实现（按草稿"必需改动 / 验收标准 / 实现指引"逐项落地）
3. ts-platform 上跑测试 + commit + push
4. 回到 ts-lab，把 [TODO.md](../../TODO.md) 中对应 technique 的 `Blocked on` 注释去掉

## 工作量（同人维护下）

| Issue | 估时 | 解锁 |
|---|---|---|
| 1 | ~半天（10-20 行 + 集成测试） | guided_json |
| 2 | ~半天（30 行 + 测试） | chain_of_zoom |
| 3 | 1-2 小时（Alembic migration + 50 行） | robust_parser Tier 5 + self_critique |

## 设计来源

派生自 `ts-platform/docs/design-vl-self-refinement.md`：
- §11.2 ts-platform 必须配合的改动
- §15.6 Track C Day 1 —— 三个 ts-platform 改动

需要扩展但不阻塞 lab 的次要改动，参见 [TODO.md](../../TODO.md) #5a-#5e。
