"""Runtime metadata contracts for reporting exporters."""

from __future__ import annotations

import json

from eval_corpus.reporting.build import build_report_payload
from eval_corpus.reporting.exporters import export_html, export_json, export_markdown
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
        "per_file": [{"file": "a.pdf", "tool": "glm", "metrics": _metrics_summary(0.93), "errors": 0, "not_applicable": 0}],
        "per_tool": [{"tool": "glm", "metrics_summary": _metrics_summary(0.93), "applicable_count": 7, "total_count": 7}],
        "overall": {
            "metrics_summary": _metrics_summary(0.90),
            "generated_at": "2026-04-13T09:00:00Z",
            "runtime_metadata": {
                "run_id": "run-001",
                "tool_versions": {"glm": "1.0"},
                "git_commit": "abc1234",
                "git_status": "clean",
            },
        },
    }
    return build_report_payload(payload)


def test_runtime_metadata_fields_exist_in_all_human_readable_outputs() -> None:
    report = _sample_report_payload()
    markdown = export_markdown(report)
    html = export_html(report)

    for field in ("generated_at", "tool_versions", "git_commit"):
        assert field in markdown
        assert field in html


def test_runtime_metadata_is_preserved_in_json_export() -> None:
    report = _sample_report_payload()
    payload = json.loads(export_json(report))
    runtime = payload["runtime"]

    assert runtime["generated_at"] == "2026-04-13T09:00:00Z"
    assert runtime["tool_versions"]["glm"] == "1.0"
    assert runtime["git_commit"] == "abc1234"
