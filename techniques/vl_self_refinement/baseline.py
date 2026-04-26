"""Baseline: single-pass Qwen-VL inference, no enhancement.

Reference implementation for benchmark comparison.
See ts-platform/docs/design-vl-self-refinement.md.

Status: TODO — implement after backend/client SDK is extracted (Track A).
"""
from typing import Any


def detect(data: Any, params: dict | None = None) -> list[dict]:
    """Run single-pass Qwen-VL detection.

    Args:
        data: Time series data (format defined by ts-platform client SDK).
        params: Override parameters (prompt, dpi, max_tokens, etc.).

    Returns:
        List of {"interval": [s, e], "type": str, "reason": str}.
    """
    raise NotImplementedError("Pending backend/client SDK extraction (Track A)")
