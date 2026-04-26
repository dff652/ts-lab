"""Few-shot prompt template for stable format compliance.

See ts-platform/docs/design-vl-self-refinement.md §3.6.

Inject 1-2 valid output examples into prompt to improve format adherence.
Cache-friendly (examples are stable).

Priority: 🟢 incremental. Predicted F1 +1~3%.
"""
from typing import Any

EXAMPLE_OUTPUT = {
    "detected_anomalies": [
        {
            "interval": [120, 145],
            "type": "spike",
            "reason": "Sudden upward jump exceeding normal range",
        }
    ]
}


def detect(data: Any, params: dict | None = None) -> list[dict]:
    """Detection with few-shot examples in prompt."""
    raise NotImplementedError("TODO")


def _build_prompt_with_examples(base_prompt: str, n_examples: int = 1) -> str:
    """Wrap base prompt with N example outputs for format priming."""
    raise NotImplementedError("TODO")
