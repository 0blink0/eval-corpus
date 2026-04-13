"""Integration tests for reporting runtime/layout and CLI commands."""

from __future__ import annotations

import json
import re
from pathlib import Path

from typer.testing import CliRunner

from eval_corpus.cli import app
from eval_corpus.reporting.layout import create_run_layout, ensure_tool_artifact_paths
from eval_corpus.reporting.runtime import collect_runtime_metadata

runner = CliRunner()


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


def _metric(raw_value: float) -> dict[str, object]:
    return {
        "raw_value": raw_value,
        "threshold": {"warn_min": 0.7, "pass_min": 0.85},
        "level": "pass",
        "numerator": 9,
        "denominator": 10,
        "excluded_count": 0,
        "applicable_count": 10,
        "total_count": 10,
        "not_applicable_reasons": [],
    }


def _metrics_map() -> dict[str, dict[str, object]]:
    return {f"METR-0{i}": _metric(0.9) for i in range(1, 8)}


def _write_metrics_payload(path: Path) -> None:
    payload = {
        "per_file": [
            {
                "file": "sample/a.txt",
                "tool": "paddle",
                "errors": 0,
                "not_applicable": 0,
                "metrics": _metrics_map(),
            }
        ],
        "per_tool": [{"tool": "paddle", "metrics_summary": _metrics_map()}],
        "overall": {
            "generated_at": "2026-04-13T10:00:00Z",
            "metrics_summary": _metrics_map(),
            "runtime_metadata": {"tool_versions": {"paddle": "test"}},
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_report_command_writes_multi_format_outputs(tmp_path: Path) -> None:
    metrics_path = tmp_path / "metrics.json"
    out_dir = tmp_path / "runs"
    _write_metrics_payload(metrics_path)

    result = runner.invoke(
        app,
        ["report", "--input", str(metrics_path), "--out-dir", str(out_dir), "--run-id", "run-report"],
    )
    assert result.exit_code == 0
    run_dirs = [item for item in out_dir.iterdir() if item.is_dir()]
    assert len(run_dirs) == 1
    run_root = run_dirs[0]

    for ext in ("json", "csv", "md", "html"):
        assert (run_root / "by_artifact" / "reports" / "all" / f"report.{ext}").exists()


def test_batch_command_supports_recursive_and_worker_retry_flags(tmp_path: Path) -> None:
    source = tmp_path / "inputs"
    nested = source / "nested"
    nested.mkdir(parents=True)
    (nested / "a.txt").write_text("hello", encoding="utf-8")

    out_dir = tmp_path / "runs"
    result = runner.invoke(
        app,
        [
            "batch",
            "--input-dir",
            str(source),
            "--out-dir",
            str(out_dir),
            "--run-id",
            "run-batch",
            "--max-workers",
            "2",
            "--failure-threshold",
            "1.0",
            "--max-retries",
            "1",
        ],
    )
    assert result.exit_code == 0
    run_root = next(item for item in out_dir.iterdir() if item.is_dir())
    assert (run_root / "by_artifact" / "batch" / "all" / "batch_result.json").exists()


def test_synthetic_data_command_generates_three_types_for_batch(tmp_path: Path) -> None:
    out_dir = tmp_path / "runs"
    result = runner.invoke(
        app,
        [
            "synthetic-data",
            "--out-dir",
            str(out_dir),
            "--run-id",
            "run-synth",
            "--total-samples",
            "9",
            "--seed",
            "123",
        ],
    )
    assert result.exit_code == 0
    run_root = next(item for item in out_dir.iterdir() if item.is_dir())
    dataset_root = run_root / "by_artifact" / "synthetic_data" / "all" / "dataset"
    assert (dataset_root / "text").exists()
    assert (dataset_root / "scan").exists()
    assert (dataset_root / "table").exists()
