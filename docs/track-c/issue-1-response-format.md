# Issue 1：给 vLLM 后端加 `response_format` 透传

**建议 labels**：`enhancement`, `priority:high`, `blocks:ts-lab`, `area:inference`
**建议 milestone**：ts-lab Phase 2（Day 14）
**预计工作量**：10–20 行代码 + 一个集成测试

---

## 背景

ts-lab 项目（Qwen-VL Self-Refinement Harness）正在 ts-platform 之上实现推理时增强技术。第一个技术 `guided_json` 需要 Qwen-VL 输出符合 JSON Schema 的强约束。

vLLM 原生通过 `extra_body.guided_json` 参数支持此特性（[vLLM 文档](https://docs.vllm.ai/en/latest/usage/structured_outputs.html)）。当前 ts-platform 的 vLLM 适配层未对 API 调用方暴露此参数。

**影响**：没有此改动，Qwen-VL 输出的 JSON 解析失败率维持在 ~5%，且 `vllm_client.py:303-330` 在 `finish_reason != "stop"` 时直接 hard error。改动后解析失败率可降至 <0.1%。

## 必需改动

新增可选 `response_format` 参数，从 API 请求 → vLLM `extra_body.guided_json`。

### 涉及文件

| 文件 | 改动 |
|---|---|
| `backend/app/adapters/gpu_algorithms/vllm_backend.py` | 接收 `response_format` 参数，传给 vLLM 的 `extra_body={"guided_json": <schema>}` |
| `backend/app/adapters/gpu_algorithms/qwen.py` | 把参数透传下去 |
| `backend/app/api/inference_external.py` | 在请求 schema 中加 `response_format: dict \| None = None` 字段 |
| `backend/app/schemas/inference_service.py` | 更新 Pydantic 模型（如适用） |

### 行为

- **传入 `response_format` 时**：模型输出强制符合 schema；`finish_reason="stop"` 始终成立（不会因结构 token 截断）
- **不传时（默认）**：行为与当前完全一致，**完全向后兼容**

## 验收标准

- [ ] API 接受请求体中的 `response_format` 字段
- [ ] 传入 schema 时，输出 100% 解析为符合 schema 的合法 JSON
- [ ] 在 50 样本测试集上，传入 `response_format` 时解析成功率 ≥ 99.9%
- [ ] 不传 `response_format` 时，集成测试无需修改即通过（向后兼容）
- [ ] API 文档 / OpenAPI spec 更新
- [ ] 至少加一个集成测试：用 `ANOMALY_SCHEMA` 提交任务并校验输出结构

## 实现指引

```python
# vLLM 适配层草图
def call_vllm(payload, ..., response_format: dict | None = None):
    extra_body = {}
    if response_format is not None:
        extra_body["guided_json"] = response_format
    if extra_body:
        payload["extra_body"] = extra_body
    ...
```

ts-lab 将传入的 schema：

```python
ANOMALY_SCHEMA = {
    "type": "object",
    "properties": {
        "detected_anomalies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "interval": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 2,
                        "maxItems": 2,
                    },
                    "type": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["interval", "type"],
            },
        }
    },
    "required": ["detected_anomalies"],
}
```

## Lab 依赖

- **阻塞**：`ts-lab/techniques/vl_self_refinement/guided_json.py`
- **要求合并时间**：Day 14（保证 ts-lab Phase 2 不延期）
- **若无此改动**：ts-lab 仍可推进 `robust_parser`（不依赖平台改动），但无法验证最高影响的稳定性技术

## 范围外

- Schema 校验 / 预检查（交给 vLLM 强制；信任调用方）
- 多种 schema 模式（仅 JSON；regex / grammar 之后再说）
- guided 生成开销的性能 benchmark

## 引用

- [design-vl-self-refinement.md §3.1](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md §11.2 —— ts-platform 配合改动](../../../ts-platform/docs/design-vl-self-refinement.md)
- vLLM structured outputs：<https://docs.vllm.ai/en/latest/usage/structured_outputs.html>
