"""Integration tests for reporting runtime/layout and CLI commands."""

from __future__ import annotations

import re
from pathlib import Path

from eval_corpus.reporting.layout import create_run_layout, ensure_tool_artifact_paths
from eval_corpus.reporting.runtime import collect_runtime_metadata


def test_create_run_layout_builds_run_id_timestamp_and_dual_tree(tmp_path: Path) -> None:
    layout = create_run_layout(base_dir=tmp_path, run_id="run-001")

    assert layout.root.exists()
    assert layout.root.parent == tmp_path
    assert re.match(r"^run-001-\d{8}T\d{6}Z$", layout.root.name)

    paths = ensure_tool_artifact_paths(
        layout=layout,
        tools=["paddle", "glm"],
        artifact_types=["reports", "logs"],
    )
    assert (layout.by_tool_dir / "paddle" / "reports").exists()
    assert (layout.by_tool_dir / "glm" / "logs").exists()
    assert (layout.by_artifact_dir / "reports" / "paddle").exists()
    assert (layout.by_artifact_dir / "logs" / "glm").exists()
    assert len(paths) == 8


def test_collect_runtime_metadata_contains_required_keys_and_git_fallback() -> None:
    metadata = collect_runtime_metadata(run_id="run-002", repo_dir=Path("Z:/definitely-not-a-repo"))

    assert metadata["run_id"] == "run-002"
    assert isinstance(metadata["generated_at"], str)
    assert isinstance(metadata["tool_versions"], dict)
    assert "typer" in metadata["tool_versions"]
    assert "pydantic" in metadata["tool_versions"]
    assert "pytest" in metadata["tool_versions"]
    assert metadata["git_commit"] is None
    assert metadata["git_status"] == "unavailable"
