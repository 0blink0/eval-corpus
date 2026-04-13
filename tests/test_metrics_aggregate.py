"""Aggregation tests for per-file/per-tool/overall metrics payload."""

from __future__ import annotations

from eval_corpus.ir_models import BlockType, Chunk
from eval_corpus.metrics.aggregate import (
    build_overall_metrics,
    build_per_file_metrics,
    build_per_tool_metrics,
)
from eval_corpus.metrics.calculators import (
    compute_metric_01,
    compute_metric_02,
    compute_metric_03,
    compute_metric_04,
    compute_metric_05,
    compute_metric_06,
    compute_metric_07_semantic_completeness,
)


def _sample_chunks() -> list[Chunk]:
    return [
        Chunk(
            chunk_id="a-1",
            text="第一段文本内容完整。",
            source_file="a.pdf",
            page=1,
            heading_path=["封面"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="a-2",
            text="第二段文本信息完整。",
            source_file="a.pdf",
            page=1,
            heading_path=["正文"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="b-1",
            text="表格条目A|B|C",
            source_file="b.pdf",
            page=2,
            heading_path=["附表"],
            parser_tool="mineru",
            block_types=[BlockType.table],
        ),
    ]


def _metric_map(chunks: list[Chunk]) -> dict[str, dict]:
    return {
        "METR-01": compute_metric_01(chunks, golden_chars=120).model_dump(),
        "METR-02": compute_metric_02(chunks, min_chars=6, max_chars=120).model_dump(),
        "METR-03": compute_metric_03(chunks).model_dump(),
        "METR-04": compute_metric_04(chunks, expected_table_blocks=1).model_dump(),
        "METR-05": compute_metric_05(chunks, min_overlap=0.0, max_overlap=1.0).model_dump(),
        "METR-06": compute_metric_06(chunks).model_dump(),
        "METR-07": compute_metric_07_semantic_completeness(chunks).model_dump(),
    }


def test_aggregate_builds_three_levels() -> None:
    chunks = _sample_chunks()
    per_file = build_per_file_metrics(chunks, _metric_map(chunks), errors=[])
    per_tool = build_per_tool_metrics(per_file)
    overall = build_overall_metrics(per_file, per_tool)

    payload = {
        "per_file": per_file,
        "per_tool": per_tool,
        "overall": overall,
    }
    assert set(payload.keys()) == {"per_file", "per_tool", "overall"}
    assert payload["per_file"]
    assert payload["per_tool"]
    assert payload["overall"]


def test_metric_fields_keep_raw_threshold_level() -> None:
    chunks = _sample_chunks()
    per_file = build_per_file_metrics(chunks, _metric_map(chunks), errors=[])

    first_item = per_file[0]
    metrics = first_item["metrics"]
    metric = metrics["METR-01"]
    assert "raw_value" in metric
    assert "threshold" in metric
    assert "level" in metric


def test_per_file_metrics_do_not_reuse_single_template_across_files() -> None:
    chunks = _sample_chunks()
    per_file = build_per_file_metrics(chunks, _metric_map(chunks), errors=[])

    by_file = {item["file"]: item for item in per_file}
    assert set(by_file.keys()) == {"a.pdf", "b.pdf"}

    a_raw = by_file["a.pdf"]["metrics"]["METR-04"]["raw_value"]
    b_raw = by_file["b.pdf"]["metrics"]["METR-04"]["raw_value"]
    assert a_raw != b_raw


def test_overall_runtime_error_count_uses_aggregated_errors() -> None:
    chunks = _sample_chunks()
    per_file = build_per_file_metrics(
        chunks,
        errors=[
            {"source_file": "a.pdf", "parser_tool": "paddle"},
            {"source_file": "a.pdf", "parser_tool": "paddle"},
        ],
    )
    per_tool = build_per_tool_metrics(per_file)

    overall = build_overall_metrics(
        per_file,
        per_tool,
        runtime_metadata={"error_count": 999, "extra": "keep"},
    )

    assert overall["runtime_metadata"]["error_count"] == 2
    assert overall["runtime_metadata"]["extra"] == "keep"
