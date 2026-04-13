"""Build canonical report payload from metrics artifact."""

from __future__ import annotations

from typing import Any

from eval_corpus.reporting.models import (
    REQUIRED_METRICS,
    DetailRow,
    MetricCell,
    ReportPayload,
    ReportingStructureError,
    RuntimeAppendix,
    SummaryRow,
)


def build_report_payload(metrics_payload: dict[str, Any]) -> ReportPayload:
    _validate_root_keys(metrics_payload)

    per_tool = metrics_payload["per_tool"]
    per_file = metrics_payload["per_file"]
    overall = metrics_payload["overall"]
    if not isinstance(per_tool, list) or not isinstance(per_file, list) or not isinstance(overall, dict):
        raise ReportingStructureError(
            "invalid-root-type",
            "metrics payload root types are invalid",
            details={"per_tool": type(per_tool).__name__, "per_file": type(per_file).__name__},
        )

    summary_rows = [_tool_row(item) for item in sorted(per_tool, key=lambda x: str(x.get("tool", "")))]
    summary_rows.append(_overall_row(overall, per_file))

    detail_rows = [
        _detail_row(item) for item in sorted(per_file, key=lambda x: (str(x.get("tool", "")), str(x.get("file", ""))))
    ]

    runtime_metadata = overall.get("runtime_metadata", {})
    if not isinstance(runtime_metadata, dict):
        raise ReportingStructureError("invalid-runtime", "overall.runtime_metadata must be an object")
    runtime = RuntimeAppendix(
        generated_at=str(overall.get("generated_at", "")),
        tool_versions=_to_tool_versions(runtime_metadata.get("tool_versions", {})),
        git_commit=_to_optional_str(runtime_metadata.get("git_commit")),
        run_id=_to_optional_str(runtime_metadata.get("run_id")),
        git_status=_to_optional_str(runtime_metadata.get("git_status")),
        **{
            key: value
            for key, value in runtime_metadata.items()
            if key not in {"tool_versions", "git_commit", "run_id", "git_status"}
        },
    )
    return ReportPayload(summary_rows=summary_rows, per_file_rows=detail_rows, runtime=runtime)


def _validate_root_keys(payload: dict[str, Any]) -> None:
    required = {"per_file", "per_tool", "overall"}
    keys = set(payload.keys())
    if keys != required:
        raise ReportingStructureError(
            "invalid-root-keys",
            "metrics payload must contain only per_file/per_tool/overall",
            details={"missing": sorted(required - keys), "extra": sorted(keys - required)},
        )


def _tool_row(item: dict[str, Any]) -> SummaryRow:
    tool = item.get("tool")
    if not isinstance(tool, str) or not tool:
        raise ReportingStructureError("missing-tool", "per_tool item must contain non-empty tool")
    metrics = _normalize_metric_map(item.get("metrics_summary"), owner=f"per_tool[{tool}]")
    return SummaryRow(
        row_key=tool,
        row_type="tool",
        label=tool,
        metrics=metrics,
        errors=0,
        not_applicable=sum(1 for metric in metrics.values() if metric.raw_value is None),
    )


def _overall_row(overall: dict[str, Any], per_file: list[dict[str, Any]]) -> SummaryRow:
    metrics = _normalize_metric_map(overall.get("metrics_summary"), owner="overall")
    errors = sum(int(item.get("errors", 0)) for item in per_file)
    not_applicable = sum(int(item.get("not_applicable", 0)) for item in per_file)
    return SummaryRow(
        row_key="overall",
        row_type="overall",
        label="overall",
        metrics=metrics,
        errors=max(errors, 0),
        not_applicable=max(not_applicable, 0),
    )


def _detail_row(item: dict[str, Any]) -> DetailRow:
    tool = item.get("tool")
    file = item.get("file")
    if not isinstance(tool, str) or not tool:
        raise ReportingStructureError("missing-tool", "per_file item must contain non-empty tool")
    if not isinstance(file, str) or not file:
        raise ReportingStructureError("missing-file", "per_file item must contain non-empty file")
    return DetailRow(
        file=file,
        tool=tool,
        metrics=_normalize_metric_map(item.get("metrics"), owner=f"per_file[{tool}:{file}]"),
        errors=max(int(item.get("errors", 0)), 0),
        not_applicable=max(int(item.get("not_applicable", 0)), 0),
    )


def _normalize_metric_map(metrics: Any, *, owner: str) -> dict[str, MetricCell]:
    if not isinstance(metrics, dict):
        raise ReportingStructureError("invalid-metrics", f"{owner} metrics must be an object")
    missing = [metric for metric in REQUIRED_METRICS if metric not in metrics]
    if missing:
        raise ReportingStructureError(
            "missing-metrics",
            f"{owner} missing required metrics",
            details={"missing": missing},
        )
    return {metric_id: MetricCell.model_validate(metrics[metric_id]) for metric_id in REQUIRED_METRICS}


def _to_tool_versions(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def _to_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
