"""Multi-tier fallback parser for Qwen-VL JSON output.

See ts-platform/docs/design-vl-self-refinement.md §3.2.

Fallback chain:
  1. Direct JSON parse
  2. Strip markdown code blocks
  3. Fix trailing comma + single quotes
  4. Regex extract [s, e] patterns
  5. Last resort: ask Qwen-VL to rewrite as valid JSON

Priority: 🔴 highest (lowest hanging fruit, zero dependency).
Status: TODO — first technique to implement.
"""
from typing import Any


def parse(raw_output: str) -> list[dict]:
    """Robustly parse Qwen-VL output to anomaly intervals.

    Args:
        raw_output: Raw text from Qwen-VL (may be JSON, JSON-in-markdown,
                    JSON with trailing comma, or unparseable).

    Returns:
        List of {"interval": [s, e], "type": str, "reason": str}.
        Returns empty list if all fallback levels fail.
    """
    raise NotImplementedError("TODO — first technique")


def _try_direct_json(s: str) -> Any:
    """Tier 1: direct json.loads."""
    raise NotImplementedError("TODO")


def _try_strip_markdown(s: str) -> Any:
    """Tier 2: strip ```json ... ``` wrappers."""
    raise NotImplementedError("TODO")


def _try_fix_common_errors(s: str) -> Any:
    """Tier 3: fix trailing commas, single quotes, etc."""
    raise NotImplementedError("TODO")


def _try_regex_extract(s: str) -> list[dict]:
    """Tier 4: regex find all [s, e] pairs."""
    raise NotImplementedError("TODO")


def _try_llm_rewrite(s: str) -> list[dict]:
    """Tier 5: ask Qwen-VL to rewrite as valid JSON (text-only call)."""
    raise NotImplementedError("TODO")
