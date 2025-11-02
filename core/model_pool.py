from __future__ import annotations

import asyncio
import os
from typing import List

# Simple round-robin model pool with async safety.
# Models can be configured via:
# - Environment variable MODEL_POOL as a comma-separated list
# - Calling set_models([...]) programmatically

_MODELS: List[str] = [
    # "dashscope/qwen3-max",
    # "dashscope/qwen-flash",
    # "dashscope/qwen-plus-2025-07-28",
    # "dashscope/qwen-flash-2025-07-28",
    "dashscope/Moonshot-Kimi-K2-Instruct",
    # "dashscope/deepseek-v3.2-exp",
    # "dashscope/glm-4.5",
    # "deepseek/deepseek-chat",
    # "volcengine/deepseek-v3-1-terminus",
    # "volcengine/doubao-seed-1-6-lite-251015",
    # "volcengine/doubao-seed-1-6-flash-250828",
    # "volcengine/doubao-seed-1-6-251015",
    # "volcengine/kimi-k2-250905",
]
_idx: int = 0
_lock = asyncio.Lock()


def set_models(models: List[str]) -> None:
    """Configure the model pool programmatically.

    If called, this overrides any environment configuration.
    """
    global _MODELS, _idx
    cleaned = [m.strip() for m in models if m and m.strip()]
    if not cleaned:
        raise ValueError("models must contain at least one non-empty model name")
    _MODELS = cleaned
    _idx = 0


async def get_model() -> str:
    """Get the next model using round-robin selection.

    This function is async to be safe when called concurrently across tasks.
    """
    global _idx
    async with _lock:
        m = _MODELS[_idx % len(_MODELS)]
        _idx = (_idx + 1) % len(_MODELS)
        return m
