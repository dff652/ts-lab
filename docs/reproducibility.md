# Reproducibility SOP

> Every benchmark run must be reproducible. If two runs of the same technique on the same dataset give different numbers without changes in input, the experiment is invalid.

## Run Manifest

Every benchmark run produces a manifest pinning:

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

Manifest stored alongside the report at `eval/reports/<run_id>.manifest.json`.

## Pre-Run Checklist

- [ ] Working tree clean (`git status` empty) OR commit dirty state with `WIP` flag
- [ ] Dataset version exists and hash matches
- [ ] Model version recorded
- [ ] Seeds explicitly set in code, not defaulted
- [ ] No environment variables affecting model behavior unrecorded

## Determinism Caveats

Even with all of the above, some sources of non-determinism:

- vLLM kernel scheduling on GPUs (especially with batch size variation)
- Floating-point reduction order across hardware
- Network/disk variability for remote-API techniques

Document observed variance in baseline (run 3 times, compute std). Subsequent improvements must exceed baseline std × 2 to be meaningful.

## Versioning Strategy

| Asset | Strategy |
|---|---|
| Code | Git commit SHA |
| Pilot dataset (<10MB) | Direct git tracking |
| Alpha-Beta dataset (200-500) | git-lfs or DVC |
| Production dataset (1000+) | DVC + remote storage |
| Reports | Git tracked (small markdown + CSV) |
| Raw model outputs | NOT git tracked (regenerable from manifest) |

## Re-running an old experiment

```bash
git checkout <commit>
# verify dataset hash matches manifest
python -m benchmarks.run_benchmark --technique <name> --dataset <version> --seed <seed>
# diff against original report
```
