"""CLI tests for metrics command output contract."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from eval_corpus.cli import app
from eval_corpus.ir_models import BlockType, ParsedBlock

runner = CliRunner()


def _write_adapter_summary(path: Path) -> None:
    blocks = [
        ParsedBlock(
            type=BlockType.paragraph,
            text="第一段内容完整。",
            page=1,
            heading_path=["章节1"],
            parser_tool="paddle",
            source_file="a.pdf",
        ).model_dump(mode="json"),
        ParsedBlock(
            type=BlockType.table,
            text="A|B|C",
            page=2,
            heading_path=["表格"],
            parser_tool="paddle",
            source_file="a.pdf",
        ).model_dump(mode="json"),
    ]
    payload = {
        "tool": "paddle",
        "runtime_metadata": {"version": "test"},
        "results": [{"file": "a.pdf", "blocks": blocks}],
        "errors": [{"source_file": "a.pdf", "parser_tool": "paddle", "error": "sample"}],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_metrics_cli_success(tmp_path: Path) -> None:
    input_path = tmp_path / "adapt-summary.json"
    out_path = tmp_path / "metrics.json"
    _write_adapter_summary(input_path)

    result = runner.invoke(app, ["metrics", "--input", str(input_path), "--out", str(out_path)])
    assert result.exit_code == 0
    assert out_path.exists()

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert set(payload.keys()) == {"per_file", "per_tool", "overall"}
    assert payload["per_file"][0]["errors"] == 1
    assert "not_applicable" in payload["per_file"][0]

    metric = payload["per_file"][0]["metrics"]["METR-01"]
    assert "raw_value" in metric
    assert "threshold" in metric
    assert "level" in metric


def test_metrics_cli_missing_input_path() -> None:
    result = runner.invoke(
        app,
        ["metrics", "--input", "not-found.json", "--out", "out.json"],
    )
    assert result.exit_code == 2
    assert "Input file not found" in result.stdout
