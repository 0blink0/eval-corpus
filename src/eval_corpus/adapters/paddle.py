"""PaddleOCR adapter."""

from __future__ import annotations

from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.ir_models import BlockType, ParsedBlock


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
            pages = ocr.ocr(str(file_path), cls=True)
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
            for line in page or []:
                text = ""
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    recog = line[1]
                    if isinstance(recog, (list, tuple)) and recog:
                        text = str(recog[0] or "").strip()
                if not text:
                    continue
                blocks.append(
                    ParsedBlock(
                        type=BlockType.paragraph,
                        text=text,
                        page=page_idx,
                        heading_path=[],
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
