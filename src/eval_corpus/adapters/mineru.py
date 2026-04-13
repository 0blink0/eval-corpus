"""MinerU adapter."""

from __future__ import annotations

from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.ir_models import BlockType, ParsedBlock


class MinerUAdapter:
    tool_name = "mineru"

    def get_runtime_metadata(self) -> RuntimeMetadata:
        ver = "unknown"
        try:
            import mineru  # type: ignore

            ver = getattr(mineru, "__version__", "unknown")
        except Exception:
            pass
        return RuntimeMetadata(tool_name=self.tool_name, tool_version=str(ver), model_id="mineru-default")

    def parse_to_blocks(self, file_path: Path, config: AdapterConfig) -> list[ParsedBlock]:
        if not file_path.exists():
            raise AdapterError(stage=AdapterStage.load, file=str(file_path), tool=self.tool_name, message="file not found")
        try:
            import mineru  # type: ignore # noqa: F401
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.load,
                file=str(file_path),
                tool=self.tool_name,
                message="mineru dependency not available",
                raw_error=repr(e) if config.debug else None,
            )
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.parse,
                file=str(file_path),
                tool=self.tool_name,
                message="failed reading input file",
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
