"""MinerU adapter."""

from __future__ import annotations

import os
import subprocess
import tempfile
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
            # Large PDFs exceed the default AdapterConfig timeout (30s); allow override via env.
            timeout_sec = int(os.getenv("EVAL_MINERU_TIMEOUT_SEC", str(max(config.timeout_sec, 7200))))
            with tempfile.TemporaryDirectory(prefix="mineru-") as temp_out:
                proc = subprocess.run(
                    ["mineru", "-p", str(file_path), "-o", temp_out],
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    check=False,
                )
                if proc.returncode != 0:
                    raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "mineru cli failed")
                md_files = sorted(Path(temp_out).rglob("*.md"))
                if not md_files:
                    raise RuntimeError("mineru output markdown not found")
                text = "\n\n".join(p.read_text(encoding="utf-8", errors="replace") for p in md_files)
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.parse,
                file=str(file_path),
                tool=self.tool_name,
                message="mineru parse failed",
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
