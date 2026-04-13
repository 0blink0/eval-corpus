"""Tests for golden statistics."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from pypdf import PdfWriter
from typer.testing import CliRunner

from eval_corpus.cli import app
from eval_corpus.stats import aggregate_golden_stats, compute_file_stats


def _minimal_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_text_file_unicode_char_count(tmp_path: Path) -> None:
    f = tmp_path / "x.txt"
    f.write_text("你好ab", encoding="utf-8")
    row = compute_file_stats(f, tmp_path)
    assert row["unicode_chars"] == 4


def test_pdf_blank_pages_need_ocr(tmp_path: Path) -> None:
    f = tmp_path / "empty.pdf"
    f.write_bytes(_minimal_pdf_bytes())
    row = compute_file_stats(f, tmp_path)
    assert row.get("page_count") == 1
    assert row.get("needs_ocr") is True
    assert row.get("unicode_chars", 0) == 0


def test_xlsx_heuristic(tmp_path: Path) -> None:
    f = tmp_path / "t.xlsx"
    f.write_bytes(b"not a real xlsx")
    row = compute_file_stats(f, tmp_path)
    assert row.get("table_count_heuristic") == 1
    assert row.get("heuristic") is True


def test_aggregate_totals(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("yy", encoding="utf-8")
    files = [tmp_path / "a.txt", tmp_path / "b.txt"]
    payload = aggregate_golden_stats(tmp_path, files)
    assert payload["schema_version"] == "1.0"
    assert payload["totals"]["total_files"] == 2
    assert payload["totals"]["total_unicode_chars"] == 3
    assert "needs_ocr_files" in payload["totals"]


def test_stats_cli_writes_golden_stats(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    runner = CliRunner(mix_stderr=False)
    out = tmp_path / "golden_stats.json"
    r = runner.invoke(
        app,
        ["stats", "--root", str(tmp_path), "--stats-out", str(out)],
    )
    assert r.exit_code == 0, r.stdout + (r.stderr or "")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["totals"]["total_unicode_chars"] == 5
    assert "unicode_chars=" in r.stderr or "needs_ocr=" in r.stderr
