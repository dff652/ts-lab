"""Benchmark runner: technique × golden dataset → metrics.

Usage:
    python -m benchmarks.run_benchmark --technique baseline --dataset v1-pilot

See ts-platform/docs/design-vl-self-refinement.md §10.

Output: eval/reports/<technique>-<dataset>-<timestamp>.{csv,md}

Status: TODO — depends on backend/client SDK + golden dataset.
"""
import argparse
from pathlib import Path

GOLDEN_ROOT = Path(__file__).parent / "golden_dataset"
REPORTS_ROOT = Path(__file__).parent.parent / "eval" / "reports"


def run(technique_name: str, dataset_version: str = "v1-pilot") -> dict:
    """Run one technique on dataset, return metrics summary.

    Args:
        technique_name: Module name under techniques/, e.g. "baseline".
        dataset_version: Subdir name under golden_dataset/.

    Returns:
        Dict with overall + per-data_type metrics.
    """
    raise NotImplementedError("TODO")


def _load_technique(name: str):
    """Dynamic import of techniques.<category>.<name>."""
    raise NotImplementedError("TODO")


def _load_dataset(version: str):
    """Load samples + ground-truth from golden_dataset/<version>/."""
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--technique", required=True, help="e.g. baseline, robust_parser")
    parser.add_argument("--dataset", default="v1-pilot")
    args = parser.parse_args()
    metrics = run(args.technique, args.dataset)
    print(metrics)
