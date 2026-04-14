"""GLM-OCR adapter."""

from __future__ import annotations

import os
from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.ir_models import BlockType, ParsedBlock


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
            blocks = [
                ParsedBlock(
                    type=BlockType.paragraph,
                    text=text.strip() or "[empty]",
                    page=1,
                    heading_path=[],
                    parser_tool=self.tool_name,
                    source_file=str(file_path),
                )
            ]
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
            if not text and hasattr(result, "to_json"):
                text = str(result.to_json() or "")
            text = text.strip()
            if not text:
                text = "[ocr-empty]"
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.parse,
                file=str(file_path),
                tool=self.tool_name,
                message="glm ocr parse failed",
                raw_error=repr(e) if config.debug else None,
            )
        blocks = [
            ParsedBlock(
                type=BlockType.paragraph,
                text=text,
                page=1,
                heading_path=[],
                parser_tool=self.tool_name,
                source_file=str(file_path),
            )
        ]
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
