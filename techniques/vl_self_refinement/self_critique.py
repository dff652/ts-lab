"""Self-Critique: second-pass review of own output.

See ts-platform/docs/design-vl-self-refinement.md §3.5.

Round 1: detect anomalies normally.
Round 2: feed result back, ask "for each interval: KEEP / REMOVE / REVISE [s, e]?".

Reference: Madaan et al. 2023, "Self-Refine: Iterative Refinement with Self-Feedback".

Priority: 🟡 medium. Predicted F1 +2~5%.
Caveat: must emphasize "be conservative" or model over-revises.
"""
from typing import Any


def detect(data: Any, params: dict | None = None) -> list[dict]:
    """Two-pass detection with self-critique."""
    raise NotImplementedError("TODO — depends on baseline + robust_parser")


def _build_critique_prompt(initial_result: list[dict]) -> str:
    """Build prompt that lists initial intervals and asks KEEP/REMOVE/REVISE.

    Must include explicit 'be conservative' instruction.
    """
    raise NotImplementedError("TODO")


def _apply_critique(initial: list[dict], critique: list[dict]) -> list[dict]:
    """Merge critique decisions into final output."""
    raise NotImplementedError("TODO")
