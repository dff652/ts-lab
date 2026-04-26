"""Token-Budget self-adaptive max_tokens.

See ts-platform/docs/design-vl-self-refinement.md §3.7.

Problem: ts-platform default max_tokens=512 gets truncated when many anomalies
are present, causing finish_reason="length" → vllm_client.py:303 returns error
→ task fails completely.

Solution: predict required token budget from data features (length, density
proxy, data_type), set max_tokens accordingly before calling Qwen-VL.

Heuristic mapping:
  - short series (<500 points), constant/step → 256
  - medium series, sparse anomalies expected → 512 (default)
  - medium series, dense → 1024
  - long series, dense → 2048
  - any time grounding mode is used → +50% for bbox coordinates

Priority: 🟢 incremental (predicted F1 +0~1%, but eliminates truncation failures).
Status: TODO — implement after baseline.
"""
from typing import Any


def predict_budget(
    series_length: int,
    data_type: str,
    inference_mode: str = "text",
) -> int:
    """Predict required max_tokens for this sample.

    Args:
        series_length: Number of points in time series.
        data_type: One of "step", "noisy", "constant", "continuous".
        inference_mode: "text" or "grounding".

    Returns:
        Suggested max_tokens value.
    """
    raise NotImplementedError("TODO")


def detect(data: Any, params: dict | None = None) -> list[dict]:
    """Detection with adaptive token budget."""
    raise NotImplementedError("TODO — depends on baseline")
