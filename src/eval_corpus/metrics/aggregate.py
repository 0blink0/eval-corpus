"""Aggregators for per-file, per-tool and overall metric payloads."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from eval_corpus.ir_models import Chunk
from eval_corpus.metrics.calculators import (
    compute_metric_01,
    compute_metric_02,
    compute_metric_03,
    compute_metric_04,
    compute_metric_05,
    compute_metric_06,
    compute_metric_07_semantic_completeness,
)
from eval_corpus.metrics.models import MetricThreshold, judge_level

MetricMap = dict[str, dict[str, Any]]


def _calculate_metrics_for_file(
    chunks: list[Chunk],
    *,
    ir_table_block_count: int | None = None,
) -> MetricMap:
    """Compute per-file metrics.

    ``ir_table_block_count``: number of ``ParsedBlock`` with ``type==table`` before chunking.
    When set, METR-04 denominator follows IR (detects chunking/regression vs adapter output).
    When omitted, METR-04 falls back to counting table-bearing chunks (legacy, tautological).
    """
    exp04 = (
        ir_table_block_count
        if ir_table_block_count is not None
        else sum(1 for c in chunks if any(bt.value == "table" for bt in c.block_types))
    )
    return {
        "METR-01": compute_metric_01(
            chunks, golden_chars=max(sum(len(c.text) for c in chunks), 1)
        ).model_dump(),
        "METR-02": compute_metric_02(chunks).model_dump(),
        "METR-03": compute_metric_03(chunks).model_dump(),
        "METR-04": compute_metric_04(chunks, expected_table_blocks=exp04).model_dump(),
        "METR-05": compute_metric_05(chunks).model_dump(),
        "METR-06": compute_metric_06(chunks).model_dump(),
        "METR-07": compute_metric_07_semantic_completeness(chunks).model_dump(),
    }


def _resolve_metrics_for_group(
    metrics_template: dict[Any, MetricMap] | MetricMap | None,
    source_file: str,
    parser_tool: str,
    file_chunks: list[Chunk],
    *,
    ir_table_block_count: int | None = None,
) -> MetricMap:
    """Resolve metrics for one (file, tool) group safely.

    A single MetricMap template (METR-* keys) is intentionally ignored to avoid
    cross-file metric reuse. Per-group templates can be passed as a mapping with
    keys like (source_file, parser_tool) or "source_file::parser_tool".
    """
    if metrics_template is None:
        return _calculate_metrics_for_file(file_chunks, ir_table_block_count=ir_table_block_count)

    if isinstance(metrics_template, dict):
        if all(str(key).startswith("METR-") for key in metrics_template.keys()):
            return _calculate_metrics_for_file(file_chunks, ir_table_block_count=ir_table_block_count)

        tuple_key = (source_file, parser_tool)
        str_key = f"{source_file}::{parser_tool}"
        if tuple_key in metrics_template:
            return deepcopy(metrics_template[tuple_key])
        if str_key in metrics_template:
            return deepcopy(metrics_template[str_key])

    return _calculate_metrics_for_file(file_chunks, ir_table_block_count=ir_table_block_count)


def build_per_file_metrics(
    chunks: list[Chunk],
    metrics_template: dict[Any, MetricMap] | MetricMap | None = None,
    *,
    errors: list[dict[str, Any]] | None = None,
    ir_table_counts: dict[tuple[str, str], int] | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        grouped[(chunk.source_file, chunk.parser_tool)].append(chunk)

    error_index: dict[tuple[str, str], int] = defaultdict(int)
    for item in errors or []:
        key = (item.get("source_file", "unknown"), item.get("parser_tool", "unknown"))
        error_index[key] += 1

    per_file: list[dict[str, Any]] = []
    for (source_file, parser_tool), file_chunks in sorted(grouped.items()):
        ir_n = ir_table_counts.get((source_file, parser_tool)) if ir_table_counts else None
        metrics = _resolve_metrics_for_group(
            metrics_template,
            source_file,
            parser_tool,
            file_chunks,
            ir_table_block_count=ir_n,
        )
        not_applicable = sum(
            1 for metric in metrics.values() if metric.get("raw_value", None) is None
        )
        per_file.append(
            {
                "file": source_file,
                "tool": parser_tool,
                "metrics": metrics,
                "errors": error_index[(source_file, parser_tool)],
                "not_applicable": not_applicable,
            }
        )
    return per_file


def build_per_tool_metrics(per_file: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_file:
        grouped[row["tool"]].append(row)

    result: list[dict[str, Any]] = []
    for tool, rows in sorted(grouped.items()):
        metrics_summary = _summarize_metric_rows([r["metrics"] for r in rows])
        result.append(
            {
                "tool": tool,
                "metrics_summary": metrics_summary,
                "applicable_count": sum(
                    metric["applicable_count"]
                    for row in rows
                    for metric in row["metrics"].values()
                ),
                "total_count": sum(
                    metric["total_count"] for row in rows for metric in row["metrics"].values()
                ),
            }
        )
    return result


def build_overall_metrics(
    per_file: list[dict[str, Any]],
    per_tool: list[dict[str, Any]],
    *,
    runtime_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics_summary = _summarize_metric_rows([r["metrics"] for r in per_file])
    merged_runtime = {
        **(runtime_metadata or {}),
        "tool_count": len(per_tool),
        "file_count": len(per_file),
        "error_count": sum(r["errors"] for r in per_file),
    }
    return {
        "metrics_summary": metrics_summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_metadata": merged_runtime,
    }


def _summarize_metric_rows(rows: list[MetricMap]) -> MetricMap:
    bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for metrics in rows:
        for metric_id, metric_data in metrics.items():
            bucket[metric_id].append(metric_data)

    summary: MetricMap = {}
    for metric_id, items in bucket.items():
        raw_values = [item["raw_value"] for item in items if item.get("raw_value") is not None]
        numerator = sum(item.get("numerator", 0) for item in items)
        denominator = sum(item.get("denominator", 0) for item in items)
        excluded_count = sum(item.get("excluded_count", 0) for item in items)
        applicable_count = sum(item.get("applicable_count", 0) for item in items)
        total_count = sum(item.get("total_count", 0) for item in items)
        not_applicable_reasons = [
            reason
            for item in items
            for reason in item.get("not_applicable_reasons", [])
        ]

        threshold_data = items[0]["threshold"]
        threshold = MetricThreshold.model_validate(threshold_data)
        raw_value = sum(raw_values) / len(raw_values) if raw_values else None
        summary[metric_id] = {
            "raw_value": raw_value,
            "threshold": threshold.model_dump(),
            "level": judge_level(raw_value, threshold),
            "numerator": numerator,
            "denominator": denominator,
            "excluded_count": excluded_count,
            "applicable_count": applicable_count,
            "total_count": total_count,
            "not_applicable_reasons": sorted(set(not_applicable_reasons)),
        }
    return summary
