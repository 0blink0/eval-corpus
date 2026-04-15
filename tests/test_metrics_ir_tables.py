"""METR-04 uses IR ParsedBlock table counts from adapter summary."""

from __future__ import annotations

import json
from pathlib import Path

from eval_corpus.metrics_io import build_metrics_artifact


def test_met_04_denominator_follows_ir_table_blocks(tmp_path: Path) -> None:
    blocks = [
        {
            "type": "paragraph",
            "text": "正文。",
            "page": 1,
            "heading_path": ["ROOT"],
            "parser_tool": "glm-ocr",
            "source_file": "x.pdf",
            "cells": None,
        },
        {
            "type": "table",
            "text": "| a | b |\n| --- | --- |\n| 1 | 2 |",
            "page": 1,
            "heading_path": ["ROOT"],
            "parser_tool": "glm-ocr",
            "source_file": "x.pdf",
            "cells": None,
        },
    ]
    summary = {
        "tool": "glm",
        "runtime_metadata": {},
        "results": [{"file": "x.pdf", "blocks": blocks}],
        "errors": [],
    }
    payload = build_metrics_artifact(summary)
    m04 = payload["per_file"][0]["metrics"]["METR-04"]
    assert m04["denominator"] == 1
    assert m04["raw_value"] == 1.0
    assert m04["numerator"] == 1
