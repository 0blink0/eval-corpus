"""Adapter contracts and shared types."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field, field_validator

from eval_corpus.ir_models import ParsedBlock


class AdapterStage(str, Enum):
    load = "load"
    parse = "parse"
    normalize = "normalize"
    validate = "validate"


class AdapterError(Exception):
    def __init__(
        self,
        *,
        stage: AdapterStage,
        file: str,
        tool: str,
        message: str,
        raw_error: str | None = None,
    ) -> None:
        super().__init__(message)
        if isinstance(stage, str):
            stage = AdapterStage(stage)
        self.stage = stage
        self.file = file
        self.tool = tool
        self.message = message
        self.raw_error = raw_error

    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "file": self.file,
            "tool": self.tool,
            "message": self.message,
            "raw_error": self.raw_error,
        }


class AdapterConfig(BaseModel):
    debug: bool = False
    timeout_sec: int = 30

    @field_validator("timeout_sec")
    @classmethod
    def _positive_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("timeout_sec must be positive")
        return v


class RuntimeMetadata(BaseModel):
    tool_name: str
    tool_version: str
    model_id: str


class ParserAdapter(Protocol):
    tool_name: str

    def parse_to_blocks(self, file_path: Path, config: AdapterConfig) -> list[ParsedBlock]:
        ...

    def get_runtime_metadata(self) -> RuntimeMetadata:
        ...


def ensure_lowest_semantics(blocks: list[ParsedBlock]) -> list[ParsedBlock]:
    """Validate lowest common semantics required by D-33."""
    for b in blocks:
        # type field already constrained by ParsedBlock/BlockType
        if not b.text:
            raise ValueError("text is required")
        if b.heading_path is None:
            b.heading_path = []
    return blocks
