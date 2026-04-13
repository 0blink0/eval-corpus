"""JSON I/O and orchestration helpers for metrics artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from eval_corpus.chunker import chunk_blocks
from eval_corpus.ir_models import ChunkConfig, ParsedBlock
from eval_corpus.metrics.aggregate import (
    build_overall_metrics,
    build_per_file_metrics,
    build_per_tool_metrics,
)

_PARSED_BLOCKS_ADAPTER = TypeAdapter(list[ParsedBlock])


def read_adapter_summary_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_metrics_artifact(adapter_summary: dict[str, Any]) -> dict[str, Any]:
    runtime_metadata = dict(adapter_summary.get("runtime_metadata", {}))
    all_chunks = []
    for item in adapter_summary.get("results", []):
        blocks = _PARSED_BLOCKS_ADAPTER.validate_python(item.get("blocks", []))
        all_chunks.extend(chunk_blocks(blocks, ChunkConfig()))

    per_file = build_per_file_metrics(
        all_chunks,
        errors=adapter_summary.get("errors", []),
    )
    per_tool = build_per_tool_metrics(per_file)
    overall = build_overall_metrics(
        per_file,
        per_tool,
        runtime_metadata=runtime_metadata,
    )
    payload = {
        "per_file": per_file,
        "per_tool": per_tool,
        "overall": overall,
    }
    _validate_metrics_payload(payload)
    return payload


def write_metrics_json(path: Path, payload: dict[str, Any]) -> None:
    _validate_metrics_payload(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _validate_metrics_payload(payload: dict[str, Any]) -> None:
    required = {"per_file", "per_tool", "overall"}
    if set(payload.keys()) != required:
        raise ValueError("metrics payload must contain per_file/per_tool/overall")
