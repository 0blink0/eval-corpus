"""Canonical reporting models shared by all exporters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from eval_corpus.metrics.models import MetricLevel, MetricThreshold

REQUIRED_METRICS: tuple[str, ...] = (
    "METR-01",
    "METR-02",
    "METR-03",
    "METR-04",
    "METR-05",
    "METR-06",
    "METR-07",
)


class ReportingStructureError(ValueError):
    """Raised when metrics artifact shape cannot be mapped to report model."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(f"{code}: {message}")


class MetricCell(BaseModel):
    raw_value: float | None = Field(default=None, ge=0.0, le=1.0)
    threshold: MetricThreshold
    level: MetricLevel
    numerator: int = Field(ge=0)
    denominator: int = Field(ge=0)
    excluded_count: int = Field(ge=0)
    applicable_count: int = Field(ge=0)
    total_count: int = Field(ge=0)
    not_applicable_reasons: list[str] = Field(default_factory=list)


class SummaryRow(BaseModel):
    row_key: str
    row_type: Literal["tool", "overall"]
    label: str
    metrics: dict[str, MetricCell]
    errors: int = Field(ge=0, default=0)
    not_applicable: int = Field(ge=0, default=0)


class DetailRow(BaseModel):
    file: str
    tool: str
    metrics: dict[str, MetricCell]
    errors: int = Field(ge=0, default=0)
    not_applicable: int = Field(ge=0, default=0)


class RuntimeAppendix(BaseModel):
    model_config = ConfigDict(extra="allow")

    generated_at: str
    tool_versions: dict[str, str] = Field(default_factory=dict)
    git_commit: str | None = None
    run_id: str | None = None
    git_status: str | None = None


class ReportPayload(BaseModel):
    summary_rows: list[SummaryRow]
    per_file_rows: list[DetailRow]
    runtime: RuntimeAppendix
    metric_order: list[str] = Field(default_factory=lambda: list(REQUIRED_METRICS))
