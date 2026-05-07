"""Multi-tier fallback parser for Qwen-VL JSON output.

See ts-platform/docs/design-vl-self-refinement.md §3.2 + ts-lab/TODO.md RC-6.

Fallback chain (按顺序尝试，先成功者返回):
  Tier 1: 直接 json.loads
  Tier 2: 剥离 markdown ``` 包装 + 前后散文
  Tier 3: 修常见格式错（尾逗号、单引号、注释）
  Tier 4: 正则抽 [s, e] 对（兜底，丢失 type/reason）
  Tier 5: 调 LLM 重写为合法 JSON（需要 llm_rewrite_fn 注入；不传则跳过）

设计契约:
  - 每个 tier 只在「能从 raw 中提取出结构」时返回 list[AnomalyInterval]
  - 「合法 list 但内容为空」（模型说"没有异常"）→ 返回 [] 是合法结果
  - 所有 tier 都失败「连一个 [s, e] 都抽不出来」→ raise ParseFailure
    （遵循 llm-platform engineering-principles.md 原则 1：显式失败优于隐式兜底）

Priority: 🔴 highest（lowest hanging fruit, zero dependency for tier 1-4）
"""
from __future__ import annotations

import json
import re
from typing import Callable, TypedDict


class AnomalyInterval(TypedDict):
    interval: list[int]
    type: str
    reason: str


class ParseFailure(Exception):
    """5 级 fallback 全部失败时抛出。包含尝试过的 tier 和原始文本，便于 debug。"""

    def __init__(self, raw_output: str, attempted: list[str], last_error: str = ""):
        self.raw_output = raw_output
        self.attempted = attempted
        self.last_error = last_error
        super().__init__(
            f"All {len(attempted)} parser tiers failed: {attempted}. "
            f"Last error: {last_error}. Raw[:200]={raw_output[:200]!r}"
        )


LlmRewriteFn = Callable[[str], str]
"""Tier 5 注入函数签名：输入 raw_output，输出重写后的 JSON 字符串。

实施时由 baseline runner 提供（带 ts-platform client SDK），robust_parser
本身不直接持有 LLM client（保持与 baseline 解耦）。
"""


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def parse(
    raw_output: str,
    llm_rewrite_fn: LlmRewriteFn | None = None,
) -> list[AnomalyInterval]:
    """5 级 fallback 解析 Qwen-VL 输出为异常区间列表。

    Args:
        raw_output: 模型原始文本。
        llm_rewrite_fn: Tier 5 重写函数。None 时仅跑 Tier 1-4，常规场景够用。

    Returns:
        异常区间列表（可能为空 —— 模型说"没异常"是合法结果）。

    Raises:
        ParseFailure: Tier 1-4（及 Tier 5 if provided）全失败、连一个 [s, e]
                      都没抽出来时。
    """
    attempted: list[str] = []
    last_error = ""

    # Tier 1
    attempted.append("tier1_direct")
    try:
        result = _tier1_direct(raw_output)
        if result is not None:
            return result
    except Exception as e:
        last_error = f"tier1: {e}"
        # fallback by design: tier1 失败是常态（markdown 包裹 / 尾逗号），降级到 tier2

    # Tier 2
    attempted.append("tier2_strip_markdown")
    try:
        result = _tier2_strip_markdown(raw_output)
        if result is not None:
            return result
    except Exception as e:
        last_error = f"tier2: {e}"
        # fallback by design: tier2 失败 → 字符串里还有非 markdown 的格式问题，降级到 tier3

    # Tier 3
    attempted.append("tier3_fix_common_errors")
    try:
        result = _tier3_fix_common_errors(raw_output)
        if result is not None:
            return result
    except Exception as e:
        last_error = f"tier3: {e}"
        # fallback by design: tier3 修不了 → 模型可能完全没按 JSON 写，降级到正则兜底

    # Tier 4
    attempted.append("tier4_regex_extract")
    try:
        result = _tier4_regex_extract(raw_output)
        if result:  # 注意：tier4 的"成功"必须抽到 ≥1 个 [s,e]，空 list 视为失败
            return result
    except Exception as e:
        last_error = f"tier4: {e}"

    # Tier 5（可选）
    if llm_rewrite_fn is not None:
        attempted.append("tier5_llm_rewrite")
        try:
            rewritten = llm_rewrite_fn(raw_output)
            result = _tier1_direct(rewritten)  # 复用 tier1 解析重写结果
            if result is not None:
                return result
        except Exception as e:
            last_error = f"tier5: {e}"

    raise ParseFailure(raw_output, attempted, last_error)


# ---------------------------------------------------------------------------
# Tier 实现
# ---------------------------------------------------------------------------

def _tier1_direct(s: str) -> list[AnomalyInterval] | None:
    """直接 json.loads 并归一化。失败返回 None。"""
    try:
        obj = json.loads(s)
    except json.JSONDecodeError:
        return None
    return _normalize_to_intervals(obj)


_MARKDOWN_BLOCK_RE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL | re.IGNORECASE)


def _tier2_strip_markdown(s: str) -> list[AnomalyInterval] | None:
    """剥 ```json ... ``` 包装 + 前后散文，再走 tier1。

    支持多种包裹形式：```json ... ``` / ``` ... ``` / 模型先写解释再贴 JSON。
    """
    # 优先匹配 markdown 代码块
    match = _MARKDOWN_BLOCK_RE.search(s)
    if match:
        candidate = match.group(1).strip()
        result = _tier1_direct(candidate)
        if result is not None:
            return result

    # 退一步：找首个 { 或 [ 到末尾的 } 或 ] 作为 JSON 子串
    candidate = _extract_json_substring(s)
    if candidate:
        return _tier1_direct(candidate)
    return None


_TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")
_PYTHON_LITERAL_RE = re.compile(r"\b(True|False|None)\b")
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def _tier3_fix_common_errors(s: str) -> list[AnomalyInterval] | None:
    """修常见 LLM JSON 格式错误后再走 tier1 / tier2。

    覆盖：
      - 尾逗号 `[1, 2,]` → `[1, 2]`
      - Python 字面量 True/False/None → true/false/null
      - 单行 // 注释、块 /* */ 注释（vLLM 偶发）
      - 单引号包字符串 → 双引号（保守：仅替换明显的 `'key':` 模式）
    """
    fixed = s
    fixed = _BLOCK_COMMENT_RE.sub("", fixed)
    fixed = _LINE_COMMENT_RE.sub("", fixed)
    fixed = _TRAILING_COMMA_RE.sub(r"\1", fixed)
    fixed = _PYTHON_LITERAL_RE.sub(
        lambda m: {"True": "true", "False": "false", "None": "null"}[m.group(0)],
        fixed,
    )
    # 单引号转双引号：仅当字符串里没有双引号时才整体替换（避免破坏内嵌引号）
    if "'" in fixed and '"' not in fixed:
        fixed = fixed.replace("'", '"')

    # 修完后用 tier1 + tier2 链路再试
    result = _tier1_direct(fixed)
    if result is not None:
        return result
    return _tier2_strip_markdown(fixed)


_INTERVAL_PAIR_RE = re.compile(r"\[\s*(\d+)\s*,\s*(\d+)\s*\]")


def _tier4_regex_extract(s: str) -> list[AnomalyInterval]:
    """正则抽所有 [整数, 整数] 对作为 interval。丢失 type/reason。"""
    intervals: list[AnomalyInterval] = []
    for m in _INTERVAL_PAIR_RE.finditer(s):
        start, end = int(m.group(1)), int(m.group(2))
        if end > start:  # 过滤 [0, 0] 这种无意义对
            intervals.append({
                "interval": [start, end],
                "type": "unknown",
                "reason": "regex-extracted, original structure lost",
            })
    return intervals


# ---------------------------------------------------------------------------
# 共用工具
# ---------------------------------------------------------------------------

def _extract_json_substring(s: str) -> str | None:
    """找首个 { 或 [ 到匹配的 } 或 ]（朴素括号配对，不处理字符串内的括号）。

    够用即可：模型一般不会在字符串里塞嵌套引号；若塞了，tier3 的格式修复会兜底。
    """
    start = -1
    open_char = ""
    for i, ch in enumerate(s):
        if ch in "{[":
            start = i
            open_char = ch
            break
    if start < 0:
        return None

    close_char = "}" if open_char == "{" else "]"
    depth = 0
    for j in range(start, len(s)):
        if s[j] == open_char:
            depth += 1
        elif s[j] == close_char:
            depth -= 1
            if depth == 0:
                return s[start : j + 1]
    return None


def _normalize_to_intervals(obj) -> list[AnomalyInterval] | None:
    """把任意 JSON 对象归一化为 AnomalyInterval list。

    支持的输入形态：
      - {"detected_anomalies": [...]}    标准 schema
      - {"anomalies": [...]}             常见变体
      - [...]                            裸 list
      - {"interval": [...]}              单对象（包成 list）

    返回 None 表示无法归一化（让上层降级）。
    """
    if isinstance(obj, dict):
        # 优先认 schema 标准 key
        for key in ("detected_anomalies", "anomalies", "results"):
            if key in obj and isinstance(obj[key], list):
                return _normalize_list(obj[key])
        # 单对象 fallback
        if "interval" in obj:
            normalized = _normalize_item(obj)
            return [normalized] if normalized else []
        return None

    if isinstance(obj, list):
        # 裸 list 输入需谨慎：tier 2 在散文里抠出 `[50, 60]` 这种数字对会
        # 当成合法 JSON list，但归一化后是空 list。空结果当"成功"会阻止
        # 降级到 tier 4 正则抽取。所以裸 list 形态要求至少 1 项可归一化。
        # （dict 形态下 `detected_anomalies: []` 仍算合法"无异常"，走 dict 分支。）
        if not obj:
            return None
        normalized = _normalize_list(obj)
        return normalized if normalized else None

    return None


def _normalize_list(items: list) -> list[AnomalyInterval]:
    """对 list 中每个 item 调 _normalize_item，跳过非法项（不整体失败）。"""
    result: list[AnomalyInterval] = []
    for item in items:
        if isinstance(item, dict):
            normalized = _normalize_item(item)
            if normalized:
                result.append(normalized)
    return result


def _normalize_item(item: dict) -> AnomalyInterval | None:
    """一个 dict → AnomalyInterval。interval 字段必须是 [int, int]。"""
    iv = item.get("interval")
    if not (isinstance(iv, list) and len(iv) == 2):
        return None
    try:
        start, end = int(iv[0]), int(iv[1])
    except (TypeError, ValueError):
        return None
    return {
        "interval": [start, end],
        "type": str(item.get("type", "")),
        "reason": str(item.get("reason", "")),
    }
