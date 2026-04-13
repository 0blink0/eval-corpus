"""CLI tests for chunk command and fixture roundtrip."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from eval_corpus.cli import app


def test_chunk_command_roundtrip(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/chunking/manual_blocks.json")
    out = tmp_path / "chunks.json"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "chunk",
            "--blocks-in",
            str(fixture),
            "--chunks-out",
            str(out),
            "--min-chars",
            "10",
            "--max-chars",
            "30",
            "--overlap-ratio",
            "0.15",
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert len(data["chunks"]) >= 2
    first = data["chunks"][0]
    assert "heading_path" in first
    assert "parser_tool" in first


def test_chunk_command_invalid_overlap_ratio(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/chunking/manual_blocks.json")
    out = tmp_path / "chunks.json"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "chunk",
            "--blocks-in",
            str(fixture),
            "--chunks-out",
            str(out),
            "--overlap-ratio",
            "0.9",
        ],
    )
    assert result.exit_code == 2
    assert "overlap-ratio" in result.output
