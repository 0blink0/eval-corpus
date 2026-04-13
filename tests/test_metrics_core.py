"""Core metric contract tests for METR-01~06."""

from __future__ import annotations

from eval_corpus.ir_models import BlockType, Chunk
from eval_corpus.metrics.calculators import (
    compute_metric_01,
    compute_metric_02,
    compute_metric_03,
    compute_metric_04,
    compute_metric_05,
    compute_metric_06,
)


def _sample_chunks() -> list[Chunk]:
    return [
        Chunk(
            chunk_id="c1",
            text="第一段内容。第二句。",
            source_file="a.pdf",
            page=1,
            heading_path=["H1"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="c2",
            text="第二段内容。句子结束。",
            source_file="a.pdf",
            page=1,
            heading_path=["H1"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
    ]


def test_coverage_completeness() -> None:
    chunks = _sample_chunks()
    golden_chars = len(chunks[0].text) + len(chunks[1].text)
    result = compute_metric_01(chunks, golden_chars=golden_chars)
    assert result.numerator == golden_chars
    assert result.denominator == golden_chars
    assert result.excluded_count == 0
    assert result.applicable_count == 2
    assert result.total_count == 2


def test_length_compliance() -> None:
    chunks = _sample_chunks()
    result = compute_metric_02(chunks, min_chars=6, max_chars=30)
    assert result.numerator == 2
    assert result.denominator == 2
    assert result.excluded_count == 0
    assert result.applicable_count == 2
    assert result.total_count == 2


def test_boundary_accuracy_and_hardcut() -> None:
    chunks = _sample_chunks()
    result = compute_metric_03(chunks)
    assert result.numerator == 2
    assert result.denominator == 2
    assert result.excluded_count == 0
    assert result.applicable_count == 2
    assert result.total_count == 2


def test_table_retention() -> None:
    chunks = [
        Chunk(
            chunk_id="c1",
            text="表格文本",
            source_file="a.pdf",
            page=2,
            heading_path=["表格"],
            parser_tool="mineru",
            block_types=[BlockType.table],
        )
    ]
    result = compute_metric_04(chunks, expected_table_blocks=1)
    assert result.numerator == 1
    assert result.denominator == 1
    assert result.excluded_count == 0
    assert result.applicable_count == 1
    assert result.total_count == 1


def test_overlap_compliance() -> None:
    chunks = [
        Chunk(
            chunk_id="c1",
            text="ABCDEFGHIJ",
            source_file="a.pdf",
            page=1,
            heading_path=["H1"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="c2",
            text="GHIJ012345",
            source_file="a.pdf",
            page=1,
            heading_path=["H1"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
    ]
    result = compute_metric_05(chunks, min_overlap=0.10, max_overlap=0.50)
    assert result.numerator == 1
    assert result.denominator == 1
    assert result.excluded_count == 0
    assert result.applicable_count == 2
    assert result.total_count == 2


def test_metadata_completeness() -> None:
    chunks = _sample_chunks()
    result = compute_metric_06(chunks)
    assert result.numerator == 2
    assert result.denominator == 2
    assert result.excluded_count == 0
    assert result.applicable_count == 2
    assert result.total_count == 2
