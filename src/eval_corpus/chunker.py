"""Unified chunking core: structural-first + sentence split + overlap."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from eval_corpus.ir_models import BlockType, Chunk, ChunkConfig, ParsedBlock

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])")


@dataclass
class _Segment:
    text: str
    blocks: list[ParsedBlock]
    is_table: bool


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    pieces = [p.strip() for p in _SENTENCE_SPLIT_RE.split(text) if p.strip()]
    return pieces if pieces else [text]


def _hard_cut(text: str, max_chars: int) -> list[str]:
    if not text:
        return []
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]


def _text_to_chunks(text: str, max_chars: int) -> list[str]:
    out: list[str] = []
    current = ""
    for sentence in _split_sentences(text):
        if len(sentence) > max_chars:
            if current:
                out.append(current)
                current = ""
            out.extend(_hard_cut(sentence, max_chars))
            continue
        candidate = sentence if not current else current + sentence
        if len(candidate) <= max_chars:
            current = candidate
        else:
            out.append(current)
            current = sentence
    if current:
        out.append(current)
    return out


def _segment_blocks(blocks: list[ParsedBlock], cfg: ChunkConfig) -> list[_Segment]:
    segments: list[_Segment] = []
    text_buf: list[ParsedBlock] = []

    def flush_text() -> None:
        nonlocal text_buf
        if not text_buf:
            return
        joined = "\n".join(b.text.strip() for b in text_buf if b.text.strip())
        if joined:
            segments.append(_Segment(text=joined, blocks=text_buf[:], is_table=False))
        text_buf = []

    for b in blocks:
        if b.type == BlockType.table:
            flush_text()
            segments.append(_Segment(text=b.text, blocks=[b], is_table=True))
        else:
            text_buf.append(b)
    flush_text()
    return segments


def _segment_meta(bs: list[ParsedBlock]) -> tuple[str, int | None, list[str], str, tuple[int, int] | None, list[BlockType]]:
    source_file = next((b.source_file for b in bs if b.source_file), "unknown")
    parser_tool = next((b.parser_tool for b in bs if b.parser_tool and b.parser_tool != "unknown"), "unknown")
    heading_path = next((b.heading_path for b in reversed(bs) if b.heading_path), [])
    pages = [b.page for b in bs if b.page is not None]
    page = min(pages) if pages else None
    page_span = (min(pages), max(pages)) if len(pages) >= 2 else None
    block_types = [b.type for b in bs]
    return source_file, page, heading_path, parser_tool, page_span, block_types


def _make_chunk(text: str, blocks: list[ParsedBlock], idx: int) -> Chunk:
    source_file, page, heading_path, parser_tool, page_span, block_types = _segment_meta(blocks)
    return Chunk(
        chunk_id=f"c{idx:04d}",
        text=text,
        source_file=source_file,
        page=page,
        heading_path=heading_path,
        parser_tool=parser_tool,
        page_span=page_span,
        block_types=block_types,
    )


def _apply_overlap(chunks: list[Chunk], ratio: float) -> None:
    for i in range(1, len(chunks)):
        prev = chunks[i - 1]
        cur = chunks[i]
        if BlockType.table in prev.block_types or BlockType.table in cur.block_types:
            continue
        need = math.ceil(ratio * len(cur.text))
        take = min(need, len(prev.text))
        if take <= 0:
            continue
        cur.text = prev.text[-take:] + cur.text
        cur.overlap_truncated = take < need


def chunk_blocks(blocks: list[ParsedBlock], cfg: ChunkConfig) -> list[Chunk]:
    segments = _segment_blocks(blocks, cfg)
    chunks: list[Chunk] = []
    idx = 1
    for seg in segments:
        if seg.is_table:
            chunks.append(_make_chunk(seg.text, seg.blocks, idx))
            idx += 1
            continue
        text_parts = _text_to_chunks(seg.text, cfg.max_chars)
        for t in text_parts:
            chunks.append(_make_chunk(t, seg.blocks, idx))
            idx += 1
    _apply_overlap(chunks, cfg.overlap_ratio)
    return chunks
