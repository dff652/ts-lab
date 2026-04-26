# Issue 3：持久化并暴露原始 VL 输出

**建议 labels**：`enhancement`, `priority:medium`, `blocks:ts-lab`, `area:inference`, `area:database`
**建议 milestone**：ts-lab Phase 3（Day 21）
**预计工作量**：DB migration + ~50 行 + 测试

---

## 背景

ts-lab 多个技术需要拿到 Qwen-VL 的**原始文本输出**，而不只是解析后的结构化异常：

- **`robust_parser` Tier 5**：当 Tier 1-4 解析全失败时，lab 用「把这段重写为合法 JSON」的 prompt 再调一次 Qwen-VL，需要原始输出
- **`self_critique`**：把模型自己上一次的输出作为文本送回审查
- **一般研究**：理解模型「怎样输出畸形 JSON」有助于精炼 prompt

当前 `vllm_client.py:303-330` 在解析成功后丢弃原始文本，解析失败时直接 hard error。原始文本永远不会进入存储或 API。

## 必需改动

持久化原始模型输出，并通过 results API 对外暴露。

### 涉及文件

| 文件 | 改动 |
|---|---|
| `backend/app/models/result.py`（或对应文件） | 加 `raw_model_output: Optional[str]` 列 |
| `backend/migrations/<新>.py`（Alembic） | Migration：加列、默认 NULL、不回填 |
| `backend/app/adapters/gpu_algorithms/qwen.py` | 在解析前持久化原始输出（成功失败都持久化） |
| `backend/app/adapters/gpu_algorithms/vllm_client.py` | 解析失败时若已捕获原始文本，不要 hard error |
| `backend/app/api/results.py` | 结果查询响应包含 `raw_model_output` |
| `backend/app/schemas/result.py` | 更新 Pydantic 响应模型 |

### 存储策略

- 默认：完整存原始输出（典型 500-2000 字符；偶尔 >5KB）
- **截断 10KB**：防止恶意 / 病态输出撑爆 DB
- **不**建索引（仅按 result_id 查询）
- 存储成本分析：~10KB × N 任务 ≈ 当前规模可忽略

## 验收标准

- [ ] 通过 Alembic migration 加列；现有库可干净升级
- [ ] 每次 Qwen-VL 调用都存原始输出（成功 + 解析失败两种都存）
- [ ] 结果 API 返回 `raw_model_output` 字段（旧行允许 NULL）
- [ ] 输出超过 10KB 截断并标记
- [ ] 既有「解析成功」行为不变（原始字段是新增，不是替代）
- [ ] 既有「解析失败」行为变化：现在存原始 + 记录失败模式（不再 hard error）
- [ ] PR 描述含存储成本分析

## 实现指引

Migration 草图：

```python
# alembic/versions/<rev>_add_raw_model_output.py
def upgrade():
    op.add_column(
        "result",
        sa.Column("raw_model_output", sa.Text, nullable=True),
    )

def downgrade():
    op.drop_column("result", "raw_model_output")
```

适配层草图：

```python
# qwen.py
def call_qwen(...):
    raw = vllm_complete(...)  # 原始文本
    record_raw(task_id, raw[:10_000])  # 截断

    try:
        parsed = parse_qwen_output(raw)
    except ParseError as e:
        record_parse_failure(task_id, str(e))
        return None  # 不再 hard error
    return parsed
```

## Lab 依赖

- **阻塞**：`ts-lab/techniques/vl_self_refinement/robust_parser.py` Tier 5（LLM-rewrite fallback）
- **阻塞**：`ts-lab/techniques/vl_self_refinement/self_critique.py`（需要原始文本回灌）
- **要求合并时间**：Day 21（保证 ts-lab Phase 3 不延期）
- **若无此改动**：robust_parser 止步 Tier 4（regex fallback，有损）；self_critique 无法忠实实现

## Migration 风险

🟡 **中**：需 DB migration。需要 rollout 计划：
- Migration 在 deploy hook 中执行（无人工步骤）
- 旧代码路径继续工作（列允许 NULL）
- 回滚：直接 `DROP COLUMN`；对未使用方无数据损失

## 范围外

- 按原始输出内容查询（暂无需求；后续如需可加全文索引）
- 长期归档（当前短期保留即可）
- 隐私脱敏（原始输出不含用户 PII；只是数值序列渲染成的图）

## 引用

- [design-vl-self-refinement.md §3.2 robust parser](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md §3.5 self-critique](../../../ts-platform/docs/design-vl-self-refinement.md)
- 当前解析失败代码：`backend/app/adapters/gpu_algorithms/vllm_client.py:303-330`
