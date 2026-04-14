"""GLM-OCR adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.adapters.postprocess import markdown_to_blocks
from eval_corpus.ir_models import BlockType, ParsedBlock


def _extract_table_texts(payload: object) -> list[str]:
    """Extract table-like content from nested JSON payload."""
    found: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                key_l = str(key).lower()
                if key_l in {"table", "tables"}:
                    found.extend(_coerce_table_values(value))
                elif key_l in {"rows", "cells"} and isinstance(value, list):
                    table = _rows_to_markdown(value)
                    if table:
                        found.append(table)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    # keep order while deduplicating
    return list(dict.fromkeys(t.strip() for t in found if t and t.strip()))


def _coerce_table_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("markdown"), str):
                    out.append(str(item["markdown"]))
                elif isinstance(item.get("text"), str):
                    out.append(str(item["text"]))
                elif isinstance(item.get("html"), str):
                    out.append(str(item["html"]))
                rows = item.get("rows") or item.get("cells")
                if isinstance(rows, list):
                    table = _rows_to_markdown(rows)
                    if table:
                        out.append(table)
        return out
    if isinstance(value, dict):
        rows = value.get("rows") or value.get("cells")
        if isinstance(rows, list):
            table = _rows_to_markdown(rows)
            if table:
                return [table]
    return []


def _rows_to_markdown(rows: list[object]) -> str:
    normalized: list[list[str]] = []
    for row in rows:
        if isinstance(row, list):
            cells = [str(c).strip() for c in row]
            if any(cells):
                normalized.append(cells)
    if not normalized:
        return ""
    width = max(len(r) for r in normalized)
    padded = [r + [""] * (width - len(r)) for r in normalized]
    header = padded[0]
    sep = ["---"] * width
    body = padded[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    lines.extend("| " + " | ".join(r) + " |" for r in body)
    return "\n".join(lines)


class GLMAdapter:
    tool_name = "glm-ocr"

    def get_runtime_metadata(self) -> RuntimeMetadata:
        sdk_ver = "unknown"
        try:
            import zhipuai  # type: ignore

            sdk_ver = getattr(zhipuai, "__version__", "unknown")
        except Exception:
            pass
        return RuntimeMetadata(tool_name=self.tool_name, tool_version=str(sdk_ver), model_id="glm-ocr")

    def parse_to_blocks(self, file_path: Path, config: AdapterConfig) -> list[ParsedBlock]:
        if not file_path.exists():
            raise AdapterError(stage=AdapterStage.load, file=str(file_path), tool=self.tool_name, message="file not found")
        api_key = os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise AdapterError(stage=AdapterStage.parse, file=str(file_path), tool=self.tool_name, message="missing GLM_API_KEY")
        os.environ.setdefault("ZHIPU_API_KEY", api_key)
        os.environ.setdefault("GLM_API_KEY", api_key)
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
            import glmocr  # type: ignore

            try:
                result = glmocr.parse(str(file_path), api_key=api_key)  # type: ignore[call-arg]
            except TypeError:
                result = glmocr.parse(str(file_path))
            text = ""
            for attr in ("markdown", "text", "content"):
                value = getattr(result, attr, None)
                if isinstance(value, str) and value.strip():
                    text = value
                    break
            if not text and hasattr(result, "to_markdown"):
                text = str(result.to_markdown() or "")
            structured_payload: object | None = None
            if hasattr(result, "to_json"):
                raw_json = result.to_json()
                if isinstance(raw_json, (dict, list)):
                    structured_payload = raw_json
                elif isinstance(raw_json, str):
                    raw_json_s = raw_json.strip()
                    if raw_json_s:
                        try:
                            structured_payload = json.loads(raw_json_s)
                        except Exception:
                            if not text:
                                text = raw_json_s
            text = text.strip()
            if not text:
                text = "[ocr-empty]"
            table_texts = _extract_table_texts(structured_payload) if structured_payload is not None else []
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.parse,
                file=str(file_path),
                tool=self.tool_name,
                message="glm ocr parse failed",
                raw_error=repr(e) if config.debug else None,
            )
        blocks = markdown_to_blocks(
            text,
            parser_tool=self.tool_name,
            source_file=str(file_path),
            page=1,
        )
        for t in table_texts:
            blocks.append(
                ParsedBlock(
                    type=BlockType.table,
                    text=t,
                    page=1,
                    heading_path=["ROOT"],
                    parser_tool=self.tool_name,
                    source_file=str(file_path),
                )
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
