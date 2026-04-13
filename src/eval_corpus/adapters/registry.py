"""Adapter registry."""

from __future__ import annotations

from eval_corpus.adapters.base import ParserAdapter
from eval_corpus.adapters.glm import GLMAdapter
from eval_corpus.adapters.mineru import MinerUAdapter
from eval_corpus.adapters.paddle import PaddleAdapter


def get_adapter(tool: str) -> ParserAdapter:
    t = tool.strip().lower()
    mapping = {
        "paddle": PaddleAdapter,
        "paddleocr": PaddleAdapter,
        "glm": GLMAdapter,
        "glm-ocr": GLMAdapter,
        "mineru": MinerUAdapter,
    }
    if t not in mapping:
        raise ValueError(f"Unsupported tool: {tool}")
    return mapping[t]()
