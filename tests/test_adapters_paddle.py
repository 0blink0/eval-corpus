"""Paddle adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.paddle import PaddleAdapter


def test_paddle_load_error_for_missing_file(tmp_path: Path) -> None:
    adapter = PaddleAdapter()
    with pytest.raises(AdapterError) as exc:
        adapter.parse_to_blocks(tmp_path / "no.txt", AdapterConfig(debug=False))
    assert exc.value.stage.value == "load"


def test_paddle_dependency_missing_or_success(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    adapter = PaddleAdapter()
    try:
        blocks = adapter.parse_to_blocks(f, AdapterConfig(debug=True))
        assert len(blocks) >= 1
        assert blocks[0].parser_tool == "paddleocr"
    except AdapterError as e:
        assert e.stage.value in {"load", "parse", "validate"}
