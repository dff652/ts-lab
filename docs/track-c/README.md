# Track C — ts-platform Issue Drafts

This directory contains draft issues for ts-platform that ts-lab depends on.

## Workflow

1. Review and refine the drafts here
2. File them in ts-platform's issue tracker (GitHub / GitLab / Jira)
3. Track issue numbers + status in `../../TODO.md` Track C section
4. Once merged, mark blocked techniques as unblocked in TODO

## Issues

| # | Title | Priority | Lab Dependency | File |
|---|---|---|---|---|
| 1 | Add `response_format` passthrough to vLLM backend | 🔴 highest | guided_json | [issue-1-response-format.md](issue-1-response-format.md) |
| 2 | Expose rendered chart image in inference response | 🟡 medium | chain_of_zoom | [issue-2-rendered-image.md](issue-2-rendered-image.md) |
| 3 | Persist and expose raw VL output in results | 🟡 medium | robust_parser Tier 5, self_critique | [issue-3-raw-output.md](issue-3-raw-output.md) |

## Deadlines

To keep ts-lab on schedule (per `../../TODO.md` 关键 Deadline):

| Issue | Merge Deadline | Blocking |
|---|---|---|
| 1 | Day 14 | guided_json technique |
| 2 | Day 21 | chain_of_zoom technique |
| 3 | Day 21 | robust_parser Tier 5 + self_critique |

## Source Design

These issues are derived from `ts-platform/docs/design-vl-self-refinement.md`:
- §11.2 ts-platform 必须配合的改动
- §15.6 Track C Day 1 — 三个 ts-platform issue

For nice-to-have follow-up changes (not blocking lab), see TODO #5a-#5e.
