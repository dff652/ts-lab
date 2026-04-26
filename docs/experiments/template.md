# experiment-YYYY-MM-DD-<technique>

## Setup

- **Model**: Qwen-VL-8B vX.Y.Z
- **Backend**: vLLM 0.17.1
- **Dataset**: golden-vN-stage (M samples)
- **Seeds**: model=42, sampling=42
- **Manifest hash**: `<sha256>`
- **Code commit**: `<git-sha>` (clean? Y/N)

## Question

What hypothesis does this experiment test?

> e.g.: "Self-Consistency with N=5 samples improves F1 on noisy data by reducing single-shot variance."

## Method

Brief description of what the technique does. Link to the technique file:
- Implementation: `techniques/vl_self_refinement/<name>.py`
- Design reference: ts-platform/docs/design-vl-self-refinement.md §X

## Result

### Overall

| Metric | Baseline | +<Technique> | Δ | 95% CI | p-value |
|---|---|---|---|---|---|
| F1 (Range, IoU=0.5) | | | | | |
| F1 (Range, IoU=0.3) | | | | | |
| F1 (Point) | | | | | |
| Precision | | | | | |
| Recall | | | | | |
| Mean IoU (TP) | | | | | |
| Latency P50 (s) | | | | | |
| Latency P99 (s) | | | | | |
| Token cost (mean) | | | | | |

### By data_type

| data_type | N | Baseline F1 | +<Technique> F1 | Δ |
|---|---|---|---|---|
| step | | | | |
| noisy | | | | |
| constant | | | | |
| continuous | | | | |

### Failure cases

Specific samples where technique hurt vs baseline:
- `series_NNN`: brief explanation
- `series_MMM`: brief explanation

## Conclusion

- **Headline**: one sentence summary
- **Where it helps**: which strata showed real gain
- **Where it hurts**: any negative strata or edge cases
- **Cost**: latency / token / GPU-hour overhead
- **Recommendation**:
  - [ ] Enable always
  - [ ] Enable per data_type: ...
  - [ ] Enable per priority tier: ...
  - [ ] Discard

## Next

Concrete follow-up experiments:
- [ ] Try variant with parameter X = ...
- [ ] Combine with technique Y
- [ ] Investigate failure case Z
