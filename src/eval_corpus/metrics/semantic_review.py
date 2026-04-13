"""Deterministic semantic sampling and manual-review ledger."""

from __future__ import annotations

from random import Random

from pydantic import BaseModel, Field

from eval_corpus.ir_models import Chunk


class SemanticSample(BaseModel):
    sample_id: str
    sample_index: int = Field(ge=0)
    source_file: str
    page: int | None = None
    text: str


class ManualReviewRecord(BaseModel):
    reviewer: str
    sample_id: str
    note: str
    manual_label: str


class SemanticReviewEntry(BaseModel):
    # D-47: auto score and manual review are stored separately.
    auto_score: float | None = Field(default=None, ge=0.0, le=1.0)
    manual_review: ManualReviewRecord


def select_semantic_samples(
    chunks: list[Chunk],
    *,
    sample_size: int,
    seed: int,
) -> list[SemanticSample]:
    """Return deterministic semantic review samples."""
    if sample_size <= 0:
        return []

    indexed = [
        (idx, chunk)
        for idx, chunk in enumerate(chunks)
        if chunk.text.strip()
    ]
    if not indexed:
        return []

    take = min(sample_size, len(indexed))
    rng = Random(seed)
    picks = rng.sample(indexed, k=take)
    picks.sort(key=lambda item: item[0])
    return [
        SemanticSample(
            sample_id=chunk.chunk_id,
            sample_index=idx,
            source_file=chunk.source_file,
            page=chunk.page,
            text=chunk.text,
        )
        for idx, chunk in picks
    ]


def build_manual_review_entry(
    *,
    reviewer: str,
    sample_id: str,
    note: str,
    manual_label: str,
    auto_score: float | None,
) -> SemanticReviewEntry:
    """Build a separated manual-review ledger entry."""
    return SemanticReviewEntry(
        auto_score=auto_score,
        manual_review=ManualReviewRecord(
            reviewer=reviewer,
            sample_id=sample_id,
            note=note,
            manual_label=manual_label,
        ),
    )
