# Issue 1: Add `response_format` passthrough to vLLM backend

**Suggested labels**: `enhancement`, `priority:high`, `blocks:ts-lab`, `area:inference`
**Suggested milestone**: ts-lab Phase 2 (Day 14)
**Estimated effort**: 10–20 lines of code + integration test

---

## Background

The ts-lab project (Qwen-VL Self-Refinement Harness) is implementing inference-time enhancement techniques on top of ts-platform. The first technique — `guided_json` — requires JSON Schema-enforced output from Qwen-VL.

vLLM natively supports this via the `extra_body.guided_json` parameter ([vLLM docs](https://docs.vllm.ai/en/latest/usage/structured_outputs.html)). Currently ts-platform's vLLM adapter does not expose this parameter to API callers.

**Impact**: Without this change, JSON parse failure rate on Qwen-VL output remains around 5%, and `vllm_client.py:303-330` returns hard errors when `finish_reason != "stop"`. With it, parse failure can drop to <0.1%.

## Required Change

Add an optional `response_format` parameter that flows from API request → vLLM `extra_body.guided_json`.

### Affected files

| File | Change |
|---|---|
| `backend/app/adapters/gpu_algorithms/vllm_backend.py` | Accept `response_format` arg, pass to vLLM as `extra_body={"guided_json": <schema>}` |
| `backend/app/adapters/gpu_algorithms/qwen.py` | Thread parameter through |
| `backend/app/api/inference_external.py` | Add `response_format: dict \| None = None` field in request schema |
| `backend/app/schemas/inference_service.py` | Update Pydantic model (if applicable) |

### Behavior

- **When `response_format` provided**: model output guaranteed to conform to schema; `finish_reason="stop"` always (no length truncation of structural tokens)
- **When omitted (default)**: behavior identical to current — fully backward compatible

## Acceptance Criteria

- [ ] API accepts `response_format` field in inference request body
- [ ] When schema is provided, output 100% parses as valid JSON conforming to schema
- [ ] On a 50-sample test corpus, parse success rate ≥ 99.9% with `response_format` set
- [ ] When `response_format` is omitted, integration tests pass without modification (backward compat)
- [ ] Documentation updated in API docs / OpenAPI spec
- [ ] At least one integration test added that submits a task with `ANOMALY_SCHEMA` and verifies output structure

## Implementation Hints

```python
# vLLM adapter sketch
def call_vllm(payload, ..., response_format: dict | None = None):
    extra_body = {}
    if response_format is not None:
        extra_body["guided_json"] = response_format
    if extra_body:
        payload["extra_body"] = extra_body
    ...
```

The schema ts-lab will pass:

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

## Lab Dependency

- **Blocks**: `ts-lab/techniques/vl_self_refinement/guided_json.py`
- **Required by**: Day 14 (to keep ts-lab Phase 2 on schedule)
- **Without it**: ts-lab can still proceed with `robust_parser` (no platform change needed), but cannot validate the highest-impact stability technique

## Out of Scope

- Schema validation / pre-checking (let vLLM enforce; we trust caller)
- Multiple schema modes (JSON only for now; regex / grammar can come later)
- Performance benchmarking of guided generation overhead

## References

- [design-vl-self-refinement.md §3.1](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md §11.2 — ts-platform 配合改动](../../../ts-platform/docs/design-vl-self-refinement.md)
- vLLM structured outputs: <https://docs.vllm.ai/en/latest/usage/structured_outputs.html>
