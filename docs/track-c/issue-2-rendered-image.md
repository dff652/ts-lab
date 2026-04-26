# Issue 2：在推理响应中暴露渲染后图像

**建议 labels**：`enhancement`, `priority:medium`, `blocks:ts-lab`, `area:inference`
**建议 milestone**：ts-lab Phase 3（Day 21）
**预计工作量**：~30 行 + 测试

---

## 背景

ts-lab 的 `chain_of_zoom` 技术采用两轮检测：
1. Round 1：全图推理，产出候选异常区间
2. Round 2：对每个候选，渲染高 DPI 局部放大图，让 Qwen-VL 二次确认

要让 Round 2 截图正确，lab 必须知道 **Round 1 实际渲染的那张图** —— 包括：
- vision_patch_size 对齐后的最终像素尺寸（[qwen.py:551-566](../../../ts-platform/backend/app/algorithms/pipeline.py)）
- 子进程 Python 3.11 浮点怪行为（[render_subprocess.py](../../../ts-platform/backend/app/algorithms/render_subprocess.py)）
- 布局模式（`tight` vs `fill`）

从原始数据重新渲染可能产生 2 像素偏差，造成坐标错位。

## 必需改动

给推理 API 加可选 flag，与检测结果一并返回渲染图。

### 涉及文件

| 文件 | 改动 |
|---|---|
| `backend/app/adapters/gpu_algorithms/qwen.py` | `render_timeseries_image()` 可选返回 `rendered_image` |
| `backend/app/api/inference_external.py` | 接收请求参数 `return_rendered_image: bool = False` |
| 响应 schema | 增加可选字段 `rendered_image_b64: str` |

### 行为

- **传 `return_rendered_image=True` 时**：响应包含 `rendered_image_b64`，是真正喂给 Qwen-VL 的那张图（PNG，base64 编码）
- **不传时（默认）**：响应不变，载荷大小无影响

## 验收标准

- [ ] API 接受 `return_rendered_image` 参数
- [ ] 为 true 时，响应含 `rendered_image_b64`，是合法的 base64 PNG
- [ ] 解码后图像尺寸与 vLLM 实际看到的一致（vision_patch_size 对齐后）
- [ ] 为 false（默认）时，响应载荷大小不变
- [ ] 集成测试：带 flag 提交任务 → 解码图像 → 验证尺寸 = `figsize × dpi` 经对齐因子取整
- [ ] 文档说明载荷大小影响（典型 50-200 KB / 响应）

## 实现指引

```python
# qwen.py 草图
def render_timeseries_image(data, ..., return_image=False):
    img = ...  # 现有 PIL.Image
    if return_image:
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return img, base64.b64encode(buf.getvalue()).decode("ascii")
    return img, None
```

载荷大小可考虑：
- WebP @ quality 95 替代 PNG（更小，对图表近似无损）
- 可选 gzip 压缩
- 不入库（仅在响应中临时返回）

## Lab 依赖

- **阻塞**：`ts-lab/techniques/vl_self_refinement/chain_of_zoom.py`
- **要求合并时间**：Day 21（保证 ts-lab Phase 3 不延期）
- **若无此改动**：chain_of_zoom 可退化为重新渲染，但坐标漂移会导致 F1 估计有噪，且无法直接与 baseline 对比

## 范围外

- 流式图像返回
- 多分辨率（只返回已渲染的那一张；Round 2 的 zoom 渲染由 lab 自己做）
- 图像缓存 / 去重（每个任务渲染天然唯一）

## 引用

- [design-vl-self-refinement.md §3.4 chain-of-zoom](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md 附录 A.4 渲染细节](../../../ts-platform/docs/design-vl-self-refinement.md)
