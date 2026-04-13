"""Golden statistics (CORP-03, D-12–D-15)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def compute_file_stats(path: Path, root: Path) -> dict[str, Any]:
    """Per-file stats: unicode chars, PDF pages, needs_ocr, table heuristics."""
    rel = path.relative_to(root).as_posix()
    suffix = path.suffix.lower()
    base: dict[str, Any] = {
        "path": rel,
        "suffix": suffix,
        "unicode_chars": 0,
    }

    if suffix in {".txt", ".md"}:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return {
                **base,
                "read_error": str(e),
                "unicode_chars": 0,
            }
        base["unicode_chars"] = len(text)
        return base

    if suffix == ".pdf":
        try:
            reader = PdfReader(str(path))
            page_count = len(reader.pages)
            extracted: list[str] = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    extracted.append(t)
            full_text = "".join(extracted)
            stripped = full_text.strip()
            needs_ocr = page_count > 0 and len(stripped) == 0
            return {
                **base,
                "page_count": page_count,
                "unicode_chars": len(full_text),
                "needs_ocr": needs_ocr,
            }
        except OSError as e:
            return {
                **base,
                "page_count_reason": f"os_error: {e}",
            }
        except Exception as e:  # noqa: BLE001 — pypdf may raise varied errors
            return {
                **base,
                "page_count_reason": f"pdf_error: {e}",
            }

    if suffix in {".xlsx", ".xls"}:
        return {
            **base,
            "table_count_heuristic": 1,
            "heuristic": True,
            "unicode_chars": 0,
        }

    base["skipped"] = True
    base["unicode_chars"] = 0
    return base


def aggregate_golden_stats(root: Path, files: list[Path]) -> dict[str, Any]:
    root = root.resolve()
    rows = [compute_file_stats(p, root) for p in files]
    total_chars = sum(int(r.get("unicode_chars", 0) or 0) for r in rows)
    needs_ocr_files = sum(1 for r in rows if r.get("needs_ocr") is True)
    return {
        "schema_version": "1.0",
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "total_files": len(rows),
            "total_unicode_chars": total_chars,
            "needs_ocr_files": needs_ocr_files,
        },
        "files": rows,
    }


def write_stats_json(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
