"""Smoke tests: imports and basic skeleton sanity.

Goal: ensure all modules import cleanly. Implementation tests come later.
"""


def test_imports_techniques():
    """All technique modules import without error."""
    from techniques.vl_self_refinement import (  # noqa: F401
        baseline,
        chain_of_zoom,
        format_locking,
        guided_json,
        robust_parser,
        self_consistency,
        self_critique,
        token_budget,
    )


def test_imports_benchmarks():
    """Benchmark runner and scripts import."""
    from benchmarks import run_benchmark  # noqa: F401
    from benchmarks.scripts import (  # noqa: F401
        audit,
        coverage_check,
        kappa_calc,
        sample_selector,
    )


def test_imports_eval():
    """Eval modules import."""
    from eval import compare, metrics  # noqa: F401


def test_iou_basic():
    """IoU correctness — only metric implemented at skeleton stage."""
    from eval.metrics import iou

    assert iou((0, 10), (5, 15)) == 5 / 15
    assert iou((0, 10), (10, 20)) == 0.0
    assert iou((0, 10), (0, 10)) == 1.0
    assert iou((0, 10), (20, 30)) == 0.0
    assert iou((5, 15), (0, 10)) == 5 / 15  # symmetry


def test_guided_json_schema_shape():
    """ANOMALY_SCHEMA constant has expected structure."""
    from techniques.vl_self_refinement.guided_json import ANOMALY_SCHEMA

    assert ANOMALY_SCHEMA["type"] == "object"
    assert "detected_anomalies" in ANOMALY_SCHEMA["properties"]
    items = ANOMALY_SCHEMA["properties"]["detected_anomalies"]["items"]
    assert "interval" in items["properties"]
