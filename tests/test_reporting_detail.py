"""Contract tests for reporting exporters detail outputs."""

from __future__ import annotations

import csv
import io
import json
import re

from eval_corpus.reporting.build import build_report_payload
from eval_corpus.reporting.exporters import export_csv, export_html, export_json, export_markdown
from eval_corpus.reporting.models import REQUIRED_METRICS


def _metric(raw_value: float) -> dict[str, object]:
    return {
        "raw_value": raw_value,
        "threshold": {"warn_min": 0.7, "pass_min": 0.9},
        "level": "pass",
        "numerator": 9,
        "denominator": 10,
        "excluded_count": 0,
        "applicable_count": 1,
        "total_count": 1,
        "not_applicable_reasons": [],
    }


def _metrics_summary(base: float) -> dict[str, dict[str, object]]:
    return {metric_id: _metric(base + idx * 0.001) for idx, metric_id in enumerate(REQUIRED_METRICS)}


def _sample_report_payload():
    payload = {
        "per_file": [
            {"file": "a.pdf", "tool": "glm", "metrics": _metrics_summary(0.93), "errors": 0, "not_applicable": 0},
            {"file": "b.pdf", "tool": "mineru", "metrics": _metrics_summary(0.91), "errors": 1, "not_applicable": 1},
        ],
        "per_tool": [
            {"tool": "glm", "metrics_summary": _metrics_summary(0.93), "applicable_count": 7, "total_count": 7},
            {"tool": "mineru", "metrics_summary": _metrics_summary(0.91), "applicable_count": 7, "total_count": 7},
            {"tool": "paddle", "metrics_summary": _metrics_summary(0.89), "applicable_count": 7, "total_count": 7},
        ],
        "overall": {
            "metrics_summary": _metrics_summary(0.90),
            "generated_at": "2026-04-13T09:00:00Z",
            "runtime_metadata": {
                "run_id": "run-001",
                "tool_versions": {"glm": "1.0", "mineru": "2.0", "paddle": "3.0"},
                "git_commit": "abc1234",
                "git_status": "clean",
            },
        },
    }
    return build_report_payload(payload)


def _extract_metric_points_from_markdown(markdown: str) -> set[tuple[str, str, str]]:
    points: set[tuple[str, str, str]] = set()
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        section, row_key, metric_id, raw_value = cells[:4]
        if section in {"summary", "detail"} and metric_id.startswith("METR-"):
            points.add((section, row_key, metric_id + ":" + raw_value))
    return points


def _extract_metric_points_from_html(html_text: str) -> set[tuple[str, str, str]]:
    pattern = re.compile(
        r'<tr data-section="(summary|detail)" data-row-key="([^"]+)" data-metric-id="([^"]+)" data-raw-value="([^"]*)">',
    )
    return {(section, row_key, metric_id + ":" + raw_value) for section, row_key, metric_id, raw_value in pattern.findall(html_text)}


def test_exporters_keep_metric_values_consistent_across_formats() -> None:
    report = _sample_report_payload()

    raw_json = export_json(report)
    raw_csv = export_csv(report)
    raw_markdown = export_markdown(report)
    raw_html = export_html(report)

    json_points = set()
    data = json.loads(raw_json)
    for row in data["summary_rows"]:
        for metric_id, metric in row["metrics"].items():
            json_points.add(("summary", row["row_key"], f"{metric_id}:{metric['raw_value']}"))
    for row in data["per_file_rows"]:
        for metric_id, metric in row["metrics"].items():
            json_points.add(("detail", f"{row['tool']}::{row['file']}", f"{metric_id}:{metric['raw_value']}"))

    csv_points = set()
    for row in csv.DictReader(io.StringIO(raw_csv)):
        if row["section"] in {"summary", "detail"}:
            csv_points.add((row["section"], row["row_key"], f"{row['metric_id']}:{row['raw_value']}"))

    markdown_points = _extract_metric_points_from_markdown(raw_markdown)
    html_points = _extract_metric_points_from_html(raw_html)

    assert json_points == csv_points == markdown_points == html_points


def test_exported_detail_rows_include_raw_threshold_level_and_error_counts() -> None:
    report = _sample_report_payload()
    rows = list(csv.DictReader(io.StringIO(export_csv(report))))
    detail_rows = [row for row in rows if row["section"] == "detail"]

    assert detail_rows
    row = detail_rows[0]
    assert row["raw_value"] != ""
    assert row["threshold_warn_min"] == "0.7"
    assert row["threshold_pass_min"] == "0.9"
    assert row["level"] in {"pass", "warn", "fail"}
    assert row["errors"] in {"0", "1"}
    assert row["not_applicable"] in {"0", "1"}
