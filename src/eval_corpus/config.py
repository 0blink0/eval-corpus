"""Corpus root resolution (CLI > EVAL_CORPUS_ROOT)."""

from __future__ import annotations

import os
from pathlib import Path


class ConfigError(Exception):
    """Invalid or missing corpus configuration."""


def resolve_corpus_root(cli_root: str | None) -> Path:
    """
    Resolve corpus root per D-02: CLI argument wins over EVAL_CORPUS_ROOT.
    Returns absolute resolved directory path.
    """
    raw = (cli_root or "").strip()
    if not raw:
        raw = os.environ.get("EVAL_CORPUS_ROOT", "").strip()
    if not raw:
        raise ConfigError(
            "Missing corpus root: set --root or environment variable EVAL_CORPUS_ROOT."
        )
    path = Path(raw).expanduser().resolve()
    if not path.exists():
        raise ConfigError(f"Corpus root does not exist: {path}")
    if not path.is_dir():
        raise ConfigError(f"Corpus root is not a directory: {path}")
    return path
