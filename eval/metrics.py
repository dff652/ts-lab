"""Anomaly detection metrics: Point-level F1, Range-based F1, IoU.

See ts-platform/docs/design-vl-self-refinement.md §16.2.

Metrics defined:
- Point-level F1: each timestamp 0/1, classic binary F1
- Range-based F1 (Tatbul 2018): IoU-thresholded segment matching
- IoU: interval overlap-over-union

Authoritative definitions live in ts-lab/docs/benchmark-methodology.md.
DO NOT change definitions without updating that doc + re-running baseline.
"""
from typing import Sequence

Interval = tuple[int, int]


def iou(a: Interval, b: Interval) -> float:
    """IoU of two intervals [s, e] (e exclusive).

    >>> iou((0, 10), (5, 15))
    0.3333...
    >>> iou((0, 10), (10, 20))
    0.0
    >>> iou((0, 10), (0, 10))
    1.0
    """
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return inter / union if union > 0 else 0.0


def point_f1(
    pred: Sequence[Interval],
    gt: Sequence[Interval],
    length: int,
) -> dict:
    """Point-level precision / recall / F1.

    Args:
        pred: Predicted intervals.
        gt: Ground-truth intervals.
        length: Total length of the time series.

    Returns:
        {"precision": float, "recall": float, "f1": float, "tp": int, "fp": int, "fn": int}.
    """
    raise NotImplementedError("TODO")


def range_f1(
    pred: Sequence[Interval],
    gt: Sequence[Interval],
    iou_threshold: float = 0.5,
) -> dict:
    """Range-based F1 with IoU threshold (Tatbul 2018 simplified).

    A predicted interval is TP iff exists a GT interval with IoU >= threshold.
    """
    raise NotImplementedError("TODO")


def per_data_type(
    results: list[dict],
    metric_fn,
) -> dict[str, dict]:
    """Compute metric stratified by data_type for fine-grained analysis.

    Returns: {"step": {...metrics}, "noisy": {...}, ...}
    """
    raise NotImplementedError("TODO")
