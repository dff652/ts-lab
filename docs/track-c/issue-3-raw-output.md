# Issue 3: Persist and expose raw VL output in results

**Suggested labels**: `enhancement`, `priority:medium`, `blocks:ts-lab`, `area:inference`, `area:database`
**Suggested milestone**: ts-lab Phase 3 (Day 21)
**Estimated effort**: DB migration + ~50 lines + test

---

## Background

Several ts-lab techniques need access to the **raw text output** from Qwen-VL, not just the post-parsed structured anomalies:

- **`robust_parser` Tier 5**: when JSON parsing fails through tiers 1-4, the lab calls Qwen-VL again with a "rewrite this as valid JSON" prompt. Requires the original raw output.
- **`self_critique`**: feeds the model's own previous output back as text for review.
- **General research**: understanding *how* the model outputs malformed JSON helps refine prompts.

Currently `vllm_client.py:303-330` parses output then discards raw text on success, and returns hard error on parse failure. The original text never reaches storage or the API.

## Required Change

Persist raw model output and expose it via the results API.

### Affected files

| File | Change |
|---|---|
| `backend/app/models/result.py` (or equivalent) | Add `raw_model_output: Optional[str]` column |
| `backend/migrations/<new>.py` (Alembic) | Migration: add column, default NULL, no backfill |
| `backend/app/adapters/gpu_algorithms/qwen.py` | Persist raw output before parsing (success or failure) |
| `backend/app/adapters/gpu_algorithms/vllm_client.py` | Don't error out on parse failure if raw is captured |
| `backend/app/api/results.py` | Include `raw_model_output` in result query response |
| `backend/app/schemas/result.py` | Update Pydantic response model |

### Storage policy

- Default: store full raw output (typically 500-2000 chars; rarely >5KB)
- **Cap at 10KB** to prevent malicious / pathological outputs blowing up DB
- Index NOT required (queries by result_id only)
- Storage cost analysis: ~10KB × N tasks ≈ negligible at current scale

## Acceptance Criteria

- [ ] DB column added via Alembic migration; runs cleanly on existing DB
- [ ] Raw output stored on every Qwen-VL call (both success and parse-failure cases)
- [ ] Result API endpoint returns `raw_model_output` field (nullable for legacy rows)
- [ ] Output truncated at 10KB with truncation indicator if exceeded
- [ ] Existing parse-success behavior unchanged (raw is additional, not replacement)
- [ ] Existing parse-failure behavior changed: now stores raw output AND records failure mode (instead of hard error)
- [ ] Storage cost analyzed and documented in PR description

## Implementation Hints

Migration sketch:

```python
# alembic/versions/<rev>_add_raw_model_output.py
def upgrade():
    op.add_column(
        "result",
        sa.Column("raw_model_output", sa.Text, nullable=True),
    )

def downgrade():
    op.drop_column("result", "raw_model_output")
```

Adapter sketch:

```python
# qwen.py
def call_qwen(...):
    raw = vllm_complete(...)  # raw text
    record_raw(task_id, raw[:10_000])  # truncate

    try:
        parsed = parse_qwen_output(raw)
    except ParseError as e:
        record_parse_failure(task_id, str(e))
        return None  # NO LONGER hard error
    return parsed
```

## Lab Dependency

- **Blocks**: `ts-lab/techniques/vl_self_refinement/robust_parser.py` Tier 5 (LLM-rewrite fallback)
- **Blocks**: `ts-lab/techniques/vl_self_refinement/self_critique.py` (needs raw text to feed back)
- **Required by**: Day 21 (to keep ts-lab Phase 3 on schedule)
- **Without it**: robust_parser caps at Tier 4 (regex fallback, lossy); self_critique cannot be implemented faithfully

## Migration Risk

🟡 **Medium**: requires DB migration. Need rollout plan:
- Migration runs in deploy hook (no manual step)
- Old code paths continue to work (column nullable)
- Rollback: simple `DROP COLUMN`; no data loss for non-using callers

## Out of Scope

- Querying by raw output content (no need yet; if so, add full-text index later)
- Long-term archival (current short-term retention is fine for lab work)
- Privacy redaction (raw output contains no user PII; just numeric series rendered as image)

## References

- [design-vl-self-refinement.md §3.2 robust parser](../../../ts-platform/docs/design-vl-self-refinement.md)
- [design-vl-self-refinement.md §3.5 self-critique](../../../ts-platform/docs/design-vl-self-refinement.md)
- Current parse-failure code: `backend/app/adapters/gpu_algorithms/vllm_client.py:303-330`
