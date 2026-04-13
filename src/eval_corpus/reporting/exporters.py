"""Export canonical report payload into multiple output formats."""

from __future__ import annotations

import csv
import html
import io
import json
from typing import Any

from eval_corpus.reporting.models import MetricCell, ReportPayload


def export_json(payload: ReportPayload) -> str:
    return json.dumps(payload.model_dump(), ensure_ascii=False, indent=2) + "\n"


def export_csv(payload: ReportPayload) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=_columns())
    writer.writeheader()
    for row in _iter_export_rows(payload):
        writer.writerow(row)
    return out.getvalue()


def export_markdown(payload: ReportPayload) -> str:
    lines = [
        "# Reporting Export",
        "",
        "| section | row_key | metric_id | raw_value | threshold_warn_min | threshold_pass_min | level | errors | not_applicable | generated_at | git_commit | run_id | git_status | tool_versions |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in _iter_export_rows(payload):
        lines.append(
            "| "
            + " | ".join(
                [
                    row["section"],
                    row["row_key"],
                    row["metric_id"],
                    row["raw_value"],
                    row["threshold_warn_min"],
                    row["threshold_pass_min"],
                    row["level"],
                    row["errors"],
                    row["not_applicable"],
                    row["generated_at"],
                    row["git_commit"],
                    row["run_id"],
                    row["git_status"],
                    row["tool_versions"],
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def export_html(payload: ReportPayload) -> str:
    rows = []
    for row in _iter_export_rows(payload):
        attrs = (
            f'data-section="{html.escape(row["section"], quote=True)}" '
            f'data-row-key="{html.escape(row["row_key"], quote=True)}" '
            f'data-metric-id="{html.escape(row["metric_id"], quote=True)}" '
            f'data-raw-value="{html.escape(row["raw_value"], quote=True)}"'
        )
        rows.append(
            "<tr "
            + attrs
            + ">"
            + "".join(f"<td>{html.escape(value)}</td>" for value in row.values())
            + "</tr>"
        )

    header_cells = "".join(f"<th>{html.escape(column)}</th>" for column in _columns())
    body = "\n".join(rows)
    return (
        "<html><body>"
        "<h1>Reporting Export</h1>"
        "<table>"
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{body}</tbody>"
        "</table>"
        "</body></html>\n"
    )


def _columns() -> list[str]:
    return [
        "section",
        "row_key",
        "metric_id",
        "raw_value",
        "threshold_warn_min",
        "threshold_pass_min",
        "level",
        "errors",
        "not_applicable",
        "generated_at",
        "git_commit",
        "run_id",
        "git_status",
        "tool_versions",
    ]


def _iter_export_rows(payload: ReportPayload) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    runtime = payload.runtime
    runtime_tool_versions = json.dumps(runtime.tool_versions, ensure_ascii=False, sort_keys=True)

    for row in payload.summary_rows:
        for metric_id in payload.metric_order:
            metric = row.metrics[metric_id]
            rows.append(
                _to_row(
                    section="summary",
                    row_key=row.row_key,
                    metric_id=metric_id,
                    metric=metric,
                    errors=row.errors,
                    not_applicable=row.not_applicable,
                    runtime=runtime,
                    runtime_tool_versions=runtime_tool_versions,
                )
            )

    for row in payload.per_file_rows:
        row_key = f"{row.tool}::{row.file}"
        for metric_id in payload.metric_order:
            metric = row.metrics[metric_id]
            rows.append(
                _to_row(
                    section="detail",
                    row_key=row_key,
                    metric_id=metric_id,
                    metric=metric,
                    errors=row.errors,
                    not_applicable=row.not_applicable,
                    runtime=runtime,
                    runtime_tool_versions=runtime_tool_versions,
                )
            )
    return rows


def _to_row(
    *,
    section: str,
    row_key: str,
    metric_id: str,
    metric: MetricCell,
    errors: int,
    not_applicable: int,
    runtime: Any,
    runtime_tool_versions: str,
) -> dict[str, str]:
    raw = "" if metric.raw_value is None else str(metric.raw_value)
    return {
        "section": section,
        "row_key": row_key,
        "metric_id": metric_id,
        "raw_value": raw,
        "threshold_warn_min": str(metric.threshold.warn_min),
        "threshold_pass_min": str(metric.threshold.pass_min),
        "level": metric.level,
        "errors": str(errors),
        "not_applicable": str(not_applicable),
        "generated_at": runtime.generated_at,
        "git_commit": runtime.git_commit or "",
        "run_id": runtime.run_id or "",
        "git_status": runtime.git_status or "",
        "tool_versions": runtime_tool_versions,
    }
