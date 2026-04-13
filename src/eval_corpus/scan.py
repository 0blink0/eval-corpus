"""Recursive corpus file enumeration with filters (D-08–D-11, CORP-02 readability)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pdf",
        ".docx",
        ".xlsx",
        ".pptx",
        ".txt",
        ".md",
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
    }
)


def normalize_extra_exts(extra: tuple[str, ...]) -> frozenset[str]:
    out: set[str] = set()
    for e in extra:
        e = e.strip().lower()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        out.add(e)
    return frozenset(out)


def _should_skip_name(name: str) -> bool:
    if name == ".DS_Store":
        return True
    if name.startswith("~$"):
        return True
    return False


def effective_extensions(extra_exts: frozenset[str]) -> frozenset[str]:
    return DEFAULT_EXTENSIONS | set(extra_exts)


@dataclass
class ScanOutcome:
    files: list[Path]
    errors: list[dict]
    unreadable_count: int


def collect_corpus_files(
    root: Path,
    extra_exts: frozenset[str] | None = None,
) -> tuple[list[Path], list[dict], int]:
    """
    Walk corpus root without following symlinks; collect files matching extensions.
    Returns (files, errors, unreadable_count).
    """
    exts = effective_extensions(extra_exts or frozenset())
    files: list[Path] = []
    errors: list[dict] = []
    unreadable = 0

    root = root.resolve()

    for dirpath, dirnames, filenames in os.walk(
        root, topdown=True, followlinks=False
    ):
        # Skip symlink directories entirely
        dirnames[:] = [
            d
            for d in dirnames
            if not (Path(dirpath) / d).is_symlink()
        ]
        for name in filenames:
            if _should_skip_name(name):
                continue
            path = Path(dirpath) / name
            if path.is_symlink():
                continue
            suffix = path.suffix.lower()
            if suffix not in exts:
                continue
            rel = None
            try:
                rel = path.relative_to(root).as_posix()
                path.stat()
            except OSError as e:
                unreadable += 1
                errors.append(
                    {
                        "path": rel or str(path),
                        "error": str(e),
                    }
                )
                continue
            files.append(path)

    files.sort(key=lambda p: str(p))
    return files, errors, unreadable
