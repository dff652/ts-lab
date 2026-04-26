"""Self-Consistency voting via multi-sample IoU clustering.

See ts-platform/docs/design-vl-self-refinement.md §3.3.

Sample N times with different seeds (or temperature variation),
cluster intervals by IoU, keep those appearing >= threshold times.

Reference: Wang et al. 2022, "Self-Consistency Improves Chain of Thought Reasoning".

Priority: 🟡 medium. Depends on baseline + robust_parser.
"""
from typing import Any


def detect(
    data: Any,
    params: dict | None = None,
    n_samples: int = 5,
    vote_threshold: int = 3,
    iou_threshold: float = 0.5,
) -> list[dict]:
    """Run N samples and IoU-vote.

    Args:
        n_samples: Number of independent samples (default 5).
        vote_threshold: Minimum vote count to keep interval (default 3/5).
        iou_threshold: IoU threshold for clustering (default 0.5).
    """
    raise NotImplementedError("TODO — depends on baseline + robust_parser")


def _iou_cluster(samples: list[list[dict]], iou_threshold: float) -> list[dict]:
    """Cluster intervals across samples by IoU, return vote counts."""
    raise NotImplementedError("TODO")
