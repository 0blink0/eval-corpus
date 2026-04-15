"""MinerU adapter."""

from __future__ import annotations

import io
import json
import http.client
import os
import shlex
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
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


def _http_json(
    *,
    method: str,
    url: str,
    timeout_sec: int,
    headers: dict[str, str] | None = None,
    payload: dict | None = None,
) -> dict:
    body: bytes | None = None
    req_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url=url, data=body, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw) if raw.strip() else {}


def _http_put_file(url: str, file_path: Path, timeout_sec: int) -> None:
    # Use low-level HTTP client to avoid urllib auto-adding Content-Type,
    # which can break OSS pre-signed URL signature verification.
    u = urllib.parse.urlsplit(url)
    conn_cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(u.netloc, timeout=timeout_sec)
    path = u.path + (f"?{u.query}" if u.query else "")
    data = file_path.read_bytes()
    try:
        conn.putrequest("PUT", path)
        conn.putheader("Content-Length", str(len(data)))
        conn.endheaders()
        conn.send(data)
        resp = conn.getresponse()
        if not (200 <= resp.status < 300):
            body = resp.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"upload failed: HTTP {resp.status} {body}")
    finally:
        conn.close()


def _http_get_bytes(url: str, timeout_sec: int) -> bytes:
    req = urllib.request.Request(url=url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        return resp.read()


def _extract_md_from_mineru_zip(zip_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        prefer = [n for n in names if n.lower().endswith("/full.md") or n.lower() == "full.md"]
        if prefer:
            return zf.read(prefer[0]).decode("utf-8", errors="replace")
        md_names = [n for n in names if n.lower().endswith(".md")]
        if not md_names:
            raise RuntimeError("mineru zip does not contain markdown output")
        return zf.read(md_names[0]).decode("utf-8", errors="replace")


def _parse_via_api(file_path: Path, config: AdapterConfig) -> str:
    token = os.getenv("EVAL_MINERU_API_TOKEN") or os.getenv("MINERU_API_TOKEN")
    if not token:
        raise RuntimeError("missing MINERU_API_TOKEN")

    base = os.getenv("EVAL_MINERU_API_BASE", "https://mineru.net").rstrip("/")
    model_version = os.getenv("EVAL_MINERU_MODEL_VERSION", "vlm")
    language = os.getenv("EVAL_MINERU_LANGUAGE", "ch")
    enable_table = os.getenv("EVAL_MINERU_ENABLE_TABLE", "true").lower() not in {"0", "false", "no"}
    enable_formula = os.getenv("EVAL_MINERU_ENABLE_FORMULA", "true").lower() not in {"0", "false", "no"}
    is_ocr = os.getenv("EVAL_MINERU_IS_OCR", "false").lower() in {"1", "true", "yes"}
    page_ranges = os.getenv("EVAL_MINERU_PAGE_RANGES", "").strip()

    timeout_sec = int(os.getenv("EVAL_MINERU_TIMEOUT_SEC", str(max(config.timeout_sec, 7200))))
    poll_timeout_sec = int(os.getenv("EVAL_MINERU_API_POLL_TIMEOUT_SEC", str(max(timeout_sec, 1200))))
    poll_interval_sec = int(os.getenv("EVAL_MINERU_API_POLL_INTERVAL_SEC", "3"))

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "*/*",
    }

    # 1) Apply upload URL by batch endpoint (supports local file upload).
    create_payload = {
        "files": [{"name": file_path.name}],
        "model_version": model_version,
        "language": language,
        "enable_table": enable_table,
        "enable_formula": enable_formula,
    }
    if is_ocr:
        create_payload["files"][0]["is_ocr"] = True
    if page_ranges:
        create_payload["files"][0]["page_ranges"] = page_ranges

    create_resp = _http_json(
        method="POST",
        url=f"{base}/api/v4/file-urls/batch",
        timeout_sec=timeout_sec,
        headers=headers,
        payload=create_payload,
    )
    if int(create_resp.get("code", -1)) != 0:
        raise RuntimeError(f"mineru create upload urls failed: {create_resp}")
    data = create_resp.get("data") or {}
    batch_id = str(data.get("batch_id") or "")
    file_urls = data.get("file_urls") or []
    if not batch_id or not file_urls:
        raise RuntimeError(f"mineru create upload urls missing batch_id/file_urls: {create_resp}")

    # 2) Upload file.
    _http_put_file(str(file_urls[0]), file_path, timeout_sec=timeout_sec)

    # 3) Poll batch result until done.
    deadline = time.time() + poll_timeout_sec
    full_zip_url = ""
    while time.time() < deadline:
        poll_resp = _http_json(
            method="GET",
            url=f"{base}/api/v4/extract-results/batch/{batch_id}",
            timeout_sec=min(120, timeout_sec),
            headers=headers,
            payload=None,
        )
        if int(poll_resp.get("code", -1)) != 0:
            raise RuntimeError(f"mineru poll failed: {poll_resp}")
        rows = (poll_resp.get("data") or {}).get("extract_result") or []
        row = rows[0] if rows else {}
        state = str(row.get("state", ""))
        if state == "done":
            full_zip_url = str(row.get("full_zip_url", "")).strip()
            if not full_zip_url:
                raise RuntimeError(f"mineru done but full_zip_url missing: {poll_resp}")
            break
        if state == "failed":
            raise RuntimeError(f"mineru task failed: {row.get('err_msg') or row}")
        time.sleep(max(1, poll_interval_sec))

    if not full_zip_url:
        raise RuntimeError("mineru polling timeout before task done")

    # 4) Download zip and read markdown.
    zbytes = _http_get_bytes(full_zip_url, timeout_sec=timeout_sec)
    return _extract_md_from_mineru_zip(zbytes)


class MinerUAdapter:
    tool_name = "mineru"

    def get_runtime_metadata(self) -> RuntimeMetadata:
        ver = "unknown"
        try:
            import mineru  # type: ignore

            ver = getattr(mineru, "__version__", "unknown")
        except Exception:
            pass
        mode = os.getenv("EVAL_MINERU_MODE", "api").strip().lower()
        model_id = f"mineru-{os.getenv('EVAL_MINERU_MODEL_VERSION', 'vlm')}" if mode == "api" else "mineru-default"
        return RuntimeMetadata(tool_name=self.tool_name, tool_version=str(ver), model_id=model_id)

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
        try:
            mode = os.getenv("EVAL_MINERU_MODE", "api").strip().lower()
            if mode == "api":
                text = _parse_via_api(file_path, config)
            else:
                if not _mineru_runtime_available():
                    raise RuntimeError("mineru CLI not available (install mineru/magic-pdf or set EVAL_MINERU_CMD)")
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
