"""Directory-recursive batch runner with retry and threshold controls."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from eval_corpus.batch.models import BatchError, BatchRunConfig, BatchRunResult


def _collect_files(input_dir: Path) -> list[Path]:
    root = input_dir.resolve()
    if not root.is_dir():
        raise ValueError(f"input_dir is not a directory: {input_dir}")

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        resolved = path.resolve()
        resolved.relative_to(root)
        files.append(resolved)
    return files


def _run_with_retries(file_path: Path, config: BatchRunConfig, processor: Callable[[Path], dict]) -> tuple[dict | None, Exception | None, int]:
    attempts = 0
    max_attempts = config.max_retries + 1
    while attempts < max_attempts:
        attempts += 1
        try:
            return processor(file_path), None, attempts
        except Exception as exc:  # noqa: BLE001
            if attempts >= max_attempts:
                return None, exc, attempts
    return None, RuntimeError("unreachable"), attempts


def run_batch(input_dir: Path, config: BatchRunConfig, *, processor: Callable[[Path], dict]) -> BatchRunResult:
    files = _collect_files(input_dir)
    result = BatchRunResult(total=len(files))
    if not files:
        return result

    with ThreadPoolExecutor(max_workers=config.max_workers) as pool:
        futures = [pool.submit(_run_with_retries, file_path, config, processor) for file_path in files]
        for file_path, future in zip(files, futures, strict=True):
            payload, err, attempts = future.result()

            if err is None:
                result.succeeded += 1
                if attempts > 1:
                    result.retry_succeeded += 1
                result.results.append({"file": str(file_path), "attempts": attempts, "payload": payload})
            else:
                result.failed += 1
                result.errors.append(BatchError(file=str(file_path), message=str(err), attempts=attempts))
                if not config.continue_on_error:
                    result.aborted = True
                    result.termination_reason = "continue_on_error_disabled"
                    break

            if result.total > 0 and (result.failed / result.total) >= config.failure_threshold:
                result.aborted = True
                result.termination_reason = "failure_threshold_exceeded"
                break

    return result
