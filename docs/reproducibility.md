# 可复现性 SOP

> 每次 benchmark 运行必须可复现。同样的技术、同样的数据集，在输入未变的前提下两次结果不同 —— 本次实验**作废**。

## 运行 Manifest

每次 benchmark 运行都生成一份 manifest，锁定：

```json
{
  "run_id": "<uuid>",
  "timestamp": "ISO-8601",
  "technique": "name",
  "code_commit": "<git-sha>",
  "code_dirty": false,
  "dataset_version": "v1-pilot",
  "dataset_hash": "<sha256>",
  "model": {
    "name": "qwen-vl",
    "checkpoint": "<version>",
    "backend": "vllm-0.17.1"
  },
  "seeds": {
    "model": 42,
    "sampling": 42
  },
  "params": {
    "temperature": 0.1,
    "max_tokens": 512,
    "...": "..."
  }
}
```

Manifest 与报告一并存放于 `eval/reports/<run_id>.manifest.json`。

## 运行前 Checklist

- [ ] 工作树干净（`git status` 为空）；或将 dirty 状态以 `WIP` 标记 commit
- [ ] 数据集版本存在且 hash 匹配
- [ ] 模型版本已记录
- [ ] 种子在代码中显式设置，未使用默认值
- [ ] 没有未记录的环境变量影响模型行为

## 非确定性的注意事项

即便满足以上所有条件，仍有以下非确定性来源：

- vLLM 在 GPU 上的核调度（尤其 batch size 变化时）
- 浮点 reduction 顺序在不同硬件上的差异
- 远程 API 类技术的网络 / 磁盘抖动

在 baseline 时记录观测方差（跑 3 次，算 std）。后续改进必须**超过 baseline std × 2** 才算有意义。

## 版本化策略

| 资产 | 策略 |
|---|---|
| 代码 | Git commit SHA |
| Pilot 数据集（<10MB） | 直接 git 跟踪 |
| Alpha-Beta 数据集（200-500） | git-lfs 或 DVC |
| Production 数据集（1000+） | DVC + 远程存储 |
| 实验报告 | Git 跟踪（小体积 markdown + CSV） |
| 原始模型输出 | **不**入 git（可由 manifest 重生） |

## 复现旧实验

```bash
git checkout <commit>
# 校验数据集 hash 与 manifest 一致
python -m benchmarks.run_benchmark --technique <name> --dataset <version> --seed <seed>
# 与原报告 diff
```
