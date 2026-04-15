"""MinerU adapter."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError, AdapterStage, RuntimeMetadata, ensure_lowest_semantics
from eval_corpus.adapters.postprocess import (
    ensure_metadata_and_table_hints,
    extract_html_tables_as_markdown,
    markdown_to_blocks,
)
from eval_corpus.ir_models import BlockType, ParsedBlock


def _build_mineru_cmd(file_path: Path, out_dir: str) -> list[str]:
    """Resolve CLI: optional ``EVAL_MINERU_CMD`` (shlex), else ``mineru``, else ``magic-pdf``."""
    custom = os.getenv("EVAL_MINERU_CMD", "").strip()
    if custom:
        parts = shlex.split(custom)
        return [p.replace("%INPUT%", str(file_path)).replace("%OUTPUT%", out_dir) for p in parts]
    exe = os.getenv("EVAL_MINERU_EXECUTABLE", "").strip()
    if exe:
        cmd = [exe, "-p", str(file_path), "-o", out_dir]
        base = os.path.basename(exe).lower()
        if "magic" in base and "-m" not in os.getenv("EVAL_MINERU_EXTRA_ARGS", ""):
            cmd.extend(["-m", os.getenv("EVAL_MINERU_METHOD", "auto")])
        extra = shlex.split(os.getenv("EVAL_MINERU_EXTRA_ARGS", ""))
        return cmd + extra
    w = shutil.which("mineru")
    if w:
        return [w, "-p", str(file_path), "-o", out_dir]
    w2 = shutil.which("magic-pdf")
    if w2:
        return [w2, "-p", str(file_path), "-o", out_dir, "-m", os.getenv("EVAL_MINERU_METHOD", "auto")]
    raise RuntimeError("neither mineru nor magic-pdf found on PATH; install MinerU or set EVAL_MINERU_CMD")


def _mineru_runtime_available() -> bool:
    try:
        import mineru  # type: ignore # noqa: F401

        return True
    except Exception:
        pass
    if os.getenv("EVAL_MINERU_CMD", "").strip():
        return True
    return bool(shutil.which("mineru") or shutil.which("magic-pdf"))


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
                raw = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                raise AdapterError(
                    stage=AdapterStage.parse,
                    file=str(file_path),
                    tool=self.tool_name,
                    message="failed reading text input file",
                    raw_error=repr(e) if config.debug else None,
                )
            body, html_tabs = extract_html_tables_as_markdown(raw.strip() or "[empty]")
            blocks = markdown_to_blocks(
                body,
                parser_tool=self.tool_name,
                source_file=str(file_path),
                page=1,
            )
            for t in html_tabs:
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
                return ensure_lowest_semantics(ensure_metadata_and_table_hints(blocks))
            except Exception as e:
                raise AdapterError(
                    stage=AdapterStage.validate,
                    file=str(file_path),
                    tool=self.tool_name,
                    message="normalized output failed schema validation",
                    raw_error=repr(e) if config.debug else None,
                )
        if not _mineru_runtime_available():
            raise AdapterError(
                stage=AdapterStage.load,
                file=str(file_path),
                tool=self.tool_name,
                message="mineru CLI not available (install mineru/magic-pdf or set EVAL_MINERU_CMD)",
            )
        try:
            # Large PDFs exceed the default AdapterConfig timeout (30s); allow override via env.
            timeout_sec = int(os.getenv("EVAL_MINERU_TIMEOUT_SEC", str(max(config.timeout_sec, 7200))))
            with tempfile.TemporaryDirectory(prefix="mineru-") as temp_out:
                cmd = _build_mineru_cmd(file_path, temp_out)
                proc = subprocess.run(
                    cmd,
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
        body, html_tabs = extract_html_tables_as_markdown(text.strip() or "[empty]")
        blocks = markdown_to_blocks(
            body,
            parser_tool=self.tool_name,
            source_file=str(file_path),
            page=1,
        )
        for t in html_tabs:
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
            return ensure_lowest_semantics(ensure_metadata_and_table_hints(blocks))
        except Exception as e:
            raise AdapterError(
                stage=AdapterStage.validate,
                file=str(file_path),
                tool=self.tool_name,
                message="normalized output failed schema validation",
                raw_error=repr(e) if config.debug else None,
            )
