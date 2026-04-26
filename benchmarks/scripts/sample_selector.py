"""Stratified sampling for golden dataset construction.

Goal: pick 50 samples covering:
- 4 data_types (step / noisy / constant / continuous) ~12 each
- 3 anomaly densities (sparse / medium / dense) ~17 each
- 3 lengths (short / medium / long) ~17 each
- 5-10 negative (no-anomaly) samples for FP detection

See ts-platform/docs/design-vl-self-refinement.md §16.3.
"""
from typing import Any


def select_pilot(
    candidates: list[dict],
    target_size: int = 50,
    negative_target: int = 7,
) -> list[dict]:
    """Stratified-sample pilot dataset from audit candidate pool.

    Args:
        candidates: List of candidate samples with metadata.
        target_size: Target dataset size (default 50).
        negative_target: Number of no-anomaly samples (default 7).

    Returns:
        Selected samples with diversity guarantee.
    """
    raise NotImplementedError("TODO — depends on audit output")
