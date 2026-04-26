# Issue 2: Expose rendered chart image in inference response

**Suggested labels**: `enhancement`, `priority:medium`, `blocks:ts-lab`, `area:inference`
**Suggested milestone**: ts-lab Phase 3 (Day 21)
**Estimated effort**: ~30 lines + test

---

## Background

The ts-lab `chain_of_zoom` technique implements a two-pass detection strategy:
1. Round 1: full-image inference produces candidate anomaly intervals
2. Round 2: for each candidate, render a higher-DPI zoomed crop, ask Qwen-VL to confirm

For Round 2 to crop correctly, the lab needs to know **the exact image that was rendered in Round 1** — including:
- Final pixel dimensions after vision_patch_size alignment ([qwen.py:551-566](../../../ts-platform/backend/app/algorithms/pipeline.py))
- Subprocess Python 3.11 floating-point quirks ([render_subprocess.py](../../../ts-platform/backend/app/algorithms/render_subprocess.py))
- Layout mode (`tight` vs `fill`)

Re-rendering from raw data may produce a 2-pixel-different image, causing coordinate misalignment.

## Required Change

Add an optional flag to inference API that returns the rendered image alongside detection results.

### Affected files

| File | Change |
|---|---|
| `backend/app/adapters/gpu_algorithms/qwen.py` | Optionally return `rendered_image` from `render_timeseries_image()` |
| `backend/app/api/inference_external.py` | Accept `return_rendered_image: bool = False` request param |
| Response schema | Add optional `rendered_image_b64: str` field |

### Behavior

- **When `return_rendered_image=True`**: response payload includes `rendered_image_b64` containing exact image fed to Qwen-VL (PNG, base64-encoded)
- **When omitted (default)**: response unchanged, no payload size impact

## Acceptance Criteria

- [ ] API accepts `return_rendered_image` parameter
- [ ] When true, response includes `rendered_image_b64` field with valid base64 PNG
- [ ] Decoded image dimensions match what vLLM actually saw (post vision_patch_size alignment)
- [ ] When false (default), response payload size unchanged from current
- [ ] Integration test: submit task with flag → decode response image → verify dimensions match `figsize × dpi` rounded to alignment factor
- [ ] Documentation note about payload size implication (typically 50-200 KB per response)

## Implementation Hints

```python
# qwen.py sketch
def render_timeseries_image(data, ..., return_image=False):
    img = ...  # existing PIL.Image
    if return_image:
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return img, base64.b64encode(buf.getvalue()).decode("ascii")
    return img, None
```

For payload size, consider:
- WebP at quality 95 instead of PNG (smaller, lossless-ish for charts)
- Optional gzip compression
- Don't store in DB (transient response only)

## Lab Dependency

- **Blocks**: `ts-lab/techniques/vl_self_refinement/chain_of_zoom.py`
- **Required by**: Day 21 (to keep ts-lab Phase 3 on schedule)
- **Without it**: chain_of_zoom can fall back to re-rendering, but coordinate drift means F1 estimates are noisy and not directly comparable to baseline

## Out of Scope

- Streaming image returns
- Multiple resolutions (return only the rendered one; lab does its own zoom rendering for Round 2)
- Image caching / dedup (each task already produces a unique render)

## References

- [design-vl-self-refinement.md §3.4 chain-of-zoom](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md 附录 A.4 渲染细节](../../../ts-platform/docs/design-vl-self-refinement.md)
