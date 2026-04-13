"""Models for local batch execution."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BatchRunConfig:
    max_workers: int = 1
    continue_on_error: bool = True
    max_retries: int = 0
    failure_threshold: float = 1.0

    def __post_init__(self) -> None:
        if self.max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if not (0 <= self.failure_threshold <= 1):
            raise ValueError("failure_threshold must be in [0, 1]")


@dataclass(slots=True)
class BatchError:
    file: str
    message: str
    attempts: int


@dataclass(slots=True)
class BatchRunResult:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    retry_succeeded: int = 0
    aborted: bool = False
    termination_reason: str | None = None
    results: list[dict] = field(default_factory=list)
    errors: list[BatchError] = field(default_factory=list)
