# ts-lab

Time-series anomaly detection inference-time enhancement harness for [ts-platform](../ts-platform).

## Mission

Improve **stability** and **accuracy** of Qwen-VL-based time-series anomaly detection through inference-time techniques (self-refinement, self-consistency, chain-of-zoom, robust parsing) — **without retraining the model**.

This is a **harness** (Python decides control flow, LLM is called as a function), **not an agent framework**.

## Key References

- **Design doc**: [ts-platform/docs/design-vl-self-refinement.md](../ts-platform/docs/design-vl-self-refinement.md) ⭐ read this first
- **Discussion archive**: [ts-platform/docs/session-2026-04-25.md](../ts-platform/docs/session-2026-04-25.md)
- **Status**: Pilot — Day 1 skeleton

## Project Structure

```
ts-lab/
├── techniques/
│   └── vl_self_refinement/      # current main line (7 techniques)
├── benchmarks/
│   ├── golden_dataset/          # data + annotations (pilot 50 samples)
│   ├── scripts/                 # audit / sample selection / kappa
│   └── run_benchmark.py
├── eval/                        # metrics + statistical comparison
├── docs/
│   └── experiments/             # per-experiment reports
├── notebooks/                   # exploration (throw-away)
└── tests/
```

## Quick Start

```bash
# install (editable)
pip install -e ".[dev]"

# run smoke tests
pytest tests/

# data audit (after backend/client SDK is extracted)
python -m benchmarks.scripts.audit

# benchmark (after golden dataset is ready)
python -m benchmarks.run_benchmark --technique baseline
```

## Development Status (2026-04-26)

| Track | Component | Status |
|---|---|---|
| A | Repo skeleton + push origin/main + docs 中文化 | ✅ |
| A | backend/client SDK extraction | 🟡 starting point exists: `ts-platform/backend/tests/examples/client.py` (509 lines) |
| A | baseline runner | 🔴 not started (blocked on SDK route decision e1/e2) |
| B | Data audit | 🔴 not started |
| B | Golden dataset (50 pilot) | 🔴 not started |
| C | ts-platform Issue 1 (response_format) | 🟡 spec ready, **direct implementation pending** (#36, half-day) |
| C | ts-platform Issue 2 (rendered image) | 🟡 spec ready, direct implementation (#4.2, half-day) |
| C | ts-platform Issue 3 (raw VL output) | 🟡 spec ready but **urgency reduced** — `vllm_client` already gracefully captures `raw_text`; only DB persistence missing |

> **Note**: ts-lab and ts-platform share a single maintainer. Track C does not require external issue filing — the `docs/track-c/` drafts now serve as design specs for direct implementation. See [TODO.md](TODO.md) §"本次会话关键发现" for full context.

## Technique Roadmap

Priority order (per design doc §15.6):

1. **robust_parser** — zero dependency, immediate value
2. **guided_json** — blocked on Issue 1
3. **baseline benchmark** — pre-requisite for everything else
4. **self_consistency** — simple and quantifiable
5. **chain_of_zoom** — most promising, blocked on Issue 2
6. **self_critique** — incremental
7. **format_locking (few-shot)** — incremental

**Do NOT start chain_of_zoom first** — it depends on everything above.

## Naming Convention

Repo named `ts-lab` (not `ts-vl-lab`) to allow future expansion beyond VL self-refinement. Current main line lives under `techniques/vl_self_refinement/`.

## Doc Boundary

- **ts-lab/docs/** — execution details (annotation spec, methodology, experiment reports)
- **ts-platform/docs/** — governance & design decisions (architecture, API specs)

Single source of truth — never copy across repos. Cross-link only.

## Contributing

Experiment reports go in `docs/experiments/YYYY-MM-DD-<technique>.md` using `docs/experiments/template.md`.
