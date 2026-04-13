"""Tests for corpus scanning."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from eval_corpus.scan import DEFAULT_EXTENSIONS, collect_corpus_files, normalize_extra_exts


def test_default_extensions_contains_pdf() -> None:
    assert ".pdf" in DEFAULT_EXTENSIONS


def test_normalize_extra_exts() -> None:
    ex = normalize_extra_exts(("CSV", ".doc"))
    assert ".csv" in ex
    assert ".doc" in ex


def test_collect_respects_allowlist_and_ignores_tmp(tmp_path: Path) -> None:
    (tmp_path / "a.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "skip.bin").write_bytes(b"xxx")
    (tmp_path / "~$lock.docx").write_bytes(b"")
    (tmp_path / ".DS_Store").write_bytes(b"")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("hello", encoding="utf-8")

    files, errors, unreadable = collect_corpus_files(tmp_path)
    rels = {p.relative_to(tmp_path).as_posix() for p in files}
    assert rels == {"a.pdf", "sub/b.txt"}
    assert errors == []
    assert unreadable == 0


def test_collect_unreadable_permission_records_error(tmp_path: Path) -> None:
    target = tmp_path / "secret.pdf"
    target.write_bytes(b"%PDF-1.4")

    real_stat = Path.stat

    def _stat(self: Path, *a, **kw):
        # Allow lstat(follow_symlinks=False) used by is_symlink(); fail normal stat.
        if self.name == "secret.pdf" and kw.get("follow_symlinks", True):
            raise PermissionError("fake unreadable")
        return real_stat(self, *a, **kw)

    with patch.object(Path, "stat", _stat):
        files, errors, unreadable = collect_corpus_files(tmp_path)

    assert files == []
    assert unreadable == 1
    assert len(errors) == 1
    assert errors[0]["path"] == "secret.pdf"
    assert "PermissionError" in errors[0]["error"] or "fake unreadable" in errors[0]["error"]
