"""GLM adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.glm import GLMAdapter


def test_glm_normalizes_to_parsed_blocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    adapter = GLMAdapter()
    monkeypatch.setenv("GLM_API_KEY", "dummy")
    blocks = adapter.parse_to_blocks(f, AdapterConfig(debug=False))
    assert len(blocks) == 1
    assert blocks[0].parser_tool == "glm-ocr"


def test_glm_error_envelope_and_run_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    monkeypatch.delenv("GLM_API_KEY", raising=False)
    monkeypatch.delenv("ZHIPU_API_KEY", raising=False)
    adapter = GLMAdapter()
    with pytest.raises(AdapterError) as exc:
        adapter.parse_to_blocks(f, AdapterConfig(debug=False))
    err = exc.value
    assert err.stage.value == "parse"
    meta = adapter.get_runtime_metadata().model_dump(mode="json")
    assert "tool_name" in meta and "tool_version" in meta and "model_id" in meta
