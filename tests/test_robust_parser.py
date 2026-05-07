"""robust_parser 5 级 fallback 单元测试。

每个 tier 至少覆盖：
  - 该 tier 能成功处理的典型输入
  - 该 tier 处理不了、需要降级到下一 tier 的输入
  - 综合：上层入口 parse() 选对 tier

Tier 5 用 fake llm_rewrite_fn 注入，不依赖真 LLM。
"""
from __future__ import annotations

import pytest

from techniques.vl_self_refinement.robust_parser import (
    ParseFailure,
    parse,
    _normalize_to_intervals,
    _tier1_direct,
    _tier2_strip_markdown,
    _tier3_fix_common_errors,
    _tier4_regex_extract,
)


# ---------------------------------------------------------------------------
# Tier 1 — 直接 json.loads
# ---------------------------------------------------------------------------

class TestTier1Direct:
    def test_standard_schema(self):
        """标准 ANOMALY_SCHEMA 形态一次解析成功。"""
        raw = '{"detected_anomalies": [{"interval": [10, 20], "type": "spike", "reason": "jump"}]}'
        result = _tier1_direct(raw)
        assert result == [{"interval": [10, 20], "type": "spike", "reason": "jump"}]

    def test_naked_list(self):
        """裸 list 形态也能识别。"""
        raw = '[{"interval": [5, 8], "type": "dip", "reason": ""}]'
        result = _tier1_direct(raw)
        assert result == [{"interval": [5, 8], "type": "dip", "reason": ""}]

    def test_empty_anomalies_is_legitimate(self):
        """空 list 是合法结果（模型说"没异常"），不是失败。"""
        raw = '{"detected_anomalies": []}'
        assert _tier1_direct(raw) == []

    def test_invalid_json_returns_none(self):
        """不是合法 JSON → 返回 None 让上层降级。"""
        assert _tier1_direct("```json\n{...}\n```") is None
        assert _tier1_direct("oops") is None

    def test_alt_key_anomalies(self):
        """anomalies / results 等常见 key 变体也认。"""
        raw = '{"anomalies": [{"interval": [1, 2], "type": "x"}]}'
        result = _tier1_direct(raw)
        assert result and result[0]["interval"] == [1, 2]


# ---------------------------------------------------------------------------
# Tier 2 — 剥 markdown / 找 JSON 子串
# ---------------------------------------------------------------------------

class TestTier2StripMarkdown:
    def test_json_fenced_block(self):
        raw = '```json\n{"detected_anomalies": [{"interval": [3, 7], "type": "spike"}]}\n```'
        result = _tier2_strip_markdown(raw)
        assert result == [{"interval": [3, 7], "type": "spike", "reason": ""}]

    def test_unfenced_with_prose(self):
        """模型先写解释再贴 JSON，没用 ``` 包。"""
        raw = (
            "Here are the anomalies I detected:\n\n"
            '{"detected_anomalies": [{"interval": [100, 145], "type": "spike", "reason": "x"}]}'
            "\n\nLet me know if you need more."
        )
        result = _tier2_strip_markdown(raw)
        assert result and result[0]["interval"] == [100, 145]

    def test_plain_json_passes_through(self):
        """已经是干净 JSON，tier2 不应破坏。"""
        raw = '{"detected_anomalies": [{"interval": [1, 2], "type": "y"}]}'
        result = _tier2_strip_markdown(raw)
        assert result and result[0]["interval"] == [1, 2]


# ---------------------------------------------------------------------------
# Tier 3 — 修常见格式错
# ---------------------------------------------------------------------------

class TestTier3FixCommonErrors:
    def test_trailing_comma(self):
        raw = '{"detected_anomalies": [{"interval": [1, 2], "type": "spike",},]}'
        result = _tier3_fix_common_errors(raw)
        assert result and result[0]["interval"] == [1, 2]

    def test_single_quotes(self):
        raw = "{'detected_anomalies': [{'interval': [3, 5], 'type': 'dip'}]}"
        result = _tier3_fix_common_errors(raw)
        assert result and result[0]["interval"] == [3, 5]

    def test_python_literals(self):
        """模型偶尔输出 Python 风格 True/None。"""
        raw = '{"detected_anomalies": [{"interval": [1, 2], "type": "x", "valid": True, "extra": None}]}'
        result = _tier3_fix_common_errors(raw)
        assert result and result[0]["interval"] == [1, 2]

    def test_inline_comments(self):
        """vLLM 偶发输出 // 注释。"""
        raw = """
        {
          "detected_anomalies": [
            {"interval": [10, 20], "type": "spike"} // suspicious peak
          ]
        }
        """
        result = _tier3_fix_common_errors(raw)
        assert result and result[0]["interval"] == [10, 20]

    def test_combined_errors(self):
        """尾逗号 + 单引号 + 注释组合（最坏情况之一）。"""
        raw = """
        {'detected_anomalies': [
          {'interval': [5, 10], 'type': 'spike',}, // bad day
        ]}
        """
        result = _tier3_fix_common_errors(raw)
        assert result and result[0]["interval"] == [5, 10]


# ---------------------------------------------------------------------------
# Tier 4 — 正则兜底
# ---------------------------------------------------------------------------

class TestTier4RegexExtract:
    def test_extract_pairs_from_prose(self):
        """完全没按 JSON 写时，从散文里抠 [s, e]。"""
        raw = "I found anomalies at [120, 145] and [300, 305] in the data."
        result = _tier4_regex_extract(raw)
        assert len(result) == 2
        assert result[0]["interval"] == [120, 145]
        assert result[1]["interval"] == [300, 305]
        # 类型/原因丢失，标记 unknown
        assert result[0]["type"] == "unknown"
        assert "regex-extracted" in result[0]["reason"]

    def test_skip_zero_width(self):
        """[0, 0] 这种无意义对不算异常。"""
        raw = "Saw [0, 0] but real one is [50, 60]"
        result = _tier4_regex_extract(raw)
        assert len(result) == 1
        assert result[0]["interval"] == [50, 60]

    def test_no_pairs_returns_empty(self):
        """完全找不到 → 空 list（让 parse() 入口判失败）。"""
        assert _tier4_regex_extract("nothing here") == []


# ---------------------------------------------------------------------------
# 入口：parse() 综合 + Tier 5
# ---------------------------------------------------------------------------

class TestParseEntry:
    def test_clean_input_uses_tier1(self):
        raw = '{"detected_anomalies": [{"interval": [1, 2], "type": "x"}]}'
        result = parse(raw)
        assert result and result[0]["interval"] == [1, 2]

    def test_markdown_input_falls_to_tier2(self):
        raw = '```json\n{"detected_anomalies": [{"interval": [9, 12], "type": "y"}]}\n```'
        result = parse(raw)
        assert result and result[0]["interval"] == [9, 12]

    def test_dirty_json_falls_to_tier3(self):
        raw = "{'detected_anomalies': [{'interval': [7, 11], 'type': 'spike',}]}"
        result = parse(raw)
        assert result and result[0]["interval"] == [7, 11]

    def test_pure_prose_falls_to_tier4(self):
        raw = "Anomalies seen at [50, 60] and [200, 220]."
        result = parse(raw)
        assert len(result) == 2
        assert result[0]["interval"] == [50, 60]

    def test_empty_legitimate(self):
        """模型说没异常 → 返回空 list，不抛错。"""
        result = parse('{"detected_anomalies": []}')
        assert result == []

    def test_total_failure_raises(self):
        """连一个 [s, e] 都没有 + 没传 tier 5 → ParseFailure。"""
        with pytest.raises(ParseFailure) as exc_info:
            parse("Sorry, I cannot detect anomalies in this image.")
        assert "tier4_regex_extract" in exc_info.value.attempted

    def test_tier5_rewrites_when_provided(self):
        """tier 1-4 都失败时，tier 5 调 LLM 重写后能成功。"""
        # 模型胡言乱语，没法抽
        raw = "Sorry, the image quality is too poor to analyze."

        # fake LLM 重写函数：知道"应该"返回什么
        def fake_rewrite(text: str) -> str:
            return '{"detected_anomalies": [{"interval": [42, 50], "type": "fallback"}]}'

        result = parse(raw, llm_rewrite_fn=fake_rewrite)
        assert result and result[0]["interval"] == [42, 50]

    def test_tier5_failure_still_raises(self):
        """tier 5 LLM 也救不回来 → ParseFailure 包含 tier5_llm_rewrite。"""
        raw = "Sorry, cannot help."

        def bad_rewrite(text: str) -> str:
            return "still garbage"

        with pytest.raises(ParseFailure) as exc_info:
            parse(raw, llm_rewrite_fn=bad_rewrite)
        assert "tier5_llm_rewrite" in exc_info.value.attempted
        assert exc_info.value.raw_output == raw

    def test_tier5_exception_caught(self):
        """tier 5 函数抛异常 → 捕获并仍 raise ParseFailure（不让 LLM 失败炸飞主流程）。"""
        raw = "garbage with no [pairs]"  # tier 4 抓不到

        def boom(text: str) -> str:
            raise RuntimeError("LLM service down")

        with pytest.raises(ParseFailure) as exc_info:
            parse(raw, llm_rewrite_fn=boom)
        assert "LLM service down" in exc_info.value.last_error


# ---------------------------------------------------------------------------
# 归一化边界
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_skip_invalid_items_dont_fail_whole(self):
        """list 中部分项不合法时，跳过坏项保留好项（不整体 None）。"""
        obj = {
            "detected_anomalies": [
                {"interval": [1, 2], "type": "good"},
                {"type": "no_interval"},          # 缺 interval，跳过
                {"interval": [3, "bad"]},         # interval 非整数对，跳过
                {"interval": [10, 20], "type": "another"},
            ]
        }
        result = _normalize_to_intervals(obj)
        assert len(result) == 2
        assert result[0]["interval"] == [1, 2]
        assert result[1]["interval"] == [10, 20]

    def test_single_object_wrapped_as_list(self):
        """模型偶尔只返回单对象。"""
        obj = {"interval": [5, 8], "type": "spike"}
        result = _normalize_to_intervals(obj)
        assert result == [{"interval": [5, 8], "type": "spike", "reason": ""}]

    def test_unknown_shape_returns_none(self):
        """完全不是 anomaly 形态 → None。"""
        assert _normalize_to_intervals({"foo": "bar"}) is None
        assert _normalize_to_intervals(42) is None

    def test_default_type_reason_when_missing(self):
        """type 和 reason 缺失时填空字符串，不报错。"""
        obj = {"detected_anomalies": [{"interval": [1, 2]}]}
        result = _normalize_to_intervals(obj)
        assert result == [{"interval": [1, 2], "type": "", "reason": ""}]
