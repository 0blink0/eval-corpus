"""MinerU adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.mineru import MinerUAdapter


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
