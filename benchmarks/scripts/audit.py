"""Data audit: answer 7 questions about ts-platform data assets.

See ts-platform/docs/design-vl-self-refinement.md §15.4.

Q1: How many series in data_pool?
Q2: How many results have non-null label? Format?
Q3: data_type distribution?
Q4: Length distribution (min/median/max)?
Q5: Which were inferred by Qwen-VL? raw_output retained?
Q6: Negative (no-anomaly) samples count?
Q7: Source provenance (public dataset overlap risk)?

Output: ../golden_dataset/audit/data-audit-YYYY-MM-DD.md

This is the GO/NO-GO checkpoint for the project.
Without this, all subsequent work is speculation.

Usage:
    python -m benchmarks.scripts.audit

Status: TODO — implement using either ts-platform/backend/client SDK
        (after Track A) or direct DB connection.
"""
from datetime import date
from pathlib import Path

AUDIT_OUT = Path(__file__).parent.parent / "golden_dataset" / "audit"


def main():
    """Run audit and write markdown report."""
    today = date.today().isoformat()
    output = AUDIT_OUT / f"data-audit-{today}.md"
    raise NotImplementedError(
        f"TODO: Implement and write {output}\n"
        "Two paths:\n"
        "  1. Wait for backend/client SDK (Track A) — clean approach\n"
        "  2. Direct SQL against ts-platform DB — faster start\n"
        "Recommendation: path 2 for Day 1 speed."
    )


def q1_data_pool_size() -> int:
    """Q1: How many series in data_pool?"""
    raise NotImplementedError("TODO")


def q2_label_status() -> dict:
    """Q2: How many results have non-null label? Sample formats."""
    raise NotImplementedError("TODO")


def q3_data_type_distribution() -> dict:
    """Q3: data_type distribution across samples."""
    raise NotImplementedError("TODO")


def q4_length_distribution() -> dict:
    """Q4: min/median/max series length."""
    raise NotImplementedError("TODO")


def q5_qwen_inference_history() -> dict:
    """Q5: Qwen-VL inference count + raw_output retention."""
    raise NotImplementedError("TODO")


def q6_negative_samples() -> int:
    """Q6: Count of confirmed no-anomaly samples."""
    raise NotImplementedError("TODO")


def q7_provenance() -> dict:
    """Q7: Source breakdown + public dataset overlap risk."""
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    main()
