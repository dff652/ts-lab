# Golden Dataset Specification

> **Status**: TODO — populate after Track B Day 1 audit.

## Schema

(See `benchmarks/golden_dataset/README.md` for layout.)

## Version History

| Version | Samples | Created | Annotators | kappa | Source |
|---|---|---|---|---|---|
| v0-audit | - | - | - | - | - |
| v1-pilot | 50 | TBD | TBD | TBD | TBD |

## Update Policy

1. Bump version on any annotation change (additive or modify)
2. Recompute manifest hash after every change
3. Old versions kept for reproducibility (in git history; large versions in DVC)
4. Each benchmark run records the dataset version used

## Distribution Targets

For pilot v1 (50 samples):

| Dimension | Target | Rationale |
|---|---|---|
| step | ~12 | balanced data_type |
| noisy | ~13 | balanced data_type |
| constant | ~12 | balanced data_type |
| continuous | ~13 | balanced data_type |
| sparse density (1-2 anomalies) | ~17 | balanced |
| medium density (3-5) | ~17 | balanced |
| dense density (>10) | ~16 | balanced |
| short length (<500) | ~17 | balanced |
| medium (500-5000) | ~17 | balanced |
| long (>5000) | ~16 | balanced |
| **negative samples (no anomaly)** | **5-10** | **FP detection** |
