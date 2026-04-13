"""Tests for synthetic dataset generator."""

from __future__ import annotations

import hashlib
from pathlib import Path

from eval_corpus.synthetic_data.generator import generate_synthetic_dataset
from eval_corpus.synthetic_data.models import SyntheticDataConfig


def _digest_tree(root: Path) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            items.append((path.relative_to(root).as_posix(), digest))
    return items


def test_generate_contains_text_scan_table_types(tmp_path: Path) -> None:
    config = SyntheticDataConfig(
        total_samples=12,
        min_text_length=80,
        max_text_length=120,
        type_ratio={"text": 0.4, "scan": 0.3, "table": 0.3},
        seed=2026,
    )
    manifest = generate_synthetic_dataset(tmp_path / "run", config)

    generated_types = {item.sample_type for item in manifest.items}
    assert generated_types == {"text", "scan", "table"}
    assert len(manifest.items) == 12


def test_generate_is_deterministic_with_same_seed(tmp_path: Path) -> None:
    config = SyntheticDataConfig(
        total_samples=9,
        min_text_length=60,
        max_text_length=90,
        type_ratio={"text": 0.34, "scan": 0.33, "table": 0.33},
        seed=7,
    )
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    manifest_a = generate_synthetic_dataset(out_a, config)
    manifest_b = generate_synthetic_dataset(out_b, config)

    summary_a = [(item.sample_type, item.relative_path) for item in manifest_a.items]
    summary_b = [(item.sample_type, item.relative_path) for item in manifest_b.items]
    assert summary_a == summary_b
    assert _digest_tree(out_a) == _digest_tree(out_b)
