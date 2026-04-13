"""Core tests for IR models and chunker behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval_corpus.chunk_io import read_parsed_blocks_json
from eval_corpus.chunker import chunk_blocks
from eval_corpus.ir_models import BlockType, ChunkConfig, ParsedBlock


def test_parsed_block_schema() -> None:
    ok = ParsedBlock(type=BlockType.paragraph, text="你好", page=None)
    assert ok.page is None
    assert ok.parser_tool == "unknown"
    with pytest.raises(Exception):
        ParsedBlock(type=BlockType.table, text="")


def test_parsed_block_json_roundtrip(tmp_path: Path) -> None:
    src = tmp_path / "blocks.json"
    src.write_text(
        json.dumps([
            {
                "type": "paragraph",
                "text": "abc",
                "page": None,
                "heading_path": ["h1"],
                "source_file": "a.pdf",
            }
        ], ensure_ascii=False),
        encoding="utf-8",
    )
    blocks = read_parsed_blocks_json(src)
    assert len(blocks) == 1
    assert blocks[0].heading_path == ["h1"]
    assert blocks[0].source_file == "a.pdf"


def test_chunking_rules() -> None:
    blocks = [
        ParsedBlock(type=BlockType.title, text="标题。", page=1, source_file="x.pdf"),
        ParsedBlock(type=BlockType.paragraph, text="第一句。第二句。第三句。", page=1, source_file="x.pdf"),
        ParsedBlock(type=BlockType.table, text="a|b", page=2, source_file="x.pdf"),
    ]
    cfg = ChunkConfig(min_chars=3, max_chars=10, overlap_ratio=0.10)
    chunks = chunk_blocks(blocks, cfg)
    assert len(chunks) >= 2
    table_chunks = [c for c in chunks if BlockType.table in c.block_types]
    assert len(table_chunks) == 1
    assert table_chunks[0].text == "a|b"


def test_overlap_formula_and_truncation() -> None:
    blocks = [
        ParsedBlock(type=BlockType.paragraph, text="abcdef", page=1, source_file="x.pdf"),
        ParsedBlock(type=BlockType.paragraph, text="ghijkl", page=1, source_file="x.pdf"),
    ]
    cfg = ChunkConfig(min_chars=1, max_chars=6, overlap_ratio=0.2)
    chunks = chunk_blocks(blocks, cfg)
    assert len(chunks) >= 2
    first, second = chunks[0], chunks[1]
    expected = first.text[-2:] + "ghijkl"
    assert second.text.replace("\n", "") == expected[:7]



