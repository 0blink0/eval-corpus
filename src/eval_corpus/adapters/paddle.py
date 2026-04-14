"""PaddleOCR adapter."""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.adapters.postprocess import ensure_metadata_and_table_hints, markdown_to_blocks
from eval_corpus.ir_models import BlockType, ParsedBlock


def _poly_to_bbox(poly: object) -> tuple[float, float, float, float] | None:
    if not isinstance(poly, (list, tuple)) or not poly:
        return None
    xs: list[float] = []
    ys: list[float] = []
    for p in poly:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                xs.append(float(p[0]))
                ys.append(float(p[1]))
            except (TypeError, ValueError):
                continue
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _detect_table_line_indexes(entries: list[dict[str, Any]]) -> set[int]:
    """Detect likely table lines via row grouping + multi-column signal."""
    boxed = [(i, e["bbox"]) for i, e in enumerate(entries) if e.get("bbox") is not None]
    if len(boxed) < 6:
        return set()
    heights = [b[3] - b[1] for _, b in boxed]
    median_h = statistics.median(h for h in heights if h > 0) if any(h > 0 for h in heights) else 10.0
    row_tol = max(6.0, median_h * 0.6)

    rows: list[list[tuple[int, tuple[float, float, float, float]]]] = []
    for idx, bbox in boxed:
        y_mid = (bbox[1] + bbox[3]) / 2
        placed = False
        for row in rows:
            row_y = statistics.mean((b[1] + b[3]) / 2 for _, b in row)
            if abs(y_mid - row_y) <= row_tol:
                row.append((idx, bbox))
                placed = True
                break
        if not placed:
            rows.append([(idx, bbox)])

    candidate_rows: list[list[tuple[int, tuple[float, float, float, float]]]] = []
    for row in rows:
        if len(row) < 2:
            continue
        row_sorted = sorted(row, key=lambda t: t[1][0])
        # Require visible horizontal separation between adjacent cells.
        gaps = [row_sorted[i + 1][1][0] - row_sorted[i][1][2] for i in range(len(row_sorted) - 1)]
        if any(g > 6.0 for g in gaps):
            candidate_rows.append(row_sorted)

    if len(candidate_rows) < 3:
        return set()
    return {idx for row in candidate_rows for idx, _ in row}


def _run_paddle_ocr(ocr: object, file_path: Path) -> list | None:
    """PaddleOCR v2 returns nested lists from ``ocr()``; v3+ uses ``predict()`` + OCRResult."""
    path = str(file_path)
    if hasattr(ocr, "predict"):
        try:
            raw = ocr.predict(input=path)  # type: ignore[no-untyped-call]
        except TypeError:
            try:
                raw = ocr.predict(path)  # type: ignore[no-untyped-call]
            except TypeError:
                raw = ocr.predict([path])  # type: ignore[no-untyped-call]
        if raw is None:
            return []
        pages_out: list[list] = []
        seq = raw if isinstance(raw, (list, tuple)) else [raw]
        for res in seq:
            texts = getattr(res, "rec_texts", None)
            polys = getattr(res, "rec_polys", None) or getattr(res, "dt_polys", None)
            if not texts:
                td = getattr(res, "to_dict", None)
                if callable(td):
                    try:
                        d = td()
                        if isinstance(d, dict):
                            texts = d.get("rec_texts") or d.get("texts")
                            polys = polys or d.get("rec_polys") or d.get("dt_polys")
                    except Exception:
                        texts = None
            line_items: list = []
            for i, t in enumerate(texts or []):
                ts = str(t).strip()
                if ts:
                    poly = polys[i] if isinstance(polys, (list, tuple)) and i < len(polys) else []
                    line_items.append([poly, (ts, 1.0)])
            pages_out.append(line_items)
        return pages_out
    return ocr.ocr(path, cls=True)  # type: ignore[no-any-return]


class PaddleAdapter:
    tool_name = "paddleocr"

    def get_runtime_metadata(self) -> RuntimeMetadata:
        ver = "unknown"
        try:
            import paddleocr  # type: ignore

            ver = getattr(paddleocr, "__version__", "unknown")
        except Exception:
            pass
        return RuntimeMetadata(tool_name=self.tool_name, tool_version=str(ver), model_id="paddle-default")

    def parse_to_blocks(self, file_path: Path, config: AdapterConfig) -> list[ParsedBlock]:
        if not file_path.exists():
            raise AdapterError(stage=AdapterStage.load, file=str(file_path), tool=self.tool_name, message="file not found")
        if file_path.suffix.lower() in {".txt", ".md", ".csv", ".json"}:
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                raise AdapterError(
                    stage=AdapterStage.parse,
                    file=str(file_path),
                    tool=self.tool_name,
                    message="failed reading text input file",
                    raw_error=repr(e) if config.debug else None,
                )
            blocks = markdown_to_blocks(
                text.strip() or "[empty]",
                parser_tool=self.tool_name,
                source_file=str(file_path),
                page=1,
            )
            try:
                return ensure_lowest_semantics(blocks)
            except Exception as e:
                raise AdapterError(
                    stage=AdapterStage.validate,
                    file=str(file_path),
                    tool=self.tool_name,
                    message="normalized output failed schema validation",
                    raw_error=repr(e) if config.debug else None,
                )
        try:
            from paddleocr import PaddleOCR  # type: ignore
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.load,
                file=str(file_path),
                tool=self.tool_name,
                message="paddleocr dependency not available",
                raw_error=repr(e) if config.debug else None,
            )
        try:
            ocr = PaddleOCR(use_angle_cls=True, lang="ch")
            pages = _run_paddle_ocr(ocr, file_path)
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.parse,
                file=str(file_path),
                tool=self.tool_name,
                message="paddleocr parse failed",
                raw_error=repr(e) if config.debug else None,
            )
        blocks: list[ParsedBlock] = []
        for page_idx, page in enumerate(pages or [], start=1):
            page_entries: list[dict[str, Any]] = []
            for line in page or []:
                text = ""
                bbox: tuple[float, float, float, float] | None = None
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    bbox = _poly_to_bbox(line[0]) if len(line) >= 1 else None
                    recog = line[1]
                    if isinstance(recog, (list, tuple)) and recog:
                        text = str(recog[0] or "").strip()
                if not text:
                    continue
                page_entries.append({"text": text, "bbox": bbox})
            table_line_indexes = _detect_table_line_indexes(page_entries)
            for i, e in enumerate(page_entries):
                blocks.append(
                    ParsedBlock(
                        type=BlockType.table if i in table_line_indexes else BlockType.paragraph,
                        text=e["text"],
                        page=page_idx,
                        heading_path=["ROOT"],
                        parser_tool=self.tool_name,
                        source_file=str(file_path),
                    )
                )
        if not blocks:
            blocks = [
                ParsedBlock(
                    type=BlockType.other,
                    text="[ocr-empty]",
                    page=1,
                    heading_path=["ROOT"],
                    parser_tool=self.tool_name,
                    source_file=str(file_path),
                )
            ]
        try:
            return ensure_lowest_semantics(ensure_metadata_and_table_hints(blocks))
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.validate,
                file=str(file_path),
                tool=self.tool_name,
                message="normalized output failed schema validation",
                raw_error=repr(e) if config.debug else None,
            )
