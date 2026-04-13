"""Tests for manifest JSON."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from eval_corpus.cli import app


def test_build_manifest_via_cli(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "one.pdf").write_bytes(b"%PDF")
    (tmp_path / "two.txt").write_text("你好", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    runner = CliRunner(mix_stderr=False)
    out_file = tmp_path / "out.json"
    result = runner.invoke(
        app,
        [
            "manifest",
            "--root",
            str(tmp_path),
            "--manifest-out",
            str(out_file),
        ],
    )
    assert result.exit_code == 0, result.stdout + (result.stderr or "")
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0"
    assert "files" in data
    names = {f["path"] for f in data["files"]}
    assert names == {"one.pdf", "two.txt"}
    assert "files=" in result.stderr
