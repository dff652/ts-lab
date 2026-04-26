"""guided_json schema enforcement (vLLM native).

See ts-platform/docs/design-vl-self-refinement.md §3.1.

Force model output to conform to JSON Schema via vLLM's guided_json.
Predicted to bring JSON parse failure rate from ~5% to <0.1%.

Priority: 🔴 highest impact on stability.
Blocked on ts-platform Issue 1 (response_format passthrough).
"""
from typing import Any

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


def detect(data: Any, params: dict | None = None) -> list[dict]:
    """Detection with JSON schema-enforced output."""
    raise NotImplementedError("TODO — blocked on ts-platform Issue 1")
