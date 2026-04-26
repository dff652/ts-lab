"""Inter-annotator agreement calculation (Cohen's kappa).

For pilot, 2 annotators independently label 30 samples; kappa must >0.7
before batch annotation begins.

See ts-platform/docs/design-vl-self-refinement.md §16.4.
"""


def segment_kappa(
    annotator_a: list[list[dict]],
    annotator_b: list[list[dict]],
    iou_threshold: float = 0.5,
) -> float:
    """Cohen's kappa on segment-level agreement.

    Two intervals "agree" if IoU >= threshold.

    Args:
        annotator_a: List of [intervals_per_sample] for annotator A.
        annotator_b: Same shape for annotator B.
        iou_threshold: IoU threshold for considering intervals as same.

    Returns:
        Cohen's kappa score in [-1, 1]. Target >= 0.7.
    """
    raise NotImplementedError("TODO — use sklearn.metrics.cohen_kappa_score")


def write_kappa_report(score: float, output_path) -> None:
    """Write kappa-report.json with score + raw counts."""
    raise NotImplementedError("TODO")
