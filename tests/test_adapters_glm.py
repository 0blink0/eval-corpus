"""GLM adapter tests."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.glm import GLMAdapter
from eval_corpus.ir_models import BlockType


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


def test_glm_extracts_tables_from_structured_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeResult:
        markdown = "正文段落"

        def to_json(self) -> str:
            return json.dumps({"tables": [{"rows": [["列1", "列2"], ["a", "b"]]}]}, ensure_ascii=False)

    fake_mod = types.SimpleNamespace(parse=lambda _p, api_key=None: _FakeResult())
    monkeypatch.setitem(sys.modules, "glmocr", fake_mod)
    monkeypatch.setenv("GLM_API_KEY", "dummy")

    f = tmp_path / "a.pdf"
    f.write_bytes(b"%PDF-1.4\n%fake\n")
    blocks = GLMAdapter().parse_to_blocks(f, AdapterConfig(debug=True))
    assert any(b.type == BlockType.table for b in blocks)
