"""Adapter runner with continue/fail-fast policies."""

from __future__ import annotations

from pathlib import Path

from eval_corpus.adapters.base import AdapterConfig, AdapterError
from eval_corpus.adapters.registry import get_adapter
from eval_corpus.ir_models import ParsedBlock


def run_adapter_on_files(
    tool: str,
    files: list[Path],
    *,
    fail_fast: bool = False,
    debug: bool = False,
) -> dict:
    adapter = get_adapter(tool)
    cfg = AdapterConfig(debug=debug)
    runtime = adapter.get_runtime_metadata().model_dump(mode="json")

    results: list[dict] = []
    errors: list[dict] = []
    for f in files:
        try:
            blocks: list[ParsedBlock] = adapter.parse_to_blocks(f, cfg)
            results.append(
                {
                    "file": str(f),
                    "blocks": [b.model_dump(mode="json") for b in blocks],
                }
            )
        except AdapterError as e:
            err = e.to_dict()
            if not debug:
                err["raw_error"] = None
            errors.append(err)
            if fail_fast:
                break
    return {
        "tool": tool,
        "runtime_metadata": runtime,
        "results": results,
        "errors": errors,
    }
