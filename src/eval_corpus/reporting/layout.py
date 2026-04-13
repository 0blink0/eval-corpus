"""Run directory layout utilities for reporting workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RunLayout:
    root: Path
    by_tool_dir: Path
    by_artifact_dir: Path


def create_run_layout(*, base_dir: Path, run_id: str) -> RunLayout:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    root = base_dir / f"{run_id}-{timestamp}"
    by_tool_dir = root / "by_tool"
    by_artifact_dir = root / "by_artifact"
    by_tool_dir.mkdir(parents=True, exist_ok=True)
    by_artifact_dir.mkdir(parents=True, exist_ok=True)
    return RunLayout(root=root, by_tool_dir=by_tool_dir, by_artifact_dir=by_artifact_dir)


def ensure_tool_artifact_paths(
    *,
    layout: RunLayout,
    tools: list[str],
    artifact_types: list[str],
) -> list[Path]:
    created: list[Path] = []
    for tool in tools:
        for artifact_type in artifact_types:
            tool_first = layout.by_tool_dir / tool / artifact_type
            artifact_first = layout.by_artifact_dir / artifact_type / tool
            tool_first.mkdir(parents=True, exist_ok=True)
            artifact_first.mkdir(parents=True, exist_ok=True)
            created.append(tool_first)
            created.append(artifact_first)
    return created
