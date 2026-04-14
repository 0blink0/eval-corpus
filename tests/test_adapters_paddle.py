"""Paddle adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.paddle import PaddleAdapter, _detect_table_line_indexes


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


def test_paddle_table_detection_from_bbox_rows() -> None:
    entries = [
        {"text": "供应项目名称", "bbox": (10.0, 10.0, 110.0, 28.0)},
        {"text": "保温杯", "bbox": (150.0, 10.0, 320.0, 28.0)},
        {"text": "采购人名称", "bbox": (10.0, 36.0, 110.0, 54.0)},
        {"text": "北京市石景山区", "bbox": (150.0, 36.0, 320.0, 54.0)},
        {"text": "采购人地址", "bbox": (10.0, 62.0, 110.0, 80.0)},
        {"text": "北京市石景山区15号", "bbox": (150.0, 62.0, 320.0, 80.0)},
    ]
    table_idx = _detect_table_line_indexes(entries)
    assert table_idx == {0, 1, 2, 3, 4, 5}
