"""Coverage check for golden dataset.

Verify selected samples meet diversity targets:
- data_type distribution within tolerance
- density / length distribution within tolerance
- negative sample count >= 5
"""


def check_coverage(samples: list[dict], targets: dict) -> dict:
    """Check if dataset meets coverage targets.

    Returns:
        Dict with per-dimension status (ok / under / over) + suggestions.
    """
    raise NotImplementedError("TODO")
