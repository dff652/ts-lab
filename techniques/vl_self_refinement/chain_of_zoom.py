"""Chain-of-Zoom self-refinement: detect at full image, confirm at zoom.

See ts-platform/docs/design-vl-self-refinement.md §3.4.

Round 1: full image detection -> candidate intervals.
Round 2: for each candidate, render zoomed image, ask "real anomaly?".
Keep only confirmed candidates.

Solves two known weaknesses:
- Long sequences losing detail to downsampling
- Grounding mode mistakenly labeling large regions

Priority: 🟡 most promising (predicted F1 +5~15%) but most complex.
Blocked on ts-platform Issue 2 (rendered image exposure).

DO NOT START FIRST — depends on baseline + robust_parser + Issue 2.
"""
from typing import Any


def detect(
    data: Any,
    params: dict | None = None,
    zoom_margin: float = 0.1,
    zoom_dpi: int = 200,
    confirmation_threshold: float = 0.5,
) -> list[dict]:
    """Two-round zoom-based detection.

    Args:
        zoom_margin: Fraction of interval width to extend on each side.
        zoom_dpi: DPI for zoom render (typically higher than base).
        confirmation_threshold: Confidence threshold for "yes/no" judge.
    """
    raise NotImplementedError("TODO — blocked on ts-platform Issue 2")


def _render_zoom(data: Any, start: int, end: int, margin: float, dpi: int):
    """Render zoomed-in chart for a candidate interval."""
    raise NotImplementedError("TODO")


def _confirm(zoom_image, original_interval) -> tuple[bool, float]:
    """Ask Qwen-VL: is this segment really anomalous? Returns (verdict, confidence)."""
    raise NotImplementedError("TODO")
