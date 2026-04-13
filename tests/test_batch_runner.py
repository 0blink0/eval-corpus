"""Tests for batch runner with retry and threshold policies."""

from __future__ import annotations

from pathlib import Path

from eval_corpus.batch.models import BatchRunConfig
from eval_corpus.batch.runner import run_batch


def _prepare_files(root: Path, names: list[str]) -> None:
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"content:{name}", encoding="utf-8")


def test_continue_on_error_collects_failed_files(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    _prepare_files(input_dir, ["a.txt", "b.txt", "nested/c.txt"])

    def processor(file_path: Path) -> dict:
        if file_path.name == "b.txt":
            raise RuntimeError("boom")
        return {"file": file_path.name}

    result = run_batch(
        input_dir,
        BatchRunConfig(max_workers=1, continue_on_error=True, max_retries=0),
        processor=processor,
    )
    assert result.total == 3
    assert result.succeeded == 2
    assert result.failed == 1
    assert result.aborted is False
    assert len(result.errors) == 1
    assert result.errors[0].file.endswith("b.txt")


def test_failure_threshold_aborts_batch(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    _prepare_files(input_dir, ["a.txt", "b.txt", "c.txt", "d.txt"])

    def processor(_: Path) -> dict:
        raise RuntimeError("always fail")

    result = run_batch(
        input_dir,
        BatchRunConfig(
            max_workers=1,
            continue_on_error=True,
            max_retries=0,
            failure_threshold=0.5,
        ),
        processor=processor,
    )
    assert result.aborted is True
    assert result.termination_reason == "failure_threshold_exceeded"
    assert result.failed >= 2


def test_retry_records_retry_success(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    _prepare_files(input_dir, ["a.txt", "b.txt"])
    attempts: dict[str, int] = {}

    def processor(file_path: Path) -> dict:
        attempts[file_path.name] = attempts.get(file_path.name, 0) + 1
        if file_path.name == "b.txt" and attempts[file_path.name] == 1:
            raise RuntimeError("first attempt fails")
        return {"file": file_path.name}

    result = run_batch(
        input_dir,
        BatchRunConfig(max_workers=1, continue_on_error=True, max_retries=1),
        processor=processor,
    )
    assert result.succeeded == 2
    assert result.retry_succeeded == 1
    assert result.failed == 0
    assert attempts["b.txt"] == 2
