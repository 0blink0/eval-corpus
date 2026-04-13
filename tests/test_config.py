"""Tests for corpus root resolution (CORP-01, D-01–D-04)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from eval_corpus.config import ConfigError, resolve_corpus_root


def test_resolve_env_only_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_CORPUS_ROOT", raising=False)
    monkeypatch.setenv("EVAL_CORPUS_ROOT", str(tmp_path))
    p = resolve_corpus_root(None)
    assert p == tmp_path.resolve()


def test_resolve_cli_overrides_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.setenv("EVAL_CORPUS_ROOT", str(tmp_path))
    p = resolve_corpus_root(str(other))
    assert p == other.resolve()


def test_resolve_both_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_CORPUS_ROOT", raising=False)
    with pytest.raises(ConfigError, match="EVAL_CORPUS_ROOT"):
        resolve_corpus_root(None)


def test_resolve_empty_cli_falls_through_to_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EVAL_CORPUS_ROOT", str(tmp_path))
    p = resolve_corpus_root("  ")
    assert p == tmp_path.resolve()


def test_resolve_missing_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_CORPUS_ROOT", raising=False)
    missing = tmp_path / "nope"
    with pytest.raises(ConfigError, match="does not exist"):
        resolve_corpus_root(str(missing))


def test_resolve_not_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_CORPUS_ROOT", raising=False)
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(ConfigError, match="not a directory"):
        resolve_corpus_root(str(f))
