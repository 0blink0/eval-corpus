"""Atomic calculators for METR-01~06."""

from __future__ import annotations

from pydantic import TypeAdapter

from eval_corpus.ir_models import BlockType, Chunk
from eval_corpus.metrics.models import MetricResult, MetricThreshold, judge_level

_PUNCT_ENDINGS = ("。", "！", "？", "!", "?", ";", "；")
_CHUNK_LIST_ADAPTER = TypeAdapter(list[Chunk])


def _validated_chunks(chunks: list[Chunk]) -> list[Chunk]:
    # Validate potentially untrusted input shape at boundary.
    return _CHUNK_LIST_ADAPTER.validate_python(chunks)


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _build_result(
    metric_id: str,
    numerator: int,
    denominator: int,
    excluded_count: int,
    applicable_count: int,
    total_count: int,
    threshold: MetricThreshold,
    not_applicable_reasons: list[str] | None = None,
) -> MetricResult:
    raw_value = _ratio(numerator, denominator)
    return MetricResult(
        metric_id=metric_id,
        raw_value=raw_value,
        threshold=threshold,
        level=judge_level(raw_value, threshold),
        numerator=numerator,
        denominator=denominator,
        excluded_count=excluded_count,
        applicable_count=applicable_count,
        total_count=total_count,
        not_applicable_reasons=not_applicable_reasons or [],
    )


def compute_metric_01(
    chunks: list[Chunk],
    *,
    golden_chars: int,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-01 覆盖完整率."""
    checked = _validated_chunks(chunks)
    total_count = len(checked)
    applicable = [c for c in checked if c.text.strip()]
    excluded_count = total_count - len(applicable)
    reasons: list[str] = []
    if golden_chars <= 0:
        reasons.append("golden_chars<=0")
    numerator = min(sum(len(c.text) for c in applicable), max(golden_chars, 0))
    denominator = max(golden_chars, 0)
    return _build_result(
        "METR-01",
        numerator=numerator,
        denominator=denominator,
        excluded_count=excluded_count,
        applicable_count=len(applicable),
        total_count=total_count,
        threshold=threshold or MetricThreshold(warn_min=0.85, pass_min=0.95),
        not_applicable_reasons=reasons,
    )


def compute_metric_02(
    chunks: list[Chunk],
    *,
    min_chars: int = 300,
    max_chars: int = 1000,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-02 块长度达标率."""
    checked = _validated_chunks(chunks)
    applicable = [c for c in checked if c.text.strip()]
    numerator = sum(1 for c in applicable if min_chars <= len(c.text) <= max_chars)
    denominator = len(applicable)
    return _build_result(
        "METR-02",
        numerator=numerator,
        denominator=denominator,
        excluded_count=len(checked) - len(applicable),
        applicable_count=len(applicable),
        total_count=len(checked),
        threshold=threshold or MetricThreshold(warn_min=0.80, pass_min=0.90),
        not_applicable_reasons=["no_applicable_chunks"] if denominator == 0 else [],
    )


def compute_metric_03(
    chunks: list[Chunk],
    *,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-03 边界准确率（句末标点命中）."""
    checked = _validated_chunks(chunks)
    applicable = [c for c in checked if c.text.strip()]
    numerator = sum(1 for c in applicable if c.text.rstrip().endswith(_PUNCT_ENDINGS))
    denominator = len(applicable)
    return _build_result(
        "METR-03",
        numerator=numerator,
        denominator=denominator,
        excluded_count=len(checked) - len(applicable),
        applicable_count=len(applicable),
        total_count=len(checked),
        threshold=threshold or MetricThreshold(warn_min=0.70, pass_min=0.85),
        not_applicable_reasons=["no_applicable_chunks"] if denominator == 0 else [],
    )


def compute_metric_04(
    chunks: list[Chunk],
    *,
    expected_table_blocks: int,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-04 表格保持率."""
    checked = _validated_chunks(chunks)
    detected_table_chunks = [c for c in checked if BlockType.table in c.block_types]
    denominator = max(expected_table_blocks, 0)
    numerator = min(len(detected_table_chunks), denominator)
    reasons = ["no_expected_tables"] if denominator == 0 else []
    return _build_result(
        "METR-04",
        numerator=numerator,
        denominator=denominator,
        excluded_count=len(checked) - len(detected_table_chunks),
        applicable_count=len(detected_table_chunks),
        total_count=len(checked),
        threshold=threshold or MetricThreshold(warn_min=0.80, pass_min=0.95),
        not_applicable_reasons=reasons,
    )


def _overlap_ratio(prev_text: str, cur_text: str) -> float:
    max_k = min(len(prev_text), len(cur_text))
    for k in range(max_k, 0, -1):
        if prev_text[-k:] == cur_text[:k]:
            return k / max(1, len(cur_text))
    return 0.0


def compute_metric_05(
    chunks: list[Chunk],
    *,
    min_overlap: float = 0.10,
    max_overlap: float = 0.20,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-05 重叠合理率."""
    checked = _validated_chunks(chunks)
    applicable = [c for c in checked if c.text.strip() and BlockType.table not in c.block_types]
    pair_count = max(0, len(applicable) - 1)
    numerator = 0
    for idx in range(1, len(applicable)):
        ratio = _overlap_ratio(applicable[idx - 1].text, applicable[idx].text)
        if min_overlap <= ratio <= max_overlap:
            numerator += 1
    return _build_result(
        "METR-05",
        numerator=numerator,
        denominator=pair_count,
        excluded_count=len(checked) - len(applicable),
        applicable_count=len(applicable),
        total_count=len(checked),
        threshold=threshold or MetricThreshold(warn_min=0.70, pass_min=0.85),
        not_applicable_reasons=["insufficient_adjacent_text_chunks"] if pair_count == 0 else [],
    )


def compute_metric_06(
    chunks: list[Chunk],
    *,
    threshold: MetricThreshold | None = None,
) -> MetricResult:
    """METR-06 元数据完整率."""
    checked = _validated_chunks(chunks)
    applicable = [c for c in checked if c.text.strip()]
    numerator = 0
    for c in applicable:
        if c.page is None:
            continue
        if not c.heading_path:
            continue
        if not c.parser_tool or c.parser_tool == "unknown":
            continue
        if not c.source_file or c.source_file == "unknown":
            continue
        numerator += 1
    denominator = len(applicable)
    return _build_result(
        "METR-06",
        numerator=numerator,
        denominator=denominator,
        excluded_count=len(checked) - len(applicable),
        applicable_count=len(applicable),
        total_count=len(checked),
        threshold=threshold or MetricThreshold(warn_min=0.80, pass_min=0.95),
        not_applicable_reasons=["no_applicable_chunks"] if denominator == 0 else [],
    )
