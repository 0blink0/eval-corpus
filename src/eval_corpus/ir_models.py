"""Pydantic v2 models for ParsedBlock and Chunk."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class BlockType(str, Enum):
    title = "title"
    paragraph = "paragraph"
    table = "table"
    other = "other"


class ParsedBlock(BaseModel):
    type: BlockType
    text: str
    page: int | None = None
    heading_path: list[str] = Field(default_factory=list)
    parser_tool: str = "unknown"
    source_file: str = "unknown"
    cells: list[list[str]] | None = None

    @model_validator(mode="after")
    def _validate_table_text(self) -> "ParsedBlock":
        if self.type == BlockType.table and not self.text.strip():
            raise ValueError("table block requires non-empty text")
        return self


class ChunkConfig(BaseModel):
    min_chars: int = 300
    max_chars: int = 1000
    overlap_ratio: float = 0.15

    @model_validator(mode="after")
    def _validate_ranges(self) -> "ChunkConfig":
        if self.min_chars <= 0:
            raise ValueError("min_chars must be > 0")
        if self.max_chars < self.min_chars:
            raise ValueError("max_chars must be >= min_chars")
        if not (0.10 <= self.overlap_ratio <= 0.20):
            raise ValueError("overlap_ratio must be in [0.10, 0.20]")
        return self


class Chunk(BaseModel):
    chunk_id: str
    text: str
    source_file: str
    page: int | None = None
    heading_path: list[str] = Field(default_factory=list)
    parser_tool: str = "unknown"
    block_types: list[BlockType] = Field(default_factory=list)
    page_span: tuple[int, int] | None = None
    overlap_truncated: bool = False
