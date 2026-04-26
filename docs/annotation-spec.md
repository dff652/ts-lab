# Annotation Specification

> **Status**: TODO — finalize after Track B Day 2 (path A/B/C decision).

## What Counts as Anomaly

(To be filled after pilot trial annotation.)

**Anomaly types** (preliminary):
- `spike` — sudden outlier point/short cluster
- `dip` — sudden downward outlier
- `drift` — gradual shift
- `level_change` — step-like jump to new baseline
- `pattern_break` — periodic pattern violation
- `flatline` — sensor stuck (constant over duration)

## Boundary Rules

- Start = first abnormal point
- End = last abnormal point + 1 (Python slice convention, e.g., `[120, 145]` includes index 144 not 145)
- For drifts, mark inflection-to-recovery range
- Margin tolerance: ±2 points (factored into IoU evaluation)

## Confidence Scale

| Level | Score | When to use |
|---|---|---|
| Certain | 1.0 | Obviously abnormal, would alert in production |
| Likely | 0.7 | Probably abnormal, would alert with low priority |
| Borderline | 0.5 | Could go either way; mostly used in critique experiments |

## Examples (TODO)

10 worked examples (positive + edge cases) to be added after pilot.

## Quality Gate

Before batch annotation:
- 2 annotators independently label same 30 samples
- Compute Cohen's kappa via `benchmarks/scripts/kappa_calc.py`
- **kappa < 0.6**: regroup, refine spec, retry
- **kappa 0.6-0.7**: proceed with risk note
- **kappa >= 0.7**: proceed with confidence
