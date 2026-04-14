"""Shared block postprocessing helpers for parser adapters."""

from __future__ import annotations

import re
from typing import Iterable

from eval_corpus.ir_models import BlockType, ParsedBlock

_TABLE_SEP_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
_ROOT_HEADING = "ROOT"


def default_heading_path(heading_path: list[str] | None) -> list[str]:
    if heading_path:
        return heading_path
    return [_ROOT_HEADING]


def classify_line_block_type(text: str) -> BlockType:
    value = text.strip()
    if not value:
        return BlockType.other
    if _looks_like_table_row(value):
        return BlockType.table
    return BlockType.paragraph


def markdown_to_blocks(
    text: str,
    *,
    parser_tool: str,
    source_file: str,
    page: int | None = 1,
) -> list[ParsedBlock]:
    """Convert markdown-like text into structured ParsedBlock list."""
    lines = text.splitlines()
    blocks: list[ParsedBlock] = []
    heading_stack: list[str] = []
    para_buffer: list[str] = []
    table_buffer: list[str] = []

    def flush_paragraph() -> None:
        if not para_buffer:
            return
        paragraph = "\n".join(para_buffer).strip()
        para_buffer.clear()
        if not paragraph:
            return
        blocks.append(
            ParsedBlock(
                type=BlockType.paragraph,
                text=paragraph,
                page=page,
                heading_path=default_heading_path(heading_stack[:]),
                parser_tool=parser_tool,
                source_file=source_file,
            )
        )

    def flush_table() -> None:
        if not table_buffer:
            return
        table_text = "\n".join(table_buffer).strip()
        table_buffer.clear()
        if not table_text:
            return
        blocks.append(
            ParsedBlock(
                type=BlockType.table,
                text=table_text,
                page=page,
                heading_path=default_heading_path(heading_stack[:]),
                parser_tool=parser_tool,
                source_file=source_file,
            )
        )

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            flush_table()
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            flush_paragraph()
            flush_table()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            heading_stack[:] = heading_stack[: level - 1] + [title]
            blocks.append(
                ParsedBlock(
                    type=BlockType.title,
                    text=title,
                    page=page,
                    heading_path=default_heading_path(heading_stack[:]),
                    parser_tool=parser_tool,
                    source_file=source_file,
                )
            )
            continue

        if _looks_like_table_row(line) or _TABLE_SEP_RE.match(line):
            flush_paragraph()
            table_buffer.append(line)
            continue

        flush_table()
        para_buffer.append(line)

    flush_paragraph()
    flush_table()
    return blocks


def ensure_metadata_and_table_hints(blocks: Iterable[ParsedBlock]) -> list[ParsedBlock]:
    """Ensure heading_path defaults and table hints for line-style OCR output."""
    normalized: list[ParsedBlock] = []
    for b in blocks:
        if not b.heading_path:
            b.heading_path = [_ROOT_HEADING]
        if b.type != BlockType.table and _looks_like_table_row(b.text):
            b.type = BlockType.table
        normalized.append(b)
    return normalized


def _looks_like_table_row(text: str) -> bool:
    line = text.strip()
    if not line:
        return False
    if line.count("|") >= 2:
        return True
    if "\t" in line:
        cells = [c.strip() for c in line.split("\t")]
        return len([c for c in cells if c]) >= 2
    return False
