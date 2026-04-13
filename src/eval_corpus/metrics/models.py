"""Metric result and threshold contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

MetricLevel = Literal["pass", "warn", "fail"]


class MetricThreshold(BaseModel):
    warn_min: float = Field(ge=0.0, le=1.0)
    pass_min: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_order(self) -> "MetricThreshold":
        if self.warn_min > self.pass_min:
            raise ValueError("warn_min must be <= pass_min")
        return self


class MetricResult(BaseModel):
    metric_id: str
    raw_value: float | None = Field(default=None, ge=0.0, le=1.0)
    threshold: MetricThreshold
    level: MetricLevel
    numerator: int = Field(ge=0)
    denominator: int = Field(ge=0)
    excluded_count: int = Field(ge=0)
    applicable_count: int = Field(ge=0)
    total_count: int = Field(ge=0)
    not_applicable_reasons: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_counts(self) -> "MetricResult":
        if self.applicable_count > self.total_count:
            raise ValueError("applicable_count must be <= total_count")
        if self.excluded_count > self.total_count:
            raise ValueError("excluded_count must be <= total_count")
        if self.denominator < self.numerator:
            raise ValueError("denominator must be >= numerator")
        return self


def judge_level(raw_value: float | None, threshold: MetricThreshold) -> MetricLevel:
    """Classify raw value to pass/warn/fail.

    None is treated as fail and is expected to be explained by not_applicable_reasons.
    """
    if raw_value is None:
        return "fail"
    if raw_value >= threshold.pass_min:
        return "pass"
    if raw_value >= threshold.warn_min:
        return "warn"
    return "fail"
