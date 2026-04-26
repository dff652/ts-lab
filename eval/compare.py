"""Pairwise technique comparison with significance tests.

See ts-platform/docs/design-vl-self-refinement.md §10.3.

Methods:
- Paired Bootstrap: 1000 resamples for confidence interval
- McNemar's test: paired binary outcome (TP/non-TP per sample)

Critical: every reported delta must come with CI + p-value.
"None of these techniques are meaningful without proper statistics."
"""
import numpy as np


def paired_bootstrap(
    diffs: np.ndarray,
    n_iters: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Bootstrap confidence interval for paired difference.

    Args:
        diffs: Per-sample (technique - baseline) differences.
        n_iters: Bootstrap iterations.
        ci: Confidence level (e.g., 0.95).
        seed: Random seed for reproducibility.

    Returns:
        (mean, ci_lower, ci_upper)
    """
    raise NotImplementedError("TODO")


def mcnemar(b: int, c: int, continuity: bool = True) -> float:
    """McNemar's chi-square test, returns p-value.

    Args:
        b: Count of (technique=correct, baseline=wrong).
        c: Count of (technique=wrong, baseline=correct).
        continuity: Apply continuity correction (recommended for small N).

    Returns:
        Two-sided p-value.
    """
    raise NotImplementedError("TODO")


def comparison_table(
    baseline_results: list[dict],
    technique_results: list[dict],
) -> dict:
    """Build comparison table with mean / CI / p-value per metric."""
    raise NotImplementedError("TODO")
