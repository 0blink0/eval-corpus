"""Semantic completeness metric tests (METR-07)."""

from __future__ import annotations

from eval_corpus.ir_models import BlockType, Chunk
from eval_corpus.metrics.calculators import compute_metric_07_semantic_completeness
from eval_corpus.metrics.semantic_review import (
    build_manual_review_entry,
    select_semantic_samples,
)


def _semantic_chunks() -> list[Chunk]:
    return [
        Chunk(
            chunk_id="s1",
            text="本项目包含采购范围、投标要求和评分规则。",
            source_file="doc-a.pdf",
            page=1,
            heading_path=["第一章"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="s2",
            text="项目周期为三个月，含实施计划与验收标准。",
            source_file="doc-a.pdf",
            page=2,
            heading_path=["第二章"],
            parser_tool="paddle",
            block_types=[BlockType.paragraph],
        ),
        Chunk(
            chunk_id="s3",
            text="",
            source_file="doc-a.pdf",
            page=None,
            heading_path=[],
            parser_tool="paddle",
            block_types=[BlockType.other],
        ),
    ]


def test_semantic_auto_score_deterministic() -> None:
    chunks = _semantic_chunks()
    first = compute_metric_07_semantic_completeness(chunks)
    second = compute_metric_07_semantic_completeness(chunks)
    assert first.raw_value == second.raw_value
    sample_a = select_semantic_samples(chunks, sample_size=2, seed=7)
    sample_b = select_semantic_samples(chunks, sample_size=2, seed=7)
    assert [item.sample_index for item in sample_a] == [item.sample_index for item in sample_b]
    assert [item.sample_id for item in sample_a] == [item.sample_id for item in sample_b]


def test_manual_review_separate_from_auto_score() -> None:
    chunks = _semantic_chunks()
    result = compute_metric_07_semantic_completeness(chunks)
    before_auto = result.raw_value
    review = build_manual_review_entry(
        reviewer="qa-user",
        sample_id="s1",
        note="人工抽检记录",
        manual_label="pass",
        auto_score=0.85,
    )
    assert review.manual_review.reviewer == "qa-user"
    assert review.manual_review.sample_id == "s1"
    assert review.auto_score == 0.85
    assert before_auto == result.raw_value


def test_semantic_not_applicable_handling() -> None:
    chunks = _semantic_chunks()
    result = compute_metric_07_semantic_completeness(chunks)
    assert result.metric_id == "METR-07"
    assert result.total_count == 3
    assert result.applicable_count == 2
    assert result.excluded_count == 1
    assert "empty_text" in result.not_applicable_reasons
