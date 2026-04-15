"""MinerU adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.mineru import MinerUAdapter, _build_mineru_cmd
from eval_corpus.ir_models import BlockType


def test_mineru_cmd_falls_back_to_magic_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_MINERU_CMD", raising=False)
    monkeypatch.delenv("EVAL_MINERU_EXECUTABLE", raising=False)

    def _which(name: str) -> str | None:
        if name == "mineru":
            return None
        if name == "magic-pdf":
            return "/opt/bin/magic-pdf"
        return None

    monkeypatch.setattr("eval_corpus.adapters.mineru.shutil.which", _which)
    cmd = _build_mineru_cmd(Path("/tmp/a.pdf"), "/out/dir")
    assert cmd[0] == "/opt/bin/magic-pdf"
    assert "-m" in cmd


def test_mineru_normalize_and_error_stage_mapping(tmp_path: Path) -> None:
    adapter = MinerUAdapter()
    with pytest.raises(AdapterError) as exc:
        adapter.parse_to_blocks(tmp_path / "none.txt", AdapterConfig(debug=False))
    assert exc.value.stage.value == "load"

    f = tmp_path / "a.txt"
    f.write_text("abc", encoding="utf-8")
    try:
        blocks = adapter.parse_to_blocks(f, AdapterConfig(debug=True))
        assert len(blocks) >= 1
        assert blocks[0].parser_tool == "mineru"
    except AdapterError as e:
        assert e.stage.value in {"load", "parse", "validate"}


def test_mineru_text_input_extracts_html_tables(tmp_path: Path) -> None:
    f = tmp_path / "x.md"
    f.write_text(
        "前文<table><tr><td>p</td><td>q</td></tr></table>后文",
        encoding="utf-8",
    )
    blocks = MinerUAdapter().parse_to_blocks(f, AdapterConfig(debug=True))
    assert any(b.type == BlockType.table and "p" in b.text for b in blocks)
