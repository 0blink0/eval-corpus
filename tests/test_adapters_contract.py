"""Contract tests for adapters and runner policies."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapter_runner import run_adapter_on_files
from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage
from eval_corpus.adapters.registry import get_adapter
from eval_corpus.ir_models import BlockType, ParsedBlock


def test_adapter_contract_and_error_schema(tmp_path: Path) -> None:
    cfg = AdapterConfig(debug=True)
    assert cfg.timeout_sec > 0
    err = AdapterError(
        stage=AdapterStage.load,
        file=str(tmp_path / "x.pdf"),
        tool="paddleocr",
        message="boom",
    )
    data = err.to_dict()
    assert data["stage"] == "load"
    with pytest.raises(Exception):
        AdapterError(stage="bad", file="x", tool="t", message="m")  # type: ignore[arg-type]


def test_runner_continue_and_fail_fast(tmp_path: Path) -> None:
    f1 = tmp_path / "ok.txt"
    f2 = tmp_path / "missing.txt"
    f1.write_text("hello", encoding="utf-8")

    out1 = run_adapter_on_files("paddle", [f1, f2], fail_fast=False, debug=False)
    assert isinstance(out1["runtime_metadata"], dict)
    assert len(out1["errors"]) >= 1

    out2 = run_adapter_on_files("paddle", [f2, f1], fail_fast=True, debug=False)
    assert len(out2["errors"]) == 1


def test_glm_in_runner_modes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    monkeypatch.delenv("GLM_API_KEY", raising=False)
    out = run_adapter_on_files("glm", [f], fail_fast=False, debug=False)
    assert out["errors"][0]["stage"] == "parse"


def test_three_tool_runtime_metadata_and_modes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    monkeypatch.delenv("GLM_API_KEY", raising=False)
    for tool in ["paddle", "glm", "mineru"]:
        res = run_adapter_on_files(tool, [f], fail_fast=False, debug=True)
        meta = res["runtime_metadata"]
        assert "tool_name" in meta and "tool_version" in meta and "model_id" in meta


def test_cross_tool_minimal_fixture_acceptance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    text = tmp_path / "text.txt"
    scan = tmp_path / "scan.txt"
    table = tmp_path / "table.txt"
    text.write_text("hello", encoding="utf-8")
    scan.write_text("scan", encoding="utf-8")
    table.write_text("a|b", encoding="utf-8")
    monkeypatch.delenv("GLM_API_KEY", raising=False)

    files = [text, scan, table]
    for tool in ["paddle", "glm", "mineru"]:
        res = run_adapter_on_files(tool, files, fail_fast=False, debug=False)
        assert len(res["results"]) + len(res["errors"]) == 3
        for r in res["results"]:
            blocks = r["blocks"]
            assert isinstance(blocks, list)
            if blocks:
                assert blocks[0]["type"] in {e.value for e in BlockType}
                assert "text" in blocks[0]
