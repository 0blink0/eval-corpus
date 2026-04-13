"""Contract tests for reporting summary builder."""

from __future__ import annotations

from eval_corpus.reporting.build import build_report_payload
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


def _sample_metrics_payload() -> dict[str, object]:
    per_tool = [
        {"tool": "mineru", "metrics_summary": _metrics_summary(0.91), "applicable_count": 7, "total_count": 7},
        {"tool": "paddle", "metrics_summary": _metrics_summary(0.89), "applicable_count": 7, "total_count": 7},
        {"tool": "glm", "metrics_summary": _metrics_summary(0.93), "applicable_count": 7, "total_count": 7},
    ]
    per_file = [
        {"file": "a.pdf", "tool": "glm", "metrics": _metrics_summary(0.93), "errors": 0, "not_applicable": 0},
        {"file": "b.pdf", "tool": "mineru", "metrics": _metrics_summary(0.91), "errors": 1, "not_applicable": 1},
    ]
    overall = {
        "metrics_summary": _metrics_summary(0.90),
        "generated_at": "2026-04-13T09:00:00Z",
        "runtime_metadata": {
            "run_id": "run-001",
            "tool_versions": {"glm": "1.0", "mineru": "2.0", "paddle": "3.0"},
            "git_commit": "abc1234",
            "git_status": "clean",
        },
    }
    return {"per_file": per_file, "per_tool": per_tool, "overall": overall}


def test_builder_keeps_required_metrics_and_threshold_for_each_summary_row() -> None:
    report = build_report_payload(_sample_metrics_payload())

    assert [row.row_key for row in report.summary_rows] == ["glm", "mineru", "paddle", "overall"]
    for row in report.summary_rows:
        assert set(row.metrics.keys()) == set(REQUIRED_METRICS)
        for metric_id in REQUIRED_METRICS:
            assert row.metrics[metric_id].threshold.pass_min == 0.9
            assert row.metrics[metric_id].threshold.warn_min == 0.7


def test_builder_generates_consistent_field_shape_for_tool_and_overall_rows() -> None:
    report = build_report_payload(_sample_metrics_payload())

    tool_row = report.summary_rows[0]
    overall_row = report.summary_rows[-1]

    assert tool_row.row_type == "tool"
    assert overall_row.row_type == "overall"
    assert set(tool_row.model_dump().keys()) == set(overall_row.model_dump().keys())
