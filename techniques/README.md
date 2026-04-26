# Techniques

Inference-time enhancement techniques for Qwen-VL anomaly detection.

## Current Main Line: VL Self-Refinement

Located in `vl_self_refinement/`. Seven techniques, priority order:

| # | File | Status | Priority | Blocked on |
|---|---|---|---|---|
| 1 | `robust_parser.py` | TODO | 🔴 first | nothing |
| 2 | `guided_json.py` | TODO | 🔴 | ts-platform Issue 1 |
| 3 | `baseline.py` | TODO | 🔴 reference | backend/client SDK |
| 4 | `self_consistency.py` | TODO | 🟡 | baseline + parser |
| 5 | `chain_of_zoom.py` | TODO | 🟡 most promising | ts-platform Issue 2 |
| 6 | `self_critique.py` | TODO | 🟡 | baseline + parser |
| 7 | `format_locking.py` | TODO | 🟢 | nothing |
| 8 | `token_budget.py` | TODO | 🟢 | baseline |

## Standard Technique Interface

Every technique exposes:

```python
def detect(data, params: dict | None = None) -> list[dict]:
    """Run technique on time-series data.

    Returns: [{"interval": [s, e], "type": str, "reason": str}, ...]
    """
```

## Adding a New Technique

1. Create `techniques/<category>/<name>.py` following the standard interface
2. Add docstring referencing the design doc section
3. Run via `python -m benchmarks.run_benchmark --technique <name>`
4. Write report in `../docs/experiments/YYYY-MM-DD-<name>.md`
5. Only after benchmark validation, propose sinking back to ts-platform

## Notebooks vs Techniques

- **notebooks/**: throw-away exploration
- **techniques/**: production-quality, validated by benchmark, has tests

**Do NOT directly copy notebook code into techniques/** — rewrite it cleanly.
