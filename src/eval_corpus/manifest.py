"""Manifest JSON builder (D-05–D-07)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_manifest_payload(
    root: Path,
    files: list[Path],
    scan_errors: list[dict],
    unreadable_count: int,
) -> dict[str, Any]:
    root = root.resolve()
    entries: list[dict[str, Any]] = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            st = p.stat()
            size = st.st_size
        except OSError:
            size = -1
        entries.append(
            {
                "path": rel,
                "size_bytes": size,
                "suffix": p.suffix.lower(),
            }
        )
    return {
        "schema_version": "1.0",
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": entries,
        "scan_errors": scan_errors,
        "unreadable_count": unreadable_count,
    }


def write_manifest(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
