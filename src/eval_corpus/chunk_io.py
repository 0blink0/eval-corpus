"""JSON I/O boundary for ParsedBlock[] and Chunk[]."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from eval_corpus.ir_models import Chunk, ParsedBlock

_PARSED_BLOCKS_ADAPTER = TypeAdapter(list[ParsedBlock])
_CHUNKS_ADAPTER = TypeAdapter(list[Chunk])


def read_parsed_blocks_json(path: Path) -> list[ParsedBlock]:
    data = path.read_text(encoding="utf-8-sig")
    return _PARSED_BLOCKS_ADAPTER.validate_json(data)


def write_chunks_json(path: Path, chunks: list[Chunk]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [c.model_dump(mode="json") for c in chunks]
    doc = {
        "schema_version": "1.0",
        "chunks": payload,
    }
    path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def chunks_from_json_doc(data: str) -> list[Chunk]:
    parsed = json.loads(data)
    if isinstance(parsed, dict) and "chunks" in parsed:
        return _CHUNKS_ADAPTER.validate_python(parsed["chunks"])
    return _CHUNKS_ADAPTER.validate_python(parsed)

