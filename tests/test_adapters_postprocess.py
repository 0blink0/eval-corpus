from __future__ import annotations

from eval_corpus.adapters.postprocess import markdown_to_blocks
from eval_corpus.ir_models import BlockType


def test_markdown_to_blocks_extracts_table_and_heading_path() -> None:
    text = """# 第一章
概览说明

| 列A | 列B |
| --- | --- |
| 1 | 2 |
"""
    blocks = markdown_to_blocks(text, parser_tool="glm-ocr", source_file="a.pdf", page=1)
    assert any(b.type == BlockType.table for b in blocks)
    assert all(b.heading_path for b in blocks if b.text.strip())


def test_markdown_to_blocks_fallback_heading_path() -> None:
    blocks = markdown_to_blocks("普通文本一行", parser_tool="paddleocr", source_file="a.pdf", page=1)
    assert len(blocks) == 1
    assert blocks[0].heading_path == ["ROOT"]
