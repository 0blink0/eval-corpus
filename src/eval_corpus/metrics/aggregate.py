"""Aggregators for per-file, per-tool and overall metric payloads."""

from __future__ import annotations

from collections import defaultdict
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


def _metric_functions() -> dict[str, Any]:
    return {
        "METR-01": lambda chunks: compute_metric_01(
            chunks, golden_chars=max(sum(len(c.text) for c in chunks), 1)
        ),
        "METR-02": lambda chunks: compute_metric_02(chunks),
        "METR-03": lambda chunks: compute_metric_03(chunks),
        "METR-04": lambda chunks: compute_metric_04(
            chunks,
            expected_table_blocks=sum(
                1 for c in chunks if any(bt.value == "table" for bt in c.block_types)
            ),
        ),
        "METR-05": lambda chunks: compute_metric_05(chunks),
        "METR-06": lambda chunks: compute_metric_06(chunks),
        "METR-07": lambda chunks: compute_metric_07_semantic_completeness(chunks),
    }


def _calculate_metrics_for_file(chunks: list[Chunk]) -> MetricMap:
    return {name: fn(chunks).model_dump() for name, fn in _metric_functions().items()}


def build_per_file_metrics(
    chunks: list[Chunk],
    metrics_template: MetricMap | None = None,
    *,
    errors: list[dict[str, Any]] | None = None,
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
        metrics = metrics_template or _calculate_metrics_for_file(file_chunks)
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
    return {
        "metrics_summary": metrics_summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_metadata": {
            "tool_count": len(per_tool),
            "file_count": len(per_file),
            "error_count": sum(r["errors"] for r in per_file),
            **(runtime_metadata or {}),
        },
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
