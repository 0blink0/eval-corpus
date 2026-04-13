"""Runtime metadata helpers for report/batch/synthetic runs."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

_TOOL_PACKAGES: tuple[str, ...] = ("typer", "pydantic", "pytest")


def collect_runtime_metadata(*, run_id: str, repo_dir: Path | None = None) -> dict[str, Any]:
    """Collect run-level metadata with safe git fallbacks."""
    commit, status = _git_snapshot(repo_dir or Path.cwd())
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool_versions": _tool_versions(),
        "git_commit": commit,
        "git_status": status,
        "run_id": run_id,
    }


def _tool_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in _TOOL_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    return versions


def _git_snapshot(repo_dir: Path) -> tuple[str | None, str]:
    try:
        commit = _run_git(["rev-parse", "HEAD"], repo_dir)
        dirty_flag = _run_git(["status", "--porcelain"], repo_dir)
    except (OSError, subprocess.SubprocessError):
        return None, "unavailable"
    status = "dirty" if dirty_flag else "clean"
    return commit, status


def _run_git(args: list[str], repo_dir: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()
