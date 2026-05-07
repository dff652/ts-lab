"""ts-platform REST API 薄壳客户端（requests 实现）。

SDK 路线 = e2（[docs/pending-decisions.md](../docs/pending-decisions.md) 2026-05-07）。

骨架原则：
  - 每个 API 一个函数，签名稳定即可，实现 5-10 行
  - 凭据从环境变量读：`TS_PLATFORM_BASE_URL` + `TS_PLATFORM_API_KEY`
  - 不做 retry / 限流 / 重试 等 production-quality 机制 —— 那是 #14-16 抽
    正式 SDK 时的事
  - 所有失败显式 raise（遵循工程原则 1：显式失败优于隐式兜底）
  - **不**写 `except: pass` silent swallow（呼应 llm-platform engineering-
    principles.md 原则 2 + ts-lab Code Review §🔴.A）

阻塞情况：
  - `infer(..., response_format=...)` 字段透传依赖 ts-platform Issue 1 实装（#36）
  - `infer(..., return_rendered_image=...)` 依赖 ts-platform Issue 2（#4.2）
  - `get_raw_model_output()` 依赖 ts-platform Issue 3（#4.3）

当前所有函数均 raise NotImplementedError，等环境 + Issue 1 后填实现。
"""
from __future__ import annotations

import os
from typing import Any, TypedDict


# ---------------------------------------------------------------------------
# 配置 + 凭据
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://localhost:8000"  # ts-platform dev 默认端口
DEFAULT_TIMEOUT = 120  # 推理任务可能慢


def _base_url() -> str:
    return os.environ.get("TS_PLATFORM_BASE_URL", DEFAULT_BASE_URL)


def _api_key() -> str:
    """从环境变量读 API key。缺失即 RuntimeError（不给默认值，遵循工程原则 1）。"""
    key = os.environ.get("TS_PLATFORM_API_KEY")
    if not key:
        raise RuntimeError(
            "TS_PLATFORM_API_KEY environment variable not set. "
            "Set it to a valid ts-platform API key before calling client functions."
        )
    return key


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# 推理（核心）
# ---------------------------------------------------------------------------

class InferResult(TypedDict):
    """ts-platform 推理任务结果。

    注：raw_text 字段依赖 ts-platform Issue 3（#4.3）持久化到 DB +
    通过 API 返回。当前 vllm_client.py:303-339 已 graceful 捕获，
    只是没暴露在 results API。
    """

    success: bool
    detected_anomalies: list[dict] | None  # 解析后区间，失败时 None
    raw_text: str | None                   # 原始模型输出（依赖 Issue 3）
    error_code: str | None
    error_message: str | None
    latency_ms: int | None


def infer(
    series_id: str,
    *,
    inference_mode: str = "text",
    response_format: dict | None = None,
    return_rendered_image: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> InferResult:
    """对单条时序触发 Qwen-VL 推理，返回结果。

    Args:
        series_id: ts-platform data_pool 中的序列 ID。
        inference_mode: "text" | "grounding"。
        response_format: vLLM guided_json schema（依赖 ts-platform Issue 1）。
        return_rendered_image: 是否回传渲染图（依赖 ts-platform Issue 2）。
        timeout: HTTP 超时（秒）。

    Returns:
        InferResult dict.

    Raises:
        RuntimeError: 凭据缺失。
        requests.HTTPError: ts-platform 4xx/5xx。
        requests.Timeout: 推理超时。

    实施提示（待 Issue 1 + 环境就绪后填）:
        import requests
        url = f"{_base_url()}/api/v1/inference/external"
        body = {
            "series_id": series_id,
            "inference_mode": inference_mode,
            "response_format": response_format,
            "return_rendered_image": return_rendered_image,
        }
        body = {k: v for k, v in body.items() if v is not None}
        resp = requests.post(url, json=body, headers=_auth_headers(), timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    """
    raise NotImplementedError(
        "Pending: ts-platform Issue 1 实装（#36）+ 环境凭据。"
        "签名已稳定，调用方可先按此 contract 编程。"
    )


# ---------------------------------------------------------------------------
# 数据池
# ---------------------------------------------------------------------------

def list_data_pool(
    page: int = 1,
    page_size: int = 50,
    *,
    data_type: str | None = None,
) -> dict[str, Any]:
    """分页列出 data_pool 序列。返回 `{"items": [...], "total": int}`。

    实施提示:
        url = f"{_base_url()}/api/v1/data-pool"
        params = {"page": page, "page_size": page_size}
        if data_type: params["data_type"] = data_type
        resp = requests.get(url, params=params, headers=_auth_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()
    """
    raise NotImplementedError("Pending: 环境就绪后填（无上游 issue 阻塞）")


def get_series(series_id: str) -> dict[str, Any]:
    """获取单条序列详情（含 values, timestamps, data_type, length）。"""
    raise NotImplementedError("Pending: 环境就绪后填")


# ---------------------------------------------------------------------------
# 结果
# ---------------------------------------------------------------------------

def get_results(
    series_id: str | None = None,
    *,
    page: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
    """查推理结果（含历史 raw_model_output 若 Issue 3 已合）。"""
    raise NotImplementedError("Pending: 环境就绪后填；raw_model_output 字段依赖 Issue 3")


def get_raw_model_output(result_id: int) -> str | None:
    """获取单次推理的原始 VL 输出文本（用于 robust_parser fixture 收集）。

    依赖 ts-platform Issue 3 实装（#4.3 raw_model_output DB 列 + API 暴露）。
    Issue 3 紧迫性已降（vllm_client 已 graceful 捕获），但持久化到 DB 仍需补。
    """
    raise NotImplementedError("Pending: ts-platform Issue 3（#4.3）实装")


# ---------------------------------------------------------------------------
# 健康检查（最简单的烟测，环境就绪后第一个能跑的函数）
# ---------------------------------------------------------------------------

def health() -> dict[str, Any]:
    """ts-platform 健康检查。环境就绪后用此函数烟测连通性。

    实施提示:
        url = f"{_base_url()}/api/v1/health"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    """
    raise NotImplementedError("Pending: 环境就绪后填（最先该填的，零依赖）")
