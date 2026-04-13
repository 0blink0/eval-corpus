"""Data models for synthetic corpus generation."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

MAX_TOTAL_SAMPLES = 5000
MAX_TEXT_LENGTH = 10000


class SyntheticDataConfig(BaseModel):
    total_samples: int = Field(default=30, ge=3)
    min_text_length: int = Field(default=80, ge=20)
    max_text_length: int = Field(default=240, ge=20)
    type_ratio: dict[str, float] = Field(
        default_factory=lambda: {"text": 0.4, "scan": 0.3, "table": 0.3}
    )
    seed: int = 42

    @model_validator(mode="after")
    def _validate(self) -> "SyntheticDataConfig":
        if self.total_samples > MAX_TOTAL_SAMPLES:
            raise ValueError(f"total_samples must be <= {MAX_TOTAL_SAMPLES}")
        if self.max_text_length < self.min_text_length:
            raise ValueError("max_text_length must be >= min_text_length")
        if self.max_text_length > MAX_TEXT_LENGTH:
            raise ValueError(f"max_text_length must be <= {MAX_TEXT_LENGTH}")
        required = {"text", "scan", "table"}
        if set(self.type_ratio.keys()) != required:
            raise ValueError("type_ratio keys must be exactly: text, scan, table")
        if any(v < 0 for v in self.type_ratio.values()):
            raise ValueError("type_ratio values must be >= 0")
        total = sum(self.type_ratio.values())
        if total <= 0:
            raise ValueError("type_ratio sum must be > 0")
        return self


class SyntheticSample(BaseModel):
    sample_id: str
    sample_type: str
    relative_path: str


class SyntheticManifest(BaseModel):
    seed: int
    total_samples: int
    items: list[SyntheticSample]
