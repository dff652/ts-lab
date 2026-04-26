# ts-lab Documentation

Execution details for ts-lab. Governance / design docs live in `ts-platform/docs/`.

## Files

| File | Purpose | Status |
|---|---|---|
| `golden-dataset.md` | Dataset schema + version history | TODO |
| `annotation-spec.md` | What counts as anomaly, boundary rules, examples | TODO |
| `benchmark-methodology.md` | F1 definitions + statistical tests | TODO |
| `reproducibility.md` | Manifest schema + version pinning + seed control | TODO |
| `experiments/` | Per-experiment reports | growing |
| `experiments/template.md` | Report template (use as starting point) | ✅ |

## Where Docs Live

| Type | Location |
|---|---|
| **Governance & design decisions** | `ts-platform/docs/` |
| **Execution details (this dir)** | `ts-lab/docs/` |
| **Discussion archive** | `ts-platform/docs/session-*.md` |

### Authoritative documents in ts-platform/docs/

- [design-vl-self-refinement.md](../../ts-platform/docs/design-vl-self-refinement.md) — main design ⭐
  - §3 7 大技术清单
  - §9 harness vs agent 定位
  - §10 预期收益与对比实验方法
  - §11 设计缺口与补强清单（含 ts-platform 8 项配合改动）
  - §15 三轨执行计划 + Track B 详解
  - §16 7 条执行建议（避免常见坑）
  - **附录 A：当前 ts-platform Pipeline 状态参考（file:line）** ⭐ 实施 technique 前必读
  - 附录 B：References（Wang 2022 / Madaan 2023 / Tatbul 2018 / vLLM）
- [session-2026-04-25.md](../../ts-platform/docs/session-2026-04-25.md) — 完整八轮讨论档案
- [design-agent-layer.md](../../ts-platform/docs/design-agent-layer.md) — 已弃用（保留作 Hermes/OpenClaw 对比 + 三层架构讨论的历史档案）

**Single source of truth — never copy across repos. Cross-link only.**

## Quick reference

实施 technique 时一定要先看：
1. **设计文档** `design-vl-self-refinement.md` 对应 §3.X 节（技术规格）
2. **Pipeline 现状** `design-vl-self-refinement.md` 附录 A（当前状态 + 痛点）
3. **TODO Reference Cards** `../TODO.md` RC-1 到 RC-10（决策规则）
4. **Methodology** `benchmark-methodology.md` + `reproducibility.md`（评测方法）
