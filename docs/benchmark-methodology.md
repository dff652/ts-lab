# Benchmark Methodology

> **Status**: TODO — finalize before first baseline run.

This document is **authoritative for F1 definitions**. Code in `eval/metrics.py` must match.

## Metrics

### Primary: Range-based F1 (Tatbul 2018, simplified)

For each predicted interval `p`:
- TP if exists ground-truth `g` with `IoU(p, g) >= threshold`
- FP otherwise

For each ground-truth interval `g`:
- TP if exists predicted `p` with `IoU(p, g) >= threshold`
- FN otherwise

Report at **two thresholds**: 0.3 (lenient) and 0.5 (strict).

### Secondary: Point-level F1

Each timestamp `t` is binary (anomaly / normal). Standard precision/recall/F1.

Report this for fine-grained comparison. Sensitive to boundary precision.

### Tertiary: Mean IoU

For matched (TP) intervals only. Indicates boundary quality.

## Reporting Requirements

Every experiment report must include:

| Metric | Reason |
|---|---|
| Range F1 @ IoU=0.3 | Lenient view |
| Range F1 @ IoU=0.5 | Strict view |
| Point F1 | Fine-grained |
| Mean IoU (TP only) | Boundary quality |
| Per-data_type breakdown | Catch local positives |

## Statistical Significance

**Mandatory** for any "+technique" claim:

1. **Paired difference**: each sample contributes (technique_F1 − baseline_F1)
2. **Bootstrap CI**: 1000 resamples, 95% CI
3. **McNemar's test**: on TP/non-TP outcomes per sample
4. **Reject claim if 95% CI crosses zero**

## Sample Size

To detect F1 +3% improvement at 80% power:
- Approximately 300 paired samples
- Pilot 50 is **insufficient for power**, only for direction-finding
- Alpha 200 enables single-technique tests
- Beta 500 enables combination ablations

## Stratification

Always report **per-data_type** in addition to overall. A technique improving overall but hurting one stratum is often a wrong choice.

## Holdout

Reserve 20% of golden dataset as **final holdout** — not used during technique development. Only touch at end-of-phase validation.

## Reproducibility

Every reported number must come with:
- Code commit SHA
- Dataset version + manifest hash
- Random seeds (model + sampling)
- vLLM / Qwen-VL checkpoint version

See `reproducibility.md`.
